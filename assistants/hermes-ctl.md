# Hermes Control Guide

This guide describes configuration, onboarding, and integration features specific to the Hermes Agent Gateway.

For shared commands, variable expansion rules, sidecars supervision, temporary file cleanups, and unified sandboxing profiles, see the general [Agent Service Guide](agents-ctl.md).

- **Source Code**: [GitHub - NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)
- **Arch/AUR Packages**: `hermes-agent` (AUR, standard source), `hermes-agent-git` (AUR, latest git source), `hermes-agent-desktop-bin` (AUR, desktop prebuilt binary).

---

## Agent-Specific Defaults

- **Sandbox Directory:** `~/.local/sandbox/hermes`
- **Home Directory (`HERMES_HOME`):** `~/.local/sandbox/hermes/.hermes`
- **Default Workspace Path:** `~/.local/sandbox/hermes/.hermes/workspace`
- **Bootstrap Environment Config:** `~/.config/systemd/user/hermes-gateway.env` (systemd service environment)
- **Local Application Secrets Override:** `~/.local/sandbox/hermes/.hermes/.env` (stores local secrets and environment overrides)
- **Main Settings Configuration:** `~/.local/sandbox/hermes/.hermes/config.yaml` (sources main settings for models, toolsets, memory providers)
- **Gateway API Port:** [8642](http://localhost:8642/)
- **Dashboard Web UI Port:** [9119](http://localhost:9119/)

---

## Environment Overrides & Secret Configuration

Hermes supports a two-stage environment variable resolution order to allow clean separation of bootstrap variables and local keys/secrets:
1. **Systemd Service Environment:** `~/.config/systemd/user/hermes-gateway.env`
2. **Application Environment Override:** `~/.local/sandbox/hermes/.hermes/.env`

The application override file is loaded **after** the systemd service configuration. Any duplicate variables declared in both files will prioritize the values set in the application `.env` file (e.g. `OPENAI_API_KEY`, custom ports, or paths).

Both files are opened automatically when executing the `./assistants/hermes-ctl edit` command.

---

## Centralized Defaults (`DEFAULT_*` Prefix)
To prevent configuration drift, all defaults are centralized as internal script constants (`DEFAULT_*` prefix) in [hermes-ctl](file:///home/wuxxin/agent-shared/code/agents-shared/assistants/hermes-ctl).
*   **Why are they prefixed with `DEFAULT_*`?**
    The wrapper script prefix indicates these are script-level fallback values. When you run `./assistants/hermes-ctl install`, these constants are written as standard environment variables (without the `DEFAULT_` prefix) into `~/.config/systemd/user/hermes-gateway.env`. If the env file does not override a variable, the script falls back to the corresponding `DEFAULT_*` constant.

---

## Local Split Services Endpoints
Hermes defaults to connecting to local hardware-accelerated services rather than remote cloud providers. The default endpoints written to the environment are:

| Service | Port | Endpoint / URL | Default Model | Environment Variables |
| :--- | :--- | :--- | :--- | :--- |
| **Local Chat** | `50080` | `http://localhost:50080/v1` | `qwen3-chat` | `OPENAI_API_BASE`, `OPENAI_API_KEY` |
| **Local Embeddings** | `50082` | `http://localhost:50082/v1` | `qwen3-embedding` | `EMBEDDING_API_BASE`, `EMBEDDING_API_KEY`, `HERMES_EMBEDDING_PROVIDER`, `HERMES_EMBEDDING_MODEL` |
| **Local Reranker** | `50086` | `http://localhost:50086/v1/rerank` | `qwen3-reranker` | `HERMES_RERANK_URL`, `HERMES_RERANK_PROVIDER`, `HERMES_RERANK_MODEL`, `HERMES_RERANK_TOP_K` |
| **Local Speech-to-Text (STT)** | `50090` | `http://localhost:50090/v1` | `whisper-1` | `STT_OPENAI_BASE_URL`, `STT_OPENAI_MODEL`, `VOICE_TOOLS_OPENAI_KEY` |
| **Local Text-to-Speech (TTS)** | `50095` | `http://localhost:50095/v1` | `qwen3-tts` | `TTS_OPENAI_BASE_URL`, `TTS_OPENAI_MODEL` |
| **Local Image Gen** | `50100` | `http://localhost:50100/v1` | `txt2img` | `IMAGE_OPENAI_BASE_URL`, `IMAGE_OPENAI_MODEL` |

### Provider Cost Structure
For tracking token usage and cost guardrails, local model costs (matching the `openai/qwen3` rates in `zeroclaw-ctl`) are:
- **Input Tokens**: $1.50 per Million tokens
- **Output Tokens**: $9.00 per Million tokens
- **Cached Input Tokens**: $0.15 per Million tokens
- **Safety thresholds**: Triggers expensive-model warning if input > $20.00/M or output > $100.00/M.

---

## Signal Channel Configuration & User Binding

Hermes includes native support for the Signal messaging channel, interfacing with a locally running `signal-cli` daemon.

### User and Agent Binding
1. **Signal Account**: Set `SIGNAL_ACCOUNT="+1234567890"` to specify the registered Signal number used by the bot itself.
2. **User Binding**: Set `SIGNAL_ALLOWED_USERS="+0000000000"` to specify the owner's phone number or UUID. Any message from this allowed number is authenticated as the owner.
3. **Agent Binding**: All incoming messages from the bound user are automatically routed to the default agent instance (`default`), storing conversations and context in the default workspace path: `/home/wuxxin/.local/sandbox/hermes/.hermes/agents/default/workspace`.

Add the following to `~/.config/systemd/user/hermes-gateway.env` (via `./assistants/hermes-ctl edit`):
```bash
# Enable Signal by supplying the account phone number and daemon endpoint
SIGNAL_ACCOUNT="+1234567890"               # The bot's Signal phone number
SIGNAL_HTTP_URL="http://localhost:50889"   # Local signal-cli REST API wrapper port
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

## Setup Wizard

Run `./assistants/hermes-ctl exec setup` to launch the interactive configuration setup.

### OpenClaw Migration

Hermes supports importing configuration from an existing OpenClaw setup. To migrate your setup, run:
```bash
./assistants/hermes-ctl exec claw migrate
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

4. **Container Backend Support**
   - **Warning**: If using docker or podman as a terminal backend inside the gateway, `NoNewPrivileges=yes` and `PrivateDevices=yes` must be relaxed, and access to `/dev/fuse` and namespace capabilities must be permitted.
