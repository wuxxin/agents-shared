# Active AI Assistants: Weekly Development Activity

This document tracks repository activity, commit counts, merge frequency, and release cycles for active assistant projects.

---

#### 📊 Summary of Last 7 Days Activity (June 29, 2026 – July 06, 2026)

<!-- START_TABLES -->
#### Repository Overview & Package Status
| Assistant Repo | Stars | Forks | Main Branch | Last Commit | Installed Pkg | Commits Since Pkg | Status |
| :--- | :---: | :---: | :---: | :---: | :--- | :---: | :---: |
| **hermes-agent** | 210,020 | 38,429 | `main` | 2026-07-06 | `hermes-agent-git` @ `0.18.0.r418.g6fad6f1dd-1` | 85 | **Highly Active** |
| **ironclaw** | 12,500 | 1,465 | `main` | 2026-07-06 | `ironclaw-reborn-git` @ `0.29.1.r1679.g85c02c2-1` | 7 | **Highly Active** |
| **zeroclaw** | 32,164 | 4,793 | `master` | 2026-07-06 | `zeroclaw-git` @ `0.8.2.r244.g3ec71f114-1` | 18 | **Highly Active** |
| **librefang** | 318 | 64 | `main` | 2026-07-05 | `librefang-git` @ `2026.6.29.r24.g7be487fe3-1` | 0 | **Active** |
| **nanobot** | 45,059 | 7,949 | `main` | 2026-07-06 | — | — | **Highly Active** |
| **nanoclaw** | 30,132 | 12,900 | `main` | 2026-07-04 | `nanoclaw-git` @ `r1996.b6cb53e21-1` | 0 | **Highly Active** |
| **picoclaw** | 29,599 | 4,263 | `main` | 2026-07-05 | `picoclaw-git` @ `0.3.1.nightly.20260702.2cf030d2-1` | 24 | **Active** |

#### Weekly Activity Metrics (Human vs Bot)
| Assistant Repo | Commits / Week | Lines Added (Human/Bot) | Lines Deleted (Human/Bot) | Merges (Last Wk) | Releases/Tags (Last Wk) | Avg Commits/Wk (4 Wks) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **hermes-agent** | **1046** / 2 | 142.0k / 435 | 37.9k / 5 | 84 | 1 | 826.8 |
| **ironclaw** | **127** / 3 | 143.2k / 3.6k | 131.4k / 291 | 0 | 1 | 114.8 |
| **zeroclaw** | **143** / 0 | 40.5k / 0 | 11.6k / 0 | 0 | 0 | 185.0 |
| **librefang** | **17** / 7 | 4.0k / 976 | 1.6k / 958 | 0 | 0 | 59.5 |
| **nanobot** | **110** / 0 | 16.5k / 0 | 2.9k / 0 | 0 | 0 | 127.8 |
| **nanoclaw** | **34** / 24 | 2.1k / 45 | 1.4k / 45 | 46 | 0 | 40.8 |
| **picoclaw** | **5** / 6 | 4.2k / 715 | 71 / 790 | 14 | 1 | 29.0 |
<!-- END_TABLES -->

---

## 🔍 Repository Breakdown

> [!NOTE]
> The contributor lists and activity metrics for each repository below are compiled according to commits from the last 7 days.

