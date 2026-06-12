# LLM Caching Optimization Benchmarks

**Benchmark Run Time:** `2026-06-11 22:58:47`

## Local Inference Services Benchmarks

We ran local benchmarks for text embedding, text-to-speech (TTS), speech-to-text (STT), and document reranking on the AMD Radeon Pro W6800 hardware target. All services run inside isolated sandboxed environments.

### 📊 Performance Comparison Matrix

#### Text Chat (`local-llm-ggml`)
| Configuration | Test Name | Device Setting | Special Setting | Avg Chat TTFT | Avg Chat Prefill | Chat TTFT (Warmup) | Chat Gen Speed | Avg Chat Gen | Chat GPU Mem | Chat CPU Mem |
|---|---|---|---|---|---|---|---|---|---|---|
| **HIP-ROCM0** | chat_hip-ROCm0 | ROCm0 | Layers: 999 | 26922.28 ms | 1152.99 t/s | 130.50 ms | 75.76 t/s | 44.97 t/s | 20035.8 MB | 77.6 MB |
| **VULKAN-VULKAN0** | chat_vulkan-Vulkan0 | Vulkan0 | Layers: 999 | 34516.53 ms | 899.31 t/s | 199.67 ms | 81.03 t/s | 72.24 t/s | 19142.7 MB | 63.3 MB |
| **VULKAN-VULKAN1** | chat_vulkan-Vulkan1 | Vulkan1 | Layers: 999 (Context: 20%) | 57170.72 ms | 101.73 t/s | 944.59 ms | 13.42 t/s | 12.38 t/s | 16210.6 MB | 62.9 MB |
| **CPU** | chat_cpu | Default | Layers: 0 (Context: 5%) | 31454.11 ms | 46.83 t/s | 649.11 ms | 12.43 t/s | 11.69 t/s | 1427.9 MB | 62.9 MB |

#### Text Embedding (`local-embedding`)
| Configuration | Test Name | Device Setting | Special Setting | Embedding Throughput | Embedding Latency (Avg) | Embedding GPU Mem | Embedding CPU Mem |
|---|---|---|---|---|---|---|---|
| **HIP-ROCM0** | embedding_hip-ROCm0 | ROCm0 | Layers: 999 | 4315.31 t/s | 1755.8 ms | 6737.1 MB | 10027.5 MB |
| **VULKAN-VULKAN0** | embedding_vulkan-Vulkan0 | Vulkan0 | Layers: 999 | 947.02 t/s | 8000.5 ms | 4410.8 MB | 15100.5 MB |
| **VULKAN-VULKAN1** | embedding_vulkan-Vulkan1 | Vulkan1 | Layers: 999 | 559.39 t/s | 6772.2 ms | 3663.9 MB | 5220.5 MB |
| **CPU** | embedding_cpu | BLAS | Layers: 0 | 99.94 t/s | 81969.0 ms | 14.6 MB | 11892.4 MB |

#### Document Reranking (`local-rerank`)
| Configuration | Test Name | Device Setting | Special Setting | Avg Reranking Time | Avg Token Speed | Avg Docs Throughput | GPU Mem | CPU Mem |
|---|---|---|---|---|---|---|---|---|
| **HIP-ROCM0** | rerank_hip-ROCm0 | ROCm0 | Layers: 99 | 840.00 ms | 4094.05 tokens/s | 11.90 docs/s | 1839.0 MB | 676.2 MB |
| **VULKAN-VULKAN0** | rerank_vulkan-Vulkan0 | Vulkan0 | Layers: 99 | 940.43 ms | 3656.84 tokens/s | 10.63 docs/s | 1581.1 MB | 240.7 MB |
| **VULKAN-VULKAN1** | rerank_vulkan-Vulkan1 | Vulkan1 | Layers: 99 | 5553.37 ms | 619.26 tokens/s | 1.80 docs/s | 1576.7 MB | 251.6 MB |
| **CPU** | rerank_cpu | BLAS | Layers: 0 | 10445.34 ms | 329.24 tokens/s | 0.96 docs/s | 0.0 MB | 2710.3 MB |

