# Generalized Sandbox & systemd Transient Launcher

`sandbox-ctl` is a flexible, generalized wrapper for running any command-line or graphical binary inside a hardened container or namespace sandbox on Linux. 

By default, it runs the application inside a native **systemd user transient service (`systemd-run`)** for cgroups confinement, resource limiting, and systemd security controls. If systemd is not reachable or if configured to do so, it falls back to a **Bubblewrap (`bwrap`)** sandbox.

---

## Features

- **Persistent Relocated HOME**: Maps the persistent sandbox home directory (`$HOME/.local/sandbox/<app_name>`) as the user's real `$HOME` inside the sandbox across all execution modes (`exec`, `run`, `shell`, `service`, and install/uninstall hooks). The application cannot see or access `.local/sandbox/<app_name>` from the inside because `$HOME` IS the persistent sandbox directory.
- **Dual Calling Modes**: Supports being called directly as a manager/orchestrator or called transparently as a symlink named after the target application.
- **Configurable Environment File**: Automatically sources and exports variables from `~/.config/systemd/user/<app_name>.env` before execution.
- **Dual Execution Engines**: Supports systemd transient service execution (`systemd-run`), Bubblewrap confinement (`bwrap`), or automatic engine detection and fallback.
- **Sandboxed Hook Execution**: Executes `LAUNCHER_INSTALL_CMDS` and `LAUNCHER_UNINSTALL_CMDS` inside the sandbox environment so package managers (`bun`, `uv`, `npm`) install strictly inside the isolated sandbox home.
- **Graphic & Audio Controls**: Securely forwards X11, Wayland, Pipewire, PulseAudio, and DBus sockets into systemd and bubblewrap environments.
- **SSH Agent Forwarding**: Forwards the host's `SSH_AUTH_SOCK` socket for Git operations.
- **Generic GUI / Desktop Lifecycle**: Automatically creates standard desktop entries (`.desktop` files) and menus for graphical applications during installation.
- **Sandbox Environment Indicators**: Automatically injects `SANDBOX_NAME="<app_name>"`, `SANDBOX_ENGINE="<engine>"`, and `SANDBOX="<app_name>"` into all container sessions, making it easy for scripts, tools, and shell prompts (`zsh`, `bash`) to detect and display the active sandbox name.

---

## Usage Styles

The launcher supports two distinct calling modes:

### Style A: Direct Orchestrator Mode (Central Launcher)

When executed directly as `sandbox-ctl` you must specify the subcommand and the target application. This is the mode used to install, uninstall, destroy, configure, or run shell/custom commands:

```bash
# Setup sandbox, service files, symlink, and run sandboxed install hooks for opencode
sandbox-ctl install opencode

# Run opencode inside the sandbox
sandbox-ctl exec opencode

# Run an interactive login shell ($SHELL -l) in the opencode sandbox
sandbox-ctl shell opencode

# Execute a custom command in the opencode sandbox
sandbox-ctl run opencode ls -la

# Open the environment configuration file for opencode
sandbox-ctl edit opencode

# Display service file and environment configuration
sandbox-ctl cat opencode

# Run sandbox self-test diagnostics and engine checks
sandbox-ctl selftest opencode

# Service Control Commands:
sandbox-ctl start opencode
sandbox-ctl stop opencode
sandbox-ctl restart opencode
sandbox-ctl status opencode
sandbox-ctl enable opencode
sandbox-ctl disable opencode
sandbox-ctl logs opencode

# Remove launcher files and run sandboxed uninstall hooks (preserves persistent data)
sandbox-ctl uninstall opencode

# Delete the persistent data/directories for opencode
sandbox-ctl destroy opencode
```

### Style B: Symlink Mode (Transparent Wrapper)

When you call the launcher via a symlink (e.g. `~/.local/bin/opencode -> sandbox-ctl`), the script operates as a **transparent proxy**.

