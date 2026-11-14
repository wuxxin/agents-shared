#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
target_dir=""
download_all=false
download_llm=false
download_embedding=false
download_reranker=false
download_stt=false
download_tts=false
download_image=false
download_completion=false
download_benchmark=false
download_projections=false
download_strata=false
download_strata_shards=false
download_strata_aux=false
download_dspark=false
# Wrapper for hf to catch click.exceptions.Exit on python 3.14
hf() {
    python3 -c '
import sys
import click
from huggingface_hub.cli.hf import main
try:
    sys.exit(main())
except click.exceptions.Exit as e:
    sys.exit(e.exit_code)
except SystemExit as e:
    sys.exit(e.code)
' "$@"
}

# Print help message
show_help() {
    cat <<EOF
Usage: $(basename "$0") <target_model_dir> [options]

Downloads local AI models and benchmark context for models into standard subdirectories:
  - <target_model_dir>/text
  - <target_model_dir>/vision-text
  - <target_model_dir>/embedding
  - <target_model_dir>/reranker
  - <target_model_dir>/speech-to-text
  - <target_model_dir>/text-to-speech
  - <target_model_dir>/image
  - <target_model_dir>/strata/projections
  - <target_model_dir>/benchmark-context.md
Options:
  --all             Download all models and build the benchmark context
  --llm             Download the LLM model, vision projector, and chat template
  --embedding       Download the text embedding model
  --reranker        Download the reranker model (with working classification head)
  --speech-to-text  Download the Speech-to-Text (Whisper) model
  --text-to-speech, --tts Download the Text-to-Speech (Qwen3-TTS) models
  --image           Download the image generation (Z-Image-Turbo) models
  --completion      Download the completions model (qwen-coder-fim) and testdata
  --benchmark-context, --benchmark Build the benchmark-context.md file using downloaded skills
  --strata          Download both Strata Qwen3.8-Flash-Next model shards and all auxiliary runtime files
  --strata-shards, --strata-model Download only the massive Strata model shards (~84 GB)
  --strata-additional, --strata-aux Download all Strata auxiliary files (vision, MTP, DSpark, projections, chat template, tokenizer runtime) without huge shards
  --projections, --strata-projections Download all Strata experimental speed projection and control vector files
  --dspark          Download the Qwen3.8-Flash-Next DSpark speculative drafter
  -h, --help        Show this help message and exit

Examples:
  $(basename "$0") /data/public/machine-learning/models --all
  $(basename "$0") ./my-models --llm --embedding
EOF
}

ensure_real_dir() {
    local dir="$1"
    if [[ -L "$dir" ]]; then
        local resolved
        resolved="$(readlink -f "$dir" || true)"
        if [[ -z "$resolved" || ! -d "$resolved" || ! -w "$resolved" ]]; then
            rm -f "$dir"
        fi
    fi
    mkdir -p "$dir"
}

acquire_file() {
    local _cache_subpath="$1"
    local download_url="$2"
    local target_path="$3"
    local target_subdir
    target_subdir="$(dirname "$target_path")"

    ensure_real_dir "$target_subdir"

    # Skip if exists and is non-empty (follows valid symlinks)
    if [[ -s "$target_path" ]]; then
        echo "File already exists and is non-empty: $target_path (Skipping)"
        return 0
    fi

    # Never write through a dangling or empty symlink
    if [[ -L "$target_path" ]]; then
        rm -f "$target_path"
    fi

    # Download from URL
    echo "Acquiring from remote: $download_url"

    # Clean URL (strip query parameters and hash fragments)
    local clean_url="${download_url%%\?*}"
    clean_url="${clean_url%%\#*}"

    # Match Hugging Face URLs (huggingface.co or hf.co; models, datasets, spaces; resolve, blob, or raw)
    local hf_regex="^(https?://)?(www\.)?(huggingface\.co|hf\.co)/((datasets|spaces)/)?([^/]+/[^/]+)/(resolve|blob|raw)/([^/]+)/(.+)$"

    if [[ "$clean_url" =~ $hf_regex ]]; then
        local repo_type="${BASH_REMATCH[5]:-model}"
        [[ "$repo_type" == "datasets" ]] && repo_type="dataset"
        [[ "$repo_type" == "spaces" ]] && repo_type="space"
        local repo_id="${BASH_REMATCH[6]}"
        local revision="${BASH_REMATCH[8]}"
        local filename="${BASH_REMATCH[9]}"

        if command -v hf &>/dev/null; then
            echo "Using 'hf download' for $repo_id / $filename (revision: $revision, type: $repo_type)..."
            local temp_dir
            temp_dir="$(mktemp -d -p "$target_subdir" ".hf_tmp_XXXXXX" 2>/dev/null || mktemp -d)"

            local hf_args=("$repo_id" "$filename" "--type" "$repo_type" "--revision" "$revision" "--local-dir" "$temp_dir")

            if hf download "${hf_args[@]}"; then
                rm -f "$target_path"
                mv -f "${temp_dir}/${filename}" "$target_path"
                rm -rf "$temp_dir"
                echo "Successfully downloaded $filename."
                return 0
            else
                rm -rf "$temp_dir"
                echo "Error: 'hf download' failed for $repo_id / $filename (gated model, missing token, or remote error)." >&2
                return 1
            fi
        else
            echo "Warning: 'hf' CLI not available for Hugging Face URL. Attempting curl..."
        fi
    fi

    # Fallback to curl (for non-HF URLs or when hf tool is absent)
    echo "Downloading via curl..."
    local temp_dl
    temp_dl="$(mktemp -p "$target_subdir" ".curl_tmp_XXXXXX")"
    local curl_args=("-L" "--fail" "-o" "$temp_dl")
    if [[ -n "${HF_TOKEN:-}" && "$download_url" =~ (huggingface\.co|hf\.co) ]]; then
        curl_args+=("-H" "Authorization: Bearer $HF_TOKEN")
    elif [[ -n "${HUGGING_FACE_HUB_TOKEN:-}" && "$download_url" =~ (huggingface\.co|hf\.co) ]]; then
        curl_args+=("-H" "Authorization: Bearer $HUGGING_FACE_HUB_TOKEN")
    fi
    if curl "${curl_args[@]}" "$download_url"; then
        rm -f "$target_path"
        mv -f "$temp_dl" "$target_path"
        echo "Successfully downloaded via curl."
        return 0
    else
        echo "Error: Failed to download $download_url" >&2
        rm -f "$temp_dl"
        return 1
    fi
}
convert_and_quantize_reranker() {
    local target_path="$1"
    local temp_hf_dir
    local temp_f16_gguf

    echo "Initiating local conversion and quantization pipeline for Qwen3-Reranker-0.6B..."

    # Verify prerequisites
    if ! command -v uv &>/dev/null; then
        echo "Error: 'uv' package manager is required for conversion but not found." >&2
        return 1
    fi

    if [[ ! -f "/usr/bin/convert_hf_to_gguf.py" ]]; then
        echo "Error: '/usr/bin/convert_hf_to_gguf.py' not found." >&2
        return 1
    fi

    if ! command -v llama-quantize &>/dev/null; then
        echo "Error: 'llama-quantize' utility not found." >&2
        return 1
    fi

    # Create temporary sandbox directory for downloading and converting
    temp_hf_dir="$(mktemp -d)"
    temp_f16_gguf="$(mktemp -p "$temp_hf_dir" -t "reranker.F16.XXXXXX.gguf")"

    # Setup clean exit traps
    cleanup() {
        echo "Cleaning up temporary files..."
        rm -rf "$temp_hf_dir"
    }
    trap cleanup EXIT

    echo "Downloading Hugging Face source weights for Qwen/Qwen3-Reranker-0.6B..."
    # Download the files via hf download
    if ! hf download Qwen/Qwen3-Reranker-0.6B --local-dir "$temp_hf_dir"; then
        echo "Error: Failed to download source weights from Hugging Face." >&2
        return 1
    fi

    echo "Converting Hugging Face weights to F16 GGUF..."
    if ! uv run --with "transformers>=4.48.0" --with gguf --with sentencepiece --with torch \
        /usr/bin/convert_hf_to_gguf.py "$temp_hf_dir" --outfile "$temp_f16_gguf" --outtype f16; then
        echo "Error: GGUF conversion failed." >&2
        return 1
    fi

    echo "Quantizing F16 GGUF to Q4_K_M..."
    rm -f "$target_path"
    if ! llama-quantize "$temp_f16_gguf" "$target_path" Q4_K_M; then
        rm -f "$target_path"
        return 1
    fi

    echo "Successfully converted and quantized reranker: $target_path"
    # Unset trap so cleanup runs now
    trap - EXIT
    cleanup
    return 0
}

