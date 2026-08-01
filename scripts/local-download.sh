#!/usr/bin/env bash

set -euo pipefail

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
  -h, --help        Show this help message and exit

Examples:
  $(basename "$0") /data/public/machine-learning/models --all
  $(basename "$0") ./my-models --llm --embedding
EOF
}

acquire_file() {
    local _cache_subpath="$1"
    local download_url="$2"
    local target_path="$3"
    local target_subdir
    target_subdir="$(dirname "$target_path")"

    mkdir -p "$target_subdir"

    # Skip if exists and is non-empty
    if [[ -s "$target_path" ]]; then
        echo "File already exists and is non-empty: $target_path (Skipping)"
        return 0
    fi

    # Download from URL
    echo "Acquiring from remote: $download_url"

    # Try hf download if applicable
    if command -v hf &>/dev/null && [[ "$download_url" =~ huggingface\.co ]]; then
        # Check if URL matches HF resolve format
        if [[ "$download_url" =~ huggingface\.co/([^/]+/[^/]+)/resolve/[^/]+/(.+) ]]; then
            local repo_id="${BASH_REMATCH[1]}"
            local filename="${BASH_REMATCH[2]}"
            local temp_dir
            temp_dir="$(mktemp -d)"

            echo "Using 'hf download' for $repo_id / $filename..."
            if hf download "$repo_id" "$filename" --local-dir "$temp_dir"; then
                mv "${temp_dir}/${filename}" "$target_path"
                rm -rf "$temp_dir"
                echo "Successfully downloaded $filename."
                return 0
            fi
            rm -rf "$temp_dir"
        fi
    fi

    # Fallback to curl
    echo "Downloading via curl..."
    if curl -L --fail -o "$target_path" "$download_url"; then
        echo "Successfully downloaded via curl."
        return 0
    else
        echo "Error: Failed to download $download_url" >&2
        rm -f "$target_path"
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
    if ! llama-quantize "$temp_f16_gguf" "$target_path" Q4_K_M; then
        echo "Error: Quantization to Q4_K_M failed." >&2
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
        *)
            echo "Error: Unknown option '$1'" >&2
            show_help >&2
            exit 1
            ;;
        esac
    done

    if [[ "$download_all" == false && "$download_llm" == false && "$download_embedding" == false && "$download_reranker" == false && "$download_stt" == false && "$download_tts" == false && "$download_image" == false && "$download_completion" == false && "$download_benchmark" == false ]]; then
        echo "Error: No models or tasks specified. Please use --all or select specific models/tasks (--llm, --embedding, --reranker, --speech-to-text, --text-to-speech, --image, --completion, --benchmark-context)." >&2
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
            python3 "$(dirname "$0")/download-helper.py" merge-mtp \
                "${target_dir}/vision-text/Qwen3.6-35B-A3B-APEX-I-Compact.gguf" \
                "${target_dir}/vision-text/Qwen3.6-35B-A3B-MTP-ONLY.gguf" \
                "$mtp_target_path"
        fi

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

        # 1h. Download Agents-A1 APEX finetune (Qwen3.6-35B-A3B agent-optimized)
        acquire_file \
            "vision-text/Agents-A1-APEX-I-Compact.gguf" \
            "https://huggingface.co/mudler/Agents-A1-APEX-GGUF/resolve/main/Agents-A1-APEX-I-Compact.gguf" \
            "${target_dir}/vision-text/Agents-A1-APEX-I-Compact.gguf"
        acquire_file \
            "vision-text/Agents-A1-APEX-I-Compact.mmproj.gguf" \
            "https://huggingface.co/mudler/Agents-A1-APEX-GGUF/resolve/main/mmproj.gguf" \
            "${target_dir}/vision-text/Agents-A1-APEX-I-Compact.mmproj.gguf"

        # 1i. Download full Hugging Face weights for MLC compilation (Qwen3.6-35B-A3B)
        echo "Downloading full Hugging Face weights for MLC (Qwen3.6-35B-A3B)..."
        mkdir -p "${target_dir}/vision-text/Qwen3.6-35B-A3B"
        if command -v hf &>/dev/null; then
            hf download Qwen/Qwen3.6-35B-A3B --local-dir "${target_dir}/vision-text/Qwen3.6-35B-A3B"
        else
            echo "Warning: 'hf' CLI not found. Skipping download of HF safetensors model." >&2
        fi

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

        # Download HF PyTorch/Safetensors weights for TEI (if hf tool is available)
        echo "Downloading full Hugging Face weights for TEI (Qwen3-Embedding-0.6B)..."
        mkdir -p "${target_dir}/embedding/Qwen3-Embedding-0.6B"
        if command -v hf &>/dev/null; then
            hf download Qwen/Qwen3-Embedding-0.6B --local-dir "${target_dir}/embedding/Qwen3-Embedding-0.6B"
        else
            echo "Warning: 'hf' CLI not found. Skipping download of HF safetensors model." >&2
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

        # Download HF PyTorch/Safetensors weights for TEI (if hf tool is available)
        echo "Downloading full Hugging Face weights for TEI (Qwen3-Reranker-0.6B)..."
        mkdir -p "${target_dir}/reranker/Qwen3-Reranker-0.6B"
        if command -v hf &>/dev/null; then
            hf download Qwen/Qwen3-Reranker-0.6B --local-dir "${target_dir}/reranker/Qwen3-Reranker-0.6B"
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

        # NOTE: jina-reranker-v3 safetensors kept for TEI reference; TEI engine is abandoned,
        # the llama.cpp path uses the GGUF + projector above instead.
        echo "Downloading full Hugging Face weights for TEI (jina-reranker-v3) [reference only]..."
        mkdir -p "${target_dir}/reranker/jina-reranker-v3"
        if command -v hf &>/dev/null; then
            hf download jinaai/jina-reranker-v3 --local-dir "${target_dir}/reranker/jina-reranker-v3"
        else
            echo "Warning: 'hf' CLI not found. Skipping download of HF safetensors model." >&2
        fi

        echo "Downloading essential TEI files for ettin-reranker-400m-v1 (~1.6 GB, skipping ONNX/OpenVINO bloat)..."
        mkdir -p "${target_dir}/reranker/ettin-reranker-400m-v1"
        python3 -c '
