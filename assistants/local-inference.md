# Local Inference Coordinator Guide

`local-inference.sh` is a wrapper and coordinator script designed to manage multiple local inference services collectively. It is not a systemd service itself, but it simplifies lifecycle management (install, uninstall, start, stop, restart, logs, status) for all 5 underlying local services:

1. **`local-chat`** (llama-server for chat & vision)
2. **`local-embedding`** (llama-server for embeddings)
3. **`local-rerank`** (llama-server for document rerank)
4. **`local-speech-to-text`** (whisper-server for speech transcription)
5. **`local-text-to-speech`** (qwen3-tts-server for voice synthesis)

## Usage

```bash
# Install all managed services and generate the default coordinator env configuration
./local-inference.sh install [--new-config]

# Start/Stop/Restart all services based on their activation states
./local-inference.sh start
./local-inference.sh stop
./local-inference.sh restart

# Check the consolidated runtime status of all services
./local-inference.sh status

# View the combined systemd user logs of all managed services
./local-inference.sh logs [journalctl-args...]

# Edit the coordinator configuration and automatically apply changes / restart services
./local-inference.sh edit

# Uninstall all managed services
./local-inference.sh uninstall
```

---

## Configuration & Environment Overrides

The coordinator stores its settings in:
- **Environment File**: `~/.config/systemd/user/local-inference.env`

### Service Activation

You can toggle which services are enabled or disabled by editing `local-inference.env`:

```env
LCHAT_ENABLED=1
LMBD_ENABLED=1
LRR_ENABLED=1
LSTT_ENABLED=1
LTTS_ENABLED=1
```

- **`start`** enables and starts all services set to `1`.
- **`stop`** stops all enabled services, and stops/disables all services set to `0`.
- **`restart`** stops/disables all services set to `0`, and enables/restarts all services set to `1`.

### Propagating Service Overrides

You can define overrides inside `local-inference.env` using Bash array syntax:

```env
LRR_OVERRIDE=(
    'CUDA_VISIBLE_DEVICES=""'
    'HIP_VISIBLE_DEVICES=""'
    'LRR_DEVICE="Vulkan1"'
)
```

The coordinator automatically extracts these key-value pairs and writes/modifies them in the respective target service env files (e.g. `~/.config/systemd/user/local-rerank.env`) on `install`, `start`, `restart`, and `edit`.

Any key matching `^KEY=.*$` or comment `^# KEY=.*$` is replaced with the override value, or appended to the service's env file if not found.
