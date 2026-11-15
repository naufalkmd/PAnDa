# Glossary: code names → standard terms

**Rule.** Prose (report, README, docs) uses standard machine-learning terms only. Where a method has no standard
name, it is described with standard parts. The method is named with DoLa's own term: **per-question DoLa-static**
(formerly FAnDa) is DoLa-static with the fixed premature layer chosen per question instead of on a validation set. PAnDa, an earlier method, was dropped; its name
appears only in code and in the history notes.

Code identifiers (decoder names, experiment folders, CSV columns) are **not renamed**, because saved runs,
plots and figure JSON depend on them. This file maps them to the standard terms.

## Standard terms used

| Term | Meaning | Source |
|---|---|---|
| Contrastive decoding | Score tokens by the difference between a stronger and a weaker model's predictions | Li et al., 2023 |
| Adaptive plausibility constraint | Keep only tokens whose probability under the stronger distribution is at least α × the top token's probability (α = 0.1 here) | Li et al., 2023 |
| DoLa (decoding by contrasting layers) | Contrastive decoding between the final (**mature**) layer and an earlier (**premature**) layer of the same model | Chuang et al., 2024 |
| Premature / mature layer | The earlier layer whose early-exit logits are subtracted / the final layer | Chuang et al., 2024 |
| Dynamic premature-layer selection | Choosing, at each token, the candidate layer with the largest Jensen–Shannon divergence (JSD) to the mature layer | Chuang et al., 2024 |
| Static premature layer (DoLa-static) | One premature layer fixed in advance, chosen on a validation set | Chuang et al., 2024 |
| Candidate layers (bucket) | The set of layers the premature layer is chosen from | Chuang et al., 2024 |
| Softmax temperature τ | Logits are divided by τ before the softmax | — |
| Early exit | Applying the output head to an intermediate layer's hidden state | — |
| Self-evaluation, P(True) | Ask the model whether a proposed answer is true; the score is the probability (here the log-odds) of the reply token `True` against `False` | Kadavath et al., 2022 (to verify) |
| Partial-input baseline | A model or score that sees only part of the input (here: the option without the question); if it is accurate, the benchmark can be solved without the missing part | Gururangan et al., 2018; Poliak et al., 2018; Balepur et al., 2024 (to verify) |
| Selective prediction; coverage; risk–coverage curve | Answer only when a confidence reaches a threshold; coverage = share of questions answered; the curve plots accuracy (or error) against coverage | standard reference to verify |
| Exploration / confirmation split | Design choices made on one part of the data, then tested once on the other part with the design frozen in advance (pre-registration) | — |
| Length-matched pairwise accuracy | Share of (true, false) option pairs whose token counts differ by at most 1 in which the true option scores higher, averaged over questions. Not a standard name: define it once in the report | defined in this project |
| Greedy decoding; top-k, nucleus (top-p) truncation | Standard decoding baselines | Holtzman et al., 2020 |
| Jacobi (parallel) decoding | Refining a block of future tokens in parallel by fixed-point iteration | Santilli et al., 2023 |
| Teacher forcing, likelihood-based multiple-choice scoring | Each answer option is scored by its token log-likelihood given the question | — |
| MC1, MC2, MC3 | TruthfulQA multiple-choice metrics | Lin et al., 2022 |
| Development set, held-out set | Data used to make design choices / data never used for them | — |
| Exact McNemar test, paired bootstrap | Paired significance tests on per-question outcomes | — |
| Ablation, factorial design | Removing or crossing components to measure each one's effect | — |
| Oracle | An upper-bound variant that uses information unavailable at test time | — |

## Method labels

| Label | Standard description (write this first) |
|---|---|
| Per-question DoLa-static (formerly FAnDa; code name `fanda`) | DoLa with four changes: no adaptive plausibility constraint; raw-logit difference instead of log-probability difference; premature layer chosen by JSD at τ = 0.5 instead of 1; premature layer **selected once, at the first answer token, and kept fixed** instead of selected at every token. The first answer token has the same input (the prompt) for every option, so the layer is the same for all options of a question |
| PAnDa (dropped) | Contrastive decoding inside Jacobi-style blocks of 4 tokens. Up to the first position where the final-layer and contrastive distributions disagree (different top token and JSD above a threshold), tokens come from the final layer. From that position on, each token comes from the contrastive score if its top-token probability is within a fixed margin of the final layer's (`panda_truth_bias`), otherwise from the final layer |

## Code names

