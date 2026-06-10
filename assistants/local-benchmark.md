# LLM Caching Optimization Benchmarks

## Local Inference Services Benchmarks

We ran local benchmarks for text embedding, text-to-speech (TTS), speech-to-text (STT), and document reranking on the AMD Radeon Pro W6800 hardware target. All services run inside isolated sandboxed environments.

### 📊 Performance Comparison Matrix

#### Text Chat & Embedding (`local-llm-ggml`)
| Configuration | Chat TTFT (Warmup) | Chat Gen Speed | Avg Chat TTFT | Avg Chat Gen | Chat GPU Mem | Embedding Throughput | Embedding Latency (Avg) | Embedding GPU Mem |
|---|---|---|---|---|---|---|---|---|
| **HIP** | 252.17 ms | 74.09 t/s | 9064.59 ms | 44.19 t/s | 20002.2 MB | 4720.74 t/s | 1616.2 ms | 6716.9 MB |
| **Vulkan** | 173.37 ms | 80.73 t/s | 11458.94 ms | 72.27 t/s | 19331.1 MB | 952.75 t/s | 7973.9 ms | 4403.1 MB |
| **CPU** | N/A | N/A | N/A | N/A | N/A | 4727.01 t/s | 1611.8 ms | 6734.1 MB |

#### Document Reranking (`local-rerank`)
| Configuration | Avg Reranking Time | Avg Token Speed | Avg Docs Throughput | GPU Mem |
|---|---|---|---|---|
| **HIP** | 790.05 ms | 4364.17 tokens/s | 12.69 docs/s | 1839.0 MB |
| **Vulkan** | 772.57 ms | 4544.04 tokens/s | 13.21 docs/s | 1585.2 MB |
| **CPU** | 33738.51 ms | 101.99 tokens/s | 0.30 docs/s | 227.3 MB |

#### Speech-to-Text (STT) (`local-speech-to-text`)
| Configuration | Avg Transcribe Time | Avg Real-Time Factor (RTF) | Speedup vs Real-time | GPU Mem |
|---|---|---|---|---|
| **HIP** | 0.70 s | 0.0155 | 64.5x | 1109.6 MB |
| **Vulkan** | 0.69 s | 0.0154 | 64.9x | 1102.0 MB |
| **CPU** | 16.62 s | 0.3693 | 2.7x | 0.0 MB |

#### Text-to-Speech (TTS) (`local-text-to-speech`)
| Configuration | Avg Synthesis Time | Avg Real-Time Factor (RTF) | Speed (chars/s) | GPU Mem |
|---|---|---|---|---|
| **HIP** | 63.97 s | 3.8688 | 4.31 chars/s | 4584.4 MB |
| **Vulkan** | 74.24 s | 3.8656 | 3.72 chars/s | 4797.9 MB |
| **CPU** | 61.50 s | 3.4947 | 4.49 chars/s | 7.3 MB |
| **Hybrid** | 61.54 s | 3.0612 | 4.49 chars/s | 2197.2 MB |

---

### ⚙️ Detailed Configuration Reports

### CPU Configuration Details

#### Text Embedding (`local-llm-ggml`)
- **Model:** `qwen3-embedding` (`Qwen3-Embedding-0.6B-Q8_0.gguf`)
- **Execution Target:** `CPU`
- **GPU Memory Used:** 6734.1 MB
- **Metrics:**
  - Avg Time/Run:         9.67 s
  - Avg Throughput:       4727.01 tokens/sec
  - Avg Chunk Latency:    1611.8 ms
  - Avg Chunk p50:        1721.1 ms
  - Avg Chunk p95:        1983.3 ms

#### Document Reranking (`local-rerank`)
- **Model:** `qwen3-reranker` (`Qwen3-Reranker-0.6B.Q4_K_M.gguf`)
- **Execution Target:** `CPU`
- **GPU Memory Used:** 227.3 MB
- **Metrics:**
  - Avg Reranking Time:   33738.51 ms
  - Avg Docs Throughput:  0.30 docs/sec
  - Avg Token Speed:      101.99 tokens/sec

#### Speech-to-Text (STT) (`local-speech-to-text`)
- **Model:** `whisper-1` (`ggml-large-v3-turbo-q5_0.bin`)
- **Execution Target:** `CPU`
- **GPU Memory Used:** 0.0 MB
- **Metrics:**
  - Avg Transcribe Time:  16.62 seconds
  - Avg Real-Time Factor (RTF): 0.3693 (2.7x faster than real-time)

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-1.7B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `CPU`
- **GPU Memory Used:** 7.3 MB
- **Metrics:**
  - Generated Audio Duration: 18.46 seconds
  - Avg Synthesis Time:   61.50 seconds
  - Avg Real-Time Factor (RTF): 3.4947
  - Avg Speed:            4.49 chars/sec

### HIP Configuration Details

#### Text Chat (`local-llm-ggml`)
- **Model:** `qwen3` (`Qwen3.6-35B-A3B-APEX-I-Compact`)
- **Execution Target:** `HIP`
- **GPU Memory Used:** 20002.2 MB
- **Warmup (Phase 0):**
  - TTFT (Prefill):       252.17 ms
  - Prefill Speed:        75.35 tokens/sec
  - Generation Speed:     74.09 tokens/sec
