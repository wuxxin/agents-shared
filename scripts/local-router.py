#!/usr/bin/env python3
# scripts/local-router.py - Combined Local Inference Router (OpenAI Proxy)
#
# Listens on port 51080 and routes incoming requests dynamically to
# local chat, embedding, rerank, speech-to-text, text-to-speech, and image services.

import os
import re
import socket
import asyncio
import json
import datetime
import threading
import atexit
import signal
import sys
from contextlib import asynccontextmanager
from typing import Any, Mapping
import httpx
from fastapi import FastAPI, Request, Response
from fastapi.responses import (
    StreamingResponse,
    JSONResponse,
    PlainTextResponse,
    HTMLResponse,
)
import tiktoken
from prometheus_client import (
    CollectorRegistry,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST,
)


# Global client for connection pooling
client: httpx.AsyncClient = None  # type: ignore[assignment]

# Global model inventory
model_inventory_list: list[dict] = []
model_to_service: dict[str, str] = {}

# Check for mock backends mode
LROUT_MOCK_BACKENDS = os.environ.get("LROUT_MOCK_BACKENDS", "") in (
    "1",
    "true",
    "TRUE",
    "yes",
)

# --- Client Identification Headers ---

CLIENT_IDENTIFICATION_HEADERS: tuple[str, ...] = (
    "x-client-id",
    "x-agent-id",
    "x-client",
    "x-agent",
)


def sanitize_client_identifier(raw: str | None) -> str | None:
    """Sanitize raw client identifier by stripping quotes, whitespace, and special characters."""
    if not raw:
        return None
    val = raw.strip().strip("'\"").strip()
    if not val:
        return None
    clean = re.sub(r"[^\w\.-]", "", val).strip().lower()
    return clean if clean else None


def resolve_client_id(custom_identifier: str | None = None) -> str:
    """Resolve client identifier strictly from custom HTTP header or body parameter."""
    clean_custom = sanitize_client_identifier(custom_identifier)
    return clean_custom if clean_custom else "unknown"


# --- Usage tracking state ---
STATIC_ERRORS_TEMPLATE = {
    "400": 0,
    "401": 0,
    "403": 0,
    "404": 0,
    "408": 0,
    "429": 0,
    "500": 0,
    "502": 0,
    "503": 0,
    "504": 0,
    "OTHER": 0,
}

usage_data_memory: dict[str, dict[str, dict[str, dict[str, dict[str, Any]]]]] = {}
last_written_total_tokens: int = 0
usage_lock = threading.Lock()
save_task: asyncio.Task = None  # type: ignore[assignment]

# --- Prometheus setup ---
metrics_registry = CollectorRegistry()

calls_gauge = Gauge(
    "local_router_calls_total",
    "Cumulative count of calls routed through local-router",
    ["agent", "service", "model"],
    registry=metrics_registry,
)

tokens_gauge = Gauge(
    "local_router_tokens_total",
    "Cumulative count of tokens processed",
    ["agent", "service", "model", "type"],
    registry=metrics_registry,
)

cost_gauge = Gauge(
    "local_router_cost_total",
    "Cumulative estimated cost of routed calls in USD",
    ["agent", "service", "model", "type"],
    registry=metrics_registry,
)

errors_gauge = Gauge(
    "local_router_errors_total",
    "Cumulative count of HTTP errors routed by service, model, call type, and HTTP code",
    ["agent", "service", "model", "call_type", "code"],
    registry=metrics_registry,
)

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

    if LROUT_MOCK_BACKENDS:
        print("Starting in MOCK BACKENDS mode...")
        model_inventory_list = [
            {
                "id": "qwen3",
                "object": "model",
                "owned_by": "local-inference",
                "pricing": PRICING_REGISTRY["chat"],
            },
            {
                "id": "qwen3-thinking",
                "object": "model",
                "owned_by": "local-inference",
                "pricing": PRICING_REGISTRY["chat"],
            },
            {
                "id": "qwen3-embedding",
                "object": "model",
                "owned_by": "local-inference",
                "pricing": PRICING_REGISTRY["embedding"],
            },
            {
                "id": "qwen3-reranker",
                "object": "model",
                "owned_by": "local-inference",
                "pricing": PRICING_REGISTRY["rerank"],
            },
            {
                "id": "whisper-1",
                "object": "model",
                "owned_by": "local-inference",
                "pricing": PRICING_REGISTRY["stt"],
            },
            {
                "id": "qwen3-tts",
                "object": "model",
                "owned_by": "local-inference",
                "pricing": PRICING_REGISTRY["tts"],
            },
            {
                "id": "z-image-turbo",
                "object": "model",
                "owned_by": "local-inference",
                "pricing": PRICING_REGISTRY["image"],
            },
        ]
        model_to_service = {
            "qwen3": "chat",
            "qwen3-thinking": "chat",
            "qwen3-embedding": "embedding",
            "qwen3-reranker": "rerank",
            "whisper-1": "stt",
            "qwen3-tts": "tts",
            "z-image-turbo": "image",
        }
        return

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


# --- Usage Tracking helper functions ---


def get_token_count(text: str) -> int:
    """Helper to count tokens in a string using tiktoken (cl100k_base)."""
    if not text:
        return 0
    try:
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
    except Exception:
        return len(text.split())


