# Agent Feature Matrix & Signal Channel Integration

This report summarizes feature discovery across the 7 agents. All findings are verified directly from their source code repositories in the `scratch/` directory.

---

## 1. Feature Matrix

| Agent | Chat/Vision Override | Embeddings | Rerank | STT / TTS Overrides | Image Gen Backend | Signal Daemon / Protocol | Signal Attachments (In/Out) | Signal Markdown | Signal Reactions | Signal Vision | Signal Audio/STT |
| :--- | :---: | :---: | :---: | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **hermes-agent** | Yes | No | No | Yes | OpenAI compatible | `signal-cli daemon --http` (SSE/HTTP) | Yes / Yes | Yes (native) | Yes (👀/✅/❌) | Yes | Yes |
| **ironclaw** (Legacy) | Yes | Yes | No | No | OpenAI compatible | `signal-cli daemon --http` (HTTP JSON-RPC) | No (ignored) / Yes | No | No | No | No |
| **librefang** | Yes | Yes | No | Yes | OpenAI compatible | `signal-cli-rest-api` (Sidecar client) | No (ignored) / No | No | No | No | No |
| **nanobot** | Yes | No | No | STT Only | OpenAI compatible | `signal-cli daemon --http` (HTTP JSON-RPC) | Yes / Yes | Yes (native) | No | Yes | Yes |
| **nanoclaw** | Delegated | Delegated | Delegated | No (hardcoded endpoint) | Delegated | `signal-cli daemon --tcp` (TCP JSON-RPC) | Yes / Yes | Yes (native) | No | Yes | Yes (local/OpenAI) |
| **picoclaw** | Yes | No | No | No | No | None (Roadmap only) | N/A | N/A | N/A | N/A | N/A |
| **zeroclaw** | Yes | Yes | No | No | fal.ai Flux (FAL_API_KEY) | `signal-cli daemon --http` (SSE/JSON-RPC) | No (ignored) / No | No | Yes (native) | No | No |

---

## 2. Key Findings Summary

### OpenAI Proxy Compatibility (Port 51080)
- **Chat + Vision**: Supported by almost all agents. 
  - **Hermes** supports it under custom providers.
  - **IronClaw** via `LLM_BASE_URL` with `openai_compatible` backend.
  - **LibreFang** via `[provider_urls]`.
  - **NanoBot** via `providers.custom.apiBase`.
  - **PicoClaw** via `api_base` per model in config list.
  - **ZeroClaw** via `base_url` under provider configs.
  - **NanoClaw** delegates all LLM/vision operations to the OneCLI gateway (`ONECLI_URL`), which manages these overrides.
- **Embeddings**: Only **IronClaw**, **LibreFang**, and **ZeroClaw** implement embeddings with customizable base URL overrides. NanoClaw delegates this to OneCLI. Other agents do not support RAG/embeddings.
- **Rerank**: **Not supported** by any agent. ZeroClaw declares it in the schema, but logs a warning at runtime noting the feature is not implemented.
- **STT / TTS**: **Hermes**, **LibreFang**, **NanoClaw**, and **NanoBot** support audio processing, but NanoClaw's OpenAI Whisper STT client uses a hardcoded URL (`https://api.openai.com/v1/audio/transcriptions`), failing to honor custom local STT base URLs. NanoBot supports local Whisper speech-to-text via its `transcription` configuration.
- **Image Generation**: **Hermes**, **IronClaw**, **LibreFang**, and **NanoBot** support standard OpenAI `/images/generations` endpoints. **ZeroClaw**'s image tool is hardcoded to talk to `fal.ai` Flux models via `FAL_API_KEY`. None support Automatic1111 directly.

### Signal Channel Integration
- **Daemon Protocols**:
  - `signal-cli daemon --http` (SSE for inbound, JSON-RPC HTTP for outbound): Used by **Hermes**, **IronClaw**, **ZeroClaw**, and **NanoBot**.
  - `signal-cli-rest-api` via Python wrapper: Used by **LibreFang**.
  - `signal-cli daemon --tcp` newline-delimited TCP socket: Used by **NanoClaw**.
- **Attachments**:
  - **Hermes**, **NanoBot**, and **NanoClaw** support both sending and receiving attachments. NanoClaw uses disk-written temporary file structures for outbound attachments.
  - **IronClaw** can send but ignores inbound.
  - **ZeroClaw** and **LibreFang** ignore/unsupport attachments in both directions.
