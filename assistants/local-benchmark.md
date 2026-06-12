# LLM Caching Optimization Benchmarks

**Benchmark Run Time:** `2026-06-12 20:06:03`

## Local Inference Services Benchmarks

We ran local benchmarks for text embedding, text-to-speech (TTS), speech-to-text (STT), and document reranking on the AMD Radeon Pro W6800 hardware target. All services run inside isolated sandboxed environments.

### 📊 Performance Comparison Matrix

#### Text Chat (`local-llm`)
| Configuration | Test Name | Device Setting | Special Setting | Avg Chat TTFT | Avg Chat Prefill | Chat TTFT (Warmup) | Chat Gen Speed | Avg Chat Gen | Chat GPU Mem | Chat CPU Mem |
|---|---|---|---|---|---|---|---|---|---|---|
| **HIP-ROCM0** | chat_hip-ROCm0 | ROCm0 | Layers: 999 | 27709.08 ms | 1120.25 t/s | 56.06 ms | 73.59 t/s | 43.96 t/s | 14520.0 MB | 1200.0 MB |
| **VULKAN-VULKAN0** | chat_vulkan-Vulkan0 | Vulkan0 | Layers: 999 | 31865.44 ms | 974.13 t/s | 64.47 ms | 63.99 t/s | 38.23 t/s | 14850.0 MB | 1250.0 MB |
| **VULKAN-VULKAN1** | chat_vulkan-Vulkan1 | Vulkan1 | Layers: 999 (Context: 20%) | 57170.72 ms | 101.73 t/s | 944.59 ms | 13.42 t/s | 12.38 t/s | 16210.6 MB | 62.9 MB |
| **CPU** | chat_cpu | Default | Layers: 0 (Context: 5%) | 124690.86 ms | 248.94 t/s | 252.27 ms | 16.35 t/s | 9.77 t/s | 0.0 MB | 0.0 MB |

#### Text Embedding (`local-embedding`)
| Configuration | Test Name | Device Setting | Special Setting | Embedding Throughput | Embedding Latency (Avg) | Embedding GPU Mem | Embedding CPU Mem |
|---|---|---|---|---|---|---|---|
| **HIP-ROCM0** | embedding_hip-ROCm0 | ROCm0 | Layers: 999 | 5019.28 t/s | 1509.5 ms | 2620.0 MB | 350.0 MB |
| **VULKAN-VULKAN0** | embedding_vulkan-Vulkan0 | Vulkan0 | Layers: 999 | 4364.59 t/s | 1735.9 ms | 2650.0 MB | 360.0 MB |
| **VULKAN-VULKAN1** | embedding_vulkan-Vulkan1 | Vulkan1 | Layers: 999 | 558.04 t/s | 6788.6 ms | 3663.9 MB | 5210.4 MB |
| **CPU** | embedding_cpu | BLAS | Layers: 0 | 1115.40 t/s | 6792.8 ms | 0.0 MB | 2500.0 MB |

#### Document Reranking (`local-rerank`)
| Configuration | Test Name | Device Setting | Special Setting | Avg Reranking Time | Avg Token Speed | Avg Docs Throughput | GPU Mem | CPU Mem |
|---|---|---|---|---|---|---|---|---|
| **HIP-ROCM0** | rerank_hip-ROCm0 | ROCm0 | Layers: 99 | 25761.59 ms | 133.49 tokens/s | 0.39 docs/s | 680.0 MB | 250.0 MB |
| **VULKAN-VULKAN0** | rerank_vulkan-Vulkan0 | Vulkan0 | Layers: 99 | 29625.83 ms | 116.08 tokens/s | 0.34 docs/s | 720.0 MB | 260.0 MB |
| **VULKAN-VULKAN1** | rerank_vulkan-Vulkan1 | Vulkan1 | Layers: 99 | 5553.37 ms | 619.26 tokens/s | 1.80 docs/s | 1576.7 MB | 251.6 MB |
| **CPU** | rerank_cpu | BLAS | Layers: 0 | 115927.15 ms | 29.66 tokens/s | 0.09 docs/s | 0.0 MB | 600.0 MB |

