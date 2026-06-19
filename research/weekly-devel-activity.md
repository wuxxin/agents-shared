# Active AI Assistants: Weekly Development Activity

This document tracks repository activity, commit counts, merge frequency, and release cycles for active assistant projects.

---

#### 📊 Summary of Last 7 Days Activity (June 12, 2026 – June 19, 2026)

#### Repository Overview & Package Status
| Assistant Repo | Stars | Forks | Main Branch | Last Commit | Installed Pkg | Commits Since Pkg | Status |
| :--- | :---: | :---: | :---: | :---: | :--- | :---: | :---: |
| **ironclaw** | 12,459 | 1,460 | `main` | 2026-06-19 | `ironclaw-git` @ `ironclaw.v0.29.1.r1427.gd01df23-1` | 11 | **Highly Active** |
| **zeroclaw** | 31,943 | 4,735 | `master` | 2026-06-19 | `zeroclaw-git` @ `0.8.0.r187.g1a4ba770c2-1` | 21 | **Highly Active** |
| **hermes-agent** | 197,011 | 34,791 | `main` | 2026-06-19 | — | — | **Highly Active** |
| **nanobot** | 44,440 | 7,849 | `main` | 2026-06-18 | — | — | **Highly Active** |
| **picoclaw** | 29,438 | 4,224 | `main` | 2026-06-18 | `picoclaw-git` @ `0.3.0.nightly.20260617.a16a1e15-1` | 12 | **Active** |
| **nanoclaw** | 29,921 | 12,888 | `main` | 2026-06-18 | — | — | **Active** |
| **librefang** | 303 | 61 | `main` | 2026-06-19 | — | — | **Active** |
| **moltis** | 2,748 | 323 | `main` | 2026-06-05 | — | — | **Inactive** |

#### Weekly Activity Metrics (Human vs Bot)
| Assistant Repo | Commits / Week | Lines Added (Human/Bot) | Lines Deleted (Human/Bot) | Merges (Last Wk) | Releases/Tags (Last Wk) | Avg Commits/Wk (4 Wks) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **ironclaw** | **120** / 0 | 119.7k / 0 | 11.0k / 0 | 0 | 0 | 150.0 |
| **zeroclaw** | **207** / 1 | 84.4k / 546 | 20.1k / 1.2k | 0 | 0 | 136.8 |
| **hermes-agent** | **541** / 0 | 88.5k / 0 | 30.2k / 0 | 55 | 0 | 671.2 |
| **nanobot** | **154** / 0 | 15.0k / 0 | 7.7k / 0 | 5 | 0 | 104.8 |
| **picoclaw** | **37** / 5 | 4.3k / 43 | 752 / 44 | 26 | 1 | 38.5 |
| **nanoclaw** | **38** / 14 | 3.6k / 32 | 915 / 32 | 24 | 1 | 35.0 |
| **librefang** | **43** / 11 | 24.9k / 836 | 2.1k / 755 | 0 | 2 | 113.5 |
| **moltis** | **0** / 0 | 0 / 0 | 0 / 0 | 0 | 0 | 21.5 |

---

## 🔍 Repository Breakdown

> [!NOTE]
> The contributor lists and activity metrics for each repository below are compiled according to commits from the last 7 days.


