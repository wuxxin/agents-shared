#!/usr/bin/env bash
# local-inference.sh - Coordinate local inference systemd user services
#
# Usage: local-inference.sh <command> [args...]
#

set -euo pipefail

# Paths

SYSTEMD_USER_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
ENV_FILE="${SYSTEMD_USER_DIR}/local-inference.env"

# Default parameters

# shellcheck disable=SC2034
LCHAT_ENABLED=1
# shellcheck disable=SC2034
LMBD_ENABLED=1
# shellcheck disable=SC2034
LRR_ENABLED=1
# shellcheck disable=SC2034
LSTT_ENABLED=1
# shellcheck disable=SC2034
LTTS_ENABLED=1
# shellcheck disable=SC2034
LIMG_ENABLED=1
# shellcheck disable=SC2034
LROUT_ENABLED=1
# shellcheck disable=SC2034
LMEM_ENABLED=1

# Load environment

load_env() {
    if [[ -f "$ENV_FILE" ]]; then
        set +u
        # Source the env file to load enabling variables and overrides
        # shellcheck disable=SC1090
        source "$ENV_FILE"
        set -u
    fi
}

# Helper to execute systemctl commands only if systemd user manager is reachable

is_systemd_running() {
    [ -S "${XDG_RUNTIME_DIR:-/run/user/$(id -u)}/systemd/private" ]
}

# Apply override to a specific service env file

apply_override() {
    local env_file="$1"
    local key="$2"
    local val="$3"

    touch "$env_file"

    if grep -q "^${key}=" "$env_file"; then
        # Key exists active, replace it
        sed -i "s|^${key}=.*|${key}=${val}|" "$env_file"
    else
        # Delete any commented-out instances to avoid duplication, then append the override
        sed -i "/^#[[:space:]]*${key}=/d" "$env_file"
        echo "${key}=${val}" >>"$env_file"
    fi
}

# Apply all overrides for a given service prefix

apply_service_overrides() {
    local svc_prefix="$1"
    local target_env_file="$2"

    local override_var_name="${svc_prefix}_OVERRIDE"

    if declare -p "$override_var_name" &>/dev/null; then
        # Use a nameref to access the array elements
        declare -n items="$override_var_name"
        for item in "${items[@]}"; do
            if [[ "$item" =~ = ]]; then
                local key="${item%%=*}"
                local val="${item#*=}"
                echo "  Applying override: ${key}=${val}"
                apply_override "$target_env_file" "$key" "$val"
            fi
        done
    fi
}

# Embedded default env file (heredoc written by install)

generate_env_file() {
    cat <<'EOF'
# local-inference.env

# Configuration wrapper for local AI inference services.
#
# Toggle service activation (1=enabled, 0=disabled) and define overrides
# for individual service environment files.
#
# Note on Combined Embeddings Mode:
# To serve both Chat and Embedding models on the same llama-server instance (on port 50080):
# 1. Set LMBD_ENABLED=0 to disable the separate local-embedding service.
# 2. Add 'LCHAT_EMBEDDING_ENABLED=true' inside LCHAT_OVERRIDE.

LCHAT_ENABLED=1
LMBD_ENABLED=1
LRR_ENABLED=1
LSTT_ENABLED=1
LTTS_ENABLED=1
LIMG_ENABLED=1
LROUT_ENABLED=1
LMEM_ENABLED=1

# ROCm0 = dgpu
# Vulkan0 = igpu
# Vulkan1 = dgpu

# Overrides for specific services (applied on install/start/restart/edit), can be defined as Bash arrays. E.g.:
# run CHAT on vulkan/dgpu
LCHAT_OVERRIDE=(
    'LCHAT_DEVICE="Vulkan1"'
    # disable Vulkan MMVQ activation quantization
    'GGML_VK_DISABLE_MMVQ=1'
    # Unified Cache: If enabled, cparams.n_ctx_seq is set equal to cparams.n_ctx,
    #   allowing slots to dynamically share a single unified KV buffer up to the full total context capacity.
    'LCHAT_EXTRA_ARGS="--kv-unified"'
    # Disable combined embedding on port 50080
    'LCHAT_EMBEDDING_ENABLED=false'
    # Enable code completion service model
    'LCOMP_ENABLED=true'
)
# run EMBEDDING on vulkan/dgpu
LMBD_OVERRIDE=(
    'LMBD_DEVICE="Vulkan1"'
)
# run RERANK on cpu (llama-server default) or switch engine to infinity (ONNX optimum)
LRR_OVERRIDE=(
    'LRR_DEVICE="none"'
    # 'LRR_ENGINE="infinity"'
    # 'INFINITY_ENGINE="optimum"'
    # 'INFINITY_DEVICE="cuda"'
)
# run SPEECH-TO-TEXT on vulkan/igpu
LSTT_OVERRIDE=(
    'CUDA_VISIBLE_DEVICES=""'
    # "0" selects Vulkan0, because we hide hip/rocm devices
    'LSTT_DEVICE="0"'
)
# run TEXT-TO-SPEECH on cpu
LTTS_OVERRIDE=(
    'LTTS_MODE="cpu"'
    'LTTS_DEVICE="none"'
)
# run IMAGE on vulkan/igpu and te on cpu
LIMG_OVERRIDE=(
    'LIMG_BACKEND="vulkan0,te=cpu"'
    # limit the command buffer batch size to 20 to keep VAE compute from timeout
    'GGML_VK_MAX_NODES_PER_SUBMIT=20'
)
LROUT_OVERRIDE=(
)
LMEM_OVERRIDE=(
    # set the actual db uri
    'HINDSIGHT_API_DATABASE_URL="postgresql://username:password@localhost:5432/dbname"'
    # Hindsight worker control plane / metrics HTTP port (default: 8889, set to 0 to disable control plane)
    'HINDSIGHT_API_WORKER_HTTP_PORT="8889"'
)

EOF
}