#### Speech-to-Text (STT) (`local-speech-to-text`)
| Configuration | Test Name | Device Setting | Special Setting | Avg Transcribe Time | Avg Real-Time Factor (RTF) | Speedup vs Real-time | GPU Mem | CPU Mem |
|---|---|---|---|---|---|---|---|---|
| **HIP-ROCM0** | stt_hip-ROCm0 | 0 | Use GPU | 0.81 s | 0.0180 | 55.6x | 1109.6 MB | 359.4 MB |
| **VULKAN-VULKAN0** | stt_vulkan-Vulkan0 | 0 | Use GPU | 1.08 s | 0.0241 | 41.5x | 838.5 MB | 145.2 MB |
| **VULKAN-VULKAN1** | stt_vulkan-Vulkan1 | 1 | Use GPU | 5.31 s | 0.1179 | 8.5x | 808.8 MB | 121.0 MB |
| **CPU** | stt_cpu | Default | No GPU | 12.71 s | 0.2824 | 3.5x | 0.1 MB | 1096.1 MB |

#### Text-to-Speech (TTS) (`local-text-to-speech`)
| Configuration | Test Name | Device Setting | Special Setting | Avg Synthesis Time | Avg Real-Time Factor (RTF) | Speed (chars/s) | GPU Mem | CPU Mem |
|---|---|---|---|---|---|---|---|---|
| **VULKAN-VULKAN0** | tts_vulkan-Vulkan0 | Default | mode: gpu | 46.14 s | 2.4163 | 5.94 chars/s | 0.0 MB | 703.8 MB |
| **VULKAN-VULKAN1** | tts_vulkan-Vulkan1 | Default | mode: gpu | 44.99 s | 2.3960 | 6.09 chars/s | 3257.3 MB | 644.2 MB |
| **CPU** | tts_cpu | Default | mode: cpu-only | 30.25 s | 1.5518 | 9.06 chars/s | 4.1 MB | 2972.0 MB |
| **SPECIAL-HYBRID** | tts_special-hybrid | Default | mode: hybrid | 25.22 s | 1.2779 | 10.86 chars/s | 2.1 MB | 2167.2 MB |
| **SPECIAL-GPU-LOW-MEM** | tts_special-gpu-low-mem | Default | mode: gpu-min-vram | 46.38 s | 2.4086 | 5.91 chars/s | 0.0 MB | 154.0 MB |
| **HIP** | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |

---

### ⚙️ Detailed Configuration Reports

### HIP-ROCM0 Configuration Details

- **Device Name**: `AMD Radeon Pro W6800` (Total: 30704 MiB, Free: 30668 MiB)

#### Text Chat (`local-llm-ggml`)
- **Benchmark Test Name:** `chat_hip-ROCm0`
- **Device Setting:** `ROCm0`
- **Special Setting:** `Layers: 999`
- **Model:** `qwen3` (`Qwen3.6-35B-A3B-APEX-I-Compact`)
- **Execution Target:** `HIP-ROCM0`
- **GPU Memory Used:** 20035.8 MB
- **CPU Memory Used:** 77.6 MB
- **Benchmark Running Time:** 52.52 s
- **Active Environment Settings:**
  - `LLM_ALIAS="qwen3"`
  - `LLM_CHAT_TEMPLATE_ARGS="--chat-template-file /data/public/machine-learning/models/vision-text/Qwen3.6-chat_template.jinja"`
  - `LLM_DEVICE="ROCm0"`
  - `LLM_EMBEDDING_ALIAS="qwen3-embedding"`
  - `LLM_EMBEDDING_MODEL="/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf"`
  - `LLM_EMBEDDING_N_CTX="8192"`
  - `LLM_EXTRA_ARGS="--flash-attn auto"`
  - `LLM_HOST="127.0.0.1"`
  - `LLM_MMPROJ_ARGS="--mmproj /data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact-mmproj.gguf"`
  - `LLM_MODEL="/data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact.gguf"`
  - `LLM_N_CTX="240000"`
  - `LLM_N_GPU_LAYERS="999"`
  - `LLM_PARALLEL="3"`
  - `LLM_PORT="50080"`
  - `LLM_SERVE_EMBEDDINGS="false"`
  - `LLM_THREADS="4"`
- **Warmup (Phase 0):**
  - TTFT (Prefill):       130.50 ms
  - Prefill Speed:        145.59 tokens/sec
  - Generation Speed:     75.76 tokens/sec
- **Generation (Phase 2):**
  - Avg Completion Tokens: 600.0
  - Avg TTFT (Prefill):   26922.28 ms
  - Avg Prefill Speed:    1152.99 tokens/sec
  - Avg Generation Speed: 44.97 tokens/sec
  - Avg Decode Time:      13.34 s

