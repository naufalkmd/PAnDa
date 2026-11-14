# Report checklist: per-question DoLa-static portfolio report

Status and open items for the report. The report is `paper/fanda_report.tex` (figures in `paper/figures/`;
build with `latexmk -pdf -outdir=build fanda_report.tex` from `paper/`, PDF in `paper/build/`). In the PDF, red
`[TODO]` marks a missing value and red `[verify]` a statement from an older run. `[x]` done, `[ ]` open.
The June 2026 course version stays unchanged in `paper/course_version_2026_06/`.

Last updated: 2026-11-14.

---

## A. Format and purpose

- [x] Purpose: portfolio piece (public, linked from the repository). Not a course submission, so no course AI rule
  applies; Claude drafts, the authors revise. An AI-use note is optional.
- [x] arXiv style, `article`, one column, no page limit (aim: 10–12 pages plus appendix).
- [x] Authors: Muhammad Naufal, Jeong Edon, Muhammad Aliff (Korea University). [ ] Co-authors review before publishing.
- [ ] Title. Proposal: "Fixing the Premature Layer in DoLa: A Small-Scale Study of Contrastive Layer Decoding on
  TruthfulQA". It describes what was done, with no claim the data cannot carry. Decide after the reruns.
- [x] Method name (decided 2026-11-14): **per-question DoLa-static**, built on DoLa's own term DoLa-static; "FAnDa"
  only as the former name. [ ] No "novel", "first" or "state of the art".

---

## B. Terms: use the standard name in the report

Full table: [`glossary.md`](glossary.md). The ones the text needs most:

Rule: standard machine-learning terms only, no project vocabulary. The method is "per-question DoLa-static" (DoLa's term plus a
standard qualifier). PAnDa was dropped (2026-11-14): it appears only in the one-line note on dropped alternatives. The full mapping, including the older notes' words, is in the glossary.

| In our code and older notes | In the report |
|---|---|
| `relative_top` filter | adaptive plausibility constraint (Li et al., 2023) |
| anchor, shallow layer | premature layer; the final layer is the mature layer (Chuang et al., 2024) |
| `update1`, `update4`, `frozen`; persistence | selection interval k = 1, 4, ∞ (the premature layer is re-selected every k tokens) |
| `fanda` (exp11, exp18) | Per-question DoLa-static, defined once as DoLa with the four changes |
| `fanda` (exp7–10) | Per-question DoLa-static with k = 4 |
| `panda_switch` | not in the report (dropped method) |
| jitter, `switch_rate` | fraction of steps at which the premature layer changes |
| view, regime, arbitration, always-contrast | score / distribution; setting; choosing between two scores; contrastive scoring at every step |
| "manual evaluation" (exp14) | correctness labels assigned by an LLM (Codex), unless the authors review them |

---

## C. Outline

**Challenges** (the spine: each method choice answers one, each result is labelled with one):

- **C1. The plausibility constraint can remove the correct answer's tokens.** Fact: DoLa 0.28 → 0.38 MC1 when only
  the constraint is removed (exp13), the largest single change, but not significant at n = 50 (McNemar p = 0.18).

**Development-set tests change the framing** (`experiment_log.md`, paired tests): per-question DoLa-static beats DoLa on MC3
(p = 0.005) and weakly on MC1 (p = 0.065), but neither per-question DoLa-static nor DoLa beats **greedy decoding** on Qwen2.5-3B.
Unless R2 shows otherwise, the report's claim is "per-question DoLa-static repairs DoLa's loss against greedy", not "per-question DoLa-static improves
truthfulness over standard decoding".
- **C2. Dynamic premature-layer selection changes the contrastive score from token to token.** Fact: with
  selection at every token, the premature layer changes at 69 % of steps (exp12).
- **C3. The evidence is small and noisy.** Fact: SE ≈ 0.07 on MC1 with 50 questions; DoLa scores 0.26–0.28 on the
  same questions across runs; the exp12 ranking did not replicate on a second random subset (exp16, seed 101).
