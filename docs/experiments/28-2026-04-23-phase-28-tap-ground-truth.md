# Phase 28 — tap-based ground truth for kizomba beat alignment

**Date:** 2026-04-23 (initial); P5d follow-up 2026-04-26.
**Status:** complete. Production tracker improved from F=0.587 → F=0.678 on 19 tap takes (+15 pp pooled F) via two changes: (1) fix all-zero kick envelope from default `n_mels=128` mel filterbank against a 150 Hz LPF, (2) lower `_KIZOMBA_BATIDA_WAIT_MS` from 600 ms → 450 ms.
**Predecessor:** [Phase 27 — cue-band sweep](./27-2026-04-22-phase-27-cue-band-sweep.md) (negative result).

## Goal

Phase 27 showed that the kizomba batida tracker has a per-track signed
offset (Baila −33.7 ms, Teu Toque −16.9 ms vs the listening notes) that
no fixed shift can cancel because the offsets diverge across tracks. It
also showed band selection inside the existing peak-pick architecture
is powerless — `mid` was bitwise identical to `low` because the
`wait_ms=600` floor dominates which events are picked.

Two hypotheses fall out of that:

1. The "constant offset" the user feels in notebook 07 may not be the
   detector — it may be the **listening notes themselves** drifting,
   since they were marked once by ear without any per-tap consensus.
2. If the offset is real, it's per-track and can only be reduced by
   changing **which** events the picker chooses, not by post-shifting
   them. Envelope-fusion across bands is the next thing worth trying.

Phase 28 builds the infrastructure to settle (1) by replacing the
single hand-marked notes with **multi-take consensus tap tracks**, and
runs a first round of (2) via `multiband_sum` against listening notes.

## What changed

| Area | Change |
| --- | --- |
| Diagnostic | `notebooks/06_kizomba_batida_check.ipynb` — new cell (`_band_envelope` + `diag_envelope_stack`) renders per-band onset envelopes (low/mid/high/HPSS-perc) overlaid on the listening notes, so the picker's view of each kizomba track is inspectable. |
| Capture | `src/rytmi/eval/tap_capture.py` — `TapTake` dataclass + `save_take` / `load_take` / `load_takes` JSON I/O + `tap_recorder()` ipywidgets recorder (TAP button, focus + Space, Save/Reset). |
| Capture UI | `notebooks/08_tap_capture.ipynb` — one cell per track for Baila / Teu Toque / Bonga; rerun with `take="take_2"`, etc. for additional takes. |
| Aggregation | `src/rytmi/eval/tap_consensus.py` — `consensus(takes, agree_window_ms, min_agree)` symmetric multi-take fusion (drops outliers), `correct_tap_latency`, `estimate_user_latency` (for metronome calibration). |
| Eval | `scripts/eval_kizomba_beats.py` — new `multiband_sum` / `multiband_sum_b8` configs (sum of normalized low/mid/high envelopes before peak-pick) and `--reference taps\|notes` (+ `--taps-root`, `--tap-latency-ms`, `--tap-agree-window-ms`, `--tap-min-agree`). |
| Tests | `tests/test_tap_capture.py` (6) + `tests/test_tap_consensus.py` (8) + extension to `tests/test_eval_kizomba_beats.py`. Total: **371 passed, 1 skipped** (was 357). |

## Evidence

### Notes-reference sweep (no taps needed)

`tmp/phase28_sweep_notes.txt`, sorted by `mean_ms`:

```
config            mean_ms  sign_ms  miss extra   n
shift_30            131.1    -29.0    23    22   2
low_b8              132.4    +14.8    25    25   2
shift_50            133.4    -21.1    24    23   2
production          134.3    -25.3    21    21   2
current             134.3    -25.3    21    21   2
mid                 134.3    -25.3    21    21   2
shift_75            138.4    -46.1    25    24   2
high                140.5    -25.4    31    17   2
multiband_sum       140.5    -25.4    31    17   2
multiband_sum_b8    140.5    -25.4    31    17   2
low_no_bt           141.3    +59.0    26    25   2
perc                148.8    -10.9    34    19   2
low_b2              162.8    -59.2    29    28   2
```

Two findings:

* `multiband_sum` is **bitwise identical** to `high`. Per-band
  normalization (each envelope ÷ its own max) plus the broad spiky
  content of the high band means the sum is dominated by hi-hat-like
  energy, and at `wait_ms=600` the picker selects the same N events as
  if it had run on `high` alone. **Envelope fusion alone does not
  defeat the wait-floor bottleneck** — same lesson Phase 27 learned for
  band swapping.
