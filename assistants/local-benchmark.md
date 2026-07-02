# LLM Caching Optimization Benchmarks

**Benchmark Run Time:** `2026-07-02 15:12:48`

## Local Inference Services Benchmarks

We ran local benchmarks for text embedding, text-to-speech (TTS), speech-to-text (STT), document reranking, and image generation on the AMD Radeon RX 7900 XTX hardware target. All services run inside isolated sandboxed environments.

### 📊 Performance Comparison Matrix

#### Text Chat (`local-chat`)
| Configuration | Test Name | GPU | Special Setting | Avg Chat TTFT | Avg Chat Prefill | Chat TTFT (Warmup) | Chat Gen Speed | Avg Chat Gen | Chat Image TTFT | Chat Image Gen | Chat GPU Mem | Chat CPU Mem |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| [**HIP-ROCM0**](#hip-rocm0-configuration-details) | chat_hip-ROCm0 | ROCm0 | Layers: 999 | 48511.01 ms | 639.88 t/s | 263.75 ms | 102.49 t/s | 65.32 t/s | 0.00 ms | 0.00 t/s | 20483.6 MB | 1438.6 MB |
| [**VULKAN-VULKAN0**](#vulkan-vulkan0-configuration-details) | chat_vulkan-Vulkan0 | Vulkan0 | Layers: 999 (Context: 20%) | 56147.14 ms | 103.58 t/s | 1649.72 ms | 13.84 t/s | 12.88 t/s | 0.00 ms | 0.00 t/s | 14039.5 MB | 845.3 MB |
| [**VULKAN-VULKAN1**](#vulkan-vulkan1-configuration-details) | chat_vulkan-Vulkan1 | Vulkan1 | Layers: 999 | 14476.21 ms | **2144.28 t/s** | 157.72 ms | 130.91 t/s | **116.66 t/s** | 0.00 ms | 0.00 t/s | 19141.9 MB | 851.0 MB |
| [**CPU**](#cpu-configuration-details) | chat_cpu | none | Layers: 0 (Context: 5%) | 35398.50 ms | 41.61 t/s | 997.77 ms | 12.20 t/s | 11.64 t/s | 0.00 ms | 0.00 t/s | 1109.2 MB | 20981.7 MB |
| [**CPU-BLAS**](#cpu-blas-configuration-details) | chat_cpu-blas | BLAS | Layers: 0 (Context: 5%) | 35513.20 ms | 41.48 t/s | 950.71 ms | 12.51 t/s | 11.75 t/s | 0.00 ms | 0.00 t/s | 1109.2 MB | 20982.3 MB |
| [**RUNNING**](#running-configuration-details) | chat_running | running on host | unknown | 17600.42 ms | 1763.65 t/s | 89.36 ms | 131.57 t/s | 116.36 t/s | 0.00 ms | 0.00 t/s | -n.a.- | -n.a.- |

#### Text Embedding (`local-embedding`)
| Configuration | Test Name | GPU | Special Setting | Embedding Throughput | Embedding Latency (Avg) | Embedding GPU Mem | Embedding CPU Mem |
|---|---|---|---|---|---|---|---|
| [**HIP-ROCM0**](#hip-rocm0-configuration-details) | embedding_hip-ROCm0 | ROCm0 | Layers: 999 | **5368.69 t/s** | 95.1 ms | 1977.6 MB | 3594.3 MB |
| [**VULKAN-VULKAN0**](#vulkan-vulkan0-configuration-details) | embedding_vulkan-Vulkan0 | Vulkan0 | Layers: 999 | 648.52 t/s | 787.6 ms | 1381.2 MB | 2911.6 MB |
| [**VULKAN-VULKAN1**](#vulkan-vulkan1-configuration-details) | embedding_vulkan-Vulkan1 | Vulkan1 | Layers: 999 | 5245.63 t/s | 97.4 ms | 1162.5 MB | 2914.6 MB |
| [**CPU**](#cpu-configuration-details) | embedding_cpu | none | Layers: 0 | 143.90 t/s | 3558.1 ms | 0.1 MB | 2645.5 MB |
| [**CPU-BLAS**](#cpu-blas-configuration-details) | embedding_cpu-blas | BLAS | Layers: 999 | 104.30 t/s | 4908.9 ms | 0.0 MB | 2645.9 MB |
| [**RUNNING**](#running-configuration-details) | embedding_running | running on host | unknown | 4816.26 t/s | 106.1 ms | -n.a.- | -n.a.- |

#### Document Reranking (`local-rerank`)
| Configuration | Test Name | GPU | Special Setting | Avg Reranking Time | Avg Token Speed | Avg Docs Throughput | GPU Mem | CPU Mem |
|---|---|---|---|---|---|---|---|---|
| [**HIP-ROCM0**](#hip-rocm0-configuration-details) | rerank_hip-ROCm0 | ROCm0 | Layers: 99 | 866.43 ms | **3969.14 tokens/s** | 11.54 docs/s | 2533.1 MB | 822.2 MB |
| [**VULKAN-VULKAN0**](#vulkan-vulkan0-configuration-details) | rerank_vulkan-Vulkan0 | Vulkan0 | Layers: 99 | 5075.97 ms | 677.51 tokens/s | 1.97 docs/s | 1571.7 MB | 246.9 MB |
| [**VULKAN-VULKAN1**](#vulkan-vulkan1-configuration-details) | rerank_vulkan-Vulkan1 | Vulkan1 | Layers: 99 | 867.68 ms | 3963.44 tokens/s | 11.52 docs/s | 1590.2 MB | 253.0 MB |
| [**CPU**](#cpu-configuration-details) | rerank_cpu | none | Layers: 0 | 12563.41 ms | 273.73 tokens/s | 0.80 docs/s | 0.1 MB | 2711.2 MB |
| [**CPU-BLAS**](#cpu-blas-configuration-details) | rerank_cpu-blas | BLAS | Layers: 99 | 12395.55 ms | 277.44 tokens/s | 0.81 docs/s | 0.1 MB | 2712.3 MB |
| [**RUNNING**](#running-configuration-details) | rerank_running | running on host | unknown | 10132.72 ms | 339.40 tokens/s | 0.99 docs/s | -n.a.- | -n.a.- |

#### Speech-to-Text (STT) (`local-speech-to-text`)
| Configuration | Test Name | GPU | Special Setting | Avg Transcribe Time | Avg Real-Time Factor (RTF) | Speedup vs Real-time | GPU Mem | CPU Mem |
|---|---|---|---|---|---|---|---|---|
| [**HIP-ROCM0**](#hip-rocm0-configuration-details) | stt_hip-ROCm0 | 0 | Use GPU | 5.56 s | 0.1235 | 8.1x | 0.1 MB | 125.8 MB |
| [**VULKAN-VULKAN0**](#vulkan-vulkan0-configuration-details) | stt_vulkan-Vulkan0 | 0 | Use GPU | 5.52 s | 0.1226 | 8.2x | 808.8 MB | 126.4 MB |
| [**VULKAN-VULKAN1**](#vulkan-vulkan1-configuration-details) | stt_vulkan-Vulkan1 | 1 | Use GPU | 0.55 s | 0.0123 | **81.4x** | 828.0 MB | 126.8 MB |
| [**CPU**](#cpu-configuration-details) | stt_cpu | none | No GPU | 16.87 s | 0.3748 | 2.7x | 0.1 MB | 1102.1 MB |
| [**CPU-BLAS**](#cpu-blas-configuration-details) | stt_cpu-blas | BLAS | No GPU | 14.02 s | 0.3115 | 3.2x | 0.1 MB | 1101.7 MB |
| [**RUNNING**](#running-configuration-details) | stt_running | running on host | unknown | 5.58 s | 0.1240 | 8.1x | -n.a.- | -n.a.- |

#### Text-to-Speech (TTS) (`local-text-to-speech`)
| Configuration | Test Name | GPU | Special Setting | Avg Synthesis Time | Avg Real-Time Factor (RTF) | Speed (chars/s) | GPU Mem | CPU Mem |
|---|---|---|---|---|---|---|---|---|
| [**HIP-ROCM0**](#hip-rocm0-configuration-details) | tts_hip-ROCm0 | ROCm0 | mode: gpu | -fail- | -fail- | -fail- | -fail- | -fail- |
| [**VULKAN-VULKAN0**](#vulkan-vulkan0-configuration-details) | tts_vulkan-Vulkan0 | Vulkan0 | mode: gpu | -fail- VALIDATION | 2.4410 | 5.73 chars/s | 3323.8 MB | 684.6 MB |
| [**VULKAN-VULKAN1**](#vulkan-vulkan1-configuration-details) | tts_vulkan-Vulkan1 | Vulkan1 | mode: gpu | 6.51 s | 0.3270 | **42.12 chars/s** | 3393.3 MB | 693.1 MB |
| [**CPU**](#cpu-configuration-details) | tts_cpu | none | mode: cpu | 29.31 s | 1.5413 | 9.35 chars/s | 0.1 MB | 2956.2 MB |
| [**CPU-BLAS**](#cpu-blas-configuration-details) | tts_cpu-blas | BLAS | mode: cpu | 28.31 s | 1.5403 | 9.68 chars/s | 0.1 MB | 2969.4 MB |
| [**CPU-HIP-ROCM0**](#special-cpu-hip-rocm0-configuration-details) | tts_cpu-hip-ROCm0 | ROCm0 | mode: hybrid | -fail- | -fail- | -fail- | -fail- | -fail- |
| [**CPU-HIP-ROCM1**](#special-cpu-hip-rocm1-configuration-details) | tts_cpu-hip-ROCm1 | ROCm1 | mode: hybrid | -fail- | -fail- | -fail- | -fail- | -fail- |
| [**CPU-VULKAN-VULKAN0**](#special-cpu-vulkan-vulkan0-configuration-details) | tts_cpu-vulkan-Vulkan0 | Vulkan0 | mode: hybrid | 50.29 s | 2.4393 | 5.45 chars/s | 3345.3 MB | 710.0 MB |
| [**CPU-VULKAN-VULKAN1**](#special-cpu-vulkan-vulkan1-configuration-details) | tts_cpu-vulkan-Vulkan1 | Vulkan1 | mode: hybrid | 6.76 s | 0.3265 | 40.55 chars/s | 3389.8 MB | 714.3 MB |
| [**RUNNING**](#running-configuration-details) | tts_running | running on host | unknown | 28.27 s | 1.5319 | 9.69 chars/s | -n.a.- | -n.a.- |

#### Image Generation (`local-image`)
| Configuration | Test Name | GPU | Special Setting | Avg Generation Time | GPU Mem | CPU Mem |
|---|---|---|---|---|---|---|
| [**HIP-ROCM0**](#hip-rocm0-configuration-details) | image_hip-ROCm0 | rocm0 | Steps: 8 | **6.18 s** | 10758.6 MB | 923.4 MB |
| [**VULKAN-VULKAN0**](#vulkan-vulkan0-configuration-details) | image_vulkan-Vulkan0 | vulkan0,te=cpu | Steps: 8 | 93.04 s | 6368.2 MB | 3811.6 MB |
| [**VULKAN-VULKAN1**](#vulkan-vulkan1-configuration-details) | image_vulkan-Vulkan1 | vulkan1 | Steps: 8 | 6.83 s | 9879.0 MB | 434.7 MB |
| [**CPU**](#cpu-configuration-details) | image_cpu | cpu | Steps: 8 | 288.11 s | 0.1 MB | 10137.6 MB |
| [**CPU-BLAS**](#cpu-blas-configuration-details) | image_cpu-blas | cpu | Steps: 8 | 287.52 s | 0.1 MB | 10137.6 MB |
| [**RUNNING**](#running-configuration-details) | image_running | running on host | unknown | 89.30 s | -n.a.- | -n.a.- |

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
- **GPU Memory Used:** 20483.6 MB
- **CPU Memory Used:** 1438.6 MB
- **Benchmark Running Time:** 59.68 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES="0"`
  - `GGML_VK_DISABLE_MMVQ="1"`
  - `HIP_VISIBLE_DEVICES="0"`
  - `LCHAT_ALIAS="qwen3"`
  - `LCHAT_CHAT_TEMPLATE_ARGS="--chat-template-file /data/public/machine-learning/models/vision-text/Qwen3.6-chat_template.jinja"`
  - `LCHAT_DEVICE="ROCm0"`
  - `LCHAT_EXTRA_ARGS=""`
  - `LCHAT_HOST="127.0.0.1"`
  - `LCHAT_MMPROJ_ARGS="--mmproj /data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact-mmproj.gguf"`
  - `LCHAT_MODEL="/data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact.gguf"`
  - `LCHAT_N_CTX="240384"`
  - `LCHAT_N_GPU_LAYERS="999"`
  - `LCHAT_PARALLEL="3"`
  - `LCHAT_PORT="50080"`
  - `LCHAT_SERVE_EMBEDDINGS="false"`
  - `LCHAT_SPECULATIVE_ARGS="--spec-type ngram-simple --spec-ngram-simple-size-n 6 --spec-ngram-simple-size-m 4"`
  - `LCHAT_THREADS="4"`
- **Errors Count:** 0
- **Package Version:** `9842 (6f4f53f2b7)`
- **Warmup (Phase 0):**
  - TTFT (Prefill):       263.75 ms
  - Prefill Speed:        72.04 tokens/sec
  - Generation Speed:     102.49 tokens/sec
- **Generation (Phase 2):**
  - Avg Completion Tokens: 600.0
  - Avg TTFT (Prefill):   48511.01 ms
  - Avg Prefill Speed:    639.88 tokens/sec
  - Avg Generation Speed: 65.32 tokens/sec
  - Avg Decode Time:      9.19 s
- **Vision Description (Phase 4):**
  - Avg TTFT (Prefill):   0.00 ms
  - Avg Generation Speed: 0.00 tokens/sec

#### Text Embedding (`local-embedding`)
- **Benchmark Test Name:** `embedding_hip-ROCm0`
- **Device Setting:** `ROCm0`
- **Special Setting:** `Layers: 999`
- **Model:** `qwen3-embedding` (`Qwen3-Embedding-0.6B-Q8_0.gguf`)
- **Execution Target:** `HIP-ROCM0`
- **GPU Memory Used:** 1977.6 MB
- **CPU Memory Used:** 3594.3 MB
- **Benchmark Running Time:** 8.92 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES="0"`
  - `HIP_VISIBLE_DEVICES="0"`
  - `LMBD_ALIAS="qwen3-embedding"`
  - `LMBD_DEVICE="ROCm0"`
  - `LMBD_EXTRA_ARGS="--flash-attn on"`
  - `LMBD_HOST="127.0.0.1"`
  - `LMBD_MODEL="/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf"`
  - `LMBD_N_CTX="8192"`
  - `LMBD_N_GPU_LAYERS="999"`
  - `LMBD_N_UBATCH="512"`
  - `LMBD_PARALLEL="2"`
  - `LMBD_PORT="50082"`
  - `LMBD_THREADS="4"`
- **Errors Count:** 0
- **Package Version:** `9842 (6f4f53f2b7)`
- **Metrics:**
  - Avg Time/Run:         8.47 s
  - Avg Throughput:       5368.69 tokens/sec
  - Avg Chunk Latency:    95.1 ms
  - Avg Chunk p50:        88.3 ms
  - Avg Chunk p95:        90.3 ms

#### Document Reranking (`local-rerank`)
- **Benchmark Test Name:** `rerank_hip-ROCm0`
- **Device Setting:** `ROCm0`
- **Special Setting:** `Layers: 99`
- **Model:** `qwen3-reranker` (`Qwen3-Reranker-0.6B.Q4_K_M.gguf`)
- **Execution Target:** `HIP-ROCM0`
- **GPU Memory Used:** 2533.1 MB
- **CPU Memory Used:** 822.2 MB
- **Benchmark Running Time:** 1.00 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES="0"`
  - `HIP_VISIBLE_DEVICES="0"`
  - `LRR_ALIAS="qwen3-reranker"`
  - `LRR_DEVICE="ROCm0"`
  - `LRR_EXTRA_ARGS="--flash-attn on"`
  - `LRR_HOST="127.0.0.1"`
  - `LRR_MODEL="/data/public/machine-learning/models/reranker/Qwen3-Reranker-0.6B.Q4_K_M.gguf"`
  - `LRR_N_CTX="8192"`
  - `LRR_N_GPU_LAYERS="99"`
  - `LRR_PARALLEL="2"`
  - `LRR_PORT="50086"`
  - `LRR_THREADS="8"`
- **Errors Count:** 0
- **Package Version:** `9842 (6f4f53f2b7)`
- **Metrics:**
  - Avg Reranking Time:   866.43 ms
  - Avg Docs Throughput:  11.54 docs/sec
  - Avg Token Speed:      3969.14 tokens/sec

#### Speech-to-Text (STT) (`local-speech-to-text`)
- **Benchmark Test Name:** `stt_hip-ROCm0`
- **Device Setting:** `0`
- **Special Setting:** `Use GPU`
- **Model:** `whisper-1` (`ggml-large-v3-turbo-q5_0.bin`)
- **Execution Target:** `HIP-ROCM0`
- **GPU Memory Used:** 0.1 MB
- **CPU Memory Used:** 125.8 MB
- **Benchmark Running Time:** 5.81 s
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
- **Package Version:** `1.9.1`
- **Metrics:**
  - Avg Transcribe Time:  5.56 seconds
  - Avg Real-Time Factor (RTF): 0.1235 (8.1x faster than real-time)

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Benchmark Test Name:** `tts_hip-ROCm0`
- **Device Setting:** `ROCm0`
- **Special Setting:** `mode: gpu`
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `HIP-ROCM0`
- **GPU Memory Used:** -fail-
- **CPU Memory Used:** -fail-
- **Benchmark Running Time:** -fail-
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
  - `Error: qwen3-tts-server failed to start or port timed out`
- **Package Version:** `unknown`
- **Metrics:**
  - Generated Audio Duration: -fail-
  - Avg Synthesis Time:   -fail-
  - Avg Real-Time Factor (RTF): -fail-
  - Avg Speed:            -fail-

#### Image Generation (`local-image`)
- **Benchmark Test Name:** `image_hip-ROCm0`
- **Device Setting:** `rocm0`
- **Special Setting:** `Steps: 8`
- **Model:** `z_image_turbo-Q8_0` (`z_image_turbo-Q8_0.gguf`)
- **Execution Target:** `HIP-ROCM0`
- **GPU Memory Used:** 10758.6 MB
- **CPU Memory Used:** 923.4 MB
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
- **Package Version:** `master-734-3ec374a-3-g3b6c9ca, commit 3b6c9ca9`
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
- **GPU Memory Used:** 14039.5 MB
- **CPU Memory Used:** 845.3 MB
- **Benchmark Running Time:** 117.70 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `GGML_VK_DISABLE_MMVQ="1"`
  - `HIP_VISIBLE_DEVICES=""`
  - `LCHAT_ALIAS="qwen3"`
  - `LCHAT_CHAT_TEMPLATE_ARGS="--chat-template-file /data/public/machine-learning/models/vision-text/Qwen3.6-chat_template.jinja"`
  - `LCHAT_DEVICE="Vulkan0"`
  - `LCHAT_EXTRA_ARGS=""`
  - `LCHAT_HOST="127.0.0.1"`
  - `LCHAT_MMPROJ_ARGS="--mmproj /data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact-mmproj.gguf"`
  - `LCHAT_MODEL="/data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact.gguf"`
  - `LCHAT_N_CTX="48076"`
  - `LCHAT_N_GPU_LAYERS="999"`
  - `LCHAT_PARALLEL="3"`
  - `LCHAT_PORT="50080"`
  - `LCHAT_SERVE_EMBEDDINGS="false"`
  - `LCHAT_SPECULATIVE_ARGS="--spec-type ngram-simple --spec-ngram-simple-size-n 6 --spec-ngram-simple-size-m 4"`
  - `LCHAT_THREADS="4"`
- **Errors Count:** 0
- **Package Version:** `9842 (6f4f53f2b7)`
- **Warmup (Phase 0):**
  - TTFT (Prefill):       1649.72 ms
  - Prefill Speed:        11.52 tokens/sec
  - Generation Speed:     13.84 tokens/sec
- **Generation (Phase 2):**
  - Avg Completion Tokens: 600.0
  - Avg TTFT (Prefill):   56147.14 ms
  - Avg Prefill Speed:    103.58 tokens/sec
  - Avg Generation Speed: 12.88 tokens/sec
  - Avg Decode Time:      46.58 s
- **Vision Description (Phase 4):**
  - Avg TTFT (Prefill):   0.00 ms
  - Avg Generation Speed: 0.00 tokens/sec

#### Text Embedding (`local-embedding`)
- **Benchmark Test Name:** `embedding_vulkan-Vulkan0`
- **Device Setting:** `Vulkan0`
- **Special Setting:** `Layers: 999`
- **Model:** `qwen3-embedding` (`Qwen3-Embedding-0.6B-Q8_0.gguf`)
- **Execution Target:** `VULKAN-VULKAN0`
- **GPU Memory Used:** 1381.2 MB
- **CPU Memory Used:** 2911.6 MB
- **Benchmark Running Time:** 70.32 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LMBD_ALIAS="qwen3-embedding"`
  - `LMBD_DEVICE="Vulkan0"`
  - `LMBD_EXTRA_ARGS="--flash-attn on"`
  - `LMBD_HOST="127.0.0.1"`
  - `LMBD_MODEL="/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf"`
  - `LMBD_N_CTX="8192"`
  - `LMBD_N_GPU_LAYERS="999"`
  - `LMBD_N_UBATCH="512"`
  - `LMBD_PARALLEL="2"`
  - `LMBD_PORT="50082"`
  - `LMBD_THREADS="4"`
- **Errors Count:** 0
- **Package Version:** `9842 (6f4f53f2b7)`
- **Metrics:**
  - Avg Time/Run:         70.10 s
  - Avg Throughput:       648.52 tokens/sec
  - Avg Chunk Latency:    787.6 ms
  - Avg Chunk p50:        790.9 ms
  - Avg Chunk p95:        796.2 ms

#### Document Reranking (`local-rerank`)
- **Benchmark Test Name:** `rerank_vulkan-Vulkan0`
- **Device Setting:** `Vulkan0`
- **Special Setting:** `Layers: 99`
- **Model:** `qwen3-reranker` (`Qwen3-Reranker-0.6B.Q4_K_M.gguf`)
- **Execution Target:** `VULKAN-VULKAN0`
- **GPU Memory Used:** 1571.7 MB
- **CPU Memory Used:** 246.9 MB
- **Benchmark Running Time:** 5.21 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LRR_ALIAS="qwen3-reranker"`
  - `LRR_DEVICE="Vulkan0"`
  - `LRR_EXTRA_ARGS="--flash-attn on"`
  - `LRR_HOST="127.0.0.1"`
  - `LRR_MODEL="/data/public/machine-learning/models/reranker/Qwen3-Reranker-0.6B.Q4_K_M.gguf"`
  - `LRR_N_CTX="8192"`
  - `LRR_N_GPU_LAYERS="99"`
  - `LRR_PARALLEL="2"`
  - `LRR_PORT="50086"`
  - `LRR_THREADS="8"`
- **Errors Count:** 0
- **Package Version:** `9842 (6f4f53f2b7)`
- **Metrics:**
  - Avg Reranking Time:   5075.97 ms
  - Avg Docs Throughput:  1.97 docs/sec
  - Avg Token Speed:      677.51 tokens/sec

#### Speech-to-Text (STT) (`local-speech-to-text`)
- **Benchmark Test Name:** `stt_vulkan-Vulkan0`
- **Device Setting:** `0`
- **Special Setting:** `Use GPU`
- **Model:** `whisper-1` (`ggml-large-v3-turbo-q5_0.bin`)
- **Execution Target:** `VULKAN-VULKAN0`
- **GPU Memory Used:** 808.8 MB
- **CPU Memory Used:** 126.4 MB
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
- **Package Version:** `1.9.1`
- **Metrics:**
  - Avg Transcribe Time:  5.52 seconds
  - Avg Real-Time Factor (RTF): 0.1226 (8.2x faster than real-time)

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Benchmark Test Name:** `tts_vulkan-Vulkan0`
- **Device Setting:** `Vulkan0`
- **Special Setting:** `mode: gpu`
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `VULKAN-VULKAN0`
- **GPU Memory Used:** 3323.8 MB
- **CPU Memory Used:** 684.6 MB
- **Benchmark Running Time:** 47.87 s
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
  - `Warning: TTS Audio validation failed (garbled audio output)`
- **Package Version:** `unknown`
- **Metrics:**
  - Generated Audio Duration: -fail- VALIDATION
  - Avg Synthesis Time:   -fail- VALIDATION
  - Avg Real-Time Factor (RTF): 2.4410
  - Avg Speed:            5.73 chars/sec

#### Image Generation (`local-image`)
- **Benchmark Test Name:** `image_vulkan-Vulkan0`
- **Device Setting:** `vulkan0,te=cpu`
- **Special Setting:** `Steps: 8`
- **Model:** `z_image_turbo-Q8_0` (`z_image_turbo-Q8_0.gguf`)
- **Execution Target:** `VULKAN-VULKAN0`
- **GPU Memory Used:** 6368.2 MB
- **CPU Memory Used:** 3811.6 MB
- **Benchmark Running Time:** 93.14 s
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
- **Package Version:** `master-734-3ec374a-3-g3b6c9ca, commit 3b6c9ca9`
- **Metrics:**
  - Avg Generation Time:  93.04 seconds

### VULKAN-VULKAN1 Configuration Details

- **Device Name**: `AMD Radeon RX 7900 XTX` (Total: 24560 MiB, Free: 24560 MiB)

#### Text Chat (`local-chat`)
- **Benchmark Test Name:** `chat_vulkan-Vulkan1`
- **Device Setting:** `Vulkan1`
- **Special Setting:** `Layers: 999`
- **Model:** `qwen3` (`Qwen3.6-35B-A3B-APEX-I-Compact`)
- **Execution Target:** `VULKAN-VULKAN1`
- **GPU Memory Used:** 19141.9 MB
- **CPU Memory Used:** 851.0 MB
- **Benchmark Running Time:** 21.23 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `GGML_VK_DISABLE_MMVQ="1"`
  - `HIP_VISIBLE_DEVICES=""`
  - `LCHAT_ALIAS="qwen3"`
  - `LCHAT_CHAT_TEMPLATE_ARGS="--chat-template-file /data/public/machine-learning/models/vision-text/Qwen3.6-chat_template.jinja"`
  - `LCHAT_DEVICE="Vulkan1"`
  - `LCHAT_EXTRA_ARGS=""`
  - `LCHAT_HOST="127.0.0.1"`
  - `LCHAT_MMPROJ_ARGS="--mmproj /data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact-mmproj.gguf"`
  - `LCHAT_MODEL="/data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact.gguf"`
  - `LCHAT_N_CTX="240384"`
  - `LCHAT_N_GPU_LAYERS="999"`
  - `LCHAT_PARALLEL="3"`
  - `LCHAT_PORT="50080"`
  - `LCHAT_SERVE_EMBEDDINGS="false"`
  - `LCHAT_SPECULATIVE_ARGS="--spec-type ngram-simple --spec-ngram-simple-size-n 6 --spec-ngram-simple-size-m 4"`
  - `LCHAT_THREADS="4"`
- **Errors Count:** 0
- **Package Version:** `9842 (6f4f53f2b7)`
- **Warmup (Phase 0):**
  - TTFT (Prefill):       157.72 ms
  - Prefill Speed:        120.47 tokens/sec
  - Generation Speed:     130.91 tokens/sec
- **Generation (Phase 2):**
  - Avg Completion Tokens: 600.0
  - Avg TTFT (Prefill):   14476.21 ms
  - Avg Prefill Speed:    2144.28 tokens/sec
  - Avg Generation Speed: 116.66 tokens/sec
  - Avg Decode Time:      5.14 s
- **Vision Description (Phase 4):**
  - Avg TTFT (Prefill):   0.00 ms
  - Avg Generation Speed: 0.00 tokens/sec

#### Text Embedding (`local-embedding`)
- **Benchmark Test Name:** `embedding_vulkan-Vulkan1`
- **Device Setting:** `Vulkan1`
- **Special Setting:** `Layers: 999`
- **Model:** `qwen3-embedding` (`Qwen3-Embedding-0.6B-Q8_0.gguf`)
- **Execution Target:** `VULKAN-VULKAN1`
- **GPU Memory Used:** 1162.5 MB
- **CPU Memory Used:** 2914.6 MB
- **Benchmark Running Time:** 8.93 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LMBD_ALIAS="qwen3-embedding"`
  - `LMBD_DEVICE="Vulkan1"`
  - `LMBD_EXTRA_ARGS="--flash-attn on"`
  - `LMBD_HOST="127.0.0.1"`
  - `LMBD_MODEL="/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf"`
  - `LMBD_N_CTX="4096"`
  - `LMBD_N_GPU_LAYERS="999"`
  - `LMBD_N_UBATCH="512"`
  - `LMBD_PARALLEL="2"`
  - `LMBD_PORT="50082"`
  - `LMBD_THREADS="4"`
- **Errors Count:** 0
- **Package Version:** `9842 (6f4f53f2b7)`
- **Metrics:**
  - Avg Time/Run:         8.67 s
  - Avg Throughput:       5245.63 tokens/sec
  - Avg Chunk Latency:    97.4 ms
  - Avg Chunk p50:        96.3 ms
  - Avg Chunk p95:        97.9 ms

#### Document Reranking (`local-rerank`)
- **Benchmark Test Name:** `rerank_vulkan-Vulkan1`
- **Device Setting:** `Vulkan1`
- **Special Setting:** `Layers: 99`
- **Model:** `qwen3-reranker` (`Qwen3-Reranker-0.6B.Q4_K_M.gguf`)
- **Execution Target:** `VULKAN-VULKAN1`
- **GPU Memory Used:** 1590.2 MB
- **CPU Memory Used:** 253.0 MB
- **Benchmark Running Time:** 1.00 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LRR_ALIAS="qwen3-reranker"`
  - `LRR_DEVICE="Vulkan1"`
  - `LRR_EXTRA_ARGS="--flash-attn on"`
  - `LRR_HOST="127.0.0.1"`
  - `LRR_MODEL="/data/public/machine-learning/models/reranker/Qwen3-Reranker-0.6B.Q4_K_M.gguf"`
  - `LRR_N_CTX="8192"`
  - `LRR_N_GPU_LAYERS="99"`
  - `LRR_PARALLEL="2"`
  - `LRR_PORT="50086"`
  - `LRR_THREADS="8"`
- **Errors Count:** 0
- **Package Version:** `9842 (6f4f53f2b7)`
- **Metrics:**
  - Avg Reranking Time:   867.68 ms
  - Avg Docs Throughput:  11.52 docs/sec
  - Avg Token Speed:      3963.44 tokens/sec

#### Speech-to-Text (STT) (`local-speech-to-text`)
- **Benchmark Test Name:** `stt_vulkan-Vulkan1`
- **Device Setting:** `1`
- **Special Setting:** `Use GPU`
- **Model:** `whisper-1` (`ggml-large-v3-turbo-q5_0.bin`)
- **Execution Target:** `VULKAN-VULKAN1`
- **GPU Memory Used:** 828.0 MB
- **CPU Memory Used:** 126.8 MB
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
- **Package Version:** `1.9.1`
- **Metrics:**
  - Avg Transcribe Time:  0.55 seconds
  - Avg Real-Time Factor (RTF): 0.0123 (81.4x faster than real-time)

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Benchmark Test Name:** `tts_vulkan-Vulkan1`
- **Device Setting:** `Vulkan1`
- **Special Setting:** `mode: gpu`
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `VULKAN-VULKAN1`
- **GPU Memory Used:** 3393.3 MB
- **CPU Memory Used:** 693.1 MB
- **Benchmark Running Time:** 6.61 s
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
- **Errors Count:** 0
- **Package Version:** `unknown`
- **Metrics:**
  - Generated Audio Duration: 19.90 seconds
  - Avg Synthesis Time:   6.51 seconds
  - Avg Real-Time Factor (RTF): 0.3270
  - Avg Speed:            42.12 chars/sec

#### Image Generation (`local-image`)
- **Benchmark Test Name:** `image_vulkan-Vulkan1`
- **Device Setting:** `vulkan1`
- **Special Setting:** `Steps: 8`
- **Model:** `z_image_turbo-Q8_0` (`z_image_turbo-Q8_0.gguf`)
- **Execution Target:** `VULKAN-VULKAN1`
- **GPU Memory Used:** 9879.0 MB
- **CPU Memory Used:** 434.7 MB
- **Benchmark Running Time:** 6.93 s
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
- **Package Version:** `master-734-3ec374a-3-g3b6c9ca, commit 3b6c9ca9`
- **Metrics:**
  - Avg Generation Time:  6.83 seconds

### CPU Configuration Details

#### Text Chat (`local-chat`)
- **Benchmark Test Name:** `chat_cpu`
- **Device Setting:** `none`
- **Special Setting:** `Layers: 0 (Context: 5%)`
- **Model:** `qwen3` (`Qwen3.6-35B-A3B-APEX-I-Compact`)
- **Execution Target:** `CPU`
- **GPU Memory Used:** 1109.2 MB
- **CPU Memory Used:** 20981.7 MB
- **Benchmark Running Time:** 102.82 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LCHAT_ALIAS="qwen3"`
  - `LCHAT_CHAT_TEMPLATE_ARGS="--chat-template-file /data/public/machine-learning/models/vision-text/Qwen3.6-chat_template.jinja"`
  - `LCHAT_DEVICE="none"`
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
- **Errors Count:** 0
- **Package Version:** `9842 (6f4f53f2b7)`
- **Warmup (Phase 0):**
  - TTFT (Prefill):       997.77 ms
  - Prefill Speed:        19.04 tokens/sec
  - Generation Speed:     12.20 tokens/sec
- **Generation (Phase 2):**
  - Avg Completion Tokens: 600.0
  - Avg TTFT (Prefill):   35398.50 ms
  - Avg Prefill Speed:    41.61 tokens/sec
  - Avg Generation Speed: 11.64 tokens/sec
  - Avg Decode Time:      51.56 s
- **Vision Description (Phase 4):**
  - Avg TTFT (Prefill):   0.00 ms
  - Avg Generation Speed: 0.00 tokens/sec

#### Text Embedding (`local-embedding`)
- **Benchmark Test Name:** `embedding_cpu`
- **Device Setting:** `none`
- **Special Setting:** `Layers: 0`
- **Model:** `qwen3-embedding` (`Qwen3-Embedding-0.6B-Q8_0.gguf`)
- **Execution Target:** `CPU`
- **GPU Memory Used:** 0.1 MB
- **CPU Memory Used:** 2645.5 MB
- **Benchmark Running Time:** 28.90 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LMBD_ALIAS="qwen3-embedding"`
  - `LMBD_DEVICE="none"`
  - `LMBD_EXTRA_ARGS="--flash-attn on"`
  - `LMBD_HOST="127.0.0.1"`
  - `LMBD_MODEL="/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf"`
  - `LMBD_N_CTX="8192"`
  - `LMBD_N_GPU_LAYERS="0"`
  - `LMBD_N_UBATCH="512"`
  - `LMBD_PARALLEL="2"`
  - `LMBD_PORT="50082"`
  - `LMBD_THREADS="4"`
- **Errors Count:** 0
- **Package Version:** `9842 (6f4f53f2b7)`
- **Metrics:**
  - Avg Time/Run:         284.64 s
  - Avg Throughput:       143.90 tokens/sec
  - Avg Chunk Latency:    3558.1 ms
  - Avg Chunk p50:        3539.7 ms
  - Avg Chunk p95:        3701.4 ms

#### Document Reranking (`local-rerank`)
- **Benchmark Test Name:** `rerank_cpu`
- **Device Setting:** `none`
- **Special Setting:** `Layers: 0`
- **Model:** `qwen3-reranker` (`Qwen3-Reranker-0.6B.Q4_K_M.gguf`)
- **Execution Target:** `CPU`
- **GPU Memory Used:** 0.1 MB
- **CPU Memory Used:** 2711.2 MB
- **Benchmark Running Time:** 12.74 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LRR_ALIAS="qwen3-reranker"`
  - `LRR_DEVICE="none"`
  - `LRR_EXTRA_ARGS="--flash-attn on"`
  - `LRR_HOST="127.0.0.1"`
  - `LRR_MODEL="/data/public/machine-learning/models/reranker/Qwen3-Reranker-0.6B.Q4_K_M.gguf"`
  - `LRR_N_CTX="8192"`
  - `LRR_N_GPU_LAYERS="0"`
  - `LRR_PARALLEL="2"`
  - `LRR_PORT="50086"`
  - `LRR_THREADS="8"`
- **Errors Count:** 0
- **Package Version:** `9842 (6f4f53f2b7)`
- **Metrics:**
  - Avg Reranking Time:   12563.41 ms
  - Avg Docs Throughput:  0.80 docs/sec
  - Avg Token Speed:      273.73 tokens/sec

#### Speech-to-Text (STT) (`local-speech-to-text`)
- **Benchmark Test Name:** `stt_cpu`
- **Device Setting:** `none`
- **Special Setting:** `No GPU`
- **Model:** `whisper-1` (`ggml-large-v3-turbo-q5_0.bin`)
- **Execution Target:** `CPU`
- **GPU Memory Used:** 0.1 MB
- **CPU Memory Used:** 1102.1 MB
- **Benchmark Running Time:** 17.06 s
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
- **Package Version:** `1.9.1`
- **Metrics:**
  - Avg Transcribe Time:  16.87 seconds
  - Avg Real-Time Factor (RTF): 0.3748 (2.7x faster than real-time)

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Benchmark Test Name:** `tts_cpu`
- **Device Setting:** `none`
- **Special Setting:** `mode: cpu`
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `CPU`
- **GPU Memory Used:** 0.1 MB
- **CPU Memory Used:** 2956.2 MB
- **Benchmark Running Time:** 29.47 s
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
- **Errors Count:** 0
- **Package Version:** `unknown`
- **Metrics:**
  - Generated Audio Duration: 19.02 seconds
  - Avg Synthesis Time:   29.31 seconds
  - Avg Real-Time Factor (RTF): 1.5413
  - Avg Speed:            9.35 chars/sec

#### Image Generation (`local-image`)
- **Benchmark Test Name:** `image_cpu`
- **Device Setting:** `cpu`
- **Special Setting:** `Steps: 8`
- **Model:** `z_image_turbo-Q8_0` (`z_image_turbo-Q8_0.gguf`)
- **Execution Target:** `CPU`
- **GPU Memory Used:** 0.1 MB
- **CPU Memory Used:** 10137.6 MB
- **Benchmark Running Time:** 288.21 s
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
- **Package Version:** `master-734-3ec374a-3-g3b6c9ca, commit 3b6c9ca9`
- **Metrics:**
  - Avg Generation Time:  288.11 seconds

### CPU-BLAS Configuration Details

#### Text Chat (`local-chat`)
- **Benchmark Test Name:** `chat_cpu-blas`
- **Device Setting:** `BLAS`
- **Special Setting:** `Layers: 0 (Context: 5%)`
- **Model:** `qwen3` (`Qwen3.6-35B-A3B-APEX-I-Compact`)
- **Execution Target:** `CPU-BLAS`
- **GPU Memory Used:** 1109.2 MB
- **CPU Memory Used:** 20982.3 MB
- **Benchmark Running Time:** 101.92 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LCHAT_ALIAS="qwen3"`
  - `LCHAT_CHAT_TEMPLATE_ARGS="--chat-template-file /data/public/machine-learning/models/vision-text/Qwen3.6-chat_template.jinja"`
  - `LCHAT_DEVICE="BLAS"`
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
- **Errors Count:** 0
- **Package Version:** `9842 (6f4f53f2b7)`
- **Warmup (Phase 0):**
  - TTFT (Prefill):       950.71 ms
  - Prefill Speed:        19.99 tokens/sec
  - Generation Speed:     12.51 tokens/sec
- **Generation (Phase 2):**
  - Avg Completion Tokens: 600.0
  - Avg TTFT (Prefill):   35513.20 ms
  - Avg Prefill Speed:    41.48 tokens/sec
  - Avg Generation Speed: 11.75 tokens/sec
  - Avg Decode Time:      51.05 s
- **Vision Description (Phase 4):**
  - Avg TTFT (Prefill):   0.00 ms
  - Avg Generation Speed: 0.00 tokens/sec

#### Text Embedding (`local-embedding`)
- **Benchmark Test Name:** `embedding_cpu-blas`
- **Device Setting:** `BLAS`
- **Special Setting:** `Layers: 999`
- **Model:** `qwen3-embedding` (`Qwen3-Embedding-0.6B-Q8_0.gguf`)
- **Execution Target:** `CPU-BLAS`
- **GPU Memory Used:** 0.0 MB
- **CPU Memory Used:** 2645.9 MB
- **Benchmark Running Time:** 40.09 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LMBD_ALIAS="qwen3-embedding"`
  - `LMBD_DEVICE="BLAS"`
  - `LMBD_EXTRA_ARGS="--flash-attn on"`
  - `LMBD_HOST="127.0.0.1"`
  - `LMBD_MODEL="/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf"`
  - `LMBD_N_CTX="8192"`
  - `LMBD_N_GPU_LAYERS="0"`
  - `LMBD_N_UBATCH="512"`
  - `LMBD_PARALLEL="2"`
  - `LMBD_PORT="50082"`
  - `LMBD_THREADS="4"`
- **Errors Count:** 0
- **Package Version:** `9842 (6f4f53f2b7)`
- **Metrics:**
  - Avg Time/Run:         392.71 s
  - Avg Throughput:       104.30 tokens/sec
  - Avg Chunk Latency:    4908.9 ms
  - Avg Chunk p50:        5103.2 ms
  - Avg Chunk p95:        5462.2 ms

#### Document Reranking (`local-rerank`)
- **Benchmark Test Name:** `rerank_cpu-blas`
- **Device Setting:** `BLAS`
- **Special Setting:** `Layers: 99`
- **Model:** `qwen3-reranker` (`Qwen3-Reranker-0.6B.Q4_K_M.gguf`)
- **Execution Target:** `CPU-BLAS`
- **GPU Memory Used:** 0.1 MB
- **CPU Memory Used:** 2712.3 MB
- **Benchmark Running Time:** 12.54 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LRR_ALIAS="qwen3-reranker"`
  - `LRR_DEVICE="BLAS"`
  - `LRR_EXTRA_ARGS="--flash-attn on"`
  - `LRR_HOST="127.0.0.1"`
  - `LRR_MODEL="/data/public/machine-learning/models/reranker/Qwen3-Reranker-0.6B.Q4_K_M.gguf"`
  - `LRR_N_CTX="8192"`
  - `LRR_N_GPU_LAYERS="0"`
  - `LRR_PARALLEL="2"`
  - `LRR_PORT="50086"`
  - `LRR_THREADS="8"`
- **Errors Count:** 0
- **Package Version:** `9842 (6f4f53f2b7)`
- **Metrics:**
  - Avg Reranking Time:   12395.55 ms
  - Avg Docs Throughput:  0.81 docs/sec
  - Avg Token Speed:      277.44 tokens/sec

#### Speech-to-Text (STT) (`local-speech-to-text`)
- **Benchmark Test Name:** `stt_cpu-blas`
- **Device Setting:** `BLAS`
- **Special Setting:** `No GPU`
- **Model:** `whisper-1` (`ggml-large-v3-turbo-q5_0.bin`)
- **Execution Target:** `CPU-BLAS`
- **GPU Memory Used:** 0.1 MB
- **CPU Memory Used:** 1101.7 MB
- **Benchmark Running Time:** 14.16 s
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
- **Package Version:** `1.9.1`
- **Metrics:**
  - Avg Transcribe Time:  14.02 seconds
  - Avg Real-Time Factor (RTF): 0.3115 (3.2x faster than real-time)

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Benchmark Test Name:** `tts_cpu-blas`
- **Device Setting:** `BLAS`
- **Special Setting:** `mode: cpu`
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `CPU-BLAS`
- **GPU Memory Used:** 0.1 MB
- **CPU Memory Used:** 2969.4 MB
- **Benchmark Running Time:** 28.48 s
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
- **Errors Count:** 0
- **Package Version:** `unknown`
- **Metrics:**
  - Generated Audio Duration: 18.38 seconds
  - Avg Synthesis Time:   28.31 seconds
  - Avg Real-Time Factor (RTF): 1.5403
  - Avg Speed:            9.68 chars/sec

#### Image Generation (`local-image`)
- **Benchmark Test Name:** `image_cpu-blas`
- **Device Setting:** `cpu`
- **Special Setting:** `Steps: 8`
- **Model:** `z_image_turbo-Q8_0` (`z_image_turbo-Q8_0.gguf`)
- **Execution Target:** `CPU-BLAS`
- **GPU Memory Used:** 0.1 MB
- **CPU Memory Used:** 10137.6 MB
- **Benchmark Running Time:** 287.70 s
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
- **Package Version:** `master-734-3ec374a-3-g3b6c9ca, commit 3b6c9ca9`
- **Metrics:**
  - Avg Generation Time:  287.52 seconds

### SPECIAL (CPU-HIP-ROCM0) Configuration Details

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Benchmark Test Name:** `tts_cpu-hip-ROCm0`
- **Device Setting:** `ROCm0`
- **Special Setting:** `mode: hybrid`
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `SPECIAL (CPU-HIP-ROCM0)`
- **GPU Memory Used:** -fail-
- **CPU Memory Used:** -fail-
- **Benchmark Running Time:** -fail-
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
  - `Error: qwen3-tts-server failed to start or port timed out`
- **Package Version:** `unknown`
- **Metrics:**
  - Generated Audio Duration: -fail-
  - Avg Synthesis Time:   -fail-
  - Avg Real-Time Factor (RTF): -fail-
  - Avg Speed:            -fail-

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
- **Package Version:** `unknown`
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
- **GPU Memory Used:** 3345.3 MB
- **CPU Memory Used:** 710.0 MB
- **Benchmark Running Time:** 50.47 s
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
- **Errors Count:** 0
- **Package Version:** `unknown`
- **Metrics:**
  - Generated Audio Duration: 20.62 seconds
  - Avg Synthesis Time:   50.29 seconds
  - Avg Real-Time Factor (RTF): 2.4393
  - Avg Speed:            5.45 chars/sec

### SPECIAL (CPU-VULKAN-VULKAN1) Configuration Details

- **Device Name**: `AMD Radeon RX 7900 XTX` (Total: 24560 MiB, Free: 24560 MiB)

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Benchmark Test Name:** `tts_cpu-vulkan-Vulkan1`
- **Device Setting:** `Vulkan1`
- **Special Setting:** `mode: hybrid`
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `SPECIAL (CPU-VULKAN-VULKAN1)`
- **GPU Memory Used:** 3389.8 MB
- **CPU Memory Used:** 714.3 MB
- **Benchmark Running Time:** 6.91 s
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
- **Errors Count:** 0
- **Package Version:** `unknown`
- **Metrics:**
  - Generated Audio Duration: 20.70 seconds
  - Avg Synthesis Time:   6.76 seconds
  - Avg Real-Time Factor (RTF): 0.3265
  - Avg Speed:            40.55 chars/sec

### RUNNING Configuration Details

#### Text Chat (`local-chat`)
- **Benchmark Test Name:** `chat_running`
- **Device Setting:** `running on host`
- **Special Setting:** `unknown`
- **Model:** `qwen3` (`Qwen3.6-35B-A3B-APEX-I-Compact`)
- **Execution Target:** `RUNNING`
- **GPU Memory Used:** -n.a.-
- **CPU Memory Used:** -n.a.-
- **Benchmark Running Time:** 24.03 s
- **Active Environment Settings:**
  - `GGML_VK_DISABLE_MMVQ="1"`
  - `LCHAT_ALIAS="qwen3"`
  - `LCHAT_CACHE_TYPE_K="q4_0"`
  - `LCHAT_CACHE_TYPE_V="q4_0"`
  - `LCHAT_CHAT_TEMPLATE_FILE="/data/public/machine-learning/models/vision-text/Qwen3.6-chat_template.jinja"`
  - `LCHAT_CTX_SIZE="240384"`
  - `LCHAT_DEVICE="Vulkan1"`
  - `LCHAT_EMBEDDING_ENABLED="true"`
  - `LCHAT_EXTRA_ARGS=""`
  - `LCHAT_HOST="127.0.0.1"`
  - `LCHAT_MMPROJ="/data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact-mmproj.gguf"`
  - `LCHAT_MODEL="/data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact.gguf"`
  - `LCHAT_N_GPU_LAYERS="999"`
  - `LCHAT_PARALLEL="3"`
  - `LCHAT_PORT="50080"`
  - `LCHAT_SPECULATIVE="--spec-type ngram-simple --spec-ngram-simple-size-n 6 --spec-ngram-simple-size-m 4"`
  - `LCHAT_THREADS="4"`
  - `LMBD_ALIAS="qwen3-embedding"`
  - `LMBD_CACHE_TYPE_K="q8_0"`
  - `LMBD_CACHE_TYPE_V="q8_0"`
  - `LMBD_CTX_SIZE="8192"`
  - `LMBD_ENABLED="true"`
  - `LMBD_EXTRA_ARGS="--flash-attn on"`
  - `LMBD_MIRROR_PORT="50082"`
  - `LMBD_MODEL="/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf"`
  - `LMBD_PARALLEL="2"`
  - `LMBD_UBATCH_SIZE="512"`
  - `LOCAL_SIDECARS="portmirror"`
  - `LOCAL_SIDECAR_PORTMIRROR_CMD="bash -c 'if [ \"\${LMBD_ENABLED}\" = \"true\" ]; then exec socat TCP-LISTEN:\${LMBD_MIRROR_PORT:-50082},fork,reuseaddr TCP:\${LCHAT_HOST:-127.0.0.1}:\${LCHAT_PORT:-50080}; else exec sleep infinity; fi'"`
- **Errors Count:** 0
- **Package Version:** `9842 (6f4f53f2b7)`
- **Warmup (Phase 0):**
  - TTFT (Prefill):       89.36 ms
  - Prefill Speed:        212.62 tokens/sec
  - Generation Speed:     131.57 tokens/sec
- **Generation (Phase 2):**
  - Avg Completion Tokens: 600.0
  - Avg TTFT (Prefill):   17600.42 ms
  - Avg Prefill Speed:    1763.65 tokens/sec
  - Avg Generation Speed: 116.36 tokens/sec
  - Avg Decode Time:      5.16 s
- **Vision Description (Phase 4):**
  - Avg TTFT (Prefill):   0.00 ms
  - Avg Generation Speed: 0.00 tokens/sec

#### Text Embedding (`local-embedding`)
- **Benchmark Test Name:** `embedding_running`
- **Device Setting:** `running on host`
- **Special Setting:** `unknown`
- **Model:** `qwen3-embedding` (`Qwen3-Embedding-0.6B-Q8_0.gguf`)
- **Execution Target:** `RUNNING`
- **GPU Memory Used:** -n.a.-
- **CPU Memory Used:** -n.a.-
- **Benchmark Running Time:** 9.72 s
- **Active Environment Settings:**
  - `LMBD_ALIAS="qwen3-embedding"`
  - `LMBD_DEVICE="Vulkan1"`
  - `LMBD_EXTRA_ARGS="--flash-attn on"`
  - `LMBD_HOST="127.0.0.1"`
  - `LMBD_MODEL="/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf"`
  - `LMBD_N_CTX="8192"`
  - `LMBD_N_GPU_LAYERS="999"`
  - `LMBD_N_UBATCH="512"`
  - `LMBD_PARALLEL="2"`
  - `LMBD_PORT="50082"`
  - `LMBD_THREADS="4"`
- **Errors Count:** 0
- **Package Version:** `9842 (6f4f53f2b7)`
- **Metrics:**
  - Avg Time/Run:         9.44 s
  - Avg Throughput:       4816.26 tokens/sec
  - Avg Chunk Latency:    106.1 ms
  - Avg Chunk p50:        104.8 ms
  - Avg Chunk p95:        106.3 ms

#### Document Reranking (`local-rerank`)
- **Benchmark Test Name:** `rerank_running`
- **Device Setting:** `running on host`
- **Special Setting:** `unknown`
- **Model:** `qwen3-reranker` (`Qwen3-Reranker-0.6B.Q4_K_M.gguf`)
- **Execution Target:** `RUNNING`
- **GPU Memory Used:** -n.a.-
- **CPU Memory Used:** -n.a.-
- **Benchmark Running Time:** 10.32 s
- **Active Environment Settings:**
  - `LRR_ALIAS="qwen3-reranker"`
  - `LRR_DEVICE="none"`
  - `LRR_EXTRA_ARGS="--flash-attn on"`
  - `LRR_HOST="127.0.0.1"`
  - `LRR_MODEL="/data/public/machine-learning/models/reranker/Qwen3-Reranker-0.6B.Q4_K_M.gguf"`
  - `LRR_N_CTX="8192"`
  - `LRR_N_GPU_LAYERS="0"`
  - `LRR_PARALLEL="2"`
  - `LRR_PORT="50086"`
  - `LRR_THREADS="8"`
- **Errors Count:** 0
- **Package Version:** `9842 (6f4f53f2b7)`
- **Metrics:**
  - Avg Reranking Time:   10132.72 ms
  - Avg Docs Throughput:  0.99 docs/sec
  - Avg Token Speed:      339.40 tokens/sec

#### Speech-to-Text (STT) (`local-speech-to-text`)
- **Benchmark Test Name:** `stt_running`
- **Device Setting:** `running on host`
- **Special Setting:** `unknown`
- **Model:** `whisper-1` (`ggml-large-v3-turbo-q5_0.bin`)
- **Execution Target:** `RUNNING`
- **GPU Memory Used:** -n.a.-
- **CPU Memory Used:** -n.a.-
- **Benchmark Running Time:** 5.91 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `LSTT_DEVICE="0"`
  - `LSTT_EXTRA_ARGS=""`
  - `LSTT_HOST="127.0.0.1"`
  - `LSTT_INFERENCE_PATH="/v1/audio/transcriptions"`
  - `LSTT_MODEL="/data/public/machine-learning/models/speech-to-text/ggml-large-v3-turbo-q5_0.bin"`
  - `LSTT_MODEL_ALIAS="whisper-1"`
  - `LSTT_PORT="50090"`
  - `LSTT_THREADS="8"`
- **Errors Count:** 0
- **Package Version:** `1.9.1`
- **Metrics:**
  - Avg Transcribe Time:  5.58 seconds
  - Avg Real-Time Factor (RTF): 0.1240 (8.1x faster than real-time)

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Benchmark Test Name:** `tts_running`
- **Device Setting:** `running on host`
- **Special Setting:** `unknown`
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `RUNNING`
- **GPU Memory Used:** -n.a.-
- **CPU Memory Used:** -n.a.-
- **Benchmark Running Time:** 28.37 s
- **Active Environment Settings:**
  - `LTTS_DEVICE="none"`
  - `LTTS_EXTRA_ARGS=""`
  - `LTTS_HOST="127.0.0.1"`
  - `LTTS_MODE="cpu"`
  - `LTTS_MODEL="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf"`
  - `LTTS_PORT="50095"`
  - `LTTS_THREADS="8"`
  - `LTTS_VOCODER="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-Tokenizer-12Hz-F16.gguf"`
- **Errors Count:** 0
- **Package Version:** `unknown`
- **Metrics:**
  - Generated Audio Duration: 18.46 seconds
  - Avg Synthesis Time:   28.27 seconds
  - Avg Real-Time Factor (RTF): 1.5319
  - Avg Speed:            9.69 chars/sec

#### Image Generation (`local-image`)
- **Benchmark Test Name:** `image_running`
- **Device Setting:** `running on host`
- **Special Setting:** `unknown`
- **Model:** `z_image_turbo-Q8_0` (`z_image_turbo-Q8_0.gguf`)
- **Execution Target:** `RUNNING`
- **GPU Memory Used:** -n.a.-
- **CPU Memory Used:** -n.a.-
- **Benchmark Running Time:** 89.40 s
- **Active Environment Settings:**
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
- **Package Version:** `master-734-3ec374a-3-g3b6c9ca, commit 3b6c9ca9`
- **Metrics:**
  - Avg Generation Time:  89.30 seconds

