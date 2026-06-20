# Central VRAM Memory Map & Co-running Guide

This document aggregates detailed memory requirements and allocations for local AI models running on the AMD Radeon RX 7900 XTX GPU (**24,576 MiB** usable VRAM) and AMD Radeon Graphics (integrated iGPU sharing System RAM).

---

## Component Footprints

### Local LLM Service ([local-chat.sh](file:///home/wuxxin/agent-shared/code/agents-shared/assistants/local-chat.sh) / `llama-server`)
Serves chat and vision.

**Model Target:** `Qwen3.6-35B-A3B-APEX-I-Compact` (LLM: ~17.0 GiB GGUF, mmproj: ~861 MiB)

**Theoretical Footprint Breakdown:**
- **Model Weights & Compute (LLM + Vision):** ~19,259 MiB (LLM weights: ~17,408 MiB, mmproj: ~861 MiB, compute buffers: ~990 MiB)
- **KV Cache (q4_0 KV, parallel=3, slot n_ctx=30,000):** ~3,011 MiB
- **HIP Context Overhead:** ~600 MiB (ROCm driver context overhead)
- **Total Theoretical Footprint:** ~22,870 MiB

**Benchmarked Footprint (Active Memory Usage):**
- **Vulkan-Vulkan1 (dGPU):** **19,197.6 MiB** (active VRAM at `n_ctx=240,384`, parallel=3, generation speed: 111.94 t/s).
- **HIP-ROCm0 (dGPU):** **20,668.3 MiB** (active VRAM at `n_ctx=240,384`, parallel=3, generation speed: 65.73 t/s).
- **Vulkan-Vulkan0 (iGPU):** **14,468.3 MiB** (active VRAM at `n_ctx=48,076`, parallel=3, generation speed: 12.59 t/s).
- **CPU:** **1,168.7 MiB** VRAM, **21,392.5 MiB** System RAM (active at `n_ctx=12,019`, parallel=3, generation speed: 12.64 t/s).

---

### Local Embedding Service ([local-embedding.sh](file:///home/wuxxin/agent-shared/code/agents-shared/assistants/local-embedding.sh) / `llama-server`)
Serves text embeddings.

**Model Target:** `Qwen3-Embedding-0.6B-Q8_0.gguf` (~568 MiB on disk)

**Theoretical Footprint Breakdown (KV cache f16, per-slot n_ctx=8192):**
- **Model Weights:** ~568 MiB (Q8_0 GGUF file size)
- **KV Cache (f16):** ~224 MiB per parallel slot (`8192 × 2 × 8kv × 64dim × 28layers × 2B`)
- **Compute/Activation Buffers:** scales with `n_ubatch` (at ubatch=2048: ~several GiB across 28 layers)
- **HIP Context Overhead:** ~600 MiB (ROCm driver overhead)

**Benchmarked Footprint** *(measured with old default `LMBD_PARALLEL=4`; current default is `LMBD_PARALLEL=1`)*:
- **HIP-ROCm0 (dGPU):** **7,119.7 MiB** (active VRAM at `n_ctx=8,192`, throughput: 1,799.58 t/s).
- **Vulkan-Vulkan0 (iGPU):** **5,229.6 MiB** (active VRAM/System RAM at `n_ctx=8,192`, batch=2048, throughput: 493.77 t/s).
- **Vulkan-Vulkan1 (dGPU):** *Failed* (warmup/initialization hang under Vulkan driver).
- **CPU:** **~0.1 MiB** VRAM, **11,898.1 MiB** System RAM (throughput: 99.29 t/s).

---

### Local Rerank Service ([local-rerank.sh](file:///home/wuxxin/agent-shared/code/agents-shared/assistants/local-rerank.sh) / `llama-server`)
Serves document reranking.

**Model Target:** `Qwen3-Reranker-0.6B.Q4_K_M.gguf` (~450 MiB GGUF)

**Theoretical Footprint Breakdown:**
- **GPU Mode:** ~1,050 MiB (Weights/Compute: ~450 MiB + HIP overhead: ~600 MiB)
- **CPU Mode:** ~450 MiB System RAM

