# Moltis Agent Management Guide

`moltis-ctl` is a control script for the Moltis Agent server, based on the `openfang-ctl` architecture.

- **Source Code**: [GitHub - moltis-org/moltis](https://github.com/moltis-org/moltis)
- **Arch/AUR Packages**: `moltis` (AUR package built from the current workspace directory, source compilation). Alternatives: `moltis-bin` (AUR, precompiled binary) or `moltis-git` (AUR, latest git source build).

## Commands

`moltis-ctl` supports all standard management operations. For detailed command reference and sandboxing path defaults, see [Standard Control Wrappers](../README.md#standard-control-wrappers-assistant-ctl).


## Installation

```bash
./assistants/moltis-ctl install --no-start
```

### Setup Code
On the first run, Moltis generates a unique setup code. You must retrieve this from the logs to complete the web-based configuration:
```bash
./assistants/moltis-ctl logs
```
Then visit `https://localhost:13131` to enter the code and create your admin account.

> [!TIP]
> For unattended deployments, edit `~/.config/systemd/user/moltis.env` via `./assistants/moltis-ctl edit` and define `MOLTIS_PASSWORD`, `MOLTIS_PROVIDER`, and `MOLTIS_API_KEY` before starting the daemon to bypass the setup wizard.

### Configuration & Ports

- **Default Port**: `13131` (Moltis Agent Server Web UI/API)
- **Secrets & Configuration**: Loaded from `~/.config/systemd/user/moltis.env`. Key variables include `MOLTIS_PASSWORD`, `MOLTIS_PROVIDER`, and `MOLTIS_API_KEY`.

## Switch to Local Inference & Qwen3

Edit `~/.local/sandbox/moltis/moltis.toml` (or via the Web UI) to configure a local OpenAI-compatible provider:
   ```toml
   [providers.models.openai.local]
   model = "qwen3"
   uri = "http://localhost:50080/v1"
   api_key = "unused"
   ```
   Then point your target agent to use `model_provider = "openai.local"`.


## OpenClaw Migration

Moltis supports OpenClaw data and setting imports directly through the Web UI. During the initial onboarding steps (at `https://localhost:13131`), if a legacy OpenClaw workspace is detected, Moltis will prompt you to import settings and agent configurations.

## Signal Channel Configuration

Moltis has native support for receiving and sending Signal messages through an external `signal-cli` daemon.

### Configuration

Add a `[channels.signal.<account-id>]` section to `~/.local/sandbox/moltis/moltis.toml`:

```toml
[channels.signal.personal]
account = "+1234567890"               # Your registered Signal phone number
http_url = "http://127.0.0.1:50888"   # Local signal-cli HTTP daemon port
dm_policy = "allowlist"               # "open", "allowlist", or "disabled"
allowlist = ["+1987654321"]           # Allowed sender phone numbers or UUIDs
group_policy = "disabled"             # "open", "allowlist", or "disabled"
mention_mode = "mention"              # "mention", "always", or "none"
otp_self_approval = true              # Let unknown DM senders self-approve with a PIN challenge
otp_cooldown_secs = 300               # Cooldown after 3 failed OTP attempts
text_chunk_limit = 4000               # Maximum UTF-8 bytes per outbound text chunk
```

Make sure `"signal"` is included in `channels.offered` in `moltis.toml` (it is included by default).

## Search, Retrieval & Embedding Configuration

Moltis provides a built-in SQLite database with Full-Text Search (FTS5) for keyword-based search and direct vector storage. It can optionally offload heavy search operations to a high-performance **QMD** sidecar for BM25 keyword search, vector similarity search, and hybrid retrieval with LLM reranking.

### Configuration

Add the following to `~/.local/sandbox/moltis/moltis.toml`:

```toml
[retrieval]
# Retrieval backend provider: "sqlite" (built-in, default) or "qmd" (external sidecar)
provider = "sqlite"

# Enable BM25 keyword search + vector similarity hybrid retrieval (requires QMD)
hybrid_search = true

# Perform LLM-based reranking on retrieved document chunks
rerank = true

# Strategy for handling agent context limits: "summarize" (default) or "truncate"
context_limit_action = "summarize"

[retrieval.qmd]
# Connection URI for the optional QMD sidecar service
uri = "http://localhost:8080"

[embeddings]
# Embedding provider: "openai" (OpenAI-compatible), "ollama", "local", or "qmd"
provider = "local"
model = "text-embedding-3-small"

# Local Inference Endpoint (llama-server or Ollama)
uri = "http://localhost:50085/v1"
api_key = "unused"
```

### Reranking Configuration

Moltis natively supports reranking via the QMD sidecar, which uses `qwen3-reranker-0.6b` by default for LLM-based reranking of retrieval candidates. Add the following to `~/.local/sandbox/moltis/moltis.toml`:

```toml
[retrieval.reranker]
# Reranker provider: "qmd" (built-in QMD model), "local" (external endpoint), or "disabled"
provider = "local"

# Local reranker endpoint (served by local-rerank on port 50086)
uri = "http://localhost:50086/v1/rerank"
model = "qwen3-reranker"

# Number of top candidates to rerank after initial retrieval
top_k = 30

# Reranking weight in final scoring (QMD default: 0.7 reranker / 0.3 original)
weight = 0.7
```

## Speech-to-Text Integration

Moltis has built-in support for local voice transcription using an external OpenAI-compatible Whisper server. You can configure Moltis to use the `local-speech-to-text` service.

### Configuration

Add the following to `~/.local/sandbox/moltis/moltis.toml`:

```toml
[voice.stt]
# Enable Speech-to-Text globally
enabled = true

# Set active provider to local_stt
provider = "local_stt"

[voice.stt.local_stt]
enabled = true
# Base URI of local-speech-to-text service (do not append '/v1/audio/transcriptions')
endpoint = "http://localhost:50090"
# Optional settings
model = "whisper-1"
language = "en"
```

## Implementation & Security Considerations

### Centralized Sandbox Options
To guarantee parity across all execution modes, `moltis-ctl` centralizes its systemd sandboxing properties in a single helper function (`get_shared_options`). The background service (installed via `install`), the transient command runner (`exec`), and the interactive shell (`shell`) all inherit the exact same filesystem, network, and security restrictions.

### Sandboxing Profile
Moltis utilizes a **Relaxed Namespaces Profile** for systemd isolation. Based on auditing the source code of Moltis, these permissions are required:

1. **Namespace Support (Bubblewrap)**
   - **Properties Omitted**: `ProtectProc=invisible`, `ProcSubset=pid`, and `RestrictNamespaces=yes`.
   - **Rationale**: Moltis features a built-in user namespace-based tool execution sandbox. Restricting namespaces or procfs traversal inside the systemd service would block the agent's ability to spawn nested sandboxes using `bwrap`.

2. **Writable & Executable Memory (WASM Plugins)**
   - **Property Set**: `MemoryDenyWriteExecute=no`.
   - **Rationale**: Moltis supports WebAssembly plugins. Blocks or strict JIT filters in systemd would prevent the WASM compiler (e.g. Wasmtime) and Python/JIT tool dependencies from allocating writeable/executable memory ranges.

3. **Network Access (Privileged Ports)**
   - **Properties Set**: `CapabilityBoundingSet=CAP_NET_BIND_SERVICE` and `AmbientCapabilities=CAP_NET_BIND_SERVICE`.
   - **Rationale**: This allows Moltis to bind to privileged ports (ports < 1024 like 80/443) if configured by the user, while dropping all other Linux capabilities.

4. **Physical Devices (Hardware Integrations)**
   - **Property Set**: `PrivateDevices=no` by default.
   - **Rationale**: Allows potential hardware-backed operations or microcontroller access if required by specific plugins.

5. **Strict Filesystem Isolation**
   - **Property Set**: `ProtectSystem=strict` and a tmpfs-mounted `$HOME` directory (`TemporaryFileSystem=%h`).
   - **Rationale**: The agent's persistent directories (`~/.local/sandbox/moltis`, `~/agent-shared`, and specified `AGENT_PRIVATE_MOUNTS`) are bind-mounted read-write, while the rest of the host filesystem is mounted read-only or hidden entirely.