def add_usage_record(
    agent: str,
    service: str,
    model: str,
    uncached_input: int,
    cached_input: int,
    cached_write: int,
    output: int,
    is_streaming: bool,
    status_code: int = 200,
):
    agent = agent or "unknown"
    service = service or "unknown"
    model = model or "unknown"
    today = datetime.date.today().isoformat()
    with usage_lock:
        if today not in usage_data_memory:
            usage_data_memory[today] = {}
        if agent not in usage_data_memory[today]:
            usage_data_memory[today][agent] = {}
        if service not in usage_data_memory[today][agent]:
            usage_data_memory[today][agent][service] = {}
        if model not in usage_data_memory[today][agent][service]:
            usage_data_memory[today][agent][service][model] = {
                "calls": 0,
                "streaming_calls": 0,
                "calls_post": 0,
                "input": 0,
                "cached_input": 0,
                "cached_write": 0,
                "output": 0,
                "errors_streaming": dict(STATIC_ERRORS_TEMPLATE),
                "errors_post": dict(STATIC_ERRORS_TEMPLATE),
            }

        entry = usage_data_memory[today][agent][service][model]

        # Backward compatibility check for loaded data:
        if "calls_post" not in entry:
            entry["calls_post"] = entry.pop("normal_calls", 0)
        if "errors_streaming" not in entry:
            entry["errors_streaming"] = dict(STATIC_ERRORS_TEMPLATE)
        if "errors_post" not in entry:
            entry["errors_post"] = dict(STATIC_ERRORS_TEMPLATE)

        entry["calls"] += 1
        if is_streaming:
            entry["streaming_calls"] += 1
        else:
            entry["calls_post"] += 1

        entry["input"] += uncached_input
        entry["cached_input"] += cached_input
        entry["cached_write"] += cached_write
        entry["output"] += output

        if status_code >= 400:
            code_str = str(status_code)
            error_dict = (
                entry["errors_streaming"] if is_streaming else entry["errors_post"]
            )
            if code_str in error_dict:
                error_dict[code_str] += 1
            else:
                error_dict["OTHER"] += 1


def get_usage_file_path() -> str:
    user_dir = get_systemd_user_dir()
    return os.path.join(user_dir, "local-router-usage.json")


def load_usage_data():
    global usage_data_memory, last_written_total_tokens
    path = get_usage_file_path()
    usage_data_memory = {}
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data_list = json.load(f)
                if isinstance(data_list, list):
                    for entry in data_list:
                        date = entry.get("date")
                        if date:
                            raw_usage = entry.get("usage", {})
                            migrated_day_data: dict[str, dict[str, dict[str, Any]]] = {}
                            for top_key, subdict in raw_usage.items():
                                if not isinstance(subdict, dict):
                                    continue
                                sample_val = (
                                    next(iter(subdict.values()), {}) if subdict else {}
                                )
                                if isinstance(sample_val, dict) and (
                                    "calls" in sample_val or "input" in sample_val
                                ):
                                    if "unknown" not in migrated_day_data:
                                        migrated_day_data["unknown"] = {}
                                    migrated_day_data["unknown"][top_key] = subdict
                                else:
                                    migrated_day_data[top_key] = subdict
                            usage_data_memory[date] = migrated_day_data
        except Exception as e:
            print(f"Warning: Failed to load usage file {path}: {e}")

    today = datetime.date.today().isoformat()
    last_written_total_tokens = get_total_tokens_for_day(today)


def get_total_tokens_for_day(day: str) -> int:
    total = 0
    if day in usage_data_memory:
        for _agent, services_map in usage_data_memory[day].items():
            if not isinstance(services_map, dict):
                continue
            for _service, models_map in services_map.items():
                if not isinstance(models_map, dict):
                    continue
                for _model, counts in models_map.items():
                    if isinstance(counts, dict):
                        total += counts.get("input", 0)
                        total += counts.get("cached_input", 0)
                        total += counts.get("cached_write", 0)
                        total += counts.get("output", 0)
    return total


def check_and_save_usage(force=False):
    global last_written_total_tokens
    today = datetime.date.today().isoformat()
    current_tokens = get_total_tokens_for_day(today)

    if force or current_tokens != last_written_total_tokens:
        path = get_usage_file_path()
        data_list = []
        with usage_lock:
            for date, usage in usage_data_memory.items():
                data_list.append({"date": date, "usage": usage})

        try:
            temp_path = path + ".tmp"
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data_list, f, indent=2)
            os.replace(temp_path, path)
            last_written_total_tokens = current_tokens
        except Exception as e:
            print(f"Error saving usage to {path}: {e}")


async def periodic_save_task():
    while True:
        await asyncio.sleep(600)  # 10 minutes
        try:
            check_and_save_usage()
        except Exception as e:
            print(f"Error in periodic save: {e}")


