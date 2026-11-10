#!/usr/bin/env python3
# scripts/test-local-router-usage.py - Test local router usage tracking and metrics

import datetime
import importlib.util
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile

from fastapi.testclient import TestClient

# Override environment BEFORE importing local-router to isolate systemd directories
temp_config_dir = tempfile.mkdtemp()
temp_state_dir = tempfile.mkdtemp()
os.environ["XDG_CONFIG_HOME"] = temp_config_dir
os.environ["XDG_STATE_HOME"] = temp_state_dir
os.environ["LROUT_MOCK_BACKENDS"] = "1"
os.makedirs(os.path.join(temp_config_dir, "systemd", "user"), exist_ok=True)
with open(os.path.join(temp_config_dir, "systemd", "user", "local-router.env"), "w") as f:
    f.write("LROUT_PORT=21099\nLROUT_HOST=127.0.0.1\n")
# Add current directory to python path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)


# Load hyphenated module using importlib
spec = importlib.util.spec_from_file_location(
    "local_router", os.path.join(script_dir, "..", "local-router.py")
)
assert spec is not None
local_router = importlib.util.module_from_spec(spec)
sys.modules["local_router"] = local_router
assert spec.loader is not None
spec.loader.exec_module(local_router)

from local_router import (  # type: ignore[import-not-found]  # ty: ignore[unresolved-import]  # noqa: E402
    _decrement_active_call,
    _increment_active_call,
    app,
    check_and_save_usage,
    get_db_connection,
    get_usage_file_path,
    load_usage_data,
    resolve_service_alias,
)


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

        # 1c. Verify root / redirects to /ui for both GET and HEAD
        print("Testing root / redirect to /ui...")
        resp_root_get = client.get("/", follow_redirects=False)
        assert resp_root_get.status_code == 302, (
            f"Expected 302 for GET /, got {resp_root_get.status_code}"
        )
        assert resp_root_get.headers.get("location") == "/ui", (
            f"Expected location '/ui', got {resp_root_get.headers.get('location')}"
        )
        resp_root_head = client.head("/", follow_redirects=False)
        assert resp_root_head.status_code == 302, (
            f"Expected 302 for HEAD /, got {resp_root_head.status_code}"
        )
        assert resp_root_head.headers.get("location") == "/ui", (
            f"Expected location '/ui', got {resp_root_head.headers.get('location')}"
        )
        print("Root redirect (GET/HEAD / -> /ui): OK")

        # 2. Simulate Chat completion from Hermes Agent
        print("Testing Chat completions (Hermes Agent)...")
        payload = {
            "model": "qwen3",
            "messages": [{"role": "user", "content": "Tell me a joke."}],
            "stream": False,
        }
        headers_hermes = {
            "User-Agent": "codex_cli_rs/0.0.0 (Hermes Agent)",
            "x-client-id": "hermes",
        }
        resp = client.post("/v1/chat/completions", json=payload, headers=headers_hermes)
        assert resp.status_code == 200
        print("Chat Hermes normal: OK")

        # 3. Simulate Chat completion streaming from Hermes Agent
        print("Testing Chat completions streaming (Hermes Agent)...")
        payload["stream"] = True
        resp = client.post("/v1/chat/completions", json=payload, headers=headers_hermes)
        assert resp.status_code == 200
        for _chunk in resp.iter_bytes():
            pass
        print("Chat Hermes streaming: OK")

        # 3b. Verify direct active stream counter increment/decrement lifecycle
        print("Testing active stream counter lifecycle...")
        _increment_active_call("test_ag", "chat", "test_md", is_streaming=True)
        active_check = client.get("/usage").json()["totals"]["calls_active_stream"]
        assert active_check == 1, f"Expected active stream 1, got {active_check}"
        _decrement_active_call("test_ag", "chat", "test_md", is_streaming=True)
        after_check = client.get("/usage").json()["totals"]["calls_active_stream"]
        assert after_check == 0, f"Expected active stream 0, got {after_check}"
        print("Active stream counter lifecycle: OK")

        # 4. Simulate Embedding from Hindsight
        print("Testing Embeddings (Hindsight)...")
        headers_hindsight = {
            "User-Agent": "codex_cli_rs/0.0.0 (Hindsight)",
            "x-client-id": "hindsight",
        }
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
        headers_curl = {"User-Agent": "curl/8.7.1", "x-client-id": "curl"}
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

        # 8d. Simulate Chat completion from Zed editor (User-Agent header auto-mapping)
        print("Testing Chat completions from Zed editor...")
        resp = client.post(
            "/v1/chat/completions",
            json={"model": "qwen3", "messages": [{"role": "user", "content": "hi"}]},
            headers={"User-Agent": "Zed/1.12.0+stable (linux; x86_64)"},
        )
        assert resp.status_code == 200
        print("Chat Zed auto-mapping: OK")

        # 8e. Simulate /props and /v1/props capability checks (excluded from usage)
        print("Testing /props and /v1/props exclusion from usage...")
        headers_omp = {"x-client-id": "oh-my-pi"}
        resp_props = client.get("/props", headers=headers_omp)
        assert resp_props.status_code == 200
        assert "default_generation_settings" in resp_props.json()
        resp_v1_props = client.get("/v1/props", headers=headers_omp)
        assert resp_v1_props.status_code == 200
        print("Props endpoints (/props, /v1/props): OK")

        # Give database background writes a small yield
        check_and_save_usage(force=True)

        # 9. Verify Usage API returns aggregated statistics
        print("Testing /usage endpoint...")
        resp = client.get("/usage")
        assert resp.status_code == 200
        usage_res = resp.json()

        # Validate totals block
        totals = usage_res.get("totals", {})
        assert totals.get("calls", 0) == 10, f"Expected 10 calls, got {totals.get('calls')}"
        assert totals.get("streaming_calls", 0) == 2, (
            f"Expected 2 streaming calls, got {totals.get('streaming_calls')}"
        )
        assert totals.get("calls_post", 0) == 8, (
            f"Expected 8 calls_post, got {totals.get('calls_post')}"
        )

        # Assert errors are recorded in totals
        assert totals.get("errors_streaming", {}).get("429") == 1
        assert totals.get("errors_post", {}).get("400") == 1

        # Check model entry with agent:model:service key
        chat_model_key = "hermes:qwen3:chat"
        models_dict = usage_res.get("models", {})
        assert chat_model_key in models_dict, f"Missing key {chat_model_key} in models"
        for model_key in models_dict:
            _ag, m_name, svc_name = model_key.split(":", 2)
            assert svc_name != "unknown", f"Unexpected service='unknown' key in /usage: {model_key}"
            assert m_name != "unknown", f"Unexpected model='unknown' key in /usage: {model_key}"
            assert m_name != "props", f"Unexpected model='props' key in /usage: {model_key}"
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
        assert "zed" in agents_dict
        assert "unknown" in agents_dict
        assert "oh-my-pi" not in agents_dict, "oh-my-pi /props probe should not appear in /usage"

        assert agents_dict["hermes"]["calls"] == 5  # 2 chat + 1 img + 2 errors
        assert agents_dict["hindsight"]["calls"] == 2  # 1 embed + 1 rerank
        assert agents_dict["curl"]["calls"] == 1  # 1 tts
        assert agents_dict["zed"]["calls"] == 1  # 1 chat zed
        assert agents_dict["unknown"]["calls"] == 1  # 1 stt

        # Verify req_stats breakdown fields in totals and models
        req_stats = totals.get("req_stats", {})
        for metric_name in [
            "total_input",
            "cached_input",
            "cached_write",
            "uniq_input",
            "output",
            "per_request",
        ]:
            assert metric_name in req_stats, f"Missing {metric_name} in req_stats"
            assert "min" in req_stats[metric_name]
            assert "median" in req_stats[metric_name]
            assert "max" in req_stats[metric_name]

        # Verify active call counters in totals
        assert "calls_active_post" in totals
        assert "calls_active_stream" in totals
        assert "calls_active" in totals
        assert totals["calls_active"] == 0, f"Expected 0 active calls, got {totals['calls_active']}"

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
        assert "local_router_time_seconds_total" in metrics_text
        # Check label structure
        assert 'agent="hermes"' in metrics_text
        assert 'agent="hindsight"' in metrics_text
        assert 'agent="curl"' in metrics_text
        assert 'agent="unknown"' in metrics_text
        assert 'service="chat"' in metrics_text
        assert 'model="qwen3"' in metrics_text
        assert 'service="unknown"' not in metrics_text
        assert 'model="props"' not in metrics_text
        print("Prometheus metrics endpoint: OK")

        # 10b. Verify /tokenize and /detokenize resolve service and model cleanly
        print("Testing /tokenize and /detokenize service/model attribution...")
        default_chat_model = resolve_service_alias("chat") or "qwen3"
        resp_tok_default = client.post(
            "/tokenize",
            json={"content": "Hello tokenization world"},
            headers=headers_hermes,
        )
        assert resp_tok_default.status_code == 200
        assert resp_tok_default.json() == {"tokens": [1, 2, 3]}

        resp_tok_embed = client.post(
            "/v1/tokenize",
            json={"model": "qwen3-embedding", "inputs": ["hello", "embedding"]},
            headers=headers_hindsight,
        )
        assert resp_tok_embed.status_code == 200
        assert resp_tok_embed.json() == {"tokens": [1, 2, 3]}

        resp_detok = client.post(
            "/detokenize",
            json={"tokens": [1, 2, 3]},
            headers=headers_hermes,
        )
        assert resp_detok.status_code == 200
        assert resp_detok.json() == {"content": "mock detokenized text"}

        check_and_save_usage(force=True)
        tok_usage = client.get("/usage?range=all").json()
        assert tok_usage["totals"]["calls"] == 13, (
            f"Expected 13 calls after tokenize/detokenize, got {tok_usage['totals']['calls']}"
        )
        tok_models = tok_usage["models"]
        default_chat_key = f"hermes:{default_chat_model}:chat"
        assert default_chat_key in tok_models, f"Missing {default_chat_key} in {tok_models.keys()}"
        expected_default_calls = 4 if default_chat_model == "qwen3" else 2
        assert tok_models[default_chat_key]["calls"] == expected_default_calls
        assert tok_models[default_chat_key]["input"] > 0
        assert "hindsight:qwen3-embedding:embedding" in tok_models
        assert tok_models["hindsight:qwen3-embedding:embedding"]["calls"] == 2
        assert not any(
            key.split(":", 2)[1] == "unknown" or key.split(":", 2)[2] == "unknown"
            for key in tok_models
        ), f"Found unexpected unknown model/service in {list(tok_models.keys())}"
        print("Tokenize/detokenize attribution: OK")

    # 11. Verify SQLite usage persistence on disk
    print("Testing SQLite usage persistence on disk...")
    usage_file = get_usage_file_path()
    assert os.path.exists(usage_file), f"Usage DB {usage_file} was not written"

    today = datetime.date.today().isoformat()
    with sqlite3.connect(usage_file) as db:
        row = db.execute(
            """
            SELECT calls, streaming_calls, calls_post, duration_post, duration_streaming
            FROM daily_aggregates
            WHERE date = ? AND agent = 'hermes' AND service = 'chat' AND model = 'qwen3'
            """,
            (today,),
        ).fetchone()
        assert row is not None, "Missing hermes/chat/qwen3 row in daily_aggregates"
        assert row[0] == 2, f"Expected calls == 2, got {row[0]}"
        assert row[1] == 1, f"Expected streaming_calls == 1, got {row[1]}"
        assert row[2] == 1, f"Expected calls_post == 1, got {row[2]}"
        assert row[3] >= 0.0, f"Expected duration_post >= 0.0, got {row[3]}"
        assert row[4] >= 0.0, f"Expected duration_streaming >= 0.0, got {row[4]}"
    print("SQLite persistence verify: OK")

    # 12. Verify normal operation does NOT delete records, while clean-unknown purges them
    print(
        "Testing that normal operation preserves records and local-router.sh clean-unknown purges unknown rows..."
    )
    conn = get_db_connection()
    bad_rows = [
        ("oh-my-pi", "unknown", "unknown"),
        ("unknown", "chat", "qwen3"),
        ("hermes", "chat", "unknown"),
    ]
    for bad_agent, bad_service, bad_model in bad_rows:
        conn.execute(
            """
            INSERT INTO request_events (
                timestamp, date, agent, service, model,
                uncached_input, cached_input, cached_write, output,
                is_streaming, status_code, duration
            ) VALUES (1.0, ?, ?, ?, ?, 0, 0, 0, 0, 0, 200, 0.01)
            """,
            (today, bad_agent, bad_service, bad_model),
        )
        conn.execute(
            """
            INSERT OR REPLACE INTO daily_aggregates (
                date, agent, service, model,
                calls, streaming_calls, calls_post,
                uncached_input, cached_input, cached_write, output,
                duration_post, duration_streaming,
                errors_streaming_json, errors_post_json
            ) VALUES (?, ?, ?, ?, 3, 0, 3, 0, 0, 0, 0, 0.03, 0.0, '{}', '{}')
            """,
            (today, bad_agent, bad_service, bad_model),
        )
    conn.commit()

    # Normal operation (load_usage_data) MUST NOT delete records
    load_usage_data()
    bad_events_count_before = conn.execute(
        "SELECT COUNT(*) FROM request_events WHERE agent = 'unknown' OR model = 'unknown' OR service = 'unknown'"
    ).fetchone()[0]
    bad_agg_count_before = conn.execute(
        "SELECT COUNT(*) FROM daily_aggregates WHERE agent = 'unknown' OR model = 'unknown' OR service = 'unknown'"
    ).fetchone()[0]
    assert bad_events_count_before >= 3, (
        f"Expected at least 3 unknown request_events preserved by load_usage_data, got {bad_events_count_before}"
    )
    assert bad_agg_count_before >= 3, (
        f"Expected at least 3 unknown daily_aggregates preserved by load_usage_data, got {bad_agg_count_before}"
    )

    # local-router.sh clean-unknown purges all unknown rows via sqlite3
    router_sh = os.path.join(script_dir, "..", "..", "assistants", "local-router.sh")
    res = subprocess.run([router_sh, "clean-unknown"], capture_output=True, text=True)
    assert res.returncode == 0, f"local-router.sh clean-unknown failed: {res.stderr}\n{res.stdout}"
    assert "Cleaned unknown records" in res.stdout, f"Unexpected output: {res.stdout}"

    bad_events_count_after = conn.execute(
        "SELECT COUNT(*) FROM request_events WHERE agent = 'unknown' OR model = 'unknown' OR service = 'unknown'"
    ).fetchone()[0]
    bad_agg_count_after = conn.execute(
        "SELECT COUNT(*) FROM daily_aggregates WHERE agent = 'unknown' OR model = 'unknown' OR service = 'unknown'"
    ).fetchone()[0]
    assert bad_events_count_after == 0, (
        f"Expected 0 unknown request_events, got {bad_events_count_after}"
    )
    assert bad_agg_count_after == 0, (
        f"Expected 0 unknown daily_aggregates, got {bad_agg_count_after}"
    )

    kept_row = conn.execute(
        "SELECT calls FROM daily_aggregates WHERE date = ? AND agent = 'hermes' AND service = 'chat' AND model = 'qwen3'",
        (today,),
    ).fetchone()
    assert kept_row is not None and kept_row[0] == 2, (
        f"Expected hermes:qwen3:chat calls=2, got {kept_row}"
    )

    load_usage_data()
    with TestClient(app) as client_after_purge:
        purged_usage = client_after_purge.get("/usage?range=all").json()
        purged_models = purged_usage.get("models", {})
        assert "hermes:qwen3:chat" in purged_models
        assert purged_models["hermes:qwen3:chat"]["calls"] == 2
        assert not any("unknown" in key.split(":", 2) for key in purged_models), (
            f"Found unknown entries in /usage after clean-unknown: {list(purged_models.keys())}"
        )
    print("Record preservation & local-router.sh clean-unknown verify: OK")
    print("\nALL TESTS PASSED SUCCESSFULLY! ✅")


if __name__ == "__main__":
    exit_code = 0
    try:
        run_tests()
    except AssertionError as ae:
        print(f"\nTEST FAIL: {ae}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        exit_code = 1
    finally:
        # Clean up temporary folders
        if os.path.exists(temp_config_dir):
            shutil.rmtree(temp_config_dir, ignore_errors=True)
        if os.path.exists(temp_state_dir):
            shutil.rmtree(temp_state_dir, ignore_errors=True)
    os._exit(exit_code)
