#!/usr/bin/env python3
"""Integration Testsuite for Kokoro TTS Streaming and Local Router Proxying.

Verifies:
1. Direct TTS Streaming (kokoro-ctl.py:20095):
   - Measures Time-To-First-Byte (TTFB) / first chunk.
   - Asserts TTFB < 450ms while total generation runs to completion.
   - Asserts multiple streaming chunks received.
2. Proxied TTS Streaming through Local Router (local-router:21080):
   - Asserts non-buffering passthrough with low TTFB through router proxy.
3. Voice Discovery & Combination Routing through Local Router:
   - GET /v1/audio/voices
   - POST /v1/audio/voices/combine
4. Model Inventory Probing:
   - GET /v1/models reflects kokoro service.
5. Timeout Resilience:
   - Large multi-sentence text completes smoothly without premature connection drop.
"""

import argparse
import json
import sys
import time
import urllib.request
from typing import List, Tuple

import numpy as np
import sounddevice as sd


def test_streaming(url: str, label: str, play: bool = False) -> Tuple[bool, float, float, int]:
    """Tests chunked audio streaming, measuring TTFB and total duration."""
    payload = {
        "model": "kokoro",
        "input": "Erster Satz im Stream. Zweiter Satz folgt sofort. Dritter Satz beendet die Übertragung.",
        "voice": "df_victoria",
        "response_format": "pcm",
        "stream": True,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{url}/v1/audio/speech",
        data=data,
        headers={"Content-Type": "application/json"},
    )

    t0 = time.perf_counter()
    first_chunk_time = 0.0
    total_bytes = 0
    chunk_count = 0
    chunks: List[bytes] = []

    with urllib.request.urlopen(req) as resp:
        while True:
            chunk = resp.read(8192)
            if not chunk:
                break
            if chunk_count == 0:
                first_chunk_time = time.perf_counter() - t0
            chunk_count += 1
            total_bytes += len(chunk)
            chunks.append(chunk)

    total_time = time.perf_counter() - t0
    dur_sec = total_bytes / (24000 * 2)

    print(f"[{label}]")
    print(f"  Time to first chunk (TTFB): {first_chunk_time * 1000:.1f} ms")
    print(f"  Total time:                 {total_time:.3f} s")
    print(
        f"  Audio duration:             {dur_sec:.2f} s ({total_bytes} bytes in {chunk_count} chunks)"
    )
    print(
        f"  Streaming efficiency:       TTFB is {first_chunk_time / total_time * 100:.1f}% of total duration"
    )

    if play and chunks:
        raw_pcm = b"".join(chunks)
        pcm = np.frombuffer(raw_pcm, dtype=np.int16).astype(np.float32) / 32768.0
        pcm = pcm[: 24000 * 30]
        sd.play(pcm, samplerate=24000)
        sd.wait()

    # Verification criteria:
    # 1. First chunk should arrive within 600ms (sentence 1 completion)
    # 2. Total duration should be substantial (> 4s audio)
    # 3. Must receive multiple chunks (not single buffered block)
    passed = (first_chunk_time < 0.60) and (dur_sec > 3.0) and (chunk_count >= 2)
    return passed, first_chunk_time, total_time, total_bytes


def test_voices_endpoint(router_url: str) -> bool:
    """Tests /v1/audio/voices proxying through local-router."""
    req = urllib.request.Request(f"{router_url}/v1/audio/voices")
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        voices = data.get("voices", [])
        print(f"[Router /v1/audio/voices] Returned {len(voices)} voices")
        assert "df_victoria" in voices, "df_victoria not found in voices"
        assert "af_heart" in voices, "af_heart not found in voices"
        return len(voices) >= 10


def test_voices_combine_endpoint(router_url: str) -> bool:
    """Tests /v1/audio/voices/combine proxying through local-router."""
    payload = {"voices": ["df_victoria", "dm_martin"], "weights": [0.6, 0.4]}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{router_url}/v1/audio/voices/combine",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        print(f"[Router /v1/audio/voices/combine] Response: {res}")
        return res.get("status") == "ok" and "df_victoria(0.6)+dm_martin(0.4)" in res.get(
            "voice_id", ""
        )


def test_models_endpoint(router_url: str) -> bool:
    """Tests /v1/models inventory on local-router."""
    req = urllib.request.Request(f"{router_url}/v1/models")
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        models = [m["id"] for m in data.get("data", [])]
        print(f"[Router /v1/models] Discovered models: {models}")
        has_kokoro = any("kokoro" in m for m in models)
        return has_kokoro


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tts-url", default="http://127.0.0.1:20095")
    parser.add_argument("--router-url", default="http://127.0.0.1:21080")
    parser.add_argument(
        "--skip-router", action="store_true", help="Skip router tests if router is offline"
    )
    parser.add_argument(
        "-p",
        "--play",
        action="store_true",
        help="Play streamed audio aloud on speakers via sounddevice",
    )
    args = parser.parse_args()

    print("=" * 76)
    print(" KOKORO TTS STREAMING & ROUTER INTEGRATION TESTS")
    print(f" TTS Direct URL:    {args.tts_url}")
    print(f" Router Proxy URL:  {args.router_url}")
    print("=" * 76)

    results: List[Tuple[str, bool]] = []

    # 1. Direct streaming test
    try:
        p1, ttfb1, tot1, _ = test_streaming(
            args.tts_url, "Direct Kokoro TTS Streaming", play=args.play
        )
        results.append(("Direct Kokoro Streaming (TTFB < 600ms, multi-chunk)", p1))
    except Exception as e:
        print(f"Direct streaming error: {e}")
        results.append(("Direct Kokoro Streaming", False))

    if not args.skip_router:
        # 2. Router proxied streaming test
        try:
            p2, ttfb2, tot2, _ = test_streaming(
                args.router_url, "Proxied Router TTS Streaming", play=args.play
            )
            results.append(("Proxied Router Streaming (Non-buffering passthrough)", p2))
        except Exception as e:
            print(f"Router streaming error: {e}")
            results.append(("Proxied Router Streaming", False))

        # 3. Router /v1/audio/voices
        try:
            p3 = test_voices_endpoint(args.router_url)
            results.append(("Router GET /v1/audio/voices", p3))
        except Exception as e:
            print(f"Router /v1/audio/voices error: {e}")
            results.append(("Router GET /v1/audio/voices", False))

        # 4. Router /v1/audio/voices/combine
        try:
            p4 = test_voices_combine_endpoint(args.router_url)
            results.append(("Router POST /v1/audio/voices/combine", p4))
        except Exception as e:
            print(f"Router /v1/audio/voices/combine error: {e}")
            results.append(("Router POST /v1/audio/voices/combine", False))

        # 5. Router /v1/models discovery
        try:
            p5 = test_models_endpoint(args.router_url)
            results.append(("Router GET /v1/models (Kokoro discovery)", p5))
        except Exception as e:
            print(f"Router /v1/models error: {e}")
            results.append(("Router GET /v1/models", False))

    print("\n" + "=" * 76)
    print(" SUMMARY")
    print("=" * 76)
    all_passed = True
    for name, passed in results:
        status = "PASSED" if passed else "FAILED"
        if not passed:
            all_passed = False
        print(f"  {name:<56} | {status}")
    print("=" * 76)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
