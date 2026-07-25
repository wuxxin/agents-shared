# Hindsight: Full Bank Export / DB Reset / Re-Import with New Embedding & Reranker

## Overview

When you change the embedding model or reranker model in Hindsight, existing vectors in the database are tied to the old model. Semantic search will produce degraded results because query embeddings come from the new model while stored embeddings are from the old one.

**Hindsight cannot change the embedding model in-place on populated banks.** The supported path is: export all banks → destroy the database → start fresh with new config → import banks (re-embedding happens automatically).

**No LLM re-extraction occurs.** Facts, observations, and entity links are imported as-is from the export archives. Only embeddings and vector indexes are regenerated from the stored text using the new model.

---

## Current Instance State (2026-07-25)

### Service

| Property | Value |
|----------|-------|
| API version | `0.8.5` |
| Health | healthy, database connected |
| Endpoint | `http://localhost:8888` |
| PostgreSQL | external, `postgresql://username:password@localhost:5432/dbname` |
| Vector extension | `pgvector` |
| Text search | `pgroonga` |

### Embedding & Reranker (current)

| Setting | Value |
|---------|-------|
| Embedding provider | `openai` (local endpoint) |
| Embedding URL | `http://localhost:51080/v1` |
| Embedding model | `pplx-embedding` |
| Reranker provider | `cohere` (local endpoint) |
| Reranker URL | `http://localhost:51080/v1/rerank` |
| Reranker model | `qwen3-reranker` |

### Banks

| Bank | Docs | Facts | Observations | Config Overrides | Mental Models |
|------|------|-------|-------------|------------------|---------------|
| `hermes-test-bank` | 13 | 24 | 2 | **None** (all defaults) | 0 |
| `hermes-assistant` | 4 | 28 | 14 | `retain_mission`, `observations_mission` | 4 |
| `hermes-test` | 3 | 419 | 183 | `retain_mission`, `observations_mission` | 8 |

### Bank Config Overrides to Preserve

#### `hermes-assistant` (and `hermes-test` — identical overrides)

These two banks share the same custom missions. The document-transfer API does **not** export bank configuration — only documents, facts, entities, and observations. After import, these overrides must be re-applied manually.

**retain_mission:**
```
Consolidate the user's preferences, recurring patterns in behavior, routines,
scheduled events, commitments, decisions, mood tracking metrics, relational
and social updates, and psychological insights. Consolidate details relating
to their sleep-wake schedule, supplement stacks, workout sessions
(inlineskaten), and interpersonal encounters. Ignore small talk and transient
details. Consolidate what they ask for repeatedly and what they care about.
What annoys them? What makes them laugh? Consolidate the user's running
machine configuration, and available tools, and paths/services shared with the
agent, the agent harness and its available tools and activate features.
```

**observations_mission:**
```
Extract the user's preferences, recurring patterns in the user's habits,
routines, constraints, values, decisions, physical wellness (fasting, sleep,
health, supplements), mood and emotional state, personal context (extract what
they ask for repeatedly and what they care about. What annoys them? What makes
them laugh?), people and the relationships to them, social
engagement/encounters, and ADHD-specific coping strategies. Extract the user's
running machine configuration, and available tools, and paths/services shared
with the agent, the agent harness and its current available tools and activate
features. Capture behavioral cues for future adaptation. Track how their
constraints and priorities evolve over time.
```

**enable_observations:** `true` (this is already the default — no action needed)

#### `hermes-test-bank`

No overrides — everything is default. No post-import config needed.

---

## What the API Exports vs. Doesn't

### Document-transfer API (`GET/POST /v1/default/banks/{bank_id}/document-transfer`)

| Exported | Not exported |
|----------|-------------|
| Documents (source content) | Embeddings (regenerated on import) |
| Raw chunks | Database IDs |
| Extracted facts | Bank configuration (missions, dispositions, entity labels) |
| Entities (by canonical name) | Mental models (auto-regenerated) |
| Causal links | Directives |
| Observations (with `include_observations=true`) | Webhooks |
| | Operation history |

---

## Step-by-Step Workflow

### Phase 1: Export All Banks

