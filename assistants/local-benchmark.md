# LLM Caching Optimization Benchmarks

## Local Inference Services Benchmarks

We ran local benchmarks for text embedding, text-to-speech (TTS), speech-to-text (STT), and document reranking on the AMD Radeon Pro W6800 hardware target. All services run inside isolated sandboxed environments.

### 📊 Performance Comparison Matrix

#### Text Chat (`local-llm-ggml`)
| Configuration | Avg Chat TTFT | Avg Chat Prefill | Chat TTFT (Warmup) | Chat Gen Speed | Avg Chat Gen | Chat GPU Mem | Chat CPU Mem |
|---|---|---|---|---|---|---|---|
| **HIP** | 27332.83 ms | 1135.67 t/s | 219.56 ms | 74.32 t/s | 44.06 t/s | 19912.4 MB | 68.7 MB |
| **Vulkan** | 27386.12 ms | 1133.46 t/s | 221.63 ms | 74.48 t/s | 44.12 t/s | 20030.0 MB | 68.8 MB |
| **CPU** | N/A | N/A | N/A | N/A | N/A | N/A | N/A |

#### Text Embedding (`local-embedding`)
| Configuration | Embedding Throughput | Embedding Latency (Avg) | Embedding GPU Mem | Embedding CPU Mem |
|---|---|---|---|---|
| **HIP** | 4725.54 t/s | 1610.3 ms | 106.9 MB | 10489.9 MB |
| **Vulkan** | 4723.47 t/s | 1610.7 ms | 116.1 MB | 10490.0 MB |
| **CPU** | 4748.48 t/s | 1602.5 ms | 106.5 MB | 10490.0 MB |

#### Document Reranking (`local-rerank`)
| Configuration | Avg Reranking Time | Avg Token Speed | Avg Docs Throughput | GPU Mem | CPU Mem |
|---|---|---|---|---|---|
| **HIP** | 21982.01 ms | 156.78 tokens/s | 0.46 docs/s | 249.1 MB | 2840.1 MB |
| **Vulkan** | 21819.65 ms | 157.64 tokens/s | 0.46 docs/s | 241.3 MB | 2841.8 MB |
| **CPU** | 21155.10 ms | 162.75 tokens/s | 0.47 docs/s | 243.2 MB | 2841.8 MB |

#### Speech-to-Text (STT) (`local-speech-to-text`)
| Configuration | Avg Transcribe Time | Avg Real-Time Factor (RTF) | Speedup vs Real-time | GPU Mem | CPU Mem |
|---|---|---|---|---|---|
| **HIP** | 0.69 s | 0.0153 | 65.4x | 1115.4 MB | 382.7 MB |
| **Vulkan** | 0.69 s | 0.0153 | 65.4x | 1121.0 MB | 382.7 MB |
| **CPU** | 0.69 s | 0.0153 | 65.4x | 1109.6 MB | 382.9 MB |

#### Text-to-Speech (TTS) (`local-text-to-speech`)
| Configuration | Avg Synthesis Time | Avg Real-Time Factor (RTF) | Speed (chars/s) | GPU Mem | CPU Mem |
|---|---|---|---|---|---|
| **HIP** | 38.19 s | 2.2730 | 7.18 chars/s | 3427.3 MB | 970.5 MB |
| **Vulkan** | 34.92 s | 2.2648 | 7.86 chars/s | 3233.8 MB | 929.5 MB |
| **CPU** | 35.27 s | 2.2680 | 7.77 chars/s | 3236.6 MB | 925.2 MB |
| **Special (Hybrid)** | 35.21 s | 2.2642 | 7.80 chars/s | 3353.2 MB | 951.1 MB |
| **Special (Low-Mem)** | 34.06 s | 2.2678 | 8.05 chars/s | 3216.8 MB | 910.5 MB |

---

### ⚙️ Detailed Configuration Reports

### CPU Configuration Details

#### Text Embedding (`local-embedding`)
- **Model:** `qwen3-embedding` (`Qwen3-Embedding-0.6B-Q8_0.gguf`)
- **Execution Target:** `CPU`
- **GPU Memory Used:** 106.5 MB
- **CPU Memory Used:** 10490.0 MB
- **Benchmark Running Time:** 34.12 s
- **Metrics:**
  - Avg Time/Run:         9.62 s
  - Avg Throughput:       4748.48 tokens/sec
  - Avg Chunk Latency:    1602.5 ms
  - Avg Chunk p50:        1720.8 ms
  - Avg Chunk p95:        1979.1 ms

