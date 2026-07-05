#!/usr/bin/env bash
# local-speech-to-text.sh - Manage local whisper-server systemd user service
#
# Usage: local-speech-to-text.sh <command> [args...]
#
# Manages a systemd user service (local-speech-to-text.service) that runs whisper-server
# for speech-to-text (STT) transcription.
#
#

set -euo pipefail

# Paths

SYSTEMD_USER_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
SERVICE_NAME="local-speech-to-text"
SERVICE_FILE="${SYSTEMD_USER_DIR}/${SERVICE_NAME}.service"
ENV_FILE="${SYSTEMD_USER_DIR}/${SERVICE_NAME}.env"

# Load environment

load_env() {
    # Default parameters
    LSTT_PORT=50090
    LSTT_HOST=127.0.0.1
    LSTT_MODEL=/data/public/machine-learning/models/speech-to-text/ggml-large-v3-turbo-q5_0.bin
    # shellcheck disable=SC2034
    LSTT_MODEL_ALIAS=whisper-1
    LSTT_THREADS=8
    LSTT_LANG=auto
    LSTT_DEVICE=""
    LSTT_NO_GPU=false
    LSTT_INFERENCE_PATH=/v1/audio/transcriptions
    LSTT_EXTRA_ARGS=""

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
    if [[ -n "${CUDA_VISIBLE_DEVICES+x}" ]]; then
        export CUDA_VISIBLE_DEVICES
    fi

    # Export any GGML_ variables so that child processes see them
    local var
    for var in $(compgen -v | grep ^GGML_); do
        export "${var?}"
    done
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
    echo "EnvironmentFile=-${home_spec}/.config/systemd/user/local-speech-to-text.env"
    echo "WorkingDirectory=${home_spec}"

    # Basic hardening (kept minimal for GPU access)
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
    # Allow read-write access to home-based paths (for temp ffmpeg files)
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

# Helper to get unified arguments for whisper-server
get_whisper_args() {
    local -n out_args=$1
    out_args=(
        --model "${LSTT_MODEL}"
        --host "${LSTT_HOST}"
        --port "${LSTT_PORT}"
        --threads "${LSTT_THREADS}"
        --inference-path "${LSTT_INFERENCE_PATH}"
        --convert
        --flash-attn
    )

    if [[ -n "${LSTT_LANG:-}" ]]; then
        out_args+=(--language "${LSTT_LANG}")
    fi

    if [[ -n "${LSTT_DEVICE:-}" ]]; then
        out_args+=(--device "${LSTT_DEVICE}")
    fi

    if [ "${LSTT_NO_GPU:-}" = "true" ] || [ "${LSTT_NO_GPU:-}" = "1" ]; then
        out_args+=(--no-gpu)
    fi

    if [[ -n "${LSTT_EXTRA_ARGS:-}" ]]; then
        local extra_arr=()
        eval "extra_arr=(${LSTT_EXTRA_ARGS})"
        out_args+=("${extra_arr[@]}")
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

# Embedded service file (heredoc written by install/start/restart)

generate_service_file() {
    load_env
    local args
    get_whisper_args args
    local exec_cmd
    exec_cmd=$(format_exec_start "${WHISPER_SERVER_BIN:-whisper-server}" "${args[@]}")

    cat <<EOF
[Unit]
Description=Local Speech-to-Text Transcription Server (whisper-server)
Documentation=https://github.com/ggerganov/whisper.cpp
After=network.target

[Service]
Type=simple
$(get_shared_options service)
ExecStart=${exec_cmd}

Restart=on-failure
RestartSec=10s

StandardOutput=journal
StandardError=journal
SyslogIdentifier=local-speech-to-text

[Install]
WantedBy=default.target
EOF
}

# Embedded default env file (heredoc written by --install)

generate_env_file() {
    cat <<'EOF'
# local-speech-to-text.env

# Configuration for the local-speech-to-text.service whisper-server instance.
#
# Edit this file to switch models or tune runtime parameters.
# Reload with:  local-speech-to-text.sh restart


# Port to bind the server to (default: 50090)
LSTT_PORT=50090

# Host to bind the server to (127.0.0.1 for local access only)
LSTT_HOST=127.0.0.1

# Path to the GGML Whisper model file
# Source: https://huggingface.co/ggerganov/whisper.cpp/blob/main/ggml-large-v3-turbo-q5_0.bin
LSTT_MODEL=/data/public/machine-learning/models/speech-to-text/ggml-large-v3-turbo-q5_0.bin

# Model alias used by client integrations (default: whisper-1)
LSTT_MODEL_ALIAS="whisper-1"

# Number of threads to use for CPU-bound computations/preprocessing
LSTT_THREADS=8

# Spoken language ('auto' for auto-detect, or language code like 'en', 'de', 'fr')
LSTT_LANG="auto"

# GPU device ID to use (e.g. 0, 1, etc.)
# By default, whisper-server automatically selects the best available GPU device.
# To force a specific GPU, uncomment the option below and specify the integer device ID:
# LSTT_DEVICE="0"

# To run inference on CPU instead of GPU, uncomment the following line:
# (This automatically utilizes the best CPU/BLAS backend available)
# LSTT_NO_GPU=true

# Inference API endpoint path (default: /v1/audio/transcriptions for OpenAI-compatibility)
LSTT_INFERENCE_PATH=/v1/audio/transcriptions

# Extra arguments to pass to whisper-server (e.g. VAD options, diarization, etc.)
LSTT_EXTRA_ARGS=""

EOF
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
    echo "  Edit the env file to select models, then:"
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

    local args
    get_whisper_args args

    if ! is_systemd_running; then
        echo "Warning: Systemd is not running. Running whisper-server directly in foreground..."
        if [ $# -gt 0 ]; then
            exec "${WHISPER_SERVER_BIN:-whisper-server}" "$@"
        else
            exec "${WHISPER_SERVER_BIN:-whisper-server}" "${args[@]}"
        fi
    fi

    echo "Starting whisper-server as a transient systemd service with args: $*"

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
        systemd-run "${opts[@]}" "${SETENV_OPTS[@]}" "${WHISPER_SERVER_BIN:-whisper-server}" "$@"
    else
        systemd-run "${opts[@]}" "${SETENV_OPTS[@]}" "${WHISPER_SERVER_BIN:-whisper-server}" "${args[@]}"
    fi
}

cmd_shell() {
    echo "Starting interactive shell in the whisper-server systemd environment..."

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
    echo "Running command inside the whisper-server environment: $*"

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
    echo "Running local-speech-to-text validation tests..."
    load_env

    # Apply defaults if values are not set
    local host="${LSTT_HOST:-127.0.0.1}"
    local port="${LSTT_PORT:-50090}"
    local inference_path="${LSTT_INFERENCE_PATH:-/v1/audio/transcriptions}"
    local model_alias="${LSTT_MODEL_ALIAS:-whisper-1}"

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
        local audio_file
        audio_file="$(dirname "$LSTT_MODEL")/speech-to-text.ogg"
        if [[ ! -f "$audio_file" ]]; then
            audio_file="/tmp/speech-to-text.ogg"
            if [[ ! -f "$audio_file" ]]; then
                echo "Downloading speech-to-text.ogg to ${audio_file}..."
                if ! curl -L -f -o "$audio_file" "https://upload.wikimedia.org/wikipedia/commons/2/23/William_McKinley_campaign_speech_1896.ogg"; then
                    echo "Error: Failed to download validation audio sample." >&2
                    return 1
                fi
            fi
        fi

        local repeat_arg=()
        if [ -n "$repeat" ]; then
            repeat_arg=(--repeat "$repeat")
        fi

        # Run STT benchmark
        python3 "$(dirname "$0")/../scripts/benchmark-helper.py" \
            --mode stt \
            --url "http://${host}:${port}" \
            --model "${model_alias}" \
            --audio "${audio_file}" \
            "${repeat_arg[@]}" \
            "${extra_args[@]}"
        return 0
    fi

    local temp_dir
    temp_dir=$(mktemp -d)
    cleanup() {
        rm -rf "$temp_dir"
    }
    trap cleanup EXIT

    echo "Downloading jfk.wav audio sample..."
    if ! curl -L -f -o "$temp_dir/jfk.wav" "https://github.com/ggerganov/whisper.cpp/raw/master/samples/jfk.wav"; then
        echo "Error: Failed to download jfk.wav sample audio." >&2
        trap - EXIT
        cleanup
        return 1
    fi

    echo "Sending transcription request to http://${host}:${port}${inference_path}..."
    local resp
    if ! resp=$(curl -s -f -X POST "http://${host}:${port}${inference_path}" \
        -H "Content-Type: multipart/form-data" \
        -F "file=@$temp_dir/jfk.wav" \
        -F "model=${model_alias}"); then
        echo "Error: Transcription curl request failed." >&2
        trap - EXIT
        cleanup
        return 1
    fi

    echo "${resp}"
    # Validate transcription response text contains key words
    if ! echo "${resp}" | grep -qi -E "(Americans|country|fellow)"; then
        echo "Error: Speech-to-text transcription verification failed." >&2
        trap - EXIT
        cleanup
        return 1
    fi

    echo "Speech-to-text validation: Success."
    trap - EXIT
    cleanup
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
    echo "  exec      - Run whisper-server as a transient systemd user service"
    echo "  run       - Run a command inside the whisper-server environment"
    echo "  shell     - Spawn an interactive shell in the whisper-server environment"
    echo "  test [--benchmark] - Run validation tests or speech-to-text benchmark"
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
