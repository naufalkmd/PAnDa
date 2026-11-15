"""Self-evaluation against the base model's likelihood on eight models (exp20 against exp21): no GPU.

Run from the repository root with the project environment (needs `datasets` for the true/false labels):
    HF_HUB_OFFLINE=1 ./.venv/bin/python scripts/self_evaluation_vs_likelihood.py

exp20 compared self-evaluation with likelihood scoring on Qwen2.5-3B only. exp21 scores the base model's option
log-likelihood for all eight models with the code path of exp19. This script compares the two on the exploration
questions of exp20, per model, and checks that exp21 reproduces exp19 on Qwen2.5-3B.

PROTOCOL below was fixed before any exp21 score existed and is written into the output folder.
Writes exp20's cross_model/self_evaluation_vs_likelihood.csv and exp21's reproduction_check.json.
"""
from __future__ import annotations

import csv
import json
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from heldout_analysis import HELDOUT_RUN, load_labels, load_run, mc_metrics, mean, write_csv  # noqa: E402
from paired_tests import exact_mcnemar, paired_bootstrap  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
EXP20 = ROOT / "results" / "experiments" / "exp20_self_evaluation"
EXP21 = ROOT / "results" / "experiments" / "exp21_likelihood_baselines"
OUT_DIR = EXP20 / "cross_model"
RESAMPLES, SEED = 10_000, 0
METRICS = ("mc1", "mc2", "mc3")

PROTOCOL = {
    "data": "the 417 exploration questions of exp20, eight models; exp21 scores all 817 questions, the confirmation "
            "questions are not used here because self-evaluation was scored on them for Qwen2.5-3B only",
    "rules": {
        "self_evaluation": "final-layer log-odds of True against False, wording is_true (the frozen exp20 method)",
        "base_likelihood": "sum of the option's token log-probabilities under the base model (exp21, pure_greedy)",
        "base_likelihood_per_token": "the same sum divided by the option's token count (count from exp20)",
        "longest_option": "the option's token count",
    },
    "test": f"MC1 of self_evaluation minus MC1 of each likelihood rule on the same questions: 95% paired-bootstrap "
            f"interval ({RESAMPLES} resamples, seed {SEED} per model and comparison) and exact McNemar; MC2 and MC3 "
            f"differences reported with their intervals",
    "statement": "self-evaluation is said to beat likelihood scoring on a model if its MC1 difference against both "
                 "likelihood rules is positive and both intervals exclude 0; the report gives the number of models "
                 "for which this holds, and names the others",
    "caveats": "on Qwen2.5-3B the exploration questions are the ones the exp20 design was chosen on (its clean test is "
               "the confirmation part); on the other seven models the final-layer method was fixed before their "
               "scores existed. Models whose verdict is at chance are reported and flagged.",
    "reproduction_check": "exp21 run_01 (Qwen2.5-3B) against exp19 pure_greedy on all 817 questions: largest absolute "
                          "difference of the option scores, and the number of questions whose MC1 differs",
}


def option_scores(run_dir: Path) -> dict:
    return load_run(run_dir)[1]["pure_greedy"]


def reproduction_check(labels) -> dict:
    run = EXP21 / "runs" / "run_01_qwen25_3b"
    a, b = option_scores(run), option_scores(HELDOUT_RUN)
    assert sorted(a) == sorted(b), "exp21 and exp19 cover different questions"
    diffs = [abs(a[q][o] - b[q][o]) for q in a for o in a[q]]
    mc1 = lambda S, q: mc_metrics(lambda o: S[q][o], labels[q])["mc1"]
    return {"questions": len(a), "options": len(diffs), "largest_option_score_difference": max(diffs),
            "options_differing_by_more_than_0.01": sum(d > 0.01 for d in diffs),
            "questions_with_different_mc1": sum(mc1(a, q) != mc1(b, q) for q in a)}


