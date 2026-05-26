# OpenCode Sandbox Launcher

`opencode-launcher.sh` is a wrapper for running the OpenCode AI coding agent inside a **Bubblewrap (`bwrap`)** sandbox with a persistent, isolated home directory.

## Features

- **Installation Utility**: Standardized subcommands (`install` and `uninstall`) to copy the script, establish search path links, and manage setup.
- **Sandbox Verification**: Automatically initializes the sandbox workspace and directories if missing.
- **Persistent Home**: Redirects `$HOME` to `~/.local/sandbox/opencode` within the sandbox.
- **Filesystem Isolation**: Mounts the host root as read-only and uses a `tmpfs` for `/tmp`.
- **Workspace Integration**: Explicitly binds `~/agent-private/opencode` and `~/agent-shared` into the sandbox.
- **Downloads**: Symlinks `~/download` inside the sandbox to `/data/download` on the host (if available).
- **X11/Wayland Support**: Securely shares display sockets and environment variables.

## Installation

To set up the launcher and initialize the sandbox environment:

```bash
./scripts/opencode-launcher.sh install
```

This command:
1. Creates the sandbox home directory structure (`~/.local/sandbox/opencode`).
2. Copies itself to `~/.local/bin/opencode-launcher.sh`.
3. Creates a symlink `~/.local/bin/opencode` pointing to `~/.local/bin/opencode-launcher.sh`.

## Usage

```bash
opencode
```
Or, if running the raw launcher from the repository:
```bash
./scripts/opencode-launcher.sh exec opencode
```

### Advanced Usage: Transient Sandboxing
You can use the launcher to run *any* binary inside the same hardened OpenCode environment using the `exec` subcommand:

```bash
opencode-launcher.sh exec /usr/bin/bash
```

Or start an interactive shell directly:
```bash
opencode-launcher.sh shell
```

## Implementation Considerations

### Security Model
- **`--unshare-all`**: All namespaces are unshared by default. Only network access (`--share-net`) is retained.
- **Privilege Control**: Adds `CAP_SYS_PTRACE` to allow debugging child processes while maintaining isolation.
- **Sandboxing Relaxations**: Electron-based applications require `--no-sandbox` and `--disable-chromium-sandbox` when running inside a pre-existing `bwrap` container to avoid namespace conflicts.

### Directory Mapping
- **Home**: The host's `~/.local/sandbox/opencode` is presented as `$HOME` inside the sandbox, ensuring that configuration files (like `.gitconfig` or `.ssh`) created within the app are persistent but isolated from the real host home.
