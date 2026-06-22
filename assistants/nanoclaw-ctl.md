# NanoClaw Agent Management Guide

`nanoclaw-ctl` manages the NanoClaw runtime, ensuring secure operations for the webhook server and container executions.

- **Source Code**: [GitHub - gavrielc/nanoclaw](https://github.com/gavrielc/nanoclaw)
- **Arch/AUR Packages**: `nanoclaw-git` (AUR, git-based typescript source build). Alternatives: `nanoclaw`, `nanoclaw-bin`.

## Commands

`nanoclaw-ctl` supports all standard management operations. For detailed command reference and sandboxing path defaults, see [Standard Control Wrappers](../README.md#standard-control-wrappers-assistant-ctl).
## Installation

```bash
./assistants/nanoclaw-ctl install --no-start
```
 to set up `~/.local/sandbox/nanoclaw` and register the systemd user service without starting it.

### Switch to Local Inference & Qwen3

Edit `~/.config/systemd/user/nanoclaw.env` (via `./assistants/nanoclaw-ctl edit`) 
and set `LLM_PROVIDER=openai`, `LLM_BASE_URL=http://localhost:50080/v1`, `LLM_API_KEY=unused`, and `LLM_MODEL=qwen3`.

### Bootstrap Agent

Run the initial setup command `./assistants/nanoclaw-ctl exec tsx scripts/init-first-agent.ts` (or trigger it interactively using the `/init-first-agent` operational skill via Claude Code) to initialize the central database, pair your messaging channel (Telegram, Discord, WhatsApp), and wire a messaging group.

### Authorize OneCLI Vault Secrets

Access the OneCLI interface (default `http://127.0.0.1:10254`). Since new agents start in `selective` credential mode, authorize keys by running:

```bash
onecli agents set-secret-mode --id <agent-group-id> --mode all
```

### Start Webhook Service

Run `./assistants/nanoclaw-ctl start` to start the webhook server on the configured port (default `3000`). Inspect routing and execution via `./assistants/nanoclaw-ctl logs -f` or the `ncl` admin CLI.


## OpenClaw Migration

OpenClaw migration is not natively supported by NanoClaw. You will need to define your agents, platform channels, and credentials manually or write custom scripts to import data into NanoClaw's datastore.

## Search, Retrieval & Embedding Configuration

NanoClaw maintains conversational state and agent mappings in an internal SQLite database within the Node.js process. Localized instructions and memory contexts are kept in files like `CLAUDE.md` within isolated agent directories. Heavy search, retrieval, and vector storage tasks are delegated to external MCP servers or handled by the agent calling custom tools.

### Configuration

Environment and embedding API options can be configured in `~/.config/systemd/user/nanoclaw.env` (via `./assistants/nanoclaw-ctl edit`):

```bash
# SQLite DB state path
DATABASE_URL="file:~/.local/sandbox/nanoclaw/nanoclaw.db"

# Embedding Provider (options: openai, anthropic, local, ollama)
EMBEDDING_PROVIDER="local"
EMBEDDING_MODEL="text-embedding-3-small"

# Local Inference or Ollama endpoint mapping
EMBEDDING_BASE_URL="http://localhost:50082/v1"
EMBEDDING_API_KEY="unused"

# MCP-based Retrieval Configuration (if running sqlite-vec or Qdrant MCP server)
MCP_SQLITE_VEC_DB_PATH="~/.local/sandbox/nanoclaw/mcp-vectors.db"
```

### Reranking Configuration

NanoClaw does not include native reranking. Reranking can be added via a custom skill or by configuring an MCP tool that calls the local-inference reranker endpoint. Set the following in `~/.config/systemd/user/nanoclaw.env`:

```bash
# Local reranker endpoint (served by local-rerank on port 50086)
RERANK_URL="http://localhost:50086/v1/rerank"
RERANK_MODEL="qwen3-reranker"
```

The reranker endpoint accepts `POST /v1/rerank` with `{"model": "qwen3-reranker", "query": "...", "documents": ["..."]}`. Custom agent skills can call this endpoint to reorder retrieval results before injecting them into the agent context.

## Speech-to-Text Integration

NanoClaw does not have native, built-in speech-to-text processing in its core runtime. However, because it runs a Node.js-based webhook/API service, voice transcription support can be integrated by:
1. Creating a custom tool/skill that forwards audio files received from messaging channel webhooks (e.g., Discord/Telegram audio attachments).
2. Performing a `multipart/form-data` POST request to the local `local-speech-to-text` service:
   - **Endpoint**: `http://localhost:50090/v1/audio/transcriptions`
   - **Form Fields**: `file` (the audio binary), `model` (default model configuration)

## Implementation & Security Considerations

### Centralized Sandbox Options
To guarantee parity across all execution modes, `nanoclaw-ctl` centralizes its systemd sandboxing properties in a single helper function (`get_shared_options`). The background service (installed via `install`), the transient command runner (`exec`), and the interactive shell (`shell`) all inherit the exact same filesystem, network, and security restrictions.

### Sandboxing Profile
NanoClaw utilizes a **Relaxed Namespaces Profile** for systemd isolation. Based on auditing the packaging and runtime configuration, these permissions are required:

1. **Namespace Support & Container Runtimes (Docker/Podman)**
   - **Properties Omitted**: `ProtectProc=invisible`, `ProcSubset=pid`, and `RestrictNamespaces=yes`.
   - **Rationale**: NanoClaw orchestrates local container runtimes (such as Docker or Podman) to launch helper agents and execute sandboxed scripts. Standard systemd namespace isolation or proc limits would prevent the runtime from communicating with container daemons or creating nested namespaces.

2. **Writable & Executable Memory (Node.js/V8 JIT)**
   - **Property Set**: `MemoryDenyWriteExecute=no`.
   - **Rationale**: NanoClaw is written in TypeScript/JavaScript and runs under Node.js, which depends on V8 JIT code generation. Rejecting W^X memory regions would prevent Node.js from running correctly.

3. **Physical Devices & Sockets**
   - **Property Set**: `PrivateDevices=no`.
   - **Rationale**: NanoClaw requires access to host device paths (such as container socket paths `/run/user/...` or `/var/run/docker.sock`) to communicate with container daemon backends.

4. **Strict Filesystem Isolation**
   - **Property Set**: `ProtectSystem=strict` and a tmpfs-mounted `$HOME` directory (`TemporaryFileSystem=%h`).
   - **Rationale**: Redirection of `HOME` to `~/.local/sandbox/nanoclaw` ensures that subprocesses do not write to the host user's real home. The persistent home, `~/agent-shared`, and `AGENT_PRIVATE_MOUNTS` are bind-mounted read-write, while other directories are read-only.
