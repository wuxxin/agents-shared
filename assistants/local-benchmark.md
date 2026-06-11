# LLM Caching Optimization Benchmarks

**Benchmark Run Time:** `2026-06-11 02:06:57`

## Local Inference Services Benchmarks

We ran local benchmarks for text embedding, text-to-speech (TTS), speech-to-text (STT), and document reranking on the AMD Radeon Pro W6800 hardware target. All services run inside isolated sandboxed environments.

### 📊 Performance Comparison Matrix

#### Text Chat (`local-llm-ggml`)
| Configuration | Test Name | Device Setting | Special Setting | Avg Chat TTFT | Avg Chat Prefill | Chat TTFT (Warmup) | Chat Gen Speed | Avg Chat Gen | Chat GPU Mem | Chat CPU Mem |
|---|---|---|---|---|---|---|---|---|---|---|
| **HIP** | chat_hip | ROCm0 | Layers: 999 | 27709.08 ms | 1120.25 t/s | 56.06 ms | 73.59 t/s | 43.96 t/s | 14520.0 MB | 1200.0 MB |
| **Vulkan** | chat_vulkan | Vulkan0 | Layers: 999 | 34341.01 ms | 903.90 t/s | 172.30 ms | 80.63 t/s | 71.79 t/s | 19226.4 MB | 68.9 MB |
| **CPU** | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |

#### Text Embedding (`local-embedding`)
| Configuration | Test Name | Device Setting | Special Setting | Embedding Throughput | Embedding Latency (Avg) | Embedding GPU Mem | Embedding CPU Mem |
|---|---|---|---|---|---|---|---|
| **HIP** | embedding_hip | ROCm0 | Layers: 999 | 4310.90 t/s | 1757.6 ms | 6637.6 MB | 9992.0 MB |
| **Vulkan** | embedding_vulkan | Vulkan0 | Layers: 999 | 921.27 t/s | 8224.2 ms | 2351.1 MB | 15105.4 MB |
| **CPU** | embedding_cpu | BLAS | Layers: 0 | 1115.40 t/s | 6792.8 ms | 0.0 MB | 2500.0 MB |

#### Document Reranking (`local-rerank`)
| Configuration | Test Name | Device Setting | Special Setting | Avg Reranking Time | Avg Token Speed | Avg Docs Throughput | GPU Mem | CPU Mem |
|---|---|---|---|---|---|---|---|---|
| **HIP** | rerank_hip | ROCm0 | Layers: 99 | 25761.59 ms | 133.49 tokens/s | 0.39 docs/s | 680.0 MB | 250.0 MB |
| **Vulkan** | rerank_vulkan | Vulkan0 | Layers: 99 | 933.74 ms | 3683.05 tokens/s | 10.71 docs/s | 1581.1 MB | 245.9 MB |
| **CPU** | rerank_cpu | BLAS | Layers: 0 | 11961.32 ms | 287.51 tokens/s | 0.84 docs/s | 4.5 MB | 2715.7 MB |

#### Speech-to-Text (STT) (`local-speech-to-text`)
| Configuration | Test Name | Device Setting | Special Setting | Avg Transcribe Time | Avg Real-Time Factor (RTF) | Speedup vs Real-time | GPU Mem | CPU Mem |
|---|---|---|---|---|---|---|---|---|
| **HIP** | stt_hip | 0 | Use GPU | 1.45 s | 0.0321 | 31.2x | 1820.0 MB | 450.0 MB |
| **Vulkan** | stt_vulkan | 0 | Use GPU | 0.75 s | 0.0167 | 59.9x | 1113.4 MB | 344.7 MB |
| **CPU** | stt_cpu | Default | No GPU | 14.86 s | 0.3302 | 3.0x | 0.0 MB | 1101.6 MB |

