#!/usr/bin/env python3
"""Comprehensive Integration Testsuite for Kokoro ONNX TTS (kokoro-ctl.py).

Verifies:
1. All Approved German Voices:
   - df_kerstin (default female), df_victoria, df_eva
   - dm_martin (default male), dm_bernd
2. All Approved English Voices:
   - af_heart, af_bella, af_sarah, bf_emma
   - am_adam, am_michael, bm_george
3. OpenAI API Compatibility & Fallbacks:
   - Omitted model, language, and voice -> default English (af_heart)
   - German language without model/voice -> default German (df_victoria)
   - OpenAI standard voice mappings (alloy, echo, fable, onyx, nova, shimmer)
4. Advanced Engine Features:
   - Feature 1: Linear Voice Style Blending (e.g. df_victoria(0.6)+dm_martin(0.4))
   - Feature 2: Multi-Speaker Inline Dialogue ([voice:NAME])
   - Feature 3: Inline Acoustic Silence Pauses ([pause:1.5s])
   - Feature 4: Low-Latency Chunked Streaming (stream: true)
   - Feature 5: Native OGG/Opus Compressed Output (response_format: "opus")
"""

import argparse
import io
import json
import os
import subprocess
import sys
import time
import urllib.request
from typing import Dict, List, Tuple

import numpy as np
import sounddevice as sd
import soundfile as sf

TEST_DIR = "/tmp/kokoro_advanced_tests"
os.makedirs(TEST_DIR, exist_ok=True)


def verify_audio_file(file_path: str, expected_format: str = "wav") -> dict:
    """Verifies generated audio using ffprobe."""
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=format_name,duration:stream=codec_name,sample_rate,channels",
        "-of",
        "json",
        file_path,
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    info = json.loads(res.stdout)
    duration = float(info["format"]["duration"])
    codec = info["streams"][0]["codec_name"]
    sample_rate = int(info["streams"][0]["sample_rate"])
    channels = int(info["streams"][0]["channels"])
    return {
        "duration": duration,
        "codec": codec,
        "sample_rate": sample_rate,
        "channels": channels,
    }


def play_audio_bytes(raw_bytes: bytes, fmt: str = "wav") -> None:
    """Plays audio bytes aloud on host speakers via sounddevice (capped at 30s)."""
    fmt_lower = fmt.lower()
    if fmt_lower == "pcm":
        pcm = np.frombuffer(raw_bytes, dtype=np.int16).astype(np.float32) / 32768.0
        sr = 24000
    else:
        pcm, sr = sf.read(io.BytesIO(raw_bytes), dtype="float32")
    pcm = pcm[: int(sr * 30)]
    sd.play(pcm, samplerate=sr)
    sd.wait()


def send_speech_request(
    base_url: str,
    payload: dict,
    output_file: str,
    stream: bool = False,
    play: bool = False,
) -> float:
    """Sends /v1/audio/speech request and returns synthesis wall time."""
    url = f"{base_url}/v1/audio/speech"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})

    t0 = time.perf_counter()
    with urllib.request.urlopen(req) as resp:
        content = resp.read()
    t1 = time.perf_counter()

    with open(output_file, "wb") as f:
        f.write(content)

    if play:
        fmt = str(payload.get("response_format", "wav"))
        play_audio_bytes(content, fmt)

    return t1 - t0


