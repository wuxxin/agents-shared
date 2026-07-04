# Combined Local Inference Router Service Guide

`local-router.sh` manages the local combined services router systemd user service (`local-router.service`), running a FastAPI web application served by `uvicorn` on port `51080`. It aggregates all underlying local inference services into a single OpenAI-compatible entrypoint.

- **Source Code**: [scripts/local-router.py](file:///home/wuxxin/agent-shared/code/agents-shared/scripts/local-router.py)
- **Control Wrapper**: [assistants/local-router.sh](file:///home/wuxxin/agent-shared/code/agents-shared/assistants/local-router.sh)

## Usage

```bash
# Install the service and environment configuration
./local-router.sh install [--no-start] [--new-config]

# Start/Stop/Restart the service
./local-router.sh start
./local-router.sh stop
./local-router.sh restart

# Check runtime status
./local-router.sh status

# Tail service stdout/stderr logs
./local-router.sh logs -f

# Edit service environment configuration and auto-restart
./local-router.sh edit

# Run API validation tests
./local-router.sh test

# Run uvicorn as a transient systemd user service
./local-router.sh exec [--env KEY=VALUE]* [-- uvicorn-args...]
```

## Configuration & Routing Details

The service is configured in:
- `~/.config/systemd/user/local-router.env`

Default configuration values:
```env
LROUT_PORT=51080
LROUT_HOST=127.0.0.1
LROUT_EXTRA_ARGS=""
```

### Route Map (Port 51080)

| Endpoint | Target URL | Service Name | Default Port | Description |
|---|---|---|---|---|
| `POST /v1/chat/completions` | `http://{LCHAT_HOST}:{LCHAT_PORT}` | Local-Chat | 50080 | LLM completions |
| `POST /v1/embeddings` | Dynamic (based on `LMBD_ENABLED`) | Local-Embedding | 50082 / 50080 | Embeddings |
| `POST /v1/rerank` or `/rerank` | `http://{LRR_HOST}:{LRR_PORT}` | Local-Rerank | 50086 | Text document ranking |
| `POST /v1/audio/transcriptions` | `http://{LSTT_HOST}:{LSTT_PORT}` | Local-Speech-To-Text | 50090 | Whisper transcription |
| `POST /v1/audio/speech` | `http://{LTTS_HOST}:{LTTS_PORT}` | Local-Text-To-Speech | 50095 | Speech synthesis |
| `POST /v1/images/generations` | `http://{LIMG_HOST}:{LIMG_PORT}` | Local-Image | 50100 | Stable Diffusion image generation |
| `GET /v1/models` | Combined Merged Models Endpoint | All Active Backends | - | Merges active models list |

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
