# PAnDa / FAnDa

Research repository for FAnDa (a DoLa variant with a fixed premature layer) and PAnDa (the earlier block-wise
method). **The GitHub repository is public**: never commit `archive/`, course material, model weights, datasets,
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
- `docs/glossary.md`: code names → standard terms. Do not rename identifiers: saved runs and figure JSON depend
  on them. Watch out: `fanda` means re-selection every 4 tokens in exp7–exp10 and a fixed layer in exp11/exp18.
- The 50-question subset (seed 42) is the **development** set: every design choice was made on it.
- exp14 "manual" scores were written by Codex (an LLM). Say so wherever they are used, unless a person reviews them.

## Environment

- `.venv/` is a Linux environment (the GPU machine). On the Windows PC, run the plotting and summary scripts with
  `uv run --no-project --with matplotlib --with pandas --with numpy python <script>`.
- Run every script from the repository root (plot scripts use paths relative to it).
- `pyproject.toml` dependencies are not pinned yet; pin them from the GPU machine's environment
  (`pip freeze`) before the final reproduction runs.