#### Text Embedding (`local-embedding`)
- **Benchmark Test Name:** `embedding_hip-ROCm0`
- **Device Setting:** `ROCm0`
- **Special Setting:** `Layers: 999`
- **Model:** `qwen3-embedding` (`Qwen3-Embedding-0.6B-Q8_0.gguf`)
- **Execution Target:** `HIP-ROCM0`
- **GPU Memory Used:** 6737.1 MB
- **CPU Memory Used:** 10027.5 MB
- **Benchmark Running Time:** 16.00 s
- **Active Environment Settings:**
  - `EMBED_ALIAS="qwen3-embedding"`
  - `EMBED_DEVICE="ROCm0"`
  - `EMBED_EXTRA_ARGS=""`
  - `EMBED_HOST="127.0.0.1"`
  - `EMBED_MODEL="/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf"`
  - `EMBED_N_CTX="8192"`
  - `EMBED_N_GPU_LAYERS="999"`
  - `EMBED_PORT="50082"`
  - `EMBED_THREADS="4"`
- **Metrics:**
  - Avg Time/Run:         10.53 s
  - Avg Throughput:       4315.31 tokens/sec
  - Avg Chunk Latency:    1755.8 ms
  - Avg Chunk p50:        1792.6 ms
  - Avg Chunk p95:        2509.6 ms

#### Document Reranking (`local-rerank`)
- **Benchmark Test Name:** `rerank_hip-ROCm0`
- **Device Setting:** `ROCm0`
- **Special Setting:** `Layers: 99`
- **Model:** `qwen3-reranker` (`Qwen3-Reranker-0.6B.Q4_K_M.gguf`)
- **Execution Target:** `HIP-ROCM0`
- **GPU Memory Used:** 1839.0 MB
- **CPU Memory Used:** 676.2 MB
- **Benchmark Running Time:** 1.00 s
- **Active Environment Settings:**
  - `LRR_DEVICE="ROCm0"`
  - `LR_ALIAS="qwen3-reranker"`
  - `LR_EXTRA_ARGS="--flash-attn auto"`
  - `LR_HOST="127.0.0.1"`
  - `LR_MODEL="/data/public/machine-learning/models/reranker/Qwen3-Reranker-0.6B.Q4_K_M.gguf"`
  - `LR_N_CTX="8192"`
  - `LR_N_GPU_LAYERS="99"`
  - `LR_PORT="50086"`
  - `LR_THREADS="8"`
- **Metrics:**
  - Avg Reranking Time:   840.00 ms
  - Avg Docs Throughput:  11.90 docs/sec
  - Avg Token Speed:      4094.05 tokens/sec

#### Speech-to-Text (STT) (`local-speech-to-text`)
- **Benchmark Test Name:** `stt_hip-ROCm0`
- **Device Setting:** `0`
- **Special Setting:** `Use GPU`
- **Model:** `whisper-1` (`ggml-large-v3-turbo-q5_0.bin`)
- **Execution Target:** `HIP-ROCM0`
- **GPU Memory Used:** 1109.6 MB
- **CPU Memory Used:** 359.4 MB
- **Benchmark Running Time:** 1.00 s
- **Active Environment Settings:**
  - `LSTT_DEVICE="0"`
  - `LSTT_EXTRA_ARGS=""`
  - `LSTT_HOST="127.0.0.1"`
  - `LSTT_INFERENCE_PATH="/v1/audio/transcriptions"`
  - `LSTT_MODEL="/data/public/machine-learning/models/speech-to-text/ggml-large-v3-turbo-q5_0.bin"`
  - `LSTT_MODEL_ALIAS="whisper-1"`
  - `LSTT_NO_GPU="false"`
  - `LSTT_PORT="50090"`
  - `LSTT_THREADS="8"`
- **Metrics:**
  - Avg Transcribe Time:  0.81 seconds
  - Avg Real-Time Factor (RTF): 0.0180 (55.6x faster than real-time)

### VULKAN-VULKAN0 Configuration Details

- **Device Name**: `AMD Radeon Pro W6800 (RADV NAVI21)` (Total: 30704 MiB, Free: 29277 MiB)

