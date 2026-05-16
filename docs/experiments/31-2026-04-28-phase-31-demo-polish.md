# 2026-04-28 — Phase 31: Demo polish (bachata dancer rewrite + kizomba song arc)

## Goal

Two demo-quality fixes surfaced when running `notebooks/00_demo.ipynb` end-to-end:

1. The bachata `dancer` output read like a metrics report ("1.00 mean strength on beat 1, 2.5 onset density, 0.05 tempo stability") — the same problem Phase 29 already fixed for `kizomba_tutor`. The dancer prompt was the worst-looking part of the demo and would undermine the "Gemma as coach, not analyzer" story for any judge skim-reading.
2. The kizomba flow had per-phase tutor depth but no narrative layer — bachata gets a song arc that frames the per-phase coaching, kizomba did not.

Phase 31 applies the surgical Phase 29 pattern to `QUESTION_DANCER` and adds a kizomba song-arc cell to the demo. Phase 32 (kizomba section-drills) is anchored as the explicit follow-up but kept out of scope.

## Context / prior state

Phase 30 part 1 (`b1b1512`) shipped the demo notebook, README, and Kaggle writeup skeleton. Test suite was at 385 passed / 1 skipped. `QUESTION_DANCER` (lines 375–399 in `src/rytmi/prompts.py`) carried a numeric-anchoring rule (`assert "specific number" in QUESTION_DANCER.lower()`) but did not distinguish between *useful numbers* (BPM, timestamps) and *raw decimals* a learner does not need (beat strength values, accent arrays, onset density floats, percussiveness ratios, RMS ratios, tempo-stability decimals).

Sample bachata dancer output before this phase (Propuesta Indecente, 123 BPM):

```text
1) Tempo & feel. At 123 BPM, this track sits in the typical range for bachata.
   The 0.05 tempo stability ensures a very steady pulse for consistent footwork.

3) Phrase dynamics. With a 1.00 mean strength on beat 1, anchor your movement
   on the downbeat. Use the tap on counts 4 and 8 for hip accents, especially
   during the peak at 139.4s where the 2.5 onset density provides clear
   rhythmic cues.

4) Drill. Loop counts 1–8 of the bachata basic step. Focus on your hips landing
   exactly on the tap on count 4 to match the 123 BPM pulse.
```

The structure (4 sections, drill at the end) reads well. The metric narration does not.

## What changed

1. **`QUESTION_DANCER` rewrite** (`src/rytmi/prompts.py`):
   - Added a "Coach like a dance teacher, not like a metrics report" line.
   - Tightened the closing rule: every claim must tie to a **BPM, timestamp, count, or phrase length** — removed the previously-allowed "ratio, onset density, accent pattern" from the anchoring list.
   - Added explicit no-raw-decimals rule listing every offending decimal pattern (beat strength values, accent-pattern arrays, onset-density floats, percussiveness ratios, tempo-stability decimals, RMS ratios) with concrete examples; instructed the model to translate them into qualitative language ("very steady tempo", "comfortable mid-range", "lower percussion than a typical track").
   - Reworded the drill rule to require a section label and timestamp from the analysis (e.g. "During the main section starting at 65s, loop counts 1–8 of the bachata basic and focus on hips landing on count 4"), not just generic "match this tempo".
   - All changes are style-agnostic since `QUESTION_DANCER` is templated by `{style}`.

2. **Kizomba song-arc cell in `notebooks/00_demo.ipynb`**:
   - Inserted a markdown header + code cell between "What librosa heard" and "What Gemma teaches — one-pass kizomba tutor".
   - Code: `print(explain_rhythm(kiz, QUESTION_SONG_ARC, processor, model))`.
   - Narrative framing in the markdown explains that `QUESTION_SONG_ARC` is style-templated and never claims a downbeat, so it works for kizomba.

3. **`QUESTION_SONG_ARC` raw-decimals tightening** (added during the same phase after the live notebook 00 run):
   - Both the kizomba and bachata song-arc outputs leaked one raw decimal in the "distinguishes this track" sentence ("percussiveness of 0.22" / "0.16"). The pre-Phase-31 prompt invited it by allowing `"numeric anchor or structural feature... e.g. a specific timestamp, energy ratio, or the presence of an instrumental passage"` — `energy ratio` was the loophole.
   - Reworded the anchor rule to name only timestamps, BPM, and structural features (with concrete examples like "a long break from 15s to 38s", "a single high-energy peak at 139s", "a percussion-led intro").
   - Added the same explicit no-raw-decimals block used in the dancer rewrite — forbids percussiveness/RMS/onset-density/beat-clarity/tempo-stability decimals and accent-pattern arrays; requires qualitative translation ("drum-light feel", "melodic and harmonic content carries the rhythm").
   - This is the same surgical pattern Phase 29 applied to `QUESTION_KIZOMBA_TUTOR` — third application of the same fix shape, suggesting the metric-guard wording could be lifted into a shared helper if a fourth use case appears.

4. **Tests** (`tests/test_prompts.py`):
   - Existing `test_question_dancer_requires_numeric_anchoring` still passes (the "specific number" and "delete" rules survive in the dancer rewrite).
   - Added `test_question_dancer_hides_raw_decimals_from_final_answer` mirroring the Phase 29 metric-guard test (`test_question_kizomba_tutor_hides_raw_metrics_from_final_answer`).
   - Added `test_question_dancer_drill_uses_section_anchor` to lock in the new drill rule.
   - `test_question_song_arc_requires_distinctiveness` updated for the new "anchor it on a timestamp / structural feature" wording (the literal phrase "numeric anchor" is gone).
   - Added `test_question_song_arc_hides_raw_decimals_from_final_answer`.