- **C4. The contrast between layers differs between models.** Fact: per-question DoLa-static leads on Gemma 3 4B and trails greedy on HINT 1.5B (exp18).

| § | Section | Holds | Source |
|---|---|---|---|
| — | Abstract | Task; C1–C4; the four changes; headline result **on the held-out set** with its test; the transfer and open-ended findings, stated at their strength | after reruns |
| 1 | Introduction | Hallucination and decoding-time methods; C1–C4 with their facts; what the report contributes (plain statements, section pointers) | exp13, exp12, exp16, exp18 |
| 2 | Related work | Contrastive decoding and the plausibility constraint; DoLa (dynamic and static premature layer); TruthfulQA; truncation baselines; how per-question DoLa-static differs from each | citations, part G |
| 3 | Method | DoLa recap in DoLa's notation; the four changes, one `\paragraph` each: problem → change → evidence (C1, C2); selection interval k; selection once per question (at the first answer token); PAnDa in brief; a TikZ pipeline figure | code: `src/panda/decoders/core.py`, `local_evaluator.py` |
| 4 | Experimental setup | TruthfulQA MC (817 questions); the 50-question development subset (seed 42) and what it was used for; fresh subsets (seeds 101–404); the held-out set; MC1/MC2/MC3; paired tests; models and the candidate-layer bucket; hardware; latency | run metadata JSON |
| 5 | Results | T1 core comparison; T2 2 × 2 factorial + τ; T3 selection interval k across subsets (mean ± sd); T4 transfer; latency | part D |
| 6 | Analysis | Switching rules that did not work (exp6–10, one compact table); open-ended generation (exp14 automatic overlap; LLM or human scores, scorer stated); one case study from exp15/exp17 | exp6–10, exp14, exp15, exp17 |
| 7 | Limitations | One benchmark, MC scoring, ≤ 4B models, the development subset, the LLM judge, τ and the fixed layer changed together (unless R3 runs) | — |
| 8 | Conclusion | What each change contributed, in order of effect; what remains; two next steps | — |
| A | Appendix | Reproduction: commit, commands, run times, hardware; the full selection-interval table; the exp1–exp10 history | — |

---

## D. Where the numbers come from

Rule: **one run per table.** Never mix rows from different runs (the course version did; see the experiment log, issue 1).

| Report table / figure | Source file(s) | Status |
|---|---|---|
| T1 core comparison (dev subset) | `exp11.../run_01_default` | [ ] exp11 has its own DoLa (0.26) and `fanda` (fixed layer); use these, not exp4/exp12 |
| T1 core comparison (held-out) | new run R2 | [ ] waits for R2 |
| T2 factorial | `exp13.../run_01_default` (+ R3 for τ) | [ ] the two no-constraint cells are identical by construction: say so |
| T3 selection interval k | `exp16.../run_01`–`run_05` | [ ] seeds 202/303/404 wait for R1 |
| T4 transfer | `exp18.../run_01, run_02, run_04` | [ ] all baselines exist; fill the table |
| Paired tests | `scripts/paired_tests.py` on `*_raw_predictions.csv` (questions matched by text; `--exclude-questions-of` for held-out; `--holm`) | [x] written and run on the development set (results in `experiment_log.md`); [ ] rerun on R1/R2 |
| Switching rules (appendix) | exp6–exp10 summaries | [ ] |
| Open-ended | `exp14.../run_01_default_summary.csv` (automatic); `*_manual_eval.csv` (`reviewer = codex`) | [ ] decision R5 |
| Pipeline figure | TikZ, drawn from the code | [x] drafted in §3 |
| Evidence for C1 (mask hits) | exp19 `*_raw_predictions.csv`, column `choice_scores` of `dola` / `exp13_*_top` | [ ] count per option how many tokens fell outside V_head (each adds about −1000 to the option score) and how often the correct option has more hits than the best false one. In the 2-question GPU test (2026-11-14) every option under DoLa's generation settings scored between −3004 and −4000, so the ranking mostly counted masked tokens |
| MC2 saturation | exp19 raw predictions | [ ] contrastive option scores differ by tens of nats, so MC2 is close to 0 or 1 per question; say so when reading MC2 |

