# Active AI Assistants: Weekly Development Activity

This document tracks repository activity, commit counts, merge frequency, and release cycles for active assistant projects.

---

#### 📊 Summary of Last 7 Days Activity (June 15, 2026 – June 22, 2026)

<!-- START_TABLES -->
#### Repository Overview & Package Status
| Assistant Repo | Stars | Forks | Main Branch | Last Commit | Installed Pkg | Commits Since Pkg | Status |
| :--- | :---: | :---: | :---: | :---: | :--- | :---: | :---: |
| **ironclaw** | 12,470 | 1,460 | `main` | 2026-06-22 | `ironclaw-git` @ `ironclaw.v0.29.1.r1448.gc50edb9-1` | 12 | **Highly Active** |
| **zeroclaw** | 31,991 | 4,752 | `master` | 2026-06-22 | `zeroclaw-git` @ `0.8.1.r16.g13a8a857a-1` | 37 | **Highly Active** |
| **hermes-agent** | 199,631 | 35,476 | `main` | 2026-06-22 | — | — | **Highly Active** |
| **nanobot** | 44,563 | 7,871 | `main` | 2026-06-22 | — | — | **Highly Active** |
| **picoclaw** | 29,458 | 4,238 | `main` | 2026-06-18 | `picoclaw-git` @ `0.3.0.nightly.20260620.287853ab-1` | 0 | **Active** |
| **nanoclaw** | 29,946 | 12,899 | `main` | 2026-06-18 | `nanoclaw-git` @ `r1859.625264ba4-1` | 0 | **Active** |
| **librefang** | 307 | 62 | `main` | 2026-06-22 | — | — | **Highly Active** |

#### Weekly Activity Metrics (Human vs Bot)
| Assistant Repo | Commits / Week | Lines Added (Human/Bot) | Lines Deleted (Human/Bot) | Merges (Last Wk) | Releases/Tags (Last Wk) | Avg Commits/Wk (4 Wks) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **ironclaw** | **94** / 0 | 95.7k / 0 | 13.0k / 0 | 0 | 0 | 137.5 |
| **zeroclaw** | **184** / 0 | 75.3k / 0 | 17.4k / 0 | 0 | 1 | 138.8 |
| **hermes-agent** | **737** / 0 | 119.9k / 0 | 32.5k / 0 | 80 | 1 | 701.2 |
| **nanobot** | **146** / 2 | 14.9k / 105 | 4.0k / 3 | 1 | 0 | 113.0 |
| **picoclaw** | **13** / 5 | 1.7k / 43 | 362 / 44 | 15 | 0 | 33.5 |
| **nanoclaw** | **24** / 5 | 1.3k / 11 | 398 / 11 | 13 | 1 | 30.5 |
| **librefang** | **70** / 12 | 28.9k / 831 | 8.3k / 747 | 0 | 4 | 83.0 |
<!-- END_TABLES -->

---

## 🔍 Repository Breakdown

> [!NOTE]
> The contributor lists and activity metrics for each repository below are compiled according to commits from the last 7 days.


### ZeroClaw (`zeroclaw-labs/zeroclaw`)
<!-- START_BD_ZEROCLAW -->
* **Status**: Highly Active (Total: 184 commits [184 H / 0 B], 1 tag/release in the last week). Lines added/deleted: +75.3k/-17.4k (Human), +0/-0 (Bot). **37 commits since installed 0.8.1.r16.g13a8a857a-1 (ref=13a8a857a).**
* **Contributors (according to last 7 days commits)** (Total: 32 Humans, 0 Bots):
  - **Top Humans**:
    - `Marc Collins <marc@nnet.tech>` (Human): 38 commits, +36.9k/-10.0k lines
    - `Dan Gilles <dfgilles@uchicago.edu>` (Human): 32 commits, +8.7k/-1.1k lines
    - `Shane Engelman <contact@shane.gg>` (Human): 22 commits, +15.0k/-3.7k lines
    - `Alix-007 <li.long15@xydigit.com>` (Human): 21 commits, +995/-87 lines
    - `Jason Perlow <jperlow@gmail.com>` (Human): 10 commits, +985/-206 lines
    - `JordanTheJet <morepencils@gmail.com>` (Human): 10 commits, +1.0k/-146 lines
    - `pick-cat <huang.ting3@xydigit.com>` (Human): 9 commits, +805/-50 lines
    - `chengzhichao-xydt <cheng.zhichao@xydigit.com>` (Human): 5 commits, +365/-28 lines
    - `Tidux <jon@borg.moe>` (Human): 4 commits, +2.1k/-160 lines
    - `ZOOWH <xu.wenhan1@xydigit.com>` (Human): 3 commits, +243/-5 lines