def get_cumulative_metrics(
    day_filter: str | None = None, range_filter: str | None = None
) -> dict[str, Any]:
    models_acc: dict[str, dict[str, Any]] = {}
    agents_acc: dict[str, dict[str, Any]] = {}
    services_acc: dict[str, dict[str, Any]] = {}
    daily_acc: dict[str, dict[str, Any]] = {}
    totals_acc: dict[str, Any] = {
        "calls": 0,
        "streaming_calls": 0,
        "calls_post": 0,
        "input": 0,
        "cached_input": 0,
        "cached_write": 0,
        "output": 0,
        "total_tokens": 0,
        "cache_pct": 0.0,
        "costs": {
            "cached_input_cost": 0.0,
            "input_cost": 0.0,
            "cached_write_cost": 0.0,
            "output_cost": 0.0,
            "total_cost": 0.0,
        },
        "errors_streaming": dict(STATIC_ERRORS_TEMPLATE),
        "errors_post": dict(STATIC_ERRORS_TEMPLATE),
    }

    today = datetime.date.today()
    days_to_process = []

    with usage_lock:
        if day_filter:
            days_to_process = [day_filter]
        elif range_filter:
            if range_filter == "today" or range_filter == "1d":
                days_to_process = [today.isoformat()]
            elif range_filter == "7d":
                days_to_process = [
                    (today - datetime.timedelta(days=i)).isoformat() for i in range(7)
                ]
            elif range_filter == "30d":
                days_to_process = [
                    (today - datetime.timedelta(days=i)).isoformat() for i in range(30)
                ]
            elif range_filter == "90d":
                days_to_process = [
                    (today - datetime.timedelta(days=i)).isoformat() for i in range(90)
                ]
            else:
                days_to_process = list(usage_data_memory.keys())
        else:
            days_to_process = list(usage_data_memory.keys())

        for day in sorted(days_to_process):
            day_data = usage_data_memory.get(day, {})
            if day not in daily_acc:
                daily_acc[day] = {
                    "calls": 0,
                    "streaming_calls": 0,
                    "calls_post": 0,
                    "input": 0,
                    "cached_input": 0,
                    "cached_write": 0,
                    "output": 0,
                    "total_tokens": 0,
                    "total_cost": 0.0,
                    "errors_streaming": 0,
                    "errors_post": 0,
                }
            for agent, services_map in day_data.items():
                if not isinstance(services_map, dict):
                    continue
                if agent not in agents_acc:
                    agents_acc[agent] = {
                        "calls": 0,
                        "streaming_calls": 0,
                        "calls_post": 0,
                        "input": 0,
                        "cached_input": 0,
                        "cached_write": 0,
                        "output": 0,
                        "total_tokens": 0,
                        "cache_pct": 0.0,
                        "costs": {
                            "cached_input_cost": 0.0,
                            "input_cost": 0.0,
                            "cached_write_cost": 0.0,
                            "output_cost": 0.0,
                            "total_cost": 0.0,
                        },
                        "errors_streaming": dict(STATIC_ERRORS_TEMPLATE),
                        "errors_post": dict(STATIC_ERRORS_TEMPLATE),
                    }

                for service, models_map in services_map.items():
                    if not isinstance(models_map, dict):
                        continue
                    if service not in services_acc:
                        services_acc[service] = {
                            "calls": 0,
                            "streaming_calls": 0,
                            "calls_post": 0,
                            "input": 0,
                            "cached_input": 0,
                            "cached_write": 0,
                            "output": 0,
                            "total_tokens": 0,
                            "cache_pct": 0.0,
                            "costs": {
                                "cached_input_cost": 0.0,
                                "input_cost": 0.0,
                                "cached_write_cost": 0.0,
                                "output_cost": 0.0,
                                "total_cost": 0.0,
                            },
                            "errors_streaming": dict(STATIC_ERRORS_TEMPLATE),
                            "errors_post": dict(STATIC_ERRORS_TEMPLATE),
                        }

                    pricing = PRICING_REGISTRY.get(service, {})
                    cost_prompt = float(pricing.get("prompt", "0.0"))
                    cost_completion = float(pricing.get("completion", "0.0"))
                    cost_cache_read = float(pricing.get("input_cache_read", "0.0"))
                    cost_cache_write = float(pricing.get("input_cache_write", "0.0"))

                    for model, counts in models_map.items():
                        if not isinstance(counts, dict):
                            continue
                        model_key = f"{agent}:{model}:{service}"
                        if model_key not in models_acc:
                            models_acc[model_key] = {
                                "calls": 0,
                                "streaming_calls": 0,
                                "calls_post": 0,
                                "input": 0,
                                "cached_input": 0,
                                "cached_write": 0,
                                "output": 0,
                                "total_tokens": 0,
                                "cache_pct": 0.0,
                                "costs": {
                                    "cached_input_cost": 0.0,
                                    "input_cost": 0.0,
                                    "cached_write_cost": 0.0,
                                    "output_cost": 0.0,
                                    "total_cost": 0.0,
                                },
                                "errors_streaming": dict(STATIC_ERRORS_TEMPLATE),
                                "errors_post": dict(STATIC_ERRORS_TEMPLATE),
                            }

                        calls = counts.get("calls", 0)
                        str_calls = counts.get("streaming_calls", 0)
                        norm_calls = counts.get(
                            "calls_post", counts.get("normal_calls", 0)
                        )
                        if str_calls == 0 and norm_calls == 0 and calls > 0:
                            norm_calls = calls

                        inp = counts.get("input", 0)
                        c_inp = counts.get("cached_input", 0)
                        c_wr = counts.get("cached_write", 0)
                        out = counts.get("output", 0)
                        tot = inp + c_inp + c_wr + out

                        c_inp_cost = c_inp * cost_cache_read
                        inp_cost = inp * cost_prompt
                        c_wr_cost = c_wr * cost_cache_write
                        out_cost = out * cost_completion
                        tot_cost = c_inp_cost + inp_cost + c_wr_cost + out_cost

                        def accum(target: dict[str, Any]):
                            target["calls"] += calls
                            target["streaming_calls"] += str_calls
                            target["calls_post"] += norm_calls
                            target["input"] += inp
                            target["cached_input"] += c_inp
                            target["cached_write"] += c_wr
                            target["output"] += out
                            target["total_tokens"] += tot
                            target["costs"]["cached_input_cost"] += c_inp_cost
                            target["costs"]["input_cost"] += inp_cost
                            target["costs"]["cached_write_cost"] += c_wr_cost
                            target["costs"]["output_cost"] += out_cost
                            target["costs"]["total_cost"] += tot_cost
                            for code in STATIC_ERRORS_TEMPLATE:
                                err_str_val = counts.get("errors_streaming", {}).get(
                                    code, 0
                                )
                                err_post_val = counts.get("errors_post", {}).get(
                                    code, 0
                                )
                                target["errors_streaming"][code] += err_str_val
                                target["errors_post"][code] += err_post_val

                        accum(models_acc[model_key])
                        accum(agents_acc[agent])
                        accum(services_acc[service])
                        accum(totals_acc)

                        daily_target = daily_acc[day]
                        daily_target["calls"] += calls
                        daily_target["streaming_calls"] += str_calls
                        daily_target["calls_post"] += norm_calls
                        daily_target["input"] += inp
                        daily_target["cached_input"] += c_inp
                        daily_target["cached_write"] += c_wr
                        daily_target["output"] += out
                        daily_target["total_tokens"] += tot
                        daily_target["total_cost"] += tot_cost
                        for code in STATIC_ERRORS_TEMPLATE:
                            daily_target["errors_streaming"] += counts.get(
                                "errors_streaming", {}
                            ).get(code, 0)
                            daily_target["errors_post"] += counts.get(
                                "errors_post", {}
                            ).get(code, 0)

    for entry in models_acc.values():
        total_inp = entry["cached_input"] + entry["input"]
        entry["cache_pct"] = (
            (entry["cached_input"] / total_inp * 100.0) if total_inp > 0 else 0.0
        )

    for entry in agents_acc.values():
        total_inp = entry["cached_input"] + entry["input"]
        entry["cache_pct"] = (
            (entry["cached_input"] / total_inp * 100.0) if total_inp > 0 else 0.0
        )

    for entry in services_acc.values():
        total_inp = entry["cached_input"] + entry["input"]
        entry["cache_pct"] = (
            (entry["cached_input"] / total_inp * 100.0) if total_inp > 0 else 0.0
        )

    total_inp = totals_acc["cached_input"] + totals_acc["input"]
    totals_acc["cache_pct"] = (
        (totals_acc["cached_input"] / total_inp * 100.0) if total_inp > 0 else 0.0
    )

    return {
        "models": models_acc,
        "agents": agents_acc,
        "services": services_acc,
        "totals": totals_acc,
        "daily": daily_acc,
    }


