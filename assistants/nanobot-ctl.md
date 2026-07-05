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

## Configuration Example

To run NanoBot fully locally using local services (Ollama for chat/vision, local Whisper for speech-to-text, and local Stable Diffusion for image generation), merge the following configuration into your `~/.nanobot/config.json`:

```json
{
  "agents": {
    "defaults": {
      "provider": "custom",
      "model": "qwen3",
      "temperature": 0.7,
      "maxToolIterations": 200
    }
  },
  "providers": {
    "custom": {
      "apiBase": "http://localhost:51080/v1",
      "apiKey": "chat-vision-unused"
      # custom: openai_compat used for chat AND Image generation
    },
    "siliconflow": {
      "apiBase": "http://localhost:51080/v1",
      "apiKey": "whisper-unused
      # siliconflow: OpenAITranscriptionProvider
    },
  },
  "transcription": {
    "enabled": true,
    "provider": "siliconflow", 
    "model": "whisper-1",
    "language": "auto",
    "maxDurationSec": 120
  },
  "tools": {
    "imageGeneration": {
      "enabled": true,
      "provider": "custom",
      "model": "z-image-turbo"
    }
  },
  "channels": {
    "signal": {
      "enabled": true,
      "account": "+1234567890",
      "apiBase": "http://localhost:50888",
      "streaming": true
    }
  }
}
```

### Enable WebUI

In the config, ensure the WebSocket channel is enabled:
   ```json
   { "channels": { "websocket": { "enabled": true } } }
   ```

## Memory

Add these blocks to `~/.local/sandbox/nanobot/config.json` to configure hybrid Dream memory stores

```json
{
  "memory": {
    "dream": {
      "enabled": true,
      "long_term_store": "vector"
    }
  }, 
}
```

## Implementation & Security Considerations

### Sandboxing & Security Profile Differences

Nanobot utilizes a **Relaxed Namespaces Profile** for systemd isolation. Based on auditing the packaging and runtime configuration, these permissions are required:

- **Properties Omitted:** `ProtectProc=invisible`, `ProcSubset=pid`, and `RestrictNamespaces=yes`.
- **Rationale:** Omitted because restricting namespaces inside systemd would prevent `bwrap` from using `CLONE_NEWUSER` and `CLONE_NEWNS` to create user/mount spaces.

1. **Namespace Support (Bubblewrap)**
   - **Properties Omitted**: `ProtectProc=invisible`, `ProcSubset=pid`, and `RestrictNamespaces=yes`.
   - **Rationale**: Nanobot runs tools and sub-agents that require their own isolation using bubblewrap (`bwrap`). `bwrap` relies on unprivileged user namespaces (`CLONE_NEWUSER` and `CLONE_NEWNS`) to build its sandbox; restricting namespaces or procfs traversal inside the systemd service would block this ability.

2. **Writable & Executable Memory (Python Runtimes)**
   - **Property Set**: `MemoryDenyWriteExecute=no`.
   - **Rationale**: Nanobot is written in Python and compiles dynamic objects or loads third-party native extensions that require W^X allocation permissions.

