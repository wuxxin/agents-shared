#!/usr/bin/env bash
# local-text-to-speech.sh - Manage local qwen3-tts systemd user service
#
# Usage: local-text-to-speech.sh <command> [args...]
#
# Manages a systemd user service (local-text-to-speech.service) that runs qwen3-tts-server
# for text-to-speech (TTS) synthesis.
#
#

set -euo pipefail

# Paths

SYSTEMD_USER_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
SERVICE_NAME="local-text-to-speech"
SERVICE_FILE="${SYSTEMD_USER_DIR}/${SERVICE_NAME}.service"
ENV_FILE="${SYSTEMD_USER_DIR}/${SERVICE_NAME}.env"

# Load environment

load_env() {
    # Default parameters
    LTTS_PORT=50095
    LTTS_HOST=127.0.0.1
    LTTS_MODEL=/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf
    LTTS_VOCODER=/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-Tokenizer-12Hz-F16.gguf
    LTTS_THREADS=8
    LTTS_MODE="cpu"
    LTTS_EXTRA_ARGS=""
    LTTS_DEVICE=""

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
    local force_cpu=0
    local low_mem=0
    local transformer_force_cpu=0
    local vocoder_force_cpu=0

    low_mem=0

    case "${LTTS_MODE:-gpu}" in
    "gpu")
        force_cpu=0
        ;;
    "hybrid")
        force_cpu=0
        transformer_force_cpu=1
        ;;
    "cpu")
        force_cpu=1
        ;;
    *)
        force_cpu=0
        ;;
    esac

    echo "Environment=QWEN3_TTS_FORCE_CPU=${force_cpu}"
    echo "Environment=QWEN3_TTS_LOW_MEM=${low_mem}"
    echo "Environment=QWEN3_TTS_TRANSFORMER_FORCE_CPU=${transformer_force_cpu}"
    echo "Environment=QWEN3_TTS_VOCODER_FORCE_CPU=${vocoder_force_cpu}"
    echo "EnvironmentFile=-${home_spec}/.config/systemd/user/local-text-to-speech.env"
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
    # Allow read-write access to home-based paths
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

# Helper to get unified arguments for qwen3-tts-server
get_tts_args() {
    local -n out_args=$1
    out_args=(
        --model "${LTTS_MODEL}"
        --vocoder "${LTTS_VOCODER}"
        --host "${LTTS_HOST}"
        --port "${LTTS_PORT}"
        --threads "${LTTS_THREADS}"
    )

    if [[ -n "${LTTS_DEVICE:-}" ]]; then
        out_args+=(--device "${LTTS_DEVICE}")
    fi

    if [[ -n "${LTTS_EXTRA_ARGS:-}" ]]; then
        local extra_arr=()
        eval "extra_arr=(${LTTS_EXTRA_ARGS})"
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

generate_service_file() {
    load_env

    local force_cpu=0
    local low_mem=0
    local transformer_force_cpu=0
    local vocoder_force_cpu=0

    low_mem=0

    case "${LTTS_MODE:-gpu}" in
    "gpu")
        force_cpu=0
        ;;
    "hybrid")
        force_cpu=0
        transformer_force_cpu=1
        ;;
    "cpu")
        force_cpu=1
        ;;
    *)
        echo "Warning: unknown LTTS_MODE '${LTTS_MODE}', defaulting to gpu" >&2
        force_cpu=0
        ;;
    esac

    local args
    get_tts_args args
    local exec_cmd
    exec_cmd=$(format_exec_start "${QWEN3_TTS_SERVER_BIN:-qwen3-tts-server}" "${args[@]}")

    cat <<EOF
[Unit]
Description=Local Text-to-Speech Synthesis Server (qwen3-tts-server)
Documentation=https://github.com/khimaros/qwen3-tts.cpp
After=network.target

[Service]
Type=simple
$(get_shared_options service)
ExecStart=${exec_cmd}

Restart=on-failure
RestartSec=10s

StandardOutput=journal
StandardError=journal
SyslogIdentifier=local-text-to-speech

[Install]
WantedBy=default.target
EOF
}

# Embedded default env file (heredoc written by install)

