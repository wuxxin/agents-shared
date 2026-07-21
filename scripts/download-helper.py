#!/usr/bin/env python3
"""
download-helper.py - Helper utility for local model downloads and processing.

Provides helper subcommands used during model acquisition:
  1. merge-mtp: Combine MTP auxiliary head tensors (block 40) into base GGUF models.
  2. benchmark-context: Download agent skills and build benchmark-context.md context file.

Usage:
  python3 download-helper.py merge-mtp <base_model.gguf> <mtp_tensors.gguf> <output_model_mtp.gguf>
  python3 download-helper.py benchmark-context --output <output_file.md> [options]
"""

import sys
import os
import shutil
import subprocess
import argparse
from typing import List, Tuple

try:
    import tiktoken
except ImportError:
    tiktoken = None

try:
    import numpy as np
    import gguf
except ImportError:
    np = None
    gguf = None


# ==============================================================================
# DEFAULT CONFIGURATION FOR BENCHMARK CONTEXT
# ==============================================================================
DEFAULT_REPO = "https://github.com/NousResearch/hermes-agent.git"
DEFAULT_COMMIT = "a91b1c8b318ed56cda41d9043b237144facc0e96"
DEFAULT_TARGET_TOKENS = 44500
DEFAULT_TOLERANCE = 500
DEFAULT_ENCODING = "cl100k_base"


def print_usage(exit_code: int = 1) -> None:
    usage_text = """download-helper.py - Unified helper utility for local model downloads

Usage:
  python3 download-helper.py <subcommand> [options]

Subcommands:
  merge-mtp <base_model.gguf> <mtp_tensors.gguf> <output_model_mtp.gguf>
    Merges MTP (Multi-Token Prediction) block 40 tensors and metadata into
    a base Qwen3.5/3.6 MoE GGUF model file.

    Positional syntax:
      download-helper.py merge-mtp <base.gguf> <mtp.gguf> <out_mtp.gguf>

    Flag syntax:
      download-helper.py merge-mtp --base <base.gguf> --mtp <mtp.gguf> --output <out_mtp.gguf>

  benchmark-context --output <output_file.md> [options]
    Downloads skill files from an agent repository and concatenates them
    into a benchmark context markdown file (~44.5k tokens).

    Options:
      --output <file>         Path to output benchmark context markdown file (required)
      --repo <url>            Git repository URL (default: https://github.com/NousResearch/hermes-agent.git)
      --commit <hash>         Pinned commit hash (default: a91b1c8b318ed56cda41d9043b237144facc0e96)
      --target-tokens <N>     Target token count (default: 44500)
      --tolerance <N>         Tolerance window around target token count (default: 500)
      --encoding <name>       Tiktoken encoding (default: cl100k_base)

Examples:
  python3 scripts/download-helper.py merge-mtp base.gguf mtp.gguf merged-mtp.gguf
  python3 scripts/download-helper.py benchmark-context --output /path/to/benchmark-context.md
"""
    print(usage_text, file=sys.stderr if exit_code != 0 else sys.stdout)
    sys.exit(exit_code)


