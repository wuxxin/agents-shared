#!/usr/bin/env bash
# local-chat.sh - Manage local llama-server systemd user service for Chat LLM
#
# Usage: local-chat.sh <command> [args...]
#
# Manages a systemd user service (local-chat.service) that runs llama-server
# serving the Chat/Vision LLM.
#
# Hardware target: AMD Radeon Pro W6800.
#
# ---------------------------------------------------------------------------

set -euo pipefail

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SYSTEMD_USER_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
SERVICE_NAME="local-chat"
SERVICE_FILE="${SYSTEMD_USER_DIR}/${SERVICE_NAME}.service"
ENV_FILE="${SYSTEMD_USER_DIR}/${SERVICE_NAME}.env"

# ---------------------------------------------------------------------------
# Load environment
# ---------------------------------------------------------------------------
load_env() {
    # Default parameters
    LC_PORT=50080
    LC_HOST=127.0.0.1
    LC_MODEL=/data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact.gguf
    LC_ALIAS=qwen3
    LC_N_CTX=240000
    LC_N_GPU_LAYERS=99
    LC_THREADS=4
    LC_MMPROJ_ARGS="--mmproj /data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact-mmproj.gguf"
    LC_CHAT_TEMPLATE_ARGS="--chat-template-file /data/public/machine-learning/models/vision-text/Qwen3.6-chat_template.jinja"
    LC_EXTRA_ARGS="--flash-attn on"

    # Source the env file to get model paths and settings if it exists
    if [[ -f "$ENV_FILE" ]]; then
        set +u
        # shellcheck disable=SC1090
        source "$ENV_FILE"
        set -u
    fi
}

# ---------------------------------------------------------------------------
# Helper to execute systemctl commands only if systemd user manager is reachable
# ---------------------------------------------------------------------------
run_systemctl() {
    if systemctl --user daemon-reload >/dev/null 2>&1; then
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

    # We expand LC_MMPROJ_ARGS and LC_CHAT_TEMPLATE_ARGS without quotes in the service template
    # so that if they are empty, no empty string argument is passed to llama-server.
    cat <<EOF
[Unit]
Description=Local LLM Chat Inference Server (llama-server)
Documentation=https://github.com/ggml-org/llama.cpp
After=network.target

[Service]
Type=simple
$(get_shared_options service)
ExecStart=llama-server \\
    --model ${LC_MODEL} \\
    ${LC_MMPROJ_ARGS} \\
    ${LC_CHAT_TEMPLATE_ARGS} \\
    --ctx-size ${LC_N_CTX} \\
    --alias ${LC_ALIAS} \\
    --parallel 2 \\
    --cache-type-k q4_0 \\
    --cache-type-v q4_0 \\
    --batch-size 2048 \\
    --ubatch-size 1024 \\
    --threads ${LC_THREADS} \\
    --n-gpu-layers ${LC_N_GPU_LAYERS} \\
    --host ${LC_HOST} \\
    --port ${LC_PORT} \\
    ${LC_EXTRA_ARGS}

Restart=on-failure
RestartSec=10s

StandardOutput=journal
StandardError=journal
SyslogIdentifier=local-chat

[Install]
WantedBy=default.target
EOF
}

# ---------------------------------------------------------------------------
# Embedded default env file (heredoc written by --install)
# ---------------------------------------------------------------------------
generate_env_file() {
    cat <<'EOF'
# local-chat.env
# ---------------------------------------------------------------------------
# Configuration for the local-chat.service llama-server instance.
#
# Edit this file to switch models or tune runtime parameters.
# Reload with:  local-chat.sh restart
# ---------------------------------------------------------------------------

# Port to bind the server to (default: 50080)
LC_PORT=50080

# Host to bind the server to (127.0.0.1 for local access only)
LC_HOST=127.0.0.1

# Path to the chat model file
LC_MODEL=/data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact.gguf

# Model alias used by client integrations (default: qwen3)
LC_ALIAS=qwen3

# Context size (default: 240000)
LC_N_CTX=240000

# Multimodal projector arguments (optional)
LC_MMPROJ_ARGS="--mmproj /data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact-mmproj.gguf"

# Chat template file (optional)
LC_CHAT_TEMPLATE_ARGS="--chat-template-file /data/public/machine-learning/models/vision-text/Qwen3.6-chat_template.jinja"

# Number of layers to offload to GPU (default: 99)
LC_N_GPU_LAYERS=99

# Extra arguments to pass to llama-server (default: --flash-attn on)
LC_EXTRA_ARGS="--flash-attn on"

# Number of threads to use (default: 4)
LC_THREADS=4

# ---------------------------------------------------------------------------
# CPU Inference Fallback:
# To run inference on CPU instead of GPU, uncomment the parameters below.
# ---------------------------------------------------------------------------
# LC_N_GPU_LAYERS=0
# LC_EXTRA_ARGS=""
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
    if [ "${1:-}" = "--no-start" ]; then
        no_start=true
    fi

    echo "Installing ${SERVICE_NAME} systemd user service..."

    # Create directory if needed
    mkdir -p "${SYSTEMD_USER_DIR}"

    # Write env file only if it doesn't exist (preserve user edits)
    if [[ -f "${ENV_FILE}" ]]; then
        echo "Warning: Env file already exists, skipping: ${ENV_FILE}"
        echo "Remove it manually if you want to regenerate the defaults."
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
        run_systemctl stop "${SERVICE_NAME}.service"
    else
        echo "Starting/Restarting service automatically..."
        run_systemctl restart "${SERVICE_NAME}.service"
    fi

    echo "Installation complete."
    echo ""
    echo "  Service: ${SERVICE_FILE}"
    echo "  Env:     ${ENV_FILE}"
    echo ""
    echo "  Edit the env file to select model/mmproj/template, then:"
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
    run_systemctl start "${SERVICE_NAME}.service"
}

cmd_stop() { run_systemctl stop "${SERVICE_NAME}.service"; }

cmd_restart() {
    write_service_file
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
            --model "${LC_MODEL}" \
            ${LC_MMPROJ_ARGS} \
            ${LC_CHAT_TEMPLATE_ARGS} \
            --ctx-size "${LC_N_CTX}" \
            --alias "${LC_ALIAS}" \
            --parallel 2 \
            --cache-type-k q4_0 \
            --cache-type-v q4_0 \
            --batch-size 2048 \
            --ubatch-size 1024 \
            --threads "${LC_THREADS}" \
            --n-gpu-layers "${LC_N_GPU_LAYERS}" \
            --host "${LC_HOST}" \
            --port "${LC_PORT}" \
            ${LC_EXTRA_ARGS}
    fi
}

cmd_shell() {
    echo "Starting interactive shell in the llama-server systemd environment..."

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

cmd_test() {
    echo "Running local-chat validation tests..."
    load_env

    local host="${LC_HOST:-127.0.0.1}"
    local port="${LC_PORT:-50080}"
    local alias="${LC_ALIAS:-qwen3}"

    local base_url="http://${host}:${port}"
    echo "Using endpoint base: ${base_url}"

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
}

usage() {
    echo "Usage: $0 <command>"
    echo "Commands:"
    echo "  install [--no-start] - Setup service and default environment (do not start service if --no-start is specified)"
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
    echo "  shell     - Spawn an interactive shell in the llama-server environment"
    echo "  test      - Run API validation tests"
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
shell) cmd_shell "$@" ;;
test) cmd_test ;;
*)
    echo "Unknown command: $COMMAND"
    usage
    exit 1
    ;;
esac
