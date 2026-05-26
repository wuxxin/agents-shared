#!/usr/bin/env bash
# Antigravity Sandbox - Persistent Home Edition
set -euo pipefail

# Configuration
app_bin="/opt/Antigravity/antigravity"
app_dir="/opt/Antigravity"
persistent_home="$HOME/.local/sandbox/antigravity"
work_dir="$HOME/agent-private/antigravity"
default_project="$work_dir/default"
agent_shared_dir="$HOME/agent-shared"
download_dir="/data/download"
# Default flags
antigravity_flags=()
electron_flags=(
	--disable-dev-shm-usage
	--disable-chromium-sandbox
	--no-sandbox
)

# Helper: Display launcher help information
show_help() {
	cat <<EOF
Antigravity Sandbox Launcher Help
---------------------------------
Usage:
  $0 [options] [antigravity-arguments...]
  $0 --exec <path-to-binary> [binary-arguments...]
  $0 --help-launcher
  $0 --launcher-install

Options:
  --help-launcher
      Show this help message.

  --launcher-install
      Install the launcher script, symlink, and desktop entries.

  --exec <path-to-binary>
      Run a custom binary/command inside the Bubblewrap sandbox instead of the
      default Antigravity application. All subsequent arguments are passed to the
      executed command.
      Example:
          $0 --exec /usr/bin/bash
          $0 --exec /usr/bin/python3 main.py
EOF
}

# Helper: Initialize the sandbox directory structure
initialize_sandbox() {
	mkdir -p "$persistent_home" "$work_dir" "$default_project"
	mkdir -p "$persistent_home/$(realpath --relative-to="$HOME" "$work_dir")"
	mkdir -p "$persistent_home/$(realpath --relative-to="$HOME" "$agent_shared_dir")"

	# Create symlink for ~/download to $download_dir
	local download_symlink="$persistent_home/download"
	if [[ ! -L "$download_symlink" ]]; then
		if [[ -e "$download_symlink" ]]; then
			rm -f "$download_symlink"
		fi
		ln -s "$download_dir" "$download_symlink"
	fi

	# Create .git for default project if not existing
	if [[ ! -d "$default_project/.git" ]]; then
		git -C "$default_project" init
	fi
}

# Helper: Install script and desktop configurations
install_launcher() {
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

	# Create symlink
	echo "Creating symlink $symlink_target -> $script_target..."
	ln -sf "$script_target" "$symlink_target"

	# Write desktop files
	echo "Installing desktop entries..."
	cat <<EOF >"$app_dir/antigravity.desktop"
[Desktop Entry]
Type=Application
Name=Antigravity(Sb)
GenericName=Code Editor
Comment=Agentic development platform (Sandboxed)
Exec=$script_target %F
TryExec=$script_target
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
Exec=$script_target --new-window %F
Icon=antigravity
EOF

	cat <<EOF >"$app_dir/antigravity-url-handler.desktop"
[Desktop Entry]
Type=Application
Name=Antigravity(SB) - URL Handler
Comment=Handle antigravity:// URLs
Exec=$script_target --open-url %U
Icon=antigravity
Terminal=false
NoDisplay=true
Categories=Development;
MimeType=x-scheme-handler/antigravity;
StartupNotify=true
EOF

	echo "Installation complete!"
	echo "Sandbox home directory: $persistent_home"
}

# --- Command Line Argument Routing ---

# 1. Handle help command
if [[ "${1:-}" == "--help-launcher" ]]; then
	show_help
	exit 0
fi

# 2. Handle installation command
if [[ "${1:-}" == "--launcher-install" ]]; then
	install_launcher
	exit 0
fi

# 3. Check if sandbox exists before proceeding
if [[ ! -d "$persistent_home" ]]; then
	echo "Error: Sandbox directory '$persistent_home' does not exist." >&2
	echo "Please run '$0 --launcher-install' to install the launcher and set up the sandbox." >&2
	echo >&2
	show_help >&2
	exit 1