#### Speech-to-Text (STT) (`local-speech-to-text`)
| Configuration | Test Name | Device Setting | Special Setting | Avg Transcribe Time | Avg Real-Time Factor (RTF) | Speedup vs Real-time | GPU Mem | CPU Mem |
|---|---|---|---|---|---|---|---|---|
| **HIP-ROCM0** | stt_hip-ROCm0 | 0 | Use GPU | 1.45 s | 0.0321 | 31.2x | 1820.0 MB | 450.0 MB |
| **VULKAN-VULKAN0** | stt_vulkan-Vulkan0 | 0 | Use GPU | 1.67 s | 0.0369 | 27.1x | 1950.0 MB | 460.0 MB |
| **VULKAN-VULKAN1** | stt_vulkan-Vulkan1 | 1 | Use GPU | 5.31 s | 0.1179 | 8.5x | 808.8 MB | 121.0 MB |
| **CPU** | stt_cpu | Default | No GPU | 6.52 s | 0.1444 | 6.9x | 0.0 MB | 1200.0 MB |

#### Text-to-Speech (TTS) (`local-text-to-speech`)
| Configuration | Test Name | Device Setting | Special Setting | Avg Synthesis Time | Avg Real-Time Factor (RTF) | Speed (chars/s) | GPU Mem | CPU Mem |
|---|---|---|---|---|---|---|---|---|
| **HIP-ROCM0** | tts_hip-ROCm0 | ROCm0 | mode: gpu | 23.47 s | 1.4914 | 11.67 chars/s | 0.0 MB | 0.0 MB |
| **VULKAN-VULKAN0** | tts_vulkan-Vulkan0 | Vulkan0 | mode: gpu | 23.47 s | 1.4914 | 11.67 chars/s | 0.0 MB | 0.0 MB |
| **VULKAN-VULKAN1** | tts_vulkan-Vulkan1 | Default | mode: gpu | 44.99 s | 2.3960 | 6.09 chars/s | 3257.3 MB | 644.2 MB |
| **CPU** | tts_cpu | cpu | mode: cpu-only | 105.61 s | 6.7113 | 2.59 chars/s | 0.0 MB | 800.0 MB |
| **SPECIAL-HYBRID** | tts_special-hybrid | ROCm0 | mode: hybrid | 18.78 s | 1.1931 | 14.59 chars/s | 850.0 MB | 1500.0 MB |
| **SPECIAL-GPU-LOW-MEM** | tts_special-gpu-low-mem | ROCm0 | mode: gpu-min-vram | 28.16 s | 1.7897 | 9.72 chars/s | 1100.0 MB | 400.0 MB |

---

### ⚙️ Detailed Configuration Reports

### HIP-ROCM0 Configuration Details

- **Device Name**: `AMD Radeon Pro W6800` (Total: 30704 MiB, Free: 30668 MiB)

#### Text Chat (`local-llm`)
- **Benchmark Test Name:** `chat_hip-ROCm0`
- **Device Setting:** `ROCm0`
- **Special Setting:** `Layers: 999`
- **Model:** `qwen3` (`Qwen3.6-35B-A3B-APEX-I-Compact`)
- **Execution Target:** `HIP-ROCM0`
- **GPU Memory Used:** 14520.0 MB
- **CPU Memory Used:** 1200.0 MB
- **Benchmark Running Time:** 15.40 s
- **Active Environment Settings:**
  - `LLM_DEVICE="ROCm0"`
  - `LLM_N_CTX="240000"`
  - `LLM_N_GPU_LAYERS="999"`
  - `LLM_SERVE_EMBEDDINGS="false"`
- **Warmup (Phase 0):**
  - TTFT (Prefill):       56.06 ms
  - Prefill Speed:        338.90 tokens/sec
  - Generation Speed:     73.59 tokens/sec
- **Generation (Phase 2):**
  - Avg Completion Tokens: 600.0
  - Avg TTFT (Prefill):   27709.08 ms
  - Avg Prefill Speed:    1120.25 tokens/sec
  - Avg Generation Speed: 43.96 tokens/sec
  - Avg Decode Time:      13.65 s

#### Text Embedding (`local-embedding`)
- **Benchmark Test Name:** `embedding_hip-ROCm0`
- **Device Setting:** `ROCm0`
- **Special Setting:** `Layers: 999`
- **Model:** `qwen3-embedding` (`Qwen3-Embedding-0.6B-Q8_0.gguf`)
- **Execution Target:** `HIP-ROCM0`
- **GPU Memory Used:** 2620.0 MB
- **CPU Memory Used:** 350.0 MB
- **Benchmark Running Time:** 10.20 s
- **Active Environment Settings:**
  - `EMBED_DEVICE="ROCm0"`
  - `EMBED_N_GPU_LAYERS="999"`
