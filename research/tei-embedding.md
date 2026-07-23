# TEI Embedding Research Notes - Qwen3-Embedding-0.6B

This document details our findings, configuration details, and execution parameters when serving `Qwen3-Embedding-0.6B` using Text Embeddings Inference (TEI) on AMD ROCm.

## Model Configuration & Serving Parameters
* **Model ID:** `/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B`
* **Port:** `50082`
* **Data Type:** `bfloat16`
* **Pooling:** `mean` (must be explicitly provided on the CLI command since the HF repository lacks a `1_Pooling/config.json`).

### Execution Command
The server was started via:
```bash
text-embeddings-router \
  --model-id /data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B \
  -p 50082 \
  --pooling mean
```

---

## Technical Findings

1. **Flash-Attention Fallback:**
   Because the ROCm system doesn't run CUDA-based flash-attention (and `flashinfer` is only dynamically checked for certain architectures), our patched `tei-rocm` server safely intercepts `flash_attn` import errors. The server falls back to PyTorch's native **Scaled Dot Product Attention (SDPA)**. This ensures standard, out-of-the-box hardware acceleration without crashing on missing CUDA modules.
   
2. **Cold-Start Latency:**
   On the first cold run, PyTorch takes approximately 9.8 seconds to compile and load ROCm kernels. Once loaded, the HTTP server initializes immediately.
   
3. **Inference Latency:**
   Under TEI, request tokenization takes ~1.3ms, and GPU forward passes take ~24ms, resulting in an end-to-end latency of **~25ms** for short texts.

---

## Validation
Functionality was verified by querying `http://localhost:50082/v1/embeddings` using the system script:
```bash
./local-embedding.sh test
```
The endpoint successfully returned high-precision dense embedding vectors.

---

## Embedding Alternatives & Comparative Analysis

Below is a comparison of different embedding models evaluated for local deployment:

| Metric / Parameter | `Alibaba-NLP/gte-Qwen2-1.5B-instruct` (Upgrade) | `pplx-embed-context-v1-0.6b` | `BAAI/bge-m3` | `Qwen3-Embedding-0.6B` (Default) |
| :--- | :--- | :--- | :--- | :--- |
| **Model Type** | Causal LM (Decoder) | Bidirectional Decoder | Encoder (Bi-Encoder) | Causal LM (Decoder) |
| **Parameters** | `1.5 Billion` | `0.6 Billion` (600M) | `567 Million` | `0.6 Billion` (570M) |
| **Context Window** | `32,768` (32K) tokens | `32,768` (32K) tokens | `8,192` tokens | `32,768` (32K) tokens |
| **Embedding Dimension**| `1536` | `1024` | `1024` (Supports Matryoshka) | `1024` |
| **Native TEI Support** | **Yes** (Native Rust backend) | **Yes** (since TEI v1.9.2) | **Yes** (Native Rust backend) | **Yes** (via Candle) |
| **Format & Disk Size** | `3.0 GB` (fp16 Safetensors) | `1.2 GB` (fp16/bf16 Safetensors) | `1.14 GB` (fp16 Safetensors) | `1.2 GB` (fp16), `600 MB` (GGUF Q8_0) |
| **GPU VRAM Baseline** | **~3.2 GB VRAM**. No KV cache. | **~1.3 GB VRAM**. No KV cache. | **~1.2 GB VRAM**. Standard stable layout. | **~900 MB VRAM** (Q8_0 GGUF). Requires KV cache. |
| **German Support** | **Excellent**. Broad multilingual. | **Good** (MIRACL-DE: 60.7%). | **Excellent**. Highly optimized (100+ lang). | **Good**. Solid German baseline coverage. |

### Recommendations
* **High-Performance Upgrade:** **`Alibaba-NLP/gte-Qwen2-1.5B-instruct`** offers outstanding MTEB retrieval results and native TEI support for a modest 3.2 GB VRAM footprint.
* **For German Language tasks:** **`BAAI/bge-m3`** is highly recommended for standard 8K context native TEI deployment.
* **For Long-Context English & German:** **`pplx-embed-context-v1-0.6b`** is optimized for chunk retrieval under TEI, providing solid German semantic representation (MIRACL-DE: 60.7%).

---

## Quantization Research (bf16 to bf8 / fp8 conversion)

We researched whether converting models from `bf16`/`fp16` to `bf8`/`fp8` would enable native execution under standard TEI:

1. **Standard TEI Compatibility:**
   **No.** The standard open-source TEI codebase does not natively support FP8 (including `e4m3` or `e5m2` formats) as a general configuration option or loading target.
2. **Quantization Alternatives in TEI:**
   TEI does natively support **INT8 quantization** (both activation and weight quantization) using the `--quantize` CLI option (values: `bitsandbytes`, `octo`).
3. **Execution Conclusion:**
   If memory bandwidth or VRAM is constrained, rather than manually quantizing to FP8 (which TEI's Candle Rust backend will fail to parse), you should utilize TEI's built-in **INT8** quantization runtime options.
