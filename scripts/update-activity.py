#!/usr/bin/env python3
"""update-activity.py

A script to automate gathering statistics and recent git history for AI Assistants.
This script checks local pacman installations, fetches upstream repository
updates under scratch/, queries GitHub metrics, compiles activity tables,
and can optionally write them directly to research/weekly-devel-activity.md.
"""

import datetime
import json
import os
import re
import subprocess
import sys
import urllib.request
from typing import Any, Dict, List, Optional

# Define the repositories to track
TRACKED_REPOS = [
    {
        "name": "ironclaw",
        "github": "nearai/ironclaw",
        "pkg": "ironclaw-git",
        "branch": "main",
        "heading": "IronClaw",
    },
    {
        "name": "zeroclaw",
        "github": "zeroclaw-labs/zeroclaw",
        "pkg": "zeroclaw-git",
        "branch": "master",
        "heading": "ZeroClaw",
    },
    {
        "name": "hermes-agent",
        "github": "NousResearch/hermes-agent",
        "pkg": "",
        "branch": "main",
        "heading": "Hermes Agent",
    },
    {
        "name": "nanobot",
        "github": "HKUDS/nanobot",
        "pkg": "",
        "branch": "main",
        "heading": "NanoBot",
    },
    {
        "name": "picoclaw",
        "github": "sipeed/picoclaw",
        "pkg": "picoclaw-git",
        "branch": "main",
        "heading": "PicoClaw",
    },
    {
        "name": "nanoclaw",
        "github": "nanocoai/nanoclaw",
        "pkg": "nanoclaw-git",
        "branch": "main",
        "heading": "NanoClaw",
    },
    {
        "name": "librefang",
        "github": "librefang/librefang",
        "pkg": "librefang-git",
        "branch": "main",
        "heading": "LibreFang",
    },
]


