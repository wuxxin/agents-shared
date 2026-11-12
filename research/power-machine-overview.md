# Host `power` — Strata & Local Inference Architecture Overview

**Host:** `power` (`Gigabyte B550 AORUS ELITE AX V2`, BIOS `F19d`, Manjaro Linux `7.2.14-1-MANJARO`)  
**Updated:** 2026-11-12  
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
| **ROCm / hipBLASLt** | `rocm-hip-runtime 7.2.4-1`, `hipblaslt 7.2.4-1` (`/opt/rocm`) | Explicit tuning table: `/usr/share/strata/tools/hip/gfx1100-hipblaslt-100202.txt` |

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
- **Host Privilege / Memory Limits:**
  - `/etc/security/limits.d/99-strata-memlock.conf` (`wuxxin soft/hard memlock unlimited`)
  - `/etc/systemd/user.conf.d/memlock.conf` (`DefaultLimitMEMLOCK=infinity`)
  - `/etc/systemd/zram-generator.conf` (`min(ram / 2, 32768)` = `32 GiB` zstd)
  - `/etc/sysctl.d/99-zram-tuning.conf` (`vm.swappiness=100`, `vm.page-cluster=0`)

---

## 4. Current Strata Production Settings & Resource Footprint

### 4.1 Key Engine Parameters (`local-chat-strata.env`)
- **Context & KV:** `--max-context 240384`, `--kv k8v4`, `--kv-resident 32768` (`2.19 GiB` pinned host RAM)
- **Conversation & Prompt Cache:** `--prompt-cache 6`, `--conversation-cache-slots 6`, `--conversation-cache-mib 24576`, `--conversation-cache-min-free-mib 2048`
- **Speculative Decoding:** `--spec 4`, `--spec-min-p 0.60`, `--suffix-draft 3`
- **Expert Offloading & Adaptation:** `--expert-cache auto` (`9,004` VRAM slots = `17.08 GiB` VRAM), `--vram-reserve-mib 512` (`~632 MiB` free VRAM), `--pcie-frac 0.20`, `--adapt-async 1`, `--adapt-every 1`, `--adapt-swaps 160`, `--adapt-decay 0.97`, `STRATA_ARENA_RELEASE=0`, `STRATA_ROUTE_TAIL_SKIP=7`
- **PLE & Prefill:** `--ple-io ram`, `STRATA_PLE_COMPACT=1`, `STRATA_PLE_COPY_STREAM=1`, `STRATA_PF_PAD=1`, `STRATA_HC_UPMIX=1`, `STRATA_PF_HCDOWN=1`, `STRATA_CVEC_FUSE=1`, `STRATA_PF_HC_REGION=1`, `STRATA_PREFILL_AUTO_MAX=16384`, `HSA_USERPTR_FOR_PAGED_MEM=0`
- **CPU Thread Pinning:** `7` expert-pool workers on logical CPUs `1–7`, host thread on CPU `0` (`--host-core first`), `nice +5` (`STRATA_ENGINE_NICE`).

### 4.2 End-to-End Memory Budget on `power` (`117.76 GiB` `MemTotal`)

| Consumer | Typical Size | Pinning / Reclaimability |
|---|---|---|
| **Strata PLE Table (`--ple-io ram`)** | `26.82 GiB` | `mlock()`ed (`unevictable`) |
| **Strata Expert Arena (`STRATA_ARENA_RELEASE=0`)** | `46.84 GiB` | `cudaHostRegister(PORTABLE)` (unswappable) |
| **Strata KV Streaming Ring (`--kv-resident 32768`)** | `2.19 GiB` | GPU-pinned (unswappable) |
| **Strata Vision + Base Runtime** | `~1.0–1.5 GiB` | Anon |
| **Strata Conversation Cache (`--conversation-cache-mib`)** | `1–24 GiB` (`24 GiB` max) | Anon (swappable to ZRAM, high latency if swapped) |
| **ZFS ARC (`/etc/modprobe.d/zfs.conf`)** | `2 GiB` min – **`12 GiB` max**; L2ARC write rate: **`512 MiB/s`** *(baked into initramfs `2026-11-12`)* | Capped at `12 GiB` max / `2 GiB` min with `l2arc_write_max=512M` and `l2arc_write_boost=512M`. Active live and in `/boot/initramfs-*.img`. |
| **AMDGPU GTT (`gpu_reclaim` / `gpu_active`)** | `~0.5–6.4 GiB` | Reclaimable/active GPU driver allocations |
| **Desktop + Agents (`gnome`, `librewolf`, `zed`, `omp`, `bun`, `java`)** | `~6–10 GiB` | Anon / ZRAM-swappable |

> **Operational Constraint:** Strata's **75.85 GiB unswappable floor** + `24 GiB` conversation cache + ZFS (`~6–7 GiB` floor) + desktop (`~6–10 GiB`) + `gpu_reclaim` (`~4–6 GiB`) totals **`116–124 GiB`**, which leaves near-zero headroom even at `117.76 GiB` `MemTotal`. Furthermore, **S3 deep suspend (`PM: suspend entry (deep)`) hangs whenever `local-chat-strata.service` is running** — stop `local-chat-strata.service` before sleep and see [`strata-machine-crashes.md`](./strata-machine-crashes.md) for crash forensics and pending tuning fixes.
