# IronClaw Agent Management Guide

`ironclaw-ctl` manages the IronClaw Agent OS runtime, providing a hardened execution environment with WASM-sandboxed tool execution, credential protection, and prompt injection defense.

- **Source Code**: [GitHub - nearai/ironclaw](https://github.com/nearai/ironclaw)
- **Arch/AUR Packages**:
  - `ironclaw-git` (Legacy V1 daemon)
  - `ironclaw-reborn-git` (Reborn V2 engine and WebUI)

---

## Common Configuration & Management

This section covers configurations, management commands, and security profiles that are shared or common to both Legacy (V1) and Reborn (V2) installations.

### Commands

`ironclaw-ctl` supports all standard management operations:
*   `install [--no-start] [--new-config]` — Sets up the home directory, user service, and config files.
*   `uninstall` — Removes the systemd user service.
*   `start` / `stop` / `restart` / `status` — Standard systemd service lifecycles.
*   `enable` / `disable` — Toggles startup on system boot.
*   `logs` — Tails daemon logs using journalctl.
*   `edit` — Opens configuration and environment overrides in a text editor.
*   `exec <subcommand>` — Runs subcommands inside the systemd runtime.
*   `run <command>` — Runs arbitrary terminal commands inside the environment.
*   `shell` — Spawns an interactive bash shell within the service sandbox.

For detailed wrapper commands, see [Standard Control Wrappers](../README.md#standard-control-wrappers-assistant-ctl).

### Installation & Directory Setup

Install the runtime using:
```bash
./assistants/ironclaw-ctl install --no-start [--new-config]
```
This initializes the IronClaw home directory at `~/.local/sandbox/ironclaw` and registers the systemd user service.

The `--new-config` flag generates (or overwrites):
*   `~/.config/systemd/user/ironclaw.env` — systemd bootstrap environment variables.
*   `~/.local/sandbox/ironclaw/.ironclaw/.env` — Application secrets and local overrides.

### Common Environment Variables

Define these variables in `~/.config/systemd/user/ironclaw.env` (recommended) or `~/.local/sandbox/ironclaw/.ironclaw/.env` to customize host and port bindings:

*   **`HTTP_HOST`** (Default: `127.0.0.1`): Bind address for the HTTP interfaces.
*   **`HTTP_PORT`** (Default: `8080`): Listen port (legacy web gateway or reborn HTTP api).
*   **`SIGNAL_ACCOUNT`**: Phone number associated with the Signal bot account.
*   **`SIGNAL_ALLOW_FROM`**: Comma-separated list of phone numbers or UUIDs permitted to message the bot.

### Diagnostics & Onboarding

*   **Setup Wizard**: Run `./assistants/ironclaw-ctl exec onboard` to configure database connections, select LLM providers, and configure default accounts.
*   **Health Verification**: Run `./assistants/ironclaw-ctl exec status` to run credentials checks and check service health.
*   **Interactive Chat**: Run `./assistants/ironclaw-ctl exec chat` to open a terminal chat session.

### Default User Setup & Messaging Pairing

#### Default User Setup
Both Legacy and Reborn execute tasks, save history/threads, and access workspace mounts under a designated owner:
*   **Legacy (V1)**: Set `owner_id = "default-owner"` in `~/.local/sandbox/ironclaw/.ironclaw/config.toml`.
*   **Reborn (V2)**: Set `default_owner = "default-owner"` in `~/.local/sandbox/ironclaw/.ironclaw/reborn/config.toml` (and ensure this matches the environment override variable `IRONCLAW_REBORN_WEBUI_USER_ID=default-owner`).

#### Signal Channel Configuration & Integration
The Signal channel connects the IronClaw agent to a running [signal-cli](https://github.com/AsamK/signal-cli) HTTP JSON-RPC daemon. Both Legacy (V1) and Reborn (V2) use the same environment bootstrap variables and share the database-level pairing store.

##### Environment Configuration
Configure the Signal channel by adding these variables to `~/.config/systemd/user/ironclaw.env` or the application `.env` file:

*   **`SIGNAL_HTTP_URL`** (Default: `http://127.0.0.1:50889`): The endpoint of the running `signal-cli` daemon.
*   **`SIGNAL_ACCOUNT`**: The phone number associated with the registered Signal bot account (e.g. `+1234567890`).
*   **`SIGNAL_ALLOW_FROM`**: A comma-separated list of phone numbers or UUIDs allowed to message the bot (e.g. `+1987654321,uuid:xxxx-xxxx-xxxx`). Set to `*` to allow all senders. Leaving it empty forces new senders to go through the pairing flow.
*   **`SIGNAL_DM_POLICY`** (Default: `pairing`): The policy for direct messages. Can be `open`, `allowlist`, or `pairing`.
*   **`SIGNAL_GROUP_POLICY`** (Default: `allowlist`): The policy for group chats. Can be `allowlist`, `open`, or `disabled`.

##### Signal Daemon Setup (signal-cli)
To link your account and receive messages, run `signal-cli` in daemon mode:
```bash
signal-cli -a "+1234567890" daemon --http 127.0.0.1:50889
```

#### Senders Pairing Flow
To protect credentials, external direct messages (such as Signal contact requests) do not gain automatic access to the default user's workspace. They must go through a secure pairing process:
1.  **Incoming Code**: When a new, unauthorized sender messages the bot via Signal, the bot replies with a pairing challenge code:
    `Enter this code in IronClaw to pair your signal account: <CODE>. CLI fallback: ironclaw pairing approve signal <CODE>`
2.  **Approve Pairing**: An administrator must approve the request using the pairing code:
    *   **Legacy (V1 CLI)**: Run the command:
        ```bash
        ./assistants/ironclaw-ctl exec pairing approve signal <PAIRING_CODE>
        ```
        (or other channels like `telegram`, `whatsapp`, etc. as the channel parameter).
    *   **Reborn (V2 Chat/WebUI)**: Log into an authorized chat session (e.g. `./assistants/ironclaw-ctl exec chat` or Web UI) and run the command:
        ```text
        approve signal <PAIRING_CODE>
        ```
3.  **Completion**: Once approved, all future messages from that Signal contact are linked to the configured default owner's memory space and workspace.


### Implementation & Security Considerations

#### Systemd-Free Fallback (Direct Execution)
If systemd is not running in the current environment (e.g. inside a Bubblewrap sandbox or container), `ironclaw-ctl` automatically falls back to direct execution of the binary for `exec`, `shell`, and `run` commands. In this fallback mode:
- Environment variables are loaded directly from the environment override files.
- The isolated home directory (`~/.local/sandbox/ironclaw`) is exported as `$HOME` and set as the working directory.
- Commands that require systemd (`start`, `stop`, etc.) exit gracefully, notifying that systemd is unavailable.

#### Centralized Sandbox Options
To guarantee parity across all execution modes, `ironclaw-ctl` centralizes its systemd sandboxing properties in a single helper function (`get_shared_options`). The background service, transient command runner (`exec`), and interactive shell (`shell`) all inherit the exact same security restrictions.

#### Sandboxing Profile
IronClaw utilizes a **Relaxed Namespaces Profile** for systemd isolation:
1.  **WASM Sandbox Execution**: Configures `MemoryDenyWriteExecute=no` to allow the wasmtime JIT compiler to allocate writable/executable pages.
2.  **Docker Sandbox**: `RestrictNamespaces=yes` is omitted when Docker sandbox mode is active to allow container orchestration.
3.  **Physical Devices**: `PrivateDevices=yes` is active by default to hide physical hardware devices.
4.  **Strict Filesystem Isolation**: Enforces `ProtectSystem=strict` and a tmpfs-mounted `$HOME` directory (`TemporaryFileSystem=%h`). The persistent directories (`~/.local/sandbox/ironclaw`, `~/agent-shared`) are bind-mounted read-write, while the rest of the host filesystem is mounted read-only or hidden.

---

## Reborn (V2) Configuration & Architecture

This section documents features and configurations specific only to the next-generation **Reborn (V2)** engine.

### Engine V2 Architecture

*   **Binary**: Managed via the `/usr/bin/ironclaw-reborn` binary.
*   **Monty VM Python Execution**: Instead of executing flat tool calls in Rust, Reborn compiles tool invocations into Python code blocks executed dynamically inside an embedded Monty VM (Python interpreter).
*   **Core Primitives**: V2 unifies legacy abstractions into 5 core primitives:
    *   `Thread` — History timeline sequence.
    *   `Step` — Single turn execution step.
    *   `Capability` — Leasable resources (tools, endpoints).
    *   `MemoryDoc` — Scoped knowledge assets.
    *   `Project` — Boundary for threads and files.
*   **Learning Loops**: Runs autonomous learning loops (Missions) for conversation insight extraction and tool-use self-repair.

### Reborn Web GUI

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
    "protocol": "open_ai_completions",
    "api_key_env": "LLM_API_KEY",
    "api_key_required": false,
    "default_base_url": "http://localhost:50080/v1",
    "default_model": "qwen3",
    "description": "Local llama-server Chat/Vision (port 50080)"
  },
  {
    "id": "local-embedding",
    "protocol": "open_ai_completions",
    "api_key_env": "EMBEDDING_API_KEY",
    "api_key_required": false,
    "default_base_url": "http://localhost:50082/v1",
    "default_model": "qwen3-embedding",
    "description": "Local llama-server Embeddings (port 50082)"
  },
  {
    "id": "local-rerank",
    "protocol": "open_ai_completions",
    "api_key_env": "RERANK_API_KEY",
    "api_key_required": false,
    "default_base_url": "http://localhost:50086/v1",
    "default_model": "qwen3-reranker",
    "description": "Local llama-server Reranker (port 50086)"
  },
  {
    "id": "local-speech-to-text",
    "protocol": "open_ai_completions",
    "api_key_env": "TRANSCRIPTION_API_KEY",
    "api_key_required": false,
    "default_base_url": "http://localhost:50090/v1",
    "default_model": "whisper-1",
    "description": "Local Whisper STT (port 50090)"
  },
  {
    "id": "local-text-to-speech",
    "protocol": "open_ai_completions",
    "api_key_env": "TTS_API_KEY",
    "api_key_required": false,
    "default_base_url": "http://localhost:50095/v1",
    "default_model": "qwen3-tts",
    "description": "Local Qwen3 TTS (port 50095)"
  },
  {
    "id": "local-image",
    "protocol": "open_ai_completions",
    "api_key_env": "IMAGE_API_KEY",
    "api_key_required": false,
    "default_base_url": "http://localhost:50100/v1",
    "default_model": "sd-image",
    "description": "Local sd-server Image Generation (port 50100)"
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

In the Reborn V2 engine, specialized services (embeddings, reranking, STT, TTS, and image generation) are not managed via direct, static blocks in `config.toml`. Instead, they are loaded dynamically via skills and extension plugins which leverage the catalog definitions in `providers.json` or query the environment overrides:

*   **Embeddings & Reranking**: Used by search and memory capabilities. The embedding requests target the `local-embedding` provider (port `50082`). Reranking is performed natively via the Reciprocal Rank Fusion (RRF) algorithm (port `50086` for `local-rerank` is available for plugins if custom reranking is needed).
*   **Speech-to-Text (STT)**: Transcribes incoming audio files (e.g. from Signal voice messages). The transcription requests target the `local-speech-to-text` provider (port `50090`).
*   **Text-to-Speech (TTS)**: Synthesizes spoken replies from text. TTS requests target the `local-text-to-speech` provider (port `50095`).
*   **Image Generation**: Generates images on demand (e.g. via drawing tools). Image requests target the `local-image` provider (port `50100`).


### Signal Senders Pairing

To safely tie an external Signal sender to a configured default user (without exposing environment secrets):
1.  Ensure the default owner identity is configured in `reborn/config.toml` and matched with `IRONCLAW_REBORN_WEBUI_USER_ID` in the environment.
2.  Have the new sender message the bot. The bot replies with a pairing challenge code.
3.  Log into an authorized chat/CLI interface (or Web UI) and run the approval command:
    ```text
    approve signal <CODE>
    ```

### OpenCode Coding Agent (MCP)

Reborn (V2) replaces the legacy Agent Client Protocol (ACP) wrapper with native Model Context Protocol (MCP) integration. OpenCode is configured as a stdio-transport MCP server.

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

---

## 3. Legacy (V1) Configuration

This section documents features and configurations specific only to the **Legacy (V1)** daemon.

### Configuration File

*   **Binary**: Managed via the `/usr/bin/ironclaw` binary.
*   **File Path**: `~/.local/sandbox/ironclaw/.ironclaw/config.toml`.
*   **Auth Token**: Set a static bearer token under `[channels]` in `config.toml`:
    ```toml
    [channels]
    gateway_enabled = true
    gateway_auth_token = "local_admin_token"
    ```
*   **Default User**: Define a default owner in `config.toml`:
    ```toml
    owner_id = "default-owner"
    ```

### PostgreSQL + pgvector Setup

Legacy IronClaw requires a running PostgreSQL 15+ database with the `pgvector` extension installed.

#### Database Creation
```bash
# Create database user and database, and activate vector extension for database
createuser ironclaw -P 'PASSWORD'
createdb ironclaw -O ironclaw
psql -d ironclaw -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

#### Environment Configuration
Supply database URL and pool details in the environment files:
*   **`DATABASE_URL`**: Connection string format: `postgres://[user]:[password]@[host]:[port]/[database]`.
*   **`DATABASE_POOL_SIZE`** (Default: `30`): Maximum size of the database connection pool.
*   **`DATABASE_SSLMODE`**: SSL connection mode. Supported values: `disable`, `prefer`, `require`.

#### Supplying PostgreSQL Password
Since the Rust Postgres driver parses the URL literally without falling back to `PGPASSWORD` by default, use bash interpolation in `ironclaw.env`:
```env
PGPASSWORD="your_secret_password"
DATABASE_URL="postgres://ironclaw:${PGPASSWORD}@localhost/ironclaw"
```

### Local Inference Config

Configure local provider endpoints and models directly in `~/.local/sandbox/ironclaw/.ironclaw/config.toml`:
```toml
llm_backend = "openai_compatible"
openai_compatible_base_url = "http://localhost:50080/v1"
selected_model = "qwen3"
```

### Embeddings & Transcription Services

Legacy V1 uses dedicated static TOML configuration blocks in `config.toml`:

```toml
[embeddings]
enabled = true
provider = "openai"
model = "qwen3-embedding"
openai_embedding_base_url = "http://localhost:50082/v1"

[transcription]
enabled = true
provider = "openai"
model = "whisper-1"
openai_transcription_base_url = "http://localhost:50090/v1"
```

### OpenCode Coding Agent (ACP)

Legacy integrates with external coding agents like **OpenCode** using the Agent Client Protocol (ACP).
1.  Configure ACP protocol options in `~/.local/sandbox/ironclaw/.ironclaw/config.toml`:
    ```toml
    [sandbox]
    acp_enabled = true
    ```
2.  Declare the command mapping in `~/.local/sandbox/ironclaw/.ironclaw/acp-agents.json`:
    ```json
    {
      "agents": [
        {
          "name": "opencode",
          "command": "opencode",
          "args": ["--stdio"],
          "env": {},
          "enabled": true,
          "description": "OpenCode coding agent running via Agent Client Protocol (ACP)"
        }
      ],
      "schema_version": 1
    }
    ```
3.  Configure memory limits and timeout bounds in the service environment:
    *   **`ACP_MEMORY_LIMIT_MB`** (Default: `4096`): Memory allocation limit.
    *   **`ACP_TIMEOUT_SECS`** (Default: `1800`): Maximum allowed execution time.
4.  **CLI Management**:
    *   `./assistants/ironclaw-ctl exec acp list` — Lists registered agents.
    *   `./assistants/ironclaw-ctl exec acp toggle <name>` — Enables/disables an agent.
    *   `./assistants/ironclaw-ctl exec acp test <name>` — Runs connection diagnostics.

### Signal Channel Configuration

Configure the Signal channel in `~/.local/sandbox/ironclaw/.ironclaw/config.toml`:
```toml
[channels]
signal_enabled = true
signal_http_url = "http://127.0.0.1:50889"
signal_dm_policy = "pairing"        # Policies: open | allowlist | pairing
signal_group_policy = "allowlist"   # Policies: allowlist | open | disabled
```

---

## Architectural differences between the Legacy (V1) daemon and the Reborn (V2) engine.

| Feature Area | Legacy (V1) | Reborn (V2) |
|---|---|---|
| **Runtime Binary** | `/usr/bin/ironclaw` (compiled from Rust backend) | `/usr/bin/ironclaw-reborn` (compiled from `crates/ironclaw_reborn_cli`) |
| **Execution Loop** | Standard Rust-native agent loop compiling flat tool calls | Python CodeAct loop running inside an embedded Monty VM (allows multi-tool compounding) |
| **Default Web Port** | `8080` (Web Gateway & Webhooks) | `3000` (started via `serve` subcommand, serving React SPA UI) |
| **Primary Database** | PostgreSQL 15+ with the `pgvector` extension (required) | SQLite/libSQL (`reborn-local-dev.db` in reborn home) by default for local dev; PostgreSQL is optional for production |
| **Configuration Files** | `~/.local/sandbox/ironclaw/.ironclaw/config.toml` | `~/.local/sandbox/ironclaw/.ironclaw/reborn/config.toml` |
| **Client Authentication** | Bearer token configured via `gateway_auth_token` in `config.toml` | Bearer token via `IRONCLAW_REBORN_WEBUI_TOKEN` env var, and Google/GitHub OAuth browser SSO |
| **LLM Provider Config** | Flat fields in `config.toml` (e.g. `llm_backend`, `selected_model`) | Structured catalog in `reborn/providers.json` & slot selector in `reborn/config.toml` |
| **Embeddings & STT** | Direct `[embeddings]` and `[transcription]` blocks in `config.toml` | Managed dynamically through skills and extension plugins |
| **Coding Integration** | Agent Client Protocol (ACP) configured via `acp-agents.json` | Native host-mediated WASM/MCP security policies |
| **Traces & Diagnostics** | Direct CLI commands and file logging | Bounded Operator Logs, SSE live thinking streams, and `TraceClientHost` facades |
| **Scheduled Jobs** | Cron-pinned jobs configured in `config.toml` | `TriggerSchedule::Once` and recurring trigger loops managed in reborn composition |

