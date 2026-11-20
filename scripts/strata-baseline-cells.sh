#!/usr/bin/env bash
# Capture paired strata benchmark cells (strata-tuning.md §12.7 Oracles A/B) for one
# engine build, with journal slices and a README skeleton. Run it from an omp session
# whose model is NOT the local model under test, with Pulse/hooks/extensions off.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
URL="http://127.0.0.1:20080"
MODEL="qwen3.8-flash-next"
CELLS="A,B"
OUT=""
BACKGROUND="unrecorded - state which services were running"
FORCE=0

usage() {
    cat <<'USAGE'
usage: strata-baseline-cells.sh [--out NAME] [--cells A,B] [--background TEXT] [--force]
  --out NAME         bench-results subdirectory (default: <UTC-date>-gfx1100-<engine>)
  --cells LIST       A = generation decode cell, B = deep-context cold-prefill cell
  --background TEXT  what was running during the run (recorded verbatim in README)
  --force            re-run cells whose output already exists
USAGE
}

while [[ $# -gt 0 ]]; do
    case "$1" in
    --out)
        OUT="$2"
        shift 2
        ;;
    --cells)
        CELLS="$2"
        shift 2
        ;;
    --background)
        BACKGROUND="$2"
        shift 2
        ;;
    --force)
        FORCE=1
        shift
        ;;
    -h | --help)
        usage
        exit 0
        ;;
    *)
        echo "unknown argument: $1" >&2
        usage
        exit 2
        ;;
    esac
done

status_json="$(curl -s --max-time 15 "$URL/v1/status")"
engine="$(printf '%s' "$status_json" | jq -r '.engine // "unknown"')"
gpu="$(printf '%s' "$status_json" | jq -r '.machine.gpu | "\(.name // "?") \(.total_mib // "?")MiB"')"
date_tag="$(date -u +%F)"
OUT="${OUT:-${date_tag}-gfx1100-${engine}}"
DIR="$REPO_ROOT/research/bench-results/$OUT"
RAW="$DIR/raw"
mkdir -p "$RAW"

printf '%s\n' "$status_json" >"$RAW/status.json"
journalctl --user -u local-chat-strata.service --no-pager --since -48h >"$RAW/service-48h.log" 2>/dev/null || true
{
    echo "generator_sha256: $(sha256sum "$REPO_ROOT/assistants/local-chat-strata.sh" | cut -d' ' -f1)"
    echo "agents_shared_head: $(git -C "$REPO_ROOT" rev-parse --short HEAD)"
    echo "agents_shared_dirty: $(git -C "$REPO_ROOT" status --porcelain assistants/local-chat-strata.sh | wc -l) entries"
} >"$RAW/config-identity.txt"

run_cell() {
    local id="$1" flags="$2" out="$3"
    if [[ -s "$RAW/$out" && $FORCE -eq 0 ]]; then
        echo "skipping $id: $RAW/$out exists (use --force)"
        return 0
    fi
    local start rc duration
    start="$(date -Is)"
    echo "== cell $id: omp bench $MODEL $flags ($start)"
    local t0 t1
    t0="$(date +%s)"
    set +e
    # shellcheck disable=SC2086  # flags is an intentional argument list
    omp bench "$MODEL" $flags >"$RAW/$out" 2>&1
    rc=$?
    set -e
    t1="$(date +%s)"
    duration=$((t1 - t0))
    journalctl --user -u local-chat-strata.service --no-pager --since "$start" >"$RAW/journal-$id.log" 2>/dev/null || true
    printf '%s\t%s\t%s\t%s\n' "$id" "$flags" "$rc" "$duration" >>"$RAW/cells.tsv"
    echo "== cell $id rc=$rc ${duration}s -> raw/$out"
}

[[ -s "$RAW/cells.tsv" ]] || : >"$RAW/cells.tsv"
if [[ ",$CELLS," == *",A,"* ]]; then
    run_cell A "--profile generation --runs 3" omp-bench-A.txt
fi
if [[ ",$CELLS," == *",B,"* ]]; then
    run_cell B "--profile mix --prefill-bytes 120000 --runs 6" omp-bench-B.txt
fi

{
    echo "# C0 cells: engine $engine (build captured $(date -u '+%F %R UTC'))"
    echo
    echo "Hardware: $gpu; model \`$MODEL\`; endpoint $URL"
    echo "Background during run: $BACKGROUND"
    cat "$RAW/config-identity.txt"
    echo
    echo "Commands (verbatim, strata-tuning.md §12.7):"
    echo '```'
    while IFS=$'\t' read -r id flags rc duration; do
        printf 'omp bench %s %s  # cell %s rc=%s %ss\n' "$MODEL" "$flags" "$id" "$rc" "$duration"
    done <"$RAW/cells.tsv"
    echo '```'
    echo
    echo "| Cell | Result lines (p50/summary from omp bench) |"
    echo "|---|---|"
    for pair in "A:omp-bench-A.txt" "B:omp-bench-B.txt"; do
        id="${pair%%:*}"
        file="${pair##*:}"
        if [[ -s "$RAW/$file" ]]; then
            summary="$(grep -iE 'p50|tok/s|TTFT' "$RAW/$file" | head -12 | awk '{ gsub(/\|/, "\\|"); printf "%s<br>", $0 }')"
            echo "| $id | ${summary:-(no p50 lines parsed; see raw/$file)} |"
        else
            echo "| $id | (not run) |"
        fi
    done
    echo
    echo "Raw captures: \`raw/omp-bench-*.txt\`, \`raw/journal-{A,B}.log\`, \`raw/status.json\`."
} >"$DIR/README.md"

echo "wrote $DIR/README.md"
