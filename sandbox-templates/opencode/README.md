# OpenCode Agent Orchestration Template

Complete configuration template for OpenCode with `oh-my-opencode-slim`, multi-agent orchestration, Arbor graph intelligence, OpenAdapt browser automation, Agent-to-Agent (A2A) protocol bridge, and per-agent Hindsight long-term memory.

---

## Setup, Installation, and Teardown

### 1. Create and Provision Sandbox

Run `sandbox-ctl` to provision the sandbox environment and create the `opencode` binary launcher in `~/.local/bin`:

```bash
sandbox-ctl install opencode --no-start --new-config-from \
  ~/agent-shared/code/agents-shared/sandbox-templates/opencode/opencode.env
```

Running `sandbox-ctl install` automatically recreates all environment dependencies, CLI tools, and Bun packages via `LAUNCHER_INSTALL_CMDS`.

### 2. Provider Authentication (If Required)

First-time provider authentication:

```bash
opencode auth login --provider google-agy
opencode auth login --provider deepseek
opencode models --refresh
```

### 3. Start OpenCode

```bash
opencode
```

---

## Plugins and Tools

| Plugin | Package | Purpose |
|---|---|---|
| `oh-my-opencode-slim` | `oh-my-opencode-slim` | Multi-agent orchestration (`orchestrator`, `oracle`, `explorer`, `librarian`, `designer`, `fixer`). |
| `@toady00/opencode-hindsight` | `@toady00/opencode-hindsight` (git) | Per-agent Hindsight long-term memory. Each agent writes to its own bank (`opencode-orchestrator`, `opencode-oracle`, etc.) with project-tagged memories. Installed from `github:Toady00/opencode-hindsight#v0.2.2`. |
| `@anthonyhaussman/opencode-agy-auth` | `@anthonyhaussman/opencode-agy-auth` | Google AGY OAuth authentication for Claude + Gemini models. |
| `@slkiser/opencode-quota` | `@slkiser/opencode-quota` | Per-provider quota tracking, toast notifications, TUI status panels. |
| `opencode-handoff` | `opencode-handoff` | Session handoff with `/handoff` command. |
| --- | --- | --- |
| `openadapt` | `openadapt[browser]` (PyPI / `uv tool`) | Headless browser rendering, DOM inspection, and web action automation (~800 - 1,100 tokens). |
| `a2a` | `opencode-a2a` (PyPI / `uv tool`) | Agent-to-Agent protocol peer discovery and remote task delegation (sidecar on port `9090`). |

---

## MCP Servers

| Server Name | Type | Command / Runner | Package / Source | Purpose |
|---|---|---|---|---|
| `sequential-thinking` | local | `bunx @modelcontextprotocol/server-sequential-thinking` | `@modelcontextprotocol/server-sequential-thinking` | Dynamic reflective reasoning chain with thought revision and branching. |
| `arbor` | local | `arbor mcp` | `arbor-agent` (PyPI / `uv tool`) | Graph-native AST code intelligence, dependency traversal, and hypothesis checks (~700 - 900 tokens). |
| `hindsight` | local | `bunx hindsight-mcp` | `hindsight-mcp` | Explicit tool-level long-term memory queries (`hindsight_recall`, `hindsight_retain`, `hindsight_reflect`) across target mental models. |
| `websearch` | remote | Exa API | Built-in / Remote | Real-time web search for docs, error messages, bug reports. |
| `gh_grep` | remote | GitHub API | Built-in / Remote | Public GitHub code search. |

---

## Subagent Profit & Skill Assignment Matrix

Each subagent in `oh-my-opencode-slim.jsonc` is equipped with dedicated MCP tools, skills, and isolated memory banks:

| Agent Role | Model & Variant | Assigned MCP Servers | Assigned Skills | Memory Bank | Benefit & Profit |
|---|---|---|---|---|---|
| **`orchestrator`** | DeepSeek V4 Pro (`xhigh`) | `*` (All MCPs) | `*` (All skills) | `opencode-orchestrator` | Auto-recall/retain, session handoffs, global plan tracking, multi-bank memory queries. |
| **`oracle`** | DeepSeek V4 Pro (`xhigh`) | `sequential-thinking`, `arbor`, `websearch`, `gh_grep` | `simplify`, `arbor`, `hindsight` | `opencode-oracle` | Pristine architectural decision memory without noise, graph-native AST code intelligence. |
| **`librarian`** | DeepSeek V4 Flash (`low`) | `websearch`, `openadapt`, `context7`, `gh_grep` | `openadapt`, `hindsight` | `opencode-librarian` | Headless DOM rendering for JS-heavy web docs, persistent research index. |
| **`explorer`** | DeepSeek V4 Flash (`low`) | `arbor`, `gh_grep` | `arbor` | `opencode-explorer` | Fast dependency graph traversal and symbol relationship lookup. |
| **`designer`** | Gemini 3.6 Flash (`medium`) | `openadapt` | `openadapt`, `hindsight` | `opencode-designer` | Visual DOM inspection, layout rendering, design system rule retention. |
| **`fixer`** | DeepSeek V4 Pro (`xhigh`) | `arbor` | `arbor`, `hindsight` | `opencode-fixer` | Isolated bank for bug post-mortems, verified fix patterns, and diagnostic runbooks. |

---

## Per-Agent Memory Isolation & Bank Architecture

Memory isolation uses `@toady00/opencode-hindsight` (v0.2.2, installed from git). Each agent resolves its bank at tool-call time via `ToolContext.agent`, routing memories to the agent's own bank.

### Plugin Configuration

Global defaults in `opencode.json` apply to all agents (`applyMode: "opt-out"`):

```json
["@toady00/opencode-hindsight", {
  "hindsightApiUrl": "http://localhost:8888",
  "applyMode": "opt-out",
  "defaults": {
    "bankId": "opencode-orchestrator",
    "autoRetain": true,
    "autoRecall": true,
    "tags": ["source:opencode", "project:{project}", "agent:orchestrator"],
    "retainEveryNTurns": 10,
    "retainConversationExtras": false
  }
}]
```

### Per-Agent Bank Overrides

