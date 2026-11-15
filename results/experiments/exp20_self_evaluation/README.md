# Experiment 20: Self-evaluation scores, P(True), with selective prediction

exp19 showed that no likelihood or layer-contrast score separates true from false answer options on this model once
option length is controlled. This experiment scores each option by the model's own verdict instead: the base model
is asked whether the option is a true answer to the question, and the score is the log-odds of the reply token
`True` against `False` (self-evaluation, P(True); Kadavath et al., 2022, arXiv:2207.05221). The option with the
highest score is chosen. This takes one forward pass per option and no decoding.

The technique is known. What this experiment adds is a test of it against the likelihood and DoLa scores of
exp19 on the same questions, a reading of the verdict at intermediate layers (early exit), and selective
prediction (answer only when the two best options are far apart).

## Design, frozen before the confirmation questions were scored

- **Split.** The 817 questions are split once (`split.json`, seed 20261115) into an exploration part (417: the 50
  development questions and 367 others) and a confirmation part (400). Every choice below was made on the
  exploration part.
- **Method.** Score = log-odds of `True` against `False` at the first answer position, final layer, for the user
  message `Question: {question}\nProposed answer: {option}\nIs the proposed answer true? Reply with one word: True or False.`
- **Selective prediction.** Confidence = difference between the two highest scores among the MC1 options. The
  question is answered when the confidence reaches a threshold. Three thresholds were set on the exploration part,
  at 25 %, 50 % and 75 % coverage.
- **Ablations.** (a) Early exit: the mean of the same log-odds read after blocks 27–30 of 36 (final norm, then
  the output embedding). (b) A second wording, `{question}\n\nAnswer: {option}\n\nIs this answer correct? Reply with one word: Yes or No.`
- **Comparisons.** Method against the base model's option likelihood (sum, and per token) and against DoLa in its
  multiple-choice configuration, all three from the saved option scores of exp19; early exit against the method;
  the second wording against likelihood per token.
- **Tests.** Paired bootstrap (10,000 resamples, seed 0) for MC1, MC2 and MC3, exact McNemar for MC1, Holm
  adjustment over all 20 p-values. MC1 is the primary metric.

`frozen_design.json` holds this design and the thresholds. `scripts/self_evaluation_analysis.py confirmation`
stops if the design in the script differs from it, and `run_experiment.py` scores the confirmation part only when
the file exists. The confirmation run's metadata records the file's SHA-256.

## Runs

| Run | Part | Questions | Options | Time on the RTX 5070 |
|---|---|---|---|---|
| `run_01_qwen25_3b_exploration` | exploration | 417 | 3,021 | 71 s |
| `run_02_qwen25_3b_confirmation` | confirmation | 400 | 2,861 | 66 s |
| `run_03_gemma3_4b_exploration` | exploration | 417 | 3,021 | 120 s |
| `run_04_falcon3_3b_exploration` | exploration | 417 | 3,021 | 50 s |
| `run_05_qwen25_15b_exploration` | exploration | 417 | 3,021 | 44 s |
| `run_06_qwen25_05b_exploration` | exploration | 417 | 3,021 | 27 s |
| `run_07_phi35_mini_exploration` | exploration | 417 | 3,021 | 62 s |
| `run_08_gemma3_1b_exploration` | exploration | 417 | 3,021 | 48 s |
| `run_09_smollm2_17b_exploration` | exploration | 417 | 3,021 | 45 s |

Runs 01 and 02 use `Qwen/Qwen2.5-3B-Instruct`; the model of every other run is in `run_matrix.csv`. All runs
are in bfloat16, with both wordings and every block saved.

Runs 03 to 09 belong to the cross-model check below, and runs 10 to 17 (the eight models again, question
removed; `run_matrix.csv`) to the section after it. The frozen design, `scripts/self_evaluation_analysis.py`
and the confirmation results cover Qwen2.5-3B only. The confirmation questions of the other models have not
been scored.

```bash
python results/experiments/exp20_self_evaluation/run_experiment.py --run-id run_01_qwen25_3b_exploration
python scripts/self_evaluation_analysis.py exploration      # also writes frozen_design.json if it is missing
python results/experiments/exp20_self_evaluation/run_experiment.py --run-id run_02_qwen25_3b_confirmation
python scripts/self_evaluation_analysis.py confirmation
```

Each analysis writes `scores.csv`, `paired_tests.csv`, `selective_prediction.csv` and `option_classification.csv`
into the run's `analysis/` folder.

## Results on the confirmation part (400 questions, MC1 chance level 0.226)