## What worked

- The Phase 29 surgical pattern (forbid raw decimals, keep BPM and timestamps) ports cleanly to `QUESTION_DANCER` and `QUESTION_SONG_ARC`. No structural changes to the dancer's 4-section format or the song-arc's narrative-then-distinguish shape were needed.
- Live run on Filomena (kizomba) and Propuesta Indecente (bachata) after the dancer rewrite confirmed: bachata dancer no longer narrates `1.00 mean strength`, `0.05 tempo stability`, or `2.5 onsets/beat`; opens with "At 123 BPM, this track sits in a comfortable mid-range for bachata. The tempo is very steady…" and the drill correctly anchors to "the main section starting at 38.2s".
- Live run also confirmed the kizomba song arc reads as narrative ("low-energy intro from 0s to 12s… reaches its peaks during the high-energy sections at 59s, 121s, and 159s… resolves into a low-energy outro from 195s to 208.9s"), no downbeat claim, no analysis jargon in the main paragraph.
- Kizomba per-phase tutor unchanged and still good — Filomena's `break` still produces the recovery vocabulary ("reduce your travel and use this time to reset and breathe").

## Risks / what to watch

- `QUESTION_DANCER` runs for every style. The kizomba dancer output (when called via this prompt instead of `QUESTION_KIZOMBA_TUTOR`) should now be metric-clean too — verify in a future kizomba run that nothing regressed.
- The bachata dancer drill now requires a section label + timestamp. If the analysis happens to produce a track with very few sections, the drill might collapse into a generic instruction. Worth eyeballing the live output.
- The song-arc no-decimals rule was anticipated by Phase 31 part-A's "watch for raw-metric leaks" but only verified after the live run caught `percussiveness of 0.22` (kizomba) and `percussiveness of 0.16` (bachata). Bundled the fix into Phase 31 rather than deferring; same surgical move would have been needed in any case.

## Decision / takeaway

- Ship the dancer rewrite, song-arc cell, and song-arc tightening as one phase (`QUESTION_SONG_ARC` is now metric-clean too; no kizomba-specific variant needed).
- One-pass `QUESTION_DANCER` and `QUESTION_SONG_ARC` remain the documented baselines; no polish helpers for them (kizomba_tutor is the only prompt with a polish pass and that stays opt-in).
- The "forbid raw decimals + qualitative translation + BPM/timestamps allowed" pattern has now been applied to three prompts (`QUESTION_KIZOMBA_TUTOR` Phase 29, `QUESTION_DANCER` Phase 31, `QUESTION_SONG_ARC` Phase 31). If a fourth use case appears, lift the wording into a shared helper string.

## Phase 32 — kizomba section-drills (anchor, not implementation)

The Phase 30 demo run made the bachata dancer drill structure look genuinely useful. It would translate well to kizomba if drills are tied to specific section labels and beat-clarity tags rather than to raw decimals.

**Rough shape:**

- New prompt or extension that emits per-section drill suggestions tied to the existing label + beat-clarity tags from the analysis.
- Example output:
  ```
  P1: 0s-12s, intro, beat: subtle — Drill: stand still, count 8 internally,
      mark the pulse with a tiny shoulder bounce; do not start travelling yet.
  P3: 59s-80s, main, beat: clear — Drill: 30s of steady walk-step, focus
      on weight transfer landing exactly with the bass.
  P6: 148s-159s, break, beat: clear — Drill: practice the recovery — reduce
      travel for 10s, keep a small pulse in your body, then reconnect at P7.
  ```

**Open design questions for Phase 32 (do not decide here):**

1. Standalone `QUESTION_KIZOMBA_DRILLS` prompt vs. an extension to `QUESTION_KIZOMBA_TUTOR` (drills as an extra cell after the coaching).
2. Same P# format as `kizomba_tutor` or a separate block?
3. Drill duration: fixed 30s or scaled to section length?
4. Interaction with the (still-deferred) `learner_level` parameter — beginner drills focus on weight transfer, improver drills add hip styling, etc.
5. Bachata drills: same path or different prompt? `QUESTION_DANCER` already has a single drill at the end; a per-section drill prompt could subsume that.

**When to do it:**

Phase 32 is worth a small focused phase between now and the demo video sprint **only if** the kizomba song-arc cell from Phase 31 lands cleanly and the demo flow has room for a third Gemma call per kizomba track. If demo time/latency budget is tight, defer until after the video.

## Next step

1. Run notebook 00 end-to-end against the local Ollama endpoint. Capture before/after evidence:
   - Bachata dancer output: confirm no `1.00`, no `0.05`, no `2.5 onsets/beat`, no accent-pattern arrays — but still tempo, timestamps, drill, 4-section structure.
   - Kizomba song arc: 3–4 sentence narrative referencing phase structure and timestamps; no downbeat / "1" claim; no raw decimals.
2. If kizomba song arc reads clean, ship as-is. If it leaks metrics, plan a Phase 31b specialization (small `QUESTION_KIZOMBA_SONG_ARC` variant).
3. Decide on Phase 32 timing based on demo-content needs.
