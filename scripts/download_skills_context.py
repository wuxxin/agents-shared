#!/usr/bin/env python3
"""
Download skills from an open-source agent repository and concatenate them
into a single context file of around 44,000 to 45,000 tokens.
"""

import os
import sys
import shutil
import subprocess
import argparse
from typing import List, Tuple
import tiktoken

# ==============================================================================
# DEFAULT CONFIGURATION
# Modify these values to change the default behavior, or use CLI flags.
# ==============================================================================
# Repository URL containing the skills to download.
# Alternative repositories:
# - Zeroclaw: "https://github.com/zeroclaw-labs/zeroclaw.git"
DEFAULT_REPO = "https://github.com/NousResearch/hermes-agent.git"

# Pinned commit hash ensures stability across upstream changes.
# Update this hash if you want to pull a different version of the repo.
DEFAULT_COMMIT = "a91b1c8b318ed56cda41d9043b237144facc0e96"

DEFAULT_TARGET_TOKENS = 44500
DEFAULT_TOLERANCE = 500
DEFAULT_ENCODING = "cl100k_base"
# ==============================================================================


def setup_temp_repo(repo_url: str, commit_hash: str, temp_dir: str) -> None:
    """
    Shallow clones or fetches a specific commit from the repository
    into a temporary directory under scratch/.
    """
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir, ignore_errors=True)
    os.makedirs(temp_dir, exist_ok=True)

    try:
        # Initialize an empty git repo
        subprocess.run(
            ["git", "init"], cwd=temp_dir, check=True, stdout=subprocess.DEVNULL
        )

        # Add the remote origin
        subprocess.run(
            ["git", "remote", "add", "origin", repo_url],
            cwd=temp_dir,
            check=True,
            stdout=subprocess.DEVNULL,
        )

        # Fetch the specific commit directly
        print(f"Fetching commit {commit_hash} from {repo_url}...")
        fetch_res = subprocess.run(
            ["git", "fetch", "--depth", "1", "origin", commit_hash],
            cwd=temp_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )

        if fetch_res.returncode != 0:
            # If fetching specific commit directly fails (e.g. server doesn't allow it),
            # fall back to fetching the default branch and checking out
            print(
                "Direct commit fetch failed or not supported. Falling back to fetching main branch..."
            )
            subprocess.run(
                ["git", "fetch", "--depth", "50", "origin"],
                cwd=temp_dir,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

        # Checkout the commit
        subprocess.run(
            ["git", "checkout", commit_hash],
            cwd=temp_dir,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print(f"Successfully checked out commit {commit_hash}.")

    except subprocess.CalledProcessError as e:
        print(f"Git command failed during setup: {e}", file=sys.stderr)
        cleanup_temp_repo(temp_dir)
        raise RuntimeError("Failed to clone/fetch repository.") from e


def cleanup_temp_repo(temp_dir: str) -> None:
    """
    Cleans up the temporary repository directory.
    """
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir, ignore_errors=True)


def find_skill_files(repo_dir: str) -> List[str]:
    """
    Recursively scans the repository directory to find all 'SKILL.md' files.
    If none are found, it falls back to finding any '.md' files in folders named 'skills'.
    """
    skill_files: List[str] = []
    for root, _, files in os.walk(repo_dir):
        for file in files:
            if file == "SKILL.md":
                skill_files.append(os.path.join(root, file))

    if not skill_files:
        # Fallback for other repositories (e.g., those without SKILL.md but having markdown skills)
        for root, _, files in os.walk(repo_dir):
            parts = root.split(os.sep)
            if "skills" in parts or ".claude" in parts:
                for file in files:
                    if file.endswith(".md"):
                        skill_files.append(os.path.join(root, file))

    return sorted(skill_files)


def count_tokens(content: str, encoding_name: str) -> int:
    """
    Counts the number of tokens in a string using tiktoken.
    """
    try:
        encoding = tiktoken.get_encoding(encoding_name)
        return len(encoding.encode(content, disallowed_special=()))
    except Exception as e:
        print(f"Error during token counting: {e}", file=sys.stderr)
        # Fallback to a rough approximation (approx 4 chars per token)
        return len(content) // 4


def select_skills(
    skills_data: List[Tuple[str, str, int]], target: int, tolerance: int
) -> List[Tuple[str, str, int]]:
    """
    Selects a subset of skills whose combined token count is within
    [target - tolerance, target + tolerance].
    Uses a greedy/knapsack approximation.
    """
    total_available_tokens = sum(tokens for _, _, tokens in skills_data)
    if total_available_tokens < target - tolerance:
        print(
            f"Warning: Total available tokens ({total_available_tokens}) is less than "
            f"the target minimum ({target - tolerance}). Selecting all available skills.",
            file=sys.stderr,
        )
        return skills_data

    # First attempt: greedy packing in alphabetical order
    selected: List[Tuple[str, str, int]] = []
    current_tokens = 0
    for path, content, tokens in skills_data:
        if current_tokens + tokens <= target + tolerance:
            selected.append((path, content, tokens))
            current_tokens += tokens
        if target - tolerance <= current_tokens <= target + tolerance:
            return selected

    # Second attempt: sort descending by size to pack larger files first, then smaller files
    selected = []
    current_tokens = 0
    sorted_skills = sorted(skills_data, key=lambda x: x[2], reverse=True)
    for path, content, tokens in sorted_skills:
        if current_tokens + tokens <= target + tolerance:
            selected.append((path, content, tokens))
            current_tokens += tokens
        if target - tolerance <= current_tokens <= target + tolerance:
            # Sort the final selected files alphabetically by path for consistency
            return sorted(selected, key=lambda x: x[0])

    # Fallback: if we still haven't landed in the range, just return whatever we have
    return selected


def main() -> None:
    """
    Main execution logic for the skills download and concatenation script.
    """
    parser = argparse.ArgumentParser(
        description="Download skills and concatenate them to a target token limit."
    )
    parser.add_argument(
        "--repo",
        type=str,
        default=DEFAULT_REPO,
        help=f"Git repository URL to download skills from (default: {DEFAULT_REPO})",
    )
    parser.add_argument(
        "--commit",
        type=str,
        default=DEFAULT_COMMIT,
        help=f"Pinned commit hash to checkout (default: {DEFAULT_COMMIT})",
    )
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="Path where the concatenated benchmark context file should be written",
    )
    parser.add_argument(
        "--target-tokens",
        type=int,
        default=DEFAULT_TARGET_TOKENS,
        help=f"Target token count (default: {DEFAULT_TARGET_TOKENS})",
    )
    parser.add_argument(
        "--tolerance",
        type=int,
        default=DEFAULT_TOLERANCE,
        help=f"Tolerance window around target token count (default: {DEFAULT_TOLERANCE})",
    )
    parser.add_argument(
        "--encoding",
        type=str,
        default=DEFAULT_ENCODING,
        help=f"Tiktoken encoding name (default: {DEFAULT_ENCODING})",
    )

    args = parser.parse_args()

    # Determine absolute paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_root = os.path.dirname(script_dir)
    scratch_dir = os.path.join(workspace_root, "scratch")
    temp_dir = os.path.join(scratch_dir, "tmp_skills_clone")

    try:
        # Clone/fetch repository
        setup_temp_repo(args.repo, args.commit, temp_dir)

        # Discover skill files
        skill_files = find_skill_files(temp_dir)
        if not skill_files:
            print(
                "Error: No skill files discovered in the checked out repository.",
                file=sys.stderr,
            )
            sys.exit(1)

        print(f"Discovered {len(skill_files)} skill files. Counting tokens...")

        # Load and count tokens for each skill file
        skills_data: List[Tuple[str, str, int]] = []
        for file_path in skill_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                tokens = count_tokens(content, args.encoding)
                skills_data.append((file_path, content, tokens))
            except Exception as e:
                print(f"Warning: Failed to read {file_path}: {e}", file=sys.stderr)

        # Select a subset of skills to hit the target token range
        selected_skills = select_skills(skills_data, args.target_tokens, args.tolerance)
        selected_token_sum = sum(tokens for _, _, tokens in selected_skills)

        print(
            f"Selected {len(selected_skills)} skills with total token count: {selected_token_sum}"
        )

        # Ensure output directory exists
        output_dir = os.path.dirname(os.path.abspath(args.output))
        os.makedirs(output_dir, exist_ok=True)

        # Concatenate selected skills
        concatenated_content = (
            "\n\n".join(content.strip() for _, content, _ in selected_skills) + "\n"
        )

        # Write to file
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(concatenated_content)

        print(f"Successfully generated skill context file at: {args.output}")

    finally:
        # Always clean up clone files
        cleanup_temp_repo(temp_dir)


if __name__ == "__main__":
    main()
