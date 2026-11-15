# Decoder Algorithms in This Repo

This folder explains the current decoder implementations in `src/truthfulqa_scoring/` as they exist in the public repo.

Files:

- [greedy.md](greedy.md): the base model's likelihood
- [dola.md](dola.md): DoLa

The notes on fixed-weight DoLa, on the selection interval of per-question DoLa-static and on the dropped PAnDa
method were removed from the tree on 2026-11-15; they are in this folder at the git tag `pre-cleanup-2026-11`. The
scoring rules of the study are defined in the report (`paper/report.tex`, Section 3). Terms:
[`../glossary.md`](../glossary.md).

## Shared Runtime

All decoders in this repo use the same local Hugging Face causal LM loaded by `Stage4Evaluator`:

- tokenizer load: `src/truthfulqa_scoring/evaluator.py`
- model load: `src/truthfulqa_scoring/evaluator.py`

The public evaluator exposes these decoder names:

- `greedy`
- `dola`
- `fixed_alpha_dola_low`
- `fixed_alpha_dola`
- `fixed_alpha_dola_high`
- `panda`

See `src/truthfulqa_scoring/utils.py`.

## Repo-Wide Decoder Defaults

These are the current code defaults, not necessarily the settings used by every historical artifact under `results/experiments/exploration/sanity_runs/stage*/` (git tag `exploration-2026-06`).

| Setting | Current repo default | Where it comes from |
| --- | --- | --- |
| CLI model default | `Qwen/Qwen2.5-3B-Instruct` | `src/truthfulqa_scoring/args.py` |
| Public preset model override | `HINT-lab/DeepSeek-R1-Distill-Qwen-1.5B-Self-Calibration` | `src/truthfulqa_scoring/args.py` |
| Comparison presets | `panda` | `src/truthfulqa_scoring/args.py` |
| Default decoder set | `greedy`, `dola`, `fixed_alpha_dola_low`, `fixed_alpha_dola`, `fixed_alpha_dola_high`, `panda` | `src/truthfulqa_scoring/utils.py` |
| Default candidate premature layers (`shallow_bucket`) | `range(0, max(1, num_layers // 4), 2)` | `src/truthfulqa_scoring/evaluator.py` |
| `tau` | `0.5` | `src/truthfulqa_scoring/config.py` |
| `alpha_min` | `0.0` | `src/truthfulqa_scoring/config.py` |
| `alpha_max` | `1.0` | `src/truthfulqa_scoring/config.py` |
| `update_every` | `4` | `src/truthfulqa_scoring/config.py` |
| `dola_relative_top` | `0.1` | `src/truthfulqa_scoring/args.py` |
| `dola_relative_top_value` | `-1000.0` | `src/truthfulqa_scoring/args.py` |
| Fixed-alpha DoLa presets | `0.0`, `0.5`, `1.0` | `src/truthfulqa_scoring/config.py` |
| PAnDa's two contrastive weights (greedy, full contrast) | `0.0`, `1.0` | `src/truthfulqa_scoring/config.py` |
| `jacobi_window_size` | `4` | `src/truthfulqa_scoring/args.py` |
| `jacobi_max_iters` | `2` | `src/truthfulqa_scoring/args.py` |
| `panda_divergence_threshold` | `0.05` | `src/truthfulqa_scoring/args.py` |
| `panda_truth_bias` | `0.02` | `src/truthfulqa_scoring/args.py` |
| `panda_early_agreement_shortcut` | `False` | `src/truthfulqa_scoring/args.py` |

## Public Preset Overrides

When you run `--comparison-preset panda`, the repo changes a few defaults if you did not override them manually:

- `model_name`: `Qwen/Qwen2.5-3B-Instruct -> HINT-lab/DeepSeek-R1-Distill-Qwen-1.5B-Self-Calibration`
- `strict_eval = True`

See `src/truthfulqa_scoring/args.py`.

## Notes

- `dola` in this repo uses no per-token contrastive weight `alpha_t`.
- `panda` chooses between the greedy and contrastive scores inside each Jacobi block, producing one sequence;
  it does not generate two complete answers and rerank them.
