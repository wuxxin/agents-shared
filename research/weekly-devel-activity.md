# Active AI Assistants: Weekly Development Activity

This document tracks repository activity, commit counts, merge frequency, and release cycles for active assistant projects.

---

### 📊 Summary of Last 7 Days Activity (June 04, 2026 – June 11, 2026)

#### Repository Overview & Package Status
| Assistant Repo | Stars | Forks | Main Branch | Last Commit | Installed Pkg | Commits Since Pkg | Status |
| :--- | :---: | :---: | :---: | :---: | :--- | :---: | :---: |
| **ironclaw** | 12,437 | 1,451 | `main` | 2026-06-11 | `ironclaw-git` @ `ironclaw.v0.29.1.r1256.g4c185e6-1` | 53 | **Highly Active** |
| **librefang** | 290 | 56 | `main` | 2026-06-11 | `librefang-git` @ `2026.5.31beta.16.r44.g648356c92-1` | 42 | **Active** |
| **zeroclaw** | 31,874 | 4,719 | `master` | 2026-06-11 | `zeroclaw-git` @ `0.8.0.beta.2.r125.g5eb5eba08-1` | 50 | **Highly Active** |
| **moltis** | 2,735 | 321 | `main` | 2026-06-05 | `moltis-git` @ `20260603.01.r8.g48c9a4192-1` | 0 | **Active** |
| **hermes-agent** | 190,411 | 33,019 | `main` | 2026-06-11 | — | — | **Highly Active** |
| **nanobot** | 44,034 | 7,798 | `main` | 2026-06-09 | — | — | **Active** |
| **picoclaw** | 29,360 | 4,207 | `main` | 2026-06-10 | `picoclaw-git` @ `0.2.9.nightly.20260609.46b29a0a-1` | 10 | **Active** |
| **nanoclaw** | 29,802 | 12,921 | `main` | 2026-06-10 | — | — | **Active** |

#### Weekly Activity Metrics (Human vs Bot)
| Assistant Repo | Commits / Week | Lines Added (Human/Bot) | Lines Deleted (Human/Bot) | Merges (Last Wk) | Releases/Tags (Last Wk) | Avg Commits/Wk (4 Wks) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **ironclaw** | **145** / 10 | 155.0k / 286 | 20.7k / 216 | 2 | 0 | 186.2 |
| **librefang** | **43** / 10 | 5.9k / 1.3k | 537 / 1.2k | 0 | 1 | 148.0 |
| **zeroclaw** | **157** / 0 | 47.5k / 0 | 12.0k / 0 | 0 | 0 | 91.0 |
| **moltis** | **2** / 0 | 1.9k / 0 | 254 / 0 | 0 | 0 | 30.2 |
| **hermes-agent** | **773** / 1 | 144.2k / 189 | 45.8k / 5 | 43 | 1 | 730.2 |
| **nanobot** | **91** / 1 | 29.7k / 315 | 4.3k / 11 | 2 | 0 | 104.8 |
| **picoclaw** | **47** / 2 | 2.2k / 21 | 383 / 21 | 41 | 1 | 34.5 |
| **nanoclaw** | **28** / 15 | 9.0k / 30 | 5.6k / 30 | 13 | 0 | 24.8 |

---

## 🔍 Repository Breakdown

> [!NOTE]
> The contributor lists and activity metrics for each repository below are compiled according to commits from the last 7 days.

### LibreFang (`librefang/librefang`)
* **Status**: Active (Total: 53 commits [43 H / 10 B], 1 release in the last week). Lines added/deleted: +5.9k/-537 (Human), +1.3k/-1.2k (Bot). **42 commits since installed 2026.5.31beta.16 (r44.g648356c92).**
* **Contributors (according to last 7 days commits)** (Total: 4 Humans, 2 Bots):
  - **Top Humans**:
    - `Evan <suzukaze.haduki@gmail.com>` (Human): 36 commits, +4.5k/-399 lines
    - `Vignesh Jagadeesh <vignesh.nrfs@gmail.com>` (Human): 3 commits, +591/-51 lines
    - `Paco Navarrete <paco.j.navarrete@gmail.com>` (Human): 3 commits, +741/-49 lines
    - `Copilot <198982749+Copilot@users.noreply.github.com>` (Human): 1 commit, +72/-38 lines
  - **Top Bots**:
    - `dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>` (Bot): 8 commits, +1.3k/-1.2k lines
    - `github-actions[bot] <41898282+github-actions[bot]@users.noreply.github.com>` (Bot): 2 commits, +23/-23 lines
