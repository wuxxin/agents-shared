# Hindsight Configuration & Tuning Guide

This document provides a consolidated reference for configuring the **Hindsight Memory Service** (`local-memory.sh`) for local inference deployments.

## Hindsight Memory Usage Patterns & Serving Recommendations

Hindsight relies heavily on embedding and reranking services for memory recall, consolidation, and reflection. The memory system delegates these computations to external models served locally or remotely.

#### Typical Hindsight Workloads
1. **RECALL (Fact Retrieval)**:
   - **Mechanism**: Initiates a 4-way parallel search strategy per requested fact type (`world`, `experience`, `observation`): **Semantic (dense embedding)**, **Keyword (BM25)**, **Graph (entity-link activation)**, and **Temporal (recency/time-decay)**.
   - **Fusion**: Combines the retrieved candidates using Reciprocal Rank Fusion (RRF).
   - **Reranker Input**: Fused candidates are capped to `reranker_max_candidates` (default: **300**) before being sent to the cross-encoder to limit expensive inference steps.
   - **Final Cut**: Results are filtered up to a token budget `max_tokens` (default: **4096** for general recall, **2048** for reflection agent queries, and **512** for consolidation).
2. **REFLECT (Agent-Driven Reasoning)**:
   - **Mechanism**: The reflection agent executes reasoning steps using multiple tools:
     - `tool_search_observations`: Searches consolidated memory observations via semantic recall (`max_tokens = 5000`).
     - `tool_recall`: Performs raw fact retrieval (`max_tokens = 2048`, `max_chunk_tokens = 1000`) for ground-truth verification.
     - `tool_search_mental_models`: Searches high-level synthesized summaries via SQL cosine similarity (`max_results = 5`).
3. **CONSOLIDATION & MENTAL MODEL REGENERATION**:
   - **Mechanism**: Background workers periodically group memories (default batch size: **8**, max memories: **100** per round).
   - **Consolidation Recall**: Uses `budget=low`, `max_tokens=512`, `include_source_facts=True` (`max_source_facts_tokens_per_observation=256`), and `reranking="interleave"`. *Note:* Interleave fusion bypasses the cross-encoder entirely to prevent demoting near-identical existing observations.
   - **Observation deduplication**: Embedding cosine similarity between observations is computed. A similarity score $\ge$ `DEFAULT_CONSOLIDATION_DEDUP_THRESHOLD = 0.97` triggers a focused 1-on-1 LLM pass to merge or keep the observations.
   - **Regeneration**: Regenerated mental models require fresh embeddings generated via the embedding model before being written back to the database.

#### Chat/Completion Serving & Throughput Recommendations

Chat and text completion in Hindsight are used for fact extraction during **Retain**, agent reasoning loops during **Reflect**, and fact-merging/summarization during **Consolidation**.

* **Concurrency & Parallel Access**:
  - **Remote Endpoints**: When using a remote API (e.g. OpenAI `gpt-4o-mini`, Gemini `gemini-1.5-flash`), parallel requests scale natively up to **32 concurrent requests** (governed by `HINDSIGHT_API_LLM_MAX_CONCURRENT=32`).
  - **Local Endpoints**: When running a local LLM (e.g. `Qwen3.6-35B-A3B` via `llama-server`), VRAM is heavily constrained by KV cache requirements. It is critical to set background concurrency caps to **1** (`HINDSIGHT_API_LLM_MAX_CONCURRENT=1`, `HINDSIGHT_API_REFLECT_LLM_MAX_CONCURRENT=1`, `HINDSIGHT_API_RETAIN_LLM_MAX_CONCURRENT=1`, and `HINDSIGHT_API_CONSOLIDATION_LLM_MAX_CONCURRENT=1`). This prevents parallel pipeline pre-fill spikes, VRAM exhaustion, and context prompt-swapping, reserving remaining slots of the unified KV cache (e.g., 240k Unified KV Cache serving 3 parallel sessions) for the active user chat.
* **Batch Size & Pipeline Depth**:
  - **Local Ingestion/Consolidation**: During memory consolidation, setting the LLM operations batch size to a low value (e.g. `HINDSIGHT_API_CONSOLIDATION_LLM_BATCH_SIZE=2`, down from default `8`) limits VRAM spikes during pre-fill. This restricts the number of concurrent generation queries dispatched to the LLM engine in a single background consolidation sweep.
  - **Local llama-server configurations**: Specify parameters like `--batch-size` and `--ubatch-size` to match or divide KV-cache slots. This ensures stable prompt-processing throughput and prevents hardware thrashing under concurrent client activity.
