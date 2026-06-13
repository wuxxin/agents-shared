# LLM Caching Optimization Benchmarks

**Benchmark Run Time:** `2026-06-13 00:14:22`

## Local Inference Services Benchmarks

We ran local benchmarks for text embedding, text-to-speech (TTS), speech-to-text (STT), and document reranking on the AMD Radeon Pro W6800 hardware target. All services run inside isolated sandboxed environments.

### 📊 Performance Comparison Matrix

#### Text Chat (`local-chat`)
| Configuration | Test Name | Device Setting | Special Setting | Avg Chat TTFT | Avg Chat Prefill | Chat TTFT (Warmup) | Chat Gen Speed | Avg Chat Gen | Chat GPU Mem | Chat CPU Mem |
|---|---|---|---|---|---|---|---|---|---|---|
| **HIP-ROCM0** | chat_hip-ROCm0 | ROCm0 | Layers: 999 | 26818.12 ms | 1157.46 t/s | 243.10 ms | 75.60 t/s | 44.80 t/s | 19998.0 MB | 1300.4 MB |
| **HIP-ROCM1** | chat_hip-ROCm1 | ROCm1 | Layers: 999 (Context: 20%) | -fail- | -fail- | -fail- | -fail- | -fail- | -fail- | -fail- |
| **VULKAN-VULKAN0** | chat_vulkan-Vulkan0 | Vulkan0 | Layers: 999 | 34307.58 ms | 904.79 t/s | 179.85 ms | 81.27 t/s | 72.46 t/s | 19144.7 MB | 817.9 MB |
| **VULKAN-VULKAN1** | chat_vulkan-Vulkan1 | Vulkan1 | Layers: 999 (Context: 20%) | 57427.08 ms | 101.28 t/s | 865.60 ms | 13.47 t/s | 12.41 t/s | 16210.6 MB | 817.8 MB |
| **CPU** | chat_cpu | Default | Layers: 0 (Context: 5%) | 34741.76 ms | 42.40 t/s | 663.72 ms | 11.94 t/s | 10.77 t/s | 1510.9 MB | 17464.7 MB |

#### Text Embedding (`local-embedding`)
| Configuration | Test Name | Device Setting | Special Setting | Embedding Throughput | Embedding Latency (Avg) | Embedding GPU Mem | Embedding CPU Mem |
|---|---|---|---|---|---|---|---|
| **HIP-ROCM0** | embedding_hip-ROCm0 | ROCm0 | Layers: 999 | 4317.09 t/s | 1755.0 ms | 6735.1 MB | 10004.5 MB |
| **VULKAN-VULKAN0** | embedding_vulkan-Vulkan0 | Vulkan0 | Layers: 999 | 936.61 t/s | 8089.5 ms | 4422.8 MB | 15099.3 MB |
| **VULKAN-VULKAN1** | embedding_vulkan-Vulkan1 | Vulkan1 | Layers: 999 | 559.60 t/s | 6769.7 ms | 3663.9 MB | 5219.0 MB |
| **CPU** | embedding_cpu | BLAS | Layers: 0 | 97.44 t/s | 84068.5 ms | 0.0 MB | 11890.9 MB |

#### Document Reranking (`local-rerank`)
| Configuration | Test Name | Device Setting | Special Setting | Avg Reranking Time | Avg Token Speed | Avg Docs Throughput | GPU Mem | CPU Mem |
|---|---|---|---|---|---|---|---|---|
| **HIP-ROCM0** | rerank_hip-ROCm0 | ROCm0 | Layers: 99 | 843.38 ms | 4077.64 tokens/s | 11.86 docs/s | 1837.0 MB | 673.4 MB |
| **VULKAN-VULKAN0** | rerank_vulkan-Vulkan0 | Vulkan0 | Layers: 99 | 930.27 ms | 3696.77 tokens/s | 10.75 docs/s | 1564.0 MB | 239.4 MB |
| **VULKAN-VULKAN1** | rerank_vulkan-Vulkan1 | Vulkan1 | Layers: 99 | 5571.62 ms | 617.24 tokens/s | 1.79 docs/s | 1576.7 MB | 241.1 MB |
| **CPU** | rerank_cpu | BLAS | Layers: 0 | 10285.86 ms | 334.34 tokens/s | 0.97 docs/s | 2.1 MB | 2709.0 MB |

#### Speech-to-Text (STT) (`local-speech-to-text`)
| Configuration | Test Name | Device Setting | Special Setting | Avg Transcribe Time | Avg Real-Time Factor (RTF) | Speedup vs Real-time | GPU Mem | CPU Mem |
|---|---|---|---|---|---|---|---|---|
| **HIP-ROCM0** | stt_hip-ROCm0 | 0 | Use GPU | 0.77 s | 0.0172 | 58.1x | 1109.6 MB | 356.9 MB |
| **VULKAN-VULKAN0** | stt_vulkan-Vulkan0 | 0 | Use GPU | 0.74 s | 0.0165 | 60.6x | 817.5 MB | 120.3 MB |
| **VULKAN-VULKAN1** | stt_vulkan-Vulkan1 | 1 | Use GPU | 5.35 s | 0.1189 | 8.4x | 808.8 MB | 120.1 MB |
| **CPU** | stt_cpu | Default | No GPU | 13.31 s | 0.2959 | 3.4x | 0.0 MB | 1095.2 MB |

