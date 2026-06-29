# LibreFang Control Guide

This guide describes configuration, onboarding, and integration features specific to the LibreFang assistant.

For shared commands, variable expansion rules, sidecars supervision, temporary file cleanups, and unified sandboxing profiles, see the general [Agent Service Guide](agents-ctl.md).

- **Source Code**: [GitHub - librefang/librefang](https://github.com/librefang/librefang)
- **Arch/AUR Packages**: `librefang-git` (latest git-based package that provides the client and server binary `/usr/bin/librefang`).

---

## Agent-Specific Defaults

- **Home Directory:** `~/.local/sandbox/librefang`
- **Default Workspace Path:** `%h/.local/sandbox/librefang/.librefang/agents/default/workspace`
- **Configuration File:** `~/.local/sandbox/librefang/.librefang/config.toml`
- **Default Gateway Port:** [4545](http://localhost:4545/) (set via `LIBREFANG_PORT` inside `librefang.env`)

---

## Onboarding & Wizards

Initialize the LibreFang configurations by running:
```bash
./assistants/librefang-ctl exec onboard
```
This sets up default provider JSON templates and the `config.toml` parameters.

---

## Local Inference

To switch LibreFang to local llama-server chat and embeddings, configure `config.toml`:

```toml
[llm]
model = "qwen3"
base_url = "http://localhost:50080/v1"
api_key = "unused"

[embeddings]
enabled = true
provider = "openai"
model = "qwen3-embedding"
openai_embedding_base_url = "http://localhost:50082/v1"
```

### Voice Transcription Integration
Configure LibreFang to use the local Whisper STT service (port `50090`) by editing `config.toml`:

```toml
[transcription]
enabled = true
provider = "openai"
model = "whisper-1"
openai_transcription_base_url = "http://localhost:50090/v1"
```

## Signal Channel Configuration

LibreFang supports native Signal integration. In this environment, it interfaces with the Go-based REST API wrapper.

Add the following to your `~/.librefang/config.toml` config file (located in the sandboxed home directory at `~/.local/sandbox/librefang/.librefang/config.toml`):

```toml
[[sidecar_channels]]
command = "python3"
args = ["-m", "librefang.sidecar.adapters.signal"]
name = "signal"
channel_type = "signal"

[sidecar_channels.env]
SIGNAL_API_URL = "http://localhost:50889/"
SIGNAL_NUMBER = "+1234567890"
SIGNAL_ALLOW_LOCAL = "1"
```

Ensure both the `signal-cli` daemon and the REST API wrapper (listening on port `50889`) are active. LibreFang will connect to the REST wrapper to retrieve message updates and send replies.


---

## Finding Configuration Environment Variables

LibreFang does **not** feature an arbitrary, dynamic environment override mapping mechanism (such as `ZEROCLAW_*` key-path parsers). Instead, configuration parameters must be managed directly in the TOML configuration file or via the CLI.

### Locating Configuration Properties in Source Code
1. **Source Schema Definition**: Open the configuration types module at [types.rs](scratch/librefang/crates/librefang-types/src/config/types.rs) and inspect the `UserConfig` struct (and its nested types).
2. **How to Search**:
   - To find config fields, inspect the types file or query it. You can search using ripgrep:
     ```bash
     rg "pub \w*embedding_provider" scratch/librefang/crates/librefang-types/
     ```
3. **CLI Config Commands**: Use LibreFang's CLI tool to read and query configuration settings:
   - Run `./assistants/librefang-ctl exec config show` to inspect the complete parsed config.
   - Run `./assistants/librefang-ctl exec config get <dotted.path>` (e.g., `default_model.provider`) to fetch the value of a specific setting.
   - Run `./assistants/librefang-ctl exec config set <dotted.path> <value>` to change a config key.
4. **Config Validation**: Run `./assistants/librefang-ctl exec doctor` to validate configuration syntax and display errors/warnings.

---

## Implementation & Security Considerations

### Sandboxing Profile
LibreFang utilizes a **Relaxed Namespaces Profile** for systemd isolation. Based on auditing the packaging and runtime configuration, these permissions are required:

1. **Namespace Support**
   - **Properties Omitted**: `ProtectProc=invisible`, `ProcSubset=pid`, and `RestrictNamespaces=yes`.
   - **Rationale**: LibreFang orchestrates tools and sub-agents that require their own isolation using bubblewrap (`bwrap`). `bwrap` relies on unprivileged user namespaces (`CLONE_NEWUSER` and `CLONE_NEWNS`) to build its sandbox; restricting namespaces or procfs traversal inside the systemd service would block this ability.

2. **Writable & Executable Memory (Execution Runtimes)**
   - **Property Set**: `MemoryDenyWriteExecute=no`.
   - **Rationale**: Required for runtime code generators, JITs, and executing dynamically compiled Python/Javascript code blocks during tool workflows.

