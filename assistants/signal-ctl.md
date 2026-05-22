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
./assistants/signal-ctl install
```

This command:
1. Initializes `~/.local/share/signal-cli`.
2. Generates environment files for both the CLI daemon and the REST API.
3. Configures a JSON-RPC bridge.
4. Enables and starts both services: `signal-cli.service` and `signal-rest-api.service`.

## Account Setup

Before starting the service, you must link an account. Run the interactive shell in the sandbox environment:

```bash
./assistants/signal-ctl stop
./assistants/signal-ctl shell
```

Choose one of the following methods:

### Method A: Link an Existing Account (Recommended)
This links the daemon to your existing Signal account on your mobile phone as a secondary linked device:

```bash
# Link the account (this will output a QR code in the terminal)
signal-cli --config "$SC_CONFIG_DIR" link --name "noben" | \
    tee >(head -1 | qrencode -t ANSIUTF8 >&2)
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
| `install` | Full dual-service setup. |
| `uninstall` | Stops and removes services (preserves account data). |
| `edit` | Opens both `.env` files and restarts services on exit. |
| `logs [args...]` | Combined logs for the daemon and the REST API. Pass `-f` to tail/follow. Supports any `journalctl` options. |
| `exec` | Run `signal-cli` commands (e.g. `listGroups`) in the sandbox. |
| `shell` | Interactive shell for manual account management. |

## Implementation Considerations

### Architecture
- **Dual Interfaces**: Runs the Java-based `signal-cli` as a daemon with both TCP (port 50887) and HTTP (port 50888) JSON-RPC interfaces enabled.
- **Optional REST API**: A Go-based `signal-cli-rest-api` (HTTP port 50889) can be enabled/disabled via `SIGNAL_REST_API_ENABLED`.
- **Communication**: The REST API connects to the daemon via the TCP JSON-RPC interface on port 50887.

### Security & Sandboxing

- **Centralized Sandboxing**: All systemd security and namespace options are centralized in the `get_shared_options` function within `signal-ctl`. This ensures that the persistent background service (`signal-cli.service`) and any transient runs (`exec` / `shell` commands) run with identical sandbox profiles, preventing configuration drift.
- **Hardening**: Runs with a very strict profile including `ProtectSystem=strict`, `TemporaryFileSystem=%h` (transient home mount point), and `RestrictNamespaces=yes`.
- **JVM Requirements**: `MemoryDenyWriteExecute` is **intentionally omitted** because the Java Virtual Machine requires writable and executable memory mappings for its JIT compiler.
- **Isolation**: The data directory `~/.local/share/signal-cli` is bind-mounted, but the rest of the home directory is hidden.
- **Process Isolation**: Confinement is tightened with `ProtectProc=invisible`, `ProcSubset=pid`, and restrictive system call filtering (`SystemCallArchitectures=native`).

### Configuration
- `signal-cli.env`: Controls the phone number (`SC_ACCOUNT`), TCP/HTTP ports (`SC_TCP_PORT`, `SC_HTTP_PORT`), and extra flags (e.g. `--ignore-stories`).
- `signal-api.env`: Controls the REST API bind address, `MODE=json-rpc`, and `SIGNAL_REST_API_ENABLED`.
