# Hindsight Support Status Across Agent Runtimes & Frameworks

## Executive Summary

This document provides a comprehensive analysis of **Hindsight** memory support across both assistant and coding agent harnesses, frameworks, and runtimes.

- **Hermes Agent** and **OMP (Oh-My-Pi)** are the primary agent runtimes with **first-class native core configuration** for Hindsight.
- **Claude Code, OpenCode, OpenHands, Roo Code, Cline, Aider, Continue, AutoGen, CrewAI, and LangChain/LangGraph** feature **official plugins, lifecycle hooks, or custom memory adapters**.
- **LibreFang, NanoBot, NanoClaw, PicoClaw, IronClaw, and ZeroClaw** do not have native core code support, but connect to Hindsight via standard Model Context Protocol (**MCP**) or REST API calls to the local memory daemon (`assistants/local-memory.sh` on port 28888).

---

## 1. Primary Assistant Agent Runtimes (Local Workspace Core)

| Agent Runtime | Hindsight Support | Integration Type | Key Features & Connection Modes |
| :--- | :--- | :--- | :--- |
| **Hermes Agent** | **Full Native Core** | Built-in provider (`plugins/memory/hindsight`) | Native tools (`hindsight_recall`, `hindsight_reflect`, `hindsight_retain`), `cloud`, `local_embedded`, and `local_external` connection modes, AUR patches, Desktop UI controls. |
| **OMP (Oh-My-Pi)** | **Full Native Core** | Built-in backend (`memory.backend: hindsight`) | Native **Mental Model Auto-Seeding** (`user-preferences`, `project-conventions`, `project-decisions`), declarative JSON bank schemas, MCP tool access. |
| **LibreFang** | Generic MCP / REST | No native core code | Uses `hindsight-mcp` or direct REST API requests to port `28888`. |
| **NanoBot** | Generic MCP / REST | No native core code | Uses `hindsight-mcp` or direct REST API requests to port `28888`. |
| **NanoClaw** | Generic MCP / REST | No native core code | Uses `hindsight-mcp` or direct REST API requests to port `28888`. |
| **PicoClaw** | Generic MCP / REST | No native core code | Uses `hindsight-mcp` or direct REST API requests to port `28888`. |
| **IronClaw** | Generic MCP / REST | No native core code | Uses `hindsight-mcp` or direct REST API requests to port `28888`. |
| **ZeroClaw** | Generic MCP / REST | No native core code | Modular memory architecture (`zeroclaw-memory`), consumes Hindsight via `hindsight-mcp`. |

---

## 2. Other Coding Agents & Assistant Harnesses

### A. Terminal & CLI Coding Agents

#### 1. Claude Code (Anthropic)
- **Support Level:** **Official Plugin & Lifecycle Hooks Integration**
- **Integration Package:** `vectorize-io/hindsight` plugin & MCP server.
- **Mechanism:** Direct integration into Claude Code lifecycle hooks (`PrePrompt`, `PostResponse`). Features **auto-recall** to prefetch workspace history before prompt execution and **auto-retain** to extract facts from conversation turns without explicit user instructions.

#### 2. OpenCode
- **Support Level:** **Official Git Plugin & Multi-Bank MCP Integration**
- **Integration Package:** `@toady00/opencode-hindsight` (v0.2.2) git plugin + `bunx hindsight-mcp`.
- **Mechanism:** Supports per-agent memory bank isolation (`opencode-orchestrator`, `opencode-oracle`, `opencode-fixer`, etc.). Automatic recall/retention runs on orchestrator sessions, with explicit tool execution (`hindsight_recall`, `hindsight_reflect`, `hindsight_retain`) available to subagents.

#### 3. OpenHands (formerly OpenDevin)
- **Support Level:** **Official Integration & MCP Server**
- **Integration Package:** Native `config.toml` binding + `hindsight-mcp`.
- **Mechanism:** Automatically prefetches historical task context on container startup and retains task transcripts and learned solutions upon task completion.

#### 4. Aider (Terminal Pair Programmer)
- **Support Level:** **Official Executable Wrapper (`hindsight-aider`)**
- **Integration Package:** `hindsight-aider` PyPI / CLI wrapper.
- **Mechanism:** Wraps `aider` CLI executions to provide stateful memory across sessions. Queries project memory bank on session init and auto-retains lessons learned from git diffs and chat transcripts on exit.