#### Text-to-Speech (TTS) (`local-text-to-speech`)
| Configuration | Test Name | Device Setting | Special Setting | Avg Synthesis Time | Avg Real-Time Factor (RTF) | Speed (chars/s) | GPU Mem | CPU Mem |
|---|---|---|---|---|---|---|---|---|
| **HIP** | tts_hip | hip | mode: gpu | 23.47 s | 1.4914 | 11.67 chars/s | 2240.0 MB | 300.0 MB |
| **Vulkan** | tts_vulkan | Default | mode: gpu | 39.30 s | 2.2669 | 6.97 chars/s | 3347.5 MB | 943.0 MB |
| **CPU** | tts_cpu | Default | mode: cpu-only | 34.30 s | 2.1046 | 7.99 chars/s | 0.0 MB | 2790.4 MB |
| **Special (Hybrid)** | tts_special-hybrid | Default | mode: hybrid | 26.74 s | 1.5790 | 10.25 chars/s | 1799.4 MB | 2344.2 MB |
| **Special (Low-Mem)** | tts_special-gpu-low-mem | Default | mode: gpu-min-vram | 32.93 s | 2.2907 | 8.32 chars/s | 273.8 MB | 438.7 MB |

---

### ⚙️ Detailed Configuration Reports

### CPU Configuration Details

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
- **GPU Memory Used:** 4.5 MB
- **CPU Memory Used:** 2715.7 MB
- **Benchmark Running Time:** 12.05 s
- **Active Environment Settings:**
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
  - Avg Reranking Time:   11961.32 ms
  - Avg Docs Throughput:  0.84 docs/sec
  - Avg Token Speed:      287.51 tokens/sec

#### Speech-to-Text (STT) (`local-speech-to-text`)
- **Benchmark Test Name:** `stt_cpu`
- **Device Setting:** `Default`
- **Special Setting:** `No GPU`
- **Model:** `whisper-1` (`ggml-large-v3-turbo-q5_0.bin`)
- **Execution Target:** `CPU`
- **GPU Memory Used:** 0.0 MB
- **CPU Memory Used:** 1101.6 MB
- **Benchmark Running Time:** 15.00 s
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
- **Metrics:**
  - Avg Transcribe Time:  14.86 seconds
  - Avg Real-Time Factor (RTF): 0.3302 (3.0x faster than real-time)

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Benchmark Test Name:** `tts_cpu`
- **Device Setting:** `Default`
- **Special Setting:** `mode: cpu-only`
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `CPU`
- **GPU Memory Used:** 0.0 MB
- **CPU Memory Used:** 2790.4 MB
- **Benchmark Running Time:** 34.39 s
- **Active Environment Settings:**
  - `LTTS_DEVICE=""`
  - `LTTS_EXTRA_ARGS=""`
  - `LTTS_HOST="127.0.0.1"`
  - `LTTS_MODE="cpu-only"`
  - `LTTS_MODEL="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf"`
  - `LTTS_PORT="50095"`
  - `LTTS_THREADS="4"`
  - `LTTS_VOCODER="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-Tokenizer-12Hz-F16.gguf"`
- **Metrics:**
  - Generated Audio Duration: 16.30 seconds
  - Avg Synthesis Time:   34.30 seconds
  - Avg Real-Time Factor (RTF): 2.1046
  - Avg Speed:            7.99 chars/sec

### HIP Configuration Details

#### Text Chat (`local-llm-ggml`)
- **Benchmark Test Name:** `chat_hip`
- **Device Setting:** `ROCm0`
- **Special Setting:** `Layers: 999`
- **Model:** `qwen3` (`Qwen3.6-35B-A3B-APEX-I-Compact`)
- **Execution Target:** `HIP`
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
- **Benchmark Test Name:** `embedding_hip`
- **Device Setting:** `ROCm0`
- **Special Setting:** `Layers: 999`
- **Model:** `qwen3-embedding` (`Qwen3-Embedding-0.6B-Q8_0.gguf`)
- **Execution Target:** `HIP`
- **GPU Memory Used:** 6637.6 MB
- **CPU Memory Used:** 9992.0 MB
- **Benchmark Running Time:** 15.85 s
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
  - Avg Time/Run:         10.55 s
  - Avg Throughput:       4310.90 tokens/sec
  - Avg Chunk Latency:    1757.6 ms
  - Avg Chunk p50:        1788.5 ms
  - Avg Chunk p95:        2521.1 ms