# Actions

cmd_install() {
    local new_config=false
    while [ $# -gt 0 ]; do
        case "$1" in
        --new-config) new_config=true ;;
        esac
        shift
    done

    echo "Installing local-inference wrapper configuration..."
    mkdir -p "${SYSTEMD_USER_DIR}"

    if [[ -f "${ENV_FILE}" ]]; then
        echo "Warning: Wrapper env file already exists, skipping: ${ENV_FILE}"
    else
        echo "Writing default wrapper env file: ${ENV_FILE}"
        generate_env_file >"${ENV_FILE}"
        chmod 600 "${ENV_FILE}"
    fi

    # Reload variables from env file
    load_env

    local services=("local-chat" "local-embedding" "local-rerank" "local-speech-to-text" "local-text-to-speech" "local-image" "local-router" "local-memory")
    local prefixes=("LCHAT" "LMBD" "LRR" "LSTT" "LTTS" "LIMG" "LROUT" "LMEM")
    local script_dir
    script_dir="$(dirname "$0")"

    # Always install all services (per user comment)
    for i in "${!services[@]}"; do
        local svc="${services[$i]}"
        local pref="${prefixes[$i]}"
        echo "Installing service: ${svc}..."

        local install_args=("--no-start")
        if [ "${new_config}" = "true" ]; then
            install_args+=("--new-config")
        fi

        "${script_dir}/${svc}.sh" install "${install_args[@]}"

        # Apply overrides if defined
        local target_env_file="${SYSTEMD_USER_DIR}/${svc}.env"
        apply_service_overrides "$pref" "$target_env_file"
    done

    echo "Installation complete."
}

cmd_uninstall() {
    echo "Uninstalling all managed local services..."
    local services=("local-chat" "local-embedding" "local-rerank" "local-speech-to-text" "local-text-to-speech" "local-image" "local-router" "local-memory")
    local script_dir
    script_dir="$(dirname "$0")"

    for svc in "${services[@]}"; do
        if [[ -f "${script_dir}/${svc}.sh" ]]; then
            echo "Uninstalling ${svc}..."
            "${script_dir}/${svc}.sh" uninstall || true
        fi
    done

    echo "Uninstallation complete. Configuration in ${ENV_FILE} is preserved."
}

