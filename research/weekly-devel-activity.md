# Active AI Assistants: Weekly Development Activity

This document tracks repository activity, commit counts, merge frequency, and release cycles for active assistant projects.

---

#### 📊 Summary of Last 7 Days Activity (June 15, 2026 – June 22, 2026)

<!-- START_TABLES -->
#### Repository Overview & Package Status
| Assistant Repo | Stars | Forks | Main Branch | Last Commit | Installed Pkg | Commits Since Pkg | Status |
| :--- | :---: | :---: | :---: | :---: | :--- | :---: | :---: |
| **ironclaw** | 0 | 0 | `main` | 2026-06-22 | `ironclaw-git` @ `ironclaw.v0.29.1.r1448.gc50edb9-1` | 10 | **Highly Active** |
| **zeroclaw** | 0 | 0 | `master` | 2026-06-21 | `zeroclaw-git` @ `0.8.1.r16.g13a8a857a-1` | 29 | **Highly Active** |
| **hermes-agent** | 0 | 0 | `main` | 2026-06-21 | — | — | **Highly Active** |
| **nanobot** | 0 | 0 | `main` | 2026-06-21 | — | — | **Highly Active** |
| **picoclaw** | 0 | 0 | `main` | 2026-06-18 | `picoclaw-git` @ `0.3.0.nightly.20260620.287853ab-1` | 0 | **Active** |
| **nanoclaw** | 0 | 0 | `main` | 2026-06-18 | `nanoclaw-git` @ `r1859.625264ba4-1` | 0 | **Active** |
| **librefang** | 0 | 0 | `main` | 2026-06-22 | — | — | **Highly Active** |

#### Weekly Activity Metrics (Human vs Bot)
| Assistant Repo | Commits / Week | Lines Added (Human/Bot) | Lines Deleted (Human/Bot) | Merges (Last Wk) | Releases/Tags (Last Wk) | Avg Commits/Wk (4 Wks) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **ironclaw** | **103** / 0 | 100.6k / 0 | 13.3k / 0 | 0 | 0 | 140.5 |
| **zeroclaw** | **210** / 1 | 80.2k / 546 | 17.3k / 1.2k | 0 | 1 | 137.8 |
| **hermes-agent** | **706** / 0 | 118.7k / 0 | 38.9k / 0 | 71 | 1 | 705.8 |
| **nanobot** | **125** / 2 | 10.6k / 105 | 2.6k / 3 | 2 | 0 | 104.2 |
| **picoclaw** | **20** / 5 | 2.2k / 43 | 511 / 44 | 15 | 1 | 33.5 |
| **nanoclaw** | **25** / 5 | 1.3k / 11 | 399 / 11 | 15 | 1 | 31.0 |
| **librefang** | **76** / 14 | 29.7k / 969 | 8.4k / 880 | 0 | 3 | 86.2 |
<!-- END_TABLES -->

---

## 🔍 Repository Breakdown

> [!NOTE]
> The contributor lists and activity metrics for each repository below are compiled according to commits from the last 7 days.


### ZeroClaw (`zeroclaw-labs/zeroclaw`)
<!-- START_BD_ZEROCLAW -->
* **Status**: Highly Active (Total: 211 commits [210 H / 1 B], 1 tag/release in the last week). Lines added/deleted: +80.2k/-17.3k (Human), +546/-1.2k (Bot). **29 commits since installed 0.8.1.r16.g13a8a857a-1 (ref=13a8a857a).**
* **Contributors (according to last 7 days commits)** (Total: 40 Humans, 1 Bots):
  - **Top Humans**:
    - `Dan Gilles <dfgilles@uchicago.edu>` (Human): 40 commits, +10.4k/-1.4k lines
    - `Marc Collins <marc@nnet.tech>` (Human): 37 commits, +34.9k/-8.4k lines
    - `Alix-007 <li.long15@xydigit.com>` (Human): 25 commits, +1.3k/-136 lines
    - `Shane Engelman <contact@shane.gg>` (Human): 24 commits, +16.0k/-4.5k lines
    - `JordanTheJet <morepencils@gmail.com>` (Human): 10 commits, +1.0k/-146 lines
    - `Jason Perlow <jperlow@gmail.com>` (Human): 9 commits, +1.0k/-195 lines
    - `pick-cat <huang.ting3@xydigit.com>` (Human): 8 commits, +792/-48 lines
    - `chengzhichao-xydt <cheng.zhichao@xydigit.com>` (Human): 8 commits, +499/-52 lines
    - `Tidux <jon@borg.moe>` (Human): 5 commits, +2.1k/-161 lines
    - `Cherilyn Buren <88433283+NiuBlibing@users.noreply.github.com>` (Human): 4 commits, +1.1k/-66 lines
  - **Top Bots**:
    - `dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>` (Bot): 1 commits, +546/-1.2k lines
