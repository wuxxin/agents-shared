#!/usr/bin/env python3
"""run-local-benchmark.py - Automate running and recording local service benchmarks.

Runs chat, text embedding, reranking, STT, and TTS benchmarks across
HIP, Vulkan, CPU, and Special configurations. Parses output stats
and writes a comprehensive comparative report in assistants/local-benchmark.md.
"""

import argparse
import json
import os
import re
import socket
import subprocess
import time
from typing import Any, Dict, List, Tuple

# ---------------------------------------------------------------------------
# Configuration & Constants
# ---------------------------------------------------------------------------
SYSTEMD_USER_DIR = os.path.expanduser("~/.config/systemd/user")
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Define service metadata
SERVICES: Dict[str, Dict[str, Any]] = {
    "chat": {
        "script": os.path.join(REPO_ROOT, "assistants", "local-llm-ggml.sh"),
        "env_file": os.path.join(SYSTEMD_USER_DIR, "local-llm-ggml.env"),
        "port": 50080,
        "proc_pattern": "llama-server.*--port 50080",
    },
    "embedding": {
        "script": os.path.join(REPO_ROOT, "assistants", "local-embedding.sh"),
        "env_file": os.path.join(SYSTEMD_USER_DIR, "local-embedding.env"),
        "port": 50082,
        "proc_pattern": "llama-server.*--port 50082",
    },
    "rerank": {
        "script": os.path.join(REPO_ROOT, "assistants", "local-rerank.sh"),
        "env_file": os.path.join(SYSTEMD_USER_DIR, "local-rerank.env"),
        "port": 50086,
        "proc_pattern": "llama-server.*--port 50086",
    },
    "stt": {
        "script": os.path.join(REPO_ROOT, "assistants", "local-speech-to-text.sh"),
        "env_file": os.path.join(SYSTEMD_USER_DIR, "local-speech-to-text.env"),
        "port": 50090,
        "proc_pattern": "whisper-server.*--port 50090",
    },
    "tts": {
        "script": os.path.join(REPO_ROOT, "assistants", "local-text-to-speech.sh"),
        "env_file": os.path.join(SYSTEMD_USER_DIR, "local-text-to-speech.env"),
        "port": 50095,
        "proc_pattern": "qwen3-tts-server.*--port 50095",
    },
}


