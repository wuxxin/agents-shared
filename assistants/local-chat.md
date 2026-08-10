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

Display service file, environment configuration, preset configuration, launcher script, and transient exec command:
  - `./local-chat.sh cat`

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

The local service runs **`BigBang-v1`** (`endless-frontier/BigBang-v1`, served via GGUF quantization `BigBang-v1-IQ4_XS.gguf` paired with `mmproj-endless-frontier_BigBang-v1-f16.gguf`) as its default primary chat, reasoning, and vision model.

#### About BigBang-v1

**BigBang-v1** is a general-purpose LLM evolved from `Qwen3.6-35B-A3B` through an efficient post-training pipeline using an **adversarial, self-evolving synthetic data framework**. The framework employs two core autonomous agent components:
1. **Generator Agents**: Continually propose and solve increasingly challenging scientific, coding, and technical problems.
2. **Critic Agents**: Evaluate correctness, difficulty, scalability, and diversity, using held-out real research tasks to calibrate the evolving synthetic data distribution.

Through iterative generator–critic interaction across ~10,000 high-difficulty post-training examples, BigBang-v1 achieves open-ended capability growth, substantially outperforming its base model across scientific research, long-horizon search, coding, and tool-use benchmarks, and achieving aggregate performance exceeding DeepSeek V4 Flash (284B) and matching/exceeding DeepSeek V4 Pro (1.6T) on key evaluations.

#### Service Configuration Defaults

| Parameter | Default | Notes |
|-----------|---------|-------|
| `LCHAT_MODEL` | `/data/public/machine-learning/models/vision-text/BigBang-v1-IQ4_XS.gguf` | IQ4_XS GGUF quantization (~17.95 GB VRAM) |
| `LCHAT_MMPROJ` | `/data/public/machine-learning/models/vision-text/BigBang-v1-mmproj-f16.gguf` | Multimodal vision projector (f16, ~840 MB) |
| `LCHAT_CTX_SIZE` | `240384` | Total allocated context length |
| `LCHAT_PARALLEL` | `2` | Concurrent chat slots (120,192 tokens per slot) |
| `LCHAT_EXTRA_ARGS` | `--temp 0.6 --top-k 20 --repeat-penalty 1.1` | Agentic & technical workload tuning |

#### Architecture (BigBang-v1 / Qwen3.6-35B-A3B)

| Attribute | Value |
|---|---|
| **Base Model** | `Qwen/Qwen3.6-35B-A3B` (fine-tuned by endless-frontier) |
| **Architecture Type** | Sparse Mixture-of-Experts (MoE) with Hybrid Attention |
| **Transformer Layers** | 40 |
| **Attention Layout** | Alternating Gated DeltaNet (linear) & Gated Attention |
| **Total Parameters** | 35.95 Billion (35B MoE) |
| **Active Parameters** | ~3 Billion per token |
| **Expert Count** | 256 experts (8 routed + 1 shared active per token) |
| **Expert Intermediate Dim**| 512 |
| **Hidden Dimension** | 2048 |
| **Native Max Context** | 262,144 tokens (extensible to 1,000,000 via YaRN) |
| **Multimodal Inputs** | Text, Image, Video |

GGUF File (`IQ4_XS`):
- **File:** `BigBang-v1-IQ4_XS.gguf`
- **File Size:** ~17.95 GiB on disk
- **Quantization:** `IQ4_XS` — imatrix-calibrated 4-bit quantization providing an optimal balance between VRAM footprint and model accuracy.
- **Vision Projector:** `BigBang-v1-mmproj-f16.gguf` (~840 MiB).

Key specifications and limits:
- **Context Window**: The Qwen3.6 architecture natively supports a context window of up to **1,000,000 (1M) tokens**. In this local deployment, the service allocates a physical context size of **240,384 tokens**, divided across **2 parallel slots (120,192 tokens per slot)**.
- **Max Output (Generation) Limit**: Supports a maximum output generation length of **65,536 (64K) tokens** in a single completion request.
- **Capabilities**: Completion, chat, reasoning, agentic tool execution, long-horizon search, multi-modal vision inputs.
- **Recommended Temperature Settings**:
  - **0.6**: Recommended for coding, diff generation, tool execution & precise reasoning.
  - **1.0**: Recommended for creative writing & open-ended brainstorming.

#### Benchmark Performance Summary

