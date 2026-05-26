# Central VRAM Memory Map & Co-running Guide

This document aggregates detailed memory requirements and allocations for local AI models running on the AMD Radeon Pro W6800 GPU (**30,704 MiB** usable VRAM).

## Component Footprints

### Local Inference (`local-inference.sh` / `llama-server`)
Managed as three separate services (Chat, Embedding, Reranking) to allow independent startup/shutdown and resource management.

| Service / Component | GPU VRAM | Details |
|---|---|---|
| **Local-Chat Service** (LLM: Qwen3.6-35B-A3B) | ~19,259 MiB | Weights (~17,408 MiB) + mmproj (~861 MiB) + Compute (~990 MiB) |
| **KV Cache** (q4_0 KV, parallel=2, n_ctx=240,000) | ~8,031 MiB | LLM KV cache allocation |
| **local-Embeddings Service** (Qwen3-Embedding-0.6B) | ~700 MiB | Weights/Compute for embedding |
| **Local-Rerank Service** (Qwen3-Reranker-0.6B) | ~450 MiB | Weights/Compute for reranking |
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
| **`gpu`** | ~600 MiB | ~3,567 MiB | ~952 MiB | Runs on GPU; holds all weights warm. (RTF 2.28x) |
| **`gpu-min-vram`** | ~600 MiB | ~2,083 MiB | ~951 MiB | Streams weights lazily; releases model VRAM when idle. (RTF 2.27x) |
| **`hybrid`** | ~600 MiB | ~2,194 MiB | ~2,447 MiB | **Recommended.** Code Gen on CPU, Vocoder on GPU. (RTF 1.11x) |
| **`cpu-only`** | 0 MiB | 0 MiB | ~2,965 MiB | Runs completely on CPU (8 threads). (RTF 1.58x) |

*Detailed breakdown for `gpu` (0.6B CustomVoice):*
- Talker Model weights (Q8_0): ~1,264 MiB (1.23 GiB GGUF file)
- Vocoder weights (F16): ~325 MiB (325 MiB GGUF file)
- KV Cache, Compute buffers, and launch overhead: ~1,378 MiB
- HIP Context Runtime Overhead: ~600 MiB

#### Variant: 1.7B Model (CustomVoice/Base) + Vocoder

| Preset / Mode | Idle GPU VRAM | Active GPU VRAM | System RAM | Notes |
|---|---|---|---|---|
| **`gpu`** | ~600 MiB | ~4,769 MiB | ~967 MiB | Runs on GPU; holds all weights warm. (RTF 3.88x) |
| **`gpu-min-vram`** | ~600 MiB | ~2,897 MiB | ~972 MiB | Streams weights lazily; releases model VRAM when idle. (RTF 3.89x) |
| **`hybrid`** | ~600 MiB | ~2,104 MiB | ~3,523 MiB | **Recommended.** Code Gen on CPU, Vocoder on GPU. (RTF 2.92x) |
| **`cpu-only`** | 0 MiB | 0 MiB | ~4,415 MiB | Runs completely on CPU (8 threads). (RTF 3.39x) |

*Detailed breakdown for `gpu` (1.7B CustomVoice):*
- Talker Model weights (Q8_0): ~2,322 MiB (2.27 GiB GGUF file)
- Vocoder weights (F16): ~325 MiB (325 MiB GGUF file)
- KV Cache, Compute buffers, and launch overhead: ~1,522 MiB
- HIP Context Runtime Overhead: ~600 MiB

---

## Combined Co-running Scenario

Here we map VRAM usage for running **Inference** (MoE LLM + Vision), **Speech-to-Text**, and **Text-to-Speech** services concurrently on a single card (30,704 MiB usable VRAM limit).

### Baseline Allocation (LLM + STT)
- **Local-Chat (MoE LLM + Vision, Embedding, Reranking)**: **20,409 MiB**
- **LLM KV Cache** (n_ctx = 240,000): **8,031 MiB**
- **Speech-to-Text (Whisper)**: **1,426 MiB**
- **Subtotal (Baseline)**: **29,866 MiB**
- **Remaining Usable VRAM**: **838 MiB**

---

### Scenario A: Full Co-Running with TTS (0.6B)

#### 1. TTS in `hybrid` or `gpu-min-vram` mode
- **TTS VRAM Requirement**: ~2,000 - 2,200 MiB
- **Total Required VRAM**: ~31,866 - 32,066 MiB
- **Status**: ❌ **OOM (Over-allocation)**. Exceeds the 30,704 MiB limit by ~1.1 - 1.3 GiB.
- **Remediation**:
  - Reduce LLM KV cache size (e.g., set `n_ctx=200,000` to save ~1.3 GiB VRAM), OR
  - Run TTS in `cpu-only` mode.

#### 2. TTS in `cpu-only` mode
- **TTS VRAM Requirement**: 0 MiB (System RAM: ~3.0 GiB)
- **Total Required VRAM**: **29,866 MiB** (Leaves 838 Headroom)
- **Status**:  **Safe**. Fits within the single card footprint.
- **Performance**: TTS RTF is ~1.58x (acceptable for conversational interaction).

---

### Scenario B: Full Co-Running with TTS (1.7B)

#### 1. TTS in `hybrid` or `gpu-min-vram` mode
- **TTS VRAM Requirement**: ~2,100 - 2,900 MiB
- **Total Required VRAM**: ~31,966 - 32,766 MiB
- **Status**: ❌ **OOM (Over-allocation)**. Exceeds the 30,704 MiB limit by ~1.2 - 2.0 GiB.
- **Remediation**:
  - Reduce LLM KV cache context size (e.g., set `n_ctx=160,000` to save ~2.7 GiB VRAM), OR
  - Run TTS in `cpu-only` mode.

#### 2. TTS in `cpu-only` mode
- **TTS VRAM Requirement**: 0 MiB (System RAM: ~4.4 GiB)
- **Total Required VRAM**: **29,866 MiB**
- **Status**:  **Safe**. Fits within the single card footprint.
- **Performance**: TTS RTF is ~3.39x (noticeable latency for long paragraphs).