match_subservice_index() {
    local query="$1"
    local query_lower
    query_lower="$(echo "$query" | tr '[:upper:]' '[:lower:]')"

    local services=("local-chat" "local-embedding" "local-rerank" "local-speech-to-text" "local-text-to-speech" "local-image" "local-router" "local-memory")
    local prefixes=("LCHAT" "LMBD" "LRR" "LSTT" "LTTS" "LIMG" "LROUT" "LMEM")
    local aliases=("chat" "embedding" "rerank" "stt" "tts" "image" "router" "memory")

    for i in "${!services[@]}"; do
        local svc="${services[$i]}"
        local pref="${prefixes[$i]}"
        local alias="${aliases[$i]}"
        local pref_lower
        pref_lower="$(echo "$pref" | tr '[:upper:]' '[:lower:]')"

        if [[ "$query_lower" == "$svc" || "$query_lower" == "$pref_lower" || "$query_lower" == "$alias" ]]; then
            echo "$i"
            return 0
        fi
    done
    return 1
}

cmd_status() {
    local target_service="${1:-}"
    local services=("local-chat" "local-embedding" "local-rerank" "local-speech-to-text" "local-text-to-speech" "local-image" "local-router" "local-memory")

    if [ -n "$target_service" ]; then
        local idx
        if ! idx="$(match_subservice_index "$target_service")"; then
            echo "Error: Unknown subservice '$target_service'."
            echo "Valid subservices: ${services[*]}"
            exit 1
        fi
        services=("${services[$idx]}")
    fi

    for svc in "${services[@]}"; do
        echo "● ${svc}.service"
        if is_systemd_running; then
            systemctl --user status "${svc}.service" 2>/dev/null | grep -E "Loaded:|Active:|Main PID:" || echo "  (Service inactive or not loaded)"
        else
            echo "  Warning: systemd user manager is not reachable."
        fi
        echo ""
    done
}

cmd_logs() {
    local services=("local-chat" "local-embedding" "local-rerank" "local-speech-to-text" "local-text-to-speech" "local-image" "local-router" "local-memory")
    local log_args=()
    for svc in "${services[@]}"; do
        log_args+=("-u" "${svc}.service")
    done
    journalctl --user "${log_args[@]}" "$@"
}

cmd_edit() {
    mkdir -p "$(dirname "${ENV_FILE}")"
    touch "${ENV_FILE}"
    ${EDITOR:-nano} "${ENV_FILE}"
    echo "Restarting services to apply updated environment..."
    cmd_restart
}

cmd_start() {
    local target_service="${1:-}"
    load_env

    local services=("local-chat" "local-embedding" "local-rerank" "local-speech-to-text" "local-text-to-speech" "local-image" "local-router" "local-memory")
    local prefixes=("LCHAT" "LMBD" "LRR" "LSTT" "LTTS" "LIMG" "LROUT" "LMEM")
    local script_dir
    script_dir="$(dirname "$0")"

    if [ -n "$target_service" ]; then
        local idx
        if ! idx="$(match_subservice_index "$target_service")"; then
            echo "Error: Unknown subservice '$target_service'."
            echo "Valid subservices: ${services[*]}"
            exit 1
        fi

        local svc="${services[$idx]}"
        local pref="${prefixes[$idx]}"

        local enabled_var="${pref}_ENABLED"
        local is_enabled=0
        eval "is_enabled=\${$enabled_var:-0}"

        if [ "$is_enabled" = "1" ]; then
            echo "Starting enabled service: ${svc}..."
            local target_env_file="${SYSTEMD_USER_DIR}/${svc}.env"
            apply_service_overrides "$pref" "$target_env_file"

            "${script_dir}/${svc}.sh" enable
            "${script_dir}/${svc}.sh" start
        else
            echo "Service ${svc} is disabled in configuration (${enabled_var}=0)."
        fi
        return 0
    fi

    for i in "${!services[@]}"; do
        local svc="${services[$i]}"
        local pref="${prefixes[$i]}"

        local enabled_var="${pref}_ENABLED"
        local is_enabled=0
        eval "is_enabled=\${$enabled_var:-0}"

        if [ "$is_enabled" = "1" ]; then
            echo "Starting enabled service: ${svc}..."
            local target_env_file="${SYSTEMD_USER_DIR}/${svc}.env"
            apply_service_overrides "$pref" "$target_env_file"

            "${script_dir}/${svc}.sh" enable
            "${script_dir}/${svc}.sh" start
        fi
    done
}

