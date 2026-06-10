#!/usr/bin/env bash
# local-llm-ggml.sh - Manage local llama-server systemd user service for Chat and Embeddings
#
# Usage: local-llm-ggml.sh <command> [args...]
#
# Manages a systemd user service (local-llm-ggml.service) that runs llama-server
# serving both the Chat/Vision LLM and the Text Embedding model.
#
# Hardware target: AMD Radeon Pro W6800.
#
# ---------------------------------------------------------------------------

set -euo pipefail

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SYSTEMD_USER_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
SERVICE_NAME="local-llm-ggml"
SERVICE_FILE="${SYSTEMD_USER_DIR}/${SERVICE_NAME}.service"
ENV_FILE="${SYSTEMD_USER_DIR}/${SERVICE_NAME}.env"
INI_FILE="${SYSTEMD_USER_DIR}/${SERVICE_NAME}.ini"

# ---------------------------------------------------------------------------
# Load environment
# ---------------------------------------------------------------------------
load_env() {
    # Default parameters
    LLM_PORT=50080
    LLM_HOST=127.0.0.1
    LLM_MODEL=/data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact.gguf
    LLM_ALIAS=qwen3
    LLM_N_CTX=240000
    LLM_PARALLEL=3
    LLM_N_GPU_LAYERS=999
    LLM_THREADS=4
    LLM_MMPROJ_ARGS="--mmproj /data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact-mmproj.gguf"
    LLM_CHAT_TEMPLATE_ARGS="--chat-template-file /data/public/machine-learning/models/vision-text/Qwen3.6-chat_template.jinja"
    LLM_EXTRA_ARGS="--flash-attn on"
    LLM_DEVICE=""

    # Embedding default parameters
    LLM_EMBEDDING_MODEL=/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf
    LLM_EMBEDDING_ALIAS=qwen3-embedding
    LLM_EMBEDDING_N_CTX=8192

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
    echo "EnvironmentFile=-${home_spec}/.config/systemd/user/local-llm-ggml.env"
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
# Generate models-preset INI file from environment variables
# ---------------------------------------------------------------------------
generate_ini_file() {
    load_env

    local ini_content=""

    # Global defaults
    ini_content+="version = 1"$'\n'
    ini_content+=""$'\n'
    ini_content+="[*]"$'\n'
    if [ -n "${LLM_EXTRA_ARGS:-}" ]; then
        local -a extra_args
        eval "extra_args=(${LLM_EXTRA_ARGS})"
        local i=0
        while [ $i -lt ${#extra_args[@]} ]; do
            local arg="${extra_args[$i]}"
            if [[ "$arg" == "--flash-attn" ]]; then
                if [ $((i + 1)) -lt ${#extra_args[@]} ] && [[ ! "${extra_args[$((i + 1))]}" =~ ^-- ]]; then
                    ini_content+="flash-attn = ${extra_args[$((i + 1))]}"$'\n'
                    i=$((i + 2))
                else
                    ini_content+="flash-attn = on"$'\n'
                    i=$((i + 1))
                fi
            else
                i=$((i + 1))
            fi
        done
    fi
    ini_content+="n-gpu-layers = ${LLM_N_GPU_LAYERS:-999}"$'\n'

    # --- LLM section ---
    ini_content+=""$'\n'
    ini_content+="[${LLM_ALIAS:-qwen3}]"$'\n'
    ini_content+="model = ${LLM_MODEL}"$'\n'
    if [[ -n "${LLM_MMPROJ_ARGS:-}" ]]; then
        # Extract mmproj path from "--mmproj /path/to/file"
        local mmproj_path
        mmproj_path="${LLM_MMPROJ_ARGS#--mmproj }"
        ini_content+="mmproj = ${mmproj_path}"$'\n'
    fi
    if [[ -n "${LLM_CHAT_TEMPLATE_ARGS:-}" ]]; then
        # Extract template path from "--chat-template-file /path/to/file"
        local template_path
        template_path="${LLM_CHAT_TEMPLATE_ARGS#--chat-template-file }"
        ini_content+="chat-template-file = ${template_path}"$'\n'
    fi
    ini_content+="ctx-size = ${LLM_N_CTX:-240000}"$'\n'
    ini_content+="parallel = ${LLM_PARALLEL:-3}"$'\n'
    ini_content+="cache-type-k = q4_0"$'\n'
    ini_content+="cache-type-v = q4_0"$'\n'
    ini_content+="batch-size = 2048"$'\n'
    ini_content+="ubatch-size = 1024"$'\n'
    ini_content+="threads = ${LLM_THREADS:-8}"$'\n'

    # Parse model-specific options from LLM_EXTRA_ARGS
    if [ -n "${LLM_EXTRA_ARGS:-}" ]; then
        local -a extra_args
        eval "extra_args=(${LLM_EXTRA_ARGS})"
        local i=0
        while [ $i -lt ${#extra_args[@]} ]; do
            local arg="${extra_args[$i]}"
            if [[ "$arg" =~ ^-- ]] && [[ "$arg" != "--flash-attn" ]]; then
                local key="${arg#--}"
                local val=""
                if [ $((i + 1)) -lt ${#extra_args[@]} ] && [[ ! "${extra_args[$((i + 1))]}" =~ ^-- ]]; then
                    val="${extra_args[$((i + 1))]}"
                    i=$((i + 2))
                else
                    val="true"
                    i=$((i + 1))
                fi
                ini_content+="${key} = ${val}"$'\n'
            else
                i=$((i + 1))
            fi
        done
    fi

    # --- Embedding section (always enabled) ---
    ini_content+=""$'\n'
    ini_content+="[${LLM_EMBEDDING_ALIAS:-qwen3-embedding}]"$'\n'
    ini_content+="model = ${LLM_EMBEDDING_MODEL}"$'\n'
    ini_content+="embedding = true"$'\n'
    ini_content+="pooling = mean"$'\n'
    ini_content+="ctx-size = ${LLM_EMBEDDING_N_CTX:-8192}"$'\n'
    ini_content+="batch-size = ${LLM_EMBEDDING_N_CTX:-8192}"$'\n'
    ini_content+="ubatch-size = ${LLM_EMBEDDING_N_CTX:-8192}"$'\n'

    printf '%s' "$ini_content" >"$INI_FILE"
    chmod 600 "$INI_FILE"
}

# ---------------------------------------------------------------------------
# Embedded service file (heredoc written by install/start/restart)
# ---------------------------------------------------------------------------
generate_service_file() {
    load_env
    generate_ini_file

    local exec_cmd="llama-server \\
    --models-preset ${INI_FILE} \\
    --models-max 2 \\
    --host ${LLM_HOST} \\
    --port ${LLM_PORT}"

    if [[ -n "${LLM_DEVICE:-}" ]]; then
        exec_cmd="${exec_cmd} \\
    --device ${LLM_DEVICE}"
    fi

    cat <<EOF
[Unit]
Description=Local LLM Chat and Embedding Inference Server (llama-server)
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
SyslogIdentifier=local-llm-ggml

[Install]
WantedBy=default.target
EOF
}

# ---------------------------------------------------------------------------
# Embedded default env file (heredoc written by --install)
# ---------------------------------------------------------------------------
generate_env_file() {
    cat <<'EOF'
# local-llm-ggml.env
# ---------------------------------------------------------------------------
# Configuration for the local-llm-ggml.service llama-server instance.
# Serves BOTH chat and embeddings from a single process on one port.
#
# Edit this file to switch models or tune runtime parameters.
# Reload with:  local-llm-ggml.sh restart
# ---------------------------------------------------------------------------

# Port to bind the server to (default: 50080)
LLM_PORT=50080

# Host to bind the server to (127.0.0.1 for local access only)
LLM_HOST=127.0.0.1

# ---------------------------------------------------------------------------
# CHAT/VISION MODEL SETTINGS
# ---------------------------------------------------------------------------
# Path to the chat model file
LLM_MODEL=/data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact.gguf

# Model alias used by client integrations (default: qwen3)
LLM_ALIAS=qwen3

# Context size (default: 240000)
LLM_N_CTX=240000

# Parallel request slots (default: 3)
LLM_PARALLEL=3

# Multimodal projector arguments (optional)
LLM_MMPROJ_ARGS="--mmproj /data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact-mmproj.gguf"

# Chat template file (optional)
LLM_CHAT_TEMPLATE_ARGS="--chat-template-file /data/public/machine-learning/models/vision-text/Qwen3.6-chat_template.jinja"

# ---------------------------------------------------------------------------
# EMBEDDING MODEL SETTINGS
# ---------------------------------------------------------------------------
# Path to the text embedding model file
LLM_EMBEDDING_MODEL=/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf

# Model alias used by client integrations (default: qwen3-embedding)
LLM_EMBEDDING_ALIAS=qwen3-embedding

# Embedding context size (default: 8192)
LLM_EMBEDDING_N_CTX=8192

# ---------------------------------------------------------------------------
# RUNTIME SETTINGS
# ---------------------------------------------------------------------------

# Number of layers to offload to GPU (all=999)
LLM_N_GPU_LAYERS=999
# To run inference on CPU instead of GPU (none=0)
# LLM_N_GPU_LAYERS=0

# GPU/CPU backend device to use (e.g. hip, vulkan, cpu, openblas)
# By default, llama-server automatically selects the best available device.
# To force a specific backend device, uncomment one of the options below:
# LLM_DEVICE="hip"
# LLM_DEVICE="vulkan"
# LLM_DEVICE="cpu"
# LLM_DEVICE="openblas"

# Number of threads to use (default: 4)
# Warning: on a 8 core 16 threads system more than 4 slowed inference down by 40%
LLM_THREADS=4

# Extra arguments to pass to llama-server (default: "--flash-attn auto")
LLM_EXTRA_ARGS="--flash-attn auto"
# eg. to enable speculative decoding (type ngram-simple):
# LLM_EXTRA_ARGS="--flash-attn auto --spec-type ngram-simple --spec-ngram-simple-size-n 6 --spec-ngram-simple-size-m 4"

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
    echo "  INI:     ${INI_FILE}"
    echo ""
    echo "  Edit the env file to select model/mmproj/template, then:"
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

    if [[ -f "${INI_FILE}" ]]; then
        rm -f "${INI_FILE}"
        echo "Removed INI file."
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
    generate_ini_file

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
        local args=(
            --models-preset "${INI_FILE}"
            --models-max 2
            --host "${LLM_HOST}"
            --port "${LLM_PORT}"
        )
        if [[ -n "${LLM_DEVICE:-}" ]]; then
            args+=(--device "${LLM_DEVICE}")
        fi
        systemd-run "${opts[@]}" llama-server "${args[@]}"
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
    echo "Running local-llm-ggml validation tests..."
    load_env

    local host="${LLM_HOST:-127.0.0.1}"
    local port="${LLM_PORT:-50080}"
    local alias="${LLM_ALIAS:-qwen3}"
    local embedding_alias="${LLM_EMBEDDING_ALIAS:-qwen3-embedding}"

    local base_url="http://${host}:${port}"
    echo "Using endpoint base: ${base_url}"

    local benchmark=false
    local only_embeddings=false
    local only_chat=false
    local skip_prefill=false
    local skip_distractor=false
    local repeat=""
    while [ $# -gt 0 ]; do
        case "$1" in
        --benchmark) benchmark=true ;;
        --only-embeddings) only_embeddings=true ;;
        --only-chat) only_chat=true ;;
        --skip-prefill) skip_prefill=true ;;
        --skip-distractor) skip_distractor=true ;;
        --repeat)
            shift
            repeat="$1"
            ;;
        esac
        shift
    done

    if [ "$benchmark" = "true" ]; then
        local context_file
        context_file="/data/public/machine-learning/models/benchmark-context.md"
        if [[ ! -f "$context_file" ]]; then
            context_file="$(dirname "$(dirname "$LLM_MODEL")")/benchmark-context.md"
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

        if [ "$only_embeddings" = "false" ]; then
            # Run chat benchmark
            local skip_prefill_arg=()
            if [ "$skip_prefill" = "true" ]; then
                skip_prefill_arg=(--skip-prefill)
            fi
            local skip_distractor_arg=()
            if [ "$skip_distractor" = "true" ]; then
                skip_distractor_arg=(--skip-distractor)
            fi
            python3 "$(dirname "$0")/../scripts/benchmark-helper.py" \
                --mode llm-chat \
                --url "${base_url}" \
                --model "${alias}" \
                --context "${context_file}" \
                "${repeat_arg[@]}" \
                "${skip_prefill_arg[@]}" \
                "${skip_distractor_arg[@]}"
        fi

        # Run embedding benchmark
        if [ "$only_chat" = "false" ]; then
            if [ "$only_embeddings" = "false" ]; then
                echo "sleeping 10 seconds to cool down gpu..."
                sleep 10
            fi
            python3 "$(dirname "$0")/../scripts/benchmark-helper.py" \
                --mode llm-embed \
                --url "${base_url}" \
                --model "${embedding_alias}" \
                --context "${context_file}" \
                "${repeat_arg[@]}"
        fi

        return 0
    fi

    echo "=== 1. Testing Chat Completion ==="
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

    echo "=== 2. Testing Text Embeddings ==="
    local embed_resp
    embed_resp=$(curl -s -f -X POST "${base_url}/v1/embeddings" \
        -H "Content-Type: application/json" \
        -d "{
          \"model\": \"${embedding_alias}\",
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
  exec      - Run llama-server as a transient systemd user service
  run       - Run a command inside the llama-server environment
  shell     - Spawn an interactive shell in the llama-server environment
  test [--benchmark] [--only-embeddings] [--only-chat] [--skip-prefill] [--skip-distractor] [--repeat XX]
    - Run validation tests or benchmarks
EOF

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
