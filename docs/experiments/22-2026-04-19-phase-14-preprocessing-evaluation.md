# 22 — Phase 14: preprocessing evaluation (HPSS / Demucs drums / B2 prompt retry)

**Date:** 2026-04-19
**Scope:** Three candidate preprocessing / prompt approaches evaluated against the 16-track eval set. All changes are behind off-by-default flags; no default behaviour changed.
**Status:** **All three options produce negligible uplift on the three stuck kizomba tracks (Baila, Filomena Teu Toque, All Of Me).** None crosses the 0.25 confidence gate. Detailed evidence and cost-vs-benefit comparison below.

## Goal

Lift the three kizomba tracks stuck at ≤0.04 downbeat confidence (Baila 0.017, Filomena Teu Toque 0.027, All Of Me 0.040) above the 0.25 gate by changing the input signal fed to the kick-band / onset DSP helpers, or by retrying the Gemma B2 tiebreaker with a less constrained prompt and later clip window.

## Context / prior state

- **Commit A2 baseline** (note 20): adaptive safe-vs-full template guard. 6 of 16 tracks above the 0.25 gate. Three target tracks at 0.017 / 0.027 / 0.040.
- **Commit B2** (note 21): Gemma E4B tiebreaker. Negative result — 52/52 NO votes. Module preserved as scaffold.
- Note 21's "Decision / takeaway" named three Phase-14 options: (1) HPSS-percussive preprocessing, (2) Demucs drum-stem preprocessing, (3) B2 prompt + clip retry.

## Hypothesis

The three stuck tracks have weak kick-band signal because the raw audio mixes harmonic content (vocal sibilance, guitar) into the 40–150 Hz band, flattening the per-offset vector. Isolating percussive transients (via HPSS or Demucs drum separation) before computing kick/onset strengths should produce a more peaked signal — potentially enough to push ambiguous tracks above the gate.

For the B2 retry: the original all-caps START/BEGINNING prompt over-constrained Gemma E4B toward NO; a permissive rephrasing with a later-in-track clip may produce per-offset discrimination.

## What changed

### Option 1 — HPSS-percussive DSP pass

- New helper `_percussive_audio(audio) → AudioData` in `dsp.py` — runs `librosa.effects.hpss(margin=2.0)` and returns the percussive component as a new `AudioData`.
- Module-level flag `_USE_HPSS_PREPROCESSING = False` (off by default). When True, `detect_downbeats()` feeds the percussive AudioData to `_beat_position_strengths`, `_low_band_beat_position_strengths`, and `_mid_high_band_beat_position_strengths`. BeatNet stays on raw audio.
- 1 new unit test: `test_hpss_kick_signal_more_peaked_on_percussive` — synthetic kick-plus-string-pad signal confirms the kick-band vector is more peaked on `y_perc` than raw. Passes.

### Option 2 — Demucs drum-stem DSP pass

- New module `src/rytmi/drum_stem.py` (175 LOC) mirroring `vocal_activity.DemucsVocalActivity` but keeping the drums stem (Demucs source index "drums") instead of vocals. Separate cache directory `cache/drums/`, tag `demucs-drums:htdemucs`.
- Module-level flag `_USE_DRUM_STEM = False` (off by default).
- Eval script `tmp/run_phase14_opt2_eval.py` with `--pause` and `--tracks` flags.
- 1 new unit test: `test_drum_stem_extract_returns_audio_data_with_stub` — stubbed `_separate_drums` verifies the AudioData contract. Passes.

### Option 3 — B2 prompt + clip retry

- New constants in `gemma_downbeat.py`: `_PROMPT_VARIANT = None` (set to `"v2"` to activate), `_PROMPT_V2` (permissive wording — no all-caps, no numeric anchoring), `_CLIP_START_FRACTION = 0.0` (set >0 to skip intro region).
- Extended `_candidate_clip_window()` with `start_fraction` kwarg — skips beats before the specified fractional position.
- Extended `_query_gemma_downbeat()` with `prompt` kwarg — uses v2 prompt when `_PROMPT_VARIANT == "v2"`.
- Eval script `tmp/run_b2_eval_v2.py` with `--variant` and `--clip-start` flags.
- All 13 existing `test_gemma_downbeat.py` tests pass unchanged.

### Test suite

312 passed, 1 skipped (baseline was 310 passed, 1 skipped; +2 new tests).

## Evidence

### Option 1 — HPSS-percussive (16-track eval)

Log: `tmp/phase14_opt1_hpss.log`

