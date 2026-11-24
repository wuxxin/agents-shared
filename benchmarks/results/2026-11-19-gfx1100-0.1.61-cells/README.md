# C0 cells: engine 0.1.61 (build captured 2026-11-19 21:48 UTC)

Hardware: AMD Radeon 24560.0MiB; model `qwen3.8-flash-next`; endpoint http://127.0.0.1:20080
Background during run: pulse stopped; omp driver = deepseek-v4-flash; bridge extension loaded but not firing (no hook processes, no ~/.claude or lifeos state writes in window; OMP_BRIDGE_SETTINGS unset); no other GPU consumer; engine idle (0 req/25s) before run; engine NOT restarted -> 4 slots carried prior parked state (incl. this session's ~22k context)
generator_sha256: e318d514a9de6148589099e2bc57dedd95d049dbb24e1ac1c319ebf652a1ac7e
agents_shared_head: da2237e
agents_shared_dirty: 0 entries

Commands (verbatim, strata-tuning.md §12.7):
```
omp bench qwen3.8-flash-next --profile generation --runs 3  # cell A rc=0 88s
omp bench qwen3.8-flash-next --profile mix --prefill-bytes 120000 --runs 6  # cell B rc=0 97s
```

| Cell | Result lines (p50/summary from omp bench) |
|---|---|
| A |   ✓ run 1/3 TTFT 3.0s tok/s 65.7 gen 72.6/s in 78 out 2K total 31.2s<br>  ✓ run 2/3 TTFT 31.9s tok/s 34.4 gen 73.9/s in 78 out 2K total 59.6s<br>  ✓ run 3/3 TTFT 29.6s tok/s 36.1 gen 75.7/s in 78 out 2K total 56.7s<br>model                         TTFT p50  p95    decode  cost/run<br> |
| B |   ✓ run 1/6 chat       TTFT 1.0s tok/s 62.9 gen 71.8/s in 70 out 512 total 8.1s<br>  ✓ run 2/6 prefill    TTFT 16.2s prefill 1370/s in 22K out 24 total 16.5s<br>  ✓ run 3/6 generation TTFT 31.5s tok/s 34.2 gen 72.1/s in 78 out 2K total 59.9s<br>  ✓ run 4/6 chat       TTFT 30.4s tok/s 13.6 gen 70.7/s in 69 out 512 total 37.6s<br>  ✓ run 5/6 prefill    TTFT 18.8s prefill 1182/s in 22K out 22 total 19.0s<br>  ✓ run 6/6 generation TTFT 13.1s tok/s 49.9 gen 73.4/s in 78 out 2K total 41.0s<br>model                         TTFT p50  p95    tok/s  prefill  decode  cost/run<br> |

Raw captures: `raw/omp-bench-*.txt`, `raw/journal-{A,B}.log`, `raw/status.json`.
