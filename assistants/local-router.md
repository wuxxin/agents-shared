# Combined Local Inference Router Service Guide

`local-router.sh` manages the local combined services router systemd user service (`local-router.service`), running a FastAPI web application served by `uvicorn` on port `51080`. It aggregates all underlying local inference services into a single OpenAI-compatible entrypoint.

On installation, the Python code is copied from `scripts/local-router.py` to the systemd user directory (`~/.config/systemd/user/local-router.py`), and is served directly from there.

- **Source Code Repository Path**: [scripts/local-router.py](file:///home/wuxxin/agent-shared/code/agents-shared/scripts/local-router.py)
- **Control Wrapper**: [assistants/local-router.sh](file:///home/wuxxin/agent-shared/code/agents-shared/assistants/local-router.sh)

## Usage

- Install the service and environment configuration:
  - `./local-router.sh install [--no-start] [--new-config]`
- Start/Stop/Restart the service:
  - `./local-router.sh start`
  - `./local-router.sh stop`
  - `./local-router.sh restart`
- Check runtime status:
  - `./local-router.sh status`
- Tail service stdout/stderr logs:
  - `./local-router.sh logs -f`
- Edit service environment configuration and auto-restart:
  - `./local-router.sh edit`
- Run API validation tests:
  - `./local-router.sh test`
- Run uvicorn as a transient systemd user service:
  - `./local-router.sh exec [--env KEY=VALUE]* [-- uvicorn-args...]`

## Configuration & Routing Details

The service is configured in:
- `~/.config/systemd/user/local-router.env`

Default configuration values:
```env
LROUT_PORT=51080
LROUT_HOST=127.0.0.1
LROUT_EXTRA_ARGS=""
LROUT_DEFAULT_MODEL="qwen3"
```

### Route Map (Port 51080)

| Endpoint | Target URL | Service | Model |  Port | Description |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `POST /v1/chat/completions` | `http://{LCHAT_HOST}:{LCHAT_PORT}` | Local-Chat | qwen3 | 50080 | LLM completions |
| `POST /v1/embeddings` | Dynamic (based on `LMBD_ENABLED`) | Local-Embedding | qwen3-embedding | 50082 / 50080 | Embeddings |
| `POST /v1/rerank` or `/rerank` | `http://{LRR_HOST}:{LRR_PORT}` | Local-Rerank | qwen3-reranker | 50086 | Text document ranking |
| `POST /v1/audio/transcriptions` | `http://{LSTT_HOST}:{LSTT_PORT}` | Local-Speech-To-Text | whisper-1 | 50090 | Whisper transcription |
| `POST /v1/audio/speech` | `http://{LTTS_HOST}:{LTTS_PORT}` | Local-Text-To-Speech | qwen3-tts | 50095 | Speech synthesis |
| `POST /v1/images/generations` | `http://{LIMG_HOST}:{LIMG_PORT}` | Local-Image | z-image-turbo | 50100 | Stable Diffusion image generation |
| `GET /v1/models` | Cached Model Inventory | - | - | - | Returns cached model inventory built on startup |


### Startup Synchronization & Model Inventory

On startup, the router parses `~/.config/systemd/user/local-inference.env` to identify which sub-services are enabled. It then polls all enabled services:
- For backends supporting models (`chat`, `embedding` if standalone, `rerank`), it queries their `/v1/models` HTTP endpoint.
- For backends not exposing a models endpoint (`stt`, `tts`, `image`), it checks if their TCP port is open.

The router polls every 2 seconds for up to **1 minute**.
- If all enabled services become available, it constructs a global model inventory mapping model IDs and configured aliases to their respective services, then begins serving requests.
- If not all services are online within 1 minute, the router prints an error to standard error and aborts startup with exit code `1`.

### Default Model Routing

When clients request tokenization (`/tokenize` or `/detokenize`) without specifying a `model` parameter in the request body, the router checks if `LROUT_DEFAULT_MODEL` is configured in `local-router.env` and maps to an active service in the inventory.
- If found, the request is routed to the corresponding service (e.g. `embedding` if `LROUT_DEFAULT_MODEL="qwen3-embedding"`).
- Otherwise, it falls back to routing to the `chat` service on port `50080`.

### Dynamic Embedding Routing

The router inspects `~/.config/systemd/user/local-inference.env`:
- If `LMBD_ENABLED=1` (standard setup): `/v1/embeddings` is routed to the dedicated `local-embedding` service on port `50082`.
- If `LMBD_ENABLED=0` (combined embeddings mode): `/v1/embeddings` is routed to `local-chat` on port `50080`.

### Error Propagation

If any backend service is down, offline, or returns an error, the router responds gracefully with a JSON object in the standard OpenAI error format:
```json
{
  "error": {
    "message": "Local service backend (http://127.0.0.1:50080) is currently offline or unreachable. [Errno 111] Connection refused",
    "type": "gateway_error",
    "code": 502
  }
}
```
This ensures integration clients (like agents or tools) receive clean HTTP errors (`502 Bad Gateway` / `503 Service Unavailable`) instead of failing with connection breaks.
