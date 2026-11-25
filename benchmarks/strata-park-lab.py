#!/usr/bin/env python3
"""Drive Strata Oracle D: park-churn under subagent pressure (adoption plan §5).

One invocation measures one arm (A-E) of the persistence mechanism, repeated N
times against an already-running engine:

  warm a ~120k-token main conversation -> burst K scripted subagent
  conversations -> return to the main conversation with a one-token probe ->
  report reuse, TTFT and the conversation-cache counters.

``--share-prefix small`` (default for A/B/C) gives workers a short, shared
plain-text system prompt, so the idle main is the LRU victim; ``full`` (default
for D/E) makes workers inherit main's whole system prompt for pinning tests.
A cell whose burst parked/evicted nothing is reported invalid and is excluded
from the gate.

The engine is never started, restarted or reconfigured here.  Arms A/B/C are
engine configurations: the plan prints the restart command the operator runs
between arms.  Arms D/E send the per-request fields themselves.

See docs/research/strata-tuning.md §8 for the Oracle D protocol, arms and
gate.  Results: <out>/cells.jsonl (one JSON row per cell, appended) and
<out>/summary.md (per-arm medians and gate verdict, regenerated from every row
in cells.jsonl so several arms can share one output directory).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import statistics
import sys
import tempfile
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# --- Oracle D constants from adoption plan §5 --------------------------------

GATED_ARMS = ("B", "D", "E")
GATE_MIN_REUSE_PCT = 95.0
GATE_MAX_TTFT_MS = 3000.0

# Per-subagent new tokens: the first turn already clears the 4,096-token
# floor, later turns grow.  Added on top of the shared system prompt.
SUBAGENT_TURN_TOKENS = (4096, 6144, 8192)

# --share-prefix small: workers share this short plain-text system prompt
# instead of the main conversation's document.  ~150 tokens, no corpus.
WORKER_PREFIX_TOKENS = 150
WORKER_SYSTEM_UNIT = (
    "You are a worker subagent in the Strata park-churn lab. You share this short "
    "system prompt with every other worker; the main conversation's document is not "
    "part of your context. Investigate the material in each user turn and answer "
    "with the three highest risks, a short justification for each, and one concrete "
    "next step. Do not ask questions. Keep the answer within the requested budget.\n\n"
)

# Arms that measure eviction + persistence get the production shape (small
# worker prefix); arms that measure prefix pinning keep main's full prefix.
SMALL_PREFIX_ARMS = ("A", "B", "C")

SPILL_DIR = "~/.cache/user-cache/conv-spill"
SPILL_MIB = 24576
REWIND_KEEP_DEFAULT = 4096

FIXED_CACHE_CONFIG = (
    "--conversation-cache-slots 8",
    "--conversation-cache-mib 16384",
    "--conversation-cache-min-free-mib 6144",
    "--conversation-cache-min-tokens 4096",
    "--conversation-cache-park-gain 2048",
    "--prompt-cache 6",
)

# The Oracle B corpus `omp bench --profile mix --prefill-bytes 120000` repeats:
# cachePrefixChunk imported from src/prompts/bench/cache-prefix-chunk.md.
CORPUS_REL = Path(
    "submodules/aur-packages/oh-my-pi-git/src/oh-my-pi/packages/coding-agent"
    "/src/prompts/bench/cache-prefix-chunk.md"
)

BYTES_PER_TOKEN = 3.6
TOKENS_PER_WORD = 1.15
_LCG_A = 6364136223846793005
_LCG_C = 1442695040888963407
_MASK64 = (1 << 64) - 1

_WORDS = (
    "adapter admission arena artifact baseline batch budget cache checkpoint "
    "cluster collector conversation corpus decode delta disk draft engine "
    "eviction expert fallback fence frontier gain geometry headroom idle "
    "journal latency lease ledger metric model monitor nonce park prefix "
    "prefill profile queue reader refusal region restore ring router sample "
    "session shard slot snapshot spill stage suffix tail tenant tier token "
    "trace turnaround valve window worker"
).split()

_METRIC_RE = re.compile(
    r"^(?P<name>[A-Za-z_:][A-Za-z0-9_:.]*)(?:\{(?P<labels>[^}]*)\})?"
    r"\s+(?P<value>[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?\d+)?)\s*$"
)
_REASON_RE = re.compile(r'reason="([^"]*)"')


class LabError(RuntimeError):
    """A condition that makes the requested run impossible (exit code 1)."""


# --- token sizing ------------------------------------------------------------

_TIKTOKEN_URL = (
    "https://openaipublic.blob.core.windows.net/encodings/cl100k_base.tiktoken"
)


def _tiktoken_cache_file() -> Path | None:
    """The cached cl100k_base BPE file, or None when tiktoken would download it."""
    # Same precedence as tiktoken's read_file_cached().
    directory = (
        os.environ.get("TIKTOKEN_CACHE_DIR")
        or os.environ.get("DATA_GYM_CACHE_DIR")
        or os.path.join(tempfile.gettempdir(), "data-gym-cache")
    )
    candidate = Path(directory) / hashlib.sha1(_TIKTOKEN_URL.encode()).hexdigest()
    return candidate if candidate.is_file() else None


class TokenEstimator:
    """Sizing and truncation of generated text.

    tiktoken's cl100k_base when importable (deterministic and cached locally),
    otherwise a bytes/3.6 heuristic.  These are estimates: the engine's own
    timings.prompt_n is the authoritative token count for every cell.
    """

    def __init__(self) -> None:
        self._enc: Any | None = None
        self.name = f"bytes/{BYTES_PER_TOKEN} heuristic"
        # Only use tiktoken when its BPE file is already cached: get_encoding()
        # downloads it otherwise, and a dry run must never touch the network.
        if _tiktoken_cache_file() is None:
            return
        try:
            import tiktoken

            self._enc = tiktoken.get_encoding("cl100k_base")
            self.name = "tiktoken cl100k_base"
        except Exception:  # pragma: no cover - optional dependency
            self._enc = None

    def count(self, text: str) -> int:
        if not text:
            return 0
        if self._enc is not None:
            return len(self._enc.encode(text, disallowed_special=()))
        return max(1, math.ceil(len(text.encode("utf-8")) / BYTES_PER_TOKEN))

    def truncate(self, text: str, tokens: int) -> str:
        if tokens <= 0 or not text:
            return ""
        if self._enc is not None:
            ids = self._enc.encode(text, disallowed_special=())[:tokens]
            return str(self._enc.decode(ids))
        raw = text.encode("utf-8")[: int(tokens * BYTES_PER_TOKEN)]
        return raw.decode("utf-8", "ignore")


def fit_text(unit: str, tokens: int, est: TokenEstimator) -> str:
    """Repeat `unit` and trim it to exactly (as measured) `tokens` tokens."""
    if tokens <= 0 or not unit:
        return ""
    unit_tokens = max(1, est.count(unit))
    repeats = max(1, math.ceil(tokens / unit_tokens))
    body = unit * repeats
    # The estimate rounds up per unit, so the first product can fall short;
    # double until the measured count covers the target, then trim.
    while est.count(body) < tokens and repeats < 1 << 24:
        repeats *= 2
        body = unit * repeats
    return est.truncate(body, tokens)


def _stream_words(seed: int, count: int) -> list[str]:
    state = (seed * _LCG_A + _LCG_C) & _MASK64 or 0x9E3779B97F4A7C15
    out: list[str] = []
    for index in range(count):
        state = (state * _LCG_A + _LCG_C) & _MASK64
        out.append(_WORDS[(state >> 33) % len(_WORDS)])
        if index % 17 == 16:
            out.append(".")
    return out


def seeded_text(seed: int, tokens: int, est: TokenEstimator) -> str:
    """Deterministic technical filler of approximately `tokens` tokens."""
    words = max(8, int(tokens / TOKENS_PER_WORD * 1.25) + 16)
    return est.truncate(" ".join(_stream_words(seed, words)), tokens)


# --- corpus ------------------------------------------------------------------


def find_default_corpus(script: Path) -> Path | None:
    for root in script.parents:
        candidate = root / CORPUS_REL
        if candidate.is_file():
            return candidate
    return None


def resolve_corpus(explicit: Path | None, script: Path) -> tuple[str, str]:
    """Return (chunk_text, human-readable source label)."""
    path = explicit if explicit is not None else find_default_corpus(script)
    if path is not None:
        if not path.is_file():
            raise LabError(f"--corpus {path} is not a file")
        chunk = path.read_text(encoding="utf-8", errors="replace")
        if not chunk.strip():
            raise LabError(f"--corpus {path} is empty")
        return chunk, f"file {path}"
    return "", "synthetic seeded filler (corpus file not found)"


# --- arms --------------------------------------------------------------------


@dataclass(frozen=True)
class ArmSpec:
    arm: str
    title: str
    assumed: tuple[str, ...]
    request_fields: dict[str, Any]
    restart_flags: tuple[str, ...]
    restart_needed: bool


def arm_spec(arm: str, rewind_keep: int) -> ArmSpec:
    common = (
        "fixed baseline (unchanged in every arm): " + " ".join(FIXED_CACHE_CONFIG),
    )
    if arm == "A":
        return ArmSpec(
            arm="A",
            title="baseline: no persistence tier (today, --disk-spill removed)",
            assumed=common
            + ("no --conversation-spill-dir / --conversation-spill-mib and no --disk-spill",),
            request_fields={},
            restart_flags=(),
            restart_needed=True,
        )
    if arm == "B":
        return ArmSpec(
            arm="B",
            title="conversation-cache SSD tier",
            assumed=common
            + (
                f"--conversation-spill-dir {SPILL_DIR}",
                f"--conversation-spill-mib {SPILL_MIB}",
            ),
            request_fields={},
            restart_flags=(
                "--conversation-spill-dir",
                SPILL_DIR,
                "--conversation-spill-mib",
                str(SPILL_MIB),
            ),
            restart_needed=True,
        )
    if arm == "C":
        return ArmSpec(
            arm="C",
            title="B + config parallel=2 (does the tier still serve the evicted main?)",
            assumed=common
            + (
                f"--conversation-spill-dir {SPILL_DIR}",
                f"--conversation-spill-mib {SPILL_MIB}",
                'config "parallel": 2',
            ),
            request_fields={},
            restart_flags=(
                "--conversation-spill-dir",
                SPILL_DIR,
                "--conversation-spill-mib",
                str(SPILL_MIB),
            ),
            restart_needed=True,
        )
    if arm == "D":
        return ArmSpec(
            arm="D",
            title="router-side strata_prefix on prefix-sharing subagent requests",
            assumed=common
            + (
                "--prompt-cache >= 3 (6 above) for strata_prefix",
                'subagent requests send "strata_prefix": {"messages": 1}',
                "no spill tier required: the pinned prefix survives the main eviction",
            ),
            request_fields={"strata_prefix": {"messages": 1}},
            restart_flags=(),
            restart_needed=False,
        )
    if arm == "E":
        return ArmSpec(
            arm="E",
            title="D + strata_checkpoint:false on the burst, --prompt-cache-spread, "
            "--conversation-cache-rewind-keep",
            assumed=common
            + (
                'subagent requests send "strata_prefix": {"messages": 1}',
                'subagent requests send "strata_checkpoint": false',
                "--prompt-cache-spread",
                f"--conversation-cache-rewind-keep {rewind_keep}",
            ),
            request_fields={
                "strata_prefix": {"messages": 1},
                "strata_checkpoint": False,
            },
            restart_flags=(
                "--prompt-cache-spread",
                "--conversation-cache-rewind-keep",
                str(rewind_keep),
            ),
            restart_needed=True,
        )
    raise LabError(f"unknown arm {arm!r}")


def restart_lines(spec: ArmSpec) -> list[str]:
    if not spec.restart_needed:
        return [
            "no engine restart needed for this arm; verify --prompt-cache >= 3",
            "and that the router (or this driver) sends strata_prefix.",
        ]
    lines: list[str] = []
    if spec.restart_flags:
        lines.append("add to the launch command: " + " ".join(spec.restart_flags))
    else:
        lines.append("ensure the launch command has no --disk-spill and no spill flags")
    lines.append("systemctl --user restart local-chat-strata")
    lines.append("(the operator runs this between arms; this script never restarts the engine)")
    return lines


# --- text plan ---------------------------------------------------------------


@dataclass(frozen=True)
class CellPlan:
    nonce: str
    prefix: str
    worker_prefix: str
    workers_prefix_tokens: int
    share_prefix: str
    warm_user: str
    probe_user: str
    turns: tuple[tuple[str, ...], ...]
    seed: int


def build_cell_plan(
    corpus_block: str,
    nonce: str,
    k: int,
    seed: int,
    est: TokenEstimator,
    share_prefix: str,
) -> CellPlan:
    prefix = (
        f"Strata park-lab cell {nonce}. This is the main conversation's system "
        "prompt.\n\n" + corpus_block
    )
    if share_prefix == "full":
        worker_prefix = prefix
    else:
        worker_prefix = fit_text(WORKER_SYSTEM_UNIT, WORKER_PREFIX_TOKENS, est)
    turns = []
    for worker in range(1, k + 1):
        worker_turns = []
        for turn, tokens in enumerate(SUBAGENT_TURN_TOKENS, 1):
            body = seeded_text(seed + 1000 * worker + turn, tokens, est)
            # The cell nonce lives in the first user turn (not the worker
            # system prompt) so a small share-prefix stays byte-identical
            # across workers while each repeat busts the previous cell's cache.
            worker_turns.append(
                f"Worker {worker} turn {turn} of {len(SUBAGENT_TURN_TOKENS)} "
                f"(cell {nonce}). "
                "Investigate the material below and list the three highest risks.\n\n"
                + body
            )
        turns.append(tuple(worker_turns))
    return CellPlan(
        nonce=nonce,
        prefix=prefix,
        worker_prefix=worker_prefix,
        workers_prefix_tokens=est.count(worker_prefix),
        share_prefix=share_prefix,
        warm_user="Warm-up: this conversation is the main agent's working set. Reply READY.",
        probe_user="Continue",  # one token; max_tokens=1 bounds the answer too
        turns=tuple(turns),
        seed=seed,
    )


def preview(text: str, width: int = 80) -> str:
    head = text[:width].replace("\n", "\\n").replace("\r", "\\r")
    return head + ("..." if len(text) > width else "")


def estimate_messages(messages: list[dict[str, str]], est: TokenEstimator) -> int:
    return sum(est.count(message["content"]) for message in messages)


# --- HTTP --------------------------------------------------------------------


@dataclass
class ChatResult:
    text: str = ""
    ttft_ms: float | None = None
    wall_ms: float = 0.0
    usage: dict[str, Any] | None = None
    timings: dict[str, Any] | None = None
    error: str | None = None


def _absorb_event(
    event: dict[str, Any], result: ChatResult, parts: list[str], started: float
) -> None:
    choices = event.get("choices")
    if isinstance(choices, list) and choices and isinstance(choices[0], dict):
        choice = choices[0]
        delta = choice.get("delta")
        if not isinstance(delta, dict):
            delta = choice.get("message") if isinstance(choice.get("message"), dict) else {}
        for key in ("content", "reasoning_content"):
            piece = delta.get(key)
            if isinstance(piece, str) and piece:
                if result.ttft_ms is None:
                    result.ttft_ms = (time.perf_counter() - started) * 1000.0
                if key == "content":
                    parts.append(piece)
    usage = event.get("usage")
    if isinstance(usage, dict):
        result.usage = usage
    timings = event.get("timings")
    if isinstance(timings, dict):
        result.timings = timings


def post_chat(base_url: str, payload: dict[str, Any], timeout: float) -> ChatResult:
    url = base_url.rstrip("/") + "/chat/completions"
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Accept": "text/event-stream"},
        method="POST",
    )
    started = time.perf_counter()
    result = ChatResult()
    parts: list[str] = []
    body: list[str] = []
    saw_sse = False
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            for raw in response:
                line = raw.decode("utf-8", "replace")
                body.append(line)
                stripped = line.strip()
                if not stripped.startswith("data:"):
                    continue
                saw_sse = True
                data = stripped[5:].strip()
                if data == "[DONE]":
                    break
                try:
                    event = json.loads(data)
                except json.JSONDecodeError:
                    continue
                if isinstance(event, dict) and event.get("error"):
                    result.error = f"stream error: {event['error']}"
                    break
                if isinstance(event, dict):
                    _absorb_event(event, result, parts, started)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace").strip()
        return ChatResult(
            error=f"HTTP {exc.code}: {detail[:500]}",
            wall_ms=(time.perf_counter() - started) * 1000.0,
        )
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return ChatResult(
            error=f"{type(exc).__name__}: {exc}",
            wall_ms=(time.perf_counter() - started) * 1000.0,
        )
    result.wall_ms = (time.perf_counter() - started) * 1000.0
    if not saw_sse and result.error is None:
        try:
            payload_json = json.loads("".join(body))
        except json.JSONDecodeError:
            result.error = "response was neither SSE nor JSON"
        else:
            if isinstance(payload_json, dict) and payload_json.get("error"):
                result.error = f"error: {payload_json['error']}"
            elif isinstance(payload_json, dict):
                _absorb_event(payload_json, result, parts, started)
    result.text = "".join(parts)
    if result.ttft_ms is None and result.error is None:
        result.ttft_ms = result.wall_ms
    return result


def metrics_root(base_url: str) -> str:
    base = base_url.rstrip("/")
    if base.endswith("/v1"):
        return base[:-3]
    marker = "/v1/"
    return base.split(marker, 1)[0] if marker in base else base


def _parse_prometheus(text: str, state: dict[str, Any]) -> bool:
    matched = False
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        match = _METRIC_RE.match(line)
        if match is None:
            continue
        name = match.group("name").rsplit(":", 1)[-1]
        try:
            value = float(match.group("value"))
        except ValueError:
            continue
        if "conversation_cache_refused" in name:
            reason_match = _REASON_RE.search(match.group("labels") or "")
            reason = reason_match.group(1) if reason_match else "unknown"
            state["refused"][reason] = int(value)
            matched = True
        elif name == "conversation_cache_parked":
            state["parked"] = int(value)
        elif name == "conversation_cache_parks_total":
            state["parks"] = int(value)
        elif name == "conversation_cache_restores_total":
            state["restores"] = int(value)
        elif name == "conversation_cache_evictions_total":
            state["evictions"] = int(value)
    if matched:
        state["refused_total"] = sum(state["refused"].values())
    return matched


def _parse_json_metrics(body: str, state: dict[str, Any]) -> bool:
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return False
    cache = data.get("conversation_cache") if isinstance(data, dict) else None
    if not isinstance(cache, dict):
        return False
    refused = cache.get("refused")
    state["refused"] = {
        str(key): int(value) for key, value in refused.items() if isinstance(value, (int, float))
    } if isinstance(refused, dict) else {}
    state["refused_total"] = int(cache.get("refused_total") or sum(state["refused"].values()))
    for key in ("parked", "bytes", "evictions", "parks", "restores"):
        value = cache.get(key)
        state[key] = int(value) if isinstance(value, (int, float)) else None
    return True


def scrape_metrics(root: str, timeout: float) -> dict[str, Any]:
    """Conversation-cache counters from /metrics/prometheus, with fallbacks."""
    state: dict[str, Any] = {
        "source": None,
        "error": None,
        "refused": {},
        "refused_total": None,
        "parked": None,
        "bytes": None,
        "evictions": None,
        "parks": None,
        "restores": None,
    }
    attempts = (
        ("/metrics/prometheus", "text/plain"),
        ("/metrics", "text/plain;version=0.0.4"),
        ("/metrics", "application/json"),
    )
    last_error: str | None = None
    for path, accept in attempts:
        request = urllib.request.Request(
            root.rstrip("/") + path, headers={"Accept": accept}
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                body = response.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as exc:
            last_error = f"HTTP {exc.code} on {path}"
            if exc.code == 404:
                continue
            break
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            state["error"] = f"{type(exc).__name__}: {exc}"
            return state
        if body.lstrip().startswith("{"):
            if _parse_json_metrics(body, state):
                state["source"] = path + " (json)"
                return state
            continue
        if "conversation_cache" in body:
            state["source"] = path
            _parse_prometheus(body, state)
            if state["refused_total"] is None:
                state["refused_total"] = 0
            return state
        last_error = f"{path}: no conversation_cache metrics"
    state["error"] = last_error or "no conversation-cache metrics endpoint"
    return state


def fetch_status(base_url: str, timeout: float) -> dict[str, Any]:
    try:
        with urllib.request.urlopen(
            base_url.rstrip("/") + "/status", timeout=timeout
        ) as response:
            data = json.loads(response.read().decode("utf-8", "replace"))
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


# --- cell execution ----------------------------------------------------------


@dataclass
class RunConfig:
    base_url: str
    model: str
    timeout: float
    max_tokens: int
    k: int
    idle_seconds: float
    arm: str
    share_prefix: str
    background: str
    spec: ArmSpec

    def __post_init__(self) -> None:
        self.base_url = self.base_url.rstrip("/")


def _int_or_none(value: Any) -> int | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return int(value)


def _float_or_none(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def _refusal_counts(metrics: dict[str, Any]) -> dict[str, int]:
    refused = metrics.get("refused")
    if not isinstance(refused, dict):
        return {}
    return {str(key): int(value) for key, value in refused.items()}


def _refusal_delta(
    before: dict[str, Any], after: dict[str, Any]
) -> dict[str, int]:
    first = _refusal_counts(before)
    second = _refusal_counts(after)
    return {
        reason: second.get(reason, 0) - first.get(reason, 0)
        for reason in sorted(set(first) | set(second))
    }


def _conv_cache(metrics: dict[str, Any]) -> dict[str, Any]:
    return {
        key: metrics.get(key)
        for key in ("parked", "bytes", "evictions", "parks", "restores", "refused_total")
    }


def _counter_rose(before: dict[str, Any], after: dict[str, Any], key: str) -> bool:
    first = _int_or_none(before.get(key))
    second = _int_or_none(after.get(key))
    return first is not None and second is not None and second > first


def _pressure_ok(before: dict[str, Any], after: dict[str, Any]) -> bool:
    """True when the burst parked or evicted something (the cell has evidence)."""
    return _counter_rose(before, after, "parks") or _counter_rose(
        before, after, "evictions"
    )


def _row_pressure(row: dict[str, Any]) -> bool:
    """pressure_ok for a row, recomputed for rows written before the field existed."""
    recorded = row.get("pressure_ok")
    if isinstance(recorded, bool):
        return recorded
    cache = row.get("conv_cache")
    if not isinstance(cache, dict):
        return False
    before = cache.get("before")
    after = cache.get("after")
    if not isinstance(before, dict) or not isinstance(after, dict):
        return False
    return _pressure_ok(before, after)


def _row_valid(row: dict[str, Any]) -> bool:
    return bool(row.get("ok")) and _row_pressure(row)


def _gate(arm: str, reuse_pct: float | None, ttft_ms: float | None) -> bool | None:
    if arm not in GATED_ARMS:
        return None
    if reuse_pct is None or ttft_ms is None:
        return False
    return reuse_pct >= GATE_MIN_REUSE_PCT and ttft_ms <= GATE_MAX_TTFT_MS


def _chat(
    cfg: RunConfig,
    messages: list[dict[str, str]],
    max_tokens: int,
    extra: dict[str, Any] | None = None,
) -> ChatResult:
    payload: dict[str, Any] = {
        "model": cfg.model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.0,
        "stream": True,
        "enable_thinking": False,
    }
    if extra:
        payload.update(extra)
    return post_chat(cfg.base_url, payload, cfg.timeout)


def _failed_row(
    cfg: RunConfig,
    repeat: int,
    plan: CellPlan,
    error: str,
    before: dict[str, Any],
    after: dict[str, Any] | None,
    stage: str,
) -> dict[str, Any]:
    cache_before = _conv_cache(before)
    cache_after = _conv_cache(after or {})
    pressure = _pressure_ok(cache_before, cache_after)
    return {
        "arm": cfg.arm,
        "repeat": repeat,
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "ok": False,
        "valid": False,
        "error": error,
        "stage": stage,
        "nonce": plan.nonce,
        "share_prefix": cfg.share_prefix,
        "workers_prefix_tokens": plan.workers_prefix_tokens,
        "base_url": cfg.base_url,
        "model": cfg.model,
        "cached_tokens": None,
        "prompt_n": None,
        "prompt_ms": None,
        "prompt_tokens": None,
        "reuse_pct": None,
        "ttft_ms": None,
        "decode_tps": None,
        "refusals": {
            "before": _refusal_counts(before),
            "after": _refusal_counts(after or {}),
            "delta": _refusal_delta(before, after or {}),
        },
        "conv_cache": {"before": cache_before, "after": cache_after},
        "metrics_source": (after or before).get("source"),
        "metrics_error": (after or before).get("error"),
        "pressure_ok": pressure,
        "gate_pass": None,
        "background": cfg.background,
    }


def run_cell(cfg: RunConfig, plan: CellPlan, repeat: int) -> dict[str, Any]:
    root = metrics_root(cfg.base_url)
    before = scrape_metrics(root, min(cfg.timeout, 30.0))
    main_history = [
        {"role": "system", "content": plan.prefix},
        {"role": "user", "content": plan.warm_user},
    ]
    print(f"[cell {cfg.arm}/{repeat}] warming {plan.nonce} ...", file=sys.stderr, flush=True)
    warm = _chat(cfg, main_history, max_tokens=min(cfg.max_tokens, 16))
    if warm.error:
        return _failed_row(cfg, repeat, plan, warm.error, before, None, "warm")
    main_history.append({"role": "assistant", "content": warm.text or "READY"})
    print(
        f"[cell {cfg.arm}/{repeat}] warm done: ttft={warm.ttft_ms or 0:.0f} ms "
        f"wall={warm.wall_ms:.0f} ms",
        file=sys.stderr,
        flush=True,
    )

    if cfg.idle_seconds > 0:
        time.sleep(cfg.idle_seconds)

    burst: list[dict[str, Any]] = []
    for worker, worker_turns in enumerate(plan.turns, 1):
        history: list[dict[str, str]] = [
            {"role": "system", "content": plan.worker_prefix}
        ]
        for turn, text in enumerate(worker_turns, 1):
            history.append({"role": "user", "content": text})
            response = _chat(
                cfg,
                history,
                max_tokens=cfg.max_tokens,
                extra=cfg.spec.request_fields,
            )
            if response.error:
                after = scrape_metrics(root, min(cfg.timeout, 30.0))
                return _failed_row(
                    cfg,
                    repeat,
                    plan,
                    f"worker {worker} turn {turn}: {response.error}",
                    before,
                    after,
                    "burst",
                )
            burst.append(
                {
                    "worker": worker,
                    "turn": turn,
                    "ttft_ms": response.ttft_ms,
                    "wall_ms": response.wall_ms,
                    "prompt_tokens": _int_or_none(
                        (response.usage or {}).get("prompt_tokens")
                    ),
                    "cached_tokens": _int_or_none(
                        ((response.usage or {}).get("prompt_tokens_details") or {}).get(
                            "cached_tokens"
                        )
                    ),
                    "prompt_n": _int_or_none((response.timings or {}).get("prompt_n")),
                }
            )
            history.append(
                {"role": "assistant", "content": response.text or f"Worker {worker} noted."}
            )
        print(
            f"[cell {cfg.arm}/{repeat}] worker {worker}/{cfg.k} done",
            file=sys.stderr,
            flush=True,
        )

    burst_metrics = scrape_metrics(root, min(cfg.timeout, 30.0))
    probe_history = main_history + [{"role": "user", "content": plan.probe_user}]
    print(f"[cell {cfg.arm}/{repeat}] probing main ...", file=sys.stderr, flush=True)
    probe = _chat(cfg, probe_history, max_tokens=1)
    after = scrape_metrics(root, min(cfg.timeout, 30.0))
    if probe.error:
        return _failed_row(
            cfg, repeat, plan, f"probe: {probe.error}", before, after, "probe"
        )

    usage = probe.usage or {}
    details = usage.get("prompt_tokens_details")
    cached_tokens = _int_or_none(
        details.get("cached_tokens") if isinstance(details, dict) else None
    )
    prompt_tokens = _int_or_none(usage.get("prompt_tokens"))
    timings = probe.timings or {}
    prompt_n = _int_or_none(timings.get("prompt_n"))
    prompt_ms = _float_or_none(timings.get("prompt_ms"))
    predicted_n = _int_or_none(timings.get("predicted_n"))
    predicted_ms = _float_or_none(timings.get("predicted_ms"))

    reuse_pct: float | None = None
    if cached_tokens is not None and prompt_tokens:
        reuse_pct = 100.0 * cached_tokens / prompt_tokens
    elif prompt_n is not None and prompt_tokens:
        reuse_pct = 100.0 * (prompt_tokens - prompt_n) / prompt_tokens

    completion_tokens = _int_or_none(usage.get("completion_tokens"))
    decode_tps: float | None = None
    if predicted_n and predicted_ms:
        decode_tps = predicted_n / predicted_ms * 1000.0
    elif completion_tokens and probe.ttft_ms is not None and probe.wall_ms > probe.ttft_ms:
        decode_tps = completion_tokens / ((probe.wall_ms - probe.ttft_ms) / 1000.0)

    ttft_ms = probe.ttft_ms
    cache_before = _conv_cache(before)
    cache_burst = _conv_cache(burst_metrics)
    cache_after = _conv_cache(after)
    pressure = _pressure_ok(cache_before, cache_burst)
    row: dict[str, Any] = {
        "arm": cfg.arm,
        "repeat": repeat,
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "ok": True,
        "valid": pressure,
        "error": None,
        "stage": "probe",
        "nonce": plan.nonce,
        "share_prefix": cfg.share_prefix,
        "workers_prefix_tokens": plan.workers_prefix_tokens,
        "base_url": cfg.base_url,
        "model": cfg.model,
        "cached_tokens": cached_tokens,
        "prompt_n": prompt_n,
        "prompt_ms": prompt_ms,
        "prompt_tokens": prompt_tokens,
        "reuse_pct": reuse_pct,
        "ttft_ms": ttft_ms,
        "decode_tps": decode_tps,
        "completion_tokens": completion_tokens,
        "warm_ttft_ms": warm.ttft_ms,
        "warm_wall_ms": warm.wall_ms,
        "probe_wall_ms": probe.wall_ms,
        "burst": burst,
        "refusals": {
            "before": _refusal_counts(before),
            "after": _refusal_counts(after),
            "delta": _refusal_delta(before, after),
        },
        "conv_cache": {
            "before": cache_before,
            "after_burst": cache_burst,
            "after": cache_after,
        },
        "metrics_source": after.get("source") or before.get("source"),
        "metrics_error": after.get("error") or before.get("error"),
        "pressure_ok": pressure,
        "gate_pass": _gate(cfg.arm, reuse_pct, ttft_ms) if pressure else None,
        "background": cfg.background,
    }
    print(
        f"[cell {cfg.arm}/{repeat}] reuse={reuse_pct if reuse_pct is None else round(reuse_pct, 1)}% "
        f"ttft={0 if ttft_ms is None else round(ttft_ms)} ms "
        f"prompt_n={prompt_n} pressure={pressure} gate={row['gate_pass']}",
        file=sys.stderr,
        flush=True,
    )
    if not pressure:
        print(
            f"[cell {cfg.arm}/{repeat}] INVALID: no parks/evictions rose during the "
            "cell (main was never evicted); raise --k or --warm-tokens",
            file=sys.stderr,
            flush=True,
        )
    return row


# --- reporting ---------------------------------------------------------------


def _median(values: list[float]) -> float | None:
    return statistics.median(values) if values else None


def _fmt(value: Any, digits: int = 1, suffix: str = "") -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.{digits}f}{suffix}"
    return f"{value}{suffix}"


def read_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.is_file():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict):
            rows.append(row)
    return rows


def summarize_arm(arm: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    arm_rows = [row for row in rows if row.get("arm") == arm]
    ok_rows = [row for row in arm_rows if row.get("ok")]
    valid_rows = [row for row in ok_rows if _row_valid(row)]
    reuse = [
        float(row["reuse_pct"]) for row in valid_rows if row.get("reuse_pct") is not None
    ]
    ttft = [float(row["ttft_ms"]) for row in valid_rows if row.get("ttft_ms") is not None]
    prompt_n = [
        float(row["prompt_n"]) for row in valid_rows if row.get("prompt_n") is not None
    ]
    cached = [
        float(row["cached_tokens"])
        for row in valid_rows
        if row.get("cached_tokens") is not None
    ]
    decode = [
        float(row["decode_tps"])
        for row in valid_rows
        if row.get("decode_tps") is not None
    ]
    refusals: dict[str, int] = {}
    for row in ok_rows:
        delta = (row.get("refusals") or {}).get("delta") or {}
        for reason, value in delta.items():
            if isinstance(value, (int, float)):
                refusals[str(reason)] = refusals.get(str(reason), 0) + int(value)
    modes = sorted(
        {str(row.get("share_prefix") or "unrecorded") for row in arm_rows}
    )
    median_reuse = _median(reuse)
    median_ttft = _median(ttft)
    if arm in GATED_ARMS:
        gate = (
            bool(valid_rows)
            and median_reuse is not None
            and median_ttft is not None
            and median_reuse >= GATE_MIN_REUSE_PCT
            and median_ttft <= GATE_MAX_TTFT_MS
        )
    else:
        gate = None
    return {
        "arm": arm,
        "modes": modes,
        "cells": len(arm_rows),
        "ok_cells": len(ok_rows),
        "valid_cells": len(valid_rows),
        "invalid_cells": len(ok_rows) - len(valid_rows),
        "median_reuse": median_reuse,
        "median_ttft": median_ttft,
        "median_prompt_n": _median(prompt_n),
        "median_cached": _median(cached),
        "median_decode_tps": _median(decode),
        "refusals": dict(sorted(refusals.items())),
        "gate": gate,
    }


def write_summary(
    out_dir: Path,
    all_rows: list[dict[str, Any]],
    args: argparse.Namespace,
    corpus_label: str,
    estimator_name: str,
    spec: ArmSpec,
) -> int:
    """Write summary.md; return 2 when a gated arm in the file fails, else 0."""
    arms = [arm for arm in ("A", "B", "C", "D", "E") if any(r.get("arm") == arm for r in all_rows)]
    summaries = [summarize_arm(arm, all_rows) for arm in arms]
    latest = all_rows[-1] if all_rows else {}
    engine = latest.get("engine") or "n/a"
    gate_failed = any(item["gate"] is False for item in summaries)

    if args.share_prefix == "small":
        mode_text = (
            "Share-prefix mode `small` (production shape): the main conversation keeps "
            f"the ~{args.warm_tokens}-token corpus in its system prompt; workers share a "
            f"short ~{WORKER_PREFIX_TOKENS}-token plain-text system prompt, so main's "
            "cache entry is the LRU victim."
        )
    else:
        mode_text = (
            "Share-prefix mode `full`: workers inherit the main conversation's entire "
            "system prompt. This measures prefix pinning/reuse, but that prefix stays "
            "hot and the main conversation may never be evicted."
        )

    lines: list[str] = [
        "# Strata park-churn lab — Oracle D",
        "",
        f"Generated: `{datetime.now(timezone.utc).isoformat(timespec='seconds')}`  ",
        f"Output: `{out_dir}`  ",
        f"Engine: `{engine}` · endpoint `{args.base_url}` · model `{args.model}`  ",
        f"Corpus: {corpus_label}  ",
        f"Token sizing: {estimator_name} (estimates only; `timings.prompt_n` is authoritative)  ",
        f"Background: {args.background}",
        "",
        f"Mode: {mode_text}",
        "",
        "Protocol: main conversation warmed to its system prompt, "
        f"`--idle-seconds {args.idle_seconds:g}`, then K={args.k} subagent conversations "
        f"of {len(SUBAGENT_TURN_TOKENS)} turns (+"
        + ", +".join(str(t) for t in SUBAGENT_TURN_TOKENS)
        + " tokens each), then a one-token probe on the main conversation. "
        f"Cells in this file: {len(all_rows)}; repeats per arm in this invocation: {args.repeat}.",
        "",
        "## Gate",
        "",
        f"Arms {'/'.join(GATED_ARMS)} pass when the per-arm median prefix reuse is "
        f">= {GATE_MIN_REUSE_PCT:g}% and the median client TTFT is "
        f"<= {GATE_MAX_TTFT_MS / 1000:g} s. Arms A and C are reference cells "
        "(baseline / exploratory) and are reported without a gate verdict. "
        "A cell with `pressure_ok: false` (no parks or evictions rose during the cell) "
        "is **invalid** and is excluded from every median and from the gate; a gated "
        "arm with no valid cell fails.",
        "",
        "| Arm | Mode | Cells (valid/ok/total) | Median reuse % | Median TTFT ms | "
        "Median prompt_n | Median cached tok | Median decode t/s | Refusals delta | Gate |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for item in summaries:
        refusals = (
            ", ".join(f"{k}:{v:+d}" for k, v in item["refusals"].items())
            if item["refusals"]
            else "-"
        )
        if item["gate"] is None:
            gate = "n/a (reference)"
        elif item["valid_cells"] == 0:
            gate = "**invalid** (no pressure)"
        else:
            gate = "**pass**" if item["gate"] else "**FAIL**"
        lines.append(
            f"| {item['arm']} | {', '.join(item['modes'])} | "
            f"{item['valid_cells']}/{item['ok_cells']}/{item['cells']} | "
            f"{_fmt(item['median_reuse'], 1)} | {_fmt(item['median_ttft'], 0)} | "
            f"{_fmt(item['median_prompt_n'], 0)} | {_fmt(item['median_cached'], 0)} | "
            f"{_fmt(item['median_decode_tps'], 1)} | {refusals} | {gate} |"
        )

    lines += [
        "",
        "## Cells",
        "",
        "| Arm | Mode | Rep | W prefix tok | ok | valid | cached | prompt_n | "
        "reuse % | TTFT ms | decode t/s | Refusals delta |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for row in all_rows:
        delta = (row.get("refusals") or {}).get("delta") or {}
        refusals = ", ".join(f"{k}:{v:+d}" for k, v in sorted(delta.items())) or "-"
        valid = _row_valid(row)
        if not row.get("ok"):
            validity = "NO (error)"
        elif valid:
            validity = "yes"
        else:
            validity = "**NO** (no pressure)"
        lines.append(
            f"| {row.get('arm')} | {row.get('share_prefix') or 'unrecorded'} | "
            f"{row.get('repeat')} | {_fmt(row.get('workers_prefix_tokens'), 0)} | "
            f"{'yes' if row.get('ok') else 'NO'} | {validity} | "
            f"{_fmt(row.get('cached_tokens'))} | {_fmt(row.get('prompt_n'))} | "
            f"{_fmt(row.get('reuse_pct'), 2)} | {_fmt(row.get('ttft_ms'), 0)} | "
            f"{_fmt(row.get('decode_tps'), 1)} | {refusals} |"
        )
        if not row.get("ok"):
            lines.append(
                f"| | | | | | | | | | | | error at {row.get('stage')}: {row.get('error')} |"
            )

    lines += [
        "",
        "## Arm configuration this invocation assumed",
        "",
        f"**{spec.arm}** — {spec.title}",
        "",
    ]
    lines += [f"- {note}" for note in spec.assumed]
    lines += [
        "",
        "Restart / verification for this arm (operator runs it; never executed here):",
        "",
    ]
    for line in restart_lines(spec):
        if line.startswith("systemctl "):
            lines += ["```bash", line, "```"]
        else:
            lines.append(f"- {line}")
    lines += [""]

    lines += [
        "## Notes and deviations from plan §5",
        "",
        "- `--share-prefix small` (default for A/B/C): the main keeps the `--warm-tokens` "
        "corpus in its system prompt and workers share a short, byte-identical plain-text "
        "system prompt — the production shape, so the idle main is the LRU victim. "
        "`full` (default for D/E): workers inherit the main's whole system prompt, which "
        "keeps it hot but is what pinning/reuse measurements need.",
        "- The cell nonce is in the main prefix and in each worker's first user turn, so "
        "repeats do not reuse the previous cell's parked conversations; the worker system "
        "prompt itself stays byte-identical within a cell.",
        '- `strata_prefix` is sent as `{"messages": 1}` — the form the engine documents '
        "(`resolve_prefix`); a bare `true` is a malformed field and returns 400.",
        "- The driver never restarts the engine. Cache state is busted per cell with a "
        "fresh nonce in the shared prefix; the operator restarts between arms (A/B/C) "
        "or applies D/E's flags.",
        "- Per-cell engine restarts (plan §3) are not performed: each restart costs a "
        "model load, and `--repeat` cells deliberately share one engine so the tier "
        "state carries across repeats the way it does in production.",
        "- Plan §3's A B B A interleave is operator choreography here: one invocation "
        "measures one arm, and arms alternate across invocations with the restart "
        "shown above between them.",
        "- Conversation-cache `parked/bytes/evictions/refused{reason}` come from "
        "`/metrics/prometheus` (fallback `/metrics` JSON), not from journalctl; the "
        "counters are engine-process scoped, exactly like the journal lines.",
        "- Whether the burst actually caused churn is read from those counters, not "
        "assumed: `pressure_ok` is true only when `parks` or `evictions` rose during "
        "the cell. Otherwise the row is `valid: false` (no eviction evidence), is "
        "excluded from the medians and the gate, and is marked invalid in the tables. "
        "Raise `--k` for more pressure: with slots=8, K=9 is the smallest burst that "
        "overflows the slot count.",
        "- TTFT is the first streamed delta (content or reasoning) after the POST. "
        "`enable_thinking` is false on every request so the probe is a true one-token turn.",
        "- Arms A/B/C are configuration-only: this script prints the restart command and "
        "cannot verify it was applied. Check the row's `engine`/`reuse_pct` before trusting "
        "the cell.",
        "",
    ]
    (out_dir / "summary.md").write_text("\n".join(lines), encoding="utf-8")
    return 2 if gate_failed else 0


# --- dry-run plan ------------------------------------------------------------


def print_plan(
    cfg: RunConfig,
    spec: ArmSpec,
    plan: CellPlan,
    corpus_label: str,
    estimator: TokenEstimator,
    out_dir: Path,
    repeat: int,
) -> None:
    prefix_tokens = estimator.count(plan.prefix)
    warm_messages = [
        {"role": "system", "content": plan.prefix},
        {"role": "user", "content": plan.warm_user},
    ]
    probe_messages = warm_messages + [
        {"role": "assistant", "content": "READY"},
        {"role": "user", "content": plan.probe_user},
    ]
    print("Strata park-churn lab — Oracle D (plan §5)")
    print("mode:           dry-run (no network; base URL is only printed)")
    print(f"arm:            {spec.arm} — {spec.title}")
    print(f"share prefix:   {plan.share_prefix}")
    if plan.share_prefix == "small":
        print("                workers share a short plain-text system prompt; the main "
              "conversation keeps the corpus")
    else:
        print("                workers inherit the main conversation's entire system prompt")
    print(f"endpoint:       {cfg.base_url}  model: {cfg.model}")
    print(f"corpus:         {corpus_label}")
    print(f"token sizing:   {estimator.name}")
    print(f"cells:          repeat 1..{repeat}, K={cfg.k} subagents, "
          f"{len(SUBAGENT_TURN_TOKENS)} turns each, idle {cfg.idle_seconds:g}s")
    print(f"outputs:        {out_dir / 'cells.jsonl'}, {out_dir / 'summary.md'} (not written in dry-run)")
    print("")
    print("assumed engine configuration:")
    for note in spec.assumed:
        print(f"  - {note}")
    print("")
    print("engine restart (operator runs it between arms; this script never does):")
    for line in restart_lines(spec):
        print(f"  # {line}")
    print("")
    print("request plan:")
    print(f"  main system prompt (corpus): {prefix_tokens:,} tok est")
    print(f"    first 80: {preview(plan.prefix)!r}")
    if plan.share_prefix == "full":
        print(
            f"  worker system prompt (main's prefix, byte-identical): "
            f"{plan.workers_prefix_tokens:,} tok est"
        )
    else:
        print(
            f"  worker system prompt (byte-identical, no corpus): "
            f"{plan.workers_prefix_tokens:,} tok est"
        )
        print(f"    first 80: {preview(plan.worker_prefix)!r}")
    print(
        f"  main warm: 2 messages, ~{estimate_messages(warm_messages, estimator):,} tok est, "
        f"max_tokens={min(cfg.max_tokens, 16)}, enable_thinking=false"
    )
    print(f"    user first 80: {preview(plan.warm_user)!r}")
    print(
        f"  main probe: {len(probe_messages)} messages, "
        f"~{estimate_messages(probe_messages, estimator):,} tok est, max_tokens=1"
    )
    print(f"    user first 80: {preview(plan.probe_user)!r}")
    print("  subagent burst (sequential, current request carries the full history):")
    for worker, worker_turns in enumerate(plan.turns, 1):
        cumulative = 0
        for turn, text in enumerate(worker_turns, 1):
            cumulative += estimator.count(text)
            if worker > 1:
                continue
            print(
                f"    worker {worker} turn {turn}: own content +{estimator.count(text):,} tok "
                f"(cumulative own {cumulative:,}), prompt ~"
                f"{plan.workers_prefix_tokens + cumulative:,} tok, "
                f"max_tokens={cfg.max_tokens}"
            )
            print(f"      first 80: {preview(text)!r}")
        if worker > 1:
            continue
        if len(plan.turns) > 1:
            print(
                f"    workers 2..{len(plan.turns)}: same shape and sizes, seeds "
                f"{plan.seed + 1000 * 2 + 1}..{plan.seed + 1000 * len(plan.turns) + len(worker_turns)}"
            )
    print("")
    print("per-request fields:")
    print('  common:      "stream": true, "temperature": 0.0, "enable_thinking": false')
    print("  warm:        none extra")
    print(f"  burst:       {json.dumps(spec.request_fields, sort_keys=True)}")
    print("  probe:       none extra")
    print("")
    print("measurement per cell:")
    print("  - GET /metrics/prometheus before and after (fallback /metrics JSON)")
    print("  - probe usage.prompt_tokens_details.cached_tokens, timings.prompt_n/prompt_ms")
    print("  - client TTFT = first streamed delta; decode from timings.predicted_n/ms")
    print("  - pressure_ok = parks or evictions rose during the cell; otherwise the")
    print("    cell is invalid and excluded from the gate")
    print("  - row appended to cells.jsonl; summary.md regenerated from every row")
    print("")
    print("notes:")
    print("  - estimates exclude chat-template overhead; the engine's prompt_n is authoritative")
    print("  - token sizing text is deterministic: repeated runs print identical estimates")
    print("  - dry-run performs no HTTP request, opens no output files and creates no directory")


# --- CLI ---------------------------------------------------------------------


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Oracle D park-churn lab for Strata (adoption plan §5).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Arms: A no tier · B spill dir+mib · C B+parallel=2 · "
            "D router strata_prefix · E D+checkpoint off+spread+rewind-keep.\n"
            "Worker prefix: small for A/B/C, full for D/E (--share-prefix overrides).\n"
            "Exit codes: 0 all cells ok and gated arms pass, 2 gate failed "
            "(summary still written), 1 driver error."
        ),
    )
    parser.add_argument("--arm", choices=("A", "B", "C", "D", "E"), default="A")
    parser.add_argument("--base-url", default="http://127.0.0.1:20080/v1")
    parser.add_argument("--model", default="qwen3.8-flash-next")
    parser.add_argument("--warm-tokens", type=int, default=120_000)
    parser.add_argument("--idle-seconds", type=float, default=15.0)
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument(
        "--share-prefix",
        choices=("full", "small"),
        default=None,
        help="worker system prompt: 'small' keeps the corpus only in main "
             "(default for A/B/C; measures eviction/persistence); 'full' makes "
             "workers inherit main's whole prefix (default for D/E; measures pinning)",
    )
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--timeout", type=float, default=600.0)
    parser.add_argument("--max-tokens", type=int, default=64)
    parser.add_argument("--corpus", type=Path, default=None,
                        help="text chunk repeated for the shared prefix; default: the "
                             "Oracle B cache-prefix-chunk.md, else synthetic filler")
    parser.add_argument("--seed", type=int, default=1337,
                        help="seed for deterministic subagent filler")
    parser.add_argument("--rewind-keep", type=int, default=REWIND_KEEP_DEFAULT,
                        help="value printed for arm E's --conversation-cache-rewind-keep")
    parser.add_argument("--background", default="unrecorded — state which services were running",
                        help="pre-flight answers recorded verbatim in summary.md")
    parser.add_argument("--yes", action="store_true",
                        help="skip the interactive pre-flight confirmation")
    parser.add_argument("--dry-run", action="store_true",
                        help="print the full request plan; no network, no output files")
    args = parser.parse_args(argv)

    if args.warm_tokens < 1:
        parser.error("--warm-tokens must be positive")
    if args.k < 1:
        parser.error("--k must be at least 1")
    if args.repeat < 1:
        parser.error("--repeat must be at least 1")
    if args.max_tokens < 1:
        parser.error("--max-tokens must be at least 1")
    if args.idle_seconds < 0:
        parser.error("--idle-seconds cannot be negative")
    if args.rewind_keep < 1:
        parser.error("--rewind-keep must be positive")
    if args.share_prefix is None:
        args.share_prefix = "small" if args.arm in SMALL_PREFIX_ARMS else "full"
    return args


def default_out(arm: str) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return (
        Path(__file__).resolve().parent.parent
        / "scratch"
        / "benchmark-results"
        / f"{stamp}-gfx1100-park-lab-{arm}"
    )


def preflight(args: argparse.Namespace) -> None:
    checklist = [
        "Oracle D pre-flight (plan §5):",
        "  [ ] Pulse is stopped.",
        "  [ ] The omp bridge is disabled (OMP_BRIDGE_SETTINGS=/dev/null).",
        "  [ ] The driving omp session and all its subagents use DeepSeek Flash,",
        "      not the local model under test.",
        "  [ ] This script drives an idle local engine; no omp session is served by it.",
        "  [ ] The arm's configuration is applied (restart done by the operator).",
        f"Recorded background: {args.background}",
    ]
    print("\n".join(checklist), file=sys.stderr, flush=True)
    if args.yes or not sys.stdin.isatty():
        return
    answer = input("Continue with the live measurement? [y/N] ").strip().lower()
    if answer not in ("y", "yes"):
        raise LabError("pre-flight declined")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    script = Path(__file__).resolve()
    try:
        corpus_chunk, corpus_label = resolve_corpus(args.corpus, script)
        spec = arm_spec(args.arm, args.rewind_keep)
        estimator = TokenEstimator()
        if not corpus_chunk:
            corpus_chunk = seeded_text(args.seed, max(4096, args.warm_tokens // 4), estimator)
        corpus_block = fit_text(corpus_chunk, args.warm_tokens, estimator)
        cfg = RunConfig(
            base_url=args.base_url,
            model=args.model,
            timeout=args.timeout,
            max_tokens=args.max_tokens,
            k=args.k,
            idle_seconds=args.idle_seconds,
            arm=args.arm,
            share_prefix=args.share_prefix,
            background=args.background,
            spec=spec,
        )
        out_dir = args.out or default_out(args.arm)
        dry_nonce = "deadbeef"
        plan = build_cell_plan(
            corpus_block,
            dry_nonce,
            args.k,
            args.seed,
            estimator,
            args.share_prefix,
        )
        if args.dry_run:
            print_plan(
                cfg, spec, plan, corpus_label, estimator, out_dir, args.repeat
            )
            return 0

        preflight(args)
    except LabError as exc:
        print(f"strata-park-lab: {exc}", file=sys.stderr)
        return 1

    status = fetch_status(cfg.base_url, min(cfg.timeout, 15.0))
    engine = status.get("engine") or status.get("version") or "n/a"
    print(
        f"engine: {engine} · share_prefix={cfg.share_prefix}",
        file=sys.stderr,
        flush=True,
    )

    out_dir.mkdir(parents=True, exist_ok=True)
    cells_path = out_dir / "cells.jsonl"
    driver_error = False
    written: list[dict[str, Any]] = []
    for repeat in range(1, args.repeat + 1):
        nonce = f"{args.arm}{repeat}-{time.time_ns() % 0xFFFFFF:06x}"
        cell_plan = build_cell_plan(
            corpus_block, nonce, args.k, args.seed, estimator, args.share_prefix
        )
        try:
            row = run_cell(cfg, cell_plan, repeat)
        except KeyboardInterrupt:
            print("strata-park-lab: interrupted", file=sys.stderr)
            driver_error = True
            break
        row["engine"] = engine
        written.append(row)
        with cells_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
        if not row.get("ok"):
            driver_error = True
            print(
                f"[cell {args.arm}/{repeat}] FAILED at {row.get('stage')}: {row.get('error')}",
                file=sys.stderr,
                flush=True,
            )

    all_rows = read_rows(cells_path)
    gate_rc = write_summary(
        out_dir, all_rows, args, corpus_label, estimator.name, spec
    )
    print(f"wrote {cells_path} and {out_dir / 'summary.md'}", file=sys.stderr)
    if driver_error:
        return 1
    return gate_rc


if __name__ == "__main__":
    sys.exit(main())
