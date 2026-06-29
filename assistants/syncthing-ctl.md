# Confined Syncthing Control Guide

This guide describes configuration and execution options specific to the confined Syncthing user service.

For shared commands, variable expansion rules, and unified sandboxing profiles, see the general [Agent Service Guide](agents-ctl.md).

---

## Service-Specific Defaults

- **Home Directory:** `~/.local/sandbox/syncthing`
- **Configuration Directory (`STCONFDIR`):** `~/.config/syncthing` (with systemd bind-mount mapping to host's `~/.config/syncthing`)
- **Data Directory (`STDATADIR`):** `~/.local/state/syncthing` (with systemd bind-mount mapping to host's `~/.local/state/syncthing`)
- **Configuration File:** `~/.config/syncthing/config.xml`
- **Default Port:** `8384` (default Syncthing Web UI port) and `22000` (default sync port)

---

## Confinement and Mounts

The Syncthing service runs in a confined user-level systemd namespace sandbox. The sandbox uses:
- `SYNCTHING_PRIVATE_MOUNTS`: A space-separated list of folders inside `~/agent-private/` to bind-mount.
- `SYNCTHING_SANDBOX_MOUNTS`: A space-separated list of folders from other sandboxes to expose.
- `SYNCTHING_EXTRA_MOUNTS`: A space-separated list of extra folders to bind-mount (syntax: `host-path:sandbox-path`). By default, this is set to bind-mount the host's `agent-shared` folder:
  ```env
  SYNCTHING_EXTRA_MOUNTS="$HOME/agent-shared:agent-shared"
  ```

---

## Commands

Use the `syncthing-ctl` script to manage the service:

*   **Install service:**
    ```bash
    ./assistants/syncthing-ctl install [--no-start] [--new-config]
    ```
    This generates the systemd user service and environment files, and populates the default config using `syncthing generate` if it doesn't already exist.

*   **Uninstall service:**
    ```bash
    ./assistants/syncthing-ctl uninstall
    ```

*   **Start/Stop/Restart/Status:**
    ```bash
    ./assistants/syncthing-ctl start
    ./assistants/syncthing-ctl stop
    ./assistants/syncthing-ctl restart
    ./assistants/syncthing-ctl status
    ```

*   **Configure service:**
    ```bash
    ./assistants/syncthing-ctl edit
    ```
    This command opens:
    - `~/.config/systemd/user/syncthing.env`
    - `~/.config/syncthing/config.xml`
    - `~/.config/user-tmpfiles.d/syncthing.conf` (or `.disabled`)
    inside the system `$EDITOR` (default: `nano`).

*   **Tail logs:**
    ```bash
    ./assistants/syncthing-ctl logs [-f]
    ```

*   **Run command inside sandbox:**
    ```bash
    ./assistants/syncthing-ctl run <command> [args...]
    ```

*   **Spawn interactive shell in sandbox:**
    ```bash
    ./assistants/syncthing-ctl shell
    ```
