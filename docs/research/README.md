# Research-driven iteration loop

> Purpose: capture the **methodology** behind the Q1–Q17 research files in this folder — how questions were formed, narrowed via follow-ups, and translated into shipped code. The Q-files are the *raw evidence*; this README is the *story* of how they were used and why the loop matters for the final Kaggle writeup.

## TL;DR

Phases 1–10 of Rytmi were built mostly from listening passes + DSP intuition: pick a heuristic, tune the threshold, listen to outputs, re-tune. Around Phase 10 several thresholds (vocal-activity gate, downbeat confidence cutoff, "instrumental" detection) had been hand-tuned three or four times each and were still wrong on specific eval tracks. The fix wasn't more tuning — it was **finding out whether the literature already had a recipe**.

That turned the build loop from:

```
notebook listen → pick threshold → code AI implements → notebook listen → repeat
```

into:

```
notebook listen → identify failure mode → code AI helps form research question
              → Perplexity → narrow with follow-ups
              → code AI translates recipe to drop-in change
              → eval-set re-run → ship
```

Phase 11 (commits `953a12b`, `aa06670`, `d4edb83`, `b8597fe`) is the first full run of this loop. Four heuristic thresholds got replaced by published recipes: **`mean − 18 dB`** vocal threshold (Q5 → Ricci et al. 2025), **BeatNet** as dominant downbeat signal (Q1 → Heydari et al. 2021), Gemma E4B **speech-vs-singing prompt** (Q7), and a **regex grounding verifier** on Gemma section output (Q11). Five eval tracks moved above the `0.25` downbeat-confidence gate where Phase 10's hand-tuning lifted zero. Full per-phase write-up: [`../experiments/17-2026-04-18-phase-11-validated-upgrades.md`](../experiments/17-2026-04-18-phase-11-validated-upgrades.md).

## The loop, end to end

### 1. Failure-mode triage from a listening pass

After each phase ships, a notebook listening pass produces a list of "this still sounds wrong" notes — usually anchored to specific eval tracks and timestamps. Examples that fed Phase 11:

- *"Baila Kizomba Amor's ~194 s passage is clearly instrumental but renders as `main`"* — a vocal-activity false negative.
- *"None of the 10 eval tracks ever clears the `0.25` downbeat-confidence gate, so Phase 7's re-anchoring is dead infrastructure"* — a confidence-metric calibration question.
- *"Propuesta Indecente P1–P8 is spoken dialog but the prompt treats it as singable intro"* — a missing label class.
- *"Gemma sometimes ignores the `cite a number` rule in `QUESTION_SECTIONS` output"* — a verifier-vs-prompt-only gap.

These four notes shaped the four research questions for the phase.

### 2. Question formation with the code-AI

Code-AI helps turn a vague failure ("vocal threshold is wrong on Baila") into a question Perplexity can usefully answer. The forms that worked best across Q1–Q17:

| Pattern | Example | Why it works |
|---|---|---|
| **Concrete-recipe ask** | "On a Demucs vocal stem, what published RMS or dB-below-stem-mean threshold is used to classify frames as vocal-present? Cite the paper that specifies the threshold, hysteresis, and smoothing window — not just reported accuracy." (Q5 FU-5a) | Forces a citation, not a survey. Output is directly translatable to code. |
| **Drop-in lib ask** | "What is the maintenance status, Python package availability, and install/dependency situation of BeatNet, madmom, Böck-TCN as of 2026? Which install cleanly with recent librosa and PyTorch?" (Q1 FU-1d) | Filters out research-only systems before we sink time on a wrapper. |
| **Failure-mode ask** | "What does Whisper-AT cost on CPU for 3–5 minute popular-music tracks at 1 s tagging resolution?" (Q7 FU-7a) | Surfaces deal-breakers (10–30 min/track CPU = unusable in batch flow) before the implementation phase. |
| **Comparison ask** | "Compare Demucs v4 / Spleeter / OpenUnmix / HTDemucs as vocal-stem sources for downstream vocal-activity classification — robustness on latin styles, CPU/GPU cost." (Q6) | Cheap way to confirm we're not on a stale or genre-mismatched tool. |
| **Genre-prior ask** | "Where does the `1` typically sit relative to kick, bass, and melodic accents in kizomba / bachata? Any published analyses of snare-on-2-and-4 vs. bachata-güira patterns?" (Q4) | Acknowledges the dataset gap (no labelled bachata/kizomba MIR corpus exists) and asks for the next-best evidence: ethnomusicology priors. |

