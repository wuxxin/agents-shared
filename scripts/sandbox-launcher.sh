#!/usr/bin/env bash
# Generalized Sandbox Launcher
# Integrates bubblewrap sandboxing for arbitrary binaries.
set -euo pipefail

# Constants
LAUNCHER_NAME="sandbox-launcher.sh"
AGENT_SHARED_DIR="$HOME/agent-shared"
DOWNLOAD_DIR="/data/download"

# Determine Calling Mode
cmd_name=$(basename "$0")

if [[ "$cmd_name" == "$LAUNCHER_NAME" || "$cmd_name" == "sandbox-launcher" ]]; then
    central_mode=true
else
    central_mode=false
    app_name="$cmd_name"
fi

# Helper: Display launcher help information
show_help() {
    cat <<EOF
Sandbox Launcher Help

Usage when called directly ($LAUNCHER_NAME):

$0 install <app_name> [opts]
    - Setup sandbox and create symlink in ~/.local/bin
    - Options:
        --no-git-config (skip copying .gitconfig)
        --new-config (overwrite environment file)

$0 uninstall <app_name>
    - Remove symlink from ~/.local/bin (preserves data)

$0 destroy <app_name>
    - Delete persistent sandbox home and env file

$0 env <app_name>
    - Edit environment configuration file for app

$0 exec <app_name> [args...]
    - Run the sandboxed application with optional args

$0 run <app_name> <cmd> [args...]
    - Run a custom command inside the sandbox

$0 shell <app_name>
    - Spawn an interactive shell inside the sandbox

Usage when called as a symlink (e.g. <app_name>):
  $0 [args...]                 - Run the sandboxed <app_name> with all arguments
                                 passed transparently to the original binary
EOF
}