### Hermes Agent (`NousResearch/hermes-agent`)
<!-- START_BD_HERMES_AGENT -->
* **Status**: Highly Active (Total: 1048 commits [1046 H / 2 B], 1 tag/release in the last week). Lines added/deleted: +142.0k/-37.9k (Human), +435/-5 (Bot). **85 commits since installed 0.18.0.r418.g6fad6f1dd-1 (ref=6fad6f1dd).**
* **Contributors (according to last 7 days commits)** (Total: 274 Humans, 2 Bots):
  - **Top Humans**:
    - `teknium1 <127238744+teknium1@users.noreply.github.com>` (Human): 168 commits, +8.0k/-9.8k lines
    - `Brooklyn Nicholson <brooklyn.bb.nicholson@gmail.com>` (Human): 121 commits, +31.6k/-13.3k lines
    - `Teknium <127238744+teknium1@users.noreply.github.com>` (Human): 110 commits, +19.2k/-2.8k lines
    - `kshitijk4poor <82637225+kshitijk4poor@users.noreply.github.com>` (Human): 103 commits, +7.2k/-1.7k lines
    - `srojk34 <286497132+srojk34@users.noreply.github.com>` (Human): 22 commits, +2.4k/-47 lines
    - `xxxigm <tuancanhnguyen706@gmail.com>` (Human): 21 commits, +1.1k/-60 lines
    - `liuhao1024 <sunsky.lau@gmail.com>` (Human): 18 commits, +1.3k/-60 lines
    - `HexLab98 <liruixinch@outlook.com>` (Human): 17 commits, +1.2k/-47 lines
    - `Ben <ben@nousresearch.com>` (Human): 13 commits, +3.5k/-352 lines
    - `devatnull <perkintahmaz50@gmail.com>` (Human): 12 commits, +2.8k/-574 lines
  - **Top Bots**:
    - `Tranquil-Flow <agent@tranquil-flow.dev>` (Bot): 1 commits, +357/-4 lines
    - `hinotoi-agent <paperlantern.agent@gmail.com>` (Bot): 1 commits, +78/-1 lines