| Benchmark Category | Benchmark Name | Base Model Score (Qwen3.6-35B) | BigBang-v1 Score | Relative Gain | Frontier Comparison |
|---|---|---:|---:|---:|---|
| **Coding Tasks** | SWE-Bench Pro | 43.6 (100%) | **54.2 (+24.3%)** | +24.3% | Beats DeepSeek V4 Flash (52.6) & Pro (55.4 near-match) |
| **Reasoning** | Humanity's Last Exam (HLE) | 36.2 (100%) | **50.3 (+39.0%)** | +39.0% | Exceeds DeepSeek V4 Pro (48.2) & Flash (45.1) |
| **Long-Horizon Search** | BrowseComp | 67.9 (100%) | **76.5 (+12.7%)** | +12.7% | Exceeds DeepSeek V4 Flash (73.2) |
| **AI Engineering** | MLE-Bench (Lite) | 31.8 (100%) | **59.1 (+85.8%)** | +85.8% | Matches GPT-5.5 (59.1) & DeepSeek V4 Pro (59.1) |
| **Scientific Research** | FrontierScience Research (FS-R) | 11.9 (100%) | **46.2 (+288.2%)** | +288.2% | Exceeds Claude Opus 4.8 (45.2) & DeepSeek V4 Pro (40.7) |
| **Paper Replication** | PaperBench (Code-Dev) | 30.7 (100%) | **53.6 (+74.6%)** | +74.6% | Exceeds DeepSeek V4 Pro (50.4) & Flash (40.4) |
| **Scientific Coding** | SciCode-V (Main / Sub) | 26.6 / 56.5 (100%) | **50.0 / 68.6 (+88.0% / +21.4%)** | +88.0% / +21.4% | SOTA performance among 35B models |
| **Bioinformatics** | BioMysteryBench (HD) | 2.0 (100%) | **15.7 (+685.0%)** | +685.0% | Exceeds DeepSeek V4 Pro (13.7) |
| **AGI Tracking** | XBench | 32.6 (100%) | **58.4 (+79.1%)** | +79.1% | Massive gain in multi-step reasoning |

### Thinking and Reasoning Capabilities

**BigBang-v1** inherits native chain-of-thought (CoT) reasoning capabilities from its base `Qwen3.6-35B-A3B` architecture, augmented by its self-evolving adversarial synthetic data training across complex scientific research, paper replication, and long-horizon search tasks.

- **Native `<think>...</think>` CoT Format**:
  - During reasoning, BigBang-v1 outputs its step-by-step chain-of-thought enclosed within `<think>` and `</think>` XML tags before producing the final answer or executing tool calls (`<tool_call>`).
  - Standard reasoning parsers (e.g. `--reasoning-parser qwen3` in SGLang/vLLM or `llama-server` Jinja template parsing) automatically extract this reasoning text into `message.reasoning_content`.

- **Integrated Chat Template (`jinja = on`, Default)**:
  - `endless-frontier/BigBang-v1` embeds the official native `Qwen3.6-35B-A3B` chat template directly inside its GGUF metadata (`tokenizer.ggml.chat_template`).
  - **Research & Best Practice**: BigBang-v1 was fine-tuned on ~10,000 frontier tasks using this exact native template for multimodal vision tags (`<|vision_start|><|image_pad|><|vision_end|>`), structured tool calls (`<tools>...</tools>`, `<function=...>`, `<parameter=...>`), and reasoning (`<think>...</think>`). Leaving `LCHAT_CHAT_TEMPLATE_FILE=""` in `local-chat.sh` enables `jinja = on` in `preset.ini`, letting `llama-server` use the integrated template natively. This ensures 100% distribution alignment with the training dataset and prevents startup errors due to missing external template files.
- **External Template Overrides (`LCHAT_CHAT_TEMPLATE_FILE`)**:
  - If custom Jinja parser logic is required (e.g. `froggeric` fixed template for tool-retry guards), you can specify `LCHAT_CHAT_TEMPLATE_FILE=/path/to/custom_template.jinja`. For standard BigBang-v1 serving, using the integrated model template is recommended.
- **Service Default (`enable_thinking: false`)**:
  - In `local-chat.sh`, `LCHAT_CHAT_TEMPLATE_KWARGS='{"enable_thinking": false}'` disables thinking by default. This ensures fast, low-latency execution for high-frequency background agent tasks (extraction, RAG memory queries, FIM completions).

- **How to Enable Thinking on Demand**:
  1. **Per-Request Payload (`chat_template_kwargs`)**:
     Pass `chat_template_kwargs: {"enable_thinking": true}` in the root of your JSON request body:
     ```json
     {
       "model": "qwen3",
       "messages": [{"role": "user", "content": "Solve this multi-step scientific problem."}],
       "chat_template_kwargs": {
         "enable_thinking": true
       }
     }
     ```
  2. **Prompt Control Tags**:
     Prepend `<|think_on|>` in the prompt or system instructions to force-enable thinking. (Prepend `<|think_off|>` to force-disable). The chat template automatically detects and strips these control tags from the input payload.
  3. **Virtual Alias (`qwen3-thinking`)**:
     For clients that cannot customize request parameters (e.g., Zed Editor), route requests through `local-router` (port `51080`) using model name **`qwen3-thinking`**. The router automatically injects `enable_thinking: true`.

