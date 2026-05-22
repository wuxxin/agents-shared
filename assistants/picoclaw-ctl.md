# PicoClaw Agent Management Guide

`picoclaw-ctl` is a control script for the PicoClaw agent and its launcher, designed similarly to the `openfang-ctl` and `moltis-ctl` architecture.

- **Source Code**: [GitHub - sipeed/picoclaw](https://github.com/sipeed/picoclaw)
- **Arch/AUR Packages**: `picoclaw` (AUR, source-based Go compilation). Alternatives: `picoclaw-bin` (AUR, pre-built binary), `picoclaw-git` (AUR, git-based).

## Installation

```bash
./assistants/picoclaw-ctl install
```

## Commands

`picoclaw-ctl` supports all standard management operations. For detailed command reference and sandboxing path defaults, see [Standard Control Wrappers](file:///home/wuxxin/agent-shared/code/aur-packages/assistants/assistants.md#standard-control-wrappers-assistant-ctl).

## Onboarding

### Using the WebUI Launcher (Recommended)
1. **Install Service**: Run `./assistants/picoclaw-ctl install` to create the home directory (`~/.local/share/picoclaw`) and start `picoclaw-launcher -no-browser`.
2. **Web Onboarding**: Open `http://localhost:18800` in your browser. Configure your LLM API Key under **Settings -> Providers** (credentials are saved securely in `.security.yml`) and set up a platform channel under **Settings -> Channels**.
3. **Launch Gateway**: Click "Start Gateway" in the launcher web interface (runs on port `18790` by default) and begin chatting.

### Headless CLI Alternative
1. **Onboard Configuration**: Run `./assistants/picoclaw-ctl exec onboard` to generate `config.json` and initialize the workspace directory.
2. **Define Config**: Configure model providers and channel rules in `~/.local/share/picoclaw/config.json`.
3. **Test & Run**: Run `./assistants/picoclaw-ctl exec agent -m "Hello"` to test connection. Launch background messaging gateway with `./assistants/picoclaw-ctl exec gateway`.

### Switch to Local Inference & Qwen3
In the WebUI, add a Custom OpenAI provider with endpoint `http://localhost:50080/v1`, model `qwen3`, and key `unused`. Alternatively, configure `~/.local/share/picoclaw/config.json` manually:
```json
{
  "providers": {
    "openai": {
      "local": {
        "api_key": "unused",
        "base_url": "http://localhost:50080/v1"
      }
    }
  },
  "agents": {
    "default": {
      "model_provider": "openai.local",
      "model": "qwen3"
    }
  }
}
```

### OpenClaw Migration

PicoClaw supports migrating configuration and secure details from an existing OpenClaw setup. To trigger the migration utility, run:
```bash
./assistants/picoclaw-ctl exec migrate
```
This maps your legacy files and `.security.yml` details directly into the PicoClaw configurations under `~/.local/share/picoclaw/`.

## Search, Retrieval & Embedding Configuration

PicoClaw is an ultra-lightweight agent gateway and does not include a native built-in vector database or memory compression engine. Conversational history is stored in raw JSON files. To perform complex search and retrieval tasks, PicoClaw uses the Model Context Protocol (MCP) to delegate operations to external databases, search APIs, or RAG servers (such as Qdrant or `sqlite-vec`).

### Configuration

Add the following to `~/.local/share/picoclaw/config.json`:

```json
{
  "memory": {
    "type": "json_file",
    "history_limit": 50
  },
  "embeddings": {
    "provider": "openai",
    "model": "text-embedding-3-small",
    "base_url": "http://localhost:50080/v1",
    "api_key": "unused"
  },
  "mcp": {
    "servers": {
      "sqlite-vec": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-sqlite-vec"],
        "env": {
          "DB_PATH": "/home/wuxxin/.local/share/picoclaw/mcp-vectors.db"
        }
      }
    }
  }
}
```

### Reranking Configuration

PicoClaw does not include native reranking due to its ultra-lightweight design. Reranking can be delegated via MCP to the local-inference reranker endpoint. Add a reranker MCP server to `~/.local/share/picoclaw/config.json`:

```json
{
  "mcp": {
    "servers": {
      "local-reranker": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-fetch"],
        "env": {
          "RERANK_URL": "http://localhost:50080/v1/rerank",
          "RERANK_MODEL": "qwen3-reranker"
        }
      }
    }
  }
}
```

The reranker endpoint accepts `POST /v1/rerank` with `{"model": "qwen3-reranker", "query": "...", "documents": ["..."]}`.

## Speech-to-Text Integration

PicoClaw supports speech-to-text (ASR) transcription by configuring a model provider pointing to the local `local-speech-to-text` service.

### Configuration

Add the following sections to `~/.local/share/picoclaw/config.json`:

```json
{
  "voice": {
    "model_name": "local_stt"
  },
  "models": {
    "local_stt": {
      "model": "whisper",
      "api_key": "dummy",
      "base_url": "http://localhost:50090/v1"
    }
  }
}
```

## Implementation & Security Considerations

### Centralized Sandbox Options
To guarantee parity across all execution modes, `picoclaw-ctl` centralizes its systemd sandboxing properties in a single helper function (`get_shared_options`). The background service (installed via `install`), the transient command runner (`exec`), and the interactive shell (`shell`) all inherit the exact same filesystem, network, and security restrictions.

### Sandboxing Profile
PicoClaw utilizes a **Strict Namespaces Profile** for systemd isolation. Based on auditing the packaging and runtime configuration, these permissions are required:

1. **Go Runtime & Strict Memory Protection**
   - **Property Set**: `MemoryDenyWriteExecute=yes`.
   - **Rationale**: PicoClaw is written in Go, which compiles to a static native binary. It does not require dynamic JIT compilation or writable/executable memory mappings, allowing the strict enforcement of `MemoryDenyWriteExecute=yes` to mitigate JIT exploitation risks.

2. **Strict Namespaces & Process Isolation**
   - **Properties Enforced**: `ProtectProc=invisible`, `ProcSubset=pid`, and `RestrictNamespaces=yes`.
   - **Rationale**: Unlike agents that execute nested Bubblewrap/Docker tool sandboxes, PicoClaw runs completely self-contained tasks. It can thus block namespace creation and restrict `/proc` filesystem visibility to maximize host isolation.

3. **Strict Filesystem Isolation**
   - **Property Set**: `ProtectSystem=strict` and a tmpfs-mounted `$HOME` directory (`TemporaryFileSystem=%h`).
   - **Rationale**: Redirection of `HOME` to `%h` ensures correct user-level context pathing. The persistent home (`~/.local/share/picoclaw`), `~/agent-shared`, and `AGENT_PRIVATE_MOUNTS` are bind-mounted read-write, while other directories are read-only.

4. **Launcher vs CLI**
   - **Service Execution**: The systemd background service uses `picoclaw-launcher -no-browser` as its `ExecStart` target, running the built-in web console service.
   - **CLI Execution**: The `picoclaw-ctl exec` command specifically targets the `/usr/bin/picoclaw` executable rather than the launcher, providing direct access to the core agent CLI binary.
