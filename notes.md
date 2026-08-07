model                                      TTFT   TPS      tokens  total
google-antigravity/tab_flash_lite_preview  355ms  274.7/s  512     1.9s
google-antigravity/gemini-3.6-flash        597ms  257.9/s  508     2.0s
google-antigravity/gemini-3-flash          719ms  250.3/s  651     2.6s
google-antigravity/gemini-2.5-flash        544ms  214.5/s  506     2.4s
deepseek/deepseek-v4-flash                 913ms  97.6/s   512     5.2s
deepseek/deepseek-v4-pro                   911ms  45.6/s   512     11.3s
google-antigravity/claude-opus-4-6         2.4s   37.0/s   2355    1m3s


+ change to better model, rememver last review.
+ sandbox-ctl: check const fileExists = (path: string) => path === "/run/user/1000/bus";

+ transform local-reranking into multi engine like local-embedding. make a hindsight reranking benchmark, 8k,8k
+ hindsight: documented full export/db-reset/re-import workflow for switching embedding+reranker models (see research/hindsight-import-export-reconfiguration.md)
+ refactor local-benchmark:+ chat, embedding, rerank engines (--engines all default), skip the combined code paths for now, is brittle
+ embedding: perplexity-ai/pplx-embed-context-v1-0.6b
  + pplx-embed-v1 and pplx-embed-context-v1 natively produce unnormalized int8-quantized embeddings. Ensure that you compare them via cosine similarity.
+ local-stt and local-tts: we installed python-faster-whisper , sherpa-onnx , and made crispasr. test and integrate if working good enough as stt and tts
+ find suiting models, test kokoro
+ local-chat: add fim warmup on benchmark, fix fim benchmark
+ reconsile roles and commands: eg. debugging, git-master, review-work, ulw-plan


+ Models

  https://huggingface.co/Godelaune/Kokoro-82M-ONNX-German-Martin
  https://huggingface.co/Yiivgeny/parakeet-tdt-0.6b-v3-sherpa-onnx-fp16
  https://huggingface.co/Supertone/supertonic
  https://huggingface.co/csukuangfj/Inflect-Nano-v2-ONNX
  https://huggingface.co/kikiri-tts/kikiri-german-victoria
  https://huggingface.co/kikiri-tts/kikiri-german-martin
  https://huggingface.co/Godelaune/Kokoro-82M-ONNX-German-Martin
  https://huggingface.co/cryptomilk/kokoro-german-kerstin

+ look into
  + https://github.com/mvanhorn/printing-press-library/tree/main/library/developer-tools/agent-desktop
  + https://github.com/mvanhorn/printing-press-library/tree/main/library/commerce/amazon-orders
  + https://github.com/mvanhorn/printing-press-library/tree/main/library/media-and-entertainment/archive-is
  + https://github.com/mvanhorn/printing-press-library/tree/main/library/travel/booking-com
  + https://github.com/mvanhorn/printing-press-library/tree/main/library/developer-tools/domain-goat
  + https://github.com/mvanhorn/printing-press-library/tree/main/library/payments/kalshi
  + https://github.com/mvanhorn/printing-press-library/tree/main/library/payments/robinhood
  + https://github.com/mvanhorn/printing-press-library/tree/main/library/marketing/trendhunter
  + https://github.com/mvanhorn/printing-press-library/tree/main/library/media-and-entertainment/wikipedia
  + https://github.com/mvanhorn/printing-press-library/tree/main/library/media-and-entertainment/youtube
  + https://github.com/mvanhorn/last30days-skill


+ look into
  https://github.com/RUC-NLPIR/DeepAgent
  https://github.com/google/mantis/
  https://github.com/simonucl/PolySkill
  https://github.com/itigges22/ATLAS
  https://github.com/router-for-me/CLIProxyAPI
  https://github.com/Arize-ai/phoenix

mcp and other interesting

  https://github.com/xberg-io/xberg
  https://github.com/lucasjinreal/Crane
  https://github.com/memvid/memvid

