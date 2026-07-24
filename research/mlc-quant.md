# MLC-LLM Quantization Options

Reference for all available quantization modes in MLC-LLM v0.20.0.

## Summary Table

| Name | Kind | Weight Dtype | Model Dtype | Group Size | Quant Embed | Quant FC | Layout | Notes |
|------|------|-------------|-------------|-----------|-------------|----------|--------|-------|
| `q0f16` | no-quant | — | float16 | — | — | — | — | No quantization, fp16 |
| `q0bf16` | no-quant | — | bfloat16 | — | — | — | — | No quantization, bf16 |
| `q0f32` | no-quant | — | float32 | — | — | — | — | No quantization, fp32 |
| `q3f16_0` | group-quant | int3 | float16 | 40 | ✅ | ✅ | KN | 3-bit, axis=0 |
| `q3f16_1` | group-quant | int3 | float16 | 40 | ✅ | ✅ | NK | 3-bit, axis=1 |
| `q4f16_0` | group-quant | int4 | float16 | 32 | ✅ | ✅ | KN | 4-bit fp16, axis=0 |
| `q4f16_1` | group-quant | int4 | float16 | 32 | ✅ | ✅ | NK | 4-bit fp16, axis=1 |
| `q4f16_2` | group-quant | int4 | float16 | 32 | ❌ | ❌ | NK | 4-bit fp16, no embed/fc quant |
| `q4bf16_0` | group-quant | int4 | bfloat16 | 32 | ✅ | ✅ | KN | 4-bit bf16, axis=0 |
| `q4bf16_1` | group-quant | int4 | bfloat16 | 32 | ✅ | ✅ | NK | 4-bit bf16, axis=1 |
| `q4f32_1` | group-quant | int4 | float32 | 32 | ✅ | ✅ | NK | 4-bit fp32 accum, axis=1 |
| `q4f16_autoawq` | awq | int4 | float16 | 128 | — | — | — | AWQ pre-quantized models |
| `q4f16_ft` | ft-quant | int4 | float16 | — | — | — | — | FasterTransformer format |
| `e5m2_e5m2_f16` | per-tensor | fp8_e5m2 | float16 | — | ❌ | ❌ | — | FP8, no scale, inference calib |
| `e4m3_e4m3_f16` | per-tensor | fp8_e4m3 | float16 | — | ❌ | ❌ | — | FP8 w/ scale, inference calib |
| `e4m3_e4m3_f16_max_calibrate` | per-tensor | fp8_e4m3 | float16 | — | ❌ | ❌ | — | FP8 w/ scale, max calibration |
| `fp8_e4m3fn_bf16_block_scale` | block-scale | fp8_e4m3 | bfloat16 | block | — | — | — | Block-scale FP8 |
| `fp8_e4m3fn_bf16_block_scale_static_activation` | block-scale | fp8_e4m3 | bfloat16 | block | — | — | — | Block-scale FP8 + static act |

## Quantization Kinds

### No Quantization (`no-quant`)
- **`q0f16`**, **`q0bf16`**, **`q0f32`**: Full-precision weights, no quantization applied.
- Use for maximum quality or when debugging quantization issues.
- `q0f32` uses 4× the memory of `q0f16`.

### Group Quantization (`group-quant`)
- Most common mode. Groups of weights share a single scale factor.
- **Group size**: 32 (4-bit) or 40 (3-bit) elements per group.
- **Storage**: Packed into `uint32` (8 int4 values or 10 int3 values per uint32).
- **Layout variants**:
  - `_0` suffix = `KN` layout (weight axis=0 quantized)
  - `_1` suffix = `NK` layout (weight axis=1 quantized, generally faster)
- **`q4f16_2`**: Same as `q4f16_1` but skips embedding and final FC quantization (higher quality output at slight memory cost).

### AWQ Quantization (`awq`)
- **`q4f16_autoawq`**: For models pre-quantized with AutoAWQ.
- Uses group size 128 (larger groups = less overhead, slightly lower quality).
- Requires the model to already be AWQ-quantized.

### FasterTransformer Quantization (`ft-quant`)
- **`q4f16_ft`**: Uses `int8` storage (2 int4 values per byte).
- Compatible with FasterTransformer-style quantized models.

### Per-Tensor FP8 Quantization (`per-tensor-quant`)
- Uses 8-bit floating point for both weights and activations.
- **`e5m2`**: 5-bit exponent, 2-bit mantissa (wider range, less precision).
- **`e4m3`**: 4-bit exponent, 3-bit mantissa (narrower range, more precision).
- Requires hardware FP8 support (MI300X, H100, etc.).

### Block-Scale FP8 Quantization (`block-scale-quant`)
- FP8 weights with per-block scaling factors in bfloat16.
- **`fp8_e4m3fn_bf16_block_scale`**: Dynamic activation quantization.
- **`..._static_activation`**: Static activation scales (requires calibration).

## ROCm / RDNA3 (gfx1100) Compatibility

> [!WARNING]
> **`q4f16_1` produces NaN on RDNA3 (gfx1100)**
> The float16 accumulation in softmax can overflow to NaN on RDNA3 GPUs.
> The CPU sampler then crashes with: `Possibly prob distribution contains NAN`.

### Recommended for RDNA3 (RX 7900 XTX / gfx1100)

| Mode | Why |
|------|-----|
| **`q4f32_1`** | ✅ Safe — float32 accumulation prevents NaN overflow |
| **`q0f32`** | ✅ Safe — no quantization, full precision |
| **`q4bf16_1`** | ⚠️ May work — bfloat16 has wider exponent range than fp16 |
| **`q4f16_1`** | ❌ NaN crash on RDNA3 in softmax sampling |
| **`q4f16_0`** | ❌ Same NaN issue as q4f16_1 |

### Recommended for CDNA (MI250X / MI300X)

All modes should work. FP8 modes (`e4m3`, `e5m2`, block-scale) require MI300X.

## Bits Per Parameter (approximate)

| Mode | Bits/param | Relative size vs fp16 |
|------|-----------|----------------------|
| `q3f16_1` | ~3.5 | 0.22× |
| `q4f16_1` / `q4f32_1` | ~4.5–5.0 | 0.28–0.31× |
| `q4f16_2` | ~5.5 | 0.34× |
| `q0f16` | 16 | 1.0× |
| `q0f32` | 32 | 2.0× |

## CLI Usage

```bash
# Convert weights
python -m mlc_llm convert_weight \
    --model-type qwen2 --quantization q4f32_1 --device rocm \
    -o /path/to/output /path/to/hf-model

# Generate config (required before compile)
python -m mlc_llm gen_config \
    --model-type qwen2 --quantization q4f32_1 --conv-template qwen2 \
    -o /path/to/output /path/to/hf-model

# Compile model library
python -m mlc_llm compile \
    --quantization q4f32_1 --device rocm \
    -o /path/to/output/model-rocm.so /path/to/output

# Serve
python -m mlc_llm serve /path/to/output --device rocm --port 50080
```