<!-- END_BD_ZEROCLAW -->
<!-- START_RF_ZEROCLAW -->
* **Recent Focus**:
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
* **Status**: Highly Active (Total: 94 commits [94 H / 0 B], 0 tags/releases in the last week). Lines added/deleted: +95.7k/-13.0k (Human), +0/-0 (Bot). **12 commits since installed ironclaw.v0.29.1.r1448.gc50edb9-1 (ref=c50edb9).**
* **Contributors (according to last 7 days commits)** (Total: 13 Humans, 0 Bots):
  - **Top Humans**:
    - `firat.sertgoz <firat.sertgoz@near.ai>` (Human): 34 commits, +13.6k/-2.3k lines
    - `Illia Polosukhin <ilblackdragon@gmail.com>` (Human): 15 commits, +26.7k/-3.0k lines
    - `Henry Park <henrypark133@gmail.com>` (Human): 11 commits, +23.5k/-3.2k lines
    - `Coffee <zjchen1234@foxmail.com>` (Human): 9 commits, +4.9k/-961 lines
    - `jinxin <106428113+italic-jinxin@users.noreply.github.com>` (Human): 7 commits, +4.1k/-1.1k lines
    - `Robert Yan <46699230+think-in-universe@users.noreply.github.com>` (Human): 5 commits, +3.7k/-292 lines
    - `Pranav Raja <pranavraja99@gmail.com>` (Human): 5 commits, +1.5k/-38 lines
    - `aiworkbot <robert.yan@near.ai>` (Human): 3 commits, +1.8k/-1.0k lines
    - `Daniel Wang <5139554+danielwpz@users.noreply.github.com>` (Human): 1 commits, +4/-29 lines
    - `loopstring <yutingytw@gmail.com>` (Human): 1 commits, +442/-53 lines
<!-- END_BD_IRONCLAW -->
<!-- START_RF_IRONCLAW -->
* **Recent Focus**:
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
* **Status**: Highly Active (Total: 737 commits [737 H / 0 B], 1 tag/release in the last week). Lines added/deleted: +119.9k/-32.5k (Human), +0/-0 (Bot).
* **Contributors (according to last 7 days commits)** (Total: 165 Humans, 0 Bots):
  - **Top Humans**:
    - `Teknium <127238744+teknium1@users.noreply.github.com>` (Human): 105 commits, +22.8k/-13.2k lines
    - `teknium1 <127238744+teknium1@users.noreply.github.com>` (Human): 93 commits, +12.2k/-2.7k lines
    - `kshitijk4poor <82637225+kshitijk4poor@users.noreply.github.com>` (Human): 72 commits, +3.4k/-910 lines
    - `Ben <ben@nousresearch.com>` (Human): 42 commits, +7.5k/-210 lines
    - `Brooklyn Nicholson <brooklyn.bb.nicholson@gmail.com>` (Human): 36 commits, +4.1k/-816 lines
    - `xxxigm <tuancanhnguyen706@gmail.com>` (Human): 28 commits, +1.8k/-44 lines
    - `Hao Zhe <haozhe4547@gmail.com>` (Human): 21 commits, +5.6k/-1.0k lines
    - `Ben Barclay <ben@nousresearch.com>` (Human): 21 commits, +5.4k/-682 lines
    - `Austin Pickett <pickett.austin@gmail.com>` (Human): 18 commits, +3.0k/-180 lines
    - `liuhao1024 <sunsky.lau@gmail.com>` (Human): 14 commits, +1.2k/-100 lines
