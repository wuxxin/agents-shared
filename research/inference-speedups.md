# Local Component Inference Speedups & Vulkan Compatibility Research

**Document Date:** `2026-07-22`  
**Target Hardware:** 
  -  Discrete GPU (dGPU: `AMD Radeon Pro W6800` / `RX 7900 XTX` (24GB, 960GB/s bandwidth, AMD gfx1100) mapped as `ROCm0` / `Vulkan1`)
  -  Integrated GPU (iGPU: `AMD Radeon Graphics (Renoir, gfx90c, 16GB (main memory))` mapped as `ROCm1` / `Vulkan0`)

---

## 1. Executive Summary

A review of the active service performance metrics in [local-benchmark.md](file:///home/wuxxin/agent-shared/code/agents-shared/assistants/local-benchmark.md) reveals several significant bottlenecks in the current production setup. 

The primary bottlenecks include:
1. **Device Misallocation:** Key compute-heavy services like **Reranking** and **Image Generation** are default-routing to the integrated GPU (`Vulkan0`), which is approximately **7x to 15x slower** than the discrete GPU (`ROCm0` under HIP, or `Vulkan1` under Vulkan).
2. **Autoregressive Overhead for Prefill:** The Text Chat model (`llama-server`) does not use prefix-sharing or radix-caching, resulting in prompt evaluation latency (TTFT) of **~19.8 seconds** for larger context histories.
3. **Suboptimal Model Architectures:** Using heavy or unoptimized models for Speech Synthesis (Qwen3-TTS) and Image Generation (`sd.cpp`) creates excessive processing delays.

This document details alternative, high-performance engines optimized for both **AMD ROCm (Native)** and **Vulkan (Cross-Platform)**, maintaining strict **OpenAI API compatibility** where applicable.

---

## 2. Component Performance & Compatibility Matrix

| Service | Current Engine (Host) | Best ROCm Option | Best Vulkan Option | Vulkan Compatibility Notes |
|---|---|---|---|---|
| **Text Chat** | `llama.cpp` (170 t/s gen, 19.8s TTFT) | **SGLang** (Radix Cache, 200+ t/s gen) | **MLC-LLM** or **`llama.cpp` (Vulkan)** | **MLC-LLM** compiles models via Apache TVM for highly optimized Vulkan SPIR-V execution. `llama.cpp` natively supports Vulkan via `ggml-vulkan`. |
| **Embedding** | `llama.cpp` (4853 t/s) | **Hugging Face TEI** (10k+ t/s) | **ONNX Runtime (Vulkan)** or **`llama.cpp` (Vulkan)** | TEI does not officially support Vulkan. Running embedding models compiled to ONNX via ONNX Runtime Vulkan EP is the best Vulkan path. |
| **Rerank** | `llama.cpp` (Vulkan0, 5.7s) | **Hugging Face TEI** (`< 100 ms`) | **ONNX Runtime (Vulkan)** or **`llama.cpp` (Vulkan)** | Same as Embeddings. Vulkan reranking is possible using `llama.cpp` on `Vulkan1` (discrete GPU) or ONNX Runtime. |
| **TTS** | `Qwen3-TTS` (27.0s) | **Kokoro-82M** (via `kokoro-fastapi` - `< 0.5s`) | **Kokoro-ONNX** (via ONNX Runtime Vulkan EP) | Kokoro-82M compiles cleanly to ONNX, allowing direct hardware acceleration via the ONNX Runtime Vulkan Execution Provider. |
| **STT** | `whisper.cpp` (7.7s) | **`faster-whisper`** (CTranslate2) | **Whisper-ONNX** (via ONNX Runtime Vulkan EP) | CTranslate2 does not support Vulkan. Running Whisper models via ONNX Runtime Vulkan EP is the fastest Vulkan alternative. |
| **Image Gen** | `sd.cpp` (Vulkan0, 89s) | **ComfyUI API / Diffusers + `stable-fast`** (`< 6s`) | **`sd.cpp` (Vulkan)** or **Diffusers ONNX (Vulkan)** | `sd.cpp` fully supports Vulkan via `ggml-vulkan`. For Python frameworks, Diffusers models must be converted to ONNX/DirectML to run on Vulkan. |

---

## 3. Detailed Component Analysis & Vulkan Support

### 3.1 Text Chat (LLM)
* **ROCm Best Option: SGLang**
  - *Why:* SGLang's **RadixAttention** caches the KV-cache of prompt prefixes (system instructions, memory context) across independent request sessions. When an agent queries the same model, the prefill step is skipped entirely (instantaneous TTFT). SGLang runs strictly on PyTorch + CUDA/ROCm (using Triton kernels).
* **Vulkan Best Option: MLC-LLM**
  - *Why:* MLC-LLM is the industry leader for running LLMs on Vulkan. It uses Apache TVM to compile model execution graphs into highly optimized SPIR-V shaders. It features PagedAttention, speculative decoding, and exposes a fully OpenAI-compatible API.
  - *Alternative:* **`llama.cpp` (Vulkan)** which achieves excellent performance (the benchmark shows Vulkan1 W6800 achieving `132.22 t/s` prefill and `116.78 t/s` decode).

### 3.2 Text Embedding & Document Reranking
* **ROCm Best Option: Hugging Face TEI (Text Embeddings Inference)**
  - *Why:* Built in Rust, highly concurrent, and supports ROCm natively. TEI implements prefix caching (encoding the query once and sharing it across all documents during reranking) and continuous batching.
* **Vulkan Best Option: ONNX Runtime (Vulkan EP)**
  - *Why:* TEI does not natively support Vulkan. For Vulkan-only environments, exporting the BERT/cross-encoder models to ONNX and serving them via ONNX Runtime using the Vulkan Execution Provider is the most efficient path.

### 3.3 Text-to-Speech (TTS)
* **ROCm Best Option: Kokoro-82M (`kokoro-fastapi`)**
  - *Why:* A tiny 82-million parameter model that beats larger models in natural voice synthesis. It runs at **50x real-time speed** (synthesizing a sentence in a fraction of a second).
* **Vulkan Best Option: Kokoro-ONNX**
  - *Why:* The official Python `kokoro-onnx` wrapper runs Kokoro models directly via ONNX Runtime. When configured with the Vulkan Execution Provider (or DirectML), it provides fully accelerated audio synthesis on any Vulkan-capable hardware.

### 3.4 Speech-to-Text (STT)
* **ROCm Best Option: `faster-whisper` (CTranslate2)**
  - *Why:* Re-implemented in C++ using CTranslate2, delivering 4x higher transcription speed than standard Whisper wrappers.
* **Vulkan Best Option: Whisper-ONNX**
  - *Why:* CTranslate2 does not support Vulkan. Running Whisper models via ONNX Runtime with Vulkan acceleration provides the fastest Vulkan-based transcribing.

### 3.5 Image Generation
* **ROCm Best Option: ComfyUI (API mode) or Diffusers + `stable-fast`**
  - *Why:* Allows compiling PyTorch diffusion models (SDXL, Flux, SD3) into optimized hardware graphs.
* **Vulkan Best Option: `sd.cpp` (Vulkan)**
  - *Why:* `stable-diffusion.cpp` features a native `ggml-vulkan` backend. By running the generation on the discrete GPU (`Vulkan1`) instead of the integrated GPU (`Vulkan0`), generation time drops from **89 seconds to 6.96 seconds** (a **12.8x speedup**).

---

## 4. VRAM Budgeting & Memory Configuration (24 GB RX 7900 XTX)

On your current host setup, you are running **Q4 quantized weights and quantized KV-caches (q4_0)** for almost all services to run heavy models (like the **Qwen3.6 35B vision-text model**) within the discrete **24 GB RX 7900 XTX VRAM budget**. Below is the memory footprint analysis mapped to this exact setup:

### 4.1 Component Memory Profiles (Targeting Your Active Models)

| Service | Active Model Config | FP16 VRAM Footprint | Quantized VRAM Footprint (Q4 / Q8) | Active Setup & Recommendation |
|---|---|---|---|---|
| **Text Chat (LLM)** | Qwen 3.6 (35B) | ~70.0 GB (OOM) | **~19.0 GB** (Q4_K_M / Compact) | **Q4 weights mandatory:** Running a 35B model on a 24 GB GPU is only possible in Q4. It leaves ~5 GB of headroom for KV-cache and system services. |
| **Embedding** | Qwen3-Embedding (0.6B) | ~1.2 GB | **~900 MB** (Q8_0) | **Q8_0:** Fits easily in memory. Runs permanently on ROCm0. |
| **Reranker** | Qwen3-Reranker-0.6B | ~1.2 GB | **~400 MB** (Q4_K_M) | **Q4_K_M:** Tiny footprint, currently redirecting from iGPU to dGPU ROCm0. |
| **STT (Speech-to-Text)**| Whisper-Large-v3-Turbo| ~1.6 GB | **~500 MB** (Q5_0) | **Q5_0 / FP16:** Highly optimized in whisper.cpp/faster-whisper. |
| **TTS (Text-to-Speech)**| Qwen3-TTS | ~1.2 GB | **~650 MB** (Q8_0) | **Q8_0:** Currently used. Switching to Kokoro (ONNX) uses only ~80MB. |
| **Image Generation** | z_image_turbo | ~6.0 GB | **~3.2 GB** (Q8_0) | **Q8_0:** Heavy model, currently redirecting to dGPU Vulkan1. |

---

### 4.2 Quantization & KV Cache Support: llama.cpp vs SGLang/vLLM

To replace `llama.cpp` with SGLang or vLLM for Chat, we must map your current Q4 configurations to their native features:

#### **A. Model Weights (Q4 Support)**
* **Current Setup:** You are running GGUF-quantized `Qwen3.6-35B-A3B-APEX-I-Compact.gguf` (weights at ~Q4 equivalent).
* **vLLM:** Has **native GGUF parser support**, allowing you to load your current `.gguf` Q4 model files directly. It also natively supports AWQ/GPTQ Q4 models.
* **SGLang:** Natively supports Q4 weights via **AWQ** and **GPTQ** formats. It does not parse GGUF directly; you would load the model converted to GPTQ/AWQ.

#### **B. KV Cache Quantization (q4_0 vs FP8/INT8)**
* **Current Setup:** You use `q4_0` KV cache quantization (`LCHAT_CACHE_TYPE_K=q4_0` / `LCHAT_CACHE_TYPE_V=q4_0`) in `llama-server` to save VRAM.
* **SGLang & vLLM Support:** These runtimes **do not** support `q4_0` for the KV-cache, but they natively support **FP8 KV Cache** (`--kv-cache-dtype fp8`) and **INT8 KV Cache** (`--kv-cache-dtype int8`).

| KV Cache Format | Bytes Per Element | Accuracy & Precision | Hardware Acceleration (AMD RX 7900 XTX) |
|---|---|---|---|
| **`q4_0`** *(Current llama.cpp)* | **~0.5 bytes** | Moderate degradation; can cause loss of coherence in long context/reasoning. | None. Must be dequantized to FP16 in GPU registers before processing, adding compute overhead. |
| **`FP8` (E4M3)** *(SGLang/vLLM)* | **1.0 byte** | Near-lossless (retains FP16 accuracy). | **Native.** AMD RDNA3 (RX 7900 XTX) has dedicated **FP8 Tensor Cores**. Calculations run natively in FP8 without register dequantization, yielding higher throughput. |
| **`INT8`** *(SGLang/vLLM)* | **1.0 byte** | Low degradation. | Supported via integer vector execution. |

* **Trade-off:** FP8 KV cache uses twice the VRAM of `q4_0` (1 byte vs 0.5 bytes), but provides **vastly superior reasoning accuracy** and **native hardware execution speed** on your RX 7900 XTX GPU.

---

### 4.3 Concurrent Allocation Strategy (RX 7900 XTX 24 GB Budget)

Given that the 35B LLM in Q4 consumes ~19.0 GB, the remaining 5 GB VRAM is budgeted as follows:

1. **Static Allocations (Persistent Services):**
   - **Embedding + Reranking (TEI):** **~1.5 GB** (using FP8/Q8 TEI models).
   - **TTS (Kokoro) + STT (Whisper):** **~1.0 GB** (switching TTS to Kokoro ONNX is crucial to save VRAM).
2. **Dynamic LLM KV Cache (SGLang/vLLM):**
   - **LLM Chat:** Constrain SGLang/vLLM memory usage to **`~19.8 GB`** (via `--gpu-memory-utilization 0.82` which includes model weights + KV cache). Running SGLang's RadixAttention saves VRAM by caching recurring prompt history.
3. **Lazy Loading (ComfyUI / Stable Diffusion):**
   - **Image Generation:** Must be loaded dynamically and offloaded when idle, or constrained to run in system memory (iGPU Vulkan0) when the LLM is heavily loaded.
4. **Total Concurrent Usage:** `1.5 GB (TEI) + 1.0 GB (Audio) + 19.8 GB (LLM Chat) = 22.3 GB VRAM`, keeping under the 24 GB RX 7900 XTX limit.

---

### 4.4 Expected Performance Limits: Prefill & Generation Speeds

Below is the theoretical hardware limit compared against real-world expected prefill and generation (decoding) speeds for the **Qwen 3.6 (35B-A3B)** model in **Q4** on the **RX 7900 XTX (960 GB/s bus, 24 GB VRAM)**:

#### **A. Decoding (Generation) Speeds**
During generation, the process is **memory-bandwidth bound**. We only load active experts ($3\text{B}$ parameters $\approx 1.5\text{ GB}$ of weights at 4-bit) per token:
* **Theoretical Hardware Ceiling:** **`640 tokens/second`** (derived from $\frac{960\text{ GB/s}}{1.5\text{ GB}}$).
* **`llama.cpp` (Current Host Baseline):** **`110 – 170 tokens/second`** (runs at ~26% of hardware limit; boosted by speculative decoding).
* **`vLLM`:**
  - *Single Stream:* **`130 – 180 tokens/second`** (runs comparable to baseline).
  - *With Speculative Decoding:* **`220 – 300 tokens/second`** (leverages native spec-draft token evaluation).
  - *Aggregate Concurrent Throughput:* **`300 – 450 tokens/second`** (scales VRAM bus saturation across parallel users).
* **`SGLang`:**
  - *Single Stream:* **`160 – 220 tokens/second`** (lower runtime overhead, optimized Triton decode kernels).
  - *Aggregate Concurrent Throughput:* **`350 – 500 tokens/second`** (near-maximum memory bandwidth saturation).

#### **B. Prefill (Prompt Processing) Speeds**
During prefill, the process is **compute-bound** (prompt evaluation runs in parallel across GPU matrix cores):
* **Theoretical Hardware Ceiling:** **`20,500 – 41,000 tokens/second`** (based on $123\text{ TFLOPs}$ FP16 accumulation up to $246\text{ TOPS}$ INT4 execution).
* **`llama.cpp` (Current Host Baseline):** **`1,500 – 1,750 tokens/second`** (requires $\approx 9.5\text{s}$ for a $16\text{k}$ context prompt; $\approx 60\text{s}$ for a $100\text{k}$ prompt).
* **`vLLM`:** **`2,500 – 4,000 tokens/second`** (utilizes native ROCm-optimized FlashAttention-2. Supports *Chunked Prefill* to prevent execution stalls).
* **`SGLang`:**
  - *Cold Prefill:* **`3,000 – 5,000 tokens/second`** (custom compiled attention routing).
  - *Radix Cache Hit (Warm Prompt):* **`Infinite (TTFT < 50 ms)`** (skips prompt evaluation entirely by loading the pre-existing KV cache blocks from the radix tree).

---

## 5. Key Recommendations

1. **Immediate Quick Fix:** Update the `local-rerank` and `local-image` systemd environment configs to target the discrete GPU (e.g. `LRR_DEVICE="ROCm0"` or `Vulkan1` instead of Vulkan0). This yields instant **7.4x to 12.8x speedups** on the host.
2. **Transition Chat to SGLang:** Integrate SGLang as the backend for `local-chat.sh` to benefit from RadixAttention prompt caching.
3. **Adopt HF TEI & Kokoro:** Replace `llama.cpp` embedding/rerank instances with TEI, and swap `qwen3-tts` for a `kokoro-fastapi` service. Both expose the exact same OpenAI compatibility with a fraction of the response latency.
4. **Enforce VRAM Limits on SGLang/vLLM:** Set explicit GPU memory utilization limits when starting LLM chat servers to prevent them from pre-allocating the entire VRAM pool.
5. **Enable FP8 KV Cache:** Run SGLang/vLLM with `--kv-cache-dtype fp8` to compress the KV cache by 50% and maximize chat history headroom on the 24 GB dGPU.

---

## 6. Installation Guide: SGLang on Arch Linux with ROCm/HIP

Since Arch Linux uses the latest ROCm runtimes (`7.2.4-1` and `python-pytorch-opt-rocm 2.12.0-4`), pre-compiled binary wheels for ROCm 6.1 (such as `FlashInfer`) will fail to load. You must compile dependencies from source using the system compilers.

### 6.1 Create a Virtual Environment with System Site Packages
To preserve a clean system environment while inheriting the system-wide optimized ROCm PyTorch binaries, create a virtual environment with `--system-site-packages`:

```bash
python -m venv --system-site-packages sglang-env
source sglang-env/bin/activate
```

### 6.2 Compile FlashInfer from Source (Required for ROCm 7.2)
FlashInfer provides SGLang's underlying RadixAttention and PageAttention GPU kernels:

```bash
git clone --recursive https://github.com/flashinfer-ai/flashinfer.git
cd flashinfer

# Export ROCm Clang compilers
export CC="/opt/rocm/llvm/bin/clang"
export CXX="/opt/rocm/llvm/bin/clang++"

# Compile and install
pip install --no-build-isolation -e .
cd ..
```

### 6.3 Compile & Install SGLang
Clone and build SGLang from source:

```bash
git clone --recursive https://github.com/sgl-project/sglang.git
cd sglang

export CC="/opt/rocm/llvm/bin/clang"
export CXX="/opt/rocm/llvm/bin/clang++"
export ROCM_PATH="/opt/rocm"

pip install --no-build-isolation -e "python[all]"
```

### 6.4 Model Weights format for SGLang
Unlike `vLLM` which can parse `.gguf` files natively, standard SGLang requires standard Hugging Face/Safetensors weights or GPU-quantized formats like **AWQ** or **GPTQ**. To run your model in SGLang, convert or download the weights in `AWQ` or `GPTQ` format.

---

## 7. Arch Linux AUR Package Landscape

The package availability in the Arch User Repository (AUR) for the recommended speedup engines is detailed below:

* **`python-faster-whisper` (ASR):** **Available** ([AUR Page](https://aur.archlinux.org/packages/python-faster-whisper) \| [Source GitHub](https://github.com/SYSTRAN/faster-whisper)). Installs the CTranslate2 engine and python dependencies. 
* **`sglang` / `sglang-git` (Chat):** **Available** ([AUR Page](https://aur.archlinux.org/packages/sglang-git) \| [Source GitHub](https://github.com/sgl-project/sglang)). Compiles from source on the host, which is beneficial for building custom kernels against your specific system-installed ROCm 7.2 stack.
* **`sherpa-onnx` (Vulkan Speech):** **Available** ([AUR Page](https://aur.archlinux.org/packages/sherpa-onnx) \| [Source GitHub](https://github.com/k2-fsa/sherpa-onnx)). A C++ runtime powered by ONNX Runtime that natively supports Vulkan-accelerated Whisper (STT) and Kokoro (TTS).
* **`text-embeddings-inference` (TEI):** **Not Available.** To run TEI, compile directly from cargo source ([Source GitHub](https://github.com/huggingface/text-embeddings-inference)) or run the official ROCm compatible Docker container image (`ghcr.io/huggingface/text-embeddings-inference:rocm-8.9`).
* **`stable-fast` (Image Gen compiler):** **Not Available.** Install via pip inside your virtual environment to compile the custom ROCm hardware-level graph compiler kernels on-the-fly (from [Source GitHub](https://github.com/chengzg/stable-fast)).
* **`mlc-llm`:** **Not Available.** Install MLC-LLM via pip or compile from the [Source GitHub](https://github.com/mlc-ai/mlc-llm) (requires linking against `tvm`).


---

## 8. iGPU Memory Bandwidth & Vulkan Acceleration (gfx90c APU)

Your system contains an **integrated GPU (iGPU)** based on the AMD Radeon Graphics Renoir (`gfx90c`) architecture sharing host system RAM.

* **ROCm/HIP Limitations:** The `gfx90c` APU has no official or full ROCm/HIP compiler support (ROCm supports discrete GPUs and newer RDNA-based APUs).
* **Vulkan Support:** The Vulkan driver (Mesa RADV `Vulkan0`) works perfectly on this APU. By allocating up to **16 GB** of shared system memory, the iGPU can execute accelerated Vulkan inference workloads.
* **Memory Bandwidth Analysis:**
  - *Theoretical Peak Bandwidth (Dual-Channel DDR4-3200):* 
    $$3200 \text{ MT/s} \times 2 \text{ channels} \times 8 \text{ bytes} = 51.2 \text{ GB/s}$$
  - *Effective Real-World Bandwidth:* **`40 to 45 GB/s`** (under active memory read/write loads).
  - *Comparison:* While significantly slower than the discrete RX 7900 XTX's **`960 GB/s`** bus (~19x slower), it is still 2x faster than single-threaded CPU execution and completely offloads computation.
* **Architecture Advantage:** Offloading Whisper STT (`whisper-onnx` via ONNX Runtime Vulkan EP) and Kokoro TTS to the iGPU via Vulkan completely frees up CPU cores and saves dGPU VRAM for SGLang/LLM Chat.

---

## 9. CrispASR (`crispasr-git-ggml-hip`) & TTS Alternatives

Your Arch Linux AUR split-package workspace contains `crispasr-git-ggml-hip` built from [CrispASR Github](https://github.com/CrispStrobe/CrispASR) (cross-platform C++ speech engine wrapper).

### 9.1 Dynamic Linking Design & Memory Savings
* Unlike standalone builds that package their own static `libggml` layers, `crispasr-git-ggml-hip` compiles `libggml` as a system-wide shared library (`/usr/lib/libggml.so`) with dynamic backend loading (`GGML_BACKEND_DL=ON`).
* This permits CrispASR to share GPU kernels and resources with `llama.cpp`, `whisper.cpp`, `stable-diffusion.cpp`, and `qwen3-tts.cpp`. It prevents duplicate shader builds and conserves VRAM.

### 9.2 Whisper ASR Performance (Speech-to-Text)
* **Model Size (Whisper-Large-v3-Turbo):** ~800M parameters.
* **VRAM Footprint:** ~1.6 GB (FP16), ~900 MB (Q8_0), ~500 MB (Q5_0).
* **Execution Speeds:**
  - *dGPU ROCm (`ROCm0`):* **30x to 50x real-time speed** (Real-Time Factor: `0.02 – 0.03`).
  - *iGPU Vulkan (`Vulkan0`):* **8x to 15x real-time speed** (Real-Time Factor: `0.06 – 0.12`). Extremely fast and keeps the dGPU VRAM free.

### 9.3 CrispASR as a Text-to-Speech (TTS) Server Replacement
CrispASR natively implements **48 TTS engines** (including Kokoro, Qwen3-TTS, CosyVoice, MeloTTS, Bark, etc.) in pure C++ linked directly to `libggml`.

#### **A. Kokoro-82M TTS Engine (Best Choice)**
* **Model Size:** 82M parameters.
* **Memory footprint:** **`~100 MB`** VRAM/RAM total.
* **Performance:** **10x to 50x faster than real-time** (synthesizes audio in `< 0.5s` on CPU/iGPU).
* **Integration:** Running `crispasr-server --port 20095 --backend kokoro -m kokoro-82m.gguf --device vulkan0` hosts an OpenAI-compatible `/v1/audio/speech` endpoint on the iGPU Vulkan with zero Python/PyTorch runtime overhead.

#### **B. Qwen3-TTS Engine (Hybrid Split Mode)**
CrispASR implements custom patches to accelerate the Qwen3-TTS architecture on host systems:
* **Autoregressive Bottleneck on GPU:** Autoregressive Code Generation (`TTSTransformer`) runs at a batch size of 1. On GPUs, dispatch latency (~10–15µs per kernel, ~400 kernels per step) starves the compute cores, making GPU-only mode slow (**2.28x** real-time for 0.6B).
* **The Hybrid Split Performance:**
  - By setting `QWEN3_TTS_TRANSFORMER_FORCE_CPU=1` (Code Gen on CPU via AVX2/AVX-512 vector instructions) and executing Vocoder Decode on the GPU (ROCm/Vulkan), you unlock **Hybrid Split Mode**.
  - **Speed:** 0.6B models synthesize at **1.11x real-time** (1.96x faster than GPU-only mode, and 1.32x faster than CPU-only mode).
  - **VRAM Savings:** Keeps transformer weights in system memory, reducing VRAM usage by **1.5 GB to 2.7 GB** (VRAM footprint stays at ~1.7–2.3 GB for vocoder execution).
* **Low Memory Mode:** Setting `QWEN3_TTS_LOW_MEM=1` lazy-loads weight buffers, saving **~1.5 GB VRAM** with zero performance impact.

---

## 10. Comparative Analysis: MLC-LLM, SGLang, vLLM, and TEI vs. llama.cpp

The table below summarizes the expected performance (speed/throughput) and memory footprint tradeoffs of the replacement inference engines compared directly against your current `llama.cpp` (`llama-server`) baseline:

### 10.1 LLM Chat Engines Comparison

| Feature / Metric | `llama.cpp` (Current) | `MLC-LLM` | `vLLM` | `SGLang` |
|---|---|---|---|---|
| **Compilation Model** | Handcrafted C/C++ | TVM compiler-based | Python/C++ PyTorch | Python/Triton C++ |
| **Decode Speed (Gen)** | $110 - 170\text{ t/s}$ (Baseline) | **$250 - 400\text{ t/s}$** (Fastest) | $130 - 180\text{ t/s}$ | **$160 - 220\text{ t/s}$** |
| **Prefill Speed (Cold)** | $1,500 - 1,750\text{ t/s}$ | $800 - 1,000\text{ t/s}$ (Slowest) | $2,500 - 4,000\text{ t/s}$ | **$3,000 - 5,000\text{ t/s}$** |
| **TTFT (Shared Prefix)** | ~10s - 30s | ~15s - 40s | ~15s - 30s | **$< 0.05\text{s}$ (Radix hit)** |
| **Concurrent Throughput** | Low (declines under load) | Medium (GQA-dependent) | High (PagedAttention) | **Highest (Radix hit + batching)** |
| **Baseline Memory** | **Lowest** (GGUF `mmap`) | High (Compiler buffers) | High (PyTorch overhead) | High (PyTorch overhead) |
| **KV Cache VRAM Allocation** | Static & deterministic | Dynamic | Pre-allocates VRAM pool | Pre-allocates VRAM pool |
| **RAM/VRAM Offloading** | **Fully Supported** (Partial layers) | Unsupported | Unsupported | Unsupported |

#### **Key Tradeoffs:**
* **MLC-LLM vs. `llama.cpp`:** MLC-LLM achieves **2x to 3x faster decoding** due to compile-time TVM optimizations for specific target GPUs. However, it suffers from a **prefill slowdown (1.5x to 2x slower)** on long contexts and has a **1.2x to 1.5x larger memory footprint**. It also lacks the fast loading benefits of GGUF `mmap`.
* **SGLang & vLLM vs. `llama.cpp`:** Both offer **1.2x to 1.8x faster single-stream generation** and **3x to 5x higher concurrent throughput** due to continuous batching. SGLang dominates in multi-turn agent tasks where the **Radix Cache** provides **100x+ faster TTFT** by caching shared history blocks. However, SGLang and vLLM must load all weights in VRAM (no RAM fallback) and pre-allocate the remaining VRAM (e.g. 80-90% of GPU memory) for the KV cache page pool at startup.

---

### 10.2 Embedding & Reranking: TEI vs. llama.cpp

| Feature / Metric | `llama.cpp` (Current) | `Hugging Face TEI` |
|---|---|---|
| **Latency (Single)** | ~10ms - 50ms | **Sub-millisecond (< 1ms)** |
| **Throughput (Batch)** | Low | **5x to 10x higher** |
| **Attention Engine** | GGML CPU/GPU kernels | Rust Candle + FlashAttention |
| **Memory Footprint** | ~500 MB - 1.5 GB | **~300 MB - 1.5 GB** (Highly efficient) |
| **Dynamic Batching** | Basic | **Native Continuous Queuing** |

* **Tradeoff:** TEI is **5x to 10x faster** in throughput with practically zero dispatch overhead. It uses native Rust bindings (Candle) and FlashAttention, providing equal or better memory efficiency than `llama.cpp` while delivering production-grade embedding speeds.

---

### 10.3 Image Generation: stable-fast vs. stable-diffusion.cpp

| Feature / Metric | `stable-diffusion.cpp` | `stable-fast` (PyTorch Compilation) |
|---|---|---|
| **Underlying Engine** | Pure C++ GGML | PyTorch + CUDA/ROCm Compiler |
| **Generation Speed** | Baseline | **1.2x to 1.5x faster** (1.5x-2x faster than raw PyTorch) |
| **Warmup/Compile Time** | **Instant (No compile)** | Slow (First generation compile takes 1-2 minutes) |
| **VRAM Footprint** | **~2 GB - 3 GB** (Highly optimized Q8/Q5) | ~4 GB - 6 GB (Full PyTorch + compiler runtime) |

* **Tradeoff:** `stable-fast` delivers **1.2x to 1.5x faster image generation** than `stable-diffusion.cpp`, but requires a slow initial warmup compilation and uses **twice the VRAM** (~4-6 GB vs ~2-3 GB) due to PyTorch runtime overheads.

---

## 11. FlashInfer Ecosystem & Alternative Serving Engines

### 11.1 FlashInfer AUR Package Status
The Arch User Repository (AUR) contains package scripts for FlashInfer:
* **`python-flashinfer` (AUR):** Available ([AUR Page](https://aur.archlinux.org/packages/python-flashinfer) \| [Source GitHub](https://github.com/flashinfer-ai/flashinfer)). Build script to compile FlashInfer's PyTorch attention binding kernels from source.
* **`python-flashinfer-rocm` (AUR):** Available ([AUR Page](https://aur.archlinux.org/packages/python-flashinfer-rocm) \| [Source GitHub](https://github.com/flashinfer-ai/flashinfer)). Optimized build variant specifically mapping compiler and environment targets for AMD GPUs under the ROCm runtime.

---

### 11.2 MLCEngine Characterization & Tradeoffs (from MLC October 2024 Blog)
According to the MLC community's benchmarks characterizing low-latency LLM serving (Llama3 8B and 70B on H100):
1. **Speculative Decoding Scaling Limits:**
   - Speculative decoding is highly effective at reducing latency under **low request concurrency** (Batch Size = 1 to 8) and high target throughputs (e.g. > 70–100 tokens/sec), where memory-bandwidth bottlenecks dominate.
   - However, under **high concurrency** (Batch Size > 32) when the engine transitions from memory-bandwidth bound to compute-bound, the overhead of verifying the draft model's token predictions matches or exceeds normal execution, yielding **marginal latency gains** (as detailed in the [MLC Blog](https://blog.mlc.ai/2024/10/10/optimizing-and-characterizing-high-throughput-low-latency-llm-inference)).
2. **Tensor Parallelism (TP) Tradeoffs:**
   - In serving heavy models (e.g., Llama-3-70B), **TP=4** provides the optimal balance of throughput per GPU and batch processing capacity.
   - Increasing split counts to **TP=8** yields the absolute lowest latency per token but reduces overall system throughput efficiency due to inter-GPU communication bounds.

---

### 11.3 Projects Integrating FlashInfer & Replacement Viability

| Project | FlashInfer Role | ROCm/HIP Status | Vulkan Status | Viability as a Replacement |
|---|---|---|---|---|
| **[LoRAX](https://github.com/predibase/lorax)** | Uses FlashInfer's multi-tenant/multi-LoRA kernels (like `sgmv`) to speed up attention calculation across different LoRAs | **Supported** (Via standard PyTorch ROCm) | **Unsupported** | **Viable replacement for SGLang/vLLM (Specialized LoRA Chat).** Best-in-class if serving hundreds of dynamically switched fine-tuned LoRA adapters on a single base LLM (e.g., Qwen 35B). |
| **[LightLLM](https://github.com/ModelTC/lightllm)** | Utilizes FlashInfer for optimized attention computation | **Experimental** (Supports PyTorch ROCm) | **Unsupported** | **Viable replacement for SGLang/vLLM (LLM Chat).** A lightweight Python-based alternative, but lacks the community size and feature-set of SGLang/vLLM. |


---

## 12. Quantization & KV Cache Compatibility (ROCm vs. Vulkan Eligibility)

To run your **35B MoE** model on a **24 GB RX 7900 XTX** dGPU (or system RAM for Vulkan iGPU offloading) alongside other local services, chat engines must meet the following eligibility criteria:
1. **Model Weights:** Must support **Q4 quantization** (AWQ, GPTQ, or GGUF) to restrict model weight memory to $\approx 19.0\text{ GB}$.
2. **KV Cache:** Must support **at least Q8 quantization** (1.0 byte per element, or equivalent FP8/INT8 footprint) and preferably **Q4 quantization** (0.5 bytes per element) to keep memory overhead low for long contexts.

Below is the eligibility and fitness evaluation for the major chat engine possibilities across ROCm and Vulkan:

### 12.1 ROCm/HIP Chat Engine Options (Minimum 2 Options)

#### **Option A: SGLang (Eligible — Highly Fit)**
* **Q4 Model Weights:** **Supported** (AWQ & GPTQ formats).
* **KV Cache Quantization:** **Supported (FP8/INT8).** SGLang does not support integer Q8 or Q4 KV cache formats, but natively supports **FP8 KV cache** (`--kv-cache-dtype fp8`) which uses **1.0 byte per element** (the exact same memory footprint as Q8). The FP8 format runs natively on RDNA3 FP8 tensor cores, offering near-lossless precision and high speed.
* **VRAM / RAM Offloading:** Unsupported (requires all weights to fit in VRAM).
* **Fitness:** **High.** Exceptional decoding speeds and best-in-class VRAM efficiency for multi-turn conversations due to RadixAttention prefix caching.

#### **Option B: vLLM (Eligible — Highly Fit)**
* **Q4 Model Weights:** **Supported** (GGUF, AWQ, and GPTQ formats). Can parse your existing GGUF model files natively.
* **KV Cache Quantization:** **Supported (FP8/INT8).** Like SGLang, vLLM supports FP8/INT8 formats (1.0 byte per element, matching Q8 memory usage). It does not support Q4 KV cache.
* **VRAM / RAM Offloading:** Unsupported.
* **Fitness:** **High.** Very stable production engine with native GGUF weight parsing and robust speculative decoding.

#### **Option C: LightLLM (Not Eligible — Low Fitness)**
* **Q4 Model Weights:** **Unsupported (Native).** LightLLM cannot natively load standard AWQ/GPTQ/GGUF weights. It requires converting them back to `bf16` via `LLMC` for online quantization, which defeats the VRAM-saving purpose.
* **KV Cache Quantization:** **Supported (FP8/INT8).** Natively implements fused FP8 KV copying and MLA optimizations.
* **Fitness:** **Low.** Ineligible due to the lack of native Q4 weight parsing, which prevents fitting the 35B model under the 19 GB VRAM threshold.

---

### 12.2 Vulkan Chat Engine Options (Minimum 2 Options)

#### **Option A: llama.cpp / llama-server (Eligible — Highly Fit)**
* **Q4 Model Weights:** **Supported** (GGUF format).
* **KV Cache Quantization:** **Supported (q8_0, q4_0, q4_1).** Fully supports both Q8 (`q8_0`) and Q4 (`q4_0` / 0.5 bytes per element) cache formats.
* **VRAM / RAM Offloading:** **Fully Supported.** Can dynamically partition layers between system RAM and VRAM.
* **Fitness:** **High.** The leanest memory overhead available. It is the only engine that supports **Q4 KV Cache** (`q4_0`), saving 50% more context memory than SGLang/vLLM. It is the optimal engine for resource-constrained Vulkan execution.

#### **Option B: MLC-LLM (Eligible — Medium Fit)**
* **Q4 Model Weights:** **Supported** (via MLC custom compiled weight format).
* **KV Cache Quantization:** **Supported (Q4, Q8).** Can compile custom KV cache quantization layouts via TVM configuration flags.
* **VRAM / RAM Offloading:** Unsupported.
* **Fitness:** **Medium.** Achieves fast Vulkan decoding, but lacks instant GGUF weight loading (`mmap`) and has slower prefill on long contexts.
