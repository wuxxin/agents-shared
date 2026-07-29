---
name: hindsight
description: Long-term memory recall, retention, reflection, and per-agent mental model queries via Vectorize Hindsight API (http://localhost:8888) and hindsight-mcp tools. Use to query past architecture decisions, retrieve bug post-mortems, retain key session learnings, or query specific agent memory banks (e.g. opencode-oracle vs opencode-fixer).
---

# Vectorize Hindsight Memory Skill

Provides persistent long-term memory and mental model access paired with `opencode-hindsight-plus` plugin and `hindsight-mcp` tools (`mcp__hindsight__*`).

## Memory Isolation & Bank Architecture

Each agent operates within an isolated memory bank namespace (`opencode-{agent}`) to prevent cross-contamination:
- **`opencode-oracle`**: Architectural decisions, post-mortems, design patterns.
- **`opencode-fixer`**: Error stack traces, low-level patch history, test fix patterns.
- **`opencode-orchestrator`**: Session handoffs, project milestones, user preferences.
- **`opencode-librarian`**: Research summaries, API documentation snapshots.

## When to Trigger

- **`hindsight_recall`**: Proactively search memory banks before answering complex questions where prior session context is valuable.
- **`hindsight_retain`**: Explicitly save crucial user preferences, architectural rules, or fix runbooks.
- **`hindsight_reflect`**: Request a synthesized summary over historical memories for a specific query.
- **Cross-Bank Queries**: Worker agents (e.g., `fixer`) can query `oracle`'s memory bank by passing `bank_id: "opencode-oracle"` in explicit `hindsight_recall` tool calls.

## Guidelines

1. Leverage automatic background retention (`opencode-hindsight-plus`) for general session history.
2. Use explicit MCP tool calls (`hindsight-mcp`) when querying target mental models across different agent banks.
