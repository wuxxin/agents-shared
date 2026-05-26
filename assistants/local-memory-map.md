# Central VRAM Memory Map & Co-running Guide

This document aggregates detailed memory requirements and allocations for local AI models running on the AMD Radeon Pro W6800 GPU (**30,704 MiB** usable VRAM).

## 1. Single Component Footprints

### A. Local Inference (`local-inference.sh` / `llama-server`)

| Component | GPU VRAM | Details |
|---|---|---|
| **MoE LLM** (Qwen3.6-35B-A3B-APEX-I-Compact) | ~17,408 MiB | 17 GiB GGUF file |
| **MoE mmproj** (Vision projector) | ~861 MiB | 861 MiB GGUF file |
| **Embedding** (Qwen3-Embedding-0.6B Q8_0) | ~700 MiB | 610 MiB GGUF file |
| **Reranker** (Qwen3-Reranker-0.6B Q4_K_M) | ~450 MiB | 379 MiB GGUF file |
| **Compute Overhead** (per LLM) | ~990 MiB | Scheduler/Activation buffers |
| **KV Cache** (q4_0 KV, parallel=2, n_ctx=240,000) | ~8,031 MiB | ~35.1 bytes/token allocation |

---

### B. Local Speech-to-Text (`local-speech-to-text.sh` / `whisper-server`)

Model Target: `ggml-large-v3-turbo-q5_0.bin`

| Component | GPU VRAM |
|---|---|
| Model Weights | ~573.45 MiB |
| KV Caches | ~49.81 MiB |
| Compute Buffers | ~202.35 MiB |
| HIP Context Runtime Overhead | ~600.00 MiB |
| **Total STT Footprint** | **~1,425.61 MiB (~1.4 GiB)** |

---

### C. Local Text-to-Speech (`local-text-to-speech.sh` / `qwen3-tts-server`)

#### Variant 1: 1.7B Model (CustomVoice/Base) + Vocoder

| Component | GPU VRAM | Details |
|---|---|---|
| Talker Model weights (Q8_0) | ~2,322 MiB | 2.27 GiB GGUF file |
| Vocoder weights (F16) | ~325 MiB | 325 MiB GGUF file |
| KV Cache & Compute buffers | ~400 MiB | Generation context overhead |
| HIP Context Runtime Overhead | ~600 MiB | ROCm runtime overhead |
| **Total TTS 1.7B Footprint** | **~3,647 MiB (~3.6 GiB)** | |

#### Variant 2: 0.6B Model (CustomVoice/Base) + Vocoder

| Component | GPU VRAM | Details |
|---|---|---|
| Talker Model weights (Q8_0) | ~1,264 MiB | 1.23 GiB GGUF file |
| Vocoder weights (F16) | ~325 MiB | 325 MiB GGUF file |
| KV Cache & Compute buffers | ~300 MiB | Generation context overhead |
| HIP Context Runtime Overhead | ~600 MiB | ROCm runtime overhead |
| **Total TTS 0.6B Footprint** | **~2,489 MiB (~2.5 GiB)** | |

---

## 2. Combined Co-running Scenario

Here we map VRAM usage for running **Inference** (MoE LLM + Vision), **Speech-to-Text**, and **Text-to-Speech** services concurrently on a single card (30,704 MiB usable VRAM limit).

### MoE LLM (with Vision) + STT + TTS (1.7B)

This setup uses the Mixture-of-Experts LLM with vision enabled, Whisper STT, and Qwen3-TTS 1.7B.

- **Required VRAM**:
  - MoE LLM + Vision weights & compute: **20,409 MiB**
  - LLM KV Cache (n_ctx = 240,000): **8,031 MiB**
  - Speech-to-Text (Whisper): **1,426 MiB**
  - Text-to-Speech (1.7B): **3,647 MiB**
  - **Total**: **33,513 MiB**
- **Status**: 🔴 **Overallocated by 2,809 MiB** (Will cause system memory fallback and performance degradation).

#### Mitigations:
1. **Reduce Context Size**: Change `LI_N_CTX=120000` in `local-inference.env` (saving ~4,016 MiB).
   - KV @ 120,000 tokens: **4,015 MiB**
   - Adjusted Total VRAM: **29,497 MiB** (Headroom: **1,207 MiB** - Safe)
2. **Downsize TTS & Context**: Swap TTS to the 0.6B variant (saving 1,158 MiB) and reduce `LI_N_CTX=160000` (saving 2,677 MiB).
   - KV @ 160,000 tokens: **5,354 MiB**
   - Adjusted Total VRAM: **29,678 MiB** (Headroom: **1,026 MiB** - Safe)
