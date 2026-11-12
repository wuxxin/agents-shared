# Host `power` — Strata & Local Inference Architecture Overview

**Host:** `power` (`Gigabyte B550 AORUS ELITE AX V2`, BIOS `F19d`, Manjaro Linux `7.2.14-1-MANJARO`)  
**Updated:** 2026-11-12 (Session 4 Tuning: Tiered Memory, NVMe KV Offload & RDNA3 `gfx1100` Round 2)  
**Related Docs:** [`strata-tuning.md`](./strata-tuning.md) | [`strata-machine-crashes.md`](./strata-machine-crashes.md)

---

## 1. Hardware & PCIe / Memory Topology

| Subsystem | Exact Specification (Verified) | Effective Limits / Notes |
|---|---|---|
| **CPU** | `AMD Ryzen 7 PRO 5750G` (Cezanne, Zen 3 APU) | 8 Cores / 16 Threads, 1 NUMA node, AVX-2 (no AVX-512), **PCIe 3.0 max** on CPU lanes |
| **Motherboard / BIOS** | `Gigabyte B550 AORUS ELITE AX V2`, BIOS `F19d` (2024-09-02) | Above 4G Decoding: **Enabled**; Resizable BAR: **Enabled** |
| **System RAM** | **128 GiB** (`4 × 32 GiB` Micron `18ASF4G72AZ-3G2F1` DDR4-3200 ECC UDIMM, 2R) | Configured at **`2666 MT/s`** (4-DIMM 2R JEDEC). ECC active (`edac mc0`, 0 errors). |
| **Visible Linux RAM** | **`117.76 GiB`** (`MemTotal: 123,480,708 kB`) | 128 GiB − 8 GiB iGPU UMA − 2.24 GiB kernel/ACPI/E820 reserved (was `109.89 GiB` when iGPU UMA was 16 GiB). |
| **Swap / Compression** | `/dev/zram0`: **32 GiB** (`zstd`, prio `100`) | `vm.swappiness=100`, `vm.page-cluster=0`, `zswap=Y` (`zstd`, `max_pool_percent=20`). No disk swap. |
| **Discrete GPU (`03:00.0`)** | **ASRock AMD Radeon RX 7900 XTX** (`Navi 31` / `gfx1100`, rev `c8`) | `24,560 MiB` VRAM, `32 GiB` BAR0, `60,293 MiB` GTT. Upstream CPU root port `00:01.1` runs at **PCIe 3.0 ×16 (`8.0 GT/s`, ~12–15 GB/s)**; card-internal switch runs `16.0 GT/s`. |
| **Integrated GPU (`0a:00.0`)** | **AMD Radeon Graphics** (`Cezanne` / `gfx90c`, rev `d8`) | **8,192 MiB** UMA VRAM carveout (`~1.84 GiB` active). **Drives the GNOME/Wayland desktop**, isolating 7900 XTX VRAM for Strata. |
| **OS Storage (`rpool`)** | 2 × `Samsung SSD 980 PRO 1TB` (`nvme0n1`, `nvme1n1`, `enczfs` mirror) | **PCIe 3.0 ×4 (`8.0 GT/s` downgraded, ~3.2–3.5 GB/s raw)**, `856G` (`50%` full, `42%` frag, `lz4`). Hosts `/`, `/home/wuxxin`, `/var`, plus dedicated Tier-3 KV dataset **`rpool/data/user-cache`** (`/home/wuxxin/.cache/user-cache`, `compression=off`, `sync=disabled`, `recordsize=1M`, `primarycache=metadata`, `com.sun:auto-snapshot=false`). |
| **Data/Model Storage (`dpool`)** | 2 × `Samsung SSD 870 QVO 8TB` (`sda1`, `sdb1` SATA mirror) | `7.27T` (`47%` full, `lz4`, `recordsize=128K`, `atime=off`, `logbias=throughput`, `primarycache=all`, `secondarycache=all`). Hosts `/data/public/machine-learning` (~500 MB/s SATA). `logs` mirror on NVMe `p5`; **L2ARC `cache` (`58G + 58G = 116 GiB` on `nvme*p4` via `by-id`) repaired `ONLINE` (2026-11-12 13:32)**. |

---

## 2. Installed Strata & ROCm Software Stack

