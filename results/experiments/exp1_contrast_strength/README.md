# Experiment 1: Contrastive weight

Does weighting the premature-layer term change DoLa's TruthfulQA results?

- `official_dola`: DoLa (dynamic premature-layer selection, log-probability difference, adaptive plausibility constraint).
- `matched_alpha_dola_0p10`, `_0p50`, `_0p95`: the same score with the premature layer's log-probabilities
  weighted by α = 0.10, 0.50, 0.95.

Terms: [`docs/glossary.md`](../../../docs/glossary.md).

Run example:

```bash
python3 results/experiments/exp1_contrast_strength/run_experiment.py \
  --model-name Qwen/Qwen2.5-3B-Instruct \
  --mode subset \
  --truthfulqa-limit 50
```
