#!/usr/bin/env python3
# scripts/local-router.py - Combined Local Inference Router (OpenAI Proxy)
#
# Listens on port 51080 and routes incoming requests dynamically to
# local chat, embedding, rerank, speech-to-text, text-to-speech, and image services.

import os
import re
import asyncio
from contextlib import asynccontextmanager
import httpx
from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse, JSONResponse

# Global client for connection pooling
client: httpx.AsyncClient = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global client
    # Set long timeouts for inference queries (e.g. 10m for long generations/transcriptions)
    client = httpx.AsyncClient(timeout=600.0)
    yield
    await client.close()

app = FastAPI(
    title="Local Inference Combined Router",
    description="Combined gateway mimicking OpenAI-compatible endpoints for local LLM, TTS, STT, and Image backends.",
    version="1.0.0",
    lifespan=lifespan
)

def get_systemd_user_dir() -> str:
    """Resolve the systemd user configuration directory."""
    xdg_config = os.environ.get("XDG_CONFIG_HOME")
    if xdg_config:
        return os.path.join(xdg_config, "systemd", "user")
    return os.path.join(os.path.expanduser("~"), ".config", "systemd", "user")

def parse_env_file(filepath: str) -> dict:
    """Parse key-value environment variables from a bash environment file."""
    if not os.path.exists(filepath):
        return {}
    
    env_vars = {}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                # Match KEY=VALUE or export KEY=VALUE
                match = re.match(r"^(?:export\s+)?([A-Za-z0-9_]+)=(.*)$", line)
                if match:
                    key = match.group(1)
                    val = match.group(2).strip()
                    # Strip inline comments if value is not fully quoted
                    if not (val.startswith('"') or val.startswith("'")):
                        val = val.split("#")[0].strip()
                    else:
                        val = val[1:-1]
                    env_vars[key] = val
    except Exception as exc:
        print(f"Warning: Failed to parse env file {filepath}: {exc}")
        
    return env_vars

def resolve_config() -> dict:
    """Read the latest environment configurations to resolve routing destinations."""
    user_dir = get_systemd_user_dir()
    
    # 1. Read the wrapper settings to see if standalone embedding is enabled
    coord_env = parse_env_file(os.path.join(user_dir, "local-inference.env"))
    lmbd_enabled_str = coord_env.get("LMBD_ENABLED", "1")
    lmbd_enabled = lmbd_enabled_str not in ("0", "false", "no", "FALSE", "NO")

    # Helper to resolve service hosts & ports
    def load_addr(svc: str, prefix: str, default_host: str, default_port: int) -> tuple[str, int]:
        env_path = os.path.join(user_dir, f"{svc}.env")
        env_data = parse_env_file(env_path)
        host = env_data.get(f"{prefix}_HOST", default_host)
        port_str = env_data.get(f"{prefix}_PORT", str(default_port))
        try:
            port = int(port_str)
        except ValueError:
            port = default_port
        return host, port

    chat_host, chat_port = load_addr("local-chat", "LCHAT", "127.0.0.1", 50080)
    
    # Embedding destination depends on whether the dedicated embedding service is active
    if lmbd_enabled:
        embed_host, embed_port = load_addr("local-embedding", "LMBD", "127.0.0.1", 50082)
    else:
        # Combined mode: routes embedding directly to local-chat port
        embed_host, embed_port = chat_host, chat_port

    rerank_host, rerank_port = load_addr("local-rerank", "LRR", "127.0.0.1", 50086)
    stt_host, stt_port = load_addr("local-speech-to-text", "LSTT", "127.0.0.1", 50090)
    tts_host, tts_port = load_addr("local-text-to-speech", "LTTS", "127.0.0.1", 50095)
    image_host, image_port = load_addr("local-image", "LIMG", "127.0.0.1", 50100)

    return {
        "chat": f"http://{chat_host}:{chat_port}",
        "embedding": f"http://{embed_host}:{embed_port}",
        "rerank": f"http://{rerank_host}:{rerank_port}",
        "stt": f"http://{stt_host}:{stt_port}",
        "tts": f"http://{tts_host}:{tts_port}",
        "image": f"http://{image_host}:{image_port}",
    }

async def proxy_request(target_url: str, request: Request) -> Response:
    """Asynchronously streams request to target and forwards the response back."""
    body = await request.body()
    headers = {k: v for k, v in request.headers.items() if k.lower() not in ("host", "content-length")}
    
    try:
        # Build and send the streaming request
        req = client.build_request(
            method=request.method,
            url=target_url,
            headers=headers,
            content=body,
            params=request.query_params,
        )
        
        response = await client.send(req, stream=True)
        
        async def response_generator():
            try:
                async for chunk in response.aiter_bytes():
                    yield chunk
            finally:
                await response.aclose()

        # Strip content-length and transfer-encoding headers to let FastAPI handle chunking correctly
        resp_headers = {k: v for k, v in response.headers.items() if k.lower() not in ("transfer-encoding", "content-length")}
        
        return StreamingResponse(
            response_generator(),
            status_code=response.status_code,
            headers=resp_headers,
            media_type=response.headers.get("content-type")
        )
        
    except httpx.HTTPStatusError as exc:
        return JSONResponse(
            status_code=exc.response.status_code,
            content={"error": {"message": f"Backend error: {str(exc)}", "type": "backend_error"}}
        )
    except (httpx.ConnectError, httpx.ConnectTimeout) as exc:
        # Gracefully handle backend downtime
        return JSONResponse(
            status_code=502,
            content={
                "error": {
                    "message": f"Local service backend ({target_url}) is currently offline or unreachable. {str(exc)}",
                    "type": "gateway_error",
                    "code": 502
                }
            }
        )
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={"error": {"message": f"Internal proxy routing error: {str(exc)}", "type": "proxy_error"}}
        )

