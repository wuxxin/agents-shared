#!/usr/bin/env bash
# local-chat.sh - Manage local llama-server systemd user service for Chat
#
# Usage: local-chat.sh <command> [args...]
#
# Manages a systemd user service (local-chat.service) that runs llama-server serving the Chat/Vision LLM and optional Embedding.

set -euo pipefail

# Paths

SYSTEMD_USER_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
SERVICE_NAME="local-chat"
SERVICE_FILE="${SYSTEMD_USER_DIR}/${SERVICE_NAME}.service"
ENV_FILE="${SYSTEMD_USER_DIR}/${SERVICE_NAME}.env"
PRESET_FILE="${SYSTEMD_USER_DIR}/${SERVICE_NAME}-preset.ini"

# Load environment

load_env() {
    # Capture environment overrides passed by caller
    local env_lchat_port="${LCHAT_PORT:-}"
    local env_lchat_host="${LCHAT_HOST:-}"
    local env_lchat_device="${LCHAT_DEVICE:-}"
    local env_lchat_threads="${LCHAT_THREADS:-}"
    local env_lchat_n_gpu_layers="${LCHAT_N_GPU_LAYERS:-}"
    local env_lchat_embedding_enabled="${LCHAT_EMBEDDING_ENABLED:-}"
    local env_lmbd_enabled="${LMBD_ENABLED:-}"
    local env_lcomp_enabled="${LCOMP_ENABLED:-}"
    local env_lchat_chat_template_file="${LCHAT_CHAT_TEMPLATE_FILE:-}"
    local env_lchat_chat_template_kwargs="${LCHAT_CHAT_TEMPLATE_KWARGS:-}"
    local env_lchat_mtp="${LCHAT_MTP:-}"
    local env_lchat_extra_args="${LCHAT_EXTRA_ARGS:-}"
    local env_lmbd_extra_args="${LMBD_EXTRA_ARGS:-}"
    local env_lcomp_extra_args="${LCOMP_EXTRA_ARGS:-}"

    # Default parameters for server/chat section
    LCHAT_PORT=20080
    LCHAT_HOST=127.0.0.1
    LCHAT_DEVICE=""
    LCHAT_THREADS=4
    LCHAT_N_GPU_LAYERS=999
    LCHAT_MODEL=/data/public/machine-learning/models/vision-text/BigBang-v1-IQ4_XS.gguf
    LCHAT_ALIAS=qwen3
    LCHAT_CTX_SIZE=240384
    LCHAT_PARALLEL=2
    LCHAT_MMPROJ=/data/public/machine-learning/models/vision-text/BigBang-v1-mmproj-f16.gguf
    LCHAT_CHAT_TEMPLATE_FILE=""
    LCHAT_CHAT_TEMPLATE_KWARGS='{"enable_thinking": true}'
    LCHAT_MTP=""
    LCHAT_SPECULATIVE="--spec-type draft-mtp --spec-draft-n-max 3 --spec-draft-type-k q4_0 --spec-draft-type-v q4_0"
    LCHAT_CACHE_TYPE_K=q4_0
    LCHAT_CACHE_TYPE_V=q4_0
    LCHAT_EXTRA_ARGS=""

    # Default parameters for embedding section
    LMBD_ENABLED=true
    LMBD_MODEL=/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf
    LMBD_ALIAS=qwen3-embedding
    LMBD_CTX_SIZE=16384
    LMBD_PARALLEL=2
    LMBD_N_GPU_LAYERS=""
    LMBD_THREADS=""
    LMBD_UBATCH_SIZE=16384
    LMBD_CACHE_TYPE_K=q8_0
    LMBD_CACHE_TYPE_V=q8_0
    # shellcheck disable=SC2034
    LMBD_EXTRA_ARGS="--flash-attn on"

    # Default parameters for completion section
    LCOMP_ENABLED=true
    LCOMP_MODEL=/data/public/machine-learning/models/completion/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf
    LCOMP_ALIAS=qwen-coder-fim
    LCOMP_CTX_SIZE=8192
    LCOMP_PARALLEL=2
    LCOMP_N_GPU_LAYERS=""
    LCOMP_THREADS=""
    LCOMP_CACHE_TYPE_K=q4_0
    LCOMP_CACHE_TYPE_V=q4_0
    LCOMP_EXTRA_ARGS=""

    # Embedding port mirror
    LMBD_MIRROR_PORT=20082

    # Sidecar configuration
    LCHAT_SIDECARS="portmirror"

    # Source the env file if it exists
    if [[ -f "$ENV_FILE" ]]; then
        set +u
        # shellcheck disable=SC1090
        source "$ENV_FILE"
        set -u
    fi

    # Support LMBD_N_UBATCH as alias for LMBD_UBATCH_SIZE
    if [[ -n "${LMBD_N_UBATCH:-}" ]]; then
        LMBD_UBATCH_SIZE="${LMBD_N_UBATCH}"
    fi

    # Resolve overrides
    LCHAT_PORT="${env_lchat_port:-${LCHAT_PORT}}"
    LCHAT_HOST="${env_lchat_host:-${LCHAT_HOST}}"
    LCHAT_DEVICE="${env_lchat_device:-${LCHAT_DEVICE}}"
    LCHAT_THREADS="${env_lchat_threads:-${LCHAT_THREADS}}"
    LCHAT_N_GPU_LAYERS="${env_lchat_n_gpu_layers:-${LCHAT_N_GPU_LAYERS}}"

    # Resolve embedding activation override
    if [[ -n "$env_lchat_embedding_enabled" ]]; then
        LMBD_ENABLED="$env_lchat_embedding_enabled"
    elif [[ -n "$env_lmbd_enabled" ]]; then
        LMBD_ENABLED="$env_lmbd_enabled"
    fi

    if [[ "${LMBD_ENABLED}" =~ ^(false|0|no|FALSE|NO)$ ]]; then
        LMBD_ENABLED=false
    else
        LMBD_ENABLED=true
    fi

    # Resolve completion activation override
    LCOMP_ENABLED="${env_lcomp_enabled:-${LCOMP_ENABLED}}"
    if [[ "${LCOMP_ENABLED}" =~ ^(false|0|no|FALSE|NO)$ ]]; then
        LCOMP_ENABLED=false
    else
        LCOMP_ENABLED=true
    fi

    # Fallback: if LCOMP_ENABLED is true but the model file doesn't exist, turn it off and warn
    if [[ "${LCOMP_ENABLED}" == "true" && ! -f "${LCOMP_MODEL}" ]]; then
        echo "Warning: Completion model file not found at ${LCOMP_MODEL}. Disabling code completion." >&2
        LCOMP_ENABLED=false
    fi

    # Resolve template overrides
    LCHAT_CHAT_TEMPLATE_FILE="${env_lchat_chat_template_file:-${LCHAT_CHAT_TEMPLATE_FILE}}"
    LCHAT_CHAT_TEMPLATE_KWARGS="${env_lchat_chat_template_kwargs:-${LCHAT_CHAT_TEMPLATE_KWARGS}}"
    LCHAT_MTP="${env_lchat_mtp:-${LCHAT_MTP}}"
    LCHAT_EXTRA_ARGS="${env_lchat_extra_args:-${LCHAT_EXTRA_ARGS}}"
    LMBD_EXTRA_ARGS="${env_lmbd_extra_args:-${LMBD_EXTRA_ARGS}}"
    LCOMP_EXTRA_ARGS="${env_lcomp_extra_args:-${LCOMP_EXTRA_ARGS}}"

    # Compute default portmirror sidecar CMD if not explicitly set by user
    if [[ -z "${LCHAT_SIDECAR_PORTMIRROR_CMD:-}" ]]; then
        LCHAT_SIDECAR_PORTMIRROR_CMD="bash -c 'if [ \"\${LMBD_ENABLED}\" = \"true\" ]; then exec socat TCP-LISTEN:\${LMBD_MIRROR_PORT:-20082},fork,reuseaddr TCP:\${LCHAT_HOST:-127.0.0.1}:\${LCHAT_PORT:-20080}; else exec sleep infinity; fi'"
    fi

    if [[ -n "${HIP_VISIBLE_DEVICES+x}" ]]; then
        export HIP_VISIBLE_DEVICES
    fi
    if [[ -n "${CUDA_VISIBLE_DEVICES+x}" ]]; then
        export CUDA_VISIBLE_DEVICES
    fi

    # Export any GGML_ variables so that child processes see them
    local var
    for var in $(compgen -v | grep ^GGML_); do
        export "${var?}"
    done
}

