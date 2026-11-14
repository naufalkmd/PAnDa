"""Paired significance tests between decoders of one saved run (TruthfulQA MC1/MC2/MC3).

For each pair "A:B" and each metric, prints n, both means, the difference A - B, a 95% paired-bootstrap
confidence interval and two-sided p-value, and for MC1 (a 0/1 score) also the exact McNemar test.
Questions are matched by their text, so every test is paired on the same questions.

Usage, from the repository root:
    python scripts/paired_tests.py RUN_DIR --pairs fanda:dola fanda:pure_greedy
    python scripts/paired_tests.py RUN_DIR --pairs fanda:dola --exclude-questions-of DEV_RUN_DIR --holm
    python scripts/paired_tests.py RUN_DIR --pairs fanda:dola --out results.csv

RUN_DIR is a folder such as results/experiments/exp11_core_decoder_comparison/runs/run_01_default.
--exclude-questions-of drops every question that appears in another run (for example the 50-question
development set), which gives held-out scores for a full-dataset run.
--holm adjusts all p-values printed by one call for multiple comparisons (Holm-Bonferroni).
Standard library only; the bootstrap uses a fixed seed (--seed, default 0).
"""
from __future__ import annotations

import argparse
import csv
import math
import random
import sys
from collections import defaultdict
from pathlib import Path

METRICS = ("mc1", "mc2", "mc3")


def raw_predictions_file(run_dir: Path) -> Path:
    files = [f for f in run_dir.glob("*_raw_predictions.csv")]
    if len(files) != 1:
        sys.exit(f"Expected one *_raw_predictions.csv in {run_dir}, found {len(files)}.")
    return files[0]


def load_scores(run_dir: Path) -> dict[str, dict[str, dict[str, float]]]:
    """Return scores[decoder][metric][question] = score."""
    scores: dict[str, dict[str, dict[str, float]]] = defaultdict(lambda: defaultdict(dict))
    with raw_predictions_file(run_dir).open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            metric, decoder, question = row["metric_name"], row["decoder"], row["question"]
            if metric not in METRICS or row["score"] == "":
                continue
            if question in scores[decoder][metric]:
                sys.exit(f"Duplicate question for {decoder}/{metric} in {run_dir}: {question[:60]!r}")
            scores[decoder][metric][question] = float(row["score"])
    return scores


def questions_of(run_dir: Path) -> set[str]:
    with raw_predictions_file(run_dir).open(encoding="utf-8", newline="") as handle:
        return {row["question"] for row in csv.DictReader(handle)}


def exact_mcnemar(b: int, c: int) -> float:
    """Two-sided exact McNemar p-value: binomial test of b successes in b + c trials at p = 0.5."""
    n = b + c
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, i) for i in range(min(b, c) + 1)) / 2**n
    return min(1.0, 2 * tail)


def paired_bootstrap(diffs: list[float], resamples: int, rng: random.Random) -> tuple[float, float, float]:
    """95% percentile interval of the mean difference and a two-sided bootstrap p-value."""
    n = len(diffs)
    means = sorted(sum(diffs[rng.randrange(n)] for _ in range(n)) / n for _ in range(resamples))
    low, high = means[int(0.025 * resamples)], means[int(0.975 * resamples) - 1]
    observed = sum(diffs) / n
    if observed == 0:
        return low, high, 1.0
    opposite = sum(1 for m in means if (m <= 0 if observed > 0 else m >= 0))
    return low, high, min(1.0, 2 * opposite / resamples)


