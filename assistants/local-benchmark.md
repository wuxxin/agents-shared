# LLM Caching Optimization Benchmarks

**Benchmark Run Time:** `2026-06-19 13:39:58`

## Local Inference Services Benchmarks

We ran local benchmarks for text embedding, text-to-speech (TTS), speech-to-text (STT), document reranking, and image generation on the AMD Radeon RX 7900 XTX hardware target. All services run inside isolated sandboxed environments.

### 📊 Performance Comparison Matrix

#### Text Chat (`local-chat`)
| Configuration | Test Name | GPU | Special Setting | Avg Chat TTFT | Avg Chat Prefill | Chat TTFT (Warmup) | Chat Gen Speed | Avg Chat Gen | Chat Image TTFT | Chat Image Gen | Chat GPU Mem | Chat CPU Mem |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **HIP-ROCM0** | chat_hip-ROCm0 | ROCm0 | Layers: 999 | 27709.08 ms | 1120.25 t/s | 56.06 ms | 73.59 t/s | 43.96 t/s | 520.12 ms | 48.12 t/s | 14520.0 MB | 1200.0 MB |
| **VULKAN-VULKAN0** | chat_vulkan-Vulkan0 | Vulkan0 | Layers: 999 (Context: 20%) | 31865.44 ms | 974.13 t/s | 64.47 ms | 63.99 t/s | 38.23 t/s | 598.14 ms | 41.84 t/s | 14850.0 MB | 1250.0 MB |
| **VULKAN-VULKAN1** | chat_vulkan-Vulkan1 | Vulkan1 | Layers: 999 | 31865.44 ms | 974.13 t/s | 64.47 ms | 63.99 t/s | 38.23 t/s | 598.14 ms | 41.84 t/s | 14850.0 MB | 1250.0 MB |
| **CPU** | chat_cpu | Default | Layers: 0 (Context: 5%) | 124690.86 ms | 248.94 t/s | 252.27 ms | 16.35 t/s | 9.77 t/s | 2340.54 ms | 10.69 t/s | 0.0 MB | 0.0 MB |

#### Text Embedding (`local-embedding`)
| Configuration | Test Name | GPU | Special Setting | Embedding Throughput | Embedding Latency (Avg) | Embedding GPU Mem | Embedding CPU Mem |
|---|---|---|---|---|---|---|---|
| **HIP-ROCM0** | embedding_hip-ROCm0 | ROCm0 | Layers: 999 | 5019.28 t/s | 1509.5 ms | 2620.0 MB | 350.0 MB |
| **VULKAN-VULKAN0** | embedding_vulkan-Vulkan0 | Vulkan0 | Layers: 999 | 4364.59 t/s | 1735.9 ms | 2650.0 MB | 360.0 MB |
| **VULKAN-VULKAN1** | embedding_vulkan-Vulkan1 | Vulkan1 | Layers: 999 | 4364.59 t/s | 1735.9 ms | 2650.0 MB | 360.0 MB |
| **CPU** | embedding_cpu | BLAS | Layers: 0 | 1115.40 t/s | 6792.8 ms | 0.0 MB | 2500.0 MB |

#### Document Reranking (`local-rerank`)
| Configuration | Test Name | GPU | Special Setting | Avg Reranking Time | Avg Token Speed | Avg Docs Throughput | GPU Mem | CPU Mem |
|---|---|---|---|---|---|---|---|---|
| **HIP-ROCM0** | rerank_hip-ROCm0 | ROCm0 | Layers: 99 | 25761.59 ms | 133.49 tokens/s | 0.39 docs/s | 680.0 MB | 250.0 MB |
| **VULKAN-VULKAN0** | rerank_vulkan-Vulkan0 | Vulkan0 | Layers: 99 | 29625.83 ms | 116.08 tokens/s | 0.34 docs/s | 720.0 MB | 260.0 MB |
| **VULKAN-VULKAN1** | rerank_vulkan-Vulkan1 | Vulkan1 | Layers: 99 | 29625.83 ms | 116.08 tokens/s | 0.34 docs/s | 720.0 MB | 260.0 MB |
| **CPU** | rerank_cpu | BLAS | Layers: 0 | 115927.15 ms | 29.66 tokens/s | 0.09 docs/s | 0.0 MB | 600.0 MB |

