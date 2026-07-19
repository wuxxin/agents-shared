#!/usr/bin/env python3
# scripts/local-router.py - Combined Local Inference Router (OpenAI Proxy)
#
# Listens on port 51080 and routes incoming requests dynamically to
# local chat, embedding, rerank, speech-to-text, text-to-speech, and image services.

import os
import re
import socket
import asyncio
from contextlib import asynccontextmanager
from typing import Any
import httpx
from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse, JSONResponse


# Global client for connection pooling
client: httpx.AsyncClient = None  # type: ignore[assignment]

# Global model inventory
model_inventory_list: list[dict] = []
model_to_service: dict[str, str] = {}

PRICING_REGISTRY: dict[str, dict[str, str]] = {
    "chat": {
        "prompt": "0.0000015",  # $1.50 per 1M tokens (similar to Gemini 3.5 Flash)
        "completion": "0.0000090",  # $9.00 per 1M tokens (similar to Gemini 3.5 Flash)
        "input_cache_read": "0.00000015",  # $0.15 per 1M tokens
        "input_cache_write": "0.0000015",  # $1.50 per 1M tokens
    },
    "embedding": {
        "prompt": "0.00000015",  # $0.15 per 1M tokens (Gemini Embedding 001)
        "completion": "0.00000000",
        "input_cache_read": "0.00000000",
        "input_cache_write": "0.00000000",
    },
    "rerank": {
        "prompt": "0.00000015",  # $0.15 per 1M tokens (reasonable equivalent to embedding)
        "completion": "0.00000000",
        "input_cache_read": "0.00000000",
        "input_cache_write": "0.00000000",
    },
    "image": {
        "prompt": "0.00000050",  # $0.50 per 1M tokens (Gemini 3.1 Flash Image)
        "completion": "0.00006000",  # $60.00 per 1M tokens (images, $0.067 per 1K image)
        "input_cache_read": "0.00000000",
        "input_cache_write": "0.00000000",
    },
    "tts": {
        "prompt": "0.00000100",  # $1.00 per 1M tokens (Gemini 3.1 Flash TTS text input)
        "completion": "0.00002000",  # $20.00 per 1M tokens (Gemini 3.1 Flash TTS audio output)
        "input_cache_read": "0.00000000",
        "input_cache_write": "0.00000000",
    },
    "stt": {
        "prompt": "0.00000000",
        "completion": "0.00003000",  # OpenAI Whisper ($0.006/min; ~200 tokens/min => $0.00003/token)
        "input_cache_read": "0.00000000",
        "input_cache_write": "0.00000000",
    },
}


def resolve_service_alias(name: str) -> str:
    """Resolve the alias for a service by checking its own env file, falling back to defaults."""
    user_dir = get_systemd_user_dir()
    if name == "chat":
        chat_env = parse_env_file(os.path.join(user_dir, "local-chat.env"))
        return chat_env.get("LCHAT_ALIAS", "qwen3")
    elif name == "embedding":
        embed_env = parse_env_file(os.path.join(user_dir, "local-embedding.env"))
        return embed_env.get("LMBD_ALIAS", "qwen3-embedding")
    elif name == "rerank":
        rerank_env = parse_env_file(os.path.join(user_dir, "local-rerank.env"))
        return rerank_env.get("LRR_ALIAS", "qwen3-reranker")
    elif name == "stt":
        stt_env = parse_env_file(os.path.join(user_dir, "local-speech-to-text.env"))
        return stt_env.get("LSTT_ALIAS", "whisper-1")
    elif name == "tts":
        tts_env = parse_env_file(os.path.join(user_dir, "local-text-to-speech.env"))
        return tts_env.get("LTTS_ALIAS", "qwen3-tts")
    elif name == "image":
        image_env = parse_env_file(os.path.join(user_dir, "local-image.env"))
        return image_env.get("LIMG_ALIAS", "z-image-turbo")
    return ""


