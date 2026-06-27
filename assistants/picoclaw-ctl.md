# PicoClaw Agent Management Guide

`picoclaw-ctl` is a control script for the PicoClaw agent and its launcher, designed similarly to the `librefang-ctl` architecture.

- **Source Code**: [GitHub - sipeed/picoclaw](https://github.com/sipeed/picoclaw)
- **Arch/AUR Packages**: `picoclaw` (AUR, source-based Go build). Alternatives: `picoclaw-bin` (AUR, pre-built binary), `picoclaw-git` (AUR, git-based).

## Commands

`picoclaw-ctl` supports all standard management operations. For detailed command reference and sandboxing path defaults, see [Standard Control Wrappers](../README.md#standard-control-wrappers-assistant-ctl).

## Installation

```bash
./assistants/picoclaw-ctl install --no-start
```
to create the home directory (`~/.local/sandbox/picoclaw`) 

### Using the CLI to Onboard

1. **Onboard Configuration**: Run `./assistants/picoclaw-ctl exec onboard` to generate `config.json` and initialize the workspace directory.
2. **Define Config**: Configure model providers and channel rules in `~/.local/sandbox/picoclaw/config.json`.
3. **Test & Run**: Run `./assistants/picoclaw-ctl exec agent -m "Hello"` to test connection. Launch background messaging gateway with `./assistants/picoclaw-ctl exec gateway`.

### Using the WebUI to Onboard

1. **Web Onboarding**: Run `./assistants/picoclaw-ctl exec picoclaw-launcher -no-browser` and open `http://localhost:18800` in your browser. Configure your LLM API Key under **Settings -> Providers** (credentials are saved securely in `.security.yml`) and set up a platform channel under **Settings -> Channels**.
2. **Launch Gateway**: Click "Start Gateway" in the launcher web interface (runs on port `18790` by default) and begin chatting.


### Switch to Local Inference & Qwen3
In the WebUI, add a Custom OpenAI provider with endpoint `http://localhost:50080/v1`, model `qwen3`, and key `unused`. Alternatively, configure `~/.local/sandbox/picoclaw/config.json` manually:
```json
{
  "version": 3,
  "agents": {
    "defaults": {
      "model_name": "qwen3",
      "context_window": 80128
    }
  },
  "model_list": [
    {
      "model_name": "qwen3",
      "provider": "openai",
      "model": "qwen3",
      "api_keys": ["unused"],
      "api_base": "http://localhost:50080/v1"
    }
  ]
}
```

### OpenClaw Migration

PicoClaw supports migrating configuration and secure details from an existing OpenClaw setup. To trigger the migration utility, run:
```bash
./assistants/picoclaw-ctl exec migrate
```
This maps your legacy files and `.security.yml` details directly into the PicoClaw configurations under `~/.local/sandbox/picoclaw/`.

## Search, Retrieval & Embedding Configuration

PicoClaw is an ultra-lightweight agent gateway and does not include a native built-in vector database or memory compression engine. Conversational history is stored in raw JSON files. To perform complex search and retrieval tasks, PicoClaw uses the Model Context Protocol (MCP) to delegate operations to external databases, search APIs, or RAG servers (such as Qdrant or `sqlite-vec`).

### Configuration

Add the following to `~/.local/sandbox/picoclaw/config.json`:

```json
{
  "version": 3,
  "embeddings": {
    "provider": "openai",
    "model": "qwen3-embedding",
    "base_url": "http://localhost:50082/v1",
    "api_key": "unused"
  },
  "tools": {
    "mcp": {
      "servers": {
        "sqlite-vec": {
          "command": "npx",
          "args": ["-y", "@modelcontextprotocol/server-sqlite-vec"],
          "env": {
            "DB_PATH": "/home/wuxxin/.local/sandbox/picoclaw/mcp-vectors.db"
          }
        }
      }
    }
  }
}
```

### Reranking Configuration

PicoClaw does not include native reranking due to its ultra-lightweight design. Reranking can be delegated via MCP to the local-inference reranker endpoint. Add a reranker MCP server to `~/.local/sandbox/picoclaw/config.json`:

```json
{
  "tools": {
    "mcp": {
      "servers": {
        "local-reranker": {
          "command": "npx",
          "args": ["-y", "@modelcontextprotocol/server-fetch"],
          "env": {
            "RERANK_URL": "http://localhost:50086/v1/rerank",
            "RERANK_MODEL": "qwen3-reranker"
          }
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

Add the following sections to `~/.local/sandbox/picoclaw/config.json`:

```json
{
  "model_list": [
    {
      "model_name": "local_stt",
      "provider": "openai",
      "model": "whisper-1",
      "api_keys": ["dummy"],
      "api_base": "http://localhost:50090/v1"
    },
    {
      "model_name": "local_tts",
      "provider": "openai",
      "model": "qwen3-tts",
      "api_keys": ["dummy"],
      "api_base": "http://localhost:50095/v1"
    }
  ],
  "voice": {
    "model_name": "local_stt",
    "tts_model_name": "local_tts"
  }
}
```

## Text-to-Speech Integration

PicoClaw supports Text-to-Speech (TTS) voice synthesis by configuring an OpenAI-compatible TTS model entry in the `model_list` (port `50095`) and pointing the `voice.tts_model_name` key to it. Outbound audio files are automatically generated and sent to messaging channels (such as Signal) when a message is dispatched. Refer to the configuration block above for details.

## Implementation & Security Considerations

### Centralized Sandbox Options
To guarantee parity across all execution modes, `picoclaw-ctl` centralizes its systemd sandboxing properties in a single helper function (`get_shared_options`). The background service (installed via `install`), the transient command runner (`exec`), and the interactive shell (`shell`) all inherit the exact same filesystem, network, and security restrictions.

### Sandboxing Profile
PicoClaw utilizes a **Relaxed Namespaces Profile** for systemd isolation, consistent with the other assistant sandboxing configurations. Based on auditing the packaging and runtime configuration, these permissions are set:

1. **Relaxed Namespaces & Process Isolation**
   - **Properties Omitted**: `ProtectProc=invisible`, `ProcSubset=pid`, and `RestrictNamespaces=yes`.
   - **Rationale**: Relaxed to match the standard agent profile, allowing compatibility with potential future MCP tool sandboxing or nested process execution.

2. **Memory Protection**
   - **Property Set**: `MemoryDenyWriteExecute=no`.
   - **Rationale**: Relaxed for consistency with other agent profiles. While Go doesn't require W^X allocations, the unified profile simplifies maintenance.

3. **Strict Filesystem Isolation**
   - **Property Set**: `ProtectSystem=strict` and a tmpfs-mounted `$HOME` directory (`TemporaryFileSystem=%h`).
   - **Rationale**: `HOME` is redirected to `%h/.local/sandbox/picoclaw` (the persistent bind-mounted data directory). The `~/agent-shared` directory is bind-mounted read-write, while other system directories are read-only.
   - **Custom Mounts**: Additional directories can be bind-mounted into the sandbox by configuring environment variables in `~/.config/systemd/user/picoclaw.env`:
     - `AGENT_PRIVATE_MOUNTS`: Space-separated list of directories inside `~/agent-private/` to expose (e.g. `AGENT_PRIVATE_MOUNTS="health diary"`).
     - `AGENT_SANDBOX_MOUNTS`: Space-separated list of sandbox paths from other agents/profiles to expose (e.g. `AGENT_SANDBOX_MOUNTS="opencode/.cache/opencode"`).
     - `AGENT_EXTRA_MOUNTS`: Space-separated list of arbitrary host paths mapped to relative paths under the user's HOME inside the sandbox (syntax: `absolute-dir:relative-dir-to-HOME`), eg. `AGENT_EXTRA_MOUNTS="/data/download:download"`

4. **Launcher vs CLI**
   - **Service Execution**: The systemd background service uses `picoclaw-launcher -no-browser` as its `ExecStart` target, running the built-in web console service.
   - **CLI Execution**: The `picoclaw-ctl exec` command specifically targets the `/usr/bin/picoclaw` executable rather than the launcher, providing direct access to the core agent CLI binary.
