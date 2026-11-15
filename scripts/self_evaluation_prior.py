"""Self-evaluation with the question removed (exp20, exploration part, all models): no GPU.

Run from the repository root with the project environment (needs `datasets` for the true/false labels):
    HF_HUB_OFFLINE=1 ./.venv/bin/python scripts/self_evaluation_prior.py

Two questions, one experiment:
  control   How well does the verdict rank the options when the model does not see the question? That score is
            what the option alone gives away: its wording, and any fact it states that can be judged alone.
  method    Does subtracting that question-free verdict from the verdict (as pointwise mutual information does for
            likelihoods) improve the choice of the true option?

PROTOCOL below was fixed before any question-free verdict was scored and is written into the output folder.
Writes cross_model/prior_correction.csv.
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
from paired_tests import exact_mcnemar, paired_bootstrap  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
EXPERIMENT_DIR = ROOT / "results" / "experiments" / "exp20_self_evaluation"
OUT_DIR = EXPERIMENT_DIR / "cross_model"
WORDINGS = ("is_true", "is_correct")
RESAMPLES, SEED = 10_000, 0

PROTOCOL = {
    "data": "the 417 exploration questions of exp20, eight models (the runs with wording_set no_question)",
    "scores": {
        "verdict": "final-layer log-odds of the affirmative against the negative reply token, question shown",
        "question_free": "the same log-odds for the same wording with the question removed from the user message",
        "corrected": "verdict minus question_free, weight 1, nothing tuned (the tested method)",
        "sum": "verdict plus question_free (reported, not part of the decision)",
    },
    "primary_wording": "is_true",
    "test": f"MC1 of corrected minus MC1 of verdict on the same questions: 95% paired-bootstrap interval "
            f"({RESAMPLES} resamples, seed {SEED} per model and wording) and exact McNemar",
    "a_model_shows_the_gain_if": "the difference is positive and the interval excludes 0",
    "a_model_shows_a_loss_if": "the difference is negative and the interval excludes 0",
    "models_counted": "those whose verdict is above chance at the final layer (MC1 at least the chance level plus two "
                      "standard errors); the others are reported and not counted",
    "decision": "prior-corrected self-evaluation is a method candidate only if at least 5 of the counted models show "
                "the gain with the primary wording and none shows a loss. A candidate still needs the confirmation "
                "questions and a second dataset. Otherwise the result is reported as the control only.",
}


def load(run_id: str) -> dict:
    return json.loads((EXPERIMENT_DIR / "runs" / run_id / f"{run_id}_scores.json").read_text(encoding="utf-8"))


def pairwise_matched(fn, questions, labels, S) -> float:
    """Mean over questions of P(score(true) > score(false)) over option pairs whose token counts differ by <= 1."""
    out = []
    for q in questions:
        vals = []
        for t, lt in zip(labels[q][2], labels[q][3]):
            if lt != 1:
                continue
            for f, lf in zip(labels[q][2], labels[q][3]):
                if lf != 0 or abs(S[q][t]["n_tokens"] - S[q][f]["n_tokens"]) > 1:
                    continue
                a, b = fn(q, t), fn(q, f)
                vals.append(1.0 if a > b else 0.5 if a == b else 0.0)
        if vals:
            out.append(mean(vals))
    return mean(out)


def main() -> None:
    labels = load_labels()
    with (EXPERIMENT_DIR / "run_matrix.csv").open(encoding="utf-8", newline="") as handle:
        runs = [r for r in csv.DictReader(handle) if r["part"] == "exploration"]
    with_question = {r["model_name"]: r["run_id"] for r in runs if r["wording_set"] == "verdict"}
    no_question = {r["model_name"]: r["run_id"] for r in runs if r["wording_set"] == "no_question"}
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "prior_protocol.json").write_text(json.dumps(PROTOCOL, indent=2) + "\n", encoding="utf-8")

    rows = []
    for model, run_id in with_question.items():
        other = EXPERIMENT_DIR / "runs" / no_question[model] / f"{no_question[model]}_scores.json"
        if not other.exists():
            print(f"\n{model}: question-free verdict not scored yet")
            continue
        S, P = load(run_id)["scores"], load(no_question[model])["scores"]
        Q = sorted(S)
        assert Q == sorted(P)
        chance = mean(1 / len(labels[q][0]) for q in Q)
        floor = chance + 2 * math.sqrt(chance * (1 - chance) / len(Q))
        print(f"\n==== {model}: {len(Q)} questions, MC1 chance level {chance:.3f}")
        for w in WORDINGS:
            rules = {
                "verdict": lambda q, o: S[q][o][w][-1],
                "question_free": lambda q, o: P[q][o][w][-1],
                "corrected": lambda q, o: S[q][o][w][-1] - P[q][o][w][-1],
                "sum": lambda q, o: S[q][o][w][-1] + P[q][o][w][-1],
            }
            res = {name: [mc_metrics(lambda o: fn(q, o), labels[q]) for q in Q] for name, fn in rules.items()}
            mc = {name: {m: mean(x[m] for x in r) for m in ("mc1", "mc2", "mc3")} for name, r in res.items()}
            row = {"model": model, "wording": w, "n": len(Q), "counted": mc["verdict"]["mc1"] >= floor}
            for name in rules:
                row.update({f"{name}_{m}": mc[name][m] for m in ("mc1", "mc2", "mc3")})
            row["question_free_pairwise_length_matched"] = pairwise_matched(rules["question_free"], Q, labels, S)
            row["verdict_pairwise_length_matched"] = pairwise_matched(rules["verdict"], Q, labels, S)
            for name in ("corrected", "sum"):
                a = [x["mc1"] for x in res[name]]
                b = [x["mc1"] for x in res["verdict"]]
                d = [x - y for x, y in zip(a, b)]
                lo, hi, _ = paired_bootstrap(d, RESAMPLES, random.Random(SEED))
                won = sum(1 for x, y in zip(a, b) if x == 1 and y == 0)
                lost = sum(1 for x, y in zip(a, b) if x == 0 and y == 1)
                row.update({f"{name}_minus_verdict": mean(d), f"{name}_ci_low": lo, f"{name}_ci_high": hi,
                            f"{name}_gained": won, f"{name}_lost": lost, f"{name}_p_mcnemar": exact_mcnemar(won, lost),
                            f"{name}_shows_the_gain": mean(d) > 0 and lo > 0, f"{name}_shows_a_loss": mean(d) < 0 and hi < 0})
            rows.append(row)
            print(f"  {w:10s} MC1: verdict {mc['verdict']['mc1']:.3f}{'' if row['counted'] else ' (at chance, not counted)'} | "
                  f"question-free {mc['question_free']['mc1']:.3f} (length-matched pairs {row['question_free_pairwise_length_matched']:.3f}, "
                  f"verdict {row['verdict_pairwise_length_matched']:.3f})")
            for name in ("corrected", "sum"):
                tag = "GAIN" if row[f"{name}_shows_the_gain"] else "LOSS" if row[f"{name}_shows_a_loss"] else "no difference"
                print(f"    {name:9s} {mc[name]['mc1']:.3f}  minus verdict {row[f'{name}_minus_verdict']:+.3f} "
                      f"[{row[f'{name}_ci_low']:+.3f}, {row[f'{name}_ci_high']:+.3f}], gained/lost "
                      f"{row[f'{name}_gained']}/{row[f'{name}_lost']}, McNemar p {row[f'{name}_p_mcnemar']:.4f} -> {tag}")
    print()
    write_csv(OUT_DIR, "prior_correction.csv", rows)
    for w in WORDINGS:
        counted = [r for r in rows if r["wording"] == w and r["counted"]]
        for name in ("corrected", "sum"):
            print(f"wording {w}, {name}: gain on {sum(r[f'{name}_shows_the_gain'] for r in counted)}, loss on "
                  f"{sum(r[f'{name}_shows_a_loss'] for r in counted)} of {len(counted)} counted models")


if __name__ == "__main__":
    main()
