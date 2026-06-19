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
    # Default parameters
    LMBD_PORT=50082
    LMBD_HOST=127.0.0.1
    LMBD_MODEL=/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf
    LMBD_ALIAS=qwen3-embedding
    LMBD_N_CTX=8192
    LMBD_N_GPU_LAYERS=999
    LMBD_THREADS=4
    LMBD_DEVICE=""
    LMBD_EXTRA_ARGS="--flash-attn on"

    # Source the env file to get model paths and settings if it exists
    if [[ -f "$ENV_FILE" ]]; then
        set +u
        # shellcheck disable=SC1090
        source "$ENV_FILE"
        set -u
    fi

    if [[ -n "${HIP_VISIBLE_DEVICES+x}" ]]; then
        export HIP_VISIBLE_DEVICES
    fi
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

generate_service_file() {
    load_env

    local exec_cmd="llama-server \\
    --model ${LMBD_MODEL} \\
    --embedding \\
    --pooling mean \\
    --ctx-size ${LMBD_N_CTX} \\
    --batch-size \$((LMBD_N_CTX / 4)) \\
    --ubatch-size \$((LMBD_N_CTX / 4)) \\
    --alias ${LMBD_ALIAS} \\
    --threads ${LMBD_THREADS} \\
    --n-gpu-layers ${LMBD_N_GPU_LAYERS} \\
    --host ${LMBD_HOST} \\
    --port ${LMBD_PORT}"

    if [[ -n "${LMBD_DEVICE:-}" ]]; then
        exec_cmd="${exec_cmd} \\
    --device ${LMBD_DEVICE}"
    fi

    if [[ -n "${LMBD_EXTRA_ARGS:-}" ]]; then
        exec_cmd="${exec_cmd} \\
    ${LMBD_EXTRA_ARGS}"
    fi

    cat <<EOF
[Unit]
Description=Local Text Embedding Inference Server (llama-server)
Documentation=https://github.com/ggml-org/llama.cpp
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

# Configuration for the local-embedding.service llama-server instance.
#
# Edit this file to switch models or tune runtime parameters.
# Reload with:  local-embedding.sh restart


# Port to bind the server to (default: 50082)
LMBD_PORT=50082

# Host to bind the server to (127.0.0.1 for local access only)
LMBD_HOST=127.0.0.1

# Path to the text embedding model file
LMBD_MODEL=/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf

# Model alias used by client integrations (default: qwen3-embedding)
LMBD_ALIAS=qwen3-embedding

# Context size (default: 8192)
LMBD_N_CTX=8192
# Note: Batch size and micro-batch size are automatically set to 1/4 of LMBD_N_CTX
# (e.g. 2048) at startup to significantly reduce memory footprint.

# Number of layers to offload to GPU (all=999)
LMBD_N_GPU_LAYERS=999
# To run inference on CPU instead of GPU (none=0)
# LMBD_N_GPU_LAYERS=0

# GPU/CPU backend device to use (run 'llama-cli --list-devices' for valid names)
# By default, llama-server automatically selects the best available device.
# To force a specific backend device, uncomment one of the options below:
# LMBD_DEVICE="ROCm0"
# LMBD_DEVICE="Vulkan0"
# LMBD_DEVICE="BLAS"  # Force CPU OpenBLAS acceleration
# LMBD_DEVICE="none"  # Force plain CPU execution (without OpenBLAS)

# Number of threads to use (default: 4)
LMBD_THREADS=4

# Extra arguments to pass to llama-server
LMBD_EXTRA_ARGS="--flash-attn on"

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

    local args=(
        --model "${LMBD_MODEL}"
        --embedding
        --pooling mean
        --ctx-size "${LMBD_N_CTX}"
        --batch-size "$((LMBD_N_CTX / 4))"
        --ubatch-size "$((LMBD_N_CTX / 4))"
        --alias "${LMBD_ALIAS}"
        --threads "${LMBD_THREADS}"
        --n-gpu-layers "${LMBD_N_GPU_LAYERS}"
        --host "${LMBD_HOST}"
        --port "${LMBD_PORT}"
    )
    if [[ -n "${LMBD_DEVICE:-}" ]]; then
        args+=(--device "${LMBD_DEVICE}")
    fi
    if [[ -n "${LMBD_EXTRA_ARGS:-}" ]]; then
        # We want word splitting for extra args
        # shellcheck disable=SC2206
        args+=(${LMBD_EXTRA_ARGS})
    fi

    if ! is_systemd_running; then
        echo "Warning: Systemd is not running. Running llama-server directly in foreground..."
        if [ $# -gt 0 ]; then
            exec llama-server "$@"
        else
            exec llama-server "${args[@]}"
        fi
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
        systemd-run "${opts[@]}" "${SETENV_OPTS[@]}" llama-server "$@"
    else
        systemd-run "${opts[@]}" "${SETENV_OPTS[@]}" llama-server "${args[@]}"
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

    systemd-run "${opts[@]}" "${SETENV_OPTS[@]}" "${SHELL:-/bin/bash}" "$@"
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

    systemd-run "${opts[@]}" "${SETENV_OPTS[@]}" "$@"
}

cmd_test() {
    echo "Running local-embedding validation tests..."
    load_env

    local host="${LMBD_HOST:-127.0.0.1}"
    local port="${LMBD_PORT:-50082}"
    local alias="${LMBD_ALIAS:-qwen3-embedding}"

    local base_url="http://${host}:${port}"
    echo "Using endpoint base: ${base_url}"

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
        context_file="/data/public/machine-learning/models/benchmark-context.md"
        if [[ ! -f "$context_file" ]]; then
            context_file="$(dirname "$(dirname "$LMBD_MODEL")")/benchmark-context.md"
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

        python3 "$(dirname "$0")/../scripts/benchmark-helper.py" \
            --mode embedding \
            --url "${base_url}" \
            --model "${alias}" \
            --context "${context_file}" \
            "${repeat_arg[@]}" \
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
    echo "  exec      - Run llama-server as a transient systemd user service"
    echo "  run       - Run a command inside the llama-server environment"
    echo "  shell     - Spawn an interactive shell in the llama-server environment"
    echo "  test [--benchmark] [--repeat XX] - Run validation tests or embedding benchmark"
}

# Main

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
