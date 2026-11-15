# Experiment 7: Rule-based switch vs. its two fixed settings

Is switching between two scores at each token better than always using one of them? The two scores:

- the final-layer logits `final_logits` (greedy);
- the contrastive score `final_logits - shallow_logits`.

Decoders:

- `pure_greedy`: greedy decoding through the standard `greedy` decoder.
- `fanda_greedy`: always the final-layer logits, through the same code path as `fanda` (the premature layer is
  still selected, but not used).
- `fanda`: always the contrastive score. In the saved run (2026-06-03) the premature layer was re-selected every
  4 tokens; the current code keeps it fixed per question.
- `pure_argmax_switch`: greedy when both scores have the same top token, the contrastive score otherwise.
- `pure_argmax_switchv2`: the same rule, with the premature-layer selection of `fanda`.
- `dola`: DoLa.

Why: exp6 found the switch rules close to each other, so the question is whether switching beats the two fixed
settings at all. `pure_greedy` vs. `fanda_greedy` checks that the shared code path does not change greedy
decoding; `pure_argmax_switchv2` checks whether the switch changes when it shares the layer selection of `fanda`.

Terms: [`docs/glossary.md`](../../../docs/glossary.md).

Run example:

```bash
python3 results/experiments/exp7_switch_vs_fixed_regimes/run_experiment.py \
  --model-name Qwen/Qwen2.5-3B-Instruct \
  --mode subset \
  --truthfulqa-limit 50
```
