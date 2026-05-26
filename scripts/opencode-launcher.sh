#!/usr/bin/env bash
# OpenCode Sandbox Launcher
set -euo pipefail

# Configuration Constants
APP_BIN="opencode"
PERSISTENT_HOME="$HOME/.local/sandbox/opencode"
WORK_DIR="$HOME/agent-private/opencode"
DEFAULT_PROJECT="$WORK_DIR/default"
AGENT_SHARED_DIR="$HOME/agent-shared"
DOWNLOAD_DIR="/data/download"

# Default flags for Electron/OpenCode
ELECTRON_FLAGS=(
    --disable-dev-shm-usage
    --disable-chromium-sandbox
    --no-sandbox
)
OPENCODE_FLAGS=()

# Helper: Display launcher help information
show_help() {
    cat <<EOF
OpenCode Sandbox Launcher Help
------------------------------
Usage when called as $(basename "$0"):
  $0 install          - Install launcher, symlinks, and initialize directories
  $0 uninstall        - Remove launcher script and symlink from ~/.local/bin
  $0 help             - Display this help message
  $0 exec <cmd> [args] - Run custom command inside the Bubblewrap sandbox
  $0 shell            - Spawn an interactive shell inside the Bubblewrap sandbox
EOF
}

# Helper: Initialize the sandbox directory structure
initialize_sandbox() {
    mkdir -p "$PERSISTENT_HOME" "$WORK_DIR" "$DEFAULT_PROJECT"
    mkdir -p "$PERSISTENT_HOME/$(realpath --relative-to="$HOME" "$WORK_DIR")"
    mkdir -p "$PERSISTENT_HOME/$(realpath --relative-to="$HOME" "$AGENT_SHARED_DIR")"

    # Create symlink for ~/download to $DOWNLOAD_DIR
    local download_symlink="$PERSISTENT_HOME/download"
    if [[ ! -L "$download_symlink" ]]; then
        if [[ -e "$download_symlink" ]]; then
            rm -f "$download_symlink"
        fi
        ln -s "$DOWNLOAD_DIR" "$download_symlink"
    fi

    # Create .git for default project if not existing
    if [[ ! -d "$DEFAULT_PROJECT/.git" ]]; then
        git -C "$DEFAULT_PROJECT" init
    fi
}

# Helper: Install launcher script and symlink
install_launcher() {
    local bin_dir="$HOME/.local/bin"
    local script_target="$bin_dir/opencode-launcher.sh"
    local symlink_target="$bin_dir/opencode"

    echo "Installing OpenCode Sandbox Launcher..."

    # Ensure bin directory exists
    mkdir -p "$bin_dir"

    # Initialize sandbox directories
    initialize_sandbox

    # Copy script to user local bin
    local current_script
    current_script="$(realpath "$0")"

    if [[ "$current_script" != "$(realpath "$script_target" 2>/dev/null)" ]]; then
        echo "Copying script to $script_target..."
        cp "$current_script" "$script_target"
        chmod +x "$script_target"
    else
        echo "Script is already running from target path."
    fi

    # Create symlink using relative path to avoid breaking if target is moved
    echo "Creating symlink $symlink_target -> opencode-launcher.sh..."
    ln -sf "opencode-launcher.sh" "$symlink_target"

    echo "Installation complete!"
    echo "Sandbox home directory: $PERSISTENT_HOME"
}

# Helper: Uninstall launcher files
uninstall_launcher() {
    local bin_dir="$HOME/.local/bin"
    local script_target="$bin_dir/opencode-launcher.sh"
    local symlink_target="$bin_dir/opencode"

    echo "Uninstalling OpenCode Sandbox Launcher..."

    if [[ -f "$script_target" ]]; then
        rm -f "$script_target"
        echo "Removed launcher script: $script_target"
    fi

    if [[ -L "$symlink_target" || -e "$symlink_target" ]]; then
        rm -f "$symlink_target"
        echo "Removed symlink: $symlink_target"
    fi

    echo "Uninstallation complete!"
    echo "Persistent sandbox directory '$PERSISTENT_HOME' was NOT deleted to prevent data loss."
    echo "You can remove it manually if you wish: rm -rf '$PERSISTENT_HOME'"
}

# Helper: Run bubblewrap sandbox
run_sandbox() {
    # Ensure bubblewrap is installed on the host
    if ! command -v bwrap >/dev/null 2>&1; then
        echo "Error: bubblewrap (bwrap) is not installed or not in PATH." >&2
        exit 1
    fi

    # Initialize sandbox directories if missing
    initialize_sandbox

    # Prepare basic bubblewrap argument list
    local display="${DISPLAY:-}"
    local xauthority="${XAUTHORITY:-}"
    local xdg_runtime_dir="${XDG_RUNTIME_DIR:-}"

    local bwrap_args=(
        --unshare-all
        --share-net
        --die-with-parent
        --new-session
        --cap-add CAP_SYS_PTRACE
        --ro-bind / /
        --tmpfs /tmp
        --dev-bind /dev /dev
        --ro-bind /sys /sys
        --proc /proc
        --bind "$PERSISTENT_HOME" "$HOME"
        --bind "$WORK_DIR" "$WORK_DIR"
        --bind "$AGENT_SHARED_DIR" "$AGENT_SHARED_DIR"
        --ro-bind /tmp/.X11-unix /tmp/.X11-unix
        --setenv DISPLAY "$display"
        --setenv XAUTHORITY "$xauthority"
        --chdir "$WORK_DIR"
    )

    # Wayland Support
    if [[ -n "$xdg_runtime_dir" ]]; then
        bwrap_args+=(
            --bind "$xdg_runtime_dir" "$xdg_runtime_dir"
            --setenv XDG_RUNTIME_DIR "$xdg_runtime_dir"
        )
    fi

    exec bwrap "${bwrap_args[@]}" "$@"
}

# MAIN LOGIC - Route based on calling command name
cmd_name=$(basename "$0")

if [[ "$cmd_name" == "opencode" ]]; then
    # Smart calling mode: wrap args and run sandboxed opencode
    # Filter empty arguments
    args=()
    for arg in "$@"; do
        if [[ -n "$arg" ]]; then
            args+=("$arg")
        fi
    done

    if [[ ${#args[@]} -eq 0 ]]; then
        run_sandbox "$APP_BIN" "${ELECTRON_FLAGS[@]}" "${OPENCODE_FLAGS[@]}" "$DEFAULT_PROJECT"
    else
        run_sandbox "$APP_BIN" "${ELECTRON_FLAGS[@]}" "${OPENCODE_FLAGS[@]}" "${args[@]}"
    fi
else
    # Called as opencode-launcher.sh (or other controls)
    if [[ $# -lt 1 ]]; then
        show_help
        exit 1
    fi

    cmd="$1"
    shift

    case "$cmd" in
    install)
        install_launcher
        ;;
    uninstall)
        uninstall_launcher
        ;;
    help)
        show_help
        ;;
    exec)
        if [[ $# -lt 1 ]]; then
            echo "Error: exec requires a command to run." >&2
            exit 1
        fi
        run_sandbox "$@"
        ;;
    shell)
        run_sandbox "${SHELL:-/bin/bash}" "$@"
        ;;
    *)
        echo "Unknown command: $cmd" >&2
        show_help >&2
        exit 1
        ;;
    esac
fi