Bad question patterns we learned to avoid: "what's the best way to detect breaks" (too broad — produces a survey), "is BeatNet good" (yes/no — produces hedging). Good questions name the failure mode, the specific input, and the form of evidence we want back.

### 3. Initial Q + targeted follow-ups

Each top-level Q is usually a survey of the field; the *follow-ups inside the same file* (the "FU" labels in Phase-11 docs) are where the Q gets useful. The pattern repeats across files:

- **Q1** opens with "state-of-the-art downbeat methods 2020–2026" (a literature review). Follow-ups narrow to *(a)* a maintained PyPI package, *(b)* genre accent templates as fusion ingredient, *(c)* fusion strategies for combining a neural tracker with a DSP heuristic. Result: BeatNet + rank-fusion recipe.
- **Q5** opens with "feature sets and thresholds for instrumental-section detection" (broad). Follow-up FU-5a asks specifically for the published *number* on a Demucs vocal stem, with the citation. Result: `mean − 18 dB`, 3 s moving average, binarise at 0.5.
- **Q7** opens with "speech-vs-singing discrimination" (broad). FU-7a checks Whisper-AT feasibility (rejected — too slow). FU-7b asks for validated prompt formulations for small multimodal LLMs on this binary task. Result: the YES/NO prompt that ships in [vocal_activity.py](../../src/rytmi/vocal_activity.py).
- **Q11** opens with "techniques for constraining LLMs to produce data-grounded explanations". FU-11b asks specifically for verifier-prompt templates with regex-style enforcement. Result: the post-generation regex verifier in [prompts.py](../../src/rytmi/prompts.py).

The discipline: *don't act on the top-level Q answer*. Always run at least one follow-up that asks for a citation, a package, or a number we can paste into code. The top-level Q answers are too survey-shaped to ship from.

### 4. Code-AI translates recipe to drop-in change

