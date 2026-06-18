# Active AI Assistants: Weekly Development Activity

This document tracks repository activity, commit counts, merge frequency, and release cycles for active assistant projects.

---

#### 📊 Summary of Last 7 Days Activity (June 11, 2026 – June 18, 2026)

#### Repository Overview & Package Status
| Assistant Repo | Stars | Forks | Main Branch | Last Commit | Installed Pkg | Commits Since Pkg | Status |
| :--- | :---: | :---: | :---: | :---: | :--- | :---: | :---: |
| **ironclaw** | 12,456 | 1,458 | `main` | 2026-06-18 | `ironclaw-git` @ `ironclaw.v0.29.1.r1256.g4c185e6-1` | 169 | **Highly Active** |
| **zeroclaw** | 31,937 | 4,729 | `master` | 2026-06-18 | `zeroclaw-git` @ `0.8.0.beta.2.r125.g5eb5eba08-1` | 274 | **Highly Active** |
| **hermes-agent** | 196,146 | 34,510 | `main` | 2026-06-17 | — | — | **Highly Active** |
| **nanobot** | 44,393 | 7,844 | `main` | 2026-06-17 | — | — | **Highly Active** |
| **picoclaw** | 29,436 | 4,223 | `main` | 2026-06-17 | `picoclaw-git` @ `0.2.9.nightly.20260609.46b29a0a-1` | 60 | **Active** |
| **nanoclaw** | 29,903 | 12,880 | `main` | 2026-06-16 | — | — | **Active** |
| **librefang** | 300 | 60 | `main` | 2026-06-18 | `librefang-git` @ `2026.5.31beta.16.r44.g648356c92-1` | 96 | **Active** |
| **moltis** | 2,747 | 323 | `main` | 2026-06-05 | `moltis-git` @ `20260603.01.r8.g48c9a4192-1` | 0 | **Inactive** |

#### Weekly Activity Metrics (Human vs Bot)
| Assistant Repo | Commits / Week | Lines Added (Human/Bot) | Lines Deleted (Human/Bot) | Merges (Last Wk) | Releases/Tags (Last Wk) | Avg Commits/Wk (4 Wks) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **ironclaw** | **132** / 0 | 133.7k / 0 | 14.0k / 0 | 0 | 0 | 151.5 |
| **zeroclaw** | **233** / 1 | 183.7k / 546 | 112.9k / 1.2k | 0 | 1 | 131.8 |
| **hermes-agent** | **562** / 0 | 95.9k / 0 | 32.3k / 0 | 56 | 0 | 658.0 |
| **nanobot** | **155** / 0 | 16.6k / 0 | 7.7k / 0 | 5 | 0 | 106.8 |
| **picoclaw** | **44** / 4 | 5.6k / 48 | 872 / 48 | 30 | 2 | 39.0 |
| **nanoclaw** | **24** / 20 | 3.5k / 41 | 705 / 41 | 25 | 1 | 29.0 |
| **librefang** | **46** / 13 | 19.4k / 689 | 1.5k / 610 | 0 | 2 | 123.5 |
| **moltis** | **0** / 0 | 0 / 0 | 0 / 0 | 0 | 0 | 21.8 |

---

## 🔍 Repository Breakdown

> [!NOTE]
> The contributor lists and activity metrics for each repository below are compiled according to commits from the last 7 days.


### ZeroClaw (`zeroclaw-labs/zeroclaw`)
* **Status**: Highly Active (Total: 234 commits [233 H / 1 B], 1 tag/release in the last week). Lines added/deleted: +183.7k/-112.9k (Human), +546/-1.2k (Bot). **274 commits since installed 0.8.0.beta.2 (r125.g5eb5eba08).**
* **Contributors (according to last 7 days commits)** (Total: 42 Humans, 1 Bots):
  - **Top Humans**:
    - `Dan Gilles <dfgilles@uchicago.edu>` (Human): 58 commits, +18.7k/-2.8k lines
    - `Shane Engelman <contact@shane.gg>` (Human): 35 commits, +114.0k/-96.8k lines
    - `Alix-007 <li.long15@xydigit.com>` (Human): 35 commits, +1.9k/-215 lines
    - `Marc Collins <marc@nnet.tech>` (Human): 20 commits, +25.4k/-10.2k lines
    - `chengzhichao-xydt <cheng.zhichao@xydigit.com>` (Human): 13 commits, +695/-92 lines
    - `JordanTheJet <morepencils@gmail.com>` (Human): 8 commits, +2.9k/-265 lines
    - `pick-cat <huang.ting3@xydigit.com>` (Human): 6 commits, +563/-46 lines
    - `Tidux <jon@borg.moe>` (Human): 6 commits, +4.1k/-169 lines
    - `Jason Perlow <jperlow@gmail.com>` (Human): 5 commits, +846/-21 lines
    - `Cherilyn Buren <88433283+NiuBlibing@users.noreply.github.com>` (Human): 4 commits, +1.1k/-66 lines
  - **Top Bots**:
    - `dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>` (Bot): 1 commits, +546/-1.2k lines
