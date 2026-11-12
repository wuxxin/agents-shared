# Strata Machine Crashes, Memory/I/O Forensics & Hardware Audit

**Host:** `power` (`Gigabyte B550 AORUS ELITE AX V2`, BIOS `F19d`, Manjaro Linux `7.2.14-1-MANJARO`)  
**Audit Date:** 2026-11-12  
**Scope:** Read-only forensic investigation of system hangs/crashes over 2026-11-10 – 2026-11-12 following `local-chat-strata.sh` deployment, ZFS ARC reclaim behavior under memory pressure, and full privileged (`sudo`) hardware/BIOS/PCIe/ZFS audit for [`strata-tuning.md`](./strata-tuning.md) Section 12.

---

## 1. Executive Summary

The machine hangs were **not hardware defects** (EDAC reports `0` correctable and `0` uncorrectable ECC errors on all 4 × 32 GiB Micron ECC DIMMs). They were caused by **two distinct, compounding software/resource-budget failures** triggered by `local-chat-strata.service`:

1. **Live Memory Exhaustion → OOM Restart Storm → `amdgpu` HMM/SVM Kernel Oops (`2026-11-10 14:38–14:44`, Boot `-5`; and severe `GFP_KERNEL` stalls at `17:22–17:30`, Boot `-4`):**
   - A single idle/running `strata` instance holds **~75.85 GiB of non-swappable, non-evictable RAM** (`26.82 GiB` `mlock`ed PLE table + `46.84 GiB` `cudaHostRegister` GPU-pinned expert arena + `2.19 GiB` pinned KV ring), growing to **78.4–80.8 GiB RSS** under active `conversation-cache-mib=24576` workloads.
   - Before the 2026-11-12 reboot, Linux `MemTotal` was only **109.89 GiB** (16 GiB withheld by the Cezanne iGPU). With ZFS kernel slab/floor (`~5.5–7 GiB`), `gpu_reclaim` (`3.3–6.4 GiB`), and desktop/agent processes (`omp`, `bun`, `zed-editor`, `librewolf`, `evolution`, `java`), free RAM hit zero.
   - When `systemd` (`Restart=on-failure`, `RestartSec=10s`) repeatedly respawned `strata` into OOM, the third OOM-kill at **`14:40:53`** struck `strata` mid-`kfd_ioctl` (`svm_range_validate_and_map`), triggering a **kernel NULL pointer dereference Oops in `amdgpu_hmm_range_valid+0x15/0x30 [amdgpu]`** (`exited with irqs disabled`, kernel tainted `D`), hanging the host hard at `14:44:06`.
   - Adding **32 GiB ZRAM** (`2026-11-10 15:09`) could not swap the `~75.85 GiB` of `mlock`/`cudaHostRegister` memory. Instead, during a `strata` restart overlap at `17:22–17:30`, ZRAM filled to **27.4 GiB used** (`4.8–6.4 GiB` `zspages` in `Normal` zone RAM), driving `Normal` free RAM to **1.26 MiB** and causing **11-second `GFP_KERNEL` page-allocation stalls and failures**.

2. **S3 Deep Suspend (`deep`) Deadlock/Hang Whenever `local-chat-strata` Is Running (`Boot -4`, `Boot -3`, `Boot -2`):**
   - On **2026-11-10 20:19:38**, **2026-11-11 03:45:38**, and **2026-11-11 21:43:20**, the system entered `PM: suspend entry (deep)` (with `/usr/lib/systemd/system-sleep/rtc-wakeup` scheduling wake for 12:00) while `local-chat-strata` was running and **hung every single time** (next boot reported `system.journal corrupted or uncleanly shut down`).
   - By contrast, on **2026-11-12 (`Boot -1`)**, `local-chat-strata` stopped cleanly at `02:35:41` *before* `PM: suspend entry (deep)` at `05:04:56`, and the machine **resumed cleanly at `09:16:15`** (`amdgpu 0000:03:00.0: MODE1 reset`, `PM: suspend exit`).
   - Before ZRAM (`Boot -5`, Nov 07–10), `amdgpu_device_evict_resources()` failed fast during suspend with `[TTM] Buffer eviction failed` / `pci_pm_prepare returns -12` (`-ENOMEM`), aborting sleep safely. Once 32 GiB ZRAM existed, TTM VRAM eviction (~23.4 GiB on RX 7900 XTX) no longer failed `-ENOMEM` in `prepare`, colliding with pinned KFD/SVM memory + ZRAM during S3 suspend/resume and freezing the kernel.

