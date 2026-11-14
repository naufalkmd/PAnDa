# Experiment log

One row per experiment: what it asked, what it found, where the numbers are, and whether the report uses it.
Terms follow [`glossary.md`](glossary.md); code names appear only in backticks. All runs use
`Qwen/Qwen2.5-3B-Instruct` on TruthfulQA multiple choice (MC1 / MC2 / MC3) unless noted. Numbers are copied from
each run's `*_summary.csv` under `results/experiments/<exp>/runs/<run>/`. Reprint them with
`python scripts/summarise_runs.py` before using them in the report.

**Notation.** *Selection interval k*: the premature layer is re-selected every k tokens; k = 1 means at every
token, k = ∞ means once, at the first token of the answer (`*_frozen`). FAnDa is defined in the glossary.

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
| exp5 | Do Jacobi blocks help on top of FAnDa (k = 4)? | n = 10 and n = 30 only; blocks never beat FAnDa (n = 30: 0.267 vs 0.367) at about 2× the time per step | One sentence |
| exp6 | Four rule-based switches between greedy and contrastive scores | Best MC1 0.38 (`guarded_argmax_switch`); every MC2 ≤ 0.520 | One sentence |
| exp7 | A switch vs. its two fixed settings (always greedy, always contrastive) | Contrastive at every step (FAnDa, k = 4) 0.40/0.576/0.351 best; greedy 0.34; best switch 0.38 | Yes (negative result) |
| exp8 | Is the switch limited by its rule? (oracle switch) | Oracle switch 0.36 < contrastive at every step 0.40 | Yes (negative result) |
| exp9 | Contrastive weight set per token by a rule | 0.36/0.561/0.325 < fixed weight 0.40/0.576/0.351 | One sentence |
| exp10 | Switch gated by an exponential moving average of the divergence | 0.34/0.531/0.307 < contrastive at every step 0.40/0.529/0.353 | One sentence |

## Main experiments (exp11–exp18)

| Exp | Question | Result | Source | Report |
|---|---|---|---|---|
| exp11 | Main comparison | Greedy 0.34/0.531/0.307 (39.2 ms per step); top-k 0.34; top-p 0.36; DoLa 0.26/0.526/0.268 (78.7 ms); FAnDa 0.40/0.557/0.364 (80.4 ms); PAnDa 0.34/0.562/0.324 (173.9 ms) | `exp11.../run_01_default` | Main table |
| exp12 | Selection interval k ∈ {1, 2, 4, ∞} | k = 1: 0.34/0.534/0.294 (layer changes at 69.2 % of steps); k = 2: 0.38/0.527/0.331; k = 4: 0.40/0.576/0.351 (13.5 %); k = ∞: 0.40/0.560/0.364 (0 %) | `exp12.../run_01_default` | Yes |
| exp13 | 2 × 2 factorial: log-probability vs. raw-logit difference × plausibility constraint, with DoLa's layer selection | log-prob + constraint 0.28/0.528/0.273 (= DoLa); raw-logit + constraint 0.30/0.520/0.300; no constraint, both differences (identical) 0.38/0.527/0.329 | `exp13.../run_01_default` | Yes |
| exp14 | Open-ended generation (64 new tokens), k ∈ {1, 2, 4, 8, ∞} | Token F1 against the true references 0.188–0.211; fraction closer to a true than a false reference 0.36–0.52; no consistent order across k. 0/1/2 correctness labels: **all 250 written by an LLM (Codex), none checked by a person** | `exp14.../run_01_default` (`*_manual_eval.csv`, column `reviewer = codex`) | Only with the labeller stated, or after human review |
| exp15 | Where do the k = ∞ and k = 1 generations first differ (8 selected questions)? | `*_assistant_full_verdict.csv`: 8 judgements by an LLM assistant; prefix sheet (80 rows) **not labelled** | `exp15.../run_01_default` | Case study only, labeller stated |
| exp16 | Does the ranking over k hold on other random subsets? | Original subset = exp12 (+ k = 8: 0.38/0.561/0.344). **New subset, seed 101:** k = 1: 0.30/0.536/0.273; k = 8: 0.32/0.531/0.315; k = ∞: 0.30/0.520/0.306. The exp12 ranking does **not** replicate. Seeds 202/303/404: **not run** | `exp16.../run_01_anchor_subset`, `run_02_seed_101` | Yes |
| exp17 | Token-level traces of high- and low-scoring k = 1 open-ended answers | Traces and figure only | `exp17...` | Possibly a figure |
| exp18 | Transfer to other models (same 50 questions) | Gemma 3 4B: greedy 0.28/0.432/0.248, DoLa 0.28/0.490/0.272, FAnDa 0.30/0.587/0.284. Falcon 3 3B: greedy 0.26/0.406/0.231, DoLa 0.22/0.442/0.214, FAnDa 0.26/0.478/0.228. HINT self-calibrated Qwen 1.5B: greedy 0.30/0.428/0.247, DoLa 0.24/0.404/0.208, FAnDa 0.24/0.413/0.206 | `exp18.../run_0{1,2,4}_*` | Yes, all baselines present |

## Known issues (fix in the report, or rerun)

1. **The course report's main table mixes runs.** Its FAnDa row is from exp12 (k = ∞), its DoLa row from exp4/exp13
   (0.28, not exp11's 0.26), and its top-k/top-p rows from exp4 (0.04/0.00), while exp11's own top-k/top-p equal
   greedy. Build every table from one run.
2. **`fanda` names two decoders**: k = 4 in the saved runs of exp5–exp10 (committed 2026-06-03), k = ∞ from
   commit `efec350` (2026-06-04) on, so in exp11/exp18 and in any rerun of exp5–exp10.
3. **k = 1 is not DoLa.** The FAnDa variants select the layer by JSD at τ = 0.5; DoLa and exp13 use τ = 1. The
   difference between DoLa and FAnDa therefore combines four changes: no plausibility constraint, raw-logit
   difference, τ = 0.5, and k = ∞. No run isolates τ.
4. **The layer is fixed per scored answer option, not per question.** Each option is scored from a fresh state,
   so two options of one question can use different premature layers.
5. **exp4 top-k/top-p of 0.04/0.00** probably predate the full-distribution fallback that exp11's README
   describes (not yet checked in the git history). Use exp11's numbers.
6. **exp16 seed 101 ran on different hardware** (about 666 ms per step vs. 86 ms), with an **uncommitted code
   version** (decoders named `always_contrast_*`; no commit defines them). Its metadata records the same selection
   intervals and the 50 dataset indices (`truthfulqa_sampling.selected_source_indices`), but the code cannot be
   checked. Compare its scores, not its latency, and rerun it under the current code before relying on it.
7. **Open-ended labels are LLM-written** (exp14, exp15).