<!-- END_BD_ZEROCLAW -->
<!-- START_RF_ZEROCLAW -->
* **Recent Focus**:
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
* **Status**: Highly Active (Total: 103 commits [103 H / 0 B], 0 tags/releases in the last week). Lines added/deleted: +100.6k/-13.3k (Human), +0/-0 (Bot). **10 commits since installed ironclaw.v0.29.1.r1448.gc50edb9-1 (ref=c50edb9).**
* **Contributors (according to last 7 days commits)** (Total: 13 Humans, 0 Bots):
  - **Top Humans**:
    - `firat.sertgoz <firat.sertgoz@near.ai>` (Human): 37 commits, +17.1k/-2.6k lines
    - `Illia Polosukhin <ilblackdragon@gmail.com>` (Human): 15 commits, +26.7k/-3.0k lines
    - `Henry Park <henrypark133@gmail.com>` (Human): 14 commits, +25.7k/-3.2k lines
    - `Coffee <zjchen1234@foxmail.com>` (Human): 13 commits, +5.8k/-1.1k lines
    - `jinxin <106428113+italic-jinxin@users.noreply.github.com>` (Human): 6 commits, +2.9k/-1.0k lines
    - `Pranav Raja <pranavraja99@gmail.com>` (Human): 6 commits, +1.8k/-45 lines
    - `Robert Yan <46699230+think-in-universe@users.noreply.github.com>` (Human): 4 commits, +2.8k/-218 lines
    - `aiworkbot <robert.yan@near.ai>` (Human): 3 commits, +1.8k/-1.0k lines
    - `Daniel Wang <5139554+danielwpz@users.noreply.github.com>` (Human): 1 commits, +4/-29 lines
    - `loopstring <yutingytw@gmail.com>` (Human): 1 commits, +442/-53 lines
<!-- END_BD_IRONCLAW -->
<!-- START_RF_IRONCLAW -->
* **Recent Focus**:
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
* **Status**: Highly Active (Total: 706 commits [706 H / 0 B], 1 tag/release in the last week). Lines added/deleted: +118.7k/-38.9k (Human), +0/-0 (Bot).
* **Contributors (according to last 7 days commits)** (Total: 168 Humans, 0 Bots):
  - **Top Humans**:
    - `Teknium <127238744+teknium1@users.noreply.github.com>` (Human): 108 commits, +21.2k/-5.9k lines
    - `teknium1 <127238744+teknium1@users.noreply.github.com>` (Human): 79 commits, +10.6k/-2.2k lines
    - `kshitijk4poor <82637225+kshitijk4poor@users.noreply.github.com>` (Human): 68 commits, +3.4k/-924 lines
    - `Ben <ben@nousresearch.com>` (Human): 42 commits, +7.5k/-210 lines
    - `Brooklyn Nicholson <brooklyn.bb.nicholson@gmail.com>` (Human): 31 commits, +3.4k/-653 lines
    - `xxxigm <tuancanhnguyen706@gmail.com>` (Human): 28 commits, +1.7k/-42 lines
    - `Ben Barclay <ben@nousresearch.com>` (Human): 19 commits, +4.8k/-670 lines
    - `Austin Pickett <pickett.austin@gmail.com>` (Human): 18 commits, +3.0k/-180 lines
    - `Hao Zhe <haozhe4547@gmail.com>` (Human): 18 commits, +5.0k/-955 lines
    - `liuhao1024 <sunsky.lau@gmail.com>` (Human): 13 commits, +1.1k/-83 lines
