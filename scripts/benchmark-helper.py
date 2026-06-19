#!/usr/bin/env python3
"""benchmark-helper.py - Unified benchmarking utility for local services.

Calculates prefill, decode, embedding, rerank, TTS, and STT latency
and throughput without external dependencies.
"""

import argparse
import json
import os
import sys



import struct
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

_OUTPUT_FORMAT = "text"

def tprint(*args, **kwargs):
    if _OUTPUT_FORMAT != "text":
        kwargs['file'] = sys.stderr
    print(*args, **kwargs)


def post_json(url: str, payload: dict) -> dict:
    """Send a POST request with JSON payload and return JSON response."""
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=300.0) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        raise RuntimeError(f"HTTP Error {e.code}: {error_body}") from e
    except Exception as e:
        raise RuntimeError(f"Connection failed: {e}") from e


def get_json(url: str) -> dict:
    """Send a GET request and return JSON response."""
    req = urllib.request.Request(
        url,
        headers={"Accept": "application/json"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=300.0) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        raise RuntimeError(f"HTTP Error {e.code}: {error_body}") from e
    except Exception as e:
        raise RuntimeError(f"Connection failed: {e}") from e


def get_tmp_dir() -> str:
    """Return the system temporary directory."""
    return tempfile.gettempdir()


def run_streamed_query(
    url: str, payload: dict, display_label: str, quiet: bool = False
) -> Tuple[float, float, str, int, int]:
    """Runs a streamed chat query. Reports progress without streaming token by token to avoid terminal scrambling."""
    t0 = time.perf_counter()
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{url}/v1/chat/completions",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    first_token_time = None
    run_text = []
    prompt_tokens = 0
    completion_tokens = 0

    if not quiet:
        tprint(f"  {display_label} Prefilling... ", end="", flush=True)

    try:
        with urllib.request.urlopen(req) as response:
            for line in response:
                if not line:
                    continue
                line_str = line.decode("utf-8").strip()
                if not line_str.startswith("data: "):
                    continue
                if line_str == "data: [DONE]":
                    break

                try:
                    chunk = json.loads(line_str[6:])
                    if "usage" in chunk and chunk["usage"]:
                        prompt_tokens = chunk["usage"].get("prompt_tokens", 0)
                        completion_tokens = chunk["usage"].get("completion_tokens", 0)

                    if "choices" in chunk and chunk["choices"]:
                        delta_choice = chunk["choices"][0].get("delta", {})
                        reasoning = delta_choice.get("reasoning_content", "")
                        content = delta_choice.get("content", "")
                        token_text = reasoning if reasoning else content
                        if token_text:
                            if first_token_time is None:
                                first_token_time = time.perf_counter()
                                if not quiet:
                                    ttft = first_token_time - t0
                                    tprint(
                                        f"Completed in {ttft:.2f}s. Generating... ",
                                        end="",
                                        flush=True,
                                    )
                            run_text.append(token_text)
                except json.JSONDecodeError:
                    pass
        t_end = time.perf_counter()
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        if not quiet:
            tprint()
        raise RuntimeError(f"HTTP Error {e.code}: {error_body}") from e
    except Exception as e:
        if not quiet:
            tprint()
        raise RuntimeError(f"Request failed: {e}") from e

    if first_token_time is None:
        first_token_time = t_end

    ttft = first_token_time - t0
    total_time = t_end - t0
    text = "".join(run_text)
    generation_time = total_time - ttft

    if not quiet:
        tprint(f"Completed in {generation_time:.2f}s.")

    if prompt_tokens == 0:
        content_len = len(payload.get("messages", [{}])[0].get("content", ""))
        prompt_tokens = int(content_len / 3.8)
    if completion_tokens == 0:
        completion_tokens = int(len(text) / 3.8)

    return ttft, total_time, text, prompt_tokens, completion_tokens


def run_llm_chat(
    url: str,
    model: str,
    context_file: str,
    repeats: int,
    skip_prefill: bool = False,
    skip_distractor: bool = False,
    skip_chat: bool = False,
    skip_image: bool = False,
    image_file: Optional[str] = None,
    fraction_context: float = 1.0,
    output_format: str = 'text') -> None:
    """Run chat completion prefill/decode benchmark using a large context."""
    if not os.path.exists(context_file):
        raise FileNotFoundError(f"Context file not found: {context_file}")

    with open(context_file, "r", encoding="utf-8") as f:
        context_content = f.read()

    # Truncate context to ~29k tokens (~115k characters) to avoid GPU memory allocation failures
    MAX_CONTEXT_CHARS = 115000
    if len(context_content) > MAX_CONTEXT_CHARS:
        tprint(
            f"Warning: Context file is very large ({len(context_content)} chars). "
            f"Truncating to {MAX_CONTEXT_CHARS} chars to prevent GPU memory/caching issues."
        )
        context_content = context_content[:MAX_CONTEXT_CHARS]

    if fraction_context < 1.0:
        target_len = max(1, int(len(context_content) * fraction_context))
        tprint(
            f"Limiting context content to fraction={fraction_context} ({target_len} chars)"
        )
        context_content = context_content[:target_len]

    # Initialize values to avoid reference errors
    ttft_p0 = 0.0
    prompt_tokens_p0 = 0
    completion_tokens_p0 = 0
    prefill_speed_p0 = 0.0
    generation_speed_p0 = 0.0
    text_p0 = ""

    # Phase 0: Warmup
    if not skip_chat:
        tprint("===================================================")
        tprint("=== PHASE 0: Warmup (Validation Query) ===")
        tprint("===================================================")
        payload_p0 = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": "Hello, respond with exactly: Hello World!",
                }
            ],
            "stream": True,
            "stream_options": {"include_usage": True},
            "temperature": 0.0,
        }

        ttft_p0, total_time_p0, text_p0, prompt_tokens_p0, completion_tokens_p0 = (
            run_streamed_query(url, payload_p0, "[Warmup]", quiet=False)
        )

        generation_time_p0 = total_time_p0 - ttft_p0
        prefill_speed_p0 = (prompt_tokens_p0 / ttft_p0) if ttft_p0 > 0 else 0.0
        generation_speed_p0 = (
            (completion_tokens_p0 / generation_time_p0)
            if generation_time_p0 > 0
            else 0.0
        )

        tprint(
            f"  Metrics: TTFT={ttft_p0 * 1000:.1f}ms, Prefill={prefill_speed_p0:.2f} t/s, Gen={generation_speed_p0:.2f} t/s"
        )
        tprint(f'  Response: "{text_p0.strip()}"')


    # Phase 1: Sequential Prefill
    phase1_durations = []
    phase1_speeds = []
    if not skip_chat and not skip_prefill:
        tprint("\n===================================================")
        tprint("=== PHASE 1: Sequential Prefill (Warmup) ===")
        tprint("===================================================")
        prompt_p1 = (
            context_content + "\n\nTask: Summarize the text above in exactly 100 words."
        )
        total_len = len(prompt_p1)
        step_chars = max(1000, total_len // 10)
        current_len = step_chars
        step_idx = 1
        prev_tokens = 0

        while current_len < total_len:
            subset = prompt_p1[:current_len]
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": subset}],
                "max_tokens": 1,
                "temperature": 0.0,
            }

            t_start = time.perf_counter()
            resp = post_json(f"{url}/v1/chat/completions", payload)
            t_end = time.perf_counter()

            delta = t_end - t_start
            phase1_durations.append(delta)

            usage = resp.get("usage", {})
            current_tokens = usage.get("prompt_tokens", 0)
            if current_tokens == 0:
                current_tokens = int(len(subset) / 3.8)

            delta_tokens = current_tokens - prev_tokens
            if delta_tokens < 0:
                delta_tokens = 0
            speed_new_chunk = (delta_tokens / delta) if delta > 0 else 0.0
            phase1_speeds.append(speed_new_chunk)

            pct = (current_len / total_len) * 100
            tprint(
                f"  [Cycle {step_idx}/10] Prefilled {current_len}/{total_len} characters ({pct:.1f}%) in {delta:.2f}s "
                f"(New chunk: {delta_tokens} tokens at {speed_new_chunk:.2f} t/s)"
            )

            prev_tokens = current_tokens
            current_len += step_chars
            step_idx += 1
            if current_len >= total_len:
                break

    else:
        tprint("\n===================================================")
        tprint("=== PHASE 1: Sequential Prefill (Warmup) ===")
        tprint("===================================================")
        tprint("  SKIPPED")

    # Phase 2: Chat Generation (300-word summary)
    phase2_runs = []
    generated_text = ""
    if not skip_chat:
        tprint("\n===================================================")
        tprint("=== PHASE 2: Chat Generation (300-word summary) ===")
        tprint("===================================================")
        prompt_p2 = (
            context_content + "\n\nTask: Summarize the text above in exactly 300 words."
        )

        for r in range(repeats):
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt_p2}],
                "stream": True,
                "stream_options": {"include_usage": True},
                "temperature": 0.0,
                "max_tokens": 600,
            }

            display_label = f"[Run {r + 1}/{repeats}]"
            quiet = r > 0

            ttft, total_time, text, prompt_tokens, completion_tokens = (
                run_streamed_query(url, payload, display_label, quiet=quiet)
            )

            generation_time = total_time - ttft
            prefill_speed = (prompt_tokens / ttft) if ttft > 0 else 0.0
            generation_speed = (
                (completion_tokens / generation_time) if generation_time > 0 else 0.0
            )

            phase2_runs.append(
                {
                    "ttft": ttft,
                    "generation_time": generation_time,
                    "prefill_speed": prefill_speed,
                    "generation_speed": generation_speed,
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                }
            )

            if r == 0:
                generated_text = text

            if quiet:
                tprint(
                    f"  [Run {r + 1}/{repeats}] Completed: TTFT {ttft * 1000:.1f} ms, Decode {generation_time * 1000:.1f} ms ({generation_speed:.2f} tokens/sec)"
                )
            else:
                tprint(
                    f"  Metrics: TTFT={ttft * 1000:.1f}ms, Prefill={prefill_speed:.2f} t/s, Gen={generation_speed:.2f} t/s"
                )

    # Phase 3: Prefix Caching & Distractor Tests
    run_phase3 = not skip_distractor and not skip_chat
    phase3_results: Dict[str, List[Dict[str, Any]]] = {}

    if run_phase3:

        tprint("\n===================================================")
        tprint("=== PHASE 3: Prefix Caching & Distractor Tests ===")
        tprint("===================================================")
        tprint("Cycling [Half Prefill, Distractor, Full Prefill] 5 times...")

        half_context = context_content[: len(context_content) // 2]
        prompt_3a = (
            half_context
            + "\n\nWhat human and syntax language was the above written in?"
        )
        prompt_3b = "What is the capital of France?"
        prompt_3c = (
            context_content
            + "\n\nWhat human and syntax language was the above written in?"
        )

        scenarios = [
            ("3a. Half Prefill + Question", prompt_3a),
            ("3b. Distractor (Short Question)", prompt_3b),
            ("3c. Full Prefill + Same Question", prompt_3c),
        ]

        # Store results for each scenario type
        phase3_results = {s[0]: [] for s in scenarios}

        for cycle in range(1, 6):
            tprint(f"\n--- Cycle {cycle}/5 ---")
            for name, p_text in scenarios:
                payload = {
                    "model": model,
                    "messages": [{"role": "user", "content": p_text}],
                    "stream": True,
                    "stream_options": {"include_usage": True},
                    "temperature": 0.0,
                    "max_tokens": 100,
                }

                display_label = f"[{name}]"
                ttft, total_time, text, prompt_tokens, completion_tokens = (
                    run_streamed_query(url, payload, display_label, quiet=False)
                )

                generation_time = total_time - ttft
                prefill_speed = (prompt_tokens / ttft) if ttft > 0 else 0.0
                generation_speed = (
                    (completion_tokens / generation_time)
                    if generation_time > 0
                    else 0.0
                )

                result_item = {
                    "ttft": ttft,
                    "generation_time": generation_time,
                    "prefill_speed": prefill_speed,
                    "generation_speed": generation_speed,
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "answer": text.strip(),
                }
                phase3_results[name].append(result_item)

                tprint(
                    f"  Metrics: TTFT={ttft * 1000:.1f}ms, Prefill={prefill_speed:.2f} t/s, Gen={generation_speed:.2f} t/s"
                )

    # Phase 4: Image Description (Vision Test)
    phase4_runs = []
    has_vision = False
    vision_text = ""
    if not skip_image and image_file:
        tprint("\n===================================================")
        tprint("=== PHASE 4: Image Description (Vision Test) ===")
        tprint("===================================================")
        if not os.path.exists(image_file):
            tprint(
                f"  Warning: Vision test image not found at {image_file}. Skipping Phase 4."
            )
        else:
            has_vision = True
            import base64

            with open(image_file, "rb") as img_f:
                img_bytes = img_f.read()
            b64_data = base64.b64encode(img_bytes).decode("utf-8")

            ext = os.path.splitext(image_file)[1].lower()
            mime = "image/jpeg"
            if ext == ".png":
                mime = "image/png"
            elif ext == ".gif":
                mime = "image/gif"
            elif ext == ".webp":
                mime = "image/webp"

            payload = {
                "model": model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Describe this image in detail. What is in this picture?",
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:{mime};base64,{b64_data}"},
                            },
                        ],
                    }
                ],
                "stream": True,
                "stream_options": {"include_usage": True},
                "temperature": 0.0,
                "max_tokens": 150,
            }

            for r in range(repeats):
                display_label = f"[Vision Run {r + 1}/{repeats}]"
                quiet = r > 0

                ttft, total_time, text, prompt_tokens, completion_tokens = (
                    run_streamed_query(url, payload, display_label, quiet=quiet)
                )

                generation_time = total_time - ttft
                prefill_speed = (prompt_tokens / ttft) if ttft > 0 else 0.0
                generation_speed = (
                    (completion_tokens / generation_time)
                    if generation_time > 0
                    else 0.0
                )

                phase4_runs.append(
                    {
                        "ttft": ttft,
                        "generation_time": generation_time,
                        "prefill_speed": prefill_speed,
                        "generation_speed": generation_speed,
                        "prompt_tokens": prompt_tokens,
                        "completion_tokens": completion_tokens,
                    }
                )

                if r == 0:
                    vision_text = text

                if quiet:
                    tprint(
                        f"  [Vision Run {r + 1}/{repeats}] Completed: TTFT {ttft * 1000:.1f} ms, Decode {generation_time * 1000:.1f} ms ({generation_speed:.2f} tokens/sec)"
                    )
                else:
                    tprint(
                        f"  Metrics: TTFT={ttft * 1000:.1f}ms, Prefill={prefill_speed:.2f} t/s, Gen={generation_speed:.2f} t/s"
                    )

            # Compare result: check for keywords
            expected_keywords = [
                "eiffel",
                "tower",
                "paris",
                "structure",
                "architecture",
                "building",
                "monument",
            ]
            matched = [w for w in expected_keywords if w in vision_text.lower()]
            match_pct = (len(matched) / len(expected_keywords)) * 100
            tprint("\n  Image Description Comparison Results:")
            tprint(
                f"    Matched {len(matched)}/{len(expected_keywords)} expected keywords ({match_pct:.1f}%): {matched}"
            )

    # Compile report
    tprint("\n===================================================")
    tprint("=== CHAT BENCHMARK RESULTS SUMMARY ===")
    tprint("===================================================")
    tprint(f"Context File:      {context_file}")

    # Phase 0 Summary
    tprint("\n--- Phase 0: Warmup ---")
    tprint(f"  Prompt Tokens:        {prompt_tokens_p0}")
    tprint(f"  Completion Tokens:    {completion_tokens_p0}")
    tprint(f"  TTFT (Prefill):       {ttft_p0 * 1000:.2f} ms")
    tprint(f"  Prefill Speed:        {prefill_speed_p0:.2f} tokens/sec")
    tprint(f"  Generation Speed:     {generation_speed_p0:.2f} tokens/sec")

    # Phase 1 Summary
    tprint("\n--- Phase 1: Sequential Prefill ---")
    if not skip_prefill:
        avg_p1_duration = (
            sum(phase1_durations) / len(phase1_durations) if phase1_durations else 0.0
        )
        avg_p1_speed = sum(phase1_speeds) / len(phase1_speeds) if phase1_speeds else 0.0
        tprint(f"  Cycles:               {len(phase1_durations)}")
        tprint(f"  Avg Cycle Prefill Time: {avg_p1_duration:.2f} s")
        tprint(f"  Avg New Chunk Prefill Speed: {avg_p1_speed:.2f} tokens/sec")
    else:
        tprint("  SKIPPED")

    # Phase 2 Summary
    if not skip_chat and phase2_runs:
        avg_p2_ttft = sum(x["ttft"] for x in phase2_runs) / len(phase2_runs)
        avg_p2_gen_time = sum(x["generation_time"] for x in phase2_runs) / len(
            phase2_runs
        )
        avg_p2_prefill_speed = sum(x["prefill_speed"] for x in phase2_runs) / len(
            phase2_runs
        )
        avg_p2_gen_speed = sum(x["generation_speed"] for x in phase2_runs) / len(
            phase2_runs
        )
        avg_p2_prompt_tokens = phase2_runs[0]["prompt_tokens"]
        avg_p2_comp_tokens = sum(x["completion_tokens"] for x in phase2_runs) / len(
            phase2_runs
        )

        tprint("\n--- Phase 2: Generation (300-word summary) ---")
        tprint(f"  Runs:                 {repeats}")
        tprint(f"  Prompt Tokens:        {avg_p2_prompt_tokens}")
        tprint(f"  Avg Completion Tokens: {avg_p2_comp_tokens:.1f}")
        tprint(f"  Avg TTFT (Prefill):   {avg_p2_ttft * 1000:.2f} ms")
        tprint(f"  Avg Prefill Speed:    {avg_p2_prefill_speed:.2f} tokens/sec")
        tprint(f"  Avg Generation Speed: {avg_p2_gen_speed:.2f} tokens/sec")
        tprint(f"  Avg Decode Time:      {avg_p2_gen_time:.2f} s")
        tprint("\n--- Summary Snippet (Run 1) ---")
        tprint(generated_text.strip()[:350] + "...")

    # Phase 3 Summary
    if not skip_chat and run_phase3:
        tprint("\n--- Phase 3: Prefix Caching & Distractor (Averages over 5 Cycles) ---")
        for name in phase3_results:
            runs = phase3_results[name]
            avg_ttft = sum(x["ttft"] for x in runs) / len(runs)
            avg_prefill = sum(x["prefill_speed"] for x in runs) / len(runs)
            avg_gen = sum(x["generation_speed"] for x in runs) / len(runs)
            last_answer = runs[-1]["answer"]
            tprint(f"  {name}:")
            tprint(f"    Avg TTFT:           {avg_ttft * 1000:.2f} ms")
            tprint(f"    Avg Prefill Speed:  {avg_prefill:.2f} tokens/sec")
            tprint(f"    Avg Gen Speed:      {avg_gen:.2f} tokens/sec")
            tprint(f'    Last Answer:        "{last_answer}"')
    else:
        tprint("\n--- Phase 3: Prefix Caching & Distractor ---")
        tprint("  SKIPPED")

    # Phase 4 Summary
    if has_vision and phase4_runs:
        avg_p4_ttft = sum(x["ttft"] for x in phase4_runs) / len(phase4_runs)
        avg_p4_gen_time = sum(x["generation_time"] for x in phase4_runs) / len(
            phase4_runs
        )
        avg_p4_prefill_speed = sum(x["prefill_speed"] for x in phase4_runs) / len(
            phase4_runs
        )
        avg_p4_gen_speed = sum(x["generation_speed"] for x in phase4_runs) / len(
            phase4_runs
        )
        avg_p4_prompt_tokens = phase4_runs[0]["prompt_tokens"]
        avg_p4_comp_tokens = sum(x["completion_tokens"] for x in phase4_runs) / len(
            phase4_runs
        )

        tprint("\n--- Phase 4: Image Description (Vision) ---")
        tprint(f"  Runs:                 {repeats}")
        tprint(f"  Prompt Tokens:        {avg_p4_prompt_tokens}")
        tprint(f"  Avg Completion Tokens: {avg_p4_comp_tokens:.1f}")
        tprint(f"  Avg TTFT (Prefill):   {avg_p4_ttft * 1000:.2f} ms")
        tprint(f"  Avg Prefill Speed:    {avg_p4_prefill_speed:.2f} tokens/sec")
        tprint(f"  Avg Generation Speed: {avg_p4_gen_speed:.2f} tokens/sec")
        tprint(f"  Avg Decode Time:      {avg_p4_gen_time:.2f} s")
        tprint("\n--- Vision Snippet (Run 1) ---")
        tprint(vision_text.strip()[:350] + "...")
    tprint("===================================================\n")


