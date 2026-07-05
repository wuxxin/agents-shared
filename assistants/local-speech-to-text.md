# Local Speech-to-Text Management Guide

`local-speech-to-text.sh` manages a persistent `whisper-server` instance for speech-to-text (STT) transcription. It serves an OpenAI-compatible audio transcription endpoint, enabling local, private voice processing.

- **Source Code**: [GitHub - ggerganov/whisper.cpp](https://github.com/ggerganov/whisper.cpp)
- **Arch/AUR Package**:
  - `whisper.cpp` (AUR, standard source package)
  - `whisper.cpp-git` (AUR, latest git source build)
  - `whisper.cpp-git-ggml-hip` (private package `libggml-git-hip` in repo https://github.com/wuxxin/aur-packages )

## Usage

| Command | Description |
|---|---|
| `install [--no-start] [--new-config]` | Sets up the service, generates default configuration env file (does not start if `--no-start` is specified, force overwrites with defaults if `--new-config` is specified). |
| `uninstall` | Stops and removes the service. |
| `edit` | Edit model selection and server parameters. |
| `logs [args...]` | View the transcription server output. Pass `-f` to tail/follow. Supports any `journalctl` options. |
| `exec [--env KEY=VAL]*` | Run `whisper-server` as a transient systemd user service with identical GPU sandbox settings. |
| `run [--env KEY=VAL]* <cmd>` | Run a custom command inside the speech-to-text sandbox environment. |
| `shell [--env KEY=VAL]*` | Spawn an interactive shell in the speech sandbox (useful for manual testing). |
| `test` | Run API validation tests (downloads jfk.wav and verifies transcription). |

### In-Memory Environment Overrides

The `exec`, `run`, and `shell` subcommands support a repeatable `--env KEY=VALUE` parameter. When passed, these parameters:
1. Override the values loaded from the `.env` configuration file on disk.
2. Are exported in the local shell environment in-memory for foreground execution.
3. Are dynamically passed to `systemd-run` via `--setenv=KEY=VALUE` for transient background runs in systemd.

These overrides are kept transient, keeping the main `.env` configuration file untouched. For example, to run the server temporarily on CPU without changing your permanent configuration:
```bash
./local-speech-to-text.sh exec --env LSTT_NO_GPU=true
```

## Architecture

The service runs `whisper-server` which loads a GGML Whisper model and exposes a REST API. By default, it runs with Flash Attention and audio transcoding enabled.

### Endpoints (all on port 50090)

| Endpoint | Purpose |
|---|---|
| `/v1/audio/transcriptions` | OpenAI-compatible audio transcription API (POST multipart/form-data) |
| `/health` | Server health check endpoint |

### Configuration Files

| File | Purpose |
|---|---|
| `~/.config/systemd/user/local-speech-to-text.env` | Model path, port, host, and thread configuration |
| `~/.config/systemd/user/local-speech-to-text.service` | Auto-generated systemd unit |

### Switching between GPU and CPU Inference

By default, the service runs the speech-to-text transcription engine on the GPU for maximum speed. If GPU resources are constrained, it can be run on the CPU instead.

To run the service on the CPU or GPU, run `./local-speech-to-text.sh edit` (or edit `~/.config/systemd/user/local-speech-to-text.env` directly) and change the `LSTT_NO_GPU` parameter:

```bash
# For CPU execution (uncomment to enable)
LSTT_NO_GPU=true

# For GPU execution (default, commented out)
# LSTT_NO_GPU=true
```

### Backend Device Selection (Dynamic Backend Loading)

When using a combined backend build (such as `whisper.cpp-git-ggml-hip`), the service supports dynamic loading of different acceleration backends (CPU, OpenBLAS, Vulkan, and HIP/ROCm) at runtime. 

You can configure the target device using the `LSTT_DEVICE` environment variable. Run `./local-speech-to-text.sh edit` (or edit `~/.config/systemd/user/local-speech-to-text.env` directly) and configure the device:

```bash
# GPU/CPU backend device to use (e.g. hip, vulkan, cpu, openblas)
# By default, whisper-server automatically selects the best available device.
# To force a specific backend device, uncomment one of the options below:
# LSTT_DEVICE="hip"
# LSTT_DEVICE="vulkan"
# LSTT_DEVICE="cpu"
# LSTT_DEVICE="openblas"
```

### Language Selection

By default, the service uses automatic language detection. You can configure the target language using the `LSTT_LANG` environment variable. Run `./local-speech-to-text.sh edit` (or edit `~/.config/systemd/user/local-speech-to-text.env` directly) and configure the language:

```bash
# Spoken language ('auto' for auto-detect, or a language code like 'en', 'de', 'fr')
# LSTT_LANG="auto"
```


## VRAM Usage

The speech-to-text service requires approximately **~1.4 GiB** of VRAM when loaded (including weights, caches, compute buffers, and HIP context overhead). 

For a detailed breakdown of all VRAM allocations, options, and scenarios (including concurrent running of all three local services), refer to [Central VRAM Memory Map](assistants/local-memory-map.md).

## Implementation & Security Considerations

### Centralized Sandboxing Configuration
All systemd security and namespace options are centralized in the `get_shared_options` function within the control script. This ensures that the persistent background service (`local-speech-to-text.service`) and any transient runs (`exec` / `shell` commands) run with identical sandbox profiles, preventing configuration drift.

### ROCm / GPU Access
Because `whisper-server` requires direct access to GPU device nodes:
- `PrivateDevices=no` is set in the systemd unit.
- Access to `/dev/dri` and `/dev/kfd` is mandatory.
- The user must be in the `render` and `video` groups.

### Filesystem and Data Access
- **Models**: Read-write access to `/data/public/machine-learning` is configured (required to read the GGML model).
- **Sandboxing**: Uses `ProtectSystem=strict`.
- **Audio Conversion**: The server automatically transcodes input audio files (e.g. MP3, AAC, FLAC) to the required format (16kHz WAV) using `ffmpeg`. Therefore, the script configures `BindPaths=%h` to allow the server to write transient temporary transcoded files in the home directory sandbox.
- **Isolation**: The home directory (`%h` / `$HOME`) is bind-mounted, and system paths are kept read-only.

### Configuration & Ports
- **Default Port**: `50090`
- **Configuration File**: Environment parameters are stored in `~/.config/systemd/user/local-speech-to-text.env`.

## Verification & Test Results

The speech-to-text service can be validated using the built-in test command:

```bash
./assistants/local-speech-to-text.sh test
```

This command downloads a test sample (`jfk.wav`), sends it to the running speech-to-text server, and verifies that the transcription succeeds and contains expected keywords.

### Benchmarking Mode

To benchmark transcription latency and throughput using a 45-second famous speech audio sample (President William McKinley's 1896 campaign address), run:

```bash
# Run speech-to-text benchmark (defaults to 10 runs)
./assistants/local-speech-to-text.sh test --benchmark

# Run speech-to-text benchmark for multiple repeats to compute cumulative averages (e.g. 5 runs)
./assistants/local-speech-to-text.sh test --benchmark --repeat 5
```

This will automatically locate `speech-to-text.ogg` in the models directory or download it to `/tmp/speech-to-text.ogg` if the models directory is read-only.

