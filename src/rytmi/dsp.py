"""DSP pipeline: onset detection, beat tracking, tempo estimation, segmentation."""

from typing import TYPE_CHECKING

import librosa
import numpy as np
from scipy.signal import butter, filtfilt, find_peaks

from rytmi.types import (
    AudioData,
    BeatData,
    OnsetData,
    RhythmAnalysis,
    RhythmFeatures,
    SongPhase,
    SongSection,
    Transition,
)

if TYPE_CHECKING:
    from rytmi.vocal_activity import VocalActivityEnvelope


def detect_onsets(audio: AudioData, backtrack: bool = True) -> OnsetData:
    """Detect onsets in the audio signal.

    Returns onset times and the onset strength envelope.
    """
    strength = librosa.onset.onset_strength(y=audio.samples, sr=audio.sr)
    frames = librosa.onset.onset_detect(
        y=audio.samples,
        sr=audio.sr,
        onset_envelope=strength,
        backtrack=backtrack,
    )
    times = librosa.frames_to_time(frames, sr=audio.sr)
    return OnsetData(times=times, strength=strength, sr=audio.sr)


# Phase 25: kizomba/urban_kiz dedicated batida tracker.  The general
# librosa.beat.beat_track latches onto syncopation/double-time on kizomba
# (e.g. Baila Kizomba Amor reads ~144 BPM instead of the ~95 BPM step pulse).
# We bypass it for kizomba by isolating the kick band with a low-pass filter,
# computing onset strength on that filtered signal, then peak-picking with a
# minimum gap that matches a slow batida step.
#
# These constants were tuned in tmp/run_kizomba_batida_trials.py against the
# 11 kizomba tracks in data/songs/eval_set/.  In that range, ``cutoff_hz``
# and ``delta_pct`` barely change the picked grid; ``wait_ms`` is the
# dominant lever.
#
# Phase 28 P5d (after the mel-filterbank fix made the envelope real for the
# first time) re-swept wait_ms against the 19 tap takes in data/eval/taps/.
# Looser-is-better trend reversed: F at wait_ms=600 was 0.587, at wait_ms=450
# was 0.678 (+15 pp pooled F). Baila Kizomba Amor in nb6 visibly skips real
# kicks at 600 ms because its kick rate is faster than that gap.
_KIZOMBA_BATIDA_LPF_HZ = 150.0
_KIZOMBA_BATIDA_WAIT_MS = 450.0
_KIZOMBA_BATIDA_DELTA_PCT = 70.0
_KIZOMBA_BATIDA_HOP = 512
_KIZOMBA_STYLES = frozenset({"kizomba", "urban_kiz"})


