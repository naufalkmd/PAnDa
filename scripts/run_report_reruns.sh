#!/usr/bin/env bash
# Reruns for the report (docs/report_checklist.md, part E). Run from the repository root on the GPU machine:
#   bash scripts/run_report_reruns.sh            # R1 then R2
#   bash scripts/run_report_reruns.sh r1         # only R1: three fresh 50-question subsets (exp16)
#   bash scripts/run_report_reruns.sh r2         # only R2: all 817 questions (exp11, exp12, exp13)
# Extra arguments after the first are passed to every run, e.g. --local-files-only.
# Outputs go to results/experiments/<exp>/runs/<run_id>/; existing runs are not touched.
set -euo pipefail

PY="${PYTHON:-./.venv/bin/python}"
WHICH="${1:-all}"
shift || true
EXP=results/experiments

r1() {
  for run in run_03_seed_202 run_04_seed_303 run_05_seed_404; do
    echo "=== R1 exp16 $run"
    "$PY" "$EXP/exp16_mc_persistence_seed_sweep/run_experiment.py" \
      --run-id "$run" --mode subset --truthfulqa-limit 50 "$@"
  done
}

r2() {
  # --truthfulqa-limit all is required: the runners default to 50 questions even with --mode full.
  for exp in exp11_core_decoder_comparison exp12_state_persistence_diagnostics exp13_logit_filter_factorial; do
    echo "=== R2 $exp run_02_full"
    "$PY" "$EXP/$exp/run_experiment.py" \
      --run-id run_02_full --mode full --truthfulqa-limit all "$@"
  done
}

case "$WHICH" in
  r1) r1 "$@" ;;
  r2) r2 "$@" ;;
  all) r1 "$@"; r2 "$@" ;;
  *) echo "usage: $0 [all|r1|r2] [extra args]" >&2; exit 2 ;;
esac

echo "Done. Next: python scripts/summarise_runs.py, then commit and push results/experiments/*/runs/."
