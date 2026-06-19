# LLM Caching Optimization Benchmarks

**Benchmark Run Time:** `2026-06-19 15:27:53`

## Local Inference Services Benchmarks

We ran local benchmarks for text embedding, text-to-speech (TTS), speech-to-text (STT), document reranking, and image generation on the AMD Radeon RX 7900 XTX hardware target. All services run inside isolated sandboxed environments.

### 📊 Performance Comparison Matrix

#### Text Chat (`local-chat`)
| Configuration | Test Name | GPU | Special Setting | Avg Chat TTFT | Avg Chat Prefill | Chat TTFT (Warmup) | Chat Gen Speed | Avg Chat Gen | Chat Image TTFT | Chat Image Gen | Chat GPU Mem | Chat CPU Mem |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **HIP-ROCM0** | chat_hip-ROCm0 | ROCm0 | Layers: 999 | 48373.39 ms | 641.70 t/s | 241.67 ms | 102.13 t/s | 65.73 t/s | 1454.27 ms | 98.68 t/s | 20668.3 MB | 2018.8 MB |
| **VULKAN-VULKAN0** | chat_vulkan-Vulkan0 | Vulkan0 | Layers: 999 (Context: 20%) | 58637.45 ms | 99.19 t/s | 1635.91 ms | 13.60 t/s | 12.59 t/s | 15953.69 ms | 13.38 t/s | 14468.3 MB | 1214.7 MB |
| **VULKAN-VULKAN1** | chat_vulkan-Vulkan1 | Vulkan1 | Layers: 999 | 14547.24 ms | 2133.81 t/s | 141.09 ms | 124.99 t/s | 111.94 t/s | 1430.75 ms | 124.14 t/s | 19197.6 MB | 1358.5 MB |
| **CPU** | chat_cpu | none | Layers: 0 (Context: 5%) | 40361.53 ms | 36.50 t/s | 655.06 ms | 13.30 t/s | 12.64 t/s | 42711.75 ms | 12.80 t/s | 1168.7 MB | 21392.5 MB |
| **CPU-BLAS** | chat_cpu-blas | BLAS | Layers: 0 (Context: 5%) | 41145.79 ms | 35.80 t/s | 655.60 ms | 13.21 t/s | 12.56 t/s | 42880.55 ms | 12.73 t/s | 1168.7 MB | 21394.2 MB |

#### Text Embedding (`local-embedding`)
| Configuration | Test Name | GPU | Special Setting | Embedding Throughput | Embedding Latency (Avg) | Embedding GPU Mem | Embedding CPU Mem |
|---|---|---|---|---|---|---|---|
| **HIP-ROCM0** | embedding_hip-ROCm0 | ROCm0 | Layers: 999 | 1799.58 t/s | 4210.2 ms | 7119.7 MB | 10116.0 MB |
| **VULKAN-VULKAN0** | embedding_vulkan-Vulkan0 | Vulkan0 | Layers: 999 | -fail- | -fail- | -fail- | -fail- |
| **VULKAN-VULKAN1** | embedding_vulkan-Vulkan1 | Vulkan1 | Layers: 999 | -fail- | -fail- | -fail- | -fail- |
| **CPU** | embedding_cpu | none | Layers: 0 | 99.29 t/s | 82506.8 ms | 0.1 MB | 11898.1 MB |
| **CPU-BLAS** | embedding_cpu-blas | BLAS | Layers: 999 | 97.88 t/s | 83693.3 ms | 0.1 MB | 11898.8 MB |

#### Document Reranking (`local-rerank`)
| Configuration | Test Name | GPU | Special Setting | Avg Reranking Time | Avg Token Speed | Avg Docs Throughput | GPU Mem | CPU Mem |
|---|---|---|---|---|---|---|---|---|
| **HIP-ROCM0** | rerank_hip-ROCm0 | ROCm0 | Layers: 99 | 0.00 ms | 0.00 tokens/s | 0.00 docs/s | 2719.6 MB | 827.6 MB |
| **VULKAN-VULKAN0** | rerank_vulkan-Vulkan0 | Vulkan0 | Layers: 99 | 0.00 ms | 0.00 tokens/s | 0.00 docs/s | 1574.7 MB | 248.0 MB |
| **VULKAN-VULKAN1** | rerank_vulkan-Vulkan1 | Vulkan1 | Layers: 99 | -fail- | -fail- | -fail- | -fail- | -fail- |
| **CPU** | rerank_cpu | none | Layers: 0 | 0.00 ms | 0.00 tokens/s | 0.00 docs/s | 0.1 MB | 2716.7 MB |
| **CPU-BLAS** | rerank_cpu-blas | BLAS | Layers: 99 | 0.00 ms | 0.00 tokens/s | 0.00 docs/s | 0.1 MB | 2714.9 MB |

#### Speech-to-Text (STT) (`local-speech-to-text`)
| Configuration | Test Name | GPU | Special Setting | Avg Transcribe Time | Avg Real-Time Factor (RTF) | Speedup vs Real-time | GPU Mem | CPU Mem |
|---|---|---|---|---|---|---|---|---|
| **HIP-ROCM0** | stt_hip-ROCm0 | 0 | Use GPU | FAIL | FAIL | FAIL | 1264.3 MB | 490.5 MB |
| **VULKAN-VULKAN0** | stt_vulkan-Vulkan0 | 0 | Use GPU | 5.51 s | 0.1224 | 8.2x | 808.8 MB | 127.2 MB |
| **VULKAN-VULKAN1** | stt_vulkan-Vulkan1 | 1 | Use GPU | 0.52 s | 0.0116 | 86.2x | 828.0 MB | 128.1 MB |
| **CPU** | stt_cpu | none | No GPU | 13.64 s | 0.3032 | 3.3x | 0.1 MB | 1102.3 MB |
| **CPU-BLAS** | stt_cpu-blas | BLAS | No GPU | 13.41 s | 0.2980 | 3.4x | 0.1 MB | 1102.4 MB |