| Scoring rule | MC1 | MC2 | MC3 | True beats false, token counts within 1 |
|---|---|---|---|---|
| Self-evaluation, final layer (the method) | 0.623 | 0.716 | 0.599 | 0.733 |
| Self-evaluation, second wording | 0.578 | 0.677 | 0.536 | 0.694 |
| Self-evaluation, early exit at blocks 27–30 | 0.685 | 0.746 | 0.641 | 0.781 |
| Base model likelihood, sum | 0.340 | 0.513 | 0.269 | 0.517 |
| Base model likelihood per token | 0.383 | 0.492 | 0.283 | 0.530 |
| DoLa, multiple-choice configuration | 0.398 | 0.599 | 0.320 | 0.542 |
| Per-question DoLa-static | 0.312 | 0.503 | 0.270 | 0.527 |
| Longest option (token count) | 0.325 | – | 0.277 | 0.567 |

MC2 for the self-evaluation rows uses the log-odds in place of the option log-likelihood.

| Comparison (MC1) | Difference | 95 % interval | Questions gained / lost |
|---|---|---|---|
| Method − base likelihood, sum | +0.282 | [+0.230, +0.338] | 131 / 18 |
| Method − base likelihood per token | +0.240 | [+0.182, +0.295] | 125 / 29 |
| Method − DoLa, multiple-choice configuration | +0.225 | [+0.163, +0.287] | 136 / 46 |
| Early exit − method | +0.062 | [+0.035, +0.092] | 31 / 6 |
| Second wording − base likelihood per token | +0.195 | [+0.138, +0.250] | 111 / 33 |

All five MC1 differences have a Holm-adjusted exact McNemar p below 0.001. The MC2 and MC3 differences are positive
in every comparison, with intervals that exclude 0 (`paired_tests.csv`).

Selective prediction with the method (thresholds from the exploration part):

| Threshold set for | Answered | Accuracy on answered | 95 % interval |
|---|---|---|---|
| 25 % coverage | 30.0 % | 0.900 | [0.843, 0.950] |
| 50 % coverage | 60.3 % | 0.788 | [0.735, 0.838] |
| 75 % coverage | 82.0 % | 0.686 | [0.635, 0.736] |
| all questions | 100 % | 0.623 | |

The confidence separates right from wrong answers with AUROC 0.783. The thresholds answered more questions on the
confirmation part than on the exploration part, so the coverage of a threshold does not transfer exactly.

The method's rank correlation with option token count within a question is +0.069 (base likelihood −0.281, DoLa
+0.791). As a classifier of single options the score has AUROC 0.747, but `True` is more likely than `False` for
only 24.8 % of the true options (9.3 % of the false ones): the score ranks options well and its zero point is not
a usable decision threshold.

The exploration part gave MC1 0.571 for the method, 0.640 for early exit and 0.537 for the second wording
(`runs/run_01_qwen25_3b_exploration/analysis/`).

## Cross-model check of the early-exit reading (exploration questions, eight models)

Does reading the verdict after an intermediate block beat the final layer on other models? The protocol is in
`cross_model/protocol.json`. It was fixed after the first three models (Qwen2.5-3B, Gemma 3 4B, Falcon3-3B) and
before the other five were scored. For each model, 50 questions are drawn as a labelled development set, the
block of the upper half of the network with the highest MC1 on them is chosen, and the gain over the final
layer is measured on the other 367 questions (500 draws). A model shows the gain if the mean gain is positive
and fewer than 5 % of the draws give a loss. Early exit would be presented as a method only if at least 6 of
the 8 models showed the gain.

```bash
python scripts/self_evaluation_layers.py      # writes cross_model/early_exit_selection.csv and early_exit_by_block.csv
```

Wording `is_true` (the primary wording), MC1 chance level 0.226:

| Model | Blocks | Final-layer MC1 | Chosen block (median) | Mean gain | 5 %–95 % of draws | Draws with a loss | Shows the gain |
|---|---|---|---|---|---|---|---|
| Qwen2.5-3B-Instruct | 36 | 0.571 | 29 | +0.065 | +0.014 to +0.082 | 2 % | yes |
| gemma-3-4b-it | 34 | 0.573 | 21 | +0.010 | -0.016 to +0.027 | 21 % | no |
| Falcon3-3B-Instruct | 22 | 0.367 | 15 | +0.073 | +0.041 to +0.090 | 1 % | yes |
| Qwen2.5-1.5B-Instruct (after the protocol) | 28 | 0.400 | 20 | +0.014 | -0.003 to +0.027 | 6 % | no |
| Qwen2.5-0.5B-Instruct (after the protocol) | 24 | 0.237 (at chance) | 16 | -0.009 | -0.041 to +0.000 | 71 % | no |
| Phi-3.5-mini-instruct (after the protocol) | 32 | 0.588 | 23 | -0.000 | -0.014 to +0.016 | 44 % | no |
| gemma-3-1b-it (after the protocol) | 26 | 0.295 | 16 | +0.007 | -0.011 to +0.022 | 19 % | no |
| SmolLM2-1.7B-Instruct (after the protocol) | 24 | 0.331 | 17 | +0.019 | -0.035 to +0.046 | 18 % | no |

