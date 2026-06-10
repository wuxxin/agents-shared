#!/usr/bin/env bash
# local-rerank.sh - Manage local llama-server systemd user service for Text Reranking
#
# Usage: local-rerank.sh <command> [args...]
#
# Manages a systemd user service (local-rerank.service) that runs llama-server
# serving the Text Reranker model.
#
# Hardware target: AMD Radeon Pro W6800.
#
# ---------------------------------------------------------------------------

set -euo pipefail

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SYSTEMD_USER_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
SERVICE_NAME="local-rerank"
SERVICE_FILE="${SYSTEMD_USER_DIR}/${SERVICE_NAME}.service"
ENV_FILE="${SYSTEMD_USER_DIR}/${SERVICE_NAME}.env"

# ---------------------------------------------------------------------------
# Load environment
# ---------------------------------------------------------------------------
load_env() {
    # Default parameters
    LR_PORT=50086
    LR_HOST=127.0.0.1
    LR_MODEL=/data/public/machine-learning/models/reranker/Qwen3-Reranker-0.6B.Q4_K_M.gguf
    LR_ALIAS=qwen3-reranker
    LR_N_CTX=8192
    LR_N_GPU_LAYERS=99
    LR_THREADS=8
    LR_EXTRA_ARGS=""

    # Source the env file to get model paths and settings if it exists
    if [[ -f "$ENV_FILE" ]]; then
        set +u
        # shellcheck disable=SC1090
        source "$ENV_FILE"
        set -u
    fi
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

# ---------------------------------------------------------------------------
# Shared Sandboxing Configuration
# ---------------------------------------------------------------------------
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
    echo "PrivateIPC=yes"

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

# ---------------------------------------------------------------------------
# Embedded service file (heredoc written by install/start/restart)
# ---------------------------------------------------------------------------
generate_service_file() {
    load_env

    cat <<EOF
[Unit]
Description=Local Document Reranking Server (llama-server)
Documentation=https://github.com/ggml-org/llama.cpp
After=network.target

[Service]
Type=simple
$(get_shared_options service)
ExecStart=llama-server \\
    --model ${LR_MODEL} \\
    --embedding \\
    --pooling rank \\
    --ctx-size ${LR_N_CTX} \\
    --alias ${LR_ALIAS} \\
    --threads ${LR_THREADS} \\
    --n-gpu-layers ${LR_N_GPU_LAYERS} \\
    --host ${LR_HOST} \\
    --port ${LR_PORT} \\
    ${LR_EXTRA_ARGS}

Restart=on-failure
RestartSec=10s

StandardOutput=journal
StandardError=journal
SyslogIdentifier=local-rerank

[Install]
WantedBy=default.target
EOF
}

# ---------------------------------------------------------------------------
# Embedded default env file (heredoc written by --install)
# ---------------------------------------------------------------------------
generate_env_file() {
    cat <<'EOF'
# local-rerank.env
# ---------------------------------------------------------------------------
# Configuration for the local-rerank.service llama-server instance.
#
# Edit this file to switch models or tune runtime parameters.
# Reload with:  local-rerank.sh restart
# ---------------------------------------------------------------------------

# Port to bind the server to (default: 50086)
LR_PORT=50086

# Host to bind the server to (127.0.0.1 for local access only)
LR_HOST=127.0.0.1

# Path to the text reranker model file
LR_MODEL=/data/public/machine-learning/models/reranker/Qwen3-Reranker-0.6B.Q4_K_M.gguf

# Model alias used by client integrations (default: qwen3-reranker)
LR_ALIAS=qwen3-reranker

# Context size (default: 8192)
LR_N_CTX=8192

# Number of layers to offload to GPU (all=99)
# LR_N_GPU_LAYERS=99
# To run inference on CPU instead of GPU (none=0)
LR_N_GPU_LAYERS=0

# Number of threads to use
LR_THREADS=8

# Use Flash Attention if on gpu and available
LR_EXTRA_ARGS="--flash-attn auto"

EOF
}

# ---------------------------------------------------------------------------
# Write service file
# ---------------------------------------------------------------------------
write_service_file() {
    generate_service_file >"${SERVICE_FILE}"
    chmod 644 "${SERVICE_FILE}"
    run_systemctl daemon-reload
}

# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------

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
    run_systemctl stop "${SERVICE_NAME}.service"
    run_systemctl disable "${SERVICE_NAME}.service"

    if [[ -f "${SERVICE_FILE}" ]]; then
        rm -f "${SERVICE_FILE}"
        run_systemctl daemon-reload
        echo "Removed service file."
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
    echo "Starting llama-server as a transient systemd service with args: $*"

    load_env

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
        systemd-run "${opts[@]}" llama-server "$@"
    else
        # shellcheck disable=SC2086
        systemd-run "${opts[@]}" llama-server \
            --model "${LR_MODEL}" \
            --embedding \
            --pooling rank \
            --ctx-size "${LR_N_CTX}" \
            --alias "${LR_ALIAS}" \
            --threads "${LR_THREADS}" \
            --n-gpu-layers "${LR_N_GPU_LAYERS}" \
            --host "${LR_HOST}" \
            --port "${LR_PORT}" \
            ${LR_EXTRA_ARGS}
    fi
}

