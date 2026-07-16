# Standalone Hindsight Memory Service Guide

`local-memory.sh` manages the standalone Hindsight memory API server systemd user service (`local-memory.service`), running the Hindsight FastAPI memory server served by `hindsight-api` on port `8888`. It provides long-term temporal, semantic, and entity-graph memory for local agents.

Hindsight has been split out from the default agent wrapper scripts (like `hermes-ctl`) to operate as a central, dedicated local microservice, offloading its processing workloads and aligning with the standalone local inference design.

- **Source Code**: [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)
- **Control Wrapper**: [assistants/local-memory.sh](file:///home/wuxxin/agent-shared/code/agents-shared/assistants/local-memory.sh)

---

## Architectural Interconnection

Hindsight functions as an agentic memory hub, coordinating with the other standalone services managed by `local-inference.sh`. It delegates heavy tasks (like embedding generation, chat reasoning, and re-ranking) to these external dedicated servers via the central `local-router` (port `51080`):

```mermaid
graph TD
    Agent[Agent Client e.g. Hermes / ZeroClaw] -->|Recall / Retain / Reflect| Memory[Local-Memory Port 8888]
    Memory -->|LLM / Embedding / Reranking Requests| Router[Local-Router Port 51080]
    Router -->|Completions| Chat[Local-Chat Port 50080]
    Router -->|Embeddings| Embed[Local-Embedding Port 50082]
    Router -->|Rerank| Rerank[Local-Rerank Port 50086]
    Memory -->|Semantic & Vector Storage| Postgres[(PostgreSQL Port 5432)]
```

In `local_external` mode, the Hindsight service itself remains lightweight: it offloads vector calculations to PostgreSQL via `pgvector` and `pgroonga`, and redirects machine-learning queries to the router, avoiding loading heavy model weights (like PyTorch or HuggingFace transformers) within its own Python virtual environment.

---

## Installation & Arch Linux Dependencies

Hindsight requires PostgreSQL with the `pgvector` and `pgroonga` extensions. On Arch Linux, these must be installed via Pacman / AUR.

### 1. Install System and AUR Packages

Run the following commands to install PostgreSQL and its required vector and full-text search extensions:

```bash
# Install PostgreSQL and the vector extension from Arch extra repos
sudo pacman -S postgresql pgvector

# Install the Groonga full-text search extension from AUR
yay -S pgroonga
```

### 2. Configure PostgreSQL User and Database

To set up the Hindsight database and enable the required extensions:

1. Log in as the `postgres` administrator system user:
   ```bash
   sudo -u postgres -i
   ```
2. Create a new PostgreSQL database role for the service (e.g., `hindsight`):
   ```bash
   createuser --interactive --pwprompt
   # Enter name of role to add: hindsight
   # Shall the new role be a superuser? no
   # Shall the new role be allowed to create databases? no
   # Shall the new role be allowed to create more new roles? no
   ```
3. Create the database owned by the new user:
   ```bash
   createdb -O hindsight hindsight_db
   ```
4. Connect to the database and register both extensions:
   ```bash
   psql -d hindsight_db -c "CREATE EXTENSION IF NOT EXISTS pgvector;"
   psql -d hindsight_db -c "CREATE EXTENSION IF NOT EXISTS pgroonga;"
   ```
5. Exit back to your user account:
   ```bash
   exit
   ```

### 3. Verify Database Setup

You can check if the database extensions are properly configured and loaded by running:
```bash
psql -U hindsight -d hindsight_db -h localhost -c "\dx"
```
Both `pgvector` and `pgroonga` should be listed in the output table.

---

## Service Installation

Install the virtual environment and default configuration files:

```bash
./local-memory.sh install
```

This subcommand:
1. Recreates a clean Python virtual environment at `~/.local/share/local-memory/venv` using `uv`.
2. Bypasses the `litellm` version constraint on Python 3.14+ by enforcing a target dependency resolution of Python 3.12 (`--python-version 3.12` during `uv pip install`).
3. Installs `hindsight-client` and `hindsight-api-slim` (which avoids downloading gigabytes of machine learning libraries).
4. Creates a default service configuration file at `~/.config/systemd/user/local-memory.env`.
5. Writes and registers `local-memory.service` in systemd.

To uninstall and clean up (which completely removes the virtual environment):
```bash
./local-memory.sh uninstall
```

---

## Configuration

The service is configured in:
- `~/.config/systemd/user/local-memory.env`

Default configuration values:
```env
# Service Configuration
LMEM_PORT=8888
LMEM_HOST=127.0.0.1
LMEM_SERVICE_CMD="%h/.local/share/local-memory/venv/bin/hindsight-api"
LMEM_SERVICE_ARGS="--port 8888 --host 127.0.0.1"
LMEM_SIDECARS=""

# Hindsight daemon configuration
HINDSIGHT_API_RUN_MIGRATIONS_ON_STARTUP="true"
HINDSIGHT_API_WORKER_ENABLED="true"
HINDSIGHT_API_MCP_ENABLED="true"

# Hindsight Chat Config (Redirected to Router)
HINDSIGHT_API_LLM_PROVIDER=openai
HINDSIGHT_API_LLM_API_KEY="unused"
HINDSIGHT_API_LLM_BASE_URL="http://localhost:51080/v1"
HINDSIGHT_API_LLM_MODEL="qwen3"
HINDSIGHT_API_LLM_EXTRA_BODY='{"chat_template_kwargs": {"enable_thinking": false}}'

# Hindsight Embeddings Config (Redirected to Router)
HINDSIGHT_API_EMBEDDINGS_PROVIDER=openai
HINDSIGHT_API_EMBEDDINGS_OPENAI_API_KEY="unused"
HINDSIGHT_API_EMBEDDINGS_OPENAI_BASE_URL="http://localhost:51080/v1"
HINDSIGHT_API_EMBEDDINGS_OPENAI_MODEL="qwen3-embedding"

# Hindsight Rerank Config (Redirected to Router)
HINDSIGHT_API_RERANKER_PROVIDER=cohere
HINDSIGHT_API_RERANKER_COHERE_API_KEY="unused"
HINDSIGHT_API_RERANKER_COHERE_BASE_URL="http://localhost:51080/v1"
HINDSIGHT_API_RERANKER_COHERE_MODEL="qwen3-reranker"

# Hindsight Database Config (Update with your DB password)
HINDSIGHT_API_DATABASE_BACKEND=postgresql
HINDSIGHT_API_VECTOR_EXTENSION=pgvector
HINDSIGHT_API_TEXT_SEARCH_EXTENSION=pgroonga
HINDSIGHT_API_DATABASE_URL="postgresql://hindsight:YOUR_PASSWORD@localhost:5432/hindsight_db"
```

---

## Usage Commands

```bash
# Start/Stop/Restart the service
./local-memory.sh start
./local-memory.sh stop
./local-memory.sh restart

# Check runtime status
./local-memory.sh status

# Tail service logs
./local-memory.sh logs -f

# Edit service environment configuration and auto-restart
./local-memory.sh edit

# Display service file, environment file, and transient execution command
./local-memory.sh cat

# Run API validation health check
./local-memory.sh test

# Run Hindsight as a transient systemd user service or foreground daemon
./local-memory.sh exec [--env KEY=VALUE]* [-- custom-args...]

# Run a custom command inside the service environment (transient/foreground)
./local-memory.sh run [--env KEY=VALUE]* <command> [args...]

# Spawn an interactive shell inside the service environment (transient/foreground)
./local-memory.sh shell [--env KEY=VALUE]*
```

### In-Memory Environment Overrides

`exec`, `run`, and `shell` support transient overrides via `--env KEY=VALUE` which are passed directly to systemd-run or local foreground shells without touching your disk configurations.

---

## Verification & Troubleshooting

You can verify that the service is running and properly initialized:
```bash
./local-memory.sh test
```

If it fails to start or connection times out, check the service log file:
```bash
./local-memory.sh logs -n 50
```

Common issues:
- **`ValueError: LLM API key is required`**: Ensure `HINDSIGHT_API_LLM_API_KEY` is not blank (use `"unused"` for local routing backends).
- **`Rolle »hindsight« existiert nicht` or DB connection failure**: Verify the database role and password match your configuration in `HINDSIGHT_API_DATABASE_URL`. Ensure PostgreSQL service is active (`systemctl status postgresql.service`).
- **`ValueError: Unknown reranker provider: none`**: Ensure `HINDSIGHT_API_RERANKER_PROVIDER` is set to a supported remote engine like `cohere` or `tei` pointing to local-router (plain `none` is not allowed by Hindsight).