def update_prometheus_metrics():
    metrics = get_cumulative_metrics()
    for key, val in metrics["models"].items():
        agent, model, service = key.split(":", 2)
        calls_gauge.labels(agent=agent, service=service, model=model).set(val["calls"])

        tokens_gauge.labels(
            agent=agent, service=service, model=model, type="input"
        ).set(val["input"])
        tokens_gauge.labels(
            agent=agent, service=service, model=model, type="cached_input"
        ).set(val["cached_input"])
        tokens_gauge.labels(
            agent=agent, service=service, model=model, type="cached_write"
        ).set(val["cached_write"])
        tokens_gauge.labels(
            agent=agent, service=service, model=model, type="output"
        ).set(val["output"])
        tokens_gauge.labels(
            agent=agent, service=service, model=model, type="total"
        ).set(val["total_tokens"])

        cost_gauge.labels(agent=agent, service=service, model=model, type="input").set(
            val["costs"]["input_cost"]
        )
        cost_gauge.labels(
            agent=agent, service=service, model=model, type="cached_input"
        ).set(val["costs"]["cached_input_cost"])
        cost_gauge.labels(
            agent=agent, service=service, model=model, type="cached_write"
        ).set(val["costs"]["cached_write_cost"])
        cost_gauge.labels(agent=agent, service=service, model=model, type="output").set(
            val["costs"]["output_cost"]
        )
        cost_gauge.labels(agent=agent, service=service, model=model, type="total").set(
            val["costs"]["total_cost"]
        )

        # Update errors
        for code in STATIC_ERRORS_TEMPLATE:
            errors_gauge.labels(
                agent=agent,
                service=service,
                model=model,
                call_type="streaming",
                code=code,
            ).set(val["errors_streaming"].get(code, 0))
            errors_gauge.labels(
                agent=agent, service=service, model=model, call_type="post", code=code
            ).set(val["errors_post"].get(code, 0))


def format_usage_table(data: dict[str, Any]) -> str:
    models = data.get("models", {})
    agents = data.get("agents", {})
    services = data.get("services", {})
    totals = data.get("totals", {})

    lines = []
    width = 153
    lines.append("-" * width)
    lines.append(
        f"| {'AGENT:MODEL:SERVICE':<30} | {'CALLS':<6} | {'STREAM':<6} | {'POST':<6} | {'INPUT':<10} | {'CACHED IN':<10} | {'CACHED WR':<10} | {'OUTPUT':<10} | {'CACHE %':<8} | {'EST COST':<9} | {'ERRORS (STR / POST)':<18} |"
    )
    lines.append("-" * width)

    def get_errors_str(stats: dict[str, Any]) -> str:
        str_errs = sum(stats.get("errors_streaming", {}).values())
        post_errs = sum(stats.get("errors_post", {}).values())
        return f"{str_errs} / {post_errs}"

    for model_key, stats in sorted(models.items()):
        cost = stats.get("costs", {}).get("total_cost", 0.0)
        errs_str = get_errors_str(stats)
        lines.append(
            f"| {model_key:<30} | {stats.get('calls', 0):<6} | {stats.get('streaming_calls', 0):<6} | {stats.get('calls_post', 0):<6} | {stats.get('input', 0):<10} | {stats.get('cached_input', 0):<10} | {stats.get('cached_write', 0):<10} | {stats.get('output', 0):<10} | {stats.get('cache_pct', 0.0):<8.2f} | ${cost:<8.4f} | {errs_str:<18} |"
        )

    lines.append("-" * width)

    for agent_name, stats in sorted(agents.items()):
        cost = stats.get("costs", {}).get("total_cost", 0.0)
        errs_str = get_errors_str(stats)
        lines.append(
            f"| {f'Agent {agent_name.upper()} Total':<30} | {stats.get('calls', 0):<6} | {stats.get('streaming_calls', 0):<6} | {stats.get('calls_post', 0):<6} | {stats.get('input', 0):<10} | {stats.get('cached_input', 0):<10} | {stats.get('cached_write', 0):<10} | {stats.get('output', 0):<10} | {stats.get('cache_pct', 0.0):<8.2f} | ${cost:<8.4f} | {errs_str:<18} |"
        )

    lines.append("-" * width)

    for svc_name, stats in sorted(services.items()):
        cost = stats.get("costs", {}).get("total_cost", 0.0)
        errs_str = get_errors_str(stats)
        lines.append(
            f"| {f'Service {svc_name.upper()} Total':<30} | {stats.get('calls', 0):<6} | {stats.get('streaming_calls', 0):<6} | {stats.get('calls_post', 0):<6} | {stats.get('input', 0):<10} | {stats.get('cached_input', 0):<10} | {stats.get('cached_write', 0):<10} | {stats.get('output', 0):<10} | {stats.get('cache_pct', 0.0):<8.2f} | ${cost:<8.4f} | {errs_str:<18} |"
        )

    lines.append("-" * width)
    total_cost = totals.get("costs", {}).get("total_cost", 0.0)
    total_errs_str = get_errors_str(totals)
    lines.append(
        f"| {'GRAND TOTAL':<30} | {totals.get('calls', 0):<6} | {totals.get('streaming_calls', 0):<6} | {totals.get('calls_post', 0):<6} | {totals.get('input', 0):<10} | {totals.get('cached_input', 0):<10} | {totals.get('cached_write', 0):<10} | {totals.get('output', 0):<10} | {totals.get('cache_pct', 0.0):<8.2f} | ${total_cost:<8.4f} | {total_errs_str:<18} |"
    )
    lines.append("-" * width)

    has_errors = False
    for name, stats in (
        [("GRAND TOTAL", totals)]
        + list(sorted((f"Agent {k.upper()}", v) for k, v in agents.items()))
        + list(sorted(models.items()))
    ):
        str_err_codes = {
            k: v for k, v in stats.get("errors_streaming", {}).items() if v > 0
        }
        post_err_codes = {
            k: v for k, v in stats.get("errors_post", {}).items() if v > 0
        }
        if str_err_codes or post_err_codes:
            if not has_errors:
                lines.append("\nHTTP Errors Breakdown:")
                has_errors = True
            lines.append(f"  {name}:")
            if str_err_codes:
                lines.append(
                    "    Streaming errors: "
                    + ", ".join(f"{k}:{v}" for k, v in sorted(str_err_codes.items()))
                )
            if post_err_codes:
                lines.append(
                    "    Post errors:      "
                    + ", ".join(f"{k}:{v}" for k, v in sorted(post_err_codes.items()))
                )

    return "\n".join(lines) + "\n"