- **Markdown Style Rendering**:
  - **Hermes**, **NanoBot**, and **NanoClaw** support parsing Markdown into Signal's native `textStyle` bodyRange formatting.
- **Emoji Reactions**:
  - **Hermes** and **ZeroClaw** are the only agents that support reacting to messages with emojis.
- **Voice/Audio Transcription**:
  - **Hermes** automatically converts inbound audio to `.m4a` via `ffmpeg` and transcribes it.
  - **NanoClaw** automatically transcribes inbound audio via local Whisper (`WHISPER_BIN`) or the OpenAI Whisper API.
  - **NanoBot** copies voice notes to media paths and transcribes them automatically when the global `[transcription]` provider is enabled.

---

## 3. IronClaw Legacy vs. Reborn Engine Split

### Legacy Engine (v1/v2 config and providers)
- Employs local configuration settings, standard environment variables (`LLM_BASE_URL`), and the `signal.rs` channel implementation.
- Employs the `ironclaw_embeddings` crate for database RAG logic.

### Reborn Engine
- **Host-Mediated MCP Runtime**: Composes host-mediated MCP runtime and auto-seeds/configures the NEAR AI MCP extension when `NEARAI_BASE_URL`/`NEARAI_API_KEY` are provided.
- **Persistent Tool Approvals**: Reborn registers persistent `AlwaysAllow` approval configurations on tool calls.
- **Slack Events Channel**: Moves beyond simple REST hooks to feature Slack Events API signing, slash-command recovery, and personal binding pairing code flows.
- **EventStreamManager**: A transport-neutral event stream supporting SSE broadcast (`/events`) and WebSocket (`/ws`) integrations.
- **Trace Commons Client**: Opt-in runtime capture queue and credit notices via `TraceClientHost` communicating with the remote `tracedao-server`.
- **Durable Job Triggers**: Reborn schedules use first-class one-shot triggers (`TriggerSchedule::Once`) rather than legacy year-pinned cron workarounds.
- **Sandboxed Execution**: Employs Bubblewrap / Docker sandboxing process plans (`SandboxProcessPlan` / `ProcessSandboxBackend`).

---


---

## 5. Integrating OpenCode as a Coding Agent

OpenCode can function as a coding assistant in two primary configurations:
1. **Subprocess Tool (One-Shot / Shell)**: Spawning `opencode run "<instruction>"` or interactive `tmux`/`pty` wrappers.
2. **Model Context Protocol (MCP) Server**: Exposing OpenCode via stdio (`opencode --stdio`) to allow host assistants to invoke it dynamically.

Here is the integration plan for assistants currently lacking native OpenCode support:

### 1. IronClaw (Legacy / Reborn)
- **Legacy (v1/v2)**: 
  - **Proposed Implementation**: Add a new built-in tool under `src/tools/builtin/opencode_cli.rs` mapping to the `opencode` binary.
  - **Mechanism**: The tool takes a string instruction and target path, executes `opencode run "<instruction>"` inside the target directory, and captures stdout/stderr.
- **Reborn**:
  - **Proposed Implementation**: OpenCode is natively supported as an MCP stdio-transport server [FEATURE_PARITY.md:L340](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/ironclaw/FEATURE_PARITY.md#L340).
  - **Mechanism**: Reborn launches `opencode --stdio` inside the sandbox workspace, injecting the standard tool definition into the orchestrator.

### 2. LibreFang
- **Proposed Implementation**: Implement a new `LlmDriver` class in `crates/librefang-llm-drivers/src/drivers/opencode.rs` (similar to Aider and Claude Code).
- **Mechanism**: 
  - Spawns the CLI in print/non-interactive mode using `opencode run --yes-always`.
  - Integrates the active repository context by writing temporary workspace configuration files.

### 3. PicoClaw
- **Proposed Implementation**: Implement a provider under `pkg/providers/cli/opencode_cli_provider.go` (similar to `claude_cli_provider.go`).
- **Mechanism**:
  - Wraps CLI calls to `opencode` by setting up standard input/output streams.
  - The provider parses the resulting diff output and maps it to the standard `LLMResponse` structures.

### 4. NanoBot
- **Proposed Implementation**: Create a new tool file `nanobot/tools/opencode.py`.
- **Mechanism**: 
  - Exposes `opencode_run` to the tool registry.
  - Executes subprocess commands to the local `opencode` CLI within sandboxed directories.
