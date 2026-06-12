# Coding Agent and Coding Agent LLM-Proxy Support 

This report details the support **OpenCode** (autonomous coding agent CLI / LLM API proxy), other **CLI Coding Agents** (such as Claude Code, Aider, Codex CLI, etc.), and **Antigravity** (Google Cloud Code Assist API), as CLI tools and/or LLM adapters across the various assistant source codes located in `scratch/`.

1. **`antigravity` (LLM Provider via Google Cloud Code Assist API)**
2. **`opencode` (LLM Provider via internal Inference Path)**: Using a local/configured OpenCode instance (e.g. spawning or communicating with `opencode serve` via the OpenCode SDK) as a local LLM proxy/router. The assistant communicates with the local OpenCode daemon's inference server.
3. **`opencode` (Coding Agent)**: Spawning the `opencode` CLI tool as a subprocess (e.g., using `opencode run '<instruction>'` or wrapping interactive sessions in tmux) to delegate entire coding, refactoring, or review tasks to OpenCode acting as a worker/subagent.
4. **Other CLI Coding Agent Support**

---

## Support Matrix

| Assistant | Antigravity (LLM) | OpenCode (LLM-Proxy) | OpenCode Coding Agent | Other CLI Coding Agents | Description |
| :--- | :---: | :---: | :---: | :--- | :--- |
| **IronClaw** | No | No | No | None | No integrations found in source code. |
| **ZeroClaw** | No | No | **Yes** (Tool) | None | Delegates to `opencode run` CLI. |
| **Hermes-Agent** | No | No | **Yes** (Skill) | Claude Code, Codex | Has agent skills. |
| **NanoBot** | No | No | No | None | No integrations found in source code. |
| **LibreFang** | No | No | No | Claude Code, Aider, Qwen Code, Gemini CLI, Codex CLI | Implements CLI coding agents as native LLM drivers (`LlmDriver`) by spawning subprocesses. |
| **Moltis** | No | No | **Yes** (Tmux) | Alibaba Coding Plan, Claude Code, Codex, Pi AI Agent | Integrates external coding agents as tmux/PTY-based runtimes under `external-agents`. |
| **PicoClaw** | **Yes** | No | No (Test only) | Claude Code, Codex, GitHub Copilot | Wraps coding CLI execution inside provider classes under the `pkg/providers/cli/` module. |
| **NanoClaw** | No | **Yes** (Local SDK) | **Yes** (Local SDK Provider) | None | Communicates with `opencode serve` via `@opencode-ai/sdk` (add-opencode skill). |

---

## 1. Antigravity (LLM Provider)

### PicoClaw
PicoClaw is the only assistant containing a first-class LLM adapter implementation for the Antigravity API:
- **Implementation**: [scratch/picoclaw/pkg/providers/oauth/antigravity_provider.go](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/picoclaw/pkg/providers/oauth/antigravity_provider.go)
- **Tests**: [scratch/picoclaw/pkg/providers/oauth/antigravity_provider_test.go](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/picoclaw/pkg/providers/oauth/antigravity_provider_test.go)
- **Configuration URL**: `https://cloudcode-pa.googleapis.com` (Cloud Code Assist API)
- **Mechanism**:
  - The provider loads stored OAuth credentials under the name `google-antigravity`.
  - Wraps chat requests in a companion envelope with `project`, `model`, `request`, `requestType = "agent"`, `userAgent = "antigravity"`, and a generated `requestId`.
  - Connects to the SSE streaming endpoint `v1internal:streamGenerateContent` to parse responses.
  - Exposes models with prefixes like `google-antigravity/` or `antigravity/` (default model is `gemini-3-flash`).

## 2. OpenCode (LLM Provider)
Under this pattern, the assistant communicates with a local OpenCode instance/daemon rather than querying online APIs directly:

* **NanoClaw**:
  - **Implementation**: Enabled via the optional `/add-opencode` skill in [scratch/nanoclaw/.claude/skills/add-opencode/SKILL.md](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/nanoclaw/.claude/skills/add-opencode/SKILL.md).
  - **Mechanism**:
    - Installs the `@opencode-ai/sdk` and `opencode-ai` CLI in the container.
    - Routes requests to the local OpenCode runtime via `AGENT_PROVIDER=opencode` using the SDK to talk to `opencode serve`.
    - Coordinates environment variables such as `OPENCODE_PROVIDER=opencode` (Zen provider id inside the OpenCode config) and `OPENCODE_MODEL`.

