# C3 — prompt F16 (`STRATA_HIP_PROMPT_F16=1`) on gfx1100

Oracle B prefill, 22k-token prompts (`omp bench --profile prefill --prefill-bytes 120000 --runs 2`),
2 cells per arm, engine restarted per arm by `scripts/strata-env-battery.sh`. Verdict metric is the
engine's own `prompt N tokens … read in X ms (Y tok/s)` line, not bench TTFT.

## Engagement proof

The flag reached the engine process (`STRATA_HIP_PROMPT_F16=1` in `/proc/<pid>/environ`) and the engine
announced the route:

```
strata prefill: HIP device 0 gfx1100 - STRATA_HIP_PROMPT_F16=1: the prompt's 16-bit GEMMs run FP16 in and out
(rocBLAS is tuned only for that on gfx103x; not bit-identical to the default)
```

Occurrences: `engine-f16.log` = 1, `engine-base.log` = 0. The arm measured what it claims to measure.
(This needed a harness fix first: the battery launched the launcher without sourcing the env file, so
env-only knobs silently never reached the engine — the same failure class as the `PARALLEL` bug.)

## Results (22k prefills, engine-side)

| Arm | Individual | Mean |
|---|---|---|
| base | 2,736 / 2,722 / 2,718 / 2,627 tok/s | **2,701** |
| `STRATA_HIP_PROMPT_F16=1` | 2,695 / 2,679 / 2,685 / 2,607 tok/s | 2,667 |

**−1.3 %** (and every f16 sample is below its base counterpart).

## Verdict

Keep the engine default (F16 prompt path **off** on gfx1100). Upstream's 11–14 % gain is documented for
discrete RX 6000 (gfx1030/31/32), where rocBLAS is tuned for the FP16 in/out route; `prompt_f16_resolve`
deliberately does not enable it on gfx1100. On this card the extra FP16 rounding buys nothing and costs
~1.3 % — and it is not bit-identical, so there is no quality argument to accept it either.

The 48-row hipBLASLt table was not a confounder here: it covers both bf16 and f16 model shapes, so the
f16 route ran on tuned kernels rather than falling back.

## Notes

- C0's caveat still stands: this cell was run after a C0 that failed its decode floor, so it closes the
  C3 matrix entry but does not legitimise the upgrade gate.
- Code: `scripts/strata-env-battery.sh` now passes `--profile/--detailed` bench args through untouched
  and sources the env file for direct launches.
