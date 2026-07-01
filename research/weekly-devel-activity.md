# Active AI Assistants: Weekly Development Activity

This document tracks repository activity, commit counts, merge frequency, and release cycles for active assistant projects.

---

#### 📊 Summary of Last 7 Days Activity (June 24, 2026 – July 01, 2026)

<!-- START_TABLES -->
#### Repository Overview & Package Status
| Assistant Repo | Stars | Forks | Main Branch | Last Commit | Installed Pkg | Commits Since Pkg | Status |
| :--- | :---: | :---: | :---: | :---: | :--- | :---: | :---: |
| **zeroclaw** | 32,113 | 4,786 | `master` | 2026-07-02 | `zeroclaw-git` @ `0.8.2.r163.gc1875895a-1` | 24 | **Highly Active** |
| **ironclaw** | 12,492 | 1,462 | `main` | 2026-07-01 | `ironclaw-reborn-git` @ `0.29.1.r1591.g41f6c57-1` | 26 | **Highly Active** |
| **librefang** | 317 | 65 | `main` | 2026-07-01 | `librefang-git` @ `2026.6.29.r9.g83ee2627b-1` | 3 | **Active** |
| **hermes-agent** | 207,205 | 37,549 | `main` | 2026-07-01 | `hermes-agent-git` @ `0.18.0.r1.g76a468e-1` | 0 | **Highly Active** |
| **nanobot** | 44,930 | 7,922 | `main` | 2026-07-01 | — | — | **Highly Active** |
| **picoclaw** | 29,542 | 4,260 | `main` | 2026-06-30 | `picoclaw-git` @ `0.3.0.nightly.20260622.287853ab-1` | 28 | **Active** |
| **nanoclaw** | 30,066 | 12,899 | `main` | 2026-06-30 | — | — | **Active** |

#### Weekly Activity Metrics (Human vs Bot)
| Assistant Repo | Commits / Week | Lines Added (Human/Bot) | Lines Deleted (Human/Bot) | Merges (Last Wk) | Releases/Tags (Last Wk) | Avg Commits/Wk (4 Wks) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **zeroclaw** | **220** / 0 | 57.6k / 0 | 14.9k / 0 | 0 | 1 | 188.0 |
| **ironclaw** | **125** / 4 | 147.4k / 2.2k | 46.5k / 1.2k | 0 | 0 | 119.2 |
| **librefang** | **37** / 6 | 13.8k / 64 | 1.8k / 46 | 0 | 2 | 60.0 |
| **hermes-agent** | **1237** / 3 | 181.2k / 519 | 37.2k / 11 | 119 | 1 | 849.0 |
| **nanobot** | **103** / 0 | 8.9k / 0 | 3.8k / 0 | 0 | 0 | 119.8 |
| **picoclaw** | **11** / 4 | 691 / 28 | 87 / 28 | 16 | 1 | 33.8 |
| **nanoclaw** | **7** / 6 | 698 / 12 | 132 / 12 | 14 | 0 | 34.2 |
<!-- END_TABLES -->

---

## 🔍 Repository Breakdown

> [!NOTE]
> The contributor lists and activity metrics for each repository below are compiled according to commits from the last 7 days.