**Benchmarked Footprint:**
- **HIP-ROCm0 (dGPU):** **2,719.6 MiB** (active VRAM at `n_ctx=8,192`).
- **Vulkan-Vulkan0 (iGPU):** **1,574.7 MiB** (active VRAM at `n_ctx=8,192`).
- **Vulkan-Vulkan1 (dGPU):** *Failed* to start.
- **CPU:** **~0.1 MiB** VRAM, **2,716.7 MiB** System RAM.

---

### Local Speech-to-Text ([local-speech-to-text.sh](file:///home/wuxxin/agent-shared/code/agents-shared/assistants/local-speech-to-text.sh) / `whisper-server`)
Serves audio transcription.

**Model Target:** `ggml-large-v3-turbo-q5_0.bin` (~573.45 MiB GGUF)

**Theoretical Footprint Breakdown:**
- **Model Weights:** ~573.45 MiB
- **KV Caches:** ~49.81 MiB
- **Compute Buffers:** ~202.35 MiB
- **HIP Context Overhead:** ~600.00 MiB
- **Total STT GPU Footprint:** ~1,425.61 MiB

**Benchmarked Footprint:**
- **Vulkan-Vulkan1 (dGPU):** **828.0 MiB** VRAM, RTF: **0.0116** (86.2x speedup).
- **Vulkan-Vulkan0 (iGPU):** **808.8 MiB** VRAM, RTF: **0.1224** (8.2x speedup).
- **HIP-ROCm0 (dGPU):** **1,264.3 MiB** VRAM, RTF: *FAIL* (Garbled output).
- **CPU:** **~0.1 MiB** VRAM, **1,102.3 MiB** System RAM, RTF: **0.3032** (3.3x speedup).

---

### Local Text-to-Speech ([local-text-to-speech.sh](file:///home/wuxxin/agent-shared/code/agents-shared/assistants/local-text-to-speech.sh) / `qwen3-tts-server`)
Serves voice synthesis.

The memory profile of the Text-to-Speech service depends significantly on the configured **`LTTS_MODE`** preset:

#### Variant: 0.6B Model (CustomVoice/Base) + Vocoder

**Model Target:** `Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf` (~1,264 MiB GGUF) + Vocoder `Qwen3-TTS-Tokenizer-12Hz-F16.gguf` (~325 MiB GGUF)

**Theoretical Footprint Breakdown (`gpu` Mode):**
- **Talker Model weights (Q8_0):** ~1,264 MiB (1.23 GiB GGUF file)
- **Vocoder weights (F16):** ~325 MiB (325 MiB GGUF file)
- **KV Cache, Compute buffers, and launch overhead:** ~1,378 MiB
- **HIP Context Runtime Overhead:** ~600 MiB
- **Total Theoretical GPU Footprint:** ~3,567 MiB

**Benchmarked Footprint (0.6B Variant):**
- **Vulkan-Vulkan1 (`gpu`):** **3,399.8 MiB** VRAM, RTF: **0.3272** (41.91 chars/s).
- **Vulkan-Vulkan1 (`hybrid`):** **3,289.4 MiB** VRAM, RTF: **0.3264** (45.10 chars/s).
- **HIP-ROCm0 (`gpu`):** **3,585.8 MiB** VRAM, RTF: **0.9190** (15.95 chars/s).
- **HIP-ROCm0 (`hybrid`):** **3,645.8 MiB** VRAM, RTF: **0.9215** (15.25 chars/s).
- **Vulkan-Vulkan0 (`gpu`):** **3,352.5 MiB** VRAM, RTF: **2.4535** (5.75 chars/s).
- **Vulkan-Vulkan0 (`hybrid`):** **3,333.5 MiB** VRAM, RTF: **2.4484** (5.74 chars/s).
- **CPU (`cpu`):** **~0.1 MiB** VRAM, **2,985.3 MiB** System RAM, RTF: **1.6372** (8.58 chars/s).

#### Variant: 1.7B Model (CustomVoice/Base) + Vocoder

| Preset / Mode | Idle GPU VRAM | Active GPU VRAM | System RAM | Notes |
|---|---|---|---|---|
| **`gpu`** | ~600 MiB | ~4,769 MiB | ~967 MiB | Runs on GPU; holds all weights warm. (RTF 3.88x) |
| **`hybrid`** | ~600 MiB | ~2,104 MiB | ~3,523 MiB | **Recommended.** Code Gen on CPU, Vocoder on GPU. (RTF 2.92x) |
| **`cpu`** | 0 MiB | 0 MiB | ~4,415 MiB | Runs completely on CPU (8 threads). (RTF 3.39x) |