def save_on_exit():
    check_and_save_usage(force=True)


# Register exit handlers
atexit.register(save_on_exit)


def handle_exit_signal(signum, frame):
    save_on_exit()
    sys.exit(0)


# Register signals (ignore errors if in non-main threads or during testing)
try:
    signal.signal(signal.SIGTERM, handle_exit_signal)
    signal.signal(signal.SIGINT, handle_exit_signal)
except Exception:
    pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    global client, save_task
    # Load usage
    load_usage_data()
    # Set long timeouts for inference queries (e.g. 10m for long generations/transcriptions)
    client = httpx.AsyncClient(timeout=600.0)
    # Build model inventory and wait for all services to become available
    await build_inventory_and_wait()
    # Start periodic save task
    save_task = asyncio.create_task(periodic_save_task())
    yield
    # Cleanup
    save_task.cancel()
    try:
        await save_task
    except asyncio.CancelledError:
        pass
    save_on_exit()
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


async def handle_mock_backend(
    service: str, model: str, request: Request, request_content: bytes
) -> Response:
    is_streaming = False
    if request_content:
        try:
            req_json = json.loads(request_content)
            is_streaming = req_json.get("stream", False)
        except Exception:
            pass

    service = service or "chat"
    model = model or "qwen3"

    if "error-" in model:
        try:
            code = int(model.split("error-")[-1])
            if is_streaming:

                async def err_sse_gen():
                    yield f'data: {{"error": {{"message": "Mocked {code}", "code": {code}}}}}\n\n'.encode(
                        "utf-8"
                    )
                    yield b"data: [DONE]\n\n"

                return StreamingResponse(
                    err_sse_gen(), status_code=code, media_type="text/event-stream"
                )
            return JSONResponse({"error": f"Mocked {code}"}, status_code=code)
        except Exception:
            pass

    if service == "chat":
        if is_streaming:

            async def sse_gen():
                yield b'data: {"choices": [{"delta": {"content": "Mock"}, "index": 0}]}\n\n'
                await asyncio.sleep(0.01)
                yield b'data: {"choices": [{"delta": {"content": " response"}, "index": 0}]}\n\n'
                await asyncio.sleep(0.01)
                usage_data = {
                    "choices": [],
                    "usage": {
                        "prompt_tokens": 100,
                        "completion_tokens": 50,
                        "prompt_tokens_details": {"cached_tokens": 20},
                    },
                }
                yield f"data: {json.dumps(usage_data)}\n\n".encode("utf-8")
                yield b"data: [DONE]\n\n"

            return StreamingResponse(sse_gen(), media_type="text/event-stream")
        else:
            return JSONResponse(
                {
                    "choices": [
                        {"message": {"role": "assistant", "content": "Mock response"}}
                    ],
                    "usage": {
                        "prompt_tokens": 100,
                        "completion_tokens": 50,
                        "prompt_tokens_details": {"cached_tokens": 20},
                    },
                }
            )
    elif service == "embedding":
        return JSONResponse(
            {
                "data": [{"embedding": [0.1] * 128, "index": 0}],
                "usage": {"prompt_tokens": 10, "total_tokens": 10},
            }
        )
    elif service == "rerank":
        return JSONResponse(
            {
                "results": [
                    {"index": 0, "relevance_score": 0.95},
                    {"index": 1, "relevance_score": 0.12},
                ],
                "usage": {"prompt_tokens": 15, "total_tokens": 15},
            }
        )
    elif service == "tts":
        return Response(content=b"MOCK_AUDIO_DATA_MP3_BYTES", media_type="audio/mpeg")
    elif service == "stt":
        return JSONResponse({"text": "Mock transcribed text."})
    elif service == "image":
        return JSONResponse(
            {"data": [{"url": "http://127.0.0.1:51080/mock_image.png"}]}
        )

    return JSONResponse({"error": "Unsupported mock service"}, status_code=400)


