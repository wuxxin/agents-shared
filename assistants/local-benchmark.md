# LLM Caching Optimization Benchmarks

## Local Inference Services Benchmarks

We ran local benchmarks for text embedding, text-to-speech (TTS), speech-to-text (STT), and document reranking on the AMD Radeon Pro W6800 hardware target. All services run inside isolated sandboxed environments.

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