fi

# Ensure bubblewrap is installed on the host
if ! command -v bwrap >/dev/null 2>&1; then
	echo "Error: bubblewrap (bwrap) is not installed or not in PATH." >&2
	exit 1
fi

# Prepare basic bubblewrap argument list
# (Unset DISPLAY, XAUTHORITY, and XDG_RUNTIME_DIR default to avoid unbound errors)
DISPLAY="${DISPLAY:-}"
XAUTHORITY="${XAUTHORITY:-}"
XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-}"

bwrap_args=(
	# Unshare namespaces for isolation
	--unshare-all
	--share-net
	--die-with-parent
	--new-session
	# Let antigravity debug processes
	--cap-add CAP_SYS_PTRACE
	# Mount host root read-only
	--ro-bind / /
	# Overlay a writable tmpfs on /tmp
	--tmpfs /tmp
	# Mount devices and process info
	--dev-bind /dev /dev
	--ro-bind /sys /sys
	--proc /proc
	# Bind the .local/sandbox/antigravity folder to $HOME
	--bind "$persistent_home" "$HOME"
	# --- OVERRIDES ---
	# Map: $HOME/agent-private/antigravity -> $persistent_home/agent-private/antigravity
	--bind "$work_dir" "$work_dir"
	# Map: $HOME/agent-shared -> $persistent_home/agent-shared
	--bind "$agent_shared_dir" "$agent_shared_dir"
	# Bind X11 / Wayland Sockets (Display)
	--ro-bind /tmp/.X11-unix /tmp/.X11-unix
	--setenv DISPLAY "$DISPLAY"
	--setenv XAUTHORITY "$XAUTHORITY"
	# Change Dir to agent-private/antigravity
	--chdir "$work_dir"
)

# Wayland Support
if [[ -n "$XDG_RUNTIME_DIR" ]]; then
	bwrap_args+=(
		--bind "$XDG_RUNTIME_DIR" "$XDG_RUNTIME_DIR"
		--setenv XDG_RUNTIME_DIR "$XDG_RUNTIME_DIR"
	)
fi

# Run sandbox initialization to ensure paths/symlinks are up to date
initialize_sandbox

# 4. Handle custom binary execution inside sandbox
if [[ "${1:-}" == "--exec" ]]; then
	if [[ -z "${2:-}" ]]; then
		echo "Error: --exec requires a binary path argument." >&2
		exit 1
	fi
	app_bin="$2"
	shift 2 # Remove --exec and the path from the argument list
	exec bwrap "${bwrap_args[@]}" "$app_bin" "$@"
fi

# 5. Handle default application execution
# Filter out empty arguments (commonly passed as "" by desktop managers)
args=()
for arg in "$@"; do
	if [[ -n "$arg" ]]; then
		args+=("$arg")
	fi
done

echo "Starting Antigravity with Persistent Home"
echo "Container Home:     $persistent_home"
echo "Workspace:          $work_dir"
echo "Agent Shared:       $agent_shared_dir"
echo "Download Dir:       $download_dir"
echo "BubbleWrap Args:    ${bwrap_args[*]}"
echo "Electron Bin:       $app_bin"
echo "Electron App Dir:   $app_dir"
echo "Electron Flags:     ${electron_flags[*]}"
echo "Antigravity Flags:  ${antigravity_flags[*]}"

if [[ ${#args[@]} -eq 0 ]]; then
	echo "Empty Args, calling with dir=$default_project"
	exec bwrap "${bwrap_args[@]}" \
		"$app_bin" "${electron_flags[@]}" "${antigravity_flags[@]}" "$default_project"
else
	echo "Calling with Args: ${args[*]}"
	exec bwrap "${bwrap_args[@]}" \
		"$app_bin" "${electron_flags[@]}" "${antigravity_flags[@]}" "${args[@]}"
fi
