# Local Document Reranking Service Guide

> Requires **libggml-git-hip >= 10148** (with `jina-reranker-v3.patch` for projector support). Model downloaded via [local-download.sh](local-download.sh).

`local-rerank.sh` manages the local `llama-server` systemd user service (`local-rerank.service`), serving the Text Reranker model (`jina-reranker-v3`). It uses LAST-token pooling with a 2-layer MLP projector (ReLU activated) to produce 512-dim embeddings. Clients POST to `/v1/embeddings` and compute cosine similarity client-side for reranking.

- **Source Code**: [GitHub - ggml-org/llama.cpp](https://github.com/ggml-org/llama.cpp)
- **AUR Package**: `libggml-git-hip` → `llama.cpp-git-ggml-hip`
- **Architecture patch**: `jina-reranker-v3.patch` adds `JinaForRankingModel` converter, `DENSE_2_OUT`/`DENSE_3_OUT` tensor mappings, and ReLU activation support

## Usage

```bash
# Install the service and environment configuration
./local-rerank.sh install [--no-start] [--new-config]

# Start/Stop/Restart the service
./local-rerank.sh start
./local-rerank.sh stop
./local-rerank.sh restart

# Check runtime status
./local-rerank.sh status

# Tail service stdout/stderr logs
./local-rerank.sh logs -f

# Edit service environment configuration and auto-restart
./local-rerank.sh edit

# Run API validation tests
./local-rerank.sh test

# Run llama-server as a transient systemd user service
./local-rerank.sh exec [--env KEY=VALUE]* [-- llama-server-args...]

# Run a custom command inside the sandboxed environment
./local-rerank.sh run [--env KEY=VALUE]* <command> [args...]

# Spawn an interactive shell inside the sandboxed environment
./local-rerank.sh shell [--env KEY=VALUE]*
```

### In-Memory Environment Overrides

The `exec`, `run`, and `shell` subcommands support a repeatable `--env KEY=VALUE` parameter. When passed, these parameters:
1. Override the values loaded from the `.env` configuration file on disk.
2. Are exported in the local shell environment in-memory for foreground execution.
3. Are dynamically passed to `systemd-run` via `--setenv=KEY=VALUE` for transient background runs in systemd.

These overrides are kept transient, keeping the main `.env` configuration file untouched. For example, to run the server temporarily on CPU without changing your permanent configuration:
```bash
./local-rerank.sh exec --env LRR_N_GPU_LAYERS=0
```


## Default Reranking Model

The local service runs **`jinaai/jina-reranker-v3`** in Q4_K_M GGUF format via llama-server.

Key specifications:
  - **Architecture**: Qwen3-0.6B decoder + 2-layer MLP projector (1024→512→512, ReLU activation)
  - **Context Size**: 131,072 tokens (served at 16,384 for VRAM efficiency)
  - **MTEB(eng, v2) Retrieval NDCG@10**: ~0.5940
  - **License**: CC-BY-NC 4.0 (private use only)
  - **Backend**: llama-server with `--embeddings --pooling last`
  - **Output**: 512-dim projected embeddings → client-side cosine similarity for reranking
  - **VRAM**: ~1,039 MB (Q4_K_M weights ~397 MB + CUDA overhead ~400 MB + activations ~242 MB)
  - **Download**: `bash scripts/local-download.sh /data/public/machine-learning/models --reranker`
  - **Capabilities**: Multi-document listwise ranking, LBNL causal self-attention interaction over query and documents.

### Serving Architecture

jina-reranker-v3 uses an embedding-based reranking approach:
1. llama-server loads the GGUF model with `--embeddings --pooling last`
2. Clients POST query + document pairs to `/v1/embeddings`
3. The model processes through Qwen3 backbone → LAST-token pooling → MLP projector
4. Returns 512-dim projected embeddings
5. Client computes cosine similarity between query and document embeddings for ranking

### Alternative: TEI / ettin-reranker-400m-v1

Set `LRR_ENGINE=tei` in `~/.config/systemd/user/local-rerank.env` to switch back to the TEI engine with `ettin-reranker-400m-v1` (ModernBERT backbone, ~401M params, Apache 2.0 license) via TEI's Candle backend. TEI uses dynamic batching with static VRAM allocation and provides a native `/v1/rerank` endpoint with Cohere-compatible relevance scores — no client-side cosine similarity needed.

Key specifications:
  - **Architecture**: ModernBERT (ModernBertForSequenceClassification, ~401M params)
  - **Context Size**: 8,192 tokens
  - **MTEB NDCG@10**: 0.6091 (English retrieval)
  - **License**: Apache 2.0
  - **TEI Backend**: Candle (Rust native) — requires `tei-rocm >= pkgrel=6` for ModernBertModel detection
  - **VRAM**: ~1.6 GB (bf16 weights ~0.8 GB + CUDA overhead ~0.4 GB + activations ~0.4 GB)
  - **Download**: `bash scripts/local-download.sh /data/public/machine-learning/models --reranker`
  - **Endpoint**: `POST /v1/rerank` — returns relevance scores directly

## Service Configuration & Ports

- **Default Port**: `50086` (HTTP)
- **Default Host**: `127.0.0.1`

### Service Endpoints (Port `50086`)

OpenAI-compatible /v1/embeddings endpoint for embedding-based reranking.

- **`POST /v1/embeddings`**: Get 512-dim projected embeddings for query/document texts. Compute cosine similarity client-side for reranking.
- **`POST /tokenize`**: Converts input text into model-specific integer token IDs.
- **`POST /detokenize`**: Converts token IDs back into string characters.
- **`GET /health`**: Returns JSON details regarding slots, queue metrics, and service health.


## Configuration Files

The service stores its configuration in the systemd user configuration directory:

- **Service Unit**: `~/.config/systemd/user/local-rerank.service`
- **Environment File**: `~/.config/systemd/user/local-rerank.env`

### llama-server Device Selection

llama-server auto-detects the best available backend (ROCm, Vulkan, or CPU). To force a specific device, set `LRR_DEVICE`:

```bash
# Auto-detect (default, recommended for dGPU):
# LRR_DEVICE=""
# Force dGPU Vulkan backend:
# LRR_DEVICE="Vulkan1"
# Force CPU execution:
# LRR_DEVICE="cpu"
```


## VRAM Usage

For detailed breakdowns of memory usage and concurrent execution scenarios (co-running Inference, Speech-to-Text, and Text-to-Speech), refer to [Central Memory Map](assistants/local-memory-map.md).

## Verification & Manual Testing

You can test that the service is running and behaving correctly by running the validation command:

```bash
./local-rerank.sh test
```

### Benchmarking Mode

To run a document reranking speed benchmark using 10 safe-length document chunks (staying within the 512 physical batch size limit), run:

```bash
# Run reranking benchmark (defaults to 1 run)
./local-rerank.sh test --benchmark

# Run reranking benchmark for multiple repeats to compute cumulative averages (e.g. 5 runs)
./local-rerank.sh test --benchmark --repeat 5
```

Alternatively, you can test it manually using `curl`:

### Document Reranking Test (Embedding-based Cosine Similarity)
```bash
# Embed query
curl -s -X POST http://localhost:50086/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{"model": "jina-reranker-v3", "input": "What is the speed of light in a vacuum?"}'

# Embed document
curl -s -X POST http://localhost:50086/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{"model": "jina-reranker-v3", "input": "The speed of light in a vacuum is a fundamental physical constant exactly equal to 299,792,458 meters per second."}'

# Compute cosine similarity between the two embeddings client-side
```
