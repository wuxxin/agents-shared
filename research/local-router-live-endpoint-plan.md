# Plan: OpenAI Realtime WebRTC endpoint in local-router.py (`live.endpoint`)

Goal: `scripts/local-router.py` serves the server side of omp's **custom live voice endpoint**, so interactive omp `/live` calls run fully on this box (llama.cpp router + LSTT/LTTS backends) instead of Codex. Pulse/OMP_VOICE stays as-is: bridge notification audio keeps going through the tts device → `/v1/audio/speech`; this plan adds only the interactive call transport and shares the same backends. No OmpHooksBridge changes.

All protocol facts pinned to the installed source checkout `submodules/aur-packages/oh-my-pi-git/src/oh-my-pi` @ d4ebe4d (cite paths relative to `packages/coding-agent/src/`).

## Contract omp enforces (server must satisfy)

Settings side (omp):
- `live.endpoint` = http(s) base URL, e.g. `http://127.0.0.1:21080/v1`; empty = Codex (`live/settings.ts:35`, validate at :24-32).
- `live.apiKey` optional bearer, resolved literal/env-name/`!command`, sent ONLY to this endpoint (`live/settings.ts:49`, `live/transport.ts:41-52,156`). Router has no auth today → leave unset.
- `live.voice` free string delivered in session config; "a custom live endpoint may take other names" (`live/settings.ts:9-18`) → map to kokoro voice ids (host policy: en `af_heart`, de `df_victoria`).

Signaling (`live/transport.ts:356-401`):
- `POST {base}/realtime/calls`, `Content-Type: application/sdp`, body = bare SDP offer, `Authorization: Bearer …` when key set.
- Response: 2xx, body = SDP answer text (non-empty), `Location:` header whose LAST path segment is the call id (any string; no `rtc_` pattern requirement for custom endpoints — `parseLiveEndpointCallId`, :143).
- Only same-origin 307/308 redirects are followed; proxy scope `PI_PROXY_LIVE`.

Sideband (`live/transport.ts:133-137,403+`):
- WebSocket to `{base as ws(s)}/realtime?call_id=<id>` with the same bearer header. Connect retried 5× (200ms backoff).
- On connect the client immediately sends `{"type":"realtime","instructions":…,"audio":{"output":{"voice":…}},"delegation":{"type":"client"}}` (`live/protocol.ts:26-33`, sent in transport `#connect`).

Server events the omp client consumes (sideband JSON; `live/protocol.ts:35-70`, handling at `live/controller.ts:331-352`):
- `{"type":"session.started","session":{"id":…}}` — required to unmute/set audio phase.
- `input_transcript.added` / `output_transcript.added` `{item:{text}}`; `turn.done {turn:{role:"user"|"assistant",transcript}}` → transcript UI.
- `delegation.created {item:{type:"delegation",target:"client",id,content:[{type:"input_text",text}]}}` → runs the real omp agent session turn (`controller.ts:354-378`).
- `error {message}`; `output_audio.delta` is IGNORED by the controller (:336) — audio out MUST ride the WebRTC RTP track, not WS.

Client→server messages the server should tolerate on the sideband: `session.update`, `session.context.append` / `delegation.context.append` (`{channel:"speakable"|"commentary",content:[{type:"input_text",text}]}`, ≤500 B chunks), `session.close` (`protocol.ts:36-49`).

Audio plane: native WebRTC peer, one Opus audio track (offer from client; server answers with sendrecv) — full ICE/DTLS/SRTP on our side.

## Router facts today

- FastAPI + uvicorn, `LROUT_HOST=127.0.0.1`, `LROUT_PORT=21080` (:2848-2850), no auth, single process; service registry via `LROUT_{CHAT,STT,TTS,…}_{HOST,PORT}` + discovery (`available_services`, :256-337).
- `/v1/audio/transcriptions` STT proxy (:2571, path override `LROUT_STT_PATH`), `/v1/audio/speech` TTS proxy (:2598) — reuse both as the call's backends; chat routing via `model_to_service` + internal forward (:2460).
- No WebSocket routes yet; uvicorn supports them in-process (single worker is already the deployment).

