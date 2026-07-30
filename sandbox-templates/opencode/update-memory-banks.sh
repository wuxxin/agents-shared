#!/usr/bin/env bash
set -euo pipefail

# update-memory-banks.sh - Provisions and updates Hindsight memory bank configurations and mental models

usage() {
    cat <<'EOF'
Usage: ./update-memory-banks.sh <BANKS_DIR> <API_URL> --yes

Provisions and updates Hindsight memory bank configurations and Mental Models
via the specified Hindsight REST API URL.

Mandatory Arguments & Flags:
  BANKS_DIR   Directory containing bank .json files (e.g., $HOME/.config/opencode/hindsight-banks)
  API_URL     Hindsight API base URL (e.g., http://localhost:8888)
  -y, --yes    Mandatory confirmation flag for execution

Flags:
  -h, --help   Show this help message and exit

Examples:
  ./update-memory-banks.sh $HOME/.config/opencode/hindsight-banks http://localhost:8888 --yes
  ./update-memory-banks.sh ./hindsight-banks http://127.0.0.1:8888 -y
EOF
}

CONFIRMED="false"
BANKS_DIR=""
API_URL=""

while [ "${#}" -gt 0 ]; do
    case "${1}" in
        -y|--yes)
            CONFIRMED="true"
            shift
            ;;
        -h|--help)
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
            if [ -z "${BANKS_DIR}" ]; then
                BANKS_DIR="${1}"
            elif [ -z "${API_URL}" ]; then
                API_URL="${1}"
            fi
            shift
            ;;
    esac
done

if [ -z "${BANKS_DIR}" ]; then
    echo "Error: Missing mandatory BANKS_DIR parameter." >&2
    echo "" >&2
    usage
    exit 1
fi

if [ -z "${API_URL}" ]; then
    echo "Error: Missing mandatory API_URL parameter." >&2
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

echo "=== Provisioning Hindsight memory banks from: ${BANKS_DIR} ==="
echo "=== Hindsight API URL: ${API_URL} ==="

if [ ! -d "${BANKS_DIR}" ]; then
    echo "Error: Memory banks directory '${BANKS_DIR}' does not exist." >&2
    exit 1
fi

shopt -s nullglob
bank_files=("${BANKS_DIR}"/*.json)
shopt -u nullglob

if [ ${#bank_files[@]} -eq 0 ]; then
    echo "No .json bank files found in ${BANKS_DIR}"
    exit 0
fi

for bank_file in "${bank_files[@]}"; do
    bank_id="$(basename "${bank_file}" .json)"
    echo "=== Applying configuration for bank: ${bank_id} ==="

    # 1. Update Retain, Observations, and Reflect missions via 'updates' wrapper
    python3 -c "
import json, urllib.request
bank_file = '${bank_file}'
api_url = '${API_URL}'
bank_id = '${bank_id}'

data = json.load(open(bank_file))
bank = data.get('bank', {})
payload = json.dumps({
    'updates': {
        'retain_mission': bank.get('retain_mission'),
        'observations_mission': bank.get('observations_mission'),
        'reflect_mission': bank.get('reflect_mission'),
        'enable_observations': bank.get('enable_observations', True)
    }
}).encode('utf-8')

req = urllib.request.Request(
    f'{api_url}/v1/default/banks/{bank_id}/config',
    data=payload,
    headers={'Content-Type': 'application/json'},
    method='PATCH'
)
try:
    with urllib.request.urlopen(req) as resp:
        print(f'  Config status: {resp.status}')
except Exception as e:
    print(f'  Config status error: {e}')
"

    # 2. Register or update Mental Models idempotently (POST -> fallback to PATCH if exists)
    python3 -c "
import json, urllib.request
bank_file = '${bank_file}'
api_url = '${API_URL}'
bank_id = '${bank_id}'

data = json.load(open(bank_file))
for mm in data.get('mental_models', []):
    mm_id = mm.get('id')
    payload = json.dumps(mm).encode('utf-8')
    req = urllib.request.Request(
        f'{api_url}/v1/default/banks/{bank_id}/mental-models',
        data=payload,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    try:
        with urllib.request.urlopen(req) as resp:
            print(f'  Registered mental model {mm_id}: {resp.status}')
    except Exception:
        # Fallback to PATCH if already registered
        patch_req = urllib.request.Request(
            f'{api_url}/v1/default/banks/{bank_id}/mental-models/{mm_id}',
            data=payload,
            headers={'Content-Type': 'application/json'},
            method='PATCH'
        )
        try:
            with urllib.request.urlopen(patch_req) as patch_resp:
                print(f'  Updated mental model {mm_id}: {patch_resp.status}')
        except Exception as patch_e:
            print(f'  Mental model error ({mm_id}): {patch_e}')
"
done

echo "=== Hindsight memory bank update complete ==="