def run_cmd(cmd: List[str], cwd: Optional[str] = None) -> str:
    """Run a shell command and return its stdout as a string."""
    try:
        res = subprocess.run(
            cmd,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        return res.stdout.strip()
    except subprocess.CalledProcessError:
        return ""


def get_git_installed_ref(pkg: str) -> str:
    """Resolve the git ref of the currently installed package."""
    if not pkg:
        return ""
    pkg_ver = run_cmd(["pacman", "-Q", pkg])
    if not pkg_ver:
        return ""
    # Extract suffix after ".g" or "-g" followed by hex characters
    ver_part = pkg_ver.split()[-1]
    # Check format <tag>.rN.g<hash>
    match = re.search(r"\.g([0-9a-f]{7,})(-.*)?$", ver_part)
    if match:
        return match.group(1)
    # Check format r<revcount>.<hash>
    match = re.search(r"r[0-9]+\.([0-9a-f]{7,})(-.*)?$", ver_part)
    if match:
        return match.group(1)
    # Check format <tag>.nightly.<date>.<hash>
    match = re.search(r"nightly\.[0-9]+\.([0-9a-f]{7,})(-.*)?$", ver_part)
    if match:
        return match.group(1)
    # Release package: strip pkgrel suffix
    rel_part = re.sub(r"-[0-9]+$", "", ver_part)
    return f"v{rel_part}"


def query_github_api(repo_slug: str) -> Dict[str, int]:
    """Query GitHub API for stargazers and forks counts."""
    url = f"https://api.github.com/repos/{repo_slug}"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (AI Assistant weekly report generator)",
            "Accept": "application/vnd.github+json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
            return {
                "stars": data.get("stargazers_count", 0),
                "forks": data.get("forks_count", 0),
            }
    except Exception:
        # Fallback to zeros if offline or rate-limited
        return {"stars": 0, "forks": 0}


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


def get_repo_stats(repo_name: str, pkg: str, branch: str) -> Dict[str, Any]:
    """Retrieve commits, merges, line stats, tags, and installed packages."""
    full_path = os.path.join("scratch", repo_name)
    if not os.path.exists(full_path):
        return {}

    # Fetch latest updates
    run_cmd(["git", "fetch", "origin"], cwd=full_path)
    run_cmd(["git", "checkout", branch], cwd=full_path)
    run_cmd(["git", "reset", "--hard", f"origin/{branch}"], cwd=full_path)

    # Commits and lines added/deleted
    human_commits = 0
    bot_commits = 0
    human_added = 0
    human_deleted = 0
    bot_added = 0
    bot_deleted = 0
    contributors = {}

    try:
        # Run git log with numstat
        log_output = run_cmd(
            [
                "git",
                "log",
                "--since=7 days ago",
                "--no-merges",
                "--numstat",
                "--pretty=format:AUTHOR: %an <%ae>",
            ],
            cwd=full_path,
        )

        current_author = None
        current_author_is_bot = False
        for line in log_output.splitlines():
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
        print(f"Error parsing commits for {repo_name}: {e}")

    # Merges
    merges = 0
    merges_out = run_cmd(
        ["git", "log", "--since=7 days ago", "--merges", "--oneline"],
        cwd=full_path,
    )
    if merges_out:
        merges = len(merges_out.strip().splitlines())

    # Last Commit Date
    last_commit = "N/A"
    last_commit_out = run_cmd(
        ["git", "log", "-1", "--format=%ad", "--date=short"],
        cwd=full_path,
    )
    if last_commit_out:
        last_commit = last_commit_out.strip()

    # Avg Commits (4 weeks)
    avg_commits = 0.0
    commits_28_out = run_cmd(
        ["git", "log", "--since=28 days ago", "--no-merges", "--oneline"],
        cwd=full_path,
    )
    if commits_28_out:
        avg_commits = len(commits_28_out.strip().splitlines()) / 4.0

    # Tags
    tags = []
    tags_out = run_cmd(
        [
            "git",
            "log",
            "--tags",
            "--since=7 days ago",
            "--simplify-by-decoration",
            "--pretty=format:%d %as",
        ],
        cwd=full_path,
    )
    for line in tags_out.splitlines():
        line = line.strip()
        if line:
            tags.append(line)

    # Installed package version and commits since installed
    installed_ver = "—"
    installed_ref = ""
    since_commits = "—"
    if pkg:
        pkg_ver_str = run_cmd(["pacman", "-Q", pkg])
        if pkg_ver_str:
            installed_ver = pkg_ver_str.split()[-1]
            installed_ref = get_git_installed_ref(pkg)
            if installed_ref:
                since_commits_out = run_cmd(
                    [
                        "git",
                        "log",
                        "--no-merges",
                        "--oneline",
                        f"{installed_ref}..HEAD",
                    ],
                    cwd=full_path,
                )
                if since_commits_out:
                    since_commits = str(len(since_commits_out.strip().splitlines()))
                else:
                    since_commits = "0"

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
        "tags": tags,
        "contributors": contributors,
        "installed_ver": installed_ver,
        "installed_ref": installed_ref,
        "since_commits": since_commits,
    }


def make_status_line(stats: Dict[str, Any]) -> str:
    """Format the Status line for assistant breakdown."""
    commits = stats["commits"]
    status = "Stale"
    if commits > 50:
        status = "Highly Active"
    elif commits > 0:
        status = "Active"

    tag_count = len(stats["tags"])
    tag_word = "tag/release" if tag_count == 1 else "tags/releases"
    tag_phrase = f"{tag_count} {tag_word} in the last week"

    pkg_phrase = ""
    if stats.get("installed_ver") and stats["installed_ver"] != "—":
        ref_suffix = (
            f" (ref={stats['installed_ref']})" if stats["installed_ref"] else ""
        )
        pkg_phrase = f" **{stats['since_commits']} commits since installed {stats['installed_ver']}{ref_suffix}.**"

    return (
        f"* **Status**: {status} (Total: {commits} commits [{stats['human_commits']} H / {stats['bot_commits']} B], "
        f"{tag_phrase}). Lines added/deleted: +{format_lines(stats['human_added'])}/-{format_lines(stats['human_deleted'])} (Human), "
        f"+{format_lines(stats['bot_added'])}/-{format_lines(stats['bot_deleted'])} (Bot).{pkg_phrase}"
    )


