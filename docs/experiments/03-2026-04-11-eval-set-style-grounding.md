# 2026-04-11 — Real-song eval set: grounding the STYLE question in social dance

## Goal
Evaluate Gemma's rhythm-learning outputs on the curated real-song eval set
(`data/songs/eval_set/bachata/`, `data/songs/eval_set/kizomba/`) and make one
focused, learner-valuable improvement based on observed failure patterns.

## Context / prior state
The eval set contains 7 tracks (3 bachata, 4 kizomba) analyzed via
`notebooks/05_batch_analysis.ipynb` using Ollama `gemma4:e4b` with the questions
`time_signature`, `style`, `dancer`.

Prior improvements already landed:
- Downbeat confidence end-to-end surfacing (see
  `2026-04-11-confidence-surfacing.md`).
- `QUESTION_STYLE` previously rewritten to ask for "dance-relevant terms" and
  forbid broad genre lists.
- `QUESTION_DANCER` compressed to a four-section 220-word budget.
- `explain_rhythm()` / `explain_all()` parameterized so generation settings can
  be tuned per call.

## Hypothesis
Inspecting the actual Gemma responses on the eval set will reveal concrete
failure modes that point at a single highest-value fix.

## Observed failure patterns

I read the saved outputs from cell 9 of the batch notebook. Across all 7 real
tracks:

### 1. STYLE is wrong on every single track (7/7)
Despite the prompt asking for "dance-relevant terms" and warning against
"broad generic genre lists", Gemma consistently produced:

| Track | Actual style | STYLE output |
|---|---|---|
| Romeo Santos — Canalla (bachata) | bachata | "Afrobeat, Funk, or EDM" |
| Grupo Extra — Me Emborrachare (bachata) | bachata | "funk, pop, or contemporary dance" |
| Romeo Santos — Propuesta Indecente (bachata) | bachata | "Funk, Disco, or Dance Pop" |
| All Of Me (kizomba) | kizomba | "Funk, Dance Pop, or Electronic" |
| Baila Kizomba Amor | kizomba | "deep house or funk" |
| Charbel — E Magia (kizomba) | kizomba | "Funk, R&B, or Hip-Hop" |
| Tony Pirata — Teu Toque (kizomba) | kizomba | "Pop, Funk, or general Dance music" |

Root cause: the prior prompt said "dance-relevant" but that's ambiguous
(could mean EDM/dance music), and it did not provide the vocabulary of
**social** dance styles. Gemma defaulted to its training-data prior — Funk /
Disco / Pop / EDM — which is exactly what the prompt was trying to prevent but
in practice did not.

### 2. STYLE contradicts DANCER on the same track
On the same track where STYLE said "Funk, Disco, Dance Pop", DANCER correctly
said "Bachata". The learner reads two sections that disagree, which undermines
trust in both.

### 3. DANCER drill section truncated on 6/7 tracks
The prompt asks for four sections ending in a `Drill` — the most actionable
part for a learner ("loop counts 1–8 and focus on X"). Only the Baila Kizomba
track had a complete four-section answer. Every other output was cut mid-
section (usually mid-"Phrase dynamics") at the default `max_new_tokens=1024`.
The Gemma E4B model writes long for this style of structured prompt.

### 4. DANCER style pick is weak in overlap BPM zones
- Romeo Santos 129 BPM (clearly bachata) → picked "Cha-cha". Both
  styles list 129 BPM in their range, and the prompt gives no tiebreaker.
- Tony Pirata 123 BPM (in `kizomba/` eval folder) → picked "Bachata". 123 is
  outside kizomba's 85-110, so the prompt as written can't pick kizomba.
- Baila Kizomba 144 BPM → picked "Merengue". 144 is also outside kizomba's
  range; probably urban kizomba / semba, which isn't in the style list.

### 5. Downbeat confidence is ambiguous (0.00–0.09) on ALL 7 real tracks
Every real track fell into the `< 0.15` "ambiguous" band. The thresholds were
calibrated on synthetic click tracks, not real music — real music onset
envelopes clearly don't give the mean-per-offset metric the contrast the
synthetic fixtures had. The uncertainty note now appears on every track, which
makes it boilerplate instead of signal.

## What changed

### `src/rytmi/prompts.py` — `QUESTION_STYLE`
Rewrote the STYLE question to be explicitly grounded in **social** dance
styles, with a concrete list, tempo ranges, rhythmic-feel cues, and an
explicit prohibition on falling back to generic genres. Key changes:

- Name the style set explicitly: bachata, kizomba, salsa, merengue, cha-cha,
  zouk. Each with its BPM range AND a short rhythmic-feel hint
  (e.g. "bachata: guitar with syncopated percussion", "kizomba: smooth
  half-time feel").
- Require the pick to be grounded in BOTH tempo AND onset density, because the
  eval set shows tempo alone is not enough (multiple tracks fell in overlap
  zones).
- Explicit fallback: if the data doesn't fit any listed style, say so — do NOT
  name funk/disco/pop/EDM/house/R&B. Previously the prompt said "too weak to
  support a specific style label" without naming the forbidden fallback
  categories, and Gemma went to them anyway.

This eliminates the STYLE↔DANCER contradiction by anchoring STYLE in the same
taxonomy DANCER already uses.

## Evidence / test results

```
$ .venv/bin/python -m pytest tests/test_llm.py tests/test_dsp.py -q
48 passed in 3.96s
```

Tests do not assert on the exact wording of `QUESTION_STYLE`, so no test
updates were needed. A live Gemma inference run on the eval set is the
remaining verification step (see Next step).

## What worked
- The concrete failure list above gives a clean prioritization — STYLE is the
  worst single failure (7/7) AND the easiest to fix (one prompt edit).
- Pinning the failure on "vocabulary, not intent" — the prior prompt DID tell
  Gemma not to list genres, and Gemma did it anyway — redirected the fix
  toward supplying the correct list rather than adding more prohibitions.
- Tying STYLE and DANCER to the same taxonomy is the smallest change that
  removes the "same track, two contradictory labels" failure without touching
  the DANCER prompt.

## What did not work / limitations

All fixes below are **deliberately out of scope** for this one-improvement
pass, but they are the next obvious targets:

- **DANCER drill truncation (6/7)** — unfixed. The drill is the most
  actionable section and it almost always gets cut. Fixing requires either
  bumping `max_new_tokens` in the notebook call (cheap, available via the
  already-parameterized `explain_rhythm` signature), or further compressing
  the DANCER prompt (harder — sections 1 and 2 alone consume most of the
  current budget because Gemma writes each step in a full sentence).
- **DANCER style disambiguation in BPM overlap zones** — unfixed. The fix
  would be a one-sentence addition to DANCER: "when tempo fits more than one
  style, use onset density as a tiebreaker — bachata and salsa are dense,
  kizomba and zouk are smooth and sparser". Same pattern as the STYLE fix.
- **Downbeat confidence thresholds are uncalibrated for real music** —
  unfixed. Every real track lands in the "ambiguous" band, which makes the
  uncertainty note boilerplate. The thresholds in `prompts.py` (0.15 / 0.35)
  were derived from synthetic fixtures and clearly don't match real-music
  distributions. This needs a calibration pass against the eval set once a
  few more tracks are labeled, or a rethink of the confidence metric itself
  (mean-per-offset may not be the right signal on dense real music).
- **Kizomba tracks at 123 and 144 BPM are outside the style list's
  85–110 range** — the list likely needs an "urban kizomba / semba" bracket
  for the 120–150 BPM zone, or the eval labels need checking.
- **Gemma has not been re-run with the new STYLE prompt yet** — this change
  is unverified on live inference. The prompt is consistent with what steered
  DANCER correctly on 4/7 tracks, so the expectation is it will work, but
  verification is the next step.

## Decision / takeaway
When a prompt's prohibition ("don't list generic genres") is being ignored by
the model, the fix is almost never another prohibition — it's supplying the
correct vocabulary the model should use instead. Gemma E4B in particular
defaults hard to its genre-label training prior unless pointed explicitly at a
different taxonomy.

The eval set also confirmed that `downbeat_confidence` thresholds calibrated
on synthetic signals do not transfer to real music — a calibration pass is
now a clear P1.

## Next step
1. Re-run the batch notebook on the eval set with the new `QUESTION_STYLE` and
   confirm that STYLE now names social dance styles (or explicitly declines to
   pick one), and that STYLE and DANCER agree on the same track.
2. Bump `max_new_tokens` in cell 9 for the DANCER question (now that
   `explain_rhythm` accepts it per call) so the drill section stops getting
   truncated; this is a one-line notebook edit.
3. Add onset-density tiebreaker language to `QUESTION_DANCER` for overlap BPM
   zones (129 BPM bachata vs cha-cha, 123 BPM bachata vs kizomba).
4. Collect `downbeat_confidence` values across the eval set and recalibrate
   the `0.15` / `0.35` thresholds, or replace the mean-per-offset metric with
   one that gives useful contrast on real music.