* **Recent Focus**: Introduced the Zerocode doctor pane and restricted the runtime provider boundary by removing `zeroclaw-providers` in favor of RPC-only communication. Enhanced gateway web chat input with slash-command support, added native WhatsApp web media markers, implemented per-channel ack_reactions overrides for Lark/Feishu, and resolved QQ voice redelivery duplication. Refined budget-trimming propagation inside the agent_turn wrapper, bypassed caching for multimodal `[IMAGE:]` markers, normalized Azure OpenAI credentials, and addressed Bedrock structured tool return bugs. Strengthened security with a new agent posture status CLI command and updated default `file_read` tools to reject binary files directly.


### IronClaw (`nearai/ironclaw`)
* **Status**: Highly Active (Total: 132 commits [132 H / 0 B], 0 tags/releases in the last week). Lines added/deleted: +133.7k/-14.0k (Human), +0/-0 (Bot). **169 commits since installed ironclaw.v0.29.1 (r1256.g4c185e6).**
* **Contributors (according to last 7 days commits)** (Total: 14 Humans, 0 Bots):
  - **Top Humans**:
    - `Henry Park <henrypark133@gmail.com>` (Human): 28 commits, +49.7k/-5.4k lines
    - `firat.sertgoz <firat.sertgoz@near.ai>` (Human): 25 commits, +18.9k/-2.9k lines
    - `Illia Polosukhin <ilblackdragon@gmail.com>` (Human): 18 commits, +23.6k/-1.2k lines
    - `Coffee <zjchen1234@foxmail.com>` (Human): 18 commits, +7.4k/-864 lines
    - `Robert Yan <46699230+think-in-universe@users.noreply.github.com>` (Human): 14 commits, +6.2k/-550 lines
    - `jinxin <106428113+italic-jinxin@users.noreply.github.com>` (Human): 9 commits, +6.0k/-1.3k lines
    - `Pranav Raja <pranavraja99@gmail.com>` (Human): 6 commits, +1.8k/-45 lines
    - `Zaki Manian <zaki@iqlusion.io>` (Human): 6 commits, +13.9k/-583 lines
    - `Josh Ford <thisisjoshford@gmail.com>` (Human): 2 commits, +2.5k/-668 lines
    - `Daniel Wang <5139554+danielwpz@users.noreply.github.com>` (Human): 2 commits, +2.1k/-151 lines
* **Recent Focus**: Developed live tool argument streams during execution inside the Reborn operator interface, integrated correlation of thread/run IDs in the Logs panel, stabilized activity visualization, and resolved stuck recurring runs on the automations dashboard. Implemented byte budgets for `read_file` to control context window expansion, refined `apply_patch` matching algorithm, and enhanced HTTP binary/PDF extraction pathways. Restored persistent-approval grant to prevent Gmail auth-resume failures, auto-denied stale AuthFlows on Slack, and moved WebUI v2 to self-host all frontend assets for better latency.

### Hermes Agent (`NousResearch/hermes-agent`)
* **Status**: Highly Active (Total: 562 commits [562 H / 0 B], 56 merges, 0 tags/releases in the last week). Lines added/deleted: +95.9k/-32.3k (Human), +0/-0 (Bot).
* **Contributors (according to last 7 days commits)** (Total: 102 Humans, 0 Bots):
  - **Top Humans**:
    - `Teknium <127238744+teknium1@users.noreply.github.com>` (Human): 154 commits, +20.9k/-5.4k lines
    - `Brooklyn Nicholson <brooklyn.bb.nicholson@gmail.com>` (Human): 57 commits, +8.2k/-3.0k lines
    - `xxxigm <tuancanhnguyen706@gmail.com>` (Human): 30 commits, +2.0k/-134 lines
    - `brooklyn! <brooklyn.bb.nicholson@gmail.com>` (Human): 30 commits, +10.1k/-1.8k lines
    - `kshitijk4poor <82637225+kshitijk4poor@users.noreply.github.com>` (Human): 27 commits, +1.7k/-481 lines
    - `teknium1 <127238744+teknium1@users.noreply.github.com>` (Human): 27 commits, +5.0k/-578 lines
    - `Austin Pickett <pickett.austin@gmail.com>` (Human): 18 commits, +2.7k/-298 lines
    - `helix4u <4317663+helix4u@users.noreply.github.com>` (Human): 14 commits, +1.7k/-170 lines
    - `ethernet <arilotter@gmail.com>` (Human): 13 commits, +666/-1.1k lines
    - `liuhao1024 <sunsky.lau@gmail.com>` (Human): 12 commits, +1.1k/-67 lines