### ZeroClaw (`zeroclaw-labs/zeroclaw`)
<!-- START_BD_ZEROCLAW -->
* **Status**: Highly Active (Total: 220 commits [220 H / 0 B], 1 tag/release in the last week). Lines added/deleted: +57.6k/-14.9k (Human), +0/-0 (Bot). **24 commits since installed 0.8.2.r163.gc1875895a-1 (ref=c1875895a).**
* **Contributors (according to last 7 days commits)** (Total: 41 Humans, 0 Bots):
  - **Top Humans**:
    - `Dan Gilles <dfgilles@uchicago.edu>` (Human): 44 commits, +8.3k/-1.0k lines
    - `Alix-007 <li.long15@xydigit.com>` (Human): 26 commits, +1.6k/-2 lines
    - `Shane Engelman <contact@shane.gg>` (Human): 23 commits, +10.1k/-9.9k lines
    - `Marc Collins <marc@nnet.tech>` (Human): 15 commits, +10.4k/-1.8k lines
    - `wangmiao0668000666 <wang.miao86@xydigit.com>` (Human): 13 commits, +3.1k/-254 lines
    - `mazhuima <xie.chaolong@xydigit.com>` (Human): 10 commits, +1.2k/-66 lines
    - `ConYel <18070323+ConYel@users.noreply.github.com>` (Human): 9 commits, +887/-88 lines
    - `llagy009 <llagy009@163.com>` (Human): 6 commits, +66/-0 lines
    - `LiLan0125 <li.lan3@xydigit.com>` (Human): 5 commits, +717/-72 lines
    - `Omkumar Solanki <144753825+OmkumarSolanki@users.noreply.github.com>` (Human): 5 commits, +1.4k/-39 lines
<!-- END_BD_ZEROCLAW -->
<!-- START_RF_ZEROCLAW -->
* **Recent Focus**:
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
* **Status**: Highly Active (Total: 129 commits [125 H / 4 B], 0 tags/releases in the last week). Lines added/deleted: +147.4k/-46.5k (Human), +2.2k/-1.2k (Bot). **26 commits since installed 0.29.1.r1591.g41f6c57-1 (ref=41f6c57).**
* **Contributors (according to last 7 days commits)** (Total: 10 Humans, 1 Bots):
  - **Top Humans**:
    - `firat.sertgoz <firat.sertgoz@near.ai>` (Human): 44 commits, +43.8k/-4.4k lines
    - `Henry Park <henrypark133@gmail.com>` (Human): 25 commits, +26.3k/-3.7k lines
    - `jinxin <106428113+italic-jinxin@users.noreply.github.com>` (Human): 20 commits, +19.7k/-14.1k lines
    - `Illia Polosukhin <ilblackdragon@gmail.com>` (Human): 14 commits, +33.3k/-5.1k lines
    - `Coffee <zjchen1234@foxmail.com>` (Human): 6 commits, +9.6k/-11.4k lines
    - `Robert Yan <46699230+think-in-universe@users.noreply.github.com>` (Human): 5 commits, +6.6k/-3.2k lines
    - `Benjamin Kurrek <57506486+BenKurrek@users.noreply.github.com>` (Human): 5 commits, +6.5k/-4.5k lines
    - `Josh Ford <thisisjoshford@gmail.com>` (Human): 3 commits, +335/-6 lines
    - `Emil Bogomolov <emil.bogomolov@near.ai>` (Human): 2 commits, +999/-83 lines
    - `loopstring <yutingytw@gmail.com>` (Human): 1 commits, +294/-29 lines
  - **Top Bots**:
    - `dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>` (Bot): 4 commits, +2.2k/-1.2k lines
