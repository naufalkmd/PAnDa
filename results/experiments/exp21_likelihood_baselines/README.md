# Experiment 21: Base-model likelihood for the eight exp20 models

exp20 compares self-evaluation with likelihood scoring on Qwen2.5-3B only, because no other model had likelihood
scores on these questions. This experiment scores the base model's option log-likelihood (`pure_greedy`, no
contrast) on all 817 TruthfulQA multiple-choice questions for the eight exp20 models, with the code path of exp19
and that one decoder only.

Run 01 repeats Qwen2.5-3B as a reproduction check against exp19 (`reproduction_check.json`).

## Protocol, fixed before any score of this experiment existed

`../exp20_self_evaluation/cross_model/likelihood_protocol.json`, written by `scripts/self_evaluation_vs_likelihood.py`:

- Data: the 417 exploration questions of exp20. The confirmation questions are not used, because self-evaluation
  was scored on them for Qwen2.5-3B only.
- Rules: self-evaluation (final-layer log-odds of `True` against `False`, the frozen exp20 method); base-model
  likelihood, sum and per token (token count from exp20); the longest option.
- Test: MC1 of self-evaluation minus MC1 of each likelihood rule, 95 % paired-bootstrap interval (10,000 resamples,
  seed 0) and exact McNemar; MC2 and MC3 differences reported.
- Statement: self-evaluation is said to beat likelihood scoring on a model if the MC1 difference against both
  likelihood rules is positive and both intervals exclude 0.
- Caveat: on Qwen2.5-3B the exploration questions are the ones the exp20 design was chosen on; its clean test is
  exp20's confirmation part. On the other seven models the method was fixed before their likelihood scores existed.

## Runs

| Run | Model |
|---|---|
| `run_01_qwen25_3b` | Qwen/Qwen2.5-3B-Instruct (reproduction check) |
| `run_02_gemma3_4b` | google/gemma-3-4b-it |
| `run_03_falcon3_3b` | tiiuae/Falcon3-3B-Instruct |
| `run_04_qwen25_15b` | Qwen/Qwen2.5-1.5B-Instruct |
| `run_05_qwen25_05b` | Qwen/Qwen2.5-0.5B-Instruct |
| `run_06_phi35_mini` | microsoft/Phi-3.5-mini-instruct |
| `run_07_gemma3_1b` | google/gemma-3-1b-it |
| `run_08_smollm2_17b` | HuggingFaceTB/SmolLM2-1.7B-Instruct |

```bash
python results/experiments/exp21_likelihood_baselines/run_experiment.py --run-id run_02_gemma3_4b --local-files-only
python scripts/self_evaluation_vs_likelihood.py      # writes ../exp20_self_evaluation/cross_model/self_evaluation_vs_likelihood.csv
```

A run row that already has results is never overwritten. 6.5–11.5 minutes per model on the RTX 5070 (70 minutes
for all eight, 2026-11-15): the exp19 scorer scores one option at a time and is limited by the CPU, not the GPU.

## Results

Reproduction check (`reproduction_check.json`): run 01 equals exp19 `pure_greedy` exactly on all 817 questions
(largest option-score difference 0.0 over 5,882 options; no question's MC1 differs).

Exploration questions of exp20 (417), MC1; differences are self-evaluation minus the likelihood rule with their 95 %
paired-bootstrap intervals. From `../exp20_self_evaluation/cross_model/self_evaluation_vs_likelihood.csv`.

| Model | Self-evaluation | Likelihood (sum) | Likelihood (per token) | Longest option (tokens) | − sum | − per token | Beats both |
|---|---|---|---|---|---|---|---|
| Qwen2.5-3B | 0.571 | 0.326 | 0.396 | 0.254 | +0.245 [+0.192, +0.297] | +0.175 [+0.122, +0.230] | yes |
| Gemma 3 4B | 0.573 | 0.314 | 0.391 | 0.264 | +0.259 [+0.199, +0.319] | +0.182 [+0.125, +0.240] | yes |
| Falcon3-3B | 0.367 | 0.240 | 0.295 | 0.259 | +0.127 [+0.070, +0.182] | +0.072 [+0.012, +0.129] | yes |
| Qwen2.5-1.5B | 0.400 | 0.242 | 0.331 | 0.254 | +0.158 [+0.106, +0.213] | +0.070 [+0.014, +0.125] | yes |
| Qwen2.5-0.5B | 0.237 | 0.211 | 0.269 | 0.254 | +0.026 [−0.024, +0.077] | −0.031 [−0.084, +0.022] | no (verdict at chance) |
| Phi-3.5-mini | 0.588 | 0.345 | 0.448 | 0.242 | +0.242 [+0.189, +0.295] | +0.139 [+0.082, +0.197] | yes |
| Gemma 3 1B | 0.295 | 0.249 | 0.317 | 0.264 | +0.046 [−0.007, +0.098] | −0.022 [−0.077, +0.034] | no |
| SmolLM2-1.7B | 0.331 | 0.247 | 0.309 | 0.245 | +0.084 [+0.031, +0.137] | +0.022 [−0.031, +0.074] | no |

By the rule fixed in the protocol, self-evaluation beats both likelihood rules on 5 of 8 models: Qwen2.5-3B,
Gemma 3 4B, Falcon3-3B, Qwen2.5-1.5B and Phi-3.5-mini. On the three others the difference with the per-token
likelihood is inside the noise (−0.031 to +0.022).

Caveats for the report:
- The protocol tests each model with its own interval and no multiple-comparison adjustment. For Falcon3-3B and
  Qwen2.5-1.5B the per-token interval only just excludes 0 (lower bounds +0.012 and +0.014; McNemar p 0.024 and
  0.018), so those two wins would not survive a Holm adjustment over the 16 MC1 comparisons. The three large wins
  (Qwen2.5-3B, Gemma 3 4B, Phi-3.5-mini) would.
- On Qwen2.5-3B these are the questions the exp20 design was chosen on; its clean test is exp20's confirmation part.
- The longest-option column counts tokens, as the protocol says, and so loses on ties (experiment log, issue 9).
  It is a reference, not one of the tested rules.

Terms: [`docs/glossary.md`](../../../docs/glossary.md).
