# Central VRAM Memory Map & Co-running Guide

This document aggregates detailed memory requirements and allocations for local AI models running on the AMD Radeon Pro W6800 GPU (**30,704 MiB** usable VRAM).

## Component Footprints

### Local LLM Service (`local-llm-ggml.sh` / `llama-server`)
Serves both chat and embeddings from a single process.

| Component / Allocation | GPU VRAM | Details |
|---|---|---|
| **Model Weights & Compute** (LLM + Vision + Embedding) | ~19,959 MiB | LLM Weights (~17,408 MiB) + mmproj (~861 MiB) + Embedding Weights (~700 MiB) + Compute (~990 MiB) |
| **KV Cache** (q4_0 KV, parallel=3, slot n_ctx=80,000) | ~8,031 MiB | LLM KV cache allocation |
| **HIP Context Overhead** (1 process) | ~600 MiB | ROCm driver context overhead |
| **Total LLM Footprint** | **~28,590 MiB** | Run on GPU |

### Local Rerank Service (`local-rerank.sh` / `llama-server`)
Serves document reranking. Can run on GPU or CPU.

| Mode / Component | GPU VRAM | Details |
|---|---|---|
| **GPU Execution** (Weights + Compute + HIP Overhead) | ~1,050 MiB | Weights (~450 MiB) + HIP Overhead (~600 MiB) |
| **CPU Execution** | **0 MiB** | Runs entirely in System RAM (~450 MiB) |

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

Here we map VRAM usage for running **Inference** (LLM + Vision, Embedding, Reranking), **Speech-to-Text**, and **Text-to-Speech** services concurrently on a single card (30,704 MiB usable VRAM limit).

To maximize VRAM efficiency, we run the **Local-LLM Service** and **Speech-to-Text** on the GPU, while offloading the **Local-Rerank Service** and the **Text-To-Speech Service** to the CPU.

### Baseline Allocation (LLM on GPU, Reranker on CPU, STT on GPU)
- **Local-LLM Service** (LLM + Vision + Embedding + HIP context): **20,559 MiB** (19,959 MiB weights/compute + 600 MiB HIP context)
- **LLM KV Cache** (n_ctx = 240,000, parallel=3, slot n_ctx=80,000): **8,031 MiB**
- **Local-Rerank Service** (on CPU): **0 MiB** (Runs in System RAM)
- **Speech-to-Text (Whisper on GPU)**: **1,426 MiB** (includes weights, KV, buffers, and STT HIP overhead)
- **TTS (Qwen3-tts 0.6B on cpu only)**: **0 MiB** VRAM (System RAM: ~3.0 GiB)
    - **Performance**: TTS RTF is ~1.58x (acceptable for conversational interaction)
- **Total Required VRAM**: **30,016 MiB** (with LLM `n_ctx=240,000`, parallel=3)
- **Status**:  **Safe**. Fits within the single card footprint.
- **Remaining Headroom**: **688 MiB** free VRAM


