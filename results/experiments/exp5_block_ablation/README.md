# Experiment 5: Jacobi blocks with contrastive decoding

After exp8, does Jacobi-style block refinement still help when the choice between the greedy and contrastive
scores is removed? The default block size for this experiment is 2.

Compared decoders:

- `fanda`: the contrastive score `final_logits - shallow_logits` at every token, one token at a time. In the
  saved runs (2026-06-03) the premature layer was re-selected every 4 tokens; the current code keeps it fixed
  per question (see `docs/glossary.md`).
- `panda_switch`: PAnDa (Jacobi blocks, choosing between greedy and contrastive scores).
- `panda_switch_update4`: PAnDa, but one premature layer (selected by JSD) is shared by all positions in the
  block and re-selected only every 4 scored tokens.
- `panda_fandas`: the same Jacobi blocks, with the premature layer selected per position and the contrastive
  score used at every position (no choice between scores).

How to read it:

- `panda_fandas` > `fanda`: blocks add something beyond contrastive scoring at every token.
- `panda_switch_update4` ≈ `panda_switch`: per-position layer selection inside a block is unnecessary.
- `panda_switch_update4` > `panda_switch`: choosing between scores inside the block was unnecessary or harmful.

Terms: [`docs/glossary.md`](../../../docs/glossary.md).

Run example:

```bash
./.venv/bin/python results/experiments/exp5_block_ablation/run_experiment.py \
  --model-name Qwen/Qwen2.5-3B-Instruct \
  --local-files-only \
  --mode subset \
  --truthfulqa-limit 50 \
  --run-id run_02_update4_default
```
