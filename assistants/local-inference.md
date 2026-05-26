# Local Inference Management Guide

`local-inference.sh` acts as a hub orchestration script managing three separate, persistent `llama-server` instances:
1. **Local Chat/Vision LLM** (`local-chat.sh`)
2. **Local Text Embeddings** (`local-embeddingss.sh`)
3. **Local Document Reranking** (`local-rerank.sh`)

This split architecture allows you to start, stop, configure, and monitor each inference service independently.

- **Source Code**: [GitHub - ggml-org/llama.cpp](https://github.com/ggml-org/llama.cpp)
- **AUR Packages**:
  - `llama.cpp-cuda` / `llama.cpp-hip` / `llama.cpp`

## Hub Usage

The primary hub script (`local-inference.sh`) delegates lifecycle commands to all sub-services:

```bash
# Install all three services
./local-inference.sh install [--no-start]

# Start/Stop/Restart all services
./local-inference.sh start
./local-inference.sh stop
./local-inference.sh restart

# Check the status of all three services
./local-inference.sh status

# Tail combined logs from all three services
./local-inference.sh logs -f

# Run validation tests on all three services
./local-inference.sh test
```

## Individual Services

Each service can also be managed independently:

| Service | Port | Endpoint | Control Script | Description |
|---|---|---|---|---|
| **Local-Chat** | `50080` | `/v1/chat/completions` | `local-chat.sh` | Chat & Vision LLM completions |
| **Local-Embeddings** | `50085` | `/v1/embeddings` | `local-embeddings.sh` | Vector embeddings |
| **Local-Rerank** | `50086` | `/v1/rerank` | `local-rerank.sh` | Relevance reranking |

Every control script (`local-chat.sh`, `local-embeddings.sh`, `local-rerank.sh`) supports standard lifecycle commands:
- `install [--no-start]`
- `uninstall`
- `start` / `stop` / `restart` / `status`
- `enable` / `disable`
- `logs [args...]`
- `edit` (opens the specific `.env` file and restarts the service)
- `exec` / `shell` (run tools/interactive command line in the service sandbox)
- `test` (executes curl tests for that specific service)

---

## Service Endpoints

Each service exposes standard and native APIs:

### 1. Local-Chat Service (Port `50080`)
- **`POST /v1/chat/completions`**: OpenAI-compatible endpoint for generating completions from message sequences. (Supports system prompt instructions, user inputs, and reasoning tokens).
- **`POST /v1/completions`**: OpenAI-compatible endpoint for completing raw text prompts.
- **`POST /completion`**: Native `llama.cpp` endpoint for custom prompt processing (supports grammar models and strict schema validation).
- **`POST /tokenize`**: Converts input text into model-specific integer token IDs.
- **`POST /detokenize`**: Converts token IDs back into string characters.
- **`GET /v1/models`**: Lists the active chat model alias.
- **`GET /health`**: Returns JSON details regarding slots, queue metrics, and service health.

### 2. Local-Embeddings Service (Port `50085`)
- **`POST /v1/embeddings`**: OpenAI-compatible endpoint for generating vector embeddings. Accepts strings or arrays of strings and returns float vector arrays.
- **`POST /embedding`**: Native `llama.cpp` endpoint to generate vector embeddings.
- **`GET /v1/models`**: Lists the active embedding model alias.
- **`GET /health`**: Returns the health status of the embedding server.

### 3. Local-Rerank Service (Port `50086`)
- **`POST /v1/rerank`** (and **`POST /rerank`**): Cohere-compatible reranking endpoint. Accepts a `"query"` string, a `"documents"` array of strings, and an optional `"top_n"` limit, returning a list of documents sorted by their `"relevance_score"`.
- **`GET /v1/models`**: Lists the active reranking model alias.
- **`GET /health`**: Returns the health status of the reranking server.

---

## Configuration Files

Each service stores its configuration in the systemd user configuration directory:

- **Local-Chat**: 
  - Service: `~/.config/systemd/user/local-chat.service`
  - Environment: `~/.config/systemd/user/local-chat.env`
- **local-embeddings**:
  - Service: `~/.config/systemd/user/local-embeddings.service`
  - Environment: `~/.config/systemd/user/local-embeddings.env`
- **Local-Rerank**:
  - Service: `~/.config/systemd/user/local-rerank.service`
  - Environment: `~/.config/systemd/user/local-rerank.env`

### GPU and CPU Inference

By default, all three services run on the GPU using ROCm/HIP offloading.
To change a service to run on CPU, run `./local-<service>.sh edit` (or edit its `.env` file) and uncomment the CPU parameters:

```bash
# For CPU execution, uncomment these variables:
# LC_N_GPU_LAYERS=0
# LC_EXTRA_ARGS=""
```

---

## Verification & Test Results

You can test that the services are running and behaving correctly by executing the validation test suite:

```bash
./local-inference.sh test
```

This runs the individual test suites for chat, embedding, and reranking sequentially.

### 1. Chat Completion Test (Port 50080)
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

### 2. Text Embedding Test (Port 50085)
- **Endpoint**: `http://localhost:50085/v1/embeddings`
- **Command**:
  ```bash
  curl -s -X POST http://localhost:50085/v1/embeddings \
    -H "Content-Type: application/json" \
    -d '{
      "model": "qwen3-embedding",
      "input": "Hello World"
    }'
  ```

### 3. Document Reranking Test (Port 50086)
- **Endpoint**: `http://localhost:50086/v1/rerank`
- **Command**:
  ```bash
  curl -s -X POST http://localhost:50086/v1/rerank \
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
