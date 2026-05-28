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

Configure the default model in `~/.librefang/config.toml` (located under the isolated home at `~/.local/sandbox/librefang/.librefang/config.toml`):

```toml
[default_model]
provider = "openai"
model = "qwen3"
api_key_env = "UNUSED_API_KEY"
context_window = 80000

[provider_urls]
openai = "http://localhost:50080/v1"
```

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
[[sidecar_channels]]
command = "python3"
args = ["-m", "librefang.sidecar.adapters.signal"]
name = "signal"
channel_type = "signal"

[sidecar_channels.env]
SIGNAL_API_URL = "http://localhost:50889/"
SIGNAL_NUMBER = "+1234567890"
SIGNAL_ALLOW_LOCAL = "1"
```

Ensure both the `signal-cli` daemon and the REST API wrapper (listening on port `50889`) are active. LibreFang will connect to the REST wrapper to retrieve message updates and send replies.

---

## Search, Retrieval & Embedding Configuration

LibreFang features native SQLite and vector memory stores for persistent agent memory, task scheduling, and background search/research. Embedding models from different providers (including local and OpenAI endpoints) can be registered to populate vector databases. Agents can also query external search APIs or databases using MCP (Model Context Protocol).

### Configuration

Add the following sections to `~/.librefang/config.toml` (located under the isolated home at `~/.local/sandbox/librefang/.librefang/config.toml`):

```toml
[memory]
embedding_provider = "openai"
embedding_model = "qwen3-embedding"
embedding_dimensions = 1536

[provider_urls]
openai = "http://localhost:50080/v1"

[mcp]
# Connect to external vector DB or search servers via Model Context Protocol
[mcp.servers.qdrant]
command = "npx"
args = ["-y", "@modelcontextprotocol/server-qdrant"]
env = { QDRANT_URL = "http://localhost:6333" }
```

> [!NOTE]
> The embedding provider can also be set to `"auto"` (the default). In this mode, the daemon automatically probes environment variables like `OLLAMA_HOST`, `VLLM_BASE_URL`, and `LMSTUDIO_BASE_URL` to select a provider, falling back to standard local ports.

### Reranking, STT, and TTS Limits

- **Reranking**: Reranking is not supported or configurable in this version of the LibreFang daemon.
- **Speech-to-Text (STT) / Text-to-Speech (TTS)**: Custom local server base URLs for transcription and speech synthesis are not supported by the upstream LibreFang daemon (endpoints are hardcoded in the codebase to cloud APIs). Patched packages (such as `librefang-git` with `feature-local-stt-tts`) are required to override STT/TTS endpoints.

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