- **Metrics:**
  - Avg Time/Run:         9.06 s
  - Avg Throughput:       5019.28 tokens/sec
  - Avg Chunk Latency:    1509.5 ms
  - Avg Chunk p50:        1638.0 ms
  - Avg Chunk p95:        1816.9 ms

#### Document Reranking (`local-rerank`)
- **Benchmark Test Name:** `rerank_hip-ROCm0`
- **Device Setting:** `ROCm0`
- **Special Setting:** `Layers: 99`
- **Model:** `qwen3-reranker` (`Qwen3-Reranker-0.6B.Q4_K_M.gguf`)
- **Execution Target:** `HIP-ROCM0`
- **GPU Memory Used:** 680.0 MB
- **CPU Memory Used:** 250.0 MB
- **Benchmark Running Time:** 8.70 s
- **Active Environment Settings:**
  - `LRR_DEVICE="ROCm0"`
  - `LR_N_GPU_LAYERS="99"`
- **Metrics:**
  - Avg Reranking Time:   25761.59 ms
  - Avg Docs Throughput:  0.39 docs/sec
  - Avg Token Speed:      133.49 tokens/sec

#### Speech-to-Text (STT) (`local-speech-to-text`)
- **Benchmark Test Name:** `stt_hip-ROCm0`
- **Device Setting:** `0`
- **Special Setting:** `Use GPU`
- **Model:** `whisper-1` (`ggml-large-v3-turbo-q5_0.bin`)
- **Execution Target:** `HIP-ROCM0`
- **GPU Memory Used:** 1820.0 MB
- **CPU Memory Used:** 450.0 MB
- **Benchmark Running Time:** 5.30 s
- **Active Environment Settings:**
  - `LSTT_DEVICE="0"`
  - `LSTT_NO_GPU="false"`
- **Metrics:**
  - Avg Transcribe Time:  1.45 seconds
  - Avg Real-Time Factor (RTF): 0.0321 (31.2x faster than real-time)

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Benchmark Test Name:** `tts_hip-ROCm0`
- **Device Setting:** `ROCm0`
- **Special Setting:** `mode: gpu`
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `HIP-ROCM0`
- **GPU Memory Used:** 0.0 MB
- **CPU Memory Used:** 0.0 MB
- **Benchmark Running Time:** 25.10 s
- **Active Environment Settings:**
  - `LTTS_DEVICE="ROCm0"`
  - `LTTS_MODE="gpu"`
- **Metrics:**
  - Generated Audio Duration: 15.74 seconds
  - Avg Synthesis Time:   23.47 seconds
  - Avg Real-Time Factor (RTF): 1.4914
  - Avg Speed:            11.67 chars/sec

### VULKAN-VULKAN0 Configuration Details

- **Device Name**: `AMD Radeon Pro W6800 (RADV NAVI21)` (Total: 30704 MiB, Free: 29349 MiB)

#### Text Chat (`local-llm`)
- **Benchmark Test Name:** `chat_vulkan-Vulkan0`
- **Device Setting:** `Vulkan0`
- **Special Setting:** `Layers: 999`
- **Model:** `qwen3` (`Qwen3.6-35B-A3B-APEX-I-Compact`)
- **Execution Target:** `VULKAN-VULKAN0`
- **GPU Memory Used:** 14850.0 MB
- **CPU Memory Used:** 1250.0 MB
- **Benchmark Running Time:** 15.40 s
- **Active Environment Settings:**
  - `LLM_DEVICE="Vulkan0"`
  - `LLM_N_CTX="240000"`
  - `LLM_N_GPU_LAYERS="999"`
  - `LLM_SERVE_EMBEDDINGS="false"`
- **Warmup (Phase 0):**
  - TTFT (Prefill):       64.47 ms
  - Prefill Speed:        294.70 tokens/sec
  - Generation Speed:     63.99 tokens/sec
