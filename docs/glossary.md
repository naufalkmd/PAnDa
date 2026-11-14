# Glossary: code names → standard terms

The code and the saved result files use project names. The report and the README use the standard
terms in the right-hand column. Identifiers are **not renamed**, because saved runs, plots and figure
JSON depend on them.

## Methods

| Code name | Standard term (used in the report) | Definition, as implemented |
|---|---|---|
| `pure_greedy`, `greedy` | Greedy decoding / final-layer scoring | Score with the final layer's log-probabilities. |
| `dola`, `official_dola` | DoLa (Chuang et al., 2024), dynamic premature-layer selection | Per token: choose the premature layer with the largest Jensen–Shannon divergence (JSD) to the mature layer, at temperature 1, from the candidate bucket (mature layer excluded). Score = log p_mature − log p_premature, then the **adaptive plausibility constraint** (`relative_top`, 0.1). |
| `relative_top`, "relative-top filter" | Adaptive plausibility constraint (Li et al., 2023) | Masks tokens whose mature-layer probability is below `relative_top` × the top token's probability. |
| `fanda`, FAnDa (exp11, exp18) | Contrastive layer decoding with a **fixed premature layer per answer**, no plausibility constraint, raw-logit difference | Score = z_mature − z_premature (raw logits). Premature layer chosen by JSD at **temperature τ = 0.5** at the first token of each scored answer, then kept for the rest of the answer. |
| `fanda` (exp7–exp10) | Same as above, but with the layer **re-selected every 4 tokens** | Config default `update_every = 4`. Not the same decoder as `fanda` in exp11/exp18; its numbers equal `fanda_update4`. |
| `fanda_update{k}`, `exp14_update{k}`, `always_contrast_update{k}` | Premature layer re-selected every k tokens | Same score as `fanda`; selection rule as above (τ = 0.5). `update1` re-selects every token but is **not** DoLa: it uses τ = 0.5 JSD and no plausibility constraint. |
| `fanda_frozen`, `exp14_frozen`, `always_contrast_frozen` | Premature layer selected once per answer | Selected at the answer's first token (`update_every = 10**9`). |
| `exp13_{logprob,logit}_{top,no_top}` | 2 × 2 factorial: score space × plausibility constraint | Per-token selection with DoLa's own JSD (τ = 1). Without the constraint the two score spaces give identical rankings, because log-softmax differs from the raw logits only by a per-step constant. |
| `fixed_alpha_dola{_low,,_high}`, `matched_alpha_dola_0p{10,50,95}` | Contrast with a fixed weight α | Score = z_mature − α · z_premature, α ∈ {0.1, 0.5, 0.95}. |
| `top_k`, `top_p` | Top-k / nucleus truncation of the final-layer distribution | Under teacher-forced multiple-choice scoring these act as truncation baselines, not sampling. |
| `panda`, `panda_switch` | Block-wise arbitration between greedy and contrast views (the project's earlier method, PAnDa) | Speculative (Jacobi-style) blocks of 4 tokens; contrast applied from the first divergence point. |
| `*_switch*`, `ema_risk_switch`, `adaptive_lambda_contrast`, `oracle_token_switch` | Rule-based switches between the greedy and contrast scores | Explored in exp6–exp10; none beat a fixed contrast. |

## Metrics and terms

| Code name | Standard term | Note |
|---|---|---|
| `mc1`, `mc2`, `mc3` | TruthfulQA MC1, MC2, MC3 (Lin et al., 2022) | Teacher-forced scoring of the answer options. |
| `switch_rate` | Premature-layer switch rate | Fraction of steps where the selected layer changes. |
| `shallow_bucket` | Candidate premature layers | Per-model default bucket in `src/panda/evaluator.py`. |
| `oref_*` (exp14) | Automatic reference-overlap scores for open-ended answers | Token F1 / win rate against TruthfulQA reference answers. |
| `manual_score_0_2` (exp14) | 0/1/2 judgement of an open-ended answer | 0 = false, 1 = mixed, 2 = correct. Who judged must be stated in the report (see `docs/experiment_log.md`). |
| "anchor", "frozen anchor" | Fixed premature layer | Use "premature layer" in the report; "anchor" only in the method name. |
| "jitter" | Layer-switching variance | Describe it as the premature layer changing between steps. |
