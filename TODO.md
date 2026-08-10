+ readd mtp
+ add second engine to local-speech-to-text, beside whisper.cpp use parakeet.cpp as second engine, with https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3 in q8 as model.
+ add second engine to local-text-to-speech, beside qwen3-tts, check what we already have in aur-packages or installed like  sherpa-onnx, and checkout: https://huggingface.co/mudler/magpie-tts.cpp-gguf if this makes any sense for us.
  + find suiting models for target engine, look in model-research, for qwen3-tts replacement, esp german voices.
+ transform local-reranking into multi engine like local-embedding. make a hindsight reranking benchmark, 8k,8k
+ sandbox-ctl: check const fileExists = (path: string) => path === "/run/user/1000/bus";
+ hindsight: documented full export/db-reset/re-import workflow for switching embedding+reranker models (see research/hindsight-import-export-reconfiguration.md)
+ refactor local-benchmark:+ chat, embedding, rerank engines (--engines all default), skip the combined code paths for now, is brittle
+ local-chat: add fim warmup on benchmark, fix fim benchmark
