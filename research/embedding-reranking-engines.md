# Embedding & Reranking Alternative Engines Research

**Date**: 2026-07-26
**Scope**: Evaluate alternatives to the current TEI + llama-server split for embedding and reranking on AMD ROCm (RX 7900 XTX, 24GB VRAM, Arch Linux).
**Decision**: Stick with TEI (text-embeddings-inference) for embeddings and reranking. Select new models within the TEI ecosystem.

---

## 1. Why We Researched Alternatives

The current setup uses two different engines:

| Service | Engine | Model | Port | Format |
|---|---|---|---|---|
| Embedding | TEI (`tei-rocm`) | Qwen3-Embedding-0.6B | 50082 | fp16 Safetensors |
| Reranking | llama-server | Qwen3-Reranker-0.6B | 50086 | Q4_K_M GGUF |

This split is operationally suboptimal:
- Two different engines with different configuration models
- llama-server wastes VRAM on KV cache for non-generative workloads
- Long-term goal of jina-reranker-v3 (131K context) requires a unified engine

We evaluated whether a single engine could serve both embedding and reranking.

---

## 2. Alternatives Evaluated

### 2.1 Engine-Level Alternatives

| Engine | Embed | Rerank | ROCm | Quant | AUR | jina-reranker-v3 | Verdict |
|---|---|---|---|---|---|---|---|
| **llama.cpp** | ✅ | ✅ | ✅ HIP | ✅ GGUF (Q4_K_M) | ✅ | 🟡 PR #22576 (draft) | Top alternative; needs 2 processes (`--embedding` / `--reranking` mutually exclusive) |
| **Infinity** (michaelfeil) | ✅ | ✅ BERT | ✅ MIGraphX EP | 🟡 FP16 GPU, INT8 CPU | 🔴 Docker | ❌ (listwise incompatible) | Best unified ONNX option; Docker-recommended, AUR painful |
| **vLLM** | ✅ | ✅ jina-v3 | ✅ HIP | ✅ | 🔴 | ✅ (native since v0.20) | Eliminated: 6-10GB VRAM overhead for 0.6B models |
| **SGLang** | ✅ | 🟡 limited | ✅ HIP | ✅ | 🔴 heavy | ❌ | Overkill for 0.6B; no JinaForRanking |
| **Ollama** | ✅ `/api/embed` | ❌ | ✅ HIP | ✅ GGUF | ✅ | ❌ | No reranking endpoint |
| **Candle** (HF Rust) | ✅ Bert | ❌ | ❌ CUDA-only | ❌ | ✅ | ❌ | No ROCm, no rerank, no server |
| **Burn** (tracel-ai) | ❌ DIY | ❌ DIY | ✅ `burn-rocm` | 🟡 possible | 🔴 | ❌ | Framework, not server; compile-time ONNX import |
| **LM Studio** | ✅ | ✅ | ✅ HIP | ✅ | 🔴 binary | ❌ | Works but proprietary, no headless AUR |

### 2.2 ONNX Runtime + MIGraphX Ecosystem

ONNX Runtime is the standard inference runtime for ONNX models. On AMD ROCm:
- **ROCmExecutionProvider**: Removed since ORT 1.23 (deprecated)
- **MIGraphXExecutionProvider**: The only AMD GPU path in ORT ≥ 1.24 (our version: 1.24.4)

Our system has `MIGraphXExecutionProvider` active (`python-onnxruntime-opt-rocm 1.24.4-8`).

#### ONNX-based embedding/reranking servers

| Server | Embed | Rerank | MIGraphX | API | Notes |
|---|---|---|---|---|---|
| **Zephyr** (nakedcity) | ✅ | ❌ | ✅ Native | OpenAI `/v1/embeddings` | Embeddings-only; per-engine worker isolation; no rerank |
| **Infinity** | ✅ | ✅ BERT | ✅ EP fallback chain | OpenAI + Cohere | Docker-recommended; jina-v3 unsupported |
| **Triton (ROCm fork)** | 🟡 custom | 🟡 custom | ✅ Accelerator | Custom (tritonclient) | Production-grade overkill; no native embed API |
| **TEI + ONNX** | ✅ (`-F ort`) | ✅ | ❌ Not tested | OpenAI | ONNX backend is CPU/NVIDIA only; ROCm path is PyTorch-only |

### 2.3 Library Ecosystems — Servers Built on Key Crates

We searched for embedding/reranking HTTP servers built on the four most promising Rust/Python libraries. Results were limited:

#### ort-rs (pykeio/ort) — Rust ONNX Runtime bindings

| Project | Stars | Embed | Rerank | Server | MIGraphX |
|---|---|---|---|---|---|
| **Engram/Kleos** | 150★ | ✅ bge-m3 | ✅ granite | ✅ Axum | 🟡 patchable |
| **TEI (HuggingFace)** | 5K+★ | ✅ | ✅ | ✅ Axum/gRPC | ❌ (PyTorch-only for ROCm) |
| **fashion-clip-rs** | 15★ | ✅ (image) | ❌ | ✅ gRPC | 🟡 |
| **gte-rs** | 12★ | ✅ | ✅ | ❌ Library only | ✅ (via orp features) |
| **orp** (pipeline framework) | 40★ | — | — | ❌ Framework | ✅ `rocm`/`migraphx` |