#### Text-to-Speech (TTS) (`local-text-to-speech`)
| Configuration | Test Name | Device Setting | Special Setting | Avg Synthesis Time | Avg Real-Time Factor (RTF) | Speed (chars/s) | GPU Mem | CPU Mem |
|---|---|---|---|---|---|---|---|---|
| **HIP-ROCM0** | tts_hip-ROCm0 | Default | mode: gpu | -fail- | -fail- | -fail- | -fail- | -fail- |
| **VULKAN-VULKAN0** | tts_vulkan-Vulkan0 | Default | mode: gpu | 43.61 s | 2.3941 | 6.28 chars/s | 6.4 MB | 632.4 MB |
| **VULKAN-VULKAN1** | tts_vulkan-Vulkan1 | Default | mode: gpu | 44.50 s | 2.4534 | 6.16 chars/s | 3205.8 MB | 626.1 MB |
| **CPU** | tts_cpu | Default | mode: cpu-only | 32.20 s | 1.5321 | 8.51 chars/s | 0.0 MB | 3058.1 MB |
| **CPU-HIP-ROCM0** | tts_cpu-hip-ROCm0 | Default | mode: hybrid | 27.25 s | 1.2914 | 10.06 chars/s | 32.1 MB | 2202.3 MB |
| **CPU-HIP-ROCM1** | tts_cpu-hip-ROCm1 | Default | mode: hybrid | 26.44 s | 1.2927 | 10.36 chars/s | 1867.8 MB | 2187.3 MB |
| **CPU-VULKAN-VULKAN0** | tts_cpu-vulkan-Vulkan0 | Default | mode: hybrid | 25.50 s | 1.2763 | 10.75 chars/s | 0.0 MB | 2172.5 MB |
| **CPU-VULKAN-VULKAN1** | tts_cpu-vulkan-Vulkan1 | Default | mode: hybrid | 24.52 s | 1.2471 | 11.18 chars/s | 1803.3 MB | 2164.1 MB |

---

### ⚙️ Detailed Configuration Reports

### HIP-ROCM0 Configuration Details

- **Device Name**: `AMD Radeon Pro W6800` (Total: 30704 MiB, Free: 30668 MiB)

#### Text Chat (`local-chat`)
- **Benchmark Test Name:** `chat_hip-ROCm0`
- **Device Setting:** `ROCm0`
- **Special Setting:** `Layers: 999`
- **Model:** `qwen3` (`Qwen3.6-35B-A3B-APEX-I-Compact`)
- **Execution Target:** `HIP-ROCM0`
- **GPU Memory Used:** 19998.0 MB
- **CPU Memory Used:** 1300.4 MB
- **Benchmark Running Time:** 52.57 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES="0"`
  - `HIP_VISIBLE_DEVICES="0"`
  - `LCHAT_ALIAS="qwen3"`
  - `LCHAT_CHAT_TEMPLATE_ARGS="--chat-template-file /data/public/machine-learning/models/vision-text/Qwen3.6-chat_template.jinja"`
  - `LCHAT_DEVICE="ROCm0"`
  - `LCHAT_EXTRA_ARGS="--flash-attn auto --spec-type ngram-simple --spec-ngram-simple-size-n 6 --spec-ngram-simple-size-m 4"`
  - `LCHAT_HOST="127.0.0.1"`
  - `LCHAT_MMPROJ_ARGS="--mmproj /data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact-mmproj.gguf"`
  - `LCHAT_MODEL="/data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact.gguf"`
  - `LCHAT_N_CTX="240000"`
  - `LCHAT_N_GPU_LAYERS="999"`
  - `LCHAT_PARALLEL="3"`
  - `LCHAT_PORT="50080"`
  - `LCHAT_SERVE_EMBEDDINGS="false"`
  - `LCHAT_THREADS="4"`
- **Errors Count:** 0
- **Warmup (Phase 0):**
  - TTFT (Prefill):       243.10 ms
  - Prefill Speed:        78.16 tokens/sec
  - Generation Speed:     75.60 tokens/sec
- **Generation (Phase 2):**
  - Avg Completion Tokens: 600.0
  - Avg TTFT (Prefill):   26818.12 ms
  - Avg Prefill Speed:    1157.46 tokens/sec
  - Avg Generation Speed: 44.80 tokens/sec
  - Avg Decode Time:      13.39 s

#### Text Embedding (`local-embedding`)
- **Benchmark Test Name:** `embedding_hip-ROCm0`
- **Device Setting:** `ROCm0`
- **Special Setting:** `Layers: 999`
- **Model:** `qwen3-embedding` (`Qwen3-Embedding-0.6B-Q8_0.gguf`)
- **Execution Target:** `HIP-ROCM0`
- **GPU Memory Used:** 6735.1 MB
- **CPU Memory Used:** 10004.5 MB
- **Benchmark Running Time:** 15.82 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES="0"`
  - `LMBD_ALIAS="qwen3-embedding"`
  - `LMBD_DEVICE="ROCm0"`
  - `LMBD_EXTRA_ARGS=""`
  - `LMBD_HOST="127.0.0.1"`
  - `LMBD_MODEL="/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf"`
  - `LMBD_N_CTX="8192"`
  - `LMBD_N_GPU_LAYERS="999"`
  - `LMBD_PORT="50082"`
  - `LMBD_THREADS="4"`
  - `HIP_VISIBLE_DEVICES="0"`
