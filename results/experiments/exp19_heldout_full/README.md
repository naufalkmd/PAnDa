# Experiment 19: Held-out evaluation on all TruthfulQA questions

Every design choice of per-question DoLa-static was made on the same 50 questions (the development set). This run evaluates the
decoders the report needs on **all 817** TruthfulQA multiple-choice questions, in one run, so each comparison is
paired on the same questions. The report's held-out scores are the 767 questions outside the development set:

```bash
python scripts/paired_tests.py results/experiments/exp19_heldout_full/runs/run_01_qwen25_3b_full \
  --exclude-questions-of results/experiments/exp12_state_persistence_diagnostics/runs/run_01_default \
  --pairs fanda_frozen:dola fanda_frozen:pure_greedy dola:pure_greedy --holm
```

The 50 development questions are also in this run. Their scores here can be compared with the saved June runs as a
check that the new environment reproduces the old results.

## Decoders

| Decoder | Standard description | Used for |
|---|---|---|
| `pure_greedy` | Base model log-likelihood, no contrast (DoLa's "baseline") | main comparison |
| `dola_mc_reference` | DoLa as in its own TruthfulQA-MC evaluation: no plausibility constraint, option score not renormalised, candidate layers in the second half (blocks 18, 20, ..., 34 of 36) | main comparison |
| `dola` | DoLa with its generation settings (constraint on, renormalised) and early candidate layers (blocks 1–9), as in the development runs | main comparison, factorial base |
| `fanda_frozen` | Per-question DoLa-static (premature layer selected once, at the first answer token, so once per question, k = ∞) | main comparison, interval |
| `exp13_logprob_top` | log-probability difference + plausibility constraint, DoLa's layer selection | factorial |
| `exp13_logprob_no_top` | log-probability difference, no constraint | factorial |
| `exp13_logit_top` | raw-logit difference + constraint | factorial |
| `fanda_update1` | Score of per-question DoLa-static, premature layer re-selected every token (k = 1) | interval |
| `fanda_update4` | Score of per-question DoLa-static, re-selected every 4 tokens (k = 4) | interval |

Left out to save time (about 14 h on the June hardware): the raw-logit, no-constraint factorial cell (identical to
the log-probability one without the constraint, by construction), k = 2, top-k and top-p (equal to greedy on the
development set), and PAnDa (about 2× the time of DoLa). These stay as development-set results only.

## Run rows

- `run_01_qwen25_3b_full`: Qwen2.5-3B-Instruct (R2, about 19 h on the June hardware).
- `run_02_gemma3_4b_full`: Gemma 3 4B (optional R4, about 27 h).

The model is read from the row's `model_name`. A row that already has results is never overwritten.

```bash
bash scripts/run_report_reruns.sh r2      # or: python results/experiments/exp19_heldout_full/run_experiment.py --run-id run_01_qwen25_3b_full
```

Each run's metadata records the environment (git commit, package versions, GPU, model precision, candidate
layers, SHA-256 of the TruthfulQA file) under `environment`.

Terms: [`docs/glossary.md`](../../../docs/glossary.md).
