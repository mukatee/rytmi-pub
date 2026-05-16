# 2026-04-21 — Phase 25 kizomba batida tracker (LPF + min-gap)

## Goal
Stop the default `librosa.beat.beat_track` from doubling kizomba beats onto
syncopated snares/hats. Land the green dashed beats on the actual kick step
pulse for kizomba/urban_kiz tracks while leaving every other style byte-identical.

## Context / prior state
- `analyze()` always called `librosa.beat.beat_track` on the full-spectrum
  signal, with no style-aware path.
- On kizomba tracks (Baila, Teu Toque, Mona Ki Ngi Xica, ...) it locked at
  ~140–190 BPM, double the perceived ~95 BPM step pulse.
- `extract_kizomba_batida` (an earlier prototype) existed in `dsp.py` but was
  not wired into the pipeline.

## Hypothesis
Restricting onset evidence to the kick band (~0–150 Hz) and forcing a minimum
gap close to the expected step interval (~600 ms) collapses the snare/hat
syncopation noise and leaves the slow kick pulse as the dominant peak — so a
simple `peak_pick` on that envelope is enough.

## What changed
- `src/rytmi/dsp.py`
  - New constants: `_KIZOMBA_BATIDA_LPF_HZ=150`, `_KIZOMBA_BATIDA_WAIT_MS=600`,
    `_KIZOMBA_BATIDA_DELTA_PCT=70`, `_KIZOMBA_BATIDA_HOP=512`,
    `_KIZOMBA_STYLES={"kizomba","urban_kiz"}`.
  - New `_track_kizomba_batida(audio)`: 4-pole Butterworth LPF →
    `onset_strength` (median-aggregated) → `util.peak_pick` with
    `wait=wait_frames` and `delta=percentile(env, 70)`. Tempo from
    `60 / median(diff(beat_times))`.
  - `track_beats(audio, dance_style=None)` branches on `dance_style ∈
    _KIZOMBA_STYLES`; non-kizomba path is the original librosa call, byte-identical.
  - `analyze()` threads `dance_style` into `track_beats`.
  - Removed unused `extract_kizomba_batida` prototype.
- `tests/test_dsp.py`
  - `_synthetic_kizomba_audio()` helper (95 BPM 80 Hz kick + 190 BPM 600 Hz syncopation, 20 s).
  - `test_track_beats_unchanged_for_non_kizomba` — regression: `None`,
    `"bachata"`, `"salsa"`, `"unknown_style"` all produce identical output to
    the no-arg call.
  - `test_track_beats_kizomba_uses_batida_path` — tempo lands in `[80, 110]`
    on the synthetic kizomba.
  - `test_track_beats_urban_kiz_matches_kizomba` — both styles route to the
    same tracker.
- `tmp/run_kizomba_batida_trials.py` — sweeps cutoff × wait × delta on 11
  kizomba tracks + 2 bachata negative controls (kept as the source of the
  locked params; ran a few times during tuning).
- `notebooks/06_kizomba_batida_check.ipynb` — visual + audio validation:
  side-by-side OLD vs NEW interactive timelines (scroll + play + cursor) per
  track, numbered per-measure onset labels color-coded by beat proximity
  (orange = within 60 ms of a downbeat, green = within 60 ms of any beat,
  grey = between beats), and **blue ▼ markers** above the wave on the NEW
  timeline showing kick-band onset candidates the tracker actually picks
  from.

## Evidence / test results
- `pytest`: 345 passed, 1 skipped (full suite).
- `ruff check src tests`: 5 pre-existing F841 warnings in untouched lines, no
  new findings.
- Trial sweep on 11 kizomba tracks (`tmp/run_kizomba_batida_trials.py`):
  with `cutoff=150 Hz`, `wait_ms=600`, `delta_pct=70`, all kizomba tracks land
  at ~95.7 BPM (median IBI ≈ 0.626 s); bachata negative controls (Romeo
  Santos – Propuesta Indecente etc.) stay on their default tracker because
  they are dispatched with `dance_style="bachata"`.
- Notebook 06 smoke test (`Baila_Kizomba_Amor`):
  - OLD: `tempo=143.6 BPM | beats=737`
  - NEW: `tempo= 95.7 BPM | beats=502`
  - kick candidates surfaced for the ▼ overlay: 197 (≈ one every 0.6–1.1 s).

## What worked
- `wait_ms=600` is the dominant lever. Cutoff (100–200 Hz) and delta
  percentile (60–80) barely change which peaks are picked once the gap is
  forced.
- The LPF + median-aggregated `onset_strength` envelope is dominated by the
  kick transient; `peak_pick` with the percentile threshold doesn't need any
  additional gating.
- Style gating (`_KIZOMBA_STYLES`) keeps the bachata/salsa/none paths
  byte-identical, so no risk of regressing the rest of the eval set.

## What did not work / limitations
- Tempo is computed from `median(diff(beat_times))`, so very sparse picks at
  the start/end of a track can pull the median; not seen on the eval set so
  far but worth keeping in mind.
- The blue ▼ overlay in notebook 06 uses a candidate envelope (`wait_ms=120`
  + a rectified-LPF framewise-max envelope) that is *similar but not identical*
  to the DSP envelope (`onset_strength`). It is for visual sanity-checking,
  not a ground truth.
- The tracker is unconditional once `dance_style ∈ {kizomba, urban_kiz}`. If
  a track is mis-tagged, it will be force-tracked at ~95 BPM. Mitigation
  belongs to the style-tagging path, not here.
- Phrase/downbeat detection still runs on top of these beats with the
  existing logic; we didn't tune downbeat offset for the new beat grid yet.

## Decision / takeaway
Ship this gated tracker for kizomba/urban_kiz. Keep the non-kizomba path
unchanged. The 150 Hz / 600 ms / 70 % triplet is now treated as locked.

## Next step
- Spot-check the notebook visually on all 11 eval kizomba tracks (the
  notebook subset list is editable).
- If the green dashed beats land on the blue ▼ markers consistently, look at
  whether the existing downbeat-offset picker still chooses the "1" sensibly
  on the new beat grid. If not, that becomes its own phase.
- Consider extending the same LPF + min-gap approach to other slow,
  kick-driven styles (zouk, semba) once they have eval coverage.
