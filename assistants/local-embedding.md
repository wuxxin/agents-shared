# Local Text Embedding Service Guide

`local-embedding.sh` manages the local `llama-server` systemd user service (`local-embedding.service`), serving the Text Embedding model (`Qwen3-Embedding-0.6B-Q8_0.gguf`). It operates with pooling mode set to `mean` to generate text embeddings for search, retrieval-augmented generation (RAG), and agentic document indexing.

- **Source Code**: [GitHub - ggml-org/llama.cpp](https://github.com/ggml-org/llama.cpp)
- **AUR Packages**: `llama.cpp-cuda` / `llama.cpp-hip` / `llama.cpp`

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

# Run API validation tests
./local-embedding.sh test

# Run llama-server as a transient systemd user service
./local-embedding.sh exec [--env KEY=VALUE]* [-- llama-server-args...]

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

These overrides are kept transient, keeping the main `.env` configuration file untouched. For example, to run the server temporarily on CPU without changing your permanent configuration:
```bash
./local-embedding.sh exec --env LMBD_N_GPU_LAYERS=0
```


## Default Embedding Model

The local service runs **`Qwen3-Embedding-0.6B`** in `Q8_0` GGUF quantization format. 

Key specifications:
  - **Context Size (`LMBD_N_CTX`):** `8192`
  - **Pooling:** `mean`
  - **Model File:** `/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf`
  - **Capabilities**: Translates text blocks into high-density vector representations for similarity checks and vector search databases.

## Service Configuration & Ports

- **Default Port**: `50082` (HTTP)
- **Default Host**: `127.0.0.1`

### Service Endpoints (Port `50082`)

- **`POST /v1/embeddings`**: OpenAI-compatible embeddings endpoint (returns vector arrays representing input texts).
- **`POST /tokenize`**: Converts input text into model-specific integer token IDs.
- **`POST /detokenize`**: Converts token IDs back into string characters.
- **`GET /health`**: Returns JSON details regarding slots, queue metrics, and service health.


## Configuration Files

The service stores its configuration in the systemd user configuration directory:

- **Service Unit**: `~/.config/systemd/user/local-embedding.service`
- **Environment File**: `~/.config/systemd/user/local-embedding.env`

### Switching between GPU and CPU Inference 

By default, the service offloads embedding layer computation to the GPU to maximize throughput. If GPU memory is constrainted, execution can be offloaded to the CPU.

To run the service on the CPU or GPU, run `./local-embedding.sh edit` (or edit `~/.config/systemd/user/local-embedding.env` directly) and change the parameter `LMBD_N_GPU_LAYERS`:

```bash
# For GPU execution (fully offload all layers)
LMBD_N_GPU_LAYERS=999

# For CPU execution
LMBD_N_GPU_LAYERS=0
```

### Backend Device Selection (Dynamic Backend Loading)

When using a combined backend build (such as `libggml-git-hip`), the service supports dynamic loading of different acceleration backends (CPU, OpenBLAS, Vulkan, and HIP/ROCm) at runtime. 

You can configure the target device using the `LMBD_DEVICE` environment variable. Run `./local-embedding.sh edit` (or edit `~/.config/systemd/user/local-embedding.env` directly) and configure the device:

```bash
# GPU/CPU backend device to use (run 'llama-cli --list-devices' for valid names)
# By default, llama-server automatically selects the best available device.
# To force a specific backend device, uncomment one of the options below:
# LMBD_DEVICE="ROCm0"
# LMBD_DEVICE="Vulkan0"
# LMBD_DEVICE="BLAS"  # Force CPU OpenBLAS acceleration
# LMBD_DEVICE="none"  # Force plain CPU execution (without OpenBLAS)
```

To list all available devices on your system, run:
```bash
llama-cli --list-devices
```

## VRAM Usage

For detailed breakdowns of memory usage and concurrent execution scenarios (co-running Inference, Speech-to-Text, and Text-to-Speech), refer to the [Central Memory Map](assistants/local-memory-map.md).

## Verification & Manual Testing

You can test that the service is running and behaving correctly by running the validation command:

```bash
./local-embedding.sh test
```

### Benchmarking Mode

To run a high-volume embedding throughput and latency benchmark using the context document `/data/public/machine-learning/models/benchmark-context.md`, run:

```bash
# Run embedding benchmark (defaults to 1 run)
./local-embedding.sh test --benchmark

# Run embedding benchmark for multiple repeats to compute cumulative averages (e.g. 3 runs)
./local-embedding.sh test --benchmark --repeat 3
```

Alternatively, you can test it manually using `curl`:

### Text Embeddings Test
```bash
curl -s -X POST http://localhost:50082/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3-embedding",
    "input": "Hello World"
  }'
```