#### Document Reranking (`local-rerank`)
- **Model:** `qwen3-reranker` (`Qwen3-Reranker-0.6B.Q4_K_M.gguf`)
- **Execution Target:** `CPU`
- **GPU Memory Used:** 243.2 MB
- **CPU Memory Used:** 2841.8 MB
- **Benchmark Running Time:** 63.56 s
- **Metrics:**
  - Avg Reranking Time:   21155.10 ms
  - Avg Docs Throughput:  0.47 docs/sec
  - Avg Token Speed:      162.75 tokens/sec

#### Speech-to-Text (STT) (`local-speech-to-text`)
- **Model:** `whisper-1` (`ggml-large-v3-turbo-q5_0.bin`)
- **Execution Target:** `CPU`
- **GPU Memory Used:** 1109.6 MB
- **CPU Memory Used:** 382.9 MB
- **Benchmark Running Time:** 2.20 s
- **Metrics:**
  - Avg Transcribe Time:  0.69 seconds
  - Avg Real-Time Factor (RTF): 0.0153 (65.4x faster than real-time)

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `CPU`
- **GPU Memory Used:** 3236.6 MB
- **CPU Memory Used:** 925.2 MB
- **Benchmark Running Time:** 105.89 s
- **Metrics:**
  - Generated Audio Duration: 15.66 seconds
  - Avg Synthesis Time:   35.27 seconds
  - Avg Real-Time Factor (RTF): 2.2680
  - Avg Speed:            7.77 chars/sec

### HIP Configuration Details

#### Text Chat (`local-llm-ggml`)
- **Model:** `qwen3` (`Qwen3.6-35B-A3B-APEX-I-Compact`)
- **Execution Target:** `HIP`
- **GPU Memory Used:** 19912.4 MB
- **CPU Memory Used:** 68.7 MB
- **Benchmark Running Time:** 53.24 s
- **Warmup (Phase 0):**
  - TTFT (Prefill):       219.56 ms
  - Prefill Speed:        86.54 tokens/sec
  - Generation Speed:     74.32 tokens/sec
- **Generation (Phase 2):**
  - Avg Completion Tokens: 600.0
  - Avg TTFT (Prefill):   27332.83 ms
  - Avg Prefill Speed:    1135.67 tokens/sec
  - Avg Generation Speed: 44.06 tokens/sec
  - Avg Decode Time:      13.62 s

#### Text Embedding (`local-embedding`)
- **Model:** `qwen3-embedding` (`Qwen3-Embedding-0.6B-Q8_0.gguf`)
- **Execution Target:** `HIP`
- **GPU Memory Used:** 106.9 MB
- **CPU Memory Used:** 10489.9 MB
- **Benchmark Running Time:** 34.26 s
- **Metrics:**
  - Avg Time/Run:         9.66 s
  - Avg Throughput:       4725.54 tokens/sec
  - Avg Chunk Latency:    1610.3 ms
  - Avg Chunk p50:        1730.4 ms
  - Avg Chunk p95:        1989.7 ms

#### Document Reranking (`local-rerank`)
- **Model:** `qwen3-reranker` (`Qwen3-Reranker-0.6B.Q4_K_M.gguf`)
- **Execution Target:** `HIP`
- **GPU Memory Used:** 249.1 MB
- **CPU Memory Used:** 2840.1 MB
- **Benchmark Running Time:** 66.04 s
- **Metrics:**
  - Avg Reranking Time:   21982.01 ms
  - Avg Docs Throughput:  0.46 docs/sec
  - Avg Token Speed:      156.78 tokens/sec

#### Speech-to-Text (STT) (`local-speech-to-text`)
- **Model:** `whisper-1` (`ggml-large-v3-turbo-q5_0.bin`)
- **Execution Target:** `HIP`
- **GPU Memory Used:** 1115.4 MB
- **CPU Memory Used:** 382.7 MB
- **Benchmark Running Time:** 2.21 s
- **Metrics:**
  - Avg Transcribe Time:  0.69 seconds
  - Avg Real-Time Factor (RTF): 0.0153 (65.4x faster than real-time)

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `HIP`
- **GPU Memory Used:** 3427.3 MB
- **CPU Memory Used:** 970.5 MB
- **Benchmark Running Time:** 114.67 s
- **Metrics:**
  - Generated Audio Duration: 16.78 seconds
  - Avg Synthesis Time:   38.19 seconds
  - Avg Real-Time Factor (RTF): 2.2730
  - Avg Speed:            7.18 chars/sec

