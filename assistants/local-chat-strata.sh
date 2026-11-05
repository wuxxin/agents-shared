#!/usr/bin/env bash
# local-chat-strata.sh - Manage local Strata OpenAI API systemd user service for Chat and Vision
#
# Usage: local-chat-strata.sh <command> [args...]
#
# Manages a systemd user service (local-chat-strata.service) running Strata serving
# Qwen3.8-Flash-Next on AMD RDNA3 (Navi 31 / RX 7900 XTX).

set -euo pipefail

# Paths

SYSTEMD_USER_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
SERVICE_NAME="local-chat-strata"
SERVICE_FILE="${SYSTEMD_USER_DIR}/${SERVICE_NAME}.service"
ENV_FILE="${ENV_FILE:-${SYSTEMD_USER_DIR}/${SERVICE_NAME}.env}"
CONFIG_FILE="${SYSTEMD_USER_DIR}/${SERVICE_NAME}-config.json"
LAUNCHER_FILE="${SYSTEMD_USER_DIR}/${SERVICE_NAME}-launcher.py"

# Engine, Vision, and Script Binaries
STRATA_ENGINE_BIN="${STRATA_ENGINE_BIN:-/usr/lib/strata/engine/strata}"
STRATA_VISION_BIN="${STRATA_VISION_BIN:-/usr/lib/strata/engine/strata-vision-hip}"
STRATA_VISION_CPU_BIN="${STRATA_VISION_CPU_BIN:-/usr/lib/strata/engine/strata-vision}"
STRATA_SERVER_SCRIPT="${STRATA_SERVER_SCRIPT:-/usr/share/strata/serve/server.py}"
export STRATA_DEFAULT_MODEL_DIR="${LCHAT_STRATA_MODEL_DIR:-/data/public/machine-learning/models/strata/swift15_iq3s}"

# Hardware, ROCm, and Strata Execution Tuning Constants (AMD Navi 31 / RX 7900 XTX)
export ROCM_PATH="${ROCM_PATH:-/opt/rocm}"
export HIP_PATH="${HIP_PATH:-/opt/rocm}"
export STRATA_HIPBLASLT_TUNING="${STRATA_HIPBLASLT_TUNING:-/usr/share/strata/tools/hip/gfx1100-hipblaslt-100202.txt}"
export STRATA_SCORES_THREAD=1
export STRATA_WMMA_GEMM=1
export STRATA_PF_GEMM=1
export STRATA_PF_PAD=1
export STRATA_PF_FUSED=1
export STRATA_DENSE_MMQ=1
export STRATA_HC_UPMIX=1
export STRATA_PF_HCDOWN=1
export STRATA_CVEC_FUSE=1
export STRATA_PF_HC_REGION=1
export STRATA_PLE_COMPACT=1
export STRATA_PLE_COPY_STREAM=1
export STRATA_PREFILL_WARM=1
export STRATA_PREFILL_AUTO_MAX=16384
export HSA_USERPTR_FOR_PAGED_MEM=0
export STRATA_ROUTE_TAIL_SKIP=7
export PYTHONUNBUFFERED=1
export STRATA_REQUEST_LINES=1
export STRATA_MEMORY_LIMIT_MIB=0
export STRATA_RESIDENT_HEADROOM_GIB=0
export STRATA_SH_STREAM=0
export STRATA_ARENA_RELEASE=0
# Default configuration values

