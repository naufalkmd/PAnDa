# Experiment 8: Oracle switch

Are the rule-based switches weak because of their rule, or because contrastive scoring at every token is simply
better under TruthfulQA multiple-choice scoring? An oracle switch gives the upper bound for any switch rule.

Compared decoders:

- `pure_greedy`: greedy decoding (final-layer log-probabilities).
- `fanda`: the contrastive score `final_logits - shallow_logits` at every token. In the saved run (2026-06-03)
  the premature layer was re-selected every 4 tokens; the current code keeps it fixed per question.
- `pure_argmax_switchv2`: a rule-based switch with the same layer selection as `fanda`; it uses the contrastive
  score only when the two scores' top tokens differ.
- `oracle_token_switch`: at each scored token, uses whichever score gives the correct token the higher
  log-probability. This uses the answer, so it is an upper bound, not a decoder.
- `dola`: DoLa.

How to read it:

- oracle ≤ `fanda`: contrastive scoring at every token is the better setting here, and no switch rule can help.
- oracle clearly > `fanda`: switching can help, and the practical rule is the weak part.

Terms: [`docs/glossary.md`](../../../docs/glossary.md).

Run example:

```bash
python3 results/experiments/exp8_oracle_switch_diagnosis/run_experiment.py \
  --model-name Qwen/Qwen2.5-3B-Instruct \
  --mode subset \
  --truthfulqa-limit 50
```
