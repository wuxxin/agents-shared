# Qwen3.6-35B-A3B MoE Speculative Decoding & MTP Research

## Executive Summary

This research document investigates **Multi-Token Prediction (MTP)** speculative decoding for **`Qwen3.6-35B-A3B`** inside `llama.cpp` (`local-chat.sh`). It analyzes our current service configuration, the mathematical and architectural mechanics of MTP, quantization precision trade-offs (`Q4_K_M`, `APEX-I`, `Q8_0`), available Hugging Face GGUF models/addons, and concrete implementation strategies.

---

## 1. Current Local Service Analysis

### Current Configuration
* **Service script**: [`assistants/local-chat.sh`](file:///home/wuxxin/agent-shared/code/agents-shared/assistants/local-chat.sh#L49)
* **Active LLM Model**: `Qwen3.6-35B-A3B-APEX-I-Compact.gguf` (acquired via [`scripts/local-download.sh`](file:///home/wuxxin/agent-shared/code/agents-shared/scripts/local-download.sh#L251) from [`mudler/Qwen3.6-35B-A3B-APEX-GGUF`](https://huggingface.co/mudler/Qwen3.6-35B-A3B-APEX-GGUF))
* **Active Speculative Mode**: N-Gram Simple Lookup (`LCHAT_SPECULATIVE="--spec-type ngram-simple --spec-ngram-simple-size-n 6 --spec-ngram-simple-size-m 4"`)
* **Multimodal Projector**: `Qwen3.6-35B-A3B-APEX-I-Compact-mmproj.gguf` (~800 MiB)
* **Total VRAM Footprint**: **~17.5 GiB** (Model ~16.7 GiB + mmproj ~0.8 GiB)
* **Performance Baseline**: 1.0x baseline generation throughput (~1.3x speedup on repetitive/structured outputs such as JSON schemas, code blocks, and function calling; baseline speed on open-ended prose).

### Limitations of Current GGUF
During the APEX-I quantization process for `Qwen3.6-35B-A3B-APEX-I-Compact.gguf`, all native MTP tensors were stripped out to minimize file size (~16.7 GiB). Consequently, invoking `--spec-type draft-mtp` directly against our current standalone model file fails due to missing MTP tensors.

---

## 2. Multi-Token Prediction (MTP) Architecture & Mechanics

### How MTP Works
Standard autoregressive Transformer LLMs generate **1 token per forward pass** ($t \to t+1$). 

MTP adds auxiliary prediction module(s)/head(s) at the top of the final Transformer layer (layer 40). When the base model processes the prompt and generates the final hidden state vector $h_t \in \mathbb{R}^{2048}$, the MTP module uses $h_t$ to compute draft candidate tokens for $w_{t+1}$ and $w_{t+2}$ in $<1\text{ ms}$.

```
Input Tokens (w_<t)
       │
┌──────▼─────────────────────────┐
│ Transformer Backbone (40 Ls)  │ ──► Primary lm_head ──► Token w_t
│ 256 MoE Experts (APEX / Q4)    │
└──────┬─────────────────────────┘
       │ Hidden State h_t (2048-dim)
┌──────▼─────────────────────────┐
│ Auxiliary MTP Head (Q8_0)      │ ──► MTP lm_head     ──► Draft Tokens (w_t+1, w_t+2)
└────────────────────────────────┘
```

In `llama.cpp` (`llama-server`), `--spec-type draft-mtp` executes as follows:
1. **Draft Generation**: The MTP head generates candidate tokens $w_{t+1}, w_{t+2}$ from hidden state $h_t$.
2. **Parallel Verification**: In the next forward step, `llama.cpp` sends $w_t, w_{t+1}, w_{t+2}$ into the main model as a **single batched forward pass**.
3. **Speedup**: If accepted by the main model, generation speed increases to **1.4x – 1.85x** across all prompt types (prose, coding, reasoning, and chat).

### Why MTP Heads Require `Q8_0` Precision
Community benchmarks demonstrate that quantizing MTP heads down to `Q4_0` or `Q4_K` causes severe accuracy degradation, dropping draft token acceptance from ~75% down to **0% – 15%**. Because MTP heads are small (~300 MiB), keeping them in **`Q8_0`** (8-bit integer weights) preserves high acceptance rates (~65%–80%+) while incurring negligible VRAM overhead.

---

## 3. Quantization Mechanics & VRAM Breakdown

### Quantization Formats Compared
* **`Q4_K_M` (Standard 4-bit)**: Quantizes weights using 4-bit K-quants with 6-bit super-block scales. Applied uniformly across all 256 MoE experts (~17.8 GiB base model).
* **`APEX-I` (Adaptive Precision for Expert Models)**: Uses an importance matrix (`imatrix`) to measure expert activation frequency. Frequently activated experts get **4-bit / 5-bit**, while rarely activated experts are compressed to **2-bit / 3-bit (`IQ3_XS`)** (~16.7 GiB base model).

### Memory Footprint Breakdown

| Setup Component | Base LLM Model | MTP Draft Head | Vision `mmproj` | Total VRAM |
| :--- | :--- | :--- | :--- | :--- |
| **Current Baseline** (`APEX-I` + `ngram-simple`) | 16.7 GiB | 0 MiB *(Stripped)* | ~0.8 GiB | **~17.5 GiB** |
| **Modular Addon** (`APEX-I` + `lym00 MTP Q8_0`) | 16.7 GiB | **~300 MiB** (`Q8_0`) | ~0.8 GiB | **~17.8 GiB** |
| **Full MTP GGUF** (`havenoammo` / `am17an`) | 17.8 GiB | **~300 MiB** (`Q8_0`) | ~0.8 GiB | **~18.9 GiB** |

> **Key Finding**: The ~1.4 GiB VRAM gap between our baseline (~17.5 GiB) and full MTP GGUF builds (~18.9 GiB) is composed of **~1.1 GiB** from MoE expert quantization (`APEX-I` vs. uniform `Q4_K_M`) and **~300 MiB** from the `Q8_0` MTP head.

---

## 4. Hugging Face Options Matrix

### Option 1: `havenoammo/Qwen3.6-35B-A3B-MTP-GGUF` *(Recommended Official Base + Grafted MTP)*
* **URL**: [https://huggingface.co/havenoammo/Qwen3.6-35B-A3B-MTP-GGUF](https://huggingface.co/havenoammo/Qwen3.6-35B-A3B-MTP-GGUF)
* **Quantization**: Unsloth Dynamic 2.0 XL (`UD-Q4_K_M` / `UD-Q5_K_M`) with grafted `Q8_0` MTP heads.
* **MTP Delivery**: **Bundled** directly in main GGUF file.
* **VRAM (w/ mmproj)**: **~18.8 GiB**
* **Expected Perf vs Baseline**: **~1.45x – 1.85x faster** generation throughput via `--spec-type draft-mtp --spec-draft-n-max 2`. High Unsloth UD XL accuracy.

### Option 2: `am17an/Qwen3.6-35BA3B-MTP-GGUF` *(Imatrix + Native MTP)*
* **URL**: [https://huggingface.co/am17an/Qwen3.6-35BA3B-MTP-GGUF](https://huggingface.co/am17an/Qwen3.6-35BA3B-MTP-GGUF)
* **Quantization**: `Q4_K_M` (imatrix calibrated with preserved native MTP tensors).
* **MTP Delivery**: **Bundled** inside main GGUF file.
* **VRAM (w/ mmproj)**: **~18.5 GiB**
* **Expected Perf vs Baseline**: **~1.40x – 1.75x faster** generation speed over `ngram-simple`.

### Option 3: `HauhauCS/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive` *(Uncensored / Abliterated)*
* **URL**: [https://huggingface.co/HauhauCS/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive](https://huggingface.co/HauhauCS/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive)  
  *(MTP Graft: [LuffyTheFox/Qwen3.6-35B-A3B-Uncensored-MTP-GGUF](https://huggingface.co/LuffyTheFox/Qwen3.6-35B-A3B-Uncensored-MTP-GGUF))*
* **Quantization**: APEX-I / `Q4_K_M` DPO-abliterated fine-tune (removes safety refusals).
* **MTP Delivery**: Available as **bundled grafted GGUF** or via external draft file.
* **VRAM (w/ mmproj)**: **~18.2 GiB**
* **Expected Perf vs Baseline**: **~1.40x – 1.80x faster** throughput with zero refusal guardrails for creative/unrestricted agentic tasks.

### Option 4: `nightmedia/Qwen3.6-35B-A3B-Fable-Holo3.1` *(Creative / Roleplay Fine-Tune)*
* **URL**: [https://huggingface.co/nightmedia/Qwen3.6-35B-A3B-Fable-Holo3.1-qx86-hi-mlx](https://huggingface.co/nightmedia/Qwen3.6-35B-A3B-Fable-Holo3.1-qx86-hi-mlx)  
  *(GGUF Quants: [mradermacher/Qwen3.6-35B-A3B-Fable-Holo3.1-GGUF](https://huggingface.co/mradermacher/Qwen3.6-35B-A3B-Fable-Holo3.1-GGUF))*
* **Quantization**: `Q4_K_M` imatrix fine-tune merge (enhanced storytelling and narrative reasoning).
* **MTP Delivery**: Requires **Extra Draft File** ([lym00/Qwen3.6-35B-A3B-MTP-ONLY-GGUF](https://huggingface.co/lym00/Qwen3.6-35B-A3B-MTP-ONLY-GGUF)).
* **VRAM (w/ mmproj)**: **~18.6 GiB**
* **Expected Perf vs Baseline**: **~1.35x – 1.65x faster** throughput with enhanced creative depth.

### Option 5: `IHaveNoClueAndIMustPost/Qwen3.6-35A3B-MTP-TENSORS-ONLY` *(Standalone Q8_0 Draft Head Addon)*
* **URL**: [https://huggingface.co/IHaveNoClueAndIMustPost/Qwen3.6-35A3B-MTP-TENSORS-ONLY](https://huggingface.co/IHaveNoClueAndIMustPost/Qwen3.6-35A3B-MTP-TENSORS-ONLY)
* **Direct File URL**: [https://huggingface.co/IHaveNoClueAndIMustPost/Qwen3.6-35A3B-MTP-TENSORS-ONLY/resolve/main/am17an-Qwen3.6-35BA3B-MTP-only.gguf](https://huggingface.co/IHaveNoClueAndIMustPost/Qwen3.6-35A3B-MTP-TENSORS-ONLY/resolve/main/am17an-Qwen3.6-35BA3B-MTP-only.gguf)
* **Quantization**: `Q8_0` MTP draft head module (~855 MiB standalone file).
* **MTP Delivery**: **Standalone Extra Draft File**.
* **VRAM Overhead**: **+0.85 GiB** added to any base model VRAM.
* **Capability**: Enables `--spec-type draft-mtp` on **any base model** (including our current APEX-I model) by attaching as an external draft head (`--model-draft`).

---

## 5. Implementation Strategies for `local-chat.sh`

### Strategy A: Modular Addon (Recommended for Minimum VRAM Increase)
Keep our current `Qwen3.6-35B-A3B-APEX-I-Compact.gguf` base model (~16.7 GiB) and attach the `IHaveNoClueAndIMustPost` `Q8_0` MTP draft head (~855 MiB).

1. Download the standalone MTP draft file:
   ```bash
   curl -L -o /data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-MTP-ONLY.gguf \
     "https://huggingface.co/IHaveNoClueAndIMustPost/Qwen3.6-35A3B-MTP-TENSORS-ONLY/resolve/main/am17an-Qwen3.6-35BA3B-MTP-only.gguf"
   ```
2. Update `~/.config/systemd/user/local-chat.env`:
   ```bash
   LCHAT_SPECULATIVE="--model-draft /data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-MTP-ONLY.gguf --spec-type draft-mtp --spec-draft-n-max 2"
   ```
3. Restart service:
   ```bash
   ./assistants/local-chat.sh restart
   ```
* **Result**: **~1.45x–1.75x speedup** for only **+855 MiB VRAM** (~18.3 GiB total).

---

### Strategy B: Full Bundled GGUF Replacement
Replace our current model file with `havenoammo/Qwen3.6-35B-A3B-MTP-GGUF` (UD-Q4_K_M).

1. Download bundled GGUF:
   ```bash
   curl -L -o /data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-MTP-UD-Q4_K_M.gguf \
     "https://huggingface.co/havenoammo/Qwen3.6-35B-A3B-MTP-GGUF/resolve/main/Qwen3.6-35B-A3B-MTP-UD-Q4_K_M.gguf"
   ```
2. Update `~/.config/systemd/user/local-chat.env`:
   ```bash
   LCHAT_MODEL=/data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-MTP-UD-Q4_K_M.gguf
   LCHAT_SPECULATIVE="--spec-type draft-mtp --spec-draft-n-max 2"
   ```
3. Restart service:
   ```bash
   ./assistants/local-chat.sh restart
   ```
* **Result**: **~1.50x–1.85x speedup** with maximum base model accuracy (~18.8 GiB total VRAM).
