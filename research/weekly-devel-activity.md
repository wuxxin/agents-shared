# Active AI Assistants: Weekly Development Activity

This document tracks repository activity, commit counts, merge frequency, and release cycles for active assistant projects.

---

#### 📊 Summary of Last 7 Days Activity (June 28, 2026 – July 05, 2026)

<!-- START_TABLES -->
#### Repository Overview & Package Status
| Assistant Repo | Stars | Forks | Main Branch | Last Commit | Installed Pkg | Commits Since Pkg | Status |
| :--- | :---: | :---: | :---: | :---: | :--- | :---: | :---: |
| **hermes-agent** | 209,459 | 38,252 | `main` | 2026-07-05 | `hermes-agent-git` @ `0.18.0.r332.g7fde19afc-1` | 13 | **Highly Active** |
| **ironclaw** | 12,497 | 1,464 | `main` | 2026-07-04 | `ironclaw-reborn-git` @ `0.29.1.r1679.g85c02c2-1` | 0 | **Highly Active** |
| **zeroclaw** | 32,157 | 4,792 | `master` | 2026-07-05 | `zeroclaw-git` @ `0.8.2.r244.g3ec71f114-1` | 1 | **Highly Active** |
| **librefang** | 318 | 64 | `main` | 2026-07-05 | `librefang-git` @ `2026.6.29.r24.g7be487fe3-1` | 0 | **Active** |
| **nanobot** | 45,031 | 7,943 | `main` | 2026-07-04 | — | — | **Highly Active** |
| **nanoclaw** | 30,130 | 12,905 | `main` | 2026-07-04 | `nanoclaw-git` @ `r1996.b6cb53e21-1` | 0 | **Highly Active** |
| **picoclaw** | 29,592 | 4,267 | `main` | 2026-07-05 | `picoclaw-git` @ `0.3.1.nightly.20260702.2cf030d2-1` | 24 | **Active** |

#### Weekly Activity Metrics (Human vs Bot)
| Assistant Repo | Commits / Week | Lines Added (Human/Bot) | Lines Deleted (Human/Bot) | Merges (Last Wk) | Releases/Tags (Last Wk) | Avg Commits/Wk (4 Wks) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **hermes-agent** | **1022** / 2 | 139.0k / 435 | 37.1k / 5 | 95 | 1 | 818.5 |
| **ironclaw** | **126** / 3 | 152.5k / 3.6k | 131.3k / 291 | 0 | 1 | 117.0 |
| **zeroclaw** | **169** / 0 | 54.0k / 0 | 13.2k / 0 | 0 | 0 | 183.8 |
| **librefang** | **28** / 7 | 14.3k / 976 | 2.1k / 958 | 0 | 1 | 60.2 |
| **nanobot** | **79** / 0 | 13.4k / 0 | 2.8k / 0 | 0 | 0 | 120.5 |
| **nanoclaw** | **37** / 25 | 2.6k / 49 | 1.5k / 49 | 47 | 0 | 42.2 |
| **picoclaw** | **5** / 6 | 4.2k / 715 | 71 / 790 | 14 | 1 | 31.5 |
<!-- END_TABLES -->

---

## 🔍 Repository Breakdown

> [!NOTE]
> The contributor lists and activity metrics for each repository below are compiled according to commits from the last 7 days.

