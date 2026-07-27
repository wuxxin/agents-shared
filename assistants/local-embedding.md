# Local Text Embedding Service Guide

`local-embedding.sh` manages the local systemd user service (`local-embedding.service`) for generating high-density text embeddings used in search, retrieval-augmented generation (RAG), and agentic document indexing.

The service supports two backend engines via the `LMBD_ENGINE` configuration parameter:
1. **Llama-Server Engine (`LMBD_ENGINE=llama`, Default)**: Serves GGUF embedding models using `llama-server` (from `llama.cpp`). Default model: Qwen3-Embedding-0.6B Q8_0 GGUF with 6 × 8K true parallel context windows (single `llama_decode` call).
2. **TEI Engine (`LMBD_ENGINE=tei`, ABANDONED)**: Serves native safetensors models using Hugging Face's `text-embeddings-inference`. Kept for reference only; not actively used.

Note: Text embeddings can also be served combined inside the [local-chat.md](local-chat.md) service on port 50080 (enabled by default). When running in combined mode, the standalone `local-embedding` service on port 50082 should be disabled.

- **Source Code**: [HuggingFace - text-embeddings-inference](https://github.com/huggingface/text-embeddings-inference) / [ggml-org/llama.cpp](https://github.com/ggml-org/llama.cpp)
- **AUR Packages**: `tei-rocm` / `text-embeddings-inference` (TEI) and `llama.cpp-cuda` / `llama.cpp-hip` / `llama.cpp` (llama-server)

## Usage

```bash
# Install the service and environment configuration
./local-embedding.sh install [--no-start] [--new-config]

# Start/Stop/Restart the service
./local-embedding.sh start
./local-embedding.sh stop
./local-embedding.sh restart

# Check runtime status
./local-embedding.sh status

# Tail service stdout/stderr logs
./local-embedding.sh logs -f

# Edit service environment configuration and auto-restart
./local-embedding.sh edit

# Print service unit, environment config, and transient exec command
./local-embedding.sh cat

# Run API validation tests
./local-embedding.sh test

# Run standard embedding benchmark
./local-embedding.sh test --benchmark [--repeat XX]

# Run parallel hindsight embedding benchmark (98K tokens: 3 rounds of 4 parallel 8K requests)
./local-embedding.sh test --benchmark --hindsight [--repeat XX]

# Run active engine server as a transient systemd user service
./local-embedding.sh exec [--env KEY=VALUE]* [-- server-args...]

# Run a custom command inside the sandboxed environment
./local-embedding.sh run [--env KEY=VALUE]* <command> [args...]

# Spawn an interactive shell inside the sandboxed environment
./local-embedding.sh shell [--env KEY=VALUE]*
```

### In-Memory Environment Overrides

The `exec`, `run`, and `shell` subcommands support a repeatable `--env KEY=VALUE` parameter. When passed, these parameters:
1. Override the values loaded from the `.env` configuration file on disk.
2. Are exported in the local shell environment in-memory for foreground execution.
3. Are dynamically passed to `systemd-run` via `--setenv=KEY=VALUE` for transient background runs in systemd.

These overrides are kept transient, keeping the main `.env` configuration file untouched. For example, to test switching engines temporarily:
```bash
# Test running llama-server engine transiently
./local-embedding.sh exec --env LMBD_ENGINE=llama

# Test TEI engine on CPU
./local-embedding.sh exec --env LMBD_ENGINE=tei --env LMBD_TEI_DEVICE=cpu
```

---

## Supported Engines & Models

### 1. TEI Engine (`LMBD_ENGINE=tei`, ABANDONED — reference only)

Serves bidirectional and causal decoder embedding models natively using `text-embeddings-router` (`tei-rocm` package).

#### Default Model: `pplx-embed-context-v1-0.6b`

- **Model Path**: `/data/public/machine-learning/models/embedding/pplx-embed-context-v1-0.6b`
- **Architecture**: Bidirectional Qwen3-based encoder backbone (modified via diffusion-based pretraining).
- **Parameters**: 600M (~1.2 GB disk size in fp16/bf16 Safetensors).
- **Max Context**: 32,768 (32K) tokens.
- **Embedding Dimension**: 1024 dense vectors (supports Matryoshka Representation Learning and INT8/binary output).
- **Pooling**: `mean` pooling over all token representations (`LMBD_TEI_POOLING="mean"`).
- **License**: Custom (Perplexity AI).

#### TEI Configuration Defaults

| Parameter | Default | Description |
|-----------|---------|-------------|
| `LMBD_ENGINE` | `tei` | Engine selector (`tei` or `llama`) |
| `LMBD_TEI_MODEL` | `/data/public/machine-learning/models/embedding/pplx-embed-context-v1-0.6b` | Path to Safetensors model directory |
| `LMBD_ALIAS` | `pplx-embedding` | Client model alias header |
| `LMBD_TEI_POOLING` | `mean` | Pooling layer override (`mean`, `cls`, `last`, etc.) |
| `LMBD_TEI_MAX_CONCURRENT` | `4` | Max concurrent request slots |
| `LMBD_TEI_MAX_BATCH_TOKENS` | `32768` | Max total tokens in a dynamic batch |
| `LMBD_TEI_DEVICE` | `""` (auto) | Target device (`rocm:0`, `rocm:1`, `vulkan:0`, `cpu`, `auto`) |
| `LMBD_TEI_EXTRA_ARGS` | `""` | Additional flags for `text-embeddings-router` |
| `TEI_ROUTER_BIN` | `text-embeddings-router` | Path to TEI router binary |

#### Helper Patch (`sitecustomize.py`)

When installing the TEI service (`./local-embedding.sh install`), the installer automatically copies `scripts/tei-helper.py` to `~/.config/systemd/user/sitecustomize.py` (and removes it upon `uninstall`).

This sitecustomize patch solves two Python gRPC / Hugging Face backend compatibility issues:
1. **Dynamic Import Identity Mismatch**: Patches `isinstance` checks to prevent `AutoModel` re-import mismatches when TEI spawns sentence-transformers in Python subprocesses.
2. **Remote Code Trust**: Forces `trust_remote_code=True` when loading custom architecture files (`configuration_qwen3.py`, `modeling_qwen3.py`) used by models such as Perplexity `pplx-embed-context`.

---

### 2. Llama-Server Engine (`LMBD_ENGINE=llama`, Default)

Serves GGUF embedding models via `llama-server`. Uses non-unified partitioned KV cache for true parallel batching — all 6 slots batch into a single `llama_decode()` call.

#### Default Model: Qwen3-Embedding-0.6B Q8_0 GGUF

| Property | Value |
|---|---|
| **Source** | [iyanello/Qwen3-Embedding-0.6B-GGUF](https://huggingface.co/iyanello/Qwen3-Embedding-0.6B-GGUF) (fixed EOS metadata) |
| **Architecture** | Causal decoder-only (Qwen3ForCausalLM), 596M params, 28 layers |
| **Pooling** | Last-token pooling (`--pooling last`) |
| **Output** | 1024-dim dense vectors, L2 normalized |
| **Training ctx** | 32,768 tokens |
| **GGUF size** | ~600 MB (Q8_0) |

**Why iyanello over official Qwen GGUF:** The official `Qwen/Qwen3-Embedding-0.6B-GGUF` lacks `add_eos_token` metadata in the GGUF header. The model was trained expecting `<|endoftext|>` appended to every input. Without it, embeddings can degrade to ~0% retrieval recall. `iyanello`'s repack has this baked in.

**Why Qwen3-Embedding over alternatives:**
- vs bge-m3: 32K context (vs 8K), better for hindsight-style multi-chunk embedding without chunking
- vs pplx-embed: GGUF-native (no TEI dependency), Q8_0 KV cache supports true parallel batching
- Same Qwen3-0.6B backbone as existing reranker — consistent VRAM behavior, shared architecture knowledge

#### Configuration Defaults

| Parameter | Default | Description |
|-----------|---------|-------------|
| `LMBD_ENGINE` | `llama` | Engine selector |
| `LMBD_LLAMA_MODEL` | `.../Qwen3-Embedding-0.6B-Q8_0.gguf` | Path to GGUF model file |
| `LMBD_ALIAS` | `qwen3-embedding` | Client model alias |
| `LMBD_LLAMA_N_CTX` | `49152` | Total context (6 × 8192 for true parallel) |
| `LMBD_LLAMA_N_UBATCH` | `49152` | Micro-batch (must match N_CTX) |
| `LMBD_LLAMA_PARALLEL` | `6` | Parallel slots |
| `LMBD_LLAMA_N_GPU_LAYERS` | `999` | GPU offload (all layers) |
| `LMBD_LLAMA_THREADS` | `4` | CPU threads |
| `LLAMA_SERVER_BIN` | `llama-server` | Path to llama-server binary |

**Server flags at runtime:**
```
--embeddings --pooling last --embd-normalize 2
--cache-type-k q8_0 --cache-type-v q8_0
--ctx-size 49152 --batch-size 49152 --ubatch-size 49152
--parallel 6 --n-gpu-layers 999
```

**How true parallel works:** Without `--kv-unified`, `ctx-size 49152 / parallel 6 = 8192` per slot. Each slot has its own 8192-position KV partition (Q8_0, ~224 MB each). `can_split() = true` (causal decoder + LAST pooling), so `pre_decode()` fills the shared batch from all 6 slots → one `llama_decode(49152)` call. Each token carries its `seq_id` — attention is zero between sequences (6 × O(8K²), not O(48K²)). Per-slot 8K cap enforced by `slot.n_ctx = 8192`.

#### Alternate Sequential Config (for GPUs < 6 GB)

```
--kv-unified --ctx-size 8192 --batch-size 8192 --ubatch-size 8192 --parallel 6
```

All slots share one 8192-position KV pool (~224 MB). One 8K request per forward pass, 6 sequential iterations. Total VRAM: ~1.4 GB.

---

## Service Configuration & Ports

- **Default Port**: `50082` (HTTP)
- **Default Host**: `127.0.0.1`

### Service Endpoints (Port `50082`)

- **`POST /v1/embeddings`**: OpenAI-compatible embeddings endpoint.
- **`POST /tokenize`**: Tokenizes input text into integer token IDs (supports TEI `{"inputs": text}` and llama-server `{"content": text}` formats).
- **`POST /detokenize`**: Detokenizes token IDs back into text.
- **`GET /health`**: Returns JSON status on service health and model loading metrics.

## Configuration Files

- **Service Unit**: `~/.config/systemd/user/local-embedding.service`
- **Environment File**: `~/.config/systemd/user/local-embedding.env`
- **Systemd Sitecustomize Patch**: `~/.config/systemd/user/sitecustomize.py` (installed automatically for TEI engine helper logic)

### Inspecting Configuration (`cmd_cat`)

To inspect the generated systemd unit, loaded environment configuration, and transient execution command in one step:
```bash
./local-embedding.sh cat
```

---

## VRAM Usage & Attention Scaling

### 1. TEI Engine (`LMBD_ENGINE=tei`)
- **No Autoregressive KV Cache**: TEI processes sequences in a single forward pass without allocating generative KV caches.
- **VRAM Breakdown**:
  - Static weight footprint: **~1.2 GB VRAM** (for 0.6B fp16/bf16 model).
  - Attention Activation Memory: Scales quadratically $O(N^2)$ with sequence length. Under Flash Attention on AMD Radeon RX 7900 XTX:
    - 8K sequence: ~256 MB activation VRAM per request.
    - 16K sequence: ~1.0 GB activation VRAM per request.
    - 32K sequence: ~4.0 GB activation VRAM per request.
- **Dynamic Batching**: Capped by `LMBD_TEI_MAX_CONCURRENT=4` and `LMBD_TEI_MAX_BATCH_TOKENS=32768`. A 4×8K or 2×16K parallel batch consumes **~1.0 GB** of activation VRAM (~2.2 GB total VRAM including weights and CUDA overhead).

### 2. Llama-Server Engine (`LMBD_ENGINE=llama`)
- **Non-unified KV Cache (default true parallel)**:
  6 partitions × 8192 pos × Q8_0 × 28 layers × 8 kv_heads × 64 head_dim × 2 (K+V) × 1 byte = **~1.34 GB** KV cache.
  Total VRAM: ~3 GB (600M weights + 1.34G KV + 400M runtime + ~600M activations).
- **Unified KV Cache (alternate sequential)**:
  1 pool × 8192 pos × Q8_0 = **~224 MB** KV cache.
  Total VRAM: ~1.4 GB. See env file for switching.

---

## Verification & Benchmarking

### API Validation Test

```bash
./local-embedding.sh test
```

### Standard Embedding Benchmark

Runs single-request throughput benchmarking using `/data/public/machine-learning/models/benchmark-context.md` (~64K tokens):
```bash
./local-embedding.sh test --benchmark [--repeat 3]
```

### Parallel Hindsight Embedding Benchmark

Runs parallel workload stress-testing using `/data/public/machine-learning/models/hindsight-context.txt` (128K multilingual context file, 50% German, 30% English tutorial, 20% Python AST code).

The hindsight benchmark dispatches **3 sequential rounds of 4 parallel 8K requests** (total 98,304 tokens):
1. **Round 1**: 4 × 8K = 32,768 tokens (4 parallel requests)
2. **Round 2**: 4 × 8K = 32,768 tokens (4 parallel requests)
3. **Round 3**: 4 × 8K = 32,768 tokens (4 parallel requests)

Run with:
```bash
./local-embedding.sh test --benchmark --hindsight [--repeat 3]
```

### Manual Curl Test

```bash
curl -s -X POST http://localhost:50082/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3-embedding",
    "input": "Antigravity local embedding service test"
  }'
```
