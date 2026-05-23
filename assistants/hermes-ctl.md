# Hermes Agent Management Guide

`hermes-ctl` is a management wrapper for the `hermes-agent` messaging gateway. It provides a standardized interface for installation, configuration, and service lifecycle management using `systemd` user units.

- **Source Code**: [GitHub - NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)
- **Arch/AUR Packages**: `hermes-agent` (AUR, standard source), `hermes-agent-git` (AUR, latest git source), `hermes-agent-desktop-bin` (AUR, desktop prebuilt binary).

## Commands

`hermes-ctl` supports all standard management operations. For detailed command reference and sandboxing path defaults, see [Standard Control Wrappers](../README.md#standard-control-wrappers-assistant-ctl).

## Installation

```bash
./assistants/hermes-ctl install --no-start
```

to set up the home directory (`~/.local/sandbox/hermes`) and register the systemd user service without starting it.

### Set Environment

Run `./assistants/hermes-ctl edit` (or edit `~/.config/systemd/user/hermes-gateway.env`) to configure necessary provider environment variables (e.g. `OPENROUTER_API_KEY`).

#### Switch to Local Inference & Qwen3

Set `OPENAI_API_BASE=http://localhost:50080/v1` and `OPENAI_API_KEY=unused`. Then, configure the default model to `qwen3` in the Setup Wizard or Web UI.

### Setup Wizard

Run `./assistants/hermes-ctl exec setup` to launch the interactive configuration setup.

### Start & Verify

Start the service with `./assistants/hermes-ctl start`. Monitor its logs via `./assistants/hermes-ctl logs -f` and access the Web UI at `http://localhost:9119`.


### OpenClaw Migration

Hermes supports importing configuration from an existing OpenClaw setup. To migrate your setup, run:
```bash
./assistants/hermes-ctl exec claw migrate
```
This utility will parse your legacy config formats and migrate them to the Hermes gateway structure.


## Configuration & Ports

- **Default Ports**:
  - **Gateway API (OpenAI-compatible)**: `8642`
  - **Dashboard Web UI**: `9119`
- **Configuration File**: Environment variables and key secrets are managed in `~/.config/systemd/user/hermes-gateway.env`.

## Signal Channel Configuration

Hermes includes native support for the Signal messaging channel, interfacing with a locally running `signal-cli` daemon.

### Configuration

Add the following environment variables to `~/.config/systemd/user/hermes-gateway.env` (via `./assistants/hermes-ctl edit`):

```bash
# Enable Signal by supplying the account phone number and daemon endpoint
SIGNAL_ACCOUNT="+1234567890"  # Your registered Signal phone number
SIGNAL_HTTP_URL="http://localhost:50888"  # Local signal-cli HTTP daemon port

# Optional Access Control Allowlists
SIGNAL_ALLOWED_USERS="+1987654321,+1555000111" # Comma-separated allowed numbers or UUIDs ("*" to allow all DMs)
SIGNAL_GROUP_ALLOWED_USERS="group_id_1,group_id_2" # Comma-separated allowed group IDs ("*" to allow all groups)
```

Ensure the local `signal-cli` daemon is running. Hermes will automatically connect, stream inbound messages via Server-Sent Events (SSE), and reply via JSON-RPC.

## Search, Retrieval & Embedding Configuration

Hermes supports built-in SQLite-based SessionDB/State management, Full-Text Search (FTS5), vector search using the `sqlite-vec` extension, and integrations with external vector databases and memory frameworks.

### Configuration

Add the following environment variables to `~/.config/systemd/user/hermes-gateway.env` (via `./assistants/hermes-ctl edit`):

```bash
# Vector Database & Memory Backend Selection
# Options: "sqlite" (default), "qdrant", "chroma"
HERMES_VECTOR_DB="sqlite"

# External Vector Database Credentials (if using qdrant/chroma)
QDRANT_URL="http://localhost:6333"
QDRANT_API_KEY=""
CHROMA_URL="http://localhost:8000"

# External Memory & RAG Frameworks (optional)
# Supports Mem0, Honcho, Supermemory, RetainDB
MEM0_API_KEY="your-mem0-key"
HONCHO_API_KEY="your-honcho-key"

# Embedding Provider Configuration
# Options: "openai", "cohere", "jina", "voyage", "local", "ollama"
HERMES_EMBEDDING_PROVIDER="local"
HERMES_EMBEDDING_MODEL="text-embedding-3-small"

# Local Inference Endpoint (llama.cpp or Ollama)
# Route to local-inference (port 50080) for system-wide local embeddings
EMBEDDING_API_BASE="http://localhost:50080/v1"
EMBEDDING_API_KEY="unused"
```

### Reranking Configuration

Hermes supports reranking via auxiliary model slots and the QMD hybrid retrieval engine. Configure the reranker endpoint to point to the local-inference server:

```bash
# Reranking Provider Configuration
# Options: "local", "cohere", "jina", "disabled"
HERMES_RERANK_PROVIDER="local"

# Local reranker endpoint (served by local-inference on port 50080)
HERMES_RERANK_URL="http://localhost:50080/v1/rerank"
HERMES_RERANK_MODEL="qwen3-reranker"

# Number of top candidates to rerank after initial retrieval
HERMES_RERANK_TOP_K=30
```

## Speech-to-Text Integration

Hermes automatically transcribes incoming voice messages (from Signal, Telegram, Discord, etc.) using its transcription tools. You can route these requests to the local `local-speech-to-text` service.

### Configuration

Add the following environment variables to `~/.config/systemd/user/hermes-gateway.env` (via `./assistants/hermes-ctl edit`):

```bash
# Set provider to openai and point base URL to local-speech-to-text service
STT_OPENAI_BASE_URL="http://localhost:50090/v1"
STT_OPENAI_MODEL="whisper"
VOICE_TOOLS_OPENAI_KEY="dummy"  # Required placeholder to activate the provider
```

Alternatively, you can configure the provider directly in your `config.yaml`:

```yaml
stt:
  enabled: true
  provider: "openai"
  openai:
    api_key: "dummy"
    base_url: "http://localhost:50090/v1"
    model: "whisper"
```


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

4. **Strict Filesystem Isolation**
   - **Property Set**: `ProtectSystem=strict` and a tmpfs-mounted `$HOME` directory (`TemporaryFileSystem=%h`).
   - **Rationale**: Redirection of `HOME` to `~/.local/sandbox/hermes` ensures that subprocesses do not write to the host user's real home. The persistent home, `~/agent-shared`, and `AGENT_PRIVATE_MOUNTS` are bind-mounted read-write, while other directories are read-only.

5. **Container Backend Support**
   - **Warning**: If using docker or podman as a terminal backend inside the gateway, `NoNewPrivileges=yes` and `PrivateDevices=yes` must be relaxed, and access to `/dev/fuse` and namespace capabilities must be permitted.
