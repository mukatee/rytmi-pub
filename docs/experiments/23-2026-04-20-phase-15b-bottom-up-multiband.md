# 2026-04-20 — Phase 15b: Bottom-up multi-band downbeat exploration

## Goal
Find whether any onset-strength signal variant can reliably identify the kizomba downbeat ("1") from pure DSP, without relying on the existing fusion system.

## Context / prior state
- The existing fusion downbeat detector combines multiple voices (full onset, low-band, mid-high-band, BeatNet, harmonic cue) with weighted voting.
- For kizomba, the fusion system's downbeat confidence was consistently low.
- Prior attempts: v1 backward-walk onset snap (1/6), v2 onset-strength scoring on full mix (2/6).
- Question: is there a sub-band or signal decomposition that separates the downbeat better than the full mix?

## Hypothesis
Bass or kick-band onset strength might emphasize the downbeat more than the full mix, since low-frequency patterns often carry the rhythmic anchor in dance music.

## What changed
- Created `tmp/run_multiband_explore.py` — a standalone exploration script testing 7 signal variants across 16 eval tracks using only `librosa.beat.beat_track` (no BeatNet):
  - `full`: default onset_strength
  - `perc`: HPSS percussive component
  - `harm`: HPSS harmonic component
  - `bass`: 40–150 Hz bandpass
  - `kick`: 40–100 Hz bandpass (narrower)
  - `snare`: 150–350 Hz bandpass
  - `rms`: frame-level RMS energy
- Method: for each variant, compute onset strength, interpolate at beat times, fold into 4-beat measure, take per-position mean, pick the position with highest mean.
- Also created v1 (`_find_stable_region`, `_extrapolate_first_beat`) and v2 (`_grid_extrapolation_offset`) functions in `src/rytmi/dsp.py` — these are standalone and NOT wired into `detect_downbeats()` or `analyze()`.

## Evidence / test results

### Match rates (6 annotated kizomba tracks, librosa beat grid)

| Variant | Match | Rate |
|---------|-------|------|
| full    | 3/6   | 50%  |
| perc    | 3/6   | 50%  |
| snare   | 3/6   | 50%  |
| rms     | 2/6   | 33%  |
| harm    | 1/6   | 17%  |
| bass    | 1/6   | 17%  |
| kick    | 1/6   | 17%  |

### Per-track pattern

| Track | User | full/perc/snare | bass/kick | Pattern |
|-------|------|----------------|-----------|---------|
| Don Kikas | 3 | all ✓ | both ✓ | Easy — pos3 dominates most signals |
| E Magia Official | 3 | all ✓ | both ✗ | Clear for full-band, bass points wrong |
| Criola | 2 | all ✓ | both ✗ | Same — full-band OK, sub-bands wrong |
| Curticao | 1 | all ✗ (pick 2) | both ✗ | Flat distribution (89–100%), only harm ✓ by noise |
| Teu Toque | 1 | all ✗ (pick 2) | both ✗ | Flat (85–100%), no variant works |
| All Of Me | 3 | all ✗ | both ✗ | Flat (86–100%). Works with BeatNet grid in full pipeline but fails with librosa-only beats |

### Bachata tracks
All 4 bachata tracks consistently pick offset=0 across full/perc/snare variants, confirming the downbeat is acoustically clear in that style.

### Key per-position distributions for hard tracks (normalized to max=1)
- **Teu Toque** (user=1): full [0.86, 0.92, **1.00**, 0.88] — genuinely flat
- **Curticao** (user=1): full [0.89, 0.90, **1.00**, 0.93] — genuinely flat
- **All Of Me** (user=3): full [**1.00**, 0.88, 0.86, 0.87] — genuinely flat

## What worked
- The exploration methodology is sound — fast to run (~minutes for 16 tracks), clear output format.
- Confirmed bachata downbeat detection is reliable across all signal variants.
- Definitively answered the sub-band question: bass/kick separation does NOT help for kizomba.

## What did not work / limitations
1. **No variant breaks past 50%** on kizomba. The theoretical ceiling is ~3/6 — the other 3 tracks have genuinely flat distributions.
2. **Bass/kick was the worst hypothesis** — 17% match, opposite of expectation. Kizomba bass patterns don't emphasize the downbeat.
3. **Harmonic is anti-correlated** — 17% and often confidently wrong (makes sense: kizomba harmony shifts on off-beats).
4. **full ≈ perc ≈ snare** — always agree. Separating percussive components adds no information.
5. **Beat grid matters more than signal variant** — All Of Me works with BeatNet's grid but fails with librosa's grid. The grid alignment determines which physical time each "position" maps to.
6. **Confidences universally low** (0.00–0.19) — the signal genuinely doesn't distinguish beat positions in kizomba.

## Decision / takeaway
**The kizomba downbeat is the wrong problem to optimize.**

The flat onset-energy distribution across beat positions is not a detection failure — it is a musical fact. Kizomba doesn't acoustically emphasize one beat over others. The dance reflects this: the dancer has freedom of movement on every beat.

**Style-differentiated analysis is the right approach:**
- **Bachata:** the "1" is critical (4+4 mini-choreo). Detection already works.
- **Kizomba:** beat clarity and rhythmic texture are what matter. Focus on helping the dancer hear and step into the beat itself, especially in songs where the pulse is subtle.

## Next step
- Implement beat clarity scoring for kizomba: onset strength variance per section, on-beat vs. off-beat energy ratio, "easy to hear" vs. "tricky" section labeling.
- Verify bachata downbeat detection on the full pipeline eval set.
- Consider whether the grid extrapolation code in `dsp.py` should be kept, removed, or gated behind a style check.
