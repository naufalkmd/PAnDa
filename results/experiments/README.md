# Experiments

Each folder holds one experiment: `run_experiment.py`, `run_matrix.csv` (one row per run), a README, and its saved
outputs in `runs/<run_id>/`. The runners import `src/panda` and the shared code here (`common.py`,
`local_evaluator.py`). Run them from the repository root.

Results and known issues for every experiment: [`docs/experiment_log.md`](../../docs/experiment_log.md).
Code names → standard terms: [`docs/glossary.md`](../../docs/glossary.md). All runs: TruthfulQA multiple choice
(MC1/MC2/MC3) with `Qwen/Qwen2.5-3B-Instruct`, on the same 50 questions (the development set) unless noted.

*Selection interval k*: the premature layer is re-selected every k tokens (k = ∞: once, at the first answer token, so once per question).

## Experiments used in the report

| Folder | Question | Decoders |
|---|---|---|
| `exp11_core_decoder_comparison/` | Main comparison (its `panda_switch` row is the dropped PAnDa method) | `pure_greedy`, `top_k`, `top_p`, `dola`, `fanda`, `panda_switch` |
| `exp12_state_persistence_diagnostics/` | Selection interval k ∈ {1, 2, 4, ∞} | `fanda_update1`, `_update2`, `_update4`, `fanda_frozen` |
| `exp13_logit_filter_factorial/` | 2 × 2: log-probability vs. raw-logit difference × adaptive plausibility constraint | `exp13_logprob_top`, `_logprob_no_top`, `_logit_top`, `_logit_no_top` |
| `exp14_openended_factuality/` | Open-ended generation, k ∈ {1, 2, 4, 8, ∞} (automatic reference overlap; LLM-assigned labels) | `exp14_update{1,2,4,8}`, `exp14_frozen` |
| `exp15_prefix_probe/` | Case study: answer prefixes, k = ∞ vs. k = 1 | `exp14_frozen`, `exp14_update1` |
| `exp16_mc_persistence_seed_sweep/` | Selection interval across random subsets | `fanda_update{1,2,4,8}`, `fanda_frozen` |
| `exp17_openended_dola_trace/` | Token-level premature-layer traces of open-ended answers | `exp14_update1` |
| `exp18_cross_model_transfer/` | Transfer to Gemma 3 4B, Falcon 3 3B, HINT self-calibrated Qwen 1.5B | `pure_greedy`, `dola`, `fanda` |
| `exp19_heldout_full/` | **Held-out evaluation on all 817 questions** (main comparison, factorial, k = 1, 4, ∞ in one run) | `pure_greedy`, `dola`, `fanda_frozen`, `exp13_logprob_top`, `_logprob_no_top`, `_logit_top`, `fanda_update1`, `_update4` |
| `exp20_self_evaluation/` | Self-evaluation score, P(True), per answer option, with selective prediction: design frozen on 417 questions, tested once on the other 400 | no decoder: one forward pass per option (`run_experiment.py` in the folder) |

exp11–exp18 ran on the 50-question development set (exp16 adds other random subsets). exp19 has 767 questions that
no design choice of the layer-contrast decoders was made on. exp20 has its own split: its design was made on 417
questions (the development set among them) and tested on the other 400.

## Exploration (not in the report's main text)

Design alternatives that the final method does not use. They are kept for the record and summarised in one
sentence (and the appendix) of the report. In their saved runs (2026-06-03), `fanda` re-selected the premature
layer every 4 tokens.

| Folder | Question |
|---|---|
| `exp1_contrast_strength/` | Weighting the premature-layer term in DoLa (α = 0.10, 0.50, 0.95) |
| `exp2_horizon_arbitration/` | Look-ahead depth when choosing between greedy and contrastive scores |
| `exp4_family_baselines/` | Baselines, including raw-logit contrast with α = 0, 0.5, 1 |
| `exp5_block_ablation/` | Jacobi blocks on top of contrastive decoding |
| `exp6_switch_variants/` | Four rule-based switches between greedy and contrastive scores |
| `exp7_switch_vs_fixed_regimes/` | A switch vs. always greedy and always contrastive |
| `exp8_oracle_switch_diagnosis/` | Oracle switch (upper bound for any switch rule) |
| `exp9_adaptive_lambda_contrast/` | Contrastive weight set per token by a rule |
| `exp10_ema_risk_switch/` | Switch gated by an exponential moving average |

`exp3` does not exist (the number was skipped).

## Rerunning

- Reruns for the report: `bash scripts/run_report_reruns.sh` (see `docs/report_checklist.md`, part E).
- Print the scores of every saved run: `python scripts/summarise_runs.py`.
- `--mode full` alone still uses 50 questions; add `--truthfulqa-limit all` for the full dataset.