No standalone ort-rs embedding/reranking server exists. The `gte-rs → orp → ort` chain supports MIGraphX, but **zero crates.io dependents** for gte-rs — completely unadopted.

#### fastembed-rs (Anush008/fastembed-rs) — Rust embedding library

| Project | Stars | Embed | Rerank | Server | Notes |
|---|---|---|---|---|---|
| **xberg-io/xberg** | 8.7K★ | ✅ | ✅ | ✅ Axum + MCP | Document intelligence platform (overkill) |
| **Ammar-Alnagar/Axion** | 1★ | ✅ | ✅ | ✅ Axum | Alpha; OAI-compatible |
| **101t/embedding_service** | 0★ | ✅ | ❌ | ✅ Actix-web | Prototype |
| **Skelf-Research/embedcache** | 0★ | ✅ | ❌ | ✅ Actix-web | Embed cache |

No dedicated, production-ready server wraps fastembed-rs's `TextRerank` over HTTP.

#### FastEmbed Python (qdrant/fastembed)

| Project | Stars | Embed | Rerank | GPU | Notes |
|---|---|---|---|---|---|
| **heshinth/LocalEmbed** | 4★ | ✅ OAI | ❌ | CUDA Docker | Active |
| **OBAA/fastembed-server** | 5★ | ✅ (non-OAI) | ❌ | CUDA Docker | Prometheus/Grafana |
| **fastembed serve CLI** | — | ✅ OAI | ❌ | CUDA | Issue #571, **not yet merged** |

No ROCm support in any FastEmbed Python server. All GPU paths are CUDA-only.

#### Burn (tracel-ai/burn) — Rust ML framework

| Project | Stars | Embed | Rerank | Server | ROCm |
|---|---|---|---|---|---|
| **burn-lm** (official) | 225★ | ❌ | ❌ | Pre-alpha | ✅ `rocm` feature |
| **Furnace** | 64★ | ❌ | ❌ | ✅ Axum | ⚠️ WGPU/Vulkan |
| **gllm** | crate | ✅ 60+ models | ✅ 12 models | ❌ Library | ⚠️ WGPU/Vulkan |

Burn-LM is the official path for production serving with first-class ROCm, but it's pre-alpha (v0.0.1). No embedding/reranking server exists today.

### 2.4 MIGraphX Production Adoption

MIGraphX is AMD's native graph compiler — it takes ONNX models, applies AMD-specific kernel fusion and GEMM autotuning, and compiles for efficient GPU inference. Key adopters:

| App | Stars | MIGraphX Use |
|---|---|---|
| **Immich** | 55K★ | CLIP embeddings + facial recognition |
| **Frigate** | 20K★ | Object detection via `-rocm` Docker image |
| **Apollo** | 25K★ | Autonomous driving perception |
| **darktable** | 10K★ | AI image processing (notes 5-30min first-compile) |
| **vllm/semantic-router** | — | Embedding + classification ("FASTER than ROCm EP") |

At the ONNX Runtime API level, switching to MIGraphX is a one-string change: `"CUDAExecutionProvider"` → `"MIGraphXExecutionProvider"`. The interface is interchangeable, but MIGraphX has a multi-minute first-run compilation that caches to disk.

---

## 3. jina-reranker-v3 Compatibility

jina-reranker-v3 uses a **listwise** architecture (`JinaForRanking`) — a causal decoder with an MLP projector head (1024 → 512 → 256). This is fundamentally different from standard cross-encoder classification models.

| Engine | jina-reranker-v3 Support | Notes |
|---|---|---|
| **TEI** | ⚠️ Needs patch | Rust router recognizes `"Ranking"` suffix, but Python backend `__init__.py` only checks `"Classification"` |
| **vLLM** | ✅ Since v0.20 | Native `JinaForRanking` support |
| **llama.cpp** | 🟡 PR #22576 (draft) | Projector graph + `POOLING_TYPE_RANK`; GGUF weights at `jinaai/jina-reranker-v3-GGUF` |
| **Infinity** | ❌ | Only supports `AutoModelForSequenceClassification` |
| **SGLang** | ❌ | Cross-encoder abstraction incompatible |
| **FastEmbed** | ❌ | ONNX cross-encoder only |

The TEI gap is small: `backends/python/server/text_embeddings_server/models/__init__.py` lines 112 and 132 check for `"Classification"` in architecture names but not `"Ranking"`. A patch adding `"Ranking"` alongside `"Classification"` in both checks would unblock jina-reranker-v3 on TEI.

---

## 4. Decision: Stick with TEI

After evaluating all alternatives, we will keep TEI as the embedding and reranking engine.

**Reasons:**

1. **It works today.** TEI serves `pplx-embed-context-v1-0.6b` (embedding, port 50082) and can serve BERT-based rerankers natively. The build infrastructure (PKGBUILD) is already fixed for glibc 2.41.

