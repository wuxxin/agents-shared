#!/usr/bin/env bash

set -euo pipefail

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

# Check arguments
if [[ $# -lt 1 ]]; then
    show_help
    exit 1
fi

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
fi

# 2. Embedding

if [[ "$download_embedding" == true ]]; then
    echo "=== Acquiring Embedding Model ==="
    acquire_file \
        "embedding/Qwen3-Embedding-0.6B-Q8_0.gguf" \
        "https://huggingface.co/Qwen/Qwen3-Embedding-0.6B-GGUF/resolve/main/Qwen3-Embedding-0.6B-Q8_0.gguf" \
        "${target_dir}/embedding/Qwen3-Embedding-0.6B-Q8_0.gguf"

    # Download HF PyTorch/Safetensors weights for TEI (if hf tool is available)
    echo "Downloading full Hugging Face weights for TEI (Qwen3-Embedding-0.6B)..."
    mkdir -p "${target_dir}/embedding/Qwen3-Embedding-0.6B"
    if command -v hf &>/dev/null; then
        hf download Qwen/Qwen3-Embedding-0.6B --local-dir "${target_dir}/embedding/Qwen3-Embedding-0.6B"
    else
        echo "Warning: 'hf' CLI not found. Skipping download of HF safetensors model." >&2
    fi

    echo "Downloading full Hugging Face weights for TEI (pplx-embed-context-v1-0.6b)..."
    mkdir -p "${target_dir}/embedding/pplx-embed-context-v1-0.6b"
    if command -v hf &>/dev/null; then
        hf download perplexity-ai/pplx-embed-context-v1-0.6b --local-dir "${target_dir}/embedding/pplx-embed-context-v1-0.6b"
    else
        echo "Warning: 'hf' CLI not found. Skipping download of HF safetensors model." >&2
    fi
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

    echo "Downloading full Hugging Face weights for TEI (jina-reranker-v3)..."
    mkdir -p "${target_dir}/reranker/jina-reranker-v3"
    if command -v hf &>/dev/null; then
        hf download jinaai/jina-reranker-v3 --local-dir "${target_dir}/reranker/jina-reranker-v3"
    else
        echo "Warning: 'hf' CLI not found. Skipping download of HF safetensors model." >&2
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
