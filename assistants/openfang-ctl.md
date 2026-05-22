# OpenFang Agent OS Management Guide

`openfang-ctl` manages the OpenFang Agent OS daemon, providing a hardened execution environment for agentic workloads.

- **Source Code**: [GitHub - RightNow-AI/openfang](https://github.com/RightNow-AI/openfang)
- **Arch/AUR Packages**: `openfang-cli` (AUR, provides both CLI client and the main server binary `/usr/bin/openfang`). Alternatives: `openfang-cli-git` (AUR, git-based).

## Installation

```bash
./assistants/openfang-ctl install
```

## Commands

`openfang-ctl` supports all standard management operations. For detailed command reference and sandboxing path defaults, see [Standard Control Wrappers](file:///home/wuxxin/agent-shared/code/aur-packages/assistants/assistants.md#standard-control-wrappers-assistant-ctl).

## Configuration & Ports

- **Default Port**: `4200` (OpenFang daemon API)
- **Secrets & Configuration**: Loaded from `~/.config/systemd/user/openfang.env` and defined via config settings in the configuration file (`~/.openfang/config.toml`).

## Signal Channel Configuration

OpenFang supports native Signal integration. In this environment, it interfaces with the Go-based REST API wrapper.

### Configuration

Add the following to your `~/.openfang/config.toml` config file (located in the sandboxed home directory at `~/.local/share/openfang/.openfang/config.toml`):

```toml
[channels.signal]
api_url = "http://localhost:50889"  # Endpoint of the signal-cli REST API
phone_number = "+1234567890"        # Your registered Signal phone number
allowed_users = ["+1987654321"]     # Optional: List of allowed phone numbers/UUIDs (empty = allow all)
default_agent = "my-agent"          # Optional: Default agent name to route messages to
```

Ensure both the `signal-cli` daemon and the REST API wrapper (listening on port `50889`) are active. OpenFang will connect to the REST wrapper to retrieve message updates and send replies.

## Search, Retrieval & Embedding Configuration

OpenFang features native SQLite and vector memory stores for persistent agent memory, task scheduling, and background search/research. Embedding models from 27 different providers (including local and OpenAI endpoints) can be registered to populate vector databases. Agents can also query external search APIs or databases using MCP (Model Context Protocol).

### Configuration

Add the following sections to `~/.openfang/config.toml` (which is located under the isolated home at `~/.local/share/openfang/.openfang/config.toml`):

```toml
[memory]
backend = "sqlite"                    # Default SQLite backend
vector_storage_enabled = true         # Enable vector search
db_path = "~/.openfang/memory.db"

[embeddings]
# Embedding provider (supports 27 providers: openai, cohere, local, etc.)
provider = "local"
model = "text-embedding-3-small"

# Local Inference (llama-server) or Ollama endpoint mapping
base_url = "http://localhost:50080/v1"
api_key = "unused"

[mcp]
# Connect to external vector DB or search servers via Model Context Protocol
[mcp.servers.qdrant]
command = "npx"
args = ["-y", "@modelcontextprotocol/server-qdrant"]
env = { QDRANT_URL = "http://localhost:6333" }
```

### Reranking Configuration

OpenFang supports reranking via configurable provider endpoints (Cohere-compatible API). Add the following to `~/.openfang/config.toml` (located under `~/.local/share/openfang/.openfang/config.toml`):

```toml
[reranker]
# Reranker provider: "local" (OpenAI-compatible /v1/rerank), "cohere", or "disabled"
provider = "local"
model = "qwen3-reranker"

# Local reranker endpoint (served by local-inference on port 50080)
base_url = "http://localhost:50080/v1"
api_key = "unused"

# Number of top candidates to rerank
top_k = 30
```

## Speech-to-Text Integration

OpenFang supports local transcription for audio assets processed during workflows (such as media hands transcribing voice memos or Signal audio events). You can configure your hands to call the `local-speech-to-text` service.

### Configuration

Add the transcription provider configuration to `~/.openfang/config.toml` (located at `~/.local/share/openfang/.openfang/config.toml`):

```toml
[transcription]
# Set provider to local_stt or openai-compatible
provider = "openai"
model = "whisper"

# Point to local-speech-to-text service
base_url = "http://localhost:50090/v1"
api_key = "dummy"
```

## Onboarding

1. **Install Service**: Run `./assistants/openfang-ctl install` to set up the OpenFang home directory (`~/.local/share/openfang`) and register the systemd user service.
2. **Initialize Workspace**: Run `./assistants/openfang-ctl exec init` to initialize the configuration workspace and prompt you interactively for LLM API keys to build `openfang.toml`.
3. **Start Service**: Start the daemon with `./assistants/openfang-ctl start`. Verify it is running by checking the dashboard at `http://localhost:4200`.
4. **Activate Hands**: Run `./assistants/openfang-ctl exec hand activate researcher` (or your hand of choice) to start autonomous background execution. Or run `./assistants/openfang-ctl exec chat <hand_name>` to converse directly.
5. **Switch to Local Inference & Qwen3**: Add a local OpenAI provider to `~/.openfang/config.toml` (which is located under the isolated home at `~/.local/share/openfang/.openfang/config.toml`):
   ```toml
   [providers.models.openai.local]
   model = "qwen3"
   uri = "http://localhost:50080/v1"
   api_key = "unused"
   ```
   Update your default agent profile's routing to target `openai.local`.

### OpenClaw Migration

OpenFang supports automatic migration from an existing OpenClaw installation. When you run:
```bash
./assistants/openfang-ctl exec init
```
OpenFang will scan your system for legacy OpenClaw directories (such as `~/.openclaw`), read your configuration, and import existing data, agent specifications, and credentials into `openfang.toml`.

## Implementation & Security Considerations

### Centralized Sandbox Options
To guarantee parity across all execution modes, `openfang-ctl` centralizes its systemd sandboxing properties in a single helper function (`get_shared_options`). The background service (installed via `install`), the transient command runner (`exec`), and the interactive shell (`shell`) all inherit the exact same filesystem, network, and security restrictions.

### Sandboxing Profile
OpenFang utilizes a **Relaxed Namespaces Profile** for systemd isolation. Based on auditing the packaging and runtime configuration, these permissions are required:

1. **Namespace Support (Bubblewrap)**
   - **Properties Omitted**: `ProtectProc=invisible`, `ProcSubset=pid`, and `RestrictNamespaces=yes`.
   - **Rationale**: OpenFang orchestrates tools and sub-agents that require their own isolation using bubblewrap (`bwrap`). `bwrap` relies on unprivileged user namespaces (`CLONE_NEWUSER` and `CLONE_NEWNS`) to build its sandbox; restricting namespaces or procfs traversal inside the systemd service would block this ability.

2. **Writable & Executable Memory (Execution Runtimes)**
   - **Property Set**: `MemoryDenyWriteExecute=no`.
   - **Rationale**: Required for runtime code generators, JITs, and executing dynamically compiled Python/Javascript code blocks during tool workflows.

3. **Strict Filesystem Isolation**
   - **Property Set**: `ProtectSystem=strict` and a tmpfs-mounted `$HOME` directory (`TemporaryFileSystem=%h`).
   - **Rationale**: The agent's persistent directories (`~/.local/share/openfang`, `~/agent-shared`, and specified `AGENT_PRIVATE_MOUNTS`) are bind-mounted read-write, while the rest of the host filesystem is mounted read-only or hidden entirely.