# ==============================================================================
# MTP MERGING LOGIC
# ==============================================================================
def run_merge_mtp(base_path: str, mtp_path: str, out_path: str) -> None:
    if gguf is None or np is None:
        print(
            "Error: 'gguf' and 'numpy' Python packages are required for merge-mtp.",
            file=sys.stderr,
        )
        sys.exit(1)

    if not os.path.isfile(base_path):
        print(f"Error: Base model file not found: {base_path}", file=sys.stderr)
        sys.exit(1)
    if not os.path.isfile(mtp_path):
        print(f"Error: MTP model file not found: {mtp_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Loading base model: {base_path}")
    main_reader = gguf.GGUFReader(base_path)
    print(f"Loading MTP draft tensors: {mtp_path}")
    mtp_reader = gguf.GGUFReader(mtp_path)

    arch = "qwen35moe"
    if "general.architecture" in main_reader.fields:
        arch_field = main_reader.fields["general.architecture"]
        arch = arch_field.parts[-1].tobytes().decode("utf-8", errors="ignore")

    print(f"Creating merged GGUF writer for architecture '{arch}': {out_path}")
    writer = gguf.GGUFWriter(out_path, arch)

    mtp_override_keys = {"qwen35moe.block_count", "qwen35moe.nextn_predict_layers"}

    for key, field in main_reader.fields.items():
        if key.startswith("GGUF.") or key == "general.architecture":
            continue

        if key == "qwen35moe.block_count":
            original_blocks = int(np.frombuffer(field.parts[-1], dtype=np.uint32)[0])
            new_blocks = original_blocks + 1
            print(f"Updating {key}: {original_blocks} -> {new_blocks}")
            writer.add_uint32(key, new_blocks)
            continue

        if key in mtp_override_keys:
            continue

        val_type = field.types[0]
        val = field.parts[-1]

        if val_type == gguf.GGUFValueType.UINT32:
            writer.add_uint32(key, int(np.frombuffer(val, dtype=np.uint32)[0]))
        elif val_type == gguf.GGUFValueType.UINT64:
            writer.add_uint64(key, int(np.frombuffer(val, dtype=np.uint64)[0]))
        elif val_type == gguf.GGUFValueType.INT32:
            writer.add_int32(key, int(np.frombuffer(val, dtype=np.int32)[0]))
        elif val_type == gguf.GGUFValueType.FLOAT32:
            writer.add_float32(key, float(np.frombuffer(val, dtype=np.float32)[0]))
        elif val_type == gguf.GGUFValueType.STRING:
            writer.add_string(key, val.tobytes().decode("utf-8", errors="ignore"))
        elif val_type == gguf.GGUFValueType.ARRAY:
            elem_type = field.types[1]
            count = int(np.frombuffer(field.parts[4], dtype=np.uint64)[0])
            if elem_type == gguf.GGUFValueType.INT32:
                arr_parts = field.parts[5 : 5 + count]
                arr_val = [int(np.frombuffer(p, dtype=np.int32)[0]) for p in arr_parts]
                writer.add_array(key, arr_val)
            elif elem_type == gguf.GGUFValueType.FLOAT32:
                arr_parts = field.parts[5 : 5 + count]
                arr_val = [
                    float(np.frombuffer(p, dtype=np.float32)[0]) for p in arr_parts
                ]
                writer.add_array(key, arr_val)
            elif elem_type == gguf.GGUFValueType.STRING:
                arr_val = [field.parts[5 + i * 2 + 1].tobytes() for i in range(count)]
                writer.add_array(key, arr_val)
            else:
                print(
                    f"Warning: Unhandled array element type {elem_type} for key {key}",
                    file=sys.stderr,
                )

    for key, field in mtp_reader.fields.items():
        if key.startswith("GGUF."):
            continue
        val = field.parts[-1]
        val_type = field.types[0]
        if val_type == gguf.GGUFValueType.UINT32:
            val_int = int(np.frombuffer(val, dtype=np.uint32)[0])
            print(f"Adding MTP metadata {key} = {val_int}")
            writer.add_uint32(key, val_int)

    print(f"Copying {len(main_reader.tensors)} base model tensors...")
    for tensor in main_reader.tensors:
        writer.add_tensor(tensor.name, tensor.data, raw_dtype=tensor.tensor_type)

    print(f"Appending {len(mtp_reader.tensors)} MTP tensors...")
    for tensor in mtp_reader.tensors:
        writer.add_tensor(tensor.name, tensor.data, raw_dtype=tensor.tensor_type)

    print("Writing GGUF header and metadata...")
    writer.write_header_to_file()
    writer.write_kv_data_to_file()
    print("Writing tensor binary data...")
    writer.write_tensors_to_file()
    writer.close()
    print(f"Successfully merged GGUF model written to: {out_path}")


# ==============================================================================
# BENCHMARK CONTEXT LOGIC
# ==============================================================================
def setup_temp_repo(repo_url: str, commit_hash: str, temp_dir: str) -> None:
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir, ignore_errors=True)
    os.makedirs(temp_dir, exist_ok=True)

    try:
        subprocess.run(
            ["git", "init"], cwd=temp_dir, check=True, stdout=subprocess.DEVNULL
        )
        subprocess.run(
            ["git", "remote", "add", "origin", repo_url],
            cwd=temp_dir,
            check=True,
            stdout=subprocess.DEVNULL,
        )

        print(f"Fetching commit {commit_hash} from {repo_url}...")
        fetch_res = subprocess.run(
            ["git", "fetch", "--depth", "1", "origin", commit_hash],
            cwd=temp_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )

        if fetch_res.returncode != 0:
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
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir, ignore_errors=True)


def find_skill_files(repo_dir: str) -> List[str]:
    skill_files: List[str] = []
    for root, _, files in os.walk(repo_dir):
        for file in files:
            if file == "SKILL.md":
                skill_files.append(os.path.join(root, file))

    if not skill_files:
        for root, _, files in os.walk(repo_dir):
            parts = root.split(os.sep)
            if "skills" in parts or ".claude" in parts:
                for file in files:
                    if file.endswith(".md"):
                        skill_files.append(os.path.join(root, file))

    return sorted(skill_files)


def count_tokens(content: str, encoding_name: str) -> int:
    if tiktoken is not None:
        try:
            encoding = tiktoken.get_encoding(encoding_name)
            return len(encoding.encode(content, disallowed_special=()))
        except Exception as e:
            print(f"Error during token counting: {e}", file=sys.stderr)
    return len(content) // 4


