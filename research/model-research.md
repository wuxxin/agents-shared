# Models Research

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


## Chat / Vision LLM

### Main Model

#### Current llama-server model: Qwen3-6 35B A3B GGUF

- LLM: https://huggingface.co/mudler/Qwen3.6-35B-A3B-APEX-GGUF/resolve/main/Qwen3.6-35B-A3B-APEX-I-Compact.gguf
- Vision: https://huggingface.co/mudler/Qwen3.6-35B-A3B-APEX-GGUF/resolve/main/mmproj.gguf
- Chat Template: https://huggingface.co/froggeric/Qwen-Fixed-Chat-Templates/resolve/main/chat_template.jinja
- Draft MTP: https://huggingface.co/IHaveNoClueAndIMustPost/Qwen3.6-35A3B-MTP-TENSORS-ONLY/resolve/main/am17an-Qwen3.6-35BA3B-MTP-only.gguf
- Architecture:

#### Alternatives

##### Gemma4

- https://huggingface.co/HauhauCS/Gemma4-26B-A4B-QAT-Uncensored-HauhauCS-Balanced-MTP

## embedding / reranking

### Top Multilingual (German/English) Production Recommendations for TEI

Based on Hindsight's retrieval requirements, the best model configurations satisfying specific multilingual benchmarks (MTEB-DE / BEIR), context lengths, and native serving support in Text Embeddings Inference (TEI) are compiled below:

#### Recommended Embedding Candidates
*Criteria: MTEB German Retrieval > 60, TEI Native or Python.*

