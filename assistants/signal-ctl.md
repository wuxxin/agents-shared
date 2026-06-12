# Signal CLI Management Guide

`signal-ctl` manages `signal-cli` as a background daemon and provides an optional REST API wrapper for integration with other agents.

- **Source Code**: 
  - `signal-cli`: [GitHub - AsamK/signal-cli](https://github.com/AsamK/signal-cli)
  - `signal-cli-rest-api`: [GitHub - bbernhard/signal-cli-rest-api](https://github.com/bbernhard/signal-cli-rest-api)
- **Arch/AUR Package**:
  - `signal-cli` (AUR / Official, Java-based commandline interface)
  - `signal-cli-bin` (AUR, precompiled binary distribution)
  - `signal-cli-git` (AUR, latest git build)
  - and (optional):
    - `signal-cli-rest-api-git` (private package `signal-cli-rest-api` in repo https://github.com/wuxxin/aur-packages , Go-based REST API wrapper)

## Installation

```bash
./assistants/signal-ctl install [--no-start] [--new-config]
```

This command:
1. Initializes `~/.local/sandbox/signal-cli`.
2. Generates environment files for both the CLI daemon and the REST API.
3. Configures a JSON-RPC bridge.
4. Enables both services (`signal-cli.service` and `signal-rest-api.service`) but does not start them.

## Account Setup

Before starting the service, you must link an account. Run the interactive shell in the sandbox environment:

```bash
./assistants/signal-ctl shell
```

Choose one of the following methods:

### Method A: Link an Existing Account (Recommended)
This links the daemon to your existing Signal account on your mobile phone as a secondary linked device:

```bash
# Link the account (this will output a QR code in the terminal)
signal-cli link --name "this-linked-device-name" | tee >(head -1 | qrencode -t ANSIUTF8 >&2)
```
Scan the QR code with your phone's Signal app (**Settings -> Linked Devices -> Add Device**).

```bash
# Exit the sandbox shell
exit

# Configure the phone number in the environment file
./assistants/signal-ctl edit
# (Set SC_ACCOUNT=+your_phone_number, then save and exit)

# Start services
./assistants/signal-ctl start
```

## Commands

| Command | Description |
|---|---|
| `install [--no-start] [--new-config]` | Full dual-service setup (do not start service if `--no-start` is specified, force overwrites with defaults if `--new-config` is specified). |
| `uninstall` | Stops and removes services (preserves account data). |
| `edit` | Opens both `.env` files and restarts services on exit. |
| `logs [args...]` | Combined logs for the daemon and the REST API. Pass `-f` to tail/follow. Supports any `journalctl` options. |
| `exec` | Run `signal-cli` commands (e.g. `listGroups`) in the sandbox. |
| `shell` | Interactive shell for manual account management. |
| `relink <device-name>` | Link an account and display QR code (passes name of link for Signal GUI). |
| `test [--interactive]` | Checks endpoints (REST, RPC HTTP, UNIX socket) and lists accounts. With `--interactive`, polls the REST API for a test message sent by the user. |

## Implementation Considerations

### Architecture
- **Secure Local Socket**: Runs the Java-based `signal-cli` as a daemon exposing a UNIX domain socket (`~/.local/sandbox/signal-cli/signal.sock`) for secure local IPC, with TCP (port 50887) and HTTP (port 50888) JSON-RPC interfaces disabled by default. Leftover socket files are automatically cleaned up prior to daemon start and upon stopping to ensure reliable startup and recreation.
- **Optional REST API**: A Go-based `signal-cli-rest-api` (HTTP port 50889) can be enabled/disabled via `SIGNAL_REST_API_ENABLED`. It can be secured with token-based authentication using `AUTH_TOKEN`.
- **Communication**: The REST API connects to the daemon via the Unix Domain Socket file, ensuring no raw TCP port is exposed.

### Security & Sandboxing

- **Centralized Sandboxing**: All systemd security and namespace options are centralized in the `get_shared_options` function within `signal-ctl`. This ensures that the persistent background service (`signal-cli.service`) and any transient runs (`exec` / `shell` commands) run with identical sandbox profiles, preventing configuration drift.
- **Hardening**: Runs with a very strict profile including `ProtectSystem=strict`, `TemporaryFileSystem=%h` (transient home mount point), and `RestrictNamespaces=yes`.
- **JVM Requirements**: `MemoryDenyWriteExecute` is **intentionally omitted** because the Java Virtual Machine requires writable and executable memory mappings for its JIT compiler.
- **Isolation**: The data directory `~/.local/sandbox/signal-cli` is bind-mounted, but the rest of the home directory is hidden.
- **Process Isolation**: Confinement is tightened with `ProtectProc=invisible`, `ProcSubset=pid`, and restrictive system call filtering (`SystemCallArchitectures=native`).

### Configuration
- `signal-cli.env`: Controls the phone number (`SC_ACCOUNT`), UNIX socket path (`SC_SOCKET_PATH`), optional TCP/HTTP host and ports (`SC_HOST`, `SC_TCP_PORT`, `SC_HTTP_PORT`), and extra flags (e.g. `--ignore-stories`).
- `signal-api.env`: Controls the REST API bind address, `MODE=json-rpc`, security token (`AUTH_TOKEN`), and `SIGNAL_REST_API_ENABLED`.