cmd_shell() {
    echo "Starting interactive shell in the llama-server systemd environment..."

    load_env

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

    systemd-run "${opts[@]}" "${SHELL:-/bin/bash}" "$@"
}

cmd_run() {
    if [ $# -lt 1 ]; then
        echo "Error: run requires a command to execute." >&2
        exit 1
    fi
    echo "Running command inside the llama-server environment: $*"

    load_env

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

    systemd-run "${opts[@]}" "$@"
}

cmd_test() {
    echo "Running local-rerank validation tests..."
    load_env

    local host="${LR_HOST:-127.0.0.1}"
    local port="${LR_PORT:-50086}"
    local alias="${LR_ALIAS:-qwen3-reranker}"

    local base_url="http://${host}:${port}"
    echo "Using endpoint base: ${base_url}"

    local benchmark=false
    local repeat=""
    while [ $# -gt 0 ]; do
        case "$1" in
        --benchmark) benchmark=true ;;
        --repeat)
            shift
            repeat="$1"
            ;;
        esac
        shift
    done

    if [ "$benchmark" = "true" ]; then
        local context_file
        # Try relative path in repo first
        context_file="$(dirname "$0")/../scratch/test-models/benchmark-context.md"
        if [[ ! -f "$context_file" ]]; then
            context_file="$(dirname "$(dirname "$LR_MODEL")")/benchmark-context.md"
        fi
        if [[ ! -f "$context_file" ]]; then
            context_file="/data/public/machine-learning/models/benchmark-context.md"
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

        # Run rerank benchmark
        python3 "$(dirname "$0")/../scripts/benchmark-helper.py" \
            --mode rerank \
            --url "${base_url}" \
            --model "${alias}" \
            --context "${context_file}" \
            "${repeat_arg[@]}"
        return 0
    fi

    echo "Sending validation query to http://${host}:${port}/v1/rerank..."
    echo "Query: \"What is the speed of light in a vacuum?\""
    echo "Documents:"
    echo "  [Index 0] \"The speed of sound in dry air at 20 degrees Celsius is approximately 343 meters per second.\""
    echo "  [Index 1] \"The speed of light in a vacuum is a fundamental physical constant exactly equal to 299,792,458 meters per second.\""
    echo "  [Index 2] \"Light travels through glass at a speed of approximately 200,000 kilometers per second, which is slower than in a vacuum.\""
    echo "  [Index 3] \"The speed of light in water is about 225,000 kilometers per second due to the refractive index.\""
    echo "  [Index 4] \"The Earth orbits the Sun at an average speed of about 29.78 kilometers per second.\""
    echo ""

    local rerank_resp
    rerank_resp=$(curl -s -f -X POST "${base_url}/v1/rerank" \
        -H "Content-Type: application/json" \
        -d "{
          \"model\": \"${alias}\",
          \"query\": \"What is the speed of light in a vacuum?\",
          \"documents\": [
            \"The speed of sound in dry air at 20 degrees Celsius is approximately 343 meters per second.\",
            \"The speed of light in a vacuum is a fundamental physical constant exactly equal to 299,792,458 meters per second.\",
            \"Light travels through glass at a speed of approximately 200,000 kilometers per second, which is slower than in a vacuum.\",
            \"The speed of light in water is about 225,000 kilometers per second due to the refractive index.\",
            \"The Earth orbits the Sun at an average speed of about 29.78 kilometers per second.\"
          ],
          \"top_n\": 3
        }")

    echo "${rerank_resp}"
    if ! echo "${rerank_resp}" | grep -q "relevance_score"; then
        echo "Error: Reranker response structure is invalid." >&2
        return 1
    fi

    local top_idx
    top_idx=$(echo "${rerank_resp}" | python3 -c "import sys, json; print(json.load(sys.stdin).get('results', [{}])[0].get('index', -1))")
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
    echo "  exec      - Run llama-server as a transient systemd user service"
    echo "  run       - Run a command inside the llama-server environment"
    echo "  shell     - Spawn an interactive shell in the llama-server environment"
    echo "  test [--benchmark] - Run validation tests or rerank benchmark"
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
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
test) cmd_test "$@" ;;
*)
    echo "Unknown command: $COMMAND"
    usage
    exit 1
    ;;
esac
