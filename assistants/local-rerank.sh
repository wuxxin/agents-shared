#!/usr/bin/env bash
# local-rerank.sh - Manage local llama-server systemd user service for Text Reranking
#
# Usage: local-rerank.sh <command> [args...]
#
# Manages a systemd user service (local-rerank.service) that runs llama-server
# serving the Text Reranker model (Qwen3-Reranker-0.6B via generative yes/no classification).
#
#

set -euo pipefail

# Paths

SYSTEMD_USER_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
SERVICE_NAME="local-rerank"
SERVICE_FILE="${SYSTEMD_USER_DIR}/${SERVICE_NAME}.service"
ENV_FILE="${SYSTEMD_USER_DIR}/${SERVICE_NAME}.env"

# Load environment

load_env() {
    # General parameters
    LRR_PORT=50086
    LRR_HOST=127.0.0.1
    LRR_ENGINE=llama
    LRR_ALIAS=qwen3-reranker

    # llama-server parameters (Qwen3-Reranker-0.6B: generative yes/no classifier, 40K ctx, Q4_K_M GGUF)
    LRR_LLAMA_MODEL=/data/public/machine-learning/models/reranker/Qwen3-Reranker-0.6B.Q4_K_M.gguf
    LRR_LLAMA_N_CTX=12288
    LRR_LLAMA_N_UBATCH=12288
    LRR_LLAMA_N_GPU_LAYERS=999
    LRR_LLAMA_THREADS=4
    LRR_LLAMA_PARALLEL=2
    # kv-unified + Q8_0 KV: 2 slots share one 16K-position pool (~448 MB). Sequential processing.
    LRR_LLAMA_DEVICE=""
    LRR_LLAMA_EXTRA_ARGS=""

    # TEI parameters (ettin-reranker-400m-v1 via ModernBertModel detection, requires tei-rocm >= pkgrel=6)
    LRR_TEI_MODEL=/data/public/machine-learning/models/reranker/ettin-reranker-400m-v1
    LRR_TEI_MAX_CONCURRENT=4 # 4 queue slots — GPU processes 1 at a time; queue absorbs others without VRAM cost
    LRR_TEI_MAX_BATCH_TOKENS=8192
    LRR_TEI_EXTRA_ARGS="--dtype bfloat16"
    LRR_TEI_DEVICE=""

    # Source the env file to get model paths and settings if it exists
    if [[ -f "$ENV_FILE" ]]; then
        set +u
        # shellcheck disable=SC1090
        source "$ENV_FILE"
        set -u
    fi

    # Auto-detect engine if not set (legacy configuration support)
    if [[ -z "${LRR_ENGINE:-}" ]]; then
        if [[ "${LRR_MODEL:-}" =~ \.gguf$ ]]; then
            LRR_ENGINE=llama
        else
            LRR_ENGINE=llama
        fi
    fi

    # Map generic variables based on selected engine for backward compatibility
    if [[ "${LRR_ENGINE}" == "tei" ]]; then
        LRR_MODEL="${LRR_TEI_MODEL:-${LRR_MODEL:-}}"
        # shellcheck disable=SC2034
        LRR_API_PATH=/rerank
    else
        LRR_MODEL="${LRR_LLAMA_MODEL:-${LRR_MODEL:-}}"
        # shellcheck disable=SC2034
        LRR_API_PATH=/v1/rerank

        # Keep existing mapping for llama parameters
        if [[ -n "${LRR_UBATCH_SIZE:-}" ]]; then
            LRR_LLAMA_N_UBATCH="${LRR_UBATCH_SIZE}"
        fi
        LRR_N_CTX="${LRR_LLAMA_N_CTX:-16384}"
        LRR_N_UBATCH="${LRR_LLAMA_N_UBATCH:-16384}"
        LRR_N_GPU_LAYERS="${LRR_LLAMA_N_GPU_LAYERS:-99}"
        LRR_THREADS="${LRR_LLAMA_THREADS:-8}"
        LRR_PARALLEL="${LRR_LLAMA_PARALLEL:-2}"
        LRR_DEVICE="${LRR_LLAMA_DEVICE:-}"
        LRR_EXTRA_ARGS="${LRR_LLAMA_EXTRA_ARGS:-}"
    fi

    # Device selection for TEI
    local active_device=""
    if [[ "${LRR_ENGINE}" == "tei" ]]; then
        active_device="${LRR_TEI_DEVICE:-${LRR_DEVICE:-}}"
        if [[ -n "${active_device}" ]]; then
            local dev_lower
            dev_lower=$(echo "${active_device}" | tr '[:upper:]' '[:lower:]')
            if [[ "$dev_lower" =~ [0-9]+ ]]; then
                local dev_idx
                dev_idx=$(echo "$dev_lower" | grep -o -E '[0-9]+' | head -n 1)
                export HIP_VISIBLE_DEVICES="${dev_idx}"
                export CUDA_VISIBLE_DEVICES="${dev_idx}"
            elif [[ "$dev_lower" == "cpu" || "$dev_lower" == "none" ]]; then
                export HIP_VISIBLE_DEVICES=""
                export CUDA_VISIBLE_DEVICES=""
            fi
        fi
        export TRUST_REMOTE_CODE=true
        # export PYTHONPATH="${HOME}/.config/systemd/user${PYTHONPATH:+:$PYTHONPATH}"  # TEI Python backends only
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
        if declare -p "$key" &>/dev/null || [[ "$key" =~ ^LRR_ || "$key" =~ ^LMBD_ || "$key" =~ ^LCHAT_ || "$key" =~ ^LSTT_ || "$key" =~ ^LTTS_ ]]; then
            printf -v "$key" "%s" "$val"
        fi
        SETENV_OPTS+=("--setenv=${key}=${val}")
    done
}

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
    echo "EnvironmentFile=-${home_spec}/.config/systemd/user/local-rerank.env"
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
        --model "${LRR_MODEL}"
        --reranking
        --kv-unified
        --ctx-size "${LRR_N_CTX}"
        --batch-size "${LRR_N_CTX}"
        --ubatch-size "${LRR_N_UBATCH}"
        --alias "${LRR_ALIAS}"
        --threads "${LRR_THREADS}"
        --parallel "${LRR_PARALLEL}"
        --n-gpu-layers "${LRR_N_GPU_LAYERS}"
        --host "${LRR_HOST}"
        --port "${LRR_PORT}"
    )

    if [[ -n "${LRR_DEVICE:-}" ]]; then
        out_args+=(--device "${LRR_DEVICE}")
    fi

    if [[ -n "${LRR_EXTRA_ARGS:-}" ]]; then
        local extra_arr=()
        eval "extra_arr=(${LRR_EXTRA_ARGS})"
        out_args+=("${extra_arr[@]}")
    fi
}

