"""Early-exit reading of the self-evaluation verdict across models (exp20, exploration part): no GPU.

Run from the repository root with the project environment (needs `datasets` for the true/false labels):
    HF_HUB_OFFLINE=1 ./.venv/bin/python scripts/self_evaluation_layers.py

Question: is the self-evaluation verdict (log-odds of the affirmative against the negative reply token) more
accurate when it is read after an intermediate block (early exit) than at the final layer, and on which models?

Protocol. It was fixed after the first three models (Qwen2.5-3B, Gemma 3 4B, Falcon3-3B) and before the others
were scored; PROTOCOL below is the binding text and is written into the output folder.

For every exploration run in the run matrix and each wording, the script prints and writes:
  early_exit_by_block.csv    MC1 of the verdict read after each block (all exploration questions)
  early_exit_selection.csv   the test of the protocol: exit block chosen on a random labelled development set,
                             gain over the final layer on the other questions, over many draws
"""
from __future__ import annotations

import csv
import json
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from heldout_analysis import load_labels, mc_metrics, mean, write_csv  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
EXPERIMENT_DIR = ROOT / "results" / "experiments" / "exp20_self_evaluation"
OUT_DIR = EXPERIMENT_DIR / "cross_model"
WORDINGS = ("is_true", "is_correct")
DEV_SIZE, DRAWS, SEED = 50, 500, 0
MIN_REPLY_MASS = 0.9

PROTOCOL = {
    "models_seen_before_the_protocol": ["Qwen/Qwen2.5-3B-Instruct", "google/gemma-3-4b-it", "tiiuae/Falcon3-3B-Instruct"],
    "models_scored_after_the_protocol": [
        "Qwen/Qwen2.5-1.5B-Instruct", "Qwen/Qwen2.5-0.5B-Instruct", "microsoft/Phi-3.5-mini-instruct",
        "google/gemma-3-1b-it", "HuggingFaceTB/SmolLM2-1.7B-Instruct",
    ],
    "inclusion_rule": "instruction-tuned decoder language models of at most 4 billion parameters that run in bfloat16 "
                      "on one 12 GB GPU, have a chat template and answer directly (no reasoning-first models, because "
                      "the verdict is read at the first reply token). meta-llama/Llama-3.2-3B-Instruct was planned and "
                      "left out because the repository is gated and access was not granted; SmolLM2-1.7B takes its place.",
    "data": "the 417 exploration questions of exp20 (the confirmation questions of these models are not scored)",
    "primary_wording": "is_true",
    "selection": f"draw {DEV_SIZE} questions at random as a labelled development set; among the blocks of the upper half "
                 "of the network (block index > number of blocks / 2, final block included) choose the one with the "
                 "highest MC1 on the development set (ties: the later block)",
    "statistic": f"gain = MC1 at the chosen block minus MC1 at the final layer, on the questions outside the "
                 f"development set; {DRAWS} draws, seed {SEED} per model and wording",
    "a_model_shows_the_gain_if": "the mean gain is positive and the gain is negative in fewer than 5% of the draws",
    "reading_is_valid_if": f"the mean probability mass on the two reply tokens at the final layer is at least {MIN_REPLY_MASS}",
    "verdict_at_chance_if": "the final-layer MC1 is below the chance level plus two standard errors (reported as a flag)",
    "decision": "early-exit self-evaluation is presented as a method only if at least two thirds of all eight models "
                "show the gain with the primary wording (6 of 8); otherwise it is reported as an observation on the "
                "models where it holds",
}


