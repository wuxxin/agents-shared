# Local Text-to-Speech Management Guide

`local-text-to-speech.sh` manages a persistent `qwen3-tts-server` instance for text-to-speech (TTS) voice synthesis. It exposes an OpenAI-compatible audio generation endpoint, enabling local, private speech synthesis.

- **Source Code**: [GitHub - khimaros/qwen3-tts.cpp](https://github.com/khimaros/qwen3-tts.cpp)
- **Arch/AUR Package**:
  - `qwen3-tts.cpp-git-ggml-hip` (private package in repo https://github.com/wuxxin/aur-packages )

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

The service runs `qwen3-tts-server` which loads a Qwen3-TTS talker model and a WavTokenizer vocoder model, exposing a REST API.

### Endpoints (all on port 50095)

| Endpoint | Purpose |
|---|---|
| `/v1/audio/speech` | OpenAI-compatible text-to-speech API (POST JSON with model, input, voice, and response_format) |
| `/v1/audio/voices` | Returns loaded voice names/presets |

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
curl -s http://127.0.0.1:50095/v1/audio/voices
```

This returns the following active voice presets loaded by the model:

- `default`
- `serena`
- `vivian`
- `uncle_fu`
- `ryan`
- `aiden`
- `ono_anna`
- `sohee`
- `eric`
- `dylan`

### Performance Tuning Presets

The server performance can be optimized using the `LTTS_MODE` environment variable in `local-text-to-speech.env`. This control toggles four primary presets:

1. **`gpu`**: Runs inference on the ROCm GPU. Keeps both the TTS transformer and the vocoder decoder models warm in VRAM, delivering maximum generation throughput.
2. **`hybrid`** (Performance Sweet Spot): Offloads Code Generation (`TTSTransformer`) to the CPU (setting `QWEN3_TTS_TRANSFORMER_FORCE_CPU=1`), while running Vocoder Decode (`AudioTokenizerDecoder`) on the GPU (`ROCm0`). This bypasses GEMV thread starvation and kernel launch latency on the GPU during the autoregressive stage, yielding a **1.5x to 2x speedup** over GPU-only and saving **1.5 GB to 2.7 GB of VRAM**.
3. **`cpu`** (Default): Completely bypasses ROCm GPU initialization and offloads all tensor computations to the CPU. Propagates dynamic threading settings to all GGML CPU backends.

To configure thread counts, edit the `LTTS_THREADS` option in the `.env` file (defaults to all cores via `$(nproc)`). For CPU-bound execution (cpu or Hybrid), the optimal thread count is **8 threads**. Setting it to 16 threads causes a ~2.2x slowdown due to CCD boundaries and synchronization overhead.

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

Pre-converted GGUF models are hosted on the [khimaros/qwen3-tts Collection](https://huggingface.co/collections/khimaros/qwen3-tts) on Hugging Face:

The default Model selected in the environment template is **0.6B CustomVoice**


- **0.6B Base Model**: [khimaros/Qwen3-TTS-12Hz-0.6B-Base-GGUF](https://huggingface.co/khimaros/Qwen3-TTS-12Hz-0.6B-Base-GGUF) (File: `Qwen3-TTS-12Hz-0.6B-Base-Q8_0.gguf`)
- **0.6B CustomVoice Model**: [khimaros/Qwen3-TTS-12Hz-0.6B-CustomVoice-GGUF](https://huggingface.co/khimaros/Qwen3-TTS-12Hz-0.6B-CustomVoice-GGUF) (File: `Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf`)
- **1.7B Base Model**: [khimaros/Qwen3-TTS-12Hz-1.7B-Base-GGUF](https://huggingface.co/khimaros/Qwen3-TTS-12Hz-1.7B-Base-GGUF) (File: `Qwen3-TTS-12Hz-1.7B-Base-Q8_0.gguf`)
- **1.7B CustomVoice Model**: [khimaros/Qwen3-TTS-12Hz-1.7B-CustomVoice-GGUF](https://huggingface.co/khimaros/Qwen3-TTS-12Hz-1.7B-CustomVoice-GGUF) (File: `Qwen3-TTS-12Hz-1.7B-CustomVoice-Q8_0.gguf`)
- **1.7B VoiceDesign Model**: [khimaros/Qwen3-TTS-12Hz-1.7B-VoiceDesign-GGUF](https://huggingface.co/khimaros/Qwen3-TTS-12Hz-1.7B-VoiceDesign-GGUF) (File: `Qwen3-TTS-12Hz-1.7B-VoiceDesign-Q8_0.gguf`)
- **Shared Vocoder**: [khimaros/Qwen3-TTS-Tokenizer-12Hz-GGUF](https://huggingface.co/khimaros/Qwen3-TTS-Tokenizer-12Hz-GGUF) (File: `Qwen3-TTS-Tokenizer-12Hz-F16.gguf`)

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
- **Default Port**: `50095`
- **Configuration File**: Environment parameters are stored in `~/.config/systemd/user/local-text-to-speech.env`.

## Verification & Test Results

The text-to-speech service can be validated using its built-in integration test command:

```bash
./assistants/local-text-to-speech.sh test
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
