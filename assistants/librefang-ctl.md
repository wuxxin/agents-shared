# LibreFang Agent OS Management Guide

`librefang-ctl` manages the LibreFang Agent OS daemon, providing a hardened execution environment for agentic workloads. LibreFang is the community-governed successor to OpenFang.

- **Source Code**: [GitHub - librefang/librefang](https://github.com/librefang/librefang)
- **Arch/AUR Packages**: `librefang-cli` (provides the client and server binary `/usr/bin/librefang`), `librefang-git` (latest git-based server package).

## Commands

`librefang-ctl` supports all standard management operations. For detailed command reference and sandboxing path defaults, see [Standard Control Wrappers](../README.md#standard-control-wrappers-assistant-ctl).
## Installation

```bash
./assistants/librefang-ctl install --no-start
```

to set up the LibreFang home directory (`~/.local/sandbox/librefang`) and register the systemd user service.

### Initialize Workspace

- Run `./assistants/librefang-ctl shell -c 'printf "[user]\nname = Assistant Name\nemail = assistant@hostname" > ~/.gitconfig'` to initialize git config.

- Run `./assistants/librefang-ctl exec init --quick` to initialize the configuration workspace with default values and `config.toml`.

### Switch to Local Inference & Qwen3

Add a local OpenAI provider to `~/.librefang/config.toml` (located under the isolated home at `~/.local/sandbox/librefang/.librefang/config.toml`):

```toml
[providers.models.openai.local]
model = "qwen3"
uri = "http://localhost:50080/v1"
api_key = "unused"
```

Update your default agent profile's routing to target `openai.local`.

### Start Service

Start the daemon with `./assistants/librefang-ctl start`. Verify it is running by checking the dashboard at `http://localhost:4545`.

### Activate Hands

Run `./assistants/librefang-ctl exec hand activate researcher` (or your hand of choice) to start autonomous background execution. Or run `./assistants/librefang-ctl exec chat <hand_name>` to converse directly.



## Configuration & Ports

- **Default Port**: `4545` (LibreFang daemon API)
- **Secrets & Configuration**: Loaded from `~/.config/systemd/user/librefang.env` and defined via config settings in the configuration file (`~/.librefang/config.toml`).


## Signal Channel Configuration

LibreFang supports native Signal integration. In this environment, it interfaces with the Go-based REST API wrapper.

### Configuration

Add the following to your `~/.librefang/config.toml` config file (located in the sandboxed home directory at `~/.local/sandbox/librefang/.librefang/config.toml`):

```toml
[channels.signal]
api_url = "http://localhost:50889"  # Endpoint of the signal-cli REST API
phone_number = "+1234567890"        # Your registered Signal phone number
allowed_users = ["+1987654321"]     # Optional: List of allowed phone numbers/UUIDs (empty = allow all)
default_agent = "my-agent"          # Optional: Default agent name to route messages to
```

Ensure both the `signal-cli` daemon and the REST API wrapper (listening on port `50889`) are active. LibreFang will connect to the REST wrapper to retrieve message updates and send replies.

---

## Search, Retrieval & Embedding Configuration

LibreFang features native SQLite and vector memory stores for persistent agent memory, task scheduling, and background search/research. Embedding models from different providers (including local and OpenAI endpoints) can be registered to populate vector databases. Agents can also query external search APIs or databases using MCP (Model Context Protocol).

### Configuration

Add the following sections to `~/.librefang/config.toml` (located under the isolated home at `~/.local/sandbox/librefang/.librefang/config.toml`):

```toml
[memory]
backend = "sqlite"                    # Default SQLite backend
vector_storage_enabled = true         # Enable vector search
db_path = "~/.librefang/memory.db"

[embeddings]
provider = "local"
model = "qwen3-embedding"

# Local Inference (llama-server) or Ollama endpoint mapping
base_url = "http://localhost:50085/v1"
api_key = "unused"

[mcp]
# Connect to external vector DB or search servers via Model Context Protocol
[mcp.servers.qdrant]
command = "npx"
args = ["-y", "@modelcontextprotocol/server-qdrant"]
env = { QDRANT_URL = "http://localhost:6333" }
```

### Reranking Configuration

LibreFang supports reranking via configurable provider endpoints (Cohere-compatible API). Add the following to `~/.librefang/config.toml` (located under `~/.local/sandbox/librefang/.librefang/config.toml`):

```toml
[reranker]
# Reranker provider: "local" (OpenAI-compatible /v1/rerank), "cohere", or "disabled"
provider = "local"
model = "qwen3-reranker"

# Local reranker endpoint (served by local-rerank on port 50086)
base_url = "http://localhost:50086/v1"
api_key = "unused"

# Number of top candidates to rerank
top_k = 30
```

---

## Speech-to-Text Integration

LibreFang supports local transcription for audio assets processed during workflows (such as transcribing voice memos or Signal audio events). You can configure your hands to call the `local-speech-to-text` service.

### Configuration

Add the transcription provider configuration to `~/.librefang/config.toml` (located at `~/.local/sandbox/librefang/.librefang/config.toml`):

```toml
[transcription]
# Set provider to local_stt or openai-compatible
provider = "openai"
model = "whisper-1"

# Point to local-speech-to-text service
base_url = "http://localhost:50090/v1"
api_key = "dummy"
```

---

## Implementation & Security Considerations

### Centralized Sandbox Options
To guarantee parity across all execution modes, `librefang-ctl` centralizes its systemd sandboxing properties in a single helper function (`get_shared_options`). The background service (installed via `install`), the transient command runner (`exec`), and the interactive shell (`shell`) all inherit the exact same filesystem, network, and security restrictions.

### Sandboxing Profile
LibreFang utilizes a **Relaxed Namespaces Profile** for systemd isolation. Based on auditing the packaging and runtime configuration, these permissions are required:

1. **Namespace Support (Bubblewrap)**
   - **Properties Omitted**: `ProtectProc=invisible`, `ProcSubset=pid`, and `RestrictNamespaces=yes`.
   - **Rationale**: LibreFang orchestrates tools and sub-agents that require their own isolation using bubblewrap (`bwrap`). `bwrap` relies on unprivileged user namespaces (`CLONE_NEWUSER` and `CLONE_NEWNS`) to build its sandbox; restricting namespaces or procfs traversal inside the systemd service would block this ability.

2. **Writable & Executable Memory (Execution Runtimes)**
   - **Property Set**: `MemoryDenyWriteExecute=no`.
   - **Rationale**: Required for runtime code generators, JITs, and executing dynamically compiled Python/Javascript code blocks during tool workflows.

3. **Strict Filesystem Isolation**
   - **Property Set**: `ProtectSystem=strict` and a tmpfs-mounted `$HOME` directory (`TemporaryFileSystem=%h`).
   - **Rationale**: The agent's persistent directories (`~/.local/sandbox/librefang`, `~/agent-shared`, and specified `AGENT_PRIVATE_MOUNTS`) are bind-mounted read-write, while the rest of the host filesystem is mounted read-only or hidden entirely.