* **Recent Focus**: Enhanced desktop application stability with stranded session recovery on boot failure, custom chat error banner dismissals, immediate title synchronization, continuous streaming paint in secondary chat windows, and Electron version pinning to fix zip extraction failures. Restructured command routing inside OpenViking by utilizing turn locks instead of blocking the main thread, and removed the agent-callable `send_message` tool. Added search headroom compression evaluation reports to `search_files`, integrated Grok-Composer-2.5-Fast, preserved mixed iMessage attachments, and added rate-limiting retries for Codex device logins.

### NanoBot (`HKUDS/nanobot`)
* **Status**: Highly Active (Total: 155 commits [155 H / 0 B], 5 merges, 0 tags/releases in the last week). Lines added/deleted: +16.6k/-7.7k (Human), +0/-0 (Bot).
* **Contributors (according to last 7 days commits)** (Total: 23 Humans, 0 Bots):
  - **Top Humans**:
    - `chengyongru <chengyongru.ai@gmail.com>` (Human): 61 commits, +6.8k/-2.9k lines
    - `chengyongru <2755839590@qq.com>` (Human): 46 commits, +7.3k/-1.7k lines
    - `Xubin Ren <52506698+Re-bin@users.noreply.github.com>` (Human): 9 commits, +278/-2.9k lines
    - `Ilya Gusev <phoenixilya@gmail.com>` (Human): 7 commits, +173/-37 lines
    - `axelray-dev <110029405+axelray-dev@users.noreply.github.com>` (Human): 4 commits, +286/-107 lines
    - `tangtaizhong666 <tangtaizhong792@gmail.com>` (Human): 4 commits, +222/-4 lines
    - `comadreja <comadreja@email.com>` (Human): 3 commits, +27/-2 lines
    - `michaelxer <michaelxer@users.noreply.github.com>` (Human): 2 commits, +83/-14 lines
    - `Haisam <you@example.com>` (Human): 2 commits, +68/-12 lines
    - `w.antar <w.antar@romulus.live>` (Human): 2 commits, +60/-8 lines
* **Recent Focus**: Introduced first-class integration for the Keenable search provider with API key authentication requirements (falling back to DuckDuckGo), including full WebUI, test suite, and documentation support. Added first-class Mistral model support. Refactored the exact-file workspace security allowlist by pruning unused states, enforcing exact writes to Dream memory files, and locking down parent directory link escapes. Improved chat history logic to preserve user turns and block replaying older long turns. Added incoming message read receipts (blue ticks) and corrected activity duration metrics in WebUI.

### PicoClaw (`sipeed/picoclaw`)
* **Status**: Active (Total: 48 commits [44 H / 4 B], 30 merges, 2 tags/releases in the last week). Lines added/deleted: +5.6k/-872 (Human), +48/-48 (Bot). **60 commits since installed 0.2.9.nightly.20260609.46b29a0a-1.**
* **Contributors (according to last 7 days commits)** (Total: 11 Humans, 1 Bots):
  - **Top Humans**:
    - `程智超0668000959 <cheng.zhichao@xydigit.com>` (Human): 10 commits, +59/-17 lines
    - `lc6464 <lclc6464@outlook.com>` (Human): 7 commits, +1.5k/-513 lines
    - `not-the-author <andreacamilleri21@gmail.com>` (Human): 7 commits, +1.7k/-195 lines
    - `SiYue-ZO <2835601846@qq.com>` (Human): 5 commits, +735/-56 lines
    - `jp39 <jp39@gmx.com>` (Human): 4 commits, +764/-48 lines
    - `徐闻涵0668001344 <xu.wenhan1@xydigit.com>` (Human): 3 commits, +13/-7 lines
    - `肆月 <2835601846@qq.com>` (Human): 2 commits, +73/-23 lines
    - `LC <lclc6464@outlook.com>` (Human): 2 commits, +348/-7 lines
    - `Carlos Prados <carlos.prados@gmail.com>` (Human): 2 commits, +73/-0 lines
    - `Guoguo <i@qwq.trade>` (Human): 1 commits, +134/-4 lines
  - **Top Bots**:
    - `dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>` (Bot): 4 commits, +48/-48 lines