def run_llm_embed(
    url: str,
    model: str,
    context_file: str,
    repeats: int,
    fraction_chunks: float = 1.0,
    output_format: str = 'text') -> None:
    """Run embedding benchmark using the full context file (~44.5k tokens).

    Tokenizes the full context via the server's /tokenize endpoint to get exact
    token counts, then splits into chunks of exactly 8192 tokens (matching the
    configured ubatch-size). Sends token ID arrays directly to /v1/embeddings
    and measures per-chunk latency plus aggregate throughput.
    """
    if not os.path.exists(context_file):
        raise FileNotFoundError(f"Context file not found: {context_file}")

    with open(context_file, "r", encoding="utf-8") as f:
        context_content = f.read()

    # Tokenize the full context via the server to get exact token IDs,
    # then split into chunks of size matching the server's context size.
    max_tokens_per_chunk = 8192
    try:
        props = get_json(f"{url}/props")
        if props and "default_generation_settings" in props:
            n_ctx = props["default_generation_settings"].get("n_ctx", 8192)
            if n_ctx > 0:
                max_tokens_per_chunk = min(8192, n_ctx)
                tprint(
                    f"  Dynamic chunk size resolved from server: {max_tokens_per_chunk}"
                )
    except Exception as e:
        tprint(f"  Warning: Failed to query server props for n_ctx: {e}")

    tprint("  Tokenizing full context via server...")
    tokenize_resp = post_json(
        f"{url}/tokenize",
        {"model": model, "content": context_content, "add_special": False},
    )
    all_tokens: List[int] = tokenize_resp.get("tokens", [])
    total_tokens_exact = len(all_tokens)

    # Split token array into chunks
    chunks: List[List[int]] = [
        all_tokens[i : i + max_tokens_per_chunk]
        for i in range(0, total_tokens_exact, max_tokens_per_chunk)
    ]

    total_context_chars = len(context_content)
    full_chunk_count = len(chunks)

    if fraction_chunks < 1.0:
        limit = max(1, int(len(chunks) * fraction_chunks))
        chunks = chunks[:limit]

    tprint("===================================================")
    tprint("=== EMBEDDING BENCHMARK                         ===")
    tprint("===================================================")
    tprint(f"Context File:      {context_file}")
    tprint(
        f"Context Size:      {total_context_chars} chars ({total_tokens_exact} tokens)"
    )
    tprint(f"Chunk Size:        {max_tokens_per_chunk} tokens (max)")
    if fraction_chunks < 1.0:
        tprint(
            f"Total Chunks:      {len(chunks)} ({', '.join(str(len(c)) for c in chunks)} tokens) [limited from {full_chunk_count} (fraction={fraction_chunks})]"
        )
    else:
        tprint(
            f"Total Chunks:      {len(chunks)} ({', '.join(str(len(c)) for c in chunks)} tokens)"
        )
    tprint(f"Repeats:           {repeats}")

    # Phase 0: Warmup — single short embedding to prime the model
    tprint("\n--- Phase 0: Warmup ---")
    warmup_payload = {"model": model, "input": "warmup embedding test"}
    t0 = time.perf_counter()
    warmup_resp = post_json(f"{url}/v1/embeddings", warmup_payload)
    t1 = time.perf_counter()

    embed_dim = 0
    if warmup_resp.get("data"):
        embed_vec = warmup_resp["data"][0].get("embedding", [])
        embed_dim = len(embed_vec)
    tprint(f"  Warmup latency:  {(t1 - t0) * 1000:.1f} ms")
    tprint(f"  Embedding dim:   {embed_dim}")


    # Phase 1: Full context embedding
    tprint("\n--- Phase 1: Full Context Embedding ---")
    run_results: List[Dict[str, Any]] = []

    for r in range(repeats):
        tprint(
            f"  [Run {r + 1}/{repeats}] Embedding {len(chunks)} chunks sequentially..."
        )
        chunk_latencies: List[float] = []
        chunk_tokens_list: List[int] = []
        run_total_tokens = 0
        run_embed_dim = 0

        t_run_start = time.perf_counter()
        for idx, chunk_tokens in enumerate(chunks):
            payload = {
                "model": model,
                "input": chunk_tokens,
            }
            t_chunk_start = time.perf_counter()
            resp = post_json(f"{url}/v1/embeddings", payload)
            t_chunk_end = time.perf_counter()

            chunk_latency_ms = (t_chunk_end - t_chunk_start) * 1000.0
            chunk_latencies.append(chunk_latency_ms)

            # Use exact token count from our chunking
            prompt_tokens = len(chunk_tokens)
            chunk_tokens_list.append(prompt_tokens)
            run_total_tokens += prompt_tokens

            # Validate embedding dimensions on first chunk
            if idx == 0 and resp.get("data"):
                run_embed_dim = len(resp["data"][0].get("embedding", []))

        t_run_end = time.perf_counter()
        run_duration_s = t_run_end - t_run_start
        run_speed = (run_total_tokens / run_duration_s) if run_duration_s > 0 else 0.0

        # Latency statistics
        sorted_lat = sorted(chunk_latencies)
        p50_idx = len(sorted_lat) // 2
        p95_idx = min(int(len(sorted_lat) * 0.95), len(sorted_lat) - 1)
        p50_lat = sorted_lat[p50_idx]
        p95_lat = sorted_lat[p95_idx]
        min_lat = sorted_lat[0]
        max_lat = sorted_lat[-1]
        avg_lat = sum(chunk_latencies) / len(chunk_latencies)

        run_info = {
            "duration_s": run_duration_s,
            "total_tokens": run_total_tokens,
            "speed_tps": run_speed,
            "embed_dim": run_embed_dim,
            "chunk_count": len(chunks),
            "latency_avg_ms": avg_lat,
            "latency_p50_ms": p50_lat,
            "latency_p95_ms": p95_lat,
            "latency_min_ms": min_lat,
            "latency_max_ms": max_lat,
        }
        run_results.append(run_info)

        tprint(
            f"    Total: {run_duration_s:.2f}s | {run_total_tokens} tokens | "
            f"{run_speed:.2f} t/s"
        )
        tprint(
            f"    Chunk latency: avg={avg_lat:.1f}ms  p50={p50_lat:.1f}ms  "
            f"p95={p95_lat:.1f}ms  min={min_lat:.1f}ms  max={max_lat:.1f}ms"
        )

    # Summary report
    tprint("\n===================================================")
    tprint("=== EMBEDDING BENCHMARK RESULTS SUMMARY         ===")
    tprint("===================================================")
    tprint(f"Context File:      {context_file}")
    tprint(
        f"Context Size:      {total_context_chars} chars ({total_tokens_exact} tokens)"
    )
    tprint(f"Chunks:            {len(chunks)} × {max_tokens_per_chunk} tokens (max)")
    tprint(f"Embedding Dim:     {embed_dim}")
    tprint(f"Repeats:           {repeats}")

    avg_duration = sum(r["duration_s"] for r in run_results) / len(run_results)
    avg_tokens = sum(r["total_tokens"] for r in run_results) / len(run_results)
    avg_speed = sum(r["speed_tps"] for r in run_results) / len(run_results)
    avg_lat = sum(r["latency_avg_ms"] for r in run_results) / len(run_results)
    avg_p50 = sum(r["latency_p50_ms"] for r in run_results) / len(run_results)
    avg_p95 = sum(r["latency_p95_ms"] for r in run_results) / len(run_results)

    tprint(f"\n  Avg Tokens/Run:       {avg_tokens:.0f}")
    tprint(f"  Avg Time/Run:         {avg_duration:.2f} s")
    tprint(f"  Avg Throughput:       {avg_speed:.2f} tokens/sec")
    tprint(f"\n  Avg Chunk Latency:    {avg_lat:.1f} ms")
    tprint(f"  Avg Chunk p50:        {avg_p50:.1f} ms")
    tprint(f"  Avg Chunk p95:        {avg_p95:.1f} ms")
    tprint("===================================================")


