# Hermes Control Guide

This guide describes configuration, onboarding, and integration features specific to the Hermes Agent Gateway.

For shared commands, variable expansion rules, sidecars supervision, temporary file cleanups, and unified sandboxing profiles, see the general [Agent Service Guide](agents.md).

- **Source Code**: [GitHub - NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)
- **Arch/AUR Packages**: `hermes-agent` (AUR, standard source), `hermes-agent-git` (AUR, latest git source), `hermes-agent-desktop-bin` (AUR, desktop prebuilt binary).
- ## Agent-Specific Defaults

- **Home Directory:** `~/.local/sandbox/hermes`
- **Default Workspace Path:** `%h/.local/sandbox/hermes/.hermes/agents/default/workspace`
- **Configuration File:** `~/.config/systemd/user/hermes-gateway.env` (environment-based variables configuration)
- **Gateway API Port:** [8642](http://localhost:8642/)
- **Dashboard Web UI Port:** [9119](http://localhost:9119/)


### Setup Wizard

Run `./assistants/hermes-ctl exec setup` to launch the interactive configuration setup.

### OpenClaw Migration

Hermes supports importing configuration from an existing OpenClaw setup. To migrate your setup, run:
```bash
./assistants/hermes-ctl exec claw migrate
```
This utility will parse your legacy config formats and migrate them to the Hermes gateway structure.

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
HERMES_EMBEDDING_MODEL="qwen3-embedding"

# Local Inference Endpoint (llama.cpp or Ollama)
# Route to local-embedding (port 50082) for system-wide local embeddings
EMBEDDING_API_BASE="http://localhost:50082/v1"
EMBEDDING_API_KEY="unused"
HERMES_EMBEDDING_PROVIDER="local"
HERMES_EMBEDDING_MODEL="qwen3-embedding"

# Reranker endpoint (llama-server on port 50086)
HERMES_RERANK_URL="http://localhost:50086/v1/rerank"
HERMES_RERANK_PROVIDER="local"
HERMES_RERANK_MODEL="qwen3-reranker"
HERMES_RERANK_TOP_K=30

# Speech-to-Text endpoint (whisper-server on port 50090)
STT_OPENAI_BASE_URL="http://localhost:50090/v1"
STT_OPENAI_MODEL="whisper-1"
VOICE_TOOLS_OPENAI_KEY="dummy"
```

---

## Text-to-Speech Integration

Hermes does not have a built-in TTS provider in the core service config, but it supports outbound speech using custom command-type tools. You can configure a tool that makes an OpenAI-compatible request to the local TTS service on port `50095`:

```bash
# Example curl command for local TTS synthesis (sends text to port 50095 and saves/plays the audio)
curl -X POST "http://localhost:50095/v1/audio/speech" \
  -H "Content-Type: application/json" \
  -d '{"model": "qwen3-tts", "input": "Hello from Hermes", "voice": "default"}' \
  -o "output.wav"
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


4. **Container Backend Support**
   - **Warning**: If using docker or podman as a terminal backend inside the gateway, `NoNewPrivileges=yes` and `PrivateDevices=yes` must be relaxed, and access to `/dev/fuse` and namespace capabilities must be permitted.
