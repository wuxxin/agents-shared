#!/usr/bin/env python3
# scripts/local-router.py - Combined Local Inference Router (OpenAI Proxy)
#
# Listens on port 21080 and routes incoming requests dynamically to
# local chat, embedding, rerank, speech-to-text, text-to-speech, and image services.

import asyncio
import atexit
import datetime
import json
import os
import re
import signal
import socket
import sqlite3
import sys
import threading
import time
from contextlib import asynccontextmanager
from typing import Any, Mapping

import httpx
import tiktoken
from fastapi import FastAPI, Request, Response
from fastapi.responses import (
    HTMLResponse,
    JSONResponse,
    PlainTextResponse,
    RedirectResponse,
    StreamingResponse,
)
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    Gauge,
    generate_latest,
)

# Global client for connection pooling
client: httpx.AsyncClient = None  # type: ignore[assignment]  # ty: ignore[invalid-assignment]

# Global model inventory
model_inventory_list: list[dict] = []
model_to_service: dict[str, str] = {}

# Backend availability tracking — services confirmed online by background discovery
available_services: set[str] = set()

# Check for mock backends mode
LROUT_MOCK_BACKENDS = os.environ.get("LROUT_MOCK_BACKENDS", "") in (
    "1",
    "true",
    "TRUE",
    "yes",
)

# --- Client Identification Headers ---

CLIENT_IDENTIFICATION_HEADERS: tuple[str, ...] = (
    "x-client-id",
    "x-agent-id",
    "x-client",
    "x-agent",
)


def sanitize_client_identifier(raw: str | None) -> str | None:
    """Sanitize raw client identifier by stripping quotes, whitespace, and special characters."""
    if not raw:
        return None
    val = raw.strip().strip("'\"").strip()
    if not val:
        return None
    clean = re.sub(r"[^\w\.-]", "", val).strip().lower()
    return clean if clean else None


def resolve_client_id(custom_identifier: str | None = None) -> str:
    """Resolve client identifier strictly from custom HTTP header or body parameter."""
    clean_custom = sanitize_client_identifier(custom_identifier)
    return clean_custom if clean_custom else "unknown"


# --- Usage tracking state ---
STATIC_ERRORS_TEMPLATE = {
    "400": 0,
    "401": 0,
    "403": 0,
    "404": 0,
    "408": 0,
    "429": 0,
    "499": 0,  # Client canceled / abandoned
    "500": 0,
    "502": 0,
    "503": 0,
    "504": 0,
    "OTHER": 0,
}

usage_data_memory: dict[str, dict[str, dict[str, dict[str, dict[str, Any]]]]] = {}
last_written_total_tokens: int = 0
usage_lock = threading.Lock()
save_task: asyncio.Task = None  # type: ignore[assignment]  # ty: ignore[invalid-assignment]

global_active_calls_post: int = 0
global_active_calls_stream: int = 0
active_calls_per_agent: dict[str, dict[str, int]] = {}
active_calls_per_service: dict[str, dict[str, int]] = {}
active_calls_per_model: dict[str, dict[str, int]] = {}
active_calls_lock = threading.RLock()

# --- Prometheus setup ---
metrics_registry = CollectorRegistry()

calls_gauge = Gauge(
    "local_router_calls_total",
    "Cumulative count of calls routed through local-router",
    ["agent", "service", "model"],
    registry=metrics_registry,
)

tokens_gauge = Gauge(
    "local_router_tokens_total",
    "Cumulative count of tokens processed",
    ["agent", "service", "model", "type"],
    registry=metrics_registry,
)

cost_gauge = Gauge(
    "local_router_cost_total",
    "Cumulative estimated cost of routed calls in USD",
    ["agent", "service", "model", "type"],
    registry=metrics_registry,
)

errors_gauge = Gauge(
    "local_router_errors_total",
    "Cumulative count of HTTP errors routed by service, model, call type, and HTTP code",
    ["agent", "service", "model", "call_type", "code"],
    registry=metrics_registry,
)

time_gauge = Gauge(
    "local_router_time_seconds_total",
    "Cumulative time spent in calls in seconds",
    ["agent", "service", "model", "type"],
    registry=metrics_registry,
)

calls_active_gauge = Gauge(
    "local_router_calls_active",
    "Count of current active requests waiting to return",
    ["agent", "service", "model"],
    registry=metrics_registry,
)

client_cancel_gauge = Gauge(
    "local_router_client_cancel_total",
    "Cumulative count of requests canceled or abandoned from client side",
    ["agent", "service", "model"],
    registry=metrics_registry,
)


def print_debug_raw(label: str, raw_bytes: bytes | None):
    if not raw_bytes:
        print(f"[ROUTER DEBUG] {label}: <empty>", file=sys.stderr)
        return
    try:
        decoded = raw_bytes.decode("utf-8", errors="replace")
        try:
            parsed = json.loads(decoded)
            formatted = json.dumps(parsed, indent=2)
            print(f"[ROUTER DEBUG] {label} (JSON):\n{formatted}", file=sys.stderr)
        except Exception:
            print(f"[ROUTER DEBUG] {label} (TEXT):\n{decoded[:4096]}", file=sys.stderr)
    except Exception as exc:
        print(
            f"[ROUTER DEBUG] {label} (BYTES len={len(raw_bytes)}): {exc}",
            file=sys.stderr,
        )


PRICING_REGISTRY: dict[str, dict[str, str]] = {
    "chat": {
        "prompt": "0.00000030",  # $0.30 per 1M tokens (DeepSeek Flash uncached input)
        "completion": "0.00000120",  # $1.20 per 1M tokens (DeepSeek Flash output)
        "input_cache_read": "0.000000006",  # $0.006 per 1M tokens (DeepSeek Flash cache hit)
        "input_cache_write": "0.00000000",  # $0.00 per 1M tokens (no cache write fee)
    },
    "embedding": {
        "prompt": "0.00000015",  # $0.15 per 1M tokens (Gemini Embedding 001)
        "completion": "0.00000000",
        "input_cache_read": "0.00000000",
        "input_cache_write": "0.00000000",
    },
    "rerank": {
        "prompt": "0.00000015",  # $0.15 per 1M tokens (reasonable equivalent to embedding)
        "completion": "0.00000000",
        "input_cache_read": "0.00000000",
        "input_cache_write": "0.00000000",
    },
    "image": {
        "prompt": "0.00000050",  # $0.50 per 1M tokens (Gemini 3.1 Flash Image)
        "completion": "0.00006000",  # $60.00 per 1M tokens (images, $0.067 per 1K image)
        "input_cache_read": "0.00000000",
        "input_cache_write": "0.00000000",
    },
    "tts": {
        "prompt": "0.00000100",  # $1.00 per 1M tokens (Gemini 3.1 Flash TTS text input)
        "completion": "0.00002000",  # $20.00 per 1M tokens (Gemini 3.1 Flash TTS audio output)
        "input_cache_read": "0.00000000",
        "input_cache_write": "0.00000000",
    },
    "stt": {
        "prompt": "0.00000000",
        "completion": "0.00003000",  # OpenAI Whisper ($0.006/min; ~200 tokens/min => $0.00003/token)
        "input_cache_read": "0.00000000",
        "input_cache_write": "0.00000000",
    },
}


DEFAULT_SERVICE_PORTS: dict[str, tuple[str, int]] = {
    "chat": ("127.0.0.1", 20080),
    "embedding": ("127.0.0.1", 20082),
    "rerank": ("127.0.0.1", 20086),
    "stt": ("127.0.0.1", 20090),
    "tts": ("127.0.0.1", 20095),
    "image": ("127.0.0.1", 20100),
}

DEFAULT_SERVICE_ALIASES: dict[str, str] = {
    "chat": "qwen3.6-35B-A3B",
    "embedding": "qwen3-embedding",
    "rerank": "qwen3-reranker",
    "stt": "whisper-1",
    "tts": "kokoro",
    "image": "z-image-turbo",
}

SERVICE_ENV_PREFIXES: dict[str, list[str]] = {
    "chat": ["LROUT_CHAT", "LCHAT"],
    "embedding": ["LROUT_EMBEDDING", "LMBD"],
    "rerank": ["LROUT_RERANK", "LRR"],
    "stt": ["LROUT_STT", "LSTT"],
    "tts": ["LROUT_TTS", "LTTS"],
    "image": ["LROUT_IMAGE", "LIMG"],
}

SERVICE_TIMEOUT_DEFAULTS: dict[str, float] = {
    "image": 900.0,
    "chat": 600.0,
    "tts": 300.0,
    "stt": 300.0,
    "embedding": 120.0,
    "rerank": 120.0,
}


def resolve_service_alias(name: str) -> str:
    """Resolve the alias for a service from environment variables or built-in defaults."""
    if name == "chat":
        strata_val = os.environ.get("LCHAT_STRATA_ENABLED", "0")
        if strata_val.lower() not in ("0", "false", "no"):
            return os.environ.get("LCHAT_STRATA_ALIAS", "qwen3.8-flash-next")
        return (
            os.environ.get("LROUT_CHAT_ALIAS")
            or os.environ.get("LCHAT_ALIAS")
            or DEFAULT_SERVICE_ALIASES["chat"]
        )

    prefixes = SERVICE_ENV_PREFIXES.get(name, [f"LROUT_{name.upper()}"])
    for pfx in prefixes:
        val = os.environ.get(f"{pfx}_ALIAS")
        if val:
            return val
    return DEFAULT_SERVICE_ALIASES.get(name, "")


def resolve_service_from_model_id(model_id: str, default_svc: str) -> str:
    """Resolve the proper service name for a given model ID to apply correct pricing and mapping."""
    model_lower = model_id.lower()
    if "embedding" in model_lower:
        return "embedding"
    elif "reranker" in model_lower or "rerank" in model_lower:
        return "rerank"
    elif "tts" in model_lower or "kokoro" in model_lower:
        return "tts"
    elif "whisper" in model_lower or "stt" in model_lower:
        return "stt"
    elif "image" in model_lower:
        return "image"
    return default_svc


def get_enabled_services() -> dict[str, bool]:
    """Determine which services are expected to be online using environment variable switches."""

    def is_enabled(pfx: str, default: bool) -> bool:
        for var in [f"LROUT_{pfx}_ENABLED", f"L{pfx[:3]}_ENABLED"]:
            val = os.environ.get(var)
            if val is not None:
                return val.lower() not in ("0", "false", "no")
        return default

    strata_active = os.environ.get("LCHAT_STRATA_ENABLED", "0").lower() not in ("0", "false", "no")
    chat_active = is_enabled("CHAT", True) or strata_active

    return {
        "chat": chat_active,
        "embedding": is_enabled("EMBEDDING", False),  # 0 (combined mode) by default
        "rerank": is_enabled("RERANK", True),
        "stt": is_enabled("STT", True),
        "tts": is_enabled("TTS", True),
        "image": is_enabled("IMAGE", True),
    }