### Hermes Agent (`NousResearch/hermes-agent`)
<!-- START_BD_HERMES_AGENT -->
* **Status**: Highly Active (Total: 1024 commits [1022 H / 2 B], 1 tag/release in the last week). Lines added/deleted: +139.0k/-37.1k (Human), +435/-5 (Bot). **13 commits since installed 0.18.0.r332.g7fde19afc-1 (ref=7fde19afc).**
* **Contributors (according to last 7 days commits)** (Total: 258 Humans, 2 Bots):
  - **Top Humans**:
    - `Brooklyn Nicholson <brooklyn.bb.nicholson@gmail.com>` (Human): 170 commits, +37.3k/-15.1k lines
    - `teknium1 <127238744+teknium1@users.noreply.github.com>` (Human): 138 commits, +7.3k/-9.4k lines
    - `Teknium <127238744+teknium1@users.noreply.github.com>` (Human): 111 commits, +16.4k/-2.4k lines
    - `kshitijk4poor <82637225+kshitijk4poor@users.noreply.github.com>` (Human): 93 commits, +6.0k/-771 lines
    - `xxxigm <tuancanhnguyen706@gmail.com>` (Human): 19 commits, +995/-60 lines
    - `liuhao1024 <sunsky.lau@gmail.com>` (Human): 16 commits, +1.1k/-51 lines
    - `srojk34 <286497132+srojk34@users.noreply.github.com>` (Human): 16 commits, +1.7k/-38 lines
    - `Ben <ben@nousresearch.com>` (Human): 16 commits, +4.0k/-350 lines
    - `Ben Barclay <ben@nousresearch.com>` (Human): 15 commits, +3.6k/-347 lines
    - `HexLab98 <liruixinch@outlook.com>` (Human): 12 commits, +911/-38 lines
  - **Top Bots**:
    - `Tranquil-Flow <agent@tranquil-flow.dev>` (Bot): 1 commits, +357/-4 lines
    - `hinotoi-agent <paperlantern.agent@gmail.com>` (Bot): 1 commits, +78/-1 lines