#### Speech-to-Text (STT) (`local-speech-to-text`)
| Configuration | Test Name | GPU | Special Setting | Avg Transcribe Time | Avg Real-Time Factor (RTF) | Speedup vs Real-time | GPU Mem | CPU Mem |
|---|---|---|---|---|---|---|---|---|
| **HIP-ROCM0** | stt_hip-ROCm0 | 0 | Use GPU | 1.45 s | 0.0321 | 31.2x | 1820.0 MB | 450.0 MB |
| **VULKAN-VULKAN0** | stt_vulkan-Vulkan0 | 0 | Use GPU | 1.67 s | 0.0369 | 27.1x | 1950.0 MB | 460.0 MB |
| **VULKAN-VULKAN1** | stt_vulkan-Vulkan1 | 0 | Use GPU | 1.67 s | 0.0369 | 27.1x | 1950.0 MB | 460.0 MB |
| **CPU** | stt_cpu | Default | No GPU | 6.52 s | 0.1444 | 6.9x | 0.0 MB | 1200.0 MB |

#### Text-to-Speech (TTS) (`local-text-to-speech`)
| Configuration | Test Name | GPU | Special Setting | Avg Synthesis Time | Avg Real-Time Factor (RTF) | Speed (chars/s) | GPU Mem | CPU Mem |
|---|---|---|---|---|---|---|---|---|
| **HIP-ROCM0** | tts_hip-ROCm0 | ROCm0 | mode: gpu | 23.47 s | 1.4914 | 11.67 chars/s | 0.0 MB | 0.0 MB |
| **VULKAN-VULKAN0** | tts_vulkan-Vulkan0 | Vulkan0 | mode: gpu | 23.47 s | 1.4914 | 11.67 chars/s | 0.0 MB | 0.0 MB |
| **VULKAN-VULKAN1** | tts_vulkan-Vulkan1 | Vulkan1 | mode: gpu | 23.47 s | 1.4914 | 11.67 chars/s | 0.0 MB | 0.0 MB |
| **CPU** | tts_cpu | cpu | mode: cpu | 105.61 s | 6.7113 | 2.59 chars/s | 0.0 MB | 800.0 MB |
| **CPU-HIP-ROCM0** | tts_cpu-hip-ROCm0 | ROCm0 | mode: hybrid | 23.47 s | 1.4914 | 11.67 chars/s | 850.0 MB | 1500.0 MB |
| **CPU-HIP-ROCM1** | tts_cpu-hip-ROCm1 | ROCm1 | mode: hybrid | 23.47 s | 1.4914 | 11.67 chars/s | 850.0 MB | 1500.0 MB |
| **CPU-VULKAN-VULKAN0** | tts_cpu-vulkan-Vulkan0 | Vulkan0 | mode: hybrid | 23.47 s | 1.4914 | 11.67 chars/s | 850.0 MB | 1500.0 MB |
| **CPU-VULKAN-VULKAN1** | tts_cpu-vulkan-Vulkan1 | Vulkan1 | mode: hybrid | 23.47 s | 1.4914 | 11.67 chars/s | 850.0 MB | 1500.0 MB |

#### Image Generation (`local-image`)
| Configuration | Test Name | GPU | Special Setting | Avg Generation Time | GPU Mem | CPU Mem |
|---|---|---|---|---|---|---|
| **HIP-ROCM0** | image_hip-ROCm0 | rocm0 | Steps: 8 | 2.45 s | 8500.0 MB | 500.0 MB |
| **VULKAN-VULKAN0** | image_vulkan-Vulkan0 | vulkan0,te=cpu | Steps: 8 | 2.82 s | 8800.0 MB | 550.0 MB |
| **VULKAN-VULKAN1** | image_vulkan-Vulkan1 | vulkan1 | Steps: 8 | 2.82 s | 8800.0 MB | 550.0 MB |
| **CPU** | image_cpu | cpu | Steps: 8 | 11.03 s | 0.0 MB | 9500.0 MB |

---

### ⚙️ Detailed Configuration Reports

### HIP-ROCM0 Configuration Details

- **Device Name**: `AMD Radeon RX 7900 XTX` (Total: 24576 MiB, Free: 24576 MiB)

#### Text Chat (`local-chat`)
- **Benchmark Test Name:** `chat_hip-ROCm0`
- **Device Setting:** `ROCm0`
- **Special Setting:** `Layers: 999`
- **Model:** `qwen3` (`Qwen3.6-35B-A3B-APEX-I-Compact`)
- **Execution Target:** `HIP-ROCM0`
- **GPU Memory Used:** 14520.0 MB
- **CPU Memory Used:** 1200.0 MB
- **Benchmark Running Time:** 15.40 s
- **Active Environment Settings:**
  - `LCHAT_ALIAS="qwen3"`
  - `LCHAT_CHAT_TEMPLATE_ARGS="--chat-template-file /data/public/machine-learning/models/vision-text/Qwen3.6-chat_template.jinja"`
  - `LCHAT_DEVICE="ROCm0"`
  - `LCHAT_EXTRA_ARGS="--flash-attn on --spec-type ngram-simple --spec-ngram-simple-size-n 6 --spec-ngram-simple-size-m 4"`
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
  - TTFT (Prefill):       56.06 ms
  - Prefill Speed:        338.90 tokens/sec
  - Generation Speed:     73.59 tokens/sec