*Detailed breakdown for `gpu` (1.7B CustomVoice):*
- Talker Model weights (Q8_0): ~2,322 MiB (2.27 GiB GGUF file)
- Vocoder weights (F16): ~325 MiB (325 MiB GGUF file)
- KV Cache, Compute buffers, and launch overhead: ~1,522 MiB
- HIP Context Runtime Overhead: ~600 MiB

---

### Local Image Service ([local-image.sh](file:///home/wuxxin/agent-shared/code/agents-shared/assistants/local-image.sh) / `sd-server`)
Serves image generation using stable diffusion.

**Model Target:** `z_image_turbo-Q8_0.gguf` (~Diffusion) + `ae.safetensors` (~VAE) + `Qwen3-4B-Q4_K_M.gguf` (~Text Encoder LLM)

**Benchmarked Footprint:**
- **HIP-ROCm0 (dGPU):** **10,758.6 MiB** VRAM, Avg Gen Time: **6.18 s** (8 steps).
- **Vulkan-Vulkan1 (dGPU):** **9,879.0 MiB** VRAM, Avg Gen Time: **6.61 s** (8 steps).
- **Vulkan-Vulkan0 (iGPU):** **6,368.2 MiB** VRAM, Avg Gen Time: **93.74 s** (special setting: `vulkan0,te=cpu`).
- **CPU:** **~0.1 MiB** VRAM, **10,141.2 MiB** System RAM, Avg Gen Time: **269.95 s** (8 steps).

---

## Combined Co-running Scenario

Here we map VRAM usage for running **Inference** (LLM + Vision), **Embedding**, **Reranking**, **Speech-to-Text**, **Text-to-Speech** and **Image** services concurrently on one system using the dgpu, the igpu and the cpu.

To maximize VRAM efficiency, we route the **Local-LLM Service** (Chat/Vision) on the dGPU using Vulkan with `max_ctx: 240384`, and route **Speech-to-Text** to the dGPU (`vulkan1`). **Local-Rerank Service**, **Local Image Service** (using the CPU text encoder offload), and **Text-To-Speech Service** (hybrid mode) are routed to the iGPU (`vulkan0`). **Local-Embedding Service** runs on the CPU.

### Co-running Allocation (Vulkan Heterogeneous Mode)

| Service / Component | Device/Backend | VRAM (dGPU Vulkan1) | VRAM (iGPU Vulkan0) | System RAM | Notes |
|---|---|---|---|---|---|
| **Local-LLM Service** | Vulkan1 (dGPU) | **19,198 MiB** | 0 MiB | ~1,359 MiB | Active with `n_ctx=240,384`, parallel=3 |
| **Speech-to-Text** | Vulkan1 (dGPU) | **828 MiB** | 0 MiB | ~128 MiB | Active Whisper transcription |
| **Local-Embedding Service** | CPU | 0 MiB | 0 MiB | **~11,898 MiB** | Offloaded to CPU due to iGPU allocation failure |
| **Local-Rerank Service** | Vulkan0 (iGPU) | 0 MiB | **1,575 MiB** | ~248 MiB | Active document reranking |
| **Local Text-to-Speech** | Vulkan0 (iGPU) | 0 MiB | **3,334 MiB** | ~681 MiB | Hybrid mode (Vocoder on iGPU, CodeGen on CPU) |
| **Local Image Service** | Vulkan0 (iGPU) | 0 MiB | **6,368 MiB** | ~3,808 MiB | `vulkan0,te=cpu` preset |
| **Total Allocation** | - | **20,026 MiB** | **11,277 MiB** | **~18,122 MiB** | |

**Status:**
- **dGPU (RX 7900 XTX):** **Safe**. Fits within 24,576 MiB usable VRAM. Remaining headroom: **4,550 MiB** free VRAM.
- **iGPU (Radeon Graphics):** **Safe**. Fits within 16 GiB shared RAM. Remaining headroom: **5,107 MiB** free VRAM.