- **Current Workdir Resolution**: 
  - If CWD is under host `$HOME/.local/sandbox/<app_name>`, it maps to `$HOME` or `$HOME/<subpath>` inside the sandbox.
  - If CWD is under host `$HOME`, it maps to `$HOME/<subpath>` inside the sandbox.
  - If CWD is under an explicitly mounted workspace (`work_dir`) or extra mount (`LAUNCHER_EXTRA_MOUNTS`), it is mapped 1:1 inside the sandbox.
- **Direct Argument Propagation**: All arguments are passed directly to the original binary inside the sandbox.
- E.g., calling `opencode --version` runs `opencode --version` inside the sandbox, and calling `git commit` runs `git commit` inside the sandbox.

---

## Sandbox Administration & Lifecycle

### `scriptcopy` (alias `install-script` / `copy-script`)

Copies the `sandbox-ctl` executable script itself to `~/.local/bin/sandbox-ctl` and sets executable permissions without setting up a sandbox, initializing environment configuration files, or creating systemd service files. Use this command when you want to make `sandbox-ctl` globally available in your user `PATH`.

### `install [--no-git-config] [--new-config] [--new-config-from <path>] [--no-start]`

Sets up:
- the persistent sandbox home directory (`~/.local/sandbox/<app_name>`)
- the workspace (`~/agent-private/<app_name>`)
- creates the `.env` configuration file, establishes the symlink in `~/.local/bin/<app_name>`, generates the systemd user service unit file, and creates desktop files if `LAUNCHER_GUI=true` is configured.
- copies your host's `~/.gitconfig` into the sandbox home to preserve your Git identity (unless `--no-git-config` is supplied).
- **Sandboxed Install Hooks**: Executes all commands listed in `LAUNCHER_INSTALL_CMDS` sequentially **inside the sandbox**. Commands execute from first to last (logging warnings if an individual command fails) seeing only the sandboxed filesystem and environment.
- Use `--no-start` to register files without automatically enabling/starting the service (if `LAUNCHER_SERVICE_ENABLED=true` is configured).

### `uninstall`

Stops, disables, and removes the systemd user service file, launcher symlink `~/.local/bin/<app_name>`, and desktop entries.
- **Sandboxed Uninstall Hooks**: Executes all commands listed in `LAUNCHER_UNINSTALL_CMDS` sequentially **inside the sandbox** to clean up installed modules or tools before removing configuration. Persistent data directories and environment files are preserved.

### `destroy`

Permanently deletes the persistent sandbox home directory (`~/.local/sandbox/<app_name>`).
- **Safety**: The workspace directory (`~/agent-private/<app_name>`) is **never** touched or deleted by this command.

### `edit`

Opens the environment configuration file `~/.config/systemd/user/<app_name>.env` in the editor specified by your `$EDITOR` environment variable (defaults to `nano` if unset). If systemd is running and the service is active, restarts the service upon editor exit to apply the updated environment.

### `cat`

Prints the systemd service unit file and environment configuration file contents.

### `selftest`

Runs automated sanity checks and diagnostic tests for the application:
1. **Config & Service File Audits**: Verifies that environment files and systemd service unit files exist and checks for raw/unresolved specifier strings (`%h`, `%H`, etc.).
2. **Systemd Service Unit Status**: Queries and displays the systemd user service unit status via `systemctl --user status`.
3. **Engine Diagnostic Execution**: Executes inline container diagnostics for **both execution engines** (`bwrap` and `systemd` if reachable):
   - Working directory (`PWD`) and `UID`
   - Real `$HOME` resolution (`HOME=$HOME`)
   - Persistent home leak check (verifying `$HOME/.local/sandbox/<app_name>` does NOT exist inside the sandbox)
   - `PATH` directory existence checks
   - Key environment variables (`SHELL`, `XDG_RUNTIME_DIR`, `SSH_AUTH_SOCK`, `DISPLAY`, `WAYLAND_DISPLAY`)
   - Unresolved specifier check in runtime environment (`env | grep -E "%[hHtSEuUbB]"`)

