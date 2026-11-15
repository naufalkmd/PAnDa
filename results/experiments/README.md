# Experiments

Each folder holds one experiment: `run_experiment.py`, `run_matrix.csv` (one row per run), a README, and its saved
outputs in `runs/<run_id>/`. The runners import `src/truthfulqa_scoring` and the shared code here (`common.py`,
`local_evaluator.py`). Run them from the repository root; a runner never overwrites a finished run.

Results and known issues for every experiment: [`docs/experiment_log.md`](../../docs/experiment_log.md).
Code names → standard terms: [`docs/glossary.md`](../../docs/glossary.md). All runs: TruthfulQA multiple choice
(MC1/MC2/MC3) with `Qwen/Qwen2.5-3B-Instruct` unless noted.

## In the report

| Folder | Question | Scoring rules (code names) | Report |
|---|---|---|---|
| `exp19_heldout_full/` | **Held-out evaluation on all 817 questions**: likelihood, DoLa in two configurations, per-question DoLa-static and the factorial, in one run | `pure_greedy`, `dola_mc_reference`, `dola`, `fanda_frozen`, `exp13_logprob_top`, `_logprob_no_top`, `_logit_top` (the run also holds `fanda_update1`, `_update4`, not used in the report) | §5, §6, Appendix B |
| `exp20_self_evaluation/` | Self-evaluation, P(True), per answer option with selective prediction: design frozen on 417 questions, tested once on the other 400; early exit and question-removed control on eight models | no decoder: one forward pass per option | §7, §8, Appendix B |
| `exp21_likelihood_baselines/` | Base-model likelihood on all 817 questions for the eight exp20 models | `pure_greedy` | §8 |

## Kept for the analysis (not cited in the report)

The first runs on the 50 development questions (seed 42). `scripts/heldout_analysis.py` and
`scripts/figure_data.py` read the list of development questions from exp12, and the environment check in the
report's §4 compares the held-out run with exp11–exp13 on those questions. exp19 repeats all three on 817 questions.

| Folder | Question |
|---|---|
| `exp11_core_decoder_comparison/` | First comparison (its `panda_switch` row is the dropped PAnDa method) |
| `exp12_state_persistence_diagnostics/` | Per-question DoLa-static with the premature layer re-selected every k ∈ {1, 2, 4, ∞} tokens |
| `exp13_logit_filter_factorial/` | 2 × 2: log-probability vs. raw-logit difference × adaptive plausibility constraint |

## Removed from the tree, kept under git tags

Results of every removed experiment stay in the experiment log. To look at one, restore it from its tag, for
example `git checkout pre-cleanup-2026-11 -- results/experiments/exp18_cross_model_transfer`, and do not commit it
back.

| Tag | What it keeps |
|---|---|
| `exploration-2026-06` | exp1–exp10 (switching rules, fixed weights, look-ahead, Jacobi blocks; in `results/experiments/exploration/`) and the first PAnDa sanity runs |
| `pre-cleanup-2026-11` | exp14, exp15, exp17 (open-ended generation; labels written by an LLM, not checked by a person), exp18 (transfer on 50 questions; Gemma final-norm issue), the development plots, the earlier method notes and presentation, the June 2026 course report |
| `dev-history-2026-11` | exp16 (selection interval on five 50-question subsets), `docs/algorithms/`, `scripts/run_report_reruns.sh`, and the report version with the development-history appendices |

`exp3` does not exist (the number was skipped).

## Rerunning

- Rebuild the report's analyses, tables and figures without a GPU: see the main [README](../../README.md#rebuild-the-report).
- Print the scores of every saved run: `python scripts/summarise_runs.py`.
- `--mode full` alone still uses 50 questions; add `--truthfulqa-limit all` for the full dataset.
