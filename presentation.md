## 1. Title
**PAnDa: Progress Toward Local Adaptive Contrastive Decoding**  
Subtitle: *From fixed contrast to block-local arbitration* [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/72329987/130b15d6-3272-4792-adfa-8e7758f58523/panda_note.pdf)

**What to say**
- Hallucination remains a core obstacle in factual LLM use. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/72329987/130b15d6-3272-4792-adfa-8e7758f58523/panda_note.pdf)
- This talk is a progress update on a decoding method, not a final result. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/72329987/130b15d6-3272-4792-adfa-8e7758f58523/panda_note.pdf)
- The key idea is to move adaptivity inside block-parallel decoding rather than reranking full responses. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/72329987/130b15d6-3272-4792-adfa-8e7758f58523/panda_note.pdf)

## 2. Motivation
**Why hallucination needs decoding-time control** [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/72329987/130b15d6-3272-4792-adfa-8e7758f58523/panda_note.pdf)

**Points**
- Inference-time decoding can improve truthfulness without retrieval or retraining. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/72329987/130b15d6-3272-4792-adfa-8e7758f58523/panda_note.pdf)
- Hallucination risk is not uniform across a generation. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/72329987/130b15d6-3272-4792-adfa-8e7758f58523/panda_note.pdf)
- That makes a single always-on decoding rule too rigid in many cases. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/72329987/130b15d6-3272-4792-adfa-8e7758f58523/panda_note.pdf)

## 3. Problem
**Greedy decoding and rigid contrast are not enough** [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/72329987/130b15d6-3272-4792-adfa-8e7758f58523/panda_note.pdf)

**Points**
- Greedy decoding is simple but weak for factual ranking. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/72329987/130b15d6-3272-4792-adfa-8e7758f58523/panda_note.pdf)
- Standard DoLa uses layer contrast, but the project found that fixed-contrast variants were more practical. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/72329987/130b15d6-3272-4792-adfa-8e7758f58523/panda_note.pdf)
- Response-level reranking is adaptive, but it is late and coarse because it only chooses between full candidates. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/72329987/130b15d6-3272-4792-adfa-8e7758f58523/panda_note.pdf)

## 4. Baseline
**DoLa as the starting point** [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/72329987/130b15d6-3272-4792-adfa-8e7758f58523/panda_note.pdf)

**Points**
- DoLa improves factuality by contrasting deeper and shallower layers. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/72329987/130b15d6-3272-4792-adfa-8e7758f58523/panda_note.pdf)
- Your project then simplified this into fixed-\(\alpha\) branches. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/72329987/130b15d6-3272-4792-adfa-8e7758f58523/panda_note.pdf)
- That changed the main question from “does contrast help?” to “how should adaptivity be reintroduced?” [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/72329987/130b15d6-3272-4792-adfa-8e7758f58523/panda_note.pdf)

## 5. Fixed-contrast finding
**Why fixed contrast became the key baseline** [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/72329987/130b15d6-3272-4792-adfa-8e7758f58523/panda_note.pdf)

**Points**
- In the sanity-10 TruthfulQA slice, weak contrast behaved almost like no contrast. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/72329987/130b15d6-3272-4792-adfa-8e7758f58523/panda_note.pdf)
- Stronger fixed contrast improved MC2 and MC3 substantially. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/72329987/130b15d6-3272-4792-adfa-8e7758f58523/panda_note.pdf)
- MC1 stayed flat across the rows, so the gain is mainly in truthful ranking, not top-1 selection. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/72329987/130b15d6-3272-4792-adfa-8e7758f58523/panda_note.pdf)

**Suggested numbers to show**
- Greedy: MC2 0.1045, MC3 0.0500. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/72329987/130b15d6-3272-4792-adfa-8e7758f58523/panda_note.pdf)
- DoLa-FixedAlpha (0.95): MC2 0.2023, MC3 0.1417. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/72329987/130b15d6-3272-4792-adfa-8e7758f58523/panda_note.pdf)

## 6. Method
**PAnDa: local arbitration inside the block** [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/72329987/130b15d6-3272-4792-adfa-8e7758f58523/panda_note.pdf)

**Points**
- PAnDa keeps two fixed contrast regimes inside each speculative block: low-\(\alpha\) safe and high-\(\alpha\) truth-seeking. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/72329987/130b15d6-3272-4792-adfa-8e7758f58523/panda_note.pdf)
- It detects the first meaningful disagreement point using token mismatch plus JSD thresholding. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/72329987/130b15d6-3272-4792-adfa-8e7758f58523/panda_note.pdf)
- From that point onward, it applies truth-biased local arbitration rather than choosing between full responses. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/72329987/130b15d6-3272-4792-adfa-8e7758f58523/panda_note.pdf)