async def check_service(name: str, url: str) -> list[dict] | None:
    """Check if a service is available.

    Returns a list of models if available, or None if not available.
    """
    match = re.search(r"//([^/:]+)(?::(\d+))?", url)
    if not match:
        if is_debug():
            print(
                f"[ROUTER CHECK] Invalid URL '{url}' for service '{name}'",
                file=sys.stderr,
            )
        return None
    host = match.group(1)
    port = int(match.group(2)) if match.group(2) else 80

    if is_debug():
        print(f"[ROUTER CHECK] Probing service '{name}' at {url}...", file=sys.stderr)

    if name in ("chat", "embedding", "rerank", "tts"):
        try:
            models_url = f"{url}/v1/models"
            if is_debug():
                print(f"[ROUTER CHECK] Attempting GET {models_url}...", file=sys.stderr)
            resp = await client.get(models_url, timeout=1.0)
            if is_debug():
                print(
                    f"[ROUTER CHECK] GET {models_url} -> status {resp.status_code}",
                    file=sys.stderr,
                )
            if resp.status_code == 200:
                data = resp.json().get("data", [])
                return data
            elif resp.status_code == 404:
                health_url = f"{url}/health"
                if is_debug():
                    print(
                        f"[ROUTER CHECK] GET {models_url} returned 404. Probing fallback GET {health_url}...",
                        file=sys.stderr,
                    )
                hresp = await client.get(health_url, timeout=1.0)
                if is_debug():
                    print(
                        f"[ROUTER CHECK] GET {health_url} -> status {hresp.status_code}",
                        file=sys.stderr,
                    )
                if hresp.status_code == 200:
                    return []
        except Exception as exc:
            if is_debug():
                print(
                    f"[ROUTER CHECK] Probe error for '{name}' at {url}: {exc}",
                    file=sys.stderr,
                )
            pass
        if name == "tts":
            try:
                reader, writer = await asyncio.open_connection(host, port)
                writer.close()
                await writer.wait_closed()
                return []
            except Exception:
                return None
    else:
        # For STT and Image: check if port is open
        try:
            if is_debug():
                print(
                    f"[ROUTER CHECK] Opening TCP connection to {host}:{port} for '{name}'...",
                    file=sys.stderr,
                )
            reader, writer = await asyncio.open_connection(host, port)
            writer.close()
            await writer.wait_closed()
            if is_debug():
                print(
                    f"[ROUTER CHECK] TCP connection to {host}:{port} for '{name}' succeeded.",
                    file=sys.stderr,
                )
            return []
        except Exception as exc:
            if is_debug():
                print(
                    f"[ROUTER CHECK] TCP connection to {host}:{port} for '{name}' failed: {exc}",
                    file=sys.stderr,
                )
            return None


def _init_fallback_inventory():
    """Seed inventory with alias-based entries so the router responds immediately at startup."""
    global model_inventory_list, model_to_service
    model_inventory_list = []
    model_to_service = {}

    for name in ["chat", "embedding", "rerank", "stt", "tts", "image"]:
        alias = resolve_service_alias(name)
        if alias:
            true_svc = resolve_service_from_model_id(alias, name)
            model_to_service[alias] = true_svc
            entry: dict[str, Any] = {
                "id": alias,
                "object": "model",
                "owned_by": "local-inference",
            }
            pricing = PRICING_REGISTRY.get(true_svc)
            if pricing:
                entry["pricing"] = pricing
            model_inventory_list.append(entry)
            # Chat service thinking variants and secondary aliases
            if name == "chat":
                thinking_id = f"{alias}-thinking"
                model_to_service[thinking_id] = name
                thinking_entry: dict[str, Any] = {
                    "id": thinking_id,
                    "object": "model",
                    "owned_by": "local-inference",
                }
                if pricing:
                    thinking_entry["pricing"] = pricing
                model_inventory_list.append(thinking_entry)

                # Legacy compatibility aliases
                if alias != "qwen3":
                    model_to_service["qwen3"] = name
                    model_to_service["qwen3-thinking"] = name
                    legacy_entry: dict[str, Any] = {
                        "id": "qwen3",
                        "object": "model",
                        "owned_by": "local-inference",
                    }
                    if pricing:
                        legacy_entry["pricing"] = pricing
                    model_inventory_list.append(legacy_entry)

                # Register secondary aliases from env
                sec_str = (
                    os.environ.get("LROUT_CHAT_ALIASES")
                    or os.environ.get("LCHAT_STRATA_ALIASES")
                    or os.environ.get("LCHAT_ALIASES", "qwen3.6-moe,qwen3.6,qwen3")
                )
                for sa in [s.strip() for s in sec_str.split(",") if s.strip()]:
                    model_to_service[sa] = name
                    model_to_service[f"{sa}-thinking"] = name
                    if not any(m.get("id") == sa for m in model_inventory_list):
                        sa_entry: dict[str, Any] = {
                            "id": sa,
                            "object": "model",
                            "owned_by": "local-inference",
                        }
                        if pricing:
                            sa_entry["pricing"] = pricing
                        model_inventory_list.append(sa_entry)


def _merge_discovered_models(svc_name: str, models: list[dict]):
    """Merge dynamically discovered models into the global inventory."""
    global model_inventory_list, model_to_service, available_services

    available_services.add(svc_name)

    for model_data in models:
        m_id = model_data.get("id")
        if not m_id:
            continue
        true_svc = resolve_service_from_model_id(m_id, svc_name)
        model_to_service[m_id] = true_svc

        if not any(m.get("id") == m_id for m in model_inventory_list):
            entry: dict[str, Any] = {
                "id": m_id,
                "object": "model",
                "owned_by": "local-inference",
            }
            pricing = PRICING_REGISTRY.get(true_svc)
            if pricing:
                entry["pricing"] = pricing
            model_inventory_list.append(entry)
            print(
                f"[DISCOVERY] Service '{svc_name}' available — added model: {m_id}",
                file=sys.stderr,
            )


async def discover_services_background():
    """Background task: seed fallback inventory, then discover backends.

    Starts asynchronously on router start. Probes enabled services every 2s during
    initial startup phase (up to 120 seconds). If not all expected services are up
    within 120 seconds, logs critical error and aborts process.
    Once all expected services are detected, switches to periodic background polling (10s).
    """
    global model_inventory_list, model_to_service, available_services

    if LROUT_MOCK_BACKENDS:
        chat_alias = resolve_service_alias("chat") or "qwen3"
        model_inventory_list = [
            {
                "id": chat_alias,
                "object": "model",
                "owned_by": "local-inference",
                "pricing": PRICING_REGISTRY["chat"],
            },
            {
                "id": f"{chat_alias}-thinking",
                "object": "model",
                "owned_by": "local-inference",
                "pricing": PRICING_REGISTRY["chat"],
            },
            {
                "id": "qwen3",
                "object": "model",
                "owned_by": "local-inference",
                "pricing": PRICING_REGISTRY["chat"],
            },
            {
                "id": "qwen3-thinking",
                "object": "model",
                "owned_by": "local-inference",
                "pricing": PRICING_REGISTRY["chat"],
            },
            {
                "id": "qwen3-embedding",
                "object": "model",
                "owned_by": "local-inference",
                "pricing": PRICING_REGISTRY["embedding"],
            },
            {
                "id": "qwen3-reranker",
                "object": "model",
                "owned_by": "local-inference",
                "pricing": PRICING_REGISTRY["rerank"],
            },
            {
                "id": "whisper-1",
                "object": "model",
                "owned_by": "local-inference",
                "pricing": PRICING_REGISTRY["stt"],
            },
            {
                "id": "kokoro",
                "object": "model",
                "owned_by": "local-inference",
                "pricing": PRICING_REGISTRY["tts"],
            },
            {
                "id": "kokoro-tts",
                "object": "model",
                "owned_by": "local-inference",
                "pricing": PRICING_REGISTRY["tts"],
            },
            {
                "id": "qwen3-tts",
                "object": "model",
                "owned_by": "local-inference",
                "pricing": PRICING_REGISTRY["tts"],
            },
            {
                "id": "z-image-turbo",
                "object": "model",
                "owned_by": "local-inference",
                "pricing": PRICING_REGISTRY["image"],
            },
        ]
        model_to_service = {
            chat_alias: "chat",
            f"{chat_alias}-thinking": "chat",
            "qwen3": "chat",
            "qwen3-thinking": "chat",
            "qwen3-embedding": "embedding",
            "qwen3-reranker": "rerank",
            "whisper-1": "stt",
            "kokoro": "tts",
            "kokoro-tts": "tts",
            "qwen3-tts": "tts",
            "z-image-turbo": "image",
        }
        for s in ["chat", "embedding", "rerank", "stt", "tts", "image"]:
            available_services.add(s)
        return

    # Seed inventory from configured aliases so the router works immediately
    _init_fallback_inventory()
    print(f"[DISCOVERY] Fallback inventory seeded: {[m['id'] for m in model_inventory_list]}")

    enabled_services = get_enabled_services()
    expected_services = [
        name
        for name, enabled in enabled_services.items()
        if enabled and not (name == "embedding" and not enabled_services["embedding"])
    ]
    print(f"[DISCOVERY] Async startup service detection (timeout 120s): {expected_services}")

    # Phase 1: Async startup synchronization (up to 120s timeout)
    start_time = asyncio.get_event_loop().time()
    timeout = 120.0
    poll_interval = 2.0

    while True:
        try:
            config = resolve_config()
            for name in expected_services:
                if name not in available_services:
                    res = await check_service(name, config[name])
                    if res is not None:
                        _merge_discovered_models(name, res)

            missing = [s for s in expected_services if s not in available_services]
            if not missing:
                print(
                    f"[DISCOVERY] All expected inference services are online and ready! ({expected_services})"
                )
                break

            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed >= timeout:
                print(
                    f"CRITICAL: Not all expected inference services came online within 120 seconds. "
                    f"Missing services: {', '.join(missing)}. Aborting.",
                    file=sys.stderr,
                )
                os._exit(1)

            await asyncio.sleep(poll_interval)
        except asyncio.CancelledError:
            return
        except Exception as exc:
            print(f"[DISCOVERY] Startup probe error: {exc}", file=sys.stderr)
            await asyncio.sleep(poll_interval)

    # Phase 2: Ongoing background polling loop (60s)
    print("[DISCOVERY] Transitioning to periodic background polling every 60s...")
    while True:
        try:
            config = resolve_config()
            for name in expected_services:
                res = await check_service(name, config[name])
                if res is not None:
                    _merge_discovered_models(name, res)
        except asyncio.CancelledError:
            break
        except Exception as exc:
            print(f"[DISCOVERY] Error: {exc}", file=sys.stderr)
        await asyncio.sleep(60.0)


def resolve_target_service(model_name: str) -> str:
    """Resolve the target service name ('chat', 'embedding', etc.) based on the requested model name."""
    if not model_name:
        default_model = os.environ.get("LROUT_DEFAULT_MODEL", "").strip()
        if default_model and default_model in model_to_service:
            return model_to_service[default_model]
        chat_alias = resolve_service_alias("chat")
        if chat_alias and chat_alias in model_to_service:
            return model_to_service[chat_alias]
        return "chat"

    # Exact match in inventory
    if model_name in model_to_service:
        return model_to_service[model_name]

    # Clean thinking suffix check
    if model_name.endswith("-thinking"):
        base_name = model_name[:-9]
        if base_name in model_to_service:
            return model_to_service[base_name]

    # Fallback substring matching rules
    if "embedding" in model_name.lower():
        return "embedding"
    elif "rerank" in model_name.lower():
        return "rerank"
    return "chat"


def resolve_target_service_and_model(model_name: str) -> tuple[str, str]:
    """Resolve both the target service name and normalized model name."""
    clean = model_name.strip() if isinstance(model_name, str) else ""
    if not clean:
        default_model = os.environ.get("LROUT_DEFAULT_MODEL", "").strip()
        resolved_model = default_model or resolve_service_alias("chat") or "qwen3"
    else:
        resolved_model = clean
    return resolve_target_service(resolved_model), resolved_model


# --- Usage Tracking helper functions ---


def get_token_count(text: str) -> int:
    """Helper to count tokens in a string using tiktoken (cl100k_base)."""
    if not text:
        return 0
    try:
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
    except Exception:
        return len(text.split())