# Helper to get unified arguments for text-embeddings-router
get_tei_args() {
    local -n out_tei_args=$1
    out_tei_args=(
        --model-id "${LRR_MODEL}"
        --port "${LRR_PORT}"
        --hostname "${LRR_HOST}"
    )

    if [[ -n "${LRR_TEI_MAX_CONCURRENT:-}" ]]; then
        out_tei_args+=(--max-concurrent-requests "${LRR_TEI_MAX_CONCURRENT}")
    fi

    if [[ -n "${LRR_TEI_MAX_BATCH_TOKENS:-}" ]]; then
        out_tei_args+=(--max-batch-tokens "${LRR_TEI_MAX_BATCH_TOKENS}")
    fi

    if [[ -n "${LRR_TEI_EXTRA_ARGS:-}" ]]; then
        local extra_arr=()
        eval "extra_arr=(${LRR_TEI_EXTRA_ARGS})"
        out_tei_args+=("${extra_arr[@]}")
    fi
}

# Helper to format array of arguments for systemd ExecStart
format_exec_start() {
    local binary="$1"
    shift
    local cmd="$binary"
    for arg in "$@"; do
        local escaped="${arg//\\/\\\\}"
        escaped="${escaped//\"/\\\"}"
        if [[ "$escaped" =~ [[:space:]] ]]; then
            escaped="\"${escaped}\""
        fi
        cmd="${cmd} \\\\\n    ${escaped}"
    done
    echo -e "$cmd"
}

