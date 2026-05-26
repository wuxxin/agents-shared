#!/usr/bin/env bash
# local-inference.sh - Hub orchestration command for local inference services
#
# Usage: local-inference.sh <command> [args...]
#
# Manages local-chat, local-embeddings, and local-rerank services collectively.
#
# ---------------------------------------------------------------------------

set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

SERVICES=("local-chat" "local-embeddings" "local-rerank")

usage() {
    echo "Usage: $0 <command> [args...]"
    echo "Commands:"
    echo "  install [--no-start] - Install all inference services"
    echo "  uninstall            - Uninstall all inference services"
    echo "  start                - Start all inference services"
    echo "  stop                 - Stop all inference services"
    echo "  restart              - Restart all inference services"
    echo "  status               - View status of all inference services"
    echo "  enable               - Enable all inference services on boot"
    echo "  disable              - Disable all inference services on boot"
    echo "  test                 - Run API validation tests on all inference services"
    echo "  logs                 - Tail/View logs for all inference services"
    echo "  edit                 - Interactively choose an environment file to edit"
}

if [ $# -lt 1 ]; then
    usage
    exit 1
fi

COMMAND="$1"
shift

case "$COMMAND" in
install | uninstall | start | stop | restart | status | enable | disable | test)
    for svc in "${SERVICES[@]}"; do
        echo "=== [${svc}] Execution: ${COMMAND} ==="
        "$DIR/${svc}.sh" "${COMMAND}" "$@"
        echo ""
    done
    ;;
logs)
    # Tail/View logs for all services simultaneously
    log_args=()
    for svc in "${SERVICES[@]}"; do
        log_args+=("-u" "${svc}.service")
    done
    journalctl --user "${log_args[@]}" "$@"
    ;;
edit)
    echo "Select the environment file you want to edit:"
    idx=1
    for svc in "${SERVICES[@]}"; do
        echo "  ${idx}) ${svc}.env"
        idx=$((idx + 1))
    done
    read -r -p "Enter choice [1-$((idx - 1))]: " choice
    if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -lt "$idx" ]; then
        target_svc="${SERVICES[$((choice - 1))]}"
        echo "Editing ${target_svc}.env..."
        "$DIR/${target_svc}.sh" edit
    else
        echo "Invalid choice."
        exit 1
    fi
    ;;
*)
    echo "Unknown command: $COMMAND"
    usage
    exit 1
    ;;
esac
