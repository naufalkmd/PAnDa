#!/usr/bin/env bash
# Reruns for the report (docs/report_checklist.md, part E). Run from the repository root, in WSL, after
# `bash scripts/setup_env.sh`:
#   bash scripts/run_report_reruns.sh            # R1 then R2
#   bash scripts/run_report_reruns.sh r1         # R1: exp16 seeds 202, 303, 404 and a rerun of seed 101 (~3 h)
#   bash scripts/run_report_reruns.sh r2         # R2: exp19 held-out run, Qwen2.5-3B, all 817 questions (~19 h)
#   bash scripts/run_report_reruns.sh r4         # R4 (optional): exp19 on Gemma 3 4B (~27 h)
# Times are estimates from the June runs' per-question speed; the RTX 5070 may differ.
# Extra arguments after the first are passed to every run, e.g. --local-files-only.
# Outputs go to results/experiments/<exp>/runs/<run_id>/. exp19 refuses to overwrite a finished run.
set -euo pipefail

PY="${PYTHON:-./.venv/bin/python}"
# The first argument is the stage (all, r1, r2, r4); if it is an option (starts with "-") or missing, the stage
# is "all" and every argument is passed on to the runs.
WHICH="all"
if [ $# -gt 0 ] && [[ "$1" != -* ]]; then
  WHICH="$1"
  shift
fi
EXP=results/experiments

r1() {
  for run in run_03_seed_202 run_04_seed_303 run_05_seed_404 run_06_seed_101_rerun; do
    echo "=== R1 exp16 $run"
    "$PY" "$EXP/exp16_mc_persistence_seed_sweep/run_experiment.py" \
      --run-id "$run" --mode subset --truthfulqa-limit 50 "$@"
  done
}

r2() {
  echo "=== R2 exp19 run_01_qwen25_3b_full"
  "$PY" "$EXP/exp19_heldout_full/run_experiment.py" \
    --run-id run_01_qwen25_3b_full --mode full --truthfulqa-limit all "$@"
}

r4() {
  echo "=== R4 exp19 run_02_gemma3_4b_full"
  "$PY" "$EXP/exp19_heldout_full/run_experiment.py" \
    --run-id run_02_gemma3_4b_full --mode full --truthfulqa-limit all "$@"
}

case "$WHICH" in
  r1) r1 "$@" ;;
  r2) r2 "$@" ;;
  r4) r4 "$@" ;;
  all) r1 "$@"; r2 "$@" ;;
  *) echo "usage: $0 [all|r1|r2|r4] [extra args]" >&2; exit 2 ;;
esac

echo "Done. Next: python scripts/summarise_runs.py, then commit and push results/experiments/*/runs/."