## Design

Add a feature-gated module behind `LROUT_REALTIME=1`:

1. **Signaling route** `POST /v1/realtime/calls` — feed the SDP offer to an `aiortc.RTCPeerConnection` (deps: `python-aiortc` from AUR, keeps our shared-lib policy; PyPI wheel bundles its own opus). Create a sendonly Opus track, set remote description, create answer, return 201 + answer body + `Location: /v1/realtime/calls/<call_id>` (`uuid4`). Call registry = in-process dict (pid 1 process, fine).
2. **Sideband route** `GET /ws-as-WS /v1/realtime?call_id=` — FastAPI WebSocket; accept the client's `{"type":"realtime",…}` config (store voice/instructions), reply `session.started`. Route: `/v1/realtime` must be registered BEFORE the catch-all `@app.api_route("/{path:path}")` (:2829).
3. **Turn pipeline** per call: RTP→PCM frames → energy/silence VAD (~600 ms tail) → chunk WAV → internal STT (same code path as `/v1/audio/transcriptions`) → emit `input_transcript.added` + `turn.done{user}`; chat completion through the existing forwarder with a realtime system prompt → sentence-chunk → TTS via `/v1/audio/speech` backend → Opus-encode into the send track (pace by 20 ms frame clock) → emit `output_transcript.added` + `turn.done{assistant}`.
4. **Delegation mode (phase 3)**: instead of running our own LLM loop, after each user turn emit `delegation.created` with the transcript text; omp runs its real agent/tools session and appends results back via `session.context.append` chunks — we then speak them. This is what makes `/live` a true voice front for the agent; the protocol already defines it (`protocol.ts:31,40-45`).
5. **Ops**: `/health` gains `realtime` capability flag; Prometheus counter for calls/turns; 15-min idle call teardown (mirrors speech model unload policy); document in `assistants/*-ctl.md` README section when the router service env changes.

## Phases & acceptance

- P0 contract mock (throwaway, `scratch/`): pure-Python fake endpoint (echo SDP + fixed answer, WS accepts config, sends `session.started`) run against a real interactive omp → proves signaling/sideband/auth before any audio work.
- P1 one-turn: mic utterance → STT transcript events visible in omp UI; canned TTS reply audible through the call. Acceptance: full duplex audio + transcripts in `/live`.
- P2 loop: continuous VAD turns, barge-in (stop send track on new speech), model = router chat default (`LROUT_DEFAULT_MODEL` / strata alias `qwen3.8-flash-next`). Latency budget to measure: end-of-speech → first TTS byte ≤ 1.5 s target; record via `/metrics`.
- P3 delegation mode (agent-backed voice) + docs sync.

## Risks

- GIL/latency: router does tiktoken + sqlite usage work on shared process; audio pacing needs a steady 20 ms pump — keep the RTP sender in its own thread, no per-frame JSON.
- llama.cpp TTFB dominates turn latency (shared `maxInFlight=2` slots with main agents) — P2 must measure, consider a dedicated realtime model slot (`LROUT_REALTIME_MODEL`).
- VAD quality on energy-only is crude; acceptable for v1, silero-vad later.
- aiortc version drift: pin via AUR package in `submodules/aur-packages` if the distro package lags (check `python-aiortc` availability first).

## Config wiring (host side)

- omp settings: `live.endpoint: http://127.0.0.1:21080/v1`, `live.apiKey:` unset, `live.voice: af_heart` (en) — set per profile; offline mode works because `live.endpoint` names the voice server (`controller.ts:379-384`).
- Pulse/OMP_VOICE pipeline untouched: bridge notifications keep using the tts device; this endpoint only answers `/live` calls.