def run_rerank(url: str, model: str, context_file: str, repeats: int, output_format: str = 'text') -> None:
    """Run rerank benchmark by splitting a portion of context into 10 safe chunks."""
    if not os.path.exists(context_file):
        raise FileNotFoundError(f"Context file not found: {context_file}")

    with open(context_file, "r", encoding="utf-8") as f:
        context_content = f.read()

    # To stay within physical batch size limits per document, we take the first 13,000 characters
    # and split them into 10 chunks of 1,300 characters (~340 tokens each).
    total_len = min(len(context_content), 13000)
    subset_content = context_content[:total_len]
    chunk_size = 1300
    chunks = [
        subset_content[i : i + chunk_size] for i in range(0, total_len, chunk_size)
    ]
    # Ensure exactly 10 documents
    chunks = [c for c in chunks if c.strip()][:10]
    while len(chunks) < 10:
        chunks.append("Empty spacer document chunk to maintain count.")

    query = "How do I configure Honcho memory recall mode and observation settings?"

    payload = {
        "model": model,
        "query": query,
        "documents": chunks,
        "top_n": 3,
    }

    tprint(f"Running rerank benchmark with {repeats} repeats...")
    durations_ms = []
    docs_speeds = []
    tokens_speeds = []
    resp = {}

    total_chars = sum(len(doc) for doc in chunks) + len(query)
    estimated_tokens = int(total_chars / 3.8)

    for r in range(repeats):
        t0 = time.perf_counter()
        resp = post_json(f"{url}/v1/rerank", payload)
        t1 = time.perf_counter()
        duration = (t1 - t0) * 1000.0
        docs_per_sec = (len(chunks) / (duration / 1000.0)) if duration > 0 else 0.0
        tokens_per_sec = (
            (estimated_tokens / (duration / 1000.0)) if duration > 0 else 0.0
        )

        durations_ms.append(duration)
        docs_speeds.append(docs_per_sec)
        tokens_speeds.append(tokens_per_sec)
        tprint(
            f"    Completed repeat {r + 1}: {duration:.2f} ms ({tokens_per_sec:.2f} tokens/sec)"
        )

    avg_duration = sum(durations_ms) / len(durations_ms)
    avg_docs_speed = sum(docs_speeds) / len(docs_speeds)
    avg_tokens_speed = sum(tokens_speeds) / len(tokens_speeds)

    tprint("\n=== Rerank Benchmark Results (Cumulative Average) ===")
    tprint(f"Query:             {query}")
    tprint(f"Number of Docs:    {len(chunks)}")
    tprint(f"Repeats:           {repeats}")
    tprint(f"Total Chars:       {total_chars}")
    tprint(f"Estimated Tokens:  {estimated_tokens}")
    tprint(f"Avg Reranking Time:{avg_duration:.2f} ms")
    tprint(f"Avg Docs Throughput:{avg_docs_speed:.2f} docs/sec")
    tprint(f"Avg Token Speed:   {avg_tokens_speed:.2f} tokens/sec")
    results = resp.get("results", [])
    if results:
        tprint("--- Top 3 Results (Last Run) ---")
        for i, r_item in enumerate(results[:3]):
            idx = r_item.get("index", 0)
            score = r_item.get("relevance_score", 0.0)
            text_snippet = chunks[idx].strip()[:100].replace("\n", " ")
            tprint(f"  {i + 1}. Index {idx:02d} (Score: {score:.4f}): {text_snippet}...")
    tprint("=====================================================\n")


