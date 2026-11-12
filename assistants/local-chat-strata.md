# Local Strata Chat Service Guide

`local-chat-strata.sh` manages the local Strata OpenAI API systemd user service (`local-chat-strata.service`), serving the **Qwen3.8-Flash-Next (Swift 1.5 GSQ-RCO)** MoE model with LLM chat, vision capabilities, bilingual speculative drafting, and runtime projective refusal control on AMD RDNA3 (Navi 31 / RX 7900 XTX).

Strata is designed as an alternative high-throughput inference engine to `local-chat.sh` on port `20080` ("either or"). It provides full LLM chat completions and multimodal vision encoder support, while omitting Fill-In-the-Middle (FIM) code completion and text embeddings. When Strata is selected, text embeddings are served by the dedicated `local-embedding.sh` service.

- **Engine Source**: Strata inference engine (`/usr/lib/strata/engine/strata` & `/usr/share/strata/serve/server.py`)
- **Vision Subsystem**: Strata HIP vision encoder (`/usr/lib/strata/engine/strata-vision-hip`)
- **Target Hardware**: AMD Radeon RX 7900 XTX (24 GiB VRAM, `gfx1100`) + 95 GiB Host RAM

---

## Architecture & Memory Profile

The deployment utilizes a hybrid VRAM/Host RAM split optimized for AMD Navi 31:

- **24 GiB VRAM (GPU)**:
  - Houses the native dense layers, attention projections, shared embeddings, and active KV cache (`k8v4`).
  - Speculative MTP draft head operating with full bilingual (German + English) vocabulary (~348 MiB).
  - Runtime projective control vector (`--control-vector-scaled ... --cvec-mode project`) intercepting hyper-connection streams across layers 4–44.
  - Multimodal vision encoder runs directly on GPU VRAM via `strata-vision-hip` with BF16 weights.
- **95 GiB Host RAM (CPU/DDR5)**:
  - Offloads expert weights into host RAM managed with an allocated budget of 42,000 MiB (~41 GiB).
  - Demand-paged PLE n-gram table (Shard 2).
  - High-concurrency prompt cache (6 slots) and dynamic conversation cache (24 GiB).
- **Zero-Swap Invariant**:
  - Requires 0B swap paging under 240,384 context with RX 7900 XTX (24 GiB VRAM) and 95 GiB Host RAM ceiling. All host memory allocations are locked via `LimitMEMLOCK=infinity`, `LimitAS=infinity`, and `HSA_USERPTR_FOR_PAGED_MEM=0`.
- **Direct Logging Launcher**:
  - Uses a lightweight Python launcher (`local-chat-strata-launcher.py`) that sets hardware and memory limits, imports Strata's `serve.server`, and routes engine/vision subprocess `stderr` directly to `sys.stderr` while `server.py` logs to `sys.stdout`. Systemd journal captures all output natively with zero disk log files or background tail hacks.

## Usage

### Installation & Lifecycle

Install the service, generate default `.env` configuration, launcher script, and config JSON:
```bash
./local-chat-strata.sh install [--no-start] [--new-config]
```

Start / Stop / Restart / Enable / Disable:
```bash
./local-chat-strata.sh start
./local-chat-strata.sh stop
./local-chat-strata.sh restart
./local-chat-strata.sh enable
./local-chat-strata.sh disable
```

Check runtime service status:
```bash
./local-chat-strata.sh status
```

Inspect logs:
```bash
./local-chat-strata.sh logs -f
```

Edit configuration in `$EDITOR` and restart automatically on exit:
```bash
./local-chat-strata.sh edit
```

Inspect generated unit file, `.env` file, config JSON, and launcher script:
```bash
./local-chat-strata.sh cat
```

Run validation tests (or benchmark):
```bash
./local-chat-strata.sh test [--benchmark]
```

### Execution & Transient Commands

Run Strata as a transient systemd user service (or foreground process in sandbox):
```bash
./local-chat-strata.sh exec [--env KEY=VALUE]* [-- server-args...]
```

Run a command inside the sandboxed environment:
```bash
./local-chat-strata.sh run [--env KEY=VALUE]* <command> [args...]
```

Spawn an interactive shell:
```bash
./local-chat-strata.sh shell [--env KEY=VALUE]*
```

---

## Configuration Reference (`local-chat-strata.env`)

Configuration is managed strictly through environment variables without requiring manual edits to JSON files. The script automatically synthesizes the engine configuration JSON from these settings upon installation, start, or transient execution.

