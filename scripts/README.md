# Helper Utilities


## `llama-cache-test.py`

A Python utility designed to measure the Key-Value (KV) cache performance, time-to-first-token (TTFT), and context processing speeds of a running `llama.cpp` server (or any OpenAI-compatible `/v1/completions` API).

Documentation: [llama-cache-test.md](llama-cache-test.md)


## `tiktoken_count.py`

A Python utility for counting tokens in text files or strings using the `tiktoken` library (consistent with OpenAI models).

```bash
python3 scripts/tiktoken_count.py <file_or_string>
```

## `tiktoken_tps_sim.py`

Simulates token-per-second (TPS) throughput for various models to help calibrate timeout settings and performance expectations.

## `local-download.sh`

An intelligent Bash utility to download local AI models (LLM, Embeddings, Reranker, Whisper Speech-to-Text) to a target directory. It utilizes local cache fallbacks, Hugging Face Hub (`hf download`) integration, and handles local GGUF conversion & quantization for the reranker if pre-converted assets are unavailable.

```bash
./scripts/local-download.sh <target_model_dir> --all
```