- **Generation (Phase 2):**
  - Avg Completion Tokens: 600.0
  - Avg TTFT (Prefill):   27709.08 ms
  - Avg Prefill Speed:    1120.25 tokens/sec
  - Avg Generation Speed: 43.96 tokens/sec
  - Avg Decode Time:      13.65 s
- **Vision Description (Phase 4):**
  - Avg TTFT (Prefill):   520.12 ms
  - Avg Generation Speed: 48.12 tokens/sec

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
  - `LMBD_ALIAS="qwen3-embedding"`
  - `LMBD_DEVICE="ROCm0"`
  - `LMBD_EXTRA_ARGS="--flash-attn on"`
  - `LMBD_HOST="127.0.0.1"`
  - `LMBD_MODEL="/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf"`
  - `LMBD_N_CTX="8192"`
  - `LMBD_N_GPU_LAYERS="999"`
  - `LMBD_PORT="50082"`
  - `LMBD_THREADS="4"`
- **Errors Count:** 0
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
  - `LRR_ALIAS="qwen3-reranker"`
  - `LRR_DEVICE="ROCm0"`
  - `LRR_EXTRA_ARGS="--flash-attn on"`
  - `LRR_HOST="127.0.0.1"`
  - `LRR_MODEL="/data/public/machine-learning/models/reranker/Qwen3-Reranker-0.6B.Q4_K_M.gguf"`
  - `LRR_N_CTX="8192"`
  - `LRR_N_GPU_LAYERS="99"`
  - `LRR_PORT="50086"`
  - `LRR_THREADS="8"`
- **Errors Count:** 0
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
  - `LTTS_EXTRA_ARGS=""`
  - `LTTS_HOST="127.0.0.1"`
  - `LTTS_MODE="gpu"`
  - `LTTS_MODEL="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf"`
  - `LTTS_PORT="50095"`
  - `LTTS_THREADS="8"`
  - `LTTS_VOCODER="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-Tokenizer-12Hz-F16.gguf"`
- **Errors Count:** 0
- **Metrics:**
  - Generated Audio Duration: 15.74 seconds
  - Avg Synthesis Time:   23.47 seconds
  - Avg Real-Time Factor (RTF): 1.4914
  - Avg Speed:            11.67 chars/sec

#### Image Generation (`local-image`)
- **Benchmark Test Name:** `image_hip-ROCm0`
- **Device Setting:** `rocm0`
- **Special Setting:** `Steps: 8`
- **Model:** `z_image_turbo-Q8_0` (`z_image_turbo-Q8_0.gguf`)
- **Execution Target:** `HIP-ROCM0`
- **GPU Memory Used:** 8500.0 MB
- **CPU Memory Used:** 500.0 MB
- **Benchmark Running Time:** 12.50 s
- **Active Environment Settings:**
  - `LIMG_BACKEND="rocm0"`
  - `LIMG_CFG_SCALE="1.0"`
  - `LIMG_EXTRA_ARGS="--fa"`
  - `LIMG_HOST="127.0.0.1"`
  - `LIMG_LLM="/home/wuxxin/models/image/Qwen3-4B-Q4_K_M.gguf"`
  - `LIMG_MODEL="/data/public/machine-learning/models/image/z_image_turbo-Q8_0.gguf"`
  - `LIMG_PORT="50100"`
  - `LIMG_STEPS="8"`
  - `LIMG_THREADS="8"`
  - `LIMG_VAE="/data/public/machine-learning/models/image/ae.safetensors"`
- **Errors Count:** 0
- **Metrics:**
  - Avg Generation Time:  2.45 seconds

### VULKAN-VULKAN0 Configuration Details

- **Device Name**: `AMD Radeon Graphics` (Total: 4096 MiB, Free: 4096 MiB)