---

## E. Reruns (GPU)

On this PC, in WSL (Ubuntu), from the repository root, after `bash scripts/setup_env.sh` (environment from
`requirements-lock.txt`): `bash scripts/run_report_reruns.sh` runs R1 then R2 (`r1`, `r2` or `r4` as the first
argument runs one; extra arguments such as `--local-files-only` are passed on). Times are estimated from the June
runs' per-question speed.

- [ ] **R1 (~35 min): more random 50-question subsets for exp16**: seeds 202, 303, 404, and seed 101 again under the
  current code (`run_06_seed_101_rerun`).
- [ ] **R2 (~4.5 h): exp19, held-out evaluation on all 817 questions** with Qwen2.5-3B, one run with greedy, DoLa,
  per-question DoLa-static, three factorial cells and k = 1, 4 (replaces the earlier plan of full runs of exp11/12/13, ~31 h; see
  `results/experiments/exp19_heldout_full/README.md` for what was left out and why). Held-out scores = the 767
  questions outside the development set, matched by question text (`example_idx` is the position in the subset, not
  the dataset index), with `scripts/paired_tests.py --exclude-questions-of`. The 50 development questions inside
  this run also check that the new environment reproduces the June scores. This is the most important run.
- [ ] **R3 (optional, needs a small code change): isolate τ.** Add one decoder to `local_evaluator.py`:
  premature layer selected once per question and raw-logit difference, but selection by DoLa's divergence at τ = 1.
  Without it, the report must say that the divergence, τ and the selection interval changed together.
- [ ] **R4 (optional, ~6 h): exp19 on Gemma 3 4B** (`run_02_gemma3_4b_full`). Run it only if R2 shows a held-out
  difference worth testing on a second model; Gemma is the model where the development-set gain of per-question DoLa-static was largest
  (MC2 vs greedy, p = 0.017 unadjusted).
- [ ] **R5 (decision, no GPU): open-ended correctness labels.** Either the authors review the 250 rows labelled by
  Codex (the sheet has `review_status` and `reviewer` columns), or the report states that an LLM assigned them.
  The exp15 prefix sheet (80 rows) has no labels: label it or drop it.

---

## F. Still to fill in

- [ ] Everything in part E.
- [ ] Hardware and versions: the run metadata records **no** GPU model, torch/transformers versions or candidate
  layers. On the GPU machine, note `nvidia-smi --query-gpu=name --format=csv` and keep the `pip freeze` output.
  The exp16 seed-101 run was about 8× slower per step (different hardware).
- [x] Candidate premature layers (default `range(0, num_layers // 4, 2)` over `hidden_states[1:]`, i.e. outputs of
  blocks 1, 3, 5, ...; from the public configs): Qwen2.5-3B (36 blocks) → blocks 1, 3, 5, 7, 9; Falcon 3 3B (22) →
  1, 3, 5; HINT Qwen 1.5B (28) → 1, 3, 5, 7; Gemma 3 4B (34, from the cached config in WSL) → 1, 3, 5, 7.
  New runs also record them (`environment.model_settings.candidate_premature_layers`).
- [x] Prompt: the question followed by "Answer with one of the provided answer options only." The options are
  **not** shown in the prompt (each is scored separately), so the instruction refers to options the model never
  sees. Mention it in the setup; it is the same for every decoder. **Decision 2026-11-14: keep this prompt** for
  exp19 (matches every development run and allows the reproduction check), and state in the setup and limitations
  that it is not the standard 6-shot TruthfulQA-MC prompt, so absolute scores are not comparable with published ones.
