"""Analysis of exp20 (self-evaluation scores, P(True)) on TruthfulQA multiple choice: no GPU.

Run from the repository root with the project environment (needs `datasets` for the true/false labels):
    HF_HUB_OFFLINE=1 ./.venv/bin/python scripts/self_evaluation_analysis.py exploration
    HF_HUB_OFFLINE=1 ./.venv/bin/python scripts/self_evaluation_analysis.py confirmation

`exploration` analyses the exploration part and freezes the design: it writes
results/experiments/exp20_self_evaluation/frozen_design.json (the method, the comparisons, the tests and the
abstention thresholds). `confirmation` applies that file unchanged to the confirmation part, and stops if the
design in this script no longer equals the frozen one.

The method: each answer option is scored by the log-odds of "True" against "False" when the base model is asked
whether the option is a true answer (self-evaluation, P(True); Kadavath et al., 2022). The option with the highest
score is chosen. For selective prediction the confidence is the difference between the two highest scores, and the
question is answered only when it reaches a threshold.

Sections printed (and written as CSV files into the run's analysis/ folder):
  1. scores      MC1/MC2/MC3 of each scoring rule, its true-vs-false pairwise accuracy (all option pairs and
                 pairs whose token counts differ by at most 1) and its rank correlation with option length
  2. tests       the frozen list of paired comparisons (paired bootstrap, exact McNemar, Holm over all p-values)
  3. selective   selective prediction with the method: accuracy against coverage, and the frozen thresholds
  4. options     the score as a classifier of single options (pooled over questions)

Likelihood-based scores come from the saved option scores of exp19 (same model, same questions).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from heldout_analysis import HELDOUT_RUN, load_labels, load_run, mc_metrics, mean, spearman, write_csv  # noqa: E402
from paired_tests import exact_mcnemar, holm, paired_bootstrap  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
EXPERIMENT_DIR = ROOT / "results" / "experiments" / "exp20_self_evaluation"
FROZEN_DESIGN_PATH = EXPERIMENT_DIR / "frozen_design.json"
SPLIT_PATH = EXPERIMENT_DIR / "split.json"
METRICS = ("mc1", "mc2", "mc3")
METHOD = "self_evaluation"
EARLY_EXIT_BLOCKS = (27, 30)  # first and last block of the band, 1-based, of 36
COVERAGES = (0.25, 0.5, 0.75)

LABELS = {
    "self_evaluation": "self-evaluation, final layer, wording is_true (the method)",
    "self_evaluation_is_correct": "self-evaluation, final layer, wording is_correct",
    "self_evaluation_early_exit": "self-evaluation, early exit at blocks 27-30, wording is_true",
    "self_evaluation_early_exit_both": "self-evaluation, early exit at blocks 27-30, mean of both wordings",
    "base_likelihood": "base model likelihood, sum of token log-probabilities",
    "base_likelihood_per_token": "base model likelihood per token",
    "dola_mc": "DoLa, its multiple-choice configuration",
    "per_question_dola_static": "per-question DoLa-static",
    "longest_option": "longest option (token count)",
}

# Everything below is the frozen design. `confirmation` refuses to run if it differs from frozen_design.json.
DESIGN = {
    "model": "Qwen/Qwen2.5-3B-Instruct",
    "method": {
        "name": METHOD,
        "option_score": "log-odds of the reply token True against False at the first answer position, final layer, "
                        "wording is_true (user message in the scores file)",
        "decision": "the option with the highest score",
    },
    "selective_prediction": {
        "confidence": "difference between the two highest scores among the MC1 options",
        "rule": "answer when confidence >= threshold, otherwise abstain",
        "thresholds": "the confidence of the question at rank floor(c * n) of the exploration part, for coverage c "
                      "in 0.25, 0.5, 0.75",
    },
    "primary_metric": "mc1",
    "early_exit_blocks": list(EARLY_EXIT_BLOCKS),
    # [A, B, role]: the difference tested is A - B.
    "comparisons": [
        ["self_evaluation", "base_likelihood", "main: method against the standard multiple-choice scoring"],
        ["self_evaluation", "base_likelihood_per_token", "main: method against the best likelihood rule of the exploration part"],
        ["self_evaluation", "dola_mc", "main: method against DoLa in its multiple-choice configuration"],
        ["self_evaluation_early_exit", "self_evaluation", "ablation: reading the verdict by early exit"],
        ["self_evaluation_is_correct", "base_likelihood_per_token", "ablation: a second prompt wording"],
    ],
    "tests": "per comparison and metric (mc1, mc2, mc3): 95% paired-bootstrap interval and two-sided p-value "
             "(10,000 resamples, seed 0, comparisons in the listed order); for mc1 also the exact McNemar test; "
             "Holm adjustment over all p-values of the list",
    "mc2_note": "MC2 uses the option score in place of the option log-likelihood (softmax over the options)",
}


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def auroc(scores, ys):
    pos = [s for s, y in zip(scores, ys) if y == 1]
    neg = [s for s, y in zip(scores, ys) if y == 0]
    if not pos or not neg:
        return float("nan")
    return mean((1.0 if p > n else 0.5 if p == n else 0.0) for p in pos for n in neg)


def find_run(part: str, model: str) -> Path:
    with (EXPERIMENT_DIR / "run_matrix.csv").open(encoding="utf-8", newline="") as handle:
        rows = [r for r in csv.DictReader(handle)
                if r["part"] == part and r["model_name"] == model and r["wording_set"] == "verdict"]
    if len(rows) != 1:
        sys.exit(f"Expected one {part} run for {model} in run_matrix.csv, found {len(rows)}.")
    return EXPERIMENT_DIR / "runs" / rows[0]["run_id"]


def build_rules(S, L):
    """Scoring rules: name -> function (question, option) -> score."""
    lo, hi = EARLY_EXIT_BLOCKS
    n = lambda q, o: S[q][o]["n_tokens"]
    band = lambda q, o, w: mean(S[q][o][w][lo - 1: hi])
    return {
        "self_evaluation": lambda q, o: S[q][o]["is_true"][-1],
        "self_evaluation_is_correct": lambda q, o: S[q][o]["is_correct"][-1],
        "self_evaluation_early_exit": lambda q, o: band(q, o, "is_true"),
        "self_evaluation_early_exit_both": lambda q, o: mean(band(q, o, w) for w in ("is_true", "is_correct")),
        "base_likelihood": lambda q, o: L["pure_greedy"][q][o],
        "base_likelihood_per_token": lambda q, o: L["pure_greedy"][q][o] / n(q, o),
        "dola_mc": lambda q, o: L["dola_mc_reference"][q][o],
        "per_question_dola_static": lambda q, o: L["fanda_frozen"][q][o],
        "longest_option": lambda q, o: n(q, o),
    }


def pairwise_accuracy(rule, questions, labels, S, matched):
    """Mean over questions of P(score(true option) > score(false option)); ties count 0.5."""
    per_question = []
    for q in questions:
        values = []
        for t, lt in zip(labels[q][2], labels[q][3]):
            if lt != 1:
                continue
            for f, lf in zip(labels[q][2], labels[q][3]):
                if lf != 0 or (matched and abs(S[q][t]["n_tokens"] - S[q][f]["n_tokens"]) > 1):
                    continue
                a, b = rule(q, t), rule(q, f)
                values.append(1.0 if a > b else 0.5 if a == b else 0.0)
        if values:
            per_question.append(mean(values))
    return mean(per_question)


def confidence_of(rule, q, labels):
    top = sorted((rule(q, o) for o in labels[q][0]), reverse=True)
    return top[0] - top[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("part", choices=("exploration", "confirmation"))
    parser.add_argument("--resamples", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    run_dir = find_run(args.part, DESIGN["model"])
    scores_path = run_dir / f"{run_dir.name}_scores.json"
    if not scores_path.exists():
        sys.exit(f"{scores_path} is missing: run results/experiments/exp20_self_evaluation/run_experiment.py "
                 f"--run-id {run_dir.name}")
    design = json.loads(json.dumps(DESIGN))
    frozen = json.loads(FROZEN_DESIGN_PATH.read_text(encoding="utf-8")) if FROZEN_DESIGN_PATH.exists() else None
    if frozen is not None and frozen["design"] != design:
        sys.exit(f"The design in this script differs from {FROZEN_DESIGN_PATH}. The frozen design is not changed.")
    if args.part == "confirmation" and frozen is None:
        sys.exit("No frozen design: run `scripts/self_evaluation_analysis.py exploration` first.")

    payload = json.loads(scores_path.read_text(encoding="utf-8"))
    S = payload["scores"]
    questions = sorted(S)
    if questions != json.loads(SPLIT_PATH.read_text(encoding="utf-8"))[args.part]:
        sys.exit(f"The questions of {scores_path} are not the {args.part} part of {SPLIT_PATH}.")
    labels = load_labels()
    _, L = load_run(HELDOUT_RUN)
    rules = build_rules(S, L)
    out_dir = run_dir / "analysis"
    chance = mean(1 / len(labels[q][0]) for q in questions)
    print(f"Run: {run_dir.name} ({payload['model_name']}, {args.part} part, {len(questions)} questions, "
          f"{sum(len(S[q]) for q in questions)} options); MC1 chance level {chance:.3f}")

    # 1. scores
    per_question = {name: [mc_metrics(lambda o: rule(q, o), labels[q]) for q in questions]
                    for name, rule in rules.items()}
    print(f"\n== 1. scores\n  {'scoring rule':68s} {'MC1':>6s} {'MC2':>6s} {'MC3':>6s} {'pairs':>6s} {'matched':>8s} {'rho':>7s}")
    rows = []
    for name, rule in rules.items():
        row = {"rule": name, "description": LABELS[name], "n": len(questions)}
        row.update({m: mean(x[m] for x in per_question[name]) for m in METRICS})
        if name == "longest_option":
            row["mc2"] = ""  # a softmax over token counts is not a probability over options
        row["pairwise_accuracy"] = pairwise_accuracy(rule, questions, labels, S, False)
        row["pairwise_accuracy_length_matched"] = pairwise_accuracy(rule, questions, labels, S, True)
        rhos = [spearman([S[q][o]["n_tokens"] for o in labels[q][2]], [rule(q, o) for o in labels[q][2]]) for q in questions]
        row["spearman_with_token_count"] = mean(r for r in rhos if r is not None)
        rows.append(row)
        mc2 = f"{row['mc2']:6.3f}" if row["mc2"] != "" else f"{'':6s}"
        print(f"  {LABELS[name]:68s} {row['mc1']:6.3f} {mc2} {row['mc3']:6.3f} {row['pairwise_accuracy']:6.3f} "
              f"{row['pairwise_accuracy_length_matched']:8.3f} {row['spearman_with_token_count']:+7.3f}")
    write_csv(out_dir, "scores.csv", rows)

    # 2. tests
    rng = random.Random(args.seed)
    results = []
    for a, b, role in DESIGN["comparisons"]:
        for metric in METRICS:
            xa = [x[metric] for x in per_question[a]]
            xb = [x[metric] for x in per_question[b]]
            diffs = [0.0 if abs(p - r) < 1e-6 else p - r for p, r in zip(xa, xb)]
            low, high, p_boot = paired_bootstrap(diffs, args.resamples, rng)
            row = {"a": a, "b": b, "role": role, "metric": metric, "n": len(diffs), "mean_a": mean(xa), "mean_b": mean(xb),
                   "diff": mean(diffs), "ci_low": low, "ci_high": high, "p_bootstrap": p_boot,
                   "mcnemar_b": "", "mcnemar_c": "", "p_mcnemar": ""}
            if metric == "mc1":
                won = sum(1 for p, r in zip(xa, xb) if p == 1 and r == 0)
                lost = sum(1 for p, r in zip(xa, xb) if p == 0 and r == 1)
                row.update(mcnemar_b=won, mcnemar_c=lost, p_mcnemar=exact_mcnemar(won, lost))
            results.append(row)
    keys = [("p_bootstrap", i) for i in range(len(results))]
    keys += [("p_mcnemar", i) for i, r in enumerate(results) if r["p_mcnemar"] != ""]
    for (k, i), value in zip(keys, holm([results[i][k] for k, i in keys])):
        results[i][k + "_holm"] = value
    # The bootstrap resolves p only to 2 / resamples, so after Holm over len(keys) p-values the smallest value
    # it can support is len(keys) * 2 / resamples. The exact McNemar test has no such limit.
    floor = len(keys) * 2 / args.resamples
    print(f"\n== 2. paired tests, A - B ({args.resamples} resamples, seed {args.seed}; p-values Holm-adjusted over the "
          f"{len(keys)} p-values of the list)")
    print(f"  {'A':32s} {'B':26s} {'metric':6s} {'A':>6s} {'B':>6s} {'A-B':>7s} {'95% CI':>17s} {'p_boot':>7s} {'b/c':>8s} {'p_McN':>7s}")
    for r in results:
        p_boot = f"<{floor:.3f}" if r["p_bootstrap_holm"] < floor else f"{r['p_bootstrap_holm']:.3f}"
        bc = f"{r['mcnemar_b']}/{r['mcnemar_c']}" if r["metric"] == "mc1" else ""
        p_mcn = ("<0.001" if r["p_mcnemar_holm"] < 0.001 else f"{r['p_mcnemar_holm']:.3f}") if r["metric"] == "mc1" else ""
        print(f"  {r['a']:32s} {r['b']:26s} {r['metric']:6s} {r['mean_a']:6.3f} {r['mean_b']:6.3f} {r['diff']:+7.3f} "
              f"[{r['ci_low']:+.3f}, {r['ci_high']:+.3f}] {p_boot:>7s} {bc:>8s} {p_mcn:>7s}")
    write_csv(out_dir, "paired_tests.csv", results)

    # 3. selective prediction with the method
    rule = rules[METHOD]
    correct = [x["mc1"] for x in per_question[METHOD]]
    confidence = [confidence_of(rule, q, labels) for q in questions]
    order = sorted(range(len(questions)), key=lambda i: -confidence[i])
    here = {str(c): confidence[order[max(1, int(c * len(order))) - 1]] for c in COVERAGES}
    if frozen is None:
        frozen = {
            "frozen_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "git_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip(),
            "design": design,
            "abstention_thresholds": here,
            "set_on": {"run_id": run_dir.name, "part": args.part, "questions": len(questions),
                       "scores_sha256": sha256_of(scores_path)},
            "split_sha256": sha256_of(SPLIT_PATH),
        }
        FROZEN_DESIGN_PATH.write_text(json.dumps(frozen, indent=2) + "\n", encoding="utf-8")
        print(f"\nDesign frozen: wrote {FROZEN_DESIGN_PATH}")
    elif args.part == "exploration" and (frozen["abstention_thresholds"] != here
                                         or frozen["set_on"]["scores_sha256"] != sha256_of(scores_path)):
        sys.exit("The exploration scores no longer give the frozen thresholds. The frozen design is not changed.")
    thresholds = frozen["abstention_thresholds"]

    print(f"\n== 3. selective prediction with the method (design frozen {frozen['frozen_at_utc']})")
    print(f"  AUROC of the confidence for MC1 correctness: {auroc(confidence, correct):.3f}")
    rows = [{"kind": "all questions", "coverage_target": 1.0, "threshold": "", "answered": len(questions),
             "coverage": 1.0, "selective_accuracy": mean(correct), "ci_low": "", "ci_high": ""}]
    for c in COVERAGES:
        top = order[: max(1, int(c * len(order)))]
        rows.append({"kind": "ranked within this part", "coverage_target": c, "threshold": "", "answered": len(top),
                     "coverage": len(top) / len(order), "selective_accuracy": mean(correct[i] for i in top),
                     "ci_low": "", "ci_high": ""})
    rng = random.Random(args.seed)
    for c in COVERAGES:
        tau = thresholds[str(c)]
        answered = [i for i in range(len(questions)) if confidence[i] >= tau]
        flags = [(1 if confidence[i] >= tau else 0, correct[i]) for i in range(len(questions))]
        boot = []
        for _ in range(args.resamples):
            sample = [flags[rng.randrange(len(flags))] for _ in range(len(flags))]
            hits = [y for a, y in sample if a]
            if hits:
                boot.append(mean(hits))
        boot.sort()
        rows.append({"kind": "frozen threshold (set on the exploration part)", "coverage_target": c, "threshold": tau,
                     "answered": len(answered), "coverage": len(answered) / len(questions),
                     "selective_accuracy": mean(correct[i] for i in answered),
                     "ci_low": boot[int(0.025 * len(boot))], "ci_high": boot[int(0.975 * len(boot)) - 1]})
    for r in rows:
        ci = f" [{r['ci_low']:.3f}, {r['ci_high']:.3f}]" if r["ci_low"] != "" else ""
        tau = f", threshold {r['threshold']:.4f}" if r["threshold"] != "" else ""
        print(f"  {r['kind']:48s} target {r['coverage_target']:.2f}{tau}: answered {r['answered']:3d} "
              f"({r['coverage']:.3f}), accuracy on answered {r['selective_accuracy']:.3f}{ci}")
    write_csv(out_dir, "selective_prediction.csv", rows)

    # 4. the score as a classifier of single options
    ys = [l for q in questions for l in labels[q][3]]
    vs = [rule(q, o) for q in questions for o in labels[q][2]]
    row = {"options": len(ys), "true_share": mean(ys), "auroc_pooled": auroc(vs, ys),
           "true_options_with_positive_score": mean(v > 0 for v, y in zip(vs, ys) if y == 1),
           "false_options_with_positive_score": mean(v > 0 for v, y in zip(vs, ys) if y == 0)}
    print(f"\n== 4. the method's score as a classifier of single options (pooled over questions)")
    print(f"  options {row['options']}, true share {row['true_share']:.3f}; AUROC {row['auroc_pooled']:.3f}; score > 0 "
          f"(True more likely than False) for {row['true_options_with_positive_score']:.3f} of the true and "
          f"{row['false_options_with_positive_score']:.3f} of the false options")
    write_csv(out_dir, "option_classification.csv", [row])


if __name__ == "__main__":
    main()