load_env() {
    # Capture environment overrides passed by caller
    local env_lchat_port="${LCHAT_STRATA_PORT:-}"
    local env_lchat_host="${LCHAT_STRATA_HOST:-}"
    local env_lchat_device="${LCHAT_STRATA_DEVICE:-}"
    local env_lchat_model="${LCHAT_STRATA_MODEL:-}"
    local env_lchat_ple_model="${LCHAT_STRATA_PLE_MODEL:-}"
    local env_lchat_pack="${LCHAT_STRATA_PACK:-}"
    local env_lchat_mmproj="${LCHAT_STRATA_MMPROJ:-}"
    local env_lchat_mtp="${LCHAT_STRATA_MTP:-}"
    local env_lchat_mtp_vocab="${LCHAT_STRATA_MTP_VOCAB:-}"
    local env_lchat_esp="${LCHAT_STRATA_ESP:-}"
    local env_lchat_esp_scale="${LCHAT_STRATA_ESP_SCALE:-}"
    local env_lchat_esp_layers="${LCHAT_STRATA_ESP_LAYERS:-}"
    local env_lchat_temp="${LCHAT_STRATA_TEMPERATURE:-}"
    local env_lchat_repeat="${LCHAT_STRATA_REPEAT_PENALTY:-}"
    local env_lchat_top_p="${LCHAT_STRATA_TOP_P:-}"
    local env_lchat_top_k="${LCHAT_STRATA_TOP_K:-}"
    local env_lchat_pcie_frac="${LCHAT_STRATA_PCIE_FRAC:-}"
    local env_lchat_adapt_every="${LCHAT_STRATA_ADAPT_EVERY:-}"
    local env_lchat_adapt_decay="${LCHAT_STRATA_ADAPT_DECAY:-}"
    local env_lchat_chat_template="${LCHAT_STRATA_CHAT_TEMPLATE_FILE:-}"
    local env_lchat_chat_template_kwargs="${LCHAT_STRATA_CHAT_TEMPLATE_KWARGS:-}"
    local env_lchat_ple_io="${LCHAT_STRATA_PLE_IO:-}"
    local env_lchat_max_context="${LCHAT_STRATA_MAX_CONTEXT:-}"
    local env_lchat_prefill="${LCHAT_STRATA_PREFILL:-}"
    local env_lchat_ram_budget="${LCHAT_STRATA_EXPERT_RAM_BUDGET:-}"
    local env_lchat_prompt_cache="${LCHAT_STRATA_PROMPT_CACHE:-}"
    local env_lchat_conv_slots="${LCHAT_STRATA_CONV_CACHE_SLOTS:-}"
    local env_lchat_conv_mib="${LCHAT_STRATA_CONV_CACHE_MIB:-}"
    local env_lchat_conv_min_free="${LCHAT_STRATA_CONV_CACHE_MIN_FREE_MIB:-}"
    local env_lchat_spec="${LCHAT_STRATA_SPEC:-}"
    local env_lchat_spec_min_p="${LCHAT_STRATA_SPEC_MIN_P:-}"
    local env_lchat_suffix_draft="${LCHAT_STRATA_SUFFIX_DRAFT:-}"
    local env_lchat_adapt_async="${LCHAT_STRATA_ADAPT_ASYNC:-}"
    local env_lchat_adapt_swaps="${LCHAT_STRATA_ADAPT_SWAPS:-}"
    local env_lchat_kv="${LCHAT_STRATA_KV:-}"
    local env_lchat_kv_resident="${LCHAT_STRATA_KV_RESIDENT:-}"
    local env_lchat_expert_cache="${LCHAT_STRATA_EXPERT_CACHE:-}"
    local env_lchat_vram_reserve="${LCHAT_STRATA_VRAM_RESERVE_MIB:-}"
    local env_lchat_speed="${LCHAT_STRATA_SPEED:-}"
    local env_lchat_vision="${LCHAT_STRATA_VISION:-}"
    local env_lchat_vision_tokens="${LCHAT_STRATA_VISION_TOKENS:-}"
    local env_lchat_alias="${LCHAT_STRATA_ALIAS:-}"
    local env_lchat_aliases="${LCHAT_STRATA_ALIASES:-}"
    local env_lchat_extra_args="${LCHAT_STRATA_EXTRA_ARGS:-}"

    # Default server settings (matching local-chat on port 20080 for drop-in replacement)
    LCHAT_STRATA_PORT=20080
    LCHAT_STRATA_HOST=127.0.0.1
    LCHAT_STRATA_DEVICE="0"

    # Auto-detect native Strata layout vs flat layout
    local base_m_dir="${LCHAT_STRATA_MODEL_DIR:-/data/public/machine-learning/models/strata/swift15_iq3s}"

    local def_model="${base_m_dir}/models/swift-IQ3_S/Swift-Qwen3.8-Flash-Next-GSQ-RCO-IQ3_S-00001-of-00002.gguf"
    [[ ! -f "$def_model" ]] && def_model="${base_m_dir}/Swift-Qwen3.8-Flash-Next-GSQ-RCO-IQ3_S-00001-of-00002.gguf"

    local def_ple="${base_m_dir}/models/swift-IQ3_S/Swift-Qwen3.8-Flash-Next-GSQ-RCO-IQ3_S-00002-of-00002.gguf"
    [[ ! -f "$def_ple" ]] && def_ple="${base_m_dir}/Swift-Qwen3.8-Flash-Next-GSQ-RCO-IQ3_S-00002-of-00002.gguf"

    local def_pack="${base_m_dir}/packs/swift-iq3_s"
    [[ ! -d "$def_pack" ]] && def_pack="${base_m_dir}/strata"

    local def_mmproj="${base_m_dir}/models/mmproj-Swift-Qwen3.8-Flash-Next-BF16.gguf"
    [[ ! -f "$def_mmproj" ]] && def_mmproj="${base_m_dir}/mmproj-Qwen3.8-Flash-Next-BF16.gguf"

    local def_mtp="${base_m_dir}/mtp/rt"
    [[ ! -d "$def_mtp" ]] && def_mtp="${base_m_dir}/strata/rt"

    # Default model files (clean un-ablated Swift 1.5 GSQ-RCO)
    LCHAT_STRATA_MODEL="$def_model"
    LCHAT_STRATA_PLE_MODEL="$def_ple"
    LCHAT_STRATA_PACK="$def_pack"
    LCHAT_STRATA_MMPROJ="$def_mmproj"
    LCHAT_STRATA_MTP="$def_mtp"
    LCHAT_STRATA_MTP_VOCAB="" # empty = default full bilingual/multilingual draft_vocab.bin (skips english-only drafter)
    LCHAT_STRATA_ESP="/usr/share/strata/data/experimental-speed-projection/Qwen3.8-Flash-Next-experimental-speed-projection.gguf"
    LCHAT_STRATA_ESP_SCALE="1.0"
    LCHAT_STRATA_ESP_LAYERS="4 44"
    # Default engine tuning parameters
    # Default engine tuning and sampling parameters
    LCHAT_STRATA_MAX_CONTEXT=240384
    LCHAT_STRATA_PREFILL="auto"
    LCHAT_STRATA_TEMPERATURE=0.6
    LCHAT_STRATA_REPEAT_PENALTY=1.1
    LCHAT_STRATA_TOP_P=0.95
    LCHAT_STRATA_TOP_K=20
    LCHAT_STRATA_PCIE_FRAC="0.20"
    LCHAT_STRATA_EXPERT_RAM_BUDGET=42000
    LCHAT_STRATA_PROMPT_CACHE=6
    LCHAT_STRATA_CONV_CACHE_SLOTS=6
    LCHAT_STRATA_CONV_CACHE_MIB=24576
    LCHAT_STRATA_CONV_CACHE_MIN_FREE_MIB=2048
    LCHAT_STRATA_SPEC=4
    LCHAT_STRATA_SPEC_MIN_P=0.60
    LCHAT_STRATA_SUFFIX_DRAFT=3
    LCHAT_STRATA_ADAPT_ASYNC=1
    LCHAT_STRATA_ADAPT_EVERY=1
    LCHAT_STRATA_ADAPT_SWAPS=160
    LCHAT_STRATA_ADAPT_DECAY="0.97"
    LCHAT_STRATA_KV="k8v4"
    LCHAT_STRATA_KV_RESIDENT=32768
    LCHAT_STRATA_EXPERT_CACHE="auto"
    LCHAT_STRATA_VRAM_RESERVE_MIB=512
    LCHAT_STRATA_PLE_IO="ram"
    LCHAT_STRATA_SPEED="faster"

    # Default vision settings
    LCHAT_STRATA_VISION=true
    LCHAT_STRATA_VISION_TOKENS=1024

    # Default aliases
    LCHAT_STRATA_ALIAS="qwen3.8-flash-next"
    LCHAT_STRATA_ALIASES="qwen3.8-flash-next-swift15,qwen3.8-moe,swift-1.5,qwen3.8,qwen3"
    LCHAT_STRATA_CHAT_TEMPLATE_FILE="${base_m_dir}/Qwen3.8-chat_template.jinja"
    [[ ! -f "$LCHAT_STRATA_CHAT_TEMPLATE_FILE" ]] && LCHAT_STRATA_CHAT_TEMPLATE_FILE="${LCHAT_STRATA_MODEL_DIR:-/data/public/machine-learning/models/strata}/Qwen3.8-chat_template.jinja"
    LCHAT_STRATA_CHAT_TEMPLATE_KWARGS='{"enable_thinking": true}'
    LCHAT_STRATA_EXTRA_ARGS=""

    # Binaries and script paths
    STRATA_ENGINE_BIN="${STRATA_ENGINE_BIN:-/usr/lib/strata/engine/strata}"
    STRATA_VISION_BIN="${STRATA_VISION_BIN:-/usr/lib/strata/engine/strata-vision-hip}"
    STRATA_SERVER_SCRIPT="${STRATA_SERVER_SCRIPT:-/usr/share/strata/serve/server.py}"

    # Source the env file if present
    if [[ -f "$ENV_FILE" ]]; then
        set +u
        # shellcheck disable=SC1090
        source "$ENV_FILE"
        set -u
    fi

    # Apply caller overrides
    LCHAT_STRATA_PORT="${env_lchat_port:-${LCHAT_STRATA_PORT}}"
    LCHAT_STRATA_HOST="${env_lchat_host:-${LCHAT_STRATA_HOST}}"
    LCHAT_STRATA_DEVICE="${env_lchat_device:-${LCHAT_STRATA_DEVICE}}"
    LCHAT_STRATA_MODEL="${env_lchat_model:-${LCHAT_STRATA_MODEL}}"
    LCHAT_STRATA_PLE_MODEL="${env_lchat_ple_model:-${LCHAT_STRATA_PLE_MODEL}}"
    LCHAT_STRATA_PACK="${env_lchat_pack:-${LCHAT_STRATA_PACK}}"
    LCHAT_STRATA_MMPROJ="${env_lchat_mmproj:-${LCHAT_STRATA_MMPROJ}}"
    LCHAT_STRATA_MTP="${env_lchat_mtp:-${LCHAT_STRATA_MTP}}"
    LCHAT_STRATA_MTP_VOCAB="${env_lchat_mtp_vocab:-${LCHAT_STRATA_MTP_VOCAB}}"
    LCHAT_STRATA_ESP="${env_lchat_esp:-${LCHAT_STRATA_ESP}}"
    LCHAT_STRATA_ESP_SCALE="${env_lchat_esp_scale:-${LCHAT_STRATA_ESP_SCALE}}"
    LCHAT_STRATA_ESP_LAYERS="${env_lchat_esp_layers:-${LCHAT_STRATA_ESP_LAYERS}}"
    LCHAT_STRATA_TEMPERATURE="${env_lchat_temp:-${LCHAT_STRATA_TEMPERATURE}}"
    LCHAT_STRATA_REPEAT_PENALTY="${env_lchat_repeat:-${LCHAT_STRATA_REPEAT_PENALTY}}"
    LCHAT_STRATA_TOP_P="${env_lchat_top_p:-${LCHAT_STRATA_TOP_P}}"
    LCHAT_STRATA_TOP_K="${env_lchat_top_k:-${LCHAT_STRATA_TOP_K}}"
    LCHAT_STRATA_PCIE_FRAC="${env_lchat_pcie_frac:-${LCHAT_STRATA_PCIE_FRAC}}"
    LCHAT_STRATA_MAX_CONTEXT="${env_lchat_max_context:-${LCHAT_STRATA_MAX_CONTEXT}}"
    LCHAT_STRATA_PREFILL="${env_lchat_prefill:-${LCHAT_STRATA_PREFILL}}"
    LCHAT_STRATA_EXPERT_RAM_BUDGET="${env_lchat_ram_budget:-${LCHAT_STRATA_EXPERT_RAM_BUDGET}}"
    LCHAT_STRATA_PROMPT_CACHE="${env_lchat_prompt_cache:-${LCHAT_STRATA_PROMPT_CACHE}}"
    LCHAT_STRATA_CONV_CACHE_SLOTS="${env_lchat_conv_slots:-${LCHAT_STRATA_CONV_CACHE_SLOTS}}"
    LCHAT_STRATA_CONV_CACHE_MIB="${env_lchat_conv_mib:-${LCHAT_STRATA_CONV_CACHE_MIB}}"
    LCHAT_STRATA_CONV_CACHE_MIN_FREE_MIB="${env_lchat_conv_min_free:-${LCHAT_STRATA_CONV_CACHE_MIN_FREE_MIB}}"
    LCHAT_STRATA_SPEC="${env_lchat_spec:-${LCHAT_STRATA_SPEC}}"
    LCHAT_STRATA_SPEC_MIN_P="${env_lchat_spec_min_p:-${LCHAT_STRATA_SPEC_MIN_P}}"
    LCHAT_STRATA_SUFFIX_DRAFT="${env_lchat_suffix_draft:-${LCHAT_STRATA_SUFFIX_DRAFT}}"
    LCHAT_STRATA_ADAPT_ASYNC="${env_lchat_adapt_async:-${LCHAT_STRATA_ADAPT_ASYNC}}"
    LCHAT_STRATA_ADAPT_EVERY="${env_lchat_adapt_every:-${LCHAT_STRATA_ADAPT_EVERY}}"
    LCHAT_STRATA_ADAPT_SWAPS="${env_lchat_adapt_swaps:-${LCHAT_STRATA_ADAPT_SWAPS}}"
    LCHAT_STRATA_ADAPT_DECAY="${env_lchat_adapt_decay:-${LCHAT_STRATA_ADAPT_DECAY}}"
    LCHAT_STRATA_KV="${env_lchat_kv:-${LCHAT_STRATA_KV}}"
    LCHAT_STRATA_KV_RESIDENT="${env_lchat_kv_resident:-${LCHAT_STRATA_KV_RESIDENT}}"
    LCHAT_STRATA_EXPERT_CACHE="${env_lchat_expert_cache:-${LCHAT_STRATA_EXPERT_CACHE}}"
    LCHAT_STRATA_VRAM_RESERVE_MIB="${env_lchat_vram_reserve:-${LCHAT_STRATA_VRAM_RESERVE_MIB}}"
    LCHAT_STRATA_PLE_IO="${env_lchat_ple_io:-${LCHAT_STRATA_PLE_IO}}"
    LCHAT_STRATA_SPEED="${env_lchat_speed:-${LCHAT_STRATA_SPEED}}"
    LCHAT_STRATA_VISION="${env_lchat_vision:-${LCHAT_STRATA_VISION}}"
    LCHAT_STRATA_VISION_TOKENS="${env_lchat_vision_tokens:-${LCHAT_STRATA_VISION_TOKENS}}"
    LCHAT_STRATA_ALIAS="${env_lchat_alias:-${LCHAT_STRATA_ALIAS}}"
    LCHAT_STRATA_ALIASES="${env_lchat_aliases:-${LCHAT_STRATA_ALIASES}}"
    LCHAT_STRATA_CHAT_TEMPLATE_FILE="${env_lchat_chat_template:-${LCHAT_STRATA_CHAT_TEMPLATE_FILE}}"
    LCHAT_STRATA_CHAT_TEMPLATE_KWARGS="${env_lchat_chat_template_kwargs:-${LCHAT_STRATA_CHAT_TEMPLATE_KWARGS}}"
    LCHAT_STRATA_EXTRA_ARGS="${env_lchat_extra_args:-${LCHAT_STRATA_EXTRA_ARGS}}"
}