- **Errors Count:** 0
- **Metrics:**
  - Avg Time/Run:         10.53 s
  - Avg Throughput:       4317.09 tokens/sec
  - Avg Chunk Latency:    1755.0 ms
  - Avg Chunk p50:        1791.1 ms
  - Avg Chunk p95:        2515.5 ms

#### Document Reranking (`local-rerank`)
- **Benchmark Test Name:** `rerank_hip-ROCm0`
- **Device Setting:** `ROCm0`
- **Special Setting:** `Layers: 99`
- **Model:** `qwen3-reranker` (`Qwen3-Reranker-0.6B.Q4_K_M.gguf`)
- **Execution Target:** `HIP-ROCM0`
- **GPU Memory Used:** 1837.0 MB
- **CPU Memory Used:** 673.4 MB
- **Benchmark Running Time:** 1.00 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES="0"`
  - `HIP_VISIBLE_DEVICES="0"`
  - `LRR_DEVICE="ROCm0"`
  - `LRR_N_GPU_LAYERS="99"`
  - `LR_ALIAS="qwen3-reranker"`
  - `LR_EXTRA_ARGS="--flash-attn auto"`
  - `LR_HOST="127.0.0.1"`
  - `LR_MODEL="/data/public/machine-learning/models/reranker/Qwen3-Reranker-0.6B.Q4_K_M.gguf"`
  - `LR_N_CTX="8192"`
  - `LR_N_GPU_LAYERS="99"`
  - `LR_PORT="50086"`
  - `LR_THREADS="8"`
- **Errors Count:** 0
- **Metrics:**
  - Avg Reranking Time:   843.38 ms
  - Avg Docs Throughput:  11.86 docs/sec
  - Avg Token Speed:      4077.64 tokens/sec

#### Speech-to-Text (STT) (`local-speech-to-text`)
- **Benchmark Test Name:** `stt_hip-ROCm0`
- **Device Setting:** `0`
- **Special Setting:** `Use GPU`
- **Model:** `whisper-1` (`ggml-large-v3-turbo-q5_0.bin`)
- **Execution Target:** `HIP-ROCM0`
- **GPU Memory Used:** 1109.6 MB
- **CPU Memory Used:** 356.9 MB
- **Benchmark Running Time:** 1.00 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES="0"`
  - `HIP_VISIBLE_DEVICES="0"`
  - `LSTT_DEVICE="0"`
  - `LSTT_EXTRA_ARGS=""`
  - `LSTT_HOST="127.0.0.1"`
  - `LSTT_INFERENCE_PATH="/v1/audio/transcriptions"`
  - `LSTT_MODEL="/data/public/machine-learning/models/speech-to-text/ggml-large-v3-turbo-q5_0.bin"`
  - `LSTT_MODEL_ALIAS="whisper-1"`
  - `LSTT_NO_GPU="false"`
  - `LSTT_PORT="50090"`
  - `LSTT_THREADS="8"`
- **Errors Count:** 0
- **Metrics:**
  - Avg Transcribe Time:  0.77 seconds
  - Avg Real-Time Factor (RTF): 0.0172 (58.1x faster than real-time)

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Benchmark Test Name:** `tts_hip-ROCm0`
- **Device Setting:** `Default`
- **Special Setting:** `mode: gpu`
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `HIP-ROCM0`
- **GPU Memory Used:** -fail-
- **CPU Memory Used:** -fail-
- **Benchmark Running Time:** -fail-
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES="0,1"`
  - `HIP_VISIBLE_DEVICES="0,1"`
  - `LTTS_DEVICE=""`
  - `LTTS_EXTRA_ARGS=""`
  - `LTTS_HOST="127.0.0.1"`
  - `LTTS_MODE="gpu"`
  - `LTTS_MODEL="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf"`
  - `LTTS_PORT="50095"`
  - `LTTS_THREADS="8"`
  - `LTTS_VOCODER="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-Tokenizer-12Hz-F16.gguf"`
- **Errors Count:** 0
- **Metrics:**
  - Generated Audio Duration: -fail-
  - Avg Synthesis Time:   -fail-
  - Avg Real-Time Factor (RTF): -fail-
  - Avg Speed:            -fail-

### HIP-ROCM1 Configuration Details

#### Text Chat (`local-chat`)
- **Benchmark Test Name:** `chat_hip-ROCm1`
- **Device Setting:** `ROCm1`
- **Special Setting:** `Layers: 999 (Context: 20%)`
- **Model:** `qwen3` (`Qwen3.6-35B-A3B-APEX-I-Compact`)
- **Execution Target:** `HIP-ROCM1`
- **GPU Memory Used:** -fail-
- **CPU Memory Used:** -fail-
- **Benchmark Running Time:** -fail-
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES="1"`
  - `HIP_VISIBLE_DEVICES="1"`
  - `LCHAT_ALIAS="qwen3"`
  - `LCHAT_CHAT_TEMPLATE_ARGS="--chat-template-file /data/public/machine-learning/models/vision-text/Qwen3.6-chat_template.jinja"`
  - `LCHAT_DEVICE="ROCm1"`
  - `LCHAT_EXTRA_ARGS="--flash-attn auto --spec-type ngram-simple --spec-ngram-simple-size-n 6 --spec-ngram-simple-size-m 4"`
  - `LCHAT_HOST="127.0.0.1"`
  - `LCHAT_MMPROJ_ARGS="--mmproj /data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact-mmproj.gguf"`
  - `LCHAT_MODEL="/data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact.gguf"`
  - `LCHAT_N_CTX="48000"`
  - `LCHAT_N_GPU_LAYERS="999"`
  - `LCHAT_PARALLEL="3"`
  - `LCHAT_PORT="50080"`
  - `LCHAT_SERVE_EMBEDDINGS="false"`
  - `LCHAT_THREADS="4"`