#### Text Chat (`local-chat`)
- **Benchmark Test Name:** `chat_vulkan-Vulkan0`
- **Device Setting:** `Vulkan0`
- **Special Setting:** `Layers: 999 (Context: 20%)`
- **Model:** `qwen3` (`Qwen3.6-35B-A3B-APEX-I-Compact`)
- **Execution Target:** `VULKAN-VULKAN0`
- **GPU Memory Used:** 14850.0 MB
- **CPU Memory Used:** 1250.0 MB
- **Benchmark Running Time:** 15.40 s
- **Active Environment Settings:**
  - `LCHAT_ALIAS="qwen3"`
  - `LCHAT_CHAT_TEMPLATE_ARGS="--chat-template-file /data/public/machine-learning/models/vision-text/Qwen3.6-chat_template.jinja"`
  - `LCHAT_DEVICE="Vulkan0"`
  - `LCHAT_EXTRA_ARGS="--flash-attn on --spec-type ngram-simple --spec-ngram-simple-size-n 6 --spec-ngram-simple-size-m 4"`
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
  - TTFT (Prefill):       64.47 ms
  - Prefill Speed:        294.70 tokens/sec
  - Generation Speed:     63.99 tokens/sec
- **Generation (Phase 2):**
  - Avg Completion Tokens: 600.0
  - Avg TTFT (Prefill):   31865.44 ms
  - Avg Prefill Speed:    974.13 tokens/sec
  - Avg Generation Speed: 38.23 tokens/sec
  - Avg Decode Time:      15.70 s
- **Vision Description (Phase 4):**
  - Avg TTFT (Prefill):   598.14 ms
  - Avg Generation Speed: 41.84 tokens/sec

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
  - `LMBD_ALIAS="qwen3-embedding"`
  - `LMBD_DEVICE="Vulkan0"`
  - `LMBD_EXTRA_ARGS="--flash-attn on"`
  - `LMBD_HOST="127.0.0.1"`
  - `LMBD_MODEL="/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf"`
  - `LMBD_N_CTX="8192"`
  - `LMBD_N_GPU_LAYERS="999"`
  - `LMBD_PORT="50082"`
  - `LMBD_THREADS="4"`
- **Errors Count:** 0
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
  - `LRR_ALIAS="qwen3-reranker"`
  - `LRR_DEVICE="Vulkan0"`
  - `LRR_EXTRA_ARGS="--flash-attn on"`
  - `LRR_HOST="127.0.0.1"`
  - `LRR_MODEL="/data/public/machine-learning/models/reranker/Qwen3-Reranker-0.6B.Q4_K_M.gguf"`
  - `LRR_N_CTX="8192"`
  - `LRR_N_GPU_LAYERS="99"`
  - `LRR_PORT="50086"`
  - `LRR_THREADS="8"`
- **Errors Count:** 0
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
  - `LTTS_EXTRA_ARGS=""`
  - `LTTS_HOST="127.0.0.1"`
  - `LTTS_MODE="gpu"`
  - `LTTS_MODEL="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf"`
  - `LTTS_PORT="50095"`
  - `LTTS_THREADS="8"`
  - `LTTS_VOCODER="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-Tokenizer-12Hz-F16.gguf"`
- **Errors Count:** 0
- **Metrics:**
  - Generated Audio Duration: 15.74 seconds
  - Avg Synthesis Time:   23.47 seconds
  - Avg Real-Time Factor (RTF): 1.4914
  - Avg Speed:            11.67 chars/sec

#### Image Generation (`local-image`)
- **Benchmark Test Name:** `image_vulkan-Vulkan0`
- **Device Setting:** `vulkan0,te=cpu`
- **Special Setting:** `Steps: 8`
- **Model:** `z_image_turbo-Q8_0` (`z_image_turbo-Q8_0.gguf`)
- **Execution Target:** `VULKAN-VULKAN0`
- **GPU Memory Used:** 8800.0 MB
- **CPU Memory Used:** 550.0 MB
- **Benchmark Running Time:** 12.50 s
- **Active Environment Settings:**
  - `LIMG_BACKEND="vulkan0,te=cpu"`
  - `LIMG_CFG_SCALE="1.0"`
  - `LIMG_EXTRA_ARGS="--fa"`
  - `LIMG_HOST="127.0.0.1"`
  - `LIMG_LLM="/home/wuxxin/models/image/Qwen3-4B-Q4_K_M.gguf"`
  - `LIMG_MODEL="/data/public/machine-learning/models/image/z_image_turbo-Q8_0.gguf"`
  - `LIMG_PORT="50100"`
  - `LIMG_STEPS="8"`
  - `LIMG_THREADS="8"`
  - `LIMG_VAE="/data/public/machine-learning/models/image/ae.safetensors"`
- **Errors Count:** 0
- **Metrics:**
  - Avg Generation Time:  2.82 seconds

### VULKAN-VULKAN1 Configuration Details

- **Device Name**: `AMD Radeon RX 7900 XTX` (Total: 24576 MiB, Free: 24576 MiB)