| Component | Version / Path | Notes |
|---|---|---|
| **Strata Engine** | `0.1.59.1` (`PKG_VERSION: 12284.r16.gccd360f-1`) | `/usr/lib/strata/engine/strata` (`local-hip`, `gfx1030`/`gfx1100`) |
| **Strata Vision** | `/usr/lib/strata/engine/strata-vision-hip` + CPU `strata-vision` | GPU vision (`--vision`, `1024` tokens) |
| **Strata Server & Tools** | `/usr/share/strata/serve/server.py`, `/usr/share/strata/strata_cli/` | Managed via `submodules/agents-shared/assistants/local-chat-strata.sh` |
| **ROCm / hipBLASLt** | `rocm-hip-runtime 7.2.4-1`, `hipblaslt 7.2.4-1` (`/opt/rocm`) | 48-row calibrated table: `~/.local/state/strata/local-chat-strata-hipblaslt.txt` (covers `T=4096, 8192, 16384` across all `bf16`/`f16` shapes) |

### Model Artifacts (`/data/public/machine-learning/models/strata/swift15_iq3s`)

| Artifact | Size | Role |
|---|---|---|
| `models/swift-IQ3_S/...00001-of-00002.gguf` | `42G` | Primary native model + expert arena + PLE index |
| `models/swift-IQ3_S/...00002-of-00002.gguf` | `37G` | Shard 2 (PLE n-gram embeddings / dense tensors) |
| `packs/swift-iq3_s` | `1.5G` | Native packed layout & tokenizer |
| `models/mmproj-Swift-Qwen3.8-Flash-Next-BF16.gguf` | `866M` | BF16 multimodal vision projector |
| `mtp/rt` (`experts.bin` + `dense.bin` + `draft_vocab.bin`) | `787M` | Bilingual/multilingual MTP speculative draft head (`1.6G` total `mtp/`) |
| `dspark` | `1.3G` | Tuned drafter directory (present on disk; baseline currently uses `mtp/rt`) |
| `projections/Qwen3.8-Flash-Next-experimental-speed-projection.gguf` | — | Control vector (`--control-vector-scaled ...:1.0`, layers `4..44`) |
| `/usr/share/strata/data/expert-profile.bin` | `192K` | Pre-ranked 24,576 expert routing profile |

---

## 3. Active Systemd User Services & Routing Architecture

```
Clients (omp / LifeOS Pulse / Zed / Hooks)
   │
   ▼  http://127.0.0.1:21080/v1
local-router.service (FastAPI / uvicorn)
   │
   ├──▶ chat ──▶ http://127.0.0.1:20080/v1  (local-chat-strata.service → RX 7900 XTX + Host RAM)
   ├──▶ stt  ──▶ local-speech-to-text.service (whisper-server)
   └──▶ (other local-router backends: embeddings, rerank, tts, imagegen)
```

### Key Unit & Configuration Files
- **Service Wrapper:** `submodules/agents-shared/assistants/local-chat-strata.sh`
- **Systemd Unit:** `~/.config/systemd/user/local-chat-strata.service` (`Restart=on-failure`, `RestartSec=10s`, `LimitMEMLOCK=infinity`, `MemoryMax=infinity`, `PrivateDevices=no`, `PrivateIPC=no`)
- **Environment & Generated Config:**
  - `~/.config/systemd/user/local-chat-strata.env`
  - `~/.config/systemd/user/local-chat-strata-config.json`
  - `~/.config/systemd/user/local-chat-strata-launcher.py`
- **Runtime State & Calibration (`~/.local/state/strata/`):**
  - `~/.local/state/strata/local-chat-strata-hipblaslt.txt` (48-row tuned hipBLASLt table for `gfx1100 100202`)
  - `~/.local/state/strata/local-chat-strata-profile.bin` (`--expert-profile-save`)
  - `~/.local/state/strata/procs/`, `~/.local/state/strata/runtime/`
- **Host Privilege / Memory Limits:**
  - `/etc/security/limits.d/99-strata-memlock.conf` (`wuxxin soft/hard memlock unlimited`)
  - `/etc/systemd/user.conf.d/memlock.conf` (`DefaultLimitMEMLOCK=infinity`)
  - `/etc/systemd/zram-generator.conf` (`min(ram / 2, 32768)` = `32 GiB` zstd)
  - `/etc/sysctl.d/99-zram-tuning.conf` (`vm.swappiness=100`, `vm.page-cluster=0`)

---

## 4. Current Strata Production Settings & Resource Footprint