### ZeroClaw (`zeroclaw-labs/zeroclaw`)
* **Status**: Highly Active (Total: 208 commits [207 H / 1 B], 0 tags/releases in the last week). Lines added/deleted: +84.4k/-20.1k (Human), +546/-1.2k (Bot). **21 commits since installed 0.8.0.r187.g1a4ba770c2-1 (ref=1a4ba770c2).**
* **Contributors (according to last 7 days commits)** (Total: 41 Humans, 1 Bots):
  - **Top Humans**:
    - `Dan Gilles <dfgilles@uchicago.edu>` (Human): 42 commits, +13.6k/-2.1k lines
    - `Alix-007 <li.long15@xydigit.com>` (Human): 32 commits, +1.8k/-197 lines
    - `Shane Engelman <contact@shane.gg>` (Human): 30 commits, +18.2k/-4.5k lines
    - `Marc Collins <marc@nnet.tech>` (Human): 25 commits, +30.3k/-10.4k lines
    - `chengzhichao-xydt <cheng.zhichao@xydigit.com>` (Human): 11 commits, +690/-75 lines
    - `JordanTheJet <morepencils@gmail.com>` (Human): 7 commits, +3.0k/-265 lines
    - `Tidux <jon@borg.moe>` (Human): 6 commits, +2.3k/-170 lines
    - `pick-cat <huang.ting3@xydigit.com>` (Human): 6 commits, +563/-46 lines
    - `Cherilyn Buren <88433283+NiuBlibing@users.noreply.github.com>` (Human): 4 commits, +1.1k/-66 lines
    - `dwc1997 <66739829+dwc1997@users.noreply.github.com>` (Human): 4 commits, +100/-43 lines
  - **Top Bots**:
    - `dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>` (Bot): 1 commits, +546/-1.2k lines
* **Recent Focus**: Configured channels and CRUD operations for agents, providers, and channels, featuring cascade deletions and renames for config entries and agent-owned state. Threaded the shared `CanvasStore` into WS chat and ACP agent sessions, resolved missing channels in the CLI binary, and surfaced history-pruning and turn-cancellation as visible ACP events. Replayed ACP session history in session/messages, moved credential redaction to the rendering layer, routed stdout diagnostics through logs, and traced native tool delivery decisions. Introduced typed slash-command options and chunked interaction follow-ups for Discord, supported cached input token pricing from OpenAI-compatible providers, honored profile tool iteration limits, and auto-included discovered MCP tools in `risk_profile`'s `allowed_tools`. Also resolved a Code/Chat tab agent picker bug in ZeroCode, suggested available ports on bind conflicts, and improved Windows portability tests.


### IronClaw (`nearai/ironclaw`)
* **Status**: Highly Active (Total: 120 commits [120 H / 0 B], 0 tags/releases in the last week). Lines added/deleted: +119.7k/-11.0k (Human), +0/-0 (Bot). **11 commits since installed ironclaw.v0.29.1.r1427.gd01df23-1 (ref=d01df23).**
* **Contributors (according to last 7 days commits)** (Total: 14 Humans, 0 Bots):
  - **Top Humans**:
    - `firat.sertgoz <firat.sertgoz@near.ai>` (Human): 26 commits, +14.7k/-1.9k lines
    - `Illia Polosukhin <ilblackdragon@gmail.com>` (Human): 23 commits, +29.2k/-1.8k lines
    - `Henry Park <henrypark133@gmail.com>` (Human): 21 commits, +40.8k/-3.3k lines
    - `Coffee <zjchen1234@foxmail.com>` (Human): 16 commits, +7.0k/-1.1k lines
    - `jinxin <106428113+italic-jinxin@users.noreply.github.com>` (Human): 8 commits, +4.4k/-1.2k lines
    - `Robert Yan <46699230+think-in-universe@users.noreply.github.com>` (Human): 6 commits, +2.2k/-176 lines
    - `Pranav Raja <pranavraja99@gmail.com>` (Human): 6 commits, +1.8k/-45 lines
    - `Zaki Manian <zaki@iqlusion.io>` (Human): 5 commits, +13.4k/-472 lines
    - `Daniel Wang <5139554+danielwpz@users.noreply.github.com>` (Human): 3 commits, +2.1k/-180 lines
    - `aiworkbot <robert.yan@near.ai>` (Human): 2 commits, +536/-37 lines
* **Recent Focus**: Focused heavily on WebChat v2 ("Reborn" project): introduced project and membership endpoints, wired project repository and services into composition, added a read-only agent filesystem viewer in WebUI v2, wired `ProjectService` ports and facades, and started implementing the `ironclaw_projects` crate. Stabilized OAuth flows in Reborn: refreshed credentials on staging, kept gates visible when the auth URL is absent, resolved validation clearing on skills install, and added GitHub authenticated user capability to Codex. Added output-aware no-progress detection with content-digest plumbing in the agent loop, and enabled live visualization of tool arguments while tools are executing. Fixed Gmail auth-resume failure by restoring the persistent-approval grant, switched logs/docs navigation to text labels, and optimized CI Rust cache seeds from the merge queue.