def _track_kizomba_batida(audio: AudioData) -> BeatData:
    """Beat tracker tuned for the kizomba batida (slow step pulse).

    Pipeline: 4-pole Butterworth low-pass at ``_KIZOMBA_BATIDA_LPF_HZ``
    isolates the kick band → ``librosa.onset.onset_strength`` builds an
    envelope dominated by bass transients → ``librosa.util.peak_pick``
    enforces a minimum gap of ``_KIZOMBA_BATIDA_WAIT_MS`` (so syncopated
    snares/hats can't double the rate) and a per-track percentile threshold
    on the envelope.
    """
    sr = audio.sr
    nyq = 0.5 * sr
    b, a = butter(4, _KIZOMBA_BATIDA_LPF_HZ / nyq, btype="low")
    y_lpf = filtfilt(b, a, audio.samples).astype(np.float32, copy=False)

    env = librosa.onset.onset_strength(
        y=y_lpf,
        sr=sr,
        # fmin=20 + n_mels=8 are essential here: the librosa default
        # n_mels=128 places no mel filter below ~80 Hz, so a 150 Hz LPF
        # input produces an all-zero envelope (and a silent
        # "Empty filters detected in mel frequency basis" warning),
        # turning peak_pick into a wait_ms-period metronome. Phase 28
        # P5d diagnostic.
        fmin=20.0,
        fmax=_KIZOMBA_BATIDA_LPF_HZ * 1.5,
        n_mels=8,
        aggregate=np.median,
    )
    wait_frames = max(
        1, int(round((_KIZOMBA_BATIDA_WAIT_MS / 1000.0) * sr / _KIZOMBA_BATIDA_HOP))
    )
    delta = float(np.percentile(env, _KIZOMBA_BATIDA_DELTA_PCT)) if env.size else 0.0

    beat_frames = librosa.util.peak_pick(
        env,
        pre_max=wait_frames // 2,
        post_max=wait_frames // 2,
        pre_avg=wait_frames,
        post_avg=wait_frames,
        delta=delta,
        wait=wait_frames,
    ).astype(np.intp, copy=False)

    # Onset-strength envelopes peak slightly *after* the actual transient
    # attack; backtrack each pick to the preceding local minimum so the
    # reported beat lines up with where the listener "steps in". Cap the
    # backshift so we never walk past the previous beat or into silence
    # between hits (which would happen on near-silent gaps).
    if beat_frames.size:
        backtracked = librosa.onset.onset_backtrack(beat_frames, env)
        max_backshift = max(1, wait_frames // 4)
        beat_frames = np.maximum(backtracked, beat_frames - max_backshift).astype(
            np.intp, copy=False
        )

    beat_times = librosa.frames_to_time(
        beat_frames, sr=sr, hop_length=_KIZOMBA_BATIDA_HOP
    )

    if len(beat_times) >= 2:
        median_ibi = float(np.median(np.diff(beat_times)))
        tempo_scalar = 60.0 / median_ibi if median_ibi > 0 else 0.0
    else:
        tempo_scalar = 0.0

    return BeatData(
        times=beat_times,
        tempo=tempo_scalar,
        beat_frames=beat_frames,
    )


def track_beats(audio: AudioData, dance_style: str | None = None) -> BeatData:
    """Track beats and estimate tempo.

    For ``dance_style in {"kizomba", "urban_kiz"}`` we use a dedicated
    batida-aware tracker (:func:`_track_kizomba_batida`) because the general
    librosa tracker locks onto double-time on these styles.  All other values
    (including ``None``) keep the historical ``librosa.beat.beat_track``
    behaviour byte-for-byte.
    """
    if dance_style in _KIZOMBA_STYLES:
        return _track_kizomba_batida(audio)
    tempo, beat_frames = librosa.beat.beat_track(y=audio.samples, sr=audio.sr)
    beat_times = librosa.frames_to_time(beat_frames, sr=audio.sr)
    # tempo may be an array with one element
    tempo_scalar = float(np.atleast_1d(tempo)[0])
    return BeatData(
        times=beat_times,
        tempo=tempo_scalar,
        beat_frames=beat_frames,
    )


def estimate_tempo(audio: AudioData) -> float:
    """Estimate tempo in BPM."""
    tempo = librosa.feature.tempo(y=audio.samples, sr=audio.sr)
    return float(np.atleast_1d(tempo)[0])


def _beat_position_strengths(
    audio: AudioData,
    beats: BeatData,
    beats_per_measure: int = 4,
) -> np.ndarray:
    """Onset strength interpolated at beat times, grouped by measure position.

    Returns an array of length ``beats_per_measure`` where each element is the
    mean onset strength at that beat position across all measures.
    """
    if len(beats.times) < beats_per_measure or beats_per_measure < 1:
        return np.ones(max(beats_per_measure, 1))

    strength = librosa.onset.onset_strength(y=audio.samples, sr=audio.sr)
    strength_times = librosa.frames_to_time(np.arange(len(strength)), sr=audio.sr)
    beat_strengths = np.interp(beats.times, strength_times, strength)

    return np.array([
        float(beat_strengths[offset::beats_per_measure].mean())
        for offset in range(beats_per_measure)
    ])


def _low_band_beat_position_strengths(
    audio: AudioData,
    beats: BeatData,
    beats_per_measure: int = 4,
    lowcut: float = 40.0,
    highcut: float = 150.0,
) -> np.ndarray:
    """Kick-band onset strength means per beat position.

    Bandpass-filters the signal to the 40–150 Hz kick-drum range before
    running onset detection, so peaks mostly reflect bass-drum transients
    rather than snares / hi-hats / vocals.  Returned as a ``beats_per_measure``
    array aligned with :func:`_beat_position_strengths`.

    Returns zeros when the filtered signal has no meaningful content (e.g. a
    pure 1 kHz sine), so the two-signal fusion in :func:`detect_downbeats`
    gracefully falls back to onset-only on non-percussive material.
    """
    if len(beats.times) < beats_per_measure or beats_per_measure < 1:
        return np.zeros(max(beats_per_measure, 1))

    sr = audio.sr
    nyq = sr / 2.0
    low = max(lowcut, 1.0) / nyq
    high = min(highcut, nyq - 1.0) / nyq
    if not (0.0 < low < high < 1.0):
        return np.zeros(beats_per_measure)

    b, a = butter(4, [low, high], btype="band")
    filtered = filtfilt(b, a, audio.samples).astype(np.float32, copy=False)

    if float(np.abs(filtered).max()) < 1e-6:
        return np.zeros(beats_per_measure)

    # n_mels=8 + fmin=20 are essential here: the librosa default
    # n_mels=128 places no mel filter below ~80 Hz, so a band-limited
    # input below that range yields an all-zero envelope (only an
    # "Empty filters detected in mel frequency basis" warning).
    # See _track_kizomba_batida for the same fix; Phase 28 P5d audit.
    strength = librosa.onset.onset_strength(
        y=filtered, sr=sr, fmin=20.0, fmax=highcut * 1.5, n_mels=8,
    )
    strength_times = librosa.frames_to_time(np.arange(len(strength)), sr=sr)
    beat_strengths = np.interp(beats.times, strength_times, strength)

    return np.array([
        float(beat_strengths[offset::beats_per_measure].mean())
        for offset in range(beats_per_measure)
    ])


def _mid_high_band_beat_position_strengths(
    audio: AudioData,
    beats: BeatData,
    beats_per_measure: int = 4,
    lowcut: float = 1000.0,
    highcut: float = 4000.0,
) -> np.ndarray:
    """Snare-band onset strength means per beat position (1–4 kHz default).

    Bandpass-filters the signal to the mid-high range where snare / clap
    transients dominate in Afro-Latin grooves, then runs onset detection and
    averages onto beat positions.  Feeds the Phase-13 accent-template scorer
    as the "2 & 4" evidence source.

    Returns zeros when the filtered signal has no meaningful content, so
    downstream fusion gracefully ignores this signal rather than injecting
    noise-driven rankings.
    """
    if len(beats.times) < beats_per_measure or beats_per_measure < 1:
        return np.zeros(max(beats_per_measure, 1))

    sr = audio.sr
    nyq = sr / 2.0
    low = max(lowcut, 1.0) / nyq
    high = min(highcut, nyq - 1.0) / nyq
    if not (0.0 < low < high < 1.0):
        return np.zeros(beats_per_measure)

    b, a = butter(4, [low, high], btype="band")
    filtered = filtfilt(b, a, audio.samples).astype(np.float32, copy=False)

    if float(np.abs(filtered).max()) < 1e-6:
        return np.zeros(beats_per_measure)

    strength = librosa.onset.onset_strength(y=filtered, sr=sr)
    strength_times = librosa.frames_to_time(np.arange(len(strength)), sr=sr)
    beat_strengths = np.interp(beats.times, strength_times, strength)

    return np.array([
        float(beat_strengths[offset::beats_per_measure].mean())
        for offset in range(beats_per_measure)
    ])


def _beatnet_beat_position_strengths(
    audio: AudioData,
    beats: BeatData,
    beats_per_measure: int = 4,
) -> np.ndarray:
    """Histogram of BeatNet downbeat predictions over the librosa beat grid.

    BeatNet (Heydari et al., ISMIR 2021; ``pip install BeatNet``) runs an
    offline CNN+DBN downbeat tracker independently of librosa.  This helper
    aligns each predicted downbeat (``beat_in_bar == 1``) to its nearest
    librosa beat and counts how often that lands at each measure offset.
    The resulting ``beats_per_measure`` array slots into the same fusion
    machinery as the onset and kick-band signals.

    Returns zeros when BeatNet is unavailable or its run fails, so the
    fusion in :func:`detect_downbeats` falls back to the Phase-10 onset +
    kick combination without surfacing the error.
    """
    if len(beats.times) < beats_per_measure or beats_per_measure < 1:
        return np.zeros(max(beats_per_measure, 1))
    if not getattr(audio, "filepath", None):
        return np.zeros(beats_per_measure)

    try:
        # BeatNet imports `pyaudio` for live-microphone mode at top of module;
        # offline mode never calls it.  Stub to avoid the libportaudio system dep.
        import sys as _sys
        import types as _types

        _sys.modules.setdefault("pyaudio", _types.ModuleType("pyaudio"))
        from BeatNet.BeatNet import BeatNet
    except Exception:
        return np.zeros(beats_per_measure)

    try:
        estimator = BeatNet(
            1, mode="offline", inference_model="DBN", plot=[], thread=False,
        )
        result = estimator.process(audio.filepath)
    except Exception:
        return np.zeros(beats_per_measure)

    counts = np.zeros(beats_per_measure, dtype=float)
    beat_times = np.asarray(beats.times, dtype=float)
    for row in result:
        try:
            t = float(row[0])
            bib = int(row[1])
        except (TypeError, ValueError, IndexError):
            continue
        if bib != 1:
            continue
        idx = int(np.argmin(np.abs(beat_times - t)))
        counts[idx % beats_per_measure] += 1.0
    return counts


def _scale_normalize(values: np.ndarray) -> np.ndarray:
    """Scale a 1-D array to ``[0, 1]`` by its own max.

    An all-zero / flat-near-zero input returns zeros, so the signal
    contributes nothing to a sum-based fusion rather than introducing
    spurious rankings from noise.
    """
    values = np.asarray(values, dtype=float)
    max_val = float(values.max())
    if max_val <= 1e-9:
        return np.zeros_like(values)
    return values / max_val


# ── Grid-extrapolation "1" detector (Phase 15b) ─────────────────────────────
# Bottom-up approach: find the most tempo-stable region of the song, project
# the beat grid backwards, and identify "1" as the first grid-aligned onset.

_STABLE_WINDOW_BEATS = 16  # sliding window size for IBI stability (4 measures)
_ONSET_SNAP_TOLERANCE_FRAC = 0.3  # max distance to nearest onset as fraction of IBI


def _find_stable_region(beats: BeatData, window: int = _STABLE_WINDOW_BEATS) -> int:
    """Return the start index of the most tempo-stable beat window.

    Scans a sliding window of ``window`` beats across the beat grid and
    picks the window with the lowest coefficient of variation (std/mean)
    of inter-beat intervals.  Returns the beat index where that window
    starts.  If the track has fewer beats than the window, returns 0.
    """
    if len(beats.times) < window + 1:
        return 0

    ibis = np.diff(beats.times)  # (N-1,) inter-beat intervals
    best_start = 0
    best_cv = float("inf")

    for start in range(len(ibis) - window + 1):
        w = ibis[start : start + window]
        mean = float(w.mean())
        if mean < 1e-9:
            continue
        cv = float(w.std() / mean)
        if cv < best_cv:
            best_cv = cv
            best_start = start

    return best_start


def _extrapolate_first_beat(
    beats: BeatData,
    onsets: OnsetData,
    window: int = _STABLE_WINDOW_BEATS,
    snap_tolerance: float = _ONSET_SNAP_TOLERANCE_FRAC,
) -> int | None:
    """Find "1" by projecting the stable-region grid back to the song start.

    1. Find the most tempo-stable window of beats.
    2. Compute the median IBI in that window.
    3. Walk backwards from the **end** of the stable window in steps of
       ``median_ibi``, looking for the earliest projected time that is
       close to an actual onset (within ``snap_tolerance × median_ibi``).
    4. Return the **beat index** in ``beats.times`` closest to that
       projected first beat.  Returns ``None`` if no onset-aligned
       projection is found before ``t = 0``.
    """
    if len(beats.times) < window + 1 or len(onsets.times) == 0:
        return None

    stable_start = _find_stable_region(beats, window)
    stable_ibis = np.diff(beats.times[stable_start : stable_start + window + 1])
    median_ibi = float(np.median(stable_ibis))
    if median_ibi < 1e-3:
        return None

    tol = snap_tolerance * median_ibi
    onset_times = np.asarray(onsets.times, dtype=float)

    # Walk backwards from the end of the stable region.
    anchor = float(beats.times[stable_start + window])
    projected = anchor
    best_projected = None

    while projected >= -tol:
        # Check if an onset exists near this projected time.
        dists = np.abs(onset_times - projected)
        if float(dists.min()) <= tol:
            best_projected = projected
        projected -= median_ibi

    if best_projected is None:
        return None

    # Map the projected time to the nearest beat index.
    beat_dists = np.abs(np.asarray(beats.times, dtype=float) - best_projected)
    return int(np.argmin(beat_dists))


def _grid_extrapolation_offset(
    beats: BeatData,
    onsets: OnsetData,
    beats_per_measure: int = 4,
) -> tuple[int, float]:
    """Score each beat position by mean onset strength; pick strongest as "1".

    For every beat in the grid, finds the nearest detected onset (within a
    tolerance of 30 % of the median IBI) and records its strength.  Mean
    onset strength is computed per beat position (0 .. beats_per_measure-1).
    The position with the highest mean is returned as the likely downbeat
    offset.

    Confidence is the relative gap between the best and second-best
    positions: ``(best - second) / best``.  Returns ``(0, 0.0)`` when there
    are too few beats or no onsets.
    """
    if len(beats.times) < beats_per_measure or len(onsets.times) == 0:
        return 0, 0.0

    onset_times = np.asarray(onsets.times, dtype=float)
    onset_strengths = np.asarray(onsets.strength, dtype=float)
    median_ibi = float(np.median(np.diff(beats.times)))
    if median_ibi < 1e-3:
        return 0, 0.0
    tol = _ONSET_SNAP_TOLERANCE_FRAC * median_ibi

    # Accumulate onset strength by beat position.
    position_sums = np.zeros(beats_per_measure)
    position_counts = np.zeros(beats_per_measure)

    for i, bt in enumerate(beats.times):
        pos = i % beats_per_measure
        position_counts[pos] += 1
        dists = np.abs(onset_times - float(bt))
        nearest_idx = int(np.argmin(dists))
        if float(dists[nearest_idx]) <= tol:
            position_sums[pos] += float(onset_strengths[nearest_idx])
        # Beats with no nearby onset contribute 0 strength (counted but not summed).

    # Mean onset strength per position.
    means = np.where(position_counts > 0, position_sums / position_counts, 0.0)
    offset = int(np.argmax(means))

    # Confidence: relative gap between best and second-best.
    sorted_means = np.sort(means)[::-1]
    if sorted_means[0] > 1e-9:
        conf = float((sorted_means[0] - sorted_means[1]) / sorted_means[0])
    else:
        conf = 0.0

    return offset, conf


# ── Harmonic-cue downbeat voice ──────────────────────────────────────────────
# Phase 15 — chroma novelty + bass onset strength per beat position.
# Targets percussion-ambiguous styles (kizomba) where chord changes and bass
# root motion carry clearer bar-level structure than kicks or snares.

_HARMONIC_CUE_CHROMA_WEIGHT = 0.5
_HARMONIC_CUE_BASS_WEIGHT = 0.5


def _harmonic_cue_beat_position_strengths(
    audio: AudioData,
    beats: BeatData,
    beats_per_measure: int = 4,
    bass_audio: AudioData | None = None,
) -> np.ndarray:
    """Harmonic-cue downbeat scores per beat position.

    Combines two signals:

    * **Chroma novelty** *H(t)* — cosine distance between consecutive
      beat-synchronous chroma vectors computed on the HPSS harmonic
      component.  Chord changes cluster on strong metric positions,
      making this a useful downbeat cue even when percussion is sparse.

    * **Bass onset strength** *B(t)* — onset energy in the bass range.
      When a separated bass stem is provided (``bass_audio``), onset
      detection runs on it directly.  Otherwise, falls back to the
      40–150 Hz bandpass of the mix (same as the kick voice, but here
      it votes as part of the harmonic composite).

    Returns a ``beats_per_measure``-length array where higher values
    indicate stronger harmonic evidence for that offset being the "1".
    Returns zeros when the signal is uninformative, so the fusion in
    :func:`detect_downbeats` can safely ignore it.
    """
    if len(beats.times) < beats_per_measure or beats_per_measure < 1:
        return np.zeros(max(beats_per_measure, 1))

    # ── Chroma novelty H(t) ──────────────────────────────────────────
    y_harm, _ = librosa.effects.hpss(audio.samples)
    chroma = librosa.feature.chroma_cqt(y=y_harm, sr=audio.sr)  # (12, T)
    chroma_times = librosa.frames_to_time(np.arange(chroma.shape[1]), sr=audio.sr)

    n_beats = len(beats.times)
    # Beat-synchronous chroma: average chroma frames within each beat interval.
    beat_chroma = np.zeros((12, n_beats), dtype=np.float64)
    for i in range(n_beats):
        t_start = beats.times[i]
        t_end = beats.times[i + 1] if i + 1 < n_beats else audio.duration
        mask = (chroma_times >= t_start) & (chroma_times < t_end)
        if mask.any():
            beat_chroma[:, i] = chroma[:, mask].mean(axis=1)

    # Cosine-distance novelty between consecutive beat-sync chroma vectors.
    novelty = np.zeros(n_beats, dtype=np.float64)
    for i in range(1, n_beats):
        a = beat_chroma[:, i - 1]
        b = beat_chroma[:, i]
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a > 1e-9 and norm_b > 1e-9:
            cos_sim = float(np.dot(a, b) / (norm_a * norm_b))
            novelty[i] = 1.0 - np.clip(cos_sim, -1.0, 1.0)

    # Aggregate by beat position (mean novelty at each offset).
    chroma_scores = np.array([
        float(novelty[offset::beats_per_measure].mean())
        for offset in range(beats_per_measure)
    ])

    # ── Bass onset strength B(t) ─────────────────────────────────────
    if bass_audio is not None:
        # n_mels=8 + fmin=20 essential for low-band envelopes; see
        # _track_kizomba_batida. Without them the default mel filterbank
        # has no bins below ~80 Hz and silently returns a much weaker
        # envelope on bass-isolated input.
        bass_strength = librosa.onset.onset_strength(
            y=bass_audio.samples, sr=bass_audio.sr,
            fmin=20.0, fmax=300.0, n_mels=8,
        )
        bass_times = librosa.frames_to_time(
            np.arange(len(bass_strength)), sr=bass_audio.sr,
        )
    else:
        # Fallback: 40–150 Hz bandpass on the mix.
        sr = audio.sr
        nyq = sr / 2.0
        low = 40.0 / nyq
        high = min(150.0, nyq - 1.0) / nyq
        if not (0.0 < low < high < 1.0):
            return _scale_normalize(chroma_scores)
        b, a = butter(4, [low, high], btype="band")
        filtered = filtfilt(b, a, audio.samples).astype(np.float32, copy=False)
        if float(np.abs(filtered).max()) < 1e-6:
            return _scale_normalize(chroma_scores)
        # Same fmin/n_mels reasoning as above; without these the LPF
        # input collapses to all-zero and the bass channel silently
        # contributes nothing to the downbeat estimator.
        bass_strength = librosa.onset.onset_strength(
            y=filtered, sr=sr, fmin=20.0, fmax=225.0, n_mels=8,
        )
        bass_times = librosa.frames_to_time(np.arange(len(bass_strength)), sr=sr)

    bass_at_beats = np.interp(beats.times, bass_times, bass_strength)
    bass_scores = np.array([
        float(bass_at_beats[offset::beats_per_measure].mean())
        for offset in range(beats_per_measure)
    ])

    # ── Combine ──────────────────────────────────────────────────────
    h_norm = _scale_normalize(chroma_scores)
    b_norm = _scale_normalize(bass_scores)
    return _HARMONIC_CUE_CHROMA_WEIGHT * h_norm + _HARMONIC_CUE_BASS_WEIGHT * b_norm


# Phase 14 — HPSS-percussive preprocessing for kick / onset voices.
# When enabled, `_low_band_beat_position_strengths` and
# `_beat_position_strengths` operate on `librosa.effects.hpss()`'s
# percussive component instead of the raw mix, suppressing harmonic bleed
# (vocal sibilance, guitar strums) that flattens the per-offset vectors on
# kizomba.  BeatNet stays on raw audio (its DBN was trained on full mixes).
_USE_HPSS_PREPROCESSING = False
_HPSS_PREPROC_MARGIN = 2.0


def _percussive_audio(audio: AudioData) -> AudioData:
    """Return an ``AudioData`` whose samples are the HPSS percussive component."""
    _, y_perc = librosa.effects.hpss(audio.samples, margin=_HPSS_PREPROC_MARGIN)
    return AudioData(
        samples=y_perc.astype(np.float32, copy=False),
        sr=audio.sr,
        duration=audio.duration,
        filepath=audio.filepath,
    )


# Phase 13 — accent templates for genre-specific downbeat phase detection.
# Sourced from docs/research/Q1 (follow-up 1b).  Kizomba kick rides 1 & 3
# with soft-pedal 2 & 4; bachata derecho hits kick on 1 & 3 only.  Snare
# template is shared — 2 & 4 is the common backbeat across both.  Templates
# are ethnomusicologically grounded rather than MIR-validated; treat as a
# hypothesis, not ground truth.
_ACCENT_TEMPLATES: dict[str, dict[str, np.ndarray]] = {
    "kizomba": {
        "kick":  np.array([1.0, 0.4, 1.0, 0.4]),
        "snare": np.array([0.0, 1.0, 0.0, 1.0]),
    },
    "bachata": {
        "kick":  np.array([1.0, 0.0, 1.0, 0.0]),
        "snare": np.array([0.0, 1.0, 0.0, 1.0]),
    },
}


def _accent_template_scores(
    kick_scores: np.ndarray,
    snare_scores: np.ndarray,
    beats_per_measure: int = 4,
) -> tuple[np.ndarray, str | None]:
    """Per-offset accent-template fusion score for genre-aware downbeat voting.

    For each genre template in :data:`_ACCENT_TEMPLATES`, and for each
    candidate "1" offset ``phi`` in ``0..bpm-1``, computes the dot product
    of the cyclically-shifted template (both kick and snare bands) with the
    scale-normalised per-offset signal vectors, then sums kick + snare
    contributions.  The higher-peaking genre's per-offset score vector
    wins; its name is returned alongside for diagnostics.

    Genre-agnostic at call time: a wrong template on a wrong genre
    produces a lower peak and loses to the better-matching template.

    Returns zeros + ``None`` when ``beats_per_measure != 4`` (templates are
    defined only for 4/4) or when both input vectors are ~zero.
    """
    if beats_per_measure != 4:
        return np.zeros(max(beats_per_measure, 1)), None

    kick_n = _scale_normalize(kick_scores)
    snare_n = _scale_normalize(snare_scores)

    if kick_n.max() <= 1e-9 and snare_n.max() <= 1e-9:
        return np.zeros(beats_per_measure), None

    best_score_vec = np.zeros(beats_per_measure)
    best_genre: str | None = None
    best_peak = -np.inf
    for genre, tmpl in _ACCENT_TEMPLATES.items():
        scores = np.zeros(beats_per_measure)
        for phi in range(beats_per_measure):
            k_rot = np.roll(tmpl["kick"], phi)
            s_rot = np.roll(tmpl["snare"], phi)
            scores[phi] = float(kick_n @ k_rot + snare_n @ s_rot)
        peak = float(scores.max())
        if peak > best_peak:
            best_peak = peak
            best_score_vec = scores
            best_genre = genre
    return best_score_vec, best_genre


def _beat_clarity(
    beat_strength_pattern: list[float],
    percussiveness: float,
    tempo_stability: float,
) -> float:
    """Derive a 0–1 beat-clarity score from per-section rhythm features.

    Three signals are combined with equal geometric weight:

    * **Beat-strength contrast** — max / mean of the normalised beat-position
      strengths.  A value of 1.0 means all positions are equal (flat, no
      accent); higher values mean some beat positions clearly stand out.
      Mapped to 0–1 via ``1 - 1/contrast``.
    * **Percussiveness** — fraction of energy in the HPSS percussive
      component.  Already 0–1; higher means a more percussion-driven
      signal where the beat is easier to hear.
    * **Tempo regularity** — ``1 / (1 + tempo_stability)`` so a steady
      pulse (low CV) maps to a value near 1.0.

    The geometric mean ensures all three signals must be present for a
    high score — a steady tempo with no percussive energy still rates low.
    """
    # Beat-strength contrast
    if not beat_strength_pattern or max(beat_strength_pattern) <= 0:
        contrast_score = 0.0
    else:
        mean_val = sum(beat_strength_pattern) / len(beat_strength_pattern)
        contrast = max(beat_strength_pattern) / mean_val if mean_val > 0 else 1.0
        contrast_score = float(np.clip(1.0 - 1.0 / contrast, 0.0, 1.0))

    # Percussiveness is already 0–1
    perc_score = float(np.clip(percussiveness, 0.0, 1.0))

    # Tempo regularity: low CV → high score
    regularity_score = 1.0 / (1.0 + tempo_stability)

    product = contrast_score * perc_score * regularity_score
    return float(np.cbrt(product)) if product > 0 else 0.0


def compute_rhythm_features(
    audio: AudioData,
    onsets: OnsetData,
    beats: BeatData,
    beats_per_measure: int = 4,
) -> RhythmFeatures:
    """Compute rhythm features for style disambiguation."""
    n_onsets = len(onsets.times)
    n_beats = len(beats.times)
    onsets_per_beat = float(n_onsets / n_beats) if n_beats > 0 else 0.0

    pattern = _beat_position_strengths(audio, beats, beats_per_measure)
    max_val = pattern.max() if pattern.max() > 0 else 1.0
    beat_strength_pattern = (pattern / max_val).tolist()

    harmonic, percussive = librosa.effects.hpss(audio.samples)
    perc_energy = float(np.sum(percussive ** 2))
    total_energy = float(np.sum(audio.samples ** 2))
    percussiveness = perc_energy / total_energy if total_energy > 0 else 0.0

    centroid = librosa.feature.spectral_centroid(y=audio.samples, sr=audio.sr)
    spectral_centroid_mean = float(np.mean(centroid))

    ibi = np.diff(beats.times) if n_beats > 1 else np.array([1.0])
    tempo_stability = float(np.std(ibi) / np.mean(ibi)) if np.mean(ibi) > 0 else 0.0

    ioi_ms = np.diff(onsets.times) * 1000.0 if n_onsets > 1 else np.array([0.0])
    ioi_median_ms = float(np.median(ioi_ms))
    ioi_std_ms = float(np.std(ioi_ms))

    return RhythmFeatures(
        onsets_per_beat=onsets_per_beat,
        beat_strength_pattern=beat_strength_pattern,
        percussiveness=percussiveness,
        spectral_centroid_mean=spectral_centroid_mean,
        tempo_stability=tempo_stability,
        ioi_median_ms=ioi_median_ms,
        ioi_std_ms=ioi_std_ms,
        beat_clarity=_beat_clarity(beat_strength_pattern, percussiveness, tempo_stability),
    )


# "Full" Phase-13 fusion weights — used when the template voice strictly
# improves confidence over the Phase-11 baseline.
_BEATNET_WEIGHT = 0.40
_TEMPLATE_WEIGHT = 0.20
_KICK_WEIGHT = 0.25
_ONSET_WEIGHT = 0.15
# "Safe" fusion weights — exactly Phase 11.  When the template voice would
# dilute a confident winner, the adaptive guard reverts to these so we never
# regress below Phase-11 confidence on tracks the template doesn't help.
_SAFE_BEATNET_WEIGHT = 0.50
_SAFE_KICK_WEIGHT = 0.30
_SAFE_ONSET_WEIGHT = 0.20
_BEATNET_DISAGREE_PENALTY = 0.7
_PHASE10_DISAGREE_PENALTY = 0.5

def _combined_metrics(combined: np.ndarray, bpm: int) -> tuple[int, float]:
    """Compute ``(best_offset, confidence)`` for a fused offset-strength vector.

    Mirrors the metric computation inline in :func:`detect_downbeats` so we
    can score multiple candidate fusions and pick the better-conditioned
    one.  Confidence formula: ``sqrt(margin × dominance)`` where
    ``margin = (best - runner_up) / best`` and ``dominance`` is the
    chance-baselined winner share.
    """
    if len(combined) < 2:
        return 0, 0.0
    best_offset = int(np.argmax(combined))
    sorted_scores = np.sort(combined)[::-1]
    best = float(sorted_scores[0])
    runner_up = float(sorted_scores[1])
    if best <= 1e-9:
        return best_offset, 0.0
    margin = (best - runner_up) / best
    total = float(combined.sum())
    winner_ratio = best / total if total > 0 else 0.0
    baseline = 1.0 / len(combined)
    dominance = float(np.clip((winner_ratio - baseline) / (1.0 - baseline), 0.0, 1.0))
    return best_offset, float(np.sqrt(margin * dominance))


def detect_downbeats(
    audio: AudioData,
    beats: BeatData,
    beats_per_measure: int = 4,
    bass_audio: AudioData | None = None,
) -> tuple[np.ndarray, int, float, int]:
    """Estimate downbeat positions and a learner-facing confidence score.

    Four-signal fusion (Phase 13)
    -----------------------------
    For each candidate "1" offset in 0..beats_per_measure-1, the mean
    strength of beats at that offset is computed from four sources:

    * **BeatNet downbeat votes** — an offline CNN+DBN downbeat tracker
      (Heydari et al., ISMIR 2021) is run on the source audio; its
      ``beat_in_bar == 1`` predictions are histogrammed onto our librosa
      beat grid, so the strongest peak indicates which offset most often
      coincides with BeatNet's downbeats.
    * **Accent-template score** — per-offset cross-correlation of the
      kick-band (40–150 Hz) and snare-band (1–4 kHz) per-position
      vectors against genre-specific templates (kizomba, bachata) from
      :data:`_ACCENT_TEMPLATES`.  Targets the three kizomba tracks that
      Phase 11's BeatNet fusion left below the 0.25 confidence gate —
      soft on-beat kick + soft-pedal snare fits a template that generic
      onset detection misses.
    * **Low-band onset strength** — the audio is bandpass-filtered to
      40–150 Hz so the signal responds mostly to kick-drum transients.
      Styles with a clear 1/3 or 1-only kick pattern disambiguate
      themselves cleanly.
    * **Full-band onset strength** — sensitive to any transient, but can be
      misled by syncopated hits or vocal / melodic accents.

    Each signal is scaled to ``[0, 1]`` by its own max
    (:func:`_scale_normalize`) and combined with weights
    ``0.40 · BeatNet + 0.20 · template + 0.25 · kick + 0.15 · onset``.
    BeatNet still dominates when informative, but the template now votes
    meaningfully on genre-shaped percussion.  When BeatNet is unavailable
    the fusion drops to ``onset + kick + template`` (Phase-10 behaviour
    plus the new template voice).

    Adaptive template weight (Phase 13 Commit A2): two candidate fusions
    are scored — a "safe" variant using the exact Phase-11 weights
    (0.5 / 0.3 / 0.2, no template voice) and a "full" variant using the
    Phase-13 weights with the template firing at its 0.20 weight.  The
    variant with strictly higher confidence wins, so the template is only
    used when it actually improves the decision and the safe path acts as a
    zero-regression floor.  Experiment 20 found that on real audio the
    snare band picks up vocal sibilance / chord strums producing a
    near-flat template vector that dilutes a confident winner's margin;
    the safe variant catches that case automatically.

    Confidence
    ----------
    Same ``sqrt(margin × dominance)`` structure as Phase 9, now computed on
    the combined array:

    * **margin** — ``(best − runner_up) / best`` — catches tied tops.
    * **dominance** — ``(winner_share − 1/bpm) / (1 − 1/bpm)`` — catches
      "winner barely above chance".

    Disagreement penalty depends on which signals are informative:

    * BeatNet present → penalty ×0.7 when BeatNet's top offset disagrees
      with the combined winner (mild, because BeatNet is the strongest
      single source but can occasionally lose a soft vote to kick+onset).
    * BeatNet absent  → Phase-10 penalty ×0.5 when kick disagrees with
      onset on the top offset and kick is informative.

    Returns ``(downbeat_times, beats_per_measure, confidence, best_offset)``.
    """
    # Not enough beats, or measure has no internal structure to score.
    # bpm < 2 has no runner-up, so margin is undefined.
    if len(beats.times) < beats_per_measure or beats_per_measure < 2:
        return beats.times[:1], beats_per_measure, 0.0, 0

    bpm = beats_per_measure
    # Phase 14: optionally run kick / onset / snare helpers on the HPSS
    # percussive component instead of the raw mix.  BeatNet stays on raw
    # audio — its CNN+DBN was trained on full mixes.
    dsp_audio = _percussive_audio(audio) if _USE_HPSS_PREPROCESSING else audio
    beatnet_scores = _beatnet_beat_position_strengths(audio, beats, bpm)
    onset_scores = _beat_position_strengths(dsp_audio, beats, bpm)
    kick_scores = _low_band_beat_position_strengths(dsp_audio, beats, bpm)
    snare_scores = _mid_high_band_beat_position_strengths(dsp_audio, beats, bpm)
    template_scores, _template_genre = _accent_template_scores(
        kick_scores, snare_scores, bpm,
    )

    beatnet_norm = _scale_normalize(beatnet_scores)
    onset_norm = _scale_normalize(onset_scores)
    kick_norm = _scale_normalize(kick_scores)
    template_norm = _scale_normalize(template_scores)

    # Phase 15: harmonic-cue voice (chroma novelty + bass onset strength).
    harmonic_scores = _harmonic_cue_beat_position_strengths(
        audio, beats, bpm, bass_audio=bass_audio,
    )
    harmonic_norm = _scale_normalize(harmonic_scores)
    harmonic_is_informative = bool(harmonic_scores.max() > 1e-9)

    beatnet_is_informative = bool(beatnet_scores.max() > 1e-9)
    kick_is_informative = bool(kick_scores.max() > 1e-9)
    template_is_informative = bool(template_scores.max() > 1e-9)

    if beatnet_is_informative:
        # "Safe" fusion: Phase-11 weights, no template voice.  Acts as a
        # zero-regression floor — when the template doesn't strictly improve
        # things, we use the exact pre-Phase-13 fusion.
        combined_safe = (
            _SAFE_BEATNET_WEIGHT * beatnet_norm
            + _SAFE_KICK_WEIGHT * kick_norm
            + _SAFE_ONSET_WEIGHT * onset_norm
        )
        # "Full" fusion: template voice fires normally at its own weight.
        combined_full = (
            _BEATNET_WEIGHT * beatnet_norm
            + _TEMPLATE_WEIGHT * template_norm
            + _KICK_WEIGHT * kick_norm
            + _ONSET_WEIGHT * onset_norm
        )
    else:
        # No BeatNet → Phase-10 sum-of-normalised fusion as the safe base;
        # template adds an extra unit-weight voice in the "full" variant.
        combined_safe = onset_norm + kick_norm
        combined_full = combined_safe + template_norm

    if template_is_informative:
        _, conf_safe = _combined_metrics(combined_safe, bpm)
        _, conf_full = _combined_metrics(combined_full, bpm)
        # Adaptive template weight (Phase 13 Commit A2): only fold the
        # template into the fusion when it strictly improves confidence.
        # Provably non-regressive — when the template would dilute a
        # confident winner's margin (the experiment-20 failure mode), we
        # fall back to the safe fusion automatically.
        combined = combined_full if conf_full > conf_safe else combined_safe
    else:
        combined = combined_safe

    # Phase 15: additive-adaptive harmonic voice.  Same non-regressive
    # pattern as the template guard — the harmonic cue is folded in only
    # when it strictly improves confidence over whichever fusion won above.
    if harmonic_is_informative:
        combined_with_harmonic = combined + harmonic_norm
        _, conf_base = _combined_metrics(combined, bpm)
        _, conf_harm = _combined_metrics(combined_with_harmonic, bpm)
        if conf_harm > conf_base:
            combined = combined_with_harmonic

    best_offset, confidence = _combined_metrics(combined, bpm)

    if combined.max() <= 1e-9:
        return beats.times[best_offset::bpm], bpm, 0.0, best_offset

    if beatnet_is_informative:
        if int(np.argmax(beatnet_scores)) != best_offset:
            confidence *= _BEATNET_DISAGREE_PENALTY
    elif (
        kick_is_informative
        and int(np.argmax(onset_scores)) != int(np.argmax(kick_scores))
    ):
        confidence *= _PHASE10_DISAGREE_PENALTY

    return beats.times[best_offset::bpm], bpm, confidence, best_offset


# ── Section segmentation ─────────────────────────────────────────────────────

# Minimum section length in seconds — avoids micro-segments that are
# meaningless for dance phrasing.  Four bars of 120 BPM ≈ 8 s.
_MIN_SECTION_S = 8.0

# Novelty curve hop length in frames — controls time resolution of the
# energy / onset density curve used for boundary detection.
_NOVELTY_HOP_FRAMES = 256


def _compute_novelty_curve(
    audio: AudioData,
    *,
    hop_length: int = _NOVELTY_HOP_FRAMES,
) -> tuple[np.ndarray, np.ndarray]:
    """Build a combined novelty curve from RMS energy and onset strength.

    Returns ``(novelty, times)`` where *novelty* is a 1-D array of positive
    values and *times* maps each frame to seconds.
    """
    rms = librosa.feature.rms(y=audio.samples, hop_length=hop_length)[0]
    onset_env = librosa.onset.onset_strength(
        y=audio.samples, sr=audio.sr, hop_length=hop_length,
    )
    # Align lengths (librosa can differ by 1 frame)
    n = min(len(rms), len(onset_env))
    rms = rms[:n]
    onset_env = onset_env[:n]

    # Normalise each to [0, 1] then combine
    rms_norm = rms / (rms.max() + 1e-9)
    onset_norm = onset_env / (onset_env.max() + 1e-9)
    novelty = 0.5 * rms_norm + 0.5 * onset_norm

    times = librosa.frames_to_time(np.arange(n), sr=audio.sr, hop_length=hop_length)
    return novelty, times


def _smooth(signal: np.ndarray, window: int) -> np.ndarray:
    """Simple moving-average smoother (preserves length via same-mode conv)."""
    if window < 2 or len(signal) < window:
        return signal
    kernel = np.ones(window) / window
    return np.convolve(signal, kernel, mode="same")


def _segment_boundaries(
    novelty: np.ndarray,
    times: np.ndarray,
    duration: float,
    *,
    min_section_s: float = _MIN_SECTION_S,
    smooth_window: int = 21,
) -> list[float]:
    """Find section boundaries as times where the smoothed novelty curve changes abruptly.

    Strategy: compute the first-order difference of the smoothed novelty curve,
    then pick peaks in the *absolute* difference that are at least
    ``min_section_s`` apart.
    """
    smoothed = _smooth(novelty, smooth_window)
    diff = np.abs(np.diff(smoothed))
    if len(diff) == 0:
        return [0.0, duration]

    # Convert min_section_s to frame distance
    dt = times[1] - times[0] if len(times) > 1 else 0.05
    min_dist = max(1, int(min_section_s / dt))

    # Threshold: peaks above 0.4× the max diff value
    threshold = 0.4 * diff.max()
    peaks, _ = find_peaks(diff, height=threshold, distance=min_dist)

    boundaries = [0.0]
    for p in peaks:
        t = float(times[p]) if p < len(times) else float(times[-1])
        # Skip if too close to start or end
        if t < min_section_s or t > duration - min_section_s:
            continue
        boundaries.append(t)
    boundaries.append(duration)
    return sorted(set(boundaries))


def _energy_level(rms_mean: float, global_rms_mean: float) -> str:
    """Classify a section's energy by fixed ratio to the global average.

    Legacy fallback used when a track has too few sections for percentile
    classification (e.g. synthetic click fixtures, very short audio).
    """
    if rms_mean < global_rms_mean * 0.6:
        return "low"
    if rms_mean > global_rms_mean * 1.3:
        return "high"
    return "medium"


# Percentile + absolute-guard thresholds for track-relative energy classification.
_ENERGY_LOW_PCT = 30.0
_ENERGY_HIGH_PCT = 75.0
_ENERGY_LOW_CEILING = 0.85  # a section must also be below 0.85× global to count as low
_ENERGY_HIGH_FLOOR = 1.10   # a section must also be above 1.10× global to count as high
_ENERGY_MIN_SECTIONS = 4    # below this, fall back to fixed-ratio classification


def _classify_section_energies(
    seg_rms_ratios: list[float],
    *,
    low_pct: float = _ENERGY_LOW_PCT,
    high_pct: float = _ENERGY_HIGH_PCT,
    low_ceiling: float = _ENERGY_LOW_CEILING,
    high_floor: float = _ENERGY_HIGH_FLOOR,
    min_sections: int = _ENERGY_MIN_SECTIONS,
) -> list[str]:
    """Classify each section's energy by its rank within this track.

    Uses per-track percentiles so real dance music — which often has a
    compressed dynamic range — actually gets a distribution of low/medium/high
    labels instead of collapsing everything to ``medium``.

    Absolute guardrails (``low_ceiling`` and ``high_floor``) keep flat tracks
    from getting spurious low/high splits from percentile noise: a section
    must be *both* below the low percentile *and* below ``low_ceiling × global``
    to count as low (and symmetrically for high).

    Tracks with fewer than ``min_sections`` sections fall back to
    ``_energy_level()`` on each ratio individually — this keeps short
    synthetic fixtures stable.
    """
    n = len(seg_rms_ratios)
    if n == 0:
        return []
    if n < min_sections:
        return [_energy_level(r, 1.0) for r in seg_rms_ratios]

    ratios_arr = np.asarray(seg_rms_ratios, dtype=float)
    p_low = float(np.percentile(ratios_arr, low_pct))
    p_high = float(np.percentile(ratios_arr, high_pct))

    levels: list[str] = []
    for r in seg_rms_ratios:
        if r <= p_low and r < low_ceiling:
            levels.append("low")
        elif r >= p_high and r > high_floor:
            levels.append("high")
        else:
            levels.append("medium")
    return levels


# HPSS source separation margin (librosa default).
_HPSS_MARGIN = 1.0

# Signal-aware label decision thresholds (track-relative medians).
_BREAK_RMS_MODERATE_DROP = 0.85    # `full` branch: moderate RMS drop gate
_BREAK_OPB_RATIO_TO_MEDIAN = 0.70  # opb threshold for the moderate-drop branch
_BREAK_MIN_PHRASES = 2.0           # break must last at least 2 phrases
_SHORT_BREAK_MIN_PHRASES = 1.0     # short_break must last at least 1 phrase
_BREAK_MELODIC_HARM_RATIO = 0.70   # melodic: harm_ratio < this × track median
_BREAK_MELODIC_PERC_FLOOR = 0.85   # melodic: perc_ratio > this × track median
_BREAK_PERCUSSIVE_PERC_RATIO = 0.70
_BREAK_PERCUSSIVE_HARM_FLOOR = 0.85
_BREAK_SEVERE_HARM_RATIO = 0.50    # severe: both collapse regardless of opb
_BREAK_SEVERE_PERC_RATIO = 0.50
# Stricter gates applied only to `short_break` emitted by the HPSS `melodic`
# and `percussive` branches.  Those branches can fire on 1-phrase sections
# whose ratios merely graze the threshold (e.g. H×0.70, P×1.4, RMS×0.94)
# which is a melodic fluctuation, not a real energy drop.  Require either a
# substantial RMS drop or a severe HPSS component collapse before surfacing
# such a section as a short_break.
_SHORT_BREAK_STRONG_RMS_RATIO = 0.70
_SHORT_BREAK_STRONG_HPSS_RATIO = 0.60
_PEAK_RMS_RATIO_TO_MEDIAN = 1.05   # a peak must have rms_ratio > 1.05 × track median
_PEAK_OPB_RATIO_TO_MEDIAN = 1.00   # and opb > 1.00 × track median
_DOWNBEAT_OFFSET_MIN_CONFIDENCE = 0.25


def _label_sections(
    sections: list[tuple[float, float, str, float, float, float, float]],
    duration: float,
    *,
    median_ibi: float = 0.5,
    phrase_length: int = 8,
) -> list[tuple[float, float, str, str | None]]:
    """Assign dancer-oriented labels (intro, main, break, build, peak, outro).

    Inputs per section:
    ``(start, end, energy_category, rms_ratio, opb, harm_ratio, perc_ratio)``.

    Returns a list of ``(start, end, label, break_branch)`` tuples.  The
    ``break_branch`` field is the name of the HPSS branch that fired on a
    break row (``"melodic"``, ``"percussive"``, ``"severe"``, ``"full"``) or
    ``None`` for non-break sections.

    Break detection uses four disjunctive branches computed against
    track-relative medians.  Branch order matters — the first branch that
    fires wins.  When ``harm_ratio`` / ``perc_ratio`` look legacy (all zero,
    e.g. synthetic fixtures), the three HPSS branches are skipped and only
    the ``full`` branch (Phase 5 rule) is considered.

    - **melodic** — ``harm < 0.70 × median_harm`` AND
      ``perc > 0.85 × median_perc``.  Classic kizomba melodic drop: bass /
      melody drops out but tumba / congas keep playing.
    - **percussive** — ``perc < 0.70 × median_perc`` AND
      ``harm > 0.85 × median_harm``.  Rare inverse: percussion drops but
      melody carries.
    - **severe** — ``harm < 0.50 × median_harm`` AND
      ``perc < 0.50 × median_perc``.  Both components collapse regardless of
      ``opb``; catches busy-but-thin drops that high ``opb`` would otherwise
      hide from the ``full`` branch.
    - **full** — ``rms_ratio < 0.85 × median_rms`` AND
      ``opb < 0.70 × median_opb``.  Classic bachata "everything thins out"
      and the fallback for legacy synthetic fixtures with no HPSS data.

    When the firing branch is ``melodic`` or ``percussive`` AND the section
    is ``short`` (1-phrase band), an additional gate applies: the section
    must also pass ``rms_ratio < 0.70 × median_rms`` OR have one HPSS
    component below ``0.60 × median``.  Without this, the HPSS branches
    surface every mild 1-phrase harmonic dip — Phase 12 tightened this
    after listen-pass review on Charbel-Ana and related kizomba tracks.

    Peak / build rules are unchanged from Phase 5:

    - **peak** — ``rms_ratio > 1.05 × track_median_rms`` AND
      ``opb > 1.00 × track_median_opb`` AND is the highest-RMS section in the
      middle half of the track.
    - **build** — immediately precedes a peak and has strictly rising
      ``rms_ratio`` vs the previous section.
    - Everything else → ``main``.

    First and last sections are always positional (``intro`` / ``outro``).
    """
    n = len(sections)
    if n == 0:
        return []
    if n == 1:
        return [(sections[0][0], sections[0][1], "main", None)]

    labels = ["main"] * n
    branch_names: list[str | None] = [None] * n
    labels[0] = "intro"
    labels[-1] = "outro"

    if n <= 2:
        return [(s[0], s[1], labels[i], branch_names[i]) for i, s in enumerate(sections)]

    rms_ratios = np.asarray([s[3] for s in sections], dtype=float)
    opbs = np.asarray([s[4] for s in sections], dtype=float)
    harm_ratios = np.asarray([s[5] for s in sections], dtype=float)
    perc_ratios = np.asarray([s[6] for s in sections], dtype=float)
    median_rms = float(np.median(rms_ratios))
    median_opb = float(np.median(opbs)) if np.any(opbs > 0) else 0.0
    median_harm = float(np.median(harm_ratios)) if np.any(harm_ratios > 0) else 0.0
    median_perc = float(np.median(perc_ratios)) if np.any(perc_ratios > 0) else 0.0
    has_hpss = bool(np.all(harm_ratios > 0) and np.all(perc_ratios > 0))

    phrase_s = phrase_length * median_ibi
    min_break_s = _BREAK_MIN_PHRASES * phrase_s if phrase_s > 0 else 0.0
    min_short_break_s = _SHORT_BREAK_MIN_PHRASES * phrase_s if phrase_s > 0 else 0.0

    moderate_break_thr = median_rms * _BREAK_RMS_MODERATE_DROP
    break_opb_thr = median_opb * _BREAK_OPB_RATIO_TO_MEDIAN
    peak_rms_thr = median_rms * _PEAK_RMS_RATIO_TO_MEDIAN
    peak_opb_thr = median_opb * _PEAK_OPB_RATIO_TO_MEDIAN

    mid_range = range(1, n - 1)

    # Pass 1: four-branch break detection. Branch order matters: melodic,
    # percussive, severe (all HPSS-gated), then full (legacy rms/opb fallback).
    # Sections below the 2-phrase `break` floor but at least 1 phrase long get
    # the `short_break` label when the same branch classifier fires — this
    # surfaces 1-phrase dramatic dips without widening the main `break` floor.
    for i in mid_range:
        start_s, end_s, _energy, rms_ratio, opb, harm, perc = sections[i]
        seg_duration = end_s - start_s
        is_short = seg_duration < min_break_s
        if is_short and seg_duration < min_short_break_s:
            continue

        fired: str | None = None
        if has_hpss:
            if (
                harm < median_harm * _BREAK_MELODIC_HARM_RATIO
                and perc > median_perc * _BREAK_MELODIC_PERC_FLOOR
            ):
                fired = "melodic"
            elif (
                perc < median_perc * _BREAK_PERCUSSIVE_PERC_RATIO
                and harm > median_harm * _BREAK_PERCUSSIVE_HARM_FLOOR
            ):
                fired = "percussive"
            elif (
                harm < median_harm * _BREAK_SEVERE_HARM_RATIO
                and perc < median_perc * _BREAK_SEVERE_PERC_RATIO
            ):
                fired = "severe"

        if fired is None:
            if rms_ratio < moderate_break_thr and opb < break_opb_thr:
                fired = "full"

        if fired in ("melodic", "percussive") and is_short:
            rms_strong = rms_ratio < median_rms * _SHORT_BREAK_STRONG_RMS_RATIO
            hpss_strong = (
                harm < median_harm * _SHORT_BREAK_STRONG_HPSS_RATIO
                or perc < median_perc * _SHORT_BREAK_STRONG_HPSS_RATIO
            )
            if not (rms_strong or hpss_strong):
                fired = None

        if fired is not None:
            labels[i] = "short_break" if is_short else "break"
            branch_names[i] = fired

    # Pass 2: peak detection — strongest mid section by RMS that also passes
    # the OPB gate and sits in the middle half of the track.
    mid_third_start = duration * 0.25
    mid_third_end = duration * 0.75
    peak_idx: int | None = None
    best_rms = -np.inf
    for i in mid_range:
        if labels[i] != "main":
            continue
        start_s, end_s, _energy, rms_ratio, opb, _harm, _perc = sections[i]
        mid_time = 0.5 * (start_s + end_s)
        if not (mid_third_start <= mid_time <= mid_third_end):
            continue
        if (
            rms_ratio > peak_rms_thr
            and opb > peak_opb_thr
            and rms_ratio > best_rms
        ):
            best_rms = rms_ratio
            peak_idx = i
    if peak_idx is not None:
        labels[peak_idx] = "peak"

    # Pass 3: build — a main section immediately before a peak with rising RMS.
    for i in mid_range:
        if labels[i] != "main":
            continue
        next_i = i + 1
        if next_i >= n or labels[next_i] != "peak":
            continue
        prev_rms = sections[i - 1][3]
        cur_rms = sections[i][3]
        if cur_rms > prev_rms:
            labels[i] = "build"

    return [(s[0], s[1], labels[i], branch_names[i]) for i, s in enumerate(sections)]


def compute_rhythm_features_windowed(
    audio: AudioData,
    onsets: OnsetData,
    beats: BeatData,
    beats_per_measure: int,
    start_s: float,
    end_s: float,
) -> RhythmFeatures | None:
    """Compute RhythmFeatures for a time window [start_s, end_s].

    Returns ``None`` if the window has too few beats/onsets for meaningful stats.
    """
    # Filter beats and onsets to this window
    beat_mask = (beats.times >= start_s) & (beats.times < end_s)
    onset_mask = (onsets.times >= start_s) & (onsets.times < end_s)
    window_beats = beats.times[beat_mask]
    window_onsets = onsets.times[onset_mask]

    n_beats = len(window_beats)
    n_onsets = len(window_onsets)
    if n_beats < 2:
        return None

    onsets_per_beat = float(n_onsets / n_beats) if n_beats > 0 else 0.0

    # Beat-position strengths within this window
    strength = librosa.onset.onset_strength(y=audio.samples, sr=audio.sr)
    strength_times = librosa.frames_to_time(np.arange(len(strength)), sr=audio.sr)
    beat_strengths = np.interp(window_beats, strength_times, strength)
    bpm = min(beats_per_measure, n_beats)
    pattern_sums = np.array([
        float(beat_strengths[offset::bpm].mean()) for offset in range(bpm)
    ])
    max_val = pattern_sums.max() if pattern_sums.max() > 0 else 1.0
    beat_strength_pattern = (pattern_sums / max_val).tolist()

    # Slice audio for the window
    s_start = int(start_s * audio.sr)
    s_end = min(int(end_s * audio.sr), len(audio.samples))
    window_samples = audio.samples[s_start:s_end]
    if len(window_samples) < audio.sr * 0.5:
        return None

    harmonic, percussive = librosa.effects.hpss(window_samples)
    perc_energy = float(np.sum(percussive**2))
    total_energy = float(np.sum(window_samples**2))
    percussiveness = perc_energy / total_energy if total_energy > 0 else 0.0

    centroid = librosa.feature.spectral_centroid(y=window_samples, sr=audio.sr)
    spectral_centroid_mean = float(np.mean(centroid))

    ibi = np.diff(window_beats)
    tempo_stability = float(np.std(ibi) / np.mean(ibi)) if np.mean(ibi) > 0 else 0.0

    ioi_ms = np.diff(window_onsets) * 1000.0 if n_onsets > 1 else np.array([0.0])
    ioi_median_ms = float(np.median(ioi_ms))
    ioi_std_ms = float(np.std(ioi_ms))

    return RhythmFeatures(
        onsets_per_beat=onsets_per_beat,
        beat_strength_pattern=beat_strength_pattern,
        percussiveness=percussiveness,
        spectral_centroid_mean=spectral_centroid_mean,
        tempo_stability=tempo_stability,
        ioi_median_ms=ioi_median_ms,
        ioi_std_ms=ioi_std_ms,
        beat_clarity=_beat_clarity(beat_strength_pattern, percussiveness, tempo_stability),
    )


def _segment_opb(
    start_s: float,
    end_s: float,
    onset_times: np.ndarray,
    beat_times: np.ndarray,
) -> float:
    """Onsets per beat for a time window [start_s, end_s)."""
    n_onsets = int(np.sum((onset_times >= start_s) & (onset_times < end_s)))
    n_beats = int(np.sum((beat_times >= start_s) & (beat_times < end_s)))
    return n_onsets / n_beats if n_beats > 0 else 0.0


_SUBSPLIT_LONG_RUN_MIN_PHRASES = 8
_SUBSPLIT_LONG_RUN_SHIFT_FLOOR = 0.10
_SUBSPLIT_MIN_GAP_PHRASES = 2
_EMBEDDED_BREAK_MIN_RUN_PHRASES = 1
_EMBEDDED_BREAK_SCAN_MIN_PHRASES = 6


def _classify_break_branch(
    rms_ratio: float,
    opb: float,
    harm_ratio: float,
    perc_ratio: float,
    *,
    median_rms: float,
    median_opb: float,
    median_harm: float,
    median_perc: float,
    has_hpss: bool,
) -> str | None:
    """Return the name of the break branch that fires on this signal tuple,
    or None. Uses the same thresholds as ``_label_sections``' pass 1.
    """
    if has_hpss and median_harm > 0 and median_perc > 0:
        if (
            harm_ratio < median_harm * _BREAK_MELODIC_HARM_RATIO
            and perc_ratio > median_perc * _BREAK_MELODIC_PERC_FLOOR
        ):
            return "melodic"
        if (
            perc_ratio < median_perc * _BREAK_PERCUSSIVE_PERC_RATIO
            and harm_ratio > median_harm * _BREAK_PERCUSSIVE_HARM_FLOOR
        ):
            return "percussive"
        if (
            harm_ratio < median_harm * _BREAK_SEVERE_HARM_RATIO
            and perc_ratio < median_perc * _BREAK_SEVERE_PERC_RATIO
        ):
            return "severe"
    opb_thr = median_opb * _BREAK_OPB_RATIO_TO_MEDIAN if median_opb > 0 else float("inf")
    if rms_ratio < median_rms * _BREAK_RMS_MODERATE_DROP and opb < opb_thr:
        return "full"
    return None


def _split_embedded_breaks(
    labelled: list[tuple[float, float, str, str | None]],
    *,
    rms_envelope: np.ndarray,
    rms_times: np.ndarray,
    global_rms_mean: float,
    median_ibi: float,
    onsets: OnsetData,
    beats: BeatData,
    harm_envelope: np.ndarray | None = None,
    perc_envelope: np.ndarray | None = None,
    global_harm_mean: float = 0.0,
    global_perc_mean: float = 0.0,
    phrase_length: int = 8,
    min_run_phrases: int = _EMBEDDED_BREAK_MIN_RUN_PHRASES,
    min_section_phrases: int = _EMBEDDED_BREAK_SCAN_MIN_PHRASES,
) -> list[float]:
    """Find break runs embedded inside long ``main`` sections whose overall
    signal averages out to main-like but whose phrase-level signal
    individually hits a break branch.

    For each ``main`` section of at least ``min_section_phrases`` phrases,
    scan phrase-by-phrase using the same branch-classification thresholds as
    ``_label_sections`` (against track-level medians computed from the
    already-labelled sections). Contiguous runs of ``>= min_run_phrases``
    break-signature phrases produce a pair of boundaries isolating the
    embedded break, so ``_label_for`` can re-classify it on re-run.

    This is a Phase 8 addition — the sub-splitter's weighted-shift detector
    catches stand-out *transitions* but misses breaks whose *average*
    dilutes into the main they were segmented into (e.g. a 3-phrase break
    embedded in a 6-phrase main section — diluted to main-like aggregate).
    """
    if median_ibi <= 0 or global_rms_mean <= 0 or phrase_length < 1 or not labelled:
        return []
    phrase_s = phrase_length * median_ibi
    if phrase_s <= 0:
        return []

    has_hpss = (
        harm_envelope is not None
        and perc_envelope is not None
        and global_harm_mean > 0
        and global_perc_mean > 0
    )

    # Track-level medians from the already-labelled sections so we classify
    # embedded phrases against the same reference as _label_sections pass 1.
    rms_ratios: list[float] = []
    opbs: list[float] = []
    harm_ratios: list[float] = []
    perc_ratios: list[float] = []
    for start, end, _label, _branch in labelled:
        mask = (rms_times >= start) & (rms_times < end)
        seg_rms = float(rms_envelope[mask].mean()) if mask.any() else global_rms_mean
        rms_ratios.append(seg_rms / global_rms_mean)
        opbs.append(_segment_opb(start, end, onsets.times, beats.times))
        if has_hpss:
            seg_harm = float(harm_envelope[mask].mean()) if mask.any() else global_harm_mean
            seg_perc = float(perc_envelope[mask].mean()) if mask.any() else global_perc_mean
            harm_ratios.append(seg_harm / global_harm_mean)
            perc_ratios.append(seg_perc / global_perc_mean)
    median_rms = float(np.median(rms_ratios)) if rms_ratios else 1.0
    median_opb = float(np.median(opbs)) if opbs else 0.0
    median_harm = float(np.median(harm_ratios)) if harm_ratios and has_hpss else 0.0
    median_perc = float(np.median(perc_ratios)) if perc_ratios and has_hpss else 0.0

    extra: list[float] = []
    for start, end, label, _branch in labelled:
        if label != "main":
            continue
        duration = end - start
        n_phrases = int(duration / phrase_s)
        if n_phrases < min_section_phrases:
            continue

        # Classify each phrase inside the section.
        phrase_branch: list[str | None] = []
        for k in range(n_phrases):
            p_s = start + k * phrase_s
            p_e = p_s + phrase_s
            mask = (rms_times >= p_s) & (rms_times < p_e)
            seg_rms_mean = float(rms_envelope[mask].mean()) if mask.any() else global_rms_mean
            rms_r = seg_rms_mean / global_rms_mean
            opb = _segment_opb(p_s, p_e, onsets.times, beats.times)
            if has_hpss:
                seg_harm_mean = float(harm_envelope[mask].mean()) if mask.any() else global_harm_mean
                seg_perc_mean = float(perc_envelope[mask].mean()) if mask.any() else global_perc_mean
                harm_r = seg_harm_mean / global_harm_mean
                perc_r = seg_perc_mean / global_perc_mean
            else:
                harm_r = 1.0
                perc_r = 1.0
            phrase_branch.append(_classify_break_branch(
                rms_r, opb, harm_r, perc_r,
                median_rms=median_rms, median_opb=median_opb,
                median_harm=median_harm, median_perc=median_perc,
                has_hpss=has_hpss,
            ))

        # Find contiguous runs of break-signature phrases and emit the
        # boundaries that isolate each run. Never emit boundaries that
        # coincide with the section's own start / end — the section boundary
        # already exists and a zero-width injection would be a no-op.
        k = 0
        while k < n_phrases:
            if phrase_branch[k] is None:
                k += 1
                continue
            run_start = k
            while k < n_phrases and phrase_branch[k] is not None:
                k += 1
            run_end = k  # exclusive
            if run_end - run_start < min_run_phrases:
                continue
            left_t = start + run_start * phrase_s
            right_t = start + run_end * phrase_s
            if left_t > start + phrase_s * 0.5:
                extra.append(left_t)
            if right_t < end - phrase_s * 0.5:
                extra.append(right_t)

    return sorted(set(extra))


def _split_long_runs_on_phrase_shifts(
    labelled: list[tuple[float, float, str, str | None]],
    *,
    rms_envelope: np.ndarray,
    rms_times: np.ndarray,
    global_rms_mean: float,
    median_ibi: float,
    onsets: OnsetData | None = None,
    beats: BeatData | None = None,
    harm_envelope: np.ndarray | None = None,
    perc_envelope: np.ndarray | None = None,
    global_harm_mean: float = 0.0,
    global_perc_mean: float = 0.0,
    phrase_length: int = 8,
    min_section_phrases: float = 4.0,
    min_section_s: float = 24.0,
    shift_threshold: float = 0.18,
    long_run_min_phrases: int = _SUBSPLIT_LONG_RUN_MIN_PHRASES,
    long_run_shift_threshold: float = _SUBSPLIT_LONG_RUN_SHIFT_FLOOR,
    min_gap_phrases: int = _SUBSPLIT_MIN_GAP_PHRASES,
    splittable_labels: tuple[str, ...] = ("main",),
) -> list[float]:
    """Return phrase-aligned boundaries to inject inside long same-label runs
    where per-phrase weighted signal shifts exceed a local threshold.

    Walks contiguous same-label runs (not just individual sections) so a
    16-phrase ``main`` run spread across two sections can still expose
    internal structure.  The shift metric is a weighted L2 of
    ``(ΔRMS×, ΔH×, ΔP×, Δopb / 5)`` when HPSS and onset data are supplied,
    falling back to RMS-only when they are not.

    Long runs (``>= long_run_min_phrases``) use a lower floor
    (``long_run_shift_threshold``) and the 75th percentile within the run,
    so sub-structure in a 16-phrase main surfaces without needing a
    stand-out structural shift.  Shorter runs keep the Phase 6 thresholds.
    Inserted boundaries must be at least ``min_gap_phrases`` phrases from
    any existing boundary — the direct sliver guard from the Phase 6 revert.
    """
    if median_ibi <= 0 or global_rms_mean <= 0 or phrase_length < 1:
        return []
    phrase_s = phrase_length * median_ibi
    if phrase_s <= 0 or not labelled:
        return []

    has_hpss = (
        harm_envelope is not None
        and perc_envelope is not None
        and global_harm_mean > 0
        and global_perc_mean > 0
    )
    has_onsets = onsets is not None and beats is not None

    # Group labelled entries into contiguous same-label runs.
    runs: list[tuple[int, int, str]] = []
    i = 0
    n = len(labelled)
    while i < n:
        j = i + 1
        while j < n and labelled[j][2] == labelled[i][2]:
            j += 1
        runs.append((i, j, labelled[i][2]))
        i = j

    # Existing boundaries (all section starts + last section end) feed the
    # min-gap guard so we never insert a boundary within min_gap_phrases of
    # any boundary the initial segmentation already produced.
    existing_bounds: list[float] = sorted({labelled[0][0]} | {lb[1] for lb in labelled})
    gap_s = min_gap_phrases * phrase_s

    extra: list[float] = []
    for r_start_idx, r_end_idx_excl, label in runs:
        if label not in splittable_labels:
            continue
        run_start = labelled[r_start_idx][0]
        run_end = labelled[r_end_idx_excl - 1][1]
        duration = run_end - run_start
        if duration < min_section_s:
            continue
        n_phrases = int(duration / phrase_s)
        if n_phrases < min_section_phrases or n_phrases < 4:
            continue

        is_long_run = n_phrases >= long_run_min_phrases

        phrase_rms: list[float] = []
        phrase_harm: list[float] = []
        phrase_perc: list[float] = []
        phrase_opb: list[float] = []
        for k in range(n_phrases):
            p_start = run_start + k * phrase_s
            p_end = p_start + phrase_s
            mask = (rms_times >= p_start) & (rms_times < p_end)
            seg_rms = float(rms_envelope[mask].mean()) if mask.any() else global_rms_mean
            phrase_rms.append(seg_rms / global_rms_mean)
            if has_hpss:
                seg_harm = float(harm_envelope[mask].mean()) if mask.any() else global_harm_mean
                seg_perc = float(perc_envelope[mask].mean()) if mask.any() else global_perc_mean
                phrase_harm.append(seg_harm / global_harm_mean)
                phrase_perc.append(seg_perc / global_perc_mean)
            else:
                phrase_harm.append(1.0)
                phrase_perc.append(1.0)
            if has_onsets:
                phrase_opb.append(_segment_opb(p_start, p_end, onsets.times, beats.times))
            else:
                phrase_opb.append(0.0)

        d_rms = np.abs(np.diff(np.asarray(phrase_rms)))
        d_harm = np.abs(np.diff(np.asarray(phrase_harm)))
        d_perc = np.abs(np.diff(np.asarray(phrase_perc)))
        d_opb = np.abs(np.diff(np.asarray(phrase_opb)))
        shifts = np.sqrt(d_rms**2 + d_harm**2 + d_perc**2 + (d_opb / 5.0) ** 2)

        if is_long_run:
            base_thr = long_run_shift_threshold
            pctile = 75
        else:
            base_thr = shift_threshold
            pctile = 90
        local_thr = max(base_thr, float(np.percentile(shifts, pctile)))

        last_split = 0
        for k in range(len(shifts)):
            if shifts[k] <= local_thr:
                continue
            left_len = (k + 1) - last_split
            right_len = n_phrases - (k + 1)
            if left_len < 2 or right_len < 2:
                continue
            cand_t = run_start + (k + 1) * phrase_s
            # Sliver guard: reject if too close to any existing boundary
            # (incl. starts/ends of sections within this run).
            if any(abs(cand_t - b) < gap_s for b in existing_bounds):
                continue
            extra.append(cand_t)
            last_split = k + 1

    return sorted(set(extra))


def detect_sections(
    audio: AudioData,
    onsets: OnsetData,
    beats: BeatData,
    beats_per_measure: int = 4,
    *,
    min_section_s: float = _MIN_SECTION_S,
) -> list[SongSection]:
    """Segment a track into dancer-oriented sections.

    Returns a list of ``SongSection`` covering the full duration, in
    chronological order.  Each section has an energy level, a positional
    label (intro/main/break/build/peak/outro), and optionally per-section
    ``RhythmFeatures``.
    """
    novelty, times = _compute_novelty_curve(audio)
    boundaries = _segment_boundaries(
        novelty, times, audio.duration, min_section_s=min_section_s,
    )

    if len(boundaries) < 2:
        boundaries = [0.0, audio.duration]

    # Compute per-segment RMS ratio and onsets-per-beat. These feed both the
    # percentile energy classifier and the signal-aware label decider.
    hop = _NOVELTY_HOP_FRAMES
    rms = librosa.feature.rms(y=audio.samples, hop_length=hop)[0]
    rms_times = librosa.frames_to_time(np.arange(len(rms)), sr=audio.sr, hop_length=hop)
    global_rms_mean = float(rms.mean()) if len(rms) > 0 else 1.0

    # HPSS-derived per-segment harmonic / percussive RMS ratios.  These give
    # the four-branch break classifier a melodic-vs-percussion signal the
    # global RMS rule cannot see (e.g. kizomba melodic drop where tumba keeps
    # playing).  Computed once per track, reused per segment.
    y_harm, y_perc = librosa.effects.hpss(audio.samples, margin=_HPSS_MARGIN)
    harm_rms = librosa.feature.rms(y=y_harm, hop_length=hop)[0]
    perc_rms = librosa.feature.rms(y=y_perc, hop_length=hop)[0]
    global_harm_mean = float(harm_rms.mean()) if len(harm_rms) > 0 else 1.0
    global_perc_mean = float(perc_rms.mean()) if len(perc_rms) > 0 else 1.0

    # Use median inter-beat interval so the "at least 2 phrases long" break
    # guard adapts to this track's tempo rather than assuming 120 BPM.
    if len(beats.times) >= 2:
        median_ibi = float(np.median(np.diff(beats.times)))
    else:
        median_ibi = 0.5

    def _label_for(bounds: list[float]) -> tuple[
        list[tuple[float, float]],
        list[float],
        list[float],
        list[float],
        list[float],
        list[str],
        list[tuple[float, float, str, str | None]],
    ]:
        """Run feature compute + energy classify + label pass on ``bounds``.

        Factored into a local closure so the sub-splitter can re-run this
        full pass on an expanded boundary list without duplicating code.
        """
        sb: list[tuple[float, float]] = []
        rr: list[float] = []
        op: list[float] = []
        hr: list[float] = []
        pr: list[float] = []
        for i in range(len(bounds) - 1):
            start, end = bounds[i], bounds[i + 1]
            mask = (rms_times >= start) & (rms_times < end)
            seg_rms = float(rms[mask].mean()) if mask.any() else global_rms_mean
            ratio = seg_rms / global_rms_mean if global_rms_mean > 0 else 1.0
            seg_harm_mean = float(harm_rms[mask].mean()) if mask.any() else global_harm_mean
            seg_perc_mean = float(perc_rms[mask].mean()) if mask.any() else global_perc_mean
            harm_ratio = seg_harm_mean / global_harm_mean if global_harm_mean > 0 else 1.0
            perc_ratio = seg_perc_mean / global_perc_mean if global_perc_mean > 0 else 1.0
            opb = _segment_opb(start, end, onsets.times, beats.times)
            sb.append((start, end))
            rr.append(ratio)
            op.append(opb)
            hr.append(harm_ratio)
            pr.append(perc_ratio)
        en = _classify_section_energies(rr)
        inp = [
            (b[0], b[1], en[i], rr[i], op[i], hr[i], pr[i])
            for i, b in enumerate(sb)
        ]
        lab = _label_sections(
            inp,
            audio.duration,
            median_ibi=median_ibi,
            phrase_length=_PHRASE_LENGTH_DEFAULT,
        )
        return sb, rr, op, hr, pr, en, lab

    seg_bounds, seg_rms_ratios, seg_opbs, seg_harm_ratios, seg_perc_ratios, energies, labelled = _label_for(boundaries)

    # Sub-phrase splitter: insert phrase-aligned boundaries inside long
    # individual main sections where per-phrase RMS shifts exceed a local
    # threshold. Narrow scope (individual sections only, main only, ≥ 4
    # phrases / 24 s) prevents the sliver regression from the previous
    # iteration of this helper.
    extra_bounds = _split_long_runs_on_phrase_shifts(
        labelled,
        rms_envelope=rms,
        rms_times=rms_times,
        global_rms_mean=global_rms_mean,
        median_ibi=median_ibi,
        onsets=onsets,
        beats=beats,
        harm_envelope=harm_rms,
        perc_envelope=perc_rms,
        global_harm_mean=global_harm_mean,
        global_perc_mean=global_perc_mean,
        phrase_length=_PHRASE_LENGTH_DEFAULT,
    )
    embedded_bounds = _split_embedded_breaks(
        labelled,
        rms_envelope=rms,
        rms_times=rms_times,
        global_rms_mean=global_rms_mean,
        median_ibi=median_ibi,
        onsets=onsets,
        beats=beats,
        harm_envelope=harm_rms,
        perc_envelope=perc_rms,
        global_harm_mean=global_harm_mean,
        global_perc_mean=global_perc_mean,
        phrase_length=_PHRASE_LENGTH_DEFAULT,
    )
    all_extra = sorted(set(list(extra_bounds) + list(embedded_bounds)))
    if all_extra:
        merged_bounds = sorted(set(list(boundaries) + all_extra))
        seg_bounds, seg_rms_ratios, seg_opbs, seg_harm_ratios, seg_perc_ratios, energies, labelled = _label_for(merged_bounds)

    sections: list[SongSection] = []
    for idx, (start, end, label, branch) in enumerate(labelled):
        features = compute_rhythm_features_windowed(
            audio, onsets, beats, beats_per_measure, start, end,
        )
        sections.append(SongSection(
            start_s=start,
            end_s=end,
            label=label,
            energy_level=energies[idx],
            rhythm_features=features,
            harm_ratio=seg_harm_ratios[idx],
            perc_ratio=seg_perc_ratios[idx],
            break_branch=branch,
        ))

    return sections


def _energy_split_points(run: list[SongSection]) -> list[int]:
    """Indices within a same-label run where it should split on sustained
    energy transitions.

    Only splits where both the preceding and following same-energy sub-runs
    are at least 2 sections long — a single-section blip will not fragment
    a phase.
    """
    n = len(run)
    if n < 4:
        return []
    splits: list[int] = []
    i = 1
    while i < n:
        if run[i].energy_level != run[i - 1].energy_level:
            left_len = 1
            j = i - 2
            while j >= 0 and run[j].energy_level == run[i - 1].energy_level:
                left_len += 1
                j -= 1
            right_len = 1
            k = i + 1
            while k < n and run[k].energy_level == run[i].energy_level:
                right_len += 1
                k += 1
            if left_len >= 2 and right_len >= 2:
                splits.append(i)
                i = k
                continue
        i += 1
    return splits


def _emit_phase(run: list[SongSection]) -> SongPhase:
    energies = [s.energy_level for s in run]
    features_list = [s.rhythm_features for s in run if s.rhythm_features is not None]
    avg_features = _average_rhythm_features(features_list) if features_list else None
    return SongPhase(
        label=run[0].label,
        start_s=run[0].start_s,
        end_s=run[-1].end_s,
        section_count=len(run),
        energy_levels=energies,
        avg_rhythm_features=avg_features,
    )


def merge_adjacent_sections(sections: list[SongSection]) -> list[SongPhase]:
    """Collapse consecutive same-label sections into phases.

    E.g. ``[main, main, main, break, main, main]`` → three phases:
    ``main ×3``, ``break ×1``, ``main ×2``.

    A long run of same-label sections is further split on sustained energy
    transitions: a ``main`` run whose energies read
    ``[med, med, high, high, med, med]`` becomes three ``main`` phases, so
    the learner can see the internal energy arc without inventing new
    boundaries.  Single-section energy blips never cause a split.

    Each phase records the merged time range, section count, all energy
    levels seen, and averaged rhythm features.
    """
    if not sections:
        return []

    phases: list[SongPhase] = []
    run_start = 0

    for i in range(1, len(sections) + 1):
        if i < len(sections) and sections[i].label == sections[run_start].label:
            continue
        run = sections[run_start:i]
        splits = _energy_split_points(run)
        prev = 0
        for split in splits:
            phases.append(_emit_phase(run[prev:split]))
            prev = split
        phases.append(_emit_phase(run[prev:]))
        run_start = i

    return phases


_MERGE_BREAK_CHAIN_MIN = 3  # only collapse chains of ≥ 3 same-branch break sections


def _merge_same_branch_break_chains(
    sections: list[SongSection],
    *,
    min_chain: int = _MERGE_BREAK_CHAIN_MIN,
) -> list[SongSection]:
    """Collapse runs of ≥ ``min_chain`` adjacent same-branch break sections.

    Addresses the Charbel-E-Magia-4K pattern where the agglomerative
    segmentation splits what a listener hears as a single long break into
    many short `break[melodic]` rows.  Only runs that meet BOTH gates fuse:
    label in {"break", "short_break"} AND matching ``break_branch``.
    Runs of ``min_chain - 1`` or fewer are left alone so two nearby but
    genuinely separate breaks don't melt into one.

    Signal ratios (``harm_ratio``, ``perc_ratio``) are duration-weighted
    across the run; ``rhythm_features`` are averaged via
    ``_average_rhythm_features``.
    """
    if not sections:
        return sections

    merged: list[SongSection] = []
    i = 0
    n = len(sections)
    while i < n:
        cur = sections[i]
        if cur.label not in ("break", "short_break") or cur.break_branch is None:
            merged.append(cur)
            i += 1
            continue
        j = i + 1
        while (
            j < n
            and sections[j].label in ("break", "short_break")
            and sections[j].break_branch == cur.break_branch
        ):
            j += 1
        run = sections[i:j]
        if len(run) < min_chain:
            merged.extend(run)
            i = j
            continue

        durations = [s.end_s - s.start_s for s in run]
        total = sum(durations) if sum(durations) > 0 else 1.0

        def _dw(attr: str) -> float | None:
            vals = [(getattr(s, attr), d) for s, d in zip(run, durations)
                    if getattr(s, attr) is not None]
            if not vals:
                return None
            num = sum(v * d for v, d in vals)
            den = sum(d for _, d in vals)
            return num / den if den > 0 else None

        features_list = [s.rhythm_features for s in run if s.rhythm_features is not None]
        avg_features = (
            _average_rhythm_features(features_list) if features_list else None
        )
        energies = [s.energy_level for s in run]
        dominant_energy = max(set(energies), key=energies.count)
        # Prefer "break" over "short_break" when any run member is a full break.
        fused_label = "break" if any(s.label == "break" for s in run) else "short_break"

        merged.append(SongSection(
            start_s=run[0].start_s,
            end_s=run[-1].end_s,
            label=fused_label,
            energy_level=dominant_energy,
            rhythm_features=avg_features,
            accent_description=run[0].accent_description,
            raw_start_s=run[0].raw_start_s,
            raw_end_s=run[-1].raw_end_s,
            harm_ratio=_dw("harm_ratio"),
            perc_ratio=_dw("perc_ratio"),
            break_branch=cur.break_branch,
        ))
        i = j

    return merged


def _average_rhythm_features(features: list[RhythmFeatures]) -> RhythmFeatures:
    """Compute element-wise average of multiple RhythmFeatures."""
    n = len(features)
    # Average beat_strength_pattern — use shortest common length
    min_len = min(len(f.beat_strength_pattern) for f in features)
    avg_pattern = [
        sum(f.beat_strength_pattern[j] for f in features) / n
        for j in range(min_len)
    ]
    return RhythmFeatures(
        onsets_per_beat=sum(f.onsets_per_beat for f in features) / n,
        beat_strength_pattern=avg_pattern,
        percussiveness=sum(f.percussiveness for f in features) / n,
        spectral_centroid_mean=sum(f.spectral_centroid_mean for f in features) / n,
        tempo_stability=sum(f.tempo_stability for f in features) / n,
        ioi_median_ms=sum(f.ioi_median_ms for f in features) / n,
        ioi_std_ms=sum(f.ioi_std_ms for f in features) / n,
        beat_clarity=sum(f.beat_clarity for f in features) / n,
    )


_PHRASE_LENGTH_DEFAULT = 8
_SNAP_MAX_DRIFT_BEATS = 8.0  # up to one full phrase of drift allowed


def _snap_boundaries_to_phrases(
    sections: list[SongSection],
    beats: BeatData,
    phrase_length: int = _PHRASE_LENGTH_DEFAULT,
    max_drift_beats: float = _SNAP_MAX_DRIFT_BEATS,
    offset: int = 0,
) -> list[SongSection]:
    """Snap interior section boundaries to the nearest phrase-grid beat time.

    The phrase grid is ``beats.times[offset::phrase_length]`` — every Nth beat
    starting from the detected downbeat offset, where N is ``phrase_length``
    (default 8 for dancer 8-count in 4/4).
    Only interior boundaries are moved; the first section's start and the
    last section's end stay at their original values.

    A boundary is snapped only if its drift to the nearest grid point is at
    most ``max_drift_beats × median_inter_beat_interval`` seconds.  After
    snapping, monotonicity is enforced — if a snap would create a zero- or
    negative-length section, the snap is reverted.

    Each returned section preserves its original pre-snap boundaries as
    ``raw_start_s`` / ``raw_end_s`` when the snap actually moved the value;
    otherwise these fields stay ``None``.  ``rhythm_features`` are NOT
    recomputed — they remain as originally windowed from the raw boundaries.
    """
    if (
        len(sections) < 2
        or len(beats.times) < phrase_length
        or phrase_length < 1
    ):
        return sections

    phrase_times = beats.times[offset::phrase_length]
    if len(phrase_times) == 0:
        return sections

    ibi = np.diff(beats.times)
    median_ibi = float(np.median(ibi)) if len(ibi) > 0 else 0.5
    max_drift_s = max_drift_beats * median_ibi

    def snap(t: float) -> tuple[float, bool]:
        idx = int(np.argmin(np.abs(phrase_times - t)))
        target = float(phrase_times[idx])
        if abs(target - t) <= max_drift_s:
            return target, True
        return t, False

    interior_raw = [sections[i].end_s for i in range(len(sections) - 1)]
    interior_snap = [snap(t) for t in interior_raw]

    # Enforce monotonicity against the previous boundary (first section start
    # initially, then each resolved boundary) and against the last section end.
    resolved: list[tuple[float, bool]] = []
    prev = sections[0].start_s
    last_end = sections[-1].end_s
    for i, (t_snap, moved) in enumerate(interior_snap):
        raw = interior_raw[i]
        cand = t_snap if moved else raw
        if cand <= prev or cand >= last_end:
            # Revert to raw if safe; otherwise keep prev (pathological).
            if raw > prev and raw < last_end:
                resolved.append((raw, False))
                prev = raw
            else:
                resolved.append((prev, False))
        else:
            resolved.append((cand, moved))
            prev = cand

    new_sections: list[SongSection] = []
    for i, sec in enumerate(sections):
        if i == 0:
            new_start = sec.start_s
            raw_start = None
        else:
            t_new, moved = resolved[i - 1]
            new_start = t_new
            raw_start = sec.start_s if moved else None

        if i == len(sections) - 1:
            new_end = sec.end_s
            raw_end = None
        else:
            t_new, moved = resolved[i]
            new_end = t_new
            raw_end = sec.end_s if moved else None

        new_sections.append(SongSection(
            start_s=new_start,
            end_s=new_end,
            label=sec.label,
            energy_level=sec.energy_level,
            rhythm_features=sec.rhythm_features,
            accent_description=sec.accent_description,
            raw_start_s=raw_start,
            raw_end_s=raw_end,
            harm_ratio=sec.harm_ratio,
            perc_ratio=sec.perc_ratio,
            break_branch=sec.break_branch,
        ))
    return new_sections


_EDGE_EXPAND_MAX_PHRASES = 3
_EDGE_NEIGHBOUR_MIN_PHRASES = 2
_EDGE_CONTRACT_MAX_PHRASES = 2
_EDGE_CONTRACT_MIN_REMAINING_PHRASES = 2


def _expand_label_edges_on_signal(
    sections: list[SongSection],
    beats: BeatData,
    onsets: OnsetData,
    *,
    rms_envelope: np.ndarray,
    rms_times: np.ndarray,
    global_rms_mean: float,
    harm_envelope: np.ndarray | None = None,
    perc_envelope: np.ndarray | None = None,
    global_harm_mean: float = 0.0,
    global_perc_mean: float = 0.0,
    phrase_length: int = _PHRASE_LENGTH_DEFAULT,
    offset: int = 0,
    max_expand_phrases: int = _EDGE_EXPAND_MAX_PHRASES,
    neighbour_min_phrases: int = _EDGE_NEIGHBOUR_MIN_PHRASES,
    max_contract_phrases: int = _EDGE_CONTRACT_MAX_PHRASES,
    contract_min_remaining_phrases: int = _EDGE_CONTRACT_MIN_REMAINING_PHRASES,
) -> list[SongSection]:
    """Expand or contract ``break`` / ``peak`` edges one phrase at a time
    based on per-phrase ``(RMS×, opb, H×, P×)`` signal support.

    **Expansion** absorbs adjacent phrases whose signals still match the
    section's label. Neighbour section boundaries are moved to match.

    **Contraction** walks the first/last phrase inside the section and
    sheds it to the neighbour if the phrase's signal no longer supports the
    label. Uses the same support criterion as expansion, so a phrase sitting
    at the threshold does not flip-flop — expansion wouldn't have added it
    and contraction won't remove it either. Contraction runs after
    expansion, so any just-absorbed phrase is stable by construction.

    Stops per edge when any of:
    - The adjacent section is another ``break`` or ``peak`` (can't eat interior).
    - The neighbour would shrink below ``neighbour_min_phrases``.
    - Expansion: adjacent phrase fails the label's signature criteria.
    - Contraction: the first/last phrase inside the section DOES match (stop).
    - ``max_expand_phrases`` / ``max_contract_phrases`` absorbed / shed on that edge.
    - Contraction never shrinks a section below ``contract_min_remaining_phrases``.

    The first / last section boundaries (song start / end) are never moved.
    ``rhythm_features`` and ``raw_start_s`` / ``raw_end_s`` are preserved as-is
    — this pass does not recompute per-section features.
    """
    n = len(sections)
    if n < 3 or phrase_length < 1:
        return sections
    if len(beats.times) < phrase_length or global_rms_mean <= 0:
        return sections

    phrase_times = beats.times[offset::phrase_length]
    if len(phrase_times) < 3:
        return sections

    has_hpss = (
        harm_envelope is not None
        and perc_envelope is not None
        and global_harm_mean > 0
        and global_perc_mean > 0
    )

    # Track-level medians from the current labelled sections. Harm / perc
    # medians are only meaningful when HPSS data is present.
    rms_ratios: list[float] = []
    opbs: list[float] = []
    harm_ratios: list[float] = []
    perc_ratios: list[float] = []
    for sec in sections:
        mask = (rms_times >= sec.start_s) & (rms_times < sec.end_s)
        seg_rms = float(rms_envelope[mask].mean()) if mask.any() else global_rms_mean
        rms_ratios.append(seg_rms / global_rms_mean)
        opbs.append(_segment_opb(sec.start_s, sec.end_s, onsets.times, beats.times))
        if sec.harm_ratio is not None:
            harm_ratios.append(sec.harm_ratio)
        if sec.perc_ratio is not None:
            perc_ratios.append(sec.perc_ratio)

    median_rms = float(np.median(rms_ratios)) if rms_ratios else 1.0
    median_opb = float(np.median(opbs)) if opbs else 0.0
    median_harm = float(np.median(harm_ratios)) if harm_ratios and has_hpss else 0.0
    median_perc = float(np.median(perc_ratios)) if perc_ratios and has_hpss else 0.0

    def phrase_rms_ratio(p_start: float, p_end: float) -> float:
        mask = (rms_times >= p_start) & (rms_times < p_end)
        seg = float(rms_envelope[mask].mean()) if mask.any() else global_rms_mean
        return seg / global_rms_mean

    def phrase_harm_ratio(p_start: float, p_end: float) -> float:
        if not has_hpss:
            return 1.0
        mask = (rms_times >= p_start) & (rms_times < p_end)
        seg = float(harm_envelope[mask].mean()) if mask.any() else global_harm_mean
        return seg / global_harm_mean

    def phrase_perc_ratio(p_start: float, p_end: float) -> float:
        if not has_hpss:
            return 1.0
        mask = (rms_times >= p_start) & (rms_times < p_end)
        seg = float(perc_envelope[mask].mean()) if mask.any() else global_perc_mean
        return seg / global_perc_mean

    def phrase_signals(p_start: float, p_end: float) -> tuple[float, float, float, float]:
        return (
            phrase_rms_ratio(p_start, p_end),
            _segment_opb(p_start, p_end, onsets.times, beats.times),
            phrase_harm_ratio(p_start, p_end),
            phrase_perc_ratio(p_start, p_end),
        )

    def supports_break(branch: str | None, sig: tuple[float, float, float, float]) -> bool:
        rms_r, opb, harm_r, perc_r = sig
        if branch == "melodic" and has_hpss and median_harm > 0 and median_perc > 0:
            return (
                harm_r < median_harm * _BREAK_MELODIC_HARM_RATIO
                and perc_r > median_perc * _BREAK_MELODIC_PERC_FLOOR
            )
        if branch == "percussive" and has_hpss and median_harm > 0 and median_perc > 0:
            return (
                perc_r < median_perc * _BREAK_PERCUSSIVE_PERC_RATIO
                and harm_r > median_harm * _BREAK_PERCUSSIVE_HARM_FLOOR
            )
        if branch == "severe" and has_hpss and median_harm > 0 and median_perc > 0:
            return (
                harm_r < median_harm * _BREAK_SEVERE_HARM_RATIO
                and perc_r < median_perc * _BREAK_SEVERE_PERC_RATIO
            )
        # "full" branch (or unknown / legacy): rms drop + low opb
        moderate_thr = median_rms * _BREAK_RMS_MODERATE_DROP
        opb_thr = median_opb * _BREAK_OPB_RATIO_TO_MEDIAN if median_opb > 0 else float("inf")
        return rms_r < moderate_thr and opb < opb_thr

    def supports_peak(sig: tuple[float, float, float, float]) -> bool:
        rms_r, opb, _h, _p = sig
        peak_rms_thr = median_rms * _PEAK_RMS_RATIO_TO_MEDIAN
        peak_opb_thr = median_opb * _PEAK_OPB_RATIO_TO_MEDIAN
        return rms_r > peak_rms_thr and opb > peak_opb_thr

    def nearest_phrase_idx(t: float) -> int:
        return int(np.argmin(np.abs(phrase_times - t)))

    starts = [sec.start_s for sec in sections]
    ends = [sec.end_s for sec in sections]

    for i, sec in enumerate(sections):
        if sec.label not in ("break", "peak"):
            continue
        if i == 0 or i == n - 1:
            continue  # first / last section boundaries are fixed to song start / end

        # Try expanding the LEFT edge.
        k_start = nearest_phrase_idx(starts[i])
        for _ in range(max_expand_phrases):
            if k_start <= 0:
                break
            left_label = sections[i - 1].label
            if left_label in ("break", "peak"):
                break
            left_start_k = nearest_phrase_idx(starts[i - 1])
            # Neighbour needs >= neighbour_min_phrases remaining after shrinking.
            if (k_start - 1) - left_start_k < neighbour_min_phrases:
                break
            p_s = float(phrase_times[k_start - 1])
            p_e = float(phrase_times[k_start])
            sig = phrase_signals(p_s, p_e)
            if sec.label == "break" and not supports_break(sec.break_branch, sig):
                break
            if sec.label == "peak" and not supports_peak(sig):
                break
            k_start -= 1
            starts[i] = p_s
            ends[i - 1] = p_s

        # Try expanding the RIGHT edge.
        k_end = nearest_phrase_idx(ends[i])
        for _ in range(max_expand_phrases):
            if k_end >= len(phrase_times) - 1:
                break
            right_label = sections[i + 1].label
            if right_label in ("break", "peak"):
                break
            right_end_k = nearest_phrase_idx(ends[i + 1])
            if right_end_k - (k_end + 1) < neighbour_min_phrases:
                break
            p_s = float(phrase_times[k_end])
            p_e = float(phrase_times[k_end + 1])
            sig = phrase_signals(p_s, p_e)
            if sec.label == "break" and not supports_break(sec.break_branch, sig):
                break
            if sec.label == "peak" and not supports_peak(sig):
                break
            k_end += 1
            ends[i] = p_e
            starts[i + 1] = p_e

        # Try contracting the LEFT edge (shed first phrase if it doesn't match).
        k_start = nearest_phrase_idx(starts[i])
        for _ in range(max_contract_phrases):
            k_end_current = nearest_phrase_idx(ends[i])
            if (k_end_current - k_start) <= contract_min_remaining_phrases:
                break
            if k_start >= len(phrase_times) - 1:
                break
            p_s = float(phrase_times[k_start])
            p_e = float(phrase_times[k_start + 1])
            sig = phrase_signals(p_s, p_e)
            if sec.label == "break" and supports_break(sec.break_branch, sig):
                break  # first phrase supports the label — stop shrinking
            if sec.label == "peak" and supports_peak(sig):
                break
            k_start += 1
            starts[i] = p_e
            ends[i - 1] = p_e

        # Try contracting the RIGHT edge (shed last phrase if it doesn't match).
        k_end = nearest_phrase_idx(ends[i])
        for _ in range(max_contract_phrases):
            k_start_current = nearest_phrase_idx(starts[i])
            if (k_end - k_start_current) <= contract_min_remaining_phrases:
                break
            if k_end <= 0:
                break
            p_s = float(phrase_times[k_end - 1])
            p_e = float(phrase_times[k_end])
            sig = phrase_signals(p_s, p_e)
            if sec.label == "break" and supports_break(sec.break_branch, sig):
                break
            if sec.label == "peak" and supports_peak(sig):
                break
            k_end -= 1
            ends[i] = p_s
            starts[i + 1] = p_s

    new_sections: list[SongSection] = []
    for i, sec in enumerate(sections):
        new_sections.append(SongSection(
            start_s=starts[i],
            end_s=ends[i],
            label=sec.label,
            energy_level=sec.energy_level,
            rhythm_features=sec.rhythm_features,
            accent_description=sec.accent_description,
            raw_start_s=sec.raw_start_s,
            raw_end_s=sec.raw_end_s,
            harm_ratio=sec.harm_ratio,
            perc_ratio=sec.perc_ratio,
            break_branch=sec.break_branch,
        ))
    return new_sections


# --- Phase 9: vocal-aware intro/outro boundary passes ---


_VOCAL_MIN_ACTIVE_RATIO = 0.20       # ≥ 20% of frames active → phrase has vocals
_INTRO_MAX_EXTEND_PHRASES = 12       # cap blast radius of intro extension
_OUTRO_MAX_CONTRACT_PHRASES = 8      # cap blast radius of outro contraction
_OUTRO_GRACE_PHRASES = 1             # leave this many phrases of grace after last vocal

# --- Phase 10: instrumental passages (vocal-quiet but energy-present runs) ---
_INSTRUMENTAL_MIN_PHRASES = 2              # smallest run that qualifies for a relabel
_INSTRUMENTAL_MAX_VOCAL_ACTIVE_RATIO = 0.25  # below this = "vocals essentially absent"
_INSTRUMENTAL_MIN_RMS_RATIO = 0.75         # at/above this = "energy still present"

# --- Phase 11: spoken-intro detection (Gemma E4B speech-vs-singing) ---
_SPOKEN_INTRO_MIN_SPEECH_RATIO = 0.6       # leading phrase needs > this fraction of speech windows
_SPOKEN_INTRO_MIN_PHRASES = 2              # at least this many speech phrases needed to relabel

# --- Phase 42: demote vocal-active "break" labels (symmetric counterpart of Phase 10) ---
_VOCAL_BREAK_DEMOTE_MIN_RATIO = 0.50       # vocal_ratio above this disqualifies a break label
_VOCAL_BREAK_DEMOTE_KEEP_LOW_ENERGY = True # genuine vocal-led breaks tend to be low-energy


def _phrase_active_ratio(
    env: "VocalActivityEnvelope",
    start_s: float,
    end_s: float,
) -> float:
    """Fraction of `env` frames inside [start_s, end_s) flagged as vocal-active."""
    if end_s <= start_s:
        return 0.0
    mask = (env.times >= start_s) & (env.times < end_s)
    n = int(mask.sum())
    if n == 0:
        return 0.0
    return float(env.active[mask].sum()) / float(n)


def _extend_intro_to_first_vocal(
    sections: list[SongSection],
    vocal_env: "VocalActivityEnvelope | None",
    phrase_times: np.ndarray,
    *,
    min_active_ratio: float = _VOCAL_MIN_ACTIVE_RATIO,
    max_extend_phrases: int = _INTRO_MAX_EXTEND_PHRASES,
) -> list[SongSection]:
    """Grow the intro forward to the last pre-vocal phrase.

    Fixes the Propuesta Indecente / Emborrachare pattern where a long
    instrumental opening gets split by the novelty detector and the second
    chunk mis-labelled as `main` or `break[full]`.  When a vocal envelope is
    available, we identify the first phrase with ≥ ``min_active_ratio``
    active frames and absorb all preceding same-era sections into the intro
    up to that boundary (capped at ``max_extend_phrases`` phrases of growth).
    """
    if vocal_env is None or not sections or len(phrase_times) < 2:
        return sections

    # First phrase index whose [phrase_times[i], phrase_times[i+1]) window is "vocal-active".
    first_vocal_idx: int | None = None
    for i in range(len(phrase_times) - 1):
        ratio = _phrase_active_ratio(
            vocal_env, float(phrase_times[i]), float(phrase_times[i + 1]),
        )
        if ratio >= min_active_ratio:
            first_vocal_idx = i
            break
    if first_vocal_idx is None:
        return sections

    target_time = float(phrase_times[first_vocal_idx])
    intro = sections[0]
    if target_time <= intro.end_s + 1e-9:
        return sections  # vocals begin within the existing intro

    # Enforce the max-extend cap.
    intro_end_idx = int(np.argmin(np.abs(phrase_times - intro.end_s)))
    max_target_idx = min(first_vocal_idx, intro_end_idx + max_extend_phrases)
    target_time = float(phrase_times[max_target_idx])
    if target_time <= intro.end_s + 1e-9:
        return sections

    # Walk subsequent sections and either fully absorb (end ≤ target) or
    # clip the partial-absorption boundary for the first survivor.
    new_intro_end = intro.end_s
    first_survivor_idx = len(sections)  # index of first section kept after the intro
    for i in range(1, len(sections)):
        sec = sections[i]
        if sec.end_s <= target_time + 1e-9:
            new_intro_end = sec.end_s
            continue
        # This section straddles target_time; clip it and stop.
        if sec.start_s < target_time:
            new_intro_end = target_time
        first_survivor_idx = i
        break

    out: list[SongSection] = [SongSection(
        start_s=intro.start_s,
        end_s=new_intro_end,
        label="intro",
        energy_level=intro.energy_level,
        rhythm_features=intro.rhythm_features,
        accent_description=intro.accent_description,
        raw_start_s=intro.raw_start_s,
        raw_end_s=intro.raw_end_s,
        harm_ratio=intro.harm_ratio,
        perc_ratio=intro.perc_ratio,
        break_branch=None,  # intros never carry a break branch
    )]
    for i in range(first_survivor_idx, len(sections)):
        sec = sections[i]
        if i == first_survivor_idx and sec.start_s < new_intro_end - 1e-9:
            # Trim partially-absorbed successor.
            if sec.end_s <= new_intro_end + 1e-9:
                continue
            out.append(SongSection(
                start_s=new_intro_end,
                end_s=sec.end_s,
                label=sec.label,
                energy_level=sec.energy_level,
                rhythm_features=sec.rhythm_features,
                accent_description=sec.accent_description,
                raw_start_s=sec.raw_start_s,
                raw_end_s=sec.raw_end_s,
                harm_ratio=sec.harm_ratio,
                perc_ratio=sec.perc_ratio,
                break_branch=sec.break_branch,
            ))
        else:
            out.append(sec)
    return out


def _contract_outro_to_last_vocal(
    sections: list[SongSection],
    vocal_env: "VocalActivityEnvelope | None",
    phrase_times: np.ndarray,
    *,
    min_active_ratio: float = _VOCAL_MIN_ACTIVE_RATIO,
    max_contract_phrases: int = _OUTRO_MAX_CONTRACT_PHRASES,
    grace_phrases: int = _OUTRO_GRACE_PHRASES,
) -> list[SongSection]:
    """Pull the outro start earlier, to just after the last sustained vocal phrase.

    Symmetric to the intro pass.  Only runs if the current outro's start is
    later than `last_vocal_phrase + grace_phrases`.  Bounded by
    `max_contract_phrases` so outros never grow by more than that many phrases.
    """
    if (
        vocal_env is None
        or len(sections) < 2
        or sections[-1].label != "outro"
        or len(phrase_times) < 2
    ):
        return sections

    # Last phrase with sustained activity.
    last_vocal_idx: int | None = None
    for i in range(len(phrase_times) - 1):
        ratio = _phrase_active_ratio(
            vocal_env, float(phrase_times[i]), float(phrase_times[i + 1]),
        )
        if ratio >= min_active_ratio:
            last_vocal_idx = i
    if last_vocal_idx is None:
        return sections

    target_idx = min(len(phrase_times) - 1, last_vocal_idx + 1 + grace_phrases)
    target_time = float(phrase_times[target_idx])
    outro = sections[-1]
    if target_time >= outro.start_s - 1e-9:
        return sections

    # Enforce max-contract cap: don't pull the outro earlier than
    # (current_outro_start − max_contract_phrases * phrase).
    outro_idx = int(np.argmin(np.abs(phrase_times - outro.start_s)))
    min_target_idx = max(0, outro_idx - max_contract_phrases)
    if target_idx < min_target_idx:
        target_time = float(phrase_times[min_target_idx])

    # Clip the previous section's end forward and move outro start.
    out: list[SongSection] = list(sections[:-2])
    prev = sections[-2]
    if prev.start_s >= target_time - 1e-9:
        # Would zero out the previous section; skip.
        return sections
    out.append(SongSection(
        start_s=prev.start_s,
        end_s=target_time,
        label=prev.label,
        energy_level=prev.energy_level,
        rhythm_features=prev.rhythm_features,
        accent_description=prev.accent_description,
        raw_start_s=prev.raw_start_s,
        raw_end_s=prev.raw_end_s,
        harm_ratio=prev.harm_ratio,
        perc_ratio=prev.perc_ratio,
        break_branch=prev.break_branch,
    ))
    out.append(SongSection(
        start_s=target_time,
        end_s=outro.end_s,
        label="outro",
        energy_level=outro.energy_level,
        rhythm_features=outro.rhythm_features,
        accent_description=outro.accent_description,
        raw_start_s=outro.raw_start_s,
        raw_end_s=outro.raw_end_s,
        harm_ratio=outro.harm_ratio,
        perc_ratio=outro.perc_ratio,
        break_branch=None,
    ))
    return out


def _relabel_vocal_drop_instrumentals(
    sections: list[SongSection],
    vocal_env: "VocalActivityEnvelope | None",
    phrase_times: np.ndarray,
    *,
    rms_envelope: np.ndarray,
    rms_times: np.ndarray,
    global_rms_mean: float,
    min_phrases: int = _INSTRUMENTAL_MIN_PHRASES,
    max_vocal_active_ratio: float = _INSTRUMENTAL_MAX_VOCAL_ACTIVE_RATIO,
    min_rms_ratio: float = _INSTRUMENTAL_MIN_RMS_RATIO,
) -> list[SongSection]:
    """Carve `instrumental` sub-sections out of vocal-quiet, high-energy runs.

    Catches the Propuesta (M84–M101), El Chaval (M44–M59) and Baila (~194 s)
    pattern: instruments continue at full strength but vocals drop for a
    multi-phrase stretch, and the novelty segmenter assigns `main` or `peak`
    because energy alone does not differentiate the passage.

    For each non-intro, non-outro section, the contained phrases are walked
    and any contiguous run of ≥ ``min_phrases`` phrases where

      * ``vocal_active_ratio < max_vocal_active_ratio``  (vocals absent), and
      * ``rms_ratio >= min_rms_ratio``                    (energy present)

    is relabelled as ``instrumental``.  If the whole section qualifies, the
    relabel happens in place (no sliver boundaries).  Otherwise the enclosing
    section is split around the qualifying run.  A ``peak`` that qualifies
    gets demoted to ``instrumental`` — dancer-relevant information survives
    in the label.
    """
    if vocal_env is None or not sections or len(phrase_times) < 2:
        return sections
    if global_rms_mean <= 0:
        return sections

    def phrase_rms_ratio(p_start: float, p_end: float) -> float:
        mask = (rms_times >= p_start) & (rms_times < p_end)
        seg = float(rms_envelope[mask].mean()) if mask.any() else global_rms_mean
        return seg / global_rms_mean

    def qualifies(p_start: float, p_end: float) -> bool:
        vocal_ratio = _phrase_active_ratio(vocal_env, p_start, p_end)
        rms_r = phrase_rms_ratio(p_start, p_end)
        return vocal_ratio < max_vocal_active_ratio and rms_r >= min_rms_ratio

    out: list[SongSection] = []
    for sec in sections:
        if sec.label in ("intro", "outro"):
            out.append(sec)
            continue

        # Gather only phrase windows that fit fully inside this section —
        # partial-overlap phrases would produce sliver boundaries.
        phrases_in_sec: list[tuple[float, float]] = []
        for i in range(len(phrase_times) - 1):
            ps = float(phrase_times[i])
            pe = float(phrase_times[i + 1])
            if pe <= sec.start_s + 1e-9 or ps >= sec.end_s - 1e-9:
                continue
            if ps < sec.start_s - 1e-9 or pe > sec.end_s + 1e-9:
                continue
            phrases_in_sec.append((ps, pe))

        if len(phrases_in_sec) < min_phrases:
            out.append(sec)
            continue

        # Find contiguous runs where both thresholds hold.
        runs: list[tuple[int, int]] = []  # inclusive (first_idx, last_idx) pairs
        run_start: int | None = None
        for i, (ps, pe) in enumerate(phrases_in_sec):
            if qualifies(ps, pe):
                if run_start is None:
                    run_start = i
            else:
                if run_start is not None and i - run_start >= min_phrases:
                    runs.append((run_start, i - 1))
                run_start = None
        if run_start is not None and len(phrases_in_sec) - run_start >= min_phrases:
            runs.append((run_start, len(phrases_in_sec) - 1))

        if not runs:
            out.append(sec)
            continue

        # Whole-section relabel: single run spanning all contained phrases.
        if len(runs) == 1 and runs[0] == (0, len(phrases_in_sec) - 1):
            out.append(SongSection(
                start_s=sec.start_s,
                end_s=sec.end_s,
                label="instrumental",
                energy_level=sec.energy_level,
                rhythm_features=sec.rhythm_features,
                accent_description=sec.accent_description,
                raw_start_s=sec.raw_start_s,
                raw_end_s=sec.raw_end_s,
                harm_ratio=sec.harm_ratio,
                perc_ratio=sec.perc_ratio,
                break_branch=None,
            ))
            continue

        # Partial: emit surrounding-section slivers around each instrumental run.
        cursor = sec.start_s
        for run_first, run_last in runs:
            run_start_time = phrases_in_sec[run_first][0]
            run_end_time = phrases_in_sec[run_last][1]
            if run_start_time > cursor + 1e-9:
                out.append(SongSection(
                    start_s=cursor,
                    end_s=run_start_time,
                    label=sec.label,
                    energy_level=sec.energy_level,
                    rhythm_features=sec.rhythm_features,
                    accent_description=sec.accent_description,
                    raw_start_s=None,
                    raw_end_s=None,
                    harm_ratio=sec.harm_ratio,
                    perc_ratio=sec.perc_ratio,
                    break_branch=sec.break_branch,
                ))
            out.append(SongSection(
                start_s=run_start_time,
                end_s=run_end_time,
                label="instrumental",
                energy_level=sec.energy_level,
                rhythm_features=sec.rhythm_features,
                accent_description=sec.accent_description,
                raw_start_s=None,
                raw_end_s=None,
                harm_ratio=sec.harm_ratio,
                perc_ratio=sec.perc_ratio,
                break_branch=None,
            ))
            cursor = run_end_time
        if cursor < sec.end_s - 1e-9:
            out.append(SongSection(
                start_s=cursor,
                end_s=sec.end_s,
                label=sec.label,
                energy_level=sec.energy_level,
                rhythm_features=sec.rhythm_features,
                accent_description=sec.accent_description,
                raw_start_s=None,
                raw_end_s=None,
                harm_ratio=sec.harm_ratio,
                perc_ratio=sec.perc_ratio,
                break_branch=sec.break_branch,
            ))
    return out


def _demote_vocal_active_breaks(
    sections: list[SongSection],
    vocal_env: "VocalActivityEnvelope | None",
    *,
    min_vocal_ratio: float = _VOCAL_BREAK_DEMOTE_MIN_RATIO,
    keep_low_energy: bool = _VOCAL_BREAK_DEMOTE_KEEP_LOW_ENERGY,
) -> list[SongSection]:
    """Reclassify `break` / `short_break` sections that are actually vocal-led.

    Symmetric counterpart of `_relabel_vocal_drop_instrumentals`: that helper
    catches vocal-quiet runs inside `main`/`peak` blocks; this one catches the
    inverse failure mode where the HPSS-driven break detector fires during a
    vocal-led passage (e.g. Charbel "E Magia" 35.9–51.2 s, where the singer
    enters but the percussion section is briefly thinned).

    A break is demoted to `main` (and its `break_branch` cleared) when:

      * vocal coverage across the section ≥ ``min_vocal_ratio`` (singer
        present for at least half of the frames), AND
      * energy_level is not ``"low"`` (when ``keep_low_energy=True``) — real
        vocal-led breaks in kizomba/bachata typically thin the band, so we
        keep the ``break`` label when the section is genuinely quiet.

    Conservative: only fires when ``vocal_env`` is available; intro/outro
    sections are left alone (they have their own dedicated post-passes).
    """
    if vocal_env is None or not sections:
        return sections

    out: list[SongSection] = []
    for sec in sections:
        if sec.label not in ("break", "short_break"):
            out.append(sec)
            continue
        if sec.label in ("intro", "outro"):  # defensive (break shouldn't be intro/outro)
            out.append(sec)
            continue
        if keep_low_energy and sec.energy_level == "low":
            out.append(sec)
            continue
        vocal_ratio = _phrase_active_ratio(vocal_env, sec.start_s, sec.end_s)
        if vocal_ratio < min_vocal_ratio:
            out.append(sec)
            continue
        # Demote: vocal-active, non-low-energy section labeled break is wrong.
        out.append(SongSection(
            start_s=sec.start_s,
            end_s=sec.end_s,
            label="main",
            energy_level=sec.energy_level,
            rhythm_features=sec.rhythm_features,
            accent_description=sec.accent_description,
            raw_start_s=sec.raw_start_s,
            raw_end_s=sec.raw_end_s,
            harm_ratio=sec.harm_ratio,
            perc_ratio=sec.perc_ratio,
            break_branch=None,
        ))
    return out


def _relabel_spoken_intro(
    sections: list[SongSection],
    speech_env: "VocalActivityEnvelope | None",
    phrase_times: np.ndarray,
    *,
    min_speech_ratio: float = _SPOKEN_INTRO_MIN_SPEECH_RATIO,
    min_phrases: int = _SPOKEN_INTRO_MIN_PHRASES,
) -> list[SongSection]:
    """Split or relabel the leading `intro` when its first phrases are speech.

    Targets the Propuesta P1–P8 pattern: a spoken-dialog opening reads as a
    low-energy `intro` band, but for coaching we want a distinct label so
    the prompt does not treat it as a singable intro.  When a Gemma-derived
    speech envelope (1.0 = speech, 0.0 = singing) is supplied:

    1. Walk leading phrases of the first section while it is `intro`.
    2. Compute per-phrase speech ratio (mean of `env.active` inside the
       phrase window).
    3. Find the longest contiguous prefix of phrases with speech-ratio
       above ``min_speech_ratio``.
    4. If that prefix has at least ``min_phrases`` phrases:
       - whole intro qualifies → relabel in place as ``spoken_intro``;
       - otherwise → split into ``spoken_intro`` prefix + ``intro`` suffix
         on the phrase-grid boundary.
    """
    if (
        speech_env is None
        or not sections
        or sections[0].label != "intro"
        or len(phrase_times) < 2
    ):
        return sections

    intro = sections[0]
    leading_phrases: list[tuple[float, float]] = []
    for i in range(len(phrase_times) - 1):
        ps = float(phrase_times[i])
        pe = float(phrase_times[i + 1])
        if pe <= intro.start_s + 1e-9:
            continue
        if ps >= intro.end_s - 1e-9:
            break
        if ps < intro.start_s - 1e-9 or pe > intro.end_s + 1e-9:
            continue
        leading_phrases.append((ps, pe))

    if len(leading_phrases) < min_phrases:
        return sections

    speech_prefix = 0
    for ps, pe in leading_phrases:
        if _phrase_active_ratio(speech_env, ps, pe) > min_speech_ratio:
            speech_prefix += 1
        else:
            break

    if speech_prefix < min_phrases:
        return sections

    if speech_prefix == len(leading_phrases):
        return [
            SongSection(
                start_s=intro.start_s,
                end_s=intro.end_s,
                label="spoken_intro",
                energy_level=intro.energy_level,
                rhythm_features=intro.rhythm_features,
                accent_description=intro.accent_description,
                raw_start_s=intro.raw_start_s,
                raw_end_s=intro.raw_end_s,
                harm_ratio=intro.harm_ratio,
                perc_ratio=intro.perc_ratio,
                break_branch=None,
            ),
            *sections[1:],
        ]

    split_time = leading_phrases[speech_prefix - 1][1]
    return [
        SongSection(
            start_s=intro.start_s,
            end_s=split_time,
            label="spoken_intro",
            energy_level=intro.energy_level,
            rhythm_features=intro.rhythm_features,
            accent_description=intro.accent_description,
            raw_start_s=intro.raw_start_s,
            raw_end_s=split_time,
            harm_ratio=intro.harm_ratio,
            perc_ratio=intro.perc_ratio,
            break_branch=None,
        ),
        SongSection(
            start_s=split_time,
            end_s=intro.end_s,
            label="intro",
            energy_level=intro.energy_level,
            rhythm_features=intro.rhythm_features,
            accent_description=intro.accent_description,
            raw_start_s=split_time,
            raw_end_s=intro.raw_end_s,
            harm_ratio=intro.harm_ratio,
            perc_ratio=intro.perc_ratio,
            break_branch=None,
        ),
        *sections[1:],
    ]


def describe_sections(analysis: RhythmAnalysis) -> str:
    """Return a human-readable table describing each detected section.

    Shows each section's time range, musical position in the same P#/M#
    coordinates the timeline chart uses, drift from the phrase grid in
    beats, duration in seconds and phrases, and per-section source signals
    (segment RMS vs global, onsets-per-beat) so the learner can see *why*
    each section was detected and whether its boundaries match musical
    phrasing.

    An asterisk next to the drift value marks boundaries that were snapped
    to the phrase grid by ``_snap_boundaries_to_phrases``; the drift shown
    is the pre-snap drift so the correction is visible.
    """
    sections = analysis.sections
    beats = analysis.beats.times
    bpm = analysis.beats_per_measure
    phrase_length = analysis.phrase_length
    offset = analysis.downbeat_offset or 0

    if len(sections) == 0:
        return "(no sections detected)"

    median_ibi = float(np.median(np.diff(beats))) if len(beats) > 1 else 0.5

    def phrase_measure_at(t: float) -> tuple[int, int]:
        if len(beats) == 0:
            return (1, 1)
        beat_idx = int(np.argmin(np.abs(beats - t)))
        rel = beat_idx - offset
        if rel < 0:
            return (0, 0)
        measure = rel // bpm + 1
        phrase = rel // phrase_length + 1
        return (phrase, measure)

    def drift_beats(t: float) -> float:
        if len(beats) < phrase_length:
            return 0.0
        phrase_times = beats[offset::phrase_length]
        if len(phrase_times) == 0:
            return 0.0
        idx = int(np.argmin(np.abs(phrase_times - t)))
        drift_s = t - float(phrase_times[idx])
        return drift_s / median_ibi if median_ibi > 0 else 0.0

    rms = librosa.feature.rms(y=analysis.audio.samples)[0]
    rms_times = librosa.frames_to_time(np.arange(len(rms)), sr=analysis.audio.sr)
    global_rms = float(rms.mean()) if len(rms) > 0 else 1.0

    lines: list[str] = []
    header = (
        f"Section table — {analysis.tempo:.0f} BPM, {bpm}/4, "
        f"{phrase_length}-count phrases, {len(sections)} sections"
    )
    lines.append(header)
    lines.append("=" * len(header))
    conf = analysis.downbeat_confidence or 0.0
    if offset > 0:
        lines.append(
            f"  downbeat offset = {offset} "
            f"(confidence = {conf:.2f})"
        )
    elif conf < _DOWNBEAT_OFFSET_MIN_CONFIDENCE and conf > 0:
        lines.append(
            f"  low downbeat confidence {conf:.2f}, "
            f"grid anchored to beat 0"
        )
    lines.append(
        f"{'#':>2} {'label':<16} {'energy':<7} {'time (s)':<15} "
        f"{'P/M':<14} {'drift':<10} {'dur':<13} {'signals (RMS×, opb, H×, P×)'}"
    )
    lines.append("-" * 120)

    any_snapped = False
    for i, sec in enumerate(sections):
        start_for_drift = sec.raw_start_s if sec.raw_start_s is not None else sec.start_s
        snap_mark = ""
        if sec.raw_start_s is not None or sec.raw_end_s is not None:
            snap_mark = "*"
            any_snapped = True

        start_drift = drift_beats(start_for_drift) if i > 0 else 0.0

        p_s, m_s = phrase_measure_at(sec.start_s)
        p_e, m_e = phrase_measure_at(sec.end_s)

        duration_s = sec.end_s - sec.start_s
        duration_phrases = (
            duration_s / (phrase_length * median_ibi) if median_ibi > 0 else 0.0
        )

        mask = (rms_times >= sec.start_s) & (rms_times < sec.end_s)
        seg_rms = float(rms[mask].mean()) if mask.any() else global_rms
        rms_ratio = seg_rms / global_rms if global_rms > 0 else 1.0

        onsets_in = int(np.sum(
            (analysis.onsets.times >= sec.start_s)
            & (analysis.onsets.times < sec.end_s)
        ))
        beats_in = int(np.sum(
            (beats >= sec.start_s) & (beats < sec.end_s)
        ))
        onsets_per_beat = onsets_in / beats_in if beats_in > 0 else 0.0

        time_str = f"{sec.start_s:5.1f}–{sec.end_s:5.1f}"
        pm_str = f"P{p_s}/M{m_s}→P{p_e}/M{m_e}"
        drift_str = "—" if i == 0 else f"{start_drift:+.1f}b{snap_mark}"
        dur_str = f"{duration_s:5.1f}s/{duration_phrases:4.1f}ph"
        hp_str = ""
        if sec.harm_ratio is not None and sec.perc_ratio is not None:
            hp_str = f" H×{sec.harm_ratio:.2f} P×{sec.perc_ratio:.2f}"
        bc_str = ""
        if sec.rhythm_features is not None:
            bc_str = f" BC={sec.rhythm_features.beat_clarity:.2f}"
        sig_str = f"RMS×{rms_ratio:.2f} opb={onsets_per_beat:.1f}{hp_str}{bc_str}"
        label_display = sec.label
        if sec.label in ("break", "short_break") and sec.break_branch is not None:
            label_display = f"{sec.label}[{sec.break_branch}]"
        lines.append(
            f"{i:>2} {label_display:<16} {sec.energy_level:<7} {time_str:<15} "
            f"{pm_str:<14} {drift_str:<10} {dur_str:<13} {sig_str}"
        )

    if any_snapped:
        lines.append("")
        lines.append("  * boundary snapped to phrase grid (drift shown is pre-snap)")

    return "\n".join(lines)


# ── Phase 40: transition extraction ──────────────────────────────────────────
# A transition is a label boundary between consecutive phases.  Same-label
# phase pairs (energy-only changes within a `main` run) are skipped — those
# are already covered by the section-role vocabulary in kizomba_tutor.

def _phase_clarity_tag(phase: SongPhase) -> str:
    """Return the qualitative beat-clarity label for a phase.

    Mirrors ``_beat_clarity_tag`` in prompts.py.  Duplicated here to avoid a
    dsp.py → prompts.py import dependency; the thresholds are simple enough
    that a small drift between the two would be obvious in tests.
    """
    rhythm_features = getattr(phase, "avg_rhythm_features", None)
    if rhythm_features is None:
        return "clear"
    beat_clarity = rhythm_features.beat_clarity
    if beat_clarity < 0.2:
        return "subtle"
    if beat_clarity < 0.35:
        return "moderate"
    return "clear"


def _phase_energy_tag(phase: SongPhase) -> str:
    """Return a single-word energy label for a phase."""
    energies = getattr(phase, "energy_levels", None) or []
    unique = sorted(set(energies))
    if len(unique) == 1:
        return unique[0]
    if not unique:
        return ""
    return "/".join(unique)


def extract_transitions(
    phases: list[SongPhase],
    *,
    include_same_label: bool = False,
) -> list[Transition]:
    """Yield transition events at phase boundaries.

    By default (``include_same_label=False``) only label-change
    boundaries are emitted (intro→main, main→break, break→main,
    main→outro, etc.).  Same-label runs are skipped — those are handled
    by the section-role vocabulary in ``QUESTION_KIZOMBA_TUTOR``.

    With ``include_same_label=True`` (Phase 40d) every consecutive phase
    boundary becomes a Transition, including same-label energy/role
    shifts (e.g. ``main ×4 [medium] → main ×2 [high]``).  The
    Transition's ``from_energy`` / ``to_energy`` fields carry the energy
    levels so consumers can distinguish label-change transitions from
    same-label energy shifts and coach them differently.

    Each :class:`Transition` carries the boundary time, the surrounding
    labels, the surrounding beat-clarity tags, the energy levels of the
    two phases, and the phase indices.  ``QUESTION_KIZOMBA_TRANSITIONS``
    consumes this list to produce per-transition coaching.
    """
    transitions: list[Transition] = []
    for i in range(1, len(phases)):
        prev = phases[i - 1]
        curr = phases[i]
        if prev.label == curr.label and not include_same_label:
            continue
        transitions.append(
            Transition(
                boundary_time_s=curr.start_s,
                from_label=prev.label,
                to_label=curr.label,
                from_clarity=_phase_clarity_tag(prev),
                to_clarity=_phase_clarity_tag(curr),
                from_phase_idx=i - 1,
                to_phase_idx=i,
                from_energy=_phase_energy_tag(prev),
                to_energy=_phase_energy_tag(curr),
            )
        )
    return transitions


def describe_transitions(
    analysis: RhythmAnalysis,
    *,
    include_same_label: bool = False,
) -> str:
    """Return a human-readable table of detected transitions.

    Parallel to :func:`describe_sections` — used both in the analysis dump
    that feeds Gemma (via ``_format_transitions_block`` in prompts.py) and
    for direct notebook display.

    The ``include_same_label`` flag mirrors :func:`extract_transitions` so
    notebook displays can show the same transition set the prompt sees.
    """
    transitions = extract_transitions(
        analysis.phases, include_same_label=include_same_label,
    )
    if not transitions:
        return "(no transitions detected — single-label song)"

    header = f"Transitions table — {len(transitions)} label boundaries"
    lines: list[str] = [header, "=" * len(header)]
    lines.append(
        " #  time   from              →  to                from→to beat   from→to energy"
    )
    lines.append("-" * 88)
    for i, tr in enumerate(transitions, 1):
        time_str = f"{tr.boundary_time_s:6.1f}s"
        from_str = f"{tr.from_label:<16}"
        to_str = f"{tr.to_label:<16}"
        beat_str = f"{tr.from_clarity:>8} → {tr.to_clarity:<8}"
        energy_str = (
            f"{tr.from_energy or '-':>6} → {tr.to_energy or '-':<6}"
            if tr.from_energy or tr.to_energy
            else "—"
        )
        lines.append(
            f"{i:>2}  {time_str}  {from_str}  →  {to_str}  {beat_str}   {energy_str}"
        )
    return "\n".join(lines)


def analyze(
    audio: AudioData,
    *,
    dance_style: str | None = None,
    snap_to_phrase_grid: bool = True,
    vocal_env: "VocalActivityEnvelope | None" = None,
    speech_env: "VocalActivityEnvelope | None" = None,
) -> RhythmAnalysis:
    """Run the full DSP pipeline: onsets, beats, tempo, IOIs, downbeats.

    When ``snap_to_phrase_grid`` is True (default), interior section
    boundaries that drift off the phrase grid by at most one phrase are
    snapped to the nearest phrase-grid beat.  Pre-snap boundaries are
    preserved on each ``SongSection`` as ``raw_start_s`` / ``raw_end_s`` so
    diagnostics can show the correction.

    ``vocal_env`` is an optional vocal-activity envelope produced by
    ``rytmi.vocal_activity``.  When provided, the intro is extended up to
    the first phrase with sustained vocal activity and the outro start is
    pulled back to where vocals have permanently faded.  When ``None``,
    those passes no-op and the pipeline behaves as before.

    ``speech_env`` is an optional speech-vs-singing envelope (e.g. from
    ``GemmaSpeechDetector``) covering the leading seconds of the track.
    When provided and the leading phrases of the intro are predominantly
    speech, the intro is split into a ``spoken_intro`` prefix + ``intro``
    suffix.  When ``None``, the spoken-intro pass no-ops.
    """
    onsets = detect_onsets(audio)
    beats = track_beats(audio, dance_style=dance_style)
    tempo = beats.tempo

    # Inter-onset intervals in milliseconds
    ioi = None
    if len(onsets.times) > 1:
        ioi = np.diff(onsets.times) * 1000.0  # seconds -> ms

    downbeats, bpm, downbeat_confidence, raw_offset = detect_downbeats(audio, beats)
    # Kizomba doesn't require exact downbeat alignment (any beat can serve
    # as "1"), so accept the DSP's best guess even when confidence is low.
    use_raw_offset = (
        downbeat_confidence >= _DOWNBEAT_OFFSET_MIN_CONFIDENCE
        or dance_style == "kizomba"
    )
    effective_offset = raw_offset if use_raw_offset else 0
    rhythm_features = compute_rhythm_features(audio, onsets, beats, bpm)
    tempo_half = tempo / 2.0 if tempo > 140 else None
    sections = detect_sections(audio, onsets, beats, bpm)
    if snap_to_phrase_grid:
        sections = _snap_boundaries_to_phrases(
            sections, beats, phrase_length=_PHRASE_LENGTH_DEFAULT,
            offset=effective_offset,
        )
        hop = _NOVELTY_HOP_FRAMES
        rms = librosa.feature.rms(y=audio.samples, hop_length=hop)[0]
        rms_t = librosa.frames_to_time(np.arange(len(rms)), sr=audio.sr, hop_length=hop)
        global_rms_mean = float(rms.mean()) if len(rms) > 0 else 1.0
        y_harm, y_perc = librosa.effects.hpss(audio.samples, margin=_HPSS_MARGIN)
        harm_rms = librosa.feature.rms(y=y_harm, hop_length=hop)[0]
        perc_rms = librosa.feature.rms(y=y_perc, hop_length=hop)[0]
        global_harm_mean = float(harm_rms.mean()) if len(harm_rms) > 0 else 0.0
        global_perc_mean = float(perc_rms.mean()) if len(perc_rms) > 0 else 0.0
        sections = _expand_label_edges_on_signal(
            sections, beats, onsets,
            rms_envelope=rms,
            rms_times=rms_t,
            global_rms_mean=global_rms_mean,
            harm_envelope=harm_rms,
            perc_envelope=perc_rms,
            global_harm_mean=global_harm_mean,
            global_perc_mean=global_perc_mean,
            phrase_length=_PHRASE_LENGTH_DEFAULT,
            offset=effective_offset,
        )
        sections = _merge_same_branch_break_chains(sections)
        if (
            (vocal_env is not None or speech_env is not None)
            and len(beats.times) >= _PHRASE_LENGTH_DEFAULT
        ):
            phrase_times = beats.times[effective_offset::_PHRASE_LENGTH_DEFAULT]
            if len(phrase_times) >= 2:
                if vocal_env is not None:
                    sections = _extend_intro_to_first_vocal(
                        sections, vocal_env, phrase_times,
                    )
                if speech_env is not None:
                    sections = _relabel_spoken_intro(
                        sections, speech_env, phrase_times,
                    )
                if vocal_env is not None:
                    sections = _contract_outro_to_last_vocal(
                        sections, vocal_env, phrase_times,
                    )
                    sections = _relabel_vocal_drop_instrumentals(
                        sections, vocal_env, phrase_times,
                        rms_envelope=rms,
                        rms_times=rms_t,
                        global_rms_mean=global_rms_mean,
                    )
                    sections = _demote_vocal_active_breaks(sections, vocal_env)
    # Phase 41-D — annotate every section with its vocal-active ratio so
    # downstream prompt formatters can surface per-phase vocal presence.
    if vocal_env is not None:
        for sec in sections:
            sec.vocal_ratio = _phrase_active_ratio(
                vocal_env, float(sec.start_s), float(sec.end_s),
            )
    phases = merge_adjacent_sections(sections)

    return RhythmAnalysis(
        audio=audio,
        onsets=onsets,
        beats=beats,
        tempo=tempo,
        inter_onset_intervals=ioi,
        downbeats=downbeats,
        beats_per_measure=bpm,
        phrase_length=_PHRASE_LENGTH_DEFAULT,
        downbeat_confidence=downbeat_confidence,
        downbeat_offset=effective_offset,
        rhythm_features=rhythm_features,
        tempo_half=tempo_half,
        dance_style=dance_style,
        sections=sections,
        phases=phases,
    )
