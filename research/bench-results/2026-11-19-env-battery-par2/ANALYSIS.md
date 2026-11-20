# C1 batching — `parallel: 1` vs `parallel: 2` (engine 0.2.16)

`omp bench --detailed --par 4 --runs 2`, engine restarted per arm by `scripts/strata-env-battery.sh`
(env file rewritten + `install`, launcher started directly). Only the parallel2 arm's second run is
valid: the first attempt silently measured base again because `LCHAT_STRATA_PARALLEL` was missing from
the launcher's export list (now fixed and re-verified: config `parallel: 2`, engine argv `--batch 2`).

## Did the second slot actually engage? Yes

```
batch 2: a slot's K/V takes 2.19 GiB of pinned RAM, 70.9 GiB are available …
batch 2: the slot sessions take 1.42 GiB of VRAM on CUDA0 that the expert cache would otherwise hold
expert cache auto: 15.51 GiB free   →  7,633 slots     (base: 16.91 GiB free → 8,374 slots)
```

`batch_slots = 2` granted; cost = **1.42 GiB VRAM and 741 expert slots (−8.8%)**.

## Single-user phase (1 concurrent)

| Cell | base (`parallel 1`) | `parallel 2` |
|---|---|---|
| 1 (cold) | aggregate 71.5, gen 74.7–80.3 | aggregate 51.1, gen 50.8–69.3 |
| 2 | aggregate 69.7, gen 74.0–76.1 | aggregate 60.3, gen 67.7–69.1 |

Single-stream decode drops **~14%** (warm cell) to **~28%** (cold) — the direct cost of halving VRAM
available to the expert cache and splitting KV.

## Parallel phase (4 concurrent requests)

| Arm | Per-request gen | TTFT range | Aggregate | Wall |
|---|---|---|---|---|
| base cell 1 | 73.3–76.1 (one full-rate, three ≈33–35) | **7.7–8.3 s** (queued), 0.87 s first | 68.1 | 30.1 s |
| base cell 2 | 71.9–76.8 (same pattern) | **7.6–9.0 s** | 66.7 | 30.7 s |
| parallel2 cell 1 | 34.9–37.9 (all four served) | **1.1–2.6 s** | 63.9 | 32.1 s |
| parallel2 cell 2 | 35.1–38.0 | **0.15–1.2 s** | 69.6 | 29.4 s |

Aggregate throughput is **unchanged** (63.9–69.6 vs 66.7–68.1). What changes is *queueing*: with one
slot three of four requests wait ~8 s and then run at ~33 tok/s anyway; with two slots all four start
within ~1 s at the same ~35 tok/s per request.

## Verdict

- `parallel: 2` **fits** on this card (no fitter trim), at 1.42 GiB VRAM and 741 expert slots.
- **Aggregate is a wash**; the gain is tail latency for concurrent callers (TTFT 8 s → ~1 s).
- **Cost is single-stream decode, −14% warm** — outside the ≤25% budget only in the cold cell, but it is
  a real, persistent regression for the interactive main session.
- Keep `parallel: 1` as production default. The knob (`LCHAT_STRATA_PARALLEL`) stays available for
  bursts where queue latency matters more than main-session decode.
- `/slots` save-restore coexistence (plan D-C) was **not** exercised here — that still needs the
  `strata-park-lab.py` run with `arm C`.
