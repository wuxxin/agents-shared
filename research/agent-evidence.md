# Agent Feature Evidence Log

This file contains exact files, line numbers, directory names, and commands used to discover features for the 7 agents.

---

## 1. hermes-agent
- **OpenAI Proxy / Override Support**:
  - **Chat + Vision**: Configured in `cli-config.yaml` / `~/.hermes/config.yaml` under `model: base_url` and `model: provider` (set to `custom`, `lmstudio`, `ollama`, `vllm`, `llamacpp`). [cli-config.yaml.example:L46-55](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/hermes-agent/cli-config.yaml.example#L46-L55).
  - **Embedding**: Not implemented in code (only placeholder comments in [auxiliary_client.py:L4430](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/hermes-agent/agent/auxiliary_client.py#L4430)).
  - **Rerank**: Not supported.
  - **TTS**: Supported. Custom base URL can be defined under `tts.openai.base_url`. Verified in [tts_tool.py:L1032-1034](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/hermes-agent/tools/tts_tool.py#L1032-L1034).
  - **STT**: Supported. Custom base URL can be defined under `stt.openai.base_url` or via env var `STT_OPENAI_BASE_URL`. Verified in [transcription_tools.py:L1759-1761](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/hermes-agent/tools/transcription_tools.py#L1759-L1761) and [transcription_tools.py:L99](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/hermes-agent/tools/transcription_tools.py#L99).
  - **Image Gen**: OpenAI image gen (`dall-e`) is supported natively via `openai` and `openai-codex` plugins. No custom base URL configuration is exposed, but client uses standard `openai.OpenAI()` which respects `OPENAI_BASE_URL` env var. Verified in [plugins/image_gen/openai/__init__.py:L273](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/hermes-agent/plugins/image_gen/openai/__init__.py#L273). Automatic1111 is NOT supported.
- **Signal Channel Integration**:
  - **Protocol/Daemon**: Uses `signal-cli` daemon running in HTTP mode (SSE events for inbound, HTTP JSON-RPC 2.0 for outbound). [gateway/platforms/signal.py:L1-12](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/hermes-agent/gateway/platforms/signal.py#L1-L12).
  - **Inbound Attachments**: Supported via `getAttachment` RPC. [gateway/platforms/signal.py:L665-688](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/hermes-agent/gateway/platforms/signal.py#L665-L688).
  - **Outbound Attachments**: Supported via JSON-RPC parameter `attachments`. [gateway/platforms/signal.py:L1410-1502](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/hermes-agent/gateway/platforms/signal.py#L1410-L1502).
  - **Markdown Rendering**: Formatted to plain text + native Signal `bodyRanges` formatting in [gateway/platforms/signal_format.py](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/hermes-agent/gateway/platforms/signal_format.py).
  - **Emoji Reaction**: Sends `👀` during execution, swaps to `✅` (success) or `❌` (failure). Configurable via `SIGNAL_REACTIONS` env var (true/false). [gateway/platforms/signal.py:L1627-1672](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/hermes-agent/gateway/platforms/signal.py#L1627-L1672).
  - **Image to Vision**: Guessed from magic bytes / MIME starting with `image/` or `MessageType.PHOTO`, then routed to vision pipeline. [gateway/platforms/signal.py:L717-718](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/hermes-agent/gateway/platforms/signal.py#L717-L718) and [gateway/run.py:L10103-10104](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/hermes-agent/gateway/run.py#L10103-L10104).
  - **Audio to STT**: Guessed as `.aac` or `.mp3` from magic bytes, losslessly remuxed using `ffmpeg` from raw AAC to M4A, classified as `MessageType.VOICE`, and automatically transcribed via the STT pipeline. Configurable in `cli-config.yaml` under `stt:` section. [gateway/platforms/signal.py:L141-193](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/hermes-agent/gateway/platforms/signal.py#L141-L193) and [gateway/run.py:L14615-14670](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/hermes-agent/gateway/run.py#L14615-L14670).

---

## 2. ironclaw

### A. Legacy Code Paths and Engine
- **OpenAI Proxy / Override Support**:
  - **Chat + Vision**: Setting `LLM_BACKEND=openai_compatible` and `LLM_BASE_URL` (typically `http://localhost:21080/v1`) overrides Chat + Vision.
  - **Embedding**: Fully supported. Configured in [embeddings.rs:L1-110](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/ironclaw/src/config/embeddings.rs#L1-L110) and resolves via `EMBEDDING_BASE_URL`.
  - **Rerank**: Not supported.
  - **Image Gen**: Supported via `image_generate` tool in [image_gen.rs:L1-200](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/ironclaw/src/tools/builtin/image_gen.rs#L1-L200). Uses standard OpenAI `/images/generations` payload. No Automatic1111 support.
- **Signal Channel Integration**:
  - **Protocol/Daemon**: Communicates with `signal-cli daemon --http`. [signal.rs:L1-20](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/ironclaw/src/channels/signal.rs#L1-L20).
  - **Inbound Attachments**: Ignored. Sets `has_attachments = true` but does not populate `msg.attachments`. [signal.rs:L720-909](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/ironclaw/src/channels/signal.rs#L720-L909).
  - **Outbound Attachments**: Supported via `"attachments"` JSON-RPC parameter. [signal.rs:L560-610](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/ironclaw/src/channels/signal.rs#L560-L610).
  - **Markdown Rendering**: Sends raw Markdown without formatting.
  - **Emoji Reaction / Vision / STT**: Unsupported.

### B. Reborn Engine
- **Host-Mediated MCP Runtime**: Composes host-mediated MCP runtime and bundles `nearai` MCP extension [FEATURE_PARITY.md:L341](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/ironclaw/FEATURE_PARITY.md#L341).
- **Persistent Tool Approvals**: Reborn stores `AlwaysAllow` approval policies [FEATURE_PARITY.md:L342](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/ironclaw/FEATURE_PARITY.md#L342).
- **Slack Events Routing**: `ironclaw-reborn serve` handles events, slash-commands, and pairing panels [FEATURE_PARITY.md:L838](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/ironclaw/FEATURE_PARITY.md#L838).
- **EventStreamManager**: Transport-neutral event stream for `/events` and `/ws` [FEATURE_PARITY.md:L51](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/ironclaw/FEATURE_PARITY.md#L51).
- **Trace Commons**: Opt-in runtime capture queue and credit notices via `TraceClientHost` [FEATURE_PARITY.md:L274](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/ironclaw/FEATURE_PARITY.md#L274).

---

## 3. librefang
- **OpenAI Proxy / Override Support**:
  - **Chat + Vision**: Configured globally in the `[provider_urls]` table. [librefang.toml.example:L1-100](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/librefang/librefang.toml.example#L1-L100).
  - **Embedding**: Configured in `[memory]` and uses `[provider_urls]` overrides.
  - **Rerank**: Not supported.
  - **Image Gen**: Standard OpenAI Images API via global URL overrides. No Automatic1111 support.
- **Signal Channel Integration**:
  - **Protocol/Daemon**: Runs as out-of-process Python sidecar via `signal-cli-rest-api`. [signal.py:L1-200](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/librefang/sdk/python/librefang/sidecar/adapters/signal.py#L1-L200).
  - **Inbound Attachments**: Ignored (empty envelopes skipped). [signal.py:L250-320](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/librefang/sdk/python/librefang/sidecar/adapters/signal.py#L250-L320).
  - **Outbound Attachments**: Unsupported (replaced by `"(Unsupported content type)"` placeholder). [signal.py:L597-636](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/librefang/sdk/python/librefang/sidecar/adapters/signal.py#L597-L636).
  - **Markdown Rendering / Reactions / Vision / STT**: Not supported.

---

## 4. nanobot
- **OpenAI Proxy / Override Support**:
  - **Chat + Vision**: Configured per provider in `ProvidersConfig` via `providers.custom.apiBase` or `providers.ollama.api_base`. [schema.py:L224-239](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/nanobot/nanobot/config/schema.py#L224-L239).
  - **Embedding / Rerank**: Not supported.
  - **Image Gen**: Supported via `CustomImageGenerationClient` mapping to `providers.custom.apiBase`. [image_generation.py:L1100-1150](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/nanobot/nanobot/providers/image_generation.py#L1100-L1150).
  - **TTS (Text-to-Speech)**: Not supported in the codebase (no files or config references exist).
  - **STT (Speech-to-Text)**: Configured in `[transcription]` section. Uses OpenAITranscriptionProvider mapping `api_base` to local Whisper servers via `providers.openai.api_base`. [transcription_registry.py:L52-55](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/nanobot/nanobot/audio/transcription_registry.py#L52-L55) and [transcription.py:L99-103](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/nanobot/nanobot/audio/transcription.py#L99-L103).
- **Signal Channel Integration**:
  - **Protocol/Daemon**: Direct HTTP JSON-RPC daemon adapter. [signal.py:L1-100](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/nanobot/nanobot/channels/signal.py#L1-L100).
  - **Inbound Attachments**: Supported (copies files from `attachments_dir` to `media_paths`). [signal.py:L890-934](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/nanobot/nanobot/channels/signal.py#L890-L934).
  - **Outbound Attachments**: Supported via `media` array param.
  - **Markdown Rendering**: Yes. Formatted using `_markdown_to_signal` parsing into native Signal `textStyle` `bodyRanges`. [signal.py:L108-150](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/nanobot/nanobot/channels/signal.py#L108-L150).
  - **Emoji Reaction**: Unsupported.
  - **Image to Vision**: Yes (media paths forwarded to message bus for Ollama vision processing).
  - **Audio to STT**: Supported. Inbound audio notes are copied to media paths and automatically transcribed via the configured global `[transcription]` provider (e.g., local Whisper/OpenAI) before reaching the agent. [transcription.py:L135-203](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/nanobot/nanobot/audio/transcription.py#L135-L203).
- **Local Memory, Compaction & Dreaming**:
  - **Compaction**: Uses `session_ttl_minutes` and `consolidation_ratio` to evict and summarize old messages in `history.jsonl` via `Consolidator` [memory.py:L675-707](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/nanobot/nanobot/agent/memory.py#L675-L707).
  - **Dream Consolidation**: Runs background cron/schedule loops to extract facts from recent history. Restricts the agent to reading history and writing updates to long-term memory files: `MEMORY.md` (facts), `SOUL.md` (prompts/directives), `USER.md` (profiles), and `skills/` (code generation for custom tools). [memory.py:L542-582](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/nanobot/nanobot/agent/memory.py#L542-L582).

---

## 5. nanoclaw
- **OpenAI Proxy / Override Support**:
  - **Chat + Vision / Embedding / Rerank / Image Gen**: Delegated to OneCLI SDK and Gateway via `ONECLI_URL` in [config.ts:L51](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/nanoclaw/src/config.ts#L51) and [container-runner.ts:L55](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/nanoclaw/src/container-runner.ts#L55).
- **Signal Channel Integration**:
  - **Protocol/Daemon**: TCP socket JSON-RPC client connected to `signal-cli daemon --tcp`. [signal.ts:L33-200](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/nanoclaw/src/channels/signal.ts#L33-L200) (channels branch).
  - **Inbound Attachments**: Supported (copies files from `signalDataDir/attachments/img.id`).
  - **Outbound Attachments**: Supported (saves to temp files and passes paths).
  - **Markdown Rendering**: Yes. Parses using `parseSignalStyles` and passes `textStyle` array.
  - **Reactions/Emojis**: Unsupported.
  - **Image to Vision**: Yes, outputs `[Image: <path>]` into message content.
  - **Audio to STT**: Yes, transcribed via local Whisper (`WHISPER_BIN`) or OpenAI Whisper (`OPENAI_API_KEY`). **Note**: OpenAI Whisper endpoint is hardcoded to `https://api.openai.com/v1/audio/transcriptions` and does not support custom base URL overrides. [signal.ts:L364-410](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/nanoclaw/src/channels/signal.ts#L364-L410) (channels branch).

---

## 6. picoclaw
- **OpenAI Proxy / Override Support**:
  - **Chat + Vision**: Configured per model in `config.json` via `api_base`. [config.example.json:L33-108](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/picoclaw/config/config.example.json#L33-L108).
  - **Embedding / Rerank / Image Gen**: Not supported.
- **Signal Channel Integration**:
  - **Protocol/Daemon / Features**: Not supported (only mentioned in `ROADMAP.md` as planned).

---

## 7. zeroclaw
- **OpenAI Proxy / Override Support**:
  - **Chat + Vision**: Override via `base_url` under `compatible` / `openai` provider profiles. [schema.rs:L128-136](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/zeroclaw/crates/zeroclaw-config/src/schema.rs#L128-L136).
  - **Embedding**: Fully supported using `OpenAiEmbedding` which parses `base_url`. [embeddings.rs:L51-100](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/zeroclaw/crates/zeroclaw-memory/src/embeddings.rs#L51-L100).
  - **Rerank**: Not supported (warning logged in [memory_strategy.rs:L28-41](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/zeroclaw/crates/zeroclaw-runtime/src/agent/memory_strategy.rs#L28-L41)).
  - **Image Gen**: Supported via `image_gen` tool, but hardcoded to `fal.ai` using `FAL_API_KEY`. No OpenAI images or Automatic1111 support. [image_gen.rs:L50-120](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/zeroclaw/crates/zeroclaw-tools/src/image_gen.rs#L50-L120).
- **Signal Channel Integration**:
  - **Protocol/Daemon**: Connects to `signal-cli daemon --http`. Inbound via SSE `/api/v1/events` and outbound JSON-RPC `/api/v1/rpc`. [signal.rs:L41-72](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/zeroclaw/crates/zeroclaw-channels/src/signal.rs#L41-L72).
  - **Inbound Attachments**: Ignored. [signal.rs:L353-359](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/zeroclaw/crates/zeroclaw-channels/src/signal.rs#L353-L359).
  - **Outbound Attachments**: Not supported. [signal.rs:L442-458](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/zeroclaw/crates/zeroclaw-channels/src/signal.rs#L442-L458).
  - **Markdown Rendering**: Unsupported.
  - **Emoji Reaction**: Supported via `add_reaction` / `remove_reaction` calling `sendReaction` JSON-RPC. [signal.rs:L688-708](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/zeroclaw/crates/zeroclaw-channels/src/signal.rs#L688-L708).
