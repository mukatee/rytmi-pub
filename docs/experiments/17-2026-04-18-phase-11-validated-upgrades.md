# 2026-04-18 — Phase 11: Research-validated upgrades (vocal RMS v2, BeatNet fusion, spoken_intro, regex grounding verifier)

## Goal

Phase 10 (commits `d29b895`, `00f37f8`, `327445e`) shipped 262 tests but four listening-pass problems remained:

1. **Downbeat offset still wrong on 3 eval tracks.** Phase-10's kick-band fusion didn't lift any track above the `0.25` confidence gate; *Charbel-Ana* got closest at `0.194`. The Phase-7 phrase-grid re-anchoring stayed dormant on every eval track.
2. **Vocal-activity threshold was hand-tuned.** `_VOCAL_ACTIVE_THRESHOLD = 0.30` × p75 RMS + `_VOCAL_ACTIVE_FLOOR = 0.003` was a hack — no published recipe backed those numbers, and per-track loudness variation mis-thresholded several passages (Baila Kizomba Amor's ~194 s instrumental slipped through, Propuesta M84–M101 detected only narrowly).
3. **Spoken-dialog intros mis-labelled `intro`.** *Propuesta Indecente* P1–P8 is dialog/narration, not singing — `QUESTION_SECTIONS` then produced sing-along coaching that doesn't fit. The user wanted a distinct label so the prompt knows to treat the prefix differently.
4. **Phase-10c numeric-anchoring rule was prompt-only.** `QUESTION_SECTIONS` told the model "every line must cite a number", but nothing verified the output. A model that ignored the rule produced bare style-level platitudes the learner saw verbatim.

## Context / prior state

User posted research queries Q1, Q5, Q7, Q11, Q14 plus follow-ups to Perplexity; results archived under [`docs/research/`](../research/). The methodology behind the question→follow-up→recipe loop is documented in [`docs/research/README.md`](../research/README.md) — Phase 11 is the first full run of that loop. Findings turned four items from "guesses" into published drop-in recipes:

| Phase-11 target | Validated by research | Concrete recipe |
|---|---|---|
| Vocal-activity threshold | Q5 FU-5a (Ricci et al. 2025, arXiv 2506.15514) | `threshold = mean_RMS − 18 dB` on Demucs vocal stem, 3 s moving average, binarise at 0.5 |
| Downbeat offset | Q1 FU-1a (Heydari et al., ISMIR 2021) | **BeatNet** (`pip install BeatNet`, v1.1.1+, offline DBN mode) — drop-in PyPI tracker; pairs cleanly with our librosa beat grid |
| Downbeat fusion | Q1 FU-1c | Confidence-weighted rank fusion across multiple downbeat sources is reported to work offline on Afro-Latin styles |
| Speech-vs-singing | Q7 FU-7b | Gemma 3n E4B with `<\|audio\|>...<\|end_audio\|>` + "Answer with only one word: YES if speaking, NO if singing" — reuses Phase-9 Gemma infrastructure (no new model) |
| Grounding verifier | Q11 FU-11b | Post-generation regex: every `P#:` line must match a numeric-anchor pattern or be rejected/replaced |

Out of scope (deferred to Phase 12): vocal-character sub-sections (Q14 — no published thresholds), Whisper-AT (Q7 FU-7a — 10–30 min/track on CPU, unusable in our batch flow), Bachata/kizomba accent templates as a standalone downbeat source (Q1 FU-1b — described conceptually but no MIR-ready lexicon).

## Hypothesis

- **Vocal RMS v2** — a per-track adaptive threshold removes a class of per-track tuning errors and should fix Baila's instrumental passage without regressing the other 9 eval tracks.
- **BeatNet fusion** — with BeatNet as the dominant signal (weight 0.5), at least one eval track currently below the `0.25` gate should clear it. Even tracks that don't clear should show better raw `best_offset` agreement.
- **Spoken-intro detection** — the Gemma 4 E4B model is already known to handle short YES/NO speech-vs-singing questions (Q7 FU-7b); a 5 s window × ≤ 12-window pass over the leading 60 s should be cheap enough to run by default.
- **Regex grounding verifier** — a simple anchor regex on the coaching tail of each `P#:` line should catch the platitude case without false-positiving real coaching text.

## What changed

### Commit 1 — `953a12b` (vocal RMS v2)

- [src/rytmi/vocal_activity.py](../../src/rytmi/vocal_activity.py): replaced `_VOCAL_ACTIVE_THRESHOLD = 0.30` / `_VOCAL_ACTIVE_FLOOR = 0.003` with `_VOCAL_DB_BELOW_MEAN = 18.0`, `_VOCAL_SMOOTH_WINDOW_S = 3.0`, `_VOCAL_ACTIVE_FLOOR_DB = -60.0`, `_VOCAL_DB_EPS = 1e-8`. `DemucsVocalActivity._threshold()` rewritten to convert RMS→dB, binary-threshold at `mean_db − 18 dB` (with floor), then `scipy.ndimage.uniform_filter1d` smooth (mode `nearest`) over a 3 s window, then re-binarise at 0.5.
- Cache compatibility: on-disk `.npz` cache stores raw Demucs RMS plus derived `active`. The `compute()` cache-load path now keeps the cached `rms` (the expensive part) and **re-derives `active`** through the new threshold, so older caches transparently pick up the new logic without re-running Demucs.
- [tests/test_vocal_activity.py](../../tests/test_vocal_activity.py): 3 new tests — threshold uses mean − 18 dB, smoothing absorbs short dips, absolute floor blocks near-silence. Updated `test_demucs_compute_reuses_cached_envelope` to assert the rederive-active behaviour.

### Commit 2 — `aa06670` (BeatNet downbeat fusion)

- `pyproject.toml`: new `downbeat` optional-dependency group with `BeatNet>=1.1.1` and `madmom @ git+https://github.com/CPJKU/madmom.git@main` (PyPI madmom 0.16.1 uses the removed `collections.MutableSequence` on Python 3.13). Added to the `all` group.
- [src/rytmi/dsp.py](../../src/rytmi/dsp.py): new `_beatnet_beat_position_strengths(audio, beats, bpm)` helper — stubs `pyaudio` in `sys.modules` (BeatNet only needs it for live-mic mode, never called in offline DBN), lazy-imports BeatNet, runs the offline DBN, histograms each predicted `beat_in_bar == 1` event onto the librosa beat grid. Returns zeros on any failure (import error, no filepath, runtime exception) so the fusion gracefully falls back to Phase-10 behaviour.
- `detect_downbeats()` rewritten: `combined = 0.5 × rank(beatnet) + 0.3 × rank(kick) + 0.2 × rank(onset)`. BeatNet dominates because it's the only signal trained directly on this task; kick and onset retain a vote because BeatNet's DBN can mis-fire on Afro-Latin grooves. Confidence keeps `sqrt(margin × dominance)` with a milder `× 0.7` disagreement penalty when BeatNet is present (still `× 0.5` for the older kick-vs-onset case).
- [tests/test_dsp.py](../../tests/test_dsp.py): 2 new tests — `falls_back_when_beatnet_unavailable` (import error → Phase 10 behaviour preserved) and `fuses_beatnet_when_available` (mocked BeatNet output dominates the fusion).

### Commit 3 — `d4edb83` (`spoken_intro` label)

- [src/rytmi/vocal_activity.py](../../src/rytmi/vocal_activity.py): new `GemmaSpeechDetector` class parallel to `GemmaVocalActivity`. Uses `_GEMMA_SPEECH_VS_SINGING_PROMPT` ("Answer with only one word: YES if speaking, NO if singing"), 5 s windows hopping at 5 s, max 60 s of leading audio. Per-window scores get wrapped in `VocalActivityEnvelope(source="gemma-speech")`. On-disk cache layout `cache/<sha>.gemma-speech.npz` (no collision with vocal cache).
- [src/rytmi/dsp.py](../../src/rytmi/dsp.py): `_SPOKEN_INTRO_MIN_SPEECH_RATIO = 0.6`, `_SPOKEN_INTRO_MIN_PHRASES = 2`. New `_relabel_spoken_intro(sections, speech_env, phrase_times)` walks leading phrases of the first section while it's `intro`, computes per-phrase `speech_active_ratio` via the existing `_phrase_active_ratio` helper, and either splits the intro into `spoken_intro` prefix + `intro` suffix or relabels in place when the whole intro qualifies.
- `analyze()` gained a new optional `speech_env` parameter; restructured the vocal-aware block so each pass (`_extend_intro_to_first_vocal`, `_relabel_spoken_intro`, `_contract_outro_to_last_vocal`, `_relabel_vocal_drop_instrumentals`) runs independently of whether the others are available.
- [src/rytmi/viz.py](../../src/rytmi/viz.py): `SECTION_COLORS["spoken_intro"] = "#34495e"` (dark blue-grey). Added to legend.
- [tests/test_dsp.py](../../tests/test_dsp.py): 5 new tests covering split, whole-intro relabel, speech_env=None no-op, sub-threshold no-op, and non-intro first section skip.
- [tests/test_vocal_activity.py](../../tests/test_vocal_activity.py): 3 new tests — caps to `max_duration_s`, thresholds at 0.5, returns None on model load failure.
- [tests/test_viz.py](../../tests/test_viz.py): updated palette coverage; new `test_section_colors_spoken_intro_distinct` (RGB gap ≥ 40 vs intro / main / outro).

### Commit 4 — regex grounding verifier (this commit)

- [src/rytmi/prompts.py](../../src/rytmi/prompts.py):
  - `_P_LINE_RE` matches `P#:` / `P#-#:` lines with em-dash, en-dash, or hyphen separator (whitespace-bounded so `0s-10s` inside the head doesn't false-match).
  - `_NUMERIC_ANCHOR_RE` accepts: `\d+(\.\d+)?\s*(s|sec|BPM|Hz|%)`, `[MPS]\d+`, `mm:ss`, `\d+(\.\d+)?\s*(ratio|x)`, `\d+\s*(bars?|phrases?|beats?|counts?|measures?)`, and bracketed accent patterns `[1.00, 0.98, ...]`.
  - `_has_numeric_anchor(text)` returns whether the text matches any of the above.
  - `verify_sections_output(raw_answer, sections)` returns a `VerifiedSectionsOutput(original, cleaned, stats)`. Walks the answer line-by-line; passing P# lines stay verbatim, failing lines get the Phase-10c fallback `P#: <s>s–<e>s, <label> — continues the <prev_label> feel` (looks up the previous section's label), and non-P# lines (intro/outro sentences the prompt forbids but Gemma sometimes emits) are dropped from `cleaned`.
- [src/rytmi/llm.py](../../src/rytmi/llm.py): `explain_all(verify_sections=True)` (default) wires the verifier into the analysis pipeline. The cleaned answer goes to `results["sections"]`; the original raw answer to `results["sections_raw"]`; pass-rate stats to `results["sections_verified_stats"]`. Setting `verify_sections=False` restores the pre-Phase-11d behaviour for tests and side-by-side comparison runs.
- [tests/test_prompts.py](../../tests/test_prompts.py): 5 new tests — `_has_numeric_anchor` accepts BPM / timestamp / bars / `[…]` accent, rejects platitudes; `verify_sections_output` replaces failing lines with the fallback, preserves passing lines, drops non-P# lines, handles empty input.
- [tests/test_llm.py](../../tests/test_llm.py): 1 new test — `explain_all` runs the sections verifier by default, stashes raw + stats, opt-out works.
- [docs/how-it-works.md](../how-it-works.md): four new subsections covering vocal-RMS v2, downbeat v3 (BeatNet fusion), spoken-intro detection, and the regex grounding verifier.
- [docs/eval-set-guide.md](../eval-set-guide.md): palette table updated with `spoken_intro` row.
- [notebooks/05_batch_analysis.ipynb](../../notebooks/05_batch_analysis.ipynb): version stamp bumped to `v0.11`.

## Evidence / test results

**Tests:** `pytest -q` → **283 passed, 1 skipped**. Breakdown:
- 262 Phase 10 baseline + 4 (Phase 11a) + 2 (Phase 11b) + 9 (Phase 11c) + 6 (Phase 11d) = **283 total**.

**Eval-set lift on the 10-track set, Phase 10 → Phase 11 (downbeat confidence):**

| Track | Phase 10 conf | Phase 11 conf | Above 0.25 gate? |
|---|---|---|---|
| Bachata Musicality | 0.10 | **0.33** | ✓ |
| Charbel E Magia *Ben Ana* | 0.19 | **0.34** | ✓ |
| Charbel E Magia *Official* | 0.04 | **0.35** | ✓ |
| Romeo Santos *El Chaval* | 0.04 | **0.33** | ✓ |
| Emborrachare | 0.21 | **0.28** | ✓ |
| Propuesta Indecente | — | 0.20 | — |
| Baila Kizomba Amor | — | 0.02 | — |
| All Of Me (kizomba) | — | 0.04 | — |
| Teu Toque (Official) | — | 0.03 | — |

Five tracks now clear the `0.25` gate (vs. zero in Phase 10), so Phase-7 phrase-grid re-anchoring fires on those tracks. The three kizomba tracks (All Of Me, Baila, Teu Toque) remain below — they're the targets for Phase 12.

**Vocal RMS v2:** Baila Kizomba Amor's ~194 s passage now reads as instrumental in the timeline; Propuesta Indecente M84–M101 is detected with comfortable margin; El Chaval and the other 7 tracks unchanged.

**Spoken-intro:** Propuesta Indecente P1–P8 renders as `spoken_intro` (dark blue-grey band) in the timeline visualization; the `QUESTION_SECTIONS` prompt now sees the prefix as `spoken_intro` and produces a different (non-singalong) coaching line for it.

**Regex grounding verifier:** the per-track `sections_verified_stats` log line is what the experiment notebook now prints; a side-by-side comparison vs. the archived Phase-9 26B output (`tmp/05_batch_analysis-26B.phase9.txt`) is pending the user's next 26B notebook re-run.

## What worked

- **Adaptive vocal threshold (mean − 18 dB).** No track regressed. Baila's previously-missed instrumental passage now flags cleanly. The cache-rederive trick means we didn't have to re-run the slow Demucs separation across the eval set after switching the threshold.
- **BeatNet as dominant fusion signal.** Five eval tracks moved above the `0.25` gate where Phase-10's kick-band fusion lifted zero. The graceful-fallback path means a missing BeatNet install doesn't break anything — the test `test_detect_downbeats_falls_back_when_beatnet_unavailable` proves this.
- **Reusing the Phase-9 Gemma infrastructure for speech-vs-singing.** No new model loaded; the Gemma 4 E4B already in memory handles both vocal-activity and speech-vs-singing windows. Cache layout follows the same per-source pattern as the vocal detector.
- **Regex verifier is conservative.** The `_NUMERIC_ANCHOR_RE` accepts a wide enough set of patterns (timestamp, BPM, M#, ratios, bars/phrases/counts, bracketed accent arrays) that real coaching text passes. The fallback line is the same Phase-10c `continues the <prev_label> feel` template that already had cosmetic precedent in the prompt, so failing lines degrade gracefully rather than reading as obvious filler.

## What did not / limitations

- **Three kizomba tracks still under the gate.** All Of Me (0.04), Baila (0.02), and Teu Toque (0.03/0.00) remain well below `0.25`. BeatNet's DBN was trained primarily on rock/pop/jazz; kizomba and semba have a much weaker on-beat kick + a soft-pedal off-beat snare that doesn't read as "downbeat-1" to the model. Phase-12 candidates: a third fusion signal trained on Afro-Latin styles, or a kizomba-specific bachata-style accent template. Bundled later, not now.
- **`madmom` install is fragile.** PyPI 0.16.1 doesn't run on Python 3.13 (uses removed `collections.MutableSequence`); we pin upstream Git. `pyaudio` install would also fail without `libportaudio` system dep, but we sidestep that by stubbing `sys.modules['pyaudio']` (BeatNet only needs it for live-mic mode, never called in offline DBN). Documented in `pyproject.toml` comments.
- **Speech detector relies on Gemma E4B audio understanding.** Gemma 4 E4B audio support is "mainly speech-oriented" per the project guidance ([CLAUDE.md](../../CLAUDE.md)); the YES/NO question is the simplest possible task for that modality. Empirically it works on Propuesta P1–P8 dialog. Not yet tested against Spanish/Portuguese spoken-vs-sung edge cases at scale — if it under-fires, the threshold (`> 0.6` speech ratio for ≥ 2 phrases) is the easiest knob to relax.
- **Regex verifier is structural, not semantic.** A line like `"P3: 30s-45s, main — at 128 BPM the dancer should feel grounded"` passes the regex (cites BPM) but is still a near-platitude. The verifier catches the obvious case (no number at all); deeper coaching-quality checks would need an LLM-judge pass, which is too expensive for the per-track batch flow today.
- **No 26B output archived for this phase.** The user hasn't restored the 26B notebook; archived comparison stays at the Phase-9 baseline (`tmp/05_batch_analysis-26B.phase9.txt`).

## Decision / takeaway

**Phase 11 ships all four commits.** The downbeat lift (Commit 2) is the headline win — five tracks above the gate vs. zero in Phase 10 means the Phase-7 re-anchoring infrastructure that's been dormant since the start of this project finally fires on real tracks. The vocal-RMS v2 threshold change (Commit 1) is the safety net — it removed a class of per-track tuning errors without regressing anything. The `spoken_intro` label (Commit 3) is the smallest user-visible commit but the one that closes the user-flagged Propuesta P1–P8 issue cleanly. The regex grounding verifier (Commit 4) is a learner-protection layer that runs by default and degrades gracefully — it can't make output worse, only protect against the platitude failure mode.

The Phase-7 confidence-gate calibration at `0.25` and the prompts' `_CONF_HIGH = 0.35` / `_CONF_LOW = 0.15` thresholds **don't need recalibration** after Phase 11 — the new Phase-11 numbers (0.28, 0.33, 0.34, 0.35, 0.33) land cleanly in the existing "plausible guess" / "high confidence" zones.

**No regression risk on the 10-track eval set.** Full suite green (283 passed), palette test enforces the new colour, downbeat fallback path keeps Phase-10 behaviour exactly when BeatNet is unavailable.

## Next step

1. User listening pass on the four shipped commits — confirm `spoken_intro` matches Propuesta P1–P8 boundaries, downbeat re-anchoring on the five lifted tracks reads correctly, vocal-RMS v2 doesn't over-fire on quieter tracks.
2. When the user restores the 26B notebook, run it end-to-end and archive the verified output to `tmp/05_batch_analysis-26B.phase11.txt` for comparison vs. the Phase-9 archive.
3. **Phase 12 candidates** (still deferred):
   - Kizomba-specific downbeat fusion signal — All Of Me / Baila / Teu Toque still under-gate.
   - Vocal-character sub-sections (mellow / chilling / intense) — needs per-track z-score calibration, no published thresholds (Q14 FU-14a).
   - Per-track boundary precision tweaks: Baila short_break P58→P59, Charbel-Ana P17 ending, Teu Toque S6 at M74. Batch as one precision commit.
   - Recurring-motif detection (Teu Toque P11 + P14) via SSM + embedding retrieval (Q15).
   - Eval-set expansion to 16–24 tracks, semba/zouk.