#### Text Chat (`local-llm-ggml`)
- **Benchmark Test Name:** `chat_vulkan-Vulkan0`
- **Device Setting:** `Vulkan0`
- **Special Setting:** `Layers: 999`
- **Model:** `qwen3` (`Qwen3.6-35B-A3B-APEX-I-Compact`)
- **Execution Target:** `VULKAN-VULKAN0`
- **GPU Memory Used:** 19142.7 MB
- **CPU Memory Used:** 63.3 MB
- **Benchmark Running Time:** 55.51 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LLM_ALIAS="qwen3"`
  - `LLM_CHAT_TEMPLATE_ARGS="--chat-template-file /data/public/machine-learning/models/vision-text/Qwen3.6-chat_template.jinja"`
  - `LLM_DEVICE="Vulkan0"`
  - `LLM_EMBEDDING_ALIAS="qwen3-embedding"`
  - `LLM_EMBEDDING_MODEL="/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf"`
  - `LLM_EMBEDDING_N_CTX="8192"`
  - `LLM_EXTRA_ARGS="--flash-attn auto"`
  - `LLM_HOST="127.0.0.1"`
  - `LLM_MMPROJ_ARGS="--mmproj /data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact-mmproj.gguf"`
  - `LLM_MODEL="/data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact.gguf"`
  - `LLM_N_CTX="240000"`
  - `LLM_N_GPU_LAYERS="999"`
  - `LLM_PARALLEL="3"`
  - `LLM_PORT="50080"`
  - `LLM_SERVE_EMBEDDINGS="false"`
  - `LLM_THREADS="4"`
- **Warmup (Phase 0):**
  - TTFT (Prefill):       199.67 ms
  - Prefill Speed:        95.16 tokens/sec
  - Generation Speed:     81.03 tokens/sec
- **Generation (Phase 2):**
  - Avg Completion Tokens: 600.0
  - Avg TTFT (Prefill):   34516.53 ms
  - Avg Prefill Speed:    899.31 tokens/sec
  - Avg Generation Speed: 72.24 tokens/sec
  - Avg Decode Time:      8.31 s

#### Text Embedding (`local-embedding`)
- **Benchmark Test Name:** `embedding_vulkan-Vulkan0`
- **Device Setting:** `Vulkan0`
- **Special Setting:** `Layers: 999`
- **Model:** `qwen3-embedding` (`Qwen3-Embedding-0.6B-Q8_0.gguf`)
- **Execution Target:** `VULKAN-VULKAN0`
- **GPU Memory Used:** 4410.8 MB
- **CPU Memory Used:** 15100.5 MB
- **Benchmark Running Time:** 53.52 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `EMBED_ALIAS="qwen3-embedding"`
  - `EMBED_DEVICE="Vulkan0"`
  - `EMBED_EXTRA_ARGS=""`
  - `EMBED_HOST="127.0.0.1"`
  - `EMBED_MODEL="/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf"`
  - `EMBED_N_CTX="8192"`
  - `EMBED_N_GPU_LAYERS="999"`
  - `EMBED_PORT="50082"`
  - `EMBED_THREADS="4"`
  - `HIP_VISIBLE_DEVICES=""`
- **Metrics:**
  - Avg Time/Run:         48.00 s
  - Avg Throughput:       947.02 tokens/sec
  - Avg Chunk Latency:    8000.5 ms
  - Avg Chunk p50:        8452.1 ms
  - Avg Chunk p95:        11662.4 ms

#### Document Reranking (`local-rerank`)
- **Benchmark Test Name:** `rerank_vulkan-Vulkan0`
- **Device Setting:** `Vulkan0`
- **Special Setting:** `Layers: 99`
- **Model:** `qwen3-reranker` (`Qwen3-Reranker-0.6B.Q4_K_M.gguf`)
- **Execution Target:** `VULKAN-VULKAN0`
- **GPU Memory Used:** 1581.1 MB
- **CPU Memory Used:** 240.7 MB
- **Benchmark Running Time:** 1.50 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LRR_DEVICE="Vulkan0"`
  - `LR_ALIAS="qwen3-reranker"`
  - `LR_EXTRA_ARGS="--flash-attn auto"`
  - `LR_HOST="127.0.0.1"`
  - `LR_MODEL="/data/public/machine-learning/models/reranker/Qwen3-Reranker-0.6B.Q4_K_M.gguf"`
  - `LR_N_CTX="8192"`
  - `LR_N_GPU_LAYERS="99"`
  - `LR_PORT="50086"`
  - `LR_THREADS="8"`