<!-- END_BD_IRONCLAW -->
<!-- START_RF_IRONCLAW -->
* **Recent Focus**:
  - `127d034b` test(reborn): prove credential injection reaches the wire (T0-SECRET-INJECT) (#5483)
  - `f2310d92` test(reborn): system-prompt capture seam for model-visible prompt asserts (#5481)
  - `66f2d7b4` test(reborn): error/deny-path coverage for http/shell/mcp tools (T0-ERRPATHS) (#5484)
  - `9e26ef4f` test(reborn): PR-E1 seam constructors for integration coverage (#5440)
  - `48a399cb` fix(webui): avoid thread list refetch on send (#5498)
  - `020af3ce` fix(reborn): add header notifications for automation approvals (#5441)
  - `ad611501` fix(webui-v2): remove duplicate chat logs header (#5491)
  - `72e5bb7e` ci(reborn): add cargo-llvm-cov integration-tier coverage job (T0-COV) (#5430)
  - `fa898bf6` fix logs for expired runner leases (#5494)
  - `a19be26b` fix(reborn): surface real failure detail instead of generic "invalid_input" (#5338)
  - `3469ea54` fix(webui): link approval card to global auto-approve settings (#5247)
  - `414967d4` fix(resources): keep unlimited governor fast path in memory (#5497)
  - `29191164` Hide skill activation chat messages (#5489)
  - `02d16e26` Label turn state filesystem write traces (#5490)
  - `8237fb87` build(reborn): enable inmemory-turn-state in the ironclaw-reborn deploy build (#5492)
  - `4f7832b9` fix(reborn): in-memory turn-state authority for hosted runtime (runtime-wedge fix) (#5486)
  - `faa85d4c` fix(ci): unblock main-only checks (#5448)
  - `3cb4d535` fix(webui): chat composer clearing after send (#5404)
  - `91bfeb31` Add inner latency spans for agent loop executor (#5487)
  - `9e69f863` fix live QA Slack connect canary (#5485)
  - `940ca7ac` Add live latency trace instrumentation (#5472)
  - `4c19f6ea` fix(deps): replace unmaintained serde_yml with serde_norway (#5475)
  - `26d6dfc6` build(deps): bump rand to 0.8.6 in /channels-src/wechat and bump channel version (#5474)
  - `193f40dd` build(deps): bump ws to 8.21.0 and esbuild to 0.28.1 in /docs/architecture-video (#5473)
  - `aed128bc` test(reborn): add extension_activate int-tier scenario (T0-EXTACT) (#5433)
  - `a69ee36e` ci(reborn): dedicated low-contention job for Reborn group tests (T0-CI) (#5432)
<!-- END_RF_IRONCLAW -->
### Hermes Agent (`NousResearch/hermes-agent`)
<!-- START_BD_HERMES_AGENT -->
* **Status**: Highly Active (Total: 1240 commits [1237 H / 3 B], 1 tag/release in the last week). Lines added/deleted: +181.2k/-37.2k (Human), +519/-11 (Bot). **0 commits since installed 0.18.0.r1.g76a468e-1 (ref=76a468e).**
* **Contributors (according to last 7 days commits)** (Total: 272 Humans, 3 Bots):
  - **Top Humans**:
    - `Brooklyn Nicholson <brooklyn.bb.nicholson@gmail.com>` (Human): 216 commits, +63.2k/-19.9k lines
    - `teknium1 <127238744+teknium1@users.noreply.github.com>` (Human): 195 commits, +12.3k/-1.7k lines
    - `Teknium <127238744+teknium1@users.noreply.github.com>` (Human): 175 commits, +22.1k/-5.2k lines
    - `kshitijk4poor <82637225+kshitijk4poor@users.noreply.github.com>` (Human): 70 commits, +4.6k/-676 lines
    - `ethernet <arilotter@gmail.com>` (Human): 28 commits, +4.0k/-2.6k lines
    - `Ben <ben@nousresearch.com>` (Human): 27 commits, +8.1k/-493 lines
    - `xxxigm <tuancanhnguyen706@gmail.com>` (Human): 27 commits, +2.0k/-130 lines
    - `Ben Barclay <ben@nousresearch.com>` (Human): 23 commits, +4.9k/-453 lines
    - `liuhao1024 <sunsky.lau@gmail.com>` (Human): 19 commits, +2.4k/-117 lines
    - `HexLab98 <liruixinch@outlook.com>` (Human): 12 commits, +765/-43 lines
  - **Top Bots**:
    - `Tranquil-Flow <agent@tranquil-flow.dev>` (Bot): 1 commits, +357/-4 lines
    - `hinotoi-agent <paperlantern.agent@gmail.com>` (Bot): 1 commits, +78/-1 lines
    - `homelab-ha-agent <ha-agent@homelab.4410.us>` (Bot): 1 commits, +84/-6 lines
<!-- END_BD_HERMES_AGENT -->
<!-- START_RF_HERMES_AGENT -->
* **Recent Focus**:
  - No new commits in this period.
<!-- END_RF_HERMES_AGENT -->
### NanoBot (`HKUDS/nanobot`)
<!-- START_BD_NANOBOT -->
* **Status**: Highly Active (Total: 103 commits [103 H / 0 B], 0 tags/releases in the last week). Lines added/deleted: +8.9k/-3.8k (Human), +0/-0 (Bot).
* **Contributors (according to last 7 days commits)** (Total: 18 Humans, 0 Bots):
  - **Top Humans**:
    - `chengyongru <chengyongru.ai@gmail.com>` (Human): 33 commits, +3.1k/-2.1k lines
    - `axelray-dev <110029405+axelray-dev@users.noreply.github.com>` (Human): 25 commits, +848/-173 lines
    - `Xubin Ren <52506698+Re-bin@users.noreply.github.com>` (Human): 17 commits, +977/-140 lines
    - `chengyongru <2755839590@qq.com>` (Human): 8 commits, +2.4k/-1.3k lines
    - `wangjunwei <wangjunwei87@gmail.com>` (Human): 3 commits, +453/-15 lines
    - `michaelxer <michaelxer@users.noreply.github.com>` (Human): 3 commits, +124/-25 lines
    - `hamb1y <rishi.s.malnad@gmail.com>` (Human): 2 commits, +146/-3 lines
    - `Ilya Gusev <phoenixilya@gmail.com>` (Human): 2 commits, +95/-36 lines
    - `dajiaohuang <mikewushuwen@outlook.com>` (Human): 1 commits, +52/-4 lines
    - `xiaweiwei67-stack <xiaweiwei67@gmail.com>` (Human): 1 commits, +32/-4 lines
<!-- END_BD_NANOBOT -->
<!-- START_RF_NANOBOT -->
* **Recent Focus**:
  - `c78421cf` fix(bus): preserve legacy outbound metadata events
  - `03be51ad` fix(channels): preserve legacy stream hook signatures
  - `c757c546` docs: update channel plugin runtime event contract
  - `5f4cfbcb` refactor(bus): type outbound runtime events
  - `f6d1dba3` fix(cron): tolerate unsupported directory fsync
  - `2ec40442` feat(webui): add dollar skill shortcuts
  - `a6d5e4f3` docs(api): document wildcard bind authentication
  - `ed483253` fix: cover API auth guard regressions
  - `56443ac6` @ feat(api): require api_key when binding to all interfaces (parity with WS gateway)
  - `21aa900d` fix: honor MCP tool error results
  - `b0258e8b` fix: preserve legacy plugin tool errors
  - `84935609` refactor(tools): use structured tool error results
  - `8d2c31eb` refactor(webui): derive provider model catalog kind
  - `a6a489e0` refactor: tighten session recency cleanup
  - `840ba5af` fix: simplify session recency activity tracking
<!-- END_RF_NANOBOT -->
### PicoClaw (`sipeed/picoclaw`)
<!-- START_BD_PICOCLAW -->
* **Status**: Active (Total: 15 commits [11 H / 4 B], 1 tag/release in the last week). Lines added/deleted: +691/-87 (Human), +28/-28 (Bot). **28 commits since installed 0.3.0.nightly.20260622.287853ab-1 (ref=287853ab).**
* **Contributors (according to last 7 days commits)** (Total: 3 Humans, 1 Bots):
  - **Top Humans**:
    - `程智超0668000959 <cheng.zhichao@xydigit.com>` (Human): 9 commits, +68/-60 lines
    - `LC <lclc6464@outlook.com>` (Human): 1 commits, +482/-15 lines
    - `Alix-007 <li.long15@xydigit.com>` (Human): 1 commits, +141/-12 lines
  - **Top Bots**:
    - `dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>` (Bot): 4 commits, +28/-28 lines
<!-- END_BD_PICOCLAW -->
<!-- START_RF_PICOCLAW -->
* **Recent Focus**:
  - `2cf030d2` fix(providers): surface friendly auth error messages (#3198)
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
<!-- END_RF_PICOCLAW -->
### NanoClaw (`nanocoai/nanoclaw`)
<!-- START_BD_NANOCLAW -->
* **Status**: Active (Total: 13 commits [7 H / 6 B], 0 tags/releases in the last week). Lines added/deleted: +698/-132 (Human), +12/-12 (Bot).
* **Contributors (according to last 7 days commits)** (Total: 5 Humans, 1 Bots):
  - **Top Humans**:
    - `Omri Maya <omri@nanoco.ai>` (Human): 2 commits, +139/-0 lines
    - `John Mathews <mthwsjc@gmail.com>` (Human): 2 commits, +406/-89 lines
    - `gavrielc <gabicohen22@yahoo.com>` (Human): 1 commits, +15/-15 lines
    - `Rob Stevenson <this.rob@protonmail.com>` (Human): 1 commits, +137/-26 lines
    - `Christophe Benoist <christophe.benoist@gmail.com>` (Human): 1 commits, +1/-2 lines
  - **Top Bots**:
    - `github-actions[bot] <github-actions[bot]@users.noreply.github.com>` (Bot): 6 commits, +12/-12 lines
<!-- END_BD_NANOCLAW -->
<!-- START_RF_NANOCLAW -->
* **Recent Focus**:
  - `557e073` chore: bump version to 2.1.23
  - `91ebc9d` chore(container): bump claude-code, agent SDK to latest
  - `14c89e9` docs: update token count to 204k tokens · 102% of context window
  - `549c424` chore: bump version to 2.1.22
  - `cf8478f` fix(setup): offer Slack Socket Mode in the guided setup flow
  - `8be5be9` docs: update token count to 203k tokens · 101% of context window
  - `0d841bc` fix(ncl): default messaging-groups create instance to channel_type
  - `dd1d0e5` fix(security): contain channel-inbound attachments via shared inbox guard (#2828)
  - `36afa40` fix(agent-to-agent): containment-check target inbox in forwardAttachedFiles (#2828)
  - `797491d` fix(migrate-v2): don't SELECT is_main from v1 registered_groups
  - `2df7544` chore: bump version to 2.1.21
  - `bfb309b` chore: bump version to 2.1.20
  - `1d6bba4` feat(container): per-container CPU/memory limits (opt-in)
<!-- END_RF_NANOCLAW -->
### LibreFang (`librefang/librefang`)
<!-- START_BD_LIBREFANG -->
* **Status**: Active (Total: 43 commits [37 H / 6 B], 2 tags/releases in the last week). Lines added/deleted: +13.8k/-1.8k (Human), +64/-46 (Bot). **3 commits since installed 2026.6.29.r9.g83ee2627b-1 (ref=83ee2627b).**
* **Contributors (according to last 7 days commits)** (Total: 4 Humans, 2 Bots):
  - **Top Humans**:
    - `Evan <suzukaze.haduki@gmail.com>` (Human): 31 commits, +6.1k/-1.5k lines
    - `Павло <pavvers1@gmail.com>` (Human): 4 commits, +1.7k/-282 lines
    - `Seungjin Kim <seungjin@users.noreply.github.com>` (Human): 1 commits, +6.1k/-7 lines
    - `FrantaNautilus <142005599+FrantaNautilus@users.noreply.github.com>` (Human): 1 commits, +1/-0 lines
  - **Top Bots**:
    - `dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>` (Bot): 3 commits, +50/-32 lines
    - `github-actions[bot] <41898282+github-actions[bot]@users.noreply.github.com>` (Bot): 3 commits, +14/-14 lines
<!-- END_BD_LIBREFANG -->
* **Note**: LibreFang is a community fork of the former `RightNow-AI/openfang` repository, which had **17,623 stars** and **2,252 forks** before going stale.
<!-- START_RF_LIBREFANG -->
* **Recent Focus**:
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
