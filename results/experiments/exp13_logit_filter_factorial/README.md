# Experiment 13: Score difference × plausibility constraint (2 × 2 factorial)

An ablation of two of the changes from DoLa to FAnDa. Earlier baselines (exp4) suggested that a raw-logit
contrastive score beats DoLa here, but they changed two things at once:

- raw-logit difference instead of DoLa's log-probability difference;
- no adaptive plausibility constraint.

They also re-selected the premature layer every 4 tokens, while DoLa re-selects it at every token. So all four
cells here use **DoLa's own layer selection** (JSD at every token) and differ only in:

- the score: log-probability difference vs. raw-logit difference;
- the adaptive plausibility constraint: on vs. off.

| Decoder | Score | Constraint |
|---|---|---|
| `exp13_logprob_top` | log-probability difference | on (this is DoLa) |
| `exp13_logprob_no_top` | log-probability difference | off |
| `exp13_logit_top` | raw-logit difference | on |
| `exp13_logit_no_top` | raw-logit difference | off |

The third change, the selection interval, is ablated in exp12. The fourth, the JSD temperature (τ = 0.5 in
FAnDa, 1 in DoLa), is not ablated anywhere yet.

How to read it: a main effect of the score shows as a gain from raw logits with the constraint both on and off;
a main effect of the constraint, as a gain from removing it with either score; an interaction, as a gain only
in the raw-logit, no-constraint cell.

**Note:** without the constraint the two scores rank every token identically, because the log-softmax differs
from the raw logits only by a per-step constant (their saved results are identical to 8 decimals).

Outputs: raw predictions, summary, pairwise summary, metadata, progress logs.

Run rows: `run_01_default` (the 50-question development set), `run_02_full` (all 817 questions; run with
`--mode full --truthfulqa-limit all`, or `bash scripts/run_report_reruns.sh r2`).

Terms: [`docs/glossary.md`](../../../docs/glossary.md).

Run example:

```bash
./.venv/bin/python results/experiments/exp13_logit_filter_factorial/run_experiment.py \
  --model-name Qwen/Qwen2.5-3B-Instruct \
  --local-files-only \
  --mode subset \
  --truthfulqa-limit 50 \
  --run-id run_01_default
```
