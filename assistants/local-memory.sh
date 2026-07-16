#!/usr/bin/env bash
# local-memory.sh - Manage local hindsight-api systemd user service and sidecars
#
# Usage: local-memory.sh <command> [args...]
#

set -euo pipefail

# Paths

SYSTEMD_USER_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
SERVICE_NAME="local-memory"
SERVICE_FILE="${SYSTEMD_USER_DIR}/${SERVICE_NAME}.service"
ENV_FILE="${SYSTEMD_USER_DIR}/${SERVICE_NAME}.env"
LMEM_HOME="${HOME}/.local/sandbox/local-memory"
VENV_DIR="${LMEM_HOME}/venv"

# Default Configuration Constants
DEFAULT_LMEM_PORT=8888
DEFAULT_LMEM_HOST=127.0.0.1
DEFAULT_LMEM_SERVICE_CMD="%h/.local/sandbox/local-memory/venv/bin/hindsight-api"
DEFAULT_LMEM_SERVICE_ARGS="--port 8888 --host 127.0.0.1"
DEFAULT_LMEM_SIDECARS=""

DEFAULT_HINDSIGHT_API_RUN_MIGRATIONS_ON_STARTUP="true"
DEFAULT_HINDSIGHT_API_WORKER_ENABLED="true"
DEFAULT_HINDSIGHT_API_MCP_ENABLED="true"

# hindsight chat
DEFAULT_HINDSIGHT_API_LLM_PROVIDER=openai
DEFAULT_HINDSIGHT_API_LLM_API_KEY="unused"
DEFAULT_HINDSIGHT_API_LLM_BASE_URL="http://localhost:51080/v1"
DEFAULT_HINDSIGHT_API_LLM_MODEL="qwen3"
DEFAULT_HINDSIGHT_API_LLM_EXTRA_BODY='{"chat_template_kwargs": {"enable_thinking": false}}'

# hindsight embedding
DEFAULT_HINDSIGHT_API_EMBEDDINGS_PROVIDER=openai
DEFAULT_HINDSIGHT_API_EMBEDDINGS_OPENAI_API_KEY="unused"
DEFAULT_HINDSIGHT_API_EMBEDDINGS_OPENAI_BASE_URL="http://localhost:51080/v1"
DEFAULT_HINDSIGHT_API_EMBEDDINGS_OPENAI_MODEL="qwen3-embedding"

# hindsight rerank
DEFAULT_HINDSIGHT_API_RERANKER_PROVIDER=cohere
DEFAULT_HINDSIGHT_API_RERANKER_COHERE_API_KEY="unused"
DEFAULT_HINDSIGHT_API_RERANKER_COHERE_BASE_URL="http://localhost:51080/v1"
DEFAULT_HINDSIGHT_API_RERANKER_COHERE_MODEL="qwen3-reranker"

# hindsight database
DEFAULT_HINDSIGHT_API_DATABASE_BACKEND=postgresql
DEFAULT_HINDSIGHT_API_VECTOR_EXTENSION=pgvector
DEFAULT_HINDSIGHT_API_TEXT_SEARCH_EXTENSION=pgroonga
DEFAULT_HINDSIGHT_API_DATABASE_URL="postgresql://username:password@localhost:5432/dbname"

# Load environment

