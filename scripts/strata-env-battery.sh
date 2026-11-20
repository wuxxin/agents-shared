#!/usr/bin/env bash
#
# Run the same Oracle A bench cell against several engine configurations by
# rewriting the env file per arm (the env file is the source of truth for both
# `install` and the launcher — process env alone is overridden by it).
#
# Needs an exclusive GPU window: stop local-chat-strata first. The script starts
# the generated launcher itself (no systemd; the user bus is unavailable in the
# sandbox) and restores the original env file on exit.
#
# One arm = env file edit + install + engine start + N bench cells. The first
# cell is discarded by default, because a cold engine reads ~7% low on decode.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENTS_SHARED="$(cd "${SCRIPT_DIR}/.." && pwd)"
LAUNCHER_SCRIPT="${AGENTS_SHARED}/assistants/local-chat-strata.sh"
SYSTEMD_USER_DIR="${XDG_CONFIG_HOME:-${HOME}/.config}/systemd/user"
ENV_FILE="${SYSTEMD_USER_DIR}/local-chat-strata.env"
LAUNCHER="${SYSTEMD_USER_DIR}/local-chat-strata-launcher.py"
CONFIG="${SYSTEMD_USER_DIR}/local-chat-strata-config.json"
MODEL="${LCHAT_BATTERY_MODEL:-qwen3.8-flash-next}"
ENDPOINT="http://127.0.0.1:20080"

out_dir=""
arms="base,dflash2,dflash2-spec6"
runs=3
cells=2
readytimeout=900
bench_args=""
workload="bench"
park_args=""

usage() {
    cat <<EOF
Usage: $(basename "$0") [--out DIR] [--arms LIST] [--runs N] [--cells N] [--check]

Runs Oracle A bench cells against several engine configurations.

Options:
  --out DIR     Output folder (default: research/bench-results/<date>-env-battery)
  --arms LIST   Comma list: base, dflash2, dflash2-spec6, f16, spec6, mtp-spec6-minp45
  --runs N      Bench runs per cell (default 3)
  --cells N     Cells per arm, first discarded as warm-up (default 2)
  --bench-args  Extra omp bench args, e.g. "--detailed --par 4 --runs 2" (C1 load)
  --workload    bench (default) | parklab (Oracle D; arms notier|tier|tier-prefix|tier-par2; --cells = repeats)
  --park-args   Extra park-lab args, e.g. "--k 9" — K must exceed the 8 cache slots to force eviction
  --check       Verify preconditions and print the plan, then exit
  -h, --help    Show this message

The env file (${ENV_FILE}) is rewritten per arm and restored on exit.
EOF
}

check_only=0
while [[ $# -gt 0 ]]; do
    case "$1" in
    --out)
        out_dir="${2:?}"
        shift 2
        ;;
    --arms)
        arms="${2:?}"
        shift 2
        ;;
    --runs)
        runs="${2:?}"
        shift 2
        ;;
    --cells)
        cells="${2:?}"
        shift 2
        ;;
    --park-args)
        park_args="${2:?}"
        shift 2
        ;;
    --workload)
        workload="${2:?}"
        shift 2
        ;;
    --bench-args)
        bench_args="${2:?}"
        shift 2
        ;;
    --check)
        check_only=1
        shift
        ;;
    -h | --help)
        usage
        exit 0
        ;;
    *)
        echo "Unknown argument: $1" >&2
        usage >&2
        exit 2
        ;;
    esac
done

date_utc="$(date -u +%Y-%m-%d)"
if [[ -z "$out_dir" ]]; then
    out_dir="${AGENTS_SHARED}/research/bench-results/${date_utc}-env-battery"
fi
mkdir -p "$out_dir/raw"

arm_keys() {
    case "$1" in
    base) echo "" ;;
    dflash2) echo "LCHAT_STRATA_DRAFTING=dflash2" ;;
    dflash2-spec6) echo "LCHAT_STRATA_DRAFTING=dflash2 LCHAT_STRATA_SPEC=6" ;;
    f16) echo "STRATA_HIP_PROMPT_F16=1" ;;
    spec6) echo "LCHAT_STRATA_SPEC=6" ;;
    mtp-spec6-minp45) echo "LCHAT_STRATA_SPEC=6 LCHAT_STRATA_SPEC_MIN_P=0.45" ;;
    parallel2) echo "LCHAT_STRATA_PARALLEL=2" ;;
    # Oracle D (park-lab) arms: the config is per mechanism, the park arm is per request shape
    notier) echo "LCHAT_STRATA_CONV_SPILL_DIR=" ;;
    tier) echo "" ;;
    tier-par2) echo "LCHAT_STRATA_PARALLEL=2" ;;
    tier-prefix) echo "" ;;
    *) echo "UNKNOWN" ;;
    esac
}

