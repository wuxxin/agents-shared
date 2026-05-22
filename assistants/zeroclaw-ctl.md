# ZeroClaw Agent Management Guide

`zeroclaw-ctl` manages the ZeroClaw Gateway and agent runtime, providing a hardened execution environment that supports Bubblewrap/Landlock isolation.

- **Source Code**: [GitHub - zeroclaw-labs/zeroclaw](https://github.com/zeroclaw-labs/zeroclaw)
- **Arch/AUR Packages**: `zeroclaw` (AUR, Rust source compilation), `zeroclaw-bin` (AUR, prebuilt binary distribution), `zeroclaw-git` (AUR, git-based).

## Installation

```bash
./assistants/zeroclaw-ctl install
```

## Commands

`zeroclaw-ctl` supports all standard management operations. For detailed command reference and sandboxing path defaults, see [Standard Control Wrappers](file:///home/wuxxin/agent-shared/code/aur-packages/assistants/assistants.md#standard-control-wrappers-assistant-ctl).

## Configuration & Ports

- **Default Port**: `42617` (ZeroClaw Gateway)
- **Port Customization Options**:
  If the default port (`42617`) needs to be modified, you can configure the new port using:
  **Systemd/Env File (Recommended)**: Edit the configuration environment file at `~/.config/systemd/user/zeroclaw.env` (either directly or via `./assistants/zeroclaw-ctl edit`) and set `ZEROCLAW_PORT=<port_number>`. The systemd service will start the gateway with the `zeroclaw gateway start --port $ZEROCLAW_PORT` command (since `--port` is a parameter on the `start` subcommand, not the base `gateway` command).

## Onboarding

1. **Install Service**: Run `./assistants/zeroclaw-ctl install` to initialize `~/.local/share/zeroclaw` and register the systemd user service.
2. **Interactive Onboarding**: Run the onboarding setup wizard with `./assistants/zeroclaw-ctl exec onboard`. This will guide you through providers, models, channels, and agent configuration, outputting a minimal four-section configuration to `~/.local/share/zeroclaw/.zeroclaw/config.toml`.
3. **Verify Connection**: Run `./assistants/zeroclaw-ctl exec auth status` to check credentials and model fallback status. Test chat via `./assistants/zeroclaw-ctl exec agent -a <agent_alias>`.
4. **Start Gateway**: Start the service via `./assistants/zeroclaw-ctl start` to launch the background daemon (listening on port `42617`). Watch logs with `./assistants/zeroclaw-ctl logs -f`.
5. **Switch to Local Inference & Qwen3**: Edit `~/.local/share/zeroclaw/.zeroclaw/config.toml` and configure the local provider:
```toml
[providers.models.openai.local]
uri = "http://127.0.0.1:50080/v1"
model = "qwen3"
api_key = "unused"
```
Point the target agent at this provider using `model_provider = "openai.local"` under `[agents.<alias>]`.
```


## Signal Channel Configuration

ZeroClaw supports native Signal integration. It communicates with the daemon via the REST API wrapper.

### Configuration

Add the following to your `config.toml` configuration file (located in the sandboxed home directory at `~/.local/share/zeroclaw/.zeroclaw/config.toml`):

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

## Search, Retrieval & Embedding Configuration

ZeroClaw contains a self-contained, native SQLite-based hybrid memory system. It integrates Full-Text Search (FTS5) and vector search directly into its SQLite datastore, removing the need for external vector database servers. The persistent memory system automatically handles context compression, conversation history limits, and user preference storage.

### Configuration

Add the following to your `config.toml` configuration file (located in the sandboxed home directory at `~/.local/share/zeroclaw/.zeroclaw/config.toml`):

```toml
[memory]
# Native hybrid (keyword FTS + vector similarity) SQLite backend
backend = "sqlite-hybrid"

embedding_model = "qwen3-embedding"
embedding_provider = "custom:http://127.0.0.1:50080/v1"

```

### Reranking Configuration

ZeroClaw includes a built-in weighted hybrid search (0.7 vector similarity / 0.3 keyword FTS) that does not require an external reranker. 

## Speech-to-Text Integration

ZeroClaw supports speech-to-text (STT) transcription by routing voice payloads to the local `local-speech-to-text` service.

### Configuration

Add the transcription provider configuration to `~/.local/share/zeroclaw/.zeroclaw/config.toml`:

```toml
# 1. Define the transcription provider
[providers.transcription.local_whisper.local_stt]
uri = "http://localhost:50090/v1/audio/transcriptions"
bearer_token = "dummy"
model = "whisper"

# 2. Reference this provider in your agent configuration
[agents.default]
transcription_provider = "local_whisper.local_stt"
```

Alternatively, you can configure it globally in the legacy `[transcription]` section of `config.toml`:

```toml
[transcription]
enabled = true

[transcription.local_whisper]
url = "http://localhost:50090/v1/audio/transcriptions"
bearer_token = "dummy"
```

### OpenClaw Migration

ZeroClaw supports importing history and conversation memory logs from an existing OpenClaw installation. To perform the migration, run:
```bash
./assistants/zeroclaw-ctl exec migrate openclaw
```
This command imports the legacy SQLite database memory logs directly into ZeroClaw's memory format.

## Implementation & Security Considerations

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
   - **Rationale**: The agent's persistent directories (`~/.local/share/zeroclaw`, `~/agent-shared`, and specified `AGENT_PRIVATE_MOUNTS`) are bind-mounted read-write, while the rest of the host filesystem is mounted read-only or hidden entirely.
