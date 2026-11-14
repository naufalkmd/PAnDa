# Experiment 11: Main decoder comparison

The baselines, DoLa, FAnDa and PAnDa in one TruthfulQA multiple-choice run, scored by teacher forcing:

- `pure_greedy`: greedy decoding (final-layer log-probabilities).
- `top_k`: final-layer distribution truncated to the top k tokens and renormalised. If the scored token falls
  outside the kept set, its full-distribution log-probability is used instead.
- `top_p`: final-layer nucleus (top-p) distribution with cumulative mass p, renormalised, with the same fallback.
- `top_p_backoff`: older name for the same nucleus baseline, kept so older runs can be compared (opt-in).
- `dola`: DoLa (dynamic premature-layer selection, log-probability difference, adaptive plausibility constraint).
- `fanda`: FAnDa, the raw-logit difference `final_logits - shallow_logits` with the premature layer selected once
  per answer.
- `panda_switch`: PAnDa (Jacobi blocks, choosing between greedy and contrastive scores).

Questions: how does FAnDa compare with the truncation baselines and DoLa, and does PAnDa add anything over the
same baselines?

Defaults:

- `top_k`: `--top-k-value 50`; `top_p`: `--top-p-value 0.9`.
- `panda_switch`: `jacobi_window_size=4`, `jacobi_max_iters=2`.
- `top_p_backoff` is added only with `--include-top-p-backoff`.

Run rows: `run_01_default` (the 50-question development set), `run_02_full` (all 817 questions; run with
`--mode full --truthfulqa-limit all`, or `bash scripts/run_report_reruns.sh r2`).

Terms: [`docs/glossary.md`](../../../docs/glossary.md).

Run example:

```bash
./.venv/bin/python results/experiments/exp11_core_decoder_comparison/run_experiment.py \
  --model-name Qwen/Qwen2.5-3B-Instruct \
  --local-files-only \
  --mode subset \
  --truthfulqa-limit 50 \
  --run-id run_01_default
```

With the `top_p_backoff` alias:

```bash
./.venv/bin/python results/experiments/exp11_core_decoder_comparison/run_experiment.py \
  --model-name Qwen/Qwen2.5-3B-Instruct \
  --local-files-only \
  --mode subset \
  --truthfulqa-limit 50 \
  --run-id run_01_default \
  --include-top-p-backoff
```