async def process_response_usage(
    agent: str,
    service: str,
    model: str,
    is_sse: bool,
    response_body: bytes,
    request_body: bytes | None,
    is_streaming: bool,
    status_code: int = 200,
):
    estimated_input_tokens = 0
    request_prompt = ""
    if request_body:
        try:
            req_data = json.loads(request_body)
            if "messages" in req_data:
                request_prompt = "\n".join(
                    [
                        m.get("content", "")
                        for m in req_data["messages"]
                        if isinstance(m, dict)
                    ]
                )
            elif "prompt" in req_data:
                if isinstance(req_data["prompt"], list):
                    request_prompt = "\n".join(req_data["prompt"])
                else:
                    request_prompt = str(req_data["prompt"])
            elif "input" in req_data:
                if isinstance(req_data["input"], list):
                    request_prompt = "\n".join(req_data["input"])
                else:
                    request_prompt = str(req_data["input"])
            elif "query" in req_data:
                request_prompt = str(req_data["query"])
                if "documents" in req_data:
                    request_prompt += "\n" + "\n".join(req_data["documents"])
            estimated_input_tokens = get_token_count(request_prompt)
        except Exception:
            pass

    prompt_tokens = 0
    completion_tokens = 0
    cached_input = 0
    cached_write = 0

    if is_sse:
        lines = response_body.decode("utf-8", errors="ignore").split("\n")
        generated_text = ""
        found_usage = False
        for line in lines:
            line = line.strip()
            if line.startswith("data:"):
                data_str = line[5:].strip()
                if data_str == "[DONE]":
                    continue
                try:
                    data_json = json.loads(data_str)
                    usage = data_json.get("usage")
                    if usage:
                        prompt_tokens = usage.get("prompt_tokens", 0)
                        completion_tokens = usage.get("completion_tokens", 0)
                        details = usage.get("prompt_tokens_details", {})
                        cached_input = details.get("cached_tokens", 0) or usage.get(
                            "cache_read_input_tokens", 0
                        )
                        cached_write = details.get(
                            "cache_creation_input_tokens", 0
                        ) or usage.get("cache_creation_input_tokens", 0)
                        found_usage = True

                    choices = data_json.get("choices", [])
                    if choices:
                        delta = choices[0].get("delta", {})
                        if "content" in delta:
                            generated_text += delta["content"]
                except Exception:
                    pass
        if not found_usage:
            prompt_tokens = estimated_input_tokens
            completion_tokens = get_token_count(generated_text)
    else:
        try:
            resp_data = json.loads(response_body)
            usage = resp_data.get("usage")
            if usage:
                prompt_tokens = usage.get("prompt_tokens", 0)
                completion_tokens = usage.get("completion_tokens", 0)
                details = usage.get("prompt_tokens_details", {})
                cached_input = details.get("cached_tokens", 0) or usage.get(
                    "cache_read_input_tokens", 0
                )
                cached_write = details.get(
                    "cache_creation_input_tokens", 0
                ) or usage.get("cache_creation_input_tokens", 0)
            else:
                if service == "embedding":
                    prompt_tokens = estimated_input_tokens
                    completion_tokens = 0
                elif service == "rerank":
                    prompt_tokens = estimated_input_tokens
                    completion_tokens = 0
                elif service == "tts":
                    prompt_tokens = estimated_input_tokens
                    words = len(request_prompt.split())
                    duration = words / 2.5
                    completion_tokens = int(duration * 283)
                elif service == "stt":
                    prompt_tokens = 0
                    transcribed = resp_data.get("text", "")
                    completion_tokens = get_token_count(transcribed)
                elif service == "image":
                    prompt_tokens = estimated_input_tokens
                    n = 1
                    try:
                        if request_body:
                            n = int(json.loads(request_body).get("n", 1))
                    except Exception:
                        pass
                    completion_tokens = n * 1117
                else:
                    prompt_tokens = estimated_input_tokens
                    completion_tokens = 0
        except Exception:
            prompt_tokens = estimated_input_tokens
            completion_tokens = 0

    uncached_input = max(0, prompt_tokens - cached_input)

    add_usage_record(
        agent=agent or "unknown",
        service=service or "unknown",
        model=model or "unknown",
        uncached_input=uncached_input,
        cached_input=cached_input,
        cached_write=cached_write,
        output=completion_tokens,
        is_streaming=is_streaming,
        status_code=status_code,
    )


