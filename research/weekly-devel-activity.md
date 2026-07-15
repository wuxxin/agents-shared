# Active AI Assistants: Weekly Development Activity

This document tracks repository activity, commit counts, merge frequency, and release cycles for active assistant projects.

---

#### 📊 Summary of Last 7 Days Activity (July 08, 2026 – July 15, 2026)

<!-- START_TABLES -->
#### Repository Overview & Package Status
| Assistant Repo | Stars | Forks | Main Branch | Last Commit | Installed Pkg | Commits Since Pkg | Status |
| :--- | :---: | :---: | :---: | :---: | :--- | :---: | :---: |
| **hermes-agent** | 215,412 | 40,168 | `main` | 2026-07-15 | `hermes-agent-git` @ `0.18.2.r783.g8b209e0dd-1` | 12 | **Highly Active** |
| **ironclaw** | 12,523 | 1,471 | `main` | 2026-07-15 | `ironclaw-reborn-git` @ `0.29.1.r1679.g85c02c2-1` | 180 | **Highly Active** |
| **zeroclaw** | 32,275 | 4,802 | `master` | 2026-07-15 | `zeroclaw-git` @ `0.8.2.r244.g3ec71f114-1` | 137 | **Active** |
| **librefang** | 338 | 65 | `main` | 2026-07-15 | `librefang-git` @ `2026.6.29.r24.g7be487fe3-1` | 46 | **Active** |
| **nanobot** | 45,661 | 8,050 | `main` | 2026-07-15 | — | — | **Highly Active** |
| **nanoclaw** | 30,260 | 12,879 | `main` | 2026-07-15 | `nanoclaw-git` @ `r1996.b6cb53e21-1` | 181 | **Highly Active** |
| **picoclaw** | 29,758 | 4,443 | `main` | 2026-07-09 | `picoclaw-git` @ `0.3.1.nightly.20260702.2cf030d2-1` | 28 | **Stale** |

#### Weekly Activity Metrics (Human vs Bot)
| Assistant Repo | Commits / Week | Lines Added (Human/Bot) | Lines Deleted (Human/Bot) | Merges (Last Wk) | Releases/Tags (Last Wk) | Avg Commits/Wk (4 Wks) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **hermes-agent** | **663** / 1 | 105.2k / 7 | 32.0k / 0 | 54 | 0 | 853.0 |
| **ironclaw** | **102** / 8 | 110.4k / 1.6k | 24.5k / 90 | 0 | 0 | 109.5 |
| **zeroclaw** | **49** / 0 | 33.5k / 0 | 3.3k / 0 | 0 | 0 | 139.5 |
| **librefang** | **26** / 8 | 50.2k / 883 | 1.6k / 647 | 0 | 2 | 47.8 |
| **nanobot** | **115** / 0 | 33.0k / 0 | 8.9k / 0 | 0 | 0 | 115.2 |
| **nanoclaw** | **66** / 20 | 10.7k / 41 | 3.3k / 41 | 32 | 0 | 67.8 |
| **picoclaw** | 0 / 0 | 0 / 0 | 0 / 0 | 1 | 0 | 13.8 |
<!-- END_TABLES -->

---

## 🔍 Repository Breakdown

> [!NOTE]
> The contributor lists and activity metrics for each repository below are compiled according to commits from the last 7 days.

### Hermes Agent (`NousResearch/hermes-agent`)
<!-- START_BD_HERMES_AGENT -->
* **Status**: Highly Active (Total: 664 commits [663 H / 1 B], 0 tags/releases in the last week). Lines added/deleted: +105.2k/-32.0k (Human), +7/-0 (Bot). **12 commits since installed 0.18.2.r783.g8b209e0dd-1 (ref=8b209e0dd).**
* **Contributors (according to last 7 days commits)** (Total: 123 Humans, 1 Bots):
  - **Top Humans**:
    - `kshitijk4poor <82637225+kshitijk4poor@users.noreply.github.com>` (Human): 117 commits, +11.0k/-2.4k lines
    - `Teknium <127238744+teknium1@users.noreply.github.com>` (Human): 97 commits, +9.4k/-1.8k lines
    - `Brooklyn Nicholson <brooklyn.bb.nicholson@gmail.com>` (Human): 93 commits, +22.9k/-4.9k lines
    - `ethernet <arilotter@gmail.com>` (Human): 72 commits, +20.8k/-16.4k lines
    - `teknium1 <127238744+teknium1@users.noreply.github.com>` (Human): 40 commits, +3.3k/-1.3k lines
    - `HexLab98 <liruixinch@outlook.com>` (Human): 18 commits, +1.5k/-121 lines
    - `liuhao1024 <sunsky.lau@gmail.com>` (Human): 12 commits, +1.2k/-148 lines
    - `Kshitij Kapoor <kshitijk4poor@users.noreply.github.com>` (Human): 11 commits, +1.0k/-175 lines
    - `Burgunthy <Burgunthy@users.noreply.github.com>` (Human): 8 commits, +1.4k/-116 lines
    - `Harry Yep <git@hode.co.uk>` (Human): 8 commits, +359/-1.2k lines
  - **Top Bots**:
    - `agent <agent@agents-Mac-mini.local>` (Bot): 1 commits, +7/-0 lines
