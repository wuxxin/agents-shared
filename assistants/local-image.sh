#!/usr/bin/env bash
# local-image.sh - Manage local sd-server systemd user service for Image Generation
#
# Usage: local-image.sh <command> [args...]
#

set -euo pipefail

# Paths
SYSTEMD_USER_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
SERVICE_NAME="local-image"
SERVICE_FILE="${SYSTEMD_USER_DIR}/${SERVICE_NAME}.service"
ENV_FILE="${SYSTEMD_USER_DIR}/${SERVICE_NAME}.env"

# Load environment
load_env() {
    # Default parameters
    LIMG_PORT=50100
    LIMG_HOST=127.0.0.1
    LIMG_MODEL=/data/public/machine-learning/models/image/z_image_turbo-Q8_0.gguf
    LIMG_VAE=/data/public/machine-learning/models/image/ae.safetensors
    LIMG_LLM=/data/public/machine-learning/models/image/Qwen3-4B-Q4_K_M.gguf
    LIMG_BACKEND=""
    LIMG_STEPS=8
    LIMG_CFG_SCALE="1.0"
    LIMG_THREADS=8
    LIMG_EXTRA_ARGS="-fa"

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
        if declare -p "$key" &>/dev/null || [[ "$key" =~ ^LRR_ || "$key" =~ ^LMBD_ || "$key" =~ ^LCHAT_ || "$key" =~ ^LSTT_ || "$key" =~ ^LTTS_ || "$key" =~ ^LIMG_ ]]; then
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
    echo "EnvironmentFile=-${home_spec}/.config/systemd/user/local-image.env"
    echo "WorkingDirectory=${home_spec}"

    # Basic hardening (minimal for GPU access)
    echo "NoNewPrivileges=yes"
    echo "CapabilityBoundingSet="
    echo "AmbientCapabilities="

    # GPU/DRI access requires PrivateDevices=no (ROCm/Vulkan needs /dev/dri, /dev/kfd)
    echo "PrivateDevices=no"
    echo "PrivateTmp=yes"
    echo "PrivateMounts=yes"
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

    local exec_cmd="sd-server \\
    --diffusion-model ${LIMG_MODEL} \\
    --vae ${LIMG_VAE} \\
    --llm ${LIMG_LLM} \\
    --listen-ip ${LIMG_HOST} \\
    --listen-port ${LIMG_PORT} \\
    --threads ${LIMG_THREADS} \\
    --steps ${LIMG_STEPS} \\
    --cfg-scale ${LIMG_CFG_SCALE}"

    if [[ -n "${LIMG_BACKEND:-}" ]]; then
        exec_cmd="${exec_cmd} \\
    --backend ${LIMG_BACKEND}"
    fi

    if [[ -n "${LIMG_EXTRA_ARGS:-}" ]]; then
        exec_cmd="${exec_cmd} \\
    ${LIMG_EXTRA_ARGS}"
    fi

    cat <<EOF
[Unit]
Description=Local Image Generation Server (sd-server)
Documentation=https://github.com/leejet/stable-diffusion.cpp
After=network.target

[Service]
Type=simple
$(get_shared_options service)
ExecStart=${exec_cmd}

Restart=on-failure
RestartSec=10s

StandardOutput=journal
StandardError=journal
SyslogIdentifier=local-image

[Install]
WantedBy=default.target
EOF
}

# Embedded default env file (heredoc written by install)

