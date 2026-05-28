# Local Document Reranking Service Guide

`local-rerank.sh` manages the local `llama-server` systemd user service (`local-rerank.service`), serving the Text Reranker model (`Qwen3-Reranker-0.6B.Q4_K_M.gguf`). It operates with pooling mode set to `rank` to compute relevance scores for query-document pairs.

This architecture enables high-performance local document reranking, which is crucial for search, retrieval-augmented generation (RAG), and agentic memory systems.

- **Source Code**: [GitHub - ggml-org/llama.cpp](https://github.com/ggml-org/llama.cpp)
- **AUR Packages**: `llama.cpp-cuda` / `llama.cpp-hip` / `llama.cpp`

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
```

## Service Configuration & Ports

- **Default Port**: `50086` (HTTP)
- **Default Host**: `127.0.0.1`

### Service Endpoints (Port `50086`)

- **`POST /v1/rerank`**: OpenAI/Cohere-compatible reranking endpoint (returns relevance scores for query-document pairs).
- **`POST /tokenize`**: Converts input text into model-specific integer token IDs.
- **`POST /detokenize`**: Converts token IDs back into string characters.
- **`GET /health`**: Returns JSON details regarding slots, queue metrics, and service health.

---

## Configuration Files

The service stores its configuration in the systemd user configuration directory:

- **Service Unit**: `~/.config/systemd/user/local-rerank.service`
- **Environment File**: `~/.config/systemd/user/local-rerank.env`

### GPU and CPU Inference

By default, the service offloads execution to the GPU using ROCm/HIP (specifically targeting AMD Radeon Pro W6800).
However, to conserve VRAM, running the reranker on the CPU is highly recommended. It runs entirely in System RAM, requiring approximately **450 MiB** of memory and using **0 MiB** of GPU VRAM.

To run the service on the CPU, run `./local-rerank.sh edit` (or edit `~/.config/systemd/user/local-rerank.env` directly) and uncomment the CPU parameters:

```bash
# For CPU execution, uncomment these variables:
# LR_N_GPU_LAYERS=0
# LR_EXTRA_ARGS=""
```

---

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
    "model": "qwen3-reranker",
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

## Model Specifications & Capabilities

The local service runs **`Qwen3-Reranker-0.6B`** in `Q4_K_M` GGUF quantization format. Below are the key specifications and limits:

- **Context Window**: The model supports a context window of up to **8,192 tokens**.
- **Capabilities**: Custom tokenization/detokenization, high-performance ROCm/HIP-accelerated execution on AMD GPUs, or low-overhead CPU execution. Primarily used to rank relevance scores of search results for hybrid retrieval and memory systems (e.g. LibreFang, Moltis, ZeroClaw).