cmd_stop() {
    local target_service="${1:-}"
    load_env

    local services=("local-chat" "local-embedding" "local-rerank" "local-speech-to-text" "local-text-to-speech" "local-image" "local-router" "local-memory")
    local prefixes=("LCHAT" "LMBD" "LRR" "LSTT" "LTTS" "LIMG" "LROUT" "LMEM")
    local script_dir
    script_dir="$(dirname "$0")"

    if [ -n "$target_service" ]; then
        local idx
        if ! idx="$(match_subservice_index "$target_service")"; then
            echo "Error: Unknown subservice '$target_service'."
            echo "Valid subservices: ${services[*]}"
            exit 1
        fi

        local svc="${services[$idx]}"
        local pref="${prefixes[$idx]}"

        local enabled_var="${pref}_ENABLED"
        local is_enabled=0
        eval "is_enabled=\${$enabled_var:-0}"

        if [ "$is_enabled" = "1" ]; then
            echo "Stopping enabled service: ${svc}..."
            "${script_dir}/${svc}.sh" stop || true
        else
            echo "Stopping and disabling service: ${svc}..."
            "${script_dir}/${svc}.sh" stop || true
            "${script_dir}/${svc}.sh" disable || true
        fi
        return 0
    fi

    for i in "${!services[@]}"; do
        local svc="${services[$i]}"
        local pref="${prefixes[$i]}"

        local enabled_var="${pref}_ENABLED"
        local is_enabled=0
        eval "is_enabled=\${$enabled_var:-0}"

        if [ "$is_enabled" = "1" ]; then
            echo "Stopping enabled service: ${svc}..."
            "${script_dir}/${svc}.sh" stop || true
        else
            echo "Stopping and disabling service: ${svc}..."
            "${script_dir}/${svc}.sh" stop || true
            "${script_dir}/${svc}.sh" disable || true
        fi
    done
}

cmd_restart() {
    local target_service="${1:-}"
    load_env

    local services=("local-chat" "local-embedding" "local-rerank" "local-speech-to-text" "local-text-to-speech" "local-image" "local-router" "local-memory")
    local prefixes=("LCHAT" "LMBD" "LRR" "LSTT" "LTTS" "LIMG" "LROUT" "LMEM")
    local script_dir
    script_dir="$(dirname "$0")"

    if [ -n "$target_service" ]; then
        local idx
        if ! idx="$(match_subservice_index "$target_service")"; then
            echo "Error: Unknown subservice '$target_service'."
            echo "Valid subservices: ${services[*]}"
            exit 1
        fi

        local svc="${services[$idx]}"
        local pref="${prefixes[$idx]}"

        local enabled_var="${pref}_ENABLED"
        local is_enabled=0
        eval "is_enabled=\${$enabled_var:-0}"

        local target_env_file="${SYSTEMD_USER_DIR}/${svc}.env"

        if [ "$is_enabled" = "1" ]; then
            echo "Restarting single enabled subservice: ${svc}..."
            apply_service_overrides "$pref" "$target_env_file"

            "${script_dir}/${svc}.sh" enable
            "${script_dir}/${svc}.sh" restart
        else
            echo "Subservice ${svc} is disabled in configuration (${enabled_var}=0). Stopping and disabling..."
            "${script_dir}/${svc}.sh" stop || true
            "${script_dir}/${svc}.sh" disable || true
        fi
        return 0
    fi

    # 1. Stop and disable all services that are NOT enabled
    for i in "${!services[@]}"; do
        local svc="${services[$i]}"
        local pref="${prefixes[$i]}"

        local enabled_var="${pref}_ENABLED"
        local is_enabled=0
        eval "is_enabled=\${$enabled_var:-0}"

        if [ "$is_enabled" != "1" ]; then
            echo "Stopping and disabling service: ${svc}..."
            "${script_dir}/${svc}.sh" stop || true
            "${script_dir}/${svc}.sh" disable || true
        fi
    done

    # 2. Enable and start/restart all services that ARE enabled
    for i in "${!services[@]}"; do
        local svc="${services[$i]}"
        local pref="${prefixes[$i]}"

        local enabled_var="${pref}_ENABLED"
        local is_enabled=0
        eval "is_enabled=\${$enabled_var:-0}"

        if [ "$is_enabled" = "1" ]; then
            echo "Restarting enabled service: ${svc}..."
            local target_env_file="${SYSTEMD_USER_DIR}/${svc}.env"
            apply_service_overrides "$pref" "$target_env_file"

            "${script_dir}/${svc}.sh" enable
            "${script_dir}/${svc}.sh" restart
        fi
    done
}

