# Generalized Sandbox & systemd Transient Launcher

`sandbox-ctl` is a flexible, generalized wrapper for running any command-line or graphical binary inside a hardened container or namespace sandbox on Linux. 

By default, it runs the application inside a native **systemd user transient service (`systemd-run`)** for cgroups confinement, resource limiting, and systemd security controls. If systemd is not reachable or if configured to do so, it falls back to a **Bubblewrap (`bwrap`)** sandbox.

---

## Features

- **Relocated HOME**: Relocates the application's home directory to `$HOME/.local/sandbox/<app_name>` by overlaying the real user home with a persistant path.
- **Dual Calling Modes**: Supports being called directly as a manager/orchestrator or called transparently as a symlink named after the target application.
- **Configurable Environment File**: Automatically sources and exports variables from `~/.local/sandbox/<app_name>.env` before execution.
- **Configurable Engines**: Supports systemd transient service execution, Bubblewrap confinement, or automatic engine detection/fallback.
- **Graphic & Audio Controls**: Securely forwards X11, Wayland, Pipewire, PulseAudio, and DBus sockets into systemd and bubblewrap environments.
- **SSH Agent Forwarding**: Forwards the host's `SSH_AUTH_SOCK` socket for Git operations.
- **Generic GUI / Desktop Lifecycle**: Automatically creates standard desktop entries (`.desktop` files) and menus for graphical applications during installation.
- **Dynamic Path Mounts (`LAUNCHER_*`)**: Easily mount workspaces, other sandboxes, or external host paths.

---

## Usage Styles

The launcher supports two distinct calling modes:

### Style A: Direct Orchestrator Mode (Central Launcher)

When executed directly as `sandbox-ctl` you must specify the subcommand and the target application. This is the mode used to install, uninstall, destroy, configure, or run shell/custom commands:

```bash
# Setup sandbox, service files, and symlink for opencode
sandbox-ctl install opencode

# Run opencode inside the sandbox
sandbox-ctl exec opencode

# Run an interactive bash shell in the opencode sandbox
sandbox-ctl shell opencode

# Execute a custom command in the opencode sandbox
sandbox-ctl run opencode ls -la

# Open the environment configuration file for opencode
sandbox-ctl edit opencode

# Display environment config, bubblewrap / systemd-run representations, and service file
sandbox-ctl analyse opencode

# Service Control Commands:
sandbox-ctl start opencode
sandbox-ctl stop opencode
sandbox-ctl restart opencode
sandbox-ctl status opencode
sandbox-ctl enable opencode
sandbox-ctl disable opencode
sandbox-ctl logs opencode

# Delete the persistent data/directories for opencode
sandbox-ctl destroy opencode
```

### Style B: Symlink Mode (Transparent Wrapper)

When you call the launcher via a symlink (e.g. `~/.local/bin/opencode -> sandbox-ctl`), the script operates as a **transparent proxy**.

- **Current Workdir**: If the current working directory is under `$HOME`, it is mapped to the corresponding path under the wrapped persistent home (`~/.local/sandbox/<app_name>`). If the current working directory is outside `$HOME` or is an explicitly mounted directory, it is mapped 1:1 inside the sandbox. No extra mounting is performed; if the directory does not exist, sandbox execution will fail.
- **Direct Argument Propagation**: All arguments are passed directly to the original binary inside the sandbox.
- E.g., calling `opencode --version` runs `opencode --version` inside the sandbox, and calling `git commit` runs `git commit` inside the sandbox.

---

## Sandbox Administration & Lifecycle

The launcher provides several commands to manage your sandbox configurations:

### `install [--no-git-config] [--new-config] [--no-start]`

Sets up:
- the persistent sandbox home directory (`~/.local/sandbox/<app_name>`)
- the workspace (`~/agent-private/<app_name>`)
- creates the `.env` configuration file, establishes the symlink in `~/.local/bin/<app_name>`, generates the systemd user service unit file, and creates desktop files if `LAUNCHER_GUI=true` is configured.
- by default, it copies your host's `~/.gitconfig` into the sandbox home to preserve your Git identity.
    - Use `--no-git-config` to skip copying the Git configuration.