Run while the service is running. Observations are included so the target won't need to re-consolidate them.

```bash
cd /tmp

# Export all three banks with observations
for bank in hermes-test-bank hermes-assistant hermes-test; do
  echo "Exporting $bank..."
  curl -sS -o "${bank}.zip" \
    "http://localhost:8888/v1/default/banks/${bank}/document-transfer?include_observations=true"
  echo "  size: $(ls -lh ${bank}.zip | awk '{print $5}')"
done
```

Verify the ZIP files are non-zero (they contain raw JSONL + metadata, usually small):

```bash
file /tmp/hermes-test-bank.zip /tmp/hermes-assistant.zip /tmp/hermes-test.zip
```

### Phase 2: Stop the Service

```bash
~/agent-shared/code/agents-shared/assistants/local-memory.sh stop
```

### Phase 3: Destroy and Recreate PostgreSQL Database

Connect to PostgreSQL and run:

```sql
-- 1. Drop and recreate the database
DROP DATABASE IF EXISTS dbname;
CREATE DATABASE dbname;

-- 2. Connect to new database and install extensions
\c dbname
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pgroonga;
```

> **Note:** If switching vector extension (e.g., to `pgvectorscale` or `vchord`), install that extension instead. If dropping pgroonga for another text-search backend, install the corresponding extension.

### Phase 4: Update Embedding & Reranker Config

```bash
~/agent-shared/code/agents-shared/assistants/local-memory.sh edit
```

In `~/.config/systemd/user/local-memory.env`, change these lines to your new models:

```ini
# --- New embedding model ---
HINDSIGHT_API_EMBEDDINGS_OPENAI_MODEL="your-new-embedding-model"

# --- New reranker model ---
HINDSIGHT_API_RERANKER_COHERE_MODEL="your-new-reranker-model"

# Optional: if new model has different dimensions
# HINDSIGHT_API_EMBEDDINGS_OPENAI_DIMENSIONS=1024
```

Save and exit. The `edit` command auto-restarts the service. Verify:

```bash
~/agent-shared/code/agents-shared/assistants/local-memory.sh status
```

If it didn't restart automatically:

```bash
~/agent-shared/code/agents-shared/assistants/local-memory.sh restart
```

### Phase 5: Wait for Startup

```bash
until curl -sf http://localhost:8888/health > /dev/null; do
  echo "Waiting for Hindsight..."
  sleep 2
done
echo "Hindsight is healthy"
```

### Phase 6: Import All Banks (Re-Embedding)

Each import creates the bank (auto-create on first access) and re-embeds all facts with the new model. This runs **asynchronously**.

```bash
cd /tmp

for bank in hermes-test-bank hermes-assistant hermes-test; do
  echo "Importing $bank..."
  RESP=$(curl -sS -X POST \
    -F "file=@${bank}.zip" \
    "http://localhost:8888/v1/default/banks/${bank}/document-transfer")
  echo "$RESP" | python3 -m json.tool
  OP_ID=$(echo "$RESP" | python3 -c "import sys,json; print(json.load(sys.stdin)['operation_id'])")
  echo "  -> operation_id: $OP_ID (bank: $bank)"
done
```

### Phase 7: Wait for Async Imports to Complete

Each import generates a `retain_batch` parent + child operations. Poll until all are terminal.

```bash
wait_for_imports() {
  for bank in hermes-test-bank hermes-assistant hermes-test; do
    while true; do
      PENDING=$(curl -sf "http://localhost:8888/v1/default/banks/${bank}/operations?status=pending" | python3 -c "import sys,json;print(json.load(sys.stdin)['total'])" 2>/dev/null || echo 0)
      PROCESSING=$(curl -sf "http://localhost:8888/v1/default/banks/${bank}/operations?status=processing" | python3 -c "import sys,json;print(json.load(sys.stdin)['total'])" 2>/dev/null || echo 0)
      printf "\r  %-20s  pending: %3s  processing: %3s" "$bank" "$PENDING" "$PROCESSING"
      if [ "$PENDING" = "0" ] && [ "$PROCESSING" = "0" ]; then
        echo ""
        break
      fi
      sleep 3
    done
  done
}

wait_for_imports
echo "All imports complete."
```

