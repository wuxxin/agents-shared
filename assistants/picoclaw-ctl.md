# PicoClaw Control Guide

This guide describes configuration, onboarding, and integration features specific to the PicoClaw assistant.

For shared commands, variable expansion rules, sidecars supervision, temporary file cleanups, and unified sandboxing profiles, see the general [Agent Service Guide](agents-ctl.md).

- **Source Code**: [GitHub - sipeed/picoclaw](https://github.com/sipeed/picoclaw)
- **Arch/AUR Packages**: `picoclaw` (AUR, source-based Go build). Alternatives: `picoclaw-bin` (AUR, pre-built binary), `picoclaw-git` (AUR, git-based).

---

## Agent-Specific Defaults

- **Home Directory:** `~/.local/sandbox/picoclaw`
- **Default Workspace Path:** `%h/.local/sandbox/picoclaw/.picoclaw/workspace`
- **Configuration File:** `~/.local/sandbox/picoclaw/config.json`
- **Launcher Web UI Port:** [18800](http://localhost:18800/) (set via `picoclaw-launcher` startup parameters)
- **Background Gateway Port:** [18790](http://localhost:18790/)

---

## Onboarding & Wizards

*   **CLI Onboarding**: Run `./assistants/picoclaw-ctl exec onboard` to generate `config.json` and initialize the workspace directory.
*   **Web Onboarding**: Run `./assistants/picoclaw-ctl start`, then open `http://localhost:18800` in your browser to configure providers (saved in `.security.yml`) and platform channels.
*   **OpenClaw Migration**: Run `./assistants/picoclaw-ctl exec migrate` to import legacy settings.

---

## Switch to Local Inference & Qwen3

To route PicoClaw to local inference servers, configure `~/.local/sandbox/picoclaw/config.json`:

```json
{
  "version": 3,
  "agents": {
    "defaults": {
      "model_name": "qwen3",
      "context_window": 120192
    }
  },
  "model_list": [
    {
      "model_name": "qwen3",
      "provider": "openai",
      "model": "qwen3",
      "api_keys": ["unused"],
      "api_base": "http://localhost:20080/v1"
    }
  ]
}
```

---

## MCP & Speech Integration

Configure `~/.local/sandbox/picoclaw/config.json` to load local MCP fetch-rerank and speech synthesis providers:

```json
{
  "embeddings": {
    "provider": "openai",
    "model": "qwen3-embedding",
    "base_url": "http://localhost:20082/v1",
    "api_key": "unused"
  },
  "tools": {
    "mcp": {
      "servers": {
        "local-reranker": {
          "command": "npx",
          "args": ["-y", "@modelcontextprotocol/server-fetch"],
          "env": {
            "RERANK_URL": "http://localhost:20086/v1/rerank",
            "RERANK_MODEL": "qwen3-reranker"
          }
        }
      }
    }
  },
  "model_list": [
    {
      "model_name": "local_stt",
      "provider": "openai",
      "model": "whisper-1",
      "api_keys": ["dummy"],
      "api_base": "http://localhost:20090/v1"
    },
    {
      "model_name": "local_tts",
      "provider": "openai",
      "model": "qwen3-tts",
      "api_keys": ["dummy"],
      "api_base": "http://localhost:20095/v1"
    }
  ],
  "voice": {
    "model_name": "local_stt",
    "tts_model_name": "local_tts"
  }
}
```

## Implementation & Security Considerations

### Sandboxing Profile
PicoClaw utilizes a **Relaxed Namespaces Profile** for systemd isolation, consistent with the other assistant sandboxing configurations. Based on auditing the packaging and runtime configuration, these permissions are set:

1. **Relaxed Namespaces & Process Isolation**
   - **Properties Omitted**: `ProtectProc=invisible`, `ProcSubset=pid`, and `RestrictNamespaces=yes`.
   - **Rationale**: Relaxed to match the standard agent profile, allowing compatibility with potential future MCP tool sandboxing or nested process execution.

2. **Memory Protection**
   - **Property Set**: `MemoryDenyWriteExecute=no`.
   - **Rationale**: Relaxed for consistency with other agent profiles. While Go doesn't require W^X allocations, the unified profile simplifies maintenance.

