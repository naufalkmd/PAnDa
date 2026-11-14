# PAnDa (dropped)

> **Status:** dropped on 2026-11-14; not part of the results or the report. This note documents the code
> (`src/panda/decoders/panda.py`) because saved exploration runs (exp5, exp11's `panda_switch`, `results/dev/`)
> used it. The project's method is per-question DoLa-static: see [`../glossary.md`](../glossary.md).

## What It Does

`panda` (PAnDa) applies contrastive decoding inside Jacobi-style blocks. It produces one sequence (it does not
generate two answers and rerank them):

1. compute the greedy score (final-layer logits) and the contrastive score for every position of the block
2. find the first position where the two disagree (different top token and JSD above a threshold)
3. from that position on, choose between the two scores token by token
4. refine the block by Jacobi iteration
5. commit the converged prefix and continue

Relevant code:

- `src/panda/evaluator.py:421-575`
- `src/panda/evaluator.py:684-729`
- `src/panda/evaluator.py:793-826`

## Generation Pseudocode

```text
# Start from the prompt tokens.
generated = prepare_prompt(prompt)

repeat until max_new_tokens or EOS:
    # The block can shrink near the end if little token budget remains.
    block_window_size = min(jacobi_window_size, remaining_budget)

    # Build and refine one speculative block under PAnDa.
    block_result = run_panda_block(generated, block_window_size)

    # Commit only the stable prefix of that refined block.
    commit_len = stable-prefix commit from block_result

    # Append the committed tokens and continue from the updated prefix.
    append committed tokens to generated

return decoded continuation
```

## `run_panda_block()` Pseudocode

```text
# Initialize the speculative block by repeating the last generated token.
buffer = repeat last generated token across the whole block
previous_buffer = buffer

for iteration in 0 .. jacobi_max_iters - 1:
    # Run one shared forward pass for the whole current block hypothesis.
    input_ids = generated + buffer
    layer_logits, final_logits = forward_with_window_layer_logits(input_ids, window_size)

    # Choose one premature layer per block position using maximum JSD.
    selected_layers = choose one premature layer per position by max JSD

    for each position in the block:
        # Premature-layer logits for this position.
        shallow_logits = layer_logits[selected_layer][position]

        # The two scores for this position.
        greedy_scores = final_logits[position]
        contrast_scores = final_logits[position] - shallow_logits

        # Each score proposes its own top token.
        greedy_token = argmax(greedy_scores)
        contrast_token = argmax(contrast_scores)

        # Only mark a real disagreement if the top tokens differ
        # and the two distributions are far enough apart (JSD).
        if greedy_token != contrast_token and JSD(greedy_scores, contrast_scores) >= panda_divergence_threshold:
            mark this position as a disagreement

    # The choice between scores starts at the earliest disagreement.
    first_divergence = earliest marked disagreement position

    for each position in the block:
        # Positions before the first disagreement keep the greedy score.
        arbitration_active = position >= first_divergence

        # From there on, use the contrastive score if its top-token probability is within
        # panda_truth_bias of the greedy score's top-token probability.
        if arbitration_active and top1_confidence(contrast_scores) > top1_confidence(greedy_scores) - panda_truth_bias:
            choose contrast_scores / contrast_token
        else:
            choose greedy_scores / greedy_token

    # These chosen tokens become the next block proposal.
    new_buffer = chosen block tokens

    if new_buffer == buffer:
        # Stop early if the block stopped changing.
        converged = True
        break

    # Otherwise keep iterating Jacobi-style on the updated block.
    previous_buffer = buffer
    buffer = new_buffer

# After refinement, commit only the stable prefix, not necessarily the whole block.
stable_prefix_len = full window if converged else common_prefix_length(previous_buffer, buffer)
commit_len = stable_prefix_len if stable_prefix_len > 0 else 1

# Return the refined block, first-position scores, and diagnostics.
return chosen block, first-position scores, diagnostics, and commit length
```

## Candidate-Scoring Pseudocode

When the repo scores a fixed candidate answer with `panda`, it does not score the full block at once. It repeatedly uses the block's first-position scores:

```text
# Start from the prompt.
generated = prepare_prompt(prompt)
total_logprob = 0

for token in tokenize(choice_text):
    # Rebuild a PAnDa block for the current prefix.
    block_result = run_panda_block(generated, min(jacobi_window_size, remaining_tokens))

    # Only the first-position scores of the block are used to score
    # the next candidate token under teacher forcing.
    total_logprob += log_softmax(block_result.first_scores)[token]

    # Teacher-force that candidate token into the prefix.
    append token to generated

return total_logprob
```

## Hyperparameters Used Here

### Current Code Defaults

| Setting | Value in this repo |
| --- | --- |
| `jacobi_window_size` | `4` |
| `jacobi_max_iters` | `2` |
| `panda_divergence_threshold` | `0.05` |
| `panda_truth_bias` | `0.02` |
| `panda_early_agreement_shortcut` | `False` |

### The Two Scores Inside PAnDa

PAnDa uses two fixed scores (contrastive weight 0 and 1), not a tuned weight:

| Setting | Value |
| --- | --- |
| Greedy score | `final_logits` |
| Contrastive score | `final_logits - shallow_logits` |

### Shared Layer-Selection Settings

| Setting | Value |
| --- | --- |
| Candidate premature layers | default `range(0, max(1, num_layers // 4), 2)` |
| Per-position layer rule | max JSD between final logits and candidate premature layer logits |
| Buffer init | repeat last token across the block |
| Commit fallback | commit at least 1 token |

## Short Summary

PAnDa, in standard terms:

```text
Jacobi decoding over blocks of 4 tokens
+ greedy and contrastive scores at every block position
+ from the first disagreement on, a per-token choice between the two scores (top-token probability margin)
+ commit the converged prefix
```
