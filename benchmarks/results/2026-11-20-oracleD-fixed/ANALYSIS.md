# Oracle D — park-churn with the conversation-cache SSD tier (engine 0.2.16)

Protocol: `scripts/strata-park-lab.py` §5 shape — warm a ~120k conversation, idle, fire **K=9** prefix-sharing
subagent conversations (3 growing turns each), then return a 1-token probe to main. Arm = engine config
written into the env file, `install`, launcher started directly (`scripts/strata-env-battery.sh
--workload parklab --park-args "--k 9"`). Two repeats per arm; each arm gets a fresh engine.

## Why the first attempts were invalid

| Attempt | Result | Verdict |
|---|---|---|
| K=5, shared 120k prefix | reuse 100%, `prompt_n=21`, **0 evictions** | invalid — 6 conversations never exceed 8 slots |
| K=9, shared 120k prefix | reuse 99.97%, `prompt_n=42`, parks 10 / evictions 4 / 16.77 GB parked | invalid — worker traffic pins the shared prefix, main is never the victim |
| K=9, `--share-prefix small` | see below | **valid** — pressure rose and main was genuinely evicted |

The lab now marks such cells `valid: false` and refuses to score them (`gate_pass: null`).

## Results (K=9, workers on a 150-token system prompt, main keeps its 120k)

| Arm | Config | Probe reuse | `prompt_n` | cached | TTFT | Pressure (parks / evictions / parked) |
|---|---|---|---|---|---|---|
| A `notier` | no SSD tier | **0.0%** | **140,072** | 0 | **53.5 / 54.2 s** | 10 / 2 / 8 → 21 / 13 / 8 |
| B `tier` | `--conversation-spill-dir … --conversation-spill-mib 24576` | **100%** | **21** | 140,051 | **2.54 / 2.15 s** | identical |
| C `tier-par2` | B + `"parallel": 2` | **100%** | **21** | 140,049 | **3.42 / 3.04 s** | identical |

Engine log for the tier arms:

```
spilled 140071 tokens to the SSD tier (evicted from RAM)
restored 140051 tokens (checkpoint) in 213.3 ms
```

**Speedup on main return after eviction: 53.8 s → 2.3 s (≈23×).** Restore from SSD itself is 213 ms; the
remaining ~2 s is scheduling/probe overhead.

## Verdict

- **Adopt the SSD tier** (already on in the installed config): it converts the exact production symptom —
  an idle main conversation evicted by subagent traffic — from a full 140k re-prefill into a 213 ms
  checkpoint restore, with 100% prefix reuse.
- **It coexists with `parallel: 2`**: reuse stays 100% and the second slot does not block the tier
  (`generate.cpp`'s `--batch` refusal applies to slot *session files*, not the conversation cache). Cost is
  ~0.9 s on the return (3.0–3.4 s vs 2.1–2.5 s).
- Tuning: keep `parallel: 1` for interactive use (C1 measured −14% single-stream decode at 2 slots); the
  tier removes the reason to batch for latency.

## Arms D/E — dropped with reason

D (`strata_prefix`) and E (thin checkpoint ladder) only make sense when subagents **share** main's prefix
as a pinned object. The k=9 run measured that regime: full sharing keeps main resident regardless of tier
(`reuse 99.97%`, `prompt_n=42`), so there is nothing for a pinned prefix or a rewind ladder to save. In the
production shape (workers share a ~150-token system prompt) the tier alone already gives 100% reuse at
2–3 s. Both arms are therefore moot for this workload; they remain available (`--share-prefix full`) if a
future client actually sends a shared long prefix.

## Caveats

- The tier is per-engine-process (`<dir>/<pid>-<nonce>`, unlocked folders deleted at start): the spill
  directory measured 9 KB after the run. It does not survive a restart — the SIGUSR1 `/slots` path stays
  the cross-reboot mechanism.
- `park-lab` reports A/C as non-gated references (`gate=None`); only B is gated (and passed).
- Two repeats per arm; the A↔B gap (54 s vs 2.3 s) is 20× the noise, so no more repetition is warranted.