### Hermes Agent (`NousResearch/hermes-agent`)
* **Status**: Highly Active (Total: 541 commits [541 H / 0 B], 55 merges, 0 tags/releases in the last week). Lines added/deleted: +88.5k/-30.2k (Human), +0/-0 (Bot).
* **Contributors (according to last 7 days commits)** (Total: 102 Humans, 0 Bots):
  - **Top Humans**:
    - `Teknium <127238744+teknium1@users.noreply.github.com>` (Human): 134 commits, +16.6k/-3.6k lines
    - `Brooklyn Nicholson <brooklyn.bb.nicholson@gmail.com>` (Human): 50 commits, +7.6k/-2.5k lines
    - `kshitijk4poor <82637225+kshitijk4poor@users.noreply.github.com>` (Human): 32 commits, +1.9k/-498 lines
    - `xxxigm <tuancanhnguyen706@gmail.com>` (Human): 29 commits, +2.2k/-112 lines
    - `teknium1 <127238744+teknium1@users.noreply.github.com>` (Human): 24 commits, +948/-466 lines
    - `brooklyn! <brooklyn.bb.nicholson@gmail.com>` (Human): 22 commits, +6.7k/-1.4k lines
    - `Ben <ben@nousresearch.com>` (Human): 18 commits, +2.5k/-76 lines
    - `Hao Zhe <haozhe4547@gmail.com>` (Human): 16 commits, +4.8k/-932 lines
    - `Ben Barclay <ben@nousresearch.com>` (Human): 12 commits, +2.9k/-607 lines
    - `ethernet <arilotter@gmail.com>` (Human): 11 commits, +610/-1.1k lines
* **Recent Focus**: Gateway and relay updates: integrated WS-only inbound on the gateway adapter (Phase 3), fixed self-provision triggers based on relay-config and NAS token (rather than `is_managed`), and resolved issues with resuming post-compression replies and preserving transcripts when `/compress` rotation is skipped. WebUI and Desktop improvements: supported WebUI installs from read-only sources in Docker, restored display of the Hindsight memory provider on desktop, made session deletion idempotent, allowed scrolling of long user messages in chat history, and locked `react-simple-icons` version. Introduced configurable per-platform system-prompt hint overrides and documented `platform_hints` usage. Removed the `max_models=50` limit in interactive model pickers, distinguished `max_models=0` from unlimited, auto-subscribed calling sessions on `kanban_create`, and resolved database/typing errors in test lanes.

### NanoBot (`HKUDS/nanobot`)
* **Status**: Highly Active (Total: 154 commits [154 H / 0 B], 5 merges, 0 tags/releases in the last week). Lines added/deleted: +15.0k/-7.7k (Human), +0/-0 (Bot).
* **Contributors (according to last 7 days commits)** (Total: 23 Humans, 0 Bots):
  - **Top Humans**:
    - `chengyongru <chengyongru.ai@gmail.com>` (Human): 69 commits, +5.6k/-3.1k lines
    - `chengyongru <2755839590@qq.com>` (Human): 38 commits, +6.8k/-1.6k lines
    - `Xubin Ren <52506698+Re-bin@users.noreply.github.com>` (Human): 10 commits, +304/-2.9k lines
    - `Ilya Gusev <phoenixilya@gmail.com>` (Human): 7 commits, +173/-37 lines
    - `tangtaizhong666 <tangtaizhong792@gmail.com>` (Human): 4 commits, +222/-4 lines
    - `comadreja <comadreja@email.com>` (Human): 3 commits, +27/-2 lines
    - `michaelxer <michaelxer@users.noreply.github.com>` (Human): 2 commits, +83/-14 lines
    - `Haisam <you@example.com>` (Human): 2 commits, +68/-12 lines
    - `w.antar <w.antar@romulus.live>` (Human): 2 commits, +60/-8 lines
    - `04cb <0x04cb@gmail.com>` (Human): 2 commits, +37/-2 lines
