# Experiment 14: Open-ended generation

Does the selection interval k matter more when the model generates a free-form answer instead of scoring short
multiple-choice options? In exp12, k = 4 and k = ∞ were close, but teacher-forced options are only a few tokens
long, so the two may differ at only a few steps.

Decoders (same FAnDa score, different k): `exp14_update1`, `exp14_update2`, `exp14_update4`, `exp14_update8`,
`exp14_frozen` (k = 1, 2, 4, 8, ∞). Same 50 TruthfulQA questions, up to 64 new tokens.

## Evaluation

Automatic reference overlap (an approximation, not a semantic judgement). For each answer:

- token-level F1 against each TruthfulQA true reference answer and each false reference answer;
- `oref_margin` (main): best true-reference F1 minus best false-reference F1;
- `oref_true_f1`: best F1 against any true reference;
- `oref_win`: 1 if the answer is closer to a true than to any false reference.

0/1/2 correctness labels (`*_manual_eval.csv`): **all 250 rows were labelled by an LLM (Codex)**
(`reviewer = codex`, `review_status = prefilled_by_codex`), not by a person. State this wherever they are used,
or have them reviewed first.

Outputs: raw predictions, summary, pairwise summary, metadata, progress logs, the label sheet.

Terms: [`docs/glossary.md`](../../../docs/glossary.md).

## Run

```bash
./.venv/bin/python results/experiments/exp14_openended_factuality/run_experiment.py \
  --model-name Qwen/Qwen2.5-3B-Instruct \
  --local-files-only \
  --mode subset \
  --truthfulqa-limit 50 \
  --max-new-tokens 64 \
  --run-id run_01_default
```