## 3. OpenCode (Coding Agent)
Under this pattern, the assistant runs the `opencode` binary as a tool/sub-process to perform autonomous coding tasks:

* **ZeroClaw**:
  - **Implementation**: [scratch/zeroclaw/crates/zeroclaw-config/src/schema.rs](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/zeroclaw/crates/zeroclaw-config/src/schema.rs#L7081-L7100)
  - Configures the `opencode_cli` tool. When enabled, ZeroClaw delegates complex tasks to the `opencode run` CLI subprocess.
* **Hermes-Agent**:
  - Includes a bundled skill to delegate tasks to the `opencode` CLI (using `opencode run` for one-shot tasks, or running the interactive TUI shell with a pty).
* **Moltis**:
  - **Implementation**: [scratch/moltis/crates/external-agents/src/runtimes/opencode.rs](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/moltis/crates/external-agents/src/runtimes/opencode.rs)
  - Implements an external agent runtime for `opencode`. If configured, it spins up an interactive OpenCode session inside tmux, allowing Moltis to orchestrate it as a sub-worker.
  - Also includes a dedicated skill ([scratch/moltis/crates/skills/src/assets/autonomous-ai-agents/opencode/SKILL.md](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/moltis/crates/skills/src/assets/autonomous-ai-agents/opencode/SKILL.md)) containing tools for running `opencode run` and managing sessions.

## 4. Other CLI Coding Agent Support Details

### IronClaw
IronClaw implements an internal subagent loop with general, explorer, coder, and planner flavors, but does not feature integrations to spawn or orchestrate external CLI coding agents (e.g. Aider, Claude Code, or Codex).

### LibreFang
In LibreFang, coding agents are resolved directly as native LLM drivers (`LlmDriver`) by spawning subprocesses:
* **Claude Code CLI** (`claude`): [scratch/librefang/crates/librefang-llm-drivers/src/drivers/claude_code.rs](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/librefang/crates/librefang-llm-drivers/src/drivers/claude_code.rs)
  - Spawns the CLI in print mode (`-p`). Integrates tools via a dynamically written local JSON config file that maps to LibreFang's HTTP `/mcp` server.
* **Aider CLI** (`aider`): [scratch/librefang/crates/librefang-llm-drivers/src/drivers/aider.rs](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/librefang/crates/librefang-llm-drivers/src/drivers/aider.rs)
  - Spawns Aider in non-interactive mode using the `--message` and `--yes-always` flags.
* **Qwen Code CLI** (`qwen`): [scratch/librefang/crates/librefang-llm-drivers/src/drivers/qwen_code.rs](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/librefang/crates/librefang-llm-drivers/src/drivers/qwen_code.rs)
* **Gemini CLI** (`gemini`): [scratch/librefang/crates/librefang-llm-drivers/src/drivers/gemini_cli.rs](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/librefang/crates/librefang-llm-drivers/src/drivers/gemini_cli.rs)
* **Codex CLI** (`codex`): [scratch/librefang/crates/librefang-llm-drivers/src/drivers/codex_cli.rs](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/librefang/crates/librefang-llm-drivers/src/drivers/codex_cli.rs)

A detailed audit of LibreFang (`scratch/librefang/`) confirms that it does not contain any native or first-class integration for either Antigravity or OpenCode (including Zen/Go, local inference, or agent runtimes):
- **Provider Registry**: The LLM drivers registry in [scratch/librefang/crates/librefang-llm-drivers/src/drivers/mod.rs](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/librefang/crates/librefang-llm-drivers/src/drivers/mod.rs) contains 47 hardcoded providers (such as Anthropic, Gemini, OpenAI, Groq, Bedrock, and various coding CLI formats like `claude-code` and `qwen-code`), but none match `antigravity` or `opencode` patterns.
- **Skills & Runtimes**: There are no references to OpenCode or Antigravity under `crates/librefang-skills/` or `examples/`.
- **Generic Fallback**: Like most multi-provider agents, LibreFang can only connect to these services if configured manually using its generic `openai` driver or `custom` endpoint URLs pointing to the appropriate server base URLs.

### Moltis
Moltis implements coding agents as external tmux/PTY-based runtimes under the `external-agents` crate:
* **Alibaba Coding Plan** (`acp`): [scratch/moltis/crates/external-agents/src/runtimes/acp.rs](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/moltis/crates/external-agents/src/runtimes/acp.rs)
* **Claude Code CLI** (`claude-code`): [scratch/moltis/crates/external-agents/src/runtimes/claude_code.rs](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/moltis/crates/external-agents/src/runtimes/claude_code.rs)
* **Codex CLI** (`codex`): [scratch/moltis/crates/external-agents/src/runtimes/codex.rs](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/moltis/crates/external-agents/src/runtimes/codex.rs)
* **OpenCode CLI** (`opencode`): [scratch/moltis/crates/external-agents/src/runtimes/opencode.rs](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/moltis/crates/external-agents/src/runtimes/opencode.rs)
* **Pi AI Agent** (`pi-agent`): [scratch/moltis/crates/external-agents/src/runtimes/pi_agent.rs](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/moltis/crates/external-agents/src/runtimes/pi_agent.rs)

### PicoClaw
PicoClaw wraps coding CLI execution inside provider classes under the `pkg/providers/cli/` module:
* **Claude Code CLI** (`claude`): [scratch/picoclaw/pkg/providers/cli/claude_cli_provider.go](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/picoclaw/pkg/providers/cli/claude_cli_provider.go)
* **Codex CLI** (`codex`): [scratch/picoclaw/pkg/providers/cli/codex_cli_provider.go](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/picoclaw/pkg/providers/cli/codex_cli_provider.go)
* **GitHub Copilot CLI** (`copilot`): [scratch/picoclaw/pkg/providers/cli/github_copilot_provider.go](file:///home/wuxxin/agent-shared/code/agents-shared/scratch/picoclaw/pkg/providers/cli/github_copilot_provider.go)

### Hermes-Agent
Hermes-Agent features bundled skills to delegate to external coding CLI installations:
* **Claude Code** (`claude-code`)
* **Codex CLI** (`codex`)
* **OpenCode CLI** (`opencode`)

---

## 📋 Instruction Guide: Recreating this Analysis

If you do links to the source code , point relative to `scratch/` so `picoclaw/pkg/providers/cli/claude_cli_provider.go`.
If you research for opencode (agent or llm-proxy support), ignore the opencode-zen (a Remote Inference API and Model by opencode) for this analysis.
To recreate or update this document, read whole document, and then follow these research steps


### step 0: checkout and pull / update all assistant sources to `scratch/`

as scratch can be full of other stuff, grep -R and other commands should only look at dirs with the checked out asssitant sources.

### Step 1: Scan for Antigravity Integrations
Search for references to `antigravity` or `cloudcode-pa` to identify any assistant implementing custom adapters or LLM provider connections:
```bash
grep -rn -i "antigravity" scratch/
```

### Step 2: Scan for OpenCode Integrations 
Search for references to `opencode` or `@opencode-ai` to see if the assistants query it as a local API or run it as a subprocess tool:
```bash
grep -rn -i "opencode" scratch/
```

### Step 3: Identify External Coding Agent References
Search for references to standard external coding agents (Aider, Claude Code, GitHub Copilot, Codex, Pi AI Agent, etc.) inside the respective repository subfolders:
```bash
# Look for aider or Claude Code integrations for each assistant source 
grep -rn -i "aider" scratch/
grep -rn -i "claude" scratch/ --include="*.rs" --include="*.go" --include="*.ts"
```

### Step 4: Verify Provider Registries and Skill Locations
Check the directories where providers and skills are declared:
- **PicoClaw**: Look in `pkg/providers/`
- **LibreFang**: Look in `crates/librefang-llm-drivers/src/drivers/`
- **Moltis**: Look in `crates/external-agents/src/runtimes/`
- **NanoClaw & Hermes-Agent**: Look in `.claude/skills/` or `skills/`
- **IronClaw**:
- **ZeroClaw**

### Step 5: Update the Matrix & Details
Based on the results, update the Support Matrix table and sections 1-4 with implementation details, paths, and relevant configuration settings.

### Step 6: Update the "Recreation Instruction Guide"

Update the instructions by lessons learned from this update.
