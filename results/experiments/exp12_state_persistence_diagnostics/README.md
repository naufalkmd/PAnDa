# Experiment 12: Selection interval of the premature layer

An ablation of one of the changes from DoLa to per-question DoLa-static: how often the premature layer is re-selected. The four
decoders share the score of per-question DoLa-static (raw-logit difference, no adaptive plausibility constraint, layer selection by
JSD at τ = 0.5) and differ only in the selection interval k:

| Decoder | Premature layer re-selected |
|---|---|
| `fanda_update1` | at every token (k = 1) |
| `fanda_update2` | every 2 tokens (k = 2) |
| `fanda_update4` | every 4 tokens (k = 4; the default before commit `efec350`) |
| `fanda_frozen` | once, at the first answer token, which is the same for every option of a question (k = ∞; per-question DoLa-static) |

k = 1 is **not** DoLa: DoLa uses JSD at τ = 1 and the plausibility constraint (exp13 isolates those).

## Hypothesis

Re-selecting the premature layer changes the contrastive score itself, so the token ranking can change even when
the context barely has. A longer interval removes these changes; a very long one keeps a layer that is no longer
the max-JSD layer. The hypothesis was that an intermediate k (k = 4) balances the two. The saved run does not
show this clearly: k = 4 and k = ∞ tie on MC1 (0.40), and exp16 did not replicate the ranking on a second subset.

## Diagnostics (in the summary CSV)

- `switch_rate`: fraction of steps at which the selected premature layer changes.
- `selected_layer_match_rate`: fraction of steps at which the layer in use equals the current max-JSD layer.
- `refresh_rate`: fraction of steps at which the layer is re-selected.
- `avg_oracle_jsd_gap`: mean JSD of the current max-JSD layer minus the JSD of the layer in use. Here "oracle"
  means the max-JSD layer at that step, not the correct answer.
- `avg_selection_margin`: mean difference between the contrastive and the greedy top-token log-probability.
- `avg_risk_score`: mean JSD between the greedy and contrastive distributions.
- `trigger_rate`: fraction of steps at which the two distributions disagree (different top token, JSD above a threshold).

## Figure

`results/figures/exp12_state_persistence_hypothesis.svg` (from `scripts/plots/plot_exp12_state_persistence_hypothesis.py`;
both removed from the tree on 2026-11-15 and kept at the git tag `pre-cleanup-2026-11`):

- left panel: `switch_rate` (x) against `selected_layer_match_rate` (y); colour `avg_oracle_jsd_gap`; size MC2;
- right panel: MC1, MC2 and MC3 for the four intervals.

Terms: [`docs/glossary.md`](../../../docs/glossary.md).

## Run

Run row: `run_01_default` (the 50-question development set). The full-dataset evaluation of these
decoders is in exp19 (`exp19_heldout_full`).

```bash
./.venv/bin/python results/experiments/exp12_state_persistence_diagnostics/run_experiment.py \
  --model-name Qwen/Qwen2.5-3B-Instruct \
  --local-files-only \
  --mode subset \
  --truthfulqa-limit 50 \
  --run-id run_01_default
```