hf_to_mlc() {
    if [ "$#" -lt 3 ]; then
        echo "Usage: hf_to_mlc <source> <destbasedir> <quant> <modeltype> <template>" >&2
        return 1
    fi

    local source_path="$1"
    local dest_path="$2"
    local quant="$3"
    local model_type="$4"
    local conv_template="$5"

    if [ ! -d "$source_path" ]; then
        echo "Error: Source directory '$source_path' does not exist." >&2
        return 1
    fi

    local model_name
    model_name=$(basename "$source_path")
    local mlc_model_dir="${dest_path}/${model_name}-MLC-${quant}"
    mkdir -p "$mlc_model_dir"

    # Files to verify progress
    local config_file="${mlc_model_dir}/mlc-chat-config.json"
    local cache_file="${mlc_model_dir}/tensor-cache.json"

    # --- Step 1: Generate Config ---
    echo "Creating config file: $config_file"
    if [ -f "$config_file" ]; then
        echo "Skipped: Config already exists." >&2
    else
        local cmd_gen_config=(mlc_llm gen_config "$source_path" --quantization "$quant" -o "$mlc_model_dir")
        cmd_gen_config+=(--model-type "$model_type")
        cmd_gen_config+=(--conv-template "$conv_template")

        if ! "${cmd_gen_config[@]}"; then
            echo "Error: gen_config failed." >&2
            return 1
        fi
    fi

    # --- Step 2: Convert Weight ---
    echo "Converting weights..."
    if [ -f "$cache_file" ]; then
        echo "Skipped: Converted weights already exist." >&2
    else
        local cmd_convert_weight=(mlc_llm convert_weight "$source_path" --quantization "$quant" -o "$mlc_model_dir")
        cmd_convert_weight+=(--model-type "$model_type")
        cmd_convert_weight+=(--device "rocm:0")

        if ! "${cmd_convert_weight[@]}"; then
            echo "Error: convert_weight failed." >&2
            return 1
        fi
        echo "Created weights: $cache_file"
    fi

    # --- Step 3: Compile .so variants ---
    # ROCm FlashInfer variant (default)
    local lib_rocm_fi="${mlc_model_dir}/lib_rocm_fi.so"
    echo "Compiling ROCm + FlashInfer..."
    if [ -f "$lib_rocm_fi" ]; then
        echo "Skipped: lib_rocm_fi.so already exists." >&2
    else
        if ! mlc_llm compile "$mlc_model_dir" --device rocm \
            --opt "flashinfer=1;cublas_gemm=0;cudagraph=1;cutlass=0" \
            -o "$lib_rocm_fi"; then
            echo "Error: Compilation failed for ROCm FlashInfer." >&2
            return 1
        fi
        echo "Compiled: lib_rocm_fi.so"
    fi

    # ROCm non-FlashInfer variant
    local lib_rocm="${mlc_model_dir}/lib_rocm.so"
    echo "Compiling ROCm (no FlashInfer)..."
    if [ -f "$lib_rocm" ]; then
        echo "Skipped: lib_rocm.so already exists." >&2
    else
        if ! mlc_llm compile "$mlc_model_dir" --device rocm \
            --opt "flashinfer=0;cublas_gemm=0;cudagraph=0;cutlass=0" \
            -o "$lib_rocm"; then
            echo "Error: Compilation failed for ROCm (non-FI)." >&2
            return 1
        fi
        echo "Compiled: lib_rocm.so"
    fi
}