def parse_wav_duration(file_path: str) -> float:
    """Parse standard PCM WAV file header and calculate duration."""
    with open(file_path, "rb") as f:
        header = f.read(44)
        if len(header) < 44:
            raise ValueError("Invalid WAV file: header too short")
        if header[0:4] != b"RIFF" or header[8:12] != b"WAVE":
            raise ValueError("Invalid WAV file: missing RIFF/WAVE header")

        num_channels = struct.unpack("<H", header[22:24])[0]
        sample_rate = struct.unpack("<I", header[24:28])[0]
        bits_per_sample = struct.unpack("<H", header[34:36])[0]
        data_size = struct.unpack("<I", header[40:44])[0]

        bytes_per_second = sample_rate * num_channels * (bits_per_sample // 8)
        if bytes_per_second == 0:
            raise ValueError("Invalid sample rate or channels in WAV header")
        return data_size / bytes_per_second


def run_tts(url: str, model: str, output_wav: str, repeats: int, output_format: str = 'text') -> None:
    """Synthesize a fixed 45-word sentence and measure synthesis speed/RTF."""
    text = (
        "The quick brown fox jumps over the lazy dog. This sentence has exactly "
        "forty five words to verify that the speech generation pipeline functions "
        "correctly. The generated audio file is sent to local speech to text service "
        "to measure synthesis performance of this audio system."
    )

    payload = {
        "model": model,
        "input": text,
        "voice": "serena",
        "response_format": "wav",
    }

    tprint(f"Running text-to-speech benchmark with {repeats} repeats...")
    durations = []
    rtfs = []
    char_speeds = []
    word_speeds = []

    for r in range(repeats):
        t0 = time.perf_counter()
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{url}/v1/audio/speech",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req) as response:
                audio_data = response.read()
        except Exception as e:
            raise RuntimeError(f"TTS Synthesis failed on repeat {r + 1}: {e}") from e
        t1 = time.perf_counter()

        synthesis_duration = t1 - t0

        # Write file for duration calculation
        with open(output_wav, "wb") as f:
            f.write(audio_data)

        audio_len = parse_wav_duration(output_wav)
        rtf = synthesis_duration / audio_len if audio_len > 0 else 0.0
        char_speed = len(text) / synthesis_duration if synthesis_duration > 0 else 0.0
        word_speed = 45.0 / synthesis_duration if synthesis_duration > 0 else 0.0

        durations.append(synthesis_duration)
        rtfs.append(rtf)
        char_speeds.append(char_speed)
        word_speeds.append(word_speed)
        tprint(
            f"    Completed repeat {r + 1}: {synthesis_duration:.2f}s (RTF: {rtf:.4f})"
        )

    avg_duration = sum(durations) / len(durations)
    avg_rtf = sum(rtfs) / len(rtfs)
    avg_char_speed = sum(char_speeds) / len(char_speeds)
    avg_word_speed = sum(word_speeds) / len(word_speeds)
    audio_len = parse_wav_duration(output_wav)

    tprint("\n=== Text-to-Speech Benchmark Results (Cumulative Average) ===")
    tprint(f"Sentence:          {text}")
    tprint(f"Sentence Length:   45 words / {len(text)} chars")
    tprint(f"Repeats:           {repeats}")
    tprint(f"Audio Duration:    {audio_len:.2f} seconds")
    tprint(f"Avg Synthesis Time:{avg_duration:.2f} seconds")
    tprint(f"Avg RTF:           {avg_rtf:.4f} (RTF < 1 is faster than real-time)")
    tprint(
        f"Avg Speed:         {avg_char_speed:.2f} chars/sec ({avg_word_speed:.2f} words/sec)"
    )
    tprint("=============================================================\n")


def make_multipart(
    filename: str, file_content: bytes, model_name: str
) -> Tuple[bytes, str]:
    """Manually construct a multipart/form-data payload."""
    boundary = f"----WebKitFormBoundaryBench{int(time.time())}"
    body = []

    # model field
    body.append(f"--{boundary}".encode("utf-8"))
    body.append(b'Content-Disposition: form-data; name="model"')
    body.append(b"")
    body.append(model_name.encode("utf-8"))

    # file field
    body.append(f"--{boundary}".encode("utf-8"))
    body.append(
        f'Content-Disposition: form-data; name="file"; filename="{filename}"'.encode(
            "utf-8"
        )
    )
    body.append(b"Content-Type: audio/wav")
    body.append(b"")
    body.append(file_content)

    body.append(f"--{boundary}--".encode("utf-8"))
    body.append(b"")

    payload = b"\r\n".join(body)
    content_type = f"multipart/form-data; boundary={boundary}"
    return payload, content_type


def run_stt(url: str, model: str, audio_file: str, repeats: int, output_format: str = 'text') -> None:
    """Trim audio file to 45 seconds using ffmpeg, transcribe, and measure RTF."""
    if not os.path.exists(audio_file):
        raise FileNotFoundError(f"Input audio file not found: {audio_file}")

    tprint(f"Trimming {audio_file} to 45 seconds (16kHz, mono WAV)...")
    temp_wav_fd, temp_wav_path = tempfile.mkstemp(suffix=".wav", dir=get_tmp_dir())
    os.close(temp_wav_fd)

    try:
        # Construct ffmpeg command to extract first 45 seconds to 16kHz mono WAV
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            audio_file,
            "-ss",
            "0",
            "-t",
            "45",
            "-ar",
            "16000",
            "-ac",
            "1",
            "-c:a",
            "pcm_s16le",
            temp_wav_path,
        ]
        # Run command quietly
        subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )

        # Read trimmed file
        with open(temp_wav_path, "rb") as f:
            wav_bytes = f.read()

        tprint(f"Running speech-to-text benchmark with {repeats} repeats...")
        durations = []
        rtfs = []
        text = ""

        for r in range(repeats):
            payload, content_type = make_multipart("speech.wav", wav_bytes, model)

            t0 = time.perf_counter()
            req = urllib.request.Request(
                f"{url}/v1/audio/transcriptions",
                data=payload,
                headers={"Content-Type": content_type},
                method="POST",
            )

            with urllib.request.urlopen(req) as response:
                resp_bytes = response.read()

            t1 = time.perf_counter()
            duration = t1 - t0
            resp_data = json.loads(resp_bytes.decode("utf-8"))
            rtf = duration / 45.0

            durations.append(duration)
            rtfs.append(rtf)

            if r == 0:
                text = resp_data.get("text", "").strip()
            tprint(f"    Completed repeat {r + 1}: {duration:.2f}s (RTF: {rtf:.4f})")

        avg_duration = sum(durations) / len(durations)
        avg_rtf = sum(rtfs) / len(rtfs)

        tprint("\n=== Speech-to-Text Benchmark Results (Cumulative Average) ===")
        tprint(f"Source Audio:      {audio_file}")
        tprint(f"Repeats:           {repeats}")
        tprint("Trimmed Segment:   45.0 seconds")
        tprint(f"Avg Transcribe Time:{avg_duration:.2f} seconds")
        tprint(f"Avg RTF:           {avg_rtf:.4f} (RTF < 1 is faster than real-time)")
        tprint("\n--- Transcription Snippet (Repeat 1) ---")
        tprint(text[:300] + ("..." if len(text) > 300 else ""))
        tprint("=============================================================\n")

    finally:
        if os.path.exists(temp_wav_path):
            os.remove(temp_wav_path)


