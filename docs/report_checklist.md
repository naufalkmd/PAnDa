# Report checklist: empirical study of scoring rules on multiple-choice TruthfulQA

Status and open items for the report. The report is `paper/report.tex` (figures in `paper/figures/`;
build with `latexmk -pdf -outdir=build report.tex` from `paper/`, PDF in `paper/build/`). In the PDF, red
`[TODO]` marks a missing value and red `[verify]` a statement from an older run. `[x]` done, `[ ]` open.
The June 2026 course version is kept at the git tag `pre-cleanup-2026-11` (`paper/course_version_2026_06/`).

Last updated: 2026-11-15.

---

## A. Format and purpose

- [x] Purpose: portfolio piece (public, linked from the repository). Not a course submission, so no course AI rule
  applies; Claude drafts, the authors revise. An AI-use note is optional.
- [x] arXiv style, `article`, one column, no page limit (aim: 10–12 pages plus appendix).
- [x] Authors: Muhammad Naufal, Jeong Edon, Muhammad Aliff (Korea University). [ ] Co-authors review before publishing.
- [x] Framing (2026-11-15): **empirical study**, not a method paper (outline in part C).
- [x] Title (decided 2026-11-15): "What Multiple-Choice TruthfulQA Rewards: Layer Contrast, Self-Evaluation and
  Option Length in Small Language Models". Considered and not taken: "What Does Multiple-Choice TruthfulQA Reward? A
  Held-Out Study of Scoring Rules in Small Language Models" (shorter, but drops DoLa and self-evaluation).
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

## C. Outline (empirical study, decided 2026-11-15)

**Framing.** The contribution is measurements, not a new method. Per-question DoLa-static is one of the scoring
rules studied and is reported with its held-out result. No "we propose", no "novel". The earlier method-paper
outline is in the git history.

**Title** (decided 2026-11-15, part A): "What Multiple-Choice TruthfulQA Rewards: Layer Contrast,
Self-Evaluation and Option Length in Small Language Models".

**Challenges** (here: what makes the measurement hard; each result section answers one):

- **C1. Small development sets mislead.** Per-question DoLa-static − base likelihood, MC1: +0.060 on the 50
  development questions, −0.034 [−0.060, −0.008] on the 767 held-out questions (exp19).
- **C2. Settings copied from generation break multiple-choice scoring.** Under DoLa's generation settings the
  plausibility constraint masks at least one token of every option (100 % of 5,529 held-out options); on the 54.8 %
  of questions where the true option has more masked tokens, DoLa's MC1 is 0.0 (exp19, mask section).
- **C3. Option scores follow option length.** DoLa's multiple-choice configuration has a within-question rank
  correlation of +0.669 with option length; choosing the longest option gives MC1 0.361, DoLa 0.356 (held-out).
- **C4. The benchmark can be answered without the question.** The self-evaluation verdict with the question
  removed is at least as accurate as with it on 6 of 8 models (exp20).

**Contributions** (plain statements, each with its section):

1. A held-out re-evaluation (767 questions) of DoLa in two configurations and of per-question DoLa-static, whose
   design was made on 50 questions: no layer-contrast rule beats the base model's likelihood on MC1 (§5).
2. Two mechanisms behind multiple-choice gains and losses of layer contrast: token masking by the plausibility
   constraint and the correlation with option length (§6).
3. Self-evaluation, P(True), against likelihood and DoLa under a design frozen before 400 confirmation questions:
   +0.225 MC1 over DoLa, and accuracy 0.900 when answering the 30 % most confident questions (§7).
4. Controls on eight models: the early-exit reading of the verdict helps on 2 of 8, and the verdict works as well
   without the question; prior correction by the question-free verdict loses on 7 of 7 (§8).
5. Checks we recommend for multiple-choice TruthfulQA evaluations: a longest-option baseline, length-matched
   pairwise accuracy, a question-removed control, and a frozen design tested on held-out questions (§9).