main() {
    # Check arguments
    if [[ $# -lt 1 ]]; then
        show_help
        exit 1
    fi

    # Check for help
    for arg in "$@"; do
        if [[ "$arg" == "--help" || "$arg" == "-h" ]]; then
            show_help
            exit 0
        fi
    done

    target_dir="$1"
    shift

    # Parse options
    while [[ $# -gt 0 ]]; do
        case "$1" in
        --all)
            download_all=true
            shift
            ;;
        --llm)
            download_llm=true
            shift
            ;;
        --embedding)
            download_embedding=true
            shift
            ;;
        --reranker)
            download_reranker=true
            shift
            ;;
        --speech-to-text)
            download_stt=true
            shift
            ;;
        --text-to-speech | --tts)
            download_tts=true
            shift
            ;;
        --image)
            download_image=true
            shift
            ;;
        --completion)
            download_completion=true
            shift
            ;;
        --benchmark-context | --benchmark)
            download_benchmark=true
            shift
            ;;
        --projections | --strata-projections)
            download_projections=true
            shift
            ;;
        --strata)
            download_strata=true
            download_strata_shards=true
            download_strata_aux=true
            download_projections=true
            download_dspark=true
            shift
            ;;
        --strata-shards | --strata-model)
            download_strata_shards=true
            shift
            ;;
        --strata-additional | --strata-aux)
            download_strata_aux=true
            download_projections=true
            download_dspark=true
            shift
            ;;
        --dspark)
            download_dspark=true
            shift
            ;;
        *)
            echo "Error: Unknown option '$1'" >&2
            show_help >&2
            exit 1
            ;;
        esac
    done

    if [[ "$download_all" == false && "$download_llm" == false && "$download_embedding" == false && "$download_reranker" == false && "$download_stt" == false && "$download_tts" == false && "$download_image" == false && "$download_completion" == false && "$download_benchmark" == false && "$download_projections" == false && "$download_strata" == false && "$download_strata_shards" == false && "$download_strata_aux" == false && "$download_dspark" == false ]]; then
        echo "Error: No models or tasks specified. Please use --all or select specific models/tasks (--llm, --embedding, --reranker, --speech-to-text, --text-to-speech, --image, --completion, --benchmark-context, --projections, --strata, --strata-shards, --strata-additional, --dspark)." >&2
        exit 1
    fi

    if [[ "$download_all" == true ]]; then
        download_llm=true
        download_embedding=true
        download_reranker=true
        download_stt=true
        download_tts=true
        download_image=true
        download_completion=true
        download_benchmark=true
        download_projections=true
        download_strata=true
        download_strata_shards=true
        download_strata_aux=true
        download_dspark=true
    fi

    # Resolve absolute target path
    target_dir="$(mkdir -p "$target_dir" && cd "$target_dir" && pwd)"

    echo "Target directory: $target_dir"

    # 1. Vision-Text (LLM)

    if [[ "$download_llm" == true ]]; then
        echo "=== Acquiring Vision-Text Models ==="

        # 1a. LLM
        acquire_file \
            "vision-text/Qwen3.6-35B-A3B-APEX-I-Compact.gguf" \
            "https://huggingface.co/mudler/Qwen3.6-35B-A3B-APEX-GGUF/resolve/main/Qwen3.6-35B-A3B-APEX-I-Compact.gguf" \
            "${target_dir}/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact.gguf"

        # 1b. vision projector (mmproj)
        acquire_file \
            "vision-text/Qwen3.6-35B-A3B-APEX-I-Compact-mmproj.gguf" \
            "https://huggingface.co/mudler/Qwen3.6-35B-A3B-APEX-GGUF/resolve/main/mmproj.gguf" \
            "${target_dir}/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact-mmproj.gguf"

        # 1c. Chat template
        acquire_file \
            "vision-text/Qwen3.6-chat_template.jinja" \
            "https://huggingface.co/froggeric/Qwen-Fixed-Chat-Templates/resolve/main/chat_template.jinja" \
            "${target_dir}/vision-text/Qwen3.6-chat_template.jinja"

        # 1d. Multimodal vision test image
        acquire_file \
            "vision-text/test_image.jpg" \
            "https://upload.wikimedia.org/wikipedia/commons/thumb/8/85/Tour_Eiffel_Wikimedia_Commons_%28cropped%29.jpg/960px-Tour_Eiffel_Wikimedia_Commons_%28cropped%29.jpg" \
            "${target_dir}/vision-text/test_image.jpg"

        # 1e. MTP Draft Head Model (Q8_0 ~855 MiB)
        acquire_file \
            "vision-text/Qwen3.6-35B-A3B-MTP-ONLY.gguf" \
            "https://huggingface.co/IHaveNoClueAndIMustPost/Qwen3.6-35A3B-MTP-TENSORS-ONLY/resolve/main/am17an-Qwen3.6-35BA3B-MTP-only.gguf" \
            "${target_dir}/vision-text/Qwen3.6-35B-A3B-MTP-ONLY.gguf"

        # 1f. Build merged MTP model with postfix -mtp
        mtp_target_path="${target_dir}/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact-mtp.gguf"
        if [[ -s "$mtp_target_path" ]]; then
            echo "Merged MTP model already exists: $mtp_target_path (Skipping)"
        else
            echo "Building merged MTP model: $mtp_target_path..."
            rm -f "$mtp_target_path"
            python3 "$(dirname "$0")/download-helper.py" merge-mtp \
                "${target_dir}/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact.gguf" \
                "${target_dir}/vision-text/Qwen3.6-35B-A3B-MTP-ONLY.gguf" \
                "$mtp_target_path"
        fi

        # 1j. Download BigBang-v1 GGUF (IQ4_XS ~17.95 GB) and vision projector
        acquire_file \
            "vision-text/BigBang-v1-IQ4_XS.gguf" \
            "https://huggingface.co/bartowski/endless-frontier_BigBang-v1-GGUF/resolve/main/endless-frontier_BigBang-v1-IQ4_XS.gguf" \
            "${target_dir}/vision-text/BigBang-v1-IQ4_XS.gguf"
        acquire_file \
            "vision-text/BigBang-v1-mmproj-f16.gguf" \
            "https://huggingface.co/bartowski/endless-frontier_BigBang-v1-GGUF/resolve/main/mmproj-endless-frontier_BigBang-v1-f16.gguf" \
            "${target_dir}/vision-text/BigBang-v1-mmproj-f16.gguf"

        # 1g. Download small Hugging Face weights for testing MLC compilation (Qwen2.5-0.5B-Instruct)
        echo "Downloading small Hugging Face weights for testing (Qwen2.5-0.5B-Instruct)..."
        mkdir -p "${target_dir}/text/Qwen2.5-0.5B-Instruct"
        if command -v hf &>/dev/null; then
            hf download Qwen/Qwen2.5-0.5B-Instruct --local-dir "${target_dir}/text/Qwen2.5-0.5B-Instruct"
        else
            echo "Warning: 'hf' CLI not found. Skipping download of HF safetensors model." >&2
        fi

        # 1h. Automatically convert and compile Qwen2.5-0.5B-Instruct
        local mlc_quant=q4bf16_1
        local mlc_out_dir="${target_dir}/text"
        hf_to_mlc "${target_dir}/text/Qwen2.5-0.5B-Instruct" "${mlc_out_dir}" ${mlc_quant} "qwen2" "qwen2"
        # 1i. Download Agents-A1 APEX finetune (Qwen3.6-35B-A3B agent-optimized)
        acquire_file \
            "vision-text/Agents-A1-APEX-I-Compact.gguf" \
            "https://huggingface.co/mudler/Agents-A1-APEX-GGUF/resolve/main/Agents-A1-APEX-I-Compact.gguf" \
            "${target_dir}/vision-text/Agents-A1-APEX-I-Compact.gguf"
        acquire_file \
            "vision-text/Agents-A1-APEX-I-Compact.mmproj.gguf" \
            "https://huggingface.co/mudler/Agents-A1-APEX-GGUF/resolve/main/mmproj.gguf" \
            "${target_dir}/vision-text/Agents-A1-APEX-I-Compact.mmproj.gguf"

    fi

    # 2. Embedding

    if [[ "$download_embedding" == true ]]; then
        echo "=== Acquiring Embedding Model ==="
        # Download Qwen3-Embedding-0.6B Q8_0 GGUF (639 MB, fixed EOS from iyanello)
        # Causal Qwen3 decoder, 596M params, 1024-dim, 32K max ctx, last-token pooling
        # Serves via: llama-server --embeddings --pooling last -c 8192
        acquire_file \
            "embedding/Qwen3-Embedding-0.6B-Q8_0.gguf" \
            "https://huggingface.co/iyanello/Qwen3-Embedding-0.6B-GGUF/resolve/main/Qwen3-Embedding-0.6B-Q8_0.gguf" \
            "${target_dir}/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf"

        # Download pplx-embed-context-v1-0.6b Q8_0 GGUF for llama.cpp (639 MB)
        # Pre-converted via hellc's fork (bit-perfect); bidirectional Qwen3 encoder, non-causal attention
        # Serves via: llama-server --embeddings --pooling mean -b 8192 -ub 8192
        acquire_file \
            "embedding/pplx-embed-context-v1-0.6b-q8_0.gguf" \
            "https://huggingface.co/argus-ai/pplx-embed-context-v1-0.6b-GGUF/resolve/main/pplx-embed-context-v1-0.6b-q8_0.gguf" \
            "${target_dir}/embedding/pplx-embed-context-v1-0.6b-q8_0.gguf"

        # Download full Hugging Face weights for TEI/Infinity
        echo "Downloading full Hugging Face weights for Infinity/TEI (Qwen3-Embedding-0.6B)..."
        mkdir -p "${target_dir}/embedding/Qwen3-Embedding-0.6B"
        if command -v hf &>/dev/null; then
            hf download Qwen/Qwen3-Embedding-0.6B --local-dir "${target_dir}/embedding/Qwen3-Embedding-0.6B"
            echo "Downloading Qwen3-Embedding-0.6B Q8 ONNX model for Infinity (~620 MB)..."
            mkdir -p "${target_dir}/embedding/Qwen3-Embedding-0.6B-ONNX"
            hf download onnx-community/Qwen3-Embedding-0.6B-ONNX \
                --include "*.json" --include "*.txt" --include "onnx/model_int8.onnx" \
                --local-dir "${target_dir}/embedding/Qwen3-Embedding-0.6B-ONNX"
        else
            echo "Warning: 'hf' CLI not found. Skipping download of HF safetensors & ONNX models." >&2
        fi

        # NOTE: pplx-embed-context-v1-0.6b safetensors are kept for reference/TEI fallback
        echo "Downloading full Hugging Face weights for TEI (pplx-embed-context-v1-0.6b)..."
        mkdir -p "${target_dir}/embedding/pplx-embed-context-v1-0.6b"
        if command -v hf &>/dev/null; then
            hf download perplexity-ai/pplx-embed-context-v1-0.6b --local-dir "${target_dir}/embedding/pplx-embed-context-v1-0.6b"
        else
            echo "Warning: 'hf' CLI not found. Skipping download of HF safetensors model." >&2
        fi

        # Download BAAI/bge-m3 Q8_0 GGUF from official ggml-org (635 MB)
        # XLM-RoBERTa encoder, 568M params, 1024-dim embeddings, 8K max context
        # Serves via: llama-server --embeddings --pooling cls -c 8192
        # Official ggml-org conversion, near-lossless quality (<0.5% degradation vs F16)
        acquire_file \
            "embedding/bge-m3-q8_0.gguf" \
            "https://huggingface.co/ggml-org/bge-m3-Q8_0-GGUF/resolve/main/bge-m3-q8_0.gguf" \
            "${target_dir}/embedding/bge-m3-q8_0.gguf"

        # NOTE: bge-m3 safetensors kept for TEI reference; TEI engine is abandoned,
        # the llama.cpp path uses bge-m3 GGUF above instead.
        echo "Downloading essential TEI files for bge-m3 (~2.3 GB, skipping ONNX/images/ColBERT extras)..."
        mkdir -p "${target_dir}/embedding/bge-m3"
        python3 -c '
