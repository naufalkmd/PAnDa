# What multiple-choice TruthfulQA rewards: layer contrast, self-evaluation and option length

Code, saved runs and report of an empirical study of scoring rules on TruthfulQA multiple choice (MC1 / MC2 /
MC3) with small instruction-tuned language models (Qwen2.5-3B-Instruct and seven others of 0.5 to 4 billion
parameters). The rules are the base model's likelihood, DoLa (decoding by contrasting layers, Chuang et al., 2024)
in two configurations, per-question DoLa-static (a DoLa variant we developed), and self-evaluation, P(True)
(Kadavath et al., 2022).

The report is `paper/report.tex`. Every number in it is read from the saved runs in `results/experiments/`
by the scripts under [Rebuild the report](#rebuild-the-report).

## Findings

- **Small development sets mislead.** Per-question DoLa-static led the base likelihood by +0.06 MC1 on the 50
  questions it was developed on and trails it by −0.034 [−0.060, −0.008] on the other 767 questions. No
  layer-contrast rule beats the likelihood on the held-out questions.
- **Settings copied from generation break multiple-choice scoring.** Under DoLa's generation settings, the adaptive
  plausibility constraint masks tokens of every option, and the number of masked tokens alone decides MC1 on 73 %
  of the held-out questions. DoLa's paper and its released multiple-choice script differ on whether the constraint
  is used.
- **Scores follow option length.** DoLa's multiple-choice configuration cannot be told apart from choosing the
  longest option (MC1 0.356 vs 0.361). On true and false options of nearly equal length, every likelihood and
  contrast rule is close to chance.
- **Self-evaluation wins, but judges statements.** Under a design frozen before 400 confirmation questions,
  self-evaluation reaches MC1 0.623 against 0.340 for the likelihood and 0.398 for DoLa, and it beats the likelihood
  on 5 of 8 models. With the question removed from the prompt it is as accurate on 6 of 8 models.

Every experiment, its result and the known issues: [`docs/experiment_log.md`](docs/experiment_log.md). Code names →
standard terms: [`docs/glossary.md`](docs/glossary.md).

**Names.** The Python package is `truthfulqa_scoring`. Until 2026-11-15 it was called `panda`, after PAnDa, an
earlier block-wise decoding method that was dropped; the PAnDa decoder (`decoders/panda.py`) stays because saved
exploration runs used it. Per-question DoLa-static was called FAnDa in the June 2026 course version, and the code
names of the scoring rules in the saved runs still use `fanda` (they are kept so the saved results stay readable).

## Install

Linux or WSL with Python 3.12 and an NVIDIA GPU (CUDA 12.8 driver). From the repository root:

```bash
bash scripts/setup_env.sh
```

This creates `.venv` from `requirements-lock.txt`, the exact versions of every package (PyTorch 2.9.1 with
CUDA 12.8, transformers 4.57.6, datasets 4.8.5, huggingface_hub 0.36.2), and installs this package without
changing them. `requirements.txt` lists the direct dependencies; `bash scripts/setup_env.sh --lock` re-resolves it
and rewrites the lock file. Keep `huggingface_hub` below 1.0: newer versions reject the dataset id `truthful_qa`.

For gated models (Gemma 3), or models not cached locally, export `HF_TOKEN` (or `HUGGINGFACE_HUB_TOKEN`).

## Rebuild the report

These steps read the saved per-question scores; no GPU is needed. Run them from the repository root (the analysis
scripts need `datasets` for the TruthfulQA labels):

```bash
PY="env HF_HUB_OFFLINE=1 ./.venv/bin/python"
$PY scripts/heldout_analysis.py --out-dir results/experiments/exp19_heldout_full/runs/run_01_qwen25_3b_full/analysis
$PY scripts/self_evaluation_analysis.py exploration     # exp20: writes frozen_design.json only if it is missing
$PY scripts/self_evaluation_analysis.py confirmation    # stops if the design differs from frozen_design.json
$PY scripts/self_evaluation_layers.py                   # early exit on eight models
$PY scripts/self_evaluation_prior.py                    # question-removed control
$PY scripts/self_evaluation_vs_likelihood.py            # self-evaluation vs likelihood on eight models (exp21)
python scripts/report_tables.py                         # writes paper/tables/*.tex
python scripts/figure_data.py                           # writes paper/figures/data/*.csv
cd paper && latexmk -pdf -outdir=build report.tex # writes paper/build/report.pdf
```

`scripts/paired_tests.py` runs the paired bootstrap and the exact McNemar test between any two rules of a run.

## Run an experiment

Each experiment in `results/experiments/expN_*/` has a `run_experiment.py`, a `run_matrix.csv` (one row per
run), a README, and its saved outputs in `runs/<run_id>/`. A runner never overwrites a finished run. For example,
the base-model likelihood of one model on all 817 questions:

```bash
./.venv/bin/python results/experiments/exp21_likelihood_baselines/run_experiment.py --run-id run_02_gemma3_4b --local-files-only
```

Print the scores of every saved run: `python scripts/summarise_runs.py`.

**Reproducibility.** Scoring is deterministic given the model weights: there is no sampling, and the question sets
come from fixed seeds (42 for the 50 development questions, 20261115 for the exploration/confirmation split).
Each answer option is scored with one forward pass (single-pass teacher forcing); on the worst-case option of a
test it matched a float32 reference within 0.003 nats, whereas the earlier one-pass-per-token scoring in bf16 was
off by up to 2.7 nats (`PANDA_SINGLE_PASS_TF=0` restores it). Each run's metadata records the git commit, package
versions, GPU, model precision and the SHA-256 of the TruthfulQA file used. Different GPUs or library versions can
still change the last digits of a score, and occasionally a close ranking between two answer options; rerunning
the 50 development questions in the current environment changed MC1 on at most 2 questions per rule.

## Repository layout

```text
PAnDa/
  src/truthfulqa_scoring/                        Evaluator, decoders, benchmark loaders, older CLI (python -m truthfulqa_scoring)
  results/experiments/              The experiments of the study (exp11-exp13, exp16, exp19-exp21): runner,
                                    run matrix, README, saved runs
  scripts/                          Analysis scripts, paired tests, table and figure data for the report
  paper/                            Report source (tables/ and figures/data/ are generated)
  docs/                             Experiment log, glossary, report checklist, notes on the likelihood and DoLa code
```

Material the study does not use was removed from the tree and is kept under two git tags (see
[`results/experiments/README.md`](results/experiments/README.md)):

- `exploration-2026-06`: the early design alternatives (exp1–exp10) and the first sanity runs;
- `pre-cleanup-2026-11`: the left-out experiments (exp14, exp15, exp17, exp18), the development plots
  (`results/figures/`, `scripts/plots/`), the earlier method notes and presentation, and the June 2026 course report
  (`paper/course_version_2026_06/`).

Key implementation files:

- `results/experiments/local_evaluator.py`: the scoring rules of the experiments (DoLa in both configurations,
  per-question DoLa-static and its selection intervals, the factorial)
- `results/experiments/exp20_self_evaluation/run_experiment.py`: self-evaluation, every block and both wordings
- `src/truthfulqa_scoring/decoders/core.py`: premature-layer selection and DoLa scores
- `src/truthfulqa_scoring/evaluation.py`: MC1 / MC2 / MC3

## Authors

Muhammad Naufal, Jeong Edon, Muhammad Aliff (Korea University). The work started as a course project
(COSE474, spring 2026).
