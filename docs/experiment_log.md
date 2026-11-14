# Experiment log

One row per experiment: what it asked, what it found, where the numbers are, and whether the report uses it.
Terms follow [`glossary.md`](glossary.md). All runs use `Qwen/Qwen2.5-3B-Instruct` on TruthfulQA multiple choice
(MC1 / MC2 / MC3) unless noted. Numbers below are copied from each run's `*_summary.csv` under
`results/experiments/<exp>/runs/<run>/`. Reprint them with `python scripts/summarise_runs.py` before using them in the report.

**Subset.** Unless noted, every run uses the same 50 questions (seed 42). These 50 questions were used both to
develop the method and to report it: there is no held-out set yet.

**Noise.** With n = 50 the standard error of MC1 is about 0.065–0.07. Official DoLa itself scores 0.26 (exp11) and
0.28 (exp1, exp4, exp7, exp8, exp13) on the same questions, so a 0.02 difference is within run-to-run variation.

## Development history (exp1–exp10)

| Exp | Question | Result (MC1 / MC2 / MC3) | Report |
|---|---|---|---|
| exp1 | Does a fixed contrast weight α beat official DoLa? | DoLa 0.28/0.528/0.273; α = 0.1: 0.34/0.525/0.306; α = 0.95: 0.30/0.527/0.280 | Background only |
| exp2 | Does a longer look-ahead horizon help arbitration (PAnDa without blocks)? | h1 0.36/0.570/0.318; h2 0.34/0.534/0.300 at 1.8× the step time | No |
| exp4 | Baseline families | Greedy-like α = 0.1 0.34; α = 0.95 (`fixed_alpha_dola_high`) 0.40/0.576/0.351; DoLa 0.28; top-k 0.04, top-p 0.00 (a scoring bug: see issues) | No |
| exp5 | Do speculative blocks help on top of a fixed contrast? | n = 10 and n = 30 only; blocks never beat `fanda` (n = 30: 0.367 vs 0.267) at about 2× the step time | One sentence |
| exp6 | Four rule-based switches between greedy and contrast | Best MC1 0.38 (`guarded_argmax_switch`), all MC2 ≤ 0.520 | One sentence |
| exp7 | Switch vs. the two fixed endpoints | Always-contrast (`fanda`, update4) 0.40/0.576/0.351 best; greedy 0.34; best switch 0.38 | Yes (negative result) |
| exp8 | Is the switch limited by its gate? (oracle token switch) | Oracle switch 0.36 < always-contrast 0.40 | Yes (negative result) |
| exp9 | Adaptive contrast weight | 0.36/0.561/0.325 < always-contrast 0.40/0.576/0.351 | One sentence |
| exp10 | EMA risk-gated switch | 0.34/0.531/0.307 < always-contrast 0.40/0.529/0.353 | One sentence |

## Main experiments (exp11–exp18)

| Exp | Question | Result | Source | Report |
|---|---|---|---|---|
| exp11 | Core comparison | Greedy 0.34/0.531/0.307 (39.2 ms/step); top-k 0.34; top-p 0.36; DoLa 0.26/0.526/0.268 (78.7 ms); FAnDa (fixed layer) 0.40/0.557/0.364 (80.4 ms); PAnDa 0.34/0.562/0.324 (173.9 ms) | `exp11.../run_01_default` | Main table |
| exp12 | Layer re-selection interval k ∈ {1, 2, 4, ∞} | update1 0.34/0.534/0.294 (switch rate 0.692); update2 0.38/0.527/0.331; update4 0.40/0.576/0.351 (0.135); fixed 0.40/0.560/0.364 (0) | `exp12.../run_01_default` | Yes |
| exp13 | 2 × 2: score space × plausibility constraint (per-token DoLa selection) | log-prob + constraint 0.28/0.528/0.273 (= DoLa); raw-logit + constraint 0.30/0.520/0.300; no constraint (both score spaces, identical) 0.38/0.527/0.329 | `exp13.../run_01_default` | Yes |
| exp14 | Open-ended generation (64 new tokens), k ∈ {1, 2, 4, 8, ∞} | Automatic reference overlap: true-F1 0.188–0.211, win rate 0.36–0.52, no consistent order. 0/1/2 scores: **all 250 written by Codex (LLM), none reviewed by a person** | `exp14.../run_01_default` (`*_manual_eval.csv`: `reviewer = codex`) | Only with the scorer stated, or after human review |
| exp15 | Where do fixed-layer and update1 generations diverge (8 selected questions) | `assistant_full_verdict.csv`: 8 verdicts by an assistant (not a person); prefix sheet (80 rows) **unreviewed** | `exp15.../run_01_default` | Case study only, scorer stated |
| exp16 | Does the k ranking hold on fresh subsets? | Anchor subset = exp12 (+ update8 0.38/0.561/0.344). **Fresh subset, seed 101:** update1 0.30/0.536/0.273; update8 0.32/0.531/0.315; fixed 0.30/0.520/0.306. The exp12 ranking does **not** replicate. Seeds 202/303/404: **not run** | `exp16.../run_01_anchor_subset`, `run_02_seed_101` | Yes (required for honesty) |
| exp17 | Token-level traces of strong and weak update1 open-ended answers | Traces and figure only | `exp17...` | Possibly a figure |
| exp18 | Transfer to other models (same 50 questions) | Gemma 3 4B: greedy 0.28/0.432/0.248, DoLa 0.28/0.490/0.272, FAnDa 0.30/0.587/0.284. Falcon 3 3B: greedy 0.26/0.406/0.231, DoLa 0.22/0.442/0.214, FAnDa 0.26/0.478/0.228. HINT self-cal Qwen 1.5B: greedy 0.30/0.428/0.247, DoLa 0.24/0.404/0.208, FAnDa 0.24/0.413/0.206 | `exp18.../run_0{1,2,4}_*` | Yes, all baselines filled |

## Known issues (fix in the report, or rerun)

1. **The course report's main table mixes runs.** Its FAnDa row is exp12 `fanda_frozen`, its DoLa row is from
   exp4/exp13 (0.28, not exp11's 0.26), and its top-k/top-p rows are from exp4 (0.04/0.00), while exp11's own top-k/top-p equal greedy. Rebuild every table from one run per table.
2. **`fanda` means two different decoders**: re-selection every 4 tokens in exp7–exp10, and a fixed layer in exp11/exp18.
3. **update1 is not DoLa.** The FAnDa family selects the layer by JSD at τ = 0.5; DoLa and exp13 use τ = 1. The
   DoLa → FAnDa difference therefore combines four changes: plausibility constraint off, raw-logit score,
   τ = 0.5 selection, fixed layer. No run isolates the τ change.
4. **The layer is fixed per scored answer, not per question.** Each answer option is scored from a fresh state, so different options of one question can use different layers.
5. **exp4 top-k/top-p of 0.04/0.00** are probably from truncation before the full-distribution fallback that
   exp11's README describes (not yet checked in the git history). Either way, use exp11's numbers.
6. **exp16 run_02 ran on different hardware** (about 666 ms/step vs. 86 ms): compare its quality, not its latency.
7. **Open-ended scores are LLM-written** (see exp14/exp15 above).
