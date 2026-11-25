# Strata Inference Engine — Host Architecture, Tuning & Benchmark Reference

**Host:** `power` (`Gigabyte B550 AORUS ELITE AX V2`, BIOS `F19d`, Manjaro Linux `7.2.14`)  
**Hardware:** AMD Ryzen 7 PRO 5750G (8C/16T, AVX-2, PCIe 3.0 limit) + 128 GiB DDR4-2666 ECC (`117.76 GiB` `MemTotal`) + ASRock AMD Radeon RX 7900 XTX (`gfx1100`, 24 GiB VRAM)  
**Model:** `Qwen3.8-Flash-Next` (`Swift-1.5 GSQ-RCO IQ3_S` + BF16 `mmproj` + bilingual `mtp/rt`)  
**Current Stack:** `strata-engine-git-hip 0.2.21.1.r0.g2af30cc-1` (engine `0.1.67`, Control `0.1.68`, ROCm `7.2.4`, `hipblaslt 7.2.4-1`)  
**Updated:** 2026-11-25

---

## 1. Host Hardware, Storage & Memory Architecture (`power`)

### 1.1 Hardware & PCIe / Storage Topology

| Subsystem | Specification | Effective Limits / Notes |
|---|---|---|
| **CPU** | AMD Ryzen 7 PRO 5750G (Cezanne, Zen 3 APU) | 8C/16T, 1 NUMA node, AVX-2 (no AVX-512), **PCIe 3.0 max** on CPU lanes |
| **Motherboard / BIOS** | Gigabyte B550 AORUS ELITE AX V2, BIOS `F19d` | Above 4G Decoding: **Enabled**; Resizable BAR: **Enabled** |
| **System RAM** | 128 GiB (`4 × 32 GiB` Micron DDR4-3200 ECC 2R) | Runs at **2666 MT/s** (4-DIMM 2R JEDEC); ECC active (`edac mc0`, 0 errors) |
| **Visible Linux RAM** | **`117.76 GiB`** (`123,480,708 kB`) | 128 GiB − 8 GiB iGPU UMA − 2.24 GiB kernel/ACPI/E820 (was `109.89 GiB` at 16 GiB UMA) |
| **Swap / ZRAM** | `/dev/zram0`: 32 GiB (`zstd`, prio 100) | `vm.swappiness=100`, `vm.page-cluster=0`, `zswap=Y` (`max_pool_percent=20`); no disk swap |
| **Discrete GPU (`03:00.0`)** | ASRock RX 7900 XTX (`Navi 31` / `gfx1100`) | `24,560 MiB` VRAM, `32 GiB` BAR0, `60,293 MiB` GTT; CPU root port **PCIe 3.0 ×16** (~12–15 GB/s) |
| **Integrated GPU (`0a:00.0`)** | AMD Radeon Graphics (`Cezanne` / `gfx90c`) | **8,192 MiB** UMA carveout (~1.84 GiB active); drives GNOME/Wayland desktop (isolates 7900 XTX VRAM). Can lower UMA to 2–4 GiB for +4–6 GiB host RAM. |
| **OS Storage (`rpool`)** | 2 × Samsung 980 PRO 1 TB (`enczfs` mirror) | **PCIe 3.0 ×4** (~3.2–3.5 GB/s raw). Dedicated KV spill dataset **`rpool/data/user-cache`** (`/home/wuxxin/.cache/user-cache`, `compression=off`, `sync=disabled`, `recordsize=1M`, `primarycache=metadata`, `secondarycache=none`, `com.sun:auto-snapshot=false`). |
| **Model Storage (`dpool`)** | 2 × Samsung 870 QVO 8 TB (SATA mirror, ~500 MB/s) | Hosts `/data/public/machine-learning` (ZFS `ro`); `atime=off`, `logbias=throughput`, NVMe `logs` mirror, 116 GiB NVMe L2ARC (`nvme*p4` via `by-id`). |

### 1.2 Software Stack, Model Artifacts & Routing

