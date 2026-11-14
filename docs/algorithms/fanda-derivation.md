# Selection interval of the premature layer: what can and cannot be derived

This note concerns the decoders in `results/experiments/` that share the score of per-question DoLa-static (not the `src/panda` CLI preset). They share one
score and differ only in the **selection interval k**, how often the premature layer is re-selected:

- raw-logit contrastive score (mature minus premature layer), no adaptive plausibility constraint;
- premature layer chosen by maximum Jensen–Shannon divergence (JSD) at softmax temperature τ = 0.5;
- re-selected every k tokens (k = 1, 2, 4, 8), or once at the first answer token (k = ∞, per-question DoLa-static).

Terms: [`../glossary.md`](../glossary.md). Code: `results/experiments/local_evaluator.py`
(`EXP12_STATEFUL_FIXED_VIEW_DECODERS`, `compute_stateful_fixed_binary_view_step`), `src/panda/decoders/core.py`
(`select_dynamic_layer`), `src/panda/evaluation.py` (multiple-choice scoring).

**Summary.** Results 1–3 are exact and standard: they bound how far the scores of a schedule with interval k can
move away from per-token selection, and give conditions under which tokens and answer rankings do not change.
They say nothing about which interval is more truthful. Section 4 (an interior optimum) is a hypothesis, not a
derivation, and the saved runs do not support it clearly.

## Setup

At decoding step t:

- V: vocabulary; f_t(v): mature-layer (final-layer) logit of token v; s_t(l, v): early-exit logit of v at
  candidate layer l;
- p_t = softmax(f_t / τ), q_t(l) = softmax(s_t(l) / τ);
- per-step selection: l*_t = argmax over candidate layers l of JSD(p_t, q_t(l));
- contrastive score of layer l: g_t(l, v) = f_t(v) − s_t(l, v); next token: argmax over v of g_t(l, v).

With interval k, the layer in use is l^k_t (the max-JSD layer at the last re-selection step). Its score is
g^k_t(v) = g_t(l^k_t, v); the per-step reference is g*_t(v) = g_t(l*_t, v). Note that **the reference is k = 1
itself**: per-step selection is what the k = 1 decoder does.

Define the deviation e^k_t(v) = g^k_t(v) − g*_t(v) = s_t(l*_t, v) − s_t(l^k_t, v).

## Result 1: the deviation depends only on the premature layers

g^k_t = g*_t + e^k_t, hence ‖g^k_t − g*_t‖_∞ = ‖e^k_t‖_∞. The mature-layer logits cancel; only the difference
between the two premature layers' logits remains.

## Result 2: the next token is unchanged under a small deviation

Let a*_t = argmax_v g*_t(v) be unique, with margin m_t = g*_t(a*_t) − max_{v ≠ a*_t} g*_t(v).

**Lemma.** If 2‖e^k_t‖_∞ < m_t, then argmax_v g^k_t(v) = a*_t.

**Proof.** g^k_t(a*_t) ≥ g*_t(a*_t) − ‖e^k_t‖_∞ and g^k_t(v) ≤ g*_t(v) + ‖e^k_t‖_∞ for every v ≠ a*_t, so
g^k_t(a*_t) − g^k_t(v) ≥ m_t − 2‖e^k_t‖_∞ > 0. ∎

This is the standard margin argument for the stability of an argmax under an ℓ∞ perturbation.

## Result 3: multiple-choice rankings are unchanged under a small total deviation

The evaluator scores an answer option y_{1:T} by teacher forcing:
S_k(y) = Σ_t log_softmax(g^k_t(y_{<t}))[y_t], and S_* is the same with per-step selection.

For any vectors x, z and index i, |log_softmax(x)_i − log_softmax(z)_i| ≤ 2‖x − z‖_∞, because
log_softmax(x)_i = x_i − logsumexp(x) and both terms are 1-Lipschitz in ‖·‖_∞.

**Proposition.** |S_k(y) − S_*(y)| ≤ 2 Σ_t E^k_t(y_{<t}), with E^k_t = ‖e^k_t‖_∞ (sum the per-token bound).

**Corollary.** If S_*(y) − S_*(z) > 2 Σ_t E^k_t(y_{<t}) + 2 Σ_t E^k_t(z_{<t}), then S_k(y) > S_k(z): the
interval-k decoder ranks y above z, as per-step selection does.

These results apply to TruthfulQA MC1/MC2/MC3, which are computed from such option scores. They do not cover
open-ended generation, where a changed token changes the rest of the sequence.

## What Results 1–3 do and do not show

They show when a longer interval gives **the same** decisions as per-step selection. They cannot show that a
longer interval is **better**: the reference they compare against is k = 1, so any deviation from it is, within
this framework, neither good nor bad. Whether k > 1 is more truthful is an empirical question.

One more property of the implementation matters here: each answer option is scored from a fresh state, but the
first answer token is scored from the prompt alone, which is the same for every option. With k = ∞ the premature
layer is therefore the same for all options of a question; it is chosen from the question, not from an option.

## 4. Hypothesis (not derived, not measured): an interior optimum

The course version proposed a trade-off: re-selecting often adds variance to the score (assumed cost A/k), and
keeping a layer long lets it drift from the max-JSD layer (assumed cost B·k), so the total is minimised at
k* = √(A/B). This is an **assumption**, not a consequence of Results 1–3:

- A/k is not defined in terms of any measured quantity. In Results 1–3, per-step selection has zero deviation
  by construction, so the framework contains no cost of re-selecting.
- B·k assumes the deviation grows linearly with the time since re-selection. This was not checked
  (`avg_oracle_jsd_gap` in exp12 could test it per step).

Keep it, if at all, as a labelled hypothesis.

## What the saved runs show (exp12, development set, n = 50)

| k | MC1 | MC2 | MC3 | Layer changes (`switch_rate`) | Same layer as per-step max-JSD (`selected_layer_match_rate`) | `avg_oracle_jsd_gap` |
|---|---|---|---|---|---|---|
| 1 | 0.340 | 0.534 | 0.294 | 0.692 | 1.000 | 0.0000 |
| 4 | 0.400 | 0.576 | 0.351 | 0.135 | 0.461 | 0.0025 |
| ∞ | 0.400 | 0.560 | 0.364 | 0.000 | 0.258 | 0.0034 |

Source: `results/experiments/exp12_state_persistence_diagnostics/runs/run_01_default/run_01_default_summary.csv`.

- k = 4 and k = ∞ tie on MC1; k = 4 is higher on MC2 and k = ∞ on MC3. All three differences are within one
  standard error (about 0.07 for MC1 at n = 50). This is not evidence of an interior optimum.
- On a second random subset (exp16, seed 101), k = 1 and k = ∞ tie on MC1 (0.30) and k = 1 is best on MC2.
- The diagnostics behave as the definitions imply: longer intervals change layer less often and agree less often
  with the per-step max-JSD layer.

## What a report can claim from this

- Exact: with a margin condition, a longer selection interval leaves tokens and option rankings unchanged
  (Results 2–3).
- Empirical, on the development set only: k > 1 scored higher than k = 1 on MC1 and MC3; this did not replicate on
  one other subset. The held-out runs (R1, R2 in `docs/report_checklist.md`) decide whether it holds.
- Not supported: that an intermediate interval is optimal, that a fixed layer is generally more truthful, or
  anything about open-ended generation.
