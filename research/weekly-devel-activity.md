# Active AI Assistants: Weekly Development Activity

This document tracks repository activity, commit counts, merge frequency, and release cycles for active assistant projects.

---

#### 📊 Summary of Last 7 Days Activity (June 14, 2026 – June 21, 2026)

#### Repository Overview & Package Status
| Assistant Repo | Stars | Forks | Main Branch | Last Commit | Installed Pkg | Commits Since Pkg | Status |
| :--- | :---: | :---: | :---: | :---: | :--- | :---: | :---: |
| **ironclaw** | 12,465 | 1,459 | `main` | 2026-06-20 | `ironclaw-git` @ `ironclaw.v0.29.1.r1448.gc50edb9-1` | 0 | **Highly Active** |
| **zeroclaw** | 31,965 | 4,743 | `master` | 2026-06-20 | `zeroclaw-git` @ `0.8.1.r1.g768f8a28a-1` | 14 | **Highly Active** |
| **hermes-agent** | 198,262 | 35,153 | `main` | 2026-06-20 | — | — | **Highly Active** |
| **nanobot** | 44,483 | 7,859 | `main` | 2026-06-20 | — | — | **Highly Active** |
| **picoclaw** | 29,446 | 4,229 | `main` | 2026-06-18 | `picoclaw-git` @ `0.3.0.nightly.20260620.287853ab-1` | 0 | **Active** |
| **nanoclaw** | 29,935 | 12,890 | `main` | 2026-06-18 | `nanoclaw-git` @ `r1859.625264ba4-1` | 0 | **Active** |
| **librefang** | 305 | 62 | `main` | 2026-06-20 | — | — | **Active** |

#### Weekly Activity Metrics (Human vs Bot)
| Assistant Repo | Commits / Week | Lines Added (Human/Bot) | Lines Deleted (Human/Bot) | Merges (Last Wk) | Releases/Tags (Last Wk) | Avg Commits/Wk (4 Wks) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **ironclaw** | **111** / 0 | 110.6k / 0 | 12.5k / 0 | 0 | 0 | 143.5 |
| **zeroclaw** | **200** / 1 | 82.4k / 546 | 17.3k / 1.2k | 0 | 1 | 133.0 |
| **hermes-agent** | **575** / 0 | 104.0k / 0 | 38.2k / 0 | 64 | 1 | 693.0 |
| **nanobot** | **127** / 0 | 9.9k / 0 | 2.8k / 0 | 2 | 0 | 103.0 |
| **picoclaw** | **27** / 5 | 2.3k / 43 | 549 / 44 | 20 | 0 | 33.8 |
| **nanoclaw** | **33** / 8 | 2.6k / 17 | 762 / 17 | 20 | 1 | 31.0 |
| **librefang** | **76** / 14 | 36.1k / 969 | 3.9k / 880 | 0 | 2 | 87.5 |

---

## 🔍 Repository Breakdown

> [!NOTE]
> The contributor lists and activity metrics for each repository below are compiled according to commits from the last 7 days.


### ZeroClaw (`zeroclaw-labs/zeroclaw`)
* **Status**: Highly Active (Total: 201 commits [200 H / 1 B], 1 tag/release in the last week). Lines added/deleted: +82.4k/-17.3k (Human), +546/-1.2k (Bot). **14 commits since installed 0.8.1.r1.g768f8a28a-1 (ref=768f8a28a).**
* **Contributors (according to last 7 days commits)** (Total: 38 Humans, 1 Bots):
  - **Top Humans**:
    - `Dan Gilles <dfgilles@uchicago.edu>` (Human): 38 commits, +10.9k/-1.4k lines
    - `Marc Collins <marc@nnet.tech>` (Human): 33 commits, +33.5k/-8.3k lines
    - `Shane Engelman <contact@shane.gg>` (Human): 29 commits, +18.4k/-4.7k lines
    - `Alix-007 <li.long15@xydigit.com>` (Human): 27 commits, +1.4k/-143 lines
    - `Jason Perlow <jperlow@gmail.com>` (Human): 8 commits, +1.1k/-103 lines
    - `chengzhichao-xydt <cheng.zhichao@xydigit.com>` (Human): 8 commits, +499/-52 lines
    - `JordanTheJet <morepencils@gmail.com>` (Human): 7 commits, +3.0k/-272 lines
    - `pick-cat <huang.ting3@xydigit.com>` (Human): 6 commits, +563/-46 lines
    - `Tidux <jon@borg.moe>` (Human): 5 commits, +2.1k/-161 lines
    - `Cherilyn Buren <88433283+NiuBlibing@users.noreply.github.com>` (Human): 4 commits, +1.1k/-66 lines
  - **Top Bots**:
    - `dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>` (Bot): 1 commits, +546/-1.2k lines