#### Document Reranking (`local-rerank`)
- **Benchmark Test Name:** `rerank_hip`
- **Device Setting:** `ROCm0`
- **Special Setting:** `Layers: 99`
- **Model:** `qwen3-reranker` (`Qwen3-Reranker-0.6B.Q4_K_M.gguf`)
- **Execution Target:** `HIP`
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
- **Benchmark Test Name:** `stt_hip`
- **Device Setting:** `0`
- **Special Setting:** `Use GPU`
- **Model:** `whisper-1` (`ggml-large-v3-turbo-q5_0.bin`)
- **Execution Target:** `HIP`
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
- **Benchmark Test Name:** `tts_hip`
- **Device Setting:** `hip`
- **Special Setting:** `mode: gpu`
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `HIP`
- **GPU Memory Used:** 2240.0 MB
- **CPU Memory Used:** 300.0 MB
- **Benchmark Running Time:** 25.10 s
- **Active Environment Settings:**
  - `LTTS_DEVICE="hip"`
  - `LTTS_MODE="gpu"`
- **Metrics:**
  - Generated Audio Duration: 15.74 seconds
  - Avg Synthesis Time:   23.47 seconds
  - Avg Real-Time Factor (RTF): 1.4914
  - Avg Speed:            11.67 chars/sec

### SPECIAL (GPU-LOW-MEM) Configuration Details

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Benchmark Test Name:** `tts_special-gpu-low-mem`
- **Device Setting:** `Default`
- **Special Setting:** `mode: gpu-min-vram`
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `SPECIAL (GPU-LOW-MEM)`
- **GPU Memory Used:** 273.8 MB
- **CPU Memory Used:** 438.7 MB
- **Benchmark Running Time:** 33.02 s
- **Active Environment Settings:**
  - `LTTS_DEVICE=""`
  - `LTTS_EXTRA_ARGS=""`
  - `LTTS_HOST="127.0.0.1"`
  - `LTTS_MODE="gpu-min-vram"`
  - `LTTS_MODEL="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf"`
  - `LTTS_PORT="50095"`
  - `LTTS_THREADS="4"`
  - `LTTS_VOCODER="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-Tokenizer-12Hz-F16.gguf"`
- **Metrics:**
  - Generated Audio Duration: 14.38 seconds
  - Avg Synthesis Time:   32.93 seconds
  - Avg Real-Time Factor (RTF): 2.2907
  - Avg Speed:            8.32 chars/sec

### SPECIAL (HYBRID) Configuration Details

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Benchmark Test Name:** `tts_special-hybrid`
- **Device Setting:** `Default`
- **Special Setting:** `mode: hybrid`
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `SPECIAL (HYBRID)`
- **GPU Memory Used:** 1799.4 MB
- **CPU Memory Used:** 2344.2 MB
- **Benchmark Running Time:** 26.84 s
- **Active Environment Settings:**
  - `LTTS_DEVICE=""`
  - `LTTS_EXTRA_ARGS=""`
  - `LTTS_HOST="127.0.0.1"`
  - `LTTS_MODE="hybrid"`
  - `LTTS_MODEL="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf"`
  - `LTTS_PORT="50095"`
  - `LTTS_THREADS="4"`
  - `LTTS_VOCODER="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-Tokenizer-12Hz-F16.gguf"`
- **Metrics:**
  - Generated Audio Duration: 16.94 seconds
  - Avg Synthesis Time:   26.74 seconds
  - Avg Real-Time Factor (RTF): 1.5790
  - Avg Speed:            10.25 chars/sec

### VULKAN Configuration Details

#### Text Chat (`local-llm-ggml`)
- **Benchmark Test Name:** `chat_vulkan`
- **Device Setting:** `Vulkan0`
- **Special Setting:** `Layers: 999`
- **Model:** `qwen3` (`Qwen3.6-35B-A3B-APEX-I-Compact`)
- **Execution Target:** `VULKAN`
- **GPU Memory Used:** 19226.4 MB
- **CPU Memory Used:** 68.9 MB
- **Benchmark Running Time:** 55.22 s
- **Active Environment Settings:**
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
  - TTFT (Prefill):       172.30 ms
  - Prefill Speed:        110.27 tokens/sec
  - Generation Speed:     80.63 tokens/sec
