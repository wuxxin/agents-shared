# Antigravity Sandbox Launcher

`antigravity-launcher.sh` is a wrapper for running the Antigravity IDE (and other Electron apps) inside a **Bubblewrap (`bwrap`)** sandbox with a persistent, isolated home directory.

## Features

- **Installation Utility**: Integrates desktop launchers and sets up search path links via `--launcher-install`.
- **Sandbox Verification**: Automatically checks if `~/.local/sandbox/antigravity` exists before invoking the container; displays help/setup instructions if missing.
- **Persistent Home**: Redirects `$HOME` to `~/.local/sandbox/antigravity` within the sandbox.
- **Filesystem Isolation**: Mounts the host root as read-only and uses a `tmpfs` for `/tmp`.
- **Workspace Integration**: Explicitly binds `~/agent-private/antigravity` and `~/agent-shared` into the sandbox.
- **X11/Wayland Support**: Securely shares display sockets and environment variables.

## Installation

To set up the launcher, initialize the sandbox environment, and install the desktop menu entries:

```bash
./scripts/antigravity-launcher.sh --launcher-install
```

This command:
1. Creates the sandbox home directory structure (`~/.local/sandbox/antigravity`).
2. Copies itself to `~/.local/bin/antigravity-launcher.sh`.
3. Creates a symlink `~/.local/bin/antigravity` pointing to `~/.local/bin/antigravity-launcher.sh`.
4. Installs the main and URL-handler desktop entries to `~/.local/share/applications/` with resolved home directory paths.

## Usage

```bash
antigravity
```
Or, if running the raw launcher from the repository:
```bash
./scripts/antigravity-launcher.sh
```

### Advanced Usage: Transient Sandboxing
You can use the launcher to run *any* binary inside the same hardened Antigravity environment using the `--exec` flag:

```bash
antigravity --exec /usr/bin/bash
```

## Implementation Considerations

### Security Model
- **`--unshare-all`**: All namespaces are unshared by default. Only network access (`--share-net`) is retained.
- **Privilege Control**: Adds `CAP_SYS_PTRACE` to allow Antigravity to debug child processes (e.g. compilers or test runners) while maintaining isolation.
- **Sandboxing Relaxations**: Electron requires `--no-sandbox` and `--disable-chromium-sandbox` when running inside a pre-existing `bwrap` container to avoid namespace conflicts.

### Directory Mapping
- **Downloads**: Symlinks `~/download` inside the sandbox to `/data/download` on the host (if available).
- **Home**: The host's `~/.local/sandbox/antigravity` is presented as `$HOME` inside the sandbox, ensuring that configuration files (like `.gitconfig` or `.ssh`) created within the app are persistent but isolated from the real host home.