* **Recent Focus**: Enabled automatic addition of `zeroclaw` to the system PATH with a `--no-modify-path` opt-out during installation. Refactored Discord channel integration to support rich interaction components (buttons, selects, modals, auto-complete, and buttoned approvals) along with rich embed rendering from `[EMBED:{...}]` markers. Added user/agent scope-selectable `/model` overrides for chat channels, and stopped caching config-derived `static_voice_peers` on channel handles. Integrated typed slash-command options within `SKILL.md` frontmatter. Addressed Groq API compatibility by stripping assistant reasoning tags on outbound replays. Resolved working directory determination for external coding tools to always resolve relative to the project root. On the gateway/dashboard side, resolved device pairing logic for legacy `/pair` endpoints (backfilling orphaned paired tokens) and ensured the dashboard Skills page accurately reflects an agent's effective skills. Also introduced config-alias rename and delete cascade previews, and captured model costs for RPC, zerocode-TUI, and standalone ACP turns.


### IronClaw (`nearai/ironclaw`)
* **Status**: Highly Active (Total: 111 commits [111 H / 0 B], 0 tags/releases in the last week). Lines added/deleted: +110.6k/-12.5k (Human), +0/-0 (Bot). **0 commits since installed ironclaw.v0.29.1.r1448.gc50edb9-1 (ref=c50edb9).**
* **Contributors (according to last 7 days commits)** (Total: 13 Humans, 0 Bots):
  - **Top Humans**:
    - `firat.sertgoz <firat.sertgoz@near.ai>` (Human): 31 commits, +16.6k/-2.3k lines
    - `Illia Polosukhin <ilblackdragon@gmail.com>` (Human): 22 commits, +30.0k/-3.3k lines
    - `Henry Park <henrypark133@gmail.com>` (Human): 17 commits, +32.5k/-2.4k lines
    - `Coffee <zjchen1234@foxmail.com>` (Human): 15 commits, +6.8k/-1.1k lines
    - `jinxin <106428113+italic-jinxin@users.noreply.github.com>` (Human): 6 commits, +2.9k/-1.0k lines
    - `Robert Yan <46699230+think-in-universe@users.noreply.github.com>` (Human): 6 commits, +2.2k/-176 lines
    - `Pranav Raja <pranavraja99@gmail.com>` (Human): 6 commits, +1.8k/-45 lines
    - `aiworkbot <robert.yan@near.ai>` (Human): 3 commits, +1.8k/-1.0k lines
    - `Daniel Wang <5139554+danielwpz@users.noreply.github.com>` (Human): 1 commits, +4/-29 lines
    - `loopstring <yutingytw@gmail.com>` (Human): 1 commits, +442/-53 lines
* **Recent Focus**: Completed the final phase (5/5) of the Projects page layout, fully lighting up Projects in WebChat v2 with project and membership endpoints, service composition, and read-only agent filesystem views. Enhanced the agent loop with output-aware no-progress detection (utilizing content-digest plumbing) and enabled live rendering of tool arguments during execution. Stabilized OAuth and credentials management by suppressing stale extension search credential prompts, bounding approval command previews, keeping auth gates visible when the auth URL is absent, and adding GitHub authenticated user capabilities to Codex. Improved coding tool efficiency by implementing a byte budget for `read_file` to prevent excessive context growth and refining fuzzy matching for the Reborn `apply_patch` tool. Streamlined developer workflows and CI infrastructure by adopting the mold linker, raising build parallelization (`CARGO_BUILD_JOBS` limit lifted), and routing Reborn suites to nightly deep CI.