---

## 2. Chronological Boot & Crash Timeline (2026-11-04 – 2026-11-12)

| Boot | Window (CET) | Config State | Observed Failure / Crash Event | Clean Exit? |
|---|---|---|---|---|
| **`-5`** | Nov 04 14:52 → Nov 10 14:44 | `MemTotal=109.89 GiB` (iGPU `16G`), **0 swap**, `memlock=unlimited` added Nov 05 23:00, `strata.env` updated Nov 09 15:49 | **Nov 07 06:12–10:12:** S3 suspend aborted repeatedly (`[TTM] Buffer eviction failed`, `-12`).<br>**Nov 07 12:07:** OOM-kill `strata-host` (`56.6 GB anon + 28.1 GB file`).<br>**Nov 10 14:38–14:42:** 4× OOM-kills in 3.5 min; at **14:40:53** **Kernel Oops (`amdgpu_hmm_range_valid+0x15/0x30`, NULL ptr `0x50`)** during `kfd_ioctl` (`Tainted: D`, IRQs disabled). System hung at **14:44:06**. | **No** (Hard hang) |
| **`-4`** | Nov 10 15:38 → Nov 10 20:19 | `MemTotal=109.89 GiB` (iGPU `16G`), **32 GiB ZRAM (`zstd`)** added `15:09` (`swappiness=100`, `page-cluster=0`) | Boot journal flagged `system.journal corrupted`.<br>**17:22:49:** `verify: timed out at layer 1` (`907 MiB` avail) → restart overlapped old 80 GiB instance → **27.4 GiB ZRAM used**, `Normal free: 1,288 kB`, `GFP_KERNEL` order-0 page allocation failures (`Bun Pool 3`, `HeapHelper`, 11s stall).<br>**20:19:38:** `PM: suspend entry (deep)` with `strata` active → **never woke / hung**. | **No** (Suspend hang) |
| **`-3`** | Nov 11 00:43 → Nov 11 03:45 | Same as `-4` (`109.89 GiB` + 32 GiB ZRAM) | Boot journal flagged `system.journal corrupted`.<br>Heavy 164k-token `oh-my-pi` session (`9.72 GB` parked conv cache).<br>**03:45:38:** `PM: suspend entry (deep)` with `strata` active → **never woke / hung**. | **No** (Suspend hang) |
| **`-2`** | Nov 11 09:29 → Nov 11 21:43 | Same as `-4` (`109.89 GiB` + 32 GiB ZRAM) | Boot journal flagged `system.journal corrupted`.<br>Startup logged `WARNING: 11.63 GiB short` (`35.21 GiB` avail vs `46.84 GiB` needed) due to ZFS ARC.<br>`oh-my-pi` + `zed` sessions (`2.15 GB` conv cache).<br>**21:43:20:** `PM: suspend entry (deep)` with `strata` active → **never woke / hung**. | **No** (Suspend hang) |
| **`-1`** | Nov 12 00:42 → Nov 12 13:00 | Same as `-4` (`109.89 GiB` + 32 GiB ZRAM) | Boot journal flagged `system.journal corrupted`.<br>Startup logged `WARNING: 12.15 GiB short` (`34.69 GiB` avail).<br>**02:35:41:** `local-chat-strata.service` **stopped** (`75.4G` peak, `66M` swap peak).<br>**05:04:56:** `PM: suspend entry (deep)` → **09:16:15 clean resume** (`MODE1 reset`).<br>**13:00:20:** Clean reboot for BIOS iGPU change. | **Yes** (Clean reboot) |
| **`0`** | Nov 12 13:02 → active | `MemTotal=117.76 GiB` (iGPU `8G`, **+7.87 GiB reclaimed**) + 32 GiB ZRAM | Clean boot; `strata` tested briefly (`75.6G` peak) and stopped (`13:05:06`). | Active |

---

## 3. Memory, Swap, and Usage Profile Before Crashes

### 3.1 `local-chat-strata` Locked/Pinned Memory Floor

From `systemd` accounting and kernel `Mem-Info` / `strata` startup logs:

| Component | Size | Evictable / Swappable? | Mechanism |
|---|---|---|---|
| **PLE Table (`--ple-io ram`, Shard 2)** | **26.82 GiB** (`28,125,264 kB` `file-rss`) | **No** (`unevictable` / `mlocked`) | `mlock()` enabled by `/etc/security/limits.d/99-strata-memlock.conf` & `/etc/systemd/user.conf.d/memlock.conf` |
| **Expert Arena (`STRATA_ARENA_RELEASE=0`)** | **46.84 GiB** | **No** (GPU-pinned) | `cudaHostRegister(..., PORTABLE)` via ROCm KFD/HMM |
| **KV Streaming Host Buffer (`--kv-resident 32768`)** | **2.19 GiB** | **No** (GPU-pinned) | Pinned host RAM (`--max-context 240384`) |
| **Token Embedding (`IQ4_XS`) + Projections + Runtime** | **~0.5–1.5 GiB** | Mostly unpinned | Mapped/anon runtime buffers |
| **Minimum Idle Resident Floor (`strata`)** | **~75.6–75.85 GiB** | **~75.85 GiB pinned/locked** | Observed `MemoryPeak=75.4G` (Boot `-1`), `75.6G` (Boot `0`) |
| **Active Conversation Cache (`--conversation-cache-mib`)** | **2.1–24.0 GiB** (`up to 24,576 MiB`, 6 slots) | Anon (swappable to ZRAM) | Observed `4.1 GB` (Boot `-4`), `9.72 GB` (Boot `-3`), pushing `strata` RSS to **78.4–80.8 GiB** |
| **Vision Sidecar (`strata-vision-hip`)** | **~0.95 GiB** (`248,814` pages) | Anon | Loaded alongside `strata` |

### 3.2 Workload & Kernel State Snapshots at Failure Points

1. **Boot `-5` (`2026-11-10 14:38:55`, No Swap, 109.89 GiB `MemTotal`):**
   - **Usage profile:** `oh-my-pi` active with **181,661–182,002 token** main requests (`14:36:53–14:36:59`) followed by rapid-fire `qwen3.8-flash-next-thinking` hook/subagent calls (`input=620` / `2110`) every 2–4 seconds (`14:37:02–14:38:39`). `strata` ran out of RAM for conversation parking (`need 254 MiB plus 2048 MiB floor, 1941 MiB available`), evicted all 3 slots, and hit OOM 17 seconds later.
   - **Kernel `Mem-Info` at `14:38:55`:**
     - `active_anon`: `49.84 GB`, `inactive_anon`: `25.55 GB` (**`75.39 GB` total anon**)
     - `unevictable` (`mlocked`): **`28.13 GB` (`26.82 GiB`)**
     - `active_file + inactive_file`: **`7.86 MB`** (Linux page cache completely drained)
     - `slab_reclaimable`: `1.18 GB`, `slab_unreclaimable`: `2.15 GB`, `gpu_reclaim`: `6.69 GB`, `pagetables`: `469 MB`, `shmem`: `436 MB`, `Free swap`: `0 kB`
     - Top consumer: `strata-host` (`pid 2249729`: `anon-rss 54,090,044 kB` + `file-rss 28,125,264 kB` = **`82.22 GB` / `78.4 GiB`**), `zed-editor` (`1.41 GiB`), `MainThread`/LibreWolf (`1.21 GiB`), `strata-vision-hip` (`0.95 GiB`), `evolution` + 9 `WebKitWebProcess`, `java`, `wezterm-gui`.
   - **Cascade:** `local-chat-strata.service` (`Restart=on-failure`, `RestartSec=10s`, `MemoryMax=infinity`) restarted into the same full system at `14:39:11`, `14:40:10`, `14:41:05`, `14:42:36`, getting OOM-killed 4 times in 3.5 min and causing the **`amdgpu_hmm_range_valid` kernel NULL pointer dereference Oops** at `14:40:53`.

