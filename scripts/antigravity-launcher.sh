#!/usr/bin/env bash
# Antigravity Sandbox - Persistent Home Edition
set -euo pipefail

# Configuration Constants
APP_BIN="/opt/Antigravity/antigravity"
PERSISTENT_HOME="$HOME/.local/sandbox/antigravity"
WORK_DIR="$HOME/agent-private/antigravity"
DEFAULT_PROJECT="$WORK_DIR/default"
AGENT_SHARED_DIR="$HOME/agent-shared"
DOWNLOAD_DIR="/data/download"
ENV_FILE="$HOME/.local/sandbox/antigravity.env"

# Helper: Check if a path is under (or matches) a parent directory
is_under() {
    local path="$1"
    local parent="$2"
    path="${path%/}"
    parent="${parent%/}"
    [[ "$path" == "$parent" || "$path" == "$parent"/* ]]
}

# Helper: Translate host path to sandbox-internal path
translate_path() {
    local host_path="$1"
    if [[ "$host_path" == "$PERSISTENT_HOME" ]]; then
        echo "$HOME"
    elif [[ "$host_path" == "$PERSISTENT_HOME"/* ]]; then
        echo "$HOME/${host_path#"$PERSISTENT_HOME"/}"
    else
        echo "$host_path"
    fi
}

# Default flags
ANTIGRAVITY_FLAGS=()
ELECTRON_FLAGS=(
    --disable-dev-shm-usage
    --disable-chromium-sandbox
    --no-sandbox
)

# Helper: Display launcher help information
show_help() {
    cat <<EOF
Antigravity Sandbox Launcher Help
---------------------------------
Usage when called as $(basename "$0"):
  $0 install [--new-config] - Install launcher, symlink, desktop entries (overwrites config if --new-config is specified)
  $0 uninstall        - Remove launcher, symlink, and desktop entries
  $0 env              - Edit environment configuration file
  $0 help             - Display this help message
  $0 exec [args]      - Run the sandboxed Antigravity application with optional args
  $0 run <cmd> [args] - Run custom command inside the Bubblewrap sandbox
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

# Helper: Install script, symlink, and desktop configurations
install_launcher() {
    local new_config=false
    while [[ $# -gt 0 ]]; do
        case "$1" in
        --new-config) new_config=true ;;
        esac
        shift
    done

    local bin_dir="$HOME/.local/bin"
    local app_dir="$HOME/.local/share/applications"
    local script_target="$bin_dir/antigravity-launcher.sh"
    local symlink_target="$bin_dir/antigravity"

    echo "Installing Antigravity Sandbox Launcher..."

    # Ensure directories exist
    mkdir -p "$bin_dir"
    mkdir -p "$app_dir"

    # Initialize sandbox directories
    initialize_sandbox

    # Write env file only if it doesn't exist (preserve user edits)
    if [[ -f "$ENV_FILE" ]] && [[ "$new_config" == "false" ]]; then
        echo "Warning: Env file already exists, skipping: $ENV_FILE"
        echo "Remove it manually or use --new-config if you want to regenerate the defaults."
    else
        echo "Creating environment file at $ENV_FILE..."
        mkdir -p "$(dirname "$ENV_FILE")"
        cat >"$ENV_FILE" <<EOF
# env configuration for antigravity
# This file is loaded by the sandbox launcher.

# Hardening / feature flags (set to 1 to disable):
# DISABLE_XDG_RUNTIME=1
# DISABLE_SSH_AUTH=1
# DISABLE_WAYLAND=1
# DISABLE_AUDIO=1
# DISABLE_DBUS=1

# Custom binds (colon-separated list of absolute paths):
# SANDBOX_BIND_PATHS=""
EOF
        chmod 600 "$ENV_FILE"
    fi

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

    # Create symlink using relative path to be robust
    echo "Creating symlink $symlink_target -> antigravity-launcher.sh..."
    ln -sf "antigravity-launcher.sh" "$symlink_target"

    # Write desktop files using symlink target absolute path
    echo "Installing desktop entries..."
    cat <<EOF >"$app_dir/antigravity.desktop"
[Desktop Entry]
Type=Application
Name=Antigravity(Sb)
GenericName=Code Editor
Comment=Agentic development platform (Sandboxed)
Exec=$symlink_target %F
TryExec=$symlink_target
Icon=antigravity
Terminal=false
Categories=Development;IDE;TextEditor;
Keywords=vscode;ide;editor;
StartupNotify=true
StartupWMClass=Antigravity
MimeType=application/x-antigravity-workspace;
Actions=new-empty-window;

[Desktop Action new-empty-window]
Name=New Empty Window
Exec=$symlink_target --new-window %F
Icon=antigravity
EOF

    cat <<EOF >"$app_dir/antigravity-url-handler.desktop"
[Desktop Entry]
Type=Application
Name=Antigravity(SB) - URL Handler
Comment=Handle antigravity:// URLs
Exec=$symlink_target --open-url %U
Icon=antigravity
Terminal=false
NoDisplay=true
Categories=Development;
MimeType=x-scheme-handler/antigravity;
StartupNotify=true
EOF

    echo "Installation complete!"
    echo "Sandbox home directory: $PERSISTENT_HOME"
}

# Helper: Uninstall script, symlink, and desktop configurations
uninstall_launcher() {
    local bin_dir="$HOME/.local/bin"
    local app_dir="$HOME/.local/share/applications"
    local script_target="$bin_dir/antigravity-launcher.sh"
    local symlink_target="$bin_dir/antigravity"

    echo "Uninstalling Antigravity Sandbox Launcher..."

    if [[ -f "$script_target" ]]; then
        rm -f "$script_target"
        echo "Removed launcher script: $script_target"
    fi

    if [[ -L "$symlink_target" || -e "$symlink_target" ]]; then
        rm -f "$symlink_target"
        echo "Removed symlink: $symlink_target"
    fi

    if [[ -f "$app_dir/antigravity.desktop" ]]; then
        rm -f "$app_dir/antigravity.desktop"
        echo "Removed desktop entry: $app_dir/antigravity.desktop"
    fi

    if [[ -f "$app_dir/antigravity-url-handler.desktop" ]]; then
        rm -f "$app_dir/antigravity-url-handler.desktop"
        echo "Removed desktop entry: $app_dir/antigravity-url-handler.desktop"
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

    # Load environment file if it exists
    if [[ -f "$ENV_FILE" ]]; then
        set +u
        set -a
        # shellcheck disable=SC1090
        source "$ENV_FILE"
        set +a
        set -u
    fi

    # Check if current working directory is within target mounts
    local cwd
    cwd="$(pwd)"
    local is_allowed=false

    if is_under "$cwd" "$PERSISTENT_HOME" || is_under "$cwd" "$WORK_DIR" || is_under "$cwd" "$AGENT_SHARED_DIR"; then
        is_allowed=true
    fi

    # Check custom bind paths
    if [[ "$is_allowed" == "false" && -n "${SANDBOX_BIND_PATHS:-}" ]]; then
        IFS=':' read -ra paths <<<"$SANDBOX_BIND_PATHS"
        for p in "${paths[@]}"; do
            if [[ -n "$p" ]] && is_under "$cwd" "$p"; then
                is_allowed=true
                break
            fi
        done
    fi

    if [[ "$is_allowed" == "false" ]]; then
        echo "Warning: Current working directory '$cwd' is outside the sandbox target mounts." >&2
        echo "This will likely cause bubblewrap (bwrap) to fail." >&2
    fi

    # Prepare basic bubblewrap argument list
    local display="${DISPLAY:-}"
    local xauthority="${XAUTHORITY:-}"
    local xdg_runtime_dir="${XDG_RUNTIME_DIR:-}"
    local ssh_auth_sock="${SSH_AUTH_SOCK:-}"

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
    )

    # Wayland & Audio Support (Selective mounting of XDG_RUNTIME_DIR)
    local enable_xdg_runtime=true
    if [[ "${DISABLE_XDG_RUNTIME:-}" == "1" || "${DISABLE_XDG_RUNTIME:-}" == "true" ]]; then
        enable_xdg_runtime=false
    fi

    if [[ "$enable_xdg_runtime" == "true" && -n "$xdg_runtime_dir" && -d "$xdg_runtime_dir" ]]; then
        bwrap_args+=(
            --tmpfs "$xdg_runtime_dir"
            --setenv XDG_RUNTIME_DIR "$xdg_runtime_dir"
        )

        local whitelist=()

        # Feature: Wayland
        local enable_wayland=true
        if [[ "${DISABLE_WAYLAND:-}" == "1" || "${DISABLE_WAYLAND:-}" == "true" ]]; then
            enable_wayland=false
        fi
        if [[ "$enable_wayland" == "true" ]]; then
            if [[ -n "${WAYLAND_DISPLAY:-}" ]]; then
                whitelist+=("$WAYLAND_DISPLAY" "$WAYLAND_DISPLAY.lock")
            else
                whitelist+=("wayland-0" "wayland-0.lock")
            fi

            # Include Xwayland/Mutter authentication files if present on the host
            local old_nullglob
            old_nullglob=$(shopt -p nullglob || true)
            shopt -s nullglob
            for auth_file in "$xdg_runtime_dir"/.mutter-Xwaylandauth*; do
                whitelist+=("$(basename "$auth_file")")
            done
            eval "$old_nullglob"
        fi

        # Feature: Audio (Pipewire & PulseAudio)
        local enable_audio=true
        if [[ "${DISABLE_AUDIO:-}" == "1" || "${DISABLE_AUDIO:-}" == "true" ]]; then
            enable_audio=false
        fi
        if [[ "$enable_audio" == "true" ]]; then
            whitelist+=("pipewire-0" "pipewire-0.lock" "pipewire-0-manager" "pipewire-0-manager.lock" "pulse")
        fi

        # Feature: DBus session bus
        local enable_dbus=true
        if [[ "${DISABLE_DBUS:-}" == "1" || "${DISABLE_DBUS:-}" == "true" ]]; then
            enable_dbus=false
        fi
        if [[ "$enable_dbus" == "true" ]]; then
            whitelist+=("bus")
        fi

        # Bind whitelisted items that exist on the host
        for item in "${whitelist[@]}"; do
            local host_path="$xdg_runtime_dir/$item"
            if [[ -e "$host_path" ]]; then
                bwrap_args+=(--bind "$host_path" "$host_path")
            fi
        done
    fi

    # Audio socket fallback or PulseAudio support outside XDG_RUNTIME_DIR
    if [[ "$enable_xdg_runtime" == "true" && "${enable_audio:-true}" == "true" && -d "/run/user/$(id -u)/pulse" ]]; then
        bwrap_args+=(--bind "/run/user/$(id -u)/pulse" "/run/user/$(id -u)/pulse")
    fi

    # SSH Agent Support
    local enable_ssh_auth=true
    if [[ "${DISABLE_SSH_AUTH:-}" == "1" || "${DISABLE_SSH_AUTH:-}" == "true" ]]; then
        enable_ssh_auth=false
    fi

    if [[ "$enable_ssh_auth" == "true" && -n "$ssh_auth_sock" && -S "$ssh_auth_sock" ]]; then
        bwrap_args+=(
            --bind "$ssh_auth_sock" "$ssh_auth_sock"
            --setenv SSH_AUTH_SOCK "$ssh_auth_sock"
        )
    fi

    # Custom bindings via SANDBOX_BIND_PATHS
    if [[ -n "${SANDBOX_BIND_PATHS:-}" ]]; then
        IFS=':' read -ra paths <<<"$SANDBOX_BIND_PATHS"
        for p in "${paths[@]}"; do
            if [[ -d "$p" ]]; then
                bwrap_args+=(--bind "$p" "$p")
            elif [[ -f "$p" ]]; then
                bwrap_args+=(--bind "$p" "$p")
            fi
        done
    fi

    # Translate and apply current working directory
    local sandbox_cwd
    sandbox_cwd=$(translate_path "$cwd")
    bwrap_args+=(--chdir "$sandbox_cwd")

    exec bwrap "${bwrap_args[@]}" "$@"
}

# MAIN LOGIC - Route based on calling command name
cmd_name=$(basename "$0")

if [[ "$cmd_name" == "antigravity" ]]; then
    # Smart calling mode: wrap args and run sandboxed antigravity
    # Filter empty arguments
    args=()
    for arg in "$@"; do
        if [[ -n "$arg" ]]; then
            args+=("$arg")
        fi
    done

    if [[ ${#args[@]} -eq 0 ]]; then
        run_sandbox "$APP_BIN" "${ELECTRON_FLAGS[@]}" "${ANTIGRAVITY_FLAGS[@]}" "$DEFAULT_PROJECT"
    else
        run_sandbox "$APP_BIN" "${ELECTRON_FLAGS[@]}" "${ANTIGRAVITY_FLAGS[@]}" "${args[@]}"
    fi
else
    # Called as antigravity-launcher.sh (or other controls)
    if [[ $# -lt 1 ]]; then
        show_help
        exit 1
    fi

    cmd="$1"
    shift

    case "$cmd" in
    install)
        install_launcher "$@"
        ;;
    uninstall)
        uninstall_launcher
        ;;
    env)
        mkdir -p "$(dirname "$ENV_FILE")"
        touch "$ENV_FILE"
        ${EDITOR:-nano} "$ENV_FILE"
        ;;
    help)
        show_help
        ;;
    exec)
        run_sandbox "$APP_BIN" "${ELECTRON_FLAGS[@]}" "${ANTIGRAVITY_FLAGS[@]}" "$@"
        ;;
    run)
        if [[ $# -lt 1 ]]; then
            echo "Error: run requires a command to run." >&2
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
