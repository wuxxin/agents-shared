---
name: hindsight
description: Long-term memory recall, retention, reflection, and per-agent mental model queries via Vectorize Hindsight API (http://localhost:8888) and hindsight-mcp tools. Use to query past architecture decisions, retrieve bug post-mortems, retain key session learnings, or query specific agent memory banks (e.g. opencode-oracle vs opencode-fixer).
---

# Vectorize Hindsight Memory Skill

Provides persistent long-term memory and mental model access paired with `@toady00/opencode-hindsight` plugin.

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
- **Cross-Bank Queries**: Each agent operates in its own bank. Cross-bank recall is not natively supported; use the Hindsight REST API directly for cross-bank queries.

## Guidelines

1. Leverage automatic background retention (`@toady00/opencode-hindsight`) for the orchestrator's root session.
2. Use explicit plugin tool calls (`hindsight_retain`, `hindsight_recall`, `hindsight_reflect`) for subagent child sessions.