# Sanitize a sidecar name to a valid shell variable suffix (uppercase, special chars → _)
sanitize_var_name() {
    local result
    result=$(printf '%s' "$1" | tr '[:lower:]' '[:upper:]' | tr -c '[:alnum:]' '_')
    echo "$result"
}

# Sidecar infrastructure

FALLBACK_SIDECAR_PIDS=()
FALLBACK_SIDECAR_NAMES=()

spawn_fallback_sidecars() {
    local sidecars_val="${LCHAT_SIDECARS:-}"
    sidecars_val="${sidecars_val//;/ }"
    sidecars_val="${sidecars_val//$'\n'/ }"

    for sidecar in ${sidecars_val}; do
        local var_name
        var_name=$(sanitize_var_name "$sidecar")
        local cmd_var="LCHAT_SIDECAR_${var_name}_CMD"
        local cmd_val="${!cmd_var:-}"
        if [ -z "$cmd_val" ]; then
            echo "Warning: Sidecar '$sidecar' has no LCHAT_SIDECAR_${var_name}_CMD defined. Skipping." >&2
            continue
        fi

        local args_var="LCHAT_SIDECAR_${var_name}_ARGS"
        local args_val="${!args_var:-}"

        echo "Starting sidecar: $sidecar"
        (
            # Execute with current environment (LMBD_ENABLED etc. are exported)
            eval "exec $cmd_val $args_val"
        ) &
        FALLBACK_SIDECAR_PIDS+=($!)
        FALLBACK_SIDECAR_NAMES+=("$sidecar")
    done
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
        if declare -p "$key" &>/dev/null || [[ "$key" =~ ^LRR_ || "$key" =~ ^LMBD_ || "$key" =~ ^LCHAT_ || "$key" =~ ^LSTT_ || "$key" =~ ^LTTS_ || "$key" =~ ^LCOMP_ ]]; then
            printf -v "$key" "%s" "$val"
        fi
        SETENV_OPTS+=("--setenv=${key}=${val}")
    done
}

# Helper to execute systemctl commands only if systemd user manager is reachable

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

# Shared Sandboxing Configuration