Check for any failures:

```bash
for bank in hermes-test-bank hermes-assistant hermes-test; do
  echo "=== $bank failures ==="
  curl -sf "http://localhost:8888/v1/default/banks/${bank}/operations?status=failed" | \
    python3 -c "
import sys,json
d=json.load(sys.stdin)
print(f'  total failed: {d[\"total\"]}')
for op in d.get('operations',[]):
    print(f'  [{op[\"operation_type\"]}] {op[\"id\"][:8]}... \n    {op.get(\"error_message\",\"no error\")[:120]}')
"
done
```

### Phase 8: Re-Apply Bank Config Overrides

The document-transfer API does not export bank configuration. Re-apply custom missions for `hermes-assistant` and `hermes-test`.

```bash
# Shared missions (identical for both banks)
RETAIN_MISSION='Consolidate the user'\''s preferences, recurring patterns in behavior, routines, scheduled events, commitments,  decisions, mood tracking metrics, relational and social updates, and psychological insights.  Consolidate details relating to their sleep-wake schedule, supplement stacks, workout sessions (inlineskaten), and interpersonal encounters. Ignore small talk and transient details. Consolidate what they ask for repeatedly and what they care about. What annoys them? What makes them laugh? Consolidate the user'\''s running machine configuration, and available tools, and paths/services shared with the agent, the agent harness and its available tools and activate features.'

OBSERVATIONS_MISSION='Extract the user'\''s preferences, recurring patterns in the user'\''s habits, routines, constraints, values, decisions, physical wellness (fasting, sleep, health, supplements), mood and emotional state, personal context (extract what they ask for repeatedly and what they care about. What annoys them? What makes them laugh?), people and the relationships to them, social engagement/encounters, and ADHD-specific coping strategies. Extract the user'\''s running machine configuration, and available tools, and paths/services shared with the agent, the agent harness and its current available tools and activate features. Capture behavioral cues for future adaptation. Track how their constraints and priorities evolve over time.'

# Apply to hermes-assistant
curl -sS -X PATCH "http://localhost:8888/v1/default/banks/hermes-assistant/config" \
  -H "Content-Type: application/json" \
  -d "$(python3 -c "
import json
print(json.dumps({
    'retain_mission': '''$RETAIN_MISSION''',
    'observations_mission': '''$OBSERVATIONS_MISSION'''
}))
")"

# Apply to hermes-test
curl -sS -X PATCH "http://localhost:8888/v1/default/banks/hermes-test/config" \
  -H "Content-Type: application/json" \
  -d "$(python3 -c "
import json
print(json.dumps({
    'retain_mission': '''$RETAIN_MISSION''',
    'observations_mission': '''$OBSERVATIONS_MISSION'''
}))
")"
```

> **Tip:** The single-quote escaping above works but is fragile. A cleaner alternative is to write the missions to a JSON file and use `curl -d @file.json`. Or, use the Hindsight Python SDK:
> ```python
> from hindsight_client import HindsightClient
> client = HindsightClient(base_url="http://localhost:8888")
> client.update_bank_config("hermes-assistant",
>     retain_mission="...",
>     observations_mission="...")
> ```

### Phase 9: Verify