#### Text-to-Speech (TTS) (`local-text-to-speech`)
| Configuration | Test Name | GPU | Special Setting | Avg Synthesis Time | Avg Real-Time Factor (RTF) | Speed (chars/s) | GPU Mem | CPU Mem |
|---|---|---|---|---|---|---|---|---|
| **HIP-ROCM0** | tts_hip-ROCm0 | ROCm0 | mode: gpu | FAIL | 0.9190 | 15.95 chars/s | 3585.8 MB | 1130.8 MB |
| **VULKAN-VULKAN0** | tts_vulkan-Vulkan0 | Vulkan0 | mode: gpu | FAIL | 2.4535 | 5.75 chars/s | 3352.5 MB | 678.8 MB |
| **VULKAN-VULKAN1** | tts_vulkan-Vulkan1 | Vulkan1 | mode: gpu | FAIL | 0.3272 | 41.91 chars/s | 3399.8 MB | 697.4 MB |
| **CPU** | tts_cpu | none | mode: cpu | FAIL | 1.6372 | 8.58 chars/s | 0.1 MB | 2985.3 MB |
| **CPU-BLAS** | tts_cpu-blas | BLAS | mode: cpu | FAIL | 1.6201 | 8.71 chars/s | 0.1 MB | 3030.5 MB |
| **CPU-HIP-ROCM0** | tts_cpu-hip-ROCm0 | ROCm0 | mode: hybrid | FAIL | 0.9215 | 15.25 chars/s | 3645.8 MB | 1148.2 MB |
| **CPU-HIP-ROCM1** | tts_cpu-hip-ROCm1 | ROCm1 | mode: hybrid | -fail- | -fail- | -fail- | -fail- | -fail- |
| **CPU-VULKAN-VULKAN0** | tts_cpu-vulkan-Vulkan0 | Vulkan0 | mode: hybrid | FAIL | 2.4484 | 5.74 chars/s | 3333.5 MB | 681.0 MB |
| **CPU-VULKAN-VULKAN1** | tts_cpu-vulkan-Vulkan1 | Vulkan1 | mode: hybrid | FAIL | 0.3264 | 45.10 chars/s | 3289.4 MB | 661.5 MB |

#### Image Generation (`local-image`)
| Configuration | Test Name | GPU | Special Setting | Avg Generation Time | GPU Mem | CPU Mem |
|---|---|---|---|---|---|---|
| **HIP-ROCM0** | image_hip-ROCm0 | rocm0 | Steps: 8 | 6.18 s | 10758.6 MB | 887.8 MB |
| **VULKAN-VULKAN0** | image_vulkan-Vulkan0 | vulkan0,te=cpu | Steps: 8 | 93.74 s | 6368.2 MB | 3807.5 MB |
| **VULKAN-VULKAN1** | image_vulkan-Vulkan1 | vulkan1 | Steps: 8 | 6.61 s | 9879.0 MB | 418.8 MB |
| **CPU** | image_cpu | cpu | Steps: 8 | 269.95 s | 0.1 MB | 10141.2 MB |
| **CPU-BLAS** | image_cpu-blas | cpu | Steps: 8 | 281.04 s | 0.1 MB | 10138.7 MB |

---

### ⚙️ Detailed Configuration Reports

### HIP-ROCM0 Configuration Details

- **Device Name**: `AMD Radeon RX 7900 XTX` (Total: 24560 MiB, Free: 24560 MiB)

#### Text Chat (`local-chat`)
- **Benchmark Test Name:** `chat_hip-ROCm0`
- **Device Setting:** `ROCm0`
- **Special Setting:** `Layers: 999`
- **Model:** `qwen3` (`Qwen3.6-35B-A3B-APEX-I-Compact`)
- **Execution Target:** `HIP-ROCM0`
- **GPU Memory Used:** 20668.3 MB
- **CPU Memory Used:** 2018.8 MB
- **Benchmark Running Time:** 62.40 s
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
  - `LCHAT_N_CTX="240384"`
  - `LCHAT_N_GPU_LAYERS="999"`
  - `LCHAT_PARALLEL="3"`
  - `LCHAT_PORT="50080"`
  - `LCHAT_SERVE_EMBEDDINGS="false"`
  - `LCHAT_THREADS="4"`
- **Errors Count:** 0
- **Warmup (Phase 0):**
  - TTFT (Prefill):       241.67 ms
  - Prefill Speed:        78.62 tokens/sec
  - Generation Speed:     102.13 tokens/sec
- **Generation (Phase 2):**
  - Avg Completion Tokens: 600.0
  - Avg TTFT (Prefill):   48373.39 ms
  - Avg Prefill Speed:    641.70 tokens/sec
  - Avg Generation Speed: 65.73 tokens/sec
  - Avg Decode Time:      9.13 s
- **Vision Description (Phase 4):**
  - Avg TTFT (Prefill):   1454.27 ms
  - Avg Generation Speed: 98.68 tokens/sec

#### Text Embedding (`local-embedding`)
- **Benchmark Test Name:** `embedding_hip-ROCm0`
- **Device Setting:** `ROCm0`
- **Special Setting:** `Layers: 999`
- **Model:** `qwen3-embedding` (`Qwen3-Embedding-0.6B-Q8_0.gguf`)
- **Execution Target:** `HIP-ROCM0`
- **GPU Memory Used:** 7119.7 MB
- **CPU Memory Used:** 10116.0 MB
- **Benchmark Running Time:** 25.63 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES="0"`
  - `HIP_VISIBLE_DEVICES="0"`
  - `LMBD_ALIAS="qwen3-embedding"`
  - `LMBD_DEVICE="ROCm0"`
  - `LMBD_EXTRA_ARGS=""`
  - `LMBD_HOST="127.0.0.1"`
  - `LMBD_MODEL="/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf"`
  - `LMBD_N_CTX="8192"`
  - `LMBD_N_GPU_LAYERS="999"`
  - `LMBD_PORT="50082"`
  - `LMBD_THREADS="4"`
- **Errors Count:** 0
- **Metrics:**
  - Avg Time/Run:         25.26 s
  - Avg Throughput:       1799.58 tokens/sec
  - Avg Chunk Latency:    4210.2 ms
  - Avg Chunk p50:        4571.7 ms
  - Avg Chunk p95:        5326.5 ms

#### Document Reranking (`local-rerank`)
- **Benchmark Test Name:** `rerank_hip-ROCm0`
- **Device Setting:** `ROCm0`
- **Special Setting:** `Layers: 99`
- **Model:** `qwen3-reranker` (`Qwen3-Reranker-0.6B.Q4_K_M.gguf`)
- **Execution Target:** `HIP-ROCM0`
- **GPU Memory Used:** 2719.6 MB
- **CPU Memory Used:** 827.6 MB
- **Benchmark Running Time:** 1.20 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES="0"`
  - `HIP_VISIBLE_DEVICES="0"`
  - `LRR_ALIAS="qwen3-reranker"`
  - `LRR_DEVICE="ROCm0"`
  - `LRR_EXTRA_ARGS="--flash-attn auto"`
  - `LRR_HOST="127.0.0.1"`
  - `LRR_MODEL="/data/public/machine-learning/models/reranker/Qwen3-Reranker-0.6B.Q4_K_M.gguf"`
  - `LRR_N_CTX="8192"`
  - `LRR_N_GPU_LAYERS="99"`
  - `LRR_PORT="50086"`
  - `LRR_THREADS="8"`