* **Context Size Recommendations**:
  - **Expected Robust Context**: **8,192 (8K) tokens**. The minimum required context length to prevent prompt truncation during basic memory updates and small ingestion runs.
  - **Expected Good Context**: **32,768 (32K) tokens**. Necessary for RAG workloads to bundle retrieved memories, observations, and entity relationships alongside conversation history.
  - **Luxury Context**: **131,072 (131K) tokens** (or higher). Highly recommended for the reflection agent (`reflect` endpoint has a strict cap `HINDSIGHT_API_REFLECT_MAX_CONTEXT_TOKENS=65536` to avoid VRAM explosion). A luxury context window allows Hindsight to evaluate months of historical interactions and large observation tables in a single reasoning pass.
  - **Impact of Context Shrinkage (< 8K)**: If context falls below 8K (e.g. 1K–4K), the multi-turn reflection agent will exhaust its context window within 1–2 tool calls (leading to crashes or hallucinations), and background consolidation prompts will overflow, causing failed merges and memory duplication.
* **Throughput Optimization**:
  - **Reasoning Overhead**: Minimize unnecessary reasoning token overhead by setting `HINDSIGHT_API_LLM_REASONING_EFFORT=low` to speed up background fact ingestion and synthesis.
  - **Timeouts**: Tune client HTTP timeouts to allow slower local GPU pre-fills and decode phases to complete without aborting (e.g. `HINDSIGHT_API_LLM_TIMEOUT=180` seconds for general tasks, and `HINDSIGHT_API_REFLECT_LLM_TIMEOUT=300` / `HINDSIGHT_API_REFLECT_WALL_TIMEOUT=600` seconds for long-running reflection consolidation).


#### Embedding Serving & Throughput Recommendations

Embedding generation in Hindsight is used for query embedding during **Recall**, chunk ingestion during **Retain** (`DEFAULT_RETAIN_CHUNK_SIZE=3000` chars, ~500–750 tokens), observation deduplication, and mental model updates.