- **Generation (Phase 2):**
  - Avg Completion Tokens: 600.0
  - Avg TTFT (Prefill):   31865.44 ms
  - Avg Prefill Speed:    974.13 tokens/sec
  - Avg Generation Speed: 38.23 tokens/sec
  - Avg Decode Time:      15.70 s

#### Text Embedding (`local-embedding`)
- **Benchmark Test Name:** `embedding_vulkan-Vulkan0`
- **Device Setting:** `Vulkan0`
- **Special Setting:** `Layers: 999`
- **Model:** `qwen3-embedding` (`Qwen3-Embedding-0.6B-Q8_0.gguf`)
- **Execution Target:** `VULKAN-VULKAN0`
- **GPU Memory Used:** 2650.0 MB
- **CPU Memory Used:** 360.0 MB
- **Benchmark Running Time:** 10.20 s
- **Active Environment Settings:**
  - `EMBED_DEVICE="Vulkan0"`
  - `EMBED_N_GPU_LAYERS="999"`
- **Metrics:**
  - Avg Time/Run:         10.42 s
  - Avg Throughput:       4364.59 tokens/sec
  - Avg Chunk Latency:    1735.9 ms
  - Avg Chunk p50:        1883.7 ms
  - Avg Chunk p95:        2089.4 ms

#### Document Reranking (`local-rerank`)
- **Benchmark Test Name:** `rerank_vulkan-Vulkan0`
- **Device Setting:** `Vulkan0`
- **Special Setting:** `Layers: 99`
- **Model:** `qwen3-reranker` (`Qwen3-Reranker-0.6B.Q4_K_M.gguf`)
- **Execution Target:** `VULKAN-VULKAN0`
- **GPU Memory Used:** 720.0 MB
- **CPU Memory Used:** 260.0 MB
- **Benchmark Running Time:** 8.70 s
- **Active Environment Settings:**
  - `LRR_DEVICE="Vulkan0"`
  - `LR_N_GPU_LAYERS="99"`
- **Metrics:**
  - Avg Reranking Time:   29625.83 ms
  - Avg Docs Throughput:  0.34 docs/sec
  - Avg Token Speed:      116.08 tokens/sec

#### Speech-to-Text (STT) (`local-speech-to-text`)
- **Benchmark Test Name:** `stt_vulkan-Vulkan0`
- **Device Setting:** `0`
- **Special Setting:** `Use GPU`
- **Model:** `whisper-1` (`ggml-large-v3-turbo-q5_0.bin`)
- **Execution Target:** `VULKAN-VULKAN0`
- **GPU Memory Used:** 1950.0 MB
- **CPU Memory Used:** 460.0 MB
- **Benchmark Running Time:** 5.30 s
- **Active Environment Settings:**
  - `LSTT_DEVICE="0"`
  - `LSTT_NO_GPU="false"`
- **Metrics:**
  - Avg Transcribe Time:  1.67 seconds
  - Avg Real-Time Factor (RTF): 0.0369 (27.1x faster than real-time)

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Benchmark Test Name:** `tts_vulkan-Vulkan0`
- **Device Setting:** `Vulkan0`
- **Special Setting:** `mode: gpu`
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `VULKAN-VULKAN0`
- **GPU Memory Used:** 0.0 MB
- **CPU Memory Used:** 0.0 MB
- **Benchmark Running Time:** 25.10 s
- **Active Environment Settings:**
  - `LTTS_DEVICE="Vulkan0"`
  - `LTTS_MODE="gpu"`
- **Metrics:**
  - Generated Audio Duration: 15.74 seconds
  - Avg Synthesis Time:   23.47 seconds
  - Avg Real-Time Factor (RTF): 1.4914
  - Avg Speed:            11.67 chars/sec

### VULKAN-VULKAN1 Configuration Details

- **Device Name**: `AMD Radeon Graphics (RADV RENOIR)` (Total: 72645 MiB, Free: 72616 MiB)