- **Agent Framework Compatibility**:
  - **ZeroClaw**: Set `reasoning_enabled = true` / `reasoning_effort = "medium"` (or `"high"`).
  - **LibreFang**: Set `thinking = true` or `reasoning_effort = "medium"`.
  - **Hermes Agent**: Set `agent: reasoning_effort: "high"` or `"xhigh"`.

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
| `LCOMP_EXTRA_ARGS` | `""` | Extra arguments / preset settings for completion model |

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
| `LMBD_CTX_SIZE` | `16384` | Max context length per parallel slot |
| `LMBD_PARALLEL` | `2` | Concurrent embedding slots |
| `LMBD_UBATCH_SIZE` | `16384` | Max hardware batch size (matches LMBD_CTX_SIZE) |
| `LMBD_EXTRA_ARGS` | `--flash-attn on` | Extra arguments / preset settings for embedding model |

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
LCHAT_SIDECARS="portmirror"

# For each sidecar, define CMD and optional ARGS:
# LCHAT_SIDECAR_<NAME>_CMD="command"
# LCHAT_SIDECAR_<NAME>_ARGS="arguments"
```

The built-in **portmirror** sidecar is pre-configured as a bash one-liner that checks `LMBD_ENABLED` at runtime:
- `true` → runs `socat TCP-LISTEN:${LMBD_MIRROR_PORT},fork,reuseaddr TCP:${LCHAT_HOST}:${LCHAT_PORT}`
- `false` → runs `sleep infinity`

To disable the port mirror, remove `portmirror` from `LCHAT_SIDECARS`. To add custom sidecars:

```bash
LCHAT_SIDECARS="portmirror mycustom"
LCHAT_SIDECAR_MYCUSTOM_CMD="/path/to/command"
LCHAT_SIDECAR_MYCUSTOM_ARGS="--flag value"
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

By default, the service enables **Multi-Token Prediction (MTP)** speculative decoding using a standalone `Q8_0` MTP draft head file to accelerate text generation.

