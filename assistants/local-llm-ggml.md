# Local LLM and Embedding Service Guide

`local-llm-ggml.sh` manages the local `llama-server` systemd user service (`local-llm-ggml.service`), serving both the Chat/Vision LLM and the Text Embedding model simultaneously from a single process using router mode (`--models-preset`).

This architecture reduces process management overhead, saves VRAM by avoiding duplicate HIP/ROCm contexts (~600 MiB saving), and consolidates chat and embedding API calls onto a single port.

- **Source Code**: [GitHub - ggml-org/llama.cpp](https://github.com/ggml-org/llama.cpp)
- **AUR Packages**: `llama.cpp-cuda` / `llama.cpp-hip` / `llama.cpp`

## Usage

```bash
# Install the service and environment configuration
./local-llm-ggml.sh install [--no-start] [--new-config]

# Start/Stop/Restart the service
./local-llm-ggml.sh start
./local-llm-ggml.sh stop
./local-llm-ggml.sh restart
./local-llm-ggml.sh enable
./local-llm-ggml.sh disable

# Check runtime status
./local-llm-ggml.sh status

# Tail service stdout/stderr logs
./local-llm-ggml.sh logs -f

# Edit service environment configuration and auto-restart
./local-llm-ggml.sh edit

# Run API validation tests
./local-llm-ggml.sh test
```

## Service Configuration & Ports

- **Default Port**: `50080` (HTTP)
- **Default Host**: `127.0.0.1`

### Service Endpoints (Port `50080`)

- **`POST /v1/chat/completions`**: OpenAI-compatible chat completion endpoint (routed to the chat LLM).
- **`POST /v1/embeddings`**: OpenAI-compatible text embedding endpoint (routed to the embedding model).
- **`POST /v1/completions`**: OpenAI-compatible text completion endpoint.
- **`POST /completion`**: Native `llama.cpp` endpoint for custom prompt completion.
- **`POST /embedding`**: Native `llama.cpp` endpoint to generate vector embeddings.
- **`POST /tokenize`**: Converts input text into model-specific integer token IDs.
- **`POST /detokenize`**: Converts token IDs back into string characters.
- **`GET /v1/models`**: Lists all active model aliases.
- **`GET /health`**: Returns JSON details regarding slots, queue metrics, and service health.

---

## Configuration Files

The service stores its configuration in the systemd user configuration directory:

- **Service Unit**: `~/.config/systemd/user/local-llm-ggml.service`
- **Environment File**: `~/.config/systemd/user/local-llm-ggml.env`
- **Router Configuration File**: `~/.config/systemd/user/local-llm-ggml.ini`

### GPU and CPU Inference

By default, the service offloads execution to the GPU using ROCm/HIP.
To run the service on the CPU, run `./local-llm-ggml.sh edit` (or edit `~/.config/systemd/user/local-llm-ggml.env` directly) and uncomment the CPU parameters:

```bash
# For CPU execution, uncomment these variables:
# LLM_N_GPU_LAYERS=0
# LLM_EXTRA_ARGS=""
```

---

## Verification & Manual Testing

You can test that the service is running and behaving correctly by running the validation command:

```bash
./local-llm-ggml.sh test
```

### Benchmarking Mode

To benchmark prefill and decoding latency and throughput using `benchmark-context.md`, run:

```bash
# Run both Chat/Summarization and Embeddings benchmarks
./local-llm-ggml.sh test --benchmark

# Run ONLY the Embeddings benchmark (mutually exclusive with --full)
./local-llm-ggml.sh test --benchmark --only-embeddings

# Run benchmarks along with the cache-hit latency evaluation script (llama-cache-test.py)
./local-llm-ggml.sh test --benchmark --full
```

Alternatively, you can test it manually using `curl`:

### 1. Chat Completion Test
```bash
curl -s -X POST http://localhost:50080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3",
    "messages": [
      {"role": "user", "content": "Hello, respond with exactly: Hello World!"}
    ]
  }'
```

### 2. Text Embedding Test
```bash
curl -s -X POST http://localhost:50080/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3-embedding",
    "input": "Hello World"
  }'
```

## Model Specifications & Capabilities

The local service runs **`Qwen3.6-35B-A3B-APEX-I-Compact`** as its primary chat and vision model. Below are the key specifications and limits:

- **Context Window**: The Qwen3.6 architecture natively supports a context window of up to **1,000,000 (1M) tokens**. In this local deployment, the service allocates a physical context size of **240,000 tokens**, which is divided across **3 parallel slots (80,000 tokens context window size per slot)**.
- **Max Output (Generation) Limit**: The Qwen3.6 architecture supports a maximum output generation length of **65,536 (64K) tokens** in a single completion request.
- **Capabilities**: Full text completion, native tool-calling, multi-modal vision inputs (using the mmproj GGUF file), and high-performance ROCm/HIP-accelerated execution on AMD GPUs.