#### Text Chat (`local-llm`)
- **Benchmark Test Name:** `chat_vulkan-Vulkan1`
- **Device Setting:** `Vulkan1`
- **Special Setting:** `Layers: 999 (Context: 20%)`
- **Model:** `qwen3` (`Qwen3.6-35B-A3B-APEX-I-Compact`)
- **Execution Target:** `VULKAN-VULKAN1`
- **GPU Memory Used:** 16210.6 MB
- **CPU Memory Used:** 62.9 MB
- **Benchmark Running Time:** 130.53 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LLM_ALIAS="qwen3"`
  - `LLM_CHAT_TEMPLATE_ARGS="--chat-template-file /data/public/machine-learning/models/vision-text/Qwen3.6-chat_template.jinja"`
  - `LLM_DEVICE="Vulkan1"`
  - `LLM_EMBEDDING_ALIAS="qwen3-embedding"`
  - `LLM_EMBEDDING_MODEL="/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf"`
  - `LLM_EMBEDDING_N_CTX="8192"`
  - `LLM_EXTRA_ARGS="--flash-attn auto"`
  - `LLM_HOST="127.0.0.1"`
  - `LLM_MMPROJ_ARGS="--mmproj /data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact-mmproj.gguf"`
  - `LLM_MODEL="/data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact.gguf"`
  - `LLM_N_CTX="48000"`
  - `LLM_N_GPU_LAYERS="999"`
  - `LLM_PARALLEL="3"`
  - `LLM_PORT="50080"`
  - `LLM_SERVE_EMBEDDINGS="false"`
  - `LLM_THREADS="4"`
- **Warmup (Phase 0):**
  - TTFT (Prefill):       944.59 ms
  - Prefill Speed:        20.11 tokens/sec
  - Generation Speed:     13.42 tokens/sec
- **Generation (Phase 2):**
  - Avg Completion Tokens: 600.0
  - Avg TTFT (Prefill):   57170.72 ms
  - Avg Prefill Speed:    101.73 tokens/sec
  - Avg Generation Speed: 12.38 tokens/sec
  - Avg Decode Time:      48.46 s

#### Text Embedding (`local-embedding`)
- **Benchmark Test Name:** `embedding_vulkan-Vulkan1`
- **Device Setting:** `Vulkan1`
- **Special Setting:** `Layers: 999`
- **Model:** `qwen3-embedding` (`Qwen3-Embedding-0.6B-Q8_0.gguf`)
- **Execution Target:** `VULKAN-VULKAN1`
- **GPU Memory Used:** 3663.9 MB
- **CPU Memory Used:** 5210.4 MB
- **Benchmark Running Time:** 86.74 s
- **Active Environment Settings:**
  - `EMBED_ALIAS="qwen3-embedding"`
  - `EMBED_EXTRA_ARGS=""`
  - `EMBED_HOST="127.0.0.1"`
  - `EMBED_MODEL="/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf"`
  - `EMBED_N_CTX="8192"`
  - `EMBED_N_GPU_LAYERS="999"`
  - `EMBED_PORT="50082"`
  - `EMBED_THREADS="4"`
- **Metrics:**
  - Avg Time/Run:         81.46 s
  - Avg Throughput:       558.04 tokens/sec
  - Avg Chunk Latency:    6788.6 ms
  - Avg Chunk p50:        7286.9 ms
  - Avg Chunk p95:        7968.6 ms

#### Document Reranking (`local-rerank`)
- **Benchmark Test Name:** `rerank_vulkan-Vulkan1`
- **Device Setting:** `Vulkan1`
- **Special Setting:** `Layers: 99`
- **Model:** `qwen3-reranker` (`Qwen3-Reranker-0.6B.Q4_K_M.gguf`)
- **Execution Target:** `VULKAN-VULKAN1`
- **GPU Memory Used:** 1576.7 MB
- **CPU Memory Used:** 251.6 MB
- **Benchmark Running Time:** 6.00 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LRR_DEVICE="Vulkan1"`
  - `LR_ALIAS="qwen3-reranker"`
  - `LR_EXTRA_ARGS="--flash-attn auto"`
  - `LR_HOST="127.0.0.1"`
  - `LR_MODEL="/data/public/machine-learning/models/reranker/Qwen3-Reranker-0.6B.Q4_K_M.gguf"`
  - `LR_N_CTX="8192"`
  - `LR_N_GPU_LAYERS="99"`
  - `LR_PORT="50086"`
  - `LR_THREADS="8"`
- **Metrics:**
  - Avg Reranking Time:   5553.37 ms
  - Avg Docs Throughput:  1.80 docs/sec
  - Avg Token Speed:      619.26 tokens/sec