#### Text Chat (`local-chat`)
- **Benchmark Test Name:** `chat_vulkan-Vulkan1`
- **Device Setting:** `Vulkan1`
- **Special Setting:** `Layers: 999`
- **Model:** `qwen3` (`Qwen3.6-35B-A3B-APEX-I-Compact`)
- **Execution Target:** `VULKAN-VULKAN1`
- **GPU Memory Used:** 14850.0 MB
- **CPU Memory Used:** 1250.0 MB
- **Benchmark Running Time:** 15.40 s
- **Active Environment Settings:**
  - `LCHAT_ALIAS="qwen3"`
  - `LCHAT_CHAT_TEMPLATE_ARGS="--chat-template-file /data/public/machine-learning/models/vision-text/Qwen3.6-chat_template.jinja"`
  - `LCHAT_DEVICE="Vulkan1"`
  - `LCHAT_EXTRA_ARGS="--flash-attn on --spec-type ngram-simple --spec-ngram-simple-size-n 6 --spec-ngram-simple-size-m 4"`
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
  - TTFT (Prefill):       64.47 ms
  - Prefill Speed:        294.70 tokens/sec
  - Generation Speed:     63.99 tokens/sec
- **Generation (Phase 2):**
  - Avg Completion Tokens: 600.0
  - Avg TTFT (Prefill):   31865.44 ms
  - Avg Prefill Speed:    974.13 tokens/sec
  - Avg Generation Speed: 38.23 tokens/sec
  - Avg Decode Time:      15.70 s
- **Vision Description (Phase 4):**
  - Avg TTFT (Prefill):   598.14 ms
  - Avg Generation Speed: 41.84 tokens/sec

#### Text Embedding (`local-embedding`)
- **Benchmark Test Name:** `embedding_vulkan-Vulkan1`
- **Device Setting:** `Vulkan1`
- **Special Setting:** `Layers: 999`
- **Model:** `qwen3-embedding` (`Qwen3-Embedding-0.6B-Q8_0.gguf`)
- **Execution Target:** `VULKAN-VULKAN1`
- **GPU Memory Used:** 2650.0 MB
- **CPU Memory Used:** 360.0 MB
- **Benchmark Running Time:** 10.20 s
- **Active Environment Settings:**
  - `LMBD_ALIAS="qwen3-embedding"`
  - `LMBD_DEVICE="Vulkan1"`
  - `LMBD_EXTRA_ARGS="--flash-attn on"`
  - `LMBD_HOST="127.0.0.1"`
  - `LMBD_MODEL="/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf"`
  - `LMBD_N_CTX="4096"`
  - `LMBD_N_GPU_LAYERS="999"`
  - `LMBD_PORT="50082"`
  - `LMBD_THREADS="4"`
- **Errors Count:** 0
- **Metrics:**
  - Avg Time/Run:         10.42 s
  - Avg Throughput:       4364.59 tokens/sec
  - Avg Chunk Latency:    1735.9 ms
  - Avg Chunk p50:        1883.7 ms
  - Avg Chunk p95:        2089.4 ms

#### Document Reranking (`local-rerank`)
- **Benchmark Test Name:** `rerank_vulkan-Vulkan1`
- **Device Setting:** `Vulkan1`
- **Special Setting:** `Layers: 99`
- **Model:** `qwen3-reranker` (`Qwen3-Reranker-0.6B.Q4_K_M.gguf`)
- **Execution Target:** `VULKAN-VULKAN1`
- **GPU Memory Used:** 720.0 MB
- **CPU Memory Used:** 260.0 MB
- **Benchmark Running Time:** 8.70 s
- **Active Environment Settings:**
  - `LRR_ALIAS="qwen3-reranker"`
  - `LRR_DEVICE="Vulkan1"`
  - `LRR_EXTRA_ARGS="--flash-attn on"`
  - `LRR_HOST="127.0.0.1"`
  - `LRR_MODEL="/data/public/machine-learning/models/reranker/Qwen3-Reranker-0.6B.Q4_K_M.gguf"`
  - `LRR_N_CTX="8192"`
  - `LRR_N_GPU_LAYERS="99"`
  - `LRR_PORT="50086"`
  - `LRR_THREADS="8"`
- **Errors Count:** 0
- **Metrics:**
  - Avg Reranking Time:   29625.83 ms
  - Avg Docs Throughput:  0.34 docs/sec
  - Avg Token Speed:      116.08 tokens/sec

