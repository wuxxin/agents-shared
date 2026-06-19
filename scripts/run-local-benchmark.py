#!/usr/bin/env python3
"""run-local-benchmark.py - Automate running and recording local service benchmarks.

Runs chat, text embedding, reranking, STT, and TTS benchmarks across
HIP, Vulkan, CPU, and Special configurations. Parses output stats
and writes a comprehensive comparative report in assistants/local-benchmark.md.
"""

import argparse
import datetime
import json
import os
import re
import socket
import subprocess
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union

# Known iGPU GFX versions
IGPU_GFX_IDS = frozenset({
    "gfx90c", "gfx902", "gfx909", "gfx1035", "gfx1036", "gfx1103", "gfx1150"
})

@dataclass
class GPUCard:
    rocm_smi_card: str         # e.g. "card0"
    name: str                  # e.g. "AMD Radeon RX 7900 XTX"
    gfx_version: str           # e.g. "gfx1100"
    vram_total_mb: float
    is_igpu: bool
    rocm_index: Optional[int]  # ROCm device index
    vulkan_index: Optional[int] # Vulkan device index

class GPURegistry:
    def __init__(self):
        self.cards: List[GPUCard] = []

    def get_by_smi_card(self, card: str) -> Optional[GPUCard]:
        return next((c for c in self.cards if c.rocm_smi_card == card), None)

    def get_by_rocm_index(self, idx: int) -> Optional[GPUCard]:
        return next((c for c in self.cards if c.rocm_index == idx), None)

    def get_by_vulkan_index(self, idx: int) -> Optional[GPUCard]:
        return next((c for c in self.cards if c.vulkan_index == idx), None)
        
    def get_by_device_string(self, device: str) -> Optional[GPUCard]:
        if not device:
            return None
        match = re.search(r"\d+", device)
        if not match:
            return None
        idx = int(match.group(0))
        if "rocm" in device.lower():
            return self.get_by_rocm_index(idx)
        if "vulkan" in device.lower():
            return self.get_by_vulkan_index(idx)
        return None

GLOBAL_GPU_REGISTRY = GPURegistry()

# Configuration & Constants

SYSTEMD_USER_DIR = os.path.expanduser("~/.config/systemd/user")
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Define service metadata
SERVICES: Dict[str, Dict[str, Any]] = {
    "chat": {
        "script": os.path.join(REPO_ROOT, "assistants", "local-chat.sh"),
        "env_file": os.path.join(SYSTEMD_USER_DIR, "local-chat.env"),
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
    "image": {
        "script": os.path.join(REPO_ROOT, "assistants", "local-image.sh"),
        "env_file": os.path.join(SYSTEMD_USER_DIR, "local-image.env"),
        "port": 50100,
        "proc_pattern": "sd-server.*--listen-port 50100",
    },
}


# Utilities for Environment Manipulation


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


def get_visible_devices_env(
    run_cfg: str, device: str, hip_devices_resolved: List[str]
) -> Tuple[str, str]:
    """Determine the appropriate HIP_VISIBLE_DEVICES and CUDA_VISIBLE_DEVICES values.

    Returns a tuple of (hip_visible, cuda_visible) values.
    """
    if run_cfg in ("vulkan", "cpu"):
        return "", ""

    is_hip = run_cfg == "hip"
    is_special_hip = (
        run_cfg == "special"
        and device
        and ("rocm" in device.lower() or "hip" in device.lower())
    )

    if is_hip or is_special_hip:
        if device and ("rocm" in device.lower() or "hip" in device.lower()):
            gpu = GLOBAL_GPU_REGISTRY.get_by_device_string(device)
            if gpu and gpu.rocm_index is not None:
                idx = str(gpu.rocm_index)
            else:
                idx_match = re.search(r"\d+", device)
                idx = idx_match.group(0) if idx_match else "0"
            return idx, idx
        else:
            indices = []
            for d in hip_devices_resolved:
                gpu = GLOBAL_GPU_REGISTRY.get_by_device_string(d)
                if gpu and gpu.rocm_index is not None:
                    indices.append(str(gpu.rocm_index))
                else:
                    idx_match = re.search(r"\d+", d)
                    if idx_match:
                        indices.append(idx_match.group(0))
            if indices:
                val = ",".join(indices)
                return val, val
            return "0", "0"

    return "", ""


def read_env_file(env_file_path: str) -> Dict[str, Any]:
    """Read environment file and parse active assignments into a dictionary."""
    env_vars: Dict[str, Any] = {}
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


def is_systemd_accessible() -> bool:
    """Check if systemd user socket is accessible."""
    xdg_runtime_dir = os.environ.get("XDG_RUNTIME_DIR")
    if not xdg_runtime_dir:
        try:
            uid = os.getuid()
            xdg_runtime_dir = f"/run/user/{uid}"
        except Exception:
            return False
    socket_path = os.path.join(xdg_runtime_dir, "systemd/private")
    try:
        import stat

        return stat.S_ISSOCK(os.stat(socket_path).st_mode)
    except Exception:
        return False


def get_journal_errors(service_name: str, since_time: str) -> List[str]:
    """Retrieve error lines from journalctl for the given systemd user service."""
    if not is_systemd_accessible():
        return []
    try:
        res = subprocess.run(
            [
                "journalctl",
                "--user",
                "-u",
                f"{service_name}.service",
                "--since",
                since_time,
                "--no-pager",
            ],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if res.returncode == 0:
            error_lines = []
            for line in res.stdout.splitlines():
                if "error" in line.lower():
                    error_lines.append(line.strip())
            return error_lines
    except Exception as e:
        print(f"Warning reading journalctl logs for {service_name}: {e}")
    return []


def get_gpu_memory_mb(device_id: str | None = None) -> float:
    """Get the current VRAM usage in Megabytes (MB) via rocm-smi for a specific device."""
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
            target_key = None
            if device_id:
                gpu = GLOBAL_GPU_REGISTRY.get_by_device_string(device_id)
                if gpu:
                    target_key = gpu.rocm_smi_card
            
            if target_key and target_key in data and "VRAM Total Used Memory (B)" in data[target_key]:
                return float(data[target_key]["VRAM Total Used Memory (B)"]) / (1024.0 * 1024.0)

            # Fallback to the first card with memory info
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

    lookup_cfg = config
    if config.startswith("cpu-hip") or config.startswith("cpu-vulkan"):
        lookup_cfg = "special-hybrid"
    elif config == "running":
        lookup_cfg = "hip"

    mems = {
        "chat": {"hip": 14520.0, "vulkan": 14850.0},
        "embedding": {"hip": 2620.0, "vulkan": 2650.0},
        "rerank": {"hip": 680.0, "vulkan": 720.0},
        "stt": {"hip": 1820.0, "vulkan": 1950.0},
        "tts": {
            "hip": 2240.0,
            "vulkan": 2420.0,
            "special-hybrid": 850.0,
        },
        "image": {
            "hip": 8500.0,
            "vulkan": 8800.0,
        },
    }
    return mems.get(mode, {}).get(lookup_cfg, 0.0)


def get_mock_cpu_mem(mode: str, config: str) -> float:
    """Get realistic mock CPU memory values for validation runs."""
    lookup_cfg = config
    if config.startswith("cpu-hip") or config.startswith("cpu-vulkan"):
        lookup_cfg = "special-hybrid"
    elif config == "running":
        lookup_cfg = "hip"

    mems = {
        "chat": {"hip": 1200.0, "vulkan": 1250.0, "cpu": 0.0},
        "embedding": {"hip": 350.0, "vulkan": 360.0, "cpu": 2500.0},
        "rerank": {"hip": 250.0, "vulkan": 260.0, "cpu": 600.0},
        "stt": {"hip": 450.0, "vulkan": 460.0, "cpu": 1200.0},
        "tts": {
            "hip": 300.0,
            "vulkan": 310.0,
            "cpu": 800.0,
            "special-hybrid": 1500.0,
        },
        "image": {
            "hip": 500.0,
            "vulkan": 550.0,
            "cpu": 9500.0,
        },
    }
    return mems.get(mode, {}).get(lookup_cfg, 0.0)


def set_service_fail_metrics(
    benchmark_data: Dict[str, Dict[str, Dict[str, Any]]],
    cfg_key: str,
    service: str,
    device_setting: str,
    special_setting: str,
    env_file: str,
    errors: List[str],
    updates: Optional[Dict[str, Any]] = None,
) -> None:
    if cfg_key not in benchmark_data:
        benchmark_data[cfg_key] = {}

    env_data = {}
    if os.path.exists(env_file):
        try:
            env_data = read_env_file(env_file)
        except Exception:
            pass
    if updates:
        env_data.update(updates)

    if service == "chat":
        benchmark_data[cfg_key]["chat"] = {
            "chat_avg_ttft": "-fail-",
            "chat_avg_prefill": "-fail-",
            "chat_warmup_ttft": "-fail-",
            "chat_warmup_gen": "-fail-",
            "chat_avg_gen": "-fail-",
            "gpu_mem_mb": "-fail-",
            "cpu_mem_mb": "-fail-",
            "bench_time_s": "-fail-",
            "errors": errors,
            "test_name": f"chat_{cfg_key}",
            "device_setting": device_setting,
            "special_setting": special_setting,
            "env": env_data,
        }
    elif service == "embedding":
        benchmark_data[cfg_key]["embedding"] = {
            "embed_throughput": "-fail-",
            "embed_lat": "-fail-",
            "gpu_mem_mb": "-fail-",
            "cpu_mem_mb": "-fail-",
            "bench_time_s": "-fail-",
            "errors": errors,
            "test_name": f"embedding_{cfg_key}",
            "device_setting": device_setting,
            "special_setting": special_setting,
            "env": env_data,
        }
    elif service == "rerank":
        benchmark_data[cfg_key]["rerank"] = {
            "rerank_time": "-fail-",
            "rerank_token_speed": "-fail-",
            "rerank_throughput": "-fail-",
            "gpu_mem_mb": "-fail-",
            "cpu_mem_mb": "-fail-",
            "bench_time_s": "-fail-",
            "errors": errors,
            "test_name": f"rerank_{cfg_key}",
            "device_setting": device_setting,
            "special_setting": special_setting,
            "env": env_data,
        }
    elif service == "stt":
        benchmark_data[cfg_key]["stt"] = {
            "stt_time": "-fail-",
            "stt_rtf": "-fail-",
            "gpu_mem_mb": "-fail-",
            "cpu_mem_mb": "-fail-",
            "bench_time_s": "-fail-",
            "errors": errors,
            "test_name": f"stt_{cfg_key}",
            "device_setting": device_setting,
            "special_setting": special_setting,
            "env": env_data,
        }
    elif service == "tts":
        benchmark_data[cfg_key]["tts"] = {
            "tts_duration": "-fail-",
            "tts_time": "-fail-",
            "tts_rtf": "-fail-",
            "tts_char_speed": "-fail-",
            "gpu_mem_mb": "-fail-",
            "cpu_mem_mb": "-fail-",
            "bench_time_s": "-fail-",
            "errors": errors,
            "test_name": f"tts_{cfg_key}",
            "device_setting": device_setting,
            "special_setting": special_setting,
            "env": env_data,
        }
    elif service == "image":
        benchmark_data[cfg_key]["image"] = {
            "image_time": "-fail-",
            "gpu_mem_mb": "-fail-",
            "cpu_mem_mb": "-fail-",
            "bench_time_s": "-fail-",
            "errors": errors,
            "test_name": f"image_{cfg_key}",
            "device_setting": device_setting,
            "special_setting": special_setting,
            "env": env_data,
        }


def parse_devices(output: str) -> Dict[str, Dict[str, Any]]:
    """Parse output from llama-cli --list-devices and return device info.

    Returns a dictionary mapping device IDs (e.g. 'ROCm0') to details.
    """
    devices: Dict[str, Dict[str, Any]] = {}
    for line in output.splitlines():
        # Match e.g. "  ROCm0: AMD Radeon RX 7900 XTX (30704 MiB, 30668 MiB free)"
        match = re.search(
            r"^\s*([^:]+):\s*(.*?)\s*\(([\d\.]+)\s*(\w+),\s*([\d\.]+)\s*(\w+)\s+free\)",
            line,
        )
        if match:
            dev_id = match.group(1).strip()
            dev_name = match.group(2).strip()
            total_val = float(match.group(3))
            total_unit = match.group(4)
            free_val = float(match.group(5))
            free_unit = match.group(6)

            # Convert to MB/MiB
            def to_mib(val: float, unit: str) -> float:
                unit_lower = unit.lower()
                if "gib" in unit_lower or "gb" in unit_lower:
                    return val * 1024.0
                if "kib" in unit_lower or "kb" in unit_lower:
                    return val / 1024.0
                if (
                    "b" in unit_lower
                    and "m" not in unit_lower
                    and "g" not in unit_lower
                    and "k" not in unit_lower
                ):
                    return val / (1024.0 * 1024.0)
                return val

            devices[dev_id] = {
                "device_id": dev_id,
                "name": dev_name,
                "total_mem_mib": to_mib(total_val, total_unit),
                "free_mem_mib": to_mib(free_val, free_unit),
            }
    return devices



def build_gpu_registry(mock: bool = False):
    GLOBAL_GPU_REGISTRY.cards.clear()
    
    if mock:
        # Hardcode mock W6800 and iGPU
        GLOBAL_GPU_REGISTRY.cards.append(GPUCard(
            rocm_smi_card="card0",
            name="AMD Radeon RX 7900 XTX",
            gfx_version="gfx1100",
            vram_total_mb=24576.0,
            is_igpu=False,
            rocm_index=0,
            vulkan_index=1
        ))
        GLOBAL_GPU_REGISTRY.cards.append(GPUCard(
            rocm_smi_card="card1",
            name="AMD Radeon Graphics",
            gfx_version="gfx90c",
            vram_total_mb=4096.0,
            is_igpu=True,
            rocm_index=1,
            vulkan_index=0
        ))
        return

    # 1. rocm-smi
    try:
        out = subprocess.check_output(
            ["/opt/rocm/bin/rocm-smi", "--showproductname", "--showmeminfo", "vram", "--json"],
            text=True
        )
        data = json.loads(out)
        for card_key, info in data.items():
            if not card_key.startswith("card"):
                continue
            name = info.get("Card series", "Unknown GPU")
            # wait, rocm-smi doesn't show gfx_version directly. Wait, the user said "gfx1100".
            # We can get gfx_version from rocm_agent_enumerator or from name.
            # For now, let's just parse VRAM
            vram_bytes = info.get("VRAM Total Memory (B)", "0")
            vram_mb = float(vram_bytes) / (1024 * 1024)
            is_igpu = "Graphics" in name or "Renoir" in name
            GLOBAL_GPU_REGISTRY.cards.append(GPUCard(
                rocm_smi_card=card_key,
                name=name,
                gfx_version="unknown",
                vram_total_mb=vram_mb,
                is_igpu=is_igpu,
                rocm_index=None,
                vulkan_index=None
            ))
    except Exception as e:
        print(f"Warning: rocm-smi failed: {e}")

    # 2. llama-cli
    cli_paths = ["llama-cli", "/usr/bin/llama-cli", "/usr/local/bin/llama-cli"]
    cli_out = ""
    for path in cli_paths:
        try:
            cli_out = subprocess.check_output([path, "--list-devices"], text=True, stderr=subprocess.STDOUT)
            break
        except Exception:
            continue
    
    # Parse llama-cli output
    for line in cli_out.splitlines():
        # ROCm0: AMD Radeon RX 7900 XTX (24576 MiB, 24000 MiB free)
        # Vulkan1: AMD Radeon RX 7900 XTX (NAVI31) (24576 MiB)
        match = re.match(r"(ROCm|Vulkan)(\d+):\s+(.*?)\s+\(", line)
        if match:
            backend = match.group(1)
            idx = int(match.group(2))
            name = match.group(3).strip()
            
            # Find matching card in registry by name or VRAM size
            # This is a bit fuzzy, but usually iGPU has "Graphics" or "RENOIR" and dGPU has "XTX" or "PRO"
            for card in GLOBAL_GPU_REGISTRY.cards:
                # Naive matching based on name overlap or if we just have 2 cards, sorting by VRAM
                pass
            

            # Assign ROCm/Vulkan indices based on heuristics since UUID mapping is hard without full ROCm APIs.
            # We know dGPU is 24GB, iGPU is much smaller.
            is_llama_igpu = "Graphics" in name or "RENOIR" in name or "gfx90c" in name
            
            for card in GLOBAL_GPU_REGISTRY.cards:
                if card.is_igpu == is_llama_igpu:
                    if backend == "ROCm":
                        card.rocm_index = idx
                    elif backend == "Vulkan":
                        card.vulkan_index = idx


def get_available_devices(mock: bool = False) -> Dict[str, Dict[str, Any]]:
    """Run llama-cli --list-devices to get available GPUs."""
    build_gpu_registry(mock)
    
    devices = {}
    for card in GLOBAL_GPU_REGISTRY.cards:
        if card.rocm_index is not None:
            key = f"ROCm{card.rocm_index}"
            devices[key] = {
                "device_id": key,
                "name": card.name,
                "total_mem_mib": card.vram_total_mb,
                "free_mem_mib": card.vram_total_mb,
                "gfx_version": card.gfx_version,
            }
        if card.vulkan_index is not None:
            key = f"Vulkan{card.vulkan_index}"
            devices[key] = {
                "device_id": key,
                "name": card.name,
                "total_mem_mib": card.vram_total_mb,
                "free_mem_mib": card.vram_total_mb,
                "gfx_version": card.gfx_version,
            }
    
    # Add dummy BLAS
    devices["BLAS0"] = {
        "device_id": "BLAS0",
        "name": "CPU BLAS",
        "total_mem_mib": 0.0,
        "free_mem_mib": 0.0,
        "gfx_version": "cpu",
    }
    return devices


def warmup_model(url: str, payload: dict, timeout: int = 180) -> bool:
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


def make_non_blocking(stream: Any) -> None:
    """Make a stream non-blocking using fcntl."""
    import fcntl
    import os

    try:
        fd = stream.fileno()
        flags = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
    except Exception:
        pass


def read_stream(stream: Any) -> str:
    """Read all available data from a non-blocking stream."""
    try:
        return stream.read() or ""
    except Exception:
        return ""


def wait_for_port(
    port: int, timeout: int = 90, proc: Optional[subprocess.Popen] = None
) -> bool:
    """Wait for port to accept TCP connections on localhost."""
    import sys

    if proc is not None:
        if proc.stdout is not None:
            make_non_blocking(proc.stdout)
        if proc.stderr is not None:
            make_non_blocking(proc.stderr)

    start_time = time.time()
    while time.time() - start_time < timeout:
        if proc is not None:
            if proc.stdout is not None:
                out = read_stream(proc.stdout)
                if out:
                    sys.stdout.write(out)
                    sys.stdout.flush()
            if proc.stderr is not None:
                err = read_stream(proc.stderr)
                if err:
                    sys.stderr.write(err)
                    sys.stderr.flush()
            if proc.poll() is not None:
                print(f"❌ Error: Process died early with exit code {proc.returncode}")
                return False

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


def start_service(
    script_path: str, env_args: Optional[List[str]] = None
) -> Tuple[subprocess.Popen, Optional[int]]:
    """Start the service transiently using the script's exec action."""
    cmd = [script_path, "exec"]
    if env_args:
        cmd.extend(env_args)
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        close_fds=True,
        cwd=os.path.dirname(script_path),
    )
    return proc, None


def run_benchmark(
    script_path: str,
    args: List[str],
    server_proc: Any = None,
) -> Tuple[str, bool, List[str]]:
    """Execute the service test command with args and return captured stdout, success flag, and error lines.

    If server_proc is provided, checks if the server process dies during benchmark.
    """
    import sys

    cmd = [script_path, "test"] + args
    print(f"Running benchmark command: {' '.join(cmd)}")

    server_output_accumulator = []

    if server_proc is None:
        # If there's no server_proc (e.g. running in mock mode or direct test mode without a managed server)
        # We still open stdout/stderr pipes, read them dynamically, and write to corresponding streams.
        bench_proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.path.dirname(script_path),
        )
        make_non_blocking(bench_proc.stdout)
        make_non_blocking(bench_proc.stderr)

        bench_stdout = []
        while True:
            out = read_stream(bench_proc.stdout)
            err = read_stream(bench_proc.stderr)
            if out:
                sys.stdout.write(out)
                sys.stdout.flush()
                bench_stdout.append(out)
            if err:
                sys.stderr.write(err)
                sys.stderr.flush()
            if bench_proc.poll() is not None:
                break
            time.sleep(0.1)

        # Read remaining
        out = read_stream(bench_proc.stdout)
        err = read_stream(bench_proc.stderr)
        if out:
            sys.stdout.write(out)
            sys.stdout.flush()
            bench_stdout.append(out)
        if err:
            sys.stderr.write(err)
            sys.stderr.flush()

        bench_exit = bench_proc.returncode
        stdout_str = "".join(bench_stdout)
        if bench_exit != 0:
            print(f"Error running benchmark. Exit code: {bench_exit}")
            return stdout_str, False, []
        return stdout_str, True, []

    # Run benchmark asynchronously and poll to check if server dies
    bench_proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=os.path.dirname(script_path),
    )
    make_non_blocking(bench_proc.stdout)
    make_non_blocking(bench_proc.stderr)

    if server_proc is not None:
        if server_proc.stdout is not None:
            make_non_blocking(server_proc.stdout)
        if server_proc.stderr is not None:
            make_non_blocking(server_proc.stderr)

    bench_stdout = []
    success = True
    while True:
        # Check if benchmark completed
        bench_exit = bench_proc.poll()
        # Check if server died
        server_exit = server_proc.poll() if server_proc is not None else None

        # Read and print outputs
        out = read_stream(bench_proc.stdout)
        err = read_stream(bench_proc.stderr)
        if out:
            sys.stdout.write(out)
            sys.stdout.flush()
            bench_stdout.append(out)
        if err:
            sys.stderr.write(err)
            sys.stderr.flush()

        if server_proc is not None:
            if server_proc.stdout is not None:
                s_out = read_stream(server_proc.stdout)
                if s_out:
                    sys.stdout.write(s_out)
                    sys.stdout.flush()
                    server_output_accumulator.append(s_out)
            if server_proc.stderr is not None:
                s_err = read_stream(server_proc.stderr)
                if s_err:
                    sys.stderr.write(s_err)
                    sys.stderr.flush()
                    server_output_accumulator.append(s_err)

        if bench_exit is not None:
            # Benchmark finished
            if bench_exit != 0:
                print(f"Error running benchmark. Exit code: {bench_exit}")
                success = False
            break

        if server_exit is not None:
            print(
                f"❌ Error: Server process died during benchmark with exit code {server_exit}!"
            )
            bench_proc.terminate()
            try:
                bench_proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                bench_proc.kill()
            success = False
            break

        time.sleep(0.1)

    # Read remaining outputs
    out = read_stream(bench_proc.stdout)
    err = read_stream(bench_proc.stderr)
    if out:
        sys.stdout.write(out)
        sys.stdout.flush()
        bench_stdout.append(out)
    if err:
        sys.stderr.write(err)
        sys.stderr.flush()

    if server_proc is not None:
        if server_proc.stdout is not None:
            s_out = read_stream(server_proc.stdout)
            if s_out:
                sys.stdout.write(s_out)
                sys.stdout.flush()
                server_output_accumulator.append(s_out)
        if server_proc.stderr is not None:
            s_err = read_stream(server_proc.stderr)
            if s_err:
                sys.stderr.write(s_err)
                sys.stderr.flush()
                server_output_accumulator.append(s_err)

    stdout_str = "".join(bench_stdout)

    # Extract error lines
    error_lines = []
    if server_proc is not None:
        server_output_str = "".join(server_output_accumulator)
        for line in server_output_str.splitlines():
            if "error" in line.lower():
                error_lines.append(line.strip())

    return stdout_str, success, error_lines


