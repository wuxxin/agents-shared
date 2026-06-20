# Helper Utilities

- **[local-download.sh](local-download.sh)**: Intelligent downloader for local AI models (LLMs, Embeddings, Reranker, Whisper STT) featuring caching, Hugging Face Hub downloads, and automated GGUF quantization.
- **[sandbox-launcher.sh](sandbox-launcher.sh)**: A flexible, generalized wrapper for running any command-line or graphical binary inside a hardened Bubblewrap sandbox with X11/Wayland support, Pipewire/PulseAudio sound, and SSH agent forwarding.
- **[antigravity-launcher.sh](antigravity-launcher.sh)**: A customized Bubblewrap sandbox wrapper specifically configured for running the Antigravity IDE (and other Electron applications) securely.
- **[run-local-benchmark.py](run-local-benchmark.py)**: Automate running and recording local service benchmarks (chat, embedding, rerank, STT, TTS) across configurations.
- **[tiktoken_count.py](tiktoken_count.py)** / **[tiktoken_tps_sim.py](tiktoken_tps_sim.py)**: Calibrates timeout thresholds and measures token counts of input texts using OpenAI-compatible counts.


## `local-download.sh`

An intelligent Bash utility to download local AI models (LLM, Embeddings, Reranker, Whisper Speech-to-Text) to a target directory. It utilizes local cache fallbacks, Hugging Face Hub (`hf download`) integration, and handles local GGUF conversion & quantization for the reranker if pre-converted assets are unavailable.

```bash
./scripts/local-download.sh <target_model_dir> --all
```

## `sandbox-launcher.sh`

A flexible, generalized wrapper for running any command-line or graphical binary inside a hardened **Bubblewrap (`bwrap`)** sandbox with persistent home directory mapping, X11/Wayland display sharing, Pipewire/PulseAudio sound support, and SSH agent forwarding.

```bash
./scripts/sandbox-launcher.sh install <app_name>
```

Documentation: [sandbox-launcher.md](sandbox-launcher.md)

## `antigravity-launcher.sh`

A wrapper for running the Antigravity IDE (and other Electron apps) inside a **Bubblewrap (`bwrap`)** sandbox with a persistent, isolated home directory.

```bash
./scripts/antigravity-launcher.sh
```

Documentation: [antigravity-launcher.md](antigravity-launcher.md)

## `run-local-benchmark.py`

A Python automation script to run local service benchmarks (chat, embedding, rerank, STT, TTS) across configurations (HIP, Vulkan, CPU, special) and write a comparative markdown report.

Documentation: [run-local-benchmark.md](run-local-benchmark.md)


## `tiktoken_count.py`

A Python utility for counting tokens in text files or strings using the `tiktoken` library (consistent with OpenAI models).

```bash
python3 scripts/tiktoken_count.py <file_or_string>
```

## `tiktoken_tps_sim.py`

Simulates token-per-second (TPS) throughput for various models to help calibrate timeout settings and performance expectations.

