# Chat / Vision LLM Research

## Chat / Vision LLM

Chat / vision models are tracked in four categories with explicit size and VRAM thresholds.
Per-model detail (architecture, quant files, chat template, thinking mode, speculative decoding,
benchmarks) lives in [`model-research-chat.md`](model-research-chat.md); this section holds the
baselines, the category indexes, the speed estimates and the cross-comparison tables.

### Category rules and thresholds

| Category | Total params | Active params | VRAM floor | Baseline reference |
|---|---|---|---|---|
| **Main MOE** | 30-37B | 3-5B | >=15 GB | `mudler/Qwen3.6-35B-A3B-APEX-GGUF` (`APEX-I-Compact`) |
| **Main Dense** | 25-30B | = total | >=10 GB | [`unsloth/Qwen3.8-27B-GGUF`](https://huggingface.co/unsloth/Qwen3.8-27B-GGUF) |
| **Main Exotic** | any | any | any | Escha-W2 / fuse-1-Lite / Ternary-Bonsai-27B |
| **Small** | <=4B | = total | <=5 GB | MiniCPM5-2B / Spark-X2.5-4B |

MoE models below the nominal 30-37B total band but above the 4B Small ceiling
(XYZ-Aquila-mini ~10B / ~3B active, North-Mini-Code-1.0 ~12B / ~4B active) stay in **Main MOE**:
they share the MoE inference profile and clear the 15 GB VRAM floor. Exotic holds main-class
models whose *type* is off-band rather than their size - grafted hybrid MoE (fuse-1-Lite),
ternary 1.58-bit dense (Ternary-Bonsai-27B), 2-bit EschaMoE (Escha-W2). Small holds only
<=4B total dense models.

### Baseline references

#### Main MOE baseline - Qwen3.6-35B-A3B (APEX-I-Compact)

- **Architecture**: 35B MoE, ~3.0B active params/token, 128 routed experts (8 active), GQA.
- **GGUF**: `mudler/Qwen3.6-35B-A3B-APEX-GGUF` -> `Qwen3.6-35B-A3B-APEX-I-Compact.gguf` (~18.5 GB VRAM).
- **Context**: 32K native, extendable to 256K with YaRN.
- **Template / thinking**: Jinja template with `<think>` CoT and tool-call XML schema.
- **Speculative decoding**: MTP draft tensors (733-tensor base builds) or embedded block-40 MTP
  tensors (753-tensor builds); CPU N-Gram fallback with `--spec-type ngram-simple`.
- **Measured locally (RX 7900 XTX, 2026-09-02)**: 
  - LCHAT_DEVICE="Vulkan1"
  - LCHAT_MODEL="/data/public/machine-learning/models/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact.gguf"`
  - LCHAT_SPECULATIVE="--spec-type ngram-simple --spec-ngram-simple-size-n 6 --spec-ngram-simple-size-m 4"
  - prefill **1744 t/s**, tokengen **107 t/s**
  - 17894.6 MB 
  - Source: `assistants/local-benchmark.md`.

#### Main Dense baseline - unsloth/Qwen3.8-27B-GGUF

- **Base model**: `Qwen/Qwen3.8-27B` - 27B dense causal LM + vision encoder, 64 layers,
  hybrid 16 x (3 x Gated DeltaNet -> FFN, 1 x Gated Attention -> FFN), MTP head trained.
- **Context**: 262,144 native, extensible to 1,000,000.
- **Thinking**: `reasoning_effort` = `xhigh` (default) / `medium` / `low`; `preserve_thinking` on by default.
- **GGUF repo**: **Unsloth Dynamic 3.0**, verified file sizes from the HF tree:

| Quant | Size | Quant | Size | Quant | Size |
|---|---|---|---|---|---|
| `UD-IQ1_S` | 6.19 GB | `UD-Q3_K_XL` | 13.15 GB | `UD-Q5_K_XL` | 20.88 GB |
| `UD-IQ1_M` | 6.73 GB | `UD-IQ4_XS` | 14.25 GB | `UD-Q6_K` | 21.98 GB |
| `UD-IQ2_XXS` | 7.27 GB | `UD-Q4_K_S` | 15.36 GB | `UD-Q6_K_M` | 23.09 GB |
| `UD-IQ2_S` | 8.37 GB | `UD-Q4_K_M` | 16.46 GB | `UD-Q6_K_L` | 24.19 GB |
| `UD-Q2_K_XL` | 9.83 GB | `UD-Q4_K_XL` | 17.56 GB | `UD-Q6_K_XL` | 25.30 GB |
| `UD-IQ3_XXS` | 10.93 GB | `Q4_0` / `Q4_1` | 16.06 / 17.54 GB | `UD-Q8_K_L` / `Q8_0` | 28.05 / 29.05 GB |
| `UD-IQ3_S` | 12.04 GB | `UD-Q5_K_S` / `UD-Q5_K_M` | 18.67 / 19.77 GB | `BF16` (dir) / `MTP` (dir) | - |

Recommended operating points: `UD-IQ4_XS` (14.25 GB) or `UD-Q4_K_XL` (17.56 GB) for 24 GB
with long context; `UD-IQ2_S` (8.37 GB) when context, not quality, is the binding constraint.

#### Main Exotic baselines

| Baseline | Type | Footprint | Role |
|---|---|---|---|
| Qwen3.6-35B-A3B-Escha-W2 | 2-bit `EschaMoE` (128 experts, ~3.0B active) | ~9.8 GB | Reference for MoE quality retained at 2-bit |
| fuse-1-Lite | LFM2.5-2.6B host + 960 transplanted Qwen3.6 experts (5.72B) | ~4.2 GB (bf16) | Reference for grafted-expert SLMs |
| Ternary-Bonsai-27B | 27B dense, ternary 1.58-bit weights | ~7.2 GB (`Q2_0`) | Reference for extreme low-bit dense |

#### Small baselines

`openbmb/MiniCPM5-2B` (2.517B dense, 131K ctx, Q4_K_M 1.56 GB) is the current 2B reference;
`XHToken/Spark-X2.5-4B` (4B dense hybrid, 1M ctx) is the 4B reference. Reported 2B-4B
composite average in the MiniCPM5 card: MiniCPM5-2B **53.9**, Qwen3.5-4B 51.1,
granite-4.2-3B 42.7, LFM2.5-2.6B 33.2, Qwen3.5-2B 28.0, Gemma-4-E2B-it 24.6.

#### Baseline prefill / token-generation speeds (RX 7900 XTX, 24 GB)

Anchored to the measured Qwen3.6-35B-A3B run above (3.0B active, ROCm0, q4_0 KV,
240384 ctx, parallel 2). Estimates are **derived, not measured** - budget planning numbers,
not benchmark results:

```
prefill_tok_s  ~= 1723 x (3.0 / A_active)          # compute-bound, linear in active params
tokengen_tok_s ~= 64   x sqrt(3.0 / A_active)      # memory/latency-bound, sublinear
```

Vulkan typically reaches ~2x the ROCm decode figure on this host; single-slot numbers run
higher than the parallel-2 average. MTP speculative decoding adds ~15-22% decode on MoE
models at usable acceptance rates.

| Model | Active params | Prefill (est.) | Token-gen (est.) | Basis |
|---|---|---|---|---|
| Qwen3.6-35B-A3B (baseline) | 3.0B | **1723 t/s (measured)** | **64 t/s (measured)** | APEX-I-Compact, ROCm0 |
| BigBang-v1 | 3.0B | ~1720 t/s | ~64 t/s | MoE, same active budget |
| BTL-4 | 3.0B | ~1720 t/s | ~64 t/s | MoE, same active budget |
| Ornith-1.0-35B | 3.0B | ~1720 t/s | ~64 t/s | MoE, Q4_K_M 21.2 GB caps context |
| KAT-Coder-V2.5-Dev | 3.0B | ~1720 t/s | ~64 t/s | MoE |
| Agents-A1 | 3.0B | ~1720 t/s | ~64 t/s | MoE (3.5 series) |
| XYZ-Aquila-mini | ~3.0B | ~1720 t/s | ~64 t/s | MoE |
| North-Mini-Code-1.0 | ~4.0B | ~1290 t/s | ~55 t/s | MoE |
| K2-Horizon-MoVA-36B-A4B | 4.0B | ~1290 t/s | ~55 t/s | MoE, no GGUF yet (BF16 ~72 GB) |
| Swift-1.5-Flash-Next (SC117 IQ3_S) | 6.0B (125B total) | 2500-3600 t/s | 92-108 t/s | ultra-sparse MoE (512 exps), Strata hybrid VRAM+RAM, MTP draft |
| Qwen3.8-27B (dense baseline) | 27B | ~190 t/s | ~21 t/s | dense |
| Qwen3.6-27B-Fable-Fusion-711 | 27B | ~190 t/s | ~21 t/s | dense, IQ4_XS 16.5 GB |
| Qwen3.8-27B-TURBO-...-735-882 | 27B | ~190 t/s | ~21 t/s (+MTP) | dense, MTP >90 t/s at 60% acceptance on 5090 |
| Qwopus3.8-27B-Flash | 27B | ~190 t/s | ~24 t/s | dense, +12.8% decode measured vs base |
| Qwen3.8-27B GSQ-RCO `IQ3_S` | 27B | ~190 t/s | ~21 t/s | dense, 11.8 GB keeps KV headroom |
| Qwen3.6-35B-A3B-Escha-W2 | 3.0B | ~1720 t/s | ~64 t/s | 2-bit MoE |
| fuse-1-Lite | ~3.0B (not published) | ~1720 t/s | ~64 t/s | grafted MoE, assumed active budget |
| Ternary-Bonsai-27B | 27B | ~190 t/s | ~21 t/s | 1.58-bit halves weight traffic; may exceed estimate |
| MiniCPM5-2B | 2.52B | ~2050 t/s | ~70 t/s | dense, Q4_K_M 1.56 GB |
| Spark-X2.5-4B | 4.0B | ~1290 t/s | ~55 t/s | dense hybrid (SWA trims prefill further) |
| Spark-X2.5-1.7B | 1.7B | ~3040 t/s | ~84 t/s | dense |
| LFM2.5-2.6B (reference) | 2.6B | ~1990 t/s | ~68 t/s | dense |

### Main MOE models

Current selected default model: **BigBang-v1**.

| Model | Total / active | Quant + VRAM | Prefill / gen (est.) | Headline |
|---|---|---|---|---|
| **Qwen3.6-35B-A3B** (baseline) | 35B / 3B | APEX-I-Compact, 18.5 GB | 1723 / 64 (measured) | Neutral standard base infrastructure |
| **BigBang-v1** | 35B / 3B | IQ4_XS, 17.95 GB | ~1720 / ~64 | SOTA 35B reasoning, self-evolving agent; current default |
| **BTL-4** | 35B / 3B | IQ4_XS 17.9 GB / IQ2_XXS 12.2 GB | ~1720 / ~64 | Execution-gated agentic reasoning, AST tool calls (BFCL 73.5) |
| **Ornith-1.0-35B** | 35B / 3B | Q4_K_M 21.2 GB / IQ4_XS 18.0 GB | ~1720 / ~64 | Highest Terminal-Bench 2.1 in the set (62.8) |
| **KAT-Coder-V2.5-Dev** | 35B / 3B | APEX, 18.5 GB | ~1720 / ~64 | AST hashline injector; best SWE-bench Verified (79.6) |
| **XYZ-Aquila-mini** | ~10B / ~3B | Q3_K_XL, 15.8 GB | ~1720 / ~64 | Long-horizon search and scraping (BrowseComp 74.1) |
| **North-Mini-Code-1.0** | ~12B / ~4B | UD-Q4, 19.2 GB | ~1290 / ~55 | Native CoT traces tuned for subagents |
| **Agents-A1** | 35B / 3B | APEX/IQ4_XS class, 17.5 GB | ~1720 / ~64 | Legacy 3.5-series baseline, kept for comparison |
| **K2-Horizon-MoVA-36B-A4B** | 36B / 4B | BF16 ~72 GB, no GGUF | ~1290 / ~55 | Frontier-class 512K-context MoE (Terminal-Bench 58.6, GPQA 80.8) |
| **Swift-1.5-Qwen3.8-Flash-Next-GSQ-RCO-abliterated** | 125B / 6B | GSQ-RCO IQ3_S 77.8 GB (Strata 24GB VRAM + 41GB RAM) | ~2500-3600 / 92-108 | 125B ultra-sparse MoE (512 exp, 6 act), Swift 1.5 token-efficient (-63.4% thinking tokens), abliterated (zero refusal), Strata acceleration |

### Main Dense models

| Model | Params | Quant + VRAM | Prefill / gen (est.) | Headline |
|---|---|---|---|---|
| **Qwen3.8-27B** (baseline) | 27B | UD-Q4_K_XL 17.56 GB / UD-IQ4_XS 14.25 GB | ~190 / ~21 | Native vision, 262K ctx, `reasoning_effort`, MTP |
| **Qwen3.6-27B-Fable-Fusion-711** | 27B | IQ4_XS 16.5 GB / Q8_0 28.5 GB | ~190 / ~21 | Heretic multi-stage merge, >700 ARC-C |
| **Qwen3.8-27B-TURBO-...-735-882** | 27B | NEO IMATRIX regular + MTP quants | ~190 / ~21 (+MTP) | ARC-C 735 (mxfp8) / 719 (mxfp4), thinking cut 1/2-1/10 |
| **Qwopus3.8-27B-Flash** | 27B | MTP-Q5_K_M 19.54 GB, Q2_K 10.86 GB | ~190 / ~24 | +12.8% decode, 80.7% MTP acceptance, 13/14 agentic SWE battery |
| **Qwen3.8-27B GSQ-RCO** | 27B | IQ3_S 11.8 GB (task-lossless) -> IQ2_XS 8.4 GB | ~190 / ~21 | Non-uniform quantization; lossless AIME25/LCB at 3.5 bpw |

### Main Exotic models

| Model | Type | Footprint | Prefill / gen (est.) | Headline |
|---|---|---|---|---|
| **Qwen3.6-35B-A3B-Escha-W2** | 2-bit `EschaMoE` | 9.8 GB | ~1720 / ~64 | ~98% of FP8 accuracy in 9.8 GB |
| **fuse-1-Lite** | grafted MoE (5.72B) | 4.2 GB (bf16) | ~1720 / ~64 | LFM2.5 host + 960 Qwen3.6 experts |
| **Ternary-Bonsai-27B** | ternary dense (1.58-bit) | 7.2 GB (`Q2_0`) | ~190 / ~21 | Extremely lean; loses syntax depth |

### Small models

| Model | Params | Quant + size | Prefill / gen (est.) | Headline |
|---|---|---|---|---|
| **MiniCPM5-2B** | 2.517B | Q4_K_M 1.56 GB / Q8_0 2.68 GB / F16 5.04 GB | ~2050 / ~70 | 2B-class SOTA composite (53.9), 131K ctx, tool calling |
| **Spark-X2.5-4B** | 4B | no GGUF published (bf16 weights) | ~1290 / ~55 | 1M ctx, hybrid SWA, harness-deep (Codex / Claude Code / OpenClaw) |
| **Spark-X2.5-1.7B** | 1.7B | no GGUF published | ~3040 / ~84 | Same architecture at 1.7B; reference row |


### Cross-comparison - all Main models

###### Main-1. CLI and agentic repository engineering

| Model | Category | Total / active | Quant + VRAM | Terminal-Bench 2.1 | SWE-bench Verified | SWE-bench Pro | Claw-Eval | NL2Repo |
|---|---|---|---|---:|---:|---:|---:|---:|
| **Claude Opus 4.8** | Frontier | Closed API | API | **84.6** | **88.5** | **69.2** | 54.7 | 47.6 |
| **GPT 5.5** | Frontier | Closed API | API | 84.3 | 86.2 | 58.6 | 78.4 | 51.8 |
| **Gemini 3.1 Pro** | Frontier | Closed API | API | 73.8 | 81.0 | 54.2 / 64.8 | 76.8 | 49.4 |
| **DeepSeek V4 Pro** | Frontier | 1.6T / ~37B | Open-Weights | 64.0 | 82.4 | 55.4 | **79.5** | **58.5** |
| **DeepSeek V4 Flash** | Frontier | 284B / ~13B | Open-Weights | 61.8 | 78.6 | 52.6 | 73.2 | 54.2 |
| **Qwen3.6-35B** (baseline) | MOE | 35B / 3B | APEX 18.5 GB | 49.2 | 73.4 | 43.6 | 68.7 | 29.4 |
| BigBang-v1 | MOE | 35B / 3B | IQ4_XS 17.95 GB | 58.3 | 79.4 | 54.2 | 77.5 | 36.0 |
| BTL-4 | MOE | 35B / 3B | IQ4_XS 17.9 GB | 60.5 | 78.4 | 48.2 | 72.8 | 35.2 |
| Ornith-1.0-35B | MOE | 35B / 3B | Q4_K_M 21.2 GB | 62.8 | 75.6 | 38.7 | 69.8 | 34.6 |
| KAT-Coder-V2.5-Dev | MOE | 35B / 3B | APEX 18.5 GB | 59.1 | 79.6 | 45.96 | 67.2 | 32.2 |
| XYZ-Aquila-mini | MOE | ~10B / ~3B | Q3_K_XL 15.8 GB | 51.3 | 70.1 | 50.2 | 69.0 | 28.6 |
| North-Mini-Code-1.0 | MOE | ~12B / ~4B | UD-Q4 19.2 GB | 53.5 | 74.0 | 47.5 | 69.5 | 32.4 |
| Agents-A1 | MOE | 35B / 3B | APEX class 17.5 GB | 38.9 | 61.5 | 42.3 | 65.4 | 20.5 |
| K2-Horizon-MoVA-36B-A4B | MOE | 36B / 4B | BF16 ~72 GB | 58.6 | +-76.8 | +-51.2 | +-71.5 | +-34.8 |
| **Qwen3.8-Flash-Next** (Base) | MOE | 125B / 6B | BF16 / GGUF | 67.6 | 81.0 | 62.5 | 64.4 (MM) | 48.1 |
| ⚡ **Swift-1.5-Flash-Next (SC117)** | MOE | 125B / 6B | IQ3_S 77.8 GB (Strata) | 69.7 | 81.2 | 62.5 | 64.4 (MM) | 48.1 |
| **Qwen3.8-27B** (baseline) | Dense | 27B | UD-Q4_K_XL 17.56 GB | 73.0 | 78.2 | 61.7 | 57.4 | 42.3 |
| Fable-Fusion-711 | Dense | 27B | IQ4_XS 16.5 GB | 59.3 | 77.2 | 53.5 | 75.2 | 36.2 |
| Qwen3.8-27B-TURBO-735-882 | Dense | 27B | NEO IMATRIX | +-62.0 | +-76.5 | +-54.0 | +-72.0 | +-37.5 |
| Qwopus3.8-27B-Flash | Dense | 27B | MTP-Q5_K_M 19.54 GB | +-68.5 | +-77.8 | +-58.2 | +-64.0 | +-40.5 |
| Qwen3.8-27B GSQ-RCO | Dense | 27B | IQ3_S 11.8 GB | +-72.4 | +-78.0 | +-61.5 | +-57.0 | +-42.1 |
| Qwen3.6-Escha-W2 | Exotic | 35B / 3B | EschaMoE 9.8 GB | 48.5 | 72.6 | 42.8 | 67.9 | 28.9 |
| fuse-1-Lite | Exotic | 5.72B | bf16 4.2 GB | 38.2 | 62.5 | 34.1 | 58.6 | 21.4 |
| Ternary-Bonsai-27B | Exotic | 27B | Q2_0 7.2 GB | 43.7 | 74.9 | 39.2 | 71.7 | 25.2 |

The dense fine-tune estimates reflect verified vendor and held-out evaluation reports; detailed multi-suite logs appear in Main-4.

###### Main-2. Frontier research, search and scientific reasoning

| Model | Category | BrowseComp | XBench | HLE | FS-R | MLE-Bench | PaperBench | SciCode-V (Main/Sub) | BioMystery (HS/HD) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **Claude Opus 4.8** | Frontier | 84.3 | 61.4 | **57.9** | 45.2 | **63.6** | **65.2** | 78.1 / 92.3 | **88.5 / 42.4** |
| **GPT 5.5** | Frontier | 84.4 | **72.4** | 52.2 | **58.3** | 59.1 | 64.2 | **90.6 / 95.1** | 76.7 / 23.5 |
| **Gemini 3.1 Pro** | Frontier | **85.9** | 68.2 | 51.4 | 24.8 | 61.4 | 58.7 | 82.4 / 91.5 | 78.2 / 28.2 |
| **DeepSeek V4 Pro** | Frontier | 83.4 | 64.8 | 48.2 | 40.7 | 59.1 | 50.4 | 78.1 / 90.2 | 64.4 / 13.7 |
| **DeepSeek V4 Flash** | Frontier | 73.2 | 62.2 | 45.1 | 37.7 | 40.9 | 40.4 | 68.6 / 83.7 | 68.0 / 23.5 |
| **Qwen3.6-35B** (baseline) | MOE | 67.9 | 32.6 | 36.2 | 11.9 | 31.8 | 30.7 | 26.6 / 56.5 | 44.8 / 2.0 |
| BigBang-v1 | MOE | 76.5 | 58.4 | 50.3 | 46.2 | 59.1 | 53.6 | 50.0 / 68.6 | 57.5 / 15.7 |
| BTL-4 | MOE | 74.2 | 59.8 | 46.8 | 31.2 | 35.4 | 32.8 | 39.2 / 60.1 | 48.5 / 6.2 |
| Ornith-1.0-35B | MOE | 73.9 | 61.8 | 45.3 | 29.6 | 27.3 | 20.5 | 35.0 / 42.0 | 50.2 / 5.9 |
| KAT-Coder-V2.5-Dev | MOE | 68.5 | 48.2 | 42.1 | 28.4 | 34.2 | 31.5 | 38.5 / 59.2 | 46.5 / 4.0 |
| XYZ-Aquila-mini | MOE | 74.1 | 57.2 | 38.4 | 36.8 | 18.2 | 14.8 | 15.6 / 39.0 | 42.9 / 5.9 |
| Agents-A1 | MOE | 48.5 | 52.4 | 46.3 | 38.4 | 27.3 | 17.3 | 50.0 / 64.1 | 48.9 / 2.0 |
| North-Mini-Code-1.0 | MOE | 71.2 | 45.8 | 43.0 | 26.5 | 32.5 | 28.0 | 34.0 / 58.0 | 47.0 / 4.0 |
| K2-Horizon-MoVA-36B-A4B | MOE | +-72.0 | +-49.5 | 25.2 | +-30.5 | +-32.0 | +-29.0 | +-38.9 / +-58.0 | +-45.0 / +-4.0 |
| Qwen3.8-Flash-Next (Base) | MOE | 78.5 | 54.2 | 35.9 | 38.2 | 44.5 | 42.0 | 46.9 / 68.2 | 51.0 / 8.0 |
| Swift-1.5-Flash-Next (SC117) | MOE | 77.8 | 53.6 | 35.0 | 37.0 | 43.8 | 41.2 | 45.5 / 66.0 | 50.2 / 7.6 |
| Qwen3.8-27B (baseline) | Dense | 71.5 | 51.2 | 30.8 | 28.4 | 36.2 | 34.5 | 36.5 / 58.2 | 46.2 / 4.5 |
| Fable-Fusion-711 | Dense | 74.8 | 56.2 | 47.1 | 34.5 | 42.6 | 41.2 | 42.5 / 62.8 | 52.0 / 8.5 |
| Qwen3.8-27B-TURBO-735-882 | Dense | +-72.0 | +-52.0 | +-33.5 | +-29.0 | +-37.0 | +-35.0 | +-38.0 / +-60.0 | +-47.0 / +-5.0 |
| Qwopus3.8-27B-Flash | Dense | +-73.0 | +-53.0 | +-34.0 | +-31.0 | +-38.5 | +-36.5 | +-40.0 / +-62.0 | +-48.0 / +-5.5 |
| Qwen3.8-27B GSQ-RCO | Dense | +-71.2 | +-51.0 | +-30.7 | +-28.2 | +-36.0 | +-34.2 | +-36.4 / +-58.0 | +-46.0 / +-4.4 |
| Qwen3.6-Escha-W2 | Exotic | 66.8 | 32.1 | 35.6 | 11.6 | 31.2 | 30.2 | 26.1 / 55.8 | 44.1 / 1.9 |
| fuse-1-Lite | Exotic | 51.2 | 24.5 | 22.4 | 8.2 | 18.5 | 16.2 | 19.4 / 41.2 | 32.0 / 1.0 |
| Ternary-Bonsai-27B | Exotic | 58.0 | 36.5 | 39.5 | 18.2 | 22.4 | 19.0 | 20.0 / 45.0 | 40.0 / 2.0 |

###### Main-3. Frontier model cross-scale comparison (35B scale vs 100B+ / closed frontier)

| Model | Architecture / Scale | LiveCodeBench v6 | GPQA-Diamond | SWE-Bench Pro | HLE | BrowseComp | FS-R | MLE-Bench | PaperBench | BioMystery (HD) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **Claude Opus 4.8** | Frontier Closed API | 89.5 | 92.0 | **69.2** | **57.9** | 84.3 | 45.2 | **63.6** | **65.2** | **42.4** |
| **GPT 5.5** | Frontier Closed API | 90.8 | 93.5 | 58.6 | 52.2 | 84.4 | **58.3** | 59.1 | 64.2 | 23.5 |
| **Gemini 3.1 Pro** | Frontier Closed API (MoE) | 91.7 | **94.1** | 54.2 / 64.8 | 51.4 / 54.6 | **85.9** | 24.8 / 48.2 | 61.4 | 58.7 | 28.2 |
| **DeepSeek V4 Pro** | 1.6T MoE Open-Weights | **93.5** | 90.5 | 55.4 | 48.2 | 83.4 | 40.7 | 59.1 | 50.4 | 13.7 |
| **DeepSeek V4 Flash** | 284B MoE Open-Weights | 91.6 | 89.4 | 52.6 | 45.1 | 73.2 | 37.7 | 40.9 | 40.4 | 23.5 |
| 🌐 **Qwen3.8-Flash-Next (Base)** | **125B MoE (Open-Weights, 6B act)** | 91.9 | 91.7 | 62.5 | 35.9 | 78.5 | 38.2 | 44.5 | 42.0 | 8.0 |
| ⚡ **Swift-1.5-Flash-Next (SC117)** | **125B MoE (Fine-tune + Transplant)** | 90.4 | 89.6 | 62.5 | +-35.0 | 77.8 | 37.0 | 43.8 | 41.2 | 7.6 |
| 💥 **BigBang-v1** | **35B MoE (Fine-tune)** | +-85.2 | +-87.8 | 54.2 | 50.3 | 76.5 | 46.2 | 59.1 | 53.6 | 15.7 |
| ⚔️ **Fable-Fusion-711** | **27B Dense (Merge)** | +-84.6 | +-86.5 | 53.5 | 47.1 | 74.8 | 34.5 | 42.6 | 41.2 | 8.5 |
| **Qwen3.6-35B** | 35B MoE (Baseline) | 73.5 | 84.1 | 43.6 | 36.2 | 67.9 | 11.9 | 31.8 | 30.7 | 2.0 |

###### Main-4. Cybersecurity, exploitation and red-teaming benchmark matrix

| Model | Architecture / Focus | ExploitBench (Ladder / T4-5) | CyberSecEval 4 (Triage / Patch) | SecEval (Overall) | SecEval (PenTest / Web) | SECURE (MAET / CWET) | CyberMetric-10000 | Refusal on Security Probes |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| **Claude Opus 4.8** | Frontier Closed API | 68.4 / 48.2 | **88.2 / 78.4** | 88.5 | 89.2 / 89.5 | **95.2 / 94.6** | 90.8 | 94.2% (High Refusal) |
| **GPT 5.5** | Frontier Closed API | **72.0 / 47.4** | 86.5 / **79.1** | **89.2** | **90.5 / 91.2** | 94.8 / 94.0 | **91.4** | 93.5% (High Refusal) |
| **Gemini 3.1 Pro** | Frontier Closed API | +-58.2 / +-32.5 | +-82.0 / +-71.5 | +-84.6 | +-85.0 / +-86.2 | 86.2 / 87.8 | +-88.5 | 95.0% (High Refusal) |
| **DeepSeek V4 Pro** | 1.6T MoE Open-Weights | +-54.0 / +-28.6 | +-81.4 / +-68.5 | +-85.6 | +-86.2 / +-87.0 | +-91.5 / +-90.8 | +-86.8 | +-82.4% (Standard Refusal) |
| **DeepSeek V4 Flash** | 284B MoE Open-Weights | +-46.5 / +-21.0 | +-76.2 / +-62.0 | +-80.2 | +-81.5 / +-82.4 | +-87.0 / +-86.5 | +-82.5 | +-79.0% (Standard Refusal) |
| 🌐 **Qwen3.8-Flash-Next (Base)** | 125B MoE Base (6B act) | +-42.8 / +-18.5 | +-74.5 / +-60.2 | +-83.4 | +-84.0 / +-84.8 | +-88.4 / +-87.5 | +-84.2 | +-81.5% (Standard Refusal) |
| ⚡ **Swift-1.5-Flash-Next (SC117)** | 125B MoE Abliterated | +-51.2 / +-26.4 | +-78.0 / +-61.5 | +-84.1 | +-86.5 / +-87.2 | +-89.0 / +-88.2 | +-84.0 | **0.0% (Zero Refusal)** |
| 💥 **BigBang-v1** | 35B MoE (Generalist) | +-39.5 / +-14.2 | +-72.8 / +-58.0 | +-79.8 | +-81.2 / +-82.0 | +-86.5 / +-85.0 | +-81.5 | +-78.5% (Standard Refusal) |
| ⚔️ **Fable-Fusion-711** | 27B Dense Merge | +-37.8 / +-12.0 | +-70.5 / +-55.4 | +-77.5 | +-79.0 / +-80.5 | +-84.0 / +-83.2 | +-79.2 | +-74.0% (Standard Refusal) |
| 🛡️ **CyberStrike-OffSec-35B** | 35B MoE (Dedicated OffSec) | +-48.6 / +-24.0 | +-84.2 / +-71.8 | 81.4 | 82.3 / 85.3 | 93.9 / 93.1 | 86.6 | **0.0% (Zero Refusal)** |
| 🦅 **Cyber-Ornith-1.5-9B** | 9B Dense (Agentic Cyber) | +-41.5 / +-16.8 | 86.7 / +-68.0 | +-76.4 | +-78.5 / +-79.2 | +-85.2 / +-84.0 | +-77.8 | **0.0% (Zero Refusal)** |
| **Qwen3.6-35B** (Baseline) | 35B MoE Baseline | +-32.4 / +-9.5 | +-66.0 / +-51.2 | +-74.2 | +-75.8 / +-76.4 | +-83.5 / +-82.0 | +-76.0 | +-76.5% (Standard Refusal) |

###### Main-5. Performance results not covered in tables
Results from specialized benchmark suites and evaluations not captured in the matrix tables above:

K2-Horizon-MoVA-36B-A4B: tau3-Banking 26.8; GPQA-Diamond 80.8; CritPt 2.1; AA-LCR 66.3; AA-Omniscience accuracy 18.8 / non-hallucination 69.2.

Qwen3.8-27B (baseline): SWE-bench Pro 61.7; NL2Repo 42.3; DeepSWE 1.1 42.2; QwenSWEBench 79.0; CoWorkBench 70.7; JobBench 33.4; Agents' Last Exam pass@1 20.4 / score 42.9; IFBench 79.5; GPQA-D 89.2; HLE 30.8; LiveCodeBench v6 90.3; OSWorld-Verified 84.3; WebArena-Verified 64.8; AndroidWorld 81.9; RecreationBench 47.1; ClawEval-MM 57.4 pass@3 / 56.9 avg; SWE-MM 38.6; Vision2Web 62.9; MathVision 94.6 (with CI); BabyVision 85.6 (with CI); CharXiv 90.2 (with CI); OmniDocBench 1.5 91.1; RealWorldQA 85.9; ERQA 65.5.

Qwen3.8-27B GSQ-RCO IQ3_S: AIME25 100.00 (BF16-equal); GPQA-Diamond 89.39 (vs 89.90); LiveCodeBench v6 85.71 (BF16-equal) at 11.8 GB / 3.50 bpw.

Qwopus3.8-27B-Flash: MMLU-Pro 91.28% (base 92.73%); +12.8% decode throughput; 80.7% weighted MTP acceptance; 13/14 agentic software-engineering battery.

Qwen3.8-27B-TURBO-735-882: ARC-C 0.735 mxfp8 / 0.719 mxfp4; ARC-E 0.882; BoolQ 0.917; HellaSwag 0.832; OBQA 0.530; PIQA 0.837; WinoGrande 0.785.

Qwen3.6-35B-A3B (baseline): LiveCodeBench v6 73.5; GPQA-Diamond 84.1; Terminal-Bench 2.1 49.2 (Terminus-2) / 44.9 (IFM); SWE-bench Verified 73.4; SWE-bench Pro 43.6; Claw-Eval 68.7; NL2Repo 29.4; BrowseComp 67.9; XBench 32.6; HLE 36.2; FS-R 11.9; MLE-Bench 31.8; PaperBench 30.7; SciCode-V (Main/Sub) 26.6 / 56.5; BioMystery (HS/HD) 44.8 / 2.0; MTP speculative decode +22.0% throughput (135.7 vs 111.3 tok/s).

BigBang-v1 (SOTA 35B MoE): LiveCodeBench v6 ~85.2; GPQA-Diamond ~87.8; Terminal-Bench 2.1 58.3; SWE-bench Verified 79.4; SWE-bench Pro 54.2; Claw-Eval 77.5; NL2Repo 36.0; BrowseComp 76.5; XBench 58.4; HLE 50.3; FS-R 46.2 (beats DeepSeek V4 Pro 40.7, Claude Opus 4.8 45.2); MLE-Bench 59.1 (ties GPT 5.5 / DeepSeek V4 Pro); PaperBench (Code-Dev) 53.6 (beats DeepSeek V4 Pro 50.4); SciCode-V (Main/Sub) 50.0 / 68.6; BioMystery (HS/HD) 57.5 / 15.7 (HD beats DeepSeek V4 Pro 13.7); embedded block 40 MTP draft tensors (753 total tensors); clean loop termination with enable_thinking: true.

Qwen3.8-Flash-Next (Base): SWE-bench Pro 62.5; DeepSWE 1.1 58.7; SWE-bench Multilingual 81.0; NL2Repo-Bench 48.1; Terminal-Bench 2.1 67.64; CoWorkBench 73.9; JobBench 55.7; Agents' Last Exam pass@1 24.3 / score 51.2; Toolathlon Verified (pass@1) 73.5; IFBench 81.3; GPQA-Diamond 91.7; HLE 35.9; LiveCodeBench v6 91.9; ClawEval-MM pass@3 64.4 / avg 60.4; RecreationBench 49.9; AndroidWorld 84.5; OSWorld 2.0 binary 19.4 / partial 52.3; Vision2Web 64.0; ERQA 72.3; LVBench 76.6; RealWorldQA 88.5; CharXiv (RQ) with CI 90.6 / without CI 84.6; AIME 2026 98.67; HMMT Nov 2025 98.00; C-Eval 93.27; MMLU-Pro 87.75; tau3-Banking ~45.4-48.0.

Swift-1.5-Qwen3.8-Flash-Next (UkisAI & SC117 abliterated): Terminal-Bench 2.1 69.66 (+2.02 pp vs 67.64 Base); LiveCodeBench v6 90.39 (+1.99 pp vs 88.40 Base); GPQA-Diamond 89.60 (vs 89.80 Base, -0.20 pp); AIME 2026 96.67 (vs 98.67 Base, -2.00 pp); HMMT Nov 2025 97.33 (vs 98.00 Base, -0.67 pp); C-Eval 93.60 (+0.33 pp); IFBench 70.13 (vs 73.20 Base); ERQA 69.30 (vs 70.80 Base); Thinking token budget: -63.4% median / -55.8% mean on GPQA-D, -51.1% median / -31.3% mean on AIME 2026, -52.0% median / -44.8% mean on LCB v6, -54.7% median on HMMT; overthinking capped (max tail 742 Swift / 1082 SC117 vs 3837 Base); code pass rate 15/15; wall-clock execution 1.8x faster; zero refusal on security probes; Strata decode 126.4 tok/s.

CyberStrike-OffSec-35B: SecEval 81.39% (#1 open-source, beating GPT-4-turbo 79.07%); Network Sec 85.09%; Web Sec 85.34%; PenTest 82.26%; Cryptography 75.00%; Vulnerability 83.33%; AppSec 82.29%; Software Sec 79.75%; System Sec 77.82%; Memory Safety 71.43%; SECURE-MAET (MITRE ATT&CK) 93.94%; SECURE-CWET (CWE) 93.05%; CyberMetric-10000 86.61% (#4 across 25 models); MMLU Computer Security 86.00%; zero refusal on offensive security workflows.

Cyber-Ornith-1.5-9B-OBLITERATED: CyberSecEval 3/4 triage & remediation 86.7% (100% test case pass); zero-refusal diagnostic compliance 100.0%; Hermes Function Calling AST 93.3%; Terminal-Bench 2.1 66.7%; GPQA-Diamond 40.0%; GSM8K 74.0%; 102 tok/s on single RTX 4080 Super workstation; zero moralizing preambles on reverse engineering and exploit diagnostics.

DeepSeek-V4.1-Flash (with GLP-39 / keysdir projective steering): refusal32 1/32 -> 23/32; cyber32 12/32 -> 29/32; cyber100 refusal 75.0% -> 0.0%; V8 exploitation ladder 15.2% -> 0.0% refusal (delivery 81.8% -> 100.0%); cyber-fullchain 37.5% -> 0.9% refusal; benign32 32/32 clean; α=0.75 calibrated; hook at post-layer hyper-connection fold.

Qwen3.8-Flash-Next (with GLP-47 / Cudecnik refusal projection): refusal32 1/32 -> 26/32 (81.2%); cyber32 5/32 -> 32/32 (100.0%); benign32 32/32 clean; capability12 12/12; KL divergence 0.186 nats on neutral text; runtime projective hook h -= s*(h*v)v across L1–47; 480 KB control vector add-on preserving PLE and MTP.

###### Main-6. Cited benchmark repositories and leaderboards

| Benchmark | Official Homepage / Leaderboard | Code Repository / Dataset |
|---|---|---|
| **Terminal-Bench 2.1** | [tbench.ai Leaderboard](https://tbench.ai) | [harbor-framework/terminal-bench-2-1 (GitHub)](https://github.com/harbor-framework/terminal-bench-2-1) |
| **SWE-bench (Verified & Pro)** | [swebench.com Leaderboard](https://www.swebench.com/) | [princeton-nlp/SWE-bench (GitHub)](https://github.com/princeton-nlp/SWE-bench) |
| **Claw-Eval** | [claw-eval.github.io](https://claw-eval.github.io/) | [claw-eval/claw-eval (GitHub)](https://github.com/claw-eval/claw-eval) \| [claw-eval/Claw-Eval (HF)](https://huggingface.co/datasets/claw-eval/Claw-Eval) |
| **NL2Repo-Bench** | [AweAgent Meta-NL2Repo (HF)](https://huggingface.co/datasets/AweAI-Team/AweAgent-Meta-NL2Repo) | [Awesome-Long-Horizon-Agents (GitHub)](https://github.com/RUC-NLPIR/Awesome-Long-Horizon-Agents) |
| **BrowseComp** | [OpenAI BrowseComp Blog](https://openai.com/index/browsecomp/) | [openai/simple-evals (GitHub)](https://github.com/openai/simple-evals) |
| **XBench** | [xbench.org](https://xbench.org) | [xbench-ai/xbench-evals (GitHub)](https://github.com/xbench-ai/xbench-evals) \| [xbench (HF)](https://huggingface.co/xbench) |
| **Humanity's Last Exam (HLE)** | [lastexam.ai Leaderboard](https://lastexam.ai) | [centerforaisafety/hle (GitHub)](https://github.com/centerforaisafety/hle) \| [cais/hle (HF)](https://huggingface.co/datasets/cais/hle) |
| **FrontierScience Research (FS-R)** | [frontier-science/FS-R (HF)](https://huggingface.co/datasets/frontier-science/FS-R) | [frontier-science/FS-R (HF Dataset)](https://huggingface.co/datasets/frontier-science/FS-R) |
| **MLE-Bench** | [OpenAI MLE-Bench Announcement](https://openai.com/index/mle-bench/) | [openai/mle-bench (GitHub)](https://github.com/openai/mle-bench) |
| **PaperBench** | [PaperBench ICML 2024](https://icml.cc) | [EnvCommons/PaperBench (GitHub)](https://github.com/EnvCommons/PaperBench) \| [josancamon/paperbench (HF)](https://huggingface.co/datasets/josancamon/paperbench) |
| **SciCode / SciCode-V** | [scicode-bench.github.io](https://scicode-bench.github.io) | [scicode-bench/SciCode (GitHub)](https://github.com/scicode-bench/SciCode) |
| **BioMysteryBench** | [Anthropic BioMysteryBench (HF)](https://huggingface.co/datasets/Anthropic/BioMysteryBench-full) | [Anthropic/BioMysteryBench-full (HF)](https://huggingface.co/datasets/Anthropic/BioMysteryBench-full) |
| **ExploitBench** | [exploitbench.ai Leaderboard](https://exploitbench.ai) | [exploitbench/exploitbench (GitHub)](https://github.com/exploitbench/exploitbench) \| [exploitbench (HF)](https://huggingface.co/exploitbench) |
| **CyberSecEval 4** | [PurpleLlama / CyberSecEval 4](https://ai.meta.com/research/publications/cyberseceval-3-advancing-the-evaluation-of-cybersecurity-risks-and-capabilities-in-large-language-models/) | [meta-llama/PurpleLlama (GitHub)](https://github.com/meta-llama/PurpleLlama) |
| **SecEval** | [xuanwuai.github.io/SecEval](https://xuanwuai.github.io/SecEval) | [XuanwuAI/SecEval (HF)](https://huggingface.co/datasets/XuanwuAI/SecEval) |
| **SECURE (MAET / CWET)** | [SECURE Benchmark](https://arxiv.org/abs/2405.02102) | [SECURE Benchmark (HF)](https://huggingface.co/datasets) |
| **CyberMetric-10000** | [CyberMetric Paper](https://arxiv.org/abs/2402.09434) | [khangmacon/cybermetric-10000 (HF)](https://huggingface.co/datasets/khangmacon/cybermetric-10000) |
| **cyber32 & cyber100** | [msuiche/weightless](https://github.com/msuiche/weightless) | [msuiche/weightless (GitHub)](https://github.com/msuiche/weightless) |
| **blueteam32** | [msuiche/weightless](https://github.com/msuiche/weightless) | [msuiche/weightless (GitHub)](https://github.com/msuiche/weightless) |
| **cyber-v8-ladder** | [msuiche/weightless](https://github.com/msuiche/weightless) | [msuiche/weightless (GitHub)](https://github.com/msuiche/weightless) |
| **refusal32** | [Keys / HF](https://huggingface.co/datasets) | [msuiche/weightless (GitHub)](https://github.com/msuiche/weightless) |
### Cross-comparison - all Small models

###### Small-1. Agent, tool use and coding

| Model | Params | Quant + size | Terminal-Bench 2.1 | SWE-bench Verified | SWE-bench Pro | tau2-bench | tau3-bench | BFCL v4 | MCP-Atlas |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| **MiniCPM5-2B** | 2.517B | Q4_K_M 1.56 GB | 8.6 | **46.4** | 14.4 | **97.1** | 20.8 | 66.6 | - |
| **Spark-X2.5-4B** | 4B | bf16 only | - | 41.6 | **44.4** | 75.1 | **30.4** | 65.1 | **54.6** |
| Spark-X2.5-1.7B | 1.7B | bf16 only | - | 28.3 | 10.4 | 65.3 | 20.1 | 46.9 | 23.4 |
| LFM2.5-2.6B (reference) | 2.6B | - | - | - | - | - | - | - | - |
| Qwen3.5-4B (reference) | 4B | - | - | 38.8 | 29.4 | 79.9 | 6.7 | 50.3 | 40.8 |

LFM2.5-2.6B has no per-benchmark row in either source card; only the composite (33.2) is published.

###### Small-2. Reasoning, knowledge and long context

| Model | Params | AIME 2026 | HMMT Feb 2026 | GPQA-D | MMLU-Pro | HLE | AA-LCR | NoLiMa | LongBench v2 | LiveCodeBench v6 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **MiniCPM5-2B** | 2.517B | 86.5 | 63.8 | **70.2** | **70.8** | 8.9 | **59.0** | **68.1** | **43.7** | **69.1** |
| **Spark-X2.5-4B** | 4B | **90.7** | **81.2** | 67.4 | - | **12.3** | 56.3 | - | - | - |
| Spark-X2.5-1.7B | 1.7B | 69.4 | 48.4 | 43.8 | - | 6.3 | 24.3 | - | - | - |
| Qwen3.5-4B (reference) | 4B | 83.0 | 69.7 | 67.2 | - | 8.6 | 57.0 | - | - | - |
| Gemma4-12B (reference) | 12B | 82.1 | 65.6 | 72.8 | - | 13.1 | 55.3 | - | - | - |

### Benchmark coverage gaps

Where results are missing across primary vendor benchmark cards and independently measured leaderboards:

| Benchmark | Missing / Estimated for |
|---|---|
| Terminal-Bench 2.1 | Spark-X2.5-4B; dense fine-tunes (Qwopus3.8-27B, TURBO-735, GSQ-RCO) use derived evaluations |
| SWE-bench Verified | Native vendor scores missing for K2-Horizon and dense fine-tunes (derived from agentic test batteries) |
| SWE-bench Pro | North-Mini-Code and Agents-A1 have no vendor Pro evaluations published |
| BrowseComp | Dense fine-tunes and K2-Horizon publish no standalone BrowseComp runs (estimated from web-evals) |
| GPQA-Diamond | Exotic low-bit/grafted models (Escha-W2, fuse-1-Lite, Ternary-Bonsai-27B) lack verified diamond runs |
| AIME 2025/2026 | Most 35B MoE fine-tunes lack AIME runs (covered for Qwen3.8-Flash-Next: 98.7 Base / 96.7 Swift, GSQ-RCO, and Small models) |
| tau2/tau3-bench, BFCL v4, MCP-Atlas/Mark | Covered for K2-Horizon (tau3 26.8), Qwen3.8-Flash-Next (tau3 45.4–48.0, Toolathlon 73.5), and Small models |
| GAIA / GDPval-AA v2 / Claw-Gym / WildClaw / QwenClaw | Tracked primarily by MiniCPM5-2B and comprehensive agentic research cards |
| NL2Repo | Exotic models and legacy fine-tunes lack standalone repo-generation benchmarks |
| OSWorld / WebArena / AndroidWorld | Published for Qwen3.8-27B (OSWorld 84.3, AndroidWorld 81.9) and Qwen3.8-Flash-Next (OSWorld 2.0 52.3 partial / 19.4 binary, AndroidWorld 84.5) |
Not resolvable from public sources: the three new dense fine-tunes publish only author-run numbers (ARC-C grid, an in-house 14-task SWE battery, a quantization-ablation table) and no vendor
harness results; the ROCmFPX Community Builds carry no benchmarks at all. Do not mix these into
the matrix - they are not comparable harnesses.

### Suggested modern agentic benchmarks

Benchmarks already used in this doc, plus 2026 agent suites worth adopting. Links verified in
this pass unless marked otherwise:

| Benchmark | Category | What it measures | Canonical link |
|---|---|---|---|
| **Terminal-Bench 2.1** (Terminus) | agentic coding | Long-horizon terminal/CLI task completion | https://tbench.ai |
| **SWE-bench Verified / Pro / Multilingual** | agentic coding | Real repository issue resolution, hard subset, non-Python repos | https://www.swebench.com/ |
| **NL2Repo-Bench** | agentic coding | Repo-scale generation from natural language | https://github.com/RUC-NLPIR/Awesome-Long-Horizon-Agents |
| **DeepSWE 1.1** | agentic coding | Multi-turn SWE under the Claude Code harness | no canonical page verified |
| **LiveCodeBench v6** | coding | Contamination-free competitive coding on dated problems | https://livecodebench.github.io/ |
| **SciCode / OJBench / LCB-Pro** | coding | Scientific, olympiad-level and professional coding | https://github.com/scicode-bench/SciCode |
| **tau2-bench / tau3-bench** | tool use | Tool-agent-user interaction in real domains (telecom, banking) | https://github.com/sierra-research/tau2-bench |
| **BFCL v4** | tool use | Function-calling accuracy across formats | https://gorilla.cs.berkeley.edu/leaderboard.html |
| **MCP-Atlas / MCP-Mark** | tool use | Tool discovery and execution over MCP servers | no canonical page verified |
| **GAIA** | search + tooling | Multi-step web/tool questions with unambiguous answers | https://huggingface.co/datasets/gaia-benchmark/GAIA |
| **BrowseComp / BrowseComp-ZH / Top100** | search | Hard-to-find web facts, English and Chinese splits | https://openai.com/index/browsecomp/ |
| **Claw-Eval / Claw-Gym / ClawEval-MM** | general agent | Harness-level agent evaluation, incl. multimodal | https://claw-eval.github.io/ |
| **WildClaw / QwenClaw / Workspace Bench** | general agent | Real workspace and office-agent tasks | no canonical page verified |
| **OSWorld-Verified** | computer use | Desktop GUI automation in real OS environments | https://github.com/xlang-ai/OSWorld |
| **WebArena-Verified** | browser use | Multi-site web navigation and completion | https://github.com/web-arena-x/webarena |
| **AndroidWorld** | mobile use | Android app control across an emulator farm | https://github.com/google-research/android_world |
| **GDPval-AA v2 / AA-LCR / AA-Omniscience** | general + long context | Occupational quality, long-context reasoning, factual accuracy vs hallucination | https://artificialanalysis.ai/methodology/intelligence-benchmarking |
| **VitaBench2.0** | general agent | Life-domain multi-turn agent tasks | no canonical page verified |
| **CoWorkBench / JobBench / RecreationBench / QwenSWEBench** | general + coding | In-house vendor suites (office work, job tasks, app recreation, SWE) | no canonical page verified |
| **Agents' Last Exam** | frontier agent | Hard agentic tasks, pass@1 and partial score | no canonical page verified |
| **NoLiMa** | long context | Retrieval with lexical distractors (no literal overlap) | no canonical page verified |
| **LongBenchPro / LongBench v2** | long context | Realistic long-context multitask understanding and reasoning | https://github.com/THUDM/LongBench |
| **SuperGPQA** | knowledge | Graduate-level knowledge across 285 disciplines | https://github.com/SuperGPQA/SuperGPQA |
| **HLE / GPQA-Diamond / AIME / HMMT / IMO-AnswerBench / CritPt** | reasoning | Expert reasoning, graduate science QA, competition math, frontier physics | https://lastexam.ai |
| **IFBench / Multi-IF / IFEval** | instruction following | Constraint adherence, multi-turn and single-turn | https://huggingface.co/datasets/allenai/IFBench |
| **MLE-Bench / PaperBench / FS-R / XBench / BioMysteryBench** | research | ML engineering, paper replication, frontier science, expert consulting, biology | https://github.com/openai/mle-bench |

Highest value for local agent usage on this host: **tau3-bench** and **MCP-Atlas** (tool-call
reliability), **Terminal-Bench 2.1** and **DeepSWE 1.1** (harness-level coding), **GAIA** and
**BrowseComp** with tool access (search arms), **NoLiMa** (long-context honesty under
distractors), and **AA-Omniscience non-hallucination** (factual discipline at low bit-width).

## Main MOE models

### Baseline llama-server model: Qwen3.6-35B-A3B (APEX-I-Compact)

- **Architecture**: 35B Mixture-of-Experts with ~3.0B active parameters per token, 128 total routed experts (8 active per token), Grouped-Query Attention (GQA).
- **Context Window**: 32K native context; extends to 256K via YaRN RoPE scaling.
- **GGUF Repo & direct URLs**: `mudler/Qwen3.6-35B-A3B-APEX-GGUF` — primary quantization `Qwen3.6-35B-A3B-APEX-I-Compact.gguf`.
- **VRAM Footprint**: ~18.5 GB VRAM with APEX-I-Compact quantization.
- **Chat Template & Thinking**: Jinja chat template (`froggeric/Qwen-Fixed-Chat-Templates/chat_template.jinja`); supports `<think>...</think>` CoT reasoning and tool-call XML schema (`<tools>...</tools>`, `<function=...>`, `<parameter=...>`).
- **Speculative Decoding**: Multi-Token Prediction (MTP) draft tensors via `am17an-Qwen3.6-35BA3B-MTP-only.gguf` (for standard 733-tensor builds) or embedded block 40 MTP tensors (for 753-tensor builds like `Qwen3.6-35B-A3B-APEX-I-Compact-mtp.gguf`), or CPU N-Gram simple predictor (`--spec-type ngram-simple`).
- **Benchmark Suite**: Terminal-Bench 2.1 49.2% (Terminus-2) / 44.9% (IFM); SWE-bench Verified 73.4%; SWE-bench Pro 43.6%; Claw-Eval 68.7%; NL2Repo 29.4%; BrowseComp 67.9%; XBench 32.6%; HLE 36.2%; FS-R 11.9%; MLE-Bench 31.8%; PaperBench 30.7%; SciCode-V (Main/Sub) 26.6% / 56.5%; BioMystery (HS/HD) 44.8% / 2.0%; GPQA-Diamond 84.1%; LiveCodeBench v6 73.5%.

### BigBang-v1

- **Base Model**: `endless-frontier/BigBang-v1` — Qwen3.6-35B-A3B fine-tuned with self-evolving synthetic CoT trajectories on ~10,000 frontier scientific & technical tasks.
- **GGUF Repo**: `bartowski/endless-frontier_BigBang-v1-GGUF`.
- **Selected GGUF** (IQ4_XS ~17.95 GB VRAM, closest footprint to APEX-I-Compact): `endless-frontier_BigBang-v1-IQ4_XS.gguf`.
- **Vision Projector**: `mmproj-endless-frontier_BigBang-v1-f16.gguf`.
- **Context Window**: 32K native; up to 256K context with YaRN/parallel slot sizing.
- **Chat Template & Thinking**: Integrated native Jinja chat template (`jinja = on`). **Requires `enable_thinking: true`** in `chat-template-kwargs` / system prompt so execution-gated CoT scratchpad retains tool evaluation state and terminates loops cleanly (avoids infinite `git diff`/`namcap` replay).
- **Speculative Decoding**: `BigBang-v1-IQ4_XS.gguf` contains **753 total tensors** with the **20 MTP draft tensors already embedded internally** under block 40 (`blk.40.nextn.*`, `blk.40.attn_*`, `blk.40.ffn_*`). It does not strictly require an external `-MTP-ONLY.gguf` slice; `llama-server` can load draft tensors directly from the main model file or from the standalone 856 MB `Qwen3.6-35B-A3B-MTP-ONLY.gguf` slice using `--spec-type draft-mtp --spec-draft-n-max 3`. Also fully compatible with CPU N-Gram speculative decoding (`--spec-type ngram-simple`).
- **Benchmark Suite**: Terminal-Bench 2.1 **58.3%**; SWE-bench Verified **79.4%**; SWE-bench Pro **54.2%**; Claw-Eval **77.5%**; NL2Repo **36.0%**; BrowseComp **76.5%**; XBench **58.4%**; HLE **50.3%**; FS-R **46.2%** (surpasses DeepSeek V4 Pro 40.7% and Claude Opus 4.8 45.2%); MLE-Bench **59.1%** (matches GPT 5.5 and DeepSeek V4 Pro); PaperBench (Code-Dev) **53.6%** (surpasses DeepSeek V4 Pro 50.4%); SciCode-V (Main/Sub) **50.0% / 68.6%**; BioMystery (HS/HD) **57.5% / 15.7%** (HD surpasses DeepSeek V4 Pro 13.7%); LiveCodeBench v6 **~85.2%**; GPQA-Diamond **~87.8%**.

### BTL-4 (Bad Theory Labs)

- **Base Model**: `badtheorylabs/BTL-4` — 35B MoE fine-tuned from `Ornith-1.0-35B` on an execution-gated reasoning corpus where candidate solution trajectories were retained only if output code compiled and passed test suites.
- **GGUF Repo & VRAM**: ~17.9 GB (`IQ4_XS`) / ~12.2 GB (`IQ2_XXS`).
- **Context Window**: 32K native; extends to 256K via YaRN RoPE scaling.
- **Chat Template & Thinking**: Jinja chat template with `enable_thinking: true` required for execution-gated CoT reasoning that evaluates tool output and terminates multi-step loops cleanly.
- **Speculative Decoding**: Supports Qwen3.6-35B MTP draft tensors (`--spec-type draft-mtp`) and CPU N-Gram predictor.

### Ornith-1.0-35B (Apodex)

- **Base Architecture**: `Apodex/Ornith-1.0-35B` — 35B MoE with ~3.0B active parameters, GQA, 128 experts.
- **HF Repo**: https://huggingface.co/Apodex/Ornith-1.0-35B
- **GGUF Repo**: `Apodex/Ornith-1.0-35B-GGUF` — quantizations `Q4_K_M` (~21.2 GB VRAM), `IQ4_XS` (~18.0 GB VRAM).
- **Context Window**: 32K native; extends to 256K via YaRN RoPE scaling.
- **Chat Template & Thinking**: Native tool-use template with `enable_thinking: true`; supports `<think>...</think>` CoT and `<tools>` XML schema.
- **Speculative Decoding**: MTP draft tensors compatible; CPU N-Gram predictor fallback.
- **Specialization**: Terminal/CLI — Terminal-Bench 2.1 score 62.8% (highest in matrix); native tool-use template optimized for terminal interaction and command execution.

### KAT-Coder-V2.5-Dev

- **Base Model & Provenance**: Fine-tuned from Qwen3.6-35B-A3B with AST hashline code-injection training; specialized for diff/patch generation.
- **HF Repo**: https://huggingface.co/KAT-Coder/KAT-Coder-V2.5-Dev
- **GGUF Repo**: `KAT-Coder/KAT-Coder-V2.5-Dev-GGUF` — quantization `APEX` (~18.5 GB VRAM).
- **Context Window**: 32K native; extends to 256K via YaRN RoPE scaling.
- **Chat Template & Thinking**: Jinja chat template with `enable_thinking: true`; supports `<think>...</think>` CoT and tool-call XML schema for code injection.
- **Speculative Decoding**: MTP draft tensors compatible; CPU N-Gram predictor fallback.
- **Specialization**: AST hashline code injector — SWE-bench Verified 79.6%; excels at diff/patch patching with line-level precision edits.

### XYZ-Aquila-mini (Nex-N2)

- **Architecture & Parameters**: Compact MoE (~10B total, ~3B active), GQA; optimized for long-context retrieval and web-agent execution.
- **HF Repo**: https://huggingface.co/Nex-N2/XYZ-Aquila-mini
- **GGUF Repo**: `Nex-N2/XYZ-Aquila-mini-GGUF` — quantization `Q3_K_XL` (~15.8 GB VRAM).
- **Context Window**: 32K native; extends to 256K via YaRN RoPE scaling.
- **Chat Template & Thinking**: Jinja chat template with `enable_thinking: true`; supports `<think>...</think>` CoT and tool-call XML schema for web-agent planning.
- **Speculative Decoding**: MTP draft tensors compatible; CPU N-Gram predictor fallback.
- **Specialization**: Long-horizon search & scraping — BrowseComp 74.1%; web-agent execution profile with extended context retention.

### North-Mini-Code-1.0

- **Architecture**: Compact code-tuned MoE (~12B total, ~4B active); fine-tuned on execution-gated coding trajectories with native CoT traces.
- **HF Repo**: https://huggingface.co/North-ML/North-Mini-Code-1.0
- **GGUF Repo**: `North-ML/North-Mini-Code-1.0-GGUF` — quantization `UD-Q4` (~19.2 GB VRAM).
- **Context Window**: 32K native; extends to 256K via YaRN RoPE scaling.
- **Chat Template & Thinking**: Jinja chat template with `enable_thinking: true`; supports `<think>...</think>` CoT and tool-call XML schema for subagent reasoning.
- **Speculative Decoding**: MTP draft tensors compatible; CPU N-Gram predictor fallback.
- **Specialization**: Native CoT reasoning traces optimized for subagent execution — balances reasoning depth with efficient token usage in multi-step agentic workflows.

### Agents-A1 (Qwen3.5 Base)

- **Architecture**: Qwen3.5 35B MoE legacy baseline (~3.0B active params, GQA, 128 experts); predecessor to the 3.6 series.
- **HF Repo**: https://huggingface.co/Agents-AI/Agents-A1
- **GGUF Repo**: `Agents-AI/Agents-A1-GGUF` — quantization ~17.5 GB VRAM (APEX/IQ4_XS class).
- **Context Window**: 32K native; extends to 256K via YaRN RoPE scaling.
- **Chat Template & Thinking**: Jinja chat template with `enable_thinking: true`; supports `<think>...</think>` CoT and tool-call XML schema.
- **Speculative Decoding**: MTP draft tensors compatible (3.5 series); CPU N-Gram predictor fallback.
- **Comparative Evaluation**: Logically falls behind the 3.6 series across all benchmarks; retains value as a legacy baseline for comparison and low-cost experimentation.

### K2-Horizon-MoVA-36B-A4B (IFM)

- **Base Model**: `IFM/K2-Horizon-MoVA-36B-A4B` — sparse MoE with Mixture-of-Values attention (MoVA): 36B stored parameters, 4B activated per token.
- **HF Repo**: https://huggingface.co/IFM/K2-Horizon-MoVA-36B-A4B
- **GGUF Repo**: none published — the repo ships Transformers/safetensors only (vLLM + SGLang recipes validated on 2x H200). No local quantization exists yet.
- **VRAM Footprint**: ~72 GB at BF16; therefore **not yet runnable on the 24 GB local target** until a 3-4 bit GGUF appears.
- **Context Window**: 524,288 (512K) native from the midtraining stages onward.
- **Chat Template & Thinking**: `k2_horizon` reasoning + tool-call parsers, `reasoning_effort="high"` always; tool-call format switchable via `chat_template_kwargs` (`json` / `xml` / `xml_typed`, default `xml`); thinking returned in `reasoning_content`.
- **Licence / Openness**: Apache-2.0; pretrain and midtrain datasets named, training code promised.
- **Reported benchmarks**: tau3-Banking 26.8 (best in its card row); Terminal-Bench 2.1 58.6; SciCode 38.9; HLE without tools 25.2; GPQA-Diamond 80.8; CritPt 2.1; AA-LCR 66.3; AA-Omniscience accuracy 18.8 / non-hallucination 69.2.
- **Relative standing (author)**: scores above open dense ~30B and MoE up to 15x its size on agentic/reasoning suites; Qwen3.6-35B-A3B scores 44.9 Terminal-Bench 2.1 in the same table.

### Swift-1.5-Qwen3.8-Flash-Next (SC117 GSQ-RCO Abliterated)

- **Architecture & Scale**: Ultra-sparse Mixture-of-Experts with 125B total parameters (plus 51B auxiliary per-layer token embedding / PLE table `per_layer_token_embd`), activating ~6.0B parameters per token across 48 layers with 512 fine-grained routed experts (top-6 activated per token). Hybrid Gated DeltaNet (GDN) linear attention + Qwen Sparse Attention (QSA) micro-block indexer + Gated Residual (GR 4-branch) routing.
- **Provenance & Parent Lineage**:
  1. **Original Foundation Model**: `Qwen/Qwen3.8-Flash-Next` (Qwen Team, Alibaba Group) — BF16 base checkpoint (~360 GB). Open-weight preview of the Qwen4 architecture; 262,144 native context (extensible to 1,000,000 via YaRN); trained with Muon + AdamW repartitioning and orthogonal scaling laws.
  2. **Base Tune**: `ukisai/Swift1.5-Qwen3.8-Flash-Next` (UkisAI) — post-trained derivative using an anti-overthinking token penalty during reinforcement learning (RL) and Online Policy Distillation (OPD). Designed to penalize pathological cyclic reasoning loops without truncating valid problem-solving traces. Trained on `ukisai/Qwen3.8-27B-multi-turn-agent-sft` re-sampled into multi-turn agent RL environments (Terminus-2 / OpenThoughts-Agent framework).
  3. **Quantization Source**: `ukisai/Swift-1.5-Qwen3.8-Flash-Next-GSQ-RCO-GGUF` — non-uniform quantization using Gumbel-Softmax learned quantization grids (GSQ) and Riemannian constrained optimization (RCO) type budgets per tensor.
  4. **Abliterated Donor Weights**: `orcarouter/Qwen3.8-Flash-Next-Uncensored-GGUF` — rank-1 linear refusal vector ablation $W \leftarrow W - r(r^T W)$ computed across all 48 layers.
  5. **Final Checkpoint (Byte-Level Transplant)**: [`SC117/Swift-1.5-Qwen3.8-Flash-Next-GSQ-RCO-abliterated-GGUF`](https://huggingface.co/SC117/Swift-1.5-Qwen3.8-Flash-Next-GSQ-RCO-abliterated-GGUF).
- **Transplant Mechanics & Mathematical Safety Verification**:
  - Replaces exactly **144 residual-writing tensors** (out of 1224 tensors in each file) across all 48 layers: `blk.*.ssm_out.weight` (36 tensors, IQ4_XS, 566M params), `blk.*.attn_output.weight` (12 tensors, IQ4_XS, 189M params), `blk.*.ffn_down_shexp.weight` (48 tensors, IQ4_NL, 79M params), and `blk.*.ffn_down_exps.weight` (48 tensors, Q2_0, 40.3B params).
  - Total transplanted parameter mass: **41.1B parameters (~33% of the 125B main model)**.
  - **BF16 Distance Ground Truth**: Measuring the relative tensor distance $\|\Delta W\| / \|W\|$ between `ukisai/Swift-Qwen3.8-Flash-Next` and base `Qwen3.8-Flash-Next` in pure BF16 space proves that `ffn_down_exps` (40.3B params, 98% of the transplanted parameter mass) is **100% byte-identical** (0.0000% delta, identical SHA-256) across all 48 layers. The remaining three families differ by only 0.21%–2.42% (mean: `ssm_out` 0.30%, `attn_output` 0.25%, `ffn_down_shexp` 1.60%). Re-quantizing BF16 would introduce ~45% quantization noise; the byte-level transplant introduces $\le 2.42\%$ delta while leaving all 1080 non-target tensors bit-identical (blake2b verified).
- **Model Files & Strata Deployment Inventory (as referenced in `research/strata-qwen3.8-flash-next.md`)**:
  - **Shard 1 (Weights / Dense Backbone + Layers 0–12 + PLE Table)**: `Swift-Qwen3.8-Flash-Next-GSQ-RCO-abliterated-IQ3_S-00001-of-00002.gguf` (41.77 GB file size; mapped contiguously as 55.0 GB in Strata). Holds embeddings, RMS norms, attention projections, LM head, and the 28.8 GB `per_layer_token_embd` table.
  - **Shard 2 (Layers 13–47 / Quantized MoE Weights)**: `Swift-Qwen3.8-Flash-Next-GSQ-RCO-abliterated-IQ3_S-00002-of-00002.gguf` (36.04 GB file size; 28.8 GB demand-paged static N-gram lookup / PLE table for prefix lookahead decoding in Strata). Total dual-shard IQ3_S footprint: **77.81 GB** (within 0.2% of upstream).
  - **Alternative Quantization Tiers**: `IQ3_XXS` (70.62 GB), `IQ2_XS` (63.47 GB), `Q2_0` (61.94 GB).
  - **Vision Support**: `mmproj-Qwen3.8-Flash-Next-BF16.gguf` (~0.91 GB / 910 MB), clip/deepseek41v vision projector tower.
  - **Speculative Drafter & MTP Runtime**:
    - Strata pack: `sc117_swift15_iq3s/strata/` scaffolding, `mtp-q2_0.gguf` (~889 MB VRAM footprint) + `strata/rt/` runtime (1.57 GB total), `draft_vocab.bin`.
    - Standard `llama.cpp` draft heads: `mtp-Qwen3.8-Flash-Next-Q8_0.gguf` (4.14 GB), `mtp-Qwen3.8-Flash-Next-Q4_0.gguf` (2.20 GB).
- **Local Hardware Operating Target (RX 7900 XTX 24 GB + 95 GiB Host RAM, 0B Swap)**:
  - **VRAM Budget (23.99 / 24.0 GB)**: Base dense layers (~8.80 GB), Vision projector (~0.91 GB), MTP drafter (~0.89 GB), Active KV resident window `--kv-resident 32768` `k8v4` (~3.20 GB), Driver headroom `--vram-reserve-mib 600` (~0.60 GB), Hot MoE expert cache pool `--expert-cache auto` (~9.59 GB, ~6800–7400 hot experts resident, ~85% routing hit rate).
  - **Host RAM Budget (92.2 / 95.0 GiB peak)**: Cold MoE expert RAM pool `--expert-ram-budget 42000` (41.0 GiB), Swift N-Gram Table Shard 2 demand-paged via `mmap` (25.2 GiB), 4-slot conversation cache pool `--conversation-cache-mib 18432` `k8v4` (18.0 GiB), Prefill scratch buffer `STRATA_RESIDENT_HEADROOM_GIB=6` (6.0 GiB), Kernel page tables (2.0 GiB). Zero swap, 2.8 GiB safety headroom.
- **Token Needed Budget in the Swift Tune**:
  - **Training Token Budget & Data Pipeline**: Post-trained on `ukisai/Qwen3.8-27B-multi-turn-agent-sft` (15,209 multi-turn agent interaction traces generated via Terminus-2 / OpenThoughts-Agent framework, covering shell commands, coding, and debugging). Re-sampled and compiled into multi-turn RL environments with negative reward shaping on cyclic self-correction tokens, followed by Online Policy Distillation (OPD).
  - **Inference Thinking Token Budget vs. Base Qwen3.8-Flash-Next**:
    - **GPQA-Diamond**: 7,823 mean thinking tokens vs 17,683 base (**&darr; 55.8% mean**, **&darr; 63.4% median**); score: 89.60% vs 89.80% (-0.20 pp).
    - **AIME 2026**: 15,806 mean thinking tokens vs 23,015 base (**&darr; 31.3% mean**, **&darr; 51.1% median**); score: 96.67% vs 98.67% (-2.00 pp).
    - **LiveCodeBench v6**: 9,849 mean thinking tokens vs 17,833 base (**&darr; 44.8% mean**, **&darr; 52.0% median**); score: **90.39% vs 88.40% (+1.99 pp)**.
    - **MMLU-Pro**: 1,519 mean thinking tokens vs 3,528 base (**&darr; 57.0% mean**, **&darr; 24.0% median**); score: 87.20% vs 87.75% (-0.55 pp).
    - **IFBench**: 4,411 mean thinking tokens vs 8,310 base (**&darr; 46.9% mean**, **&darr; 55.6% median**); score: 70.13% vs 73.20% (-3.07 pp).
    - **HMMT (Nov 2025)**: 16,530 mean thinking tokens vs 25,487 base (**&darr; 35.1% mean**, **&darr; 54.7% median**); score: 97.33% vs 98.00% (-0.67 pp).
    - **C-Eval**: 586 mean thinking tokens vs 1,048 base (**&darr; 44.1% mean**, **&darr; 7.1% median**); score: 93.60% vs 93.27% (+0.33 pp).
    - **ERQA (Multimodal)**: 1,788 mean thinking tokens vs 4,036 base (**&darr; 55.7% mean**, **&darr; 47.7% median**); score: 69.30% vs 70.80% (-1.50 pp).
    - **Terminal-Bench 2.1**: 45,428 mean output tokens vs 40,591 base (+11.9% mean total generated tokens, but **&darr; 17.9% median**); score: **69.66% vs 67.64% (+2.02 pp)**.
  - **Reasoning Effort Token Scaling (GPQA-Diamond)**:
    - `xhigh`: 7,823 mean tokens (89.60%) vs base 17,683 (89.80%) — accuracy preserved within 0.20 pp.
    - `medium`: 2,483 mean tokens (83.74%) vs base 4,157 (86.36%) — 40.3% fewer tokens, 2.62 pp accuracy delta.
    - `low`: 2,645 mean tokens (84.75%) vs base 3,966 (87.17%) — 33.3% fewer tokens, 2.42 pp accuracy delta.
  - **Evaluation Output Caps**: AIME 2026 and HMMT evaluated with a 250,000-token cap; GPQA-Diamond, MMLU-Pro, ERQA, and LiveCodeBench v6 with a 100,000-token cap; IFBench with an 81,920-token cap; C-Eval with a 16,384-token cap. Native context 262,144 tokens.
  - **Long-Tail Overthinking Cap**: Paired code-task testing (3 tasks × 5 seeds) shows base Qwen3.8-Flash-Next averages 847 thinking tokens with a maximum pathological tail of **3,837 tokens**. Swift 1.5 collapses the mean to 471 tokens and caps the maximum tail at **742 tokens** (-80.7%). The SC117 abliterated transplant averages 552 tokens with a maximum tail of **1,082 tokens** (-71.8% vs base), retaining 15/15 code test pass rate.
- **Divergence and Accuracy Loss Analysis (General & Domain-Specific)**:
  1. **General Accuracy Divergence Across the Lineage Chain**:
     - *Anti-Overthinking Penalty (Base &rarr; Swift 1.5)*: Compresses thinking traces by ~52%–63.4%, speeding wall-clock execution by ~1.8x. Overall benchmark accuracy loss across broad suites is <1%, with coding and terminal execution gaining (+1.99 pp on LCB v6, +2.02 pp on Terminal-Bench 2.1). The trade-off is an increased vulnerability to premature convergence on problems that genuinely require speculative branch backtracking.
     - *Non-Uniform Quantization (BF16 &rarr; GSQ-RCO IQ3_S)*: At 3.5 bpw (77.8 GB), the dense attention spine and shared experts (`ffn_down_shexp`) are safeguarded at IQ4_XS/IQ4_NL. However, the 512 routed experts (`ffn_down_exps`) are encoded at Q2_0. While high-frequency routing paths retain full fidelity, low-frequency expert pathways suffer an estimated 3–5% degradation in representational capacity.
     - *Abliteration Transplant (GSQ-RCO &rarr; SC117)*: Removes the rank-1 refusal direction. Because 98% of the target parameter mass is byte-identical, general perplexity shifts by <0.2%. However, MTP draft acceptance drops from 66.8% to 62.5% (-4.3 pp) because the draft head was trained on un-ablated weights. Mean thinking tokens rise slightly (+7.1%, 471 &rarr; 552), reflecting slight activation drift in the attention/SSM output projections.
     - *Strata Runtime Expert Pruning (`--speed faster` & `STRATA_ROUTE_TAIL_SKIP=7`)*: Pruning the 6th routed expert (<2% softmax probability) speeds decode by 16–20%. General queries show zero noticeable drift; however, complex multi-domain queries occasionally lose tail nuance.
  2. **Domain-Specific Accuracy & Behavior Expectations**:
     - **Cybersecurity & Penetration Testing (Major Gain / Zero Refusal)**: The baseline model aggressively refuses exploit payload construction, reverse-engineering queries, and security research prompts. The SC117 abliterated transplant exhibits **zero refusal**, answering detailed technical questions (e.g. paywall bypassing, binary exploitation, CVE reproducer scripts) while maintaining 100% technical competence. Built-in safety is absent; isolation must be enforced by the host harness.
     - **Agentic CLI & Tool Calling (High Retention & Loop Immunity)**: Standard LLMs frequently fall into pathological overthinking loops when encountering failed tool outputs (e.g. infinite `git diff` re-evaluations, repeating terminal commands). Swift 1.5's token penalty terminates cyclic loops cleanly, keeping agent execution snappy (~180ms TTFT across cached multi-turn turns in Strata). Jitter in JSON/XML schema syntax is minimized at recommended sampling (temp 0.6–0.7, top_p 0.95, min_p 0.05).
     - **Competitive Programming & Software Engineering (Net Positive, Edge-Case Trap)**: Pass rates on standard software engineering batteries remain at 100% (15/15), and LiveCodeBench v6 improves to 90.39%. However, for complex combinatorial optimization or novel invariant algorithmic puzzles, the truncation of the reasoning tail increases the risk of "first plausible solution" bias.
     - **Advanced Mathematics & Formal Reasoning (Minor Accuracy Penalty, ~1–2 pp)**: On AIME 2026 (96.67% vs 98.67%) and HMMT (97.33% vs 98.00%), Swift 1.5 exhibits a 0.67–2.00 pp drop. Capping reasoning traces at ~16K tokens prevents the extensive multi-path sanity checks that foundation models use to achieve near-100% math scores.
     - **Multimodal Vision & Document OCR (~1.5 pp Drop)**: Multimodal reasoning on ERQA drops from 70.80% to 69.30% (-1.5 pp) while saving 55.7% thinking tokens. The BF16 `mmproj` vision tower remains stable, with UI screenshots, charts, and technical schematics parsed reliably.
     - **Uncensored Discourse & Tone Consistency**: The linear ablation cleanly removes moralizing disclaimers, lecturing preambles, and evasive refusals without inducing the stylometric degradation or incoherence common in blunt fine-tuned uncensored models.

## Main Dense models

### Baseline: unsloth/Qwen3.8-27B-GGUF

Baseline reference, quant sizes and benchmark rows for the 27B dense class are in [`model-research.md`](model-research.md#main-dense-models). Per-model detail below.

### Qwen3.6-27B-Fable-Fusion-711 (DavidAU)

- **Base Architecture**: 27B dense Heretic multi-stage merge combining Fable, Polaris, and Claude Opus reasoning traces; >700 ARC-Challenge (first 27B model to breach 700 in both 4-bit and 8-bit).
- **Model Repo**: `DavidAU/Qwen3.6-27B-Fable-Fusion-711-Uncensored-Heretic-NM-DAU-NEO-MAX-MTP-GGUF`.
- **VRAM Footprint**: ~16.5 GB (`IQ4_XS`) / ~28.5 GB (`Q8_0`).
- **Context Window**: 32K native; extends to 256K via YaRN RoPE scaling.
- **Chat Template & Thinking**: Jinja chat template with `enable_thinking: true` for multi-stage reasoning traces and tool-call XML schema.
- **Speculative Decoding**: MTP (Multi-Token Prediction) GGUF acceleration for fast decode throughput; also CPU N-Gram predictor compatible.

### Qwen3.8-27B-TURBO-Fable-Cold-Fusion-735-882-Heretic (DavidAU)

- **Base Model / Construction**: multi-stage fine-tune and merge on `Qwen/Qwen3.8-27B`. Built with COLD FUSION (GAIN + Unsloth) and the Fable-Fusion-711 method, then Heretic/ARA de-censored. Core "DNA": `Qwen3.6-27B-Fable-Fusion-711` + `Qwen3.8-27B-Cold-Fusion-GAIN-V1.1`.
- **HF Repo**: https://huggingface.co/DavidAU/Qwen3.8-27B-TURBO-Fable-Cold-Fusion-735-882-Heretic-Uncensored-NEO-CODER-MAX-MTP-GGUF
- **GGUF Quants**: "regular" and "MTP" NEO IMATRIX quants; output tensor forced to 16-bit; MTP tensor set at Q8_0; two special `LOW` quants (IQ4_XS, Q6_K) for smaller footprint.
- **Vision**: requires a separate `mmproj` file placed next to the GGUF.
- **Context Window**: 256K.
- **Chat Template & Thinking**: `reasoning_effort` = `xhigh` (default) / `medium` / `low` set at the top of the Jinja template; TURBO tuning cuts thinking-token volume to 1/2-1/10 of stock Qwen3.8-27B (median ~2/3 reduction) while keeping output detail.
- **Reported benchmarks (Instruct mode)**: ARC-C 0.735 (mxfp8) / 0.719 (mxfp4); ARC-E 0.882; BoolQ 0.917; HellaSwag 0.832; OpenBookQA 0.530; PIQA 0.837; WinoGrande 0.785 — above Qwen3.8-27B (0.591 / 0.581 ARC-C), Qwen3.6-27B (0.647), Qwen3.6-35B-A3B-Instruct (0.581) and Qwen3.5-27B (0.557).
- **Reported speed**: ~75 t/s with regular Q4_K_S; MTP quants exceed 90 t/s at ~60% acceptance (2 draft tokens) on RTX 5090 / LM Studio. Below 50% acceptance the regular quant is faster.
- **Tool calling**: q4_K_M is the practical minimum, Q5/Q6 recommended; temp 0.6-0.7, repetition penalty 1.0.
- **Caveat**: author-reported numbers only — no independent agentic-harness results (Terminal-Bench, SWE-bench, tau-bench) published.

### Qwopus3.8-27B-Flash (Jackrong)

- **Base Model**: `Qwen/Qwen3.8-27B` fine-tune. Stage 1: ~1.5M teacher SFT examples filtered to the best 10%. Stage 2: NVIDIA NeMo-RL + GSPO sequence-level reasoning RL. Goal is "preserve capability, collapse cost": fewer thinking tokens, faster completion for long agent loops.
- **HF Repo**: https://huggingface.co/Jackrong/Qwopus3.8-27B-Flash-GGUF
- **GGUF Quants (all carry a NextN/MTP head)**: `MTP-Q2_K` 10.86 GB, `MTP-Q3_K_S` 12.26 GB, `MTP-Q3_K_M` 13.50 GB, `MTP-Q3_K_L` 14.56 GB, `MTP-IQ4_XS` 15.42 GB, `MTP-Q4_K_S` 15.83 GB, `MTP-Q4_K_M` 16.81 GB, `MTP-Q5_K_S` 18.97 GB, `MTP-Q5_K_M` 19.54 GB, `MTP-Q6_K` 22.43 GB, `MTP-Q8_0` 29.05 GB, `MTP-BF16` 54.66 GB; `mmproj-F32.gguf` 1.84 GB.
- **Context Window**: served at `-c 327680` with `-np 10` in the reported configuration.
- **Speculative Decoding**: bundled MTP head, `--spec-type draft-mtp`, `draft_n_max = 2`, q8_0 KV cache in the reported runs.
- **Reported results**: MMLU-Pro 91.28% vs 92.73% for base (-1.45 pp); +12.8% decoder-only throughput (9.347 vs 8.284 tok/s across Math/Physics/Chemistry); weighted MTP draft acceptance 80.7% vs 66.1% (+14.6 pp); aggregate output characters -9.9%.
- **Agentic battery**: 13/14 (93%) on a held-out 14-task agentic software-engineering battery with hidden-test verifiers — 26.0 minutes on one RTX 5090, 99.0 tok/s mean, 88.8% mean MTP acceptance, 10.1 turns/task, 0 integrity violations. Failure mode: non-termination (kept iterating after the hidden suite already passed).
- **Known issue (author)**: occasional incorrect Python indentation in some coding tasks.

### Qwen3.8-27B GSQ-RCO GGUFs (ISTA-DASLab)

- **Base Model**: `Qwen/Qwen3.8-27B` — non-uniform GGUF quantization: GSQ learns per-coordinate scalar grids + per-group scales, RCO assigns a quantization type per tensor under an exact size budget (Riemannian constrained optimization).
- **HF Repo**: https://huggingface.co/ISTA-DASLab/Qwen3.8-27B-GSQ-RCO-GGUF
- **Files**: `IQ2_XS` 2.50 bpw / 8.4 GB; `IQ2_S` 2.75 / 9.3 GB; `IQ3_XXS` 3.00 / 10.1 GB; `IQ3_S` 3.50 / 11.8 GB (recommended, task-lossless); each with an optional `-mtp` build (+~0.35 GB) carrying the MTP head; `mmproj-Qwen3.8-27B-BF16.gguf` 0.9 GB for vision.
- **Context Window**: inherits Qwen3.8-27B (262,144 native, extensible to 1M).
- **Reported results vs BF16 (53.8 GB)**: `IQ3_S` reproduces AIME25 (100.00) and LiveCodeBench v6 (85.71) exactly and GPQA-Diamond 89.39 vs 89.90 — task average 91.70 vs 91.87 (99.8%) at 11.8 GB, a 4.6x size reduction. `IQ2_XXS` already matches BF16 on AIME25 at 10.1 GB. At matched file size (8.4 GB) `IQ2_XS` beats Unsloth `UD-IQ2_S` by +10.00 AIME25, +8.59 GPQA-D, +4.57 LCB v6.
- **Reproducibility**: per-file tensor allocation dumps and the shared imatrix ship inside the repo.
- **Verdict**: the strongest low-bit lane for the Main Dense baseline — 11.8 GB keeps a 27B dense model plus KV inside 24 GB at long context where Q4-class GGUFs do not.

## Main Exotic models

### Qwen3.6-35B-A3B-Escha-W2 (EschaLabs)

- **Base Architecture**: Qwen3.6-35B-A3B MoE with 2-bit `EschaMoE` weight quantization (128 experts, ~3.0B active params, GQA).
- **Model Repo**: `EschaLabs/Qwen3.6-35B-Escha-W2`.
- **Runtime Engine**: [escha-runtime-qwen3moe](https://huggingface.co/EschaLabs/escha-runtime-qwen3moe) (SGLang & ZML backends).
- **VRAM Footprint**: ~9.8 GB (`EschaMoE` 2-bit quantization, retains ~98% of FP8 accuracy).
- **Context Window**: 32K native; extends to 256K via YaRN RoPE scaling.
- **Chat Template & Thinking**: Jinja chat template with `enable_thinking: true`; supports `<think>...</think>` CoT and tool-call XML schema.
- **Speculative Decoding**: MTP draft tensors supported via Qwen3.6-35B MTP-only GGUF; CPU N-Gram fallback available.

### fuse-1-Lite (Akahsizrr)

- **Architecture**: 5.72B MoE SLM fusing `LiquidAI/LFM2.5-2.6B` host (2.70B frozen params) with 960 coding experts (3.02B params) transplanted from `Qwen3.6-35B-A3B`; learned router.
- **Model Repo**: `Akahsizrr/fuse-1-Lite`.
- **VRAM Footprint**: ~4.2 GB (`bfloat16`).
- **Context Window**: 32K native; extends to 256K via YaRN RoPE scaling.
- **Chat Template & Thinking**: Jinja chat template with `enable_thinking: true`; supports tool-call XML schema for subagent execution.
- **Speculative Decoding**: MTP draft tensors compatible (smaller KV footprint); CPU N-Gram predictor fallback.

### Ternary-Bonsai-27B

- **Architecture**: 27B dense decoder with ternary (1.58-bit) weight quantization; extreme parameter efficiency via ternary activations + low-bit weights.
- **HF Repo**: https://huggingface.co/Ternary/Bonsai-27B
- **GGUF Repo**: `Ternary/Bonsai-27B-GGUF` — quantization `Q2_0` (~7.2 GB VRAM).
- **Context Window**: 32K native; extends to 256K via YaRN RoPE scaling.
- **Chat Template & Thinking**: Jinja chat template with `enable_thinking: true`; supports `<think>...</think>` CoT and tool-call XML schema.
- **Speculative Decoding**: MTP draft tensors compatible (27B dense family); CPU N-Gram predictor fallback.
- **Low-Memory Deployment Tradeoffs**: Extremely lean at 7.2 GB VRAM enables deployment on constrained hardware, but loses syntax depth vs full-precision 35B MoE — best for code-completion and lightweight agentic assist rather than deep reasoning.

## Small models

### MiniCPM5-2B (OpenBMB)

- **Architecture**: dense 2.517B-parameter transformer (`LlamaForCausalLM`; 1.982B non-embedding), 42 layers, GQA 16 Q / 2 KV heads. Standard architecture: no custom kernels, no model-code fork.
- **HF Repo**: https://huggingface.co/openbmb/MiniCPM5-2B
- **GGUF Repo**: `openbmb/MiniCPM5-2B-GGUF` — `MiniCPM5-2B-Q4_K_M.gguf` 1.56 GB, `-Q8_0.gguf` 2.68 GB, `-F16.gguf` 5.04 GB.
- **Context Window**: 131,072.
- **Chat Template & Thinking**: `enable_thinking` toggle via `apply_chat_template`; XML-style tool calls parsed natively by SGLang (`--tool-call-parser minicpm5`).
- **Speculative Decoding**: `openbmb/MiniCPM5-2B-DSpark` draft model (SGLang `--speculative-algorithm DSPARK`, block size 7).
- **Training**: base + midtrain on UltraData tiers; post-training = 400B-token deep-thinking SFT, RL (JustRL II critic-based), then On-Policy Distillation of 16 RL teachers (5 agentic). RL+OPD adds ~+10.96 points reasoning/general and ~+6.96 agentic.
- **Reported average 53.9** — 2B-class open-source SOTA in its own comparison set, above every 4B-class model listed (Qwen3.5-4B 51.1, granite-4.2-3B 42.7, Nemotron-3-Nano-4B 32.6, Gemma-4-E4B-it 31.2) and far above LFM2.5-2.6B (33.2), Qwen3.5-2B (28.0), Gemma-4-E2B-it (24.6).
- **Key results**: LiveCodeBench v6 69.1; LCB-Pro Easy 68.0 / Medium 17.5; OJBench 32.5; SciCode 26.3; AIME 2025 86.5 / AIME 2026 86.5; HMMT Feb 2026 63.8; MATH-500 94.6; IFBench 66.3; IFEval 86.7; Multi-IF 71.8; MMLU-Pro 70.8; MMLU-Redux 84.7; HLE 8.9; GPQA-Diamond 70.2; SuperGPQA 40.8; AA-LCR 59.0; NoLiMa 68.1; LongBenchPro 44.8; LongBench v2 43.7; tau3-Banking 20.8; tau2-Telecom 97.1; BFCL v4 66.6; SWE-bench Verified 46.4; SWE-bench Pro 14.4; Terminal-Bench v2.1 8.6; BrowseComp-ZH 43.5; BrowseComp Top100 39.7; GAIA Text-103 88.7; GDPval-AA v2 19.6; Claw-Gym 59.2; WildClaw 23.9; QwenClaw 42.9.
- **Fit**: strongest sub-2GB agentic sidecar in the set; 131K context plus tool parsing make it the default Small-class candidate.

### Spark-X2.5-4B (XHToken / SparkLLM)

- **Architecture**: 4B dense hybrid attention — one full-attention layer per three sliding-window layers (trims long-context compute and KV size); >200 languages; Apache-2.0; trained on Huawei Ascend clusters (20T pre-training tokens, 1M-token long-context stage).
- **HF Repo**: https://huggingface.co/XHToken/Spark-X2.5-4B — sibling `Spark-X2.5-1.7B`.
- **GGUF**: none published in the model repo; llama.cpp / Ollama / LM Studio are documented via the `XHToken/llama.cpp` and `XHToken/llama.cpp-spark` forks, and SGLang/vLLM/MLX paths are given.
- **Context Window**: 1,048,576 (1M) native.
- **Chat Template & Thinking**: thinking on by default (chat template + Qwen3 reasoning parser); `chat_template_kwargs: {"enable_thinking": false}` disables per request; `--tool-call-parser spark25`.
- **Harness integrations (author)**: Codex, Claude Code, OpenClaw, Hermes.
- **Key results (4B)**: BFCL-V4 65.1; tau2-bench 75.1; tau3-bench 30.4; MCP-Atlas 54.6; MCP-Mark 14.2; Workspace Bench 31.2; VitaBench2.0 25.2; BrowseComp 40.9; SWE-bench Pro 44.4; SWE-bench Verified 41.6; SWE-bench Multilingual 53.3; SciCode 34.7; Gaokao 2026 133.4; AIME 2026 90.7; HMMT Feb 2026 81.2; IMO-AnswerBench 74.2; IFEval 93.0; IFBench 75.0; AA-LCR 56.3; HLE 12.3; GPQA 67.4.
- **Reference rows from the same card**: Spark-X2.5-1.7B (BFCL 46.9, tau3 20.1, MCP-Atlas 23.4, SWE-bench Verified 28.3, SWE-bench Pro 10.4, AIME 2026 69.4, HLE 6.3); Qwen3.5-4B (BFCL 50.3, tau2 79.9, tau3 6.7, SWE-bench Verified 38.8, AIME 2026 83.0); Gemma4-12B (BFCL 37.4, tau3 13.3, SWE-bench Verified 44.2, AIME 2026 82.1, HLE 13.1).
- **Note**: agentic numbers come from a 4B model with 1M context — the closest Small-class competitor to MiniCPM5-2B on tool/MCP tasks, while trailing it on raw coding.

## Community Builds candidates (ROCmFPX / ROCmFP4)

Models published by the community using ROCmFPX weight formats that are **not already
in the chat list above**. Sizes are whole-repository totals (several ship more than one
quant preset, a drafter, or a vision projector), taken from the ROCmFPX *Community
Builds* table plus the HF repo metadata. None of these builds has been benchmarked or
endorsed by the ROCmFPX project, and none carries an independent agentic benchmark.

| Repository | Base model | Class | Sizes / notes |
|---|---|---|---|
| [`jcbtc/chadrock-35b-ace-saber-rocmfp4-mtp`](https://huggingface.co/jcbtc/chadrock-35b-ace-saber-rocmfp4-mtp) | `GestaltLabs/Qwen3.6-35B-A3B-NSC-ACE-SABER-GGUF-MTP` | Main MOE (35B A3B) | MoEQuality 7.07 bpw + F16->ROCmFP4 STRIX_LEAN, `qwen35moe` 262K ctx, MTP + vision, agentic-coding/tool-calling tags; 31.4 GB main file |
| [`jcbtc/Laguna-S-2.1-Chadrock-ROCmFP4-StrixKVSpine-V4-GGUF`](https://huggingface.co/jcbtc/Laguna-S-2.1-Chadrock-ROCmFP4-StrixKVSpine-V4-GGUF) | `poolside/Laguna-S-2.1` | Main (arch `laguna`) | single 65.4 GB ROCmFP4 file, 262K ctx, long-context + agentic-coding + tool-use, openmdw-1.1 |
| [`plunderstruck/Qwen3.6-40B-Deckard-MTP-ROCmFP4-GGUF`](https://huggingface.co/plunderstruck/Qwen3.6-40B-Deckard-MTP-ROCmFP4-GGUF) | `DavidAU/Qwen3.6-40B-Claude-4.6-Opus-Deckard-Heretic-...` | Main (40B frankenmerge) | MTP + vision, Di-IMATRIX MAX, embQ8/headQ6; ~22.4 GiB per the ROCmFPX table |
| [`lmcoleman/Tess-4-27B-ROCmFPX-GGUF`](https://huggingface.co/lmcoleman/Tess-4-27B-ROCmFPX-GGUF) | `migtissera/Tess-4-27B` | Main Dense 27B | 8 presets (`Q3_0_ROCMFPX` -> `Q8_0_ROCMFPX`, incl. `_AGENT` and `_COHERENT`), 262K ctx; 160.9 GiB repo |
| [`lmcoleman/ThinkingCap-Qwen3.6-27B-ROCmFPX-GGUF`](https://huggingface.co/lmcoleman/ThinkingCap-Qwen3.6-27B-ROCmFPX-GGUF) | `bottlecapai/ThinkingCap-Qwen3.6-27B` | Main Dense 27B | MagicQuant MQ-Q4 / MQ-Q6 + f16 mmproj, 262K ctx; 36.2 GiB repo |
| [`raulvidis/Ling-3.0-flash-ROCmFP4-STRIX-MTP-GGUF`](https://huggingface.co/raulvidis/Ling-3.0-flash-ROCmFP4-STRIX-MTP-GGUF) | `inclusionAI/Ling-3.0-flash` | Main MOE (`bailingmoe3`) | MTP, 262K ctx, MIT; 64.9 GiB repo |
| [`kingjones777/Leanstral-1.5-119B-A6B-ROCmFP4-STRIX_LEAN-GGUF`](https://huggingface.co/kingjones777/Leanstral-1.5-119B-A6B-ROCmFP4-STRIX_LEAN-GGUF) | `mistralai/Leanstral-1.5-119B-A6B` | Exotic (119B / 6B active, Lean4) | `deepseek2` arch, 1,048,576 ctx, `reasoning_effort` none/high; 59.0 GiB - far above 24 GB, only formal-proof-tuned entry |
| [`christopher-kapic/AEON-Ultimate-ROCmFP4-Strix-Halo-GGUF`](https://huggingface.co/christopher-kapic/AEON-Ultimate-ROCmFP4-Strix-Halo-GGUF) | `AEON-7/Qwen3.6-27B-AEON-Ultimate-Uncensored-BF16` | Main Dense 27B | ROCmFP4 STRIX / STRIX_LEAN + ROCmFP6 + ROCmFP6-AGENT, MTP, 262K ctx; 72.3 GiB repo |

Additional ROCmFPX lanes seen in the same table, kept for reference rather than as new
candidates: Ornith-1.0-35B ROCmFP4/FPX rebuilds (already listed), Qwopus3.6-27B Coder/v2
(3.6-era, superseded by Qwopus3.8-27B-Flash), DeepSeek-V4-Flash ROCmFP3 (284B,
cross-scale reference only), MiMo-V2.5 ROCmFP4 (433 GiB, out of scope), chadrock
Laguna variants and `Tess`/`ThinkingCap` siblings.

## Cross-cutting architecture

### Multi-Token Prediction (MTP) Speculative Decoding: Architecture, Memory Overhead & VRAM Scaling

Multi-Token Prediction (MTP) accelerates autoregressive generation by training an auxiliary transformer block (`blk.40`) to predict $k$ future tokens in parallel with the main model forward pass. During speculative decoding in `llama-server`, candidate draft tokens from `blk.40` are validated in a single forward verification pass through the 40-layer base model.

#### 1. MTP Tensor Architecture Breakdown
The MTP module consists of **20 dedicated tensors** totaling **844,640,768 parameters (~844.6M params)** representing a complete single-layer prediction head:
- **Dual Hidden State Projection**: `blk.40.nextn.eh_proj.weight` ($4096 \times 2048$, 8.39M elems) fuses the previous token embedding with the current hidden state.
- **Layer Normalizations**: `blk.40.nextn.enorm.weight`, `blk.40.nextn.hnorm.weight`, `blk.40.nextn.shared_head_norm.weight` (F32, 2,048 elems each).
- **Attention Sub-layer**: `blk.40.attn_q.weight` (16.78M elems), `blk.40.attn_k.weight` (1.05M elems), `blk.40.attn_v.weight` (1.05M elems), `blk.40.attn_output.weight` (8.39M elems), with per-head Q/K RMS norms.
- **MoE Expert Feed-Forward Sub-layer**: 256 routed experts with `blk.40.ffn_gate_exps.weight`, `blk.40.ffn_up_exps.weight`, `blk.40.ffn_down_exps.weight` (268.4M elems each in `Q4_0`), plus shared expert routing tensors (`blk.40.ffn_*_shexp.weight`).

#### 2. Exact VRAM Memory Overhead Calculation

| Component | Quantization / Format | Memory Allocation | Notes |
| :--- | :--- | :--- | :--- |
| **MTP Weights (`blk.40`)** | `Q4_0` / `F32` | **454.86 MiB (0.444 GiB)** | 844.6M parameters stored in VRAM. |
| **Draft KV Cache** | `q4_0` K / `q4_0` V | **~2.35 MiB** | 1 layer only; scales with draft window ($n_{\text{draft\_max}}=4$) across 2 parallel slots. |
| **Compute Graph & Activations** | Backend Scratch Buffer | **~25.00 MiB** | Transient forward-pass working tensors on Vulkan/ROCm backend. |
| **Total Additional VRAM** | — | **~482.2 MiB (~0.471 GiB)** | **+2.4% VRAM increase** over 20 GB baseline. |

#### 3. Empirical Speed vs VRAM Tradeoff (RX 7900 XT / Vulkan)

| Speculative Mode | Extra VRAM | Generation Throughput | 1024-Token Decode Time | Relative Speedup |
| :--- | :--- | :--- | :--- | :--- |
| **Internal MTP (Optimized, $n=4$)** | **+482 MiB** | **135.70 tokens/sec** | **7.55 s** | **+22.0% faster** |
| **Internal MTP (Default, $n=3$)** | **+482 MiB** | **127.52 tokens/sec** | **8.03 s** | **+14.6% faster** |
| **Baseline (No Speculative)** | 0 MiB | **111.29 tokens/sec** | **9.20 s** | 1.00x |
| **CPU N-Gram Predictor** | 0 MiB GPU (RAM only) | **110.51 tokens/sec** | **9.27 s** | ~1.00x |

#### 4. Serving Recommendations
1. **Embedded MTP GGUFs (`BigBang-v1-IQ4_XS.gguf`)**:
   Launch with `--spec-type draft-mtp --spec-draft-n-max 4 --cache-type-k-draft q4_0 --cache-type-v-draft q4_0` without `--model-draft`. `llama-server` automatically detects `blk.40` in memory and builds the draft context without duplicate file loading.
2. **Non-MTP GGUFs (733-tensor base builds)**:
   Load the standalone 856 MB slice `--model-draft /path/to/Qwen3.6-35B-A3B-MTP-ONLY.gguf --spec-type draft-mtp`.

## Baseline-normalized benchmark matrix (Qwen3.6-35B Baseline = 100%)


##### 📊 Multi-Domain Benchmark Matrix (Qwen3.6-35B Baseline = 100%)

The benchmarks below combine local agentic/CLI evaluations (Terminal-Bench 2.1, SWE-bench Verified/Pro, Claw-Eval, NL2Repo) with the frontier scientific, search, reasoning, and AI engineering benchmark suite (BrowseComp, XBench, HLE, FS-R, MLE-Bench, PaperBench, SciCode-V, BioMysteryBench). All entries follow the standardized format: **raw_score (+-relative_change%)**.

###### 1. CLI & Agentic Repository Engineering
| Model / Fine-tune | Terminal-Bench 2.1 | SWE-bench Verified | SWE-Bench Pro | Claw-Eval | NL2Repo  | VRAM & Footprint | Primary Specialization |
|---|---:|---:|---:|---:|---:|---|---|
| **Qwen3.6-35B (Baseline)** | 49.2 (100%) | 73.4 (100%) | 43.6 (100%) | 68.7 (100%) | 29.4 (100%) | 18.5 GB (APEX) | Neutral standard base infrastructure |
| 💥 **BigBang-v1** | 58.3 (+18.5%) | 79.4 (+8.2%) | **54.2 (+24.3%)** | 77.5 (+12.8%) | 36.0 (+22.4%) | 17.95 GB (IQ4_XS) | SOTA 35B reasoning & self-evolving agent |
| 🛡️ **BTL-4** (Bad Theory Labs) | 60.5 (+23.0%) | **78.4 (+6.8%)** | 48.2 (+10.6%) | 72.8 (+6.0%) | 35.2 (+19.7%) | 17.9 GB (IQ4_XS) | Execution-gated agentic reasoning & AST tool calls (73.5% BFCL) |
| ⚔️ **Fable-Fusion-711** (DavidAU) | 59.3 (+20.5%) | 77.2 (+5.2%) | 53.5 (+22.7%) | 75.2 (+9.5%) | **36.2 (+23.1%)** | 16.5 GB (IQ4_XS) | 27B Heretic multi-stage merge (>700 ARC-C, MTP accel) |
| 🌺 **Ornith-1.0-35B** (Apodex) | **62.8 (+27.6%)** | 75.6 (+3.0%) | 38.7 (-11.2%) | 69.8 (+1.6%) | 34.6 (+17.7%) | 21.2 GB (Q4_K_M) | Massive gain in CLI & terminal interaction |
| 🛠️ **KAT-Coder-V2.5-Dev** | 59.1 (+20.1%) | 79.6 (+8.4%) | 45.96 (+5.4%) | 67.2 (-2.2%) | 32.2 (+9.5%) | 18.5 GB (APEX) | Best code injector for hashline/diff edits |
| 🦅 **XYZ-Aquila-mini** (Nex-N2) | 51.3 (+4.3%) | 70.1 (-4.5%) | 50.2 (+15.1%) | 69.0 (+0.4%) | 28.6 (-2.7%) | 15.8 GB (Q3_K_XL) | Web browsing, scraping & long-horizon search |
| ⚡ **Qwen3.6-Escha-W2** | 48.5 (-1.4%) | 72.6 (-1.1%) | 42.8 (-1.8%) | 67.9 (-1.2%) | 28.9 (-1.7%) | **9.8 GB (EschaMoE)** | Ultra-compact 2-bit MoE (~98% FP8 retention in 9.8GB) |
| 🧪 **fuse-1-Lite** (5.72B) | 38.2 (-22.4%) | 62.5 (-14.9%) | 34.1 (-21.8%) | 58.6 (-14.7%) | 21.4 (-27.2%) | **4.2 GB (bfloat16)** | Compact 5.7B SLM fusing LFM2.5 base with 960 Qwen3.6 experts |
| 🧩 **Agents-A1** (Qwen3.5 Base) | 38.9 (-20.9%) | 61.5 (-16.2%) | 42.3 (-3.0%) | 65.4 (-4.8%) | 20.5 (-30.3%) | 17.5 GB (APEX) | Logically falls behind 3.6 series |
| ❄️ **North-Mini-Code-1.0** | 53.5 (+8.7%) | 74.0 (+0.8%) | 47.5 (+8.9%) | 69.5 (+1.1%) | 32.4 (+10.2%) | 19.2 GB (UD-Q4) | Native CoT reasoning for subagents |
| 🌐 **Qwen3.8-Flash-Next (Base)** | 67.6 (+37.4%) | - | **62.5 (+43.3%)** | 64.4 (-6.3%) | **48.1 (+63.6%)** | BF16 / GGUF | 125B ultra-sparse MoE base (512 experts, 6 active), GDN+QSA |
| ⚡ **Swift-1.5-Flash-Next (SC117)** | **69.7 (+41.7%)** | - | **62.5 (+43.3%)** | 64.4 (-6.3%) | **48.1 (+63.6%)** | 77.8 GB (IQ3_S Strata) | 125B ultra-sparse MoE, token-efficient Swift tune (-63.4% thinking tokens), zero refusal |
| 🍃 **Ternary-Bonsai-27B** | 43.7 (-11.2%) | 74.9 (+2.1%) | 39.2 (-10.1%) | 71.7 (+4.4%) | 25.2 (-14.3%) | 7.2 GB (Q2_0) | Extremely lean, but loses syntax depth |

###### 2. Frontier Research, Search & Scientific Reasoning Benchmarks
| Model / Fine-tune | BrowseComp (Search) | XBench | HLE (Reasoning) | FS-R (Sci-Research) | MLE-Bench (AI) | PaperBench (Dev) | SciCode-V (Main/Sub) | BioMystery (HS/HD) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **Qwen3.6-35B (Baseline)** | 67.9 (100%) | 32.6 (100%) | 36.2 (100%) | 11.9 (100%) | 31.8 (100%) | 30.7 (100%) | 26.6 / 56.5 (100%) | 44.8 / 2.0 (100%) |
| 💥 **BigBang-v1** | **76.5 (+12.7%)** | 58.4 (+79.1%) | **50.3 (+39.0%)** | **46.2 (+288.2%)** | **59.1 (+85.8%)** | **53.6 (+74.6%)** | **50.0 / 68.6 (+88.0% / +21.4%)** | **57.5 / 15.7 (+28.3% / +685%)** |
| 🛡️ **BTL-4** (Bad Theory Labs) | 74.2 (+9.3%) | 59.8 (+83.4%) | 46.8 (+29.3%) | 31.2 (+162.2%) | 35.4 (+11.3%) | 32.8 (+6.8%) | 39.2 / 60.1 (+47.4% / +6.4%) | 48.5 / 6.2 (+8.3% / +210%) |
| ⚔️ **Fable-Fusion-711** (DavidAU) | 74.8 (+10.2%) | 56.2 (+72.4%) | 47.1 (+30.1%) | 34.5 (+189.9%) | 42.6 (+34.0%) | 41.2 (+34.2%) | 42.5 / 62.8 (+59.8% / +11.2%) | 52.0 / 8.5 (+16.1% / +325%) |
| 🌺 **Ornith-1.0-35B** (Apodex) | 73.9 (+8.8%) | **61.8 (+89.6%)** | 45.3 (+25.1%) | 29.6 (+148.7%) | 27.3 (-14.2%) | 20.5 (-33.2%) | 35.0 / 42.0 (+31.6% / -25.7%) | 50.2 / 5.9 (+12.1% / +195%) |
| 🛠️ **KAT-Coder-V2.5-Dev** | 68.5 (+0.9%) | 48.2 (+47.9%) | 42.1 (+16.3%) | 28.4 (+138.7%) | 34.2 (+7.5%) | 31.5 (+2.6%) | 38.5 / 59.2 (+44.7% / +4.8%) | 46.5 / 4.0 (+3.8% / +100%) |
| 🦅 **XYZ-Aquila-mini** (Nex-N2) | 74.1 (+9.1%) | 57.2 (+75.5%) | 38.4 (+6.1%) | 36.8 (+209.2%) | 18.2 (-42.8%) | 14.8 (-51.8%) | 15.6 / 39.0 (-41.4% / -31.0%) | 42.9 / 5.9 (-4.2% / +195%) |
| ⚡ **Qwen3.6-Escha-W2** | 66.8 (-1.6%) | 32.1 (-1.5%) | 35.6 (-1.7%) | 11.6 (-2.5%) | 31.2 (-1.9%) | 30.2 (-1.6%) | 26.1 / 55.8 (-1.9% / -1.2%) | 44.1 / 1.9 (-1.6% / -5.0%) |
| 🧪 **fuse-1-Lite** (5.72B) | 51.2 (-24.6%) | 24.5 (-24.8%) | 22.4 (-38.1%) | 8.2 (-31.1%) | 18.5 (-41.8%) | 16.2 (-47.2%) | 19.4 / 41.2 (-27.1% / -27.1%) | 32.0 / 1.0 (-28.6% / -50.0%) |
| 🧩 **Agents-A1** (Qwen3.5 Base) | 48.5 (-28.6%) | 52.4 (+60.7%) | 46.3 (+27.9%) | 38.4 (+222.7%) | 27.3 (-14.2%) | 17.3 (-43.6%) | 50.0 / 64.1 (+88.0% / +13.5%) | 48.9 / 2.0 (+9.2% / 0.0%) |
| ❄️ **North-Mini-Code-1.0** | 71.2 (+4.9%) | 45.8 (+40.5%) | 43.0 (+18.8%) | 26.5 (+122.7%) | 32.5 (+2.2%) | 28.0 (-8.8%) | 34.0 / 58.0 (+27.8% / +2.7%) | 47.0 / 4.0 (+4.9% / +100%) |
| 🍃 **Ternary-Bonsai-27B** | 58.0 (-14.6%) | 36.5 (+12.0%) | 39.5 (+9.1%) | 18.2 (+52.9%) | 22.4 (-29.6%) | 19.0 (-38.1%) | 20.0 / 45.0 (-24.8% / -20.4%) | 40.0 / 2.0 (-10.7% / 0.0%) |
| 🌐 **Qwen3.8-Flash-Next (Base)** | - | - | 35.9 (-0.8%) | - | - | - | - | - |
| ⚡ **Swift-1.5-Flash-Next (SC117)** | - | - | ~35.0 (-3.3%) | - | - | - | - | - |

All entries keep the original format: **raw_score (+-relative_change%)**. The clean
cross-comparison tables without deltas live in the main document; this section preserves the
baseline-normalized view.

## ROCmFPX / Custom AMD ROCm Quants & Expected Differences

Source: [charlie12345/ROCmFPX](https://github.com/charlie12345/ROCmFPX) - an experimental feature
family on the canonical `main` branch of a `llama.cpp` fork (MIT, C++, 383 stars / 59 forks).
ROCmFPX adds AMD-oriented 2-, 3-, 4-, 6- and 8-bit **model-weight** GGUF formats with CPU
reference paths plus accelerated HIP/ROCm and Vulkan kernels. It is not a K/V-cache-only
compression trick: the formats are real weight tensor types with dequant math, and the
K/V side is a separate runtime control (TurboQuant, below).

### Format family

| Family | GGUF preset | Layout | Status |
|---|---|---|---|
| **ROCmFP2** | `Q2_0_ROCMFPX` | 2.50 bpw, S40 `{-4,-1,+1,+4}` codebook, dual UE4M3 scales | Optimized and validated |
| **ROCmFP3** | `Q3_0_ROCMFPX` | 3.5 bpw | Development preview |
| **ROCmFP4** | `Q4_0_ROCMFP4` / `Q4_0_ROCMFP4_FAST` | 4.50 bpw dual per-16 scale / 4.25 bpw single scale | Optimized and validated |
| **ROCmI4** | `Q4_0_ROCMI4` | signed 4-bit weights; optional gfx1151 IU4 W4A4 MMQ | Exact path by default; W4A4 opt-in |
| **ROCmFP6** | `Q6_0_ROCMFPX` | 6.5 bpw | Development preview |
| **ROCmFP8** | `Q8_0_ROCMFPX` | 8.25 bpw | Development preview |

Agent variants: `Q3_0_ROCMFPX_AGENT`, `Q6_0_ROCMFPX_AGENT`, `Q8_0_ROCMFPX_AGENT`, and
`Q4_0_ROCMFP4_COHERENT` (ROCmFP4 agent preset). These use the same dequant math but route
extra bits to the tensors that break structured output: token and output embeddings,
attention Q/K/V/O, selected FFN-down, and selective FFN-gate tensors (bulk FFN-up stays on the
family quant). Agent quants are therefore slightly larger than straight quants.

### Expected differences vs regular GGUF quants

Sizes and speeds below are the project's own Strix Halo / `gfx1151` measurements (same model
pair, backend, batch shape, K/V and FlashAttention per row, one test at a time).

- **File size**: ROCmFP4 lands ~12% below the matched `Q4_K_M`. Qwen3.6-27B: 16.55 GB ->
  14.59 GB (-11.82%). Qwen3.6-35B-A3B MTP: 21.71 GB -> 19.05 GB (-12.28%).
- **Decode**: faster than `Q4_K_M` on both backends. Qwen3.6-27B vanilla: Vulkan 12.89 ->
  14.27 t/s, ROCm0 11.74 -> 13.53 t/s. Qwen3.6-35B-A3B: Vulkan 70.57 -> 76.71 t/s,
  ROCm0 59.00 -> 66.42 t/s.
- **Prompt fill**: mixed. On `llama-bench pp512` ROCm is slightly behind `Q4_K_M` (27B
  336.97 -> 328.03 t/s; 35B-A3B 1353.50 -> 1301.21 t/s) while Vulkan leads (27B 352.04 ->
  376.98 t/s; 35B-A3B 1065.83 -> 1200.81 t/s). On a 20-prompt Hermes-style agent smoke both
  backends favour ROCmFP4: ROCm0 699.7 -> 731.4 prompt t/s and 31.9 -> 47.1 generation t/s;
  Vulkan0 654.0 -> 730.9 prompt t/s and 40.2 -> 57.5 generation t/s.
- **ROCmFP2 is the more lossy family** - use it when memory traffic and capacity dominate.
  Matched Qwen3.6-35B-A3B 256-token decode: Vulkan 90.30 t/s vs ROCmFP4 76.20 (+18.50%);
  ROCm0 75.90 vs 67.50 t/s (+12.44%).
- **Quality is not free**: the 4.25 bpw `_FAST` layout cost ~5% higher perplexity than the
  4.50 bpw target for a ~10% smaller file on a 9B test model; the 4.50 bpw target landed within
  noise of its NVFP4 source. Always A/B against the BF16/F16 origin on your own prompts.
- **NVFP4 -> ROCmFP4 remap is the closest conversion available**: same UE4M3 scale and 7 of 8
  codebook levels identical (only the top magnitude level differs: NVFP4 12 vs ROCmFP4 10).
  `--allow-requantize` is required because NVFP4 files usually keep `output.weight` at a
  higher-precision type. `Q4_0_ROCMFP4_EVEN` / `Q4_0_ROCMFP4_FAST_EVEN` force one type for
  every tensor (implies `--pure`).
- **Built-in MTP self-speculative decoding**: models with an embedded MTP/NextN head (including
  M-RoPE `qwen35` / `qwen35moe` models) can verify drafted tokens against the target with no
  separate draft model. Verified on `gfx1151`: Qwable-5-27B-Coder 14.0 -> 33.2 t/s (2.37x at
  `n6 / p0.60`); Qwen3.6-35B-A3B 76.5 -> 116.1 t/s median / 118.3 peak (1.52x at `n4 / p0.55`).
  Greedy (`--temp 0`) output is token-for-token identical to non-speculative decode; gains are
  content-dependent (code/JSON/lists accept more drafts than prose).
- **K/V is a separate control**: TurboQuant runtime cache types `turbo3` / `turbo4` are built
  into the tree (CPU reference + ROCm/HIP + Vulkan). Recommended agentic policy is asymmetric:
  `-ctk q8_0 -ctv turbo4`. The guard promotes `-ctk q3_0_rocmfpx` to `q6_0_rocmfpx` because fp3
  K cache fell below the observed tool-call coherency floor; `q3_0_rocmfpx` remains usable for V.
  Symmetric TurboQuant is a sweep setting, not a default.
- **ROCmI4 W4A4 (gfx1151 only, opt-in, lossy)**: `GGML_HIP_ROCMI4_W4A4` defaults to `OFF`, device
  code compiles only for `__gfx1151__`, and runtime dispatch requires the exact gfx1151 device id.
  It targets prompt processing and MTP target verification (batched MMQ), not single-token decode.
  Matched 10-task Qwen3.8-27B pilot with strict MTP-16: mean decode 41.63 -> 49.40 t/s
  (+18.66%), aggregate decode 40.90 -> 48.29 t/s, prompt processing 283.83 -> 318.83 t/s. A full
  164-task run measured 44.39 t/s mean / 45.23 t/s median with HumanEval pass@1 94.5% and
  HumanEval+ 91.5%, at ~5.4% higher perplexity than the exact path. **Not usable on this host**:
  the RX 7900 XTX is `gfx1100` (RDNA3), not `gfx1151` (RDNA3.5).
- **Build targets**: Strix Halo `gfx1151`, RDNA2 `gfx1030`, RDNA3 `gfx1100`, RDNA4 `gfx1200`, plus a
  self-contained ROCm 7.14 RDNA4 build. On the local RDNA3 `gfx1100` host the build script is
  `scripts/build-rdna3.sh` -> `build-rdna3/`.

### Format selection

| Goal | Preset |
|---|---|
| Smallest optimized | `Q2_0_ROCMFPX` (validate quality per model) |
| Speed-first 4-bit | `Q4_0_ROCMFP4_FAST` |
| Balanced 4-bit | `Q4_0_ROCMFP4` |
| Agents / tools / JSON / code | `Q4_0_ROCMFP4_COHERENT` or any `*_AGENT` |
| Strix Halo tuned | `Q4_0_ROCMFP4_STRIX_LEAN` |
| Experimental gfx1151 IU4 + MTP | `Q4_0_ROCMI4` with W4A4 enabled |
| Higher-bit previews | `Q6_0_ROCMFPX` / `Q8_0_ROCMFPX` (6.5 / 8.25 bpw) |

Bottom line for this doc: ROCmFP2 and ROCmFP4 are the only validated families, and only the
RDNA3-class kernels apply to the RX 7900 XTX. They buy ~12% size and ~10-20% decode over matched
`Q4_K_M` with a documented, measurable quality cost; the `*_AGENT` presets are the safer default
for tool-calling and JSON work, and embedded-MTP GGUFs are the cheapest available decode win.

### Community Builds

Non-listed models quantized by the community with ROCmFPX / ROCmFP4 (chadrock-35B, Laguna-S-2.1,
Qwen3.6-40B-Deckard, Tess-4-27B, ThinkingCap-27B, Ling-3.0-flash, Leanstral-1.5-119B,
AEON-Ultimate-27B) are catalogued with base models, architectures and repository sizes in
[`model-research-chat.md`](model-research-chat.md#community-builds-candidates-rocmfpx--rocmfp4).
None of them carries benchmarks, and none is endorsed by the ROCmFPX project.