- **Metrics:**
  - Avg Reranking Time:   940.43 ms
  - Avg Docs Throughput:  10.63 docs/sec
  - Avg Token Speed:      3656.84 tokens/sec

#### Speech-to-Text (STT) (`local-speech-to-text`)
- **Benchmark Test Name:** `stt_vulkan-Vulkan0`
- **Device Setting:** `0`
- **Special Setting:** `Use GPU`
- **Model:** `whisper-1` (`ggml-large-v3-turbo-q5_0.bin`)
- **Execution Target:** `VULKAN-VULKAN0`
- **GPU Memory Used:** 838.5 MB
- **CPU Memory Used:** 145.2 MB
- **Benchmark Running Time:** 1.50 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LSTT_DEVICE="0"`
  - `LSTT_EXTRA_ARGS=""`
  - `LSTT_HOST="127.0.0.1"`
  - `LSTT_INFERENCE_PATH="/v1/audio/transcriptions"`
  - `LSTT_MODEL="/data/public/machine-learning/models/speech-to-text/ggml-large-v3-turbo-q5_0.bin"`
  - `LSTT_MODEL_ALIAS="whisper-1"`
  - `LSTT_NO_GPU="false"`
  - `LSTT_PORT="50090"`
  - `LSTT_THREADS="8"`
- **Metrics:**
  - Avg Transcribe Time:  1.08 seconds
  - Avg Real-Time Factor (RTF): 0.0241 (41.5x faster than real-time)

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Benchmark Test Name:** `tts_vulkan-Vulkan0`
- **Device Setting:** `Default`
- **Special Setting:** `mode: gpu`
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `VULKAN-VULKAN0`
- **GPU Memory Used:** 0.0 MB
- **CPU Memory Used:** 703.8 MB
- **Benchmark Running Time:** 46.51 s
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
  - Generated Audio Duration: 19.10 seconds
  - Avg Synthesis Time:   46.14 seconds
  - Avg Real-Time Factor (RTF): 2.4163
  - Avg Speed:            5.94 chars/sec

### VULKAN-VULKAN1 Configuration Details

- **Device Name**: `AMD Radeon Graphics (RADV RENOIR)` (Total: 72645 MiB, Free: 72616 MiB)

#### Text Chat (`local-llm-ggml`)
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
- **CPU Memory Used:** 5220.5 MB
- **Benchmark Running Time:** 86.52 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `EMBED_ALIAS="qwen3-embedding"`
  - `EMBED_DEVICE="Vulkan1"`
  - `EMBED_EXTRA_ARGS=""`
  - `EMBED_HOST="127.0.0.1"`
  - `EMBED_MODEL="/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf"`
  - `EMBED_N_CTX="4096"`
  - `EMBED_N_GPU_LAYERS="999"`
  - `EMBED_PORT="50082"`
  - `EMBED_THREADS="4"`
  - `HIP_VISIBLE_DEVICES=""`
- **Metrics:**
  - Avg Time/Run:         81.27 s
  - Avg Throughput:       559.39 tokens/sec
  - Avg Chunk Latency:    6772.2 ms
  - Avg Chunk p50:        7276.5 ms
  - Avg Chunk p95:        7990.0 ms

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

- **Device Name**: `OpenBLAS` (Total: 0 MiB, Free: 0 MiB)

#### Text Chat (`local-llm-ggml`)
- **Benchmark Test Name:** `chat_cpu`
- **Device Setting:** `Default`
- **Special Setting:** `Layers: 0 (Context: 5%)`
- **Model:** `qwen3` (`Qwen3.6-35B-A3B-APEX-I-Compact`)
- **Execution Target:** `CPU`
- **GPU Memory Used:** 1427.9 MB
- **CPU Memory Used:** 62.9 MB
- **Benchmark Running Time:** 107.53 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES="all"`
  - `HIP_VISIBLE_DEVICES="all"`
  - `LLM_ALIAS="qwen3"`
  - `LLM_CHAT_TEMPLATE_ARGS="--chat-template-file /data/public/machine-learning/models/vision-text/Qwen3.6-chat_template.jinja"`
  - `LLM_DEVICE=""`
  - `LLM_EMBEDDING_ALIAS="qwen3-embedding"`
  - `LLM_EMBEDDING_MODEL="/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf"`
  - `LLM_EMBEDDING_N_CTX="8192"`
  - `LLM_EXTRA_ARGS="--flash-attn auto"`
  - `LLM_HOST="127.0.0.1"`
  - `LLM_MMPROJ_ARGS="--mmproj /data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact-mmproj.gguf"`
  - `LLM_MODEL="/data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact.gguf"`
  - `LLM_N_CTX="12000"`
  - `LLM_N_GPU_LAYERS="0"`
  - `LLM_PARALLEL="3"`
  - `LLM_PORT="50080"`
  - `LLM_SERVE_EMBEDDINGS="false"`
  - `LLM_THREADS="4"`
