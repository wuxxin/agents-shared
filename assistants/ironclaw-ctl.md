# IronClaw Reborn Agent Control Guide

This guide describes configuration, onboarding, and integration features specific to the IronClaw Reborn Agent runtime environment.

For shared commands, variable expansion rules, sidecars supervision, temporary file cleanups, and unified sandboxing profiles, see the general [Agent Service Guide](agents-ctl.md).

- **Source Code**: [GitHub - nearai/ironclaw](https://github.com/nearai/ironclaw)
- **Arch/AUR Packages**:
  - `ironclaw-reborn-git` (Reborn engine and WebUI)

---

## Agent-Specific Defaults

- **Home Directory:** `~/.local/sandbox/ironclaw`
- **Default Workspace Path:** `%h/.local/sandbox/ironclaw/.ironclaw/default/workspace`
- **Reborn Configuration File:** `~/.local/sandbox/ironclaw/.ironclaw/reborn/config.toml`
- **Default Port Web UI:** [3000](http://localhost:3000/) (started via `serve` subcommand, set via `HTTP_PORT` in `ironclaw.env`)

---

## Common Environment Variables

Configure these inside `~/.config/systemd/user/ironclaw.env`:
*   **`HTTP_HOST`** (Default: `127.0.0.1`): Host bind address.
*   **`HTTP_PORT`** (Default: `3000`): Listen port for Web UI / API gateway.
*   **`IRONCLAW_REBORN_PROFILE`** (Default: `local-dev-yolo`): Boot profile selector. Supported values: `local-dev`, `local-dev-yolo`, `production`, `migration-dry-run`.
*   **`IRONCLAW_REBORN_WEBUI_TOKEN`** (Default: `local_reborn_token`): Access token for Web UI authentication.
*   **`IRONCLAW_REBORN_WEBUI_USER_ID`** (Default: `default-owner`): User scope this runtime acts under.

### Environment Configuration Override

IronClaw supports a two-stage environment resolution order:
1. **Systemd Service Environment:** `~/.config/systemd/user/ironclaw.env`
2. **Application Environment Override:** `~/.local/sandbox/ironclaw/.ironclaw/.env`

The application environment override file (`.ironclaw/.env`) is loaded after `ironclaw.env`. Any variables defined in `.ironclaw/.env` will override conflicting keys defined in `ironclaw.env`.

---

## Onboarding & Wizards

*   **Setup Wizard**: Run `./assistants/ironclaw-ctl exec onboard` to configure database connections, select LLM providers, and setup default accounts.
*   **Interactive Chat**: Run `./assistants/ironclaw-ctl exec chat` to open a terminal chat session.

### Default User Setup & Messaging Pairing

#### Default User Setup
IronClaw Reborn executes tasks, saves history/threads, and accesses workspace mounts under a designated owner:
*   Set `default_owner = "default-owner"` in `~/.local/sandbox/ironclaw/.ironclaw/reborn/config.toml` (and ensure this matches the environment override variable `IRONCLAW_REBORN_WEBUI_USER_ID=default-owner`).

#### Signal Channel Configuration & Integration
The Signal channel connects the IronClaw agent to a running [signal-cli](https://github.com/AsamK/signal-cli) HTTP JSON-RPC daemon.

##### Environment Configuration
Configure the Signal channel by adding these variables to `~/.config/systemd/user/ironclaw.env` or the application `.env` file:

* **`SIGNAL_HTTP_URL`** (Default: `http://127.0.0.1:20889`): The endpoint of the running `signal-cli` daemon.
* **`SIGNAL_ACCOUNT`**: The phone number associated with the registered Signal bot account (e.g. `+1234567890`).
* **`SIGNAL_ALLOW_FROM`**: A comma-separated list of phone numbers or UUIDs allowed to message the bot (e.g. `+1987654321,uuid:xxxx-xxxx-xxxx`)
    *  Set to `*` to allow all senders. Leaving it empty forces new senders to go through the pairing flow.
* **`SIGNAL_GROUP_POLICY`** (Default: `allowlist`): The policy for group chats. Can be `allowlist`, `open`, or `disabled`.
* **`SIGNAL_DM_POLICY`**: (Default: `pairing`): The policy for direct messages. Can be `open`, `allowlist`, or `pairing`

##### Signal Daemon Setup (signal-cli)
To link your account and receive messages, run `signal-cli` in daemon mode:
```bash
signal-cli -a "+1234567890" daemon --http 127.0.0.1:20889
```

#### Senders Pairing Flow
To protect credentials, external direct messages (such as Signal contact requests) do not gain automatic access to the default user's workspace. They must go through a secure pairing process:
1.  **Incoming Code**: When a new, unauthorized sender messages the bot via Signal, the bot replies with a pairing challenge code:
    `Enter this code in IronClaw to pair your signal account: <CODE>. CLI fallback: ironclaw pairing approve signal <CODE>`
2.  **Approve Pairing**: An administrator must approve the request using the pairing code inside an authorized chat session (e.g. `./assistants/ironclaw-ctl exec chat` or Web UI) using the command:
    ```text
    approve signal <PAIRING_CODE>
    ```
3.  **Completion**: Once approved, all future messages from that Signal contact are linked to the configured default owner's memory space and workspace.


### Implementation & Security Considerations

#### Sandboxing Profile
IronClaw utilizes a **Relaxed Namespaces Profile** for systemd isolation:
1.  **WASM Sandbox Execution**: Configures `MemoryDenyWriteExecute=no` to allow the wasmtime JIT compiler to allocate writable/executable pages.
2.  **Docker Sandbox**: `RestrictNamespaces=yes` is omitted when Docker sandbox mode is active to allow container orchestration.
3.  **Physical Devices**: `PrivateDevices=yes` is active by default to hide physical hardware devices.

---

## Configuration & Architecture

This section documents features and configurations specific to the **Reborn** engine.

### Engine Architecture

*   **Binary**: Managed via the `/usr/bin/ironclaw-reborn` binary.
*   **Monty VM Python Execution**: Instead of executing flat tool calls in Rust, Reborn compiles tool invocations into Python code blocks executed dynamically inside an embedded Monty VM (Python interpreter).
*   **Core Primitives**: Unifies abstractions into 5 core primitives:
    *   `Thread` — History timeline sequence.
    *   `Step` — Single turn execution step.
    *   `Capability` — Leasable resources (tools, endpoints).
    *   `MemoryDoc` — Scoped knowledge assets.
    *   `Project` — Boundary for threads and files.
*   **Learning Loops**: Runs autonomous learning loops (Missions) for conversation insight extraction and tool-use self-repair.

### Web GUI

The Reborn Web UI is a React Single Page Application (SPA) providing stream tracking, project file workspaces, and interactive chat.
*   **Default Port**: Runs on port **`3000`** by default (started via `serve` subcommand, e.g. `./assistants/ironclaw-ctl exec serve`).
*   **Identity**: Configure default users in `~/.local/sandbox/ironclaw/.ironclaw/reborn/config.toml`:
    ```toml
    [identity]
    default_owner = "default-owner"
    ```
    Ensure `default_owner` matches the environment variable:
    ```env
    IRONCLAW_REBORN_WEBUI_USER_ID=default-owner
    ```
*   **Web Authentication**: Define the access token in `~/.local/sandbox/ironclaw/.ironclaw/.env`:
    ```env
    IRONCLAW_REBORN_WEBUI_TOKEN=your_reborn_auth_token
    ```
    Supports Google/GitHub OAuth browser SSO logins under the `webui-v2-beta` feature flag.

### Reborn Composition Profiles

Reborn uses composition profiles configured under the `[boot]` block of `reborn/config.toml` (or via the `IRONCLAW_REBORN_PROFILE` environment variable) to adapt the security model, database storage backend, and execution constraints:

*   **`local-dev`**: Designed for offline local development and quick testing.
    - **Storage**: Uses local embedded SQLite (libSQL) (`reborn-local-dev.db` under the reborn home directory).
    - **Security**: Enforces strict sandboxed tool execution path isolation.
    - **Networking**: Binds to loopback-only connections (`127.0.0.1`).
*   **`local-dev-yolo`** (Default): Designed for trusted laptop environments where sandboxing is secondary to ease of local host access.
    - **Storage**: Uses local embedded SQLite (libSQL).
    - **Security**: **Bypasses strict path/filesystem sandbox isolation**, giving local coding tools and commands direct read/write access to the user's host home directory.
    - **Enforcement Gate**: Because of the safety implications of exposing the host home filesystem, any subcommands run under this profile (e.g. `serve`, `repl`, `run`) must explicitly pass the `--confirm-host-access` flag to proceed (we append this on serve automatically).
*   **`hosted-single-tenant`**: Built for hosted single-tenant setups. Supports SQLite/libSQL or PostgreSQL database backends and wires login authentication portals.
*   **`production`**: Production composition profile. Requires a PostgreSQL backend with TLS (configured via environment overrides). Enforces full WASM sandboxing and Docker workers with namespace-level isolation.
*   **`migration-dry-run`**: Utility profile. Runs schema checks and PostgreSQL database migration scripts under production rules, and then terminates safely without booting the active runtime loops.

### Storage & PostgreSQL Configuration

By default, Reborn uses an embedded SQLite database (`reborn-local-dev.db`), requiring no configuration. To switch to PostgreSQL:
1.  Edit `~/.local/sandbox/ironclaw/.ironclaw/reborn/config.toml` to change the profile to `"production"` (or `"hosted-single-tenant"`).
2.  Uncomment the `[storage]` block:
    ```toml
    [storage]
    backend = "postgres"
    url_env = "IRONCLAW_REBORN_POSTGRES_URL"
    secret_master_key_env = "IRONCLAW_REBORN_SECRET_MASTER_KEY"
    pool_max_size = 2
    ```
3.  Add credentials to the environment file:
    ```env
    IRONCLAW_REBORN_POSTGRES_URL="postgres://postgres:password@localhost:5432/ironclaw_reborn"
    IRONCLAW_REBORN_SECRET_MASTER_KEY="your-secret-master-key"
    ```

### LLM Provider & Local Services Config

Reborn manages LLM providers and local endpoints through a JSON catalog. By default, `ironclaw-ctl` pre-configures all local services inside `~/.local/sandbox/ironclaw/.ironclaw/reborn/providers.json`:

```json
[
  {
    "id": "local-chat",
    "aliases": [],
    "protocol": "open_ai_completions",
    "api_key_env": "LLM_API_KEY",
    "api_key_required": false,
    "model_env": "LOCAL_MODEL",
    "default_base_url": "http://localhost:20080/v1",
    "default_model": "qwen3",
    "description": "Local llama-server Chat/Vision (port 20080)",
    "setup": {
      "kind": "api_key",
      "secret_name": "llm_local_chat_api_key",
      "display_name": "Local Chat"
    }
  },
  {
    "id": "local-embedding",
    "aliases": [],
    "protocol": "open_ai_completions",
    "api_key_env": "EMBEDDING_API_KEY",
    "api_key_required": false,
    "model_env": "LOCAL_MODEL",
    "default_base_url": "http://localhost:20082/v1",
    "default_model": "qwen3-embedding",
    "description": "Local llama-server Embeddings (port 20082)",
    "setup": {
      "kind": "api_key",
      "secret_name": "llm_local_embedding_api_key",
      "display_name": "Local Embedding"
    }
  },
  {
    "id": "local-rerank",
    "aliases": [],
    "protocol": "open_ai_completions",
    "api_key_env": "RERANK_API_KEY",
    "api_key_required": false,
    "model_env": "LOCAL_MODEL",
    "default_base_url": "http://localhost:20086/v1",
    "default_model": "qwen3-reranker",
    "description": "Local llama-server Reranker (port 20086)",
    "setup": {
      "kind": "api_key",
      "secret_name": "llm_local_rerank_api_key",
      "display_name": "Local Reranker"
    }
  },
  {
    "id": "local-speech-to-text",
    "aliases": [],
    "protocol": "open_ai_completions",
    "api_key_env": "TRANSCRIPTION_API_KEY",
    "api_key_required": false,
    "model_env": "LOCAL_MODEL",
    "default_base_url": "http://localhost:20090/v1",
    "default_model": "whisper-1",
    "description": "Local Whisper STT (port 20090)",
    "setup": {
      "kind": "api_key",
      "secret_name": "llm_local_stt_api_key",
      "display_name": "Local STT"
    }
  },
  {
    "id": "local-text-to-speech",
    "aliases": [],
    "protocol": "open_ai_completions",
    "api_key_env": "TTS_API_KEY",
    "api_key_required": false,
    "model_env": "LOCAL_MODEL",
    "default_base_url": "http://localhost:20095/v1",
    "default_model": "qwen3-tts",
    "description": "Local Qwen3 TTS (port 20095)",
    "setup": {
      "kind": "api_key",
      "secret_name": "llm_local_tts_api_key",
      "display_name": "Local TTS"
    }
  },
  {
    "id": "local-image",
    "aliases": [],
    "protocol": "open_ai_completions",
    "api_key_env": "IMAGE_API_KEY",
    "api_key_required": false,
    "model_env": "LOCAL_MODEL",
    "default_base_url": "http://localhost:20100/v1",
    "default_model": "sd-image",
    "description": "Local sd-server Image Generation (port 20100)",
    "setup": {
      "kind": "api_key",
      "secret_name": "llm_local_image_api_key",
      "display_name": "Local Image"
    }
  }
]
```

Next, the default chat LLM slot is selected in `~/.local/sandbox/ironclaw/.ironclaw/reborn/config.toml` under the `[llm.default]` block:
```toml
[llm.default]
provider_id = "local-chat"
model = "qwen3"
api_key_env = "LLM_API_KEY"
```

### Embeddings, STT, TTS & Image Services in Reborn

In the Reborn engine, specialized services (embeddings, reranking, STT, TTS, and image generation) are not managed via direct, static blocks in `config.toml`. Instead, they are loaded dynamically via skills and extension plugins which leverage the catalog definitions in `providers.json` or query the environment overrides:

*   **Embeddings & Reranking**: Used by search and memory capabilities. The embedding requests target the `local-embedding` provider (port `20082`). Reranking is performed natively via the Reciprocal Rank Fusion (RRF) algorithm (port `20086` for `local-rerank` is available for plugins if custom reranking is needed).
*   **Speech-to-Text (STT)**: Transcribes incoming audio files (e.g. from Signal voice messages). The transcription requests target the `local-speech-to-text` provider (port `20090`).
*   **Text-to-Speech (TTS)**: Synthesizes spoken replies from text. TTS requests target the `local-text-to-speech` provider (port `20095`).
*   **Image Generation**: Generates images on demand (e.g. via drawing tools). Image requests target the `local-image` provider (port `20100`).

### Signal Senders Pairing

To safely tie an external Signal sender to a configured default user (without exposing environment secrets):
1.  Ensure the default owner identity is configured in `reborn/config.toml` and matched with `IRONCLAW_REBORN_WEBUI_USER_ID` in the environment.
2.  Have the new sender message the bot. The bot replies with a pairing challenge code.
3.  Log into an authorized chat/CLI interface (or Web UI) and run the approval command:
    ```text
    approve signal <CODE>
    ```

### OpenCode Coding Agent (MCP)

Reborn replaces the legacy Agent Client Protocol (ACP) wrapper with native Model Context Protocol (MCP) integration. OpenCode is configured as a stdio-transport MCP server.

1.  **Configuration File**: Declare the server configuration in `~/.local/sandbox/ironclaw/.ironclaw/mcp-servers.json`:
    ```json
    {
      "schema_version": 1,
      "servers": [
        {
          "name": "opencode",
          "url": "",
          "transport": {
            "transport": "stdio",
            "command": "opencode",
            "args": [
              "--stdio"
            ]
          },
          "enabled": true,
          "description": "OpenCode coding agent running via Model Context Protocol (MCP)"
        }
      ]
    }
    ```
2.  **Execution Lifecycle**:
    *   On the first boot, Reborn reads `mcp-servers.json` and automatically migrates the servers into the database.
    *   Reborn launches `opencode --stdio` inside the host-mediated sandbox runtime, communicating over standard input/output (stdio).
    *   Ensure `opencode` is installed on your host or within the sandbox search path.
