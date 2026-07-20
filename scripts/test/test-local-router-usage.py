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
    "local_router", os.path.join(script_dir, "..", "local-router.py")
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

        # 1b. Verify /routing/ui and /ui HTML endpoints
        print("Testing /routing/ui and /ui endpoints...")
        resp_ui = client.get("/routing/ui")
        assert resp_ui.status_code == 200
        assert "Local Inference Router Dashboard" in resp_ui.text
        resp_ui2 = client.get("/ui")
        assert resp_ui2.status_code == 200
        assert "Local Inference Router Dashboard" in resp_ui2.text
        print("UI endpoints (/routing/ui, /ui): OK")

        # 2. Simulate Chat completion from Hermes Agent
        print("Testing Chat completions (Hermes Agent)...")
        payload = {
            "model": "qwen3",
            "messages": [{"role": "user", "content": "Tell me a joke."}],
            "stream": False,
        }
        headers_hermes = {"User-Agent": "codex_cli_rs/0.0.0 (Hermes Agent)"}
        resp = client.post("/v1/chat/completions", json=payload, headers=headers_hermes)
        assert resp.status_code == 200
        print("Chat Hermes normal: OK")

        # 3. Simulate Chat completion streaming from Hermes Agent
        print("Testing Chat completions streaming (Hermes Agent)...")
        payload["stream"] = True
        resp = client.post("/v1/chat/completions", json=payload, headers=headers_hermes)
        assert resp.status_code == 200
        # Iterate over stream chunks to trigger interception code
        for chunk in resp.iter_bytes():
            pass
        print("Chat Hermes streaming: OK")

        # 4. Simulate Embedding from Hindsight
        print("Testing Embeddings (Hindsight)...")
        headers_hindsight = {"User-Agent": "codex_cli_rs/0.0.0 (Hindsight)"}
        resp = client.post(
            "/v1/embeddings",
            json={"model": "qwen3-embedding", "input": "Hello world!"},
            headers=headers_hindsight,
        )
        assert resp.status_code == 200
        print("Embeddings Hindsight: OK")

        # 5. Simulate Rerank from Hindsight
        print("Testing Reranker (Hindsight)...")
        resp = client.post(
            "/v1/rerank",
            json={
                "model": "qwen3-reranker",
                "query": "Is light fast?",
                "documents": ["Yes, light is fast.", "Water is wet."],
            },
            headers=headers_hindsight,
        )
        assert resp.status_code == 200
        print("Reranker Hindsight: OK")

        # 6. Simulate TTS from curl
        print("Testing Text-to-Speech (curl)...")
        headers_curl = {"User-Agent": "curl/8.7.1"}
        resp = client.post(
            "/v1/audio/speech",
            json={
                "model": "qwen3-tts",
                "input": "This is a test of synthesized voice narration.",
            },
            headers=headers_curl,
        )
        assert resp.status_code == 200
        print("TTS curl: OK")

        # 7. Simulate STT with no User-Agent (Unknown)
        print("Testing Speech-to-Text (Unknown client)...")
        files = {"file": ("test.wav", b"AUDIO_DATA_RAW", "audio/wav")}
        data = {"model": "whisper-1"}
        resp = client.post(
            "/v1/audio/transcriptions",
            files=files,
            data=data,
            headers={"User-Agent": ""},
        )
        assert resp.status_code == 200
        print("STT unknown: OK")

        # 8. Simulate Image generation from Hermes Agent
        print("Testing Image generation (Hermes Agent)...")
        resp = client.post(
            "/v1/images/generations",
            json={
                "model": "z-image-turbo",
                "prompt": "A beautiful sunset over mountain peaks.",
                "n": 2,
            },
            headers=headers_hermes,
        )
        assert resp.status_code == 200
        print("Image generation Hermes: OK")

        # 8b. Simulate Chat completion post error (400) from Hermes Agent
        print("Testing Chat completions post error (400) (Hermes Agent)...")
        resp = client.post(
            "/v1/chat/completions",
            json={
                "model": "error-400",
                "messages": [{"role": "user", "content": "err"}],
                "stream": False,
            },
            headers=headers_hermes,
        )
        assert resp.status_code == 400
        print("Chat completions post error (400): OK")

        # 8c. Simulate Chat completions streaming error (429) from Hermes Agent
        print("Testing Chat completions streaming error (429) (Hermes Agent)...")
        resp = client.post(
            "/v1/chat/completions",
            json={
                "model": "error-429",
                "messages": [{"role": "user", "content": "err"}],
                "stream": True,
            },
            headers=headers_hermes,
        )
        assert resp.status_code == 429
        # Read the error chunk to execute generator close
        for _ in resp.iter_bytes():
            pass
        print("Chat completions streaming error (429): OK")

        # Give database background writes a small yield
        check_and_save_usage(force=True)

        # 9. Verify Usage API returns aggregated statistics
        print("Testing /usage endpoint...")
        resp = client.get("/usage")
        assert resp.status_code == 200
        usage_res = resp.json()

        # Validate totals block
        totals = usage_res.get("totals", {})
        assert totals.get("calls", 0) == 9, (
            f"Expected 9 calls, got {totals.get('calls')}"
        )
        assert totals.get("streaming_calls", 0) == 2, (
            f"Expected 2 streaming calls, got {totals.get('streaming_calls')}"
        )
        assert totals.get("calls_post", 0) == 7, (
            f"Expected 7 calls_post, got {totals.get('calls_post')}"
        )

        # Assert errors are recorded in totals
        assert totals.get("errors_streaming", {}).get("429") == 1
        assert totals.get("errors_post", {}).get("400") == 1

        # Check model entry with agent:model:service key
        chat_model_key = "hermes:qwen3:chat"
        models_dict = usage_res.get("models", {})
        assert chat_model_key in models_dict, f"Missing key {chat_model_key} in models"
        chat_stats = models_dict[chat_model_key]
        assert chat_stats.get("calls", 0) == 2
        # Mock responses return prompt=100, completion=50, cached=20
        # Uncached input = 100 - 20 = 80 per call. Total input for 2 calls = 160.
        # Cached input = 20 * 2 = 40. Output = 50 * 2 = 100.
        assert chat_stats.get("input") == 160
        assert chat_stats.get("cached_input") == 40
        assert chat_stats.get("output") == 100
        assert chat_stats.get("cache_pct") == 20.0

        # Check agents block breakdown
        agents_dict = usage_res.get("agents", {})
        assert "hermes" in agents_dict
        assert "hindsight" in agents_dict
        assert "curl" in agents_dict
        assert "unknown" in agents_dict

        assert agents_dict["hermes"]["calls"] == 5  # 2 chat + 1 img + 2 errors
        assert agents_dict["hindsight"]["calls"] == 2  # 1 embed + 1 rerank
        assert agents_dict["curl"]["calls"] == 1  # 1 tts
        assert agents_dict["unknown"]["calls"] == 1  # 1 stt

        # Verify cost calculations are populated
        costs = chat_stats.get("costs", {})
        assert costs.get("total_cost", 0.0) > 0.0
        print("Usage endpoint JSON structure: OK")

        # 9b. Verify /usage?format=text pre-formatted output
        print("Testing /usage?format=text output...")
        resp_text = client.get("/usage?format=text")
        assert resp_text.status_code == 200
        assert "AGENT:MODEL:SERVICE" in resp_text.text
        assert "Agent HERMES Total" in resp_text.text
        assert "Agent HINDSIGHT Total" in resp_text.text
        assert "Service CHAT Total" in resp_text.text
        assert "GRAND TOTAL" in resp_text.text
        assert "HTTP Errors Breakdown:" in resp_text.text
        print("\n--- MOCKED USAGE STATISTICS TABLE ---")
        print(resp_text.text)
        print("--------------------------------------\n")

        # 10. Verify /metrics (Prometheus) contains our custom metrics
        print("Testing /metrics endpoint...")
        resp = client.get("/metrics")
        assert resp.status_code == 200
        metrics_text = resp.text

        assert "local_router_calls_total" in metrics_text
        assert "local_router_tokens_total" in metrics_text
        assert "local_router_cost_total" in metrics_text
        assert "local_router_errors_total" in metrics_text
        # Check label structure
        assert 'agent="hermes"' in metrics_text
        assert 'agent="hindsight"' in metrics_text
        assert 'agent="curl"' in metrics_text
        assert 'agent="unknown"' in metrics_text
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
        assert "hermes" in day_usage
        assert "hindsight" in day_usage
        assert "chat" in day_usage["hermes"]
        assert "qwen3" in day_usage["hermes"]["chat"]
        assert day_usage["hermes"]["chat"]["qwen3"]["calls"] == 2
        assert day_usage["hermes"]["chat"]["qwen3"]["streaming_calls"] == 1
        assert day_usage["hermes"]["chat"]["qwen3"]["calls_post"] == 1
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
