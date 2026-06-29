# Assistant Runtime & Service Management Guide

This document describes the unified runtime, service configuration, and sandboxing architecture shared by all assistant control scripts (`*-ctl`) in this repository.

---

## Shared Control Commands

All `*-ctl` scripts support a standard set of lifecycle, configuration, and execution commands. Each assistant runs within its own systemd user namespace or fallback direct-execution sandbox:

*   **`install [--no-start] [--new-config]`**
    Initializes the assistant's dedicated home directory under `~/.local/sandbox/<agent>`, writes systemd unit files, generates environment templates, and starts the service.
    - `--no-start`: Setup files and register systemd unit without starting the service.
    - `--new-config`: Force-overwrite existing configuration and environment files with repository defaults.
*   **`uninstall`**
    Stops, disables, and removes the systemd user service. Configuration and database stores are preserved.
*   **`start` / `stop` / `restart` / `status`**
    Standard service controls mapped to `systemctl --user`.
*   **`enable` / `disable`**
    Toggles automatic starting of the user service on system boot.
*   **`logs [-f] [args...]`**
    Tails service output using `journalctl --user`.
*   **`edit`**
    Opens the assistant's environment configuration (`~/.config/systemd/user/<agent>.env`) and/or application config files in the system `$EDITOR` (falling back to `nano`). If systemd is running, restarts the service upon editor exit.
*   **`exec <subcommand> [args...]`**
    Executes assistant commands inside the systemd runtime or direct sandbox.
*   **`run <command> [args...]`**
    Executes arbitrary host commands inside the assistant's container/sandbox environment.
*   **`shell`**
    Spawns an interactive bash shell in the assistant's sandboxed environment.

---

## Common Configuration Variables

Configurations are defined in `~/.config/systemd/user/<agent>.env`. The following parameters are unified across all control wrappers:

*   **`AGENT_WORKSPACE`**
    Configures the default folder where the agent reads and writes active workspace data (contexts, notes, files). The default path is agent-specific (e.g., `%h/.local/sandbox/<agent>/.../workspace`).
*   **`AGENT_EXTRA_MOUNTS`**
    A space-separated list of host-to-sandbox bind mounts (syntax: `host-path:sandbox-path`). Host paths can use `$HOME`, `%h`, or `~` prefixes.
    - *Default:* Binds the repository's shared folder: `AGENT_EXTRA_MOUNTS="%h/agent-shared:agent-shared"`.
*   **`AGENT_PRIVATE_MOUNTS`**
    A space-separated list of directories inside `~/agent-private/` to bind-mount into the sandbox (e.g., `AGENT_PRIVATE_MOUNTS="health diary"`).
*   **`AGENT_SANDBOX_MOUNTS`**
    A space-separated list of directories from other assistants' sandboxes to expose (e.g., `AGENT_SANDBOX_MOUNTS="opencode/.cache/opencode"`).
*   **`AGENT_SIDECARS`**
    A space- or semicolon-separated list of background sidecar scripts or daemons to start/stop with the main daemon (e.g., `AGENT_SIDECARS="audionotes"`).
*   **`AGENT_SIDECAR_<NAME>_CMD`**
    The command or path to the sidecar executable (e.g., `AGENT_SIDECAR_AUDIONOTES_CMD="$AGENT_WORKSPACE/scripts/audionotes.sh"`).
*   **`AGENT_SIDECAR_<NAME>_ARGS`**
    Arguments to pass to the sidecar command.
*   **`AGENT_SIDECAR_<NAME>_ENV_REMOVE`**
    Space-separated list of environment variables to filter out from the sidecar.
*   **`AGENT_SIDECAR_<NAME>_ENV_OVERRIDE`**
    Space-separated list of environment overrides specifically for the sidecar process.
*   **`AGENT_TMPFILES_CLEANUP`** (Default: `false`)
    Toggles systemd-tmpfiles directory cleanup rules.

### Generating a Secure Token

To generate a secure, random 32-character alphanumeric token (`0-9A-Za-z`):

*   **Using `/dev/urandom` and `tr` (Standard, no dependencies):**
    ```bash
    tr -dc 'A-Za-z0-9' < /dev/urandom | head -c 32; echo
    ```
*   **Using `openssl` (Base64 filtering):**
    ```bash
    openssl rand -base64 48 | tr -dc 'A-Za-z0-9' | head -c 32; echo
    ```
*   **Using `python3` (Cryptographically secure secrets module):**
    ```bash
    python3 -c "import secrets, string; print(''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32)))"
    ```
*   **Using `pwgen` (If installed on the host):**
    ```bash
    pwgen -s 32 1
    ```

---

## Variable Path Expansion Rules

To make configurations flexible and compatible with both systemd and direct execution fallback environments, path variables inside environment configs are resolved as follows:

1.  **`AGENT_WORKSPACE`**:
    - **Usage**: You can use `$HOME`, `%h`, or `~` to specify the workspace path (e.g., `AGENT_WORKSPACE="$HOME/.local/workspace"`).
    - **Resolution**: Systemd replaces `%h` with the user's home directory. In fallback mode, the wrapper script resolves and expands `$HOME`, `%h`, and `~` to ensure correct directories are created.
2.  **`AGENT_EXTRA_MOUNTS`**:
    - **Usage**: Syntax is `host-path:sandbox-path`. You can use `$HOME`, `%h`, or `~` for the host path (e.g., `AGENT_EXTRA_MOUNTS="$HOME/shared:shared"`).
    - **Resolution**: `$HOME` is expanded when bash sources the environment file. `%h` and `~` are resolved by the wrapper during service file generation and fallback directory checking.
