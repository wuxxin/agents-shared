---
name: opencode-a2a
description: Agent-to-Agent (A2A) protocol peer discovery, remote agent delegation, and inter-agent message passing via opencode-a2a mcp. Use when querying external agent capabilities, delegating sub-tasks across framework boundaries, or communicating with remote agent cards on port 9090.
---

# OpenCode Agent-to-Agent (A2A) Skill

Provides Agent-to-Agent protocol communication paired with `opencode-a2a` tools (`mcp__a2a__*`) and sidecar server (`http://localhost:9090`).

## When to Trigger

Use A2A tools when:
- Discovering capabilities of peer agents via A2A Agent Cards
- Delegating specialized tasks to remote or external agent runtimes (e.g. AutoGen, CrewAI, LangGraph)
- Exposing OpenCode subagent services to external A2A clients
- Exchanging structured task messages and streaming progress across agent mesh endpoints

## Workflow & Guidelines

1. **Discovery**: Call A2A card discovery to read target agent capabilities and supported schemas.
2. **Task Delegation**: Formulate a task contract and send via `a2a` message payload.
3. **Status Polling & Result Handling**: Stream or poll task completion status before synthesizing results for the main orchestrator session.
