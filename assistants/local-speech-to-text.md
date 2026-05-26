# Local Speech-to-Text Management Guide

`local-speech-to-text.sh` manages a persistent `whisper-server` instance for speech-to-text (STT) transcription. It serves an OpenAI-compatible audio transcription endpoint, enabling local, private, and high-performance voice processing. Optimized for AMD ROCm hardware (specifically tested on Radeon Pro W6800).

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
| `exec` | Run `whisper-server` in a transient unit with the same GPU access. |
| `shell` | Spawn an interactive shell in the speech sandbox (useful for manual testing). |
| `test` | Run API validation tests (downloads jfk.wav and verifies transcription). |

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

## VRAM Budget Summary

Hardware: AMD Radeon Pro W6800 — **30,704 MiB** usable VRAM.

The speech-to-text service requires approximately **~1.4 GiB** of VRAM when loaded (including weights, caches, compute buffers, and HIP context overhead). 

For a detailed breakdown of all VRAM allocations, options, and scenarios (including concurrent running of all three local services), refer to [Central VRAM Memory Map](file:///home/wuxxin/agent-shared/code/agents-shared/assistants/local-memory-map.md).

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