<!-- END_BD_HERMES_AGENT -->
<!-- START_RF_HERMES_AGENT -->
* **Recent Focus**:
  - `0ca2a927c` chore: add devatnull to AUTHOR_MAP for PR #58697 salvage
  - `558001307` feat(desktop,docs): surface stt.echo_transcripts in desktop settings and docs
  - `4be749d15` fix: honor top-level STT transcript echo config
  - `406eb719c` fix: gate interrupt STT transcript echoes
  - `bfc526272` feat: add STT transcript echo toggle
  - `95fc3c6b4` chore: add alastraz to AUTHOR_MAP for PR #41383 salvage
  - `519ec7b3b` fix(computer_use): parse (label) and = "value" AX element label forms
  - `13b75e73f` fix(computer_use): re-fetch via CLI when MCP returns silent-empty captures
  - `7af9abd17` fix(computer_use): fall back to CLI transport when cua-driver MCP bridge hits EAGAIN
  - `de4310c8f` fix(computer-use): report the wedged startup phase in the session ready-timeout error (#58801)
  - `24a754691` fix(cli): drop shell=True from cua-driver installer — download to mkstemp, exec as argv (#58796)
  - `2c0820c9f` feat(cli): autocomplete + ghost text for stacked slash-skill invocations (#58763)
  - `1c156736d` docs: warn that mid-session model switches break prompt caching (#58747)
<!-- END_RF_HERMES_AGENT -->


### IronClaw (`nearai/ironclaw`)
<!-- START_BD_IRONCLAW -->
* **Status**: Highly Active (Total: 129 commits [126 H / 3 B], 1 tag/release in the last week). Lines added/deleted: +152.5k/-131.3k (Human), +3.6k/-291 (Bot). **0 commits since installed 0.29.1.r1679.g85c02c2-1 (ref=85c02c2).**
* **Contributors (according to last 7 days commits)** (Total: 10 Humans, 2 Bots):
  - **Top Humans**:
    - `firat.sertgoz <firat.sertgoz@near.ai>` (Human): 52 commits, +56.3k/-4.0k lines
    - `Henry Park <henrypark133@gmail.com>` (Human): 32 commits, +44.5k/-14.7k lines
    - `Illia Polosukhin <ilblackdragon@gmail.com>` (Human): 15 commits, +30.7k/-101.7k lines
    - `jinxin <106428113+italic-jinxin@users.noreply.github.com>` (Human): 13 commits, +7.6k/-8.4k lines
    - `Robert Yan <46699230+think-in-universe@users.noreply.github.com>` (Human): 5 commits, +1.5k/-1.0k lines
    - `Benjamin Kurrek <57506486+BenKurrek@users.noreply.github.com>` (Human): 5 commits, +11.2k/-1.4k lines
    - `abbyshekit <153240993+abbyshekit@users.noreply.github.com>` (Human): 1 commits, +43/-3 lines
    - `Pranav Raja <pranavraja99@gmail.com>` (Human): 1 commits, +15/-4 lines
    - `Coffee <zjchen1234@foxmail.com>` (Human): 1 commits, +603/-17 lines
    - `Josh Ford <thisisjoshford@gmail.com>` (Human): 1 commits, +145/-3 lines
  - **Top Bots**:
    - `dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>` (Bot): 2 commits, +543/-291 lines
    - `ironclaw-ci[bot] <266877842+ironclaw-ci[bot]@users.noreply.github.com>` (Bot): 1 commits, +3.1k/-0 lines
<!-- END_BD_IRONCLAW -->
<!-- START_RF_IRONCLAW -->
* **Recent Focus**:
  - No new commits in this period.
<!-- END_RF_IRONCLAW -->

### ZeroClaw (`zeroclaw-labs/zeroclaw`)
<!-- START_BD_ZEROCLAW -->
* **Status**: Highly Active (Total: 169 commits [169 H / 0 B], 0 tags/releases in the last week). Lines added/deleted: +54.0k/-13.2k (Human), +0/-0 (Bot). **1 commits since installed 0.8.2.r244.g3ec71f114-1 (ref=3ec71f114).**
* **Contributors (according to last 7 days commits)** (Total: 28 Humans, 0 Bots):
  - **Top Humans**:
    - `Dan Gilles <dfgilles@uchicago.edu>` (Human): 38 commits, +3.9k/-643 lines
    - `Marc Collins <marc@nnet.tech>` (Human): 18 commits, +10.5k/-2.4k lines
    - `Alix-007 <li.long15@xydigit.com>` (Human): 17 commits, +1.1k/-0 lines
    - `wangmiao0668000666 <wang.miao86@xydigit.com>` (Human): 15 commits, +3.3k/-480 lines
    - `Shane Engelman <contact@shane.gg>` (Human): 13 commits, +9.0k/-8.0k lines
    - `JordanTheJet <morepencils@gmail.com>` (Human): 7 commits, +5.6k/-176 lines
    - `Tidux <jon@borg.moe>` (Human): 7 commits, +6.1k/-232 lines
    - `ConYel <18070323+ConYel@users.noreply.github.com>` (Human): 7 commits, +1.1k/-103 lines
    - `mazhuima <xie.chaolong@xydigit.com>` (Human): 7 commits, +968/-75 lines
    - `LiLan0125 <li.lan3@xydigit.com>` (Human): 6 commits, +818/-69 lines
<!-- END_BD_ZEROCLAW -->
<!-- START_RF_ZEROCLAW -->
* **Recent Focus**:
  - `caed62f9` docs(plugins): add plugin authoring guide series, correct stale plugin claims in docs and source comments (#8621)
<!-- END_RF_ZEROCLAW -->

### LibreFang (`librefang/librefang`)
<!-- START_BD_LIBREFANG -->
* **Status**: Active (Total: 35 commits [28 H / 7 B], 1 tag/release in the last week). Lines added/deleted: +14.3k/-2.1k (Human), +976/-958 (Bot). **0 commits since installed 2026.6.29.r24.g7be487fe3-1 (ref=7be487fe3).**
* **Contributors (according to last 7 days commits)** (Total: 4 Humans, 1 Bots):
  - **Top Humans**:
    - `Evan <suzukaze.haduki@gmail.com>` (Human): 23 commits, +7.5k/-2.1k lines
    - `Павло <pavvers1@gmail.com>` (Human): 3 commits, +687/-36 lines
    - `Seungjin Kim <seungjin@users.noreply.github.com>` (Human): 1 commits, +6.1k/-7 lines
    - `FrantaNautilus <142005599+FrantaNautilus@users.noreply.github.com>` (Human): 1 commits, +1/-0 lines
  - **Top Bots**:
    - `dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>` (Bot): 7 commits, +976/-958 lines
<!-- END_BD_LIBREFANG -->
* **Note**: LibreFang is a community fork of the former `RightNow-AI/openfang` repository, which had **17,623 stars** and **2,252 forks** before going stale.
<!-- START_RF_LIBREFANG -->
* **Recent Focus**:
  - No new commits in this period.
<!-- END_RF_LIBREFANG -->

### NanoBot (`HKUDS/nanobot`)
<!-- START_BD_NANOBOT -->
* **Status**: Highly Active (Total: 79 commits [79 H / 0 B], 0 tags/releases in the last week). Lines added/deleted: +13.4k/-2.8k (Human), +0/-0 (Bot).
* **Contributors (according to last 7 days commits)** (Total: 18 Humans, 0 Bots):
  - **Top Humans**:
    - `chengyongru <chengyongru.ai@gmail.com>` (Human): 34 commits, +3.8k/-898 lines
    - `Xubin Ren <52506698+Re-bin@users.noreply.github.com>` (Human): 13 commits, +1.5k/-237 lines
    - `chengyongru <2755839590@qq.com>` (Human): 10 commits, +4.1k/-1.3k lines
    - `axelray-dev <110029405+axelray-dev@users.noreply.github.com>` (Human): 4 commits, +245/-64 lines
    - `Yuxin Lou <louyuxin_730@163.com>` (Human): 2 commits, +58/-8 lines
    - `yu-xin-c <2182712990@qq.com>` (Human): 2 commits, +61/-0 lines
    - `hamb1y <rishi.s.malnad@gmail.com>` (Human): 2 commits, +146/-3 lines
    - `wangjunwei <wangjunwei87@gmail.com>` (Human): 2 commits, +45/-10 lines
    - `xcao <xcao@bonditech.com.cn>` (Human): 1 commits, +56/-3 lines
    - `yorkhellen <zhangxiaoyu.york@bytedance.com>` (Human): 1 commits, +56/-2 lines
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

### NanoClaw (`nanocoai/nanoclaw`)
<!-- START_BD_NANOCLAW -->
* **Status**: Highly Active (Total: 62 commits [37 H / 25 B], 0 tags/releases in the last week). Lines added/deleted: +2.6k/-1.5k (Human), +49/-49 (Bot). **0 commits since installed r1996.b6cb53e21-1 (ref=b6cb53e21).**
* **Contributors (according to last 7 days commits)** (Total: 7 Humans, 1 Bots):
  - **Top Humans**:
    - `gavrielc <gabicohen22@yahoo.com>` (Human): 30 commits, +973/-1.4k lines
    - `John Mathews <mthwsjc@gmail.com>` (Human): 2 commits, +406/-89 lines
    - `glifocat <ethan@nanoco.ai>` (Human): 1 commits, +13/-3 lines
    - `leetwito <leetwito@gmail.com>` (Human): 1 commits, +8/-3 lines
    - `Amit Shafnir <amit@nanoco.ai>` (Human): 1 commits, +939/-8 lines
    - `Rob Stevenson <this.rob@protonmail.com>` (Human): 1 commits, +137/-26 lines
    - `Omri Maya <omri@nanoco.ai>` (Human): 1 commits, +87/-0 lines
  - **Top Bots**:
    - `github-actions[bot] <github-actions[bot]@users.noreply.github.com>` (Bot): 25 commits, +49/-49 lines
<!-- END_BD_NANOCLAW -->
<!-- START_RF_NANOCLAW -->
* **Recent Focus**:
  - No new commits in this period.
<!-- END_RF_NANOCLAW -->

### PicoClaw (`sipeed/picoclaw`)
<!-- START_BD_PICOCLAW -->
* **Status**: Active (Total: 11 commits [5 H / 6 B], 1 tag/release in the last week). Lines added/deleted: +4.2k/-71 (Human), +715/-790 (Bot). **24 commits since installed 0.3.1.nightly.20260702.2cf030d2-1 (ref=2cf030d2).**
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


---
## 📋 Instruction Guide: Recreating this Analysis

**Fully Automated Update**: You can run the automation script `scripts/update-activity.py` with the `--write` (or `-w`) flag to automatically pull all repository updates, calculate the statistics, and optionally write the updated tables directly back into this file:
```bash
python scripts/update-activity.py [--write]
```