<!-- END_BD_HERMES_AGENT -->
<!-- START_RF_HERMES_AGENT -->
* **Recent Focus**:
  - `09466971f` chore: map AIalliAI id-form noreply email in AUTHOR_MAP for #44222 salvage
  - `7487afbd9` test(gateway): update stale expectation — #31884 surfaces retry hint for uninterrupted zero-call drops
  - `a14caf775` fix(gateway): stop post-/stop stale interrupt from silently swallowing the next message
  - `83e6a487e` test(tui_gateway): isolate verification.status not_applicable test from stray tmp markers
  - `4df2536f2` chore: map Ahmett101 noreply email in AUTHOR_MAP for #59455
  - `2e828d4b7` fix(background-review): guard summarize against list-shaped tool responses (#59437)
  - `4a80e27bb` fix telegram explicit private thread routing
  - `e53e8a782` fix(mcp): sanitize server names for auth env keys
  - `ef79ad014` fix(dashboard): accept HA ingress prefix paths
  - `3b5c64543` fix(cron): durable run-claim for one-shots instead of a fixed +60s advance
  - `8f849ea36` chore: credit isheng-eqi for #59446 in AUTHOR_MAP
  - `06cc983b8` fix(cron): prevent double-execution of one-shot jobs across concurrent schedulers
  - `f3af7930c` fix(tui_gateway): honor launch profile terminal.cwd for dashboard chat
  - `83f14b2f2` fix(gateway): relax session_key traversal guard to allow interior '/' (#59322)
  - `9d848cc60` fix(cli): pass custom_providers to resolve_display_context_length (#59314)
  - `b5158442f` fix(skills): apply disabled-skill gate to CLI/TUI preloaded skills
  - `1a2885535` fix(web): widen config-aware env resolution to exa/parallel/tavily/brave-free providers
  - `026ab4737` fix(web): use get_env_value for Firecrawl config resolution
  - `3ba5ba89c` test(cron): cover cron_list/status/tick/create CLI helpers
  - `7e7e3af5b` chore: map allenliang2022 in AUTHOR_MAP for #56932 test fold-in
  - `f6d4c1aa6` test(error-classifier): 408 boundary coverage — Copilot user_request_timeout shape, never auto-compress, falsification guard
  - `8457752a3` fix(error-classifier): retry HTTP 408 as timeout instead of aborting as format_error
  - `a88e0fd2a` fix(file-sync): re-deliver deferred Ctrl+C via raise_signal, not os.kill (Windows hard-kill)
  - `c67aab763` chore: map isheng-eqi in AUTHOR_MAP for #59428 salvage
  - `8def4ccb4` fix(cron): reject past one-shot timestamps in update_job fallback + resume_job (#59395)
  - `0800af0b8` perf(cli): TTFT round 2 — live reasoning by default, partial-line streaming, prompt-build cache, stale budget-warning docs (#59389)
  - `4976d3c38` fix(cron): guard update_job past-one-shot + enrich rejection message (#59395)
  - `848089ac9` fix: reject stale one-shot cron jobs
  - `845a2d815` feat(sessions): any prune filter matches all ages; preview shows age span (#59415)
  - `590a19332` fix(skills): don't request Brotli for the centralized skills index
  - `d3602e630` fix(gateway): read multiplex_profiles from nested gateway section
  - `040a5e30d` feat(sessions): full filter surface for prune + bulk archive subcommand (#59327)
  - `0f154e780` fix(gateway): isolate multiplex profile config env reads
  - `9169591c5` test(gateway): pin random tip in topic-mode /new test to kill 1-in-380 flake (#59380)
  - `f761fb9d6` test(gateway): pin source.profile=None on MagicMock fixtures hitting _adapter_for_source
  - `f600dfca9` chore(release): map author emails for PR #56854/#57417 salvage
  - `ab70551b3` fix(gateway): fail-closed adapter resolution for unregistered secondary profiles
  - `8a9bc38c2` fix(gateway): route multiplex profile responses through correct adapter
  - `43a425632` fix(mcp): wake stale cached servers on session startup + AUTHOR_MAP
  - `6f5573c52` test(mcp): make circuit-breaker reconnect stub survive a None session
  - `756dd75fb` fix(mcp): iteration-bound the session-ready poll so frozen-clock tests can't spin forever
  - `27beeb183` fix: reconnect stale MCP sessions before retry
  - `a124d1676` perf: cut first-turn time-to-first-token by ~80% (all platforms) (#59332)
  - `9080c8b4f` test(agent): cover empty tool_calls array stripping in sanitizer (#58755)
  - `a7932d86c` fix(agent): drop empty tool_calls arrays in pre-API sanitizer (#58755)
  - `5cc7c9b6a` chore(release): map derek2000139 author email for PR #57838 salvage
  - `713236dcd` fix(desktop): normalize CRLF back to LF in update-marker files
  - `d00c7193c` fix(desktop/windows): pre-write update marker before quit dwell to prevent backend respawn
  - `81becec45` chore: docs table entry + AUTHOR_MAP for preflight cluster salvage
  - `e8b0e38a2` docs+test(mcp): document skip_preflight and cover the bypass with a test
  - `549def3a2` fix(mcp): add skip_preflight config option for servers serving HTML on GET
  - `32c1c47ee` fix(mcp): add POST probe fallback in preflight content-type check
  - `18e840469` fix(install): guard Windows desktop installs against broken web_server
  - `94205a113` refactor(gateway): move routing index to state.db, make sessions.json an optional legacy mirror (#59203)
  - `571f2a7fd` refactor(auxiliary): fold main_runtime custom-endpoint reuse into the shared client-build path
  - `92da7a997` fix(auxiliary): reuse main_runtime credentials for named custom providers
  - `3c2f628f5` fix(desktop): probe venv python in unwrapWindowsVenvHermesCommand so Repair can escape a broken venv (#59204)
  - `b6f230b88` chore(release): map EdderTalmor author email for PR #41575 salvage
  - `21a012b6a` test(prompt-size): cover resolved-toolset parity and blank-slate minimal count
  - `fe8d02cec` fix(prompt-size): respect enabled/disabled toolsets per platform
  - `6d359e068` test(mcp): initial-connect exhaustion now parks — update awaiting tests
  - `b80b0b682` test(mcp): parked server self-probe revival + AUTHOR_MAP for #54139 salvage
  - `2ea03d8c6` fix(mcp): park after initial connect failures
  - `e412316b8` fix(mcp): self-probe parked servers so they can actually revive (#57129)
  - `cdbdcd643` fix(mcp): re-register tools after a parked server is revived
  - `e33470080` fix(mcp): reset reconnect retry counter after successful session establishment
  - `f26ae4f68` fix(mcp): align OAuth login connect_timeout floor at 315s across CLI and GUI
  - `8a9e30dbd` chore: AUTHOR_MAP entries for #54494/#56699 salvage
  - `d52d2973a` feat(cli): add --connect-timeout flag to hermes mcp add
  - `a34836801` fix: honor configured connect_timeout on MCP OAuth login path
  - `087aa74e6` fix(cli): honor MCP probe connect timeout
  - `613328559` chore(release): map Alix-007 author email for PR #54620 salvage
  - `2bcb893d8` fix(feishu): set client_max_size on the webhook Application
  - `a26680eb2` Enforce Feishu webhook body limit while reading
  - `e82d71db4` fix(whatsapp): set client_max_size on the webhook Application
  - `eec92a92c` Enforce WhatsApp Cloud webhook body limit while reading
  - `deae37e33` fix(tests): add missing json import in msgraph webhook test fixture
  - `4f4cbff8b` fix(msgraph): enforce webhook body limits
  - `3dd5ce236` fix(sms): set client_max_size on the Twilio webhook Application
  - `940b69b1a` fix(sms): bound Twilio webhook body reads to prevent OOM
  - `c5a8df3af` chore(release): map jashlee+microsoft@microsoft.com -> s905060 (PR #57943 salvage)
  - `127d2ee87` fix(photon): bound the sidecar dep self-heal npm run with a timeout
  - `3cd93f6aa` fix(photon): auto-reinstall stale sidecar deps before start
  - `ede7e3163` fix(auxiliary): gate main api_key inheritance on same-host aux base_url
  - `8e09afda2` fix(auxiliary): inherit model.api_key for custom endpoint when per-task key is empty (#9318)
<!-- END_RF_HERMES_AGENT -->


### IronClaw (`nearai/ironclaw`)
<!-- START_BD_IRONCLAW -->
* **Status**: Highly Active (Total: 130 commits [127 H / 3 B], 1 tag/release in the last week). Lines added/deleted: +143.2k/-131.4k (Human), +3.6k/-291 (Bot). **7 commits since installed 0.29.1.r1679.g85c02c2-1 (ref=85c02c2).**
* **Contributors (according to last 7 days commits)** (Total: 11 Humans, 2 Bots):
  - **Top Humans**:
    - `firat.sertgoz <firat.sertgoz@near.ai>` (Human): 49 commits, +47.1k/-4.1k lines
    - `Henry Park <henrypark133@gmail.com>` (Human): 32 commits, +44.5k/-14.7k lines
    - `Illia Polosukhin <ilblackdragon@gmail.com>` (Human): 16 commits, +31.1k/-101.8k lines
    - `jinxin <106428113+italic-jinxin@users.noreply.github.com>` (Human): 15 commits, +7.0k/-8.3k lines
    - `Robert Yan <46699230+think-in-universe@users.noreply.github.com>` (Human): 5 commits, +1.5k/-1.0k lines
    - `Benjamin Kurrek <57506486+BenKurrek@users.noreply.github.com>` (Human): 5 commits, +11.2k/-1.4k lines
    - `Coffee <95295094+hanakannzashi@users.noreply.github.com>` (Human): 1 commits, +107/-0 lines
    - `abbyshekit <153240993+abbyshekit@users.noreply.github.com>` (Human): 1 commits, +43/-3 lines
    - `Pranav Raja <pranavraja99@gmail.com>` (Human): 1 commits, +15/-4 lines
    - `Coffee <zjchen1234@foxmail.com>` (Human): 1 commits, +603/-17 lines
  - **Top Bots**:
    - `dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>` (Bot): 2 commits, +543/-291 lines
    - `ironclaw-ci[bot] <266877842+ironclaw-ci[bot]@users.noreply.github.com>` (Bot): 1 commits, +3.1k/-0 lines
<!-- END_BD_IRONCLAW -->
<!-- START_RF_IRONCLAW -->
* **Recent Focus**:
  - `0606cd55` ci: include PR context in canary Slack reports (#5684)
  - `22102e9c` fix(reborn): refresh automation runs waiting for thread attachment (#5593)
  - `f02e8d49` fix(reborn): clear chat sidebar highlight off chat routes (#5592)
  - `3dad156c` fix(reborn): keep terminal shortcut clear of chat composer (#5589)
  - `62271c2e` Fix subagent spawn run failure (#5170)
  - `b8551ad5` chore: add IronLoop configurations (#5580)
  - `771c1fe4` feat(reborn): project Slack ingress routes from the manifest, delete the Rust policy literals (#5626)
<!-- END_RF_IRONCLAW -->

### ZeroClaw (`zeroclaw-labs/zeroclaw`)
<!-- START_BD_ZEROCLAW -->
* **Status**: Highly Active (Total: 143 commits [143 H / 0 B], 0 tags/releases in the last week). Lines added/deleted: +40.5k/-11.6k (Human), +0/-0 (Bot). **18 commits since installed 0.8.2.r244.g3ec71f114-1 (ref=3ec71f114).**
* **Contributors (according to last 7 days commits)** (Total: 25 Humans, 0 Bots):
  - **Top Humans**:
    - `Dan Gilles <dfgilles@uchicago.edu>` (Human): 35 commits, +4.4k/-701 lines
    - `Marc Collins <marc@nnet.tech>` (Human): 18 commits, +8.6k/-1.8k lines
    - `wangmiao0668000666 <wang.miao86@xydigit.com>` (Human): 15 commits, +2.5k/-1.3k lines
    - `Shane Engelman <contact@shane.gg>` (Human): 13 commits, +6.6k/-6.8k lines
    - `JordanTheJet <morepencils@gmail.com>` (Human): 11 commits, +6.1k/-190 lines
    - `Alix-007 <li.long15@xydigit.com>` (Human): 8 commits, +502/-0 lines
    - `LiLan0125 <li.lan3@xydigit.com>` (Human): 6 commits, +818/-69 lines
    - `ConYel <18070323+ConYel@users.noreply.github.com>` (Human): 6 commits, +937/-103 lines
    - `Jason Perlow <jperlow@gmail.com>` (Human): 5 commits, +1.1k/-35 lines
    - `mazhuima <xie.chaolong@xydigit.com>` (Human): 4 commits, +554/-51 lines
<!-- END_BD_ZEROCLAW -->
<!-- START_RF_ZEROCLAW -->
* **Recent Focus**:
  - `58f85096` docs(agents): sync model_provider trait rename in extension points (#8728)
  - `32d420f6` fix(web): gate MCP server command/url required-ness on transport (#8032)
  - `fead96c8` feat(config): emit x-required-by-transport metadata for mcp servers (#8349)
  - `414a690c` feat(web): visual editor for typed slash-command options in skill bundles (#8620)
  - `939910d2` fix(web): show created storages across all badge-filtered config surfaces (#8345)
  - `54a15a66` refactor(runtime): route the independent-delegate tool registry through the scoped seam (#8744)
  - `1bb55531` fix(gateway): reject empty bearer token in require_auth (#8727)
  - `4a53a148` fix(gateway): exclude env-overridden secrets from reload drift (#8704)
  - `e78a949a` ci(release): ship self-contained desktop installers on all three platforms (#8709)
  - `585b3947` feat(desktop): self-contained installer — bundle the kernel as a Tauri sidecar (#8708)
  - `abe98bac` docs(architecture): restore ADR decision records (#8694)
  - `824e9bbf` feat(skills): add opt-in bounded SKILL.md reflection for skill creation (#8261)
  - `26a410ca` feat(skills): integrate arch-review artifact into PR review session (#6717)
  - `51558af7` fix(audit): remove rag-pdf feature to clear RUSTSEC-2026-0192 (ttf-parser) (#8547)
  - `2782c681` docs(labels): define tracker marker policy (#8715)
  - `1c5ed417` ci(desktop): compile + lint zeroclaw-desktop on macOS/Linux/Windows (#8706)
  - `ba8dff2f` feat(skills): surface security-audit-skipped skills in 'skills list' (#8699)
  - `caed62f9` docs(plugins): add plugin authoring guide series, correct stale plugin claims in docs and source comments (#8621)
<!-- END_RF_ZEROCLAW -->

### LibreFang (`librefang/librefang`)
<!-- START_BD_LIBREFANG -->
* **Status**: Active (Total: 24 commits [17 H / 7 B], 0 tags/releases in the last week). Lines added/deleted: +4.0k/-1.6k (Human), +976/-958 (Bot). **0 commits since installed 2026.6.29.r24.g7be487fe3-1 (ref=7be487fe3).**
* **Contributors (according to last 7 days commits)** (Total: 2 Humans, 1 Bots):
  - **Top Humans**:
    - `Evan <suzukaze.haduki@gmail.com>` (Human): 16 commits, +3.4k/-1.6k lines
    - `Павло <pavvers1@gmail.com>` (Human): 1 commits, +580/-14 lines
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
* **Status**: Highly Active (Total: 110 commits [110 H / 0 B], 0 tags/releases in the last week). Lines added/deleted: +16.5k/-2.9k (Human), +0/-0 (Bot).
* **Contributors (according to last 7 days commits)** (Total: 22 Humans, 0 Bots):
  - **Top Humans**:
    - `chengyongru <chengyongru.ai@gmail.com>` (Human): 35 commits, +3.8k/-810 lines
    - `Xubin Ren <52506698+Re-bin@users.noreply.github.com>` (Human): 18 commits, +1.6k/-245 lines
    - `chengyongru <2755839590@qq.com>` (Human): 16 commits, +4.5k/-1.4k lines
    - `Kenneth Zhao <ken@epenguin.com>` (Human): 7 commits, +1.6k/-81 lines
    - `hamb1y <rishi.s.malnad@gmail.com>` (Human): 7 commits, +404/-33 lines
    - `dajiaohuang <mikewushuwen@outlook.com>` (Human): 3 commits, +214/-26 lines
    - `axelray-dev <110029405+axelray-dev@users.noreply.github.com>` (Human): 3 commits, +206/-30 lines
    - `hata <1553126902@qq.com>` (Human): 2 commits, +69/-11 lines
    - `ThomasZP Yang <thomas_zp_yang@163.com>` (Human): 2 commits, +80/-10 lines
    - `franciscomaestre <francisco@maestretorreblanca.com>` (Human): 2 commits, +171/-1 lines
<!-- END_BD_NANOBOT -->
<!-- START_RF_NANOBOT -->
* **Recent Focus**:
  - `d04ad1a5` fix(gateway): resolve runtime config path for state refresh
  - `67b56cba` @ fix(gateway): self-heal state file PID on server startup
  - `105230cc` fix(cli): print response text when streaming fails in interactive mode
  - `dd014b50` docs(mattermost): finish channel ordering cleanup
  - `595d789c` docs(mattermost): list new channel last
  - `cf352388` fix(mattermost): harden channel lifecycle and streaming
  - `ef978071` style: fix import ordering in mattermost tests
  - `cc70a2a7` fix(mattermost): fix file download paths and mobile streaming
  - `f9806cc6` fix(mattermost): address second round of review feedback
  - `76877036` mattermost: remove unused _BOT_MENTION_RE
  - `a710a7d6` fix(mattermost): address review comments
  - `fff38f11` feat: add Mattermost channel support
  - `5e51c501` feat(feishu): render new session divider
  - `937f04ac` docs(config): document canonical OpenCode provider
  - `9eade9be` test: update quick start provider expectations
<!-- END_RF_NANOBOT -->

### NanoClaw (`nanocoai/nanoclaw`)
<!-- START_BD_NANOCLAW -->
* **Status**: Highly Active (Total: 58 commits [34 H / 24 B], 0 tags/releases in the last week). Lines added/deleted: +2.1k/-1.4k (Human), +45/-45 (Bot). **0 commits since installed r1996.b6cb53e21-1 (ref=b6cb53e21).**
* **Contributors (according to last 7 days commits)** (Total: 5 Humans, 1 Bots):
  - **Top Humans**:
    - `gavrielc <gabicohen22@yahoo.com>` (Human): 30 commits, +973/-1.4k lines
    - `glifocat <ethan@nanoco.ai>` (Human): 1 commits, +13/-3 lines
    - `leetwito <leetwito@gmail.com>` (Human): 1 commits, +8/-3 lines
    - `Amit Shafnir <amit@nanoco.ai>` (Human): 1 commits, +939/-8 lines
    - `Rob Stevenson <this.rob@protonmail.com>` (Human): 1 commits, +137/-26 lines
  - **Top Bots**:
    - `github-actions[bot] <github-actions[bot]@users.noreply.github.com>` (Bot): 24 commits, +45/-45 lines
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