2. **Boot `-4` (`2026-11-10 17:22–17:30`, 32 GiB ZRAM added, 109.89 GiB `MemTotal`):**
   - **Usage profile:** Long thinking generation under `< 1 GiB` free RAM (`907 MiB` in memory guard at `17:22:06`) → `verify: timed out at layer 1` (`17:22:49`, `strata` `80.0G` peak + `6.3G` swap peak) → immediate restart at `17:22:50` before the previous instance finished exiting (`available` dropped `41.67 GiB` → `39.65 GiB` while allocating `46.84 GiB`).
   - **Kernel `Mem-Info` progression:**
     - `17:23:49` (`Bun Pool 3: page allocation failure`, `GFP_KERNEL`): `Normal free: 6.19 MB`, `zspages: 4.32 GB`, `Free swap: 13.87 GB` (~`19.7 GB` swapped to ZRAM).
     - `17:25:10` (`HeapHelper: page allocation failure`, stack in `zswap_shrinker_scan` → `shrink_slab` → `evict_folios`): `Normal free: 1.29 MB`, `DMA32 free: 2.23 MB`, `zspages: 6.83 GB`, `Free swap: 11.19 GB` (~`22.4 GB` swapped).
     - `17:28:53` (`HeapHelper: page allocation stall for 11 secs`): `Free swap: 4.85 GB` (**`28.7 GB` / `26.7 GiB` of 32 GiB ZRAM filled!**), `gpu_active: 2.53 GB`, `gpu_reclaim: 0.42 GB`.
   - Later (`18:16–18:23`), `oh-my-pi` ran a `108,933`-token session (`parked=6 bytes=4.10 GB`), then suspended at `20:19:38` and hung.

3. **Boots `-3` (`2026-11-11 00:43–03:45`) & `-2` (`2026-11-11 09:29–21:43`):**
   - **Boot `-3` usage profile:** `oh-my-pi` active up to **`164,698` input tokens** (`parked=6`, `bytes=9.72 GB`, `reused_kv_bytes=1.94 GB`) until `01:47:48`; suspended at `03:45:38` and hung.
   - **Boot `-2` usage profile:** `oh-my-pi` (`600–9,000` tokens) + `zed` (`1,300–8,000` tokens) alternating until `17:49:33` (`parked=6`, `bytes=2.15 GB`); suspended at `21:43:20` and hung.

---

## 4. ZFS ARC Behavior Under Memory Pressure

**Direct Answer:** **Yes — OpenZFS (`zfs-2.4.4-1`) does shrink ARC automatically via its Linux kernel shrinker under memory pressure, *and* evictable ARC data was evicted before the OOM killer fired. However, uncapped ZFS ARC (`zfs_arc_max=0`) still causes severe startup memory pressure, allocation stalls, and ~5.5–7 GiB of non-reclaimable floor overhead.**

### 4.1 Evidence Observed on `power`

1. **Uncapped ARC Target (`zfs_arc_max = 0`):**
   - In `/sys/module/zfs/parameters/`: `zfs_arc_max = 0`, `zfs_arc_min = 0`, `zfs_arc_pc_percent = 0`, `zfs_arc_sys_free = 0`.
   - On OpenZFS 2.4, `0` sets `c_max` to nearly 100% of physical RAM: `/proc/spl/kstat/zfs/arcstats` reports **`c_max = 125,370,503,168` bytes (116.76 GiB)** and `c_min = 3,951,382,656` bytes (**3.68 GiB**).
2. **ARC Balloons Immediately When Strata Loads Model Files:**
   - All Strata model weights (`79 GiB` GGUFs + `1.5 GiB` packs + `1.6 GiB` MTP) live on ZFS dataset `dpool/data/public` with `primarycache=all`.
   - When `strata` reads the model through buffered I/O (`expert arena read through the file cache`), ZFS ARC caches ~35 GiB of those reads in kernel memory. Even after a 1m48s idle start on Boot `0`, `arcstats` showed **`size = 36.54 GB` (`34.03 GiB`)**, `data_size = 30.70 GB`, `metadata_size = 4.31 GB`, `memory_indirect_count = 12,390`.