---

## Execution Engines & Engine Differences

`sandbox-ctl` supports two execution engines configured via `LAUNCHER_ENGINE`:

| Feature / Aspect | Systemd Engine (`LAUNCHER_ENGINE="systemd"`) | Bubblewrap Engine (`LAUNCHER_ENGINE="bwrap"`) |
| :--- | :--- | :--- |
| **Execution Tool** | `systemd-run --user` (transient scopes/services) | `bwrap` (Bubblewrap container executable) |
| **Prerequisites** | Systemd user daemon socket reachable | `bwrap` binary installed in PATH |
| **Persistent HOME** | Host `$HOME/.local/sandbox/<app>` -> `$HOME` | Host `$HOME/.local/sandbox/<app>` -> `$HOME` |
| **Path Mounts** | `BindPaths` systemd properties | `--bind` Bubblewrap arguments |
| **Environment Exports** | `Environment=` systemd properties | `--setenv` Bubblewrap arguments |
| **Background Services** | Registered as native systemd user units | Executed under systemd service or wrapper |
| **Resource Limits** | Native cgroups v2 containment | Managed by parent process tree / namespaces |
| **Logging** | Systemd journal (`journalctl --user`) | Stdout/Stderr streaming |

### Engine Selection (`LAUNCHER_ENGINE`)
- `"auto"` (Default): Uses systemd if the systemd user manager socket is reachable; otherwise automatically falls back to `bwrap`.
- `"systemd"`: Forces execution through systemd (`systemd-run`). Fails if systemd user socket is unreachable.
- `"bwrap"`: Forces execution through Bubblewrap containers directly, bypassing systemd.

### Environment Identifiers & Shell Prompt Integration

`sandbox-ctl` automatically injects identity environment variables into every sandboxed session:
- **`SANDBOX_NAME`**: Set to the target application name (e.g. `opencode`).
- **`SANDBOX_ENGINE`**: Set to the active engine (`systemd` or `bwrap`).
- **`SANDBOX`**: Set to the target application name (`opencode`).

You can customize your `zsh` or `bash` prompt inside the sandbox to display the active sandbox indicator:

**Zsh (`~/.zshrc`)**:
```zsh
if [[ -n "$SANDBOX_NAME" ]]; then
    PROMPT="%F{cyan}[$SANDBOX_NAME]%f $PROMPT"
fi
```

**Bash (`~/.bashrc`)**:
```bash
if [ -n "$SANDBOX_NAME" ]; then
    PS1="[$SANDBOX_NAME] $PS1"
fi
```

---

## Configuration (`.env` file)

Each application's environment configuration file is stored on the host at:
`~/.config/systemd/user/<app_name>.env`

Sourcing this file automatically loads and exports variables into the sandbox environment.

### Configuration Options Reference

- **`LAUNCHER_ENGINE`** (Default: `"auto"`)
  Configures the execution engine (`auto`, `systemd`, or `bwrap`).

- **`DISABLE_XDG_RUNTIME`** (Default: `"false"`)
  Disables binding the host's `$XDG_RUNTIME_DIR` entirely (deactivates Wayland, Pipewire, PulseAudio, DBus).

- **`DISABLE_SSH_AUTH`** (Default: `"false"`)
  Disables forwarding the host's SSH agent socket (`SSH_AUTH_SOCK`).

- **`DISABLE_WAYLAND`** (Default: `"false"`)
  Disables forwarding Wayland compositor sockets.

- **`DISABLE_AUDIO`** (Default: `"false"`)
  Disables forwarding PulseAudio/Pipewire sockets.

- **`DISABLE_DBUS`** (Default: `"false"`)
  Disables forwarding the DBus session socket.

- **`DISABLE_IPC_SHARE`** (Default: `"true"`)
  Disables host IPC namespace sharing (set to `"false"` for GPU/ROCm hardware IPC access).

