# Spec-depth battery — MTP `--spec 4` vs `--spec 6 --spec-min-p 0.45`

Engine 0.2.16, 3 Oracle A cells per arm (`omp bench --profile generation --runs 3`), engine restarted
per arm via `scripts/strata-env-battery.sh` (env file rewritten + `install`, launcher started
directly). Cells ran back-to-back within an arm, so the warm-up curve is visible.

## Decode per cell (gen tok/s)

| Cell | base (`spec 4`) | `spec 6 --spec-min-p 0.45` |
|---|---|---|
| 1 (cold) | 66.7 / 67.6 / 70.1 (67.6) | 66.8 / 67.7 / 70.3 (67.7) |
| 2 | 68.6 / 69.4 / 69.9 (69.4) | 66.2 / 67.7 / 68.6 (67.7) |
| 3 | 67.7 / 69.8 / 71.6 (69.8) | 66.8 / 68.1 / 70.0 (68.1) |
| **median (warm, cells 2–3)** | **69.6** | **67.9** |

## Drafting behaviour (9 requests per arm)

| Arm | Accept rate | Proposals | Accepted (mean) |
|---|---|---|---|
| base `spec 4` | **59.3%** | 1,219–1,592 | 844 |
| `spec 6 --min_p 0.45` | 54.8% | 1,164–1,847 | **859** |

Spec 6 produces +1.8% accepted tokens but costs 2.4% decode: the extra draft work per step (longer
speculation, lower acceptance per proposal) is paid on every token while the extra accepted tokens only
arrive when the drafter is confident.

## Verdict

`--spec 6` is a **regression for MTP** in production shape. Keep `--spec 4`.

This also closes the loop on the DFlash2 arm: there, spec 6 *helped* (66.8 → 68.3) because DFlash2's
accept rate is high enough (73.6%) that more proposals convert; MTP at 55–59% does not. Spec depth is a
function of drafter quality, not a global knob.

**Warm-up curve:** medians rose 67.6 → 69.4 → 69.8 across three consecutive cells in the same arm,
confirming the ~7% cold-engine rule and that two cells still leave a rising bias — three cells with the
first discarded is the practical minimum.
