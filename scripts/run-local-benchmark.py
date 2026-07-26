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
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union

# Known iGPU GFX versions
IGPU_GFX_IDS = frozenset(
    {"gfx90c", "gfx902", "gfx909", "gfx1035", "gfx1036", "gfx1103", "gfx1150"}
)


@dataclass
class GPUCard:
    rocm_smi_card: str  # e.g. "card0"
    name: str  # e.g. "AMD Radeon RX 7900 XTX"
    gfx_version: str  # e.g. "gfx1100"
    vram_total_mb: float
    is_igpu: bool
    rocm_index: Optional[int]  # ROCm device index
    vulkan_index: Optional[int]  # Vulkan device index


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
    "completion": {
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
        "proc_pattern": "(llama-server|text-embeddings-router).*--port 50086",
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


def gather_pkg_versions() -> Dict[str, str]:
    """Retrieve versions of CLI packages using binary commands with graceful fallbacks."""
    # 1. llama
    llama_ver = "unknown"
    try:
        res = subprocess.run(
            ["llama-cli", "--version"],
            capture_output=True,
            text=True,
            check=False,
        )
        output = res.stdout.strip() or res.stderr.strip()
        match = re.search(r"version:\s*([^\n]+)", output)
        if match:
            llama_ver = match.group(1).strip()
        elif output:
            llama_ver = output.splitlines()[0].strip()
    except Exception:
        pass

    # 2. stabledifussion
    sd_ver = "unknown"
    try:
        res = subprocess.run(
            ["sd-cli", "--version"], capture_output=True, text=True, check=False
        )
        output = res.stdout.strip() or res.stderr.strip()
        match = re.search(r"stable-diffusion\.cpp version\s*([^\n]+)", output)
        if match:
            sd_ver = match.group(1).strip()
        elif output:
            sd_ver = output.splitlines()[0].strip()
    except Exception:
        pass

    # 3. whisper
    whisper_ver = "unknown"
    try:
        res = subprocess.run(
            ["whisper-cli", "--version"],
            capture_output=True,
            text=True,
            check=False,
        )
        output = res.stdout.strip() or res.stderr.strip()
        for line in output.splitlines():
            match = re.search(r"whisper\.cpp version:\s*([^\n]+)", line)
            if match:
                whisper_ver = match.group(1).strip()
                break
        if whisper_ver == "unknown" and output:
            for line in reversed(output.splitlines()):
                if "version" in line.lower():
                    whisper_ver = line.strip()
                    break
    except Exception:
        pass

    # 4. qwen3-tts
    qwen_ver = "unknown"
    try:
        res = subprocess.run(
            ["qwen3-tts-cli", "--version"],
            capture_output=True,
            text=True,
            check=False,
        )
        if res.returncode == 0:
            output = res.stdout.strip() or res.stderr.strip()
            match = re.search(
                r"(?:version|qwen3-tts\.cpp version):\s*([^\n]+)",
                output,
                re.IGNORECASE,
            )
            if match:
                qwen_ver = match.group(1).strip()
            elif output:
                qwen_ver = output.splitlines()[0].strip()
    except Exception:
        pass

    return {
        "llama": llama_ver,
        "stabledifussion": sd_ver,
        "whisper": whisper_ver,
        "qwen3-tts": qwen_ver,
    }


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
    if run_cfg == "vulkan" or run_cfg.startswith("cpu"):
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

            if (
                target_key
                and target_key in data
                and "VRAM Total Used Memory (B)" in data[target_key]
            ):
                return float(data[target_key]["VRAM Total Used Memory (B)"]) / (
                    1024.0 * 1024.0
                )

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
    if config.endswith("-combi"):
        config = config[:-6]
    if config.startswith("cpu"):
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
        "completion": {
            "hip": 1200.0,
            "vulkan": 1250.0,
        },
    }
    return mems.get(mode, {}).get(lookup_cfg, 0.0)


