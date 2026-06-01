# LLM Caching Optimization Benchmarks

## Local Inference Services Benchmarks

We ran local benchmarks for text embedding, text-to-speech (TTS), speech-to-text (STT), and document reranking on the AMD Radeon Pro W6800 hardware target. All services run inside hardened `bwrap`/systemd sandboxed environments.

### Text Chat (`local-llm-ggml`)

- **Model:** `qwen3` (`Qwen3.6-35B-A3B-APEX-I-Compact`)
  - **GPU Offload Layers (`LLM_N_GPU_LAYERS`):** `99` (Fully offloaded, ROCm GPU)
- **Context:** `benchmark-context.md` (truncated to 115,000 characters / ~31,041 tokens)
- **Phase 1 (Sequential Prefill):**
  - **Avg Cycle Prefill Time:** 3.69 s
  - **Avg New Chunk Prefill Speed:** 1072.06 tokens/sec (10 cycles)
- **Phase 2 (Chat Generation):** (tested with --skip-prefill)
  - **Avg TTFT (Prefill):** 27803.68 ms
  - **Avg Prefill Speed:** 1116.44 tokens/sec
  - **Avg Generation Speed:** 44.71 tokens/sec
  - **Avg Decode Time:** 13.42 s
- **Phase 3 (Prefix Caching & Distractor - Averages over 5 Cycles):**
  - **3a. Half Prefill + Question:** TTFT: 982.58 ms, Prefill: 16018.77 tokens/sec, Gen: 55.09 tokens/sec
  - **3b. Distractor (Short Question):** TTFT: 44.56 ms, Prefill: 382.60 tokens/sec, Gen: 74.80 tokens/sec
  - **3c. Full Prefill + Same Question:** TTFT: 16959.80 ms, Prefill: 1830.00 tokens/sec, Gen: 44.16 tokens/sec

### Text Embedding (`local-llm-ggml`)
- **Model:** `qwen3-embedding` (`Qwen3-Embedding-0.6B-Q8_0.gguf`)
  - **Embedding Context Size (`LLM_EMBEDDING_N_CTX`):** `8192` (Pooling: `mean`)
  - **GPU Offload Layers (`LLM_N_GPU_LAYERS`):** `99` (Fully offloaded, ROCm GPU)
- **Context:** `benchmark-context.md`
- **Configuration:** 20 chunks sequentially, 10 repeats
- **Avg Tokens/Run:** 7564.0
- **Avg Time/Run:** 2156.91 ms
- **Avg Speed:** 3506.99 tokens/sec

### Document Reranking (`local-rerank`)
- **Model:** `qwen3-reranker` (`Qwen3-Reranker-0.6B.Q4_K_M.gguf`)
  - **Context Size (`LR_N_CTX`):** `8192` (Pooling: `rank`)
  - **GPU Offload Layers (`LR_N_GPU_LAYERS`):** `0` (cpu only)
- **Query:** *"How do I configure Honcho memory recall mode and observation settings?"*
- **Documents:** 10 documents (Total 13,070 characters, ~3,439 estimated tokens)
- **Avg Reranking Time:** 25761.59 ms
- **Avg Token Speed:** 133.49 tokens/sec
- **Avg Throughput:** 0.39 docs/sec

### Speech-to-Text (STT) (`local-speech-to-text`)
- **Model:** `whisper-1` (`ggml-large-v3-turbo-q5_0.bin`)
- **Audio Source:** `speech-to-text.ogg` (trimmed to 45.0 seconds)
- **Repeats:** 10
- **Avg Transcribe Time:** 1.45 seconds
- **Avg Real-Time Factor (RTF):** 0.0321 (approx. 31x faster than real-time)

### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-1.7B-CustomVoice-Q8_0.gguf` + Vocoder `Qwen3-TTS-Tokenizer-12Hz-F16.gguf`)
  - **Execution Mode (`LTTS_MODE`):** `cpu-only`
- **Synthesis Text:** 45 words / 274 characters (Default Voice, WAV format)
- **Generated Audio Duration:** 15.74 seconds
- **Avg Synthesis Time:** 23.47 seconds
- **Avg Real-Time Factor (RTF):** 1.4914 (approx. 1.5x real-time generation latency)
- **Avg Speed:** 11.67 chars/sec (1.92 words/sec)

## Legacy Benchmark Results

**Context:** Testing advanced optimization flags for `llama.cpp` using the `Qwen3.6-35B` model, restricted to a **45,000 character context** with interleaved vision/text distractors.

### Benchmark Results (45k Chars)

We tested 6 configurations spanning combinations of Flash Attention (`-fa on`) and Physical Batch Size (`-ub`). and compressed K/V-Caches ('--cache-type-k q4_0 --cache-type-v q4_0')

| Configuration | Prefill Speed | Hit Latency | Cache Hit Rate | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Baseline** (`-ub 512`) | 3579 Char/s | ~863 ms | 87.5% | Stable |
| **FA** (`-ub 512, -fa on`) | 3522 Char/s | ~869 ms | 87.5% | Stable |
| **Batch 1024** (`-ub 1024`) | 4148 Char/s | ~1213 ms | 87.5% | **Optimal Balance** |
| **FA + Batch 1024** | 4123 Char/s | ~1219 ms | 87.5% | **Optimal Balance** |
| **Batch 2048** (`-ub 2048`) | 4419 Char/s | ~1922 ms | 0.0% (<1.5s limit) | Prefill Only |
| **FA + Batch 2048** | 4404 Char/s | ~1928 ms | 0.0% (<1.5s limit) | Prefill Only |

#### 1. Flash Attention (`-fa on`)
At 45,000 characters, explicitly enabling Flash Attention continues to show a **negligible or very slightly negative impact** on both prefill speed and cache hit latency. 
**Conclusion:** On this specific hardware/backend (ROCm W6800), Flash Attention overhead currently cancels out its benefits at 45k context. It may become beneficial closer to the 100k+ mark, or it may already be implicitly enabled, or optimally managed by the backend.

#### 2. Physical Batch Size (`-ub`)
The physical batch size dictates how many tokens the GPU processes in a single forward pass.
- **`-ub 512` (Default):** Lowest hit latency (~860ms), but slowest prefill. Best for highly concurrent, rapid chat applications.
- **`-ub 1024` (The Sweet Spot):** Achieves a **16% faster prefill** (4148 Char/s vs 3579) while keeping the cache hit latency at ~1.2s. This successfully maintains the 87.5% cache hit rate by staying under the 1.5s threshold limit.
- **`-ub 2048` (Max Speed):** Achieves the **maximum prefill speed** (4419 Char/s, 23% faster than baseline). However, the overhead of processing the interleaved requests in massive 2048-token chunks causes the cache hit retrieval latency to spike to almost 2 seconds, breaking the cache hit threshold.

#### Final Recommendation

**`-b 2048 -ub 1024` is the absolute sweet spot**. 

It significantly boosts the initial parsing speed of large documents while keeping the retrieval latency low enough to ensure rapid responses to follow-up questions from the cached context!