- **Errors Count:** 1
- **Top Errors:**
  - `Error: llama-server failed to start or port timed out`
- **Warmup (Phase 0):**
  - TTFT (Prefill):       -fail-
  - Prefill Speed:        -n.a.-
  - Generation Speed:     -fail-
- **Generation (Phase 2):**
  - Avg Completion Tokens: -n.a.-
  - Avg TTFT (Prefill):   -fail-
  - Avg Prefill Speed:    -fail-
  - Avg Generation Speed: -fail-
  - Avg Decode Time:      -n.a.-

### VULKAN-VULKAN0 Configuration Details

- **Device Name**: `AMD Radeon Pro W6800 (RADV NAVI21)` (Total: 30704 MiB, Free: 29435 MiB)

#### Text Chat (`local-chat`)
- **Benchmark Test Name:** `chat_vulkan-Vulkan0`
- **Device Setting:** `Vulkan0`
- **Special Setting:** `Layers: 999`
- **Model:** `qwen3` (`Qwen3.6-35B-A3B-APEX-I-Compact`)
- **Execution Target:** `VULKAN-VULKAN0`
- **GPU Memory Used:** 19144.7 MB
- **CPU Memory Used:** 817.9 MB
- **Benchmark Running Time:** 55.17 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LCHAT_ALIAS="qwen3"`
  - `LCHAT_CHAT_TEMPLATE_ARGS="--chat-template-file /data/public/machine-learning/models/vision-text/Qwen3.6-chat_template.jinja"`
  - `LCHAT_DEVICE="Vulkan0"`
  - `LCHAT_EXTRA_ARGS="--flash-attn auto --spec-type ngram-simple --spec-ngram-simple-size-n 6 --spec-ngram-simple-size-m 4"`
  - `LCHAT_HOST="127.0.0.1"`
  - `LCHAT_MMPROJ_ARGS="--mmproj /data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact-mmproj.gguf"`
  - `LCHAT_MODEL="/data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact.gguf"`
  - `LCHAT_N_CTX="240000"`
  - `LCHAT_N_GPU_LAYERS="999"`
  - `LCHAT_PARALLEL="3"`
  - `LCHAT_PORT="50080"`
  - `LCHAT_SERVE_EMBEDDINGS="false"`
  - `LCHAT_THREADS="4"`
- **Errors Count:** 0
- **Warmup (Phase 0):**
  - TTFT (Prefill):       179.85 ms
  - Prefill Speed:        105.64 tokens/sec
  - Generation Speed:     81.27 tokens/sec
- **Generation (Phase 2):**
  - Avg Completion Tokens: 600.0
  - Avg TTFT (Prefill):   34307.58 ms
  - Avg Prefill Speed:    904.79 tokens/sec
  - Avg Generation Speed: 72.46 tokens/sec
  - Avg Decode Time:      8.28 s

#### Text Embedding (`local-embedding`)
- **Benchmark Test Name:** `embedding_vulkan-Vulkan0`
- **Device Setting:** `Vulkan0`
- **Special Setting:** `Layers: 999`
- **Model:** `qwen3-embedding` (`Qwen3-Embedding-0.6B-Q8_0.gguf`)
- **Execution Target:** `VULKAN-VULKAN0`
- **GPU Memory Used:** 4422.8 MB
- **CPU Memory Used:** 15099.3 MB
- **Benchmark Running Time:** 53.76 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `LMBD_ALIAS="qwen3-embedding"`
  - `LMBD_DEVICE="Vulkan0"`
  - `LMBD_EXTRA_ARGS=""`
  - `LMBD_HOST="127.0.0.1"`
  - `LMBD_MODEL="/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf"`
  - `LMBD_N_CTX="8192"`
  - `LMBD_N_GPU_LAYERS="999"`
  - `LMBD_PORT="50082"`
  - `LMBD_THREADS="4"`
  - `HIP_VISIBLE_DEVICES=""`
- **Errors Count:** 1
- **Top Errors:**
  - `[34m0.06.132.047[0m [35mW ggml_vulkan: Failed to allocate pinned memory (Requested buffer size exceeds device buffer size limit: ErrorOutOfDeviceMemory)`
- **Metrics:**
  - Avg Time/Run:         48.54 s
  - Avg Throughput:       936.61 tokens/sec
  - Avg Chunk Latency:    8089.5 ms
  - Avg Chunk p50:        8756.3 ms
  - Avg Chunk p95:        11204.3 ms

#### Document Reranking (`local-rerank`)
- **Benchmark Test Name:** `rerank_vulkan-Vulkan0`
- **Device Setting:** `Vulkan0`
- **Special Setting:** `Layers: 99`
- **Model:** `qwen3-reranker` (`Qwen3-Reranker-0.6B.Q4_K_M.gguf`)
- **Execution Target:** `VULKAN-VULKAN0`
- **GPU Memory Used:** 1564.0 MB
- **CPU Memory Used:** 239.4 MB
- **Benchmark Running Time:** 1.10 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LRR_DEVICE="Vulkan0"`
  - `LRR_N_GPU_LAYERS="99"`
  - `LR_ALIAS="qwen3-reranker"`
  - `LR_EXTRA_ARGS="--flash-attn auto"`
  - `LR_HOST="127.0.0.1"`
  - `LR_MODEL="/data/public/machine-learning/models/reranker/Qwen3-Reranker-0.6B.Q4_K_M.gguf"`
  - `LR_N_CTX="8192"`
  - `LR_N_GPU_LAYERS="99"`
  - `LR_PORT="50086"`
  - `LR_THREADS="8"`
- **Errors Count:** 0
- **Metrics:**
  - Avg Reranking Time:   930.27 ms
  - Avg Docs Throughput:  10.75 docs/sec
  - Avg Token Speed:      3696.77 tokens/sec

#### Speech-to-Text (STT) (`local-speech-to-text`)
- **Benchmark Test Name:** `stt_vulkan-Vulkan0`
- **Device Setting:** `0`
- **Special Setting:** `Use GPU`
- **Model:** `whisper-1` (`ggml-large-v3-turbo-q5_0.bin`)
- **Execution Target:** `VULKAN-VULKAN0`
- **GPU Memory Used:** 817.5 MB
- **CPU Memory Used:** 120.3 MB
- **Benchmark Running Time:** 0.90 s
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
- **Errors Count:** 0
- **Metrics:**
  - Avg Transcribe Time:  0.74 seconds
  - Avg Real-Time Factor (RTF): 0.0165 (60.6x faster than real-time)

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Benchmark Test Name:** `tts_vulkan-Vulkan0`
- **Device Setting:** `Default`
- **Special Setting:** `mode: gpu`
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `VULKAN-VULKAN0`
- **GPU Memory Used:** 6.4 MB
- **CPU Memory Used:** 632.4 MB
- **Benchmark Running Time:** 43.77 s
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
- **Errors Count:** 0
- **Metrics:**
  - Generated Audio Duration: 18.22 seconds
  - Avg Synthesis Time:   43.61 seconds
  - Avg Real-Time Factor (RTF): 2.3941
  - Avg Speed:            6.28 chars/sec

### VULKAN-VULKAN1 Configuration Details

- **Device Name**: `AMD Radeon Graphics (RADV RENOIR)` (Total: 72645 MiB, Free: 72616 MiB)

#### Text Chat (`local-chat`)
- **Benchmark Test Name:** `chat_vulkan-Vulkan1`
- **Device Setting:** `Vulkan1`
- **Special Setting:** `Layers: 999 (Context: 20%)`
- **Model:** `qwen3` (`Qwen3.6-35B-A3B-APEX-I-Compact`)
- **Execution Target:** `VULKAN-VULKAN1`
- **GPU Memory Used:** 16210.6 MB
- **CPU Memory Used:** 817.8 MB
- **Benchmark Running Time:** 130.30 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LCHAT_ALIAS="qwen3"`
  - `LCHAT_CHAT_TEMPLATE_ARGS="--chat-template-file /data/public/machine-learning/models/vision-text/Qwen3.6-chat_template.jinja"`
  - `LCHAT_DEVICE="Vulkan1"`
  - `LCHAT_EXTRA_ARGS="--flash-attn auto --spec-type ngram-simple --spec-ngram-simple-size-n 6 --spec-ngram-simple-size-m 4"`
  - `LCHAT_HOST="127.0.0.1"`
  - `LCHAT_MMPROJ_ARGS="--mmproj /data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact-mmproj.gguf"`
  - `LCHAT_MODEL="/data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact.gguf"`
  - `LCHAT_N_CTX="48000"`
  - `LCHAT_N_GPU_LAYERS="999"`
  - `LCHAT_PARALLEL="3"`
  - `LCHAT_PORT="50080"`
  - `LCHAT_SERVE_EMBEDDINGS="false"`
  - `LCHAT_THREADS="4"`
- **Errors Count:** 0
- **Warmup (Phase 0):**
  - TTFT (Prefill):       865.60 ms
  - Prefill Speed:        21.95 tokens/sec
  - Generation Speed:     13.47 tokens/sec
- **Generation (Phase 2):**
  - Avg Completion Tokens: 600.0
  - Avg TTFT (Prefill):   57427.08 ms
  - Avg Prefill Speed:    101.28 tokens/sec
  - Avg Generation Speed: 12.41 tokens/sec
  - Avg Decode Time:      48.33 s

#### Text Embedding (`local-embedding`)
- **Benchmark Test Name:** `embedding_vulkan-Vulkan1`
- **Device Setting:** `Vulkan1`
- **Special Setting:** `Layers: 999`
- **Model:** `qwen3-embedding` (`Qwen3-Embedding-0.6B-Q8_0.gguf`)
- **Execution Target:** `VULKAN-VULKAN1`
- **GPU Memory Used:** 3663.9 MB
- **CPU Memory Used:** 5219.0 MB
- **Benchmark Running Time:** 86.42 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `LMBD_ALIAS="qwen3-embedding"`
  - `LMBD_DEVICE="Vulkan1"`
  - `LMBD_EXTRA_ARGS=""`
  - `LMBD_HOST="127.0.0.1"`
  - `LMBD_MODEL="/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf"`
  - `LMBD_N_CTX="4096"`
  - `LMBD_N_GPU_LAYERS="999"`
  - `LMBD_PORT="50082"`
  - `LMBD_THREADS="4"`
  - `HIP_VISIBLE_DEVICES=""`
- **Errors Count:** 0
- **Metrics:**
  - Avg Time/Run:         81.24 s
  - Avg Throughput:       559.60 tokens/sec
  - Avg Chunk Latency:    6769.7 ms
  - Avg Chunk p50:        7264.4 ms
  - Avg Chunk p95:        7963.1 ms

#### Document Reranking (`local-rerank`)
- **Benchmark Test Name:** `rerank_vulkan-Vulkan1`
- **Device Setting:** `Vulkan1`
- **Special Setting:** `Layers: 99`
- **Model:** `qwen3-reranker` (`Qwen3-Reranker-0.6B.Q4_K_M.gguf`)
- **Execution Target:** `VULKAN-VULKAN1`
- **GPU Memory Used:** 1576.7 MB
- **CPU Memory Used:** 241.1 MB
- **Benchmark Running Time:** 5.71 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LRR_DEVICE="Vulkan1"`
  - `LRR_N_GPU_LAYERS="99"`
  - `LR_ALIAS="qwen3-reranker"`
  - `LR_EXTRA_ARGS="--flash-attn auto"`
  - `LR_HOST="127.0.0.1"`
  - `LR_MODEL="/data/public/machine-learning/models/reranker/Qwen3-Reranker-0.6B.Q4_K_M.gguf"`
  - `LR_N_CTX="8192"`
  - `LR_N_GPU_LAYERS="99"`
  - `LR_PORT="50086"`
  - `LR_THREADS="8"`
- **Errors Count:** 0
- **Metrics:**
  - Avg Reranking Time:   5571.62 ms
  - Avg Docs Throughput:  1.79 docs/sec
  - Avg Token Speed:      617.24 tokens/sec

#### Speech-to-Text (STT) (`local-speech-to-text`)
- **Benchmark Test Name:** `stt_vulkan-Vulkan1`
- **Device Setting:** `1`
- **Special Setting:** `Use GPU`
- **Model:** `whisper-1` (`ggml-large-v3-turbo-q5_0.bin`)
- **Execution Target:** `VULKAN-VULKAN1`
- **GPU Memory Used:** 808.8 MB
- **CPU Memory Used:** 120.1 MB
- **Benchmark Running Time:** 5.51 s
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
- **Errors Count:** 0
- **Metrics:**
  - Avg Transcribe Time:  5.35 seconds
  - Avg Real-Time Factor (RTF): 0.1189 (8.4x faster than real-time)

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Benchmark Test Name:** `tts_vulkan-Vulkan1`
- **Device Setting:** `Default`
- **Special Setting:** `mode: gpu`
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `VULKAN-VULKAN1`
- **GPU Memory Used:** 3205.8 MB
- **CPU Memory Used:** 626.1 MB
- **Benchmark Running Time:** 44.68 s
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
- **Errors Count:** 0
- **Metrics:**
  - Generated Audio Duration: 18.14 seconds
  - Avg Synthesis Time:   44.50 seconds
  - Avg Real-Time Factor (RTF): 2.4534
  - Avg Speed:            6.16 chars/sec

### CPU Configuration Details

- **Device Name**: `OpenBLAS` (Total: 0 MiB, Free: 0 MiB)

#### Text Chat (`local-chat`)
- **Benchmark Test Name:** `chat_cpu`
- **Device Setting:** `Default`
- **Special Setting:** `Layers: 0 (Context: 5%)`
- **Model:** `qwen3` (`Qwen3.6-35B-A3B-APEX-I-Compact`)
- **Execution Target:** `CPU`
- **GPU Memory Used:** 1510.9 MB
- **CPU Memory Used:** 17464.7 MB
- **Benchmark Running Time:** 115.76 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LCHAT_ALIAS="qwen3"`
  - `LCHAT_CHAT_TEMPLATE_ARGS="--chat-template-file /data/public/machine-learning/models/vision-text/Qwen3.6-chat_template.jinja"`
  - `LCHAT_DEVICE=""`
  - `LCHAT_EXTRA_ARGS="--flash-attn auto --spec-type ngram-simple --spec-ngram-simple-size-n 6 --spec-ngram-simple-size-m 4"`
  - `LCHAT_HOST="127.0.0.1"`
  - `LCHAT_MMPROJ_ARGS="--mmproj /data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact-mmproj.gguf"`
  - `LCHAT_MODEL="/data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact.gguf"`
  - `LCHAT_N_CTX="12000"`
  - `LCHAT_N_GPU_LAYERS="0"`
  - `LCHAT_PARALLEL="3"`
  - `LCHAT_PORT="50080"`
  - `LCHAT_SERVE_EMBEDDINGS="false"`
  - `LCHAT_THREADS="4"`
- **Errors Count:** 0
- **Warmup (Phase 0):**
  - TTFT (Prefill):       663.72 ms
  - Prefill Speed:        28.63 tokens/sec
  - Generation Speed:     11.94 tokens/sec
- **Generation (Phase 2):**
  - Avg Completion Tokens: 600.0
  - Avg TTFT (Prefill):   34741.76 ms
  - Avg Prefill Speed:    42.40 tokens/sec
  - Avg Generation Speed: 10.77 tokens/sec
  - Avg Decode Time:      55.71 s

#### Text Embedding (`local-embedding`)
- **Benchmark Test Name:** `embedding_cpu`
- **Device Setting:** `BLAS`
- **Special Setting:** `Layers: 0`
- **Model:** `qwen3-embedding` (`Qwen3-Embedding-0.6B-Q8_0.gguf`)
- **Execution Target:** `CPU`
- **GPU Memory Used:** 0.0 MB
- **CPU Memory Used:** 11890.9 MB
- **Benchmark Running Time:** 89.29 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `LMBD_ALIAS="qwen3-embedding"`
  - `LMBD_DEVICE="BLAS"`
  - `LMBD_EXTRA_ARGS=""`
  - `LMBD_HOST="127.0.0.1"`
  - `LMBD_MODEL="/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf"`
  - `LMBD_N_CTX="8192"`
  - `LMBD_N_GPU_LAYERS="0"`
  - `LMBD_PORT="50082"`
  - `LMBD_THREADS="4"`
  - `HIP_VISIBLE_DEVICES=""`
- **Errors Count:** 0
- **Metrics:**
  - Avg Time/Run:         84.07 s
  - Avg Throughput:       97.44 tokens/sec
  - Avg Chunk Latency:    84068.5 ms
  - Avg Chunk p50:        84068.5 ms
  - Avg Chunk p95:        84068.5 ms

#### Document Reranking (`local-rerank`)
- **Benchmark Test Name:** `rerank_cpu`
- **Device Setting:** `BLAS`
- **Special Setting:** `Layers: 0`
- **Model:** `qwen3-reranker` (`Qwen3-Reranker-0.6B.Q4_K_M.gguf`)
- **Execution Target:** `CPU`
- **GPU Memory Used:** 2.1 MB
- **CPU Memory Used:** 2709.0 MB
- **Benchmark Running Time:** 10.43 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LRR_DEVICE="BLAS"`
  - `LRR_N_GPU_LAYERS="0"`
  - `LR_ALIAS="qwen3-reranker"`
  - `LR_EXTRA_ARGS="--flash-attn auto"`
  - `LR_HOST="127.0.0.1"`
  - `LR_MODEL="/data/public/machine-learning/models/reranker/Qwen3-Reranker-0.6B.Q4_K_M.gguf"`
  - `LR_N_CTX="8192"`
  - `LR_N_GPU_LAYERS="99"`
  - `LR_PORT="50086"`
  - `LR_THREADS="8"`
- **Errors Count:** 0
- **Metrics:**
  - Avg Reranking Time:   10285.86 ms
  - Avg Docs Throughput:  0.97 docs/sec
  - Avg Token Speed:      334.34 tokens/sec

#### Speech-to-Text (STT) (`local-speech-to-text`)
- **Benchmark Test Name:** `stt_cpu`
- **Device Setting:** `Default`
- **Special Setting:** `No GPU`
- **Model:** `whisper-1` (`ggml-large-v3-turbo-q5_0.bin`)
- **Execution Target:** `CPU`
- **GPU Memory Used:** 0.0 MB
- **CPU Memory Used:** 1095.2 MB
- **Benchmark Running Time:** 13.55 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LSTT_DEVICE=""`
  - `LSTT_EXTRA_ARGS=""`
  - `LSTT_HOST="127.0.0.1"`
  - `LSTT_INFERENCE_PATH="/v1/audio/transcriptions"`
  - `LSTT_MODEL="/data/public/machine-learning/models/speech-to-text/ggml-large-v3-turbo-q5_0.bin"`
  - `LSTT_MODEL_ALIAS="whisper-1"`
  - `LSTT_NO_GPU="true"`
  - `LSTT_PORT="50090"`
  - `LSTT_THREADS="8"`
- **Errors Count:** 0
- **Metrics:**
  - Avg Transcribe Time:  13.31 seconds
  - Avg Real-Time Factor (RTF): 0.2959 (3.4x faster than real-time)

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Benchmark Test Name:** `tts_cpu`
- **Device Setting:** `Default`
- **Special Setting:** `mode: cpu-only`
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `CPU`
- **GPU Memory Used:** 0.0 MB
- **CPU Memory Used:** 3058.1 MB
- **Benchmark Running Time:** 32.38 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LTTS_DEVICE=""`
  - `LTTS_EXTRA_ARGS=""`
  - `LTTS_HOST="127.0.0.1"`
  - `LTTS_MODE="cpu-only"`
  - `LTTS_MODEL="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf"`
  - `LTTS_PORT="50095"`
  - `LTTS_THREADS="8"`
  - `LTTS_VOCODER="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-Tokenizer-12Hz-F16.gguf"`
- **Errors Count:** 0
- **Metrics:**
  - Generated Audio Duration: 21.02 seconds
  - Avg Synthesis Time:   32.20 seconds
  - Avg Real-Time Factor (RTF): 1.5321
  - Avg Speed:            8.51 chars/sec

### SPECIAL (CPU-HIP-ROCM0) Configuration Details

- **Device Name**: `AMD Radeon Pro W6800` (Total: 30704 MiB, Free: 30668 MiB)

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Benchmark Test Name:** `tts_cpu-hip-ROCm0`
- **Device Setting:** `Default`
- **Special Setting:** `mode: hybrid`
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `SPECIAL (CPU-HIP-ROCM0)`
- **GPU Memory Used:** 32.1 MB
- **CPU Memory Used:** 2202.3 MB
- **Benchmark Running Time:** 27.36 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LTTS_DEVICE=""`
  - `LTTS_EXTRA_ARGS=""`
  - `LTTS_HOST="127.0.0.1"`
  - `LTTS_MODE="hybrid"`
  - `LTTS_MODEL="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf"`
  - `LTTS_PORT="50095"`
  - `LTTS_THREADS="8"`
  - `LTTS_VOCODER="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-Tokenizer-12Hz-F16.gguf"`
- **Errors Count:** 0
- **Metrics:**
  - Generated Audio Duration: 21.10 seconds
  - Avg Synthesis Time:   27.25 seconds
  - Avg Real-Time Factor (RTF): 1.2914
  - Avg Speed:            10.06 chars/sec

### SPECIAL (CPU-HIP-ROCM1) Configuration Details

- **Device Name**: `AMD Radeon Graphics` (Total: 56261 MiB, Free: 65414 MiB)

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Benchmark Test Name:** `tts_cpu-hip-ROCm1`
- **Device Setting:** `Default`
- **Special Setting:** `mode: hybrid`
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `SPECIAL (CPU-HIP-ROCM1)`
- **GPU Memory Used:** 1867.8 MB
- **CPU Memory Used:** 2187.3 MB
- **Benchmark Running Time:** 26.56 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LTTS_DEVICE=""`
  - `LTTS_EXTRA_ARGS=""`
  - `LTTS_HOST="127.0.0.1"`
  - `LTTS_MODE="hybrid"`
  - `LTTS_MODEL="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf"`
  - `LTTS_PORT="50095"`
  - `LTTS_THREADS="8"`
  - `LTTS_VOCODER="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-Tokenizer-12Hz-F16.gguf"`
- **Errors Count:** 0
- **Metrics:**
  - Generated Audio Duration: 20.46 seconds
  - Avg Synthesis Time:   26.44 seconds
  - Avg Real-Time Factor (RTF): 1.2927
  - Avg Speed:            10.36 chars/sec

### SPECIAL (CPU-VULKAN-VULKAN0) Configuration Details

- **Device Name**: `AMD Radeon Pro W6800 (RADV NAVI21)` (Total: 30704 MiB, Free: 29435 MiB)

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Benchmark Test Name:** `tts_cpu-vulkan-Vulkan0`
- **Device Setting:** `Default`
- **Special Setting:** `mode: hybrid`
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `SPECIAL (CPU-VULKAN-VULKAN0)`
- **GPU Memory Used:** 0.0 MB
- **CPU Memory Used:** 2172.5 MB
- **Benchmark Running Time:** 25.66 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LTTS_DEVICE=""`
  - `LTTS_EXTRA_ARGS=""`
  - `LTTS_HOST="127.0.0.1"`
  - `LTTS_MODE="hybrid"`
  - `LTTS_MODEL="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf"`
  - `LTTS_PORT="50095"`
  - `LTTS_THREADS="8"`
  - `LTTS_VOCODER="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-Tokenizer-12Hz-F16.gguf"`
- **Errors Count:** 0
- **Metrics:**
  - Generated Audio Duration: 19.98 seconds
  - Avg Synthesis Time:   25.50 seconds
  - Avg Real-Time Factor (RTF): 1.2763
  - Avg Speed:            10.75 chars/sec

### SPECIAL (CPU-VULKAN-VULKAN1) Configuration Details

- **Device Name**: `AMD Radeon Graphics (RADV RENOIR)` (Total: 72645 MiB, Free: 72616 MiB)

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Benchmark Test Name:** `tts_cpu-vulkan-Vulkan1`
- **Device Setting:** `Default`
- **Special Setting:** `mode: hybrid`
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `SPECIAL (CPU-VULKAN-VULKAN1)`
- **GPU Memory Used:** 1803.3 MB
- **CPU Memory Used:** 2164.1 MB
- **Benchmark Running Time:** 24.65 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LTTS_DEVICE=""`
  - `LTTS_EXTRA_ARGS=""`
  - `LTTS_HOST="127.0.0.1"`
  - `LTTS_MODE="hybrid"`
  - `LTTS_MODEL="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf"`
  - `LTTS_PORT="50095"`
  - `LTTS_THREADS="8"`
  - `LTTS_VOCODER="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-Tokenizer-12Hz-F16.gguf"`
- **Errors Count:** 0
- **Metrics:**
  - Generated Audio Duration: 19.66 seconds
  - Avg Synthesis Time:   24.52 seconds
  - Avg Real-Time Factor (RTF): 1.2471
  - Avg Speed:            11.18 chars/sec