| Track | Baseline (off, conf) | HPSS (off, conf) | Δ conf | Above gate? |
|---|---|---|---|---|
| bachata / Bachata Musicality 12 | (2, 0.332) | (2, 0.314) | −0.018 | ✅→✅ |
| bachata / Romeo Canalla | (2, 0.331) | (2, 0.302) | −0.029 | ✅→✅ |
| bachata / Grupo Extra | (2, 0.281) | (2, 0.277) | −0.004 | ✅→✅ |
| bachata / Romeo Propuesta | (2, 0.181) | (2, 0.200) | +0.019 | ❌→❌ |
| **kizomba / All Of Me** | **(3, 0.040)** | **(3, 0.037)** | **−0.003** | **❌** |
| **kizomba / Baila** | **(2, 0.017)** | **(2, 0.008)** | **−0.009** | **❌** |
| kizomba / Charbel Ben-Ana | (3, 0.336) | (3, 0.337) | +0.001 | ✅→✅ |
| kizomba / Charbel Official | (3, 0.347) | (3, 0.384) | +0.037 | ✅→✅ |
| **kizomba / Filomena Teu Toque** | **(3, 0.027)** | **(3, 0.029)** | **+0.002** | **❌** |
| kizomba / Tony Pirata | (3, 0.004) | (3, 0.011) | +0.007 | ❌ |
| bachata / Prince Royce | (0, 0.406) | (0, 0.349) | −0.057 | ✅→✅ |
| kizomba / Curticão | (2, 0.038) | (2, 0.040) | +0.002 | ❌ |
| kizomba / Bonga | (3, 0.184) | (3, 0.182) | −0.002 | ❌ |
| kizomba / Criola | (0, 0.008) | (0, 0.021) | +0.013 | ❌ |
| kizomba / Don Kikas | (3, 0.053) | (3, 0.052) | −0.001 | ❌ |
| kizomba / Mika Mendes | (2, 0.045) | (2, 0.043) | −0.002 | ❌ |

**Above-gate count:** 6→6 (same set). No offset changes. Target tracks: negligible movement (−0.003, −0.009, +0.002). Prince Royce regresses −0.057 but stays above gate.

### Option 2 — Demucs drum-stem (16-track eval)

Log: `tmp/phase14_opt2_demucs.log`

| Track | Baseline (off, conf) | Drums (off, conf) | Δ conf | Above gate? |
|---|---|---|---|---|
| bachata / Bachata Musicality 12 | (2, 0.332) | (2, 0.330) | −0.002 | ✅→✅ |
| bachata / Romeo Canalla | (2, 0.331) | (2, 0.327) | −0.004 | ✅→✅ |
| bachata / Grupo Extra | (2, 0.281) | (2, 0.290) | +0.008 | ✅→✅ |
| bachata / Romeo Propuesta | (2, 0.181) | (2, 0.185) | +0.004 | ❌→❌ |
| **kizomba / All Of Me** | **(3, 0.040)** | **(3, 0.028)** | **−0.012** | **❌** |
| **kizomba / Baila** | **(2, 0.017)** | **(2, 0.005)** | **−0.012** | **❌** |
| kizomba / Charbel Ben-Ana | (3, 0.336) | (3, 0.309) | −0.027 | ✅→✅ |
| kizomba / Charbel Official | (3, 0.347) | (3, 0.337) | −0.010 | ✅→✅ |
| **kizomba / Filomena Teu Toque** | **(3, 0.027)** | **(3, 0.041)** | **+0.014** | **❌** |
| kizomba / Tony Pirata | (3, 0.004) | (3, 0.002) | −0.002 | ❌ |
| bachata / Prince Royce | (0, 0.406) | (0, 0.352) | −0.054 | ✅→✅ |
| kizomba / Curticão | (2, 0.038) | (2, 0.095) | +0.057 | ❌ |
| kizomba / Bonga | (3, 0.184) | (3, 0.210) | +0.026 | ❌ |
| kizomba / Criola | (0, 0.008) | (2, 0.017) | +0.009 | ❌ offset change |
| kizomba / Don Kikas | (3, 0.053) | (3, 0.082) | +0.029 | ❌ |
| kizomba / Mika Mendes | (2, 0.045) | (2, 0.032) | −0.013 | ❌ |

**Above-gate count:** 6→6 (same set). Target tracks: All Of Me −0.012, Baila −0.012, Filomena +0.014. None near the gate. Curticão shows the largest positive shift (+0.057→0.095) but still well below 0.25. Some tracks (Charbel Ben-Ana −0.027, Prince Royce −0.054) regress modestly. One offset change (Criola 0→2, both at very low confidence).

### Option 3 — B2 prompt v2 + 50% clip start (3-track probe)

Log: `tmp/phase14_opt3_b2_retry.log`

| Track | DSP (off, conf) | Gemma votes (0,1,2,3) | Refined (off, conf) | Moved above gate? |
|---|---|---|---|---|
| **kizomba / Baila** | (2, 0.017) | `Y, Y, Y, Y` | (2, 0.300) | "✅" — false signal |
| **kizomba / Filomena Teu Toque** | (3, 0.027) | `Y, Y, Y, Y` | (3, 0.300) | "✅" — false signal |
| kizomba / Tony Pirata | (3, 0.004) | `Y, Y, Y, Y` | (3, 0.300) | "✅" — false signal |

**Result: the opposite pathology from v1.** The original prompt produced 52/52 NO (over-constrained); the permissive v2 prompt produced 12/12 YES (over-permissive). Neither provides per-offset discrimination. The 0.300 confidence is an artefact of the multi-YES-with-DSP-among-them branch endorsing DSP's existing pick — it's not evidence that the DSP offset is correct.

