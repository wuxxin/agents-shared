#!/usr/bin/env bash
set -euo pipefail

# copy-config-to-target.sh - Copies OpenCode sandbox template files to target config directory

usage() {
    cat <<'EOF'
Usage: ./copy-config-to-target.sh <TARGET_DIR> --yes

Copies all OpenCode template files, plugins, skills, hindsight-banks, and README.md
to the specified target configuration directory.

Mandatory Arguments & Flags:
  TARGET_DIR   Target directory path (e.g., $HOME/.config/opencode)
  -y, --yes    Mandatory confirmation flag for execution

Flags:
  -h, --help   Show this help message and exit

Examples:
  ./copy-config-to-target.sh $HOME/.config/opencode --yes
  ./copy-config-to-target.sh /tmp/opencode-test -y
EOF
}

CONFIRMED="false"
TARGET_DIR=""

while [ "${#}" -gt 0 ]; do
    case "${1}" in
    -y | --yes)
        CONFIRMED="true"
        shift
        ;;
    -h | --help)
        usage
        exit 0
        ;;
    -*)
        echo "Error: Unknown option '${1}'" >&2
        echo "" >&2
        usage
        exit 1
        ;;
    *)
        if [ -z "${TARGET_DIR}" ]; then
            TARGET_DIR="${1}"
        fi
        shift
        ;;
    esac
done

if [ -z "${TARGET_DIR}" ]; then
    echo "Error: Missing mandatory TARGET_DIR parameter." >&2
    echo "" >&2
    usage
    exit 1
fi

if [ "${CONFIRMED}" != "true" ]; then
    echo "Error: Missing mandatory '--yes' / '-y' confirmation flag." >&2
    echo "" >&2
    usage
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Copying OpenCode template configuration to: ${TARGET_DIR} ==="
mkdir -p "${TARGET_DIR}"

# Copy root configuration files and documentation
for file in opencode.json package.json tui.json oh-my-opencode-slim.jsonc README.md copy-config-to-target.sh update-memory-banks.sh patch-hindsight-tags.js; do
    if [ -f "${SCRIPT_DIR}/${file}" ]; then
        cp "${SCRIPT_DIR}/${file}" "${TARGET_DIR}/${file}"
        echo "  Copied ${file}"
    fi
done

# Copy skills directory
if [ -d "${SCRIPT_DIR}/skills" ]; then
    mkdir -p "${TARGET_DIR}/skills"
    cp -r "${SCRIPT_DIR}/skills/"* "${TARGET_DIR}/skills/"
    echo "  Copied skills/"
fi

# Copy hindsight-banks directory
if [ -d "${SCRIPT_DIR}/hindsight-banks" ]; then
    mkdir -p "${TARGET_DIR}/hindsight-banks"
    cp -r "${SCRIPT_DIR}/hindsight-banks/"* "${TARGET_DIR}/hindsight-banks/"
    echo "  Copied hindsight-banks/"
fi

echo "=== Copy complete ==="
