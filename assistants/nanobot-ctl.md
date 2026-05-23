# Nanobot Setup and Usage Guide

`nanobot-ctl` is a lightweight, virtual environment based installation and management script designed to deploy the `nanobot` python service. It utilizes `uv` to manage an isolated virtual environment and integrates seamlessly with `systemd` user services.

- **Source Code**: [GitHub - HKUDS/nanobot](https://github.com/HKUDS/nanobot)
- **Arch/AUR Packages**: No system-wide AUR packages are available for NanoBot. It is a lightweight Python framework designed to be installed inside a virtual environment using `uv` (pip package: `nanobot-ai`).

## Commands

`nanobot-ctl` supports all standard management operations. For detailed command reference and sandboxing path defaults, see [Standard Control Wrappers](../README.md#standard-control-wrappers-assistant-ctl).

## Installation

Ensure you have `uv` installed, then simply run the script's `install` command:

```bash
./assistants/nanobot-ctl install --no-start
```
to initialize `~/.local/sandbox/nanobot`, set up the python virtualenv, install the `nanobot-ai` package, and register the systemd unit without starting it.

During installation, `nanobot-ctl` will set up the isolated environment and generate standard service files.

### Configuration Wizard

Run the interactive onboarding wizard via `./assistants/nanobot-ctl exec onboard --wizard` to generate the default configuration.

### Switch to Local Inference & Qwen3
Edit `~/.local/sandbox/nanobot/config.json` (via `./assistants/nanobot-ctl config`) to configure the local OpenAI-compatible endpoint and default models (under `agents.defaults`):
```json
{
  "providers": {
    "openai_compatible": {
      "local": {
        "api_key": "unused",
        "base_url": "http://localhost:50080/v1"
      }
    }
  },
  "agents": {
    "defaults": {
      "provider": "openai_compatible/local",
      "model": "qwen3"
    }
  }
}
```

### Enable WebUI

In the config, ensure the WebSocket channel is enabled:
   ```json
   { "channels": { "websocket": { "enabled": true } } }
   ```
### Start & Verify
Run `./assistants/nanobot-ctl start`. Verify status with `./assistants/nanobot-ctl status` and access the WebUI console at `http://localhost:8790`.



## Configuration & Ports
- **Configuration File**: Stored at `~/.local/sandbox/nanobot/config.json`.
- **Default Port**: The gateway service runs on port `8790` (set via `--port 8790` in the systemd service unit) to prevent conflicts with other services.

## OpenClaw Migration

OpenClaw migration is not natively supported by NanoBot. Configuration must be set up manually using the configuration wizard (`onboard --wizard`) or by editing the JSON configuration.


## Signal Channel Configuration

NanoBot supports native Signal integration. It communicates with a local `signal-cli` daemon in HTTP mode.

### Configuration

Add the following to your `~/.local/sandbox/nanobot/config.json` configuration file under the `"channels"` block (via `nanobot-ctl config`):

```json
{
  "channels": {
    "signal": {
      "enabled": true,
      "phoneNumber": "+1234567890",
      "daemonHost": "localhost",
      "daemonPort": 50888,
      "dm": {
        "enabled": true,
        "policy": "open"
      },
      "group": {
        "enabled": true,
        "policy": "open",
        "requireMention": true
      }
    }
  }
}
```

Ensure the local `signal-cli` daemon is running. NanoBot will connect, handle inbound messages via Server-Sent Events, convert markdown formatting to native Signal styles, and handle reconnects automatically.

## Search, Retrieval & Embedding Configuration

NanoBot implements a structured two-stage memory system ("Dream") that separates active conversation buffers from long-term memory. Long-term memory is queried using vector similarity search (RAG). It also includes a Document Store to index, chunk, and search local files (PDFs, TXT, markdown) and can execute dynamic external search via MCP (Model Context Protocol).

### Configuration

Add the following configuration blocks to `~/.local/sandbox/nanobot/config.json` (via `./assistants/nanobot-ctl config`):

```json
{
  "memory": {
    "dream": {
      "enabled": true,
      "buffer_size_limit": 4096,
      "long_term_store": "vector"
    }
  },
  "document_store": {
    "enabled": true,
    "chunk_size": 500,
    "chunk_overlap": 50,
    "allowed_extensions": [".pdf", ".txt", ".md"]
  },
  "embeddings": {
    "provider": "openai_compatible/local",
    "model": "text-embedding-3-small",
    "api_key": "unused",
    "base_url": "http://localhost:50080/v1"
  },
  "mcp": {
    "servers": {
      "brave-search": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-brave-search"],
        "env": {
          "BRAVE_API_KEY": "your_api_key_here"
        }
      }
    }
  }
}
```

### Reranking Configuration

NanoBot does not include native reranking support. To add reranking capabilities, configure a custom MCP tool that wraps the local-inference reranker endpoint. Add the following MCP server definition to `config.json`:

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

The agent can then call the reranker via the MCP tool to reorder retrieval results before injecting them into context. The reranker endpoint accepts `POST /v1/rerank` with `{"model": "qwen3-reranker", "query": "...", "documents": ["..."]}`.

## Speech-to-Text Integration

NanoBot supports local transcription using an external OpenAI-compatible Whisper server. You can configure it to point to the `local-speech-to-text` service.

### Configuration

Add the following environment variables to `~/.config/systemd/user/nanobot.env` (via `./assistants/nanobot-ctl edit`):

```bash
# Point transcription endpoint to local-speech-to-text service
OPENAI_TRANSCRIPTION_BASE_URL="http://localhost:50090/v1/audio/transcriptions"
OPENAI_API_KEY="dummy"  # Required placeholder to activate the provider
```

Alternatively, you can configure it inside `~/.local/sandbox/nanobot/config.json`:

```json
{
  "transcription": {
    "provider": "openai",
    "openai": {
      "api_key": "dummy",
      "base_url": "http://localhost:50090/v1/audio/transcriptions"
    }
  }
}
```


## Implementation & Security Considerations

### Centralized Sandbox Options
To guarantee parity across all execution modes, `nanobot-ctl` centralizes its systemd sandboxing properties in a single helper function (`get_shared_options`). The background service (installed via `install`), the transient command runner (`exec`), and the interactive shell (`shell`) all inherit the exact same filesystem, network, and security restrictions.

### Sandboxing Profile
Nanobot utilizes a **Relaxed Namespaces Profile** for systemd isolation. Based on auditing the packaging and runtime configuration, these permissions are required:

1. **Namespace Support (Bubblewrap)**
   - **Properties Omitted**: `ProtectProc=invisible`, `ProcSubset=pid`, and `RestrictNamespaces=yes`.
   - **Rationale**: Nanobot runs tools and sub-agents that require their own isolation using bubblewrap (`bwrap`). `bwrap` relies on unprivileged user namespaces (`CLONE_NEWUSER` and `CLONE_NEWNS`) to build its sandbox; restricting namespaces or procfs traversal inside the systemd service would block this ability.

2. **Writable & Executable Memory (Python Runtimes)**
   - **Property Set**: `MemoryDenyWriteExecute=no`.
   - **Rationale**: Nanobot is written in Python and compiles dynamic objects or loads third-party native extensions that require W^X allocation permissions.

3. **Strict Filesystem Isolation**
   - **Property Set**: `ProtectSystem=strict` and a tmpfs-mounted `$HOME` directory (`TemporaryFileSystem=%h`).
   - **Rationale**: Redirection of `HOME` to `~/.local/sandbox/nanobot` ensures that subprocesses do not write to the host user's real home. The persistent home, `~/agent-shared`, and `AGENT_PRIVATE_MOUNTS` are bind-mounted read-write, while other directories are read-only.