- Use `--new-config` to force overwrite the environment configuration file with defaults.
- Use `--no-start` to register files without automatically enabling/starting the service (if `LAUNCHER_SERVICE_ENABLED=true` is configured).

### `uninstall`

Stops, disables, and removes the systemd user service file. It also removes the launcher symlink `~/.local/bin/<app_name>` and any desktop entries. Persistent data directories and the environment configuration file are preserved.

### `destroy`

Permanently deletes the persistent sandbox home directory (`~/.local/sandbox/<app_name>`).
- **Safety**: The workspace directory (`~/agent-private/<app_name>`) is **never** touched or deleted by this command.

### `edit`

Opens the environment configuration file `~/.config/systemd/user/<app_name>.env` in the editor specified by your `$EDITOR` environment variable (defaults to `nano` if unset). If systemd is running and the service is active, restarts the service upon editor exit to apply the updated environment.

### `analyse`

Displays the environment configuration file content, the bubblewrap CLI arguments representation, the systemd-run CLI arguments representation, and the generated systemd service file (if it exists) to help inspect and debug containment parameters.

---

## Configuration (`.env` file)

Each application's environment configuration file is stored on the host at:
`~/.config/systemd/user/<app_name>.env`

Sourcing this file automatically loads and exports variables into the sandbox. Note: For backward compatibility, installing or running a command automatically migrates any legacy environment files from `~/.local/sandbox/<app_name>.env` to the new path.

### Detailed Configuration Option Documentation

These variables can be defined in the application's environment configuration file on the host (`~/.config/systemd/user/<app_name>.env`):

- **`LAUNCHER_ENGINE`** (Default: `"auto"`)
  Configures the execution engine. Can be set to `auto` (detect systemd and fallback to bwrap), `systemd` (force systemd scope transient service execution), or `bwrap` (force bubblewrap container execution). Use `bwrap` if you need strict namespace isolation bypassing systemd, or `systemd` to force cgroups containment.

- **`DISABLE_XDG_RUNTIME`** (Default: `"false"`)
  Disables binding the host's `$XDG_RUNTIME_DIR` entirely. This deactivates Wayland, Pipewire, PulseAudio, and DBus, forcing the application to run completely headless.

- **`DISABLE_SSH_AUTH`** (Default: `"false"`)
  Disables forwarding the host's SSH agent socket (`SSH_AUTH_SOCK`). This prevents the sandbox from accessing or using your host's SSH keys for Git commands or SSH connections.

- **`DISABLE_WAYLAND`** (Default: `"false"`)
  Disables forwarding Wayland compositor sockets. The application will not be able to render window displays on a Wayland desktop (though it may fall back to X11 if `DISPLAY` is still set).

- **`DISABLE_AUDIO`** (Default: `"false"`)
  Disables forwarding PulseAudio/Pipewire sockets. The application will have no audio playback or recording capabilities.

- **`DISABLE_DBUS`** (Default: `"false"`)
  Disables forwarding the DBus session socket. The application cannot send desktop notifications, interact with the system tray, query desktop themes, or communicate with other host desktop services (which significantly reduces host breakout risk).

- **`DISABLE_IPC_SHARE`** (Default: `"true"`)
  Disables host IPC namespace sharing. Set to `"true"` to isolate the IPC namespace for security, or `"false"` to share the host's IPC namespace. Sharing the IPC namespace is required for GPU/ROCm servers to communicate with host device drivers.

- **`DISABLE_PID_SHARE`** (Default: `"true"`)
  Disables host PID namespace sharing. Set to `"true"` to isolate the PID namespace, or `"false"` to share the host's PID namespace. Sharing PIDs is rarely needed unless the sandboxed app must trace or inspect host processes.

- **`DISABLE_HARDWARE`** (Default: `"false"`)
  Disables access to host hardware and DRI/GPU devices. Set to `"true"` to isolate host hardware (runs completely headless using `--dev /dev` / `PrivateDevices=yes`), or `"false"` to allow host device access.

