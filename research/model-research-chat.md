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
| **Qwen3.6-35B** (baseline) | MOE | 35B / 3B | APEX 18.5 GB | 49.2 | 73.4 | 43.6 | 68.7 | 29.4 |
| BigBang-v1 | MOE | 35B / 3B | IQ4_XS 17.95 GB | 58.3 | 79.4 | **54.2** | 77.5 | 36.0 |
| BTL-4 | MOE | 35B / 3B | IQ4_XS 17.9 GB | 60.5 | 78.4 | 48.2 | 72.8 | 35.2 |
| Ornith-1.0-35B | MOE | 35B / 3B | Q4_K_M 21.2 GB | **62.8** | 75.6 | 38.7 | 69.8 | 34.6 |
| KAT-Coder-V2.5-Dev | MOE | 35B / 3B | APEX 18.5 GB | 59.1 | **79.6** | 45.96 | 67.2 | 32.2 |
| XYZ-Aquila-mini | MOE | ~10B / ~3B | Q3_K_XL 15.8 GB | 51.3 | 70.1 | 50.2 | 69.0 | 28.6 |
| North-Mini-Code-1.0 | MOE | ~12B / ~4B | UD-Q4 19.2 GB | 53.5 | 74.0 | 47.5 | 69.5 | 32.4 |
| Agents-A1 | MOE | 35B / 3B | APEX class 17.5 GB | 38.9 | 61.5 | 42.3 | 65.4 | 20.5 |
| K2-Horizon-MoVA-36B-A4B | MOE | 36B / 4B | BF16 ~72 GB | 58.6 | - | - | - | - |
| **Qwen3.8-27B** (baseline) | Dense | 27B | UD-Q4_K_XL 17.56 GB | **73.0** | - | **61.7** | - | 42.3 |
| Fable-Fusion-711 | Dense | 27B | IQ4_XS 16.5 GB | 59.3 | 77.2 | 53.5 | 75.2 | 36.2 |
| Qwen3.8-27B-TURBO-735-882 | Dense | 27B | NEO IMATRIX | - | - | - | - | - |
| Qwopus3.8-27B-Flash | Dense | 27B | MTP-Q5_K_M 19.54 GB | - | - | - | - | - |
| Qwen3.8-27B GSQ-RCO | Dense | 27B | IQ3_S 11.8 GB | - | - | - | - | - |
| Qwen3.6-Escha-W2 | Exotic | 35B / 3B | EschaMoE 9.8 GB | 48.5 | 72.6 | 42.8 | 67.9 | 28.9 |
| fuse-1-Lite | Exotic | 5.72B | bf16 4.2 GB | 38.2 | 62.5 | 34.1 | 58.6 | 21.4 |
| Ternary-Bonsai-27B | Exotic | 27B | Q2_0 7.2 GB | 43.7 | 74.9 | 39.2 | 71.7 | 25.2 |

The three new dense entries publish no Terminal-Bench / SWE-bench numbers; what they do report
(agentic SWE battery, ARC-C, AIME25/GPQA/LCB) is in table 3 and in
[`model-research-chat.md`](model-research-chat.md).

###### Main-2. Frontier research, search and scientific reasoning