**This confirms note 21's hypothesis #2 (prompt over-constraint) was partially correct** — the all-caps anchoring pushed toward NO — but the fix (removing it) merely swung the bias to all-YES. Gemma E4B's audio front-end does not have the competence to discriminate phrase boundaries in kizomba music. The B2 tiebreaker path is now doubly closed.

## Cost-vs-benefit comparison

| Dimension | Option 1 (HPSS) | Option 2 (Demucs drums) | Option 3 (B2 v2 prompt) |
|---|---|---|---|
| **LOC added** | ~25 (helper + flag) | ~175 (new module) | ~25 (constants + kwarg) |
| **New files** | 0 | 1 (`drum_stem.py`) | 0 |
| **New tests** | 1 | 1 | 0 (13 existing pass) |
| **Runtime cost/track** | ~2 s CPU (HPSS) | ~30 s GPU first run, cached after | ~15 s GPU (4 Gemma calls) |
| **Dependency footprint** | None (librosa already used) | Demucs (already installed) | Gemma multimodal (already installed) |
| **Baila Δ** | −0.009 | −0.012 | false 0.300 (all-YES) |
| **Filomena Teu Toque Δ** | +0.002 | +0.014 | false 0.300 (all-YES) |
| **All Of Me Δ** | −0.003 | −0.012 | not probed |
| **Above-gate regressions** | 0 (some Δ < 0, none drops) | 0 (some Δ < 0, none drops) | N/A (false signal) |
| **Above-gate net change** | 6→6 | 6→6 | N/A |
| **Maintenance** | Low (one helper) | Medium (new module + cache) | Low (constants) |
| **Recommendation** | **Shelve** | **Shelve** | **Close permanently** |

## What worked

- **Fail-safe flags** kept all three options from shipping as defaults. The eval was non-destructive.
- **Option 1's synthetic test** validated the HPSS hypothesis in isolation — the percussive component does produce a more peaked kick-band vector on synthetic data. The hypothesis just doesn't translate to the real kizomba tracks where the problem is the kick signal itself being weak, not the harmonic bleed diluting it.
- **Option 2** showed some interesting secondary effects: Curticão +0.057, Bonga +0.026, Don Kikas +0.029. These are still far from the gate, but they suggest Demucs drum separation does extract a cleaner signal on tracks with a stronger drum kit. It's just not the right tool for the three stuck tracks whose percussion is genuinely ambiguous.
- **Option 3** produced a clean A/B between v1 (all-NO) and v2 (all-YES), definitively closing the prompt-iteration angle: the problem is model competence, not prompt wording.

## What did not / limitations

- **All three options produced ≤ ±0.014 movement on the three target tracks.** None came close to the 0.25 gate. The fundamental problem is that Baila, Filomena Teu Toque, and All Of Me have genuinely weak, ambiguous rhythmic cues for automatic downbeat detection — the kick is soft, the on-beat pattern is inconsistent, and no amount of spectral isolation recovers a signal that doesn't exist in the audio.
- **HPSS margin tuning was not explored.** Margin=2.0 was a reasonable starting point (wider than the section-features margin=1.0) but other values might shift results. Given the magnitude of the problem (target tracks at ~0.02–0.04 vs gate at 0.25), margin tuning is unlikely to close the gap.
- **Demucs drum separation** on the stuck tracks may have been hurt by source bleed — kizomba drum patterns are often synthesized with soft attack, which Demucs's `htdemucs` model (trained mostly on rock/pop) may not separate cleanly.

## Decision / takeaway

- **Shelve all three options.** None produces meaningful uplift on the target tracks. The off-by-default flags remain in the code for future reference but should not be activated.
- **Close the B2 tiebreaker path permanently.** Two prompt variants (v1: all-NO, v2: all-YES) plus two clip positions (intro, 50%) exhausted the reasonable parameter space. Gemma E4B cannot discriminate phrase boundaries in kizomba music.
- **Reframe the problem.** The three stuck tracks' downbeat confidence is low because their rhythmic cues are genuinely ambiguous — not because of signal processing noise. Possible future directions:
  1. **Style-specific confidence gating** — lower the gate for kizomba tracks where the user has provided a style hint, accepting lower-confidence offset estimates that are still better than the default `beat[0]`.
  2. **User-assisted offset** — let the user tap the "1" once and lock the grid.
  3. **Larger / music-specialized models** — a Gemma 26B or 31B model, or a purpose-built music downbeat model, might succeed where E4B's speech-oriented front-end failed.
  4. **Multi-feature fusion** — combine onset, kick, template, and harmonic ratio signals with learned weights rather than hand-tuned fusion.

## Next step

The most practical immediate move is **style-specific confidence gating** (direction 1 above). When the user says "kizomba", the system could accept offset estimates at confidence ≥ 0.01 instead of 0.25, treating any non-zero DSP signal as better than the `beat[0]` default. This doesn't improve the underlying signal quality but closes the user-facing gap: the phrase grid would at least use the DSP's best guess instead of always defaulting.

The user should **keep the Commit A2 baseline as-is** and move to Phase 15 (style-gating or user-tap) rather than continuing to search for a preprocessing solution to what is fundamentally a signal-doesn't-exist problem.