* **Recent Focus**: Feishu integration: added CLI commands for QR code scan-to-create bots, stabilized login setup and simplified network error handling, polished login prompts, and added fallback URL handling. Web features: supported Firecrawl keyless MCP presets in WebUI, required API keys for the Keenable search provider with DuckDuckGo fallback, used a shared user-agent, and sent custom headers like `X-Keenable-Title`.

### PicoClaw (`sipeed/picoclaw`)
* **Status**: Active (Total: 42 commits [37 H / 5 B], 26 merges, 1 tag/release in the last week). Lines added/deleted: +4.3k/-752 (Human), +43/-44 (Bot). **12 commits since installed 0.3.0.nightly.20260617.a16a1e15-1 (ref=a16a1e15).**
* **Contributors (according to last 7 days commits)** (Total: 12 Humans, 1 Bots):
  - **Top Humans**:
    - `程智超0668000959 <cheng.zhichao@xydigit.com>` (Human): 9 commits, +49/-15 lines
    - `not-the-author <andreacamilleri21@gmail.com>` (Human): 7 commits, +1.7k/-195 lines
    - `lc6464 <lclc6464@outlook.com>` (Human): 5 commits, +941/-438 lines
    - `徐闻涵0668001344 <xu.wenhan1@xydigit.com>` (Human): 3 commits, +13/-7 lines
    - `jp39 <jp39@gmx.com>` (Human): 3 commits, +619/-47 lines
    - `SiYue-ZO <2835601846@qq.com>` (Human): 3 commits, +180/-35 lines
    - `Carlos Prados <carlos.prados@gmail.com>` (Human): 2 commits, +73/-0 lines
    - `肆月 <2835601846@qq.com>` (Human): 1 commits, +2/-2 lines
    - `徐金城0668000897 <xu.jincheng@xydigit.com>` (Human): 1 commits, +13/-0 lines
    - `Guoguo <i@qwq.trade>` (Human): 1 commits, +134/-4 lines
  - **Top Bots**:
    - `dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>` (Bot): 5 commits, +43/-44 lines
* **Recent Focus**: Added NEAR AI Cloud provider support. Configured Gemini tool calls to pass both camelCase and snake_case `thought_signature` fields in request bodies. Secured OneBot interface by blocking private inbound media fetches and tightening inbound media download limits. Fixed Sogou search parser regex to adapt to new HTML structure, and added diagnostics for Brave search empty results. Bumped various dependencies: `anthropic-sdk-go`, `azure-sdk-for-go/sdk/azidentity`, `golang.org/x/sys`, `golang.org/x/term`, and GitHub actions.

### NanoClaw (`nanocoai/nanoclaw`)
* **Status**: Active (Total: 52 commits [38 H / 14 B], 24 merges, 1 tag/release in the last week). Lines added/deleted: +3.6k/-915 (Human), +32/-32 (Bot). **Not installed as system package.**
* **Contributors (according to last 7 days commits)** (Total: 10 Humans, 1 Bots):
  - **Top Humans**:
    - `Moshe Krupper <moshekrupper@Moshes-MacBook-Pro.local>` (Human): 16 commits, +861/-366 lines
    - `Omri Maya <omri@nanoco.ai>` (Human): 6 commits, +2.0k/-401 lines
    - `Koshkoshinsk <daniel.milliner@gmail.com>` (Human): 4 commits, +26/-2 lines
    - `gavrielc <gavrielc@github>` (Human): 4 commits, +209/-86 lines
    - `Amit Shafnir <amit@nanoco.ai>` (Human): 2 commits, +154/-15 lines
    - `Juntai Park <juntai81@gmail.com>` (Human): 2 commits, +231/-0 lines
    - `exe.dev user <exedev@crane-waterpolo.exe.xyz>` (Human): 1 commits, +2/-0 lines
    - `sturdy4days <58111365+sturdy4days@users.noreply.github.com>` (Human): 1 commits, +2/-16 lines
    - `glifocat <glifocat@gmail.com>` (Human): 1 commits, +3/-3 lines
    - `assafpin <assaf.pinhasi@gmail.com>` (Human): 1 commits, +132/-26 lines
  - **Top Bots**:
    - `github-actions[bot] <github-actions[bot]@users.noreply.github.com>` (Bot): 14 commits, +32/-32 lines
