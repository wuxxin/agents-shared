# Interpretation — C0 Arm A cells, engine 0.1.61 (2026-11-19 22:44–22:48 local)

Cross-reference: `README.md` (generated), `raw/omp-bench-{A,B}.txt`, `raw/journal-{A,B}.log`.

## Bridge taint: checked, none found

Three independent checks, all negative:

1. **Hook registry contents** — `~/.claude/settings.json` registers command hooks (`$HOME/.claude/hooks/*.hook.ts`). `grep -rlnE '20080|qwen3\.8|qwen3-|strata|localhost:21' ~/.claude/hooks/` returns nothing: no hook talks to the local engine. (http-type Pulse guards are skipped by the bridge anyway — it runs command hooks only.)
2. **Hook activity** — no `*.hook.ts` process ran, and `~/.claude` plus `~/.local/share/lifeos` had **no** file writes during the window; no `lifeos-bridge` audit lines (log off by default).
3. **Engine side** — the per-cell `omp bench` processes log only `provider: llama.cpp` traffic with the in-flight limit queueing one request at a time; the engine journal shows only the cells' own sequential requests, `concurrency.serving = 1`, no interleaved foreign completions.

Conclusion: the bridge is loaded but inert here, and even if active it generates no local-model calls. It cannot taint engine measurements — only harness-side prompt text.

## The taint that IS present: warm queue

The engine was **not restarted** for this run, so cells started with parked state from earlier sessions (4 slots, including this migration session's ~22k-token context). Fingerprint in the numbers:

- Cell A run 1 TTFT 3.0 s, runs 2–3 TTFT **31.9 s / 29.6 s for a 78-token prompt** — no prefill of the prompt explains that; it is queue churn (park/evict of resident conversations plus the adaptive-tier flip) landing ahead of a trivial request.
- Cell B chat run 4: TTFT 30.4 s, `tok/s 13.6` for a 69-token prompt with 70.7 tok/s decode — same signature, end-to-end inflated by queue wait.

Treat these cells as **warm-queue**: valid for decode and cold-prefill rates, not for TTFT. Arm B (post-install) must be captured under the same condition to stay paired; a clean-queue re-run of both arms belongs in the benchmark session (engine restart, Pulse off, bridge off).

## Rates vs the §13.3–13.4 reference — reconciled (no prefill regression)

`omp bench` reports prefill from TTFT (wall time), while the engine logs the actual prompt read. Side by side:

| Cell B run | `omp bench` prefill | engine log `prompt N tokens … read in X ms` | gap |
|---|---|---|---|
run 2 | 1,370 tok/s (22K in 16.2 s) | **2,681 tok/s** (22,184 tok in 8,273 ms) | 7.9 s of admission |
run 5 | 1,182 tok/s (22K in 18.8 s) | **2,185 tok/s** (22,181 tok in 10,152 ms) | 8.7 s of admission |

Engine-side prefill (2,185–2,681 tok/s) **matches** §13's 2,543–2,685 tok/s. The bench's "half-speed" figure is the warm-queue admission cost landing inside TTFT: each new 22k conversation forces the previous one to be parked (`parked 22,207 tokens in 1,892 ms`, `22,202 in 1,930 ms`) and the request waits ~8 s before its prompt read even starts. Decode (70.7–75.7 tok/s) and park costs therefore confirm the reference; only TTFT is inflated.

Consequences:
- **Do not use bench TTFT alone for the prefill verdict.** C0 Arm B must be compared on the engine-side `prompt … read in` rates, with bench TTFT reported separately as the user-visible latency.
- No pre-upgrade investigation is warranted; the reference holds. The ~8 s admission penalty per new long conversation is the park-churn symptom Oracle D (§5) exists to fix — it is measured here in production shape for the first time.

## What to carry forward

- Arm A reference for C0: decode 70.7–75.7 tok/s; engine-side prefill 2,185–2,681 tok/s @22K; bench TTFT 16–19 s for a new 22k conversation (≈8 s admission) and clean-cell TTFT 1.0 s.
- Park evidence during the run: `parked=3..4`, parks of 22,202–22,207 tokens costing **1.89–1.93 s** each — matching the passive 48 h median (828 ms) at the upper end for 22k-token conversations.
- Next: v0.2.16+4 install, then the identical two commands into `…-<newengine>-cells`; compare engine-side prefill rates and decode first, bench TTFT second, and run Oracle D (§5) to attack the ~8 s admission penalty.