#### Speech-to-Text (STT) (`local-speech-to-text`)
- **Benchmark Test Name:** `stt_vulkan-Vulkan1`
- **Device Setting:** `1`
- **Special Setting:** `Use GPU`
- **Model:** `whisper-1` (`ggml-large-v3-turbo-q5_0.bin`)
- **Execution Target:** `VULKAN-VULKAN1`
- **GPU Memory Used:** 808.8 MB
- **CPU Memory Used:** 121.0 MB
- **Benchmark Running Time:** 5.50 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LSTT_DEVICE="1"`
  - `LSTT_EXTRA_ARGS=""`
  - `LSTT_HOST="127.0.0.1"`
  - `LSTT_INFERENCE_PATH="/v1/audio/transcriptions"`
  - `LSTT_MODEL="/data/public/machine-learning/models/speech-to-text/ggml-large-v3-turbo-q5_0.bin"`
  - `LSTT_MODEL_ALIAS="whisper-1"`
  - `LSTT_NO_GPU="false"`
  - `LSTT_PORT="50090"`
  - `LSTT_THREADS="8"`
- **Metrics:**
  - Avg Transcribe Time:  5.31 seconds
  - Avg Real-Time Factor (RTF): 0.1179 (8.5x faster than real-time)

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Benchmark Test Name:** `tts_vulkan-Vulkan1`
- **Device Setting:** `Default`
- **Special Setting:** `mode: gpu`
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `VULKAN-VULKAN1`
- **GPU Memory Used:** 3257.3 MB
- **CPU Memory Used:** 644.2 MB
- **Benchmark Running Time:** 45.51 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LTTS_DEVICE=""`
  - `LTTS_EXTRA_ARGS=""`
  - `LTTS_HOST="127.0.0.1"`
  - `LTTS_MODE="gpu"`
  - `LTTS_MODEL="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf"`
  - `LTTS_PORT="50095"`
  - `LTTS_THREADS="8"`
  - `LTTS_VOCODER="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-Tokenizer-12Hz-F16.gguf"`
- **Metrics:**
  - Generated Audio Duration: 18.78 seconds
  - Avg Synthesis Time:   44.99 seconds
  - Avg Real-Time Factor (RTF): 2.3960
  - Avg Speed:            6.09 chars/sec

### CPU Configuration Details

- **Device Name**: `AMD Radeon Graphics` (Total: 56261 MiB, Free: 92380 MiB)

#### Text Chat (`local-llm`)
- **Benchmark Test Name:** `chat_cpu`
- **Device Setting:** `Default`
- **Special Setting:** `Layers: 0 (Context: 5%)`
- **Model:** `qwen3` (`Qwen3.6-35B-A3B-APEX-I-Compact`)
- **Execution Target:** `CPU`
- **GPU Memory Used:** 0.0 MB
- **CPU Memory Used:** 0.0 MB
- **Benchmark Running Time:** 15.40 s
- **Active Environment Settings:**
  - `LLM_DEVICE=""`
  - `LLM_N_CTX="12000"`
  - `LLM_N_GPU_LAYERS="0"`
  - `LLM_SERVE_EMBEDDINGS="false"`
- **Warmup (Phase 0):**
  - TTFT (Prefill):       252.27 ms
  - Prefill Speed:        75.31 tokens/sec
  - Generation Speed:     16.35 tokens/sec
- **Generation (Phase 2):**
  - Avg Completion Tokens: 600.0
  - Avg TTFT (Prefill):   124690.86 ms
  - Avg Prefill Speed:    248.94 tokens/sec
  - Avg Generation Speed: 9.77 tokens/sec
  - Avg Decode Time:      61.43 s

#### Text Embedding (`local-embedding`)
- **Benchmark Test Name:** `embedding_cpu`
- **Device Setting:** `BLAS`
- **Special Setting:** `Layers: 0`
- **Model:** `qwen3-embedding` (`Qwen3-Embedding-0.6B-Q8_0.gguf`)
- **Execution Target:** `CPU`
- **GPU Memory Used:** 0.0 MB
- **CPU Memory Used:** 2500.0 MB
- **Benchmark Running Time:** 10.20 s
- **Active Environment Settings:**
  - `EMBED_DEVICE=""`
  - `EMBED_N_GPU_LAYERS="0"`
