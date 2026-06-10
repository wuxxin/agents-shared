# Active AI Assistants: Weekly Development Activity

This document tracks repository activity, commit counts, merge frequency, and release cycles for active assistant projects.

---

### 📊 Summary of Weekly Activity (June 03, 2026 – June 10, 2026)

#### Repository Overview & Package Status
| Assistant Repo | Stars | Forks | Main Branch | Last Commit | Installed Pkg | Commits Since Pkg | Status |
| :--- | :---: | :---: | :---: | :---: | :--- | :---: | :---: |
| **ironclaw** | 12,436 | 1,449 | `main` | 2026-06-10 | `ironclaw-git` @ `ironclaw.v0.29.1.r1256.g4c185e6-1` | 27 | **Highly Active** |
| **librefang** | 288 | 55 | `main` | 2026-06-10 | `librefang-git` @ `2026.5.31beta.16.r44.g648356c92-1` | 29 | **Active** |
| **zeroclaw** | 31,853 | 4,713 | `master` | 2026-06-10 | `zeroclaw-git` @ `0.8.0.beta.2.r125.g5eb5eba08-1` | 2 | **Highly Active** |
| **moltis** | 2,733 | 321 | `main` | 2026-06-05 | `moltis-git` @ `20260603.01.r8.g48c9a4192-1` | 0 | **Active** |
| **hermes-agent** | 189,354 | 32,703 | `main` | 2026-06-10 | — | — | **Highly Active** |
| **nanobot** | 43,986 | 7,793 | `main` | 2026-06-10 | — | — | **Active** |
| **picoclaw** | 29,342 | 4,206 | `main` | 2026-06-09 | `picoclaw-git` @ `0.2.9.nightly.20260609.46b29a0a-1` | 2 | **Active** |
| **nanoclaw** | 29,780 | 12,923 | `main` | 2026-06-10 | — | — | **Active** |

#### Weekly Activity Metrics (Human vs Bot)
| Assistant Repo | Commits / Week | Lines Added (Human/Bot) | Lines Deleted (Human/Bot) | Merges (Last Wk) | Releases/Tags (Last Wk) | Avg Commits/Wk (4 Wks) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **ironclaw** | **159** / 10 | 161.2k / 286 | 21.7k / 216 | 2 | 1 | 193.8 |
| **librefang** | **34** / 6 | 3.5k / 1.1k | 320 / 992 | 0 | 0 | 151.2 |
| **zeroclaw** | **116** / 0 | 29.9k / 0 | 4.7k / 0 | 0 | 0 | 84.0 |
| **moltis** | **9** / 2 | 3.1k / 53 | 291 / 10 | 0 | 1 | 30.2 |
| **hermes-agent** | **844** / 1 | 157.1k / 189 | 49.0k / 5 | 51 | 1 | 739.2 |
| **nanobot** | **79** / 1 | 27.3k / 315 | 3.8k / 11 | 0 | 0 | 101.8 |
| **picoclaw** | **44** / 2 | 1.7k / 21 | 308 / 21 | 40 | 0 | 34.2 |
| **nanoclaw** | **25** / 14 | 6.4k / 28 | 5.0k / 28 | 12 | 0 | 24.0 |

---

## 🔍 Repository Breakdown

> [!NOTE]
> The contributor lists and activity metrics for each repository below are compiled according to commits from the last 7 days.

### LibreFang (`librefang/librefang`)
* **Status**: Active (Total: 40 commits [34 H / 6 B], 0 releases in the last week). Lines added/deleted: +3.5k/-320 (Human), +1.1k/-992 (Bot). **29 commits since installed 2026.5.31beta.16 (r44.g648356c92).**
* **Contributors (according to last 7 days commits)** (Total: 4 Humans, 2 Bots):
  - **Top Humans**:
    - `Evan <suzukaze.haduki@gmail.com>` (Human): 27 commits, +2.0k/-182 lines
    - `Paco Navarrete <paco.j.navarrete@gmail.com>` (Human): 3 commits, +741/-49 lines
    - `Vignesh Jagadeesh <vignesh.nrfs@gmail.com>` (Human): 3 commits, +591/-51 lines
    - `Copilot <198982749+Copilot@users.noreply.github.com>` (Human): 1 commit, +72/-38 lines
  - **Top Bots**:
    - `dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>` (Bot): 5 commits, +1.1k/-985 lines
    - `github-actions[bot] <41898282+github-actions[bot]@users.noreply.github.com>` (Bot): 1 commit, +7/-7 lines
