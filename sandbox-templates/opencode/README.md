# OpenCode Agent Orchestration Template

Complete sandbox configuration template for OpenCode with `oh-my-opencode-slim`, multi-agent orchestration, Arbor graph intelligence, OpenAdapt browser automation, Agent-to-Agent (A2A) protocol bridge, and per-agent Hindsight long-term memory.

---

## Setup, Installation, and Teardown

### 1. Create and Provision Sandbox

Run `sandbox-ctl` to provision the sandbox environment:

```bash
sandbox-ctl install opencode --no-start --new-config-from sandbox-templates/opencode/opencode.env
```

### 2. Copy Template Configuration Files

Ensure the template files exist under `$HOME/.config/opencode/`:
- `opencode.json`
- `package.json`
- `tui.json`
- `oh-my-opencode-slim.jsonc`
- `skills/*` (`arbor`, `openadapt`, `opencode-a2a`, `hindsight`, `sequential-thinking`)

### 3. Provider Authentication (If Required)

If authenticating for the first time inside the sandbox:

```bash
opencode auth login --provider google-agy
opencode auth login --provider deepseek
opencode models --refresh
```

### 4. Automatic Environment & Skill Recreation

Running `sandbox-ctl install` automatically recreates all environment dependencies, CLI tools (`arbor-agent`, `openadapt[browser]`, `opencode-a2a`), bun packages, and skills via `LAUNCHER_INSTALL_CMDS`.

### 5. Start OpenCode

```bash
opencode
```

---

## Plugins Overview

| Plugin | Package | Purpose |
|---|---|---|
| `oh-my-opencode-slim` | `oh-my-opencode-slim` | Multi-agent orchestration (`orchestrator`, `oracle`, `explorer`, `librarian`, `designer`, `fixer`). |
| `opencode-hindsight-plus` | `opencode-hindsight-plus` | Advanced Hindsight long-term memory plugin with per-agent dynamic bank isolation and `additionalBanks` cross-recall. |
| `@anthonyhaussman/opencode-agy-auth` | `@anthonyhaussman/opencode-agy-auth` | Google AGY OAuth authentication for Claude + Gemini models. |
| `@slkiser/opencode-quota` | `@slkiser/opencode-quota` | Per-provider quota tracking, toast notifications, TUI status panels. |
| `opencode-handoff` | `opencode-handoff` | Session handoff with `/handoff` command. |
| `opencode-llm-proxy` | `opencode-llm-proxy` | Local LLM proxy on `127.0.0.1:4010`. |

---

## MCP Servers

| Server Name | Type | Command / Runner | Package / Source | Purpose |
|---|---|---|---|---|
| `sequential-thinking` | local | `bunx @modelcontextprotocol/server-sequential-thinking` | `@modelcontextprotocol/server-sequential-thinking` | Dynamic reflective reasoning chain with thought revision and branching. |
| `arbor` | local | `arbor mcp` | `arbor-agent` (PyPI / `uv tool`) | Graph-native AST code intelligence, dependency traversal, and hypothesis checks (~700 - 900 tokens). |
| `openadapt` | local | `openadapt mcp` | `openadapt[browser]` (PyPI / `uv tool`) | Headless browser rendering, DOM inspection, and web action automation (~800 - 1,100 tokens). |
| `a2a` | local | `opencode-a2a mcp` | `opencode-a2a` (PyPI / `uv tool`) | Agent-to-Agent protocol peer discovery and remote task delegation (sidecar on port `9090`). |
| `hindsight` | local | `bunx hindsight-mcp` | `hindsight-mcp` | Explicit tool-level long-term memory queries (`hindsight_recall`, `hindsight_retain`, `hindsight_reflect`) across target mental models. |
| `websearch` | remote | Exa API | Built-in / Remote | Real-time web search for docs, error messages, bug reports. |
| `gh_grep` | remote | GitHub API | Built-in / Remote | Public GitHub code search. |

---

## Subagent Profit & Skill Assignment Matrix

Each subagent in `oh-my-opencode-slim.jsonc` is equipped with dedicated MCP tools, skills, and isolated memory banks:

| Agent Role | Model & Variant | Assigned MCP Servers | Assigned Skills | Memory Bank Partition | Benefit & Profit |
|---|---|---|---|---|---|
| **`orchestrator`** | DeepSeek V4 Pro (`xhigh`) | `*` (All MCPs) | `*` (All skills) | `opencode-orchestrator` | Session handoffs, global plan tracking, multi-bank memory queries, cross-runtime A2A delegation. |
| **`oracle`** | DeepSeek V4 Pro (`xhigh`) | `sequential-thinking`, `arbor`, `hindsight`, `websearch`, `gh_grep` | `simplify`, `arbor`, `hindsight` | `opencode-oracle` | Pristine architectural decision memory without noise, graph-native AST code intelligence, sequential hypothesis revision. |
| **`librarian`** | DeepSeek V4 Flash (`low`) | `websearch`, `openadapt`, `context7`, `gh_grep` | `openadapt`, `hindsight` | `opencode-librarian` | Headless DOM rendering for JS-heavy web docs, persistent research index. |
| **`explorer`** | DeepSeek V4 Flash (`low`) | `arbor`, `gh_grep` | `arbor` | `opencode-explorer` | Fast dependency graph traversal and symbol relationship lookup without heavy RAG scans. |
| **`designer`** | Gemini 3.6 Flash (`medium`) | `openadapt`, `hindsight` | `openadapt`, `hindsight` | `opencode-designer` | Visual DOM inspection, layout rendering, visual regression checking, design system rule retention. |
| **`fixer`** | DeepSeek V4 Pro (`xhigh`) | `arbor`, `hindsight` | `arbor`, `hindsight` | `opencode-fixer` *(Reads `opencode-oracle` via `additionalBanks`)* | Isolated bank for low-level stack trace logs while reading high-level architectural decisions from `oracle`. |

---

## Per-Agent Memory Isolation & Bank Architecture

Memory isolation is configured in `opencode.json` via `opencode-hindsight-plus`:

```json
[
  "opencode-hindsight-plus",
  {
    "hindsightApiUrl": "http://localhost:8888",
    "dynamicBankId": true,
    "dynamicBankGranularity": ["agent", "gitProject"],
    "enableKnowledgePages": true
  }
]
```

### What is `enableKnowledgePages`?
In `opencode-hindsight-plus`, **Knowledge Pages** are dynamic, auto-synthesized markdown documents generated from a bank's mental models (`hindsight_page_list`, `hindsight_page_get`, `hindsight_page_create`, `hindsight_page_refresh`). Instead of executing an raw search (`hindsight_recall`) that returns multiple disjointed memory chunks, calling `hindsight_page_get` reads an up-to-date, auto-consolidated executive summary of an entire mental model (e.g. `User Profile & Core Preferences`, `System Architecture`, `Known Bugs & Verified Fixes`) in 1 single high-density call.

### Bank Naming Convention

