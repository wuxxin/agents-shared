# Central VRAM Memory Map & Co-running Guide

This document aggregates detailed memory requirements and allocations for local AI models running on the AMD Radeon Pro W6800 GPU (**30,704 MiB** usable VRAM).

## Component Footprints

### Local Inference (`local-inference.sh` / `llama-server`)
Managed as three separate services (Chat, Embedding, Reranking) to allow independent startup/shutdown and resource management.

| Service / Component | GPU VRAM | Details |
|---|---|---|
| **Local-Chat Service** (LLM: Qwen3.6-35B-A3B) | ~19,259 MiB | Weights (~17,408 MiB) + mmproj (~861 MiB) + Compute (~990 MiB) |
| **local-embeddings Service** (Qwen3-Embedding-0.6B) | ~700 MiB | Weights/Compute for embedding |
| **Local-Rerank Service** (Qwen3-Reranker-0.6B) | ~450 MiB | Weights/Compute for reranking |
| **KV Cache** (q4_0 KV, parallel=2, n_ctx=240,000) | ~8,031 MiB | LLM KV cache allocation |
| **HIP Context Overhead** (3 processes) | ~1,800 MiB | ~600 MiB overhead per running daemon |
| **Total Inference Footprint** | **~30,240 MiB** | Run simultaneously |

---

### Local Speech-to-Text (`local-speech-to-text.sh` / `whisper-server`)

Model Target: `ggml-large-v3-turbo-q5_0.bin`

| Component | GPU VRAM |
|---|---|
| Model Weights | ~573.45 MiB |
| KV Caches | ~49.81 MiB |
| Compute Buffers | ~202.35 MiB |
| HIP Context Runtime Overhead | ~600.00 MiB |
| **Total STT Footprint** | **~1,425.61 MiB (~1.4 GiB)** |

---

### Local Text-to-Speech (`local-text-to-speech.sh` / `qwen3-tts-server`)

The memory profile of the Text-to-Speech service depends significantly on the configured **`LTTS_MODE`** preset:

#### Variant: 0.6B Model (CustomVoice/Base) + Vocoder

| Preset / Mode | Idle GPU VRAM | Active GPU VRAM | System RAM | Notes |
|---|---|---|---|---|
| **`gpu+max-throughput`** | ~2,489 MiB | ~2,489 MiB | ~1.0 GiB | Holds all weights warm in GPU memory (fastest). |
| **`gpu+min.vram`** | ~600 MiB | ~2,489 MiB | ~2.0 GiB | Releases weights when idle; retains only HIP context runtime. |
| **`cpu-only`** | 0 MiB | 0 MiB | ~2.0 GiB | Bypasses GPU completely; runs tensors on CPU. |

*Detailed breakdown for `gpu+max-throughput` (0.6B):*
- Talker Model weights (Q8_0): ~1,264 MiB (1.23 GiB GGUF file)
- Vocoder weights (F16): ~325 MiB (325 MiB GGUF file)
- KV Cache & Compute buffers: ~300 MiB
- HIP Context Runtime Overhead: ~600 MiB

#### Variant: 1.7B Model (CustomVoice/Base) + Vocoder

| Preset / Mode | Idle GPU VRAM | Active GPU VRAM | System RAM | Notes |
|---|---|---|---|---|
| **`gpu+max-throughput`** | ~3,647 MiB | ~3,647 MiB | ~1.5 GiB | Holds all weights warm in GPU memory (fastest). |
| **`gpu+min.vram`** | ~600 MiB | ~3,647 MiB | ~3.0 GiB | Releases weights when idle; retains only HIP context runtime. |
| **`cpu-only`** | 0 MiB | 0 MiB | ~3.0 GiB | Bypasses GPU completely; runs tensors on CPU. |

*Detailed breakdown for `gpu+max-throughput` (1.7B):*
- Talker Model weights (Q8_0): ~2,322 MiB (2.27 GiB GGUF file)
- Vocoder weights (F16): ~325 MiB (325 MiB GGUF file)
- KV Cache & Compute buffers: ~400 MiB
- HIP Context Runtime Overhead: ~600 MiB


---

## Combined Co-running Scenario

Here we map VRAM usage for running **Inference** (MoE LLM + Vision), **Speech-to-Text**, and **Text-to-Speech** services concurrently on a single card (30,704 MiB usable VRAM limit).

### MoE LLM (with Vision) + STT + TTS (0.6B)

This setup uses the Mixture-of-Experts LLM with vision enabled,  Embedding, Reranking Whisper STT, and Qwen3-TTS 0.6B.

- **Required VRAM**:
  - MoE LLM + Vision weights , Embedding, Reranking & compute: **20,409 MiB**
  - LLM KV Cache (n_ctx = 240,000): **8,031 MiB**
  - Speech-to-Text (Whisper): **1,426 MiB**
  - Text-to-Speech (qwen3-tts): 
- **Status**: 


