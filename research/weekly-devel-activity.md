# Active AI Assistants: Weekly Development Activity

This document tracks repository activity, commit counts, merge frequency, and release cycles for active assistant projects.

---

#### 📊 Summary of Last 7 Days Activity (June 27, 2026 – July 04, 2026)

<!-- START_TABLES -->
#### Repository Overview & Package Status
| Assistant Repo | Stars | Forks | Main Branch | Last Commit | Installed Pkg | Commits Since Pkg | Status |
| :--- | :---: | :---: | :---: | :---: | :--- | :---: | :---: |
| **zeroclaw** | 32,151 | 4,794 | `master` | 2026-07-04 | `zeroclaw-git` @ `0.8.2.r163.gc1875895a-1` | 81 | **Highly Active** |
| **ironclaw** | 12,498 | 1,464 | `main` | 2026-07-04 | `ironclaw-reborn-git` @ `0.29.1.r1647.g4b5997e-1` | 26 | **Highly Active** |
| **librefang** | 318 | 64 | `main` | 2026-07-04 | `librefang-git` @ `2026.6.29.r9.g83ee2627b-1` | 13 | **Active** |
| **hermes-agent** | 209,145 | 38,151 | `main` | 2026-07-04 | `hermes-agent-git` @ `0.18.0.r206.g19d417445-1` | 36 | **Highly Active** |
| **nanobot** | 45,006 | 7,940 | `main` | 2026-07-04 | — | — | **Highly Active** |
| **picoclaw** | 29,585 | 4,266 | `main` | 2026-07-04 | `picoclaw-git` @ `0.3.0.nightly.20260622.287853ab-1` | 50 | **Active** |
| **nanoclaw** | 30,123 | 12,901 | `main` | 2026-07-04 | — | — | **Highly Active** |

#### Weekly Activity Metrics (Human vs Bot)
| Assistant Repo | Commits / Week | Lines Added (Human/Bot) | Lines Deleted (Human/Bot) | Merges (Last Wk) | Releases/Tags (Last Wk) | Avg Commits/Wk (4 Wks) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **zeroclaw** | **199** / 0 | 58.3k / 0 | 13.7k / 0 | 0 | 0 | 191.2 |
| **ironclaw** | **125** / 4 | 152.5k / 5.3k | 139.5k / 1.2k | 0 | 1 | 116.2 |
| **librefang** | **27** / 7 | 14.3k / 976 | 2.1k / 958 | 0 | 1 | 59.8 |
| **hermes-agent** | **1124** / 3 | 149.7k / 519 | 30.7k / 11 | 89 | 1 | 817.5 |
| **nanobot** | **87** / 0 | 14.4k / 0 | 2.9k / 0 | 0 | 0 | 120.8 |
| **picoclaw** | **5** / 6 | 4.2k / 715 | 71 / 790 | 13 | 1 | 32.8 |
| **nanoclaw** | **35** / 25 | 2.5k / 49 | 1.5k / 49 | 46 | 0 | 41.8 |
<!-- END_TABLES -->

---

## 🔍 Repository Breakdown

> [!NOTE]
> The contributor lists and activity metrics for each repository below are compiled according to commits from the last 7 days.


### ZeroClaw (`zeroclaw-labs/zeroclaw`)
<!-- START_BD_ZEROCLAW -->
* **Status**: Highly Active (Total: 199 commits [199 H / 0 B], 0 tags/releases in the last week). Lines added/deleted: +58.3k/-13.7k (Human), +0/-0 (Bot). **81 commits since installed 0.8.2.r163.gc1875895a-1 (ref=c1875895a).**
* **Contributors (according to last 7 days commits)** (Total: 36 Humans, 0 Bots):
  - **Top Humans**:
    - `Dan Gilles <dfgilles@uchicago.edu>` (Human): 44 commits, +4.9k/-722 lines
    - `Marc Collins <marc@nnet.tech>` (Human): 19 commits, +11.5k/-2.5k lines
    - `Alix-007 <li.long15@xydigit.com>` (Human): 19 commits, +1.2k/-0 lines
    - `Shane Engelman <contact@shane.gg>` (Human): 16 commits, +7.6k/-8.0k lines
    - `wangmiao0668000666 <wang.miao86@xydigit.com>` (Human): 15 commits, +3.3k/-480 lines
    - `JordanTheJet <morepencils@gmail.com>` (Human): 7 commits, +5.6k/-176 lines
    - `LiLan0125 <li.lan3@xydigit.com>` (Human): 7 commits, +908/-79 lines
    - `Tidux <jon@borg.moe>` (Human): 7 commits, +6.1k/-232 lines
    - `Jason Perlow <jperlow@gmail.com>` (Human): 7 commits, +1.3k/-49 lines
    - `ConYel <18070323+ConYel@users.noreply.github.com>` (Human): 7 commits, +1.1k/-103 lines
