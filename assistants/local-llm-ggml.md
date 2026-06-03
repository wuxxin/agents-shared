# Local LLM and Embedding Service Guide

`local-llm-ggml.sh` manages the local `llama-server` systemd user service (`local-llm-ggml.service`), serving both the Chat/Vision LLM and the Text Embedding model simultaneously from a single process using router mode (`--models-preset`).

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

### Default Embedding

The local service runs **`Qwen3-Embedding-0.6B-Q8_0.gguf`** as its embeddings model. 

Key specifications and limits:
- **Embedding Context Size (`LLM_EMBEDDING_N_CTX`):** `8192`
- **Pooling:** `mean`

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
To run the service on the CPU, run `./local-llm-ggml.sh edit` (or edit `~/.config/systemd/user/local-llm-ggml.env` directly) and edit this parameter:

```bash
# Number of layers to offload to GPU (all=99)
LR_N_GPU_LAYERS=99
# To run inference on CPU instead of GPU (none=0)
# LR_N_GPU_LAYERS=0
```

## VRAM Usage

For detailed breakdowns of memory usage and concurrent execution scenarios (co-running Inference, Speech-to-Text, and Text-to-Speech), refer to [Central Memory Map](file:///home/wuxxin/agent-shared/code/agents-shared/assistants/local-memory-map.md).


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

# Run ONLY the Chat benchmark
./local-llm-ggml.sh test --benchmark --only-chat

# Run ONLY the Embeddings benchmark
./local-llm-ggml.sh test --benchmark --only-embeddings

# Skip Phase 1 (Sequential Prefill) of the Chat benchmark
./local-llm-ggml.sh test --benchmark --only-chat --skip-prefill

# Skip Phase 3 (Prefix Caching & Distractor Tests) of the Chat benchmark
./local-llm-ggml.sh test --benchmark --only-chat --skip-distractor

# Specify the number of runs to compute cumulative average over (e.g. 5 runs)
./local-llm-ggml.sh test --benchmark --repeat 5
```

The chat completion benchmark evaluates prefill speed, generation speed, and Key-Value (KV) cache retrieval latency using a truncated ~30k token context (~115k characters) from `benchmark-context.md`. The benchmark runs in 4 distinct phases:

1. **Phase 0: Warmup**
   - Runs a quick validation query ("Hello, respond with exactly: Hello World!") to measure base TTFT/latency and ensure the server is ready.
   - Sleeps for 10 seconds.

2. **Phase 1: Sequential Prefill**
   - Incrementally feeds context chunks (10% increments) to monitor prefill speed and new chunk parsing efficiency.
   - Can be bypassed entirely using the `--skip-prefill` parameter (e.g. `./local-llm-ggml.sh test --benchmark --only-chat --skip-prefill`).
   - Sleeps for 10 seconds.

3. **Phase 2: Chat Generation**
   - Loads the full prefilled context and requests a 300-word summary to evaluate decode throughput (expecting ~25+ tokens/sec).
   - Sleeps for 10 seconds (if Phase 3 is active).

4. **Phase 3: Prefix Caching & Distractor Tests**
   - Sequentially cycles 5 times through:
     - *3a. Half Prefill Prompt + Question* (measures prefix cache hit/latency).
     - *3b. Distractor Prompt* (a short, unrelated question to test cache eviction/interference).
     - *3c. Full Prefill Prompt + Question* (measures prompt re-parsing speed after distractor cache eviction).
   - To avoid GPU overheating on target hardware (Radeon Pro W6800), a 10-second cooldown sleep is executed *only* after the full context query (`3c`). No sleeps are executed after the half-prefill or distractor queries.
   - Can be skipped entirely using the `--skip-distractor` parameter (e.g. `./local-llm-ggml.sh test --benchmark --only-chat --skip-distractor`) to avoid overheating during extended test suites.
  
> [!NOTE]
> If `--repeat` is omitted, the embedding benchmark defaults to `10` runs to calculate a stable cumulative average, while the chat completion benchmark defaults to `1` run. If `--repeat` is explicitly provided, it will use the specified number of runs for all executed benchmarks.

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