* **Recent Focus**: Scoped and configured remote cron command access while warning against remote wildcards. Added a shift-enter hint below the chat composer and adjusted the Sogou search parser regex to support new HTML layouts. Improved OneBot integration security by restricting private inbound media fetches and limiting media downloads. Configured composite chat IDs for Telegram forum topics, resolved several core-path goroutine panic recovery issues, updated Gemini provider logic to send both camelCase and snake_case thought signatures, and switched to Cond-based counter mechanisms inside the agent launcher.

### NanoClaw (`nanocoai/nanoclaw`)
* **Status**: Active (Total: 44 commits [24 H / 20 B], 25 merges, 1 tag/release in the last week). Lines added/deleted: +3.5k/-705 (Human), +41/-41 (Bot). **Not installed as system package.**
* **Contributors (according to last 7 days commits)** (Total: 5 Humans, 1 Bots):
  - **Top Humans**:
    - `gavrielc <gabicohen22@yahoo.com>` (Human): 12 commits, +1.3k/-273 lines
    - `Omri Maya <omri@nanoco.ai>` (Human): 6 commits, +2.0k/-401 lines
    - `Koshkoshinsk <daniel.milliner@gmail.com>` (Human): 4 commits, +26/-2 lines
    - `glifocat <glifocat@gmail.com>` (Human): 1 commits, +3/-3 lines
    - `assafpin <assaf.pinhasi@gmail.com>` (Human): 1 commits, +132/-26 lines
  - **Top Bots**:
    - `github-actions[bot] <github-actions[bot]@users.noreply.github.com>` (Bot): 20 commits, +41/-41 lines
* **Recent Focus**: Upgraded OneCLI gateway tracking upstream changes, integrated Codex CLI installations via `cli-tools.json`, added host-restart setup steps, and resolved interactive device-login warnings. Enabled operator-driven provider selection, dynamic model switching, memory migrations (restricting the schema to `/migrate-memory`), and delivered budget/billing errors gracefully inside the agent runner. Updated documentation tracking maximum context window usage limits up to 196k tokens.

### LibreFang (`librefang/librefang`)
* **Status**: Active (Total: 59 commits [46 H / 13 B], 2 tags/releases in the last week). Lines added/deleted: +19.4k/-1.5k (Human), +689/-610 (Bot). **96 commits since installed 2026.5.31beta.16 (r44.g648356c92).**
* **Contributors (according to last 7 days commits)** (Total: 4 Humans, 2 Bots):
  - **Top Humans**:
    - `Evan <suzukaze.haduki@gmail.com>` (Human): 41 commits, +12.5k/-1.4k lines
    - `Paco Navarrete <paco.j.navarrete@gmail.com>` (Human): 3 commits, +145/-50 lines
    - `HuaGu-Dragon <1801943622@qq.com>` (Human): 1 commits, +28/-19 lines
    - `Павло <pavvers1@gmail.com>` (Human): 1 commits, +6.7k/-97 lines
  - **Top Bots**:
    - `dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>` (Bot): 7 commits, +611/-548 lines
    - `github-actions[bot] <41898282+github-actions[bot]@users.noreply.github.com>` (Bot): 6 commits, +78/-62 lines
* **Note**: LibreFang is a community fork of the former `RightNow-AI/openfang` repository, which had **17,623 stars** and **2,252 forks** before going stale.
* **Recent Focus**: Focused heavily on dashboard enhancements including enlarging the TOML view, supporting reset-to-default for agent prompts/tools, adding a resizable sidebar for the agent panel with a larger editor, and establishing a central prompt repository with versioning/binding. Introduced WebAuthn/FIDO2 passkey logins for dashboard authentication. Enhanced runtime capabilities by disabling rather than deleting cron jobs, propagating W3C traceparents on outbound MCP requests, and accurately reporting model usage. Configured channel-instance bindings for deterministic inbound dispatch, added GitHub/Codeberg source selection for hands, and resolved Windows CI test lane compilation issues by pinning and building vendored OpenSSL.

### Moltis (`moltis-org/moltis`)
* **Status**: Inactive (Total: 0 commits [0 H / 0 B], 0 tags/releases in the last week). Lines added/deleted: +0/-0 (Human), +0/-0 (Bot). **0 commits since installed 20260603.01 (r8.g48c9a4192).**
* **Contributors (according to last 7 days commits)** (Total: 0 Humans, 0 Bots):
* **Recent Focus**: Stable with no active commits this week.

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
