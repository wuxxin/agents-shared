+ local-stt and local-tts: we installed python-faster-whisper , sherpa-onnx , and made crispasr. test and integrate if working good enough as stt and tts
  + find suiting models, test kokoro

embedding: perplexity-ai/pplx-embed-context-v1-0.6b
pplx-embed-v1 and pplx-embed-context-v1 natively produce unnormalized int8-quantized embeddings. Ensure that you compare them via cosine similarity.

rerank: jinaai/jina-reranker-v3


+ local-chat: add additional gemma26/4 llm to choose.
+ local-chat: add fim warmup on benchmark, fix fim benchmark
+ opencode: add opencode llm proxy service sidecar
