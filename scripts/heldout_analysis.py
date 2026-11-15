"""Post hoc analysis of the held-out run (exp19): no GPU, reads only the saved per-option scores.

Run from the repository root with the project environment (needs `datasets` for the true/false labels):
    HF_HUB_OFFLINE=1 ./.venv/bin/python scripts/heldout_analysis.py [--out-dir DIR]

Sections printed (and written as CSV files when --out-dir is given):
  1. check     MC1/MC2/MC3 recomputed from the saved option scores equal the saved metric values
  2. scores    mean MC1/MC2/MC3 per decoder on all questions, the development set and the held-out set
  3. repro     the development questions in this run against the saved June development runs
  4. mask      plausibility constraint in multiple-choice scoring: how many option tokens fall outside
               the plausible set (each adds the mask value, -1000, to the option score) and how often that
               count alone decides MC1
  5. length    association between option score and option length, and the "longest option" baseline
  6. beta      contrast-weight sweep S = S_base + beta * S_contrast, with S_base the base model's option
               log-likelihood and S_contrast DoLa's option score in its multiple-choice configuration
               (sum of log q_N - log q_M); beta is selected on the development set only

Held-out = the questions of exp19 that are not in the development run (matched by question text).
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import random
import statistics
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paired_tests import exact_mcnemar, paired_bootstrap  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
EXP = ROOT / "results" / "experiments"
HELDOUT_RUN = EXP / "exp19_heldout_full" / "runs" / "run_01_qwen25_3b_full"
DEV_RUN = EXP / "exp12_state_persistence_diagnostics" / "runs" / "run_01_default"
JUNE_RUNS = (
    EXP / "exp11_core_decoder_comparison" / "runs" / "run_01_default",
    EXP / "exp12_state_persistence_diagnostics" / "runs" / "run_01_default",
    EXP / "exp13_logit_filter_factorial" / "runs" / "run_01_default",
)
METRICS = ("mc1", "mc2", "mc3")
MASK_VALUE = 1000.0  # magnitude of the plausibility-constraint mask value in the decoders
BETAS = (0.0, 0.02, 0.05, 0.1, 0.15, 0.2, 0.3, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 5.0, 10.0, math.inf)

csv.field_size_limit(10**9)


def raw_file(run_dir: Path) -> Path:
    files = list(run_dir.glob("*_raw_predictions.csv"))
    if len(files) != 1:
        sys.exit(f"Expected one *_raw_predictions.csv in {run_dir}, found {len(files)}.")
    return files[0]


def load_run(run_dir: Path):
    """saved[decoder][metric][question] = score; options[decoder][question] = {option text: option score}."""
    saved = defaultdict(lambda: defaultdict(dict))
    options = defaultdict(dict)
    with raw_file(run_dir).open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row["metric_name"] not in METRICS or row["score"] == "":
                continue
            saved[row["decoder"]][row["metric_name"]][row["question"]] = float(row["score"])
            if row.get("choice_scores"):
                options[row["decoder"]][row["question"]] = json.loads(row["choice_scores"])
    return saved, options


def load_labels():
    """labels[question] = (mc1 options, mc1 labels, mc2 options, mc2 labels), as in src/panda/benchmarks.py."""
    from datasets import load_dataset

    labels = {}
    for row in load_dataset("truthful_qa", "multiple_choice", split="validation"):
        labels[row["question"]] = (
            list(row["mc1_targets"]["choices"]), list(row["mc1_targets"]["labels"]),
            list(row["mc2_targets"]["choices"]), list(row["mc2_targets"]["labels"]),
        )
    return labels


def softmax(values):
    top = max(values)
    exps = [math.exp(v - top) for v in values]
    total = sum(exps)
    return [e / total for e in exps]


def mc_metrics(score_of, label_row):
    """MC1/MC2/MC3 from a function option -> score, as in src/panda/evaluation.py."""
    mc1_options, mc1_labels, mc2_options, mc2_labels = label_row
    s1 = [score_of(o) for o in mc1_options]
    true1 = [s for s, l in zip(s1, mc1_labels) if l == 1]
    false1 = [s for s, l in zip(s1, mc1_labels) if l == 0]
    s2 = [score_of(o) for o in mc2_options]
    probs = softmax(s2)
    true2 = [s for s, l in zip(s2, mc2_labels) if l == 1]
    cutoff = max(s for s, l in zip(s2, mc2_labels) if l == 0)
    return {
        "mc1": float(max(true1) > max(false1)),
        "mc2": sum(p for p, l in zip(probs, mc2_labels) if l == 1),
        "mc3": statistics.mean(float(s > cutoff) for s in true2),
    }


def mean(values):
    values = list(values)
    return sum(values) / len(values) if values else float("nan")


def spearman(xs, ys):
    def ranks(values):
        order = sorted(range(len(values)), key=lambda i: values[i])
        out, i = [0.0] * len(values), 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
                j += 1
            for k in range(i, j + 1):
                out[order[k]] = (i + j) / 2 + 1
            i = j + 1
        return out

    rx, ry = ranks(xs), ranks(ys)
    mx, my = mean(rx), mean(ry)
    sx = math.sqrt(sum((a - mx) ** 2 for a in rx))
    sy = math.sqrt(sum((b - my) ** 2 for b in ry))
    if sx == 0 or sy == 0:
        return None
    return sum((a - mx) * (b - my) for a, b in zip(rx, ry)) / (sx * sy)


def write_csv(out_dir: Path | None, name: str, rows: list[dict]):
    if out_dir is None or not rows:
        return
    out_dir.mkdir(parents=True, exist_ok=True)
    with (out_dir / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(dict.fromkeys(k for r in rows for k in r)))
        writer.writeheader()
        writer.writerows(rows)
    print(f"  wrote {out_dir / name}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out-dir", type=Path, default=None)
    parser.add_argument("--resamples", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    labels = load_labels()
    saved, options = load_run(HELDOUT_RUN)
    decoders = list(saved)
    questions = sorted(saved["pure_greedy"]["mc1"])
    dev_saved, _ = load_run(DEV_RUN)
    dev_questions = set(next(iter(dev_saved.values()))["mc1"])
    dev = [q for q in questions if q in dev_questions]
    held = [q for q in questions if q not in dev_questions]
    missing = [q for q in questions if q not in labels]
    print(f"questions: {len(questions)} in the run, {len(dev)} development, {len(held)} held-out, "
          f"{len(missing)} without labels")

    # ---- 1. check -------------------------------------------------------------------------------------------
    print("\n== 1. check: metrics recomputed from the saved option scores vs the saved values")
    worst, absent = 0.0, 0
    for d in decoders:
        for q in questions:
            table = options[d][q]
            absent += sum(o not in table for o in labels[q][0] + labels[q][2])
            if any(o not in table for o in labels[q][0] + labels[q][2]):
                continue
            again = mc_metrics(table.__getitem__, labels[q])
            worst = max(worst, max(abs(again[m] - saved[d][m][q]) for m in METRICS))
    print(f"  largest absolute difference over all decoders, questions and metrics: {worst:.2e}; "
          f"options missing from the saved scores: {absent}")

    # ---- 2. scores ------------------------------------------------------------------------------------------
    print("\n== 2. mean scores per decoder")
    print(f"  {'decoder':24s} " + " ".join(f"{name + ' ' + m:>10s}" for name in ("all", "dev", "held") for m in METRICS))
    score_rows = []
    for d in decoders:
        row = {"decoder": d}
        for name, subset in (("all", questions), ("dev", dev), ("heldout", held)):
            for m in METRICS:
                row[f"{name}_{m}"] = round(mean(saved[d][m][q] for q in subset), 4)
            row[f"{name}_n"] = len(subset)
        score_rows.append(row)
        print(f"  {d:24s} " + " ".join(f"{row[f'{name}_{m}']:10.3f}" for name in ("all", "dev", "heldout") for m in METRICS))
    write_csv(args.out_dir, "scores_by_split.csv", score_rows)

    # ---- 3. repro -------------------------------------------------------------------------------------------
    print("\n== 3. development questions: this run vs the saved June runs (same decoder name, same questions)")
    repro_rows = []
    for run_dir in JUNE_RUNS:
        if not run_dir.exists():
            continue
        june, _ = load_run(run_dir)
        for d in sorted(set(june) & set(saved)):
            common = sorted(set(june[d]["mc1"]) & set(saved[d]["mc1"]))
            if not common:
                continue
            row = {"june_run": run_dir.parent.parent.name, "decoder": d, "n": len(common)}
            for m in METRICS:
                row[f"june_{m}"] = round(mean(june[d][m][q] for q in common), 4)
                row[f"now_{m}"] = round(mean(saved[d][m][q] for q in common), 4)
            row["mc1_flips"] = sum(june[d]["mc1"][q] != saved[d]["mc1"][q] for q in common)
            repro_rows.append(row)
            print(f"  {row['june_run'][:34]:34s} {d:22s} n={row['n']:3d}  MC1 {row['june_mc1']:.3f} -> {row['now_mc1']:.3f} "
                  f"({row['mc1_flips']} questions changed)  MC2 {row['june_mc2']:.3f} -> {row['now_mc2']:.3f}  "
                  f"MC3 {row['june_mc3']:.3f} -> {row['now_mc3']:.3f}")
    write_csv(args.out_dir, "development_reproduction.csv", repro_rows)

    # ---- 4. mask --------------------------------------------------------------------------------------------
    print("\n== 4. plausibility constraint in multiple-choice scoring (decoder dola, held-out questions)")
    masked = lambda score: max(0, round(-score / MASK_VALUE))
    residuals = [s + MASK_VALUE * masked(s) for q in held for s in options["dola"][q].values()]
    all_counts = [masked(s) for q in held for s in options["dola"][q].values()]
    print(f"  options: {len(all_counts)}; with at least one masked token: {mean(c > 0 for c in all_counts):.1%}; "
          f"masked tokens per option: mean {mean(all_counts):.2f}, median {statistics.median(all_counts)}, max {max(all_counts)}")
    print(f"  option score minus -1000 x count (the part not due to the mask): min {min(residuals):.1f}, max {max(residuals):.1f}")
    groups = defaultdict(list)
    for q in held:
        mc1_options, mc1_labels, _, _ = labels[q]
        true_count = [masked(options["dola"][q][o]) for o, l in zip(mc1_options, mc1_labels) if l == 1][0]
        false_min = min(masked(options["dola"][q][o]) for o, l in zip(mc1_options, mc1_labels) if l == 0)
        key = "true option has more masked tokens" if true_count > false_min else (
            "true option has fewer masked tokens" if true_count < false_min else "same count")
        groups[key].append(q)
    mask_rows = []
    for key in ("true option has more masked tokens", "same count", "true option has fewer masked tokens"):
        qs = groups[key]
        row = {"group": key, "questions": len(qs), "share": round(len(qs) / len(held), 4),
               "mc1_dola": round(mean(saved["dola"]["mc1"][q] for q in qs), 4) if qs else "",
               "mc1_base": round(mean(saved["pure_greedy"]["mc1"][q] for q in qs), 4) if qs else "",
               "mc1_dola_mc_reference": round(mean(saved["dola_mc_reference"]["mc1"][q] for q in qs), 4) if qs else ""}
        mask_rows.append(row)
        print(f"  {key:38s} {len(qs):4d} questions ({row['share']:.1%}): MC1 DoLa(generation settings) {row['mc1_dola']}, "
              f"base model {row['mc1_base']}, DoLa(MC configuration) {row['mc1_dola_mc_reference']}")
    lost = [q for q in held if saved["pure_greedy"]["mc1"][q] == 1 and saved["dola"]["mc1"][q] == 0]
    lost_by_mask = sum(q in groups["true option has more masked tokens"] for q in lost)
    print(f"  questions the base model answers correctly and DoLa(generation settings) does not: {len(lost)}; "
          f"of these, true option has more masked tokens: {lost_by_mask}")
    write_csv(args.out_dir, "mask_counts.csv", mask_rows)

    # ---- 5. length ------------------------------------------------------------------------------------------
    print("\n== 5. option score vs option length in characters (held-out questions, MC2 option set)")
    length_rows = []
    for d in decoders:
        rhos = [r for q in held if (r := spearman([len(o) for o in labels[q][2]],
                                                  [options[d][q][o] for o in labels[q][2]])) is not None]
        length_rows.append({"decoder": d, "mean_spearman_score_vs_length": round(mean(rhos), 4), "questions": len(rhos)})
        print(f"  {d:24s} mean within-question Spearman correlation {mean(rhos):+.3f}")
    for name, sign in (("longest option", 1), ("shortest option", -1)):
        m = {k: mean(mc_metrics(lambda o: sign * len(o), labels[q])[k] for q in held) for k in ("mc1", "mc3")}
        length_rows.append({"decoder": name, "mc1": round(m["mc1"], 4), "mc3": round(m["mc3"], 4)})
        print(f"  baseline, choose the {name}: MC1 {m['mc1']:.3f}, MC3 {m['mc3']:.3f}")
    write_csv(args.out_dir, "length_association.csv", length_rows)

    # ---- 6. beta --------------------------------------------------------------------------------------------
    print("\n== 6. contrast weight: S = S_base + beta * S_contrast (beta = inf: S_contrast alone)")
    base, contrast = options["pure_greedy"], options["dola_mc_reference"]

    def per_question(beta, subset):
        if math.isinf(beta):
            return {q: mc_metrics(lambda o: contrast[q][o], labels[q]) for q in subset}
        return {q: mc_metrics(lambda o: base[q][o] + beta * contrast[q][o], labels[q]) for q in subset}

    beta_rows, by_beta = [], {}
    for beta in BETAS:
        d_scores, h_scores = per_question(beta, dev), per_question(beta, held)
        by_beta[beta] = (d_scores, h_scores)
        row = {"beta": beta}
        for name, scores in (("dev", d_scores), ("heldout", h_scores)):
            for m in METRICS:
                row[f"{name}_{m}"] = round(mean(s[m] for s in scores.values()), 4)
        beta_rows.append(row)
    print(f"  {'beta':>6s} " + " ".join(f"{name + ' ' + m:>10s}" for name in ("dev", "held") for m in METRICS))
    for row in beta_rows:
        print(f"  {row['beta']:6.2f} " + " ".join(f"{row[f'{name}_{m}']:10.3f}" for name in ("dev", "heldout") for m in METRICS))
    # Selection rule, fixed before looking at held-out scores: highest development MC1, ties by MC3, then MC2,
    # then the smallest beta.
    chosen = max(beta_rows, key=lambda r: (r["dev_mc1"], r["dev_mc3"], r["dev_mc2"], -r["beta"]))["beta"]
    print(f"  beta selected on the development set: {chosen}")
    rng = random.Random(args.seed)
    chosen_held = by_beta[chosen][1]
    test_rows = []
    for other in ("pure_greedy", "dola_mc_reference"):
        for m in METRICS:
            a = [chosen_held[q][m] for q in held]
            b = [saved[other][m][q] for q in held]
            diffs = [0.0 if abs(x - y) < 1e-6 else x - y for x, y in zip(a, b)]
            low, high, p_boot = paired_bootstrap(diffs, args.resamples, rng)
            row = {"comparison": f"beta={chosen} - {other}", "metric": m, "n": len(held), "mean_a": round(mean(a), 4),
                   "mean_b": round(mean(b), 4), "diff": round(mean(diffs), 4), "ci_low": round(low, 4),
                   "ci_high": round(high, 4), "p_bootstrap": p_boot}
            text = ""
            if m == "mc1":
                wins = sum(x == 1 and y == 0 for x, y in zip(a, b))
                losses = sum(x == 0 and y == 1 for x, y in zip(a, b))
                row.update(mcnemar_b=wins, mcnemar_c=losses, p_mcnemar=exact_mcnemar(wins, losses))
                text = f"  McNemar {wins}/{losses} p={row['p_mcnemar']:.3f}"
            test_rows.append(row)
            print(f"  held-out, beta={chosen} vs {other:18s} {m}: {row['mean_a']:.3f} vs {row['mean_b']:.3f}, "
                  f"difference {row['diff']:+.3f} [{low:+.3f}, {high:+.3f}], p={p_boot:.3f}{text}")
    write_csv(args.out_dir, "contrast_weight_sweep.csv", beta_rows)
    write_csv(args.out_dir, "contrast_weight_tests.csv", test_rows)


if __name__ == "__main__":
    main()