- **`LAUNCHER_PRIVATE_BASEPATH`** (Default: `"$HOME/agent-private"`)
  Configures the base directory on the host where private workspaces are stored. Customize this if your workspaces reside on a separate drive or path.

- **`LAUNCHER_PRIVATE_MOUNTS`** (Default: `""`)
  A space-separated list of relative directories under `LAUNCHER_PRIVATE_BASEPATH` to bind-mount. Use this to selectively expose specific workspace directories inside the sandbox.

- **`LAUNCHER_SANDBOX_MOUNTS`** (Default: `""`)
  A space-separated list of other application sandboxes to expose. Format is `sandbox_name/subpath`. Use this when one sandboxed app must access specific folders in another app's persistent home.

- **`LAUNCHER_EXTRA_MOUNTS`** (Default: `"$HOME/agent-shared:agent-shared /data/download:download"`)
  A space-separated list of `host-path:sandbox-path` mount specifications. Use this to bind mount arbitrary host directories or files. Relative sandbox paths are mounted under the relocated home directory.

- **`LAUNCHER_GUI`** (Default: `"false"`)
  Enables graphical desktop entry integration. Set to `"true"` to automatically create a desktop entry launcher (`.desktop` file) under `~/.local/share/applications/` on install. Set to `"false"` to skip or remove it.

- **`LAUNCHER_GUI_NAME`** (Default: Capitalized `<app_name>`)
  Specifies the display name inside the generated desktop entry.

- **`LAUNCHER_GUI_COMMENT`** (Default: `"Sandboxed <app_name>"`)
  Specifies the description/comment inside the generated desktop entry.

- **`LAUNCHER_GUI_ICON`** (Default: `"<app_name>"`)
  Specifies the application icon name inside the generated desktop entry.

- **`LAUNCHER_GUI_CATEGORIES`** (Default: `"Utility;"`)
  Specifies the desktop menu categories for the desktop entry.

- **`LAUNCHER_GUI_TERMINAL`** (Default: `"false"`)
  Specifies whether the graphical application requires running inside a terminal window.

- **`LAUNCHER_APP_FLAGS`** (Default: `""`)
  A list of command-line arguments to append when launching the real binary. Use this to pass mandatory startup flags (e.g. `--no-sandbox` for Electron-based apps).

- **`LAUNCHER_DEFAULT_ARGS`** (Default: `""`)
  Default arguments passed to the application if it is invoked with none. Use this to open a default folder or project.

- **`LAUNCHER_INIT_DEFAULT_PROJECT`** (Default: `"false"`)
  Automates repository initialization. Set to `"true"` to run `git init` on the default project workspace on install.

- **`LAUNCHER_SERVICE_ENABLED`** (Default: `"false"`)
  Enables the systemd user service. If `"true"`, the service will be enabled and started on installation or configuration updates.

- **`LAUNCHER_SERVICE_CMD`** (Default: `"sleep"`)
  The main command/binary to run in the background as the primary service.

- **`LAUNCHER_SERVICE_ARGS`** (Default: `"10"`)
  The arguments passed to the primary service command.

- **`LAUNCHER_SIDECARS`** (Default: `"sleep"`)
  A space- or semicolon-separated list of background sidecar processes to monitor and execute with the main service.

- **`LAUNCHER_SIDECAR_<NAME>_CMD`**
  The command or path to the sidecar executable (e.g. `LAUNCHER_SIDECAR_SLEEP_CMD="sleep"`).

- **`LAUNCHER_SIDECAR_<NAME>_ARGS`**
  The arguments to pass to the sidecar command (e.g. `LAUNCHER_SIDECAR_SLEEP_ARGS="10"`).

- **`LAUNCHER_EXPORTS`** (Default: `()`)
  A bash array containing key-value environment variable exports (e.g., `'KEY=VALUE'`) to be injected into the sandbox for all execution modes (service, run, exec, shell).