generate_env_file() {
    cat <<'EOF'
# local-image.env

# Configuration for the local-image.service sd-server instance.
#
# Edit this file to switch models or tune runtime parameters.
# Reload with:  local-image.sh restart


# Port to bind the server to (default: 50100)
LIMG_PORT=50100

# Host to bind the server to (127.0.0.1 for local access only)
LIMG_HOST=127.0.0.1

# Path to the standalone GGUF diffusion model file (Z-Image-Turbo)
LIMG_MODEL=/data/public/machine-learning/models/image/z_image_turbo-Q8_0.gguf

# Path to the standalone VAE file (Flux VAE)
LIMG_VAE=/data/public/machine-learning/models/image/ae.safetensors

# Path to the LLM Text Encoder GGUF file (Qwen3-4B)
LIMG_LLM=/data/public/machine-learning/models/image/Qwen3-4B-Q4_K_M.gguf

# GPU/CPU backend device to use (run 'sd-cli --help' or check hardware targets)
# Valid options for LIMG_BACKEND include:
#   - cpu                                     : Force CPU-only execution for all components
#   - vulkan0, vulkan1, etc.                 : Run everything on the specified Vulkan device
#   - cuda0, cuda1, etc.                     : Run everything on the specified CUDA device
#   - vulkan1,te=cpu                         : Run diffusion/VAE on Vulkan1 and offload text encoder (te) to CPU
#                                               (highly recommended to bypass Vulkan's 1GB parameter buffer limit)
#   - clip=cpu,vae=vulkan1,diffusion=vulkan1  : Custom heterogeneous backend routing
#                                               (e.g., keeping clip on CPU, and others on Vulkan)
# LIMG_BACKEND="vulkan1"

# Number of sample steps (default: 8, optimized for Turbo models)
LIMG_STEPS=8

# Unconditional guidance scale (default: 1.0, optimized for Z-Image-Turbo)
LIMG_CFG_SCALE="1.0"

# Number of computation threads to use (default: 8)
LIMG_THREADS=8

# Extra arguments to pass to sd-server (e.g. "--vae-tiling", "--diffusion-fa")
LIMG_EXTRA_ARGS="--fa"

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
    echo "  Edit the env file to select model/vae/llm, then:"
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
        --diffusion-model "${LIMG_MODEL}"
        --vae "${LIMG_VAE}"
        --llm "${LIMG_LLM}"
        --listen-ip "${LIMG_HOST}"
        --listen-port "${LIMG_PORT}"
        --threads "${LIMG_THREADS}"
        --steps "${LIMG_STEPS}"
        --cfg-scale "${LIMG_CFG_SCALE}"
    )

    if [[ -n "${LIMG_BACKEND:-}" ]]; then
        args+=(--backend "${LIMG_BACKEND}")
    fi

    if [[ -n "${LIMG_EXTRA_ARGS:-}" ]]; then
        # shellcheck disable=SC2206
        args+=(${LIMG_EXTRA_ARGS})
    fi

    if ! is_systemd_running; then
        echo "Warning: Systemd is not running. Running sd-server directly in foreground..."
        if [ $# -gt 0 ]; then
            exec sd-server "$@"
        else
            exec sd-server "${args[@]}"
        fi
    fi

    echo "Starting sd-server as a transient systemd service with args: $*"

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
        systemd-run "${opts[@]}" "${SETENV_OPTS[@]}" sd-server "$@"
    else
        systemd-run "${opts[@]}" "${SETENV_OPTS[@]}" sd-server "${args[@]}"
    fi
}

cmd_shell() {
    echo "Starting interactive shell in the sd-server systemd environment..."

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
    echo "Running command inside the sd-server environment: $*"

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
    echo "Running local-image validation tests..."
    load_env

    local host="${LIMG_HOST:-127.0.0.1}"
    local port="${LIMG_PORT:-50100}"
    local base_url="http://${host}:${port}"

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
        local repeat_arg=()
        if [ -n "$repeat" ]; then
            repeat_arg=(--repeat "$repeat")
        fi

        # Run image generation benchmark
        python3 "$(dirname "$0")/../scripts/benchmark-helper.py" \
            --mode image \
            --url "${base_url}" \
            --model "z-image-turbo" \
            "${repeat_arg[@]}" \
            "${extra_args[@]}"
        return 0
    fi

    echo "=== Testing Image Generation API ==="
    local temp_output="/tmp/local_image_test_output.png"
    if test -e "${temp_output}"; then rm -f "${temp_output}"; fi

    local resp
    resp=$(curl -s -f -X POST "${base_url}/v1/images/generations" \
        -H "Content-Type: application/json" \
        -d '{
          "prompt": "A high-resolution, beautiful photograph of a pristine mountain lake at sunrise, highly detailed.",
          "steps": 8,
          "cfg_scale": 1.0
        }')

    if echo "${resp}" | grep -q "data"; then
        # Extract base64 representation if it exists and decode it to temp_output
        local b64
        b64=$(echo "${resp}" | grep -o '"b64_json":"[^"]*' | cut -d'"' -f4)
        if [[ -n "$b64" ]]; then
            echo "$b64" | base64 -d >"${temp_output}"
            echo "Success: Image generated and saved to ${temp_output} (Size: $(wc -c <"${temp_output}") bytes)."
        else
            echo "Success: Image response received but b64_json field not parsed directly. Raw JSON:"
            echo "${resp}" | cut -c 1-500
        fi
    else
        echo "Error: Image generation test failed. Response:" >&2
        echo "${resp}" >&2
        return 1
    fi
}

usage() {
    cat <<EOF
Usage: $0 <command> [args...]
Commands:
  install [--no-start] [--new-config] - Setup service and default environment (do not start service if --no-start is specified, overwrite configs with defaults if --new-config is specified)
  uninstall - Stop and remove systemd service
  start     - Start the systemd service
  stop      - Stop the systemd service
  restart   - Restart the systemd service
  status    - View systemd service status
  enable    - Enable systemd service on boot
  disable   - Disable systemd service on boot
  logs      - Tail the systemd service logs
  edit      - Edit the .env file and restart the service upon exit
  exec      - Run sd-server as a transient systemd user service
  run       - Run a command inside the sd-server environment
  shell     - Spawn an interactive shell in the sd-server environment
  test [--benchmark] [--repeat XX]
    - Run validation tests or image generation benchmark
EOF
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