def select_skills(
    skills_data: List[Tuple[str, str, int]], target: int, tolerance: int
) -> List[Tuple[str, str, int]]:
    total_available_tokens = sum(tokens for _, _, tokens in skills_data)
    if total_available_tokens < target - tolerance:
        print(
            f"Warning: Total available tokens ({total_available_tokens}) is less than "
            f"the target minimum ({target - tolerance}). Selecting all available skills.",
            file=sys.stderr,
        )
        return skills_data

    selected: List[Tuple[str, str, int]] = []
    current_tokens = 0
    for path, content, tokens in skills_data:
        if current_tokens + tokens <= target + tolerance:
            selected.append((path, content, tokens))
            current_tokens += tokens
        if target - tolerance <= current_tokens <= target + tolerance:
            return selected

    selected = []
    current_tokens = 0
    sorted_skills = sorted(skills_data, key=lambda x: x[2], reverse=True)
    for path, content, tokens in sorted_skills:
        if current_tokens + tokens <= target + tolerance:
            selected.append((path, content, tokens))
            current_tokens += tokens
        if target - tolerance <= current_tokens <= target + tolerance:
            return sorted(selected, key=lambda x: x[0])

    return selected


def run_benchmark_context(args: argparse.Namespace) -> None:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_root = os.path.dirname(script_dir)
    scratch_dir = os.path.join(workspace_root, "scratch")
    temp_dir = os.path.join(scratch_dir, "tmp_skills_clone")

    try:
        setup_temp_repo(args.repo, args.commit, temp_dir)
        skill_files = find_skill_files(temp_dir)
        if not skill_files:
            print(
                "Error: No skill files discovered in the checked out repository.",
                file=sys.stderr,
            )
            sys.exit(1)

        print(f"Discovered {len(skill_files)} skill files. Counting tokens...")

        skills_data: List[Tuple[str, str, int]] = []
        for file_path in skill_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                tokens = count_tokens(content, args.encoding)
                skills_data.append((file_path, content, tokens))
            except Exception as e:
                print(f"Warning: Failed to read {file_path}: {e}", file=sys.stderr)

        selected_skills = select_skills(skills_data, args.target_tokens, args.tolerance)
        selected_token_sum = sum(tokens for _, _, tokens in selected_skills)

        print(
            f"Selected {len(selected_skills)} skills with total token count: {selected_token_sum}"
        )

        output_dir = os.path.dirname(os.path.abspath(args.output))
        os.makedirs(output_dir, exist_ok=True)

        concatenated_content = (
            "\n\n".join(content.strip() for _, content, _ in selected_skills) + "\n"
        )

        with open(args.output, "w", encoding="utf-8") as f:
            f.write(concatenated_content)

        print(f"Successfully generated skill context file at: {args.output}")

    finally:
        cleanup_temp_repo(temp_dir)


# ==============================================================================
# MAIN ENTRYPOINT
# ==============================================================================
def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help", "help"):
        print_usage(
            exit_code=0 if len(sys.argv) >= 2 and sys.argv[1] in ("-h", "--help") else 1
        )

    subcommand = sys.argv[1]

    if subcommand == "merge-mtp":
        # Check positional vs flag args
        if len(sys.argv) == 5 and not sys.argv[2].startswith("-"):
            base_path = sys.argv[2]
            mtp_path = sys.argv[3]
            out_path = sys.argv[4]
        else:
            parser = argparse.ArgumentParser(
                prog="download-helper.py merge-mtp",
                description="Merge MTP tensors into GGUF model.",
            )
            parser.add_argument("--base", required=True, help="Base GGUF model path")
            parser.add_argument("--mtp", required=True, help="MTP GGUF model path")
            parser.add_argument(
                "--output", required=True, help="Output merged GGUF model path"
            )
            parsed_args = parser.parse_args(sys.argv[2:])
            base_path = parsed_args.base
            mtp_path = parsed_args.mtp
            out_path = parsed_args.output

        run_merge_mtp(base_path, mtp_path, out_path)

    elif subcommand in ("benchmark-context", "build-context"):
        parser = argparse.ArgumentParser(
            prog=f"download-helper.py {subcommand}",
            description="Download skills and concatenate them to a target token limit.",
        )
        parser.add_argument(
            "--output",
            type=str,
            required=True,
            help="Path where the concatenated benchmark context file should be written",
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
        parsed_args = parser.parse_args(sys.argv[2:])
        run_benchmark_context(parsed_args)

    else:
        print(f"Error: Unknown subcommand '{subcommand}'\n", file=sys.stderr)
        print_usage(exit_code=1)


if __name__ == "__main__":
    main()