import sys
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id="BAAI/bge-m3",
    local_dir=sys.argv[1],
    ignore_patterns=[
        "onnx/**",      # ONNX exports (redundant for TEI PyTorch backend)
        "imgs/**",      # sample images
        "*.jpg",        # sample image
        "colbert_linear.pt",   # ColBERT multi-vector (not used by TEI bi-encoder)
        "sparse_linear.pt",    # lexical retrieval (not used by TEI bi-encoder)
    ],
)
' "${target_dir}/embedding/bge-m3" || {
            echo "Warning: snapshot_download failed. Falling back to hf download."
            echo "  hf download BAAI/bge-m3 --local-dir ${target_dir}/embedding/bge-m3"
            hf download BAAI/bge-m3 --local-dir "${target_dir}/embedding/bge-m3" || true
        }
    fi

    # 3. Reranker

    if [[ "$download_reranker" == true ]]; then
        echo "=== Acquiring Reranker Model ==="
        reranker_target="${target_dir}/reranker/Qwen3-Reranker-0.6B.Q4_K_M.gguf"

        if [[ -s "$reranker_target" ]]; then
            echo "Reranker model already exists and is non-empty: $reranker_target (Skipping)"
        else
            success=false

            # Try downloading the working sequence-classification version from Hugging Face
            if [[ "$success" == false ]]; then
                echo "Attempting to download pre-converted sequence classification GGUF from prithivMLmods..."
                if acquire_file \
                    "reranker/Qwen3-Reranker-0.6B.Q4_K_M.gguf" \
                    "https://huggingface.co/prithivMLmods/Qwen3-Reranker-0.6B-seq-cls-GGUF/resolve/main/Qwen3-Reranker-0.6B-seq-cls.Q4_K_M.gguf" \
                    "$reranker_target"; then
                    echo "Successfully downloaded pre-converted working reranker."
                    success=true
                fi
            fi

            # Adopt the local conversion pipeline if downloading pre-converted fails
            if [[ "$success" == false ]]; then
                echo "Pre-converted download not successful or not found. Falling back to local conversion..."
                if convert_and_quantize_reranker "$reranker_target"; then
                    success=true
                fi
            fi

            if [[ "$success" == false ]]; then
                echo "Error: Failed to acquire a working Qwen3 Reranker GGUF." >&2
                exit 1
            fi
        fi

        # Download HF PyTorch/Safetensors weights for Infinity (Qwen3-Reranker-0.6B)
        echo "Downloading full Hugging Face weights for Infinity (Qwen3-Reranker-0.6B)..."
        mkdir -p "${target_dir}/reranker/Qwen3-Reranker-0.6B"
        if command -v hf &>/dev/null; then
            hf download Qwen/Qwen3-Reranker-0.6B --local-dir "${target_dir}/reranker/Qwen3-Reranker-0.6B"
        else
            echo "Warning: 'hf' CLI not found. Skipping download of HF safetensors model." >&2
        fi

        # Download HF PyTorch/Safetensors/ONNX weights for Infinity (BAAI/bge-reranker-v2-m3)
        echo "Downloading full Hugging Face weights for Infinity (BAAI/bge-reranker-v2-m3)..."
        mkdir -p "${target_dir}/reranker/bge-reranker-v2-m3"
        if command -v hf &>/dev/null; then
            hf download BAAI/bge-reranker-v2-m3 --local-dir "${target_dir}/reranker/bge-reranker-v2-m3"
        else
            echo "Warning: 'hf' CLI not found. Skipping download of HF safetensors model." >&2
        fi

        # Download jina-reranker-v3 Q4_K_M GGUF for llama.cpp (397 MB)
        # Official Jina AI conversion; requires hanxiao/llama.cpp fork or PR #22576 (draft)
        # Architecture: Qwen3-0.6B decoder + MLP projector, 131K context, listwise 64 docs
        # Serves via: llama-server --reranking --pooling rank (when PR #22576 merges)
        acquire_file \
            "reranker/jina-reranker-v3-Q4_K_M.gguf" \
            "https://huggingface.co/jinaai/jina-reranker-v3-GGUF/resolve/main/jina-reranker-v3-Q4_K_M.gguf" \
            "${target_dir}/reranker/jina-reranker-v3-Q4_K_M.gguf"

        # Download projector weights for jina-reranker-v3 (3 MB)
        # Required for the Python rerank.py wrapper in the hanxiao/llama.cpp fork
        # The projector (1024 → 512 → 256) is NOT baked into the GGUF
        acquire_file \
            "reranker/jina-reranker-v3-projector.safetensors" \
            "https://huggingface.co/jinaai/jina-reranker-v3-GGUF/resolve/main/projector.safetensors" \
            "${target_dir}/reranker/jina-reranker-v3-projector.safetensors"

        # NOTE: jina-reranker-v3 safetensors kept for reference; TEI engine is abandoned,
        # the llama.cpp path uses the GGUF + projector above instead.
        echo "Downloading full Hugging Face weights for jina-reranker-v3 [reference only]..."
        mkdir -p "${target_dir}/reranker/jina-reranker-v3"
        if command -v hf &>/dev/null; then
            hf download jinaai/jina-reranker-v3 --local-dir "${target_dir}/reranker/jina-reranker-v3"
        else
            echo "Warning: 'hf' CLI not found. Skipping download of HF safetensors model." >&2
        fi

        echo "Downloading essential model files for ettin-reranker-400m-v1..."
        mkdir -p "${target_dir}/reranker/ettin-reranker-400m-v1"
        python3 -c '
import sys
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id="cross-encoder/ettin-reranker-400m-v1",
    local_dir=sys.argv[1],
    ignore_patterns=["openvino/**"],
)
' "${target_dir}/reranker/ettin-reranker-400m-v1" || {
            echo "Warning: snapshot_download failed." >&2
            echo "  Try: hf download cross-encoder/ettin-reranker-400m-v1 --local-dir ${target_dir}/reranker/ettin-reranker-400m-v1" >&2
        }

        echo "Downloading essential files for ettin-reranker-150m-v1 (~596 MB)..."
        # No GGUF exists for 150m/400m ettin (SentTrans head, not standard BertForSeqClass)
        mkdir -p "${target_dir}/reranker/ettin-reranker-150m-v1"
        python3 -c '