- [x] Option score: sum of token log-probabilities (no length normalisation). MC1 = best true option above best
  false (MC1 option set); MC2 = normalised probability mass on true options; MC3 = fraction of true options above
  the best false option (MC2 option set), as in DoLa's evaluation (`src/panda/evaluation.py`).

## Draft status

- [x] §2 Related work and §3 Method drafted (2026-11-14). Method facts checked in the code: early exit = final norm +
  output head on each block's hidden state; DoLa's divergence as in its reference implementation,
  ½[KL(m‖q_N) + KL(m‖q_j)] (mixture first, checked in the DoLa repository); per-question DoLa-static uses the standard JSD at τ = 0.5; the
  −1000 mask value and its effect on option scores. PAnDa removed from §2/§3 (dropped method).
- [ ] §2/§3 cite tables `tab:factorial`, `tab:interval`, `tab:main` that the Results section will define.
- [ ] Abstract, §1, §4–§8 wait for R1/R2 (§4 Setup can be drafted now except hardware).
- [ ] Why exp11 DoLa (0.26) differs from exp4/exp13 DoLa (0.28) on the same questions: code change or nondeterminism? Check with `git log -p` on the DoLa path.

---

## G. Citations to verify (look each up, then write the BibTeX from the record)

All verified 2026-11-14 and written to `paper/references.bib` from the publisher's or archive's own record
(ACL Anthology, OpenReview, Crossref, arXiv API, Hugging Face). Each entry's comment says what it supports.

- [x] DoLa, ICLR 2024 (`chuang2024dola`). Checked in the PDF: dynamic selection by max JSD over candidate set J;
  buckets of J chosen on a validation set; DoLa-static = one layer chosen on a validation set; adaptive
  plausibility constraint α = 0.1 from Li et al.
- [x] Contrastive decoding, ACL 2023 (`li2023contrastive`). Checked: V_head = {x : p_EXP(x) ≥ α max p_EXP}, α = 0.1.
- [x] TruthfulQA, ACL 2022 (`lin2022truthfulqa`).
- [x] Nucleus sampling, ICLR 2020 (`holtzman2020curious`).
- [x] ~~Jacobi / parallel decoding (`santilli2023accelerating`)~~: removed with PAnDa; record in git history (verified ACL 2023.acl-long.689).
- [x] Significance tests: McNemar 1947 (`mcnemar1947note`); paired bootstrap, Berg-Kirkpatrick et al. 2012
  (`bergkirkpatrick2012empirical`); test choice, Dror et al. 2018 (`dror2018hitchhiker`).
- [x] Models: Qwen2.5 report (`qwen2024qwen25`); Gemma 3 report (`gemmateam2025gemma3`); Falcon 3 has no paper,
  so its model card (`tii2024falcon3`); HINT model → arXiv 2503.00031 (`huang2025efficient`); its base model,
  DeepSeek-R1 in Nature 2025 (`guo2025deepseekr1`), only if named.
- [x] Hallucination survey, ACM TOIS 2025 (`huang2025survey`), optional.
- [x] Not carried over: the course version's citations of the Transformer and Qwen2.5 papers as support for the design intuition.

---

## H. Before publishing

Rigor:
- [ ] Every design choice is said to be made on the 50-question dev subset; headline numbers come from the held-out set (R2).
- [ ] No "significant" without a test; no claim from a difference inside the noise (C3).
- [ ] Every number matches its source (`report_check.py --sources ../results/experiments`, then by hand).
- [ ] Open-ended scorer stated (R5).
- [ ] No code names in the text; terms as in part B.
- [ ] The proposition and the A/k + Bk model from the course version are dropped, or kept only as a labelled hypothesis.

Reproducibility:
- [ ] The appendix commands reproduce the reported numbers from a clean clone at the stated commit.

Presentation:
- [ ] Figures are vector (TikZ / pgfplots / exported PDF).
- [ ] Three decimals for MC scores everywhere; latency in ms per step with one decimal.
- [ ] No `\todo` / `\verify` left.