| § | Section | Holds | Pages | Source |
|---|---|---|---|---|
| — | Abstract | Setting; C1–C4 as findings with their numbers; the recommendation | 0.3 | below |
| 1 | Introduction | Decoding-time truthfulness methods and how they are evaluated; C1–C4, each with its fact; contributions list | 1 | as above |
| 2 | Related work | Contrastive and layer-contrastive decoding; TruthfulQA and its known weaknesses (option heuristics, binary version); partial-input baselines (hypothesis-only NLI, MCQA without the question); self-evaluation and its uses (selection, abstention, beam search, probes); reading intermediate layers; selective prediction. How this report differs from each group | 1.5 | part G |
| 3 | Scoring rules | One `\paragraph` each: base likelihood (sum, per token); DoLa, generation settings and multiple-choice configuration; per-question DoLa-static (DoLa with four changes, in brief); self-evaluation; early exit of the verdict; the question-removed verdict. Figure F1 | 1.5 | code; exp19/exp20 READMEs |
| 4 | Experimental setup | TruthfulQA MC (817 questions); the question sets and what each decided (F2); MC1/MC2/MC3 and length-matched pairwise accuracy; tests (paired bootstrap, exact McNemar, Holm); the eight models and the inclusion rule (Llama 3.2 gated, not used); prompts (not the 6-shot prompt: absolute scores not comparable with published ones); hardware, run times, environment check (development questions reproduce the June runs within 2 questions per decoder) | 1.5 | run metadata; `heldout_analysis.py` check/repro |
| 5 | Layer contrast on held-out questions (C1) | T1 main; T2 factorial; T3 selection interval; F3 development vs held-out | 1.5 | exp19 |
| 6 | Why multiple-choice scores mislead (C2, C3) | T4 masking; T5 length (rank correlation, longest option, length-matched pairs); contrast-weight sweep chosen on the development set (β = 10) equals DoLa on held-out | 1 | exp19 |
| 7 | Self-evaluation (frozen design) | T6 scores, T7 paired differences, T8 selective prediction, F4 risk–coverage | 1.5 | exp20 run_02 |
| 8 | Controls on eight models (C4) | T9 early exit; T10 question removed and prior correction (rejected); the sum, reported only; T11 self-evaluation vs base likelihood (5 of 8 models); F5 MC1 by block | 1.5 | exp20 cross_model, exp21 |
| 9 | Discussion | What the benchmark measures; the recommended checks; what our results do and do not show about truthfulness | 0.7 | — |
| 10 | Limitations | One benchmark, multiple choice only; ≤ 4B models; non-standard prompt; DoLa on Qwen2.5-3B only (likelihood on all eight, exp21); confirmation questions scored for Qwen2.5-3B only; likelihood and DoLa scores seen on all held-out questions before the exp20 split; candidate layers untuned; two wordings | 0.5 | — |
| 11 | Conclusion and future work | Findings in order of strength; future work: (a) apply the checks to more decoding methods; (b) self-evaluation where the question is needed (open-ended generation, binary-choice TruthfulQA, short-answer QA) | 0.4 | — |
| A | Appendix | Reproduction (commit, commands, run times); development-set history (exp1–exp13, switching rules, one compact table); selection interval on five random subsets (exp16); MC1 by block for all models and both wordings; prompts verbatim | 3 | exp1–exp16, exp20 |

