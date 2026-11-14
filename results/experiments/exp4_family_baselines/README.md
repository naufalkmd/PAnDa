# Experiment 4: Baselines

Compares the baseline decoders before any contrastive weight is tuned. All are scored by teacher forcing
(likelihood-based multiple-choice scoring):

- `top_k`: final-layer distribution truncated to the top k tokens and renormalised (`--top-k-value`, default 50).
- `top_p`: final-layer nucleus (top-p) distribution with cumulative mass p, renormalised (`--top-p-value`, default 0.9).
- `dola`: DoLa (log-probability difference, adaptive plausibility constraint).
- `fixed_alpha_dola_low`, `fixed_alpha_dola`, `fixed_alpha_dola_high`: raw-logit contrastive score
  z_mature − α · z_premature with α = 0.0, 0.5, 1.0, premature layer re-selected every 4 tokens.
  α = 0 is greedy decoding.

`top_k` and `top_p` here are truncated-distribution scoring baselines, not sampling. Their exp4 scores
(0.04 and 0.00 MC1) are unusable; use exp11's (see `docs/experiment_log.md`, issue 5).

Terms: [`docs/glossary.md`](../../../docs/glossary.md).

Run example:

```bash
python3 results/experiments/exp4_family_baselines/run_experiment.py \
  --model-name Qwen/Qwen2.5-3B-Instruct \
  --top-k-value 50 \
  --top-p-value 0.9 \
  --mode subset \
  --truthfulqa-limit 50
```