### Hermes Agent (`NousResearch/hermes-agent`)
* **Status**: Highly Active (Total: 575 commits [575 H / 0 B], 64 merges, 1 tag/release in the last week). Lines added/deleted: +104.0k/-38.2k (Human), +0/-0 (Bot).
* **Contributors (according to last 7 days commits)** (Total: 116 Humans, 0 Bots):
  - **Top Humans**:
    - `Teknium <127238744+teknium1@users.noreply.github.com>` (Human): 100 commits, +19.2k/-6.1k lines
    - `kshitijk4poor <82637225+kshitijk4poor@users.noreply.github.com>` (Human): 62 commits, +3.1k/-851 lines
    - `teknium1 <127238744+teknium1@users.noreply.github.com>` (Human): 44 commits, +8.0k/-2.1k lines
    - `Ben <ben@nousresearch.com>` (Human): 40 commits, +7.2k/-206 lines
    - `Brooklyn Nicholson <brooklyn.bb.nicholson@gmail.com>` (Human): 33 commits, +4.5k/-770 lines
    - `xxxigm <tuancanhnguyen706@gmail.com>` (Human): 27 commits, +1.7k/-60 lines
    - `Ben Barclay <ben@nousresearch.com>` (Human): 19 commits, +4.8k/-670 lines
    - `Austin Pickett <pickett.austin@gmail.com>` (Human): 18 commits, +3.0k/-180 lines
    - `Hao Zhe <haozhe4547@gmail.com>` (Human): 18 commits, +5.0k/-955 lines
    - `brooklyn! <brooklyn.bb.nicholson@gmail.com>` (Human): 13 commits, +2.1k/-390 lines
* **Recent Focus**: Heavily refactored the session compression and compaction systems: introduced non-destructive, durable in-place compaction that maintains a single session ID and preserves the discoverability of compacted turns in session searches, and aborted compression routines early on authentication failure to prevent degraded sessions. Stabilized provider failovers by automatically falling back to alternative providers on persistent 401/403 errors, keeping system-prompt model identities synchronized during failover, and healing poisoned Nous inference URLs upon refresh. Introduced background fan-out capability to spawn parallel subagents and consolidate their returns into a single response. Added a 'Blank Slate' setup mode for minimal agent configuration with opt-in components, and updated the gateway to prevent busy sessions from being interrupted by internal completion events.

### NanoBot (`HKUDS/nanobot`)
* **Status**: Highly Active (Total: 127 commits [127 H / 0 B], 2 merges, 0 tags/releases in the last week). Lines added/deleted: +9.9k/-2.8k (Human), +0/-0 (Bot).
* **Contributors (according to last 7 days commits)** (Total: 25 Humans, 0 Bots):
  - **Top Humans**:
    - `chengyongru <chengyongru.ai@gmail.com>` (Human): 45 commits, +2.9k/-1.2k lines
    - `chengyongru <2755839590@qq.com>` (Human): 26 commits, +4.0k/-1.3k lines
    - `Xubin Ren <52506698+Re-bin@users.noreply.github.com>` (Human): 15 commits, +382/-60 lines
    - `Ilya Gusev <phoenixilya@gmail.com>` (Human): 7 commits, +173/-37 lines
    - `michaelxer <michaelxer@users.noreply.github.com>` (Human): 4 commits, +268/-24 lines
    - `sbyinin <2064038+sbyinin@users.noreply.github.com>` (Human): 3 commits, +245/-26 lines
    - `comadreja <comadreja@email.com>` (Human): 3 commits, +27/-2 lines
    - `yu-xin-c <2182712990@qq.com>` (Human): 2 commits, +284/-10 lines
    - `Haisam <you@example.com>` (Human): 2 commits, +68/-12 lines
    - `w.antar <w.antar@romulus.live>` (Human): 2 commits, +60/-8 lines
* **Recent Focus**: Polished Feishu integration by simplifying table card extraction (row parsing) and supporting WebSocket-rendered Feishu card content. Addressed Model Context Protocol (MCP) stability issues: set explicit HTTPX timeouts for the streamable HTTP transport to avoid event loop blocking, and isolated timeout regression testing from DNS dependencies. Hardened session teardown by ensuring that deleting a session removes legacy file paths to prevent accidental history revival. Resolved OpenAI image reference path expansion issues on Windows, and adjusted image processing to use non-descriptive placeholders when stripping images, updating placeholder assertions accordingly in tests.

