# Experiment 2: Look-ahead depth for choosing between two scores

PAnDa without Jacobi blocks. At each token the decoder has two scores:

- the final-layer logits `final_logits` (greedy);
- the contrastive score `final_logits - shallow_logits` (mature minus premature layer).

When their top tokens disagree, it chooses between them by a short look-ahead:

- `simple_panda_h1`: compare each score's top token by its log-probability under that score.
- `simple_panda_h2`: extend each candidate by one more token under the same score and compare the two-token totals.

Terms: [`docs/glossary.md`](../../../docs/glossary.md).

Run example:

```bash
python3 results/experiments/exp2_horizon_arbitration/run_experiment.py \
  --model-name Qwen/Qwen2.5-3B-Instruct \
  --mode subset \
  --truthfulqa-limit 50
```