2. **No KV cache overhead.** Unlike llama-server, TEI runs pure forward-pass inference — zero wasted VRAM on KV cache slots for non-generative workloads.

3. **jina-reranker-v3 path is a small patch away.** A ~5 line change in the Python backend enables jina-reranker-v3. This is far less work than adopting any alternative engine.

4. **All alternatives have critical gaps:**
   - **llama.cpp**: Needs 2 server processes; jina-v3 PR not merged
   - **Infinity**: Docker-only on ROCm; AUR infeasible; no jina-v3
   - **All ONNX servers**: No MIGraphX production embedding server exists (Zephyr lacks reranking)
   - **ort-rs/gte-rs**: Unadopted; building a server from scratch is high effort
   - **Burn/FastEmbed**: Library-only; no production server wrappers

5. **TEI's Python backend uses PyTorch ROCm.** Our system has `python-pytorch-opt-rocm` with native RDNA3 HIP kernels. TEI's Python backend (required for Qwen-based models like pplx-embed and jina-reranker-v3) directly benefits from this.

---

## 5. Model Recommendations (TEI-Compatible)

### 5.1 Embedding Models

| Model | Params | Context | German (MIRACL) | TEI Backend | License | VRAM (4×8K) |
|---|---|---|---|---|---|---|
| **bge-m3** (BAAI) | 567M | 8K | 70.9 | Candle (native) | MIT | ~1.6 GB |
| **jina-embeddings-v3** | 685M | 8K | 71.8 | Candle (native) | CC-BY-NC 4.0 | ~1.8 GB |
| **pplx-embed-context-v1-0.6b** | 600M | 32K | 60.7 | Python (PyTorch) | Custom | ~1.95 GB |
| **gte-Qwen2-1.5B-instruct** | 1.5B | 32K | 66.2 | Python (PyTorch) | Apache 2.0 | ~3.4 GB |
| **jina-embeddings-v5-text-small** | 677M | 32K | 65.0 | Python (PyTorch) | CC-BY-NC 4.0 | ~2.15 GB |

**Recommended**: **bge-m3** for strong multilingual with permissive license (MIT), or **pplx-embed-context-v1-0.6b** for long context (32K) at minimal VRAM.

### 5.2 Reranking Models

| Model | Params | Context | German BEIR | TEI Backend | License | VRAM (4×8K) |
|---|---|---|---|---|---|---|
| **bge-reranker-v2-m3** (BAAI) | 567M | 8K | 57.2 | Candle (native) | MIT | ~1.6 GB |
| **jina-reranker-v2-base-multilingual** | 278M | 1K (sliding window) | 59.1 | Candle (Python fallback) | CC-BY-NC 4.0 | ~1.0 GB |
| **jina-reranker-v3** | 600M | 131K | 63.8 | Python (PyTorch) | CC-BY-NC 4.0 | ~2.05 GB |

**Recommended**: **bge-reranker-v2-m3** for permissive license + native TEI, or **jina-reranker-v3** once the Python backend patch is applied (for 131K context and listwise ranking of up to 64 documents in a single pass).

---

## 6. Architecture: Current vs. Target

### Current
```
embedding (50082) ← TEI → Qwen3-Embedding-0.6B (fp16)
reranking  (50086) ← llama-server → Qwen3-Reranker-0.6B (GGUF Q4_K_M)
```

### Target (Phase 1 — replace models, same engine structure)
```
embedding (50082) ← TEI → bge-m3 or pplx-embed-context-v1-0.6b
reranking  (50086) ← TEI → bge-reranker-v2-m3
```

### Target (Phase 2 — unified single engine)
```
embedding (50082) ← TEI → [chosen embed model]
reranking  (50086) ← TEI → [chosen rerank model, or jina-reranker-v3 after patch]
```

Both services run under TEI with no KV cache waste. The Python backend handles Qwen-based models (pplx-embed, jina-reranker-v3) while Candle handles BERT/XLM-RoBERTa models (bge-m3, bge-reranker-v2-m3).

---

## 7. Open Items

| Item | Priority | Effort | Notes |
|---|---|---|---|
| jina-reranker-v3 `__init__.py` patch | Medium | ~5 lines | Add `"Ranking"` checks alongside `"Classification"` in the Python backend model loader |
| llama.cpp jina-reranker-v3 (PR #22576) | Low | Track | Provides GGUF alt path if TEI patch is insufficient |
| `tei-rocm` PKGBUILD rebase | Low | Build test | Rebase on TEI 1.10+ when jina-v3 support lands upstream |

---

## 8. Key References

- Existing TEI config: `assistants/local-embedding.sh` and `assistants/local-rerank.sh`
- TEI PKGBUILD: `aur-packages/tei-rocm/PKGBUILD` (pkgrel=3, fixed glibc 2.41 build)
- Model benchmarks: `research/model-research.md`
- TEI embedding notes: `research/tei-embedding.md`
- TEI reranker notes: `research/tei-reranker.md`
- Cloned research repos: `aur-packages/scratch/tei-alternatives/{infinity,fastembed,llama.cpp}`