## 7. Pipeline
**How the decoder works step by step** [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/72329987/130b15d6-3272-4792-adfa-8e7758f58523/panda_note.pdf)

**Flow**
1. Shared block forward pass. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/72329987/130b15d6-3272-4792-adfa-8e7758f58523/panda_note.pdf)
2. Build safe and truth-seeking contrastive views. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/72329987/130b15d6-3272-4792-adfa-8e7758f58523/panda_note.pdf)
3. Measure local disagreement. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/72329987/130b15d6-3272-4792-adfa-8e7758f58523/panda_note.pdf)
4. Find earliest divergence point. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/72329987/130b15d6-3272-4792-adfa-8e7758f58523/panda_note.pdf)
5. Apply arbitration only from that point onward. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/72329987/130b15d6-3272-4792-adfa-8e7758f58523/panda_note.pdf)
6. Commit stable prefix and refine again. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/72329987/130b15d6-3272-4792-adfa-8e7758f58523/panda_note.pdf)

**Speaker framing**
- The point is not global search. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/72329987/130b15d6-3272-4792-adfa-8e7758f58523/panda_note.pdf)
- The point is local, structured intervention inside a speculative block. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/72329987/130b15d6-3272-4792-adfa-8e7758f58523/panda_note.pdf)

## 8. Evaluation
**What we will measure** [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/72329987/130b15d6-3272-4792-adfa-8e7758f58523/panda_note.pdf)

**Metrics**
- MC1 for hard top-choice accuracy. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/72329987/130b15d6-3272-4792-adfa-8e7758f58523/panda_note.pdf)
- MC2 and MC3 for soft truthful ranking. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/72329987/130b15d6-3272-4792-adfa-8e7758f58523/panda_note.pdf)
- Latency to capture quality-cost tradeoff. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/72329987/130b15d6-3272-4792-adfa-8e7758f58523/panda_note.pdf)

**Dataset scope**
- Primary: TruthfulQA sanity-10 development slice. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/72329987/130b15d6-3272-4792-adfa-8e7758f58523/panda_note.pdf)
- Planned broader validation: larger TruthfulQA and HaluEval. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/72329987/130b15d6-3272-4792-adfa-8e7758f58523/panda_note.pdf)

## 9. Current findings
**What the current artifact suggests** [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/72329987/130b15d6-3272-4792-adfa-8e7758f58523/panda_note.pdf)

**Points**
- PAnDa is currently the strongest saved configuration on the development slice. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/72329987/130b15d6-3272-4792-adfa-8e7758f58523/panda_note.pdf)
- It improves MC2 to 0.2669 and MC3 to 0.1667 on that slice. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/72329987/130b15d6-3272-4792-adfa-8e7758f58523/panda_note.pdf)
- It is slower than the response-level alpha-switch reranker, so speed is not the current claim. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/72329987/130b15d6-3272-4792-adfa-8e7758f58523/panda_note.pdf)

**Interpretation**
- The current evidence supports a quality-latency tradeoff, not a speed win. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/72329987/130b15d6-3272-4792-adfa-8e7758f58523/panda_note.pdf)
- The mechanism looks promising, but the evidence is still from a small development run. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/72329987/130b15d6-3272-4792-adfa-8e7758f58523/panda_note.pdf)

## 10. Next steps
**Experiment plan going forward** [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/72329987/130b15d6-3272-4792-adfa-8e7758f58523/panda_note.pdf)

**Points**
- Keep the current settings fixed and scale TruthfulQA evaluation. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/72329987/130b15d6-3272-4792-adfa-8e7758f58523/panda_note.pdf)
- Add a held-out protocol where possible. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/72329987/130b15d6-3272-4792-adfa-8e7758f58523/panda_note.pdf)
- Run ablations on divergence threshold, truth-bias margin, block size, and commit efficiency. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/72329987/130b15d6-3272-4792-adfa-8e7758f58523/panda_note.pdf)
- Optimize refinement overhead so more truthfulness gain can be retained at lower runtime. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/72329987/130b15d6-3272-4792-adfa-8e7758f58523/panda_note.pdf)

## Good talk arc

A clean speaking arc is:

**hallucination problem → decoding-time opportunity → DoLa baseline → fixed-contrast breakthrough → PAnDa idea → local arbitration method → current results → future experiments**. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/72329987/130b15d6-3272-4792-adfa-8e7758f58523/panda_note.pdf)

## One-slide summary

If you need a single thesis sentence for the deck, use this:

**Fixed contrast is already a strong baseline; PAnDa explores whether adaptivity can be moved inside block-parallel decoding as local arbitration rather than full-response reranking.** [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/72329987/130b15d6-3272-4792-adfa-8e7758f58523/panda_note.pdf)