def main() -> None:
    labels = load_labels()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "likelihood_protocol.json").write_text(json.dumps(PROTOCOL, indent=2) + "\n", encoding="utf-8")
    with (EXP20 / "run_matrix.csv").open(encoding="utf-8", newline="") as handle:
        verdict_runs = {r["model_name"]: r["run_id"] for r in csv.DictReader(handle)
                        if r["part"] == "exploration" and r["wording_set"] == "verdict"}
    with (EXP21 / "run_matrix.csv").open(encoding="utf-8", newline="") as handle:
        likelihood_runs = {r["model_name"]: r["run_id"] for r in csv.DictReader(handle)}

    if any((EXP21 / "runs" / "run_01_qwen25_3b").glob("*_raw_predictions.csv")):
        check = reproduction_check(labels)
        (EXP21 / "reproduction_check.json").write_text(json.dumps(check, indent=2) + "\n", encoding="utf-8")
        print("reproduction check against exp19:", check)

    rows = []
    for model, run_id in verdict_runs.items():
        lik_dir = EXP21 / "runs" / likelihood_runs[model]
        if not any(lik_dir.glob("*_raw_predictions.csv")):
            print(f"\n{model}: likelihood not scored yet")
            continue
        S = json.loads((EXP20 / "runs" / run_id / f"{run_id}_scores.json").read_text(encoding="utf-8"))["scores"]
        L = option_scores(lik_dir)
        Q = sorted(S)
        chance = mean(1 / len(labels[q][0]) for q in Q)
        floor = chance + 2 * math.sqrt(chance * (1 - chance) / len(Q))
        rules = {
            "self_evaluation": lambda q, o: S[q][o]["is_true"][-1],
            "base_likelihood": lambda q, o: L[q][o],
            "base_likelihood_per_token": lambda q, o: L[q][o] / S[q][o]["n_tokens"],
            "longest_option": lambda q, o: S[q][o]["n_tokens"],
        }
        res = {name: [mc_metrics(lambda o: fn(q, o), labels[q]) for q in Q] for name, fn in rules.items()}
        row = {"model": model, "n": len(Q), "verdict_at_chance": mean(x["mc1"] for x in res["self_evaluation"]) < floor}
        for name in rules:
            row.update({f"{name}_{m}": mean(x[m] for x in res[name]) for m in METRICS})
        beats = []
        for other in ("base_likelihood", "base_likelihood_per_token"):
            for m in METRICS:
                d = [x[m] - y[m] for x, y in zip(res["self_evaluation"], res[other])]
                lo, hi, _ = paired_bootstrap(d, RESAMPLES, random.Random(SEED))
                row.update({f"minus_{other}_{m}": mean(d), f"minus_{other}_{m}_ci_low": lo,
                            f"minus_{other}_{m}_ci_high": hi})
                if m == "mc1":
                    won = sum(1 for x, y in zip(res["self_evaluation"], res[other]) if x["mc1"] == 1 and y["mc1"] == 0)
                    lost = sum(1 for x, y in zip(res["self_evaluation"], res[other]) if x["mc1"] == 0 and y["mc1"] == 1)
                    row.update({f"minus_{other}_gained": won, f"minus_{other}_lost": lost,
                                f"minus_{other}_p_mcnemar": exact_mcnemar(won, lost)})
                    beats.append(mean(d) > 0 and lo > 0)
        row["self_evaluation_beats_likelihood"] = all(beats)
        rows.append(row)
        print(f"\n==== {model}: {len(Q)} questions, MC1 chance level {chance:.3f}"
              f"{' (verdict at chance)' if row['verdict_at_chance'] else ''}")
        for name in rules:
            print(f"  {name:26s} MC1 {row[f'{name}_mc1']:.3f}  MC2 {row[f'{name}_mc2']:.3f}  MC3 {row[f'{name}_mc3']:.3f}")
        for other in ("base_likelihood", "base_likelihood_per_token"):
            print(f"  self-evaluation minus {other:26s} MC1 {row[f'minus_{other}_mc1']:+.3f} "
                  f"[{row[f'minus_{other}_mc1_ci_low']:+.3f}, {row[f'minus_{other}_mc1_ci_high']:+.3f}], gained/lost "
                  f"{row[f'minus_{other}_gained']}/{row[f'minus_{other}_lost']}, McNemar p {row[f'minus_{other}_p_mcnemar']:.4f}")
    print()
    write_csv(OUT_DIR, "self_evaluation_vs_likelihood.csv", rows)
    print(f"self-evaluation beats both likelihood rules on {sum(r['self_evaluation_beats_likelihood'] for r in rows)} "
          f"of {len(rows)} scored models: "
          + ", ".join(m["model"].split("/")[-1] for m in rows if m["self_evaluation_beats_likelihood"]))


if __name__ == "__main__":
    main()