- **Errors Count:** 0
- **Metrics:**
  - Avg Reranking Time:   0.00 ms
  - Avg Docs Throughput:  0.00 docs/sec
  - Avg Token Speed:      0.00 tokens/sec

#### Speech-to-Text (STT) (`local-speech-to-text`)
- **Benchmark Test Name:** `stt_hip-ROCm0`
- **Device Setting:** `0`
- **Special Setting:** `Use GPU`
- **Model:** `whisper-1` (`ggml-large-v3-turbo-q5_0.bin`)
- **Execution Target:** `HIP-ROCM0`
- **GPU Memory Used:** 1264.3 MB
- **CPU Memory Used:** 490.5 MB
- **Benchmark Running Time:** 3.91 s
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
- **Errors Count:** 1
- **Top Errors:**
  - `Warning: STT Transcription text mismatch (garbled output)`
- **Metrics:**
  - Avg Transcribe Time:  FAIL
  - Avg Real-Time Factor (RTF): FAIL (FAIL faster than real-time)

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Benchmark Test Name:** `tts_hip-ROCm0`
- **Device Setting:** `ROCm0`
- **Special Setting:** `mode: gpu`
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `HIP-ROCM0`
- **GPU Memory Used:** 3585.8 MB
- **CPU Memory Used:** 1130.8 MB
- **Benchmark Running Time:** 17.33 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES="0"`
  - `HIP_VISIBLE_DEVICES="0"`
  - `LTTS_DEVICE="ROCm0"`
  - `LTTS_EXTRA_ARGS=""`
  - `LTTS_HOST="127.0.0.1"`
  - `LTTS_MODE="gpu"`
  - `LTTS_MODEL="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf"`
  - `LTTS_PORT="50095"`
  - `LTTS_THREADS="8"`
  - `LTTS_VOCODER="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-Tokenizer-12Hz-F16.gguf"`
- **Errors Count:** 1
- **Top Errors:**
  - `Warning: TTS Audio validation failed (STT process error)`
- **Metrics:**
  - Generated Audio Duration: FAIL
  - Avg Synthesis Time:   FAIL
  - Avg Real-Time Factor (RTF): 0.9190
  - Avg Speed:            15.95 chars/sec

#### Image Generation (`local-image`)
- **Benchmark Test Name:** `image_hip-ROCm0`
- **Device Setting:** `rocm0`
- **Special Setting:** `Steps: 8`
- **Model:** `z_image_turbo-Q8_0` (`z_image_turbo-Q8_0.gguf`)
- **Execution Target:** `HIP-ROCM0`
- **GPU Memory Used:** 10758.6 MB
- **CPU Memory Used:** 887.8 MB
- **Benchmark Running Time:** 6.32 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES="0"`
  - `HIP_VISIBLE_DEVICES="0"`
  - `LIMG_BACKEND="rocm0"`
  - `LIMG_CFG_SCALE="1.0"`
  - `LIMG_EXTRA_ARGS="--fa"`
  - `LIMG_HOST="127.0.0.1"`
  - `LIMG_LLM="/data/public/machine-learning/models/image/Qwen3-4B-Q4_K_M.gguf"`
  - `LIMG_MODEL="/data/public/machine-learning/models/image/z_image_turbo-Q8_0.gguf"`
  - `LIMG_PORT="50100"`
  - `LIMG_STEPS="8"`
  - `LIMG_THREADS="8"`
  - `LIMG_VAE="/data/public/machine-learning/models/image/ae.safetensors"`
- **Errors Count:** 0
- **Metrics:**
  - Avg Generation Time:  6.18 seconds

### VULKAN-VULKAN0 Configuration Details

- **Device Name**: `AMD Radeon Graphics` (Total: 16384 MiB, Free: 16384 MiB)

#### Text Chat (`local-chat`)
- **Benchmark Test Name:** `chat_vulkan-Vulkan0`
- **Device Setting:** `Vulkan0`
- **Special Setting:** `Layers: 999 (Context: 20%)`
- **Model:** `qwen3` (`Qwen3.6-35B-A3B-APEX-I-Compact`)
- **Execution Target:** `VULKAN-VULKAN0`
- **GPU Memory Used:** 14468.3 MB
- **CPU Memory Used:** 1214.7 MB
- **Benchmark Running Time:** 148.72 s
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
  - `LCHAT_N_CTX="48076"`
  - `LCHAT_N_GPU_LAYERS="999"`
  - `LCHAT_PARALLEL="3"`
  - `LCHAT_PORT="50080"`
  - `LCHAT_SERVE_EMBEDDINGS="false"`
  - `LCHAT_THREADS="4"`
- **Errors Count:** 0
- **Warmup (Phase 0):**
  - TTFT (Prefill):       1635.91 ms
  - Prefill Speed:        11.61 tokens/sec
  - Generation Speed:     13.60 tokens/sec
- **Generation (Phase 2):**
  - Avg Completion Tokens: 600.0
  - Avg TTFT (Prefill):   58637.45 ms
  - Avg Prefill Speed:    99.19 tokens/sec
  - Avg Generation Speed: 12.59 tokens/sec
  - Avg Decode Time:      47.66 s
- **Vision Description (Phase 4):**
  - Avg TTFT (Prefill):   15953.69 ms
  - Avg Generation Speed: 13.38 tokens/sec

