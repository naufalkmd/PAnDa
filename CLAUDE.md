# Per-question DoLa-static (formerly FAnDa)

Research repository for per-question DoLa-static (code name `fanda`, formerly FAnDa): DoLa with the premature
layer chosen once per question and kept fixed. PAnDa, the earlier block-wise
method the repository and the `panda` package are named after, was dropped (2026-11-14): keep its code (saved
exploration runs use it), but leave it out of the report and the README's description.
**The GitHub repository is public**: never commit `archive/`, course material, model weights, datasets,
tokens or `.env`.

## Report

- Source: `paper/fanda_report.tex` (`references.bib`, `figures/`). Build from `paper/` with
  `latexmk -pdf -outdir=build fanda_report.tex`.
- Purpose: a portfolio piece in arXiv style (one column, no page limit). Authors: Muhammad Naufal, Jeong Edon,
  Muhammad Aliff (Korea University).
- The June 2026 course version is `paper/course_version_2026_06/`. Keep it unchanged as a record; do not reuse its
  tables (they mix runs).
- Status, outline, table sources, reruns and citations to verify: `docs/report_checklist.md`. Read it first.

## Results and terms

- Results are read only from `results/experiments/<exp>/runs/<run>/*_summary.csv`, `*_raw_predictions.csv`
  (one row per question, `example_idx`) and `*_metadata.json`. `python scripts/summarise_runs.py` prints them all.
- `docs/experiment_log.md`: every experiment, its result and the known issues. Update it after each new run.
- **Terms:** prose (report, README, docs, commit messages) uses standard machine-learning terms only, never project
  vocabulary (anchor, jitter, persistence, view, regime, arbitration, ...). The method's name builds on DoLa's own term
  DoLa-static; do not reintroduce "FAnDa" in prose except as the former name.
- `docs/glossary.md`: code names and older-note words → standard terms. Do not rename identifiers: saved runs and figure JSON depend
  on them. Watch out: `fanda` means re-selection every 4 tokens in exp7–exp10 and a fixed layer in exp11/exp18.
- The 50-question subset (seed 42) is the **development** set: every design choice was made on it.
- exp14 "manual" scores were written by Codex (an LLM). Say so wherever they are used, unless a person reviews them.

## Environment

- **GPU runs happen on this PC, in WSL Ubuntu** (RTX 5070, 12 GB), in `.venv` (a Linux venv on the Windows
  drive, created by `bash scripts/setup_env.sh` from `requirements-lock.txt`; no system site-packages). Run in
  `tmux`. Model and dataset caches are in WSL's `~/.cache/huggingface` (Qwen2.5-3B, Gemma 3 4B, Falcon 3 3B, the
  HINT model, and the TruthfulQA arrow file are cached there).
- The June 2026 runs used a `.venv` whose torch came from the system Python (version lost; package list in
  `docs/environment_2026-06.txt`); that venv is in `archive/venv-2026-06-no-torch`. Pins in `requirements.txt` match
  its versions, plus torch 2.9.1 + cu128.
- On the Windows side, run the plotting and summary scripts with
  `uv run --no-project --with matplotlib --with pandas --with numpy python <script>`.
- Run every script from the repository root (plot scripts use paths relative to it).
- Keep `huggingface_hub` < 1.0: newer versions reject the dataset id `truthful_qa` (they need `namespace/name`).
- New runs record their environment in the metadata (`collect_environment` in `results/experiments/common.py`).
- Exploration experiments (exp1–exp10) are to move to `results/experiments/exploration/` **after** the R1/R2
  reruns finish (the runners and plot scripts locate files by path).
