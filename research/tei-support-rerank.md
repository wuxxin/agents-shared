# Implementation Plan - Add TEI Engine to local-rerank.sh

Add TEI (Text Embeddings Inference) as a second engine alongside `llama-server` in [local-rerank.sh](file:///home/wuxxin/agent-shared/code/agents-shared/assistants/local-rerank.sh), defaulting to `jinaai/jina-reranker-v3` with 2 parallel × 16K max context. The implementation mirrors the dual-engine pattern established in [local-embedding.sh](file:///home/wuxxin/agent-shared/code/agents-shared/assistants/local-embedding.sh).

## User Review Required

> [!IMPORTANT]
> **TEI Reranker Endpoint Compatibility**
> TEI exposes the reranking endpoint at **`POST /rerank`** (not `/v1/rerank`).
> `llama-server` exposes it at **`POST /v1/rerank`** (Cohere-compatible path).
>
> `local-router` currently proxies `/v1/rerank` to the rerank backend. We need to confirm that `local-router` can handle the path translation (`/v1/rerank` → `/rerank`) when TEI is the backend, or whether the TEI instance should be called directly by Hindsight (bypassing the router).

> [!IMPORTANT]
> **jina-reranker-v3 runs on TEI's Python (PyTorch) backend**
> The model uses a Qwen3-0.6B causal decoder backbone with custom `JinaForRanking` code, requiring `trust_remote_code=True`. TEI auto-detects this and spawns a Python gRPC subprocess. The same `sitecustomize.py` patch (already installed by `local-embedding.sh`) is needed for the `isinstance` and `trust_remote_code` fixes.

> [!WARNING]
> **VRAM: Running TEI Reranker + TEI Embedding Simultaneously**
> Two separate TEI processes incur ~350–400 MB extra CUDA/HIP context overhead vs. a hypothetical single process. Total estimated VRAM for both:
> - Embedding TEI (pplx-embed 0.6B, 2×8K): ~1.6 GiB idle, ~2 GiB peak
> - Reranker TEI (jina-reranker-v3 0.6B, 2×16K): ~1.6 GiB idle, ~2.6 GiB peak
> - Combined peak: **~4.6 GiB** (vs. ~3.8 GiB hypothetical single-process)
>
> This fits within the 24 GB RX 7900 XTX budget alongside the ~19 GiB main chat model.

## Open Questions

> [!IMPORTANT]
> 1. **Router path translation**: Does `local-router` already translate `/v1/rerank` → `/rerank` for TEI, or do we need to update the router config? Alternatively, should Hindsight call the TEI reranker directly (port `20086`) instead of through the router (port `21080`)?
>
> 2. **sitecustomize.py sharing**: Both `local-embedding.sh` and `local-rerank.sh` need the same `sitecustomize.py` patch in `~/.config/systemd/user/`. Since `local-embedding.sh` already installs it during `install`, should `local-rerank.sh` just verify it exists (and warn if missing), or should it also install/overwrite it independently?
>
> 3. **Benchmark test adaptation**: The current `cmd_test --benchmark` calls `benchmark-helper.py --mode rerank`. TEI's rerank endpoint uses different request/response format (`POST /rerank` with `texts` field vs. `/v1/rerank` with `documents` field). Should the benchmark test auto-detect the engine and adjust the endpoint, or should we add a `--tei` flag?

## Proposed Changes

### 1. Update local-rerank.sh with Dual-Engine Support

#### [MODIFY] [local-rerank.sh](file:///home/wuxxin/agent-shared/code/agents-shared/assistants/local-rerank.sh)

##### `load_env()` — Split into `LRR_TEI_*` / `LRR_LLAMA_*` namespaces

```bash
load_env() {
    # General parameters
    LRR_PORT=20086
    LRR_HOST=127.0.0.1
    LRR_ENGINE=tei

    # llama-server parameters (legacy, conservative defaults)
    LRR_LLAMA_MODEL=/data/public/machine-learning/models/reranker/Qwen3-Reranker-0.6B.Q4_K_M.gguf
    LRR_LLAMA_N_CTX=12288
    LRR_LLAMA_N_UBATCH=12288
    LRR_LLAMA_N_GPU_LAYERS=99
    LRR_LLAMA_THREADS=8
    LRR_LLAMA_PARALLEL=2
    LRR_LLAMA_EXTRA_ARGS="--flash-attn on"
    LRR_LLAMA_DEVICE=""

    # TEI parameters (jina-reranker-v3, 2 parallel, 32k max batch tokens)
    LRR_TEI_MODEL=/data/public/machine-learning/models/reranker/jina-reranker-v3
    LRR_ALIAS=jina-reranker
    LRR_TEI_MAX_CONCURRENT=2
    LRR_TEI_MAX_BATCH_TOKENS=32768
    LRR_TEI_EXTRA_ARGS=""
    LRR_TEI_DEVICE=""

    # Source env file ...
    # Engine dispatch (same pattern as local-embedding.sh) ...
}
```

##### `get_tei_args()` — New TEI argument builder

```bash
get_tei_args() {
    local -n out_tei_args=$1
    out_tei_args=(
        --model-id "${LRR_MODEL}"
        --port "${LRR_PORT}"
        --hostname "${LRR_HOST}"
    )
    # No --pooling for reranker (TEI auto-detects from model config)
    if [[ -n "${LRR_TEI_MAX_CONCURRENT:-}" ]]; then
        out_tei_args+=(--max-concurrent-requests "${LRR_TEI_MAX_CONCURRENT}")
    fi
    if [[ -n "${LRR_TEI_MAX_BATCH_TOKENS:-}" ]]; then
        out_tei_args+=(--max-batch-tokens "${LRR_TEI_MAX_BATCH_TOKENS}")
    fi
    # ... extra args
}
```

##### Engine dispatch in `generate_service_file()`, `cmd_exec()`, `cmd_cat()`

Same pattern as [local-embedding.sh](file:///home/wuxxin/agent-shared/code/agents-shared/assistants/local-embedding.sh): check `LRR_ENGINE` and dispatch to `get_tei_args` or `get_llama_args`.

##### `cmd_install()` — Install `sitecustomize.py` for TEI Python backend

Copy `scripts/tei-helper.py` → `~/.config/systemd/user/sitecustomize.py` if not already present, set `TRUST_REMOTE_CODE=true` and `PYTHONPATH` in the generated env file.

---

### 2. Update generate_env_file() with Dual-Engine Sections

```
# local-rerank.env

LRR_ENGINE=tei
LRR_ALIAS=jina-reranker
LRR_PORT=20086
LRR_HOST=127.0.0.1

# TEI ENGINE SETTINGS
LRR_TEI_MODEL=/data/public/machine-learning/models/reranker/jina-reranker-v3
LRR_TEI_MAX_CONCURRENT=2
LRR_TEI_MAX_BATCH_TOKENS=32768
# LRR_TEI_DEVICE="rocm:0"

TRUST_REMOTE_CODE=true
PYTHONPATH=~/.config/systemd/user

# LLAMA ENGINE SETTINGS
LRR_LLAMA_MODEL=/data/public/machine-learning/models/reranker/Qwen3-Reranker-0.6B.Q4_K_M.gguf
# LRR_ALIAS=qwen3-reranker
LRR_LLAMA_N_CTX=16384
LRR_LLAMA_N_UBATCH=16384
LRR_LLAMA_N_GPU_LAYERS=99
LRR_LLAMA_THREADS=8
LRR_LLAMA_PARALLEL=2
LRR_LLAMA_EXTRA_ARGS="--flash-attn on"
```

---

### 3. Update local-rerank.md Documentation

#### [MODIFY] [local-rerank.md](file:///home/wuxxin/agent-shared/code/agents-shared/assistants/local-rerank.md)

- Update header to mention dual-engine (TEI default + llama fallback)
- Document `LRR_ENGINE` selection (`tei` or `llama`)
- Document `LRR_TEI_*` configuration parameters
- Update default model description: `jinaai/jina-reranker-v3` (600M, Qwen3 backbone, listwise LBNL architecture)
- Update curl examples to show both TEI (`/rerank`) and llama (`/v1/rerank`) endpoints
- Document `TRUST_REMOTE_CODE` and `sitecustomize.py` requirements

---

### 4. Update local-memory.sh Reranker Default

#### [MODIFY] [local-memory.sh](file:///home/wuxxin/agent-shared/code/agents-shared/assistants/local-memory.sh)

Update `DEFAULT_HINDSIGHT_API_RERANKER_COHERE_MODEL` from `qwen3-reranker` to `jina-reranker` to match the new default `LRR_ALIAS`.

---

## Verification Plan

### Automated Tests
```bash
# Generate test config
./assistants/local-rerank.sh install --no-start --new-config

# Verify generated config
./assistants/local-rerank.sh cat

# Verify env resolution with override
LRR_TEI_MAX_CONCURRENT=4 ./assistants/local-rerank.sh run printenv LRR_TEI_MAX_CONCURRENT

# Lint
shfmt -i 4 -d assistants/local-rerank.sh
```

### Manual Verification
- Verify TEI reranker starts and serves on port 20086
- Verify `/rerank` endpoint returns correct relevance scores
- Verify Hindsight can reach the reranker through `local-router`