### SPECIAL (GPU-LOW-MEM) Configuration Details

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `SPECIAL (GPU-LOW-MEM)`
- **GPU Memory Used:** 3216.8 MB
- **CPU Memory Used:** 910.5 MB
- **Benchmark Running Time:** 102.25 s
- **Metrics:**
  - Generated Audio Duration: 15.26 seconds
  - Avg Synthesis Time:   34.06 seconds
  - Avg Real-Time Factor (RTF): 2.2678
  - Avg Speed:            8.05 chars/sec

### SPECIAL (HYBRID) Configuration Details

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `SPECIAL (HYBRID)`
- **GPU Memory Used:** 3353.2 MB
- **CPU Memory Used:** 951.1 MB
- **Benchmark Running Time:** 105.71 s
- **Metrics:**
  - Generated Audio Duration: 16.62 seconds
  - Avg Synthesis Time:   35.21 seconds
  - Avg Real-Time Factor (RTF): 2.2642
  - Avg Speed:            7.80 chars/sec

### VULKAN Configuration Details

#### Text Chat (`local-llm-ggml`)
- **Model:** `qwen3` (`Qwen3.6-35B-A3B-APEX-I-Compact`)
- **Execution Target:** `VULKAN`
- **GPU Memory Used:** 20030.0 MB
- **CPU Memory Used:** 68.8 MB
- **Benchmark Running Time:** 53.28 s
- **Warmup (Phase 0):**
  - TTFT (Prefill):       221.63 ms
  - Prefill Speed:        85.73 tokens/sec
  - Generation Speed:     74.48 tokens/sec
- **Generation (Phase 2):**
  - Avg Completion Tokens: 600.0
  - Avg TTFT (Prefill):   27386.12 ms
  - Avg Prefill Speed:    1133.46 tokens/sec
  - Avg Generation Speed: 44.12 tokens/sec
  - Avg Decode Time:      13.60 s

#### Text Embedding (`local-embedding`)
- **Model:** `qwen3-embedding` (`Qwen3-Embedding-0.6B-Q8_0.gguf`)
- **Execution Target:** `VULKAN`
- **GPU Memory Used:** 116.1 MB
- **CPU Memory Used:** 10490.0 MB
- **Benchmark Running Time:** 34.27 s
- **Metrics:**
  - Avg Time/Run:         9.66 s
  - Avg Throughput:       4723.47 tokens/sec
  - Avg Chunk Latency:    1610.7 ms
  - Avg Chunk p50:        1727.2 ms
  - Avg Chunk p95:        1992.6 ms

#### Document Reranking (`local-rerank`)
- **Model:** `qwen3-reranker` (`Qwen3-Reranker-0.6B.Q4_K_M.gguf`)
- **Execution Target:** `VULKAN`
- **GPU Memory Used:** 241.3 MB
- **CPU Memory Used:** 2841.8 MB
- **Benchmark Running Time:** 65.56 s
- **Metrics:**
  - Avg Reranking Time:   21819.65 ms
  - Avg Docs Throughput:  0.46 docs/sec
  - Avg Token Speed:      157.64 tokens/sec

#### Speech-to-Text (STT) (`local-speech-to-text`)
- **Model:** `whisper-1` (`ggml-large-v3-turbo-q5_0.bin`)
- **Execution Target:** `VULKAN`
- **GPU Memory Used:** 1121.0 MB
- **CPU Memory Used:** 382.7 MB
- **Benchmark Running Time:** 2.20 s
- **Metrics:**
  - Avg Transcribe Time:  0.69 seconds
  - Avg Real-Time Factor (RTF): 0.0153 (65.4x faster than real-time)

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `VULKAN`
- **GPU Memory Used:** 3233.8 MB
- **CPU Memory Used:** 929.5 MB
- **Benchmark Running Time:** 104.84 s
- **Metrics:**
  - Generated Audio Duration: 15.90 seconds
  - Avg Synthesis Time:   34.92 seconds
  - Avg Real-Time Factor (RTF): 2.2648
  - Avg Speed:            7.86 chars/sec