def resolve_service_from_model_id(model_id: str, default_svc: str) -> str:
    """Resolve the proper service name for a given model ID to apply correct pricing and mapping."""
    model_lower = model_id.lower()
    if "embedding" in model_lower:
        return "embedding"
    elif "reranker" in model_lower or "rerank" in model_lower:
        return "rerank"
    elif "tts" in model_lower:
        return "tts"
    elif "whisper" in model_lower or "stt" in model_lower:
        return "stt"
    elif "image" in model_lower:
        return "image"
    return default_svc


def get_enabled_services() -> dict[str, bool]:
    """Parse local-inference.env to determine which services are enabled."""
    user_dir = get_systemd_user_dir()
    coord_env = parse_env_file(os.path.join(user_dir, "local-inference.env"))

    def is_enabled(key: str, default: bool) -> bool:
        val = coord_env.get(key)
        if val is None:
            return default
        return val not in ("0", "false", "no", "FALSE", "NO")

    return {
        "chat": is_enabled("LCHAT_ENABLED", True),
        "embedding": is_enabled("LMBD_ENABLED", False),  # 0 (combined mode) by default
        "rerank": is_enabled("LRR_ENABLED", True),
        "stt": is_enabled("LSTT_ENABLED", True),
        "tts": is_enabled("LTTS_ENABLED", True),
        "image": is_enabled("LIMG_ENABLED", True),
    }


async def check_service(name: str, url: str) -> list[dict] | None:
    """Check if a service is available.

    Returns a list of models if available, or None if not available.
    """
    match = re.search(r"//([^/:]+)(?::(\d+))?", url)
    if not match:
        return None
    host = match.group(1)
    port = int(match.group(2)) if match.group(2) else 80

    if name in ("chat", "embedding", "rerank"):
        try:
            # We query the HTTP endpoint with a short timeout
            resp = await client.get(f"{url}/v1/models", timeout=1.0)
            if resp.status_code == 200:
                data = resp.json().get("data", [])
                return data
        except Exception:
            pass
        return None
    else:
        # For STT, TTS, Image: check if port is open
        try:
            reader, writer = await asyncio.open_connection(host, port)
            writer.close()
            await writer.wait_closed()
            return []
        except Exception:
            return None


async def build_inventory_and_wait():
    global model_inventory_list, model_to_service
    import sys

    enabled_services = get_enabled_services()
    print(f"Startup synchronization: checking enabled services: {enabled_services}")

    start_time = asyncio.get_event_loop().time()
    timeout = 60.0
    poll_interval = 2.0

    while True:
        config = resolve_config()
        pending_services = []

        for name, enabled in enabled_services.items():
            if not enabled:
                continue
            # If standalone embedding is disabled, it runs inside chat, so we don't check it separately
            if name == "embedding" and not enabled_services["embedding"]:
                continue
            pending_services.append((name, config[name]))

        # Poll all in parallel
        poll_tasks = [check_service(name, url) for name, url in pending_services]
        poll_res = await asyncio.gather(*poll_tasks)

        all_available = True
        iteration_results = {}
        for (name, url), res in zip(pending_services, poll_res):
            if res is None:
                all_available = False
                break
            iteration_results[name] = res

        if all_available:
            print("All enabled inference services are online and ready!")
            new_inventory_list = []
            new_model_to_service = {}

            def add_model(
                model_id: str,
                svc_name: str,
                existing_pricing: dict[str, Any] | None = None,
            ):
                if not model_id:
                    return
                # Resolve the true service name for the model based on its ID
                true_svc = resolve_service_from_model_id(model_id, svc_name)

                # Determine pricing
                pricing = existing_pricing
                if not pricing:
                    pricing = PRICING_REGISTRY.get(true_svc)

                # Check for duplicates
                existing_entry = None
                for m in new_inventory_list:
                    if m["id"] == model_id:
                        existing_entry = m
                        break

                if existing_entry is not None:
                    if pricing:
                        existing_entry["pricing"] = pricing
                else:
                    model_entry: dict[str, Any] = {
                        "id": model_id,
                        "object": "model",
                        "owned_by": "local-inference",
                    }
                    if pricing:
                        model_entry["pricing"] = pricing
                    new_inventory_list.append(model_entry)
                new_model_to_service[model_id] = true_svc

            # Add dynamically returned models from llama-server backends
            for name, models in iteration_results.items():
                for model_data in models:
                    m_id = model_data.get("id")
                    if m_id:
                        add_model(m_id, name, model_data.get("pricing"))

            # Add configured aliases for all active/fallback services
            for name in ["chat", "embedding", "rerank", "stt", "tts", "image"]:
                # Embedding is active if either standalone is enabled or if chat is enabled
                is_active = (
                    enabled_services["embedding"]
                    if name == "embedding"
                    else enabled_services[name]
                )
                if not is_active and name == "embedding" and enabled_services["chat"]:
                    is_active = True

                if is_active:
                    alias = resolve_service_alias(name)
                    if alias:
                        add_model(alias, name)
                        if alias == "qwen3":
                            add_model("qwen3-thinking", name)

            model_inventory_list = new_inventory_list
            model_to_service = new_model_to_service
            print(f"Model inventory successfully built: {model_inventory_list}")
            return

        elapsed = asyncio.get_event_loop().time() - start_time
        if elapsed >= timeout:
            failed = [
                f"{name} ({url})"
                for (name, url), res in zip(pending_services, poll_res)
                if res is None
            ]
            print(
                f"CRITICAL: Timeout waiting for inference services to start. "
                f"Missing services: {', '.join(failed)}. Aborting.",
                file=sys.stderr,
            )
            sys.exit(1)

        print(f"Waiting for services to become available... ({int(elapsed)}s elapsed)")
        await asyncio.sleep(poll_interval)