* No notes-reference config beats `production` on misses+extras. The
  best `mean_ms` (`shift_30`, 131.1) trades 2 ms for 2 extra misses and
  1 extra extra. Consistent with Phase 27.

### Tap-reference sweep

Pending: requires running `notebooks/08_tap_capture.ipynb` (≥3 takes
per track for Baila / Teu Toque / Bonga, optional metronome
calibration). Then:

```bash
python scripts/eval_kizomba_beats.py --sweep --reference taps \
    --tap-latency-ms <est_from_calibration> > tmp/phase28_sweep_taps.txt
```

## Decision

* **Do not ship** `multiband_sum` to production based on the
  notes-reference sweep — it is no better than `high` and worse than
  `production` on the metric the user actually cares about (combined
  miss+extra count).
* **Hold** the production constants (`_KIZOMBA_BATIDA_*` in
  `src/rytmi/dsp.py`) at their Phase 27 baseline. Tag
  `phase27-baseline` is the rollback point.
* **Promote** `multiband_sum` only if the tap-reference sweep shows
  it wins on ≥2 of {Baila, Teu Toque, Bonga}, **and** the per-track
  signed offsets converge (i.e. the picker stops drifting per-track).
  Otherwise the picker — not the envelope — is the next thing to
  redesign.

## Limitations

* The notes-reference half is **two-track only** (Baila + Teu Toque);
  Bonga has no listening notes. Bonga only enters once tap takes exist.
* `multiband_sum` collapses to `high` because each band is normalized
  independently. A natural next variant is *un-normalized* sum, or
  weighted sum that down-weights bands with too many peaks; both are
  cheap to add as new `BeatConfig` entries.
* `tap_recorder()` is the only Jupyter-coupled bit and is **not unit
  tested**. The recorder uses `time.perf_counter()` between TAP
  button clicks, so OS scheduler jitter (~1–5 ms) is a noise floor on
  top of the user's own tap jitter.
* No `sounddevice`/`ipyevents` were used — the spacebar path relies on
  HTML button focus. If browser focus is lost between taps the user
  has to click the button instead. Acceptable trade-off vs writing a
  fragile JS-keypress bridge.

## Next

1. Record taps in `notebooks/08_tap_capture.ipynb` (3 takes × 3 tracks
   + 1 calibration take if a metronome track is added).
2. Run the tap-reference sweep; compare the per-config signed offsets
   between `--reference notes` and `--reference taps`. If signed
   offsets converge to ~0 ms across tracks under taps, the listening
   notes were the source of the constant-offset feeling — and the
   picker is fine. If they stay divergent, try the un-normalized
   `multiband_sum` variant and an `wait_ms` sweep.
3. Decide whether to ship anything to `_track_kizomba_batida`. Either
   way, write a follow-up note here.

---

## P5 follow-up (2026-04-26): real fix found

After the infrastructure landed and the first tap takes were recorded
(19 takes across the 5 kizomba tracks), an `lrel_alpha` (local-relative
threshold) prototype produced bizarrely identical results across every
config variant. Diagnosing that uncovered a much bigger bug.

### P5d — the mel-filterbank bug (commit `1b879ab`)

`_track_kizomba_batida` was a wait-time metronome the whole time since
Phase 25. The pipeline is `audio → 150 Hz LPF → onset_strength → peak_pick`.
The LPF strips everything above 150 Hz; `librosa.onset.onset_strength`
defaults to a mel-spectrogram with `n_mels=128, fmin=0, fmax=sr/2`,
which on a 22050 Hz / 44100 Hz signal places the **lowest mel bin
centre at ~80 Hz** and the next ones above. Result: the LPF input has
no energy in any mel bin, the envelope is flat zero, and `peak_pick`
falls back to firing exactly once per `wait_ms` ms (`_KIZOMBA_BATIDA_WAIT_MS=600`).

The symptom that everyone had been seeing for weeks — 'beats are
periodic at 627 ms regardless of band swap' — was the picker emitting
on its `wait_ms` floor against a zero envelope. Verified with
`pylanceRunCodeSnippet`: `env.max() == 0.0`, `env[beat_frames]` all
zero, librosa silently emits an 'Empty filters detected in mel
frequency basis' UserWarning.

**Fix:** pass `fmin=20.0, n_mels=8, fmax=hi*1.5` to `onset_strength`
whenever the input is band-limited below ~80 Hz. With those settings
the filterbank actually has bins in the kick range. The fix was applied
in one place initially and then audited across the codebase.

### P5d audit — same bug everywhere (commit `ece8b1e` + `2699c7a`)

Grepped every `librosa.onset.onset_strength` call site:

| Site | State | Action |
| --- | --- | --- |
| `dsp.py::_track_kizomba_batida` | broken (zero env) | fixed in `1b879ab` |
| `dsp.py::_low_band_beat_position_strengths` (40–150 Hz BPF) | broken (zero env feeding `detect_downbeats` template scoring) | fixed |
| `dsp.py` Demucs bass-stem branch in `detect_downbeats` | suboptimal (~3× weaker envelope vs fixed) | fixed |
| `dsp.py` 40–150 Hz fallback when bass stem missing | broken | fixed |
| `notebooks/06_kizomba_batida_check` `kick_onset_times` | broken (overlay was a wait-time metronome) | fixed |
| `notebooks/06_kizomba_batida_check` `_band_onsets` low branch | broken | fixed |
| `notebooks/06_kizomba_batida_check` `_band_envelope` low branch | broken (the 'low' envelope panel was flat zero) | fixed |
| `dsp.py::_mid_high_band_beat_position_strengths` (1–4 kHz) | safe — well above the mel `fmin` cliff | none |
| `compute_onsets`, `compute_beats`, `_compute_novelty_curve` | safe — full-spectrum input | none |

Real impact: `_low_band_beat_position_strengths` is in the live
`detect_downbeats` path, so the kick-band evidence channel had been
contributing **zero** for downbeat scoring this whole time. Phase 10's
'kick-drum band vote' design was sound; the implementation was silently
broken by the same gotcha.

### P5d wait_ms re-sweep — production bumped (commit `5473ac9`)

With the envelope finally real, the `wait_ms` trend reversed. The old
sweep had said 'tighter is worse' because tighter `wait_ms` against a
zero envelope just produced more false metronome ticks. Post-fix:

```
wait_ms  F (pooled, 19 takes, 5 tracks)
  600   0.587   (Phase 25 default, was prod)
  450   0.678   (+15 pp)   <- new prod
  400   0.623
  350   0.487
  300   0.470
  250   0.436
```

`_KIZOMBA_BATIDA_WAIT_MS` is now **450**. Visual confirmation in nb6
on Baila Kizomba Amor: triangles + envelope spikes were both visible
at real kick locations, but at the 600 ms gap the picker was forced
to skip every other one. At 450 ms those previously-skipped picks
come through.

### P5d follow-up sweeps — both null (commit `f7814fc`)

Two questions remained after the wait_ms bump:

**(a) Re-test `lrel_alpha`** now that the envelope is real (built on the
new `low_w450` baseline, F=0.678):

```
lrel_a30   F=0.673   (miss=317, extra=600)
lrel_a40   F=0.654   (miss=381, extra=550)
lrel_a50   F=0.632   (miss=461, extra=470)
lrel_a60   F=0.602   (miss=542, extra=409)
lrel_a70   F=0.566   (miss=621, extra=362)
```

Does what it advertises (extras drop monotonically), but prunes real
beats faster than false picks. The kick envelope's local-relative
profile doesn't separate 'real kick' from 'filler' cleanly enough on
these tracks. Wider lrel windows (900 ms, 1200 ms) also lose. Plumbing
left in `BeatConfig` for future bands; not used in production.

**(b) `backtrack_div` neighborhood** (the prior sweep had `low_b8`
+0.4 pp ahead of default):

```
low_b2   F=0.678          low_b10  F=0.652   <- saturation
default  F=0.678  (b4)    low_b12  F=0.652   identical to b10
low_b6   F=0.679          low_b16  F=0.652   identical to b10
low_b8   F=0.682  +0.4pp
```

`b2 / b4 / b6 / b8` cluster within 0.4 pp; `b10+` collapse to identical
worse numbers (likely an internal window clamp in `librosa.onset.onset_backtrack`).
No real trend; production stays at `b4`.

### Final verdict

Production `_track_kizomba_batida` is now `low_w450` with the fixed
envelope: F=0.678 pooled across 19 tap takes (vs F=0.587 pre-fix).
The picker is no longer a wait-floor metronome — it picks real kicks
with a 450 ms gap.

What the 'next' list above said to do (multiband_sum un-normalized
variant, picker redesign) is no longer the priority. The picker was
fine; the **input** was the bug. Things that still might pay off but
are lower priority:

* Expand the tap reference set — F=0.678 on n=5 tracks is a believable
  but small sample. Adding 5 more tracks would tighten the wait_ms /
  backtrack reads.
* Investigate why the listening notes (purple ✕ in nb6) drift relative
  to the new (clearly correct) green dashed beats. The notes were
  hand-marked once and may use a different reference grid than
  `notes_to_times` resolves against now.
* Apply the same audit pattern (`fmin / n_mels` on band-limited
  `onset_strength` inputs) anywhere new low-band DSP gets added.
