# Experiment log

One row per experiment: what it asked, what it found, where the numbers are, and whether the report uses it.
Terms follow [`glossary.md`](glossary.md); code names appear only in backticks. All runs use
`Qwen/Qwen2.5-3B-Instruct` on TruthfulQA multiple choice (MC1 / MC2 / MC3) unless noted. Numbers are copied from
each run's `*_summary.csv` under `results/experiments/<exp>/runs/<run>/`. Reprint them with
`python scripts/summarise_runs.py` before using them in the report.

**Notation.** *Selection interval k*: the premature layer is re-selected every k tokens; k = 1 means at every
token, k = ∞ means once, at the first token of the answer (`*_frozen`). Per-question DoLa-static is defined in the glossary.

**Data.** Unless noted, every run uses the same 50 questions (seed 42). They served as the development set: the
method was designed on them and the results were reported on them. There is no held-out set yet.

**Noise.** With n = 50 the standard error of MC1 is about 0.065–0.07. DoLa scores 0.26 (exp11) and 0.28 (exp1,
exp4, exp7, exp8, exp13) on the same questions, so a difference of 0.02 is within run-to-run variation.

## Development history (exp1–exp10)

| Exp | Question | Result (MC1 / MC2 / MC3) | Report |
|---|---|---|---|
| exp1 | Does a fixed contrastive weight α beat DoLa? | DoLa 0.28/0.528/0.273; α = 0.1: 0.34/0.525/0.306; α = 0.95: 0.30/0.527/0.280 | Background only |
| exp2 | Does a two-token look-ahead help PAnDa's choice between scores (without blocks)? | one token 0.36/0.570/0.318; two tokens 0.34/0.534/0.300 at 1.8× the time per step | No |
| exp4 | Baselines | Raw-logit contrast with α = 0 (= greedy): 0.34/0.531/0.307; α = 0.5: 0.36/0.565/0.315; α = 1: 0.40/0.576/0.351; DoLa 0.28; top-k 0.04, top-p 0.00 (scoring problem: see issue 5) | No |
| exp5 | Do Jacobi blocks help on top of per-question DoLa-static (k = 4)? | n = 10 and n = 30 only; blocks never beat per-question DoLa-static (n = 30: 0.267 vs 0.367) at about 2× the time per step | One sentence |
| exp6 | Four rule-based switches between greedy and contrastive scores | Best MC1 0.38 (`guarded_argmax_switch`); every MC2 ≤ 0.520 | One sentence |
| exp7 | A switch vs. its two fixed settings (always greedy, always contrastive) | Contrastive at every step (per-question DoLa-static, k = 4) 0.40/0.576/0.351 best; greedy 0.34; best switch 0.38 | Yes (negative result) |
| exp8 | Is the switch limited by its rule? (oracle switch) | Oracle switch 0.36 < contrastive at every step 0.40 | Yes (negative result) |
| exp9 | Contrastive weight set per token by a rule | 0.36/0.561/0.325 < fixed weight 0.40/0.576/0.351 | One sentence |
| exp10 | Switch gated by an exponential moving average of the divergence | 0.34/0.531/0.307 < contrastive at every step 0.40/0.529/0.353 | One sentence |

## Main experiments (exp11–exp18)

| Exp | Question | Result | Source | Report |
|---|---|---|---|---|
| exp11 | Main comparison | Greedy 0.34/0.531/0.307 (39.2 ms per step); top-k 0.34; top-p 0.36; DoLa 0.26/0.526/0.268 (78.7 ms); per-question DoLa-static 0.40/0.557/0.364 (80.4 ms); PAnDa 0.34/0.562/0.324 (173.9 ms) | `exp11.../run_01_default` | Main table |
| exp12 | Selection interval k ∈ {1, 2, 4, ∞} | k = 1: 0.34/0.534/0.294 (layer changes at 69.2 % of steps); k = 2: 0.38/0.527/0.331; k = 4: 0.40/0.576/0.351 (13.5 %); k = ∞: 0.40/0.560/0.364 (0 %) | `exp12.../run_01_default` | Yes |
| exp13 | 2 × 2 factorial: log-probability vs. raw-logit difference × plausibility constraint, with DoLa's layer selection | log-prob + constraint 0.28/0.528/0.273 (= DoLa); raw-logit + constraint 0.30/0.520/0.300; no constraint, both differences (identical) 0.38/0.527/0.329 | `exp13.../run_01_default` | Yes |
| exp14 | Open-ended generation (64 new tokens), k ∈ {1, 2, 4, 8, ∞} | Token F1 against the true references 0.188–0.211; fraction closer to a true than a false reference 0.36–0.52; no consistent order across k. 0/1/2 correctness labels: **all 250 written by an LLM (Codex), none checked by a person** | `exp14.../run_01_default` (`*_manual_eval.csv`, column `reviewer = codex`) | Only with the labeller stated, or after human review |
| exp15 | Where do the k = ∞ and k = 1 generations first differ (8 selected questions)? | `*_assistant_full_verdict.csv`: 8 judgements by an LLM assistant; prefix sheet (80 rows) **not labelled** | `exp15.../run_01_default` | Case study only, labeller stated |
| exp16 | Does the ranking over k hold on other random subsets? | Original subset = exp12 (+ k = 8: 0.38/0.561/0.344). **New subset, seed 101:** k = 1: 0.30/0.536/0.273; k = 8: 0.32/0.531/0.315; k = ∞: 0.30/0.520/0.306. The exp12 ranking does **not** replicate. Seeds 202/303/404: **not run** | `exp16.../run_01_anchor_subset`, `run_02_seed_101` | Yes |
| exp17 | Token-level traces of high- and low-scoring k = 1 open-ended answers | Traces and figure only | `exp17...` | Possibly a figure |
| exp18 | Transfer to other models (same 50 questions) | Gemma 3 4B: greedy 0.28/0.432/0.248, DoLa 0.28/0.490/0.272, per-question DoLa-static 0.30/0.587/0.284. Falcon 3 3B: greedy 0.26/0.406/0.231, DoLa 0.22/0.442/0.214, per-question DoLa-static 0.26/0.478/0.228. HINT self-calibrated Qwen 1.5B: greedy 0.30/0.428/0.247, DoLa 0.24/0.404/0.208, per-question DoLa-static 0.24/0.413/0.206 | `exp18.../run_0{1,2,4}_*` | Yes, all baselines present |

