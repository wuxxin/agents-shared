# Local Document Reranking Service Guide

`local-rerank.sh` manages the local `llama-server` systemd user service (`local-rerank.service`), serving the Text Reranker model (`Qwen3-Reranker-0.6B.Q4_K_M.gguf`). It operates with pooling mode set to `rank` to compute relevance scores for query-document pairs.

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

The local service runs **`Qwen3-Reranker-0.6B`** in `Q4_K_M` GGUF quantization format. 

Key specifications:
  - **Context Size (`LRR_N_CTX`):** `16384` (µ-Batch Size `LRR_N_UBATCH`: `16384`)
  - **Pooling:** `rank`
  - **Capabilities**: Primarily used to rank relevance scores of search results for hybrid retrieval and memory systems.

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

### Switching between GPU and CPU Inference 

By default, the service runs the reranker on the CPU, which is highly recommended to conserve VRAM.
or if VRAM is available, it can offload execution to the GPU using ROCm/HIP acceleration.

To run the service on the CPU or GPU, run `./local-rerank.sh edit` (or edit `~/.config/systemd/user/local-rerank.env` directly) and change the parameter LRR_N_GPU_LAYERS:

```bash
# For CPU execution
LRR_N_GPU_LAYERS=0
# For GPU execution
LRR_N_GPU_LAYERS=99
```

### Backend Device Selection (Dynamic Backend Loading)

When using a combined backend build (such as `libggml-git-hip`), the service supports dynamic loading of different acceleration backends (CPU, OpenBLAS, Vulkan, and HIP/ROCm) at runtime. 

You can configure the target device using the `LRR_DEVICE` environment variable. Run `./local-rerank.sh edit` (or edit `~/.config/systemd/user/local-rerank.env` directly) and configure the device:

```bash
# GPU/CPU backend device to use (run 'llama-cli --list-devices' for valid names)
# By default, llama-server automatically selects the best available device.
# To force a specific backend device, uncomment one of the options below:
# LRR_DEVICE="ROCm0"
# LRR_DEVICE="Vulkan0"
# LRR_DEVICE="BLAS"  # Force CPU OpenBLAS acceleration
# LRR_DEVICE="none"  # Force plain CPU execution (without OpenBLAS)
```

To list all available devices on your system, run:
```bash
llama-cli --list-devices
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
