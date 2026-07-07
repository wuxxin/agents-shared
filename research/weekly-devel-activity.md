# Active AI Assistants: Weekly Development Activity

This document tracks repository activity, commit counts, merge frequency, and release cycles for active assistant projects.

---

#### 📊 Summary of Last 7 Days Activity (June 30, 2026 – July 07, 2026)

<!-- START_TABLES -->
#### Repository Overview & Package Status
| Assistant Repo | Stars | Forks | Main Branch | Last Commit | Installed Pkg | Commits Since Pkg | Status |
| :--- | :---: | :---: | :---: | :---: | :--- | :---: | :---: |
| **hermes-agent** | 210,935 | 38,722 | `main` | 2026-07-07 | `hermes-agent-git` @ `0.18.0.r516.g7426c09be-1` | 143 | **Highly Active** |
| **ironclaw** | 12,505 | 1,466 | `main` | 2026-07-07 | `ironclaw-reborn-git` @ `0.29.1.r1679.g85c02c2-1` | 46 | **Highly Active** |
| **zeroclaw** | 32,186 | 4,798 | `master` | 2026-07-07 | `zeroclaw-git` @ `0.8.2.r244.g3ec71f114-1` | 39 | **Highly Active** |
| **librefang** | 318 | 64 | `main` | 2026-07-07 | `librefang-git` @ `2026.6.29.r24.g7be487fe3-1` | 3 | **Active** |
| **nanobot** | 45,105 | 7,959 | `main` | 2026-07-07 | — | — | **Highly Active** |
| **nanoclaw** | 30,151 | 12,893 | `main` | 2026-07-07 | `nanoclaw-git` @ `r1996.b6cb53e21-1` | 9 | **Highly Active** |
| **picoclaw** | 29,616 | 4,272 | `main` | 2026-07-06 | `picoclaw-git` @ `0.3.1.nightly.20260702.2cf030d2-1` | 25 | **Active** |

#### Weekly Activity Metrics (Human vs Bot)
| Assistant Repo | Commits / Week | Lines Added (Human/Bot) | Lines Deleted (Human/Bot) | Merges (Last Wk) | Releases/Tags (Last Wk) | Avg Commits/Wk (4 Wks) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **hermes-agent** | **962** / 2 | 122.3k / 435 | 27.1k / 5 | 51 | 1 | 825.2 |
| **ironclaw** | **135** / 3 | 123.4k / 3.6k | 128.2k / 289 | 0 | 1 | 114.8 |
| **zeroclaw** | **118** / 0 | 43.3k / 0 | 5.4k / 0 | 0 | 0 | 183.5 |
| **librefang** | **12** / 6 | 3.0k / 943 | 774 / 943 | 0 | 0 | 58.5 |
| **nanobot** | **107** / 0 | 16.8k / 0 | 3.2k / 0 | 0 | 0 | 125.8 |
| **nanoclaw** | **39** / 23 | 3.0k / 44 | 2.2k / 44 | 48 | 0 | 40.2 |
| **picoclaw** | **5** / 6 | 4.0k / 715 | 61 / 790 | 15 | 0 | 27.2 |
<!-- END_TABLES -->

---

## 🔍 Repository Breakdown

> [!NOTE]
> The contributor lists and activity metrics for each repository below are compiled according to commits from the last 7 days.

### Hermes Agent (`NousResearch/hermes-agent`)
<!-- START_BD_HERMES_AGENT -->
* **Status**: Highly Active (Total: 964 commits [962 H / 2 B], 1 tag/release in the last week). Lines added/deleted: +122.3k/-27.1k (Human), +435/-5 (Bot). **143 commits since installed 0.18.0.r516.g7426c09be-1 (ref=7426c09be).**
* **Contributors (according to last 7 days commits)** (Total: 260 Humans, 2 Bots):
  - **Top Humans**:
    - `teknium1 <127238744+teknium1@users.noreply.github.com>` (Human): 180 commits, +10.8k/-10.8k lines
    - `Teknium <127238744+teknium1@users.noreply.github.com>` (Human): 118 commits, +19.2k/-2.4k lines
    - `kshitijk4poor <82637225+kshitijk4poor@users.noreply.github.com>` (Human): 115 commits, +7.6k/-1.8k lines
    - `Brooklyn Nicholson <brooklyn.bb.nicholson@gmail.com>` (Human): 34 commits, +9.4k/-3.0k lines
    - `srojk34 <286497132+srojk34@users.noreply.github.com>` (Human): 21 commits, +2.3k/-47 lines
    - `HexLab98 <liruixinch@outlook.com>` (Human): 19 commits, +1.3k/-65 lines
    - `xxxigm <tuancanhnguyen706@gmail.com>` (Human): 17 commits, +956/-36 lines
    - `liuhao1024 <sunsky.lau@gmail.com>` (Human): 17 commits, +1.3k/-65 lines
    - `Ben <ben@nousresearch.com>` (Human): 13 commits, +3.3k/-346 lines
    - `helix4u <4317663+helix4u@users.noreply.github.com>` (Human): 12 commits, +1.4k/-444 lines
  - **Top Bots**:
    - `Tranquil-Flow <agent@tranquil-flow.dev>` (Bot): 1 commits, +357/-4 lines
    - `hinotoi-agent <paperlantern.agent@gmail.com>` (Bot): 1 commits, +78/-1 lines