<!-- END_BD_ZEROCLAW -->
<!-- START_RF_ZEROCLAW -->
* **Recent Focus**:
  - `3ec71f11` feat(skills): document work queue query in issue triage skill (#6718)
  - `e43604a9` feat(observability): runtime OTel content policy for LLM and tool I/O (#8567)
  - `a44af5d1` refactor(runtime): unify process_message built-in tool filter through the scoped seam (#8701)
  - `ee97859e` fix(zerocode): let active sessions switch agents (#8477)
  - `6734b222` refactor(runtime): route loop_::run tool assembly through the ScopedToolRegistry seam (#8700)
  - `665308d6` feat(desktop): reintroduce zeroclaw-desktop as a self-contained, Quickstart-first companion (#8565)
  - `f753dc41` feat(skills): add pr-architecture-check advisory review skill (#6716)
  - `710a2b54` feat(sop): add procedural memory workshop (#8509)
  - `10d1f6fc` fix(channels): repair master build under all-features (#8702)
  - `d948071e` fix(plugins): feature-graph, install-time config seeding, and degraded-section visibility (#8641)
  - `a9a2646c` fix(provider): guard SSE parsers against EOF-as-success truncation (#8663)
  - `078dc36b` docs(labels): document provider router and security labels (#8668)
  - `b1236a7b` docs(skills): route issue filing by current templates (#8666)
  - `6005b54f` docs(review): require template truthfulness checks (#8651)
  - `aa68d3f7` docs(skills): align squash-merge gh version floor (#8670)
  - `43701255` fix(memory): refresh embedder on config/set provider-profile change (#8625)
  - `409dd4f3` fix(channels): refine Lark/Feishu tool-use prompt (#8608)
  - `a24d5d16` fix(channels): carry WeCom reply scope as structured metadata (#8596)
  - `955deee6` fix(providers): omit Responses tool_choice for empty tools (#8667)
  - `563715d9` fix(windows): silence config shell clippy warnings (#8665)
  - `89268f1e` fix(install): prebuild dashboard for embedded web (#8643)
  - `fa832579` fix(zerocode): advertise deferred MCP tools in Chat TUI system prompt (#8634)
  - `b003f94f` fix(providers): omit empty assistant tool-call content in OpenAI-compatible requests (#8524)
  - `10f909e4` chore(deps): bump wasmtime 43 -> 45.0.3 to clear three wasmtime-wasi CVEs (#8519) (#8542)
  - `a815089a` fix(skill_http): reject URL userinfo to close parser-level SSRF gap (#8658)
  - `154860e1` feat(install): add --full flag to install everything (#8566)
  - `0349838a` feat(memory): epic A durable store seam (supersede/dedup/budget/policy-gate) (#8570)
  - `3962ec80` build(windows): statically link MSVC CRT for windows-msvc targets (#8604)
  - `d9873818` fix(runtime): seed full personality preset on agent creation (#8507)
  - `0937e7d8` fix(agent): cap interactive CLI stdin lines to 1 MiB (#8463)
  - `fbe6bf6d` test(skills): add regression tests for zip entries with lying declared sizes (#8574)
  - `3a196097` docs(maintainers): add audit-policy.md for cargo-audit/deny.toml ignore governance (#8543)
  - `928d1a62` docs(maintainers): define PR stale escalation ramp (#8607)
  - `167871d3` feat(tools): gate the gateway tool registries through the ScopedToolRegistry assemble seam (#8640)
  - `9a33826f` docs(book): add memory payload lifecycle architecture guide (#8610)
  - `4a775a3b` fix(agent): align Agent::from_config tool dispatcher and prompt with active provider per turn (#8054 Surface 2) (#8599)
  - `a5791acf` fix(daemon): stop WSL2 restart-storm OOM in component supervisor (#8633)
  - `45a15f8c` docs(labels): document agent prompt label (#8612)
  - `2715cf50` docs(skills): add squash-merge freshness basis (#8613)
  - `0dcdd49d` fix(channels): derive channel prompt tool-availability from per-turn effective specs (#8054 Surface 1(a)) (#8488)
  - `e72f8874` refactor(channels): route the orchestrator turn back through ResolvedAgentExecution::resolve (#8629)
  - `1dddc3bc` fix(config): guard the real config.toml against agent self-modification in nested layouts (#8606)
  - `60b67e09` feat(rfc-6969): per-turn output routing via send_via + voice delivery fixes (#7361)
  - `169683d3` fix(skills): bound skill zip extraction (#8548)
  - `dc23e658` fix(cron): thread CancellationToken through cron::run for explicit shutdown (#8465)
  - `7a56c816` docs(providers): update MiniMax catalog example to M3 (#7144)
  - `9c2dba13` feat(zerocode): Cost tab by-period + org billed views (#8483)
  - `1b470e04` feat(sop): consume CAS run claims (#8506)
  - `49741842` docs(tools): add relationship memory skill workflow
  - `c3a160a3` docs(config): add config lifecycle architecture guide (#8594)
  - `303ba38f` docs(labels): document channel core label (#8593)
  - `069a3c5a` feat(plugins): channel host bindings (wasi:http, inbound queue, config jail) and registration API (#8551)
  - `d23c5c71` fix(docs): repair SOP fan-in snippet links (#8595)
  - `d1ca4cd2` fix(providers): include tool name in native tool-result messages (#7909)
  - `85de8e95` docs(labels): document type test label (#8597)
  - `bbd965ad` feat(mcp): resources-as-context, pinning, and named-prompt rendering (#8508)
  - `6b81cd6a` test(log): cover tool-io capture truncation edge cases (#8255)
  - `dc66e029` fix(tools): bound browser_open launcher waits (#8564)
  - `541aa21c` fix(cron): filter recv_log_event by job_id to prevent cross-test broadcast pollution (#8562)
  - `35aa0f0d` feat(web): show secret set/not-set state instead of bare password input (#8557)
  - `1363b431` fix(gateway): read CARGO_MANIFEST_DIR at runtime in build script (#8552)
  - `ad17c812` fix(tool-call-parser): recover malformed file_write content (#8545)
  - `e170bad2` test(log): cover reader action/category/outcome filter matching (#8269)
  - `68549a28` fix(runtime): gate Unix-only shell test helper behind #[cfg(unix)] (#8535)
  - `3c83360e` fix(gateway): advertise A2A cards on runtime port (#8538)
  - `b4a42781` fix(agent): refresh system prompt TASK_FRAMING anchor per-turn for vision-routed providers (#8054 Surface 3) (#8503)
  - `7b0312df` ci(workflows): guard declared repository submodules (#8516)
  - `8c080dd3` fix(channels): fire message_sent hooks after delivery (#8355)
  - `2e801fc4` feat(skills): suggest missing plugins from cached registry (#8428)
  - `c4299bce` fix(i18n): reject local path leaks in translations (#8365)
  - `bbf20b67` docs(security): clarify tool receipt guarantees (#8407)
  - `8e682a17` fix(docs): autolink ACP elicitation RFD (#8498)
  - `4264cb01` ci(workflows): gate Windows Clippy for tools changes (#8517)
  - `f856d9c4` fix(ci): allow generated docs reference links (#8533)
  - `4e60c43e` test(tools): cover weather HTTP skill shape (#8433)
  - `81930521` feat(config): add local_small runtime preset (#8531)
  - `a1ba2091` docs(labels): document line and memory backend labels (#8523)
  - `b5598680` feat(amqp): SOP fan-in dispatch path, fan-in usage docs, and AMQP credential secret fix (#8521)
  - `58720129` feat(web): add select all/deselect all toggle to tool picker groups (#8464)
  - `427af575` fix(config): warn when sqlite memory requests vector search without an embedder (#8501)
  - `b089888b` chore(desktop): remove the zeroclaw-desktop Tauri app and all wiring (#8544)
<!-- END_RF_ZEROCLAW -->
### IronClaw (`nearai/ironclaw`)
<!-- START_BD_IRONCLAW -->
* **Status**: Highly Active (Total: 129 commits [125 H / 4 B], 1 tag/release in the last week). Lines added/deleted: +152.5k/-139.5k (Human), +5.3k/-1.2k (Bot). **26 commits since installed 0.29.1.r1647.g4b5997e-1 (ref=4b5997e).**
* **Contributors (according to last 7 days commits)** (Total: 9 Humans, 2 Bots):
  - **Top Humans**:
    - `firat.sertgoz <firat.sertgoz@near.ai>` (Human): 51 commits, +55.9k/-4.0k lines
    - `Henry Park <henrypark133@gmail.com>` (Human): 31 commits, +44.4k/-14.7k lines
    - `Illia Polosukhin <ilblackdragon@gmail.com>` (Human): 16 commits, +30.9k/-102.0k lines
    - `jinxin <106428113+italic-jinxin@users.noreply.github.com>` (Human): 13 commits, +7.6k/-8.4k lines
    - `Robert Yan <46699230+think-in-universe@users.noreply.github.com>` (Human): 5 commits, +1.5k/-1.0k lines
    - `Benjamin Kurrek <57506486+BenKurrek@users.noreply.github.com>` (Human): 5 commits, +11.2k/-1.4k lines
    - `Coffee <zjchen1234@foxmail.com>` (Human): 2 commits, +932/-7.9k lines
    - `Pranav Raja <pranavraja99@gmail.com>` (Human): 1 commits, +15/-4 lines
    - `Josh Ford <thisisjoshford@gmail.com>` (Human): 1 commits, +145/-3 lines
  - **Top Bots**:
    - `dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>` (Bot): 3 commits, +2.2k/-1.2k lines
    - `ironclaw-ci[bot] <266877842+ironclaw-ci[bot]@users.noreply.github.com>` (Bot): 1 commits, +3.1k/-0 lines
<!-- END_BD_IRONCLAW -->
<!-- START_RF_IRONCLAW -->
* **Recent Focus**:
  - `54ab4088` test(reborn): integration-suite restructure — tests/integration/ home, framework disentanglement, single-run coverage (#5633)
  - `2603114b` fix(ci): stabilize Slack live QA harness (#5632)
  - `f67e482b` ci(fix): scope E2E coverage to standalone Reborn (#5634)
  - `32d88656` ci(fix): codecov action signature verification (#5631)
  - `63d48820` ci(fix): fix main Docker build prompt inputs (#5630)
  - `19f069a1` fix(ci): stabilize main-equivalent clippy and coverage checks (#5591)
  - `39c9c481` test(reborn): wave-4 integration coverage — auth-gate wire regression pack, triggered auth delivery, attachments, golden/synthetic expansions (#5610)
  - `3aef4688` test(reborn): extract trigger-prompt materializer into shared test support (#5609)
  - `129ce21e` refactor(types,traits): execute judged dedup backlog — 6 traits removed, 6 DTO clusters unified (#5567)
  - `920d9def` feat(reborn): manifest-projected host-ingress route + fail-closed credential coherence (#5625)
  - `e85cbbb1` [codex] Refactor Reborn composition internals (#5585)
  - `c0d281b9` Reborn #3231 follow-ups: extract host-runtime test harness + landing-policy doc (#5624)
  - `ac6bb8d8` refactor(reborn_identity): de-slop — dead types, boundary rule, CONTRACT, error-path tests (#5619)
  - `9c2fea84` feat(skills): add parallel-pr-review skill (#5622)
  - `b63ae605` docs: reference main, not staging, as the PR/integration branch (#5620)
  - `fcd3b654` docs(commands): add /deslop-reborn de-slop loop command (#5612)
  - `5c712dea` Stabilize QA6 and QA8 live canary assertions (#5607)
  - `f92c658c` [codex] Harden Slack pairing activation flows (#5362)
  - `6c63b3c3` test(reborn): wave-3 integration coverage — journeys, multi-user isolation, triggered/outbound, budget/comm-context/hooks seams, golden payloads, denied-edge contracts (#5584)
  - `b47f8a9b` Fix CI after engine v2 removal (#5601)
  - `2cc9e4f5` refactor: remove engine v2 (crates/ironclaw_engine) (#5545)
  - `5b80cb08` Enable distributed sccache in key CI workflows (#5599)
  - `c510b88a` [codex] Harden Reborn WebUI v2 live canary diagnostics (#5586)
  - `0398ab3b` Address sccache dist smoke review comments (#5597)
  - `89daa53b` Add sccache dist smoke workflow (#5596)
  - `174c9fe1` docs(oauth): mark ironclaw_oauth v1-only, delete-with-v1 (#5569)
<!-- END_RF_IRONCLAW -->
### Hermes Agent (`NousResearch/hermes-agent`)
<!-- START_BD_HERMES_AGENT -->
* **Status**: Highly Active (Total: 1127 commits [1124 H / 3 B], 1 tag/release in the last week). Lines added/deleted: +149.7k/-30.7k (Human), +519/-11 (Bot). **36 commits since installed 0.18.0.r206.g19d417445-1 (ref=19d417445).**
* **Contributors (according to last 7 days commits)** (Total: 265 Humans, 3 Bots):
  - **Top Humans**:
    - `teknium1 <127238744+teknium1@users.noreply.github.com>` (Human): 178 commits, +10.0k/-1.2k lines
    - `Brooklyn Nicholson <brooklyn.bb.nicholson@gmail.com>` (Human): 170 commits, +37.3k/-15.1k lines
    - `Teknium <127238744+teknium1@users.noreply.github.com>` (Human): 147 commits, +19.8k/-4.2k lines
    - `kshitijk4poor <82637225+kshitijk4poor@users.noreply.github.com>` (Human): 96 commits, +6.4k/-774 lines
    - `xxxigm <tuancanhnguyen706@gmail.com>` (Human): 21 commits, +1.4k/-75 lines
    - `liuhao1024 <sunsky.lau@gmail.com>` (Human): 19 commits, +2.1k/-103 lines
    - `HexLab98 <liruixinch@outlook.com>` (Human): 16 commits, +1.1k/-58 lines
    - `Ben Barclay <ben@nousresearch.com>` (Human): 16 commits, +3.7k/-357 lines
    - `Ben <ben@nousresearch.com>` (Human): 16 commits, +4.0k/-350 lines
    - `srojk34 <286497132+srojk34@users.noreply.github.com>` (Human): 15 commits, +1.6k/-38 lines
  - **Top Bots**:
    - `Tranquil-Flow <agent@tranquil-flow.dev>` (Bot): 1 commits, +357/-4 lines
    - `hinotoi-agent <paperlantern.agent@gmail.com>` (Bot): 1 commits, +78/-1 lines
    - `homelab-ha-agent <ha-agent@homelab.4410.us>` (Bot): 1 commits, +84/-6 lines
<!-- END_BD_HERMES_AGENT -->
<!-- START_RF_HERMES_AGENT -->
* **Recent Focus**:
  - `81f1ba800` test(telegram): cancel leaked conflict-retry task before fatal assertion
  - `b1c7b9654` fix(telegram): bound the 3 sibling updater.stop() calls with the same CLOSE-WAIT timeout
  - `8645b3430` fix(telegram): bound updater.stop() with timeout to prevent CLOSE-WAIT reconnect hang
  - `dba585c17` fix(agent): deduplicate tool_call_id across the pre-API sanitizers (#58327)
  - `60906be3f` chore: map yingwaizhiying@gmail.com -> msh01 in AUTHOR_MAP
  - `d8504df7e` refactor(compression): reuse _fresh_compaction_message_copy in user-turn guard
  - `6e176e4c2` fix(compression): preserve user turn after compaction
  - `2d3eac5fb` fix(moa): apply prompt-caching decoration to the aggregator's one-shot synthesis call
  - `a37fd66de` fix(telegram): shut down abandoned init app + AUTHOR_MAP + cover the deadline helper
  - `d50aae0e3` fix(telegram): use wall deadline for init timeout
  - `86a0c5553` feat: allow suppressing Codex gpt-5.5 autoraise notice
  - `8b24376d6` fix(dashboard): close credential-dir-tree gap + .git-credentials in managed-files guard
  - `43ec69cef` security(dashboard): widen managed-files sensitive-filename guard past .env
  - `09693cd3a` fix: complete OAuth-UA salvage follow-up (stale comment + test keychain isolation)
  - `4c5b4417b` fix(anthropic): OAuth token endpoint UA must not be claude-code/ (login 429, #48534)
  - `88f2c0caf` fix(agent): match tool results on call_id||id in pre-request repair (#58168)
  - `ca596e228` chore: map marxb@protonmail.com to Marxb85 in AUTHOR_MAP
  - `fab6d4d1b` Fix computer-use crash on X11 windows with null PID
  - `fc31f14cd` fix(cron): disambiguate Telegram forum vs channel DM topics at delivery time (#52060)
  - `3c8c968d1` chore: map huanshan5195 in AUTHOR_MAP for #57601 salvage
  - `67df958db` fix(custom-provider): emit reasoning_effort at the live profile path
  - `a1c17edcb` test: update reasoning-effort docstring guards for new 'max' level
  - `f69a33794` fix: forward reasoning_effort for custom providers (GLM-5.2 on ARK)
  - `4651ac64a` refactor(ssh): extract shared _is_ssh_remote_tilde_cwd predicate
  - `83fb8ec27` fix(ssh): preserve remote tilde cwd
  - `90f84144e` refactor: gate pre-API compaction through the preflight guard chain
  - `af0ce1cf8` refactor(mcp): DRY the non-interactive OAuth guard + positive-control test
  - `0c8441c88` test(mcp): cover non-interactive fail-fast at OAuth callback boundary (#57836)
  - `755194ffe` fix(mcp): fail fast at OAuth redirect/callback boundary when non-interactive (#57836)
  - `475dd9726` fix: re-baseline flush cursor after mid-turn pre-API compaction
  - `1f430e1aa` fix: recover Codex max-output truncation
  - `8229d7765` chore: map lavya@loom.local -> LavyaTandel in AUTHOR_MAP
  - `52cf9dbad` fix(prompt-caching): align _can_carry_marker with last-part-dict marking
  - `8b797f7a7` fix(prompt-caching): skip invalid top-level cache_control on empty assistant/tool messages on OpenRouter
  - `7a648a8bf` fix(telegram): paginate model provider picker
  - `4bf749fd5` fix(desktop): add tooltip and fix scrollbar overlap on tool output copy button
<!-- END_RF_HERMES_AGENT -->
### NanoBot (`HKUDS/nanobot`)
<!-- START_BD_NANOBOT -->
* **Status**: Highly Active (Total: 87 commits [87 H / 0 B], 0 tags/releases in the last week). Lines added/deleted: +14.4k/-2.9k (Human), +0/-0 (Bot).
* **Contributors (according to last 7 days commits)** (Total: 19 Humans, 0 Bots):
  - **Top Humans**:
    - `chengyongru <chengyongru.ai@gmail.com>` (Human): 34 commits, +3.8k/-898 lines
    - `Xubin Ren <52506698+Re-bin@users.noreply.github.com>` (Human): 15 commits, +1.5k/-239 lines
    - `chengyongru <2755839590@qq.com>` (Human): 10 commits, +4.1k/-1.3k lines
    - `axelray-dev <110029405+axelray-dev@users.noreply.github.com>` (Human): 7 commits, +507/-103 lines
    - `wangjunwei <wangjunwei87@gmail.com>` (Human): 3 commits, +453/-15 lines
    - `yorkhellen <zhangxiaoyu.york@bytedance.com>` (Human): 2 commits, +229/-12 lines
    - `Yuxin Lou <louyuxin_730@163.com>` (Human): 2 commits, +58/-8 lines
    - `yu-xin-c <2182712990@qq.com>` (Human): 2 commits, +61/-0 lines
    - `hamb1y <rishi.s.malnad@gmail.com>` (Human): 2 commits, +146/-3 lines
    - `xcao <xcao@bonditech.com.cn>` (Human): 1 commits, +56/-3 lines
<!-- END_BD_NANOBOT -->
<!-- START_RF_NANOBOT -->
* **Recent Focus**:
  - `83e4bae7` fix(gateway): skip ctrl-break wait when signal is rejected
  - `58b5bb92` fix(gateway): handle Windows stop fallback
  - `c579551b` fix(dingtalk): stop stream task on shutdown
  - `8b645135` fix(pairing): restore durable atomic writes
  - `28011413` fix(copilot): guard token refresh with asyncio.Lock to prevent race condition
  - `614ea86a` test: align MCP transient reconnect coverage
  - `6d28db32` fix: reconnect MCP sessions on transient stream failures
  - `0d1221be` fix(mcp): contain malformed tool results
  - `8b9f93d7` test(config): lock model presets alias serialization
  - `a119c35b` fix(config): serialize model presets as camelCase
  - `067e0c4a` feat(cli): add safe WebUI first-run launcher (#4688)
  - `5283ceae` Add optional Nanobot plugin controls (#4396)
  - `00cc0da5` fix(providers): omit temperature for sonnet 5
  - `b19a7441` fix(providers): update Anthropic default model to claude-sonnet-4-6
  - `c9c69e43` fix(memory): cap workspace Dream prompt overrides
<!-- END_RF_NANOBOT -->
### PicoClaw (`sipeed/picoclaw`)
<!-- START_BD_PICOCLAW -->
* **Status**: Active (Total: 11 commits [5 H / 6 B], 1 tag/release in the last week). Lines added/deleted: +4.2k/-71 (Human), +715/-790 (Bot). **50 commits since installed 0.3.0.nightly.20260622.287853ab-1 (ref=287853ab).**
* **Contributors (according to last 7 days commits)** (Total: 3 Humans, 1 Bots):
  - **Top Humans**:
    - `Ethan1918 <75773519+Ethan1918@users.noreply.github.com>` (Human): 3 commits, +262/-49 lines
    - `pancake <pancake@nopcode.org>` (Human): 1 commits, +3.4k/-7 lines
    - `LC <lclc6464@outlook.com>` (Human): 1 commits, +482/-15 lines
  - **Top Bots**:
    - `dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>` (Bot): 6 commits, +715/-790 lines
<!-- END_BD_PICOCLAW -->
<!-- START_RF_PICOCLAW -->
* **Recent Focus**:
  - `79c075fb` fix(openai_compat): remove unused log import
  - `ffffb6a0` refactor(agent): route /clear through ContextManager.Clear for all agents
  - `c4fb7a20` fix(agent): clear routed agent session
  - `93a58e05` build(deps-dev): bump @vitejs/plugin-react in /web/frontend
  - `70b9cb9e` build(deps-dev): bump typescript-eslint in /web/frontend
  - `8fd07bca` build(deps): bump shadcn from 4.7.0 to 4.12.0 in /web/frontend
  - `e56ab1f1` build(deps): bump react-i18next from 17.0.6 to 17.0.7 in /web/frontend
  - `addaef78` build(deps): bump golang.org/x/crypto from 0.51.0 to 0.53.0
  - `ba881f82` build(deps): bump github.com/anthropics/anthropic-sdk-go
  - `612e485d` WIP: Initial support for deltachat gateway
  - `2cf030d2` fix(providers): surface friendly auth error messages (#3198)
<!-- END_RF_PICOCLAW -->
### NanoClaw (`nanocoai/nanoclaw`)
<!-- START_BD_NANOCLAW -->
* **Status**: Highly Active (Total: 60 commits [35 H / 25 B], 0 tags/releases in the last week). Lines added/deleted: +2.5k/-1.5k (Human), +49/-49 (Bot).
* **Contributors (according to last 7 days commits)** (Total: 6 Humans, 1 Bots):
  - **Top Humans**:
    - `gavrielc <gabicohen22@yahoo.com>` (Human): 29 commits, +972/-1.4k lines
    - `John Mathews <mthwsjc@gmail.com>` (Human): 2 commits, +406/-89 lines
    - `leetwito <leetwito@gmail.com>` (Human): 1 commits, +8/-3 lines
    - `Amit Shafnir <amit@nanoco.ai>` (Human): 1 commits, +939/-8 lines
    - `Rob Stevenson <this.rob@protonmail.com>` (Human): 1 commits, +137/-26 lines
    - `Omri Maya <omri@nanoco.ai>` (Human): 1 commits, +87/-0 lines
  - **Top Bots**:
    - `github-actions[bot] <github-actions[bot]@users.noreply.github.com>` (Bot): 25 commits, +49/-49 lines
<!-- END_BD_NANOCLAW -->
<!-- START_RF_NANOCLAW -->
* **Recent Focus**:
  - `08a1ac9` chore: bump version to 2.1.38
  - `694ab74` chore: bump version to 2.1.37
  - `7145370` Apply suggestion from @gavrielc
  - `0aa9e66` Apply suggestion from @gavrielc
  - `55c003c` Apply suggestion from @gavrielc
  - `20f2bae` Apply suggestion from @gavrielc
  - `d6b82e6` Apply suggestion from @gavrielc
  - `fea5ac5` Apply suggestion from @gavrielc
  - `2b86bbe` Apply suggestion from @gavrielc
  - `9dc0a7e` Apply suggestion from @gavrielc
  - `2035033` Delete docs/docker-sandboxes.md
  - `1c294ff` Delete docs/APPLE-CONTAINER-NETWORKING.md
  - `4319831` chore: bump version to 2.1.36
  - `a8b7da7` docs: update token count to 208k tokens · 104% of context window
  - `0b6ad55` chore: bump version to 2.1.35
<!-- END_RF_NANOCLAW -->
### LibreFang (`librefang/librefang`)
<!-- START_BD_LIBREFANG -->
* **Status**: Active (Total: 34 commits [27 H / 7 B], 1 tag/release in the last week). Lines added/deleted: +14.3k/-2.1k (Human), +976/-958 (Bot). **13 commits since installed 2026.6.29.r9.g83ee2627b-1 (ref=83ee2627b).**
* **Contributors (according to last 7 days commits)** (Total: 4 Humans, 1 Bots):
  - **Top Humans**:
    - `Evan <suzukaze.haduki@gmail.com>` (Human): 22 commits, +7.5k/-2.1k lines
    - `Павло <pavvers1@gmail.com>` (Human): 3 commits, +687/-36 lines
    - `Seungjin Kim <seungjin@users.noreply.github.com>` (Human): 1 commits, +6.1k/-7 lines
    - `FrantaNautilus <142005599+FrantaNautilus@users.noreply.github.com>` (Human): 1 commits, +1/-0 lines
  - **Top Bots**:
    - `dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>` (Bot): 7 commits, +976/-958 lines
<!-- END_BD_LIBREFANG -->
* **Note**: LibreFang is a community fork of the former `RightNow-AI/openfang` repository, which had **17,623 stars** and **2,252 forks** before going stale.
<!-- START_RF_LIBREFANG -->
* **Recent Focus**:
  - `a9c5496c` fix(deps): clear quick-xml RUSTSEC-2026-0194/0195 advisories (#6387)
  - `a6b84aa2` docs: add Arch Linux pacman installation instructions (#6386)
  - `b0d78537` chore(deps): bump the docs-minor-patch group in /docs with 10 updates (#6380)
  - `fcac113a` chore(deps-dev): bump @types/node from 25.9.3 to 26.1.0 in /docs (#6381)
  - `2d4b0843` docs: update contributors and star history (#6385)
  - `a906d8e9` docs: update contributors and star history (#6383)
  - `b01e37af` docs: update contributors and star history (#6379)
  - `59133586` feat(i18n): complete and proofread dashboard and website translations (#6376)
  - `fb41ec49` chore(deps): bump the web-minor-patch group in /web with 10 updates (#6377)
  - `e42f09af` chore(deps): bump the dashboard-minor-patch group (#6378)
  - `50a03d4c` chore(deps): bump the actions-minor-patch group with 2 updates (#6373)
  - `261b04e3` chore(deps): bump tauri-apps/tauri-action from 0.6.2 to 1.0.0 (#6374)
  - `c42b460c` docs: update contributors and star history (#6375)
<!-- END_RF_LIBREFANG -->
---
## 📋 Instruction Guide: Recreating this Analysis

**Fully Automated Update**: You can run the automation script `scripts/update-activity.py` with the `--write` (or `-w`) flag to automatically pull all repository updates, calculate the statistics, and optionally write the updated tables directly back into this file:
```bash
python scripts/update-activity.py [--write]
```
