# Experiment 10: Switch gated by an exponential moving average

Does a rule-based switch improve when it is gated by an exponential moving average (EMA) of an uncertainty
signal, instead of reacting to each token alone? Single pass, no Jacobi blocks, fixed contrastive weight.

Compared decoders (the premature layer is fixed by the run row):

- `fanda`: the contrastive score `final_logits - shallow_logits` at every token.
- `ema_risk_switch`: the same contrastive score, used only when the greedy and contrastive top tokens differ
  **and** the EMA of the uncertainty signal is above a threshold. It can stay on the contrastive score for a few
  more tokens (`sticky` hold).

Rule:

```text
signal_t = weighted_mean(normalized_final_entropy,
                         1 - (top-1 probability - top-2 probability),
                         normalized_jsd(final_probs, shallow_probs))
ema_t    = beta * ema_{t-1} + (1 - beta) * signal_t
use_contrastive_t = (top tokens differ) and ema_t >= risk_threshold
```

Run rows:

- `run_01_layer4_default`: premature layer 4, `beta = 0.8`, equal weights, `risk_threshold = 0.55`.
- `run_02_layer8_default`: the same with premature layer 8.

How to read it: if `ema_risk_switch` beats `fanda`, smoothing the signal over tokens helps beyond a per-token
switch; if it ties or loses, the contrastive score at every token is preferable here.

Terms: [`docs/glossary.md`](../../../docs/glossary.md).

Run example:

```bash
python3 results/experiments/exp10_ema_risk_switch/run_experiment.py \
  --model-name Qwen/Qwen2.5-3B-Instruct \
  --mode subset \
  --truthfulqa-limit 50
```
