# Experiments

Each folder holds one experiment: `run_experiment.py`, `run_matrix.csv` (one row per run), a README, and its saved
outputs in `runs/<run_id>/`. The runners import `src/panda` and the shared code here (`common.py`,
`local_evaluator.py`). Run them from the repository root; a runner never overwrites a finished run.

Results and known issues for every experiment: [`docs/experiment_log.md`](../../docs/experiment_log.md).
Code names → standard terms: [`docs/glossary.md`](../../docs/glossary.md). All runs: TruthfulQA multiple choice
(MC1/MC2/MC3) with `Qwen/Qwen2.5-3B-Instruct` unless noted. exp11–exp18 ran on the same 50 questions (seed 42, the
development set).

*Selection interval k*: the premature layer is re-selected every k tokens (k = ∞: once, at the first answer token,
so once per question).

## In the report

| Folder | Question | Scoring rules (code names) | Report |
|---|---|---|---|
| `exp19_heldout_full/` | **Held-out evaluation on all 817 questions**: likelihood, DoLa in two configurations, per-question DoLa-static, the factorial and k = 1, 4, ∞ in one run | `pure_greedy`, `dola_mc_reference`, `dola`, `fanda_frozen`, `exp13_logprob_top`, `_logprob_no_top`, `_logit_top`, `fanda_update1`, `_update4` | §5, §6, Appendix B |
| `exp20_self_evaluation/` | Self-evaluation, P(True), per answer option with selective prediction: design frozen on 417 questions, tested once on the other 400; early exit and question-removed control on eight models | no decoder: one forward pass per option | §7, §8, Appendix B |
| `exp21_likelihood_baselines/` | Base-model likelihood on all 817 questions for the eight exp20 models | `pure_greedy` | §8 |
| `exp16_mc_persistence_seed_sweep/` | Selection interval on the development set and four other random 50-question subsets | `fanda_update{1,2,4,8}`, `fanda_frozen` | Appendix C |

## Development history (summarised in Appendix C)

| Folder | Question | Scoring rules |
|---|---|---|
| `exp11_core_decoder_comparison/` | First main comparison (its `panda_switch` row is the dropped PAnDa method) | `pure_greedy`, `top_k`, `top_p`, `dola`, `fanda`, `panda_switch` |
| `exp12_state_persistence_diagnostics/` | Selection interval k ∈ {1, 2, 4, ∞} | `fanda_update1`, `_update2`, `_update4`, `fanda_frozen` |
| `exp13_logit_filter_factorial/` | 2 × 2: log-probability vs. raw-logit difference × adaptive plausibility constraint | `exp13_logprob_top`, `_logprob_no_top`, `_logit_top`, `_logit_no_top` |

exp19 repeats exp11–exp13 on all 817 questions; the report uses the exp19 numbers.

## Left out of the report

| Folder | Question | Why it is left out |
|---|---|---|
| `exp14_openended_factuality/` | Open-ended generation, k ∈ {1, 2, 4, 8, ∞} | Correctness labels written by an LLM (Codex), not checked by a person |
| `exp15_prefix_probe/` | Case study: answer prefixes, k = ∞ vs. k = 1 | Same labeller; open-ended generation is outside the study |
| `exp17_openended_dola_trace/` | Token-level premature-layer traces of open-ended answers | Open-ended generation is outside the study |
| `exp18_cross_model_transfer/` | Layer contrast on Gemma 3 4B, Falcon 3 3B, a self-calibrated Qwen 1.5B | 50 questions only; the Gemma DoLa rows may lack the final norm (experiment log, issue 8) |

## Exploration (`exploration/`)

Design alternatives on the development set that the study does not use, kept for the record. In their saved runs
(2026-06-03), `fanda` re-selected the premature layer every 4 tokens. `exploration/sanity_runs/` holds the first
sanity runs of the dropped PAnDa method (historical "stage" names).

| Folder | Question |
|---|---|
| `exploration/exp1_contrast_strength/` | Weighting the premature-layer term in DoLa (α = 0.10, 0.50, 0.95) |
| `exploration/exp2_horizon_arbitration/` | Look-ahead depth when choosing between greedy and contrastive scores |
| `exploration/exp4_family_baselines/` | Baselines, including raw-logit contrast with α = 0, 0.5, 1 |
| `exploration/exp5_block_ablation/` | Jacobi blocks on top of contrastive decoding |
| `exploration/exp6_switch_variants/` | Four rule-based switches between greedy and contrastive scores |
| `exploration/exp7_switch_vs_fixed_regimes/` | A switch vs. always greedy and always contrastive |
| `exploration/exp8_oracle_switch_diagnosis/` | Oracle switch (upper bound for any switch rule) |
| `exploration/exp9_adaptive_lambda_contrast/` | Contrastive weight set per token by a rule |
| `exploration/exp10_ema_risk_switch/` | Switch gated by an exponential moving average |

`exp3` does not exist (the number was skipped).

## Rerunning

- Rebuild the report's analyses, tables and figures without a GPU: see the main [README](../../README.md#rebuild-the-report).
- Print the scores of every saved run, exploration included: `python scripts/summarise_runs.py`.
- `scripts/run_report_reruns.sh` is how the exp16 subsets and the exp19 held-out run were scored (2026-11-14).
- `--mode full` alone still uses 50 questions; add `--truthfulqa-limit all` for the full dataset.
