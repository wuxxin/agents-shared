#!/usr/bin/env bash
# local-embedding.sh - Manage local llama-server systemd user service for Text Embeddings
#
# Usage: local-embedding.sh <command> [args...]
#
# Manages a systemd user service (local-embedding.service) that runs llama-server
# serving the Text Embedding model.
#
#

set -euo pipefail

# Paths

SYSTEMD_USER_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
SERVICE_NAME="local-embedding"
SERVICE_FILE="${SYSTEMD_USER_DIR}/${SERVICE_NAME}.service"
ENV_FILE="${SYSTEMD_USER_DIR}/${SERVICE_NAME}.env"

# Load environment

load_env() {
    # General parameters
    LMBD_PORT=50082
    LMBD_HOST=127.0.0.1
    LMBD_ENGINE=tei

    # llama-server parameters (default to conservative/existing settings for VRAM safety)
    LMBD_LLAMA_MODEL=/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf
    LMBD_LLAMA_N_CTX=16384
    LMBD_LLAMA_N_UBATCH=16384
    LMBD_LLAMA_N_GPU_LAYERS=999
    LMBD_LLAMA_THREADS=4
    LMBD_LLAMA_PARALLEL=2
    LMBD_LLAMA_DEVICE=""
    LMBD_LLAMA_EXTRA_ARGS="--flash-attn on"

    # Max concurrent request slots (default: 8, 6 for Hindsight recall + 2 headroom for Hermes)
    # GPU dynamically packs requests up to max-batch-tokens per pass; queue absorbs extras at zero VRAM cost
    LMBD_TEI_MODEL=/data/public/machine-learning/models/embedding/pplx-embed-context-v1-0.6b
    LMBD_ALIAS=pplx-embedding
    LMBD_TEI_POOLING="mean"
    LMBD_TEI_MAX_CONCURRENT=8
    LMBD_TEI_MAX_BATCH_TOKENS=49152
    LMBD_TEI_EXTRA_ARGS="--dtype bfloat16"
    LMBD_TEI_DEVICE=""

    # Source the env file to get model paths and settings if it exists
    if [[ -f "$ENV_FILE" ]]; then
        set +u
        # shellcheck disable=SC1090
        source "$ENV_FILE"
        set -u
    fi

    # Auto-detect engine if not set (legacy configuration support)
    if [[ -z "${LMBD_ENGINE:-}" ]]; then
        if [[ "${LMBD_MODEL:-}" =~ \.gguf$ ]]; then
            LMBD_ENGINE=llama
        else
            LMBD_ENGINE=tei
        fi
    fi

    # Map generic variables based on selected engine for backward compatibility
    if [[ "${LMBD_ENGINE}" == "tei" ]]; then
        LMBD_MODEL="${LMBD_TEI_MODEL:-${LMBD_MODEL:-}}"
        LMBD_ALIAS="${LMBD_ALIAS:-}"
    else
        LMBD_MODEL="${LMBD_LLAMA_MODEL:-${LMBD_MODEL:-}}"
        LMBD_ALIAS="${LMBD_ALIAS:-}"

        # Keep existing mapping for llama parameters
        if [[ -n "${LMBD_UBATCH_SIZE:-}" ]]; then
            LMBD_LLAMA_N_UBATCH="${LMBD_UBATCH_SIZE}"
        fi
        LMBD_N_CTX="${LMBD_LLAMA_N_CTX:-16384}"
        LMBD_N_UBATCH="${LMBD_LLAMA_N_UBATCH:-16384}"
        LMBD_N_GPU_LAYERS="${LMBD_LLAMA_N_GPU_LAYERS:-999}"
        LMBD_THREADS="${LMBD_LLAMA_THREADS:-4}"
        LMBD_PARALLEL="${LMBD_LLAMA_PARALLEL:-2}"
        LMBD_DEVICE="${LMBD_LLAMA_DEVICE:-}"
        LMBD_EXTRA_ARGS="${LMBD_LLAMA_EXTRA_ARGS:-}"
    fi

    # Device selection for TEI
    local active_device=""
    if [[ "${LMBD_ENGINE}" == "tei" ]]; then
        active_device="${LMBD_TEI_DEVICE:-${LMBD_DEVICE:-}}"
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
        export PYTHONPATH="${HOME}/.config/systemd/user${PYTHONPATH:+:$PYTHONPATH}"
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
    echo "EnvironmentFile=-${home_spec}/.config/systemd/user/local-embedding.env"
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
        --model "${LMBD_MODEL}"
        --embedding
        --pooling mean
        --cache-type-k q8_0
        --cache-type-v q8_0
        --ctx-size "${LMBD_N_CTX}"
        --batch-size "${LMBD_N_CTX}"
        --ubatch-size "${LMBD_N_UBATCH}"
        --threads "${LMBD_THREADS}"
        --parallel "${LMBD_PARALLEL}"
        --n-gpu-layers "${LMBD_N_GPU_LAYERS}"
        --host "${LMBD_HOST}"
        --port "${LMBD_PORT}"
    )

    if [[ -n "${LMBD_ALIAS:-}" ]]; then
        out_args+=(--alias "${LMBD_ALIAS}")
    fi

    if [[ -n "${LMBD_DEVICE:-}" ]]; then
        out_args+=(--device "${LMBD_DEVICE}")
    fi

    if [[ -n "${LMBD_EXTRA_ARGS:-}" ]]; then
        local extra_arr=()
        eval "extra_arr=(${LMBD_EXTRA_ARGS})"
        out_args+=("${extra_arr[@]}")
    fi
}