# Regex Parsers


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

    # Partition Phase 0, Phase 2, and Phase 4
    p0_content = ""
    p2_content = ""
    p4_content = ""

    parts_p0 = output.split("--- Phase 0: Warmup ---")
    if len(parts_p0) > 1:
        p0_content = parts_p0[1].split("---")[0]

    parts_p2 = output.split("--- Phase 2: Generation (300-word summary) ---")
    if len(parts_p2) > 1:
        p2_content = parts_p2[1].split("---")[0]

    parts_p4 = output.split("--- Phase 4: Image Description (Vision) ---")
    if len(parts_p4) > 1:
        p4_content = parts_p4[1].split("---")[0]

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

    if p4_content:
        res["chat_image_ttft"] = extract_metric(
            r"Avg TTFT \(Prefill\):\s+([\d\.]+)\s+ms", p4_content
        )
        res["chat_image_gen"] = extract_metric(
            r"Avg Generation Speed:\s+([\d\.]+)\s+tokens", p4_content
        )

    return res


def parse_image_output(output: str) -> Dict[str, float]:
    """Parse image benchmark stats from stdout."""
    res = {}
    res["image_time"] = extract_metric(
        r"Avg Generation Time:\s*([\d\.]+)\s*seconds", output
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


# Mock Outputs for Validation


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

    if mode == "chat":
        return f"""
Running local-chat validation tests...
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

--- Phase 4: Image Description (Vision) ---
  Runs:                 1
  Prompt Tokens:        292
  Avg Completion Tokens: 85.0
  Avg TTFT (Prefill):   {520.12 * fac:.2f} ms
  Avg Prefill Speed:    {561.42 / fac:.2f} tokens/sec
  Avg Generation Speed: {48.12 / fac:.2f} tokens/sec
  Avg Decode Time:      {1.76 * fac:.2f} s
"""
    elif mode == "image":
        return f"""
=== Image Generation Benchmark Results (Cumulative Average) ===
Prompt:            A high-resolution, beautiful photograph...
Steps:             8
CFG Scale:         1.0
Repeats:           1
Avg Generation Time: {2.45 * fac:.2f} seconds
=============================================================
"""
    elif mode == "embedding":
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


# Report Generator


def generate_report(
    data: Dict[str, Dict[str, Dict[str, Any]]],
    hip_devices: Optional[List[str]] = None,
    vulkan_devices: Optional[List[str]] = None,
) -> str:
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

    def format_errors(cfg: str, mode: str) -> str:
        if cfg in data and mode in data[cfg] and "errors" in data[cfg][mode]:
            errors = data[cfg][mode]["errors"]
            if errors:
                lines = [f"- **Errors Count:** {len(errors)}", "- **Top Errors:**"]
                for err in errors[:10]:
                    lines.append(f"  - `{err}`")
                return "\n".join(lines)
        return "- **Errors Count:** 0"

    # Helper to print values safely
    def val(
        cfg: str,
        mode: str,
        key: str,
        fmt: str = ".2f",
        suffix: str = "",
        default: str = "-n.a.-",
    ) -> str:
        if cfg in data and mode in data[cfg] and key in data[cfg][mode]:
            v = data[cfg][mode][key]
            if isinstance(v, str):
                return v
            if v is None:
                return default
            try:
                return f"{v:{fmt}}{suffix}"
            except (ValueError, TypeError):
                return str(v)
        return default

    # Speedup ratio vs Real-time (1 / RTF)
    def speedup(cfg: str, mode: str, rtf_key: str) -> str:
        if cfg in data and mode in data[cfg] and rtf_key in data[cfg][mode]:
            rtf = data[cfg][mode][rtf_key]
            if isinstance(rtf, str):
                return rtf
            if rtf > 0:
                return f"{1.0 / rtf:.1f}x"
        return "-n.a.-"

    def get_test_name(cfg: str, mode: str) -> str:
        if cfg in data and mode in data[cfg] and "test_name" in data[cfg][mode]:
            return str(data[cfg][mode]["test_name"])
        fallback_names = {
            "chat": "chat",
            "embedding": "embedding",
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
                    "LCHAT_DEVICE",
                    "LMBD_DEVICE",
                    "LRR_DEVICE",
                    "LSTT_DEVICE",
                    "LTTS_DEVICE",
                    "LIMG_BACKEND",
                ]:
                    if k in env and env[k]:
                        return env[k]
        # Fallback if not found in data/env
        cfg_lower = cfg.lower()
        if cfg_lower.startswith("hip"):
            parts = cfg.split("-")
            if len(parts) > 1:
                return parts[1]
            return (
                "ROCm0"
                if mode in ("chat", "embedding", "rerank")
                else ("0" if mode == "stt" else "Default")
            )
        elif cfg_lower.startswith("vulkan"):
            parts = cfg.split("-")
            if len(parts) > 1:
                return parts[1]
            return (
                "Vulkan0"
                if mode in ("chat", "embedding", "rerank")
                else ("0" if mode == "stt" else "Default")
            )
        elif cfg_lower.startswith("cpu-hip"):
            parts = cfg.split("-")
            if len(parts) > 2:
                return parts[2]
            return "ROCm0"
        elif cfg_lower.startswith("cpu-vulkan"):
            parts = cfg.split("-")
            if len(parts) > 2:
                return parts[2]
            return "Vulkan1"
        elif cfg_lower == "cpu":
            return (
                "BLAS" if mode in ("chat", "embedding", "rerank") else "Default (CPU)"
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
                for k in [
                    "LCHAT_N_GPU_LAYERS",
                    "LMBD_N_GPU_LAYERS",
                    "LRR_N_GPU_LAYERS",
                ]:
                    if k in env:
                        return f"Layers: {env[k]}"
                if "LSTT_NO_GPU" in env:
                    return "No GPU" if env["LSTT_NO_GPU"] == "true" else "Use GPU"
        if cfg.startswith("cpu-hip") or cfg.startswith("cpu-vulkan"):
            return "mode: hybrid"
        return "None"

    def sort_config_keys(cfg: str) -> Tuple[int, str]:
        cfg_lower = cfg.lower()
        if cfg_lower.startswith("hip"):
            return (0, cfg_lower)
        elif cfg_lower.startswith("vulkan"):
            return (1, cfg_lower)
        elif cfg_lower == "cpu":
            return (2, cfg_lower)
        elif cfg_lower.startswith("cpu-hip"):
            return (3, cfg_lower)
        elif cfg_lower.startswith("cpu-vulkan"):
            return (4, cfg_lower)
        elif cfg_lower.startswith("special"):
            return (5, cfg_lower)
        return (6, cfg_lower)

    import datetime

    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Generate matrix table contents dynamically
    # 1. Chat Table Body
    chat_rows = []
    chat_keys = [cfg for cfg in data.keys() if "chat" in data[cfg]]
    chat_keys.sort(key=sort_config_keys)
    for cfg in chat_keys:
        cfg_label = cfg.upper()
        row = f"| **{cfg_label}** | {get_test_name(cfg, 'chat')} | {get_device_setting(cfg, 'chat')} | {get_special_setting(cfg, 'chat')} | {val(cfg, 'chat', 'chat_avg_ttft', '.2f', ' ms')} | {val(cfg, 'chat', 'chat_avg_prefill', '.2f', ' t/s')} | {val(cfg, 'chat', 'chat_warmup_ttft', '.2f', ' ms')} | {val(cfg, 'chat', 'chat_warmup_gen', '.2f', ' t/s')} | {val(cfg, 'chat', 'chat_avg_gen', '.2f', ' t/s')} | {val(cfg, 'chat', 'chat_image_ttft', '.2f', ' ms')} | {val(cfg, 'chat', 'chat_image_gen', '.2f', ' t/s')} | {val(cfg, 'chat', 'gpu_mem_mb', '.1f', ' MB')} | {val(cfg, 'chat', 'cpu_mem_mb', '.1f', ' MB')} |"
        chat_rows.append(row)
    if not any(cfg.startswith("hip") for cfg in chat_keys):
        chat_rows.append(
            "| **HIP** | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- |"
        )
    if not any(cfg.startswith("vulkan") for cfg in chat_keys):
        chat_rows.append(
            "| **VULKAN** | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- |"
        )
    if not any(cfg == "cpu" for cfg in chat_keys):
        chat_rows.append(
            "| **CPU** | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- |"
        )
    chat_table_body = "\n".join(chat_rows)

    # 2. Embedding Table Body
    embed_rows = []
    embed_keys = [cfg for cfg in data.keys() if "embedding" in data[cfg]]
    embed_keys.sort(key=sort_config_keys)
    for cfg in embed_keys:
        cfg_label = cfg.upper()
        row = f"| **{cfg_label}** | {get_test_name(cfg, 'embedding')} | {get_device_setting(cfg, 'embedding')} | {get_special_setting(cfg, 'embedding')} | {val(cfg, 'embedding', 'embed_throughput', '.2f', ' t/s')} | {val(cfg, 'embedding', 'embed_lat', '.1f', ' ms')} | {val(cfg, 'embedding', 'gpu_mem_mb', '.1f', ' MB')} | {val(cfg, 'embedding', 'cpu_mem_mb', '.1f', ' MB')} |"
        embed_rows.append(row)
    if not any(cfg.startswith("hip") for cfg in embed_keys):
        embed_rows.append(
            "| **HIP** | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- |"
        )
    if not any(cfg.startswith("vulkan") for cfg in embed_keys):
        embed_rows.append(
            "| **VULKAN** | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- |"
        )
    if not any(cfg == "cpu" for cfg in embed_keys):
        embed_rows.append(
            "| **CPU** | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- |"
        )
    embed_table_body = "\n".join(embed_rows)

    # 3. Reranking Table Body
    rerank_rows = []
    rerank_keys = [cfg for cfg in data.keys() if "rerank" in data[cfg]]
    rerank_keys.sort(key=sort_config_keys)
    for cfg in rerank_keys:
        cfg_label = cfg.upper()
        row = f"| **{cfg_label}** | {get_test_name(cfg, 'rerank')} | {get_device_setting(cfg, 'rerank')} | {get_special_setting(cfg, 'rerank')} | {val(cfg, 'rerank', 'rerank_time', '.2f', ' ms')} | {val(cfg, 'rerank', 'rerank_token_speed', '.2f', ' tokens/s')} | {val(cfg, 'rerank', 'rerank_throughput', '.2f', ' docs/s')} | {val(cfg, 'rerank', 'gpu_mem_mb', '.1f', ' MB')} | {val(cfg, 'rerank', 'cpu_mem_mb', '.1f', ' MB')} |"
        rerank_rows.append(row)
    if not any(cfg.startswith("hip") for cfg in rerank_keys):
        rerank_rows.append(
            "| **HIP** | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- |"
        )
    if not any(cfg.startswith("vulkan") for cfg in rerank_keys):
        rerank_rows.append(
            "| **VULKAN** | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- |"
        )
    if not any(cfg == "cpu" for cfg in rerank_keys):
        rerank_rows.append(
            "| **CPU** | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- |"
        )
    rerank_table_body = "\n".join(rerank_rows)

    # 4. Speech-to-Text Table Body
    stt_rows = []
    stt_keys = [cfg for cfg in data.keys() if "stt" in data[cfg]]
    stt_keys.sort(key=sort_config_keys)
    for cfg in stt_keys:
        cfg_label = cfg.upper()
        row = f"| **{cfg_label}** | {get_test_name(cfg, 'stt')} | {get_device_setting(cfg, 'stt')} | {get_special_setting(cfg, 'stt')} | {val(cfg, 'stt', 'stt_time', '.2f', ' s')} | {val(cfg, 'stt', 'stt_rtf', '.4f')} | {speedup(cfg, 'stt', 'stt_rtf')} | {val(cfg, 'stt', 'gpu_mem_mb', '.1f', ' MB')} | {val(cfg, 'stt', 'cpu_mem_mb', '.1f', ' MB')} |"
        stt_rows.append(row)
    if not any(cfg.startswith("hip") for cfg in stt_keys):
        stt_rows.append(
            "| **HIP** | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- |"
        )
    if not any(cfg.startswith("vulkan") for cfg in stt_keys):
        stt_rows.append(
            "| **VULKAN** | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- |"
        )
    if not any(cfg == "cpu" for cfg in stt_keys):
        stt_rows.append(
            "| **CPU** | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- |"
        )
    stt_table_body = "\n".join(stt_rows)

    # 5. Text-to-Speech Table Body
    tts_rows = []
    tts_keys = [cfg for cfg in data.keys() if "tts" in data[cfg]]
    tts_keys.sort(key=sort_config_keys)
    for cfg in tts_keys:
        cfg_label = cfg.upper()
        row = f"| **{cfg_label}** | {get_test_name(cfg, 'tts')} | {get_device_setting(cfg, 'tts')} | {get_special_setting(cfg, 'tts')} | {val(cfg, 'tts', 'tts_time', '.2f', ' s')} | {val(cfg, 'tts', 'tts_rtf', '.4f')} | {val(cfg, 'tts', 'tts_char_speed', '.2f', ' chars/s')} | {val(cfg, 'tts', 'gpu_mem_mb', '.1f', ' MB')} | {val(cfg, 'tts', 'cpu_mem_mb', '.1f', ' MB')} |"
        tts_rows.append(row)
    if not any(cfg.startswith("hip") for cfg in tts_keys):
        tts_rows.append(
            "| **HIP** | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- |"
        )
    if not any(cfg.startswith("vulkan") for cfg in tts_keys):
        tts_rows.append(
            "| **VULKAN** | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- |"
        )
    if not any(cfg == "cpu" for cfg in tts_keys):
        tts_rows.append(
            "| **CPU** | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- |"
        )

    # Dynamic fallback rows for special hybrid configs
    resolved_hip = hip_devices or ["ROCm0"]
    resolved_vulk = vulkan_devices or ["Vulkan0"]
    for dev in resolved_hip:
        key = f"cpu-hip-{dev}"
        if key not in tts_keys:
            tts_rows.append(
                f"| **{key.upper()}** | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- |"
            )
    for dev in resolved_vulk:
        key = f"cpu-vulkan-{dev}"
        if key not in tts_keys:
            tts_rows.append(
                f"| **{key.upper()}** | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- |"
            )
    tts_table_body = "\n".join(tts_rows)

    # 6. Image Generation Table Body
    image_rows = []
    image_keys = [cfg for cfg in data.keys() if "image" in data[cfg]]
    image_keys.sort(key=sort_config_keys)
    for cfg in image_keys:
        cfg_label = cfg.upper()
        row = f"| **{cfg_label}** | {get_test_name(cfg, 'image')} | {get_device_setting(cfg, 'image')} | {get_special_setting(cfg, 'image')} | {val(cfg, 'image', 'image_time', '.2f', ' s')} | {val(cfg, 'image', 'gpu_mem_mb', '.1f', ' MB')} | {val(cfg, 'image', 'cpu_mem_mb', '.1f', ' MB')} |"
        image_rows.append(row)
    if not any(cfg.startswith("hip") for cfg in image_keys):
        image_rows.append(
            "| **HIP** | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- |"
        )
    if not any(cfg.startswith("vulkan") for cfg in image_keys):
        image_rows.append(
            "| **VULKAN** | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- |"
        )
    if not any(cfg == "cpu" for cfg in image_keys):
        image_rows.append(
            "| **CPU** | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- |"
        )
    image_table_body = "\n".join(image_rows)

    report = f"""# LLM Caching Optimization Benchmarks

**Benchmark Run Time:** `{now_str}`

## Local Inference Services Benchmarks

We ran local benchmarks for text embedding, text-to-speech (TTS), speech-to-text (STT), document reranking, and image generation on the AMD Radeon RX 7900 XTX hardware target. All services run inside isolated sandboxed environments.

### 📊 Performance Comparison Matrix

#### Text Chat (`local-chat`)
| Configuration | Test Name | GPU | Device Setting | Special Setting | Avg Chat TTFT | Avg Chat Prefill | Chat TTFT (Warmup) | Chat Gen Speed | Avg Chat Gen | Chat Image TTFT | Chat Image Gen | Chat GPU Mem | Chat CPU Mem |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
{chat_table_body}

#### Text Embedding (`local-embedding`)
| Configuration | Test Name | GPU | Device Setting | Special Setting | Embedding Throughput | Embedding Latency (Avg) | Embedding GPU Mem | Embedding CPU Mem |
|---|---|---|---|---|---|---|---|---|
{embed_table_body}

#### Document Reranking (`local-rerank`)
| Configuration | Test Name | GPU | Device Setting | Special Setting | Avg Reranking Time | Avg Token Speed | Avg Docs Throughput | GPU Mem | CPU Mem |
|---|---|---|---|---|---|---|---|---|---|
{rerank_table_body}

#### Speech-to-Text (STT) (`local-speech-to-text`)
| Configuration | Test Name | GPU | Device Setting | Special Setting | Avg Transcribe Time | Avg Real-Time Factor (RTF) | Speedup vs Real-time | GPU Mem | CPU Mem |
|---|---|---|---|---|---|---|---|---|---|
{stt_table_body}

#### Text-to-Speech (TTS) (`local-text-to-speech`)
| Configuration | Test Name | GPU | Device Setting | Special Setting | Avg Synthesis Time | Avg Real-Time Factor (RTF) | Speed (chars/s) | GPU Mem | CPU Mem |
|---|---|---|---|---|---|---|---|---|---|
{tts_table_body}

#### Image Generation (`local-image`)
| Configuration | Test Name | GPU | Device Setting | Special Setting | Avg Generation Time | GPU Mem | CPU Mem |
|---|---|---|---|---|---|---|
{image_table_body}

---

### ⚙️ Detailed Configuration Reports

"""

    for cfg in sorted(data.keys(), key=sort_config_keys):
        if not data[cfg]:
            continue
        cfg_upper = cfg.upper()
        if cfg.startswith("cpu-hip") or cfg.startswith("cpu-vulkan"):
            cfg_upper = f"SPECIAL ({cfg.upper()})"

        # Check if there is device_details in any service
        device_details_str = ""
        for mode in data[cfg]:
            if "device_details" in data[cfg][mode]:
                details = data[cfg][mode]["device_details"]
                if details and "name" in details:
                    device_details_str = f"- **Device Name**: `{details['name']}` (Total: {details.get('total_mem_mib', 0.0):.0f} MiB, Free: {details.get('free_mem_mib', 0.0):.0f} MiB)\n"
                    break

        report += f"### {cfg_upper} Configuration Details\n\n"
        if device_details_str:
            report += device_details_str + "\n"

        # Chat details
        if "chat" in data[cfg]:
            report += f"""#### Text Chat (`local-chat`)
- **Benchmark Test Name:** `{get_test_name(cfg, "chat")}`
- **Device Setting:** `{get_device_setting(cfg, "chat")}`
- **Special Setting:** `{get_special_setting(cfg, "chat")}`
- **Model:** `qwen3` (`Qwen3.6-35B-A3B-APEX-I-Compact`)
- **Execution Target:** `{cfg_upper}`
- **GPU Memory Used:** {val(cfg, "chat", "gpu_mem_mb", ".1f", " MB")}
- **CPU Memory Used:** {val(cfg, "chat", "cpu_mem_mb", ".1f", " MB")}
- **Benchmark Running Time:** {val(cfg, "chat", "bench_time_s", ".2f", " s")}
- **Active Environment Settings:**
{format_env(cfg, "chat")}
{format_errors(cfg, "chat")}
- **Warmup (Phase 0):**
  - TTFT (Prefill):       {val(cfg, "chat", "chat_warmup_ttft", ".2f", " ms")}
  - Prefill Speed:        {val(cfg, "chat", "chat_warmup_prefill", ".2f", " tokens/sec")}
  - Generation Speed:     {val(cfg, "chat", "chat_warmup_gen", ".2f", " tokens/sec")}
- **Generation (Phase 2):**
  - Avg Completion Tokens: {val(cfg, "chat", "chat_avg_comp", ".1f")}
  - Avg TTFT (Prefill):   {val(cfg, "chat", "chat_avg_ttft", ".2f", " ms")}
  - Avg Prefill Speed:    {val(cfg, "chat", "chat_avg_prefill", ".2f", " tokens/sec")}
  - Avg Generation Speed: {val(cfg, "chat", "chat_avg_gen", ".2f", " tokens/sec")}
  - Avg Decode Time:      {val(cfg, "chat", "chat_avg_decode", ".2f", " s")}
- **Vision Description (Phase 4):**
  - Avg TTFT (Prefill):   {val(cfg, "chat", "chat_image_ttft", ".2f", " ms")}
  - Avg Generation Speed: {val(cfg, "chat", "chat_image_gen", ".2f", " tokens/sec")}

"""

        # Embedding details
        if "embedding" in data[cfg]:
            report += f"""#### Text Embedding (`local-embedding`)
- **Benchmark Test Name:** `{get_test_name(cfg, "embedding")}`
- **Device Setting:** `{get_device_setting(cfg, "embedding")}`
- **Special Setting:** `{get_special_setting(cfg, "embedding")}`
- **Model:** `qwen3-embedding` (`Qwen3-Embedding-0.6B-Q8_0.gguf`)
- **Execution Target:** `{cfg_upper}`
- **GPU Memory Used:** {val(cfg, "embedding", "gpu_mem_mb", ".1f", " MB")}
- **CPU Memory Used:** {val(cfg, "embedding", "cpu_mem_mb", ".1f", " MB")}
- **Benchmark Running Time:** {val(cfg, "embedding", "bench_time_s", ".2f", " s")}
- **Active Environment Settings:**
{format_env(cfg, "embedding")}
{format_errors(cfg, "embedding")}
- **Metrics:**
  - Avg Time/Run:         {val(cfg, "embedding", "embed_time_s", ".2f", " s")}
  - Avg Throughput:       {val(cfg, "embedding", "embed_throughput", ".2f", " tokens/sec")}
  - Avg Chunk Latency:    {val(cfg, "embedding", "embed_lat", ".1f", " ms")}
  - Avg Chunk p50:        {val(cfg, "embedding", "embed_p50", ".1f", " ms")}
  - Avg Chunk p95:        {val(cfg, "embedding", "embed_p95", ".1f", " ms")}

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
{format_errors(cfg, "rerank")}
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
{format_errors(cfg, "stt")}
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
{format_errors(cfg, "tts")}
- **Metrics:**
  - Generated Audio Duration: {val(cfg, "tts", "tts_duration", ".2f", " seconds")}
  - Avg Synthesis Time:   {val(cfg, "tts", "tts_time", ".2f", " seconds")}
  - Avg Real-Time Factor (RTF): {val(cfg, "tts", "tts_rtf", ".4f")}
  - Avg Speed:            {val(cfg, "tts", "tts_char_speed", ".2f", " chars/sec")}

"""

        # Image details
        if "image" in data[cfg]:
            report += f"""#### Image Generation (`local-image`)
- **Benchmark Test Name:** `{get_test_name(cfg, "image")}`
- **Device Setting:** `{get_device_setting(cfg, "image")}`
- **Special Setting:** `{get_special_setting(cfg, "image")}`
- **Model:** `z_image_turbo-Q8_0` (`z_image_turbo-Q8_0.gguf`)
- **Execution Target:** `{cfg_upper}`
- **GPU Memory Used:** {val(cfg, "image", "gpu_mem_mb", ".1f", " MB")}
- **CPU Memory Used:** {val(cfg, "image", "cpu_mem_mb", ".1f", " MB")}
- **Benchmark Running Time:** {val(cfg, "image", "bench_time_s", ".2f", " s")}
- **Active Environment Settings:**
{format_env(cfg, "image")}
{format_errors(cfg, "image")}
- **Metrics:**
  - Avg Generation Time:  {val(cfg, "image", "image_time", ".2f", " seconds")}

"""

    return report


# Main Execution Loop


def main() -> None:
    gpu_mem_mb: Union[float, str] = 0.0
    cpu_mem_mb: Union[float, str] = 0.0
    parser = argparse.ArgumentParser(
        description="Run local inference service benchmarks across different hardware acceleration backends."
    )
    import sys

    parser.add_argument(
        "--configs",
        type=str,
        default="hip,vulkan,cpu,special",
        help="Comma-separated list of hardware configurations to test, or 'running' to test already running services (default: hip,vulkan,cpu,special)",
    )
    parser.add_argument(
        "--services",
        type=str,
        default="chat,embedding,rerank,stt,tts,image",
        help="Comma-separated list of services to test, or 'all' to test all services (default: chat,embedding,rerank,stt,tts,image)",
    )
    parser.add_argument(
        "--hip-devices",
        type=str,
        default="ROCm0",
        help="Comma-separated list of HIP/ROCm devices or 'all' to test (default: ROCm0)",
    )
    parser.add_argument(
        "--vulkan-devices",
        type=str,
        default="Vulkan0",
        help="Comma-separated list of Vulkan devices or 'all' to test (default: Vulkan0)",
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Simulate execution and parsing (dry-run/mocking mode for systemd-less environments)",
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Do not load existing benchmark cache, useful for clean runs.",
    )
    parser.add_argument(
        "--report",
        type=str,
        default=os.path.join(REPO_ROOT, "assistants", "local-benchmark.md"),
        help="Path to write the output markdown report (default: assistants/local-benchmark.md)",
    )
    parser.add_argument(
        "--data",
        type=str,
        default=os.path.join(REPO_ROOT, "assistants", "local-benchmark.json"),
        help="Path to the JSON database/cache file (default: assistants/local-benchmark.json)",
    )

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    target_configs = [c.strip().lower() for c in args.configs.split(",")]
    if args.services.lower() == "all":
        target_services = ["chat", "embedding", "rerank", "stt", "tts", "image"]
    else:
        target_services = [s.strip().lower() for s in args.services.split(",")]

    if not args.mock:
        missing_envs = []
        for sname in target_services:
            if sname in SERVICES:
                srv = SERVICES[sname]
                env_file = srv["env_file"]
                if not os.path.exists(env_file) or os.path.getsize(env_file) == 0:
                    missing_envs.append((sname, env_file, srv["script"]))
                else:
                    with open(env_file, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                    non_comments = [
                        line
                        for line in content.splitlines()
                        if line.strip() and not line.strip().startswith("#")
                    ]
                    if not non_comments:
                        missing_envs.append((sname, env_file, srv["script"]))
        if missing_envs:
            print("❌ Error: Missing or empty environment configuration files:")
            for sname, env_file, script in missing_envs:
                print(
                    f"  - {sname}: {env_file} is missing or has no active configurations."
                )
                script_name = os.path.basename(script)
                print(
                    f"    Please install it first: `./assistants/{script_name} install --no-start --new-config`"
                )
            sys.exit(1)

    available_devices = get_available_devices(args.mock)

    # Resolve "all" for hip-devices
    if args.hip_devices.lower() == "all":
        hip_devs = [
            dev_id for dev_id in available_devices if dev_id.lower().startswith("rocm")
        ]
        if not hip_devs:
            hip_devs = ["ROCm0"]
        hip_devices_resolved = hip_devs
    else:
        hip_devices_resolved = [
            d.strip() for d in args.hip_devices.split(",") if d.strip()
        ]

    # Resolve "all" for vulkan-devices
    if args.vulkan_devices.lower() == "all":
        vulk_devs = [
            dev_id
            for dev_id in available_devices
            if dev_id.lower().startswith("vulkan")
        ]
        if not vulk_devs:
            vulk_devs = ["Vulkan0"]
        vulkan_devices_resolved = vulk_devs
    else:
        vulkan_devices_resolved = [
            d.strip() for d in args.vulkan_devices.split(",") if d.strip()
        ]

    # Construct run configurations: List of (cfg_name, device_id)
    run_configs: List[Tuple[str, Any]] = []
    for cfg in target_configs:
        if cfg == "hip":
            for dev in hip_devices_resolved:
                gpu = GLOBAL_GPU_REGISTRY.get_by_device_string(dev)
                if gpu and gpu.is_igpu:
                    print(f"Skipping HIP test for {dev} ({gpu.name}) as it is an unsupported iGPU.")
                    continue
                run_configs.append((cfg, dev))
        elif cfg == "vulkan":
            for dev in vulkan_devices_resolved:
                run_configs.append((cfg, dev))
        else:
            run_configs.append((cfg, None))

    print("==================================================")
    print("🚀 Local Inference Service Benchmark Suite")
    print("==================================================")
    print(f"Configs to test:  {', '.join(target_configs)}")
    print(f"Services to test: {', '.join(target_services)}")
    print(f"Output report:    {args.report}")
    print(f"JSON Cache:       {args.data}")
    if args.mock:
        print("💡 Running in MOCK mode (simulated runs)")
    print("==================================================\n")

    # Compute set of tests that we will execute on this test run (incremental logic)
    will_execute = set()
    for run_cfg, dev in run_configs:
        cache_key = f"{run_cfg}-{dev}" if dev else run_cfg

        # Determine TTS modes to test for this configuration to add them to will_execute
        if "tts" in target_services:
            if run_cfg == "special":
                for dev_id in hip_devices_resolved:
                    will_execute.add((f"cpu-hip-{dev_id}", "tts"))
                for dev_id in vulkan_devices_resolved:
                    will_execute.add((f"cpu-vulkan-{dev_id}", "tts"))
                if not hip_devices_resolved and not vulkan_devices_resolved:
                    will_execute.add(("cpu-hip-ROCm0", "tts"))
            else:
                will_execute.add((cache_key, "tts"))

        for sname in target_services:
            if sname == "tts":
                continue
            if sname == "chat" and run_cfg == "special":
                continue
            if sname == "embedding" and run_cfg == "special":
                continue
            if sname == "rerank" and run_cfg == "special":
                continue
            if sname == "stt" and run_cfg == "special":
                continue
            if sname == "image" and run_cfg == "special":
                continue
            will_execute.add((cache_key, sname))

    cache_file = args.data
    old_data: Dict[str, Dict[str, Dict[str, Any]]] = {}

    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                old_data = json.load(f)
            print(f"Loaded existing benchmark state from: {cache_file}")
        except Exception as e:
            print(f"Warning: Failed to load benchmark cache: {e}")

    # Use old data only if not executed test on this test run
    benchmark_data: Dict[str, Dict[str, Dict[str, Any]]] = {}
    for cfg in old_data:
        for sname in old_data[cfg]:
            if (cfg, sname) not in will_execute:
                if cfg not in benchmark_data:
                    benchmark_data[cfg] = {}
                benchmark_data[cfg][sname] = old_data[cfg][sname]

    # Pre-test Warmup Loop for 'running' configuration
    if "running" in target_configs and not args.mock:
        print("\n==================================================")
        print("🔥 Pre-test Warmup for Running Services")
        print("==================================================")
        for sname in target_services:
            if sname in SERVICES:
                srv = SERVICES[sname]
                script_path = srv["script"]
                print(
                    f"Warming up service '{sname}' via: {os.path.basename(script_path)} test..."
                )
                try:
                    # Run quick test command to warm up models (e.g. local-chat.sh test)
                    subprocess.run(
                        [script_path, "test"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        timeout=180,
                    )
                except Exception as e:
                    print(f"⚠️ Warning warming up '{sname}': {e}")
        print("==================================================\n")

    for run_cfg, dev in run_configs:
        cache_key = f"{run_cfg}-{dev}" if dev else run_cfg
        print(f"\n--- Testing Configuration: {cache_key.upper()} ---")
        if cache_key not in benchmark_data:
            benchmark_data[cache_key] = {}

        # ---------------------------------------------------------
        # 1. Chat Service
        # ---------------------------------------------------------
        if "chat" in target_services:
            srv = SERVICES["chat"]
            if run_cfg == "special":
                print("Skipping Chat for Special configuration.")
            else:
                if run_cfg != "running":
                    print(f"Preparing environment file: {srv['env_file']}")
                proc = None
                master_fd = None
                baseline_vram = 0.0

                # Determine configuration settings for current config
                if run_cfg == "running":
                    llm_device = "running on host"
                    fraction = 1.0
                    llm_n_ctx = 240000
                else:
                    device_map = {
                        "hip": dev if dev else "ROCm0",
                        "vulkan": dev if dev else "Vulkan0",
                        "cpu": "",
                    }
                    llm_device = device_map.get(run_cfg, run_cfg)

                    # Determine context scaling fraction and context size
                    fraction = 1.0
                    if run_cfg == "cpu":
                        fraction = 0.05
                    elif dev and "1" in dev:
                        fraction = 0.20
                    llm_n_ctx = int(240000 * fraction)

                if not args.mock:
                    if run_cfg == "running":
                        baseline_vram = 0.0
                        updates = {}
                        is_up = False
                        try:
                            with socket.create_connection(
                                ("127.0.0.1", srv["port"]), timeout=1.0
                            ):
                                is_up = True
                        except Exception:
                            pass
                        if not is_up:
                            print(
                                f"Error: llama-server is not running on port {srv['port']}."
                            )
                            set_service_fail_metrics(
                                benchmark_data,
                                cache_key,
                                "chat",
                                "running on host",
                                "unknown",
                                srv["env_file"],
                                ["Error: service is not running on port"],
                                {},
                            )
                            continue
                        proc = None
                        master_fd = None
                    else:
                        baseline_vram = get_gpu_memory_mb(llm_device)

                        updates = {
                            "LCHAT_DEVICE": llm_device,
                            "LCHAT_N_GPU_LAYERS": 0 if run_cfg == "cpu" else 999,
                            "LCHAT_N_CTX": llm_n_ctx,
                            "LCHAT_SERVE_EMBEDDINGS": "false",
                        }
                        hip_vis, cuda_vis = get_visible_devices_env(
                            run_cfg, llm_device, hip_devices_resolved
                        )
                        updates["HIP_VISIBLE_DEVICES"] = hip_vis
                        updates["CUDA_VISIBLE_DEVICES"] = cuda_vis

                        # Build environment arguments
                        env_args = []
                        for k, v in updates.items():
                            env_args.extend(["--env", f"{k}={v}"])

                        # Start service
                        proc, master_fd = start_service(srv["script"], env_args)

                        # Wait for server readiness
                        print(f"Waiting for llama-server on port {srv['port']}...")
                        if not wait_for_port(srv["port"], proc=proc):
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
                            set_service_fail_metrics(
                                benchmark_data,
                                cache_key,
                                "chat",
                                llm_device if llm_device else "Default",
                                f"Layers: {0 if run_cfg == 'cpu' else 999}"
                                + (
                                    f" (Context: {fraction * 100:.0f}%)"
                                    if fraction < 1.0
                                    else ""
                                ),
                                srv["env_file"],
                                [
                                    "Error: llama-server failed to start or port timed out"
                                ],
                                updates,
                            )
                            continue
                else:
                    proc = None

                # Run benchmarks
                print("Running LLM Chat benchmark")
                if not args.mock:
                    if run_cfg != "running":
                        print("Warming up chat model (qwen3)...")
                        if not warmup_model(
                            f"http://127.0.0.1:{srv['port']}/v1/chat/completions",
                            {
                                "model": "qwen3",
                                "messages": [{"role": "user", "content": "ping"}],
                                "max_tokens": 1,
                            },
                        ):
                            print(
                                "⚠️ Warning: Model warmup timed out. Benchmark might fail."
                            )
                    test_args = [
                        "--benchmark",
                        "--skip-prefill",
                        "--skip-distractor",
                        "--repeat",
                        "1",
                        "--only-chat",
                        "--fraction-context",
                        str(fraction),
                    ]
                    start_time = time.time()
                    bench_start_time_str = datetime.datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                    stdout, success, error_lines = run_benchmark(
                        srv["script"], test_args, server_proc=proc
                    )
                    if not success:
                        print(
                            f"⚠️ Warning: Benchmark command for chat on config '{cache_key}' failed."
                        )
                        if run_cfg == "running":
                            journal_errors = get_journal_errors(
                                "local-chat", bench_start_time_str
                            )
                            error_lines.extend(journal_errors)
                        set_service_fail_metrics(
                            benchmark_data,
                            cache_key,
                            "chat",
                            "running on host"
                            if run_cfg == "running"
                            else (llm_device if llm_device else "Default"),
                            "unknown"
                            if run_cfg == "running"
                            else (
                                f"Layers: {0 if run_cfg == 'cpu' else 999}"
                                + (
                                    f" (Context: {fraction * 100:.0f}%)"
                                    if fraction < 1.0
                                    else ""
                                )
                            ),
                            srv["env_file"],
                            error_lines,
                            updates,
                        )
                    else:
                        elapsed_time = time.time() - start_time
                        benchmark_data[cache_key]["chat"] = parse_chat_output(stdout)
                        benchmark_data[cache_key]["chat"]["bench_time_s"] = elapsed_time
                        if run_cfg == "running":
                            journal_errors = get_journal_errors(
                                "local-chat", bench_start_time_str
                            )
                            error_lines.extend(journal_errors)
                        benchmark_data[cache_key]["chat"]["errors"] = error_lines

                        # Measure VRAM and RAM right before stopping
                        if run_cfg == "running":
                            gpu_mem_mb = "-n.a.-"
                            cpu_mem_mb = "-n.a.-"
                        else:
                            post_run_vram = get_gpu_memory_mb(llm_device)
                            gpu_mem_mb = max(0.0, post_run_vram - baseline_vram)
                            cpu_mem_mb = get_process_rss_mem_mb(srv["proc_pattern"])

                        benchmark_data[cache_key]["chat"]["gpu_mem_mb"] = gpu_mem_mb
                        benchmark_data[cache_key]["chat"]["cpu_mem_mb"] = cpu_mem_mb
                        benchmark_data[cache_key]["chat"]["test_name"] = (
                            f"chat_{cache_key}"
                        )
                        benchmark_data[cache_key]["chat"]["device_setting"] = (
                            "running on host"
                            if run_cfg == "running"
                            else (llm_device if llm_device else "Default")
                        )
                        if run_cfg == "running":
                            benchmark_data[cache_key]["chat"]["special_setting"] = (
                                "unknown"
                            )
                        else:
                            layers = 999 if run_cfg != "cpu" else 0
                            special_setting = f"Layers: {layers}"
                            if fraction < 1.0:
                                special_setting += f" (Context: {fraction * 100:.0f}%)"
                            benchmark_data[cache_key]["chat"]["special_setting"] = (
                                special_setting
                            )
                        env_dict = read_env_file(srv["env_file"])
                        env_dict.update(updates)
                        benchmark_data[cache_key]["chat"]["env"] = env_dict
                        if run_cfg != "running" and llm_device in available_devices:
                            benchmark_data[cache_key]["chat"]["device_details"] = (
                                available_devices[llm_device]
                            )
                else:
                    stdout = get_mock_output("chat", run_cfg)
                    benchmark_data[cache_key]["chat"] = parse_chat_output(stdout)
                    # Mock simulated configuration errors for demonstration
                    if run_cfg == "running":
                        benchmark_data[cache_key]["chat"]["errors"] = []
                        benchmark_data[cache_key]["chat"]["gpu_mem_mb"] = "-n.a.-"
                        benchmark_data[cache_key]["chat"]["cpu_mem_mb"] = "-n.a.-"
                        benchmark_data[cache_key]["chat"]["device_setting"] = (
                            "running on host"
                        )
                        benchmark_data[cache_key]["chat"]["special_setting"] = "unknown"
                    else:
                        benchmark_data[cache_key]["chat"]["errors"] = (
                            [
                                "error: simulated configuration mismatch",
                                "error: mock error line 2",
                            ]
                            if run_cfg == "cpu"
                            else []
                        )
                        benchmark_data[cache_key]["chat"]["gpu_mem_mb"] = (
                            get_mock_gpu_mem("chat", run_cfg)
                        )
                        benchmark_data[cache_key]["chat"]["cpu_mem_mb"] = (
                            get_mock_cpu_mem("chat", run_cfg)
                        )
                        benchmark_data[cache_key]["chat"]["device_setting"] = (
                            dev
                            if dev
                            else (
                                "ROCm0"
                                if run_cfg == "hip"
                                else ("Vulkan0" if run_cfg == "vulkan" else "Default")
                            )
                        )
                        layers = 999 if run_cfg != "cpu" else 0
                        special_setting = f"Layers: {layers}"
                        if fraction < 1.0:
                            special_setting += f" (Context: {fraction * 100:.0f}%)"
                        benchmark_data[cache_key]["chat"]["special_setting"] = (
                            special_setting
                        )

                    benchmark_data[cache_key]["chat"]["bench_time_s"] = 15.4
                    benchmark_data[cache_key]["chat"]["test_name"] = f"chat_{cache_key}"

                    if run_cfg == "running":
                        mock_updates = {}
                    else:
                        mock_updates = {
                            "LCHAT_DEVICE": dev
                            if dev
                            else (
                                "ROCm0"
                                if run_cfg == "hip"
                                else ("Vulkan0" if run_cfg == "vulkan" else "")
                            ),
                            "LCHAT_N_GPU_LAYERS": "999" if run_cfg != "cpu" else "0",
                            "LCHAT_N_CTX": str(llm_n_ctx),
                            "LCHAT_SERVE_EMBEDDINGS": "false",
                        }
                    try:
                        env_dict = read_env_file(srv["env_file"])
                    except Exception:
                        env_dict = {}
                    env_dict.update(mock_updates)
                    benchmark_data[cache_key]["chat"]["env"] = env_dict

                    if run_cfg != "running":
                        llm_device = (
                            dev
                            if dev
                            else (
                                "ROCm0"
                                if run_cfg == "hip"
                                else ("Vulkan0" if run_cfg == "vulkan" else "")
                            )
                        )
                        dev_details = available_devices.get(llm_device, {})
                        if not dev_details:
                            dev_details = {
                                "device_id": llm_device,
                                "name": "AMD Radeon RX 7900 XTX"
                                if "0" in llm_device
                                else "AMD Radeon Graphics",
                                "total_mem_mib": 24576.0
                                if "0" in llm_device
                                else 56261.0,
                                "free_mem_mib": 24000.0
                                if "0" in llm_device
                                else 92380.0,
                            }
                        benchmark_data[cache_key]["chat"]["device_details"] = (
                            dev_details
                        )

                # Stop service
                if not args.mock and run_cfg != "running":
                    stop_service(
                        "chat",
                        srv["port"],
                        srv["proc_pattern"],
                        proc,
                        master_fd,
                    )

        # ---------------------------------------------------------
        # 1.5 Embedding Service
        if "embedding" in target_services:
            srv = SERVICES["embedding"]
            if run_cfg == "special":
                print("Skipping Embedding for Special configuration.")
            else:
                if run_cfg != "running":
                    print(f"Preparing environment file: {srv['env_file']}")
                proc = None
                master_fd = None
                baseline_vram = 0.0

                # Determine configuration settings for current config
                if run_cfg == "running":
                    embed_device = "running on host"
                else:
                    device_map = {
                        "hip": dev if dev else "ROCm0",
                        "vulkan": dev if dev else "Vulkan0",
                        "cpu": "BLAS",
                    }
                    embed_device = device_map.get(run_cfg, run_cfg)

                if not args.mock:
                    if run_cfg == "running":
                        baseline_vram = 0.0
                        updates = {}
                        is_up = False
                        try:
                            with socket.create_connection(
                                ("127.0.0.1", srv["port"]), timeout=1.0
                            ):
                                is_up = True
                        except Exception:
                            pass
                        if not is_up:
                            print(
                                f"Error: llama-server is not running on port {srv['port']}."
                            )
                            set_service_fail_metrics(
                                benchmark_data,
                                cache_key,
                                "embedding",
                                "running on host",
                                "unknown",
                                srv["env_file"],
                                ["Error: service is not running on port"],
                                {},
                            )
                            continue
                        proc = None
                        master_fd = None
                    else:
                        baseline_vram = get_gpu_memory_mb(embed_device)

                        updates = {
                            "LMBD_DEVICE": embed_device,
                            "LMBD_N_GPU_LAYERS": 0 if run_cfg == "cpu" else 999,
                        }
                        hip_vis, cuda_vis = get_visible_devices_env(
                            run_cfg, embed_device, hip_devices_resolved
                        )
                        updates["HIP_VISIBLE_DEVICES"] = hip_vis
                        updates["CUDA_VISIBLE_DEVICES"] = cuda_vis

                        if dev and "1" in dev:
                            # Limit context size to 4096 on integrated GPUs to prevent out-of-memory buffer errors
                            updates["LMBD_N_CTX"] = 4096
                        else:
                            updates["LMBD_N_CTX"] = 8192

                        # Build environment arguments
                        env_args = []
                        for k, v in updates.items():
                            env_args.extend(["--env", f"{k}={v}"])

                        # Start service
                        proc, master_fd = start_service(srv["script"], env_args)

                        # Wait for server readiness
                        print(f"Waiting for llama-server on port {srv['port']}...")
                        if not wait_for_port(srv["port"], proc=proc):
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
                            set_service_fail_metrics(
                                benchmark_data,
                                cache_key,
                                "embedding",
                                embed_device if embed_device else "Default",
                                f"Layers: {0 if run_cfg == 'cpu' else 999}",
                                srv["env_file"],
                                [
                                    "Error: llama-server failed to start or port timed out"
                                ],
                                updates,
                            )
                            continue
                else:
                    proc = None

                # Run benchmarks
                print("Running LLM Embedding benchmark")
                if not args.mock:
                    if run_cfg != "running":
                        print("Warming up embedding model (qwen3-embedding)...")
                        if not warmup_model(
                            f"http://127.0.0.1:{srv['port']}/v1/embeddings",
                            {
                                "model": "qwen3-embedding",
                                "input": "ping",
                            },
                        ):
                            print(
                                "⚠️ Warning: Model warmup timed out. Benchmark might fail."
                            )
                    test_args = [
                        "--benchmark",
                        "--repeat",
                        "1",
                    ]
                    if run_cfg == "cpu":
                        test_args.extend(["--fraction-chunks", "0.1"])
                    start_time = time.time()
                    bench_start_time_str = datetime.datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                    stdout, success, error_lines = run_benchmark(
                        srv["script"], test_args, server_proc=proc
                    )
                    if not success:
                        print(
                            f"⚠️ Warning: Benchmark command for embedding on config '{cache_key}' failed."
                        )
                        if run_cfg == "running":
                            journal_errors = get_journal_errors(
                                "local-embedding", bench_start_time_str
                            )
                            error_lines.extend(journal_errors)
                        set_service_fail_metrics(
                            benchmark_data,
                            cache_key,
                            "embedding",
                            "running on host"
                            if run_cfg == "running"
                            else (embed_device if embed_device else "Default"),
                            "unknown"
                            if run_cfg == "running"
                            else f"Layers: {0 if run_cfg == 'cpu' else 999}",
                            srv["env_file"],
                            error_lines,
                            updates,
                        )
                    else:
                        elapsed_time = time.time() - start_time
                        benchmark_data[cache_key]["embedding"] = parse_embed_output(
                            stdout
                        )
                        benchmark_data[cache_key]["embedding"]["bench_time_s"] = (
                            elapsed_time
                        )
                        if run_cfg == "running":
                            journal_errors = get_journal_errors(
                                "local-embedding", bench_start_time_str
                            )
                            error_lines.extend(journal_errors)
                        benchmark_data[cache_key]["embedding"]["errors"] = error_lines

                        # Measure VRAM and RAM right before stopping
                        if run_cfg == "running":
                            gpu_mem_mb = "-n.a.-"
                            cpu_mem_mb = "-n.a.-"
                        else:
                            post_run_vram = get_gpu_memory_mb(embed_device)
                            gpu_mem_mb = max(0.0, post_run_vram - baseline_vram)
                            cpu_mem_mb = get_process_rss_mem_mb(srv["proc_pattern"])

                        benchmark_data[cache_key]["embedding"]["gpu_mem_mb"] = (
                            gpu_mem_mb
                        )
                        benchmark_data[cache_key]["embedding"]["cpu_mem_mb"] = (
                            cpu_mem_mb
                        )
                        benchmark_data[cache_key]["embedding"]["test_name"] = (
                            f"embedding_{cache_key}"
                        )
                        benchmark_data[cache_key]["embedding"]["device_setting"] = (
                            "running on host"
                            if run_cfg == "running"
                            else (embed_device if embed_device else "Default")
                        )
                        benchmark_data[cache_key]["embedding"]["special_setting"] = (
                            "unknown"
                            if run_cfg == "running"
                            else f"Layers: {999 if run_cfg != 'cpu' else 0}"
                        )
                        env_dict = read_env_file(srv["env_file"])
                        env_dict.update(updates)
                        benchmark_data[cache_key]["embedding"]["env"] = env_dict
                        if run_cfg != "running" and embed_device in available_devices:
                            benchmark_data[cache_key]["embedding"]["device_details"] = (
                                available_devices[embed_device]
                            )
                else:
                    stdout = get_mock_output("embedding", run_cfg)
                    benchmark_data[cache_key]["embedding"] = parse_embed_output(stdout)
                    benchmark_data[cache_key]["embedding"]["errors"] = []

                    if run_cfg == "running":
                        benchmark_data[cache_key]["embedding"]["gpu_mem_mb"] = "-n.a.-"
                        benchmark_data[cache_key]["embedding"]["cpu_mem_mb"] = "-n.a.-"
                        benchmark_data[cache_key]["embedding"]["device_setting"] = (
                            "running on host"
                        )
                        benchmark_data[cache_key]["embedding"]["special_setting"] = (
                            "unknown"
                        )
                    else:
                        benchmark_data[cache_key]["embedding"]["gpu_mem_mb"] = (
                            get_mock_gpu_mem("embedding", run_cfg)
                        )
                        benchmark_data[cache_key]["embedding"]["cpu_mem_mb"] = (
                            get_mock_cpu_mem("embedding", run_cfg)
                        )
                        benchmark_data[cache_key]["embedding"]["device_setting"] = (
                            dev
                            if dev
                            else (
                                "ROCm0"
                                if run_cfg == "hip"
                                else (
                                    "Vulkan0"
                                    if run_cfg == "vulkan"
                                    else ("BLAS" if run_cfg == "cpu" else "Default")
                                )
                            )
                        )
                        benchmark_data[cache_key]["embedding"]["special_setting"] = (
                            f"Layers: {999 if run_cfg != 'cpu' else 0}"
                        )

                    benchmark_data[cache_key]["embedding"]["bench_time_s"] = 10.2
                    benchmark_data[cache_key]["embedding"]["test_name"] = (
                        f"embedding_{cache_key}"
                    )

                    if run_cfg == "running":
                        mock_updates = {}
                    else:
                        mock_updates = {
                            "LMBD_DEVICE": dev
                            if dev
                            else (
                                "ROCm0"
                                if run_cfg == "hip"
                                else ("Vulkan0" if run_cfg == "vulkan" else "")
                            ),
                            "LMBD_N_GPU_LAYERS": "999" if run_cfg != "cpu" else "0",
                            "LMBD_N_CTX": "4096" if (dev and "1" in dev) else "8192",
                        }
                    try:
                        env_dict = read_env_file(srv["env_file"])
                    except Exception:
                        env_dict = {}
                    env_dict.update(mock_updates)
                    benchmark_data[cache_key]["embedding"]["env"] = env_dict

                    if run_cfg != "running":
                        embed_device = (
                            dev
                            if dev
                            else (
                                "ROCm0"
                                if run_cfg == "hip"
                                else ("Vulkan0" if run_cfg == "vulkan" else "")
                            )
                        )
                        dev_details = available_devices.get(embed_device, {})
                        if not dev_details:
                            dev_details = {
                                "device_id": embed_device,
                                "name": "AMD Radeon RX 7900 XTX"
                                if "0" in embed_device
                                else "AMD Radeon Graphics",
                                "total_mem_mib": 24576.0
                                if "0" in embed_device
                                else 56261.0,
                                "free_mem_mib": 24000.0
                                if "0" in embed_device
                                else 92380.0,
                            }
                        benchmark_data[cache_key]["embedding"]["device_details"] = (
                            dev_details
                        )

                # Stop service
                if not args.mock and run_cfg != "running":
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
            if run_cfg == "special":
                print("Skipping Reranker for Special configuration.")
            else:
                if run_cfg != "running":
                    print(f"Preparing environment file: {srv['env_file']}")
                proc = None
                master_fd = None
                baseline_vram = 0.0

                # Determine configuration settings for current config
                if run_cfg == "running":
                    lrr_device = "running on host"
                else:
                    device_map = {
                        "hip": dev if dev else "ROCm0",
                        "vulkan": dev if dev else "Vulkan0",
                        "cpu": "BLAS",
                    }
                    lrr_device = device_map.get(run_cfg, run_cfg)

                if not args.mock:
                    if run_cfg == "running":
                        baseline_vram = 0.0
                        updates = {}
                        is_up = False
                        try:
                            with socket.create_connection(
                                ("127.0.0.1", srv["port"]), timeout=1.0
                            ):
                                is_up = True
                        except Exception:
                            pass
                        if not is_up:
                            print(
                                f"Error: reranker is not running on port {srv['port']}."
                            )
                            set_service_fail_metrics(
                                benchmark_data,
                                cache_key,
                                "rerank",
                                "running on host",
                                "unknown",
                                srv["env_file"],
                                ["Error: service is not running on port"],
                                {},
                            )
                            continue
                        proc = None
                        master_fd = None
                    else:
                        baseline_vram = get_gpu_memory_mb(lrr_device)
                        updates = {
                            "LRR_DEVICE": lrr_device,
                            "LRR_N_GPU_LAYERS": 0 if run_cfg == "cpu" else 99,
                        }
                        hip_vis, cuda_vis = get_visible_devices_env(
                            run_cfg, lrr_device, hip_devices_resolved
                        )
                        updates["HIP_VISIBLE_DEVICES"] = hip_vis
                        updates["CUDA_VISIBLE_DEVICES"] = cuda_vis

                        # Build environment arguments
                        env_args = []
                        for k, v in updates.items():
                            env_args.extend(["--env", f"{k}={v}"])

                        proc, master_fd = start_service(srv["script"], env_args)
                        # Wait for server readiness
                        print(f"Waiting for reranker on port {srv['port']}...")
                        if not wait_for_port(srv["port"], proc=proc):
                            print(
                                f"Error: reranker failed to start on port {srv['port']}."
                            )
                            stop_service(
                                "rerank",
                                srv["port"],
                                srv["proc_pattern"],
                                proc,
                                master_fd,
                            )
                            set_service_fail_metrics(
                                benchmark_data,
                                cache_key,
                                "rerank",
                                lrr_device if lrr_device else "Default",
                                f"Layers: {0 if run_cfg == 'cpu' else 99}",
                                srv["env_file"],
                                ["Error: reranker failed to start or port timed out"],
                                updates,
                            )
                            continue
                else:
                    proc = None

                print("Running reranker benchmark...")
                if not args.mock:
                    if run_cfg != "running":
                        print("Warming up reranker model (qwen3-reranker)...")
                        if not warmup_model(
                            f"http://127.0.0.1:{srv['port']}/v1/rerank",
                            {
                                "model": "qwen3-reranker",
                                "query": "ping",
                                "documents": ["ping"],
                            },
                        ):
                            print(
                                "⚠️ Warning: Model warmup timed out. Benchmark might fail."
                            )
                    start_time = time.time()
                    bench_start_time_str = datetime.datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                    stdout, success, error_lines = run_benchmark(
                        srv["script"],
                        ["--benchmark", "--repeat", "1", "--format", "json"],
                        server_proc=proc,
                    )
                    if not success:
                        print(
                            f"⚠️ Warning: Benchmark command for reranker on config '{cache_key}' failed."
                        )
                        if run_cfg == "running":
                            journal_errors = get_journal_errors(
                                "local-rerank", bench_start_time_str
                            )
                            error_lines.extend(journal_errors)
                        set_service_fail_metrics(
                            benchmark_data,
                            cache_key,
                            "rerank",
                            "running on host"
                            if run_cfg == "running"
                            else (lrr_device if lrr_device else "Default"),
                            "unknown"
                            if run_cfg == "running"
                            else f"Layers: {0 if run_cfg == 'cpu' else 99}",
                            srv["env_file"],
                            error_lines,
                            updates,
                        )
                    else:
                        elapsed_time = time.time() - start_time
                        benchmark_data[cache_key]["rerank"] = parse_rerank_output(
                            stdout
                        )
                        benchmark_data[cache_key]["rerank"]["bench_time_s"] = (
                            elapsed_time
                        )
                        if run_cfg == "running":
                            journal_errors = get_journal_errors(
                                "local-rerank", bench_start_time_str
                            )
                            error_lines.extend(journal_errors)
                        benchmark_data[cache_key]["rerank"]["errors"] = error_lines

                        # Measure VRAM and RAM
                        if run_cfg == "running":
                            gpu_mem_mb = "-n.a.-"
                            cpu_mem_mb = "-n.a.-"
                        else:
                            post_run_vram = get_gpu_memory_mb(lrr_device)
                            gpu_mem_mb = max(0.0, post_run_vram - baseline_vram)
                            cpu_mem_mb = get_process_rss_mem_mb(srv["proc_pattern"])

                        benchmark_data[cache_key]["rerank"]["gpu_mem_mb"] = gpu_mem_mb
                        benchmark_data[cache_key]["rerank"]["cpu_mem_mb"] = cpu_mem_mb
                        benchmark_data[cache_key]["rerank"]["test_name"] = (
                            f"rerank_{cache_key}"
                        )
                        benchmark_data[cache_key]["rerank"]["device_setting"] = (
                            "running on host"
                            if run_cfg == "running"
                            else (lrr_device if lrr_device else "Default")
                        )
                        benchmark_data[cache_key]["rerank"]["special_setting"] = (
                            "unknown"
                            if run_cfg == "running"
                            else f"Layers: {99 if run_cfg != 'cpu' else 0}"
                        )
                        env_dict = read_env_file(srv["env_file"])
                        env_dict.update(updates)
                        benchmark_data[cache_key]["rerank"]["env"] = env_dict
                        if run_cfg != "running" and lrr_device in available_devices:
                            benchmark_data[cache_key]["rerank"]["device_details"] = (
                                available_devices[lrr_device]
                            )
                else:
                    stdout = get_mock_output("rerank", run_cfg)
                    benchmark_data[cache_key]["rerank"] = parse_rerank_output(stdout)
                    benchmark_data[cache_key]["rerank"]["errors"] = []

                    if run_cfg == "running":
                        benchmark_data[cache_key]["rerank"]["gpu_mem_mb"] = "-n.a.-"
                        benchmark_data[cache_key]["rerank"]["cpu_mem_mb"] = "-n.a.-"
                        benchmark_data[cache_key]["rerank"]["device_setting"] = (
                            "running on host"
                        )
                        benchmark_data[cache_key]["rerank"]["special_setting"] = (
                            "unknown"
                        )
                    else:
                        benchmark_data[cache_key]["rerank"]["gpu_mem_mb"] = (
                            get_mock_gpu_mem("rerank", run_cfg)
                        )
                        benchmark_data[cache_key]["rerank"]["cpu_mem_mb"] = (
                            get_mock_cpu_mem("rerank", run_cfg)
                        )
                        benchmark_data[cache_key]["rerank"]["device_setting"] = (
                            dev
                            if dev
                            else (
                                "ROCm0"
                                if run_cfg == "hip"
                                else (
                                    "Vulkan0"
                                    if run_cfg == "vulkan"
                                    else ("BLAS" if run_cfg == "cpu" else "Default")
                                )
                            )
                        )
                        benchmark_data[cache_key]["rerank"]["special_setting"] = (
                            f"Layers: {99 if run_cfg != 'cpu' else 0}"
                        )

                    benchmark_data[cache_key]["rerank"]["bench_time_s"] = 8.7
                    benchmark_data[cache_key]["rerank"]["test_name"] = (
                        f"rerank_{cache_key}"
                    )

                    if run_cfg == "running":
                        mock_updates = {}
                    else:
                        mock_updates = {
                            "LRR_DEVICE": dev
                            if dev
                            else (
                                "ROCm0"
                                if run_cfg == "hip"
                                else ("Vulkan0" if run_cfg == "vulkan" else "")
                            ),
                            "LRR_N_GPU_LAYERS": "99" if run_cfg != "cpu" else "0",
                        }
                    try:
                        env_dict = read_env_file(srv["env_file"])
                    except Exception:
                        env_dict = {}
                    env_dict.update(mock_updates)
                    benchmark_data[cache_key]["rerank"]["env"] = env_dict

                    if run_cfg != "running":
                        lrr_device = (
                            dev
                            if dev
                            else (
                                "ROCm0"
                                if run_cfg == "hip"
                                else ("Vulkan0" if run_cfg == "vulkan" else "")
                            )
                        )
                        dev_details = available_devices.get(lrr_device, {})
                        if not dev_details:
                            dev_details = {
                                "device_id": lrr_device,
                                "name": "AMD Radeon RX 7900 XTX"
                                if "0" in lrr_device
                                else "AMD Radeon Graphics",
                                "total_mem_mib": 24576.0
                                if "0" in lrr_device
                                else 56261.0,
                                "free_mem_mib": 24000.0
                                if "0" in lrr_device
                                else 92380.0,
                            }
                        benchmark_data[cache_key]["rerank"]["device_details"] = (
                            dev_details
                        )

                if not args.mock and run_cfg != "running":
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
            if run_cfg == "special":
                print("Skipping STT for Special configuration.")
            else:
                if run_cfg != "running":
                    print(f"Preparing environment file: {srv['env_file']}")
                proc = None
                master_fd = None
                baseline_vram = 0.0

                # Determine the target device
                if run_cfg == "running":
                    stt_device = "running on host"
                else:
                    stt_device = (
                        dev
                        if dev
                        else (
                            "Vulkan0"
                            if run_cfg == "vulkan"
                            else ("ROCm0" if run_cfg == "hip" else "")
                        )
                    )

                if not args.mock:
                    if run_cfg == "running":
                        baseline_vram = 0.0
                        updates = {}
                        is_up = False
                        try:
                            with socket.create_connection(
                                ("127.0.0.1", srv["port"]), timeout=1.0
                            ):
                                is_up = True
                        except Exception:
                            pass
                        if not is_up:
                            print(
                                f"Error: whisper-server is not running on port {srv['port']}."
                            )
                            set_service_fail_metrics(
                                benchmark_data,
                                cache_key,
                                "stt",
                                "running on host",
                                "unknown",
                                srv["env_file"],
                                ["Error: service is not running on port"],
                                {},
                            )
                            continue
                        proc = None
                        master_fd = None
                    else:
                        baseline_vram = get_gpu_memory_mb(stt_device)

                        # Extract numeric index if dev is e.g. "ROCm1" -> "1"
                        if run_cfg in ("vulkan", "hip") and dev:
                            idx_match = re.search(r"\d+", dev)
                            lstt_device = idx_match.group(0) if idx_match else "0"
                        else:
                            lstt_device = ""

                        updates = {
                            "LSTT_DEVICE": lstt_device,
                            "LSTT_NO_GPU": "true" if run_cfg == "cpu" else "false",
                        }
                        hip_vis, cuda_vis = get_visible_devices_env(
                            run_cfg, stt_device, hip_devices_resolved
                        )
                        updates["HIP_VISIBLE_DEVICES"] = hip_vis
                        updates["CUDA_VISIBLE_DEVICES"] = cuda_vis
                        # Build environment arguments
                        env_args = []
                        for k, v in updates.items():
                            env_args.extend(["--env", f"{k}={v}"])

                        proc, master_fd = start_service(srv["script"], env_args)
                        # Wait for server readiness
                        print(f"Waiting for whisper-server on port {srv['port']}...")
                        if not wait_for_port(srv["port"], proc=proc):
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
                            set_service_fail_metrics(
                                benchmark_data,
                                cache_key,
                                "stt",
                                lstt_device if lstt_device else "Default",
                                "No GPU" if run_cfg == "cpu" else "Use GPU",
                                srv["env_file"],
                                [
                                    "Error: whisper-server failed to start or port timed out"
                                ],
                                updates,
                            )
                            continue
                else:
                    proc = None

                print("Running STT benchmark...")
                if not args.mock:
                    start_time = time.time()
                    bench_start_time_str = datetime.datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                    stdout, success, error_lines = run_benchmark(
                        srv["script"],
                        ["--benchmark", "--repeat", "1", "--format", "json"],
                        server_proc=proc,
                    )
                    if not success:
                        print(
                            f"⚠️ Warning: Benchmark command for STT on config '{cache_key}' failed."
                        )
                        if run_cfg == "running":
                            journal_errors = get_journal_errors(
                                "local-speech-to-text", bench_start_time_str
                            )
                            error_lines.extend(journal_errors)
                        set_service_fail_metrics(
                            benchmark_data,
                            cache_key,
                            "stt",
                            "running on host"
                            if run_cfg == "running"
                            else (lstt_device if lstt_device else "Default"),
                            "unknown"
                            if run_cfg == "running"
                            else ("No GPU" if run_cfg == "cpu" else "Use GPU"),
                            srv["env_file"],
                            error_lines,
                            updates,
                        )
                    else:
                        elapsed_time = time.time() - start_time
                        benchmark_data[cache_key]["stt"] = parse_stt_output(stdout)
                        benchmark_data[cache_key]["stt"]["bench_time_s"] = elapsed_time
                        if run_cfg == "running":
                            journal_errors = get_journal_errors(
                                "local-speech-to-text", bench_start_time_str
                            )
                            error_lines.extend(journal_errors)
                        benchmark_data[cache_key]["stt"]["errors"] = error_lines

                        # Measure VRAM and RAM
                        if run_cfg == "running":
                            gpu_mem_mb = "-n.a.-"
                            cpu_mem_mb = "-n.a.-"
                        else:
                            post_run_vram = get_gpu_memory_mb(stt_device)
                            gpu_mem_mb = max(0.0, post_run_vram - baseline_vram)
                            cpu_mem_mb = get_process_rss_mem_mb(srv["proc_pattern"])

                        benchmark_data[cache_key]["stt"]["gpu_mem_mb"] = gpu_mem_mb
                        benchmark_data[cache_key]["stt"]["cpu_mem_mb"] = cpu_mem_mb
                        benchmark_data[cache_key]["stt"]["test_name"] = (
                            f"stt_{cache_key}"
                        )
                        benchmark_data[cache_key]["stt"]["device_setting"] = (
                            "running on host"
                            if run_cfg == "running"
                            else (lstt_device if lstt_device else "Default")
                        )
                        benchmark_data[cache_key]["stt"]["special_setting"] = (
                            "unknown"
                            if run_cfg == "running"
                            else ("No GPU" if run_cfg == "cpu" else "Use GPU")
                        )
                        env_dict = read_env_file(srv["env_file"])
                        env_dict.update(updates)
                        benchmark_data[cache_key]["stt"]["env"] = env_dict
                        if run_cfg != "running" and dev and dev in available_devices:
                            benchmark_data[cache_key]["stt"]["device_details"] = (
                                available_devices[dev]
                            )
                else:
                    stdout = get_mock_output("stt", run_cfg)
                    benchmark_data[cache_key]["stt"] = parse_stt_output(stdout)
                    benchmark_data[cache_key]["stt"]["errors"] = []

                    if run_cfg == "running":
                        benchmark_data[cache_key]["stt"]["gpu_mem_mb"] = "-n.a.-"
                        benchmark_data[cache_key]["stt"]["cpu_mem_mb"] = "-n.a.-"
                        benchmark_data[cache_key]["stt"]["device_setting"] = (
                            "running on host"
                        )
                        benchmark_data[cache_key]["stt"]["special_setting"] = "unknown"
                    else:
                        benchmark_data[cache_key]["stt"]["gpu_mem_mb"] = (
                            get_mock_gpu_mem("stt", run_cfg)
                        )
                        benchmark_data[cache_key]["stt"]["cpu_mem_mb"] = (
                            get_mock_cpu_mem("stt", run_cfg)
                        )
                        mock_lstt_dev = "0"
                        if run_cfg in ("vulkan", "hip") and dev:
                            m_idx = re.search(r"\d+", dev)
                            if m_idx:
                                mock_lstt_dev = m_idx.group(0)
                        else:
                            mock_lstt_dev = "Default" if run_cfg == "cpu" else "0"

                        benchmark_data[cache_key]["stt"]["device_setting"] = (
                            "0"
                            if run_cfg != "cpu" and mock_lstt_dev != "Default"
                            else mock_lstt_dev
                        )
                        benchmark_data[cache_key]["stt"]["special_setting"] = (
                            "No GPU" if run_cfg == "cpu" else "Use GPU"
                        )

                    benchmark_data[cache_key]["stt"]["bench_time_s"] = 5.3
                    benchmark_data[cache_key]["stt"]["test_name"] = f"stt_{cache_key}"

                    if run_cfg == "running":
                        mock_updates = {}
                    else:
                        mock_updates = {
                            "LSTT_DEVICE": mock_lstt_dev
                            if run_cfg != "cpu" and mock_lstt_dev != "Default"
                            else "",
                            "LSTT_NO_GPU": "false" if run_cfg != "cpu" else "true",
                        }
                    try:
                        env_dict = read_env_file(srv["env_file"])
                    except Exception:
                        env_dict = {}
                    env_dict.update(mock_updates)
                    benchmark_data[cache_key]["stt"]["env"] = env_dict

                    if run_cfg != "running" and dev:
                        dev_details = available_devices.get(dev, {})
                        if not dev_details:
                            dev_details = {
                                "device_id": dev,
                                "name": "AMD Radeon RX 7900 XTX"
                                if "0" in dev
                                else "AMD Radeon Graphics",
                                "total_mem_mib": 24576.0 if "0" in dev else 56261.0,
                                "free_mem_mib": 24000.0 if "0" in dev else 92380.0,
                            }
                        benchmark_data[cache_key]["stt"]["device_details"] = dev_details

                # Stop service
                if not args.mock and run_cfg != "running":
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
            if run_cfg == "special":
                # combination of all enabled GPU devices with CPU
                tts_modes_to_test = []
                for dev_id in hip_devices_resolved:
                    tts_modes_to_test.append((f"cpu-hip-{dev_id}", "hybrid", dev_id))
                for dev_id in vulkan_devices_resolved:
                    tts_modes_to_test.append((f"cpu-vulkan-{dev_id}", "hybrid", dev_id))
                # fallback
                if not tts_modes_to_test:
                    tts_modes_to_test.append(("cpu-hip-ROCm0", "hybrid", "ROCm0"))
            elif run_cfg == "running":
                ltts_mode = "unknown"
                ltts_device = "running on host"
                tts_modes_to_test = [(cache_key, ltts_mode, ltts_device)]
            else:
                ltts_mode = "cpu" if run_cfg == "cpu" else "gpu"
                ltts_device = "cpu" if run_cfg == "cpu" else (dev if dev else run_cfg)
                tts_modes_to_test = [(cache_key, ltts_mode, ltts_device)]

            for data_key, ltts_mode, ltts_device in tts_modes_to_test:
                print(
                    f"Running TTS benchmark for mode '{ltts_mode}' on device '{ltts_device}' (key: {data_key})"
                )
                if run_cfg != "running":
                    print(f"Preparing environment file: {srv['env_file']}")
                proc = None
                master_fd = None
                baseline_vram = 0.0

                # Initialize sub-dict for data_key if not exists
                if data_key not in benchmark_data:
                    benchmark_data[data_key] = {}

                actual_device = ltts_device
                if not args.mock:
                    if run_cfg == "running":
                        baseline_vram = 0.0
                        updates = {}
                        is_up = False
                        try:
                            with socket.create_connection(
                                ("127.0.0.1", srv["port"]), timeout=1.0
                            ):
                                is_up = True
                        except Exception:
                            pass
                        if not is_up:
                            print(
                                f"Error: qwen3-tts-server is not running on port {srv['port']}."
                            )
                            set_service_fail_metrics(
                                benchmark_data,
                                data_key,
                                "tts",
                                "running on host",
                                "unknown",
                                srv["env_file"],
                                ["Error: service is not running on port"],
                                {},
                            )
                            continue
                        proc = None
                        master_fd = None
                    else:
                        baseline_vram = get_gpu_memory_mb(ltts_device)

                        # Self-healing check: check if qwen3-tts-server supports --device
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
                        hip_vis, cuda_vis = get_visible_devices_env(
                            run_cfg, actual_device, hip_devices_resolved
                        )
                        updates["HIP_VISIBLE_DEVICES"] = hip_vis
                        updates["CUDA_VISIBLE_DEVICES"] = cuda_vis

                        # Build environment arguments
                        env_args = []
                        for k, v in updates.items():
                            env_args.extend(["--env", f"{k}={v}"])

                        proc, master_fd = start_service(srv["script"], env_args)
                        print(f"Waiting for qwen3-tts-server on port {srv['port']}...")
                        if not wait_for_port(srv["port"], proc=proc):
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
                            set_service_fail_metrics(
                                benchmark_data,
                                data_key,
                                "tts",
                                actual_device if actual_device else "Default",
                                f"mode: {ltts_mode}",
                                srv["env_file"],
                                [
                                    "Error: qwen3-tts-server failed to start or port timed out"
                                ],
                                updates,
                            )
                            continue
                else:
                    proc = None

                print("Running TTS benchmark...")
                if not args.mock:
                    start_time = time.time()
                    bench_start_time_str = datetime.datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                    stdout, success, error_lines = run_benchmark(
                        srv["script"],
                        ["--benchmark", "--repeat", "1", "--format", "json"],
                        server_proc=proc,
                    )
                    if not success:
                        print(
                            f"⚠️ Warning: Benchmark command for TTS on config '{data_key}' failed."
                        )
                        if run_cfg == "running":
                            journal_errors = get_journal_errors(
                                "local-text-to-speech", bench_start_time_str
                            )
                            error_lines.extend(journal_errors)
                        set_service_fail_metrics(
                            benchmark_data,
                            data_key,
                            "tts",
                            "running on host"
                            if run_cfg == "running"
                            else (actual_device if actual_device else "Default"),
                            "unknown" if run_cfg == "running" else f"mode: {ltts_mode}",
                            srv["env_file"],
                            error_lines,
                            updates,
                        )
                    else:
                        elapsed_time = time.time() - start_time
                        benchmark_data[data_key]["tts"] = parse_tts_output(stdout)
                        benchmark_data[data_key]["tts"]["bench_time_s"] = elapsed_time
                        if run_cfg == "running":
                            journal_errors = get_journal_errors(
                                "local-text-to-speech", bench_start_time_str
                            )
                            error_lines.extend(journal_errors)
                        benchmark_data[data_key]["tts"]["errors"] = error_lines

                        # Measure VRAM and RAM
                        if run_cfg == "running":
                            gpu_mem_mb = "-n.a.-"
                            cpu_mem_mb = "-n.a.-"
                        else:
                            post_run_vram = get_gpu_memory_mb(ltts_device)
                            gpu_mem_mb = max(0.0, post_run_vram - baseline_vram)
                            cpu_mem_mb = get_process_rss_mem_mb(srv["proc_pattern"])

                        benchmark_data[data_key]["tts"]["gpu_mem_mb"] = gpu_mem_mb
                        benchmark_data[data_key]["tts"]["cpu_mem_mb"] = cpu_mem_mb
                        benchmark_data[data_key]["tts"]["test_name"] = f"tts_{data_key}"
                        benchmark_data[data_key]["tts"]["device_setting"] = (
                            "running on host"
                            if run_cfg == "running"
                            else (actual_device if actual_device else "Default")
                        )
                        benchmark_data[data_key]["tts"]["special_setting"] = (
                            "unknown" if run_cfg == "running" else f"mode: {ltts_mode}"
                        )
                        env_dict = read_env_file(srv["env_file"])
                        env_dict.update(updates)
                        benchmark_data[data_key]["tts"]["env"] = env_dict
                        if run_cfg != "running" and ltts_device in available_devices:
                            benchmark_data[data_key]["tts"]["device_details"] = (
                                available_devices[ltts_device]
                            )
                else:
                    stdout = get_mock_output("tts", data_key)
                    benchmark_data[data_key]["tts"] = parse_tts_output(stdout)
                    benchmark_data[data_key]["tts"]["errors"] = []

                    if run_cfg == "running":
                        benchmark_data[data_key]["tts"]["gpu_mem_mb"] = "-n.a.-"
                        benchmark_data[data_key]["tts"]["cpu_mem_mb"] = "-n.a.-"
                        benchmark_data[data_key]["tts"]["device_setting"] = (
                            "running on host"
                        )
                        benchmark_data[data_key]["tts"]["special_setting"] = "unknown"
                    else:
                        benchmark_data[data_key]["tts"]["gpu_mem_mb"] = (
                            get_mock_gpu_mem("tts", data_key)
                        )
                        benchmark_data[data_key]["tts"]["cpu_mem_mb"] = (
                            get_mock_cpu_mem("tts", data_key)
                        )
                        benchmark_data[data_key]["tts"]["device_setting"] = (
                            ltts_device if ltts_device else "Default"
                        )
                        benchmark_data[data_key]["tts"]["special_setting"] = (
                            f"mode: {ltts_mode}"
                        )

                    benchmark_data[data_key]["tts"]["bench_time_s"] = 25.1
                    benchmark_data[data_key]["tts"]["test_name"] = f"tts_{data_key}"

                    if run_cfg == "running":
                        mock_updates = {}
                    else:
                        mock_updates = {
                            "LTTS_MODE": ltts_mode,
                            "LTTS_DEVICE": ltts_device,
                        }
                    try:
                        env_dict = read_env_file(srv["env_file"])
                    except Exception:
                        env_dict = {}
                    env_dict.update(mock_updates)
                    benchmark_data[data_key]["tts"]["env"] = env_dict

                    if run_cfg != "running":
                        dev_details = available_devices.get(ltts_device, {})
                        if not dev_details and ltts_device != "cpu":
                            dev_details = {
                                "device_id": ltts_device,
                                "name": "AMD Radeon RX 7900 XTX"
                                if "0" in ltts_device
                                else "AMD Radeon Graphics",
                                "total_mem_mib": 24576.0
                                if "0" in ltts_device
                                else 56261.0,
                                "free_mem_mib": 24000.0
                                if "0" in ltts_device
                                else 92380.0,
                            }
                        if dev_details:
                            benchmark_data[data_key]["tts"]["device_details"] = (
                                dev_details
                            )

                if not args.mock and run_cfg != "running":
                    stop_service(
                        "tts",
                        srv["port"],
                        srv["proc_pattern"],
                        proc,
                        master_fd,
                    )
        # ---------------------------------------------------------
        # 5. Image Generation Service
        # ---------------------------------------------------------
        if "image" in target_services:
            srv = SERVICES["image"]
            if run_cfg == "special":
                print("Skipping Image for Special configuration.")
            else:
                if run_cfg != "running":
                    print(f"Preparing environment file: {srv['env_file']}")
                proc = None
                master_fd = None
                baseline_vram = 0.0

                # Determine the target backend device
                if run_cfg == "running":
                    img_backend = "running on host"
                else:
                    if run_cfg == "cpu":
                        img_backend = "cpu"
                    else:
                        target_dev = dev if dev else "vulkan1"
                        gpu = GLOBAL_GPU_REGISTRY.get_by_device_string(target_dev)
                        if run_cfg == "hip" or run_cfg == "special":
                            idx = gpu.rocm_index if gpu and gpu.rocm_index is not None else 0
                            img_backend = f"rocm{idx}"
                        else:
                            idx = gpu.vulkan_index if gpu and gpu.vulkan_index is not None else 1
                            img_backend = f"vulkan{idx}"
                            if gpu and gpu.is_igpu:
                                img_backend += ",te=cpu"  # offload text encoder for iGPU

                if not args.mock:
                    if run_cfg == "running":
                        baseline_vram = 0.0
                        updates = {}
                        is_up = False
                        try:
                            with socket.create_connection(
                                ("127.0.0.1", srv["port"]), timeout=1.0
                            ):
                                is_up = True
                        except Exception:
                            pass
                        if not is_up:
                            print(
                                f"Error: sd-server is not running on port {srv['port']}."
                            )
                            set_service_fail_metrics(
                                benchmark_data,
                                cache_key,
                                "image",
                                "running on host",
                                "unknown",
                                srv["env_file"],
                                ["Error: service is not running on port"],
                                {},
                            )
                            continue
                        proc = None
                        master_fd = None
                    else:
                        baseline_vram = get_gpu_memory_mb(img_backend)

                        updates = {
                            "LIMG_BACKEND": img_backend,
                        }
                        hip_vis, cuda_vis = get_visible_devices_env(
                            run_cfg, img_backend, hip_devices_resolved
                        )
                        updates["HIP_VISIBLE_DEVICES"] = hip_vis
                        updates["CUDA_VISIBLE_DEVICES"] = cuda_vis

                        # Build environment arguments
                        env_args = []
                        for k, v in updates.items():
                            env_args.extend(["--env", f"{k}={v}"])

                        # Start service
                        proc, master_fd = start_service(srv["script"], env_args)

                        # Wait for server readiness
                        print(f"Waiting for sd-server on port {srv['port']}...")
                        if not wait_for_port(srv["port"], proc=proc):
                            print(
                                f"Error: sd-server failed to start on port {srv['port']}."
                            )
                            stop_service(
                                "image",
                                srv["port"],
                                srv["proc_pattern"],
                                proc,
                                master_fd,
                            )
                            set_service_fail_metrics(
                                benchmark_data,
                                cache_key,
                                "image",
                                img_backend if img_backend else "Default",
                                "Steps: 8",
                                srv["env_file"],
                                ["Error: sd-server failed to start or port timed out"],
                                updates,
                            )
                            continue
                else:
                    proc = None

                # Run benchmarks
                print("Running Image Generation benchmark")
                if not args.mock:
                    start_time = time.time()
                    bench_start_time_str = datetime.datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                    stdout, success, error_lines = run_benchmark(
                        srv["script"],
                        ["--benchmark", "--repeat", "1", "--format", "json"],
                        server_proc=proc,
                    )
                    if not success:
                        print(
                            f"⚠️ Warning: Benchmark command for image on config '{cache_key}' failed."
                        )
                        if run_cfg == "running":
                            journal_errors = get_journal_errors(
                                "local-image", bench_start_time_str
                            )
                            error_lines.extend(journal_errors)
                        set_service_fail_metrics(
                            benchmark_data,
                            cache_key,
                            "image",
                            "running on host"
                            if run_cfg == "running"
                            else (img_backend if img_backend else "Default"),
                            "unknown" if run_cfg == "running" else "Steps: 8",
                            srv["env_file"],
                            error_lines,
                            updates,
                        )
                    else:
                        elapsed_time = time.time() - start_time
                        benchmark_data[cache_key]["image"] = parse_image_output(stdout)
                        benchmark_data[cache_key]["image"]["bench_time_s"] = (
                            elapsed_time
                        )
                        if run_cfg == "running":
                            journal_errors = get_journal_errors(
                                "local-image", bench_start_time_str
                            )
                            error_lines.extend(journal_errors)
                        benchmark_data[cache_key]["image"]["errors"] = error_lines

                        # Measure VRAM and RAM
                        if run_cfg == "running":
                            gpu_mem_mb = "-n.a.-"
                            cpu_mem_mb = "-n.a.-"
                        else:
                            post_run_vram = get_gpu_memory_mb(img_backend)
                            gpu_mem_mb = max(0.0, post_run_vram - baseline_vram)
                            cpu_mem_mb = get_process_rss_mem_mb(srv["proc_pattern"])

                        benchmark_data[cache_key]["image"]["gpu_mem_mb"] = gpu_mem_mb
                        benchmark_data[cache_key]["image"]["cpu_mem_mb"] = cpu_mem_mb
                        benchmark_data[cache_key]["image"]["test_name"] = (
                            f"image_{cache_key}"
                        )
                        benchmark_data[cache_key]["image"]["device_setting"] = (
                            "running on host"
                            if run_cfg == "running"
                            else (img_backend if img_backend else "Default")
                        )
                        benchmark_data[cache_key]["image"]["special_setting"] = (
                            "unknown" if run_cfg == "running" else "Steps: 8"
                        )
                        env_dict = read_env_file(srv["env_file"])
                        env_dict.update(updates)
                        benchmark_data[cache_key]["image"]["env"] = env_dict
                        if run_cfg != "running" and img_backend in available_devices:
                            benchmark_data[cache_key]["image"]["device_details"] = (
                                available_devices[img_backend]
                            )
                else:
                    stdout = get_mock_output("image", run_cfg)
                    benchmark_data[cache_key]["image"] = parse_image_output(stdout)
                    benchmark_data[cache_key]["image"]["errors"] = []

                    if run_cfg == "running":
                        benchmark_data[cache_key]["image"]["gpu_mem_mb"] = "-n.a.-"
                        benchmark_data[cache_key]["image"]["cpu_mem_mb"] = "-n.a.-"
                        benchmark_data[cache_key]["image"]["device_setting"] = (
                            "running on host"
                        )
                        benchmark_data[cache_key]["image"]["special_setting"] = (
                            "unknown"
                        )
                    else:
                        benchmark_data[cache_key]["image"]["gpu_mem_mb"] = (
                            get_mock_gpu_mem("image", run_cfg)
                        )
                        benchmark_data[cache_key]["image"]["cpu_mem_mb"] = (
                            get_mock_cpu_mem("image", run_cfg)
                        )
                        benchmark_data[cache_key]["image"]["device_setting"] = (
                            img_backend
                        )
                        benchmark_data[cache_key]["image"]["special_setting"] = (
                            "Steps: 8"
                        )

                    benchmark_data[cache_key]["image"]["bench_time_s"] = 12.5
                    benchmark_data[cache_key]["image"]["test_name"] = (
                        f"image_{cache_key}"
                    )

                    if run_cfg == "running":
                        mock_updates = {}
                    else:
                        mock_updates = {
                            "LIMG_BACKEND": img_backend,
                        }
                    try:
                        env_dict = read_env_file(srv["env_file"])
                    except Exception:
                        env_dict = {}
                    env_dict.update(mock_updates)
                    benchmark_data[cache_key]["image"]["env"] = env_dict

                    if run_cfg != "running":
                        dev_details = available_devices.get(img_backend, {})
                        if not dev_details:
                            dev_details = {
                                "device_id": img_backend,
                                "name": "AMD Radeon RX 7900 XTX"
                                if "0" in img_backend
                                else "AMD Radeon Graphics",
                                "total_mem_mib": 24576.0
                                if "0" in img_backend
                                else 56261.0,
                                "free_mem_mib": 24000.0
                                if "0" in img_backend
                                else 92380.0,
                            }
                        benchmark_data[cache_key]["image"]["device_details"] = (
                            dev_details
                        )

                # Stop service
                if not args.mock and run_cfg != "running":
                    stop_service(
                        "image",
                        srv["port"],
                        srv["proc_pattern"],
                        proc,
                        master_fd,
                    )

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
    report_content = generate_report(
        benchmark_data,
        hip_devices=hip_devices_resolved,
        vulkan_devices=vulkan_devices_resolved,
    )

    # Save report
    os.makedirs(os.path.dirname(args.report), exist_ok=True)
    with open(args.report, "w", encoding="utf-8") as f:
        f.write(report_content)
    print(f"Successfully wrote report to: {args.report}")

    # Memory summary printout for 'running' config
    if "running" in target_configs:
        print("\n==================================================")
        print("💾 Running Services VRAM / RAM Memory Usage Summary")
        print("==================================================")
        if args.mock:
            print("  - dGPU (ROCm0) VRAM Used: 14520.00 MB (Mock)")
            print("  - iGPU (ROCm1) VRAM Used: 2620.00 MB (Mock)")
            print("  - CPU RSS Memory by Service Process (Mock):")
            for sname in SERVICES:
                print(f"    * {sname:10}: 300.00 MB (Mock)")
            print("    * Total Services CPU RSS: 1500.00 MB (Mock)")
        else:
            dgpu_mem = get_gpu_memory_mb("ROCm0")
            igpu_mem = get_gpu_memory_mb("ROCm1")
            print(f"  - dGPU (ROCm0) VRAM Used: {dgpu_mem:.2f} MB")
            print(f"  - iGPU (ROCm1) VRAM Used: {igpu_mem:.2f} MB")
            print("  - CPU RSS Memory by Service Process:")
            total_rss = 0.0
            for sname, srv in SERVICES.items():
                rss = get_process_rss_mem_mb(srv["proc_pattern"])
                total_rss += rss
                print(f"    * {sname:10}: {rss:.2f} MB")
            print(f"    * Total Services CPU RSS: {total_rss:.2f} MB")
        print("==================================================\n")


if __name__ == "__main__":
    main()
