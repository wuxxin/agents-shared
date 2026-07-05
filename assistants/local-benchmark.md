# LLM Caching Optimization Benchmarks

**Benchmark Run Time:** `2026-07-04 22:27:18`

## Local Inference Services Benchmarks

We ran local benchmarks for text embedding, text-to-speech (TTS), speech-to-text (STT), document reranking, and image generation on the AMD Radeon RX 7900 XTX hardware target. All services run inside isolated sandboxed environments.

### 📊 Performance Comparison Matrix

#### Text Chat (`local-chat`)
| Configuration | Test Name | GPU | Special Setting | Avg Chat TTFT | Avg Chat Prefill | Chat TTFT (Warmup) | Chat Gen Speed | Avg Chat Gen | Chat Image TTFT | Chat Image Gen | Chat GPU Mem | Chat CPU Mem |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| [**HIP-COMBI-ROCM0**](#hip-combi-rocm0-configuration-details) | chat_hip-combi-ROCm0 | ROCm0 | Layers: 999 | 55195.27 ms | 562.39 t/s | 255.74 ms | 101.32 t/s | 66.77 t/s | 0.00 ms | 0.00 t/s | 20346.8 MB | 81.4 MB |
| [**HIP-ROCM0**](#hip-rocm0-configuration-details) | chat_hip-ROCm0 | ROCm0 | Layers: 999 | 55192.76 ms | 562.41 t/s | 302.68 ms | 101.31 t/s | 66.47 t/s | 0.00 ms | 0.00 t/s | 20346.9 MB | 77.9 MB |
| [**VULKAN-COMBI-VULKAN0**](#vulkan-combi-vulkan0-configuration-details) | chat_vulkan-combi-Vulkan0 | Vulkan0 | Layers: 999 (Context: 20%) | 69000.03 ms | 84.29 t/s | 1631.10 ms | 13.84 t/s | 12.86 t/s | 0.00 ms | 0.00 t/s | 13938.7 MB | 65.3 MB |
| [**VULKAN-COMBI-VULKAN1**](#vulkan-combi-vulkan1-configuration-details) | chat_vulkan-combi-Vulkan1 | Vulkan1 | Layers: 999 | 17753.22 ms | 1748.47 t/s | 143.14 ms | 132.22 t/s | **116.78 t/s** | 0.00 ms | 0.00 t/s | 19026.4 MB | 65.7 MB |
| [**VULKAN-VULKAN0**](#vulkan-vulkan0-configuration-details) | chat_vulkan-Vulkan0 | Vulkan0 | Layers: 999 (Context: 20%) | 69407.87 ms | 83.79 t/s | 1796.20 ms | 13.56 t/s | 12.58 t/s | 0.00 ms | 0.00 t/s | 13927.8 MB | 65.3 MB |
| [**VULKAN-VULKAN1**](#vulkan-vulkan1-configuration-details) | chat_vulkan-Vulkan1 | Vulkan1 | Layers: 999 | 17850.39 ms | 1738.95 t/s | 159.42 ms | 132.02 t/s | 116.13 t/s | 0.00 ms | 0.00 t/s | 19026.4 MB | 65.8 MB |
| [**CPU**](#cpu-configuration-details) | chat_cpu | none | Layers: 0 (Context: 5%) | 33334.50 ms | 44.19 t/s | 700.68 ms | 13.21 t/s | 12.55 t/s | 0.00 ms | 0.00 t/s | 1109.2 MB | 65.2 MB |
| [**CPU-COMBI**](#cpu-combi-configuration-details) | chat_cpu-combi | none | Layers: 0 (Context: 5%) | 36199.37 ms | 40.69 t/s | 859.65 ms | 12.88 t/s | 12.07 t/s | 0.00 ms | 0.00 t/s | 1109.2 MB | 65.2 MB |
| [**CPU-BLAS**](#cpu-blas-configuration-details) | chat_cpu-blas | BLAS | Layers: 0 (Context: 5%) | 36565.32 ms | 40.28 t/s | 856.16 ms | 12.98 t/s | 11.99 t/s | 0.00 ms | 0.00 t/s | 1109.2 MB | 64.9 MB |
| [**CPU-BLAS-COMBI**](#cpu-blas-combi-configuration-details) | chat_cpu-blas-combi | BLAS | Layers: 0 (Context: 5%) | 36080.19 ms | 40.83 t/s | 879.28 ms | 12.86 t/s | 11.95 t/s | 0.00 ms | 0.00 t/s | 1109.2 MB | 64.7 MB |
| [**SPECIAL-COMBI**](#special-combi-configuration-details) | chat_special-combi | special | Layers: 999 | -fail- | -fail- | -fail- | -fail- | -fail- | -n.a.- | -n.a.- | -fail- | -fail- |
| [**RUNNING**](#running-configuration-details) | chat_running | running on host | unknown | 17614.25 ms | **1762.27 t/s** | 118.68 ms | 129.71 t/s | 114.08 t/s | 0.00 ms | 0.00 t/s | -n.a.- | -n.a.- |

#### Text Embedding (`local-embedding`)
| Configuration | Test Name | GPU | Special Setting | Embedding Throughput | Embedding Latency (Avg) | Embedding GPU Mem | Embedding CPU Mem |
|---|---|---|---|---|---|---|---|
| [**HIP-COMBI-ROCM0**](#hip-combi-rocm0-configuration-details) | embedding_hip-combi-ROCm0 | ROCm0 | Layers: 999 | **5851.93 t/s** | 87.3 ms | 22324.3 MB | 84.3 MB |
| [**HIP-ROCM0**](#hip-rocm0-configuration-details) | embedding_hip-ROCm0 | ROCm0 | Layers: 999 | 5624.86 t/s | 90.8 ms | 1977.5 MB | 3612.1 MB |
| [**VULKAN-COMBI-VULKAN0**](#vulkan-combi-vulkan0-configuration-details) | embedding_vulkan-combi-Vulkan0 | Vulkan0 | Layers: 999 | 812.08 t/s | 629.0 ms | 13941.8 MB | 68.5 MB |
| [**VULKAN-COMBI-VULKAN1**](#vulkan-combi-vulkan1-configuration-details) | embedding_vulkan-combi-Vulkan1 | Vulkan1 | Layers: 999 | 5307.90 t/s | 96.2 ms | 20446.5 MB | 68.6 MB |
| [**VULKAN-VULKAN0**](#vulkan-vulkan0-configuration-details) | embedding_vulkan-Vulkan0 | Vulkan0 | Layers: 999 | 651.82 t/s | 783.6 ms | 1390.2 MB | 3011.1 MB |
| [**VULKAN-VULKAN1**](#vulkan-vulkan1-configuration-details) | embedding_vulkan-Vulkan1 | Vulkan1 | Layers: 999 | 5325.07 t/s | 95.9 ms | 1180.3 MB | 2917.0 MB |
| [**CPU**](#cpu-configuration-details) | embedding_cpu | none | Layers: 0 | 182.42 t/s | 2806.7 ms | 0.1 MB | 2641.9 MB |
| [**CPU-COMBI**](#cpu-combi-configuration-details) | embedding_cpu-combi | none | Layers: 999 | 117.63 t/s | 4352.6 ms | 1109.3 MB | 67.9 MB |
| [**CPU-BLAS**](#cpu-blas-configuration-details) | embedding_cpu-blas | BLAS | Layers: 999 | 120.65 t/s | 4243.7 ms | 0.1 MB | 2642.0 MB |
| [**CPU-BLAS-COMBI**](#cpu-blas-combi-configuration-details) | embedding_cpu-blas-combi | BLAS | Layers: 999 | 120.86 t/s | 4236.1 ms | 1109.3 MB | 67.6 MB |
| [**RUNNING**](#running-configuration-details) | embedding_running | running on host | unknown | 4877.78 t/s | 104.7 ms | -n.a.- | -n.a.- |

#### Document Reranking (`local-rerank`)
| Configuration | Test Name | GPU | Special Setting | Avg Reranking Time | Avg Token Speed | Avg Docs Throughput | GPU Mem | CPU Mem |
|---|---|---|---|---|---|---|---|---|
| [**HIP-ROCM0**](#hip-rocm0-configuration-details) | rerank_hip-ROCm0 | ROCm0 | Layers: 99 | 846.45 ms | **4062.86 tokens/s** | 11.81 docs/s | 2532.9 MB | 819.0 MB |
| [**VULKAN-VULKAN0**](#vulkan-vulkan0-configuration-details) | rerank_vulkan-Vulkan0 | Vulkan0 | Layers: 99 | 5112.79 ms | 672.63 tokens/s | 1.96 docs/s | 1593.9 MB | 263.1 MB |
| [**VULKAN-VULKAN1**](#vulkan-vulkan1-configuration-details) | rerank_vulkan-Vulkan1 | Vulkan1 | Layers: 99 | 875.32 ms | 3928.84 tokens/s | 11.42 docs/s | 1597.7 MB | 265.8 MB |
| [**CPU**](#cpu-configuration-details) | rerank_cpu | none | Layers: 0 | 10044.38 ms | 342.38 tokens/s | 1.00 docs/s | 0.1 MB | 2707.8 MB |
| [**CPU-BLAS**](#cpu-blas-configuration-details) | rerank_cpu-blas | BLAS | Layers: 99 | 14062.26 ms | 244.56 tokens/s | 0.71 docs/s | 0.1 MB | 2708.7 MB |
| [**RUNNING**](#running-configuration-details) | rerank_running | running on host | unknown | 14651.89 ms | 234.71 tokens/s | 0.68 docs/s | -n.a.- | -n.a.- |

#### Speech-to-Text (STT) (`local-speech-to-text`)
| Configuration | Test Name | GPU | Special Setting | Avg Transcribe Time | Avg Real-Time Factor (RTF) | Speedup vs Real-time | GPU Mem | CPU Mem |
|---|---|---|---|---|---|---|---|---|
| [**HIP-ROCM0**](#hip-rocm0-configuration-details) | stt_hip-ROCm0 | 0 | Use GPU | -fail- VALIDATION | -fail- VALIDATION | -fail- VALIDATION | 1264.4 MB | 485.9 MB |
| [**VULKAN-VULKAN0**](#vulkan-vulkan0-configuration-details) | stt_vulkan-Vulkan0 | 0 | Use GPU | 5.57 s | 0.1238 | 8.1x | 802.2 MB | 126.1 MB |
| [**VULKAN-VULKAN1**](#vulkan-vulkan1-configuration-details) | stt_vulkan-Vulkan1 | 1 | Use GPU | 0.88 s | 0.0195 | **51.4x** | 839.8 MB | 150.2 MB |
| [**CPU**](#cpu-configuration-details) | stt_cpu | none | No GPU | 12.14 s | 0.2698 | 3.7x | 0.1 MB | 1099.2 MB |
| [**CPU-BLAS**](#cpu-blas-configuration-details) | stt_cpu-blas | BLAS | No GPU | 16.94 s | 0.3765 | 2.7x | 0.1 MB | 1097.6 MB |
| [**RUNNING**](#running-configuration-details) | stt_running | running on host | unknown | 5.59 s | 0.1243 | 8.0x | -n.a.- | -n.a.- |

#### Text-to-Speech (TTS) (`local-text-to-speech`)
| Configuration | Test Name | GPU | Special Setting | Avg Synthesis Time | Avg Real-Time Factor (RTF) | Speed (chars/s) | GPU Mem | CPU Mem |
|---|---|---|---|---|---|---|---|---|
| [**HIP-ROCM0**](#hip-rocm0-configuration-details) | tts_hip-ROCm0 | ROCm0 | mode: gpu | 16.32 s | 0.9330 | 16.78 chars/s | 3493.9 MB | 1090.3 MB |
| [**VULKAN-VULKAN0**](#vulkan-vulkan0-configuration-details) | tts_vulkan-Vulkan0 | Vulkan0 | mode: gpu | 54.94 s | 2.4465 | 4.99 chars/s | 3552.1 MB | 787.7 MB |
| [**VULKAN-VULKAN1**](#vulkan-vulkan1-configuration-details) | tts_vulkan-Vulkan1 | Vulkan1 | mode: gpu | -fail- VALIDATION | 0.3457 | 39.52 chars/s | 3393.2 MB | 729.0 MB |
| [**CPU**](#cpu-configuration-details) | tts_cpu | none | mode: cpu | -fail- VALIDATION | 1.5229 | 9.12 chars/s | 0.1 MB | 2998.5 MB |
| [**CPU-BLAS**](#cpu-blas-configuration-details) | tts_cpu-blas | BLAS | mode: cpu | 30.63 s | 1.6242 | 8.95 chars/s | 0.1 MB | 2997.6 MB |
| [**CPU-HIP-ROCM0**](#special-cpu-hip-rocm0-configuration-details) | tts_cpu-hip-ROCm0 | ROCm0 | mode: hybrid | 19.18 s | 0.9413 | 14.29 chars/s | 3717.9 MB | 1161.0 MB |
| [**CPU-HIP-ROCM1**](#special-cpu-hip-rocm1-configuration-details) | tts_cpu-hip-ROCm1 | ROCm1 | mode: hybrid | -fail- | -fail- | -fail- | -fail- | -fail- |
| [**CPU-VULKAN-VULKAN0**](#special-cpu-vulkan-vulkan0-configuration-details) | tts_cpu-vulkan-Vulkan0 | Vulkan0 | mode: hybrid | 50.09 s | 2.4487 | 5.47 chars/s | 3378.7 MB | 696.9 MB |
| [**CPU-VULKAN-VULKAN1**](#special-cpu-vulkan-vulkan1-configuration-details) | tts_cpu-vulkan-Vulkan1 | Vulkan1 | mode: hybrid | 6.60 s | 0.3371 | **41.52 chars/s** | 3354.3 MB | 677.4 MB |
| [**RUNNING**](#running-configuration-details) | tts_running | running on host | unknown | 34.63 s | 1.9178 | 7.91 chars/s | -n.a.- | -n.a.- |

#### Image Generation (`local-image`)
| Configuration | Test Name | GPU | Special Setting | Avg Generation Time | GPU Mem | CPU Mem |
|---|---|---|---|---|---|---|
| [**HIP-ROCM0**](#hip-rocm0-configuration-details) | image_hip-ROCm0 | rocm0 | Steps: 8 | 7.43 s | 10758.5 MB | 862.6 MB |
| [**VULKAN-VULKAN0**](#vulkan-vulkan0-configuration-details) | image_vulkan-Vulkan0 | vulkan0,te=cpu | Steps: 8 | 92.76 s | 6354.1 MB | 3804.6 MB |
| [**VULKAN-VULKAN1**](#vulkan-vulkan1-configuration-details) | image_vulkan-Vulkan1 | vulkan1 | Steps: 8 | **6.96 s** | 9892.4 MB | 510.0 MB |
| [**CPU**](#cpu-configuration-details) | image_cpu | cpu | Steps: 8 | 282.65 s | 0.1 MB | 10132.8 MB |
| [**CPU-BLAS**](#cpu-blas-configuration-details) | image_cpu-blas | cpu | Steps: 8 | 281.93 s | 0.1 MB | 10131.6 MB |
| [**RUNNING**](#running-configuration-details) | image_running | running on host | unknown | 89.35 s | -n.a.- | -n.a.- |

---

### ⚙️ Detailed Configuration Reports

### HIP-COMBI-ROCM0 Configuration Details

- **Device Name**: `AMD Radeon RX 7900 XTX` (Total: 24560 MiB, Free: 24560 MiB)

#### Text Chat (`local-chat`)
- **Benchmark Test Name:** `chat_hip-combi-ROCm0`
- **Device Setting:** `ROCm0`
- **Special Setting:** `Layers: 999`
- **Model:** `qwen3` (`Qwen3.6-35B-A3B-APEX-I-Compact`)
- **Execution Target:** `HIP-COMBI-ROCM0`
- **GPU Memory Used:** 20346.8 MB
- **CPU Memory Used:** 81.4 MB
- **Benchmark Running Time:** 66.13 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES="0"`
  - `GGML_VK_DISABLE_MMVQ="1"`
  - `HIP_VISIBLE_DEVICES="0"`
  - `LCHAT_ALIAS="qwen3"`
  - `LCHAT_CACHE_TYPE_K="q4_0"`
  - `LCHAT_CACHE_TYPE_V="q4_0"`
  - `LCHAT_CHAT_TEMPLATE_FILE="/data/public/machine-learning/models/vision-text/Qwen3.6-chat_template.jinja"`
  - `LCHAT_CTX_SIZE="240384"`
  - `LCHAT_DEVICE="ROCm0"`
  - `LCHAT_EMBEDDING_ENABLED="true"`
  - `LCHAT_EXTRA_ARGS=""`
  - `LCHAT_HOST="127.0.0.1"`
  - `LCHAT_MMPROJ="/data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact-mmproj.gguf"`
  - `LCHAT_MODEL="/data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact.gguf"`
  - `LCHAT_N_CTX="240384"`
  - `LCHAT_N_GPU_LAYERS="999"`
  - `LCHAT_PARALLEL="3"`
  - `LCHAT_PORT="50080"`
  - `LCHAT_SERVE_EMBEDDINGS="true"`
  - `LCHAT_SPECULATIVE="--spec-type ngram-simple --spec-ngram-simple-size-n 6 --spec-ngram-simple-size-m 4"`
  - `LCHAT_THREADS="4"`
  - `LMBD_ALIAS="qwen3-embedding"`
  - `LMBD_CACHE_TYPE_K="q8_0"`
  - `LMBD_CACHE_TYPE_V="q8_0"`
  - `LMBD_CTX_SIZE="8192"`
  - `LMBD_DEVICE="ROCm0"`
  - `LMBD_ENABLED="true"`
  - `LMBD_EXTRA_ARGS="--flash-attn on"`
  - `LMBD_MIRROR_PORT="50082"`
  - `LMBD_MODEL="/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf"`
  - `LMBD_N_CTX="8192"`
  - `LMBD_N_GPU_LAYERS="999"`
  - `LMBD_PARALLEL="2"`
  - `LMBD_UBATCH_SIZE="512"`
  - `LOCAL_SIDECARS="portmirror"`
  - `LOCAL_SIDECAR_PORTMIRROR_CMD="bash -c 'if [ \"\${LMBD_ENABLED}\" = \"true\" ]; then exec socat TCP-LISTEN:\${LMBD_MIRROR_PORT:-50082},fork,reuseaddr TCP:\${LCHAT_HOST:-127.0.0.1}:\${LCHAT_PORT:-50080}; else exec sleep infinity; fi'"`
- **Errors Count:** 0
- **Package Version:** `9860 (fdb1db877c)`
- **Warmup (Phase 0):**
  - TTFT (Prefill):       255.74 ms
  - Prefill Speed:        74.29 tokens/sec
  - Generation Speed:     101.32 tokens/sec
- **Generation (Phase 2):**
  - Avg Completion Tokens: 600.0
  - Avg TTFT (Prefill):   55195.27 ms
  - Avg Prefill Speed:    562.39 tokens/sec
  - Avg Generation Speed: 66.77 tokens/sec
  - Avg Decode Time:      8.99 s
- **Vision Description (Phase 4):**
  - Avg TTFT (Prefill):   0.00 ms
  - Avg Generation Speed: 0.00 tokens/sec

#### Text Embedding (`local-embedding`)
- **Benchmark Test Name:** `embedding_hip-combi-ROCm0`
- **Device Setting:** `ROCm0`
- **Special Setting:** `Layers: 999`
- **Model:** `qwen3-embedding` (`Qwen3-Embedding-0.6B-Q8_0.gguf`)
- **Execution Target:** `HIP-COMBI-ROCM0`
- **GPU Memory Used:** 22324.3 MB
- **CPU Memory Used:** 84.3 MB
- **Benchmark Running Time:** 8.12 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES="0"`
  - `GGML_VK_DISABLE_MMVQ="1"`
  - `HIP_VISIBLE_DEVICES="0"`
  - `LCHAT_ALIAS="qwen3"`
  - `LCHAT_CACHE_TYPE_K="q4_0"`
  - `LCHAT_CACHE_TYPE_V="q4_0"`
  - `LCHAT_CHAT_TEMPLATE_FILE="/data/public/machine-learning/models/vision-text/Qwen3.6-chat_template.jinja"`
  - `LCHAT_CTX_SIZE="240384"`
  - `LCHAT_DEVICE="ROCm0"`
  - `LCHAT_EMBEDDING_ENABLED="true"`
  - `LCHAT_EXTRA_ARGS=""`
  - `LCHAT_HOST="127.0.0.1"`
  - `LCHAT_MMPROJ="/data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact-mmproj.gguf"`
  - `LCHAT_MODEL="/data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact.gguf"`
  - `LCHAT_N_CTX="240384"`
  - `LCHAT_N_GPU_LAYERS="999"`
  - `LCHAT_PARALLEL="3"`
  - `LCHAT_PORT="50080"`
  - `LCHAT_SERVE_EMBEDDINGS="true"`
  - `LCHAT_SPECULATIVE="--spec-type ngram-simple --spec-ngram-simple-size-n 6 --spec-ngram-simple-size-m 4"`
  - `LCHAT_THREADS="4"`
  - `LMBD_ALIAS="qwen3-embedding"`
  - `LMBD_CACHE_TYPE_K="q8_0"`
  - `LMBD_CACHE_TYPE_V="q8_0"`
  - `LMBD_CTX_SIZE="8192"`
  - `LMBD_DEVICE="ROCm0"`
  - `LMBD_ENABLED="true"`
  - `LMBD_EXTRA_ARGS="--flash-attn on"`
  - `LMBD_MIRROR_PORT="50082"`
  - `LMBD_MODEL="/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf"`
  - `LMBD_N_CTX="8192"`
  - `LMBD_N_GPU_LAYERS="999"`
  - `LMBD_PARALLEL="2"`
  - `LMBD_UBATCH_SIZE="512"`
  - `LOCAL_SIDECARS="portmirror"`
  - `LOCAL_SIDECAR_PORTMIRROR_CMD="bash -c 'if [ \"\${LMBD_ENABLED}\" = \"true\" ]; then exec socat TCP-LISTEN:\${LMBD_MIRROR_PORT:-50082},fork,reuseaddr TCP:\${LCHAT_HOST:-127.0.0.1}:\${LCHAT_PORT:-50080}; else exec sleep infinity; fi'"`
- **Errors Count:** 0
- **Package Version:** `9860 (fdb1db877c)`
- **Metrics:**
  - Avg Time/Run:         7.77 s
  - Avg Throughput:       5851.93 tokens/sec
  - Avg Chunk Latency:    87.3 ms
  - Avg Chunk p50:        86.8 ms
  - Avg Chunk p95:        87.6 ms

### HIP-ROCM0 Configuration Details

- **Device Name**: `AMD Radeon RX 7900 XTX` (Total: 24560 MiB, Free: 24560 MiB)

#### Text Chat (`local-chat`)
- **Benchmark Test Name:** `chat_hip-ROCm0`
- **Device Setting:** `ROCm0`
- **Special Setting:** `Layers: 999`
- **Model:** `qwen3` (`Qwen3.6-35B-A3B-APEX-I-Compact`)
- **Execution Target:** `HIP-ROCM0`
- **GPU Memory Used:** 20346.9 MB
- **CPU Memory Used:** 77.9 MB
- **Benchmark Running Time:** 66.21 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES="0"`
  - `GGML_VK_DISABLE_MMVQ="1"`
  - `HIP_VISIBLE_DEVICES="0"`
  - `LCHAT_ALIAS="qwen3"`
  - `LCHAT_CACHE_TYPE_K="q4_0"`
  - `LCHAT_CACHE_TYPE_V="q4_0"`
  - `LCHAT_CHAT_TEMPLATE_FILE="/data/public/machine-learning/models/vision-text/Qwen3.6-chat_template.jinja"`
  - `LCHAT_CTX_SIZE="240384"`
  - `LCHAT_DEVICE="ROCm0"`
  - `LCHAT_EMBEDDING_ENABLED="false"`
  - `LCHAT_EXTRA_ARGS=""`
  - `LCHAT_HOST="127.0.0.1"`
  - `LCHAT_MMPROJ="/data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact-mmproj.gguf"`
  - `LCHAT_MODEL="/data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact.gguf"`
  - `LCHAT_N_CTX="240384"`
  - `LCHAT_N_GPU_LAYERS="999"`
  - `LCHAT_PARALLEL="3"`
  - `LCHAT_PORT="50080"`
  - `LCHAT_SERVE_EMBEDDINGS="false"`
  - `LCHAT_SPECULATIVE="--spec-type ngram-simple --spec-ngram-simple-size-n 6 --spec-ngram-simple-size-m 4"`
  - `LCHAT_THREADS="4"`
  - `LMBD_ALIAS="qwen3-embedding"`
  - `LMBD_CACHE_TYPE_K="q8_0"`
  - `LMBD_CACHE_TYPE_V="q8_0"`
  - `LMBD_CTX_SIZE="8192"`
  - `LMBD_ENABLED="false"`
  - `LMBD_EXTRA_ARGS="--flash-attn on"`
  - `LMBD_MIRROR_PORT="50082"`
  - `LMBD_MODEL="/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf"`
  - `LMBD_PARALLEL="2"`
  - `LMBD_UBATCH_SIZE="512"`
  - `LOCAL_SIDECARS="portmirror"`
  - `LOCAL_SIDECAR_PORTMIRROR_CMD="bash -c 'if [ \"\${LMBD_ENABLED}\" = \"true\" ]; then exec socat TCP-LISTEN:\${LMBD_MIRROR_PORT:-50082},fork,reuseaddr TCP:\${LCHAT_HOST:-127.0.0.1}:\${LCHAT_PORT:-50080}; else exec sleep infinity; fi'"`
- **Errors Count:** 0
- **Package Version:** `9860 (fdb1db877c)`
- **Warmup (Phase 0):**
  - TTFT (Prefill):       302.68 ms
  - Prefill Speed:        62.77 tokens/sec
  - Generation Speed:     101.31 tokens/sec
- **Generation (Phase 2):**
  - Avg Completion Tokens: 600.0
  - Avg TTFT (Prefill):   55192.76 ms
  - Avg Prefill Speed:    562.41 tokens/sec
  - Avg Generation Speed: 66.47 tokens/sec
  - Avg Decode Time:      9.03 s
- **Vision Description (Phase 4):**
  - Avg TTFT (Prefill):   0.00 ms
  - Avg Generation Speed: 0.00 tokens/sec

#### Text Embedding (`local-embedding`)
- **Benchmark Test Name:** `embedding_hip-ROCm0`
- **Device Setting:** `ROCm0`
- **Special Setting:** `Layers: 999`
- **Model:** `qwen3-embedding` (`Qwen3-Embedding-0.6B-Q8_0.gguf`)
- **Execution Target:** `HIP-ROCM0`
- **GPU Memory Used:** 1977.5 MB
- **CPU Memory Used:** 3612.1 MB
- **Benchmark Running Time:** 8.42 s
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
- **Package Version:** `9860 (fdb1db877c)`
- **Metrics:**
  - Avg Time/Run:         8.08 s
  - Avg Throughput:       5624.86 tokens/sec
  - Avg Chunk Latency:    90.8 ms
  - Avg Chunk p50:        90.1 ms
  - Avg Chunk p95:        91.3 ms

#### Document Reranking (`local-rerank`)
- **Benchmark Test Name:** `rerank_hip-ROCm0`
- **Device Setting:** `ROCm0`
- **Special Setting:** `Layers: 99`
- **Model:** `qwen3-reranker` (`Qwen3-Reranker-0.6B.Q4_K_M.gguf`)
- **Execution Target:** `HIP-ROCM0`
- **GPU Memory Used:** 2532.9 MB
- **CPU Memory Used:** 819.0 MB
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
- **Package Version:** `9860 (fdb1db877c)`
- **Metrics:**
  - Avg Reranking Time:   846.45 ms
  - Avg Docs Throughput:  11.81 docs/sec
  - Avg Token Speed:      4062.86 tokens/sec

#### Speech-to-Text (STT) (`local-speech-to-text`)
- **Benchmark Test Name:** `stt_hip-ROCm0`
- **Device Setting:** `0`
- **Special Setting:** `Use GPU`
- **Model:** `whisper-1` (`ggml-large-v3-turbo-q5_0.bin`)
- **Execution Target:** `HIP-ROCM0`
- **GPU Memory Used:** 1264.4 MB
- **CPU Memory Used:** 485.9 MB
- **Benchmark Running Time:** 4.01 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES="0"`
  - `HIP_VISIBLE_DEVICES="0"`
  - `LSTT_DEVICE="0"`
  - `LSTT_EXTRA_ARGS=""`
  - `LSTT_HOST="127.0.0.1"`
  - `LSTT_INFERENCE_PATH="/v1/audio/transcriptions"`
  - `LSTT_MODEL="/data/public/machine-learning/models/speech-to-text/ggml-large-v3-turbo-q5_0.bin"`
  - `LSTT_ALIAS="whisper-1"`
  - `LSTT_NO_GPU="false"`
  - `LSTT_PORT="50090"`
  - `LSTT_THREADS="8"`
- **Errors Count:** 1
- **Top Errors:**
  - `Warning: STT Transcription text mismatch (garbled output)`
- **Package Version:** `1.9.1 (6fc7c33b4)`
- **Metrics:**
  - Avg Transcribe Time:  -fail- VALIDATION
  - Avg Real-Time Factor (RTF): -fail- VALIDATION (-fail- VALIDATION faster than real-time)

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Benchmark Test Name:** `tts_hip-ROCm0`
- **Device Setting:** `ROCm0`
- **Special Setting:** `mode: gpu`
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `HIP-ROCM0`
- **GPU Memory Used:** 3493.9 MB
- **CPU Memory Used:** 1090.3 MB
- **Benchmark Running Time:** 16.43 s
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
- **Errors Count:** 0
- **Package Version:** `qwen3-tts version 0.1-main-0c8b2ba`
- **Metrics:**
  - Generated Audio Duration: 17.50 seconds
  - Avg Synthesis Time:   16.32 seconds
  - Avg Real-Time Factor (RTF): 0.9330
  - Avg Speed:            16.78 chars/sec

#### Image Generation (`local-image`)
- **Benchmark Test Name:** `image_hip-ROCm0`
- **Device Setting:** `rocm0`
- **Special Setting:** `Steps: 8`
- **Model:** `z_image_turbo-Q8_0` (`z_image_turbo-Q8_0.gguf`)
- **Execution Target:** `HIP-ROCM0`
- **GPU Memory Used:** 10758.5 MB
- **CPU Memory Used:** 862.6 MB
- **Benchmark Running Time:** 7.52 s
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
- **Package Version:** `master-746-2574f59, commit 2574f593`
- **Metrics:**
  - Avg Generation Time:  7.43 seconds

### VULKAN-COMBI-VULKAN0 Configuration Details

- **Device Name**: `AMD Radeon Graphics` (Total: 16384 MiB, Free: 16384 MiB)

#### Text Chat (`local-chat`)
- **Benchmark Test Name:** `chat_vulkan-combi-Vulkan0`
- **Device Setting:** `Vulkan0`
- **Special Setting:** `Layers: 999 (Context: 20%)`
- **Model:** `qwen3` (`Qwen3.6-35B-A3B-APEX-I-Compact`)
- **Execution Target:** `VULKAN-COMBI-VULKAN0`
- **GPU Memory Used:** 13938.7 MB
- **CPU Memory Used:** 65.3 MB
- **Benchmark Running Time:** 129.88 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `GGML_VK_DISABLE_MMVQ="1"`
  - `HIP_VISIBLE_DEVICES=""`
  - `LCHAT_ALIAS="qwen3"`
  - `LCHAT_CACHE_TYPE_K="q4_0"`
  - `LCHAT_CACHE_TYPE_V="q4_0"`
  - `LCHAT_CHAT_TEMPLATE_FILE="/data/public/machine-learning/models/vision-text/Qwen3.6-chat_template.jinja"`
  - `LCHAT_CTX_SIZE="240384"`
  - `LCHAT_DEVICE="Vulkan0"`
  - `LCHAT_EMBEDDING_ENABLED="true"`
  - `LCHAT_EXTRA_ARGS=""`
  - `LCHAT_HOST="127.0.0.1"`
  - `LCHAT_MMPROJ="/data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact-mmproj.gguf"`
  - `LCHAT_MODEL="/data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact.gguf"`
  - `LCHAT_N_CTX="48076"`
  - `LCHAT_N_GPU_LAYERS="999"`
  - `LCHAT_PARALLEL="3"`
  - `LCHAT_PORT="50080"`
  - `LCHAT_SERVE_EMBEDDINGS="true"`
  - `LCHAT_SPECULATIVE="--spec-type ngram-simple --spec-ngram-simple-size-n 6 --spec-ngram-simple-size-m 4"`
  - `LCHAT_THREADS="4"`
  - `LMBD_ALIAS="qwen3-embedding"`
  - `LMBD_CACHE_TYPE_K="q8_0"`
  - `LMBD_CACHE_TYPE_V="q8_0"`
  - `LMBD_CTX_SIZE="8192"`
  - `LMBD_DEVICE="Vulkan0"`
  - `LMBD_ENABLED="true"`
  - `LMBD_EXTRA_ARGS="--flash-attn on"`
  - `LMBD_MIRROR_PORT="50082"`
  - `LMBD_MODEL="/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf"`
  - `LMBD_N_CTX="8192"`
  - `LMBD_N_GPU_LAYERS="999"`
  - `LMBD_PARALLEL="2"`
  - `LMBD_UBATCH_SIZE="512"`
  - `LOCAL_SIDECARS="portmirror"`
  - `LOCAL_SIDECAR_PORTMIRROR_CMD="bash -c 'if [ \"\${LMBD_ENABLED}\" = \"true\" ]; then exec socat TCP-LISTEN:\${LMBD_MIRROR_PORT:-50082},fork,reuseaddr TCP:\${LCHAT_HOST:-127.0.0.1}:\${LCHAT_PORT:-50080}; else exec sleep infinity; fi'"`
- **Errors Count:** 0
- **Package Version:** `9860 (fdb1db877c)`
- **Warmup (Phase 0):**
  - TTFT (Prefill):       1631.10 ms
  - Prefill Speed:        11.65 tokens/sec
  - Generation Speed:     13.84 tokens/sec
- **Generation (Phase 2):**
  - Avg Completion Tokens: 600.0
  - Avg TTFT (Prefill):   69000.03 ms
  - Avg Prefill Speed:    84.29 tokens/sec
  - Avg Generation Speed: 12.86 tokens/sec
  - Avg Decode Time:      46.66 s
- **Vision Description (Phase 4):**
  - Avg TTFT (Prefill):   0.00 ms
  - Avg Generation Speed: 0.00 tokens/sec

#### Text Embedding (`local-embedding`)
- **Benchmark Test Name:** `embedding_vulkan-combi-Vulkan0`
- **Device Setting:** `Vulkan0`
- **Special Setting:** `Layers: 999`
- **Model:** `qwen3-embedding` (`Qwen3-Embedding-0.6B-Q8_0.gguf`)
- **Execution Target:** `VULKAN-COMBI-VULKAN0`
- **GPU Memory Used:** 13941.8 MB
- **CPU Memory Used:** 68.5 MB
- **Benchmark Running Time:** 56.18 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `GGML_VK_DISABLE_MMVQ="1"`
  - `HIP_VISIBLE_DEVICES=""`
  - `LCHAT_ALIAS="qwen3"`
  - `LCHAT_CACHE_TYPE_K="q4_0"`
  - `LCHAT_CACHE_TYPE_V="q4_0"`
  - `LCHAT_CHAT_TEMPLATE_FILE="/data/public/machine-learning/models/vision-text/Qwen3.6-chat_template.jinja"`
  - `LCHAT_CTX_SIZE="240384"`
  - `LCHAT_DEVICE="Vulkan0"`
  - `LCHAT_EMBEDDING_ENABLED="true"`
  - `LCHAT_EXTRA_ARGS=""`
  - `LCHAT_HOST="127.0.0.1"`
  - `LCHAT_MMPROJ="/data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact-mmproj.gguf"`
  - `LCHAT_MODEL="/data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact.gguf"`
  - `LCHAT_N_CTX="48076"`
  - `LCHAT_N_GPU_LAYERS="999"`
  - `LCHAT_PARALLEL="3"`
  - `LCHAT_PORT="50080"`
  - `LCHAT_SERVE_EMBEDDINGS="true"`
  - `LCHAT_SPECULATIVE="--spec-type ngram-simple --spec-ngram-simple-size-n 6 --spec-ngram-simple-size-m 4"`
  - `LCHAT_THREADS="4"`
  - `LMBD_ALIAS="qwen3-embedding"`
  - `LMBD_CACHE_TYPE_K="q8_0"`
  - `LMBD_CACHE_TYPE_V="q8_0"`
  - `LMBD_CTX_SIZE="8192"`
  - `LMBD_DEVICE="Vulkan0"`
  - `LMBD_ENABLED="true"`
  - `LMBD_EXTRA_ARGS="--flash-attn on"`
  - `LMBD_MIRROR_PORT="50082"`
  - `LMBD_MODEL="/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf"`
  - `LMBD_N_CTX="8192"`
  - `LMBD_N_GPU_LAYERS="999"`
  - `LMBD_PARALLEL="2"`
  - `LMBD_UBATCH_SIZE="512"`
  - `LOCAL_SIDECARS="portmirror"`
  - `LOCAL_SIDECAR_PORTMIRROR_CMD="bash -c 'if [ \"\${LMBD_ENABLED}\" = \"true\" ]; then exec socat TCP-LISTEN:\${LMBD_MIRROR_PORT:-50082},fork,reuseaddr TCP:\${LCHAT_HOST:-127.0.0.1}:\${LCHAT_PORT:-50080}; else exec sleep infinity; fi'"`
- **Errors Count:** 0
- **Package Version:** `9860 (fdb1db877c)`
- **Metrics:**
  - Avg Time/Run:         55.98 s
  - Avg Throughput:       812.08 tokens/sec
  - Avg Chunk Latency:    629.0 ms
  - Avg Chunk p50:        627.1 ms
  - Avg Chunk p95:        636.9 ms

### VULKAN-COMBI-VULKAN1 Configuration Details

- **Device Name**: `AMD Radeon RX 7900 XTX` (Total: 24560 MiB, Free: 24560 MiB)

#### Text Chat (`local-chat`)
- **Benchmark Test Name:** `chat_vulkan-combi-Vulkan1`
- **Device Setting:** `Vulkan1`
- **Special Setting:** `Layers: 999`
- **Model:** `qwen3` (`Qwen3.6-35B-A3B-APEX-I-Compact`)
- **Execution Target:** `VULKAN-COMBI-VULKAN1`
- **GPU Memory Used:** 19026.4 MB
- **CPU Memory Used:** 65.7 MB
- **Benchmark Running Time:** 24.43 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `GGML_VK_DISABLE_MMVQ="1"`
  - `HIP_VISIBLE_DEVICES=""`
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
  - `LCHAT_N_CTX="240384"`
  - `LCHAT_N_GPU_LAYERS="999"`
  - `LCHAT_PARALLEL="3"`
  - `LCHAT_PORT="50080"`
  - `LCHAT_SERVE_EMBEDDINGS="true"`
  - `LCHAT_SPECULATIVE="--spec-type ngram-simple --spec-ngram-simple-size-n 6 --spec-ngram-simple-size-m 4"`
  - `LCHAT_THREADS="4"`
  - `LMBD_ALIAS="qwen3-embedding"`
  - `LMBD_CACHE_TYPE_K="q8_0"`
  - `LMBD_CACHE_TYPE_V="q8_0"`
  - `LMBD_CTX_SIZE="8192"`
  - `LMBD_DEVICE="Vulkan1"`
  - `LMBD_ENABLED="true"`
  - `LMBD_EXTRA_ARGS="--flash-attn on"`
  - `LMBD_MIRROR_PORT="50082"`
  - `LMBD_MODEL="/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf"`
  - `LMBD_N_CTX="4096"`
  - `LMBD_N_GPU_LAYERS="999"`
  - `LMBD_PARALLEL="2"`
  - `LMBD_UBATCH_SIZE="512"`
  - `LOCAL_SIDECARS="portmirror"`
  - `LOCAL_SIDECAR_PORTMIRROR_CMD="bash -c 'if [ \"\${LMBD_ENABLED}\" = \"true\" ]; then exec socat TCP-LISTEN:\${LMBD_MIRROR_PORT:-50082},fork,reuseaddr TCP:\${LCHAT_HOST:-127.0.0.1}:\${LCHAT_PORT:-50080}; else exec sleep infinity; fi'"`
- **Errors Count:** 0
- **Package Version:** `9860 (fdb1db877c)`
- **Warmup (Phase 0):**
  - TTFT (Prefill):       143.14 ms
  - Prefill Speed:        132.74 tokens/sec
  - Generation Speed:     132.22 tokens/sec
- **Generation (Phase 2):**
  - Avg Completion Tokens: 600.0
  - Avg TTFT (Prefill):   17753.22 ms
  - Avg Prefill Speed:    1748.47 tokens/sec
  - Avg Generation Speed: 116.78 tokens/sec
  - Avg Decode Time:      5.14 s
- **Vision Description (Phase 4):**
  - Avg TTFT (Prefill):   0.00 ms
  - Avg Generation Speed: 0.00 tokens/sec

#### Text Embedding (`local-embedding`)
- **Benchmark Test Name:** `embedding_vulkan-combi-Vulkan1`
- **Device Setting:** `Vulkan1`
- **Special Setting:** `Layers: 999`
- **Model:** `qwen3-embedding` (`Qwen3-Embedding-0.6B-Q8_0.gguf`)
- **Execution Target:** `VULKAN-COMBI-VULKAN1`
- **GPU Memory Used:** 20446.5 MB
- **CPU Memory Used:** 68.6 MB
- **Benchmark Running Time:** 8.82 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `GGML_VK_DISABLE_MMVQ="1"`
  - `HIP_VISIBLE_DEVICES=""`
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
  - `LCHAT_N_CTX="240384"`
  - `LCHAT_N_GPU_LAYERS="999"`
  - `LCHAT_PARALLEL="3"`
  - `LCHAT_PORT="50080"`
  - `LCHAT_SERVE_EMBEDDINGS="true"`
  - `LCHAT_SPECULATIVE="--spec-type ngram-simple --spec-ngram-simple-size-n 6 --spec-ngram-simple-size-m 4"`
  - `LCHAT_THREADS="4"`
  - `LMBD_ALIAS="qwen3-embedding"`
  - `LMBD_CACHE_TYPE_K="q8_0"`
  - `LMBD_CACHE_TYPE_V="q8_0"`
  - `LMBD_CTX_SIZE="8192"`
  - `LMBD_DEVICE="Vulkan1"`
  - `LMBD_ENABLED="true"`
  - `LMBD_EXTRA_ARGS="--flash-attn on"`
  - `LMBD_MIRROR_PORT="50082"`
  - `LMBD_MODEL="/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf"`
  - `LMBD_N_CTX="4096"`
  - `LMBD_N_GPU_LAYERS="999"`
  - `LMBD_PARALLEL="2"`
  - `LMBD_UBATCH_SIZE="512"`
  - `LOCAL_SIDECARS="portmirror"`
  - `LOCAL_SIDECAR_PORTMIRROR_CMD="bash -c 'if [ \"\${LMBD_ENABLED}\" = \"true\" ]; then exec socat TCP-LISTEN:\${LMBD_MIRROR_PORT:-50082},fork,reuseaddr TCP:\${LCHAT_HOST:-127.0.0.1}:\${LCHAT_PORT:-50080}; else exec sleep infinity; fi'"`
- **Errors Count:** 0
- **Package Version:** `9860 (fdb1db877c)`
- **Metrics:**
  - Avg Time/Run:         8.56 s
  - Avg Throughput:       5307.90 tokens/sec
  - Avg Chunk Latency:    96.2 ms
  - Avg Chunk p50:        95.1 ms
  - Avg Chunk p95:        96.4 ms

### VULKAN-VULKAN0 Configuration Details

- **Device Name**: `AMD Radeon Graphics` (Total: 16384 MiB, Free: 16384 MiB)

#### Text Chat (`local-chat`)
- **Benchmark Test Name:** `chat_vulkan-Vulkan0`
- **Device Setting:** `Vulkan0`
- **Special Setting:** `Layers: 999 (Context: 20%)`
- **Model:** `qwen3` (`Qwen3.6-35B-A3B-APEX-I-Compact`)
- **Execution Target:** `VULKAN-VULKAN0`
- **GPU Memory Used:** 13927.8 MB
- **CPU Memory Used:** 65.3 MB
- **Benchmark Running Time:** 131.79 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `GGML_VK_DISABLE_MMVQ="1"`
  - `HIP_VISIBLE_DEVICES=""`
  - `LCHAT_ALIAS="qwen3"`
  - `LCHAT_CACHE_TYPE_K="q4_0"`
  - `LCHAT_CACHE_TYPE_V="q4_0"`
  - `LCHAT_CHAT_TEMPLATE_FILE="/data/public/machine-learning/models/vision-text/Qwen3.6-chat_template.jinja"`
  - `LCHAT_CTX_SIZE="240384"`
  - `LCHAT_DEVICE="Vulkan0"`
  - `LCHAT_EMBEDDING_ENABLED="false"`
  - `LCHAT_EXTRA_ARGS=""`
  - `LCHAT_HOST="127.0.0.1"`
  - `LCHAT_MMPROJ="/data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact-mmproj.gguf"`
  - `LCHAT_MODEL="/data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact.gguf"`
  - `LCHAT_N_CTX="48076"`
  - `LCHAT_N_GPU_LAYERS="999"`
  - `LCHAT_PARALLEL="3"`
  - `LCHAT_PORT="50080"`
  - `LCHAT_SERVE_EMBEDDINGS="false"`
  - `LCHAT_SPECULATIVE="--spec-type ngram-simple --spec-ngram-simple-size-n 6 --spec-ngram-simple-size-m 4"`
  - `LCHAT_THREADS="4"`
  - `LMBD_ALIAS="qwen3-embedding"`
  - `LMBD_CACHE_TYPE_K="q8_0"`
  - `LMBD_CACHE_TYPE_V="q8_0"`
  - `LMBD_CTX_SIZE="8192"`
  - `LMBD_ENABLED="false"`
  - `LMBD_EXTRA_ARGS="--flash-attn on"`
  - `LMBD_MIRROR_PORT="50082"`
  - `LMBD_MODEL="/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf"`
  - `LMBD_PARALLEL="2"`
  - `LMBD_UBATCH_SIZE="512"`
  - `LOCAL_SIDECARS="portmirror"`
  - `LOCAL_SIDECAR_PORTMIRROR_CMD="bash -c 'if [ \"\${LMBD_ENABLED}\" = \"true\" ]; then exec socat TCP-LISTEN:\${LMBD_MIRROR_PORT:-50082},fork,reuseaddr TCP:\${LCHAT_HOST:-127.0.0.1}:\${LCHAT_PORT:-50080}; else exec sleep infinity; fi'"`
- **Errors Count:** 0
- **Package Version:** `9860 (fdb1db877c)`
- **Warmup (Phase 0):**
  - TTFT (Prefill):       1796.20 ms
  - Prefill Speed:        10.58 tokens/sec
  - Generation Speed:     13.56 tokens/sec
- **Generation (Phase 2):**
  - Avg Completion Tokens: 600.0
  - Avg TTFT (Prefill):   69407.87 ms
  - Avg Prefill Speed:    83.79 tokens/sec
  - Avg Generation Speed: 12.58 tokens/sec
  - Avg Decode Time:      47.70 s
- **Vision Description (Phase 4):**
  - Avg TTFT (Prefill):   0.00 ms
  - Avg Generation Speed: 0.00 tokens/sec

#### Text Embedding (`local-embedding`)
- **Benchmark Test Name:** `embedding_vulkan-Vulkan0`
- **Device Setting:** `Vulkan0`
- **Special Setting:** `Layers: 999`
- **Model:** `qwen3-embedding` (`Qwen3-Embedding-0.6B-Q8_0.gguf`)
- **Execution Target:** `VULKAN-VULKAN0`
- **GPU Memory Used:** 1390.2 MB
- **CPU Memory Used:** 3011.1 MB
- **Benchmark Running Time:** 70.00 s
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
- **Package Version:** `9860 (fdb1db877c)`
- **Metrics:**
  - Avg Time/Run:         69.74 s
  - Avg Throughput:       651.82 tokens/sec
  - Avg Chunk Latency:    783.6 ms
  - Avg Chunk p50:        785.4 ms
  - Avg Chunk p95:        790.2 ms

#### Document Reranking (`local-rerank`)
- **Benchmark Test Name:** `rerank_vulkan-Vulkan0`
- **Device Setting:** `Vulkan0`
- **Special Setting:** `Layers: 99`
- **Model:** `qwen3-reranker` (`Qwen3-Reranker-0.6B.Q4_K_M.gguf`)
- **Execution Target:** `VULKAN-VULKAN0`
- **GPU Memory Used:** 1593.9 MB
- **CPU Memory Used:** 263.1 MB
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
- **Package Version:** `9860 (fdb1db877c)`
- **Metrics:**
  - Avg Reranking Time:   5112.79 ms
  - Avg Docs Throughput:  1.96 docs/sec
  - Avg Token Speed:      672.63 tokens/sec

#### Speech-to-Text (STT) (`local-speech-to-text`)
- **Benchmark Test Name:** `stt_vulkan-Vulkan0`
- **Device Setting:** `0`
- **Special Setting:** `Use GPU`
- **Model:** `whisper-1` (`ggml-large-v3-turbo-q5_0.bin`)
- **Execution Target:** `VULKAN-VULKAN0`
- **GPU Memory Used:** 802.2 MB
- **CPU Memory Used:** 126.1 MB
- **Benchmark Running Time:** 5.71 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LSTT_DEVICE="0"`
  - `LSTT_EXTRA_ARGS=""`
  - `LSTT_HOST="127.0.0.1"`
  - `LSTT_INFERENCE_PATH="/v1/audio/transcriptions"`
  - `LSTT_MODEL="/data/public/machine-learning/models/speech-to-text/ggml-large-v3-turbo-q5_0.bin"`
  - `LSTT_ALIAS="whisper-1"`
  - `LSTT_NO_GPU="false"`
  - `LSTT_PORT="50090"`
  - `LSTT_THREADS="8"`
- **Errors Count:** 0
- **Package Version:** `1.9.1 (6fc7c33b4)`
- **Metrics:**
  - Avg Transcribe Time:  5.57 seconds
  - Avg Real-Time Factor (RTF): 0.1238 (8.1x faster than real-time)

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Benchmark Test Name:** `tts_vulkan-Vulkan0`
- **Device Setting:** `Vulkan0`
- **Special Setting:** `mode: gpu`
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `VULKAN-VULKAN0`
- **GPU Memory Used:** 3552.1 MB
- **CPU Memory Used:** 787.7 MB
- **Benchmark Running Time:** 55.08 s
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
- **Errors Count:** 0
- **Package Version:** `qwen3-tts version 0.1-main-0c8b2ba`
- **Metrics:**
  - Generated Audio Duration: 22.46 seconds
  - Avg Synthesis Time:   54.94 seconds
  - Avg Real-Time Factor (RTF): 2.4465
  - Avg Speed:            4.99 chars/sec

#### Image Generation (`local-image`)
- **Benchmark Test Name:** `image_vulkan-Vulkan0`
- **Device Setting:** `vulkan0,te=cpu`
- **Special Setting:** `Steps: 8`
- **Model:** `z_image_turbo-Q8_0` (`z_image_turbo-Q8_0.gguf`)
- **Execution Target:** `VULKAN-VULKAN0`
- **GPU Memory Used:** 6354.1 MB
- **CPU Memory Used:** 3804.6 MB
- **Benchmark Running Time:** 92.93 s
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
- **Package Version:** `master-746-2574f59, commit 2574f593`
- **Metrics:**
  - Avg Generation Time:  92.76 seconds

### VULKAN-VULKAN1 Configuration Details

- **Device Name**: `AMD Radeon RX 7900 XTX` (Total: 24560 MiB, Free: 24560 MiB)

#### Text Chat (`local-chat`)
- **Benchmark Test Name:** `chat_vulkan-Vulkan1`
- **Device Setting:** `Vulkan1`
- **Special Setting:** `Layers: 999`
- **Model:** `qwen3` (`Qwen3.6-35B-A3B-APEX-I-Compact`)
- **Execution Target:** `VULKAN-VULKAN1`
- **GPU Memory Used:** 19026.4 MB
- **CPU Memory Used:** 65.8 MB
- **Benchmark Running Time:** 24.53 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `GGML_VK_DISABLE_MMVQ="1"`
  - `HIP_VISIBLE_DEVICES=""`
  - `LCHAT_ALIAS="qwen3"`
  - `LCHAT_CACHE_TYPE_K="q4_0"`
  - `LCHAT_CACHE_TYPE_V="q4_0"`
  - `LCHAT_CHAT_TEMPLATE_FILE="/data/public/machine-learning/models/vision-text/Qwen3.6-chat_template.jinja"`
  - `LCHAT_CTX_SIZE="240384"`
  - `LCHAT_DEVICE="Vulkan1"`
  - `LCHAT_EMBEDDING_ENABLED="false"`
  - `LCHAT_EXTRA_ARGS=""`
  - `LCHAT_HOST="127.0.0.1"`
  - `LCHAT_MMPROJ="/data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact-mmproj.gguf"`
  - `LCHAT_MODEL="/data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact.gguf"`
  - `LCHAT_N_CTX="240384"`
  - `LCHAT_N_GPU_LAYERS="999"`
  - `LCHAT_PARALLEL="3"`
  - `LCHAT_PORT="50080"`
  - `LCHAT_SERVE_EMBEDDINGS="false"`
  - `LCHAT_SPECULATIVE="--spec-type ngram-simple --spec-ngram-simple-size-n 6 --spec-ngram-simple-size-m 4"`
  - `LCHAT_THREADS="4"`
  - `LMBD_ALIAS="qwen3-embedding"`
  - `LMBD_CACHE_TYPE_K="q8_0"`
  - `LMBD_CACHE_TYPE_V="q8_0"`
  - `LMBD_CTX_SIZE="8192"`
  - `LMBD_ENABLED="false"`
  - `LMBD_EXTRA_ARGS="--flash-attn on"`
  - `LMBD_MIRROR_PORT="50082"`
  - `LMBD_MODEL="/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf"`
  - `LMBD_PARALLEL="2"`
  - `LMBD_UBATCH_SIZE="512"`
  - `LOCAL_SIDECARS="portmirror"`
  - `LOCAL_SIDECAR_PORTMIRROR_CMD="bash -c 'if [ \"\${LMBD_ENABLED}\" = \"true\" ]; then exec socat TCP-LISTEN:\${LMBD_MIRROR_PORT:-50082},fork,reuseaddr TCP:\${LCHAT_HOST:-127.0.0.1}:\${LCHAT_PORT:-50080}; else exec sleep infinity; fi'"`
- **Errors Count:** 0
- **Package Version:** `9860 (fdb1db877c)`
- **Warmup (Phase 0):**
  - TTFT (Prefill):       159.42 ms
  - Prefill Speed:        119.18 tokens/sec
  - Generation Speed:     132.02 tokens/sec
- **Generation (Phase 2):**
  - Avg Completion Tokens: 600.0
  - Avg TTFT (Prefill):   17850.39 ms
  - Avg Prefill Speed:    1738.95 tokens/sec
  - Avg Generation Speed: 116.13 tokens/sec
  - Avg Decode Time:      5.17 s
- **Vision Description (Phase 4):**
  - Avg TTFT (Prefill):   0.00 ms
  - Avg Generation Speed: 0.00 tokens/sec

#### Text Embedding (`local-embedding`)
- **Benchmark Test Name:** `embedding_vulkan-Vulkan1`
- **Device Setting:** `Vulkan1`
- **Special Setting:** `Layers: 999`
- **Model:** `qwen3-embedding` (`Qwen3-Embedding-0.6B-Q8_0.gguf`)
- **Execution Target:** `VULKAN-VULKAN1`
- **GPU Memory Used:** 1180.3 MB
- **CPU Memory Used:** 2917.0 MB
- **Benchmark Running Time:** 8.82 s
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
- **Package Version:** `9860 (fdb1db877c)`
- **Metrics:**
  - Avg Time/Run:         8.54 s
  - Avg Throughput:       5325.07 tokens/sec
  - Avg Chunk Latency:    95.9 ms
  - Avg Chunk p50:        94.8 ms
  - Avg Chunk p95:        96.2 ms

#### Document Reranking (`local-rerank`)
- **Benchmark Test Name:** `rerank_vulkan-Vulkan1`
- **Device Setting:** `Vulkan1`
- **Special Setting:** `Layers: 99`
- **Model:** `qwen3-reranker` (`Qwen3-Reranker-0.6B.Q4_K_M.gguf`)
- **Execution Target:** `VULKAN-VULKAN1`
- **GPU Memory Used:** 1597.7 MB
- **CPU Memory Used:** 265.8 MB
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
- **Package Version:** `9860 (fdb1db877c)`
- **Metrics:**
  - Avg Reranking Time:   875.32 ms
  - Avg Docs Throughput:  11.42 docs/sec
  - Avg Token Speed:      3928.84 tokens/sec

#### Speech-to-Text (STT) (`local-speech-to-text`)
- **Benchmark Test Name:** `stt_vulkan-Vulkan1`
- **Device Setting:** `1`
- **Special Setting:** `Use GPU`
- **Model:** `whisper-1` (`ggml-large-v3-turbo-q5_0.bin`)
- **Execution Target:** `VULKAN-VULKAN1`
- **GPU Memory Used:** 839.8 MB
- **CPU Memory Used:** 150.2 MB
- **Benchmark Running Time:** 1.10 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LSTT_DEVICE="1"`
  - `LSTT_EXTRA_ARGS=""`
  - `LSTT_HOST="127.0.0.1"`
  - `LSTT_INFERENCE_PATH="/v1/audio/transcriptions"`
  - `LSTT_MODEL="/data/public/machine-learning/models/speech-to-text/ggml-large-v3-turbo-q5_0.bin"`
  - `LSTT_ALIAS="whisper-1"`
  - `LSTT_NO_GPU="false"`
  - `LSTT_PORT="50090"`
  - `LSTT_THREADS="8"`
- **Errors Count:** 0
- **Package Version:** `1.9.1 (6fc7c33b4)`
- **Metrics:**
  - Avg Transcribe Time:  0.88 seconds
  - Avg Real-Time Factor (RTF): 0.0195 (51.4x faster than real-time)

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Benchmark Test Name:** `tts_vulkan-Vulkan1`
- **Device Setting:** `Vulkan1`
- **Special Setting:** `mode: gpu`
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `VULKAN-VULKAN1`
- **GPU Memory Used:** 3393.2 MB
- **CPU Memory Used:** 729.0 MB
- **Benchmark Running Time:** 7.11 s
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
  - `Warning: TTS Audio validation failed (garbled audio output)`
- **Package Version:** `qwen3-tts version 0.1-main-0c8b2ba`
- **Metrics:**
  - Generated Audio Duration: -fail- VALIDATION
  - Avg Synthesis Time:   -fail- VALIDATION
  - Avg Real-Time Factor (RTF): 0.3457
  - Avg Speed:            39.52 chars/sec

#### Image Generation (`local-image`)
- **Benchmark Test Name:** `image_vulkan-Vulkan1`
- **Device Setting:** `vulkan1`
- **Special Setting:** `Steps: 8`
- **Model:** `z_image_turbo-Q8_0` (`z_image_turbo-Q8_0.gguf`)
- **Execution Target:** `VULKAN-VULKAN1`
- **GPU Memory Used:** 9892.4 MB
- **CPU Memory Used:** 510.0 MB
- **Benchmark Running Time:** 7.13 s
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
- **Package Version:** `master-746-2574f59, commit 2574f593`
- **Metrics:**
  - Avg Generation Time:  6.96 seconds

### CPU Configuration Details

#### Text Chat (`local-chat`)
- **Benchmark Test Name:** `chat_cpu`
- **Device Setting:** `none`
- **Special Setting:** `Layers: 0 (Context: 5%)`
- **Model:** `qwen3` (`Qwen3.6-35B-A3B-APEX-I-Compact`)
- **Execution Target:** `CPU`
- **GPU Memory Used:** 1109.2 MB
- **CPU Memory Used:** 65.2 MB
- **Benchmark Running Time:** 95.50 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `GGML_VK_DISABLE_MMVQ="1"`
  - `HIP_VISIBLE_DEVICES=""`
  - `LCHAT_ALIAS="qwen3"`
  - `LCHAT_CACHE_TYPE_K="q4_0"`
  - `LCHAT_CACHE_TYPE_V="q4_0"`
  - `LCHAT_CHAT_TEMPLATE_FILE="/data/public/machine-learning/models/vision-text/Qwen3.6-chat_template.jinja"`
  - `LCHAT_CTX_SIZE="240384"`
  - `LCHAT_DEVICE="none"`
  - `LCHAT_EMBEDDING_ENABLED="false"`
  - `LCHAT_EXTRA_ARGS=""`
  - `LCHAT_HOST="127.0.0.1"`
  - `LCHAT_MMPROJ="/data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact-mmproj.gguf"`
  - `LCHAT_MODEL="/data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact.gguf"`
  - `LCHAT_N_CTX="12019"`
  - `LCHAT_N_GPU_LAYERS="0"`
  - `LCHAT_PARALLEL="3"`
  - `LCHAT_PORT="50080"`
  - `LCHAT_SERVE_EMBEDDINGS="false"`
  - `LCHAT_SPECULATIVE="--spec-type ngram-simple --spec-ngram-simple-size-n 6 --spec-ngram-simple-size-m 4"`
  - `LCHAT_THREADS="4"`
  - `LMBD_ALIAS="qwen3-embedding"`
  - `LMBD_CACHE_TYPE_K="q8_0"`
  - `LMBD_CACHE_TYPE_V="q8_0"`
  - `LMBD_CTX_SIZE="8192"`
  - `LMBD_ENABLED="false"`
  - `LMBD_EXTRA_ARGS="--flash-attn on"`
  - `LMBD_MIRROR_PORT="50082"`
  - `LMBD_MODEL="/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf"`
  - `LMBD_PARALLEL="2"`
  - `LMBD_UBATCH_SIZE="512"`
  - `LOCAL_SIDECARS="portmirror"`
  - `LOCAL_SIDECAR_PORTMIRROR_CMD="bash -c 'if [ \"\${LMBD_ENABLED}\" = \"true\" ]; then exec socat TCP-LISTEN:\${LMBD_MIRROR_PORT:-50082},fork,reuseaddr TCP:\${LCHAT_HOST:-127.0.0.1}:\${LCHAT_PORT:-50080}; else exec sleep infinity; fi'"`
- **Errors Count:** 0
- **Package Version:** `9860 (fdb1db877c)`
- **Warmup (Phase 0):**
  - TTFT (Prefill):       700.68 ms
  - Prefill Speed:        27.12 tokens/sec
  - Generation Speed:     13.21 tokens/sec
- **Generation (Phase 2):**
  - Avg Completion Tokens: 600.0
  - Avg TTFT (Prefill):   33334.50 ms
  - Avg Prefill Speed:    44.19 tokens/sec
  - Avg Generation Speed: 12.55 tokens/sec
  - Avg Decode Time:      47.79 s
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
- **CPU Memory Used:** 2641.9 MB
- **Benchmark Running Time:** 22.79 s
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
- **Package Version:** `9860 (fdb1db877c)`
- **Metrics:**
  - Avg Time/Run:         224.54 s
  - Avg Throughput:       182.42 tokens/sec
  - Avg Chunk Latency:    2806.7 ms
  - Avg Chunk p50:        2797.7 ms
  - Avg Chunk p95:        3035.6 ms

#### Document Reranking (`local-rerank`)
- **Benchmark Test Name:** `rerank_cpu`
- **Device Setting:** `none`
- **Special Setting:** `Layers: 0`
- **Model:** `qwen3-reranker` (`Qwen3-Reranker-0.6B.Q4_K_M.gguf`)
- **Execution Target:** `CPU`
- **GPU Memory Used:** 0.1 MB
- **CPU Memory Used:** 2707.8 MB
- **Benchmark Running Time:** 10.23 s
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
- **Package Version:** `9860 (fdb1db877c)`
- **Metrics:**
  - Avg Reranking Time:   10044.38 ms
  - Avg Docs Throughput:  1.00 docs/sec
  - Avg Token Speed:      342.38 tokens/sec

#### Speech-to-Text (STT) (`local-speech-to-text`)
- **Benchmark Test Name:** `stt_cpu`
- **Device Setting:** `none`
- **Special Setting:** `No GPU`
- **Model:** `whisper-1` (`ggml-large-v3-turbo-q5_0.bin`)
- **Execution Target:** `CPU`
- **GPU Memory Used:** 0.1 MB
- **CPU Memory Used:** 1099.2 MB
- **Benchmark Running Time:** 12.35 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LSTT_DEVICE=""`
  - `LSTT_EXTRA_ARGS=""`
  - `LSTT_HOST="127.0.0.1"`
  - `LSTT_INFERENCE_PATH="/v1/audio/transcriptions"`
  - `LSTT_MODEL="/data/public/machine-learning/models/speech-to-text/ggml-large-v3-turbo-q5_0.bin"`
  - `LSTT_ALIAS="whisper-1"`
  - `LSTT_NO_GPU="true"`
  - `LSTT_PORT="50090"`
  - `LSTT_THREADS="8"`
- **Errors Count:** 0
- **Package Version:** `1.9.1 (6fc7c33b4)`
- **Metrics:**
  - Avg Transcribe Time:  12.14 seconds
  - Avg Real-Time Factor (RTF): 0.2698 (3.7x faster than real-time)

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Benchmark Test Name:** `tts_cpu`
- **Device Setting:** `none`
- **Special Setting:** `mode: cpu`
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `CPU`
- **GPU Memory Used:** 0.1 MB
- **CPU Memory Used:** 2998.5 MB
- **Benchmark Running Time:** 30.17 s
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
  - `Warning: TTS Audio validation failed (garbled audio output)`
- **Package Version:** `qwen3-tts version 0.1-main-0c8b2ba`
- **Metrics:**
  - Generated Audio Duration: -fail- VALIDATION
  - Avg Synthesis Time:   -fail- VALIDATION
  - Avg Real-Time Factor (RTF): 1.5229
  - Avg Speed:            9.12 chars/sec

#### Image Generation (`local-image`)
- **Benchmark Test Name:** `image_cpu`
- **Device Setting:** `cpu`
- **Special Setting:** `Steps: 8`
- **Model:** `z_image_turbo-Q8_0` (`z_image_turbo-Q8_0.gguf`)
- **Execution Target:** `CPU`
- **GPU Memory Used:** 0.1 MB
- **CPU Memory Used:** 10132.8 MB
- **Benchmark Running Time:** 282.76 s
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
- **Package Version:** `master-746-2574f59, commit 2574f593`
- **Metrics:**
  - Avg Generation Time:  282.65 seconds

### CPU-COMBI Configuration Details

#### Text Chat (`local-chat`)
- **Benchmark Test Name:** `chat_cpu-combi`
- **Device Setting:** `none`
- **Special Setting:** `Layers: 0 (Context: 5%)`
- **Model:** `qwen3` (`Qwen3.6-35B-A3B-APEX-I-Compact`)
- **Execution Target:** `CPU-COMBI`
- **GPU Memory Used:** 1109.2 MB
- **CPU Memory Used:** 65.2 MB
- **Benchmark Running Time:** 100.82 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `GGML_VK_DISABLE_MMVQ="1"`
  - `HIP_VISIBLE_DEVICES=""`
  - `LCHAT_ALIAS="qwen3"`
  - `LCHAT_CACHE_TYPE_K="q4_0"`
  - `LCHAT_CACHE_TYPE_V="q4_0"`
  - `LCHAT_CHAT_TEMPLATE_FILE="/data/public/machine-learning/models/vision-text/Qwen3.6-chat_template.jinja"`
  - `LCHAT_CTX_SIZE="240384"`
  - `LCHAT_DEVICE="none"`
  - `LCHAT_EMBEDDING_ENABLED="true"`
  - `LCHAT_EXTRA_ARGS=""`
  - `LCHAT_HOST="127.0.0.1"`
  - `LCHAT_MMPROJ="/data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact-mmproj.gguf"`
  - `LCHAT_MODEL="/data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact.gguf"`
  - `LCHAT_N_CTX="12019"`
  - `LCHAT_N_GPU_LAYERS="0"`
  - `LCHAT_PARALLEL="3"`
  - `LCHAT_PORT="50080"`
  - `LCHAT_SERVE_EMBEDDINGS="true"`
  - `LCHAT_SPECULATIVE="--spec-type ngram-simple --spec-ngram-simple-size-n 6 --spec-ngram-simple-size-m 4"`
  - `LCHAT_THREADS="4"`
  - `LMBD_ALIAS="qwen3-embedding"`
  - `LMBD_CACHE_TYPE_K="q8_0"`
  - `LMBD_CACHE_TYPE_V="q8_0"`
  - `LMBD_CTX_SIZE="8192"`
  - `LMBD_DEVICE="none"`
  - `LMBD_ENABLED="true"`
  - `LMBD_EXTRA_ARGS="--flash-attn on"`
  - `LMBD_MIRROR_PORT="50082"`
  - `LMBD_MODEL="/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf"`
  - `LMBD_N_CTX="8192"`
  - `LMBD_N_GPU_LAYERS="0"`
  - `LMBD_PARALLEL="2"`
  - `LMBD_UBATCH_SIZE="512"`
  - `LOCAL_SIDECARS="portmirror"`
  - `LOCAL_SIDECAR_PORTMIRROR_CMD="bash -c 'if [ \"\${LMBD_ENABLED}\" = \"true\" ]; then exec socat TCP-LISTEN:\${LMBD_MIRROR_PORT:-50082},fork,reuseaddr TCP:\${LCHAT_HOST:-127.0.0.1}:\${LCHAT_PORT:-50080}; else exec sleep infinity; fi'"`
- **Errors Count:** 0
- **Package Version:** `9860 (fdb1db877c)`
- **Warmup (Phase 0):**
  - TTFT (Prefill):       859.65 ms
  - Prefill Speed:        22.10 tokens/sec
  - Generation Speed:     12.88 tokens/sec
- **Generation (Phase 2):**
  - Avg Completion Tokens: 600.0
  - Avg TTFT (Prefill):   36199.37 ms
  - Avg Prefill Speed:    40.69 tokens/sec
  - Avg Generation Speed: 12.07 tokens/sec
  - Avg Decode Time:      49.71 s
- **Vision Description (Phase 4):**
  - Avg TTFT (Prefill):   0.00 ms
  - Avg Generation Speed: 0.00 tokens/sec

#### Text Embedding (`local-embedding`)
- **Benchmark Test Name:** `embedding_cpu-combi`
- **Device Setting:** `none`
- **Special Setting:** `Layers: 999`
- **Model:** `qwen3-embedding` (`Qwen3-Embedding-0.6B-Q8_0.gguf`)
- **Execution Target:** `CPU-COMBI`
- **GPU Memory Used:** 1109.3 MB
- **CPU Memory Used:** 67.9 MB
- **Benchmark Running Time:** 35.32 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `GGML_VK_DISABLE_MMVQ="1"`
  - `HIP_VISIBLE_DEVICES=""`
  - `LCHAT_ALIAS="qwen3"`
  - `LCHAT_CACHE_TYPE_K="q4_0"`
  - `LCHAT_CACHE_TYPE_V="q4_0"`
  - `LCHAT_CHAT_TEMPLATE_FILE="/data/public/machine-learning/models/vision-text/Qwen3.6-chat_template.jinja"`
  - `LCHAT_CTX_SIZE="240384"`
  - `LCHAT_DEVICE="none"`
  - `LCHAT_EMBEDDING_ENABLED="true"`
  - `LCHAT_EXTRA_ARGS=""`
  - `LCHAT_HOST="127.0.0.1"`
  - `LCHAT_MMPROJ="/data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact-mmproj.gguf"`
  - `LCHAT_MODEL="/data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact.gguf"`
  - `LCHAT_N_CTX="12019"`
  - `LCHAT_N_GPU_LAYERS="0"`
  - `LCHAT_PARALLEL="3"`
  - `LCHAT_PORT="50080"`
  - `LCHAT_SERVE_EMBEDDINGS="true"`
  - `LCHAT_SPECULATIVE="--spec-type ngram-simple --spec-ngram-simple-size-n 6 --spec-ngram-simple-size-m 4"`
  - `LCHAT_THREADS="4"`
  - `LMBD_ALIAS="qwen3-embedding"`
  - `LMBD_CACHE_TYPE_K="q8_0"`
  - `LMBD_CACHE_TYPE_V="q8_0"`
  - `LMBD_CTX_SIZE="8192"`
  - `LMBD_DEVICE="none"`
  - `LMBD_ENABLED="true"`
  - `LMBD_EXTRA_ARGS="--flash-attn on"`
  - `LMBD_MIRROR_PORT="50082"`
  - `LMBD_MODEL="/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf"`
  - `LMBD_N_CTX="8192"`
  - `LMBD_N_GPU_LAYERS="0"`
  - `LMBD_PARALLEL="2"`
  - `LMBD_UBATCH_SIZE="512"`
  - `LOCAL_SIDECARS="portmirror"`
  - `LOCAL_SIDECAR_PORTMIRROR_CMD="bash -c 'if [ \"\${LMBD_ENABLED}\" = \"true\" ]; then exec socat TCP-LISTEN:\${LMBD_MIRROR_PORT:-50082},fork,reuseaddr TCP:\${LCHAT_HOST:-127.0.0.1}:\${LCHAT_PORT:-50080}; else exec sleep infinity; fi'"`
- **Errors Count:** 0
- **Package Version:** `9860 (fdb1db877c)`
- **Metrics:**
  - Avg Time/Run:         348.21 s
  - Avg Throughput:       117.63 tokens/sec
  - Avg Chunk Latency:    4352.6 ms
  - Avg Chunk p50:        4367.4 ms
  - Avg Chunk p95:        4556.1 ms

### CPU-BLAS Configuration Details

#### Text Chat (`local-chat`)
- **Benchmark Test Name:** `chat_cpu-blas`
- **Device Setting:** `BLAS`
- **Special Setting:** `Layers: 0 (Context: 5%)`
- **Model:** `qwen3` (`Qwen3.6-35B-A3B-APEX-I-Compact`)
- **Execution Target:** `CPU-BLAS`
- **GPU Memory Used:** 1109.2 MB
- **CPU Memory Used:** 64.9 MB
- **Benchmark Running Time:** 101.40 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `GGML_VK_DISABLE_MMVQ="1"`
  - `HIP_VISIBLE_DEVICES=""`
  - `LCHAT_ALIAS="qwen3"`
  - `LCHAT_CACHE_TYPE_K="q4_0"`
  - `LCHAT_CACHE_TYPE_V="q4_0"`
  - `LCHAT_CHAT_TEMPLATE_FILE="/data/public/machine-learning/models/vision-text/Qwen3.6-chat_template.jinja"`
  - `LCHAT_CTX_SIZE="240384"`
  - `LCHAT_DEVICE="BLAS"`
  - `LCHAT_EMBEDDING_ENABLED="false"`
  - `LCHAT_EXTRA_ARGS=""`
  - `LCHAT_HOST="127.0.0.1"`
  - `LCHAT_MMPROJ="/data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact-mmproj.gguf"`
  - `LCHAT_MODEL="/data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact.gguf"`
  - `LCHAT_N_CTX="12019"`
  - `LCHAT_N_GPU_LAYERS="0"`
  - `LCHAT_PARALLEL="3"`
  - `LCHAT_PORT="50080"`
  - `LCHAT_SERVE_EMBEDDINGS="false"`
  - `LCHAT_SPECULATIVE="--spec-type ngram-simple --spec-ngram-simple-size-n 6 --spec-ngram-simple-size-m 4"`
  - `LCHAT_THREADS="4"`
  - `LMBD_ALIAS="qwen3-embedding"`
  - `LMBD_CACHE_TYPE_K="q8_0"`
  - `LMBD_CACHE_TYPE_V="q8_0"`
  - `LMBD_CTX_SIZE="8192"`
  - `LMBD_ENABLED="false"`
  - `LMBD_EXTRA_ARGS="--flash-attn on"`
  - `LMBD_MIRROR_PORT="50082"`
  - `LMBD_MODEL="/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf"`
  - `LMBD_PARALLEL="2"`
  - `LMBD_UBATCH_SIZE="512"`
  - `LOCAL_SIDECARS="portmirror"`
  - `LOCAL_SIDECAR_PORTMIRROR_CMD="bash -c 'if [ \"\${LMBD_ENABLED}\" = \"true\" ]; then exec socat TCP-LISTEN:\${LMBD_MIRROR_PORT:-50082},fork,reuseaddr TCP:\${LCHAT_HOST:-127.0.0.1}:\${LCHAT_PORT:-50080}; else exec sleep infinity; fi'"`
- **Errors Count:** 0
- **Package Version:** `9860 (fdb1db877c)`
- **Warmup (Phase 0):**
  - TTFT (Prefill):       856.16 ms
  - Prefill Speed:        22.19 tokens/sec
  - Generation Speed:     12.98 tokens/sec
- **Generation (Phase 2):**
  - Avg Completion Tokens: 600.0
  - Avg TTFT (Prefill):   36565.32 ms
  - Avg Prefill Speed:    40.28 tokens/sec
  - Avg Generation Speed: 11.99 tokens/sec
  - Avg Decode Time:      50.04 s
- **Vision Description (Phase 4):**
  - Avg TTFT (Prefill):   0.00 ms
  - Avg Generation Speed: 0.00 tokens/sec

#### Text Embedding (`local-embedding`)
- **Benchmark Test Name:** `embedding_cpu-blas`
- **Device Setting:** `BLAS`
- **Special Setting:** `Layers: 999`
- **Model:** `qwen3-embedding` (`Qwen3-Embedding-0.6B-Q8_0.gguf`)
- **Execution Target:** `CPU-BLAS`
- **GPU Memory Used:** 0.1 MB
- **CPU Memory Used:** 2642.0 MB
- **Benchmark Running Time:** 34.45 s
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
- **Package Version:** `9860 (fdb1db877c)`
- **Metrics:**
  - Avg Time/Run:         339.50 s
  - Avg Throughput:       120.65 tokens/sec
  - Avg Chunk Latency:    4243.7 ms
  - Avg Chunk p50:        4239.6 ms
  - Avg Chunk p95:        4521.6 ms

#### Document Reranking (`local-rerank`)
- **Benchmark Test Name:** `rerank_cpu-blas`
- **Device Setting:** `BLAS`
- **Special Setting:** `Layers: 99`
- **Model:** `qwen3-reranker` (`Qwen3-Reranker-0.6B.Q4_K_M.gguf`)
- **Execution Target:** `CPU-BLAS`
- **GPU Memory Used:** 0.1 MB
- **CPU Memory Used:** 2708.7 MB
- **Benchmark Running Time:** 14.24 s
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
- **Package Version:** `9860 (fdb1db877c)`
- **Metrics:**
  - Avg Reranking Time:   14062.26 ms
  - Avg Docs Throughput:  0.71 docs/sec
  - Avg Token Speed:      244.56 tokens/sec

#### Speech-to-Text (STT) (`local-speech-to-text`)
- **Benchmark Test Name:** `stt_cpu-blas`
- **Device Setting:** `BLAS`
- **Special Setting:** `No GPU`
- **Model:** `whisper-1` (`ggml-large-v3-turbo-q5_0.bin`)
- **Execution Target:** `CPU-BLAS`
- **GPU Memory Used:** 0.1 MB
- **CPU Memory Used:** 1097.6 MB
- **Benchmark Running Time:** 17.17 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LSTT_DEVICE=""`
  - `LSTT_EXTRA_ARGS=""`
  - `LSTT_HOST="127.0.0.1"`
  - `LSTT_INFERENCE_PATH="/v1/audio/transcriptions"`
  - `LSTT_MODEL="/data/public/machine-learning/models/speech-to-text/ggml-large-v3-turbo-q5_0.bin"`
  - `LSTT_ALIAS="whisper-1"`
  - `LSTT_NO_GPU="true"`
  - `LSTT_PORT="50090"`
  - `LSTT_THREADS="8"`
- **Errors Count:** 0
- **Package Version:** `1.9.1 (6fc7c33b4)`
- **Metrics:**
  - Avg Transcribe Time:  16.94 seconds
  - Avg Real-Time Factor (RTF): 0.3765 (2.7x faster than real-time)

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Benchmark Test Name:** `tts_cpu-blas`
- **Device Setting:** `BLAS`
- **Special Setting:** `mode: cpu`
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `CPU-BLAS`
- **GPU Memory Used:** 0.1 MB
- **CPU Memory Used:** 2997.6 MB
- **Benchmark Running Time:** 30.78 s
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
- **Package Version:** `qwen3-tts version 0.1-main-0c8b2ba`
- **Metrics:**
  - Generated Audio Duration: 18.86 seconds
  - Avg Synthesis Time:   30.63 seconds
  - Avg Real-Time Factor (RTF): 1.6242
  - Avg Speed:            8.95 chars/sec

#### Image Generation (`local-image`)
- **Benchmark Test Name:** `image_cpu-blas`
- **Device Setting:** `cpu`
- **Special Setting:** `Steps: 8`
- **Model:** `z_image_turbo-Q8_0` (`z_image_turbo-Q8_0.gguf`)
- **Execution Target:** `CPU-BLAS`
- **GPU Memory Used:** 0.1 MB
- **CPU Memory Used:** 10131.6 MB
- **Benchmark Running Time:** 282.06 s
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
- **Package Version:** `master-746-2574f59, commit 2574f593`
- **Metrics:**
  - Avg Generation Time:  281.93 seconds

### CPU-BLAS-COMBI Configuration Details

#### Text Chat (`local-chat`)
- **Benchmark Test Name:** `chat_cpu-blas-combi`
- **Device Setting:** `BLAS`
- **Special Setting:** `Layers: 0 (Context: 5%)`
- **Model:** `qwen3` (`Qwen3.6-35B-A3B-APEX-I-Compact`)
- **Execution Target:** `CPU-BLAS-COMBI`
- **GPU Memory Used:** 1109.2 MB
- **CPU Memory Used:** 64.7 MB
- **Benchmark Running Time:** 101.22 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `GGML_VK_DISABLE_MMVQ="1"`
  - `HIP_VISIBLE_DEVICES=""`
  - `LCHAT_ALIAS="qwen3"`
  - `LCHAT_CACHE_TYPE_K="q4_0"`
  - `LCHAT_CACHE_TYPE_V="q4_0"`
  - `LCHAT_CHAT_TEMPLATE_FILE="/data/public/machine-learning/models/vision-text/Qwen3.6-chat_template.jinja"`
  - `LCHAT_CTX_SIZE="240384"`
  - `LCHAT_DEVICE="BLAS"`
  - `LCHAT_EMBEDDING_ENABLED="true"`
  - `LCHAT_EXTRA_ARGS=""`
  - `LCHAT_HOST="127.0.0.1"`
  - `LCHAT_MMPROJ="/data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact-mmproj.gguf"`
  - `LCHAT_MODEL="/data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact.gguf"`
  - `LCHAT_N_CTX="12019"`
  - `LCHAT_N_GPU_LAYERS="0"`
  - `LCHAT_PARALLEL="3"`
  - `LCHAT_PORT="50080"`
  - `LCHAT_SERVE_EMBEDDINGS="true"`
  - `LCHAT_SPECULATIVE="--spec-type ngram-simple --spec-ngram-simple-size-n 6 --spec-ngram-simple-size-m 4"`
  - `LCHAT_THREADS="4"`
  - `LMBD_ALIAS="qwen3-embedding"`
  - `LMBD_CACHE_TYPE_K="q8_0"`
  - `LMBD_CACHE_TYPE_V="q8_0"`
  - `LMBD_CTX_SIZE="8192"`
  - `LMBD_DEVICE="BLAS"`
  - `LMBD_ENABLED="true"`
  - `LMBD_EXTRA_ARGS="--flash-attn on"`
  - `LMBD_MIRROR_PORT="50082"`
  - `LMBD_MODEL="/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf"`
  - `LMBD_N_CTX="8192"`
  - `LMBD_N_GPU_LAYERS="0"`
  - `LMBD_PARALLEL="2"`
  - `LMBD_UBATCH_SIZE="512"`
  - `LOCAL_SIDECARS="portmirror"`
  - `LOCAL_SIDECAR_PORTMIRROR_CMD="bash -c 'if [ \"\${LMBD_ENABLED}\" = \"true\" ]; then exec socat TCP-LISTEN:\${LMBD_MIRROR_PORT:-50082},fork,reuseaddr TCP:\${LCHAT_HOST:-127.0.0.1}:\${LCHAT_PORT:-50080}; else exec sleep infinity; fi'"`
- **Errors Count:** 0
- **Package Version:** `9860 (fdb1db877c)`
- **Warmup (Phase 0):**
  - TTFT (Prefill):       879.28 ms
  - Prefill Speed:        21.61 tokens/sec
  - Generation Speed:     12.86 tokens/sec
- **Generation (Phase 2):**
  - Avg Completion Tokens: 600.0
  - Avg TTFT (Prefill):   36080.19 ms
  - Avg Prefill Speed:    40.83 tokens/sec
  - Avg Generation Speed: 11.95 tokens/sec
  - Avg Decode Time:      50.19 s
- **Vision Description (Phase 4):**
  - Avg TTFT (Prefill):   0.00 ms
  - Avg Generation Speed: 0.00 tokens/sec

#### Text Embedding (`local-embedding`)
- **Benchmark Test Name:** `embedding_cpu-blas-combi`
- **Device Setting:** `BLAS`
- **Special Setting:** `Layers: 999`
- **Model:** `qwen3-embedding` (`Qwen3-Embedding-0.6B-Q8_0.gguf`)
- **Execution Target:** `CPU-BLAS-COMBI`
- **GPU Memory Used:** 1109.3 MB
- **CPU Memory Used:** 67.6 MB
- **Benchmark Running Time:** 34.42 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `GGML_VK_DISABLE_MMVQ="1"`
  - `HIP_VISIBLE_DEVICES=""`
  - `LCHAT_ALIAS="qwen3"`
  - `LCHAT_CACHE_TYPE_K="q4_0"`
  - `LCHAT_CACHE_TYPE_V="q4_0"`
  - `LCHAT_CHAT_TEMPLATE_FILE="/data/public/machine-learning/models/vision-text/Qwen3.6-chat_template.jinja"`
  - `LCHAT_CTX_SIZE="240384"`
  - `LCHAT_DEVICE="BLAS"`
  - `LCHAT_EMBEDDING_ENABLED="true"`
  - `LCHAT_EXTRA_ARGS=""`
  - `LCHAT_HOST="127.0.0.1"`
  - `LCHAT_MMPROJ="/data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact-mmproj.gguf"`
  - `LCHAT_MODEL="/data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact.gguf"`
  - `LCHAT_N_CTX="12019"`
  - `LCHAT_N_GPU_LAYERS="0"`
  - `LCHAT_PARALLEL="3"`
  - `LCHAT_PORT="50080"`
  - `LCHAT_SERVE_EMBEDDINGS="true"`
  - `LCHAT_SPECULATIVE="--spec-type ngram-simple --spec-ngram-simple-size-n 6 --spec-ngram-simple-size-m 4"`
  - `LCHAT_THREADS="4"`
  - `LMBD_ALIAS="qwen3-embedding"`
  - `LMBD_CACHE_TYPE_K="q8_0"`
  - `LMBD_CACHE_TYPE_V="q8_0"`
  - `LMBD_CTX_SIZE="8192"`
  - `LMBD_DEVICE="BLAS"`
  - `LMBD_ENABLED="true"`
  - `LMBD_EXTRA_ARGS="--flash-attn on"`
  - `LMBD_MIRROR_PORT="50082"`
  - `LMBD_MODEL="/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf"`
  - `LMBD_N_CTX="8192"`
  - `LMBD_N_GPU_LAYERS="0"`
  - `LMBD_PARALLEL="2"`
  - `LMBD_UBATCH_SIZE="512"`
  - `LOCAL_SIDECARS="portmirror"`
  - `LOCAL_SIDECAR_PORTMIRROR_CMD="bash -c 'if [ \"\${LMBD_ENABLED}\" = \"true\" ]; then exec socat TCP-LISTEN:\${LMBD_MIRROR_PORT:-50082},fork,reuseaddr TCP:\${LCHAT_HOST:-127.0.0.1}:\${LCHAT_PORT:-50080}; else exec sleep infinity; fi'"`
- **Errors Count:** 0
- **Package Version:** `9860 (fdb1db877c)`
- **Metrics:**
  - Avg Time/Run:         338.89 s
  - Avg Throughput:       120.86 tokens/sec
  - Avg Chunk Latency:    4236.1 ms
  - Avg Chunk p50:        4167.1 ms
  - Avg Chunk p95:        4489.1 ms

### SPECIAL (CPU-HIP-ROCM0) Configuration Details

- **Device Name**: `AMD Radeon RX 7900 XTX` (Total: 24560 MiB, Free: 24560 MiB)

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Benchmark Test Name:** `tts_cpu-hip-ROCm0`
- **Device Setting:** `ROCm0`
- **Special Setting:** `mode: hybrid`
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `SPECIAL (CPU-HIP-ROCM0)`
- **GPU Memory Used:** 3717.9 MB
- **CPU Memory Used:** 1161.0 MB
- **Benchmark Running Time:** 19.33 s
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
- **Errors Count:** 0
- **Package Version:** `qwen3-tts version 0.1-main-0c8b2ba`
- **Metrics:**
  - Generated Audio Duration: 20.38 seconds
  - Avg Synthesis Time:   19.18 seconds
  - Avg Real-Time Factor (RTF): 0.9413
  - Avg Speed:            14.29 chars/sec

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
- **Package Version:** `qwen3-tts version 0.1-main-0c8b2ba`
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
- **GPU Memory Used:** 3378.7 MB
- **CPU Memory Used:** 696.9 MB
- **Benchmark Running Time:** 50.28 s
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
- **Package Version:** `qwen3-tts version 0.1-main-0c8b2ba`
- **Metrics:**
  - Generated Audio Duration: 20.46 seconds
  - Avg Synthesis Time:   50.09 seconds
  - Avg Real-Time Factor (RTF): 2.4487
  - Avg Speed:            5.47 chars/sec

### SPECIAL (CPU-VULKAN-VULKAN1) Configuration Details

- **Device Name**: `AMD Radeon RX 7900 XTX` (Total: 24560 MiB, Free: 24560 MiB)

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Benchmark Test Name:** `tts_cpu-vulkan-Vulkan1`
- **Device Setting:** `Vulkan1`
- **Special Setting:** `mode: hybrid`
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `SPECIAL (CPU-VULKAN-VULKAN1)`
- **GPU Memory Used:** 3354.3 MB
- **CPU Memory Used:** 677.4 MB
- **Benchmark Running Time:** 6.71 s
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
- **Package Version:** `qwen3-tts version 0.1-main-0c8b2ba`
- **Metrics:**
  - Generated Audio Duration: 19.58 seconds
  - Avg Synthesis Time:   6.60 seconds
  - Avg Real-Time Factor (RTF): 0.3371
  - Avg Speed:            41.52 chars/sec

### SPECIAL-COMBI Configuration Details

#### Text Chat (`local-chat`)
- **Benchmark Test Name:** `chat_special-combi`
- **Device Setting:** `special`
- **Special Setting:** `Layers: 999`
- **Model:** `qwen3` (`Qwen3.6-35B-A3B-APEX-I-Compact`)
- **Execution Target:** `SPECIAL-COMBI`
- **GPU Memory Used:** -fail-
- **CPU Memory Used:** -fail-
- **Benchmark Running Time:** -fail-
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `GGML_VK_DISABLE_MMVQ="1"`
  - `HIP_VISIBLE_DEVICES=""`
  - `LCHAT_ALIAS="qwen3"`
  - `LCHAT_CACHE_TYPE_K="q4_0"`
  - `LCHAT_CACHE_TYPE_V="q4_0"`
  - `LCHAT_CHAT_TEMPLATE_FILE="/data/public/machine-learning/models/vision-text/Qwen3.6-chat_template.jinja"`
  - `LCHAT_CTX_SIZE="240384"`
  - `LCHAT_DEVICE="special"`
  - `LCHAT_EMBEDDING_ENABLED="true"`
  - `LCHAT_EXTRA_ARGS=""`
  - `LCHAT_HOST="127.0.0.1"`
  - `LCHAT_MMPROJ="/data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact-mmproj.gguf"`
  - `LCHAT_MODEL="/data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact.gguf"`
  - `LCHAT_N_CTX="240384"`
  - `LCHAT_N_GPU_LAYERS="999"`
  - `LCHAT_PARALLEL="3"`
  - `LCHAT_PORT="50080"`
  - `LCHAT_SERVE_EMBEDDINGS="true"`
  - `LCHAT_SPECULATIVE="--spec-type ngram-simple --spec-ngram-simple-size-n 6 --spec-ngram-simple-size-m 4"`
  - `LCHAT_THREADS="4"`
  - `LMBD_ALIAS="qwen3-embedding"`
  - `LMBD_CACHE_TYPE_K="q8_0"`
  - `LMBD_CACHE_TYPE_V="q8_0"`
  - `LMBD_CTX_SIZE="8192"`
  - `LMBD_DEVICE="special"`
  - `LMBD_ENABLED="true"`
  - `LMBD_EXTRA_ARGS="--flash-attn on"`
  - `LMBD_MIRROR_PORT="50082"`
  - `LMBD_MODEL="/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf"`
  - `LMBD_N_CTX="8192"`
  - `LMBD_N_GPU_LAYERS="999"`
  - `LMBD_PARALLEL="2"`
  - `LMBD_UBATCH_SIZE="512"`
  - `LOCAL_SIDECARS="portmirror"`
  - `LOCAL_SIDECAR_PORTMIRROR_CMD="bash -c 'if [ \"\${LMBD_ENABLED}\" = \"true\" ]; then exec socat TCP-LISTEN:\${LMBD_MIRROR_PORT:-50082},fork,reuseaddr TCP:\${LCHAT_HOST:-127.0.0.1}:\${LCHAT_PORT:-50080}; else exec sleep infinity; fi'"`
- **Errors Count:** 1
- **Top Errors:**
  - `Error: llama-server failed to start or port timed out`
- **Package Version:** `9860 (fdb1db877c)`
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
- **Vision Description (Phase 4):**
  - Avg TTFT (Prefill):   -n.a.-
  - Avg Generation Speed: -n.a.-

### RUNNING Configuration Details

#### Text Chat (`local-chat`)
- **Benchmark Test Name:** `chat_running`
- **Device Setting:** `running on host`
- **Special Setting:** `unknown`
- **Model:** `qwen3` (`Qwen3.6-35B-A3B-APEX-I-Compact`)
- **Execution Target:** `RUNNING`
- **GPU Memory Used:** -n.a.-
- **CPU Memory Used:** -n.a.-
- **Benchmark Running Time:** 24.23 s
- **Active Environment Settings:**
  - `GGML_VK_DISABLE_MMVQ="1"`
  - `LCHAT_ALIAS="qwen3"`
  - `LCHAT_CACHE_TYPE_K="q4_0"`
  - `LCHAT_CACHE_TYPE_V="q4_0"`
  - `LCHAT_CHAT_TEMPLATE_FILE="/data/public/machine-learning/models/vision-text/Qwen3.6-chat_template.jinja"`
  - `LCHAT_CTX_SIZE="240384"`
  - `LCHAT_DEVICE="Vulkan1"`
  - `LCHAT_EMBEDDING_ENABLED="false"`
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
  - `LOCAL_SIDECARS=""`
  - `LOCAL_SIDECAR_PORTMIRROR_CMD="bash -c 'if [ \"\${LMBD_ENABLED}\" = \"true\" ]; then exec socat TCP-LISTEN:\${LMBD_MIRROR_PORT:-50082},fork,reuseaddr TCP:\${LCHAT_HOST:-127.0.0.1}:\${LCHAT_PORT:-50080}; else exec sleep infinity; fi'"`
- **Errors Count:** 0
- **Package Version:** `9860 (fdb1db877c)`
- **Warmup (Phase 0):**
  - TTFT (Prefill):       118.68 ms
  - Prefill Speed:        160.09 tokens/sec
  - Generation Speed:     129.71 tokens/sec
- **Generation (Phase 2):**
  - Avg Completion Tokens: 600.0
  - Avg TTFT (Prefill):   17614.25 ms
  - Avg Prefill Speed:    1762.27 tokens/sec
  - Avg Generation Speed: 114.08 tokens/sec
  - Avg Decode Time:      5.26 s
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
- **Benchmark Running Time:** 9.51 s
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
- **Package Version:** `9860 (fdb1db877c)`
- **Metrics:**
  - Avg Time/Run:         9.32 s
  - Avg Throughput:       4877.78 tokens/sec
  - Avg Chunk Latency:    104.7 ms
  - Avg Chunk p50:        103.5 ms
  - Avg Chunk p95:        104.4 ms

#### Document Reranking (`local-rerank`)
- **Benchmark Test Name:** `rerank_running`
- **Device Setting:** `running on host`
- **Special Setting:** `unknown`
- **Model:** `qwen3-reranker` (`Qwen3-Reranker-0.6B.Q4_K_M.gguf`)
- **Execution Target:** `RUNNING`
- **GPU Memory Used:** -n.a.-
- **CPU Memory Used:** -n.a.-
- **Benchmark Running Time:** 14.84 s
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
- **Package Version:** `9860 (fdb1db877c)`
- **Metrics:**
  - Avg Reranking Time:   14651.89 ms
  - Avg Docs Throughput:  0.68 docs/sec
  - Avg Token Speed:      234.71 tokens/sec

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
  - `LSTT_ALIAS="whisper-1"`
  - `LSTT_PORT="50090"`
  - `LSTT_THREADS="8"`
- **Errors Count:** 0
- **Package Version:** `1.9.1 (6fc7c33b4)`
- **Metrics:**
  - Avg Transcribe Time:  5.59 seconds
  - Avg Real-Time Factor (RTF): 0.1243 (8.0x faster than real-time)

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Benchmark Test Name:** `tts_running`
- **Device Setting:** `running on host`
- **Special Setting:** `unknown`
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `RUNNING`
- **GPU Memory Used:** -n.a.-
- **CPU Memory Used:** -n.a.-
- **Benchmark Running Time:** 34.77 s
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
- **Package Version:** `qwen3-tts version 0.1-main-0c8b2ba`
- **Metrics:**
  - Generated Audio Duration: 18.06 seconds
  - Avg Synthesis Time:   34.63 seconds
  - Avg Real-Time Factor (RTF): 1.9178
  - Avg Speed:            7.91 chars/sec

#### Image Generation (`local-image`)
- **Benchmark Test Name:** `image_running`
- **Device Setting:** `running on host`
- **Special Setting:** `unknown`
- **Model:** `z_image_turbo-Q8_0` (`z_image_turbo-Q8_0.gguf`)
- **Execution Target:** `RUNNING`
- **GPU Memory Used:** -n.a.-
- **CPU Memory Used:** -n.a.-
- **Benchmark Running Time:** 89.53 s
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
- **Package Version:** `master-746-2574f59, commit 2574f593`
- **Metrics:**
  - Avg Generation Time:  89.35 seconds

