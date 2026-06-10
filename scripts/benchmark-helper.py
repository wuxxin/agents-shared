#!/usr/bin/env python3
"""benchmark-helper.py - Unified benchmarking utility for local services.

Calculates prefill, decode, embedding, rerank, TTS, and STT latency
and throughput without external dependencies.
"""

import argparse
import json
import os
import struct
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from typing import Any, Dict, List, Tuple


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
        with urllib.request.urlopen(req) as response:
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
        print(f"  {display_label} Prefilling... ", end="", flush=True)

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
                                    print(
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
            print()
        raise RuntimeError(f"HTTP Error {e.code}: {error_body}") from e
    except Exception as e:
        if not quiet:
            print()
        raise RuntimeError(f"Request failed: {e}") from e

    if first_token_time is None:
        first_token_time = t_end

    ttft = first_token_time - t0
    total_time = t_end - t0
    text = "".join(run_text)
    generation_time = total_time - ttft

    if not quiet:
        print(f"Completed in {generation_time:.2f}s.")

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
) -> None:
    """Run chat completion prefill/decode benchmark using a large context."""
    if not os.path.exists(context_file):
        raise FileNotFoundError(f"Context file not found: {context_file}")

    with open(context_file, "r", encoding="utf-8") as f:
        context_content = f.read()

    # Truncate context to ~30k tokens (~115k characters) to avoid GPU memory allocation failures
    MAX_CONTEXT_CHARS = 115000
    if len(context_content) > MAX_CONTEXT_CHARS:
        print(
            f"Warning: Context file is very large ({len(context_content)} chars). "
            f"Truncating to {MAX_CONTEXT_CHARS} chars to prevent GPU memory/caching issues."
        )
        context_content = context_content[:MAX_CONTEXT_CHARS]

    # Phase 0: Warmup
    print("===================================================")
    print("=== PHASE 0: Warmup (Validation Query) ===")
    print("===================================================")
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
        (completion_tokens_p0 / generation_time_p0) if generation_time_p0 > 0 else 0.0
    )

    print(
        f"  Metrics: TTFT={ttft_p0 * 1000:.1f}ms, Prefill={prefill_speed_p0:.2f} t/s, Gen={generation_speed_p0:.2f} t/s"
    )
    print(f'  Response: "{text_p0.strip()}"')

    # Sleep 10 seconds between Phase 0 and next phase
    print("\nSleeping 10 seconds between Phase 0 and next phase...")
    time.sleep(10)

    # Phase 1: Sequential Prefill
    phase1_durations = []
    phase1_speeds = []
    if not skip_prefill:
        print("\n===================================================")
        print("=== PHASE 1: Sequential Prefill (Warmup) ===")
        print("===================================================")
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
            print(
                f"  [Cycle {step_idx}/10] Prefilled {current_len}/{total_len} characters ({pct:.1f}%) in {delta:.2f}s "
                f"(New chunk: {delta_tokens} tokens at {speed_new_chunk:.2f} t/s)"
            )

            prev_tokens = current_tokens
            current_len += step_chars
            step_idx += 1
            if current_len >= total_len:
                break

        # Sleep 10 seconds between Phase 1 and Phase 2
        print("\nSleeping 10 seconds between Phase 1 and Phase 2...")
        time.sleep(10)
    else:
        print("\n===================================================")
        print("=== PHASE 1: Sequential Prefill (Warmup) ===")
        print("===================================================")
        print("  SKIPPED")

    # Phase 2: Chat Generation (300-word summary)
    print("\n===================================================")
    print("=== PHASE 2: Chat Generation (300-word summary) ===")
    print("===================================================")
    prompt_p2 = (
        context_content + "\n\nTask: Summarize the text above in exactly 300 words."
    )

    phase2_runs = []
    generated_text = ""

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

        ttft, total_time, text, prompt_tokens, completion_tokens = run_streamed_query(
            url, payload, display_label, quiet=quiet
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
            print(
                f"  [Run {r + 1}/{repeats}] Completed: TTFT {ttft * 1000:.1f} ms, Decode {generation_time * 1000:.1f} ms ({generation_speed:.2f} tokens/sec)"
            )
        else:
            print(
                f"  Metrics: TTFT={ttft * 1000:.1f}ms, Prefill={prefill_speed:.2f} t/s, Gen={generation_speed:.2f} t/s"
            )

    # Phase 3: Prefix Caching & Distractor Tests
    run_phase3 = not skip_distractor
    phase3_results: Dict[str, List[Dict[str, Any]]] = {}

    if run_phase3:
        # Sleep 10 seconds between Phase 2 and Phase 3
        print("\nSleeping 10 seconds between Phase 2 and Phase 3...")
        time.sleep(10)

        print("\n===================================================")
        print("=== PHASE 3: Prefix Caching & Distractor Tests ===")
        print("===================================================")
        print("Cycling [Half Prefill, Distractor, Full Prefill] 5 times...")

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
            print(f"\n--- Cycle {cycle}/5 ---")
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

                print(
                    f"  Metrics: TTFT={ttft * 1000:.1f}ms, Prefill={prefill_speed:.2f} t/s, Gen={generation_speed:.2f} t/s"
                )
                if "Full Prefill" in name:
                    print("  Sleeping 10 seconds to let GPU cool down...")
                    time.sleep(10)

    # Compile report
    print("\n===================================================")
    print("=== CHAT BENCHMARK RESULTS SUMMARY ===")
    print("===================================================")
    print(f"Context File:      {context_file}")

    # Phase 0 Summary
    print("\n--- Phase 0: Warmup ---")
    print(f"  Prompt Tokens:        {prompt_tokens_p0}")
    print(f"  Completion Tokens:    {completion_tokens_p0}")
    print(f"  TTFT (Prefill):       {ttft_p0 * 1000:.2f} ms")
    print(f"  Prefill Speed:        {prefill_speed_p0:.2f} tokens/sec")
    print(f"  Generation Speed:     {generation_speed_p0:.2f} tokens/sec")

    # Phase 1 Summary
    print("\n--- Phase 1: Sequential Prefill ---")
    if not skip_prefill:
        avg_p1_duration = (
            sum(phase1_durations) / len(phase1_durations) if phase1_durations else 0.0
        )
        avg_p1_speed = sum(phase1_speeds) / len(phase1_speeds) if phase1_speeds else 0.0
        print(f"  Cycles:               {len(phase1_durations)}")
        print(f"  Avg Cycle Prefill Time: {avg_p1_duration:.2f} s")
        print(f"  Avg New Chunk Prefill Speed: {avg_p1_speed:.2f} tokens/sec")
    else:
        print("  SKIPPED")

    # Phase 2 Summary
    avg_p2_ttft = sum(x["ttft"] for x in phase2_runs) / len(phase2_runs)
    avg_p2_gen_time = sum(x["generation_time"] for x in phase2_runs) / len(phase2_runs)
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

    print("\n--- Phase 2: Generation (300-word summary) ---")
    print(f"  Runs:                 {repeats}")
    print(f"  Prompt Tokens:        {avg_p2_prompt_tokens}")
    print(f"  Avg Completion Tokens: {avg_p2_comp_tokens:.1f}")
    print(f"  Avg TTFT (Prefill):   {avg_p2_ttft * 1000:.2f} ms")
    print(f"  Avg Prefill Speed:    {avg_p2_prefill_speed:.2f} tokens/sec")
    print(f"  Avg Generation Speed: {avg_p2_gen_speed:.2f} tokens/sec")
    print(f"  Avg Decode Time:      {avg_p2_gen_time:.2f} s")
    print("\n--- Summary Snippet (Run 1) ---")
    print(generated_text.strip()[:350] + "...")

    # Phase 3 Summary
    if run_phase3:
        print("\n--- Phase 3: Prefix Caching & Distractor (Averages over 5 Cycles) ---")
        for name in phase3_results:
            runs = phase3_results[name]
            avg_ttft = sum(x["ttft"] for x in runs) / len(runs)
            avg_prefill = sum(x["prefill_speed"] for x in runs) / len(runs)
            avg_gen = sum(x["generation_speed"] for x in runs) / len(runs)
            last_answer = runs[-1]["answer"]
            print(f"  {name}:")
            print(f"    Avg TTFT:           {avg_ttft * 1000:.2f} ms")
            print(f"    Avg Prefill Speed:  {avg_prefill:.2f} tokens/sec")
            print(f"    Avg Gen Speed:      {avg_gen:.2f} tokens/sec")
            print(f'    Last Answer:        "{last_answer}"')
    else:
        print("\n--- Phase 3: Prefix Caching & Distractor ---")
        print("  SKIPPED")
    print("===================================================\n")


def run_llm_embed(url: str, model: str, context_file: str, repeats: int) -> None:
    """Run embedding benchmark using a large context by chunking it to fit batch size."""
    if not os.path.exists(context_file):
        raise FileNotFoundError(f"Context file not found: {context_file}")

    with open(context_file, "r", encoding="utf-8") as f:
        context_content = f.read()

    # Split text into chunks of 1500 characters (~400 tokens) to stay within physical batch size
    chunk_size = 1500
    chunks = [
        context_content[i : i + chunk_size]
        for i in range(0, len(context_content), chunk_size)
    ]
    # Limit to 20 chunks for a fast but representative benchmark
    chunks = [c for c in chunks if c.strip()][:20]

    print(f"Running embedding benchmark with {repeats} repeats...")
    durations = []
    tokens_list = []
    speeds = []

    for r in range(repeats):
        print(
            f"  [Repeat {r + 1}/{repeats}] Sending {len(chunks)} embedding requests sequentially..."
        )
        total_tokens = 0
        t0 = time.perf_counter()
        for idx, chunk in enumerate(chunks):
            payload = {
                "model": model,
                "input": chunk + f" [r{r}]",
            }
            resp = post_json(f"{url}/v1/embeddings", payload)
            usage = resp.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            if prompt_tokens == 0:
                prompt_tokens = int(len(chunk) / 3.8)
            total_tokens += prompt_tokens
        t1 = time.perf_counter()

        duration_ms = (t1 - t0) * 1000.0
        speed = (total_tokens / (duration_ms / 1000.0)) if duration_ms > 0 else 0.0

        durations.append(duration_ms)
        tokens_list.append(total_tokens)
        speeds.append(speed)
        print(
            f"    Completed repeat {r + 1}: {duration_ms:.2f} ms ({speed:.2f} tokens/sec)"
        )

    avg_duration = sum(durations) / len(durations)
    avg_tokens = sum(tokens_list) / len(tokens_list)
    avg_speed = sum(speeds) / len(speeds)

    print("\n=== Embedding Benchmark Results (Cumulative Average) ===")
    print(f"Context File:      {context_file}")
    print(f"Repeats:           {repeats}")
    print(f"Total Chunks:      {len(chunks)}")
    print(f"Avg Tokens/Run:    {avg_tokens:.1f}")
    print(f"Avg Time/Run:      {avg_duration:.2f} ms")
    print(f"Avg Speed:         {avg_speed:.2f} tokens/sec")
    print("========================================================\n")


def run_rerank(url: str, model: str, context_file: str, repeats: int) -> None:
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

    print(f"Running rerank benchmark with {repeats} repeats...")
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
        print(
            f"    Completed repeat {r + 1}: {duration:.2f} ms ({tokens_per_sec:.2f} tokens/sec)"
        )

    avg_duration = sum(durations_ms) / len(durations_ms)
    avg_docs_speed = sum(docs_speeds) / len(docs_speeds)
    avg_tokens_speed = sum(tokens_speeds) / len(tokens_speeds)

    print("\n=== Rerank Benchmark Results (Cumulative Average) ===")
    print(f"Query:             {query}")
    print(f"Number of Docs:    {len(chunks)}")
    print(f"Repeats:           {repeats}")
    print(f"Total Chars:       {total_chars}")
    print(f"Estimated Tokens:  {estimated_tokens}")
    print(f"Avg Reranking Time:{avg_duration:.2f} ms")
    print(f"Avg Docs Throughput:{avg_docs_speed:.2f} docs/sec")
    print(f"Avg Token Speed:   {avg_tokens_speed:.2f} tokens/sec")
    results = resp.get("results", [])
    if results:
        print("--- Top 3 Results (Last Run) ---")
        for i, r_item in enumerate(results[:3]):
            idx = r_item.get("index", 0)
            score = r_item.get("relevance_score", 0.0)
            text_snippet = chunks[idx].strip()[:100].replace("\n", " ")
            print(f"  {i + 1}. Index {idx:02d} (Score: {score:.4f}): {text_snippet}...")
    print("=====================================================\n")


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


def run_tts(url: str, model: str, output_wav: str, repeats: int) -> None:
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
        "voice": "default",
        "response_format": "wav",
    }

    print(f"Running text-to-speech benchmark with {repeats} repeats...")
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
        print(
            f"    Completed repeat {r + 1}: {synthesis_duration:.2f}s (RTF: {rtf:.4f})"
        )

    avg_duration = sum(durations) / len(durations)
    avg_rtf = sum(rtfs) / len(rtfs)
    avg_char_speed = sum(char_speeds) / len(char_speeds)
    avg_word_speed = sum(word_speeds) / len(word_speeds)
    audio_len = parse_wav_duration(output_wav)

    print("\n=== Text-to-Speech Benchmark Results (Cumulative Average) ===")
    print(f"Sentence:          {text}")
    print(f"Sentence Length:   45 words / {len(text)} chars")
    print(f"Repeats:           {repeats}")
    print(f"Audio Duration:    {audio_len:.2f} seconds")
    print(f"Avg Synthesis Time:{avg_duration:.2f} seconds")
    print(f"Avg RTF:           {avg_rtf:.4f} (RTF < 1 is faster than real-time)")
    print(
        f"Avg Speed:         {avg_char_speed:.2f} chars/sec ({avg_word_speed:.2f} words/sec)"
    )
    print("=============================================================\n")


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


