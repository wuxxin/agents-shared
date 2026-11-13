# Local Text-to-Speech Management Guide

`local-text-to-speech.sh` manages local text-to-speech (TTS) voice synthesis services. It supports two switchable backend engines exposing an OpenAI-compatible audio generation endpoint (`/v1/audio/speech`):
1. **`kokoro`** (Default): Fast ONNX Runtime CPU inference (`scripts/kokoro-ctl.py`) with AVX2 MLAS acceleration, C API `libespeak-ng.so`, and in-process audio playback via `python-sounddevice`. Generates German (`df_victoria`, `dm_martin`) and all 55 official multilingual voices at **4.6× real-time** with **0 MB VRAM** and ~350 MB host RAM.
2. **`qwen3`**: Runs `qwen3-tts-server` (C++ GGML backend) loading Qwen3-TTS and WavTokenizer GGUF models with CPU, Vulkan, and ROCm/HIP support.

- **Source Code**:
  - Kokoro-82M ONNX: [Hugging Face - hexgrad/Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M)
  - Qwen3-TTS C++: [GitHub - khimaros/qwen3-tts.cpp](https://github.com/khimaros/qwen3-tts.cpp)
  - kokoro.cpp (Vulkan/CPU GGML): [GitHub - simonfxr/kokoro.cpp](https://github.com/simonfxr/kokoro.cpp)
- **Arch/AUR Packages**:
  - `python-onnxruntime` + `python-sounddevice` + `python-soundfile` + `python-fastapi` + `python-uvicorn` + `espeak-ng` (system Arch packages for Kokoro ONNX)
  - `python-gguf` (AUR) + `python-safetensors` (Arch official repo) for offline voice conversion
  - `qwen3-tts.cpp-git-ggml-hip` (in `aur-packages/libggml-git-hip` for Qwen3)
## Usage

| Command | Description |
|---|---|
| `install [--no-start] [--new-config]` | Sets up the service, generates default configuration env file (does not start if `--no-start` is specified, force overwrites with defaults if `--new-config` is specified). |
| `uninstall` | Stops and removes the service. |
| `edit` | Edit model selection and server parameters. |
| `logs [args...]` | View the synthesis server output. Pass `-f` to tail/follow. Supports any `journalctl` options. |
| `exec [--env KEY=VAL]*` | Run `qwen3-tts-server` as a transient systemd user service with identical GPU sandbox settings. |
| `run [--env KEY=VAL]* <cmd>` | Run a custom command inside the text-to-speech sandbox environment. |
| `shell [--env KEY=VAL]*` | Spawn an interactive shell in the speech sandbox (useful for manual testing). |
| `test` | Run API validation tests (synthesizes speech and transcribes it back). |

### In-Memory Environment Overrides

The `exec`, `run`, and `shell` subcommands support a repeatable `--env KEY=VALUE` parameter. When passed, these parameters:
1. Override the values loaded from the `.env` configuration file on disk.
2. Are exported in the local shell environment in-memory for foreground execution.
3. Are dynamically passed to `systemd-run` via `--setenv=KEY=VALUE` for transient background runs in systemd.

These overrides are kept transient, keeping the main `.env` configuration file untouched. For example, to run the server temporarily on CPU without changing your permanent configuration:
```bash
./local-text-to-speech.sh exec --env LTTS_MODE=cpu
```

## Architecture

The service routes requests to either `kokoro-ctl.py` (Kokoro ONNX) or `qwen3-tts-server` (Qwen3-TTS) based on the configured `LTTS_ENGINE`. Both engines serve an OpenAI-compatible REST API on port `20095`.
### Endpoints (all on port 20095)

| Endpoint | Purpose |
|---|---|
| `/v1/audio/speech` | OpenAI-compatible text-to-speech API (supports `wav`, `pcm`, `ogg`, `opus`, and `stream: true`) |
| `/v1/audio/voices` | Returns all available voice style IDs |
| `/v1/audio/voices/combine` | Creates or queries a combined/blended voice style definition |
| `/health` | Health check reporting loaded voices, formats, and active features |

### Kokoro Advanced Serving Features

The Kokoro engine (`scripts/kokoro-ctl.py`) includes advanced speech synthesis features:

#### 1. Voice Blending / Adaptation
Blend two or more voice style embeddings with custom weights:
```json
{
  "model": "kokoro",
  "input": "Diese synthetische Stimme ist eine Mischung aus Kerstin und Martin.",
  "voice": "df_kerstin(0.6)+dm_martin(0.4)"
}
```
You can also call `POST /v1/audio/voices/combine` with `{"voices": ["df_kerstin", "dm_martin"], "weights": [0.6, 0.4]}`.

#### 2. Multi-Speaker Inline Dialogue (`[voice:...]`)
Switch speakers mid-utterance within a single request:
```json
{
  "model": "kokoro",
  "input": "[voice:df_kerstin] Guten Morgen Martin! [voice:dm_martin] Hallo Kerstin, ein wunderschöner Tag heute. [voice:af_heart] And hello from America!",
  "voice": "df_kerstin"
}
```
Each segment automatically switches phonemizer language and voice embedding.

#### 3. Inline Silence / Pause Tags (`[pause:...]`)
Insert explicit acoustic pauses anywhere in the text:
```json
{
  "model": "kokoro",
  "input": "Erster Satz vor der Pause. [pause:1.5s] Zweiter Satz nach anderthalb Sekunden Stille."
}
```
Supports seconds (e.g. `[pause:1.5s]`) and milliseconds (e.g. `[pause:500ms]`).

#### 4. Chunked Low-Latency Streaming (`stream: true`)
Receive audio chunks as each sentence finishes synthesizing:
```json
{
  "model": "kokoro",
  "input": "Erster Satz im Stream. Zweiter Satz folgt sofort. Dritter Satz beendet die Übertragung.",
  "stream": true,
  "response_format": "pcm"
}
```
Time-to-first-audio drops to **< 250 ms**.

#### 5. OGG/Opus Compressed Audio Output (`response_format: "opus"`)
Generate high-fidelity compressed audio for low-bandwidth transfer:
```json
{
  "model": "kokoro",
  "input": "Hochkomprimiertes Ogg Opus Audioformat für minimale Bandbreite.",
  "response_format": "opus"
}
```
Achieves **> 10× compression** relative to uncompressed 16-bit PCM WAV.

#### 6. OpenAI API Fallback Cascades & Language Resolution
To ensure seamless drop-in compatibility with OpenAI client libraries that may omit `model`, `voice`, or `language`:
- **Omitted Model & Language**: Defaults to English using `LTTS_DEFAULT_VOICE_EN` (`af_heart`).
- **German Language (`language: "de"` or `"german"`)**: Automatically selects the default German voice `LTTS_DEFAULT_VOICE_DE` (`df_victoria`) even if `model` is omitted.
- **OpenAI Standard Voice Mappings**: Standard OpenAI voice names map directly to their Kokoro counterparts:
  - `alloy` $\rightarrow$ `af_alloy`
  - `echo` $\rightarrow$ `am_echo`
  - `fable` $\rightarrow$ `bm_fable`
  - `onyx` $\rightarrow$ `am_onyx`
  - `nova` $\rightarrow$ `af_nova`
  - `shimmer` $\rightarrow$ `af_sarah`

These defaults can be customized in `~/.config/systemd/user/local-text-to-speech.env`:
```bash
LTTS_DEFAULT_VOICE_EN="af_heart"
LTTS_DEFAULT_VOICE_DE="df_victoria"
LTTS_DEFAULT_LANGUAGE="en"
```
### Approved High-Quality Voice Lineup

The following voice profiles have been auditioned, benchmarked, and verified for production use:

| Voice ID | Language / Gender | Provenance & Character | Recommended Use Case |
| :--- | :--- | :--- | :--- |
| **`dm_martin`** | German Male | Martin Harbecke, Kokoro Stage-2 HUI corpus fine-tune (Godelaune / dida-80b). Natural, accent-free German. | Primary German male voice for assistant conversations. |
| **`dm_heinrich`** | German Male | Heinrich, trained from scratch on German HUI corpus (junkstage/kikiri-de). Crisp, native German male timbre. | Alternative German male voice. |
| **`df_victoria`** | German Female | Victoria, Kikiri Kokoro Stage-2 HUI corpus fine-tune. Natural German prosody. | Primary German female voice. |
| **`df_anna`** | German Female | Anna, trained from scratch on German HUI corpus (junkstage/kikiri-de). Natural, accent-free German female voice. | Alternative German female voice. |
| **`df_kerstin`** | German Female | Kerstin German fine-tune. Consistent pacing across mixed phrasing. | Secondary German female voice. |
| **`af_heart`** | English Female | Official Kokoro-82M reference voice. Clear, friendly American English female timbre. | Primary English female voice. |
| **`af_bella`** | English Female | Official Kokoro-82M American female voice. Warm, natural vocal delivery. | Secondary English female voice (warm timbre). |
| **`af_sarah`** | English Female | Official Kokoro-82M American female voice. Professional, clear midrange articulation. | Secondary English female voice (articulate). |
| **`bf_emma`** | English Female | Official Kokoro-82M British female voice. Clear, polished British English articulation. | Primary British English female voice. |
| **`am_adam`** | English Male | Official Kokoro-82M American male voice. Mid-range, articulate, clear cadence. | Primary English male voice. |
| **`am_michael`** | English Male | Official Kokoro-82M American male voice. Deeper, warmer vocal presence. | Secondary English male voice. |
| **`bm_george`** | English Male | Official Kokoro-82M British male voice. Polished, refined British English articulation. | Primary British English male voice. |

> **Note on External References**: Piper Thorsten (`thorsten-high`) is retained strictly as an external reference baseline for acoustic comparison, and is not bundled or routed inside the `local-text-to-speech` service.


### Configuration Files

| File | Purpose |
|---|---|
| `~/.config/systemd/user/local-text-to-speech.env` | Model paths, port, host, and thread configuration |
| `~/.config/systemd/user/local-text-to-speech.service` | Auto-generated systemd unit |

#### Default Language for Speech Generation

If not supplied by request, the default language generated is "en" (english).

To set a different default language eg. german (de) use:

```bash
LTTS_EXTRA_ARGS="--language de"
```

Info: the --language parameter is only available in the patched libggml-git-hip qwen3-tts binary.

### Available Voices

When running the local text-to-speech service with the default custom voice model (`Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`), you can query the available voices via the `/v1/audio/voices` endpoint:

```bash
curl -s http://127.0.0.1:20095/v1/audio/voices
```

This returns the active voice presets loaded by the model. The table below lists the characteristics and native pronunciation/dialect profiles of these voices:

| Voice | Gender | Native Language / Dialect | Accent & Description |
| :--- | :--- | :--- | :--- |
| `default` | - | - | Default speaker (general/neutral) |
| `serena` | Female | Chinese (Standard Mandarin) | Warm, gentle, young female voice |
| `vivian` | Female | Chinese (Standard Mandarin) | Bright, slightly edgy, young female voice |
| `uncle_fu` | Male | Chinese (Standard Mandarin) | Low, mellow, seasoned/mature male voice |
| `ryan` | Male | English (British/General English) | Dynamic with a strong, rhythmic drive |
| `aiden` | Male | English (American English) | Sunny, friendly, American accent with a clear midrange |
| `ono_anna` | Female | Japanese | Playful, light, and nimble Japanese female voice |
| `sohee` | Female | Korean | Warm, soft, gentle Korean female voice with rich emotion |
| `eric` | Male | Chinese (Sichuan dialect) | Lively, slightly husky, bright male voice |
| `dylan` | Male | Chinese (Beijing dialect) | Youthful, clear, natural Beijing-accented male voice |

#### Cross-Language Pronunciation Capabilities

A key feature of Qwen3-TTS is its **cross-language consistency**. Each voice is optimized for and maintains its signature timbre and accent, but is fully capable of pronouncing any of the 10 languages supported by the model (Chinese, English, Japanese, Korean, German, French, Russian, Portuguese, Spanish, and Italian). For example:
- Generating German speech with `serena` outputs German spoken with a gentle female timbre and Chinese-influenced accent traits.
- Generating Chinese speech with `aiden` outputs Chinese spoken with a sunny American-accented timbre.

For optimal pronunciation naturalness, it is recommended to align the input language with the speaker's native language.

### Performance Tuning Presets & Engine Modes

#### 1. Kokoro Engine (`LTTS_ENGINE="kokoro"`)
Kokoro runs via `scripts/kokoro-server.py` using system ONNX Runtime (`libonnxruntime.so.1`) with AVX2 MLAS thread pooling:
- **Zero VRAM Consumption**: Leaves discrete GPU VRAM completely free for large conversational LLMs.
- **High Throughput**: 4.6× real-time synthesis (RTF 0.218) on an 8-core CPU (Ryzen 7 PRO 5750G).
- **Native German & Multilingual Support**: Automatic language mapping by voice prefix (e.g. `df_*`/`dm_*` -> German `de`, `af_*`/`am_*` -> American English `en-us`, `bf_*`/`bm_*` -> British English `en-gb`).
- **Long-Form Sentence Chunking**: Seamless regex-based clause/sentence splitting with 150ms natural pauses, bypassing the 510-token hard limit of Kokoro's PL-BERT encoder.
- **Voice Caching**: In-memory caching of 256-dimensional style embeddings across requests.
- **Thread Tuning**: Configurable with `LTTS_KOKORO_THREADS=8`.

##### Dependencies for Kokoro Server (`scripts/kokoro-server.py`)
All dependencies are available as standard Arch Linux packages:
* **`python`** (>= 3.10)
* **`python-onnxruntime`** (provides `libonnxruntime.so.1` with AVX2 MLAS)
* **`python-fastapi`** & **`python-uvicorn`** (asynchronous REST HTTP serving)
* **`python-soundfile`** & **`python-numpy`** (audio encoding and vector operations)
* **`espeak-ng`** (`/usr/bin/espeak-ng` for IPA phonemization)
* **Model**: `/data/public/machine-learning/models/text-to-speech/Kokoro-82M-v1.0-German-ONNX` (containing `onnx/model.onnx`, `tokenizer.json`, and `voices/*.bin`)
#### 2. Qwen3 Engine (`LTTS_ENGINE="qwen3"`)
The server performance can be optimized using the `LTTS_MODE` environment variable in `local-text-to-speech.env`:
1. **`gpu`**: Runs inference on the ROCm GPU. Keeps both the TTS transformer and the vocoder decoder models warm in VRAM.
2. **`hybrid`** (Performance Sweet Spot): Offloads Code Generation (`TTSTransformer`) to the CPU (`QWEN3_TTS_TRANSFORMER_FORCE_CPU=1`), while running Vocoder Decode on GPU (`ROCm0`).
3. **`cpu`** (Default): Offloads all tensor computations to CPU threads (`LTTS_THREADS=8`).
### Backend Device Selection (Dynamic Backend Loading)

When using a combined backend build (such as `qwen3-tts.cpp-git-ggml-hip`), the service supports dynamic loading of different acceleration backends (CPU, OpenBLAS, Vulkan, and HIP/ROCm) at runtime. 

You can configure the target device using the `LTTS_DEVICE` environment variable. Run `./local-text-to-speech.sh edit` (or edit `~/.config/systemd/user/local-text-to-speech.env` directly) and configure the device:

```bash
# GPU/CPU backend device to use (run 'llama-cli --list-devices' for valid names)
# By default, qwen3-tts-server selects the default available backend.
# To force a specific backend device, uncomment one of the options below:
# LTTS_DEVICE="ROCm0"
# LTTS_DEVICE="Vulkan0"
# LTTS_DEVICE="BLAS"  # Force CPU OpenBLAS acceleration
# LTTS_DEVICE="none"  # Force plain CPU execution (without OpenBLAS)
```


## Models & Repositories

### Kokoro Engine Models
Kokoro models are downloaded via `scripts/local-download.sh --tts`:
- **Kokoro-82M German ONNX (Default)**: [crane-local-ai/Kokoro-82M-v1.0-German-ONNX](https://huggingface.co/crane-local-ai/Kokoro-82M-v1.0-German-ONNX) (Voice: `df_kerstin`, includes all 55 official voices in `voices/`)
- **German HUI GGUF Models**: [cstr/kokoro-de-hui-base-GGUF](https://huggingface.co/cstr/kokoro-de-hui-base-GGUF) (`kokoro-de-hui-base-q8_0.gguf`, `kokoro-de-hui-base-f16.gguf` for kokoro.cpp)
- **German GGUF Voicepack Cascade**: [cstr/kokoro-voices-GGUF](https://huggingface.co/cstr/kokoro-voices-GGUF) (`kokoro-voice-df_victoria.gguf`, `kokoro-voice-dm_martin.gguf`)
- **Multilingual Kokoro GGUF**: [simonfxr/kokoro.cpp-GGUF](https://huggingface.co/simonfxr/kokoro.cpp-GGUF) (`kokoro-82m-q8_0.gguf`)
- **Thorsten Voice German Kokoro**: [Thorsten-Voice/Kokoro](https://huggingface.co/Thorsten-Voice/Kokoro)
- **Martin German ONNX Model**: [miro-dietiker/kokoro-de-martin](https://huggingface.co/miro-dietiker/kokoro-de-martin)
### Qwen3-TTS (GGUF) Engine Models
Pre-converted GGUF models are hosted on the [khimaros/qwen3-tts Collection](https://huggingface.co/collections/khimaros/qwen3-tts):
- **0.6B CustomVoice Model**: `Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`
- **0.6B Base Model**: `Qwen3-TTS-12Hz-0.6B-Base-Q8_0.gguf`
- **1.7B CustomVoice Model**: `Qwen3-TTS-12Hz-1.7B-CustomVoice-Q8_0.gguf`
- **Shared Vocoder**: `Qwen3-TTS-Tokenizer-12Hz-F16.gguf`
## Feature Comparison: Kokoro ONNX vs. kokoro.cpp (simonfxr)

| Feature / Metric | Kokoro ONNX (`scripts/kokoro-ctl.py`) | `kokoro.cpp` (`simonfxr/kokoro.cpp`) |
| :--- | :--- | :--- |
| **Execution Engine** | System ONNX Runtime (`libonnxruntime.so.1` AVX2 MLAS) | `libggml` C++ runtime + Google Highway SIMD |
| **Hardware Backends** | CPU (`CPUExecutionProvider`) | CPU (AVX2), Vulkan (`Vulkan0` APU, `Vulkan1` dGPU), CUDA, Metal |
| **CPU Real-Time Speed** | **4.6× – 5.1× real-time** (RTF ~0.20, 0.75s for 3.5s audio) | **1.73× real-time** (RTF 0.577, 1.86s for 3.22s audio) |
| **Vulkan iGPU Speed** | N/A (ONNX Runtime Linux lacks Vulkan EP) | **2.1× – 3.2× real-time** on Renoir APU (`Vulkan0`) |
| **Vulkan dGPU Speed** | N/A | **4.01× real-time** on RX 7900 XTX (`Vulkan1`) |
| **CPU Load (8 threads)**| ~550% (multithreaded batch) | 592% on CPU; **111% on Vulkan0 APU** (offloaded) |
| **Memory RSS (Host RAM)**| **~350 MB** | **601 MB** on CPU; **205 MB** on Vulkan |
| **dGPU VRAM Footprint** | **0 MB** | **0 MB** on Vulkan0 (APU) / CPU; ~120 MB on Vulkan1 (dGPU) |
| **Serving Protocol** | Native HTTP daemon: `/v1/audio/speech`, `/v1/audio/voices`, `/v1/audio/voices/combine` | CLI utility (`kokoro-cli`); requires external HTTP daemon wrapper |
| **Audio Output** | Direct in-process host playback via `python-sounddevice` (0 exec spawn) | CLI WAV file export |
| **Model Container** | ONNX (`model.onnx`, `model-de.onnx`) | GGUF (`kokoro-82m-q8_0.gguf`, `kokoro-de-hui-base-q8_0.gguf`) |
| **Voice Formats** | Pre-converted standard float32 `.bin` ($510 \times 256$, 522 KB) | GGUF voicepacks (`kokoro-voice-*.gguf`) |
| **Phonemizer** | Direct `libespeak-ng.so` C API via `ctypes` (zero subprocess overhead) | `libespeak-ng.so` direct C API link |
| **Long-Text Handling** | Automatic sentence chunking with 150ms speech gaps | Hard limit of 510 tokens (caller must chunk externally) |
| **Voice Blending** | Native linear style combination (e.g. `df_victoria(0.6)+dm_martin(0.4)`) | Supports voice style blending expressions |

## VRAM Usage

For detailed breakdowns of memory usage and concurrent execution scenarios (co-running Inference, Speech-to-Text, and Text-to-Speech), refer to [Central Memory Map](assistants/local-memory-map.md).

## Implementation & Security Considerations

### Centralized Sandboxing Configuration
All systemd security and namespace options are centralized in the `get_shared_options` function within the control script, ensuring identical sandbox profiles for the persistent background service and transient runs.

### ROCm / GPU Access
Because `qwen3-tts-server` requires direct access to GPU device nodes:
- `PrivateDevices=no` is set in the systemd unit.
- Access to `/dev/dri` and `/dev/kfd` is mandatory.
- The user must be in the `render` and `video` groups.

### Filesystem and Data Access
- **Models**: Read-write access to `/data/public/machine-learning` is configured (required to read the GGML models).
- **Sandboxing**: Uses `ProtectSystem=strict`.
- **Isolation**: The home directory (`%h` / `$HOME`) is bind-mounted, and system paths are kept read-only.

### Configuration & Ports
- **Default Port**: `20095`
- **Configuration File**: Environment parameters are stored in `~/.config/systemd/user/local-text-to-speech.env`.

## Verification & Test Results

The text-to-speech service can be validated using its built-in integration test command:

```bash
./assistants/local-text-to-speech.sh test

# Or run the comprehensive testsuite (all voices, OpenAI fallbacks, and features):
python3 tests/test-kokoro-features.py
```

This runs a complete text-to-audio synthesis cycle, pipes the generated audio file to the local transcription service, outputs the transcription, and plays the audio if a command-line player (`aplay`, `paplay`, `pw-play`) is available.

### Benchmarking Mode

To benchmark synthesis latency and throughput using a fixed 45-word sentence, run:

```bash
# Run text-to-speech benchmark (defaults to 1 run)
./assistants/local-text-to-speech.sh test --benchmark

# Run text-to-speech benchmark for multiple repeats to compute cumulative averages (e.g. 5 runs)
./assistants/local-text-to-speech.sh test --benchmark --repeat 5
```
