"""Print MC1/MC2/MC3 (or the run's own metrics) and step latency per decoder for every saved experiment run.

Usage, from the repository root:
    python scripts/summarise_runs.py [results/experiments]
"""
from __future__ import annotations

import collections
import csv
import sys
from pathlib import Path


def main() -> None:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "results/experiments")
    summaries = list(root.glob("exp*/runs/*/*_summary.csv")) + list(root.glob("exploration/exp*/runs/*/*_summary.csv"))
    for summary in sorted(summaries, key=lambda s: s.parts[-4:]):
        if "pairwise" in summary.name:
            continue
        rows = list(csv.DictReader(summary.open(encoding="utf-8")))
        scores: dict[str, dict[str, float]] = collections.defaultdict(dict)
        counts, step_ms = {}, {}
        for row in rows:
            if row["score_mean"]:
                scores[row["decoder"]][row.get("metric_name", "")] = float(row["score_mean"])
            counts[row["decoder"]] = row.get("num_examples")
            step_ms[row["decoder"]] = row.get("latency_per_step_ms_mean")
        print(f"## {summary.parts[-4]}/{summary.parts[-2]}")
        for decoder, metrics in scores.items():
            text = " ".join(f"{name}={value:.3f}" for name, value in metrics.items())
            latency = f" step_ms={float(step_ms[decoder]):.1f}" if step_ms[decoder] else ""
            print(f"   {decoder:32s} n={counts[decoder]} {text}{latency}")


if __name__ == "__main__":
    main()
