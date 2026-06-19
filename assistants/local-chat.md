# Local Chat Service Guide

`local-chat.sh` manages the local `llama-server` systemd user service (`local-chat.service`), serving the Chat/Vision LLM.

Note: Text embeddings are served separately by the standalone [local-embedding.md](local-embedding.md) service.

- **Source Code**: [GitHub - ggml-org/llama.cpp](https://github.com/ggml-org/llama.cpp)
- **AUR Packages**: `llama.cpp-cuda` / `llama.cpp-hip` / `llama.cpp`

## Usage

```bash
# Install the service and environment configuration
./local-chat.sh install [--no-start] [--new-config]

# Start/Stop/Restart the service
./local-chat.sh start
./local-chat.sh stop
./local-chat.sh restart
./local-chat.sh enable
./local-chat.sh disable

# Check runtime status
./local-chat.sh status

# Tail service stdout/stderr logs
./local-chat.sh logs -f

# Edit service environment configuration and auto-restart
./local-chat.sh edit

# Run API validation tests
./local-chat.sh test

# Run llama-server as a transient systemd user service
./local-chat.sh exec [--env KEY=VALUE]* [-- llama-server-args...]

# Run a custom command inside the sandboxed environment
./local-chat.sh run [--env KEY=VALUE]* <command> [args...]

# Spawn an interactive shell inside the sandboxed environment
./local-chat.sh shell [--env KEY=VALUE]*
```

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

### Default LLM

The local service runs **`Qwen3.6-35B-A3B-APEX-I-Compact`** as its primary chat and vision model.

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

- **Jinja Chat Template Integration**: The model uses a custom template [Qwen3.6-chat_template.jinja](file:///data/public/machine-learning/models/vision-text/Qwen3.6-chat_template.jinja) which exposes the `enable_thinking` parameter.
- **Thinking Mode Control**:
  - By default, `enable_thinking` is `true`. The template pre-fills `<think>\n` at the start of the assistant response, encouraging the model to perform reasoning.
  - When thinking is disabled (e.g. `enable_thinking = false` via template arguments or if `<|think_off|>` is detected in prompt content), the template pre-fills `<think>\n\n</think>\n\n`, immediately closing the reasoning block and forcing the model to generate the direct answer.
- **Client Integration**:
  - In **ZeroClaw**, configuring `reasoning_enabled = true` / `reasoning_effort = "low"` maps to these parameters.
  - In **LibreFang**, passing `reasoning_effort = "low"` or `thinking = true/false` controls response generation behavior.
  - In **Moltis**, preset configurations mapping to `reasoning_effort = "low"` adjust agent-level thinking budgets and parameters.

## Service Configuration & Ports

- **Default Port**: `50080` (HTTP)
- **Default Host**: `127.0.0.1`

### Service Endpoints (Port `50080`)

- **`POST /v1/chat/completions`**: OpenAI-compatible chat completion endpoint (routed to the chat LLM).
- **`POST /v1/completions`**: OpenAI-compatible text completion endpoint.
- **`POST /completion`**: Native `llama.cpp` endpoint for custom prompt completion.
- **`POST /tokenize`**: Converts input text into model-specific integer token IDs.
- **`POST /detokenize`**: Converts token IDs back into string characters.
- **`GET /v1/models`**: Lists all active model aliases.
- **`GET /health`**: Returns JSON details regarding slots, queue metrics, and service health.

---

## Configuration Files

The service stores its configuration in the systemd user configuration directory:

- **Service Unit**: `~/.config/systemd/user/local-chat.service`
- **Environment File**: `~/.config/systemd/user/local-chat.env`

### GPU and CPU Inference

By default, the service offloads execution to the GPU using ROCm/HIP.
To run the service on the CPU, run `./local-chat.sh edit` (or edit `~/.config/systemd/user/local-chat.env` directly) and edit this parameter:

```bash
# Number of layers to offload to GPU (all=999)
LCHAT_N_GPU_LAYERS=999
# To run inference on CPU instead of GPU (none=0)
# LCHAT_N_GPU_LAYERS=0
```

### Backend Device Selection (Dynamic Backend Loading)

When using a combined backend build (such as `libggml-git-hip`), the service supports dynamic loading of different acceleration backends (CPU, OpenBLAS, Vulkan, and HIP/ROCm) at runtime.

You can configure the target device using the `LCHAT_DEVICE` environment variable. Run `./local-chat.sh edit` (or edit `~/.config/systemd/user/local-chat.env` directly) and configure the device:

```bash
# GPU/CPU backend device to use (e.g. hip, vulkan, cpu, openblas)
# By default, llama-server automatically selects the best available device.
# To force a specific backend device, uncomment one of the options below:
# LCHAT_DEVICE="hip"
# LCHAT_DEVICE="vulkan"
# LCHAT_DEVICE="cpu"
# LCHAT_DEVICE="openblas"
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
LCHAT_EXTRA_ARGS="--flash-attn on --tensor-split 1,1"

# Example: Distribute across a 24GB GPU and a 12GB GPU (2:1 ratio)
LCHAT_EXTRA_ARGS="--flash-attn on --tensor-split 2,1"
```

You can also specify which GPU handles consolidations and intermediate compute using `--main-gpu` (defaults to GPU 0):
```bash
# Consolidate intermediate calculations on GPU 1
LCHAT_EXTRA_ARGS="--flash-attn on --tensor-split 1,1 --main-gpu 1"
```


### Speculative Decoding (Optional)

By default, the service enables self-speculative decoding via **N-Gram lookup** to accelerate text generation.

#### How N-Gram Speculation Works:
* **No Draft Model Required**: Unlike traditional speculative decoding which loads a second smaller model (incurring extra memory and load latency), N-Gram lookup is a CPU-side lookup that matches sequences of tokens in the generation history.
* **Mechanism**: It matches the last $N$ tokens (key size `--spec-ngram-simple-size-n`), searches the generation history for identical sequences, and drafts the next $M$ tokens (draft size `--spec-ngram-simple-size-m`) that previously followed. The target model verifies all of them in parallel in a single forward pass.
* **Performance**: Highly optimized for structured agent outputs (like JSON, YAML, code blocks, or tool schema outputs) where formatting patterns and syntax repeat heavily, offering a **~1.3x to 1.4x speedup** with **zero VRAM overhead**.

This is configured via `LCHAT_EXTRA_ARGS` in the environment file:

```bash
# Enabled by default in LCHAT_EXTRA_ARGS:
LCHAT_EXTRA_ARGS="--flash-attn on --spec-type ngram-simple --spec-ngram-simple-size-n 6 --spec-ngram-simple-size-m 4"
```

To disable speculative decoding, edit the environment file and remove the speculative arguments, leaving only:
```bash
LCHAT_EXTRA_ARGS="--flash-attn on"
```

## VRAM Usage

For detailed breakdowns of memory usage and concurrent execution scenarios (co-running Inference, Speech-to-Text, and Text-to-Speech), refer to [Central Memory Map](local-memory-map.md).


## Verification & Manual Testing

You can test that the service is running and behaving correctly by running the validation command:

```bash
./local-chat.sh test
```

### Benchmarking Mode

To benchmark prefill and decoding latency and throughput using `benchmark-context.md`, run:

```bash
# Run the Chat benchmark
./local-chat.sh test --benchmark

# Skip Phase 1 (Sequential Prefill) of the Chat benchmark
./local-chat.sh test --benchmark --skip-prefill

# Skip Phase 3 (Prefix Caching & Distractor Tests) of the Chat benchmark
./local-chat.sh test --benchmark --skip-distractor

# Specify the number of runs to compute cumulative average over (e.g. 5 runs)
./local-chat.sh test --benchmark --repeat 5
```

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

Alternatively, you can test it manually using `curl`:

### Chat Completion Test
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
