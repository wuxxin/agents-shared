# Local Image Generation Management Guide

`local-image.sh` manages a persistent `sd-server` instance for image generation. It exposes an OpenAI-compatible image generation endpoint, enabling local, private text-to-image synthesis.

- **Source Code**: [GitHub - leejet/stable-diffusion.cpp](https://github.com/leejet/stable-diffusion.cpp)
- **Arch/AUR Package**:
  - `stable-diffusion.cpp-git-ggml-hip` (private package in repo https://github.com/wuxxin/aur-packages )

## Usage

| Command | Description |
|---|---|
| `install [--no-start] [--new-config]` | Sets up the service, generates default configuration env file (does not start if `--no-start` is specified, force overwrites with defaults if `--new-config` is specified). |
| `uninstall` | Stops and removes the service. |
| `edit` | Edit model selection and server parameters. |
| `logs [args...]` | View the generation server output. Pass `-f` to tail/follow. Supports any `journalctl` options. |
| `exec [--env KEY=VAL]*` | Run `sd-server` as a transient systemd user service with identical GPU sandbox settings. |
| `run [--env KEY=VAL]* <cmd>` | Run a custom command inside the image generation sandbox environment. |
| `shell [--env KEY=VAL]*` | Spawn an interactive shell in the image generation sandbox (useful for manual testing). |
| `test` | Run API validation tests (requests a simple image and saves it). |

### In-Memory Environment Overrides

The `exec`, `run`, and `shell` subcommands support a repeatable `--env KEY=VALUE` parameter. When passed, these parameters:
1. Override the values loaded from the `.env` configuration file on disk.
2. Are exported in the local shell environment in-memory for foreground execution.
3. Are dynamically passed to `systemd-run` via `--setenv=KEY=VALUE` for transient background runs in systemd.

These overrides are kept transient, keeping the main `.env` configuration file untouched. For example, to run the server temporarily on CPU without changing your permanent configuration:
```bash
./local-image.sh exec --env LIMG_BACKEND=cpu
```

## Architecture

The service runs `sd-server` which loads a GGUF diffusion model, a VAE, and a GGUF text encoder (LLM), exposing a REST API.

### Endpoints (all on port 50100)

| Endpoint | Purpose |
|---|---|
| `/v1/images/generations` | OpenAI-compatible image generation API (POST JSON with prompt, steps, and cfg_scale) |
| `/sdapi/v1/txt2img` | Automatic1111-compatible image generation API |

### Configuration Files

| File | Purpose |
|---|---|
| `~/.config/systemd/user/local-image.env` | Model paths, port, host, backend, steps, and thread configuration |
| `~/.config/systemd/user/local-image.service` | Auto-generated systemd unit |

### Backend Device Selection (Dynamic Backend Loading)

When using `stable-diffusion.cpp-git-ggml-hip`, the service supports dynamic loading of different acceleration backends (CPU, Vulkan, and HIP/ROCm) at runtime. 

You can configure the target device/backends using the `LIMG_BACKEND` environment variable. Run `./local-image.sh edit` (or edit `~/.config/systemd/user/local-image.env` directly) and configure:

```bash
# GPU/CPU backend device to use (run 'sd-cli --help' or check hardware targets)
# Valid options for LIMG_BACKEND include:
#   - cpu                                     : Force CPU-only execution for all components
#   - vulkan0, vulkan1, etc.                 : Run everything on the specified Vulkan device
#   - cuda0, cuda1, etc.                     : Run everything on the specified CUDA device
#   - vulkan1,te=cpu                         : Run diffusion/VAE on Vulkan1 and offload text encoder (te) to CPU
#                                               (highly recommended to bypass Vulkan's 1GB parameter buffer limit)
#   - clip=cpu,vae=vulkan1,diffusion=vulkan1  : Custom heterogeneous backend routing
#                                               (e.g., keeping clip on CPU, and others on Vulkan)
# LIMG_BACKEND="vulkan1"
```

## Models & Repositories

Pre-converted models are downloaded into `<target_model_dir>/image/`:

- **Diffusion Model**: [jayn7/Z-Image-Turbo-GGUF](https://huggingface.co/jayn7/Z-Image-Turbo-GGUF) (File: `z_image_turbo-Q8_0.gguf`)
- **VAE**: [black-forest-labs/FLUX.1-schnell](https://huggingface.co/black-forest-labs/FLUX.1-schnell) (File: `ae.safetensors`)
- **Text Encoder (LLM)**: [unsloth/Qwen3-4B-GGUF](https://huggingface.co/unsloth/Qwen3-4B-GGUF) (File: `Qwen3-4B-Q4_K_M.gguf`)

## Implementation & Security Considerations

### Centralized Sandboxing Configuration
All systemd security and namespace options are centralized in the `get_shared_options` function within the control script, ensuring identical sandbox profiles for the persistent background service and transient runs.

### ROCm / Vulkan / GPU Access
Because `sd-server` requires direct access to GPU device nodes:
- `PrivateDevices=no` is set in the systemd unit.
- Access to `/dev/dri` and `/dev/kfd` is mandatory.
- The user must be in the `render` and `video` groups.

### Filesystem and Data Access
- **Models**: Read-write access to `/data/public/machine-learning` is configured (required to read the GGUF models).
- **Sandboxing**: Uses `ProtectSystem=strict`.
- **Isolation**: The home directory (`%h` / `$HOME`) is bind-mounted, and system paths are kept read-only.

### Configuration & Ports
- **Default Port**: `50100`
- **Configuration File**: Environment parameters are stored in `~/.config/systemd/user/local-image.env`.

## Verification & Test Results

The image generation service can be validated using its built-in integration test command:

```bash
./assistants/local-image.sh test
```

This runs a simple generation cycle using curl and saves the generated output to `/tmp/local_image_test_output.png`.

### Benchmarking Mode

To benchmark image generation latency using a fixed prompt and 8 steps, run:

```bash
# Run image generation benchmark (defaults to 1 run)
./assistants/local-image.sh test --benchmark

# Run image generation benchmark for multiple repeats to compute cumulative averages (e.g. 5 runs)
./assistants/local-image.sh test --benchmark --repeat 5
```