- **Generation (Phase 2):**
  - Avg Completion Tokens: 600.0
  - Avg TTFT (Prefill):   34341.01 ms
  - Avg Prefill Speed:    903.90 tokens/sec
  - Avg Generation Speed: 71.79 tokens/sec
  - Avg Decode Time:      8.36 s

#### Text Embedding (`local-embedding`)
- **Benchmark Test Name:** `embedding_vulkan`
- **Device Setting:** `Vulkan0`
- **Special Setting:** `Layers: 999`
- **Model:** `qwen3-embedding` (`Qwen3-Embedding-0.6B-Q8_0.gguf`)
- **Execution Target:** `VULKAN`
- **GPU Memory Used:** 2351.1 MB
- **CPU Memory Used:** 15105.4 MB
- **Benchmark Running Time:** 54.53 s
- **Active Environment Settings:**
  - `EMBED_ALIAS="qwen3-embedding"`
  - `EMBED_DEVICE="Vulkan0"`
  - `EMBED_EXTRA_ARGS=""`
  - `EMBED_HOST="127.0.0.1"`
  - `EMBED_MODEL="/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf"`
  - `EMBED_N_CTX="8192"`
  - `EMBED_N_GPU_LAYERS="999"`
  - `EMBED_PORT="50082"`
  - `EMBED_THREADS="4"`
- **Metrics:**
  - Avg Time/Run:         49.35 s
  - Avg Throughput:       921.27 tokens/sec
  - Avg Chunk Latency:    8224.2 ms
  - Avg Chunk p50:        8562.8 ms
  - Avg Chunk p95:        12172.1 ms

#### Document Reranking (`local-rerank`)
- **Benchmark Test Name:** `rerank_vulkan`
- **Device Setting:** `Vulkan0`
- **Special Setting:** `Layers: 99`
- **Model:** `qwen3-reranker` (`Qwen3-Reranker-0.6B.Q4_K_M.gguf`)
- **Execution Target:** `VULKAN`
- **GPU Memory Used:** 1581.1 MB
- **CPU Memory Used:** 245.9 MB
- **Benchmark Running Time:** 1.02 s
- **Active Environment Settings:**
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
  - Avg Reranking Time:   933.74 ms
  - Avg Docs Throughput:  10.71 docs/sec
  - Avg Token Speed:      3683.05 tokens/sec

#### Speech-to-Text (STT) (`local-speech-to-text`)
- **Benchmark Test Name:** `stt_vulkan`
- **Device Setting:** `0`
- **Special Setting:** `Use GPU`
- **Model:** `whisper-1` (`ggml-large-v3-turbo-q5_0.bin`)
- **Execution Target:** `VULKAN`
- **GPU Memory Used:** 1113.4 MB
- **CPU Memory Used:** 344.7 MB
- **Benchmark Running Time:** 0.90 s
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
  - Avg Transcribe Time:  0.75 seconds
  - Avg Real-Time Factor (RTF): 0.0167 (59.9x faster than real-time)

#### Text-to-Speech (TTS) (`local-text-to-speech`)
- **Benchmark Test Name:** `tts_vulkan`
- **Device Setting:** `Default`
- **Special Setting:** `mode: gpu`
- **Model:** `qwen3-tts` (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **Execution Target:** `VULKAN`
- **GPU Memory Used:** 3347.5 MB
- **CPU Memory Used:** 943.0 MB
- **Benchmark Running Time:** 39.39 s
- **Active Environment Settings:**
  - `LTTS_DEVICE=""`
  - `LTTS_EXTRA_ARGS=""`
  - `LTTS_HOST="127.0.0.1"`
  - `LTTS_MODE="gpu"`
  - `LTTS_MODEL="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf"`
  - `LTTS_PORT="50095"`
  - `LTTS_THREADS="4"`
  - `LTTS_VOCODER="/data/public/machine-learning/models/text-to-speech/Qwen3-TTS-Tokenizer-12Hz-F16.gguf"`
- **Metrics:**
  - Generated Audio Duration: 17.34 seconds
  - Avg Synthesis Time:   39.30 seconds
  - Avg Real-Time Factor (RTF): 2.2669
  - Avg Speed:            6.97 chars/sec