Once a follow-up returns something concrete, code-AI (this loop's other half) does the integration:

- Identifies the existing call site that owns the heuristic ([`DemucsVocalActivity._threshold()`](../../src/rytmi/vocal_activity.py), [`detect_downbeats()`](../../src/rytmi/dsp.py), etc.).
- Preserves cache/config compatibility where possible — the Phase-11a vocal-RMS change kept the expensive Demucs RMS in the `.npz` cache and only re-derived the cheap binary `active` mask, so the eval set didn't need a full re-separation pass.
- Writes the failure-mode test *first* (e.g., `test_demucs_threshold_uses_mean_minus_18db` against synthetic input), then the change, then the regression tests.
- Logs the citation in the experiment note so the rationale survives the next code refactor.

### 5. Eval-set re-run, ship, write the experiment note

The 10-track eval set ([`../eval-set-guide.md`](../eval-set-guide.md)) is the unit of validation. A research-driven change is shippable when the per-track before/after table shows a real lift on at least one target track and no regression elsewhere. Phase 11's table:

| Track | Phase 10 conf | Phase 11 conf |
|---|---|---|
| Bachata Musicality | 0.10 | **0.33** |
| Charbel E Magia *Ben Ana* | 0.19 | **0.34** |
| Charbel E Magia *Official* | 0.04 | **0.35** |
| Romeo Santos *El Chaval* | 0.04 | **0.33** |
| Emborrachare | 0.21 | **0.28** |

Five tracks above the gate where Phase 10 had zero — that's the kind of evidence the experiment note can stand on. Without the loop, we'd still be tuning kick-band weights by hand.

## When the loop *doesn't* produce a recipe

Roughly half the Q-files end with "no published threshold exists for this" or "the only fix needs a new dataset". Those outcomes are still useful:

- **Q14** asked for absolute thresholds on spectral centroid / roll-off / RMS for "mellow / chill / intense" vocal sub-sections. Answer: no fixed thresholds exist; published work uses per-track z-scores and trains a classifier on the relative space. **Decision:** deferred to Phase 12 — the work needed is its own eval pass + per-track calibration, not a one-line constant change.
- **Q7 FU-7a** confirmed Whisper-AT is 10–30 min/track on CPU. **Decision:** skipped entirely; reuse the in-memory Gemma E4B for the YES/NO speech question instead.
- **Q1 FU-1b** described bachata/kizomba accent templates conceptually but no MIR-ready lexicon exists. **Decision:** encoded conceptually in the experiment note, not shipped as a standalone fusion signal — weaker evidence than BeatNet, would be a Phase-12 third fusion ingredient if BeatNet under-performs on a specific style.
- **Q8** (latin-music section-labelling corpora) and **Q16** (inter-annotator agreement on listener-subjective labels) confirmed no bachata/kizomba labelled corpus exists, so our 10-track curated eval set *is* the eval set. **Decision:** keep listening-pass + eval-set regression-table as the validation method; don't wait for a corpus.

A "no" from Perplexity is a permission slip to defer or skip — and it's faster than discovering the same dead-end through code.

## Mapping research → shipped code

| Research file | Shipped in | Concrete change |
|---|---|---|
| [`Q1*`](./Q1.%20What%20state-of-the-art%20methods%20%282020–2026%29%20estimate.md) | Phase 11b | BeatNet as dominant downbeat signal in `detect_downbeats()` rank fusion |
| [`Q5*`](./Q5.%20Published%20feature%20sets%20and%20thresholds%20for%20dete.md) | Phase 11a | `mean − 18 dB` vocal-activity threshold + 3 s smoothing in `DemucsVocalActivity._threshold()` |
| [`Q7*`](./Q7.%20Speech-vs-singing%20discrimination%20for%20distingui.md) | Phase 11c | `GemmaSpeechDetector` + `_GEMMA_SPEECH_VS_SINGING_PROMPT` + `_relabel_spoken_intro` pass |
| [`Q11*`](./Q11.%20Techniques%20for%20constraining%20LLMs%20to%20produce%20d.md) | Phase 11d | `_NUMERIC_ANCHOR_RE` + `verify_sections_output()` + `explain_all(verify_sections=True)` |
| [`Q14*`](./Q14.%20Features%20for%20_mellow%20_%20chill%20_%20intense_%20vocal.md) | (deferred → Phase 12) | per-track z-scores for vocal character bins |
| [`Q1 FU-1b`](./Q1.%20What%20state-of-the-art%20methods%20%282020–2026%29%20estimate.md) | (deferred → Phase 12) | bachata/kizomba accent templates as third fusion signal |
| [`Q4`](./Q4.%20Musicological%20priors%20for%20kizomba%20_%20bachata_%20wh.md), [`Q6`](./Q6.%20Comparison%20of%20Demucs%20v4%20_%20Spleeter%20_%20OpenUnmix.md), [`Q8`](./Q8.%20Datasets%20and%20evaluation%20methodologies%20for%20sect.md) | (informed earlier phases) | confirmed Demucs v4 choice, kizomba `1`-on-kick prior, no labelled corpus available |
| [`Q12`](./Q12.%20Evaluation%20methodologies%20for%20the%20distinctiven.md), [`Q16`](./Q16.%20How%20do%20MIR%20evaluation%20sets%20handle%20the%20_ground.md), [`Q17`](./Q17.%20Minimum%20eval-set%20size%20for%20statistically%20meani.md) | (validated approach) | confirmed 10-track curated eval is methodologically defensible; no rush to expand to 100+ |

## How to add a new research thread

1. **In the experiment note for the in-flight phase**, add a "Research questions raised" subsection that lists the failure modes you can't fix from listening alone.
2. **Form the question** following the patterns in §2 above. Bias toward concrete-recipe / drop-in-lib / failure-mode forms.
3. **Run Perplexity (or equivalent)**. Save the full conversation — both the top-level Q and every follow-up — as `docs/research/Q<n>. <slug>.md` (Perplexity exports cleanly via copy-paste; keep its citation footnotes intact).
4. **Always run at least one follow-up** that narrows to a citation, a package, or a number. If you can't get one, the evidence isn't shippable yet — note the gap and defer.
5. **In the experiment note**, add a row to the "Validated by research" table mapping the Q + FU number to the concrete recipe and the file that consumes it.
6. **In this README's "Mapping research → shipped code" table**, add a row for the new Q.

## Why this matters for the Kaggle writeup

The competition asks for a working Gemma-4 demo, but the *story* of how a small project converged on the right heuristics is what makes it credible. The research loop turns "we hand-tuned a threshold" into "we found the published recipe and verified it on our eval set" — which is the claim the judges and downstream readers can act on.

Concretely for the writeup:
- The five-track downbeat lift in Phase 11 is the demo-facing headline.
- The four heuristic-to-recipe substitutions (vocal RMS, BeatNet, speech-vs-singing prompt, regex verifier) are the methodology section.
- The deferred items (Q14 vocal character, Q1 FU-1b accent templates, Whisper-AT) are the honest-limitations section — and they're more credible *because* the research file shows exactly why we deferred them.

The Q-files in this folder are the raw artefacts; this README and the per-phase experiment notes are the curated story on top.
