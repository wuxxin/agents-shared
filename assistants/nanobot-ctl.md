# NanoBot Control Guide

This guide describes configuration, onboarding, and integration features specific to the NanoBot assistant service.

For shared commands, variable expansion rules, sidecars supervision, temporary file cleanups, and unified sandboxing profiles, see the general [Agent Service Guide](agents-ctl.md).

- **Source Code**: [GitHub - HKUDS/nanobot](https://github.com/HKUDS/nanobot)
- **Arch/AUR Packages**: No system-wide AUR packages are available for NanoBot. It is a lightweight Python framework designed to be installed inside a virtual environment using `uv` (pip package: `nanobot-ai`).

---

## Agent-Specific Defaults

- **Home Directory:** `~/.local/sandbox/nanobot`
- **Default Workspace Path:** `%h/.local/sandbox/nanobot/.nanobot/workspace`
- **Configuration File:** `~/.local/sandbox/nanobot/config.json`
- **Gateway API Port:** [8790](http://localhost:8790/) (set via `NANOBOT_PORT` inside `nanobot.env`)

---

## Onboarding & Wizards

*   **Configuration Wizard**: Run `./assistants/nanobot-ctl exec onboard --wizard` to generate the onboarding default configurations.
*   **Verification**: Run `./assistants/nanobot-ctl exec agent -m "Hello"` to verify connection.

---

## Sandboxing & Security Profile Differences

Because NanoBot executes skills and external tools using bubblewrap (`bwrap`) to build nested runtime sandboxes, the systemd configurations are adjusted:

- **Properties Omitted:** `ProtectProc=invisible`, `ProcSubset=pid`, and `RestrictNamespaces=yes`.
- **Rationale:** Omitted because restricting namespaces inside systemd would prevent `bwrap` from using `CLONE_NEWUSER` and `CLONE_NEWNS` to create user/mount spaces.

---

## Switch to Local Inference & Qwen3

To route NanoBot to local inference servers, configure `~/.local/sandbox/nanobot/config.json`:

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

---

## MCP, RAG & Speech Configuration

Add these blocks to `~/.local/sandbox/nanobot/config.json` to configure hybrid Dream memory stores, local embeddings, fetch-rerank MCP, and speech/image synthesizers:

```json
{
  "memory": {
    "dream": {
      "enabled": true,
      "long_term_store": "vector"
    }
  },
  "embeddings": {
    "provider": "openai_compatible/local",
    "model": "text-embedding-3-small",
    "base_url": "http://localhost:50082/v1"
  },
  "tools": {
    "mcp_servers": {
      "local-reranker": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-fetch"],
        "env": {
          "RERANK_URL": "http://localhost:50086/v1/rerank",
          "RERANK_MODEL": "qwen3-reranker"
        }
      }
    },
    "image_generation": {
      "enabled": true,
      "provider": "openai",
      "model": "stability-ai/sdxl"
    }
  },
  "providers": {
    "openai": {
      "api_key": "unused",
      "api_base": "http://localhost:50100/v1"
    }
  },
  "transcription": {
    "provider": "openai",
    "openai": {
      "api_key": "dummy",
      "base_url": "http://localhost:50090/v1"
    }
  }
}
```

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

## Implementation & Security Considerations

### Sandboxing Profile
Nanobot utilizes a **Relaxed Namespaces Profile** for systemd isolation. Based on auditing the packaging and runtime configuration, these permissions are required:

1. **Namespace Support (Bubblewrap)**
   - **Properties Omitted**: `ProtectProc=invisible`, `ProcSubset=pid`, and `RestrictNamespaces=yes`.
   - **Rationale**: Nanobot runs tools and sub-agents that require their own isolation using bubblewrap (`bwrap`). `bwrap` relies on unprivileged user namespaces (`CLONE_NEWUSER` and `CLONE_NEWNS`) to build its sandbox; restricting namespaces or procfs traversal inside the systemd service would block this ability.

2. **Writable & Executable Memory (Python Runtimes)**
   - **Property Set**: `MemoryDenyWriteExecute=no`.
   - **Rationale**: Nanobot is written in Python and compiles dynamic objects or loads third-party native extensions that require W^X allocation permissions.

