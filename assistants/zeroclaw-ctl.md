# ZeroClaw Agent Management Guide

`zeroclaw-ctl` manages the ZeroClaw Gateway and agent runtime, providing a hardened execution environment that supports Bubblewrap/Landlock isolation.

- **Source Code**: [GitHub - zeroclaw-labs/zeroclaw](https://github.com/zeroclaw-labs/zeroclaw)
- **Arch/AUR Packages**: `zeroclaw` (AUR, Rust source compilation), `zeroclaw-bin` (AUR, prebuilt binary distribution), `zeroclaw-git` (AUR, git-based).

## Commands

`zeroclaw-ctl` supports all standard management operations. For detailed command reference and sandboxing path defaults, see [Standard Control Wrappers](../README.md#standard-control-wrappers-assistant-ctl).

## Installation

```bash
./assistants/zeroclaw-ctl install --no-start [--new-config]
```

to set up the ZeroClaw home directory (`~/.local/sandbox/zeroclaw`), register the systemd user service, and generate default configuration files pre-configured for local inference services.

The `--new-config` flag generates (or overwrites) both:
- `~/.config/systemd/user/zeroclaw.env` — bootstrap environment variables (port, host, sandbox mounts)
- `~/.local/sandbox/zeroclaw/.zeroclaw/config.toml` — application configuration with local chat (Qwen3), memory (sqlite-hybrid), STT, TTS, and Signal channel settings

### Interactive Onboarding

- Run `./assistants/zeroclaw-ctl exec doctor` to validate configuration syntax and display errors/warnings.

- Run the onboarding setup wizard with `./assistants/zeroclaw-ctl exec onboard`. This will guide you through providers, models, channels, and agent configuration, outputting a minimal four-section configuration to `~/.local/sandbox/zeroclaw/.zeroclaw/config.toml`.

### Switch to Local Inference & Qwen3

Edit `~/.local/sandbox/zeroclaw/.zeroclaw/config.toml` and configure the local provider:
```toml
[providers.models.openai.local]
uri = "http://localhost:50080/v1"
model = "qwen3"
api_key = "unused"
temperature = 1.0
```
Point the target agent at this provider using `model_provider = "openai.local"` under `[agents.<alias>]`.

### Reasoning & Thinking Effort

You can configure the global thinking/reasoning settings for providers that support thinking level controls (e.g. Qwen3) under the `[runtime]` block in `config.toml`:

```toml
[runtime]
reasoning_enabled = true
reasoning_effort = "low"
```


### Verify Connection

Run `./assistants/zeroclaw-ctl exec auth status` to check credentials and model fallback status. Test chat via `./assistants/zeroclaw-ctl exec agent -a <agent_alias>`.

### Start Gateway

Start the service via `./assistants/zeroclaw-ctl start` to launch the background daemon (listening on port `42617`). Watch logs with `./assistants/zeroclaw-ctl logs -f`.


## Configuration & Ports

- **Default Port**: `42617` (ZeroClaw Gateway)
- **Port Customization Options**:
  If the default port (`42617`) needs to be modified, you can configure the new port using:
  **Systemd/Env File (Recommended)**: Edit the configuration files via `./assistants/zeroclaw-ctl edit` (which opens both `zeroclaw.env` and `config.toml`) and set `ZEROCLAW_PORT=<port_number>`. The systemd service will start the daemon with the `zeroclaw daemon --host $ZEROCLAW_HOST --port $ZEROCLAW_PORT` command.


## OpenClaw Migration

ZeroClaw supports importing history and conversation memory logs from an existing OpenClaw installation. To perform the migration, run:
```bash
./assistants/zeroclaw-ctl exec migrate openclaw
```
This command imports the legacy SQLite database memory logs directly into ZeroClaw's memory format.

## Signal Channel Configuration

ZeroClaw supports native Signal integration. It communicates with the daemon via the REST API wrapper.

Add the following to your `config.toml` configuration file (located in the sandboxed home directory at `~/.local/sandbox/zeroclaw/.zeroclaw/config.toml`):

```toml
[channels.signal.default]
approval_timeout_secs = 0
dm_only = true
enabled = true
ignore_attachments = false
ignore_stories = true
http_url = "http://localhost:50889"
# account = Your registered Signal phone number
account = "+1234567890"                  
```

Make sure both the `signal-cli` daemon and the REST API wrapper (listening on port `50889`) are active. ZeroClaw will retrieve message payloads and send messages through this endpoint.

## Search, Retrieval, Embedding & Reranking Configuration

ZeroClaw contains a self-contained, native SQLite-based hybrid memory system. It integrates Full-Text Search (FTS5) and vector search directly into its SQLite datastore, removing the need for external vector database servers. The persistent memory system automatically handles context compression, conversation history limits, and user preference storage.

Reranking Configuration: ZeroClaw includes a built-in weighted hybrid search (0.7 vector similarity / 0.3 keyword FTS) that does not require an external reranker. 

Add the following to your `config.toml` configuration file (located in the sandboxed home directory at `~/.local/sandbox/zeroclaw/.zeroclaw/config.toml`):

```toml
[memory]
# Native hybrid (keyword FTS + vector similarity) SQLite backend
backend = "sqlite.default"

embedding_model = "qwen3-embedding"
embedding_provider = "custom:http://localhost:50080/v1"

```

## Risk & Runtime Profiles

ZeroClaw enforces runtime security and resource isolation using profiles. Any enabled agent (e.g. `[agents.default]`) must reference a valid risk profile and runtime profile:

```toml
[agents.default]
risk_profile = "default"
runtime_profile = "default"
```

These referenced profile names must exist under the corresponding `[risk_profiles]` and `[runtime_profiles]` headers in `config.toml`.

> [!WARNING]
> Since ZeroClaw runs in a systemd/bwrap sandbox by default, the template configuration leverages "Full Autonomy" (YOLO mode) as the default risk profile and a "balanced" runtime profile to provide maximum flexibility:

```toml
# --- Risk & Runtime Profiles
[risk_profiles.default]
level = "full"
workspace_only = false
allowed_commands = ["*"]
forbidden_paths = []
require_approval_for_medium_risk = false
block_high_risk_commands = false
sandbox_enabled = false

[runtime_profiles.default]
agentic = false
max_tool_iterations = 0
max_actions_per_hour = 20
max_cost_per_day_cents = 500
shell_timeout_secs = 60
```

## Speech-to-Text Integration

ZeroClaw supports speech-to-text (STT) transcription by routing voice payloads to the local `local-speech-to-text` service.

Add the transcription provider configuration to `~/.local/sandbox/zeroclaw/.zeroclaw/config.toml`:

```toml
# 1. Define the transcription provider
[providers.transcription.local_whisper.localstt]
uri = "http://localhost:50090/v1/audio/transcriptions"
bearer_token = "dummy"
model = "whisper-1"

# 2. Reference this provider in your agent configuration
[agents.default]
transcription_provider = "local_whisper.localstt"
```

Alternatively, you can configure it globally in the legacy `[transcription]` section of `config.toml`:

```toml
[transcription]
enabled = true

[transcription.local_whisper]
url = "http://localhost:50090/v1/audio/transcriptions"
bearer_token = "dummy"
```

## Text-to-Speech Integration

ZeroClaw supports text-to-speech (TTS) synthesis through OpenAI-compatible endpoints.

Add the TTS provider configuration to `~/.local/sandbox/zeroclaw/.zeroclaw/config.toml`:

```toml
# 1. Enable TTS globally
[tts]
enabled = true

# 2. Define the TTS provider
[providers.tts.openai.local]
uri = "http://localhost:50095/v1/audio/speech"
model = "qwen3-tts"
api_key = "unused"

# 3. Reference this provider in your agent configuration
[agents.default]
tts_provider = "openai.local"
```

## OpenCode Coding Agent Integration

ZeroClaw supports delegating coding and file manipulation tasks to the **OpenCode** coding agent natively. It uses the `opencode_cli` tool wrapper under the hood.

### Prerequisites
1. OpenCode must be installed on the host.
2. The `opencode` CLI binary must be available on the PATH.

### Configuration
Add the `[opencode_cli]` configuration section to `~/.local/sandbox/zeroclaw/.zeroclaw/config.toml`:

```toml
[opencode_cli]
enabled = true
timeout_secs = 600
max_output_bytes = 2097152
# Extra environment variables passed to the opencode subprocess if needed
env_passthrough = []
```

Because OpenCode utilizes the binary's own session by default, no API key or secret token is required unless custom provider credentials need to be passed through via `env_passthrough`.

### Configuration Parameters
*   **`timeout_secs`**: The maximum allowed execution time in seconds for the `opencode run` subprocess. If a coding task runs longer than this limit, the subprocess is automatically terminated and cleaned up to prevent zombie processes on the host. Default: `600` (10 minutes).
*   **`max_output_bytes`**: The maximum captured standard output (`stdout`) size in bytes returned to the ZeroClaw agent loop. If the output exceeds this size, it is truncated on a UTF-8 character boundary to avoid invalid byte decoding errors. Default: `2097152` (2 MB).

---

## Finding Configuration Environment Variables

ZeroClaw supports dynamic environment overrides for all configuration fields.

### Environment Override Syntax
Any dotted path in `config.toml` can be overridden by setting an environment variable following these rules:
- **Prefix**: `ZEROCLAW_`
- **Case**: The tail portion must be in **lowercase** (e.g. `ZEROCLAW_providers...` overrides the config tree, while uppercase tails like `ZEROCLAW_WORKSPACE` and `ZEROCLAW_CONFIG_DIR` are reserved for bootstrap exceptions).
- **Separators**: Dotted separators (`.`) in the TOML path must be replaced with double underscores (`__`).
- **Snake/Kebab conversion**: Single underscores (`_`) map to kebab-case dashes (`-`) for struct field properties (e.g., `api-key` is represented as `api_key`), or act as literal characters within dynamic provider/alias keys.
- **Example**: Overriding `providers.models.openai.default.model` is done via:
  ```bash
  export ZEROCLAW_providers__models__openai__default__model="qwen3"
  ```

### Locating Configuration Properties in Source Code
1. **Source Schema Definition**: Open the configuration schema module at [schema.rs](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/zeroclaw/crates/zeroclaw-config/src/schema.rs) and inspect the `Config` struct (and its nested types) that derive `Configurable`.
2. **How to Search**:
   - ZeroClaw uses struct definitions where fields map to TOML keys. Dynamic model fields and aliases are stored in hash maps or resolved properties.
   - To find configuration fields, search in the config crate for struct fields matching the key. Note that ZeroClaw maps snake_case properties to kebab-case in the config schema natively (e.g. `api_key` maps to `api-key`). Search using ripgrep:
     ```bash
     rg "pub \w*api_key" scratch/zeroclaw/crates/zeroclaw-config/
     ```
3. **CLI Schema Query**: Run `./assistants/zeroclaw-ctl exec config schema` to dump the complete JSON Schema of all properties.
4. **CLI Active Config Listing**: Run `./assistants/zeroclaw-ctl exec config list` to print a list of all currently configured dotted properties.

---

## Implementation & Security Considerations

### Systemd-Free Fallback (Direct Execution)

If systemd is not running in the current environment (e.g. inside a Bubblewrap sandbox), `zeroclaw-ctl` automatically falls back to direct execution of the binary for `exec`, `shell`, and `run` commands. In this fallback mode:
- Environment variables are loaded directly from the generated `zeroclaw.env` file.
- The isolated home directory (`~/.local/sandbox/zeroclaw`) is exported as `$HOME` and set as the working directory.
- `install` and `uninstall` generate configuration/service files but bypass systemctl.
- Commands that require systemd (`start`, `stop`, `restart`, `status`, `enable`, `disable`, `logs`) will exit gracefully with a message indicating systemd is unavailable. To run the daemon directly, use `exec`.

### Centralized Sandbox Options
To guarantee parity across all execution modes, `zeroclaw-ctl` centralizes its systemd sandboxing properties in a single helper function (`get_shared_options`). The background service (installed via `install`), the transient command runner (`exec`), and the interactive shell (`shell`) all inherit the exact same filesystem, network, and security restrictions.

### Sandboxing Profile
ZeroClaw utilizes a **Relaxed Namespaces Profile** for systemd isolation. Based on auditing the source code of ZeroClaw (`v0.8.0-beta-1`), these permissions are required:

1. **Namespace Support (Bubblewrap)**
   - **Properties Omitted**: `ProtectProc=invisible`, `ProcSubset=pid`, and `RestrictNamespaces=yes`.
   - **Rationale**: ZeroClaw features a built-in user namespace-based tool execution sandbox (`crates/zeroclaw-runtime/src/security/bubblewrap.rs`). Restricting namespaces or procfs traversal inside the systemd service would block the agent's ability to spawn nested sandboxes using `bwrap`.

2. **Writable & Executable Memory (WASM Plugins)**
   - **Property Set**: `MemoryDenyWriteExecute=no`.
   - **Rationale**: ZeroClaw supports WebAssembly plugins (`plugins-wasm` feature in the runtime). Blocks or strict JIT filters in systemd would prevent the WASM compiler (e.g. Wasmtime) and Python/JIT tool dependencies from allocating writeable/executable memory ranges.

3. **Physical Devices (USB / Microcontrollers)**
   - **Property Set**: `PrivateDevices=yes` by default.
   - **Rationale**: For security, physical hardware devices are hidden. However, if you are actively using hardware discovery (`zeroclaw hardware discover`) or board flashing (`zeroclaw peripheral flash-nucleo`) over serial/USB, you must configure `PrivateDevices=no` to allow device node access under `/dev`.

4. **Strict Filesystem Isolation**
   - **Property Set**: `ProtectSystem=strict` and a tmpfs-mounted `$HOME` directory (`TemporaryFileSystem=%h`).
   - **Rationale**: The agent's persistent directories (`~/.local/sandbox/zeroclaw`, `~/agent-shared`, and specified `AGENT_PRIVATE_MOUNTS`) are bind-mounted read-write, while the rest of the host filesystem is mounted read-only or hidden entirely.