generate_service_file() {
    load_env
    local args
    local exec_cmd
    local description
    local doc_link

    if [[ "${LRR_ENGINE}" == "tei" ]]; then
        get_tei_args args
        exec_cmd=$(format_exec_start "${TEI_ROUTER_BIN:-text-embeddings-router}" "${args[@]}")
        description="Local Document Reranking Server (TEI)"
        doc_link="https://github.com/huggingface/text-embeddings-inference"
    else
        get_llama_args args
        exec_cmd=$(format_exec_start "${LLAMA_SERVER_BIN:-llama-server}" "${args[@]}")
        description="Local Document Reranking Server (llama-server + Qwen3-Reranker)"
        doc_link="https://github.com/ggml-org/llama.cpp"
    fi

    cat <<EOF
[Unit]
Description=${description}
Documentation=${doc_link}
After=network.target

[Service]
Type=simple
$(get_shared_options service)
ExecStart=${exec_cmd}

Restart=on-failure
RestartSec=10s

StandardOutput=journal
StandardError=journal
SyslogIdentifier=local-rerank

[Install]
WantedBy=default.target
EOF
}

# Embedded default env file (heredoc written by install)

generate_env_file() {
    cat <<'EOF'
# local-rerank.env

# Configuration for the local-rerank.service.
# Edit this file to switch engines, models, or tune runtime parameters.
# Reload with:  local-rerank.sh restart

# Active inference engine: 'llama' (llama-server) or 'tei' (Text Embeddings Inference)
# NOTE: TEI now supports ettin-reranker-400m-v1 via ModernBertModel detection (tei-rocm >= pkgrel=6).
#       Download: scripts/local-download.sh /data/public/machine-learning/models --reranker
LRR_ENGINE=llama

# Model alias for client integrations (default: qwen3-reranker)
LRR_ALIAS=qwen3-reranker

# Port to bind the server to (default: 50086)
LRR_PORT=50086

# Host to bind the server to (127.0.0.1 for local access only)
LRR_HOST=127.0.0.1

# API path for rerank endpoint (/v1/rerank for llama-server, /rerank for TEI)
LRR_API_PATH=/v1/rerank

# TEI (Text Embeddings Inference) ENGINE SETTINGS
#
# Alternative engine: set LRR_ENGINE=tei to switch from llama-server back to TEI.
# TEI auto-detects reranker model architecture and sets appropriate
# pooling and tokenization. TEI uses dynamic batching with static VRAM
# allocation, allowing efficient parallel reranking request handling.
#
# Path to the safetensors model directory
LRR_TEI_MODEL=/data/public/machine-learning/models/reranker/ettin-reranker-400m-v1

# Max concurrent request slots (default: 4, GPU processes 1 at a time; queue absorbs the rest without VRAM cost)
LRR_TEI_MAX_CONCURRENT=4

# Max total tokens in a dynamic batch (default: 8192, 1 × 8K single batch)
# TEI auto-sizes each batch: with 8K chunks this means ~1 request per forward pass
LRR_TEI_MAX_BATCH_TOKENS=8192

# GPU/CPU backend device index or name (e.g. rocm[:0], rocm:1, vulkan[:0], equals to auto if empty)
# Maps to HIP_VISIBLE_DEVICES / CUDA_VISIBLE_DEVICES internally for TEI
# LRR_TEI_DEVICE="rocm:0"

# Extra arguments to pass to text-embeddings-router
LRR_TEI_EXTRA_ARGS="--dtype bfloat16"

# Trust remote code to run custom models
TRUST_REMOTE_CODE=true

# Python search path for custom model patches (TEI Python backends only — not used by llama engine)
EOF
    echo "# PYTHONPATH=${SYSTEMD_USER_DIR}  # uncomment if using TEI engine"
    echo ""
    echo "# PyTorch CUDA memory allocator configuration (prevents VRAM fragmentation/OOM on large contexts)"
    echo "PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True"
    cat <<'EOF'


# LLAMA-SERVER ENGINE SETTINGS
#
# jina-reranker-v3 (alternative): Qwen3-0.6B causal decoder with a 2-layer MLP projector (1024→512→512, ReLU).
# Uses LAST-token pooling to produce 512-dim embeddings. Clients POST to /v1/embeddings and
# compute cosine similarity client-side for reranking. NOTE: requires GGUF with projector tensors
# and patched llama.cpp converter; the official GGUF lacks projector weights.
#
# Qwen3-Reranker-0.6B (current): generative yes/no classifier using rank pooling.
# Clients POST query + documents to /v1/rerank and receive relevance_score (P(yes)) directly.
# F16 KV cache (default) stores K/V in 16-bit per element. With --kv-unified, the 2 parallel
# slots share one 16384-position KV pool (~896 MB F16). No projector or separate embedding step.
# Total VRAM: ~1.04 GB (360M Q4_K_M weights + 896M KV + 400M runtime + ~100M activations).
#
# Path to the text reranker GGUF model file
LRR_LLAMA_MODEL=/data/public/machine-learning/models/reranker/Qwen3-Reranker-0.6B.Q4_K_M.gguf

# Context size per parallel slot (default: 12288)
LRR_LLAMA_N_CTX=12288

# Micro-batch size (default: 12288, matching context size)
LRR_LLAMA_N_UBATCH=12288

# Number of layers to offload to GPU (all=999)
LRR_LLAMA_N_GPU_LAYERS=999
# To run inference on CPU instead of GPU (none=0)
# LRR_LLAMA_N_GPU_LAYERS=0

# GPU/CPU backend device to use (run 'llama-cli --list-devices' for valid names)
# LRR_LLAMA_DEVICE="ROCm0"

# Number of threads to use (default: 4)
LRR_LLAMA_THREADS=4

# Parallel request slots (default: 2)
LRR_LLAMA_PARALLEL=2

# Extra arguments to pass to llama-server
LRR_LLAMA_EXTRA_ARGS=""

EOF
}