_db_conn: sqlite3.Connection | None = None
_db_lock = threading.Lock()


def get_usage_db_path() -> str:
    state_dir = os.environ.get("XDG_STATE_HOME") or os.path.expanduser("~/.local/state")
    target_dir = os.path.join(state_dir, "local-router")
    os.makedirs(target_dir, exist_ok=True)
    return os.path.join(target_dir, "local-router-usage.db")


def get_usage_file_path() -> str:
    """Backward compatibility alias pointing to SQLite usage DB."""
    return get_usage_db_path()


def get_db_connection() -> sqlite3.Connection:
    global _db_conn
    with _db_lock:
        if _db_conn is None:
            db_path = get_usage_db_path()
            conn = sqlite3.connect(db_path, check_same_thread=False, timeout=30.0)
            conn.execute("PRAGMA journal_mode = WAL;")
            conn.execute("PRAGMA synchronous = NORMAL;")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS request_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    date TEXT,
                    agent TEXT,
                    service TEXT,
                    model TEXT,
                    uncached_input INTEGER,
                    cached_input INTEGER,
                    cached_write INTEGER,
                    output INTEGER,
                    is_streaming INTEGER,
                    status_code INTEGER,
                    duration REAL
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_requests_date ON request_events(date);")
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_requests_agent_model ON request_events(agent, model);"
            )
            conn.execute("""
                CREATE TABLE IF NOT EXISTS daily_aggregates (
                    date TEXT,
                    agent TEXT,
                    service TEXT,
                    model TEXT,
                    calls INTEGER DEFAULT 0,
                    streaming_calls INTEGER DEFAULT 0,
                    calls_post INTEGER DEFAULT 0,
                    uncached_input INTEGER DEFAULT 0,
                    cached_input INTEGER DEFAULT 0,
                    cached_write INTEGER DEFAULT 0,
                    output INTEGER DEFAULT 0,
                    duration_post REAL DEFAULT 0.0,
                    duration_streaming REAL DEFAULT 0.0,
                    errors_streaming_json TEXT DEFAULT '{}',
                    errors_post_json TEXT DEFAULT '{}',
                    PRIMARY KEY (date, agent, service, model)
                );
            """)
            conn.commit()
            _db_conn = conn
        return _db_conn