# Helper: Find the real binary on the host to avoid recursive launcher calls
find_real_binary() {
    local binary_name="$1"
    # Clean PATH to exclude ~/.local/bin where the launcher symlink is located
    local clean_path
    clean_path=$(echo "$PATH" | tr ':' '\n' | grep -v "$HOME/.local/bin" | tr '\n' ':' | sed 's/:$//')

    # Locate the binary in the cleaned PATH
    PATH="$clean_path" command -v "$binary_name" || true
}

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
    if [[ "$host_path" == "$persistent_home" ]]; then
        echo "$HOME"
    elif [[ "$host_path" == "$persistent_home"/* ]]; then
        echo "$HOME/${host_path#"$persistent_home"/}"
    else
        echo "$host_path"
    fi
}

# Helper: Initialize the sandbox directory structure
initialize_sandbox() {
    echo "Initializing sandbox directories for '$app_name'..."
    mkdir -p "$persistent_home" "$work_dir"
    mkdir -p "$persistent_home/$(realpath --relative-to="$HOME" "$work_dir")"
    mkdir -p "$persistent_home/$(realpath --relative-to="$HOME" "$AGENT_SHARED_DIR")"

    # Create symlink for ~/download to $DOWNLOAD_DIR
    local download_symlink="$persistent_home/download"
    if [[ ! -L "$download_symlink" ]]; then
        if [[ -e "$download_symlink" ]]; then
            rm -f "$download_symlink"
        fi
        ln -s "$DOWNLOAD_DIR" "$download_symlink"
    fi

}

# Command: Install launcher and symlink
cmd_install() {
    local no_git_config=false
    local new_config=false
    while [[ $# -gt 0 ]]; do
        case "$1" in
        --no-git-config) no_git_config=true ;;
        --new-config) new_config=true ;;
        esac
        shift
    done

    local bin_dir="$HOME/.local/bin"
    local script_target="$bin_dir/$LAUNCHER_NAME"
    local symlink_target="$bin_dir/$app_name"

    echo "Installing Sandbox Launcher for '$app_name'..."

    # Initialize sandbox directories
    initialize_sandbox

    # Copy .gitconfig from host if it exists and is missing in sandbox home
    if [[ "$no_git_config" == "false" ]]; then
        if [[ -f "$HOME/.gitconfig" && ! -f "$persistent_home/.gitconfig" ]]; then
            echo "Copying .gitconfig to $persistent_home/.gitconfig..."
            cp "$HOME/.gitconfig" "$persistent_home/.gitconfig"
        fi
    fi

    # Opencode-specific default project initialization
    if [[ "$app_name" == "opencode" ]]; then
        local default_project="$work_dir/default"
        mkdir -p "$default_project"
        if [[ ! -d "$default_project/.git" ]]; then
            git -C "$default_project" init
        fi
    fi

    # Ensure local bin directory exists
    mkdir -p "$bin_dir"

    # Copy launcher script itself to user local bin if called from elsewhere
    local current_script
    current_script="$(realpath "$0")"

    if [[ "$current_script" != "$(realpath "$script_target" 2>/dev/null)" ]]; then
        echo "Copying launcher script to $script_target..."
        cp "$current_script" "$script_target"
        chmod +x "$script_target"
    fi

    # Create symlink if it does not exist yet
    if [[ ! -e "$symlink_target" && ! -L "$symlink_target" ]]; then
        echo "Creating symlink $symlink_target -> $LAUNCHER_NAME..."
        ln -s "$LAUNCHER_NAME" "$symlink_target"
    else
        echo "Symlink/file already exists at $symlink_target (skipping creation)."
    fi

    # Create environment configuration file if missing or if --new-config is specified
    if [[ ! -f "$env_file" || "$new_config" == "true" ]]; then
        echo "Creating environment file at $env_file..."
        mkdir -p "$(dirname "$env_file")"
        cat >"$env_file" <<EOF
# env configuration for $app_name
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
        chmod 600 "$env_file"
    fi

    echo "Installation complete!"
    echo "Sandbox home directory: $persistent_home"
    echo "Sandbox environment file: $env_file"
    echo "Sandbox workspace: $work_dir"
}

# Command: Edit environment configuration file
cmd_env() {
    mkdir -p "$(dirname "$env_file")"
    touch "$env_file"
    ${EDITOR:-nano} "$env_file"
}

# Command: Uninstall symlink
cmd_uninstall() {
    local bin_dir="$HOME/.local/bin"
    local symlink_target="$bin_dir/$app_name"

    echo "Uninstalling Sandbox Launcher for '$app_name'..."

    if [[ -L "$symlink_target" || -e "$symlink_target" ]]; then
        rm -f "$symlink_target"
        echo "Removed symlink: $symlink_target"
    else
        echo "No symlink found at $symlink_target."
    fi

    echo "Uninstallation complete!"
    echo "Persistent sandbox directories was NOT deleted: '$persistent_home'"
}

# Command: Destroy sandbox data
cmd_destroy() {
    echo "Destroying sandbox data for '$app_name'..."

    if [[ -d "$persistent_home" ]]; then
        rm -rf "$persistent_home"
        echo "Deleted sandbox home: $persistent_home"
    fi

    echo "Sandbox destruction for '$app_name' complete (workspace '$work_dir', and env file: $env_file was preserved)."
}

# Command: Run Bubblewrap Sandbox
run_sandbox() {
    # Ensure bubblewrap is installed on the host
    if ! command -v bwrap >/dev/null 2>&1; then
        echo "Error: bubblewrap (bwrap) is not installed or not in PATH." >&2
        exit 1
    fi

    # Initialize sandbox directories if missing (does not delete existing data)
    initialize_sandbox

    # Load environment file if it exists
    if [[ -f "$env_file" ]]; then
        set +u
        set -a
        # shellcheck disable=SC1090
        source "$env_file"
        set +a
        set -u
    fi

    # Check if current working directory is within target mounts
    local cwd
    cwd="$(pwd)"
    local is_allowed=false

    if is_under "$cwd" "$persistent_home" || is_under "$cwd" "$work_dir" || is_under "$cwd" "$AGENT_SHARED_DIR"; then
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

    # Prepare basic bubblewrap arguments
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
        --bind "$persistent_home" "$HOME"
        --bind "$work_dir" "$work_dir"
        --bind "$AGENT_SHARED_DIR" "$AGENT_SHARED_DIR"
        --ro-bind /tmp/.X11-unix /tmp/.X11-unix
        --setenv DISPLAY "$display"
        --setenv XAUTHORITY "$xauthority"
    )

    # Wayland & Audio (Pipewire/PulseAudio) Support
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

    # Download folder write support (if writable on host)
    if [[ -d "$DOWNLOAD_DIR" && -w "$DOWNLOAD_DIR" ]]; then
        bwrap_args+=(--bind "$DOWNLOAD_DIR" "$DOWNLOAD_DIR")
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

    # Execute inside Bubblewrap
    exec bwrap "${bwrap_args[@]}" "$@"
}

# --- Parsing Command and Routing ---

if [[ "$central_mode" == "true" ]]; then
    # Central Mode: sandbox-launcher.sh <cmd> <app_name> [args...]
    if [[ $# -lt 1 ]]; then
        show_help
        exit 1
    fi

    cmd="$1"
    shift

    if [[ "$cmd" == "help" ]]; then
        show_help
        exit 0
    fi

    if [[ $# -lt 1 ]]; then
        echo "Error: Application name (app_name) is required for command '$cmd'." >&2
        show_help >&2
        exit 1
    fi

    app_name="$1"
    shift

    # Setup paths for app_name
    persistent_home="$HOME/.local/sandbox/$app_name"
    work_dir="$HOME/agent-private/$app_name"
    env_file="$HOME/.local/sandbox/$app_name.env"

    case "$cmd" in
    install)
        cmd_install "$@"
        ;;
    uninstall)
        cmd_uninstall
        ;;
    destroy)
        cmd_destroy
        ;;
    env)
        cmd_env
        ;;
    exec)
        real_bin=$(find_real_binary "$app_name")
        if [[ -n "$real_bin" ]]; then
            run_sandbox "$real_bin" "$@"
        else
            run_sandbox "$app_name" "$@"
        fi
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

else
    # App Symlink Mode: <app_name> [args...]
    persistent_home="$HOME/.local/sandbox/$app_name"
    work_dir="$HOME/agent-private/$app_name"
    env_file="$HOME/.local/sandbox/$app_name.env"

    real_bin=$(find_real_binary "$app_name")
    if [[ -n "$real_bin" ]]; then
        run_sandbox "$real_bin" "$@"
    else
        run_sandbox "$app_name" "$@"
    fi
fi