* **Note**: LibreFang is a community fork of the former `RightNow-AI/openfang` repository, which had **17,623 stars** and **2,252 forks** before going stale.
* **Recent Focus**: Security fixes including vault key-derivation Argon2 pinning, UTF-8-safe custom-event summaries/truncations, capping sidecar stderr reads to prevent OOM, resolving broadcast lag on permission bridges, blocking ClawHub zip install supply-chain audit bypass (.pth RCE), atomic/private updater script staging, validating workspace bind mounts and preventing path traversal, memory quota comparison fixes, cron fire metrics, non-headless Chrome startup stabilization under env isolation, and preventing TOML injection in generated agent manifests.

### ZeroClaw (`zeroclaw-labs/zeroclaw`)
* **Status**: Highly Active (Total: 116 commits [116 H / 0 B], 0 releases in the last week). Lines added/deleted: +29.9k/-4.7k (Human), +0/-0 (Bot). **2 commits since installed 0.8.0.beta.2 (r125.g5eb5eba08).**
* **Contributors (according to last 7 days commits)** (Total: 28 Humans, 0 Bots):
  - **Top Humans**:
    - `Shane Engelman <contact@shane.gg>` (Human): 26 commits, +15.2k/-2.1k lines
    - `Dan Gilles <dfgilles@uchicago.edu>` (Human): 19 commits, +4.2k/-953 lines
    - `Alix-007 <li.long15@xydigit.com>` (Human): 11 commits, +498/-71 lines
    - `Argenis De La Rosa <theonlyhennygod@gmail.com>` (Human): 9 commits, +2.8k/-111 lines
    - `Cherilyn Buren <88433283+NiuBlibing@users.noreply.github.com>` (Human): 6 commits, +742/-62 lines
    - `Tidux <jon@borg.moe>` (Human): 5 commits, +1.0k/-841 lines
    - `rifuki <rifuki.dev@gmail.com>` (Human): 5 commits, +508/-54 lines
    - `robinDU <drbparadise@gmail.com>` (Human): 5 commits, +387/-19 lines
    - `Jason Perlow <jperlow@gmail.com>` (Human): 4 commits, +1.3k/-30 lines
    - `JordanTheJet <morepencils@gmail.com>` (Human): 4 commits, +390/-43 lines
* **Recent Focus**: Zerocode context-window usage bar optimization; AMQP inbound channel with mutual TLS and deterministic SOP run execution; defining WASI WIT interfaces for Tool, Channel, and Memory plugins; LanguageTool grammar/style plugin addition; matrix session isolation and sync timeout prevention; stripping XML tool_result blocks from channel responses; trimming history guard against orphan-cascade; WebP image normalization for vision; and introducing sd-webui self-hosted image-gen plugin.

### Moltis (`moltis-org/moltis`)
* **Status**: Active (Total: 11 commits [9 H / 2 B], 1 release in the last week). Lines added/deleted: +3.1k/-291 (Human), +53/-10 (Bot). **0 commits since installed 20260603.01 (r8.g48c9a4192).**
* **Contributors (according to last 7 days commits)** (Total: 2 Humans, 1 Bots):
  - **Top Humans**:
    - `Fabien Penso <gpg@pen.so>` (Human): 8 commits, +1.3k/-60 lines
    - `Sergey Salamatov <55296341+s-salamatov@users.noreply.github.com>` (Human): 1 commit, +1.9k/-231 lines
  - **Top Bots**:
    - `github-actions[bot] <41898282+github-actions[bot]@users.noreply.github.com>` (Bot): 2 commits, +53/-10 lines
* **Recent Focus**: Telegram progress stream separation from final replies in Codex; presentation slide updates showing Polyphony in workflow; Fireworks Kimi final turn error handling; personal site additions to deck titles; expanding AI engineering and NFC Summit deck examples; fixing PDF presentation exports; and retrying transient ZAI catalog probes.