### 4.1 Key Engine Parameters (`local-chat-strata.env`)
- **Context & KV Architecture:** `--max-context 240384`, `--kv k8v4`, **`--kv-grow`** (HIP Virtual Memory Management elastic growth via `hipMemAddressReserve`/`hipMemCreate`/`hipMemMap` starting at `16,384` cells / `0.21 GiB` VRAM, trading slots dynamically up to `240,384` cells / `2.46 GiB` and completely eliminating the `2.19 GiB` pinned host KV streaming ring).
- **Multi-Agent Conversation Cache & Memory Defense:** `--prompt-cache 6`, `--conversation-cache-slots 8`, `--conversation-cache-mib 16384`, `--conversation-cache-min-free-mib 6144`, `--conversation-cache-min-tokens 4096`, `--conversation-cache-park-gain 2048`. Guaranteed `6,144 MiB` `MemAvailable` floor prevents OOM storms and ZRAM page-allocation stalls. Short Pulse/hook queries ($< 4,096$ tokens) are rejected from slots to protect deep project histories.
- **Tier-3 NVMe `O_DIRECT` KV Offload:** `slot_save_path = ~/.cache/user-cache` on dedicated ZFS dataset `rpool/data/user-cache` (`sync=disabled`, `recordsize=1M`, `compression=off`). Inactive $43\text{k}$-token context saves in `855 ms` (`903 MB/s`) and restores in **`463 ms` (`1,667 MB/s` — $36\times$ faster than cold prefill)** with `99.96%` KV reuse on follow-up turns.
- **Speculative Decoding:** `"drafting": "mtp"`, `--spec 4`, `--spec-min-p 0.58`, `--suffix-draft 3`, `--lookup-chain 2`, `STRATA_SPEC_COST=1` (cost-aware window sizing), `STRATA_FUSE_HEAD_GR=1` (fused LM head + hyper-connection read), `STRATA_NORM_ROPE=1` (combined RMSNorm + RoPE).
- **Expert Offloading & Adaptation:** `--expert-cache auto` (`9,024` VRAM slots = `17.11 GiB` VRAM), `--vram-reserve-mib 576` (`~670 MiB` free VRAM at start, $\ge 530$ MiB after graph capture, zero VRAM starvation), `--pcie-frac 0.20`, `--adapt-async 1`, `--adapt-every 1`, `--adapt-swaps 160`, `--adapt-decay 0.97`, `STRATA_ARENA_RELEASE=0`, `STRATA_ROUTE_TAIL_SKIP=7`.
- **Prefill & Decode Kernel Acceleration (`gfx1100`):** `--ple-io ram`, `--prefill 24576` (single-pass $\le 24\text{k}$ prompts), `STRATA_PREFILL_RING=512` (prevents `HIP_WMMA` ring drop to 96), `STRATA_PREFILL_ROUTED_STREAM=1` (prunes unrouted experts before PCIe transfer), `STRATA_EMB_REUSE_ACCOUNT=1`, `STRATA_GDN_HEAD=1`, `STRATA_GDN_PP=2`, `STRATA_GDN_CONVL2=2`, `STRATA_GDN_NOY=1`, `STRATA_HIP_WMMA=1`, `STRATA_PA_FAST=1`, `STRATA_SELECT_WMMA=1`, `STRATA_PF_F16=1`, `STRATA_PF_DM16=1`, `STRATA_Q8_PACKED=1`, `STRATA_MMVF_ROWS=1`, `STRATA_ATTN_LANECELL=1`, `STRATA_ATTN_MERGE_V2=1`, `STRATA_EXPERT_V2=1`, `STRATA_TSUM=1`, `STRATA_LFUSE=1`, `STRATA_GDN_SPLIT=1`, `STRATA_QFUSE=1`, `STRATA_PLE_BATCH=1`, `STRATA_SMALL_UNR=3`, `STRATA_GR_Q32_G=2`, `STRATA_GR_Q8_PFS=1`, `STRATA_HEAD_MIX_MULTI=1`, `STRATA_FUSE_HITS=1`, `STRATA_FUSE_WAIT=1`, `STRATA_VERIFY_QDEDUP=1`, `HSA_USERPTR_FOR_PAGED_MEM=1`, 48-row calibrated `local-chat-strata-hipblaslt.txt`.
- **CPU Thread Pinning:** `7` expert-pool workers on logical CPUs `1–7`, host thread on CPU `0` (`--host-core first`), `nice +5` (`STRATA_ENGINE_NICE`).

### 4.2 End-to-End Memory Budget on `power` (`117.76 GiB` `MemTotal`)

