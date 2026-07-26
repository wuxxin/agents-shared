# Local Document Reranking Service Guide

> Requires **tei-rocm >= pkgrel=6** (ModernBertModel detection patch). Model downloaded via [local-download.sh](local-download.sh).

`local-rerank.sh` manages the local `text-embeddings-router` (TEI) systemd user service (`local-rerank.service`), serving the Text Reranker model (`ettin-reranker-400m-v1`). It uses TEI's Candle backend with ModernBertModel detection to compute relevance scores for query-document pairs via cross-encoder classification.

- **Source Code**: [GitHub - huggingface/text-embeddings-inference](https://github.com/huggingface/text-embeddings-inference)
- **AUR Packages**: `tei-rocm`

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

The local service runs **`cross-encoder/ettin-reranker-400m-v1`** in float16 Safetensors format via TEI's Candle backend.

Key specifications:
  - **Architecture**: ModernBERT (ModernBertForSequenceClassification, ~401M params)
  - **Context Size**: 8,192 tokens
  - **MTEB NDCG@10**: 0.6091 (English retrieval)
  - **License**: Apache 2.0
  - **TEI Backend**: Candle (Rust native) — requires `tei-rocm >= pkgrel=6` for ModernBertModel detection
  - **VRAM**: ~1.6 GB (bf16 weights ~0.8 GB + CUDA overhead ~0.4 GB + activations ~0.4 GB)
  - **Download**: `bash scripts/local-download.sh /data/public/machine-learning/models --reranker`
  - **Capabilities**: Cross-encoder relevance scoring for hybrid retrieval and memory systems.

## Service Configuration & Ports

- **Default Port**: `50086` (HTTP)
- **Default Host**: `127.0.0.1`

### Service Endpoints (Port `50086`)

Cohere-compatible /rerank endpoint (Azure AI Foundry, Jina, Voyage, etc.)

- **`POST /v1/rerank`**: Cohere-compatible reranking endpoint (returns relevance scores for query-document pairs).
- **`POST /tokenize`**: Converts input text into model-specific integer token IDs.
- **`POST /detokenize`**: Converts token IDs back into string characters.
- **`GET /health`**: Returns JSON details regarding slots, queue metrics, and service health.


## Configuration Files

The service stores its configuration in the systemd user configuration directory:

- **Service Unit**: `~/.config/systemd/user/local-rerank.service`
- **Environment File**: `~/.config/systemd/user/local-rerank.env`

### TEI Device Selection

TEI auto-detects the best available backend (ROCm, Vulkan, or CPU). To force a specific device, set `LRR_TEI_DEVICE`:

```bash
# Auto-detect (default, recommended for dGPU):
# LRR_TEI_DEVICE=""
# Force dGPU Vulkan backend:
# LRR_TEI_DEVICE="Vulkan1"
# Force CPU execution:
# LRR_TEI_DEVICE="cpu"
```

Device mapping is handled via `HIP_VISIBLE_DEVICES` / `CUDA_VISIBLE_DEVICES` internally.


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

### Document Reranking Test
```bash
curl -s -X POST http://localhost:50086/v1/rerank \
  -H "Content-Type: application/json" \
  -d '{
    "model": "ettin-reranker",
    "query": "What is the speed of light in a vacuum?",
    "documents": [
      "The speed of sound in dry air at 20 degrees Celsius is approximately 343 meters per second.",
      "The speed of light in a vacuum is a fundamental physical constant exactly equal to 299,792,458 meters per second.",
      "Light travels through glass at a speed of approximately 200,000 kilometers per second, which is slower than in a vacuum.",
      "The speed of light in water is about 225,000 kilometers per second due to the refractive index.",
      "The Earth orbits the Sun at an average speed of about 29.78 kilometers per second."
    ],
    "top_n": 3
  }'
```