def main() -> None:
    labels = load_labels()
    with (EXPERIMENT_DIR / "run_matrix.csv").open(encoding="utf-8", newline="") as handle:
        runs = [r for r in csv.DictReader(handle) if r["part"] == "exploration" and r["wording_set"] == "verdict"]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "protocol.json").write_text(json.dumps(PROTOCOL, indent=2) + "\n", encoding="utf-8")

    by_block, selection = [], []
    for run in runs:
        run_dir = EXPERIMENT_DIR / "runs" / run["run_id"]
        scores_path = run_dir / f"{run['run_id']}_scores.json"
        if not scores_path.exists():
            print(f"\n{run['run_id']}: not scored yet ({run['model_name']})")
            continue
        payload = json.loads(scores_path.read_text(encoding="utf-8"))
        checks = json.loads((run_dir / f"{run['run_id']}_metadata.json").read_text(encoding="utf-8"))["checks"]
        S, B = payload["scores"], payload["blocks"]
        Q = sorted(S)
        chance = mean(1 / len(labels[q][0]) for q in Q)
        at_chance_below = chance + 2 * math.sqrt(chance * (1 - chance) / len(Q))
        candidates = [b for b in range(B) if b + 1 > B / 2]  # 0-based indices of the upper-half blocks
        print(f"\n==== {run['model_name']} ({run['run_id']}): {B} blocks, {len(Q)} questions, MC1 chance level {chance:.3f}")
        for w in WORDINGS:
            per_block = [[mc_metrics(lambda o: S[q][o][w][b], labels[q])["mc1"] for q in Q] for b in range(B)]
            mc1 = [mean(x) for x in per_block]
            by_block += [{"model": run["model_name"], "run_id": run["run_id"], "wording": w, "block": b + 1,
                          "blocks": B, "mc1": mc1[b]} for b in range(B)]
            rng = random.Random(SEED)
            gains, picks = [], []
            for _ in range(DRAWS):
                idx = list(range(len(Q)))
                rng.shuffle(idx)
                dev, rest = idx[:DEV_SIZE], idx[DEV_SIZE:]
                best = max(candidates, key=lambda b: (sum(per_block[b][i] for i in dev), b))
                picks.append(best + 1)
                gains.append(mean(per_block[best][i] for i in rest) - mean(per_block[-1][i] for i in rest))
            gains.sort()
            picks.sort()
            mass = checks[w]["mean_probability_mass_on_the_two_reply_tokens"]
            negative = mean(g < 0 for g in gains)
            best_upper = max(candidates, key=lambda b: mc1[b])
            row = {
                "model": run["model_name"], "run_id": run["run_id"], "wording": w, "blocks": B,
                "mc1_final_layer": mc1[-1], "best_upper_half_block_all_questions": best_upper + 1,
                "mc1_at_that_block": mc1[best_upper],
                "chosen_block_median": picks[len(picks) // 2], "chosen_block_p5": picks[int(0.05 * DRAWS)],
                "chosen_block_p95": picks[int(0.95 * DRAWS) - 1],
                "mean_gain": mean(gains), "gain_p5": gains[int(0.05 * DRAWS)], "gain_p95": gains[int(0.95 * DRAWS) - 1],
                "share_of_draws_with_negative_gain": negative,
                "shows_the_gain": mean(gains) > 0 and negative < 0.05,
                "reply_token_mass": mass, "reading_valid": mass >= MIN_REPLY_MASS,
                "verdict_at_chance": mc1[-1] < at_chance_below,
            }
            selection.append(row)
            start = max(0, B - 12)
            print(f"  {w}: MC1 by block " + " ".join(f"{b + 1}:{mc1[b]:.2f}" for b in range(start, B)))
            print(f"    final layer {mc1[-1]:.3f}{' (at chance)' if row['verdict_at_chance'] else ''}; best upper-half block "
                  f"{best_upper + 1}: {mc1[best_upper]:.3f}; reply-token mass {mass:.3f}"
                  f"{'' if row['reading_valid'] else ' (READING NOT VALID)'}")
            print(f"    block chosen on {DEV_SIZE} questions: median {row['chosen_block_median']} "
                  f"(5%-95%: {row['chosen_block_p5']}-{row['chosen_block_p95']}); gain on the other questions mean "
                  f"{row['mean_gain']:+.3f} (5%-95%: {row['gain_p5']:+.3f} to {row['gain_p95']:+.3f}), negative in "
                  f"{negative:.2f} of draws -> {'GAIN' if row['shows_the_gain'] else 'no gain'}")
    print()
    write_csv(OUT_DIR, "early_exit_by_block.csv", by_block)
    write_csv(OUT_DIR, "early_exit_selection.csv", selection)
    for w in WORDINGS:
        rows = [r for r in selection if r["wording"] == w]
        print(f"wording {w}: {sum(r['shows_the_gain'] for r in rows)} of {len(rows)} scored models show the gain: "
              + ", ".join(f"{r['model'].split('/')[-1]} {r['mean_gain']:+.3f}" for r in rows))


if __name__ == "__main__":
    main()
