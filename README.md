# Local Agent Ecosystem & Assistant Orchestrator

This repository is a centralized orchestration hub for deploying, sandboxing, and monitoring local AI assistants, speech-to-text engines, local inference models, and communication integrations. It provides systemd-confinement configurations, bubblewrap (`bwrap`) isolation wrappers, and standardized daemon control utilities (`*-ctl` scripts) to ensure secure and isolated agent execution on Linux while facilitating structured inter-agent collaboration.

## Assistant Software covered

See [Current Weekly Development Status](research/weekly-devel-activity.md) for GIT development.


| Assistant | Language & Runtime | Embedding | Reranking | Search & Retrieval | Signal | STT |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **[ZeroClaw](#zeroclaw)** | Rust (Source) <br> Rust Backend + Web GUI| Remote & Local | Hybrid & Local | SQLite Hybrid (Vector & FTS5) | Native | Local |
| **[IronClaw](#ironclaw)** | Rust (Source) <br> Rust Backend + Web GUI | Remote & Local | Native (RRF) | PostgreSQL + pgvector / Hybrid (FTS + Vector) | Native | Local |
| **[Hermes](#hermes)** | Python (Source) <br> frozen Python Backend + Web GUI | Remote & Local | Native & Local | SQLite FTS5 / Vector / RAG | Native | Local |
| **[NanoBot](#nanobot)** | Python (Source) <br> Python CLI (via `uv`) | Remote & Local | Via MCP Tool | RAG / Document Store / MCP | Native | Local |

also covered, but currently not point of interest:

| Assistant | Language & Runtime | Embedding | Reranking | Search & Retrieval | Signal | STT |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **[LibreFang](#librefang)** | Rust (Source) <br> Rust Backend + Web GUI | Remote & Local | Native & Local | SQLite & Vector / MCP | Native | Local |
| **[PicoClaw](#picoclaw)** | Go (Source) <br> Go Backend + Web GUI | Remote & Local via MCP | Via MCP | JSON state / MCP | No | Via MCP |
| **[NanoClaw](#nanoclaw)** | TypeScript (Source) <br> Node.js Webhook Backend | Remote & Local via Tools | Via Custom Skills/MCP | SQLite state / Custom Tools / MCP | No | Via Custom Tools |


## Integrations

### Local Chat Services
- **Description**: Manages persistent `llama-server` instances for chat/vision LLM completions (`local-chat.sh`).
- **Sandboxing**: Requires `PrivateDevices=no` to access `/dev/dri` and `/dev/kfd`. Enforces `ProtectSystem=strict` while bind-mounting the user's home configuration and granting read-write access to `/data/public/machine-learning`.
- **Features**: Chat completions (`50080`) running with 3 parallel slots (80,000 tokens context size each, total 240,000 tokens).
- Documentation: [local-chat.md](assistants/local-chat.md)

### Local Embedding Services
- **Description**: Manages persistent `llama-server` instances for text embeddings (`local-embedding.sh`).
- **Sandboxing**: Requires `PrivateDevices=no` to access `/dev/dri` and `/dev/kfd`. Enforces `ProtectSystem=strict` while bind-mounting the user's home configuration and granting read-write access to `/data/public/machine-learning`.
- **Features**: Standalone text embedding server (`50082`) running with mean pooling and ROCm GPU offloading.
- Documentation: [local-embedding.md](assistants/local-embedding.md)

### Local Reranking Services
- **Description**: Manages persistent `llama-server` instances for document reranking (`local-rerank.sh`). 
- **Sandboxing**: Requires `PrivateDevices=no` to access `/dev/dri` and `/dev/kfd` for GPU-accelerated synthesis (unless run in cpu only mode). Enforces `ProtectSystem=strict` while restricting filesystem access to the home directory and read-only system files.
- **Features**: Rerank Service (`50086`) services.
- Documentation:  [local-rerank.md](assistants/local-rerank.md)

### Local Speech-to-Text
- **Description**: Manages a persistent `whisper-server` instance for speech-to-text (STT) transcription. Serves an OpenAI-compatible audio transcription API on port 50090.
- **Sandboxing**: Requires `PrivateDevices=no` to access `/dev/dri` and `/dev/kfd` for GPU-accelerated synthesis (unless run in cpu only mode). Enforces `ProtectSystem=strict` while restricting filesystem access to the home directory and read-only system files.
- **Features**: audio transcoding using `ffmpeg`.
- Documentation: [local-speech-to-text.md](assistants/local-speech-to-text.md)

### Local Text-to-Speech
- **Description**: Manages a persistent `qwen3-tts-server` instance for text-to-speech (TTS) synthesis. Serves an OpenAI-compatible audio synthesis API on port 50095.
- **Sandboxing**: Requires `PrivateDevices=no` to access `/dev/dri` and `/dev/kfd` for GPU-accelerated synthesis (unless run in `cpu` mode). Enforces `ProtectSystem=strict` while restricting filesystem access to the home directory and read-only system files.
- **Features**: performance tuning modes cpu, fully parallelized CPU threading, and streaming/batch PCM generation.
- Documentation: [local-text-to-speech.md](assistants/local-text-to-speech.md)

### Local Image Services
- **Description**: Manages a persistent `sd-server` instance for image generation. Serves an OpenAI-compatible image generation API on port 50100.
- **Sandboxing**: Requires `PrivateDevices=no` to access `/dev/dri` and `/dev/kfd` for GPU-accelerated generation (unless run in `cpu` mode). Enforces `ProtectSystem=strict` while restricting filesystem access to the home directory and read-only system files.
- **Features**: Generates images using the `z_image_turbo-Q8_0.gguf` model with options for sampler steps, CFG scale, and backend routing.
- Documentation: [local-image.md](assistants/local-image.md)

### Local Inference Coordinator
- **Description**: Coordinator and wrapper script to manage the installation, state, and activation of all 6 local services (`local-inference.sh`).
- **Sandboxing**: Not a system service itself, but executes individual service scripts which utilize systemd user sandboxing.
- **Features**: Bulk installation, uninstall, lifecycle control (start, stop, restart), status reports, combined logs, and automatic propagation of environment overrides (e.g. LRR_OVERRIDE) to target services.
- Documentation: [local-inference.md](assistants/local-inference.md)

### Signal Integration
- **Description**: Connects agents to Signal. Runs a `signal-cli` daemon exposing both TCP and HTTP JSON-RPC interfaces. It also provides an optional Go-based REST API wrapper for robust, HTTP-based polling/webhook integrations (like linking LibreFang).
- **Sandboxing**: Standard filesystem hardening, but disables `MemoryDenyWriteExecute` because the underlying JVM (Java) requires it for JIT compilation. 
- **Features**: Account linking via QR code, dual daemon interfaces, and isolated home directory execution to prevent contamination.
- Documentation: [signal-ctl.md](assistants/signal-ctl.md)

The following assistants have native Signal channel integration available in their source code:
- [Hermes](assistants/hermes-ctl.md)
- [IronClaw](assistants/ironclaw-ctl.md)
- [LibreFang](assistants/librefang-ctl.md)
- [NanoBot](assistants/nanobot-ctl.md)
- [ZeroClaw](assistants/zeroclaw-ctl.md)

To configure them, refer to their specific configuration sections in their respective control guides.


## Helper Utilities

The repository contains several scripts under `scripts/` to assist with sandboxing, benchmarking, downloading models, and calibrating agent runtimes.

For details, see the [scripts/README.md](scripts/README.md).


## Default Ports

The following default ports are used by various agent systems and services to avoid conflicts. When integrating new agents, ensure their configured `PORT` or `WEBHOOK_PORT` does not overlap with existing infrastructure.

| Agent/Service | Default Port(s) | Description / Protocol |
|---------------|-----------------|------------------------|
| **Local-Chat** | [50080](http://localhost:50080) | Llama-server serving Chat/Vision LLM (embeddings disabled) |
| **Local-Embedding** | [50082](http://localhost:50082) | Llama-server serving Text Embeddings |
| **Local-Rerank** | [50086](http://localhost:50086) | Llama-server serving Document Reranking |
| **Local-Speech-To-Text** | [50090](http://localhost:50090) | Whisper-server audio transcription API (HTTP) |
| **Local-Text-to-Speech** | [50095](http://localhost:50095) | Qwen3-tts-server audio synthesis API (HTTP) |
| **Local-Image** | [50100](http://localhost:50100) | sd-server serving Image Generation API (HTTP) |
| **Signal-CLI** | [50889](http://localhost:50889) (optional: `50887`, `50888`) | REST API (TCP/HTTP JSON-RPC disabled by default in favor of secure UNIX socket) |
| **ZeroClaw** | [42617](http://localhost:42617) | ZeroClaw Gateway |
| **IronClaw** | [8080](http://localhost:8080) | IronClaw Web Gateway & HTTP Webhooks |
| **Hermes** | [8000](http://localhost:8000), [8642](http://localhost:8642), [9119](http://localhost:9119) | Hermes Messaging Gateway (API: 8642, UI: 9119) |
| **NanoBot** | [8790](http://localhost:8790) | NanoBot Gateway API |
| **LibreFang** | [4545](http://localhost:4545) | LibreFang daemon API (HTTP) |
| **PicoClaw** | [18790](http://localhost:18790), [18800](http://localhost:18800) | Gateway (HTTP/Webhook) & Launcher Web UI |
| **NanoClaw** | [3000](http://localhost:3000) | Webhook Server |


## Sandboxing Architecture

Agent runtimes in this repository operate under strict, layered sandboxing configurations via systemd user services to protect the host system while allowing agents to execute their tools securely. 

Two primary isolation profiles are used across all assistants:

### Strict Confinement Profile
Used by agents that execute tools directly or do not require creating new user namespaces for their internal sandboxing.
- `ProtectProc=invisible` and `ProcSubset=pid`: Hides other system processes.
- `RestrictNamespaces=yes`: Prevents the creation of new namespaces.
- `MemoryDenyWriteExecute=yes`: Prevents W^X memory mappings (unless specifically required by an interpreter).
- `PrivateTmp=yes`, `ProtectSystem=strict`, `PrivateDevices=yes`: Standard filesystem hardening.

### Relaxed Namespaces Profile
Used by agents that orchestrate sub-agents or use tools like Bubblewrap (`bwrap`), Rootless Podman, or Docker for internal sandboxing.
- `RestrictNamespaces=yes` is **omitted** to allow `bwrap` or Podman to create `CLONE_NEWUSER` and `CLONE_NEWNS` unprivileged namespaces.
- `ProtectProc=invisible` and `ProcSubset=pid` are **omitted** so `bwrap` can securely bind its own `/proc` filesystem.
- `NoNewPrivileges=yes` is maintained for modern `bwrap` compatibility.
- `PrivateDevices` may be disabled (`no`) if access to the container daemon or GPU devices is required.

---

## Assistants

### ZeroClaw
- **Major Features**: Rust-based security-focused agent gateway and runtime featuring built-in SQLite hybrid memory (vector + keyword FTS5) and native Landlock/Bubblewrap sandbox backends.
- **Language/Runtime**: Rust (Source) / Compiled binary (Rust Backend, no Web GUI).
- **Requirements**: Support for Linux namespace isolation or Landlock.
- **Sandboxing**: **Relaxed Namespaces Profile** is enforced via the systemd unit so that ZeroClaw can spawn secure nested sub-sandboxes via `bwrap` internally.
- **Memory**: Native SQLite-based memory system. Supports `sqlite` and `sqlite-hybrid` (vector + keyword FTS5) natively; can also use PostgreSQL or Qdrant.
- **Retention/Compression/Compaction**: Features time-decay scoring (evergreen Core category, time-decayed Conversation/others with a 7-day half-life), two-phase LLM-driven memory consolidation (Daily history + Core fact extraction) at the end of each turn, and periodic memory hygiene (every 12 hours) to archive, purge, and prune database rows.
- **Search & Retrieval**: Native hybrid search (0.7 vector similarity / 0.3 keyword FTS5) directly inside SQLite.
- **Autonomous 24/7 Support**: Yes — Built-in scheduling and task memory for unattended 24/7 operations.
- **Signal Support**: Yes — Native channel integration communicating via the Go REST API wrapper (port 50889).
- **Coding Agent Support**: Yes — Natively supports **OpenCode** as a coding worker tool (`opencode_cli`).
- **Local LLM & Inference**: Supports local GGUF models via OpenAI-compatible endpoints served by `local-chat` (port 50080) or Ollama.
- **Embedding Options**: Local embeddings using the `local-embedding` server (port 50082) or Ollama, or OpenAI-compatible embedding APIs.
- **Reranking Support**: Native weighted hybrid search, or routes to external local-rerank service (`http://localhost:50086/v1/rerank`).
- **STT/TTS Support**: Natively routes voice uploads to local Whisper server (`local-speech-to-text` on port 50090) and local TTS via Qwen3-tts (`local-text-to-speech` on port 50095).
- **Agent Client Protocol**: Yes — Native stdio-based ACP server via `zeroclaw-acp-bridge` and a dedicated `Acp` (Code) pane in the `zerocode` TUI.
- **Agent to Agent Protocol**: Yes — Built-in peer-to-peer delegation via the `delegate` tool, restricted by shared risk profiles and `delegation_policy` configurations.
- **Detailed Guide & Onboarding**: [zeroclaw-ctl.md](assistants/zeroclaw-ctl.md)


### IronClaw
- **Major Features**: Security-focused Agent OS providing WASM-sandboxed tool execution, credential protection with leak detection, prompt injection defense, and endpoint allowlisting. Built as a Rust reimplementation of OpenClaw with a focus on privacy, zero-trust architecture, and self-expanding capabilities via dynamic WASM tool building.
- **Language/Runtime**: Rust (Source) / Compiled binary (Rust Backend + Web Gateway GUI).
- **Requirements**: PostgreSQL 15+ with [pgvector](https://github.com/pgvector/pgvector) extension. Rust 1.92+ for source builds. NEAR AI account for default authentication.
- **Sandboxing**: **Relaxed Namespaces Profile** to support WASM sandbox execution (wasmtime) and optional Docker sandbox orchestrator/worker pattern. `MemoryDenyWriteExecute=no` required for WASM JIT compilation.
- **Memory**: PostgreSQL 15+ database with the `pgvector` extension. Workspace filesystem provides flexible path-based storage for notes, logs, and context. Identity files maintain settings and contexts.
- **Retention/Compression/Compaction**: Context compaction supports auto-summarization of history. Settings and metadata are persisted in PostgreSQL.
- **Search & Retrieval**: Hybrid search combining full-text search and vector similarity via Reciprocal Rank Fusion (RRF) backed by PostgreSQL.
- **Autonomous 24/7 Support**: Yes — Heartbeat support (`HEARTBEAT_ENABLED`) for background tasks and cron jobs.
- **Signal Support**: Yes — Native integration communicating via the `signal-cli` HTTP daemon (port 50889).
- **Coding Agent Support**: Yes — Supports external coding agents via Agent Client Protocol (e.g. `ironclaw acp add goose`). No native OpenCode support.
- **Local LLM & Inference**: Supports local GGUF models via OpenAI-compatible endpoints served by `local-chat` (port 50080) or Ollama.
- **Embedding Options**: Local embeddings using the `local-embedding` server (port 50082) or Ollama, or remote/Ollama embeddings.
- **Reranking Support**: Native Reciprocal Rank Fusion (RRF) algorithm. No external reranker required.
- **STT/TTS Support**: Local STT via OpenAI-compatible transcription endpoint (`local-speech-to-text` on port 50090). No native TTS support.
- **Agent Client Protocol**: Yes — Configurable external coding agents using ACP commands (e.g. `ironclaw acp add goose`).
- **Agent to Agent Protocol**: Yes — Orchestrator/worker pattern for RPC-based sub-agent execution, and NEAR AI multi-agent routing.
- **Detailed Guide & Onboarding**: [ironclaw-ctl.md](assistants/ironclaw-ctl.md)

### Hermes
- **Major Features**: Messaging Gateway designed for agent-to-agent and agent-to-human integration. Features an OpenAI-compatible API and a Dashboard Web UI. Supports graceful shutdowns and nested container execution.
- **Language/Runtime**: Python (Source) / private 3.11 Python Runtime /opt (Web-based Dashboard GUI).
- **Requirements**: `~/.local/sandbox/hermes` for persistent state, `~/agent-shared` for integration. Can integrate with podman/docker backend.
- **Sandboxing**: Utilizes the **Relaxed Namespaces Profile** to support nested `bwrap` orchestration. Isolated `HOME` directory redirection.
- **Memory**: Built-in SQLite-based SessionDB/State management. Keeps localized context via `MEMORY.md` and `USER.md` prompt injections. Context compaction (`ContextCompressor`) supports tool output pruning (removes screenshots, replaces outputs with 1-line summaries), token-budget tail protection, and iterative summary updates (LLM summarizes middle turns). Offline trajectory compressor (`trajectory_compressor.py`) compresses trajectories under a target budget (default 15,250 tokens) for model training.
- **Search & Retrieval**: SQLite FTS5 for keyword search, plus vector search using the `sqlite-vec` extension. Direct integrations with external vector databases (Qdrant, Chroma) and memory frameworks (Mem0, Honcho).
- **Autonomous 24/7 Support**: Yes — Built-in cron scheduler with platform delivery. Background batch and SWE runners (`batch_runner.py` / `mini_swe_runner.py`).
- **Signal Support**: Yes — Native integration connecting to a local `signal-cli` HTTP daemon (port 50888/50889).
- **Coding Agent Support**: Yes — Supports Claude Code, Codex, and **OpenCode** via bundled skills.
- **Local LLM & Inference**: Supports local GGUF models via `local-chat` (port 50080) or Ollama.
- **Embedding Options**: Local embeddings via `local-embedding` (port 50082) or Ollama, or remote embedding providers (OpenAI, Cohere, Jina, Voyage AI).
- **Reranking Support**: Native reranking via auxiliary model slots and QMD hybrid retrieval engine, or routes to external reranker (`http://localhost:50086/v1/rerank`).
- **STT/TTS Support**: Local STT via local Whisper server (`local-speech-to-text` on port 50090). No native TTS support.
- **Agent Client Protocol (ACP)**: Yes — Native stdio-based ACP server adapter (`acp_adapter/server.py`) for editor integrations (VS Code, Zed, JetBrains).
- **Agent to Agent Protocol**: Yes — Supports spawning isolated subagents for parallel workstreams and calling tools/subagents via RPC.
- **Detailed Guide & Onboarding**: [hermes-ctl.md](assistants/hermes-ctl.md)

### NanoBot
- **Major Features**: Lightweight python service built with `uv` featuring an onboarding setup wizard, a structured two-stage memory system ("Dream"), and Bubblewrap tool confinement.
- **Language/Runtime**: Python (Source) / Python runtime managed by `uv` (Python CLI + Setup Wizard, no Web GUI).
- **Requirements**: `uv` package manager installed.
- **Sandboxing**: Relies on the **Relaxed Namespaces Profile** because it natively spawns agent code wrapped in nested `bwrap` isolation. Isolated `HOME`.
- **Memory**: Two-stage memory system. Active conversation buffers in session jsonl files, and long-term memory in a file-based `MEMORY.md` (and persona/user preferences in `SOUL.md`/`USER.md`). Auto-versioned via GitStore. Auto-compaction of idle sessions via `AutoCompact` based on `session_ttl_minutes` limit (keeps last 8 messages, archives the rest into session metadata). Context-length/token-triggered memory consolidation (`maybe_consolidate_by_tokens`) during active turns loops to archive message chunks to `history.jsonl`. Ephemeral background "Dream" loop reads `history.jsonl` (tracked via `.dream_cursor`) and runs an ephemeral agent to synthesize and update `MEMORY.md`, `SOUL.md`, or `USER.md` with auto-commits via Git.
- **Search & Retrieval**: Vector similarity search (RAG) for long-term memory. Document Store for indexing and searching local files (PDFs, TXT, markdown). External search via MCP tools (Brave Search).
- **Autonomous 24/7 Support**: Yes — Periodic background "Dream" loop and cron tasks.
- **Signal Support**: Yes — Native integration via HTTP Server-Sent Events (SSE) (port 50888) with markdown-to-Signal formatting.
- **Coding Agent Support**: None (No OpenCode support).
- **Local LLM & Inference**: Routes to local GGUF models via `local-chat` (port 50080) or Ollama.
- **Embedding Options**: Local embeddings via `local-embedding` (port 50082) or Ollama, or remote embeddings.
- **Reranking Support**: No native reranking. Integrates with external reranker via custom MCP tools.
- **STT/TTS Support**: Local STT via local Whisper server (`local-speech-to-text` on port 50090). No native local TTS.
- **Agent Client Protocol (ACP)**: No ACP support.
- **Agent to Agent Protocol**: Yes — Background subagent spawning (`SubagentManager`) communicating asynchronously via the message bus (`MessageBus` / `InboundMessage` system injection).
- **Detailed Guide & Onboarding**: [nanobot-ctl.md](assistants/nanobot-ctl.md)

### LibreFang
- **Major Features**: Hardened Agent OS daemon providing isolated execution environments and coordinating complex multi-agent workflows. It is a community fork of the former OpenFang project.
- **Language/Runtime**: Rust (Source) / Compiled binary (Rust Backend + Web-based Dashboard GUI).
- **Requirements**: `~/.local/sandbox/librefang` and `~/agent-shared`.
- **Sandboxing**: **Relaxed Namespaces Profile** to support bubblewrap (`bwrap`) nested sandboxing for sub-agents. Read-only system paths and strict filesystem protection for the host.
- **Memory**: SQLite-based memory system and vector storage for persistent agent memories and knowledge. Custom configuration workspace.
- **Retention/Compression/Compaction**: Context limit handling: automatically extracts facts and summarizes history when approaching context limits.
- **Search & Retrieval**: Native SQLite and vector memory stores for persistent agent memory, task scheduling, and background search/research. Can connect to external databases via MCP.
- **Autonomous 24/7 Support**: Yes — Built-in scheduling and task memory for running 24/7 (run autonomous background execution via `hand activate researcher` or other hands).
- **Signal Support**: Yes — Native channel integration interfacing with the Go REST API wrapper (port 50889), using `[[sidecar_channels]]` adapter `librefang.sidecar.adapters.signal`.
- **Coding Agent Support**: Yes — Supports Claude Code, Aider, Qwen Code, Gemini CLI, and Codex CLI (spawned as subprocesses; No native OpenCode support).
- **Local LLM & Inference**: Supports local GGUF models via OpenAI-compatible endpoints served by `local-chat` (port 50080) or Ollama.
- **Embedding Options**: Local embeddings using the `local-embedding` server (port 50082) or Ollama, or remote/Ollama embeddings.
- **Reranking Support**: None. Reranking is not supported by the LibreFang daemon.
- **STT/TTS Support**: Local STT via local Whisper server (`local-speech-to-text` on port 50090) and local TTS via Qwen3-tts (`local-text-to-speech` on port 50095) supported via a patched package (`librefang-git` with `feature-local-stt-tts` patchset).
- **Agent Client Protocol**: Yes — Bridges the runtime to the Agent Client Protocol (ACP) for editor integrations (stdio or Unix socket).
- **Agent to Agent Protocol**: Yes — Spawns subagents isolated with bubblewrap (`bwrap`), passing context via `SubagentContext` for context inheritance.
- **Detailed Guide & Onboarding**: [librefang-ctl.md](assistants/librefang-ctl.md)


### PicoClaw
- **Major Features**: Ultra-lightweight gateway (<10MB memory) with built-in web console and CLI integration, leveraging Model Context Protocol (MCP) for tools/memory.
- **Language/Runtime**: Go (Source) / Compiled binary (Go Backend + Web-based Console GUI).
- **Requirements**: `~/.local/sandbox/picoclaw` for persistent configuration.
- **Sandboxing**: **Relaxed Namespaces Profile**. Uses standard agent isolation with redirected `HOME` and strict filesystem protection. Isolated `HOME`.
- **Memory**: RAW JSON files for session/history (history limit default 50). No native vector db.
- **Retention/Compression/Compaction**: Simple context limit: history limit (default 50). No native compression.
- **Search & Retrieval**: Uses Model Context Protocol (MCP) to delegate search/retrieval tasks to external databases (such as `sqlite-vec` MCP, Qdrant MCP, or Chroma MCP).
- **Autonomous 24/7 Support**: Yes — Messaging gateway daemon background service (`picoclaw-launcher -no-browser`).
- **Signal Support**: No — Not natively supported.
- **Coding Agent Support**: Yes — Supports Claude Code, Codex, and Copilot CLI via provider-wrapped CLI execution (No OpenCode support).
- **Local LLM & Inference**: Routes to local GGUF models via `local-chat` (port 50080) or Ollama.
- **Embedding Options**: Local embeddings via `local-embedding` (port 50082) or Ollama via API routing or MCP.
- **Reranking Support**: No native reranking. Reranking can be delegated via MCP to the local-inference reranker endpoint on port 50086.
- **STT/TTS Support**: Local STT by defining an ASR provider pointing to the local whisper-server on port 50090. No native TTS engine; requires an external MCP TTS tool.
- **Agent Client Protocol**: No native ACP support.
- **Agent to Agent Protocol**: Yes — Supports `spawn` (asynchronous background subagents via goroutines) and `delegate` (synchronous targeted subagents) tools, with target allowlist validation.
- **Detailed Guide & Onboarding**: [picoclaw-ctl.md](assistants/picoclaw-ctl.md)

### NanoClaw
- **Major Features**: Node.js webhook server designed for securely executing containerized runtime tools and managing agent workspaces.
- **Language/Runtime**: TypeScript/Node.js (Source) / Node.js containerized (Node.js Webhook Backend, no Web GUI).
- **Requirements**: Requires Docker/Podman running locally to spawn tool environments.
- **Sandboxing**: **Relaxed Namespaces Profile** with `PrivateDevices=no`. Strict profiles are dropped to allow the agent to launch local Docker/Podman containers successfully.
- **Memory**: Per-session SQLite database mounted inside the container at `/workspace/session.db` (containing `messages_in` and `messages_out` tables) and a central SQLite database. Maintains `CLAUDE.md` and related markdown files in isolated agent group directories under `/workspace/agent/`.
- **Retention/Compression/Compaction**: Context limit handling is handled by the agent (e.g. Claude SDK) discovering its own session data in `.claude/` inside `/workspace/.claude/`. No native compaction.
- **Search & Retrieval**: Uses SQLite databases within the Node.js process to maintain state. Maintains `CLAUDE.md` and related markdown files in isolated agent group directories. Heavy search, retrieval, and vector storage tasks are delegated to external MCP servers (like `sqlite-vec` MCP, Qdrant MCP, or Chroma MCP) or handled by the agent calling custom tools.
- **Autonomous 24/7 Support**: Yes — background host sweep (every ~60s) and active container poll (~1s) check for due `process_after` / `deliver_after` timestamps, reschedule recurring tasks using cron, and wake up agents.
- **Signal Support**: No — Not natively supported.
- **Coding Agent Support**: None (No native OpenCode support), but has an optional `add-opencode` skill for local inference.
- **Local LLM & Inference**: Routes to local GGUF models via OpenAI-compatible endpoints served by `local-chat` (port 50080) or Ollama.
- **Embedding Options**: Local embeddings via `local-embedding` (port 50082) or Ollama, or remote embeddings.
- **Reranking Support**: No native reranking. Reranking can be added via a custom skill or by configuring an MCP tool that calls the local-inference reranker endpoint on port 50086.
- **STT/TTS Support**: No native STT/TTS in the core daemon, but easily integrated via custom tools/skills calling `local-speech-to-text` (port 50090) and `local-text-to-speech` (port 50095).
- **Agent Client Protocol**: No native ACP support.
- **Agent to Agent Protocol**: Yes — supported via target-agent routing on `messages_out`. An agent-runner can set `channel_type: 'agent'`, `platform_id` to the target agent group ID, and `thread_id` to a target session ID. The host reads this, validates permissions, and writes a `messages_in` row to the target session's DB.
- **Detailed Guide & Onboarding**: [nanoclaw-ctl.md](assistants/nanoclaw-ctl.md)

---

## Standard Control Wrappers (assistant-ctl)

Each assistant in this repository is managed by a dedicated shell wrapper script (`assistants/<assistant>-ctl`) adhering to standard design and lifecycle management guidelines.

### Common Commands

| Command | Action | Description |
|---|---|---|
| `install` | Install | Set up local directory structures under `~/.local/sandbox/<assistant>`, generate environment file `.env` if missing, and create/register the systemd user unit. |
| `install --no-start` | Install | Same as install, but do not start (or stop it if already running) the service after installation for further configuration (e.g. editing `.env`). |
| `install --new-config` | Install | Same as install, but force overwrite any existing environment and configuration files with their default templates (useful for resetting to defaults). |
| `uninstall` | Uninstall | Stop and disable the systemd service, and clean up the systemd service files. (Data is preserved). |
| `start` / `stop` / `restart` | Lifecycle | Standard controls to start, stop, or restart the systemd user service. |
| `status` | Status | Show the current runtime status of the systemd service. |
| `logs [args...]` | Logs | View the daemon stdout/stderr output. Pass `-f` to tail/follow (e.g. `<assistant>-ctl logs -f`). Supports passing any additional `journalctl` options. |
| `edit` | Edit Config | Open the assistant's `.env` environment file (and `config.toml` configuration files for supported assistants) in your `$EDITOR` and automatically restart the service upon exit to apply changes. |
| `exec <args...>` | Sandbox Execute | Run the assistant's CLI binary or command line inside a transient systemd user service inheriting the same sandboxing and environment. |
| `shell` | Sandbox Shell | Spawn an interactive shell inside the assistant's systemd user sandbox for debugging. |

### Common Paths & Redirections

- **Service File**: `~/.config/systemd/user/<assistant>.service` (or `hermes-gateway.service`)
- **Environment File**: `~/.config/systemd/user/<assistant>.env` (or `hermes-gateway.env`)
- **Data Home**: `~/.local/sandbox/<assistant>` (the service forces an isolated `HOME` environment variable to this location to keep configurations and cached libraries contained).
- **Shared Space (`agent-shared`)**: `~/agent-shared` is bind-mounted in read-write mode to the sandbox of all assistants by default. This enables cross-assistant sharing of outputs, databases, and logs.
- **Private Submounts (`agent-private`)**: To easily share specific directories from your host's private workspace (`~/agent-private/*`) to an assistant's sandbox without exposing the entire home directory, configure the `AGENT_PRIVATE_MOUNTS` environment variable inside the assistant's `.env` environment file.
  - **Syntax**: `AGENT_PRIVATE_MOUNTS="health diary"`
  - **Behavior**: The control wrapper will dynamically parse this list, ensure that the target directories (e.g. `~/agent-private/health` and `~/agent-private/diary`) exist on the host, inject the corresponding `BindPaths=` rules into the systemd service file, reload the user daemon, and dynamically mount them in all `start`, `restart`, `exec`, and `shell` wrapper commands.

---

## How to Recreate/Update This Document

This `README.md` serves as the primary system registry and architectural entry point. Follow this process to update or recreate the information documented here:

1. **Update Remote Sources**: Fetch the latest commits for all sandboxed assistants under `scratch/` by running:
   ```bash
   for d in librefang zeroclaw ironclaw hermes-agent nanobot nanoclaw picoclaw; do
     cd "scratch/$d" 2>/dev/null && git fetch origin && git pull || true
   done
   ```
2. **Review Control Configurations**: Check the respective control wrappers (`assistants/*-ctl.md`) to verify default port allocations, sandbox profiles, and setup procedures.
3. **Verify Feature Implementations**: Inspect configuration schemas and source code directories:
   - For ZeroClaw: check `crates/zeroclaw-config/src/schema.rs` and `crates/zeroclaw-memory/`.
   - For IronClaw: check `.env.example` and `FEATURE_PARITY.md`.
   - For Hermes: check `hermes_constants.py`, `agent/context_compressor.py`, and `acp_adapter/`.
   - For NanoBot: check `nanobot/config/schema.py` and `nanobot/agent/memory.py`.
4. **Audit Default Ports**: Keep the `## Default Ports` registry table synchronized with any new or modified port bindings found in the assistants' configs.
5. **Enforce Sandboxing Alignment**: If any assistant introduces new hardware or namespace isolation requirements, update the `## Sandboxing Architecture` profiles accordingly.