<!-- END_BD_HERMES_AGENT -->
<!-- START_RF_HERMES_AGENT -->
* **Recent Focus**:
  - `00a36831d` fix: update package-lock.json
  - `56ab9951b` fix(dashboard): add MCP auth to profile builder (#65163)
  - `3bfa6001f` fix(js ci): don't ignore native deps anymore
  - `93808ca6a` fix(desktop): resolve eslint errors in composer-input-sanitize.ts
  - `3102fc9a6` fix(shared): add missing 'fix' script alias
  - `02613a4d5` fix(web): resolve all eslint errors, downgrade react-hooks v7 to warnings
  - `894e62759` feat(fmt): add "npm run fix" in root
  - `f32a1f607` ci: add desktop autofix-on-merge with two-job security split
  - `ef7aabd3d` ci: add ci-reviewed label gate for CI-sensitive files
  - `2179d5e8a` ci: add eslint lint matrix to js-tests.yml
  - `214cbf77f` refactor(lint): hoist shared eslint + prettier config to root
  - `b80b52aa4` feat(desktop): add background-task indicator to sidebar session rows (#65174)
<!-- END_RF_HERMES_AGENT -->


### IronClaw (`nearai/ironclaw`)
<!-- START_BD_IRONCLAW -->
* **Status**: Highly Active (Total: 110 commits [102 H / 8 B], 0 tags/releases in the last week). Lines added/deleted: +110.4k/-24.5k (Human), +1.6k/-90 (Bot). **180 commits since installed 0.29.1.r1679.g85c02c2-1 (ref=85c02c2).**
* **Contributors (according to last 7 days commits)** (Total: 13 Humans, 1 Bots):
  - **Top Humans**:
    - `firat.sertgoz <firat.sertgoz@near.ai>` (Human): 33 commits, +20.3k/-4.8k lines
    - `jinxin <106428113+italic-jinxin@users.noreply.github.com>` (Human): 25 commits, +8.1k/-4.8k lines
    - `Illia Polosukhin <ilblackdragon@gmail.com>` (Human): 12 commits, +9.5k/-3.8k lines
    - `Henry Park <henrypark133@gmail.com>` (Human): 10 commits, +13.1k/-2.8k lines
    - `Benjamin Kurrek <57506486+BenKurrek@users.noreply.github.com>` (Human): 10 commits, +45.1k/-7.1k lines
    - `Pranav Raja <pranavraja99@gmail.com>` (Human): 4 commits, +386/-37 lines
    - `Coffee <95295094+hanakannzashi@users.noreply.github.com>` (Human): 2 commits, +30/-8 lines
    - `Den <41162202+denbite@users.noreply.github.com>` (Human): 1 commits, +1.8k/-56 lines
    - `Bohdan Khorolets <bogdan@khorolets.com>` (Human): 1 commits, +123/-2 lines
    - `aiworkbot <robert.yan@near.ai>` (Human): 1 commits, +139/-15 lines
  - **Top Bots**:
    - `ironloopai[bot] <295884755+ironloopai[bot]@users.noreply.github.com>` (Bot): 8 commits, +1.6k/-90 lines
<!-- END_BD_IRONCLAW -->
<!-- START_RF_IRONCLAW -->
* **Recent Focus**:
  - `7ae6c411` fix(webui-v2): render extension registry without enrichment delay (#6082)
  - `19f561c5` feat(webui): replace native confirmations with a shared modal (#6084)
  - `4ba64bc3` fix(webui-v2): submit follow-up messages reliably with Enter (#6081)
  - `c2c29e45` fix(webui): surface extension catalog load failures (#6088)
  - `57430cf8` fix: keep http save output compact (#5915)
  - `e01d3fe7` fix(reborn): remove unsupported admin token action (#6086)
  - `1a56f287` fix(triggers): derive active-hold visibility for gate-parked automations (#6066)
  - `ae553971` Advertise Reborn skills as a one-line listing; load bodies on activation (#5977)
  - `ad33cda8` test(reborn): Slack channel lifecycle state-machine integration scenario (#6105) (#6110)
  - `f5c649ba` Fix WebUI memory browse isolation (#5896)
  - `b0b268da` fix(reborn): recover resource governor from libSQL contention (#6089)
  - `15f06e1b` feat(agent-loop): tools-capable completion nudge for interactive coding (#6013)
  - `d6807333` fix(webui-v2): show chat connection status (#6040)
  - `c41d3f6b` fix(webui): use theme-aware semantic colors (#6041)
  - `07f1d65a` fix: distinguish inactive extension search results (#5952)
<!-- END_RF_IRONCLAW -->

### ZeroClaw (`zeroclaw-labs/zeroclaw`)
<!-- START_BD_ZEROCLAW -->
* **Status**: Active (Total: 49 commits [49 H / 0 B], 0 tags/releases in the last week). Lines added/deleted: +33.5k/-3.3k (Human), +0/-0 (Bot). **137 commits since installed 0.8.2.r244.g3ec71f114-1 (ref=3ec71f114).**
* **Contributors (according to last 7 days commits)** (Total: 18 Humans, 0 Bots):
  - **Top Humans**:
    - `Dan Gilles <dfgilles@uchicago.edu>` (Human): 10 commits, +3.4k/-416 lines
    - `Tidux <jon@borg.moe>` (Human): 7 commits, +3.1k/-342 lines
    - `JordanTheJet <morepencils@gmail.com>` (Human): 5 commits, +1.8k/-201 lines
    - `Shane Engelman <contact@shane.gg>` (Human): 5 commits, +22.3k/-2.0k lines
    - `wangmiao0668000666 <wang.miao86@xydigit.com>` (Human): 4 commits, +840/-4 lines
    - `Marc Collins <marc@nnet.tech>` (Human): 3 commits, +519/-172 lines
    - `Leon-SK668 <llagy007@163.com>` (Human): 3 commits, +31/-17 lines
    - `Alex Yanchenko <alex@yanchenko.com>` (Human): 2 commits, +241/-7 lines
    - `tzy-17 <tang.ziyi@xydigit.com>` (Human): 1 commits, +3/-15 lines
    - `databillm <164733617+databillm@users.noreply.github.com>` (Human): 1 commits, +244/-12 lines
<!-- END_BD_ZEROCLAW -->
<!-- START_RF_ZEROCLAW -->
* **Recent Focus**:
  - `08baac5c` chore(release): cut v0.8.3 — changelog, version bump, locale sync (#9081)
  - `1f8ab7bc` chore(release): add CHANGELOG-next.md for v0.8.3 (#9054)
  - `abf5b484` fix(ci): escape release verification Markdown (#9031)
  - `d8f0720e` fix(release): restore lean prebuilt feature set (#9051)
  - `de325eb3` docs(rustdoc): stop linking private helpers (#9004)
  - `0277f67a` fix(security): scan link/image destinations for deterministic credential patterns (#8906)
  - `6d0ebb95` test(eval): ensure invalid regex checks continue (#8972)
  - `5ef75481` test(commands): cover slash token normalization (#8971)
  - `82fe8510` refactor(log): remove unused tool IO empty marker (#8970)
  - `0eb33284` docs(maintainers): fix dashboard workflow link (#9003)
  - `42fa1971` fix(channels): localize channel runtime replies (#8769)
  - `379e4603` feat(zerocode): choose saved Code session on entry (#8922)
  - `7b92e2a9` feat(quickstart): run CLI subscription auth inline (#8981)
  - `6c2be72b` feat(channels): operator-bind identities without the /bind code round-trip (#8707)
  - `72ab1335` feat(quickstart): add subscription auth modes (#8980)
<!-- END_RF_ZEROCLAW -->

### LibreFang (`librefang/librefang`)
<!-- START_BD_LIBREFANG -->
* **Status**: Active (Total: 34 commits [26 H / 8 B], 2 tags/releases in the last week). Lines added/deleted: +50.2k/-1.6k (Human), +883/-647 (Bot). **46 commits since installed 2026.6.29.r24.g7be487fe3-1 (ref=7be487fe3).**
* **Contributors (according to last 7 days commits)** (Total: 1 Humans, 1 Bots):
  - **Top Humans**:
    - `Evan <suzukaze.haduki@gmail.com>` (Human): 26 commits, +50.2k/-1.6k lines
  - **Top Bots**:
    - `dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>` (Bot): 8 commits, +883/-647 lines
<!-- END_BD_LIBREFANG -->
* **Note**: LibreFang is a community fork of the former `RightNow-AI/openfang` repository, which had **17,623 stars** and **2,252 forks** before going stale.
<!-- START_RF_LIBREFANG -->
* **Recent Focus**:
  - `627fa3cf` fix(runtime): trust operator env allowlist in sandbox_command (#6458) (#6465)
  - `4b318c97` fix(ci): treat retired pnpm audit endpoint as skip, not a dependency issue (#6466)
  - `00d1bd61` fix(security/channels): enforce cross-account channel_send guard through the /mcp bridge (#6443) (#6455)
  - `9d3beeb1` chore(deps): bump the actions-minor-patch group with 3 updates (#6456)
  - `70208cdf` chore(deps): bump actions/setup-node from 6.4.0 to 7.0.0 (#6457)
  - `d7787bef` chore(deps): bump the cargo-minor-patch group with 10 updates (#6452)
  - `ba43dcc9` chore(deps): bump tokio-tungstenite from 0.29.0 to 0.30.0 (#6453)
  - `ca899354` chore(deps): update yanked spin 0.9.8 to 0.9.9 (#6454)
  - `492dbf31` fix: resolve four reported bugs (#6423, #6442, #6443, #6444) (#6449)
  - `d980c02c` fix: fourth-pass security and correctness hardening from repo-wide audit (#6446)
  - `d243bcde` fix: third-pass security and correctness hardening from repo-wide audit (#6441)
  - `481cd9d7` docs: update contributors and star history (#6440)
  - `76fe32db` fix: second-pass security and correctness hardening from repo-wide audit (#6439)
  - `46ffd3be` fix: security and correctness hardening from repo-wide audit (#6438)
  - `77d896b4` docs: update contributors and star history (#6436)
<!-- END_RF_LIBREFANG -->

### NanoBot (`HKUDS/nanobot`)
<!-- START_BD_NANOBOT -->
* **Status**: Highly Active (Total: 115 commits [115 H / 0 B], 0 tags/releases in the last week). Lines added/deleted: +33.0k/-8.9k (Human), +0/-0 (Bot).
* **Contributors (according to last 7 days commits)** (Total: 21 Humans, 0 Bots):
  - **Top Humans**:
    - `chengyongru <2755839590@qq.com>` (Human): 37 commits, +4.9k/-2.1k lines
    - `chengyongru <chengyongru.ai@gmail.com>` (Human): 31 commits, +6.1k/-3.6k lines
    - `chengyongru <61816729+chengyongru@users.noreply.github.com>` (Human): 13 commits, +3.6k/-1.5k lines
    - `Xubin Ren <52506698+Re-bin@users.noreply.github.com>` (Human): 9 commits, +15.8k/-1.5k lines
    - `Eric Yang <eyang@apache.org>` (Human): 5 commits, +344/-41 lines
    - `Arthur K. <me@wzray.com>` (Human): 2 commits, +279/-18 lines
    - `sanasif786ka <asif786ka@gmail.com>` (Human): 2 commits, +11/-8 lines
    - `Aleksander W. Oleszkiewicz (Alek) <aleksander.oleszkiewicz@auticon.com>` (Human): 2 commits, +54/-7 lines
    - `NOKIAO <62821977+luojiaaoo@users.noreply.github.com>` (Human): 2 commits, +4/-1 lines
    - `Olu B <obankole@rccl.com>` (Human): 1 commits, +2/-2 lines
<!-- END_BD_NANOBOT -->
<!-- START_RF_NANOBOT -->
* **Recent Focus**:
  - `d4e02947` fix(gateway): stop channels before draining tasks
  - `681edfa6` fix(providers): honor Codex proxy config consistently
  - `ba86dccc` fix(webui): correct activity timer duration (#4649)
  - `5ed28a67` fix(webui): validate inferred file paths before preview (#4935)
  - `aa70aa48` fix(cli): point onboarding to the WebUI launcher (#4938)
  - `0fd4d0ab` fix(prompts): handle undecodable overrides
  - `c1fd76ad` refactor(prompts): share workspace override handling
  - `63a6d5d0` fix(heartbeat): retain history after empty runs
  - `dcb37259` feat(heartbeat): custom evaluator prompt
  - `88c38e9b` fix(restart): deliver completion after channel reconnects (#4931)
  - `37165b0d` feat(webui): highlight slash commands and app mentions (#4933)
  - `2116e320` test: speed up CI and harden the suite
  - `06f47fa5` fix: standardize --config help text across CLI commands
  - `905da8e3` ci(webui): verify npm and bun lockfiles
  - `5365bab0` fix(webui): sync package-lock.json for qrcode dependency
<!-- END_RF_NANOBOT -->

### NanoClaw (`nanocoai/nanoclaw`)
<!-- START_BD_NANOCLAW -->
* **Status**: Highly Active (Total: 86 commits [66 H / 20 B], 0 tags/releases in the last week). Lines added/deleted: +10.7k/-3.3k (Human), +41/-41 (Bot). **181 commits since installed r1996.b6cb53e21-1 (ref=b6cb53e21).**
* **Contributors (according to last 7 days commits)** (Total: 9 Humans, 1 Bots):
  - **Top Humans**:
    - `gavrielc <gabicohen22@yahoo.com>` (Human): 37 commits, +4.2k/-1.2k lines
    - `Amit Shafnir <amit@nanoco.ai>` (Human): 14 commits, +2.5k/-1.1k lines
    - `glifocat <ethan@nanoco.ai>` (Human): 5 commits, +824/-59 lines
    - `Omri Maya <omri@nanoco.ai>` (Human): 4 commits, +1.2k/-624 lines
    - `Koshkoshinsk <daniel.milliner@gmail.com>` (Human): 2 commits, +125/-20 lines
    - `Moshe Krupper <moshe@nanoco.ai>` (Human): 1 commits, +1.7k/-333 lines
    - `Gabi Simons <gabi@nanoco.ai>` (Human): 1 commits, +85/-1 lines
    - `exe.dev user <exedev@shuf-nanoclaw.exe.xyz>` (Human): 1 commits, +35/-0 lines
    - `omri-maya <omri@nanoco.ai>` (Human): 1 commits, +4/-1 lines
  - **Top Bots**:
    - `github-actions[bot] <github-actions[bot]@users.noreply.github.com>` (Bot): 20 commits, +41/-41 lines
<!-- END_BD_NANOCLAW -->
<!-- START_RF_NANOCLAW -->
* **Recent Focus**:
  - `3fd0793` Apply suggestions from code review
  - `134d9ae` docs(changelog): summarize shared memory change
  - `c54fb3c` docs(changelog): preserve upstream entries
  - `787873b` docs(codex): preserve shared memory guidance
  - `949ffd1` fix(memory): register Claude session hook in settings
  - `c542c46` refactor(memory): use agent-defined folder tree
  - `9169571` refactor(memory): centralize session hook integration
  - `796e312` Apply suggestions from code review
  - `25b820c` feat(memory): adopt OKF-compatible memory bundles
  - `fe70584` docs(memory): guide entity-specific storage
  - `1c56f52` docs(memory): keep migration content-blind
  - `e8de194` fix(memory): harden upgrade and migration paths
  - `76d941b` feat(memory): add provider-agnostic persistent memory
  - `1ed14cc` fix(skills): switch Telegram deep-link from t.me to telegram.me
  - `e247644` feat: support scripts in template tasks
<!-- END_RF_NANOCLAW -->

### PicoClaw (`sipeed/picoclaw`)
<!-- START_BD_PICOCLAW -->
* **Status**: Stale (Total: 0 commits [0 H / 0 B], 0 tags/releases in the last week). Lines added/deleted: +0/-0 (Human), +0/-0 (Bot). **28 commits since installed 0.3.1.nightly.20260702.2cf030d2-1 (ref=2cf030d2).**
* **Contributors (according to last 7 days commits)** (Total: 0 Humans, 0 Bots):
<!-- END_BD_PICOCLAW -->
<!-- START_RF_PICOCLAW -->
* **Recent Focus**:
  - No new commits in this period.
<!-- END_RF_PICOCLAW -->


---
## 📋 Instruction Guide: Recreating this Analysis

**Fully Automated Update**: You can run the automation script `scripts/update-activity.py` with the `--write` (or `-w`) flag to automatically pull all repository updates, calculate the statistics, and optionally write the updated tables directly back into this file:
```bash
python scripts/update-activity.py [--write]
```