get_shared_options() {
    local mode="$1" # "service" or "transient"
    local home_spec
    if [ "$mode" = "service" ]; then
        home_spec="%h"
    else
        home_spec="$HOME"
    fi

    # Environment file & Working directory
    echo "EnvironmentFile=-${home_spec}/.config/systemd/user/local-chat.env"
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
    echo "ReadOnlyPaths=/etc/ssl /etc/ca-certificates /etc/resolv.conf /etc/hosts /etc/nsswitch.conf"
    echo "ReadWritePaths=/data/public/machine-learning"

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

# Embedded service file (heredoc written by install/start/restart)

# Helper to get unified arguments for llama-server
get_llama_args() {
    local -n out_args=$1
    out_args=(
        --host "${LCHAT_HOST}"
        --port "${LCHAT_PORT}"
        --models-preset "${PRESET_FILE}"
    )

    if [[ -n "${LCHAT_DEVICE:-}" ]]; then
        out_args+=(--device "${LCHAT_DEVICE}")
    fi

    if [[ -n "${LCHAT_MTP:-}" ]]; then
        if [[ ! -f "${LCHAT_MTP}" ]]; then
            echo "Error: MTP draft model file not found at ${LCHAT_MTP}." >&2
            echo "Run 'scripts/local-download.sh <target_dir> --llm' to download required models." >&2
            exit 1
        fi
        out_args+=(--model-draft "${LCHAT_MTP}")
    fi

    if [[ -n "${LCHAT_SPECULATIVE:-}" ]]; then
        local speculative_arr=()
        eval "speculative_arr=(${LCHAT_SPECULATIVE})"
        out_args+=("${speculative_arr[@]}")
    fi

    if [[ -n "${LCHAT_EXTRA_ARGS:-}" ]]; then
        local extra_arr=()
        eval "extra_arr=(${LCHAT_EXTRA_ARGS})"
        out_args+=("${extra_arr[@]}")
    fi
}

append_extra_args_to_preset() {
    local extra_args="$1"
    if [[ -z "$extra_args" ]]; then
        return
    fi

    local tokens=()
    eval "tokens=(${extra_args})"

    local i=0
    while [ $i -lt ${#tokens[@]} ]; do
        local token="${tokens[$i]}"
        if [[ "$token" =~ = ]]; then
            local k="${token%%=*}"
            local v="${token#*=}"
            k="${k#--}"
            echo "${k} = ${v}"
            i=$((i + 1))
        elif [[ "$token" =~ ^-- ]]; then
            local k="${token#--}"
            local next_idx=$((i + 1))
            if [ $next_idx -lt ${#tokens[@]} ] && [[ ! "${tokens[$next_idx]}" =~ ^-- ]]; then
                echo "${k} = ${tokens[$next_idx]}"
                i=$((i + 2))
            else
                echo "${k} = true"
                i=$((i + 1))
            fi
        else
            i=$((i + 1))
        fi
    done
}

generate_preset_file() {
    local alias="${LCHAT_ALIAS:-qwen3}"
    local m_ngl="${LCHAT_N_GPU_LAYERS:-999}"
    local m_threads="${LCHAT_THREADS:-4}"

    mkdir -p "$(dirname "${PRESET_FILE}")"

    cat <<EOF
[*]
ngl = ${m_ngl}
threads = ${m_threads}
flash-attn = on

[${alias}]
model = ${LCHAT_MODEL}
ctx-size = ${LCHAT_CTX_SIZE}
parallel = ${LCHAT_PARALLEL}
EOF

    if [[ -n "${LCHAT_CACHE_TYPE_K:-}" ]]; then
        echo "cache-type-k = ${LCHAT_CACHE_TYPE_K}"
    fi
    if [[ -n "${LCHAT_CACHE_TYPE_V:-}" ]]; then
        echo "cache-type-v = ${LCHAT_CACHE_TYPE_V}"
    fi
    if [[ -n "${LCHAT_MMPROJ:-}" ]]; then
        echo "mmproj = ${LCHAT_MMPROJ}"
    fi
    if [[ -n "${LCHAT_CHAT_TEMPLATE_FILE:-}" ]]; then
        echo "chat-template-file = ${LCHAT_CHAT_TEMPLATE_FILE}"
    else
        echo "jinja = on"
    fi
    if [[ -n "${LCHAT_CHAT_TEMPLATE_KWARGS:-}" ]]; then
        echo "chat-template-kwargs = ${LCHAT_CHAT_TEMPLATE_KWARGS}"
    fi

    if [ "${LMBD_ENABLED}" = "true" ]; then
        local e_alias="${LMBD_ALIAS:-qwen3-embedding}"
        local e_ngl="${LMBD_N_GPU_LAYERS:-${m_ngl}}"
        local e_threads="${LMBD_THREADS:-${m_threads}}"
        cat <<EOF

[${e_alias}]
model = ${LMBD_MODEL}
embedding = true
pooling = last
ctx-size = ${LMBD_CTX_SIZE}
parallel = ${LMBD_PARALLEL}
ngl = ${e_ngl}
threads = ${e_threads}
ubatch-size = ${LMBD_UBATCH_SIZE}
EOF
        if [[ -n "${LMBD_CACHE_TYPE_K:-}" ]]; then
            echo "cache-type-k = ${LMBD_CACHE_TYPE_K}"
        fi
        if [[ -n "${LMBD_CACHE_TYPE_V:-}" ]]; then
            echo "cache-type-v = ${LMBD_CACHE_TYPE_V}"
        fi
        if [[ -n "${LMBD_EXTRA_ARGS:-}" ]]; then
            append_extra_args_to_preset "${LMBD_EXTRA_ARGS}"
        fi
    fi

    if [ "${LCOMP_ENABLED}" = "true" ]; then
        local c_alias="${LCOMP_ALIAS:-qwen-coder-fim}"
        local c_ngl="${LCOMP_N_GPU_LAYERS:-${m_ngl}}"
        local c_threads="${LCOMP_THREADS:-${m_threads}}"
        cat <<EOF

[${c_alias}]
model = ${LCOMP_MODEL}
ctx-size = ${LCOMP_CTX_SIZE}
parallel = ${LCOMP_PARALLEL}
ngl = ${c_ngl}
threads = ${c_threads}
EOF
        if [[ -n "${LCOMP_CACHE_TYPE_K:-}" ]]; then
            echo "cache-type-k = ${LCOMP_CACHE_TYPE_K}"
        fi
        if [[ -n "${LCOMP_CACHE_TYPE_V:-}" ]]; then
            echo "cache-type-v = ${LCOMP_CACHE_TYPE_V}"
        fi
        if [[ -n "${LCOMP_EXTRA_ARGS:-}" ]]; then
            append_extra_args_to_preset "${LCOMP_EXTRA_ARGS}"
        fi
    fi
}

generate_launcher_script() {
    local args
    get_llama_args args

    local sidecars_val="${LCHAT_SIDECARS:-}"
    sidecars_val="${sidecars_val//;/ }"
    sidecars_val="${sidecars_val//$'\n'/ }"

    local has_sidecars=false
    for sidecar in ${sidecars_val}; do
        local var_name
        var_name=$(sanitize_var_name "$sidecar")
        local cmd_var="LCHAT_SIDECAR_${var_name}_CMD"
        if [ -n "${!cmd_var:-}" ]; then
            has_sidecars=true
            break
        fi
    done

    cat <<'HEADER'
#!/usr/bin/env bash
set -euo pipefail
HEADER

    if [ "$has_sidecars" = "true" ]; then
        # Generate launcher that starts main process, then sidecars, then wait -n
        echo ""
        echo "# Start llama-server in background"
        printf '%s' "${LLAMA_SERVER_BIN:-llama-server}"
        for arg in "${args[@]}"; do
            printf ' %q' "$arg"
        done
        echo ' &'
        echo 'MAIN_PID=$!'
        echo 'sleep 2'
        echo 'if ! kill -0 "$MAIN_PID" 2>/dev/null; then'
        echo '    echo "Main llama-server process (PID $MAIN_PID) failed to start." >&2'
        echo '    exit 1'
        echo 'fi'
        echo ""
        echo "# Start sidecars"
        local idx=0
        for sidecar in ${sidecars_val}; do
            local var_name
            var_name=$(sanitize_var_name "$sidecar")
            local cmd_var="LCHAT_SIDECAR_${var_name}_CMD"
            local cmd_val="${!cmd_var:-}"
            if [ -z "$cmd_val" ]; then
                continue
            fi

            local args_var="LCHAT_SIDECAR_${var_name}_ARGS"
            local args_val="${!args_var:-}"

            echo "echo \"Starting sidecar: $sidecar\""
            echo "$cmd_val $args_val &"
            echo "SIDECAR_PID_${idx}=\$!"
            idx=$((idx + 1))
        done
        echo ""
        echo "# Wait for any process to exit"
        echo 'wait -n'
        echo ""
        echo "# Report which process died"
        echo 'if ! kill -0 "$MAIN_PID" 2>/dev/null; then'
        echo '    echo "Main llama-server process (PID $MAIN_PID) terminated."'
        echo 'fi'
        idx=0
        for sidecar in ${sidecars_val}; do
            local var_name
            var_name=$(sanitize_var_name "$sidecar")
            local cmd_var="LCHAT_SIDECAR_${var_name}_CMD"
            if [ -z "${!cmd_var:-}" ]; then
                continue
            fi
            echo "if ! kill -0 \"\$SIDECAR_PID_${idx}\" 2>/dev/null; then"
            echo "    echo \"Sidecar $sidecar (PID \$SIDECAR_PID_${idx}) terminated.\""
            echo "fi"
            idx=$((idx + 1))
        done
        echo 'exit 1'
    else
        # No sidecars, just exec llama-server directly
        printf 'exec %s' "${LLAMA_SERVER_BIN:-llama-server}"
        for arg in "${args[@]}"; do
            printf ' %q' "$arg"
        done
        echo ""
    fi
}

generate_service_file() {
    load_env
    local PRESET_FILE="%h/.config/systemd/user/local-chat-preset.ini"
    local launcher_path="%h/.config/systemd/user/local-chat-launcher.sh"

    cat <<EOF
[Unit]
Description=Local Chat Inference Server (llama-server)
Documentation=https://github.com/ggml-org/llama.cpp
After=network.target

[Service]
Type=simple
$(get_shared_options service)
ExecStart=/bin/bash ${launcher_path}

Restart=on-failure
RestartSec=10s

StandardOutput=journal
StandardError=journal
SyslogIdentifier=local-chat

[Install]
WantedBy=default.target
EOF
}

# Embedded default env file (heredoc written by install)

generate_env_file() {
    cat <<'EOF'
# local-chat.env
# Configuration file for local-chat.service.
#
# Combined Chat and Embedding settings. Sourced by local-chat.sh.
# Reload with:  local-chat.sh restart

# ### SERVER SETTINGS

# Port to bind the server to (default: 20080)
LCHAT_PORT=20080

# Host to bind the server to (127.0.0.1 for local access only)
LCHAT_HOST=127.0.0.1

# GPU/CPU backend device to use (run 'llama-cli --list-devices' for valid names)
# By default, llama-server automatically selects the best available device.
# To force a specific backend device, uncomment one of the options below:
# LCHAT_DEVICE="ROCm0"
# LCHAT_DEVICE="Vulkan0"
# LCHAT_DEVICE="BLAS"  # Force CPU OpenBLAS acceleration
# LCHAT_DEVICE="none"  # Force plain CPU execution (without OpenBLAS)
LCHAT_DEVICE=""

# Number of CPU threads to use (default: 4)
LCHAT_THREADS=4

# Number of layers to offload to GPU (all=999, none=0)
LCHAT_N_GPU_LAYERS=999


# ### CHAT / VISION MODEL SETTINGS

# Path to the chat model file
# spec-type mtp Model (original Qwen3.6 MoE)
# LCHAT_MODEL=/data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact-mtp.gguf
# Default Model: BigBang-v1 (Qwen3.6-35B-A3B fine-tune via self-evolving synthetic tasks)
LCHAT_MODEL=/data/public/machine-learning/models/vision-text/BigBang-v1-IQ4_XS.gguf
# Separate MTP draft model file path (leave empty when using built-in MTP model)
LCHAT_MTP=""

# Speculative Decoding config (default: CPU N-Gram speculative decoding)
# To enable MTP and use MTP speculative decoding with 2 draft tokens instead:
#   1. Use model in LCHAT_MODEL with integrated mtp, or add path to mtp draft model in LCHAT_MTP
#   2. Set LCHAT_SPECULATIVE="--spec-type ngram-simple --spec-ngram-simple-size-n 6 --spec-ngram-simple-size-m 4"
# LCHAT_SPECULATIVE="--spec-type draft-mtp --spec-draft-n-max 3 --spec-draft-type-k q4_0 --spec-draft-type-v q4_0"
LCHAT_SPECULATIVE="--spec-type ngram-simple --spec-ngram-simple-size-n 6 --spec-ngram-simple-size-m 4"

# Model alias used by client integrations (default: qwen3)
LCHAT_ALIAS=qwen3

# Context size (default: 240384)
LCHAT_CTX_SIZE=240384

# Parallel request slots (default: 2, true parallel: 240384/2 = 120192 ctx per slot)
LCHAT_PARALLEL=2

# Multimodal projector arguments (optional)
LCHAT_MMPROJ=/data/public/machine-learning/models/vision-text/BigBang-v1-mmproj-f16.gguf

# Chat template file (optional; leave empty to use the integrated BigBang-v1 model chat template via 'jinja = on')
# LCHAT_CHAT_TEMPLATE_FILE=/data/public/machine-learning/models/vision-text/Qwen3.6-chat_template.jinja
LCHAT_CHAT_TEMPLATE_FILE=""

# Additional parameters for the Jinja chat template parser (JSON string)
# Default '{"enable_thinking": true}' enables chain-of-thought/thinking by default.
LCHAT_CHAT_TEMPLATE_KWARGS='{"enable_thinking": true}'

# KV cache type (default: q4_0)
LCHAT_CACHE_TYPE_K=q4_0
LCHAT_CACHE_TYPE_V=q4_0

# Extra arguments to pass to chat service (default: "--temp 0.6 --top-k 20 --repeat-penalty 1.1")
# --top-k 20: https://qwen.ai/blog?id=qwen3.6-35b-a3b
#   * Terminal-Bench 2.0: Harbor/Terminus-2 harness; 3h timeout, 32 CPU/48 GB RAM; temp=1.0, top_p=0.95, top_k=20, max_tokens=80K, 256K ctx; avg of 5 runs.
# --repeat-penalty 1.1: https://www.reddit.com/r/hermesagent/comments/1tk8x46/infinite_loop/
LCHAT_EXTRA_ARGS="--temp 0.6 --top-k 20 --repeat-penalty 1.1"

# ### SIDECARS CONFIGURATION

# Space or semicolon separated list of sidecar names (default: "portmirror")
# Each sidecar runs as a background process alongside llama-server.
# LCHAT_SIDECARS="portmirror"
LCHAT_SIDECARS=""

# --- Port Mirror Sidecar (default built-in)
# Checks LMBD_ENABLED at runtime: socat port mirror when true, sleep when false.
# To disable the portmirror, remove "portmirror" from LCHAT_SIDECARS.
LCHAT_SIDECAR_PORTMIRROR_CMD="bash -c 'if [ \"\${LMBD_ENABLED}\" = \"true\" ]; then exec socat TCP-LISTEN:\${LMBD_MIRROR_PORT:-20082},fork,reuseaddr TCP:\${LCHAT_HOST:-127.0.0.1}:\${LCHAT_PORT:-20080}; else exec sleep infinity; fi'"

# Custom sidecar example:
# LCHAT_SIDECARS="portmirror mycustom"
# LCHAT_SIDECAR_MYCUSTOM_CMD="/path/to/command"
# LCHAT_SIDECAR_MYCUSTOM_ARGS="--flag value"


# ### TEXT EMBEDDING MODEL SETTINGS

# Whether to enable the text embedding model in this server instance (default: true)
LMBD_ENABLED=true

# EMBEDDING PORT MIRROR
# Port to mirror embedding API on (default: 20082, matching standalone local-embedding)
# When LMBD_ENABLED=true, the portmirror sidecar forwards this port → LCHAT_PORT
# When LMBD_ENABLED=false, the portmirror sidecar sleeps (port unused)
LMBD_MIRROR_PORT=20082

# Path to the text embedding model file
LMBD_MODEL=/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf

# Model alias used by client integrations (default: qwen3-embedding)
LMBD_ALIAS=qwen3-embedding

# Context size (default: 16384)
LMBD_CTX_SIZE=16384

# Parallel request slots (default: 2)
LMBD_PARALLEL=2

# micro-batch size (default: 16384, matching context size for long prompt embeddings)
LMBD_UBATCH_SIZE=16384

# KV cache type (default: q8_0)
LMBD_CACHE_TYPE_K=q8_0
LMBD_CACHE_TYPE_V=q8_0

# Extra arguments for embedding (optional)
LMBD_EXTRA_ARGS="--flash-attn on"


# ### CODE COMPLETION FIM SETTINGS

# Whether to enable completions model in this server instance (default: true)
LCOMP_ENABLED=true

# Path to the completions model file
LCOMP_MODEL=/data/public/machine-learning/models/completion/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf

# Model alias used by client integrations (default: qwen-coder-fim)
LCOMP_ALIAS=qwen-coder-fim

# Context size (default: 8192)
LCOMP_CTX_SIZE=8192

# Parallel request slots (default: 2)
LCOMP_PARALLEL=2

# KV cache type (default: q4_0 for completions)
LCOMP_CACHE_TYPE_K=q4_0
LCOMP_CACHE_TYPE_V=q4_0

# Extra arguments for completions (optional)
LCOMP_EXTRA_ARGS=""


EOF
}

# Write service file

write_service_file() {
    load_env
    # Generate the actual model preset file on disk
    generate_preset_file >"${SYSTEMD_USER_DIR}/${SERVICE_NAME}-preset.ini"
    chmod 600 "${SYSTEMD_USER_DIR}/${SERVICE_NAME}-preset.ini"

    # Generate the launcher script (handles sidecars)
    generate_launcher_script >"${SYSTEMD_USER_DIR}/${SERVICE_NAME}-launcher.sh"
    chmod 755 "${SYSTEMD_USER_DIR}/${SERVICE_NAME}-launcher.sh"

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

    # Create directory if needed
    mkdir -p "${SYSTEMD_USER_DIR}"

    # Write env config file only if it doesn't exist (preserve user edits)
    if [[ -f "${ENV_FILE}" ]] && [ "${new_config}" = "false" ]; then
        echo "Warning: Env file already exists, skipping: ${ENV_FILE}"
        echo "Remove it manually or use --new-config if you want to regenerate the defaults."
    else
        echo "Writing default env config file: ${ENV_FILE}"
        generate_env_file >"${ENV_FILE}"
        chmod 600 "${ENV_FILE}"
        echo "Env file written."
    fi

    # Write service file and preset
    echo "Writing service file and preset: ${SERVICE_FILE}"
    write_service_file
    echo "Service file written."

    # Enable service
    echo "Enabling ${SERVICE_NAME}.service..."
    run_systemctl enable "${SERVICE_NAME}.service"

    if [ "$no_start" = "true" ]; then
        echo "Stopping service if running (--no-start specified)..."
        run_systemctl stop "${SERVICE_NAME}.service" || true
    else
        echo "Starting/Restarting service automatically..."
        run_systemctl restart "${SERVICE_NAME}.service"
    fi

    echo "Installation complete."
    echo ""
    echo "  Service:  ${SERVICE_FILE}"
    echo "  Env:      ${ENV_FILE}"
    echo "  Preset:   ${SYSTEMD_USER_DIR}/${SERVICE_NAME}-preset.ini"
    echo "  Launcher: ${SYSTEMD_USER_DIR}/${SERVICE_NAME}-launcher.sh"
    echo ""
    echo "  Edit the env file to select model/mmproj/template, then:"
    echo "    $0 restart"
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
        rm -f "${SYSTEMD_USER_DIR}/${SERVICE_NAME}-preset.ini"
        rm -f "${SYSTEMD_USER_DIR}/${SERVICE_NAME}-launcher.sh"
        run_systemctl daemon-reload
        echo "Removed service file, preset, and launcher."
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

    # Generate the actual model preset file on disk before executing
    generate_preset_file >"${SYSTEMD_USER_DIR}/${SERVICE_NAME}-preset.ini"
    chmod 600 "${SYSTEMD_USER_DIR}/${SERVICE_NAME}-preset.ini"

    local args
    get_llama_args args

    if ! is_systemd_running; then
        echo "Warning: Systemd is not running. Running llama-server directly in foreground..."
        # Export env vars so sidecars see them
        export LMBD_ENABLED LMBD_MIRROR_PORT LCHAT_HOST LCHAT_PORT
        if [ $# -gt 0 ]; then
            "${LLAMA_SERVER_BIN:-llama-server}" "$@" &
        else
            "${LLAMA_SERVER_BIN:-llama-server}" "${args[@]}" &
        fi
        local main_pid=$!
        sleep 2
        if ! kill -0 "$main_pid" 2>/dev/null; then
            echo "Main llama-server process (PID $main_pid) failed to start." >&2
            exit 1
        fi
        spawn_fallback_sidecars
        wait -n

        # Identify which process died
        if ! kill -0 "$main_pid" 2>/dev/null; then
            echo "Main llama-server process (PID $main_pid) terminated."
        fi
        for i in "${!FALLBACK_SIDECAR_PIDS[@]}"; do
            local pid="${FALLBACK_SIDECAR_PIDS[$i]}"
            local name="${FALLBACK_SIDECAR_NAMES[$i]}"
            if ! kill -0 "$pid" 2>/dev/null; then
                echo "Sidecar $name (PID $pid) terminated."
            fi
        done
        exit 1
    fi

    echo "Starting llama-server as a transient systemd service with args: $*"

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

    if [ $# -gt 0 ]; then
        # shellcheck disable=SC2086
        systemd-run "${opts[@]}" "${SETENV_OPTS[@]}" -- "${LLAMA_SERVER_BIN:-llama-server}" "$@"
    else
        systemd-run "${opts[@]}" "${SETENV_OPTS[@]}" -- "${LLAMA_SERVER_BIN:-llama-server}" "${args[@]}"
    fi
}

cmd_shell() {
    echo "Starting interactive shell in the llama-server systemd environment..."

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
    echo "Running command inside the llama-server environment: $*"

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

# Wait for server to become ready (Vulkan shader compilation takes time on first load)
wait_for_endpoint() {
    local url="$1"
    local max_retries="${2:-30}"
    local delay="${3:-2}"
    local label="${4:-server}"
    for i in $(seq 1 $max_retries); do
        if curl -s -f "$url" >/dev/null 2>&1; then
            return 0
        fi
        echo "  Waiting for ${label} to become ready... ($i/$max_retries)"
        sleep "$delay"
    done
    echo "Error: ${label} did not become ready after $((max_retries * delay))s." >&2
    return 1
}

cmd_test() {
    echo "Running local-chat validation tests..."
    load_env

    local host="${LCHAT_HOST:-127.0.0.1}"
    local port="${LCHAT_PORT:-20080}"
    local alias="${LCHAT_ALIAS:-qwen3}"

    local base_url="http://${host}:${port}"
    echo "Using endpoint base: ${base_url}"

    # Wait for server to become ready (shader compilation on first load takes time)
    wait_for_endpoint "${base_url}/v1/models" 30 2 "local-chat" || return 1

    local benchmark=false
    local skip_prefill=false
    local skip_distractor=false
    local skip_all_chat=false
    local skip_image=false
    local skip_embedding=false
    local skip_completion=false
    local repeat=""
    local extra_args=()
    while [ $# -gt 0 ]; do
        case "$1" in
        --benchmark) benchmark=true ;;
        --skip-prefill) skip_prefill=true ;;
        --skip-distractor) skip_distractor=true ;;
        --skip-chat | --skip-all-chat) skip_all_chat=true ;;
        --skip-image) skip_image=true ;;
        --skip-embedding) skip_embedding=true ;;
        --skip-completion) skip_completion=true ;;
        --repeat)
            shift
            repeat="$1"
            ;;
        *)
            extra_args+=("$1")
            ;;
        esac
        shift
    done

    if [ "$benchmark" = "true" ]; then
        local context_file
        context_file="/data/public/machine-learning/models/benchmark-context.md"
        if [[ ! -f "$context_file" ]]; then
            context_file="$(dirname "$(dirname "$LCHAT_MODEL")")/benchmark-context.md"
        fi
        if [[ ! -f "$context_file" ]]; then
            context_file="/tmp/benchmark-context.md"
        fi
        if [[ ! -f "$context_file" ]]; then
            echo "benchmark-context.md not found. Generating it via download_skills_context.py..."
            python3 "$(dirname "$0")/../scripts/download_skills_context.py" --output "$context_file" || true
        fi

        local repeat_arg=()
        if [ -n "$repeat" ]; then
            repeat_arg=(--repeat "$repeat")
        fi

        # 1. Run chat benchmark if not skipped
        if [ "$skip_all_chat" = "false" ]; then
            local skip_prefill_arg=()
            if [ "$skip_prefill" = "true" ]; then
                skip_prefill_arg=(--skip-prefill)
            fi
            local skip_distractor_arg=()
            if [ "$skip_distractor" = "true" ]; then
                skip_distractor_arg=(--skip-distractor)
            fi
            local skip_image_arg=()
            if [ "$skip_image" = "true" ]; then
                skip_image_arg=(--skip-image)
            fi
            local image_file_arg=()
            local image_file_path
            image_file_path="$(dirname "$LCHAT_MODEL")/test_image.jpg"
            if [ -f "$image_file_path" ]; then
                image_file_arg=(--image-file "$image_file_path")
            fi

            echo "=== Running Chat Benchmark ==="
            python3 "$(dirname "$0")/../scripts/benchmark-helper.py" \
                --mode chat \
                --url "${base_url}" \
                --model "${alias}" \
                --context "${context_file}" \
                "${repeat_arg[@]}" \
                "${skip_prefill_arg[@]}" \
                "${skip_distractor_arg[@]}" \
                "${skip_image_arg[@]}" \
                "${image_file_arg[@]}" \
                "${extra_args[@]}"
        fi

        # 2. Run embedding benchmark if enabled and not skipped
        if [ "${LMBD_ENABLED}" = "true" ] && [ "$skip_embedding" = "false" ]; then
            local e_alias="${LMBD_ALIAS:-qwen3-embedding}"
            echo "=== Running Embedding Benchmark ==="
            python3 "$(dirname "$0")/../scripts/benchmark-helper.py" \
                --mode embedding \
                --url "${base_url}" \
                --model "${e_alias}" \
                --context "${context_file}" \
                "${repeat_arg[@]}" \
                "${extra_args[@]}"
        fi

        # 3. Run completion benchmark if enabled and not skipped
        if [ "${LCOMP_ENABLED}" = "true" ] && [ "$skip_completion" = "false" ]; then
            local c_alias="${LCOMP_ALIAS:-qwen-coder-fim}"
            local comp_file
            comp_file="/data/public/machine-learning/models/completion/test_fim.py"
            if [[ ! -f "$comp_file" ]]; then
                comp_file="$(dirname "$(dirname "$LCHAT_MODEL")")/completion/test_fim.py"
            fi
            if [[ ! -f "$comp_file" ]]; then
                comp_file="/tmp/test_fim.py"
            fi
            if [[ ! -f "$comp_file" ]]; then
                echo "test_fim.py not found. Downloading it..."
                curl -L -s -f -o "$comp_file" "https://raw.githubusercontent.com/psf/requests/main/src/requests/api.py" || true
            fi

            echo "=== Running Completion Benchmark ==="
            python3 "$(dirname "$0")/../scripts/benchmark-helper.py" \
                --mode completion \
                --url "${base_url}" \
                --model "${c_alias}" \
                --context "${comp_file}" \
                "${repeat_arg[@]}" \
                "${extra_args[@]}"
        fi
        return 0
    fi

    # Sequential validation test
    if [ "$skip_all_chat" = "false" ]; then
        echo "=== Testing Chat Completion ==="
        local chat_resp
        chat_resp=$(curl -s -f -X POST "${base_url}/v1/chat/completions" \
            -H "Content-Type: application/json" \
            -d "{
              \"model\": \"${alias}\",
              \"messages\": [
                {\"role\": \"user\", \"content\": \"Hello, respond with exactly: Hello World!\"}
              ]
            }")

        echo "${chat_resp}"
        if ! echo "${chat_resp}" | grep -q "choices"; then
            echo "Error: Chat completion test failed." >&2
            return 1
        fi
        echo "Chat completion: Success."
    fi

    if [ "${LMBD_ENABLED}" = "true" ] && [ "$skip_embedding" = "false" ]; then
        local e_alias="${LMBD_ALIAS:-qwen3-embedding}"
        echo "=== Testing Text Embeddings ==="
        local embed_resp
        embed_resp=$(curl -s -f -X POST "${base_url}/v1/embeddings" \
            -H "Content-Type: application/json" \
            -d "{
              \"model\": \"${e_alias}\",
              \"input\": \"Hello World\"
            }")

        echo "${embed_resp}"
        if ! echo "${embed_resp}" | grep -q "embedding"; then
            echo "Error: Text embedding test failed." >&2
            return 1
        fi
        echo "Text embedding: Success."
    fi

    if [ "${LCOMP_ENABLED}" = "true" ] && [ "$skip_completion" = "false" ]; then
        local c_alias="${LCOMP_ALIAS:-qwen-coder-fim}"
        echo "=== Testing Code Completion (FIM) ==="
        local comp_resp
        comp_resp=$(curl -s -f -X POST "${base_url}/v1/completions" \
            -H "Content-Type: application/json" \
            -d "{
              \"model\": \"${c_alias}\",
              \"prompt\": \"<|fim_prefix|>def add(a, b):\n    <|fim_suffix|>\n    return c<|fim_middle|>\",
              \"max_tokens\": 10,
              \"temperature\": 0.0
            }")

        echo "${comp_resp}"
        if ! echo "${comp_resp}" | grep -q "choices"; then
            echo "Error: Code completion FIM test failed." >&2
            return 1
        fi
        echo "Code completion FIM: Success."
    fi
}

