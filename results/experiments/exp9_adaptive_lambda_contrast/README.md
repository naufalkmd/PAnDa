# Experiment 9: Per-token contrastive weight

Does a contrastive weight set per token by a rule beat a fixed weight of 1?

Compared decoders:

- `fanda`: `scores = final_logits - shallow_logits` at every token. In the saved runs (2026-06-03) the
  premature layer was re-selected every 4 tokens; the current code keeps it fixed per question.
- `adaptive_lambda_contrast`: the same layer selection, with `scores = final_logits - lambda_t * shallow_logits`.
  `lambda_t` rises with the normalised entropy of the final-layer distribution and falls when the greedy
  score's top-token probability exceeds the contrastive score's; it is clipped to `[lambda_min, 1.0]`.

Rule:

```text
signal_t = uncertainty_weight * normalized_final_entropy
           - confidence_gap_weight * max(0, greedy_confidence - contrast_confidence)
lambda_t = clamp(lambda_min + (lambda_max - lambda_min) * signal_t, lambda_min, lambda_max)
```

How to read it: if `adaptive_lambda_contrast` beats `fanda`, a fixed weight of 1 is too strong at some tokens;
if it ties or loses, a fixed weight is preferable here.

Run rows: `run_01_default` (`lambda_min = 0.5`), `run_02_lambda_floor_025` (`lambda_min = 0.25`).

Terms: [`docs/glossary.md`](../../../docs/glossary.md).

Run example:

```bash
python3 results/experiments/exp9_adaptive_lambda_contrast/run_experiment.py \
  --model-name Qwen/Qwen2.5-3B-Instruct \
  --mode subset \
  --truthfulqa-limit 50
```