# ---------------------------------------------------------------------------
# Utilities for Environment Manipulation
# ---------------------------------------------------------------------------
def update_env_file(env_file_path: str, updates: Dict[str, Any]) -> None:
    """Read the env file, filter out duplicate definitions, and append updates."""
    if not os.path.exists(env_file_path):
        os.makedirs(os.path.dirname(env_file_path), exist_ok=True)
        lines: List[str] = []
    else:
        with open(env_file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

    # Filter out lines defining the keys we want to override
    new_lines: List[str] = []
    keys_to_remove = set(updates.keys())
    for line in lines:
        stripped = line.strip()
        # Regex to identify variable assignment (handles commented out values as well)
        match = re.match(r"^\s*(?:#\s*)?(?:export\s+)?([A-Za-z0-9_]+)\s*=", stripped)
        if match:
            key = match.group(1)
            if key in keys_to_remove:
                continue
        new_lines.append(line)

    # Ensure clean spacing at EOF
    if new_lines and not new_lines[-1].endswith("\n"):
        new_lines.append("\n")

    # Append our custom assignments
    for key, val in updates.items():
        if isinstance(val, str) and not val.startswith('"') and not val.startswith("'"):
            new_lines.append(f'{key}="{val}"\n')
        else:
            new_lines.append(f"{key}={val}\n")

    # Write the modified content back to the file
    with open(env_file_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)


def read_env_file(env_file_path: str) -> Dict[str, str]:
    """Read environment file and parse active assignments into a dictionary."""
    env_vars: Dict[str, str] = {}
    if not os.path.exists(env_file_path):
        return env_vars
    with open(env_file_path, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            # Ignore comments and empty lines
            if not stripped or stripped.startswith("#"):
                continue
            # Match KEY=VAL or export KEY=VAL
            match = re.match(r"^\s*(?:export\s+)?([A-Za-z0-9_]+)\s*=\s*(.*)$", stripped)
            if match:
                key = match.group(1)
                val = match.group(2).strip()
                # Strip wrapping quotes if present
                if (val.startswith('"') and val.endswith('"')) or (
                    val.startswith("'") and val.endswith("'")
                ):
                    val = val[1:-1]
                env_vars[key] = val
    return env_vars


# ---------------------------------------------------------------------------
def get_gpu_memory_mb() -> float:
    """Get the current VRAM usage in Megabytes (MB) via rocm-smi."""
    try:
        import json

        res = subprocess.run(
            ["/opt/rocm/bin/rocm-smi", "--showmeminfo", "vram", "--json"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        json_str = ""
        for line in res.stdout.splitlines():
            if line.strip().startswith("{"):
                json_str = line
                break
        if json_str:
            data = json.loads(json_str)
            for card in data.values():
                if "VRAM Total Used Memory (B)" in card:
                    bytes_used = float(card["VRAM Total Used Memory (B)"])
                    return bytes_used / (1024.0 * 1024.0)
    except Exception:
        pass
    return 0.0


def get_process_rss_mem_mb(pattern: str) -> float:
    """Find the process matching pattern and return its RSS memory usage in MB."""
    try:
        res = subprocess.run(
            ["pgrep", "-f", pattern],
            capture_output=True,
            text=True,
            timeout=5,
        )
        pids = [p.strip() for p in res.stdout.splitlines() if p.strip()]
        if not pids:
            return 0.0

        total_rss_bytes = 0
        for pid in pids:
            statm_path = f"/proc/{pid}/statm"
            if os.path.exists(statm_path):
                with open(statm_path, "r") as f:
                    fields = f.read().split()
                    if len(fields) >= 2:
                        rss_pages = int(fields[1])
                        page_size = (
                            os.sysconf("SC_PAGE_SIZE")
                            if hasattr(os, "sysconf")
                            else 4096
                        )
                        total_rss_bytes += rss_pages * page_size
        return total_rss_bytes / (1024.0 * 1024.0)
    except Exception as e:
        print(f"Warning measuring CPU memory: {e}")
        return 0.0


def get_mock_gpu_mem(mode: str, config: str) -> float:
    """Get realistic mock GPU memory values for validation runs."""
    if config == "cpu":
        return 0.0

    mems = {
        "llm-chat": {"hip": 14520.0, "vulkan": 14850.0},
        "llm-embed": {"hip": 2620.0, "vulkan": 2650.0},
        "rerank": {"hip": 680.0, "vulkan": 720.0},
        "stt": {"hip": 1820.0, "vulkan": 1950.0},
        "tts": {
            "hip": 2240.0,
            "vulkan": 2420.0,
            "special-hybrid": 850.0,
            "special-gpu-low-mem": 1100.0,
        },
    }
    return mems.get(mode, {}).get(config, 0.0)


def get_mock_cpu_mem(mode: str, config: str) -> float:
    """Get realistic mock CPU memory values for validation runs."""
    mems = {
        "llm-chat": {"hip": 1200.0, "vulkan": 1250.0, "cpu": 0.0},
        "llm-embed": {"hip": 350.0, "vulkan": 360.0, "cpu": 2500.0},
        "rerank": {"hip": 250.0, "vulkan": 260.0, "cpu": 600.0},
        "stt": {"hip": 450.0, "vulkan": 460.0, "cpu": 1200.0},
        "tts": {
            "hip": 300.0,
            "vulkan": 310.0,
            "cpu": 800.0,
            "special-hybrid": 1500.0,
            "special-gpu-low-mem": 400.0,
        },
    }
    return mems.get(mode, {}).get(config, 0.0)


# ---------------------------------------------------------------------------
def warmup_model(url: str, payload: dict, timeout: int = 60) -> bool:
    """Send a warmup request and wait for model to be fully loaded."""
    import json
    import urllib.error
    import urllib.request

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with urllib.request.urlopen(req, timeout=15.0) as response:
                response.read()
                return True
        except urllib.error.HTTPError as e:
            # 503 Service Unavailable or 500 proxy errors
            # mean the model is still loading. Wait and retry.
            print(f"Warmup returned HTTP {e.code}. Retrying in 3 seconds...")
            time.sleep(3)
        except Exception as e:
            # Connection refused or other error
            print(f"Warmup error: {e}. Retrying in 3 seconds...")
            time.sleep(3)
    return False


def wait_for_port(port: int, timeout: int = 90) -> bool:
    """Wait for port to accept TCP connections on localhost."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=1.0):
                return True
        except (socket.timeout, ConnectionRefusedError):
            time.sleep(1.0)
    return False


def wait_for_port_close(port: int, timeout: int = 15) -> bool:
    """Wait for port to close on localhost."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                time.sleep(0.5)
        except (socket.timeout, ConnectionRefusedError):
            return True
    return False


def stop_service(
    service_name: str,
    port: int,
    pattern: str,
    proc: Any,
    master_fd: Any,
) -> None:
    """Cleanly stop the transient service and terminate any orphan servers."""
    import signal

    print(f"Stopping service {service_name} on port {port}...")
    if proc is not None:
        try:
            # 1. Try SIGTERM
            proc.terminate()
            proc.wait(timeout=3)
        except Exception:
            try:
                # 2. Try SIGINT (Ctrl-C)
                proc.send_signal(signal.SIGINT)
                proc.wait(timeout=2)
            except Exception:
                try:
                    # 3. Try SIGKILL
                    proc.kill()
                    proc.wait(timeout=2)
                except Exception:
                    pass

    if master_fd is not None:
        try:
            os.close(master_fd)
        except Exception:
            pass

    # Clean up orphan servers
    try:
        # Try SIGTERM first
        subprocess.run(["pkill", "-f", pattern], capture_output=True)
        time.sleep(1)
        # Force SIGKILL to ensure no stuck processes remain
        subprocess.run(["pkill", "-9", "-f", pattern], capture_output=True)
    except Exception as e:
        print(f"Warning running pkill for {service_name}: {e}")

    # Wait for port to be fully released
    if not wait_for_port_close(port):
        raise RuntimeError(
            f"Failed to stop service {service_name} on port {port}: port did not close cleanly in time."
        )


def start_service(script_path: str) -> Tuple[subprocess.Popen, int]:
    """Start the service transiently using the script's exec action in a pseudo-terminal (PTY)."""
    import pty

    master_fd, slave_fd = pty.openpty()
    proc = subprocess.Popen(
        [script_path, "exec"],
        stdin=slave_fd,
        stdout=slave_fd,
        stderr=slave_fd,
        close_fds=True,
        cwd=os.path.dirname(script_path),
    )
    os.close(slave_fd)
    return proc, master_fd


def run_benchmark(script_path: str, args: List[str]) -> Tuple[str, bool]:
    """Execute the service test command with args and return captured stdout and success flag."""
    cmd = [script_path, "test"] + args
    print(f"Running benchmark command: {' '.join(cmd)}")
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=os.path.dirname(script_path),
    )
    if result.returncode != 0:
        print(f"Error running benchmark. Exit code: {result.returncode}")
        print(f"Stderr: {result.stderr}")
        return result.stdout, False
    return result.stdout, True


# ---------------------------------------------------------------------------
# Regex Parsers
# ---------------------------------------------------------------------------
def extract_metric(
    pattern: str,
    text: str,
    group_idx: int = 1,
    default: float = 0.0,
) -> float:
    """Extract a float metric from text using a regular expression."""
    match = re.search(pattern, text)
    if match:
        try:
            return float(match.group(group_idx))
        except ValueError:
            return default
    return default


def parse_chat_output(output: str) -> Dict[str, float]:
    """Parse chat benchmark stats from stdout."""
    res = {}

    # Partition Phase 0 and Phase 2
    p0_content = ""
    p2_content = ""

    parts_p0 = output.split("--- Phase 0: Warmup ---")
    if len(parts_p0) > 1:
        p0_content = parts_p0[1].split("---")[0]

    parts_p2 = output.split("--- Phase 2: Generation (300-word summary) ---")
    if len(parts_p2) > 1:
        p2_content = parts_p2[1].split("---")[0]

    if p0_content:
        res["chat_warmup_prompt"] = extract_metric(
            r"Prompt Tokens:\s+(\d+)", p0_content
        )
        res["chat_warmup_comp"] = extract_metric(
            r"Completion Tokens:\s+(\d+)", p0_content
        )
        res["chat_warmup_ttft"] = extract_metric(
            r"TTFT \(Prefill\):\s+([\d\.]+)\s+ms", p0_content
        )
        res["chat_warmup_prefill"] = extract_metric(
            r"Prefill Speed:\s+([\d\.]+)\s+tokens", p0_content
        )
        res["chat_warmup_gen"] = extract_metric(
            r"Generation Speed:\s+([\d\.]+)\s+tokens", p0_content
        )

    if p2_content:
        res["chat_avg_comp"] = extract_metric(
            r"Avg Completion Tokens:\s+([\d\.]+)", p2_content
        )
        res["chat_avg_ttft"] = extract_metric(
            r"Avg TTFT \(Prefill\):\s+([\d\.]+)\s+ms", p2_content
        )
        res["chat_avg_prefill"] = extract_metric(
            r"Avg Prefill Speed:\s+([\d\.]+)\s+tokens", p2_content
        )
        res["chat_avg_gen"] = extract_metric(
            r"Avg Generation Speed:\s+([\d\.]+)\s+tokens", p2_content
        )
        res["chat_avg_decode"] = extract_metric(
            r"Avg Decode Time:\s+([\d\.]+)\s+s", p2_content
        )

    return res


def parse_embed_output(output: str) -> Dict[str, float]:
    """Parse embedding benchmark stats from stdout."""
    res = {}
    res["embed_throughput"] = extract_metric(
        r"Avg Throughput:\s+([\d\.]+)\s+tokens/sec", output
    )
    res["embed_time_s"] = extract_metric(r"Avg Time/Run:\s+([\d\.]+)\s+s", output)
    res["embed_lat"] = extract_metric(r"Avg Chunk Latency:\s+([\d\.]+)\s+ms", output)
    res["embed_p50"] = extract_metric(r"Avg Chunk p50:\s+([\d\.]+)\s+ms", output)
    res["embed_p95"] = extract_metric(r"Avg Chunk p95:\s+([\d\.]+)\s+ms", output)
    return res


def parse_rerank_output(output: str) -> Dict[str, float]:
    """Parse reranker benchmark stats from stdout."""
    res = {}
    res["rerank_time"] = extract_metric(r"Avg Reranking Time:\s*([\d\.]+)\s*ms", output)
    res["rerank_throughput"] = extract_metric(
        r"Avg Docs Throughput:\s*([\d\.]+)\s*docs", output
    )
    res["rerank_token_speed"] = extract_metric(
        r"Avg Token Speed:\s*([\d\.]+)\s*tokens", output
    )
    return res


def parse_stt_output(output: str) -> Dict[str, float]:
    """Parse STT benchmark stats from stdout."""
    res = {}
    res["stt_time"] = extract_metric(
        r"Avg Transcribe Time:\s*([\d\.]+)\s*seconds", output
    )
    res["stt_rtf"] = extract_metric(r"Avg RTF:\s*([\d\.]+)", output)
    return res


def parse_tts_output(output: str) -> Dict[str, float]:
    """Parse TTS benchmark stats from stdout."""
    res = {}
    res["tts_duration"] = extract_metric(
        r"Audio Duration:\s*([\d\.]+)\s*seconds", output
    )
    res["tts_time"] = extract_metric(
        r"Avg Synthesis Time:\s*([\d\.]+)\s*seconds", output
    )
    res["tts_rtf"] = extract_metric(r"Avg RTF:\s*([\d\.]+)", output)
    res["tts_char_speed"] = extract_metric(r"Avg Speed:\s*([\d\.]+)\s*chars", output)
    return res


# ---------------------------------------------------------------------------
# Mock Outputs for Validation
# ---------------------------------------------------------------------------
def get_mock_output(mode: str, config: str) -> str:
    """Generate typical stdout data for validation testing in sandbox environments."""
    factors = {
        "hip": 1.0,
        "vulkan": 1.15,
        "cpu": 4.5,
        "special-hybrid": 0.8,
        "special-gpu-low-mem": 1.2,
    }
    fac = factors.get(config, 1.0)

    if mode == "llm-chat":
        return f"""
Running local-llm-ggml validation tests...
Using endpoint base: http://127.0.0.1:50080
--- Phase 0: Warmup ---
  Prompt Tokens:        19
  Completion Tokens:    148
  TTFT (Prefill):       {56.06 * fac:.2f} ms
  Prefill Speed:        {338.90 / fac:.2f} tokens/sec
  Generation Speed:     {73.59 / fac:.2f} tokens/sec

--- Phase 2: Generation (300-word summary) ---
  Runs:                 3
  Prompt Tokens:        29246
  Avg Completion Tokens: 600.0
  Avg TTFT (Prefill):   {27709.08 * fac:.2f} ms
  Avg Prefill Speed:    {1120.25 / fac:.2f} tokens/sec
  Avg Generation Speed: {43.96 / fac:.2f} tokens/sec
  Avg Decode Time:      {13.65 * fac:.2f} s
"""
    elif mode == "llm-embed":
        return f"""
=== EMBEDDING BENCHMARK RESULTS SUMMARY         ===
  Avg Tokens/Run:       45460
  Avg Time/Run:         {9.06 * fac:.2f} s
  Avg Throughput:       {5019.28 / fac:.2f} tokens/sec

  Avg Chunk Latency:    {1509.5 * fac:.1f} ms
  Avg Chunk p50:        {1638.0 * fac:.1f} ms
  Avg Chunk p95:        {1816.9 * fac:.1f} ms
"""
    elif mode == "rerank":
        return f"""
=== RERANK BENCHMARK RESULTS SUMMARY ===
Avg Reranking Time:   {25761.59 * fac:.2f} ms
Avg Docs Throughput:  {0.39 / fac:.2f} docs/sec
Avg Token Speed:      {133.49 / fac:.2f} tokens/sec
"""
    elif mode == "stt":
        return f"""
=== Speech-to-Text Benchmark Results (Cumulative Average) ===
Avg Transcribe Time:  {1.45 * fac:.2f} seconds
Avg RTF:              {0.0321 * fac:.4f}
"""
    elif mode == "tts":
        return f"""
=== Text-to-Speech Benchmark Results (Cumulative Average) ===
Audio Duration:       15.74 seconds
Avg Synthesis Time:   {23.47 * fac:.2f} seconds
Avg RTF:              {1.4914 * fac:.4f}
Avg Speed:            {11.67 / fac:.2f} chars/sec (1.92 words/sec)
"""
    return ""


# ---------------------------------------------------------------------------
# Report Generator
# ---------------------------------------------------------------------------
def generate_report(data: Dict[str, Dict[str, Dict[str, Any]]]) -> str:
    """Format parsed metrics into a beautiful markdown benchmark document."""

    def format_env(cfg: str, mode: str) -> str:
        if cfg in data and mode in data[cfg] and "env" in data[cfg][mode]:
            env_vars = data[cfg][mode]["env"]
            if isinstance(env_vars, dict):
                lines = []
                for k, v in sorted(env_vars.items()):
                    lines.append(f'  - `{k}="{v}"`')
                return "\n".join(lines)
        return "  - *No environment settings recorded*"

    # Helper to print values safely
    def val(
        cfg: str,
        mode: str,
        key: str,
        fmt: str = ".2f",
        suffix: str = "",
        default: str = "N/A",
    ) -> str:
        if cfg in data and mode in data[cfg] and key in data[cfg][mode]:
            return f"{data[cfg][mode][key]:{fmt}}{suffix}"
        return default

    # Speedup ratio vs Real-time (1 / RTF)
    def speedup(cfg: str, mode: str, rtf_key: str) -> str:
        if cfg in data and mode in data[cfg] and rtf_key in data[cfg][mode]:
            rtf = data[cfg][mode][rtf_key]
            if rtf > 0:
                return f"{1.0 / rtf:.1f}x"
        return "N/A"

    def get_test_name(cfg: str, mode: str) -> str:
        if cfg in data and mode in data[cfg] and "test_name" in data[cfg][mode]:
            return str(data[cfg][mode]["test_name"])
        fallback_names = {
            "llm-chat": "chat",
            "llm-embed": "embedding",
            "rerank": "rerank",
            "stt": "stt",
            "tts": "tts",
        }
        base = fallback_names.get(mode, mode)
        return f"{base}_{cfg}"

    def get_device_setting(cfg: str, mode: str) -> str:
        if cfg in data and mode in data[cfg] and "device_setting" in data[cfg][mode]:
            return str(data[cfg][mode]["device_setting"])
        if cfg in data and mode in data[cfg] and "env" in data[cfg][mode]:
            env = data[cfg][mode]["env"]
            if isinstance(env, dict):
                for k in [
                    "LLM_DEVICE",
                    "EMBED_DEVICE",
                    "LRR_DEVICE",
                    "LSTT_DEVICE",
                    "LTTS_DEVICE",
                ]:
                    if k in env and env[k]:
                        return env[k]
        if cfg == "hip":
            return (
                "ROCm0"
                if mode in ("llm-chat", "llm-embed", "rerank")
                else ("0" if mode == "stt" else "Default")
            )
        elif cfg == "vulkan":
            return (
                "Vulkan0"
                if mode in ("llm-chat", "llm-embed", "rerank")
                else ("0" if mode == "stt" else "Default")
            )
        elif cfg == "cpu":
            return (
                "BLAS"
                if mode in ("llm-chat", "llm-embed", "rerank")
                else "Default (CPU)"
            )
        return "Default"

    def get_special_setting(cfg: str, mode: str) -> str:
        if cfg in data and mode in data[cfg] and "special_setting" in data[cfg][mode]:
            return str(data[cfg][mode]["special_setting"])
        if cfg in data and mode in data[cfg] and "env" in data[cfg][mode]:
            env = data[cfg][mode]["env"]
            if isinstance(env, dict):
                if mode == "tts" and "LTTS_MODE" in env:
                    return f"mode: {env['LTTS_MODE']}"
                for k in ["LLM_N_GPU_LAYERS", "EMBED_N_GPU_LAYERS", "LR_N_GPU_LAYERS"]:
                    if k in env:
                        return f"Layers: {env[k]}"
                if "LSTT_NO_GPU" in env:
                    return "No GPU" if env["LSTT_NO_GPU"] == "true" else "Use GPU"
        if cfg == "special-hybrid":
            return "mode: hybrid"
        elif cfg == "special-gpu-low-mem":
            return "mode: gpu-min-vram"
        return "None"

    import datetime

    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report = f"""# LLM Caching Optimization Benchmarks

**Benchmark Run Time:** `{now_str}`

## Local Inference Services Benchmarks

We ran local benchmarks for text embedding, text-to-speech (TTS), speech-to-text (STT), and document reranking on the AMD Radeon Pro W6800 hardware target. All services run inside isolated sandboxed environments.

### 📊 Performance Comparison Matrix

#### Text Chat (`local-llm-ggml`)
| Configuration | Test Name | Device Setting | Special Setting | Avg Chat TTFT | Avg Chat Prefill | Chat TTFT (Warmup) | Chat Gen Speed | Avg Chat Gen | Chat GPU Mem | Chat CPU Mem |
|---|---|---|---|---|---|---|---|---|---|---|
| **HIP** | {get_test_name("hip", "llm-chat")} | {get_device_setting("hip", "llm-chat")} | {get_special_setting("hip", "llm-chat")} | {val("hip", "llm-chat", "chat_avg_ttft", ".2f", " ms")} | {val("hip", "llm-chat", "chat_avg_prefill", ".2f", " t/s")} | {val("hip", "llm-chat", "chat_warmup_ttft", ".2f", " ms")} | {val("hip", "llm-chat", "chat_warmup_gen", ".2f", " t/s")} | {val("hip", "llm-chat", "chat_avg_gen", ".2f", " t/s")} | {val("hip", "llm-chat", "gpu_mem_mb", ".1f", " MB")} | {val("hip", "llm-chat", "cpu_mem_mb", ".1f", " MB")} |
| **Vulkan** | {get_test_name("vulkan", "llm-chat")} | {get_device_setting("vulkan", "llm-chat")} | {get_special_setting("vulkan", "llm-chat")} | {val("vulkan", "llm-chat", "chat_avg_ttft", ".2f", " ms")} | {val("vulkan", "llm-chat", "chat_avg_prefill", ".2f", " t/s")} | {val("vulkan", "llm-chat", "chat_warmup_ttft", ".2f", " ms")} | {val("vulkan", "llm-chat", "chat_warmup_gen", ".2f", " t/s")} | {val("vulkan", "llm-chat", "chat_avg_gen", ".2f", " t/s")} | {val("vulkan", "llm-chat", "gpu_mem_mb", ".1f", " MB")} | {val("vulkan", "llm-chat", "cpu_mem_mb", ".1f", " MB")} |
| **CPU** | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |

#### Text Embedding (`local-embedding`)
| Configuration | Test Name | Device Setting | Special Setting | Embedding Throughput | Embedding Latency (Avg) | Embedding GPU Mem | Embedding CPU Mem |
|---|---|---|---|---|---|---|---|
| **HIP** | {get_test_name("hip", "llm-embed")} | {get_device_setting("hip", "llm-embed")} | {get_special_setting("hip", "llm-embed")} | {val("hip", "llm-embed", "embed_throughput", ".2f", " t/s")} | {val("hip", "llm-embed", "embed_lat", ".1f", " ms")} | {val("hip", "llm-embed", "gpu_mem_mb", ".1f", " MB")} | {val("hip", "llm-embed", "cpu_mem_mb", ".1f", " MB")} |
| **Vulkan** | {get_test_name("vulkan", "llm-embed")} | {get_device_setting("vulkan", "llm-embed")} | {get_special_setting("vulkan", "llm-embed")} | {val("vulkan", "llm-embed", "embed_throughput", ".2f", " t/s")} | {val("vulkan", "llm-embed", "embed_lat", ".1f", " ms")} | {val("vulkan", "llm-embed", "gpu_mem_mb", ".1f", " MB")} | {val("vulkan", "llm-embed", "cpu_mem_mb", ".1f", " MB")} |
| **CPU** | {get_test_name("cpu", "llm-embed")} | {get_device_setting("cpu", "llm-embed")} | {get_special_setting("cpu", "llm-embed")} | {val("cpu", "llm-embed", "embed_throughput", ".2f", " t/s")} | {val("cpu", "llm-embed", "embed_lat", ".1f", " ms")} | {val("cpu", "llm-embed", "gpu_mem_mb", ".1f", " MB")} | {val("cpu", "llm-embed", "cpu_mem_mb", ".1f", " MB")} |

#### Document Reranking (`local-rerank`)
| Configuration | Test Name | Device Setting | Special Setting | Avg Reranking Time | Avg Token Speed | Avg Docs Throughput | GPU Mem | CPU Mem |
|---|---|---|---|---|---|---|---|---|
| **HIP** | {get_test_name("hip", "rerank")} | {get_device_setting("hip", "rerank")} | {get_special_setting("hip", "rerank")} | {val("hip", "rerank", "rerank_time", ".2f", " ms")} | {val("hip", "rerank", "rerank_token_speed", ".2f", " tokens/s")} | {val("hip", "rerank", "rerank_throughput", ".2f", " docs/s")} | {val("hip", "rerank", "gpu_mem_mb", ".1f", " MB")} | {val("hip", "rerank", "cpu_mem_mb", ".1f", " MB")} |
| **Vulkan** | {get_test_name("vulkan", "rerank")} | {get_device_setting("vulkan", "rerank")} | {get_special_setting("vulkan", "rerank")} | {val("vulkan", "rerank", "rerank_time", ".2f", " ms")} | {val("vulkan", "rerank", "rerank_token_speed", ".2f", " tokens/s")} | {val("vulkan", "rerank", "rerank_throughput", ".2f", " docs/s")} | {val("vulkan", "rerank", "gpu_mem_mb", ".1f", " MB")} | {val("vulkan", "rerank", "cpu_mem_mb", ".1f", " MB")} |
| **CPU** | {get_test_name("cpu", "rerank")} | {get_device_setting("cpu", "rerank")} | {get_special_setting("cpu", "rerank")} | {val("cpu", "rerank", "rerank_time", ".2f", " ms")} | {val("cpu", "rerank", "rerank_token_speed", ".2f", " tokens/s")} | {val("cpu", "rerank", "rerank_throughput", ".2f", " docs/s")} | {val("cpu", "rerank", "gpu_mem_mb", ".1f", " MB")} | {val("cpu", "rerank", "cpu_mem_mb", ".1f", " MB")} |

#### Speech-to-Text (STT) (`local-speech-to-text`)
| Configuration | Test Name | Device Setting | Special Setting | Avg Transcribe Time | Avg Real-Time Factor (RTF) | Speedup vs Real-time | GPU Mem | CPU Mem |
|---|---|---|---|---|---|---|---|---|
| **HIP** | {get_test_name("hip", "stt")} | {get_device_setting("hip", "stt")} | {get_special_setting("hip", "stt")} | {val("hip", "stt", "stt_time", ".2f", " s")} | {val("hip", "stt", "stt_rtf", ".4f")} | {speedup("hip", "stt", "stt_rtf")} | {val("hip", "stt", "gpu_mem_mb", ".1f", " MB")} | {val("hip", "stt", "cpu_mem_mb", ".1f", " MB")} |
| **Vulkan** | {get_test_name("vulkan", "stt")} | {get_device_setting("vulkan", "stt")} | {get_special_setting("vulkan", "stt")} | {val("vulkan", "stt", "stt_time", ".2f", " s")} | {val("vulkan", "stt", "stt_rtf", ".4f")} | {speedup("vulkan", "stt", "stt_rtf")} | {val("vulkan", "stt", "gpu_mem_mb", ".1f", " MB")} | {val("vulkan", "stt", "cpu_mem_mb", ".1f", " MB")} |
| **CPU** | {get_test_name("cpu", "stt")} | {get_device_setting("cpu", "stt")} | {get_special_setting("cpu", "stt")} | {val("cpu", "stt", "stt_time", ".2f", " s")} | {val("cpu", "stt", "stt_rtf", ".4f")} | {speedup("cpu", "stt", "stt_rtf")} | {val("cpu", "stt", "gpu_mem_mb", ".1f", " MB")} | {val("cpu", "stt", "cpu_mem_mb", ".1f", " MB")} |

#### Text-to-Speech (TTS) (`local-text-to-speech`)
| Configuration | Test Name | Device Setting | Special Setting | Avg Synthesis Time | Avg Real-Time Factor (RTF) | Speed (chars/s) | GPU Mem | CPU Mem |
|---|---|---|---|---|---|---|---|---|
| **HIP** | {get_test_name("hip", "tts")} | {get_device_setting("hip", "tts")} | {get_special_setting("hip", "tts")} | {val("hip", "tts", "tts_time", ".2f", " s")} | {val("hip", "tts", "tts_rtf", ".4f")} | {val("hip", "tts", "tts_char_speed", ".2f", " chars/s")} | {val("hip", "tts", "gpu_mem_mb", ".1f", " MB")} | {val("hip", "tts", "cpu_mem_mb", ".1f", " MB")} |
| **Vulkan** | {get_test_name("vulkan", "tts")} | {get_device_setting("vulkan", "tts")} | {get_special_setting("vulkan", "tts")} | {val("vulkan", "tts", "tts_time", ".2f", " s")} | {val("vulkan", "tts", "tts_rtf", ".4f")} | {val("vulkan", "tts", "tts_char_speed", ".2f", " chars/s")} | {val("vulkan", "tts", "gpu_mem_mb", ".1f", " MB")} | {val("vulkan", "tts", "cpu_mem_mb", ".1f", " MB")} |
| **CPU** | {get_test_name("cpu", "tts")} | {get_device_setting("cpu", "tts")} | {get_special_setting("cpu", "tts")} | {val("cpu", "tts", "tts_time", ".2f", " s")} | {val("cpu", "tts", "tts_rtf", ".4f")} | {val("cpu", "tts", "tts_char_speed", ".2f", " chars/s")} | {val("cpu", "tts", "gpu_mem_mb", ".1f", " MB")} | {val("cpu", "tts", "cpu_mem_mb", ".1f", " MB")} |
| **Special (Hybrid)** | {get_test_name("special-hybrid", "tts")} | {get_device_setting("special-hybrid", "tts")} | {get_special_setting("special-hybrid", "tts")} | {val("special-hybrid", "tts", "tts_time", ".2f", " s")} | {val("special-hybrid", "tts", "tts_rtf", ".4f")} | {val("special-hybrid", "tts", "tts_char_speed", ".2f", " chars/s")} | {val("special-hybrid", "tts", "gpu_mem_mb", ".1f", " MB")} | {val("special-hybrid", "tts", "cpu_mem_mb", ".1f", " MB")} |
| **Special (Low-Mem)** | {get_test_name("special-gpu-low-mem", "tts")} | {get_device_setting("special-gpu-low-mem", "tts")} | {get_special_setting("special-gpu-low-mem", "tts")} | {val("special-gpu-low-mem", "tts", "tts_time", ".2f", " s")} | {val("special-gpu-low-mem", "tts", "tts_rtf", ".4f")} | {val("special-gpu-low-mem", "tts", "tts_char_speed", ".2f", " chars/s")} | {val("special-gpu-low-mem", "tts", "gpu_mem_mb", ".1f", " MB")} | {val("special-gpu-low-mem", "tts", "cpu_mem_mb", ".1f", " MB")} |

---

### ⚙️ Detailed Configuration Reports

"""

    for cfg in sorted(data.keys()):
        if not data[cfg]:
            continue
        cfg_upper = cfg.upper()
        if cfg == "special-hybrid":
            cfg_upper = "SPECIAL (HYBRID)"
        elif cfg == "special-gpu-low-mem":
            cfg_upper = "SPECIAL (GPU-LOW-MEM)"

        report += f"### {cfg_upper} Configuration Details\n\n"

        # Chat details
        if "llm-chat" in data[cfg]:
            report += f"""#### Text Chat (`local-llm-ggml`)
- **Benchmark Test Name:** `{get_test_name(cfg, "llm-chat")}`
- **Device Setting:** `{get_device_setting(cfg, "llm-chat")}`
- **Special Setting:** `{get_special_setting(cfg, "llm-chat")}`
- **Model:** `qwen3` (`Qwen3.6-35B-A3B-APEX-I-Compact`)
- **Execution Target:** `{cfg_upper}`
- **GPU Memory Used:** {val(cfg, "llm-chat", "gpu_mem_mb", ".1f", " MB")}
- **CPU Memory Used:** {val(cfg, "llm-chat", "cpu_mem_mb", ".1f", " MB")}
- **Benchmark Running Time:** {val(cfg, "llm-chat", "bench_time_s", ".2f", " s")}
- **Active Environment Settings:**
{format_env(cfg, "llm-chat")}
- **Warmup (Phase 0):**
  - TTFT (Prefill):       {val(cfg, "llm-chat", "chat_warmup_ttft", ".2f", " ms")}
  - Prefill Speed:        {val(cfg, "llm-chat", "chat_warmup_prefill", ".2f", " tokens/sec")}
  - Generation Speed:     {val(cfg, "llm-chat", "chat_warmup_gen", ".2f", " tokens/sec")}
- **Generation (Phase 2):**
  - Avg Completion Tokens: {val(cfg, "llm-chat", "chat_avg_comp", ".1f")}
  - Avg TTFT (Prefill):   {val(cfg, "llm-chat", "chat_avg_ttft", ".2f", " ms")}
  - Avg Prefill Speed:    {val(cfg, "llm-chat", "chat_avg_prefill", ".2f", " tokens/sec")}
  - Avg Generation Speed: {val(cfg, "llm-chat", "chat_avg_gen", ".2f", " tokens/sec")}
  - Avg Decode Time:      {val(cfg, "llm-chat", "chat_avg_decode", ".2f", " s")}

"""

        # Embedding details
        if "llm-embed" in data[cfg]:
            report += f"""#### Text Embedding (`local-embedding`)
- **Benchmark Test Name:** `{get_test_name(cfg, "llm-embed")}`
- **Device Setting:** `{get_device_setting(cfg, "llm-embed")}`
- **Special Setting:** `{get_special_setting(cfg, "llm-embed")}`
- **Model:** `qwen3-embedding` (`Qwen3-Embedding-0.6B-Q8_0.gguf`)
- **Execution Target:** `{cfg_upper}`
- **GPU Memory Used:** {val(cfg, "llm-embed", "gpu_mem_mb", ".1f", " MB")}
- **CPU Memory Used:** {val(cfg, "llm-embed", "cpu_mem_mb", ".1f", " MB")}
- **Benchmark Running Time:** {val(cfg, "llm-embed", "bench_time_s", ".2f", " s")}
- **Active Environment Settings:**
{format_env(cfg, "llm-embed")}
- **Metrics:**
  - Avg Time/Run:         {val(cfg, "llm-embed", "embed_time_s", ".2f", " s")}
  - Avg Throughput:       {val(cfg, "llm-embed", "embed_throughput", ".2f", " tokens/sec")}
  - Avg Chunk Latency:    {val(cfg, "llm-embed", "embed_lat", ".1f", " ms")}
  - Avg Chunk p50:        {val(cfg, "llm-embed", "embed_p50", ".1f", " ms")}
  - Avg Chunk p95:        {val(cfg, "llm-embed", "embed_p95", ".1f", " ms")}

"""

        # Reranker details
        if "rerank" in data[cfg]:
            report += f"""#### Document Reranking (`local-rerank`)
- **Benchmark Test Name:** `{get_test_name(cfg, "rerank")}`
- **Device Setting:** `{get_device_setting(cfg, "rerank")}`
- **Special Setting:** `{get_special_setting(cfg, "rerank")}`
- **Model:** `qwen3-reranker` (`Qwen3-Reranker-0.6B.Q4_K_M.gguf`)
- **Execution Target:** `{cfg_upper}`
- **GPU Memory Used:** {val(cfg, "rerank", "gpu_mem_mb", ".1f", " MB")}
- **CPU Memory Used:** {val(cfg, "rerank", "cpu_mem_mb", ".1f", " MB")}
- **Benchmark Running Time:** {val(cfg, "rerank", "bench_time_s", ".2f", " s")}
- **Active Environment Settings:**
{format_env(cfg, "rerank")}
- **Metrics:**
  - Avg Reranking Time:   {val(cfg, "rerank", "rerank_time", ".2f", " ms")}
  - Avg Docs Throughput:  {val(cfg, "rerank", "rerank_throughput", ".2f", " docs/sec")}
  - Avg Token Speed:      {val(cfg, "rerank", "rerank_token_speed", ".2f", " tokens/sec")}

"""

        # STT details
        if "stt" in data[cfg]:
            report += f"""#### Speech-to-Text (STT) (`local-speech-to-text`)
- **Benchmark Test Name:** `{get_test_name(cfg, "stt")}`
- **Device Setting:** `{get_device_setting(cfg, "stt")}`
- **Special Setting:** `{get_special_setting(cfg, "stt")}`
- **Model:** `whisper-1` (`ggml-large-v3-turbo-q5_0.bin`)
- **Execution Target:** `{cfg_upper}`
- **GPU Memory Used:** {val(cfg, "stt", "gpu_mem_mb", ".1f", " MB")}
- **CPU Memory Used:** {val(cfg, "stt", "cpu_mem_mb", ".1f", " MB")}
- **Benchmark Running Time:** {val(cfg, "stt", "bench_time_s", ".2f", " s")}
- **Active Environment Settings:**
{format_env(cfg, "stt")}
- **Metrics:**
  - Avg Transcribe Time:  {val(cfg, "stt", "stt_time", ".2f", " seconds")}
  - Avg Real-Time Factor (RTF): {val(cfg, "stt", "stt_rtf", ".4f")} ({speedup(cfg, "stt", "stt_rtf")} faster than real-time)

"""

        # TTS details
        if "tts" in data[cfg]:
            report += f"""#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Benchmark Test Name:** `{get_test_name(cfg, "tts")}`
- **Device Setting:** `{get_device_setting(cfg, "tts")}`
- **Special Setting:** `{get_special_setting(cfg, "tts")}`
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `{cfg_upper}`
- **GPU Memory Used:** {val(cfg, "tts", "gpu_mem_mb", ".1f", " MB")}
- **CPU Memory Used:** {val(cfg, "tts", "cpu_mem_mb", ".1f", " MB")}
- **Benchmark Running Time:** {val(cfg, "tts", "bench_time_s", ".2f", " s")}
- **Active Environment Settings:**
{format_env(cfg, "tts")}
- **Metrics:**
  - Generated Audio Duration: {val(cfg, "tts", "tts_duration", ".2f", " seconds")}
  - Avg Synthesis Time:   {val(cfg, "tts", "tts_time", ".2f", " seconds")}
  - Avg Real-Time Factor (RTF): {val(cfg, "tts", "tts_rtf", ".4f")}
  - Avg Speed:            {val(cfg, "tts", "tts_char_speed", ".2f", " chars/sec")}

"""

    return report


# ---------------------------------------------------------------------------
# Main Execution Loop
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run local inference service benchmarks across different hardware acceleration backends."
    )
    parser.add_argument(
        "--configs",
        type=str,
        default="hip,vulkan,cpu,special",
        help="Comma-separated list of hardware configurations to test (default: hip,vulkan,cpu,special)",
    )
    parser.add_argument(
        "--only-services",
        type=str,
        default="chat,embedding,rerank,stt,tts",
        help="Comma-separated list of services to test (default: chat,embedding,rerank,stt,tts)",
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Simulate execution and parsing (dry-run/mocking mode for systemd-less environments)",
    )
    parser.add_argument(
        "--output-file",
        type=str,
        default=os.path.join(REPO_ROOT, "assistants", "local-benchmark.md"),
        help="Path to write the output markdown report (default: assistants/local-benchmark.md)",
    )

    args = parser.parse_args()

    target_configs = [c.strip().lower() for c in args.configs.split(",")]
    target_services = [s.strip().lower() for s in args.only_services.split(",")]

    print("==================================================")
    print("🚀 Local Inference Service Benchmark Suite")
    print("==================================================")
    print(f"Configs to test:  {', '.join(target_configs)}")
    print(f"Services to test: {', '.join(target_services)}")
    print(f"Output report:    {args.output_file}")
    if args.mock:
        print("💡 Running in MOCK mode (simulated runs)")
    print("==================================================\n")

    cache_file = os.path.splitext(args.output_file)[0] + ".json"
    benchmark_data: Dict[str, Dict[str, Dict[str, Any]]] = {}

    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                benchmark_data = json.load(f)
            print(f"Loaded existing benchmark state from: {cache_file}")
        except Exception as e:
            print(f"Warning: Failed to load benchmark cache: {e}")

    for cfg in target_configs:
        print(f"\n--- Testing Configuration: {cfg.upper()} ---")
        if cfg not in benchmark_data:
            benchmark_data[cfg] = {}

        # ---------------------------------------------------------
        # 1. Chat Service
        # ---------------------------------------------------------
        if "chat" in target_services:
            srv = SERVICES["chat"]
            if cfg == "special":
                print("Skipping Chat for Special configuration.")
            elif cfg == "cpu":
                print("Skipping Chat for CPU configuration.")
            else:
                print(f"Preparing environment file: {srv['env_file']}")
                proc = None
                master_fd = None
                if not args.mock:
                    # Install service default config
                    subprocess.run(
                        [srv["script"], "install", "--no-start", "--new-config"],
                        check=True,
                    )

                    # Update configuration settings for current config
                    device_map = {
                        "hip": "ROCm0",
                        "vulkan": "Vulkan0",
                        "cpu": "",
                    }
                    llm_device = device_map.get(cfg, cfg)
                    updates = {
                        "LLM_DEVICE": llm_device,
                        "LLM_N_GPU_LAYERS": 0 if cfg == "cpu" else 999,
                        "LLM_N_CTX": 240000,
                        "LLM_SERVE_EMBEDDINGS": "false",
                    }
                    update_env_file(srv["env_file"], updates)

                    # Start service
                    proc, master_fd = start_service(srv["script"])

                    # Wait for server readiness
                    print(f"Waiting for llama-server on port {srv['port']}...")
                    if not wait_for_port(srv["port"]):
                        print(
                            f"Error: llama-server failed to start on port {srv['port']}."
                        )
                        stop_service(
                            "chat",
                            srv["port"],
                            srv["proc_pattern"],
                            proc,
                            master_fd,
                        )
                        continue
                else:
                    proc = None

                baseline_vram = 0.0
                if not args.mock:
                    baseline_vram = get_gpu_memory_mb()

                # Run benchmarks
                print("Running LLM Chat benchmark")
                if not args.mock:
                    print("Warming up chat model (qwen3)...")
                    warmup_model(
                        f"http://127.0.0.1:{srv['port']}/v1/chat/completions",
                        {
                            "model": "qwen3",
                            "messages": [{"role": "user", "content": "ping"}],
                            "max_tokens": 1,
                        },
                    )
                    test_args = [
                        "--benchmark",
                        "--skip-prefill",
                        "--skip-distractor",
                        "--repeat",
                        "1",
                        "--only-chat",
                    ]
                    start_time = time.time()
                    stdout, success = run_benchmark(srv["script"], test_args)
                    if not success:
                        print(f"⚠️ Warning: Benchmark command for chat on config '{cfg}' returned a non-zero exit code or failed. Preserving existing cached results if available.")
                    else:
                        elapsed_time = time.time() - start_time
                        benchmark_data[cfg]["llm-chat"] = parse_chat_output(stdout)
                        benchmark_data[cfg]["llm-chat"]["bench_time_s"] = elapsed_time

                        # Measure VRAM and RAM right before stopping
                        post_run_vram = get_gpu_memory_mb()
                        gpu_mem_mb = max(0.0, post_run_vram - baseline_vram)
                        cpu_mem_mb = get_process_rss_mem_mb(srv["proc_pattern"])

                        benchmark_data[cfg]["llm-chat"]["gpu_mem_mb"] = gpu_mem_mb
                        benchmark_data[cfg]["llm-chat"]["cpu_mem_mb"] = cpu_mem_mb
                        benchmark_data[cfg]["llm-chat"]["test_name"] = f"chat_{cfg}"
                        benchmark_data[cfg]["llm-chat"]["device_setting"] = (
                            llm_device if llm_device else "Default"
                        )
                        benchmark_data[cfg]["llm-chat"]["special_setting"] = (
                            f"Layers: {999 if cfg != 'cpu' else 0}"
                        )
                        benchmark_data[cfg]["llm-chat"]["env"] = read_env_file(
                            srv["env_file"]
                        )
                else:
                    stdout = get_mock_output("llm-chat", cfg)
                    benchmark_data[cfg]["llm-chat"] = parse_chat_output(stdout)
                    benchmark_data[cfg]["llm-chat"]["gpu_mem_mb"] = get_mock_gpu_mem(
                        "llm-chat", cfg
                    )
                    benchmark_data[cfg]["llm-chat"]["cpu_mem_mb"] = get_mock_cpu_mem(
                        "llm-chat", cfg
                    )
                    benchmark_data[cfg]["llm-chat"]["bench_time_s"] = 15.4
                    benchmark_data[cfg]["llm-chat"]["test_name"] = f"chat_{cfg}"
                    benchmark_data[cfg]["llm-chat"]["device_setting"] = (
                        "ROCm0"
                        if cfg == "hip"
                        else ("Vulkan0" if cfg == "vulkan" else "Default")
                    )
                    benchmark_data[cfg]["llm-chat"]["special_setting"] = (
                        f"Layers: {999 if cfg != 'cpu' else 0}"
                    )
                    benchmark_data[cfg]["llm-chat"]["env"] = {
                        "LLM_DEVICE": "ROCm0"
                        if cfg == "hip"
                        else ("Vulkan0" if cfg == "vulkan" else ""),
                        "LLM_N_GPU_LAYERS": "999" if cfg != "cpu" else "0",
                        "LLM_N_CTX": "240000",
                        "LLM_SERVE_EMBEDDINGS": "false",
                    }

                # Stop service
                if not args.mock:
                    stop_service(
                        "chat",
                        srv["port"],
                        srv["proc_pattern"],
                        proc,
                        master_fd,
                    )

        # ---------------------------------------------------------
        # 1.5 Embedding Service
        # ---------------------------------------------------------
        if "embedding" in target_services:
            srv = SERVICES["embedding"]
            if cfg == "special":
                print("Skipping Embedding for Special configuration.")
            elif cfg == "cpu":
                print("Skipping Embedding for CPU configuration.")
            else:
                print(f"Preparing environment file: {srv['env_file']}")
                proc = None
                master_fd = None
                if not args.mock:
                    # Install service default config
                    subprocess.run(
                        [srv["script"], "install", "--no-start", "--new-config"],
                        check=True,
                    )

                    # Update configuration settings for current config
                    device_map = {
                        "hip": "ROCm0",
                        "vulkan": "Vulkan0",
                        "cpu": "BLAS",
                    }
                    embed_device = device_map.get(cfg, cfg)
                    updates = {
                        "EMBED_DEVICE": embed_device,
                        "EMBED_N_GPU_LAYERS": 0 if cfg == "cpu" else 999,
                    }
                    update_env_file(srv["env_file"], updates)

                    # Start service
                    proc, master_fd = start_service(srv["script"])

                    # Wait for server readiness
                    print(f"Waiting for llama-server on port {srv['port']}...")
                    if not wait_for_port(srv["port"]):
                        print(
                            f"Error: llama-server failed to start on port {srv['port']}."
                        )
                        stop_service(
                            "embedding",
                            srv["port"],
                            srv["proc_pattern"],
                            proc,
                            master_fd,
                        )
                        continue
                else:
                    proc = None

                baseline_vram = 0.0
                if not args.mock:
                    baseline_vram = get_gpu_memory_mb()

                # Run benchmarks
                print("Running LLM Embedding benchmark")
                if not args.mock:
                    print("Warming up embedding model (qwen3-embedding)...")
                    warmup_model(
                        f"http://127.0.0.1:{srv['port']}/v1/embeddings",
                        {
                            "model": "qwen3-embedding",
                            "input": "ping",
                        },
                    )
                    test_args = [
                        "--benchmark",
                        "--repeat",
                        "1",
                    ]
                    start_time = time.time()
                    stdout, success = run_benchmark(srv["script"], test_args)
                    if not success:
                        print(f"⚠️ Warning: Benchmark command for embedding on config '{cfg}' returned a non-zero exit code or failed. Preserving existing cached results if available.")
                    else:
                        elapsed_time = time.time() - start_time
                        benchmark_data[cfg]["llm-embed"] = parse_embed_output(stdout)
                        benchmark_data[cfg]["llm-embed"]["bench_time_s"] = elapsed_time

                        # Measure VRAM and RAM right before stopping
                        post_run_vram = get_gpu_memory_mb()
                        gpu_mem_mb = max(0.0, post_run_vram - baseline_vram)
                        cpu_mem_mb = get_process_rss_mem_mb(srv["proc_pattern"])

                        benchmark_data[cfg]["llm-embed"]["gpu_mem_mb"] = gpu_mem_mb
                        benchmark_data[cfg]["llm-embed"]["cpu_mem_mb"] = cpu_mem_mb
                        benchmark_data[cfg]["llm-embed"]["test_name"] = f"embedding_{cfg}"
                        benchmark_data[cfg]["llm-embed"]["device_setting"] = (
                            embed_device if embed_device else "Default"
                        )
                        benchmark_data[cfg]["llm-embed"]["special_setting"] = (
                            f"Layers: {999 if cfg != 'cpu' else 0}"
                        )
                        benchmark_data[cfg]["llm-embed"]["env"] = read_env_file(
                            srv["env_file"]
                        )
                else:
                    stdout = get_mock_output("llm-embed", cfg)
                    benchmark_data[cfg]["llm-embed"] = parse_embed_output(stdout)
                    benchmark_data[cfg]["llm-embed"]["gpu_mem_mb"] = get_mock_gpu_mem(
                        "llm-embed", cfg
                    )
                    benchmark_data[cfg]["llm-embed"]["cpu_mem_mb"] = get_mock_cpu_mem(
                        "llm-embed", cfg
                    )
                    benchmark_data[cfg]["llm-embed"]["bench_time_s"] = 10.2
                    benchmark_data[cfg]["llm-embed"]["test_name"] = f"embedding_{cfg}"
                    benchmark_data[cfg]["llm-embed"]["device_setting"] = (
                        "ROCm0"
                        if cfg == "hip"
                        else (
                            "Vulkan0"
                            if cfg == "vulkan"
                            else ("BLAS" if cfg == "cpu" else "Default")
                        )
                    )
                    benchmark_data[cfg]["llm-embed"]["special_setting"] = (
                        f"Layers: {999 if cfg != 'cpu' else 0}"
                    )
                    benchmark_data[cfg]["llm-embed"]["env"] = {
                        "EMBED_DEVICE": "ROCm0"
                        if cfg == "hip"
                        else ("Vulkan0" if cfg == "vulkan" else ""),
                        "EMBED_N_GPU_LAYERS": "999" if cfg != "cpu" else "0",
                    }

                # Stop service
                if not args.mock:
                    stop_service(
                        "embedding",
                        srv["port"],
                        srv["proc_pattern"],
                        proc,
                        master_fd,
                    )

        # ---------------------------------------------------------
        # 2. Document Reranker
        # ---------------------------------------------------------
        if "rerank" in target_services:
            srv = SERVICES["rerank"]
            if cfg == "special":
                print("Skipping Reranker for Special configuration.")
            else:
                print(f"Preparing environment file: {srv['env_file']}")
                proc = None
                master_fd = None
                baseline_vram = 0.0
                if not args.mock:
                    baseline_vram = get_gpu_memory_mb()
                    subprocess.run(
                        [srv["script"], "install", "--no-start", "--new-config"],
                        check=True,
                    )
                    device_map = {
                        "hip": "ROCm0",
                        "vulkan": "Vulkan0",
                        "cpu": "BLAS",
                    }
                    lrr_device = device_map.get(cfg, cfg)
                    updates = {
                        "LRR_DEVICE": lrr_device,
                        "LR_N_GPU_LAYERS": 0 if cfg == "cpu" else 99,
                    }
                    update_env_file(srv["env_file"], updates)

                    proc, master_fd = start_service(srv["script"])
                    print(f"Waiting for reranker on port {srv['port']}...")
                    if not wait_for_port(srv["port"]):
                        print(f"Error: reranker failed to start on port {srv['port']}.")
                        stop_service(
                            "rerank",
                            srv["port"],
                            srv["proc_pattern"],
                            proc,
                            master_fd,
                        )
                        continue
                else:
                    proc = None

                print("Running reranker benchmark...")
                if not args.mock:
                    print("Warming up reranker model (qwen3-reranker)...")
                    warmup_model(
                        f"http://127.0.0.1:{srv['port']}/v1/rerank",
                        {
                            "model": "qwen3-reranker",
                            "query": "ping",
                            "documents": ["ping"],
                        },
                    )
                    start_time = time.time()
                    stdout, success = run_benchmark(
                        srv["script"], ["--benchmark", "--repeat", "1"]
                    )
                    if not success:
                        print(f"⚠️ Warning: Benchmark command for reranker on config '{cfg}' returned a non-zero exit code or failed. Preserving existing cached results if available.")
                    else:
                        elapsed_time = time.time() - start_time
                        benchmark_data[cfg]["rerank"] = parse_rerank_output(stdout)
                        benchmark_data[cfg]["rerank"]["bench_time_s"] = elapsed_time
                        post_run_vram = get_gpu_memory_mb()
                        gpu_mem_mb = max(0.0, post_run_vram - baseline_vram)
                        cpu_mem_mb = get_process_rss_mem_mb(srv["proc_pattern"])
                        benchmark_data[cfg]["rerank"]["gpu_mem_mb"] = gpu_mem_mb
                        benchmark_data[cfg]["rerank"]["cpu_mem_mb"] = cpu_mem_mb
                        benchmark_data[cfg]["rerank"]["test_name"] = f"rerank_{cfg}"
                        benchmark_data[cfg]["rerank"]["device_setting"] = (
                            lrr_device if lrr_device else "Default"
                        )
                        benchmark_data[cfg]["rerank"]["special_setting"] = (
                            f"Layers: {99 if cfg != 'cpu' else 0}"
                        )
                        benchmark_data[cfg]["rerank"]["env"] = read_env_file(
                            srv["env_file"]
                        )
                else:
                    stdout = get_mock_output("rerank", cfg)
                    benchmark_data[cfg]["rerank"] = parse_rerank_output(stdout)
                    benchmark_data[cfg]["rerank"]["gpu_mem_mb"] = get_mock_gpu_mem(
                        "rerank", cfg
                    )
                    benchmark_data[cfg]["rerank"]["cpu_mem_mb"] = get_mock_cpu_mem(
                        "rerank", cfg
                    )
                    benchmark_data[cfg]["rerank"]["bench_time_s"] = 8.7
                    benchmark_data[cfg]["rerank"]["test_name"] = f"rerank_{cfg}"
                    benchmark_data[cfg]["rerank"]["device_setting"] = (
                        "ROCm0"
                        if cfg == "hip"
                        else (
                            "Vulkan0"
                            if cfg == "vulkan"
                            else ("BLAS" if cfg == "cpu" else "Default")
                        )
                    )
                    benchmark_data[cfg]["rerank"]["special_setting"] = (
                        f"Layers: {99 if cfg != 'cpu' else 0}"
                    )
                    benchmark_data[cfg]["rerank"]["env"] = {
                        "LRR_DEVICE": "ROCm0"
                        if cfg == "hip"
                        else ("Vulkan0" if cfg == "vulkan" else ""),
                        "LR_N_GPU_LAYERS": "99" if cfg != "cpu" else "0",
                    }

                if not args.mock:
                    stop_service(
                        "rerank",
                        srv["port"],
                        srv["proc_pattern"],
                        proc,
                        master_fd,
                    )

        # ---------------------------------------------------------
        # 3. Speech-to-Text (STT)
        # ---------------------------------------------------------
        if "stt" in target_services:
            srv = SERVICES["stt"]
            if cfg == "special":
                print("Skipping STT for Special configuration.")
            else:
                print(f"Preparing environment file: {srv['env_file']}")
                proc = None
                master_fd = None
                baseline_vram = 0.0
                if not args.mock:
                    baseline_vram = get_gpu_memory_mb()
                    subprocess.run(
                        [srv["script"], "install", "--no-start", "--new-config"],
                        check=True,
                    )

                    lstt_device = "0" if cfg in ("vulkan", "hip") else ""
                    updates = {
                        "LSTT_DEVICE": lstt_device,
                        "LSTT_NO_GPU": "true" if cfg == "cpu" else "false",
                    }
                    update_env_file(srv["env_file"], updates)

                    proc, master_fd = start_service(srv["script"])
                    print(f"Waiting for whisper-server on port {srv['port']}...")
                    if not wait_for_port(srv["port"]):
                        print(
                            f"Error: whisper-server failed to start on port {srv['port']}."
                        )
                        stop_service(
                            "stt",
                            srv["port"],
                            srv["proc_pattern"],
                            proc,
                            master_fd,
                        )
                        continue
                else:
                    proc = None

                print("Running STT benchmark...")
                if not args.mock:
                    start_time = time.time()
                    stdout, success = run_benchmark(
                        srv["script"], ["--benchmark", "--repeat", "1"]
                    )
                    if not success:
                        print(f"⚠️ Warning: Benchmark command for STT on config '{cfg}' returned a non-zero exit code or failed. Preserving existing cached results if available.")
                    else:
                        elapsed_time = time.time() - start_time
                        benchmark_data[cfg]["stt"] = parse_stt_output(stdout)
                        benchmark_data[cfg]["stt"]["bench_time_s"] = elapsed_time
                        post_run_vram = get_gpu_memory_mb()
                        gpu_mem_mb = max(0.0, post_run_vram - baseline_vram)
                        cpu_mem_mb = get_process_rss_mem_mb(srv["proc_pattern"])
                        benchmark_data[cfg]["stt"]["gpu_mem_mb"] = gpu_mem_mb
                        benchmark_data[cfg]["stt"]["cpu_mem_mb"] = cpu_mem_mb
                        benchmark_data[cfg]["stt"]["test_name"] = f"stt_{cfg}"
                        benchmark_data[cfg]["stt"]["device_setting"] = (
                            lstt_device if lstt_device else "Default"
                        )
                        benchmark_data[cfg]["stt"]["special_setting"] = (
                            "No GPU" if cfg == "cpu" else "Use GPU"
                        )
                        benchmark_data[cfg]["stt"]["env"] = read_env_file(srv["env_file"])
                else:
                    stdout = get_mock_output("stt", cfg)
                    benchmark_data[cfg]["stt"] = parse_stt_output(stdout)
                    benchmark_data[cfg]["stt"]["gpu_mem_mb"] = get_mock_gpu_mem(
                        "stt", cfg
                    )
                    benchmark_data[cfg]["stt"]["cpu_mem_mb"] = get_mock_cpu_mem(
                        "stt", cfg
                    )
                    benchmark_data[cfg]["stt"]["bench_time_s"] = 5.3
                    benchmark_data[cfg]["stt"]["test_name"] = f"stt_{cfg}"
                    benchmark_data[cfg]["stt"]["device_setting"] = (
                        "0" if cfg != "cpu" else "Default"
                    )
                    benchmark_data[cfg]["stt"]["special_setting"] = (
                        "No GPU" if cfg == "cpu" else "Use GPU"
                    )
                    benchmark_data[cfg]["stt"]["env"] = {
                        "LSTT_DEVICE": "0" if cfg != "cpu" else "",
                        "LSTT_NO_GPU": "false" if cfg != "cpu" else "true",
                    }

                if not args.mock:
                    stop_service(
                        "stt",
                        srv["port"],
                        srv["proc_pattern"],
                        proc,
                        master_fd,
                    )

        # ---------------------------------------------------------
        # 4. Text-to-Speech (TTS)
        # ---------------------------------------------------------
        if "tts" in target_services:
            srv = SERVICES["tts"]

            # Determine which TTS modes to test for this configuration
            if cfg == "special":
                tts_modes_to_test = [
                    ("special-hybrid", "hybrid", "hip"),
                    ("special-gpu-low-mem", "gpu-min-vram", "hip"),
                ]
            else:
                ltts_mode = "cpu-only" if cfg == "cpu" else "gpu"
                ltts_device = "cpu" if cfg == "cpu" else cfg
                tts_modes_to_test = [(cfg, ltts_mode, ltts_device)]

            for data_key, ltts_mode, ltts_device in tts_modes_to_test:
                print(
                    f"Running TTS benchmark for mode '{ltts_mode}' on device '{ltts_device}' (key: {data_key})"
                )
                print(f"Preparing environment file: {srv['env_file']}")
                proc = None
                master_fd = None
                baseline_vram = 0.0
                if not args.mock:
                    baseline_vram = get_gpu_memory_mb()
                    subprocess.run(
                        [srv["script"], "install", "--no-start", "--new-config"],
                        check=True,
                    )

                    # Self-healing check: check if qwen3-tts-server supports --device
                    actual_device = ltts_device
                    try:
                        res = subprocess.run(
                            ["qwen3-tts-server", "--help"],
                            capture_output=True,
                            text=True,
                            timeout=2,
                        )
                        if (
                            "--device" not in res.stdout
                            and "--device" not in res.stderr
                        ):
                            # Clear device argument since it's not supported by this binary
                            actual_device = ""
                    except Exception:
                        actual_device = ""

                    updates = {
                        "LTTS_MODE": ltts_mode,
                        "LTTS_DEVICE": actual_device,
                    }
                    update_env_file(srv["env_file"], updates)

                    proc, master_fd = start_service(srv["script"])
                    print(f"Waiting for qwen3-tts-server on port {srv['port']}...")
                    if not wait_for_port(srv["port"]):
                        print(
                            f"Error: qwen3-tts-server failed to start on port {srv['port']}."
                        )
                        stop_service(
                            "tts",
                            srv["port"],
                            srv["proc_pattern"],
                            proc,
                            master_fd,
                        )
                        continue
                else:
                    proc = None

                print("Running TTS benchmark...")
                # Initialize sub-dict for data_key if not exists
                if data_key not in benchmark_data:
                    benchmark_data[data_key] = {}

                if not args.mock:
                    start_time = time.time()
                    stdout, success = run_benchmark(
                        srv["script"], ["--benchmark", "--repeat", "1"]
                    )
                    if not success:
                        print(f"⚠️ Warning: Benchmark command for TTS on config '{data_key}' (mode: {ltts_mode}) returned a non-zero exit code or failed. Preserving existing cached results if available.")
                    else:
                        elapsed_time = time.time() - start_time
                        benchmark_data[data_key]["tts"] = parse_tts_output(stdout)
                        benchmark_data[data_key]["tts"]["bench_time_s"] = elapsed_time
                        post_run_vram = get_gpu_memory_mb()
                        gpu_mem_mb = max(0.0, post_run_vram - baseline_vram)
                        cpu_mem_mb = get_process_rss_mem_mb(srv["proc_pattern"])
                        benchmark_data[data_key]["tts"]["gpu_mem_mb"] = gpu_mem_mb
                        benchmark_data[data_key]["tts"]["cpu_mem_mb"] = cpu_mem_mb
                        benchmark_data[data_key]["tts"]["test_name"] = f"tts_{data_key}"
                        benchmark_data[data_key]["tts"]["device_setting"] = (
                            actual_device if actual_device else "Default"
                        )
                        benchmark_data[data_key]["tts"]["special_setting"] = (
                            f"mode: {ltts_mode}"
                        )
                        benchmark_data[data_key]["tts"]["env"] = read_env_file(
                            srv["env_file"]
                        )
                else:
                    stdout = get_mock_output("tts", data_key)
                    benchmark_data[data_key]["tts"] = parse_tts_output(stdout)
                    benchmark_data[data_key]["tts"]["gpu_mem_mb"] = get_mock_gpu_mem(
                        "tts", data_key
                    )
                    benchmark_data[data_key]["tts"]["cpu_mem_mb"] = get_mock_cpu_mem(
                        "tts", data_key
                    )
                    benchmark_data[data_key]["tts"]["bench_time_s"] = 25.1
                    benchmark_data[data_key]["tts"]["test_name"] = f"tts_{data_key}"
                    benchmark_data[data_key]["tts"]["device_setting"] = (
                        ltts_device if ltts_device else "Default"
                    )
                    benchmark_data[data_key]["tts"]["special_setting"] = (
                        f"mode: {ltts_mode}"
                    )
                    benchmark_data[data_key]["tts"]["env"] = {
                        "LTTS_MODE": ltts_mode,
                        "LTTS_DEVICE": ltts_device,
                    }

                if not args.mock:
                    stop_service(
                        "tts",
                        srv["port"],
                        srv["proc_pattern"],
                        proc,
                        master_fd,
                    )
        pass

    # Save the cache JSON file next to the markdown report
    try:
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(benchmark_data, f, indent=4, sort_keys=True)
        print(f"Successfully saved benchmark state to: {cache_file}")
    except Exception as e:
        print(f"Error saving benchmark state: {e}")

    # ---------------------------------------------------------
    # Generate Output Report
    # ---------------------------------------------------------
    print("\n==================================================")
    print("📝 Generating Comparative Benchmark Report...")
    print("==================================================")
    report_content = generate_report(benchmark_data)

    # Save report
    os.makedirs(os.path.dirname(args.output_file), exist_ok=True)
    with open(args.output_file, "w", encoding="utf-8") as f:
        f.write(report_content)
    print(f"Successfully wrote report to: {args.output_file}")


if __name__ == "__main__":
    main()
