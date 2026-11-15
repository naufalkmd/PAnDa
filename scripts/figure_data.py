"""Write the data files of the report's figures into paper/figures/data/ (no GPU, no dataset download).

Run from the repository root:
    python scripts/figure_data.py

Every plotted number comes from a results file of exp19, exp20 or exp21; this script only selects, renames and
(for F3) adds 95 % bootstrap intervals. The paper folder then builds on its own (arXiv needs that).

    f3_dev_vs_heldout.csv   F3: MC1 and MC2 per rule on the 50 development and 767 held-out questions, exp19,
                            with 95 % percentile bootstrap intervals of the mean (10,000 resamples, seed 0)
    f4_curve.csv            F4: risk-coverage curve of self-evaluation on the 400 confirmation questions, exp20
    f4_frozen.csv           F4: the three thresholds frozen on the exploration questions, with their intervals
    f4_reference.csv        F4: MC1 of base likelihood and DoLa (multiple-choice configuration), same questions
    f5_<model>.csv          F5: MC1 of the self-evaluation verdict read after each block (wording is_true),
                            exploration questions, exp20; depth = block / number of blocks; the model's
                            base-likelihood MC1 on the same questions (exp21) on the first and last row
    f5_models.csv           F5: panel order, labels, final-layer MC1 and base-likelihood MC1 (exp21) per model
"""
from __future__ import annotations

import csv
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from heldout_analysis import DEV_RUN, HELDOUT_RUN, load_run, mean  # noqa: E402
from paired_tests import paired_bootstrap  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
EXP20 = ROOT / "results" / "experiments" / "exp20_self_evaluation"
OUT = ROOT / "paper" / "figures" / "data"
RESAMPLES, SEED = 10_000, 0

F3_RULES = (  # (decoder in exp19, label in the report)
    ("pure_greedy", "Base likelihood"),
    ("dola_mc_reference", "DoLa (MC configuration)"),
    ("dola", "DoLa (generation settings)"),
    ("fanda_frozen", "Per-question DoLa-static"),
)
F5_MODELS = (  # (model name, file slug, label), smallest to largest within each family
    ("Qwen/Qwen2.5-0.5B-Instruct", "qwen25_05b", "Qwen2.5-0.5B"),
    ("Qwen/Qwen2.5-1.5B-Instruct", "qwen25_15b", "Qwen2.5-1.5B"),
    ("Qwen/Qwen2.5-3B-Instruct", "qwen25_3b", "Qwen2.5-3B"),
    ("google/gemma-3-1b-it", "gemma3_1b", "Gemma 3 1B"),
    ("google/gemma-3-4b-it", "gemma3_4b", "Gemma 3 4B"),
    ("HuggingFaceTB/SmolLM2-1.7B-Instruct", "smollm2_17b", "SmolLM2-1.7B"),
    ("tiiuae/Falcon3-3B-Instruct", "falcon3_3b", "Falcon3-3B"),
    ("microsoft/Phi-3.5-mini-instruct", "phi35_mini", "Phi-3.5-mini"),
)


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write(name: str, rows: list[dict]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"  wrote {name} ({len(rows)} rows)")


def f3() -> None:
    saved, _ = load_run(HELDOUT_RUN)
    dev_saved, _ = load_run(DEV_RUN)
    dev_questions = set(next(iter(dev_saved.values()))["mc1"])
    questions = sorted(saved["pure_greedy"]["mc1"])
    splits = {"dev": [q for q in questions if q in dev_questions],
              "held": [q for q in questions if q not in dev_questions]}
    assert (len(splits["dev"]), len(splits["held"])) == (50, 767)
    rows = []
    for x, (decoder, label) in enumerate(F3_RULES, start=1):
        row = {"x": x, "rule": label}
        for metric in ("mc1", "mc2"):
            for split, qs in splits.items():
                values = [saved[decoder][metric][q] for q in qs]
                m = mean(values)
                lo, hi, _ = paired_bootstrap(values, RESAMPLES, random.Random(SEED))
                row.update({f"{metric}_{split}": round(m, 4), f"{metric}_{split}_minus": round(m - lo, 4),
                            f"{metric}_{split}_plus": round(hi - m, 4)})
        rows.append(row)
    write("f3_dev_vs_heldout.csv", rows)


def f4() -> None:
    analysis = EXP20 / "runs" / "run_02_qwen25_3b_confirmation" / "analysis"
    write("f4_curve.csv", [{"coverage": r["coverage"], "accuracy": r["selective_accuracy"]}
                           for r in read_csv(analysis / "selective_prediction_curve.csv")])
    frozen = [r for r in read_csv(analysis / "selective_prediction.csv") if r["kind"].startswith("frozen threshold")]
    write("f4_frozen.csv", [{"target": r["coverage_target"], "coverage": r["coverage"],
                             "accuracy": r["selective_accuracy"],
                             "minus": round(float(r["selective_accuracy"]) - float(r["ci_low"]), 4),
                             "plus": round(float(r["ci_high"]) - float(r["selective_accuracy"]), 4)}
                            for r in frozen])
    scores = {r["rule"]: r for r in read_csv(analysis / "scores.csv")}
    write("f4_reference.csv", [{"rule": label, "mc1": scores[rule]["mc1"]} for rule, label in
                               (("base_likelihood", "Base likelihood"), ("dola_mc", "DoLa (MC configuration)"),
                                ("self_evaluation", "Self-evaluation (all questions)"))])


def f5() -> None:
    blocks = [r for r in read_csv(EXP20 / "cross_model" / "early_exit_by_block.csv")
              if r["wording"] == "is_true" and r["run_id"].endswith("_exploration")]
    likelihood = {r["model"]: r for r in read_csv(EXP20 / "cross_model" / "self_evaluation_vs_likelihood.csv")}
    summary = []
    for panel, (model, slug, label) in enumerate(F5_MODELS, start=1):
        rows = sorted((r for r in blocks if r["model"] == model), key=lambda r: int(r["block"]))
        n_blocks = int(rows[0]["blocks"])
        assert [int(r["block"]) for r in rows] == list(range(1, n_blocks + 1)), model
        base = round(float(likelihood[model]["base_likelihood_mc1"]), 4)  # exp21, same 417 questions
        # the reference value only on the first and last block ("nan" elsewhere), so it plots as one segment
        write(f"f5_{slug}.csv", [{"block": r["block"], "depth": round(int(r["block"]) / n_blocks, 4),
                                  "mc1": round(float(r["mc1"]), 4),
                                  "base_likelihood_mc1": base if int(r["block"]) in (1, n_blocks) else "nan"}
                                 for r in rows])
        summary.append({"panel": panel, "slug": slug, "label": label, "blocks": n_blocks,
                        "final_mc1": round(float(rows[-1]["mc1"]), 4), "base_likelihood_mc1": base})
    write("f5_models.csv", summary)


if __name__ == "__main__":
    f3()
    f4()
    f5()