#### Speech-to-Text (STT) (`local-speech-to-text`)
- **Benchmark Test Name:** `stt_vulkan-Vulkan1`
- **Device Setting:** `0`
- **Special Setting:** `Use GPU`
- **Model:** `whisper-1` (`ggml-large-v3-turbo-q5_0.bin`)
- **Execution Target:** `VULKAN-VULKAN1`
- **GPU Memory Used:** 1950.0 MB
- **CPU Memory Used:** 460.0 MB
- **Benchmark Running Time:** 5.30 s
- **Active Environment Settings:**
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
  - Avg Transcribe Time:  1.67 seconds
  - Avg Real-Time Factor (RTF): 0.0369 (27.1x faster than real-time)

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Benchmark Test Name:** `tts_vulkan-Vulkan1`
- **Device Setting:** `Vulkan1`
- **Special Setting:** `mode: gpu`
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `VULKAN-VULKAN1`
- **GPU Memory Used:** 0.0 MB
- **CPU Memory Used:** 0.0 MB
- **Benchmark Running Time:** 25.10 s
- **Active Environment Settings:**
  - `LTTS_DEVICE="Vulkan1"`
  - `LTTS_EXTRA_ARGS=""`
  - `LTTS_HOST="127.0.0.1"`
  - `LTTS_MODE="gpu"`
  - `LTTS_MODEL="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf"`
  - `LTTS_PORT="50095"`
  - `LTTS_THREADS="8"`
  - `LTTS_VOCODER="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-Tokenizer-12Hz-F16.gguf"`
- **Errors Count:** 0
- **Metrics:**
  - Generated Audio Duration: 15.74 seconds
  - Avg Synthesis Time:   23.47 seconds
  - Avg Real-Time Factor (RTF): 1.4914
  - Avg Speed:            11.67 chars/sec

#### Image Generation (`local-image`)
- **Benchmark Test Name:** `image_vulkan-Vulkan1`
- **Device Setting:** `vulkan1`
- **Special Setting:** `Steps: 8`
- **Model:** `z_image_turbo-Q8_0` (`z_image_turbo-Q8_0.gguf`)
- **Execution Target:** `VULKAN-VULKAN1`
- **GPU Memory Used:** 8800.0 MB
- **CPU Memory Used:** 550.0 MB
- **Benchmark Running Time:** 12.50 s
- **Active Environment Settings:**
  - `LIMG_BACKEND="vulkan1"`
  - `LIMG_CFG_SCALE="1.0"`
  - `LIMG_EXTRA_ARGS="--fa"`
  - `LIMG_HOST="127.0.0.1"`
  - `LIMG_LLM="/home/wuxxin/models/image/Qwen3-4B-Q4_K_M.gguf"`
  - `LIMG_MODEL="/data/public/machine-learning/models/image/z_image_turbo-Q8_0.gguf"`
  - `LIMG_PORT="50100"`
  - `LIMG_STEPS="8"`
  - `LIMG_THREADS="8"`
  - `LIMG_VAE="/data/public/machine-learning/models/image/ae.safetensors"`
- **Errors Count:** 0
- **Metrics:**
  - Avg Generation Time:  2.82 seconds

### CPU Configuration Details

- **Device Name**: `AMD Radeon Graphics` (Total: 56261 MiB, Free: 92380 MiB)

#### Text Chat (`local-chat`)
- **Benchmark Test Name:** `chat_cpu`
- **Device Setting:** `Default`
- **Special Setting:** `Layers: 0 (Context: 5%)`
- **Model:** `qwen3` (`Qwen3.6-35B-A3B-APEX-I-Compact`)
- **Execution Target:** `CPU`
- **GPU Memory Used:** 0.0 MB
- **CPU Memory Used:** 0.0 MB
- **Benchmark Running Time:** 15.40 s
- **Active Environment Settings:**
  - `LCHAT_ALIAS="qwen3"`
  - `LCHAT_CHAT_TEMPLATE_ARGS="--chat-template-file /data/public/machine-learning/models/vision-text/Qwen3.6-chat_template.jinja"`
  - `LCHAT_DEVICE=""`
  - `LCHAT_EXTRA_ARGS="--flash-attn on --spec-type ngram-simple --spec-ngram-simple-size-n 6 --spec-ngram-simple-size-m 4"`
  - `LCHAT_HOST="127.0.0.1"`
  - `LCHAT_MMPROJ_ARGS="--mmproj /data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact-mmproj.gguf"`
  - `LCHAT_MODEL="/data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact.gguf"`
  - `LCHAT_N_CTX="12019"`
  - `LCHAT_N_GPU_LAYERS="0"`
  - `LCHAT_PARALLEL="3"`
  - `LCHAT_PORT="50080"`
  - `LCHAT_SERVE_EMBEDDINGS="false"`
  - `LCHAT_THREADS="4"`