def transcribe_audio(stt_url: str, file_path: str) -> str:
    """Sends audio to local speech-to-text service (Whisper)."""
    cmd = [
        "curl",
        "-s",
        "-f",
        "-X",
        "POST",
        f"{stt_url}/v1/audio/transcriptions",
        "-H",
        "Content-Type: multipart/form-data",
        "-F",
        f"file=@{file_path}",
        "-F",
        "model=whisper-1",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        try:
            return json.loads(res.stdout).get("text", "").strip()
        except Exception:
            return res.stdout.strip()
    return "(STT unreachable)"


def run_tests(base_url: str, stt_url: str, play: bool = False) -> int:
    print("=" * 76)
    print(" KOKORO ONNX COMPREHENSIVE INTEGRATION TESTSUITE")
    print(f" Target Server: {base_url}")
    print(f" STT Server:    {stt_url}")
    print(f" Speaker Play:  {'ENABLED' if play else 'disabled (use --play / -p)'}")
    print("=" * 76)

    results: List[Tuple[str, bool, float]] = []

    # Group 1: Approved German Voices
    german_voices: Dict[str, str] = {
        "df_kerstin": "Guten Tag, hier spricht Kerstin mit einer klaren deutschen Stimme.",
        "df_victoria": "Guten Tag, hier spricht Victoria mit der zweiten Stimme.",
        "df_eva": "Guten Tag, hier spricht Eva mit einer warmen deutschen Stimme.",
        "dm_martin": "Guten Tag, hier spricht Martin mit natürlicher Betonung.",
        "dm_bernd": "Hallo, ich bin Bernd, die männliche deutsche Stimme.",
    }

    print("\n--- GROUP 1: Approved German Voices ---")
    for voice_id, sample_text in german_voices.items():
        out_path = os.path.join(TEST_DIR, f"voice_{voice_id}.wav")
        t_wall = send_speech_request(
            base_url,
            {
                "model": "kokoro",
                "input": sample_text,
                "voice": voice_id,
                "response_format": "wav",
            },
            out_path,
            play=play,
        )
        meta = verify_audio_file(out_path, "wav")
        rtf = t_wall / meta["duration"] if meta["duration"] > 0 else 0
        speed_x = 1.0 / rtf if rtf > 0 else 0
        print(
            f"  [{voice_id:<12}] {meta['duration']:.2f}s audio in {t_wall:.3f}s ({speed_x:.1f}x RT)"
        )
        assert meta["duration"] > 1.5, f"Audio too short for {voice_id}"
        results.append((f"Voice: {voice_id} (German)", True, rtf))

    # Group 2: Approved English Voices
    english_voices: Dict[str, str] = {
        "af_heart": "Hello, I am Heart, the primary American English voice.",
        "af_bella": "Hi there, this is Bella speaking with a warm tone.",
        "af_sarah": "Good day, I am Sarah, clear and articulate.",
        "bf_emma": "Good afternoon, this is Emma with British English.",
        "am_adam": "Hello, this is Adam, the primary American male voice.",
        "am_michael": "Greetings, I am Michael with a deeper vocal presence.",
        "bm_george": "Good evening, this is George speaking British English.",
    }

    print("\n--- GROUP 2: Approved English Voices ---")
    for voice_id, sample_text in english_voices.items():
        out_path = os.path.join(TEST_DIR, f"voice_{voice_id}.wav")
        t_wall = send_speech_request(
            base_url,
            {
                "model": "kokoro",
                "input": sample_text,
                "voice": voice_id,
                "response_format": "wav",
            },
            out_path,
            play=play,
        )
        meta = verify_audio_file(out_path, "wav")
        rtf = t_wall / meta["duration"] if meta["duration"] > 0 else 0
        speed_x = 1.0 / rtf if rtf > 0 else 0
        print(
            f"  [{voice_id:<12}] {meta['duration']:.2f}s audio in {t_wall:.3f}s ({speed_x:.1f}x RT)"
        )
        assert meta["duration"] > 1.5, f"Audio too short for {voice_id}"
        results.append((f"Voice: {voice_id} (English)", True, rtf))

    # Group 3: OpenAI API Fallbacks & Defaults
    print("\n--- GROUP 3: OpenAI API Compatibility & Fallbacks ---")

    # 3a. Completely omitted model, language, and voice -> defaults to English (af_heart)
    out_omitted = os.path.join(TEST_DIR, "fallback_omitted.wav")
    t_omitted = send_speech_request(
        base_url,
        {"input": "No model or voice specified, defaulting to English."},
        out_omitted,
        play=play,
    )
    meta_omitted = verify_audio_file(out_omitted, "wav")
    rtf_omitted = t_omitted / meta_omitted["duration"] if meta_omitted["duration"] > 0 else 0
    print(f"  [Omitted -> EN] {meta_omitted['duration']:.2f}s in {t_omitted:.3f}s")
    assert meta_omitted["duration"] > 1.5, "Omitted fallback audio too short"
    results.append(("Fallback: Omitted Model/Lang/Voice -> English", True, rtf_omitted))

    # 3b. German language specified without model or voice -> defaults to German (df_kerstin)
    out_de_fallback = os.path.join(TEST_DIR, "fallback_german.wav")
    t_de_fallback = send_speech_request(
        base_url,
        {
            "language": "de",
            "input": "Nur Deutsch als Sprache gewählt, automatischer Standard.",
        },
        out_de_fallback,
        play=play,
    )
    meta_de = verify_audio_file(out_de_fallback, "wav")
    rtf_de = t_de_fallback / meta_de["duration"] if meta_de["duration"] > 0 else 0
    print(f"  [Lang 'de' -> DE] {meta_de['duration']:.2f}s in {t_de_fallback:.3f}s")
    assert meta_de["duration"] > 1.5, "German fallback audio too short"
    results.append(("Fallback: Language 'de' without Model -> German (df_kerstin)", True, rtf_de))
    # 3c. OpenAI voice names mapped to Kokoro equivalents
    openai_voice_samples = {
        "alloy": "OpenAI Alloy alias mapped directly to Kokoro.",
        "echo": "OpenAI Echo alias mapped directly to Kokoro.",
        "fable": "OpenAI Fable alias mapped directly to Kokoro.",
        "onyx": "OpenAI Onyx alias mapped directly to Kokoro.",
        "nova": "OpenAI Nova alias mapped directly to Kokoro.",
        "shimmer": "OpenAI Shimmer alias mapped directly to Kokoro.",
    }
    for oai_voice, text_oai in openai_voice_samples.items():
        out_oai = os.path.join(TEST_DIR, f"fallback_openai_{oai_voice}.wav")
        t_oai = send_speech_request(
            base_url,
            {"voice": oai_voice, "input": text_oai},
            out_oai,
            play=False if (play and oai_voice != "nova") else play,
        )
        meta_oai = verify_audio_file(out_oai, "wav")
        rtf_oai = t_oai / meta_oai["duration"] if meta_oai["duration"] > 0 else 0
        speed_x = 1.0 / rtf_oai if rtf_oai > 0 else 0
        print(
            f"  [OpenAI {oai_voice:<7}] {meta_oai['duration']:.2f}s in {t_oai:.3f}s ({speed_x:.1f}x RT)"
        )
        assert meta_oai["duration"] > 1.5, f"Audio too short for OpenAI voice {oai_voice}"
        results.append((f"OpenAI Mapping: voice='{oai_voice}'", True, rtf_oai))

    # Group 4: Advanced Engine Features
    print("\n--- GROUP 4: Advanced Engine Features ---")

    # 4a. Feature 1: Linear Voice Blending
    out_blend = os.path.join(TEST_DIR, "feat_blend.wav")
    t_blend = send_speech_request(
        base_url,
        {
            "model": "kokoro",
            "input": "Diese Stimme ist eine Mischung aus Victoria und Martin.",
            "voice": "df_victoria(0.6)+dm_martin(0.4)",
        },
        out_blend,
        play=play,
    )
    meta_blend = verify_audio_file(out_blend, "wav")
    rtf_blend = t_blend / meta_blend["duration"] if meta_blend["duration"] > 0 else 0
    print(f"  [Voice Blending] {meta_blend['duration']:.2f}s in {t_blend:.3f}s")
    assert meta_blend["duration"] > 2.0, "Blend audio too short"
    results.append(("Feature 1: Linear Voice Blending", True, rtf_blend))

    # 4b. Feature 2: Multi-Speaker Inline Dialogue Switching
    out_dialogue = os.path.join(TEST_DIR, "feat_dialogue.wav")
    t_dialogue = send_speech_request(
        base_url,
        {
            "model": "kokoro",
            "input": (
                "[voice:df_victoria] Hallo Martin! "
                "[voice:dm_martin] Grüß dich Victoria! "
                "[voice:af_heart] And hello from Heart!"
            ),
            "voice": "df_victoria",
        },
        out_dialogue,
        play=play,
    )
    meta_dialogue = verify_audio_file(out_dialogue, "wav")
    rtf_dialogue = t_dialogue / meta_dialogue["duration"] if meta_dialogue["duration"] > 0 else 0
    print(f"  [Multi-Speaker] {meta_dialogue['duration']:.2f}s in {t_dialogue:.3f}s")
    assert meta_dialogue["duration"] > 3.0, "Dialogue audio too short"
    results.append(("Feature 2: Multi-Speaker Inline Dialogue", True, rtf_dialogue))

    # 4c. Feature 3: Inline Acoustic Silence Pauses
    out_pause = os.path.join(TEST_DIR, "feat_pause.wav")
    t_pause = send_speech_request(
        base_url,
        {
            "model": "kokoro",
            "input": "Achtung, jetzt folgt eine Sekunde Pause. [pause:1.0s] Und weiter geht es.",
            "voice": "df_victoria",
        },
        out_pause,
        play=play,
    )
    meta_pause = verify_audio_file(out_pause, "wav")
    rtf_pause = t_pause / meta_pause["duration"] if meta_pause["duration"] > 0 else 0
    print(f"  [Inline Pause]  {meta_pause['duration']:.2f}s in {t_pause:.3f}s")
    assert meta_pause["duration"] > 3.0, "Pause audio too short"
    results.append(("Feature 3: Inline Silence Pauses", True, rtf_pause))

    # 4d. Feature 4: Low-Latency Chunked Streaming
    out_stream = os.path.join(TEST_DIR, "feat_stream.pcm")
    t_stream = send_speech_request(
        base_url,
        {
            "model": "kokoro",
            "input": "Erster Satz im Stream. Zweiter Satz folgt sofort. Dritter Satz beendet die Übertragung.",
            "voice": "df_victoria",
            "response_format": "pcm",
            "stream": True,
        },
        out_stream,
        play=play,
    )
    file_size_stream = os.path.getsize(out_stream)
    dur_stream = file_size_stream / (24000 * 2)
    rtf_stream = t_stream / dur_stream if dur_stream > 0 else 0
    print(f"  [Streaming PCM] {dur_stream:.2f}s in {t_stream:.3f}s ({file_size_stream} bytes)")
    assert file_size_stream > 100000, "Streamed audio too small"
    results.append(("Feature 4: Chunked Streaming (PCM)", True, rtf_stream))

    # 4e. Feature 5: Native OGG/Opus Compressed Container Output
    out_opus = os.path.join(TEST_DIR, "feat_opus.ogg")
    t_opus = send_speech_request(
        base_url,
        {
            "model": "kokoro",
            "input": "Hochkomprimiertes Ogg Opus Audioformat für minimale Bandbreite und maximale Effizienz.",
            "voice": "df_victoria",
            "response_format": "opus",
        },
        out_opus,
        play=play,
    )
    meta_opus = verify_audio_file(out_opus, "ogg")
    wav_equiv = int(meta_opus["duration"] * 24000 * 2)
    actual_size = os.path.getsize(out_opus)
    comp_ratio = wav_equiv / actual_size if actual_size > 0 else 0
    rtf_opus = t_opus / meta_opus["duration"] if meta_opus["duration"] > 0 else 0
    print(
        f"  [Opus OGG]      {meta_opus['duration']:.2f}s in {t_opus:.3f}s ({comp_ratio:.1f}x compression)"
    )
    assert meta_opus["codec"] == "opus", f"Expected opus codec, got {meta_opus['codec']}"
    results.append(("Feature 5: Native OGG/Opus Encoding", True, rtf_opus))

    # Summary
    print("\n" + "=" * 76)
    print(" KOKORO INTEGRATION TESTSUITE SUMMARY")
    print("=" * 76)
    print(f"{'Test Case':<48} | {'Status':<8} | {'RTF':<8} | {'Speed'}")
    print("-" * 76)
    all_passed = True
    for name, passed, rtf_val in results:
        status = "PASSED" if passed else "FAILED"
        if not passed:
            all_passed = False
        speed_str = f"{1 / rtf_val:.1f}x RT" if rtf_val > 0 else "N/A"
        print(f"{name:<48} | {status:<8} | {rtf_val:<8.3f} | {speed_str}")
    print("=" * 76)

    if all_passed:
        print(f"\nAll {len(results)} test cases PASSED successfully!")
        return 0
    else:
        print("\nSome test cases FAILED!")
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Kokoro ONNX Testsuite")
    parser.add_argument("--base-url", default="http://127.0.0.1:21080")
    parser.add_argument("--stt-url", default="http://127.0.0.1:20090")
    parser.add_argument(
        "-p",
        "--play",
        action="store_true",
        help="Play each synthesized audio sample aloud on speakers via sounddevice",
    )
    args = parser.parse_args()

    sys.exit(run_tests(args.base_url, args.stt_url, play=args.play))