- **Routing:** `omp` / LifeOS Pulse (`:31337`) / hooks → `local-router.service` (`http://127.0.0.1:21080/v1`) → `local-chat-strata.service` (`http://127.0.0.1:20080/v1`).
- **Package binaries (`/usr/lib/strata/engine/`):** `strata` (main HIP, zero `libggml`/`libllama` linkage since `0.2.16`), `strata-q36`, `strata-inkling`, `strata-hy4` (system `zstd`), `strata-vision-hip` (GPU), `strata-vision` (CPU fallback), `strata-gguf`, `strata-dequant`, `strata-plan`.
- **Service & config files:** `assistants/local-chat-strata.sh` + `scripts/strata-launcher.py` → `~/.config/systemd/user/local-chat-strata.{service,env,-config.json,-launcher.py}`; runtime state in `~/.local/state/strata/` (`local-chat-strata-hipblaslt.txt` 48-row `gfx1100 100202` table, `local-chat-strata-profile.bin`).
- **Host limits:** `/etc/security/limits.d/99-strata-memlock.conf` (`memlock unlimited`), `/etc/systemd/user.conf.d/memlock.conf` (`DefaultLimitMEMLOCK=infinity`), `/etc/modprobe.d/zfs.conf` (`zfs_arc_max=12 GiB`, `zfs_arc_min=2 GiB`, `l2arc_write_max/boost=512 MiB/s`).
- **Model artifacts (`/data/public/machine-learning/models/strata/swift15_iq3s`, provenance in `~/.local/share/strata/PROVENANCE.json`):**
  - Shard 1 (`42G`, native IQ3_S + expert arena + PLE index) & Shard 2 (`37G`, PLE n-gram table)
  - `packs/swift-iq3_s` (`1.5G`), `mmproj-Swift-Qwen3.8-Flash-Next-BF16.gguf` (`866M`), `mtp/rt` (`787M`, bilingual `draft_vocab.bin`)
  - Canonical ESP refusal/speed projection & `expert-profile.bin` (`192K`, 24,576 ranked pairs) from `/usr/share/strata/terminal/data/`
  - Optional `dflash2/` pack (`522M` Q4_0; kept on disk, not production default).

### 1.3 End-to-End Host Memory Budget (`117.76 GiB` `MemTotal`)

| Memory Consumer | Footprint | Backing / Pinning | Operational Behavior |
|---|---|---|---|
| **PLE Table (Shard 2)** | **26.82 GiB** | `mlock()`ed host RAM | Zero page faults / zero disk reads during ingestion (`--ple-io ram`) |
| **Expert Arena (24,576 experts)** | **46.84 GiB** | `cudaHostRegister(PORTABLE)` | Permanent RAM residency (`STRATA_ARENA_RELEASE=0`); zero NVMe churn on VRAM evictions |
| **Pinned Host KV Ring** | **0 GiB** *(was 2.19 GiB)* | Reclaimed via `--kv-grow` | Replaced by elastic in-VRAM HIP VMM (`0.21–2.46 GiB` VRAM) |
| **Vision Sidecar + Runtime** | ~1.0–1.5 GiB | Anon RAM (+956 MiB VRAM) | `strata-vision-hip` (`--vision`, 1024 tokens, `"gpu": true`) |
| **Strata Pinned Floor Total** | **73.66 GiB** | Unswappable OS floor | Baseline resident before parked conversations |
| **Conversation Cache (RAM Tier)** | 0.5–16.0 GiB (cap `16384 MiB`) | Anon DDR4 RAM | 8 slots, `--conversation-cache-min-free-mib 6144`, `min-tokens=4096`, `park-gain=2048` |
| **Persistent SSD Spill Tier** | 0 GiB RAM (cap `24576 MiB` NVMe) | `rpool/data/user-cache/conv-spill/fp-<hash>/` | `--conversation-spill-persist`: survives restarts/reboots, self-managed LRU, no external janitor |
| **OpenZFS ARC** | 2.0–12.0 GiB | Kernel slab | Hard-capped at 12 GiB in `/etc/modprobe.d/zfs.conf` |
| **AMDGPU GTT + Desktop Apps** | ~6.5–13.0 GiB | Reclaimable / ZRAM-swappable | `0 B` swap used in steady state |
| **`MemAvailable` Headroom** | **16.0–19.0 GiB** | Free / reclaimable | Eliminates `GFP_KERNEL` stalls and OOM cascades |