#### Text Embedding (`local-embedding`)
- **Benchmark Test Name:** `embedding_vulkan-Vulkan0`
- **Device Setting:** `Vulkan0`
- **Special Setting:** `Layers: 999`
- **Model:** `qwen3-embedding` (`Qwen3-Embedding-0.6B-Q8_0.gguf`)
- **Execution Target:** `VULKAN-VULKAN0`
- **GPU Memory Used:** -fail-
- **CPU Memory Used:** -fail-
- **Benchmark Running Time:** -fail-
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LMBD_ALIAS="qwen3-embedding"`
  - `LMBD_DEVICE="Vulkan0"`
  - `LMBD_EXTRA_ARGS=""`
  - `LMBD_HOST="127.0.0.1"`
  - `LMBD_MODEL="/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf"`
  - `LMBD_N_CTX="8192"`
  - `LMBD_N_GPU_LAYERS="999"`
  - `LMBD_PORT="50082"`
  - `LMBD_THREADS="4"`
- **Errors Count:** 3
- **Top Errors:**
  - `[34m0.04.152.667[0m [35mW ggml_vulkan: Failed to allocate pinned memory (Requested buffer size exceeds device buffer size limit: ErrorOutOfDeviceMemory)`
  - `terminate called after throwing an instance of 'vk::DeviceLostError'`
  - `what():  vk::Queue::submit: ErrorDeviceLost`
- **Metrics:**
  - Avg Time/Run:         -n.a.-
  - Avg Throughput:       -fail-
  - Avg Chunk Latency:    -fail-
  - Avg Chunk p50:        -n.a.-
  - Avg Chunk p95:        -n.a.-

#### Document Reranking (`local-rerank`)
- **Benchmark Test Name:** `rerank_vulkan-Vulkan0`
- **Device Setting:** `Vulkan0`
- **Special Setting:** `Layers: 99`
- **Model:** `qwen3-reranker` (`Qwen3-Reranker-0.6B.Q4_K_M.gguf`)
- **Execution Target:** `VULKAN-VULKAN0`
- **GPU Memory Used:** 1574.7 MB
- **CPU Memory Used:** 248.0 MB
- **Benchmark Running Time:** 5.31 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LRR_ALIAS="qwen3-reranker"`
  - `LRR_DEVICE="Vulkan0"`
  - `LRR_EXTRA_ARGS="--flash-attn auto"`
  - `LRR_HOST="127.0.0.1"`
  - `LRR_MODEL="/data/public/machine-learning/models/reranker/Qwen3-Reranker-0.6B.Q4_K_M.gguf"`
  - `LRR_N_CTX="8192"`
  - `LRR_N_GPU_LAYERS="99"`
  - `LRR_PORT="50086"`
  - `LRR_THREADS="8"`
- **Errors Count:** 0
- **Metrics:**
  - Avg Reranking Time:   0.00 ms
  - Avg Docs Throughput:  0.00 docs/sec
  - Avg Token Speed:      0.00 tokens/sec

#### Speech-to-Text (STT) (`local-speech-to-text`)
- **Benchmark Test Name:** `stt_vulkan-Vulkan0`
- **Device Setting:** `0`
- **Special Setting:** `Use GPU`
- **Model:** `whisper-1` (`ggml-large-v3-turbo-q5_0.bin`)
- **Execution Target:** `VULKAN-VULKAN0`
- **GPU Memory Used:** 808.8 MB
- **CPU Memory Used:** 127.2 MB
- **Benchmark Running Time:** 5.71 s
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
  - Avg Transcribe Time:  5.51 seconds
  - Avg Real-Time Factor (RTF): 0.1224 (8.2x faster than real-time)

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Benchmark Test Name:** `tts_vulkan-Vulkan0`
- **Device Setting:** `Vulkan0`
- **Special Setting:** `mode: gpu`
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `VULKAN-VULKAN0`
- **GPU Memory Used:** 3352.5 MB
- **CPU Memory Used:** 678.8 MB
- **Benchmark Running Time:** 47.78 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LTTS_DEVICE="Vulkan0"`
  - `LTTS_EXTRA_ARGS=""`
  - `LTTS_HOST="127.0.0.1"`
  - `LTTS_MODE="gpu"`
  - `LTTS_MODEL="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf"`
  - `LTTS_PORT="50095"`
  - `LTTS_THREADS="8"`
  - `LTTS_VOCODER="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-Tokenizer-12Hz-F16.gguf"`
- **Errors Count:** 1
- **Top Errors:**
  - `Warning: TTS Audio validation failed (STT process error)`
- **Metrics:**
  - Generated Audio Duration: FAIL
  - Avg Synthesis Time:   FAIL
  - Avg Real-Time Factor (RTF): 2.4535
  - Avg Speed:            5.75 chars/sec

#### Image Generation (`local-image`)
- **Benchmark Test Name:** `image_vulkan-Vulkan0`
- **Device Setting:** `vulkan0,te=cpu`
- **Special Setting:** `Steps: 8`
- **Model:** `z_image_turbo-Q8_0` (`z_image_turbo-Q8_0.gguf`)
- **Execution Target:** `VULKAN-VULKAN0`
- **GPU Memory Used:** 6368.2 MB
- **CPU Memory Used:** 3807.5 MB
- **Benchmark Running Time:** 93.84 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LIMG_BACKEND="vulkan0,te=cpu"`
  - `LIMG_CFG_SCALE="1.0"`
  - `LIMG_EXTRA_ARGS="--fa"`
  - `LIMG_HOST="127.0.0.1"`
  - `LIMG_LLM="/data/public/machine-learning/models/image/Qwen3-4B-Q4_K_M.gguf"`
  - `LIMG_MODEL="/data/public/machine-learning/models/image/z_image_turbo-Q8_0.gguf"`
  - `LIMG_PORT="50100"`
  - `LIMG_STEPS="8"`
  - `LIMG_THREADS="8"`
  - `LIMG_VAE="/data/public/machine-learning/models/image/ae.safetensors"`
- **Errors Count:** 0
- **Metrics:**
  - Avg Generation Time:  93.74 seconds

### VULKAN-VULKAN1 Configuration Details

- **Device Name**: `AMD Radeon RX 7900 XTX` (Total: 24560 MiB, Free: 24560 MiB)

#### Text Chat (`local-chat`)
- **Benchmark Test Name:** `chat_vulkan-Vulkan1`
- **Device Setting:** `Vulkan1`
- **Special Setting:** `Layers: 999`
- **Model:** `qwen3` (`Qwen3.6-35B-A3B-APEX-I-Compact`)
- **Execution Target:** `VULKAN-VULKAN1`
- **GPU Memory Used:** 19197.6 MB
- **CPU Memory Used:** 1358.5 MB
- **Benchmark Running Time:** 24.23 s
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
  - `LCHAT_N_CTX="240384"`
  - `LCHAT_N_GPU_LAYERS="999"`
  - `LCHAT_PARALLEL="3"`
  - `LCHAT_PORT="50080"`
  - `LCHAT_SERVE_EMBEDDINGS="false"`
  - `LCHAT_THREADS="4"`
- **Errors Count:** 0
- **Warmup (Phase 0):**
  - TTFT (Prefill):       141.09 ms
  - Prefill Speed:        134.67 tokens/sec
  - Generation Speed:     124.99 tokens/sec
- **Generation (Phase 2):**
  - Avg Completion Tokens: 600.0
  - Avg TTFT (Prefill):   14547.24 ms
  - Avg Prefill Speed:    2133.81 tokens/sec
  - Avg Generation Speed: 111.94 tokens/sec
  - Avg Decode Time:      5.36 s
- **Vision Description (Phase 4):**
  - Avg TTFT (Prefill):   1430.75 ms
  - Avg Generation Speed: 124.14 tokens/sec

#### Text Embedding (`local-embedding`)
- **Benchmark Test Name:** `embedding_vulkan-Vulkan1`
- **Device Setting:** `Vulkan1`
- **Special Setting:** `Layers: 999`
- **Model:** `qwen3-embedding` (`Qwen3-Embedding-0.6B-Q8_0.gguf`)
- **Execution Target:** `VULKAN-VULKAN1`
- **GPU Memory Used:** -fail-
- **CPU Memory Used:** -fail-
- **Benchmark Running Time:** -fail-
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LMBD_ALIAS="qwen3-embedding"`
  - `LMBD_DEVICE="Vulkan1"`
  - `LMBD_EXTRA_ARGS=""`
  - `LMBD_HOST="127.0.0.1"`
  - `LMBD_MODEL="/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf"`
  - `LMBD_N_CTX="4096"`
  - `LMBD_N_GPU_LAYERS="999"`
  - `LMBD_PORT="50082"`
  - `LMBD_THREADS="4"`
- **Errors Count:** 0
- **Metrics:**
  - Avg Time/Run:         -n.a.-
  - Avg Throughput:       -fail-
  - Avg Chunk Latency:    -fail-
  - Avg Chunk p50:        -n.a.-
  - Avg Chunk p95:        -n.a.-

#### Document Reranking (`local-rerank`)
- **Benchmark Test Name:** `rerank_vulkan-Vulkan1`
- **Device Setting:** `Vulkan1`
- **Special Setting:** `Layers: 99`
- **Model:** `qwen3-reranker` (`Qwen3-Reranker-0.6B.Q4_K_M.gguf`)
- **Execution Target:** `VULKAN-VULKAN1`
- **GPU Memory Used:** -fail-
- **CPU Memory Used:** -fail-
- **Benchmark Running Time:** -fail-
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LRR_ALIAS="qwen3-reranker"`
  - `LRR_DEVICE="Vulkan1"`
  - `LRR_EXTRA_ARGS="--flash-attn auto"`
  - `LRR_HOST="127.0.0.1"`
  - `LRR_MODEL="/data/public/machine-learning/models/reranker/Qwen3-Reranker-0.6B.Q4_K_M.gguf"`
  - `LRR_N_CTX="8192"`
  - `LRR_N_GPU_LAYERS="99"`
  - `LRR_PORT="50086"`
  - `LRR_THREADS="8"`
- **Errors Count:** 0
- **Metrics:**
  - Avg Reranking Time:   -fail-
  - Avg Docs Throughput:  -fail-
  - Avg Token Speed:      -fail-

#### Speech-to-Text (STT) (`local-speech-to-text`)
- **Benchmark Test Name:** `stt_vulkan-Vulkan1`
- **Device Setting:** `1`
- **Special Setting:** `Use GPU`
- **Model:** `whisper-1` (`ggml-large-v3-turbo-q5_0.bin`)
- **Execution Target:** `VULKAN-VULKAN1`
- **GPU Memory Used:** 828.0 MB
- **CPU Memory Used:** 128.1 MB
- **Benchmark Running Time:** 0.70 s
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
  - Avg Transcribe Time:  0.52 seconds
  - Avg Real-Time Factor (RTF): 0.0116 (86.2x faster than real-time)

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Benchmark Test Name:** `tts_vulkan-Vulkan1`
- **Device Setting:** `Vulkan1`
- **Special Setting:** `mode: gpu`
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `VULKAN-VULKAN1`
- **GPU Memory Used:** 3399.8 MB
- **CPU Memory Used:** 697.4 MB
- **Benchmark Running Time:** 6.71 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LTTS_DEVICE="Vulkan1"`
  - `LTTS_EXTRA_ARGS=""`
  - `LTTS_HOST="127.0.0.1"`
  - `LTTS_MODE="gpu"`
  - `LTTS_MODEL="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf"`
  - `LTTS_PORT="50095"`
  - `LTTS_THREADS="8"`
  - `LTTS_VOCODER="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-Tokenizer-12Hz-F16.gguf"`
- **Errors Count:** 1
- **Top Errors:**
  - `Warning: TTS Audio validation failed (STT process error)`
- **Metrics:**
  - Generated Audio Duration: FAIL
  - Avg Synthesis Time:   FAIL
  - Avg Real-Time Factor (RTF): 0.3272
  - Avg Speed:            41.91 chars/sec

#### Image Generation (`local-image`)
- **Benchmark Test Name:** `image_vulkan-Vulkan1`
- **Device Setting:** `vulkan1`
- **Special Setting:** `Steps: 8`
- **Model:** `z_image_turbo-Q8_0` (`z_image_turbo-Q8_0.gguf`)
- **Execution Target:** `VULKAN-VULKAN1`
- **GPU Memory Used:** 9879.0 MB
- **CPU Memory Used:** 418.8 MB
- **Benchmark Running Time:** 6.73 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LIMG_BACKEND="vulkan1"`
  - `LIMG_CFG_SCALE="1.0"`
  - `LIMG_EXTRA_ARGS="--fa"`
  - `LIMG_HOST="127.0.0.1"`
  - `LIMG_LLM="/data/public/machine-learning/models/image/Qwen3-4B-Q4_K_M.gguf"`
  - `LIMG_MODEL="/data/public/machine-learning/models/image/z_image_turbo-Q8_0.gguf"`
  - `LIMG_PORT="50100"`
  - `LIMG_STEPS="8"`
  - `LIMG_THREADS="8"`
  - `LIMG_VAE="/data/public/machine-learning/models/image/ae.safetensors"`
- **Errors Count:** 0
- **Metrics:**
  - Avg Generation Time:  6.61 seconds

### CPU Configuration Details

#### Text Chat (`local-chat`)
- **Benchmark Test Name:** `chat_cpu`
- **Device Setting:** `none`
- **Special Setting:** `Layers: 0 (Context: 5%)`
- **Model:** `qwen3` (`Qwen3.6-35B-A3B-APEX-I-Compact`)
- **Execution Target:** `CPU`
- **GPU Memory Used:** 1168.7 MB
- **CPU Memory Used:** 21392.5 MB
- **Benchmark Running Time:** 156.52 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LCHAT_ALIAS="qwen3"`
  - `LCHAT_CHAT_TEMPLATE_ARGS="--chat-template-file /data/public/machine-learning/models/vision-text/Qwen3.6-chat_template.jinja"`
  - `LCHAT_DEVICE="none"`
  - `LCHAT_EXTRA_ARGS="--flash-attn auto --spec-type ngram-simple --spec-ngram-simple-size-n 6 --spec-ngram-simple-size-m 4"`
  - `LCHAT_HOST="127.0.0.1"`
  - `LCHAT_MMPROJ_ARGS="--mmproj /data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact-mmproj.gguf"`
  - `LCHAT_MODEL="/data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact.gguf"`
  - `LCHAT_N_CTX="12019"`
  - `LCHAT_N_GPU_LAYERS="0"`
  - `LCHAT_PARALLEL="3"`
  - `LCHAT_PORT="50080"`
  - `LCHAT_SERVE_EMBEDDINGS="false"`
  - `LCHAT_THREADS="4"`
- **Errors Count:** 0
- **Warmup (Phase 0):**
  - TTFT (Prefill):       655.06 ms
  - Prefill Speed:        29.00 tokens/sec
  - Generation Speed:     13.30 tokens/sec
- **Generation (Phase 2):**
  - Avg Completion Tokens: 600.0
  - Avg TTFT (Prefill):   40361.53 ms
  - Avg Prefill Speed:    36.50 tokens/sec
  - Avg Generation Speed: 12.64 tokens/sec
  - Avg Decode Time:      47.49 s
- **Vision Description (Phase 4):**
  - Avg TTFT (Prefill):   42711.75 ms
  - Avg Generation Speed: 12.80 tokens/sec

#### Text Embedding (`local-embedding`)
- **Benchmark Test Name:** `embedding_cpu`
- **Device Setting:** `none`
- **Special Setting:** `Layers: 0`
- **Model:** `qwen3-embedding` (`Qwen3-Embedding-0.6B-Q8_0.gguf`)
- **Execution Target:** `CPU`
- **GPU Memory Used:** 0.1 MB
- **CPU Memory Used:** 11898.1 MB
- **Benchmark Running Time:** 82.79 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LMBD_ALIAS="qwen3-embedding"`
  - `LMBD_DEVICE="none"`
  - `LMBD_EXTRA_ARGS=""`
  - `LMBD_HOST="127.0.0.1"`
  - `LMBD_MODEL="/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf"`
  - `LMBD_N_CTX="8192"`
  - `LMBD_N_GPU_LAYERS="0"`
  - `LMBD_PORT="50082"`
  - `LMBD_THREADS="4"`
- **Errors Count:** 0
- **Metrics:**
  - Avg Time/Run:         82.51 s
  - Avg Throughput:       99.29 tokens/sec
  - Avg Chunk Latency:    82506.8 ms
  - Avg Chunk p50:        82506.8 ms
  - Avg Chunk p95:        82506.8 ms

#### Document Reranking (`local-rerank`)
- **Benchmark Test Name:** `rerank_cpu`
- **Device Setting:** `none`
- **Special Setting:** `Layers: 0`
- **Model:** `qwen3-reranker` (`Qwen3-Reranker-0.6B.Q4_K_M.gguf`)
- **Execution Target:** `CPU`
- **GPU Memory Used:** 0.1 MB
- **CPU Memory Used:** 2716.7 MB
- **Benchmark Running Time:** 11.14 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LRR_ALIAS="qwen3-reranker"`
  - `LRR_DEVICE="none"`
  - `LRR_EXTRA_ARGS="--flash-attn auto"`
  - `LRR_HOST="127.0.0.1"`
  - `LRR_MODEL="/data/public/machine-learning/models/reranker/Qwen3-Reranker-0.6B.Q4_K_M.gguf"`
  - `LRR_N_CTX="8192"`
  - `LRR_N_GPU_LAYERS="0"`
  - `LRR_PORT="50086"`
  - `LRR_THREADS="8"`
- **Errors Count:** 0
- **Metrics:**
  - Avg Reranking Time:   0.00 ms
  - Avg Docs Throughput:  0.00 docs/sec
  - Avg Token Speed:      0.00 tokens/sec

#### Speech-to-Text (STT) (`local-speech-to-text`)
- **Benchmark Test Name:** `stt_cpu`
- **Device Setting:** `none`
- **Special Setting:** `No GPU`
- **Model:** `whisper-1` (`ggml-large-v3-turbo-q5_0.bin`)
- **Execution Target:** `CPU`
- **GPU Memory Used:** 0.1 MB
- **CPU Memory Used:** 1102.3 MB
- **Benchmark Running Time:** 13.85 s
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
  - Avg Transcribe Time:  13.64 seconds
  - Avg Real-Time Factor (RTF): 0.3032 (3.3x faster than real-time)

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Benchmark Test Name:** `tts_cpu`
- **Device Setting:** `none`
- **Special Setting:** `mode: cpu`
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `CPU`
- **GPU Memory Used:** 0.1 MB
- **CPU Memory Used:** 2985.3 MB
- **Benchmark Running Time:** 32.09 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LTTS_DEVICE="none"`
  - `LTTS_EXTRA_ARGS=""`
  - `LTTS_HOST="127.0.0.1"`
  - `LTTS_MODE="cpu"`
  - `LTTS_MODEL="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf"`
  - `LTTS_PORT="50095"`
  - `LTTS_THREADS="8"`
  - `LTTS_VOCODER="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-Tokenizer-12Hz-F16.gguf"`
- **Errors Count:** 1
- **Top Errors:**
  - `Warning: TTS Audio validation failed (STT process error)`
- **Metrics:**
  - Generated Audio Duration: FAIL
  - Avg Synthesis Time:   FAIL
  - Avg Real-Time Factor (RTF): 1.6372
  - Avg Speed:            8.58 chars/sec

#### Image Generation (`local-image`)
- **Benchmark Test Name:** `image_cpu`
- **Device Setting:** `cpu`
- **Special Setting:** `Steps: 8`
- **Model:** `z_image_turbo-Q8_0` (`z_image_turbo-Q8_0.gguf`)
- **Execution Target:** `CPU`
- **GPU Memory Used:** 0.1 MB
- **CPU Memory Used:** 10141.2 MB
- **Benchmark Running Time:** 270.07 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LIMG_BACKEND="cpu"`
  - `LIMG_CFG_SCALE="1.0"`
  - `LIMG_EXTRA_ARGS="--fa"`
  - `LIMG_HOST="127.0.0.1"`
  - `LIMG_LLM="/data/public/machine-learning/models/image/Qwen3-4B-Q4_K_M.gguf"`
  - `LIMG_MODEL="/data/public/machine-learning/models/image/z_image_turbo-Q8_0.gguf"`
  - `LIMG_PORT="50100"`
  - `LIMG_STEPS="8"`
  - `LIMG_THREADS="8"`
  - `LIMG_VAE="/data/public/machine-learning/models/image/ae.safetensors"`
- **Errors Count:** 0
- **Metrics:**
  - Avg Generation Time:  269.95 seconds

### CPU-BLAS Configuration Details

#### Text Chat (`local-chat`)
- **Benchmark Test Name:** `chat_cpu-blas`
- **Device Setting:** `BLAS`
- **Special Setting:** `Layers: 0 (Context: 5%)`
- **Model:** `qwen3` (`Qwen3.6-35B-A3B-APEX-I-Compact`)
- **Execution Target:** `CPU-BLAS`
- **GPU Memory Used:** 1168.7 MB
- **CPU Memory Used:** 21394.2 MB
- **Benchmark Running Time:** 157.92 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LCHAT_ALIAS="qwen3"`
  - `LCHAT_CHAT_TEMPLATE_ARGS="--chat-template-file /data/public/machine-learning/models/vision-text/Qwen3.6-chat_template.jinja"`
  - `LCHAT_DEVICE="BLAS"`
  - `LCHAT_EXTRA_ARGS="--flash-attn auto --spec-type ngram-simple --spec-ngram-simple-size-n 6 --spec-ngram-simple-size-m 4"`
  - `LCHAT_HOST="127.0.0.1"`
  - `LCHAT_MMPROJ_ARGS="--mmproj /data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact-mmproj.gguf"`
  - `LCHAT_MODEL="/data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact.gguf"`
  - `LCHAT_N_CTX="12019"`
  - `LCHAT_N_GPU_LAYERS="0"`
  - `LCHAT_PARALLEL="3"`
  - `LCHAT_PORT="50080"`
  - `LCHAT_SERVE_EMBEDDINGS="false"`
  - `LCHAT_THREADS="4"`
- **Errors Count:** 0
- **Warmup (Phase 0):**
  - TTFT (Prefill):       655.60 ms
  - Prefill Speed:        28.98 tokens/sec
  - Generation Speed:     13.21 tokens/sec
- **Generation (Phase 2):**
  - Avg Completion Tokens: 600.0
  - Avg TTFT (Prefill):   41145.79 ms
  - Avg Prefill Speed:    35.80 tokens/sec
  - Avg Generation Speed: 12.56 tokens/sec
  - Avg Decode Time:      47.79 s
- **Vision Description (Phase 4):**
  - Avg TTFT (Prefill):   42880.55 ms
  - Avg Generation Speed: 12.73 tokens/sec

#### Text Embedding (`local-embedding`)
- **Benchmark Test Name:** `embedding_cpu-blas`
- **Device Setting:** `BLAS`
- **Special Setting:** `Layers: 999`
- **Model:** `qwen3-embedding` (`Qwen3-Embedding-0.6B-Q8_0.gguf`)
- **Execution Target:** `CPU-BLAS`
- **GPU Memory Used:** 0.1 MB
- **CPU Memory Used:** 11898.8 MB
- **Benchmark Running Time:** 83.98 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LMBD_ALIAS="qwen3-embedding"`
  - `LMBD_DEVICE="BLAS"`
  - `LMBD_EXTRA_ARGS=""`
  - `LMBD_HOST="127.0.0.1"`
  - `LMBD_MODEL="/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf"`
  - `LMBD_N_CTX="8192"`
  - `LMBD_N_GPU_LAYERS="0"`
  - `LMBD_PORT="50082"`
  - `LMBD_THREADS="4"`
- **Errors Count:** 0
- **Metrics:**
  - Avg Time/Run:         83.69 s
  - Avg Throughput:       97.88 tokens/sec
  - Avg Chunk Latency:    83693.3 ms
  - Avg Chunk p50:        83693.3 ms
  - Avg Chunk p95:        83693.3 ms

#### Document Reranking (`local-rerank`)
- **Benchmark Test Name:** `rerank_cpu-blas`
- **Device Setting:** `BLAS`
- **Special Setting:** `Layers: 99`
- **Model:** `qwen3-reranker` (`Qwen3-Reranker-0.6B.Q4_K_M.gguf`)
- **Execution Target:** `CPU-BLAS`
- **GPU Memory Used:** 0.1 MB
- **CPU Memory Used:** 2714.9 MB
- **Benchmark Running Time:** 11.24 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LRR_ALIAS="qwen3-reranker"`
  - `LRR_DEVICE="BLAS"`
  - `LRR_EXTRA_ARGS="--flash-attn auto"`
  - `LRR_HOST="127.0.0.1"`
  - `LRR_MODEL="/data/public/machine-learning/models/reranker/Qwen3-Reranker-0.6B.Q4_K_M.gguf"`
  - `LRR_N_CTX="8192"`
  - `LRR_N_GPU_LAYERS="0"`
  - `LRR_PORT="50086"`
  - `LRR_THREADS="8"`
- **Errors Count:** 0
- **Metrics:**
  - Avg Reranking Time:   0.00 ms
  - Avg Docs Throughput:  0.00 docs/sec
  - Avg Token Speed:      0.00 tokens/sec

#### Speech-to-Text (STT) (`local-speech-to-text`)
- **Benchmark Test Name:** `stt_cpu-blas`
- **Device Setting:** `BLAS`
- **Special Setting:** `No GPU`
- **Model:** `whisper-1` (`ggml-large-v3-turbo-q5_0.bin`)
- **Execution Target:** `CPU-BLAS`
- **GPU Memory Used:** 0.1 MB
- **CPU Memory Used:** 1102.4 MB
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
  - Avg Transcribe Time:  13.41 seconds
  - Avg Real-Time Factor (RTF): 0.2980 (3.4x faster than real-time)

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Benchmark Test Name:** `tts_cpu-blas`
- **Device Setting:** `BLAS`
- **Special Setting:** `mode: cpu`
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `CPU-BLAS`
- **GPU Memory Used:** 0.1 MB
- **CPU Memory Used:** 3030.5 MB
- **Benchmark Running Time:** 31.59 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LTTS_DEVICE="BLAS"`
  - `LTTS_EXTRA_ARGS=""`
  - `LTTS_HOST="127.0.0.1"`
  - `LTTS_MODE="cpu"`
  - `LTTS_MODEL="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf"`
  - `LTTS_PORT="50095"`
  - `LTTS_THREADS="8"`
  - `LTTS_VOCODER="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-Tokenizer-12Hz-F16.gguf"`
- **Errors Count:** 1
- **Top Errors:**
  - `Warning: TTS Audio validation failed (STT process error)`
- **Metrics:**
  - Generated Audio Duration: FAIL
  - Avg Synthesis Time:   FAIL
  - Avg Real-Time Factor (RTF): 1.6201
  - Avg Speed:            8.71 chars/sec

#### Image Generation (`local-image`)
- **Benchmark Test Name:** `image_cpu-blas`
- **Device Setting:** `cpu`
- **Special Setting:** `Steps: 8`
- **Model:** `z_image_turbo-Q8_0` (`z_image_turbo-Q8_0.gguf`)
- **Execution Target:** `CPU-BLAS`
- **GPU Memory Used:** 0.1 MB
- **CPU Memory Used:** 10138.7 MB
- **Benchmark Running Time:** 281.13 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LIMG_BACKEND="cpu"`
  - `LIMG_CFG_SCALE="1.0"`
  - `LIMG_EXTRA_ARGS="--fa"`
  - `LIMG_HOST="127.0.0.1"`
  - `LIMG_LLM="/data/public/machine-learning/models/image/Qwen3-4B-Q4_K_M.gguf"`
  - `LIMG_MODEL="/data/public/machine-learning/models/image/z_image_turbo-Q8_0.gguf"`
  - `LIMG_PORT="50100"`
  - `LIMG_STEPS="8"`
  - `LIMG_THREADS="8"`
  - `LIMG_VAE="/data/public/machine-learning/models/image/ae.safetensors"`
- **Errors Count:** 0
- **Metrics:**
  - Avg Generation Time:  281.04 seconds

### SPECIAL (CPU-HIP-ROCM0) Configuration Details

- **Device Name**: `AMD Radeon RX 7900 XTX` (Total: 24560 MiB, Free: 24560 MiB)

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Benchmark Test Name:** `tts_cpu-hip-ROCm0`
- **Device Setting:** `ROCm0`
- **Special Setting:** `mode: hybrid`
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `SPECIAL (CPU-HIP-ROCM0)`
- **GPU Memory Used:** 3645.8 MB
- **CPU Memory Used:** 1148.2 MB
- **Benchmark Running Time:** 18.13 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES="0"`
  - `HIP_VISIBLE_DEVICES="0"`
  - `LTTS_DEVICE="ROCm0"`
  - `LTTS_EXTRA_ARGS=""`
  - `LTTS_HOST="127.0.0.1"`
  - `LTTS_MODE="hybrid"`
  - `LTTS_MODEL="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf"`
  - `LTTS_PORT="50095"`
  - `LTTS_THREADS="8"`
  - `LTTS_VOCODER="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-Tokenizer-12Hz-F16.gguf"`
- **Errors Count:** 1
- **Top Errors:**
  - `Warning: TTS Audio validation failed (STT process error)`
- **Metrics:**
  - Generated Audio Duration: FAIL
  - Avg Synthesis Time:   FAIL
  - Avg Real-Time Factor (RTF): 0.9215
  - Avg Speed:            15.25 chars/sec

### SPECIAL (CPU-HIP-ROCM1) Configuration Details

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Benchmark Test Name:** `tts_cpu-hip-ROCm1`
- **Device Setting:** `ROCm1`
- **Special Setting:** `mode: hybrid`
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `SPECIAL (CPU-HIP-ROCM1)`
- **GPU Memory Used:** -fail-
- **CPU Memory Used:** -fail-
- **Benchmark Running Time:** -fail-
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES="1"`
  - `HIP_VISIBLE_DEVICES="1"`
  - `LTTS_DEVICE="ROCm1"`
  - `LTTS_EXTRA_ARGS=""`
  - `LTTS_HOST="127.0.0.1"`
  - `LTTS_MODE="hybrid"`
  - `LTTS_MODEL="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf"`
  - `LTTS_PORT="50095"`
  - `LTTS_THREADS="8"`
  - `LTTS_VOCODER="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-Tokenizer-12Hz-F16.gguf"`
- **Errors Count:** 1
- **Top Errors:**
  - `Error: qwen3-tts-server failed to start or port timed out`
- **Metrics:**
  - Generated Audio Duration: -fail-
  - Avg Synthesis Time:   -fail-
  - Avg Real-Time Factor (RTF): -fail-
  - Avg Speed:            -fail-

### SPECIAL (CPU-VULKAN-VULKAN0) Configuration Details

- **Device Name**: `AMD Radeon Graphics` (Total: 16384 MiB, Free: 16384 MiB)

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Benchmark Test Name:** `tts_cpu-vulkan-Vulkan0`
- **Device Setting:** `Vulkan0`
- **Special Setting:** `mode: hybrid`
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `SPECIAL (CPU-VULKAN-VULKAN0)`
- **GPU Memory Used:** 3333.5 MB
- **CPU Memory Used:** 681.0 MB
- **Benchmark Running Time:** 47.88 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LTTS_DEVICE="Vulkan0"`
  - `LTTS_EXTRA_ARGS=""`
  - `LTTS_HOST="127.0.0.1"`
  - `LTTS_MODE="hybrid"`
  - `LTTS_MODEL="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf"`
  - `LTTS_PORT="50095"`
  - `LTTS_THREADS="8"`
  - `LTTS_VOCODER="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-Tokenizer-12Hz-F16.gguf"`
- **Errors Count:** 1
- **Top Errors:**
  - `Warning: TTS Audio validation failed (STT process error)`
- **Metrics:**
  - Generated Audio Duration: FAIL
  - Avg Synthesis Time:   FAIL
  - Avg Real-Time Factor (RTF): 2.4484
  - Avg Speed:            5.74 chars/sec

### SPECIAL (CPU-VULKAN-VULKAN1) Configuration Details

- **Device Name**: `AMD Radeon RX 7900 XTX` (Total: 24560 MiB, Free: 24560 MiB)

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Benchmark Test Name:** `tts_cpu-vulkan-Vulkan1`
- **Device Setting:** `Vulkan1`
- **Special Setting:** `mode: hybrid`
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `SPECIAL (CPU-VULKAN-VULKAN1)`
- **GPU Memory Used:** 3289.4 MB
- **CPU Memory Used:** 661.5 MB
- **Benchmark Running Time:** 6.21 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LTTS_DEVICE="Vulkan1"`
  - `LTTS_EXTRA_ARGS=""`
  - `LTTS_HOST="127.0.0.1"`
  - `LTTS_MODE="hybrid"`
  - `LTTS_MODEL="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf"`
  - `LTTS_PORT="50095"`
  - `LTTS_THREADS="8"`
  - `LTTS_VOCODER="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-Tokenizer-12Hz-F16.gguf"`
- **Errors Count:** 1
- **Top Errors:**
  - `Warning: TTS Audio validation failed (STT process error)`
- **Metrics:**
  - Generated Audio Duration: FAIL
  - Avg Synthesis Time:   FAIL
  - Avg Real-Time Factor (RTF): 0.3264
  - Avg Speed:            45.10 chars/sec

