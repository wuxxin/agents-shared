# llama.cpp Context Size Allocation Research: Total vs. Per-Slot

## Executive Summary

In `llama.cpp` (including `llama-server`), the command-line argument `-c` / `--ctx-size` (configured via `LCHAT_CTX_SIZE` in `local-chat.env`) represents the **total physical KV cache context length allocated across all parallel slots** in the server instance.

For standard multi-slot execution (where `kv_unified = false`, the default setting), the context available to each individual slot (`n_ctx_slot` or `n_ctx_seq`) is computed by dividing the total context size by the number of parallel slots (`LCHAT_PARALLEL` / `-np` / `--parallel`):

$$\text{per-slot context size} = \frac{\text{LCHAT\_CTX\_SIZE}}{\text{LCHAT\_PARALLEL}}$$

### Verification of Documentation Statement

The following table statement is **TRUE** and matches the current `llama.cpp` source code behavior:

| Setting | Value | Description |
|---|---|---|
| `LCHAT_CTX_SIZE` | `240384` | Total context length, equals `120192` per slot |
| `LCHAT_PARALLEL` | `2` | Concurrent chat slots |

With `LCHAT_CTX_SIZE = 240384` and `LCHAT_PARALLEL = 3`, `llama-server` allocates a total KV cache size of 240,384 tokens, providing **80,128 tokens per slot**.

---

## Technical Analysis & Source Code Evidence

Research conducted in `libggml-git-hip/src/llama.cpp` (`v10057.r3` / `b10059+`).

### 1. Command Line Parsing (`common/arg.cpp`)

The `--ctx-size` and `--parallel` CLI flags populate `common_params`:

```cpp
// common/arg.cpp
add_opt(common_arg(
    {"-c", "--ctx-size"}, "N",
    string_format("size of the prompt context (default: %d, 0 = loaded from model)", params.n_ctx),
    [](common_params & params, int value) {
        params.n_ctx = value;
    }
).set_env("LLAMA_ARG_CTX_SIZE"));

add_opt(common_arg(
    {"-np", "--parallel"}, "N",
    string_format("number of server slots (default: %d, -1 = auto)", params.n_parallel),
    [](common_params & params, int value) {
        params.n_parallel = value;
    }
).set_env("LLAMA_ARG_N_PARALLEL"));
```

### 2. Context Parameter Mapping (`common/common.cpp`)

In `common_context_params_to_llama`, `params.n_ctx` becomes `cparams.n_ctx` and `params.n_parallel` becomes `cparams.n_seq_max`:

```cpp
// common/common.cpp
struct llama_context_params common_context_params_to_llama(const common_params & params) {
    auto cparams = llama_context_default_params();

    cparams.n_ctx     = params.n_ctx;
    cparams.n_seq_max = params.n_parallel;
    ...
}
```

### 3. Context & Slot Division (`src/llama-context.cpp`)

During context initialization, `llama.cpp` computes `n_ctx_seq` (the sequence/slot context limit). In standard (non-unified) mode, `cparams.n_ctx` is divided by `cparams.n_seq_max`:

```cpp
// src/llama-context.cpp (lines 284-300)
cparams.n_ctx = GGML_PAD(cparams.n_ctx, 256);

if (cparams.kv_unified) {
    cparams.n_ctx_seq = cparams.n_ctx;
} else {
    cparams.n_ctx_seq = cparams.n_ctx / cparams.n_seq_max;
    cparams.n_ctx_seq = GGML_PAD(cparams.n_ctx_seq, 256);

    if (cparams.n_ctx_seq == 0) {
        throw std::runtime_error("n_ctx_seq == 0");
    }

    if (cparams.n_ctx != cparams.n_ctx_seq * cparams.n_seq_max) {
        cparams.n_ctx = cparams.n_ctx_seq * cparams.n_seq_max;
        LLAMA_LOG_WARN("%s: n_ctx is not divisible by n_seq_max - rounding down to %u\n", __func__, cparams.n_ctx);
    }
}
```

### 4. Server Slot Initialization (`tools/server/server-context.cpp`)

When `llama-server` sets up its request processing slots, each slot's maximum context capacity (`slot.n_ctx`) is set to `n_ctx_slot` (`llama_n_ctx_seq(ctx_tgt)`):

```cpp
// tools/server/server-context.cpp (lines 1247-1301)
int n_ctx_slot = llama_n_ctx_seq(ctx_tgt);

for (int i = 0; i < params_base.n_parallel; i++) {
    server_slot & slot = slots[i];
    ...
    slot.n_ctx = n_ctx_slot;  // Each slot gets n_ctx / n_parallel
}
```

When incoming requests are evaluated, the server validates token length against `slot.n_ctx` (e.g. line 3126: `if (slot.task->n_tokens() > slot.n_ctx)`).

---

## Unified KV Cache Mode (`--kv-unified` / `-kvu`)

Introduced via PR #16736 (commit `cd5e3b57541`):
If `--kv-unified` (`-kvu`) is enabled, `cparams.kv_unified` is `true`. In this mode:

```cpp
if (cparams.kv_unified) {
    cparams.n_ctx_seq = cparams.n_ctx;
}
```

In unified mode, `n_ctx_seq` is equal to `n_ctx`, allowing slots to dynamically share a single unified KV buffer up to the full total context limit. By default (`kv_unified = false`), static partitioning applies (`n_ctx / n_parallel`).

---

## Summary Matrix

| Mode | `LCHAT_CTX_SIZE` (`-c`) | `LCHAT_PARALLEL` (`-np`) | Effective Capacity per Slot (`n_ctx_slot`) |
|---|---|---|---|
| **Default (`kv_unified = false`)** | `240384` | `2` | **`120192` tokens per slot** (`240384 / 2`) |
| **Unified (`kv_unified = true`)** | `240384` | `2` | **Dynamic pool up to `240384` total tokens** across slots |