### PicoClaw (`sipeed/picoclaw`)
* **Status**: Active (Total: 32 commits [27 H / 5 B], 20 merges, 0 tags/releases in the last week). Lines added/deleted: +2.3k/-549 (Human), +43/-44 (Bot). **0 commits since installed 0.3.0.nightly.20260620.287853ab-1 (ref=287853ab).**
* **Contributors (according to last 7 days commits)** (Total: 10 Humans, 1 Bots):
  - **Top Humans**:
    - `程智超0668000959 <cheng.zhichao@xydigit.com>` (Human): 7 commits, +24/-9 lines
    - `lc6464 <lclc6464@outlook.com>` (Human): 5 commits, +941/-438 lines
    - `徐闻涵0668001344 <xu.wenhan1@xydigit.com>` (Human): 3 commits, +13/-7 lines
    - `jp39 <jp39@gmx.com>` (Human): 3 commits, +619/-47 lines
    - `SiYue-ZO <2835601846@qq.com>` (Human): 3 commits, +180/-35 lines
    - `Carlos Prados <carlos.prados@gmail.com>` (Human): 2 commits, +73/-0 lines
    - `肆月 <2835601846@qq.com>` (Human): 1 commits, +2/-2 lines
    - `徐金城0668000897 <xu.jincheng@xydigit.com>` (Human): 1 commits, +13/-0 lines
    - `Guoguo <i@qwq.trade>` (Human): 1 commits, +134/-4 lines
    - `LC <lclc6464@outlook.com>` (Human): 1 commits, +347/-7 lines
  - **Top Bots**:
    - `dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>` (Bot): 5 commits, +43/-44 lines
* **Recent Focus**: Secured and refined remote cron command executions by restricting command access paths while introducing warnings for cron remote wildcards. Stabilized Gemini tool calls by including both camelCase and snake_case `thought_signature` fields in request payloads. Hardened integration endpoints: updated Sogou web search parsing to match their updated HTML structure, added diagnostic logs for empty Brave search queries, restricted private media fetches and tightened download limits in OneBot, and supported forum topics on Telegram by utilizing the `compositeChatID` in chat contexts. Mitigated file system errors by explicitly ignoring `Close()` failures on directory file descriptors and in write error paths. Updated core dependencies including the Anthropic SDK, Azure Identity, and Go sys/term libraries.

### NanoClaw (`nanocoai/nanoclaw`)
* **Status**: Active (Total: 41 commits [33 H / 8 B], 20 merges, 1 tag/release in the last week). Lines added/deleted: +2.6k/-762 (Human), +17/-17 (Bot). **0 commits since installed r1859.625264ba4-1 (ref=625264ba4).**
* **Contributors (according to last 7 days commits)** (Total: 10 Humans, 1 Bots):
  - **Top Humans**:
    - `Moshe Krupper <moshekrupper@Moshes-MacBook-Pro.local>` (Human): 16 commits, +861/-366 lines
    - `Koshkoshinsk <daniel.milliner@gmail.com>` (Human): 4 commits, +26/-2 lines
    - `gavrielc <gavrielc@github>` (Human): 3 commits, +209/-82 lines
    - `Amit Shafnir <amit@nanoco.ai>` (Human): 2 commits, +154/-15 lines
    - `Juntai Park <juntai81@gmail.com>` (Human): 2 commits, +231/-0 lines
    - `Omri Maya <omri@nanoco.ai>` (Human): 2 commits, +1.0k/-252 lines
    - `exe.dev user <exedev@crane-waterpolo.exe.xyz>` (Human): 1 commits, +2/-0 lines
    - `sturdy4days <58111365+sturdy4days@users.noreply.github.com>` (Human): 1 commits, +2/-16 lines
    - `glifocat <glifocat@gmail.com>` (Human): 1 commits, +3/-3 lines
    - `assafpin <assaf.pinhasi@gmail.com>` (Human): 1 commits, +132/-26 lines
  - **Top Bots**:
    - `github-actions[bot] <github-actions[bot]@users.noreply.github.com>` (Bot): 8 commits, +17/-17 lines
* **Recent Focus**: Refactored the Agent-to-Agent (A2A) approvals framework: implemented mandatory policy approvers with optional single approver limits per policy, restricted approvals strictly to named users via a dedicated `pending_approvals` database column, and enabled flexible authorizations where either the source or target policy approver can resolve a payload-named authorization. Restructured message routing by extracting the `sourceAgentGroupId` and separating content parsing from the `buildGateQuestion` generation. Upgraded the system database migrations (017, 018), bumped the system version to 2.1.19, and updated the documentation to support contexts of up to 199k tokens (occupying 100% of the context window).

