# Active AI Assistants: Weekly Development Activity

This document tracks repository activity, commit counts, merge frequency, and release cycles for active assistant projects.

---

#### 📊 Summary of Last 7 Days Activity (June 21, 2026 – June 28, 2026)

<!-- START_TABLES -->
#### Repository Overview & Package Status
| Assistant Repo | Stars | Forks | Main Branch | Last Commit | Installed Pkg | Commits Since Pkg | Status |
| :--- | :---: | :---: | :---: | :---: | :--- | :---: | :---: |
| **zeroclaw** | 32,074 | 4,775 | `master` | 2026-06-28 | `zeroclaw-git` @ `0.8.2.r43.g97f8782ed-1` | 18 | **Highly Active** |
| **ironclaw** | 12,485 | 1,465 | `main` | 2026-06-28 | `ironclaw-git` @ `ironclaw_skill_learning.v0.1.0.r21.g4f28feb-1` | 61 | **Highly Active** |
| **librefang** | 315 | 65 | `main` | 2026-06-27 | — | — | **Highly Active** |
| **hermes-agent** | 204,588 | 36,853 | `main` | 2026-06-28 | — | — | **Highly Active** |
| **nanobot** | 44,812 | 7,901 | `main` | 2026-06-27 | — | — | **Highly Active** |
| **picoclaw** | 29,513 | 4,252 | `main` | 2026-06-26 | `picoclaw-git` @ `0.3.0.nightly.20260622.287853ab-1` | 27 | **Active** |
| **nanoclaw** | 30,015 | 12,897 | `main` | 2026-06-26 | `nanoclaw-git` @ `r1866.9bb69c0e5-1` | 7 | **Active** |

#### Weekly Activity Metrics (Human vs Bot)
| Assistant Repo | Commits / Week | Lines Added (Human/Bot) | Lines Deleted (Human/Bot) | Merges (Last Wk) | Releases/Tags (Last Wk) | Avg Commits/Wk (4 Wks) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **zeroclaw** | **188** / 0 | 49.8k / 0 | 223.4k / 0 | 0 | 1 | 163.8 |
| **ironclaw** | **98** / 2 | 118.9k / 1.7k | 34.1k / 941 | 0 | 1 | 126.0 |
| **librefang** | **53** / 10 | 15.3k / 338 | 7.9k / 340 | 0 | 4 | 63.0 |
| **hermes-agent** | **869** / 0 | 151.6k / 0 | 33.9k / 0 | 117 | 0 | 731.5 |
| **nanobot** | **128** / 1 | 11.5k / 11 | 4.6k / 0 | 0 | 1 | 123.8 |
| **picoclaw** | **15** / 5 | 275 / 140 | 79 / 123 | 21 | 0 | 36.0 |
| **nanoclaw** | **9** / 2 | 1.1k / 2 | 82 / 2 | 12 | 0 | 32.5 |
<!-- END_TABLES -->

---

## 🔍 Repository Breakdown

> [!NOTE]
> The contributor lists and activity metrics for each repository below are compiled according to commits from the last 7 days.


### ZeroClaw (`zeroclaw-labs/zeroclaw`)
<!-- START_BD_ZEROCLAW -->
* **Status**: Highly Active (Total: 188 commits [188 H / 0 B], 1 tag/release in the last week). Lines added/deleted: +49.8k/-223.4k (Human), +0/-0 (Bot). **18 commits since installed 0.8.2.r43.g97f8782ed-1 (ref=97f8782ed).**
* **Contributors (according to last 7 days commits)** (Total: 34 Humans, 0 Bots):
  - **Top Humans**:
    - `Dan Gilles <dfgilles@uchicago.edu>` (Human): 52 commits, +12.3k/-1.5k lines
    - `Shane Engelman <contact@shane.gg>` (Human): 28 commits, +9.8k/-218.1k lines
    - `Marc Collins <marc@nnet.tech>` (Human): 20 commits, +13.3k/-2.6k lines
    - `Alix-007 <li.long15@xydigit.com>` (Human): 11 commits, +605/-2 lines
    - `wangmiao0668000666 <wang.miao86@xydigit.com>` (Human): 9 commits, +2.8k/-131 lines
    - `Jason Perlow <jperlow@gmail.com>` (Human): 8 commits, +1.3k/-162 lines
    - `pick-cat <huang.ting3@xydigit.com>` (Human): 5 commits, +364/-4 lines
    - `JordanTheJet <morepencils@gmail.com>` (Human): 5 commits, +600/-74 lines
    - `ConYel <18070323+ConYel@users.noreply.github.com>` (Human): 4 commits, +593/-102 lines
    - `llagy009 <llagy009@163.com>` (Human): 4 commits, +48/-0 lines