def get_mock_cpu_mem(mode: str, config: str) -> float:
    """Get realistic mock CPU memory values for validation runs."""
    if config.endswith("-combi"):
        config = config[:-6]
    lookup_cfg = config
    if config.startswith("cpu-hip") or config.startswith("cpu-vulkan"):
        lookup_cfg = "special-hybrid"
    elif config == "running":
        lookup_cfg = "hip"
    elif config.startswith("cpu"):
        lookup_cfg = "cpu"

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
        "completion": {
            "hip": 300.0,
            "vulkan": 320.0,
            "cpu": 1500.0,
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
        GLOBAL_GPU_REGISTRY.cards.append(
            GPUCard(
                rocm_smi_card="card0",
                name="AMD Radeon RX 7900 XTX",
                gfx_version="gfx1100",
                vram_total_mb=24576.0,
                is_igpu=False,
                rocm_index=0,
                vulkan_index=1,
            )
        )
        GLOBAL_GPU_REGISTRY.cards.append(
            GPUCard(
                rocm_smi_card="card1",
                name="AMD Radeon Graphics",
                gfx_version="gfx90c",
                vram_total_mb=4096.0,
                is_igpu=True,
                rocm_index=1,
                vulkan_index=0,
            )
        )
        return

    # 1. rocm-smi
    try:
        out = subprocess.check_output(
            [
                "/opt/rocm/bin/rocm-smi",
                "--showproductname",
                "--showmeminfo",
                "vram",
                "--json",
            ],
            text=True,
        )
        data = json.loads(out)
        for card_key, info in data.items():
            if not card_key.startswith("card"):
                continue
            name = info.get("Card Series", "Unknown GPU")
            gfx_version = info.get("GFX Version", "unknown")
            vram_bytes = info.get("VRAM Total Memory (B)", "0")
            vram_mb = float(vram_bytes) / (1024 * 1024)
            is_igpu = "Graphics" in name or "Renoir" in name
            GLOBAL_GPU_REGISTRY.cards.append(
                GPUCard(
                    rocm_smi_card=card_key,
                    name=name,
                    gfx_version=gfx_version,
                    vram_total_mb=vram_mb,
                    is_igpu=is_igpu,
                    rocm_index=None,
                    vulkan_index=None,
                )
            )
    except Exception as e:
        print(f"Warning: rocm-smi failed: {e}")

    # 2. llama-cli
    cli_paths = ["llama-cli", "/usr/bin/llama-cli", "/usr/local/bin/llama-cli"]
    custom_cli = os.getenv("LLAMA_CLI_BIN")
    if custom_cli:
        cli_paths.insert(0, custom_cli)
    cli_out = ""
    for path in cli_paths:
        try:
            cli_out = subprocess.check_output(
                [path, "--list-devices"], text=True, stderr=subprocess.STDOUT
            )
            break
        except Exception:
            continue

    # Parse llama-cli output
    for line in cli_out.splitlines():
        # ROCm0: AMD Radeon RX 7900 XTX (24576 MiB, 24000 MiB free)
        # Vulkan1: AMD Radeon RX 7900 XTX (NAVI31) (24576 MiB)
        match = re.search(r"(ROCm|Vulkan)(\d+):\s+(.*?)\s+\(", line)
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
    final_env_args = list(env_args) if env_args else []
    existing_keys = set()
    for i in range(len(final_env_args) - 1):
        if final_env_args[i] == "--env":
            val = final_env_args[i + 1]
            if "=" in val:
                existing_keys.add(val.split("=", 1)[0])

    for k, v in os.environ.items():
        k_upper = k.upper()
        if (
            k_upper.startswith(
                (
                    "LLAMA_",
                    "WHISPER_",
                    "QWEN3_",
                    "SD_",
                    "GGML_",
                    "LCHAT_",
                    "LMBD_",
                    "LCOMP_",
                    "LRR_",
                    "LSTT_",
                    "LTTS_",
                    "LIMG_",
                )
            )
            and k not in existing_keys
        ):
            final_env_args.extend(["--env", f"{k}={v}"])

    cmd.extend(final_env_args)
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


# Regex Parsers / JSON Block Extraction


def extract_json_block(
    output: str, required_key: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """Find and load the valid JSON block containing required_key in output."""
    idx = 0
    while True:
        idx = output.find("{", idx)
        if idx == -1:
            break
        jdx = output.rfind("}")
        while jdx > idx:
            sub = output[idx : jdx + 1]
            try:
                data = json.loads(sub)
                if required_key is None or required_key in data:
                    return data
            except Exception:
                pass
            jdx = output.rfind("}", 0, jdx)
        idx += 1
    return None


def parse_chat_output(output: str) -> Dict[str, float]:
    """Parse chat benchmark stats from stdout."""
    res = {}
    data = extract_json_block(output, "chat_avg_gen")
    if data is not None:
        res["chat_warmup_prompt"] = float(data.get("chat_warmup_prompt", 0.0))
        res["chat_warmup_comp"] = float(data.get("chat_warmup_comp", 0.0))
        res["chat_warmup_ttft"] = float(data.get("chat_warmup_ttft", 0.0))
        res["chat_warmup_prefill"] = float(data.get("chat_warmup_prefill", 0.0))
        res["chat_warmup_gen"] = float(data.get("chat_warmup_gen", 0.0))
        res["chat_avg_comp"] = float(data.get("chat_avg_comp", 0.0))
        res["chat_avg_ttft"] = float(data.get("chat_avg_ttft", 0.0))
        res["chat_avg_prefill"] = float(data.get("chat_avg_prefill", 0.0))
        res["chat_avg_gen"] = float(data.get("chat_avg_gen", 0.0))
        res["chat_avg_decode"] = float(data.get("chat_avg_decode", 0.0))
        res["chat_image_ttft"] = float(data.get("chat_image_ttft", 0.0))
        res["chat_image_gen"] = float(data.get("chat_image_gen", 0.0))
    return res


def parse_image_output(output: str) -> Dict[str, Any]:
    """Parse image benchmark stats from stdout."""
    res = {}
    data = extract_json_block(output, "image_time")
    if data is not None:
        res["image_time"] = float(data.get("image_time", 0.0))
    return res


def parse_embed_output(output: str) -> Dict[str, float]:
    """Parse embedding benchmark stats from stdout."""
    res = {}
    data = extract_json_block(output, "embed_throughput")
    if data is not None:
        res["embed_throughput"] = float(data.get("embed_throughput", 0.0))
        embed_time = float(data.get("embed_time_s", 0.0))
        fraction_chunks = float(data.get("fraction_chunks", 1.0))
        fraction_context = float(data.get("fraction_context", 1.0))

        # Normalize the time to represent a full (1.0 fraction) run
        fraction = fraction_chunks * fraction_context
        if fraction > 0.0:
            res["embed_time_s"] = embed_time / fraction
        else:
            res["embed_time_s"] = embed_time

        res["embed_lat"] = float(data.get("embed_lat", 0.0))
        res["embed_p50"] = float(data.get("embed_p50", 0.0))
        res["embed_p95"] = float(data.get("embed_p95", 0.0))
    return res


def parse_comp_output(output: str) -> Dict[str, float]:
    """Parse completion benchmark stats from stdout."""
    res = {}
    data = extract_json_block(output, "comp_avg_gen")
    if data is not None:
        res["comp_warmup_ttft"] = float(data.get("comp_warmup_ttft", 0.0))
        res["comp_warmup_gen"] = float(data.get("comp_warmup_gen", 0.0))
        res["comp_avg_ttft"] = float(data.get("comp_avg_ttft", 0.0))
        res["comp_avg_prefill"] = float(data.get("comp_avg_prefill", 0.0))
        res["comp_avg_gen"] = float(data.get("comp_avg_gen", 0.0))
        res["comp_avg_decode"] = float(data.get("comp_avg_decode", 0.0))
    return res


def parse_rerank_output(output: str) -> Dict[str, Any]:
    """Parse reranker benchmark stats from stdout."""
    res = {}
    data = extract_json_block(output, "rerank_token_speed")
    if data is not None:
        res["rerank_time"] = float(data.get("rerank_time", 0.0))
        res["rerank_throughput"] = float(data.get("rerank_throughput", 0.0))
        res["rerank_token_speed"] = float(data.get("rerank_token_speed", 0.0))
    return res


def parse_stt_output(output: str) -> Dict[str, Any]:
    """Parse STT benchmark stats from stdout."""
    res: Dict[str, Any] = {}
    data = extract_json_block(output, "stt_rtf")
    if data is not None:
        res["stt_time"] = float(data.get("stt_time", 0.0))
        res["stt_rtf"] = float(data.get("stt_rtf", 0.0))
        res["stt_text"] = data.get("stt_text", "")
    return res


def parse_tts_output(output: str) -> Dict[str, Any]:
    """Parse TTS benchmark stats from stdout."""
    res = {}
    data = extract_json_block(output, "tts_char_speed")
    if data is not None:
        res["tts_duration"] = float(data.get("tts_duration", 0.0))
        res["tts_time"] = float(data.get("tts_time", 0.0))
        res["tts_rtf"] = float(data.get("tts_rtf", 0.0))
        res["tts_char_speed"] = float(data.get("tts_char_speed", 0.0))
    return res


def check_text_match(actual: str, expected: str, min_words_match: int = 20) -> bool:
    """Check if the actual text loosely matches the expected text."""
    if not actual:
        return False

    def normalize(text: str) -> str:
        text = text.lower()
        text = re.sub(r"[^\w\s]", " ", text)
        text = text.replace("forty five", "45")
        text = text.replace("forty-five", "45")
        return " ".join(text.split())

    act_norm = normalize(actual)
    exp_norm = normalize(expected)
    act_words = act_norm.split()
    exp_words = exp_norm.split()

    if len(act_words) < min_words_match:
        return False

    expected_prefix = " ".join(exp_words[:min_words_match])
    return expected_prefix in act_norm or act_norm.startswith(expected_prefix)


# Mock Outputs for Validation


def get_mock_output(mode: str, config: str) -> str:
    """Generate typical stdout data for validation testing in sandbox environments."""
    if config.endswith("-combi"):
        config = config[:-6]
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
    elif mode == "completion":
        return f"""
{{
  "comp_warmup_ttft": {35.0 * fac:.1f},
  "comp_warmup_gen": {120.0 / fac:.1f},
  "comp_avg_ttft": {15.0 * fac:.1f},
  "comp_avg_prefill": {450.0 / fac:.1f},
  "comp_avg_gen": {115.0 / fac:.1f},
  "comp_avg_decode": {0.5 * fac:.2f}
}}
"""
    return ""


# Report Generator


def generate_report(
    data: Dict[str, Dict[str, Dict[str, Any]]],
    hip_devices: Optional[List[str]] = None,
    vulkan_devices: Optional[List[str]] = None,
) -> str:
    """Format parsed metrics into a beautiful markdown benchmark document."""

    def get_cfg_anchor(cfg: str) -> str:
        cfg_upper = cfg.upper()
        if cfg.startswith("cpu-hip") or cfg.startswith("cpu-vulkan"):
            cfg_upper = f"SPECIAL ({cfg.upper()})"
        header_text = f"{cfg_upper} Configuration Details"
        anchor = header_text.lower()
        anchor = re.sub(r"[^a-z0-9\s\-]", "", anchor)
        anchor = anchor.replace(" ", "-")
        anchor = re.sub(r"\-+", "-", anchor)
        return f"#{anchor}"

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
        bold: bool = False,
    ) -> str:
        if cfg in data and mode in data[cfg] and key in data[cfg][mode]:
            v = data[cfg][mode][key]
            if isinstance(v, str):
                return v
            if v is None:
                return default
            try:
                formatted = f"{v:{fmt}}{suffix}"
                if bold:
                    return f"**{formatted}**"
                return formatted
            except (ValueError, TypeError):
                return str(v)
        return default

    # Speedup ratio vs Real-time (1 / RTF)
    def speedup(cfg: str, mode: str, rtf_key: str, bold: bool = False) -> str:
        if cfg in data and mode in data[cfg] and rtf_key in data[cfg][mode]:
            rtf = data[cfg][mode][rtf_key]
            if isinstance(rtf, str):
                return rtf
            if rtf > 0:
                formatted = f"{1.0 / rtf:.1f}x"
                if bold:
                    return f"**{formatted}**"
                return formatted
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
        elif cfg_lower == "cpu-blas":
            return "BLAS"
        elif cfg_lower == "cpu":
            return "none"
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
        is_combi = cfg_lower.endswith("-combi")
        base_cfg = cfg_lower[:-6] if is_combi else cfg_lower
        suffix = "-combi" if is_combi else ""

        if base_cfg.startswith("hip"):
            return (0, base_cfg + suffix)
        elif base_cfg.startswith("vulkan"):
            return (1, base_cfg + suffix)
        elif base_cfg == "cpu":
            return (2, "cpu-0-none" + suffix)
        elif base_cfg == "cpu-blas":
            return (2, "cpu-1-blas" + suffix)
        elif base_cfg.startswith("cpu-hip"):
            return (3, base_cfg + suffix)
        elif base_cfg.startswith("cpu-vulkan"):
            return (4, base_cfg + suffix)
        elif base_cfg.startswith("special"):
            return (5, base_cfg + suffix)
        return (6, base_cfg + suffix)

    import datetime

    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    chat_keys = [cfg for cfg in data.keys() if "chat" in data[cfg]]
    chat_keys.sort(key=sort_config_keys)
    embed_keys = [cfg for cfg in data.keys() if "embedding" in data[cfg]]
    embed_keys.sort(key=sort_config_keys)
    rerank_keys = [cfg for cfg in data.keys() if "rerank" in data[cfg]]
    rerank_keys.sort(key=sort_config_keys)
    stt_keys = [cfg for cfg in data.keys() if "stt" in data[cfg]]
    stt_keys.sort(key=sort_config_keys)
    tts_keys = [cfg for cfg in data.keys() if "tts" in data[cfg]]
    tts_keys.sort(key=sort_config_keys)
    image_keys = [cfg for cfg in data.keys() if "image" in data[cfg]]
    image_keys.sort(key=sort_config_keys)
    comp_keys = [cfg for cfg in data.keys() if "completion" in data[cfg]]
    comp_keys.sort(key=sort_config_keys)

    # Find the best configuration for each metric
    best_chat_cfg = None
    max_chat_gen = -1.0
    best_chat_prefill_cfg = None
    max_chat_prefill = -1.0
    for cfg in chat_keys:
        if cfg in data and "chat" in data[cfg] and "chat_avg_gen" in data[cfg]["chat"]:
            v = data[cfg]["chat"]["chat_avg_gen"]
            if isinstance(v, (int, float)):
                if v > max_chat_gen:
                    max_chat_gen = v
                    best_chat_cfg = cfg
        if (
            cfg in data
            and "chat" in data[cfg]
            and "chat_avg_prefill" in data[cfg]["chat"]
        ):
            v = data[cfg]["chat"]["chat_avg_prefill"]
            if isinstance(v, (int, float)):
                if v > max_chat_prefill:
                    max_chat_prefill = v
                    best_chat_prefill_cfg = cfg

    best_comp_cfg = None
    max_comp_gen = -1.0
    for cfg in comp_keys:
        if (
            cfg in data
            and "completion" in data[cfg]
            and "comp_avg_gen" in data[cfg]["completion"]
        ):
            v = data[cfg]["completion"]["comp_avg_gen"]
            if isinstance(v, (int, float)):
                if v > max_comp_gen:
                    max_comp_gen = v
                    best_comp_cfg = cfg

    best_embed_cfg = None
    max_embed_throughput = -1.0
    for cfg in embed_keys:
        if (
            cfg in data
            and "embedding" in data[cfg]
            and "embed_throughput" in data[cfg]["embedding"]
        ):
            v = data[cfg]["embedding"]["embed_throughput"]
            if isinstance(v, (int, float)):
                if v > max_embed_throughput:
                    max_embed_throughput = v
                    best_embed_cfg = cfg

    best_rerank_cfg = None
    max_rerank_token_speed = -1.0
    for cfg in rerank_keys:
        if (
            cfg in data
            and "rerank" in data[cfg]
            and "rerank_token_speed" in data[cfg]["rerank"]
        ):
            v = data[cfg]["rerank"]["rerank_token_speed"]
            if isinstance(v, (int, float)):
                if v > max_rerank_token_speed:
                    max_rerank_token_speed = v
                    best_rerank_cfg = cfg

    best_stt_cfg = None
    max_stt_speedup = -1.0
    for cfg in stt_keys:
        if cfg in data and "stt" in data[cfg] and "stt_rtf" in data[cfg]["stt"]:
            rtf = data[cfg]["stt"]["stt_rtf"]
            if isinstance(rtf, (int, float)) and rtf > 0:
                speedup_val = 1.0 / rtf
                if speedup_val > max_stt_speedup:
                    max_stt_speedup = speedup_val
                    best_stt_cfg = cfg

    best_tts_cfg = None
    max_tts_char_speed = -1.0
    for cfg in tts_keys:
        if cfg in data and "tts" in data[cfg] and "tts_char_speed" in data[cfg]["tts"]:
            v = data[cfg]["tts"]["tts_char_speed"]
            if isinstance(v, (int, float)):
                if v > max_tts_char_speed:
                    max_tts_char_speed = v
                    best_tts_cfg = cfg

    best_image_cfg = None
    min_image_time = 1e9
    for cfg in image_keys:
        if cfg in data and "image" in data[cfg] and "image_time" in data[cfg]["image"]:
            v = data[cfg]["image"]["image_time"]
            if isinstance(v, (int, float)):
                if v < min_image_time:
                    min_image_time = v
                    best_image_cfg = cfg

    # Generate matrix table contents dynamically
    # 1. Chat Table Body
    chat_rows = []
    for cfg in chat_keys:
        cfg_label = cfg.upper()
        row = f"| [**{cfg_label}**]({get_cfg_anchor(cfg)}) | {get_test_name(cfg, 'chat')} | {get_device_setting(cfg, 'chat')} | {get_special_setting(cfg, 'chat')} | {val(cfg, 'chat', 'chat_avg_ttft', '.2f', ' ms')} | {val(cfg, 'chat', 'chat_avg_prefill', '.2f', ' t/s', bold=(cfg == best_chat_prefill_cfg))} | {val(cfg, 'chat', 'chat_warmup_ttft', '.2f', ' ms')} | {val(cfg, 'chat', 'chat_warmup_gen', '.2f', ' t/s')} | {val(cfg, 'chat', 'chat_avg_gen', '.2f', ' t/s', bold=(cfg == best_chat_cfg))} | {val(cfg, 'chat', 'chat_image_ttft', '.2f', ' ms')} | {val(cfg, 'chat', 'chat_image_gen', '.2f', ' t/s')} | {val(cfg, 'chat', 'gpu_mem_mb', '.1f', ' MB')} | {val(cfg, 'chat', 'cpu_mem_mb', '.1f', ' MB')} |"
        chat_rows.append(row)
    if not any(cfg.startswith("hip") for cfg in chat_keys):
        chat_rows.append(
            "| **HIP** | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- |"
        )
    if not any(cfg.startswith("vulkan") for cfg in chat_keys):
        chat_rows.append(
            "| **VULKAN** | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- |"
        )
    if not any(cfg.startswith("cpu") for cfg in chat_keys):
        chat_rows.append(
            "| **CPU** | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- |"
        )
    chat_table_body = "\n".join(chat_rows)

    # 2. Embedding Table Body
    embed_rows = []
    for cfg in embed_keys:
        cfg_label = cfg.upper()
        row = f"| [**{cfg_label}**]({get_cfg_anchor(cfg)}) | {get_test_name(cfg, 'embedding')} | {get_device_setting(cfg, 'embedding')} | {get_special_setting(cfg, 'embedding')} | {val(cfg, 'embedding', 'embed_throughput', '.2f', ' t/s', bold=(cfg == best_embed_cfg))} | {val(cfg, 'embedding', 'embed_lat', '.1f', ' ms')} | {val(cfg, 'embedding', 'gpu_mem_mb', '.1f', ' MB')} | {val(cfg, 'embedding', 'cpu_mem_mb', '.1f', ' MB')} |"
        embed_rows.append(row)
    if not any(cfg.startswith("hip") for cfg in embed_keys):
        embed_rows.append(
            "| **HIP** | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- |"
        )
    if not any(cfg.startswith("vulkan") for cfg in embed_keys):
        embed_rows.append(
            "| **VULKAN** | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- |"
        )
    if not any(cfg.startswith("cpu") for cfg in embed_keys):
        embed_rows.append(
            "| **CPU** | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- |"
        )
    embed_table_body = "\n".join(embed_rows)

    # 3. Reranking Table Body
    rerank_rows = []
    for cfg in rerank_keys:
        cfg_label = cfg.upper()
        row = f"| [**{cfg_label}**]({get_cfg_anchor(cfg)}) | {get_test_name(cfg, 'rerank')} | {get_device_setting(cfg, 'rerank')} | {get_special_setting(cfg, 'rerank')} | {val(cfg, 'rerank', 'rerank_time', '.2f', ' ms')} | {val(cfg, 'rerank', 'rerank_token_speed', '.2f', ' tokens/s', bold=(cfg == best_rerank_cfg))} | {val(cfg, 'rerank', 'rerank_throughput', '.2f', ' docs/s')} | {val(cfg, 'rerank', 'gpu_mem_mb', '.1f', ' MB')} | {val(cfg, 'rerank', 'cpu_mem_mb', '.1f', ' MB')} |"
        rerank_rows.append(row)
    if not any(cfg.startswith("hip") for cfg in rerank_keys):
        rerank_rows.append(
            "| **HIP** | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- |"
        )
    if not any(cfg.startswith("vulkan") for cfg in rerank_keys):
        rerank_rows.append(
            "| **VULKAN** | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- |"
        )
    if not any(cfg.startswith("cpu") for cfg in rerank_keys):
        rerank_rows.append(
            "| **CPU** | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- |"
        )
    rerank_table_body = "\n".join(rerank_rows)

    # 4. Speech-to-Text Table Body
    stt_rows = []
    for cfg in stt_keys:
        cfg_label = cfg.upper()
        row = f"| [**{cfg_label}**]({get_cfg_anchor(cfg)}) | {get_test_name(cfg, 'stt')} | {get_device_setting(cfg, 'stt')} | {get_special_setting(cfg, 'stt')} | {val(cfg, 'stt', 'stt_time', '.2f', ' s')} | {val(cfg, 'stt', 'stt_rtf', '.4f')} | {speedup(cfg, 'stt', 'stt_rtf', bold=(cfg == best_stt_cfg))} | {val(cfg, 'stt', 'gpu_mem_mb', '.1f', ' MB')} | {val(cfg, 'stt', 'cpu_mem_mb', '.1f', ' MB')} |"
        stt_rows.append(row)
    if not any(cfg.startswith("hip") for cfg in stt_keys):
        stt_rows.append(
            "| **HIP** | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- |"
        )
    if not any(cfg.startswith("vulkan") for cfg in stt_keys):
        stt_rows.append(
            "| **VULKAN** | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- |"
        )
    if not any(cfg.startswith("cpu") for cfg in stt_keys):
        stt_rows.append(
            "| **CPU** | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- |"
        )
    stt_table_body = "\n".join(stt_rows)

    # 5. Text-to-Speech Table Body
    tts_rows = []
    for cfg in tts_keys:
        cfg_label = cfg.upper()
        row = f"| [**{cfg_label}**]({get_cfg_anchor(cfg)}) | {get_test_name(cfg, 'tts')} | {get_device_setting(cfg, 'tts')} | {get_special_setting(cfg, 'tts')} | {val(cfg, 'tts', 'tts_time', '.2f', ' s')} | {val(cfg, 'tts', 'tts_rtf', '.4f')} | {val(cfg, 'tts', 'tts_char_speed', '.2f', ' chars/s', bold=(cfg == best_tts_cfg))} | {val(cfg, 'tts', 'gpu_mem_mb', '.1f', ' MB')} | {val(cfg, 'tts', 'cpu_mem_mb', '.1f', ' MB')} |"
        tts_rows.append(row)
    if not any(cfg.startswith("hip") for cfg in tts_keys):
        tts_rows.append(
            "| **HIP** | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- |"
        )
    if not any(cfg.startswith("vulkan") for cfg in tts_keys):
        tts_rows.append(
            "| **VULKAN** | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- |"
        )
    if not any(cfg.startswith("cpu") for cfg in tts_keys):
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
    for cfg in image_keys:
        cfg_label = cfg.upper()
        row = f"| [**{cfg_label}**]({get_cfg_anchor(cfg)}) | {get_test_name(cfg, 'image')} | {get_device_setting(cfg, 'image')} | {get_special_setting(cfg, 'image')} | {val(cfg, 'image', 'image_time', '.2f', ' s', bold=(cfg == best_image_cfg))} | {val(cfg, 'image', 'gpu_mem_mb', '.1f', ' MB')} | {val(cfg, 'image', 'cpu_mem_mb', '.1f', ' MB')} |"
        image_rows.append(row)
    if not any(cfg.startswith("hip") for cfg in image_keys):
        image_rows.append(
            "| **HIP** | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- |"
        )
    if not any(cfg.startswith("vulkan") for cfg in image_keys):
        image_rows.append(
            "| **VULKAN** | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- |"
        )
    if not any(cfg.startswith("cpu") for cfg in image_keys):
        image_rows.append(
            "| **CPU** | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- |"
        )
    image_table_body = "\n".join(image_rows)

    # 7. Code Completion Table Body
    comp_rows = []
    for cfg in comp_keys:
        cfg_label = cfg.upper()
        row = f"| [**{cfg_label}**]({get_cfg_anchor(cfg)}) | {get_test_name(cfg, 'completion')} | {get_device_setting(cfg, 'completion')} | {get_special_setting(cfg, 'completion')} | {val(cfg, 'completion', 'comp_avg_ttft', '.2f', ' ms')} | {val(cfg, 'completion', 'comp_avg_prefill', '.2f', ' t/s')} | {val(cfg, 'completion', 'comp_warmup_ttft', '.2f', ' ms')} | {val(cfg, 'completion', 'comp_avg_gen', '.2f', ' t/s', bold=(cfg == best_comp_cfg))} | {val(cfg, 'completion', 'gpu_mem_mb', '.1f', ' MB')} | {val(cfg, 'completion', 'cpu_mem_mb', '.1f', ' MB')} |"
        comp_rows.append(row)
    if not any(cfg.startswith("hip") for cfg in comp_keys):
        comp_rows.append(
            "| **HIP** | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- |"
        )
    if not any(cfg.startswith("vulkan") for cfg in comp_keys):
        comp_rows.append(
            "| **VULKAN** | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- |"
        )
    if not any(cfg.startswith("cpu") for cfg in comp_keys):
        comp_rows.append(
            "| **CPU** | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- | -n.a.- |"
        )
    comp_table_body = "\n".join(comp_rows)

    report = f"""# LLM Caching Optimization Benchmarks

**Benchmark Run Time:** `{now_str}`

## Local Inference Services Benchmarks

We ran local benchmarks for text embedding, text-to-speech (TTS), speech-to-text (STT), document reranking, and image generation on the AMD Radeon RX 7900 XTX hardware target. All services run inside isolated sandboxed environments.

### 📊 Performance Comparison Matrix

#### Text Chat (`local-chat`)
| Configuration | Test Name | GPU | Special Setting | Avg Chat TTFT | Avg Chat Prefill | Chat TTFT (Warmup) | Chat Gen Speed | Avg Chat Gen | Chat Image TTFT | Chat Image Gen | Chat GPU Mem | Chat CPU Mem |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
{chat_table_body}

#### Text Embedding (`local-embedding`)
| Configuration | Test Name | GPU | Special Setting | Embedding Throughput | Embedding Latency (Avg) | Embedding GPU Mem | Embedding CPU Mem |
|---|---|---|---|---|---|---|---|
{embed_table_body}

#### Document Reranking (`local-rerank`)
| Configuration | Test Name | GPU | Special Setting | Avg Reranking Time | Avg Token Speed | Avg Docs Throughput | GPU Mem | CPU Mem |
|---|---|---|---|---|---|---|---|---|
{rerank_table_body}

#### Speech-to-Text (STT) (`local-speech-to-text`)
| Configuration | Test Name | GPU | Special Setting | Avg Transcribe Time | Avg Real-Time Factor (RTF) | Speedup vs Real-time | GPU Mem | CPU Mem |
|---|---|---|---|---|---|---|---|---|
{stt_table_body}

#### Text-to-Speech (TTS) (`local-text-to-speech`)
| Configuration | Test Name | GPU | Special Setting | Avg Synthesis Time | Avg Real-Time Factor (RTF) | Speed (chars/s) | GPU Mem | CPU Mem |
|---|---|---|---|---|---|---|---|---|
{tts_table_body}

#### Image Generation (`local-image`)
| Configuration | Test Name | GPU | Special Setting | Avg Generation Time | GPU Mem | CPU Mem |
|---|---|---|---|---|---|---|
{image_table_body}

#### Code Completion FIM (`local-chat` - tab completion)
| Configuration | Test Name | GPU | Special Setting | Avg Completion TTFT | Avg Prefill Speed | Warmup TTFT | Avg Generation Speed | GPU Mem | CPU Mem |
|---|---|---|---|---|---|---|---|---|---|
{comp_table_body}

---

### ⚙️ Detailed Configuration Reports

"""

    for cfg in sorted(data.keys(), key=sort_config_keys):
        if cfg == "pkg_versions":
            continue
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
- **Package Version:** `{data.get("pkg_versions", {}).get("llama", "unknown")}`
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
- **Package Version:** `{data.get("pkg_versions", {}).get("llama", "unknown")}`
- **Metrics:**
  - Avg Time/Run:         {val(cfg, "embedding", "embed_time_s", ".2f", " s")}
  - Avg Throughput:       {val(cfg, "embedding", "embed_throughput", ".2f", " tokens/sec")}
  - Avg Chunk Latency:    {val(cfg, "embedding", "embed_lat", ".1f", " ms")}
  - Avg Chunk p50:        {val(cfg, "embedding", "embed_p50", ".1f", " ms")}
  - Avg Chunk p95:        {val(cfg, "embedding", "embed_p95", ".1f", " ms")}

"""

        # Completion details
        if "completion" in data[cfg]:
            report += f"""#### Code Completion FIM (`local-chat` - tab completion)
- **Benchmark Test Name:** `{get_test_name(cfg, "completion")}`
- **Device Setting:** `{get_device_setting(cfg, "completion")}`
- **Special Setting:** `{get_special_setting(cfg, "completion")}`
- **Model:** `qwen-coder-fim` (`qwen2.5-coder-1.5b-instruct-q4_k_m.gguf`)
- **Execution Target:** `{cfg_upper}`
- **GPU Memory Used:** {val(cfg, "completion", "gpu_mem_mb", ".1f", " MB")}
- **CPU Memory Used:** {val(cfg, "completion", "cpu_mem_mb", ".1f", " MB")}
- **Benchmark Running Time:** {val(cfg, "completion", "bench_time_s", ".2f", " s")}
- **Active Environment Settings:**
{format_env(cfg, "completion")}
{format_errors(cfg, "completion")}
- **Package Version:** `{data.get("pkg_versions", {}).get("llama", "unknown")}`
- **Warmup (Phase 0):**
  - TTFT (Prefill):       {val(cfg, "completion", "comp_warmup_ttft", ".2f", " ms")}
  - Generation Speed:     {val(cfg, "completion", "comp_warmup_gen", ".2f", " tokens/sec")}
- **Generation (Phase 2):**
  - Avg TTFT (Prefill):   {val(cfg, "completion", "comp_avg_ttft", ".2f", " ms")}
  - Avg Prefill Speed:    {val(cfg, "completion", "comp_avg_prefill", ".2f", " tokens/sec")}
  - Avg Generation Speed: {val(cfg, "completion", "comp_avg_gen", ".2f", " tokens/sec")}
  - Avg Decode Time:      {val(cfg, "completion", "comp_avg_decode", ".2f", " s")}

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
- **Package Version:** `{data.get("pkg_versions", {}).get("llama", "unknown")}`
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
- **Package Version:** `{data.get("pkg_versions", {}).get("whisper", "unknown")}`
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
- **Package Version:** `{data.get("pkg_versions", {}).get("qwen3-tts", "unknown")}`
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
- **Package Version:** `{data.get("pkg_versions", {}).get("stabledifussion", "unknown")}`
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
        default="hip,vulkan,cpu,cpu-blas,special",
        help="Comma-separated list of hardware configurations to test, or 'running' to test already running services (default: hip,vulkan,cpu,cpu-blas,special)",
    )
    parser.add_argument(
        "--services",
        type=str,
        default="chat,completion,embedding,rerank,stt,tts,image",
        help="Comma-separated list of services to test, or 'all' to test all services (default: chat,completion,embedding,rerank,stt,tts,image)",
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
        "--rank",
        action="store_true",
        help="Record and update historical runs per test name in local-benmark-testname-rank.json when overwriting existing values",
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
    parser.add_argument(
        "--use-router",
        action="store_true",
        help="Use the router service URL (http://127.0.0.1:51080) for all services instead of individual ports (useful for --configs running)",
    )

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    router_host = os.environ.get("LROUT_HOST", "127.0.0.1")
    router_port = int(os.environ.get("LROUT_PORT", "51080"))
    router_url = f"http://{router_host}:{router_port}"

    if args.mock:
        # Redirect outputs to scratch directory so we don't overwrite production files during testing
        if args.report == os.path.join(REPO_ROOT, "assistants", "local-benchmark.md"):
            args.report = os.path.join(REPO_ROOT, "scratch", "local-benchmark-mock.md")
        if args.data == os.path.join(REPO_ROOT, "assistants", "local-benchmark.json"):
            args.data = os.path.join(REPO_ROOT, "scratch", "local-benchmark-mock.json")

    target_configs = [c.strip().lower() for c in args.configs.split(",")]
    if args.services.lower() == "all":
        target_services = [
            "chat",
            "embedding",
            "rerank",
            "stt",
            "tts",
            "image",
            "completion",
        ]
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
        is_combi = cfg.endswith("-combi")
        base_cfg = cfg[:-6] if is_combi else cfg

        if base_cfg == "hip":
            for dev in hip_devices_resolved:
                gpu = GLOBAL_GPU_REGISTRY.get_by_device_string(dev)
                if gpu and gpu.is_igpu:
                    print(
                        f"Skipping HIP test for {dev} ({gpu.name}) as it is an unsupported iGPU."
                    )
                    continue
                run_configs.append((cfg, dev))
                if (
                    False
                    and not is_combi
                    and "chat" in target_services
                    and "embedding" in target_services
                ):
                    run_configs.append((f"{cfg}-combi", dev))
        elif base_cfg == "vulkan":
            for dev in vulkan_devices_resolved:
                run_configs.append((cfg, dev))
                if (
                    False
                    and not is_combi
                    and "chat" in target_services
                    and "embedding" in target_services
                ):
                    run_configs.append((f"{cfg}-combi", dev))
        else:
            run_configs.append((cfg, None))
            if (
                False
                and not is_combi
                and "chat" in target_services
                and "embedding" in target_services
            ):
                if cfg != "running":
                    run_configs.append((f"{cfg}-combi", None))

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
            elif run_cfg.endswith("-combi"):
                pass  # Combined configs only support chat and embedding
            else:
                will_execute.add((cache_key, "tts"))

        for sname in target_services:
            if sname == "tts":
                continue
            if sname == "chat" and run_cfg == "special":
                continue
            if sname == "embedding" and run_cfg == "special":
                continue
            if sname in ("rerank", "stt", "image") and (
                run_cfg == "special" or run_cfg.endswith("-combi")
            ):
                continue
            will_execute.add((cache_key, sname))

    cache_file = args.data
    old_data: Dict[str, Dict[str, Dict[str, Any]]] = {}

    if not args.no_cache and os.path.exists(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                old_data = json.load(f)
            print(f"Loaded existing benchmark state from: {cache_file}")
        except Exception as e:
            print(f"Warning: Failed to load benchmark cache: {e}")

    # Use old data only if not executed test on this test run
    benchmark_data: Dict[str, Dict[str, Dict[str, Any]]] = {}
    for cfg in old_data:
        if cfg == "pkg_versions":
            continue
        for sname in old_data[cfg]:
            if "-combi" in cfg and sname not in ("chat", "embedding"):
                continue
            if (cfg, sname) not in will_execute:
                if cfg not in benchmark_data:
                    benchmark_data[cfg] = {}
                benchmark_data[cfg][sname] = old_data[cfg][sname]

    # Gather package versions
    benchmark_data["pkg_versions"] = gather_pkg_versions()  # type: ignore

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
                    llm_n_ctx = 240384
                else:
                    lookup_cfg = run_cfg[:-6] if run_cfg.endswith("-combi") else run_cfg
                    device_map = {
                        "hip": dev if dev else "ROCm0",
                        "vulkan": dev if dev else "Vulkan0",
                        "cpu": "none",
                        "cpu-blas": "BLAS",
                    }
                    llm_device = device_map.get(lookup_cfg, lookup_cfg)

                    # Determine context scaling fraction and context size
                    fraction = 1.0
                    if lookup_cfg.startswith("cpu"):
                        fraction = 0.05
                    elif dev:
                        gpu = GLOBAL_GPU_REGISTRY.get_by_device_string(dev)
                        if gpu and gpu.is_igpu:
                            fraction = 0.20
                    llm_n_ctx = int(
                        os.environ.get("LCHAT_N_CTX", int(240384 * fraction))
                    )

                target_port = (
                    router_port
                    if (args.use_router and run_cfg == "running")
                    else srv["port"]
                )

                if not args.mock:
                    if run_cfg == "running":
                        baseline_vram = 0.0
                        updates = {}
                        is_up = False
                        try:
                            with socket.create_connection(
                                ("127.0.0.1", target_port), timeout=1.0
                            ):
                                is_up = True
                        except Exception:
                            pass
                        if not is_up:
                            port_msg = (
                                f"router on port {target_port}"
                                if args.use_router
                                else f"llama-server on port {target_port}"
                            )
                            print(f"Error: {port_msg} is not running.")
                            set_service_fail_metrics(
                                benchmark_data,
                                cache_key,
                                "chat",
                                "running on host",
                                "unknown",
                                srv["env_file"],
                                [
                                    f"Error: service is not running on port {target_port}"
                                ],
                                {},
                            )
                            continue
                        proc = None
                        master_fd = None

                    else:
                        baseline_vram = get_gpu_memory_mb(llm_device)
                        lookup_cfg = (
                            run_cfg[:-6] if run_cfg.endswith("-combi") else run_cfg
                        )

                        updates = {
                            "LCHAT_DEVICE": llm_device,
                            "LCHAT_N_GPU_LAYERS": 0
                            if lookup_cfg.startswith("cpu")
                            else 999,
                            "LCHAT_N_CTX": llm_n_ctx,
                        }
                        if run_cfg.endswith("-combi"):
                            updates["LMBD_ENABLED"] = "true"
                            updates["LCHAT_EMBEDDING_ENABLED"] = "true"
                            updates["LCHAT_SERVE_EMBEDDINGS"] = "true"
                            updates["LMBD_DEVICE"] = llm_device
                            updates["LMBD_N_GPU_LAYERS"] = (
                                0 if lookup_cfg.startswith("cpu") else 999
                            )
                            if dev and "1" in dev:
                                updates["LMBD_N_CTX"] = 4096
                            else:
                                updates["LMBD_N_CTX"] = 8192
                        else:
                            updates["LMBD_ENABLED"] = "false"
                            updates["LCHAT_EMBEDDING_ENABLED"] = "false"
                            updates["LCHAT_SERVE_EMBEDDINGS"] = "false"

                        hip_vis, cuda_vis = get_visible_devices_env(
                            lookup_cfg, llm_device, hip_devices_resolved
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
                            f"http://127.0.0.1:{target_port}/v1/chat/completions",
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
                        "--skip-image",
                        "--fraction-context",
                        str(fraction),
                        "--format",
                        "json",
                    ]
                    if args.use_router and run_cfg == "running":
                        test_args.extend(["--url", router_url])
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
                                f"Layers: {0 if run_cfg.startswith('cpu') else 999}"
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
                            layers = 999 if not run_cfg.startswith("cpu") else 0
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

                        # In combined mode, run embedding benchmark inside the same running service!
                        if (
                            run_cfg.endswith("-combi")
                            and "embedding" in target_services
                        ):
                            print("Running LLM Embedding benchmark in combined mode...")
                            embed_alias = os.environ.get(
                                "LMBD_ALIAS", "qwen3-embedding"
                            )
                            embed_port = target_port

                            print(
                                "Warming up embedding model (qwen3-embedding) on port {}...".format(
                                    embed_port
                                )
                            )
                            data_ping = json.dumps(
                                {"model": embed_alias, "input": "ping"}
                            ).encode("utf-8")
                            req = urllib.request.Request(
                                f"http://127.0.0.1:{embed_port}/v1/embeddings",
                                data=data_ping,
                                headers={"Content-Type": "application/json"},
                                method="POST",
                            )
                            try:
                                with urllib.request.urlopen(
                                    req, timeout=5.0
                                ) as response:
                                    response.read()
                                    cached = True
                            except Exception:
                                cached = False

                            if not cached:
                                warmup_model(
                                    f"http://127.0.0.1:{embed_port}/v1/embeddings",
                                    {
                                        "model": embed_alias,
                                        "input": "ping",
                                    },
                                    timeout=600,
                                )

                            test_args_embed = [
                                "--benchmark",
                                "--repeat",
                                "1",
                                "--format",
                                "json",
                                "--skip-all-chat",
                            ]
                            if run_cfg.startswith("cpu"):
                                test_args_embed.extend(["--fraction-chunks", "0.1"])
                            if args.use_router and run_cfg == "running":
                                test_args_embed.extend(["--url", router_url])

                            start_time_embed = time.time()
                            stdout_embed, success_embed_run, error_lines_embed = (
                                run_benchmark(
                                    srv["script"], test_args_embed, server_proc=proc
                                )
                            )
                            if not success_embed_run:
                                print(
                                    f"⚠️ Warning: Combined embedding benchmark on config '{cache_key}' failed."
                                )
                                set_service_fail_metrics(
                                    benchmark_data,
                                    cache_key,
                                    "embedding",
                                    "running on host"
                                    if run_cfg == "running"
                                    else (llm_device if llm_device else "Default"),
                                    "unknown"
                                    if run_cfg == "running"
                                    else f"Layers: {0 if run_cfg.startswith('cpu') else 999}",
                                    srv["env_file"],
                                    error_lines_embed,
                                    updates,
                                )
                            else:
                                elapsed_time_embed = time.time() - start_time_embed
                                benchmark_data[cache_key]["embedding"] = (
                                    parse_embed_output(stdout_embed)
                                )
                                benchmark_data[cache_key]["embedding"][
                                    "bench_time_s"
                                ] = elapsed_time_embed
                                benchmark_data[cache_key]["embedding"]["errors"] = (
                                    error_lines_embed
                                )

                                # Measure VRAM and RAM specifically after embedding benchmark runs (now that embedding model is loaded)
                                gpu_mem_mb_embed: Any = "-n.a.-"
                                cpu_mem_mb_embed: Any = "-n.a.-"
                                if run_cfg != "running":
                                    post_run_vram_embed = get_gpu_memory_mb(llm_device)
                                    gpu_mem_mb_embed = max(
                                        0.0, post_run_vram_embed - baseline_vram
                                    )
                                    cpu_mem_mb_embed = get_process_rss_mem_mb(
                                        srv["proc_pattern"]
                                    )

                                benchmark_data[cache_key]["embedding"]["gpu_mem_mb"] = (
                                    gpu_mem_mb_embed
                                )
                                benchmark_data[cache_key]["embedding"]["cpu_mem_mb"] = (
                                    cpu_mem_mb_embed
                                )
                                benchmark_data[cache_key]["embedding"]["test_name"] = (
                                    f"embedding_{cache_key}"
                                )
                                benchmark_data[cache_key]["embedding"][
                                    "device_setting"
                                ] = (
                                    "running on host"
                                    if run_cfg == "running"
                                    else (llm_device if llm_device else "Default")
                                )
                                benchmark_data[cache_key]["embedding"][
                                    "special_setting"
                                ] = (
                                    "unknown"
                                    if run_cfg == "running"
                                    else f"Layers: {999 if run_cfg != 'cpu' else 0}"
                                )
                                env_dict_embed = read_env_file(srv["env_file"])
                                env_dict_embed.update(updates)
                                benchmark_data[cache_key]["embedding"]["env"] = (
                                    env_dict_embed
                                )
                                if (
                                    run_cfg != "running"
                                    and llm_device in available_devices
                                ):
                                    benchmark_data[cache_key]["embedding"][
                                        "device_details"
                                    ] = available_devices[llm_device]
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
                            if run_cfg.startswith("cpu")
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
                                else (
                                    "Vulkan0"
                                    if run_cfg == "vulkan"
                                    else (
                                        "BLAS"
                                        if run_cfg == "cpu-blas"
                                        else ("none" if run_cfg == "cpu" else "Default")
                                    )
                                )
                            )
                        )
                        layers = 999 if not run_cfg.startswith("cpu") else 0
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
                        lookup_cfg = (
                            run_cfg[:-6] if run_cfg.endswith("-combi") else run_cfg
                        )
                        mock_updates = {
                            "LCHAT_DEVICE": dev
                            if dev
                            else (
                                "ROCm0"
                                if lookup_cfg == "hip"
                                else (
                                    "Vulkan0"
                                    if lookup_cfg == "vulkan"
                                    else (
                                        "BLAS"
                                        if lookup_cfg == "cpu-blas"
                                        else ("none" if lookup_cfg == "cpu" else "")
                                    )
                                )
                            ),
                            "LCHAT_N_GPU_LAYERS": "999"
                            if not lookup_cfg.startswith("cpu")
                            else "0",
                            "LCHAT_N_CTX": str(llm_n_ctx),
                        }
                        if run_cfg.endswith("-combi"):
                            mock_updates["LMBD_ENABLED"] = "true"
                            mock_updates["LCHAT_EMBEDDING_ENABLED"] = "true"
                            mock_updates["LCHAT_SERVE_EMBEDDINGS"] = "true"
                        else:
                            mock_updates["LMBD_ENABLED"] = "false"
                            mock_updates["LCHAT_EMBEDDING_ENABLED"] = "false"
                            mock_updates["LCHAT_SERVE_EMBEDDINGS"] = "false"
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

                        if (
                            run_cfg.endswith("-combi")
                            and "embedding" in target_services
                        ):
                            mock_out_embed = get_mock_output("embedding", run_cfg)
                            benchmark_data[cache_key]["embedding"] = parse_embed_output(
                                mock_out_embed
                            )
                            benchmark_data[cache_key]["embedding"]["bench_time_s"] = 1.0
                            benchmark_data[cache_key]["embedding"]["errors"] = []
                            benchmark_data[cache_key]["embedding"]["gpu_mem_mb"] = (
                                get_mock_gpu_mem("embedding", run_cfg)
                            )
                            benchmark_data[cache_key]["embedding"]["cpu_mem_mb"] = (
                                get_mock_cpu_mem("embedding", run_cfg)
                            )
                            benchmark_data[cache_key]["embedding"]["test_name"] = (
                                f"embedding_{cache_key}"
                            )
                            benchmark_data[cache_key]["embedding"]["device_setting"] = (
                                dev_details.get("device_id", "Default")
                            )
                            benchmark_data[cache_key]["embedding"][
                                "special_setting"
                            ] = f"Layers: {999 if not run_cfg.startswith('cpu') else 0}"
                            try:
                                env_dict_embed = read_env_file(srv["env_file"])
                            except Exception:
                                env_dict_embed = {}
                            env_dict_embed.update(mock_updates)
                            benchmark_data[cache_key]["embedding"]["env"] = (
                                env_dict_embed
                            )
                            benchmark_data[cache_key]["embedding"]["device_details"] = (
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
            elif run_cfg.endswith("-combi"):
                print("Skipping separate Embedding service for Combined config.")
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
                        "cpu": "none",
                        "cpu-blas": "BLAS",
                    }
                    embed_device = device_map.get(run_cfg, run_cfg)

                target_port = (
                    router_port
                    if (args.use_router and run_cfg == "running")
                    else srv["port"]
                )

                if not args.mock:
                    if run_cfg == "running":
                        baseline_vram = 0.0
                        updates = {}
                        is_up = False
                        try:
                            with socket.create_connection(
                                ("127.0.0.1", target_port), timeout=1.0
                            ):
                                is_up = True
                        except Exception:
                            pass
                        if not is_up:
                            port_msg = (
                                f"router on port {target_port}"
                                if args.use_router
                                else f"llama-server on port {target_port}"
                            )
                            print(f"Error: {port_msg} is not running.")
                            set_service_fail_metrics(
                                benchmark_data,
                                cache_key,
                                "embedding",
                                "running on host",
                                "unknown",
                                srv["env_file"],
                                [
                                    f"Error: service is not running on port {target_port}"
                                ],
                                {},
                            )
                            continue
                        proc = None
                        master_fd = None

                    else:
                        baseline_vram = get_gpu_memory_mb(embed_device)

                        updates = {
                            "LMBD_DEVICE": embed_device,
                            "LMBD_N_GPU_LAYERS": 0
                            if run_cfg.startswith("cpu")
                            else 999,
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
                        if not wait_for_port(srv["port"], timeout=180, proc=proc):
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
                        # Send a quick warmup request with a 5-second timeout to check if shaders are cached
                        data = json.dumps(
                            {"model": "qwen3-embedding", "input": "ping"}
                        ).encode("utf-8")
                        req = urllib.request.Request(
                            f"http://127.0.0.1:{target_port}/v1/embeddings",
                            data=data,
                            headers={"Content-Type": "application/json"},
                            method="POST",
                        )

                        try:
                            with urllib.request.urlopen(req, timeout=5.0) as response:
                                response.read()
                                cached = True
                        except Exception:
                            cached = False

                        if not cached:
                            print(
                                "⚠️ Shaders needed for this test are not in the cache. Generating shaders now (this will take time)..."
                            )
                            # Wait for up to 10 minutes (600 seconds) for shader compilation to finish
                            success = warmup_model(
                                f"http://127.0.0.1:{target_port}/v1/embeddings",
                                {
                                    "model": "qwen3-embedding",
                                    "input": "ping",
                                },
                                timeout=600,
                            )
                        else:
                            success = True

                        if not success:
                            print(
                                "⚠️ Warning: Model warmup timed out after 10 minutes. Benchmark might fail."
                            )
                    test_args = [
                        "--benchmark",
                        "--repeat",
                        "1",
                        "--format",
                        "json",
                        "--skip-chat",
                    ]
                    if run_cfg.startswith("cpu"):
                        test_args.extend(["--fraction-chunks", "0.1"])
                    if args.use_router and run_cfg == "running":
                        test_args.extend(["--url", router_url])
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
                            else f"Layers: {0 if run_cfg.startswith('cpu') else 999}",
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
                                    else (
                                        "BLAS"
                                        if run_cfg == "cpu-blas"
                                        else ("none" if run_cfg == "cpu" else "Default")
                                    )
                                )
                            )
                        )
                        benchmark_data[cache_key]["embedding"]["special_setting"] = (
                            f"Layers: {999 if not run_cfg.startswith('cpu') else 0}"
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
                                else (
                                    "Vulkan0"
                                    if run_cfg == "vulkan"
                                    else (
                                        "BLAS"
                                        if run_cfg == "cpu-blas"
                                        else ("none" if run_cfg == "cpu" else "")
                                    )
                                )
                            ),
                            "LMBD_N_GPU_LAYERS": "999"
                            if not run_cfg.startswith("cpu")
                            else "0",
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
        # 1.8 Code Completion Service
        # ---------------------------------------------------------
        if "completion" in target_services:
            srv = SERVICES["completion"]
            if run_cfg == "special":
                print("Skipping Code Completion for Special configuration.")
            else:
                if run_cfg != "running":
                    print(f"Preparing environment file: {srv['env_file']}")
                proc = None
                master_fd = None
                baseline_vram = 0.0

                # Determine configuration settings for current config
                if run_cfg == "running":
                    comp_device = "running on host"
                    fraction = 1.0
                else:
                    lookup_cfg = run_cfg[:-6] if run_cfg.endswith("-combi") else run_cfg
                    device_map = {
                        "hip": dev if dev else "ROCm0",
                        "vulkan": dev if dev else "Vulkan0",
                        "cpu": "none",
                        "cpu-blas": "BLAS",
                    }
                    comp_device = device_map.get(lookup_cfg, lookup_cfg)

                    fraction = 1.0
                    if lookup_cfg.startswith("cpu"):
                        fraction = 0.05
                    elif dev:
                        gpu = GLOBAL_GPU_REGISTRY.get_by_device_string(dev)
                        if gpu and gpu.is_igpu:
                            fraction = 0.20

                target_port = (
                    router_port
                    if (args.use_router and run_cfg == "running")
                    else srv["port"]
                )

                if not args.mock:
                    if run_cfg == "running":
                        baseline_vram = 0.0
                        updates = {}
                        is_up = False
                        try:
                            with socket.create_connection(
                                ("127.0.0.1", target_port), timeout=1.0
                            ):
                                is_up = True
                        except Exception:
                            pass
                        if not is_up:
                            port_msg = (
                                f"router on port {target_port}"
                                if args.use_router
                                else f"llama-server on port {target_port}"
                            )
                            print(f"Error: {port_msg} is not running.")
                            set_service_fail_metrics(
                                benchmark_data,
                                cache_key,
                                "completion",
                                "running on host",
                                "unknown",
                                srv["env_file"],
                                [
                                    f"Error: service is not running on port {target_port}"
                                ],
                                {},
                            )
                            continue
                        proc = None
                        master_fd = None

                    else:
                        baseline_vram = get_gpu_memory_mb(comp_device)
                        lookup_cfg = (
                            run_cfg[:-6] if run_cfg.endswith("-combi") else run_cfg
                        )

                        # Enable completion model, disable embedding (unless combi)
                        updates = {
                            "LCOMP_DEVICE": comp_device,
                            "LCOMP_ENABLED": "true",
                            "LCOMP_N_GPU_LAYERS": 0
                            if lookup_cfg.startswith("cpu")
                            else 999,
                            "LMBD_ENABLED": "false",
                            "LCHAT_EMBEDDING_ENABLED": "false",
                            "LCHAT_SERVE_EMBEDDINGS": "false",
                        }
                        if run_cfg.endswith("-combi"):
                            updates["LMBD_ENABLED"] = "true"
                            updates["LCHAT_EMBEDDING_ENABLED"] = "true"
                            updates["LCHAT_SERVE_EMBEDDINGS"] = "true"
                            updates["LMBD_DEVICE"] = comp_device
                            updates["LMBD_N_GPU_LAYERS"] = (
                                0 if lookup_cfg.startswith("cpu") else 999
                            )
                            if dev and "1" in dev:
                                updates["LMBD_N_CTX"] = 4096
                            else:
                                updates["LMBD_N_CTX"] = 8192

                        hip_vis, cuda_vis = get_visible_devices_env(
                            lookup_cfg, comp_device, hip_devices_resolved
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
                                "completion",
                                srv["port"],
                                srv["proc_pattern"],
                                proc,
                                master_fd,
                            )
                            set_service_fail_metrics(
                                benchmark_data,
                                cache_key,
                                "completion",
                                comp_device if comp_device else "Default",
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

                # Run benchmarks
                print("Running Code Completion benchmark")
                if not args.mock:
                    if run_cfg != "running":
                        print("Warming up completion model (qwen-coder-fim)...")
                        if not warmup_model(
                            f"http://127.0.0.1:{target_port}/v1/completions",
                            {
                                "model": "qwen-coder-fim",
                                "prompt": "<|fim_prefix|>def add(a, b):\n    <|fim_suffix|>\n    return c<|fim_middle|>",
                                "max_tokens": 1,
                            },
                        ):
                            print(
                                "⚠️ Warning: Model warmup timed out. Benchmark might fail."
                            )
                    repeats_scaled = int(30 * fraction)
                    if repeats_scaled < 1:
                        repeats_scaled = 1
                    test_args = [
                        "--benchmark",
                        "--repeat",
                        str(repeats_scaled),
                        "--format",
                        "json",
                    ]
                    if args.use_router and run_cfg == "running":
                        test_args.extend(["--url", router_url])
                    start_time = time.time()
                    bench_start_time_str = datetime.datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                    stdout, success, error_lines = run_benchmark(
                        srv["script"], test_args, server_proc=proc
                    )

                    if not success:
                        print(
                            f"⚠️ Warning: Benchmark command for completion on config '{cache_key}' failed."
                        )
                        if run_cfg == "running":
                            journal_errors = get_journal_errors(
                                "local-chat", bench_start_time_str
                            )
                            error_lines.extend(journal_errors)
                        set_service_fail_metrics(
                            benchmark_data,
                            cache_key,
                            "completion",
                            "running on host"
                            if run_cfg == "running"
                            else (comp_device if comp_device else "Default"),
                            "unknown"
                            if run_cfg == "running"
                            else f"Layers: {0 if run_cfg.startswith('cpu') else 999}",
                            srv["env_file"],
                            error_lines,
                            updates,
                        )
                    else:
                        elapsed_time = time.time() - start_time
                        benchmark_data[cache_key]["completion"] = parse_comp_output(
                            stdout
                        )
                        benchmark_data[cache_key]["completion"]["bench_time_s"] = (
                            elapsed_time
                        )
                        if run_cfg == "running":
                            journal_errors = get_journal_errors(
                                "local-chat", bench_start_time_str
                            )
                            error_lines.extend(journal_errors)
                        if error_lines:
                            benchmark_data[cache_key]["completion"]["errors"] = (
                                error_lines
                            )

                        # Measure resources if running
                        rss_mb = get_process_rss_mem_mb(srv["proc_pattern"])
                        gpu_mb = (
                            get_gpu_memory_mb(comp_device)
                            if run_cfg != "running"
                            else 0.0
                        )
                        benchmark_data[cache_key]["completion"]["gpu_mem_mb"] = gpu_mb
                        benchmark_data[cache_key]["completion"]["cpu_mem_mb"] = rss_mb
                        benchmark_data[cache_key]["completion"]["test_name"] = (
                            f"completion_{cache_key}"
                        )
                        benchmark_data[cache_key]["completion"]["device_setting"] = (
                            "running on host"
                            if run_cfg == "running"
                            else (comp_device if comp_device else "Default")
                        )
                        benchmark_data[cache_key]["completion"]["special_setting"] = (
                            "unknown"
                            if run_cfg == "running"
                            else f"Layers: {999 if not run_cfg.startswith('cpu') else 0}"
                        )
                        env_dict = read_env_file(srv["env_file"])
                        env_dict.update(updates)
                        benchmark_data[cache_key]["completion"]["env"] = env_dict
                        if run_cfg != "running" and comp_device in available_devices:
                            benchmark_data[cache_key]["completion"][
                                "device_details"
                            ] = available_devices[comp_device]
                else:
                    stdout = get_mock_output("completion", run_cfg)
                    benchmark_data[cache_key]["completion"] = parse_comp_output(stdout)
                    benchmark_data[cache_key]["completion"]["errors"] = []

                    if run_cfg == "running":
                        benchmark_data[cache_key]["completion"]["gpu_mem_mb"] = "-n.a.-"
                        benchmark_data[cache_key]["completion"]["cpu_mem_mb"] = "-n.a.-"
                        benchmark_data[cache_key]["completion"]["device_setting"] = (
                            "running on host"
                        )
                        benchmark_data[cache_key]["completion"]["special_setting"] = (
                            "unknown"
                        )
                    else:
                        benchmark_data[cache_key]["completion"]["gpu_mem_mb"] = (
                            get_mock_gpu_mem("completion", run_cfg)
                        )
                        benchmark_data[cache_key]["completion"]["cpu_mem_mb"] = (
                            get_mock_cpu_mem("completion", run_cfg)
                        )
                        benchmark_data[cache_key]["completion"]["device_setting"] = (
                            dev
                            if dev
                            else (
                                "ROCm0"
                                if run_cfg == "hip"
                                else (
                                    "Vulkan0"
                                    if run_cfg == "vulkan"
                                    else (
                                        "BLAS"
                                        if run_cfg == "cpu-blas"
                                        else ("none" if run_cfg == "cpu" else "Default")
                                    )
                                )
                            )
                        )
                        benchmark_data[cache_key]["completion"]["special_setting"] = (
                            f"Layers: {999 if not run_cfg.startswith('cpu') else 0}"
                        )

                    benchmark_data[cache_key]["completion"]["bench_time_s"] = 12.5
                    benchmark_data[cache_key]["completion"]["test_name"] = (
                        f"completion_{cache_key}"
                    )

                    if run_cfg == "running":
                        mock_updates = {}
                    else:
                        mock_updates = {
                            "LCOMP_DEVICE": dev
                            if dev
                            else (
                                "ROCm0"
                                if run_cfg == "hip"
                                else (
                                    "Vulkan0"
                                    if run_cfg == "vulkan"
                                    else (
                                        "BLAS"
                                        if run_cfg == "cpu-blas"
                                        else ("none" if run_cfg == "cpu" else "")
                                    )
                                )
                            ),
                            "LCOMP_N_GPU_LAYERS": "999"
                            if not run_cfg.startswith("cpu")
                            else "0",
                        }
                    try:
                        env_dict = read_env_file(srv["env_file"])
                    except Exception:
                        env_dict = {}
                    env_dict.update(mock_updates)
                    benchmark_data[cache_key]["completion"]["env"] = env_dict

                    if run_cfg != "running":
                        comp_device = (
                            dev
                            if dev
                            else (
                                "ROCm0"
                                if run_cfg == "hip"
                                else ("Vulkan0" if run_cfg == "vulkan" else "")
                            )
                        )
                        dev_details = available_devices.get(comp_device, {})
                        if not dev_details:
                            dev_details = {
                                "device_id": comp_device,
                                "name": "AMD Radeon RX 7900 XTX"
                                if "0" in comp_device
                                else "AMD Radeon Graphics",
                                "total_mem_mib": 24576.0
                                if "0" in comp_device
                                else 56261.0,
                                "free_mem_mib": 24000.0
                                if "0" in comp_device
                                else 92380.0,
                            }
                        benchmark_data[cache_key]["completion"]["device_details"] = (
                            dev_details
                        )

                # Stop service
                if not args.mock and run_cfg != "running":
                    stop_service(
                        "completion",
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
            elif run_cfg.endswith("-combi"):
                print("Skipping separate Reranker for Combined config.")
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
                        "cpu": "none",
                        "cpu-blas": "BLAS",
                    }
                    lrr_device = device_map.get(run_cfg, run_cfg)

                target_port = (
                    router_port
                    if (args.use_router and run_cfg == "running")
                    else srv["port"]
                )

                if not args.mock:
                    if run_cfg == "running":
                        baseline_vram = 0.0
                        updates = {}
                        is_up = False
                        try:
                            with socket.create_connection(
                                ("127.0.0.1", target_port), timeout=1.0
                            ):
                                is_up = True
                        except Exception:
                            pass
                        if not is_up:
                            port_msg = (
                                f"router on port {target_port}"
                                if args.use_router
                                else f"reranker on port {target_port}"
                            )
                            print(f"Error: {port_msg} is not running.")
                            set_service_fail_metrics(
                                benchmark_data,
                                cache_key,
                                "rerank",
                                "running on host",
                                "unknown",
                                srv["env_file"],
                                [
                                    f"Error: service is not running on port {target_port}"
                                ],
                                {},
                            )
                            continue
                        proc = None
                        master_fd = None

                    else:
                        baseline_vram = get_gpu_memory_mb(lrr_device)
                        rr_env = read_env_file(srv["env_file"])
                        lrr_engine = rr_env.get("LRR_ENGINE", "llama")
                        lrr_alias = rr_env.get("LRR_ALIAS", "qwen3-reranker")
                        updates = {
                            "LRR_DEVICE": lrr_device,
                            "LRR_N_GPU_LAYERS": 0 if run_cfg.startswith("cpu") else 99,
                            "LRR_ENGINE": lrr_engine,
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
                        warmup_endpoint = (
                            "/rerank" if lrr_engine == "tei" else "/v1/rerank"
                        )
                        warmup_field = "texts" if lrr_engine == "tei" else "documents"
                        print(f"Warming up reranker model ({lrr_alias})...")
                        if not warmup_model(
                            f"http://127.0.0.1:{target_port}{warmup_endpoint}",
                            {
                                "model": lrr_alias,
                                "query": "ping",
                                warmup_field: ["ping"],
                            },
                        ):
                            print(
                                "⚠️ Warning: Model warmup timed out. Benchmark might fail."
                            )
                    rerank_test_args = [
                        "--benchmark",
                        "--repeat",
                        "1",
                        "--format",
                        "json",
                    ]
                    if args.use_router and run_cfg == "running":
                        rerank_test_args.extend(["--url", router_url])
                    start_time = time.time()
                    bench_start_time_str = datetime.datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                    stdout, success, error_lines = run_benchmark(
                        srv["script"],
                        rerank_test_args,
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
                                    else (
                                        "BLAS"
                                        if run_cfg == "cpu-blas"
                                        else ("none" if run_cfg == "cpu" else "Default")
                                    )
                                )
                            )
                        )
                        benchmark_data[cache_key]["rerank"]["special_setting"] = (
                            f"Layers: {99 if not run_cfg.startswith('cpu') else 0}"
                        )

                    benchmark_data[cache_key]["rerank"]["bench_time_s"] = 8.7
                    benchmark_data[cache_key]["rerank"]["test_name"] = (
                        f"rerank_{cache_key}"
                    )

                    if run_cfg == "running":
                        mock_updates = {}
                    else:
                        try:
                            mock_rr_env = read_env_file(srv["env_file"])
                            mock_lrr_engine = mock_rr_env.get("LRR_ENGINE", "llama")
                        except Exception:
                            mock_lrr_engine = "llama"
                        mock_updates = {
                            "LRR_DEVICE": dev
                            if dev
                            else (
                                "ROCm0"
                                if run_cfg == "hip"
                                else (
                                    "Vulkan0"
                                    if run_cfg == "vulkan"
                                    else (
                                        "BLAS"
                                        if run_cfg == "cpu-blas"
                                        else ("none" if run_cfg == "cpu" else "")
                                    )
                                )
                            ),
                            "LRR_N_GPU_LAYERS": "99"
                            if not run_cfg.startswith("cpu")
                            else "0",
                            "LRR_ENGINE": mock_lrr_engine,
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
            elif run_cfg.endswith("-combi"):
                print("Skipping STT for Combined config.")
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

                target_port = (
                    router_port
                    if (args.use_router and run_cfg == "running")
                    else srv["port"]
                )

                if not args.mock:
                    if run_cfg == "running":
                        baseline_vram = 0.0
                        updates = {}
                        is_up = False
                        try:
                            with socket.create_connection(
                                ("127.0.0.1", target_port), timeout=1.0
                            ):
                                is_up = True
                        except Exception:
                            pass
                        if not is_up:
                            port_msg = (
                                f"router on port {target_port}"
                                if args.use_router
                                else f"whisper-server on port {target_port}"
                            )
                            print(f"Error: {port_msg} is not running.")
                            set_service_fail_metrics(
                                benchmark_data,
                                cache_key,
                                "stt",
                                "running on host",
                                "unknown",
                                srv["env_file"],
                                [
                                    f"Error: service is not running on port {target_port}"
                                ],
                                {},
                            )
                            continue
                        proc = None
                        master_fd = None

                    else:
                        baseline_vram = get_gpu_memory_mb(stt_device)

                        if run_cfg in ("vulkan", "hip") and dev:
                            idx_match = re.search(r"\d+", dev)
                            lstt_device = idx_match.group(0) if idx_match else "0"
                        elif run_cfg == "cpu-blas":
                            lstt_device = "BLAS"
                        elif run_cfg == "cpu":
                            lstt_device = "none"
                        else:
                            lstt_device = ""

                        # whisper-server requires integer device IDs.
                        # For CPU runs, LSTT_DEVICE must be empty.
                        env_device = "" if run_cfg.startswith("cpu") else lstt_device

                        updates = {
                            "LSTT_DEVICE": env_device,
                            "LSTT_NO_GPU": "true"
                            if run_cfg.startswith("cpu")
                            else "false",
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
                    stt_test_args = ["--benchmark", "--repeat", "1", "--format", "json"]
                    if args.use_router and run_cfg == "running":
                        stt_test_args.extend(["--url", router_url])
                    start_time = time.time()
                    bench_start_time_str = datetime.datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                    stdout, success, error_lines = run_benchmark(
                        srv["script"],
                        stt_test_args,
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

                        expected_stt_text = (
                            "As campaigns go, the one in 1892 was not a particularly exciting one. "
                            "Both candidates had already served a term in the White House. "
                            "Cleveland from 1884 to 1888, Harrison succeeding him and running now for re-election. "
                            "Both men were well known to the voters. It was a time of industrial expansi"
                        )
                        stt_actual_text = benchmark_data[cache_key]["stt"].get(
                            "stt_text", ""
                        )
                        if not check_text_match(
                            stt_actual_text, expected_stt_text, min_words_match=20
                        ):
                            error_lines.append(
                                "Warning: STT Transcription text mismatch (garbled output)"
                            )
                            success = False
                            benchmark_data[cache_key]["stt"]["errors"] = error_lines
                            # Update metric with FAIL
                            benchmark_data[cache_key]["stt"]["stt_time"] = (
                                "-fail- VALIDATION"
                            )
                            benchmark_data[cache_key]["stt"]["stt_rtf"] = (
                                "-fail- VALIDATION"
                            )

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
                            else ("No GPU" if run_cfg.startswith("cpu") else "Use GPU")
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
                            mock_lstt_dev = (
                                (
                                    "none"
                                    if run_cfg == "cpu"
                                    else (
                                        "BLAS" if run_cfg == "cpu-blas" else "Default"
                                    )
                                )
                                if run_cfg.startswith("cpu")
                                else "0"
                            )

                        benchmark_data[cache_key]["stt"]["device_setting"] = (
                            "0"
                            if not run_cfg.startswith("cpu")
                            and mock_lstt_dev not in ("none", "BLAS", "Default")
                            else mock_lstt_dev
                        )
                        benchmark_data[cache_key]["stt"]["special_setting"] = (
                            "No GPU" if run_cfg.startswith("cpu") else "Use GPU"
                        )

                    benchmark_data[cache_key]["stt"]["bench_time_s"] = 5.3
                    benchmark_data[cache_key]["stt"]["test_name"] = f"stt_{cache_key}"

                    if run_cfg == "running":
                        mock_updates = {}
                    else:
                        mock_updates = {
                            "LSTT_DEVICE": mock_lstt_dev
                            if not run_cfg.startswith("cpu")
                            else mock_lstt_dev,
                            "LSTT_NO_GPU": "false"
                            if not run_cfg.startswith("cpu")
                            else "true",
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
            if run_cfg.endswith("-combi"):
                print("Skipping TTS for Combined config.")
                tts_modes_to_test: List[Tuple[str, str, str]] = []
            elif run_cfg == "special":
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
                ltts_mode = "cpu" if run_cfg.startswith("cpu") else "gpu"
                ltts_device = (
                    "BLAS"
                    if run_cfg == "cpu-blas"
                    else ("none" if run_cfg == "cpu" else (dev if dev else run_cfg))
                )
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
                target_port = (
                    router_port
                    if (args.use_router and run_cfg == "running")
                    else srv["port"]
                )

                if not args.mock:
                    if run_cfg == "running":
                        baseline_vram = 0.0
                        updates = {}
                        is_up = False
                        try:
                            with socket.create_connection(
                                ("127.0.0.1", target_port), timeout=1.0
                            ):
                                is_up = True
                        except Exception:
                            pass
                        if not is_up:
                            port_msg = (
                                f"router on port {target_port}"
                                if args.use_router
                                else f"qwen3-tts-server on port {target_port}"
                            )
                            print(f"Error: {port_msg} is not running.")
                            set_service_fail_metrics(
                                benchmark_data,
                                data_key,
                                "tts",
                                "running on host",
                                "unknown",
                                srv["env_file"],
                                [
                                    f"Error: service is not running on port {target_port}"
                                ],
                                {},
                            )
                            continue
                        proc = None
                        master_fd = None

                    else:
                        baseline_vram = get_gpu_memory_mb(ltts_device)

                        # Self-healing check: check if qwen3-tts-server supports --device
                        try:
                            qwen3_tts_server = os.getenv(
                                "QWEN3_TTS_SERVER_BIN", "qwen3-tts-server"
                            )
                            res = subprocess.run(
                                [qwen3_tts_server, "--help"],
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
                    tts_test_args = ["--benchmark", "--repeat", "1", "--format", "json"]
                    if args.use_router and run_cfg == "running":
                        tts_test_args.extend(["--url", router_url])
                    start_time = time.time()
                    bench_start_time_str = datetime.datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                    stdout, success, error_lines = run_benchmark(
                        srv["script"],
                        tts_test_args,
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

                        expected_tts_text = (
                            "The quick brown fox jumps over the lazy dog. This sentence has exactly 45 words "
                            "to verify that the speech generation pipeline functions correctly. The generated audio file is "
                            "sent to local speech to text service to measure synthesis performance of its audio system."
                        )
                        print("Validating TTS audio with STT...")
                        whisper_cli = os.getenv("WHISPER_CLI_BIN", "whisper-cli")
                        val_cmd = [
                            os.path.join(
                                os.path.dirname(srv["script"]),
                                "local-speech-to-text.sh",
                            ),
                        ]
                        for k, v in os.environ.items():
                            if k.upper().startswith(
                                ("LLAMA_", "WHISPER_", "QWEN3_", "SD_", "GGML_")
                            ):
                                val_cmd.extend(["--env", f"{k}={v}"])
                        val_cmd.extend(
                            [
                                "run",
                                whisper_cli,
                                "-m",
                                "/data/public/machine-learning/models/speech-to-text/ggml-large-v3-turbo-q5_0.bin",
                                "-f",
                                os.path.join(
                                    REPO_ROOT, "scratch", "tts_benchmark_output.wav"
                                ),
                                "-nt",
                                "-ng",
                            ]
                        )
                        tts_val_proc = subprocess.run(
                            val_cmd,
                            capture_output=True,
                            text=True,
                        )
                        if tts_val_proc.returncode != 0:
                            error_lines.append(
                                "Warning: TTS Audio validation failed (STT process error)"
                            )
                            success = False
                            benchmark_data[data_key]["tts"]["errors"] = error_lines
                            benchmark_data[data_key]["tts"]["tts_duration"] = (
                                "-fail- VALIDATION"
                            )
                            benchmark_data[data_key]["tts"]["tts_time"] = (
                                "-fail- VALIDATION"
                            )
                        else:
                            if not check_text_match(
                                tts_val_proc.stdout,
                                expected_tts_text,
                                min_words_match=12,
                            ):
                                error_lines.append(
                                    "Warning: TTS Audio validation failed (garbled audio output)"
                                )
                                success = False
                                benchmark_data[data_key]["tts"]["errors"] = error_lines
                                benchmark_data[data_key]["tts"]["tts_duration"] = (
                                    "-fail- VALIDATION"
                                )
                                benchmark_data[data_key]["tts"]["tts_time"] = (
                                    "-fail- VALIDATION"
                                )

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
                        if not dev_details and ltts_device not in (
                            "cpu",
                            "BLAS",
                            "none",
                        ):
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
            elif run_cfg.endswith("-combi"):
                print("Skipping Image for Combined config.")
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
                    if run_cfg.startswith("cpu"):
                        img_backend = "cpu"
                    else:
                        target_dev = dev if dev else "vulkan1"
                        gpu = GLOBAL_GPU_REGISTRY.get_by_device_string(target_dev)
                        if run_cfg == "hip" or run_cfg == "special":
                            idx = (
                                gpu.rocm_index
                                if gpu and gpu.rocm_index is not None
                                else 0
                            )
                            img_backend = f"rocm{idx}"
                        else:
                            idx = (
                                gpu.vulkan_index
                                if gpu and gpu.vulkan_index is not None
                                else 1
                            )
                            img_backend = f"vulkan{idx}"
                            if gpu and gpu.is_igpu:
                                img_backend += (
                                    ",te=cpu"  # offload text encoder for iGPU
                                )

                target_port = (
                    router_port
                    if (args.use_router and run_cfg == "running")
                    else srv["port"]
                )

                if not args.mock:
                    if run_cfg == "running":
                        baseline_vram = 0.0
                        updates = {}
                        is_up = False
                        try:
                            with socket.create_connection(
                                ("127.0.0.1", target_port), timeout=1.0
                            ):
                                is_up = True
                        except Exception:
                            pass
                        if not is_up:
                            port_msg = (
                                f"router on port {target_port}"
                                if args.use_router
                                else f"sd-server on port {target_port}"
                            )
                            print(f"Error: {port_msg} is not running.")
                            set_service_fail_metrics(
                                benchmark_data,
                                cache_key,
                                "image",
                                "running on host",
                                "unknown",
                                srv["env_file"],
                                [
                                    f"Error: service is not running on port {target_port}"
                                ],
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
                    image_test_args = [
                        "--benchmark",
                        "--repeat",
                        "1",
                        "--format",
                        "json",
                    ]
                    if args.use_router and run_cfg == "running":
                        image_test_args.extend(["--url", router_url])
                    start_time = time.time()
                    bench_start_time_str = datetime.datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                    stdout, success, error_lines = run_benchmark(
                        srv["script"],
                        image_test_args,
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

    # Write historical rank files if requested and not checking clean cache
    if not args.no_cache and args.rank:
        print("\n📈 Recording benchmark rank histories...")
        old_mtime = (
            int(os.path.getmtime(cache_file))
            if os.path.exists(cache_file)
            else int(time.time() - 60)
        )
        old_pkg_versions = old_data.get("pkg_versions", {})
        new_pkg_versions = benchmark_data.get("pkg_versions", {})

        for cfg, sname in sorted(will_execute):
            if cfg in old_data and sname in old_data[cfg]:
                # We have an overwrite!
                test_name = None
                if (
                    cfg in benchmark_data
                    and sname in benchmark_data[cfg]
                    and "test_name" in benchmark_data[cfg][sname]
                ):
                    test_name = benchmark_data[cfg][sname]["test_name"]
                elif (
                    cfg in old_data
                    and sname in old_data[cfg]
                    and "test_name" in old_data[cfg][sname]
                ):
                    test_name = old_data[cfg][sname]["test_name"]

                if not test_name:
                    fallback_names = {
                        "chat": "chat",
                        "embedding": "embedding",
                        "rerank": "rerank",
                        "stt": "stt",
                        "tts": "tts",
                        "image": "image",
                    }
                    base = fallback_names.get(sname, sname)
                    test_name = f"{base}_{cfg}"

                rank_filename = f"local-benmark-{test_name}-rank.json"
                rank_path = os.path.join(os.path.dirname(cache_file), rank_filename)

                runs = []
                if os.path.exists(rank_path):
                    try:
                        with open(rank_path, "r", encoding="utf-8") as rf:
                            runs = json.load(rf)
                    except Exception as e:
                        print(f"Warning: Failed to load rank file {rank_filename}: {e}")

                def is_duplicate(e1, e2):
                    r1 = {
                        k: v
                        for k, v in e1.get("results", {}).items()
                        if k != "bench_time_s"
                    }
                    r2 = {
                        k: v
                        for k, v in e2.get("results", {}).items()
                        if k != "bench_time_s"
                    }
                    return r1 == r2 and e1.get("pkg_versions") == e2.get("pkg_versions")

                if not runs:
                    old_run = {
                        "timestamp": old_mtime,
                        "pkg_versions": old_pkg_versions,
                        "results": old_data[cfg][sname],
                    }
                    runs.append(old_run)

                new_run = {
                    "timestamp": int(time.time()),
                    "pkg_versions": new_pkg_versions,
                    "results": benchmark_data[cfg][sname],
                }

                if not runs or not is_duplicate(runs[-1], new_run):
                    runs.append(new_run)

                runs.sort(key=lambda x: x.get("timestamp", 0))

                try:
                    os.makedirs(os.path.dirname(rank_path), exist_ok=True)
                    with open(rank_path, "w", encoding="utf-8") as wf:
                        json.dump(runs, wf, indent=4, sort_keys=True)
                    print(f"Recorded history run for '{test_name}' in: {rank_filename}")
                except Exception as e:
                    print(f"Error saving rank history for {test_name}: {e}")

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