def make_contributors_block(stats: Dict[str, Any]) -> str:
    """Format the Contributors list block."""
    contributors = stats["contributors"]
    humans = [item for item in contributors.items() if not item[1]["is_bot"]]
    bots = [item for item in contributors.items() if item[1]["is_bot"]]

    humans_sorted = sorted(humans, key=lambda x: x[1]["commits"], reverse=True)
    bots_sorted = sorted(bots, key=lambda x: x[1]["commits"], reverse=True)

    lines = []
    lines.append(
        f"* **Contributors (according to last 7 days commits)** (Total: {len(humans)} Humans, {len(bots)} Bots):"
    )
    if humans_sorted:
        lines.append("  - **Top Humans**:")
        for name, info in humans_sorted[:10]:
            lines.append(
                f"    - `{name}` (Human): {info['commits']} commits, +{format_lines(info['added'])}/-{format_lines(info['deleted'])} lines"
            )
    if bots_sorted:
        lines.append("  - **Top Bots**:")
        for name, info in bots_sorted[:3]:
            lines.append(
                f"    - `{name}` (Bot): {info['commits']} commits, +{format_lines(info['added'])}/-{format_lines(info['deleted'])} lines"
            )

    return "\n".join(lines)


def update_assistant_section(
    content: str, name_heading: str, stats: Dict[str, Any]
) -> str:
    """Locate and update status and contributor lists for an assistant section in content."""
    # Find the heading block starting with "### Name (" up to next heading or end of file
    pattern = re.compile(
        rf"(^### {re.escape(name_heading)} \(.*?\n)(.*?)(?=\n### |\n## |\n--- |\Z)",
        re.MULTILINE | re.DOTALL,
    )

    match = pattern.search(content)
    if not match:
        return content

    header_line = match.group(1)
    old_section_block = match.group(2)

    # Extract Recent Focus
    recent_focus = ""
    focus_match = re.search(
        r"(\* \*\*Recent Focus\*\*:.*)", old_section_block, re.DOTALL
    )
    if focus_match:
        recent_focus = focus_match.group(1).strip()

    # Extract Note (if any)
    note = ""
    note_match = re.search(r"(\* \*\*Note\*\*:.*)", old_section_block)
    if note_match:
        note_text = note_match.group(1).strip()
        if "* **Recent Focus**:" in note_text:
            note_text = note_text.split("* **Recent Focus**:")[0].strip()
        note = note_text

    # Rebuild body
    status_line = make_status_line(stats)
    contributors_block = make_contributors_block(stats)

    new_parts = [status_line, contributors_block]
    if note:
        new_parts.append(note)
    if recent_focus:
        new_parts.append(recent_focus)

    new_body = "\n".join(new_parts)
    return content.replace(match.group(0), f"{header_line}{new_body}\n")