import sys
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id="cross-encoder/ettin-reranker-150m-v1",
    local_dir=sys.argv[1],
    ignore_patterns=["openvino/**"],
)
' "${target_dir}/reranker/ettin-reranker-150m-v1" || {
            echo "Warning: snapshot_download failed. Trying fallback..." >&2
            hf download cross-encoder/ettin-reranker-150m-v1 --local-dir "${target_dir}/reranker/ettin-reranker-150m-v1" || true
        }

        # --- Additional Reranker Models (GGUF for llama-server) ---

        # bge-reranker-v2-m3 GGUF (gpustack community conversion)
        # 567M params, 8K ctx, XLM-RoBERTa cross-encoder, MIT license
        # MTEB(eng,v2) NDCG@10: ~0.553, German BEIR: ~57.2
        # Q4_K_M ~360 MB disk, ~2.0 GB VRAM
        # Serves via: llama-server --reranking
        acquire_file \
            "reranker/bge-reranker-v2-m3-Q4_K_M.gguf" \
            "https://huggingface.co/gpustack/bge-reranker-v2-m3-GGUF/resolve/main/bge-reranker-v2-m3-Q4_K_M.gguf" \
            "${target_dir}/reranker/bge-reranker-v2-m3-Q4_K_M.gguf"

        # jina-reranker-v3.5 GGUF (official Jina AI conversion)
        # 600M params, 131K ctx, listwise LBNL architecture, Qwen3-0.6B backbone
        # BEIR: 63.20 (highest in 0.6B class), MIRACL: 74.11, German: ✅
        # License: CC BY-NC 4.0 (non-commercial)
        # Q4_K_M ~379 MB disk, ~2.5 GB VRAM
        acquire_file \
            "reranker/jina-reranker-v3.5-Q4_K_M.gguf" \
            "https://huggingface.co/jinaai/jina-reranker-v3.5-GGUF/resolve/main/jina-reranker-v3.5-Q4_K_M.gguf" \
            "${target_dir}/reranker/jina-reranker-v3.5-Q4_K_M.gguf"

        # --- Additional Reranker Models (Infinity / TEI / safetensors) ---

        # LAMAR-600m (safetensors) — BEST multilingual under 5GB, MIT license
        # 600M params, 8K ctx, XLM-RoBERTa cross-encoder, 51 langs including German
        # MIRACL: 69.49, XQuAD nDCG@10: 98.59, German: ✅✅ (excellent)
        # License: MIT
        # ~1.2 GB fp16 safetensors, ~3.5 GB VRAM at full precision
        if command -v hf &>/dev/null; then
            echo "Downloading LAMAR-600m (safetensors, MIT license, excellent German)..."
            mkdir -p "${target_dir}/reranker/LAMAR-600m"
            hf download nlpai-lab/LAMAR-600m --local-dir "${target_dir}/reranker/LAMAR-600m"
        else
            echo "Warning: 'hf' CLI not found. Skipping LAMAR-600m download." >&2
        fi

        # KaLM-Reranker-V1-Nano (safetensors) — Ultra-lightweight, 128K ctx, Apache 2.0
        # 270M params, 128K ctx, encoder-decoder (T5Gemma2), FBNL architecture
        # Apache 2.0 license
        # ~600 MB fp16 safetensors, ~1.5 GB VRAM
        if command -v hf &>/dev/null; then
            echo "Downloading KaLM-Reranker-V1-Nano (safetensors, Apache 2.0, 128K ctx)..."
            mkdir -p "${target_dir}/reranker/KaLM-Reranker-V1-Nano"
            hf download KaLM-Embedding/KaLM-Reranker-V1-Nano --local-dir "${target_dir}/reranker/KaLM-Reranker-V1-Nano"
        else
            echo "Warning: 'hf' CLI not found. Skipping KaLM-Reranker-V1-Nano download." >&2
        fi

        # mxbai-rerank-base-v2 (safetensors) — 109 languages, 32K ctx, Apache 2.0
        # 494M params, 32K ctx, causal decoder (Qwen2-0.5B), GRPO-trained
        # BEIR: 55.57, German: ✅
        # Apache 2.0 license
        # ~1.0 GB fp16 safetensors, ~2.5 GB VRAM
        if command -v hf &>/dev/null; then
            echo "Downloading mxbai-rerank-base-v2 (safetensors, Apache 2.0, 32K ctx)..."
            mkdir -p "${target_dir}/reranker/mxbai-rerank-base-v2"
            hf download mixedbread-ai/mxbai-rerank-base-v2 --local-dir "${target_dir}/reranker/mxbai-rerank-base-v2"

            echo "Downloading BAAI/bge-reranker-v2-m3 Q8 ONNX model for Infinity (~588 MB)..."
            mkdir -p "${target_dir}/reranker/bge-reranker-v2-m3-ONNX"
            hf download onnx-community/bge-reranker-v2-m3-ONNX \
                --include "*.json" --include "*.txt" --include "onnx/model_int8.onnx" \
                --local-dir "${target_dir}/reranker/bge-reranker-v2-m3-ONNX"

            echo "Downloading BAAI/bge-reranker-large (safetensors + ONNX)..."
            mkdir -p "${target_dir}/reranker/bge-reranker-large"
            hf download BAAI/bge-reranker-large --local-dir "${target_dir}/reranker/bge-reranker-large"

            echo "Downloading Qwen3-Reranker-0.6B Q4 ONNX model for Infinity (~995 MB)..."
            mkdir -p "${target_dir}/reranker/Qwen3-Reranker-0.6B-ONNX"
            hf download onnx-community/Qwen3-Reranker-0.6B-ONNX \
                --include "*.json" --include "*.txt" --include "onnx/model_q4.onnx" \
                --local-dir "${target_dir}/reranker/Qwen3-Reranker-0.6B-ONNX"
        else
            echo "Warning: 'hf' CLI not found. Skipping ONNX reranker downloads." >&2
        fi

        # KaLM-Reranker-V1-Nano Q4_K_M GGUF for llama-server
        acquire_file \
            "reranker/kalm-reranker-v1-nano-q4_k_m.gguf" \
            "https://huggingface.co/KaLM-Embedding/KaLM-Reranker-V1-Nano-Q4_K_M-GGUF/resolve/main/kalm-reranker-v1-nano-q4_k_m.gguf" \
            "${target_dir}/reranker/kalm-reranker-v1-nano-q4_k_m.gguf"
    fi

    # 4. Speech-to-Text

    if [[ "$download_stt" == true ]]; then
        echo "=== Acquiring Speech-to-Text Model ==="
        acquire_file \
            "speech-to-text/ggml-large-v3-turbo-q5_0.bin" \
            "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3-turbo-q5_0.bin" \
            "${target_dir}/speech-to-text/ggml-large-v3-turbo-q5_0.bin"
        acquire_file \
            "speech-to-text/speech-to-text.ogg" \
            "https://upload.wikimedia.org/wikipedia/commons/2/23/William_McKinley_campaign_speech_1896.ogg" \
            "${target_dir}/speech-to-text/speech-to-text.ogg"
    fi

    # 5. Text-to-Speech

    if [[ "$download_tts" == true ]]; then
        echo "=== Acquiring Text-to-Speech Models ==="
        # 5a. CustomVoice 0.6B (GGUF for qwen3-tts.cpp)
        acquire_file \
            "text-to-speech/Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf" \
            "https://huggingface.co/khimaros/Qwen3-TTS-12Hz-0.6B-CustomVoice-GGUF/resolve/main/Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf" \
            "${target_dir}/text-to-speech/Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf"

        # 5b. Tokenizer (GGUF for qwen3-tts.cpp)
        acquire_file \
            "text-to-speech/Qwen3-TTS-Tokenizer-12Hz-F16.gguf" \
            "https://huggingface.co/khimaros/Qwen3-TTS-Tokenizer-12Hz-GGUF/resolve/main/Qwen3-TTS-Tokenizer-12Hz-F16.gguf" \
            "${target_dir}/text-to-speech/Qwen3-TTS-Tokenizer-12Hz-F16.gguf"

        # 5c. Qwen3-TTS Safetensors Checkpoint
        echo "Downloading Qwen3-TTS checkpoint (Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice)..."
        mkdir -p "${target_dir}/text-to-speech/Qwen3-TTS-12Hz-0.6B-CustomVoice"
        if command -v hf &>/dev/null; then
            hf download Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice --local-dir "${target_dir}/text-to-speech/Qwen3-TTS-12Hz-0.6B-CustomVoice"
        else
            echo "Warning: 'hf' CLI not found. Skipping Qwen3-TTS download." >&2
        fi

        local onnx_dir="${target_dir}/text-to-speech/kokoro-onnx"
        local gguf_dir="${target_dir}/text-to-speech/kokoro-gguf"
        mkdir -p "${onnx_dir}/voices" "${gguf_dir}/voices"

        # 5d. Multilingual Kokoro-82M ONNX Reference Model & English Voices
        if command -v hf &>/dev/null; then
            echo "Acquiring Multilingual Kokoro-82M ONNX model (English & Multilingual)..."
            hf download onnx-community/Kokoro-82M-v1.0-ONNX \
                --include "onnx/model.onnx" \
                --include "tokenizer.json" \
                --include "voices/*.bin" \
                --local-dir "${onnx_dir}"
            # Standardize filename if inside subfolder
            if [[ -f "${onnx_dir}/onnx/model.onnx" && ! -f "${onnx_dir}/model.onnx" ]]; then
                ln -sfn "onnx/model.onnx" "${onnx_dir}/model.onnx"
            fi
        fi

        # 5e. Native German Martin ONNX Model
        if command -v hf &>/dev/null; then
            echo "Acquiring Native German Martin ONNX model..."
            hf download Godelaune/Kokoro-82M-ONNX-German-Martin \
                --include "kokoro-martin.onnx" \
                --include "voices-martin.npz" \
                --local-dir "${onnx_dir}"
            if [[ -f "${onnx_dir}/kokoro-martin.onnx" && ! -f "${onnx_dir}/model-de.onnx" ]]; then
                ln -sfn "kokoro-martin.onnx" "${onnx_dir}/model-de.onnx"
            fi
            # Extract German Victoria voice embedding (full GGUF pack preferred over 1KB stub)
            hf download soniqo/Kokoro-82M-German-Victoria-ONNX \
                --include "voices/df_victoria.bin" \
                --local-dir "${onnx_dir}"
            # Acquire Kerstin voicepack (cryptomilk/kokoro-german-kerstin)
            hf download cryptomilk/kokoro-german-kerstin \
                --include "voices/df_kerstin.pt" \
                --local-dir "${onnx_dir}"
        fi

        # 5f. Multilingual Kokoro-82M GGUF Model & Approved English Voices
        echo "Acquiring Multilingual Kokoro-82M Q8_0 GGUF model..."
        acquire_file \
            "text-to-speech/kokoro-gguf/kokoro-82m-q8_0.gguf" \
            "https://huggingface.co/simonfxr/kokoro.cpp-GGUF/resolve/main/kokoro-82m-q8_0.gguf" \
            "${gguf_dir}/kokoro-82m-q8_0.gguf"
        if command -v hf &>/dev/null; then
            echo "Acquiring approved English GGUF voicepacks..."
            hf download simonfxr/kokoro.cpp-GGUF \
                --include "voices/kokoro-voice-af_heart.gguf" \
                --include "voices/kokoro-voice-af_bella.gguf" \
                --include "voices/kokoro-voice-af_sarah.gguf" \
                --include "voices/kokoro-voice-bf_emma.gguf" \
                --include "voices/kokoro-voice-am_adam.gguf" \
                --include "voices/kokoro-voice-am_michael.gguf" \
                --include "voices/kokoro-voice-bm_george.gguf" \
                --local-dir "${gguf_dir}"
        fi

        # 5g. German Multispeaker Kokoro HUI Base GGUF Model & German Voicepacks
        acquire_file \
            "text-to-speech/kokoro-gguf/kokoro-de-hui-base-q8_0.gguf" \
            "https://huggingface.co/cstr/kokoro-de-hui-base-GGUF/resolve/main/kokoro-de-hui-base-q8_0.gguf" \
            "${gguf_dir}/kokoro-de-hui-base-q8_0.gguf"
        if command -v hf &>/dev/null; then
            echo "Acquiring approved German GGUF voicepacks (dm_martin, df_victoria, df_eva, dm_bernd)..."
            hf download cstr/kokoro-voices-GGUF \
                --include "kokoro-voice-dm_martin.gguf" \
                --include "kokoro-voice-df_victoria.gguf" \
                --include "kokoro-voice-df_eva.gguf" \
                --include "kokoro-voice-dm_bernd.gguf" \
                --local-dir "${gguf_dir}/voices"
        fi

        # 5h. Native German Kikiri-de Model: Heinrich & Anna (junkstage/kikiri-de)
        if command -v hf &>/dev/null; then
            echo "Acquiring Native German Kikiri-de Model (Heinrich & Anna)..."
            local kikiri_dir="${target_dir}/text-to-speech/kokoro-kikiri-de"
            mkdir -p "${kikiri_dir}"
            hf download junkstage/kikiri-de \
                --include "model.safetensors" \
                --include "config.json" \
                --include "voices/Heinrich.safetensors" \
                --include "voices/Anna.safetensors" \
                --local-dir "${kikiri_dir}"
        fi

        # 5i. Post-Processing: Convert all voice formats into standard .bin in kokoro-onnx/voices/
        echo "Converting and standardizing all voices into ${onnx_dir}/voices/ as .bin files..."
        local convert_cli="${SCRIPT_DIR}/kokoro-ctl.py"

        # Convert and clean up any NPZ files in onnx_dir (e.g. voices-martin.npz -> voices/dm_martin.bin)
        for npz_file in "${onnx_dir}"/*.npz "${onnx_dir}/voices"/*.npz; do
            if [[ -f "$npz_file" ]]; then
                local base_npz
                base_npz="$(basename "$npz_file" .npz)"
                local out_bin="${onnx_dir}/voices/${base_npz}.bin"
                if [[ "$base_npz" == "voices-martin" ]]; then
                    out_bin="${onnx_dir}/voices/dm_martin.bin"
                fi
                echo "  Converting NPZ voice: ${npz_file} -> ${out_bin}"
                "$convert_cli" --convert-voice "$npz_file" "$out_bin"
                rm -f "$npz_file"
            fi
        done
        # Convert PyTorch voicepacks (.pt) in onnx_dir (e.g. df_kerstin.pt -> voices/df_kerstin.bin)
        for pt_file in "${onnx_dir}"/*.pt "${onnx_dir}/voices"/*.pt; do
            if [[ -f "$pt_file" ]]; then
                local base_pt
                base_pt="$(basename "$pt_file" .pt)"
                local out_bin="${onnx_dir}/voices/${base_pt}.bin"
                if [[ ! -f "$out_bin" || $(stat -c%s "$out_bin" 2>/dev/null || echo 0) -lt 500000 ]]; then
                    echo "  Converting PT voice: ${pt_file} -> ${out_bin}"
                    "$convert_cli" --convert-voice "$pt_file" "$out_bin"
                fi
                rm -f "$pt_file"
            fi
        done

        # Convert GGUF voices from kokoro-gguf/voices/ if not already present in kokoro-onnx/voices/
        if [[ -d "${gguf_dir}/voices" ]]; then
            for gguf_file in "${gguf_dir}/voices"/*.gguf; do
                if [[ -f "$gguf_file" ]]; then
                    local base_gguf
                    base_gguf="$(basename "$gguf_file" .gguf)"
                    base_gguf="${base_gguf#kokoro-voice-}"
                    local out_bin="${onnx_dir}/voices/${base_gguf}.bin"
                    # Overwrite if missing or incomplete (< 500KB)
                    if [[ ! -f "$out_bin" || $(stat -c%s "$out_bin" 2>/dev/null || echo 0) -lt 500000 ]]; then
                        echo "  Converting GGUF voice: ${gguf_file} -> ${out_bin}"
                        "$convert_cli" --convert-voice "$gguf_file" "$out_bin"
                    fi
                fi
            done
        fi

        # Convert Safetensors voices from kokoro-kikiri-de/voices/ if present
        local kikiri_voices="${target_dir}/text-to-speech/kokoro-kikiri-de/voices"
        if [[ -d "$kikiri_voices" ]]; then
            for st_file in "${kikiri_voices}"/*.safetensors; do
                if [[ -f "$st_file" ]]; then
                    local st_name
                    st_name="$(basename "$st_file" .safetensors)"
                    local out_bin=""
                    if [[ "${st_name,,}" == "heinrich" ]]; then
                        out_bin="${onnx_dir}/voices/dm_heinrich.bin"
                    elif [[ "${st_name,,}" == "anna" ]]; then
                        out_bin="${onnx_dir}/voices/df_anna.bin"
                    else
                        out_bin="${onnx_dir}/voices/${st_name}.bin"
                    fi
                    if [[ ! -f "$out_bin" ]]; then
                        echo "  Converting Safetensors voice: ${st_file} -> ${out_bin}"
                        "$convert_cli" --convert-voice "$st_file" "$out_bin"
                    fi
                fi
            done
        fi
        echo "All Kokoro voices successfully standardized as .bin format in ${onnx_dir}/voices/."
    fi

    # 6. Image Generation (Z-Image-Turbo)

    if [[ "$download_image" == true ]]; then
        echo "=== Acquiring Image Generation Models ==="
        # 6a. Diffusion model
        acquire_file \
            "image/z_image_turbo-Q8_0.gguf" \
            "https://huggingface.co/jayn7/Z-Image-Turbo-GGUF/resolve/main/z_image_turbo-Q8_0.gguf" \
            "${target_dir}/image/z_image_turbo-Q8_0.gguf"

        # 6b. VAE
        acquire_file \
            "image/ae.safetensors" \
            "https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/ae.safetensors" \
            "${target_dir}/image/ae.safetensors"

        # 6c. Text encoder (LLM)
        acquire_file \
            "image/Qwen3-4B-Q4_K_M.gguf" \
            "https://huggingface.co/unsloth/Qwen3-4B-GGUF/resolve/main/Qwen3-4B-Q4_K_M.gguf" \
            "${target_dir}/image/Qwen3-4B-Q4_K_M.gguf"
    fi

    # 6.5. Code Completion Model and FIM Testdata
    if [[ "$download_completion" == true ]]; then
        echo "=== Acquiring Code Completion Models & Testdata ==="
        acquire_file \
            "completion/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf" \
            "https://huggingface.co/Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF/resolve/main/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf" \
            "${target_dir}/completion/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf"

        acquire_file \
            "completion/test_fim.py" \
            "https://raw.githubusercontent.com/psf/requests/main/src/requests/api.py" \
            "${target_dir}/completion/test_fim.py"
    fi

    # 7. Benchmark Context

    if [[ "$download_benchmark" == true ]]; then
        echo "=== Building Benchmark Context ==="
        python3 "$(dirname "$0")/download-helper.py" benchmark-context --output "${target_dir}/benchmark-context.md"
        python3 "$(dirname "$0")/download-helper.py" hindsight-context --output "${target_dir}/hindsight-context.txt"
    fi

    # 8. Strata Projections & Control Vectors
    if [[ "$download_projections" == true || "$download_strata_aux" == true ]]; then
        echo "=== Acquiring Strata Control Vectors & Projections ==="
        local proj_dir="${target_dir}/strata/projections"
        ensure_real_dir "$proj_dir"

        # 8a. Cudecnik Qwen3.8-Flash-Next refusal projection (480 KB unit vector)
        acquire_file \
            "strata/projections/Qwen3.8-Flash-Next-refusal-projection.gguf" \
            "https://huggingface.co/Cudecnik/Qwen3.8-Flash-Next-refusal-projection/resolve/main/Qwen3.8-Flash-Next-refusal-projection.gguf" \
            "${proj_dir}/Qwen3.8-Flash-Next-refusal-projection.gguf"

        acquire_file \
            "strata/projections/Qwen3.8-Flash-Next-experimental-speed-projection.gguf" \
            "https://huggingface.co/Cudecnik/Qwen3.8-Flash-Next-refusal-projection/resolve/main/Qwen3.8-Flash-Next-refusal-projection.gguf" \
            "${proj_dir}/Qwen3.8-Flash-Next-experimental-speed-projection.gguf"

        acquire_file \
            "strata/projections/Qwen3.8-Flash-Next-refusal-projection.json" \
            "https://huggingface.co/Cudecnik/Qwen3.8-Flash-Next-refusal-projection/resolve/main/Qwen3.8-Flash-Next-refusal-projection.json" \
            "${proj_dir}/Qwen3.8-Flash-Next-refusal-projection.json"

        acquire_file \
            "strata/projections/Qwen3.8-Flash-Next-refusal-additive.gguf" \
            "https://huggingface.co/Cudecnik/Qwen3.8-Flash-Next-refusal-projection/resolve/main/Qwen3.8-Flash-Next-refusal-additive.gguf" \
            "${proj_dir}/Qwen3.8-Flash-Next-refusal-additive.gguf"

        # 8b. msuiche Cyber-Contrast vectors (GLP-47 for Qwen3.8-Flash-Next, GLP-39 for DeepSeek-V4.1, GLP-29 for DSV4)
        acquire_file \
            "strata/projections/Qwen3.8-Flash-Next-abliterated-cyber-GLP-47-L1-47-a1.gguf" \
            "https://huggingface.co/msuiche/Qwen3.8-Flash-Next-abliterated-cyber-GLP-47/resolve/main/Qwen3.8-Flash-Next-abliterated-cyber-GLP-47-L1-47-a1.gguf" \
            "${proj_dir}/Qwen3.8-Flash-Next-abliterated-cyber-GLP-47-L1-47-a1.gguf" || true
        if [[ -f "${proj_dir}/Qwen3.8-Flash-Next-abliterated-cyber-GLP-47-L1-47-a1.gguf" ]]; then
            ln -sfn "Qwen3.8-Flash-Next-abliterated-cyber-GLP-47-L1-47-a1.gguf" "${proj_dir}/Qwen3.8-Flash-Next-abliterated-cyber-GLP-47.gguf"
        fi

        acquire_file \
            "strata/projections/glp.deepseek-v41-flash-1017-GLP-39-L1-39-a0.75.gguf" \
            "https://huggingface.co/msuiche/DeepSeek-V4.1-Flash-1017-abliterated-cyber-GLP-39-L1-39-a0.75/resolve/main/glp.deepseek-v41-flash-1017-GLP-39-L1-39-a0.75.gguf" \
            "${proj_dir}/glp.deepseek-v41-flash-1017-GLP-39-L1-39-a0.75.gguf" || true
        if [[ -f "${proj_dir}/glp.deepseek-v41-flash-1017-GLP-39-L1-39-a0.75.gguf" ]]; then
            ln -sfn "glp.deepseek-v41-flash-1017-GLP-39-L1-39-a0.75.gguf" "${proj_dir}/DeepSeek-V4.1-Flash-1017-abliterated-cyber-GLP-39-L1-39-a0.75.gguf"
        fi

        acquire_file \
            "strata/projections/DeepSeek-V4-Flash-0731-abliterated-cyber-GLP-29-L10-38-a4.gguf" \
            "https://huggingface.co/msuiche/DeepSeek-V4-Flash-0731-abliterated-cyber-GLP-29/resolve/main/DeepSeek-V4-Flash-0731-abliterated-cyber-GLP-29-L10-38-a4.gguf" \
            "${proj_dir}/DeepSeek-V4-Flash-0731-abliterated-cyber-GLP-29-L10-38-a4.gguf" || true
        if [[ -f "${proj_dir}/DeepSeek-V4-Flash-0731-abliterated-cyber-GLP-29-L10-38-a4.gguf" ]]; then
            ln -sfn "DeepSeek-V4-Flash-0731-abliterated-cyber-GLP-29-L10-38-a4.gguf" "${proj_dir}/DeepSeek-V4-Flash-0731-abliterated-cyber-GLP-29.gguf"
        fi
    fi

    # 9. Strata Model Shards, Auxiliary Files & Runtimes
    local strata_dir="${target_dir}/strata/swift15_iq3s"
    local pack_dir="${strata_dir}/packs/swift-iq3_s"

    # 9a. Strata Big Model Shards (~84 GB)
    if [[ "$download_strata_shards" == true ]]; then
        echo "=== Acquiring Strata Swift 1.5 Qwen3.8-Flash-Next Model Shards ==="
        ensure_real_dir "${strata_dir}/models/swift-IQ3_S"

        # Shard 1 (Dense + Experts ~55 GB)
        acquire_file \
            "strata/swift15_iq3s/Swift-Qwen3.8-Flash-Next-GSQ-RCO-IQ3_S-00001-of-00002.gguf" \
            "https://huggingface.co/ukisai/Swift-1.5-Qwen3.8-Flash-Next-GSQ-RCO-GGUF/resolve/main/Swift-Qwen3.8-Flash-Next-GSQ-RCO-IQ3_S-00001-of-00002.gguf" \
            "${strata_dir}/models/swift-IQ3_S/Swift-Qwen3.8-Flash-Next-GSQ-RCO-IQ3_S-00001-of-00002.gguf"

        # Shard 2 (PLE n-gram table ~28.8 GB)
        acquire_file \
            "strata/swift15_iq3s/Swift-Qwen3.8-Flash-Next-GSQ-RCO-IQ3_S-00002-of-00002.gguf" \
            "https://huggingface.co/ukisai/Swift-1.5-Qwen3.8-Flash-Next-GSQ-RCO-GGUF/resolve/main/Swift-Qwen3.8-Flash-Next-GSQ-RCO-IQ3_S-00002-of-00002.gguf" \
            "${strata_dir}/models/swift-IQ3_S/Swift-Qwen3.8-Flash-Next-GSQ-RCO-IQ3_S-00002-of-00002.gguf"
    fi

    # 9b. Strata Auxiliary Files & Runtimes
    if [[ "$download_strata_aux" == true ]]; then
        echo "=== Acquiring Strata Auxiliary Files & Runtimes ==="
        ensure_real_dir "${strata_dir}/models"
        ensure_real_dir "${strata_dir}/mtp"
        ensure_real_dir "${strata_dir}/packs"
        ensure_real_dir "${strata_dir}/dspark"

        # Vision Projector (BF16)
        acquire_file \
            "strata/swift15_iq3s/mmproj-Qwen3.8-Flash-Next-BF16.gguf" \
            "https://huggingface.co/ukisai/Swift-1.5-Qwen3.8-Flash-Next-GSQ-RCO-GGUF/resolve/main/mmproj-Swift-Qwen3.8-Flash-Next-BF16.gguf" \
            "${strata_dir}/models/mmproj-Swift-Qwen3.8-Flash-Next-BF16.gguf"

        # MTP Speculative Drafter weights
        acquire_file \
            "strata/swift15_iq3s/mtp-q2_0.gguf" \
            "https://huggingface.co/SC117/Swift-1.5-Qwen3.8-Flash-Next-GSQ-RCO-abliterated-GGUF/resolve/main/mtp-q2_0.gguf" \
            "${strata_dir}/mtp/mtp-q2_0.gguf"

        # Qwen3.8 Fixed Community Chat Template (froggeric v22.5)
        acquire_file \
            "strata/Qwen3.8-chat_template.jinja" \
            "https://huggingface.co/froggeric/Qwen-Fixed-Chat-Templates/resolve/main/chat_template.jinja" \
            "${target_dir}/strata/Qwen3.8-chat_template.jinja"
        ln -sfn "../Qwen3.8-chat_template.jinja" "${strata_dir}/Qwen3.8-chat_template.jinja"

        # DSpark Speculative Drafter
        local dspark_dir="${strata_dir}/dspark"
        acquire_file \
            "strata/swift15_iq3s/dspark/model.safetensors" \
            "https://huggingface.co/shadowpa0327/Qwen3.8-Flash-Next-DSpark/resolve/main/model.safetensors" \
            "${dspark_dir}/model.safetensors"
        acquire_file \
            "strata/swift15_iq3s/dspark/config.json" \
            "https://huggingface.co/shadowpa0327/Qwen3.8-Flash-Next-DSpark/resolve/main/config.json" \
            "${dspark_dir}/config.json"

        # MTP Runtime Preparation
        local mtp_gguf="${strata_dir}/mtp/mtp-q2_0.gguf"
        local mtp_rt_dir="${strata_dir}/mtp/rt"
        if [[ -s "$mtp_gguf" && ! -s "${mtp_rt_dir}/experts.bin" ]]; then
            echo "=== Preparing Strata MTP Runtime via mtp_rt.py ==="
            ensure_real_dir "$mtp_rt_dir"
            local mtp_rt_tool="${STRATA_TOOLS_DIR:-/usr/share/strata/tools}/mtp_rt.py"
            if [[ -f "$mtp_rt_tool" ]]; then
                python3 "$mtp_rt_tool" --gguf "$mtp_gguf" --out "$mtp_rt_dir"
            else
                echo "Warning: mtp_rt.py not found at $mtp_rt_tool; skipping MTP runtime preparation." >&2
            fi
        fi

        # Draft Vocab Setup
        local draft_vocab_src="${STRATA_DATA_DIR:-/usr/share/strata/data}/draft_vocab.bin"
        if [[ -f "$draft_vocab_src" && ! -s "${mtp_rt_dir}/draft_vocab.bin" ]]; then
            echo "=== Copying MTP draft vocabulary subset ==="
            ensure_real_dir "$mtp_rt_dir"
            cp --remove-destination "$draft_vocab_src" "${mtp_rt_dir}/draft_vocab.bin"
        fi

        # Strata Native Pack Preparation (if Shard 1 is present)
        local shard1_path="${strata_dir}/models/swift-IQ3_S/Swift-Qwen3.8-Flash-Next-GSQ-RCO-IQ3_S-00001-of-00002.gguf"
        if [[ -s "$shard1_path" && ! -s "${pack_dir}/native_experts.txt" ]]; then
            echo "=== Preparing Strata Native Pack via iq_pack.py ==="
            ensure_real_dir "$pack_dir"
            local iq_pack_tool="${STRATA_TOOLS_DIR:-/usr/share/strata/tools}/iq_pack.py"
            if [[ -f "$iq_pack_tool" ]]; then
                python3 "$iq_pack_tool" --gguf "$shard1_path" --out "$pack_dir"
            else
                echo "Warning: iq_pack.py not found at $iq_pack_tool; skipping native pack preparation." >&2
            fi
        fi

        # Custom Tokenizer Runtime Assembly
        local raw_tok_dir="${pack_dir}/tokenizer"
        local custom_tok_dir="${pack_dir}/tokenizer-custom"
        local template_src="${target_dir}/strata/Qwen3.8-chat_template.jinja"

        if [[ -d "$raw_tok_dir" && -f "${raw_tok_dir}/vocab.json" && -f "$template_src" ]]; then
            echo "=== Assembling Strata Custom Tokenizer Runtime ==="
            ensure_real_dir "$custom_tok_dir"
            for f in vocab.json merges.txt tokenizer.json token_type.json tokenizer_config.json; do
                if [[ -f "${raw_tok_dir}/$f" ]]; then
                    ln -sfn "../tokenizer/$f" "${custom_tok_dir}/$f"
                fi
            done
            # Link modified Jinja chat template
            ln -sfn "../../../Qwen3.8-chat_template.jinja" "${custom_tok_dir}/chat_template.jinja"

            # Create convenience symlink at strata_dir root
            ln -sfn "packs/swift-iq3_s/tokenizer-custom" "${strata_dir}/tok_runtime"
            echo "Custom tokenizer runtime assembled at ${custom_tok_dir} (symlinked as ${strata_dir}/tok_runtime)."
        fi
    fi

    # 10. Standalone DSpark Speculative Drafter (if requested without --strata-aux)
    if [[ "$download_dspark" == true && "$download_strata_aux" == false ]]; then
        echo "=== Acquiring Qwen3.8-Flash-Next DSpark Speculative Drafter ==="
        local dspark_dir="${strata_dir}/dspark"
        ensure_real_dir "$dspark_dir"

        acquire_file \
            "strata/swift15_iq3s/dspark/model.safetensors" \
            "https://huggingface.co/shadowpa0327/Qwen3.8-Flash-Next-DSpark/resolve/main/model.safetensors" \
            "${dspark_dir}/model.safetensors"

        acquire_file \
            "strata/swift15_iq3s/dspark/config.json" \
            "https://huggingface.co/shadowpa0327/Qwen3.8-Flash-Next-DSpark/resolve/main/config.json" \
            "${dspark_dir}/config.json"
    fi

    echo "=== All requested model downloads/conversions completed. ==="

}

main "$@"
