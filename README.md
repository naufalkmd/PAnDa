# Per-question DoLa-static: contrastive layer decoding with a premature layer chosen per question

Research code for **per-question DoLa-static**, a variant of DoLa (decoding by contrasting layers, Chuang et al.,
2024), evaluated on TruthfulQA multiple choice. DoLa-static is DoLa's own name for its variant with one fixed
premature layer chosen on a validation set; here the fixed layer is chosen separately for each question.
The method was called FAnDa in the June 2026 course version; code identifiers still use `fanda`.

It differs from DoLa in four settings:

- no adaptive plausibility constraint (DoLa's "relative-top" filter);
- the raw-logit difference `z_mature − z_premature` instead of the log-probability difference;
- the premature layer is chosen by Jensen–Shannon divergence at temperature 0.5 (DoLa uses 1);
- the premature layer is chosen **once per question** (at the first answer token, where every answer option has
  the same input) and then kept fixed, instead of being re-selected at every token.

**History.** The repository and the Python package (`panda`) are named after PAnDa, an earlier block-wise
variant that was dropped. Its code stays because saved exploration runs used it (see
[`docs/algorithms/panda.md`](docs/algorithms/panda.md)); it is not part of the results.

**Status.** This is a development-stage research repository, not a benchmark package. Most results come
from one 50-question TruthfulQA subset, which was also used to develop the method. See
[`docs/experiment_log.md`](docs/experiment_log.md) for every experiment, its result and its known issues.
Code names are explained in [`docs/glossary.md`](docs/glossary.md).

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

**Reproducibility.** Scoring is deterministic given the model weights: there is no sampling, and the question
subsets come from fixed seeds (42 for the development set). Each answer option is scored with one forward pass
(single-pass teacher forcing); on the worst-case option of a test it matched a float32 reference within 0.003
nats, whereas the earlier one-pass-per-token scoring in bf16 was off by up to 2.7 nats (`PANDA_SINGLE_PASS_TF=0`
restores it). Each run's metadata records the git commit, package
versions, GPU, model precision, candidate layers and the SHA-256 of the TruthfulQA file used (`environment` in
`*_metadata.json`). Different GPUs or library versions can still change the last digits of a score, and
occasionally a close ranking between two answer options.

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

## Older evaluator CLI

The experiments above use the runners in `results/experiments/`. The package also has an older general evaluator
(`python -m panda`, TruthfulQA multiple choice) with the decoders `greedy`, `dola`, `fixed_alpha_dola_low`,
`fixed_alpha_dola`, `fixed_alpha_dola_high` and `panda`. It is not used for the results; `--mode sanity` /
`subset` / `full` choose the question subset, `--model-name` the model, `--local-files-only` disables downloads.

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
  results/dev/          Early sanity runs of the dropped PAnDa method (historical "stage" names)
  scripts/              Run wrappers and scripts/summarise_runs.py
  scripts/plots/        Figure scripts
  paper/                Report source; paper/course_version_2026_06/ is the June 2026 course version
  docs/                 Algorithm notes, glossary, experiment log, presentation
```

Key implementation files:

- `src/panda/decoders/core.py`: premature-layer selection, DoLa scores, contrastive scores
- `results/experiments/local_evaluator.py`: the experiment decoders (per-question DoLa-static and its selection-interval variants, the factorial, rule-based switches)
- `src/panda/evaluation.py`: MC1/MC2/MC3 scoring and summaries

## Reproducibility notes

- Fixed seeds: the default subset is seed 42; exp16 adds fresh subsets with seeds 101–404.
- Exact reproduction depends on model availability, the Hugging Face dataset version and the GPU. Official DoLa
  scores 0.26–0.28 MC1 on the same 50 questions across runs.
- The saved runs are compact artifacts (summaries, raw predictions, metadata), not every exploratory run.

## Authors

Muhammad Naufal, Jeong Edon, Muhammad Aliff (Korea University). The work started as a course project
(COSE474, spring 2026).