def resolve_target_service(model_name: str) -> str:
    """Resolve the target service name ('chat', 'embedding', etc.) based on the requested model name."""
    if not model_name:
        # Load default model from local-router.env if set
        user_dir = get_systemd_user_dir()
        router_env = parse_env_file(os.path.join(user_dir, "local-router.env"))
        default_model = router_env.get("LROUT_DEFAULT_MODEL", "")
        if default_model and default_model in model_to_service:
            return model_to_service[default_model]
        return "chat"

    # Exact match in inventory
    if model_name in model_to_service:
        return model_to_service[model_name]

    # Fallback substring matching rules
    if "embedding" in model_name.lower():
        return "embedding"
    elif "rerank" in model_name.lower():
        return "rerank"
    return "chat"


@asynccontextmanager
async def lifespan(app: FastAPI):
    global client
    # Set long timeouts for inference queries (e.g. 10m for long generations/transcriptions)
    client = httpx.AsyncClient(timeout=600.0)
    # Build model inventory and wait for all services to become available
    await build_inventory_and_wait()
    yield
    await client.aclose()


app = FastAPI(
    title="Local Inference Combined Router",
    description="Combined gateway mimicking OpenAI-compatible endpoints for local LLM, TTS, STT, and Image backends.",
    version="1.0.0",
    lifespan=lifespan,
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
    def load_addr(
        svc: str, prefix: str, default_host: str, default_port: int
    ) -> tuple[str, int]:
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
        embed_host, embed_port = load_addr(
            "local-embedding", "LMBD", "127.0.0.1", 50082
        )
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


async def proxy_request(
    target_url: str, request: Request, content: bytes = None
) -> Response:
    """Asynchronously streams request to target and forwards the response back."""
    body = content if content is not None else await request.body()
    headers = {
        k: v
        for k, v in request.headers.items()
        if k.lower() not in ("host", "content-length")
    }

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
        resp_headers = {
            k: v
            for k, v in response.headers.items()
            if k.lower() not in ("transfer-encoding", "content-length")
        }

        return StreamingResponse(
            response_generator(),
            status_code=response.status_code,
            headers=resp_headers,
            media_type=response.headers.get("content-type"),
        )

    except httpx.HTTPStatusError as exc:
        return JSONResponse(
            status_code=exc.response.status_code,
            content={
                "error": {
                    "message": f"Backend error: {str(exc)}",
                    "type": "backend_error",
                }
            },
        )
    except (httpx.ConnectError, httpx.ConnectTimeout) as exc:
        # Gracefully handle backend downtime
        return JSONResponse(
            status_code=502,
            content={
                "error": {
                    "message": f"Local service backend ({target_url}) is currently offline or unreachable. {str(exc)}",
                    "type": "gateway_error",
                    "code": 502,
                }
            },
        )
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "message": f"Internal proxy routing error: {str(exc)}",
                    "type": "proxy_error",
                }
            },
        )