#### How MTP Speculation Works:
* **Standalone Draft Head Addon**: The service pairs the primary `Agents-A1-APEX-I-Compact.gguf` model with `Qwen3.6-35B-A3B-MTP-ONLY.gguf` (acquired from [`IHaveNoClueAndIMustPost/Qwen3.6-35A3B-MTP-TENSORS-ONLY`](https://huggingface.co/IHaveNoClueAndIMustPost/Qwen3.6-35A3B-MTP-TENSORS-ONLY), `Q8_0` ~855 MiB).
* **Mechanism**: During each forward step, the MTP draft head takes the 2048-dimensional hidden state ($h_t$) from the final layer of the base model and predicts candidate future tokens ($w_{t+1}, w_{t+2}$) in $<1\text{ ms}$. The target model verifies all candidate tokens in parallel in a single batched forward pass.
* **Performance & VRAM**: Provides a **~1.45x to 1.75x speedup** across all prompt types (prose, coding, tool-calling, and reasoning) with minimal VRAM overhead (~17.8 GiB total VRAM with `mmproj`).

#### Tuning MTP (`--spec-draft-n-max N`):

The maximum number of draft tokens proposed per step is controlled by `--spec-draft-n-max N` in `LCHAT_SPECULATIVE`:

* **`N=1` (Conservative)**:
  * Drafts 1 extra token per step. Highest token acceptance rate (~85%+), minimal latency overhead per step, ~1.25x–1.40x overall speedup.
* **`N=2` (Default - Recommended for Personal Agents & Light Coding)**:
  * Drafts 2 extra tokens per step. **Optimal balance for personal agentic workloads and code completions**.
  * **Why `N=2` is optimal**: Personal agents (ZeroClaw, LibreFang, Hermes) and inline code completion engines frequently output semi-predictable structures (JSON tool arguments, function signatures, indentations, variable definitions, and short reasoning steps). Drafting 2 tokens hits the sweet spot (~70%–80% acceptance rate) where draft tokens are accepted consistently. It delivers peak effective throughput without wasting compute on verifying long candidate sequences when logic branches or variable names change.
* **`N=3` / `N=4` (Aggressive)**:
  * Drafts 3 to 4 extra tokens per step. Best for highly repetitive code boilerplate generation (~1.60x–2.00x peak speedup).
  * *Trade-off*: On creative writing or complex chain-of-thought reasoning where acceptance drops below 50%, verifying 4 rejected tokens per step adds extra compute overhead, slightly increasing step latency.

#### Reverting to N-Gram or Disabling Speculative Decoding:

If `LCHAT_MTP` is specified but the draft file does not exist on disk, `local-chat.sh` will print an error (`Error: MTP draft model file not found at ...`) instructing you to run `scripts/local-download.sh <target_dir> --llm` and exit immediately (`exit 1`) to prevent starting with an invalid model configuration.

To explicitly use CPU-based N-Gram lookup speculative decoding (zero extra VRAM):
```bash
LCHAT_MTP=""
LCHAT_SPECULATIVE="--spec-type ngram-simple --spec-ngram-simple-size-n 6 --spec-ngram-simple-size-m 4"
```

To disable speculative decoding entirely:
```bash
LCHAT_MTP=""
LCHAT_SPECULATIVE=""
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
            "max_tokens": 120192,
            "max_output_tokens": 16384,
            "max_completion_tokens": 120192,
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


## Old Default Models

### Agents-A1-APEX-I-Compact (Qwen3.6-35B-A3B)

Previous default chat and vision model before the update to BigBang-v1.

#### Service Configuration (Legacy)

| Parameter | Default Value | Notes |
|---|---|---|
| `LCHAT_MODEL` | `/data/public/machine-learning/models/vision-text/Agents-A1-APEX-I-Compact.gguf` | Legacy model file |
| `LCHAT_MMPROJ` | `/data/public/machine-learning/models/vision-text/Agents-A1-APEX-I-Compact.mmproj.gguf` | Legacy vision projector |
| `LCHAT_CTX_SIZE` | `240384` | Context length (divided across parallel slots) |
| `LCHAT_PARALLEL` | `2` | Concurrent slots |

#### Architecture (Agents-A1 / Qwen3.6-35B-A3B)

| Attribute | Value |
|---|---|
| **Architecture Type** | Sparse Mixture-of-Experts (MoE) with Hybrid Attention |
| **Transformer Layers** | 40 |
| **Attention Layout** | Alternating Gated DeltaNet (linear) & Gated Attention |
| **Total Parameters** | 35.95 Billion |
| **Active Parameters** | ~3 Billion per token |
| **Expert Count** | 256 experts (8 routed + 1 shared active per token) |
| **Expert Intermediate Dim**| 512 |
| **Hidden Dimension** | 2048 |
| **Native Max Context** | 262,144 tokens (extensible to 1,000,000 via YaRN) |
| **Multimodal Inputs** | Text, Image, Video |

GGUF File (APEX-I-Compact):
- **File:** `Agents-A1-APEX-I-Compact.gguf`
- **File Size:** ~17 GiB on disk
- **Quantization:** APEX-I-Compact — specialized Mixture-of-Experts adaptive quantization using importance matrix calibration.

#### Legacy Thinking and Reasoning Capabilities (Agents-A1)

The previous **`Agents-A1-APEX-I-Compact`** model supported chain-of-thought (CoT) reasoning via custom `<|think_on|>` / `<|think_off|>` tags in system/user prompts or `chat_template_kwargs: {"enable_thinking": true/false}`. In `local-chat.sh`, `enable_thinking` defaulted to `false` to keep background tasks fast and deterministic.

#### Legacy Chat Template (`Qwen3.6-chat_template.jinja` / `froggeric`)

The previous model deployment explicitly overrode the embedded GGUF chat template using an external file:

- **File Path:** `/data/public/machine-learning/models/vision-text/Qwen3.6-chat_template.jinja`
- **Source Origin:** Derived from [`froggeric/Qwen-Fixed-Chat-Templates`](https://huggingface.co/froggeric/Qwen-Fixed-Chat-Templates).
- **Service Parameter (Legacy):** `LCHAT_CHAT_TEMPLATE_FILE=/data/public/machine-learning/models/vision-text/Qwen3.6-chat_template.jinja`

##### Key Features of the Legacy Chat Template:

1. **`llama-server` Jinja Compatibility Fixes**: Fixed edge-case bugs in `llama.cpp`'s internal Jinja template engine when rendering multi-turn tool responses (`<tool_response>`) and function call schemas (`<tool_call>`).
2. **Automatic Tool-Loop Mitigation**: Tracked consecutive tool execution failures (`ns2.consecutive_failures >= 2`). If an agent tool call failed multiple times in succession, the template automatically forced `<think>\n\n</think>\n\n` (disabling CoT thinking) on the next turn to prevent infinite reasoning loops during error recovery.
3. **Role & Thought Parsing**: Normalized non-standard roles (e.g. `developer` role) into `system` instructions, and parsed reasoning content stored in `message.reasoning_content` or `thought` fields into `<think>...</think>` blocks.
4. **Prompt Control Directive Stripping**: Scanned input messages for `<|think_on|>` and `<|think_off|>` directives, set the internal `ns_state.thinking` boolean flag accordingly, and automatically stripped the control strings from the prompt text prior to model tokenization.

