# C0 cells: engine 0.1.62 (build captured 2026-11-19 22:54 UTC)

Hardware: AMD Radeon 24560.0MiB; model `qwen3.8-flash-next`; endpoint http://127.0.0.1:20080
Background during run: pulse stopped; bridge off (OMP_BRIDGE_SETTINGS=/dev/null); driver = deepseek-v4-flash; post-install
generator_sha256: 2b38f7c043c510e85afd96d63062ead455aa65fce8e241cc7f9771fa4f7b9fa9
agents_shared_head: da2237e
agents_shared_dirty: 1 entries

Commands (verbatim, strata-tuning.md §12.7):
```
omp bench qwen3.8-flash-next --profile generation --runs 3  # cell A rc=0 94s
omp bench qwen3.8-flash-next --profile mix --prefill-bytes 120000 --runs 6  # cell B rc=0 99s
```

| Cell | Result lines (p50/summary from omp bench) |
|---|---|