def run_image(url: str, model: str, repeats: int, output_format: str = 'text') -> None:
    """Run image generation benchmark by generating an image and measuring time."""
    prompt = "A high-resolution, beautiful photograph of a pristine mountain lake at sunrise, highly detailed."
    payload = {"prompt": prompt, "steps": 8, "cfg_scale": 1.0}

    tprint(f"Running image generation benchmark with {repeats} repeats...")
    durations = []

    for r in range(repeats):
        t0 = time.perf_counter()
        try:
            resp = post_json(f"{url}/v1/images/generations", payload)
            if not resp.get("data"):
                raise RuntimeError("Empty response or missing 'data' field")
        except Exception as e:
            raise RuntimeError(f"Image generation failed on repeat {r + 1}: {e}") from e
        t1 = time.perf_counter()

        duration = t1 - t0
        durations.append(duration)
        tprint(f"    Completed repeat {r + 1}: {duration:.2f}s")

    avg_duration = sum(durations) / len(durations)

    if output_format in ("json", "yaml"):
        result = {
            "mode": "image",
            "prompt": prompt,
            "steps": 8,
            "cfg_scale": 1.0,
            "repeats": repeats,
            "image_time": avg_duration
        }
        print(json.dumps(result, indent=2))
        return

    tprint("\n=== Image Generation Benchmark Results (Cumulative Average) ===")
    tprint(f"Prompt:            {prompt}")
    tprint("Steps:             8")
    tprint("CFG Scale:         1.0")
    tprint(f"Repeats:           {repeats}")
    tprint(f"Avg Generation Time:{avg_duration:.2f} seconds")
    tprint("=============================================================\n")


