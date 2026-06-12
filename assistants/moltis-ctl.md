# Moltis Agent Management Guide

`moltis-ctl` is a control script for the Moltis Agent server, based on the `openfang-ctl` architecture.

- **Source Code**: [GitHub - moltis-org/moltis](https://github.com/moltis-org/moltis)
- **Arch/AUR Packages**: `moltis` (AUR package built from the current workspace directory, rust source compilation). Alternatives: `moltis-bin` (AUR, precompiled binary) or `moltis-git` (AUR, latest git source build).

## Commands

`moltis-ctl` supports all standard management operations. For detailed command reference and sandboxing path defaults, see [Standard Control Wrappers](../README.md#standard-control-wrappers-assistant-ctl).

## Installation

```bash
./assistants/moltis-ctl install --no-start [--new-config]
```

to set up the Moltis home directory (`~/.local/sandbox/moltis`), register the systemd user service, and generate default configuration files pre-configured for local inference services.

The `--new-config` flag generates (or overwrites) both:
- `~/.config/systemd/user/moltis.env` — bootstrap environment variables (password, data/config directories, sandbox mounts)
- `~/.local/sandbox/moltis/.config/moltis/moltis.toml` — application configuration with local chat (Qwen3), memory/embeddings, STT, TTS, and Signal channel settings

> [!TIP]
> For unattended deployments, run `./assistants/moltis-ctl edit` to configure the environment and define `MOLTIS_PASSWORD`, `MOLTIS_PROVIDER`, and `MOLTIS_API_KEY` before starting the daemon to bypass the setup wizard.

- Run `./assistants/moltis-ctl exec doctor` to validate configuration syntax and display errors/warnings.

- On the first run, Moltis generates a unique setup code. You must retrieve this from the logs to complete the web-based configuration:
```bash
./assistants/moltis-ctl logs
```
Then visit `https://localhost:13131` to enter the code and create your admin account.

### Configuration & Ports

- **Default Port**: `13131` (Moltis Agent Server Web UI/API)
- **Secrets & Configuration**: Bootstrap parameters and application settings are configured via `./assistants/moltis-ctl edit` (which opens both the env file and `moltis.toml`).


## OpenClaw Migration

Moltis supports OpenClaw data and setting imports directly through the Web UI. During the initial onboarding steps (at `https://localhost:13131`), if a legacy OpenClaw workspace is detected, Moltis will prompt you to import settings and agent configurations.

## Local Inference with Qwen3

Run `./assistants/moltis-ctl edit` (or use the Web UI) to configure a local OpenAI-compatible provider in `moltis.toml`:
   ```toml
   [providers.openai]
   enabled = true
   base_url = "http://localhost:50080/v1"
   api_key = "unused"
   models = ["qwen3"]

   [providers.openai.model_overrides.qwen3]
   context_window = 80000
   ```

### Reasoning & Thinking Effort

You can configure the reasoning/thinking effort level for agents that support extended thinking (e.g. Qwen3) under the corresponding agent preset section in `moltis.toml`:

```toml
[agents.presets.research]
reasoning_effort = "low"
```

> [!NOTE]
> Moltis does not expose a dedicated `temperature` property in `moltis.toml`. When executing requests via the standard OpenAI-compatible provider client, it inherits the defaults configured on the upstream server (e.g., the local `llama-server` instance managed by `local-llm-ggml`). For embedded local GGUF/MLX setups inside the gateway, the default temperature is internally set to `0.7`.


## Signal Channel Configuration

Moltis has native support for receiving and sending Signal messages through an external `signal-cli` daemon.

Add a `[channels.signal.<account-id>]` section to `~/.local/sandbox/moltis/.config/moltis/moltis.toml`:

```toml
[channels.signal.personal]
account = "+1234567890"               # Your registered Signal phone number
http_url = "http://127.0.0.1:50889"   # Local signal-cli REST API wrapper port
dm_policy = "allowlist"               # "open", "allowlist", or "disabled"
allowlist = ["+1987654321"]           # Allowed sender phone numbers or UUIDs
group_policy = "disabled"             # "open", "allowlist", or "disabled"
mention_mode = "mention"              # "mention", "always", or "none"
otp_self_approval = true              # Let unknown DM senders self-approve with a PIN challenge
otp_cooldown_secs = 300               # Cooldown after 3 failed OTP attempts
text_chunk_limit = 4000               # Maximum UTF-8 bytes per outbound text chunk
```

Make sure `"signal"` is included in `channels.offered` in `moltis.toml` (it is included by default).

## Search, Retrieval, Embedding & Reranking Configuration

Moltis provides a built-in SQLite database with Full-Text Search (FTS5) for keyword-based search and direct vector storage. It can optionally offload heavy search operations to a high-performance **QMD** sidecar for BM25 keyword search, vector similarity search, and hybrid retrieval with LLM reranking.

Add the following to `~/.local/sandbox/moltis/.config/moltis/moltis.toml`:

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

[memory]
# Embedding provider: "openai" (OpenAI-compatible), "ollama", "local", or "qmd"
provider = "local"
model = "qwen3-embedding"

# Local Inference Endpoint (llama-server or Ollama)
base_url = "http://localhost:50082/v1"
api_key = "unused"
```

### Reranking Configuration

Moltis natively supports reranking via the QMD sidecar, which uses `qwen3-reranker-0.6b` by default for LLM-based reranking of retrieval candidates. Add the following to `~/.local/sandbox/moltis/.config/moltis/moltis.toml`:

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

Add the following to `~/.local/sandbox/moltis/.config/moltis/moltis.toml`:

```toml
[voice.stt]
# Enable Speech-to-Text globally
enabled = true

# Set active provider to whisper-local
provider = "whisper-local"

[voice.stt.whisper-local]
enabled = true
# Base URI of local-speech-to-text service (do not append '/v1/audio/transcriptions')
endpoint = "http://localhost:50090/"
# Optional settings
model = "whisper-1"
```

## Text-to-Speech Integration

Moltis supports text-to-speech (TTS) output through OpenAI-compatible endpoints, allowing agents to generate voice responses.

Add the following to `~/.local/sandbox/moltis/.config/moltis/moltis.toml`:

```toml
[voice.tts]
enabled = true
provider = "openai"

[voice.tts.openai]
enabled = true
base_url = "http://localhost:50095/v1"
model = "qwen3-tts"
voice = "serena"
api_key = "unused"
```

---

## Finding Configuration Environment Variables

Moltis supports environment overrides for configuration parameters.

### Environment Override Syntax
Any configuration field in `moltis.toml` can be overridden by setting an environment variable following these rules:
- **Prefix**: `MOLTIS_`
- **Case**: Environment variable names are case-insensitive when parsed, but are typically written in **UPPERCASE** (and converted to lowercase segments internally).
- **Separators**: Dotted separators (`.`) in the TOML path must be replaced with double underscores (`__`).
- **Snake case**: Unlike ZeroClaw, Moltis uses snake_case keys natively, so single underscores (`_`) are preserved (e.g. `dm_policy` remains `dm_policy`).
- **Example**: Overriding `channels.signal.personal.dm_policy` is done via:
  ```bash
  export MOLTIS_CHANNELS__SIGNAL__PERSONAL__DM_POLICY="open"
  ```
- **Excluded**: Bootstrap settings like `MOLTIS_CONFIG_DIR`, `MOLTIS_DATA_DIR`, `MOLTIS_SHARE_DIR`, `MOLTIS_ASSETS_DIR`, `MOLTIS_TOKEN`, `MOLTIS_PASSWORD`, `MOLTIS_TAILSCALE`, and `MOLTIS_EXTERNAL_URL` are parsed separately and cannot be overridden as config properties.

### Locating Configuration Properties in Source Code
1. **Source Schema Definition**: Open the configuration schema module at [schema.rs](scratch/moltis/crates/config/src/schema.rs) and inspect the `MoltisConfig` struct (and its nested types).
2. **How to Search**:
   - To find where a TOML configuration key (like `dm_policy` or `base_url`) is defined or parsed, search for the key name as a Rust field identifier in snake_case (e.g. `pub dm_policy` or `pub base_url`) within the configuration crates.
   - Run a ripgrep command targeting the `crates/config` directory:
     ```bash
     rg "pub \w*base_url" scratch/moltis/crates/config/
     ```
3. **Config Validation**: Run `./assistants/moltis-ctl exec doctor` to validate the current configuration. This command parses the files and highlights errors or warnings, referencing the correct property paths.
4. **Reference Toml**: Inspect the default/sample `moltis.toml` file to see the structure of configuration parameters.

---

## Implementation & Security Considerations

### Systemd-Free Fallback (Direct Execution)

If systemd is not running in the current environment (e.g. inside a Bubblewrap sandbox), `moltis-ctl` automatically falls back to direct execution of the binary for `exec`, `shell`, and `run` commands. In this fallback mode:
- Environment variables are loaded directly from the generated `moltis.env` file.
- The isolated home directory (`~/.local/sandbox/moltis`) is exported as `$HOME` and set as the working directory.
- `install` and `uninstall` generate configuration/service files but bypass systemctl.
- Commands that require systemd (`start`, `stop`, `restart`, `status`, `enable`, `disable`, `logs`) will exit gracefully with a message indicating systemd is unavailable. To run the daemon directly, use `exec`.

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
