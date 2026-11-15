# Experiment 6: Rule-based switches between greedy and contrastive scores

Tests single-pass rules that choose, at each token, between two scores:

- the final-layer logits `final_logits` (greedy);
- the contrastive score `final_logits - shallow_logits`.

The question is whether a simple per-token rule recovers the benefit of contrastive decoding without the cost
of Jacobi blocks or look-ahead.

Decoders:

- `pure_argmax_switch`: if both scores have the same top token, use greedy; otherwise use the contrastive score.
- `guarded_argmax_switch`: as above, but keep greedy if the greedy token is still in the contrastive score's
  top k (`exp6_guarded_top_k`).
- `sticky_contrast_switch`: the guarded rule, but once it switches to the contrastive score it stays there for
  the next `sticky_hold_steps` tokens.
- `contrast_margin_switch`: if the top tokens differ, switch only when the contrastive score of its own top
  token exceeds its score of the greedy token by more than `exp6_margin_threshold`.

All four are single-pass: no Jacobi blocks, no look-ahead, no tuning of the contrastive weight.

Terms: [`docs/glossary.md`](../../../docs/glossary.md).

Run example:

```bash
python3 results/experiments/exp6_switch_variants/run_experiment.py \
  --model-name Qwen/Qwen2.5-3B-Instruct \
  --mode subset \
  --truthfulqa-limit 50
```