def run_stt(url: str, model: str, audio_file: str, repeats: int) -> None:
    """Trim audio file to 45 seconds using ffmpeg, transcribe, and measure RTF."""
    if not os.path.exists(audio_file):
        raise FileNotFoundError(f"Input audio file not found: {audio_file}")

    print(f"Trimming {audio_file} to 45 seconds (16kHz, mono WAV)...")
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

        print(f"Running speech-to-text benchmark with {repeats} repeats...")
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
            print(f"    Completed repeat {r + 1}: {duration:.2f}s (RTF: {rtf:.4f})")

        avg_duration = sum(durations) / len(durations)
        avg_rtf = sum(rtfs) / len(rtfs)

        print("\n=== Speech-to-Text Benchmark Results (Cumulative Average) ===")
        print(f"Source Audio:      {audio_file}")
        print(f"Repeats:           {repeats}")
        print("Trimmed Segment:   45.0 seconds")
        print(f"Avg Transcribe Time:{avg_duration:.2f} seconds")
        print(f"Avg RTF:           {avg_rtf:.4f} (RTF < 1 is faster than real-time)")
        print("\n--- Transcription Snippet (Repeat 1) ---")
        print(text[:300] + ("..." if len(text) > 300 else ""))
        print("=============================================================\n")

    finally:
        if os.path.exists(temp_wav_path):
            os.remove(temp_wav_path)