| Memory Tier / Consumer | Typical / Max Footprint | Backing & Pinning Behavior | Operational Mechanics & Reclaim |
|---|---|---|---|
| **Strata PLE Table (Shard 2)** | **`26.82 GiB`** (`28,125 MiB` RSS) | `mlock()`ed unevictable host RAM | Locked at start via `/etc/security/limits.d/99-strata-memlock.conf`. Zero page faults, zero NVMe reads during token ingestion. |
| **Strata Expert Arena** | **`46.84 GiB`** (`24,576` experts) | `cudaHostRegister(PORTABLE)` pinned | Permanent DDR4-2666 host memory residency (`STRATA_ARENA_RELEASE=0`). Avoids `MADV_DONTNEED` NVMe churn on dynamic VRAM expert evictions. |
| **Strata Pinned Host KV Ring** | **`0 GiB`** *(was `2.19 GiB`)* | Reclaimed host RAM | **Reclaimed completely via `--kv-grow`**. Replaced by elastic in-VRAM HIP VMM mapping (`0.21–2.46 GiB` VRAM). |
| **Strata Vision Sidecar + Base Runtime** | `~1.0–1.5 GiB` | Anon host memory | Multimodal vision projector runtime and token buffers (`strata-vision-hip`). |
| **Total Strata Pinned / Locked Floor** | **`73.66 GiB`** *(was `75.85 GiB`)* | Unswappable OS floor | Baseline resident memory occupied before conversation parking or active token generation. |
| **Strata Conversation Cache (Active Tier)** | **`0.5 – 16.0 GiB`** (`16 GiB` cap) | Anon host DDR4 RAM | Expanded to 8 slots; capped at `16,384 MiB` with `--conversation-cache-min-free-mib 6144`. Only requests $\ge 4,096$ tokens park (`min-tokens`). Advance $\ge 2,048$ tokens required to re-snapshot (`park-gain`). |
| **Tier-3 NVMe Offloaded Contexts (`user-cache`)** | `0 GiB` Host RAM (`~0.77 GiB` / 43k ctx on disk) | Direct I/O (`O_DIRECT`) on NVMe | Inactive large contexts swapped to `/home/wuxxin/.cache/user-cache` (`rpool/data/user-cache`). Bypasses Linux page cache; restored at **`1,667 MB/s`** ($463\text{ ms}$). |
| **OpenZFS ARC (`/etc/modprobe.d/zfs.conf`)** | **`2.0 GiB` min – `12.0 GiB` max** | Linux kernel slab (`ABD`) | Hard-capped at `12 GiB` (baked into initramfs `2026-11-12`). Evicts smoothly under memory pressure down to `2.0 GiB` floor without triggering OOM killer. |
| **AMDGPU GTT (`gpu_reclaim` / `gpu_active`)** | `~0.5 – 4.0 GiB` | Kernel GPU driver pages | Reclaimable driver-allocated staging buffers and command queues. |
| **Desktop & Applications (`gnome`, `zed`, `omp`, `bun`, `librewolf`)** | `~6.0 – 9.0 GiB` | Anon / ZRAM swappable | Swappable to 32 GiB `/dev/zram0` (`zstd`). |
| **Guaranteed `MemAvailable` Safety Headroom** | **`16.0 – 19.0 GiB`** (`0 B` swap used) | Free / reclaimable OS pool | Verified under concurrent 4-stream load (`Oracle C`) and 43k token ingestion. Completely eliminates `GFP_KERNEL` allocation stalls and OOM-kill cascades. |

### 4.3 Operational Rules & Guardrails

1. **S3 Deep Suspend Guard:** S3 deep suspend (`PM: suspend entry (deep)`) deadlocks/hangs whenever `local-chat-strata.service` is active due to TTM VRAM buffer eviction colliding with the `73.66 GiB` pinned KFD/HMM memory and ZRAM. **Always stop `local-chat-strata.service` before sleep.**
2. **Single-Stream Benchmark Protocol:** Current `omp bench` defaults `--par` to `4`. For single-user benchmarks (Oracles A & B), always pass `--par 1` explicitly alongside `OMP_BRIDGE_SETTINGS=/dev/null` to prevent synthetic multi-stream concurrency.
3. **State vs. Config Path Separation:** Keep configuration files in `~/.config/systemd/user/` and runtime tables/profiles in `~/.local/state/strata/`. All environment paths use `${HOME}` rather than `%h` for POSIX and shell consistency.
4. **Model Path Safety:** Use scratch symlink trees (`scratch/models/strata/`) when downloading or testing experimental drafters/weights to prevent unauthorized write attempts to read-only `/data/public/`.