| Parameter | Default | Description |
|---|---|---|
| `LCHAT_STRATA_PORT` | `20080` | Port for the OpenAI API server (defaults to 20080 matching local-chat) |
| `LCHAT_STRATA_HOST` | `127.0.0.1` | Host address to bind to |
| `LCHAT_STRATA_DEVICE` | `"0"` | HIP device ID (0 for RX 7900 XTX `gfx1100`) |
| `LCHAT_STRATA_MODEL` | `.../swift15_iq3s/models/swift-IQ3_S/...-00001-of-00002.gguf` | Path to Shard 1 (Native Strata layout) |
| `LCHAT_STRATA_PLE_MODEL` | `.../swift15_iq3s/models/swift-IQ3_S/...-00002-of-00002.gguf` | Path to Shard 2 (PLE n-gram table) |
| `LCHAT_STRATA_PACK` | `.../swift15_iq3s/packs/swift-iq3_s` | Strata native pack directory |
| `LCHAT_STRATA_MMPROJ` | `.../swift15_iq3s/models/mmproj-Swift-Qwen3.8-Flash-Next-BF16.gguf` | Vision projector encoder model (BF16) |
| `LCHAT_STRATA_MTP` | `.../swift15_iq3s/mtp/rt` | MTP speculative draft runtime directory (unpacked via `mtp_rt.py`) |
| `LCHAT_STRATA_MTP_VOCAB` | `""` | Draft vocabulary override (empty = default full bilingual German/English draft_vocab.bin) |
| `LCHAT_STRATA_ESP` | `/data/public/machine-learning/models/strata/projections/Qwen3.8-Flash-Next-experimental-speed-projection.gguf` | Uncensored runtime experimental speed projection and refusal elimination vector |
| `LCHAT_STRATA_ESP_SCALE` | `1.0` | Projection scaling factor ($\alpha$) |
| `LCHAT_STRATA_ESP_LAYERS` | `"4 44"` | Layer range for projective steering |
| `LCHAT_STRATA_MAX_CONTEXT` | `240384` | Maximum context window in tokens (240k) |
| `LCHAT_STRATA_PREFILL` | `"24576"` | Prefill chunk size (24,576 tokens = single-pass ingestion for $\le 24\text{k}$ prompts) |
| `LCHAT_STRATA_TEMPERATURE` | `0.6` | Deterministic agentic sampling temperature |
| `LCHAT_STRATA_REPEAT_PENALTY` | `1.1` | Repetition penalty preventing CoT reasoning loops |
| `LCHAT_STRATA_TOP_P` | `0.95` | Top-p nucleus sampling |
| `LCHAT_STRATA_TOP_K` | `20` | Top-k sampling limit |
| `LCHAT_STRATA_PCIE_FRAC` | `0.20` | Calibrated PCIe bandwidth fractional allocation |
| `LCHAT_STRATA_EXPERT_RAM_BUDGET` | `42000` | Host RAM budget for experts in MiB (~41 GiB) |
| `LCHAT_STRATA_PROMPT_CACHE` | `6` | Number of concurrent prompt cache slots (sized for multi-agent workflows) |
| `LCHAT_STRATA_CONV_CACHE_SLOTS` | `8` | Conversation cache slots (1 main + 4 subagents + LifeOS + spares) |
| `LCHAT_STRATA_CONV_CACHE_MIB` | `16384` | Conversation cache budget in MiB (16 GiB host RAM; safe under 117.76 GiB `MemTotal`) |
| `LCHAT_STRATA_CONV_CACHE_MIN_FREE_MIB` | `6144` | Minimum free RAM floor (6 GiB) preventing ZRAM thrashing / OOM storms |
| `LCHAT_STRATA_CONV_CACHE_MIN_TOKENS` | `4096` | Minimum prompt tokens before parking (keeps Pulse/hook calls out of slots) |
| `LCHAT_STRATA_CONV_CACHE_PARK_GAIN` | `2048` | Minimum token advance before re-snapshotting a parked conversation |
| `LCHAT_STRATA_DRAFTING` | `"mtp"` | Pinned speculative drafter (`mtp` matches Swift-1.5; overrides auto-switch) |
| `LCHAT_STRATA_SPEC` | `4` | Speculative draft token step count |
| `LCHAT_STRATA_SPEC_MIN_P` | `0.58` | Speculative acceptance probability threshold (paired with `STRATA_SPEC_COST=1`) |
| `LCHAT_STRATA_SUFFIX_DRAFT` | `3` | Suffix draft length |
| `LCHAT_STRATA_LOOKUP_CHAIN` | `2` | Chained n-gram lookup drafts appended after MTP proposals |
| `LCHAT_STRATA_ADAPT_ASYNC` | `1` | Asynchronous expert swapping |
| `LCHAT_STRATA_ADAPT_EVERY` | `1` | Adaptive step interval |
| `LCHAT_STRATA_ADAPT_SWAPS` | `160` | Calibrated parallel swap channels for host-to-device transfers (+22% tok/s) |
| `LCHAT_STRATA_ADAPT_DECAY` | `0.97` | Adaptive decay rate |
| `LCHAT_STRATA_KV` | `"k8v4"` | Quantization format for Key-Value cache |
| `LCHAT_STRATA_KV_GROW` | `true` | Elastic HIP VMM KV growth (starts at 16,384 cells, eliminates 2.19 GiB pinned KV RAM) |
| `LCHAT_STRATA_KV_RESIDENT` | `0` | Fixed VRAM resident KV cells (only used when `LCHAT_STRATA_KV_GROW=false`) |
| `LCHAT_STRATA_SLOT_SAVE_PATH` | `$HOME/.cache/user-cache` | Tier-3 NVMe `O_DIRECT` session save/restore directory (`rpool/data/user-cache`) |
| `LCHAT_STRATA_EXPERT_CACHE` | `"auto"` | Expert cache policy |
| `LCHAT_STRATA_VRAM_RESERVE_MIB` | `576` | VRAM reserve in MiB (leaves ~670 MiB at start, $\ge 530$ MiB after graph capture) |
| `LCHAT_STRATA_PLE_IO` | `"ram"` | PLE n-gram table storage tier |
| `LCHAT_STRATA_SPEED` | `"faster"` | Engine execution speed optimization tier |
| `LCHAT_STRATA_VISION` | `true` | Enable multimodal image reasoning via `strata-vision-hip` |
| `LCHAT_STRATA_VISION_TOKENS` | `1024` | Maximum tokens allocated for vision patches |
| `LCHAT_STRATA_ALIAS` | `qwen3.8-flash-next` | Primary model identifier reported to clients |
| `LCHAT_STRATA_ALIASES` | `qwen3.8-flash-next-swift15,qwen3.8-moe,swift-1.5,qwen3.8,qwen3` | Comma-separated alternative model aliases |
| `LCHAT_STRATA_TOKENIZER_DIR` | `.../swift15_iq3s/tok_runtime` | Pre-assembled tokenizer runtime directory pointing to `packs/swift-iq3_s/tokenizer-custom` with modified thinking-enabled `chat_template.jinja` |
| `LCHAT_STRATA_CHAT_TEMPLATE_KWARGS` | `'{"enable_thinking": true}'` | Template parsing arguments enabling reasoning |
| `LCHAT_STRATA_EXTRA_ARGS` | `""` | Extra arguments passed directly to `server.py` |
---

