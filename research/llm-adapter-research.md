# Research Report: LLM Adapter & Coding Agent Support

This report details the support for **Antigravity** (Google Cloud Code Assist API), **OpenCode** (autonomous coding agent CLI / API proxy), and other **CLI Coding Agents** (such as Claude Code, Aider, Codex CLI, etc.) as LLM adapters or CLI tools across the various assistant source codes located in `scratch/`.

---

## The Three OpenCode Integration Patterns

To understand OpenCode integration, we must distinguish between three distinct patterns in the assistant source codes:

1. **`opencode-zen` (Model Provider)**: Direct connection to the online OpenCode Zen/Go API endpoints (`https://opencode.ai/zen/v1` or `/go/v1`) using an API key (`OPENCODE_ZEN_API_KEY` / `OPENCODE_GO_API_KEY`). The assistant queries this online service for chat completions just like any standard LLM provider (OpenAI, Anthropic).
2. **`opencode` (LLM Provider via Inference Path)**: Using a local/configured OpenCode instance (e.g. spawning or communicating with `opencode serve` via the OpenCode SDK) as a local LLM proxy/router. The assistant communicates with the local OpenCode daemon's inference server.
3. **`opencode` (Coding Agent)**: Spawning the `opencode` CLI tool as a subprocess (e.g., using `opencode run '<instruction>'` or wrapping interactive sessions in tmux) to delegate entire coding, refactoring, or review tasks to OpenCode acting as a worker/subagent.

---

## Support Matrix

| Assistant | Antigravity (LLM) | OpenCode Support | Other CLI Coding Agents | Description |
| :--- | :---: | :---: | :--- | :--- |
| **PicoClaw** | **Yes** (Native LLM) | No (Test only) | Claude Code, Codex, GitHub Copilot | Wraps coding CLI execution inside provider classes under the `pkg/providers/cli/` module. |
| **ZeroClaw** | No (Policy only) | **Yes** (Zen Provider & Tool) | None | Supports `opencode-zen` models and delegates to `opencode run` CLI. |
| **Hermes-Agent** | No | **Yes** (Zen Provider & Skill) | Claude Code, Codex | Supports `opencode-zen/go` models and has agent skills. |
| **Moltis** | No | **Yes** (Zen Provider & Tmux) | Alibaba Coding Plan, Claude Code, Codex, Pi AI Agent | Integrates external coding agents as tmux/PTY-based runtimes under `external-agents`. |
| **NanoClaw** | No | **Yes** (Local SDK Provider) | None | Communicates with `opencode serve` via `@opencode-ai/sdk` (add-opencode skill). |
| **LibreFang** | No | No | Claude Code, Aider, Qwen Code, Gemini CLI, Codex CLI | Implements CLI coding agents as native LLM drivers (`LlmDriver`) by spawning subprocesses. |
| **NanoBot** | No | No | None | No integrations found in source code. |

---

## 1. Antigravity Support Details

### PicoClaw
PicoClaw is the only assistant containing a first-class LLM adapter implementation for the Antigravity API:
- **Implementation**: [antigravity_provider.go](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/picoclaw/pkg/providers/oauth/antigravity_provider.go)
- **Tests**: [antigravity_provider_test.go](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/picoclaw/pkg/providers/oauth/antigravity_provider_test.go)
- **Configuration URL**: `https://cloudcode-pa.googleapis.com` (Cloud Code Assist API)
- **Mechanism**:
  - The provider loads stored OAuth credentials under the name `google-antigravity`.
  - Wraps chat requests in a companion envelope with `project`, `model`, `request`, `requestType = "agent"`, `userAgent = "antigravity"`, and a generated `requestId`.
  - Connects to the SSE streaming endpoint `v1internal:streamGenerateContent` to parse responses.
  - Exposes models with prefixes like `google-antigravity/` or `antigravity/` (default model is `gemini-3-flash`).

