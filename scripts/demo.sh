#!/usr/bin/env bash
# One-command demo: run, then show the trace it produced.
set -Eeuo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH=src
python3 -m foundry run --case "${1:-evals/cases/01-refund.json}" --mock
echo
python3 -m foundry trace --last