3.  **`AGENT_SIDECAR_<NAME>_CMD` and `AGENT_SIDECAR_<NAME>_ARGS`**:
    - **Usage**: You can use `$AGENT_WORKSPACE`, `$HOME`, `%h`, or `~` (e.g., `AGENT_SIDECAR_AUDIONOTES_CMD="$AGENT_WORKSPACE/scripts/audionotes.sh"`).
    - **Resolution**:
      - Inside systemd, these sidecars run under a bash execution wrapper, so bash resolves `$AGENT_WORKSPACE` and `$HOME` at runtime.
      - During direct execution fallback mode, the wrapper expands `$AGENT_WORKSPACE`, `$HOME`, `%h`, and `~` on the host to run existence validation checks, and passes them to bash's `eval` for runtime evaluation.

---

## Agent Sidecars & Supervisor

Sidecar processes run within the **exact same systemd-confinement/namespaces** (or direct sandbox) as the main gateway daemon. They share the same isolated home directory, bind mounts, network/IPC namespace, and systemd cgroup limits.

### Supervision & Exit Behavior
Sidecar processes are managed via the main service wrapper using an event-driven `wait -n` supervisor.
- If the main daemon fails to start (fails a 2-second initial validation check), the wrapper exits immediately.
- If any sidecar process exits or crashes, the parent shell exits immediately (with code `1`), signaling systemd to tear down the entire control group (cgroup) and automatically restart the service.
- To prevent run-away crash loops, the systemd unit enforces a restart rate limit: if the service undergoes more than **4 continuous restarts within a 40-second interval**, systemd will mark the service as permanently failed and stop attempting to restart it (`StartLimitIntervalSec=40` and `StartLimitBurst=4`).

---

## systemd-tmpfiles Confinement Cleanup

Each assistant supports user-level `systemd-tmpfiles` configurations to clean up temporary, workspace, or staging directories automatically.

### Configuration
1.  Enable cleanup in the environment file:
    ```env
    AGENT_TMPFILES_CLEANUP=true
    ```
2.  Edit cleanup rules using:
    ```bash
    ./assistants/<agent>-ctl edit
    ```
    This command automatically opens the configuration file at `~/.config/user-tmpfiles.d/<service-name>.conf` alongside your environment and config files.

### Workspace Cleanup Example
You can configure cleanup policies (e.g., deleting files older than 24 hours in the monitored voice notes folder) in `~/.config/user-tmpfiles.d/<service-name>.conf`:

```ini
# ~/.config/user-tmpfiles.d/<service-name>.conf
# systemd-tmpfiles configuration for assistant

# Example: Delete all files in workspace/voice-notes/read/ if older than 24 hours
# Type  Path                                                                                    Mode UID  GID  Age  Argument
e       %h/.local/sandbox/<agent>/.../workspace/voice-notes/read                                 -    -    -    24h  -
```

When enabled, the cleanup policy runs immediately on service startup/restart, and integrates with the host user's periodic `systemd-tmpfiles-clean.timer`. When disabled, the configuration file is renamed to `<service-name>.conf.disabled` to prevent systemd's clean timer from running it, while preserving your configuration edits.

---

## Unified Security Sandboxing Profile

To guarantee parity across all execution modes, the wrapper centralizes its systemd sandboxing properties in a single helper function (`get_shared_options`). The background service (installed via `install`), the transient command runner (`exec`), and the interactive shell (`shell`) all inherit the exact same security profile:

1.  **Physical Devices**: `PrivateDevices=yes` is active by default to hide physical hardware devices 
2.  **Strict Filesystem Isolation**: Enforces `ProtectSystem=strict` and a tmpfs-mounted `$HOME` directory (`TemporaryFileSystem=%h`). The persistent directories (`~/.local/sandbox/<agent>`, `~/agent-shared`) are bind-mounted read-write, while the rest of the host filesystem is mounted read-only or hidden and `PrivateTmp=yes` is set to have a unique private temp for the process
3.  **Kernel and IPC constraints**: Enforces kernel module, clock, and tunable protections, lock personality restrictions, and IPC namespaces.
4. 
4.  **NoNewPrivileges**: Enforces `NoNewPrivileges=yes` to prevent escalations.
5.  **Direct Execution Fallback**: If systemd is not running in the current environment (e.g., inside a Bubblewrap container or systemd-free shell), the wrapper automatically falls back to direct execution of the binary under host environment variable overrides, setting `$HOME` to the sandboxed path.

### Strict Confinement Profile
- `ProtectProc=invisible` and `ProcSubset=pid`: Hides other system processes.
- `RestrictNamespaces=yes`: Prevents the creation of new namespaces.
- `MemoryDenyWriteExecute=yes`: Prevents W^X memory mappings (unless specifically required by an interpreter).

### Relaxed Namespaces Profile
Used by agents that orchestrate sub-agents or use tools like Bubblewrap (`bwrap`), Rootless Podman, or Docker for internal sandboxing.
- `RestrictNamespaces=yes` is **omitted** to allow `bwrap` or Podman to create `CLONE_NEWUSER` and `CLONE_NEWNS` unprivileged namespaces.
- `ProtectProc=invisible` and `ProcSubset=pid` are **omitted** so `bwrap` can securely bind its own `/proc` filesystem.
- `NoNewPrivileges=yes` is maintained for modern `bwrap` compatibility.