Each subagent overrides `bankId` to route to its own bank. Auto-recall and auto-retain are disabled for subagents (child sessions — only the orchestrator's root session gets automatic behavior). Manual tools (`hindsight_retain`, `hindsight_recall`, `hindsight_reflect`) work for all configured agents:

```json
"agent": {
  "oracle": {
    "options": {
      "hindsight": {
        "bankId": "opencode-oracle",
        "autoRetain": false, "autoRecall": false,
        "tags": ["source:opencode", "project:{project}", "agent:oracle"]
      }
    }
  },
  "fixer": { "options": { "hindsight": { "bankId": "opencode-fixer", "autoRetain": false, "autoRecall": false, "tags": ["source:opencode", "project:{project}", "agent:fixer"] } } },
  "librarian": { "options": { "hindsight": { "bankId": "opencode-librarian", "autoRetain": false, "autoRecall": false, "tags": ["source:opencode", "project:{project}", "agent:librarian"] } } },
  "explorer": { "options": { "hindsight": { "bankId": "opencode-explorer", "autoRetain": false, "autoRecall": false, "tags": ["source:opencode", "project:{project}", "agent:explorer"] } } },
  "designer": { "options": { "hindsight": { "bankId": "opencode-designer", "autoRetain": false, "autoRecall": false, "tags": ["source:opencode", "project:{project}", "agent:designer"] } } }
}
```

### Tag Template Variable Patch (`patch-hindsight-tags.js`)

The `patch-hindsight-tags.js` script runs idempotently post-install (`LAUNCHER_INSTALL_CMDS`). It patches `@toady00/opencode-hindsight` to expand `{project}`, `{gitProject}`, `{directory}`, and `{pwd}` template placeholders in `tags` dynamically at retention time (resolving to `path.basename(process.cwd())` even after directory shifts like `/move`).

### MCP Server Removal

The `hindsight-mcp` MCP server is **removed from subagents** to avoid tool name collisions with the plugin. Only the plugin's bank-aware tools (`hindsight_retain`, `hindsight_recall`, `hindsight_reflect`) are available.

### Auto-Recall Behavior

The orchestrator gets auto-recall at session start and compaction. Subagents (child sessions) call recall/retain explicitly when the orchestrator delegates work. The plugin's `sessionStartMentalModel` config can auto-inject a specific mental model at orchestrator session start.

### Tag Storage

Tags are stored at the memory level (not document level). Verify with:
```bash
curl -s http://localhost:8888/v1/default/banks/opencode-orchestrator/tags | jq
```

---

## Hindsight Bank Configuration Setup & Apply Script

Each bank in `sandbox-templates/opencode/hindsight-banks/` contains custom `retain_mission`, `observations_mission`, `reflect_mission`, disposition traits, and Mental Model definitions tailored to that agent's role:

| Bank JSON File | Disposition (Sk / Lit / Emp) | Primary Focus | Custom `reflect_mission` Summary |
|---|:---:|---|---|
| `opencode-orchestrator.json` | 3 / 3 / **5** | Project roadmap, developer preferences, host profile, handoffs | Executive status summary, user preferences, host setup, milestones, and handoffs. |
| `opencode-oracle.json` | **5** / 2 / 3 | System architecture, design trade-offs, post-mortems | Authoritative architectural breakdown detailing design patterns, trade-offs, and invariants. |
| `opencode-fixer.json` | 4 / **5** / 1 | Error trace patterns, bug root causes, fix runbooks | Root-cause diagnosis and actionable repair runbook based on past post-mortems. |
| `opencode-librarian.json` | 2 / **5** / 2 | External documentation, API specs, library quirks | Structured documentation briefing highlighting API signatures and library gotchas. |
| `opencode-explorer.json` | 3 / 2 / 1 | Directory structure, module layout, AST symbol maps | Codebase architecture map detailing module responsibilities and symbol layout. |
| `opencode-designer.json` | 2 / 3 / **5** | UI component patterns, brand tokens, accessibility | Visual design specification detailing component tokens, layout rules, and ARIA guidelines. |

### Single Command to Provision / Reconfigure All Banks

Run `./update-memory-banks.sh` to apply all bank configurations from `hindsight-banks/` to the local Hindsight server:

```bash
./update-memory-banks.sh $HOME/.config/opencode/hindsight-banks http://localhost:8888 --yes
```

### Deprecated: `patch-hindsight-plus.js`

The legacy `patch-hindsight-plus.js` script targeted the older `opencode-hindsight-plus` package and is no longer called during installation. It is retained for reference only.

---

## Plugin Resolution & Cache Single-Copy Architecture

### Mechanism Findings & OpenCode Resolution Logic

Reverse engineering the OpenCode binary (`/usr/bin/opencode`, Bun-compiled executable) revealed the exact mechanism governing plugin specifier resolution (`resolvePluginSpec` / `pQ`):

1. **NPM Specifiers (`oh-my-opencode-slim`, `@toady00/opencode-hindsight`)**:
   - Evaluated via `Jq(spec)` -> returns `false` (not starting with `.`, `file://`, or absolute path).
   - Rewrites bare names to `${pkg}@latest`.
   - Triggers OpenCode's internal downloader (`V1.add(...)`), which fetches packages directly into `~/.cache/opencode/packages/<pkg>/`.
   - Files in `~/.config/opencode/node_modules/` are ignored for NPM specifiers, causing duplicate package downloads and `@latest` vs. bare directory divergence.

2. **Relative File Specifiers (`./node_modules/<pkg>`)**:
   - Evaluated via `Jq(spec)` -> returns `true`.
   - Resolved directly relative to the configuration folder (`~/.config/opencode/node_modules/<pkg>`).
   - Completely **bypasses OpenCode's internal downloader**, ensuring `~/.cache/opencode/packages/` remains empty (0 extra copies).

### Single-Copy Architecture

To eliminate package cache fragmentation and maintain exactly one physical copy on disk:

1. **`opencode.json`**: Configured with relative paths (`"./node_modules/<package>"`) for all plugins.
2. **`package.json`**: Serves as the single source of truth for all plugin versions and git repositories (e.g. `"@toady00/opencode-hindsight": "github:Toady00/opencode-hindsight#v0.2.2"`).
3. **`LAUNCHER_INSTALL_CMDS` (`opencode.env`)**: Runs a single `bun install` command inside `$HOME/.config/opencode`.
4. **Hard-link Sharing**: Bun hard-links `node_modules/` to Bun's global cache (`~/.bun/install/cache`), sharing identical inodes with zero extra disk footprint.

---

## Skill Recreation & Download Guide

### Main Purpose & Sources of Each Skill / Tool

1. **`sequential-thinking`**:
   * **Main Purpose**: Provides dynamic, reflective step-by-step reasoning with thought revision, hypothesis branching, and backtracking capabilities.
   * **Source**: Adapted from [mrgoonie/claudekit-skills](https://github.com/mrgoonie/claudekit-skills/tree/main/.claude/skills/sequential-thinking) (MIT).
   * **MCP Package**: `@modelcontextprotocol/server-sequential-thinking` (run via `bunx`).

2. **`arbor`**:
   * **Main Purpose**: Exposes graph-native AST code intelligence, dependency traversal, and targeted hypothesis checks (~700 - 900 tokens) without full codebase RAG scans.
   * **Source**: [RUC-NLPIR/Arbor](https://github.com/RUC-NLPIR/Arbor) agent framework & MCP specification.
   * **Tool Command**: `uv tool install arbor-agent` -> `arbor mcp`.

3. **`openadapt`**:
   * **Main Purpose**: Provides headless browser rendering, DOM state inspection, visual web element verification, and web action automation (~800 - 1,100 tokens).
   * **Source**: [OpenAdapt AI](https://github.com/openadapt-ai/OpenAdapt) browser automation emitter.
   * **Tool Command**: `uv tool install "openadapt[browser]"` -> `openadapt mcp`.
   * **Dependencies for Playwright WebKit Browser:** `icu74`, `playwright-webkit-flite-deps`.

4. **`opencode-a2a`**:
   * **Main Purpose**: Enables Agent-to-Agent (A2A) protocol peer discovery, remote agent card inspection, and inter-agent task delegation across framework boundaries.
   * **Source**: [Intelligent-Internet/opencode-a2a](https://github.com/Intelligent-Internet/opencode-a2a) runtime.
   * **Tool Command**: `uv tool install opencode-a2a` -> `opencode-a2a serve --port 9090` (sidecar) & `opencode-a2a mcp`.

5. **`hindsight`**:
   * **Main Purpose**: Per-agent long-term memory with bank isolation. Each agent writes to its own bank (`opencode-{agent}`) with project-tagged memories. Auto-recall/retain for the orchestrator's root session; explicit tools for subagent child sessions.
   * **Source**: [Toady00/opencode-hindsight](https://github.com/Toady00/opencode-hindsight) (installed from git) & [Vectorize Hindsight](https://github.com/vectorize-io/hindsight).
   * **Package / Service**: `@toady00/opencode-hindsight` (plugin).

6. **`hindsight-api`**:
   * **Main Purpose**: Teaches agents how to programmatically inspect, query, and reconfigure Hindsight memory banks, missions, and mental models via the Hindsight REST API (`http://localhost:8888`).
   * **Source**: Local Hindsight REST API (`local-memory.sh`).
