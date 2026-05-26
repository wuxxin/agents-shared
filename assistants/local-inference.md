# Local Inference Management Guide

`local-inference.sh` manages a persistent `llama-server` instance in **router mode**, serving an LLM, an embedding model, and an optional reranker from a single process on one port. Optimized for AMD ROCm hardware (specifically tested on Radeon Pro W6800).

- **Source Code**: [GitHub - ggml-org/llama.cpp](https://github.com/ggml-org/llama.cpp)
- **Arch/AUR Package**:
  - `llama.cpp` (Official extra repository, CPU-only/OpenBLAS fallback)
  - `llama.cpp-cuda` (AUR, with CUDA acceleration for NVIDIA GPUs)
  - `llama.cpp-hip` (AUR, with HIP/ROCm acceleration for AMD GPUs)
  - `llama.cpp-git` (AUR, latest git source build, CPU)
  - `llama.cpp-git-cuda` (AUR, latest git source build with CUDA)
  - `llama.cpp-git-hip` (AUR, latest git source build with HIP/ROCm)
  - `llama.cpp-git-ggml-hip` (private package `libggml-git-hip` in repo https://github.com/wuxxin/aur-packages )

## Usage

| Command | Description |
|---|---|
| `install [--no-start]` | Sets up the service, generates default configuration and models INI (does not start if --no-start is specified). |
| `uninstall` | Stops and removes the service. |
| `edit` | Edit model selection and server parameters. |
| `logs [args...]` | View the inference server output. Pass `-f` to tail/follow. Supports any `journalctl` options. |
| `exec` | Run `llama-server` in a transient unit with the same GPU access. |
| `shell` | Spawn an interactive shell in the inference sandbox (useful for `rocm-smi`). |

## Router Mode Architecture

The service uses `llama-server --models-preset` to serve multiple models from a single process. All models are kept warm simultaneously in VRAM (`--models-max 2` or `3`), eliminating swap delays.

### Endpoints (all on port 50080)

| Endpoint | Model Name | Purpose |
|---|---|---|
| `/v1/chat/completions` | `qwen3` | LLM chat completions |
| `/v1/embeddings` | `qwen3-embedding` | Text embedding generation |
| `/v1/rerank` | `qwen3-reranker` | Document reranking (if enabled) |

### Configuration Files

| File | Purpose |
|---|---|
| `~/.config/systemd/user/local-inference.env` | Model paths, aliases, toggle reranker |
| `~/.config/systemd/user/local-inference.ini` | Auto-generated models preset (do not edit manually) |
| `~/.config/systemd/user/local-inference.service` | Auto-generated systemd unit |

## VRAM Budget Summary

Hardware: AMD Radeon Pro W6800 — **30,704 MiB** usable VRAM.

For this service running in **router mode** with the default config (MoE + Vision + Embedding + Reranker), the weights and compute require **~20,409 MiB**. With a 240,000 token context KV cache (**~8,031 MiB**), the total VRAM footprint is **~28,440 MiB**, leaving **~2,264 MiB** of free headroom.

For a detailed breakdown of all VRAM allocations, options, and scenarios (including concurrent running of all three local services), refer to [Central VRAM Memory Map](file:///home/wuxxin/agent-shared/code/agents-shared/assistants/local-memory-map.md).

## Implementation & Security Considerations

### Centralized Sandboxing Configuration
All systemd security and namespace options are centralized in the `get_shared_options` function within the control script. This ensures that the persistent background service (`local-inference.service`) and any transient runs (`exec` / `shell` commands) run with identical sandbox profiles, preventing configuration drift.

### ROCm / GPU Access
Because `llama-server` requires direct access to GPU device nodes:
- `PrivateDevices=no` is set in the systemd unit.
- Access to `/dev/dri` and `/dev/kfd` is mandatory.
- The user must be in the `render` and `video` groups.

### Filesystem and Data Access
- **Models**: Read-write access to `/data/public/machine-learning` is configured.
- **Sandboxing**: Uses `ProtectSystem=strict`.
- **Isolation**: The user's home directory (`%h` / `$HOME`) is bind-mounted to allow the server to read its configurations, while system paths are protected.

### Configuration & Ports
- **Default Port**: `50080` (llama-server OpenAI-compatible API — LLM, embeddings, reranking)
- **Configuration File**: Environment parameters and model settings are configured in `~/.config/systemd/user/local-inference.env`.

### Models Preset (INI)
The `local-inference.ini` file is **auto-generated** from the env file on every `install`, `start`, and `restart`. Do not edit it manually. It defines:
- The LLM model section with KV cache, batch, and context parameters
- The embedding model section with `embedding = true` and `pooling = mean`
- The optional reranker section with `embedding = true` and `pooling = rank`

### Reranker Toggle
Set `LI_RERANKER_ENABLED=true` in the env file to enable the `/v1/rerank` endpoint. When disabled, `--models-max` is reduced from 3 to 2, and the reranker model is not loaded.

## Verification & Test Results

The local-inference service (serving LLM, Embeddings, and Reranking) was validated using the following test setup:

### 1. Chat Completion (LLM)
- **Model**: `qwen3`
- **Endpoint**: `http://localhost:50080/v1/chat/completions`
- **Command**:
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
- **Response**:
  ```json
  {
    "choices": [
      {
        "finish_reason": "stop",
        "index": 0,
        "message": {
          "role": "assistant",
          "content": "Hello World!",
          "reasoning_content": "..."
        }
      }
    ],
    "created": 1779406181,
    "model": "qwen3",
    "object": "chat.completion"
  }
  ```
- **Result**: Success.

### 2. Text Embedding
- **Model**: `qwen3-embedding`
- **Endpoint**: `http://localhost:50080/v1/embeddings`
- **Command**:
  ```bash
  curl -s -X POST http://localhost:50080/v1/embeddings \
    -H "Content-Type: application/json" \
    -d '{
      "model": "qwen3-embedding",
      "input": "Hello World"
    }'
  ```
- **Response**:
  Successfully generated a list of float values representing the embedding vector.
- **Result**: Success.

### 3. Reranking Validation (3 Documents)
- **Model**: `qwen3-reranker`
- **Endpoint**: `http://localhost:50080/v1/rerank`
- **Command**:
  ```bash
  curl -s -X POST http://localhost:50080/v1/rerank \
    -H "Content-Type: application/json" \
    -d '{
      "model": "qwen3-reranker",
      "query": "What is the capital of France?",
      "documents": [
        "Paris is the capital of France.",
        "Berlin is the capital of Germany.",
        "London is the capital of the United Kingdom."
      ],
      "top_n": 3
    }'
  ```
- **Response**:
  ```json
  {
    "model": "qwen3-reranker",
    "object": "list",
    "usage": {
      "prompt_tokens": 257,
      "total_tokens": 257
    },
    "results": [
      {"index": 0, "relevance_score": 0.9941950440406799},
      {"index": 2, "relevance_score": 0.02772255428135395},
      {"index": 1, "relevance_score": 0.0008937619277276099}
    ]
  }
  ```
- **Result**: Success.
  > [!NOTE]
  > The original community-quantized model GGUF file (`Qwen3-Reranker-0.6B.Q4_K_M.gguf`) was missing the classification weights head (`cls.output.weight`). We successfully re-converted the model from the official Hugging Face source weights (`Qwen/Qwen3-Reranker-0.6B`) using the official `convert_hf_to_gguf.py` script and quantized it to `Q4_K_M`, which resolved the issue and restored correct semantic ranking.

### 4. Reranking Multi-Example Validation (7 Documents)
- **Query**: "How do I optimize systemd service sandboxing for security?"
- **Command**:
  ```bash
  curl -s -X POST http://localhost:50080/v1/rerank \
    -H "Content-Type: application/json" \
    -d '{
      "model": "qwen3-reranker",
      "query": "How do I optimize systemd service sandboxing for security?",
      "documents": [
        "To restrict a systemd service, configure sandbox options like ProtectSystem=strict, ProtectHome=yes, PrivateTmp=yes, and CapabilityBoundingSet= to limit kernel capabilities.",
        "Bubblewrap is a low-level unprivileged sandboxing tool used to create isolated environments by mounting namespaces manually.",
        "Systemd is an init system and system manager for Linux operating systems that boot the system and manage user services.",
        "Baking a chocolate cake requires flour, sugar, cocoa powder, eggs, and baking in a warm oven to 350 degrees Fahrenheit.",
        "For local AI inference, AMD ROCm requires installing the correct GPU drivers and mapping /dev/kfd and /dev/dri into the runtime sandbox.",
        "Docker containers provide application-level virtualization and process isolation using Linux cgroups and namespaces.",
        "A systemd service can be configured to run as a dynamic user by setting DynamicUser=yes, which automatically allocates transient UIDs and GIDs."
      ],
      "top_n": 7
    }' | jq .
  ```
- **Response**:
  ```json
  {
    "model": "qwen3-reranker",
    "object": "list",
    "usage": {
      "prompt_tokens": 755,
      "total_tokens": 755
    },
    "results": [
      {
        "index": 0,
        "relevance_score": 0.9999607801437378
      },
      {
        "index": 6,
        "relevance_score": 0.9976387023925781
      },
      {
        "index": 5,
        "relevance_score": 0.23269306123256683
      },
      {
        "index": 1,
        "relevance_score": 0.188172847032547
      },
      {
        "index": 2,
        "relevance_score": 0.10291396081447601
      },
      {
        "index": 4,
        "relevance_score": 0.004374932497739792
      },
      {
        "index": 3,
        "relevance_score": 0.00007212698255898431
      }
    ]
  }
  ```
- **Result**: Success. The scores are highly accurate: systemd security options (index 0) and dynamic user allocation (index 6) receive scores $> 0.99$, while general systemd definitions or alternative sandboxes (Docker, Bubblewrap) score low ($0.10 - 0.23$), and irrelevant items (ROCm inference, baking a cake) score near zero ($< 0.005$).