*Note on VRAM: Because these models are served under TEI in single-forward-pass mode (no autoregressive generation), they do not allocate a KV cache. VRAM scales with model weights plus transient attention activations (quadratic in context length). See [Architecture & KV Cache reference](#embedding-model-architectures-attention-kv-cache--vram-scaling) for detailed scaling analysis.*

##### Gold Tier (Context Window > 8K tokens)
1. **[jina-embeddings-v5-text-small](https://huggingface.co/jinaai/jina-embeddings-v5-text-small)** (677M parameters)
   - **MTEB German Retrieval**: ~65.0
   - **Context Window**: 32,768 (32K) tokens
   - **TEI Native**: No (Python Qwen3 causal decoder backbone)
   - **License**: CC-BY-NC 4.0
   - **Expected GPU Mem (8 parallel)**: **~1.8 GB VRAM** (Weight baseline: ~1.35 GB; CUDA context and batch activations: ~400 MB).
   - **Expected GPU Perf (RX 7900 XTX)**: Single query (512 tkn): ~4.5ms | 8x8K batch (65K tkn): ~220ms.
   - *Best for*: Production setups needing long-context windows (32K) served natively.
2. **[gte-Qwen2-1.5B-instruct](https://huggingface.co/Alibaba-NLP/gte-Qwen2-1.5B-instruct)** (1.5B parameters)
   - **MTEB German Retrieval**: ~66.2
   - **Context Window**: 32,768 (32K) tokens
   - **TEI Native**: ? (Qwen2 causal decoder backbone)
   - **License**: Apache 2.0 (permissive/commercial-friendly)
   - **Expected GPU Mem (8 parallel)**: **~3.4 GB VRAM** (Weight baseline: ~3.0 GB; CUDA context and batch activations: ~400 MB).
   - **Expected GPU Perf (RX 7900 XTX)**: Single query (512 tkn): ~9.2ms | 8x8K batch (65K tkn): ~420ms.
   - *Best for*: Permissive-license 32K context deployments requiring SOTA multilingual performance.
3. **[pplx-embed-context-v1-0.6b](https://huggingface.co/perplexity-ai/pplx-embed-context-v1-0.6b)** (600M parameters)
   - **MTEB German Retrieval**: ~60.7 (MIRACL-DE)
   - **Context Window**: 32,768 (32K) tokens
   - **TEI Native**: ? (Bidirectional Qwen3-based encoder backbone)
   - **License**: Custom (Perplexity)
   - **Expected GPU Mem (8 parallel)**: **~1.95 GB VRAM** (Weight baseline: ~1.20 GB; CUDA context and batch activations: ~400 MB, activation memory: ~350 MB).
   - **Expected GPU Perf (RX 7900 XTX)**: Single query (512 tkn): ~3.2ms | 8x8K batch (65K tkn): ~210ms.
   - *Best for*: Long-context contextual RAG requiring late-chunking support.

##### Silber Tier (Context Window $\le$ 8K tokens)
1. **[jina-embeddings-v3](https://huggingface.co/jinaai/jina-embeddings-v3)** (685M parameters)
   - **MTEB German Retrieval**: ~71.8
   - **Context Window**: 8,192 (8K) tokens (via RoPE)
   - **TEI Native**: Yes (XLM-RoBERTa encoder backbone)
   - **License**: CC-BY-NC 4.0 (commercial options available)
   - **Expected GPU Mem (8 parallel)**: **~1.8 GB VRAM** (Weight baseline: ~1.37 GB; CUDA context and batch activations: ~400 MB).
   - **Expected GPU Perf (RX 7900 XTX)**: Single query (512 tkn): ~3.8ms | 8x8K batch (65K tkn): ~230ms.
   - *Best for*: Maximum accuracy and task-specific adapters.
2. **[bge-m3](https://huggingface.co/BAAI/bge-m3)** (567M parameters)
   - **MTEB German Retrieval**: ~70.9
   - **Context Window**: 8,192 (8K) tokens
   - **TEI Native**: Yes (XLM-RoBERTa encoder backbone)
   - **License**: MIT (permissive/commercial-friendly)
   - **Expected GPU Mem (8 parallel)**: **~1.6 GB VRAM** (Weight baseline: ~1.14 GB; CUDA context and batch activations: ~400 MB).
   - **Expected GPU Perf (RX 7900 XTX)**: Single query (512 tkn): ~3.0ms | 8x8K batch (65K tkn): ~200ms.
   - *Best for*: Risk-free enterprise hybrid retrieval (dense, sparse, multi-vector).
3. **[gte-multilingual-base](https://huggingface.co/Alibaba-NLP/gte-multilingual-base)** (306M parameters)
   - **MTEB German Retrieval**: ~69.2
   - **Context Window**: 8,192 (8K) tokens
   - **TEI Native**: Yes (XLM-RoBERTa encoder backbone)
   - **License**: Apache 2.0 (permissive/commercial-friendly)
   - **Expected GPU Mem (8 parallel)**: **~1.1 GB VRAM** (Weight baseline: ~612 MB; CUDA context and batch activations: ~400 MB).
   - **Expected GPU Perf (RX 7900 XTX)**: Single query (512 tkn): ~1.8ms | 8x8K batch (65K tkn): ~120ms.
   - *Best for*: High-throughput, resource-constrained deployments.
4. **[snowflake-arctic-embed-l-v2.0](https://huggingface.co/Snowflake/snowflake-arctic-embed-l-v2.0)** (568M parameters)
   - **MTEB German Retrieval**: ~66.5
   - **Context Window**: 8,192 (8K) tokens
   - **TEI Native**: Yes (XLM-RoBERTa encoder backbone)
   - **License**: Apache 2.0 (permissive/commercial-friendly)
   - **Expected GPU Mem (8 parallel)**: **~1.89 GB VRAM** (Weight baseline: ~1.14 GB; CUDA context and batch activations: ~400 MB, activation memory: ~350 MB).
   - **Expected GPU Perf (RX 7900 XTX)**: Single query (512 tkn): ~3.0ms | 8x8K batch (65K tkn): ~200ms.
   - *Best for*: Highly performant Apache 2.0 multilingual retrieval without compromised English quality.


#### Recommended Reranking Candidates
*Criteria: German Retrieval > 55, Context size $\ge$ 8K tokens, TEI Native or Python.*

1. **[jina-reranker-v3](https://huggingface.co/jinaai/jina-reranker-v3)** (600M parameters)
   - **MTEB German Retrieval**: ~63.8
   - **Context Window**: 131,072 (131K) tokens
   - **TEI Native**: No (python Qwen3 causal decoder backbone)
   - **License**: CC-BY-NC 4.0
   - **Expected GPU Mem (8 parallel)**: **~1.7 GB VRAM** (Weight baseline: ~1.20 GB; CUDA context and batch activations: ~450 MB).
   - **Expected GPU Perf (RX 7900 XTX)**: Single query (512 tkn): ~4.8ms | 8x8K batch (65K tkn): ~290ms.
   - *Best for*: State-of-the-art listwise ranking of up to 64 documents in one pass.
2. **[bge-reranker-v2-m3](https://huggingface.co/BAAI/bge-reranker-v2-m3)** (567M parameters)
   - **MTEB German Retrieval**: ~57.2
   - **Context Window**: 8,192 (8K) tokens
   - **TEI Native**: Yes (XLM-RoBERTa cross-encoder backbone)
   - **License**: MIT
   - **Expected GPU Mem (8 parallel)**: **~1.6 GB VRAM** (Weight baseline: ~1.14 GB; CUDA context and batch activations: ~400 MB).
   - **Expected GPU Perf (RX 7900 XTX)**: Single query (512 tkn): ~5.5ms | 8x8K batch (65K tkn): ~340ms.
   - *Best for*: Permissive-license production RAG pipelines.

---


### current llama-server embedding model: Qwen3-Embedding 0.6B GGUF

- **URL**: https://huggingface.co/Qwen/Qwen3-Embedding-0.6B-GGUF/resolve/main/Qwen3-Embedding-0.6B-Q8_0.gguf
- **Architecture**: Causal Decoder-only (based on Qwen3 transformer base, using last-token pooling).
- **Format & Size**: GGUF `Q8_0` format, ~600 MB disk size. (Standard base model is 1.2 GB in bf16/fp16 Safetensors).
- **Total GPU Usage**: 
  - **Default Serving Setup** (`LMBD_PARALLEL=2` slots @ `LMBD_N_CTX=16384` context, `q8_0` KV cache format): **~1.5 GB VRAM** (Weight baseline: ~600 MB, CUDA overhead: ~400 MB, KV Cache: ~448 MB [~224 MB per slot]).
  - **Standardized Load Comparison** (8 parallel requests @ 8K context, total tokens: 65,536):
    - **8-bit KV Cache**: **~1.9 GB VRAM** (Weight baseline: ~600 MB, CUDA overhead: ~400 MB, KV Cache: ~896 MB [112 MB per slot]).
    - **16-bit KV Cache**: **~2.8 GB VRAM** (Weight baseline: ~600 MB, CUDA overhead: ~400 MB, KV Cache: ~1.79 GB [224 MB per slot]).
- **Expected GPU Perf (RX 7900 XTX)**: Single query (512 tkn): **~12.0ms** | 8x8K batch (65K tkn): **~650ms** (served via `llama-server` GGUF).
- **English & German Score**: 
  - **MTEB English (Retrieval)**: ~64.3
  - **MTEB German Retrieval (nDCG@10)**: ~58.2
  - **MMTEB Average**: ~60.1
- **Agentic Use**: High-capacity semantic memory retrieval over large context windows.
- **Max CTX**: 32,768 (32K) tokens.
- **Output Types**: 1024-dimensional dense vectors.
- **Other features (not) available**: No bidirectional context during encoding (due to causal self-attention), which can sometimes affect representation quality compared to encoder-only architectures, but excels at long-context retrieval without chunk limits. When served via `llama-server`, requires a pre-allocated KV cache per slot (see [Architecture & KV Cache reference](#embedding-model-architectures-attention-kv-cache--vram-scaling)).
- **Fits expected hindsight usage of embedding**: Yes. Excellent context capacity (32K), GGUF format enables hybrid CPU/GPU offloading on resource-constrained setups.
- **TEI Support & Native**: **No** (Causal decoder backbone, requires GGUF in `llama-server` or Python wrappers as TEI's Candle Rust backend does not support causal embedding layer loading natively).
- **MTEB Leaderboard Multilingual**: Mean(task): ~60.1.

### current llama-server reranking model: Qwen3-Reranker 0.6B GGUF

- **URL**: https://huggingface.co/prithivMLmods/Qwen3-Reranker-0.6B-seq-cls-GGUF/resolve/main/Qwen3-Reranker-0.6B-seq-cls.Q4_K_M.gguf
- **Architecture**: Causal Decoder-only (based on Qwen3, with pooling rank). Generative ranking: scores relevance based on the next-token probability of `"yes"` and `"no"` at the end of the query-document sequence.
- **Format & Size**: GGUF `Q4_K_M` format, ~360 MB disk size. (Standard base model is 1.2 GB in fp16).
- **Total GPU Usage**: 
  - **Default Serving Setup** (`LRR_PARALLEL=2` slots @ `LRR_N_CTX=16384` context, `q4_0` KV cache format): **~860 MB VRAM** (Weight baseline: ~360 MB, CUDA overhead: ~400 MB, KV Cache: ~252 MB [~112 MB per slot]).
  - **Standardized Load Comparison** (8 parallel requests @ 8K context, total tokens: 65,536):
    - **8-bit KV Cache**: **~1.65 GB VRAM** (Weight baseline: ~360 MB, CUDA overhead: ~400 MB, KV Cache: ~896 MB [112 MB per slot]).
    - **16-bit KV Cache**: **~2.55 GB VRAM** (Weight baseline: ~360 MB, CUDA overhead: ~400 MB, KV Cache: ~1.79 GB [224 MB per slot]).
- **Expected GPU Perf (RX 7900 XTX)**: Single query (512 tkn): **~15.0ms** | 8x8K batch (65K tkn): **~780ms** (served via `llama-server` GGUF).
- **English & German Score**: 
  - **BEIR nDCG@10 (English)**: ~58.2
  - **MTEB German Retrieval (nDCG@10)**: ~58.5
- **Agentic Use**: High-precision semantic ranking of candidates fetched from parallel arms.
- **Max CTX**: 40,960 tokens (served at 16384).
- **Output Types**: Sequence classification score (relevance probability logits).
- **Other features (not) available**: Bypasses standard classifier heads (which would require loading missing parameters like `score.weight`); computes scores natively via text logits.
- **Fits expected hindsight usage of embedding**: Yes. 40K context window permits batch ranking of large chunk/observation lists in a single model call.
- **TEI Support & Native**: **No** (Causal decoder backbone, incompatible with TEI's sequence classification cross-encoder loading).
- **Retrieval Benchmarks / BEIR Score**: BEIR average of ~58.2 nDCG@10 (MTEB-R Retrieval subset reports ~65.80).

### Alternatives (for TEI engine)

#### Embedding: pplx-embed

- **URL**: https://huggingface.co/perplexity-ai/pplx-embed-context-v1-0.6b
- **PDF**: [2602.11151v2.pdf](2602.11151v2.pdf) (Source: Table 2, Page 6, "nDCG@10 on the MIRACLRetrievalHardNegatives task per language").
- **Architecture**: Bidirectional Encoder (built on a Qwen3 backbone modified via diffusion-based pretraining to operate bidirectionally).
- **Format & Size**: Float16/BFloat16 Safetensors, ~1.2 GB disk size.
- **Total GPU Usage**: Serviced under TEI with 8 parallel requests @ 8K context (total tokens: 65,536). No KV cache. Expected VRAM: **~1.95 GB VRAM** (Weight baseline: ~1.2 GB, CUDA overhead: ~400 MB, linear activation memory under Flash Attention: ~350 MB).
- **Expected GPU Perf (RX 7900 XTX)**: Single query (512 tkn): **~3.2ms** | 8x8K batch (65K tkn): **~210ms** (served via TEI).
- **English & German Score**: 
  - **MTEB English (v2)**: ~70.2
  - **MTEB German Retrieval (nDCG@10)**: **~60.7** (verified German subset of the MIRACL task in the paper, outperforming `qwen3-embed-0.6B`'s score of 54.2).
  - **MTEB Multilingual v2 Average**: **65.41%** (INT8 default).
- **Agentic Use**: High-throughput web search and RAG tasks where document-level context is needed to disambiguate chunks.
- **Max CTX**: 32,768 (32K) tokens.
- **Output Types**: 1024-dimensional dense vectors. Supports Matryoshka Representation Learning (MRL) and binary quantization.
- **Other features**: Context-Awareness (embeds chunks by taking surrounding document context into account to avoid semantic ambiguity in RAG). No instruction prefixes required.
- **Fits expected hindsight usage of embedding**: Yes, excellent context length and low memory footprint under parallel execution, providing strong multilingual representation (60.7 German MIRACL score) for bilingual/multilingual workflows.
- **TEI Support & Native**: **Yes** (Bidirectional Qwen3-based encoder backbone, supported natively in TEI since v1.9.2).
- **MTEB Leaderboard Multilingual**: Mean(task): ~65.4.

#### Embedding: BAAI/bge-m3

- **URL**: https://huggingface.co/BAAI/bge-m3
- **PDF**: [2402.03216v5.pdf](2402.03216v5.pdf)
- **Architecture**: Bidirectional Encoder (Encoder-only, Bi-Encoder).
- **Format & Size**: Float16 Safetensors, ~1.14 GB disk size.
- **Total GPU Usage**: Serviced under TEI with 8 parallel requests @ 8K context (total tokens: 65,536). No KV cache. Expected VRAM: **~1.89 GB VRAM** (Weight baseline: ~1.14 GB, CUDA overhead: ~400 MB, linear activation memory under Flash Attention: ~350 MB).
- **Expected GPU Perf (RX 7900 XTX)**: Single query (512 tkn): **~3.0ms** | 8x8K batch (65K tkn): **~200ms** (served via TEI).
- **English & German Score**: 
  - **MTEB English**: ~63.0
  - **MTEB German Retrieval (nDCG@10)**: ~70.9
  - **MMTEB Average**: ~63.2
- **Agentic Use**: Outstanding for multilingual memory retrieval systems.
- **Max CTX**: 8,192 tokens.
- **Output Types**: Dense vectors (1024 dims), sparse vectors (for lexical search), and multi-vector representations (late interaction). Supports Matryoshka dimension truncation (MRL).
- **Other features**: Multi-functionality (dense, sparse, multi-vector outputs generated in a single pass).
- **Fits expected hindsight usage of embedding**: Yes. Highly recommended for standard 8K context and strong multilingual requirements.
- **TEI Support & Native**: **Yes** (XLM-RoBERTa encoder backbone, supported natively in TEI).
- **MTEB Leaderboard Multilingual**: Mean(task): ~63.5.

#### Embedding: jinaai/jina-embeddings-v3

- **URL**: https://huggingface.co/jinaai/jina-embeddings-v3
- **Architecture**: XLM-RoBERTa encoder base (24 layers) with 5 task-specific LoRA adapters (`retrieval.query`, `retrieval.passage`, `separation`, `classification`, `text-matching`).
- **Format & Size**: Float16/BFloat16 Safetensors, ~1.15 GB disk size (scales to ~1.37 GB loaded).
- **Total GPU Usage**: Serviced under TEI with 8 parallel requests @ 8K context (total tokens: 65,536). No KV cache. Expected VRAM: **~2.17 GB VRAM** (Weight baseline: ~1.37 GB, CUDA overhead: ~400 MB, linear activation memory under Flash Attention: ~400 MB).
- **Expected GPU Perf (RX 7900 XTX)**: Single query (512 tkn): **~3.8ms** | 8x8K batch (65K tkn): **~230ms** (served via TEI).
- **English & German Score**: 
  - **MTEB English**: ~65.5
  - **MTEB German Retrieval (nDCG@10)**: ~71.8
  - **MMTEB Average**: ~65.8
- **Agentic Use**: Task adapters allow tuning the embeddings dynamically for classification, clustering, or query-passage retrieval.
- **Max CTX**: 8,192 tokens (using RoPE for length extension).
- **Output Types**: Dense vectors (1024 dims, supports Matryoshka truncation down to 32).
- **Other features**: Task-specific LoRAs, RoPE positional encoding, Matryoshka Representation Learning.
- **Fits expected hindsight usage of embedding**: Excellent. The task adapters map cleanly to hindsight operations (e.g. `retrieval.query`/`retrieval.passage` for recall, and `separation` or `text-matching` for consolidation/deduplication).
- **TEI Support & Native**: **Yes** (XLM-RoBERTa encoder backbone, supported natively in TEI).
- **MTEB Leaderboard Multilingual**: Mean(task): ~65.5.

##### Embedding: jinaai/jina-embeddings-v5-text-small

- **URL**: https://huggingface.co/jinaai/jina-embeddings-v5-text-small
- **Architecture**: Causal Encoder (built on Qwen3-0.6B base backbone, last-token pooling, task-specific LoRA adapters).
- **Format & Size**: Float16/BFloat16 Safetensors, ~1.35 GB disk size (~677M parameters).
- **Total GPU Usage**: Serviced under TEI with 8 parallel requests @ 8K context (total tokens: 65,536). No KV cache. Expected VRAM: **~2.15 GB VRAM** (Weight baseline: ~1.35 GB, CUDA overhead: ~400 MB, linear activation memory under Flash Attention: ~400 MB).
- **Expected GPU Perf (RX 7900 XTX)**: Single query (512 tkn): **~4.5ms** | 8x8K batch (65K tkn): **~220ms** (served via TEI).
- **English & German Score**: 	
  - **MTEB English (v2)**: ~71.7
  - **MTEB German Retrieval (nDCG@10)**: ~65.0
  - **MMTEB Average**: ~67.7
- **Agentic Use**: Exceptional for long-context multilingual semantic search.
- **Max CTX**: 32,768 (32K) tokens.
- **Output Types**: Dense vectors (1024 dims, supports MRL down to 32).
- **Other features**: Task-specific LoRA adapters (retrieval, text-matching, clustering, classification), embedding distillation.
- **Fits expected hindsight usage of embedding**: Excellent fit. Outperforms older 0.6B models, matches the 32K context of Qwen3-Embedding, but runs under TEI and has task-specific adapters.
- **TEI Support & Native**: **Yes** (Qwen3 causal decoder backbone, supported in TEI via Python runner or vLLM adapter).
- **MTEB Leaderboard Multilingual / MMTEB**: Mean(task): 67.7.

#### Embedding: Alibaba-NLP/gte-multilingual-base

- **URL**: https://huggingface.co/Alibaba-NLP/gte-multilingual-base
- **Architecture**: XLM-RoBERTa encoder backbone.
- **Format & Size**: Float16/BFloat16 Safetensors, ~612 MB disk size (306M parameters).
- **Total GPU Usage**: Serviced under TEI with 8 parallel requests @ 8K context (total tokens: 65,536). No KV cache. Expected VRAM: **~1.21 GB VRAM** (Weight baseline: ~612 MB, CUDA overhead: ~400 MB, linear activation memory under Flash Attention: ~200 MB).
- **Expected GPU Perf (RX 7900 XTX)**: Single query (512 tkn): **~1.8ms** | 8x8K batch (65K tkn): **~120ms** (served via TEI).
- **English & German Score**: 	
  - **MTEB German Retrieval (nDCG@10)**: ~69.2
  - **MTEB English Retrieval**: ~64.8
  - **MMTEB Average**: ~63.0
- **Agentic Use**: Highly efficient RAG and classification queries where compute resources are constrained.
- **Max CTX**: 8,192 (8K) tokens.
- **Output Types**: 768-dimensional dense vectors.
- **Other features**: Bidirectional context representation, Apache 2.0 permissive license.
- **Fits expected hindsight usage of embedding**: Yes, excellent for 8K context and strong multilingual requirements under tight resource constraints.
- **TEI Support & Native**: **Yes** (XLM-RoBERTa encoder backbone, supported natively in TEI).
- **MTEB Leaderboard Multilingual**: Mean(task): ~63.0.

#### Embedding: Snowflake/snowflake-arctic-embed-l-v2.0

- **URL**: https://huggingface.co/Snowflake/snowflake-arctic-embed-l-v2.0
- **Architecture**: XLM-RoBERTa encoder backbone.
- **Format & Size**: Float16/BFloat16 Safetensors, ~1.14 GB disk size (568M parameters).
- **Total GPU Usage**: Serviced under TEI with 8 parallel requests @ 8K context (total tokens: 65,536). No KV cache. Expected VRAM: **~1.89 GB VRAM** (Weight baseline: ~1.14 GB, CUDA overhead: ~400 MB, linear activation memory under Flash Attention: ~350 MB).
- **Expected GPU Perf (RX 7900 XTX)**: Single query (512 tkn): **~3.0ms** | 8x8K batch (65K tkn): **~200ms** (served via TEI).
- **English & German Score**: 
  - **MTEB German Retrieval (nDCG@10)**: ~66.5
  - **MTEB English Retrieval**: ~67.5
  - **MMTEB Average**: ~65.2
- **Agentic Use**: High-performance multilingual semantic retrieval with permissive licensing.
- **Max CTX**: 8,192 (8K) tokens.
- **Output Types**: 1024-dimensional dense vectors. Supports Matryoshka Representation Learning (MRL) truncation down to 256.
- **Other features**: Bidirectional context, Apache 2.0 permissive license.
- **Fits expected hindsight usage of embedding**: Yes, excellent choice for standard 8K context with strict permissive license requirements.
- **TEI Support & Native**: **Yes** (XLM-RoBERTa encoder backbone, supported natively in TEI).
- **MTEB Leaderboard Multilingual**: Mean(task): ~65.2.

#### Embedding: codefuse-ai/F2LLM-v2-0.6B

- **URL**: https://huggingface.co/codefuse-ai/F2LLM-v2-0.6B
- **Architecture**: Causal Decoder backbone (based on Qwen3).
- **Format & Size**: Float16/BFloat16 Safetensors, ~1.2 GB disk size (600M parameters).
- **Total GPU Usage**: Serviced under `llama-server` (requires KV cache) with 8 parallel requests @ 8K context (total tokens: 65,536):
  - **8-bit KV Cache**: **~2.5 GB VRAM** (Weight baseline: ~1.2 GB, CUDA overhead: ~400 MB, 8-bit KV Cache: ~896 MB [112 MB per slot]).
  - **16-bit KV Cache**: **~3.4 GB VRAM** (Weight baseline: ~1.2 GB, CUDA overhead: ~400 MB, 16-bit KV Cache: ~1.79 GB [224 MB per slot]).
- **Expected GPU Perf (RX 7900 XTX)**: Single query (512 tkn): **~9.5ms** | 8x8K batch (65K tkn): **~520ms** (served via `llama-server` / python wrapper).
- **English & German Score**: 
  - **MTEB German Retrieval (nDCG@10)**: ~64.8
  - **MTEB English Retrieval**: ~68.2
- **Agentic Use**: Multilingual long-context retrieval where native TEI is not required, but permissive licensing is necessary.
- **Max CTX**: 32,768 (32K) tokens.
- **Output Types**: 1024-dimensional dense vectors (supports Matryoshka learning and knowledge distillation).
- **Other features**: Causal decoder representation, last-token pooling with L2 normalization, Apache 2.0 permissive license.
- **Fits expected hindsight usage of embedding**: Yes, viable as a long-context, permissively licensed alternative to Qwen3-Embedding served via `llama-server`.
- **TEI Support & Native**: **No** (Qwen3 causal decoder backbone, not compatible with TEI's native Candle sequence embedding loader).

#### Embedding: Alibaba-NLP/gte-Qwen2-1.5B-instruct

- **URL**: https://huggingface.co/Alibaba-NLP/gte-Qwen2-1.5B-instruct
- **Architecture**: Causal Decoder backbone (based on Qwen2).
- **Format & Size**: Float16/BFloat16 Safetensors, ~3.0 GB disk size (1.5B parameters).
- **Total GPU Usage**: Serviced under TEI with 8 parallel requests @ 8K context (total tokens: 65,536). No KV cache. Expected VRAM: **~3.4 GB VRAM** (Weight baseline: ~3.0 GB, CUDA overhead: ~400 MB, linear activation memory under Flash Attention: ~400 MB).
- **Expected GPU Perf (RX 7900 XTX)**: Single query (512 tkn): **~9.2ms** | 8x8K batch (65K tkn): **~420ms** (served via TEI).
- **English & German Score**: 
  - **MTEB German Retrieval (nDCG@10)**: ~66.2
  - **MTEB English Retrieval**: ~70.8
- **Agentic Use**: High-performance, long-context multilingual retrieval where Apache 2.0 license is required.
- **Max CTX**: 32,768 (32K) tokens.
- **Output Types**: 1536-dimensional dense vectors (supports instruction prefixes for retrieval).
- **Other features**: Causal decoder representation, last-token pooling with bidirectional instruction context, Apache 2.0 permissive license.
- **Fits expected hindsight usage of embedding**: Yes, excellent for 32K context deployments with strong multilingual benchmarks and permissive license requirements.
- **TEI Support & Native**: **Yes** (Qwen2 causal decoder backbone, supported natively in TEI).
- **MTEB Leaderboard Multilingual**: Mean(task): ~68.0.


#### Reranking: BAAI/bge-reranker-v2-m3

- **URL**: https://huggingface.co/BAAI/bge-reranker-v2-m3
- **Architecture**: Cross-Encoder (Sequence Classification model based on XLM-RoBERTa).
- **Format & Size**: Float16 Safetensors, ~1.14 GB disk size (567M parameters).
- **Total GPU Usage**: Serviced under TEI with 8 parallel requests @ 8K context (total tokens: 65,536). No KV cache. Expected VRAM: **~1.89 GB VRAM** (Weight baseline: ~1.14 GB, CUDA overhead: ~400 MB, linear activation memory under Flash Attention: ~350 MB).
- **Expected GPU Perf (RX 7900 XTX)**: Single query (512 tkn): **~5.5ms** | 8x8K batch (65K tkn): **~340ms** (served via TEI).
- **English & German Score**: 	
  - **BEIR nDCG@10 (English)**: ~56.51
  - **MTEB German Retrieval (nDCG@10)**: ~57.2
- **Agentic Use**: Perfect for scoring candidates retrieved from multi-strategy arms.
- **Max CTX**: 8,192 tokens.
- **Output Types**: Relevance score logit.
- **Other features**: Bidirectional cross-attention.
- **Fits expected hindsight usage of embedding**: Yes, excellent for 8K context reranking.
- **TEI Support & Native**: **Yes** (XLM-RoBERTa cross-encoder backbone, supported natively in TEI).
- **Retrieval Benchmarks / BEIR Score**: BEIR average of ~55.8 nDCG@10.

#### Reranking: jinaai/jina-reranker-v2-base-multilingual

- **URL**: https://huggingface.co/jinaai/jina-reranker-v2-base-multilingual
- **Architecture**: Cross-Encoder (Sequence Classification model using XLM-RoBERTa base).
- **Format & Size**: Float16 Safetensors, ~560 MB disk size (278M parameters).
- **Total GPU Usage**: Serviced under TEI with 8 parallel requests @ 1K max context (truncates 8K inputs to its native limit of 1,024 tokens; total tokens: 8,192). No KV cache. Expected VRAM: **~1.01 GB VRAM** (Weight baseline: ~560 MB, CUDA overhead: ~400 MB, linear activation memory under Flash Attention: ~50 MB).
- **Expected GPU Perf (RX 7900 XTX)**: Single query (512 tkn): **~2.8ms** | 8x1K batch (8K tkn): **~80ms** (served via TEI; input truncated to 1K limit).
- **English & German Score**: 	
  - **BEIR nDCG@10 (English)**: ~57.06
  - **MTEB German Retrieval (nDCG@10)**: ~59.1
- **Agentic Use**: Best choice for low-latency, low-VRAM multilingual reranking.
- **Max CTX**: 1,024 tokens (uses sliding window chunking to process longer documents).
- **Output Types**: Relevance score logit.
- **Other features**: Native sequence classification classifier head.
- **Fits expected hindsight usage of embedding**: Yes, but the 1K context window can be restrictive for very long facts/chunks unless chunk size is capped.
- **TEI Support & Native**: **Yes** (XLM-RoBERTa cross-encoder backbone, supported under TEI).
- **Retrieval Benchmarks / BEIR Score**: BEIR average of ~54.5 nDCG@10.

#### Reranking: jinaai/jina-reranker-v3

- **URL**: https://huggingface.co/jinaai/jina-reranker-v3
- **PDF**: [2509.25085v4.pdf](2509.25085v4.pdf)
- **Architecture**: Causal Cross-Encoder (built on Qwen3-0.6B transformer backbone, uses "Last but Not Late" (LBNL) causal self-attention interaction over query and multiple documents, with a lightweight MLP projector head).
- **Format & Size**: Float16 Safetensors, ~1.2 GB disk size (600M parameters).
- **Total GPU Usage**: Serviced under TEI with 8 parallel requests @ 8K context (total tokens: 65,536). No KV cache. Expected VRAM: **~2.05 GB VRAM** (Weight baseline: ~1.2 GB, CUDA overhead: ~400 MB, linear activation memory under Flash Attention: ~450 MB).
- **Expected GPU Perf (RX 7900 XTX)**: Single query (512 tkn): **~4.8ms** | 8x8K batch (65K tkn): **~290ms** (served via TEI).
- **English & German Score**: 
  - **BEIR nDCG@10 (English)**: ~61.94
  - **MTEB German Retrieval (nDCG@10)**: ~63.8
- **Agentic Use**: Advanced multi-hop retrieval and fact verification.
- **Max CTX**: 131,072 (131K) tokens. Can process up to 64 documents concurrently in a single context window.
- **Output Types**: Relevance scores for each document.
- **Other features**: LBNL interaction, multi-document batch ranking inside a single forward pass, MLP projector (1024 -> 512 -> 256).
- **Fits expected hindsight usage of embedding**: Outstanding. Its huge 131K context and ability to evaluate multiple documents concurrently make it an ideal fit for complex hindsight reflections.
- **TEI Support & Native**: **Yes** (Qwen3 causal decoder backbone, supported in TEI).
- **Retrieval Benchmarks / BEIR Score**: BEIR average of 61.94 nDCG@10, HotpotQA 78.58, FEVER 94.01.

---

### Embedding & Reranking Model Architectures: Attention, KV Cache & VRAM Scaling

The models listed above span seven distinct architecture × backend combinations. Understanding their attention mechanisms and TEI backend is critical for sizing VRAM, tuning parallelism, and choosing between `llama-server` (GGUF) and TEI serving.

#### Architecture Comparison

| Architecture | Task | TEI Backend | Attention Mask | Input → Output | Pooling / Head | KV Cache | VRAM Scaling | Example Models |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| **Causal Decoder (llama-server)** | Embedding | N/A (GGUF) | Causal (triangular) | Single text → dense vector | Last-token (`[EOS]`) | **Required** (pre-allocated per slot) | Weights + KV cache (linear in slots × ctx) | Qwen3-Embedding GGUF, F2LLM |
| **Causal Decoder (TEI)** | Embedding | Python (PyTorch) | Causal (triangular) | Single text → dense vector | Last-token (`[EOS]`) | **Not used** (single forward pass) | Weights + $O(N^2)$ activations | gte-Qwen2-1.5B, jina-v5-small |
| **Bidirectional Encoder (TEI Candle)** | Embedding | Candle (Rust) | Full (bidirectional) | Single text → dense vector | Mean pooling / `[CLS]` | **Not used** (incompatible) | Weights + $O(N^2)$ activations | bge-m3, jina-v3, gte-multilingual-base, snowflake-arctic |
| **Bidirectional Encoder (TEI Python)** | Embedding | Python (PyTorch) | Full (bidirectional) | Single text → dense vector | Mean pooling | **Not used** (incompatible) | Weights + $O(N^2)$ activations | pplx-embed-context |
| **Bidirectional Cross-Encoder (TEI Candle)** | Reranking | Candle (Rust) | Full (bidirectional) | Query–document pair → score | `[CLS]` → classifier head | **Not used** (incompatible) | Weights + $O(N^2)$ activations | bge-reranker-v2-m3, jina-reranker-v2 |
| **Causal Cross-Encoder (TEI Python)** | Reranking | Python (PyTorch) | Causal (triangular) | Query + N docs → N scores | Last-token → MLP projector | **Not used** (single forward pass) | Weights + $O(N^2)$ activations | jina-reranker-v3 |

> **Candle vs Python backend**: The Candle (Rust) backend compiles attention kernels natively and handles standard BERT/XLM-RoBERTa architectures. The Python (PyTorch) backend spawns a gRPC subprocess using `sentence-transformers` and is required for models with custom architectures (Qwen2/Qwen3 backbones, `trust_remote_code=True`). On ROCm, the Python backend uses `python-pytorch-opt-rocm` with native HIP kernels for RDNA3 GPU acceleration.

#### Why No KV Cache for Embedding / Reranking Inference?

**KV cache** is an optimization for *autoregressive text generation*, where the model generates tokens one-at-a-time and caches the Key/Value tensors of all previous tokens to avoid recomputing them at each step. For embedding and reranking tasks, the model processes the **entire input sequence in a single forward pass** — there are no iterative decoding steps, so there is nothing to cache.

- **Causal decoders under `llama-server`**: The server is designed for generation and *always* pre-allocates a KV cache per parallel slot. Even when used purely for embeddings, each slot consumes KV cache memory (e.g., ~112–224 MB per 8K-context slot for a 0.6B model). This is wasted memory but architecturally unavoidable in `llama-server`.
- **Causal decoders / cross-encoders under TEI (Python)**: TEI's Python/PyTorch backend runs the model in pure forward-pass mode. No KV cache is allocated. VRAM scales with model weights plus the transient attention activation tensors. This applies equally to causal embedding models (gte-Qwen2, jina-v5) and the causal cross-encoder reranker (jina-reranker-v3 with LBNL architecture).
- **Bidirectional encoders / cross-encoders (Candle and Python)**: KV caching is **fundamentally impossible** because every token attends to every other token — there is no sequential "prefix" whose K/V states remain stable. The full $O(N^2)$ attention matrix is always computed. This applies to Candle-served models (bge-m3, bge-reranker-v2-m3) and Python-served models (pplx-embed-context) alike.

#### VRAM Scaling: Attention Activations vs. Context Length

For all TEI serving modes (Candle and Python, causal and bidirectional), the dominant variable VRAM cost is the **attention activation memory**, which scales quadratically with sequence length:

$$\text{Attention VRAM per request} \approx \frac{N^2 \times H \times 2}{1024^2} \text{ MB}$$

where $N$ is the sequence length in tokens, $H$ is the number of attention heads, and the factor of 2 accounts for the Q×K and softmax×V matrices in float16/bfloat16.

Practical estimates for a **0.6B parameter model** (16 heads, bf16 activations, Flash Attention enabled), default **4 parallel requests @ 8K context**:

| Context Length | Per Request | 4 Parallel (default) | 8 Parallel |
|:---|:---|:---|:---|
| **512 tokens** | ~8 MB | ~32 MB | ~64 MB |
| **2K tokens** | ~128 MB | ~512 MB | ~1.0 GB |
| **8K tokens** | ~256 MB | **~1.0 GB** | ~2.0 GB |
| **32K tokens** | ~4.0 GB | ~16.0 GB | ~32.0 GB ⚠️ OOM |

> **Note**: Flash Attention reduces *peak* memory from $O(N^2)$ to $O(N)$ by tiling the computation, but the *compute* cost remains $O(N^2)$. The values above represent effective observed VRAM under Flash Attention. Without Flash Attention, memory would be significantly higher.

#### Practical Implications for Local Serving (RX 7900 XTX, 24 GB VRAM)

Given 24 GB total VRAM, and ~1.2 GB consumed by model weights + ~0.4 GB CUDA overhead:

- **Default budget (4 × 8K)**: ~1.0 GB activation — well within the ~22.4 GB available
- **32K context**: **1 parallel** (~4.0 GB) fits comfortably; **2 parallel** (~8.0 GB) is feasible; **4 parallel** (~16.0 GB) is tight; **8 parallel** exceeds VRAM
- **Mixed workloads** (e.g., 3×8K + 1×32K): ~0.8 + 4.0 GB = ~4.8 GB activations — fits with headroom

These constraints directly informed the hindsight benchmark tuning: the parallel request pattern was set to 3 rounds of 4 parallel × 8K requests (32K tokens per round, 98K total tokens) to stay within safe VRAM limits for the 0.6B model under TEI.

#### Quantization: Weights vs. Activations vs. Embedding Output

There are three distinct levels of quantization relevant to embedding/reranking inference. They target different memory consumers and have different support levels in TEI:

| Quantization Type | What It Reduces | TEI Support | Effect on $O(N^2)$ Activation Memory |
|:---|:---|:---|:---|
| **Weight quantization** | Model parameter storage (static) | Candle: GGUF-based quantized models. Python: `--dtype float16` (default bf16/fp16). No INT8 weight-only flag. | **None** — weights are a fixed cost, activations are computed at runtime precision |
| **Activation quantization** | Intermediate attention tensors (dynamic, $O(N^2)$) | **Not supported** — neither Candle nor Python backend expose INT8/FP8 activation compute paths | **Would halve** $O(N^2)$ memory if available (INT8 = half of fp16) |
| **Embedding output quantization** | Output vector storage (post-processing) | Models like pplx-embed natively output INT8/binary embeddings; `sentence-transformers` can quantize any output | **None** — post-forward-pass only, does not affect inference VRAM |

**Key findings:**

- **All TEI-served architectures compute activations in float16 or bfloat16.** There is no CLI flag or backend option to run attention in INT8 or FP8 precision. The `--dtype` flag only controls weight loading precision (`float16` vs `float32`), not the compute dtype of the attention matrix.
- **INT8 activation quantization** (computing Q×K and softmax×V in INT8) would theoretically halve the $O(N^2)$ attention memory cost. Specialized implementations exist (e.g., INT-FlashAttention for NVIDIA Ampere), but they are not integrated into TEI's Candle or Python backends.
- **FP8 activation quantization** (via FlashAttention-3) exists for NVIDIA Hopper/Ada hardware but is **not available on RDNA3** — the RX 7900 XTX (`gfx1100`) lacks native FP8 tensor core support.
- **RDNA3 INT8 status**: The hardware has basic INT8 dot-product instructions (`v_dot4_i32_iu8`) but no dedicated INT8 tensor cores. ROCm's Flash Attention implementation (via Composable Kernel) does not currently offer an INT8 compute path.

> **Bottom line**: On the current RX 7900 XTX + TEI stack, all architectures are locked to **bf16/fp16 activations**. The $O(N^2)$ attention memory cost cannot be reduced via precision — the only levers are parallelism (fewer concurrent requests), context length (shorter sequences), or Flash Attention (which reduces peak memory from $O(N^2)$ to $O(N)$ via tiling, already enabled by default).

---

### TEI Backends & Expected Performance on Host GPU (AMD Radeon RX 7900 XTX)

The local TEI deployment is built via the custom package **`tei-rocm`**, which compiles the Hugging Face `text-embeddings-inference` router with specific features:
1. **Candle Backend (Rust native)**: Used for standard bidirectional encoder models (e.g. BERT/XLM-RoBERTa). While Candle runs natively in Rust, in this build configuration it operates primarily on the CPU or falls back to ROCm compatibility layers when compiled with specific GPU flags.
2. **Python Backend (PyTorch / sentence-transformers)**: Spawns an optimized Python gRPC server subprocess. Because `tei-rocm` lists `python-pytorch-opt-rocm` as a dependency (which is compiled with native AMD ROCm/HIP optimizations for RDNA3 hardware), this backend leverages the host GPU directly.

#### GPU Hardware Profile (AMD Radeon RX 7900 XTX)
- **Architecture**: Navi 31 (`gfx1100`), 96 Compute Units.
- **Compute Capability**: ~123 TFLOPS FP16/BF16.
- **Memory Subsystem**: 24 GB GDDR6 VRAM, 384-bit memory bus width, **960 GB/s bandwidth** (extremely fast weight-loading).

#### Expected Performance & Throughput under ROCm PyTorch Backend
With PyTorch's native ROCm kernels (including SDPA / Flash Attention) enabled, the expected inference latency and token throughput for RAG workloads on the RX 7900 XTX are:

*   **Standard Embeddings (e.g. `bge-m3` or `jina-embeddings-v3` - ~500M to 700M parameters)**:
    *   *Short Context (512 tokens, Batch Size 1)*: Latency is **~2.5ms to 4.0ms**.
    *   *Ingestion Batch (e.g., 8 parallel requests @ 8K context length = 65,536 tokens)*: Total batch forward pass latency is **~180ms to 240ms** (yielding a processing throughput of **~270,000 to 360,000 tokens/second**).
*   **Causal/Decoder Embeddings (e.g. `gte-Qwen2-1.5B-instruct` - 1.5B parameters)**:
    *   *Short Context (512 tokens, Batch Size 1)*: Latency is **~8.0ms to 12.0ms**.
    *   *Heavy Batch (8 parallel requests @ 8K context length = 65,536 tokens)*: Total batch forward pass latency is **~380ms to 480ms** (throughput of **~135,000 to 170,000 tokens/second**).
*   **Listwise Rerankers (e.g. `jina-reranker-v3` - 600M parameters)**:
    *   *Heavy Evaluation Load (8 parallel requests @ 32K context length = 262,144 tokens)*: Total batch evaluation pass latency is **~500ms to 700ms** (throughput of **~370,000 to 520,000 tokens/second** due to length-sorted bucket batching and Flash Attention scaling).

## Text to Speech

## Speech to Text

## Image Generation