---

## 2. Current Production Configuration (`v0.2.21.1` / Engine `0.1.67`)

Canonical source: [local-chat-strata.sh](file:///home/wuxxin/agent-shared/code/mypai/submodules/agents-shared/assistants/local-chat-strata.sh) & [strata-launcher.py](file:///home/wuxxin/agent-shared/code/mypai/submodules/agents-shared/scripts/strata-launcher.py).

- **Context, KV & Caching:** `--max-context 240384`, `--kv k8v4`, `--kv-grow`, `--prefill 24576`, `--prompt-cache 6`, `--conversation-cache-slots 8`, `--conversation-cache-mib 16384`, `--conversation-cache-min-free-mib 6144`, `--conversation-cache-min-tokens 4096`, `--conversation-cache-park-gain 2048`, `--conversation-spill-dir ~/.cache/user-cache/conv-spill`, `--conversation-spill-mib 24576`, `--conversation-spill-persist`, `STRATA_SLOT_RAM_RESERVE_GIB=8`.
- **Lifecycle & Reclaim:** `LCHAT_STRATA_IDLE_UNLOAD=0` (weights stay warm in VRAM indefinitely), `LCHAT_STRATA_IDLE_CACHE_CLEAR=3600` (1 h idle timer + `SIGUSR1` pre-suspend hook send `CLEAR_CACHE` via `strata-clear-cache.patch`, which evicts parked RAM conversations through `evict_sink` into the persistent SSD tier, waits for `spill_writer`, shrinks idle pools, and trims heap). Legacy `_run_prune()` janitor and default `slot_save_path` retired.
- **Drafting & Sampling:** `"drafting": "mtp"`, `--spec 4`, `--spec-min-p 0.58`, `--suffix-draft 3`, `--lookup-chain 2`, `"arch": "qwen4exp"`, `"presence_penalty": 0.0` (neutralizes instruct-mode penalty that suppresses greedy MTP), `temperature=0.6`, `repetition_penalty=1.1`, `top_p=0.95`, `top_k=20`. `LCHAT_STRATA_PARALLEL=1` (default; `LCHAT_STRATA_BATCH_MTP_FUSED=0`).
- **Expert Offloading & `gfx1100` Kernels:** `--expert-cache auto` (`8,323` VRAM slots = `15.79 GiB` VRAM), `--vram-reserve-mib 576`, `--pcie-frac 0.20`, `--adapt-async 1`, `--adapt-every 1`, `--adapt-swaps 160`, `--adapt-decay 0.97`, `--ple-io ram`, `STRATA_ARENA_RELEASE=0`, `HSA_USERPTR_FOR_PAGED_MEM=1`, 48-row `STRATA_HIPBLASLT_TUNING` (`100202`), `STRATA_PREFILL_RING=512`, `STRATA_GR_FUSED=1`, plus the Round 1–4 `gfx1100` kernel fusion set (`STRATA_DENSE_MMQ` removed as dead no-op since `0.2.16`).
- **CPU Pinning:** 7 expert-pool workers on logical CPUs `1–7`, host thread on CPU `0` (`--host-core first`), `nice +5`.

---

## 3. Benchmark Protocol & Isolation Rules

- **Isolation:** Stop `local-chat-strata.service` and `omp.service` (Pulse `:31337`), set `OMP_BRIDGE_SETTINGS=/dev/null` (silences `OmpHooksBridge.ts`), and pass `PI_CODING_AGENT_DIR=omp/agent` with model `llama.cpp/qwen3.8-flash-next` (`omp` 19.1.1 fuzzy-matches bare `qwen3.8-flash-next` to `vercel-ai-gateway`).
- **Warm-up & Measurement Invariants:**
  1. Discard cells taken within ~10 min of a fresh restart (cold engine reads ~7% low on decode: `66.7 → 71.3 tok/s`).
  2. Never use `omp bench` TTFT as the prefill verdict (park/admission stalls sit inside TTFT); always read the engine log line `prompt N tokens = R reused + Y read in X ms`.
  3. Pass `--par 1` explicitly for single-stream Oracles A & B (`omp bench` defaults `--par` to 4).
- **Oracles:**
  - **Oracle A (Decode):** `omp bench llama.cpp/qwen3.8-flash-next --profile generation --par 1 --runs 3`
  - **Oracle B (Cold 22K Prefill + Mix):** `omp bench llama.cpp/qwen3.8-flash-next --profile mix --par 1 --prefill-bytes 120000 --runs 6`
  - **Oracle C (4-Way Concurrency):** `omp bench llama.cpp/qwen3.8-flash-next --detailed --par 4 --prefill-bytes 120000 --runs 3`
  - **Oracle D (Park-Churn):** `benchmarks/strata-park-lab.py` (warm 120K main + `K=9` > 8 slots with small 150-token worker prefix so workers don't pin main's prefix).
- **Result storage:** All dated run archives live untracked under `scratch/benchmark-results/`.

---

## 4. Grand Tuning Progression Scorecard

| Metric | Stock (`TEST-00`, Nov 5) | Round 1 (`PROD-WIN`) | Session 4 (`0.1.59.1` `T4-FINAL`) | Session 5 (`0.2.16` `S5-C0`) | **Session 6 (`0.2.21.1` + `GR_FUSED`)** | Total Gain vs Stock |
|---|---|---|---|---|---|---|
| **22K Cold Prefill (engine)** | 1,296–1,310 tok/s (`17.1 s`) | 1,486–1,519 tok/s (`14.6 s`) | 2,547–2,685 tok/s (`8.3 s`) | 2,672–2,673 tok/s | **2,672–2,704 tok/s** (`8.2 s`) | **+107% (2.07×)** |
| **Sustained Decode (Oracle A)** | 54.3–63.7 tok/s | 68.6–76.4 tok/s | 71.5–77.9 tok/s (med 73.9) | 70.6 med (−4.5%) | **74.6 (`base`) / 76.4 (`GR_FUSED`)** | **+26% to +41%** |
| **Chat Decode / 31K Bench** | 68.5–70.6 tok/s | 72.8–75.2 tok/s | 74.4–79.8 tok/s | 77.3 (agent) | **80.7 tok/s** (`local-bench` 31K→1K) | **+15%** |
| **22K Conv Park Cost** | ~1,900 ms | ~1,900 ms | ~1,900 ms | **72.2 ms** | **84.4–90.8 ms** | **~22× cheaper** |
| **Evicted 140K Main Return** | 53.8 s cold prefill | 53.8 s cold prefill | 463 ms manual `/slots` | **2.3 s** (213 ms SSD restore) | **Persists across restarts** (`344.8 ms` flush) | **~23× faster** |
| **Pinned Host RAM Floor** | 75.85 GiB | 75.85 GiB | **73.66 GiB** (`--kv-grow`) | 73.66 GiB | **73.66 GiB** (0 B swap) | **−2.19 GiB** |
| **VRAM Headroom** | 170 MiB (OOM risk) | 636 MiB | 670–702 MiB | ≥576 MiB reserve | **≥576 MiB reserve** | Zero OOM |

---

## 5. Round 1 (Phases 1–3, Nov 5–8): Prefill, MTP & Disk-Spike Elimination

| Test ID | Change | Prefill (22K) | Decode (p50) | Verdict & Reasoning |
|---|---|---|---|---|
| `TEST-00` | Stock defaults (`hipBLASLt 100500` mismatch → `hipBLASEx`) | 1,303 tok/s | 63.2 tok/s | Baseline; silent GEMM fallback discovered in startup log. |
| `TEST-01` | `STRATA_PLE_COMPACT=1`, `STRATA_PLE_COPY_STREAM=1` | 1,305 tok/s | 67.3 tok/s | 7× PCIe PLE reduction (10.2 KB → 1.44 KB IQ4_NL/tok) overlapped with Layer 0. |
| `TEST-02` | + `STRATA_PF_PAD=1` + matched `gfx1100-hipblaslt-100202.txt` | 1,301 tok/s | 65.3 tok/s | +64 stride pad eliminates 4 KB MCD channel camping at `K=6144`; 26 tuned GEMM rows active. |
| `TEST-03` | + `HC_UPMIX`, `PF_HCDOWN`, `CVEC_FUSE`, `HC_REGION`, `PREFILL_WARM`, `AUTO_MAX=16384` | **1,478 tok/s** | **68.8 tok/s** | **+14.3% prefill**: collapsed layer 4–44 HC/cvec VRAM round-trips; 2 chunks instead of 3. |
| `TEST-04` | + `STRATA_MMQ_DIRECT=1`, `MMQ_GROUP_SORT=1` | 1,385 tok/s | 51.0 tok/s | **Discarded:** slot-guard stalls clashed with adaptive swaps (decode dropped to 37–51 tok/s). |
| `TEST-05/06` | `AUTO_MAX=32768` / `PREFILL_RING=512` (before reserve) | 1,629 / OOM | 64.4 / OOM | **Discarded:** <100 MiB VRAM left caused `mtp: round capture: out of memory`. Fixed via `--vram-reserve-mib 512`. |
| `GEN-01` | `LCHAT_STRATA_SPEC_MIN_P=0.60` (vs `0.70` stock `54.3`) | 1,490 tok/s | **68.5 tok/s** | **+26.1% decode**; `0.55` (`GEN-A1`) collapsed to **30.0 tok/s** (−56% rollback cascade). |
| `GEN-02/03/05` | `spec=5` (`58.5`), `lookup-chain=2` on short ctx (`63.7`), `adapt-swaps=200` (`63.1`) | — | 58.5–63.7 | **Discarded:** 5th draft FLOPs & swap churn hurt; kept `spec=4`, `swaps=160`, `decay=0.97`. |
| `PAR-01/03/05` | `prompt-cache-every 4096` (`64.5`), `--short-read 128` (`61.0`), `--batch 2` (`61.8`) | 1,468–1,487 | 61.0–64.5 | **Discarded:** 4k checkpoints stalled prefill; `--batch 2` cost 1.65 GiB VRAM (9,004→8,077 slots). |
| `PAR-WIN` | `prompt-cache 6`, `slots 6`, `mib 24576`, `STRATA_ARENA_RELEASE=0`, `RLIMIT_MEMLOCK=infinity` | **1,481 tok/s** | **69.0 agg@4** | **Eliminated 100–300 MB/s SSD read spikes** (PLE locked in RAM, expert arena never `MADV_DONTNEED`'d). |

---

## 6. Session 4 (`0.1.59.1`, Nov 12): RDNA3 Round 2, Drafters & Elastic KV

**Key architectural discoveries:**
1. `arch_defaults.cpp` left `gfx1100` empty in `0.1.59.1`, leaving 19+ compiled gfx11 WMMA/GDN/decode kernels idle unless set explicitly.
2. `STRATA_HIP_WMMA=1` without `STRATA_PREFILL_RING=512` silently drops the streaming ring `512 → 96` (`prefill.cpp:434`), causing a −6.7% prefill regression (`1,841 → 1,704 tok/s`). Pinning `STRATA_PREFILL_RING=512` recovered overlap and broke `2,000 tok/s`.
3. Explicit `--prefill 24576` + 48-row calibrated `gfx1100-hipblaslt-100202.txt` (via `tune_hipblaslt.cpp`, adding `T=16384` and missing `bf16`/`f16` shapes) enabled single-pass 22K prefill.
4. `--kv-grow` (HIP VMM) eliminated the 2.19 GiB pinned host KV ring, expanded VRAM expert cache to 9,024 slots, and grew/shrank KV elastically (`43,217`-token prompt grew KV to `49,152` cells / `0.52 GiB`, then returned 209 slots).

| Test ID | Configuration | Oracle A (`--par 1`) | Oracle B 22K Prefill | Slots / Free VRAM | Verdict |
|---|---|---|---|---|---|
| `S4-BASE` | `PROD-WIN` on `0.1.59.1` | 70.4 p50 | 1,827–1,841 tok/s (`12.1 s`) | 9,004 / 632→504 MiB | Baseline |
| `PF2-1` | `GDN_*`, `HIP_WMMA`, `PA_FAST`, `SELECT_WMMA`, `PF_F16/DM16` | — | 1,704–1,721 tok/s | 9,004 / 504 MiB | −6.7% (ring dropped to 96) |
| `PF2-2` | `PF2-1` + `PREFILL_RING=512` + `PREFILL_ROUTED_STREAM=1` | — | 1,996–2,023 tok/s (`11.0 s`) | 9,004 / 499 MiB | +10.2% prefill |
| `PF2-4` | + `--prefill 24576`, `--vram-reserve-mib 576`, 48-row hipBLASLt, `HSA_USERPTR=1` | — | 2,190–2,228 tok/s (`10.0 s`) | 8,973 / 684 MiB | Single-pass 22K, +21% |
| `GEN2-1` | + `Q8_PACKED`, `MMVF_ROWS`, `ATTN_LANECELL/MERGE_V2`, `EXPERT_V2`, `TSUM`, `LFUSE`, `GDN_SPLIT`, `QFUSE`, `PLE_BATCH`, `SMALL_UNR=3`, `GR_Q32_G=2`, `GR_Q8_PFS=1`, `HEAD_MIX_MULTI`, `FUSE_HITS/WAIT`, `VERIFY_QDEDUP` | 69.5 p50 | **2,543–2,555 tok/s** (`8.7 s`) | 8,973 / 684 MiB | **+39% prefill**, chat up to 75.5 tok/s |
| `GEN2-2/3/4` | DFlash2 (`q4_0-selq4` & `strata1`, conf `0.8`/`0.5`, `spec=6`) | 67.6–69.9 p50 | 2,544–2,573 tok/s | 9,097 / 702 MiB | Lagged Swift-1.5 MTP (47.8–51.8% accept) |
| `GEN2-5` | **Tuned MTP** (`SPEC_COST=1`, `FUSE_HEAD_GR=1`, `NORM_ROPE=1`, `spec-min-p 0.58`, `lookup-chain 2`) | **71.5 p50** (73.5–77.9) | — | 8,973 / 670 MiB | **Winner** (54.7% accept); `--mtp-q4 all` (`GEN2-6`) tied p50 with lower peak (`74.2`), discarded |
| `T4-KVGROW` / `T4-FINAL` | + `--kv-grow`, `slots=8`, `mib=16384`, `min-free=6144`, `min-tok=4096`, `park-gain=2048` | 67.1–71.5 p50 | **2,547–2,685 tok/s** (`8.3 s`) | 9,024 / 670 MiB | −2.19 GiB pinned RAM; 43K NVMe save `855 ms`, restore `463 ms` (`1,667 MB/s`, 36× faster, 99.96% KV hit) |

---

## 7. Crash Forensics & S3 Suspend Architecture (Nov 10–14 Resolution)

1. **Nov 10–12 Live OOM Storms (`amdgpu_hmm_range_valid` Kernel Oops, `27.4 GiB` ZRAM saturation):**
   - *Cause:* Uncapped OpenZFS ARC (`c_max=116.76 GiB`), 16 GiB iGPU UMA leaving only `109.89 GiB` `MemTotal`, and overlapping restarts with `75.85 GiB` unswappable Strata floor.
   - *Resolution:* Reclaimed +7.87 GiB via BIOS UMA `16G → 8G` (`MemTotal=117.76 GiB`), capped ZFS ARC to `2–12 GiB` in `/etc/modprobe.d/zfs.conf`, enabled `--kv-grow` (−2.19 GiB pinned RAM), enforced `--conversation-cache-min-free-mib 6144` + `min-tokens=4096`, and set `StartLimitBurst=3` / `RestartSec=30s`. Result: 40+ h uptime with **0 OOMs and 0 B swap**.
2. **Nov 14 05:07 S3 Deep-Suspend Hang (`amdgpu_device_evict_resources`):**
   - *Cause:* On S3 sleep, `amdgpu` must evict ~24 GiB VRAM into host RAM while userspace is frozen and OOM killer is disabled; with ~82.5 GiB resident in RAM (~16 GiB free), `ttm_pool_alloc` deadlocked. (`--vram-elastic` is CUDA-only.)
   - *Current `v0.2.21.1` Architecture:* `LCHAT_STRATA_IDLE_UNLOAD=0` keeps VRAM warm during active use (disable GNOME AC auto-suspend or rely on the sleep hook); `LCHAT_STRATA_IDLE_CACHE_CLEAR=3600` + `/usr/lib/systemd/system-sleep/local-chat-strata.sh` (`SIGUSR1`) invoke our upgraded `CLEAR_CACHE` patch, flushing all parked RAM conversations into `--conversation-spill-persist` on NVMe and trimming host heap.

---

## 8. Session 5 (`0.2.16`, Nov 19–20): Own-Stack Cutover, C0–C3 & Oracle D

Strata `0.2.16` removed all `ggml`/`llama.cpp`/`mtmd` linkage (`STRATA_OWN_CPU_QUANT=ON`), moved to `terminal/`/`engine/`/`tools/`, and introduced the conversation-cache SSD tier (`#5697 P2`).

| Cell | Arm A vs Arm B | Result | Verdict |
|---|---|---|---|
| **C0 Gate** | `0.1.61` warm (`73.9` med, `2,681` pf) vs `0.2.16` warm (`70.6` med, `2,673` pf, park `72.2 ms`) | Decode −4.5% (cold 5-min start was 68.6, −7%); prefill parity; park **26× cheaper** | Pass (attributed −4.5% to `STRATA_OWN_CPU_QUANT`) |
| **C1 Batching** | `parallel=1` (`71.5` solo, 4-way TTFT `7.6–9.0 s`, agg `67.4`) vs `parallel=2` (`60.3` solo, TTFT `0.15–2.6 s`, agg `66.8`, −1.42 GiB VRAM / `7,633` slots) | −14% warm / −28% cold solo decode; 5–10× lower queue TTFT | Keep `parallel=1` default |
| **C2 Drafter** | MTP `spec=4` (**68.5**, 59.5% acc) vs DFlash2 `spec=4` (`66.8`, 72.1%, −710 MiB VRAM) vs DFlash2 `spec=6` (`68.3`, 73.6%) vs MTP `spec=6 min-p 0.45` (`67.9`, −2.4%) | DFlash2 VRAM cost offsets higher accept rate; MTP `spec=6` regresses | Keep MTP `spec=4` |
| **C3 Prompt F16** | `STRATA_HIP_PROMPT_F16=1` (`2,667` mean) vs default (`2,701` mean) | **−1.3%** on `gfx1100` (gain is `gfx103x`-only) | Keep OFF |
| **Oracle D (`park-lab`, `K=9`)** | `S5-D-A` no tier (`0%` reuse, `140K` read, **53.8 s** TTFT) vs `S5-D-B` spill 24 GiB (**100%** reuse, `21` read, **2.3 s** TTFT, `213.3 ms` SSD restore) vs `S5-D-C` + `parallel=2` (**100%**, **3.2 s**) | **23× faster return** on evicted 140K main context; coexists with `parallel=2` | **Adopted** (`--conversation-spill-dir/mib`) |
| **`strata_bench.py`** | 4K (`1,294 tok/s`, `3.14 s`), 16K (`2,644 tok/s`, `6.11 s`), chat `62.0`, agent `77.3` (71.3% cache hit) | Fixed-cost model: **4,081 tok/s marginal + 2.16 s fixed/prompt**; agent re-reads 1,642 tok/turn | Baseline recorded |

---

## 9. Session 6 (`0.2.21.1` / Engine `0.1.67`, Nov 24–25): Cutover, Round 6 & Mixed Parallel A/B

Upgraded `strata-engine-git-hip` `0.2.16.r4.g58ee322-1 → 0.2.21.1.r0.g2af30cc-1` (+770 commits; B1 package scope adding `strata-q36`, `strata-inkling`, `strata-hy4`, CPU `strata-vision`, CLI utils). Key upstream wins now active: `STRATA_POOL_DEP=1` default ON (−2.9% verify window), `STRATA_HIP_FAST_DEC=1` default ON on `gfx1100`, Linux HIP NUMA-balancing disable (`#4866`), greedy API default under MTP (`#6536`), `--conversation-spill-persist`, superseded-snapshot drop (`#6833`), and HIP fix for `STRATA_GR_FUSED` (`#6730`/`#6760`).

| Test ID | Configuration | Decode (warm) | Prefill (engine log) | Verdict & Notes |
|---|---|---|---|---|
| `S6-LCHAT` | `local-benchmark` (`31,053` prompt → `1,024` out) | **80.67 tok/s** (warmup 117.8) | **2,717.9 tok/s** (`11.43 s`) | Live service via `:20080` |
| `S6-C0` | `0.2.21.1` live service (`base`, Oracle A/B) | `74.6 / 76.2 / 72.2` (med **74.6**) | `2,687.3 / 2,672.4 tok/s` | **PASS** — fully recovers `0.2.16` −4.5% delta (+5.7% vs `0.2.16`, +0.9% vs `0.1.61`); park 84–91 ms. |
| `S6-R6-base` | Exclusive GPU (`base`, 48/48 layers fused) | `71.8 / 75.3 / 79.0` (med **75.3**) | `2,703.6 / 2,676.2 tok/s` | Round 6 baseline |
| `S6-R6-gr-fused` | **`STRATA_GR_FUSED=1`** | **`75.4 / 76.4 / 77.9`** (med **76.4**) | — | **ADOPTED (+1.5% median, +3.6 tok/s floor)**; zero crashes after `#6730`. |
| `S6-R6-pf-iq2s` | `STRATA_PF_FUSED_IQ2S=1` | `69.5 / 73.5 / 78.5` | `2,699.5 / 2,672.0 tok/s` | **SKIP** — no-op on `gfx1100` (already 48/48 fused; `gfx12`-only flag). |
| `S6-SPILL` | `SIGUSR1` `CLEAR_CACHE` + `--conversation-spill-persist` | — | — | **VERIFIED** — flushed 8,926-tok (330 MiB) parked conv to `fp-825c7f4b4b76c785/conv-1.session` in **344.8 ms** (`CLEARED 1`); next start adopted `1 conversation, 330 MiB`. |
| `S6-MIX-p1` | `parallel=1` (53.9K `omp` + 2×8K `side` + 4×1K `lifeos`, 2,008 out) | **79.0–89.2 tok/s**; agg **48.71** (`41.23 s`) | **2,747 tok/s** (53.9K in `19.63 s`) | **WINNER** — 8,323 VRAM slots, full `--spec 4` clears burst 20% faster. |
| `S6-MIX-p2` | `parallel=2` + `STRATA_BATCH_MTP=1` + `STRATA_BATCH_MTP_FUSED=1` | 19.8–41.0 tok/s; agg **40.56** (`49.51 s`) | 2,465 tok/s (53.9K in `21.88 s`) | **KEEP OFF** — loses 804 VRAM slots (−1.53 GiB), amplifies CPU misses across concurrent streams, caps MTP to 1 proposal/slot. |

**Notes from Session 6:**
- **`STRATA_DOT_X4=1` & `STRATA_POOL_DEP=0`:** Left at upstream defaults (`DOT_X4` off per `#6552` DRAM-bound regression; `POOL_DEP=1` on per −2.9% window win). Direct back-to-back battery restarts occasionally hit a ROCm 7.2.4 KFD VMM page fault at `generate.cpp:7759` (`session_zero()`), independent of CPU-pool flags; production is unaffected (`LCHAT_STRATA_IDLE_UNLOAD=0` + systemd `RestartSec=30s`).
- **`run-local-benchmark.py`:** Now auto-detects Strata (`--chat-backend auto|strata|llama`) and dispatches to `local-chat-strata.sh` with `--url` (for `--use-router`) and `--context`.
