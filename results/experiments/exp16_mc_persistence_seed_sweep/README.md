# Experiment 16: Selection interval across random subsets

Does the ranking of the selection intervals k = 1, 2, 4, 8, ∞ (exp12) hold on other random 50-question subsets
of TruthfulQA? Only the interval and the subset change; the evaluator is fixed.

## Design

- Decoders: `fanda_update1`, `fanda_update2`, `fanda_update4`, `fanda_update8`, `fanda_frozen`.
  The saved seed-101 run names them `always_contrast_update{k}` / `always_contrast_frozen`: it was produced by an
  uncommitted code version from before the rename. Its metadata (`refresh_schedule`) records the same intervals,
  but the scoring code itself cannot be checked. Rerun it under the current names if it ends up in the report.
- Metrics: MC2 first, then MC1 and MC3.
- 50 questions per run.

Run rows:

1. `run_01_anchor_subset`: the same 50 dataset indices as `exp12_state_persistence_diagnostics/run_01_default`
   (the development set);
2. `run_02_seed_101` (done), `run_03_seed_202`, `run_04_seed_303`, `run_05_seed_404`: new random subsets.
   Rows 3–5 are run by `bash scripts/run_report_reruns.sh r1`.

## Outputs

`*_raw_predictions.csv`, `*_summary.csv`, `*_pairwise_summary.csv`, `*_metadata.json`, `progress.json`,
`progress.ndjson`. The metadata of row 1 records the reused dataset indices and the source run.

## How to read it

- one interval best on MC2 in nearly every subset: a stable choice;
- k = 4 and k = ∞ close in every subset: a long interval helps, but the best one is not identified;
- rankings that change from subset to subset: the subset, not the interval, drives the differences.

The seed-101 subset already differs from the development set: there k = 1 and k = ∞ tie on MC1 (0.30) and
k = 1 is best on MC2.

Terms: [`docs/glossary.md`](../../../docs/glossary.md).

## Run

```bash
./.venv/bin/python results/experiments/exp16_mc_persistence_seed_sweep/run_experiment.py \
  --model-name Qwen/Qwen2.5-3B-Instruct \
  --local-files-only \
  --mode subset \
  --truthfulqa-limit 50
```
