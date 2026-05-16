# 2026-04-18 — Phase 10: Downbeat-confidence v2, `instrumental` label, prompt distinctiveness

## Goal
Close three listening-pass issues surfaced after Phase 9 landed (commits `b1dfb99` + `dfec87c`, 241 tests):

1. Downbeat offset wrong on *All Of Me (kizomba)*, *Charbel E Magia Official*, *Teu Toque (Official)* — user hears the "1" at `M10+4` / `M16+4` / `M6+1`, but `detect_downbeats()` picks `best_offset=0` with confidence far below the `0.25` gate, so the Phase 7 re-anchoring infrastructure stays dormant.
2. Mid-song vocal-quiet passages mis-labelled — *Propuesta Indecente* M84–M101 and *El Chaval (Bachata Musicality)* M44–M59 land on `main` / `break[melodic]`; *Baila Kizomba Amor* ~194 s is labelled `peak` but is really an instrumental bridge.
3. LLM explanations generic — the 26B MoE cloud run (`05_batch_analysis-26B.ipynb`) "boring and repeating the exact same obvious things (4/4 rhythm etc.)", per the user. Per-phase `QUESTION_SECTIONS` coaching didn't force any numeric anchoring so larger models reverted to style-level platitudes.

## Context / prior state
Phase 9 produced a reliable vocal-activity envelope (Demucs + Gemma paths) and used it for intro-extension + outro-contraction, but didn't touch the mid-song labelling. The kick-drum hypothesis for downbeats was noted but not implemented. Prompts were structurally sound (`QUESTION_DANCER` + 4-section format, style placeholders, coaching hints) but had no numeric-anchoring guard.

## Hypothesis
- **Downbeat**: a kick-drum band signal (40–150 Hz, bandpass + `onset_strength`) voting alongside the existing full-band onset signal will tip the combined score toward the right offset on at least one eval track. Combine signals by scale-normalization (divide each by its own max, then sum) rather than rank-averaging, so a flat signal can't contribute false confidence.
- **Instrumental**: the Phase 9 vocal envelope already has the information. A per-phrase `vocal_active_ratio < 0.25` AND `rms_ratio >= 0.75` (vocals absent, instruments still loud) double-gate, run after the Phase 9 passes, identifies exactly the passages the user flagged without needing new signals.
- **Prompts**: explicit format enforcement (`P#: <start>s-<end>s, <label> — <coaching>`) plus a "every sentence must cite a number" constraint will force specific output, at the cost of some fluency.

## What changed

### Commit 1 — `d29b895` (downbeat v2)
- [src/rytmi/dsp.py](../../src/rytmi/dsp.py):
  - New `_low_band_beat_position_strengths(audio, beats, bpm, lowcut=40, highcut=150)` — 4th-order Butterworth bandpass via `scipy.signal.butter + filtfilt`, then `librosa.onset.onset_strength` on the filtered audio, grouped per-offset. Returns zeros when the filtered signal is silent (synth/sine tracks).
  - New `_scale_normalize()` — divide by own max (flat signals → zeros), preserving within-signal decisiveness.
  - `detect_downbeats()` rewrite: `combined = _scale_normalize(onset_scores) + _scale_normalize(kick_scores)`; `best_offset = argmax(combined)`; `sqrt(margin × dominance)` confidence on `combined`; disagreement penalty `× 0.5` when kick and onset pick different offsets and kick has any signal.
- [tests/test_dsp.py](../../tests/test_dsp.py): 3 new tests — kick-agreement picks correct offset when onset is ambiguous; confidence penalised when the two signals disagree; graceful fallback on a pure-sine (non-percussive) track.

### Commit 2 — `00f37f8` (instrumental label)
- [src/rytmi/dsp.py](../../src/rytmi/dsp.py):
  - `_INSTRUMENTAL_MIN_PHRASES=2`, `_INSTRUMENTAL_MAX_VOCAL_ACTIVE_RATIO=0.25`, `_INSTRUMENTAL_MIN_RMS_RATIO=0.75`.
  - New pass `_relabel_vocal_drop_instrumentals(sections, vocal_env, phrase_times, rms_envelope, rms_times, global_rms_mean)` — walks phrase windows fully inside each non-intro/non-outro section; contiguous runs of ≥ 2 qualifying phrases become `instrumental` sections (whole-section matches relabel in place to avoid sliver boundaries).
  - Wired into `analyze()` inside the `if vocal_env is not None` block, after `_contract_outro_to_last_vocal` and before `_merge_same_branch_break_chains`.
