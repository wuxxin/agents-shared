# Active AI Assistants: Weekly Development Activity

This document tracks repository activity, commit counts, merge frequency, and release cycles for active assistant projects.

---

#### 📊 Summary of Last 7 Days Activity (June 16, 2026 – June 23, 2026)

<!-- START_TABLES -->
#### Repository Overview & Package Status
| Assistant Repo | Stars | Forks | Main Branch | Last Commit | Installed Pkg | Commits Since Pkg | Status |
| :--- | :---: | :---: | :---: | :---: | :--- | :---: | :---: |
| **ironclaw** | 12,471 | 1,464 | `main` | 2026-06-23 | `ironclaw-git` @ `ironclaw.v0.29.1.r1448.gc50edb9-1` | 24 | **Highly Active** |
| **zeroclaw** | 32,009 | 4,751 | `master` | 2026-06-23 | `zeroclaw-git` @ `0.8.1.r16.g13a8a857a-1` | 87 | **Highly Active** |
| **hermes-agent** | 200,543 | 35,746 | `main` | 2026-06-23 | — | — | **Highly Active** |
| **nanobot** | 44,634 | 7,878 | `main` | 2026-06-23 | — | — | **Highly Active** |
| **picoclaw** | 29,468 | 4,244 | `main` | 2026-06-23 | `picoclaw-git` @ `0.3.0.nightly.20260620.287853ab-1` | 8 | **Active** |
| **nanoclaw** | 29,957 | 12,896 | `main` | 2026-06-23 | `nanoclaw-git` @ `r1859.625264ba4-1` | 3 | **Active** |
| **librefang** | 309 | 63 | `main` | 2026-06-23 | — | — | **Highly Active** |

#### Weekly Activity Metrics (Human vs Bot)
| Assistant Repo | Commits / Week | Lines Added (Human/Bot) | Lines Deleted (Human/Bot) | Merges (Last Wk) | Releases/Tags (Last Wk) | Avg Commits/Wk (4 Wks) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **ironclaw** | **78** / 0 | 91.2k / 0 | 15.7k / 0 | 0 | 1 | 135.5 |
| **zeroclaw** | **219** / 0 | 78.4k / 0 | 229.8k / 0 | 0 | 1 | 148.5 |
| **hermes-agent** | **724** / 0 | 120.5k / 0 | 32.6k / 0 | 83 | 1 | 704.2 |
| **nanobot** | **132** / 2 | 14.0k / 105 | 3.0k / 3 | 1 | 1 | 113.2 |
| **picoclaw** | **9** / 6 | 1.4k / 155 | 350 / 139 | 20 | 0 | 34.5 |
| **nanoclaw** | **25** / 3 | 1.3k / 6 | 448 / 6 | 10 | 0 | 31.2 |
| **librefang** | **80** / 13 | 36.4k / 766 | 10.3k / 750 | 0 | 3 | 87.5 |
<!-- END_TABLES -->

---

## 🔍 Repository Breakdown

> [!NOTE]
> The contributor lists and activity metrics for each repository below are compiled according to commits from the last 7 days.


### ZeroClaw (`zeroclaw-labs/zeroclaw`)
<!-- START_BD_ZEROCLAW -->
* **Status**: Highly Active (Total: 219 commits [219 H / 0 B], 1 tag/release in the last week). Lines added/deleted: +78.4k/-229.8k (Human), +0/-0 (Bot). **87 commits since installed 0.8.1.r16.g13a8a857a-1 (ref=13a8a857a).**
* **Contributors (according to last 7 days commits)** (Total: 35 Humans, 0 Bots):
  - **Top Humans**:
    - `Dan Gilles <dfgilles@uchicago.edu>` (Human): 45 commits, +9.5k/-1.1k lines
    - `Marc Collins <marc@nnet.tech>` (Human): 43 commits, +31.4k/-6.5k lines
    - `Shane Engelman <contact@shane.gg>` (Human): 29 commits, +19.9k/-219.4k lines
    - `Alix-007 <li.long15@xydigit.com>` (Human): 21 commits, +995/-87 lines
    - `Jason Perlow <jperlow@gmail.com>` (Human): 14 commits, +2.0k/-348 lines
    - `JordanTheJet <morepencils@gmail.com>` (Human): 10 commits, +1.0k/-146 lines
    - `pick-cat <huang.ting3@xydigit.com>` (Human): 9 commits, +805/-50 lines
    - `Cherilyn Buren <88433283+NiuBlibing@users.noreply.github.com>` (Human): 4 commits, +1.4k/-56 lines
    - `Tidux <jon@borg.moe>` (Human): 4 commits, +2.1k/-160 lines
    - `chengzhichao-xydt <cheng.zhichao@xydigit.com>` (Human): 4 commits, +330/-28 lines