<!-- END_BD_HERMES_AGENT -->
<!-- START_RF_HERMES_AGENT -->
* **Recent Focus**:
  - `b1b20270c` refactor(memory): move write-mirror gating behind MemoryManager interface
  - `027cb649e` fix(memory): fail closed on unclear write results
  - `c7e0501e9` fix(openviking): drain memory mirror workers on shutdown
  - `70e7132e2` fix(openviking): gate memory writes and add viking_forget
  - `38c56a1e8` fix(computer_use): probe cua-driver-rs release tag, not monorepo releases/latest
  - `e3505c7f7` fix(computer_use): reconcile Linux gate with stale "gated off" comments
  - `f2e37549c` feat(computer_use): cross-platform cua-driver (macOS/Windows/Linux)
  - `17dfc6bec` fix(desktop): set AppUserModelID on Windows so notifications fire (#50808)
  - `ff85af3fc` feat(goals): /goal wait <pid> — park the loop on a background process (#50503)
  - `d4fa2db1c` fix(desktop): show all of a provider's models when searching the composer picker
  - `a6ce9b2fb` fix(picker): keep flat-namespace reseller first-party models in desktop picker
  - `ef6492b64` fix(gateway): cold-start installed Windows gateway after update when none was running (#50804)
  - `da498ed99` chore(release): map ScotterMonk for PR #50145 salvage
  - `e9cd8c5bf` fix(delivery): drop env-var knob, flag all chunking adapters
  - `86e4521cb` fix(delivery): make cron output truncation configurable + adapter-aware
<!-- END_RF_HERMES_AGENT -->
### NanoBot (`HKUDS/nanobot`)
<!-- START_BD_NANOBOT -->
* **Status**: Highly Active (Total: 148 commits [146 H / 2 B], 0 tags/releases in the last week). Lines added/deleted: +14.9k/-4.0k (Human), +105/-3 (Bot).
* **Contributors (according to last 7 days commits)** (Total: 20 Humans, 1 Bots):
  - **Top Humans**:
    - `chengyongru <chengyongru.ai@gmail.com>` (Human): 46 commits, +2.9k/-1.0k lines
    - `Xubin Ren <52506698+Re-bin@users.noreply.github.com>` (Human): 31 commits, +6.4k/-724 lines
    - `chengyongru <2755839590@qq.com>` (Human): 29 commits, +3.0k/-2.0k lines
    - `Ilya Gusev <phoenixilya@gmail.com>` (Human): 9 commits, +201/-64 lines
    - `michaelxer <michaelxer@users.noreply.github.com>` (Human): 7 commits, +300/-36 lines
    - `yu-xin-c <2182712990@qq.com>` (Human): 4 commits, +477/-20 lines
    - `sbyinin <2064038+sbyinin@users.noreply.github.com>` (Human): 3 commits, +245/-26 lines
    - `comadreja <comadreja@email.com>` (Human): 3 commits, +27/-2 lines
    - `Haisam <you@example.com>` (Human): 2 commits, +68/-12 lines
    - `w.antar <w.antar@romulus.live>` (Human): 2 commits, +60/-8 lines
  - **Top Bots**:
    - `NanoBot <nanobot@local>` (Bot): 2 commits, +105/-3 lines
<!-- END_BD_NANOBOT -->
<!-- START_RF_NANOBOT -->
* **Recent Focus**:
  - `f80a78d5` fix(webui): preserve fork replies during history refresh
  - `747104c9` fix(gateway): make foreground shutdown responsive
  - `a9d1fdce` fix(webui): follow active turn output after send
  - `83c29292` chore(release): prepare v0.2.2
  - `7170761e` fix(webui): anchor sent prompts during active turns
  - `fbaa8511` fix: close MCP stdio transports from agent task
  - `6efef270` docs: align my tool context window examples
  - `0db9fbe2` chore: default context window to 200k
  - `991422a3` refactor: simplify CLI Apps route await
  - `a67285e6` fix: use async CLI Apps catalog refresh
  - `dd2cb4ca` fix: refresh optional CLI Apps catalogs
  - `22164058` fix: avoid stuck Apps loading during catalog refresh
  - `1cd5a0e0` fix: keep refreshable Codex OAuth configured
  - `b8abe554` Avoid blocking settings on CLI Apps catalog refresh
  - `7b153c5a` Avoid refreshing Codex token in settings
<!-- END_RF_NANOBOT -->
### PicoClaw (`sipeed/picoclaw`)
<!-- START_BD_PICOCLAW -->
* **Status**: Active (Total: 18 commits [13 H / 5 B], 0 tags/releases in the last week). Lines added/deleted: +1.7k/-362 (Human), +43/-44 (Bot). **0 commits since installed 0.3.0.nightly.20260620.287853ab-1 (ref=287853ab).**
* **Contributors (according to last 7 days commits)** (Total: 7 Humans, 1 Bots):
  - **Top Humans**:
    - `徐闻涵0668001344 <xu.wenhan1@xydigit.com>` (Human): 3 commits, +13/-7 lines
    - `jp39 <jp39@gmx.com>` (Human): 3 commits, +619/-47 lines
    - `lc6464 <lclc6464@outlook.com>` (Human): 2 commits, +803/-300 lines
    - `SiYue-ZO <2835601846@qq.com>` (Human): 2 commits, +108/-2 lines
    - `肆月 <2835601846@qq.com>` (Human): 1 commits, +2/-2 lines
    - `徐金城0668000897 <xu.jincheng@xydigit.com>` (Human): 1 commits, +13/-0 lines
    - `Guoguo <i@qwq.trade>` (Human): 1 commits, +134/-4 lines
  - **Top Bots**:
    - `dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>` (Bot): 5 commits, +43/-44 lines
<!-- END_BD_PICOCLAW -->
<!-- START_RF_PICOCLAW -->
* **Recent Focus**:
  - No new commits in this period.
<!-- END_RF_PICOCLAW -->
### NanoClaw (`nanocoai/nanoclaw`)
<!-- START_BD_NANOCLAW -->
* **Status**: Active (Total: 29 commits [24 H / 5 B], 1 tag/release in the last week). Lines added/deleted: +1.3k/-398 (Human), +11/-11 (Bot). **0 commits since installed r1859.625264ba4-1 (ref=625264ba4).**
* **Contributors (according to last 7 days commits)** (Total: 6 Humans, 1 Bots):
  - **Top Humans**:
    - `Moshe Krupper <moshekrupper@Moshes-MacBook-Pro.local>` (Human): 16 commits, +861/-366 lines
    - `Amit Shafnir <amit@nanoco.ai>` (Human): 2 commits, +154/-15 lines
    - `Juntai Park <juntai81@gmail.com>` (Human): 2 commits, +231/-0 lines
    - `Koshkoshinsk <daniel.milliner@gmail.com>` (Human): 2 commits, +7/-1 lines
    - `exe.dev user <exedev@crane-waterpolo.exe.xyz>` (Human): 1 commits, +2/-0 lines
    - `sturdy4days <58111365+sturdy4days@users.noreply.github.com>` (Human): 1 commits, +2/-16 lines
  - **Top Bots**:
    - `github-actions[bot] <github-actions[bot]@users.noreply.github.com>` (Bot): 5 commits, +11/-11 lines
<!-- END_BD_NANOCLAW -->
<!-- START_RF_NANOCLAW -->
* **Recent Focus**:
  - No new commits in this period.
<!-- END_RF_NANOCLAW -->
### LibreFang (`librefang/librefang`)
<!-- START_BD_LIBREFANG -->
* **Status**: Highly Active (Total: 82 commits [70 H / 12 B], 4 tags/releases in the last week). Lines added/deleted: +28.9k/-8.3k (Human), +831/-747 (Bot).
* **Contributors (according to last 7 days commits)** (Total: 7 Humans, 2 Bots):
  - **Top Humans**:
    - `Evan <suzukaze.haduki@gmail.com>` (Human): 59 commits, +19.6k/-6.2k lines
    - `Павло <pavvers1@gmail.com>` (Human): 3 commits, +8.2k/-1.8k lines
    - `maoxin1234 <875408344@qq.com>` (Human): 2 commits, +188/-137 lines
    - `Vignesh Jagadeesh <vignesh.nrfs@gmail.com>` (Human): 2 commits, +425/-33 lines
    - `BunnyMoth <bunnymoth@proton.me>` (Human): 2 commits, +40/-31 lines
    - `Paco Navarrete <paco.j.navarrete@gmail.com>` (Human): 1 commits, +472/-34 lines
    - `HuaGu-Dragon <1801943622@qq.com>` (Human): 1 commits, +28/-19 lines
  - **Top Bots**:
    - `github-actions[bot] <41898282+github-actions[bot]@users.noreply.github.com>` (Bot): 6 commits, +128/-104 lines
    - `dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>` (Bot): 6 commits, +703/-643 lines
<!-- END_BD_LIBREFANG -->
* **Note**: LibreFang is a community fork of the former `RightNow-AI/openfang` repository, which had **17,623 stars** and **2,252 forks** before going stale.
<!-- START_RF_LIBREFANG -->
* **Recent Focus**:
  - `c643a324` release: v2026.6.22-beta.22 (#6273)
  - `a59e28f2` fix(installer): fall back to installable release, roll back bad upgrades (#6272)
  - `feb7e3f5` release: v2026.6.22-beta.21 (#6268)
  - `ed16b20c` refactor(api): make WebhookStore async-safe with tokio RwLock (#6256)
  - `dfb53e03` chore(runtime): warn on cleanup failures in shell and web_fetch_to_file (#6255)
  - `91aa92c3` fix(runtime): channel_send replies to the group, not the speaker (#6261)
  - `24b9fe17` fix(channels): rank explicit per-peer bindings above the sidecar instance default (#6258)
  - `e2b40976` chore(secrets): replace detect-secrets baseline with gitleaks (#6262)
  - `ab59e2d3` feat(mcp): confidential OAuth clients via client_secret_env (revives #5060) (#6260)
  - `9b7bf00f` fix(ci): clear .secrets.baseline drift from #6190 and hard-error pre-commit when detect-secrets missing (#6259)
  - `5595d7f6` docs: update contributors and star history (#6252)
  - `842ebc25` fix(channels): deliver streaming final answer as a fresh notifying message (#6248) (#6249)
  - `3f2a1626` fix(sec): zeroize EmbeddingConfig.api_key on drop (partial LF-001) (#6190)
  - `9da53e0c` feat(cli): localize TUI main interface, welcome, sessions, and peers screens (#6241)
  - `4d438b9b` fix(runtime): allow close_range, getresuid/gid, and pipe splicing syscalls in seccomp sandbox (#6221)
<!-- END_RF_LIBREFANG -->
---
## 📋 Instruction Guide: Recreating this Analysis

**Fully Automated Update**: You can run the automation script `scripts/update-activity.py` with the `--write` (or `-w`) flag to automatically pull all repository updates, calculate the statistics, and optionally write the updated tables directly back into this file:
```bash
python scripts/update-activity.py [--write]
```
