# LLM Caching Optimization Benchmarks

**Benchmark Run Time:** `2026-07-28 03:25:59`

## Local Inference Services Benchmarks

We ran local benchmarks for text embedding, text-to-speech (TTS), speech-to-text (STT), document reranking, and image generation on the AMD Radeon RX 7900 XTX hardware target. All services run inside isolated sandboxed environments.

### 📊 Performance Comparison Matrix

#### Text Chat (`local-chat`)
| Configuration | Test Name | GPU | Special Setting | Avg Chat TTFT | Avg Chat Prefill | Chat TTFT (Warmup) | Chat Gen Speed | Avg Chat Gen | Chat Image TTFT | Chat Image Gen | Chat GPU Mem | Chat CPU Mem |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| [**HIP-COMBI-ROCM0**](#hip-combi-rocm0-configuration-details) | chat_hip-combi-ROCm0 | ROCm0 | Layers: 999 | 55195.27 ms | 562.39 t/s | 255.74 ms | 101.32 t/s | 66.77 t/s | 0.00 ms | 0.00 t/s | 20346.8 MB | 81.4 MB |
| [**HIP-ROCM0**](#hip-rocm0-configuration-details) | chat_hip-ROCm0 | ROCm0 | Layers: 999 | 18026.50 ms | 1722.74 t/s | 116.27 ms | 89.26 t/s | 63.88 t/s | 0.00 ms | 0.00 t/s | 18872.9 MB | 79.8 MB |
| [**VULKAN-VULKAN0**](#vulkan-vulkan0-configuration-details) | chat_vulkan-Vulkan0 | Vulkan0 | Layers: 999 (Context: 20%) | 72105.11 ms | 80.85 t/s | 1657.46 ms | 15.69 t/s | 12.22 t/s | 0.00 ms | 0.00 t/s | 14416.1 MB | 63.4 MB |
| [**VULKAN-VULKAN1**](#vulkan-vulkan1-configuration-details) | chat_vulkan-Vulkan1 | Vulkan1 | Layers: 999 | 17804.84 ms | 1744.19 t/s | 142.95 ms | 141.65 t/s | **107.04 t/s** | 0.00 ms | 0.00 t/s | 17894.6 MB | 63.8 MB |
| [**CPU**](#cpu-configuration-details) | chat_cpu | none | Layers: 0 (Context: 5%) | 41745.44 ms | 35.62 t/s | 576.59 ms | 16.04 t/s | 12.01 t/s | 0.00 ms | 0.00 t/s | 0.1 MB | 63.1 MB |
| [**CPU-BLAS**](#cpu-blas-configuration-details) | chat_cpu-blas | BLAS | Layers: 0 (Context: 5%) | 41882.37 ms | 35.50 t/s | 582.41 ms | 16.89 t/s | 12.00 t/s | 0.00 ms | 0.00 t/s | 0.1 MB | 63.4 MB |
| [**RUNNING**](#running-configuration-details) | chat_running | running on host | unknown | 17578.88 ms | **1766.61 t/s** | 73.19 ms | 146.58 t/s | 106.95 t/s | 0.00 ms | 0.00 t/s | -n.a.- | -n.a.- |

#### Text Embedding (`local-embedding`)
| Configuration | Test Name | GPU | Special Setting | Embedding Throughput | Embedding Latency (Avg) | Embedding GPU Mem | Embedding CPU Mem |
|---|---|---|---|---|---|---|---|
| [**HIP-COMBI-ROCM0**](#hip-combi-rocm0-configuration-details) | embedding_hip-combi-ROCm0 | ROCm0 | Layers: 999 | 5851.93 t/s | 87.3 ms | 22324.3 MB | 84.3 MB |
| [**HIP-ROCM0**](#hip-rocm0-configuration-details) | embedding_hip-ROCm0 | ROCm0 | Layers: 999 | **10858.97 t/s** | 47.0 ms | 2181.6 MB | 895.2 MB |
| [**VULKAN-VULKAN0**](#vulkan-vulkan0-configuration-details) | embedding_vulkan-Vulkan0 | Vulkan0 | Layers: 999 | 850.22 t/s | 600.8 ms | 1692.5 MB | 294.1 MB |
| [**VULKAN-VULKAN1**](#vulkan-vulkan1-configuration-details) | embedding_vulkan-Vulkan1 | Vulkan1 | Layers: 999 | 6098.09 t/s | 83.8 ms | 1483.9 MB | 297.0 MB |
| [**CPU**](#cpu-configuration-details) | embedding_cpu | none | Layers: 0 | 140.20 t/s | 3651.9 ms | 0.0 MB | 2438.5 MB |
| [**CPU-BLAS**](#cpu-blas-configuration-details) | embedding_cpu-blas | BLAS | Layers: 999 | 140.58 t/s | 3642.1 ms | 0.1 MB | 2438.7 MB |
| [**RUNNING**](#running-configuration-details) | embedding_running | running on host | unknown | 9024.01 t/s | 56.6 ms | -n.a.- | -n.a.- |

#### Document Reranking (`local-rerank`)
| Configuration | Test Name | GPU | Special Setting | Avg Reranking Time | Avg Token Speed | Avg Docs Throughput | GPU Mem | CPU Mem |
|---|---|---|---|---|---|---|---|---|
| [**HIP-ROCM0**](#hip-rocm0-configuration-details) | rerank_hip-ROCm0 | ROCm0 | Layers: 99 | 612.47 ms | **5614.95 tokens/s** | 16.33 docs/s | 13264.1 MB | 1858.9 MB |
| [**VULKAN-VULKAN0**](#vulkan-vulkan0-configuration-details) | rerank_vulkan-Vulkan0 | Vulkan0 | Layers: 99 | 6278.25 ms | 547.76 tokens/s | 1.59 docs/s | 3510.8 MB | 412.6 MB |
| [**VULKAN-VULKAN1**](#vulkan-vulkan1-configuration-details) | rerank_vulkan-Vulkan1 | Vulkan1 | Layers: 99 | 861.75 ms | 3990.73 tokens/s | 11.60 docs/s | 3544.6 MB | 417.7 MB |
| [**CPU**](#cpu-configuration-details) | rerank_cpu | none | Layers: 0 | 15104.88 ms | 227.67 tokens/s | 0.66 docs/s | 0.1 MB | 4281.0 MB |
| [**CPU-BLAS**](#cpu-blas-configuration-details) | rerank_cpu-blas | BLAS | Layers: 99 | 14795.03 ms | 232.44 tokens/s | 0.68 docs/s | 0.1 MB | 4280.8 MB |
| [**RUNNING**](#running-configuration-details) | rerank_running | running on host | unknown | 6339.59 ms | 542.46 tokens/s | 1.58 docs/s | -n.a.- | -n.a.- |

#### Speech-to-Text (STT) (`local-speech-to-text`)
| Configuration | Test Name | GPU | Special Setting | Avg Transcribe Time | Avg Real-Time Factor (RTF) | Speedup vs Real-time | GPU Mem | CPU Mem |
|---|---|---|---|---|---|---|---|---|
| [**HIP-ROCM0**](#hip-rocm0-configuration-details) | stt_hip-ROCm0 | 0 | Use GPU | -fail- VALIDATION | -fail- VALIDATION | -fail- VALIDATION | 1264.4 MB | 485.9 MB |
| [**VULKAN-VULKAN0**](#vulkan-vulkan0-configuration-details) | stt_vulkan-Vulkan0 | 0 | Use GPU | 5.57 s | 0.1238 | 8.1x | 802.2 MB | 126.1 MB |
| [**VULKAN-VULKAN1**](#vulkan-vulkan1-configuration-details) | stt_vulkan-Vulkan1 | 1 | Use GPU | 0.88 s | 0.0195 | **51.4x** | 839.8 MB | 150.2 MB |
| [**CPU**](#cpu-configuration-details) | stt_cpu | none | No GPU | 12.14 s | 0.2698 | 3.7x | 0.1 MB | 1099.2 MB |
| [**CPU-BLAS**](#cpu-blas-configuration-details) | stt_cpu-blas | BLAS | No GPU | 16.94 s | 0.3765 | 2.7x | 0.1 MB | 1097.6 MB |
| [**RUNNING**](#running-configuration-details) | stt_running | running on host | unknown | 7.77 s | 0.1726 | 5.8x | -n.a.- | -n.a.- |

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
| [**RUNNING**](#running-configuration-details) | tts_running | running on host | unknown | 38.69 s | 1.9365 | 7.08 chars/s | -n.a.- | -n.a.- |

#### Image Generation (`local-image`)
| Configuration | Test Name | GPU | Special Setting | Avg Generation Time | GPU Mem | CPU Mem |
|---|---|---|---|---|---|---|
| [**HIP-ROCM0**](#hip-rocm0-configuration-details) | image_hip-ROCm0 | rocm0 | Steps: 8 | 7.43 s | 10758.5 MB | 862.6 MB |
| [**VULKAN-VULKAN0**](#vulkan-vulkan0-configuration-details) | image_vulkan-Vulkan0 | vulkan0,te=cpu | Steps: 8 | 92.76 s | 6354.1 MB | 3804.6 MB |
| [**VULKAN-VULKAN1**](#vulkan-vulkan1-configuration-details) | image_vulkan-Vulkan1 | vulkan1 | Steps: 8 | **6.96 s** | 9892.4 MB | 510.0 MB |
| [**CPU**](#cpu-configuration-details) | image_cpu | cpu | Steps: 8 | 282.65 s | 0.1 MB | 10132.8 MB |
| [**CPU-BLAS**](#cpu-blas-configuration-details) | image_cpu-blas | cpu | Steps: 8 | 281.93 s | 0.1 MB | 10131.6 MB |
| [**RUNNING**](#running-configuration-details) | image_running | running on host | unknown | 90.16 s | -n.a.- | -n.a.- |

#### Code Completion FIM (`local-chat` - tab completion)
| Configuration | Test Name | GPU | Special Setting | Avg Completion TTFT | Avg Prefill Speed | Warmup TTFT | Avg Generation Speed | GPU Mem | CPU Mem |
|---|---|---|---|---|---|---|---|---|---|
| [**HIP-ROCM0**](#hip-rocm0-configuration-details) | completion_hip-ROCm0 | ROCm0 | Layers: 999 | 116.36 ms | 34648.08 t/s | 29.02 ms | 210.22 t/s | 1916.3 MB | 76.2 MB |
| [**VULKAN-VULKAN0**](#vulkan-vulkan0-configuration-details) | completion_vulkan-Vulkan0 | Vulkan0 | Layers: 999 | 128.04 ms | 15479.29 t/s | 26.35 ms | 248.12 t/s | 1944.2 MB | 59.4 MB |
| [**VULKAN-VULKAN1**](#vulkan-vulkan1-configuration-details) | completion_vulkan-Vulkan1 | Vulkan1 | Layers: 999 | 70.71 ms | 37891.66 t/s | 15.30 ms | **252.04 t/s** | 1121.8 MB | 65.7 MB |
| [**CPU**](#cpu-configuration-details) | completion_cpu | none | Layers: 0 | 13769.06 ms | 79.89 t/s | 37.61 ms | 30.68 t/s | 46.5 MB | 64.1 MB |
| [**CPU-BLAS**](#cpu-blas-configuration-details) | completion_cpu-blas | BLAS | Layers: 0 | 13717.94 ms | 80.19 t/s | 37.54 ms | 30.64 t/s | 46.5 MB | 64.0 MB |

---

### ⚙️ Detailed Configuration Reports

### HIP-COMBI-ROCM0 Configuration Details

- **Device Name**: `AMD Radeon RX 7900 XTX` (Total: 24560 MiB, Free: 24560 MiB)

#### Text Chat (`local-chat`)
- **Benchmark Test Name:** `chat_hip-combi-ROCm0`
- **Device Setting:** `ROCm0`
- **Special Setting:** `Layers: 999`
- **Model:** `qwen3` (`Agents-A1-APEX-I-Compact`)
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
  - `LCHAT_MMPROJ="/data/public/machine-learning/models/vision-text/Agents-A1-APEX-I-Compact-mmproj.gguf"`
  - `LCHAT_MODEL="/data/public/machine-learning/models/vision-text/Agents-A1-APEX-I-Compact.gguf"`
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
- **Package Version:** `10154 (0e4a036223)`
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
  - `LCHAT_MMPROJ="/data/public/machine-learning/models/vision-text/Agents-A1-APEX-I-Compact-mmproj.gguf"`
  - `LCHAT_MODEL="/data/public/machine-learning/models/vision-text/Agents-A1-APEX-I-Compact.gguf"`
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
- **Package Version:** `10154 (0e4a036223)`
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
- **Model:** `qwen3` (`Agents-A1-APEX-I-Compact`)
- **Execution Target:** `HIP-ROCM0`
- **GPU Memory Used:** 18872.9 MB
- **CPU Memory Used:** 79.8 MB
- **Benchmark Running Time:** 34.35 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES="0"`
  - `GGML_VK_DISABLE_MMVQ="1"`
  - `HIP_VISIBLE_DEVICES="0"`
  - `LCHAT_ALIAS="qwen3"`
  - `LCHAT_CACHE_TYPE_K="q4_0"`
  - `LCHAT_CACHE_TYPE_V="q4_0"`
  - `LCHAT_CHAT_TEMPLATE_FILE="/data/public/machine-learning/models/vision-text/Qwen3.6-chat_template.jinja"`
  - `LCHAT_CHAT_TEMPLATE_KWARGS="{"enable_thinking": false}"`
  - `LCHAT_CTX_SIZE="240384"`
  - `LCHAT_DEVICE="ROCm0"`
  - `LCHAT_EMBEDDING_ENABLED="false"`
  - `LCHAT_EXTRA_ARGS="--temp 0.6 --top-k 20 --repeat-penalty 1.1"`
  - `LCHAT_HOST="127.0.0.1"`
  - `LCHAT_MMPROJ=""`
  - `LCHAT_MODEL="/data/public/machine-learning/models/vision-text/Agents-A1-APEX-I-Compact.gguf"`
  - `LCHAT_MTP=""`
  - `LCHAT_N_CTX="240384"`
  - `LCHAT_N_GPU_LAYERS="999"`
  - `LCHAT_PARALLEL="2"`
  - `LCHAT_PORT="50080"`
  - `LCHAT_SERVE_EMBEDDINGS="false"`
  - `LCHAT_SIDECARS=""`
  - `LCHAT_SIDECAR_PORTMIRROR_CMD="bash -c 'if [ \"\${LMBD_ENABLED}\" = \"true\" ]; then exec socat TCP-LISTEN:\${LMBD_MIRROR_PORT:-50082},fork,reuseaddr TCP:\${LCHAT_HOST:-127.0.0.1}:\${LCHAT_PORT:-50080}; else exec sleep infinity; fi'"`
  - `LCHAT_SPECULATIVE="--spec-type ngram-simple --spec-ngram-simple-size-n 6 --spec-ngram-simple-size-m 4"`
  - `LCHAT_THREADS="4"`
  - `LCOMP_ALIAS="qwen-coder-fim"`
  - `LCOMP_CACHE_TYPE_K="q4_0"`
  - `LCOMP_CACHE_TYPE_V="q4_0"`
  - `LCOMP_CTX_SIZE="8192"`
  - `LCOMP_ENABLED="false"`
  - `LCOMP_EXTRA_ARGS=""`
  - `LCOMP_MODEL="/data/public/machine-learning/models/completion/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf"`
  - `LCOMP_PARALLEL="2"`
  - `LMBD_ALIAS="qwen3-embedding"`
  - `LMBD_CACHE_TYPE_K="q8_0"`
  - `LMBD_CACHE_TYPE_V="q8_0"`
  - `LMBD_CTX_SIZE="16384"`
  - `LMBD_ENABLED="false"`
  - `LMBD_EXTRA_ARGS="--flash-attn on"`
  - `LMBD_MIRROR_PORT="50082"`
  - `LMBD_MODEL="/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf"`
  - `LMBD_PARALLEL="2"`
  - `LMBD_UBATCH_SIZE="16384"`
- **Errors Count:** 1
- **Top Errors:**
  - `[34m0.31.724.982[0m [31mE srv    operator(): http client error: Connection handling canceled`
- **Package Version:** `10154 (0e4a036223)`
- **Warmup (Phase 0):**
  - TTFT (Prefill):       116.27 ms
  - Prefill Speed:        180.61 tokens/sec
  - Generation Speed:     89.26 tokens/sec
- **Generation (Phase 2):**
  - Avg Completion Tokens: 1024.0
  - Avg TTFT (Prefill):   18026.50 ms
  - Avg Prefill Speed:    1722.74 tokens/sec
  - Avg Generation Speed: 63.88 tokens/sec
  - Avg Decode Time:      16.03 s
- **Vision Description (Phase 4):**
  - Avg TTFT (Prefill):   0.00 ms
  - Avg Generation Speed: 0.00 tokens/sec

#### Text Embedding (`local-embedding`)
- **Benchmark Test Name:** `embedding_hip-ROCm0`
- **Device Setting:** `ROCm0`
- **Special Setting:** `Layers: 999`
- **Model:** `qwen3-embedding` (`Qwen3-Embedding-0.6B-Q8_0.gguf`)
- **Execution Target:** `HIP-ROCM0`
- **GPU Memory Used:** 2181.6 MB
- **CPU Memory Used:** 895.2 MB
- **Benchmark Running Time:** 4.41 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES="0"`
  - `HIP_VISIBLE_DEVICES="0"`
  - `LMBD_ALIAS="qwen3-embedding"`
  - `LMBD_DEVICE="ROCm0"`
  - `LMBD_ENGINE="llama"`
  - `LMBD_HOST="127.0.0.1"`
  - `LMBD_LLAMA_DEVICE="rocm0"`
  - `LMBD_LLAMA_EXTRA_ARGS=""`
  - `LMBD_LLAMA_KV_UNIFIED="false"`
  - `LMBD_LLAMA_MODEL="/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf"`
  - `LMBD_LLAMA_N_CTX="8192"`
  - `LMBD_LLAMA_N_GPU_LAYERS="999"`
  - `LMBD_LLAMA_N_UBATCH="1024"`
  - `LMBD_LLAMA_PARALLEL="1"`
  - `LMBD_LLAMA_THREADS="4"`
  - `LMBD_N_CTX="8192"`
  - `LMBD_N_GPU_LAYERS="999"`
  - `LMBD_PORT="50082"`
  - `LMBD_TEI_DEVICE="rocm:0"`
  - `LMBD_TEI_EXTRA_ARGS="--dtype float32"`
  - `LMBD_TEI_MAX_BATCH_TOKENS="49152"`
  - `LMBD_TEI_MAX_CONCURRENT="6"`
  - `LMBD_TEI_MODEL="/data/public/machine-learning/models/embedding/bge-m3"`
  - `PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"`
  - `TRUST_REMOTE_CODE="true"`
- **Errors Count:** 0
- **Package Version:** `10154 (0e4a036223)`
- **Metrics:**
  - Avg Time/Run:         4.19 s
  - Avg Throughput:       10858.97 tokens/sec
  - Avg Chunk Latency:    47.0 ms
  - Avg Chunk p50:        46.1 ms
  - Avg Chunk p95:        47.0 ms

#### Code Completion FIM (`local-chat` - tab completion)
- **Benchmark Test Name:** `completion_hip-ROCm0`
- **Device Setting:** `ROCm0`
- **Special Setting:** `Layers: 999`
- **Model:** `qwen-coder-fim` (`qwen2.5-coder-1.5b-instruct-q4_k_m.gguf`)
- **Execution Target:** `HIP-ROCM0`
- **GPU Memory Used:** 1916.3 MB
- **CPU Memory Used:** 76.2 MB
- **Benchmark Running Time:** 18.02 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES="0"`
  - `HIP_VISIBLE_DEVICES="0"`
  - `LCHAT_ALIAS="qwen3"`
  - `LCHAT_CACHE_TYPE_K="q4_0"`
  - `LCHAT_CACHE_TYPE_V="q4_0"`
  - `LCHAT_CHAT_TEMPLATE_FILE="/data/public/machine-learning/models/vision-text/Qwen3.6-chat_template.jinja"`
  - `LCHAT_CTX_SIZE="240384"`
  - `LCHAT_DEVICE=""`
  - `LCHAT_EMBEDDING_ENABLED="false"`
  - `LCHAT_EXTRA_ARGS="--temp 0.6 --top-k 20 --repeat-penalty 1.1"`
  - `LCHAT_HOST="127.0.0.1"`
  - `LCHAT_MMPROJ="/data/public/machine-learning/models/vision-text/Agents-A1-APEX-I-Compact-mmproj.gguf"`
  - `LCHAT_MODEL="/data/public/machine-learning/models/vision-text/Agents-A1-APEX-I-Compact.gguf"`
  - `LCHAT_N_GPU_LAYERS="999"`
  - `LCHAT_PARALLEL="3"`
  - `LCHAT_PORT="50080"`
  - `LCHAT_SERVE_EMBEDDINGS="false"`
  - `LCHAT_SPECULATIVE="--spec-type ngram-simple --spec-ngram-simple-size-n 6 --spec-ngram-simple-size-m 4"`
  - `LCHAT_THREADS="4"`
  - `LCOMP_ALIAS="qwen-coder-fim"`
  - `LCOMP_CACHE_TYPE_K="q4_0"`
  - `LCOMP_CACHE_TYPE_V="q4_0"`
  - `LCOMP_CTX_SIZE="8192"`
  - `LCOMP_DEVICE="ROCm0"`
  - `LCOMP_ENABLED="true"`
  - `LCOMP_MODEL="/data/public/machine-learning/models/completion/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf"`
  - `LCOMP_N_GPU_LAYERS="999"`
  - `LCOMP_PARALLEL="2"`
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
  - `LOCAL_SIDECARS=""`
  - `LOCAL_SIDECAR_PORTMIRROR_CMD="bash -c 'if [ \"\${LMBD_ENABLED}\" = \"true\" ]; then exec socat TCP-LISTEN:\${LMBD_MIRROR_PORT:-50082},fork,reuseaddr TCP:\${LCHAT_HOST:-127.0.0.1}:\${LCHAT_PORT:-50080}; else exec sleep infinity; fi'"`
- **Errors Count:** 0
- **Package Version:** `10154 (0e4a036223)`
- **Warmup (Phase 0):**
  - TTFT (Prefill):       29.02 ms
  - Generation Speed:     194.34 tokens/sec
- **Generation (Phase 2):**
  - Avg TTFT (Prefill):   116.36 ms
  - Avg Prefill Speed:    34648.08 tokens/sec
  - Avg Generation Speed: 210.22 tokens/sec
  - Avg Decode Time:      0.48 s

#### Document Reranking (`local-rerank`)
- **Benchmark Test Name:** `rerank_hip-ROCm0`
- **Device Setting:** `ROCm0`
- **Special Setting:** `Layers: 99`
- **Model:** `qwen3-reranker` (`Qwen3-Reranker-0.6B.Q4_K_M.gguf`)
- **Execution Target:** `HIP-ROCM0`
- **GPU Memory Used:** 13264.1 MB
- **CPU Memory Used:** 1858.9 MB
- **Benchmark Running Time:** 0.80 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES="0"`
  - `HIP_VISIBLE_DEVICES="0"`
  - `LRR_ALIAS="qwen3-reranker"`
  - `LRR_API_PATH="/v1/rerank"`
  - `LRR_DEVICE="ROCm0"`
  - `LRR_ENGINE="llama"`
  - `LRR_HOST="127.0.0.1"`
  - `LRR_LLAMA_DEVICE="vulkan0"`
  - `LRR_LLAMA_EXTRA_ARGS=""`
  - `LRR_LLAMA_MODEL="/data/public/machine-learning/models/reranker/Qwen3-Reranker-0.6B.Q4_K_M.gguf"`
  - `LRR_LLAMA_N_CTX="12288"`
  - `LRR_LLAMA_N_GPU_LAYERS="999"`
  - `LRR_LLAMA_N_UBATCH="12288"`
  - `LRR_LLAMA_PARALLEL="2"`
  - `LRR_LLAMA_THREADS="4"`
  - `LRR_N_GPU_LAYERS="99"`
  - `LRR_PORT="50086"`
  - `LRR_TEI_DEVICE="rocm:0"`
  - `LRR_TEI_EXTRA_ARGS="--dtype bfloat16"`
  - `LRR_TEI_MAX_BATCH_TOKENS="8192"`
  - `LRR_TEI_MAX_CONCURRENT="4"`
  - `LRR_TEI_MODEL="/data/public/machine-learning/models/reranker/ettin-reranker-400m-v1"`
  - `PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"`
  - `TRUST_REMOTE_CODE="true"`
- **Errors Count:** 0
- **Package Version:** `10154 (0e4a036223)`
- **Metrics:**
  - Avg Reranking Time:   612.47 ms
  - Avg Docs Throughput:  16.33 docs/sec
  - Avg Token Speed:      5614.95 tokens/sec

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
  - `LSTT_ALIAS="whisper-1"`
  - `LSTT_DEVICE="0"`
  - `LSTT_EXTRA_ARGS=""`
  - `LSTT_HOST="127.0.0.1"`
  - `LSTT_INFERENCE_PATH="/v1/audio/transcriptions"`
  - `LSTT_MODEL="/data/public/machine-learning/models/speech-to-text/ggml-large-v3-turbo-q5_0.bin"`
  - `LSTT_NO_GPU="false"`
  - `LSTT_PORT="50090"`
  - `LSTT_THREADS="8"`
- **Errors Count:** 1
- **Top Errors:**
  - `Warning: STT Transcription text mismatch (garbled output)`
- **Package Version:** `1.9.1 (080bbbe85)`
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
- **Package Version:** `master-797-5ef4a75-1-g2251699, commit 22516991`
- **Metrics:**
  - Avg Generation Time:  7.43 seconds

### VULKAN-VULKAN0 Configuration Details

- **Device Name**: `AMD Radeon Graphics` (Total: 16384 MiB, Free: 16384 MiB)

#### Text Chat (`local-chat`)
- **Benchmark Test Name:** `chat_vulkan-Vulkan0`
- **Device Setting:** `Vulkan0`
- **Special Setting:** `Layers: 999 (Context: 20%)`
- **Model:** `qwen3` (`Agents-A1-APEX-I-Compact`)
- **Execution Target:** `VULKAN-VULKAN0`
- **GPU Memory Used:** 14416.1 MB
- **CPU Memory Used:** 63.4 MB
- **Benchmark Running Time:** 121.11 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `GGML_VK_DISABLE_MMVQ="1"`
  - `HIP_VISIBLE_DEVICES=""`
  - `LCHAT_ALIAS="qwen3"`
  - `LCHAT_CACHE_TYPE_K="q4_0"`
  - `LCHAT_CACHE_TYPE_V="q4_0"`
  - `LCHAT_CHAT_TEMPLATE_FILE="/data/public/machine-learning/models/vision-text/Qwen3.6-chat_template.jinja"`
  - `LCHAT_CHAT_TEMPLATE_KWARGS="{"enable_thinking": false}"`
  - `LCHAT_CTX_SIZE="240384"`
  - `LCHAT_DEVICE="Vulkan0"`
  - `LCHAT_EMBEDDING_ENABLED="false"`
  - `LCHAT_EXTRA_ARGS="--temp 0.6 --top-k 20 --repeat-penalty 1.1"`
  - `LCHAT_HOST="127.0.0.1"`
  - `LCHAT_MMPROJ=""`
  - `LCHAT_MODEL="/data/public/machine-learning/models/vision-text/Agents-A1-APEX-I-Compact.gguf"`
  - `LCHAT_MTP=""`
  - `LCHAT_N_CTX="48076"`
  - `LCHAT_N_GPU_LAYERS="999"`
  - `LCHAT_PARALLEL="2"`
  - `LCHAT_PORT="50080"`
  - `LCHAT_SERVE_EMBEDDINGS="false"`
  - `LCHAT_SIDECARS=""`
  - `LCHAT_SIDECAR_PORTMIRROR_CMD="bash -c 'if [ \"\${LMBD_ENABLED}\" = \"true\" ]; then exec socat TCP-LISTEN:\${LMBD_MIRROR_PORT:-50082},fork,reuseaddr TCP:\${LCHAT_HOST:-127.0.0.1}:\${LCHAT_PORT:-50080}; else exec sleep infinity; fi'"`
  - `LCHAT_SPECULATIVE="--spec-type ngram-simple --spec-ngram-simple-size-n 6 --spec-ngram-simple-size-m 4"`
  - `LCHAT_THREADS="4"`
  - `LCOMP_ALIAS="qwen-coder-fim"`
  - `LCOMP_CACHE_TYPE_K="q4_0"`
  - `LCOMP_CACHE_TYPE_V="q4_0"`
  - `LCOMP_CTX_SIZE="8192"`
  - `LCOMP_ENABLED="false"`
  - `LCOMP_EXTRA_ARGS=""`
  - `LCOMP_MODEL="/data/public/machine-learning/models/completion/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf"`
  - `LCOMP_PARALLEL="2"`
  - `LMBD_ALIAS="qwen3-embedding"`
  - `LMBD_CACHE_TYPE_K="q8_0"`
  - `LMBD_CACHE_TYPE_V="q8_0"`
  - `LMBD_CTX_SIZE="16384"`
  - `LMBD_ENABLED="false"`
  - `LMBD_EXTRA_ARGS="--flash-attn on"`
  - `LMBD_MIRROR_PORT="50082"`
  - `LMBD_MODEL="/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf"`
  - `LMBD_PARALLEL="2"`
  - `LMBD_UBATCH_SIZE="16384"`
- **Errors Count:** 0
- **Package Version:** `10154 (0e4a036223)`
- **Warmup (Phase 0):**
  - TTFT (Prefill):       1657.46 ms
  - Prefill Speed:        12.67 tokens/sec
  - Generation Speed:     15.69 tokens/sec
- **Generation (Phase 2):**
  - Avg Completion Tokens: 574.0
  - Avg TTFT (Prefill):   72105.11 ms
  - Avg Prefill Speed:    80.85 tokens/sec
  - Avg Generation Speed: 12.22 tokens/sec
  - Avg Decode Time:      46.98 s
- **Vision Description (Phase 4):**
  - Avg TTFT (Prefill):   0.00 ms
  - Avg Generation Speed: 0.00 tokens/sec

#### Text Embedding (`local-embedding`)
- **Benchmark Test Name:** `embedding_vulkan-Vulkan0`
- **Device Setting:** `Vulkan0`
- **Special Setting:** `Layers: 999`
- **Model:** `qwen3-embedding` (`Qwen3-Embedding-0.6B-Q8_0.gguf`)
- **Execution Target:** `VULKAN-VULKAN0`
- **GPU Memory Used:** 1692.5 MB
- **CPU Memory Used:** 294.1 MB
- **Benchmark Running Time:** 53.79 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LMBD_ALIAS="qwen3-embedding"`
  - `LMBD_DEVICE="Vulkan0"`
  - `LMBD_ENGINE="llama"`
  - `LMBD_HOST="127.0.0.1"`
  - `LMBD_LLAMA_DEVICE="rocm0"`
  - `LMBD_LLAMA_EXTRA_ARGS=""`
  - `LMBD_LLAMA_KV_UNIFIED="false"`
  - `LMBD_LLAMA_MODEL="/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf"`
  - `LMBD_LLAMA_N_CTX="8192"`
  - `LMBD_LLAMA_N_GPU_LAYERS="999"`
  - `LMBD_LLAMA_N_UBATCH="1024"`
  - `LMBD_LLAMA_PARALLEL="1"`
  - `LMBD_LLAMA_THREADS="4"`
  - `LMBD_N_CTX="8192"`
  - `LMBD_N_GPU_LAYERS="999"`
  - `LMBD_PORT="50082"`
  - `LMBD_TEI_DEVICE="rocm:0"`
  - `LMBD_TEI_EXTRA_ARGS="--dtype float32"`
  - `LMBD_TEI_MAX_BATCH_TOKENS="49152"`
  - `LMBD_TEI_MAX_CONCURRENT="6"`
  - `LMBD_TEI_MODEL="/data/public/machine-learning/models/embedding/bge-m3"`
  - `PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"`
  - `TRUST_REMOTE_CODE="true"`
- **Errors Count:** 0
- **Package Version:** `10154 (0e4a036223)`
- **Metrics:**
  - Avg Time/Run:         53.47 s
  - Avg Throughput:       850.22 tokens/sec
  - Avg Chunk Latency:    600.8 ms
  - Avg Chunk p50:        601.4 ms
  - Avg Chunk p95:        603.3 ms

#### Code Completion FIM (`local-chat` - tab completion)
- **Benchmark Test Name:** `completion_vulkan-Vulkan0`
- **Device Setting:** `Vulkan0`
- **Special Setting:** `Layers: 999`
- **Model:** `qwen-coder-fim` (`qwen2.5-coder-1.5b-instruct-q4_k_m.gguf`)
- **Execution Target:** `VULKAN-VULKAN0`
- **GPU Memory Used:** 1944.2 MB
- **CPU Memory Used:** 59.4 MB
- **Benchmark Running Time:** 3.41 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LCHAT_ALIAS="qwen3"`
  - `LCHAT_CACHE_TYPE_K="q4_0"`
  - `LCHAT_CACHE_TYPE_V="q4_0"`
  - `LCHAT_CHAT_TEMPLATE_FILE="/data/public/machine-learning/models/vision-text/Qwen3.6-chat_template.jinja"`
  - `LCHAT_CTX_SIZE="240384"`
  - `LCHAT_DEVICE=""`
  - `LCHAT_EMBEDDING_ENABLED="false"`
  - `LCHAT_EXTRA_ARGS="--temp 0.6 --top-k 20 --repeat-penalty 1.1"`
  - `LCHAT_HOST="127.0.0.1"`
  - `LCHAT_MMPROJ="/data/public/machine-learning/models/vision-text/Agents-A1-APEX-I-Compact-mmproj.gguf"`
  - `LCHAT_MODEL="/data/public/machine-learning/models/vision-text/Agents-A1-APEX-I-Compact.gguf"`
  - `LCHAT_N_GPU_LAYERS="999"`
  - `LCHAT_PARALLEL="3"`
  - `LCHAT_PORT="50080"`
  - `LCHAT_SERVE_EMBEDDINGS="false"`
  - `LCHAT_SPECULATIVE="--spec-type ngram-simple --spec-ngram-simple-size-n 6 --spec-ngram-simple-size-m 4"`
  - `LCHAT_THREADS="4"`
  - `LCOMP_ALIAS="qwen-coder-fim"`
  - `LCOMP_CACHE_TYPE_K="q4_0"`
  - `LCOMP_CACHE_TYPE_V="q4_0"`
  - `LCOMP_CTX_SIZE="8192"`
  - `LCOMP_DEVICE="Vulkan0"`
  - `LCOMP_ENABLED="true"`
  - `LCOMP_MODEL="/data/public/machine-learning/models/completion/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf"`
  - `LCOMP_N_GPU_LAYERS="999"`
  - `LCOMP_PARALLEL="2"`
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
  - `LOCAL_SIDECARS=""`
  - `LOCAL_SIDECAR_PORTMIRROR_CMD="bash -c 'if [ \"\${LMBD_ENABLED}\" = \"true\" ]; then exec socat TCP-LISTEN:\${LMBD_MIRROR_PORT:-50082},fork,reuseaddr TCP:\${LCHAT_HOST:-127.0.0.1}:\${LCHAT_PORT:-50080}; else exec sleep infinity; fi'"`
- **Errors Count:** 0
- **Package Version:** `10154 (0e4a036223)`
- **Warmup (Phase 0):**
  - TTFT (Prefill):       26.35 ms
  - Generation Speed:     240.11 tokens/sec
- **Generation (Phase 2):**
  - Avg TTFT (Prefill):   128.04 ms
  - Avg Prefill Speed:    15479.29 tokens/sec
  - Avg Generation Speed: 248.12 tokens/sec
  - Avg Decode Time:      0.40 s

#### Document Reranking (`local-rerank`)
- **Benchmark Test Name:** `rerank_vulkan-Vulkan0`
- **Device Setting:** `Vulkan0`
- **Special Setting:** `Layers: 99`
- **Model:** `qwen3-reranker` (`Qwen3-Reranker-0.6B.Q4_K_M.gguf`)
- **Execution Target:** `VULKAN-VULKAN0`
- **GPU Memory Used:** 3510.8 MB
- **CPU Memory Used:** 412.6 MB
- **Benchmark Running Time:** 6.41 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LRR_ALIAS="qwen3-reranker"`
  - `LRR_API_PATH="/v1/rerank"`
  - `LRR_DEVICE="Vulkan0"`
  - `LRR_ENGINE="llama"`
  - `LRR_HOST="127.0.0.1"`
  - `LRR_LLAMA_DEVICE="vulkan0"`
  - `LRR_LLAMA_EXTRA_ARGS=""`
  - `LRR_LLAMA_MODEL="/data/public/machine-learning/models/reranker/Qwen3-Reranker-0.6B.Q4_K_M.gguf"`
  - `LRR_LLAMA_N_CTX="12288"`
  - `LRR_LLAMA_N_GPU_LAYERS="999"`
  - `LRR_LLAMA_N_UBATCH="12288"`
  - `LRR_LLAMA_PARALLEL="2"`
  - `LRR_LLAMA_THREADS="4"`
  - `LRR_N_GPU_LAYERS="99"`
  - `LRR_PORT="50086"`
  - `LRR_TEI_DEVICE="rocm:0"`
  - `LRR_TEI_EXTRA_ARGS="--dtype bfloat16"`
  - `LRR_TEI_MAX_BATCH_TOKENS="8192"`
  - `LRR_TEI_MAX_CONCURRENT="4"`
  - `LRR_TEI_MODEL="/data/public/machine-learning/models/reranker/ettin-reranker-400m-v1"`
  - `PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"`
  - `TRUST_REMOTE_CODE="true"`
- **Errors Count:** 0
- **Package Version:** `10154 (0e4a036223)`
- **Metrics:**
  - Avg Reranking Time:   6278.25 ms
  - Avg Docs Throughput:  1.59 docs/sec
  - Avg Token Speed:      547.76 tokens/sec

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
  - `LSTT_ALIAS="whisper-1"`
  - `LSTT_DEVICE="0"`
  - `LSTT_EXTRA_ARGS=""`
  - `LSTT_HOST="127.0.0.1"`
  - `LSTT_INFERENCE_PATH="/v1/audio/transcriptions"`
  - `LSTT_MODEL="/data/public/machine-learning/models/speech-to-text/ggml-large-v3-turbo-q5_0.bin"`
  - `LSTT_NO_GPU="false"`
  - `LSTT_PORT="50090"`
  - `LSTT_THREADS="8"`
- **Errors Count:** 0
- **Package Version:** `1.9.1 (080bbbe85)`
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
- **Package Version:** `master-797-5ef4a75-1-g2251699, commit 22516991`
- **Metrics:**
  - Avg Generation Time:  92.76 seconds

### VULKAN-VULKAN1 Configuration Details

- **Device Name**: `AMD Radeon RX 7900 XTX` (Total: 24560 MiB, Free: 24560 MiB)

#### Text Chat (`local-chat`)
- **Benchmark Test Name:** `chat_vulkan-Vulkan1`
- **Device Setting:** `Vulkan1`
- **Special Setting:** `Layers: 999`
- **Model:** `qwen3` (`Agents-A1-APEX-I-Compact`)
- **Execution Target:** `VULKAN-VULKAN1`
- **GPU Memory Used:** 17894.6 MB
- **CPU Memory Used:** 63.8 MB
- **Benchmark Running Time:** 27.64 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `GGML_VK_DISABLE_MMVQ="1"`
  - `HIP_VISIBLE_DEVICES=""`
  - `LCHAT_ALIAS="qwen3"`
  - `LCHAT_CACHE_TYPE_K="q4_0"`
  - `LCHAT_CACHE_TYPE_V="q4_0"`
  - `LCHAT_CHAT_TEMPLATE_FILE="/data/public/machine-learning/models/vision-text/Qwen3.6-chat_template.jinja"`
  - `LCHAT_CHAT_TEMPLATE_KWARGS="{"enable_thinking": false}"`
  - `LCHAT_CTX_SIZE="240384"`
  - `LCHAT_DEVICE="Vulkan1"`
  - `LCHAT_EMBEDDING_ENABLED="false"`
  - `LCHAT_EXTRA_ARGS="--temp 0.6 --top-k 20 --repeat-penalty 1.1"`
  - `LCHAT_HOST="127.0.0.1"`
  - `LCHAT_MMPROJ=""`
  - `LCHAT_MODEL="/data/public/machine-learning/models/vision-text/Agents-A1-APEX-I-Compact.gguf"`
  - `LCHAT_MTP=""`
  - `LCHAT_N_CTX="240384"`
  - `LCHAT_N_GPU_LAYERS="999"`
  - `LCHAT_PARALLEL="2"`
  - `LCHAT_PORT="50080"`
  - `LCHAT_SERVE_EMBEDDINGS="false"`
  - `LCHAT_SIDECARS=""`
  - `LCHAT_SIDECAR_PORTMIRROR_CMD="bash -c 'if [ \"\${LMBD_ENABLED}\" = \"true\" ]; then exec socat TCP-LISTEN:\${LMBD_MIRROR_PORT:-50082},fork,reuseaddr TCP:\${LCHAT_HOST:-127.0.0.1}:\${LCHAT_PORT:-50080}; else exec sleep infinity; fi'"`
  - `LCHAT_SPECULATIVE="--spec-type ngram-simple --spec-ngram-simple-size-n 6 --spec-ngram-simple-size-m 4"`
  - `LCHAT_THREADS="4"`
  - `LCOMP_ALIAS="qwen-coder-fim"`
  - `LCOMP_CACHE_TYPE_K="q4_0"`
  - `LCOMP_CACHE_TYPE_V="q4_0"`
  - `LCOMP_CTX_SIZE="8192"`
  - `LCOMP_ENABLED="false"`
  - `LCOMP_EXTRA_ARGS=""`
  - `LCOMP_MODEL="/data/public/machine-learning/models/completion/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf"`
  - `LCOMP_PARALLEL="2"`
  - `LMBD_ALIAS="qwen3-embedding"`
  - `LMBD_CACHE_TYPE_K="q8_0"`
  - `LMBD_CACHE_TYPE_V="q8_0"`
  - `LMBD_CTX_SIZE="16384"`
  - `LMBD_ENABLED="false"`
  - `LMBD_EXTRA_ARGS="--flash-attn on"`
  - `LMBD_MIRROR_PORT="50082"`
  - `LMBD_MODEL="/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf"`
  - `LMBD_PARALLEL="2"`
  - `LMBD_UBATCH_SIZE="16384"`
- **Errors Count:** 0
- **Package Version:** `10154 (0e4a036223)`
- **Warmup (Phase 0):**
  - TTFT (Prefill):       142.95 ms
  - Prefill Speed:        146.91 tokens/sec
  - Generation Speed:     141.65 tokens/sec
- **Generation (Phase 2):**
  - Avg Completion Tokens: 1024.0
  - Avg TTFT (Prefill):   17804.84 ms
  - Avg Prefill Speed:    1744.19 tokens/sec
  - Avg Generation Speed: 107.04 tokens/sec
  - Avg Decode Time:      9.57 s
- **Vision Description (Phase 4):**
  - Avg TTFT (Prefill):   0.00 ms
  - Avg Generation Speed: 0.00 tokens/sec

#### Text Embedding (`local-embedding`)
- **Benchmark Test Name:** `embedding_vulkan-Vulkan1`
- **Device Setting:** `Vulkan1`
- **Special Setting:** `Layers: 999`
- **Model:** `qwen3-embedding` (`Qwen3-Embedding-0.6B-Q8_0.gguf`)
- **Execution Target:** `VULKAN-VULKAN1`
- **GPU Memory Used:** 1483.9 MB
- **CPU Memory Used:** 297.0 MB
- **Benchmark Running Time:** 7.72 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LMBD_ALIAS="qwen3-embedding"`
  - `LMBD_DEVICE="Vulkan1"`
  - `LMBD_ENGINE="llama"`
  - `LMBD_HOST="127.0.0.1"`
  - `LMBD_LLAMA_DEVICE="rocm0"`
  - `LMBD_LLAMA_EXTRA_ARGS=""`
  - `LMBD_LLAMA_KV_UNIFIED="false"`
  - `LMBD_LLAMA_MODEL="/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf"`
  - `LMBD_LLAMA_N_CTX="8192"`
  - `LMBD_LLAMA_N_GPU_LAYERS="999"`
  - `LMBD_LLAMA_N_UBATCH="1024"`
  - `LMBD_LLAMA_PARALLEL="1"`
  - `LMBD_LLAMA_THREADS="4"`
  - `LMBD_N_CTX="4096"`
  - `LMBD_N_GPU_LAYERS="999"`
  - `LMBD_PORT="50082"`
  - `LMBD_TEI_DEVICE="rocm:0"`
  - `LMBD_TEI_EXTRA_ARGS="--dtype float32"`
  - `LMBD_TEI_MAX_BATCH_TOKENS="49152"`
  - `LMBD_TEI_MAX_CONCURRENT="6"`
  - `LMBD_TEI_MODEL="/data/public/machine-learning/models/embedding/bge-m3"`
  - `PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"`
  - `TRUST_REMOTE_CODE="true"`
- **Errors Count:** 0
- **Package Version:** `10154 (0e4a036223)`
- **Metrics:**
  - Avg Time/Run:         7.45 s
  - Avg Throughput:       6098.09 tokens/sec
  - Avg Chunk Latency:    83.8 ms
  - Avg Chunk p50:        82.4 ms
  - Avg Chunk p95:        84.7 ms

#### Code Completion FIM (`local-chat` - tab completion)
- **Benchmark Test Name:** `completion_vulkan-Vulkan1`
- **Device Setting:** `Vulkan1`
- **Special Setting:** `Layers: 999`
- **Model:** `qwen-coder-fim` (`qwen2.5-coder-1.5b-instruct-q4_k_m.gguf`)
- **Execution Target:** `VULKAN-VULKAN1`
- **GPU Memory Used:** 1121.8 MB
- **CPU Memory Used:** 65.7 MB
- **Benchmark Running Time:** 14.22 s
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
  - `LCHAT_EXTRA_ARGS="--temp 0.6 --top-k 20 --repeat-penalty 1.1"`
  - `LCHAT_HOST="127.0.0.1"`
  - `LCHAT_MMPROJ="/data/public/machine-learning/models/vision-text/Agents-A1-APEX-I-Compact-mmproj.gguf"`
  - `LCHAT_MODEL="/data/public/machine-learning/models/vision-text/Agents-A1-APEX-I-Compact.gguf"`
  - `LCHAT_N_GPU_LAYERS="999"`
  - `LCHAT_PARALLEL="3"`
  - `LCHAT_PORT="50080"`
  - `LCHAT_SERVE_EMBEDDINGS="false"`
  - `LCHAT_SPECULATIVE="--spec-type ngram-simple --spec-ngram-simple-size-n 6 --spec-ngram-simple-size-m 4"`
  - `LCHAT_THREADS="4"`
  - `LCOMP_ALIAS="qwen-coder-fim"`
  - `LCOMP_CACHE_TYPE_K="q4_0"`
  - `LCOMP_CACHE_TYPE_V="q4_0"`
  - `LCOMP_CTX_SIZE="8192"`
  - `LCOMP_DEVICE="Vulkan1"`
  - `LCOMP_ENABLED="true"`
  - `LCOMP_MODEL="/data/public/machine-learning/models/completion/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf"`
  - `LCOMP_N_GPU_LAYERS="999"`
  - `LCOMP_PARALLEL="2"`
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
  - `LOCAL_SIDECARS=""`
  - `LOCAL_SIDECAR_PORTMIRROR_CMD="bash -c 'if [ \"\${LMBD_ENABLED}\" = \"true\" ]; then exec socat TCP-LISTEN:\${LMBD_MIRROR_PORT:-50082},fork,reuseaddr TCP:\${LCHAT_HOST:-127.0.0.1}:\${LCHAT_PORT:-50080}; else exec sleep infinity; fi'"`
- **Errors Count:** 0
- **Package Version:** `10154 (0e4a036223)`
- **Warmup (Phase 0):**
  - TTFT (Prefill):       15.30 ms
  - Generation Speed:     254.03 tokens/sec
- **Generation (Phase 2):**
  - Avg TTFT (Prefill):   70.71 ms
  - Avg Prefill Speed:    37891.66 tokens/sec
  - Avg Generation Speed: 252.04 tokens/sec
  - Avg Decode Time:      0.40 s

#### Document Reranking (`local-rerank`)
- **Benchmark Test Name:** `rerank_vulkan-Vulkan1`
- **Device Setting:** `Vulkan1`
- **Special Setting:** `Layers: 99`
- **Model:** `qwen3-reranker` (`Qwen3-Reranker-0.6B.Q4_K_M.gguf`)
- **Execution Target:** `VULKAN-VULKAN1`
- **GPU Memory Used:** 3544.6 MB
- **CPU Memory Used:** 417.7 MB
- **Benchmark Running Time:** 1.00 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LRR_ALIAS="qwen3-reranker"`
  - `LRR_API_PATH="/v1/rerank"`
  - `LRR_DEVICE="Vulkan1"`
  - `LRR_ENGINE="llama"`
  - `LRR_HOST="127.0.0.1"`
  - `LRR_LLAMA_DEVICE="vulkan0"`
  - `LRR_LLAMA_EXTRA_ARGS=""`
  - `LRR_LLAMA_MODEL="/data/public/machine-learning/models/reranker/Qwen3-Reranker-0.6B.Q4_K_M.gguf"`
  - `LRR_LLAMA_N_CTX="12288"`
  - `LRR_LLAMA_N_GPU_LAYERS="999"`
  - `LRR_LLAMA_N_UBATCH="12288"`
  - `LRR_LLAMA_PARALLEL="2"`
  - `LRR_LLAMA_THREADS="4"`
  - `LRR_N_GPU_LAYERS="99"`
  - `LRR_PORT="50086"`
  - `LRR_TEI_DEVICE="rocm:0"`
  - `LRR_TEI_EXTRA_ARGS="--dtype bfloat16"`
  - `LRR_TEI_MAX_BATCH_TOKENS="8192"`
  - `LRR_TEI_MAX_CONCURRENT="4"`
  - `LRR_TEI_MODEL="/data/public/machine-learning/models/reranker/ettin-reranker-400m-v1"`
  - `PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"`
  - `TRUST_REMOTE_CODE="true"`
- **Errors Count:** 0
- **Package Version:** `10154 (0e4a036223)`
- **Metrics:**
  - Avg Reranking Time:   861.75 ms
  - Avg Docs Throughput:  11.60 docs/sec
  - Avg Token Speed:      3990.73 tokens/sec

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
  - `LSTT_ALIAS="whisper-1"`
  - `LSTT_DEVICE="1"`
  - `LSTT_EXTRA_ARGS=""`
  - `LSTT_HOST="127.0.0.1"`
  - `LSTT_INFERENCE_PATH="/v1/audio/transcriptions"`
  - `LSTT_MODEL="/data/public/machine-learning/models/speech-to-text/ggml-large-v3-turbo-q5_0.bin"`
  - `LSTT_NO_GPU="false"`
  - `LSTT_PORT="50090"`
  - `LSTT_THREADS="8"`
- **Errors Count:** 0
- **Package Version:** `1.9.1 (080bbbe85)`
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
- **Package Version:** `master-797-5ef4a75-1-g2251699, commit 22516991`
- **Metrics:**
  - Avg Generation Time:  6.96 seconds

### CPU Configuration Details

#### Text Chat (`local-chat`)
- **Benchmark Test Name:** `chat_cpu`
- **Device Setting:** `none`
- **Special Setting:** `Layers: 0 (Context: 5%)`
- **Model:** `qwen3` (`Agents-A1-APEX-I-Compact`)
- **Execution Target:** `CPU`
- **GPU Memory Used:** 0.1 MB
- **CPU Memory Used:** 63.1 MB
- **Benchmark Running Time:** 83.77 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `GGML_VK_DISABLE_MMVQ="1"`
  - `HIP_VISIBLE_DEVICES=""`
  - `LCHAT_ALIAS="qwen3"`
  - `LCHAT_CACHE_TYPE_K="q4_0"`
  - `LCHAT_CACHE_TYPE_V="q4_0"`
  - `LCHAT_CHAT_TEMPLATE_FILE="/data/public/machine-learning/models/vision-text/Qwen3.6-chat_template.jinja"`
  - `LCHAT_CHAT_TEMPLATE_KWARGS="{"enable_thinking": false}"`
  - `LCHAT_CTX_SIZE="240384"`
  - `LCHAT_DEVICE="none"`
  - `LCHAT_EMBEDDING_ENABLED="false"`
  - `LCHAT_EXTRA_ARGS="--temp 0.6 --top-k 20 --repeat-penalty 1.1"`
  - `LCHAT_HOST="127.0.0.1"`
  - `LCHAT_MMPROJ=""`
  - `LCHAT_MODEL="/data/public/machine-learning/models/vision-text/Agents-A1-APEX-I-Compact.gguf"`
  - `LCHAT_MTP=""`
  - `LCHAT_N_CTX="12019"`
  - `LCHAT_N_GPU_LAYERS="0"`
  - `LCHAT_PARALLEL="2"`
  - `LCHAT_PORT="50080"`
  - `LCHAT_SERVE_EMBEDDINGS="false"`
  - `LCHAT_SIDECARS=""`
  - `LCHAT_SIDECAR_PORTMIRROR_CMD="bash -c 'if [ \"\${LMBD_ENABLED}\" = \"true\" ]; then exec socat TCP-LISTEN:\${LMBD_MIRROR_PORT:-50082},fork,reuseaddr TCP:\${LCHAT_HOST:-127.0.0.1}:\${LCHAT_PORT:-50080}; else exec sleep infinity; fi'"`
  - `LCHAT_SPECULATIVE="--spec-type ngram-simple --spec-ngram-simple-size-n 6 --spec-ngram-simple-size-m 4"`
  - `LCHAT_THREADS="4"`
  - `LCOMP_ALIAS="qwen-coder-fim"`
  - `LCOMP_CACHE_TYPE_K="q4_0"`
  - `LCOMP_CACHE_TYPE_V="q4_0"`
  - `LCOMP_CTX_SIZE="8192"`
  - `LCOMP_ENABLED="false"`
  - `LCOMP_EXTRA_ARGS=""`
  - `LCOMP_MODEL="/data/public/machine-learning/models/completion/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf"`
  - `LCOMP_PARALLEL="2"`
  - `LMBD_ALIAS="qwen3-embedding"`
  - `LMBD_CACHE_TYPE_K="q8_0"`
  - `LMBD_CACHE_TYPE_V="q8_0"`
  - `LMBD_CTX_SIZE="16384"`
  - `LMBD_ENABLED="false"`
  - `LMBD_EXTRA_ARGS="--flash-attn on"`
  - `LMBD_MIRROR_PORT="50082"`
  - `LMBD_MODEL="/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf"`
  - `LMBD_PARALLEL="2"`
  - `LMBD_UBATCH_SIZE="16384"`
- **Errors Count:** 0
- **Package Version:** `10154 (0e4a036223)`
- **Warmup (Phase 0):**
  - TTFT (Prefill):       576.59 ms
  - Prefill Speed:        36.42 tokens/sec
  - Generation Speed:     16.04 tokens/sec
- **Generation (Phase 2):**
  - Avg Completion Tokens: 493.0
  - Avg TTFT (Prefill):   41745.44 ms
  - Avg Prefill Speed:    35.62 tokens/sec
  - Avg Generation Speed: 12.01 tokens/sec
  - Avg Decode Time:      41.04 s
- **Vision Description (Phase 4):**
  - Avg TTFT (Prefill):   0.00 ms
  - Avg Generation Speed: 0.00 tokens/sec

#### Text Embedding (`local-embedding`)
- **Benchmark Test Name:** `embedding_cpu`
- **Device Setting:** `none`
- **Special Setting:** `Layers: 0`
- **Model:** `qwen3-embedding` (`Qwen3-Embedding-0.6B-Q8_0.gguf`)
- **Execution Target:** `CPU`
- **GPU Memory Used:** 0.0 MB
- **CPU Memory Used:** 2438.5 MB
- **Benchmark Running Time:** 29.50 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LMBD_ALIAS="qwen3-embedding"`
  - `LMBD_DEVICE="none"`
  - `LMBD_ENGINE="llama"`
  - `LMBD_HOST="127.0.0.1"`
  - `LMBD_LLAMA_DEVICE="rocm0"`
  - `LMBD_LLAMA_EXTRA_ARGS=""`
  - `LMBD_LLAMA_KV_UNIFIED="false"`
  - `LMBD_LLAMA_MODEL="/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf"`
  - `LMBD_LLAMA_N_CTX="8192"`
  - `LMBD_LLAMA_N_GPU_LAYERS="999"`
  - `LMBD_LLAMA_N_UBATCH="1024"`
  - `LMBD_LLAMA_PARALLEL="1"`
  - `LMBD_LLAMA_THREADS="4"`
  - `LMBD_N_CTX="8192"`
  - `LMBD_N_GPU_LAYERS="0"`
  - `LMBD_PORT="50082"`
  - `LMBD_TEI_DEVICE="rocm:0"`
  - `LMBD_TEI_EXTRA_ARGS="--dtype float32"`
  - `LMBD_TEI_MAX_BATCH_TOKENS="49152"`
  - `LMBD_TEI_MAX_CONCURRENT="6"`
  - `LMBD_TEI_MODEL="/data/public/machine-learning/models/embedding/bge-m3"`
  - `PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"`
  - `TRUST_REMOTE_CODE="true"`
- **Errors Count:** 0
- **Package Version:** `10154 (0e4a036223)`
- **Metrics:**
  - Avg Time/Run:         292.15 s
  - Avg Throughput:       140.20 tokens/sec
  - Avg Chunk Latency:    3651.9 ms
  - Avg Chunk p50:        3640.1 ms
  - Avg Chunk p95:        3786.1 ms

#### Code Completion FIM (`local-chat` - tab completion)
- **Benchmark Test Name:** `completion_cpu`
- **Device Setting:** `none`
- **Special Setting:** `Layers: 0`
- **Model:** `qwen-coder-fim` (`qwen2.5-coder-1.5b-instruct-q4_k_m.gguf`)
- **Execution Target:** `CPU`
- **GPU Memory Used:** 46.5 MB
- **CPU Memory Used:** 64.1 MB
- **Benchmark Running Time:** 17.45 s
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
  - `LCHAT_EXTRA_ARGS="--temp 0.6 --top-k 20 --repeat-penalty 1.1"`
  - `LCHAT_HOST="127.0.0.1"`
  - `LCHAT_MMPROJ="/data/public/machine-learning/models/vision-text/Agents-A1-APEX-I-Compact-mmproj.gguf"`
  - `LCHAT_MODEL="/data/public/machine-learning/models/vision-text/Agents-A1-APEX-I-Compact.gguf"`
  - `LCHAT_N_GPU_LAYERS="999"`
  - `LCHAT_PARALLEL="3"`
  - `LCHAT_PORT="50080"`
  - `LCHAT_SERVE_EMBEDDINGS="false"`
  - `LCHAT_SPECULATIVE="--spec-type ngram-simple --spec-ngram-simple-size-n 6 --spec-ngram-simple-size-m 4"`
  - `LCHAT_THREADS="4"`
  - `LCOMP_ALIAS="qwen-coder-fim"`
  - `LCOMP_CACHE_TYPE_K="q4_0"`
  - `LCOMP_CACHE_TYPE_V="q4_0"`
  - `LCOMP_CTX_SIZE="8192"`
  - `LCOMP_DEVICE="none"`
  - `LCOMP_ENABLED="true"`
  - `LCOMP_MODEL="/data/public/machine-learning/models/completion/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf"`
  - `LCOMP_N_GPU_LAYERS="0"`
  - `LCOMP_PARALLEL="2"`
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
  - `LOCAL_SIDECARS=""`
  - `LOCAL_SIDECAR_PORTMIRROR_CMD="bash -c 'if [ \"\${LMBD_ENABLED}\" = \"true\" ]; then exec socat TCP-LISTEN:\${LMBD_MIRROR_PORT:-50082},fork,reuseaddr TCP:\${LCHAT_HOST:-127.0.0.1}:\${LCHAT_PORT:-50080}; else exec sleep infinity; fi'"`
- **Errors Count:** 0
- **Package Version:** `10154 (0e4a036223)`
- **Warmup (Phase 0):**
  - TTFT (Prefill):       37.61 ms
  - Generation Speed:     37.82 tokens/sec
- **Generation (Phase 2):**
  - Avg TTFT (Prefill):   13769.06 ms
  - Avg Prefill Speed:    79.89 tokens/sec
  - Avg Generation Speed: 30.68 tokens/sec
  - Avg Decode Time:      3.26 s

#### Document Reranking (`local-rerank`)
- **Benchmark Test Name:** `rerank_cpu`
- **Device Setting:** `none`
- **Special Setting:** `Layers: 0`
- **Model:** `qwen3-reranker` (`Qwen3-Reranker-0.6B.Q4_K_M.gguf`)
- **Execution Target:** `CPU`
- **GPU Memory Used:** 0.1 MB
- **CPU Memory Used:** 4281.0 MB
- **Benchmark Running Time:** 15.26 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LRR_ALIAS="qwen3-reranker"`
  - `LRR_API_PATH="/v1/rerank"`
  - `LRR_DEVICE="none"`
  - `LRR_ENGINE="llama"`
  - `LRR_HOST="127.0.0.1"`
  - `LRR_LLAMA_DEVICE="vulkan0"`
  - `LRR_LLAMA_EXTRA_ARGS=""`
  - `LRR_LLAMA_MODEL="/data/public/machine-learning/models/reranker/Qwen3-Reranker-0.6B.Q4_K_M.gguf"`
  - `LRR_LLAMA_N_CTX="12288"`
  - `LRR_LLAMA_N_GPU_LAYERS="999"`
  - `LRR_LLAMA_N_UBATCH="12288"`
  - `LRR_LLAMA_PARALLEL="2"`
  - `LRR_LLAMA_THREADS="4"`
  - `LRR_N_GPU_LAYERS="0"`
  - `LRR_PORT="50086"`
  - `LRR_TEI_DEVICE="rocm:0"`
  - `LRR_TEI_EXTRA_ARGS="--dtype bfloat16"`
  - `LRR_TEI_MAX_BATCH_TOKENS="8192"`
  - `LRR_TEI_MAX_CONCURRENT="4"`
  - `LRR_TEI_MODEL="/data/public/machine-learning/models/reranker/ettin-reranker-400m-v1"`
  - `PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"`
  - `TRUST_REMOTE_CODE="true"`
- **Errors Count:** 0
- **Package Version:** `10154 (0e4a036223)`
- **Metrics:**
  - Avg Reranking Time:   15104.88 ms
  - Avg Docs Throughput:  0.66 docs/sec
  - Avg Token Speed:      227.67 tokens/sec

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
  - `LSTT_ALIAS="whisper-1"`
  - `LSTT_DEVICE=""`
  - `LSTT_EXTRA_ARGS=""`
  - `LSTT_HOST="127.0.0.1"`
  - `LSTT_INFERENCE_PATH="/v1/audio/transcriptions"`
  - `LSTT_MODEL="/data/public/machine-learning/models/speech-to-text/ggml-large-v3-turbo-q5_0.bin"`
  - `LSTT_NO_GPU="true"`
  - `LSTT_PORT="50090"`
  - `LSTT_THREADS="8"`
- **Errors Count:** 0
- **Package Version:** `1.9.1 (080bbbe85)`
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
- **Package Version:** `master-797-5ef4a75-1-g2251699, commit 22516991`
- **Metrics:**
  - Avg Generation Time:  282.65 seconds

### CPU-BLAS Configuration Details

#### Text Chat (`local-chat`)
- **Benchmark Test Name:** `chat_cpu-blas`
- **Device Setting:** `BLAS`
- **Special Setting:** `Layers: 0 (Context: 5%)`
- **Model:** `qwen3` (`Agents-A1-APEX-I-Compact`)
- **Execution Target:** `CPU-BLAS`
- **GPU Memory Used:** 0.1 MB
- **CPU Memory Used:** 63.4 MB
- **Benchmark Running Time:** 83.89 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `GGML_VK_DISABLE_MMVQ="1"`
  - `HIP_VISIBLE_DEVICES=""`
  - `LCHAT_ALIAS="qwen3"`
  - `LCHAT_CACHE_TYPE_K="q4_0"`
  - `LCHAT_CACHE_TYPE_V="q4_0"`
  - `LCHAT_CHAT_TEMPLATE_FILE="/data/public/machine-learning/models/vision-text/Qwen3.6-chat_template.jinja"`
  - `LCHAT_CHAT_TEMPLATE_KWARGS="{"enable_thinking": false}"`
  - `LCHAT_CTX_SIZE="240384"`
  - `LCHAT_DEVICE="BLAS"`
  - `LCHAT_EMBEDDING_ENABLED="false"`
  - `LCHAT_EXTRA_ARGS="--temp 0.6 --top-k 20 --repeat-penalty 1.1"`
  - `LCHAT_HOST="127.0.0.1"`
  - `LCHAT_MMPROJ=""`
  - `LCHAT_MODEL="/data/public/machine-learning/models/vision-text/Agents-A1-APEX-I-Compact.gguf"`
  - `LCHAT_MTP=""`
  - `LCHAT_N_CTX="12019"`
  - `LCHAT_N_GPU_LAYERS="0"`
  - `LCHAT_PARALLEL="2"`
  - `LCHAT_PORT="50080"`
  - `LCHAT_SERVE_EMBEDDINGS="false"`
  - `LCHAT_SIDECARS=""`
  - `LCHAT_SIDECAR_PORTMIRROR_CMD="bash -c 'if [ \"\${LMBD_ENABLED}\" = \"true\" ]; then exec socat TCP-LISTEN:\${LMBD_MIRROR_PORT:-50082},fork,reuseaddr TCP:\${LCHAT_HOST:-127.0.0.1}:\${LCHAT_PORT:-50080}; else exec sleep infinity; fi'"`
  - `LCHAT_SPECULATIVE="--spec-type ngram-simple --spec-ngram-simple-size-n 6 --spec-ngram-simple-size-m 4"`
  - `LCHAT_THREADS="4"`
  - `LCOMP_ALIAS="qwen-coder-fim"`
  - `LCOMP_CACHE_TYPE_K="q4_0"`
  - `LCOMP_CACHE_TYPE_V="q4_0"`
  - `LCOMP_CTX_SIZE="8192"`
  - `LCOMP_ENABLED="false"`
  - `LCOMP_EXTRA_ARGS=""`
  - `LCOMP_MODEL="/data/public/machine-learning/models/completion/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf"`
  - `LCOMP_PARALLEL="2"`
  - `LMBD_ALIAS="qwen3-embedding"`
  - `LMBD_CACHE_TYPE_K="q8_0"`
  - `LMBD_CACHE_TYPE_V="q8_0"`
  - `LMBD_CTX_SIZE="16384"`
  - `LMBD_ENABLED="false"`
  - `LMBD_EXTRA_ARGS="--flash-attn on"`
  - `LMBD_MIRROR_PORT="50082"`
  - `LMBD_MODEL="/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf"`
  - `LMBD_PARALLEL="2"`
  - `LMBD_UBATCH_SIZE="16384"`
- **Errors Count:** 0
- **Package Version:** `10154 (0e4a036223)`
- **Warmup (Phase 0):**
  - TTFT (Prefill):       582.41 ms
  - Prefill Speed:        36.06 tokens/sec
  - Generation Speed:     16.89 tokens/sec
- **Generation (Phase 2):**
  - Avg Completion Tokens: 493.0
  - Avg TTFT (Prefill):   41882.37 ms
  - Avg Prefill Speed:    35.50 tokens/sec
  - Avg Generation Speed: 12.00 tokens/sec
  - Avg Decode Time:      41.07 s
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
- **CPU Memory Used:** 2438.7 MB
- **Benchmark Running Time:** 29.39 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LMBD_ALIAS="qwen3-embedding"`
  - `LMBD_DEVICE="BLAS"`
  - `LMBD_ENGINE="llama"`
  - `LMBD_HOST="127.0.0.1"`
  - `LMBD_LLAMA_DEVICE="rocm0"`
  - `LMBD_LLAMA_EXTRA_ARGS=""`
  - `LMBD_LLAMA_KV_UNIFIED="false"`
  - `LMBD_LLAMA_MODEL="/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf"`
  - `LMBD_LLAMA_N_CTX="8192"`
  - `LMBD_LLAMA_N_GPU_LAYERS="999"`
  - `LMBD_LLAMA_N_UBATCH="1024"`
  - `LMBD_LLAMA_PARALLEL="1"`
  - `LMBD_LLAMA_THREADS="4"`
  - `LMBD_N_CTX="8192"`
  - `LMBD_N_GPU_LAYERS="0"`
  - `LMBD_PORT="50082"`
  - `LMBD_TEI_DEVICE="rocm:0"`
  - `LMBD_TEI_EXTRA_ARGS="--dtype float32"`
  - `LMBD_TEI_MAX_BATCH_TOKENS="49152"`
  - `LMBD_TEI_MAX_CONCURRENT="6"`
  - `LMBD_TEI_MODEL="/data/public/machine-learning/models/embedding/bge-m3"`
  - `PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"`
  - `TRUST_REMOTE_CODE="true"`
- **Errors Count:** 0
- **Package Version:** `10154 (0e4a036223)`
- **Metrics:**
  - Avg Time/Run:         291.36 s
  - Avg Throughput:       140.58 tokens/sec
  - Avg Chunk Latency:    3642.1 ms
  - Avg Chunk p50:        3621.1 ms
  - Avg Chunk p95:        3958.7 ms

#### Code Completion FIM (`local-chat` - tab completion)
- **Benchmark Test Name:** `completion_cpu-blas`
- **Device Setting:** `BLAS`
- **Special Setting:** `Layers: 0`
- **Model:** `qwen-coder-fim` (`qwen2.5-coder-1.5b-instruct-q4_k_m.gguf`)
- **Execution Target:** `CPU-BLAS`
- **GPU Memory Used:** 46.5 MB
- **CPU Memory Used:** 64.0 MB
- **Benchmark Running Time:** 17.45 s
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
  - `LCHAT_EXTRA_ARGS="--temp 0.6 --top-k 20 --repeat-penalty 1.1"`
  - `LCHAT_HOST="127.0.0.1"`
  - `LCHAT_MMPROJ="/data/public/machine-learning/models/vision-text/Agents-A1-APEX-I-Compact-mmproj.gguf"`
  - `LCHAT_MODEL="/data/public/machine-learning/models/vision-text/Agents-A1-APEX-I-Compact.gguf"`
  - `LCHAT_N_GPU_LAYERS="999"`
  - `LCHAT_PARALLEL="3"`
  - `LCHAT_PORT="50080"`
  - `LCHAT_SERVE_EMBEDDINGS="false"`
  - `LCHAT_SPECULATIVE="--spec-type ngram-simple --spec-ngram-simple-size-n 6 --spec-ngram-simple-size-m 4"`
  - `LCHAT_THREADS="4"`
  - `LCOMP_ALIAS="qwen-coder-fim"`
  - `LCOMP_CACHE_TYPE_K="q4_0"`
  - `LCOMP_CACHE_TYPE_V="q4_0"`
  - `LCOMP_CTX_SIZE="8192"`
  - `LCOMP_DEVICE="BLAS"`
  - `LCOMP_ENABLED="true"`
  - `LCOMP_MODEL="/data/public/machine-learning/models/completion/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf"`
  - `LCOMP_N_GPU_LAYERS="0"`
  - `LCOMP_PARALLEL="2"`
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
  - `LOCAL_SIDECARS=""`
  - `LOCAL_SIDECAR_PORTMIRROR_CMD="bash -c 'if [ \"\${LMBD_ENABLED}\" = \"true\" ]; then exec socat TCP-LISTEN:\${LMBD_MIRROR_PORT:-50082},fork,reuseaddr TCP:\${LCHAT_HOST:-127.0.0.1}:\${LCHAT_PORT:-50080}; else exec sleep infinity; fi'"`
- **Errors Count:** 0
- **Package Version:** `10154 (0e4a036223)`
- **Warmup (Phase 0):**
  - TTFT (Prefill):       37.54 ms
  - Generation Speed:     37.82 tokens/sec
- **Generation (Phase 2):**
  - Avg TTFT (Prefill):   13717.94 ms
  - Avg Prefill Speed:    80.19 tokens/sec
  - Avg Generation Speed: 30.64 tokens/sec
  - Avg Decode Time:      3.26 s

#### Document Reranking (`local-rerank`)
- **Benchmark Test Name:** `rerank_cpu-blas`
- **Device Setting:** `BLAS`
- **Special Setting:** `Layers: 99`
- **Model:** `qwen3-reranker` (`Qwen3-Reranker-0.6B.Q4_K_M.gguf`)
- **Execution Target:** `CPU-BLAS`
- **GPU Memory Used:** 0.1 MB
- **CPU Memory Used:** 4280.8 MB
- **Benchmark Running Time:** 14.94 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `HIP_VISIBLE_DEVICES=""`
  - `LRR_ALIAS="qwen3-reranker"`
  - `LRR_API_PATH="/v1/rerank"`
  - `LRR_DEVICE="BLAS"`
  - `LRR_ENGINE="llama"`
  - `LRR_HOST="127.0.0.1"`
  - `LRR_LLAMA_DEVICE="vulkan0"`
  - `LRR_LLAMA_EXTRA_ARGS=""`
  - `LRR_LLAMA_MODEL="/data/public/machine-learning/models/reranker/Qwen3-Reranker-0.6B.Q4_K_M.gguf"`
  - `LRR_LLAMA_N_CTX="12288"`
  - `LRR_LLAMA_N_GPU_LAYERS="999"`
  - `LRR_LLAMA_N_UBATCH="12288"`
  - `LRR_LLAMA_PARALLEL="2"`
  - `LRR_LLAMA_THREADS="4"`
  - `LRR_N_GPU_LAYERS="0"`
  - `LRR_PORT="50086"`
  - `LRR_TEI_DEVICE="rocm:0"`
  - `LRR_TEI_EXTRA_ARGS="--dtype bfloat16"`
  - `LRR_TEI_MAX_BATCH_TOKENS="8192"`
  - `LRR_TEI_MAX_CONCURRENT="4"`
  - `LRR_TEI_MODEL="/data/public/machine-learning/models/reranker/ettin-reranker-400m-v1"`
  - `PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"`
  - `TRUST_REMOTE_CODE="true"`
- **Errors Count:** 0
- **Package Version:** `10154 (0e4a036223)`
- **Metrics:**
  - Avg Reranking Time:   14795.03 ms
  - Avg Docs Throughput:  0.68 docs/sec
  - Avg Token Speed:      232.44 tokens/sec

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
  - `LSTT_ALIAS="whisper-1"`
  - `LSTT_DEVICE=""`
  - `LSTT_EXTRA_ARGS=""`
  - `LSTT_HOST="127.0.0.1"`
  - `LSTT_INFERENCE_PATH="/v1/audio/transcriptions"`
  - `LSTT_MODEL="/data/public/machine-learning/models/speech-to-text/ggml-large-v3-turbo-q5_0.bin"`
  - `LSTT_NO_GPU="true"`
  - `LSTT_PORT="50090"`
  - `LSTT_THREADS="8"`
- **Errors Count:** 0
- **Package Version:** `1.9.1 (080bbbe85)`
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
- **Package Version:** `master-797-5ef4a75-1-g2251699, commit 22516991`
- **Metrics:**
  - Avg Generation Time:  281.93 seconds

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

### RUNNING Configuration Details

#### Text Chat (`local-chat`)
- **Benchmark Test Name:** `chat_running`
- **Device Setting:** `running on host`
- **Special Setting:** `unknown`
- **Model:** `qwen3` (`Agents-A1-APEX-I-Compact`)
- **Execution Target:** `RUNNING`
- **GPU Memory Used:** -n.a.-
- **CPU Memory Used:** -n.a.-
- **Benchmark Running Time:** 27.44 s
- **Active Environment Settings:**
  - `GGML_VK_DISABLE_MMVQ="1"`
  - `LCHAT_ALIAS="qwen3"`
  - `LCHAT_CACHE_TYPE_K="q4_0"`
  - `LCHAT_CACHE_TYPE_V="q4_0"`
  - `LCHAT_CHAT_TEMPLATE_FILE="/data/public/machine-learning/models/vision-text/Qwen3.6-chat_template.jinja"`
  - `LCHAT_CHAT_TEMPLATE_KWARGS="{"enable_thinking": false}"`
  - `LCHAT_CTX_SIZE="240384"`
  - `LCHAT_DEVICE="vulkan1"`
  - `LCHAT_EXTRA_ARGS="--temp 0.6 --top-k 20 --repeat-penalty 1.1"`
  - `LCHAT_HOST="127.0.0.1"`
  - `LCHAT_MMPROJ=""`
  - `LCHAT_MODEL="/data/public/machine-learning/models/vision-text/Agents-A1-APEX-I-Compact.gguf"`
  - `LCHAT_MTP=""`
  - `LCHAT_N_GPU_LAYERS="999"`
  - `LCHAT_PARALLEL="2"`
  - `LCHAT_PORT="50080"`
  - `LCHAT_SIDECARS=""`
  - `LCHAT_SIDECAR_PORTMIRROR_CMD="bash -c 'if [ \"\${LMBD_ENABLED}\" = \"true\" ]; then exec socat TCP-LISTEN:\${LMBD_MIRROR_PORT:-50082},fork,reuseaddr TCP:\${LCHAT_HOST:-127.0.0.1}:\${LCHAT_PORT:-50080}; else exec sleep infinity; fi'"`
  - `LCHAT_SPECULATIVE="--spec-type ngram-simple --spec-ngram-simple-size-n 6 --spec-ngram-simple-size-m 4"`
  - `LCHAT_THREADS="4"`
  - `LCOMP_ALIAS="qwen-coder-fim"`
  - `LCOMP_CACHE_TYPE_K="q4_0"`
  - `LCOMP_CACHE_TYPE_V="q4_0"`
  - `LCOMP_CTX_SIZE="8192"`
  - `LCOMP_ENABLED="false"`
  - `LCOMP_EXTRA_ARGS=""`
  - `LCOMP_MODEL="/data/public/machine-learning/models/completion/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf"`
  - `LCOMP_PARALLEL="2"`
  - `LMBD_ALIAS="qwen3-embedding"`
  - `LMBD_CACHE_TYPE_K="q8_0"`
  - `LMBD_CACHE_TYPE_V="q8_0"`
  - `LMBD_CTX_SIZE="16384"`
  - `LMBD_ENABLED="false"`
  - `LMBD_EXTRA_ARGS="--flash-attn on"`
  - `LMBD_MIRROR_PORT="50082"`
  - `LMBD_MODEL="/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf"`
  - `LMBD_PARALLEL="2"`
  - `LMBD_UBATCH_SIZE="16384"`
- **Errors Count:** 0
- **Package Version:** `10154 (0e4a036223)`
- **Warmup (Phase 0):**
  - TTFT (Prefill):       73.19 ms
  - Prefill Speed:        286.92 tokens/sec
  - Generation Speed:     146.58 tokens/sec
- **Generation (Phase 2):**
  - Avg Completion Tokens: 1024.0
  - Avg TTFT (Prefill):   17578.88 ms
  - Avg Prefill Speed:    1766.61 tokens/sec
  - Avg Generation Speed: 106.95 tokens/sec
  - Avg Decode Time:      9.57 s
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
- **Benchmark Running Time:** 5.31 s
- **Active Environment Settings:**
  - `LMBD_ALIAS="qwen3-embedding"`
  - `LMBD_ENGINE="llama"`
  - `LMBD_HOST="127.0.0.1"`
  - `LMBD_LLAMA_DEVICE="rocm0"`
  - `LMBD_LLAMA_EXTRA_ARGS=""`
  - `LMBD_LLAMA_KV_UNIFIED="false"`
  - `LMBD_LLAMA_MODEL="/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf"`
  - `LMBD_LLAMA_N_CTX="8192"`
  - `LMBD_LLAMA_N_GPU_LAYERS="999"`
  - `LMBD_LLAMA_N_UBATCH="1024"`
  - `LMBD_LLAMA_PARALLEL="1"`
  - `LMBD_LLAMA_THREADS="4"`
  - `LMBD_PORT="50082"`
  - `LMBD_TEI_DEVICE="rocm:0"`
  - `LMBD_TEI_EXTRA_ARGS="--dtype float32"`
  - `LMBD_TEI_MAX_BATCH_TOKENS="49152"`
  - `LMBD_TEI_MAX_CONCURRENT="6"`
  - `LMBD_TEI_MODEL="/data/public/machine-learning/models/embedding/bge-m3"`
  - `PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"`
  - `TRUST_REMOTE_CODE="true"`
- **Errors Count:** 0
- **Package Version:** `10154 (0e4a036223)`
- **Metrics:**
  - Avg Time/Run:         5.04 s
  - Avg Throughput:       9024.01 tokens/sec
  - Avg Chunk Latency:    56.6 ms
  - Avg Chunk p50:        46.0 ms
  - Avg Chunk p95:        47.6 ms

#### Document Reranking (`local-rerank`)
- **Benchmark Test Name:** `rerank_running`
- **Device Setting:** `running on host`
- **Special Setting:** `unknown`
- **Model:** `qwen3-reranker` (`Qwen3-Reranker-0.6B.Q4_K_M.gguf`)
- **Execution Target:** `RUNNING`
- **GPU Memory Used:** -n.a.-
- **CPU Memory Used:** -n.a.-
- **Benchmark Running Time:** 6.51 s
- **Active Environment Settings:**
  - `LRR_ALIAS="qwen3-reranker"`
  - `LRR_API_PATH="/v1/rerank"`
  - `LRR_ENGINE="llama"`
  - `LRR_HOST="127.0.0.1"`
  - `LRR_LLAMA_DEVICE="vulkan0"`
  - `LRR_LLAMA_EXTRA_ARGS=""`
  - `LRR_LLAMA_MODEL="/data/public/machine-learning/models/reranker/Qwen3-Reranker-0.6B.Q4_K_M.gguf"`
  - `LRR_LLAMA_N_CTX="12288"`
  - `LRR_LLAMA_N_GPU_LAYERS="999"`
  - `LRR_LLAMA_N_UBATCH="12288"`
  - `LRR_LLAMA_PARALLEL="2"`
  - `LRR_LLAMA_THREADS="4"`
  - `LRR_PORT="50086"`
  - `LRR_TEI_DEVICE="rocm:0"`
  - `LRR_TEI_EXTRA_ARGS="--dtype bfloat16"`
  - `LRR_TEI_MAX_BATCH_TOKENS="8192"`
  - `LRR_TEI_MAX_CONCURRENT="4"`
  - `LRR_TEI_MODEL="/data/public/machine-learning/models/reranker/ettin-reranker-400m-v1"`
  - `PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"`
  - `TRUST_REMOTE_CODE="true"`
- **Errors Count:** 0
- **Package Version:** `10154 (0e4a036223)`
- **Metrics:**
  - Avg Reranking Time:   6339.59 ms
  - Avg Docs Throughput:  1.58 docs/sec
  - Avg Token Speed:      542.46 tokens/sec

#### Speech-to-Text (STT) (`local-speech-to-text`)
- **Benchmark Test Name:** `stt_running`
- **Device Setting:** `running on host`
- **Special Setting:** `unknown`
- **Model:** `whisper-1` (`ggml-large-v3-turbo-q5_0.bin`)
- **Execution Target:** `RUNNING`
- **GPU Memory Used:** -n.a.-
- **CPU Memory Used:** -n.a.-
- **Benchmark Running Time:** 8.01 s
- **Active Environment Settings:**
  - `CUDA_VISIBLE_DEVICES=""`
  - `LSTT_ALIAS="whisper-1"`
  - `LSTT_DEVICE="0"`
  - `LSTT_EXTRA_ARGS=""`
  - `LSTT_HOST="127.0.0.1"`
  - `LSTT_INFERENCE_PATH="/v1/audio/transcriptions"`
  - `LSTT_LANG="auto"`
  - `LSTT_MODEL="/data/public/machine-learning/models/speech-to-text/ggml-large-v3-turbo-q5_0.bin"`
  - `LSTT_PORT="50090"`
  - `LSTT_THREADS="8"`
- **Errors Count:** 0
- **Package Version:** `1.9.1 (080bbbe85)`
- **Metrics:**
  - Avg Transcribe Time:  7.77 seconds
  - Avg Real-Time Factor (RTF): 0.1726 (5.8x faster than real-time)

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Benchmark Test Name:** `tts_running`
- **Device Setting:** `running on host`
- **Special Setting:** `unknown`
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `RUNNING`
- **GPU Memory Used:** -n.a.-
- **CPU Memory Used:** -n.a.-
- **Benchmark Running Time:** 38.88 s
- **Active Environment Settings:**
  - `LTTS_DEVICE="none"`
  - `LTTS_EXTRA_ARGS="--language de"`
  - `LTTS_HOST="127.0.0.1"`
  - `LTTS_MODE="cpu"`
  - `LTTS_MODEL="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf"`
  - `LTTS_PORT="50095"`
  - `LTTS_THREADS="8"`
  - `LTTS_VOCODER="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-Tokenizer-12Hz-F16.gguf"`
- **Errors Count:** 0
- **Package Version:** `qwen3-tts version 0.1-main-0c8b2ba`
- **Metrics:**
  - Generated Audio Duration: 19.98 seconds
  - Avg Synthesis Time:   38.69 seconds
  - Avg Real-Time Factor (RTF): 1.9365
  - Avg Speed:            7.08 chars/sec

#### Image Generation (`local-image`)
- **Benchmark Test Name:** `image_running`
- **Device Setting:** `running on host`
- **Special Setting:** `unknown`
- **Model:** `z_image_turbo-Q8_0` (`z_image_turbo-Q8_0.gguf`)
- **Execution Target:** `RUNNING`
- **GPU Memory Used:** -n.a.-
- **CPU Memory Used:** -n.a.-
- **Benchmark Running Time:** 90.34 s
- **Active Environment Settings:**
  - `GGML_VK_MAX_NODES_PER_SUBMIT="20"`
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
- **Package Version:** `master-797-5ef4a75-1-g2251699, commit 22516991`
- **Metrics:**
  - Avg Generation Time:  90.16 seconds

