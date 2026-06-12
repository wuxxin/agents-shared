# IronClaw Agent Management Guide

`ironclaw-ctl` manages the IronClaw Agent OS runtime, providing a hardened execution environment with WASM-sandboxed tool execution, credential protection, and prompt injection defense.

- **Source Code**: [GitHub - nearai/ironclaw](https://github.com/nearai/ironclaw)
- **Arch/AUR Packages**: `ironclaw-git` (AUR, git-based Rust source compilation).

## Commands

`ironclaw-ctl` supports all standard management operations. For detailed command reference and sandboxing path defaults, see [Standard Control Wrappers](../README.md#standard-control-wrappers-assistant-ctl).

## Installation

```bash
./assistants/ironclaw-ctl install --no-start [--new-config]
```

to set up the IronClaw home directory (`~/.local/sandbox/ironclaw`), register the systemd user service, and generate default configuration files pre-configured for local inference services.

The `--new-config` flag generates (or overwrites):
- `~/.config/systemd/user/ironclaw.env` — bootstrap environment variables (ports, database URL, LLM backend)
- `~/.local/sandbox/ironclaw/.ironclaw/.env` — application environment overrides

### Prerequisites

IronClaw requires a PostgreSQL 15+ database with the [pgvector](https://github.com/pgvector/pgvector) extension installed. Ensure the database is running before starting the service:

```bash
# Create the database (one-time setup)
createdb ironclaw
psql -d ironclaw -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### Interactive Onboarding

Run the onboarding setup wizard with `./assistants/ironclaw-ctl exec onboard`. This will guide you through database connection, LLM provider selection, authentication, and channel configuration.

### Switch to Local Inference

Edit `~/.local/sandbox/ironclaw/.ironclaw/.env` and configure the local provider:

```env
LLM_BACKEND=openai_compatible
LLM_API_KEY=unused
LLM_BASE_URL=http://localhost:50080/v1
LLM_MODEL=qwen3
```

### Verify Connection

Run `./assistants/ironclaw-ctl exec status` to check credentials and service health. Test chat via `./assistants/ironclaw-ctl exec chat`.

### Start Gateway

Start the service via `./assistants/ironclaw-ctl start` to launch the background daemon (listening on port `8080` by default). Watch logs with `./assistants/ironclaw-ctl logs -f`.


## Configuration & Ports

- **Default Port**: `8080` (IronClaw Web Gateway & HTTP Webhooks)
- **Port Customization Options**:
  Edit the configuration environment file at `~/.config/systemd/user/ironclaw.env` (either directly or via `./assistants/ironclaw-ctl edit`) and set:
  ```env
  HTTP_HOST=0.0.0.0
  HTTP_PORT=8080
  ```

### Key Environment Variables

IronClaw uses flat environment variables (no `IRONCLAW_*` prefix convention). Configuration priority: **Environment Variables > Database Settings > Defaults**.

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `postgres://localhost/ironclaw` | PostgreSQL connection string |
| `LLM_BACKEND` | `nearai` | LLM provider (`nearai`, `ollama`, `openai_compatible`, `openai`, `anthropic`, `github_copilot`, `gemini_oauth`) |
| `LLM_API_KEY` | — | API key for the configured LLM provider |
| `LLM_BASE_URL` | — | Base URL override for OpenAI-compatible providers |
| `LLM_MODEL` | — | Model name override |
| `HTTP_HOST` | `0.0.0.0` | Web gateway bind address |
| `HTTP_PORT` | `8080` | Web gateway listen port |
| `AGENT_NAME` | `ironclaw` | Agent display name |
| `AGENT_MAX_PARALLEL_JOBS` | `5` | Maximum concurrent job contexts |
| `ENGINE_V2` | `true` | Enable v2 engine |
| `SANDBOX_ENABLED` | `true` | Enable WASM tool sandboxing |
| `SANDBOX_POLICY` | `readonly` | Sandbox access policy (`readonly`, `workspace_write`, `full_access`) |
| `HEARTBEAT_ENABLED` | `false` | Enable proactive background heartbeat tasks |
| `SAFETY_INJECTION_CHECK_ENABLED` | `true` | Enable prompt injection defense |
| `ACP_ENABLED` | `false` | Enable Agent Client Protocol for external coding agents |


## Signal Channel Configuration

IronClaw supports native Signal integration. It communicates with the daemon via the `signal-cli` HTTP interface.

Configure Signal via environment variables in `~/.local/sandbox/ironclaw/.ironclaw/.env`:

```env
SIGNAL_HTTP_URL=http://127.0.0.1:50889
# account = Your registered Signal phone number
SIGNAL_ACCOUNT=+1234567890
# Comma-separated allowlist of phone numbers or uuid: prefixed UUIDs
SIGNAL_ALLOW_FROM=+1234567890,uuid:your-uuid-here
# DM policy: open | allowlist | pairing
SIGNAL_DM_POLICY=pairing
# Group policy: open | allowlist
SIGNAL_GROUP_POLICY=allowlist
SIGNAL_IGNORE_ATTACHMENTS=false
SIGNAL_IGNORE_STORIES=true
```

Make sure both the `signal-cli` daemon and the REST API wrapper (listening on port `50889`) are active. IronClaw will retrieve message payloads and send messages through this endpoint.


## Search, Retrieval, Embedding & Reranking Configuration

IronClaw uses PostgreSQL with the pgvector extension for its persistent memory system. It combines full-text search and vector similarity via Reciprocal Rank Fusion (RRF), providing hybrid search without requiring external vector database infrastructure.

Additionally, IronClaw features a workspace filesystem for flexible path-based storage (notes, logs, context) and identity files that maintain consistent personality and preferences across sessions.

Embedding configuration is handled via the LLM provider settings. For local embeddings using `local-embedding`:

```env
# Use the local embedding endpoint
LLM_BACKEND=openai_compatible
LLM_BASE_URL=http://localhost:50082/v1
LLM_API_KEY=unused
```

Reranking is handled natively through the built-in Reciprocal Rank Fusion (RRF) algorithm that merges full-text and vector search results. No external reranker endpoint is required.


## Speech-to-Text Integration

IronClaw supports speech-to-text (STT) transcription via OpenAI-compatible transcription endpoints. It also includes a built-in SILK audio decoder for WeChat voice messages.

Configure local STT via environment variables in `~/.local/sandbox/ironclaw/.ironclaw/.env`:

```env
TRANSCRIPTION_ENABLED=true
TRANSCRIPTION_PROVIDER=openai
TRANSCRIPTION_BASE_URL=http://localhost:50090/v1
TRANSCRIPTION_MODEL=whisper-1
```

This routes audio transcription requests to the local `local-speech-to-text` service on port 50090.


## Additional Channels

IronClaw supports multiple communication channels beyond Signal:

| Channel | Type | Notes |
|---|---|---|
| REPL | Built-in | Terminal-based interactive chat |
| Web Gateway | Built-in | Browser UI with SSE/WebSocket streaming (port 8080) |
| Telegram | WASM Channel | Install via `ironclaw registry install telegram` |
| Slack | WASM Channel | Install via `ironclaw registry install slack` |
| Discord | WASM Channel | Install via `ironclaw registry install discord` |
| WhatsApp | WASM Channel | Install via `ironclaw registry install whatsapp` |
| WeChat / WeCom | WASM Channel | Install via `ironclaw registry install wecom` |
| Feishu | WASM Channel | Install via `ironclaw registry install feishu` |

WASM channels are installed from the IronClaw registry and run in isolated WebAssembly containers with capability-based permissions.

---

## Implementation & Security Considerations

### Systemd-Free Fallback (Direct Execution)

If systemd is not running in the current environment (e.g. inside a Bubblewrap sandbox), `ironclaw-ctl` automatically falls back to direct execution of the binary for `exec`, `shell`, and `run` commands. In this fallback mode:
- Environment variables are loaded directly from the generated `ironclaw.env` file.
- The isolated home directory (`~/.local/sandbox/ironclaw`) is exported as `$HOME` and set as the working directory.
- `install` and `uninstall` generate configuration/service files but bypass systemctl.
- Commands that require systemd (`start`, `stop`, `restart`, `status`, `enable`, `disable`, `logs`) will exit gracefully with a message indicating systemd is unavailable. To run the daemon directly, use `exec`.

### Centralized Sandbox Options
To guarantee parity across all execution modes, `ironclaw-ctl` centralizes its systemd sandboxing properties in a single helper function (`get_shared_options`). The background service (installed via `install`), the transient command runner (`exec`), and the interactive shell (`shell`) all inherit the exact same filesystem, network, and security restrictions.

### Sandboxing Profile
IronClaw utilizes a **Relaxed Namespaces Profile** for systemd isolation. Based on auditing the source code of IronClaw (`v0.29.0`), these permissions are required:

1. **WASM Sandbox Execution**
   - **Property Set**: `MemoryDenyWriteExecute=no`.
   - **Rationale**: IronClaw executes all untrusted tools inside isolated WebAssembly containers via wasmtime. The WASM JIT compiler requires allocating writable/executable memory pages, which `MemoryDenyWriteExecute=yes` would block.

2. **Docker Sandbox (Optional)**
   - **Properties**: `RestrictNamespaces=yes` is **omitted** when Docker sandbox mode is active.
   - **Rationale**: IronClaw supports an orchestrator/worker Docker sandbox pattern for isolated container execution with per-job tokens. This requires namespace creation capabilities.

3. **Physical Devices**
   - **Property Set**: `PrivateDevices=yes` by default.
   - **Rationale**: Physical hardware devices are hidden for security. No hardware access is required for standard agent operation.

4. **Strict Filesystem Isolation**
   - **Property Set**: `ProtectSystem=strict` and a tmpfs-mounted `$HOME` directory (`TemporaryFileSystem=%h`).
   - **Rationale**: The agent's persistent directories (`~/.local/sandbox/ironclaw`, `~/agent-shared`, and specified `AGENT_PRIVATE_MOUNTS`) are bind-mounted read-write, while the rest of the host filesystem is mounted read-only or hidden entirely.

### Key Architectural Differences from Other Agents

- **PostgreSQL + pgvector** instead of SQLite (unique among covered agents): Requires a running PostgreSQL instance but provides more robust concurrent access and scalable vector operations.
- **WASM sandbox** instead of Bubblewrap/Landlock for tool isolation: Tools run in WebAssembly containers with fine-grained capability-based permissions (allowed HTTP endpoints, secret injection at host boundary).
- **Flat environment variables** (no `IRONCLAW_*` prefix override mechanism): Uses direct env vars like `LLM_BACKEND`, `DATABASE_URL`, `HTTP_PORT`.
- **Settings stored in database**: After onboarding, settings are persisted in PostgreSQL. Bootstrap variables remain in `~/.ironclaw/.env`.
- **NEAR AI integration**: Default authentication and LLM backend uses NEAR AI platform. Can be overridden to use fully local providers.
