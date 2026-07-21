# Hermes Control Guide

This guide describes configuration, onboarding, and integration features specific to the Hermes Agent Gateway.

For shared commands, variable expansion rules, sidecars supervision, temporary file cleanups, and unified sandboxing profiles, see the general [Agent Service Guide](agents-ctl.md).

- **Source Code**: [GitHub - NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)
- **Arch/AUR Packages**: `hermes-agent` (AUR, standard source), `hermes-agent-git` (AUR, latest git source), `hermes-agent-desktop-bin` (AUR, desktop prebuilt binary).

---

## Profile Directory Layout & Defaults

By default, Hermes is configured to use the named profile **`assistant`** (`DEFAULT_AGENT_PROFILE="assistant"`). The file layout is structured as follows:

- **Sandbox Home Directory:** `~/.local/sandbox/hermes`
- **Hermes Home Directory (`HERMES_HOME`):** `~/.local/sandbox/hermes/.hermes` (always points to the base `.hermes` directory and does NOT change with active profile)
- **Active Profile File:** `~/.local/sandbox/hermes/.hermes/active_profile` (written on install to make the profile the sticky default)
- **Active Profile Root (`AGENT_PROFILE_ROOT`):** `~/.local/sandbox/hermes/.hermes/profiles/assistant`
- **Active Profile Workspace (`AGENT_WORKSPACE`):** `~/.local/sandbox/hermes/.hermes/profiles/assistant/workspace` (where the service starts and transient runs are run)
- **Profile Config Overrides:** `~/.local/sandbox/hermes/.hermes/profiles/assistant/config.yaml`
- **Profile Secret Overrides:** `~/.local/sandbox/hermes/.hermes/profiles/assistant/.env`
- **Profile SOUL.md**: `~/.local/sandbox/hermes/.hermes/profiles/assistant/SOUL.md`
- **Profile profile.yaml**: `~/.local/sandbox/hermes/.hermes/profiles/assistant/profile.yaml`
- **Gateway API Port:** [8642](http://localhost:8642/)
- **Dashboard Web UI Port:** [9119](http://localhost:9119/)

---

## Environment Overrides & Secret Configuration

Hermes resolves configuration settings using a structured environment variable resolution order to allow clean separation of bootstrap variables and local keys/secrets. Environment loading is completely consistent across the **installed systemd service**, **transient execution runner (`exec`, `run`, `shell`)**, and **fallback direct execution** modes:

### Environment Sourcing Order

1. **Systemd Bootstrap Environment:** `~/.config/systemd/user/hermes-gateway.env`
   - Defines systemd service bootstrap paths and profile selection variables (`AGENT_PROFILE`, `AGENT_PROFILE_ROOT`, `AGENT_WORKSPACE`, `HERMES_SANDBOX_HOME`, `HERMES_HOME`). Sourced on startup/wrapper initialization.
2. **Profile Application Environment:** `~/.local/sandbox/hermes/.hermes/profiles/<profile>/.env`
   - Stores the active profile's local keys and secret overrides (e.g. `OPENAI_API_KEY`, `HERMES_YOLO_MODE`, etc.). Sourced after the bootstrap environment; any duplicate variables declared here override previous stages.

### Consistency Across Run Modes

- **Service Run**: The systemd service uses `EnvironmentFile=` directives to load the bootstrap env file first, followed by the profile-specific env file.
- **Transient Run (`exec`/`run`/`shell` under systemd)**: Translates local paths using Bubblewrap mappings, and feeds the resolved directories as transient options (`-p Environment=...`, `-p EnvironmentFile=...`) to `systemd-run` in the exact same loading order.
- **Fallback Direct Run (outside systemd)**: Sources the files in sequence (`source <bootstrap-env>`, then `source <profile-env>`), exports variables (`export PATH`, `export HERMES_HOME`, etc.), and changes directory to the workspace.

> [!IMPORTANT]
> - Command-line overrides (e.g., executing `AGENT_PROFILE=test ./assistants/hermes-ctl run env`) take precedence over the settings loaded from systemd's bootstrap `ENV_FILE`. If `AGENT_PROFILE` is overridden, the wrapper clears any static profile paths loaded from systemd and regenerates them dynamically.
> - Core systemd bootstrap variables (`AGENT_PROFILE`, `AGENT_PROFILE_ROOT`, `AGENT_WORKSPACE`, `HERMES_SANDBOX_HOME`, and `HERMES_HOME`) are resolved prior to sourcing the local `.env` files and **cannot** be modified or overridden by the profile's `.env`.

Executing the `./assistants/hermes-ctl edit` command automatically opens these active config files:
1. Systemd User Env Config (`~/.config/systemd/user/hermes-gateway.env`)
2. Profile-specific Configuration (`~/.local/sandbox/hermes/.hermes/profiles/assistant/config.yaml`)
3. Profile-specific Environment overrides (`~/.local/sandbox/hermes/.hermes/profiles/assistant/.env`)

## Workspace & CWD Propagation

To ensure that the agent, its sidecars (like the dashboard), and any spawned background processes (like the `prompt-size` diagnostics) correctly agree on the project's working directory:
- **WorkingDirectory Configuration**: For the systemd service and fallback direct execution, the working directory (cwd) is dynamically resolved to the value of `AGENT_WORKSPACE` (which defaults to `%h/.local/sandbox/hermes/.hermes/workspace`).
- **TERMINAL_CWD Propagation**: The environment variable `TERMINAL_CWD` is automatically set to `AGENT_WORKSPACE`'s resolved value at the systemd service/wrapper level (`Environment=TERMINAL_CWD=...` or `export TERMINAL_CWD="..."`).
- **Dotenv Default**: The default `.env` template writes `TERMINAL_CWD="${AGENT_WORKSPACE}"` to ensure shell-based executions resolve it properly.

This propagation is crucial for WebUI dashboard actions (such as computing the prompt size via `action-prompt-size`). It ensures that background diagnostic subprocesses (which are spawned in `/opt/hermes-agent` or `/opt/hermes`) can resolve project-local files (e.g., `AGENTS.md` and `.cursorrules`) by reading `TERMINAL_CWD` from their inherited environment instead of falling back to scan the installation directory.

## Setup Wizard

Run `./assistants/hermes-ctl exec setup` to launch the interactive configuration setup.

```bash
for i in agent_browser camofox cua_driver kittentts piper ddgs langfuse; do hermes tools post-setup $i; done
```

### OpenClaw Migration

Hermes supports importing configuration from an existing OpenClaw setup. To migrate your setup, run:
```bash
./assistants/hermes-ctl exec claw migrate
```

## Local Split Services Endpoints
Hermes defaults to connecting to local hardware-accelerated services rather than remote cloud providers. The default endpoints are:

| Service | Port | Endpoint / URL | Default Model | 
| :--- | :--- | :--- | :--- |
| **Local Chat** | `50080` | `http://localhost:50080/v1` | `qwen3-chat` | 
| **Local Embeddings** | `50082` | `http://localhost:50082/v1` | `qwen3-embedding` | 
| **Local Reranker** | `50086` | `http://localhost:50086/v1/rerank` | `qwen3-reranker` | 
| **Local Speech-to-Text (STT)** | `50090` | `http://localhost:50090/v1` | `whisper-1` |
| **Local Text-to-Speech (TTS)** | `50095` | `http://localhost:50095/v1` | `qwen3-tts` |
| **Local Image Gen** | `50100` | `http://localhost:50100/v1` |

### Local Router Client Identification Headers

Hermes includes identification headers (`X-Client-ID: hermes` and `X-Agent-ID: hermes`) in `default_headers` / `extra_headers` inside `config.yaml` so that inference calls routed through `local-router` (port 51080) are attributed to `hermes` in Prometheus metrics and token usage tracking.

### Provider Cost Structure
For tracking token usage and cost guardrails, local model costs (matching the `openai/qwen3` rates in `zeroclaw-ctl`) are:
- **Input Tokens**: $1.50 per Million tokens
- **Output Tokens**: $9.00 per Million tokens
- **Cached Input Tokens**: $0.15 per Million tokens
- **Safety thresholds**: Triggers expensive-model warning if input > $20.00/M or output > $100.00/M.

---

## Signal Channel Configuration & User Binding

Hermes includes native support for the Signal messaging channel, interfacing with a locally running `signal-cli` daemon in JSON-RPC over http.

### User and Agent Binding
1. **Signal Account**: Set `SIGNAL_ACCOUNT="+1234567890"` to specify the registered Signal number used by the bot itself.
2. **User Binding**: Set `SIGNAL_ALLOWED_USERS="+0000000000"` to specify the owner's phone number or UUID. Any message from this allowed number is authenticated as the owner.
3. **Agent Binding**: All incoming messages from the bound user are automatically routed to the default agent instance (`default`), storing conversations and context in the default workspace path: `/home/wuxxin/.local/sandbox/hermes/.hermes/agents/default/workspace`.

Add the following to `~/.config/systemd/user/hermes-gateway.env` (via `./assistants/hermes-ctl edit`):
```bash
# Enable Signal by supplying the account phone number and daemon endpoint
SIGNAL_ACCOUNT="+1234567890"               # The bot's Signal phone number
SIGNAL_HTTP_URL="http://localhost:50888"   # Local signal-cli JSON-RPC over HTTP
SIGNAL_ALLOWED_USERS="+0000000000"         # Comma-separated allowed users (owner binding)
```

---

## YOLO Mode
To execute terminal commands or code blocks without prompting the operator for confirmation, you can enable **YOLO Mode**:
- **Environment Setting**: Set `HERMES_YOLO_MODE="true"` in your env file to bypass the approval gate globally.
- **TUI Command Toggle**: Alternatively, type `/yolo` directly in the chat window to toggle yolo mode for the current session.

---

## Memory Backend & OpenCode Research Options

Hermes implements memory as profile-scoped plugins. Select your preferred plugin by setting `memory.provider` in `~/.local/sandbox/hermes/.hermes/config.yaml`.

### 1. SQLite (Default)
- **Description**: Uses a local SQLite database for vector retrieval and Full-Text Search (FTS5). Stored in `$HERMES_HOME/memory.db`.
- **Arch Linux Dependencies**: None (uses standard Python `sqlite3`).
- **Configuration**:
  ```yaml
  memory:
    provider: sqlite
  ```

### 2. Holographic Fact Store
- **Description**: Extracts atomic facts from conversations with entity resolution, trust scoring, and compositional retrieval using Holographic Reduced Representations (HRR).
- **Arch Linux Dependencies**: Requires `numpy` (`pacman -S python-numpy` or `pip install numpy`).
- **Configuration**:
  Add to `~/.local/sandbox/hermes/.hermes/config.yaml`:
  ```yaml
  memory:
    provider: holographic
  plugins:
    hermes-memory-store:
      db_path: /home/wuxxin/.local/sandbox/hermes/.hermes/memory_store.db
      auto_extract: true
      default_trust: 0.5
      min_trust_threshold: 0.3
  ```

### 3. OpenViking
- **Description**: Tiered hierarchical context database organizing knowledge into `viking://` URIs.
- **Arch Linux Dependencies**: Requires `httpx` (`pip install httpx` or `pacman -S python-httpx`).
- **External Server Requirement**: Requires a running OpenViking server. Check details on the official GitHub repository: [volcengine/OpenViking](https://github.com/volcengine/OpenViking).
- **Configuration**:
  Configure variables in the env file:
  ```bash
  OPENVIKING_ENDPOINT="http://127.0.0.1:1933"
  OPENVIKING_ACCOUNT="default"
  OPENVIKING_USER="default"
  ```
  Set in `~/.local/sandbox/hermes/.hermes/config.yaml`:
  ```yaml
  memory:
    provider: openviking
  ```

### 4. ByteRover
- **Description**: Context tree with fuzzy search and LLM-driven query strategies.
- **Arch Linux Dependencies**: Requires `nodejs` and `npm` (`pacman -S nodejs npm`) to install `byterover-cli`.
- **CLI setup**: `npm install -g byterover-cli` or `curl -fsSL https://byterover.dev/install.sh | sh`.
- **Configuration**:
  Configure env variables:
  ```bash
  BRV_API_KEY="your-optional-api-key"
  ```
  Set in `~/.local/sandbox/hermes/.hermes/config.yaml`:
  ```yaml
  memory:
    provider: byterover
  ```

### 5. Hindsight
- **Description**: Long-term memory graph with temporal decay and multi-strategy recall.
- **Self-Hosting Options**:
  - **Local Embedded Mode**: Auto-spawns a local PostgreSQL background daemon. Installs on first use and shuts down after 5 minutes of idle time. Requires: `pip install hindsight-all` (downloads ~200MB, requires a valid LLM key).
  - **Local External Mode**: Connect to a running self-hosted instance or Docker container on port 8888.
- **Configuration**:
  ```yaml
  memory:
    provider: hindsight
  ```
  And specify in env file:
  ```bash
  HINDSIGHT_MODE="local_embedded"    # or "local_external"
  HINDSIGHT_API_URL="http://localhost:8888" # (if using local_external)
  ```

### 6. Supermemory
- **Description**: Semantic memory with profile recall and automatic conversation ingestion at the end of sessions.
- **Self-Hosting Options**: Deploy the Supermemory server stack (Node/Go) locally or in Docker. Note that the core plugin hits `https://api.supermemory.ai/v4/conversations` by default; custom hosting requires setting up a reverse proxy or patching the plugin endpoint.
- **Configuration**:
  ```yaml
  memory:
    provider: supermemory
  ```
  And specify in env file:
  ```bash
  SUPERMEMORY_API_KEY="your-api-key"
  ```


---

## Implementation & Security Considerations

### Centralized Sandbox Options
To guarantee parity across all execution modes, `hermes-ctl` centralizes its systemd sandboxing properties in a single helper function (`get_shared_options`). The background service (installed via `install`), the transient command runner (`exec`), and the interactive shell (`shell`) all inherit the exact same filesystem, network, and security restrictions.

### Sandboxing Profile
Hermes utilizes a **Relaxed Namespaces Profile** for systemd isolation. Based on auditing the packaging and runtime configuration, these permissions are required:

1. **Namespace Support (Bubblewrap / Docker Runtimes)**
   - **Properties Omitted**: `ProtectProc=invisible`, `ProcSubset=pid`, and `RestrictNamespaces=yes`.
   - **Rationale**: Hermes executes tools and sub-agents that may require user-namespace-based sandboxes (e.g. `bwrap`). Restricting namespaces or procfs traversal inside the systemd service would block this ability.

2. **Writable & Executable Memory (Python JIT & Runtimes)**
   - **Property Set**: `MemoryDenyWriteExecute=no`.
   - **Rationale**: Hermes is written in Python and invokes diverse JIT runtimes or compilers for dynamic tool execution, requiring memory-denied execution filters to be turned off.

3. **Graceful Shutdown & Restarts**
   - **Properties Set**: `KillMode=mixed`, `KillSignal=SIGTERM`, `ExecReload=/bin/kill -USR1 \$MAINPID`, and `TimeoutStopSec=210`.
   - **Rationale**: Allows the gateway to perform a graceful drain of active messaging sessions and correctly handle child processes. Exiting with status `75` (force exit code) triggers systemd restart via `RestartForceExitStatus=75`.

4. **Pseudo-Terminal (PTY) Support & Device Access**
   - **Property Set**: `PrivateDevices=no`.
   - **Rationale**: The WebUI chat tab (`/api/pty`) spawns shell processes using pseudo-terminals (POSIX PTYs). Systemd's `PrivateDevices=yes` removes access to the pseudo-terminal multiplexer (`/dev/ptmx` and `/dev/pts`), causing PTY allocation to fail ("out of pty"). Thus, `PrivateDevices=no` is set to ensure the embedded chat can allocate terminal lines and connect successfully.

5. **Container Backend Support**
   - **Warning**: If using docker or podman as a terminal backend inside the gateway, `NoNewPrivileges=yes` must be relaxed, and access to `/dev/fuse` and namespace capabilities must be permitted.

6. **Systemd/Systemctl Masking**
   - **Property Set**: `InaccessiblePaths=/usr/bin/systemctl /bin/systemctl`.
   - **Rationale**: When running inside the sandboxed user service, the gateway daemon's built-in startup code attempts to reload the unit file via `systemctl`. Because `/run/user/<UID>` is isolated, this call hangs on D-Bus communication. Masking `systemctl` makes it fail fast immediately (causing `shutil.which` to return `None`), ensuring the gateway starts up instantly without any blocking behavior.
