# `strata_bench.py` baseline — engine 0.2.16 on RX 7900 XTX

Upstream's own protocol (the one `docs/BENCHMARK_PROTOCOL.md` defines), run against the live service:
`strata_bench.py --url http://127.0.0.1:20080 --runs 3`. Folder is the tool's own output
(`README.md` + `results.json`) so it can be compared later with `--compare`.

Note: run went **direct to the engine**; the router-side path (`:21080`) was added the same day for
visibility (plan §6) and needs a router restart before it can be used for the next run.

## Results (median, range)

| Metric | Value |
|---|---|
| chat decode | **62.0 tok/s** (56.8–75.8, n=9) |
| chat first token | 0.46 s (0.42–0.51) |
| 4K prompt | **1,293.7 tok/s** (first token 3.14 s) |
| 16K prompt | **2,643.5 tok/s** (first token 6.11 s) |
| agent cache hit | **71.26 %** (71.25–71.31) |
| agent re-read per turn | 1,642–1,643 tokens (constant) |
| agent decode | **77.3 tok/s** (45.9–90.0, n=15) |

## The 4K anomaly is a fixed cost, not slow prefill

4K reads at 1,294 tok/s while 16K reads at 2,644 — a 2× rate difference for the same engine. Fitting
`t = fixed + tokens/rate` to the two medians:

```
marginal prefill  ≈ 4,081 tok/s
fixed per fresh prompt ≈ 2.16 s
predicted 22k time = 2.16 + 22210/4081 = 7.6 s   (measured 8.1–8.3 s)
```

So the engine's *marginal* prefill is ~4.1k tok/s; what looks like a 1.3k tok/s rate at 4K is 2.16 s of
fixed work plus 1 s of reading. This single number explains:

- the 4K/16K "rate inversion" and why prompt tok/s measured on short prompts always looks bad,
- the C0 prefill comparison (2,672–2,736 at 22k) — same fixed cost, same marginal rate,
- the TTFT tails in the batteries (~2 s floor even for a cached 100-token request, ~8 s under queue churn).

`[INFERENCE]` The fixed component is per *fresh* prompt (window capture/verify + admission + checkpoint
creation); the agent rows show it shrinking to near zero across turns once a checkpoint exists.

## Agent session — the checkpoint ladder works

Per turn: `turn 1` reuses 674/2316 (29 %); `turn 5` reuses 7,448/9,090 (82 %), with **exactly 1,642 tokens
re-read every turn** — a constant-size suffix recomputed against the previous checkpoint. That is the
behaviour `--conversation-cache-rewind-keep` exists to control, and it costs a flat 1,642-token prefill per
turn (~0.4 s at the marginal rate) rather than re-reading the whole session.

## Cross-checks against our own protocol

| | `strata_bench` | `omp bench` / engine log |
|---|---|---|
| long-prompt prefill | 16K: 2,643.5 tok/s | 22k: 2,672–2,736 tok/s |
| decode, long generation | agent 77.3 tok/s | generation profile 69–71 tok/s |

Both protocols agree within the fixed-cost model: the 16K figure is lower only because the same 2.16 s is
spread over fewer tokens. Chat decode (62) is lower than generation decode (70–77) because it is measured
over 100-token replies, where the first-token cost is still a large share.

## To do next

- Rerun through `http://127.0.0.1:21080` after the router restart, so the run shows up in token accounting
  and Prometheus; keep this direct run as the engine-only reference.
- `--compare` this folder against any future run to quantify drift instead of re-deriving it.