import sys
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id="cross-encoder/ettin-reranker-400m-v1",
    local_dir=sys.argv[1],
    ignore_patterns=["onnx/**", "openvino/**"],
)
' "${target_dir}/reranker/ettin-reranker-400m-v1" || {
            echo "Warning: snapshot_download failed. The model repo is ~10.67 GB due to ONNX/OpenVINO exports." >&2
            echo "  Try: hf download cross-encoder/ettin-reranker-400m-v1 --local-dir ${target_dir}/reranker/ettin-reranker-400m-v1" >&2
        }

        echo "Downloading essential files for ettin-reranker-150m-v1 (~596 MB, skipping ONNX/OpenVINO bloat)..."
        # No GGUF exists for 150m/400m ettin (SentTrans head, not standard BertForSeqClass)
        # Download safetensors only for potential future GGUF conversion or TEI fallback
        mkdir -p "${target_dir}/reranker/ettin-reranker-150m-v1"
        python3 -c '
import sys
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id="cross-encoder/ettin-reranker-150m-v1",
    local_dir=sys.argv[1],
    ignore_patterns=["onnx/**", "openvino/**"],
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
        # NOTE: jina-reranker-v3.patch is applied in both libggml-git-hip and tei-rocm,
        # but neither produces working reranking in practice (embedding path produces bad scores,
        # TEI Python backend can't load JinaForRanking). Downloaded for future use when fixes land.
        acquire_file \
            "reranker/jina-reranker-v3.5-Q4_K_M.gguf" \
            "https://huggingface.co/jinaai/jina-reranker-v3.5-GGUF/resolve/main/jina-reranker-v3.5-Q4_K_M.gguf" \
            "${target_dir}/reranker/jina-reranker-v3.5-Q4_K_M.gguf"

        # --- Additional Reranker Models (TEI / safetensors only, no GGUF) ---

        # LAMAR-600m (TEI safetensors) — BEST multilingual under 5GB, MIT license
        # 600M params, 8K ctx, XLM-RoBERTa cross-encoder, 51 langs including German
        # MIRACL: 69.49, XQuAD nDCG@10: 98.59, German: ✅✅ (excellent)
        # License: MIT
        # ~1.2 GB fp16 safetensors, ~3.5 GB VRAM at full precision
        # NOTE: TEI-only (no GGUF). Serve via: text-embeddings-router --model-id <path>
        if command -v hf &>/dev/null; then
            echo "Downloading LAMAR-600m (TEI safetensors, MIT license, excellent German)..."
            mkdir -p "${target_dir}/reranker/LAMAR-600m"
            hf download nlpai-lab/LAMAR-600m --local-dir "${target_dir}/reranker/LAMAR-600m"
        else
            echo "Warning: 'hf' CLI not found. Skipping LAMAR-600m download." >&2
        fi

        # KaLM-Reranker-V1-Nano (TEI safetensors) — Ultra-lightweight, 128K ctx, Apache 2.0
        # 270M params, 128K ctx, encoder-decoder (T5Gemma2), FBNL architecture
        # Apache 2.0 license
        # ~600 MB fp16 safetensors, ~1.5 GB VRAM
        # NOTE: TEI/Sentence Transformers only (no GGUF). Requires trust_remote_code=True.
        if command -v hf &>/dev/null; then
            echo "Downloading KaLM-Reranker-V1-Nano (TEI safetensors, Apache 2.0, 128K ctx)..."
            mkdir -p "${target_dir}/reranker/KaLM-Reranker-V1-Nano"
            hf download KaLM-Embedding/KaLM-Reranker-V1-Nano --local-dir "${target_dir}/reranker/KaLM-Reranker-V1-Nano"
        else
            echo "Warning: 'hf' CLI not found. Skipping KaLM-Reranker-V1-Nano download." >&2
        fi

        # mxbai-rerank-base-v2 (TEI safetensors) — 109 languages, 32K ctx, Apache 2.0
        # 494M params, 32K ctx, causal decoder (Qwen2-0.5B), GRPO-trained
        # BEIR: 55.57, German: ✅
        # Apache 2.0 license
        # ~1.0 GB fp16 safetensors, ~2.5 GB VRAM
        # NOTE: TEI compatible (tagged text-embeddings-inference). No official GGUF.
        # GGUF conversion is feasible (standard Qwen2 decoder).
        if command -v hf &>/dev/null; then
            echo "Downloading mxbai-rerank-base-v2 (TEI safetensors, Apache 2.0, 32K ctx)..."
            mkdir -p "${target_dir}/reranker/mxbai-rerank-base-v2"
            hf download mixedbread-ai/mxbai-rerank-base-v2 --local-dir "${target_dir}/reranker/mxbai-rerank-base-v2"
        else
            echo "Warning: 'hf' CLI not found. Skipping mxbai-rerank-base-v2 download." >&2
        fi
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
        # 5a. CustomVoice 0.6B
        acquire_file \
            "text-to-speech/Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf" \
            "https://huggingface.co/khimaros/Qwen3-TTS-12Hz-0.6B-CustomVoice-GGUF/resolve/main/Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf" \
            "${target_dir}/text-to-speech/Qwen3-TTS-12Hz-0.6B-CustomVoice-Q8_0.gguf"

        # 5b. Tokenizer
        acquire_file \
            "text-to-speech/Qwen3-TTS-Tokenizer-12Hz-F16.gguf" \
            "https://huggingface.co/khimaros/Qwen3-TTS-Tokenizer-12Hz-GGUF/resolve/main/Qwen3-TTS-Tokenizer-12Hz-F16.gguf" \
            "${target_dir}/text-to-speech/Qwen3-TTS-Tokenizer-12Hz-F16.gguf"
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

    echo "=== All requested model downloads/conversions completed. ==="

}

main "$@"
