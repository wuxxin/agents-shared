# Local Chat Service Guide

`local-chat.sh` manages the local `llama-server` systemd user service (`local-chat.service`), serving the Chat/Vision LLM and optionally the text embedding model in a combined multi-model setup.

Note: Text embeddings can be served combined directly within this service instance on port 50080 (enabled by default), or separately via the standalone [local-embedding.md](local-embedding.md) service.

When combined embedding mode is enabled, a **port mirror sidecar** automatically mirrors port `50082` → `50080` via `socat`, ensuring clients configured for the standalone embedding port work transparently.

- **Source Code**: [GitHub - ggml-org/llama.cpp](https://github.com/ggml-org/llama.cpp)
- **AUR Packages**: `llama.cpp-cuda` / `llama.cpp-hip` / `llama.cpp`

## Usage

Install the service and environment configuration:
  - `./local-chat.sh install [--no-start] [--new-config]`

Start/Stop/Restart/Enable/Disable the Service:
  - `./local-chat.sh start`
  - `./local-chat.sh stop`
  - `./local-chat.sh restart`
  - `./local-chat.sh enable`
  - `./local-chat.sh disable`

Check runtime status:
  - `./local-chat.sh status`

Tail service stdout/stderr logs:
  - `./local-chat.sh logs -f`

Edit service environment configuration and auto-restart:
  - `./local-chat.sh edit`

Run API validation tests:
  - `./local-chat.sh test`

Run llama-server as a transient systemd user service:
  - `./local-chat.sh exec [--env KEY=VALUE]* [-- llama-server-args...]`

Run a custom command inside the sandboxed environment:
  - `./local-chat.sh run [--env KEY=VALUE]* <command> [args...]`

Spawn an interactive shell inside the sandboxed environment:
  - `./local-chat.sh shell [--env KEY=VALUE]*`


### In-Memory Environment Overrides

The `exec`, `run`, and `shell` subcommands support a repeatable `--env KEY=VALUE` parameter. When passed, these parameters:
1. Override the values loaded from the `.env` configuration file on disk.
2. Are exported in the local shell environment in-memory for foreground execution.
3. Are dynamically passed to `systemd-run` via `--setenv=KEY=VALUE` for transient background runs in systemd.

These overrides are kept transient, keeping the main `.env` configuration file untouched. For example, to run the server temporarily on CPU without changing your permanent configuration:
```bash
./local-chat.sh exec --env LCHAT_N_GPU_LAYERS=0
```


## Default Models

### Default LLM Model

The local service runs **`Qwen3.6-35B-A3B-APEX-I-Compact`** as its primary chat and vision model.

#### Service Configuration Defaults

| Parameter | Default | Notes |
|-----------|---------|-------|
| `LCHAT_CTX_SIZE` | `240384` | Total context length, equals `80128` per slot |
| `LCHAT_PARALLEL` | `3` | Concurrent chat slots |
| `LCHAT_EXTRA_ARGS` | `--temp 0.6 --top-k 20 --repeat-penalty 1.1` | agentic workload tuning |
| `LCHAT_SPECULATIVE` | `--spec-type ngram-simple --spec-ngram-simple-size-n 6 --spec-ngram-simple-size-m 4` | speculative decoding config| 

#### Architecture (Qwen3.6-35B-A3B)

| Attribute                  | Value |
|----------------------------|-------|
| **Architecture Type**      | Sparse Mixture-of-Experts (MoE) with Hybrid Attention |
| **Transformer Layers**     | 40 |
| **Attention Layout**       | Alternating Gated DeltaNet (linear) & Gated Attention |
| **Total Parameters**       | 35 Billion |
| **Active Parameters**      | ~3 Billion per token |
| **Expert Count**           | 256 experts (8 routed + 1 shared active per token) |
| **Expert Intermediate Dim**| 512 |
| **Hidden Dimension**       | 2048 |
| **Native Max Context**     | 262,144 tokens (extensible to 1,000,000 via YaRN) |
| **Multimodal Inputs**      | Text, Image, Video |

GGUF File (APEX-I-Compact):
- **File:** `Qwen3.6-35B-A3B-APEX-I-Compact.gguf`
- **File Size:** ~17 GiB on disk
- **Quantization:** APEX-I-Compact — specialized Mixture-of-Experts adaptive quantization using importance matrix calibration.

Key specifications and limits:
- **Context Window**: The Qwen3.6 architecture natively supports a context window of up to **1,000,000 (1M) tokens**.
  - In this local deployment, the service allocates a physical context size of **240,000 tokens**, which is divided across **3 parallel slots (80,000 tokens context window size per slot)**.
- **Max Output (Generation) Limit**: The Qwen3.6 architecture supports a maximum output generation length of **65,536 (64K) tokens** in a single completion request.
- **Capabilities**: Completion, chat, native tool-calling, multi-modal vision inputs (using the mmproj GGUF file)
- **Recommended Temperature Settings**
  - A higher temperature leads to more varied responses and a lower temperature produces more focused and deterministic outputs.
  - General Tasks: Temperature: **1.0**
  - Precise Coding Tasks: Recommended Temperature: **0.6**

### Thinking and Reasoning Capabilities

The local **`Qwen3.6-35B-A3B-APEX-I-Compact`** model supports native chain-of-thought (CoT) reasoning.

- **Jinja Chat Template Integration**: The model uses a custom template [Qwen3.6-chat_template.jinja](Qwen3.6-chat_template.jinja) which exposes the `enable_thinking` parameter.
- **Default Behavior**: In our customized template, `enable_thinking` defaults to **`false`** (thinking off/none by default) to keep background memory queries, extraction, and verification tasks fast, cheap, and robust.
- **Thinking Mode Control**:
  - **API Request Control (`api_kwargs` / `extra_body`)**: You can explicitly override the default template behavior on a per-request basis by sending `chat_template_kwargs` in the root of the request payload. For example:
    ```json
    {
      "model": "qwen3",
      "messages": [{"role": "user", "content": "Say ok"}],
      "chat_template_kwargs": {
        "enable_thinking": true
      }
    }
    ```
    To disable it, pass `"enable_thinking": false`. Hindsight and other clients can set this globally by passing it inside their `extra_body` config (e.g. `HINDSIGHT_API_LLM_EXTRA_BODY='{"chat_template_kwargs": {"enable_thinking": false}}'`).
  - **System Prompt / Prompt Content Injection**: The template automatically inspects prompt messages (system, developer, or user prompts) for control tags:
    - Prepend **`<|think_on|>`** to the system instructions or prompt content to force the model to think (perform chain-of-thought reasoning).
    - Prepend **`<|think_off|>`** to force-disable thinking.
    - *Note: The chat template automatically detects and strips these control tags (`<|think_on|>` / `<|think_off|>`) from the final prompt text, so the model itself never sees them.*
  - **Local Router Virtual Alias (`qwen3-thinking`)**: For client integrations that do not support custom request payloads or template parameters (such as the Zed Editor), you can point the client to the local-router (port `51080`) and request model **`qwen3-thinking`**. The local-router automatically rewrites the request to use `qwen3` with the `enable_thinking` template argument enabled. (See [local-router.md](local-router.md) for details).
- **Client Integration**:
  - In **ZeroClaw**, configuring `reasoning_enabled = true` / `reasoning_effort = "low"` maps to these parameters.
  - In **LibreFang**, passing `reasoning_effort = "low"` or `thinking = true/false` controls response generation behavior.
  - In **Hermes Agent**, configuring `agent: reasoning_effort: "xhigh" (max), "high", "medium", "low", "minimal", "none" (disable)

### Default Completions Model

When completions mode is enabled (default via `LCOMP_ENABLED=true`), the service also hosts the code completion model **`Qwen2.5-Coder-1.5B-Instruct`** with alias `qwen-coder-fim` on the same server instance.

#### Service Configuration Defaults

| Parameter | Default | Notes |
|-----------|---------|-------|
| `LCOMP_ENABLED` | `true` | Set to false to disable completions |
| `LCOMP_CTX_SIZE` | `8192` | Max context length for completion slot |
| `LCOMP_PARALLEL` | `2` | Concurrent completion slots |
| `LCOMP_CACHE_TYPE_K` | `q4_0` | Key cache format |
| `LCOMP_CACHE_TYPE_V` | `q4_0` | Value cache format |

#### Architecture (Qwen2.5-Coder-1.5B)

| Attribute                  | Value |
|----------------------------|-------|
| **Parameters**             | 1.54B (Non-Embedding: 1.31B) |
| **Transformer Layers**     | 28 |
| **Hidden Size**            | 1536 |
| **Attention Mechanism**    | Grouped Query Attention (GQA) |
| **Attention Heads**        | 12 Query heads, 2 Key-Value heads |
| **Native Max Context**     | 32,768 tokens |
| **Activation Function**    | SwiGLU |
| **Layer Normalization**    | RMSNorm |
| **Tied Word Embeddings**   | Yes |

GGUF File (Q4_K_M):
- **File:** `qwen2.5-coder-1.5b-instruct-q4_k_m.gguf`
- **File Size:** ~1.0 GiB on disk
- **Quantization:** Q4_K_M — 4-bit quantization optimized for code generation speed


### Default Embedding Model

When combined mode is enabled (default via `LMBD_ENABLED=true`), the service also hosts the text embedding model **`Qwen3-Embedding-0.6B`** in `Q8_0` GGUF format on the same server instance.

#### Service Configuration Defaults

| Parameter | Default | Notes |
|-----------|---------|-------|
| `LMBD_N_CTX` | `4096` | Max context length per parallel slot |
| `LMBD_PARALLEL` | `2` | Concurrent embedding slots |
| `LMBD_UBATCH_SIZE` | `512` | Max hardware batch size |

#### Architecture (Qwen3-Embedding-0.6B)

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
| **Paper**                  | [arXiv:2506.05176](https://arxiv.org/abs/2506.05176) |

> **MRL** (Matryoshka Representation Learning) allows truncating the output embedding to any dimension from 32 to 1024, enabling smaller index sizes at a small accuracy cost. The full 1024-dimensional output is used by default.

GGUF File (Q8_0):
- **File:** `Qwen3-Embedding-0.6B-Q8_0.gguf`
- **File Size:** ~568 MiB on disk
- **Quantization:** Q8_0 — 8-bit integer weights, minimal quality loss vs. F16


## Service Ports

- **Default Port**: `50080` (HTTP) — primary chat and embedding API
- **Default Mirror Port**: `50082` (HTTP) — embedding-only port mirror (via socat sidecar)
- **Default Host**: `127.0.0.1`

### Service Endpoints 

- **`POST /v1/chat/completions`**: OpenAI-compatible chat completion endpoint (routed to the chat LLM).
- **`POST /v1/completions`**: OpenAI-compatible text completion endpoint.
- **`POST /completion`**: Native `llama.cpp` endpoint for custom prompt completion.
- **`POST /v1/embeddings`**: OpenAI-compatible embeddings endpoint (routed to the embedding LLM).
- **`POST /embedding`**: Native `llama.cpp` endpoint for embeddings.
- **`POST /tokenize`**: Converts input text into model-specific integer token IDs.
- **`POST /detokenize`**: Converts token IDs back into string characters.
- **`GET /v1/models`**: Lists all active model aliases.
- **`GET /health`**: Returns JSON details regarding slots, queue metrics, and service health.

### Embedding Port Mirror (Port `50082`)

When `LMBD_ENABLED=true`, the **portmirror** sidecar runs `socat` to forward port `50082` → `50080`. This ensures that clients configured for the standalone `local-embedding` service (which defaults to port 50082) work transparently when using the combined server.

All embedding endpoints available on port `50080` are accessible on port `50082`:
- **`POST /v1/embeddings`** and **`POST /embedding`** work identically on both ports.

The mirror port is configurable via `LMBD_MIRROR_PORT` in the env file. When `LMBD_ENABLED=false`, the sidecar runs `sleep infinity` and the port is not used.

---

## Configuration Files

The service stores its configuration in the systemd user configuration directory:

- **Service Unit**: `~/.config/systemd/user/local-chat.service`
- **Environment Configuration**: `~/.config/systemd/user/local-chat.env`
- **Model Preset File**: `~/.config/systemd/user/local-chat-preset.ini` (Automatically generated upon install/start/exec)
- **Launcher Script**: `~/.config/systemd/user/local-chat-launcher.sh` (Automatically generated; orchestrates llama-server and sidecars)

### Sidecars Configuration

The service supports running **sidecar processes** alongside `llama-server`. Sidecars are background processes managed by the service lifecycle — they start after llama-server and the service exits if any process (main or sidecar) terminates.

Sidecars are configured in the env file via:

```bash
# Space or semicolon separated list of sidecar names
LOCAL_SIDECARS="portmirror"

# For each sidecar, define CMD and optional ARGS:
# LOCAL_SIDECAR_<NAME>_CMD="command"
# LOCAL_SIDECAR_<NAME>_ARGS="arguments"
```

The built-in **portmirror** sidecar is pre-configured as a bash one-liner that checks `LMBD_ENABLED` at runtime:
- `true` → runs `socat TCP-LISTEN:${LMBD_MIRROR_PORT},fork,reuseaddr TCP:${LCHAT_HOST}:${LCHAT_PORT}`
- `false` → runs `sleep infinity`

To disable the port mirror, remove `portmirror` from `LOCAL_SIDECARS`. To add custom sidecars:

```bash
LOCAL_SIDECARS="portmirror mycustom"
LOCAL_SIDECAR_MYCUSTOM_CMD="/path/to/command"
LOCAL_SIDECAR_MYCUSTOM_ARGS="--flag value"
```

> [!NOTE]
> The portmirror sidecar requires `socat` to be installed (`pacman -S socat`). If `socat` is not available and embedding is enabled, the sidecar will fail and the service will restart.

### GPU and CPU Inference

By default, the service offloads execution to the GPU using ROCm/HIP.
To run the service on the CPU, run `./local-chat.sh edit` (or edit `~/.config/systemd/user/local-chat.env` directly) and edit this parameter:

```bash
# Number of layers to offload to GPU (all=999, none=0)
LCHAT_N_GPU_LAYERS=999
```

### Backend Device Selection (Dynamic Backend Loading)

When using a combined backend build (such as `libggml-git-hip`), the service supports dynamic loading of different acceleration backends (CPU, OpenBLAS, Vulkan, and HIP/ROCm) at runtime.

You can configure the target device in `~/.config/systemd/user/local-chat.env`:

```bash
# GPU/CPU backend device to use (run 'llama-cli --list-devices' for valid names)
# By default, llama-server automatically selects the best available device.
# To force a specific backend device, uncomment one of the options below:
# LCHAT_DEVICE="ROCm0"
# LCHAT_DEVICE="Vulkan0"
# LCHAT_DEVICE="BLAS"  # Force CPU OpenBLAS acceleration
# LCHAT_DEVICE="none"  # Force plain CPU execution (without OpenBLAS)
LCHAT_DEVICE=""
```

To list all available devices on your system, run:
```bash
llama-cli --list-devices
```

### Multi-GPU Configurations

If your system contains more than one GPU, you can configure the service to target a specific GPU or distribute the model across multiple cards.

#### Targeting a Specific GPU
You can force the service to use only a specific card in a multi-GPU environment:

*   **Option 1: Device configuration (via `LCHAT_DEVICE`)**
    Dynamic builds list GPU devices sequentially (e.g., `hip0`, `hip1`, `vulkan0`, `vulkan1`). Edit your `.env` file and set the device variable to target a specific index:
    ```bash
    # Target only the second AMD GPU
    LCHAT_DEVICE="hip1"
    ```
*   **Option 2: HIP Runtime restriction (via `HIP_VISIBLE_DEVICES`)**
    You can restrict device visibility at the driver level by adding an environment override in your `.env` file:
    ```bash
    # Hide all other GPUs, making only GPU 1 visible to the service
    Environment="HIP_VISIBLE_DEVICES=1"
    ```

#### Splitting Layers Across Multiple GPUs (Tensor Split)
Llama.cpp automatically splits model layers proportionally based on each GPU's available VRAM when all devices are visible. If you want to specify an explicit ratio (e.g. if cards have different sizes or to optimize overhead), use the `--tensor-split` (or `-ts`) flag inside `LCHAT_EXTRA_ARGS` in your `.env` file:

```bash
# Example: Distribute model layers evenly (50/50) across two identical GPUs
LCHAT_EXTRA_ARGS="--tensor-split 1,1"

# Example: Distribute across a 24GB GPU and a 12GB GPU (2:1 ratio)
LCHAT_EXTRA_ARGS="--tensor-split 2,1"
```

You can also specify which GPU handles consolidations and intermediate compute using `--main-gpu` (defaults to GPU 0):
```bash
# Consolidate intermediate calculations on GPU 1
LCHAT_EXTRA_ARGS="--tensor-split 1,1 --main-gpu 1"
```

### Speculative Decoding

By default, the service enables self-speculative decoding via **N-Gram lookup** to accelerate text generation.

#### How N-Gram Speculation Works:
* **No Draft Model Required**: Unlike traditional speculative decoding which loads a second smaller model (incurring extra memory and load latency), N-Gram lookup is a CPU-side lookup that matches sequences of tokens in the generation history.
* **Mechanism**: It matches the last $N$ tokens (key size `--spec-ngram-simple-size-n`), searches the generation history for identical sequences, and drafts the next $M$ tokens (draft size `--spec-ngram-simple-size-m`) that previously followed. The target model verifies all of them in parallel in a single forward pass.
* **Performance**: Highly optimized for structured agent outputs (like JSON, YAML, code blocks, or tool schema outputs) where formatting patterns and syntax repeat heavily, offering a **~1.3x to 1.4x speedup** with **zero VRAM overhead**.

This is configured via `LCHAT_SPECULATIVE_ARGS` in the environment file:

```bash
# Enabled by default in LCHAT_SPECULATIVE_ARGS
LCHAT_SPECULATIVE_ARGS="--spec-type ngram-simple --spec-ngram-simple-size-n 6 --spec-ngram-simple-size-m 4"
```

To disable speculative decoding, edit the environment file and remove the speculative arguments, leaving only:
```bash
LCHAT_SPECULATIVE_ARGS=""
```

## VRAM Usage

For detailed breakdowns of memory usage and concurrent execution scenarios (co-running Inference, Speech-to-Text, and Text-to-Speech), refer to [Central Memory Map](local-memory-map.md).


## Editor `Language Model` and `Edit Prediction Service` Integration

### Zed Editor Integration

To configure the Zed editor to use the local services for both chat and inline edit predictions (tab completions), add the following configuration block to your Zed `settings.json` file. This directs chat requests to the main `qwen3` model and code completions to the lightweight `qwen-coder-fim` model through the local service router (port `51080`):

```json
{
  "language_models": {
    "openai_compatible": {
      "local-inference": {
        "api_url": "http://localhost:51080",
        "available_models": [
          {
            "name": "qwen3",
            "max_tokens": 80128,
            "max_output_tokens": 16384,
            "max_completion_tokens": 80128,
            "capabilities": {
              "tools": true,
              "images": true,
              "parallel_tool_calls": true,
              "prompt_cache_key": true,
              "chat_completions": true,
              "interleaved_reasoning": true
            }
          }
        ]
      }
    }
  },
  "edit_predictions": {
    "provider": "open_ai_compatible_api",
    "open_ai_compatible_api": {
      "api_url": "http://localhost:51080",
      "model": "qwen-coder-fim",
      "max_output_tokens": 250
    },
    "allow_data_collection": "no"
  }
}
```

## Verification and Testing

You can test that the service is running and behaving correctly by running the validation command:

```bash
./local-chat.sh test
```

### Benchmarking Mode

To benchmark prefill and decoding latency and throughput using benchmark data, run:

Run Chat, Embedding, and Completions benchmarks (sequentially, if enabled):
 - `./local-chat.sh test --benchmark`

Run only the Completions benchmark (skipping others)
 - `./local-chat.sh test --benchmark --skip-all-chat --skip-embedding`

Skip the Completions benchmark, running Chat and Embedding
 - `./local-chat.sh test --benchmark --skip-completion`

Skip Phase 1 (Sequential Prefill) of the Chat benchmark
 - `./local-chat.sh test --benchmark --skip-prefill`

Skip Phase 3 (Prefix Caching & Distractor Tests) of the Chat benchmark
 - `./local-chat.sh test --benchmark --skip-distractor`

Specify the number of runs to compute cumulative average over (e.g. 5 runs)
 - `./local-chat.sh test --benchmark --repeat 5`

The chat completion benchmark evaluates prefill speed, generation speed, and Key-Value (KV) cache retrieval latency using a truncated ~30k token context (~115k characters) from `benchmark-context.md`. The benchmark runs in 4 distinct phases:

1. **Phase 0: Warmup**
   - Runs a quick validation query ("Hello, respond with exactly: Hello World!") to measure base TTFT/latency and ensure the server is ready.
   - Sleeps for 10 seconds.

2. **Phase 1: Sequential Prefill**
   - Incrementally feeds context chunks (10% increments) to monitor prefill speed and new chunk parsing efficiency.
   - Can be bypassed entirely using the `--skip-prefill` parameter (e.g. `./local-chat.sh test --benchmark --skip-prefill`).
   - Sleeps for 10 seconds.

3. **Phase 2: Chat Generation**
   - Loads the full prefilled context and requests a 300-word summary to evaluate decode throughput (expecting ~25+ tokens/sec).
   - Sleeps for 10 seconds (if Phase 3 is active).

4. **Phase 3: Prefix Caching & Distractor Tests**
   - Sequentially cycles 5 times through:
     - *3a. Half Prefill Prompt + Question* (measures prefix cache hit/latency).
     - *3b. Distractor Prompt* (a short, unrelated question to test cache eviction/interference).
     - *3c. Full Prefill Prompt + Question* (measures prompt re-parsing speed after distractor cache eviction).
   - Can be skipped entirely using the `--skip-distractor` parameter (e.g. `./local-chat.sh test --benchmark --skip-distractor`) to avoid overheating during extended test suites.

> [!NOTE]
> If `--repeat` is omitted, the chat completion benchmark defaults to `1` run. If `--repeat` is explicitly provided, it will use the specified number of runs.

