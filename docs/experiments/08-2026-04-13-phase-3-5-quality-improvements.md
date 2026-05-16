# 08 — 2026-04-13 — Phase 3.5: merge phases, song arc, basic_step guardrails

## Goal
Improve the quality of section-aware LLM coaching based on reviewing real
notebook outputs from the 7-track eval set (3 bachata, 4 kizomba) after
Phase 3 (section-aware prompts, experiment 07).

Specific problems observed:
1. Too many repetitive "main" sections (14–16 per track, almost all labeled "main")
2. Wall-of-text section coaching with no visual breathing room
3. Bachata 8-count hallucinations (Gemma invented "3+3+2" or "1-2-3, 4-5-6, 7-8 hold" instead of the correct "1-2-3-tap(4), 5-6-7-tap(8)")
4. Missing high-level narrative — sections coaching jumped into detail without overview
5. Micro-segments from DSP (some <8 seconds)

## Context / prior state
Phase 3 (commit `eba8154`) added `detect_sections()`, per-section `RhythmFeatures`,
`QUESTION_SECTIONS`, and `_format_sections_block()`. The LLM received raw section
lists directly. A typical track produced 10–16 sections, mostly labeled "main",
and Gemma listed them one by one in the output — repetitive and unhelpful.

## Hypothesis
- Merging consecutive same-label sections into "phases" will reduce prompt noise and
  give Gemma a cleaner structure to reason about.
- A separate `QUESTION_SONG_ARC` will produce a useful high-level energy narrative.
- An explicit `basic_step` guardrail per style will prevent counting hallucinations.
- Raising `_MIN_SECTION_S` from 6→8 will eliminate micro-segments.
- Two-tier sections block (phase summary for user + section detail for Gemma) will
  let the model see detail while coaching at the phase level.

## What changed
- `types.py`: `SongPhase` dataclass, `basic_step` field on `StyleProfile`, `phases` on `RhythmAnalysis`
- `dsp.py`: `merge_adjacent_sections()`, `_average_rhythm_features()`, `_MIN_SECTION_S` 6→8
- `styles.py`: `basic_step` text for bachata, kizomba, semba
- `prompts.py`: two-tier `_format_sections_block()`, `QUESTION_SONG_ARC`, rewritten `QUESTION_SECTIONS`, `basic_step` rendering in style section
- `llm.py`: `explain_rhythm()` extracts and forwards phases + basic_step
- Notebook: added `song_arc` to QUESTIONS list
- Tests: 15 new tests (163 total passing)

Commit: `cb4efaf`

## Evidence / test results
Re-ran the full 7-track eval set through notebook 05. Key observations:

### What worked
- **Basic step guardrails effective.** All three bachata tracks now consistently
  describe "1-2-3-tap(4), 5-6-7-tap(8)". No more hallucinated groupings.
- **Song Arc adds real value.** Compact 3-4 sentence narratives like "begins softly...
  energy builds... peak moment... resolves" orient the dancer before section detail.
- **Phase grouping reduces noise.** Instead of listing 14 individual sections, Gemma
  groups them into ~3-5 coached blocks ("Phases 2–7: Early Main Groove").
- **Kizomba coaching is style-appropriate.** "Follow the bass line", "smooth walk-step",
  "intentional stillness during the break" — grounded in profile, not generic.
- **Half-time detection carries through.** Baila Kizomba (144 BPM detected) correctly
  references the 72 BPM half-time feel for kizomba.
- **Formatting improved.** Phase-level coaching with blank lines between items.

### What did not work / limitations
- **Downbeat confidence universally "ambiguous"** (0.00–0.09) across all 7 tracks.
  Known DSP limitation — not a regression. Future improvement target.
- **Raw sections still visible in metadata display.** The notebook `**Sections:**` line
  still dumps all raw section boundaries. Could collapse to phases for display.
- **Language detection quirk.** One track (Canalla / Romeo Santos) detected as "kriol"
  instead of Spanish. Minor transcription model issue.
- **Still many "main" segments.** Phase merging helps the prompt, but the underlying
  DSP novelty-curve segmentation produces mostly "main" labels for tracks without
  strong energy contrast. Better DSP labeling is a future direction.
- **Section coaching can still be long.** The 250-word limit in QUESTION_SECTIONS is
  sometimes exceeded. Model compliance with word limits is approximate.

## Key assumptions documented
1. **Learner knows their dance style.** The system accepts style as user input (or
   infers from folder structure). It does not auto-detect dance style from audio.
2. **Learner wants per-section coaching.** The phased coaching assumes the user will
   listen through the song and benefit from section-specific guidance.
3. **8-count phrasing is primary.** All current style profiles assume 4/4 time with
   8-count dancer phrases. 3/4 or 6/8 styles are not yet supported.
4. **DSP segmentation is energy-based.** Section labels are derived from spectral
   novelty curves and energy thresholds, not from music-theory structure (verse/chorus).

## Decision / takeaway
Phase 3.5 significantly improved coaching quality. The two-tier prompt approach
(phase summary + section detail) and style-specific guardrails are the right pattern
for keeping Gemma grounded while still producing useful output. The basic_step
constraint is essential — without it, the model hallucinated incorrect counting.

## Next step
Phase 4: section-aware visualization — add phase/section color bands and labels to
the interactive timeline so learners see the structure visually alongside the coaching.
