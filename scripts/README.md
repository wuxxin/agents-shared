# Helper Utilities

## `antigravity-launcher.sh`


A wrapper for running the Antigravity IDE (and other Electron apps) inside a **Bubblewrap (`bwrap`)** sandbox with a persistent, isolated home directory.

```bash
./scripts/antigravity-launcher.sh
```

Documentation: [antigravity-launcher.md](antigravity-launcher.md]

## `llama-cache-test.py`

A Python utility designed to measure the Key-Value (KV) cache performance, time-to-first-token (TTFT), and context processing speeds of a running `llama.cpp` server (or any OpenAI-compatible `/v1/completions` API).

Documentation: [llama-cache-test.md](llama-cache-test.md]

## `run-on-screen.sh`

Allows running GUI applications (like browser tests or IDEs) from a non-interactive shell (e.g. SSH or a systemd service) by "stealing" the current user's `DISPLAY`, `XAUTHORITY`, and `DBUS_SESSION_BUS_ADDRESS`.

```bash
./scripts/run-on-screen.sh <executable> [args...]
```


## `tiktoken_count.py`

A Python utility for counting tokens in text files or strings using the `tiktoken` library (consistent with OpenAI models).

```bash
python3 scripts/tiktoken_count.py <file_or_string>
```

## `tiktoken_tps_sim.py`

Simulates token-per-second (TPS) throughput for various models to help calibrate timeout settings and performance expectations.
