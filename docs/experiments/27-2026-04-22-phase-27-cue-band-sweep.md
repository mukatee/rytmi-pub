# Phase 27 — Cue-band & backtrack sweep for the kizomba beat tracker

**Date**: 2026-04-22
**Status**: Negative result — no production change shipped.

## Goal

After Phase 26 made listening-note ground truth a real artefact, the user
ran [notebooks/07_kizomba_tutor.ipynb](../../notebooks/07_kizomba_tutor.ipynb)
end-to-end and reported:

- Beats are *off by a small constant amount* relative to the perceived
  step (visible in [notebooks/06_kizomba_batida_check.ipynb](../../notebooks/06_kizomba_batida_check.ipynb)).
- The 26B tutor output is bland.

Phase 27 only addressed the beats. The hypothesis was that the constant
offset comes from picking the wrong **cue band** — the current Phase 25
tracker low-passes at 150 Hz to follow the kick, but the perceived step
might be cued by something brighter (snap, clave, rim) or by the
broadband percussive layer. A secondary hypothesis was that the offset
comes from `librosa.onset.onset_backtrack` being too aggressive
(or not aggressive enough) for kizomba.

## Hypothesis

If the constant offset is band-driven, swapping the input filter
should pull beats closer to the purple ✕ listening notes for both
Baila Kizomba Amor and Teu Toque, *without* increasing miss/extra count.
A clean winner — better mean_ms AND not worse miss/extra on both tracks
— would be ported back into `_track_kizomba_batida`.

## What changed

No production code was changed. All work is in the eval/diag tools.

- [scripts/eval_kizomba_beats.py](../../scripts/eval_kizomba_beats.py) —
  added `BeatConfig`, `compute_beats(audio, config)`, a small `CONFIGS`
  registry, `--config NAME` and `--sweep` flags, a `mean_signed_ms`
  metric (sign reveals lag direction), and a per-track `analyze()`
  cache so the sweep doesn't re-do the heavy DSP for every config.
- Configs swept: `current` (mirror of production), `low_b8` (tighter
  backtrack cap, ~75 ms), `low_b2` (looser, ~300 ms), `low_no_bt`
  (no backtrack), `mid` (200–800 Hz band), `high` (1.5–6 kHz band),
  `perc` (HPSS percussive), `shift_30/50/75` (constant negative
  perceptual shift on the production beats).
- [tests/test_eval_kizomba_beats.py](../../tests/test_eval_kizomba_beats.py)
  — added `test_configs_registry_has_current_mirror` and
  `test_compute_beats_runs_on_synthetic`.
- [notebooks/06_kizomba_batida_check.ipynb](../../notebooks/06_kizomba_batida_check.ipynb)
  — added a "Phase 27 multi-band onset diagnostic" cell that overlays
  4 candidate band onsets stacked above the wave, restricted to the
  listening-note window, with the ✕ marks for direct comparison.

## Evidence

Full sweep saved to [tmp/phase27_sweep.txt](../../tmp/phase27_sweep.txt).
`pytest -q` was 357 passed, 1 skipped after the changes (up from 355,
from the two new sweep tests).

Sorted by `mean_ms` (lower = beats closer to ✕ on average):

```
config            mean_ms  sign_ms  miss extra   n
-----------------------------------------------------
shift_30            131.1    -29.0    23    22   2
low_b8              132.4    +14.8    25    25   2
shift_50            133.4    -21.1    24    23   2
production          134.3    -25.3    21    21   2   ← baseline
current             134.3    -25.3    21    21   2
mid                 134.3    -25.3    21    21   2
shift_75            138.4    -46.1    25    24   2
high                140.5    -25.4    31    17   2
low_no_bt           141.3    +59.0    26    25   2
perc                148.8    -10.9    34    19   2
low_b2              162.8    -59.2    29    28   2
```

Per-track signed offsets (production):
- Baila Kizomba Amor: **−33.7 ms** (beats land before ✕)
- Filomena Maricoa — Teu Toque: **−16.9 ms** (mild)

## What worked

- **The signed metric was the most useful addition.** It confirmed that
  the offset is consistently *negative* — beats land before perceived
  steps — which agrees with the user's report.
- **The sweep harness with per-track caching** runs the full grid in
  ~3 minutes. It will generalize to any future kizomba DSP knob.
- **The multi-band notebook cell** lines up onsets visually so future
  rhythm-tuning work can sanity-check by eye before running numbers.

## What didn't work / limitations

1. **No band/backtrack config beats baseline on the joint metric.**
   - `low_b8` improves mean_ms by 1.9 ms but adds 4 misses and 4 extras.
   - `shift_30` improves mean_ms by 3.2 ms but adds 2 misses and 1 extra.
   - Both cases trade alignment quality for *fewer beats inside the
     100 ms tolerance window* — that's a regression on the metric users
     care about.
2. **`mid` is bitwise identical to `low`.** Same 134.3 mean_ms, same
   miss/extra, same beat counts. The 600 ms `wait_ms` floor swamps band
   choice — the same N kick events get picked regardless of where the
   onset envelope's energy comes from. Band sweeps inside the current
   peak-pick architecture are essentially powerless.
3. **The "constant" offset isn't constant across tracks.** Baila is
   −33.7 ms, Teu Toque is −16.9 ms — a 17 ms spread. A single fixed
   shift can't fix both.
4. **`high` and `perc` make per-track signed offsets explode in
   opposite directions** (e.g. `high`: Baila −114 ms, Teu Toque +63 ms),
   while keeping the average near production. The mean is misleading
   here; the variance grew.
5. Only 2 listening-noted tracks. A third (Bonga) would help guard
   against overfitting.

## Decision

**Skip P3 (no production change).** The current `_track_kizomba_batida`
is at or near the ceiling of what the band/backtrack/shift family can
do on these tracks. Further improvement needs a different architecture
(beat-DNN like madmom, or a beat-aware transformer), which is out of
scope for the hackathon timeline.

## Next step

Phase 28 — make the tutor (`QUESTION_KIZOMBA_TUTOR`) less bland. The
user feedback was *both* "beats off" and "tutor bland", and we now know
the beats can't easily be improved with DSP knobs. The bland tutor
output is therefore the more leveraged thing to fix.

Concrete plan for Phase 28:

- Inject actual numeric `beat_clarity` per phrase into the prompt
  (current prompt only sees subtle/moderate/clear *labels*).
- Ask Gemma to *rank* phrases by clarity rather than to describe each.
- Re-test against the same kizomba tracks via notebook 07.

If Phase 28 lands and beat alignment still hurts user trust, the
follow-up would be to bring in a learned beat tracker (madmom RNN +
DBN postprocessor) as a second `dance_style="kizomba_dnn"` variant.