### LibreFang (`librefang/librefang`)
* **Status**: Active (Total: 90 commits [76 H / 14 B], 0 merges, 2 tags/releases in the last week). Lines added/deleted: +36.1k/-3.9k (Human), +969/-880 (Bot). **Not installed as system package.**
* **Contributors (according to last 7 days commits)** (Total: 5 Humans, 2 Bots):
  - **Top Humans**:
    - `Evan <suzukaze.haduki@gmail.com>` (Human): 65 commits, +20.5k/-1.9k lines
    - `Павло <pavvers1@gmail.com>` (Human): 4 commits, +14.9k/-1.9k lines
    - `Paco Navarrete <paco.j.navarrete@gmail.com>` (Human): 4 commits, +617/-84 lines
    - `BunnyMoth <bunnymoth@proton.me>` (Human): 2 commits, +40/-31 lines
    - `HuaGu-Dragon <1801943622@qq.com>` (Human): 1 commits, +28/-19 lines
  - **Top Bots**:
    - `github-actions[bot] <41898282+github-actions[bot]@users.noreply.github.com>` (Bot): 7 commits, +134/-110 lines
    - `dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>` (Bot): 7 commits, +835/-770 lines
* **Note**: LibreFang is a community fork of the former `RightNow-AI/openfang` repository, which had **17,623 stars** and **2,252 forks** before going stale.
* **Recent Focus**: Focused heavily on redesigning and stabilizing the automations manager dashboard UI: introduced customizable layout templates, aligned toolbar controls, collapsed execution history by default, and refined mobile responsiveness. Strengthened automation security and execution rules by strictly preventing unbound automation executions, requiring bound sessions, and refreshing goal continuation contexts. Refactored the built-in file tools configuration with a `tools.file.enable` switch to allow toggling standard file operations on subagents. Improved dashboard configuration by grouping the agent panel into 'Core Agents' and 'Hands' categories, and merging settings instead of replacing configs. Added telemetry features including an agent dimension for tool execution latency and detailed failure breakdowns. Expanded provider options to cover Fable models (`claude-fable-5`) and updated partner documentation.
---

## 📋 Instruction Guide: Recreating this Analysis

To re-perform this development activity analysis, follow these steps.

- Read this instructions, then follow these steps for a new analysis

### Step 1: Repository Reference Map
Here is the list of active upstream GitHub repositories and their corresponding system package names (if installed):

| Assistant | GitHub Repo | System Package | Pkg Type |
| :--- | :--- | :--- | :--- |
| **LibreFang** | `librefang/librefang` | `librefang-git` | AUR `-git` |
| **ZeroClaw** | `zeroclaw-labs/zeroclaw` | `zeroclaw-git` | AUR `-git` |
| **IronClaw** | `nearai/ironclaw` | `ironclaw-git` | AUR `-git` |
| **Hermes Agent** | `NousResearch/hermes-agent` | — | not installed |
| **NanoBot** | `HKUDS/nanobot` | — | not installed |
| **PicoClaw** | `sipeed/picoclaw` | `picoclaw-git` | AUR `-git` |
| **NanoClaw** | `nanocoai/nanoclaw` | `nanoclaw-git` | AUR `-git` |

### Step 2: Gather local installed Package Versions
For each assistant check if installed as a system package and record the version. On Arch Linux, use `pacman -Q`:

```bash
# Probe all known package names and print installed versions
for pkg in librefang-git zeroclaw-git ironclaw-git nanoclaw-git picoclaw-git; do
  ver=$(pacman -Q "$pkg" 2>/dev/null | awk '{print $2}')
  if [ -n "$ver" ]; then
    echo "$pkg: $ver"
  else
    echo "$pkg: not installed"
  fi
done
```

**Version format notes** (Arch `-git` packages follow `pkgver-pkgrel`):
* `-git` packages with a tag base embed the git hash after `g`: e.g. `2026.5.25beta.13.r1.gd4adc14f8-1`
  * Extract the commit hash after the last `g`: `echo "$ver" | grep -oP 'g\K[0-9a-f]+'`
  * The `rN` part is the number of commits *past* the last tag.
* `-git` packages without tags use `r<revcount>.<hash>`: e.g. `r1687.24922593e-1`
  * Extract with: `echo "$ver" | grep -oP 'r[0-9]+\.\K[0-9a-f]+'`
* Release packages use the upstream tag directly: e.g. `0.2.8-1` → git tag `v0.2.8`.