def holm(p_values: list[float]) -> list[float]:
    order = sorted(range(len(p_values)), key=lambda i: p_values[i])
    adjusted, running = [0.0] * len(p_values), 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (len(p_values) - rank) * p_values[i]))
        adjusted[i] = running
    return adjusted


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--pairs", nargs="+", required=True, help="decoder pairs A:B (difference = A - B)")
    parser.add_argument("--metrics", nargs="+", default=list(METRICS), choices=METRICS)
    parser.add_argument("--exclude-questions-of", type=Path, default=None)
    parser.add_argument("--resamples", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--holm", action="store_true")
    parser.add_argument("--out", type=Path, default=None, help="also write the table as CSV")
    args = parser.parse_args()

    scores = load_scores(args.run_dir)
    excluded = questions_of(args.exclude_questions_of) if args.exclude_questions_of else set()
    rng = random.Random(args.seed)

    results = []
    for pair in args.pairs:
        a, _, b = pair.partition(":")
        for name in (a, b):
            if name not in scores:
                sys.exit(f"Decoder {name!r} not in {args.run_dir}. Available: {sorted(scores)}")
        for metric in args.metrics:
            common = sorted((set(scores[a][metric]) & set(scores[b][metric])) - excluded)
            if not common:
                sys.exit(f"No shared questions for {pair} / {metric}.")
            xa = [scores[a][metric][q] for q in common]
            xb = [scores[b][metric][q] for q in common]
            # Differences below 1e-6 are floating-point noise (e.g. two scorings that are identical by construction).
            diffs = [0.0 if abs(p - q) < 1e-6 else p - q for p, q in zip(xa, xb)]
            low, high, p_boot = paired_bootstrap(diffs, args.resamples, rng)
            row = {
                "pair": pair, "metric": metric, "n": len(common),
                "mean_a": sum(xa) / len(xa), "mean_b": sum(xb) / len(xb),
                "diff": sum(diffs) / len(diffs), "ci_low": low, "ci_high": high, "p_bootstrap": p_boot,
                "mcnemar_b": "", "mcnemar_c": "", "p_mcnemar": "",
            }
            if metric == "mc1":
                b_count = sum(1 for p, q in zip(xa, xb) if p == 1 and q == 0)
                c_count = sum(1 for p, q in zip(xa, xb) if p == 0 and q == 1)
                row.update(mcnemar_b=b_count, mcnemar_c=c_count, p_mcnemar=exact_mcnemar(b_count, c_count))
            results.append(row)

    if args.holm:
        keys = [("p_bootstrap", i) for i in range(len(results))]
        keys += [("p_mcnemar", i) for i, r in enumerate(results) if r["p_mcnemar"] != ""]
        adjusted = holm([results[i][k] for k, i in keys])
        for (k, i), value in zip(keys, adjusted):
            results[i][k + "_holm"] = value

    width = max(34, max(len(r["pair"]) for r in results))
    header = f"{'pair':{width}s} {'metric':6s} {'n':>4s} {'A':>6s} {'B':>6s} {'A-B':>7s} {'95% CI':>17s} {'p_boot':>7s} {'b/c':>7s} {'p_McN':>7s}"
    print(f"Run: {args.run_dir}" + (f"  (excluding {len(excluded)} questions of {args.exclude_questions_of})" if excluded else ""))
    print(f"Paired bootstrap: {args.resamples} resamples, seed {args.seed}" + ("; p-values Holm-adjusted" if args.holm else ""))
    print(header)
    for r in results:
        p_boot = r.get("p_bootstrap_holm", r["p_bootstrap"])
        p_mcn = r.get("p_mcnemar_holm", r["p_mcnemar"])
        bc = f"{r['mcnemar_b']}/{r['mcnemar_c']}" if r["metric"] == "mc1" else ""
        p_mcn_text = f"{p_mcn:.3f}" if p_mcn != "" else ""
        # The bootstrap resolves p only to about 2 / resamples, so small values are shown as a bound.
        p_boot_text = "<0.001" if p_boot < 0.001 else f"{p_boot:.3f}"
        print(f"{r['pair']:{width}s} {r['metric']:6s} {r['n']:4d} {r['mean_a']:6.3f} {r['mean_b']:6.3f} {r['diff']:+7.3f} "
              f"[{r['ci_low']:+.3f}, {r['ci_high']:+.3f}] {p_boot_text:>7s} {bc:>7s} {p_mcn_text:>7s}")

    if args.out:
        with args.out.open("w", encoding="utf-8", newline="") as handle:
            fieldnames = list(dict.fromkeys(key for r in results for key in r))
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