* **Concurrency & Parallel Access**:
  - **Remote Endpoints**: When using a remote API (e.g. OpenAI `text-embedding-3-small` or Gemini `gemini-embedding-001`), parallel requests scale natively up to **32 concurrent requests** (governed by `HINDSIGHT_API_RECALL_MAX_CONCURRENT=32`).
  - **Local Endpoints**: If served locally via `llama-server` (e.g. Qwen3-Embedding GGUF), VRAM is optimized using `LMBD_PARALLEL=2` slots and `q8_0` KV cache. `llama-server` always pre-allocates a KV cache per slot (even for embedding-only workloads), which limits high local concurrency. Standalone TEI instances run a single forward pass without any KV cache allocation, enabling higher parallel local dispatches (see [Architecture & KV Cache reference](#embedding-model-architectures-attention-kv-cache--vram-scaling)).
* **Batch Size & Processing Throughput**:
  - **Remote Batching**: APIs like OpenAI batch multiple text inputs into a single request (default: `100` texts per batch). This reduces network latency and transaction overhead significantly.
  - **Local llama-server configurations**: Set the batch size to match the context size (e.g. `--batch-size 16384`) to allow processing long document ingestions in a single pre-fill/batch pass.
  - **TEI Dynamic Batching**: Standalone TEI instances dynamically pack queries up to `--max-batch-size 32` or `64`. Since embeddings are computed independently per chunk, packing them fully saturates GPU tensor cores without VRAM penalty.
* **Context Size Recommendations**:
  - **Expected Robust Context**: **8,192 (8K) tokens**. More than sufficient for standard chunk ingestion (~500–750 tokens) and query embeddings.
  - **Expected Good / Luxury Context**: **32,768 (32K) tokens**. This allows embedding extremely large text files or raw code documents without needing pre-chunking.
  - **Impact of Context Shrinkage (< 8K)**: If context is limited to 1K–4K, long documents or massive chunks during the `Retain` phase will be forcefully truncated, leading to information loss and broken memory semantics.
* **Optimizing Speed for Local/TEI Serving**:
  - Since encoder-based embedding models (e.g. `BGE-M3`, `Jina v3`) do not use a KV cache, VRAM footprint is static (~1.2 GB). They are entirely **compute-bound (ALU/memory bandwidth)**.
  - Set TEI `--max-batch-size` to **32** or **64** and `--max-concurrent-requests` to **32** to maximize GPU utilization via parallel processing.


#### Reranking Serving & Throughput Recommendations

Reranking in Hindsight is used exclusively in the final stage of **Recall** to compute cross-attention over query-document pairs for the top `reranker_max_candidates` (default: 300) candidates. It is computationally heavy compared to embeddings.

* **Concurrency & Parallel Access**:
  - **Remote Endpoints**: Remote reranking (e.g. Cohere Rerank or remote TEI) permits up to **32** parallel sessions.
  - **Local Endpoints**: Local cross-encoders are extremely CPU/GPU intensive. Thus, local concurrency is strictly capped by default: CPU-bound cross-encoders are restricted to `DEFAULT_RERANKER_LOCAL_MAX_CONCURRENT=4` to prevent CPU thrashing; local TEI servers default to `DEFAULT_RERANKER_TEI_MAX_CONCURRENT=8`.
* **Batch Size & Processing Throughput**:
  - **Local Cross-Encoders**: Capped at `DEFAULT_RERANKER_LOCAL_BATCH_SIZE=32` to prevent CPU/GPU core thrashing during high-load candidate evaluation.
  - **TEI Instances**: Standalone TEI servers are configured with `DEFAULT_RERANKER_TEI_BATCH_SIZE=128`. Evaluating up to 300 candidates in large batch chunks allows maximum GPU parallel computation.
  - **Length-Sorted Bucket Batching**: Combined with batching, enabling bucket batching (`HINDSIGHT_API_RERANKER_LOCAL_BUCKET_BATCHING=true` or TEI dynamic sequence-length batching) ensures documents are sorted by length before being grouped. This eliminates unnecessary padding token computation and boosts cross-encoder throughput by **36% to 54%**.
* **Context Size Recommendations**:
  - **Expected Robust Context**: **16,384 (16K) tokens**. Necessary to accommodate the sequence concatenation of `query + document` for 300 candidates.
  - **Expected Good Context**: **32,768 (32K) tokens**. Essential for reranking long raw chunks or observation lists with embedded source facts.
  - **Luxury Context**: **131,072 (131K) tokens**. Enables listwise cross-attention over dozens of large documents simultaneously (e.g. Jina Reranker v3's LBNL architecture) without sequence clipping.
  - **Impact of Context Shrinkage (< 16K)**: If the reranker context window drops below 16K tokens (or below 8K), query-document sequences are truncated, causing the model to score based on partial text. This results in poor ranking, burying high-relevance observations, and causing the LLM to hallucinate or miss relevant facts.
* **Optimizing Speed for Local/TEI Serving**:
  - Since cross-encoders (e.g. `BGE-Reranker-v2-m3`, `Jina-Reranker-v2`) do not use a KV cache, their GPU footprint is static and stable under load.
  - **Precision & Quantization**: Enable `--quantize bitsandbytes` (INT8) or serve weights in `float16`/`bfloat16` to maximize memory bandwidth.

---

#### Hindsight Four Memory Buckets & Median Context Usage

Hindsight partitions memory into 4 major categories ("buckets") with distinct median sizes:
- **World facts**: General/universal assertions. Median size: **~50–150 tokens** per fact.
- **Experience facts**: Narrative/episodic memory. Median size: **~100–300 tokens** per fact.
- **Observations**: Consolidated facts derived from raw memory. Median size: **~150–400 tokens** per observation.
- **Mental models**: High-level consolidated summaries. Median size: **~500–1,500 tokens** per mental model.

Median context sizes active across different Hindsight operations:
- *Ingestion (Retain)*: Text chunks default to `DEFAULT_RETAIN_CHUNK_SIZE=3000` characters (approx. **500–750 tokens**).
- *Fact Recall*: Fetches memories up to 4096 tokens, yielding a median context payload of **1,000–2,500 tokens** to the LLM.
- *Consolidation*: Queries observations up to 512 tokens (median context **300–400 tokens**).
- *Agent Reflection*: Enforces a hard limit of `HINDSIGHT_API_REFLECT_MAX_CONTEXT_TOKENS=65536` tokens (default: 100k), processing a median context of **10,000–30,000 tokens** of conversational history, observations, and retrieved facts.

---


## Hardware & Backend Capacity Model

The default configuration is tuned for a local inference environment with the following concurrency and context boundaries:

With our current setup, we are only able to support 2 parallel chat, and 1 8k embedding and 1 16K rerank call. 

- **Chat/Vision LLM**: **2 parallel LLM calls** available for Hindsight tasks (`HINDSIGHT_API_LLM_MAX_CONCURRENT=2`).
- **Embedding Model**: **1 parallel embedding calls** available (`HINDSIGHT_API_RECALL_MAX_CONCURRENT=1`), **8,192 (8K) max context window**.
- **Reranking Model**: **1 parallel rerank calls** available (`HINDSIGHT_API_RERANKER_MAX_CONCURRENT=1`), **16,384 (16K) max context window**.

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