## Paired tests on the development set (2026-11-14)

`python scripts/paired_tests.py RUN_DIR --pairs A:B ...` (exact McNemar on MC1; paired bootstrap, 10,000 resamples,
seed 0, on all three). n = 50 in every row; p-values are **not** adjusted for multiple comparisons unless noted.

| Comparison (run) | MC1 diff (b/c, p McNemar) | MC2 diff (p) | MC3 diff (p) |
|---|---|---|---|
| Per-question DoLa-static − DoLa (exp11) | +0.140 (9/2, 0.065) | +0.031 (0.58) | +0.096 (0.005) |
| Per-question DoLa-static − greedy (exp11) | +0.060 (4/1, 0.375) | +0.026 (0.48) | +0.057 (0.07) |
| DoLa − greedy (exp11) | −0.080 (3/7, 0.344) | −0.004 (0.94) | −0.039 (0.31) |
| PAnDa − greedy (exp11) | 0.000 (3/3, 1.0) | +0.032 (0.30) | +0.017 (0.57) |
| Constraint off − on, log-prob (exp13) | +0.100 (7/2, 0.180) | −0.000 (0.98) | +0.056 (0.12) |
| Raw-logit − log-prob, constraint on (exp13) | +0.020 (2/1, 1.0) | −0.008 (0.45) | +0.027 (0.13) |
| k = ∞ − k = 1 (exp12) | +0.060 (4/1, 0.375) | +0.026 (0.46) | +0.071 (< 0.001) |
| k = ∞ − k = 4 (exp12) | 0.000 (0/0, 1.0) | −0.016 (0.33) | +0.013 (0.42) |
| k = ∞ − k = 1 (exp16, seed 101) | 0.000 (1/1, 1.0) | −0.016 (0.53) | +0.033 (0.09) |
| Per-question DoLa-static − greedy, Gemma 3 4B (exp18) | +0.020 (5/4, 1.0) | +0.155 (0.017) | +0.036 (0.36) |
| Per-question DoLa-static − DoLa, Gemma 3 4B (exp18) | +0.020 (2/1, 1.0) | +0.097 (0.09) | +0.012 (0.62) |
| Per-question DoLa-static − greedy, Falcon 3 3B (exp18) | 0.000 (4/4, 1.0) | +0.073 (0.22) | −0.003 (0.92) |
| Per-question DoLa-static − greedy, HINT Qwen 1.5B (exp18) | −0.060 (3/6, 0.508) | −0.015 (0.72) | −0.041 (0.33) |

Reading, on the development set only:

- Per-question DoLa-static beats DoLa on MC3 (p = 0.005) and, less clearly, on MC1 (McNemar p = 0.065). It does **not** beat
  greedy decoding on any metric for Qwen2.5-3B, and DoLa does not beat greedy either.
- Removing the plausibility constraint gives the largest single MC1 change (+0.10), but it is not significant at n = 50.
- The selection-interval effect is significant only on MC3 (k = 1 vs. longer intervals), and not on seed 101.
- The only significant cross-model gain is per-question DoLa-static over greedy on Gemma 3 4B MC2 (p = 0.017, unadjusted).
- With this many comparisons, an unadjusted p ≈ 0.02–0.07 is weak evidence. The held-out run (R2, n = 767)
  is what can settle the per-question DoLa-static vs. DoLa and per-question DoLa-static vs. greedy questions.

## Known issues (fix in the report, or rerun)

