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

### Architecture (Qwen3-Embedding-0.6B)

| Attribute                  | Value |
|----------------------------|-------|
| **Parameters**             | 0.6B |
| **Transformer Layers**     | 28 |
| **Hidden Size**            | 1024 |
| **Attention Heads**        | 16 (GQA KV-heads: 8) |
| **Head Dimension**         | 64 |
| **Native Max Context**     | 32,768 tokens |
| **Embedding Dimension**    | 1024 (MRL: 32–1024 user-selectable) |
| **Pooling (native)**       | Last-token pooling |
| **Pooling (service)**      | `mean` (configured via `--pooling mean`) |
| **Multilingual**           | 100+ languages, 100+ programming languages |
| **Base Model**             | `Qwen/Qwen3-0.6B-Base` |
| **License**                | Apache-2.0 |
| **Paper**                  | [arXiv:2506.05176](https://arxiv.org/abs/2506.05176) |

> **MRL** (Matryoshka Representation Learning) allows truncating the output embedding to any dimension from 32 to 1024, enabling smaller index sizes at a small accuracy cost. The full 1024-dimensional output is used by default.

### GGUF File (Q8_0)

- **File:** `/data/public/machine-learning/models/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf`
- **File Size:** ~568 MiB on disk
- **Quantization:** Q8_0 — 8-bit integer weights, minimal quality loss vs. F16

### Service Configuration Defaults

| Parameter | Default | Notes |
|-----------|---------|-------|
| `LMBD_N_CTX` | `8192` | Max context length per parallel slot |
| Batch Size | `8192` | Same as LMBD_N_CTX |
| µ-Batch Size | `512` | max hardware batch size |
| `LMBD_PARALLEL` | `2` | Concurrent embedding slots |
| Pooling | `mean` | Pooling mode passed to `--pooling` |

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

### KV Cache Formula

For `llama-server`, the KV cache is allocated upfront using:

$$\text{KV cache} = n\_\text{parallel} \times n\_\text{ctx} \times 2 \times n\_\text{kv\_heads} \times d\_\text{head} \times n\_\text{layers} \times \text{bytes\_per\_element}$$

For Qwen3-Embedding-0.6B (GQA with 8 KV-heads, head-dim 64, 28 layers) at the default `n_ctx=8192`:

| Parallel Slots | KV Cache (f16, default) | KV Cache (q8_0) | KV Cache (q4_0) |
|:--------------:|:-----------------------:|:---------------:|:---------------:|
| 1              | ~224 MiB               | ~112 MiB        | ~56 MiB         |
| 2 (default)    | ~448 MiB               | ~224 MiB        | ~112 MiB        |
| 4              | ~896 MiB               | ~448 MiB        | ~224 MiB        |

> **Formula applied:** `1 × 8192 × 2 × 8 × 64 × 28 × 2 bytes (f16) = 224 MiB` per slot.

### KV Cache Quantization (`--cache-type-k/v`)

`llama-server` supports quantizing the KV cache independently from the model weights to reduce VRAM usage:

```bash
# In local-embedding.env (or via exec --env):
LMBD_EXTRA_ARGS="--cache-type-k q8_0 --cache-type-v q8_0"
```

**Available types** (for both `-ctk`/`--cache-type-k` and `-ctv`/`--cache-type-v`):

| Type   | Bits | Default | Memory vs. f16 | Notes |
|--------|------|---------|---------------|-------|
| `f32`  | 32   |         | 2× larger     | Full precision |
| `f16`  | 16   | ✅ Yes  | 1×            | Default |
| `bf16` | 16   |         | 1×            | Brain float |
| `q8_0` | 8    |         | ~0.5×         | **Recommended** — negligible quality loss |
| `q4_0` | 4    |         | ~0.25×        | Aggressive — may affect long-context quality |
| `q4_1` | 4    |         | ~0.25×        | Slight quality improvement over q4_0 |
| `q5_0` | 5    |         | ~0.31×        | |
| `q5_1` | 5    |         | ~0.31×        | |
| `iq4_nl` | ~4 |         | ~0.25×        | i-quantization variant |

> **Note:** KV cache quantization is most effective with `--flash-attn` enabled. For embedding workloads (no generation), `q8_0` KV cache is very safe as there is no token-by-token autoregressive accumulation of rounding errors.

### Benchmarked Footprints

The following were measured with the **previous default** of `LMBD_PARALLEL=4` and `n_ctx=8192` (note: current default is `LMBD_PARALLEL=1`):

| Backend | Active Memory | Notes |
|---------|--------------|-------|
| HIP-ROCm0 (dGPU) | **7,119.7 MiB** VRAM | throughput: 1,799.58 t/s |
| Vulkan-Vulkan0 (iGPU) | **5,229.6 MiB** VRAM | batch=2048, throughput: 493.77 t/s |
| Vulkan-Vulkan1 (dGPU) | *Failed* | warmup/initialization hang |
| CPU | ~0.1 MiB VRAM + **11,898.1 MiB** System RAM | throughput: 99.29 t/s |

> The high observed memory (vs. the ~224 MiB KV cache estimate per slot) comes primarily from compute graph pre-allocation and intermediate activation buffers which scale with `n_ubatch` (physical batch size). With `n_ubatch=2048`, the attention score matrix alone reaches `n_ubatch × n_heads × n_ubatch × 2 bytes` ≈ **256 MiB per layer**, totalling several GiB across 28 layers during active inference.

For detailed co-running breakdowns and allocation tables, refer to the [Central Memory Map](assistants/local-memory-map.md).

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