generate_env_file() {
    cat <<'EOF'
# local-text-to-speech.env

# Configuration for the local-text-to-speech.service qwen3-tts-server instance.
#
# Edit this file to switch models or tune runtime parameters.
# Reload with:  local-text-to-speech.sh restart


# Port to bind the server to (default: 50095)
LTTS_PORT=50095

# Host to bind the server to (127.0.0.1 for local access only)
LTTS_HOST=127.0.0.1

# Path to the GGUF Talker model file
LTTS_MODEL=/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf

# Path to the GGUF Tokenizer/Vocoder model file
LTTS_VOCODER=/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-Tokenizer-12Hz-F16.gguf

# Performance mode preset:
#   - gpu                : Runs on GPU, holds models warm (fastest)
#   - hybrid             : Runs Code Gen on CPU, Vocoder on GPU (performance sweet spot)
#   - cpu                : Forces cpu execution via GGML backends
LTTS_MODE="cpu"

# GPU/CPU backend device to use (run 'llama-cli --list-devices' for valid names)
# By default, qwen3-tts-server selects the default available backend.
# To force a specific backend device, uncomment one of the options below:
# LTTS_DEVICE="ROCm0"
# LTTS_DEVICE="Vulkan0"
# LTTS_DEVICE="BLAS"  # Force CPU OpenBLAS acceleration
# LTTS_DEVICE="none"  # Force plain CPU execution (without OpenBLAS)

# Number of threads to use for computations
LTTS_THREADS=8

# Extra arguments to pass to qwen3-tts-server (e.g. --temperature, --seed, etc.)
# set default language for generation, if not supplied by request: only available in patched (libggml-git-hip) qwen3-tts
# eg. "--language de"
LTTS_EXTRA_ARGS="--language de"

EOF
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

export_tts_env_vars() {
    local force_cpu=0
    local low_mem=0
    local transformer_force_cpu=0
    local vocoder_force_cpu=0
    case "${LTTS_MODE:-gpu}" in
    "gpu")
        force_cpu=0
        low_mem=0
        ;;
    "gpu-min-vram")
        force_cpu=0
        low_mem=1
        ;;
    "hybrid")
        force_cpu=0
        low_mem=0
        transformer_force_cpu=1
        ;;
    "cpu")
        force_cpu=1
        low_mem=0
        ;;
    *)
        force_cpu=0
        low_mem=0
        ;;
    esac

    export QWEN3_TTS_FORCE_CPU="${force_cpu}"
    export QWEN3_TTS_LOW_MEM="${low_mem}"
    export QWEN3_TTS_TRANSFORMER_FORCE_CPU="${transformer_force_cpu}"
    export QWEN3_TTS_VOCODER_FORCE_CPU="${vocoder_force_cpu}"
}