- **`DISABLE_PID_SHARE`** (Default: `"true"`)
  Disables host PID namespace sharing.

- **`DISABLE_HARDWARE`** (Default: `"false"`)
  Disables access to host hardware and DRI/GPU devices (`PrivateDevices=yes` / `--dev /dev`).

- **`LAUNCHER_PRIVATE_BASEPATH`** (Default: `"$HOME/agent-private"`)
  Configures host base directory for private workspaces.

- **`LAUNCHER_PRIVATE_MOUNTS`** (Default: `""`)
  Space-separated list of relative directories under `LAUNCHER_PRIVATE_BASEPATH` to bind-mount.

- **`LAUNCHER_SANDBOX_MOUNTS`** (Default: `""`)
  Space-separated list of other sandboxes to expose (`sandbox_name/subpath`). Host `~/.local/sandbox/sandbox_name/subpath` is mounted directly to `~/.subpath` inside the sandbox (e.g., `deep-research/.cache/deep-research-profiles` mounts to `~/.cache/deep-research-profiles` inside the container).

- **`LAUNCHER_EXTRA_MOUNTS`** (Default: `"$HOME/agent-shared:agent-shared /data/download:download"`)
  Space-separated list of `host-path:sandbox-path` mount specifications. Relative sandbox paths map under `$HOME`.

- **`LAUNCHER_GUI`** (Default: `"false"`)
  Enables desktop entry launcher (`.desktop` file) creation under `~/.local/share/applications/`.

- **`LAUNCHER_GUI_NAME`**, **`LAUNCHER_GUI_COMMENT`**, **`LAUNCHER_GUI_ICON`**, **`LAUNCHER_GUI_CATEGORIES`**, **`LAUNCHER_GUI_TERMINAL`**
  Customize display properties for the generated desktop entry.

- **`LAUNCHER_SERVICE_ENABLED`** (Default: `"false"`)
  Enables background systemd user service.

- **`LAUNCHER_SERVICE_CMD`** (Default: `"sleep"`), **`LAUNCHER_SERVICE_ARGS`** (Default: `"10"`)
  The main background service command and arguments.
  *Example service test configuration*:
  ```bash
  LAUNCHER_SERVICE_CMD="bash"
  LAUNCHER_SERVICE_ARGS='-c "export; exec sleep infinity"'
  ```

- **`LAUNCHER_SIDECARS`** (Default: `"sleep"`)
  Space- or semicolon-separated list of background sidecar processes to monitor with the main service.

- **`LAUNCHER_EXPORTS`** (Default: `()`)
  Bash array containing key-value environment variable exports (e.g. `'KEY=VALUE'`) injected into all execution modes.

- **`LAUNCHER_INSTALL_CMDS`** (Default: `()`)
  Bash array of commands executed **inside the sandbox** during `install`. Must be idempotent. Runs sequentially from first to last.

- **`LAUNCHER_UNINSTALL_CMDS`** (Default: `()`)
  Bash array of commands executed **inside the sandbox** during `uninstall` to clean up installed tools or packages.

---

## Complete Application Configuration Example (`opencode.env`)

Below is a complete, annotated example environment configuration file (`~/.config/systemd/user/opencode.env`) demonstrating persistent home isolation, sandboxed install/uninstall hooks, background service options, and extra directory mounts:

```bash
# env configuration for opencode
# This file is loaded by the sandbox launcher.

# --- Execution Options ---
# Configures the execution engine (auto, systemd, bwrap).
# Set to 'systemd' to force cgroups containment or 'bwrap' to force bubblewrap container.
# LAUNCHER_ENGINE="auto"

# --- Hardening / Feature Flags (set to true to disable) ---
# DISABLE_XDG_RUNTIME="false"   # Disable XDG runtime directory (Wayland, DBus, audio)
DISABLE_SSH_AUTH="true"      # Disable SSH agent forwarding
DISABLE_WAYLAND="true"       # Disable Wayland display access
# DISABLE_AUDIO="false"         # Disable audio playback/recording
DISABLE_DBUS="true"          # Disable DBus session bus communication

# --- Namespace & Hardware Containment (set to true to isolate, false to share) ---
# DISABLE_HARDWARE="false"     # Isolate host GPU/DRI devices (set to true to run headless)
# DISABLE_IPC_SHARE="true"     # Isolate IPC namespace (set to false for GPU/ROCm hardware)
# DISABLE_PID_SHARE="true"     # Isolate PID namespace (set to false to share host PIDs, to enable trace or inspect of child processes)

# --- Path / Directory Mounts ---
# LAUNCHER_PRIVATE_BASEPATH="$HOME/agent-private"
# LAUNCHER_PRIVATE_MOUNTS=""
# LAUNCHER_SANDBOX_MOUNTS=""
LAUNCHER_EXTRA_MOUNTS="$HOME/agent-shared:agent-shared /data/download:download"

# --- Desktop / GUI Integration ---
# LAUNCHER_GUI="false"            # Set to true to enable generating a desktop entry (.desktop file)
# LAUNCHER_GUI_NAME=""
# LAUNCHER_GUI_COMMENT="Sandboxed app"
# LAUNCHER_GUI_ICON=""
# LAUNCHER_GUI_CATEGORIES="Utility;"
# LAUNCHER_GUI_TERMINAL="false"

# --- Service & Sidecar Options ---
# Set LAUNCHER_SERVICE_ENABLED="true" to enable background systemd service execution.
# Example launcher service command that outputs environment exports and waits until stopped:
LAUNCHER_SERVICE_ENABLED="true"
LAUNCHER_SERVICE_CMD="bash"
LAUNCHER_SERVICE_ARGS='-c "export; exec sleep infinity"'
LAUNCHER_SIDECARS="sleep"
LAUNCHER_SIDECAR_SLEEP_CMD="bash"
LAUNCHER_SIDECAR_SLEEP_ARGS='-c "export; exec sleep infinity"'

# --- Environment Variable Exports ---
# List of environment variables to export into the sandbox environment
# LAUNCHER_EXPORTS=(
#   'OPENCODE_EXPERIMENTAL_BACKGROUND_SUBAGENTS=true'
# )

# --- Application Startup Options ---
# LAUNCHER_APP_FLAGS=""     # Extra flags appended to binary (e.g. '--no-sandbox' for Electron)
# LAUNCHER_DEFAULT_ARGS=""   # Default args passed if none are provided (e.g. '$work_dir/default')
LAUNCHER_INIT_DEFAULT_PROJECT="true" # Set to true to run 'git init' on the default project workspace

# Array of bash commands executed during uninstall. Should clean up any files/directories created by LAUNCHER_INSTALL_CMDS.
LAUNCHER_UNINSTALL_CMDS=(
   'cd $HOME/.local/bin/ && rm arbor arbor-mcp coordinator executor openadapt review-research run-research'
   'rm -rf $HOME/.local/share/uv'
   'rm -rf $HOME/.config/opencode/node_modules'
   'rm -rf $HOME/.cache/opencode/packages'
   'cd $HOME/.config/opencode && rm bun.lock package-lock.json'
)

# Array of bash commands executed during install. Must be idempotent — should recreate everything needed as if it were a fresh install.
LAUNCHER_INSTALL_CMDS=(
   "${LAUNCHER_UNINSTALL_CMDS[@]}"
   'cd $HOME/.config/opencode && bun install'
   'cd $HOME/.config/opencode && bunx oh-my-opencode-slim install --no-tui --skills=yes --companion=no --background-subagents=no'
   'cd $HOME/.config/opencode && npx @slkiser/opencode-quota update --yes'
   'for tool in arbor-agent "openadapt[browser]" opencode-a2a; do uv tool install --force --refresh $tool;done'
)

```