Memory banks are named using agent role namespaces: `opencode-{agent}` (e.g., `opencode-orchestrator`, `opencode-oracle`, `opencode-fixer`, `opencode-librarian`, `opencode-explorer`, `opencode-designer`, and the user's personal context bank `assistant-test`).

---

## Hindsight Bank Configuration Setup & Apply Script

Each bank in `sandbox-templates/opencode/hindsight-banks/` contains custom `retain_mission`, `observations_mission`, `reflect_mission`, and Mental Model definitions tailored to that agent's role:

| Bank JSON File | Primary Focus | Custom `reflect_mission` Summary |
|---|---|---|
| `assistant-test.json` | Personal user context, wellness, routines, host environment | Empathetic, actionable personal summary respecting ADHD routines and wellness priorities. |
| `opencode-orchestrator.json` | Project roadmap, session handoffs, subagent assignments | Executive project status summary, upcoming milestones, and active handoffs. |
| `opencode-oracle.json` | System architecture, design trade-offs, post-mortems | Authoritative architectural breakdown detailing design patterns, trade-offs, and invariants. |
| `opencode-fixer.json` | Error trace patterns, bug root causes, fix runbooks | Root-cause diagnosis and actionable repair runbook based on past post-mortems. |
| `opencode-librarian.json` | External documentation, API specs, library quirks | Structured documentation briefing highlighting API signatures and library gotchas. |
| `opencode-explorer.json` | Directory structure, module layout, AST symbol maps | Codebase architecture map detailing module responsibilities and symbol export locations. |
| `opencode-designer.json` | UI component patterns, brand tokens, accessibility | Visual design specification detailing component tokens, layout rules, and ARIA guidelines. |

### Single Command to Provision / Reconfigure All Banks

Run this script block to apply all bank configurations to the local Hindsight server on `http://localhost:8888`:

```bash
for bank_file in sandbox-templates/opencode/hindsight-banks/*.json; do
  bank_id=$(basename "$bank_file" .json)
  echo "=== Applying configuration for bank: $bank_id ==="
  
  # 1. Update Retain, Observations, and Reflect missions
  python3 -c "
import json, urllib.request
data = json.load(open('$bank_file'))
bank = data.get('bank', {})
payload = json.dumps({
    'retain_mission': bank.get('retain_mission'),
    'observations_mission': bank.get('observations_mission'),
    'reflect_mission': bank.get('reflect_mission'),
    'enable_observations': bank.get('enable_observations', True)
}).encode('utf-8')
req = urllib.request.Request(
    'http://localhost:8888/v1/default/banks/$bank_id/config',
    data=payload,
    headers={'Content-Type': 'application/json'},
    method='PATCH'
)
try:
    with urllib.request.urlopen(req) as resp:
        print(f'  Config status: {resp.status}')
except Exception as e:
    print(f'  Config error (creating bank): {e}')
"

  # 2. Register Mental Models
  python3 -c "
import json, urllib.request
data = json.load(open('$bank_file'))
for mm in data.get('mental_models', []):
    payload = json.dumps(mm).encode('utf-8')
    req = urllib.request.Request(
        'http://localhost:8888/v1/default/banks/$bank_id/mental-models',
        data=payload,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    try:
        with urllib.request.urlopen(req) as resp:
            print(f'  Registered mental model {mm[\"id\"]}: {resp.status}')
    except Exception as e:
        print(f'  Mental model error ({mm[\"id\"]}): {e}')
"
done
```

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

4. **`opencode-a2a`**:
   * **Main Purpose**: Enables Agent-to-Agent (A2A) protocol peer discovery, remote agent card inspection, and inter-agent task delegation across framework boundaries.
   * **Source**: [Intelligent-Internet/opencode-a2a](https://github.com/Intelligent-Internet/opencode-a2a) runtime.
   * **Tool Command**: `uv tool install opencode-a2a` -> `opencode-a2a serve --port 9090` (sidecar) & `opencode-a2a mcp`.

5. **`hindsight`**:
   * **Main Purpose**: Enables long-term temporal, semantic, and entity-graph memory recall, retention, and reflection against local Hindsight server (`http://localhost:8888`), with per-agent bank isolation (`opencode-{agent}`) and cross-bank recall via `additionalBanks`.
   * **Source**: [best-linux-code/opencode-hindsight-plus](https://github.com/best-linux-code/opencode-hindsight-plus) & [Vectorize Hindsight](https://github.com/vectorize-io/hindsight).
   * **Package / Service**: `opencode-hindsight-plus` (plugin) + `hindsight-mcp` (MCP server).

6. **`hindsight-api`**:
   * **Main Purpose**: Teaches agents how to programmatically inspect, query, and reconfigure Hindsight memory banks, missions, and mental models via the Hindsight REST API (`http://localhost:8888`).
   * **Source**: Local Hindsight REST API (`local-memory.sh`).

### Single Command to Recreate / Sync All Skills

Run the following unified script block to recreate all skill directories and sync definition files from the template to `$HOME/.config/opencode/skills/`:

```bash
for skill in sequential-thinking arbor openadapt opencode-a2a hindsight hindsight-api; do
  mkdir -p "$HOME/.config/opencode/skills/$skill"
  if [ -f "sandbox-templates/opencode/skills/$skill/SKILL.md" ]; then
    cp "sandbox-templates/opencode/skills/$skill/SKILL.md" "$HOME/.config/opencode/skills/$skill/SKILL.md"
  fi
done
```