# Helper to get unified arguments for text-embeddings-router
get_tei_args() {
    local -n out_tei_args=$1
    out_tei_args=(
        --model-id "${LMBD_MODEL}"
        --port "${LMBD_PORT}"
        --hostname "${LMBD_HOST}"
    )

    if [[ -n "${LMBD_TEI_POOLING:-}" ]]; then
        out_tei_args+=(--pooling "${LMBD_TEI_POOLING}")
    fi

    if [[ -n "${LMBD_TEI_MAX_CONCURRENT:-}" ]]; then
        out_tei_args+=(--max-concurrent-requests "${LMBD_TEI_MAX_CONCURRENT}")
    fi

    if [[ -n "${LMBD_TEI_MAX_BATCH_TOKENS:-}" ]]; then
        out_tei_args+=(--max-batch-tokens "${LMBD_TEI_MAX_BATCH_TOKENS}")
    fi

    if [[ -n "${LMBD_TEI_EXTRA_ARGS:-}" ]]; then
        local extra_arr=()
        eval "extra_arr=(${LMBD_TEI_EXTRA_ARGS})"
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

    if [[ "${LMBD_ENGINE}" == "tei" ]]; then
        get_tei_args args
        exec_cmd=$(format_exec_start "${TEI_ROUTER_BIN:-text-embeddings-router}" "${args[@]}")
        description="Local Text Embedding Inference Server (TEI)"
        doc_link="https://github.com/huggingface/text-embeddings-inference"
    else
        get_llama_args args
        exec_cmd=$(format_exec_start "${LLAMA_SERVER_BIN:-llama-server}" "${args[@]}")
        description="Local Text Embedding Inference Server (llama-server)"
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
SyslogIdentifier=local-embedding

[Install]
WantedBy=default.target
EOF
}

# Embedded default env file (heredoc written by install)