- **Errors Count:** 2
- **Top Errors:**
  - `error: simulated configuration mismatch`
  - `error: mock error line 2`
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
- **Vision Description (Phase 4):**
  - Avg TTFT (Prefill):   2340.54 ms
  - Avg Generation Speed: 10.69 tokens/sec

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
  - `LMBD_ALIAS="qwen3-embedding"`
  - `LMBD_DEVICE=""`
  - `LMBD_EXTRA_ARGS="--flash-attn on"`
  - `LMBD_HOST="127.0.0.1"`
  - `LMBD_MODEL="/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf"`
  - `LMBD_N_CTX="8192"`
  - `LMBD_N_GPU_LAYERS="0"`
  - `LMBD_PORT="50082"`
  - `LMBD_THREADS="4"`
- **Errors Count:** 0
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
  - `LRR_ALIAS="qwen3-reranker"`
  - `LRR_DEVICE=""`
  - `LRR_EXTRA_ARGS="--flash-attn on"`
  - `LRR_HOST="127.0.0.1"`
  - `LRR_MODEL="/data/public/machine-learning/models/reranker/Qwen3-Reranker-0.6B.Q4_K_M.gguf"`
  - `LRR_N_CTX="8192"`
  - `LRR_N_GPU_LAYERS="0"`
  - `LRR_PORT="50086"`
  - `LRR_THREADS="8"`
- **Errors Count:** 0
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
  - Avg Transcribe Time:  6.52 seconds
  - Avg Real-Time Factor (RTF): 0.1444 (6.9x faster than real-time)

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Benchmark Test Name:** `tts_cpu`
- **Device Setting:** `cpu`
- **Special Setting:** `mode: cpu`
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `CPU`
- **GPU Memory Used:** 0.0 MB
- **CPU Memory Used:** 800.0 MB
- **Benchmark Running Time:** 25.10 s
- **Active Environment Settings:**
  - `LTTS_DEVICE="cpu"`
  - `LTTS_EXTRA_ARGS=""`
  - `LTTS_HOST="127.0.0.1"`
  - `LTTS_MODE="cpu"`
  - `LTTS_MODEL="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf"`
  - `LTTS_PORT="50095"`
  - `LTTS_THREADS="8"`
  - `LTTS_VOCODER="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-Tokenizer-12Hz-F16.gguf"`
- **Errors Count:** 0
- **Metrics:**
  - Generated Audio Duration: 15.74 seconds
  - Avg Synthesis Time:   105.61 seconds
  - Avg Real-Time Factor (RTF): 6.7113
  - Avg Speed:            2.59 chars/sec

#### Image Generation (`local-image`)
- **Benchmark Test Name:** `image_cpu`
- **Device Setting:** `cpu`
- **Special Setting:** `Steps: 8`
- **Model:** `z_image_turbo-Q8_0` (`z_image_turbo-Q8_0.gguf`)
- **Execution Target:** `CPU`
- **GPU Memory Used:** 0.0 MB
- **CPU Memory Used:** 9500.0 MB
- **Benchmark Running Time:** 12.50 s
- **Active Environment Settings:**
  - `LIMG_BACKEND="cpu"`
  - `LIMG_CFG_SCALE="1.0"`
  - `LIMG_EXTRA_ARGS="--fa"`
  - `LIMG_HOST="127.0.0.1"`
  - `LIMG_LLM="/home/wuxxin/models/image/Qwen3-4B-Q4_K_M.gguf"`
  - `LIMG_MODEL="/data/public/machine-learning/models/image/z_image_turbo-Q8_0.gguf"`
  - `LIMG_PORT="50100"`
  - `LIMG_STEPS="8"`
  - `LIMG_THREADS="8"`
  - `LIMG_VAE="/data/public/machine-learning/models/image/ae.safetensors"`
- **Errors Count:** 0
- **Metrics:**
  - Avg Generation Time:  11.03 seconds

### SPECIAL (CPU-HIP-ROCM0) Configuration Details

- **Device Name**: `AMD Radeon RX 7900 XTX` (Total: 24576 MiB, Free: 24576 MiB)

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Benchmark Test Name:** `tts_cpu-hip-ROCm0`
- **Device Setting:** `ROCm0`
- **Special Setting:** `mode: hybrid`
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `SPECIAL (CPU-HIP-ROCM0)`
- **GPU Memory Used:** 850.0 MB
- **CPU Memory Used:** 1500.0 MB
- **Benchmark Running Time:** 25.10 s
- **Active Environment Settings:**
  - `LTTS_DEVICE="ROCm0"`
  - `LTTS_EXTRA_ARGS=""`
  - `LTTS_HOST="127.0.0.1"`
  - `LTTS_MODE="hybrid"`
  - `LTTS_MODEL="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf"`
  - `LTTS_PORT="50095"`
  - `LTTS_THREADS="8"`
  - `LTTS_VOCODER="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-Tokenizer-12Hz-F16.gguf"`
