# TEI Reranker Research Notes - Qwen3-Reranker-0.6B

This document details our findings, limitations, and architectural constraints discovered when attempting to serve `Qwen3-Reranker-0.6B` using Text Embeddings Inference (TEI) on AMD ROCm.

## Summary of Findings

Generative rerankers like **`Qwen3-Reranker-0.6B`** cannot be served using TEI's sequence classification backend. They must instead be run using `llama-server` (as implemented in `local-rerank.sh`), which supports generative ranking natively via `--pooling rank`.

---

## Technical Details & TEI Impediment

### 1. Model Type Misclassification
By default, running `text-embeddings-router` on this model fails with:
`Error: The --pooling arg is not set and we could not find a pooling configuration` or `Failed to parse sentence_bert_config.json: missing field max_seq_length`.

If you bypass this by manually creating a configuration workspace and setting `max_seq_length`, the TEI Rust router rejects `/rerank` queries with:
`Backend error: model is not a re-ranker model`

* **Root Cause:** In the model's `config.json`, the architectures list is `["Qwen3ForCausalLM"]`. Because it does not end with `"Classification"`, the Rust router defaults to treating it as an `Embedding` model type instead of a `Classifier`/`Reranker` type.

### 2. The Classification Head Workaround & Failure
We attempted to force classification mode by making a writable directory copy of the config files (`/tmp/Qwen3-Reranker-0.6B`) and modifying `config.json`:
- Changed `architectures` to `["Qwen3ForSequenceClassification"]`
- Injected `id2label: {"0": "score"}` and `label2id: {"score": 0}` mappings.

This successfully fooled the Rust router into matching the classifier/reranker path, and the Python backend loaded the model under `AutoModelForSequenceClassification`. However:

* **The Missing Weight Crash:** During load, `transformers` reported:
  `score.weight | MISSING`
* **Why it's missing:** Generative rerankers do not have a dedicated sequence classification linear layer (`score.weight` or similar) in `model.safetensors`. Instead, they compute relevance logits by checking the next-token probabilities of `"yes"` and `"no"` at the end of the prompt.
* **The Result:** Because `AutoModelForSequenceClassification` did not find `score.weight` in the safetensors, it initialized it with **random weights**. This caused the model to produce completely random relevance scores, rendering the reranking useless.

---

## The Correct Path: `llama-server`

Because `llama-server` has native support for generative sequence classification (ranking), it is the correct engine for GGUF versions of this model:
* **Command:** `llama-server --model Qwen3-Reranker-0.6B.Q4_K_M.gguf --pooling rank`
* **API:** Exposes a Cohere-compatible `/v1/rerank` endpoint.
* **Validation:** Successfully tested and verified using `./local-rerank.sh test` (which scored the correct vacuum speed of light document top-1 with a score of `0.9857`).

---

## Reranker Alternatives & Comparative Analysis

Below is a comparison of alternative reranking models evaluated for local deployment:

| Metric / Parameter | `Qwen3-Reranker-0.6B` (Default) | `BAAI/bge-reranker-v2-m3` | `jinaai/jina-reranker-v2-base-multilingual` |
| :--- | :--- | :--- | :--- |
| **Model Type** | Generative Causal LM | Cross-Encoder (Sequence Classification) | Cross-Encoder (Sequence Classification) |
| **Parameters** | `0.6 Billion` (570M) | `567 Million` | `278 Million` (Compact) |
| **Context Window** | `40,960` tokens | `8,192` tokens | `1,024` tokens (sliding window chunking) |
| **Deployment Engine** | `llama-server --pooling rank` | TEI `/rerank` (Rust backend) | TEI `/rerank` (Python fallback) |
| **Format & Disk Size** | `1.2 GB` (fp16), `360 MB` (Q4 GGUF) | `1.14 GB` (fp16 Safetensors) | `560 MB` (fp16 Safetensors) |
| **GPU VRAM Baseline** | **~450 MB** (Q4_K_M GGUF) | **~1.2 GB** (fp16) | **~600 MB** (fp16) |
| **VRAM under Load** | **Scales with KV cache**. ~600–800 MB active VRAM with 8K context. | **Highly Stable**. No KV cache. ~1.3 GB total VRAM under load. | **Very Low**. ~700–800 MB active VRAM under load. |
| **German Support** | **Good**. Standard Qwen3 baseline. | **Excellent**. Highly optimized cross-lingual ranking. | **Outstanding**. Berlin-tuned with exceptional German vocabulary coverage. |

### Recommendations
* **For best German precision / latency:** **`jina-reranker-v2-base-multilingual`** is outstanding, highly compact, uses very little VRAM, and runs under TEI.
* **For long context (up to 40K) and low VRAM footprint:** Running the GGUF version of **`Qwen3-Reranker-0.6B`** via `llama-server` is extremely efficient, but slower under high concurrency due to sequential KV cache decoding.
