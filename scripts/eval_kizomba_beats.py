#!/usr/bin/env python3
"""Evaluate the kizomba beat tracker against hand-marked listening notes.

For each track in ``data/eval/kizomba_listening_notes.yaml`` whose audio
is found under ``data/songs/eval_set/kizomba/``, this script:

  1. Runs ``analyze(audio, dance_style="kizomba")``.
  2. Resolves listening notes to times via ``notes_to_times``.
  3. Reports three metrics, scored only over the time window the
     listening notes cover (padded by ``--window-pad-s`` on each side):

     * ``mean_ms``  — for each tracked beat in the window, distance to
       the nearest listening note; mean over those beats. (Lower =
       beats sit closer to perceived steps.)
     * ``misses``   — listening notes with no in-window tracked beat
       within ``--tol-ms`` (default 100 ms).
     * ``extras``   — in-window tracked beats with no listening note
       within ``--tol-ms``.

These are the regression baseline: if a future change makes any of them
worse on these tracks, that's a real regression.

Usage:
    python scripts/eval_kizomba_beats.py
    python scripts/eval_kizomba_beats.py --tol-ms 80
    python scripts/eval_kizomba_beats.py --config mid_b150
    python scripts/eval_kizomba_beats.py --sweep
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

import librosa
import numpy as np
from scipy.signal import butter, filtfilt

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rytmi import analyze, load_audio  # noqa: E402
from rytmi.eval.listening_notes import (  # noqa: E402
    TrackNotes,
    load_notes,
    notes_to_times,
)
from rytmi.eval.tap_capture import load_takes  # noqa: E402
from rytmi.eval.tap_consensus import consensus, correct_tap_latency  # noqa: E402
from rytmi.types import AudioData  # noqa: E402

DEFAULT_NOTES = REPO_ROOT / "data" / "eval" / "kizomba_listening_notes.yaml"
DEFAULT_AUDIO_DIR = REPO_ROOT / "data" / "songs" / "eval_set" / "kizomba"
DEFAULT_TAPS_ROOT = REPO_ROOT / "data" / "eval" / "taps"

# --- Sweep configs ---------------------------------------------------------
#
# Each ``BeatConfig`` is a candidate kizomba beat tracker. ``band`` selects
# how the input is filtered before ``onset_strength``:
#
#   ("low",  hi_hz)            — 4-pole Butterworth low-pass at hi_hz
#   ("band", lo_hz, hi_hz)     — 4-pole Butterworth band-pass
#   ("perc", None)             — HPSS percussive component, no extra filter#   ('multiband_sum', None)    — sum of normalized low/mid/high envelopes
#                                 (envelope-fusion before peak-pick)#
# Other knobs mirror ``src/rytmi/dsp.py::_track_kizomba_batida``:
#   wait_ms       — minimum gap between picked beats
#   delta_pct     — percentile of the envelope used as peak threshold
#   backtrack_div — cap on backshift = wait_frames // backtrack_div
#                   (0 means: no backtrack at all)
#
# The ``current`` config must mirror the production constants exactly so
# the sweep includes the live baseline.
_HOP = 512


@dataclass(frozen=True)
class BeatConfig:
    name: str
    band: tuple = ("low", 150.0)
    wait_ms: float = 450.0
    delta_pct: float = 70.0
    backtrack_div: int = 4  # 0 disables backtrack
    shift_ms: float = 0.0  # added to every beat time; -ve pulls beats earlier
    halve: bool = False  # decimate beats by 2, picking the phase whose
    # frames carry more onset-envelope energy. Tests Option A from the
    # Phase 28 diagnostic: when DSP runs at ~2× the perceived batida rate,
    # halving + phase-pick should align with tapped beats.
    lrel_alpha: float = 0.0  # if >0, drop a picked beat whose envelope
    # value is below alpha * (local max) inside lrel_window_ms. Real
    # post-pick filter — fights extras without re-tuning wait_ms.
    lrel_window_ms: float = 600.0


# --- Option B (deferred) ---------------------------------------------------
#
# Diagnostic on Baila + Criola showed DSP emits a near-constant 627 ms
# grid (~95.7 BPM) regardless of song. Two interpretations:
#
#   * "DSP is at ~2× the batida rate; halve it" — implemented below as
#     ``halve``. Works when beats/taps ratio is ~2 and phase is wrong.
#   * "DSP and taps are at *different* tempi" — the harder case. Baila
#     taps at ~551 ms (~109 BPM), Criola at ~766 ms (~78 BPM). Neither
#     is exactly half of 627 ms. A real fix here is a *batida extractor*
#     that picks the 2 most syncopated hits per 4-beat measure (i.e.
#     positions 1 and 2.5), instead of a uniform grid. That requires
#     downbeat estimation + per-bar peak ranking and is bigger than the
#     current sweep. Tracked for after we see how (A) and the wait_ms
#     variants below score.
# --------------------------------------------------------------------------


CONFIGS: dict[str, BeatConfig] = {
    "current": BeatConfig(name="current"),
    "low_b8": BeatConfig(name="low_b8", backtrack_div=8),
    "low_b2": BeatConfig(name="low_b2", backtrack_div=2),
    "low_no_bt": BeatConfig(name="low_no_bt", backtrack_div=0),
    "mid": BeatConfig(name="mid", band=("band", 200.0, 800.0)),
    "high": BeatConfig(name="high", band=("band", 1500.0, 6000.0)),
    "perc": BeatConfig(name="perc", band=("perc", None)),
    # Perceptual-shift candidates: same DSP as `current`, but every beat
    # is pulled earlier by a fixed amount. Tests the hypothesis that the
    # constant offset is a perceived-step-vs-audible-attack mismatch
    # rather than a band-choice mismatch.
    "shift_30": BeatConfig(name="shift_30", shift_ms=-30.0),
    "shift_50": BeatConfig(name="shift_50", shift_ms=-50.0),
    "shift_75": BeatConfig(name="shift_75", shift_ms=-75.0),
    # Phase 28 P4: envelope-fusion candidates. The Phase 27 sweep showed
    # that picking on a single band is bottlenecked by the wait_ms=600
    # floor (mid ≡ low). Summing normalized envelopes across bands
    # before peak-pick changes *which* events are picked, not just where.
    "multiband_sum": BeatConfig(name="multiband_sum", band=("multiband_sum", None)),
    "multiband_sum_b8": BeatConfig(
        name="multiband_sum_b8", band=("multiband_sum", None), backtrack_div=8
    ),
    # Phase 28 P5: wait_ms variants. The diagnostic showed beats are
    # almost perfectly periodic at 627 ms (= ~wait_ms=600 floor + a frame
    # of slop), suggesting the picker is locked to the wait floor rather
    # than to musical structure. Lowering wait_ms lets it pick faster
    # batidas; we want to see if F goes up on tap reference.
    "low_w450": BeatConfig(name="low_w450", wait_ms=450.0),
    "low_w400": BeatConfig(name="low_w400", wait_ms=400.0),
    "low_w350": BeatConfig(name="low_w350", wait_ms=350.0),
    "low_w300": BeatConfig(name="low_w300", wait_ms=300.0),
    "low_w250": BeatConfig(name="low_w250", wait_ms=250.0),
    # Phase 28 P5b: at wait_ms=400 the picker fires faster than the
    # 600 ms floor, but more extras come along. Tried raising delta_pct
    # (the global percentile threshold) at d75/80/85/90 — output was
    # *bitwise identical* to delta_pct=70. Reason: peak_pick computes
    # `delta` over the whole envelope (mostly near-zero between hits),
    # so any value high enough to fire under wait_ms=400 already clears
    # even the 90th percentile. The global threshold is dead-weight in
    # this picker. Keeping low_w400_d90 only as evidence.
    "low_w400_d90": BeatConfig(name="low_w400_d90", wait_ms=400.0, delta_pct=90.0),
    # Phase 28 P5c was going to add lrel_alpha configs, but the diagnostic
    # below (rytmi/scripts inline) found the *real* bug: the LPF input to
    # librosa.onset.onset_strength produces an all-zero envelope (mel
    # filterbank has no bins below ~80 Hz at default n_mels=128, and the
    # LPF at 150 Hz leaves nothing above that). All previous sweep results
    # were wait_ms-driven metronomes, not real beat detection. The
    # lrel_alpha plumbing is left in BeatConfig for future use once the
    # envelope is fixed.
    # Phase 28 P5: Option A — halve and phase-pick. The base config is
    # picked first; then we keep every other beat, choosing the phase
    # (even-indexed vs odd-indexed) with higher total envelope energy.
    "halve_low": BeatConfig(name="halve_low", halve=True),
    "halve_low_no_bt": BeatConfig(name="halve_low_no_bt", backtrack_div=0, halve=True),
    "halve_multiband_b8": BeatConfig(
        name="halve_multiband_b8",
        band=("multiband_sum", None),
        backtrack_div=8,
        halve=True,
    ),
    # Phase 28 P5d (post-fix re-run): now that the kick-band envelope
    # is real, retest the local-relative threshold. Drops a picked beat
    # whose envelope value is below alpha * local_max within
    # +/- lrel_window_ms / 2. Pre-fix this killed every beat (zero env
    # > 0 == False everywhere). Post-fix it should prune low-energy
    # picks that the wait_ms=450 picker emits between real kicks.
    # All variants build on the new low_w450 baseline.
    #
    # NULL RESULT (5 tap tracks, post-fix sweep):
    #   baseline (low_w450) F=0.678   (miss=246, extra=720)
    #   lrel_a30            F=0.673   (miss=317, extra=600)
    #   lrel_a40            F=0.654   (miss=381, extra=550)
    #   lrel_a50            F=0.632   (miss=461, extra=470)
    #   lrel_a60            F=0.602   (miss=542, extra=409)
    #   lrel_a70            F=0.566   (miss=621, extra=362)
    # Lrel does what it advertises (extras drop monotonically), but it
    # prunes real beats faster than false picks. The kick envelope's
    # local-relative profile doesn't separate "real kick" from "filler"
    # cleanly enough on these tracks. Wider windows (a50_w900, a50_w1200)
    # also lose. Configs kept as evidence; not used in production.
    "lrel_a30": BeatConfig(name="lrel_a30", wait_ms=450.0, lrel_alpha=0.30),
    "lrel_a40": BeatConfig(name="lrel_a40", wait_ms=450.0, lrel_alpha=0.40),
    "lrel_a50": BeatConfig(name="lrel_a50", wait_ms=450.0, lrel_alpha=0.50),
    "lrel_a60": BeatConfig(name="lrel_a60", wait_ms=450.0, lrel_alpha=0.60),
    "lrel_a70": BeatConfig(name="lrel_a70", wait_ms=450.0, lrel_alpha=0.70),
    "lrel_a50_w900": BeatConfig(
        name="lrel_a50_w900", wait_ms=450.0, lrel_alpha=0.50, lrel_window_ms=900.0
    ),
    "lrel_a50_w1200": BeatConfig(
        name="lrel_a50_w1200", wait_ms=450.0, lrel_alpha=0.50, lrel_window_ms=1200.0
    ),
    # Phase 28 P5d (post-fix re-run): backtrack_div neighborhood. The
    # post-fix sweep showed low_b8 (backtrack_div=8) edged the b4
    # default by 0.4 pp F. Tested b6, b10, b12, b16 to see if there's
    # a real trend or noise on n=5.
    #
    # NULL RESULT (5 tap tracks, post-fix sweep):
    #   low_b2   F=0.678   (miss=246, extra=720)  same as default
    #   default  F=0.678   (b4)
    #   low_b6   F=0.679   (miss=244, extra=718)  +0.1 pp, noise
    #   low_b8   F=0.682   (miss=240, extra=713)  +0.4 pp, noise
    #   low_b10  F=0.652   (miss=285, extra=758)  saturation cliff
    #   low_b12  F=0.652   (identical to b10)
    #   low_b16  F=0.652   (identical to b10)
    # b2/b4/b6/b8 cluster within 0.4 pp; b10+ collapse to identical
    # numbers (likely hitting a window-clamping ceiling in onset_backtrack).
    # No real trend; stay at the b4 default. Configs kept as evidence.
    "low_b6": BeatConfig(name="low_b6", backtrack_div=6),
    "low_b10": BeatConfig(name="low_b10", backtrack_div=10),
    "low_b12": BeatConfig(name="low_b12", backtrack_div=12),
    "low_b16": BeatConfig(name="low_b16", backtrack_div=16),
}


def _filter_audio(audio: AudioData, band: tuple) -> np.ndarray:
    sr = audio.sr
    nyq = 0.5 * sr
    kind = band[0]
    if kind == "low":
        b, a = butter(4, band[1] / nyq, btype="low")
        return filtfilt(b, a, audio.samples).astype(np.float32, copy=False)
    if kind == "band":
        lo, hi = band[1] / nyq, band[2] / nyq
        b, a = butter(4, [lo, hi], btype="band")
        return filtfilt(b, a, audio.samples).astype(np.float32, copy=False)
    if kind == "perc":
        # HPSS percussive component; no extra band filter.
        _, perc = librosa.effects.hpss(audio.samples.astype(np.float32, copy=False))
        return perc.astype(np.float32, copy=False)
    if kind == "multiband_sum":
        # Marker only; the actual fusion happens in compute_beats so it
        # can sum onset_strength envelopes (not raw audio).
        return audio.samples.astype(np.float32, copy=False)
    raise ValueError(f"unknown band spec: {band!r}")


def compute_beats(audio: AudioData, config: BeatConfig) -> np.ndarray:
    """Run the parameterized kizomba batida tracker; return beat times.

    Mirrors ``_track_kizomba_batida`` in ``src/rytmi/dsp.py`` so a winning
    config can be ported back as production constants.
    """
    sr = audio.sr

    if config.band[0] == "multiband_sum":
        # Fuse envelopes across low / mid / high before peak-pick. Each
        # band's envelope is normalized to its own max so a loud kick
        # cannot drown out a clear hi-hat (or vice versa).
        bands = (
            ("low", 150.0),
            ("band", 200.0, 800.0),
            ("band", 1500.0, 6000.0),
        )
        envs = []
        for spec in bands:
            y_b = _filter_audio(audio, spec)
            # See note below: low-band envelopes need fmin + n_mels, or
            # the default mel filterbank produces an all-zero envelope.
            if spec[0] == "low":
                e = librosa.onset.onset_strength(
                    y=y_b, sr=sr, fmin=20.0, fmax=spec[1] * 1.5, n_mels=8,
                    aggregate=np.median, hop_length=_HOP,
                )
            else:
                e = librosa.onset.onset_strength(
                    y=y_b, sr=sr, aggregate=np.median, hop_length=_HOP,
                )
            peak = float(np.max(e)) if e.size else 0.0
            if peak > 0:
                e = e / peak
            envs.append(e)
        # Align lengths (filtfilt + onset_strength can drift by 1 frame).
        n = min(e.size for e in envs)
        env = np.sum([e[:n] for e in envs], axis=0)
    else:
        y = _filter_audio(audio, config.band)
        # For low-passed kick band: fmin=20 + n_mels=8 are essential.
        # The librosa default n_mels=128 places no mel filter below
        # ~80 Hz, so any LPF input below that threshold yields an
        # all-zero envelope (silently — only an "Empty filters" warning).
        # Phase 28 P5d diagnostic; same fix is applied in src/rytmi/dsp.py.
        if config.band[0] == "low":
            env = librosa.onset.onset_strength(
                y=y, sr=sr, fmin=20.0, fmax=float(config.band[1]) * 1.5,
                n_mels=8, aggregate=np.median, hop_length=_HOP,
            )
        else:
            env = librosa.onset.onset_strength(
                y=y, sr=sr, aggregate=np.median, hop_length=_HOP,
            )
    wait_frames = max(1, int(round((config.wait_ms / 1000.0) * sr / _HOP)))
    delta = float(np.percentile(env, config.delta_pct)) if env.size else 0.0
    beat_frames = librosa.util.peak_pick(
        env,
        pre_max=wait_frames // 2,
        post_max=wait_frames // 2,
        pre_avg=wait_frames,
        post_avg=wait_frames,
        delta=delta,
        wait=wait_frames,
    ).astype(np.intp, copy=False)

    if config.lrel_alpha > 0.0 and beat_frames.size:
        # Local-relative threshold: keep a beat only if its envelope
        # value reaches alpha * local_max in a ±window around it.
        # Cuts weak beats sitting next to a much louder neighbour.
        # Done BEFORE backtrack because backtrack shifts frames off the
        # peak, which would make env[beat_frame] underestimate strength.
        win_frames = max(
            1, int(round((config.lrel_window_ms / 1000.0) * sr / _HOP))
        )
        keep = np.zeros(beat_frames.size, dtype=bool)
        n_env = env.size
        for i, f in enumerate(beat_frames):
            lo = max(0, int(f) - win_frames)
            hi = min(n_env, int(f) + win_frames + 1)
            local_max = float(env[lo:hi].max()) if hi > lo else 0.0
            if local_max <= 0.0:
                continue
            keep[i] = float(env[int(f)]) >= config.lrel_alpha * local_max
        beat_frames = beat_frames[keep]

    if beat_frames.size and config.backtrack_div > 0:
        backtracked = librosa.onset.onset_backtrack(beat_frames, env)
        max_backshift = max(1, wait_frames // config.backtrack_div)
        beat_frames = np.maximum(
            backtracked, beat_frames - max_backshift
        ).astype(np.intp, copy=False)

    if config.halve and beat_frames.size >= 2:
        # Pick the phase (even-indexed vs odd-indexed beats) whose frames
        # carry more onset-envelope energy. Falls back gracefully when
        # one phase is empty (1- or 2-beat tracks).
        even = beat_frames[0::2]
        odd = beat_frames[1::2]
        e_even = float(env[even].sum()) if even.size else 0.0
        e_odd = float(env[odd].sum()) if odd.size else 0.0
        beat_frames = even if e_even >= e_odd else odd

    times = librosa.frames_to_time(beat_frames, sr=sr, hop_length=_HOP)
    if config.shift_ms:
        times = times + (config.shift_ms / 1000.0)
    return times


@dataclass
class TrackMetrics:
    name: str
    n_notes: int
    n_resolved: int
    n_beats: int
    mean_abs_ms: float
    mean_signed_ms: float  # +ve = beats land AFTER ✕; −ve = before
    misses: int
    extras: int


def _nearest_dist(times: np.ndarray, refs: np.ndarray) -> np.ndarray:
    """For each t in `times`, return distance to nearest value in `refs`.

    Returns an empty array if either input is empty.
    """
    if times.size == 0 or refs.size == 0:
        return np.array([], dtype=np.float64)
    refs_sorted = np.sort(refs)
    idx = np.searchsorted(refs_sorted, times)
    idx = np.clip(idx, 1, refs_sorted.size - 1)
    left = refs_sorted[idx - 1]
    right = refs_sorted[idx]
    return np.minimum(np.abs(times - left), np.abs(times - right))


def evaluate_track(
    audio_path: Path,
    track_notes: TrackNotes,
    tol_ms: float,
    window_pad_s: float,
    config: BeatConfig | None = None,
    cache: dict[Path, tuple] | None = None,
    override_ref_times: np.ndarray | None = None,
) -> TrackMetrics:
    """Score one track against a reference (listening notes or taps).

    When ``override_ref_times`` is given, those times replace the
    YAML-derived listening notes as the scoring reference. The track
    name and listening-note count in the printed table still come from
    ``track_notes`` so the rows line up across runs.
    """
    if cache is not None and audio_path in cache:
        audio, analysis, note_times, prod_beats = cache[audio_path]
    else:
        audio = load_audio(audio_path)
        analysis = analyze(audio, dance_style="kizomba")
        note_times = notes_to_times(list(track_notes.notes), analysis)
        prod_beats = np.asarray(analysis.beats.times, dtype=np.float64)
        if cache is not None:
            cache[audio_path] = (audio, analysis, note_times, prod_beats)
    if override_ref_times is not None:
        note_times = np.asarray(override_ref_times, dtype=np.float64)
    if config is None:
        beats = prod_beats
    else:
        beats = np.asarray(compute_beats(audio, config), dtype=np.float64)
    tol_s = tol_ms / 1000.0

    # Listening notes only cover the first part of each track. Restrict the
    # beat comparison to that window so the metrics describe behavior where
    # ground truth actually exists.
    if note_times.size:
        t_lo = float(note_times.min()) - window_pad_s
        t_hi = float(note_times.max()) + window_pad_s
        beats_window = beats[(beats >= t_lo) & (beats <= t_hi)]
    else:
        beats_window = beats[:0]

    if beats_window.size and note_times.size:
        beat_to_note = _nearest_dist(beats_window, note_times)
        mean_abs_ms = float(np.mean(beat_to_note) * 1000.0)
        extras = int(np.sum(beat_to_note > tol_s))
        note_to_beat = _nearest_dist(note_times, beats_window)
        misses = int(np.sum(note_to_beat > tol_s))
        # Signed offset: for each beat in the window, signed distance
        # (beat - nearest note). +ve => beats land AFTER ✕; −ve => before.
        # Useful for spotting a perceptual constant lag.
        notes_sorted = np.sort(note_times)
        idx = np.searchsorted(notes_sorted, beats_window)
        idx = np.clip(idx, 1, notes_sorted.size - 1)
        left = notes_sorted[idx - 1]
        right = notes_sorted[idx]
        d_left = beats_window - left
        d_right = beats_window - right
        signed = np.where(np.abs(d_left) <= np.abs(d_right), d_left, d_right)
        mean_signed_ms = float(np.mean(signed) * 1000.0)
    else:
        mean_abs_ms = float("nan")
        mean_signed_ms = float("nan")
        extras = beats_window.size
        misses = note_times.size

    return TrackMetrics(
        name=audio_path.stem.split(" [")[0],
        n_notes=len(track_notes.notes),
        n_resolved=int(note_times.size),
        n_beats=int(beats_window.size),
        mean_abs_ms=mean_abs_ms,
        mean_signed_ms=mean_signed_ms,
        misses=misses,
        extras=extras,
    )


def find_audio_for(
    stem_substr: str, audio_dir: Path, taps_root: Path | None = None
) -> Path | None:
    """Find an audio file whose stem contains ``stem_substr``.

    When multiple files match (e.g. several recordings of the same
    song), prefer one that has tap takes recorded under ``taps_root``
    so we don't silently pick a sibling track that has no data.
    """
    matches = [p for p in sorted(audio_dir.glob("*.mp3")) if stem_substr in p.stem]
    if not matches:
        return None
    if taps_root is not None and len(matches) > 1:
        with_takes = [p for p in matches if (taps_root / p.stem).is_dir()]
        if with_takes:
            return with_takes[0]
    return matches[0]


def _load_tap_reference(
    audio_path: Path,
    taps_root: Path,
    latency_ms: float,
    agree_window_ms: float,
    min_agree: int,
) -> np.ndarray | None:
    """Return consensus tap times for ``audio_path`` (latency-corrected).

    Each take's ``tap_times_s`` is *relative to its first tap*. To compare
    against song-absolute DSP beats, we shift each take by its own
    ``audio_offset_s`` (the song-time of tap 0, populated by
    ``scripts/backfill_tap_offsets.py``) **before** running consensus,
    so all takes live in the same coordinate system.

    Returns ``None`` when fewer than ``min_agree`` takes exist on disk
    so the caller can fall back to listening notes for that track.
    """
    takes = load_takes(audio_path.stem, taps_root)
    if len(takes) < min_agree:
        return None
    shifted = [
        [t + take.audio_offset_s for t in take.tap_times_s] for take in takes
    ]
    raw = consensus(shifted, agree_window_ms=agree_window_ms, min_agree=min_agree)
    if not raw:
        return None
    corrected = correct_tap_latency(raw, latency_ms)
    return np.asarray(corrected, dtype=np.float64)


def _run_one(
    notes: list[TrackNotes],
    audio_dir: Path,
    tol_ms: float,
    window_pad_s: float,
    config: BeatConfig | None,
    label: str,
    print_table: bool = True,
    cache: dict[Path, tuple] | None = None,
    tap_overrides: dict[Path, np.ndarray] | None = None,
    taps_root: Path | None = None,
) -> tuple[float, int, int, int]:
    """Run one (config or production) pass; return (mean_ms, miss, extra, n)."""
    if print_table:
        print(f"\n=== {label} ===", flush=True)
        print(
            f"{'track':40s} {'notes':>5s} {'res':>4s} {'beats':>5s} "
            f"{'mean_ms':>8s} {'sign_ms':>8s} {'miss':>5s} {'extra':>5s} "
            f"{'F':>5s}",
            flush=True,
        )
        print("-" * 96, flush=True)
    rows: list[TrackMetrics] = []
    for tn in notes:
        audio_path = find_audio_for(tn.stem, audio_dir, taps_root)
        if audio_path is None:
            if print_table:
                print(f"{tn.stem:40s}  <no audio under {audio_dir}>", flush=True)
            continue
        m = evaluate_track(
            audio_path, tn, tol_ms, window_pad_s, config=config, cache=cache,
            override_ref_times=(
                tap_overrides.get(audio_path) if tap_overrides else None
            ),
        )
        rows.append(m)
        if print_table:
            tp_b = max(0, m.n_beats - m.extras)
            tp_n = max(0, m.n_resolved - m.misses)
            tp = min(tp_b, tp_n)
            prec = tp / m.n_beats if m.n_beats else 0.0
            rec = tp / m.n_resolved if m.n_resolved else 0.0
            f = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
            print(
                f"{m.name[:40]:40s} {m.n_notes:5d} {m.n_resolved:4d} "
                f"{m.n_beats:5d} {m.mean_abs_ms:8.1f} {m.mean_signed_ms:+8.1f} "
                f"{m.misses:5d} {m.extras:5d} {f:5.3f}",
                flush=True,
            )
    if not rows:
        return float("nan"), float("nan"), 0, 0, 0
    mean_ms = float(np.nanmean([r.mean_abs_ms for r in rows]))
    mean_signed = float(np.nanmean([r.mean_signed_ms for r in rows]))
    total_miss = int(sum(r.misses for r in rows))
    total_extra = int(sum(r.extras for r in rows))
    # Corpus-level F: pool TPs across tracks (so big tracks weight more,
    # which is what we want when comparing configs).
    total_beats = int(sum(r.n_beats for r in rows))
    total_refs = int(sum(r.n_resolved for r in rows))
    total_tp = int(sum(
        min(max(0, r.n_beats - r.extras), max(0, r.n_resolved - r.misses))
        for r in rows
    ))
    prec = total_tp / total_beats if total_beats else 0.0
    rec = total_tp / total_refs if total_refs else 0.0
    f_corpus = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
    if print_table:
        print("-" * 96, flush=True)
        print(
            f"summary (tol={tol_ms:.0f} ms): mean_ms={mean_ms:.1f}  "
            f"signed={mean_signed:+.1f}  "
            f"misses={total_miss}  extras={total_extra}  "
            f"P={prec:.3f} R={rec:.3f} F={f_corpus:.3f}  "
            f"n_tracks={len(rows)}",
            flush=True,
        )
    return mean_ms, mean_signed, total_miss, total_extra, len(rows), f_corpus


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--notes", type=Path, default=DEFAULT_NOTES)
    p.add_argument("--audio-dir", type=Path, default=DEFAULT_AUDIO_DIR)
    p.add_argument("--tol-ms", type=float, default=100.0)
    p.add_argument(
        "--window-pad-s",
        type=float,
        default=0.5,
        help="Seconds to pad before/after the listening-note span when "
        "selecting which beats are scored.",
    )
    p.add_argument(
        "--config",
        choices=sorted(CONFIGS.keys()) + ["production"],
        default="production",
        help="Which beat tracker to evaluate. 'production' uses the live "
        "analyze() pipeline (the regression baseline).",
    )
    p.add_argument(
        "--sweep",
        action="store_true",
        help="Run every config in CONFIGS plus 'production', print one "
        "table per config, then a sorted summary.",
    )
    p.add_argument(
        "--reference",
        choices=["notes", "taps"],
        default="notes",
        help="Score against listening notes (default) or against "
        "per-track tap consensus from --taps-root.",
    )
    p.add_argument("--taps-root", type=Path, default=DEFAULT_TAPS_ROOT)
    p.add_argument(
        "--tap-latency-ms",
        type=float,
        default=0.0,
        help="Personal tap latency to subtract from consensus tap times. "
        "Estimate via rytmi.eval.tap_consensus.estimate_user_latency.",
    )
    p.add_argument(
        "--tap-agree-window-ms",
        type=float,
        default=80.0,
        help="Agreement window for tap consensus (default 80 ms).",
    )
    p.add_argument(
        "--tap-min-agree",
        type=int,
        default=2,
        help="Minimum takes that must agree to keep a consensus tap.",
    )
    args = p.parse_args(argv)

    notes = load_notes(args.notes)
    if not notes:
        print(f"no tracks in {args.notes}", file=sys.stderr)
        return 1

    tap_overrides: dict[Path, np.ndarray] | None = None
    if args.reference == "taps":
        tap_overrides = {}
        for tn in notes:
            ap = find_audio_for(tn.stem, args.audio_dir, args.taps_root)
            if ap is None:
                continue
            ref = _load_tap_reference(
                ap, args.taps_root, args.tap_latency_ms,
                args.tap_agree_window_ms, args.tap_min_agree,
            )
            if ref is not None:
                tap_overrides[ap] = ref
                print(
                    f"[taps] {ap.stem.split(' [')[0]}: {ref.size} "
                    f"consensus taps (latency={args.tap_latency_ms:.0f} ms)",
                    flush=True,
                )
            else:
                print(
                    f"[taps] {ap.stem.split(' [')[0]}: no usable takes; "
                    f"falling back to listening notes",
                    flush=True,
                )

    if args.sweep:
        labels = ["production", *sorted(CONFIGS.keys())]
        results: list[tuple[str, float, float, int, int, int, float]] = []
        cache: dict[Path, tuple] = {}
        for label in labels:
            cfg = None if label == "production" else CONFIGS[label]
            mean_ms, signed_ms, miss, extra, n, f_corpus = _run_one(
                notes, args.audio_dir, args.tol_ms, args.window_pad_s, cfg, label,
                cache=cache, tap_overrides=tap_overrides,
                taps_root=args.taps_root,
            )
            results.append((label, mean_ms, signed_ms, miss, extra, n, f_corpus))
        # Sorted summary at the bottom (by F descending; higher F = better).
        print("\n=== sweep summary (sorted by F descending) ===")
        print(
            f"{'config':16s} {'F':>5s} {'mean_ms':>8s} {'sign_ms':>8s} "
            f"{'miss':>5s} {'extra':>5s} {'n':>3s}"
        )
        print("-" * 60)
        for label, mean_ms, signed_ms, miss, extra, n, f_corpus in sorted(
            results, key=lambda r: -r[6]
        ):
            print(
                f"{label:16s} {f_corpus:5.3f} {mean_ms:8.1f} {signed_ms:+8.1f} "
                f"{miss:5d} {extra:5d} {n:3d}"
            )
        return 0

    cfg = None if args.config == "production" else CONFIGS[args.config]
    label = args.config
    _run_one(
        notes, args.audio_dir, args.tol_ms, args.window_pad_s, cfg, label,
        tap_overrides=tap_overrides,
        taps_root=args.taps_root,
    )
    return 0



if __name__ == "__main__":
    raise SystemExit(main())