<!-- END_BD_ZEROCLAW -->
<!-- START_RF_ZEROCLAW -->
* **Recent Focus**:
  - `bbd7b9a6` feat(sop): durable SQLite run-state store and live run metrics (#8206)
  - `a7361541` fix(receipts): wire HMAC tool receipts through the agent turn paths (ACP, gateway WS, CLI) (#8009)
  - `57544736` ci(docs): run link gate in PR checks (#8197)
  - `e75e1ea3` docs(mdbook): avoid stale placeholder warning translations (#8194)
  - `8a72f16b` fix(zerocode): detect daemon version mismatches (#8192)
  - `6aba8bdb` fix(config): gate Android shell import on non-Windows (#8189)
  - `2113a2a8` feat(runtime): suggest cached extra registry skills (#8185)
  - `d14f6d1f` docs(developing): define external integration boundary (#8184)
  - `8fe3765c` fix(tests): make screenshot expectations platform-aware (#8183)
  - `c6906dae` feat(knowledge): restore client relationship graph actions (#8182)
  - `23f86b4f` fix(tools): normalize Windows workspace-prefixed paths (#8114)
  - `b980e3a2` feat(channels/lark): restore outbound media markers (#8113)
  - `4b066e21` fix(docker): keep Node base policy in container TOML (#8112)
  - `513a9bb6` docs(maintainers): standardize label spelling (#8111)
  - `c4765b5a` docs(channels): remove stale guild override wording (#8108)
  - `ca96a5ba` fix(ci): stop Kilo labeler matching shared provider files (#8106)
  - `aecd9554` fix(tests): make process fixtures portable on Windows (#7956)
  - `18ad9a5c` feat(plugins): add SSRF guard to zc_http_request host function (#8128)
  - `a8da3970` refactor(history): rip out history pruning/compression, redo trim as one whole-turn function with a visible RPC event (#8196)
  - `5b46847a` feat(plugins): scope plugin config per-alias and remove raw env access (#8137)
  - `31dcb675` feat(sop): frame untrusted trigger payloads before the model prompt (#8215)
  - `63e0ef5b` feat(turn): add ResolvedAgentExecution::resolve and route prod turn paths (#8179)
  - `607d69ef` feat(runtime): durable run/task control-plane + delegate/subagent supervision (#8217)
  - `b3bab65f` feat(docs): move translation catalogues to git submodule (#8169)
  - `295a77db` feat(gateway): A2A agent discovery surface (#7763)
  - `a6a5997e` feat(presets): redefine Balanced as the trusted-local daily driver (#8133)
  - `3cca4caa` fix(telegram): redact bot token via global leak detector (#8127)
  - `6289ecd1` fix(runtime): refresh system prompt on tool dispatcher swap (#8126)
  - `d19167bd` feat(zerocode): add Aliases/Costs tabs to provider alias list (#8006)
  - `0a48eb76` ci(docker): build base Dockerfiles from source on container changes (#8093)
  - `d7edf20d` fix(web): surface config drift conflict on the enable/disable toggle (#8042)
  - `df255e7d` feat(web): themed click-to-open config pickers (Select primitive) (#8086)
  - `2ee5906e` feat(web): dashboard component-health "fix in place" modal (#8087)
  - `451b15e9` fix(vision): scope the no-vision capability error to the latest user image (#8180)
  - `87c186e0` fix(agent): self-contained context-compression summary provider (#7973)
  - `991a5b4d` fix(daemon): drain gateway before RPC reload (#8104)
  - `d65404c1` fix(zerocode): initialize MCP for Chat TUI sessions (#8199)
  - `8df6b8aa` docs(rustdoc): quiet warning links (#8191)
  - `a3b82014` feat(sop): add SopRunStore trait + in-memory backend (EPIC B scaffold) (#8001)
  - `2b834174` feat(security): Principal type + AuthProvider seam (#7141) (#8063)
  - `ffbf4109` fix(tools/image): expose stable attachment paths in image-generation output (#7985)
  - `ef18ac65` fix(update): repair Windows self-update and harden the update pipeline (#7853)
  - `c6c4a239` fix(zerocode): surface active config directory in Config header (#7999)
  - `f218b949` fix(cron): claim/release in-flight lock to prevent duplicate launches (#8107)
  - `80d159da` fix(model_switch): resolve list_models from live models.dev catalog, hardcoded list as offline fallback (#8088) (#8097)
  - `dcaf38dc` fix(channels): suppress bound channels when their owning agent is disabled (#8013) (#8051)
  - `338fa6e2` test(runtime): pin hook panic recovery + cancellation propagation (#7688) (#8041)
  - `ba46f82d` feat(channels/whatsapp): add allowed_groups per-JID group allowlist for Web mode (#7720)
  - `65a0f089` fix(runtime): present native/MCP tools to reasoning models in the system prompt (#7756) (#8053)
  - `2b1ec61e` fix(gateway): surface option-backed tunnel providers in the picker (#8026)
  - `717845fd` refactor(turn): bundle per-agent ToolLoop fields into ResolvedAgentExecution (#8156)
  - `9efc7c08` fix(mcp): scope MCP tools per-agent and enforce the denylist (#8120)
  - `1a3fdb9b` fix(whatsapp_storage): store app-state mutation MACs raw, not JSON-wrapped (#7912)
  - `d2ed46f4` fix(zerocode): skip queue-paused hint when backlog is empty (#7857)
  - `9db2c40c` fix(read_skill): load plugin-bundled and bundled skills (#7245)
  - `8043f285` feat(skill-tool): expose ZEROCLAW_SESSION_ID to skill shell tools (#8035)
  - `a8600417` fix(daemon): handle file-descriptor exhaustion (EMFILE) in IPC accept loop (#7983)
  - `b31d1648` fix(skills): guard truncate_output against UTF-8 char boundaries (#7962)
  - `8e9e6327` feat(skills): user-configured extra skill registries via registry:<name>/<skill> (#7827)
  - `5152cd7d` fix(self-test): authenticate websocket handshake probe (#7732)
  - `c408422d` feat(slack): upload outbound attachments (#7170)
  - `111a9662` fix(tools/git_operations): add recovery hint and path context to non-repository error (#7835)
  - `ea207f88` fix(install): detect Intel vs Apple Silicon for prebuilt target triple (#8096)
  - `8ffd39fc` test(runtime/tool_execution): add regression for poisoned activated-tool lock recovery (#7845)
  - `9f1456d7` test(runtime): cover blank-input turn rejection (#7859)
  - `afba0a77` fix(runtime): base missing-skill suggestions on effective tool set in process_message path (#7819)
  - `e86be5b7` ci(actions): add advisory cross-platform clippy workflow (#7885)
  - `6a1dd4d6` fix(zerocode): fill approval overlay background (#7823)
  - `57b7a87b` docs(architecture): align extension point overview (#7880)
  - `a4135cdb` docs(plugin): align plugin docs with WIT target (#8061)
  - `b10d2227` fix(docker): drop stale aardvark-sys build.rs COPY (#8092)
  - `185fcde3` docs(windows-setup): fix dead quick-start link breaking docs build (#8085)
  - `91c4a0cc` test(memory): cover storage-reader timestamp and ordering edge cases (#7694) (#7916)
  - `a5d58033` fix(memory): decouple embedding key from chat provider; survive embed failures (#7942)
  - `56b1bcab` fix(zeroclaw-runtime): drop unused unconditional rumqttc dependency (#8077)
  - `c338e094` chore(hardware): gate aardvark-sys behind the hardware feature (#8028)
  - `b54bec7c` fix(gateway): persist agent rename before moving owned state (#7940)
  - `e3d0b51f` feat(gateway/cron): accept enabled on CronPatchBody for pause/resume; scope the agent check to shell-command patches (#7666)
  - `592daa9a` feat(observability): categorize and verb-tag agent-loop log events (#8067)
  - `9e7dee6c` fix(channels): preserve tool-result content when proactively trimming channel history (#8050)
  - `1176f9b0` fix(runtime): stop duplicating streamed narration before native tool calls (#8014)
  - `74711fbb` fix(cost): make budget config reloadable instead of frozen at boot (#8004)
  - `a0bf350f` feat(xtask): drive container base pins from a canonical TOML (#8005)
  - `c6cf7565` docs(windows-setup): rewrite + fix setup.bat known issues (#6102)
  - `215be2e7` chore(deps): unyank bitcoin crates in Cargo.lock (#7992)
  - `eb6f1a46` feat(channels/discord): slash command localizations + guild scope (#7922)
  - `5a248ee1` fix(docker): correct Node 24 digest pins (#7932)
<!-- END_RF_ZEROCLAW -->
### IronClaw (`nearai/ironclaw`)
<!-- START_BD_IRONCLAW -->
* **Status**: Highly Active (Total: 78 commits [78 H / 0 B], 1 tag/release in the last week). Lines added/deleted: +91.2k/-15.7k (Human), +0/-0 (Bot). **24 commits since installed ironclaw.v0.29.1.r1448.gc50edb9-1 (ref=c50edb9).**
* **Contributors (according to last 7 days commits)** (Total: 11 Humans, 0 Bots):
  - **Top Humans**:
    - `firat.sertgoz <firat.sertgoz@near.ai>` (Human): 34 commits, +19.3k/-3.5k lines
    - `Illia Polosukhin <ilblackdragon@gmail.com>` (Human): 14 commits, +24.4k/-2.7k lines
    - `Henry Park <henrypark133@gmail.com>` (Human): 10 commits, +26.7k/-5.9k lines
    - `Robert Yan <46699230+think-in-universe@users.noreply.github.com>` (Human): 6 commits, +4.6k/-338 lines
    - `jinxin <106428113+italic-jinxin@users.noreply.github.com>` (Human): 5 commits, +6.2k/-1.2k lines
    - `aiworkbot <robert.yan@near.ai>` (Human): 3 commits, +1.8k/-1.0k lines
    - `Coffee <zjchen1234@foxmail.com>` (Human): 2 commits, +4.2k/-856 lines
    - `krishna-505 <102638219+krishna-505@users.noreply.github.com>` (Human): 1 commits, +3.7k/-40 lines
    - `Daniel Wang <5139554+danielwpz@users.noreply.github.com>` (Human): 1 commits, +4/-29 lines
    - `loopstring <yutingytw@gmail.com>` (Human): 1 commits, +442/-53 lines
<!-- END_BD_IRONCLAW -->
<!-- START_RF_IRONCLAW -->
* **Recent Focus**:
  - `c0294299` feat(reborn): wire Reborn operator diagnostics (#4801)
  - `6e4b0446` feat(reborn): support Reborn operator log tail/follow (#4804)
  - `ff57520f` feat(reborn): add automation pause resume (#5131)
  - `9e5912f7` Add Emulate-backed Gmail OAuth E2E coverage (#5136)
  - `a38a280f` fix(gsuite): restore duplicate account fallback (#5150)
  - `a0bd021e` feat(reborn): skill extraction & self-evolution with activation controls (#5061)
  - `3111e661` fix(turns): prevent turn-state write convoy (#5142)
  - `c62f0f84` fix(triggers): complete once permanent failures (#5141)
  - `9ac7b476` [codex] Add hosted single-tenant Postgres profile (#5081)
  - `d2b91964` fix(triggers): surface trigger input errors (#5140)
  - `14f7a1d1` feat(reborn): concurrent turn execution via TurnRunScheduler + per-user/per-type caps (#5085)
  - `f85347dd` feat(reborn): per-turn auto-approve resolution + never-auto-approve hard floor (#4959) (#5063)
  - `8b1777e3` feat(approvals): per-tool permission override model for Reborn (#4958) (#5062)
  - `704fcd43` feat(admin): persist Engine V2 LLM usage (#4989)
  - `1da2d40c` ci(reborn): share one Rust cache across the closure instead of ~60 per-crate caches (#5118)
  - `726bbb3d` feat(triggers): one-shot scheduled triggers via TriggerSchedule::Once{at} (#5065)
  - `b1924ab8` ci(reborn): retry crates.io network failures in the closure (CARGO_NET_RETRY) (#5115)
  - `61f37d65` ci: extract cross-cutting jobs into platform-and-compat.yml (#5113)
  - `2d264e9b` fix(reborn): NEAR AI MCP ready state projection (#4990)
  - `3b4e1a01` ci(reborn): run the full reborn_cli dependency closure on every PR (#5110)
  - `9ccb2364` test(host_runtime): clear closure-exposed test debt (stale profile test + flaky scheduler log) (#5112)
  - `60898402` fix(coding): read_file limit:0 must not emit a continuation footer (#5111)
  - `b975943f` fix(skills,host_runtime,gsuite): close reborn-closure tail failures (#5108)
  - `2b2ccc55` fix(reborn): proactively refresh Google OAuth tokens before expiry (#5071) (#5087)
<!-- END_RF_IRONCLAW -->
### Hermes Agent (`NousResearch/hermes-agent`)
<!-- START_BD_HERMES_AGENT -->
* **Status**: Highly Active (Total: 724 commits [724 H / 0 B], 1 tag/release in the last week). Lines added/deleted: +120.5k/-32.6k (Human), +0/-0 (Bot).
* **Contributors (according to last 7 days commits)** (Total: 163 Humans, 0 Bots):
  - **Top Humans**:
    - `Teknium <127238744+teknium1@users.noreply.github.com>` (Human): 107 commits, +21.4k/-13.5k lines
    - `teknium1 <127238744+teknium1@users.noreply.github.com>` (Human): 91 commits, +12.2k/-2.7k lines
    - `kshitijk4poor <82637225+kshitijk4poor@users.noreply.github.com>` (Human): 77 commits, +3.7k/-941 lines
    - `Ben <ben@nousresearch.com>` (Human): 43 commits, +7.8k/-213 lines
    - `Brooklyn Nicholson <brooklyn.bb.nicholson@gmail.com>` (Human): 40 commits, +5.1k/-939 lines
    - `xxxigm <tuancanhnguyen706@gmail.com>` (Human): 25 commits, +2.0k/-37 lines
    - `Ben Barclay <ben@nousresearch.com>` (Human): 22 commits, +5.9k/-683 lines
    - `Hao Zhe <haozhe4547@gmail.com>` (Human): 21 commits, +5.6k/-1.0k lines
    - `Austin Pickett <pickett.austin@gmail.com>` (Human): 13 commits, +2.3k/-111 lines
    - `teknium <127238744+teknium1@users.noreply.github.com>` (Human): 11 commits, +460/-136 lines
<!-- END_BD_HERMES_AGENT -->
<!-- START_RF_HERMES_AGENT -->
* **Recent Focus**:
  - `5ecf3bf0e` fix(slack): report ext-matched audio mimetype for rerouted voice clips
  - `219658416` fix(slack): transcribe in-app voice messages (audio/mp4) instead of failing
  - `45bc4fb37` feat(relay): declare relevance policy to the connector + document the management plane (#51248)
  - `211ba9c7d` feat(agent): one-shot LLM helper + llm.oneshot gateway RPC (#51261)
  - `af7b7f632` feat(agent): expose coding-context project facts as structured data + project.facts RPC (#51259)
  - `bb7ff7dc3` revert(cron): return cron job storage to per-profile (reverts #32117 + #50993) (#51116)
  - `7daa6d83f` style(desktop): soften inline code and expanded tool chrome
  - `48a8f8416` fix(desktop): toggle preview rail and open in browser
  - `d0af7fc95` feat(desktop): detect tool previews into composer status stack
  - `cb17a9efb` fix(desktop): stop auto-opening tool previews
  - `ba9e3a491` feat(memory): Honcho OAuth connect — desktop and CLI flows + token refresh (#44335)
  - `3fffecbda` feat(desktop): add timeline rail for long chat threads
  - `88e136448` fix(agent): shrink anthropic-native image history
  - `a6b670d4a` fix(desktop): avoid stack overflow on embedded image replay
  - `3c1058e2e` fix(computer-use): set stdin=DEVNULL on cua-driver subprocess calls
<!-- END_RF_HERMES_AGENT -->
### NanoBot (`HKUDS/nanobot`)
<!-- START_BD_NANOBOT -->
* **Status**: Highly Active (Total: 134 commits [132 H / 2 B], 1 tag/release in the last week). Lines added/deleted: +14.0k/-3.0k (Human), +105/-3 (Bot).
* **Contributors (according to last 7 days commits)** (Total: 18 Humans, 1 Bots):
  - **Top Humans**:
    - `Xubin Ren <52506698+Re-bin@users.noreply.github.com>` (Human): 36 commits, +6.4k/-728 lines
    - `chengyongru <chengyongru.ai@gmail.com>` (Human): 35 commits, +2.4k/-669 lines
    - `chengyongru <2755839590@qq.com>` (Human): 24 commits, +2.5k/-1.4k lines
    - `Ilya Gusev <phoenixilya@gmail.com>` (Human): 9 commits, +201/-64 lines
    - `michaelxer <michaelxer@users.noreply.github.com>` (Human): 7 commits, +300/-36 lines
    - `yu-xin-c <2182712990@qq.com>` (Human): 4 commits, +477/-20 lines
    - `sbyinin <2064038+sbyinin@users.noreply.github.com>` (Human): 3 commits, +245/-26 lines
    - `comadreja <comadreja@email.com>` (Human): 2 commits, +26/-2 lines
    - `Haisam <you@example.com>` (Human): 2 commits, +68/-12 lines
    - `w.antar <w.antar@romulus.live>` (Human): 2 commits, +60/-8 lines
  - **Top Bots**:
    - `NanoBot <nanobot@local>` (Bot): 2 commits, +105/-3 lines
<!-- END_BD_NANOBOT -->
<!-- START_RF_NANOBOT -->
* **Recent Focus**:
  - `d2da6df1` docs: align release news dates
  - `701ae556` docs: add v0.2.2 release news
  - `e2e75c91` docs: add June 20 news entry
  - `87f3e08f` docs: remove unreleased 0.2.2 news entry
  - `951fd73c` fix(webui): keep new chat heading on one line
  - `90703002` fix(gateway): restore tty signal mode for ctrl-c
  - `e624943b` fix(gateway): tolerate cancelled channel tasks during shutdown
  - `f80a78d5` fix(webui): preserve fork replies during history refresh
  - `747104c9` fix(gateway): make foreground shutdown responsive
  - `a9d1fdce` fix(webui): follow active turn output after send
  - `83c29292` chore(release): prepare v0.2.2
  - `7170761e` fix(webui): anchor sent prompts during active turns
  - `fbaa8511` fix: close MCP stdio transports from agent task
  - `6efef270` docs: align my tool context window examples
  - `0db9fbe2` chore: default context window to 200k
<!-- END_RF_NANOBOT -->
### PicoClaw (`sipeed/picoclaw`)
<!-- START_BD_PICOCLAW -->
* **Status**: Active (Total: 15 commits [9 H / 6 B], 0 tags/releases in the last week). Lines added/deleted: +1.4k/-350 (Human), +155/-139 (Bot). **8 commits since installed 0.3.0.nightly.20260620.287853ab-1 (ref=287853ab).**
* **Contributors (according to last 7 days commits)** (Total: 6 Humans, 1 Bots):
  - **Top Humans**:
    - `jp39 <jp39@gmx.com>` (Human): 3 commits, +619/-47 lines
    - `lc6464 <lclc6464@outlook.com>` (Human): 2 commits, +803/-300 lines
    - `phoeagon <phoeagon@gmail.com>` (Human): 1 commits, +5/-0 lines
    - `徐闻涵0668001344 <xu.wenhan1@xydigit.com>` (Human): 1 commits, +5/-1 lines
    - `肆月 <2835601846@qq.com>` (Human): 1 commits, +2/-2 lines
    - `徐金城0668000897 <xu.jincheng@xydigit.com>` (Human): 1 commits, +13/-0 lines
  - **Top Bots**:
    - `dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>` (Bot): 6 commits, +155/-139 lines
<!-- END_BD_PICOCLAW -->
<!-- START_RF_PICOCLAW -->
* **Recent Focus**:
  - `646c2db1` build(deps-dev): bump vite from 8.0.13 to 8.0.16 in /web/frontend
  - `a63b44ac` add installation instructions to picoclaw skills search.
  - `d26e4eca` chore(openai_compat): fix golines formatting for CI linter
  - `bbdf746b` fix(evolution): use CompareAndSwap for atomic lockStoreFile repair
  - `409cc051` fix(openai_compat): log warning instead of silently discarding native_search ok check
  - `c5a98a5f` build(deps-dev): bump eslint from 10.2.1 to 10.4.1 in /web/frontend
  - `351ecf01` fix(openai_compat): add ok check for native_search type assertion
  - `f5add27d` fix(evolution): add ok check for LoadOrStore type assertion in lockStoreFile
<!-- END_RF_PICOCLAW -->
### NanoClaw (`nanocoai/nanoclaw`)
<!-- START_BD_NANOCLAW -->
* **Status**: Active (Total: 28 commits [25 H / 3 B], 0 tags/releases in the last week). Lines added/deleted: +1.3k/-448 (Human), +6/-6 (Bot). **3 commits since installed r1859.625264ba4-1 (ref=625264ba4).**
* **Contributors (according to last 7 days commits)** (Total: 7 Humans, 1 Bots):
  - **Top Humans**:
    - `Moshe Krupper <moshekrupper@Moshes-MacBook-Pro.local>` (Human): 16 commits, +861/-366 lines
    - `Gabi Simons <gabi@nanoco.ai>` (Human): 2 commits, +37/-27 lines
    - `Amit Shafnir <amit@nanoco.ai>` (Human): 2 commits, +154/-15 lines
    - `Juntai Park <juntai81@gmail.com>` (Human): 2 commits, +231/-0 lines
    - `Koshkoshinsk <daniel.milliner@gmail.com>` (Human): 1 commits, +35/-24 lines
    - `exe.dev user <exedev@crane-waterpolo.exe.xyz>` (Human): 1 commits, +2/-0 lines
    - `sturdy4days <58111365+sturdy4days@users.noreply.github.com>` (Human): 1 commits, +2/-16 lines
  - **Top Bots**:
    - `github-actions[bot] <github-actions[bot]@users.noreply.github.com>` (Bot): 3 commits, +6/-6 lines
<!-- END_BD_NANOCLAW -->
<!-- START_RF_NANOCLAW -->
* **Recent Focus**:
  - `8f2f788` chore(deps): bump channel adapter install pins to 4.29.0 (skills + setup)
  - `e96d7fd` chore(deps): pin chat SDK to 4.29.0
  - `055cf49` fix(update-skills): nudge into skill updates, rebuild container on re-apply
<!-- END_RF_NANOCLAW -->
### LibreFang (`librefang/librefang`)
<!-- START_BD_LIBREFANG -->
* **Status**: Highly Active (Total: 93 commits [80 H / 13 B], 3 tags/releases in the last week). Lines added/deleted: +36.4k/-10.3k (Human), +766/-750 (Bot).
* **Contributors (according to last 7 days commits)** (Total: 7 Humans, 2 Bots):
  - **Top Humans**:
    - `Evan <suzukaze.haduki@gmail.com>` (Human): 61 commits, +19.1k/-6.3k lines
    - `maoxin1234 <875408344@qq.com>` (Human): 5 commits, +1.6k/-159 lines
    - `Павло <pavvers1@gmail.com>` (Human): 5 commits, +14.1k/-3.7k lines
    - `Paco Navarrete <paco.j.navarrete@gmail.com>` (Human): 4 commits, +1.1k/-42 lines
    - `Vignesh Jagadeesh <vignesh.nrfs@gmail.com>` (Human): 2 commits, +425/-33 lines
    - `BunnyMoth <bunnymoth@proton.me>` (Human): 2 commits, +40/-31 lines
    - `HuaGu-Dragon <1801943622@qq.com>` (Human): 1 commits, +28/-19 lines
  - **Top Bots**:
    - `dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>` (Bot): 7 commits, +630/-638 lines
    - `github-actions[bot] <41898282+github-actions[bot]@users.noreply.github.com>` (Bot): 6 commits, +136/-112 lines
<!-- END_BD_LIBREFANG -->
* **Note**: LibreFang is a community fork of the former `RightNow-AI/openfang` repository, which had **17,623 stars** and **2,252 forks** before going stale.
<!-- START_RF_LIBREFANG -->
* **Recent Focus**:
  - `1160eb0c` feat: pluggable context-rewrite modules — per-agent engine + host-run request_llm_summary (closes #6264) (#6287)
  - `34107567` fix(kernel): forward web-UI-initiated delegation results to the home channel (refs #6266) (#6286)
  - `67e9fe27` fix(metering): gate provider hourly token budget pre-call so exhaustion flags the fallback chain (#5980) (#5988)
  - `06ace6c1` fix(changelog): merge the dual [Unreleased] sections into one at the top (#6285)
  - `480d78ee` fix(cli): handle /new in the TUI chat surfaces (closes #6265) (#6284)
  - `2aca289d` fix(desktop): merge updater plugin config into base tauri.conf.json (closes #6270) (#6283)
  - `f9088c69` perf(runtime): JSON-aware token estimation for tool paths (#6281)
  - `fe306ece` chore(deps): bump wasmtime from 45.0.2 to 46.0.0 (#6277)
  - `d8bf80e9` feat(cli): localize TUI Onboarding Wizard and Agents screen (#6253)
  - `d762258b` chore(deps): bump cron from 0.16.0 to 0.17.0 (#6278)
  - `b5c8b039` fix(runtime): embed developer-loop placeholder in first result delivery (closes #6251) (#6254)
  - `70fefa5f` fix(kernel): persist agent skill & MCP-server assignments to agent.toml (#6046)
  - `5b136d40` chore(deps): bump the cargo-minor-patch group across 1 directory with 8 updates (#6276)
  - `abbf8995` fix(channels,kernel): kill sidecar child on shutdown + forward async delegation result to channel (#6267)
  - `5c4f3ae8` test(runtime): add token-estimation accuracy benchmark with multi-tokenizer baselines (#6269)
<!-- END_RF_LIBREFANG -->
---
## 📋 Instruction Guide: Recreating this Analysis

**Fully Automated Update**: You can run the automation script `scripts/update-activity.py` with the `--write` (or `-w`) flag to automatically pull all repository updates, calculate the statistics, and optionally write the updated tables directly back into this file:
```bash
python scripts/update-activity.py [--write]
```