### Step 3: Gathering Data via Local Clone
If you have local checkouts of the repositories under `scratch/`, make sure they are up-to-date by fetching and resetting to the latest origin tracking branches (to prevent stale local statistics):

```bash
# 1. Clone any missing repositories (e.g. hermes-agent or librefang) using shallow clone
git clone --depth 2000 https://github.com/NousResearch/hermes-agent.git scratch/hermes-agent

# 2. Fetch the latest commits for existing checkouts
git fetch --all

# 3. Reset local branches to the remote counterpart
# Note: ZeroClaw uses 'master' as its default branch; all others use 'main'.
git checkout main && git reset --hard origin/main
# (or for zeroclaw: git checkout master && git reset --hard origin/master)
```

Once updated, you can query statistics for each repository:

```bash
# 1. Total commits in the last 7 days
git log --since="7 days ago" --no-merges --oneline | wc -l

# 1.1 Commits since installed package version.
#     For -git packages: extract the embedded commit hash from pacman version.
#     For release packages: map version to a git tag (e.g. 0.2.8 -> v0.2.8).
pkg_ver=$(pacman -Q "$PKG_NAME" 2>/dev/null | awk '{print $2}')
if [ -n "$pkg_ver" ]; then
  # Try to extract git hash: format <tag>.rN.g<hash> (most -git packages)
  installed_ref=$(echo "$pkg_ver" | grep -oP 'g\K[0-9a-f]+')
  # Fallback: format r<revcount>.<hash> (no-tag -git packages like nanoclaw)
  if [ -z "$installed_ref" ]; then
    installed_ref=$(echo "$pkg_ver" | grep -oP 'r[0-9]+\.\K[0-9a-f]+')
  fi
  # Fallback: format <tag>.nightly.<date>.<hash> (release/nightly packages)
  if [ -z "$installed_ref" ]; then
    installed_ref=$(echo "$pkg_ver" | grep -oP 'nightly\.[0-9]+\.\K[0-9a-f]+')
  fi
  if [ -z "$installed_ref" ]; then
    # Release package: strip pkgrel suffix and prepend 'v'
    installed_ref="v$(echo "$pkg_ver" | sed 's/-[0-9]*$//')"
  fi
  echo "Commits since installed ($installed_ref):"
  git log --no-merges --oneline "${installed_ref}..HEAD" | wc -l
fi

# 2. Total pull request merges in the last 7 days
git log --since="7 days ago" --merges --oneline | wc -l

# 3. Last commit date
git log -1 --format="%ad" --date=short

# 4. Average weekly commits over the last 4 weeks
# (Total commits divided by 4)
git log --since="28 days ago" --no-merges --oneline | wc -l

# 5. List tags/releases created in the last 7 days
git log --tags --since="7 days ago" --simplify-by-decoration --pretty="format:%d %as"

# 6. Show recent commit subjects to summarize focus areas
git log --since="7 days ago" --no-merges --oneline -n 15

# 6.1 If assistant is installed, show commit subjects since installed version
if [ -n "$pkg_ver" ]; then
  echo "--- commits since installed ($installed_ref) ---"
  git log --no-merges --oneline "${installed_ref}..HEAD" -n 25
fi
```

### Step 4: Batch Statistics Helper Script (Python)
To gather all required metrics, including contributor breakdowns and lines added/deleted, run the following Python script (`scratch/collect_stats.py`) from the root directory of the workspace:

```python
#!/usr/bin/env python3
"""
Python script to gather weekly development statistics for all assistant repos.
Classifies commits and line changes as Human or Bot, and lists contributor breakdowns.
"""

import subprocess
import os
from typing import Dict, Any

# Map: directory_name -> pacman package name (empty = not installed)
PKG_MAP = {
    "librefang": "librefang-git",
    "zeroclaw": "zeroclaw-git",
    "ironclaw": "ironclaw-git",
    "hermes-agent": "",
    "nanobot": "",
    "picoclaw": "picoclaw-git",
    "nanoclaw": "nanoclaw-git",
}

ROOT_DIR = "/home/wuxxin/agent-shared/code/agents-shared"


def is_bot(author_info: str) -> bool:
    """Check if the author is a bot/agent based on name or email patterns."""
    author_lc = author_info.lower()
    bot_patterns = [
        "[bot]",
        "github-actions",
        "dependabot",
        "renovate",
        "nanobot@local",
        "agent@ironclaw.com",
        "agent@",
    ]
    return any(pat in author_lc for pat in bot_patterns)


def format_lines(count: int) -> str:
    """Format large numbers with k/M suffixes for readability in table."""
    if count >= 1000000:
        return f"{count / 1000000:.1f}M"
    elif count >= 1000:
        return f"{count / 1000:.1f}k"
    return str(count)


def get_stats(repo_dir: str) -> Dict[str, Any]:
    """Retrieve commits, merges, line stats, tags, and installed packages."""
    full_path = os.path.join(ROOT_DIR, "scratch", repo_dir)
    if not os.path.exists(full_path):
        return {}

    # Git fetch and reset
    try:
        subprocess.run(
            ["git", "fetch", "origin"],
            cwd=full_path,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        # Get remote branch
        res = subprocess.run(
            ["git", "symbolic-ref", "refs/remotes/origin/HEAD"],
            cwd=full_path,
            capture_output=True,
            text=True,
            check=False,
        )
        branch = res.stdout.strip().replace("refs/remotes/origin/", "")
        if not branch:
            res = subprocess.run(
                ["git", "branch", "-r"],
                cwd=full_path,
                capture_output=True,
                text=True,
                check=False,
            )
            branches = res.stdout.split()
            if any("origin/main" in b for b in branches):
                branch = "main"
            elif any("origin/master" in b for b in branches):
                branch = "master"
            else:
                branch = "main"

        subprocess.run(
            ["git", "checkout", branch],
            cwd=full_path,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        subprocess.run(
            ["git", "reset", "--hard", f"origin/{branch}"],
            cwd=full_path,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as e:
        print(f"Error updating {repo_dir}: {e}")

    # Gather commits and lines
    human_commits = 0
    bot_commits = 0
    human_added = 0
    human_deleted = 0
    bot_added = 0
    bot_deleted = 0

    contributors = {}  # author_info -> {"commits": 0, "added": 0, "deleted": 0, "is_bot": bool}

    # Run git log with numstat
    try:
        cmd = [
            "git",
            "log",
            "--since=7 days ago",
            "--no-merges",
            "--numstat",
            "--pretty=format:AUTHOR: %an <%ae>",
        ]
        res = subprocess.run(
            cmd, cwd=full_path, capture_output=True, text=True, check=True
        )

        current_author = None
        current_author_is_bot = False
        for line in res.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            if line.startswith("AUTHOR: "):
                author_info = line[8:]
                current_author = author_info
                current_author_is_bot = is_bot(author_info)
                if current_author not in contributors:
                    contributors[current_author] = {
                        "commits": 0,
                        "added": 0,
                        "deleted": 0,
                        "is_bot": current_author_is_bot,
                    }
                contributors[current_author]["commits"] += 1
                if current_author_is_bot:
                    bot_commits += 1
                else:
                    human_commits += 1
            else:
                # numstat line: added deleted filename
                parts = line.split(None, 2)
                if len(parts) >= 2:
                    added_str, deleted_str = parts[0], parts[1]
                    added = int(added_str) if added_str.isdigit() else 0
                    deleted = int(deleted_str) if deleted_str.isdigit() else 0
                    if current_author:
                        contributors[current_author]["added"] += added
                        contributors[current_author]["deleted"] += deleted
                    if current_author_is_bot:
                        bot_added += added
                        bot_deleted += deleted
                    else:
                        human_added += added
                        human_deleted += deleted
    except Exception as e:
        print(f"Error gathering git log for {repo_dir}: {e}")

    # Merges
    merges = 0
    try:
        res = subprocess.run(
            ["git", "log", "--since=7 days ago", "--merges", "--oneline"],
            cwd=full_path,
            capture_output=True,
            text=True,
            check=True,
        )
        merges = len(res.stdout.strip().splitlines()) if res.stdout.strip() else 0
    except Exception:
        pass

    # Last Commit Date
    last_commit = "N/A"
    try:
        res = subprocess.run(
            ["git", "log", "-1", "--format=%ad", "--date=short"],
            cwd=full_path,
            capture_output=True,
            text=True,
            check=True,
        )
        last_commit = res.stdout.strip()
    except Exception:
        pass

    # Avg Commits (4 weeks)
    avg_commits = 0.0
    try:
        res = subprocess.run(
            ["git", "log", "--since=28 days ago", "--no-merges", "--oneline"],
            cwd=full_path,
            capture_output=True,
            text=True,
            check=True,
        )
        count_28 = len(res.stdout.strip().splitlines()) if res.stdout.strip() else 0
        avg_commits = count_28 / 4.0
    except Exception:
        pass

    # Tags
    tags_list = []
    try:
        res = subprocess.run(
            [
                "git",
                "log",
                "--tags",
                "--since=7 days ago",
                "--simplify-by-decoration",
                "--pretty=format:%d %as",
            ],
            cwd=full_path,
            capture_output=True,
            text=True,
            check=True,
        )
        for line in res.stdout.splitlines():
            line = line.strip()
            if line:
                tags_list.append(line)
    except Exception:
        pass

    return {
        "commits": human_commits + bot_commits,
        "human_commits": human_commits,
        "bot_commits": bot_commits,
        "human_added": human_added,
        "human_deleted": human_deleted,
        "bot_added": bot_added,
        "bot_deleted": bot_deleted,
        "merges": merges,
        "last_commit": last_commit,
        "avg_commits": avg_commits,
        "tags": tags_list,
        "contributors": contributors,
    }


def main():
    for repo in PKG_MAP.keys():
        stats = get_stats(repo)
        if not stats:
            continue
        print(f"=== {repo} ===")
        print(
            f"Commits: Total={stats['commits']} (Human={stats['human_commits']}, Bot={stats['bot_commits']})"
        )
        print(
            f"Lines Added: Human={stats['human_added']} ({format_lines(stats['human_added'])}), Bot={stats['bot_added']} ({format_lines(stats['bot_added'])})"
        )
        print(
            f"Lines Deleted: Human={stats['human_deleted']} ({format_lines(stats['human_deleted'])}), Bot={stats['bot_deleted']} ({format_lines(stats['bot_deleted'])})"
        )
        print(
            f"Merges: {stats['merges']}, Last Commit: {stats['last_commit']}, Avg Commits: {stats['avg_commits']:.1f}"
        )
        print(f"Tags: {stats['tags']}")
        print("Contributors (according to last 7 days commits):")
        humans = [
            item
            for item in stats["contributors"].items()
            if not item[1]["is_bot"]
        ]
        bots = [
            item for item in stats["contributors"].items() if item[1]["is_bot"]
        ]

        # Sort descending by commits
        humans_sorted = sorted(
            humans, key=lambda x: x[1]["commits"], reverse=True
        )
        bots_sorted = sorted(bots, key=lambda x: x[1]["commits"], reverse=True)

        print(f"Total: {len(humans)} Humans, {len(bots)} Bots")
        if humans_sorted:
            print("  - Top Humans:")
            for name, info in humans_sorted[:10]:
                print(
                    f"    - `{name}` (Human): {info['commits']} commits, +{format_lines(info['added'])}/-{format_lines(info['deleted'])} lines"
                )
        if bots_sorted:
            print("  - Top Bots:")
            for name, info in bots_sorted[:3]:
                print(
                    f"    - `{name}` (Bot): {info['commits']} commits, +{format_lines(info['added'])}/-{format_lines(info['deleted'])} lines"
                )
        print()


if __name__ == "__main__":
    main()
```