* **Note**: LibreFang is a community fork of the former `RightNow-AI/openfang` repository, which had **17,623 stars** and **2,252 forks** before going stale.
* **Recent Focus**: Dependency bumping (dashboard, @whiskeysockets/baileys, @types/react); Nix-build runner disk space optimizations; version bumps to beta release tags; database runtime auditing fixes for SQLite DELETE failures; addressing non-ASCII offset misalignments in memory-wiki; fixing unauthenticated pre-handshake buffer pinning; SSRF allowlist omissions; stack overflow prevention on self-referential MCP/skill schemas; and WASM redirection validation.

### ZeroClaw (`zeroclaw-labs/zeroclaw`)
* **Status**: Highly Active (Total: 157 commits [157 H / 0 B], 0 releases in the last week). Lines added/deleted: +47.5k/-12.0k (Human), +0/-0 (Bot). **50 commits since installed 0.8.0.beta.2 (r125.g5eb5eba08).**
* **Contributors (according to last 7 days commits)** (Total: 33 Humans, 0 Bots):
  - **Top Humans**:
    - `Dan Gilles <dfgilles@uchicago.edu>` (Human): 37 commits, +5.8k/-1.1k lines
    - `Shane Engelman <contact@shane.gg>` (Human): 29 commits, +25.2k/-8.3k lines
    - `Alix-007 <li.long15@xydigit.com>` (Human): 12 commits, +504/-72 lines
    - `Cherilyn Buren <88433283+NiuBlibing@users.noreply.github.com>` (Human): 8 commits, +1.2k/-145 lines
    - `Argenis De La Rosa <theonlyhennygod@gmail.com>` (Human): 8 commits, +2.8k/-109 lines
    - `Marc Collins <marc@nnet.tech>` (Human): 6 commits, +1.2k/-74 lines
    - `chengzhichao-xydt <cheng.zhichao@xydigit.com>` (Human): 5 commits, +393/-14 lines
    - `Jason Perlow <jperlow@gmail.com>` (Human): 5 commits, +1.4k/-31 lines
    - `rifuki <rifuki.dev@gmail.com>` (Human): 5 commits, +508/-54 lines
    - `robinDU <drbparadise@gmail.com>` (Human): 5 commits, +387/-19 lines
* **Recent Focus**: Local-only empty document send tests for Telegram channel, pinning Node version with nvmrc, trimming whitespace-only assistant content to prevent blank lines, repairing Quickstart model-provider UX defects, making reload banner dismissable, clippy lint cross-platform gate restoration, dashboard live/persisted/loading status distinctions, and performance updates to avoid final CLI output clones.

### Moltis (`moltis-org/moltis`)
* **Status**: Active (Total: 2 commits [2 H / 0 B], 0 releases in the last week). Lines added/deleted: +1.9k/-254 (Human), +0/-0 (Bot). **0 commits since installed 20260603.01 (r8.g48c9a4192).**
* **Contributors (according to last 7 days commits)** (Total: 2 Humans, 0 Bots):
  - **Top Humans**:
    - `Sergey Salamatov <55296341+s-salamatov@users.noreply.github.com>` (Human): 1 commit, +1.9k/-231 lines
    - `Fabien Penso <gpg@pen.so>` (Human): 1 commit, +23/-23 lines
* **Recent Focus**: Separating Telegram progress stream from final replies in Codex, and documenting/visualizing Polyphony in the workflow presentation deck.