## Model Downloads & Auxiliary Preparation (`local-download.sh`)

Model files and execution runtimes are provisioned via `scripts/local-download.sh`:

```bash
# Complete deployment: downloads model shards (~84 GB) and all auxiliary runtime files
./scripts/local-download.sh /data/public/machine-learning/models --strata

# Download only the large model shards (~84 GB)
./scripts/local-download.sh /data/public/machine-learning/models --strata-shards

# Download and assemble all auxiliary runtime files without pulling the ~84 GB weights:
# - Vision mmproj (BF16)
# - MTP drafter weights & unpacked runtime (`mtp_rt.py`, `draft_vocab.bin`)
# - DSpark speculative drafter (`model.safetensors`, `config.json`)
# - Speed and refusal control vectors (`strata/projections/`)
# - Modified thinking-enabled Jinja template (froggeric v22.5)
# - Native pack preparation (`iq_pack.py` if Shard 1 is present)
# - Custom tokenizer runtime assembly (`packs/swift-iq3_s/tokenizer-custom/` & `tok_runtime` symlink)
./scripts/local-download.sh /data/public/machine-learning/models --strata-additional
```

## Hardware Environment & Kernel Flags

The launcher script sets low-level kernel optimizations specifically tuned for Navi 31:

- `STRATA_SCORES_THREAD=1`: Dedicated thread for attention score computation.
- `STRATA_WMMA_GEMM=1`: Hardware Wavefront Matrix Multiply-Accumulate (WMMA) execution.
- `STRATA_PF_GEMM=1` & `STRATA_PF_FUSED=1`: Prefill WMMA GEMM and fused expert execution.
- `STRATA_PF_PAD=1`: Pads FP16 activation row strides (+64) in `strata_pf_gemm_f16_ld` to eliminate 4KB memory channel camping across Navi 31 MCDs.
- `STRATA_DENSE_MMQ=1`: Quantized dense layer acceleration.
- `STRATA_HC_UPMIX=1`: Fuses hyper-connection up-projection and `gr_mix_r` for gfx11.
- `STRATA_PF_HCDOWN=1`: Fuses hyper-connection down and inject projections via native gfx11 WMMA GEMM.
- `STRATA_CVEC_FUSE=1`: Fuses FFN write, control vector projection, and next-half RMSNorm into a single sweep over $R$.
- `STRATA_PF_HC_REGION=1`: Places hyper-connection scratch memory into the shared attention/MoE region.
- `STRATA_PLE_COMPACT=1` & `STRATA_PLE_COPY_STREAM=1`: 7x compressed raw IQ4_NL PLE transfer over dedicated async DMA stream overlapping Layer 0 compute.
- `STRATA_PREFILL_WARM=1`: Pre-warms hipBLAS BF16 and FP16 libraries at startup, eliminating cold-prompt load delays.
- `STRATA_PREFILL_AUTO_MAX=24576`, `STRATA_PREFILL_RING=512`, `STRATA_PREFILL_ROUTED_STREAM=1`, `STRATA_EMB_REUSE_ACCOUNT=1`: Single-pass $\le 24\text{k}$ chunking, 512-slot PCIe staging ring (preventing `HIP_WMMA` from dropping to 96 slots), and pre-copy unrouted expert pruning.
- `STRATA_GDN_HEAD=1`, `STRATA_GDN_PP=2`, `STRATA_GDN_CONVL2=2`, `STRATA_GDN_NOY=1`: RDNA3 GDN recurrence, 2-column quad pass, single-pass conv+SiLU+L2 norm, and dead store elimination.
- `STRATA_HIP_WMMA=1`, `STRATA_PA_FAST=1`, `STRATA_SELECT_WMMA=1`, `STRATA_PF_F16=1`, `STRATA_PF_DM16=1`: RDNA3 matrix-core QSA attention/block-scorer and F16 matrix-core MoE kernels with FP16 combine rows.
- `STRATA_Q8_PACKED=1`, `STRATA_MMVF_ROWS=1`, `STRATA_ATTN_LANECELL=1`, `STRATA_ATTN_MERGE_V2=1`, `STRATA_EXPERT_V2=1`, `STRATA_TSUM=1`, `STRATA_LFUSE=1`, `STRATA_GDN_SPLIT=1`, `STRATA_QFUSE=1`, `STRATA_PLE_BATCH=1`, `STRATA_SMALL_UNR=3`, `STRATA_GR_Q32_G=2`, `STRATA_GR_Q8_PFS=1`, `STRATA_HEAD_MIX_MULTI=1`, `STRATA_FUSE_HITS=1`, `STRATA_FUSE_WAIT=1`, `STRATA_VERIFY_QDEDUP=1`, `STRATA_SPEC_COST=1`, `STRATA_FUSE_HEAD_GR=1`, `STRATA_NORM_ROPE=1`: Opt-in gfx1100 decode kernel fusions, grouped IQ3_S/IQ4_NL experts, and cost-aware speculative verification.
- `STRATA_HIPBLASLT_TUNING`: Points to the 48-row `gfx1100` `hipBLASLt 100202` table generated at `~/.local/state/strata/local-chat-strata-hipblaslt.txt` (covers `T=4096, 8192, 16384` across all `bf16` and `f16` model shapes).
- `HSA_USERPTR_FOR_PAGED_MEM=1`: Enables ROCm HSA userptr paged memory mapping (verified stable and +10% faster on kernel `7.2.14` + ROCm `7.2.4`).
- `STRATA_ROUTE_TAIL_SKIP=7`: Skips tail routing computations in MoE layers.
- `STRATA_MEMORY_LIMIT_MIB=0`: Unlimited system memory allocation.
- `STRATA_RESIDENT_HEADROOM_GIB=0`: Zero artificial headroom caps, maximizing contiguous allocations.
- `STRATA_SH_STREAM=0`: Shared expert execution on main stream (+1 tok/s speedup).
- `PYTHONUNBUFFERED=1` & `STRATA_REQUEST_LINES=1`: Direct unbuffered journal logging.
- `STRATA_ARENA_RELEASE=0`: Retains all VRAM-held experts in host DDR4-2666 ECC memory permanently, eliminating SSD re-reads on evictions.
---

## Coordinator Integration (`local-inference.sh`)

`local-chat-strata` integrates into `local-inference.sh` as an optional drop-in replacement for `local-chat`.

To switch from standard `local-chat` to `local-chat-strata`:

1. Edit `~/.config/systemd/user/local-inference.env` (or run `./assistants/local-inference.sh edit`):
   ```bash
   LCHAT_STRATA_ENABLED=1
   LCHAT_ENABLED=0
   LMBD_ENABLED=1
   ```
2. Restart services:
   ```bash
   ./assistants/local-inference.sh restart
   ```

Because both services default to port `20080`, `local-inference.sh` enforces a port collision safeguard: if both `LCHAT_ENABLED=1` and `LCHAT_STRATA_ENABLED=1` are set, the coordinator will fail fast and warn you to disable one before starting.