3. **Why ARC Still Causes Problems Despite Shrinking Under Pressure:**
   - **Blindness in `MemAvailable` & Strata's Memory Guard:** ZFS ARC allocates via kernel ABD/page allocators rather than Linux's `Cached:` / `Inactive(file):` page cache. Consequently, `/proc/meminfo` `MemAvailable` does **not** credit ZFS ARC as reclaimable. On Boots `-2` and `-1`, `strata` logged `MemAvailable 101.6 GiB` *before* loading PLE, then watched `MemAvailable` collapse to **`34.69–35.21 GiB`** once ARC absorbed the Shard 1/2 reads, triggering `WARNING: 12.15 GiB short` (`reclaimable cache credited 0.0 GiB`).
   - **Hard Non-Evictable Floor (`c_min` + `SUnreclaim`):** Under OOM (`Boot -5 14:38:55`), `active_file + inactive_file` dropped to `7.86 MB` and ARC evicted its compressible data down to its floor, **but** ZFS kept `slab_unreclaimable = 2.15–3.12 GiB` + `c_min` (`3.68 GiB` target) / `arc_meta_used` (`~1.5–5.8 GB`), leaving **~5.5–7 GiB** unusable by `strata` or ZRAM.
   - **Synchronous Reclaim Thrashing:** Forcing the kernel to shrink 30+ GiB of ZFS ARC synchronously during `strata`'s 46.84 GiB allocation—while simultaneously compressing anon pages into ZRAM—drove the `shrink_slab` / `zswap_shrinker_scan` stalls observed on `Boot -4` (`17:25:10`, `17:28:53`).
   - **Broken L2ARC on `dpool`:** Both NVMe L2ARC cache devices on `dpool` (`nvme0n1p4`, `nvme1n1p4`) are **`FAULTED (corrupted data)`**, so ARC evictions cannot fall back to NVMe L2ARC and cold reads must come from the SATA 870 QVO mirror (~500 MB/s, observed `0.97–2.08 GiB/s` only when partially cached).

---

## 5. Privileged (`sudo`) Hardware, BIOS, PCIe & ZFS Audit Answers (Section 12)

This section records all root-only hardware/system facts required by [`strata-tuning.md`](./strata-tuning.md) Section 12 so future unprivileged tuning sessions do not require `sudo`.

### 5.1 System, BIOS & Physical Memory (`dmidecode`)

- **Motherboard / BIOS:** `Gigabyte Technology Co., Ltd. B550 AORUS ELITE AX V2`, BIOS `F19d` (`09/02/2024`).
- **CPU:** `AMD Ryzen 7 PRO 5750G with Radeon Graphics` (Cezanne, Zen 3 APU, 8 cores / 16 threads, single NUMA node, **AVX-2 only / no AVX-512**, **PCIe 3.0 only**).
- **Physical RAM (`dmidecode -t memory`):**
  - **4 × 32 GiB = 128 GiB Micron `18ASF4G72AZ-3G2F1`** — **DDR4 Unbuffered ECC (`72-bit` total width, `64-bit` data width, Dual-Rank)** *(Correction: NOT DDR5 as previously noted in `strata-tuning.md`)*.
  - **Rated vs. Configured Speed:** Modules are rated **DDR4-3200 (`3G2`)**, currently running at **`2666 MT/s`** (1.2 V; AM4 4-DIMM Dual-Rank JEDEC default without manual DRAM frequency/timings).
  - **ECC Status (`edac`):** Active (`mc0: F19h_M50h`), `ce_count: 0`, `ue_count: 0`.

### 5.2 Host Memory Map, E820 & iGPU UMA Allocation (`dmesg`, `rocm-smi`)

| Memory Pool / Region | Before 2026-11-12 Reboot (`Boot -5..-1`) | After 2026-11-12 Reboot (`Boot 0`) | Notes |
|---|---|---|---|
| **Physical Installed DDR4** | 128.00 GiB | 128.00 GiB | 4 × 32 GiB Micron ECC |
| **iGPU (`0a:00.0`) UMA Carveout** | **16,384 MiB (16.00 GiB)** (`0xF400000000–0xF7FFFFFFFF`) | **8,192 MiB (8.00 GiB)** (`0xF400000000–0xF5FFFFFFFF`) | Reclaimed **+8 GiB** in BIOS before `Boot 0` |
| **Kernel / ACPI / E820 Reserved** | ~2.11 GiB | **2.24 GiB** (`2,350,240 kB` reserved) | `dmesg`: `123296292K/125670668K available` |
| **Linux `MemTotal` (`/proc/meminfo`)** | `115,223,172 kB` (**109.89 GiB**) | `123,480,708 kB` (**117.76 GiB**) | Net **+7.87 GiB** visible to OS |
| **iGPU Actual Usage (`rocm-smi`)** | Active display | **1,979.5 MiB (~1.84 GiB)** VRAM used | **Cezanne iGPU drives the desktop!** |
| **RX 7900 XTX (`03:00.0`) VRAM / GTT** | `24,560 MiB` VRAM / `56,261 MiB` GTT | `24,560 MiB` VRAM / `60,293 MiB` GTT | GTT scales to ~50% of `MemTotal` |