# --- Routes Mapping ---


@app.post("/v1/chat/completions")
async def route_chat(request: Request):
    config = resolve_config()
    body = await request.body()
    try:
        import json

        data = json.loads(body)
        if data.get("model") == "qwen3-thinking":
            data["model"] = "qwen3"
            kwargs = data.get("chat_template_kwargs") or {}
            kwargs["enable_thinking"] = True
            data["chat_template_kwargs"] = kwargs
            body = json.dumps(data).encode("utf-8")
    except Exception:
        pass
    return await proxy_request(
        f"{config['chat']}/v1/chat/completions", request, content=body
    )


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


@app.post("/v1/completions")
@app.post("/completion")
async def route_completions(request: Request):
    """Routes completions / completion requests to the chat service."""
    config = resolve_config()
    path = request.url.path
    return await proxy_request(f"{config['chat']}{path}", request)


@app.post("/embedding")
async def route_native_embedding(request: Request):
    """Routes native llama.cpp /embedding requests to the embedding service."""
    config = resolve_config()
    return await proxy_request(f"{config['embedding']}/embedding", request)


@app.get("/props")
@app.get("/v1/props")
async def route_props(request: Request):
    """Routes properties query to the chat service as default fallback."""
    config = resolve_config()
    path = request.url.path
    return await proxy_request(f"{config['chat']}{path}", request)


@app.post("/tokenize")
@app.post("/v1/tokenize")
async def route_tokenize(request: Request):
    """Routes tokenization requests to the matching model service backend."""
    try:
        body = await request.json()
        model_name = body.get("model", "")
    except Exception:
        model_name = ""

    config = resolve_config()
    target_svc = resolve_target_service(model_name)
    target_url = config.get(target_svc, config["chat"])

    path = request.url.path
    return await proxy_request(f"{target_url}{path}", request)


@app.post("/detokenize")
@app.post("/v1/detokenize")
async def route_detokenize(request: Request):
    """Routes detokenization requests to the matching model service backend."""
    try:
        body = await request.json()
        model_name = body.get("model", "")
    except Exception:
        model_name = ""

    config = resolve_config()
    target_svc = resolve_target_service(model_name)
    target_url = config.get(target_svc, config["chat"])

    path = request.url.path
    return await proxy_request(f"{target_url}{path}", request)


@app.get("/health")
@app.get("/healthz")
async def route_health():
    """Aggregates router status and connection health checks to registered backends."""
    config = resolve_config()
    res = {"status": "ok", "backends": {}}

    for key, url in config.items():
        match = re.search(r":(\d+)", url)
        if match:
            port = int(match.group(1))
            try:
                with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                    res["backends"][key] = "online"
            except Exception:
                res["backends"][key] = "offline"
        else:
            res["backends"][key] = "unknown"
    return res


@app.get("/v1/models")
async def route_models():
    """Returns the cached model inventory built on startup."""
    return {"object": "list", "data": model_inventory_list}


@app.api_route(
    "/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"]
)
async def route_catchall(path: str, request: Request):
    """Graceful handler for unmapped routes."""
    return JSONResponse(
        status_code=404,
        content={
            "error": {
                "message": f"Combined endpoint proxy path '/{path}' not found.",
                "type": "invalid_request_error",
                "code": 404,
            }
        },
    )
