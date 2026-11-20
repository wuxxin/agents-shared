# Community benchmark on AMD Radeon RX 7900 XTX

Measured on 2026-11-20 with `tools/strata_bench.py` (suite 1, 3 runs per test, medians with ranges). Speeds are the engine's own timings; first-token times are measured by the client over HTTP. Speed only: no correctness check was run.

## Hardware and software

- GPU and VRAM: AMD Radeon RX 7900 XTX, 24 GiB VRAM
- CPU: AMD Ryzen 7 PRO 5750G with Radeon Graphics (8 cores, 16 threads); installed RAM: 117.8 GiB; storage: sda     Samsung SSD 870 QVO 8TB sata; sdb     Samsung SSD 870 QVO 8TB sata; zram0; nvme1n1 Samsung SSD 980 PRO 1TB nvme; nvme0n1 Samsung SSD 980 PRO 1TB nvme
- OS: Linux 7.2.14-1-MANJARO; GPU driver: not read; CUDA (driver supports up to): not read
- Strata: project 0.1.62, commit not a git checkout; engine 0.1.62
- Background workloads: not recorded (GPU <host> limit/draw read above)

## Model and configuration

- Model and quantization: qwen3.8-flash-next
- Context: 240384 tokens; parallel slots: 1
- Settings: the install's own configuration, unchanged; thinking off for the suite; temperature 0

## Method

Run by `python tools/strata_bench.py` against the HTTP API of a Strata server (already running); model loading is not timed. One warm-up chat and a 1K prompt are discarded first. Every prompt starts with a unique tag, so the conversation cache cannot help the fresh-prompt tests.

- short chat: the three questions of `tools/ab_engine.py`, up to 100 new tokens, 3 runs
- 4K / 16K prompts: generated word lists sized by a calibration request, 24 new tokens, 3 fresh prompts each
- agent session: system prompt and four tools, then 5 turns that each add about 1500 words of a project file and continue from the model's own earlier answers (the way agent clients resend a conversation), 64 new tokens per turn, 3 sessions; the cache numbers come from the answer's usage (`cached_tokens`) and timings (`prompt_n`)
- concurrency (when run): N requests sent at the same moment, total tokens over the wall time of the burst, latency over all requests

## Results

| Configuration | Actual prompt tokens | Reused tokens | Generated tokens | Runs | Prompt tok/s median and range | Decode tok/s median and range | TTFT seconds median and range |
| --- | ---: | ---: | ---: | ---: | --- | --- | --- |
| short chat | 46 (43-51) | 0 | 100 (100-100) | 9 | not measured | 62.0 (56.8-75.8) | 0.46 (0.42-0.51) |
| 4K prompt, fresh | 4019 (4019-4019) | 0 (0-0) | 24 cap | 3 | 1293.7 (1286.9-1294.7) | not measured | 3.14 (3.13-3.15) |
| 16K prompt, fresh | 16058 (16058-16058) | 0 (0-0) | 24 cap | 3 | 2643.5 (2633.8-2675.0) | not measured | 6.11 (6.04-6.13) |
| agent session, follow-up turns | 9106 (9090-9137) at the last turn | see below | up to 64 | 3 | see below | 77.3 (45.9-90.0) | 3.04 (3.03-3.46) |

Ranges are the lowest and highest of the runs; `Runs` counts requests that returned a token.

### Agent session (conversation cache)

Cache hit over the follow-up turns: 71.3 % (71.3-71.3); earlier-turn tokens read again per session: 5 (5-5) (earlier turns that the cache did not hold; the 8207 (8207-8209) new tokens of the files are read once); first turn (nothing cached) first token: 2.79 s (2.59-2.86).

| Turn (run 1) | Prompt tokens | Reused | Read | Prompt tok/s | First token (s) | Decode tok/s |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 661 | 0 | 661 | 258.5 | 2.587 | 45.2 |
| 1 | 2316 | 674 | 1642 | 544.7 | 3.04 | 68.7 |
| 2 | 4022 | 2379 | 1643 | 544.6 | 3.043 | 66.2 |
| 3 | 5728 | 4085 | 1643 | 544.9 | 3.041 | 68.4 |
| 4 | 7410 | 5768 | 1642 | 545.0 | 3.04 | 73.8 |
| 5 | 9090 | 7448 | 1642 | 545.0 | 3.039 | 88.7 |

Per-request data: `results.json`. Engine log lines from the start: `engine-log-excerpt.txt` (when this run started the server).

## Correctness and limitations

Not measured: this is a speed suite. The conversation uses the model's own replies, so token counts differ a little between runs. Machine details come from the server, `nvidia-smi`/`rocm-smi` and the OS; background load is not recorded. Total time of the suite: 120 s.
