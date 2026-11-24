# Helper Utilities

- **`scripts/local-download.sh`**: Intelligent downloader for local AI models (LLMs, Embeddings, Reranker, Whisper STT) featuring caching, Hugging Face Hub downloads, and automated GGUF quantization.
- **`scripts/download-helper.py`**: Python helper utility supporting model MTP tensor merging (`merge-mtp`) and agent skills context generation (`benchmark-context`).
- **[`sandbox-ctl`](sandbox-ctl.md)**: A flexible, generalized wrapper for running any command-line or graphical binary inside a hardened Bubblewrap sandbox with X11/Wayland support, Pipewire/PulseAudio sound, and SSH agent forwarding.
- **[`antigravity-launcher.sh`](antigravity-launcher.md)**: A customized Bubblewrap sandbox wrapper specifically configured for running the Antigravity IDE (and other Electron applications) securely.
- **[`kpxc-secret`](kpxc-secret.md)**: KeePassXC secret helper utility.
- **`scripts/strata-launcher.py`**: runtime half of the strata service — `assistants/local-chat-strata.sh install` copies it next to the unit as `~/.config/systemd/user/local-chat-strata-launcher.py`. Supervises the engine (start, readiness, idle unload, SIGUSR1/2 save-restore, CLEAR_CACHE); it builds no argv and reads no knobs, because `generate_config_json()` owns both.
- **[`local-router.py`](../inference/router.md)**: Combined local inference router application serving unified OpenAI-compatible routes, token tracking, estimated cost metrics, and Prometheus scrapable endpoints.
- **[Benchmarks](../benchmarks/index.md)**: Local inference and Strata benchmark scripts, reports, and results.
- **`tests/`**: Automated test suite directory housing integration and performance test scripts (`test-local-router-usage.py`, `test-local-memory.py`, `test-fim-perf.py`).
- **`scripts/tiktoken_count.py`** / **`scripts/tiktoken_tps_sim.py`**: Calibrates timeout thresholds and measures token counts of input texts using OpenAI-compatible counts.


## `local-download.sh`

An intelligent Bash utility to download local AI models (LLM, Embeddings, Reranker, Whisper Speech-to-Text) to a target directory. It utilizes local cache fallbacks, Hugging Face Hub (`hf download`) integration, and handles local GGUF conversion & quantization for the reranker if pre-converted assets are unavailable.

```bash
./scripts/local-download.sh <target_model_dir> --all
```

## `download-helper.py`

Unified Python helper script executed by `local-download.sh` and assistant control scripts. Provides subcommands for MTP model tensor merging (`merge-mtp`) and agent skills context generation (`benchmark-context`).

```bash
# Merge MTP auxiliary head tensors into base GGUF model:
python3 scripts/download-helper.py merge-mtp <base_model.gguf> <mtp_tensors.gguf> <output_model_mtp.gguf>

# Download skills and build benchmark context file:
python3 scripts/download-helper.py benchmark-context --output <output_file.md>
```

## `sandbox-ctl`

A flexible, generalized wrapper for running any command-line or graphical binary inside a hardened systemd transient service or Bubblewrap (`bwrap`) container with persistent home directory mapping, sandboxed install/uninstall hooks, X11/Wayland display sharing, Pipewire/PulseAudio sound support, and SSH agent forwarding.

```bash
./scripts/sandbox-ctl install <app_name>
```

Documentation: [sandbox-ctl.md](sandbox-ctl.md)

## `antigravity-launcher.sh`

A wrapper for running the Antigravity IDE (and other Electron apps) inside a **Bubblewrap (`bwrap`)** sandbox with a persistent, isolated home directory.

```bash
./scripts/antigravity-launcher.sh
```

Documentation: [antigravity-launcher.md](antigravity-launcher.md)

## `tiktoken_count.py`

A Python utility for counting tokens in text files or strings using the `tiktoken` library (consistent with OpenAI models).

```bash
python3 scripts/tiktoken_count.py <file_or_string>
```

## `tiktoken_tps_sim.py`

Simulates token-per-second (TPS) throughput for various models to help calibrate timeout settings and performance expectations.

## `local-router.py`

FastAPI web application that unifies local inference services into a single OpenAI-compatible port (21080). Operates token tracking, cost estimations, text tables (`/usage?format=text`), and Prometheus scraping endpoints (`/metrics`).

Documentation: [router.md](../inference/router.md)


