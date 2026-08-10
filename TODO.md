+ sandbox-ctl: check const fileExists = (path: string) => path === "/run/user/1000/bus";
+ transform local-reranking into multi engine like local-embedding. make a hindsight reranking benchmark, 8k,8k
+ hindsight: documented full export/db-reset/re-import workflow for switching embedding+reranker models (see research/hindsight-import-export-reconfiguration.md)
+ refactor local-benchmark:+ chat, embedding, rerank engines (--engines all default), skip the combined code paths for now, is brittle
+ embedding: perplexity-ai/pplx-embed-context-v1-0.6b
  + pplx-embed-v1 and pplx-embed-context-v1 natively produce unnormalized int8-quantized embeddings. Ensure that you compare them via cosine similarity.
+ local-stt and local-tts: we installed python-faster-whisper , sherpa-onnx , and made crispasr. test and integrate if working good enough as stt and tts
+ find suiting models, test kokoro
+ local-chat: add fim warmup on benchmark, fix fim benchmark