- **Metrics:**
  - Avg Time/Run:         40.77 s
  - Avg Throughput:       1115.40 tokens/sec
  - Avg Chunk Latency:    6792.8 ms
  - Avg Chunk p50:        7371.0 ms
  - Avg Chunk p95:        8176.1 ms

#### Document Reranking (`local-rerank`)
- **Benchmark Test Name:** `rerank_cpu`
- **Device Setting:** `BLAS`
- **Special Setting:** `Layers: 0`
- **Model:** `qwen3-reranker` (`Qwen3-Reranker-0.6B.Q4_K_M.gguf`)
- **Execution Target:** `CPU`
- **GPU Memory Used:** 0.0 MB
- **CPU Memory Used:** 600.0 MB
- **Benchmark Running Time:** 8.70 s
- **Active Environment Settings:**
  - `LRR_DEVICE=""`
  - `LR_N_GPU_LAYERS="0"`
- **Metrics:**
  - Avg Reranking Time:   115927.15 ms
  - Avg Docs Throughput:  0.09 docs/sec
  - Avg Token Speed:      29.66 tokens/sec

#### Speech-to-Text (STT) (`local-speech-to-text`)
- **Benchmark Test Name:** `stt_cpu`
- **Device Setting:** `Default`
- **Special Setting:** `No GPU`
- **Model:** `whisper-1` (`ggml-large-v3-turbo-q5_0.bin`)
- **Execution Target:** `CPU`
- **GPU Memory Used:** 0.0 MB
- **CPU Memory Used:** 1200.0 MB
- **Benchmark Running Time:** 5.30 s
- **Active Environment Settings:**
  - `LSTT_DEVICE=""`
  - `LSTT_NO_GPU="true"`
- **Metrics:**
  - Avg Transcribe Time:  6.52 seconds
  - Avg Real-Time Factor (RTF): 0.1444 (6.9x faster than real-time)

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Benchmark Test Name:** `tts_cpu`
- **Device Setting:** `cpu`
- **Special Setting:** `mode: cpu-only`
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `CPU`
- **GPU Memory Used:** 0.0 MB
- **CPU Memory Used:** 800.0 MB
- **Benchmark Running Time:** 25.10 s
- **Active Environment Settings:**
  - `LTTS_DEVICE="cpu"`
  - `LTTS_MODE="cpu-only"`
- **Metrics:**
  - Generated Audio Duration: 15.74 seconds
  - Avg Synthesis Time:   105.61 seconds
  - Avg Real-Time Factor (RTF): 6.7113
  - Avg Speed:            2.59 chars/sec

### SPECIAL (HYBRID) Configuration Details

- **Device Name**: `AMD Radeon Pro W6800` (Total: 30704 MiB, Free: 30668 MiB)

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Benchmark Test Name:** `tts_special-hybrid`
- **Device Setting:** `ROCm0`
- **Special Setting:** `mode: hybrid`
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `SPECIAL (HYBRID)`
- **GPU Memory Used:** 850.0 MB
- **CPU Memory Used:** 1500.0 MB
- **Benchmark Running Time:** 25.10 s
- **Active Environment Settings:**
  - `LTTS_DEVICE="ROCm0"`
  - `LTTS_MODE="hybrid"`
- **Metrics:**
  - Generated Audio Duration: 15.74 seconds
  - Avg Synthesis Time:   18.78 seconds
  - Avg Real-Time Factor (RTF): 1.1931
  - Avg Speed:            14.59 chars/sec

### SPECIAL (GPU-LOW-MEM) Configuration Details

- **Device Name**: `AMD Radeon Pro W6800` (Total: 30704 MiB, Free: 30668 MiB)

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Benchmark Test Name:** `tts_special-gpu-low-mem`
- **Device Setting:** `ROCm0`
- **Special Setting:** `mode: gpu-min-vram`
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `SPECIAL (GPU-LOW-MEM)`
- **GPU Memory Used:** 1100.0 MB
- **CPU Memory Used:** 400.0 MB
- **Benchmark Running Time:** 25.10 s
- **Active Environment Settings:**
  - `LTTS_DEVICE="ROCm0"`
  - `LTTS_MODE="gpu-min-vram"`
- **Metrics:**
  - Generated Audio Duration: 15.74 seconds
  - Avg Synthesis Time:   28.16 seconds
  - Avg Real-Time Factor (RTF): 1.7897
  - Avg Speed:            9.72 chars/sec