### Step 5: Gathering Data via GitHub API
If you do not have local clones, you can fetch the statistics using `curl` and the GitHub API. 
*Note: Set your `GITHUB_TOKEN` environment variable if you hit rate limits.*

```bash
# Define target repository and date boundaries
REPO="librefang/librefang"
SINCE_DATE="2026-05-16T00:00:00Z"

# 1. Fetch commits since a given date
curl -s -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/$REPO/commits?since=$SINCE_DATE" | jq '. | length'

# 2. Fetch releases created since a given date
curl -s -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/$REPO/releases" | jq --arg since "$SINCE_DATE" \
  '.[] | select(.created_at >= $since) | {name: .name, tag_name: .tag_name, date: .created_at}'

# 3. Fetch current stars and forks
curl -s -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/$REPO" | jq '{stargazers_count, forks_count}'
```

### Step 6: Compiling the Summary
1. Update the dates in the report title and column headers.
2. Query each active repository using the commands above.
3. Populate the weekly commits, commits since systempkg version, merges, releases, and averages into the table.
4. Review the recent commit subjects to write the brief summary of recent focus areas for each repository, also include changes since systempkg version

### Step 7: Update and Cleanup of Instructions

- Modified the Step 4 batch script to run `git fetch origin` directly inside the loop to ensure stats are calculated against the most up-to-date remote state.
