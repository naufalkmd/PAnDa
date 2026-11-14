# Experiment 17: Token-level premature-layer traces of open-ended answers

Regenerates a few exp14 open-ended answers with the premature layer re-selected at every token
(`exp14_update1`) and records which premature layer was selected at each token, for plotting.

Case selection:

- source: `results/experiments/exp14_openended_factuality/runs/run_01_default/run_01_default_manual_eval.csv`;
- decoder: `exp14_update1`;
- high-scoring cases: `manual_score_0_2 = 2`; low-scoring cases: `manual_score_0_2 = 0`;
- order within each group: `proxy_oref_margin` (automatic reference-overlap margin).

**Note:** the 0/1/2 labels used for selection were assigned by an LLM (Codex), not by a person
(`reviewer = codex` in the source sheet).

exp14 saved the answers and summary metrics but no per-token traces, so exp17 reruns only the selected prompts.

Outputs:

- `run_01_default_selected_cases.csv`: one row per selected question, with the source label, the saved answer,
  the regenerated answer and trace summaries;
- `run_01_default_token_trace.csv`: one row per generated token, with `selected_layer`, `token_step` and the token;
- `run_01_default_metadata.json`: metadata and the source of the labels.

Terms: [`docs/glossary.md`](../../../docs/glossary.md).
