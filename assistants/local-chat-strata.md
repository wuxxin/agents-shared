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
  - High-concurrency prompt cache (4 slots) and dynamic conversation cache (18 GiB).
- **Zero-Swap Invariant**:
  - Requires 0B swap paging. All host memory allocations are contiguous and locked via `LimitMEMLOCK=infinity` and `HSA_USERPTR_FOR_PAGED_MEM=0`.
---

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
| `LCHAT_STRATA_MODEL` | `.../swift15_iq3s/...-00001-of-00002.gguf` | Path to Shard 1 (Auto-detects native Strata `models/swift-IQ3_S/` or flat directory) |
| `LCHAT_STRATA_PLE_MODEL` | `.../swift15_iq3s/...-00002-of-00002.gguf` | Path to Shard 2 (Auto-detects native Strata `models/swift-IQ3_S/` or flat directory) |
| `LCHAT_STRATA_PACK` | `.../swift15_iq3s/packs/swift-iq3_s` | Strata pack directory (auto-detects `packs/swift-iq3_s` or `strata`) |
| `LCHAT_STRATA_MMPROJ` | `.../swift15_iq3s/models/mmproj-Swift-Qwen3.8-Flash-Next-BF16.gguf` | Vision projector encoder model (auto-detects `models/` or root) |
| `LCHAT_STRATA_MTP` | `.../swift15_iq3s/mtp/rt` | MTP speculative draft head directory (auto-detects `mtp/rt` or `strata/rt`) |
| `LCHAT_STRATA_MTP_VOCAB` | `""` | Draft vocabulary override (empty = default full bilingual German/English draft_vocab.bin) |
| `LCHAT_STRATA_ESP` | `/usr/share/strata/data/experimental-speed-projection/...` | Built-in runtime projective control vector for refusal elimination |
| `LCHAT_STRATA_ESP_SCALE` | `1.0` | Projection scaling factor ($\alpha$) |
| `LCHAT_STRATA_ESP_LAYERS` | `"4 44"` | Layer range for projective steering |
| `LCHAT_STRATA_MAX_CONTEXT` | `184320` | Maximum context window in tokens (~180k) |
| `LCHAT_STRATA_PREFILL` | `8192` | Prefill chunk size |
| `LCHAT_STRATA_EXPERT_RAM_BUDGET` | `42000` | Host RAM budget for experts in MiB (~41 GiB) |
| `LCHAT_STRATA_PROMPT_CACHE` | `4` | Number of concurrent prompt cache slots |
| `LCHAT_STRATA_CONV_CACHE_SLOTS` | `4` | Conversation cache slots |
| `LCHAT_STRATA_CONV_CACHE_MIB` | `18432` | Conversation cache size in MiB (18 GiB) |
| `LCHAT_STRATA_CONV_CACHE_MIN_FREE_MIB` | `2048` | Minimum free headroom for conversation cache |
| `LCHAT_STRATA_SPEC` | `5` | Speculative draft token step count |
| `LCHAT_STRATA_SPEC_MIN_P` | `0.75` | Speculative acceptance probability threshold |
| `LCHAT_STRATA_SUFFIX_DRAFT` | `3` | Suffix draft length |
| `LCHAT_STRATA_ADAPT_ASYNC` | `1` | Asynchronous expert swapping |
| `LCHAT_STRATA_ADAPT_SWAPS` | `8` | Parallel swap channels for host-to-device transfers |
| `LCHAT_STRATA_KV` | `"k8v4"` | Quantization format for Key-Value cache |
| `LCHAT_STRATA_KV_RESIDENT` | `32768` | VRAM resident KV cache token capacity |
| `LCHAT_STRATA_EXPERT_CACHE` | `"auto"` | Expert cache policy |
| `LCHAT_STRATA_VRAM_RESERVE_MIB` | `600` | Headroom reserved for display/OS allocations |
| `LCHAT_STRATA_SPEED` | `"faster"` | Engine execution speed optimization tier |
| `LCHAT_STRATA_VISION` | `true` | Enable multimodal image reasoning via `strata-vision-hip` |
| `LCHAT_STRATA_VISION_TOKENS` | `1024` | Maximum tokens allocated for vision patches |
| `LCHAT_STRATA_ALIAS` | `qwen3.8-flash-next-swift15` | Primary model identifier reported to clients |
| `LCHAT_STRATA_ALIASES` | `qwen3,qwen3.8-flash-next,swift-1.5,qwen3.8` | Comma-separated alternative model aliases |
| `LCHAT_STRATA_EXTRA_ARGS` | `""` | Extra arguments passed directly to `server.py` |

---

## Hardware Environment & Kernel Flags

The launcher script sets low-level kernel optimizations specifically tuned for Navi 31:

- `STRATA_SCORES_THREAD=1`: Dedicated thread for attention score computation.
- `STRATA_WMMA_GEMM=1`: Hardware Wavefront Matrix Multiply-Accumulate (WMMA) execution.
- `STRATA_PF_GEMM=1` & `STRATA_PF_FUSED=1`: Pipelined prefetch GEMM kernels.
- `STRATA_DENSE_MMQ=1`: Quantized dense layer acceleration.
- `STRATA_HIPBLASLT_TUNING`: Tuned gemm shapes from `/usr/share/strata/tools/hip/gfx1100-hipblaslt-100500.txt`.
- `HSA_USERPTR_FOR_PAGED_MEM=0`: Bypasses HSA user pointer paged memory faults.
- `STRATA_ROUTE_TAIL_SKIP=7`: Skips tail routing computations in MoE layers.
- `STRATA_RESIDENT_HEADROOM_GIB=6`: Preserves 6 GiB buffer headroom in system memory.

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