async def proxy_request(
    target_url: str,
    request: Request,
    content: bytes | None = None,
    service: str | None = None,
    model: str | None = None,
    agent: str | None = None,
) -> Response:
    """Asynchronously streams request to target and forwards the response back."""
    body = content if content is not None else await request.body()

    if LROUT_MOCK_BACKENDS:
        mock_resp = await handle_mock_backend(service or "", model or "", request, body)
        is_sse = (
            isinstance(mock_resp, StreamingResponse)
            and mock_resp.media_type == "text/event-stream"
        )
        is_streaming = False
        if body:
            try:
                is_streaming = json.loads(body).get("stream", False)
            except Exception:
                pass

        if isinstance(mock_resp, JSONResponse):
            resp_body = (
                mock_resp.body
                if isinstance(mock_resp.body, bytes)
                else bytes(mock_resp.body)
            )
            await process_response_usage(
                agent or "unknown",
                service or "",
                model or "",
                is_sse,
                resp_body,
                body,
                is_streaming,
                status_code=mock_resp.status_code,
            )
        elif isinstance(mock_resp, Response) and not isinstance(
            mock_resp, StreamingResponse
        ):
            resp_body = (
                mock_resp.body
                if isinstance(mock_resp.body, bytes)
                else bytes(mock_resp.body)
            )
            await process_response_usage(
                agent or "unknown",
                service or "",
                model or "",
                is_sse,
                resp_body,
                body,
                is_streaming,
                status_code=mock_resp.status_code,
            )
        elif isinstance(mock_resp, StreamingResponse):
            original_chunks = []

            async def mock_generator():
                async for chunk in mock_resp.body_iterator:
                    yield chunk
                    original_chunks.append(chunk)
                try:
                    full_body = b"".join(original_chunks)
                    await process_response_usage(
                        agent or "unknown",
                        service or "",
                        model or "",
                        is_sse,
                        full_body,
                        body,
                        is_streaming,
                        status_code=mock_resp.status_code,
                    )
                except Exception as e:
                    print(f"Error processing mock usage: {e}")

            return StreamingResponse(
                mock_generator(),
                status_code=mock_resp.status_code,
                headers=dict(mock_resp.headers),
                media_type=mock_resp.media_type,
            )
        return mock_resp

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

        is_sse = response.headers.get("content-type", "").startswith(
            "text/event-stream"
        )
        is_streaming = False
        if body:
            try:
                is_streaming = json.loads(body).get("stream", False)
            except Exception:
                pass

        async def response_generator():
            body_accumulator = []
            try:
                async for chunk in response.aiter_bytes():
                    yield chunk
                    body_accumulator.append(chunk)
            finally:
                await response.aclose()
                try:
                    full_body = b"".join(body_accumulator)
                    await process_response_usage(
                        agent or "unknown",
                        service or "",
                        model or "",
                        is_sse,
                        full_body,
                        body,
                        is_streaming,
                        status_code=response.status_code,
                    )
                except Exception as e:
                    print(f"Error processing usage: {e}")

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
        try:
            await process_response_usage(
                agent=agent or "unknown",
                service=service or "",
                model=model or "",
                is_sse=False,
                response_body=b"",
                request_body=body,
                is_streaming=is_streaming,
                status_code=exc.response.status_code,
            )
        except Exception:
            pass
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
        try:
            await process_response_usage(
                agent=agent or "unknown",
                service=service or "",
                model=model or "",
                is_sse=False,
                response_body=b"",
                request_body=body,
                is_streaming=is_streaming,
                status_code=502,
            )
        except Exception:
            pass
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
        try:
            await process_response_usage(
                agent=agent or "unknown",
                service=service or "",
                model=model or "",
                is_sse=False,
                response_body=b"",
                request_body=body,
                is_streaming=is_streaming,
                status_code=500,
            )
        except Exception:
            pass
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "message": f"Internal proxy routing error: {str(exc)}",
                    "type": "proxy_error",
                }
            },
        )


# --- Usage & Metrics Routes ---


@app.get("/usage")
@app.get("/v1/usage")
async def route_usage(
    day: str | None = None, range: str | None = None, format: str = "json"
):
    try:
        metrics = get_cumulative_metrics(day_filter=day, range_filter=range)
        if format == "text":
            return PlainTextResponse(format_usage_table(metrics))
        return metrics
    except Exception as e:
        if format == "text":
            return PlainTextResponse(f"Error: {e}", status_code=500)
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/metrics")
@app.get("/v1/metrics")
async def route_metrics():
    try:
        update_prometheus_metrics()
        return Response(
            content=generate_latest(metrics_registry), media_type=CONTENT_TYPE_LATEST
        )
    except Exception as e:
        return Response(
            content=f"Error generating metrics: {e}",
            status_code=500,
            media_type="text/plain",
        )