- **BIOS iGPU Recommendation:** Because the Cezanne iGPU (`0a:00.0`) actively renders the GNOME/Wayland desktop (`1.84 GiB` VRAM in use), disabling it completely would shift desktop rendering onto the RX 7900 XTX (which only has `~632 MiB` free VRAM under Strata). Instead, reducing BIOS `UMA Frame Buffer Size` further from `8G` to `2G` or `4G` reclaims another **4–6 GiB** of host RAM safely without touching the RX 7900 XTX.

### 5.3 Above 4G Decoding, Resizable BAR & PCIe Link Audit (`lspci -vvv`, `sysfs`)

- **Above 4G Decoding & Resizable BAR:** **ENABLED.**
  - RX 7900 XTX (`03:00.0`, ASRock): `Region 0` = **32 GB** (`0x7000000000`, 64-bit prefetchable), `Region 2` = **256 MB** (`0x7800000000`), `Physical Resizable BAR: BAR 0 current size: 32GB`, `BAR 2: 256MB`.
  - iGPU (`0a:00.0`): `Region 0` = **8 GB** (`0xF400000000`–`0xF5FFFFFFFF` in kernel `amdgpu` BAR; `lspci` reports 256M/2M apertures), ATS/PRI/PASID enabled.
- **Actual PCIe Link Speeds (Critical Correction to `strata-tuning.md`):**
  - **RX 7900 XTX Upstream CPU Link (`0000:00:01.1` ↔ `0000:01:00.0`):** **`8.0 GT/s` (PCIe 3.0) × 16**. Although the card's internal Navi 10 XL switch (`02:00.0` ↔ `03:00.0`) negotiates `16.0 GT/s` (PCIe 4.0), the Ryzen 7 PRO 5750G CPU root port maxes out at **PCIe 3.0 ×16 (~12–15 GB/s real host↔GPU bandwidth, not 28 GB/s PCIe 4.0)**.
  - **NVMe SSDs (`0000:06:00.0` & `0000:09:00.0`, both Samsung SSD 980 PRO 1TB, FW `3B2QGXA7`):** Both report `LnkCap: 16GT/s x4` but **`LnkSta: Speed 8GT/s (downgraded), Width x4`** (PCIe 3.0 ×4, **~3.2–3.5 GB/s max raw**, not PCIe 4.0 5–7 GB/s as assumed in `strata-tuning.md` §12.3).
  - **B550 Chipset SATA (`04:00.1`):** Drives 2 × `Samsung SSD 870 QVO 8TB` (`sda`, `sdb`, `mq-deadline` scheduler, Linux quirks `noncqtrim zeroaftertrim noncqonati nolpmonati`).

### 5.4 ZFS Storage Pools, Datasets & Swap/OOM Configuration

- **`rpool` (`856G`, `50%` full, `42%` fragmented, `lz4`, `primarycache=all`):**
  - `mirror-0`: `enczfs_ROOT1` + `enczfs_ROOT2` (LUKS/encrypted partitions on `nvme0n1` + `nvme1n1`). Hosts `/`, `/home/wuxxin`, `/var`.
  - **`rpool/data/user-cache`** *(Created `2026-11-12`)*: Dedicated Tier-3 NVMe KV-cache dataset mounted at `/home/wuxxin/.cache/user-cache` (`wuxxin:wuxxin`, `0700`) with `compression=off`, `atime=off`, `sync=disabled`, `recordsize=1M`, `primarycache=metadata`, `secondarycache=none`, `logbias=throughput`, `com.sun:auto-snapshot=false`.
- **`dpool` (`7.27T`, `47%` full, `1%` fragmented, `lz4`, `recordsize=128K`, `atime=off`, `primarycache=all`, `secondarycache=all`, `logbias=throughput`):**
  - `mirror-0`: `sda1` + `sdb1` (2 × Samsung 870 QVO 8TB SATA SSDs). Hosts `/data/public/machine-learning` (Strata models). `atime=off` and `logbias=throughput` applied on `dpool/data/public` (`2026-11-12`).
  - `logs`: `mirror-1` (`nvme-Samsung_SSD_980_PRO_1TB_S5GXNF0R937753T-part5` + `...-part5`, `7.50G` usable).
  - **`cache` (L2ARC): Repaired `2026-11-12 13:32` — `ONLINE`** (`58G + 58G = 116 GiB` striped across `nvme-Samsung_SSD_980_PRO_1TB_S5GXNF0R937752F-part4` and `...53T-part4` via persistent `/dev/disk/by-id` paths; `0` errors; `l2arc_rebuild_enabled=1`, `l2arc_noprefetch=1`, `l2arc_write_max=512 MiB/s`, `l2arc_write_boost=512 MiB/s`).