### IronClaw (`nearai/ironclaw`)
* **Status**: Highly Active (Total: 169 commits [159 H / 10 B], 1 release in the last week). Lines added/deleted: +161.2k/-21.7k (Human), +286/-216 (Bot). **27 commits since installed ironclaw.v0.29.1 (r1256.g4c185e6).**
* **Contributors (according to last 7 days commits)** (Total: 10 Humans, 1 Bots):
  - **Top Humans**:
    - `firat.sertgoz <firat.sertgoz@near.ai>` (Human): 81 commits, +61.7k/-9.3k lines
    - `Henry Park <henrypark133@gmail.com>` (Human): 33 commits, +41.1k/-5.5k lines
    - `Coffee <zjchen1234@foxmail.com>` (Human): 9 commits, +9.9k/-434 lines
    - `jinxin <106428113+italic-jinxin@users.noreply.github.com>` (Human): 9 commits, +14.2k/-2.7k lines
    - `Zaki Manian <zaki@iqlusion.io>` (Human): 9 commits, +18.3k/-2.6k lines
    - `Robert Yan <46699230+think-in-universe@users.noreply.github.com>` (Human): 8 commits, +8.6k/-787 lines
    - `Benjamin Kurrek <57506486+BenKurrek@users.noreply.github.com>` (Human): 3 commits, +565/-41 lines
    - `Illia Polosukhin <ilblackdragon@gmail.com>` (Human): 3 commits, +5.5k/-275 lines
    - `Daniel Wang <5139554+danielwpz@users.noreply.github.com>` (Human): 3 commits, +1.0k/-81 lines
    - `Josh Ford <thisisjoshford@gmail.com>` (Human): 1 commit, +200/-39 lines
  - **Top Bots**:
    - `IronClaw Agent <agent@ironclaw.com>` (Bot): 10 commits, +286/-216 lines
* **Recent Focus**: Reborn project deployment and runtime integration, including SSO operator WebUI auth, per-caller Reborn extension auth state, Docker migration copying and storage opt-ins, NEAR AI MCP web search tool alignment, production Postgres storage configuration wiring, readiness diagnostics contract definition, i18n localization token synchronization, Slack personal DM outbound targets, and Playwright E2E smoke test setup.

### Hermes Agent (`NousResearch/hermes-agent`)
* **Status**: Highly Active (Total: 845 commits [844 H / 1 B], 51 merges, 1 release in the last week). Lines added/deleted: +157.1k/-49.0k (Human), +189/-5 (Bot).
* **Contributors (according to last 7 days commits)** (Total: 137 Humans, 1 Bots):
  - **Top Humans**:
    - `Teknium <127238744+teknium1@users.noreply.github.com>` (Human): 188 commits, +30.2k/-12.9k lines
    - `Brooklyn Nicholson <brooklyn.bb.nicholson@gmail.com>` (Human): 108 commits, +17.1k/-6.3k lines
    - `teknium1 <127238744+teknium1@users.noreply.github.com>` (Human): 98 commits, +20.4k/-14.1k lines
    - `brooklyn! <brooklyn.bb.nicholson@gmail.com>` (Human): 35 commits, +9.0k/-3.0k lines
    - `Ben Barclay <ben@nousresearch.com>` (Human): 24 commits, +3.1k/-136 lines
    - `kshitijk4poor <82637225+kshitijk4poor@users.noreply.github.com>` (Human): 23 commits, +2.1k/-394 lines
    - `xxxigm <tuancanhnguyen706@gmail.com>` (Human): 22 commits, +1.4k/-59 lines
    - `Ben <ben@nousresearch.com>` (Human): 18 commits, +6.6k/-546 lines
    - `underthestars-zhy <zhuhaoyu0909@icloud.com>` (Human): 17 commits, +4.4k/-1.5k lines
    - `helix4u <4317663+helix4u@users.noreply.github.com>` (Human): 15 commits, +1.3k/-148 lines
  - **Top Bots**:
    - `Sol Aitken <solaiagent@gmail.com>` (Bot): 1 commit, +189/-5 lines
* **Recent Focus**: Adding Gemini audio tag rewrite and persona prompt files; voice-reply suffix assertions; fixing memory/skills write-approval inline prompt and gateway staging; self-healing venvs left half-built by interrupted installations; routing reasoning_effort to verbosity for adaptive Anthropic models; Slack approval UX block-size overflow corrections in threads; desktop titlebar user bubble fixes; live per-source progress for browsing skills; and requiring confirmations for expensive model selections.