@app.get("/routing/ui", response_class=HTMLResponse)
@app.get("/ui", response_class=HTMLResponse)
async def route_ui():
    ui_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "local-router-ui.html"
    )
    if not os.path.exists(ui_path):
        return HTMLResponse(
            "<h1>Error: local-router-ui.html not found</h1>", status_code=404
        )
    with open(ui_path, "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content)


# --- Routes Mapping ---


def extract_request_agent(
    request: Request, body_data: Mapping[str, Any] | None = None
) -> str:
    """Extract and normalize client identifier strictly from request HTTP headers or JSON body payload."""
    custom: str | None = None
    for header_name in CLIENT_IDENTIFICATION_HEADERS:
        val = request.headers.get(header_name)
        if val:
            custom = val
            break

    if not custom and isinstance(body_data, Mapping):
        c_val = (
            body_data.get("client_id")
            or body_data.get("agent_id")
            or body_data.get("client")
            or body_data.get("agent")
        )
        if isinstance(c_val, str):
            custom = c_val
        elif isinstance(body_data.get("extra_body"), Mapping):
            eb = body_data["extra_body"]
            eb_val = (
                eb.get("client_id")
                or eb.get("agent_id")
                or eb.get("client")
                or eb.get("agent")
            )
            if isinstance(eb_val, str):
                custom = eb_val

    agent = resolve_client_id(custom)
    if agent == "unknown":
        client_host = request.client.host if request.client else "unknown"
        path = request.url.path
        method = request.method
        ua = request.headers.get("user-agent", "")
        print(
            f"[UNMAPPED CLIENT] Path: {method} {path} | User-Agent: '{ua or '<missing>'}' | Custom Identifier: '{custom or '<none>'}' | IP: {client_host}",
            file=sys.stderr,
        )
    return agent


@app.post("/v1/chat/completions")
async def route_chat(request: Request):
    config = resolve_config()
    body = await request.body()
    data: dict[str, Any] | None = None
    model = "qwen3"
    try:
        data = json.loads(body)
        model = data.get("model", "qwen3")
        if model == "qwen3-thinking":
            data["model"] = "qwen3"
            kwargs = data.get("chat_template_kwargs") or {}
            kwargs["enable_thinking"] = True
            data["chat_template_kwargs"] = kwargs
            body = json.dumps(data).encode("utf-8")
    except Exception:
        pass
    agent = extract_request_agent(request, data)
    return await proxy_request(
        f"{config['chat']}/v1/chat/completions",
        request,
        content=body,
        service="chat",
        model=model,
        agent=agent,
    )


@app.post("/v1/embeddings")
async def route_embedding(request: Request):
    config = resolve_config()
    model = "qwen3-embedding"
    body = None
    data: dict[str, Any] | None = None
    try:
        body = await request.body()
        data = json.loads(body)
        model = data.get("model", "qwen3-embedding")
    except Exception:
        pass
    agent = extract_request_agent(request, data)
    return await proxy_request(
        f"{config['embedding']}/v1/embeddings",
        request,
        content=body,
        service="embedding",
        model=model,
        agent=agent,
    )


@app.post("/v1/rerank")
@app.post("/rerank")
async def route_rerank(request: Request):
    config = resolve_config()
    model = "qwen3-reranker"
    body = None
    data: dict[str, Any] | None = None
    try:
        body = await request.body()
        data = json.loads(body)
        model = data.get("model", "qwen3-reranker")
    except Exception:
        pass
    agent = extract_request_agent(request, data)
    return await proxy_request(
        f"{config['rerank']}/v1/rerank",
        request,
        content=body,
        service="rerank",
        model=model,
        agent=agent,
    )


@app.post("/v1/audio/transcriptions")
async def route_stt(request: Request):
    config = resolve_config()
    user_dir = get_systemd_user_dir()
    stt_env = parse_env_file(os.path.join(user_dir, "local-speech-to-text.env"))
    inf_path = stt_env.get("LSTT_INFERENCE_PATH", "/v1/audio/transcriptions")
    agent = extract_request_agent(request)
    model = "whisper-1"
    body_bytes = b""
    try:
        body_bytes = await request.body()
        form = await request.form()
        model_form = form.get("model")
        if isinstance(model_form, str):
            model = model_form
    except Exception:
        pass
    return await proxy_request(
        f"{config['stt']}{inf_path}",
        request,
        content=body_bytes,
        service="stt",
        model=model,
        agent=agent,
    )


@app.post("/v1/audio/speech")
async def route_tts(request: Request):
    config = resolve_config()
    model = "qwen3-tts"
    body = None
    data: dict[str, Any] | None = None
    try:
        body = await request.body()
        data = json.loads(body)
        model = data.get("model", "qwen3-tts")
    except Exception:
        pass
    agent = extract_request_agent(request, data)
    return await proxy_request(
        f"{config['tts']}/v1/audio/speech",
        request,
        content=body,
        service="tts",
        model=model,
        agent=agent,
    )


@app.post("/v1/images/generations")
async def route_image(request: Request):
    config = resolve_config()
    model = "z-image-turbo"
    body = None
    data: dict[str, Any] | None = None
    try:
        body = await request.body()
        data = json.loads(body)
        model = data.get("model", "z-image-turbo")
    except Exception:
        pass
    agent = extract_request_agent(request, data)
    return await proxy_request(
        f"{config['image']}/v1/images/generations",
        request,
        content=body,
        service="image",
        model=model,
        agent=agent,
    )


@app.post("/v1/completions")
@app.post("/completion")
async def route_completions(request: Request):
    """Routes completions / completion requests to the chat service."""
    config = resolve_config()
    path = request.url.path
    model = "qwen3"
    body = None
    data: dict[str, Any] | None = None
    try:
        body = await request.body()
        data = json.loads(body)
        model = data.get("model", "qwen3")
    except Exception:
        pass
    agent = extract_request_agent(request, data)
    return await proxy_request(
        f"{config['chat']}{path}",
        request,
        content=body,
        service="chat",
        model=model,
        agent=agent,
    )


@app.post("/embedding")
async def route_native_embedding(request: Request):
    """Routes native llama.cpp /embedding requests to the embedding service."""
    config = resolve_config()
    agent = extract_request_agent(request)
    body = None
    try:
        body = await request.body()
    except Exception:
        pass
    return await proxy_request(
        f"{config['embedding']}/embedding",
        request,
        content=body,
        service="embedding",
        model="qwen3-embedding",
        agent=agent,
    )


@app.get("/props")
@app.get("/v1/props")
async def route_props(request: Request):
    """Routes properties query to the chat service as default fallback."""
    config = resolve_config()
    agent = extract_request_agent(request)
    path = request.url.path
    return await proxy_request(f"{config['chat']}{path}", request, agent=agent)


@app.post("/tokenize")
@app.post("/v1/tokenize")
async def route_tokenize(request: Request):
    """Routes tokenization requests to the matching model service backend."""
    body_bytes = None
    model_name = ""
    agent = extract_request_agent(request)
    try:
        body_bytes = await request.body()
        body = json.loads(body_bytes)
        model_name = body.get("model", "")
    except Exception:
        pass

    config = resolve_config()
    target_svc = resolve_target_service(model_name)
    target_url = config.get(target_svc, config["chat"])

    path = request.url.path
    return await proxy_request(
        f"{target_url}{path}", request, content=body_bytes, agent=agent
    )


@app.post("/detokenize")
@app.post("/v1/detokenize")
async def route_detokenize(request: Request):
    """Routes detokenization requests to the matching model service backend."""
    body_bytes = None
    model_name = ""
    agent = extract_request_agent(request)
    try:
        body_bytes = await request.body()
        body = json.loads(body_bytes)
        model_name = body.get("model", "")
    except Exception:
        pass

    config = resolve_config()
    target_svc = resolve_target_service(model_name)
    target_url = config.get(target_svc, config["chat"])

    path = request.url.path
    return await proxy_request(
        f"{target_url}{path}", request, content=body_bytes, agent=agent
    )


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
