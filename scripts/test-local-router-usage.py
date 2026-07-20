#!/usr/bin/env python3
# scripts/test-local-router-usage.py - Test local router usage tracking and metrics

import os
import sys
import tempfile
import shutil
import json
import datetime
import importlib.util

# Override environment BEFORE importing local-router to isolate systemd directories
temp_config_dir = tempfile.mkdtemp()
os.environ["XDG_CONFIG_HOME"] = temp_config_dir
os.environ["LROUT_MOCK_BACKENDS"] = "1"

# Add current directory to python path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

# Import test client and router app
from fastapi.testclient import TestClient  # noqa: E402

# Load hyphenated module using importlib
spec = importlib.util.spec_from_file_location(
    "local_router", os.path.join(script_dir, "local-router.py")
)
assert spec is not None
local_router = importlib.util.module_from_spec(spec)
sys.modules["local_router"] = local_router
assert spec.loader is not None
spec.loader.exec_module(local_router)

from local_router import app, check_and_save_usage, get_usage_file_path  # type: ignore[import-not-found] # noqa: E402


def run_tests():
    print("=== Running Local Inference Router Usage Tests ===")

    # Initialize TestClient
    client = TestClient(app)

    # Wait for startup logic (lifespan) to run
    # Note: TestClient context manager triggers lifespan events
    with client:
        # 1. Verify models endpoint returns mock inventory
        print("Testing /v1/models endpoint...")
        resp = client.get("/v1/models")
        assert resp.status_code == 200, f"Status code: {resp.status_code}"
        models_data = resp.json().get("data", [])
        assert len(models_data) > 0, "Inventory is empty"
        print("Models endpoint: OK")

        # 2. Simulate Chat completion (normal call)
        print("Testing Chat completions (normal)...")
        payload = {
            "model": "qwen3",
            "messages": [{"role": "user", "content": "Tell me a joke."}],
            "stream": False,
        }
        resp = client.post("/v1/chat/completions", json=payload)
        assert resp.status_code == 200
        print("Chat normal: OK")

        # 3. Simulate Chat completion (streaming call)
        print("Testing Chat completions (streaming)...")
        payload["stream"] = True
        resp = client.post("/v1/chat/completions", json=payload)
        assert resp.status_code == 200
        # Iterate over stream chunks to trigger interception code
        for chunk in resp.iter_bytes():
            pass
        print("Chat streaming: OK")

        # 4. Simulate Embedding
        print("Testing Embeddings...")
        resp = client.post(
            "/v1/embeddings", json={"model": "qwen3-embedding", "input": "Hello world!"}
        )
        assert resp.status_code == 200
        print("Embeddings: OK")

        # 5. Simulate Rerank
        print("Testing Reranker...")
        resp = client.post(
            "/v1/rerank",
            json={
                "model": "qwen3-reranker",
                "query": "Is light fast?",
                "documents": ["Yes, light is fast.", "Water is wet."],
            },
        )
        assert resp.status_code == 200
        print("Reranker: OK")

        # 6. Simulate TTS
        print("Testing Text-to-Speech...")
        resp = client.post(
            "/v1/audio/speech",
            json={
                "model": "qwen3-tts",
                "input": "This is a test of synthesized voice narration.",
            },
        )
        assert resp.status_code == 200
        print("TTS: OK")

        # 7. Simulate STT
        print("Testing Speech-to-Text...")
        # Since it uses multipart/form-data, we upload a mock file
        files = {"file": ("test.wav", b"AUDIO_DATA_RAW", "audio/wav")}
        data = {"model": "whisper-1"}
        resp = client.post("/v1/audio/transcriptions", files=files, data=data)
        assert resp.status_code == 200
        print("STT: OK")

        # 8. Simulate Image generation
        print("Testing Image generation...")
        resp = client.post(
            "/v1/images/generations",
            json={
                "model": "z-image-turbo",
                "prompt": "A beautiful sunset over mountain peaks.",
                "n": 2,
            },
        )
        assert resp.status_code == 200
        print("Image generation: OK")

        # Give database background writes a small yield
        check_and_save_usage(force=True)

        # 9. Verify Usage API returns aggregated statistics
        print("Testing /usage endpoint...")
        resp = client.get("/usage")
        assert resp.status_code == 200
        usage_res = resp.json()

        # Validate totals block
        totals = usage_res.get("totals", {})
        assert totals.get("calls", 0) == 7, (
            f"Expected 7 calls, got {totals.get('calls')}"
        )
        assert totals.get("streaming_calls", 0) == 1, (
            f"Expected 1 streaming call, got {totals.get('streaming_calls')}"
        )
        assert totals.get("normal_calls", 0) == 6, (
            f"Expected 6 normal calls, got {totals.get('normal_calls')}"
        )

        # Chat costs/tokens check
        chat_model_key = "chat:qwen3"
        chat_stats = usage_res.get("models", {}).get(chat_model_key, {})
        assert chat_stats.get("calls", 0) == 2
        # Mock responses return prompt=100, completion=50, cached=20
        # Uncached input = 100 - 20 = 80 per call. Total input for 2 calls = 160.
        # Cached input = 20 * 2 = 40. Output = 50 * 2 = 100.
        assert chat_stats.get("input") == 160
        assert chat_stats.get("cached_input") == 40
        assert chat_stats.get("output") == 100
        assert chat_stats.get("cache_pct") == 20.0

        # Verify cost calculations are populated
        costs = chat_stats.get("costs", {})
        assert costs.get("total_cost", 0.0) > 0.0
        print("Usage endpoint JSON structure: OK")

        # 10. Verify /metrics (Prometheus) contains our custom metrics
        print("Testing /metrics endpoint...")
        resp = client.get("/metrics")
        assert resp.status_code == 200
        metrics_text = resp.text

        assert "local_router_calls_total" in metrics_text
        assert "local_router_tokens_total" in metrics_text
        assert "local_router_cost_total" in metrics_text
        # Check label structure
        assert 'service="chat"' in metrics_text
        assert 'model="qwen3"' in metrics_text
        print("Prometheus metrics endpoint: OK")

    # 11. Verify usage.json serialization to disk on shutdown
    print("Testing usage serialization to disk...")
    usage_file = get_usage_file_path()
    assert os.path.exists(usage_file), f"Usage file {usage_file} was not written"

    with open(usage_file, "r") as f:
        saved_data = json.load(f)
        assert isinstance(saved_data, list)
        assert len(saved_data) == 1
        today = datetime.date.today().isoformat()
        assert saved_data[0].get("date") == today
        day_usage = saved_data[0].get("usage", {})
        assert "chat" in day_usage
        assert "qwen3" in day_usage["chat"]
        assert day_usage["chat"]["qwen3"]["calls"] == 2
        assert day_usage["chat"]["qwen3"]["streaming_calls"] == 1
        assert day_usage["chat"]["qwen3"]["normal_calls"] == 1
    print("Serialization verify: OK")


if __name__ == "__main__":
    try:
        run_tests()
        print("\nALL TESTS PASSED SUCCESSFULLY! ✅")
        sys.exit(0)
    except AssertionError as ae:
        print(f"\nTEST FAIL: {ae}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)
    finally:
        # Clean up temporary folders
        if os.path.exists(temp_config_dir):
            shutil.rmtree(temp_config_dir)