* **Recent Focus**: Extensively restructured agent-to-agent (A2A) approvals: made policy approvers mandatory, enabled optional single approver per policy, restricted approvals strictly to named users, and carried the assigned approver on a `pending_approvals` column rather than in the message payload. Refactored message gating and routing: extracted `sourceAgentGroupId` in routing, split content parsing from `buildGateQuestion`, destructured payload variables, and authorized actions by the payload-named approver (source or target). Incremented system version to 2.1.19, numbered database migration files (017, 018), and updated documentation to reflect support for up to 199k tokens (100% of context window).

### LibreFang (`librefang/librefang`)
* **Status**: Active (Total: 54 commits [43 H / 11 B], 0 merges, 2 tags/releases in the last week). Lines added/deleted: +24.9k/-2.1k (Human), +836/-755 (Bot). **Not installed as system package.**
* **Contributors (according to last 7 days commits)** (Total: 4 Humans, 2 Bots):
  - **Top Humans**:
    - `Evan <suzukaze.haduki@gmail.com>` (Human): 37 commits, +15.6k/-1.4k lines
    - `Paco Navarrete <paco.j.navarrete@gmail.com>` (Human): 3 commits, +145/-50 lines
    - `Павло <pavvers1@gmail.com>` (Human): 2 commits, +9.2k/-602 lines
    - `HuaGu-Dragon <1801943622@qq.com>` (Human): 1 commits, +28/-19 lines
  - **Top Bots**:
    - `dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>` (Bot): 6 commits, +755/-690 lines
    - `github-actions[bot] <41898282+github-actions[bot]@users.noreply.github.com>` (Bot): 5 commits, +81/-65 lines
* **Note**: LibreFang is a community fork of the former `RightNow-AI/openfang` repository, which had **17,623 stars** and **2,252 forks** before going stale.
* **Recent Focus**: Dashboard enhancements: enlarged TOML view, enabled editing of agent system prompts and tools with reset-to-default, added a central prompt repository page with version tracking and agent bindings, and docked the agent panel as a resizable sidebar with an expanded prompt editor. CLI and runtime: localized CLI console output and the TUI launcher, added auto system locale support, and configured the cron-management tool to disable jobs rather than delete them. CI and dependencies: raised Windows test-lane timeout to 90 minutes to handle vendored OpenSSL cold builds, pinned vendored OpenSSL to Strawberry Perl on the Windows lane, resolved `webauthn-rs` linking failures on Windows CI, and updated dependencies.

### Moltis (`moltis-org/moltis`)
* **Status**: Inactive (Total: 0 commits [0 H / 0 B], 0 tags/releases in the last week). Lines added/deleted: +0/-0 (Human), +0/-0 (Bot). **Not installed as system package.**
* **Contributors (according to last 7 days commits)** (Total: 0 Humans, 0 Bots):
* **Recent Focus**: Stable with no active commits this week. Last commit remains 2026-06-05.

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
| **Moltis** | `moltis-org/moltis` | `moltis-git` | AUR `-git` |
| **IronClaw** | `nearai/ironclaw` | `ironclaw-git` | AUR `-git` |
| **Hermes Agent** | `NousResearch/hermes-agent` | — | not installed |
| **NanoBot** | `HKUDS/nanobot` | — | not installed |
| **PicoClaw** | `sipeed/picoclaw` | `picoclaw-git` | AUR `-git` |
| **NanoClaw** | `nanocoai/nanoclaw` | `nanoclaw-git` | AUR `-git` |

### Step 2: Gather local installed Package Versions
For each assistant check if installed as a system package and record the version. On Arch Linux, use `pacman -Q`:

```bash
# Probe all known package names and print installed versions
for pkg in librefang-git moltis-git zeroclaw-git ironclaw-git nanoclaw-git picoclaw-git; do
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
    "moltis": "moltis-git",
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