| Code name | Standard description | Note |
|---|---|---|
| `pure_greedy`, `greedy` | Base model (no contrast): the final-layer log-likelihood of each option. DoLa calls it the baseline | Named "greedy" in the code; under multiple-choice scoring nothing is decoded, so the report says "base model" |
| `dola`, `official_dola` | **DoLa (generation settings)**: dynamic premature-layer selection by DoLa's reference divergence (τ = 1), log-probability difference renormalised, adaptive plausibility constraint, candidate layers in the first quarter | The baseline of the development runs. Not DoLa's multiple-choice configuration (see `dola_mc_reference`) |
| `dola_mc_reference` | **DoLa (MC settings)**, as in DoLa's own TruthfulQA-MC evaluation: no plausibility constraint, option score = sum of log q_N − log q_M without renormalisation, candidate layers in the second half (blocks N/2, N/2 + 2, …, N − 2) | Added 2026-11-14 for exp19 |
| `relative_top` | Adaptive plausibility constraint | `relative_top_value` is the score given to masked tokens |
| `fanda` (exp11, exp18) | Per-question DoLa-static: premature layer selected once per question | |
| `fanda` (saved runs of exp5–exp10) | Per-question DoLa-static with the premature layer re-selected every 4 tokens | These runs (committed 2026-06-03) predate commit `efec350` (2026-06-04), which made `fanda` a fixed layer. Their numbers equal `fanda_update4`; rerunning them now would use the fixed layer |
| `fanda_update{k}`, `exp14_update{k}`, `always_contrast_update{k}` | Per-question DoLa-static scoring with the premature layer re-selected every k tokens ("selection interval k") | k = 1 is **not** DoLa: τ = 0.5 and no plausibility constraint |
| `fanda_frozen`, `exp14_frozen`, `always_contrast_frozen` | Per-question DoLa-static scoring with the premature layer selected once, at the first answer token (so once per question) | `update_every = 10**9` |
| `fanda_greedy` | Greedy decoding through the same code path (no contrast) | |
| `exp13_{logprob,logit}_{top,no_top}` | 2 × 2 factorial: log-probability vs. raw-logit difference × plausibility constraint on vs. off, with DoLa's layer selection | Without the constraint both differences rank tokens identically: log-softmax shifts all logits by the same constant |
| `fixed_alpha_dola{_low,,_high}` | Raw-logit contrastive score z_mature − α · z_premature with α = 0.0, 0.5, 1.0, premature layer re-selected every 4 tokens | α = 0 is greedy decoding; α = 1 equals `fanda_update4` (`src/panda/config.py`) |
| `matched_alpha_dola_0p{10,50,95}` | DoLa's log-probability score with the premature term weighted by α = 0.10, 0.50, 0.95 | exp1 |
| `top_k`, `top_p` | Top-k / nucleus truncation of the final-layer distribution, scored by likelihood | |
| `is_true`, `is_correct` (exp20) | The two self-evaluation prompt wordings: True/False after "Is the proposed answer true?"; Yes/No after "Is this answer correct?" | `is_true` is the frozen method |
| `verdict`, `no_question` (exp20 `wording_set`) | Self-evaluation with the question shown; the same prompt with the question removed (partial-input baseline) | |
| `corrected`, `sum` (exp20 prior correction) | Verdict minus / plus the question-free verdict | `corrected` was the tested method (rejected) |
| exploration / confirmation (exp20 `part`) | The 417 / 400 questions of the exp20 split (`split.json`, seed 20261115) | |
| `panda`, `panda_switch` | PAnDa (dropped; exploration only) | Not in the report's results |
| `*_switch*`, `ema_risk_switch` | Rule-based switch between greedy and contrastive scores at each token | EMA = exponential moving average of a divergence |
| `adaptive_lambda_contrast` | Contrastive score with a per-token weight set by a rule | |
| `oracle_token_switch` | Oracle switch: picks, per token, whichever score ranks the correct token higher | |
| `switch_rate` | Fraction of steps at which the selected premature layer changes | Report column: "layer changes (%)" |
| `selected_layer_match_rate` | Fraction of steps at which the selected layer equals the current max-JSD layer | |
| `shallow_bucket` | Candidate layers | Per-model default in `src/panda/evaluator.py` |
| `oref_true_f1`, `oref_win` (exp14) | Token-level F1 against the TruthfulQA reference answers; fraction of answers closer to a true than to a false reference | Automatic metric |
| `manual_score_0_2` (exp14) | 0/1/2 correctness label (0 false, 1 partly correct, 2 correct) | All 250 written by an LLM (Codex): see `experiment_log.md` |

## Words from older notes → standard terms

The older notes (the experiment READMEs, and the method notes, presentation and June course paper kept at the git
tag `pre-cleanup-2026-11`) use project words. Replace them in any new text:

| Older word | Standard term |
|---|---|
| anchor, frozen anchor, shallow anchor, contrast reference | premature layer; fixed premature layer |
| shallow layer | premature layer |
| persistence, refresh schedule, update schedule | selection interval (how often the premature layer is re-selected) |
| jitter, selector jitter | premature-layer changes between steps |
| staleness, stale anchor | the fixed layer is no longer the max-JSD layer |
| view (greedy view, contrast view, safe/truth view) | score or distribution (final-layer distribution, contrastive score) |
| always-contrast, fixed endpoint, regime | contrastive scoring at every step; fixed setting |
| arbitration, truth-biased arbitration | choosing between two scores |
| family | variants |
| lens, correction signal | contrastive score |