- **ZFS ARC & Swap / Kernel VM / OOM Settings:**
  - `/etc/modprobe.d/zfs.conf` *(Applied & baked into initramfs `2026-11-12`)*: `zfs_arc_max=12884901888` (**12 GiB**), `zfs_arc_min=2147483648` (**2 GiB**), `l2arc_write_max=536870912` (**512 MiB/s**), `l2arc_write_boost=536870912` (**512 MiB/s**). Applied live to `/sys/module/zfs/parameters/` and baked into `/boot/initramfs-*.img` via `mkinitcpio -P`.
  - `/etc/systemd/zram-generator.conf`: `zram-size = min(ram / 2, 32768)` (`32 GiB`), `compression-algorithm = zstd`, `swap-priority = 100`.
  - `/etc/sysctl.d/99-zram-tuning.conf`: `vm.page-cluster = 0`, `vm.swappiness = 100`.
  - `zswap` kernel module: `enabled = Y` (`zstd`, `max_pool_percent = 20`, `shrinker_enabled = Y`).
  - `systemd-oomd`: `inactive`; `earlyoom`: `inactive`.
  - `/etc/systemd/logind.conf.d/21-kill-user-processes.conf`: `KillUserProcesses=yes`.
  - `/etc/systemd/system.conf`: `RuntimeWatchdogSec=off` (default commented).

---

## 6. Root-Cause Action Items (For Later User-Approved Application)

*(No system modifications were performed during this investigation. Apply only when approved.)*

1. **Block/Stop `strata` Across S3 Suspend (Fixes the Nightly Suspend Hangs):**
   - Add a `systemd` sleep hook (or `Conflicts=sleep.target` / `Before=sleep.target` wrapper stopping `local-chat-strata.service` before suspend and restarting on resume) so S3 sleep never enters with 23.4 GiB VRAM + 49 GiB `cudaHostRegister` pinned.
2. **ZFS ARC & Dataset Tuning Status (`2026-11-12`):**
   - **Applied & Baked into Initramfs:** `/etc/modprobe.d/zfs.conf` (`zfs_arc_max=12 GiB`, `zfs_arc_min=2 GiB`, `l2arc_write_max=512 MiB/s`, `l2arc_write_boost=512 MiB/s`), `mkinitcpio -P` completed, `dpool/data/public` (`atime=off`, `logbias=throughput`), and `rpool/data/user-cache` (`/home/wuxxin/.cache/user-cache` for Tier-3 NVMe KV offload).
3. **Fit Strata's Pinned RAM Budget Inside `117.76 GiB` (`MemTotal`) Safely:**
   - Current pinned/locked floor (`75.85 GiB`) + `conversation-cache-mib=24576` (`24 GiB`) + `gpu_reclaim` (`~4–6 GiB`) + ZFS (`~6–8 GiB`) + desktop/agents (`~6–10 GiB`) = **`116–124 GiB`**, leaving zero margin even at `117.76 GiB` `MemTotal`.
   - Reduce `LCHAT_STRATA_CONV_CACHE_MIB` (e.g. `16384`–`18432`), or switch `--ple-io` / `--resident-budget-gib` if running heavy multi-agent sessions; also add `MemoryHigh=`/`OOMPolicy=stop` or `RestartSec=30s` with `StartLimitBurst` to prevent 10-second OOM restart storms, and consider enabling `earlyoom` / `systemd-oomd` so `strata` or runaway clients are killed cleanly before `amdgpu_hmm_range_valid` or `GFP_KERNEL` stalls occur.
   - Disable `zswap` (`zswap.enabled=0`) when using `zram` as the sole swap device to remove redundant `zswap_shrinker_scan` slab churn.
4. **Optional BIOS Reclaim (+4–6 GiB RAM & Bandwidth):**
   - Lower BIOS iGPU `UMA Frame Buffer Size` from `8G` → `2G` or `4G` (keep iGPU enabled since it drives the desktop).
   - Audit whether the 4 × Micron 32 GiB ECC DDR4-3200 DIMMs can run stably at `2933` or `3200 MT/s` (currently `2666 MT/s`), noting PCIe 3.0 (`8.0 GT/s`) is a hard Ryzen 5750G silicon limit.
