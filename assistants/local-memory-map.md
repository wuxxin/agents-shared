# Central VRAM Memory Map & Co-running Guide

This document aggregates detailed memory requirements and allocations for local AI models running on the AMD Radeon Pro W6800 GPU (**30,704 MiB** usable VRAM).

## Component Footprints

### Local Inference (`local-inference.sh` / `llama-server`)

| Component | GPU VRAM | Details |
|---|---|---|
| **MoE LLM** (Qwen3.6-35B-A3B-APEX-I-Compact) | ~17,408 MiB | 17 GiB GGUF file |
| **MoE mmproj** (Vision projector) | ~861 MiB | 861 MiB GGUF file |
| **Embedding** (Qwen3-Embedding-0.6B Q8_0) | ~700 MiB | 610 MiB GGUF file |
| **Reranker** (Qwen3-Reranker-0.6B Q4_K_M) | ~450 MiB | 379 MiB GGUF file |
| **Compute Overhead** (per LLM) | ~990 MiB | Scheduler/Activation buffers |
| **KV Cache** (q4_0 KV, parallel=2, n_ctx=240,000) | ~8,031 MiB | ~35.1 bytes/token allocation |
| **Total Footprint** | |

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