def main() -> None:
    """Parse args and dispatch benchmark execution."""
    parser = argparse.ArgumentParser(
        description="Benchmark helper for local LLM, Embeddings, Reranker, TTS, and STT."
    )
    parser.add_argument(
        "--mode",
        choices=["chat", "embedding", "rerank", "tts", "stt", "image"],
        required=True,
        help="Benchmark mode to run",
    )
    parser.add_argument(
        "--url",
        required=True,
        help="Base API endpoint URL (e.g. http://127.0.0.1:50080)",
    )
    parser.add_argument(
        "--model", required=True, help="Model name or alias to benchmark"
    )
    parser.add_argument(
        "--context", help="Path to benchmark-context.md (for LLM and rerank)"
    )
    parser.add_argument("--audio", help="Path to input audio file (for speech-to-text)")
    parser.add_argument(
        "--output-dir",
        default="/tmp",
        help="Directory to save outputs (e.g. synthesized speech)",
    )
    parser.add_argument(
        "--repeat",
        type=int,
        default=None,
        help="Number of repeats to run the benchmark and compute cumulative averages",
    )
    parser.add_argument(
        "--skip-prefill",
        action="store_true",
        help="Skip LLM Chat Phase 1 sequential prefill",
    )
    parser.add_argument(
        "--skip-distractor",
        action="store_true",
        help="Skip LLM Chat Phase 3 prefix caching & distractor tests",
    )
    parser.add_argument(
        "--skip-chat",
        action="store_true",
        help="Skip LLM Chat Phase 1, 2, and 3",
    )
    parser.add_argument(
        "--skip-image",
        action="store_true",
        help="Skip LLM Chat Phase 4 vision/image test",
    )
    parser.add_argument(
        "--image-file",
        help="Path to multimodal validation image (for chat vision test)",
    )
    parser.add_argument(
        "--fraction-chunks",
        type=float,
        default=1.0,
        help="Fraction of chunks to use for the Embedding benchmark (between 0.0 and 1.0)",
    )
    parser.add_argument(
        "--fraction-context",
        type=float,
        default=1.0,
        help="Fraction of context length to use for the LLM Chat benchmark (between 0.0 and 1.0)",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json", "yaml"],
        default="text",
        help="Output format (default: text)",
    )

    args = parser.parse_args()
    global _OUTPUT_FORMAT
    _OUTPUT_FORMAT = args.format

    repeats = (
        args.repeat if args.repeat is not None else (10 if args.mode in ["stt"] else 1)
    )

    output_dir = args.output_dir if args.output_dir else "/tmp"
    output_path = os.path.join(output_dir, "tts_benchmark_output.wav")

    if args.mode == "chat":
        if not args.context:
            parser.error("--context is required in chat mode")
        run_llm_chat(
            args.url,
            args.model,
            args.context,
            repeats,
            skip_prefill=args.skip_prefill,
            skip_distractor=args.skip_distractor,
            skip_chat=args.skip_chat,
            skip_image=args.skip_image,
            image_file=args.image_file,
            fraction_context=args.fraction_context,
            output_format=args.format,
        )
    elif args.mode == "embedding":
        if not args.context:
            parser.error("--context is required in embedding mode")
        run_llm_embed(
            args.url,
            args.model,
            args.context,
            repeats,
            fraction_chunks=args.fraction_chunks,
            output_format=args.format,
        )
    elif args.mode == "rerank":
        if not args.context:
            parser.error("--context is required in rerank mode")
        run_rerank(args.url, args.model, args.context, repeats, output_format=args.format)
    elif args.mode == "tts":
        run_tts(args.url, args.model, output_path, repeats, output_format=args.format)
    elif args.mode == "stt":
        if not args.audio:
            parser.error("--audio is required in stt mode")
        run_stt(args.url, args.model, args.audio, repeats, output_format=args.format)
    elif os.path.basename(__file__) == "benchmark-helper.py" and args.mode == "image":
        # Keep as dummy or just call run_image
        run_image(args.url, args.model, repeats, output_format=args.format)
    elif args.mode == "image":
        run_image(args.url, args.model, repeats, output_format=args.format)


if __name__ == "__main__":
    main()