<!-- END_BD_HERMES_AGENT -->
<!-- START_RF_HERMES_AGENT -->
* **Recent Focus**:
  - `5e51b123f` feat(mem0): add self-hosted mode to the setup wizard
  - `b4289200b` fix(web-server): close OAuth token TOCTOU by writing 0o600 atomically
  - `b1500af27` fix: restore cli-config.yaml.example from main (stale-branch version leaked into salvage)
  - `94b4ac118` chore: add alex107ivanov to AUTHOR_MAP
  - `e0176cbd4` feat(discord): optionally mention approval owners on exec prompts
  - `f76899fac` feat(sessions): wire html + prompt-only formats into 'sessions export'
  - `b172e03c2` feat(cli): filter internal session_meta messages from HTML export
  - `ab07e0652` style(export): restore width: 0 for multi-session flex layout
  - `4bd6fce1c` fix(cli): fix layout width bug and ensure system prompt header is used
  - `271130af5` feat(cli): expand system prompt by default in HTML export
  - `a73015662` feat(cli): redesign system prompt display as dedicated header section
  - `49dd0b1cb` feat(cli): include system prompts in HTML export
  - `a80e5e72b` feat(cli): add standalone HTML session export with sidebar navigation
  - `b598f8e69` feat: add prompt-only session export
  - `9a322726a` fix(mem0): prune dead get_all, wire rerank config default, warn on MEM0_HOST env override
  - `53edf6f98` fix(mem0): make prompt label + platform setup honor host routing precedence
  - `2a14205ff` feat(mem0): self-hosted dashboard backend + recall tuning (salvage #55614)
  - `b2d6a512d` fix: normalize string stop + surface dropped stream/tool_choice in Converse shim
  - `e9da62980` test(bedrock): cover auxiliary Converse routing for non-Claude models
  - `fa651375b` fix(bedrock): route non-Claude auxiliary models through Converse API
  - `d43863f00` fix: widen stale circuit breaker to non-streaming path + all provider-swap resets
  - `437052f03` docs: document HERMES_STREAM_STALE_GIVEUP alongside sibling stream knobs
  - `2985d16be` fix: reset stream-stale breaker on model switch and fallback activation
  - `985e19c11` fix(agent): add cross-turn stream-stale circuit breaker (#58962)
  - `ee66ff279` chore(desktop): drop PR screenshot assets from tree
  - `8ce3c2f99` feat(desktop): add UI scale setting to appearance settings
  - `4c3a388cb` fix(discord): widen expired-defer handling to /thread slash command
  - `b9d9b8aad` fix(discord): handle expired slash defer interactions
  - `acfefa4fd` feat(sessions): full prune-filter set + --redact on sessions export
  - `51dd5695e` docs(i18n): add zh-Hans docs for Markdown/QMD session export
  - `f3c27e30e` refactor(sessions): fold Markdown/QMD export into 'sessions export --format'
  - `91885a32b` feat(sessions): export sessions to markdown
  - `4ca61869c` docs: sharpen bypass comment per review
  - `d33becd87` fix(gateway): demote PRIORITY-path interrupt to queue during compression (#56391)
  - `8ff162fb2` test(installer): guard Ensure-NodeExeOnPath wiring in install.ps1
  - `2bc6e1a74` fix(installer): put node.exe on PATH for Windows npm lifecycle scripts
  - `009b42d00` fix(discord): mirror all interactive prompt payloads into message content
  - `2acbdd184` fix(discord): include approval command in message content
  - `3c63ed3a3` chore: add vampyren to AUTHOR_MAP (PR #59830 salvage)
  - `cc0aa18fe` feat(kanban): add grab-to-pan board scrolling
  - `afb5808d8` feat(discord): make interactive view timeout configurable (#60230)
  - `685f527d6` chore: add andrewhomeyer to AUTHOR_MAP (co-author on snapshot perms salvage)
  - `a1e6ea7d7` fix(tools): keep shell snapshots owner-only
  - `4f6313ead` test(tui): accept profile_home kwarg in _FakeWorker doubles
  - `c6a3d412d` fix(skills): widen call-time skills-dir resolution to skill_manager_tool
  - `4a99571d5` fix(tui): pass profile_home to slash_worker subprocess for profile-local skill discovery (#40677)
  - `f8723c478` fix(skills): resolve skills dir from active profile
  - `491689784` feat: add uninstall dry-run mode
  - `1deeaf71a` fix(discord): truncate thread titles by UTF-16 units + AUTHOR_MAP
  - `0d9ed9214` Add semantic titles for Discord auto-threads
  - `9c272a306` feat(gateway): default session auto-reset to off (mode: none) (#60194)
  - `b899ffd1e` test(e2e): stub reset-notice session info to deflake test_new_resets_session (#60175)
  - `9420f1acb` test(google_meet): assert ladder-based dependency install instead of bespoke pip argv
  - `ba865e403` refactor(setup): route dependency installs through the canonical uv→pip→ensurepip ladder
  - `569b78c1f` fix(setup): bootstrap pip with ensurepip when not available in venv before neutts install
  - `b2c66681c` chore: add flo1t to AUTHOR_MAP
  - `271817913` fix(docs): discord permissions (add Create Public Threads, remove Use External Emojis)
  - `aaeba213d` fix(telegram): bound start_polling() at bootstrap and conflict-retry sites too; strengthen tests
  - `4aaaa206a` fix(telegram): add timeout to start_polling() in network error handler
  - `ce038a0e0` fix(schema): preserve multi-type arrays as anyOf instead of dropping branches
  - `f341cadb7` refactor(discord): detect streaming bodies structurally, not by mock-module sniffing
  - `e0bca1cbe` fix(discord): bound standalone response reads
  - `87be36c24` fix(discord): bound component labels by UTF-16 units
  - `b8ce583e0` fix(discord): bound REST response reads
  - `87b65e24a` refactor(compression): scope Codex-native compaction to the app-server runtime
  - `d1c8c0341` feat(agent): add Codex-native compaction paths
  - `8fc1cb754` fix: repair URL authority whitespace before web fetches (#46363)
  - `a796e0b79` fix: cool down transient Telegram typing failures (#46355)
  - `7ff86f445` refactor(desktop): route preview-pane mermaid fences through shared embeds registry
  - `c0adfd4a6` feat(desktop): render Mermaid code blocks in markdown file preview
  - `299d5c660` fix(cli): safe mode also skips shell-hook registration
  - `fc02b1c27` refactor(cli): simplify safe-mode startup wiring
  - `144457d80` fix(interrupt): extend post-worker /stop guard to Bedrock streaming path
  - `c2c73605e` test: set pool.provider= on mocks to avoid MagicMock truthy guard trigger
  - `2e30a5e62` fix: prevent /stop signal loss and empty provider credential corruption
  - `179ca25a3` chore: add williamumu to AUTHOR_MAP for PR #31041 salvage
  - `8a7d0790d` fix: merge split gateway pairing stores
  - `3c8130a82` fix: re-apply confirmation expiry on the cached-agent live-history path
  - `2c5762f57` chore: debug log for untrusted absolute skill paths; drop misleading test patch
  - `713e50e7d` fix: normalize against tools.skills_tool.SKILLS_DIR, the root skill_view enforces
  - `e7082ea99` test(cron): cover absolute skill path normalization (#59824)
  - `62972060c` fix(cron): normalize absolute skill paths before skill_view (#59824)
  - `07d93413e` fix: default memory null target to memory store (#46356)
  - `6d3d9d0ba` fix: drop timestamp in handle_max_iterations' hand-built api_messages
  - `e7a6d676c` fix: redact expired confirmations in place to preserve role alternation
  - `33a529538` fix(gateway): strip stale dangerous-confirmation text in user messages (#59607)
  - `11516f3cc` perf: partial index so the startup NULL-active repair skips the table scan
  - `b75783e6d` fix(state): heal NULL active rows on every startup, not just pre-v12 DBs
  - `7445df150` test(state): cover explicit active=1 on message INSERT (#51646)
  - `ae878e1ae` fix(state): set active=1 explicitly in message INSERTs (#51646)
  - `043e71f1f` fix(gateway): use process-level HERMES_HOME for identity files (#56993 salvage) (#59341)
  - `4b9d9b205` fix(dashboard): use loopback host for in-container WebSocket client (#58993) [salvage #59682] (#60092)
  - `76979a086` fix(auth): per-profile Anthropic OAuth file + complete port-binding platform set (#57563 salvage) (#59339)
  - `249c69b95` fix(gateway): per-profile pairing whitelist isolation in multiplex mode (#53045 salvage) (#59330)
  - `088b98944` fix(gateway): scope reset banners' session info to the serving profile (#59048 salvage) (#59329)
  - `f1fde49e4` fix(gateway): avoid cross-profile session recovery (#59325)
  - `d29756829` fix(gateway): detect config token credential collisions (#59321)
  - `2726c2138` feat(display): show file_path in skill_view tool progress lines (#60079)
  - `5eac66525` feat(status): expose nous_session_valid on /api/status for hosted-agent self-heal
  - `182256206` test: drop worktree-path sanity guard that fails in CI
  - `444dc0da8` feat(auth): log forensic detail at Nous quarantine so terminal auth death is visible
  - `536ffedbf` feat(docker): re-seed a terminally-dead Nous bootstrap session on boot (#59983)
  - `ef599aa7f` chore: map spiky02plateau in AUTHOR_MAP for #32824 salvage
  - `130e2337c` fix(usage): scope Codex usage pool fallback to AuthError, keep singleton token on account_id read failure
  - `c59b30086` test: lock Codex usage percent polarity
  - `b2213ba87` fix: fetch Codex quota from credential pool
  - `45f5a6e65` refactor(retry): single-source Z.AI overload short-attempts + drop change-detector assert
  - `ba03c5ab2` test(retry): cover Z.AI overload retry ceiling reachability
  - `1c702aa73` fix(agent): run Z.AI overload adaptive backoff on the overloaded path
  - `05cbddc01` Revert "feat(skills): add dynamic-workflow orchestration skill"
  - `91bcfff47` Revert "docs(skills): tighten dynamic-workflow per donovan-yohan review"
  - `8f80a982a` chore: add fanyangCS to AUTHOR_MAP
  - `d42e9b178` fix(auxiliary): recover from stale fallback-candidate credentials instead of aborting
  - `f69e3aadf` fix(auxiliary): refresh auto-routed provider credentials on 401
  - `830165473` fix(web): refresh dashboard model picker
  - `b3bee33ab` fix(tui): keep bare custom model listing stable
  - `4b4f05886` fix(tui): probe active custom model provider
  - `4131ec380` fix(tui): support model picker refresh
  - `70c6ae609` fix(tui): stop hermes --tui -m from persisting the model globally (#59805)
  - `dd7198e71` chore: add tanmayxchoudhary to AUTHOR_MAP
  - `5de42325d` test: expect model slug in autoraise notice dict (follow-up to gpt-5.4 extension)
  - `60391d0ee` fix(agent): don't apply Codex gpt-5.5 autoraise notice when an external context engine is active
  - `fff240896` fix(agent): dedupe Codex gpt-5.5 autoraise notice across agent inits
  - `bdca94e74` fix(compression): keep Codex gpt-5.5 autoraise from lowering a higher threshold
  - `0b6df665a` fix(compression): autoraise gpt-5.3-codex-spark threshold to 70% (#48621)
  - `948993cd6` feat(compression): extend Codex 272K compaction autoraise to gpt-5.4
  - `370a489fb` fix(auxiliary): floor compression timeout so reasoning models don't fall back to marker (#54915)
  - `5e685999a` fix(ci): make the CI timing report unflakeable (#59818)
  - `8cc1ca4ce` chore: add bigstar0920 to AUTHOR_MAP
  - `78ee0aa36` [verified] fix: account for codex replay in compression tail budget
  - `d4bcd93bb` docs: browser provider plugin guide + complete the plugin routing map (#59817)
  - `586acf530` feat(curator): add 'hermes curator usage' — all-skills usage view
  - `4f008b641` docs(skills): tighten dynamic-workflow per donovan-yohan review
  - `5e5191b9f` feat(skills): add dynamic-workflow orchestration skill
  - `2ebf9a90b` refactor(skills): finish shop-app→shop rename in zh-Hans docs
  - `b24ff550c` docs: Plugins subcategory under Extending + secret-source plugin guide + 1Password sidebar fix (#59613)
  - `1ea0bbbb0` feat(config): add display.timestamp_format and honor it in CLI timestamps
  - `94cdd56b8` feat(plugins): surface entry-point plugins in hermes plugins list
  - `51e6ef5fc` feat(banner): size skills display to terminal width instead of fixed 8/47
  - `5431bf292` fix(desktop): default HERMES_DESKTOP_CWD to cwd when --cwd omitted
  - `077419b22` test(desktop): regression-guard fetchJsonViaOauthSession headers (#40069)
  - `7dfd5077c` feat(oneshot): add --usage-file JSON usage report to hermes -z (#59615)
  - `f0f8c84d1` feat(cli): make hermes serve a real headless backend
<!-- END_RF_HERMES_AGENT -->


### IronClaw (`nearai/ironclaw`)
<!-- START_BD_IRONCLAW -->
* **Status**: Highly Active (Total: 138 commits [135 H / 3 B], 1 tag/release in the last week). Lines added/deleted: +123.4k/-128.2k (Human), +3.6k/-289 (Bot). **46 commits since installed 0.29.1.r1679.g85c02c2-1 (ref=85c02c2).**
* **Contributors (according to last 7 days commits)** (Total: 9 Humans, 2 Bots):
  - **Top Humans**:
    - `Henry Park <henrypark133@gmail.com>` (Human): 47 commits, +45.7k/-14.5k lines
    - `firat.sertgoz <firat.sertgoz@near.ai>` (Human): 41 commits, +47.1k/-4.8k lines
    - `jinxin <106428113+italic-jinxin@users.noreply.github.com>` (Human): 18 commits, +8.5k/-8.8k lines
    - `Illia Polosukhin <ilblackdragon@gmail.com>` (Human): 11 commits, +9.5k/-97.9k lines
    - `Benjamin Kurrek <57506486+BenKurrek@users.noreply.github.com>` (Human): 6 commits, +11.2k/-1.4k lines
    - `Coffee <95295094+hanakannzashi@users.noreply.github.com>` (Human): 4 commits, +117/-5 lines
    - `Robert Yan <46699230+think-in-universe@users.noreply.github.com>` (Human): 4 commits, +1.3k/-742 lines
    - `Pranav Raja <pranavraja99@gmail.com>` (Human): 3 commits, +46/-22 lines
    - `abbyshekit <153240993+abbyshekit@users.noreply.github.com>` (Human): 1 commits, +43/-3 lines
  - **Top Bots**:
    - `ironclaw-ci[bot] <266877842+ironclaw-ci[bot]@users.noreply.github.com>` (Bot): 2 commits, +3.1k/-3 lines
    - `dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>` (Bot): 1 commits, +538/-286 lines
<!-- END_BD_IRONCLAW -->
<!-- START_RF_IRONCLAW -->
* **Recent Focus**:
  - `d29d40a0` fix(filesystem): pool libSQL connections to stop concurrent-CAS SQLITE_MISUSE (#5466) (#5751)
  - `c0751d36` test(reborn): CAS-contention + discard-tombstone coverage; fix #5467 InMemory store parity (#5661)
  - `3b6870aa` chore(webui): fix generated frontend ignores (#5728)
  - `a8053cc4` fix(reborn): preserve model outage failure category (#5774)
  - `2d522bd8` chore: update IronLoop network access config (#5771)
  - `9f267e5c` refactor(composition): group llm-admin cluster under llm_admin/ (dissection n6) (#5709)
  - `067eb66d` refactor(composition): group product-auth cluster under product_auth/ (dissection n4) (#5686)
  - `ca8bb1d0` [HST Postgres v2 2/4] Add row-store turn state (#5725)
  - `a560b55c` feat(reborn): localize shell, chat, and extensions UI (#5685)
  - `ff8079bf` Optimize RootFilesystem latency substrate (#5724)
  - `aaec3128` fix(webui-v2): surface tool permission save errors (#5699)
  - `7aa69132` fix(reborn): prevent mobile chat horizontal overflow (#5682)
  - `26fd0730` fix(reborn): make WebUI v2 clientActionId survive insecure origins (#5695)
  - `913aa115` fix(webui-v2): hide unsupported inference config fields (#5697)
  - `3802a89f` chore: enable IronLoop developer network access (#5761)
  - `d9a3b752` reborn: no run-borking failures — collapsed recoverability stack (#4841 + #5389/#5390/#5403/#5613) (#5692)
  - `d9eaae2b` test(reborn): W6-API2 — webui_v2 mid-gate approval refresh over real gate dispatch (#5743)
  - `5a90d3b9` test(reborn): extension activation-gating + HostInternal surface-hiding at int tier (#5738)
  - `ca98b376` test(reborn): lease-expiry wedge coverage via tool-path parking seam (#5476) (#5723)
  - `8bbf2c76` ci(bench): stop forwarding sccache-dist creds (dist compile was slower) (#5755)
  - `a1a1a7d4` chore: update IronLoop auto review config (#5753)
  - `fb4c70d6` ci(bench): forward sccache-dist creds to the benchmarks reusable (#5752)
  - `1255f871` test(reborn): real-egress pipeline + reopen-resume-through-gate harness seams [test-support only] (#5740)
  - `1775ba41` fix(reborn): [PRODUCTION CHANGE] #5572 — forward checkpoint stage/load through HookedLoopCheckpointPort; activate hooks integration coverage (#5733)
  - `12e7a7c3` [PRODUCTION CRATE — trait-object seam, zero behavior change] Real gate-dispatch harness convergence + triggered-delivery outcome proof (#5735)
  - `5787897e` fix(deps): bump crossbeam-epoch 0.9.18→0.9.20 for RUSTSEC-2026-0204; drop stale RUSTSEC-2026-0097 ignore (#5746)
  - `15260cba` test(reborn): triggered Slack delivery skips terminal non-Completed runs (#5719)
  - `ca88418d` test(reborn): outbound real-store durability + PDF attachment extraction coverage (#5660)
  - `3b2dc728` test(reborn): C-MULTIUSER turn/run-state isolation across distinct actors (#5720)
  - `ae3a512e` ci(reborn): coverage-regression ratchet (dry-run) + integration-first coverage rule (#5718)
  - `28da8bd1` test(reborn): W5-SLACK-PAIR — slack pairing coverage + slack-v2-host-beta onto the int-tier lane (#5656)
  - `073cc3d6` ci(reborn): count crate-tier tests in coverage + scoped denominator exemptions (#5658)
  - `2e07cfe5` test(reborn): W5-WEBUI-API-1 — webui_v2 product-API coverage over real RebornServices (#5655)
  - `eaf15e45` test(reborn): composition test-support accessors for WebUI approval/auth interaction services (#5654)
  - `62bfdf9a` test(reborn): duplicate inbound event replays prior ack over the real ledger (#5653)
  - `6ffdab12` test(reborn): update nightly expectations for pairing flow (#5714)
  - `6dd94d2d` docs: update OpenWiki wiki (#5683)
  - `72d3ae4e` Add SQL clients to Reborn image (#5700)
  - `8b229e4d` ci: comment canary results on triggering PR (#5687)
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
* **Status**: Highly Active (Total: 118 commits [118 H / 0 B], 0 tags/releases in the last week). Lines added/deleted: +43.3k/-5.4k (Human), +0/-0 (Bot). **39 commits since installed 0.8.2.r244.g3ec71f114-1 (ref=3ec71f114).**
* **Contributors (according to last 7 days commits)** (Total: 24 Humans, 0 Bots):
  - **Top Humans**:
    - `Dan Gilles <dfgilles@uchicago.edu>` (Human): 29 commits, +3.7k/-646 lines
    - `Marc Collins <marc@nnet.tech>` (Human): 22 commits, +15.9k/-1.8k lines
    - `wangmiao0668000666 <wang.miao86@xydigit.com>` (Human): 12 commits, +2.3k/-1.3k lines
    - `Shane Engelman <contact@shane.gg>` (Human): 11 commits, +4.3k/-924 lines
    - `JordanTheJet <morepencils@gmail.com>` (Human): 11 commits, +6.3k/-190 lines
    - `LiLan0125 <li.lan3@xydigit.com>` (Human): 5 commits, +759/-67 lines
    - `Cherilyn Buren <88433283+NiuBlibing@users.noreply.github.com>` (Human): 4 commits, +103/-55 lines
    - `ConYel <18070323+ConYel@users.noreply.github.com>` (Human): 3 commits, +1.1k/-103 lines
    - `Tidux <jon@borg.moe>` (Human): 3 commits, +594/-15 lines
    - `Jason Perlow <jperlow@gmail.com>` (Human): 2 commits, +484/-32 lines
<!-- END_BD_ZEROCLAW -->
<!-- START_RF_ZEROCLAW -->
* **Recent Focus**:
  - `50282094` refactor(runtime): route Agent::from_config tool assembly through the scoped seam (#8711)
  - `a3ff1af4` feat(tools): add Bocha AI web search provider (#8737)
  - `d04467f3` test(gateway): make persist-failure & archive-failure injection root-safe (ENOTDIR, not DAC) (#8750)
  - `a5b66fed` fix(sop): reject sop_advance on runs parked at a gate (#8747)
  - `433e6a2c` feat(delegate): give independent delegates the target agent MCP and skill tools (#8761)
  - `da09bbc5` fix(deps): bump crossbeam-epoch to 0.9.20 (RUSTSEC-2026-0204) (#8783)
  - `3fab9191` chore(runtime/shell): drop phantom audit citation from SSRF guard comment (#8755)
  - `dd6edc43` feat(zerocode): add ctrl-w word delete (#8774)
  - `b639a2f5` feat(doctor): warn on OpenAI Codex profile/slot wiring mismatch (#8030)
  - `3a6d689a` feat(line): loading indicator, icon/nickname switch, and bind reply feedback (#7768)
  - `b78c6275` test(agent): add the agent-policy parity harness scaffold (#8659)
  - `1f0f920f` fix(gateway): only print dashboard URL when web_dist_dir is available (#7529)
  - `a297be23` fix(sop): execute deterministic capability steps via a registry and fail closed on driverless steps (#8724)
  - `2a8f0421` feat(cost): fill unpriced models from live gateway pricing (#8233)
  - `844ee075` ci(security): add CodeQL analysis and scheduled Trivy image scan (#8729)
  - `dc8b9daa` fix(web): point favicon and sidebar logos to existing logo.png (#8487)
  - `087607a8` feat(runtime): add model context window ctx bar to zerocode tui, gateway agent chat, and command line interactive mode. (#7946)
  - `06969f85` docs(channels): add Git channel + SOP fan-in pages (#8618)
  - `10ca1aad` feat(delegate): await background sessions (#8525)
  - `6405f33f` feat(channels): add Gitea/Forgejo provider for the Git forge channel (#8611)
  - `a4ce8f0d` feat(channels): add Git forge channel (GitHub provider) with SOP ingress (#8609)
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
* **Status**: Active (Total: 18 commits [12 H / 6 B], 0 tags/releases in the last week). Lines added/deleted: +3.0k/-774 (Human), +943/-943 (Bot). **3 commits since installed 2026.6.29.r24.g7be487fe3-1 (ref=7be487fe3).**
* **Contributors (according to last 7 days commits)** (Total: 2 Humans, 1 Bots):
  - **Top Humans**:
    - `Evan <suzukaze.haduki@gmail.com>` (Human): 11 commits, +2.4k/-760 lines
    - `Павло <pavvers1@gmail.com>` (Human): 1 commits, +580/-14 lines
  - **Top Bots**:
    - `dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>` (Bot): 6 commits, +943/-943 lines
<!-- END_BD_LIBREFANG -->
* **Note**: LibreFang is a community fork of the former `RightNow-AI/openfang` repository, which had **17,623 stars** and **2,252 forks** before going stale.
<!-- START_RF_LIBREFANG -->
* **Recent Focus**:
  - `fccd4b66` fix(deps): clear crossbeam-epoch RUSTSEC-2026-0204 advisory (#6400)
  - `72f2026d` docs: update contributors and star history (#6399)
  - `10022a91` docs: update contributors and star history (#6392)
<!-- END_RF_LIBREFANG -->

### NanoBot (`HKUDS/nanobot`)
<!-- START_BD_NANOBOT -->
* **Status**: Highly Active (Total: 107 commits [107 H / 0 B], 0 tags/releases in the last week). Lines added/deleted: +16.8k/-3.2k (Human), +0/-0 (Bot).
* **Contributors (according to last 7 days commits)** (Total: 20 Humans, 0 Bots):
  - **Top Humans**:
    - `chengyongru <chengyongru.ai@gmail.com>` (Human): 38 commits, +4.2k/-1.2k lines
    - `chengyongru <2755839590@qq.com>` (Human): 15 commits, +4.5k/-1.3k lines
    - `Xubin Ren <52506698+Re-bin@users.noreply.github.com>` (Human): 14 commits, +1.4k/-157 lines
    - `hamb1y <rishi.s.malnad@gmail.com>` (Human): 9 commits, +540/-105 lines
    - `Kenneth Zhao <ken@epenguin.com>` (Human): 7 commits, +1.6k/-81 lines
    - `wangjunwei <wangjunwei87@gmail.com>` (Human): 4 commits, +189/-18 lines
    - `dajiaohuang <mikewushuwen@outlook.com>` (Human): 3 commits, +214/-26 lines
    - `hata <1553126902@qq.com>` (Human): 2 commits, +69/-11 lines
    - `ThomasZP Yang <thomas_zp_yang@163.com>` (Human): 2 commits, +80/-10 lines
    - `axelray-dev <110029405+axelray-dev@users.noreply.github.com>` (Human): 2 commits, +168/-30 lines
<!-- END_BD_NANOBOT -->
<!-- START_RF_NANOBOT -->
* **Recent Focus**:
  - `a7b8a9ed` fix(webui): clarify new chat command text
  - `7e135b45` docs(webui): document slash command lifecycles
  - `fa73448f` fix(webui): drive slash command routing from metadata
  - `8a231b6e` fix(webui): finalize turn-ending slash commands
  - `ef5318eb` fix(webui): classify builtin slash commands without metadata
  - `8f68040f` fix(webui): keep slash commands out of streaming state
  - `0f889273` fix(webui): show generic tool arguments in activity
  - `3f33ff31` chore: remove unused dead code
  - `29e99d37` docs: document Alt+Enter multiline input
  - `01a0f5aa` fix: remove unreliable Shift+Enter shortcut
  - `77a60032` fix(cli): make Alt+Enter insert a newline on LF-as-Enter terminals
  - `25a47705` fix(cli): make the xterm modifyOtherKeys Shift+Enter encoding insert a newline
  - `ea0516e6` fix(cli): stop hijacking ControlJ for Shift+Enter, it breaks Enter on WSL
  - `18a230de` feat(cli): support multiline input via Shift+Enter / Alt+Enter
  - `c5e053f8` fix: pin validated DNS for SSRF-safe fetches
<!-- END_RF_NANOBOT -->

### NanoClaw (`nanocoai/nanoclaw`)
<!-- START_BD_NANOCLAW -->
* **Status**: Highly Active (Total: 62 commits [39 H / 23 B], 0 tags/releases in the last week). Lines added/deleted: +3.0k/-2.2k (Human), +44/-44 (Bot). **9 commits since installed r1996.b6cb53e21-1 (ref=b6cb53e21).**
* **Contributors (according to last 7 days commits)** (Total: 4 Humans, 1 Bots):
  - **Top Humans**:
    - `gavrielc <gabicohen22@yahoo.com>` (Human): 30 commits, +958/-1.4k lines
    - `glifocat <ethan@nanoco.ai>` (Human): 7 commits, +1.1k/-806 lines
    - `leetwito <leetwito@gmail.com>` (Human): 1 commits, +8/-3 lines
    - `Amit Shafnir <amit@nanoco.ai>` (Human): 1 commits, +939/-8 lines
  - **Top Bots**:
    - `github-actions[bot] <github-actions[bot]@users.noreply.github.com>` (Bot): 23 commits, +44/-44 lines
<!-- END_BD_NANOCLAW -->
<!-- START_RF_NANOCLAW -->
* **Recent Focus**:
  - `559bb5c` chore: bump version to 2.1.39
  - `8986fef` Apply suggestion from @gavrielc
  - `d3499b7` docs: update token count to 209k tokens · 104% of context window
  - `44f3513` docs: Output Delivery — messages_out comes from <message> envelope parsing, not raw results
  - `e8a3220` fix(agent-runner): match rate_limit_event as a top-level SDK message type
  - `1dda751` docs: update SDK deep-dive from 0.2.x to 0.3.x
  - `4f1b17c` docs: sync DB schema + entity docs with migrations 010-018
  - `967aee2` docs: fix stale claims vs v2.1.38 (skills lists, runtime claims, file refs)
  - `5aac750` docs: rewrite architecture + agent-runner internals to match current code
<!-- END_RF_NANOCLAW -->

### PicoClaw (`sipeed/picoclaw`)
<!-- START_BD_PICOCLAW -->
* **Status**: Active (Total: 11 commits [5 H / 6 B], 0 tags/releases in the last week). Lines added/deleted: +4.0k/-61 (Human), +715/-790 (Bot). **25 commits since installed 0.3.1.nightly.20260702.2cf030d2-1 (ref=2cf030d2).**
* **Contributors (according to last 7 days commits)** (Total: 3 Humans, 1 Bots):
  - **Top Humans**:
    - `Ethan1918 <75773519+Ethan1918@users.noreply.github.com>` (Human): 3 commits, +262/-49 lines
    - `AayushGupta16 <aayugupta04@gmail.com>` (Human): 1 commits, +265/-5 lines
    - `pancake <pancake@nopcode.org>` (Human): 1 commits, +3.4k/-7 lines
  - **Top Bots**:
    - `dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>` (Bot): 6 commits, +715/-790 lines
<!-- END_BD_PICOCLAW -->
<!-- START_RF_PICOCLAW -->
* **Recent Focus**:
  - `994c0aea` fix(providers): resolve tool_use name/args from Function on reloaded history
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
<!-- END_RF_PICOCLAW -->


---
## 📋 Instruction Guide: Recreating this Analysis

**Fully Automated Update**: You can run the automation script `scripts/update-activity.py` with the `--write` (or `-w`) flag to automatically pull all repository updates, calculate the statistics, and optionally write the updated tables directly back into this file:
```bash
python scripts/update-activity.py [--write]
```