<!-- END_BD_ZEROCLAW -->
<!-- START_RF_ZEROCLAW -->
* **Recent Focus**:
  - `3f87e1d6` ci(release): build release artifacts from the canonical feature registry (#8343)
  - `be5f17c6` fix(windows): share cmd shell command construction (#8247)
  - `aa9e20c5` docs(tools): document relationship memory workflows (#8263)
  - `b46b3016` fix(self_test): correct comment numbering in run_full function (#8212)
  - `f4cee1d0` test(eval): cover trace case parsing and suite loading (#8252)
  - `ca080ca8` fix(cli): add confirmation feedback after secret prompt input (#7856)
  - `565a2cee` test(tools): cover pushover notification shape overlap (#8356)
  - `19bcbe56` docs(mdbook): escape generated CLI placeholders (#8204)
  - `6d2ce034` fix(provider): cool down rate-limited fallback entries (#8317)
  - `48ce4ffe` fix(runtime): forward narration emitted after a native tool call (#8329)
  - `78067a86` fix(agent/loop-detector): do not count failed tool results as "no progress" (#8213)
  - `542a0dd9` docs(labels): document ACP channel label (#8406)
  - `f6650b01` test(tools): cover report template substitution safety and html escaping (#8270)
  - `8d841c77` test(tools): cover email_imap TLS close_notify detection (#8346)
  - `7de78002` fix(ci): defer stable-pointer tag check to deploy time (#8344)
  - `4fbec3e4` feat(acp): add opt-in MCP support for standalone ACP sessions (#8237)
  - `d4005151` feat(sop): out-of-band approval plane with fail-closed timeout and PriorityBased gate fix (#8304)
  - `7198b178` fix(zerocode): render only the viewport in long sessions (#8330)
<!-- END_RF_ZEROCLAW -->
### IronClaw (`nearai/ironclaw`)
<!-- START_BD_IRONCLAW -->
* **Status**: Highly Active (Total: 100 commits [98 H / 2 B], 1 tag/release in the last week). Lines added/deleted: +118.9k/-34.1k (Human), +1.7k/-941 (Bot). **61 commits since installed ironclaw_skill_learning.v0.1.0.r21.g4f28feb-1 (ref=4f28feb).**
* **Contributors (according to last 7 days commits)** (Total: 11 Humans, 1 Bots):
  - **Top Humans**:
    - `firat.sertgoz <firat.sertgoz@near.ai>` (Human): 32 commits, +26.0k/-6.7k lines
    - `Henry Park <henrypark133@gmail.com>` (Human): 17 commits, +31.9k/-7.2k lines
    - `jinxin <106428113+italic-jinxin@users.noreply.github.com>` (Human): 14 commits, +19.1k/-7.7k lines
    - `Illia Polosukhin <ilblackdragon@gmail.com>` (Human): 9 commits, +11.7k/-1.3k lines
    - `Robert Yan <46699230+think-in-universe@users.noreply.github.com>` (Human): 9 commits, +9.6k/-3.2k lines
    - `Benjamin Kurrek <57506486+BenKurrek@users.noreply.github.com>` (Human): 6 commits, +6.5k/-4.5k lines
    - `Coffee <zjchen1234@foxmail.com>` (Human): 5 commits, +8.8k/-3.5k lines
    - `Josh Ford <thisisjoshford@gmail.com>` (Human): 2 commits, +190/-3 lines
    - `Emil Bogomolov <emil.bogomolov@near.ai>` (Human): 2 commits, +999/-83 lines
    - `loopstring <yutingytw@gmail.com>` (Human): 1 commits, +294/-29 lines
  - **Top Bots**:
    - `dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>` (Bot): 2 commits, +1.7k/-941 lines
<!-- END_BD_IRONCLAW -->
<!-- START_RF_IRONCLAW -->
* **Recent Focus**:
  - `79f9be3e` chore(webui-v2): pin frontend node tooling (#5370) (#5384)
  - `6a3b10fa` Reborn integration-test framework (slices 1–2): scripted-SDK seam + tool-call/egress + design (#5381)
  - `128e7444` build(deps): bump the everything-else group across 1 directory with 47 updates (#5271)
  - `ea85058f` fix hosted volume runtime startup (#5382)
  - `2fa0cb46` feat(reborn): external-tool Responses round-trip (Phase 4b-4f) (#5099)
  - `4c82051b` fix: default reborn calendar events to upcoming (#5363)
  - `28a4c9a5` fix(reborn): provider-backed OAuth token refresh on local-dev/hosted-single-tenant profiles (#5379)
  - `f0f46a52` [codex] Port Reborn Responses API input handling (#5347)
  - `5298504a` feat(approvals): default "Always allow eligible tools" to on (#5366)
  - `c8a51ada` [codex] Align Reborn runtime tool surface (#5346)
  - `1a01a094` [codex] test llm loop failures (#5367)
  - `0eccde57` feat(reborn): env-configurable turn-runner concurrency (0 = unlimited) (#5265)
  - `a1b7f80b` build(deps-dev): bump js-yaml in /docs/architecture-video (#4934)
  - `2fe061f3` fix(reborn): unblock parallel-thread sends and new chats during active runs (#5352)
  - `a16b67a2` test(e2e): add reborn webui legacy harness (#5345)
  - `667e3cc6` fix(ci): gate skills io/Read import to unix (fixes Clippy Windows ripple from #5325) (#5351)
  - `185ce889` fix(reborn): discourage disabled tool workarounds (#5307)
  - `f344180a` fix(webui-v2): anchor run failure messages (#5299)
  - `0e492365` fix(reborn): persist always-allow for shared registry tools (#5309)
  - `aeaee50e` fix(ci): green up main + cargo/non-cargo network resilience (#5325)
  - `535c29c3` Fix hosted-volume scoped tool service resolution (#5321)
  - `26a5f902` fix(reborn): deliver triggered Slack runs after settlement (#5318)
  - `f7c82f5b` fix(reborn): duplicate logs header (#5324)
  - `e2742bb9` [codex] harden agent loop chaos handling (#5296)
  - `0c79a2d2` Add hosted single-tenant volume profile (#5259)
  - `4e1e816b` Move legacy tests to nightly CI (#5308)
  - `c785ca2e` fix(ci): unblock main and cut flake (libsql feature, apt retry, fail-fast, .codegraph) (#5281)
  - `bc4cc6e5` fix(reborn): align external tool provider names (#5303)
  - `54ca2108` [codex] Type provider tool names at model protocol boundaries (#5292)
  - `7e191be3` feat(reborn): /v1/models, model validation, external-tool gate foundation (#5094)
  - `0c00929b` perf(reborn): batch durable event-log appends (write-behind coalescing) (#5257)
  - `e37772f9` fix(webui-v2): move active run logs link out of composer (#5284)
  - `6985e634` docs(reborn): design — native hot-store primitives on the unified RootFilesystem trait (#5269)
  - `e67882e5` fix(webui-v2): make logs page scrollable (#5278)
  - `46ed73f5` fix(filesystem): fold CAS put directory pre-check into one statement (3→1 round-trip) (#5255)
  - `031f2e2f` add a seam for download_file to extract binary docs (PDF/PPTX/DOCX/XLSX) as text (#4997)
  - `bf29e050` fix(reborn): treat parked Blocked* triggered runs as terminal-for-delivery (#5222)
  - `799eb154` fix(reborn): stop WASM execution from starving the tokio worker pool (#5206)
  - `24faee72` fix(turns): exempt certified skill content from prompt content denylist (#5169) (#5258)
  - `9ce47c4d` feat(reborn): expose user-scoped tool settings (#5256)
  - `afa54950` fix(reborn): keep approval gates visible on busy sends (#5241)
  - `ef729fc0` fix(triggers): recover stale claim-only fires (#5245)
  - `6af6b931` fix(webui): keep streamed chat responses in view (#5248)
  - `81dd13ab` fix(webui-v2): keep chat composer editable while running (#5235)
  - `92e77640` fix(reborn): persist approval-card always allow as tool settings (#5195)
  - `a38119f5` fix(reborn): chat timestamp hover actions (#5226)
  - `9632f909` [codex] Fix durable preview owner scope (#5230)
  - `fbb85eee` fix(reborn): show NEAR AI default base URL in provider card (#5217)
  - `c02f73da` fix(reborn): allow web ui logs for multi-tenancy users (#5199)
  - `163d594b` feat(reborn-webui): tool permissions + global auto-approve settings surface (#4960) (#5068)
  - `44f063d9` [codex] Persist hosted trigger access via filesystem (#5233)
  - `e8132ffb` [codex] durable runner lease sidecar (#5232)
  - `82dbb158` style(webui-v2): improve responsive sidebar behavior (#5183)
  - `a76ecb5c` refactor(reborn): clean up capability activity lifecycle (#5145)
  - `8b873673` fix(reborn): release Slack admission permit once inbound is durably accepted (#5225)
  - `0f08d5e5` [codex] fix recurring trigger poller hang (#5202)
  - `3cbde9b2` fix(reborn): bound NEAR AI provider calls below the runner lease (#5204)
  - `dbdbbd39` feat(reborn): wire local service lifecycle backend (#4860)
  - `25922c1b` fix(reborn): repair dead failure-category arms in failure-explanation path (#5207)
  - `cecd9589` fix(reborn): populate provider on runtime auth-required gates (#5180)
  - `ecff564a` feat(memory): model memory as a userland extension (#3537) (#5163)
<!-- END_RF_IRONCLAW -->
### Hermes Agent (`NousResearch/hermes-agent`)
<!-- START_BD_HERMES_AGENT -->
* **Status**: Highly Active (Total: 869 commits [869 H / 0 B], 0 tags/releases in the last week). Lines added/deleted: +151.6k/-33.9k (Human), +0/-0 (Bot).
* **Contributors (according to last 7 days commits)** (Total: 175 Humans, 0 Bots):
  - **Top Humans**:
    - `Teknium <127238744+teknium1@users.noreply.github.com>` (Human): 174 commits, +25.2k/-14.0k lines
    - `teknium1 <127238744+teknium1@users.noreply.github.com>` (Human): 129 commits, +10.1k/-1.6k lines
    - `Brooklyn Nicholson <brooklyn.bb.nicholson@gmail.com>` (Human): 110 commits, +44.7k/-8.5k lines
    - `kshitijk4poor <82637225+kshitijk4poor@users.noreply.github.com>` (Human): 53 commits, +5.1k/-794 lines
    - `ethernet <arilotter@gmail.com>` (Human): 28 commits, +3.4k/-2.8k lines
    - `xxxigm <tuancanhnguyen706@gmail.com>` (Human): 27 commits, +2.4k/-134 lines
    - `liuhao1024 <sunsky.lau@gmail.com>` (Human): 19 commits, +2.4k/-117 lines
    - `Ben Barclay <ben@nousresearch.com>` (Human): 17 commits, +3.4k/-148 lines
    - `Ben <ben@nousresearch.com>` (Human): 17 commits, +5.3k/-164 lines
    - `konsisumer <der@konsi.org>` (Human): 11 commits, +1.5k/-51 lines
<!-- END_BD_HERMES_AGENT -->
<!-- START_RF_HERMES_AGENT -->
* **Recent Focus**:
  - `135f23516` docs: fix incorrect web search instructions
  - `546193aa6` fix(install): time-box desktop + node-deps installs so a stalled download self-heals (#39219)
  - `c1c179a23` fix(security): redact secrets in background process + foreground env-dump output (#43025) (#54149)
  - `d5ba374c0` fix(telegram): detect wedged getUpdates consumer via pending_update_count
  - `822b71cbf` docs: add infographic for #43083 secret-redaction fix
  - `bbe1bf404` fix(agent): stop redacting tool-call args in history; fix auth-header quote-eating
  - `204a67f0c` fix(kanban): retry write_txn on transient SQLITE_BUSY
  - `90c1dc049` test(kanban): cover write_txn BUSY retry (currently failing)
  - `9844243b1` fix(gateway): gate quick_commands through slash access policy
  - `6d879d486` fix(dashboard): close PTY WebSocket on child EOF to stop FD leak (#54028) (#54123)
  - `7ef04ae7a` fix(browser): close eval return-value SSRF bypass (sibling of #44731)
  - `0ae619608` fix(browser): allow local sidecar sessions to bypass SSRF guard
  - `48f5c4259` fix(browser): extend private-network guard to browser_vision
  - `7a6fe9bbf` fix(browser): block snapshot from eval-navigated private pages
  - `7c0a5def5` fix(memory/holographic): close DB connection on shutdown instead of leaking to GC (#54133)
<!-- END_RF_HERMES_AGENT -->
### NanoBot (`HKUDS/nanobot`)
<!-- START_BD_NANOBOT -->
* **Status**: Highly Active (Total: 129 commits [128 H / 1 B], 1 tag/release in the last week). Lines added/deleted: +11.5k/-4.6k (Human), +11/-0 (Bot).
* **Contributors (according to last 7 days commits)** (Total: 17 Humans, 1 Bots):
  - **Top Humans**:
    - `chengyongru <chengyongru.ai@gmail.com>` (Human): 37 commits, +3.1k/-1.9k lines
    - `Xubin Ren <52506698+Re-bin@users.noreply.github.com>` (Human): 26 commits, +3.8k/-567 lines
    - `chengyongru <2755839590@qq.com>` (Human): 24 commits, +3.1k/-1.9k lines
    - `axelray-dev <110029405+axelray-dev@users.noreply.github.com>` (Human): 20 commits, +501/-97 lines
    - `michaelxer <michaelxer@users.noreply.github.com>` (Human): 3 commits, +124/-25 lines
    - `Zhou <32321321@qq.com>` (Human): 3 commits, +176/-13 lines
    - `zpljd258 <11162658+zpljd258@users.noreply.github.com>` (Human): 2 commits, +118/-1 lines
    - `Ilya Gusev <phoenixilya@gmail.com>` (Human): 2 commits, +95/-36 lines
    - `hyoukadev <ziv3@outlook.com>` (Human): 2 commits, +32/-7 lines
    - `w.antar <antarwael189@gmail.com>` (Human): 2 commits, +59/-7 lines
  - **Top Bots**:
    - `NanoBot <nanobot@local>` (Bot): 1 commits, +11/-0 lines
<!-- END_BD_NANOBOT -->
<!-- START_RF_NANOBOT -->
* **Recent Focus**:
  - `c90e4330` fix(session): guard lossy migration by stored key
  - `3ce77633` fix(session): add _decode_storage_key for corrupt-file repair in list_sessions
  - `00a907c4` fix(session): split safe_key and _storage_key to fix WebUI coupling (#4533)
  - `cf2f5896` fix(session): prevent save from writing to legacy lossy path, add collision tests (#4533)
  - `463f5367` fix: prevent session key collision on disk (#4057)
  - `00a7de01` fix: stringify Anthropic typeless blocks as JSON
  - `efb792ff` fix: validate content block type in Anthropic assistant blocks (#4060)
  - `d8601478` test: cover stream-id delta coalescing
  - `66fc5442` fix: include _stream_id in stream delta coalescing key (#4063)
  - `6a27c262` test: cover non-stream duplicate tool call ids
  - `3ca82ea8` fix: deduplicate tool call IDs in non-stream parser (#4059)
  - `47dcc61e` test(agent): fix flaky test_keeps_n_most_recent by ensuring sequential mtimes
  - `2bf111f4` fix(exec): remove ad-hoc shell comment stripping from _guard_command
  - `aa6c1bf3` fix(exec): prevent allowPatterns bypass via chained commands and shell comments
  - `5281e672` fix(docker): repair whatsapp image build
<!-- END_RF_NANOBOT -->
### PicoClaw (`sipeed/picoclaw`)
<!-- START_BD_PICOCLAW -->
* **Status**: Active (Total: 20 commits [15 H / 5 B], 0 tags/releases in the last week). Lines added/deleted: +275/-79 (Human), +140/-123 (Bot). **27 commits since installed 0.3.0.nightly.20260622.287853ab-1 (ref=287853ab).**
* **Contributors (according to last 7 days commits)** (Total: 3 Humans, 1 Bots):
  - **Top Humans**:
    - `程智超0668000959 <cheng.zhichao@xydigit.com>` (Human): 9 commits, +68/-60 lines
    - `Alix-007 <li.long15@xydigit.com>` (Human): 5 commits, +202/-19 lines
    - `phoeagon <phoeagon@gmail.com>` (Human): 1 commits, +5/-0 lines
  - **Top Bots**:
    - `dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>` (Bot): 5 commits, +140/-123 lines
<!-- END_BD_PICOCLAW -->
<!-- START_RF_PICOCLAW -->
* **Recent Focus**:
  - `2cdfadaa` test(utils): explicitly ignore resp.Body.Close() errors in tests
  - `0eb721ff` fix(health): explicitly ignore json.Encode errors in HTTP handler responses
  - `14c9a1f1` fix(membench): explicitly ignore resp.Body.Close() error after io.ReadAll
  - `500ce724` fix(onebot): explicitly ignore resp.Body.Close() error after websocket dial
  - `583d9e1e` fix(updater): explicitly ignore resp2.Body.Close() error after io.ReadAll
  - `1bd2e845` fix(channels): explicitly ignore resp.Body.Close() errors in websocket dial cleanup
  - `36d72a01` fix(gateway): guard startup info assertions
  - `9287df41` build(deps): bump github.com/mymmrac/telego from 1.9.0 to 1.10.0
  - `ae81ae93` build(deps): bump fyne.io/systray from 1.12.1 to 1.12.2
  - `e4bda8c4` build(deps): bump github.com/line/line-bot-sdk-go/v8
  - `34002215` build(deps): bump modernc.org/sqlite from 1.51.0 to 1.53.0
  - `7ee4ee3b` fix: correct indentation in shell.go and updater.go for gci linter
  - `62a2b001` fix: explicitly ignore Close() errors in error paths and retry loops
  - `d6371fcb` fix(agent): close base64 encoder on io.Copy error path
  - `f53e6e68` fix(model): avoid shadowing response error
<!-- END_RF_PICOCLAW -->
### NanoClaw (`nanocoai/nanoclaw`)
<!-- START_BD_NANOCLAW -->
* **Status**: Active (Total: 11 commits [9 H / 2 B], 0 tags/releases in the last week). Lines added/deleted: +1.1k/-82 (Human), +2/-2 (Bot). **7 commits since installed r1866.9bb69c0e5-1 (ref=9bb69c0e5).**
* **Contributors (according to last 7 days commits)** (Total: 7 Humans, 1 Bots):
  - **Top Humans**:
    - `Gabi Simons <gabi@nanoco.ai>` (Human): 2 commits, +37/-27 lines
    - `Moshe Krupper <moshekrupper@Moshes-MacBook-Pro.local>` (Human): 2 commits, +620/-26 lines
    - `Christophe Benoist <christophe.benoist@gmail.com>` (Human): 1 commits, +1/-2 lines
    - `Omri Maya <omri@nanoco.ai>` (Human): 1 commits, +52/-0 lines
    - `robbyczgw-cla <robbyczgw-cla@users.noreply.github.com>` (Human): 1 commits, +97/-0 lines
    - `Amit Shafnir <amit@nanoco.ai>` (Human): 1 commits, +256/-3 lines
    - `Koshkoshinsk <daniel.milliner@gmail.com>` (Human): 1 commits, +35/-24 lines
  - **Top Bots**:
    - `github-actions[bot] <github-actions[bot]@users.noreply.github.com>` (Bot): 2 commits, +2/-2 lines
<!-- END_BD_NANOCLAW -->
<!-- START_RF_NANOCLAW -->
* **Recent Focus**:
  - `797491d` fix(migrate-v2): don't SELECT is_main from v1 registered_groups
  - `2df7544` chore: bump version to 2.1.21
  - `bfb309b` chore: bump version to 2.1.20
  - `1d6bba4` feat(container): per-container CPU/memory limits (opt-in)
  - `520ec44` feat: add /learn skill — distill or refine a reusable skill from anything
  - `2ac7809` feat(agent-to-agent): clarify the a2a gate approval prompt
  - `e8148bc` feat(approvals): reject-with-reason — relay an optional decline reason to the agent
<!-- END_RF_NANOCLAW -->
### LibreFang (`librefang/librefang`)
<!-- START_BD_LIBREFANG -->
* **Status**: Highly Active (Total: 63 commits [53 H / 10 B], 4 tags/releases in the last week). Lines added/deleted: +15.3k/-7.9k (Human), +338/-340 (Bot).
* **Contributors (according to last 7 days commits)** (Total: 5 Humans, 2 Bots):
  - **Top Humans**:
    - `Evan <suzukaze.haduki@gmail.com>` (Human): 37 commits, +4.6k/-5.5k lines
    - `Павло <pavvers1@gmail.com>` (Human): 5 commits, +8.1k/-2.2k lines
    - `maoxin1234 <875408344@qq.com>` (Human): 5 commits, +1.6k/-159 lines
    - `Paco Navarrete <paco.j.navarrete@gmail.com>` (Human): 4 commits, +644/-18 lines
    - `Vignesh Jagadeesh <vignesh.nrfs@gmail.com>` (Human): 2 commits, +425/-33 lines
  - **Top Bots**:
    - `github-actions[bot] <41898282+github-actions[bot]@users.noreply.github.com>` (Bot): 5 commits, +75/-67 lines
    - `dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>` (Bot): 5 commits, +263/-273 lines
<!-- END_BD_LIBREFANG -->
* **Note**: LibreFang is a community fork of the former `RightNow-AI/openfang` repository, which had **17,623 stars** and **2,252 forks** before going stale.
<!-- START_RF_LIBREFANG -->
* **Recent Focus**:
  - `fbb5d5ca` docs: update contributors and star history (#6344)
  - `69e685aa` ci(contributors): enable auto-merge instead of forcing --admin (#6340)
  - `bebc950f` ci(mobile): put NDK bin on PATH so openssl-src finds the legacy ranlib symlink (#6338)
  - `12c3daf4` fix(deps): bump pdf-extract 0.10→0.12 to patch lopdf RUSTSEC-2026-0187 (#6339)
  - `f5055cad` docs: update contributors and star history (#6337)
  - `5484593e` ci(mobile): symlink legacy NDK binutils so vendored OpenSSL cross-compiles for Android (#6335)
  - `d522fea4` release: v2026.6.26-beta.24 (#6333)
  - `71cac88c` test(llm-drivers): pin claude_code resolved-model parsing (#6318) (#6331)
  - `359a97c6` fix(ofp): accept empty-recipient HMAC so bootstrap_peers can connect (#6330)
  - `2f27879d` feat(web): add Ukrainian localization and extract hardcoded copy (#6312)
  - `cbd8bf4e` feat: add AUR packaging for Arch Linux (#6314)
  - `43db218d` fix(channels): describe inbound images on the debounced channel path (#6323)
  - `d01cc691` feat(dashboard/workflows): surface run params, errors, and one-click re-run (#6324)
  - `a8116376` feat(dashboard/agents): allow a custom model id when editing an agent (#6327)
  - `3ebec2a4` fix(runtime): block separator-less secret env names from WASM guests (#6316)
<!-- END_RF_LIBREFANG -->
---
## 📋 Instruction Guide: Recreating this Analysis

**Fully Automated Update**: You can run the automation script `scripts/update-activity.py` with the `--write` (or `-w`) flag to automatically pull all repository updates, calculate the statistics, and optionally write the updated tables directly back into this file:
```bash
python scripts/update-activity.py [--write]
```
