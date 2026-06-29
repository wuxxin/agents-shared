# ZeroClaw Agent OS Control Guide

This guide describes configuration, onboarding, and integration features specific to the ZeroClaw Agent OS daemon.

For shared commands, variable expansion rules, sidecars supervision, temporary file cleanups, and unified sandboxing profiles, see the general [Agent Service Guide](agents-ctl.md).

- **Source Code**: [GitHub - zeroclaw-labs/zeroclaw](https://github.com/zeroclaw-labs/zeroclaw)
- **Arch/AUR Packages**: `zeroclaw` (AUR, Rust source compilation), `zeroclaw-bin` (AUR, prebuilt binary distribution), `zeroclaw-git` (AUR, git-based).

---

## Agent-Specific Defaults

- **Home Directory:** `~/.local/sandbox/zeroclaw`
- **Default Workspace Path:** `%h/.local/sandbox/zeroclaw/.zeroclaw/agents/default/workspace`
- **Configuration File:** `~/.local/sandbox/zeroclaw/.zeroclaw/config.toml`
- **Default Gateway Port:** [42617](http://localhost:42617/) (set via `ZEROCLAW_PORT` inside `zeroclaw.env`)
- **Default Web UI Port:** [42618](http://localhost:42618/)` (if dashboard is active)

---

## Onboarding & Wizards

Initialize the ZeroClaw configuration using:
```bash
./assistants/zeroclaw-ctl exec config onboard
```
This generates the initial `config.toml` file under the sandbox home.

To query active settings:
*   **Dump JSON Schema:** `./assistants/zeroclaw-ctl exec config schema`
*   **List Active Configurations:** `./assistants/zeroclaw-ctl exec config list`

---

## Local Inference

To switch ZeroClaw to use the local llama-server, set the following parameters in `~/.local/sandbox/zeroclaw/.zeroclaw/config.toml`:

```toml
[llm]
model = "qwen3"
base_url = "http://localhost:50080/v1"
api_key = "unused"
temperature = 1.0
```
### Reasoning & Thinking Effort

You can configure the global thinking/reasoning settings for providers that support thinking level controls (e.g. Qwen3) under the `[runtime]` block in `config.toml`:

```toml
[runtime]
reasoning_enabled = true
reasoning_effort = "low"
```

## Signal Channel Configuration & Peer Group Routing

ZeroClaw supports native Signal integration. It communicates with the daemon via the REST API wrapper.

#### Centralized Service Env / Common Variables
For credentials and dynamic overrides, configure environment variables in the centralized service env configuration file: `~/.config/systemd/user/zeroclaw.env` (recommended). ZeroClaw supports dotted-path environment overrides:
```env
# Centralized Signal Account & Endpoint Overrides
ZEROCLAW_channels__signal__default__account="+1234567890"
ZEROCLAW_channels__signal__default__http_url="http://localhost:50889"

# Centralized Peer Group Routing Overrides
# Map Signal senders to the target agents (e.g. allowing '+1234567890' or wildcard '*' for all)
ZEROCLAW_peer_groups__signal_group__external_peers='["+1234567890"]'
```

#### Application Configuration
Add the Signal channel and peer group routing config to `~/.local/sandbox/zeroclaw/.zeroclaw/config.toml`:

```toml
# 1. Configure the Signal channel instance
[channels.signal.default]
enabled = true
http_url = "http://localhost:50889"
account = "+1234567890"
approval_timeout_secs = 300
dm_only = true
ignore_attachments = false
ignore_stories = true

# 2. Configure peer group routing to map users/senders to agents
[peer_groups.signal_group]
channel = "signal.default"                 # Binds to channels.signal.default
agents = ["default"]                       # Routes inbound messages to the 'default' agent
external_peers = ["+1234567890", "uuid:xxxx-xxxx-xxxx"] # Allowed senders (E.164 phone numbers or UUIDs)
```

Make sure both the `signal-cli` daemon and the REST API wrapper (listening on port `50889`) are active. ZeroClaw will retrieve message payloads and send messages through this endpoint.

#### Tying Senders to Agents
Unlike other systems that map senders to a global `default_owner`, ZeroClaw utilizes **Peer Groups** to authorize senders and route them to specific agents:

##### Method A: Auto-Admittance via Peer Group
Specify the allowed sender phone numbers (or privacy UUIDs) in the `external_peers` list under a `[peer_groups.<name>]` block. 
- Senders in this list are automatically admitted.
- Their messages are routed directly to the agents listed in `agents`.

##### Method B: Wildcard Admittance (Open Channel)
To allow anyone to message the agent without individual phone number allowlisting:
- Set `external_peers = ["*"]` in the peer group config.
- Any incoming Signal sender will be accepted and routed to the configured agent.

##### Pairing Guard Note
While ZeroClaw supports a dynamic `PairingGuard` pairing flow (exchanging a code using `/bind <code>`) for **LINE** and **WeChat** channels when `dm_policy = "pairing"` is active, the **Signal** channel relies on static configuration of the allowed sender E.164 phone numbers/UUIDs in the `external_peers` slice (or environment overrides) to verify and map users.

## Search, Retrieval, Embedding & Reranking Configuration

ZeroClaw contains a self-contained, native SQLite-based hybrid memory system. It integrates Full-Text Search (FTS5) and vector search directly into its SQLite datastore, removing the need for external vector database servers. The persistent memory system automatically handles context compression, conversation history limits, and user preference storage.

Reranking Configuration: ZeroClaw includes a built-in weighted hybrid search (0.7 vector similarity / 0.3 keyword FTS) that does not require an external reranker. 

Add the following to your `config.toml` configuration file (located in the sandboxed home directory at `~/.local/sandbox/zeroclaw/.zeroclaw/config.toml`):

```toml
[memory]
# Native hybrid (keyword FTS + vector similarity) SQLite backend
backend = "sqlite.default"

embedding_model = "qwen3-embedding"
embedding_provider = "custom:http://localhost:50082/v1"

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
max_actions_per_hour = 100
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
1. **Source Schema Definition**: Open the configuration schema module at [schema.rs](scratch/zeroclaw/crates/zeroclaw-config/src/schema.rs) and inspect the `Config` struct (and its nested types) that derive `Configurable`.
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


### Sandboxing Profile
ZeroClaw utilizes a **Relaxed Namespaces Profile** for systemd isolation. Based on auditing the source code of ZeroClaw (`v0.8.0-beta-1`), these permissions are required:

1. **Namespace Support**
   - **Properties Omitted**: `ProtectProc=invisible`, `ProcSubset=pid`, and `RestrictNamespaces=yes`.
   - **Rationale**: ZeroClaw features a built-in user namespace-based tool execution sandbox (`crates/zeroclaw-runtime/src/security/bubblewrap.rs`). Restricting namespaces or procfs traversal inside the systemd service would block the agent's ability to spawn nested sandboxes using `bwrap`.

2. **Writable & Executable Memory (WASM Plugins)**
   - **Property Set**: `MemoryDenyWriteExecute=no`.
   - **Rationale**: ZeroClaw supports WebAssembly plugins (`plugins-wasm` feature in the runtime). Blocks or strict JIT filters in systemd would prevent the WASM compiler (e.g. Wasmtime) and Python/JIT tool dependencies from allocating writeable/executable memory ranges.

3. **Physical Devices (USB / Microcontrollers)**
   - **Property Set**: `PrivateDevices=yes` by default.
   - **Rationale**: For security, physical hardware devices are hidden. However, if you are actively using hardware discovery (`zeroclaw hardware discover`) or board flashing (`zeroclaw peripheral flash-nucleo`) over serial/USB, you must configure `PrivateDevices=no` to allow device node access under `/dev`.