### IronClaw (`nearai/ironclaw`)
* **Status**: Highly Active (Total: 155 commits [145 H / 10 B], 0 releases in the last week). Lines added/deleted: +155.0k/-20.7k (Human), +286/-216 (Bot). **53 commits since installed ironclaw.v0.29.1 (r1256.g4c185e6).**
* **Contributors (according to last 7 days commits)** (Total: 10 Humans, 1 Bots):
  - **Top Humans**:
    - `firat.sertgoz <firat.sertgoz@near.ai>` (Human): 57 commits, +45.9k/-6.8k lines
    - `Henry Park <henrypark133@gmail.com>` (Human): 30 commits, +41.7k/-5.7k lines
    - `Robert Yan <46699230+think-in-universe@users.noreply.github.com>` (Human): 16 commits, +14.2k/-1.3k lines
    - `Coffee <zjchen1234@foxmail.com>` (Human): 11 commits, +10.8k/-562 lines
    - `jinxin <106428113+italic-jinxin@users.noreply.github.com>` (Human): 9 commits, +12.7k/-3.2k lines
    - `Zaki Manian <zaki@iqlusion.io>` (Human): 9 commits, +18.3k/-2.6k lines
    - `Daniel Wang <5139554+danielwpz@users.noreply.github.com>` (Human): 5 commits, +4.7k/-226 lines
    - `Benjamin Kurrek <57506486+BenKurrek@users.noreply.github.com>` (Human): 3 commits, +565/-41 lines
    - `Illia Polosukhin <ilblackdragon@gmail.com>` (Human): 3 commits, +5.5k/-275 lines
    - `Josh Ford <thisisjoshford@gmail.com>` (Human): 2 commits, +572/-48 lines
  - **Top Bots**:
    - `IronClaw Agent <agent@ironclaw.com>` (Bot): 10 commits, +286/-216 lines
* **Recent Focus**: Improving WebUI approval prompt context in codex, parity readiness diagnostics tests, model credential error summary fixes, forcing IANA timezones on cron triggers, Slack DM outbound runs thread owner persistence, documenting Reborn contract APIs, enabling NEAR AI MCP from Reborn env configuration, cutover production gate enforcement, and resume auth-gate re-dispatching of original capability calls.

### Hermes Agent (`NousResearch/hermes-agent`)
* **Status**: Highly Active (Total: 774 commits [773 H / 1 B], 43 merges, 1 release in the last week). Lines added/deleted: +144.2k/-45.8k (Human), +189/-5 (Bot).
* **Contributors (according to last 7 days commits)** (Total: 137 Humans, 1 Bots):
  - **Top Humans**:
    - `Teknium <127238744+teknium1@users.noreply.github.com>` (Human): 168 commits, +28.4k/-12.9k lines
    - `teknium1 <127238744+teknium1@users.noreply.github.com>` (Human): 97 commits, +20.2k/-14.2k lines
    - `Brooklyn Nicholson <brooklyn.bb.nicholson@gmail.com>` (Human): 71 commits, +12.7k/-3.7k lines
    - `brooklyn! <brooklyn.bb.nicholson@gmail.com>` (Human): 37 commits, +12.5k/-3.5k lines
    - `xxxigm <tuancanhnguyen706@gmail.com>` (Human): 23 commits, +1.2k/-86 lines
    - `kshitijk4poor <82637225+kshitijk4poor@users.noreply.github.com>` (Human): 21 commits, +1.8k/-253 lines
    - `underthestars-zhy <zhuhaoyu0909@icloud.com>` (Human): 17 commits, +4.4k/-1.5k lines
    - `helix4u <4317663+helix4u@users.noreply.github.com>` (Human): 16 commits, +1.4k/-138 lines
    - `Ben Barclay <ben@nousresearch.com>` (Human): 15 commits, +2.3k/-80 lines
    - `yoniebans <jonny@nousresearch.com>` (Human): 14 commits, +1.0k/-342 lines
  - **Top Bots**:
    - `Sol Aitken <solaiagent@gmail.com>` (Bot): 1 commit, +189/-5 lines
* **Recent Focus**: Desktop sidebar row deduplication by compression lineage in merge session page, official-SSH remote detection for passive updates, merging PATH in Update-ProcessPathForPackages on Windows instead of overwriting, staging SQLite snapshots beside output zip in update paths, archiving compressed conversation lineages, and preserving detached gateway restart watcher environments.