# Parse --env KEY=VALUE from arguments, export them in memory, and build systemd-run --setenv options.

parse_env_args() {
    COMMAND_ARGS=()
    SETENV_OPTS=()
    local env_updates=()

    while [ $# -gt 0 ]; do
        if [[ "$1" == "--env" ]]; then
            if [ $# -lt 2 ]; then
                echo "Error: --env requires a value (KEY=VALUE)" >&2
                exit 1
            fi
            env_updates+=("$2")
            shift 2
        else
            COMMAND_ARGS+=("$1")
            shift
        fi
    done

    load_env

    for update in "${env_updates[@]}"; do
        local key="${update%%=*}"
        local val="${update#*=}"
        export "${key}"="${val}"
        if declare -p "$key" &>/dev/null || [[ "$key" =~ ^LCHAT_STRATA_ ]]; then
            printf -v "$key" "%s" "$val"
        fi
        SETENV_OPTS+=("--setenv=${key}=${val}")
    done
}

# Systemd execution helpers

is_systemd_running() {
    [ -S "${XDG_RUNTIME_DIR:-/run/user/$(id -u)}/systemd/private" ]
}

run_systemctl() {
    if is_systemd_running; then
        systemctl --user "$@"
    else
        echo "Warning: systemd user manager is not reachable. Skipping: systemctl --user $*"
    fi
}

# Sandboxing configuration for systemd user unit

get_shared_options() {
    local mode="$1" # "service" or "transient"
    local home_spec
    if [ "$mode" = "service" ]; then
        home_spec="%h"
    else
        home_spec="$HOME"
    fi

    # Environment file & Working directory
    echo "EnvironmentFile=-${home_spec}/.config/systemd/user/${SERVICE_NAME}.env"
    echo "WorkingDirectory=${home_spec}"

    # Basic hardening (minimal for GPU access)
    echo "NoNewPrivileges=yes"
    echo "CapabilityBoundingSet="
    echo "AmbientCapabilities="

    # GPU/DRI access requires PrivateDevices=no (ROCm needs /dev/dri, /dev/kfd)
    echo "PrivateDevices=no"
    echo "PrivateTmp=yes"
    echo "PrivateMounts=yes"
    # ROCm HSA runtime requires shared memory (IPC) to communicate with /dev/kfd
    echo "PrivateIPC=no"

    echo "ProtectSystem=strict"
    # Allow read-write access to model storage and home-based paths
    echo "BindPaths=${home_spec}"
    echo "ReadOnlyPaths=/etc/ssl /etc/ca-certificates /etc/resolv.conf /etc/hosts /etc/nsswitch.conf /usr /opt/rocm"
    echo "ReadWritePaths=/data/public/machine-learning /dev/shm /tmp"

    # Memory and resource limits (unlimited to consume all host memory)
    echo "LimitMEMLOCK=infinity"
    echo "LimitAS=infinity"
    echo "LimitDATA=infinity"
    echo "LimitRSS=infinity"
    echo "LimitSTACK=infinity"
    echo "MemoryMax=infinity"
    echo "MemoryHigh=infinity"
    echo "MemorySwapMax=infinity"
    echo "TasksMax=infinity"
    echo "ProtectKernelTunables=yes"
    echo "ProtectKernelModules=yes"
    echo "ProtectKernelLogs=yes"
    echo "ProtectControlGroups=yes"
    echo "ProtectClock=yes"
    echo "ProtectHostname=yes"

    echo "LockPersonality=yes"
    echo "RestrictSUIDSGID=yes"
    echo "RestrictRealtime=yes"
    echo "KeyringMode=private"
    echo "UMask=0077"
}

# Dynamic JSON configuration generator for Strata engine

generate_config_json() {
    python3 -c '
import json, os, sys

def get_env(k, default=""):
    return os.environ.get(k, default)

model = get_env("LCHAT_STRATA_MODEL")
ple_model = get_env("LCHAT_STRATA_PLE_MODEL")
pack = get_env("LCHAT_STRATA_PACK")
mmproj = get_env("LCHAT_STRATA_MMPROJ")
mtp = get_env("LCHAT_STRATA_MTP")
mtp_vocab = get_env("LCHAT_STRATA_MTP_VOCAB")
esp = get_env("LCHAT_STRATA_ESP")
esp_scale = get_env("LCHAT_STRATA_ESP_SCALE", "1.0")
esp_layers_str = get_env("LCHAT_STRATA_ESP_LAYERS", "4 44")
esp_layers = [l.strip() for l in esp_layers_str.split() if l.strip()]
engine_bin = get_env("STRATA_ENGINE_BIN", "/usr/lib/strata/engine/strata")
vision_bin = get_env("STRATA_VISION_BIN", "/usr/lib/strata/engine/strata-vision-hip")
alias = get_env("LCHAT_STRATA_ALIAS", "qwen3.8-flash-next")
aliases_str = get_env("LCHAT_STRATA_ALIASES", "qwen3.8-flash-next-swift15,qwen3.8-moe,swift-1.5,qwen3.8,qwen3")
aliases = [a.strip() for a in aliases_str.split(",") if a.strip()]

def resolve_file(path, fallbacks):
    if path and os.path.isfile(path):
        return path
    for fb in fallbacks:
        if fb and os.path.isfile(fb):
            return fb
    return path

def resolve_dir(path, fallbacks):
    if path and os.path.isdir(path):
        return path
    for fb in fallbacks:
        if fb and os.path.isdir(fb):
            return fb
    return path

base_dir = "/data/public/machine-learning/models/strata/swift15_iq3s"
model = resolve_file(model, [
    os.path.join(base_dir, "models/swift-IQ3_S/Swift-Qwen3.8-Flash-Next-GSQ-RCO-IQ3_S-00001-of-00002.gguf"),
    os.path.join(base_dir, "Swift-Qwen3.8-Flash-Next-GSQ-RCO-IQ3_S-00001-of-00002.gguf")
])
ple_model = resolve_file(ple_model, [
    os.path.join(base_dir, "models/swift-IQ3_S/Swift-Qwen3.8-Flash-Next-GSQ-RCO-IQ3_S-00002-of-00002.gguf"),
    os.path.join(base_dir, "Swift-Qwen3.8-Flash-Next-GSQ-RCO-IQ3_S-00002-of-00002.gguf")
])
pack = resolve_dir(pack, [
    os.path.join(base_dir, "packs/swift-iq3_s"),
    os.path.join(base_dir, "strata")
])
mmproj = resolve_file(mmproj, [
    os.path.join(base_dir, "models/mmproj-Swift-Qwen3.8-Flash-Next-BF16.gguf"),
    os.path.join(base_dir, "mmproj-Qwen3.8-Flash-Next-BF16.gguf")
])
mtp = resolve_dir(mtp, [
    os.path.join(base_dir, "mtp/rt"),
    os.path.join(base_dir, "strata/rt")
])
engine_args = [
    "--native", model,
    "--native-dense-gguf", model,
]
if ple_model and ple_model != model:
    engine_args.extend(["--native-dense-gguf", ple_model])

engine_args.extend([
    "--prefill", get_env("LCHAT_STRATA_PREFILL", "auto"),
    "--pcie-frac", get_env("LCHAT_STRATA_PCIE_FRAC", "0.20"),
    "--prompt-cache", get_env("LCHAT_STRATA_PROMPT_CACHE", "6"),
    "--conversation-cache-slots", get_env("LCHAT_STRATA_CONV_CACHE_SLOTS", "6"),
    "--conversation-cache-mib", get_env("LCHAT_STRATA_CONV_CACHE_MIB", "24576"),
    "--conversation-cache-min-free-mib", get_env("LCHAT_STRATA_CONV_CACHE_MIN_FREE_MIB", "2048"),
    "--max-context", get_env("LCHAT_STRATA_MAX_CONTEXT", "240384"),
    "--spec", get_env("LCHAT_STRATA_SPEC", "4"),
    "--spec-min-p", get_env("LCHAT_STRATA_SPEC_MIN_P", "0.60"),
    "--suffix-draft", get_env("LCHAT_STRATA_SUFFIX_DRAFT", "3"),
    "--adapt-async", get_env("LCHAT_STRATA_ADAPT_ASYNC", "1"),
    "--adapt-every", get_env("LCHAT_STRATA_ADAPT_EVERY", "1"),
    "--adapt-swaps", get_env("LCHAT_STRATA_ADAPT_SWAPS", "160"),
    "--adapt-decay", get_env("LCHAT_STRATA_ADAPT_DECAY", "0.97"),
    "--kv", get_env("LCHAT_STRATA_KV", "k8v4"),
    "--kv-resident", get_env("LCHAT_STRATA_KV_RESIDENT", "32768"),
    "--expert-cache", get_env("LCHAT_STRATA_EXPERT_CACHE", "auto"),
    "--vram-reserve-mib", get_env("LCHAT_STRATA_VRAM_RESERVE_MIB", "0"),
    "--ple-io", get_env("LCHAT_STRATA_PLE_IO", "ram"),
    "--ple-gguf", model,
])
if pack:
    engine_args.extend(["--pack", pack])
if mtp:
    engine_args.extend(["--mtp", mtp])
if mtp_vocab:
    engine_args.extend(["--mtp-draft-vocab", mtp_vocab])
if esp:
    l_start = esp_layers[0] if len(esp_layers) > 0 else "4"
    l_end = esp_layers[1] if len(esp_layers) > 1 else "44"
    engine_args.extend([
        "--control-vector-scaled", f"{esp}:{esp_scale}",
        "--control-vector-layer-range", l_start, l_end,
        "--cvec-mode", "project",
        "--cvec-dir", "per-layer",
    ])
profile = get_env("LCHAT_STRATA_EXPERT_PROFILE", "")
if not profile:
    for cand in [
        os.path.join(base_dir, "expert-profile.bin"),
        os.path.join(base_dir, "data/expert-profile.bin"),
        "/usr/share/strata/data/expert-profile.bin",
    ]:
        if os.path.exists(cand):
            profile = cand
            break

if profile:
    engine_args.extend(["--expert-profile", profile])

profile_save = get_env("LCHAT_STRATA_EXPERT_PROFILE_SAVE", "")
if profile_save:
    engine_args.extend(["--expert-profile-save", profile_save])
tok_path = None
tok_candidates = []
if pack:
    tok_candidates.extend([os.path.join(pack, "tokenizer"), pack])
tok_candidates.extend([
    os.path.join(base_dir, "packs/swift-iq3_s/tokenizer"),
    os.path.join(base_dir, "packs/swift-iq3_s"),
    os.path.join(base_dir, "strata/tokenizer"),
    os.path.join(base_dir, "strata"),
])
for cand in tok_candidates:
    if os.path.isfile(os.path.join(cand, "vocab.json")):
        tok_path = cand
        break
tok_runtime = get_env("LCHAT_STRATA_TOKENIZER_DIR", "")
if tok_runtime and os.path.isdir(tok_runtime) and os.path.isfile(os.path.join(tok_runtime, "vocab.json")):
    tok_path = tok_runtime
if not tok_path:
    tok_path = os.path.join(pack, "tokenizer") if pack else pack

cfg = {
    "exe": engine_bin,
    "args": engine_args,
    "cwd": "/usr/share/strata",
    "tokenizer": tok_path,
    "model_name": alias,
    "aliases": aliases,
    "arch": "qwen",
    "backend": "hip",
    "sampling": {
        "temperature": float(get_env("LCHAT_STRATA_TEMPERATURE", "0.6")),
        "repetition_penalty": float(get_env("LCHAT_STRATA_REPEAT_PENALTY", "1.1")),
        "top_p": float(get_env("LCHAT_STRATA_TOP_P", "0.95")),
        "top_k": int(get_env("LCHAT_STRATA_TOP_K", "20")),
    },
}

vision_enabled = get_env("LCHAT_STRATA_VISION", "true").lower() in ("true", "1", "yes")
if vision_enabled:
    engine_args.append("--vision")
    cfg["vision"] = {
        "exe": vision_bin,
        "cpu_exe": "/usr/lib/strata/engine/strata-vision",
        "mmproj": mmproj,
        "model": model,
        "max_tokens": int(get_env("LCHAT_STRATA_VISION_TOKENS", "1024")),
    }
print(json.dumps(cfg, indent=2))
'
}

# Launcher script generator

generate_launcher_script() {
    cat <<'EOF'
#!/usr/bin/env python3
"""Strata Service Launcher: sets tuning flags, memory limits, and runs server with direct stdout/stderr."""
import os
import sys
import resource
import subprocess

# Hardware, ROCm, and execution tuning flags
os.environ.setdefault("STRATA_SCORES_THREAD", "1")
os.environ.setdefault("STRATA_WMMA_GEMM", "1")
os.environ.setdefault("STRATA_PF_GEMM", "1")
os.environ.setdefault("STRATA_PF_PAD", "1")
os.environ.setdefault("STRATA_PF_FUSED", "1")
os.environ.setdefault("STRATA_DENSE_MMQ", "1")
os.environ.setdefault("STRATA_HC_UPMIX", "1")
os.environ.setdefault("STRATA_PF_HCDOWN", "1")
os.environ.setdefault("STRATA_CVEC_FUSE", "1")
os.environ.setdefault("STRATA_PF_HC_REGION", "1")
os.environ.setdefault("STRATA_PLE_COMPACT", "1")
os.environ.setdefault("STRATA_PLE_COPY_STREAM", "1")
os.environ.setdefault("STRATA_PREFILL_WARM", "1")
os.environ.setdefault("STRATA_PREFILL_AUTO_MAX", "16384")
os.environ.setdefault("STRATA_HIPBLASLT_TUNING", "/usr/share/strata/tools/hip/gfx1100-hipblaslt-100202.txt")
os.environ.setdefault("HSA_USERPTR_FOR_PAGED_MEM", "0")
os.environ.setdefault("STRATA_ROUTE_TAIL_SKIP", "7")
os.environ.setdefault("ROCM_PATH", os.environ.get("ROCM_PATH", "/opt/rocm"))
os.environ.setdefault("HIP_PATH", os.environ.get("HIP_PATH", "/opt/rocm"))
os.environ.setdefault("PYTHONUNBUFFERED", "1")
os.environ.setdefault("STRATA_REQUEST_LINES", "1")
os.environ.setdefault("STRATA_MEMORY_LIMIT_MIB", "0")
os.environ.setdefault("STRATA_RESIDENT_HEADROOM_GIB", "0")
os.environ.setdefault("STRATA_SH_STREAM", "0")
if "LCHAT_STRATA_DEVICE" in os.environ:
    os.environ.setdefault("HIP_VISIBLE_DEVICES", os.environ["LCHAT_STRATA_DEVICE"])

# Set host memory limits to unlimited
for limit in (resource.RLIMIT_MEMLOCK, resource.RLIMIT_AS, resource.RLIMIT_DATA):
    try:
        resource.setrlimit(limit, (resource.RLIM_INFINITY, resource.RLIM_INFINITY))
    except (ValueError, OSError):
        pass

# Import Strata server and ensure subprocesses stream directly to sys.stderr
sys.path.insert(0, "/usr/share/strata")
from serve import lifeline
import serve.server as strata_server

# Patch lifeline.popen so engine and vision processes stream stderr directly to sys.stderr
_orig_popen = lifeline.popen
def _direct_popen(args, role="engine", **kw):
    if kw.get("stderr") in (None, subprocess.DEVNULL):
        kw["stderr"] = sys.stderr
    return _orig_popen(args, role=role, **kw)
lifeline.popen = _direct_popen

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
EOF
}

# Systemd service generator

generate_service_file() {
    local launcher_path="%h/.config/systemd/user/${SERVICE_NAME}-launcher.py"

    cat <<EOF
[Unit]
Description=Local Strata Chat Inference Service (Qwen3.8-Flash-Next on RX 7900 XTX)
Documentation=https://github.com/strata-org/strata
After=network.target

[Service]
Type=simple
TimeoutStartSec=600
TimeoutStopSec=60
$(get_shared_options service)
ExecStart=/usr/bin/python3 ${launcher_path}
Restart=on-failure
RestartSec=10s

StandardOutput=journal
StandardError=journal
SyslogIdentifier=${SERVICE_NAME}

[Install]
WantedBy=default.target
EOF
}

# Default environment template generator

generate_env_file() {
    cat <<'EOF'
# local-chat-strata.env
# Configuration file for local-chat-strata.service.
#
# Dedicated Strata Chat and Vision inference settings for Qwen3.8-Flash-Next on AMD RDNA3 (RX 7900 XTX).
# Reload with:  local-chat-strata.sh restart

# ### SERVER SETTINGS

# Port to bind the server to (default: 20080, matching local-chat for drop-in replacement)
LCHAT_STRATA_PORT=20080

# Host to bind the server to (127.0.0.1 for local access only)
LCHAT_STRATA_HOST=127.0.0.1

# HIP GPU device ID (0 for primary RX 7900 XTX)
LCHAT_STRATA_DEVICE="0"


# ### MODEL AND ENGINE PATHS
# Shard 1 (Native IQ3_S model - clean un-ablated Swift 1.5)
LCHAT_STRATA_MODEL="/data/public/machine-learning/models/strata/swift15_iq3s/Swift-Qwen3.8-Flash-Next-GSQ-RCO-IQ3_S-00001-of-00002.gguf"

# Shard 2 (PLE GGUF)
LCHAT_STRATA_PLE_MODEL="/data/public/machine-learning/models/strata/swift15_iq3s/Swift-Qwen3.8-Flash-Next-GSQ-RCO-IQ3_S-00002-of-00002.gguf"

# Strata native pack directory
LCHAT_STRATA_PACK="/data/public/machine-learning/models/strata/swift15_iq3s/strata"

# Vision mmproj model (BF16 vision encoder)
LCHAT_STRATA_MMPROJ="/data/public/machine-learning/models/strata/swift15_iq3s/mmproj-Qwen3.8-Flash-Next-BF16.gguf"

# MTP Draft head runtime folder (speculative decoding)
LCHAT_STRATA_MTP="/data/public/machine-learning/models/strata/swift15_iq3s/strata/rt"

# MTP Draft vocabulary override (empty = default full bilingual/multilingual draft_vocab.bin)
LCHAT_STRATA_MTP_VOCAB=""

# Runtime experimental speed projection / refusal control vector
LCHAT_STRATA_ESP="/usr/share/strata/data/experimental-speed-projection/Qwen3.8-Flash-Next-experimental-speed-projection.gguf"
LCHAT_STRATA_ESP_SCALE="1.0"
LCHAT_STRATA_ESP_LAYERS="4 44"
# ### ENGINE TUNING PARAMETERS

# Context window size in tokens (up to 240,384 tokens)
LCHAT_STRATA_MAX_CONTEXT=240384

# Prefill chunk size ("auto" dynamically scales chunk processing)
LCHAT_STRATA_PREFILL="auto"

# Deterministic Agentic Sampling parameters
LCHAT_STRATA_TEMPERATURE=0.6
LCHAT_STRATA_REPEAT_PENALTY=1.1
LCHAT_STRATA_TOP_P=0.95
LCHAT_STRATA_TOP_K=20

# Hardware calibrated PCIe fractional saturation
LCHAT_STRATA_PCIE_FRAC="0.20"

# Host RAM budget for experts in MiB (42000 MiB = ~41 GiB out of 95 GiB host RAM)
LCHAT_STRATA_EXPERT_RAM_BUDGET=42000

# Prompt cache slots
LCHAT_STRATA_PROMPT_CACHE=6

# Conversation cache slots and memory limits
LCHAT_STRATA_CONV_CACHE_SLOTS=6
LCHAT_STRATA_CONV_CACHE_MIB=24576
LCHAT_STRATA_CONV_CACHE_MIN_FREE_MIB=2048

# Speculative decoding tokens and threshold
LCHAT_STRATA_SPEC=4
LCHAT_STRATA_SPEC_MIN_P=0.60
LCHAT_STRATA_SUFFIX_DRAFT=3
LCHAT_STRATA_ADAPT_ASYNC=1
LCHAT_STRATA_ADAPT_EVERY=1
LCHAT_STRATA_ADAPT_SWAPS=160
LCHAT_STRATA_ADAPT_DECAY="0.97"

# KV cache quantization and residency
LCHAT_STRATA_KV="k8v4"
LCHAT_STRATA_KV_RESIDENT=32768
LCHAT_STRATA_EXPERT_CACHE="auto"
LCHAT_STRATA_VRAM_RESERVE_MIB=512
# Routing profile and adaptive persistence
LCHAT_STRATA_EXPERT_PROFILE="/usr/share/strata/data/expert-profile.bin"
LCHAT_STRATA_EXPERT_PROFILE_SAVE="%h/.config/systemd/user/local-chat-strata-profile.bin"
LCHAT_STRATA_PLE_IO="ram"

# ### VISION ENCODER

# Enable multimodal vision processing via strata-vision-hip
LCHAT_STRATA_VISION=true
LCHAT_STRATA_VISION_TOKENS=1024


# ### ALIASES AND METADATA

# Primary alias reported to clients and router
LCHAT_STRATA_ALIAS="qwen3.8-flash-next"

# Comma-separated list of recognized aliases
LCHAT_STRATA_ALIASES="qwen3.8-flash-next-swift15,qwen3.8-moe,swift-1.5,qwen3.8,qwen3"

# Custom Jinja chat template file (fixed froggeric community template v22.5)
LCHAT_STRATA_CHAT_TEMPLATE_FILE="/data/public/machine-learning/models/strata/Qwen3.8-chat_template.jinja"
LCHAT_STRATA_CHAT_TEMPLATE_KWARGS='{"enable_thinking": true}'

# Extra arguments passed directly to server.py
LCHAT_STRATA_EXTRA_ARGS=""

# Native Strata execution & ROCm flags
STRATA_SCORES_THREAD=1
STRATA_WMMA_GEMM=1
STRATA_PF_GEMM=1
STRATA_PF_PAD=1
STRATA_PF_FUSED=1
STRATA_DENSE_MMQ=1
STRATA_HC_UPMIX=1
STRATA_PF_HCDOWN=1
STRATA_CVEC_FUSE=1
STRATA_PF_HC_REGION=1
STRATA_PLE_COMPACT=1
STRATA_PLE_COPY_STREAM=1
STRATA_PREFILL_WARM=1
STRATA_PREFILL_AUTO_MAX=16384
STRATA_HIPBLASLT_TUNING="/usr/share/strata/tools/hip/gfx1100-hipblaslt-100202.txt"
HSA_USERPTR_FOR_PAGED_MEM=0
STRATA_ROUTE_TAIL_SKIP=7
STRATA_MEMORY_LIMIT_MIB=0
STRATA_RESIDENT_HEADROOM_GIB=0
STRATA_SH_STREAM=0
STRATA_ARENA_RELEASE=0
PYTHONUNBUFFERED=1
STRATA_REQUEST_LINES=1

EOF
}

# Write service, launcher, and json config to disk

write_service_file() {
    load_env
    mkdir -p "${SYSTEMD_USER_DIR}"

    # Setup managed tokenizer directory if custom chat template is configured
    if [[ -n "${LCHAT_STRATA_CHAT_TEMPLATE_FILE:-}" && -f "${LCHAT_STRATA_CHAT_TEMPLATE_FILE}" ]]; then
        local tok_runtime="${SYSTEMD_USER_DIR}/${SERVICE_NAME}-tokenizer"
        mkdir -p "${tok_runtime}"
        local tok_src="${LCHAT_STRATA_PACK:-/data/public/machine-learning/models/strata/swift15_iq3s/strata}/tokenizer"
        [[ ! -d "$tok_src" ]] && tok_src="${LCHAT_STRATA_PACK:-/data/public/machine-learning/models/strata/swift15_iq3s/strata}"
        for f in vocab.json tokenizer.json merges.txt tokenizer_config.json; do
            if [[ -f "${tok_src}/${f}" ]]; then
                ln -sf "${tok_src}/${f}" "${tok_runtime}/${f}"
            fi
        done
        ln -sf "${LCHAT_STRATA_CHAT_TEMPLATE_FILE}" "${tok_runtime}/chat_template.jinja"
        export LCHAT_STRATA_TOKENIZER_DIR="${tok_runtime}"
    fi

    # Export variables so generate_config_json python environment sees them
    export LCHAT_STRATA_MODEL LCHAT_STRATA_PLE_MODEL LCHAT_STRATA_PACK
    export LCHAT_STRATA_MMPROJ LCHAT_STRATA_MTP LCHAT_STRATA_MTP_VOCAB LCHAT_STRATA_ESP
    export LCHAT_STRATA_ESP_SCALE LCHAT_STRATA_ESP_LAYERS STRATA_ENGINE_BIN STRATA_VISION_BIN
    export LCHAT_STRATA_SPEED LCHAT_STRATA_PREFILL LCHAT_STRATA_EXPERT_RAM_BUDGET
    export LCHAT_STRATA_PROMPT_CACHE LCHAT_STRATA_CONV_CACHE_SLOTS
    export LCHAT_STRATA_CONV_CACHE_MIB LCHAT_STRATA_CONV_CACHE_MIN_FREE_MIB
    export LCHAT_STRATA_MAX_CONTEXT LCHAT_STRATA_SPEC LCHAT_STRATA_SPEC_MIN_P
    export LCHAT_STRATA_SUFFIX_DRAFT LCHAT_STRATA_ADAPT_ASYNC LCHAT_STRATA_ADAPT_EVERY
    export LCHAT_STRATA_ADAPT_SWAPS LCHAT_STRATA_ADAPT_DECAY
    export LCHAT_STRATA_KV LCHAT_STRATA_KV_RESIDENT LCHAT_STRATA_EXPERT_CACHE
    export LCHAT_STRATA_VRAM_RESERVE_MIB LCHAT_STRATA_VISION LCHAT_STRATA_VISION_TOKENS
    export LCHAT_STRATA_TEMPERATURE LCHAT_STRATA_REPEAT_PENALTY LCHAT_STRATA_TOP_P LCHAT_STRATA_TOP_K
    export LCHAT_STRATA_PCIE_FRAC LCHAT_STRATA_PLE_IO LCHAT_STRATA_ALIAS LCHAT_STRATA_ALIASES
    export LCHAT_STRATA_CHAT_TEMPLATE_FILE LCHAT_STRATA_CHAT_TEMPLATE_KWARGS

    # Generate JSON config
    generate_config_json >"${CONFIG_FILE}"
    chmod 600 "${CONFIG_FILE}"

    # Generate launcher script
    generate_launcher_script >"${LAUNCHER_FILE}"
    chmod 755 "${LAUNCHER_FILE}"

    # Generate systemd service unit
    generate_service_file >"${SERVICE_FILE}"
    chmod 644 "${SERVICE_FILE}"

    run_systemctl daemon-reload
}

# Actions

cmd_install() {
    local no_start=false
    local new_config=false
    while [ $# -gt 0 ]; do
        case "$1" in
        --no-start) no_start=true ;;
        --new-config) new_config=true ;;
        esac
        shift
    done

    echo "Installing ${SERVICE_NAME} systemd user service..."
    mkdir -p "${SYSTEMD_USER_DIR}"

    if [[ -f "${ENV_FILE}" ]] && [ "${new_config}" = "false" ]; then
        echo "Warning: Env file already exists, skipping: ${ENV_FILE}"
        echo "Use --new-config if you want to regenerate defaults."
    else
        echo "Writing default env config file: ${ENV_FILE}"
        generate_env_file >"${ENV_FILE}"
        chmod 600 "${ENV_FILE}"
        echo "Env file written."
    fi

    echo "Writing service files, launcher script, and config JSON: ${SERVICE_FILE}"
    write_service_file
    echo "Service files written."

    echo "Enabling ${SERVICE_NAME}.service..."
    run_systemctl enable "${SERVICE_NAME}.service"

    if [ "$no_start" = "true" ]; then
        echo "Stopping service if running (--no-start specified)..."
        run_systemctl stop "${SERVICE_NAME}.service" || true
    else
        echo "Starting/Restarting service..."
        run_systemctl restart "${SERVICE_NAME}.service"
    fi

    echo "Installation complete."
    echo ""
    echo "  Service:  ${SERVICE_FILE}"
    echo "  Env:      ${ENV_FILE}"
    echo "  Config:   ${CONFIG_FILE}"
    echo "  Launcher: ${LAUNCHER_FILE}"
    echo ""
    echo "  Status:  $0 status"
    echo "  Logs:    $0 logs"
}

cmd_uninstall() {
    echo "Uninstalling ${SERVICE_NAME} systemd user service..."
    run_systemctl stop "${SERVICE_NAME}.service" || true
    run_systemctl disable "${SERVICE_NAME}.service" || true

    if [[ -f "${SERVICE_FILE}" ]]; then
        rm -f "${SERVICE_FILE}"
        rm -f "${CONFIG_FILE}"
        rm -f "${LAUNCHER_FILE}"
        run_systemctl daemon-reload
        echo "Removed service file, config JSON, and launcher."
    fi

    echo "Uninstalled successfully. Configuration in ${ENV_FILE} is preserved."
}

cmd_start() {
    write_service_file
    if ! is_systemd_running; then
        echo "Error: Systemd is not running. Use 'exec' to run ${SERVICE_NAME} directly." >&2
        exit 1
    fi
    run_systemctl start "${SERVICE_NAME}.service"
}

cmd_stop() { run_systemctl stop "${SERVICE_NAME}.service"; }

cmd_restart() {
    write_service_file
    if ! is_systemd_running; then
        echo "Error: Systemd is not running. Use 'exec' to run ${SERVICE_NAME} directly." >&2
        exit 1
    fi
    run_systemctl restart "${SERVICE_NAME}.service"
}

cmd_status() { run_systemctl status "${SERVICE_NAME}.service"; }
cmd_enable() {
    write_service_file
    run_systemctl enable "${SERVICE_NAME}.service"
}
cmd_disable() { run_systemctl disable "${SERVICE_NAME}.service"; }
cmd_logs() { journalctl --user -u "${SERVICE_NAME}.service" "$@"; }

cmd_edit() {
    mkdir -p "$(dirname "${ENV_FILE}")"
    touch "${ENV_FILE}"
    ${EDITOR:-nano} "${ENV_FILE}"
    echo "Restarting service to apply updated configuration..."
    cmd_restart
}

cmd_exec() {
    parse_env_args "$@"
    set -- "${COMMAND_ARGS[@]}"

    write_service_file

    if ! is_systemd_running; then
        echo "Warning: Systemd is not running. Running Strata directly in foreground..."
        exec /usr/bin/python3 "${LAUNCHER_FILE}" "$@"
    fi

    echo "Starting Strata as a transient systemd service..."
    local opts=(
        --user
        --pty
        --wait
        --collect
        --quiet
        -p "Type=exec"
    )

    while IFS= read -r opt; do
        if [ -n "$opt" ]; then
            opts+=(-p "$opt")
        fi
    done < <(get_shared_options transient)

    systemd-run "${opts[@]}" "${SETENV_OPTS[@]}" -- /usr/bin/python3 "${LAUNCHER_FILE}" "$@"
}

cmd_shell() {
    echo "Starting interactive shell in the Strata systemd environment..."
    parse_env_args "$@"
    set -- "${COMMAND_ARGS[@]}"

    local opts=(
        --user
        --pty
        --wait
        --collect
        --quiet
        -p "Type=exec"
    )

    while IFS= read -r opt; do
        if [ -n "$opt" ]; then
            opts+=(-p "$opt")
        fi
    done < <(get_shared_options transient)

    systemd-run "${opts[@]}" "${SETENV_OPTS[@]}" -- "${SHELL:-/bin/bash}" "$@"
}

cmd_run() {
    parse_env_args "$@"
    set -- "${COMMAND_ARGS[@]}"

    if [ $# -lt 1 ]; then
        echo "Error: run requires a command to execute." >&2
        exit 1
    fi
    echo "Running command inside the Strata environment: $*"

    local opts=(
        --user
        --pty
        --wait
        --collect
        --quiet
        -p "Type=exec"
    )

    while IFS= read -r opt; do
        if [ -n "$opt" ]; then
            opts+=(-p "$opt")
        fi
    done < <(get_shared_options transient)

    systemd-run "${opts[@]}" "${SETENV_OPTS[@]}" -- "$@"
}

wait_for_endpoint() {
    local url="$1"
    local max_retries="${2:-30}"
    local retry_delay="${3:-2}"
    local desc="${4:-endpoint}"

    echo "Waiting for ${desc} at ${url} to be ready..."
    local count=0
    while [ "$count" -lt "$max_retries" ]; do
        if curl -s -f -o /dev/null "${url}" 2>/dev/null; then
            echo "${desc} is ready."
            return 0
        fi
        sleep "$retry_delay"
        count=$((count + 1))
        echo -n "."
    done
    echo ""
    echo "Error: Timed out waiting for ${desc} at ${url}." >&2
    return 1
}

cmd_test() {
    echo "Running local-chat-strata validation tests..."
    load_env

    local host="${LCHAT_STRATA_HOST:-127.0.0.1}"
    local port="${LCHAT_STRATA_PORT:-20080}"
    local alias="${LCHAT_STRATA_ALIAS:-qwen3.8-flash-next}"
    local base_url="http://${host}:${port}"
    echo "Using endpoint base: ${base_url}"

    local benchmark=false
    local extra_args=()
    while [ $# -gt 0 ]; do
        case "$1" in
        --benchmark) benchmark=true ;;
        *) extra_args+=("$1") ;;
        esac
        shift
    done

    wait_for_endpoint "${base_url}/v1/models" 30 2 "local-chat-strata" || return 1

    echo "Checking models endpoint: ${base_url}/v1/models"
    local models_json
    models_json=$(curl -s "${base_url}/v1/models")
    echo "Available models: ${models_json}"

    echo "Testing chat completion endpoint: ${base_url}/v1/chat/completions"
    local chat_resp
    chat_resp=$(curl -s -X POST "${base_url}/v1/chat/completions" \
        -H "Content-Type: application/json" \
        -d "{
            \"model\": \"${alias}\",
            \"messages\": [{\"role\": \"user\", \"content\": \"Say hello in one short sentence.\"}],
            \"max_tokens\": 32
        }")

    echo "Chat response: ${chat_resp}"
    if echo "${chat_resp}" | grep -q "choices"; then
        echo "SUCCESS: Chat completion test passed."
    else
        echo "FAILED: Chat response missing 'choices'."
        return 1
    fi

    if [ "$benchmark" = "true" ]; then
        echo "Running chat benchmark via benchmark-helper.py..."
        local helper_script
        helper_script="$(dirname "$0")/../scripts/benchmark-helper.py"
        if [ -f "$helper_script" ]; then
            python3 "$helper_script" --mode chat --url "${base_url}" --model "${alias}" "${extra_args[@]}"
        else
            echo "Warning: scripts/benchmark-helper.py not found, skipping benchmark."
        fi
    fi
}

cmd_cat() {
    load_env
    export LCHAT_STRATA_MODEL LCHAT_STRATA_PLE_MODEL LCHAT_STRATA_PACK
    export LCHAT_STRATA_MMPROJ LCHAT_STRATA_MTP LCHAT_STRATA_MTP_VOCAB LCHAT_STRATA_ESP
    export LCHAT_STRATA_ESP_SCALE LCHAT_STRATA_ESP_LAYERS STRATA_ENGINE_BIN STRATA_VISION_BIN
    export LCHAT_STRATA_SPEED LCHAT_STRATA_PREFILL LCHAT_STRATA_EXPERT_RAM_BUDGET
    export LCHAT_STRATA_PROMPT_CACHE LCHAT_STRATA_CONV_CACHE_SLOTS
    export LCHAT_STRATA_CONV_CACHE_MIB LCHAT_STRATA_CONV_CACHE_MIN_FREE_MIB
    export LCHAT_STRATA_MAX_CONTEXT LCHAT_STRATA_SPEC LCHAT_STRATA_SPEC_MIN_P
    export LCHAT_STRATA_SUFFIX_DRAFT LCHAT_STRATA_ADAPT_ASYNC LCHAT_STRATA_ADAPT_EVERY
    export LCHAT_STRATA_ADAPT_SWAPS LCHAT_STRATA_ADAPT_DECAY
    export LCHAT_STRATA_KV LCHAT_STRATA_KV_RESIDENT LCHAT_STRATA_EXPERT_CACHE
    export LCHAT_STRATA_VRAM_RESERVE_MIB LCHAT_STRATA_VISION LCHAT_STRATA_VISION_TOKENS
    export LCHAT_STRATA_TEMPERATURE LCHAT_STRATA_REPEAT_PENALTY LCHAT_STRATA_TOP_P LCHAT_STRATA_TOP_K
    export LCHAT_STRATA_PCIE_FRAC LCHAT_STRATA_PLE_IO LCHAT_STRATA_ALIAS LCHAT_STRATA_ALIASES
    export LCHAT_STRATA_CHAT_TEMPLATE_FILE LCHAT_STRATA_CHAT_TEMPLATE_KWARGS

    echo "=== Service File: ${SERVICE_FILE} ==="
    generate_service_file
    echo ""
    echo "=== Environment File: ${ENV_FILE} ==="
    if [[ -f "${ENV_FILE}" ]]; then
        cat "${ENV_FILE}"
    else
        generate_env_file
    fi
    echo ""
    echo "=== Config JSON: ${CONFIG_FILE} ==="
    generate_config_json
    echo ""
    echo "=== Launcher Script: ${LAUNCHER_FILE} ==="
    generate_launcher_script
}

usage() {
    cat <<EOF
Usage: $0 <command> [args...]
Commands:
  install [--no-start] [--new-config] - Setup service and default configuration
  uninstall - Stop and remove systemd service, config JSON, and launcher
  start     - Start the systemd service
  stop      - Stop the systemd service
  restart   - Restart the systemd service
  status    - View systemd service status
  enable    - Enable systemd service on boot
  disable   - Disable systemd service on boot
  logs      - Tail the systemd service logs
  edit      - Edit the .env config file and restart the service upon exit
  exec      - Run Strata server as a transient systemd user service
  run       - Run a command inside the Strata environment
  shell     - Spawn an interactive shell in the Strata environment
  cat       - Print service file, environment config, config JSON, and launcher script
  test [--benchmark ...] - Run validation tests or benchmarks (chat + vision)
EOF
}

main() {
    if [ $# -lt 1 ]; then
        usage
        exit 1
    fi

    COMMAND="$1"
    shift

    case "$COMMAND" in
    install) cmd_install "$@" ;;
    uninstall) cmd_uninstall ;;
    start) cmd_start ;;
    stop) cmd_stop ;;
    restart) cmd_restart ;;
    status) cmd_status ;;
    enable) cmd_enable ;;
    disable) cmd_disable ;;
    logs) cmd_logs "$@" ;;
    edit) cmd_edit ;;
    exec) cmd_exec "$@" ;;
    run) cmd_run "$@" ;;
    shell) cmd_shell "$@" ;;
    cat) cmd_cat ;;
    test) cmd_test "$@" ;;
    *)
        echo "Unknown command: $COMMAND"
        usage
        exit 1
        ;;
    esac
}

main "$@"