# Write service file

write_service_file() {
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

    # Copy TEI gRPC helper monkeypatch to systemd directory next to env and service
    local root_dir
    root_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
    if [[ -f "${root_dir}/scripts/tei-helper.py" ]]; then
        if [[ ! -f "${SYSTEMD_USER_DIR}/sitecustomize.py" ]] ||
            ! cmp -s "${root_dir}/scripts/tei-helper.py" "${SYSTEMD_USER_DIR}/sitecustomize.py"; then
            echo "Copying TEI helper patch to ${SYSTEMD_USER_DIR}/sitecustomize.py..."
            cp "${root_dir}/scripts/tei-helper.py" "${SYSTEMD_USER_DIR}/sitecustomize.py"
            chmod 644 "${SYSTEMD_USER_DIR}/sitecustomize.py"
        fi
    fi

    # Write env file only if it doesn't exist (preserve user edits)
    if [[ -f "${ENV_FILE}" ]] && [ "${new_config}" = "false" ]; then
        echo "Warning: Env file already exists, skipping: ${ENV_FILE}"
        echo "Remove it manually or use --new-config if you want to regenerate the defaults."
    else
        echo "Writing default env file: ${ENV_FILE}"
        generate_env_file >"${ENV_FILE}"
        chmod 600 "${ENV_FILE}"
        echo "Env file written."
    fi

    # Write service file
    echo "Writing service file: ${SERVICE_FILE}"
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
    echo "  Service: ${SERVICE_FILE}"
    echo "  Env:     ${ENV_FILE}"
    echo ""
    echo "  Edit the env file to select model, then:"
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
        run_systemctl daemon-reload
        echo "Removed service file."
    fi

    if [[ -f "${SYSTEMD_USER_DIR}/sitecustomize.py" ]]; then
        rm -f "${SYSTEMD_USER_DIR}/sitecustomize.py"
        echo "Removed sitecustomize.py helper patch."
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
    echo "Restarting service to apply updated environment..."
    cmd_restart
}