Left out of the report: PAnDa (dropped method), open-ended generation (exp14/exp15/exp17: labels written by an
LLM, and out of the study's scope), exp18 (50 questions only, and the Gemma final-norm issue below).

**Figures** (TikZ / pgfplots from the results files, never generated images):

- F1. Three ways to score one option: likelihood of the option tokens; contrast of a mature and a premature layer;
  the verdict token after "Is the proposed answer true?". TikZ.
- F2. The question sets: 50 development (exp1–exp18 design), 767 held-out (exp19), 417 exploration / 400
  confirmation (exp20 design and test), with an arrow from each set to the decisions made on it. TikZ.
- F3. MC1 per rule on development vs held-out questions, with 95 % intervals. pgfplots, exp19.
- F4. Risk–coverage curve of self-evaluation on the confirmation questions, with the three frozen thresholds
  marked. pgfplots; needs the curve written by the analysis (open item).
- F5. MC1 by block for the eight models, final block = 1.0 depth. pgfplots, `early_exit_by_block.csv`.

Status (2026-11-15): all five drawn in `paper/figures/f*.tex`, shared style `paper/figures/figstyle.tex` (loaded in
the report preamble). Their data are `paper/figures/data/*.csv`, written by `scripts/figure_data.py` from the results
files (rerun it after any results change; never edit the CSVs by hand). F3 adds 95 % bootstrap intervals of the mean
(10,000 resamples, seed 0). F4 adds base likelihood and DoLa (MC configuration) on the same 400 questions as
reference lines; F5 adds each model's base likelihood (exp21). Captions are still to be written with the sections.

---

## D. Where the numbers come from

Rule: **one run per table.** Never mix rows from different runs (the course version did; see the experiment log, issue 1).

| Report table / figure | Source file(s) | Status |
|---|---|---|
| T1 main: base likelihood, DoLa (two configurations), per-question DoLa-static; development and held-out columns | exp19 `run_01_qwen25_3b_full` via `scripts/heldout_analysis.py` (scores) and `scripts/paired_tests.py --exclude-questions-of ... --holm` | [x] `exp19.../run_01_qwen25_3b_full/analysis/heldout_main.csv`, `scores_by_split.csv` |
| T2 factorial | exp19, decoders `exp13_*`; the two no-constraint cells are identical by construction | [x] `analysis/heldout_factorial.csv` |
| T3 selection interval | exp19, `fanda_update1/4`, `fanda_frozen` (held-out); exp16 runs 01–06 (appendix) | [x] `analysis/heldout_interval.csv`; [ ] exp16 summary for the appendix |
| F3 development vs held-out | exp19 per-question scores via `scripts/figure_data.py` → `paper/figures/data/f3_dev_vs_heldout.csv` | [x] with 95 % intervals |
| T4 masking | `heldout_analysis.py`, mask section | [x] |
| T5 length | `analysis/length_association.csv`, `length_control.csv` (section 7 of `heldout_analysis.py`) | [x] use the character-length baseline (token counts tie; see the experiment log, issue 9) |
| Contrast-weight sweep | `heldout_analysis.py`, beta section | [x] |
| T6–T8 self-evaluation | exp20 `run_02_qwen25_3b_confirmation/analysis/*.csv` | [x] |
| F4 risk–coverage | exp20 `run_02.../analysis/selective_prediction_curve.csv` | [x] |
| T9, F5 early exit | exp20 `cross_model/early_exit_selection.csv`, `early_exit_by_block.csv` | [x] |
| T10 question removed | exp20 `cross_model/prior_correction.csv` | [x] |
| T11 self-evaluation vs likelihood, eight models (§8) | exp20 `cross_model/self_evaluation_vs_likelihood.csv` (exp21 scores) | [x] |
| Pipeline / scoring figure F1, split figure F2 | TikZ, drawn from the code (`src/truthfulqa_scoring/prompts.py`, `local_evaluator.py`, exp20 README) and `split.json` | [x] `paper/figures/f1_scoring.tex`, `f2_question_sets.tex` |

---

## E. Runs and open items before drafting

Done:
- [x] R1: exp16 seeds 202, 303, 404 and seed 101 under the current code (runs 03–06).
- [x] R2: exp19 on all 817 questions, Qwen2.5-3B (`run_01_qwen25_3b_full`).
- [x] exp20: self-evaluation, design frozen on 417 exploration questions (`frozen_design.json`), tested once on
  400 confirmation questions; cross-model early exit and question-removed control on eight models.

No longer needed under the empirical framing: R3 (isolating τ: per-question DoLa-static shows no held-out gain to
attribute), R4 (exp19 on Gemma), R5 (open-ended labels: exp14 is left out).

Open (no GPU unless noted):
- [x] Held-out paired tests saved in `exp19.../run_01_qwen25_3b_full/analysis/`.
- [x] Length control is section 7 of `scripts/heldout_analysis.py`.
- [x] Risk–coverage curve for F4.
- [x] Experiment log (exp19 held-out, exp20, exp21) and glossary updated.
- [x] R6 = exp21 (2026-11-15, 70 min): base-model likelihood on all 817 questions for the eight exp20 models; compared
  with self-evaluation by `scripts/self_evaluation_vs_likelihood.py` (protocol fixed before scoring:
  `exp20.../cross_model/likelihood_protocol.json`). Reproduces exp19 exactly. Self-evaluation beats both likelihood
  rules on 5 of 8 models; two of the five only just (no multiple-comparison adjustment in the protocol: say so).
- [ ] exp18 / Gemma: `apply_final_norm` does not find the final norm of `Gemma3ForConditionalGeneration`
  (transformers 4.57.6), so exp18's Gemma DoLa rows may read premature layers without the norm. exp18 is left out;
  check before any Gemma DoLa number is used.

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
  the best false option (MC2 option set), as in DoLa's evaluation (`src/truthfulqa_scoring/evaluation.py`).

## Draft status

- [x] §2 Related work and §3 Method drafted (2026-11-14). Method facts checked in the code: early exit = final norm +
  output head on each block's hidden state; DoLa's divergence as in its reference implementation,
  ½[KL(m‖q_N) + KL(m‖q_j)] (mixture first, checked in the DoLa repository); per-question DoLa-static uses the standard JSD at τ = 0.5; the
  −1000 mask value and its effect on option scores. PAnDa removed from §2/§3 (dropped method).
- [x] §2 Related work and §3 Scoring rules rewritten for the empirical framing (2026-11-15). §2: six groups, each
  with how this report differs. §3: base likelihood (sum, per token), DoLa in both configurations, per-question
  DoLa-static (four changes, renormalised option score checked in `local_evaluator.py`), self-evaluation, early exit,
  question removed (prompt from `exp20.../run_experiment.py`), longest option, selective prediction; Figure F1.
  The other sections are placeholders in the outline's order. The section numbers in part C now match the `.tex`.
- [ ] Decide on the appendix "When a longer selection interval changes nothing" (not in the outline; keep only if
  §5 discusses the interval).
- [x] §4 Setup drafted (2026-11-15): data, question sets with F2, metrics, tests, models and inclusion rule, prompts,
  implementation. Facts from run metadata, `requirements.txt`, exp20 `protocol.json`, `development_reproduction.csv`.
- [x] Checked in the DoLa paper (arXiv 2309.03883v2, §3.2): MC1/MC2/MC3 reported; TruthfulQA run with the default
  QA prompt; the text says the constraint is used in MC with −1000 in place of −∞, while the released
  `tfqa_mc_eval.py` defaults to `relative_top = 0.0` (no constraint) and the README commands keep it. §3 states both
  and that we follow the script. This strengthens C2: the paper's description and its code disagree.
- [x] Checked in the TruthfulQA paper: its MC score is the normalised likelihood of the true answers (= MC2); the
  names MC1/MC3 are not in it. §4 attributes only MC2 to it. Bib comments updated.
- [ ] Uncited entries from the method framing (`holtzman2020curious`, `huang2025efficient`, `guo2025deepseekr1`,
  `huang2025survey`): cite in the appendix's development history or remove.
- [x] §5–§8 drafted with T1–T11 (2026-11-15). Tables are generated by `scripts/report_tables.py` into
  `paper/tables/*.tex` from the results CSVs (rerun it after any analysis change; never edit the .tex tables by
  hand); each is capped at the text width with `adjustbox`. The check script traced all 107 numbers in text and
  tables. Figure captions F3–F5 written.
- [x] T2, T3, T9, T10 moved to Appendix B (2026-11-15).
- [x] Full draft (2026-11-15): abstract, §1 (C1–C4 with one fact each, contributions 1–5), §9 (what the scores
  measure; four recommended checks; what the results do not show), §10, §11, Appendix A (reproduction), B
  (tables), C (development history with T12 from exp16), D (selection-interval bound). Prompts are verbatim in §3/§4,
  so no separate prompt appendix. `huang2025efficient` and `guo2025deepseekr1` removed from the bib (exp18 left
  out); `holtzman2020curious` cited in Appendix C, `huang2025survey` in §1. Check script: 0 FAIL; 136 numbers
  traced; all 26 citations resolve.
- [x] Repository URL in Appendix A (2026-11-15; `reorganise-report` merged into `main` as PR #1). Appendix A names
  the tag `v1.0-report` for the version described.
- [x] Tag `v1.0-report` (2026-11-15): on `main` after the citation update, pushed to GitHub. Appendix A cites it.
  A later change to the report needs a new tag (`v1.1-report`, ...) and the matching line in Appendix A.
- [x] Length: body runs to p. 16 (references from p. 16, appendix pp. 19–21). Kept at this length (user's decision,
  2026-11-15); the 10–12 page target in part C no longer applies.
- [x] Title (part A), kept 2026-11-15.
- [x] Refocused after the authors' read (2026-11-15): no development history in the report. Removed Appendix C
  (development history, Table 12), Appendix D (selection-interval bound), the selection-interval paragraph of §5 and
  its table (T3), the k-variants sentence of §3, and the project story at the start of §1 (now a neutral sentence on
  why per-question DoLa-static is the test case for C1). `holtzman2020curious` removed from the bib. Tag
  `dev-history-2026-11` (on b686fd8) keeps that version, exp16, `docs/algorithms/` and `scripts/run_report_reruns.sh`,
  which were removed from the tree. Push the tag with the branch.
- [x] A final read by the first author (2026-11-15), which led to the refocus above.
- [x] Repository cleanup (2026-11-15): exp1–exp10 and `results/dev/` moved to `results/experiments/exploration/`
  (`dev` → `sanity_runs`; runners use `parents[2]`, all nine `--list` checked; `summarise_runs.py` finds all 32
  runs); README, `results/experiments/README.md`, project `CLAUDE.md`, `pyproject.toml` description and
  `CITATION.cff` rewritten for the empirical framing.
- [x] Exploration folder removed from the tree (user's decision, 2026-11-15) after tagging the last commit that
  holds it: annotated tag `exploration-2026-06` (109 files). Appendix C, the experiment log, both READMEs, project
  `CLAUDE.md` and `docs/algorithms/` point to the tag. The tag must be pushed with the branch
  (`git push origin exploration-2026-06`), or the citation in Appendix C leads nowhere.
- [x] Second cleanup (user's decision, 2026-11-15): annotated tag `pre-cleanup-2026-11` (118 files), then removed
  exp14, exp15, exp17, exp18, `scripts/build_exp14_manual_eval_sheet.py`, `results/figures/`, `scripts/plots/`,
  `docs/presentation/`, the method notes in `docs/algorithms/` (kept `dola.md`, `greedy.md`) and
  `paper/course_version_2026_06/`. The two exp18 `launcher.log` files (git-ignored, not in the tag) were moved to
  the local `archive/exp18_launcher_logs/`. Push the tag with the branch.
- [x] `CITATION.cff` (2026-11-15): Jeong Edon and Muhammad Aliff added with their names as written in the report
  (not split into family and given names, at the user's request); version `1.0-report`; validated with `cffconvert`.
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


New for the empirical framing, verified 2026-11-15 and appended to `references.bib` (15 entries, from the venue's
own record where one exists: ACL Anthology .bib, NeurIPS proceedings .bib, PMLR, JMLR, OpenReview search, arXiv API).
All 28 entries compile with `plainnat` without BibTeX warnings.
- [x] Self-evaluation, P(True): Kadavath et al. 2022, arXiv only (`kadavath2022language`).
- [x] Self-evaluation for selective generation and abstention, on TruthfulQA and TL;DR: Ren et al., PMLR 239
  (ICBINB workshop at NeurIPS 2023) (`ren2023selfevaluation`).
- [x] Self-evaluation guided beam search: Xie et al., NeurIPS 2023 (`xie2023selfevaluation`; author names as in the
  NeurIPS record, which differs from arXiv on two of them).
- [x] Self-alignment for factuality: Zhang et al., ACL 2024 (`zhang2024selfalignment`). **Correction:** they do not use
  P(True) to choose the MC option. Self-evaluation scores label the model's own responses as DPO training data; their
  TruthfulQA MC accuracy still compares the answers' conditional probabilities; DoLa is one of their baselines. Cite
  it as "self-evaluation used to train", the contrast with this report being that we score the option with it.
- [x] Truthfulness probe on hidden states: Azaria and Mitchell, Findings of EMNLP 2023 (`azaria2023internal`).
- [x] Intermediate layers under false demonstrations: Halawi et al., ICLR 2024 spotlight (`halawi2024overthinking`).
- [x] MCQA with choices only: Balepur et al., ACL 2024 (`balepur2024artifacts`).
- [x] TruthfulQA weaknesses, cited as blog posts: Turner and Kurzeja 2025 (`turner2025gaming`; decision-tree
  heuristics, 79.6 % in theory; **says nothing about option length**, so do not cite it for C3); Evans, Chua and Lin
  2025 (`evans2025improved`; MC format may measure test-taking ability; binary-choice version recommended).
- [x] Hypothesis-only baselines in NLI: Gururangan et al., NAACL 2018 (`gururangan2018annotation`); Poliak et al.,
  *SEM 2018 (`poliak2018hypothesis`).
- [x] Selective prediction: El-Yaniv and Wiener, JMLR 2010, which names the risk–coverage trade-off
  (`elyaniv2010foundations`); Geifman and El-Yaniv, NeurIPS 2017 (`geifman2017selective`).
- [x] Model reports for the two exp20 models without one yet: Phi-3 report, arXiv 2404.14219 (`abdin2024phi3`);
  SmolLM2, arXiv 2502.02737 (`benallal2025smollm2`); both linked from the model cards. Gemma 3 1B and Qwen2.5-0.5B/1.5B
  are covered by the existing Gemma 3 and Qwen2.5 entries.
- [ ] Still to find, if §6 wants prior work on length: a published result on length bias in multiple-choice or
  likelihood scoring. None verified yet; without one, C3 is stated as our measurement only.

---

## H. Before publishing

Rigor:
- [ ] Every choice states its data: 50 development questions (exp1–exp18), 417 exploration questions (exp20 design);
  headline numbers come from the 767 held-out (exp19) and 400 confirmation (exp20) questions. Say that the
  likelihood and DoLa scores were seen on all held-out questions before the exp20 split.
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
