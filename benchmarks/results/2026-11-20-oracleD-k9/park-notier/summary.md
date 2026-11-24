# Strata park-churn lab — Oracle D

Generated: `2026-11-20T00:10:16+00:00`  
Output: `research/bench-results/2026-11-20-oracleD-k9/park-notier`  
Engine: `0.1.62` · endpoint `http://127.0.0.1:20080/v1` · model `qwen3.8-flash-next`  
Corpus: file /home/wuxxin/agent-shared/code/mypai/submodules/aur-packages/oh-my-pi-git/src/oh-my-pi/packages/coding-agent/src/prompts/bench/cache-prefix-chunk.md  
Token sizing: tiktoken cl100k_base (estimates only; `timings.prompt_n` is authoritative)  
Background: unrecorded — state which services were running

Protocol: main conversation warmed to the whole shared system prompt, `--idle-seconds 15`, then K=9 subagent conversations of 3 turns (+4096, +6144, +8192 tokens each), then a one-token probe on the main conversation. Cells in this file: 1; repeats per arm in this invocation: 1.

## Gate

Arms B/D/E pass when the per-arm median prefix reuse is >= 95% and the median client TTFT is <= 3 s. Arms A and C are reference cells (baseline / exploratory) and are reported without a gate verdict.

| Arm | Cells (ok/total) | Median reuse % | Median TTFT ms | Median prompt_n | Median cached tok | Median decode t/s | Refusals delta | Gate |
|---|---|---|---|---|---|---|---|---|
| A | 1/1 | 100.0 | 1425 | 42 | 140037 | 41.5 | - | n/a (reference) |

## Cells

| Arm | Rep | Timestamp | ok | cached | prompt_n | reuse % | TTFT ms | decode t/s | Refusals delta |
|---|---|---|---|---|---|---|---|---|---|
| A | 1 | 2026-11-20T00:10:16+00:00 | yes | 140037 | 42 | 99.97 | 1425 | 41.5 | - |

## Arm configuration this invocation assumed

**A** — baseline: no persistence tier (today, --disk-spill removed)

- fixed baseline (unchanged in every arm): --conversation-cache-slots 8 --conversation-cache-mib 16384 --conversation-cache-min-free-mib 6144 --conversation-cache-min-tokens 4096 --conversation-cache-park-gain 2048 --prompt-cache 6
- no --conversation-spill-dir / --conversation-spill-mib and no --disk-spill

Restart / verification for this arm (operator runs it; never executed here):

- ensure the launch command has no --disk-spill and no spill flags
```bash
systemctl --user restart local-chat-strata
```
- (the operator runs this between arms; this script never restarts the engine)

## Notes and deviations from plan §5

- The shared prefix is the **entire system prompt** of the main conversation (sized by `--warm-tokens`); every subagent sends the same literal bytes, so reuse is measurable token-for-token.
- `strata_prefix` is sent as `{"messages": 1}` — the form the engine documents (`resolve_prefix`); a bare `true` is a malformed field and returns 400.
- The driver never restarts the engine. Cache state is busted per cell with a fresh nonce in the shared prefix; the operator restarts between arms (A/B/C) or applies D/E's flags.
- Per-cell engine restarts (plan §3) are not performed: each restart costs a model load, and `--repeat` cells deliberately share one engine so the tier state carries across repeats the way it does in production.
- Plan §3's A B B A interleave is operator choreography here: one invocation measures one arm, and arms alternate across invocations with the restart shown above between them.
- Conversation-cache `parked/bytes/evictions/refused{reason}` come from `/metrics/prometheus` (fallback `/metrics` JSON), not from journalctl; the counters are engine-process scoped, exactly like the journal lines.
- Whether the burst actually caused churn is read from those counters, not assumed: if `evictions` and `refused{budget|ram_floor}` stay 0, the engine kept every conversation and the cell cannot show a tier effect. Raise `--k` or `--warm-tokens` for more pressure and re-run the arm.
- TTFT is the first streamed delta (content or reasoning) after the POST. `enable_thinking` is false on every request so the probe is a true one-token turn.
- Arms A/B/C are configuration-only: this script prints the restart command and cannot verify it was applied. Check the row's `engine`/`reuse_pct` before trusting the cell.