| Model | Category | BrowseComp | XBench | HLE | FS-R | MLE-Bench | PaperBench | SciCode-V (Main/Sub) | BioMystery (HS/HD) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **Qwen3.6-35B** (baseline) | MOE | 67.9 | 32.6 | 36.2 | 11.9 | 31.8 | 30.7 | 26.6 / 56.5 | 44.8 / 2.0 |
| BigBang-v1 | MOE | **76.5** | 58.4 | **50.3** | **46.2** | **59.1** | **53.6** | **50.0 / 68.6** | **57.5 / 15.7** |
| BTL-4 | MOE | 74.2 | 59.8 | 46.8 | 31.2 | 35.4 | 32.8 | 39.2 / 60.1 | 48.5 / 6.2 |
| Ornith-1.0-35B | MOE | 73.9 | **61.8** | 45.3 | 29.6 | 27.3 | 20.5 | 35.0 / 42.0 | 50.2 / 5.9 |
| KAT-Coder-V2.5-Dev | MOE | 68.5 | 48.2 | 42.1 | 28.4 | 34.2 | 31.5 | 38.5 / 59.2 | 46.5 / 4.0 |
| XYZ-Aquila-mini | MOE | 74.1 | 57.2 | 38.4 | 36.8 | 18.2 | 14.8 | 15.6 / 39.0 | 42.9 / 5.9 |
| Agents-A1 | MOE | 48.5 | 52.4 | 46.3 | 38.4 | 27.3 | 17.3 | 50.0 / 64.1 | 48.9 / 2.0 |
| North-Mini-Code-1.0 | MOE | 71.2 | 45.8 | 43.0 | 26.5 | 32.5 | 28.0 | 34.0 / 58.0 | 47.0 / 4.0 |
| K2-Horizon-MoVA-36B-A4B | MOE | - | - | 25.2 | - | - | - | 38.9 / - | - |
| Qwen3.8-27B (baseline) | Dense | - | - | 30.8 | - | - | - | - | - |
| Fable-Fusion-711 | Dense | 74.8 | 56.2 | 47.1 | 34.5 | 42.6 | 41.2 | 42.5 / 62.8 | 52.0 / 8.5 |
| Qwen3.6-Escha-W2 | Exotic | 66.8 | 32.1 | 35.6 | 11.6 | 31.2 | 30.2 | 26.1 / 55.8 | 44.1 / 1.9 |
| fuse-1-Lite | Exotic | 51.2 | 24.5 | 22.4 | 8.2 | 18.5 | 16.2 | 19.4 / 41.2 | 32.0 / 1.0 |
| Ternary-Bonsai-27B | Exotic | 58.0 | 36.5 | 39.5 | 18.2 | 22.4 | 19.0 | 20.0 / 45.0 | 40.0 / 2.0 |

###### Main-3. 2026 agent-suite results not covered by tables 1-2

| Model | Reported result |
|---|---|
| K2-Horizon-MoVA-36B-A4B | tau3-Banking 26.8; GPQA-Diamond 80.8; CritPt 2.1; AA-LCR 66.3; AA-Omniscience accuracy 18.8 / non-hallucination 69.2 |
| Qwen3.8-27B (baseline) | SWE-bench Pro 61.7; NL2Repo 42.3; DeepSWE 1.1 42.2; QwenSWEBench 79.0; CoWorkBench 70.7; JobBench 33.4; Agents' Last Exam pass@1 20.4 / score 42.9; IFBench 79.5; GPQA-D 89.2; HLE 30.8; LiveCodeBench v6 90.3; OSWorld-Verified 84.3; WebArena-Verified 64.8; AndroidWorld 81.9; RecreationBench 47.1; ClawEval-MM 57.4 pass@3 / 56.9 avg; SWE-MM 38.6; Vision2Web 62.9; MathVision 94.6 (with CI); BabyVision 85.6 (with CI); CharXiv 90.2 (with CI); OmniDocBench 1.5 91.1; RealWorldQA 85.9; ERQA 65.5 |
| Qwen3.8-27B GSQ-RCO `IQ3_S` | AIME25 100.00 (BF16-equal), GPQA-Diamond 89.39 (vs 89.90), LiveCodeBench v6 85.71 (BF16-equal) at 11.8 GB / 3.50 bpw |
| Qwopus3.8-27B-Flash | MMLU-Pro 91.28% (base 92.73%); +12.8% decode throughput; 80.7% weighted MTP acceptance; 13/14 agentic software-engineering battery |
| Qwen3.8-27B-TURBO-735-882 | ARC-C 0.735 mxfp8 / 0.719 mxfp4; ARC-E 0.882; BoolQ 0.917; HellaSwag 0.832; OBQA 0.530; PIQA 0.837; WinoGrande 0.785 |


###### Main-4. Frontier model cross-scale comparison (35B scale vs 100B+ / closed frontier)

| Model | Architecture / Scale | BrowseComp | SWE-Bench Pro | HLE | FS-R | MLE-Bench | PaperBench | BioMystery (HD) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| **Claude Opus 4.8** | Frontier Closed API | 84.3 | 69.2 | 57.9 | 45.2 | 63.6 | - | 42.4 |
| **GPT 5.5** | Frontier Closed API | 84.4 | 58.6 | 52.2 | 58.3 | 59.1 | 64.2 | 23.5 |
| **DeepSeek V4 Pro** | 1.6T MoE Open-Weights | 83.4 | 55.4 | 48.2 | 40.7 | 59.1 | 50.4 | 13.7 |
| **DeepSeek V4 Flash** | 284B MoE Open-Weights | 73.2 | 52.6 | 45.1 | 37.7 | 40.9 | 40.4 | 23.5 |
| 💥 **BigBang-v1** | **35B MoE (Fine-tune)** | **76.5** | **54.2** | **50.3** | **46.2** | **59.1** | **53.6** | **15.7** |
| ⚔️ **Fable-Fusion-711** | **27B Dense (Merge)** | **74.8** | **53.5** | **47.1** | **34.5** | **42.6** | **41.2** | **8.5** |
| **Qwen3.6-35B** | 35B MoE (Baseline) | 67.9 | 43.6 | 36.2 | 11.9 | 31.8 | 30.7 | 2.0 |