port_busy() {
    ss -ltn 2>/dev/null | grep -q '127.0.0.1:20080 '
}

# Set KEY=VAL pairs in the env file: replace an existing assignment or append.
apply_overrides() {
    local file="$1"
    shift || true
    local pair key val
    for pair in "$@"; do
        key="${pair%%=*}"
        val="${pair#*=}"
        if grep -qE "^${key}=" "$file"; then
            python3 - "$file" "$key" "$val" <<'PY'
import re, sys
path, key, val = sys.argv[1], sys.argv[2], sys.argv[3]
with open(path, encoding="utf-8") as fh:
    lines = fh.readlines()
out = []
for line in lines:
    if re.match(rf"^{re.escape(key)}=", line):
        out.append(f'{key}="{val}"\n')
    else:
        out.append(line)
with open(path, "w", encoding="utf-8") as fh:
    fh.writelines(out)
PY
        else
            printf '%s="%s"\n' "$key" "$val" >>"$file"
        fi
    done
}

config_summary() {
    python3 - "$CONFIG" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
a = d["args"]
def val(flag):
    return a[a.index(flag) + 1] if flag in a else "-"
print(f'drafting={d["drafting"]} spec={val("--spec")} draft_model={val("--draft-model")} f16={"yes" if "1" in str(a) and "PROMPT_F16" in str(a) else "env-only"}')
PY
}

plan() {
    echo "launcher script: ${LAUNCHER_SCRIPT}"
    echo "env file       : ${ENV_FILE}"
    echo "model          : ${MODEL} (Oracle A --profile generation --runs ${runs})"
    echo "cells per arm  : ${cells} (first discarded as warm-up)"
    echo "output         : ${out_dir}"
    local arm key
    for arm in ${arms//,/ }; do
        key="$(arm_keys "$arm")"
        if [[ "$key" == "UNKNOWN" ]]; then
            echo "  ERROR unknown arm: ${arm}" >&2
            return 1
        fi
        echo "  arm ${arm}: ${key:-<no overrides>}"
    done
}

plan || exit 2

[[ -f "$LAUNCHER_SCRIPT" ]] || {
    echo "missing ${LAUNCHER_SCRIPT}" >&2
    exit 2
}
[[ -f "$ENV_FILE" ]] || {
    echo "missing env file ${ENV_FILE} (run local-chat-strata.sh install)" >&2
    exit 2
}
if port_busy; then
    echo "Port 20080 is busy — stop local-chat-strata before running the battery." >&2
    exit 2
fi

if [[ "$check_only" == "1" ]]; then
    echo "preconditions OK (port free, env file present)"
    exit 0
fi

env_backup="${out_dir}/env-original.env"
cp -p "$ENV_FILE" "$env_backup"
restore_env() {
    cp -p "$env_backup" "$ENV_FILE"
    "$LAUNCHER_SCRIPT" install --no-start >/dev/null 2>&1 || true
    echo "env file restored from ${env_backup}"
}
trap restore_env EXIT

tsv="${out_dir}/battery.tsv"
[[ -f "$tsv" ]] || printf 'arm\tcell\tconfig\tttft_p50\tgen_rates\tprefill_reads\n' >"$tsv"

wait_ready() {
    local pid="$1" deadline=$((SECONDS + readytimeout))
    while ((SECONDS < deadline)); do
        if curl -sf --max-time 2 "${ENDPOINT}/v1/models" >/dev/null 2>&1; then
            return 0
        fi
        if ! kill -0 "$pid" 2>/dev/null; then
            return 1
        fi
        sleep 2
    done
    return 1
}

stop_engine() {
    local pid="$1"
    kill "$pid" 2>/dev/null || true
    for _ in $(seq 1 20); do
        port_busy || break
        sleep 1
    done
    pkill -f '/usr/lib/strata/engine/strata --serve' 2>/dev/null || true
    sleep 2
}

park_arm() {
    case "$1" in
    notier) echo A ;;
    tier) echo B ;;
    tier-par2) echo C ;;
    tier-prefix) echo D ;;
    *) echo "" ;;
    esac
}