2 of 8 models show the gain, and none of the five models scored after the protocol was fixed. The bar of
6 of 8 is not met, so early exit is not a general improvement of self-evaluation. It is an observation on
Qwen2.5-3B (confirmed on that model's confirmation questions, above) and Falcon3-3B. With the second wording,
1 of 8 models shows the gain (`cross_model/early_exit_selection.csv`).

The table also shows how much the final-layer score depends on the model: it is between 0.57 and 0.59 for three
of the four models with 3 to 4 billion parameters and between 0.24 and 0.40 for the models below 2 billion.

`meta-llama/Llama-3.2-3B-Instruct` was planned and left out because the repository is gated and access was not
granted. SmolLM2-1.7B takes its place.

## Verdict with the question removed (exploration questions, eight models)

Runs 10 to 17 score the same options with the question deleted from the user message, so the model sees only
`Proposed answer: {option}` and the instruction. This serves as a control (what does the option alone give
away?) and as the test of one method: subtracting the question-free verdict from the verdict, as pointwise mutual
information does for likelihoods. The protocol is in `cross_model/prior_protocol.json` and was fixed before any
question-free verdict was scored.

```bash
python scripts/self_evaluation_prior.py      # writes cross_model/prior_correction.csv
```

MC1, wording `is_true`, final layer, chance level 0.226:

| Model | Verdict, question shown | Verdict, question removed | Corrected (difference) | Corrected minus verdict, 95 % interval | Sum minus verdict, 95 % interval |
|---|---|---|---|---|---|
| Qwen2.5-3B-Instruct | 0.571 | 0.643 | 0.300 | -0.271 [-0.321, -0.221] | +0.094 [+0.055, +0.132] |
| gemma-3-4b-it | 0.573 | 0.554 | 0.278 | -0.295 [-0.345, -0.242] | +0.026 [-0.007, +0.062] |
| Falcon3-3B-Instruct | 0.367 | 0.468 | 0.197 | -0.170 [-0.218, -0.125] | +0.055 [+0.014, +0.096] |
| Qwen2.5-1.5B-Instruct | 0.400 | 0.405 | 0.314 | -0.086 [-0.132, -0.043] | +0.026 [-0.002, +0.058] |
| Qwen2.5-0.5B-Instruct | 0.237 (at chance, not counted) | 0.312 | 0.187 | -0.050 [-0.089, -0.012] | +0.014 [-0.012, +0.041] |
| Phi-3.5-mini-instruct | 0.588 | 0.552 | 0.283 | -0.305 [-0.357, -0.252] | +0.017 [-0.019, +0.053] |
| gemma-3-1b-it | 0.295 | 0.422 | 0.175 | -0.120 [-0.163, -0.077] | +0.065 [+0.026, +0.103] |
| SmolLM2-1.7B-Instruct | 0.331 | 0.338 | 0.242 | -0.089 [-0.132, -0.046] | +0.014 [-0.017, +0.046] |

- **Control.** The verdict ranks the options about as well without the question as with it: the question-free MC1
  is at least the MC1 with the question on 6 of 8 models (the two were not tested against each other). Each
  option is scored in its own forward pass, so this is not a comparison between options. On TruthfulQA the options
  are statements that can be judged alone, and the self-evaluation score of this experiment is therefore mostly a
  judgement of the option as a statement, not of the option as an answer to the question.
- **Method.** The corrected score shows a loss on 7 of the 7 counted models and a gain on 0. Subtracting
  the question-free verdict removes the signal. The method is rejected.
- **Sum.** Adding the two verdicts shows a gain on 3 of the 7 counted models and no loss. It was not part of
  the decision and is reported only.

That multiple-choice TruthfulQA can be answered above chance without the question is known for heuristics that
compare the options; the dataset's authors recommend a binary-choice version for that reason. Those sources are
not yet in the report's bibliography.

## Limits

- Multiple choice only. Open-ended generation was not tested: there the candidates would be sampled answers, and
  the method helps only if a true answer is among them.
- The comparison with DoLa exists for Qwen2.5-3B only. The comparison with base likelihood was extended to all
  eight models on the exploration questions by exp21 (2026-11-15; `cross_model/self_evaluation_vs_likelihood.csv`):
  self-evaluation beats both likelihood rules on 5 of 8 models.
- The block band 27–30 was chosen on the exploration part with the first wording. It was tested on the
  confirmation part with that wording only.
- Two wordings were tested. How much the score depends on the wording was not studied further.
- The self-evaluation score works about as well without the question (section above). The comparison with
  likelihood and DoLa scores on Qwen2.5-3B therefore shows that judging each option as a statement beats
  likelihood scoring on this benchmark. It does not show that the model answers the question better.
- The likelihood and DoLa scores were seen on all held-out questions during the exp19 analysis, before the split
  was made. Only the self-evaluation scores are new on the confirmation part.

Terms: [`docs/glossary.md`](../../../docs/glossary.md).
