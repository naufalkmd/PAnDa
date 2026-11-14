# Experiment 15: Answer prefixes (case study)

A small case study after exp14. On a few selected questions, at what point in the answer do the generations with
k = ∞ (`exp14_frozen`) and k = 1 (`exp14_update1`) start to differ in correctness?

For each selected question it:

1. generates one answer (up to 120 new tokens) with each of the two decoders;
2. cuts **the same** answer into prefixes of 10, 30, 60 and 100 words and the full answer, so prefixes are
   compared within one generation rather than across separate short and long generations;
3. saves a prefix-level labelling sheet and a per-token trace with cumulative word counts.

Question selection, from the exp14 label sheet: 3 questions where k = ∞ scored higher, 3 where k = 1 scored
higher, 2 where both scored low. Those exp14 labels were assigned by an LLM (Codex).

## Outputs

- `selected_questions.csv`: the chosen questions and why;
- `full_generations.csv`: one answer per question × decoder;
- `token_trace.csv`: per-token rows with cumulative word counts;
- `prefix_manual_eval.csv`: one row per question × decoder × prefix, with empty label columns. **Not labelled yet.**
- `assistant_full_verdict.csv`: one judgement per question (8 rows), written by an LLM assistant, not a person;
- `metadata.json`.

## How to read it (once labelled)

- k = ∞ better at 10–30 words but worse by 60–100: the fixed layer helps early and hurts later in long answers.
- k = ∞ better at every prefix: a layer chosen at the start suits the whole answer.
- k = 1 better from 10 words on: fixing the layer does not help in free generation.
- no consistent pattern: the difference depends on the question more than on answer length.

Terms: [`docs/glossary.md`](../../../docs/glossary.md).

## Run

```bash
./.venv/bin/python results/experiments/exp15_prefix_probe/run_experiment.py \
  --model-name Qwen/Qwen2.5-3B-Instruct \
  --local-files-only \
  --mode subset \
  --truthfulqa-limit 50 \
  --max-new-tokens 120 \
  --run-id run_01_default
```

Plot (top panel from the automatic scores; the bottom panel needs the prefix labels):

```bash
./.venv/bin/python scripts/plots/plot_exp15_prefix_probe.py
```

It writes `results/figures/exp15_prefix_probe_summary.svg` and `.json`.
