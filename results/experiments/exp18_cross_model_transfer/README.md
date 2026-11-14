# Experiment 18: Transfer to other models

Does the ranking greedy vs. DoLa vs. Per-question DoLa-static from Qwen2.5-3B-Instruct hold on other models, with the same
50 TruthfulQA multiple-choice questions?

## Design

- Decoders: `pure_greedy`, `dola`, `fanda` (per-question DoLa-static, premature layer selected once per question).
- Metrics: MC2 first, then MC1 and MC3.
- Questions: by default the same 50 dataset indices as `exp11_core_decoder_comparison/run_01_default`.
- One run-matrix row per model; each writes to `runs/<run_id>/`. The DeepSeek-R1-Distill-Llama row is disabled
  until its exact model id is filled in.

This is narrower than exp11 on purpose: it tests transfer before spending compute on more baselines
(top-k, top-p), on the selection interval k, or on the full dataset.

## Run examples

List the configured rows:

```bash
./.venv/bin/python results/experiments/exp18_cross_model_transfer/run_experiment.py \
  --list
```

Dry-run one row without loading weights:

```bash
./.venv/bin/python results/experiments/exp18_cross_model_transfer/run_experiment.py \
  --run-id run_01_gemma3_4b_it \
  --local-files-only \
  --dry-run
```

Run one row:

```bash
./.venv/bin/python results/experiments/exp18_cross_model_transfer/run_experiment.py \
  --run-id run_01_gemma3_4b_it \
  --local-files-only
```

Run every enabled row:

```bash
./.venv/bin/python results/experiments/exp18_cross_model_transfer/run_experiment.py \
  --local-files-only
```

## Notes

- `--mode subset` and `--truthfulqa-limit 50` are the defaults, to match the exp11 questions.
- For a new random subset, set the row's `subset_strategy` to `random_seed_subset`.
- To enable the DeepSeek-R1-Distill-Llama row, replace the placeholder `model_name` in `run_matrix.csv` and set
  `enabled=true`.

Terms: [`docs/glossary.md`](../../../docs/glossary.md).