- **Warmup (Phase 0):**
  - TTFT (Prefill):       649.11 ms
  - Prefill Speed:        29.27 tokens/sec
  - Generation Speed:     12.43 tokens/sec
- **Generation (Phase 2):**
  - Avg Completion Tokens: 600.0
  - Avg TTFT (Prefill):   31454.11 ms
  - Avg Prefill Speed:    46.83 tokens/sec
  - Avg Generation Speed: 11.69 tokens/sec
  - Avg Decode Time:      51.31 s

#### Text Embedding (`local-embedding`)
- **Benchmark Test Name:** `embedding_cpu`
- **Device Setting:** `BLAS`
- **Special Setting:** `Layers: 0`
- **Model:** `qwen3-embedding` (`Qwen3-Embedding-0.6B-Q8_0.gguf`)
- **Execution Target:** `CPU`
- **GPU Memory Used:** 14.6 MB
- **CPU Memory Used:** 11892.4 MB
- **Benchmark Running Time:** 87.54 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES="all"`
  - `EMBED_ALIAS="qwen3-embedding"`
  - `EMBED_DEVICE="BLAS"`
  - `EMBED_EXTRA_ARGS=""`
  - `EMBED_HOST="127.0.0.1"`
  - `EMBED_MODEL="/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf"`
  - `EMBED_N_CTX="8192"`
  - `EMBED_N_GPU_LAYERS="0"`
  - `EMBED_PORT="50082"`
  - `EMBED_THREADS="4"`
  - `HIP_VISIBLE_DEVICES="all"`
- **Metrics:**
  - Avg Time/Run:         81.97 s
  - Avg Throughput:       99.94 tokens/sec
  - Avg Chunk Latency:    81969.0 ms
  - Avg Chunk p50:        81969.0 ms
  - Avg Chunk p95:        81969.0 ms

#### Document Reranking (`local-rerank`)
- **Benchmark Test Name:** `rerank_cpu`
- **Device Setting:** `BLAS`
- **Special Setting:** `Layers: 0`
- **Model:** `qwen3-reranker` (`Qwen3-Reranker-0.6B.Q4_K_M.gguf`)
- **Execution Target:** `CPU`
- **GPU Memory Used:** 0.0 MB
- **CPU Memory Used:** 2710.3 MB
- **Benchmark Running Time:** 11.01 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES="all"`
  - `HIP_VISIBLE_DEVICES="all"`
  - `LRR_DEVICE="BLAS"`
  - `LR_ALIAS="qwen3-reranker"`
  - `LR_EXTRA_ARGS="--flash-attn auto"`
  - `LR_HOST="127.0.0.1"`
  - `LR_MODEL="/data/public/machine-learning/models/reranker/Qwen3-Reranker-0.6B.Q4_K_M.gguf"`
  - `LR_N_CTX="8192"`
  - `LR_N_GPU_LAYERS="0"`
  - `LR_PORT="50086"`
  - `LR_THREADS="8"`
- **Metrics:**
  - Avg Reranking Time:   10445.34 ms
  - Avg Docs Throughput:  0.96 docs/sec
  - Avg Token Speed:      329.24 tokens/sec