#### 5. Goose (Block)
- **Support Level:** **MCP Integration**
- **Integration Package:** `hindsight-mcp`.
- **Mechanism:** Connects to Hindsight via standard Model Context Protocol, enabling Goose's autonomous execution tools to read/write persistent project memories.

---

### B. IDE & Editor Extensions

#### 1. Roo Code (VS Code Extension)
- **Support Level:** **Official Tool Provider & MCP Integration**
- **Integration Package:** `hindsight-roo-code` PyPI package / MCP server.
- **Mechanism:** Exposes `hindsight_recall`, `hindsight_retain`, and `hindsight_reflect` tools across Roo Code execution modes (Code, Architect, Ask).

#### 2. Cline (VS Code Extension)
- **Support Level:** **Deterministic Event Hook Adapter**
- **Integration Package:** `hindsight-cline` adapter.
- **Mechanism:** Bypasses LLM tool-call dependency by attaching directly to Cline's event triggers (`TaskStart`, `UserPromptSubmit`, `TaskComplete`) for automated context retrieval and memory retention.

#### 3. Continue.dev
- **Support Level:** **Official Extension Adapter & Context Provider**
- **Integration Package:** `hindsight-continue` adapter & `@hindsight` provider.
- **Mechanism:** Enables `@hindsight` context command in chat and uses MCP in autonomous agent mode to query workspace history.

---

### C. Agent Frameworks & SDKs

#### 1. Microsoft AutoGen
- **Support Level:** **Official `FunctionTool` / Python SDK Integration**
- **Integration Package:** `hindsight-client` Python SDK.
- **Mechanism:** Wraps `recall`, `reflect`, and `retain` operations into `FunctionTool` objects for `AssistantAgent` instances, facilitating shared or isolated memory banks across multi-agent groups.

#### 2. CrewAI
- **Support Level:** **Official `ExternalMemory` Provider (`HindsightStorage`)**
- **Integration Package:** `HindsightStorage` plugin.
- **Mechanism:** Overrides CrewAI's default memory storage backend with Hindsight's memory engine for cross-crew memory persistence.

#### 3. LangChain & LangGraph
- **Support Level:** **SDK & Framework Adapters**
- **Integration Package:** `hindsight-client` (Python), `@vectorize-io/hindsight-ai-sdk` (TypeScript/Vercel AI SDK), `hindsight-haystack`.
- **Mechanism:** Provides custom memory nodes and state graph channels for LangChain chains, LangGraph state machines, Vercel AI SDK pipelines, and Haystack RAG flows.

---

## 3. Comprehensive Harness Matrix

| Harness / Framework | Category | Native Built-in | Plugin / Adapter | MCP Integration | Integration Pattern |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Hermes Agent** | Assistant Agent | **Yes** | Yes | Yes | Native core provider (`plugins/memory/hindsight`) |
| **OMP (Oh-My-Pi)** | Assistant Harness | **Yes** | Yes | Yes | Native `memory.backend: hindsight` + mental model auto-seeding |
| **Claude Code** | Coding CLI Agent | No | **Yes** | Yes | Lifecycle hooks (`vectorize-io/hindsight`) |
| **OpenCode** | Multi-Agent Harness | No | **Yes** | Yes | `@toady00/opencode-hindsight` + per-agent bank isolation |
| **OpenHands** | Autonomous Coding Agent | No | **Yes** | Yes | `config.toml` + `hindsight-mcp` |
| **Roo Code** | IDE Extension | No | **Yes** | Yes | `hindsight-roo-code` tool wrapper |
| **Cline** | IDE Extension | No | **Yes** | No | `hindsight-cline` deterministic event hooks |
| **Aider** | CLI Pair Programmer | No | **Yes** | No | `hindsight-aider` CLI wrapper |
| **Goose** | Autonomous Agent | No | No | **Yes** | Standard `hindsight-mcp` |
| **Continue.dev** | IDE Extension | No | **Yes** | Yes | `hindsight-continue` + `@hindsight` context command |
| **AutoGen** | Agent Framework | No | **Yes** | Yes | `FunctionTool` wrappers for `AssistantAgent` |
| **CrewAI** | Agent Framework | No | **Yes** | Yes | `HindsightStorage` / `ExternalMemory` plugin |
| **LangChain / LangGraph** | Agent Framework | No | **Yes** | Yes | `hindsight-client`, `@vectorize-io/hindsight-ai-sdk` |