1. **The course report's main table mixes runs.** Its per-question DoLa-static row is from exp12 (k = ∞), its DoLa row from exp4/exp13
   (0.28, not exp11's 0.26), and its top-k/top-p rows from exp4 (0.04/0.00), while exp11's own top-k/top-p equal
   greedy. Build every table from one run.
2. **`fanda` names two decoders**: k = 4 in the saved runs of exp5–exp10 (committed 2026-06-03), k = ∞ from
   commit `efec350` (2026-06-04) on, so in exp11/exp18 and in any rerun of exp5–exp10.
3. **k = 1 is not DoLa.** The decoders with selection interval k (`fanda_update{k}`) select the layer by JSD at τ = 0.5; DoLa and exp13 use τ = 1. The
   difference between DoLa and per-question DoLa-static therefore combines four changes: no plausibility constraint, raw-logit
   difference, τ = 0.5, and k = ∞. No run isolates τ.
4. **With k = ∞ the premature layer is the same for all options of a question.** Each option is scored from a
   fresh state, but the layer is selected at the first answer token, whose input is the prompt alone, so every
   option gets the same layer. (Corrected 2026-11-14; an earlier version of this log said the opposite.)
5. **exp4 top-k/top-p of 0.04/0.00** probably predate the full-distribution fallback that exp11's README
   describes (not yet checked in the git history). Use exp11's numbers.
6. **exp16 seed 101 ran on different hardware** (about 666 ms per step vs. 86 ms), with an **uncommitted code
   version** (decoders named `always_contrast_*`; no commit defines them). Its metadata records the same selection
   intervals and the 50 dataset indices (`truthfulqa_sampling.selected_source_indices`), but the code cannot be
   checked. Compare its scores, not its latency, and rerun it under the current code before relying on it.
7. **Open-ended labels are LLM-written** (exp14, exp15).

## Setup audit (2026-11-14, before the held-out run)

Checked against the code and against DoLa's reference code (github.com/voidism/DoLa: `tfqa_mc_eval.py`, `dola.py`).

| # | Finding | Effect | Action |
|---|---|---|---|
| A1 | **Our `dola` is not DoLa's multiple-choice configuration.** DoLa's TruthfulQA-MC script uses no plausibility constraint (`relative_top` 0.0), an un-renormalised option score (`post_softmax=False`), and candidate layers in the second half (16–30 of 32). Ours uses the constraint (0.1), renormalises, and uses the first quarter (blocks 1–9 of 36): DoLa's generation settings. | The development-set gap DoLa → per-question DoLa-static is partly a baseline-configuration effect; removing the constraint (C1) repeats DoLa's own MC setting. | New decoder `dola_mc_reference` (DoLa's MC settings, late layers transferred by relative depth) added to exp19. The report shows both DoLa configurations. |
| A2 | **The divergence differs.** DoLa's reference code computes ½[KL(m‖q_N) + KL(m‖q_j)]; per-question DoLa-static uses the standard JSD at τ = 0.5. | One more difference between DoLa and per-question DoLa-static (issue 3). | Stated in the Method; optional R3. |
| A3 | **With k = ∞ the layer is chosen from the question.** | See issue 4 (corrected). | Method corrected. |
| A4 | **"Greedy" decodes nothing under multiple-choice scoring.** It is the base model's log-likelihood of each option (DoLa calls it the baseline). | Naming only. | The report calls it "base model (no contrast)". |
| A5 | **The prompt is not the standard TruthfulQA-MC prompt.** Ours: chat template, the question, then "Answer with one of the provided answer options only." (the options are never shown). DoLa and TruthfulQA use a 6-shot Q/A primer without a chat template. Each option is appended after the assistant turn with a leading space. | Same for every decoder, so comparisons between decoders are valid; absolute scores are not comparable with published TruthfulQA-MC numbers. | Kept, so the held-out run matches the development runs; stated as a limitation. |
| A6 | **Candidate layers were never tuned** for any model (first quarter for DoLa (generation settings), PAnDa and per-question DoLa-static; second half for DoLa (MC settings)). | DoLa chose its candidate set on a validation set. | Stated as a limitation. |
| A7 | **exp11 DoLa 0.26 vs exp4/exp13 DoLa 0.28**: one question differs, with its MC1 margin moving from +0.233 to −0.127. Too large for floating-point noise, so a code change between 2026-06-03 and 2026-06-09. | Old development runs are not all from one code version. | exp19 runs every decoder under one code version, and its environment is recorded. |
| A8 | **The June environment is lost** (torch came from the system Python and is gone). | Old runs cannot be reproduced bit for bit. | New pinned environment (`requirements-lock.txt`); exp19's 50 development questions check how close it comes. |
| A9 | Statistics: unit = question; paired tests (McNemar on MC1, paired bootstrap); Holm adjustment across a family of comparisons; held-out = the 767 non-development questions. | — | `scripts/paired_tests.py`. |
| A10 | Teacher forcing recomputes the full forward pass for every answer token (`use_cache=False`). | Correct but slow (the reason for ~19 h). | None. |
