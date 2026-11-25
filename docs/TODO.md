# TODO

+ strata: redo optimization and integrate with launcher
+ local-chat-*: readd or make a new service for fim, fix fim benchmark
+ local-speech-to-text: add second engine, beside whisper.cpp use parakeet.cpp as second engine, with phonon multilingual 
https://huggingface.co/gradium/phonon-40m-multilingual/tree/main
+ local-reranking: transform into multi engine like local-embedding. make a reranking benchmark, 8k,8k
+ local-benchmark: refactor chat, embedding, rerank engines (--engines all default), skip the combined code paths for now, is brittle

+ sandbox-ctl: Dynamic host-side secret injection (`LAUNCHER_SECRETS`)
  + Add `LAUNCHER_SECRETS` array to app configuration (`.env`) for dynamic secret resolution on the host before sandbox launch.
  + Implement host-side resolution using `git-credential-keepassxc` (or companion script):
    - In-memory injection only: passes values via `--setenv KEY VALUE` (bwrap) / `Environment=KEY=VALUE` (systemd).
    - Never write or persist resolved plaintext secrets to disk or `.env` files.
    - Fail-safe abort: if access is denied or database is locked, exit launch with error code 1.
  + Provide standalone companion helper `scripts/kpxc-secret` for URI parsing (`kpxc://[group/]entry[:field]`, TOTP, custom `KPH:` fields, export, and run wrappers).
  + Update `cmd_cat`, `cmd_selftest`, and default `.env` template in `cmd_install` for `LAUNCHER_SECRETS`.

+ docs: Migrate from Material for MkDocs (EOL May 5, 2027) to **Zensical** (https://zensical.org/docs/compatibility/mkdocs/migration/)
  + Tested `zensical 0.1.3` with existing `mkdocs.yml` (`-c -s`): builds cleanly in `1.74s` with 0 warnings; Mermaid, search, and `docs/stylesheets/extra.css` work out of the box.
  + Staying on MkDocs Material for now because Zensical `0.1.3`'s `include-markdown` adapter ignores `rewrite-relative-urls` (so `docs/...` links in `../README.md` included via `docs/index.md` emit `href="docs/..."` and 404 on the homepage). Revisit once Zensical implements relative URL rewriting or `docs/index.md` is decoupled from `README.md`.
