# LLM Caching Optimization Benchmarks

## Local Inference Services Benchmarks

We ran local benchmarks for text embedding, text-to-speech (TTS), speech-to-text (STT), and document reranking on the AMD Radeon Pro W6800 hardware target. All services run inside isolated sandboxed environments.

### Text Chat (`local-llm-ggml`)

- **Model:** `qwen3` (`Qwen3.6-35B-A3B-APEX-I-Compact`)
- GPU Offload Layers (`LLM_N_GPU_LAYERS`): `99` (Fully offloaded, ROCm GPU)
- Context File: /data/public/machine-learning/models/benchmark-context.md
- Context Size: truncated to 115000 characters / ~29246 tokens

- Phase 0 (Warmup):
  - Prompt Tokens:        19
  - Completion Tokens:    148
  - TTFT (Prefill):       14489.78 ms
  - Prefill Speed:        1.31 tokens/sec
  - Generation Speed:     74.03 tokens/sec

- Phase 1 (Sequential Prefill):
  - Avg Cycle Prefill Time: 3.69 s
  - Avg New Chunk Prefill Speed: 1072.06 tokens/sec (10 cycles)

- Phase 2 (Chat Generation): (300-word summary, tested with --skip-prefill)
  - Prompt Tokens:        31041
  - Avg Completion Tokens: 600.0
  - Avg TTFT (Prefill):   27709.08 ms
  - Avg Prefill Speed:    1120.25 tokens/sec
  - Avg Generation Speed: 43.96 tokens/sec
  - Avg Decode Time:      13.65 s

- Phase 3 (Prefix Caching & Distractor - Averages over 5 Cycles):
  - 3a. Half Prefill + Question: TTFT: 982.58 ms, Prefill: 16018.77 tokens/sec, Gen: 55.09 tokens/sec
  - 3b. Distractor (Short Question): TTFT: 44.56 ms, Prefill: 382.60 tokens/sec, Gen: 74.80 tokens/sec
  - 3c. Full Prefill + Same Question: TTFT: 16959.80 ms, Prefill: 1830.00 tokens/sec, Gen: 44.16 tokens/sec

  
### Text Embedding (`local-llm-ggml`)
- **Model:** `qwen3-embedding` (`Qwen3-Embedding-0.6B-Q8_0.gguf`)
- GPU Offload Layers (`LLM_N_GPU_LAYERS`): `99` (Fully offloaded, ROCm GPU)
- Context File: /data/public/machine-learning/models/benchmark-context.md
- Context Size: 172832 chars (45460 tokens)
- Chunks:               6 × 8192 tokens (max)
- Embedding Dim:        1024
- Avg Tokens/Run:       45460
- Avg Time/Run:         9.06 s
- Avg Throughput:       5019.28 tokens/sec
- Avg Chunk Latency:    1509.5 ms
- Avg Chunk p50:        1638.0 ms
- Avg Chunk p95:        1816.9 ms

### Document Reranking (`local-rerank`)
- **Model:** `qwen3-reranker` (`Qwen3-Reranker-0.6B.Q4_K_M.gguf`)
- Execution Mode: `cpu`
- Query: *"How do I configure Honcho memory recall mode and observation settings?"*
- Documents: 10 documents (Total 13,070 characters, ~3,439 estimated tokens)
- Avg Reranking Time: 25761.59 ms
- Avg Token Speed: 133.49 tokens/sec
- Avg Throughput: 0.39 docs/sec

### Speech-to-Text (STT) (`local-speech-to-text`)
- **Model:** `whisper-1` (`ggml-large-v3-turbo-q5_0.bin`)
- Execution Mode: `gpu`
- Audio Source: `speech-to-text.ogg` (trimmed to 45.0 seconds)
- Repeats: 10
- Avg Transcribe Time: 1.45 seconds
- Avg Real-Time Factor (RTF): 0.0321 (approx. 31x faster than real-time)

### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-1.7B-CustomVoice-Q8_0.gguf` + Vocoder `Qwen3-TTS-Tokenizer-12Hz-F16.gguf`)
- Execution Mode (`LTTS_MODE`): `cpu-only`
- Synthesis Text: 45 words / 274 characters (Default Voice, WAV format)
- Generated Audio Duration: 15.74 seconds
- Avg Synthesis Time: 23.47 seconds
- Avg Real-Time Factor (RTF): 1.4914 (approx. 1.5x real-time generation latency)
- Avg Speed: 11.67 chars/sec (1.92 words/sec)

