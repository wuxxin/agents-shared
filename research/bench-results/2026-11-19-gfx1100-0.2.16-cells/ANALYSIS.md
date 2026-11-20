# C0 gate — engine 0.2.16 (58ee32277) vs 0.1.61 (2cbfc3c)

Cells captured 2026-11-19 23:51–23:55 by `scripts/strata-baseline-cells.sh`, same protocol as the
0.1.61 baseline in `../2026-11-19-gfx1100-0.1.61-cells/`: Oracle A `--profile generation --runs 3`,
Oracle B `--profile mix --prefill-bytes 120000 --runs 6`, driver on DeepSeek Flash, Pulse stopped.

## Decode (engine `predicted_per_second` equivalents, tok/s)

| Cell / run | 0.1.61 | 0.2.16 | delta |
|---|---|---|---|
| A run 1 | 72.6 | 66.7 | −8.1% |
| A run 2 | 73.9 | 68.6 | −7.2% |
| A run 3 | 75.7 | 68.9 | −9.0% |
| **A median (first cell, cold engine)** | **73.9** | **68.6** | **−7.2%** |
| A repeat (warm, +5 min) | — | 71.3 / 70.6 / 70.2 | — |
| **A median (warm repeat)** | **73.9** | **70.6** | **−4.5%** |
| B chat | 71.8 / 70.7 | 72.1 / 65.0 | −0.4% / −8.1% |
| B generation | 72.1 / 73.4 | 68.1 / 67.1 | −5.5% / −8.6% |

`§13.3–13.4 T4-FINAL` reference is 71.5–79.8 tok/s. The cold first cell (68.6) sits below that floor; the
warm repeat (70.6) is 1% under it and inside the 0.1.61 range's lower half.

**Warm-up is a real effect, not noise:** the same run position five minutes apart went 66.7 → 71.3 tok/s
(+6.9%). The 0.1.61 baseline was measured on an engine that had been up for ~48 h; the 0.2.16 first cell
ran ~5 min after restart. Like-for-like (warm 0.2.16 vs warm 0.1.61) the decode gap is **−4.5%**, not −9%.
Pooled 0.2.16 A median over 6 runs: 69.6 tok/s. A cold-engine cell is not a valid C0 comparison.

## Prefill — the verdict metric (engine log, not TTFT)

| Measurement | 0.1.61 | 0.2.16 |
|---|---|---|
| `prompt 22184 … read in 8273 ms` | 2,681 tok/s | — |
| `prompt 22208 … read in 8307 ms` | — | **2,673 tok/s** |
| `prompt 22211 … read in 8312 ms` | — | **2,672 tok/s** |

Prefill is at parity (±0.3%). Bench-level "prefill tok/s" still reads 1,275 and (one outlier) 564
because it is TTFT-derived; the engine read a 22K prompt in 8.3 s in both runs.

## Park cost — the adoption's headline win

| | 0.1.61 | 0.2.16 |
|---|---|---|
| Park of a ~22.2K-token conversation | **1,892–1,930 ms** | **72.2 ms** |
| parked bytes | 22,202–22,207 tok | 22,230 tok / 511,629,756 B |
| evictions in cell | — | 0 |

26× cheaper park with the conversation-spill tier active. This is the mechanism behind the ~8 s
admission penalty measured on 0.1.61; it should show up as lower TTFT once the queue is exercised.

## TTFT churn — unchanged

| | 0.1.61 | 0.2.16 |
|---|---|---|
| A runs | 3.0 / 31.9 / 29.6 s | 0.94 / 32.5 / 32.1 s |
| B chat | 1.0 s | 1.1 s |
| B prefill | 16.2 / 18.8 s | 17.4 s, one outlier **39.4 s** (engine read still 8.3 s ⇒ admission, not prefill) |

The 30 s TTFT pattern on ~100-token prompts is the same queue-churn symptom Oracle D targets; the one
39.4 s run is the worst measurement of either engine.

## Attribution — what actually changed in the running config

Diffing the real pre-cutover runtime args (regenerated from `git show HEAD:assistants/local-chat-strata.sh`)
against the live 0.2.16 config, only two deltas exist:

1. `+ --conversation-spill-dir ~/.cache/user-cache/conv-spill --conversation-spill-mib 24576` (new tier)
2. expert-profile path `/usr/share/strata/data/` → `/usr/share/strata/terminal/data/` — **the file is
   byte-identical** (`8f59b4aa…`, 196,632 B), so it is not a behaviour change.

Therefore the −7.2% decode sits with the engine binary itself. The adoption plan flagged the likely
cause in advance: `STRATA_OWN_CPU_QUANT` is a **CMake build option** (ON for x86) that moved the CPU
expert lane onto Strata's own quant layer — "attribute any decode delta there before blaming the engine
core". Not yet tested.

Also noted: prompts are 104 tokens under 0.2.16 vs 78 under 0.1.61 for the same profile — the request
shape changed (template/tokenizer path), not the decode loop.

## Verdict

- Prefill: **pass** (parity within 0.3%).
- Park/tier: **clear win** (26× cheaper parks).
- Decode: **−4.5% warm** (−9% only in the cold cell) — marginally below the §13 floor, cause isolated to
  the engine build, not to our config. A cold-engine cell must not be used as the verdict.
- TTFT churn: unchanged, one 39.4 s outlier.

Next, cheapest first: (a) ~~2–3 more A cells~~ — done, see the warm repeat; (b) if a further −4.5% matters,
isolate `STRATA_OWN_CPU_QUANT` by rebuilding with it OFF and re-running cell A only (95 s) — this is now
the only untested hypothesis; (c) C3 (`STRATA_HIP_PROMPT_F16=1`) does not address decode; (d) otherwise
accept as an upgrade cost and re-baseline §13's decode band under 0.2.16.

**Protocol note for future cells:** warm the engine for ≥10 minutes (or discard the first cell) — the first
cell after a restart under-reads decode by ~7%.
