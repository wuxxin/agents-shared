# Oh-my-PI (OMP) Orchestration Template

Complete configuration template for Oh-my-PI (`omp`) with multi-agent orchestration, Arbor graph intelligence, OpenAdapt browser automation, local OpenAI-compatible inference routing (`local-router`), and native Hindsight long-term memory.

---

## Setup, Installation, and Teardown

### 1. Create and Provision Sandbox

Run `sandbox-ctl` to provision the sandbox environment and create the `omp` binary launcher in `~/.local/bin`:

```bash
sandbox-ctl install omp --no-start --new-config-from \
  ~/agent-shared/code/agents-shared/sandbox-templates/omp/omp.env
```

Running `sandbox-ctl install` automatically recursively copies `sandbox-templates/omp/omp/*` into `$HOME/.omp/` without deleting existing files, provisions CLI tools (`openadapt`, `arbor-agent`), and runs `update-memory-banks.sh` via `LAUNCHER_INSTALL_CMDS`.

### 2. Start Oh-my-PI

```bash
omp
```

---

## Template Directory Structure (`sandbox-templates/omp/omp/`)

The template directory mirrors the `$HOME/.omp/` structure:

```
sandbox-templates/omp/omp/
└── agent/
    ├── agents/                 # Custom subagents (*.md)
    ├── commands/               # Custom slash commands & macros
    ├── config.yml              # OMP main engine configuration
    ├── extensions/             # OMP plugins & extension modules
    ├── hindsight-bankconfig/   # Hindsight memory bank JSON configs
    ├── rules/                  # Time-Traveling Stream Rules (TTSR)
    ├── skills/                 # Copied skills (arbor, caveman, hindsight, openadapt, etc.)
    ├── tools/                  # Custom agent tools
    └── update-memory-banks.sh  # Smart Hindsight memory bank update script
```

---

## Configured Local Services & Environment

| Service | Protocol / Endpoint | Port | Environment Variable / Setting | Purpose |
|---|---|:---:|---|---|
| **Local Router** | OpenAI Compatible (`http://localhost:51080/v1`) | `51080` | `OPENAI_BASE_URL` in `omp.env` | Unified routing for chat completions, embeddings, reranking, transcription, speech, and image generation. |
| **Hindsight Memory** | REST API (`http://localhost:8888`) | `8888` | `HINDSIGHT_API_URL` & `hindsight.apiUrl` in `config.yml` | Long-term vector memory recall, turn retention, and mental model reflection. |
| **Speech-to-Text** | OpenAI Audio (`http://localhost:50090/v1`) | `50090` | `stt.enabled` in `config.yml` | Local speech-to-text audio transcription. |
| **Text-to-Speech** | Local Neural Kokoro / OpenAI (`http://localhost:50095/v1`) | `50095` | `providers.tts` in `config.yml` | Speech synthesis for `omp say` and voice output. |
| **Image Generation** | OpenAI Images (`http://localhost:50100/v1`) | `50100` | `generate_image.enabled` in `config.yml` | Local image generation. |

---

## MCP Servers

| Server Name | Type | Command / Runner | Package / Source | Purpose |
|---|---|---|---|---|
| `sequential-thinking` | local | `bunx @modelcontextprotocol/server-sequential-thinking` | `@modelcontextprotocol/server-sequential-thinking` | Dynamic reflective reasoning chain with thought revision and branching. |
| `arbor` | local | `arbor mcp` | `arbor-agent` (PyPI / `uv tool`) | Graph-native AST code intelligence, dependency traversal, and hypothesis checks (~700 - 900 tokens). |
| `hindsight` | local | `bunx hindsight-mcp` | `hindsight-mcp` | Explicit tool-level long-term memory queries (`hindsight_recall`, `hindsight_retain`, `hindsight_reflect`). |

---

## Copied & Installed Skills

Skills located in `sandbox-templates/omp/omp/agent/skills/` are recursively copied into `~/.omp/agent/skills/`:

| Skill Name | Purpose | Source / Command |
|---|---|---|
| **`arbor`** | AST code intelligence and graph traversal without full RAG scans. | `arbor mcp` |
| **`caveman`** | Ultra-concise, low-overhead reasoning and output formatting. | `oh-my-opencode-slim` / local |
| **`hindsight`** | Long-term memory query patterns and retention strategies. | `@toady00/opencode-hindsight` |
| **`hindsight-api`** | Direct REST API interaction with Hindsight server (`http://localhost:8888`). | Hindsight REST API |
| **`openadapt`** | Headless DOM rendering, visual web element verification, and UI automation. | `openadapt[browser,capture]` |
| **`sequential-thinking`** | Step-by-step reasoning with hypothesis branching and backtracking. | `@modelcontextprotocol/server-sequential-thinking` |

---

## Hindsight Bank Configuration & Auto-Seeding

Hindsight long-term memory is natively integrated into OMP's core engine:

- **Auto-Seeding**: Enabled via `hindsight.mentalModelAutoSeed: true`. OMP automatically creates built-in seed mental models (`user-preferences`, `project-conventions`, `project-decisions`) on the server at session start.
- **Scoping**: `per-project-tagged` ensures global memories and project-specific memories are seamlessly merged on recall.
- **Smart Idempotent Updates**: `update-memory-banks.sh` inspects existing bank configs and mental models via `GET /v1/default/banks/<bank_id>/config` and `GET /v1/default/banks/<bank_id>/mental-models`. It issues `PATCH`/`POST`/`DELETE` requests **only when local definitions differ from server state**. Pass `--prune` to remove leftover mental models on the server.