def add_usage_record(
    agent: str,
    service: str,
    model: str,
    uncached_input: int,
    cached_input: int,
    cached_write: int,
    output: int,
    is_streaming: bool,
    status_code: int = 200,
    duration: float = 0.0,
):
    agent = agent or "unknown"
    service = service or "unknown"
    model = model or "unknown"
    today = datetime.date.today().isoformat()
    timestamp = time.time()

    with usage_lock:
        if today not in usage_data_memory:
            usage_data_memory[today] = {}
        if agent not in usage_data_memory[today]:
            usage_data_memory[today][agent] = {}
        if service not in usage_data_memory[today][agent]:
            usage_data_memory[today][agent][service] = {}
        if model not in usage_data_memory[today][agent][service]:
            usage_data_memory[today][agent][service][model] = {
                "calls": 0,
                "streaming_calls": 0,
                "calls_post": 0,
                "input": 0,
                "cached_input": 0,
                "cached_write": 0,
                "output": 0,
                "errors_streaming": dict(STATIC_ERRORS_TEMPLATE),
                "errors_post": dict(STATIC_ERRORS_TEMPLATE),
                "duration_post": 0.0,
                "duration_streaming": 0.0,
                "_req_input_vals": [],
                "_req_cached_input_vals": [],
                "_req_cached_write_vals": [],
                "_req_output_vals": [],
                "_req_total_vals": [],
                "_req_total_input_vals": [],
                "_req_uniq_input_vals": [],
            }

        entry = usage_data_memory[today][agent][service][model]

        entry["calls"] += 1
        if is_streaming:
            entry["streaming_calls"] += 1
            entry["duration_streaming"] += duration
        else:
            entry["calls_post"] += 1
            entry["duration_post"] += duration

        entry["input"] += uncached_input
        entry["cached_input"] += cached_input
        entry["cached_write"] += cached_write
        entry["output"] += output

        total_input_req = uncached_input + cached_input
        per_request_total = total_input_req + cached_write + output

        entry["_req_total_input_vals"].append(total_input_req)
        entry["_req_cached_input_vals"].append(cached_input)
        entry["_req_cached_write_vals"].append(cached_write)
        entry["_req_uniq_input_vals"].append(uncached_input)
        entry["_req_output_vals"].append(output)
        entry["_req_total_vals"].append(per_request_total)
        entry["_req_input_vals"].append(total_input_req)

        max_in_mem = 500
        if len(entry["_req_total_vals"]) > max_in_mem:
            entry["_req_total_input_vals"] = entry["_req_total_input_vals"][-max_in_mem:]
            entry["_req_cached_input_vals"] = entry["_req_cached_input_vals"][-max_in_mem:]
            entry["_req_cached_write_vals"] = entry["_req_cached_write_vals"][-max_in_mem:]
            entry["_req_uniq_input_vals"] = entry["_req_uniq_input_vals"][-max_in_mem:]
            entry["_req_output_vals"] = entry["_req_output_vals"][-max_in_mem:]
            entry["_req_total_vals"] = entry["_req_total_vals"][-max_in_mem:]
            entry["_req_input_vals"] = entry["_req_input_vals"][-max_in_mem:]

        if status_code >= 400:
            code_str = str(status_code)
            error_dict = entry["errors_streaming"] if is_streaming else entry["errors_post"]
            if code_str in error_dict:
                error_dict[code_str] += 1
            else:
                error_dict["OTHER"] += 1

        err_str_json = json.dumps(entry["errors_streaming"])
        err_post_json = json.dumps(entry["errors_post"])

    # Persist incrementally to SQLite WAL
    conn = get_db_connection()
    with _db_lock:
        try:
            conn.execute(
                """
                INSERT INTO request_events (
                    timestamp, date, agent, service, model,
                    uncached_input, cached_input, cached_write, output,
                    is_streaming, status_code, duration
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
                (
                    timestamp,
                    today,
                    agent,
                    service,
                    model,
                    uncached_input,
                    cached_input,
                    cached_write,
                    output,
                    1 if is_streaming else 0,
                    status_code,
                    duration,
                ),
            )
            conn.execute(
                """
                INSERT INTO daily_aggregates (
                    date, agent, service, model,
                    calls, streaming_calls, calls_post,
                    uncached_input, cached_input, cached_write, output,
                    duration_post, duration_streaming,
                    errors_streaming_json, errors_post_json
                ) VALUES (
                    ?, ?, ?, ?,
                    1, ?, ?,
                    ?, ?, ?, ?,
                    ?, ?,
                    ?, ?
                )
                ON CONFLICT(date, agent, service, model) DO UPDATE SET
                    calls = calls + 1,
                    streaming_calls = streaming_calls + excluded.streaming_calls,
                    calls_post = calls_post + excluded.calls_post,
                    uncached_input = uncached_input + excluded.uncached_input,
                    cached_input = cached_input + excluded.cached_input,
                    cached_write = cached_write + excluded.cached_write,
                    output = output + excluded.output,
                    duration_post = duration_post + excluded.duration_post,
                    duration_streaming = duration_streaming + excluded.duration_streaming,
                    errors_streaming_json = excluded.errors_streaming_json,
                    errors_post_json = excluded.errors_post_json;
            """,
                (
                    today,
                    agent,
                    service,
                    model,
                    1 if is_streaming else 0,
                    0 if is_streaming else 1,
                    uncached_input,
                    cached_input,
                    cached_write,
                    output,
                    0.0 if is_streaming else duration,
                    duration if is_streaming else 0.0,
                    err_str_json,
                    err_post_json,
                ),
            )
            conn.commit()
        except Exception as exc:
            print(f"Error persisting usage to SQLite: {exc}", file=sys.stderr)


def load_usage_data():
    global usage_data_memory, last_written_total_tokens
    usage_data_memory = {}
    conn = get_db_connection()
    with _db_lock:
        cursor = conn.execute("""
            SELECT date, agent, service, model,
                   calls, streaming_calls, calls_post,
                   uncached_input, cached_input, cached_write, output,
                   duration_post, duration_streaming,
                   errors_streaming_json, errors_post_json
            FROM daily_aggregates
        """)
        for row in cursor.fetchall():
            day, agent, service, model = row[0], row[1], row[2], row[3]
            if day not in usage_data_memory:
                usage_data_memory[day] = {}
            if agent not in usage_data_memory[day]:
                usage_data_memory[day][agent] = {}
            if service not in usage_data_memory[day][agent]:
                usage_data_memory[day][agent][service] = {}

            try:
                err_str = json.loads(row[13])
            except Exception:
                err_str = dict(STATIC_ERRORS_TEMPLATE)
            try:
                err_post = json.loads(row[14])
            except Exception:
                err_post = dict(STATIC_ERRORS_TEMPLATE)

            usage_data_memory[day][agent][service][model] = {
                "calls": row[4],
                "streaming_calls": row[5],
                "calls_post": row[6],
                "input": row[7],
                "cached_input": row[8],
                "cached_write": row[9],
                "output": row[10],
                "duration_post": row[11],
                "duration_streaming": row[12],
                "errors_streaming": err_str,
                "errors_post": err_post,
                "_req_total_input_vals": [],
                "_req_cached_input_vals": [],
                "_req_cached_write_vals": [],
                "_req_uniq_input_vals": [],
                "_req_output_vals": [],
                "_req_total_vals": [],
                "_req_input_vals": [],
            }
    today = datetime.date.today().isoformat()
    last_written_total_tokens = get_total_tokens_for_day(today)


def get_total_tokens_for_day(day: str) -> int:
    total = 0
    if day in usage_data_memory:
        for _agent, services_map in usage_data_memory[day].items():
            if not isinstance(services_map, dict):
                continue
            for _service, models_map in services_map.items():
                if not isinstance(models_map, dict):
                    continue
                for _model, counts in models_map.items():
                    if isinstance(counts, dict):
                        total += counts.get("input", 0)
                        total += counts.get("cached_input", 0)
                        total += counts.get("cached_write", 0)
                        total += counts.get("output", 0)
    return total


def check_and_save_usage(force=False):
    global last_written_total_tokens
    today = datetime.date.today().isoformat()
    last_written_total_tokens = get_total_tokens_for_day(today)
    conn = get_db_connection()
    with _db_lock:
        try:
            conn.commit()
            conn.execute("PRAGMA wal_checkpoint(PASSIVE);")
        except Exception as e:
            print(f"Error checking usage db: {e}")


async def periodic_save_task():
    while True:
        await asyncio.sleep(600)  # 10 minutes
        try:
            check_and_save_usage()
        except Exception as e:
            print(f"Error in periodic save: {e}")


def compute_req_stats(vals: list[int]) -> dict[str, int]:
    """Compute min, median, max from a list of integer values."""
    if not vals:
        return {"min": 0, "median": 0, "max": 0}
    sorted_vals = sorted(vals)
    n = len(sorted_vals)
    if n % 2 == 1:
        median = sorted_vals[n // 2]
    else:
        median = (sorted_vals[n // 2 - 1] + sorted_vals[n // 2]) // 2
    return {"min": sorted_vals[0], "median": median, "max": sorted_vals[-1]}


def get_cumulative_metrics(
    day_filter: str | None = None, range_filter: str | None = None
) -> dict[str, Any]:
    models_acc: dict[str, dict[str, Any]] = {}
    agents_acc: dict[str, dict[str, Any]] = {}
    services_acc: dict[str, dict[str, Any]] = {}
    daily_acc: dict[str, dict[str, Any]] = {}

    def _new_acc_dict() -> dict[str, Any]:
        return {
            "calls": 0,
            "streaming_calls": 0,
            "calls_post": 0,
            "calls_active_post": 0,
            "calls_active_stream": 0,
            "calls_active": 0,
            "input": 0,
            "cached_input": 0,
            "cached_write": 0,
            "output": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "cache_pct": 0.0,
            "costs": {
                "cached_input_cost": 0.0,
                "input_cost": 0.0,
                "cached_write_cost": 0.0,
                "output_cost": 0.0,
                "total_cost": 0.0,
            },
            "errors_streaming": dict(STATIC_ERRORS_TEMPLATE),
            "errors_post": dict(STATIC_ERRORS_TEMPLATE),
            "duration_post": 0.0,
            "duration_streaming": 0.0,
            "total_duration": 0.0,
            "_req_total_input_vals": [],
            "_req_cached_input_vals": [],
            "_req_cached_write_vals": [],
            "_req_uniq_input_vals": [],
            "_req_output_vals": [],
            "_req_total_vals": [],
            "_req_input_vals": [],
        }

    totals_acc = _new_acc_dict()

    today = datetime.date.today()
    days_to_process = []

    with usage_lock:
        if day_filter:
            days_to_process = [day_filter]
        elif range_filter:
            if range_filter == "today" or range_filter == "1d":
                days_to_process = [today.isoformat()]
            elif range_filter == "7d":
                days_to_process = [
                    (today - datetime.timedelta(days=i)).isoformat() for i in range(7)
                ]
            elif range_filter == "30d":
                days_to_process = [
                    (today - datetime.timedelta(days=i)).isoformat() for i in range(30)
                ]
            elif range_filter == "90d":
                days_to_process = [
                    (today - datetime.timedelta(days=i)).isoformat() for i in range(90)
                ]
            else:
                days_to_process = list(usage_data_memory.keys())
        else:
            days_to_process = list(usage_data_memory.keys())

        for day in sorted(days_to_process):
            day_data = usage_data_memory.get(day, {})
            if day not in daily_acc:
                daily_acc[day] = _new_acc_dict()

            for agent, services_map in day_data.items():
                if not isinstance(services_map, dict):
                    continue
                if agent not in agents_acc:
                    agents_acc[agent] = _new_acc_dict()

                for service, models_map in services_map.items():
                    if not isinstance(models_map, dict):
                        continue
                    if service not in services_acc:
                        services_acc[service] = _new_acc_dict()

                    pricing = PRICING_REGISTRY.get(service, {})
                    cost_prompt = float(pricing.get("prompt", "0.0"))
                    cost_completion = float(pricing.get("completion", "0.0"))
                    cost_cache_read = float(pricing.get("input_cache_read", "0.0"))
                    cost_cache_write = float(pricing.get("input_cache_write", "0.0"))

                    for model, counts in models_map.items():
                        if not isinstance(counts, dict):
                            continue
                        model_key = f"{agent}:{model}:{service}"
                        if model_key not in models_acc:
                            models_acc[model_key] = _new_acc_dict()

                        calls = counts.get("calls", 0)
                        str_calls = counts.get("streaming_calls", 0)
                        norm_calls = counts.get("calls_post", counts.get("normal_calls", 0))
                        if str_calls == 0 and norm_calls == 0 and calls > 0:
                            norm_calls = calls

                        inp = counts.get("input", 0)
                        c_inp = counts.get("cached_input", 0)
                        c_wr = counts.get("cached_write", 0)
                        out = counts.get("output", 0)
                        tot = inp + c_inp + c_wr + out

                        c_inp_cost = c_inp * cost_cache_read
                        inp_cost = inp * cost_prompt
                        c_wr_cost = c_wr * cost_cache_write
                        out_cost = out * cost_completion
                        tot_cost = c_inp_cost + inp_cost + c_wr_cost + out_cost

                        dur_post = counts.get("duration_post", 0.0)
                        dur_str = counts.get("duration_streaming", 0.0)
                        tot_dur = dur_post + dur_str

                        src_tot_in = (
                            counts.get("_req_total_input_vals")
                            or counts.get("_req_input_vals")
                            or []
                        )
                        src_c_in = counts.get("_req_cached_input_vals") or []
                        src_c_wr = counts.get("_req_cached_write_vals") or []
                        src_u_in = counts.get("_req_uniq_input_vals") or []
                        src_out = counts.get("_req_output_vals") or []
                        src_tot = counts.get("_req_total_vals") or []

                        def accum(target: dict[str, Any]):
                            target["calls"] += calls
                            target["streaming_calls"] += str_calls
                            target["calls_post"] += norm_calls
                            target["input"] += inp
                            target["cached_input"] += c_inp
                            target["cached_write"] += c_wr
                            target["output"] += out
                            target["total_tokens"] += tot
                            target["costs"]["cached_input_cost"] += c_inp_cost
                            target["costs"]["input_cost"] += inp_cost
                            target["costs"]["cached_write_cost"] += c_wr_cost
                            target["costs"]["output_cost"] += out_cost
                            target["costs"]["total_cost"] += tot_cost
                            target["duration_post"] += dur_post
                            target["duration_streaming"] += dur_str
                            target["total_duration"] += tot_dur
                            for code in STATIC_ERRORS_TEMPLATE:
                                err_str_val = counts.get("errors_streaming", {}).get(code, 0)
                                err_post_val = counts.get("errors_post", {}).get(code, 0)
                                target["errors_streaming"][code] += err_str_val
                                target["errors_post"][code] += err_post_val

                            if src_tot_in:
                                target["_req_total_input_vals"].extend(src_tot_in)
                            if src_c_in:
                                target["_req_cached_input_vals"].extend(src_c_in)
                            if src_c_wr:
                                target["_req_cached_write_vals"].extend(src_c_wr)
                            if src_u_in:
                                target["_req_uniq_input_vals"].extend(src_u_in)
                            if src_out:
                                target["_req_output_vals"].extend(src_out)
                            if src_tot:
                                target["_req_total_vals"].extend(src_tot)

                        accum(models_acc[model_key])
                        accum(agents_acc[agent])
                        accum(services_acc[service])
                        accum(totals_acc)

                        daily_target = daily_acc[day]
                        daily_target["calls"] += calls
                        daily_target["streaming_calls"] += str_calls
                        daily_target["calls_post"] += norm_calls
                        daily_target["input"] += inp
                        daily_target["cached_input"] += c_inp
                        daily_target["cached_write"] += c_wr
                        daily_target["output"] += out
                        daily_target["total_tokens"] += tot
                        daily_target["total_cost"] += tot_cost
                        daily_target["duration_post"] += dur_post
                        daily_target["duration_streaming"] += dur_str
                        daily_target["total_duration"] += tot_dur
                        for code in STATIC_ERRORS_TEMPLATE:
                            daily_target["errors_streaming"][code] = daily_target.get(
                                "errors_streaming", {}
                            ).get(code, 0) + counts.get("errors_streaming", {}).get(code, 0)
                            daily_target["errors_post"][code] = daily_target.get(
                                "errors_post", {}
                            ).get(code, 0) + counts.get("errors_post", {}).get(code, 0)

                        if src_tot_in:
                            daily_target["_req_total_input_vals"].extend(src_tot_in)
                        if src_c_in:
                            daily_target["_req_cached_input_vals"].extend(src_c_in)
                        if src_c_wr:
                            daily_target["_req_cached_write_vals"].extend(src_c_wr)
                        if src_u_in:
                            daily_target["_req_uniq_input_vals"].extend(src_u_in)
                        if src_out:
                            daily_target["_req_output_vals"].extend(src_out)
                        if src_tot:
                            daily_target["_req_total_vals"].extend(src_tot)

    for entry in models_acc.values():
        total_inp = entry["cached_input"] + entry["input"]
        entry["cache_pct"] = (entry["cached_input"] / total_inp * 100.0) if total_inp > 0 else 0.0

    for entry in agents_acc.values():
        total_inp = entry["cached_input"] + entry["input"]
        entry["cache_pct"] = (entry["cached_input"] / total_inp * 100.0) if total_inp > 0 else 0.0

    for entry in services_acc.values():
        total_inp = entry["cached_input"] + entry["input"]
        entry["cache_pct"] = (entry["cached_input"] / total_inp * 100.0) if total_inp > 0 else 0.0

    total_inp = totals_acc["cached_input"] + totals_acc["input"]
    totals_acc["cache_pct"] = (
        (totals_acc["cached_input"] / total_inp * 100.0) if total_inp > 0 else 0.0
    )

    # Compute per-request statistics for all buckets
    def _finalize_req_stats(bucket_dict):
        for entry in bucket_dict.values():
            src_tot_in = entry.pop("_req_total_input_vals", [])
            src_c_in = entry.pop("_req_cached_input_vals", [])
            src_c_wr = entry.pop("_req_cached_write_vals", [])
            src_u_in = entry.pop("_req_uniq_input_vals", [])
            src_out = entry.pop("_req_output_vals", [])
            src_tot = entry.pop("_req_total_vals", [])

            src_legacy = entry.pop("_req_input_vals", [])
            if not src_tot_in and src_legacy:
                src_tot_in = list(src_legacy)
            if not src_u_in and src_legacy:
                src_u_in = list(src_legacy)

            entry["req_stats"] = {
                "total_input": compute_req_stats(src_tot_in),
                "cached_input": compute_req_stats(src_c_in),
                "cached_write": compute_req_stats(src_c_wr),
                "uniq_input": compute_req_stats(src_u_in),
                "output": compute_req_stats(src_out),
                "per_request": compute_req_stats(src_tot),
                # Backward compatibility aliases
                "input": compute_req_stats(src_tot_in),
                "input_read": compute_req_stats(src_c_in),
                "input_write": compute_req_stats(src_c_wr),
            }

    _finalize_req_stats(models_acc)
    _finalize_req_stats(agents_acc)
    _finalize_req_stats(services_acc)
    _finalize_req_stats(daily_acc)

    # Compute for totals_acc as well
    src_tot_in = totals_acc.pop("_req_total_input_vals", [])
    src_c_in = totals_acc.pop("_req_cached_input_vals", [])
    src_c_wr = totals_acc.pop("_req_cached_write_vals", [])
    src_u_in = totals_acc.pop("_req_uniq_input_vals", [])
    src_out = totals_acc.pop("_req_output_vals", [])
    src_tot = totals_acc.pop("_req_total_vals", [])

    src_legacy = totals_acc.pop("_req_input_vals", [])
    if not src_tot_in and src_legacy:
        src_tot_in = list(src_legacy)
    if not src_u_in and src_legacy:
        src_u_in = list(src_legacy)

    totals_acc["req_stats"] = {
        "total_input": compute_req_stats(src_tot_in),
        "cached_input": compute_req_stats(src_c_in),
        "cached_write": compute_req_stats(src_c_wr),
        "uniq_input": compute_req_stats(src_u_in),
        "output": compute_req_stats(src_out),
        "per_request": compute_req_stats(src_tot),
        # Backward compatibility aliases
        "input": compute_req_stats(src_tot_in),
        "input_read": compute_req_stats(src_c_in),
        "input_write": compute_req_stats(src_c_wr),
    }

    with active_calls_lock:
        for ag, item in agents_acc.items():
            ac = active_calls_per_agent.get(ag, {"post": 0, "stream": 0})
            item["calls_active_post"] = ac.get("post", 0)
            item["calls_active_stream"] = ac.get("stream", 0)
            item["calls_active"] = ac.get("post", 0) + ac.get("stream", 0)
        for svc, item in services_acc.items():
            ac = active_calls_per_service.get(svc, {"post": 0, "stream": 0})
            item["calls_active_post"] = ac.get("post", 0)
            item["calls_active_stream"] = ac.get("stream", 0)
            item["calls_active"] = ac.get("post", 0) + ac.get("stream", 0)
        for m_key, item in models_acc.items():
            ac = active_calls_per_model.get(m_key, {"post": 0, "stream": 0})
            item["calls_active_post"] = ac.get("post", 0)
            item["calls_active_stream"] = ac.get("stream", 0)
            item["calls_active"] = ac.get("post", 0) + ac.get("stream", 0)

        totals_acc["calls_active_post"] = global_active_calls_post
        totals_acc["calls_active_stream"] = global_active_calls_stream
        totals_acc["calls_active"] = global_active_calls_post + global_active_calls_stream

    return {
        "models": models_acc,
        "agents": agents_acc,
        "services": services_acc,
        "totals": totals_acc,
        "daily": daily_acc,
    }


def update_prometheus_metrics():
    metrics = get_cumulative_metrics()
    for key, val in metrics["models"].items():
        agent, model, service = key.split(":", 2)
        calls_gauge.labels(agent=agent, service=service, model=model).set(val["calls"])
        client_cancel_count = val["errors_streaming"].get("499", 0) + val["errors_post"].get(
            "499", 0
        )
        client_cancel_gauge.labels(agent=agent, service=service, model=model).set(
            client_cancel_count
        )

        tokens_gauge.labels(agent=agent, service=service, model=model, type="input").set(
            val["input"]
        )
        tokens_gauge.labels(agent=agent, service=service, model=model, type="cached_input").set(
            val["cached_input"]
        )
        tokens_gauge.labels(agent=agent, service=service, model=model, type="cached_write").set(
            val["cached_write"]
        )
        tokens_gauge.labels(agent=agent, service=service, model=model, type="output").set(
            val["output"]
        )
        tokens_gauge.labels(agent=agent, service=service, model=model, type="total").set(
            val["total_tokens"]
        )

        cost_gauge.labels(agent=agent, service=service, model=model, type="input").set(
            val["costs"]["input_cost"]
        )
        cost_gauge.labels(agent=agent, service=service, model=model, type="cached_input").set(
            val["costs"]["cached_input_cost"]
        )
        cost_gauge.labels(agent=agent, service=service, model=model, type="cached_write").set(
            val["costs"]["cached_write_cost"]
        )
        cost_gauge.labels(agent=agent, service=service, model=model, type="output").set(
            val["costs"]["output_cost"]
        )
        cost_gauge.labels(agent=agent, service=service, model=model, type="total").set(
            val["costs"]["total_cost"]
        )

        time_gauge.labels(agent=agent, service=service, model=model, type="post").set(
            val.get("duration_post", 0.0)
        )
        time_gauge.labels(agent=agent, service=service, model=model, type="stream").set(
            val.get("duration_streaming", 0.0)
        )
        time_gauge.labels(agent=agent, service=service, model=model, type="total").set(
            val.get("total_duration", 0.0)
        )

        # Update errors
        for code in STATIC_ERRORS_TEMPLATE:
            errors_gauge.labels(
                agent=agent,
                service=service,
                model=model,
                call_type="streaming",
                code=code,
            ).set(val["errors_streaming"].get(code, 0))
            errors_gauge.labels(
                agent=agent, service=service, model=model, call_type="post", code=code
            ).set(val["errors_post"].get(code, 0))


def format_usage_table(data: dict[str, Any]) -> str:
    models = data.get("models", {})
    agents = data.get("agents", {})
    services = data.get("services", {})
    totals = data.get("totals", {})

    lines = []
    width = 166
    lines.append("-" * width)
    lines.append(
        f"| {'AGENT:MODEL:SERVICE':<30} | {'CALLS':<6} | {'STREAM':<6} | {'POST':<6} | {'INPUT':<10} | {'CACHED IN':<10} | {'CACHED WR':<10} | {'OUTPUT':<10} | {'CACHE %':<8} | {'p.TimeT':<10} | {'EST COST':<9} | {'ERRORS (STR / POST)':<18} |"
    )
    lines.append("-" * width)

    def get_errors_str(stats: dict[str, Any]) -> str:
        str_errs = sum(stats.get("errors_streaming", {}).values())
        post_errs = sum(stats.get("errors_post", {}).values())
        return f"{str_errs} / {post_errs}"

    for model_key, stats in sorted(models.items()):
        cost = stats.get("costs", {}).get("total_cost", 0.0)
        errs_str = get_errors_str(stats)
        time_mins = stats.get("total_duration", 0.0) / 60.0
        lines.append(
            f"| {model_key:<30} | {stats.get('calls', 0):<6} | {stats.get('streaming_calls', 0):<6} | {stats.get('calls_post', 0):<6} | {stats.get('input', 0):<10} | {stats.get('cached_input', 0):<10} | {stats.get('cached_write', 0):<10} | {stats.get('output', 0):<10} | {stats.get('cache_pct', 0.0):<8.2f} | {time_mins:<10.2f} | ${cost:<8.4f} | {errs_str:<18} |"
        )

    lines.append("-" * width)

    for agent_name, stats in sorted(agents.items()):
        cost = stats.get("costs", {}).get("total_cost", 0.0)
        errs_str = get_errors_str(stats)
        time_mins = stats.get("total_duration", 0.0) / 60.0
        lines.append(
            f"| {f'Agent {agent_name.upper()} Total':<30} | {stats.get('calls', 0):<6} | {stats.get('streaming_calls', 0):<6} | {stats.get('calls_post', 0):<6} | {stats.get('input', 0):<10} | {stats.get('cached_input', 0):<10} | {stats.get('cached_write', 0):<10} | {stats.get('output', 0):<10} | {stats.get('cache_pct', 0.0):<8.2f} | {time_mins:<10.2f} | ${cost:<8.4f} | {errs_str:<18} |"
        )

    lines.append("-" * width)

    for svc_name, stats in sorted(services.items()):
        cost = stats.get("costs", {}).get("total_cost", 0.0)
        errs_str = get_errors_str(stats)
        time_mins = stats.get("total_duration", 0.0) / 60.0
        lines.append(
            f"| {f'Service {svc_name.upper()} Total':<30} | {stats.get('calls', 0):<6} | {stats.get('streaming_calls', 0):<6} | {stats.get('calls_post', 0):<6} | {stats.get('input', 0):<10} | {stats.get('cached_input', 0):<10} | {stats.get('cached_write', 0):<10} | {stats.get('output', 0):<10} | {stats.get('cache_pct', 0.0):<8.2f} | {time_mins:<10.2f} | ${cost:<8.4f} | {errs_str:<18} |"
        )

    lines.append("-" * width)
    total_cost = totals.get("costs", {}).get("total_cost", 0.0)
    total_errs_str = get_errors_str(totals)
    tot_time_mins = totals.get("total_duration", 0.0) / 60.0
    lines.append(
        f"| {'GRAND TOTAL':<30} | {totals.get('calls', 0):<6} | {totals.get('streaming_calls', 0):<6} | {totals.get('calls_post', 0):<6} | {totals.get('input', 0):<10} | {totals.get('cached_input', 0):<10} | {totals.get('cached_write', 0):<10} | {totals.get('output', 0):<10} | {totals.get('cache_pct', 0.0):<8.2f} | {tot_time_mins:<10.2f} | ${total_cost:<8.4f} | {total_errs_str:<18} |"
    )
    lines.append("-" * width)

    has_errors = False
    for name, stats in (
        [("GRAND TOTAL", totals)]
        + list(sorted((f"Agent {k.upper()}", v) for k, v in agents.items()))
        + list(sorted(models.items()))
    ):
        str_err_codes = {k: v for k, v in stats.get("errors_streaming", {}).items() if v > 0}
        post_err_codes = {k: v for k, v in stats.get("errors_post", {}).items() if v > 0}
        if str_err_codes or post_err_codes:
            if not has_errors:
                lines.append("\nHTTP Errors Breakdown:")
                has_errors = True
            lines.append(f"  {name}:")
            if str_err_codes:
                lines.append(
                    "    Streaming errors: "
                    + ", ".join(f"{k}:{v}" for k, v in sorted(str_err_codes.items()))
                )
            if post_err_codes:
                lines.append(
                    "    Post errors:      "
                    + ", ".join(f"{k}:{v}" for k, v in sorted(post_err_codes.items()))
                )

    return "\n".join(lines) + "\n"


def save_on_exit():
    check_and_save_usage(force=True)


# Register exit handlers
atexit.register(save_on_exit)


def handle_exit_signal(signum, frame):
    # Shutdown is handled by uvicorn via lifespan cleanup — do nothing here
    pass


# Register signals (ignore errors if in non-main threads or during testing)
try:
    signal.signal(signal.SIGTERM, handle_exit_signal)
    signal.signal(signal.SIGINT, handle_exit_signal)
except Exception:
    pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    global client, save_task
    load_usage_data()
    # Global client timeout: 900s total, 5s connect
    client = httpx.AsyncClient(timeout=httpx.Timeout(900.0, connect=5.0))
    # Background discovery — non-blocking, starts fallback inventory immediately
    discovery_task = asyncio.create_task(discover_services_background())
    save_task = asyncio.create_task(periodic_save_task())
    yield
    # --- shutdown ---
    discovery_task.cancel()
    save_task.cancel()
    await asyncio.gather(discovery_task, save_task, return_exceptions=True)
    save_on_exit()
    if client:
        try:
            await asyncio.wait_for(client.aclose(), timeout=2.0)
        except Exception:
            pass


app = FastAPI(
    title="Local Inference Combined Router",
    description="Combined gateway mimicking OpenAI-compatible endpoints for local LLM, TTS, STT, and Image backends.",
    version="1.0.0",
    lifespan=lifespan,
)


def get_log_config() -> tuple[bool, bool]:
    """Resolve fused verbose and debug settings from CLI args and environment variables."""
    log_level = os.environ.get("LROUT_LOG_LEVEL", "").lower()
    env_verbose = os.environ.get("LROUT_VERBOSE", "").lower() in ("1", "true", "yes")
    env_debug = os.environ.get("LROUT_DEBUG", "").lower() in ("1", "true", "yes")

    cli_verbose = "--verbose" in sys.argv
    cli_debug = "--debug" in sys.argv

    verbose = cli_verbose or env_verbose or log_level in ("verbose", "debug")
    debug = cli_debug or env_debug or log_level == "debug"

    if debug:
        verbose = True

    return verbose, debug


def is_verbose() -> bool:
    v, _ = get_log_config()
    return v


def is_debug() -> bool:
    _, d = get_log_config()
    return d


def resolve_config() -> dict[str, str]:
    """Resolve routing destinations using standard default localhost ports with env variable overrides."""
    lmbd_enabled_env = (
        os.environ.get("LROUT_EMBEDDING_ENABLED") or os.environ.get("LMBD_ENABLED") or "0"
    )
    lmbd_enabled = str(lmbd_enabled_env).lower() not in ("0", "false", "no")

    config = {}
    for svc, (def_host, def_port) in DEFAULT_SERVICE_PORTS.items():
        prefixes = SERVICE_ENV_PREFIXES.get(svc, [f"LROUT_{svc.upper()}"])
        host = def_host
        port = def_port

        for pfx in prefixes:
            h_val = os.environ.get(f"{pfx}_HOST")
            if h_val:
                host = h_val
                break
        for pfx in prefixes:
            p_val = os.environ.get(f"{pfx}_PORT")
            if p_val:
                try:
                    port = int(p_val)
                    break
                except ValueError:
                    pass

        config[svc] = f"http://{host}:{port}"

    if not lmbd_enabled:
        config["embedding"] = config["chat"]

    config["rerank_api_path"] = os.environ.get("LROUT_RERANK_PATH") or os.environ.get(
        "LRR_API_PATH", "/v1/rerank"
    )
    return config


async def handle_mock_backend(
    service: str, model: str, request: Request, request_content: bytes
) -> Response:
    is_streaming = False
    if request_content:
        try:
            req_json = json.loads(request_content)
            is_streaming = req_json.get("stream", False)
        except Exception:
            pass

    service = service or "chat"
    model = model or "qwen3"

    if "error-" in model:
        try:
            code = int(model.split("error-")[-1])
            if is_streaming:

                async def err_sse_gen():
                    yield f'data: {{"error": {{"message": "Mocked {code}", "code": {code}}}}}\n\n'.encode(
                        "utf-8"
                    )
                    yield b"data: [DONE]\n\n"

                return StreamingResponse(
                    err_sse_gen(), status_code=code, media_type="text/event-stream"
                )
            return JSONResponse({"error": f"Mocked {code}"}, status_code=code)
        except Exception:
            pass

    if request.url.path in ("/props", "/v1/props"):
        return JSONResponse(
            {
                "default_generation_settings": {"n_ctx": 120192},
                "model_alias": resolve_service_alias("chat") or "qwen3",
            }
        )
    if request.url.path in ("/tokenize", "/v1/tokenize"):
        return JSONResponse({"tokens": [1, 2, 3]})
    if request.url.path in ("/detokenize", "/v1/detokenize"):
        return JSONResponse({"content": "mock detokenized text"})

    if service == "chat":
        if is_streaming:

            async def sse_gen():
                yield b'data: {"choices": [{"delta": {"content": "Mock"}, "index": 0}]}\n\n'
                await asyncio.sleep(0.01)
                yield b'data: {"choices": [{"delta": {"content": " response"}, "index": 0}]}\n\n'
                await asyncio.sleep(0.01)
                usage_data = {
                    "choices": [],
                    "usage": {
                        "prompt_tokens": 100,
                        "completion_tokens": 50,
                        "prompt_tokens_details": {"cached_tokens": 20},
                    },
                }
                yield f"data: {json.dumps(usage_data)}\n\n".encode("utf-8")
                yield b"data: [DONE]\n\n"

            return StreamingResponse(sse_gen(), media_type="text/event-stream")
        else:
            return JSONResponse(
                {
                    "choices": [{"message": {"role": "assistant", "content": "Mock response"}}],
                    "usage": {
                        "prompt_tokens": 100,
                        "completion_tokens": 50,
                        "prompt_tokens_details": {"cached_tokens": 20},
                    },
                }
            )
    elif service == "embedding":
        return JSONResponse(
            {
                "data": [{"embedding": [0.1] * 128, "index": 0}],
                "usage": {"prompt_tokens": 10, "total_tokens": 10},
            }
        )
    elif service == "rerank":
        return JSONResponse(
            {
                "results": [
                    {"index": 0, "relevance_score": 0.95},
                    {"index": 1, "relevance_score": 0.12},
                ],
                "usage": {"prompt_tokens": 15, "total_tokens": 15},
            }
        )
    elif service == "tts":
        return Response(content=b"MOCK_AUDIO_DATA_MP3_BYTES", media_type="audio/mpeg")
    elif service == "stt":
        return JSONResponse({"text": "Mock transcribed text."})
    elif service == "image":
        return JSONResponse({"data": [{"url": "http://127.0.0.1:21080/mock_image.png"}]})

    return JSONResponse({"error": "Unsupported mock service"}, status_code=400)


async def process_response_usage(
    agent: str,
    service: str,
    model: str,
    is_sse: bool,
    response_body: bytes,
    request_body: bytes | None,
    is_streaming: bool,
    status_code: int = 200,
    duration: float = 0.0,
):
    estimated_input_tokens = 0
    request_prompt = ""
    if request_body:
        try:
            req_data = json.loads(request_body)
            if "messages" in req_data:
                request_prompt = "\n".join(
                    [m.get("content", "") for m in req_data["messages"] if isinstance(m, dict)]
                )
            elif "prompt" in req_data:
                if isinstance(req_data["prompt"], list):
                    request_prompt = "\n".join(req_data["prompt"])
                else:
                    request_prompt = str(req_data["prompt"])
            elif "input" in req_data:
                if isinstance(req_data["input"], list):
                    request_prompt = "\n".join(req_data["input"])
                else:
                    request_prompt = str(req_data["input"])
            elif "query" in req_data:
                request_prompt = str(req_data["query"])
                if "documents" in req_data:
                    request_prompt += "\n" + "\n".join(req_data["documents"])
            elif "content" in req_data:
                if isinstance(req_data["content"], list):
                    request_prompt = "\n".join(str(item) for item in req_data["content"])
                else:
                    request_prompt = str(req_data["content"])
            elif "inputs" in req_data:
                if isinstance(req_data["inputs"], list):
                    request_prompt = "\n".join(str(item) for item in req_data["inputs"])
                else:
                    request_prompt = str(req_data["inputs"])
            estimated_input_tokens = get_token_count(request_prompt)
        except Exception:
            pass

    prompt_tokens = 0
    completion_tokens = 0
    cached_input = 0
    cached_write = 0

    if is_sse:
        lines = response_body.decode("utf-8", errors="ignore").split("\n")
        generated_text = ""
        found_usage = False
        for line in lines:
            line = line.strip()
            if line.startswith("data:"):
                data_str = line[5:].strip()
                if data_str == "[DONE]":
                    continue
                try:
                    data_json = json.loads(data_str)
                    usage = data_json.get("usage")
                    if usage:
                        prompt_tokens = usage.get("prompt_tokens", 0)
                        completion_tokens = usage.get("completion_tokens", 0)
                        details = usage.get("prompt_tokens_details", {})
                        cached_input = details.get("cached_tokens", 0) or usage.get(
                            "cache_read_input_tokens", 0
                        )
                        cached_write = details.get("cache_creation_input_tokens", 0) or usage.get(
                            "cache_creation_input_tokens", 0
                        )
                        found_usage = True

                    choices = data_json.get("choices", [])
                    if choices:
                        delta = choices[0].get("delta", {})
                        if "content" in delta:
                            generated_text += delta["content"]
                except Exception:
                    pass
        if not found_usage:
            prompt_tokens = estimated_input_tokens
            completion_tokens = get_token_count(generated_text)
    else:
        try:
            resp_data = json.loads(response_body)
            usage = resp_data.get("usage")
            if usage:
                prompt_tokens = usage.get("prompt_tokens", 0)
                completion_tokens = usage.get("completion_tokens", 0)
                details = usage.get("prompt_tokens_details", {})
                cached_input = details.get("cached_tokens", 0) or usage.get(
                    "cache_read_input_tokens", 0
                )
                cached_write = details.get("cache_creation_input_tokens", 0) or usage.get(
                    "cache_creation_input_tokens", 0
                )
            else:
                if service == "embedding":
                    prompt_tokens = estimated_input_tokens
                    completion_tokens = 0
                elif service == "rerank":
                    prompt_tokens = estimated_input_tokens
                    completion_tokens = 0
                elif service == "tts":
                    prompt_tokens = estimated_input_tokens
                    words = len(request_prompt.split())
                    duration_val = words / 2.5
                    completion_tokens = int(duration_val * 283)
                elif service == "stt":
                    prompt_tokens = 0
                    transcribed = resp_data.get("text", "")
                    completion_tokens = get_token_count(transcribed)
                elif service == "image":
                    prompt_tokens = estimated_input_tokens
                    n = 1
                    try:
                        if request_body:
                            n = int(json.loads(request_body).get("n", 1))
                    except Exception:
                        pass
                    completion_tokens = n * 1117
                else:
                    prompt_tokens = estimated_input_tokens
                    completion_tokens = 0
        except Exception:
            prompt_tokens = estimated_input_tokens
            completion_tokens = 0

    uncached_input = max(0, prompt_tokens - cached_input)

    add_usage_record(
        agent=agent or "unknown",
        service=service or "unknown",
        model=model or "unknown",
        uncached_input=uncached_input,
        cached_input=cached_input,
        cached_write=cached_write,
        output=completion_tokens,
        is_streaming=is_streaming,
        status_code=status_code,
        duration=duration,
    )

    if is_verbose():
        status_info = (
            f"status={status_code}" if status_code != 499 else "status=499 (CLIENT CANCELED)"
        )
        print(
            f"[ROUTER VERBOSE] client='{agent or 'unknown'}' service='{service or 'unknown'}' model='{model or 'unknown'}' input={uncached_input + cached_input} output={completion_tokens} {status_info} duration={duration:.3f}s",
            file=sys.stderr,
        )
    if is_debug() and response_body:
        print_debug_raw(f"RESPONSE [{agent}:{service}:{model}] status={status_code}", response_body)


def _increment_active_call(agent_id: str, service_id: str, model_id: str, is_streaming: bool):
    global global_active_calls_stream, global_active_calls_post
    model_key = f"{agent_id}:{model_id}:{service_id}"
    calls_active_gauge.labels(agent=agent_id, service=service_id, model=model_id).inc()
    with active_calls_lock:
        if is_streaming:
            global_active_calls_stream += 1
            if agent_id not in active_calls_per_agent:
                active_calls_per_agent[agent_id] = {"post": 0, "stream": 0}
            active_calls_per_agent[agent_id]["stream"] += 1
            if service_id not in active_calls_per_service:
                active_calls_per_service[service_id] = {"post": 0, "stream": 0}
            active_calls_per_service[service_id]["stream"] += 1
            if model_key not in active_calls_per_model:
                active_calls_per_model[model_key] = {"post": 0, "stream": 0}
            active_calls_per_model[model_key]["stream"] += 1
        else:
            global_active_calls_post += 1
            if agent_id not in active_calls_per_agent:
                active_calls_per_agent[agent_id] = {"post": 0, "stream": 0}
            active_calls_per_agent[agent_id]["post"] += 1
            if service_id not in active_calls_per_service:
                active_calls_per_service[service_id] = {"post": 0, "stream": 0}
            active_calls_per_service[service_id]["post"] += 1
            if model_key not in active_calls_per_model:
                active_calls_per_model[model_key] = {"post": 0, "stream": 0}
            active_calls_per_model[model_key]["post"] += 1


def _decrement_active_call(agent_id: str, service_id: str, model_id: str, is_streaming: bool):
    global global_active_calls_stream, global_active_calls_post
    model_key = f"{agent_id}:{model_id}:{service_id}"
    calls_active_gauge.labels(agent=agent_id, service=service_id, model=model_id).dec()
    with active_calls_lock:
        if is_streaming:
            global_active_calls_stream = max(0, global_active_calls_stream - 1)
            if agent_id in active_calls_per_agent:
                active_calls_per_agent[agent_id]["stream"] = max(
                    0, active_calls_per_agent[agent_id]["stream"] - 1
                )
            if service_id in active_calls_per_service:
                active_calls_per_service[service_id]["stream"] = max(
                    0, active_calls_per_service[service_id]["stream"] - 1
                )
            if model_key in active_calls_per_model:
                active_calls_per_model[model_key]["stream"] = max(
                    0, active_calls_per_model[model_key]["stream"] - 1
                )
        else:
            global_active_calls_post = max(0, global_active_calls_post - 1)
            if agent_id in active_calls_per_agent:
                active_calls_per_agent[agent_id]["post"] = max(
                    0, active_calls_per_agent[agent_id]["post"] - 1
                )
            if service_id in active_calls_per_service:
                active_calls_per_service[service_id]["post"] = max(
                    0, active_calls_per_service[service_id]["post"] - 1
                )
            if model_key in active_calls_per_model:
                active_calls_per_model[model_key]["post"] = max(
                    0, active_calls_per_model[model_key]["post"] - 1
                )


async def proxy_request(
    target_url: str,
    request: Request,
    content: bytes | None = None,
    service: str | None = None,
    model: str | None = None,
    agent: str | None = None,
    track_usage: bool = True,
) -> Response:
    """Asynchronously streams request to target and forwards the response back."""
    body = content if content is not None else await request.body()
    start_time = time.perf_counter()

    agent_id = agent or "unknown"
    service_id = service or "unknown"
    model_id = model or "unknown"

    is_streaming = False
    if body:
        try:
            is_streaming = json.loads(body).get("stream", False)
        except Exception:
            pass

    stream_response_returned = False
    active_decremented = False

    if is_debug() and body:
        print_debug_raw(
            f"REQUEST [{agent_id}:{service_id}:{model_id}] {request.method} {request.url.path}",
            body,
        )

    # If the target backend hasn't been confirmed online yet, tell the client to retry
    if not LROUT_MOCK_BACKENDS and service and service not in available_services:
        print(
            f"[ROUTER] Backend '{service}' not yet available — returning 503 (Retry-After: 5s)",
            file=sys.stderr,
        )
        return JSONResponse(
            status_code=503,
            content={
                "error": {
                    "message": f"Backend service '{service}' is not available yet — retry shortly",
                    "type": "service_unavailable",
                }
            },
            headers={"Retry-After": "5"},
        )

    if track_usage:
        _increment_active_call(agent_id, service_id, model_id, is_streaming)

    try:
        if LROUT_MOCK_BACKENDS:
            mock_resp = await handle_mock_backend(service or "", model or "", request, body)
            is_sse = (
                isinstance(mock_resp, StreamingResponse)
                and mock_resp.media_type == "text/event-stream"
            )

            if isinstance(mock_resp, JSONResponse):
                if track_usage:
                    resp_body = (
                        mock_resp.body
                        if isinstance(mock_resp.body, bytes)
                        else bytes(mock_resp.body)
                    )
                    elapsed = time.perf_counter() - start_time
                    await process_response_usage(
                        agent or "unknown",
                        service or "",
                        model or "",
                        is_sse,
                        resp_body,
                        body,
                        is_streaming,
                        status_code=mock_resp.status_code,
                        duration=elapsed,
                    )
            elif isinstance(mock_resp, Response) and not isinstance(mock_resp, StreamingResponse):
                if track_usage:
                    resp_body = (
                        mock_resp.body
                        if isinstance(mock_resp.body, bytes)
                        else bytes(mock_resp.body)
                    )
                    elapsed = time.perf_counter() - start_time
                    await process_response_usage(
                        agent or "unknown",
                        service or "",
                        model or "",
                        is_sse,
                        resp_body,
                        body,
                        is_streaming,
                        status_code=mock_resp.status_code,
                        duration=elapsed,
                    )
            elif isinstance(mock_resp, StreamingResponse):
                original_chunks = []

                async def mock_generator():
                    nonlocal active_decremented
                    try:
                        async for chunk in mock_resp.body_iterator:
                            yield chunk
                            original_chunks.append(chunk)
                        if track_usage:
                            full_body = b"".join(original_chunks)
                            elapsed = time.perf_counter() - start_time
                            await process_response_usage(
                                agent or "unknown",
                                service or "",
                                model or "",
                                is_sse,
                                full_body,
                                body,
                                is_streaming,
                                status_code=mock_resp.status_code,
                                duration=elapsed,
                            )
                    except Exception as e:
                        print(f"Error processing mock usage: {e}", file=sys.stderr)
                    finally:
                        if track_usage and not active_decremented:
                            _decrement_active_call(agent_id, service_id, model_id, is_streaming)
                            active_decremented = True

                stream_response_returned = True
                return StreamingResponse(
                    mock_generator(),
                    status_code=mock_resp.status_code,
                    headers=dict(mock_resp.headers),
                    media_type=mock_resp.media_type,
                )
            return mock_resp

        headers = {
            k: v for k, v in request.headers.items() if k.lower() not in ("host", "content-length")
        }

        try:
            default_svc_to = SERVICE_TIMEOUT_DEFAULTS.get(service or "", 120.0)
            env_var_name = (
                f"LROUT_{service.upper()}_TIMEOUT" if service else "LROUT_DEFAULT_TIMEOUT"
            )
            read_timeout_val = float(os.environ.get(env_var_name, str(default_svc_to)))
            connect_timeout_val = float(os.environ.get("LROUT_CONNECT_TIMEOUT", "5.0"))

            req_timeout = httpx.Timeout(
                timeout=read_timeout_val,
                connect=connect_timeout_val,
                read=read_timeout_val,
                write=60.0,
                pool=10.0,
            )
            req = client.build_request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
                params=request.query_params,
                timeout=req_timeout,
            )

            response = await client.send(req, stream=True)

            is_sse = response.headers.get("content-type", "").startswith("text/event-stream")

            async def response_generator():
                nonlocal active_decremented
                body_accumulator = []
                try:
                    async for chunk in response.aiter_bytes():
                        yield chunk
                        body_accumulator.append(chunk)
                finally:
                    await response.aclose()
                    if track_usage:
                        if not active_decremented:
                            _decrement_active_call(agent_id, service_id, model_id, is_streaming)
                            active_decremented = True
                        try:
                            full_body = b"".join(body_accumulator)
                            elapsed = time.perf_counter() - start_time
                            await process_response_usage(
                                agent or "unknown",
                                service or "",
                                model or "",
                                is_sse,
                                full_body,
                                body,
                                is_streaming,
                                status_code=response.status_code,
                                duration=elapsed,
                            )
                        except Exception as e:
                            print(f"Error processing usage: {e}", file=sys.stderr)

            # Strip content-length and transfer-encoding headers to let FastAPI handle chunking correctly
            resp_headers = {
                k: v
                for k, v in response.headers.items()
                if k.lower() not in ("transfer-encoding", "content-length")
            }

            stream_response_returned = True
            return StreamingResponse(
                response_generator(),
                status_code=response.status_code,
                headers=resp_headers,
                media_type=response.headers.get("content-type"),
            )

        except httpx.HTTPStatusError as exc:
            print(f"HTTPStatusError proxying to {target_url}: {exc}", file=sys.stderr)
            if track_usage:
                elapsed = time.perf_counter() - start_time
                try:
                    await process_response_usage(
                        agent=agent or "unknown",
                        service=service or "",
                        model=model or "",
                        is_sse=False,
                        response_body=b"",
                        request_body=body,
                        is_streaming=is_streaming,
                        status_code=exc.response.status_code,
                        duration=elapsed,
                    )
                except Exception:
                    pass
            return JSONResponse(
                status_code=exc.response.status_code,
                content={
                    "error": {
                        "message": f"Backend error: {str(exc)}",
                        "type": "backend_error",
                    }
                },
            )
        except (httpx.ConnectError, httpx.ConnectTimeout) as exc:
            print(f"ConnectionError proxying to {target_url}: {exc}", file=sys.stderr)
            if track_usage:
                elapsed = time.perf_counter() - start_time
                # Gracefully handle backend downtime
                try:
                    await process_response_usage(
                        agent=agent or "unknown",
                        service=service or "",
                        model=model or "",
                        is_sse=False,
                        response_body=b"",
                        request_body=body,
                        is_streaming=is_streaming,
                        status_code=502,
                        duration=elapsed,
                    )
                except Exception:
                    pass
            return JSONResponse(
                status_code=502,
                content={
                    "error": {
                        "message": f"Local service backend ({target_url}) is currently offline or unreachable. {str(exc)}",
                        "type": "gateway_error",
                        "code": 502,
                    }
                },
            )
        except Exception as exc:
            print(f"Exception proxying to {target_url}: {exc}", file=sys.stderr)
            import traceback

            traceback.print_exc(file=sys.stderr)
            if track_usage:
                elapsed = time.perf_counter() - start_time
                try:
                    await process_response_usage(
                        agent=agent or "unknown",
                        service=service or "",
                        model=model or "",
                        is_sse=False,
                        response_body=b"",
                        request_body=body,
                        is_streaming=is_streaming,
                        status_code=500,
                        duration=elapsed,
                    )
                except Exception:
                    pass
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "message": f"Internal proxy routing error: {str(exc)}",
                        "type": "proxy_error",
                    }
                },
            )
    except asyncio.CancelledError:
        if track_usage:
            elapsed = time.perf_counter() - start_time
            client_cancel_gauge.labels(agent=agent_id, service=service_id, model=model_id).inc()
            if is_verbose():
                print(
                    f"[ROUTER VERBOSE] client='{agent_id}' path='{request.url.path}' service='{service_id}' model='{model_id}' status=499 (CLIENT CANCELED) duration={elapsed:.3f}s",
                    file=sys.stderr,
                )
            try:
                await process_response_usage(
                    agent=agent_id,
                    service=service_id,
                    model=model_id,
                    is_sse=False,
                    response_body=b"",
                    request_body=body,
                    is_streaming=is_streaming,
                    status_code=499,
                    duration=elapsed,
                )
            except Exception:
                pass
        raise
    finally:
        if track_usage and not stream_response_returned and not active_decremented:
            _decrement_active_call(agent_id, service_id, model_id, is_streaming)
            active_decremented = True


# --- Usage & Metrics Routes ---


@app.get("/usage")
@app.get("/v1/usage")
async def route_usage(day: str | None = None, range: str | None = None, format: str = "json"):
    try:
        metrics = get_cumulative_metrics(day_filter=day, range_filter=range)
        if format == "text":
            return PlainTextResponse(format_usage_table(metrics))
        return metrics
    except Exception as e:
        print(f"Error in route_usage: {e}", file=sys.stderr)
        if format == "text":
            return PlainTextResponse(f"Error: {e}", status_code=500)
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/metrics")
@app.get("/v1/metrics")
async def route_metrics():
    try:
        update_prometheus_metrics()
        return Response(content=generate_latest(metrics_registry), media_type=CONTENT_TYPE_LATEST)
    except Exception as e:
        print(f"Error in route_metrics: {e}", file=sys.stderr)
        return Response(
            content=f"Error generating metrics: {e}",
            status_code=500,
            media_type="text/plain",
        )


@app.api_route("/", methods=["GET", "HEAD"])
async def route_root():
    """Redirect root path to the Web Dashboard UI."""
    return RedirectResponse(url="/ui", status_code=302)


@app.get("/routing/ui", response_class=HTMLResponse)
@app.get("/ui", response_class=HTMLResponse)
async def route_ui():
    ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "local-router-ui.html")
    if not os.path.exists(ui_path):
        return HTMLResponse("<h1>Error: local-router-ui.html not found</h1>", status_code=404)
    with open(ui_path, "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content)


# --- Routes Mapping ---


def extract_request_agent(request: Request, body_data: Mapping[str, Any] | None = None) -> str:
    """Extract and normalize client identifier strictly from request HTTP headers or JSON body payload."""
    custom: str | None = None
    for header_name in CLIENT_IDENTIFICATION_HEADERS:
        val = request.headers.get(header_name)
        if val:
            custom = val
            break

    if not custom and isinstance(body_data, Mapping):
        c_val = (
            body_data.get("client_id")
            or body_data.get("agent_id")
            or body_data.get("client")
            or body_data.get("agent")
        )
        if isinstance(c_val, str):
            custom = c_val
        elif isinstance(body_data.get("extra_body"), Mapping):
            eb = body_data["extra_body"]
            eb_val = (
                eb.get("client_id") or eb.get("agent_id") or eb.get("client") or eb.get("agent")
            )
            if isinstance(eb_val, str):
                custom = eb_val

    # Fallback: check User-Agent header if no custom header/body identifier provided
    if not custom:
        ua_raw = request.headers.get("user-agent", "")
        ua_lower = ua_raw.lower()
        if "zed/" in ua_lower:
            custom = "zed"
        elif "hindsight" in ua_lower:
            custom = "hindsight"
        elif "hermes" in ua_lower:
            custom = "hermes"
        elif "omp/" in ua_lower or "oh-my-pi" in ua_lower:
            custom = "oh-my-pi"
    agent = resolve_client_id(custom)
    if agent == "unknown":
        client_host = request.client.host if request.client else "unknown"
        path = request.url.path
        method = request.method
        ua = request.headers.get("user-agent", "")
        print(
            f"[UNMAPPED CLIENT] Path: {method} {path} | User-Agent: '{ua or '<missing>'}' | Custom Identifier: '{custom or '<none>'}' | IP: {client_host}",
            file=sys.stderr,
        )
    return agent


@app.post("/v1/chat/completions")
async def route_chat(request: Request):
    config = resolve_config()
    body = await request.body()
    data: dict[str, Any] | None = None
    chat_alias = resolve_service_alias("chat") or "qwen3"
    model = chat_alias
    try:
        data = json.loads(body)
        model = data.get("model", chat_alias)

        reasoning_effort = data.get("reasoning_effort")
        thinking_dict = data.get("thinking")
        chat_template_kwargs = data.get("chat_template_kwargs")
        if not isinstance(chat_template_kwargs, dict):
            chat_template_kwargs = {}

        explicit_disable = (
            reasoning_effort == "none"
            or chat_template_kwargs.get("enable_thinking") is False
            or (isinstance(thinking_dict, dict) and thinking_dict.get("enabled") is False)
        )

        explicit_enable = (
            model == "qwen3-thinking"
            or (isinstance(model, str) and model.endswith("-thinking"))
            or (
                isinstance(reasoning_effort, str)
                and reasoning_effort.lower()
                in ["minimal", "low", "medium", "high", "xhigh", "true", "enabled"]
            )
            or (isinstance(thinking_dict, dict) and thinking_dict.get("enabled") is True)
            or chat_template_kwargs.get("enable_thinking") is True
        )

        if explicit_disable:
            chat_template_kwargs["enable_thinking"] = False
        elif explicit_enable:
            chat_template_kwargs["enable_thinking"] = True
        else:
            # Default to True for chat service routes so reasoning models retain CoT scratchpad
            chat_template_kwargs["enable_thinking"] = True

        if model == "qwen3-thinking" or (isinstance(model, str) and model.endswith("-thinking")):
            if model == "qwen3-thinking":
                data["model"] = "qwen3"
            else:
                data["model"] = model[:-9]

        data["chat_template_kwargs"] = chat_template_kwargs
        body = json.dumps(data).encode("utf-8")
    except Exception:
        pass
    agent = extract_request_agent(request, data)
    return await proxy_request(
        f"{config['chat']}/v1/chat/completions",
        request,
        content=body,
        service="chat",
        model=model,
        agent=agent,
    )


@app.post("/v1/embeddings")
async def route_embedding(request: Request):
    config = resolve_config()
    model = "qwen3-embedding"
    body = None
    data: dict[str, Any] | None = None
    try:
        body = await request.body()
        data = json.loads(body)
        model = data.get("model", "qwen3-embedding")
    except Exception:
        pass
    agent = extract_request_agent(request, data)
    return await proxy_request(
        f"{config['embedding']}/v1/embeddings",
        request,
        content=body,
        service="embedding",
        model=model,
        agent=agent,
    )


@app.post("/v1/rerank")
@app.post("/rerank")
async def route_rerank(request: Request):
    config = resolve_config()
    model = "qwen3-reranker"
    body = None
    data: dict[str, Any] | None = None
    try:
        body = await request.body()
        data = json.loads(body)
        model = data.get("model", "qwen3-reranker")
    except Exception:
        pass
    agent = extract_request_agent(request, data)
    return await proxy_request(
        f"{config['rerank']}{config['rerank_api_path']}",
        request,
        content=body,
        service="rerank",
        model=model,
        agent=agent,
    )


@app.post("/v1/audio/transcriptions")
async def route_stt(request: Request):
    config = resolve_config()
    inf_path = os.environ.get("LROUT_STT_PATH") or os.environ.get(
        "LSTT_INFERENCE_PATH", "/v1/audio/transcriptions"
    )
    agent = extract_request_agent(request)
    model = "whisper-1"
    body_bytes = b""
    try:
        body_bytes = await request.body()
        form = await request.form()
        model_form = form.get("model")
        if isinstance(model_form, str):
            model = model_form
    except Exception:
        pass
    return await proxy_request(
        f"{config['stt']}{inf_path}",
        request,
        content=body_bytes,
        service="stt",
        model=model,
        agent=agent,
    )


@app.post("/v1/audio/speech")
async def route_tts(request: Request):
    config = resolve_config()
    default_model = resolve_service_alias("tts") or "kokoro"
    model = default_model
    body = None
    data: dict[str, Any] | None = None
    try:
        body = await request.body()
        data = json.loads(body)
        model = data.get("model") or default_model
    except Exception:
        pass
    agent = extract_request_agent(request, data)
    return await proxy_request(
        f"{config['tts']}/v1/audio/speech",
        request,
        content=body,
        service="tts",
        model=model,
        agent=agent,
    )


@app.get("/v1/audio/voices")
async def route_voices(request: Request):
    config = resolve_config()
    return await proxy_request(
        f"{config['tts']}/v1/audio/voices",
        request,
        service="tts",
        model=resolve_service_alias("tts") or "kokoro",
    )


@app.post("/v1/audio/voices/combine")
async def route_voices_combine(request: Request):
    config = resolve_config()
    body = await request.body()
    return await proxy_request(
        f"{config['tts']}/v1/audio/voices/combine",
        request,
        content=body,
        service="tts",
        model=resolve_service_alias("tts") or "kokoro",
    )


@app.post("/v1/images/generations")
async def route_image(request: Request):
    config = resolve_config()
    model = "z-image-turbo"
    body = None
    data: dict[str, Any] | None = None
    try:
        body = await request.body()
        data = json.loads(body)
        model = data.get("model", "z-image-turbo")
    except Exception:
        pass
    agent = extract_request_agent(request, data)
    return await proxy_request(
        f"{config['image']}/v1/images/generations",
        request,
        content=body,
        service="image",
        model=model,
        agent=agent,
    )


@app.post("/v1/completions")
@app.post("/completion")
async def route_completions(request: Request):
    """Routes completions / completion requests to the chat service."""
    config = resolve_config()
    path = request.url.path
    chat_alias = resolve_service_alias("chat") or "qwen3"
    model = chat_alias
    body = None
    data: dict[str, Any] | None = None
    try:
        body = await request.body()
        data = json.loads(body)
        model = data.get("model", chat_alias)
    except Exception:
        pass
    agent = extract_request_agent(request, data)
    return await proxy_request(
        f"{config['chat']}{path}",
        request,
        content=body,
        service="chat",
        model=model,
        agent=agent,
    )


@app.post("/embedding")
async def route_native_embedding(request: Request):
    """Routes native llama.cpp /embedding requests to the embedding service."""
    config = resolve_config()
    agent = extract_request_agent(request)
    body = None
    try:
        body = await request.body()
    except Exception:
        pass
    return await proxy_request(
        f"{config['embedding']}/embedding",
        request,
        content=body,
        service="embedding",
        model="qwen3-embedding",
        agent=agent,
    )


@app.get("/props")
@app.get("/v1/props")
async def route_props(request: Request):
    """Routes properties query to the chat service as default fallback."""
    config = resolve_config()
    agent = extract_request_agent(request)
    path = request.url.path
    return await proxy_request(
        f"{config['chat']}{path}",
        request,
        service="chat",
        model="props",
        agent=agent,
        track_usage=False,
    )


@app.post("/tokenize")
@app.post("/v1/tokenize")
async def route_tokenize(request: Request):
    """Routes tokenization requests to the matching model service backend."""
    body_bytes = await request.body()
    data: dict[str, Any] | None = None
    try:
        parsed = json.loads(body_bytes)
        if isinstance(parsed, dict):
            data = parsed
    except Exception:
        pass

    agent = extract_request_agent(request, data)
    raw_model = data.get("model") if isinstance(data, dict) else None
    model_name = raw_model.strip() if isinstance(raw_model, str) else ""

    config = resolve_config()
    target_svc, resolved_model = resolve_target_service_and_model(model_name)
    target_url = config.get(target_svc, config["chat"])

    path = request.url.path
    return await proxy_request(
        f"{target_url}{path}",
        request,
        content=body_bytes,
        service=target_svc,
        model=resolved_model,
        agent=agent,
    )


@app.post("/detokenize")
@app.post("/v1/detokenize")
async def route_detokenize(request: Request):
    """Routes detokenization requests to the matching model service backend."""
    body_bytes = await request.body()
    data: dict[str, Any] | None = None
    try:
        parsed = json.loads(body_bytes)
        if isinstance(parsed, dict):
            data = parsed
    except Exception:
        pass

    agent = extract_request_agent(request, data)
    raw_model = data.get("model") if isinstance(data, dict) else None
    model_name = raw_model.strip() if isinstance(raw_model, str) else ""

    config = resolve_config()
    target_svc, resolved_model = resolve_target_service_and_model(model_name)
    target_url = config.get(target_svc, config["chat"])

    path = request.url.path
    return await proxy_request(
        f"{target_url}{path}",
        request,
        content=body_bytes,
        service=target_svc,
        model=resolved_model,
        agent=agent,
    )


@app.get("/health")
@app.get("/healthz")
async def route_health():
    """Aggregates router status and connection health checks to registered backends."""
    config = resolve_config()
    res = {"status": "ok", "backends": {}}

    for key, url in config.items():
        match = re.search(r":(\d+)", url)
        if match:
            port = int(match.group(1))
            try:
                with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                    res["backends"][key] = "online"
            except Exception:
                res["backends"][key] = "offline"
        else:
            res["backends"][key] = "unknown"
    return res


@app.get("/v1/models")
async def route_models():
    """Returns the cached model inventory built on startup."""
    return {"object": "list", "data": model_inventory_list}


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"])
async def route_catchall(path: str, request: Request):
    """Graceful handler for unmapped routes."""
    print(f"Error: Route not found: {request.method} /{path}", file=sys.stderr)
    return JSONResponse(
        status_code=404,
        content={
            "error": {
                "message": f"Combined endpoint proxy path '/{path}' not found.",
                "type": "invalid_request_error",
                "code": 404,
            }
        },
    )


if __name__ == "__main__":
    import uvicorn

    host = os.environ.get("LROUT_HOST", "127.0.0.1")
    port = int(os.environ.get("LROUT_PORT", "21080"))
    uvicorn.run(app, host=host, port=port)