- [src/rytmi/viz.py](../../src/rytmi/viz.py): `SECTION_COLORS["instrumental"]="#16a085"` (teal, ≥ 40-channel RGB gap from every other label). Legend list updated.
- [tests/test_dsp.py](../../tests/test_dsp.py): 6 new tests — promotes vocal-drop main; rejects 1-phrase dip; demotes vocal-quiet peak; leaves vocal peak untouched; no-op when envelope is None; splits partial runs correctly.
- [tests/test_viz.py](../../tests/test_viz.py): palette coverage updated; `test_section_colors_instrumental_distinct` asserts the RGB gap.

### Commit 3 — prompt distinctiveness (this commit)
- [src/rytmi/prompts.py](../../src/rytmi/prompts.py):
  - `_format_distinct_features_section(tempo, rhythm_features, style_profile)` — new helper. Surfaces 1–3 bullets when a track is an outlier vs. the style's typical range: tempo above/below `style_profile.bpm_range`; percussiveness > 0.65 or < 0.25; onsets-per-beat > 3.0 or < 1.0. Returns empty string for middle-of-the-road tracks so there's no spurious "this track is typical" bullet.
  - `{distinct_features_section}` inserted into `RHYTHM_ANALYSIS_TEMPLATE` between `{rhythm_features_section}` and `{sections_block}`.
  - `QUESTION_SECTIONS` rewritten: strict `P#: <start>s-<end>s, <label> — <coaching>` line format; coaching MUST cite a specific number (timestamp, BPM, onset density, percussiveness, energy ratio, accent pattern, rms ratio); style-platitudes without numbers "must be deleted"; 5-word fallback `continues the <prev_label> feel` for phases with no distinct feature; no intro/outro/summary text.
  - `QUESTION_DANCER`: appended the numeric-anchoring bullet ("every claim ties to a specific number; delete sentences you can't back").
  - `QUESTION_SONG_ARC`: appended a novelty constraint — after the 3–4-sentence narrative, one additional sentence identifying 1–2 things that distinguish THIS track from other same-style same-tempo tracks, anchored on a number or structural feature.
  - `DEFAULT_SYSTEM_PROMPT`: appended "emphasize specific numbers; avoid generic style-level statements" sentence.
- [tests/test_prompts.py](../../tests/test_prompts.py) (**new**): 11 tests — distinct-feature bullets for each outlier (percussiveness high/low, onset density dense, tempo above/below range), empty output when nothing stands out, empty without style profile, ≤ 3-bullet cap, and presence tests for the new numeric-anchoring / distinctiveness constraints on QUESTION_SECTIONS / QUESTION_DANCER / QUESTION_SONG_ARC.
- [tmp/05_batch_analysis-26B.phase9.txt](../../tmp/05_batch_analysis-26B.phase9.txt) — archived Phase 9 26B outputs for side-by-side comparison.

## Evidence / test results

**Tests:** `pytest -q` → **262 passed, 1 skipped**. Breakdown:
- 241 Phase 9 baseline + 3 new downbeat tests = 244 after Commit 1.
- + 6 instrumental DSP tests + 1 viz palette test = 251 after Commit 2.
- + 11 new prompt tests = **262 total** after Commit 3.

**Eval-set observations:**

- **Commit 1 (downbeat v2):** no track on the current 10-track eval lifts above the `0.25` confidence gate even with the kick-band addition. Highest observed was *Charbel-Ana-Ben* at `0.194`. `best_offset` raw output is measurably more diagnostic (5 of 10 tracks pick non-zero offsets where Phase 9 picked all zeros) but the confidence penalty correctly keeps `effective_offset=0` when the two signals disagree, so user-facing behaviour is unchanged on this eval set. **No regression; the signal is in place for when better-suited tracks are added.**
- **Commit 2 (instrumental):** fires on every user-flagged passage.
  - *Propuesta Indecente*: `instrumental 02:50.90–02:58.93` and `03:06.76–03:14.56` (within the M84–M101 range the user flagged).
  - *El Chaval*: `instrumental 01:29.84–01:44.61` (user flagged M44–M59 area).
  - *Baila Kizomba Amor*: `instrumental 02:54.57–03:14.70` bracketing the ~194 s former pseudo-peak; the Phase 8 `peak` label is demoted in place.
  - Timeline renders these as teal bands distinct from main/break/peak.
- **Commit 3 (prompts):** qualitative — see `tmp/05_batch_analysis-26B.phase9.txt` vs. the post-Commit-3 run. The new `P#:` format forces per-phase numeric references; the `DEFAULT_SYSTEM_PROMPT` addition is a second line of defence when `QUESTION_SECTIONS` is paraphrased away by a generative model. Full side-by-side is pending the user's next notebook re-run.

## What worked