#### Speech-to-Text (STT) (`local-speech-to-text`)
- **Benchmark Test Name:** `stt_cpu`
- **Device Setting:** `Default`
- **Special Setting:** `No GPU`
- **Model:** `whisper-1` (`ggml-large-v3-turbo-q5_0.bin`)
- **Execution Target:** `CPU`
- **GPU Memory Used:** 0.1 MB
- **CPU Memory Used:** 1096.1 MB
- **Benchmark Running Time:** 13.01 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES="all"`
  - `HIP_VISIBLE_DEVICES="all"`
  - `LSTT_DEVICE=""`
  - `LSTT_EXTRA_ARGS=""`
  - `LSTT_HOST="127.0.0.1"`
  - `LSTT_INFERENCE_PATH="/v1/audio/transcriptions"`
  - `LSTT_MODEL="/data/public/machine-learning/models/speech-to-text/ggml-large-v3-turbo-q5_0.bin"`
  - `LSTT_MODEL_ALIAS="whisper-1"`
  - `LSTT_NO_GPU="true"`
  - `LSTT_PORT="50090"`
  - `LSTT_THREADS="8"`
- **Metrics:**
  - Avg Transcribe Time:  12.71 seconds
  - Avg Real-Time Factor (RTF): 0.2824 (3.5x faster than real-time)

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Benchmark Test Name:** `tts_cpu`
- **Device Setting:** `Default`
- **Special Setting:** `mode: cpu-only`
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `CPU`
- **GPU Memory Used:** 4.1 MB
- **CPU Memory Used:** 2972.0 MB
- **Benchmark Running Time:** 30.51 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES="all"`
  - `HIP_VISIBLE_DEVICES="all"`
  - `LTTS_DEVICE=""`
  - `LTTS_EXTRA_ARGS=""`
  - `LTTS_HOST="127.0.0.1"`
  - `LTTS_MODE="cpu-only"`
  - `LTTS_MODEL="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf"`
  - `LTTS_PORT="50095"`
  - `LTTS_THREADS="8"`
  - `LTTS_VOCODER="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-Tokenizer-12Hz-F16.gguf"`
- **Metrics:**
  - Generated Audio Duration: 19.50 seconds
  - Avg Synthesis Time:   30.25 seconds
  - Avg Real-Time Factor (RTF): 1.5518
  - Avg Speed:            9.06 chars/sec

### SPECIAL (HYBRID) Configuration Details

- **Device Name**: `AMD Radeon Pro W6800` (Total: 30704 MiB, Free: 30668 MiB)

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Benchmark Test Name:** `tts_special-hybrid`
- **Device Setting:** `Default`
- **Special Setting:** `mode: hybrid`
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `SPECIAL (HYBRID)`
- **GPU Memory Used:** 2.1 MB
- **CPU Memory Used:** 2167.2 MB
- **Benchmark Running Time:** 25.51 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES="all"`
  - `HIP_VISIBLE_DEVICES="all"`
  - `LTTS_DEVICE=""`
  - `LTTS_EXTRA_ARGS=""`
  - `LTTS_HOST="127.0.0.1"`
  - `LTTS_MODE="hybrid"`
  - `LTTS_MODEL="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf"`
  - `LTTS_PORT="50095"`
  - `LTTS_THREADS="8"`
  - `LTTS_VOCODER="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-Tokenizer-12Hz-F16.gguf"`
- **Metrics:**
  - Generated Audio Duration: 19.74 seconds
  - Avg Synthesis Time:   25.22 seconds
  - Avg Real-Time Factor (RTF): 1.2779
  - Avg Speed:            10.86 chars/sec

### SPECIAL (GPU-LOW-MEM) Configuration Details

- **Device Name**: `AMD Radeon Pro W6800` (Total: 30704 MiB, Free: 30668 MiB)

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Benchmark Test Name:** `tts_special-gpu-low-mem`
- **Device Setting:** `Default`
- **Special Setting:** `mode: gpu-min-vram`
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `SPECIAL (GPU-LOW-MEM)`
- **GPU Memory Used:** 0.0 MB
- **CPU Memory Used:** 154.0 MB
- **Benchmark Running Time:** 46.51 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES="all"`
  - `HIP_VISIBLE_DEVICES="all"`
  - `LTTS_DEVICE=""`
  - `LTTS_EXTRA_ARGS=""`
  - `LTTS_HOST="127.0.0.1"`
  - `LTTS_MODE="gpu-min-vram"`
  - `LTTS_MODEL="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf"`
  - `LTTS_PORT="50095"`
  - `LTTS_THREADS="8"`
  - `LTTS_VOCODER="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-Tokenizer-12Hz-F16.gguf"`
- **Metrics:**
  - Generated Audio Duration: 19.26 seconds
  - Avg Synthesis Time:   46.38 seconds
  - Avg Real-Time Factor (RTF): 2.4086
  - Avg Speed:            5.91 chars/sec