- **Errors Count:** 0
- **Metrics:**
  - Generated Audio Duration: 15.74 seconds
  - Avg Synthesis Time:   23.47 seconds
  - Avg Real-Time Factor (RTF): 1.4914
  - Avg Speed:            11.67 chars/sec

### SPECIAL (CPU-HIP-ROCM1) Configuration Details

- **Device Name**: `AMD Radeon Graphics` (Total: 4096 MiB, Free: 4096 MiB)

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Benchmark Test Name:** `tts_cpu-hip-ROCm1`
- **Device Setting:** `ROCm1`
- **Special Setting:** `mode: hybrid`
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `SPECIAL (CPU-HIP-ROCM1)`
- **GPU Memory Used:** 850.0 MB
- **CPU Memory Used:** 1500.0 MB
- **Benchmark Running Time:** 25.10 s
- **Active Environment Settings:**
  - `LTTS_DEVICE="ROCm1"`
  - `LTTS_EXTRA_ARGS=""`
  - `LTTS_HOST="127.0.0.1"`
  - `LTTS_MODE="hybrid"`
  - `LTTS_MODEL="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf"`
  - `LTTS_PORT="50095"`
  - `LTTS_THREADS="8"`
  - `LTTS_VOCODER="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-Tokenizer-12Hz-F16.gguf"`
- **Errors Count:** 0
- **Metrics:**
  - Generated Audio Duration: 15.74 seconds
  - Avg Synthesis Time:   23.47 seconds
  - Avg Real-Time Factor (RTF): 1.4914
  - Avg Speed:            11.67 chars/sec

### SPECIAL (CPU-VULKAN-VULKAN0) Configuration Details

- **Device Name**: `AMD Radeon Graphics` (Total: 4096 MiB, Free: 4096 MiB)

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Benchmark Test Name:** `tts_cpu-vulkan-Vulkan0`
- **Device Setting:** `Vulkan0`
- **Special Setting:** `mode: hybrid`
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `SPECIAL (CPU-VULKAN-VULKAN0)`
- **GPU Memory Used:** 850.0 MB
- **CPU Memory Used:** 1500.0 MB
- **Benchmark Running Time:** 25.10 s
- **Active Environment Settings:**
  - `LTTS_DEVICE="Vulkan0"`
  - `LTTS_EXTRA_ARGS=""`
  - `LTTS_HOST="127.0.0.1"`
  - `LTTS_MODE="hybrid"`
  - `LTTS_MODEL="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf"`
  - `LTTS_PORT="50095"`
  - `LTTS_THREADS="8"`
  - `LTTS_VOCODER="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-Tokenizer-12Hz-F16.gguf"`
- **Errors Count:** 0
- **Metrics:**
  - Generated Audio Duration: 15.74 seconds
  - Avg Synthesis Time:   23.47 seconds
  - Avg Real-Time Factor (RTF): 1.4914
  - Avg Speed:            11.67 chars/sec

### SPECIAL (CPU-VULKAN-VULKAN1) Configuration Details

- **Device Name**: `AMD Radeon RX 7900 XTX` (Total: 24576 MiB, Free: 24576 MiB)

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Benchmark Test Name:** `tts_cpu-vulkan-Vulkan1`
- **Device Setting:** `Vulkan1`
- **Special Setting:** `mode: hybrid`
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `SPECIAL (CPU-VULKAN-VULKAN1)`
- **GPU Memory Used:** 850.0 MB
- **CPU Memory Used:** 1500.0 MB
- **Benchmark Running Time:** 25.10 s
- **Active Environment Settings:**
  - `LTTS_DEVICE="Vulkan1"`
  - `LTTS_EXTRA_ARGS=""`
  - `LTTS_HOST="127.0.0.1"`
  - `LTTS_MODE="hybrid"`
  - `LTTS_MODEL="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf"`
  - `LTTS_PORT="50095"`
  - `LTTS_THREADS="8"`
  - `LTTS_VOCODER="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-Tokenizer-12Hz-F16.gguf"`
- **Errors Count:** 0
- **Metrics:**
  - Generated Audio Duration: 15.74 seconds
  - Avg Synthesis Time:   23.47 seconds
  - Avg Real-Time Factor (RTF): 1.4914
  - Avg Speed:            11.67 chars/sec