generate_env_file() {
    cat <<'EOF'
# local-embedding.env

# Configuration for the local-embedding.service.
# Edit this file to switch engines, models, or tune runtime parameters.
# Reload with:  local-embedding.sh restart

# Active inference engine: 'tei' (Text Embeddings Inference) or 'llama' (llama-server)
LMBD_ENGINE=tei

# Model alias used by client integrations (default: pplx-embedding)
LMBD_ALIAS=pplx-embedding

# Port to bind the server to (default: 50082)
LMBD_PORT=50082

# Host to bind the server to (127.0.0.1 for local access only)
LMBD_HOST=127.0.0.1

# TEI (Text Embeddings Inference) ENGINE SETTINGS
#
# Standalone TEI instances run bidirectional/causal encoders with dynamic batching.
# Because TEI does not use an autoregressive KV cache, VRAM is static and highly
# optimized, allowing for larger batch sizes and long contexts without pre-allocation.
#
# Path to the safetensors model directory
LMBD_TEI_MODEL=/data/public/machine-learning/models/embedding/pplx-embed-context-v1-0.6b

# Model alias used by client integrations (default: pplx-embedding)
# LMBD_ALIAS=pplx-embedding

# Pooling method to override model pooling config (default: mean)
LMBD_TEI_POOLING="mean"

# Max concurrent request slots (default: 8, 6 for Hindsight recall + 2 headroom for Hermes/other agents)
# GPU dynamically packs requests up to max-batch-tokens per pass; extra slots are queue-only (zero VRAM cost)
LMBD_TEI_MAX_CONCURRENT=8

# Max total tokens in a dynamic batch (default: 49152, ~6 × 8192 for 8K context chunks)
# TEI auto-sizes each batch: shorter chunks pack more, longer ones pack fewer — always stays within token limit
LMBD_TEI_MAX_BATCH_TOKENS=49152

# GPU/CPU backend device index or name (e.g. rocm[:0], rocm:1, vukan[:0], equals to auto if empty)
# Maps to HIP_VISIBLE_DEVICES / CUDA_VISIBLE_DEVICES internally for TEI
# LMBD_TEI_DEVICE="rocm:0"

# Extra arguments to pass to text-embeddings-router
LMBD_TEI_EXTRA_ARGS="--dtype bfloat16"

# Trust remote code to run custom models (e.g. Perplexity pplx-embed-context)
TRUST_REMOTE_CODE=true

# Python search path for custom model patches (bypasses Hugging Face import bugs)
EOF
    echo "PYTHONPATH=${SYSTEMD_USER_DIR}"
    echo ""
    echo "# PyTorch CUDA memory allocator configuration (prevents VRAM fragmentation/OOM on large contexts)"
    echo "PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True"
    cat <<'EOF'


# LLAMA-SERVER ENGINE SETTINGS
#
# llama-server pre-allocates KV cache slots statically at startup.
# Each slot allocates LMBD_LLAMA_N_CTX tokens. High context + parallel slots
# will result in large, persistent VRAM consumption on the GPU:
#   - LMBD_LLAMA_PARALLEL=2, N_CTX=16384 (at q8_0): ~448 MiB KV Cache VRAM
#   - LMBD_LLAMA_PARALLEL=8, N_CTX=32768 (at q8_0): ~3.5 GiB KV Cache VRAM
# Keep parallel/context conservative on llama-server to prevent GPU OOM under chat load.
#
# Path to the text embedding GGUF model file
LMBD_LLAMA_MODEL=/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf

# Model alias used by client integrations (default: qwen3-embedding)
# LMBD_ALIAS=qwen3-embedding

# Context size per parallel slot (default: 16384)
LMBD_LLAMA_N_CTX=16384

# Micro-batch size (default: 16384, matching context size)
LMBD_LLAMA_N_UBATCH=16384

# Number of layers to offload to GPU (all=999)
LMBD_LLAMA_N_GPU_LAYERS=999

# GPU/CPU backend device to use (run 'llama-cli --list-devices' for valid names)
# LMBD_LLAMA_DEVICE="ROCm0"

# Number of threads to use (default: 4)
LMBD_LLAMA_THREADS=4

# Parallel request slots (default: 2)
LMBD_LLAMA_PARALLEL=2

# Extra arguments to pass to llama-server
LMBD_LLAMA_EXTRA_ARGS="--flash-attn on"

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
        echo "Copying TEI helper patch to ${SYSTEMD_USER_DIR}/sitecustomize.py..."
        cp "${root_dir}/scripts/tei-helper.py" "${SYSTEMD_USER_DIR}/sitecustomize.py"
        chmod 644 "${SYSTEMD_USER_DIR}/sitecustomize.py"
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
    if [[ "${LMBD_ENGINE}" == "tei" ]]; then
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
    echo "Starting interactive shell in the local-embedding systemd environment..."

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
    echo "Running command inside the local-embedding environment: $*"

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

cmd_test() {
    echo "Running local-embedding validation tests..."
    load_env

    local host="${LMBD_HOST:-127.0.0.1}"
    local port="${LMBD_PORT:-50082}"
    local alias="${LMBD_ALIAS:-${LMBD_MODEL}}"

    local base_url="http://${host}:${port}"
    echo "Using endpoint base: ${base_url}"

    local benchmark=false
    local repeat=""
    local hindsight=false
    local extra_args=()
    while [ $# -gt 0 ]; do
        case "$1" in
        --benchmark) benchmark=true ;;
        --hindsight) hindsight=true ;;
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
        if [ "$hindsight" = "true" ]; then
            context_file="/data/public/machine-learning/models/hindsight-context.txt"
            if [[ ! -f "$context_file" ]]; then
                context_file="$(dirname "$(dirname "$LMBD_MODEL")")/hindsight-context.txt"
            fi
            if [[ ! -f "$context_file" ]]; then
                context_file="/tmp/hindsight-context.txt"
            fi
            if [[ ! -f "$context_file" ]]; then
                echo "hindsight-context.txt not found. Generating it via download-helper.py..."
                python3 "$(dirname "$0")/../scripts/download-helper.py" hindsight-context --output "$context_file" || true
            fi
        else
            context_file="/data/public/machine-learning/models/benchmark-context.md"
            if [[ ! -f "$context_file" ]]; then
                context_file="$(dirname "$(dirname "$LMBD_MODEL")")/benchmark-context.md"
            fi
            if [[ ! -f "$context_file" ]]; then
                context_file="/tmp/benchmark-context.md"
            fi
            if [[ ! -f "$context_file" ]]; then
                echo "benchmark-context.md not found. Generating it via download-helper.py..."
                python3 "$(dirname "$0")/../scripts/download-helper.py" benchmark-context --output "$context_file" || true
            fi
        fi

        local repeat_arg=()
        if [ -n "$repeat" ]; then
            repeat_arg=(--repeat "$repeat")
        fi

        local hindsight_arg=()
        if [ "$hindsight" = "true" ]; then
            hindsight_arg=(--hindsight)
        fi

        python3 "$(dirname "$0")/../scripts/benchmark-helper.py" \
            --mode embedding \
            --url "${base_url}" \
            --model "${alias}" \
            --context "${context_file}" \
            "${repeat_arg[@]}" \
            "${hindsight_arg[@]}" \
            "${extra_args[@]}"
        return 0
    fi

    echo "=== Testing Text Embeddings ==="
    local embed_resp
    embed_resp=$(curl -s -f -X POST "${base_url}/v1/embeddings" \
        -H "Content-Type: application/json" \
        -d "{
          \"model\": \"${alias}\",
          \"input\": \"Hello World\"
        }")

    echo "${embed_resp}"
    if ! echo "${embed_resp}" | grep -q "embedding"; then
        echo "Error: Text embedding test failed." >&2
        return 1
    fi
    echo "Text embedding: Success."
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
    echo "  test [--benchmark] [--repeat XX] - Run validation tests or embedding benchmark"
    echo "Note: Text embeddings can also be served combined inside the local-chat service."
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
    if [[ "${LMBD_ENGINE}" == "tei" ]]; then
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
