#!/usr/bin/env bash
# local-router.sh - Manage local uvicorn combined routing service
#
# Usage: local-router.sh <command> [args...]
#
# Manages a systemd user service (local-router.service) that runs uvicorn serving the
# combined local inference router python app.

set -euo pipefail

# Paths

SYSTEMD_USER_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
SERVICE_NAME="local-router"
SERVICE_FILE="${SYSTEMD_USER_DIR}/${SERVICE_NAME}.service"
ENV_FILE="${SYSTEMD_USER_DIR}/${SERVICE_NAME}.env"

# Load environment

load_env() {
    # Default parameters
    LROUT_PORT=51080
    LROUT_HOST=127.0.0.1
    LROUT_EXTRA_ARGS=""

    # Source the env file to get model paths and settings if it exists
    if [[ -f "$ENV_FILE" ]]; then
        set +u
        # shellcheck disable=SC1090
        source "$ENV_FILE"
        set -u
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
        if declare -p "$key" &>/dev/null || [[ "$key" =~ ^LROUT_ ]]; then
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
    echo "EnvironmentFile=-${home_spec}/.config/systemd/user/local-router.env"
    echo "WorkingDirectory=${home_spec}/.config/systemd/user"

    # Basic hardening
    echo "NoNewPrivileges=yes"
    echo "CapabilityBoundingSet="
    echo "AmbientCapabilities="

    # Simple network service (no GPU/DRI needed)
    echo "PrivateDevices=yes"
    echo "PrivateTmp=yes"
    echo "PrivateMounts=yes"
    echo "PrivateIPC=yes"

    echo "ProtectSystem=strict"
    echo "BindPaths=${home_spec}"
    echo "ReadOnlyPaths=/etc/ssl /etc/ca-certificates /etc/resolv.conf /etc/hosts /etc/nsswitch.conf"

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

get_router_args() {
    local -n out_args=$1
    out_args=(
        local-router:app
        --host "${LROUT_HOST}"
        --port "${LROUT_PORT}"
    )

    if [[ -n "${LROUT_EXTRA_ARGS:-}" ]]; then
        local extra_arr=()
        eval "extra_arr=(${LROUT_EXTRA_ARGS})"
        out_args+=("${extra_arr[@]}")
    fi
}

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
    get_router_args args
    local exec_cmd
    exec_cmd=$(format_exec_start "/usr/bin/uvicorn" "${args[@]}")

    cat <<EOF
[Unit]
Description=Local Inference Combined Router (FastAPI)
After=network.target

[Service]
Type=simple
$(get_shared_options service)
ExecStart=${exec_cmd}

Restart=on-failure
RestartSec=10s

StandardOutput=journal
StandardError=journal
SyslogIdentifier=local-router

[Install]
WantedBy=default.target
EOF
}

# Embedded default env file (heredoc written by --install)