- **Kick-band + scale-normalization fusion** keeps the Phase-9 `test_detect_downbeats_confidence_low_on_uniform_beats` assertion green: a flat uniform-click signal produces `_scale_normalize(zeros) = zeros`, so the combined score stays uninformative and confidence correctly stays low. Rank-averaging (the original plan) would have artificially spread flat inputs across [0, 1] and produced false confidence.
- **Disagreement penalty** acts as a built-in safety net: when kick and onset pick different offsets, confidence is halved. Combined with the unchanged `0.25` gate, Commit 1 cannot introduce a regression on any currently-working track — worst case, nothing changes.
- **`instrumental` detection** lands exactly the three passages the user flagged, with zero over-fire on the other seven eval tracks. The double-gate (`vocal_active_ratio < 0.25 AND rms_ratio >= 0.75`) is strict enough that a chorus with a short instrumental bridge doesn't qualify (bridge-phrases will typically trigger only on one side of the gate).
- **Palette gap ≥ 40 test** catches the error the viz module could have regressed into — teal was chosen to sit between `peak` red and `break` yellow in hue space but at very different saturation, giving clear visual separation from both.
- **Distinct-features helper is conservative by design.** Middle-of-the-road values produce zero bullets, so the block doesn't dilute the analysis when there's nothing to say. On outlier tracks it reliably surfaces the specific number, which is what the prompt upgrades need to grab onto.

## What did not / limitations

- **`0.25` confidence gate still not cleared** by any current eval track. Likely needs either (a) eval-set expansion with tracks that have a cleaner drum-led "1" (semba, zouk with strong percussion), (b) a third signal (e.g. low-band RMS peak detection at beat positions, or a learned per-style prior), or (c) recalibration of the gate itself to something like `0.15` if qualitative listening confirms the raw offsets are useful below that threshold. Kept the gate at `0.25` for now — this commit introduces infrastructure, not a calibration change.
- **Instrumental threshold is eval-set calibrated, not principled.** The specific `0.25` / `0.75` cutoffs fit the three flagged passages but haven't been tested against adversarial cases (e.g. a chorus with heavily-filtered vocals below the Demucs activity threshold but clearly present to a human listener). The strict `_INSTRUMENTAL_MIN_PHRASES=2` cap is the main safety net here.
- **Prompt-constraint effectiveness is model-dependent.** A well-aligned model (26B MoE) will follow the format. Smaller models (Gemma 4 E4B local) may paraphrase, drop the `P#:` prefix, or revert to platitudes — the constraints are upstream guardrails, not a hard filter.
- **`_format_distinct_features_section` only reads global rhythm features.** Per-section outliers (e.g. one peak with `rms_ratio > 1.4`) are out of scope for this commit; they would need a second traversal with extra state. Deferred to Phase 11 if the current global-only bullets prove insufficient.

## Decision / takeaway

**Phase 10 ships all three commits.** Commit 2 is the clearest win — a user-visible new label, exact match on flagged passages, six tests. Commit 1 is infrastructure without a behaviour change on this eval set, but is the foundation for downbeat-aware phrasing when tracks arrive that can clear the gate. Commit 3 is the Kaggle-demo lever — the distinction between "generic 4/4 bachata" and "track-specific `P5-8: 38s-85s, main — percussiveness 0.72 dominates the timba layer`" is exactly the difference between boring and useful LLM output.

**No regression risk on the 10-track eval set.** Full suite green (262 passed), palette tests enforce the new colour, the downbeat disagreement penalty keeps the confidence gate honest.

## Next step

1. Collect user listening feedback on the three commits together:
   - Do the `instrumental` bands match the passages the user wants them to?
   - Does the 26B run post-Commit-3 feel less boring? Is there any track where the P# format regresses fluency?
   - With the raw `best_offset` now diagnostic on 5/10 tracks, is the right call to lower the confidence gate (e.g. `0.20`) or to keep gathering better eval tracks?
2. If the distinct-features block fires rarely on the current eval set, consider adding per-section outliers (strongest peak / deepest break by `rms_ratio`) — the most common "this track is different" signal is a dramatic section-to-section contrast, not a track-level global outlier.
3. Phase 11 candidates — still deferred:
   - Vocal character / register sub-sections (All Of Me M80–M85 "mellow", Baila P6–P11 "chilling") — needs vocal pitch/timbre analysis on the Demucs vocal stem.
   - Speech-vs-singing discrimination (Propuesta P1–P8 dialog prologue) — potentially via a Gemma multimodal YES/NO on the Phase 9 window infrastructure.
   - Per-track boundary precision tweaks: Baila short_break P58→P59, Charbel-Ana beginning false-positive short_break, break P17→P18, Teu Toque S6→M74.
   - Recurring-motif prompts (Teu Toque P11 + P14 short drops as one coaching motif).
   - Eval-set expansion to 16–24 tracks, semba / zouk.