def compile_activity(write_to_file: bool = False) -> None:
    """Compile the weekly development activity report for active assistants."""
    print("Starting AI Assistant development activity report update...")
    start_date = (datetime.date.today() - datetime.timedelta(days=7)).strftime(
        "%B %d, %Y"
    )
    end_date = datetime.date.today().strftime("%B %d, %Y")
    print(f"Reporting Period: {start_date} - {end_date}")

    results = []
    for repo in TRACKED_REPOS:
        name = repo["name"]
        github = repo["github"]
        pkg = repo["pkg"]
        branch = repo["branch"]

        print(f"\nProcessing {name} ({github})...")
        stats = get_repo_stats(name, pkg, branch)
        if not stats:
            print(f"Warning: Could not gather stats for {name}")
            continue

        # Get GitHub stars & forks
        gh_metrics = query_github_api(github)
        stats["stars"] = gh_metrics["stars"]
        stats["forks"] = gh_metrics["forks"]
        stats["github"] = github
        stats["name"] = name
        stats["heading"] = repo["heading"]
        stats["pkg"] = pkg
        stats["branch"] = branch
        results.append(stats)

    # Format Overview Table
    overview_rows = [
        "#### Repository Overview & Package Status",
        "| Assistant Repo | Stars | Forks | Main Branch | Last Commit | Installed Pkg | Commits Since Pkg | Status |",
        "| :--- | :---: | :---: | :---: | :---: | :--- | :---: | :---: |",
    ]
    for r in results:
        status = "Stale"
        if r["commits"] > 50:
            status = "Highly Active"
        elif r["commits"] > 0:
            status = "Active"

        pkg_str = "—"
        if r["installed_ver"] != "—":
            pkg_str = f"`{r['pkg']}` @ `{r['installed_ver']}`"

        overview_rows.append(
            f"| **{r['name']}** | {r['stars']:,} | {r['forks']:,} | `{r['branch']}` | {r['last_commit']} | {pkg_str} | {r['since_commits']} | **{status}** |"
        )

    # Format Metrics Table
    metrics_rows = [
        "#### Weekly Activity Metrics (Human vs Bot)",
        "| Assistant Repo | Commits / Week | Lines Added (Human/Bot) | Lines Deleted (Human/Bot) | Merges (Last Wk) | Releases/Tags (Last Wk) | Avg Commits/Wk (4 Wks) |",
        "| :--- | :---: | :---: | :---: | :---: | :---: | :---: |",
    ]
    for r in results:
        commits_str = f"**{r['human_commits']}**" if r["human_commits"] > 0 else "0"
        lines_add_str = (
            f"{format_lines(r['human_added'])} / {format_lines(r['bot_added'])}"
        )
        lines_del_str = (
            f"{format_lines(r['human_deleted'])} / {format_lines(r['bot_deleted'])}"
        )
        metrics_rows.append(
            f"| **{r['name']}** | {commits_str} / {r['bot_commits']} | {lines_add_str} | {lines_del_str} | {r['merges']} | {len(r['tags'])} | {r['avg_commits']:.1f} |"
        )

    tables_block = "\n".join(overview_rows) + "\n\n" + "\n".join(metrics_rows)

    if write_to_file:
        file_path = "research/weekly-devel-activity.md"
        if not os.path.exists(file_path):
            print(f"Error: {file_path} not found in the current directory.")
            return

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Update date header
        header_pattern = r"(#### 📊 Summary of Last 7 Days Activity \()[^\)]+(\))"
        new_header = f"\\1{start_date} – {end_date}\\2"
        content = re.sub(header_pattern, new_header, content)

        # Update tables
        start_tag = "<!-- START_WEEKLY_ACTIVITY_TABLES -->"
        end_tag = "<!-- END_WEEKLY_ACTIVITY_TABLES -->"
        table_pattern = re.compile(
            rf"{re.escape(start_tag)}.*?{re.escape(end_tag)}", re.DOTALL
        )
        new_block = f"{start_tag}\n{tables_block}\n{end_tag}"
        content = re.sub(table_pattern, new_block, content)

        # Update breakdown sections
        for r in results:
            content = update_assistant_section(content, r["heading"], r)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"\nSuccessfully wrote updated activity report to {file_path}!")

    else:
        print("\n" + "=" * 40)
        print("Compiled Tables Output:")
        print("=" * 40)
        print(tables_block)

    # Print raw logs for focus areas
    print("\n" + "=" * 40)
    print("Recent Upstream Commit Logs (Last 7 Days):")
    print("=" * 40)
    for r in results:
        if r["commits"] == 0:
            continue
        print(f"\n### {r['name']} ({r['github']}) - {r['commits']} commits")
        log = run_cmd(
            [
                "git",
                "-C",
                f"scratch/{r['name']}",
                "log",
                "--since=7 days ago",
                "--no-merges",
                "--oneline",
                "-n",
                "15",
            ]
        )
        print(log)


if __name__ == "__main__":
    write_flag = "--write" in sys.argv or "-w" in sys.argv
    compile_activity(write_to_file=write_flag)
