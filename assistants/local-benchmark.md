# LLM Caching Optimization Benchmarks

**Context:** Testing advanced optimization flags for `llama.cpp` using the `Qwen3.6-35B` model, restricted to a **45,000 character context** with interleaved vision/text distractors.

## Benchmark Results (45k Chars)

We tested 6 configurations spanning combinations of Flash Attention (`-fa on`) and Physical Batch Size (`-ub`). and compressed K/V-Caches ('--cache-type-k q4_0 --cache-type-v q4_0')

| Configuration | Prefill Speed | Hit Latency | Cache Hit Rate | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Baseline** (`-ub 512`) | 3579 Char/s | ~863 ms | 87.5% | Stable |
| **FA** (`-ub 512, -fa on`) | 3522 Char/s | ~869 ms | 87.5% | Stable |
| **Batch 1024** (`-ub 1024`) | 4148 Char/s | ~1213 ms | 87.5% | **Optimal Balance** |
| **FA + Batch 1024** | 4123 Char/s | ~1219 ms | 87.5% | **Optimal Balance** |
| **Batch 2048** (`-ub 2048`) | 4419 Char/s | ~1922 ms | 0.0% (<1.5s limit) | Prefill Only |
| **FA + Batch 2048** | 4404 Char/s | ~1928 ms | 0.0% (<1.5s limit) | Prefill Only |

---

## Hypothesis Analysis

### 1. Flash Attention (`-fa on`)
At 45,000 characters, explicitly enabling Flash Attention continues to show a **negligible or very slightly negative impact** on both prefill speed and cache hit latency. 
**Conclusion:** On this specific hardware/backend (ROCm W6800), Flash Attention overhead currently cancels out its benefits at 45k context. It may become beneficial closer to the 100k+ mark, or it may already be implicitly enabled, or optimally managed by the backend.

### 2. Physical Batch Size (`-ub`)
The physical batch size dictates how many tokens the GPU processes in a single forward pass.
- **`-ub 512` (Default):** Lowest hit latency (~860ms), but slowest prefill. Best for highly concurrent, rapid chat applications.
- **`-ub 1024` (The Sweet Spot):** Achieves a **16% faster prefill** (4148 Char/s vs 3579) while keeping the cache hit latency at ~1.2s. This successfully maintains the 87.5% cache hit rate by staying under the 1.5s threshold limit.
- **`-ub 2048` (Max Speed):** Achieves the **maximum prefill speed** (4419 Char/s, 23% faster than baseline). However, the overhead of processing the interleaved requests in massive 2048-token chunks causes the cache hit retrieval latency to spike to almost 2 seconds, breaking the cache hit threshold.

## Final Recommendations
For your goal of aggressive caching with two 120k contexts, **`-b 2048 -ub 1024` is the absolute sweet spot**. 
It significantly boosts the initial parsing speed of large documents while keeping the retrieval latency low enough to ensure rapid responses to follow-up questions from the cached context!
