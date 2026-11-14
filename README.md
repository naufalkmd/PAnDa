# PAnDa / FAnDa: contrastive layer decoding experiments

Research code for **FAnDa**, a simplification of DoLa (contrastive layer decoding, Chuang et al., 2024) for
truthful question answering, and for **PAnDa**, the earlier block-wise method it grew out of. The repository is
named after PAnDa; the current results and the report are about FAnDa.

**FAnDa** differs from DoLa in four settings:

- no adaptive plausibility constraint (DoLa's "relative-top" filter);
- the raw-logit difference `z_mature − z_premature` instead of the log-probability difference;
- the premature layer is chosen by Jensen–Shannon divergence at temperature 0.5 (DoLa uses 1);
- the premature layer is chosen **once per answer** and then kept fixed, instead of being re-selected at every token.

**PAnDa** (Parallel-block Adaptive Contrast DoLa) applies contrastive decoding inside Jacobi-style blocks of
4 tokens. It takes tokens from the final layer up to the first position where the final-layer and contrastive
distributions disagree, then chooses between the two scores token by token. It is kept as a baseline.

**Status.** This is a development-stage research repository, not a benchmark package. Most results come
from one 50-question TruthfulQA subset, which was also used to develop the method. See
[`docs/experiment_log.md`](docs/experiment_log.md) for every experiment, its result and its known issues.
Code names are explained in [`docs/glossary.md`](docs/glossary.md).

## Install

Run from the repository root:

```bash
python -m venv .venv
./.venv/bin/python -m pip install -U pip
./.venv/bin/python -m pip install -e .
```

For gated models, or models not cached locally, export `HF_TOKEN` (or `HUGGINGFACE_HUB_TOKEN`).

## Run an experiment

Each experiment in `results/experiments/expN_*/` has a `run_experiment.py`, a `run_matrix.csv` (one row per
run), a README, and its saved outputs in `runs/`. For example, the layer re-selection sweep:

```bash
./.venv/bin/python results/experiments/exp16_mc_persistence_seed_sweep/run_experiment.py \
  --model-name Qwen/Qwen2.5-3B-Instruct \
  --mode subset \
  --truthfulqa-limit 50
```

Print the scores of every saved run:

```bash
python scripts/summarise_runs.py
```

## Evaluator CLI

The package also has a general evaluator (TruthfulQA multiple choice, MC1/MC2/MC3) with the decoders
`greedy`, `dola`, `fixed_alpha_dola_low`, `fixed_alpha_dola`, `fixed_alpha_dola_high` and `panda`:

```bash
./.venv/bin/python -m panda \
  --comparison-preset panda \
  --mode sanity \
  --save-results \
  --results-dir results/dev/panda_truthfulqa_sanity10
```

- `--mode sanity` / `subset` / `full`: small seeded subset, larger seeded subset, or all questions.
- `--model-name`: any Hugging Face causal LM.
- `--truthfulqa-limit N`: override the subset size.
- `--local-files-only`: no network access.

`scripts/run_panda_truthfulqa.py` wraps the PAnDa preset (`--bootstrap` installs missing dependencies).

## Figures

Plot scripts live in `scripts/plots/` and write to `results/figures/`. Run them from the repository root, for example:

```bash
python scripts/plots/plot_exp13_logit_filter_factorial.py
```

## Repository layout

```text
PAnDa/
  src/panda/            Evaluator, decoders, benchmark loaders, CLI
  results/experiments/  One folder per experiment: runner, run matrix, README, saved runs
  results/figures/      Generated figures and their data (JSON)
  results/dev/          Early PAnDa sanity runs (historical "stage" names)
  scripts/              Run wrappers and scripts/summarise_runs.py
  scripts/plots/        Figure scripts
  paper/                Report source; paper/course_version_2026_06/ is the June 2026 course version
  docs/                 Algorithm notes, glossary, experiment log, presentation
```

Key implementation files:

- `src/panda/decoders/core.py`: premature-layer selection, DoLa scores, contrastive scores
- `results/experiments/local_evaluator.py`: the experiment decoders (FAnDa variants, the factorial, rule-based switches)
- `src/panda/evaluation.py`: MC1/MC2/MC3 scoring and summaries

## Reproducibility notes

- Fixed seeds: the default subset is seed 42; exp16 adds fresh subsets with seeds 101–404.
- Exact reproduction depends on model availability, the Hugging Face dataset version and the GPU. Official DoLa
  scores 0.26–0.28 MC1 on the same 50 questions across runs.
- The saved runs are compact artifacts (summaries, raw predictions, metadata), not every exploratory run.

## Authors

Muhammad Naufal, Jeong Edon, Muhammad Aliff (Korea University). The work started as a course project
(COSE474, spring 2026).
