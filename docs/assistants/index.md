# Assistant Runtime & Service Management Guide

This document describes the unified runtime, service configuration, and sandboxing architecture shared by all assistant control scripts (`*-ctl`) in this repository.

---

## Assistants

| Agent | Language | Default Port(s) | Description |
| :--- | :---: | :---: | :--- |
| **[ZeroClaw](#zeroclaw)** | Rust | [42617](http://localhost:42617) | ZeroClaw Gateway |
| **[IronClaw](#ironclaw)** | Rust | [28080](http://localhost:28080) | IronClaw Web Gateway & HTTP Webhooks |
| **[LibreFang](#librefang)** | Rust | [4545](http://localhost:4545) | LibreFang daemon API (HTTP) |
| **[Hermes](#hermes)** | Python | [8642](http://localhost:8642), [9119](http://localhost:9119) | Hermes Gateway (API: 8642, UI: 9119) |
| **[NanoBot](#nanobot)** | Python | [8790](http://localhost:8790) | NanoBot Gateway API |
| **[PicoClaw](#picoclaw)** | Go | [18790](http://localhost:18790), [18800](http://localhost:18800) | Gateway (HTTP/Webhook) & Launcher Web UI |
| **[NanoClaw](#nanoclaw)** | TypeScript | [3000](http://localhost:3000) | Webhook Server |

Each assistant in this repository is managed by a dedicated shell wrapper script (`assistants/<assistant>-ctl`) adhering to standard design and lifecycle management guidelines.

### ZeroClaw
- **Major Features**: Rust-based security-focused agent gateway and runtime featuring built-in SQLite hybrid memory (vector + keyword FTS5) and native Landlock/Bubblewrap sandbox backends.
- **Language/Runtime**: Rust (Source) / Compiled binary (Rust Backend, no Web GUI).
- **Requirements**: Support for Linux namespace isolation or Landlock.
- **Sandboxing**: **Relaxed Namespaces Profile** is enforced via the systemd unit so that ZeroClaw can spawn secure nested sub-sandboxes via `bwrap` internally.
- **Memory**: Native SQLite-based memory system. Supports `sqlite` and `sqlite-hybrid` (vector + keyword FTS5) natively; can also use PostgreSQL or Qdrant.
- **Retention/Compression/Compaction**: Features time-decay scoring (evergreen Core category, time-decayed Conversation/others with a 7-day half-life), two-phase LLM-driven memory consolidation (Daily history + Core fact extraction) at the end of each turn, and periodic memory hygiene (every 12 hours) to archive, purge, and prune database rows.
- **Search & Retrieval**: Native hybrid search (0.7 vector similarity / 0.3 keyword FTS5) directly inside SQLite.
- **Autonomous 24/7 Support**: Yes — Built-in scheduling and task memory for unattended 24/7 operations.
- **Signal Support**: Yes — Native channel integration communicating via the Go REST API wrapper (port 20889).
- **Coding Agent Support**: Yes — Natively supports **OpenCode** as a coding worker tool (`opencode_cli`).
- **Local LLM & Inference**: Supports local GGUF models via OpenAI-compatible endpoints served by `local-chat` (port 20080) or Ollama.
- **Embedding Options**: Local embeddings using the `local-embedding` server (port 20082) or Ollama, or OpenAI-compatible embedding APIs.
- **Reranking Support**: Native weighted hybrid search, or routes to external local-rerank service (`http://localhost:20086/v1/rerank`).
- **STT/TTS Support**: Natively routes voice uploads to local Whisper server (`local-speech-to-text` on port 20090) and local TTS via Kokoro-82M ONNX / Qwen3-tts (`local-text-to-speech` on port 20095).
- **Agent Client Protocol**: Yes — Native stdio-based ACP server via `zeroclaw-acp-bridge` and a dedicated `Acp` (Code) pane in the `zerocode` TUI.
- **Agent to Agent Protocol**: Yes — Built-in peer-to-peer delegation via the `delegate` tool, restricted by shared risk profiles and `delegation_policy` configurations.
- **Detailed Guide & Onboarding**: [zeroclaw.md](zeroclaw.md)


### IronClaw
- **Major Features**: Security-focused Agent OS providing WASM-sandboxed tool execution, credential protection with leak detection, prompt injection defense, and endpoint allowlisting. Built as a Rust reimplementation of OpenClaw with a focus on privacy, zero-trust architecture, and self-expanding capabilities via dynamic WASM tool building.
- **Language/Runtime**: Rust (Source) / Compiled binary (Rust Backend + Web Gateway GUI).
- **Requirements**: PostgreSQL 15+ with [pgvector](https://github.com/pgvector/pgvector) extension. Rust 1.92+ for source builds. NEAR AI account for default authentication.
- **Sandboxing**: **Relaxed Namespaces Profile** to support WASM sandbox execution (wasmtime) and optional Docker sandbox orchestrator/worker pattern. `MemoryDenyWriteExecute=no` required for WASM JIT compilation.
- **Memory**: PostgreSQL 15+ database with the `pgvector` extension. Workspace filesystem provides flexible path-based storage for notes, logs, and context. Identity files maintain settings and contexts.
- **Retention/Compression/Compaction**: Context compaction supports auto-summarization of history. Settings and metadata are persisted in PostgreSQL.
- **Search & Retrieval**: Hybrid search combining full-text search and vector similarity via Reciprocal Rank Fusion (RRF) backed by PostgreSQL.
- **Autonomous 24/7 Support**: Yes — Heartbeat support (`HEARTBEAT_ENABLED`) for background tasks and cron jobs.
- **Signal Support**: Yes — Native integration communicating via the `signal-cli` HTTP daemon (port 20889).
- **Coding Agent Support**: Yes — Supports external coding agents via Agent Client Protocol (e.g. `ironclaw acp add goose`). No native OpenCode support.
- **Local LLM & Inference**: Supports local GGUF models via OpenAI-compatible endpoints served by `local-chat` (port 20080) or Ollama.
- **Embedding Options**: Local embeddings using the `local-embedding` server (port 20082) or Ollama, or remote/Ollama embeddings.
- **Reranking Support**: Native Reciprocal Rank Fusion (RRF) algorithm. No external reranker required.
- **STT/TTS Support**: Local STT via OpenAI-compatible transcription endpoint (`local-speech-to-text` on port 20090). No native TTS support.
- **Agent Client Protocol**: Yes — Configurable external coding agents using ACP commands (e.g. `ironclaw acp add goose`).
- **Agent to Agent Protocol**: Yes — Orchestrator/worker pattern for RPC-based sub-agent execution, and NEAR AI multi-agent routing.
- **Detailed Guide & Onboarding**: [ironclaw.md](ironclaw.md)

### Hermes
- **Major Features**: Messaging Gateway designed for agent-to-agent and agent-to-human integration. Features an OpenAI-compatible API and a Dashboard Web UI. Supports graceful shutdowns and nested container execution.
- **Language/Runtime**: Python (Source) / private 3.11 Python Runtime /opt (Web-based Dashboard GUI).
- **Requirements**: `~/.local/sandbox/hermes` for persistent state, `~/agent-shared` for integration. Can integrate with podman/docker backend.
- **Sandboxing**: Utilizes the **Relaxed Namespaces Profile** to support nested `bwrap` orchestration. Isolated `HOME` directory redirection.
- **Memory**: Built-in SQLite-based SessionDB/State management. Keeps localized context via `MEMORY.md` and `USER.md` prompt injections. Context compaction (`ContextCompressor`) supports tool output pruning (removes screenshots, replaces outputs with 1-line summaries), token-budget tail protection, and iterative summary updates (LLM summarizes middle turns). Offline trajectory compressor (`trajectory_compressor.py`) compresses trajectories under a target budget (default 15,250 tokens) for model training.
- **Search & Retrieval**: SQLite FTS5 for keyword search, plus vector search using the `sqlite-vec` extension. Direct integrations with external vector databases (Qdrant, Chroma) and memory frameworks (Mem0, Honcho).
- **Autonomous 24/7 Support**: Yes — Built-in cron scheduler with platform delivery. Background batch and SWE runners (`batch_runner.py` / `mini_swe_runner.py`).
- **Signal Support**: Yes — Native integration connecting to a local `signal-cli` HTTP daemon (port 20888/20889).
- **Coding Agent Support**: Yes — Supports Claude Code, Codex, and **OpenCode** via bundled skills.
- **Local LLM & Inference**: Supports local GGUF models via `local-chat` (port 20080) or Ollama.
- **Embedding Options**: Local embeddings via `local-embedding` (port 20082) or Ollama, or remote embedding providers (OpenAI, Cohere, Jina, Voyage AI).
- **Reranking Support**: Native reranking via auxiliary model slots and QMD hybrid retrieval engine, or routes to external reranker (`http://localhost:20086/v1/rerank`).
- **STT/TTS Support**: Local STT via local Whisper server (`local-speech-to-text` on port 20090). No native TTS support.
- **Agent Client Protocol (ACP)**: Yes — Native stdio-based ACP server adapter (`acp_adapter/server.py`) for editor integrations (VS Code, Zed, JetBrains).
- **Agent to Agent Protocol**: Yes — Supports spawning isolated subagents for parallel workstreams and calling tools/subagents via RPC.
- **Detailed Guide & Onboarding**: [hermes.md](hermes.md)

### NanoBot
- **Major Features**: Lightweight python service built with `uv` featuring an onboarding setup wizard, a structured two-stage memory system ("Dream"), and Bubblewrap tool confinement.
- **Language/Runtime**: Python (Source) / Python runtime managed by `uv` (Python CLI + Setup Wizard, no Web GUI).
- **Requirements**: `uv` package manager installed.
- **Sandboxing**: Relies on the **Relaxed Namespaces Profile** because it natively spawns agent code wrapped in nested `bwrap` isolation. Isolated `HOME`.
- **Memory**: Two-stage memory system. Active conversation buffers in session jsonl files, and long-term memory in a file-based `MEMORY.md` (and persona/user preferences in `SOUL.md`/`USER.md`). Auto-versioned via GitStore. Auto-compaction of idle sessions via `AutoCompact` based on `session_ttl_minutes` limit (keeps last 8 messages, archives the rest into session metadata). Context-length/token-triggered memory consolidation (`maybe_consolidate_by_tokens`) during active turns loops to archive message chunks to `history.jsonl`. Ephemeral background "Dream" loop reads `history.jsonl` (tracked via `.dream_cursor`) and runs an ephemeral agent to synthesize and update `MEMORY.md`, `SOUL.md`, or `USER.md` with auto-commits via Git.
- **Search & Retrieval**: Vector similarity search (RAG) for long-term memory. Document Store for indexing and searching local files (PDFs, TXT, markdown). External search via MCP tools (Brave Search).
- **Autonomous 24/7 Support**: Yes — Periodic background "Dream" loop and cron tasks.
- **Signal Support**: Yes — Native integration via HTTP Server-Sent Events (SSE) (port 20888) with markdown-to-Signal formatting.
- **Coding Agent Support**: None (No OpenCode support).
- **Local LLM & Inference**: Routes to local GGUF models via `local-chat` (port 20080) or Ollama.
- **Embedding Options**: Local embeddings via `local-embedding` (port 20082) or Ollama, or remote embeddings.
- **Reranking Support**: No native reranking. Integrates with external reranker via custom MCP tools.
- **STT/TTS Support**: Local STT via local Whisper server (`local-speech-to-text` on port 20090). No native local TTS.
- **Agent Client Protocol (ACP)**: No ACP support.
- **Agent to Agent Protocol**: Yes — Background subagent spawning (`SubagentManager`) communicating asynchronously via the message bus (`MessageBus` / `InboundMessage` system injection).
- **Detailed Guide & Onboarding**: [nanobot.md](nanobot.md)

### LibreFang
- **Major Features**: Hardened Agent OS daemon providing isolated execution environments and coordinating complex multi-agent workflows. It is a community fork of the former OpenFang project.
- **Language/Runtime**: Rust (Source) / Compiled binary (Rust Backend + Web-based Dashboard GUI).
- **Requirements**: `~/.local/sandbox/librefang` and `~/agent-shared`.
- **Sandboxing**: **Relaxed Namespaces Profile** to support bubblewrap (`bwrap`) nested sandboxing for sub-agents. Read-only system paths and strict filesystem protection for the host.
- **Memory**: SQLite-based memory system and vector storage for persistent agent memories and knowledge. Custom configuration workspace.
- **Retention/Compression/Compaction**: Context limit handling: automatically extracts facts and summarizes history when approaching context limits.
- **Search & Retrieval**: Native SQLite and vector memory stores for persistent agent memory, task scheduling, and background search/research. Can connect to external databases via MCP.
- **Autonomous 24/7 Support**: Yes — Built-in scheduling and task memory for running 24/7 (run autonomous background execution via `hand activate researcher` or other hands).
- **Signal Support**: Yes — Native channel integration interfacing with the Go REST API wrapper (port 20889), using `[[sidecar_channels]]` adapter `librefang.sidecar.adapters.signal`.
- **Coding Agent Support**: Yes — Supports Claude Code, Aider, Qwen Code, Gemini CLI, and Codex CLI (spawned as subprocesses; No native OpenCode support).
- **Local LLM & Inference**: Supports local GGUF models via OpenAI-compatible endpoints served by `local-chat` (port 20080) or Ollama.
- **Embedding Options**: Local embeddings using the `local-embedding` server (port 20082) or Ollama, or remote/Ollama embeddings.
- **Reranking Support**: None. Reranking is not supported by the LibreFang daemon.
- **STT/TTS Support**: Local STT via local Whisper server (`local-speech-to-text` on port 20090) and local TTS via Kokoro-82M ONNX / Qwen3-tts (`local-text-to-speech` on port 20095).
- **Agent Client Protocol**: Yes — Bridges the runtime to the Agent Client Protocol (ACP) for editor integrations (stdio or Unix socket).
- **Agent to Agent Protocol**: Yes — Spawns subagents isolated with bubblewrap (`bwrap`), passing context via `SubagentContext` for context inheritance.
- **Detailed Guide & Onboarding**: [librefang.md](librefang.md)


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
- **Local LLM & Inference**: Routes to local GGUF models via `local-chat` (port 20080) or Ollama.
- **Embedding Options**: Local embeddings via `local-embedding` (port 20082) or Ollama via API routing or MCP.
- **Reranking Support**: No native reranking. Reranking can be delegated via MCP to the local-inference reranker endpoint on port 20086.
- **STT/TTS Support**: Local STT by defining an ASR provider pointing to the local whisper-server on port 20090. No native TTS engine; requires an external MCP TTS tool.
- **Agent Client Protocol**: No native ACP support.
- **Agent to Agent Protocol**: Yes — Supports `spawn` (asynchronous background subagents via goroutines) and `delegate` (synchronous targeted subagents) tools, with target allowlist validation.
- **Detailed Guide & Onboarding**: [picoclaw.md](picoclaw.md)

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
- **Local LLM & Inference**: Routes to local GGUF models via OpenAI-compatible endpoints served by `local-chat` (port 20080) or Ollama.
- **Embedding Options**: Local embeddings via `local-embedding` (port 20082) or Ollama, or remote embeddings.
- **Reranking Support**: No native reranking. Reranking can be added via a custom skill or by configuring an MCP tool that calls the local-inference reranker endpoint on port 20086.
- **STT/TTS Support**: No native STT/TTS in the core daemon, but easily integrated via custom tools/skills calling `local-speech-to-text` (port 20090) and `local-text-to-speech` (port 20095).
- **Agent Client Protocol**: No native ACP support.
- **Agent to Agent Protocol**: Yes — supported via target-agent routing on `messages_out`. An agent-runner can set `channel_type: 'agent'`, `platform_id` to the target agent group ID, and `thread_id` to a target session ID. The host reads this, validates permissions, and writes a `messages_in` row to the target session's DB.
- **Detailed Guide & Onboarding**: [nanoclaw.md](nanoclaw.md)


## Shared Control Commands

All `*-ctl` scripts support a standard set of lifecycle, configuration, and execution commands. Each assistant runs within its own systemd user namespace or fallback direct-execution sandbox:

*   **`install [--no-start] [--new-config]`**
    Initializes the assistant's dedicated home directory under `~/.local/sandbox/<agent>`, writes systemd unit files, generates environment templates, and starts the service.
    - `--no-start`: Setup files and register systemd unit without starting the service.
    - `--new-config`: Force-overwrite existing configuration and environment files with repository defaults.
*   **`uninstall`**
    Stops, disables, and removes the systemd user service. Configuration and database stores are preserved.
*   **`start` / `stop` / `restart` / `status`**
    Standard service controls mapped to `systemctl --user`.
*   **`enable` / `disable`**
    Toggles automatic starting of the user service on system boot.
*   **`logs [-f] [args...]`**
    Tails service output using `journalctl --user`.
*   **`edit`**
    Opens the assistant's environment configuration (`~/.config/systemd/user/<agent>.env`) and/or application config files in the system `$EDITOR` (falling back to `nano`). If systemd is running, restarts the service upon editor exit.
*   **`exec <subcommand> [args...]`**
    Executes assistant commands inside the systemd runtime or direct sandbox.
*   **`run <command> [args...]`**
    Executes arbitrary host commands inside the assistant's container/sandbox environment.
*   **`shell`**
    Spawns an interactive bash shell in the assistant's sandboxed environment.

---

## Common Configuration Variables

Configurations are primarily defined in `~/.config/systemd/user/<agent>.env`.

### Environment File Overlays (Hermes, IronClaw & LibreFang)

For assistants that support application-level configurations (specifically Hermes, IronClaw, and LibreFang), configuration environment variables are loaded in a two-stage resolution order:
1. **Systemd Service Environment File:** `~/.config/systemd/user/<agent>.env`
2. **Application Environment Override File:** `~/.local/sandbox/<agent>/.<agent>/.env` (e.g. `.hermes/.env`, `.ironclaw/.env` or `.librefang/.env`)

The application environment override file is loaded **after** the systemd service environment file. Therefore, any conflicting keys declared in both files will prioritize the values set in the application environment override file.

The following parameters are unified across all control wrappers:

*   **`AGENT_WORKSPACE`**
    Configures the default folder where the agent reads and writes active workspace data (contexts, notes, files). The default path is agent-specific (e.g., `%h/.local/sandbox/<agent>/.../workspace`).
*   **`AGENT_EXTRA_MOUNTS`**
    A space-separated list of host-to-sandbox bind mounts (syntax: `host-path:sandbox-path`). Host paths can use `$HOME`, `%h`, or `~` prefixes.
    - *Default:* Binds the repository's shared folder: `AGENT_EXTRA_MOUNTS="%h/agent-shared:agent-shared"`.
*   **`AGENT_PRIVATE_MOUNTS`**
    A space-separated list of directories inside `~/agent-private/` to bind-mount into the sandbox (e.g., `AGENT_PRIVATE_MOUNTS="health diary"`).
*   **`AGENT_SANDBOX_MOUNTS`**
    A space-separated list of directories from other assistants' sandboxes to expose (e.g., `AGENT_SANDBOX_MOUNTS="opencode/.cache/opencode"`).
*   **`AGENT_SIDECARS`**
    A space- or semicolon-separated list of background sidecar scripts or daemons to start/stop with the main daemon (e.g., `AGENT_SIDECARS="audionotes"`).
*   **`AGENT_SIDECAR_<NAME>_CMD`**
    The command or path to the sidecar executable (e.g., `AGENT_SIDECAR_AUDIONOTES_CMD="$AGENT_WORKSPACE/scripts/audionotes.sh"`).
*   **`AGENT_SIDECAR_<NAME>_ARGS`**
    Arguments to pass to the sidecar command.
*   **`AGENT_SIDECAR_<NAME>_ENV_REMOVE`**
    Space-separated list of environment variables to filter out from the sidecar.
*   **`AGENT_SIDECAR_<NAME>_ENV_OVERRIDE`**
    Space-separated list of environment overrides specifically for the sidecar process.
*   **`AGENT_TMPFILES_CLEANUP`** (Default: `false`)
    Toggles systemd-tmpfiles directory cleanup rules.

### Generating a Secure Token

To generate a secure, random 32-character alphanumeric token (`0-9A-Za-z`):

*   **Using `/dev/urandom` and `tr` (Standard, no dependencies):**
    ```bash
    tr -dc 'A-Za-z0-9' < /dev/urandom | head -c 32; echo
    ```
*   **Using `openssl` (Base64 filtering):**
    ```bash
    openssl rand -base64 48 | tr -dc 'A-Za-z0-9' | head -c 32; echo
    ```
*   **Using `python3` (Cryptographically secure secrets module):**
    ```bash
    python3 -c "import secrets, string; print(''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32)))"
    ```
*   **Using `pwgen` (If installed on the host):**
    ```bash
    pwgen -s 32 1
    ```

---

## Variable Path Expansion Rules

To make configurations flexible and compatible with both systemd and direct execution fallback environments, path variables inside environment configs are resolved as follows:

1.  **`AGENT_WORKSPACE`**:
    - **Usage**: You can use `$HOME`, `%h`, or `~` to specify the workspace path (e.g., `AGENT_WORKSPACE="$HOME/.local/workspace"`).
    - **Resolution**: Since systemd's `EnvironmentFile` loader does not perform specifier expansion, the control wrapper automatically expands `%h` to the actual home directory path on the host at service installation/update time. For any fallback environment configurations, the wrapper also resolves `$HOME` and `~` to guarantee absolute paths are present at runtime.
2.  **`AGENT_EXTRA_MOUNTS`**:
    - **Usage**: Syntax is `host-path:sandbox-path`. You can use `$HOME`, `%h`, or `~` for the host path (e.g., `AGENT_EXTRA_MOUNTS="$HOME/shared:shared"`).
    - **Resolution**: `$HOME` is expanded when bash sources the environment file. `%h` and `~` are resolved by the wrapper during service file generation and fallback directory checking.
3.  **`AGENT_SIDECAR_<NAME>_CMD` and `AGENT_SIDECAR_<NAME>_ARGS`**:
    - **Usage**: You can use `$AGENT_WORKSPACE`, `$HOME`, `%h`, or `~` (e.g., `AGENT_SIDECAR_AUDIONOTES_CMD="$AGENT_WORKSPACE/scripts/audionotes.sh"`).
    - **Resolution**:
      - Inside systemd, these sidecars run under a bash execution wrapper, so bash resolves `$AGENT_WORKSPACE` and `$HOME` at runtime.
      - During direct execution fallback mode, the wrapper expands `$AGENT_WORKSPACE`, `$HOME`, `%h`, and `~` on the host to run existence validation checks, and passes them to bash's `eval` for runtime evaluation.

---

## Agent Sidecars & Supervisor

Sidecar processes run within the **exact same systemd-confinement/namespaces** (or direct sandbox) as the main gateway daemon. They share the same isolated home directory, bind mounts, network/IPC namespace, and systemd cgroup limits.

#### Supervision & Exit Behavior
Sidecar processes are managed via the main service wrapper using an event-driven `wait -n` supervisor.
- If any sidecar process or the main daemon exits or crashes, the parent shell exits immediately (via an `EXIT` trap that terminates all remaining sibling processes in `hermes-ctl`, or via sequential `kill` blocks in other scripts), signaling systemd to tear down the entire control group (cgroup) and automatically restart the service.
- To prevent run-away crash loops, the systemd unit enforces a restart rate limit: if the service undergoes more than **4 continuous restarts within a 40-second interval**, systemd will mark the service as permanently failed and stop attempting to restart it (`StartLimitIntervalSec=40` and `StartLimitBurst=4`).

---

## systemd-tmpfiles Confinement Cleanup

Each assistant supports user-level `systemd-tmpfiles` configurations to clean up temporary, workspace, or staging directories automatically.

### Configuration
1.  Enable cleanup in the environment file:
    ```env
    AGENT_TMPFILES_CLEANUP=true
    ```
2.  Edit cleanup rules using:
    ```bash
    ./assistants/<agent>-ctl edit
    ```
    This command automatically opens the configuration file at `~/.config/user-tmpfiles.d/<service-name>.conf` alongside your environment and config files.

### Workspace Cleanup Example
You can configure cleanup policies (e.g., deleting files older than 24 hours in the monitored voice notes folder) in `~/.config/user-tmpfiles.d/<service-name>.conf`:

```ini
# ~/.config/user-tmpfiles.d/<service-name>.conf
# systemd-tmpfiles configuration for assistant

# Example: Delete all files in workspace/voice-notes/read/ if older than 24 hours
# Type  Path                                                                                    Mode UID  GID  Age  Argument
e       %h/.local/sandbox/<agent>/.../workspace/voice-notes/read                                 -    -    -    24h  -
```

When enabled, the cleanup policy runs immediately on service startup/restart, and integrates with the host user's periodic `systemd-tmpfiles-clean.timer`. When disabled, the configuration file is renamed to `<service-name>.conf.disabled` to prevent systemd's clean timer from running it, while preserving your configuration edits.

---

## Unified Security Sandboxing Profile

To guarantee parity across all execution modes, the wrapper centralizes its systemd sandboxing properties in a single helper function (`get_shared_options`). The background service (installed via `install`), the transient command runner (`exec`), and the interactive shell (`shell`) all inherit the exact same security profile:

1.  **Physical Devices**: `PrivateDevices=yes` is active by default to hide physical hardware devices (relaxed to `no` for agents like Hermes that require POSIX pseudo-terminal / PTY allocation for embedded WebUI chats).
2.  **Strict Filesystem Isolation**: Enforces `ProtectSystem=strict` and a tmpfs-mounted `$HOME` directory (`TemporaryFileSystem=%h`). The persistent directories (`~/.local/sandbox/<agent>`, `~/agent-shared`) are bind-mounted read-write, while the rest of the host filesystem is mounted read-only or hidden and `PrivateTmp=yes` is set to have a unique private temp for the process.
3.  **Kernel and IPC constraints**: Enforces kernel module, clock, and tunable protections, lock personality restrictions, and IPC namespaces.
4.  **NoNewPrivileges**: Enforces `NoNewPrivileges=yes` to prevent escalations.
5.  **Systemctl Masking**: Enforces `InaccessiblePaths=/usr/bin/systemctl /bin/systemctl` (currently implemented in `hermes-ctl` to prevent the sandboxed processes from trying to execute blocking daemon-reloads or systemd queries inside the isolated service cgroup, ensuring instant startup).
6.  **Direct Execution Fallback**: If systemd is not running in the current environment (e.g., inside a Bubblewrap container or systemd-free shell), the wrapper automatically falls back to direct execution of the binary under host environment variable overrides, setting `$HOME` to the sandboxed path.

### Strict Confinement Profile
- `ProtectProc=invisible` and `ProcSubset=pid`: Hides other system processes.
- `RestrictNamespaces=yes`: Prevents the creation of new namespaces.
- `MemoryDenyWriteExecute=yes`: Prevents W^X memory mappings (unless specifically required by an interpreter).

### Relaxed Namespaces Profile
Used by agents that orchestrate sub-agents or use tools like Bubblewrap (`bwrap`), Rootless Podman, or Docker for internal sandboxing.
- `RestrictNamespaces=yes` is **omitted** to allow `bwrap` or Podman to create `CLONE_NEWUSER` and `CLONE_NEWNS` unprivileged namespaces.
- `ProtectProc=invisible` and `ProcSubset=pid` are **omitted** so `bwrap` can securely bind its own `/proc` filesystem.
- `NoNewPrivileges=yes` is maintained for modern `bwrap` compatibility.