### NanoBot (`HKUDS/nanobot`)
* **Status**: Active (Total: 92 commits [91 H / 1 B], 2 merges, 0 releases in the last week). Lines added/deleted: +29.7k/-4.3k (Human), +315/-11 (Bot).
* **Contributors (according to last 7 days commits)** (Total: 23 Humans, 1 Bots):
  - **Top Humans**:
    - `chengyongru <chengyongru.ai@gmail.com>` (Human): 24 commits, +2.9k/-455 lines
    - `Xubin Ren <52506698+Re-bin@users.noreply.github.com>` (Human): 24 commits, +16.2k/-2.8k lines
    - `axelray-dev <110029405+axelray-dev@users.noreply.github.com>` (Human): 8 commits, +668/-110 lines
    - `Flávio Veloso Soares <flaviovs@magnux.com>` (Human): 7 commits, +720/-82 lines
    - `chengyongru <2755839590@qq.com>` (Human): 4 commits, +206/-12 lines
    - `Kunal Karmakar <kkdthunlshd@gmail.com>` (Human): 4 commits, +420/-34 lines
    - `moran <moranfong@gmail.com>` (Human): 2 commits, +669/-6 lines
    - `04cb <0x04cb@gmail.com>` (Human): 2 commits, +50/-1 lines
    - `chengyongru <61816729+chengyongru@users.noreply.github.com>` (Human): 2 commits, +4.2k/-583 lines
    - `Jiajun Xie <jiajunbernoulli@foxmail.com>` (Human): 1 commit, +200/-0 lines
  - **Top Bots**:
    - `NanoBot <nanobot@local>` (Bot): 1 commit, +315/-11 lines
* **Recent Focus**: Balanced code block streaming over Telegram, splitting message helper refactoring for fenced code block awareness, SiliconFlow ASR/transcription settings integration and settings views, refactoring sidebar index out of WebUI session manager, index session list metadata optimizations, segmented transcript storage, and click-to-check version updates.

### PicoClaw (`sipeed/picoclaw`)
* **Status**: Active (Total: 49 commits [47 H / 2 B], 41 merges, 1 release in the last week). Lines added/deleted: +2.2k/-383 (Human), +21/-21 (Bot). **10 commits since installed 0.2.9.nightly.20260609.46b29a0a-1.**
* **Contributors (according to last 7 days commits)** (Total: 14 Humans, 1 Bots):
  - **Top Humans**:
    - `程智超0668000959 <cheng.zhichao@xydigit.com>` (Human): 33 commits, +654/-212 lines
    - `lc6464 <lclc6464@outlook.com>` (Human): 2 commits, +566/-75 lines
    - `肆月 <2835601846@qq.com>` (Human): 1 commit, +71/-21 lines
    - `LC <lclc6464@outlook.com>` (Human): 1 commit, +1/-0 lines
    - `cs8425 <cs8425@gmail.com>` (Human): 1 commit, +3/-0 lines
    - `Guoguo <i@qwq.trade>` (Human): 1 commit, +0/-0 lines
    - `Yue_chen <1737456545@qq.com>` (Human): 1 commit, +8/-2 lines
    - `pancake <pancake@nopcode.org>` (Human): 1 commit, +5/-0 lines
    - `2023478 <2694762037@qq.com>` (Human): 1 commit, +43/-0 lines
    - `jp39 <jp39@gmx.com>` (Human): 1 commit, +675/-13 lines
  - **Top Bots**:
    - `dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>` (Bot): 2 commits, +21/-21 lines
* **Recent Focus**: Hardening trusted proxy client IP parsing, launcher access control hardening, hiding console flashes in Windows child processes, normalizing gitignore text encoding, adding ok checks for type assertions in http.Transport CreateHTTPClient, checking strconv.Atoi and json.Unmarshal errors, blocking 198.18.0.0/15 in SSRF guard, and resolving health check defects.

### NanoClaw (`nanocoai/nanoclaw`)
* **Status**: Active (Total: 43 commits [28 H / 15 B], 13 merges, 0 releases in the last week). Lines added/deleted: +9.0k/-5.6k (Human), +30/-30 (Bot). **Not installed as system package.**
* **Contributors (according to last 7 days commits)** (Total: 4 Humans, 1 Bots):
  - **Top Humans**:
    - `gavrielc <gabicohen22@yahoo.com>` (Human): 23 commits, +6.2k/-5.0k lines
    - `Amit Shafnir <amit@nanoco.ai>` (Human): 3 commits, +2.6k/-602 lines
    - `Omri Maya <omri@nanoco.ai>` (Human): 1 commit, +157/-2 lines
    - `markbala <22162779+markbala@users.noreply.github.com>` (Human): 1 commit, +74/-0 lines
  - **Top Bots**:
    - `github-actions[bot] <github-actions[bot]@users.noreply.github.com>` (Bot): 15 commits, +30/-30 lines
* **Recent Focus**: Token count updates to 185k tokens, TS uninstaller porting and uninstall.sh creation with OneCLI agent cleanup, host-side authorization gate for confined group create_agent, alignment of README and CONTRIBUTING with registry-branch install instructions, and version bumping.

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
