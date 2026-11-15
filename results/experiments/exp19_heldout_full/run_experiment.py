#!/usr/bin/env python3
"""Run exp19: the held-out evaluation on all 817 TruthfulQA questions.

One run with only the decoders the report needs, so each comparison is paired on the same questions and no
decoder is evaluated twice:

- main comparison: the base model, DoLa in two configurations (its own multiple-choice evaluation settings, and
  the generation settings the development runs used), FAnDa (premature layer selected once per question);
- 2 x 2 factorial with DoLa's layer selection: log-probability vs raw-logit difference x adaptive plausibility
  constraint on / off. The raw-logit, constraint-off cell is left out: without the constraint it gives the same
  scores as the log-probability cell by construction (see exp13);
- selection interval k = 1 and k = 4 (FAnDa is k = infinity).

The report's held-out scores are this run with the 50 development questions removed
(`scripts/paired_tests.py --exclude-questions-of <a development run>`).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


EXPERIMENTS_ROOT = Path(__file__).resolve().parents[1]
if str(EXPERIMENTS_ROOT) not in sys.path:
    sys.path.insert(0, str(EXPERIMENTS_ROOT))

from common import build_evaluator_args, read_run_matrix, run_truthfulqa_suite


EXPERIMENT_NAME = "exp19_heldout_full"
EXPERIMENT_DIR = Path(__file__).resolve().parent
RUN_MATRIX_PATH = EXPERIMENT_DIR / "run_matrix.csv"
RUNS_DIR = EXPERIMENT_DIR / "runs"
EXP19_DECODER_NAMES = (
    "pure_greedy",            # base model log-likelihood (no contrast)
    "dola_mc_reference",      # DoLa as in its own TruthfulQA-MC evaluation (no constraint, no renormalisation, late layers)
    "dola",                   # DoLa with its generation settings (constraint on, renormalised), early layers
    "fanda_frozen",           # FAnDa: premature layer selected once per question (k = infinity)
    "exp13_logprob_top",      # factorial: log-probability difference, constraint on (DoLa through the factorial code)
    "exp13_logprob_no_top",   # factorial: log-probability difference, constraint off
    "exp13_logit_top",        # factorial: raw-logit difference, constraint on
    "fanda_update1",          # FAnDa score, premature layer re-selected at every token (k = 1)
    "fanda_update4",          # FAnDa score, re-selected every 4 tokens (k = 4)
)


def parse_args():
    parser = argparse.ArgumentParser(description="Run exp19, the held-out evaluation on all TruthfulQA questions.")
    parser.add_argument("--model-name", default="Qwen/Qwen2.5-3B-Instruct",
                        help="used when the run row has no model_name")
    parser.add_argument("--mode", choices=("sanity", "subset", "full"), default="full")
    parser.add_argument("--truthfulqa-limit", type=str, default="all")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--progress-every", type=int, default=1)
    parser.add_argument("--local-files-only", action="store_true")
    parser.add_argument("--no-chat-template", action="store_true")
    parser.add_argument("--strict-eval", action="store_true")
    parser.add_argument("--shallow-bucket", type=str, default=None)
    parser.add_argument("--jacobi-window-size", type=int, default=4)
    parser.add_argument("--jacobi-max-iters", type=int, default=2)
    parser.add_argument("--panda-divergence-threshold", type=float, default=0.05)
    parser.add_argument("--panda-truth-bias", type=float, default=0.02)
    parser.add_argument("--panda-early-agreement-shortcut", action="store_true")
    parser.add_argument("--dola-relative-top", type=float, default=0.1)
    parser.add_argument("--dola-relative-top-value", type=float, default=-1000.0)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    rows = read_run_matrix(RUN_MATRIX_PATH)
    selected_rows = rows if args.run_id is None else [row for row in rows if row["run_id"] == args.run_id]
    if args.list:
        print(json.dumps(selected_rows, indent=2))
        return
    if not selected_rows:
        raise SystemExit(f"No run rows matched run_id={args.run_id!r}.")

    for row in selected_rows:
        run_id = row["run_id"]
        results_dir = RUNS_DIR / run_id
        evaluator_args = build_evaluator_args(args, row, results_dir)
        evaluator_args.model_name = row.get("model_name") or args.model_name
        print({"experiment": EXPERIMENT_NAME, "run_id": run_id, "model_name": evaluator_args.model_name,
               "results_dir": str(results_dir), "decoder_names": list(EXP19_DECODER_NAMES),
               "mode": args.mode, "truthfulqa_limit": args.truthfulqa_limit})
        if args.dry_run:
            continue
        if results_dir.exists() and any(results_dir.glob("*_summary.csv")):
            raise SystemExit(f"{results_dir} already has results; choose a new run_id instead of overwriting.")
        from local_evaluator import ExperimentEvaluator

        evaluator = ExperimentEvaluator(evaluator_args, EXP19_DECODER_NAMES)
        metadata = {
            "experiment_name": EXPERIMENT_NAME,
            "run_id": run_id,
            "notes": row.get("notes"),
            "model_name": evaluator_args.model_name,
            "mode": evaluator_args.mode,
            "seed": evaluator_args.seed,
            "strict_eval": evaluator_args.strict_eval,
            "decoder_names": list(EXP19_DECODER_NAMES),
            "experiment_note": "held_out_evaluation_development_questions_removed_at_analysis_time",
            "refresh_schedule": {"fanda_update1": 1, "fanda_update4": 4, "fanda_frozen": "first_step_only_then_hold"},
            "factorial_axes": {"score_space": ["logprob", "raw-logit"], "relative_top_filter": ["on", "off"],
                               "omitted_cell": "exp13_logit_no_top (identical to exp13_logprob_no_top)"},
        }
        run_truthfulqa_suite(
            evaluator,
            EXP19_DECODER_NAMES,
            evaluator_args,
            artifact_prefix=run_id,
            results_dir=results_dir,
            metadata=metadata,
        )


if __name__ == "__main__":
    main()
