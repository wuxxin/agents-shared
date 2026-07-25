# Hindsight Configuration & Tuning Guide

This document provides a consolidated reference for configuring the **Hindsight Memory Service** (`local-memory.sh`) for local inference deployments.

## Hardware & Backend Capacity Model

The default configuration is tuned for a local inference environment with the following concurrency and context boundaries:

- **Chat/Vision LLM**: **2 parallel LLM calls** available for Hindsight tasks (`HINDSIGHT_API_LLM_MAX_CONCURRENT=2`).
- **Embedding Model**: **2 parallel embedding calls** available (`HINDSIGHT_API_RECALL_MAX_CONCURRENT=2`), **8,192 (8K) max context window**.
- **Reranking Model**: **2 parallel rerank calls** available (`HINDSIGHT_API_RERANKER_MAX_CONCURRENT=2`), **16,384 (16K) max context window**.

By setting strict concurrency caps across global, reflection, retention, and consolidation scopes, Hindsight avoids VRAM exhaustion, prompt thrashing, and KV cache eviction on local GPU endpoints while maintaining low-latency background memory indexing.

---

## Knob Catalog (Configuration Reference)

| Knob Name | Default (Cloud) | Local Default | Description | Rationale for Local Setup |
| :--- | :---: | :---: | :--- | :--- |
| **`HINDSIGHT_API_LLM_TIMEOUT`** | `120` | `180` | Client HTTP timeout for LLM requests (seconds). | Gives local GPUs up to 3 minutes for initial pre-fill and decode. |
| **`HINDSIGHT_API_LLM_MAX_CONCURRENT`** | `32` | `2` | Global cap on simultaneous LLM requests. | Matches 2 parallel LLM slots available for memory operations. |
| **`HINDSIGHT_API_LLM_REASONING_EFFORT`** | `medium` | `low` | Reasoning effort for supporting models (`low`, `medium`, `high`). | Reduces thinking token overhead in background summarization. |
| **`HINDSIGHT_API_RECALL_MAX_CONCURRENT`** | `32` | `2` | Cap on concurrent embedding requests during recall/retain. | Matches 2 parallel slots supported by 8K embedding model. |
| **`HINDSIGHT_API_RECALL_INCLUDE_CHUNKS`** | `true` | `false` | Pull raw text chunks alongside facts during recall. | Disabling raw chunks cuts memory payload size by ~50%. |
| **`HINDSIGHT_API_RECALL_MAX_TOKENS`** | `2048` | `1536` | Token budget for facts returned by internal recall. | Keeps context light; fits comfortably inside 8K embedding / 16K reranker bounds. |
| **`HINDSIGHT_API_RECALL_CHUNKS_MAX_TOKENS`** | `1000` | `500` | Token budget for chunks if `include_chunks=true`. | Backup budget kept small to limit VRAM usage if chunks enabled. |
| **`HINDSIGHT_API_RERANKER_MAX_CONCURRENT`** | `32` | `2` | Cap on concurrent reranking requests. | Matches 2 parallel slots supported by 16K cross-encoder reranker. |
| **`HINDSIGHT_API_REFLECT_WALL_TIMEOUT`** | `300` | `600` | Overall wall-clock timeout for background reflect job (seconds). | Allows deep multi-step reflection synthesis to finish without aborting. |
| **`HINDSIGHT_API_REFLECT_MAX_CONTEXT_TOKENS`** | `100000` | `65536` | Strict cap on total tokens fed to a single reflection pass. | Prevents VRAM spikes from massive context bursts. |
| **`HINDSIGHT_API_REFLECT_LLM_MAX_CONCURRENT`** | `32` | `2` | LLM concurrency cap specifically for reflection phase. | Allows up to 2 parallel reasoning passes during reflection loops. |
| **`HINDSIGHT_API_REFLECT_LLM_TIMEOUT`** | `120` | `300` | LLM HTTP request timeout during reflection (seconds). | Accommodates multi-step agent reasoning passes. |
| **`HINDSIGHT_API_RETAIN_LLM_MAX_CONCURRENT`** | `32` | `2` | Concurrent LLM threads for interaction ingestion. | Enables up to 2 parallel retention extraction streams. |
| **`HINDSIGHT_API_FILE_DELETE_AFTER_RETAIN`** | `false` | `false` | Automatically delete uploaded binary files after parsing. | Prevents storage accumulation when processing raw uploads. |
| **`HINDSIGHT_API_DISPOSITION_SKEPTICISM`** | `3` | `3` | Memory fact skepticism level (1–5). | Standard balanced fact retention. |
| **`HINDSIGHT_API_DISPOSITION_LITERALISM`** | `3` | `3` | Memory fact literalness score (1–5). | Standard literal assertion mapping. |
| **`HINDSIGHT_API_DISPOSITION_EMPATHY`** | `3` | `4` | Memory fact empathy weighting (1–5). | Slightly elevated to capture interpersonal/agent context. |
| **`HINDSIGHT_API_CONSOLIDATION_RECALL_BUDGET`** | `medium` | `low` | Token retrieval density for memory consolidation. | Reduces CPU/GPU overhead by fetching high-scoring memories only. |
| **`HINDSIGHT_API_CONSOLIDATION_SOURCE_FACTS_MAX_TOKENS`** | `4096` | `4096` | Max facts tokens retrieved when grouping memories. | Evaluates a rich set of facts during background merges. |
| **`HINDSIGHT_API_CONSOLIDATION_SOURCE_FACTS_MAX_TOKENS_PER_OBSERVATION`** | `256` | `256` | Token limit for individual facts when summarizing. | Preserves clear boundaries inside memory graphs. |
| **`HINDSIGHT_API_CONSOLIDATION_LLM_MAX_CONCURRENT`** | `32` | `1` | Concurrency cap for background consolidation routines. | Enforces serial background consolidation so it doesn't starve the 2 LLM slots. |
| **`HINDSIGHT_API_CONSOLIDATION_LLM_BATCH_SIZE`** | `8` | `2` | Batch size of LLM operations in consolidation. | Prevents VRAM pre-fill spikes by processing smaller batches. |
| **`HINDSIGHT_API_CONSOLIDATION_MAX_MEMORIES_PER_ROUND`** | `50` | `20` | Max memories evaluated in one consolidation sweep. | Prevents large document dumps from overwhelming background loops. |

---

## Additional Hygiene & Security Knobs

### 1. Disk & Memory Hygiene
- **`HINDSIGHT_API_FILE_DELETE_AFTER_RETAIN=false`** (Default: `false`)
  - Once a file (e.g. PDF/TXT) has been ingested, parsed, and its memories extracted, setting this to `true` immediately cleans up source binary uploads to save local disk space.

### 2. Security & MCP Access
- **`HINDSIGHT_API_AUTH_ENABLED=false`** (Default: `false`)
  - Enforces API key authentication when Hindsight is exposed on LAN or multi-user networks.
- **`HINDSIGHT_API_MCP_AUTH_TOKEN=""`** (Default: `""`)
  - Authentication token securing the Model Context Protocol (MCP) socket from unauthorized client tools.