cmd_cat() {
    load_env
    echo "=== Service File: ${SERVICE_FILE} ==="
    if [[ -f "${SERVICE_FILE}" ]]; then
        cat "${SERVICE_FILE}"
    else
        echo "(Service file does not exist. Run 'install' to create it.)"
    fi
    echo ""
    echo "=== Environment File: ${ENV_FILE} ==="
    if [[ -f "${ENV_FILE}" ]]; then
        cat "${ENV_FILE}"
    else
        echo "(Environment file does not exist. Run 'install' to create it.)"
    fi
    echo ""
    local preset_path="${SYSTEMD_USER_DIR}/${SERVICE_NAME}-preset.ini"
    echo "=== Preset File: ${preset_path} ==="
    if [[ -f "${preset_path}" ]]; then
        cat "${preset_path}"
    else
        echo "(Preset file does not exist. Run 'install' to create it.)"
    fi
    echo ""
    local launcher_path="${SYSTEMD_USER_DIR}/${SERVICE_NAME}-launcher.sh"
    echo "=== Launcher Script: ${launcher_path} ==="
    if [[ -f "${launcher_path}" ]]; then
        cat "${launcher_path}"
    else
        echo "(Launcher script does not exist. Run 'install' to create it.)"
    fi
    echo ""
    echo "=== Transient Execution Command (exec) ==="
    local args
    get_llama_args args
    echo "${LLAMA_SERVER_BIN:-llama-server} ${args[*]}"
}

usage() {
    cat <<EOF
Usage: $0 <command> [args...]
Commands:
  install [--no-start] [--new-config] - Setup service and default configuration (do not start service if --no-start is specified, overwrite configs with defaults if --new-config is specified)
  uninstall - Stop and remove systemd service and preset
  start     - Start the systemd service
  stop      - Stop the systemd service
  restart   - Restart the systemd service
  status    - View systemd service status
  enable    - Enable systemd service on boot
  disable   - Disable systemd service on boot
  logs      - Tail the systemd service logs
  edit      - Edit the .env config file and restart the service upon exit
  exec      - Run llama-server as a transient systemd user service
  run       - Run a command inside the llama-server environment
  shell     - Spawn an interactive shell in the llama-server environment
  cat       - Print service file, environment configuration, preset, launcher script, and transient exec command
  test [--benchmark [--skip-prefill] [--skip-all-chat] [--skip-distractor] [--skip-image] [--skip-embedding] [--skip_completion] [--repeat XX] ]
    - Run validation tests or benchmarks
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