### NanoBot (`HKUDS/nanobot`)
* **Status**: Active (Total: 80 commits [79 H / 1 B], 0 releases in the last week). Lines added/deleted: +27.3k/-3.8k (Human), +315/-11 (Bot).
* **Contributors (according to last 7 days commits)** (Total: 22 Humans, 1 Bots):
  - **Top Humans**:
    - `Xubin Ren <52506698+Re-bin@users.noreply.github.com>` (Human): 20 commits, +14.6k/-2.4k lines
    - `chengyongru <chengyongru.ai@gmail.com>` (Human): 19 commits, +2.7k/-409 lines
    - `Flávio Veloso Soares <flaviovs@magnux.com>` (Human): 7 commits, +720/-82 lines
    - `axelray-dev <110029405+axelray-dev@users.noreply.github.com>` (Human): 7 commits, +452/-10 lines
    - `chengyongru <2755839590@qq.com>` (Human): 4 commits, +206/-12 lines
    - `Kunal Karmakar <kkdthunlshd@gmail.com>` (Human): 4 commits, +420/-34 lines
    - `04cb <0x04cb@gmail.com>` (Human): 2 commits, +50/-1 lines
    - `chengyongru <61816729+chengyongru@users.noreply.github.com>` (Human): 2 commits, +4.2k/-583 lines
    - `Syoc <Syoc@users.noreply.github.com>` (Human): 1 commit, +1/-1 lines
    - `Moran <moranfong@gmail.com>` (Human): 1 commit, +153/-1 lines
  - **Top Bots**:
    - `NanoBot <nanobot@local>` (Bot): 1 commit, +315/-11 lines
* **Recent Focus**: WebUI chat history forking (fork-from-here, fork boundary visibility and metadata persistence); websocket stream end text logic; adding Bocha and Exa web search providers; setting HOME inside bwrap sandbox; adding StepFun ASR SSE transcription provider and endpoint normalization; max-iteration turn finalization without tools; max_completion_tokens handling for gpt-5/o-series; and email postActionExpunge configuration option to gate broad IMAP expunges.

### PicoClaw (`sipeed/picoclaw`)
* **Status**: Active (Total: 46 commits [44 H / 2 B], 40 merges, 0 releases in the last week). Lines added/deleted: +1.7k/-308 (Human), +21/-21 (Bot). **2 commits since installed 0.2.9.nightly.20260609.46b29a0a-1.**
* **Contributors (according to last 7 days commits)** (Total: 9 Humans, 1 Bots):
  - **Top Humans**:
    - `程智超0668000959 <cheng.zhichao@xydigit.com>` (Human): 35 commits, +741/-234 lines
    - `Mauro <afjcjsbx@gmail.com>` (Human): 2 commits, +9/-9 lines
    - `Guoguo <i@qwq.trade>` (Human): 1 commit, +0/-0 lines
    - `pancake <pancake@nopcode.org>` (Human): 1 commit, +5/-0 lines
    - `2023478 <2694762037@qq.com>` (Human): 1 commit, +43/-0 lines
    - `jp39 <jp39@gmx.com>` (Human): 1 commit, +675/-13 lines
    - `Sutra Hsing <sutrahsing@163.com>` (Human): 1 commit, +39/-1 lines
    - `Jay Shen <shenjiecode@gmail.com>` (Human): 1 commit, +38/-51 lines
    - `SebastianBoehler <27767932+SebastianBoehler@users.noreply.github.com>` (Human): 1 commit, +110/-0 lines
  - **Top Bots**:
    - `dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>` (Bot): 2 commits, +21/-21 lines
* **Recent Focus**: Systematic integration of ok checks for type assertions across subagent, spawn, context, model probe, and configuration modules; replacing log/fmt printing with structured logging; using %w for error wrapping; handling os.Getwd errors in context builder, skills recall, and drafts; handling Telegram location messages; adding native Kagi web search provider; checking Close() errors after files copy/download; and resolving a health check bug always returning not ready.

### NanoClaw (`nanocoai/nanoclaw`)
* **Status**: Active (Total: 39 commits [25 H / 14 B], 12 merges, 0 releases in the last week). Lines added/deleted: +6.4k/-5.0k (Human), +28/-28 (Bot). **Not installed as system package.**
* **Contributors (according to last 7 days commits)** (Total: 3 Humans, 1 Bots):
  - **Top Humans**:
    - `gavrielc <gabicohen22@yahoo.com>` (Human): 23 commits, +6.2k/-5.0k lines
    - `Omri Maya <omri@nanoco.ai>` (Human): 1 commit, +157/-2 lines
    - `markbala <22162779+markbala@users.noreply.github.com>` (Human): 1 commit, +74/-0 lines
  - **Top Bots**:
    - `github-actions[bot] <github-actions[bot]@users.noreply.github.com>` (Bot): 14 commits, +28/-28 lines
* **Recent Focus**: Aligning CONTRIBUTING and README with the registry-branch install model; security enhancements including host-side authorization for create_agent in confined groups and opt-in egress lockdown limiting agent egress to OneCLI; filtering cache-busting hashes for Ollama prompt caching; v2 rewrite for use-native-credential-proxy, add-ollama-tool, and migrate-from-openclaw skills; and conformance cleanups for MCP-tool capabilities, providers, and channel families.

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