load_env() {
    # Capture environment overrides passed by caller
    local env_lmem_port="${LMEM_PORT:-}"
    local env_lmem_host="${LMEM_HOST:-}"
    local env_lmem_service_cmd="${LMEM_SERVICE_CMD:-}"
    local env_lmem_service_args="${LMEM_SERVICE_ARGS:-}"
    local env_lmem_sidecars="${LMEM_SIDECARS:-}"

    local env_hindsight_api_run_migrations_on_startup="${HINDSIGHT_API_RUN_MIGRATIONS_ON_STARTUP:-}"
    local env_hindsight_api_worker_enabled="${HINDSIGHT_API_WORKER_ENABLED:-}"
    local env_hindsight_api_mcp_enabled="${HINDSIGHT_API_MCP_ENABLED:-}"

    local env_hindsight_api_llm_provider="${HINDSIGHT_API_LLM_PROVIDER:-}"
    local env_hindsight_api_llm_api_key="${HINDSIGHT_API_LLM_API_KEY:-}"
    local env_hindsight_api_llm_base_url="${HINDSIGHT_API_LLM_BASE_URL:-}"
    local env_hindsight_api_llm_model="${HINDSIGHT_API_LLM_MODEL:-}"
    local env_hindsight_api_llm_extra_body="${HINDSIGHT_API_LLM_EXTRA_BODY:-}"

    local env_hindsight_api_embeddings_provider="${HINDSIGHT_API_EMBEDDINGS_PROVIDER:-}"
    local env_hindsight_api_embeddings_openai_api_key="${HINDSIGHT_API_EMBEDDINGS_OPENAI_API_KEY:-}"
    local env_hindsight_api_embeddings_openai_base_url="${HINDSIGHT_API_EMBEDDINGS_OPENAI_BASE_URL:-}"
    local env_hindsight_api_embeddings_openai_model="${HINDSIGHT_API_EMBEDDINGS_OPENAI_MODEL:-}"

    local env_hindsight_api_reranker_provider="${HINDSIGHT_API_RERANKER_PROVIDER:-}"
    local env_hindsight_api_reranker_cohere_api_key="${HINDSIGHT_API_RERANKER_COHERE_API_KEY:-}"
    local env_hindsight_api_reranker_cohere_base_url="${HINDSIGHT_API_RERANKER_COHERE_BASE_URL:-}"
    local env_hindsight_api_reranker_cohere_model="${HINDSIGHT_API_RERANKER_COHERE_MODEL:-}"

    local env_hindsight_api_database_backend="${HINDSIGHT_API_DATABASE_BACKEND:-}"
    local env_hindsight_api_vector_extension="${HINDSIGHT_API_VECTOR_EXTENSION:-}"
    local env_hindsight_api_text_search_extension="${HINDSIGHT_API_TEXT_SEARCH_EXTENSION:-}"
    local env_hindsight_api_database_url="${HINDSIGHT_API_DATABASE_URL:-}"

    # Apply defaults using constants
    export LMEM_PORT="${DEFAULT_LMEM_PORT}"
    export LMEM_HOST="${DEFAULT_LMEM_HOST}"
    export LMEM_SERVICE_CMD="${DEFAULT_LMEM_SERVICE_CMD}"
    export LMEM_SERVICE_ARGS="${DEFAULT_LMEM_SERVICE_ARGS}"
    export LMEM_SIDECARS="${DEFAULT_LMEM_SIDECARS}"

    export HINDSIGHT_API_RUN_MIGRATIONS_ON_STARTUP="${DEFAULT_HINDSIGHT_API_RUN_MIGRATIONS_ON_STARTUP}"
    export HINDSIGHT_API_WORKER_ENABLED="${DEFAULT_HINDSIGHT_API_WORKER_ENABLED}"
    export HINDSIGHT_API_MCP_ENABLED="${DEFAULT_HINDSIGHT_API_MCP_ENABLED}"

    export HINDSIGHT_API_LLM_PROVIDER="${DEFAULT_HINDSIGHT_API_LLM_PROVIDER}"
    export HINDSIGHT_API_LLM_API_KEY="${DEFAULT_HINDSIGHT_API_LLM_API_KEY}"
    export HINDSIGHT_API_LLM_BASE_URL="${DEFAULT_HINDSIGHT_API_LLM_BASE_URL}"
    export HINDSIGHT_API_LLM_MODEL="${DEFAULT_HINDSIGHT_API_LLM_MODEL}"
    export HINDSIGHT_API_LLM_EXTRA_BODY="${DEFAULT_HINDSIGHT_API_LLM_EXTRA_BODY}"

    export HINDSIGHT_API_EMBEDDINGS_PROVIDER="${DEFAULT_HINDSIGHT_API_EMBEDDINGS_PROVIDER}"
    export HINDSIGHT_API_EMBEDDINGS_OPENAI_API_KEY="${DEFAULT_HINDSIGHT_API_EMBEDDINGS_OPENAI_API_KEY}"
    export HINDSIGHT_API_EMBEDDINGS_OPENAI_BASE_URL="${DEFAULT_HINDSIGHT_API_EMBEDDINGS_OPENAI_BASE_URL}"
    export HINDSIGHT_API_EMBEDDINGS_OPENAI_MODEL="${DEFAULT_HINDSIGHT_API_EMBEDDINGS_OPENAI_MODEL}"

    export HINDSIGHT_API_RERANKER_PROVIDER="${DEFAULT_HINDSIGHT_API_RERANKER_PROVIDER}"
    export HINDSIGHT_API_RERANKER_COHERE_API_KEY="${DEFAULT_HINDSIGHT_API_RERANKER_COHERE_API_KEY}"
    export HINDSIGHT_API_RERANKER_COHERE_BASE_URL="${DEFAULT_HINDSIGHT_API_RERANKER_COHERE_BASE_URL}"
    export HINDSIGHT_API_RERANKER_COHERE_MODEL="${DEFAULT_HINDSIGHT_API_RERANKER_COHERE_MODEL}"

    export HINDSIGHT_API_DATABASE_BACKEND="${DEFAULT_HINDSIGHT_API_DATABASE_BACKEND}"
    export HINDSIGHT_API_VECTOR_EXTENSION="${DEFAULT_HINDSIGHT_API_VECTOR_EXTENSION}"
    export HINDSIGHT_API_TEXT_SEARCH_EXTENSION="${DEFAULT_HINDSIGHT_API_TEXT_SEARCH_EXTENSION}"
    export HINDSIGHT_API_DATABASE_URL="${DEFAULT_HINDSIGHT_API_DATABASE_URL}"

    # Source the env file and automatically export all variables
    if [[ -f "$ENV_FILE" ]]; then
        set +u
        set -a
        # shellcheck disable=SC1090
        source "$ENV_FILE"
        set +a
        set -u
    fi

    # Re-apply captured overrides
    if [[ -n "$env_lmem_port" ]]; then export LMEM_PORT="$env_lmem_port"; fi
    if [[ -n "$env_lmem_host" ]]; then export LMEM_HOST="$env_lmem_host"; fi
    if [[ -n "$env_lmem_service_cmd" ]]; then export LMEM_SERVICE_CMD="$env_lmem_service_cmd"; fi
    if [[ -n "$env_lmem_service_args" ]]; then export LMEM_SERVICE_ARGS="$env_lmem_service_args"; fi
    if [[ -n "$env_lmem_sidecars" ]]; then export LMEM_SIDECARS="$env_lmem_sidecars"; fi

    if [[ -n "$env_hindsight_api_run_migrations_on_startup" ]]; then export HINDSIGHT_API_RUN_MIGRATIONS_ON_STARTUP="$env_hindsight_api_run_migrations_on_startup"; fi
    if [[ -n "$env_hindsight_api_worker_enabled" ]]; then export HINDSIGHT_API_WORKER_ENABLED="$env_hindsight_api_worker_enabled"; fi
    if [[ -n "$env_hindsight_api_mcp_enabled" ]]; then export HINDSIGHT_API_MCP_ENABLED="$env_hindsight_api_mcp_enabled"; fi

    if [[ -n "$env_hindsight_api_llm_provider" ]]; then export HINDSIGHT_API_LLM_PROVIDER="$env_hindsight_api_llm_provider"; fi
    if [[ -n "$env_hindsight_api_llm_api_key" ]]; then export HINDSIGHT_API_LLM_API_KEY="$env_hindsight_api_llm_api_key"; fi
    if [[ -n "$env_hindsight_api_llm_base_url" ]]; then export HINDSIGHT_API_LLM_BASE_URL="$env_hindsight_api_llm_base_url"; fi
    if [[ -n "$env_hindsight_api_llm_model" ]]; then export HINDSIGHT_API_LLM_MODEL="$env_hindsight_api_llm_model"; fi
    if [[ -n "$env_hindsight_api_llm_extra_body" ]]; then export HINDSIGHT_API_LLM_EXTRA_BODY="$env_hindsight_api_llm_extra_body"; fi

    if [[ -n "$env_hindsight_api_embeddings_provider" ]]; then export HINDSIGHT_API_EMBEDDINGS_PROVIDER="$env_hindsight_api_embeddings_provider"; fi
    if [[ -n "$env_hindsight_api_embeddings_openai_api_key" ]]; then export HINDSIGHT_API_EMBEDDINGS_OPENAI_API_KEY="$env_hindsight_api_embeddings_openai_api_key"; fi
    if [[ -n "$env_hindsight_api_embeddings_openai_base_url" ]]; then export HINDSIGHT_API_EMBEDDINGS_OPENAI_BASE_URL="$env_hindsight_api_embeddings_openai_base_url"; fi
    if [[ -n "$env_hindsight_api_embeddings_openai_model" ]]; then export HINDSIGHT_API_EMBEDDINGS_OPENAI_MODEL="$env_hindsight_api_embeddings_openai_model"; fi

    if [[ -n "$env_hindsight_api_reranker_provider" ]]; then export HINDSIGHT_API_RERANKER_PROVIDER="$env_hindsight_api_reranker_provider"; fi
    if [[ -n "$env_hindsight_api_reranker_cohere_api_key" ]]; then export HINDSIGHT_API_RERANKER_COHERE_API_KEY="$env_hindsight_api_reranker_cohere_api_key"; fi
    if [[ -n "$env_hindsight_api_reranker_cohere_base_url" ]]; then export HINDSIGHT_API_RERANKER_COHERE_BASE_URL="$env_hindsight_api_reranker_cohere_base_url"; fi
    if [[ -n "$env_hindsight_api_reranker_cohere_model" ]]; then export HINDSIGHT_API_RERANKER_COHERE_MODEL="$env_hindsight_api_reranker_cohere_model"; fi

    if [[ -n "$env_hindsight_api_database_backend" ]]; then export HINDSIGHT_API_DATABASE_BACKEND="$env_hindsight_api_database_backend"; fi
    if [[ -n "$env_hindsight_api_vector_extension" ]]; then export HINDSIGHT_API_VECTOR_EXTENSION="$env_hindsight_api_vector_extension"; fi
    if [[ -n "$env_hindsight_api_text_search_extension" ]]; then export HINDSIGHT_API_TEXT_SEARCH_EXTENSION="$env_hindsight_api_text_search_extension"; fi
    if [[ -n "$env_hindsight_api_database_url" ]]; then export HINDSIGHT_API_DATABASE_URL="$env_hindsight_api_database_url"; fi
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
        if declare -p "$key" &>/dev/null || [[ "$key" =~ ^(LMEM_|HINDSIGHT_) ]]; then
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
    echo "EnvironmentFile=-${home_spec}/.config/systemd/user/local-memory.env"
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

sanitize_var_name() {
    local val="$1"
    val="${val//-/_}"
    val="${val//./_}"
    val="${val^^}"
    echo "$val"
}

# Build the complete start command (main daemon + sidecars background logic)
get_exec_start_cmd() {
    local target="$1" # "systemd" or "bash"
    shift

    local dol
    if [ "$target" = "systemd" ]; then
        dol="\$\$"
    else
        dol="\$"
    fi

    local service_cmd="${LMEM_SERVICE_CMD}"
    # Resolve %h or ~ in systemd and bash
    if [ "$target" = "systemd" ]; then
        service_cmd="${service_cmd//\$HOME/"%h"}"
        service_cmd="${service_cmd//\~/"%h"}"
    else
        service_cmd="${service_cmd//%h/"$HOME"}"
        service_cmd="${service_cmd//\~/"$HOME"}"
        service_cmd="${service_cmd//\$HOME/"$HOME"}"
    fi

    local service_args
    if [ $# -gt 0 ]; then
        local custom_args=()
        for arg in "$@"; do
            local escaped="${arg//\\/\\\\}"
            escaped="${escaped//\"/\\\"}"
            if [[ "$escaped" =~ [[:space:]] ]]; then
                escaped="\"${escaped}\""
            fi
            custom_args+=("${escaped}")
        done
        service_args="${custom_args[*]}"
    else
        service_args="${LMEM_SERVICE_ARGS}"
    fi

    local sidecars_val="${LMEM_SIDECARS:-}"
    sidecars_val="${sidecars_val//;/ }"
    sidecars_val="${sidecars_val//$'\n'/ }"

    local sidecars_exec=""
    local idx=0
    local kill_pids=""
    for sidecar in ${sidecars_val}; do
        local var_name
        var_name=$(sanitize_var_name "$sidecar")
        local cmd_var="LMEM_SIDECAR_${var_name}_CMD"
        local cmd_val="${!cmd_var:-}"
        if [[ -z "$cmd_val" ]]; then
            cmd_val="$sidecar"
        fi

        # Resolve paths in cmd_val
        if [ "$target" = "systemd" ]; then
            cmd_val="${cmd_val//\$HOME/"%h"}"
            cmd_val="${cmd_val//\~/"%h"}"
        else
            cmd_val="${cmd_val//%h/"$HOME"}"
            cmd_val="${cmd_val//\~/"$HOME"}"
            cmd_val="${cmd_val//\$HOME/"$HOME"}"
        fi

        local args_var="LMEM_SIDECAR_${var_name}_ARGS"
        local args_val="${!args_var:-}"

        local env_remove_var="LMEM_SIDECAR_${var_name}_ENV_REMOVE"
        local env_remove_val="${!env_remove_var:-}"
        local env_flags=""
        for r in ${env_remove_val}; do
            env_flags="$env_flags -u $r"
        done

        local env_override_var="LMEM_SIDECAR_${var_name}_ENV_OVERRIDE"
        local env_override_val="${!env_override_var:-}"
        for o in ${env_override_val}; do
            env_flags="$env_flags $o"
        done

        sidecars_exec="${sidecars_exec}env${env_flags} ${cmd_val} ${args_val} & LMEM_SIDECAR_PID_${idx}=${dol}! ; "
        kill_pids="${kill_pids} ${dol}LMEM_SIDECAR_PID_${idx}"
        idx=$((idx + 1))
    done

    if [[ -n "$sidecars_exec" ]]; then
        echo "/bin/bash -c 'trap \"kill ${dol}MAIN_PID ${kill_pids} 2>/dev/null || true\" EXIT ; ${service_cmd} ${service_args} & MAIN_PID=${dol}! ; ${sidecars_exec} wait -n'"
    else
        echo "${service_cmd} ${service_args}"
    fi
}

generate_service_file() {
    load_env
    local exec_cmd
    exec_cmd=$(get_exec_start_cmd systemd)

    cat <<EOF
[Unit]
Description=Hindsight Local Memory Service (FastAPI)
After=network.target

[Service]
Type=simple
$(get_shared_options service)
ExecStart=${exec_cmd}

Restart=on-failure
RestartSec=10s

StandardOutput=journal
StandardError=journal
SyslogIdentifier=local-memory

[Install]
WantedBy=default.target
EOF
}

generate_env_file() {
    cat <<EOF
# local-memory.env

# Configuration for the local-memory.service Hindsight instance.
#
# Edit this file to switch ports, adjust models, or configure databases.
# Reload with: local-memory.sh restart

# Service Configuration
LMEM_PORT="${DEFAULT_LMEM_PORT}"
LMEM_HOST="${DEFAULT_LMEM_HOST}"
LMEM_SERVICE_CMD="${DEFAULT_LMEM_SERVICE_CMD}"
LMEM_SERVICE_ARGS="${DEFAULT_LMEM_SERVICE_ARGS}"
LMEM_SIDECARS="${DEFAULT_LMEM_SIDECARS}"

# Hindsight daemon configuration
HINDSIGHT_API_RUN_MIGRATIONS_ON_STARTUP="${DEFAULT_HINDSIGHT_API_RUN_MIGRATIONS_ON_STARTUP}"
HINDSIGHT_API_WORKER_ENABLED="${DEFAULT_HINDSIGHT_API_WORKER_ENABLED}"
HINDSIGHT_API_MCP_ENABLED="${DEFAULT_HINDSIGHT_API_MCP_ENABLED}"

# hindsight chat
HINDSIGHT_API_LLM_PROVIDER="${DEFAULT_HINDSIGHT_API_LLM_PROVIDER}"
HINDSIGHT_API_LLM_API_KEY="${DEFAULT_HINDSIGHT_API_LLM_API_KEY}"
HINDSIGHT_API_LLM_BASE_URL="${DEFAULT_HINDSIGHT_API_LLM_BASE_URL}"
HINDSIGHT_API_LLM_MODEL="${DEFAULT_HINDSIGHT_API_LLM_MODEL}"
HINDSIGHT_API_LLM_EXTRA_BODY='${DEFAULT_HINDSIGHT_API_LLM_EXTRA_BODY}'

# hindsight embedding
HINDSIGHT_API_EMBEDDINGS_PROVIDER="${DEFAULT_HINDSIGHT_API_EMBEDDINGS_PROVIDER}"
HINDSIGHT_API_EMBEDDINGS_OPENAI_API_KEY="${DEFAULT_HINDSIGHT_API_EMBEDDINGS_OPENAI_API_KEY}"
HINDSIGHT_API_EMBEDDINGS_OPENAI_BASE_URL="${DEFAULT_HINDSIGHT_API_EMBEDDINGS_OPENAI_BASE_URL}"
HINDSIGHT_API_EMBEDDINGS_OPENAI_MODEL="${DEFAULT_HINDSIGHT_API_EMBEDDINGS_OPENAI_MODEL}"

# hindsight rerank
HINDSIGHT_API_RERANKER_PROVIDER="${DEFAULT_HINDSIGHT_API_RERANKER_PROVIDER}"
HINDSIGHT_API_RERANKER_COHERE_API_KEY="${DEFAULT_HINDSIGHT_API_RERANKER_COHERE_API_KEY}"
HINDSIGHT_API_RERANKER_COHERE_BASE_URL="${DEFAULT_HINDSIGHT_API_RERANKER_COHERE_BASE_URL}"
HINDSIGHT_API_RERANKER_COHERE_MODEL="${DEFAULT_HINDSIGHT_API_RERANKER_COHERE_MODEL}"

# hindsight database
HINDSIGHT_API_DATABASE_BACKEND="${DEFAULT_HINDSIGHT_API_DATABASE_BACKEND}"
HINDSIGHT_API_VECTOR_EXTENSION="${DEFAULT_HINDSIGHT_API_VECTOR_EXTENSION}"
HINDSIGHT_API_TEXT_SEARCH_EXTENSION="${DEFAULT_HINDSIGHT_API_TEXT_SEARCH_EXTENSION}"
HINDSIGHT_API_DATABASE_URL="${DEFAULT_HINDSIGHT_API_DATABASE_URL}"
EOF
}

write_service_file() {
    generate_service_file >"${SERVICE_FILE}"
    chmod 644 "${SERVICE_FILE}"
    run_systemctl daemon-reload
}

require_uv() {
    if ! command -v uv &>/dev/null; then
        echo "Error: 'uv' is not installed or not in PATH." >&2
        exit 1
    fi
}

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

    require_uv

    echo "Installing Hindsight virtual environment..."
    mkdir -p "${LMEM_HOME}"
    if [[ -d "${VENV_DIR}" ]]; then
        echo "Cleaning up existing virtual environment..."
        rm -rf "${VENV_DIR}"
    fi

    # Create virtual environment using system Python 3
    uv venv --clear --python /usr/bin/python3 "${VENV_DIR}"

    # fix limitation for litellm different.
    echo "Installing Hindsight packages into venv..."
    uv pip install --python "${VENV_DIR}" hindsight-client hindsight-api-slim

    # Create directory if needed
    mkdir -p "${SYSTEMD_USER_DIR}"

    # Write default env file if it doesn't exist
    if [[ -f "${ENV_FILE}" ]] && [ "${new_config}" != "true" ]; then
        echo "Configuration already exists: ${ENV_FILE}"
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
    echo "  Edit the env file to configure databases/ports, then:"
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

    # Remove virtual environment
    if [[ -d "${VENV_DIR}" ]]; then
        echo "Removing virtual environment at ${VENV_DIR}..."
        rm -rf "${VENV_DIR}"
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

    local exec_cmd
    exec_cmd=$(get_exec_start_cmd bash "$@")

    if ! is_systemd_running; then
        echo "Warning: Systemd is not running. Running directly in foreground..."
        eval exec "$exec_cmd"
    fi

    echo "Starting local-memory as a transient systemd service..."

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

    # shellcheck disable=SC2086
    systemd-run "${opts[@]}" "${SETENV_OPTS[@]}" /bin/bash -c "$exec_cmd"
}

cmd_run() {
    parse_env_args "$@"
    set -- "${COMMAND_ARGS[@]}"

    if [ $# -lt 1 ]; then
        echo "Error: run requires a command to execute." >&2
        exit 1
    fi

    if ! is_systemd_running; then
        echo "Warning: Systemd is not running. Running command directly in foreground..."
        exec "$@"
    fi

    echo "Running command inside the local-memory systemd environment: $*"

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

cmd_shell() {
    parse_env_args "$@"
    set -- "${COMMAND_ARGS[@]}"

    if ! is_systemd_running; then
        echo "Warning: Systemd is not running. Spawning shell directly in foreground..."
        exec "${SHELL:-/bin/bash}" "$@"
    fi

    echo "Starting interactive shell in the local-memory systemd environment..."

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
    get_exec_start_cmd bash
}

cmd_test() {
    load_env
    echo "=== Testing Hindsight Memory API ==="
    echo "Querying API health: http://${LMEM_HOST}:${LMEM_PORT}/health"
    local resp
    if ! resp=$(curl -s -f --max-time 10 "http://${LMEM_HOST}:${LMEM_PORT}/health"); then
        echo "Error: Failed to connect to Hindsight Memory API. Is the service running?" >&2
        return 1
    fi
    echo "${resp}"
    echo "Hindsight Memory API validation: Success."
}

usage() {
    cat <<EOF
Usage: $0 <command> [args...]
Commands:
  install [--no-start] [--new-config] - Setup virtualenv, configuration, and systemd service
  uninstall - Stop and remove systemd service and virtualenv
  start     - Start the systemd service
  stop      - Stop the systemd service
  restart   - Restart the systemd service
  status    - View systemd service status
  enable    - Enable systemd service on boot
  disable   - Disable systemd service on boot
  logs      - Tail the systemd service logs
  edit      - Edit the .env file and restart the service upon exit
  exec      - Run hindsight-api as a transient systemd user service or foreground daemon
  run       - Run a custom command in the service environment
  shell     - Spawn a shell in the service environment
  cat       - Print service file, environment configuration, and transient exec command
  test      - Run validation tests/health checks for the service
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