def main() -> None:
    """Parse args and dispatch benchmark execution."""
    parser = argparse.ArgumentParser(
        description="Benchmark helper for local LLM, Embeddings, Reranker, TTS, and STT."
    )
    parser.add_argument(
        "--mode",
        choices=["llm-chat", "llm-embed", "rerank", "tts", "stt"],
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
        "--output",
        default=None,
        help="Path to save output synthesized speech (for text-to-speech)",
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
        help="Skip Phase 1 sequential prefill",
    )
    parser.add_argument(
        "--skip-distractor",
        action="store_true",
        help="Skip Phase 3 prefix caching & distractor tests",
    )

    args = parser.parse_args()

    repeats = (
        args.repeat
        if args.repeat is not None
        else (10 if args.mode in ("llm-embed", "stt") else 1)
    )

    output_path = args.output
    if output_path is None:
        output_path = os.path.join(get_tmp_dir(), "tts_benchmark_output.wav")

    if args.mode == "llm-chat":
        if not args.context:
            parser.error("--context is required in llm-chat mode")
        run_llm_chat(
            args.url,
            args.model,
            args.context,
            repeats,
            skip_prefill=args.skip_prefill,
            skip_distractor=args.skip_distractor,
        )
    elif args.mode == "llm-embed":
        if not args.context:
            parser.error("--context is required in llm-embed mode")
        run_llm_embed(args.url, args.model, args.context, repeats)
    elif args.mode == "rerank":
        if not args.context:
            parser.error("--context is required in rerank mode")
        run_rerank(args.url, args.model, args.context, repeats)
    elif args.mode == "tts":
        run_tts(args.url, args.model, output_path, repeats)
    elif args.mode == "stt":
        if not args.audio:
            parser.error("--audio is required in stt mode")
        run_stt(args.url, args.model, args.audio, repeats)


if __name__ == "__main__":
    main()