cmd_test() {
    load_env

    local services=("local-chat" "local-embedding" "local-rerank" "local-speech-to-text" "local-text-to-speech" "local-image" "local-router" "local-memory")
    local prefixes=("LCHAT" "LMBD" "LRR" "LSTT" "LTTS" "LIMG" "LROUT" "LMEM")
    local script_dir
    script_dir="$(dirname "$0")"

    for i in "${!services[@]}"; do
        local svc="${services[$i]}"
        local pref="${prefixes[$i]}"

        local enabled_var="${pref}_ENABLED"
        local is_enabled=0
        eval "is_enabled=\${$enabled_var:-0}"

        if [ "$is_enabled" = "1" ]; then
            echo "=== Testing enabled service: ${svc} ==="
            local target_env_file="${SYSTEMD_USER_DIR}/${svc}.env"
            apply_service_overrides "$pref" "$target_env_file"

            "${script_dir}/${svc}.sh" test "$@"
            echo ""
        fi
    done
}

cmd_cat() {
    local target_service="${1:-}"
    load_env

    echo "=== Environment File: ${ENV_FILE} ==="
    if [[ -f "${ENV_FILE}" ]]; then
        cat "${ENV_FILE}"
    else
        echo "(Environment file does not exist. Run 'install' to create it.)"
    fi
    echo ""

    local services=("local-chat" "local-embedding" "local-rerank" "local-speech-to-text" "local-text-to-speech" "local-image" "local-router" "local-memory")
    local prefixes=("LCHAT" "LMBD" "LRR" "LSTT" "LTTS" "LIMG" "LROUT" "LMEM")
    local script_dir
    script_dir="$(dirname "$0")"

    if [ -n "$target_service" ]; then
        local idx
        if ! idx="$(match_subservice_index "$target_service")"; then
            echo "Error: Unknown subservice '$target_service'."
            echo "Valid subservices: ${services[*]}"
            exit 1
        fi
        services=("${services[$idx]}")
        prefixes=("${prefixes[$idx]}")
    fi

    for i in "${!services[@]}"; do
        local svc="${services[$i]}"
        local pref="${prefixes[$i]}"

        local enabled_var="${pref}_ENABLED"
        local is_enabled=0
        eval "is_enabled=\${$enabled_var:-0}"

        if [ "$is_enabled" = "1" ] || [ -n "$target_service" ]; then
            echo "=== Subservice Configuration: ${svc} ==="
            local target_env_file="${SYSTEMD_USER_DIR}/${svc}.env"
            apply_service_overrides "$pref" "$target_env_file"

            if [[ -x "${script_dir}/${svc}.sh" ]]; then
                "${script_dir}/${svc}.sh" cat || true
            fi
            echo ""
        fi
    done
}

usage() {
    cat <<EOF
Usage: $0 <command> [args...]
Commands:
  install [--new-config] - Setup coordinator config and install all services
  uninstall             - Uninstall all services
  start [subservice]    - Start all (or target subservice) enabled services and apply overrides
  stop [subservice]     - Stop enabled services, stop and disable disabled ones (or target subservice)
  restart [subservice]  - Apply overrides and restart enabled services (or single target subservice)
  status [subservice]   - View status of all services (or target subservice)
  logs [args...]        - View combined logs of all services
  edit                  - Edit coordinator configuration and restart services
  cat [subservice]      - Print wrapper environment configuration and configuration of enabled services (or target subservice)
  test [args...]        - Run validation tests/benchmarks for all enabled services
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
    start) cmd_start "$@" ;;
    stop) cmd_stop "$@" ;;
    restart) cmd_restart "$@" ;;
    status) cmd_status "$@" ;;
    logs) cmd_logs "$@" ;;
    edit) cmd_edit ;;
    cat) cmd_cat "$@" ;;
    test) cmd_test "$@" ;;
    *)
        echo "Unknown command: $COMMAND"
        usage
        exit 1
        ;;
    esac
}

main "$@"