- **Generation (Phase 2):**
  - Avg Completion Tokens: 600.0
  - Avg TTFT (Prefill):   9064.59 ms
  - Avg Prefill Speed:    218816.72 tokens/sec
  - Avg Generation Speed: 44.19 tokens/sec
  - Avg Decode Time:      13.58 s

#### Text Embedding (`local-llm-ggml`)
- **Model:** `qwen3-embedding` (`Qwen3-Embedding-0.6B-Q8_0.gguf`)
- **Execution Target:** `HIP`
- **GPU Memory Used:** 6716.9 MB
- **Metrics:**
  - Avg Time/Run:         9.70 s
  - Avg Throughput:       4720.74 tokens/sec
  - Avg Chunk Latency:    1616.2 ms
  - Avg Chunk p50:        1712.3 ms
  - Avg Chunk p95:        1983.2 ms

#### Document Reranking (`local-rerank`)
- **Model:** `qwen3-reranker` (`Qwen3-Reranker-0.6B.Q4_K_M.gguf`)
- **Execution Target:** `HIP`
- **GPU Memory Used:** 1839.0 MB
- **Metrics:**
  - Avg Reranking Time:   790.05 ms
  - Avg Docs Throughput:  12.69 docs/sec
  - Avg Token Speed:      4364.17 tokens/sec

#### Speech-to-Text (STT) (`local-speech-to-text`)
- **Model:** `whisper-1` (`ggml-large-v3-turbo-q5_0.bin`)
- **Execution Target:** `HIP`
- **GPU Memory Used:** 1109.6 MB
- **Metrics:**
  - Avg Transcribe Time:  0.70 seconds
  - Avg Real-Time Factor (RTF): 0.0155 (64.5x faster than real-time)

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-1.7B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `HIP`
- **GPU Memory Used:** 4584.4 MB
- **Metrics:**
  - Generated Audio Duration: 18.30 seconds
  - Avg Synthesis Time:   63.97 seconds
  - Avg Real-Time Factor (RTF): 3.8688
  - Avg Speed:            4.31 chars/sec

### HYBRID Configuration Details

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-1.7B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `HYBRID`
- **GPU Memory Used:** 2197.2 MB
- **Metrics:**
  - Generated Audio Duration: 20.30 seconds
  - Avg Synthesis Time:   61.54 seconds
  - Avg Real-Time Factor (RTF): 3.0612
  - Avg Speed:            4.49 chars/sec

### VULKAN Configuration Details

#### Text Chat (`local-llm-ggml`)
- **Model:** `qwen3` (`Qwen3.6-35B-A3B-APEX-I-Compact`)
- **Execution Target:** `VULKAN`
- **GPU Memory Used:** 19331.1 MB
- **Warmup (Phase 0):**
  - TTFT (Prefill):       173.37 ms
  - Prefill Speed:        109.59 tokens/sec
  - Generation Speed:     80.73 tokens/sec
- **Generation (Phase 2):**
  - Avg Completion Tokens: 600.0
  - Avg TTFT (Prefill):   11458.94 ms
  - Avg Prefill Speed:    223344.07 tokens/sec
  - Avg Generation Speed: 72.27 tokens/sec
  - Avg Decode Time:      8.30 s

#### Text Embedding (`local-llm-ggml`)
- **Model:** `qwen3-embedding` (`Qwen3-Embedding-0.6B-Q8_0.gguf`)
- **Execution Target:** `VULKAN`
- **GPU Memory Used:** 4403.1 MB
- **Metrics:**
  - Avg Time/Run:         47.84 s
  - Avg Throughput:       952.75 tokens/sec
  - Avg Chunk Latency:    7973.9 ms
  - Avg Chunk p50:        8977.7 ms
  - Avg Chunk p95:        9789.6 ms

#### Document Reranking (`local-rerank`)
- **Model:** `qwen3-reranker` (`Qwen3-Reranker-0.6B.Q4_K_M.gguf`)
- **Execution Target:** `VULKAN`
- **GPU Memory Used:** 1585.2 MB
- **Metrics:**
  - Avg Reranking Time:   772.57 ms
  - Avg Docs Throughput:  13.21 docs/sec
  - Avg Token Speed:      4544.04 tokens/sec

#### Speech-to-Text (STT) (`local-speech-to-text`)
- **Model:** `whisper-1` (`ggml-large-v3-turbo-q5_0.bin`)
- **Execution Target:** `VULKAN`
- **GPU Memory Used:** 1102.0 MB
- **Metrics:**
  - Avg Transcribe Time:  0.69 seconds
  - Avg Real-Time Factor (RTF): 0.0154 (64.9x faster than real-time)

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-1.7B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `VULKAN`
- **GPU Memory Used:** 4797.9 MB
- **Metrics:**
  - Generated Audio Duration: 17.74 seconds
  - Avg Synthesis Time:   74.24 seconds
  - Avg Real-Time Factor (RTF): 3.8656
  - Avg Speed:            3.72 chars/sec