# --- Routes Mapping ---

@app.post("/v1/chat/completions")
async def route_chat(request: Request):
    config = resolve_config()
    return await proxy_request(f"{config['chat']}/v1/chat/completions", request)

@app.post("/v1/embeddings")
async def route_embedding(request: Request):
    config = resolve_config()
    return await proxy_request(f"{config['embedding']}/v1/embeddings", request)

@app.post("/v1/rerank")
@app.post("/rerank")
async def route_rerank(request: Request):
    config = resolve_config()
    return await proxy_request(f"{config['rerank']}/v1/rerank", request)

@app.post("/v1/audio/transcriptions")
async def route_stt(request: Request):
    config = resolve_config()
    # Resolve optional custom endpoint path for stt if defined in env
    user_dir = get_systemd_user_dir()
    stt_env = parse_env_file(os.path.join(user_dir, "local-speech-to-text.env"))
    inf_path = stt_env.get("LSTT_INFERENCE_PATH", "/v1/audio/transcriptions")
    return await proxy_request(f"{config['stt']}{inf_path}", request)

@app.post("/v1/audio/speech")
async def route_tts(request: Request):
    config = resolve_config()
    return await proxy_request(f"{config['tts']}/v1/audio/speech", request)

@app.post("/v1/images/generations")
async def route_image(request: Request):
    config = resolve_config()
    return await proxy_request(f"{config['image']}/v1/images/generations", request)

@app.get("/v1/models")
async def route_models():
    """Aggregates active backend models in parallel, falling back to config presets if offline."""
    config = resolve_config()
    user_dir = get_systemd_user_dir()

    # Define targets to query
    targets = [
        ("chat", config["chat"]),
        ("embedding", config["embedding"]),
        ("rerank", config["rerank"]),
        ("stt", config["stt"]),
        ("tts", config["tts"]),
        ("image", config["image"]),
    ]

    # De-duplicate queries to the same backend host
    unique_queries = {}
    for name, url in targets:
        unique_queries[url] = unique_queries.get(url, []) + [name]

    async def fetch_backend_models(url: str, svc_names: list[str]) -> list:
        try:
            # Query backend directly with a short timeout
            resp = await client.get(f"{url}/v1/models", timeout=1.5)
            if resp.status_code == 200:
                return resp.json().get("data", [])
        except Exception:
            pass

        # Fallback to loading configured alias names from local environment configurations
        fallbacks = []
        for name in svc_names:
            if name == "chat":
                chat_env = parse_env_file(os.path.join(user_dir, "local-chat.env"))
                alias = chat_env.get("LCHAT_ALIAS", "qwen3")
                fallbacks.append({"id": alias, "object": "model", "owned_by": "local-inference"})
            elif name == "embedding":
                embed_env = parse_env_file(os.path.join(user_dir, "local-embedding.env"))
                alias = embed_env.get("LMBD_ALIAS", "qwen3-embedding")
                fallbacks.append({"id": alias, "object": "model", "owned_by": "local-inference"})
            elif name == "rerank":
                rerank_env = parse_env_file(os.path.join(user_dir, "local-rerank.env"))
                alias = rerank_env.get("LRR_ALIAS", "qwen3-reranker")
                fallbacks.append({"id": alias, "object": "model", "owned_by": "local-inference"})
            elif name == "stt":
                fallbacks.append({"id": "whisper-1", "object": "model", "owned_by": "local-inference"})
            elif name == "tts":
                fallbacks.append({"id": "qwen3-tts", "object": "model", "owned_by": "local-inference"})
            elif name == "image":
                fallbacks.append({"id": "z-image-turbo", "object": "model", "owned_by": "local-inference"})
        return fallbacks

    tasks = [fetch_backend_models(url, svcs) for url, svcs in unique_queries.items()]
    results = await asyncio.gather(*tasks)

    # Merge results, preserving unique model IDs
    merged_data = []
    seen_ids = set()
    for res in results:
        for model in res:
            m_id = model.get("id")
            if m_id and m_id not in seen_ids:
                seen_ids.add(m_id)
                merged_data.append(model)

    return {"object": "list", "data": merged_data}

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"])
async def route_catchall(path: str, request: Request):
    """Graceful handler for unmapped routes."""
    return JSONResponse(
        status_code=404,
        content={"error": {"message": f"Combined endpoint proxy path '/{path}' not found.", "type": "invalid_request_error", "code": 404}}
    )