###### Main-5. Cited benchmark repositories and leaderboards

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

Where results are missing across the tracked models (checked against every model card in this
doc and in [`model-research-chat.md`](model-research-chat.md)):

| Benchmark | Missing for |
|---|---|
| Terminal-Bench 2.1 | Spark-X2.5-4B; Qwopus3.8-27B-Flash; DavidAU TURBO-735-882; GSQ-RCO quant lanes |
| SWE-bench Verified | Qwen3.8-27B; K2-Horizon-MoVA-36B-A4B; Qwopus3.8-27B-Flash; TURBO-735-882; GSQ-RCO; all Main Exotic models |
| SWE-bench Pro | Main MOE fine-tunes except KAT-Coder and XYZ-Aquila (Ornith, BTL-4, North-Mini-Code, Agents-A1); all Main Exotic |
| BrowseComp | Qwen3.8-27B; all Main Dense entries; all Main Exotic except Fable-Fusion-711 (74.8) |
| GPQA-Diamond | Every Main MOE fine-tune (no vendor numbers); Escha-W2; fuse-1-Lite; Ternary-Bonsai-27B |
| HLE | Main MOE fine-tunes (matrix HLE tracks the baseline row); all Main Dense except Qwen3.8-27B |
| AIME 2025/2026 | All Main MOE and Main Exotic models; only GSQ-RCO and the Small models publish numbers |
| tau2/tau3-bench, BFCL v4, MCP-Atlas/Mark | All Main models; only K2-Horizon (tau3-Banking) among Main, plus the Small models |
| GAIA / GDPval-AA v2 / Claw-Gym / WildClaw / QwenClaw | All Main models; only MiniCPM5-2B publishes these |
| NL2Repo | Ornith-1.0-35B, XYZ-Aquila-mini, Agents-A1, North-Mini-Code-1.0, Escha-W2, fuse-1-Lite, Ternary-Bonsai-27B |
| Claw-Eval | Every Main Dense and Main Exotic entry |
| OSWorld / WebArena / AndroidWorld | All models except Qwen3.8-27B |

Not resolvable from public sources: the three new dense fine-tunes publish only author-run numbers
(ARC-C grid, an in-house 14-task SWE battery, a quantization-ablation table) and no vendor
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

### BigBang-v1

- **Base Model**: `endless-frontier/BigBang-v1` — Qwen3.6-35B-A3B fine-tuned with self-evolving synthetic CoT trajectories on ~10,000 frontier scientific & technical tasks.
- **GGUF Repo**: `bartowski/endless-frontier_BigBang-v1-GGUF`.
- **Selected GGUF** (IQ4_XS ~17.95 GB VRAM, closest footprint to APEX-I-Compact): `endless-frontier_BigBang-v1-IQ4_XS.gguf`.
- **Vision Projector**: `mmproj-endless-frontier_BigBang-v1-f16.gguf`.
- **Context Window**: 32K native; up to 256K context with YaRN/parallel slot sizing.
- **Chat Template & Thinking**: Integrated native Jinja chat template (`jinja = on`). **Requires `enable_thinking: true`** in `chat-template-kwargs` / system prompt so execution-gated CoT scratchpad retains tool evaluation state and terminates loops cleanly (avoids infinite `git diff`/`namcap` replay).
- **Speculative Decoding**: `BigBang-v1-IQ4_XS.gguf` contains **753 total tensors** with the **20 MTP draft tensors already embedded internally** under block 40 (`blk.40.nextn.*`, `blk.40.attn_*`, `blk.40.ffn_*`). It does not strictly require an external `-MTP-ONLY.gguf` slice; `llama-server` can load draft tensors directly from the main model file or from the standalone 856 MB `Qwen3.6-35B-A3B-MTP-ONLY.gguf` slice using `--spec-type draft-mtp --spec-draft-n-max 3`. Also fully compatible with CPU N-Gram speculative decoding (`--spec-type ngram-simple`).

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