```bash
# 1. Check bank stats match pre-export counts
for bank in hermes-test-bank hermes-assistant hermes-test; do
  echo "=== $bank ==="
  curl -sf "http://localhost:8888/v1/default/banks/${bank}/stats" | \
    python3 -c "
import sys,json
d=json.load(sys.stdin)
print(f'  docs: {d[\"total_documents\"]}, facts: {d[\"total_nodes\"]}, observations: {d[\"total_observations\"]}')
print(f'  world: {d[\"nodes_by_fact_type\"].get(\"world\",0)}, experience: {d[\"nodes_by_fact_type\"].get(\"experience\",0)}, observation: {d[\"nodes_by_fact_type\"].get(\"observation\",0)}')
"
done

# Expected:
#   hermes-test-bank: 13 docs, 24 facts, 2 observations
#   hermes-assistant:  4 docs, 28 facts, 14 observations
#   hermes-test:        3 docs, 419 facts, 183 observations

# 2. Verify bank configs were restored
for bank in hermes-assistant hermes-test; do
  echo "=== $bank overrides ==="
  curl -sf "http://localhost:8888/v1/default/banks/${bank}/config" | \
    python3 -c "
import sys,json
d=json.load(sys.stdin)
o=d.get('overrides',{})
for k,v in o.items():
    if v is not None:
        print(f'  {k}: {\"present\" if v else \"empty\"} (len={len(str(v))})')
    else:
        print(f'  {k}: null')
"
done

# 3. Run a recall query to confirm semantic search works
curl -sf -X POST "http://localhost:8888/v1/default/banks/hermes-test/recall" \
  -H "Content-Type: application/json" \
  -d '{"query": "user preferences and habits", "max_tokens": 500}' | \
  python3 -c "
import sys,json
d=json.load(sys.stdin)
memories=d.get('memories',[])
print(f'  memories returned: {len(memories)}')
if memories:
    print(f'  top score: {memories[0].get(\"score\",\"?\")}')
    print(f'  first: {memories[0].get(\"content\",\"\")[:120]}...')
"
```

### Phase 10 (Optional): Trigger Consolidation

Imported observations are restored as-is. To force a fresh consolidation pass with the new embedding model:

```bash
for bank in hermes-test-bank hermes-assistant hermes-test; do
  echo "Triggering consolidation for $bank..."
  curl -sS -X POST "http://localhost:8888/v1/default/banks/${bank}/consolidate"
done
```

Wait for consolidation to complete (check `pending_consolidation` goes to 0):

```bash
for bank in hermes-test-bank hermes-assistant hermes-test; do
  STATS=$(curl -sf "http://localhost:8888/v1/default/banks/${bank}/stats")
  PENDING=$(echo "$STATS" | python3 -c "import sys,json;print(json.load(sys.stdin)['pending_consolidation'])")
  echo "$bank: pending_consolidation=$PENDING"
done
```

---

## Rollback Plan

If the new embedding/reranker produces worse results:

1. Stop the service
2. Restore the old database (if you kept a backup) or re-run the old config
3. Revert `~/.config/systemd/user/local-memory.env` to the old settings
4. Start the service — old vectors are unaffected

The ZIP exports are a permanent archive. You can re-import them at any time.

---

## Key Limitations

1. **Bank config is not exported.** Missions, dispositions, entity labels, recall/consolidation tuning — all lost on DB reset. Re-apply after import.
2. **Mental models are not exported.** They are auto-generated from facts. After import, they will be rebuilt on next use (reflect, manual refresh, or auto-refresh schedule).
3. **Directives and webhooks are not exported.** Re-create if needed. (None existed in current instance.)
4. **Operation history is not exported.** Failed/completed operation logs are not preserved.
5. **Embedding dimension changes.** If the new model has different dimensions than the old one, you MUST use a fresh database or the import will fail (the `embedding` column type is fixed per schema). This is the primary reason for the full DB reset approach.
6. **No merge on import.** `import-bank` (admin CLI) requires the target bank not to exist. The `document-transfer` API import is additive — documents with matching IDs are handled per `on_conflict` (skip/replace/new-id).

---

## Environment Variables Changed

In `~/.config/systemd/user/local-memory.env`:

| Variable | Old | New |
|----------|-----|-----|
| `HINDSIGHT_API_EMBEDDINGS_OPENAI_MODEL` | `pplx-embedding` | *(user's choice)* |
| `HINDSIGHT_API_RERANKER_COHERE_MODEL` | `qwen3-reranker` | *(user's choice)* |

Optional additional changes:

| Variable | Purpose |
|----------|---------|
| `HINDSIGHT_API_EMBEDDINGS_OPENAI_DIMENSIONS` | Set if new model uses non-default dimensions |
| `HINDSIGHT_API_VECTOR_EXTENSION` | Switch to `pgvectorscale` or `vchord` for better perf |
| `HINDSIGHT_API_TEXT_SEARCH_EXTENSION` | Switch from `pgroonga` to another BM25 backend |