generate_env_file() {
    cat <<'EOF'
# local-router.env

# Configuration for the local-router.service FastAPI/uvicorn proxy instance.
#
# Edit this file to switch ports or tune runtime parameters.
# Reload with:  local-router.sh restart

# Port to bind the router to (default: 51080)
LROUT_PORT=51080

# Host to bind the router to (127.0.0.1 for local access only)
LROUT_HOST=127.0.0.1

# Extra arguments to pass to uvicorn
LROUT_EXTRA_ARGS=""

# Default model to route requests to if no model parameter is specified in the request (e.g. in /tokenize)
LROUT_DEFAULT_MODEL="qwen3"

# Logging & Diagnostics verbosity level: 'info' (default), 'verbose', or 'debug'
LROUT_LOG_LEVEL="verbose"

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

    # Resolve source python file location
    # Resolve source python and html file locations
    local script_dir
    script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
    local source_py="${script_dir}/../scripts/local-router.py"
    local source_html="${script_dir}/../scripts/local-router-ui.html"

    if [[ ! -f "${source_py}" ]]; then
        echo "Error: Source Python file not found at ${source_py}" >&2
        exit 1
    fi

    if [[ ! -f "${source_html}" ]]; then
        echo "Error: Source HTML file not found at ${source_html}" >&2
        exit 1
    fi

    # Create directory if needed
    mkdir -p "${SYSTEMD_USER_DIR}"

    # Copy local-router.py and local-router-ui.html to systemd config directory
    echo "Copying local-router.py and local-router-ui.html to ${SYSTEMD_USER_DIR}..."
    cp "${source_py}" "${SYSTEMD_USER_DIR}/local-router.py"
    chmod 644 "${SYSTEMD_USER_DIR}/local-router.py"
    cp "${source_html}" "${SYSTEMD_USER_DIR}/local-router-ui.html"
    chmod 644 "${SYSTEMD_USER_DIR}/local-router-ui.html"

    # Write default env file if it doesn't exist
    if [[ -f "${ENV_FILE}" ]] && [ "${new_config}" != "true" ]; then
        echo "Configuration already exists: ${ENV_FILE}"
    else
        echo "Writing default env file: ${ENV_FILE}"
        generate_env_file >"${ENV_FILE}"
        chmod 600 "${ENV_FILE}"
        echo "Env file written."
    fi

    if [[ -f "${SYSTEMD_USER_DIR}/local-router-usage.json" ]]; then
        echo "[local-router] Preserving local-router-usage.json (not overwritten)"
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
    echo "  Edit the env file to select host/port, then:"
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

    if [[ -f "${SYSTEMD_USER_DIR}/local-router.py" ]]; then
        rm -f "${SYSTEMD_USER_DIR}/local-router.py"
        echo "Removed local-router.py from ${SYSTEMD_USER_DIR}."
    fi

    if [[ -f "${SYSTEMD_USER_DIR}/local-router-ui.html" ]]; then
        rm -f "${SYSTEMD_USER_DIR}/local-router-ui.html"
        echo "Removed local-router-ui.html from ${SYSTEMD_USER_DIR}."
    fi

    if [[ -f "${SYSTEMD_USER_DIR}/local-router-usage.json" ]]; then
        echo "[local-router] Preserving local-router-usage.json (not deleted)"
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
    get_router_args args

    if ! is_systemd_running; then
        echo "Warning: Systemd is not running. Running uvicorn directly in foreground..."
        cd "${SYSTEMD_USER_DIR}"
        if [ $# -gt 0 ]; then
            exec /usr/bin/uvicorn "$@"
        else
            exec /usr/bin/uvicorn "${args[@]}"
        fi
    fi

    echo "Starting uvicorn as a transient systemd service with args: $*"

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
        systemd-run "${opts[@]}" "${SETENV_OPTS[@]}" -- /usr/bin/uvicorn "$@"
    else
        systemd-run "${opts[@]}" "${SETENV_OPTS[@]}" -- /usr/bin/uvicorn "${args[@]}"
    fi
}

cmd_shell() {
    echo "Starting interactive shell in the uvicorn systemd environment..."

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

cmd_test() {
    load_env
    echo "=== Testing Combined Router API ==="
    echo "Querying models endpoint: http://${LROUT_HOST}:${LROUT_PORT}/v1/models"
    local resp
    if ! resp=$(curl -s -f "http://${LROUT_HOST}:${LROUT_PORT}/v1/models"); then
        echo "Error: Failed to fetch models from combined router. Is it running?" >&2
        return 1
    fi
    echo "${resp}"
    if ! echo "${resp}" | grep -q "object"; then
        echo "Error: Unexpected response format from combined router models endpoint." >&2
        return 1
    fi
    echo "Combined router validation: Success."
}

cmd_usage() {
    load_env
    local range="${1:-today}"
    if [[ "$range" != "today" && "$range" != "all" && "$range" != "7d" && "$range" != "30d" && "$range" != "90d" ]]; then
        echo "Error: Invalid range '$range'. Supported values: today, all, 7d, 30d, 90d" >&2
        return 1
    fi

    echo "=== Fetching local-router usage (range: $range) ==="
    if ! curl -s -f "http://${LROUT_HOST}:${LROUT_PORT}/usage?range=${range}&format=text"; then
        echo "Error: Failed to fetch usage from router at http://${LROUT_HOST}:${LROUT_PORT}/usage. Is the service running?" >&2
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
  exec      - Run uvicorn as a transient systemd user service
  cat       - Print service file, environment configuration, and transient exec command
  test      - Run validation tests for the combined router
  usage [today|all|7d|30d|90d] - Print a formatted table of token usage (defaults to today)
EOF
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
    get_router_args args
    echo "/usr/bin/uvicorn ${args[*]}"
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
    cat) cmd_cat ;;
    test) cmd_test "$@" ;;
    usage) cmd_usage "$@" ;;
    *)
        echo "Unknown command: $COMMAND"
        usage
        exit 1
        ;;
    esac
}

main "$@"