### ZeroClaw
ZeroClaw does not have an LLM adapter for Antigravity, but its security policy references the binary path `/usr/bin/antigravity` under `allowed_commands` to control command execution sandboxing:
- **File**: [policy.rs](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/zeroclaw/crates/zeroclaw-config/src/policy.rs#L2927)

### OpenCode (Self-references)
OpenCode's own repository (`scratch/opencode/`) lists `opencode-antigravity-auth` and `opencode-google-antigravity-auth` plugins in its ecosystem docs to allow users to authenticate and leverage Antigravity's free companion models instead of paying for API credits:
- **File**: [ecosystem.mdx](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/opencode/packages/web/src/content/docs/ecosystem.mdx#L25-L27)
- OpenCode's UI also includes a launcher button to open current sessions directly in the Antigravity IDE.

---

## 2. OpenCode Support Details by Pattern

### A. OpenCode-Zen / Go (Model Provider)
Under this pattern, the assistant connects to OpenCode's hosted cloud endpoint to perform inference using an API key:

* **Hermes-Agent**:
  - **Implementation**: [__init__.py](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/hermes-agent/plugins/model-providers/opencode-zen/__init__.py)
  - Configures model providers `opencode-zen` (base URL `https://opencode.ai/zen/v1`) and `opencode-go` (base URL `https://opencode.ai/zen/go/v1`).
  - Expects environment variables `OPENCODE_ZEN_API_KEY` and `OPENCODE_GO_API_KEY`.
* **ZeroClaw**:
  - **Implementation**: [providers.rs](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/zeroclaw/crates/zeroclaw-config/src/providers.rs#L233)
  - Supports `opencode` (with `opencode-zen` and `opencode-go` aliases, folded under the `opencode` provider).
  - Migration aliases are resolved in [v2.rs](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/zeroclaw/crates/zeroclaw-config/src/schema/v2.rs#L607-L636).
* **Moltis**:
  - **Implementation**: [known_providers.rs](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/moltis/crates/provider-setup/src/known_providers.rs#L261)
  - Registers `opencode-zen` as a known provider pointing to `https://opencode.ai/zen/v1`.

---

### B. OpenCode (LLM Provider via Local Inference)
Under this pattern, the assistant communicates with a local OpenCode instance/daemon rather than querying online APIs directly:

* **NanoClaw**:
  - **Implementation**: Enabled via the optional `/add-opencode` skill in [.claude/skills/add-opencode/SKILL.md](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/nanoclaw/.claude/skills/add-opencode/SKILL.md).
  - **Mechanism**:
    - Installs the `@opencode-ai/sdk` and `opencode-ai` CLI in the container.
    - Routes requests to the local OpenCode runtime via `AGENT_PROVIDER=opencode` using the SDK to talk to `opencode serve`.
    - Coordinates environment variables such as `OPENCODE_PROVIDER=opencode` (Zen provider id inside the OpenCode config) and `OPENCODE_MODEL`.

---

### C. OpenCode (Coding Agent)
Under this pattern, the assistant runs the `opencode` binary as a tool/sub-process to perform autonomous coding tasks:

* **ZeroClaw**:
  - **Implementation**: [schema.rs](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/zeroclaw/crates/zeroclaw-config/src/schema.rs#L7081-L7100)
  - Configures the `opencode_cli` tool. When enabled, ZeroClaw delegates complex tasks to the `opencode run` CLI subprocess.
* **Hermes-Agent**:
  - Includes a bundled skill to delegate tasks to the `opencode` CLI (using `opencode run` for one-shot tasks, or running the interactive TUI shell with a pty).
* **Moltis**:
  - **Implementation**: [opencode.rs](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/moltis/crates/external-agents/src/runtimes/opencode.rs)
  - Implements an external agent runtime for `opencode`. If configured, it spins up an interactive OpenCode session inside tmux, allowing Moltis to orchestrate it as a sub-worker.
  - Also includes a dedicated skill ([SKILL.md](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/moltis/crates/skills/src/assets/autonomous-ai-agents/opencode/SKILL.md)) containing tools for running `opencode run` and managing sessions.

---

## 3. Other CLI Coding Agent Support Details

### LibreFang
In LibreFang, coding agents are resolved directly as native LLM drivers (`LlmDriver`) by spawning subprocesses:
* **Claude Code CLI** (`claude`): [claude_code.rs](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/librefang/crates/librefang-llm-drivers/src/drivers/claude_code.rs)
  - Spawns the CLI in print mode (`-p`). Integrates tools via a dynamically written local JSON config file that maps to LibreFang's HTTP `/mcp` server.
* **Aider CLI** (`aider`): [aider.rs](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/librefang/crates/librefang-llm-drivers/src/drivers/aider.rs)
  - Spawns Aider in non-interactive mode using the `--message` and `--yes-always` flags.
* **Qwen Code CLI** (`qwen`): [qwen_code.rs](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/librefang/crates/librefang-llm-drivers/src/drivers/qwen_code.rs)
* **Gemini CLI** (`gemini`): [gemini_cli.rs](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/librefang/crates/librefang-llm-drivers/src/drivers/gemini_cli.rs)
* **Codex CLI** (`codex`): [codex_cli.rs](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/librefang/crates/librefang-llm-drivers/src/drivers/codex_cli.rs)

### Moltis
Moltis implements coding agents as external tmux/PTY-based runtimes under the `external-agents` crate:
* **Alibaba Coding Plan** (`acp`): [acp.rs](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/moltis/crates/external-agents/src/runtimes/acp.rs)
* **Claude Code CLI** (`claude-code`): [claude_code.rs](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/moltis/crates/external-agents/src/runtimes/claude_code.rs)
* **Codex CLI** (`codex`): [codex.rs](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/moltis/crates/external-agents/src/runtimes/codex.rs)
* **OpenCode CLI** (`opencode`): [opencode.rs](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/moltis/crates/external-agents/src/runtimes/opencode.rs)
* **Pi AI Agent** (`pi-agent`): [pi_agent.rs](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/moltis/crates/external-agents/src/runtimes/pi_agent.rs)

### PicoClaw
PicoClaw wraps coding CLI execution inside provider classes under the `pkg/providers/cli/` module:
* **Claude Code CLI** (`claude`): [claude_cli_provider.go](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/picoclaw/pkg/providers/cli/claude_cli_provider.go)
* **Codex CLI** (`codex`): [codex_cli_provider.go](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/picoclaw/pkg/providers/cli/codex_cli_provider.go)
* **GitHub Copilot CLI** (`copilot`): [github_copilot_provider.go](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/picoclaw/pkg/providers/cli/github_copilot_provider.go)

### Hermes-Agent
Hermes-Agent features bundled skills to delegate to external coding CLI installations:
* **Claude Code** (`claude-code`)
* **Codex CLI** (`codex`)
* **OpenCode CLI** (`opencode`)

---

## 4. LibreFang LLM Drivers Provider Registry Audit

A detailed audit of LibreFang (`scratch/librefang/`) confirms that it does not contain any native or first-class integration for either Antigravity or OpenCode (including Zen/Go, local inference, or agent runtimes):
- **Provider Registry**: The LLM drivers registry in [mod.rs](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/librefang/crates/librefang-llm-drivers/src/drivers/mod.rs) contains 47 hardcoded providers (such as Anthropic, Gemini, OpenAI, Groq, Bedrock, and various coding CLI formats like `claude-code` and `qwen-code`), but none match `antigravity` or `opencode` patterns.
- **Skills & Runtimes**: There are no references to OpenCode or Antigravity under `crates/librefang-skills/` or `examples/`.
- **Generic Fallback**: Like most multi-provider agents, LibreFang can only connect to these services if configured manually using its generic `openai` driver or `custom` endpoint URLs pointing to the appropriate server base URLs.
