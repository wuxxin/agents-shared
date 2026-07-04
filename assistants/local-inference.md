# Local Inference Coordinator Guide

`local-inference.sh` is a wrapper and coordinator script designed to manage multiple local inference services collectively.  it simplifies lifecycle management (install, uninstall, start, stop, restart, logs, status) for all 7 underlying local services.

Input:

| Service | Default Port(s) | Description / Protocol |
|---------------|-----------------|------------------------|
| **Local-Chat** | [50080](http://localhost:50080) | Llama-server serving Chat/Vision LLM (and optional embeddings) |
| **Local-Embedding** | [50082](http://localhost:50082) | Llama-server serving Text Embeddings |
| **Local-Rerank** | [50086](http://localhost:50086) | Llama-server serving Document Reranking |
| **Local-Speech-To-Text** | [50090](http://localhost:50090) | Whisper-server audio transcription API (HTTP) |
| **Local-Text-to-Speech** | [50095](http://localhost:50095) | Qwen3-tts-server audio synthesis API (HTTP) |
| **Local-Image** | [50100](http://localhost:50100) | sd-server serving Image Generation API (HTTP) |
| **Local-Router** | [51080](http://localhost:51080) | combined service router / OpenAI proxy (HTTP) |


## Usage

```bash
# Install all managed services and re-create the default configuration for each service
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

# Run validation tests / benchmarks for all enabled services
./local-inference.sh test [test-args...]

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
LIMG_ENABLED=1
LROUT_ENABLED=1
```

- **`start`** enables and starts all services set to `1`.
- **`stop`** stops all enabled services, and stops/disables all services set to `0`.
- **`restart`** stops/disables all services set to `0`, and enables/restarts all services set to `1`.

#### Combined Embeddings Mode
By default, the embedding service runs as a standalone server on port 50082 (`LMBD_ENABLED=1`).
To run in **Combined Mode** (serving both Chat and Embeddings in a single `llama-server` instance on port 50080):
1. Set `LMBD_ENABLED=0` in `local-inference.env` to disable the separate service.
2. Add `'LCHAT_EMBEDDING_ENABLED=true'` inside the `LCHAT_OVERRIDE` array in `local-inference.env`:
   ```env
   LCHAT_OVERRIDE=(
       'LCHAT_EMBEDDING_ENABLED=true'
   )
   ```

### Propagating Service Overrides

You can define overrides inside `local-inference.env` using Bash array syntax:

```env
LCHAT_OVERRIDE=(
    'LCHAT_DEVICE="ROCm0"'
    'GGML_VK_DISABLE_MMVQ=1'
)
LRR_OVERRIDE=(
    'CUDA_VISIBLE_DEVICES=""'
    'HIP_VISIBLE_DEVICES=""'
    'LRR_DEVICE="Vulkan1"'
)
LIMG_OVERRIDE=(
    'LIMG_BACKEND="vulkan,te=cpu"'
)
```

The coordinator automatically extracts these key-value pairs and writes/modifies them in the respective target service env files (e.g. `~/.config/systemd/user/local-rerank.env`) on `install`, `start`, `restart`, `edit`, and `test`.

For example, to run the image diffusion and VAE modules on a specific Vulkan GPU (`vulkan1`) while offloading the text encoder parameters to CPU RAM (highly recommended to bypass Vulkan's 1GB parameter buffer limit), configure the following in `local-inference.env`:

```env
LIMG_OVERRIDE=(
    'LIMG_BACKEND="vulkan1,te=cpu"'
    'LIMG_LLM="/home/wuxxin/models/image/Qwen3-4B-Q4_K_M.gguf"'
)
```

Any key matching `^KEY=.*$` or comment `^# KEY=.*$` is replaced with the override value, or appended to the service's env file if not found.

### Backend Environment Variable Propagation (`GGML_*` & GPUs)

For the underlying C++ backend engines (built on `ggml`/`llama.cpp`), environment variables control hardware dispatching and optimizations:
- **`GGML_*` Backend Controls**: Variables like `GGML_VK_DISABLE_MMVQ=1` (to disable Vulkan MMVQ activation quantization) or `GGML_VULKAN_DEVICE` are automatically propagated.
- **GPU Visibility Controls**: Variables like `CUDA_VISIBLE_DEVICES` or `HIP_VISIBLE_DEVICES` control which GPU devices are visible to the backends.

To support this seamlessly across different runtimes, the service control scripts automatically detect and **export** all `GGML_*`, `CUDA_VISIBLE_DEVICES`, and `HIP_VISIBLE_DEVICES` variables loaded from their configuration files. This ensures they are correctly set in the environment for:
1. **Systemd Services**: Read via systemd's `EnvironmentFile=` directive.
2. **Foreground/Transient Executions**: Sourced and exported during direct/CLI runs (e.g., `./local-chat.sh exec` when systemd is not active).
