# Strata park-churn lab — Oracle D

Generated: `2026-11-20T00:29:39+00:00`  
Output: `research/bench-results/2026-11-20-oracleD-fixed/park-tier`  
Engine: `0.1.62` · endpoint `http://127.0.0.1:20080/v1` · model `qwen3.8-flash-next`  
Corpus: file /home/wuxxin/agent-shared/code/mypai/submodules/aur-packages/oh-my-pi-git/src/oh-my-pi/packages/coding-agent/src/prompts/bench/cache-prefix-chunk.md  
Token sizing: tiktoken cl100k_base (estimates only; `timings.prompt_n` is authoritative)  
Background: unrecorded — state which services were running

Mode: Share-prefix mode `small` (production shape): the main conversation keeps the ~120000-token corpus in its system prompt; workers share a short ~150-token plain-text system prompt, so main's cache entry is the LRU victim.

Protocol: main conversation warmed to its system prompt, `--idle-seconds 15`, then K=9 subagent conversations of 3 turns (+4096, +6144, +8192 tokens each), then a one-token probe on the main conversation. Cells in this file: 2; repeats per arm in this invocation: 2.

## Gate

Arms B/D/E pass when the per-arm median prefix reuse is >= 95% and the median client TTFT is <= 3 s. Arms A and C are reference cells (baseline / exploratory) and are reported without a gate verdict. A cell with `pressure_ok: false` (no parks or evictions rose during the cell) is **invalid** and is excluded from every median and from the gate; a gated arm with no valid cell fails.

| Arm | Mode | Cells (valid/ok/total) | Median reuse % | Median TTFT ms | Median prompt_n | Median cached tok | Median decode t/s | Refusals delta | Gate |
|---|---|---|---|---|---|---|---|---|---|
| B | small | 2/2/2 | 100.0 | 2344 | 21 | 140050 | 29.7 | - | **pass** |

## Cells

| Arm | Mode | Rep | W prefix tok | ok | valid | cached | prompt_n | reuse % | TTFT ms | decode t/s | Refusals delta |
|---|---|---|---|---|---|---|---|---|---|---|---|
| B | small | 1 | 150 | yes | yes | 140051 | 21 | 99.99 | 2535 | 26.1 | - |
| B | small | 2 | 150 | yes | yes | 140049 | 21 | 99.99 | 2152 | 33.3 | - |

## Arm configuration this invocation assumed

**B** — conversation-cache SSD tier

- fixed baseline (unchanged in every arm): --conversation-cache-slots 8 --conversation-cache-mib 16384 --conversation-cache-min-free-mib 6144 --conversation-cache-min-tokens 4096 --conversation-cache-park-gain 2048 --prompt-cache 6
- --conversation-spill-dir ~/.cache/user-cache/conv-spill
- --conversation-spill-mib 24576

Restart / verification for this arm (operator runs it; never executed here):

- add to the launch command: --conversation-spill-dir ~/.cache/user-cache/conv-spill --conversation-spill-mib 24576
```bash
systemctl --user restart local-chat-strata
```
- (the operator runs this between arms; this script never restarts the engine)

## Notes and deviations from plan §5

- `--share-prefix small` (default for A/B/C): the main keeps the `--warm-tokens` corpus in its system prompt and workers share a short, byte-identical plain-text system prompt — the production shape, so the idle main is the LRU victim. `full` (default for D/E): workers inherit the main's whole system prompt, which keeps it hot but is what pinning/reuse measurements need.
- The cell nonce is in the main prefix and in each worker's first user turn, so repeats do not reuse the previous cell's parked conversations; the worker system prompt itself stays byte-identical within a cell.
- `strata_prefix` is sent as `{"messages": 1}` — the form the engine documents (`resolve_prefix`); a bare `true` is a malformed field and returns 400.
- The driver never restarts the engine. Cache state is busted per cell with a fresh nonce in the shared prefix; the operator restarts between arms (A/B/C) or applies D/E's flags.
- Per-cell engine restarts (plan §3) are not performed: each restart costs a model load, and `--repeat` cells deliberately share one engine so the tier state carries across repeats the way it does in production.
- Plan §3's A B B A interleave is operator choreography here: one invocation measures one arm, and arms alternate across invocations with the restart shown above between them.
- Conversation-cache `parked/bytes/evictions/refused{reason}` come from `/metrics/prometheus` (fallback `/metrics` JSON), not from journalctl; the counters are engine-process scoped, exactly like the journal lines.
- Whether the burst actually caused churn is read from those counters, not assumed: `pressure_ok` is true only when `parks` or `evictions` rose during the cell. Otherwise the row is `valid: false` (no eviction evidence), is excluded from the medians and the gate, and is marked invalid in the tables. Raise `--k` for more pressure: with slots=8, K=9 is the smallest burst that overflows the slot count.
- TTFT is the first streamed delta (content or reasoning) after the POST. `enable_thinking` is false on every request so the probe is a true one-token turn.
- Arms A/B/C are configuration-only: this script prints the restart command and cannot verify it was applied. Check the row's `engine`/`reuse_pct` before trusting the cell.
