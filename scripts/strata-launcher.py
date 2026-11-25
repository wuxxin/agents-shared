#!/usr/bin/env python3
"""Strata Service Launcher — runtime half of the strata service.

`assistants/local-chat-strata.sh install` copies this file to
`~/.config/systemd/user/local-chat-strata-launcher.py` next to the `.service`,
`.env` and `-config.json`; the unit's ExecStart runs the copy. Keeping it here
means it is lintable, diffable and testable without generating a heredoc, and a
change to it no longer hides inside a 1700-line shell script.

Responsibilities (and deliberately nothing else):

- exports the engine tuning env defaults (os.environ.setdefault) so the engine
  sees them even when the unit's EnvironmentFile lacks a knob,
- applies memory limits (RLIMIT_MEMLOCK) for the HIP allocator,
- reads `-config.json` (written at install time) for argv, env and cwd,
- supervises the engine: start, readiness, idle RAM cache clear (flushing
  parked conversations to Strata's persistent SSD spill tier), SIGUSR1/2
  pre-suspend reclaim, and teardown.

What it does NOT do, by design:

- build argv or decide knobs — `generate_config_json()` in local-chat-strata.sh
  owns that, so argv is inspectable in one JSON file;
- read per-arm overrides from the process environment: `load_env()` in the
  shell script sources `-env` LAST, so the env file wins over the caller's
  environment (learned the hard way in the env battery — a `LCHAT_STRATA_PARALLEL=2`
  override silently did nothing until it was written into the file);
- start, stop or reconfigure itself: tests drive it directly
  (`python3 .../local-chat-strata-launcher.py` in a manager-less shell) rather
  than through systemd, which is how the benchmark batteries got an exclusive
  GPU window with no user bus.
"""
import os
import resource
import signal
import subprocess
import sys
import threading
import time

# Hardware, ROCm, and execution tuning flags
os.environ.setdefault("STRATA_SCORES_THREAD", "1")
os.environ.setdefault("STRATA_WMMA_GEMM", "1")
os.environ.setdefault("STRATA_PF_GEMM", "1")
os.environ.setdefault("STRATA_PF_PAD", "1")
os.environ.setdefault("STRATA_PF_FUSED", "1")
os.environ.setdefault("STRATA_PF_F16", "1")
os.environ.setdefault("STRATA_PF_DM16", "1")
os.environ.setdefault("STRATA_HC_UPMIX", "1")
os.environ.setdefault("STRATA_PF_HCDOWN", "1")
os.environ.setdefault("STRATA_CVEC_FUSE", "1")
os.environ.setdefault("STRATA_PF_HC_REGION", "1")
os.environ.setdefault("STRATA_PLE_COMPACT", "1")
os.environ.setdefault("STRATA_PLE_COPY_STREAM", "1")
os.environ.setdefault("STRATA_PREFILL_WARM", "1")
os.environ.setdefault("STRATA_PREFILL_AUTO_MAX", "24576")
os.environ.setdefault("STRATA_PREFILL_RING", "512")
os.environ.setdefault("STRATA_PREFILL_ROUTED_STREAM", "1")
os.environ.setdefault("STRATA_EMB_REUSE_ACCOUNT", "1")
os.environ.setdefault("STRATA_GDN_HEAD", "1")
os.environ.setdefault("STRATA_GDN_PP", "2")
os.environ.setdefault("STRATA_GDN_CONVL2", "2")
os.environ.setdefault("STRATA_GDN_NOY", "1")
os.environ.setdefault("STRATA_HIP_WMMA", "1")
os.environ.setdefault("STRATA_PA_FAST", "1")
os.environ.setdefault("STRATA_SELECT_WMMA", "1")
os.environ.setdefault("STRATA_Q8_PACKED", "1")
os.environ.setdefault("STRATA_MMVF_ROWS", "1")
os.environ.setdefault("STRATA_ATTN_LANECELL", "1")
os.environ.setdefault("STRATA_ATTN_MERGE_V2", "1")
os.environ.setdefault("STRATA_EXPERT_V2", "1")
os.environ.setdefault("STRATA_TSUM", "1")
os.environ.setdefault("STRATA_LFUSE", "1")
os.environ.setdefault("STRATA_GDN_SPLIT", "1")
os.environ.setdefault("STRATA_QFUSE", "1")
os.environ.setdefault("STRATA_PLE_BATCH", "1")
os.environ.setdefault("STRATA_SMALL_UNR", "3")
os.environ.setdefault("STRATA_GR_Q32_G", "2")
os.environ.setdefault("STRATA_GR_Q8_PFS", "1")
os.environ.setdefault("STRATA_GR_FUSED", "1")
os.environ.setdefault("STRATA_HEAD_MIX_MULTI", "1")
os.environ.setdefault("STRATA_FUSE_HITS", "1")
os.environ.setdefault("STRATA_FUSE_WAIT", "1")
os.environ.setdefault("STRATA_VERIFY_QDEDUP", "1")
os.environ.setdefault("STRATA_SPEC_COST", "1")
os.environ.setdefault("STRATA_FUSE_HEAD_GR", "1")
os.environ.setdefault("STRATA_NORM_ROPE", "1")
tuned_lt = os.path.expanduser(os.environ.get("STRATA_HIPBLASLT_TUNING", "~/.local/state/strata/local-chat-strata-hipblaslt.txt"))
fallback_lt = os.path.join(
    os.environ.get("STRATA_TOOLS_DIR", "/usr/share/strata/terminal/tools"),
    "hip/gfx1100-hipblaslt-100202.txt",
)
os.environ.setdefault(
    "STRATA_HIPBLASLT_TUNING",
    tuned_lt if os.path.exists(tuned_lt) else fallback_lt,
)
os.environ.setdefault("HSA_USERPTR_FOR_PAGED_MEM", "1")
os.environ.setdefault("ROCM_PATH", os.environ.get("ROCM_PATH", "/opt/rocm"))
os.environ.setdefault("HIP_PATH", os.environ.get("HIP_PATH", "/opt/rocm"))
os.environ.setdefault("PYTHONUNBUFFERED", "1")
os.environ.setdefault("STRATA_REQUEST_LINES", "1")
os.environ.setdefault("STRATA_MEMORY_LIMIT_MIB", "0")
os.environ.setdefault("STRATA_RESIDENT_HEADROOM_GIB", "0")
os.environ.setdefault("STRATA_SH_STREAM", "0")
if "LCHAT_STRATA_DEVICE" in os.environ:
    os.environ.setdefault("HIP_VISIBLE_DEVICES", os.environ["LCHAT_STRATA_DEVICE"])