cmd_exec() {
    parse_env_args "$@"
    set -- "${COMMAND_ARGS[@]}"

    local args
    local bin
    if [[ "${LRR_ENGINE}" == "tei" ]]; then
        get_tei_args args
        bin="${TEI_ROUTER_BIN:-text-embeddings-router}"
    else
        get_llama_args args
        bin="${LLAMA_SERVER_BIN:-llama-server}"
    fi

    if ! is_systemd_running; then
        echo "Warning: Systemd is not running. Running ${bin} directly in foreground..."
        if [ $# -gt 0 ]; then
            exec "${bin}" "$@"
        else
            exec "${bin}" "${args[@]}"
        fi
    fi

    echo "Starting ${bin} as a transient systemd service with args: $*"

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
        systemd-run "${opts[@]}" "${SETENV_OPTS[@]}" "${bin}" "$@"
    else
        systemd-run "${opts[@]}" "${SETENV_OPTS[@]}" "${bin}" "${args[@]}"
    fi
}

cmd_shell() {
    echo "Starting interactive shell in the local-rerank systemd environment..."

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

    systemd-run "${opts[@]}" "${SETENV_OPTS[@]}" "${SHELL:-/bin/bash}" "$@"
}

cmd_run() {
    parse_env_args "$@"
    set -- "${COMMAND_ARGS[@]}"

    if [ $# -lt 1 ]; then
        echo "Error: run requires a command to execute." >&2
        exit 1
    fi
    echo "Running command inside the local-rerank environment: $*"

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

    systemd-run "${opts[@]}" "${SETENV_OPTS[@]}" "$@"
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
    echo "Running local-rerank validation tests..."
    load_env

    local host="${LRR_HOST:-127.0.0.1}"
    local port="${LRR_PORT:-50086}"
    local alias="${LRR_ALIAS:-qwen3-reranker}"

    local base_url="http://${host}:${port}"
    echo "Using endpoint base: ${base_url}"

    # Wait for server to become ready (shader compilation on first load takes time)
    wait_for_endpoint "${base_url}/health" 30 2 "local-rerank" || return 1

    local benchmark=false
    local repeat=""
    local extra_args=()
    while [ $# -gt 0 ]; do
        case "$1" in
        --benchmark) benchmark=true ;;
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
        # Try relative path in repo first
        context_file="$(dirname "$0")/../scratch/test-models/benchmark-context.md"
        if [[ ! -f "$context_file" ]]; then
            context_file="$(dirname "$(dirname "$LRR_MODEL")")/benchmark-context.md"
        fi
        if [[ ! -f "$context_file" ]]; then
            context_file="/data/public/machine-learning/models/benchmark-context.md"
        fi
        if [[ ! -f "$context_file" ]]; then
            context_file="/tmp/benchmark-context.md"
        fi
        if [[ ! -f "$context_file" ]]; then
            echo "benchmark-context.md not found. Generating it via download-helper.py..."
            python3 "$(dirname "$0")/../scripts/download-helper.py" benchmark-context --output "$context_file" || true
        fi

        local repeat_arg=()
        if [ -n "$repeat" ]; then
            repeat_arg=(--repeat "$repeat")
        fi

        # Qwen3-Reranker serves via /v1/rerank; benchmark as reranking workload
        python3 "$(dirname "$0")/../scripts/benchmark-helper.py" \
            --mode rerank \
            --url "${base_url}" \
            --model "${alias}" \
            --context "${context_file}" \
            "${repeat_arg[@]}" \
            "${extra_args[@]}"
        return 0
    fi

    echo "Sending validation rerank request to http://${host}:${port}/v1/rerank..."
    echo "Query: \"What is the speed of light in a vacuum?\""
    echo "Documents:"
    echo "  [Index 0] \"The speed of sound in dry air at 20 degrees Celsius is approximately 343 meters per second.\""
    echo "  [Index 1] \"The speed of light in a vacuum is a fundamental physical constant exactly equal to 299,792,458 meters per second.\""
    echo "  [Index 2] \"Light travels through glass at a speed of approximately 200,000 kilometers per second, which is slower than in a vacuum.\""
    echo "  [Index 3] \"The speed of light in water is about 225,000 kilometers per second due to the refractive index.\""
    echo "  [Index 4] \"The Earth orbits the Sun at an average speed of about 29.78 kilometers per second.\""
    echo ""

    # Qwen3-Reranker serves via /v1/rerank with yes/no generative classification
    # Scores are returned directly as relevance_score (P(yes) probability)
    local result
    result=$(python3 -c "
import json, subprocess, sys

docs = [
    'The speed of sound in dry air at 20 degrees Celsius is approximately 343 meters per second.',
    'The speed of light in a vacuum is a fundamental physical constant exactly equal to 299,792,458 meters per second.',
    'Light travels through glass at a speed of approximately 200,000 kilometers per second, which is slower than in a vacuum.',
    'The speed of light in water is about 225,000 kilometers per second due to the refractive index.',
    'The Earth orbits the Sun at an average speed of about 29.78 kilometers per second.'
]
query = 'What is the speed of light in a vacuum?'

payload = {'model': '${alias}', 'query': query, 'documents': docs}
resp = subprocess.run(['curl', '-s', '-f', '-X', 'POST', '${base_url}/v1/rerank',
    '-H', 'Content-Type: application/json',
    '-d', json.dumps(payload)],
    capture_output=True, text=True)
data = json.loads(resp.stdout)

scores = [(r['index'], r['relevance_score']) for r in data['results']]
scores.sort(key=lambda x: x[1], reverse=True)
top_idx = scores[0][0]
print(json.dumps({'top_index': top_idx, 'scores': [{'index': i, 'score': round(s, 4)} for i, s in scores]}))
")

    echo "${result}"
    local top_idx
    top_idx=$(echo "${result}" | python3 -c "import sys, json; print(json.load(sys.stdin)['top_index'])")
    if [ "$top_idx" -ne 1 ]; then
        echo "Error: Reranker validation failed. Top document index was $top_idx, expected 1." >&2
        return 1
    fi
    echo "Reranker: Success (verified correct result with index $top_idx)."
}

usage() {
    echo "Usage: $0 <command> [args...]"
    echo "Commands:"
    echo "  install [--no-start] [--new-config] - Setup service and default environment (do not start service if --no-start is specified, overwrite configs with defaults if --new-config is specified)"
    echo "  uninstall - Stop and remove systemd service"
    echo "  start     - Start the systemd service"
    echo "  stop      - Stop the systemd service"
    echo "  restart   - Restart the systemd service"
    echo "  status    - View systemd service status"
    echo "  enable    - Enable systemd service on boot"
    echo "  disable   - Disable systemd service on boot"
    echo "  logs      - Tail the systemd service logs"
    echo "  edit      - Edit the .env file and restart the service upon exit"
    echo "  exec      - Run the active engine server as a transient systemd user service"
    echo "  run       - Run a command inside the server environment"
    echo "  shell     - Spawn an interactive shell in the server environment"
    echo "  cat       - Print service file, environment configuration, and transient exec command"
    echo "  test [--benchmark] [--repeat XX] - Run validation tests (cosine similarity) or embedding benchmark"
    echo "Note: Text reranking can also be served combined inside the local-chat service."
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
    echo "=== Transient Execution Command (exec) ==="
    local args
    if [[ "${LRR_ENGINE}" == "tei" ]]; then
        get_tei_args args
        echo "${TEI_ROUTER_BIN:-text-embeddings-router} ${args[*]}"
    else
        get_llama_args args
        echo "${LLAMA_SERVER_BIN:-llama-server} ${args[*]}"
    fi
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