for arm in ${arms//,/ }; do
    keys="$(arm_keys "$arm")"
    log="${out_dir}/raw/engine-${arm}.log"
    echo "=== arm ${arm} (${keys:-no overrides})"
    cp -p "$env_backup" "$ENV_FILE"
    # shellcheck disable=SC2086
    apply_overrides "$ENV_FILE" $keys
    if ! "$LAUNCHER_SCRIPT" install --no-start >"${out_dir}/raw/install-${arm}.log" 2>&1; then
        echo "  install failed for arm ${arm}; see raw/install-${arm}.log" >&2
        continue
    fi
    summary="$(config_summary)"
    echo "  config: ${summary}"

    python3 "$LAUNCHER" >"$log" 2>&1 &
    launcher_pid=$!
    if ! wait_ready "$launcher_pid"; then
        echo "  engine did not become ready; see ${log}" >&2
        stop_engine "$launcher_pid"
        printf '%s\t0\t%s\tNOT_READY\t-\t-\n' "$arm" "$summary" >>"$tsv"
        continue
    fi
    echo "  engine ready (pid ${launcher_pid})"

    if [[ "$workload" == "parklab" ]]; then
        pa="$(park_arm "$arm")"
        if [[ -z "$pa" ]]; then
            echo "  parklab workload needs arms notier|tier|tier-par2 (got ${arm})" >&2
            stop_engine "$launcher_pid"
            continue
        fi
        echo "  park-lab arm ${pa} (repeat ${cells}) ..."
        # shellcheck disable=SC2086
        python3 "${SCRIPT_DIR}/strata-park-lab.py" --arm "$pa" --repeat "$cells" \
            --out "${out_dir}/park-${arm}" --yes --base-url "${ENDPOINT}/v1" ${park_args} \
            >"${out_dir}/raw/park-${arm}.txt" 2>&1 || true
        pc="$(grep -aoE 'reuse[^,;]{0,40}|TTFT[^,;]{0,30}|gate[^,;]{0,30}' "${out_dir}/raw/park-${arm}.txt" | tail -4 | tr '\n' ' ' || true)"
        printf '%s\t%s\t%s\t%s\t-\t%s\n' "$arm" "$cells" "$summary" "${pc:-see raw}" "parklab-${pa}" >>"$tsv"
        echo "    ${pc:-see raw/park-${arm}.txt}"
        stop_engine "$launcher_pid"
        continue
    fi

    for ((c = 1; c <= cells; c++)); do
        cellout="${out_dir}/raw/bench-${arm}-cell${c}.txt"
        echo "  cell ${c}/${cells} ..."
        # --detailed is mutually exclusive with --profile (bench validates this),
        # and it carries its own --runs, so only use --profile for plain cells.
        # shellcheck disable=SC2086
        if [[ "$bench_args" == *--detailed* ]]; then
            omp bench "$MODEL" ${bench_args} >"$cellout" 2>&1 || true
        else
            omp bench "$MODEL" --profile generation --runs "$runs" ${bench_args} >"$cellout" 2>&1 || true
        fi
        rates="$(perl -pe 's/\e\[[0-9;]*[A-Za-z]//g; s/\r/\n/g' "$cellout" | grep -aoE 'gen [0-9.]+/s' | grep -oE '[0-9.]+' | sort -n | tr '\n' ' ' || true)"
        if [[ -z "$rates" ]]; then
            # --detailed output: aggregate tok/s per phase
            rates="$(perl -pe 's/\e\[[0-9;]*[A-Za-z]//g; s/\r/\n/g' "$cellout" | grep -aoE 'aggregate[^0-9]*[0-9.]+|tok/s [0-9.]+' | grep -oE '[0-9.]+' | sort -n | tr '\n' ' ' || true)"
        fi
        ttft="$(perl -pe 's/\e\[[0-9;]*[A-Za-z]//g; s/\r/\n/g' "$cellout" | grep -aoE 'TTFT p50[[:space:]]+[0-9.]+m?s' | tail -1 | grep -oE '[0-9.]+m?s' || true)"
        prefill="$(grep -oE 'read in [0-9]+ ms \([0-9.]+ tok/s\)' "$log" | tail -3 | tr '\n' '; ')"
        printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$arm" "$c" "$summary" "${ttft:-?}" "${rates:-?}" "${prefill:-none}" >>"$tsv"
        printf '    decode: %s tok/s | TTFT p50 %s\n' "${rates:-?}" "${ttft:-?}"
    done

    stop_engine "$launcher_pid"
done

echo
echo "Results: ${tsv}"