<!-- END_BD_HERMES_AGENT -->
<!-- START_RF_HERMES_AGENT -->
* **Recent Focus**:
  - `2b3a4f0af` fix(agent): strip stale reasoning_content when falling back to a strict provider (#50480)
  - `73340d8be` chore: add buihongduc132 to AUTHOR_MAP for mem0 salvage
  - `452a725ae` fix(mem0): address PR review — restore docstrings, keep api_key required
  - `b6d2ac176` feat(mem0): add self-hosted support via MEM0_HOST / host config
  - `012f40c98` fix(status): cross-platform start-time fingerprint via psutil fallback
  - `1cefc2a24` test(whatsapp): fix port-spares-client test race (listen before announce + retry connect)
  - `0fb3b13b0` chore: add valentt to AUTHOR_MAP for #43846 salvage
  - `615a8e651` fix(whatsapp): add missing re import + fix test import path after adapter relocation
  - `069ab40c5` fix(whatsapp): only kill LISTENers when freeing the bridge port, never clients
  - `77fdbbfe8` fix(whatsapp): validate bridge PID identity before killing stale pidfile entry
  - `e44772314` fix(process-registry): re-validate PID identity before killing host processes
  - `84e1d31e5` refactor(kanban): fold worker/orchestrator skills into injected guidance (#50473)
  - `e5e258363` fix(desktop): relaunch on Linux after in-app update instead of hanging (#45205)
  - `1f6994d1e` chore(release): add AUTHOR_MAP entry for #45205 salvage (EtherAura)
  - `13ce81190` fix: show desktop approval fallback (#46548)
<!-- END_RF_HERMES_AGENT -->
### NanoBot (`HKUDS/nanobot`)
<!-- START_BD_NANOBOT -->
* **Status**: Highly Active (Total: 127 commits [125 H / 2 B], 0 tags/releases in the last week). Lines added/deleted: +10.6k/-2.6k (Human), +105/-3 (Bot).
* **Contributors (according to last 7 days commits)** (Total: 21 Humans, 1 Bots):
  - **Top Humans**:
    - `chengyongru <chengyongru.ai@gmail.com>` (Human): 45 commits, +2.9k/-1.2k lines
    - `Xubin Ren <52506698+Re-bin@users.noreply.github.com>` (Human): 22 commits, +3.1k/-213 lines
    - `chengyongru <2755839590@qq.com>` (Human): 15 commits, +1.6k/-968 lines
    - `Ilya Gusev <phoenixilya@gmail.com>` (Human): 9 commits, +201/-64 lines
    - `michaelxer <michaelxer@users.noreply.github.com>` (Human): 7 commits, +300/-36 lines
    - `yu-xin-c <2182712990@qq.com>` (Human): 4 commits, +477/-20 lines
    - `Stellar鱼 <2182712990@qq.com>` (Human): 3 commits, +193/-15 lines
    - `sbyinin <2064038+sbyinin@users.noreply.github.com>` (Human): 3 commits, +245/-26 lines
    - `comadreja <comadreja@email.com>` (Human): 3 commits, +27/-2 lines
    - `Haisam <you@example.com>` (Human): 2 commits, +68/-12 lines
  - **Top Bots**:
    - `NanoBot <nanobot@local>` (Bot): 2 commits, +105/-3 lines
<!-- END_BD_NANOBOT -->
<!-- START_RF_NANOBOT -->
* **Recent Focus**:
  - `9db3dc5e` docs(readme): update news through 2026-06-20
  - `dbf3c4b2` feat(sdk): expand Python runtime controls
  - `f4cc0014` refactor(sdk): pass run hooks explicitly
  - `b6a9a972` test(sdk): cover concurrent run hook isolation
  - `a19725bc` docs: add note about ephemeral guard and per-call hooks contextvar
  - `345ef805` fix: update facade tests for contextvar hooks + fix ephemeral guard
  - `0bb1b0b3` fix(sdk): use contextvars for per-call hooks to prevent concurrent run() race
  - `fede2ecf` test(websocket): expect optional Keenable search key
  - `d30f3d46` fix(webui): allow optional Keenable search key
  - `5feb6f48` refactor(web): use module constant for Keenable search URL
  - `74daa81a` feat(web): allow Keenable search without an API key
  - `a5768a4e` fix(tools): reject unknown builtin parameters
  - `85036bac` test(telegram): cover rich message fallback latch
  - `a8c65b50` fix: narrow rich capability error detection to prevent false latch
  - `e9494c1d` feat(telegram): add Bot API 10.1 sendRichMessage support
<!-- END_RF_NANOBOT -->
### PicoClaw (`sipeed/picoclaw`)
<!-- START_BD_PICOCLAW -->
* **Status**: Active (Total: 25 commits [20 H / 5 B], 1 tag/release in the last week). Lines added/deleted: +2.2k/-511 (Human), +43/-44 (Bot). **0 commits since installed 0.3.0.nightly.20260620.287853ab-1 (ref=287853ab).**
* **Contributors (according to last 7 days commits)** (Total: 9 Humans, 1 Bots):
  - **Top Humans**:
    - `lc6464 <lclc6464@outlook.com>` (Human): 5 commits, +941/-438 lines
    - `徐闻涵0668001344 <xu.wenhan1@xydigit.com>` (Human): 3 commits, +13/-7 lines
    - `jp39 <jp39@gmx.com>` (Human): 3 commits, +619/-47 lines
    - `程智超0668000959 <cheng.zhichao@xydigit.com>` (Human): 3 commits, +10/-4 lines
    - `SiYue-ZO <2835601846@qq.com>` (Human): 2 commits, +108/-2 lines
    - `肆月 <2835601846@qq.com>` (Human): 1 commits, +2/-2 lines
    - `徐金城0668000897 <xu.jincheng@xydigit.com>` (Human): 1 commits, +13/-0 lines
    - `Guoguo <i@qwq.trade>` (Human): 1 commits, +134/-4 lines
    - `LC <lclc6464@outlook.com>` (Human): 1 commits, +347/-7 lines
  - **Top Bots**:
    - `dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>` (Bot): 5 commits, +43/-44 lines
<!-- END_BD_PICOCLAW -->
<!-- START_RF_PICOCLAW -->
* **Recent Focus**:
  - No new commits in this period.
<!-- END_RF_PICOCLAW -->
### NanoClaw (`nanocoai/nanoclaw`)
<!-- START_BD_NANOCLAW -->
* **Status**: Active (Total: 30 commits [25 H / 5 B], 1 tag/release in the last week). Lines added/deleted: +1.3k/-399 (Human), +11/-11 (Bot). **0 commits since installed r1859.625264ba4-1 (ref=625264ba4).**
* **Contributors (according to last 7 days commits)** (Total: 6 Humans, 1 Bots):
  - **Top Humans**:
    - `Moshe Krupper <moshekrupper@Moshes-MacBook-Pro.local>` (Human): 16 commits, +861/-366 lines
    - `Koshkoshinsk <daniel.milliner@gmail.com>` (Human): 3 commits, +8/-2 lines
    - `Amit Shafnir <amit@nanoco.ai>` (Human): 2 commits, +154/-15 lines
    - `Juntai Park <juntai81@gmail.com>` (Human): 2 commits, +231/-0 lines
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
* **Status**: Highly Active (Total: 90 commits [76 H / 14 B], 3 tags/releases in the last week). Lines added/deleted: +29.7k/-8.4k (Human), +969/-880 (Bot).
* **Contributors (according to last 7 days commits)** (Total: 7 Humans, 2 Bots):
  - **Top Humans**:
    - `Evan <suzukaze.haduki@gmail.com>` (Human): 62 commits, +20.2k/-6.3k lines
    - `Paco Navarrete <paco.j.navarrete@gmail.com>` (Human): 4 commits, +617/-84 lines
    - `Павло <pavvers1@gmail.com>` (Human): 3 commits, +8.2k/-1.8k lines
    - `maoxin1234 <875408344@qq.com>` (Human): 2 commits, +188/-137 lines
    - `Vignesh Jagadeesh <vignesh.nrfs@gmail.com>` (Human): 2 commits, +425/-33 lines
    - `BunnyMoth <bunnymoth@proton.me>` (Human): 2 commits, +40/-31 lines
    - `HuaGu-Dragon <1801943622@qq.com>` (Human): 1 commits, +28/-19 lines
  - **Top Bots**:
    - `github-actions[bot] <41898282+github-actions[bot]@users.noreply.github.com>` (Bot): 7 commits, +134/-110 lines
    - `dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>` (Bot): 7 commits, +835/-770 lines
<!-- END_BD_LIBREFANG -->
* **Note**: LibreFang is a community fork of the former `RightNow-AI/openfang` repository, which had **17,623 stars** and **2,252 forks** before going stale.
<!-- START_RF_LIBREFANG -->
* **Recent Focus**:
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
  - `33c2b13d` feat(runtime,kernel): non-blocking agent_send via the async-task tracker (#6044)
  - `6ced8fa3` fix(runtime): spill oversized shell_exec output instead of truncating (#6242) (#6246)
<!-- END_RF_LIBREFANG -->
---
## 📋 Instruction Guide: Recreating this Analysis

**Fully Automated Update**: You can run the automation script `scripts/update-activity.py` with the `--write` (or `-w`) flag to automatically pull all repository updates, calculate the statistics, and optionally write the updated tables directly back into this file:
```bash
python scripts/update-activity.py [--write]
```
