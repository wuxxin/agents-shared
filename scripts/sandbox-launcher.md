# Generalized Sandbox Launcher

`sandbox-launcher.sh` is a flexible, generalized wrapper for running any command-line or graphical binary inside a hardened **Bubblewrap (`bwrap`)** sandbox on Linux. It isolates the application's filesystem access, environment, and namespaces while providing support for home directory persistence, GUI displays, sound, and SSH agent forwarding.

## Features

- **Dual Calling Modes**: Supports being called directly as a manager/orchestrator or called transparently as a symlink named after the target application.
- **Configurable Environment File**: Automatically sources and exports variables from `~/.local/sandbox/<app_name>.env` before execution.
- **Graphic & Audio Controls**: Configure X11, Wayland, and audio (PulseAudio/Pipewire) sharing.
- **SSH Agent Forwarding**: Configure Forward the host's `SSH_AUTH_SOCK` socket for Git operations.
- **Location Warning**: Detects if you run from outside allowed mounts, warning you before execution.

---

## Usage Styles

The launcher supports two distinct calling modes:

### Style A: Direct Orchestrator Mode (Central Launcher)

When executed directly as `sandbox-launcher.sh` or `sandbox-launcher`, you must specify the subcommand and the target application. This is the mode used to install, uninstall, destroy, configure, or run shell/custom commands:

```bash
# Setup sandbox and symlink for firefox
sandbox-launcher.sh install firefox

# Run firefox inside the sandbox
sandbox-launcher.sh exec firefox

# Run an interactive bash shell in the firefox sandbox
sandbox-launcher.sh shell firefox

# Execute a custom command in the firefox sandbox
sandbox-launcher.sh run firefox ls -la

# Open the .env configuration file for firefox
sandbox-launcher.sh env firefox

# Delete the persistent data/directories for firefox
sandbox-launcher.sh destroy firefox
```

### Style B: Symlink Mode (Transparent Wrapper)

When you call the launcher via a symlink (e.g. `~/.local/bin/opencode -> sandbox-launcher.sh`), the script operates as a **transparent proxy**.

- **Direct Argument Propagation**: All arguments are passed directly to the original binary inside the sandbox.
- E.g., calling `opencode --version` runs `opencode --version` inside the sandbox, and calling `git commit` runs `git commit` inside the sandbox without colliding with launcher command names.

---

## Sandbox Administration & Lifecycle

The launcher provides several commands to manage your sandbox configurations:

### `install [--no-git-config] [--new-config]`

Sets up 

- the persistent sandbox home directory (`~/.local/sandbox/<app_name>`)
- the workspace (`~/agent-private/<app_name>`)
- creates the `.env` configuration file, and establishes the symlink in `~/.local/bin/<app_name>`.
- by default, it copies your host's `~/.gitconfig` into the sandbox home to preserve your Git identity.
    - Use `--no-git-config` to skip copying the Git configuration.
- Use `--new-config` to force overwrite the environment configuration file with defaults.

### `uninstall`

Removes the launcher symlink `~/.local/bin/<app_name>` from the host. Persistent data directories are preserved.

### `destroy`

Permanently deletes the persistent sandbox home directory (`~/.local/sandbox/<app_name>`).

- **Safety**: The workspace directory (`~/agent-private/<app_name>`) is **never** touched or deleted by this command.

### `env`

Opens the environment configuration file `~/.local/sandbox/<app_name>.env` in the editor specified by your `$EDITOR` environment variable (defaults to `nano` if unset).

---

## Configuration (`.env` file)

Each application's environment configuration file is stored on the host at:
`~/.local/sandbox/<app_name>.env`

Sourcing this file automatically loads and exports variables into the sandbox.

### Custom Bind Mounts
To make additional host directories or files readable and writable inside the sandbox, define `SANDBOX_BIND_PATHS` as a colon-separated list of absolute paths:
```bash
SANDBOX_BIND_PATHS="/home/username/my-shared-project:/opt/special-tool"
```

### Disabling Sockets
You can restrict sandbox access to graphical, audio, and credential resources by setting:
- `DISABLE_XDG_RUNTIME=1`: Disables binding the host's `$XDG_RUNTIME_DIR` entirely. This deactivates Wayland, Pipewire, PulseAudio, and DBus, forcing the application to run completely headless.
- `DISABLE_SSH_AUTH=1`: Disables forwarding the host's SSH agent socket (`SSH_AUTH_SOCK`). This prevents the sandbox from accessing or using your host's SSH keys for Git commands or SSH connections.
- `DISABLE_WAYLAND=1`: Disables forwarding Wayland compositor sockets. The application will not be able to render window displays on a Wayland desktop (though it may fall back to X11 if `DISPLAY` is still set).
- `DISABLE_AUDIO=1`: Disables forwarding PulseAudio/Pipewire sockets. The application will have no audio playback or recording capabilities.
- `DISABLE_DBUS=1`: Disables forwarding the DBus session socket. The application cannot send desktop notifications, interact with the system tray, query desktop themes, or communicate with other host desktop services (which significantly reduces host breakout risk).

---

## Directory Validation & Translation

Because the host home directory is not visible inside the sandbox:

- The launcher **warns** you if the current directory (`pwd`) is outside the allowed target mounts (`~/agent-private/<app_name>`, `~/agent-shared`, or `~/.local/sandbox/<app_name>`) before invoking bubblewrap.
- If the current directory is within the persistent sandbox home on the host (e.g. `~/.local/sandbox/<app_name>/projects`), the launcher **translates** the host path into its internal representation (e.g. `/home/username/projects`) before executing `--chdir` to ensure bubblewrap boots successfully.
