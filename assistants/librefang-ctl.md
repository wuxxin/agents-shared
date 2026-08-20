# LibreFang Control Guide

This guide describes configuration, onboarding, and integration features specific to the LibreFang assistant.

For shared commands, variable expansion rules, sidecars supervision, temporary file cleanups, and unified sandboxing profiles, see the general [Agent Service Guide](agents-ctl.md).

- **Source Code**: [GitHub - librefang/librefang](https://github.com/librefang/librefang)
- **Arch/AUR Packages**: `librefang-git` (latest git-based package that provides the client and server binary `/usr/bin/librefang`).

---

## Agent-Specific Defaults

- **Home Directory:** `~/.local/sandbox/librefang`
- **Default Workspace Path:** `%h/.local/sandbox/librefang/.librefang/workspaces/agents/assistant`
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

To run LibreFang with a fully local inference pipeline (chat, embeddings, STT, TTS, and image generation), we use a hybrid configuration. 
- **Chat and Embeddings** use custom providers (`local-chat` and `local-embedding`) defined in `providers/local-chat.toml` and `providers/local-embedding.toml`.
- **STT, TTS, and Image generation** use the built-in `"openai"` provider name to satisfy the backend's hardcoded provider checks, with their base URLs overridden to point to the respective local services.

To edit the configuration files and the custom provider files together in your `$EDITOR`, run:
```bash
./assistants/librefang-ctl edit
```

### 1. Chat (LLM) Configuration
Chat is routed through the custom `local-chat` provider (configured in `providers/local-chat.toml` pointing to `llama-server` on port `20080`):
```toml
[default_model]
provider = "local-chat"
model = "qwen3"
api_key_env = "LOCAL_CHAT_API_KEY"
```

### 2. Vector Memory & Embeddings Configuration
Semantic memory embeddings are routed through the custom `local-embedding` provider (configured in `providers/local-embedding.toml` pointing to the embedding server on port `20082`):
```toml
[memory]
embedding_provider = "local-embedding"
embedding_model = "qwen3-embedding"
```

### 3. Speech-to-Text (STT) Configuration
Voice transcription is configured to use the built-in `"openai"` provider, but redirected to the local `whisper-server` (port `20090`) via `audio_base_url`:
```toml
[media]
audio_transcription = true
audio_provider = "openai"
audio_model = "whisper-1"
audio_base_url = "http://localhost:20090/v1"
```

### 4. Text-to-Speech (TTS) Configuration
Speech synthesis is configured to use the built-in `"openai"` provider, but redirected to the local `qwen3-tts-server` (port `20095`) via `[tts.openai]` `base_url`:
```toml
[tts]
enabled = true
provider = "openai"
timeout_secs = 60

[tts.openai]
base_url = "http://localhost:20095/v1"
model = "qwen3-tts"
voice = "serena"
format = "wav"
```

### 5. Local Image Generation Configuration
Image generation is configured to use the built-in `"openai"` provider, but redirected to the local `sd-server` (port `20100`) via `[provider_urls]` base URL override:
```toml
[provider_urls]
openai = "http://localhost:20100/v1"
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
SIGNAL_API_URL = "http://localhost:20889/"
SIGNAL_NUMBER = "+10987654321"       # The bot's Signal phone number
SIGNAL_ALLOW_LOCAL = "1"
SIGNAL_ALLOWED_USERS = "+1234567890"  # Your Signal phone number (allowed user)
```

Ensure both the `signal-cli` daemon and the REST API wrapper (listening on port `20889`) are active. LibreFang will connect to the REST wrapper to retrieve message updates and send replies.


## User Management and Authentication

LibreFang provides Role-Based Access Control (RBAC) to manage users, restrict tool usage, and route channel messages to specific workspaces.

### 1. Configuring Dashboard Authentication
By default, when binding to loopback (`127.0.0.1:4545`), no password is required. To configure password protection for the web dashboard interface:

#### Option A: Set via Environment Variables (Recommended)
Run `./assistants/librefang-ctl edit` and add these keys to the `.librefang/.env` file:
```bash
LIBREFANG_DASHBOARD_USER="my_user"
LIBREFANG_DASHBOARD_PASS="my_password"
```

#### Option B: Set in `config.toml`
Add these keys directly at the root of `config.toml`:
```toml
dashboard_user = "my_user"
dashboard_pass = "my_password"  # Or "vault:dashboard_password"
```
*(Note: If using `vault:`, run `./assistants/librefang-ctl exec vault set dashboard_password` to securely store the value).*

### 2. Tying a User to the Signal Channel
To link your physical Signal identity (phone number) to your LibreFang dashboard user, define a `[[users]]` block and route it via `[[bindings]]` in `config.toml`:

```toml
# Define the user and map their Signal identity
[[users]]
name = "my_user"
role = "owner"                          # Roles: owner, admin, user, viewer
channel_bindings = { signal = "+1234567890" }  # Ties phone number to user

# Route messages from the Signal channel to the assistant agent
[[bindings]]
agent = "assistant"
match_rule = { channel = "signal", peer_id = "+1234567890" }
```


## Tool Execution Timeouts

When agents execute tools (e.g., calling image generation, running shell commands, or executing python scripts), they are bound by execution timeout limits. If a tool call (such as a slow image generation model) exceeds these limits, the process is terminated.

You can configure and increase these timeouts in `config.toml`:

### 1. Global Tool Timeout Override
You can configure a global default timeout for all tool executions using the root-level setting:
```toml
# Timeout for individual tool executions in seconds (Default: 30)
tool_timeout_secs = 120
```

### 2. Per-Tool Timeout Overrides
You can pin custom timeouts for specific tools under the `[tool_timeouts]` block. Exact keys take priority over glob patterns:
```toml
[tool_timeouts]
# Set specific timeout for image generation tool in seconds
image_generate = 120
# Set specific timeout for shell_exec command executions (Default: 30)
shell_exec = 120
# Example of setting a longer timeout for browser tools
"mcp_browser_*" = 300
```

### 3. Local (Host) Execution Limits
If tools are run on the host (default `local` backend), the security boundaries are configured in `[exec_policy]`:
```toml
[exec_policy]
# Max execution timeout in seconds (Default: 30)
timeout_secs = 120

# No-output idle timeout in seconds (Default: 30)
# Terminate if the process produces no stdout/stderr for this duration.
no_output_timeout_secs = 60
```

### 2. Docker Sandbox Tool Execution Timeout
If you run tools inside a Docker sandbox container (`tool_exec.backend = "docker"`), the timeout limits are configured under the `[docker]` block:
```toml
[docker]
# Max execution time inside the container in seconds (Default: 60)
timeout_secs = 120
```

### 3. TTS Request Timeout
You can also adjust the timeout per Text-to-Speech (TTS) generation request under the `[tts]` block:
```toml
[tts]
# Timeout per TTS request in seconds (Default: 30)
timeout_secs = 60
```


## Environment Configuration Override

LibreFang supports a two-stage environment resolution order:
1. **Systemd Service Environment:** `~/.config/systemd/user/librefang.env`
2. **Application Environment Override:** `~/.local/sandbox/librefang/.librefang/.env`

The application environment override file (`.librefang/.env`) is loaded after `librefang.env`. Any variables defined in `.librefang/.env` will override conflicting keys defined in `librefang.env`.

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