cmd_exec() {
    parse_env_args "$@"
    set -- "${COMMAND_ARGS[@]}"

    export_tts_env_vars

    local args
    get_tts_args args

    if ! is_systemd_running; then
        echo "Warning: Systemd is not running. Running qwen3-tts-server directly in foreground..."
        if [ $# -gt 0 ]; then
            exec "${QWEN3_TTS_SERVER_BIN:-qwen3-tts-server}" "$@"
        else
            exec "${QWEN3_TTS_SERVER_BIN:-qwen3-tts-server}" "${args[@]}"
        fi
    fi

    echo "Starting qwen3-tts-server as a transient systemd service with args: $*"

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
        systemd-run "${opts[@]}" "${SETENV_OPTS[@]}" "${QWEN3_TTS_SERVER_BIN:-qwen3-tts-server}" "$@"
    else
        systemd-run "${opts[@]}" "${SETENV_OPTS[@]}" "${QWEN3_TTS_SERVER_BIN:-qwen3-tts-server}" "${args[@]}"
    fi
}

cmd_shell() {
    echo "Starting interactive shell in the qwen3-tts-server systemd environment..."

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
    echo "Running command inside the qwen3-tts-server environment: $*"

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
    echo "Running local-text-to-speech validation tests..."
    load_env

    local play=false
    local benchmark=false
    local repeat=""
    local extra_args=()
    while [ $# -gt 0 ]; do
        case "$1" in
        --play) play=true ;;
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

    local host="${LTTS_HOST:-127.0.0.1}"
    local port="${LTTS_PORT:-50095}"

    if [ "$benchmark" = "true" ]; then
        local repeat_arg=()
        if [ -n "$repeat" ]; then
            repeat_arg=(--repeat "$repeat")
        fi

        # Run TTS benchmark
        python3 "$(dirname "$0")/../scripts/benchmark-helper.py" \
            --mode tts \
            --url "http://${host}:${port}" \
            --model "qwen3-tts" \
            --output-dir "$(dirname "$0")/../scratch" \
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

    # Create a test sentence of 9 words
    local text="The quick brown fox jumps over the lazy dog."
    echo "Synthesizing test sentence (9 words):"
    echo "  \"${text}\""
    echo "Sending request to http://${host}:${port}/v1/audio/speech..."

    if ! curl -s -f -X POST "http://${host}:${port}/v1/audio/speech" \
        -H "Content-Type: application/json" \
        -d "{
          \"model\": \"qwen3-tts\",
          \"input\": \"${text}\",
          \"voice\": \"serena\",
          \"response_format\": \"wav\"
        }" \
        -o "$temp_dir/tts_output.wav"; then
        echo "Error: Failed to synthesize speech via local-text-to-speech." >&2
        trap - EXIT
        cleanup
        return 1
    fi

    echo "Synthesis complete. File size: $(wc -c <"$temp_dir/tts_output.wav") bytes."
    cp "$temp_dir/tts_output.wav" "/tmp/tts_test_output.wav"
    echo "Saved output to /tmp/tts_test_output.wav"

    # Pipe through local-speech-to-text
    local lstt_env_file="${SYSTEMD_USER_DIR:-$HOME/.config}/systemd/user/local-speech-to-text.env"
    if [[ -f "$lstt_env_file" ]]; then
        # shellcheck disable=SC1090
        source "$lstt_env_file" || true
    fi
    local lstt_host="${LSTT_HOST:-127.0.0.1}"
    local lstt_port="${LSTT_PORT:-50090}"
    local lstt_inference_path="${LSTT_INFERENCE_PATH:-/v1/audio/transcriptions}"
    local lstt_model_alias="${LSTT_ALIAS:-whisper-1}"

    echo "Transcribing generated audio using local-speech-to-text at http://${lstt_host}:${lstt_port}..."
    local stt_resp
    if ! stt_resp=$(curl -s -f -X POST "http://${lstt_host}:${lstt_port}${lstt_inference_path}" \
        -H "Content-Type: multipart/form-data" \
        -F "file=@$temp_dir/tts_output.wav" \
        -F "model=${lstt_model_alias}"); then
        echo "Error: Speech-to-text transcription service failed or is unreachable." >&2
        trap - EXIT
        cleanup
        return 1
    fi

    echo "Transcription Response:"
    echo "${stt_resp}"

    if [ "$play" = "true" ]; then
        # Try playing the audio output
        echo "Playing generated audio output..."
        if command -v aplay &>/dev/null; then
            aplay "$temp_dir/tts_output.wav" || true
        elif command -v paplay &>/dev/null; then
            paplay "$temp_dir/tts_output.wav" || true
        elif command -v pw-play &>/dev/null; then
            pw-play "$temp_dir/tts_output.wav" || true
        else
            echo "No command-line audio player (aplay, paplay, pw-play) found. Skipping audio playback."
        fi
    else
        echo "Skipping audio playback (use --play to play generated sound)."
    fi

    echo "Local text-to-speech validation: Success."
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
    echo "  exec      - Run qwen3-tts-server as a transient systemd user service"
    echo "  run       - Run a command inside the qwen3-tts-server environment"
    echo "  shell     - Spawn an interactive shell in the qwen3-tts-server environment"
    echo "  cat       - Print service file, environment configuration, and transient exec command"
    echo "  test [--play] [--benchmark] - Run synthesis and validation tests or benchmark"
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
    get_tts_args args
    echo "${QWEN3_TTS_SERVER_BIN:-qwen3-tts-server} ${args[*]}"
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