if os.environ.get("LCHAT_STRATA_BATCH_MTP_FUSED", "").strip().lower() in ("1", "true", "yes"):
    os.environ.setdefault("STRATA_BATCH_MTP", "1")
    os.environ.setdefault("STRATA_BATCH_MTP_FUSED", "1")

# Set host memory limits to unlimited
for limit in (resource.RLIMIT_MEMLOCK, resource.RLIMIT_AS, resource.RLIMIT_DATA):
    try:
        resource.setrlimit(limit, (resource.RLIM_INFINITY, resource.RLIM_INFINITY))
    except (ValueError, OSError):
        pass

# Import Strata server and ensure subprocesses stream directly to sys.stderr
sys.path.insert(0, "/usr/share/strata/terminal")
import serve.server as strata_server  # noqa: E402  (needs sys.path above)
from serve import lifeline  # noqa: E402


# Forward engine stderr to sys.stderr while updating conv_log in real time for the Monitor GUI
def _forward_stderr(pipe_r):
    with os.fdopen(pipe_r, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            sys.stderr.write(line)
            sys.stderr.flush()
            if "conversation cache:" in line:
                svc = getattr(strata_server, "_active_svc", None)
                if svc and hasattr(svc, "conv_log"):
                    m = strata_server.ConvCacheLog.EVENT.search(line)
                    if m:
                        st = svc.conv_log.state
                        st["parked"], st["bytes"] = int(m.group(3)), int(m.group(4))
                        if m.group(5) is not None:
                            st["evictions"] = int(m.group(5))
                        if m.group(1) != "skipped":
                            st["parks" if m.group(1) == "parked" else "restores"] += 1
                            st["last_event"], st["last_tokens"], st["last_at"] = m.group(1), int(m.group(2)), time.time()
                    else:
                        m2 = strata_server.ConvCacheLog.DROPPED.search(line)
                        if m2:
                            svc.conv_log.state["parked"] = int(m2.group(1))

_orig_popen = lifeline.popen
def _direct_popen(args, role="engine", **kw):
    if role == "engine":
        r, w = os.pipe()
        kw["stderr"] = w
        proc = _orig_popen(args, role=role, **kw)
        os.close(w)
        threading.Thread(target=_forward_stderr, args=(r,), daemon=True).start()
        return proc
    if kw.get("stderr") in (None, subprocess.DEVNULL):
        kw["stderr"] = sys.stderr
    return _orig_popen(args, role=role, **kw)
lifeline.popen = _direct_popen

_orig_conv_poll = strata_server.ConvCacheLog.poll
def _hooked_conv_poll(self, path, start):
    if not path or start is None:
        return dict(self.state)
    return _orig_conv_poll(self, path, start)
strata_server.ConvCacheLog.poll = _hooked_conv_poll

# Hook Service initialization to capture active service instance and start idle RAM-cache-clear timer

_clear_lock = threading.Lock()


def _clear_ram_cache(reason: str) -> bool:
    """Flush parked RAM conversations to Strata's persistent SSD spill tier and trim host heap.

    Leaves the model weights warm in VRAM. Safe to call from both SIGUSR1 (pre-suspend)
    and the idle cache-clear timer.
    """
    svc = getattr(strata_server, "_active_svc", None)
    if not svc or not svc.loaded():
        return False
    engine = getattr(svc, "engine", None)
    if not engine or not getattr(engine, "proc", None) or not engine.proc.stdin:
        return False
    if not _clear_lock.acquire(blocking=False):
        return False
    try:
        with engine._exclusive_control():
            engine.proc.stdin.write("CLEAR_CACHE\n")
            engine.proc.stdin.flush()
            try:
                resp = engine.lines.get(timeout=30.0)
                sys.stderr.write(f"[strata-launcher] {reason}: CLEAR_CACHE response: {resp.strip()!r}\n")
                return True
            except Exception as e:
                sys.stderr.write(f"[strata-launcher] {reason}: lines.get error: {e}\n")
                return False
    except Exception as e:
        sys.stderr.write(f"[strata-launcher] {reason}: CLEAR_CACHE error: {e}\n")
        return False
    finally:
        _clear_lock.release()


def _start_idle_cache_clear_timer() -> None:
    try:
        idle_s = float(os.environ.get("LCHAT_STRATA_IDLE_CACHE_CLEAR", "3600") or "0")
    except ValueError:
        idle_s = 0.0
    if idle_s <= 0:
        return
    sys.stderr.write(f"[strata-launcher] idle RAM cache clear armed: {idle_s:.0f} s (flushes parked RAM -> persistent SSD spill)\n")

    def _loop() -> None:
        last_cleared_req = -1.0
        poll_s = max(5.0, min(30.0, idle_s / 4.0))
        while True:
            time.sleep(poll_s)
            svc = getattr(strata_server, "_active_svc", None)
            if not svc or not svc.loaded():
                continue
            with svc.status_lock:
                if svc.status.get("busy") or svc.status.get("queued"):
                    continue
            last_req = float(getattr(svc, "last_request_at", 0.0) or 0.0)
            ref_ts = last_req or float(getattr(svc, "started_at", 0.0) or 0.0)
            if last_req <= 0.0 or last_req <= last_cleared_req:
                continue
            if time.time() - ref_ts < idle_s:
                continue
            if not svc.fifo.acquire(blocking=False):
                continue
            try:
                with svc.status_lock:
                    if svc.status.get("busy") or svc.status.get("queued"):
                        continue
                if _clear_ram_cache(f"idle {idle_s:.0f}s"):
                    last_cleared_req = last_req
            finally:
                svc.fifo.release()

    threading.Thread(target=_loop, daemon=True, name="strata-idle-clear").start()


_orig_svc_init = strata_server.Service.__init__
def _hooked_svc_init(self, *a, **kw):
    _orig_svc_init(self, *a, **kw)
    strata_server._active_svc = self
    _start_idle_cache_clear_timer()
strata_server.Service.__init__ = _hooked_svc_init


# Signal handlers for pre-suspend RAM cache flush & reclaim (SIGUSR1) and optional post-suspend restore (SIGUSR2).
# Persistent SSD spill (--conversation-spill-persist) is managed natively by Strata's own LRU (--conversation-spill-mib);
# no external NVMe janitor is run.
def _handle_sigusr1(signum, frame):
    svc = getattr(strata_server, "_active_svc", None)
    if svc and svc.loaded():
        if getattr(svc, "slot_save_path", None) and hasattr(svc, "slot_action"):
            try:
                code, _body = svc.slot_action("0", "save", "suspend-session.bin")
                sys.stderr.write(f"[strata-launcher] SIGUSR1: session saved ({code})\n")
            except Exception as e:
                sys.stderr.write(f"[strata-launcher] SIGUSR1 save error: {e}\n")
        _clear_ram_cache("SIGUSR1")
        try:
            with open("/tmp/strata-reclaimed", "w") as f:
                f.write("ok\n")
        except OSError:
            pass


def _handle_sigusr2(signum, frame):
    svc = getattr(strata_server, "_active_svc", None)
    if svc and getattr(svc, "slot_save_path", None) and hasattr(svc, "slot_action"):
        save_path = os.path.join(svc.slot_save_path, "suspend-session.bin")
        if not os.path.exists(save_path):
            return
        try:
            if not svc.loaded():
                svc.load()
            code, _body = svc.slot_action("0", "restore", "suspend-session.bin")
            sys.stderr.write(f"[strata-launcher] SIGUSR2: session restored ({code})\n")
        except Exception as e:
            sys.stderr.write(f"[strata-launcher] SIGUSR2 restore error: {e}\n")

signal.signal(signal.SIGUSR1, _handle_sigusr1)
signal.signal(signal.SIGUSR2, _handle_sigusr2)


# If custom arguments were passed to launcher, forward them; else construct standard invocation
if len(sys.argv) > 1:
    forward_argv = [sys.argv[0], *sys.argv[1:]]
else:
    forward_argv = [
        sys.argv[0],
        "--engine", "strata",
        "--config", os.environ.get("CONFIG_FILE", f"{os.environ.get('HOME', '')}/.config/systemd/user/local-chat-strata-config.json"),
        "--port", os.environ.get("LCHAT_STRATA_PORT", "20080"),
        "--host", os.environ.get("LCHAT_STRATA_HOST", "127.0.0.1"),
    ]
    extra_args = os.environ.get("LCHAT_STRATA_EXTRA_ARGS", "").strip()
    if extra_args:
        import shlex
        forward_argv.extend(shlex.split(extra_args))

sys.argv = forward_argv
sys.exit(strata_server.main())
