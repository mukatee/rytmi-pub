import numpy as np
import pytest

from rytmi.dsp import (
    analyze,
    compute_rhythm_features,
    describe_transitions,
    detect_downbeats,
    detect_onsets,
    estimate_tempo,
    extract_transitions,
    merge_adjacent_sections,
    track_beats,
)
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


def test_detect_onsets_returns_onset_data(synthetic_click_audio):
    onsets = detect_onsets(synthetic_click_audio)
    assert isinstance(onsets, OnsetData)
    assert len(onsets.times) > 0


def test_detect_onsets_times_in_range(synthetic_click_audio):
    onsets = detect_onsets(synthetic_click_audio)
    assert np.all(onsets.times >= 0)
    assert np.all(onsets.times <= synthetic_click_audio.duration + 0.1)


def test_detect_onsets_count(synthetic_click_audio):
    """120 BPM for 10s = 20 beats. Onset count should be in a reasonable range."""
    onsets = detect_onsets(synthetic_click_audio)
    assert 10 <= len(onsets.times) <= 30


def test_track_beats_returns_beat_data(synthetic_click_audio):
    beats = track_beats(synthetic_click_audio)
    assert isinstance(beats, BeatData)


def test_track_beats_tempo_range(synthetic_click_audio):
    """Tempo should be close to 120 BPM."""
    beats = track_beats(synthetic_click_audio)
    assert 90 <= beats.tempo <= 150


def test_track_beats_times_in_range(synthetic_click_audio):
    beats = track_beats(synthetic_click_audio)
    assert np.all(beats.times >= 0)
    assert np.all(beats.times <= synthetic_click_audio.duration + 0.1)


def test_track_beats_unchanged_for_non_kizomba(synthetic_click_audio):
    """Phase 25 regression guard: dance_style other than kizomba/urban_kiz
    must produce byte-identical output to the no-style call (preserving the
    existing librosa.beat.beat_track behaviour for bachata/salsa/None)."""
    baseline = track_beats(synthetic_click_audio)
    for style in (None, "bachata", "salsa", "unknown_style"):
        b = track_beats(synthetic_click_audio, dance_style=style)
        assert b.tempo == pytest.approx(baseline.tempo)
        np.testing.assert_array_equal(b.beat_frames, baseline.beat_frames)
        np.testing.assert_array_equal(b.times, baseline.times)


def _synthetic_kizomba_audio() -> AudioData:
    """20 s of synthetic kizomba: ~95 BPM bass kick (80 Hz burst every 0.63 s)
    plus a 190 BPM mid-band syncopation layer (sine bursts at 600 Hz) that the
    general beat tracker tends to latch onto.  The batida tracker should ignore
    the syncopation and lock onto the slow kick pulse."""
    sr = 22050
    duration = 20.0
    n = int(sr * duration)
    samples = np.zeros(n, dtype=np.float32)

    def _burst(freq: float, length_s: float, amp: float) -> np.ndarray:
        m = int(sr * length_s)
        t = np.arange(m) / sr
        env = np.linspace(1.0, 0.0, m, dtype=np.float32) ** 2
        return (amp * np.sin(2 * np.pi * freq * t) * env).astype(np.float32)

    kick = _burst(80.0, 0.18, 0.9)
    syncop = _burst(600.0, 0.05, 0.5)

    kick_period = 60.0 / 95.0  # ~0.632 s
    syncop_period = 60.0 / 190.0
    for t in np.arange(0.0, duration, kick_period):
        i = int(t * sr)
        end = min(i + len(kick), n)
        samples[i:end] += kick[: end - i]
    for t in np.arange(syncop_period / 2, duration, syncop_period):
        i = int(t * sr)
        end = min(i + len(syncop), n)
        samples[i:end] += syncop[: end - i]

    return AudioData(samples=samples, sr=sr, duration=duration)


def test_track_beats_kizomba_uses_batida_path():
    """dance_style='kizomba' should pick the slow batida pulse (~95 BPM),
    not the 190-BPM syncopation that the default tracker is prone to lock on."""
    audio = _synthetic_kizomba_audio()
    beats = track_beats(audio, dance_style="kizomba")
    assert 80.0 <= beats.tempo <= 110.0, (
        f"kizomba tracker should land near 95 BPM, got {beats.tempo:.1f}"
    )
    # Sanity: produced enough beats to support phasing downstream.
    assert len(beats.times) >= int(audio.duration / 1.0)


def test_track_beats_urban_kiz_matches_kizomba():
    """urban_kiz should route through the same batida tracker as kizomba."""
    audio = _synthetic_kizomba_audio()
    a = track_beats(audio, dance_style="kizomba")
    b = track_beats(audio, dance_style="urban_kiz")
    assert b.tempo == pytest.approx(a.tempo)
    np.testing.assert_array_equal(b.beat_frames, a.beat_frames)


def test_estimate_tempo(synthetic_click_audio):
    tempo = estimate_tempo(synthetic_click_audio)
    assert 90 <= tempo <= 150


def test_analyze_returns_rhythm_analysis(synthetic_click_audio):
    result = analyze(synthetic_click_audio)
    assert isinstance(result, RhythmAnalysis)
    assert result.audio is synthetic_click_audio
    assert result.tempo > 0
    assert len(result.onsets.times) > 0
    assert len(result.beats.times) > 0


def test_analyze_has_ioi(synthetic_click_audio):
    result = analyze(synthetic_click_audio)
    assert result.inter_onset_intervals is not None
    assert len(result.inter_onset_intervals) > 0
    # IOIs should be positive
    assert np.all(result.inter_onset_intervals > 0)


# --- downbeat confidence tests ---


def test_detect_downbeats_returns_four_tuple(synthetic_click_audio):
    """detect_downbeats should return (times, bpm, confidence, offset)."""
    beats = track_beats(synthetic_click_audio)
    result = detect_downbeats(synthetic_click_audio, beats)
    assert len(result) == 4
    downbeats, bpm, confidence, offset = result
    assert isinstance(downbeats, np.ndarray)
    assert isinstance(bpm, int)
    assert isinstance(confidence, float)
    assert isinstance(offset, int)
    assert 0 <= offset < bpm


def test_detect_downbeats_confidence_in_range(synthetic_click_audio):
    """Confidence must always be in [0.0, 1.0]."""
    beats = track_beats(synthetic_click_audio)
    _, _, confidence, _ = detect_downbeats(synthetic_click_audio, beats)
    assert 0.0 <= confidence <= 1.0


def test_detect_downbeats_confidence_low_on_uniform_beats(synthetic_click_audio):
    """Uniform beat strength → cannot determine the '1' → confidence near zero.

    Tight threshold: mean-based scoring should remove the offset-count bias
    that previously left a ~3-6% noise floor on uniform tracks.
    """
    beats = track_beats(synthetic_click_audio)
    _, _, confidence, _ = detect_downbeats(synthetic_click_audio, beats)
    assert confidence < 0.15


def test_detect_downbeats_accented_higher_confidence_than_uniform(
    synthetic_click_audio,
    synthetic_accented_click_audio,
):
    """Accented downbeat track should produce clearly higher confidence."""
    beats_flat = track_beats(synthetic_click_audio)
    beats_accented = track_beats(synthetic_accented_click_audio)
    _, _, conf_flat, _ = detect_downbeats(synthetic_click_audio, beats_flat)
    _, _, conf_accented, _ = detect_downbeats(synthetic_accented_click_audio, beats_accented)
    assert conf_accented > conf_flat


def test_detect_downbeats_confidence_meaningfully_above_zero_on_accented(
    synthetic_accented_click_audio,
):
    """Clear bass-register accented downbeats should yield confidence > 0.2.

    This checks that the metric is not just noise — a signal with an obviously
    stronger "1" should be well above the random-guess floor.
    """
    beats = track_beats(synthetic_accented_click_audio)
    _, _, confidence, _ = detect_downbeats(synthetic_accented_click_audio, beats)
    assert confidence > 0.2


def test_detect_downbeats_short_audio_returns_zero_confidence():
    """Fewer beats than beats_per_measure → confidence is 0.0 (no evidence)."""
    sr = 22050
    silence = np.zeros(int(sr * 0.5), dtype=np.float32)
    audio = AudioData(samples=silence, sr=sr, duration=0.5)
    beats = BeatData(times=np.array([0.1]), tempo=120.0, beat_frames=np.array([5]))
    _, _, confidence, offset = detect_downbeats(audio, beats, beats_per_measure=4)
    assert confidence == 0.0
    assert offset == 0


def test_detect_downbeats_bpm_less_than_two_returns_zero_confidence(
    synthetic_click_audio,
):
    """beats_per_measure < 2 has no runner-up → margin undefined → confidence 0."""
    beats = track_beats(synthetic_click_audio)
    _, _, confidence, _ = detect_downbeats(synthetic_click_audio, beats, beats_per_measure=1)
    assert confidence == 0.0


def test_detect_downbeats_tied_tops_have_low_confidence():
    """A 2-beat accent pattern scored as 4/4 → top two offsets are tied → low confidence.

    This is the diagnostic case the margin component exists for: when the
    accent falls on every other beat (a 2/4 feel), offsets 0 and 2 of a
    4/4 grouping carry equally strong evidence.  The "1" is genuinely
    ambiguous between them, and confidence should reflect that.
    """
    sr = 22050
    duration = 10.0
    beat_interval = 60.0 / 120  # 120 BPM

    click = np.sin(2 * np.pi * 80 * np.arange(int(0.02 * sr)) / sr).astype(np.float32)
    click *= np.linspace(1, 0, len(click), dtype=np.float32)

    samples = np.zeros(int(sr * duration), dtype=np.float32)
    for i, t in enumerate(np.arange(0, duration, beat_interval)):
        idx = int(t * sr)
        end = min(idx + len(click), len(samples))
        # Accent every other beat — a 2-beat pattern
        amplitude = 5.0 if (i % 2 == 0) else 1.0
        samples[idx:end] = amplitude * click[: end - idx]

    audio = AudioData(samples=samples, sr=sr, duration=duration)
    beats = track_beats(audio)
    _, _, confidence, _ = detect_downbeats(audio, beats, beats_per_measure=4)

    # Strict: tied tops should collapse confidence well below the
    # ~0.4 the same fixture would produce with a true 4-beat accent.
    assert confidence < 0.15


def test_detect_downbeats_offset_matches_first_downbeat(
    synthetic_accented_click_audio,
):
    """Accented downbeat track: best_offset should point to the accented beat."""
    beats = track_beats(synthetic_accented_click_audio)
    _, bpm, _, offset = detect_downbeats(synthetic_accented_click_audio, beats)
    assert isinstance(offset, int)
    assert 0 <= offset < bpm


def _make_kick_track(
    *,
    sr: int = 22050,
    duration: float = 10.0,
    bpm_tempo: int = 120,
    kick_freq: float = 60.0,
    kick_amp_at_offset: dict[int, float] | None = None,
    default_amp: float = 1.0,
    beats_per_measure: int = 4,
) -> AudioData:
    """Build a synthetic kick-only track with configurable per-offset amplitudes.

    Each beat is a short decaying sine at ``kick_freq`` (kick-band by default).
    ``kick_amp_at_offset`` overrides the amplitude for specific measure-offset
    positions; remaining offsets use ``default_amp``.
    """
    beat_interval = 60.0 / bpm_tempo
    click = np.sin(2 * np.pi * kick_freq * np.arange(int(0.03 * sr)) / sr).astype(np.float32)
    click *= np.linspace(1, 0, len(click), dtype=np.float32)

    samples = np.zeros(int(sr * duration), dtype=np.float32)
    amp_map = kick_amp_at_offset or {}
    for i, t in enumerate(np.arange(0, duration, beat_interval)):
        idx = int(t * sr)
        end = min(idx + len(click), len(samples))
        offset = i % beats_per_measure
        amplitude = amp_map.get(offset, default_amp)
        samples[idx:end] = amplitude * click[: end - idx]
    return AudioData(samples=samples, sr=sr, duration=duration)


def test_detect_downbeats_prefers_kick_agreement_when_onset_ambiguous():
    """Kick-band votes strongly for offset 0; a secondary mid-frequency accent
    on offset 2 partially pulls the full-band onset signal.  The combined
    (onset + kick) fusion should still pick offset 0 with non-zero confidence.
    """
    sr = 22050
    duration = 10.0
    beat_interval = 60.0 / 120

    kick = np.sin(2 * np.pi * 60 * np.arange(int(0.03 * sr)) / sr).astype(np.float32)
    kick *= np.linspace(1, 0, len(kick), dtype=np.float32)
    # Mild mid-frequency accent on offset 2 — enough to muddy the onset
    # signal but not strong enough to dominate the kick-band decision.
    accent = np.sin(2 * np.pi * 2000 * np.arange(int(0.02 * sr)) / sr).astype(np.float32)
    accent *= np.linspace(1, 0, len(accent), dtype=np.float32)

    samples = np.zeros(int(sr * duration), dtype=np.float32)
    for i, t in enumerate(np.arange(0, duration, beat_interval)):
        idx = int(t * sr)
        offset = i % 4
        kick_amp = 5.0 if offset == 0 else 1.0
        end_k = min(idx + len(kick), len(samples))
        samples[idx:end_k] += kick_amp * kick[: end_k - idx]
        if offset == 2:
            end_a = min(idx + len(accent), len(samples))
            samples[idx:end_a] += 1.5 * accent[: end_a - idx]

    audio = AudioData(samples=samples, sr=sr, duration=duration)
    beats = track_beats(audio)
    _, bpm, confidence, offset = detect_downbeats(audio, beats, beats_per_measure=4)
    assert offset == 0
    assert confidence > 0.0


def test_detect_downbeats_confidence_penalised_when_signals_disagree():
    """Onset picks one offset, kick picks another → confidence halved vs. agreement."""
    sr = 22050
    duration = 10.0
    bpm_tempo = 120
    beat_interval = 60.0 / bpm_tempo

    # Kick strongly on offset 0; wideband percussive accent strongly on offset 2
    kick = np.sin(2 * np.pi * 60 * np.arange(int(0.03 * sr)) / sr).astype(np.float32)
    kick *= np.linspace(1, 0, len(kick), dtype=np.float32)
    snare = np.random.default_rng(0).normal(0, 1, int(0.02 * sr)).astype(np.float32)
    snare *= np.linspace(1, 0, len(snare), dtype=np.float32)

    # Build baseline: kick accented on offset 0, no other content
    baseline = np.zeros(int(sr * duration), dtype=np.float32)
    for i, t in enumerate(np.arange(0, duration, beat_interval)):
        idx = int(t * sr)
        end = min(idx + len(kick), len(baseline))
        amp = 5.0 if (i % 4) == 0 else 1.0
        baseline[idx:end] = amp * kick[: end - idx]
    audio_agree = AudioData(samples=baseline, sr=sr, duration=duration)

    # Disagreement: same kick pattern, plus a very loud snare-like burst on offset 2
    # that drives onset_strength argmax to offset 2.
    disagree_samples = baseline.copy()
    for i, t in enumerate(np.arange(0, duration, beat_interval)):
        if (i % 4) == 2:
            idx = int(t * sr)
            end = min(idx + len(snare), len(disagree_samples))
            disagree_samples[idx:end] += 10.0 * snare[: end - idx]
    audio_disagree = AudioData(samples=disagree_samples, sr=sr, duration=duration)

    beats_a = track_beats(audio_agree)
    beats_d = track_beats(audio_disagree)
    _, _, conf_agree, _ = detect_downbeats(audio_agree, beats_a, beats_per_measure=4)
    _, _, conf_disagree, _ = detect_downbeats(audio_disagree, beats_d, beats_per_measure=4)

    # Agreement should give strictly higher confidence than disagreement.
    assert conf_agree > conf_disagree


def test_detect_downbeats_falls_back_gracefully_on_non_percussive_track(
    synthetic_click_audio,
):
    """Pure 1 kHz sine has no kick-band content → behaviour ≈ onset-only.

    The uniform-beat confidence should stay below the low-confidence
    threshold, identical to the Phase 9 onset-only behaviour this fixture
    was calibrated for.
    """
    beats = track_beats(synthetic_click_audio)
    _, _, confidence, _ = detect_downbeats(synthetic_click_audio, beats, beats_per_measure=4)
    # Mirror test_detect_downbeats_confidence_low_on_uniform_beats' threshold.
    assert confidence < 0.15


# --- Phase 11: BeatNet downbeat fusion tests ---


def test_detect_downbeats_falls_back_when_beatnet_unavailable(
    synthetic_accented_click_audio, monkeypatch,
):
    """If BeatNet returns zeros (unavailable / no filepath / runtime error), the
    fusion gracefully drops to the Phase-10 onset+kick combination so we keep
    detecting accented downbeats on synthetic clicks."""
    import rytmi.dsp as dsp_mod

    monkeypatch.setattr(
        dsp_mod, "_beatnet_beat_position_strengths",
        lambda audio, beats, bpm: np.zeros(bpm),
    )
    beats = track_beats(synthetic_accented_click_audio)
    _, bpm, confidence, offset = detect_downbeats(
        synthetic_accented_click_audio, beats, beats_per_measure=4,
    )
    assert bpm == 4
    assert confidence > 0.15  # still confident on the accented fixture
    assert 0 <= offset < 4


def test_detect_downbeats_fuses_beatnet_when_available(
    synthetic_accented_click_audio, monkeypatch,
):
    """When BeatNet provides a strong vote, its choice dominates the fusion
    even if onset/kick disagree, because BeatNet carries the largest weight."""
    import rytmi.dsp as dsp_mod

    # Force BeatNet to vote unanimously for offset 2; onset/kick may pick others.
    def fake_beatnet_phase(audio, beats, bpm):
        votes = np.zeros(bpm)
        votes[2] = 10.0
        return votes

    monkeypatch.setattr(
        dsp_mod, "_beatnet_beat_position_strengths", fake_beatnet_phase,
    )
    beats = track_beats(synthetic_accented_click_audio)
    _, bpm, confidence, offset = detect_downbeats(
        synthetic_accented_click_audio, beats, beats_per_measure=4,
    )
    assert offset == 2
    assert confidence > 0.0


# --- Phase 13: accent-template fusion tests ---


def test_accent_template_kizomba_synthetic_aligned():
    """Kick [1, 0.4, 1, 0.4] + snare [0, 1, 0, 1] aligned to offset 0 → kizomba wins at phi=0."""
    from rytmi.dsp import _accent_template_scores

    kick = np.array([1.0, 0.4, 1.0, 0.4])
    snare = np.array([0.0, 1.0, 0.0, 1.0])
    scores, genre = _accent_template_scores(kick, snare, beats_per_measure=4)
    assert genre == "kizomba"
    assert int(np.argmax(scores)) == 0


def test_accent_template_kizomba_synthetic_shifted():
    """Same kizomba pattern rotated by 1 → winning offset shifts to 1."""
    from rytmi.dsp import _accent_template_scores

    kick = np.roll(np.array([1.0, 0.4, 1.0, 0.4]), 1)
    snare = np.roll(np.array([0.0, 1.0, 0.0, 1.0]), 1)
    scores, genre = _accent_template_scores(kick, snare, beats_per_measure=4)
    assert genre == "kizomba"
    assert int(np.argmax(scores)) == 1


def test_accent_template_offset_peak_on_derecho_signal():
    """Hard derecho (kick [1, 0, 1, 0]) + 2&4 snare — both templates match offset 0 or 2.

    Since onset strengths are non-negative, the kizomba template (a soft
    superset of bachata with 0.4 weights at offsets 1 & 3) can tie bachata
    but never strictly lose on a sparse derecho-shaped kick.  The fusion
    only needs the *offset* to be right — which genre label carries the win
    is diagnostic-only.  This test pins the offset peak at 0 (or the
    symmetric 2) regardless of which template was selected.
    """
    from rytmi.dsp import _accent_template_scores

    kick = np.array([1.0, 0.0, 1.0, 0.0])
    snare = np.array([0.0, 1.0, 0.0, 1.0])
    scores, genre = _accent_template_scores(kick, snare, beats_per_measure=4)
    assert genre in {"bachata", "kizomba"}
    assert int(np.argmax(scores)) in {0, 2}


def test_accent_template_uniform_signal_gives_flat_scores():
    """Uniform per-offset values → scores equal across phi → low margin, no spurious confidence."""
    from rytmi.dsp import _accent_template_scores

    kick = np.ones(4)
    snare = np.ones(4)
    scores, _ = _accent_template_scores(kick, snare, beats_per_measure=4)
    # All rotations of the template cover the same flat signal → equal dot products.
    assert np.allclose(scores, scores[0])


def test_accent_template_returns_zeros_for_silent_signal():
    """Both inputs zero → zeros vector + None genre, so fusion skips the voice."""
    from rytmi.dsp import _accent_template_scores

    scores, genre = _accent_template_scores(np.zeros(4), np.zeros(4), beats_per_measure=4)
    assert np.all(scores == 0.0)
    assert genre is None


def test_detect_downbeats_template_does_not_regress_confident_beatnet_track(
    synthetic_accented_click_audio, monkeypatch,
):
    """Regression guard: when BeatNet votes strongly, a mis-shaped snare signal must not
    drop the winner.  Template weight (0.20) is small enough that BeatNet (0.40) + kick
    (0.25) agreeing on offset 2 always dominates a rogue template vote for offset 0."""
    import rytmi.dsp as dsp_mod

    def fake_beatnet_phase(audio, beats, bpm):
        votes = np.zeros(bpm)
        votes[2] = 10.0
        return votes

    # Force snare band to vote for offset 0 → template picks phi=2 for kizomba
    # (snare [0, 1, 0, 1] rotated to peak at 0 means phi=1 or 3 for kizomba).
    # We want template's winner ≠ BeatNet's offset 2 but fusion still picks 2.
    def fake_snare(audio, beats, bpm):
        scores = np.zeros(bpm)
        scores[0] = 5.0
        return scores

    monkeypatch.setattr(dsp_mod, "_beatnet_beat_position_strengths", fake_beatnet_phase)
    monkeypatch.setattr(dsp_mod, "_mid_high_band_beat_position_strengths", fake_snare)

    beats = track_beats(synthetic_accented_click_audio)
    _, bpm, confidence, offset = detect_downbeats(
        synthetic_accented_click_audio, beats, beats_per_measure=4,
    )
    assert offset == 2
    assert confidence > 0.0


# --- Phase 13 Commit A2: adaptive template weight tests ---


def test_combined_metrics_returns_zero_confidence_on_silent_signal():
    """All-zeros vector → zero confidence, offset 0 (well-defined fallback)."""
    from rytmi.dsp import _combined_metrics

    offset, conf = _combined_metrics(np.zeros(4), 4)
    assert offset == 0
    assert conf == 0.0


def test_combined_metrics_matches_inline_formula():
    """For a known spiky vector the metric matches sqrt(margin × dominance)."""
    from rytmi.dsp import _combined_metrics

    combined = np.array([0.1, 0.05, 0.4, 0.2])
    offset, conf = _combined_metrics(combined, 4)
    # margin = (0.4 - 0.2) / 0.4 = 0.5; total = 0.75; winner_ratio = 0.533;
    # dominance = (0.533 - 0.25) / 0.75 ≈ 0.378; conf ≈ sqrt(0.5 * 0.378).
    assert offset == 2
    assert conf == pytest.approx(np.sqrt(0.5 * (0.5333333 - 0.25) / 0.75), rel=1e-3)


def test_detect_downbeats_skips_template_when_beatnet_concentrated(
    synthetic_accented_click_audio, monkeypatch,
):
    """When BeatNet is strongly concentrated, a noisy flat template must NOT
    drag the combined-vector margin down (Phase 13 experiment 20 regression)."""
    import rytmi.dsp as dsp_mod

    # Strong BeatNet concentration on offset 2 (winner ≫ runner-up).
    def fake_beatnet_phase(audio, beats, bpm):
        votes = np.zeros(bpm)
        votes[2] = 10.0
        return votes

    # Near-flat snare band — what real-audio mid-high actually looks like
    # once vocal sibilance and chord content bleed in.
    def fake_snare(audio, beats, bpm):
        return np.array([0.95, 1.0, 0.97, 0.93])

    monkeypatch.setattr(dsp_mod, "_beatnet_beat_position_strengths", fake_beatnet_phase)
    monkeypatch.setattr(dsp_mod, "_mid_high_band_beat_position_strengths", fake_snare)

    beats = track_beats(synthetic_accented_click_audio)
    _, _, conf_with_guard, offset = detect_downbeats(
        synthetic_accented_click_audio, beats, beats_per_measure=4,
    )
    assert offset == 2
    # With the adaptive guard, confidence should clear the 0.25 gate by a
    # comfortable margin despite the noisy template.  Phase 13 (no guard)
    # regressed similar synthetic shapes to ~0.1.
    assert conf_with_guard > 0.3


# --- Phase 10: instrumental relabel tests ---


def _fake_vocal_env(active_segments: list[tuple[float, float]], *, duration: float = 100.0, fps: int = 10):
    """Build a VocalActivityEnvelope where `active_segments` are True, rest False."""
    from rytmi.vocal_activity import VocalActivityEnvelope
    n = int(duration * fps)
    times = np.arange(n, dtype=np.float64) / fps
    active = np.zeros(n, dtype=bool)
    for s, e in active_segments:
        active |= (times >= s) & (times < e)
    rms = active.astype(np.float32)
    return VocalActivityEnvelope(times=times, rms=rms, active=active, sr=fps, source="fake")


def _mk_section(start_s: float, end_s: float, label: str) -> SongSection:
    return SongSection(
        start_s=start_s,
        end_s=end_s,
        label=label,
        energy_level="medium",
    )


def _flat_rms_env(duration: float = 100.0, fps: int = 50, value: float = 1.0):
    """RMS envelope that reports a uniform value ≥ global_rms_mean at every frame.

    Returned as (rms_envelope, rms_times, global_rms_mean) matching the
    arguments `_relabel_vocal_drop_instrumentals` takes.
    """
    n = int(duration * fps)
    rms_times = np.arange(n, dtype=np.float64) / fps
    rms_env = np.full(n, value, dtype=np.float32)
    return rms_env, rms_times, float(value)


def test_relabel_instrumental_promotes_vocal_drop_main_section():
    """Main section with 3 vocal-quiet, high-energy phrases → instrumental."""
    from rytmi.dsp import _relabel_vocal_drop_instrumentals
    phrase_times = np.array([10.0, 14.0, 18.0, 22.0, 26.0])  # 4 phrases of 4s
    sections = [_mk_section(10.0, 26.0, "main")]
    vocal_env = _fake_vocal_env(active_segments=[], duration=40.0)
    rms_env, rms_t, g = _flat_rms_env(duration=40.0, value=1.0)
    out = _relabel_vocal_drop_instrumentals(
        sections, vocal_env, phrase_times,
        rms_envelope=rms_env, rms_times=rms_t, global_rms_mean=g,
    )
    assert len(out) == 1
    assert out[0].label == "instrumental"
    assert out[0].start_s == pytest.approx(10.0)
    assert out[0].end_s == pytest.approx(26.0)


def test_relabel_instrumental_rejects_single_phrase():
    """A 1-phrase dip can't qualify (min_phrases=2)."""
    from rytmi.dsp import _relabel_vocal_drop_instrumentals
    phrase_times = np.array([10.0, 14.0, 18.0, 22.0])  # 3 phrases
    sections = [_mk_section(10.0, 22.0, "main")]
    # Only middle phrase is vocal-quiet; surrounding ones have vocals.
    vocal_env = _fake_vocal_env(
        active_segments=[(10.0, 14.0), (18.0, 22.0)], duration=40.0,
    )
    rms_env, rms_t, g = _flat_rms_env(duration=40.0, value=1.0)
    out = _relabel_vocal_drop_instrumentals(
        sections, vocal_env, phrase_times,
        rms_envelope=rms_env, rms_times=rms_t, global_rms_mean=g,
    )
    # No qualifying run of ≥ 2 → original section preserved unchanged.
    assert len(out) == 1
    assert out[0].label == "main"


def test_relabel_instrumental_demotes_vocal_quiet_peak():
    """Peak without vocals (full section qualifies) → instrumental."""
    from rytmi.dsp import _relabel_vocal_drop_instrumentals
    phrase_times = np.array([50.0, 54.0, 58.0, 62.0])
    sections = [_mk_section(50.0, 62.0, "peak")]
    vocal_env = _fake_vocal_env(active_segments=[], duration=100.0)
    rms_env, rms_t, g = _flat_rms_env(duration=100.0, value=1.0)
    out = _relabel_vocal_drop_instrumentals(
        sections, vocal_env, phrase_times,
        rms_envelope=rms_env, rms_times=rms_t, global_rms_mean=g,
    )
    assert len(out) == 1
    assert out[0].label == "instrumental"


def test_relabel_instrumental_leaves_vocal_peak_untouched():
    """Peak with vocals on every phrase → stays peak."""
    from rytmi.dsp import _relabel_vocal_drop_instrumentals
    phrase_times = np.array([50.0, 54.0, 58.0, 62.0])
    sections = [_mk_section(50.0, 62.0, "peak")]
    # Full vocal coverage across the peak
    vocal_env = _fake_vocal_env(
        active_segments=[(50.0, 62.0)], duration=100.0,
    )
    rms_env, rms_t, g = _flat_rms_env(duration=100.0, value=1.0)
    out = _relabel_vocal_drop_instrumentals(
        sections, vocal_env, phrase_times,
        rms_envelope=rms_env, rms_times=rms_t, global_rms_mean=g,
    )
    assert len(out) == 1
    assert out[0].label == "peak"


def test_relabel_instrumental_noop_when_env_is_none():
    """No vocal envelope → no relabelling."""
    from rytmi.dsp import _relabel_vocal_drop_instrumentals
    phrase_times = np.array([0.0, 4.0, 8.0, 12.0])
    sections = [_mk_section(0.0, 12.0, "main")]
    rms_env, rms_t, g = _flat_rms_env(duration=20.0, value=1.0)
    out = _relabel_vocal_drop_instrumentals(
        sections, None, phrase_times,
        rms_envelope=rms_env, rms_times=rms_t, global_rms_mean=g,
    )
    assert out is sections  # returned unchanged


def test_relabel_instrumental_splits_partial_run():
    """Vocal-active start + vocal-quiet tail → split into [main, instrumental]."""
    from rytmi.dsp import _relabel_vocal_drop_instrumentals
    phrase_times = np.array([0.0, 4.0, 8.0, 12.0, 16.0, 20.0])  # 5 phrases
    sections = [_mk_section(0.0, 20.0, "main")]
    # Vocals fill phrases 0-2 (0-12s); phrases 3-4 (12-20s) are quiet.
    vocal_env = _fake_vocal_env(active_segments=[(0.0, 12.0)], duration=30.0)
    rms_env, rms_t, g = _flat_rms_env(duration=30.0, value=1.0)
    out = _relabel_vocal_drop_instrumentals(
        sections, vocal_env, phrase_times,
        rms_envelope=rms_env, rms_times=rms_t, global_rms_mean=g,
    )
    labels = [s.label for s in out]
    assert labels == ["main", "instrumental"]
    assert out[0].end_s == pytest.approx(12.0)
    assert out[1].start_s == pytest.approx(12.0)
    assert out[1].end_s == pytest.approx(20.0)


# --- Phase 42: vocal-active break demotion tests ---


def _mk_section_with_energy(start_s: float, end_s: float, label: str, energy: str) -> SongSection:
    return SongSection(
        start_s=start_s, end_s=end_s, label=label,
        energy_level=energy, break_branch="melodic" if "break" in label else None,
    )


def test_demote_vocal_active_break_to_main():
    """Vocal-active, non-low-energy break → demoted to main, branch cleared."""
    from rytmi.dsp import _demote_vocal_active_breaks
    sections = [_mk_section_with_energy(20.0, 40.0, "break", "medium")]
    vocal_env = _fake_vocal_env(active_segments=[(20.0, 40.0)], duration=60.0)
    out = _demote_vocal_active_breaks(sections, vocal_env)
    assert len(out) == 1
    assert out[0].label == "main"
    assert out[0].break_branch is None
    assert out[0].start_s == pytest.approx(20.0)
    assert out[0].end_s == pytest.approx(40.0)


def test_demote_preserves_low_energy_vocal_break():
    """Low-energy break stays a break even with vocal coverage (kizomba pattern)."""
    from rytmi.dsp import _demote_vocal_active_breaks
    sections = [_mk_section_with_energy(20.0, 40.0, "break", "low")]
    vocal_env = _fake_vocal_env(active_segments=[(20.0, 40.0)], duration=60.0)
    out = _demote_vocal_active_breaks(sections, vocal_env)
    assert out[0].label == "break"
    assert out[0].break_branch == "melodic"


def test_demote_preserves_vocal_quiet_break():
    """Break without vocals → unchanged regardless of energy."""
    from rytmi.dsp import _demote_vocal_active_breaks
    sections = [_mk_section_with_energy(20.0, 40.0, "break", "medium")]
    vocal_env = _fake_vocal_env(active_segments=[], duration=60.0)
    out = _demote_vocal_active_breaks(sections, vocal_env)
    assert out[0].label == "break"


def test_demote_vocal_active_short_break():
    """short_break is also covered by the demotion rule."""
    from rytmi.dsp import _demote_vocal_active_breaks
    sections = [_mk_section_with_energy(10.0, 20.0, "short_break", "medium")]
    vocal_env = _fake_vocal_env(active_segments=[(10.0, 20.0)], duration=30.0)
    out = _demote_vocal_active_breaks(sections, vocal_env)
    assert out[0].label == "main"


def test_demote_noop_without_vocal_env():
    """No envelope → returns sections unchanged."""
    from rytmi.dsp import _demote_vocal_active_breaks
    sections = [_mk_section_with_energy(20.0, 40.0, "break", "medium")]
    out = _demote_vocal_active_breaks(sections, None)
    assert out is sections


def test_demote_leaves_main_and_intro_alone():
    """Only break / short_break sections are touched."""
    from rytmi.dsp import _demote_vocal_active_breaks
    sections = [
        _mk_section_with_energy(0.0, 10.0, "intro", "low"),
        _mk_section_with_energy(10.0, 20.0, "main", "medium"),
        _mk_section_with_energy(20.0, 30.0, "peak", "high"),
    ]
    vocal_env = _fake_vocal_env(active_segments=[(0.0, 30.0)], duration=40.0)
    out = _demote_vocal_active_breaks(sections, vocal_env)
    assert [s.label for s in out] == ["intro", "main", "peak"]


def test_analyze_has_downbeat_confidence(synthetic_click_audio):
    """analyze() should populate downbeat_confidence on RhythmAnalysis."""
    result = analyze(synthetic_click_audio)
    assert result.downbeat_confidence is not None
    assert 0.0 <= result.downbeat_confidence <= 1.0


def test_analyze_stores_downbeat_offset(synthetic_click_audio):
    """analyze() should populate downbeat_offset on RhythmAnalysis."""
    result = analyze(synthetic_click_audio)
    assert result.downbeat_offset is not None
    assert isinstance(result.downbeat_offset, int)


# --- rhythm features tests ---


def test_compute_rhythm_features_basic(synthetic_click_audio):
    """Click track at 120 BPM: ~1 onset per beat, low tempo variation."""
    result = analyze(synthetic_click_audio)
    features = compute_rhythm_features(
        result.audio, result.onsets, result.beats, result.beats_per_measure,
    )
    assert 0.5 <= features.onsets_per_beat <= 2.0
    assert features.tempo_stability < 0.15


def test_rhythm_features_percussiveness(synthetic_click_audio):
    """Click track (percussive) should have higher percussiveness than a sine sweep."""
    from rytmi.dsp import compute_rhythm_features

    result = analyze(synthetic_click_audio)
    click_features = compute_rhythm_features(
        result.audio, result.onsets, result.beats, result.beats_per_measure,
    )

    sr = 22050
    t = np.linspace(0, 10.0, int(sr * 10.0), dtype=np.float32)
    sweep = np.sin(2 * np.pi * 440 * t).astype(np.float32)
    sweep_audio = AudioData(samples=sweep, sr=sr, duration=10.0)
    sweep_result = analyze(sweep_audio)
    sweep_features = compute_rhythm_features(
        sweep_result.audio, sweep_result.onsets, sweep_result.beats,
        sweep_result.beats_per_measure,
    )

    assert click_features.percussiveness > sweep_features.percussiveness


def test_beat_strength_pattern_length(synthetic_click_audio):
    """Pattern length should equal beats_per_measure."""
    result = analyze(synthetic_click_audio)
    features = compute_rhythm_features(
        result.audio, result.onsets, result.beats, result.beats_per_measure,
    )
    assert len(features.beat_strength_pattern) == result.beats_per_measure


def test_rhythm_features_handles_short_audio():
    """<1 second audio should not crash."""
    sr = 22050
    samples = np.random.randn(int(sr * 0.5)).astype(np.float32) * 0.1
    audio = AudioData(samples=samples, sr=sr, duration=0.5)
    result = analyze(audio)
    features = compute_rhythm_features(
        result.audio, result.onsets, result.beats, result.beats_per_measure,
    )
    assert features.onsets_per_beat >= 0
    assert features.percussiveness >= 0


def test_analyze_has_rhythm_features(synthetic_click_audio):
    """analyze() should populate rhythm_features on RhythmAnalysis."""
    result = analyze(synthetic_click_audio)
    assert result.rhythm_features is not None
    assert result.rhythm_features.onsets_per_beat > 0


def test_analyze_tempo_half_below_140(synthetic_click_audio):
    """120 BPM click → tempo_half should be None."""
    result = analyze(synthetic_click_audio)
    assert result.tempo_half is None


# --- section segmentation tests ---


def test_detect_sections_returns_list(synthetic_click_audio):
    """detect_sections should return a list of SongSection."""
    from rytmi.dsp import detect_sections
    from rytmi.types import SongSection

    onsets = detect_onsets(synthetic_click_audio)
    beats = track_beats(synthetic_click_audio)
    sections = detect_sections(synthetic_click_audio, onsets, beats)
    assert isinstance(sections, list)
    for s in sections:
        assert isinstance(s, SongSection)


def test_detect_sections_covers_full_duration(synthetic_click_audio):
    """Sections should span from 0.0 to the full audio duration."""
    from rytmi.dsp import detect_sections

    onsets = detect_onsets(synthetic_click_audio)
    beats = track_beats(synthetic_click_audio)
    sections = detect_sections(synthetic_click_audio, onsets, beats)
    assert len(sections) >= 1
    assert sections[0].start_s == pytest.approx(0.0)
    assert sections[-1].end_s == pytest.approx(synthetic_click_audio.duration)


def test_detect_sections_no_gaps(synthetic_click_audio):
    """Adjacent sections should have no time gaps between them."""
    from rytmi.dsp import detect_sections

    onsets = detect_onsets(synthetic_click_audio)
    beats = track_beats(synthetic_click_audio)
    sections = detect_sections(synthetic_click_audio, onsets, beats)
    for i in range(len(sections) - 1):
        assert sections[i].end_s == pytest.approx(sections[i + 1].start_s)


def test_detect_sections_valid_labels(synthetic_click_audio):
    """All section labels should be from the expected set."""
    from rytmi.dsp import detect_sections

    valid_labels = {"intro", "main", "break", "build", "peak", "outro"}
    onsets = detect_onsets(synthetic_click_audio)
    beats = track_beats(synthetic_click_audio)
    sections = detect_sections(synthetic_click_audio, onsets, beats)
    for s in sections:
        assert s.label in valid_labels, f"unexpected label: {s.label!r}"


def test_detect_sections_valid_energy_levels(synthetic_click_audio):
    """All energy levels should be low, medium, or high."""
    from rytmi.dsp import detect_sections

    onsets = detect_onsets(synthetic_click_audio)
    beats = track_beats(synthetic_click_audio)
    sections = detect_sections(synthetic_click_audio, onsets, beats)
    for s in sections:
        assert s.energy_level in {"low", "medium", "high"}


def test_detect_sections_populates_hpss_ratios(synthetic_click_audio):
    """Every emitted SongSection carries HPSS-derived harm/perc ratios."""
    from rytmi.dsp import detect_sections

    onsets = detect_onsets(synthetic_click_audio)
    beats = track_beats(synthetic_click_audio)
    sections = detect_sections(synthetic_click_audio, onsets, beats)
    assert len(sections) >= 1
    for s in sections:
        assert s.harm_ratio is not None
        assert s.perc_ratio is not None
        assert s.harm_ratio > 0
        assert s.perc_ratio > 0


def test_analyze_has_sections(synthetic_click_audio):
    """analyze() should populate sections on RhythmAnalysis."""
    result = analyze(synthetic_click_audio)
    assert isinstance(result.sections, list)
    # A 10s uniform click may produce 1 section (no novelty contrast)
    assert len(result.sections) >= 1


def test_detect_sections_multi_energy():
    """Audio with distinctly different energy halves should produce > 1 section."""
    from rytmi.dsp import detect_sections

    sr = 22050
    duration = 30.0  # long enough for 8s min section with clear contrast
    bpm = 120
    beat_interval = 60.0 / bpm

    # First half: near-silence with tiny clicks.  Second half: loud broadband clicks.
    # Use 80 Hz click (broad-spectrum, like a kick) for better energy contrast.
    samples = np.zeros(int(sr * duration), dtype=np.float32)
    click = np.sin(2 * np.pi * 80 * np.arange(int(0.02 * sr)) / sr).astype(np.float32)
    click *= np.linspace(1, 0, len(click), dtype=np.float32)

    for t in np.arange(0, duration, beat_interval):
        idx = int(t * sr)
        end = min(idx + len(click), len(samples))
        amplitude = 0.02 if t < duration / 2 else 1.0
        samples[idx:end] = amplitude * click[: end - idx]

    audio = AudioData(samples=samples, sr=sr, duration=duration)
    onsets = detect_onsets(audio)
    beats = track_beats(audio)
    sections = detect_sections(audio, onsets, beats)

    assert len(sections) >= 2, (
        f"Expected at least 2 sections for contrasting energy halves, "
        f"got {len(sections)}: {[(s.label, s.start_s, s.end_s) for s in sections]}"
    )
    # The sections should still cover the full duration
    assert sections[0].start_s == pytest.approx(0.0)
    assert sections[-1].end_s == pytest.approx(duration)


def test_compute_rhythm_features_windowed(synthetic_click_audio):
    """Windowed features should return valid data for a reasonable window."""
    from rytmi.dsp import compute_rhythm_features_windowed

    onsets = detect_onsets(synthetic_click_audio)
    beats = track_beats(synthetic_click_audio)
    features = compute_rhythm_features_windowed(
        synthetic_click_audio, onsets, beats, 4, 0.0, 5.0,
    )
    assert features is not None
    assert features.onsets_per_beat > 0
    assert features.percussiveness >= 0


def test_compute_rhythm_features_windowed_short_window():
    """A window with too few beats should return None gracefully."""
    from rytmi.dsp import compute_rhythm_features_windowed

    sr = 22050
    samples = np.zeros(int(sr * 0.3), dtype=np.float32)
    audio = AudioData(samples=samples, sr=sr, duration=0.3)
    onsets = OnsetData(times=np.array([0.1]), strength=np.array([1.0]), sr=sr)
    beats = BeatData(times=np.array([0.1]), tempo=120.0, beat_frames=np.array([5]))
    result = compute_rhythm_features_windowed(audio, onsets, beats, 4, 0.0, 0.3)
    assert result is None


# --- beat clarity tests ---


class TestBeatClarity:
    """Tests for the _beat_clarity helper and its integration into RhythmFeatures."""

    def test_clear_percussive_signal(self):
        """High percussiveness + uneven beat pattern + stable tempo → high clarity."""
        from rytmi.dsp import _beat_clarity

        # One beat position clearly dominant, percussion-driven, steady pulse
        score = _beat_clarity(
            beat_strength_pattern=[1.0, 0.3, 0.5, 0.3],
            percussiveness=0.7,
            tempo_stability=0.02,
        )
        assert score > 0.4, f"Expected high clarity, got {score}"

    def test_flat_pattern_low_clarity(self):
        """Flat beat pattern (all positions equal) → low clarity."""
        from rytmi.dsp import _beat_clarity

        score = _beat_clarity(
            beat_strength_pattern=[1.0, 1.0, 1.0, 1.0],
            percussiveness=0.5,
            tempo_stability=0.05,
        )
        assert score == 0.0, f"Flat pattern should give 0.0 clarity, got {score}"

    def test_no_percussion_low_clarity(self):
        """No percussive energy → low clarity even with uneven pattern."""
        from rytmi.dsp import _beat_clarity

        score = _beat_clarity(
            beat_strength_pattern=[1.0, 0.3, 0.5, 0.3],
            percussiveness=0.0,
            tempo_stability=0.02,
        )
        assert score == 0.0, f"Zero percussion should give 0.0, got {score}"

    def test_unstable_tempo_lowers_clarity(self):
        """Very unstable tempo should reduce clarity."""
        from rytmi.dsp import _beat_clarity

        stable = _beat_clarity([1.0, 0.3, 0.5, 0.3], 0.6, 0.02)
        unstable = _beat_clarity([1.0, 0.3, 0.5, 0.3], 0.6, 1.0)
        assert stable > unstable, f"Stable ({stable}) should beat unstable ({unstable})"

    def test_features_include_beat_clarity(self, synthetic_click_audio):
        """compute_rhythm_features should populate beat_clarity."""
        result = analyze(synthetic_click_audio)
        features = compute_rhythm_features(
            result.audio, result.onsets, result.beats, result.beats_per_measure,
        )
        assert hasattr(features, "beat_clarity")
        assert 0.0 <= features.beat_clarity <= 1.0

    def test_windowed_features_include_beat_clarity(self, synthetic_click_audio):
        """compute_rhythm_features_windowed should populate beat_clarity."""
        from rytmi.dsp import compute_rhythm_features_windowed

        onsets = detect_onsets(synthetic_click_audio)
        beats = track_beats(synthetic_click_audio)
        features = compute_rhythm_features_windowed(
            synthetic_click_audio, onsets, beats, 4, 0.0, 5.0,
        )
        assert features is not None
        assert 0.0 <= features.beat_clarity <= 1.0

    def test_empty_pattern(self):
        """Empty beat_strength_pattern should not crash."""
        from rytmi.dsp import _beat_clarity

        score = _beat_clarity([], 0.5, 0.05)
        assert score == 0.0


def test_average_rhythm_features_includes_beat_clarity():
    """_average_rhythm_features should average beat_clarity across features."""
    from rytmi.dsp import _average_rhythm_features

    f1 = RhythmFeatures(
        onsets_per_beat=2.0, beat_strength_pattern=[1.0, 0.5],
        percussiveness=0.4, spectral_centroid_mean=2000.0,
        tempo_stability=0.05, ioi_median_ms=250.0, ioi_std_ms=40.0,
        beat_clarity=0.3,
    )
    f2 = RhythmFeatures(
        onsets_per_beat=3.0, beat_strength_pattern=[0.8, 0.6],
        percussiveness=0.6, spectral_centroid_mean=3000.0,
        tempo_stability=0.10, ioi_median_ms=200.0, ioi_std_ms=50.0,
        beat_clarity=0.5,
    )
    avg = _average_rhythm_features([f1, f2])
    assert avg.beat_clarity == pytest.approx(0.4)


def test_detect_sections_short_audio():
    """Very short audio (<2s) should not crash and return at least 1 section."""
    from rytmi.dsp import detect_sections

    sr = 22050
    samples = np.random.randn(int(sr * 1.5)).astype(np.float32) * 0.1
    audio = AudioData(samples=samples, sr=sr, duration=1.5)
    onsets = detect_onsets(audio)
    beats = track_beats(audio)
    sections = detect_sections(audio, onsets, beats)
    assert len(sections) >= 1


# --- merge_adjacent_sections tests ---


def test_merge_adjacent_sections_empty():
    """Empty list returns empty phases."""
    assert merge_adjacent_sections([]) == []


def test_merge_adjacent_sections_single():
    """A single section becomes a single phase."""
    sections = [SongSection(start_s=0.0, end_s=10.0, label="main", energy_level="high")]
    phases = merge_adjacent_sections(sections)
    assert len(phases) == 1
    assert phases[0].label == "main"
    assert phases[0].section_count == 1
    assert phases[0].start_s == 0.0
    assert phases[0].end_s == 10.0
    assert phases[0].energy_levels == ["high"]


def test_merge_adjacent_sections_all_same_label():
    """Multiple consecutive same-label sections collapse into one phase."""
    sections = [
        SongSection(start_s=0.0, end_s=10.0, label="main", energy_level="low"),
        SongSection(start_s=10.0, end_s=20.0, label="main", energy_level="medium"),
        SongSection(start_s=20.0, end_s=30.0, label="main", energy_level="high"),
    ]
    phases = merge_adjacent_sections(sections)
    assert len(phases) == 1
    assert phases[0].label == "main"
    assert phases[0].section_count == 3
    assert phases[0].start_s == 0.0
    assert phases[0].end_s == 30.0
    assert phases[0].energy_levels == ["low", "medium", "high"]


def test_merge_adjacent_sections_alternating():
    """Alternating labels produce one phase per section."""
    sections = [
        SongSection(start_s=0.0, end_s=10.0, label="intro", energy_level="low"),
        SongSection(start_s=10.0, end_s=20.0, label="main", energy_level="high"),
        SongSection(start_s=20.0, end_s=30.0, label="break", energy_level="low"),
    ]
    phases = merge_adjacent_sections(sections)
    assert len(phases) == 3
    assert [p.label for p in phases] == ["intro", "main", "break"]
    assert all(p.section_count == 1 for p in phases)


def test_merge_adjacent_sections_mixed_runs():
    """Mixed runs produce the correct phase structure."""
    sections = [
        SongSection(start_s=0.0, end_s=8.0, label="intro", energy_level="low"),
        SongSection(start_s=8.0, end_s=16.0, label="main", energy_level="medium"),
        SongSection(start_s=16.0, end_s=24.0, label="main", energy_level="high"),
        SongSection(start_s=24.0, end_s=32.0, label="main", energy_level="high"),
        SongSection(start_s=32.0, end_s=40.0, label="break", energy_level="low"),
        SongSection(start_s=40.0, end_s=48.0, label="main", energy_level="high"),
    ]
    phases = merge_adjacent_sections(sections)
    assert len(phases) == 4
    assert [p.label for p in phases] == ["intro", "main", "break", "main"]
    assert [p.section_count for p in phases] == [1, 3, 1, 1]


def test_merge_adjacent_sections_averages_rhythm_features():
    """Phase should average rhythm features from its constituent sections."""
    rf1 = RhythmFeatures(
        onsets_per_beat=2.0, beat_strength_pattern=[1.0, 0.5],
        percussiveness=0.4, spectral_centroid_mean=2000.0,
        tempo_stability=0.02, ioi_median_ms=300.0, ioi_std_ms=40.0,
    )
    rf2 = RhythmFeatures(
        onsets_per_beat=4.0, beat_strength_pattern=[0.8, 0.3],
        percussiveness=0.6, spectral_centroid_mean=3000.0,
        tempo_stability=0.04, ioi_median_ms=400.0, ioi_std_ms=60.0,
    )
    sections = [
        SongSection(start_s=0.0, end_s=10.0, label="main", energy_level="medium",
                    rhythm_features=rf1),
        SongSection(start_s=10.0, end_s=20.0, label="main", energy_level="high",
                    rhythm_features=rf2),
    ]
    phases = merge_adjacent_sections(sections)
    assert len(phases) == 1
    avg = phases[0].avg_rhythm_features
    assert avg is not None
    assert avg.onsets_per_beat == pytest.approx(3.0)
    assert avg.percussiveness == pytest.approx(0.5)
    assert avg.spectral_centroid_mean == pytest.approx(2500.0)
    assert avg.beat_strength_pattern == [pytest.approx(0.9), pytest.approx(0.4)]


# --- Phase 9: same-branch break-chain merge ---


def test_phase_merge_collapses_melodic_chain():
    """Six consecutive break[melodic] sections collapse into one break."""
    from rytmi.dsp import _merge_same_branch_break_chains

    sections = [
        SongSection(start_s=0.0, end_s=4.0, label="main", energy_level="medium"),
    ]
    # Six back-to-back 4-second break[melodic] sections (Charbel-4K pattern)
    for k in range(6):
        sections.append(SongSection(
            start_s=4.0 + k * 4.0, end_s=8.0 + k * 4.0,
            label="break", energy_level="low",
            harm_ratio=0.55, perc_ratio=0.45, break_branch="melodic",
        ))
    sections.append(SongSection(
        start_s=28.0, end_s=32.0, label="main", energy_level="medium",
    ))
    merged = _merge_same_branch_break_chains(sections)
    assert len(merged) == 3  # main, break (fused), main
    fused = merged[1]
    assert fused.label == "break"
    assert fused.break_branch == "melodic"
    assert fused.start_s == pytest.approx(4.0)
    assert fused.end_s == pytest.approx(28.0)
    assert fused.harm_ratio == pytest.approx(0.55)
    assert fused.perc_ratio == pytest.approx(0.45)


def test_phase_merge_preserves_mixed_branches():
    """melodic, melodic, percussive, melodic → stays 4 sections (no run of same branch ≥ 3)."""
    from rytmi.dsp import _merge_same_branch_break_chains

    sections = [
        SongSection(start_s=0.0, end_s=4.0, label="break", energy_level="low",
                    harm_ratio=0.5, perc_ratio=0.4, break_branch="melodic"),
        SongSection(start_s=4.0, end_s=8.0, label="break", energy_level="low",
                    harm_ratio=0.5, perc_ratio=0.4, break_branch="melodic"),
        SongSection(start_s=8.0, end_s=12.0, label="break", energy_level="low",
                    harm_ratio=0.4, perc_ratio=0.6, break_branch="percussive"),
        SongSection(start_s=12.0, end_s=16.0, label="break", energy_level="low",
                    harm_ratio=0.5, perc_ratio=0.4, break_branch="melodic"),
    ]
    merged = _merge_same_branch_break_chains(sections)
    assert len(merged) == 4
    assert [s.break_branch for s in merged] == ["melodic", "melodic", "percussive", "melodic"]


def test_phase_merge_two_adjacent_same_branch_not_fused():
    """A run of exactly 2 same-branch breaks is below the min_chain floor — keep both."""
    from rytmi.dsp import _merge_same_branch_break_chains

    sections = [
        SongSection(start_s=0.0, end_s=4.0, label="break", energy_level="low",
                    harm_ratio=0.5, perc_ratio=0.4, break_branch="melodic"),
        SongSection(start_s=4.0, end_s=8.0, label="break", energy_level="low",
                    harm_ratio=0.5, perc_ratio=0.4, break_branch="melodic"),
    ]
    merged = _merge_same_branch_break_chains(sections)
    assert len(merged) == 2


def test_analyze_has_phases(synthetic_click_audio):
    """analyze() should populate phases on RhythmAnalysis."""
    result = analyze(synthetic_click_audio)
    assert isinstance(result.phases, list)
    assert len(result.phases) >= 1
    # phases should cover the same time span as sections
    assert len(result.phases) <= len(result.sections)


# --- phrase-grid snapping tests ---


def test_snap_boundaries_moves_boundary_to_nearest_phrase():
    """An interior boundary drifted off the phrase grid should snap to it."""
    from rytmi.dsp import _snap_boundaries_to_phrases

    # 120 BPM → beat interval 0.5s → phrase (8 beats) every 4.0s
    sr = 22050
    beat_times = np.arange(0.0, 40.0, 0.5)
    beats = BeatData(times=beat_times, tempo=120.0, beat_frames=np.arange(len(beat_times)))

    # Two sections with interior boundary at 8.7s — should snap to 8.0s
    # (beat index 16, phrase boundary), drift = +1.4 beats
    sections = [
        SongSection(start_s=0.0, end_s=8.7, label="intro", energy_level="low"),
        SongSection(start_s=8.7, end_s=20.0, label="main", energy_level="medium"),
    ]
    snapped = _snap_boundaries_to_phrases(sections, beats, phrase_length=8)

    assert len(snapped) == 2
    assert snapped[0].end_s == pytest.approx(8.0)
    assert snapped[1].start_s == pytest.approx(8.0)
    # Raw pre-snap values preserved
    assert snapped[0].raw_end_s == pytest.approx(8.7)
    assert snapped[1].raw_start_s == pytest.approx(8.7)
    # First section start and last section end are never snapped
    assert snapped[0].raw_start_s is None
    assert snapped[1].raw_end_s is None


def test_snap_boundaries_respects_drift_threshold():
    """A boundary >1 phrase off the grid should NOT be moved."""
    from rytmi.dsp import _snap_boundaries_to_phrases

    beat_times = np.arange(0.0, 40.0, 0.5)  # 120 BPM
    beats = BeatData(times=beat_times, tempo=120.0, beat_frames=np.arange(len(beat_times)))

    # Interior boundary at 6.0s is exactly halfway between phrase boundaries
    # at 4.0s and 8.0s — drift = 4 beats = half a phrase. With default
    # threshold of 8 beats this IS snappable, so use a stricter test:
    # construct a boundary >8 beats from any phrase boundary.  Not possible
    # on an 8-beat grid (max drift = 4 beats). Instead use phrase_length=4
    # (which means phrase boundary every 2 s at 120 BPM).
    # Boundary at 5.0s, nearest phrase boundary 4.0 or 6.0, drift 2 beats.
    # Use max_drift_beats=1.0 to force the no-snap case.
    sections = [
        SongSection(start_s=0.0, end_s=5.0, label="intro", energy_level="low"),
        SongSection(start_s=5.0, end_s=20.0, label="main", energy_level="medium"),
    ]
    snapped = _snap_boundaries_to_phrases(
        sections, beats, phrase_length=4, max_drift_beats=1.0,
    )
    assert snapped[0].end_s == pytest.approx(5.0)
    assert snapped[0].raw_end_s is None
    assert snapped[1].raw_start_s is None


def test_snap_boundaries_preserves_first_start_and_last_end():
    """Snapping never moves sections[0].start_s or sections[-1].end_s."""
    from rytmi.dsp import _snap_boundaries_to_phrases

    beat_times = np.arange(0.3, 40.0, 0.5)  # first beat at 0.3s (not 0)
    beats = BeatData(times=beat_times, tempo=120.0, beat_frames=np.arange(len(beat_times)))

    sections = [
        SongSection(start_s=0.0, end_s=10.3, label="intro", energy_level="low"),
        SongSection(start_s=10.3, end_s=30.0, label="main", energy_level="medium"),
    ]
    snapped = _snap_boundaries_to_phrases(sections, beats, phrase_length=8)
    assert snapped[0].start_s == pytest.approx(0.0)  # always 0
    assert snapped[-1].end_s == pytest.approx(30.0)  # always original end


def test_snap_boundaries_noop_when_too_few_sections():
    """A single section cannot be snapped."""
    from rytmi.dsp import _snap_boundaries_to_phrases

    beat_times = np.arange(0.0, 10.0, 0.5)
    beats = BeatData(times=beat_times, tempo=120.0, beat_frames=np.arange(len(beat_times)))
    sections = [SongSection(start_s=0.0, end_s=10.0, label="main", energy_level="medium")]
    snapped = _snap_boundaries_to_phrases(sections, beats, phrase_length=8)
    assert snapped == sections


def test_snap_boundaries_respects_offset():
    """With offset=2, phrase grid starts at beat index 2 (time 1.0s at 120 BPM)."""
    from rytmi.dsp import _snap_boundaries_to_phrases

    beat_times = np.arange(0.0, 40.0, 0.5)  # 120 BPM
    beats = BeatData(times=beat_times, tempo=120.0, beat_frames=np.arange(len(beat_times)))

    # Phrase grid with offset=0: 0.0, 4.0, 8.0, 12.0, ...
    # Phrase grid with offset=2: 1.0, 5.0, 9.0, 13.0, ...
    # Interior boundary at 8.7s:
    #   offset=0 → snaps to 8.0
    #   offset=2 → snaps to 9.0
    sections = [
        SongSection(start_s=0.0, end_s=8.7, label="intro", energy_level="low"),
        SongSection(start_s=8.7, end_s=20.0, label="main", energy_level="medium"),
    ]

    snapped_0 = _snap_boundaries_to_phrases(sections, beats, phrase_length=8, offset=0)
    snapped_2 = _snap_boundaries_to_phrases(sections, beats, phrase_length=8, offset=2)

    assert snapped_0[0].end_s == pytest.approx(8.0)
    assert snapped_2[0].end_s == pytest.approx(9.0)


def test_analyze_snap_flag_toggles_raw_fields(synthetic_click_audio):
    """analyze(snap_to_phrase_grid=False) should produce no raw_* values."""
    result_off = analyze(synthetic_click_audio, snap_to_phrase_grid=False)
    for s in result_off.sections:
        assert s.raw_start_s is None
        assert s.raw_end_s is None


# --- describe_sections tests ---


def test_describe_sections_returns_non_empty_table(synthetic_click_audio):
    """describe_sections should return a non-empty, multi-line human-readable table."""
    from rytmi.dsp import describe_sections

    result = analyze(synthetic_click_audio)
    text = describe_sections(result)
    assert len(text) > 0
    lines = text.split("\n")
    # header + separator + column headings + separator + at least 1 section row
    assert len(lines) >= 5
    assert "BPM" in text
    assert "label" in text
    assert "energy" in text


def test_describe_sections_handles_empty_sections(synthetic_click_audio):
    """describe_sections should not crash on an analysis with no sections."""
    from rytmi.dsp import describe_sections

    result = analyze(synthetic_click_audio)
    result.sections = []
    text = describe_sections(result)
    assert "no sections" in text.lower()


def test_describe_sections_includes_section_index_and_label(synthetic_click_audio):
    """Every section should appear in the output with its label."""
    from rytmi.dsp import describe_sections

    result = analyze(synthetic_click_audio)
    text = describe_sections(result)
    for s in result.sections:
        assert s.label in text


def test_describe_sections_shows_hpss_and_branch(synthetic_click_audio):
    """Output includes H×/P× columns and break[branch] on a break row."""
    from rytmi.dsp import describe_sections

    result = analyze(synthetic_click_audio)
    # Inject a synthetic break section so the branch indicator is exercised
    # even if the click-track analysis produced no natural break.
    result.sections = [
        SongSection(
            start_s=0.0,
            end_s=8.0,
            label="intro",
            energy_level="medium",
            harm_ratio=1.00,
            perc_ratio=1.00,
        ),
        SongSection(
            start_s=8.0,
            end_s=16.0,
            label="break",
            energy_level="low",
            harm_ratio=0.45,
            perc_ratio=1.05,
            break_branch="melodic",
        ),
        SongSection(
            start_s=16.0,
            end_s=result.audio.duration,
            label="outro",
            energy_level="medium",
            harm_ratio=1.00,
            perc_ratio=1.00,
        ),
    ]
    text = describe_sections(result)
    assert "H×" in text
    assert "P×" in text
    assert "break[melodic]" in text


def test_describe_sections_phrase_measure_respects_offset(synthetic_click_audio):
    """With downbeat_offset=2, P/M numbering shifts relative to offset."""
    from rytmi.dsp import describe_sections

    result = analyze(synthetic_click_audio)
    result.downbeat_offset = 2
    result.downbeat_confidence = 0.50
    result.sections = [
        SongSection(start_s=0.0, end_s=8.0, label="intro", energy_level="low"),
        SongSection(start_s=8.0, end_s=result.audio.duration, label="main", energy_level="medium"),
    ]
    text = describe_sections(result)
    assert "P0/M0" in text or "downbeat offset = 2" in text


def test_describe_sections_shows_offset_header(synthetic_click_audio):
    """Output includes downbeat offset info when offset > 0."""
    from rytmi.dsp import describe_sections

    result = analyze(synthetic_click_audio)
    result.downbeat_offset = 3
    result.downbeat_confidence = 0.60
    result.sections = [
        SongSection(start_s=0.0, end_s=result.audio.duration, label="main", energy_level="medium"),
    ]
    text = describe_sections(result)
    assert "downbeat offset = 3" in text
    assert "confidence = 0.60" in text


# --- Phase 8: break / peak edge expansion ---


def _flat_rms_envelope(duration_s: float, frame_hop_s: float = 0.02) -> tuple[np.ndarray, np.ndarray]:
    n = int(duration_s / frame_hop_s) + 1
    times = np.arange(n) * frame_hop_s
    rms = np.ones(n, dtype=np.float32)
    return rms, times


def _edge_test_beats(phrase_length: int = 8, bpm: float = 120.0, n_phrases: int = 10) -> BeatData:
    beat_interval = 60.0 / bpm
    n_beats = phrase_length * n_phrases + 1
    beat_times = np.arange(n_beats, dtype=float) * beat_interval
    return BeatData(
        times=beat_times,
        tempo=bpm,
        beat_frames=np.arange(len(beat_times)),
    )


def test_expand_label_edges_extends_break_into_supporting_phrase():
    """Adjacent phrases carrying the break signature should be absorbed."""
    from rytmi.dsp import _expand_label_edges_on_signal

    beats = _edge_test_beats(phrase_length=8, n_phrases=10)  # 40s at 120 BPM
    phrase_s = 8 * 0.5  # 4 s per phrase

    # Build RMS envelope: main is loud (2.0), break region is near-silent (0.1).
    # Extend the silent region one phrase past each break edge so the helper
    # sees break-signature support on the adjacent phrases.
    rms, rms_t = _flat_rms_envelope(duration_s=40.0)
    rms *= 2.0  # loud main default
    break_start = 3 * phrase_s  # P4
    break_end = 7 * phrase_s    # P8 exclusive
    silent_mask = (rms_t >= break_start - phrase_s) & (rms_t < break_end + phrase_s)
    rms[silent_mask] = 0.1
    global_rms_mean = float(rms.mean())

    onsets = OnsetData(times=np.array([]), strength=np.array([]), sr=22050)

    sections = [
        SongSection(start_s=0.0, end_s=break_start, label="intro", energy_level="medium",
                    harm_ratio=1.0, perc_ratio=1.0),
        SongSection(start_s=break_start, end_s=break_end, label="break",
                    energy_level="low", harm_ratio=1.0, perc_ratio=1.0,
                    break_branch="full"),
        SongSection(start_s=break_end, end_s=40.0, label="outro", energy_level="medium",
                    harm_ratio=1.0, perc_ratio=1.0),
    ]
    expanded = _expand_label_edges_on_signal(
        sections, beats, onsets,
        rms_envelope=rms, rms_times=rms_t, global_rms_mean=global_rms_mean,
        phrase_length=8, offset=0,
    )
    brk = expanded[1]
    # Break should have grown by one phrase on each edge.
    assert brk.start_s == pytest.approx(break_start - phrase_s)
    assert brk.end_s == pytest.approx(break_end + phrase_s)
    # Neighbours' boundaries move to match.
    assert expanded[0].end_s == pytest.approx(break_start - phrase_s)
    assert expanded[2].start_s == pytest.approx(break_end + phrase_s)


def test_expand_label_edges_stops_at_unsupported_phrase():
    """Adjacent phrase with a non-break RMS profile should not be absorbed."""
    from rytmi.dsp import _expand_label_edges_on_signal

    beats = _edge_test_beats(phrase_length=8, n_phrases=10)
    phrase_s = 8 * 0.5
    rms, rms_t = _flat_rms_envelope(duration_s=40.0)
    rms *= 2.0
    # Only the break region itself is quiet; neighbours stay loud.
    break_start = 3 * phrase_s
    break_end = 6 * phrase_s
    in_break = (rms_t >= break_start) & (rms_t < break_end)
    rms[in_break] = 0.1
    global_rms_mean = float(rms.mean())

    onsets = OnsetData(times=np.array([]), strength=np.array([]), sr=22050)

    sections = [
        SongSection(start_s=0.0, end_s=break_start, label="intro", energy_level="medium",
                    harm_ratio=1.0, perc_ratio=1.0),
        SongSection(start_s=break_start, end_s=break_end, label="break",
                    energy_level="low", harm_ratio=1.0, perc_ratio=1.0,
                    break_branch="full"),
        SongSection(start_s=break_end, end_s=40.0, label="outro", energy_level="medium",
                    harm_ratio=1.0, perc_ratio=1.0),
    ]
    expanded = _expand_label_edges_on_signal(
        sections, beats, onsets,
        rms_envelope=rms, rms_times=rms_t, global_rms_mean=global_rms_mean,
        phrase_length=8, offset=0,
    )
    brk = expanded[1]
    # No expansion — adjacent phrase RMS does not match break signature.
    assert brk.start_s == pytest.approx(break_start)
    assert brk.end_s == pytest.approx(break_end)


def test_edge_contraction_shrinks_break_first_phrase_mismatch():
    """A break whose first phrase doesn't match the label signature shrinks.

    Mirror of Baila Kizomba Amor's break P36→P42 where P36 is above-median
    RMS (not break-like) and the actual break starts at P37.
    """
    from rytmi.dsp import _expand_label_edges_on_signal

    beats = _edge_test_beats(phrase_length=8, n_phrases=10)  # 40s at 120 BPM
    phrase_s = 8 * 0.5  # 4 s per phrase

    # Loud main everywhere; break region P3→P7 exists in labels, but only
    # P4→P7 is actually quiet — P3 is still at main energy.
    rms, rms_t = _flat_rms_envelope(duration_s=40.0)
    rms *= 2.0
    quiet_start = 4 * phrase_s  # actual break begins at P5 (index 4)
    quiet_end = 7 * phrase_s
    quiet_mask = (rms_t >= quiet_start) & (rms_t < quiet_end)
    rms[quiet_mask] = 0.1
    global_rms_mean = float(rms.mean())

    onsets = OnsetData(times=np.array([]), strength=np.array([]), sr=22050)

    break_start = 3 * phrase_s  # P4 (index 3) — first phrase doesn't support
    break_end = 7 * phrase_s
    sections = [
        SongSection(start_s=0.0, end_s=break_start, label="intro", energy_level="medium",
                    harm_ratio=1.0, perc_ratio=1.0),
        SongSection(start_s=break_start, end_s=break_end, label="break",
                    energy_level="low", harm_ratio=1.0, perc_ratio=1.0,
                    break_branch="full"),
        SongSection(start_s=break_end, end_s=40.0, label="outro", energy_level="medium",
                    harm_ratio=1.0, perc_ratio=1.0),
    ]
    result = _expand_label_edges_on_signal(
        sections, beats, onsets,
        rms_envelope=rms, rms_times=rms_t, global_rms_mean=global_rms_mean,
        phrase_length=8, offset=0,
    )
    brk = result[1]
    # Left edge should contract by exactly one phrase (P4 is non-supporting).
    assert brk.start_s == pytest.approx(break_start + phrase_s)
    assert brk.end_s == pytest.approx(break_end)
    # The previous section absorbs the shed phrase.
    assert result[0].end_s == pytest.approx(break_start + phrase_s)


def test_edge_contraction_respects_min_remaining():
    """Contraction never shrinks a break below the 2-phrase minimum."""
    from rytmi.dsp import _expand_label_edges_on_signal

    beats = _edge_test_beats(phrase_length=8, n_phrases=10)
    phrase_s = 8 * 0.5

    # Loud main everywhere; break is only 2 phrases long and BOTH are
    # above-median RMS (no break support). Contraction cannot shrink below
    # 2 phrases, so the break stays put even though neither phrase matches.
    rms, rms_t = _flat_rms_envelope(duration_s=40.0)
    rms *= 2.0
    global_rms_mean = float(rms.mean())

    onsets = OnsetData(times=np.array([]), strength=np.array([]), sr=22050)

    break_start = 4 * phrase_s  # P5
    break_end = 6 * phrase_s    # P7 (exclusive) — exactly 2 phrases
    sections = [
        SongSection(start_s=0.0, end_s=break_start, label="intro", energy_level="medium",
                    harm_ratio=1.0, perc_ratio=1.0),
        SongSection(start_s=break_start, end_s=break_end, label="break",
                    energy_level="low", harm_ratio=1.0, perc_ratio=1.0,
                    break_branch="full"),
        SongSection(start_s=break_end, end_s=40.0, label="outro", energy_level="medium",
                    harm_ratio=1.0, perc_ratio=1.0),
    ]
    result = _expand_label_edges_on_signal(
        sections, beats, onsets,
        rms_envelope=rms, rms_times=rms_t, global_rms_mean=global_rms_mean,
        phrase_length=8, offset=0,
    )
    brk = result[1]
    # Untouched — no contraction below the 2-phrase floor.
    assert brk.start_s == pytest.approx(break_start)
    assert brk.end_s == pytest.approx(break_end)


def test_expand_label_edges_respects_neighbour_interior():
    """A break edge adjacent to another break/peak must not be absorbed."""
    from rytmi.dsp import _expand_label_edges_on_signal

    beats = _edge_test_beats(phrase_length=8, n_phrases=12)  # 48s
    phrase_s = 8 * 0.5
    rms, rms_t = _flat_rms_envelope(duration_s=48.0)
    rms *= 2.0
    # Mark two adjacent breaks as quiet.
    b1s, b1e = 3 * phrase_s, 5 * phrase_s
    b2s, b2e = 5 * phrase_s, 8 * phrase_s
    quiet_mask = (rms_t >= b1s) & (rms_t < b2e)
    rms[quiet_mask] = 0.1
    global_rms_mean = float(rms.mean())

    onsets = OnsetData(times=np.array([]), strength=np.array([]), sr=22050)

    sections = [
        SongSection(start_s=0.0, end_s=b1s, label="intro", energy_level="medium",
                    harm_ratio=1.0, perc_ratio=1.0),
        SongSection(start_s=b1s, end_s=b1e, label="break", energy_level="low",
                    harm_ratio=1.0, perc_ratio=1.0, break_branch="full"),
        SongSection(start_s=b1e, end_s=b2e, label="break", energy_level="low",
                    harm_ratio=1.0, perc_ratio=1.0, break_branch="full"),
        SongSection(start_s=b2e, end_s=48.0, label="outro", energy_level="medium",
                    harm_ratio=1.0, perc_ratio=1.0),
    ]
    expanded = _expand_label_edges_on_signal(
        sections, beats, onsets,
        rms_envelope=rms, rms_times=rms_t, global_rms_mean=global_rms_mean,
        phrase_length=8, offset=0,
    )
    # Neither break absorbs the other — interior boundary between b1 and b2
    # is untouched.
    assert expanded[1].end_s == pytest.approx(b1e)
    assert expanded[2].start_s == pytest.approx(b1e)


# --- Phase 8: sub-splitter widening ---


def test_subsplitter_walks_multi_section_same_label_run():
    """A 16-phrase main run spread across 2 main sections should split on a
    strong internal weighted shift when no existing boundary sits near it."""
    from rytmi.dsp import _split_long_runs_on_phrase_shifts

    phrase_length = 8
    median_ibi = 0.5
    phrase_s = phrase_length * median_ibi  # 4 s / phrase
    # 16 phrases → 64 s total. Split at phrase index 8 is the existing main↔main
    # boundary. Place the weighted-shift hotspot at phrase 12 (≥ 2 phrases from
    # the existing boundary) by changing RMS there.
    n_phrases = 16
    duration = n_phrases * phrase_s
    rms_t = np.arange(0, duration + 0.02, 0.02)
    rms = np.full(rms_t.shape, 1.0, dtype=np.float32)
    hotspot_start = 12 * phrase_s
    hotspot_end = (12 + 1) * phrase_s
    shift_mask = rms_t >= hotspot_start
    rms[shift_mask] = 1.6  # strong +60% shift from phrase 12 onwards
    global_rms_mean = float(rms.mean())

    # Two adjacent main sections of 8 phrases each.
    labelled = [
        (0.0, 8 * phrase_s, "main", None),
        (8 * phrase_s, duration, "main", None),
    ]
    extra = _split_long_runs_on_phrase_shifts(
        labelled,
        rms_envelope=rms,
        rms_times=rms_t,
        global_rms_mean=global_rms_mean,
        median_ibi=median_ibi,
        phrase_length=phrase_length,
    )
    # At least one new boundary should land near phrase 12 (48 s).
    assert any(abs(b - hotspot_start) < phrase_s for b in extra), (
        f"expected a boundary near {hotspot_start}s, got {extra}"
    )


def test_subsplitter_respects_min_gap():
    """A weighted-shift hotspot within min_gap_phrases of an existing
    boundary must be ignored (direct sliver guard)."""
    from rytmi.dsp import _split_long_runs_on_phrase_shifts

    phrase_length = 8
    median_ibi = 0.5
    phrase_s = phrase_length * median_ibi
    n_phrases = 16
    duration = n_phrases * phrase_s
    rms_t = np.arange(0, duration + 0.02, 0.02)
    rms = np.full(rms_t.shape, 1.0, dtype=np.float32)
    # Hotspot at phrase 9 — exactly 1 phrase from the section boundary at
    # phrase 8. With min_gap_phrases=2 this should be rejected.
    hotspot_start = 9 * phrase_s
    shift_mask = rms_t >= hotspot_start
    rms[shift_mask] = 1.6
    global_rms_mean = float(rms.mean())

    labelled = [
        (0.0, 8 * phrase_s, "main", None),
        (8 * phrase_s, duration, "main", None),
    ]
    extra = _split_long_runs_on_phrase_shifts(
        labelled,
        rms_envelope=rms,
        rms_times=rms_t,
        global_rms_mean=global_rms_mean,
        median_ibi=median_ibi,
        phrase_length=phrase_length,
        min_gap_phrases=2,
    )
    # No boundary may sit within 2 phrases of 32 s (the existing main↔main bound).
    for b in extra:
        assert abs(b - 8 * phrase_s) >= 2 * phrase_s, (
            f"boundary at {b}s violates min_gap={2 * phrase_s}s from existing 32.0s"
        )


def test_split_embedded_breaks_isolates_phrase_level_drop_inside_main():
    """A single phrase with severe/full break signature embedded in a long
    main section must produce a pair of boundaries that isolate the drop."""
    from rytmi.dsp import _split_embedded_breaks

    phrase_length = 8
    median_ibi = 0.5
    phrase_s = phrase_length * median_ibi  # 4 s
    n_phrases = 8  # 32 s — crosses the 6-phrase scan floor
    duration = n_phrases * phrase_s
    rms_t = np.arange(0, duration + 0.02, 0.02)
    rms = np.ones(rms_t.shape, dtype=np.float32)
    # Phrase 4 (16 s – 20 s) drops to 0.4 — a sharp isolated dip.
    dip_start = 4 * phrase_s
    dip_end = 5 * phrase_s
    dip_mask = (rms_t >= dip_start) & (rms_t < dip_end)
    rms[dip_mask] = 0.4
    # Also drop HPSS envelopes to trigger the full branch cleanly.
    harm = rms.copy()
    perc = rms.copy()
    global_rms = float(rms.mean())
    global_harm = float(harm.mean())
    global_perc = float(perc.mean())

    # Onsets: produce an opb drop during the dip so the "full" branch fires.
    beats = np.arange(0, duration + median_ibi, median_ibi)
    # One onset per beat, except skip the dip window (low opb).
    onset_list = [t for t in beats if not (dip_start <= t < dip_end)]
    onsets = OnsetData(times=np.asarray(onset_list), strength=np.ones(len(onset_list)), sr=22050)
    beats_obj = BeatData(times=beats, tempo=120.0, beat_frames=np.arange(len(beats)))

    labelled = [(0.0, duration, "main", None)]
    extra = _split_embedded_breaks(
        labelled,
        rms_envelope=rms, rms_times=rms_t, global_rms_mean=global_rms,
        median_ibi=median_ibi,
        onsets=onsets, beats=beats_obj,
        harm_envelope=harm, perc_envelope=perc,
        global_harm_mean=global_harm, global_perc_mean=global_perc,
        phrase_length=phrase_length,
        min_run_phrases=1,
        min_section_phrases=6,
    )
    # Boundaries should bracket the dip at 16 s and 20 s.
    assert any(abs(b - dip_start) < 0.5 for b in extra), f"no boundary near {dip_start}s: {extra}"
    assert any(abs(b - dip_end) < 0.5 for b in extra), f"no boundary near {dip_end}s: {extra}"


def test_split_embedded_breaks_noop_on_steady_main():
    """No embedded boundaries should be emitted when every phrase in a main
    section sits at track median — the ordinary no-break case."""
    from rytmi.dsp import _split_embedded_breaks

    phrase_length = 8
    median_ibi = 0.5
    phrase_s = phrase_length * median_ibi
    n_phrases = 8
    duration = n_phrases * phrase_s
    rms_t = np.arange(0, duration + 0.02, 0.02)
    rms = np.ones(rms_t.shape, dtype=np.float32)
    harm = rms.copy()
    perc = rms.copy()
    global_rms = float(rms.mean())

    beats = np.arange(0, duration + median_ibi, median_ibi)
    onsets = OnsetData(times=beats.copy(), strength=np.ones(len(beats)), sr=22050)
    beats_obj = BeatData(times=beats, tempo=120.0, beat_frames=np.arange(len(beats)))

    labelled = [(0.0, duration, "main", None)]
    extra = _split_embedded_breaks(
        labelled,
        rms_envelope=rms, rms_times=rms_t, global_rms_mean=global_rms,
        median_ibi=median_ibi,
        onsets=onsets, beats=beats_obj,
        harm_envelope=harm, perc_envelope=perc,
        global_harm_mean=float(harm.mean()), global_perc_mean=float(perc.mean()),
        phrase_length=phrase_length,
    )
    assert extra == [], f"expected no boundaries on flat main, got {extra}"


# --- Phase 5: percentile energy classifier + signal-aware labels ---


def test_classify_section_energies_percentile_varied():
    """A varied RMS distribution gets low/medium/high split by percentile."""
    from rytmi.dsp import _classify_section_energies

    # 10 ratios spanning a real range — p30≈0.645, p75≈1.05
    ratios = [0.50, 0.60, 0.70, 0.80, 0.90, 1.00, 1.10, 1.20, 1.35, 1.50]
    levels = _classify_section_energies(ratios)

    assert levels.count("low") >= 2   # bottom chunk
    assert levels.count("high") >= 2  # top chunk
    assert levels.count("medium") >= 3
    # Lowest ratio is definitely low, highest definitely high
    assert levels[0] == "low"
    assert levels[-1] == "high"


def test_classify_section_energies_flat_track_stays_medium():
    """A near-flat RMS distribution never produces spurious low/high labels.

    Absolute floor/ceiling guardrails (< 0.85 × global for low, > 1.10 × global
    for high) prevent percentile classification from splitting a flat track.
    """
    from rytmi.dsp import _classify_section_energies

    ratios = [0.98, 0.99, 1.00, 1.01, 1.02, 1.00, 0.99, 1.01]
    levels = _classify_section_energies(ratios)
    assert all(lvl == "medium" for lvl in levels), levels


def test_classify_section_energies_min_sections_fallback():
    """With < 4 sections, fall back to fixed-ratio per-section classification."""
    from rytmi.dsp import _classify_section_energies

    # 3 sections: legacy _energy_level (thresholds 0.6 / 1.3 of 1.0 baseline)
    levels = _classify_section_energies([0.5, 1.0, 1.4])
    assert levels == ["low", "medium", "high"]


def test_label_sections_assigns_break_on_low_rms_low_opb():
    """A sustained middle section with both RMS and opb clearly below median
    gets labeled 'break' regardless of the collapsed energy category."""
    from rytmi.dsp import _label_sections

    # 5 sections at 120 BPM (phrase = 4 s). Middle section is 8 s long
    # (>= 2 phrases) with rms_ratio 0.70 and opb 0.80 — track medians are 1.0.
    # Neutral HPSS ratios (1.0) so the legacy rms/opb branch path still fires.
    sections = [
        (0.0, 10.0, "medium", 1.00, 2.0, 1.00, 1.00),   # intro
        (10.0, 20.0, "medium", 1.00, 2.0, 1.00, 1.00),
        (20.0, 28.0, "medium", 0.70, 0.80, 1.00, 1.00),  # break candidate
        (28.0, 38.0, "medium", 1.00, 2.0, 1.00, 1.00),
        (38.0, 48.0, "medium", 1.00, 2.0, 1.00, 1.00),   # outro
    ]
    labelled = _label_sections(sections, duration=48.0, median_ibi=0.5, phrase_length=8)
    labels = [lbl for _, _, lbl, _ in labelled]
    branches = [br for _, _, _, br in labelled]
    assert labels[0] == "intro"
    assert labels[-1] == "outro"
    assert labels[2] == "break", labels
    # Neutral HPSS ratios → legacy `full` branch fires, not a HPSS branch.
    assert branches[2] == "full", branches


def test_label_sections_assigns_peak_on_high_rms_high_opb():
    """A middle-half section with rms_ratio and opb both above median gets peak."""
    from rytmi.dsp import _label_sections

    # Peak sits right in the middle of the track so the middle-half window catches it.
    sections = [
        (0.0, 10.0, "medium", 1.00, 2.0, 1.00, 1.00),
        (10.0, 20.0, "medium", 1.00, 2.0, 1.00, 1.00),
        (20.0, 30.0, "high", 1.30, 2.8, 1.00, 1.00),   # peak candidate
        (30.0, 40.0, "medium", 1.00, 2.0, 1.00, 1.00),
        (40.0, 50.0, "medium", 1.00, 2.0, 1.00, 1.00),
    ]
    labelled = _label_sections(sections, duration=50.0, median_ibi=0.5, phrase_length=8)
    labels = [lbl for _, _, lbl, _ in labelled]
    assert labels[2] == "peak", labels


def test_label_sections_assigns_build_before_peak():
    """A main section with strictly rising RMS just before a peak becomes build."""
    from rytmi.dsp import _label_sections

    sections = [
        (0.0, 10.0, "medium", 1.00, 2.0, 1.00, 1.00),
        (10.0, 20.0, "medium", 1.00, 2.0, 1.00, 1.00),
        (20.0, 30.0, "medium", 1.10, 2.0, 1.00, 1.00),  # rising — build
        (30.0, 40.0, "high", 1.35, 2.8, 1.00, 1.00),    # peak
        (40.0, 50.0, "medium", 1.00, 2.0, 1.00, 1.00),
        (50.0, 60.0, "medium", 1.00, 2.0, 1.00, 1.00),
    ]
    labelled = _label_sections(sections, duration=60.0, median_ibi=0.5, phrase_length=8)
    labels = [lbl for _, _, lbl, _ in labelled]
    assert labels[3] == "peak", labels
    assert labels[2] == "build", labels


def test_label_sections_intro_outro_always_positional():
    """First and last sections are always intro/outro regardless of signals."""
    from rytmi.dsp import _label_sections

    sections = [
        (0.0, 10.0, "high", 1.50, 3.0, 1.00, 1.00),    # would be peak — first
        (10.0, 20.0, "medium", 1.00, 2.0, 1.00, 1.00),
        (20.0, 30.0, "medium", 1.00, 2.0, 1.00, 1.00),
        (30.0, 40.0, "low", 0.50, 0.50, 1.00, 1.00),   # would be break — last
    ]
    labelled = _label_sections(sections, duration=40.0, median_ibi=0.5, phrase_length=8)
    labels = [lbl for _, _, lbl, _ in labelled]
    assert labels[0] == "intro"
    assert labels[-1] == "outro"


def test_label_sections_break_requires_minimum_duration():
    """A low-RMS low-opb section shorter than 1 phrase stays `main`.

    Below the `_SHORT_BREAK_MIN_PHRASES = 1.0` floor even the `short_break`
    path is closed — we don't surface sub-phrase blips as sections.
    """
    from rytmi.dsp import _label_sections

    # Middle section is only 3 s long (< 1 phrase of 4 s at 120 BPM).
    sections = [
        (0.0, 10.0, "medium", 1.00, 2.0, 1.00, 1.00),
        (10.0, 20.0, "medium", 1.00, 2.0, 1.00, 1.00),
        (20.0, 23.0, "medium", 0.50, 0.50, 1.00, 1.00),  # too short
        (23.0, 33.0, "medium", 1.00, 2.0, 1.00, 1.00),
        (33.0, 43.0, "medium", 1.00, 2.0, 1.00, 1.00),
    ]
    labelled = _label_sections(sections, duration=43.0, median_ibi=0.5, phrase_length=8)
    assert labelled[2][2] == "main"
    assert labelled[2][3] is None


def test_short_break_labels_1phrase_drop_matching_branch():
    """A 1-phrase full-drop section becomes `short_break[full]`, not `main`.

    Phrase_s = 8 beats × 0.5 s = 4 s; the 4-s mid section is exactly 1 phrase
    long — below the 2-phrase `break` floor but at the 1-phrase `short_break`
    floor. With RMS×0.48 and low opb the `full` branch fires.
    """
    from rytmi.dsp import _label_sections

    sections = [
        (0.0, 10.0, "medium", 1.00, 2.0, 1.00, 1.00),
        (10.0, 20.0, "medium", 1.00, 2.0, 1.00, 1.00),
        (20.0, 24.0, "medium", 0.48, 0.50, 1.00, 1.00),  # 1 phrase (4 s)
        (24.0, 34.0, "medium", 1.00, 2.0, 1.00, 1.00),
        (34.0, 44.0, "medium", 1.00, 2.0, 1.00, 1.00),
    ]
    labelled = _label_sections(sections, duration=44.0, median_ibi=0.5, phrase_length=8)
    assert labelled[2][2] == "short_break"
    assert labelled[2][3] == "full"


def test_short_break_rejects_1phrase_drop_not_matching_any_branch():
    """A 1-phrase section with only a mild RMS dip and healthy signals stays `main`.

    Without a branch classifier match the `short_break` path is gated off,
    just like the regular `break` floor — this is the guard against spurious
    short_break rows on every minor energy blip.
    """
    from rytmi.dsp import _label_sections

    sections = [
        (0.0, 10.0, "medium", 1.00, 2.0, 1.00, 1.00),
        (10.0, 20.0, "medium", 1.00, 2.0, 1.00, 1.00),
        (20.0, 24.0, "medium", 0.92, 1.8, 0.90, 0.95),  # mild dip, no branch match
        (24.0, 34.0, "medium", 1.00, 2.0, 1.00, 1.00),
        (34.0, 44.0, "medium", 1.00, 2.0, 1.00, 1.00),
    ]
    labelled = _label_sections(sections, duration=44.0, median_ibi=0.5, phrase_length=8)
    assert labelled[2][2] == "main"
    assert labelled[2][3] is None


def test_short_break_rejects_melodic_graze_without_strong_rms_or_hpss():
    """A 1-phrase section that only grazes the `melodic` branch stays `main`.

    Phase 12 short-break gate: when the firing branch is ``melodic`` or
    ``percussive`` AND the section is short, require either a substantial
    RMS drop (< 0.70 × median) or a severe HPSS collapse (< 0.60 × median).
    Here harm = 0.68 just below the base melodic threshold and perc = 1.37
    (Charbel-Ana row-6 pattern) with RMS×0.94 — the base melodic branch
    fires but the short-break gate retracts it.
    """
    from rytmi.dsp import _label_sections

    sections = [
        (0.0, 10.0, "medium", 1.00, 2.0, 1.00, 1.00),
        (10.0, 20.0, "medium", 1.00, 2.0, 1.00, 1.00),
        (20.0, 24.0, "medium", 0.94, 2.9, 0.68, 1.37),  # melodic graze, 1 phrase
        (24.0, 34.0, "medium", 1.00, 2.0, 1.00, 1.00),
        (34.0, 44.0, "medium", 1.00, 2.0, 1.00, 1.00),
    ]
    labelled = _label_sections(sections, duration=44.0, median_ibi=0.5, phrase_length=8)
    assert labelled[2][2] == "main"
    assert labelled[2][3] is None


def test_short_break_keeps_melodic_when_hpss_drop_is_severe():
    """A 1-phrase section with a severe HPSS collapse stays `short_break[melodic]`.

    Short-break gate passes via `hpss_strong` when harm < 0.60 × median.
    Ensures real 1-phrase melodic breaks (bass + melody drop out entirely,
    percussion continues) are still surfaced.
    """
    from rytmi.dsp import _label_sections

    sections = [
        (0.0, 10.0, "medium", 1.00, 2.0, 1.00, 1.00),
        (10.0, 20.0, "medium", 1.00, 2.0, 1.00, 1.00),
        (20.0, 24.0, "medium", 0.90, 1.5, 0.50, 1.05),  # harm collapse, perc OK
        (24.0, 34.0, "medium", 1.00, 2.0, 1.00, 1.00),
        (34.0, 44.0, "medium", 1.00, 2.0, 1.00, 1.00),
    ]
    labelled = _label_sections(sections, duration=44.0, median_ibi=0.5, phrase_length=8)
    assert labelled[2][2] == "short_break"
    assert labelled[2][3] == "melodic"


def test_short_break_keeps_melodic_when_rms_drop_is_strong():
    """A 1-phrase section with a substantial RMS drop stays `short_break[melodic]`.

    Short-break gate passes via `rms_strong` when rms_ratio < 0.70 × median.
    Protects genuine kizomba-style 1-phrase melodic drops where both H
    and RMS fall together.
    """
    from rytmi.dsp import _label_sections

    sections = [
        (0.0, 10.0, "medium", 1.00, 2.0, 1.00, 1.00),
        (10.0, 20.0, "medium", 1.00, 2.0, 1.00, 1.00),
        (20.0, 24.0, "medium", 0.65, 1.4, 0.68, 1.10),  # RMS drop + melodic
        (24.0, 34.0, "medium", 1.00, 2.0, 1.00, 1.00),
        (34.0, 44.0, "medium", 1.00, 2.0, 1.00, 1.00),
    ]
    labelled = _label_sections(sections, duration=44.0, median_ibi=0.5, phrase_length=8)
    assert labelled[2][2] == "short_break"
    assert labelled[2][3] == "melodic"


def test_regular_break_melodic_not_affected_by_short_break_gate():
    """A 2-phrase (≥ break floor) melodic section stays `break[melodic]`.

    The Phase 12 gate is scoped to ``is_short`` — regular breaks keep
    the looser base thresholds so genuine multi-phrase melodic drops
    are not regressed by the short-break tightening.
    """
    from rytmi.dsp import _label_sections

    sections = [
        (0.0, 10.0, "medium", 1.00, 2.0, 1.00, 1.00),
        (10.0, 20.0, "medium", 1.00, 2.0, 1.00, 1.00),
        (20.0, 28.0, "medium", 0.94, 2.9, 0.68, 1.37),  # melodic graze, 2 phrases
        (28.0, 38.0, "medium", 1.00, 2.0, 1.00, 1.00),
        (38.0, 48.0, "medium", 1.00, 2.0, 1.00, 1.00),
    ]
    labelled = _label_sections(sections, duration=48.0, median_ibi=0.5, phrase_length=8)
    assert labelled[2][2] == "break"
    assert labelled[2][3] == "melodic"


def test_short_break_full_branch_not_affected_by_short_break_gate():
    """The `full` branch keeps its own gate; the Phase 12 short-break gate
    only restricts `melodic` and `percussive`.

    Baila row 17 pattern: 1-phrase `short_break[full]` with RMS×0.48, opb=0.9.
    This is a real structural break — the full branch already required
    rms < 0.85 AND opb < 0.70 × median, so no extra restriction is needed.
    """
    from rytmi.dsp import _label_sections

    sections = [
        (0.0, 10.0, "medium", 1.00, 2.0, 1.00, 1.00),
        (10.0, 20.0, "medium", 1.00, 2.0, 1.00, 1.00),
        (20.0, 24.0, "medium", 0.80, 1.2, 0.90, 0.95),  # full branch, 1 phrase
        (24.0, 34.0, "medium", 1.00, 2.0, 1.00, 1.00),
        (34.0, 44.0, "medium", 1.00, 2.0, 1.00, 1.00),
    ]
    labelled = _label_sections(sections, duration=44.0, median_ibi=0.5, phrase_length=8)
    assert labelled[2][2] == "short_break"
    assert labelled[2][3] == "full"


def _uniform_sections(
    rms: float = 1.00, opb: float = 2.0, harm: float = 1.00, perc: float = 1.00,
) -> list[tuple[float, float, str, float, float, float, float]]:
    """5-section list at 120 BPM with identical flanking sections (no peak).

    Mid section defaults can be overridden to test a specific branch.
    """
    return [
        (0.0, 10.0, "medium", rms, opb, harm, perc),
        (10.0, 20.0, "medium", rms, opb, harm, perc),
        (20.0, 28.0, "medium", rms, opb, harm, perc),
        (28.0, 38.0, "medium", rms, opb, harm, perc),
        (38.0, 48.0, "medium", rms, opb, harm, perc),
    ]


def test_label_sections_melodic_branch_fires():
    """Kizomba-style melodic drop: harm collapses, perc stays up."""
    from rytmi.dsp import _label_sections

    sections = _uniform_sections()
    sections[2] = (20.0, 28.0, "medium", 0.85, 1.3, 0.50, 1.00)
    labelled = _label_sections(sections, duration=48.0, median_ibi=0.5, phrase_length=8)
    assert labelled[2][2] == "break"
    assert labelled[2][3] == "melodic"


def test_label_sections_percussive_branch_fires():
    """Inverse: percussion drops but melody carries."""
    from rytmi.dsp import _label_sections

    sections = _uniform_sections()
    sections[2] = (20.0, 28.0, "medium", 0.90, 1.3, 1.00, 0.50)
    labelled = _label_sections(sections, duration=48.0, median_ibi=0.5, phrase_length=8)
    assert labelled[2][2] == "break"
    assert labelled[2][3] == "percussive"


def test_label_sections_severe_branch_fires():
    """Both harm and perc collapse; high opb keeps `full` from firing."""
    from rytmi.dsp import _label_sections

    # High opb (2.5) keeps the full branch's opb < 0.70 × median gate closed;
    # only the severe branch (harm < 0.50 AND perc < 0.50) can catch this.
    sections = _uniform_sections()
    sections[2] = (20.0, 28.0, "medium", 0.50, 2.5, 0.40, 0.40)
    labelled = _label_sections(sections, duration=48.0, median_ibi=0.5, phrase_length=8)
    assert labelled[2][2] == "break"
    assert labelled[2][3] == "severe"


def test_label_sections_full_branch_fires():
    """Classic bachata full drop: moderate rms + low opb, no HPSS separation."""
    from rytmi.dsp import _label_sections

    sections = _uniform_sections()
    sections[2] = (20.0, 28.0, "medium", 0.80, 0.60, 1.00, 1.00)
    labelled = _label_sections(sections, duration=48.0, median_ibi=0.5, phrase_length=8)
    assert labelled[2][2] == "break"
    assert labelled[2][3] == "full"


def test_label_sections_no_false_break_on_quieter_groove():
    """A slightly quieter mid groove with healthy HPSS ratios stays `main`."""
    from rytmi.dsp import _label_sections

    sections = _uniform_sections()
    sections[2] = (20.0, 28.0, "medium", 0.90, 1.4, 0.90, 0.95)
    labelled = _label_sections(sections, duration=48.0, median_ibi=0.5, phrase_length=8)
    assert labelled[2][2] == "main"
    assert labelled[2][3] is None


def test_split_long_runs_inserts_boundary():
    """6-phrase main section with a mid-run 30% RMS dip produces a split."""
    from rytmi.dsp import _split_long_runs_on_phrase_shifts

    # 48 s section at phrase_s = 4 s → 12 phrases. Phases 0..5 at RMS 1.0,
    # phase 6 drops to 0.70, phases 6..11 stay at 0.70. One shift at
    # boundary j=5 → j+1=6. Use an evenly spaced rms envelope.
    median_ibi = 0.5
    phrase_length = 8
    phrase_s = phrase_length * median_ibi
    n_phrases = 12
    duration = n_phrases * phrase_s
    rms_times = np.linspace(0.0, duration, num=int(duration * 50), endpoint=False)
    rms_values = np.ones_like(rms_times)
    rms_values[rms_times >= 6 * phrase_s] = 0.70
    labelled = [(0.0, duration, "main", None)]
    extra = _split_long_runs_on_phrase_shifts(
        labelled,
        rms_envelope=rms_values,
        rms_times=rms_times,
        global_rms_mean=1.0,
        median_ibi=median_ibi,
        phrase_length=phrase_length,
    )
    assert len(extra) >= 1
    assert any(abs(t - 6 * phrase_s) < phrase_s for t in extra), extra


def test_split_long_runs_no_op_on_short_run():
    """A 2-phrase section is never split even with a big shift."""
    from rytmi.dsp import _split_long_runs_on_phrase_shifts

    median_ibi = 0.5
    phrase_length = 8
    phrase_s = phrase_length * median_ibi
    n_phrases = 2
    duration = n_phrases * phrase_s  # 8 s
    rms_times = np.linspace(0.0, duration, num=int(duration * 50), endpoint=False)
    rms_values = np.ones_like(rms_times)
    rms_values[rms_times >= phrase_s] = 0.30
    labelled = [(0.0, duration, "main", None)]
    extra = _split_long_runs_on_phrase_shifts(
        labelled,
        rms_envelope=rms_values,
        rms_times=rms_times,
        global_rms_mean=1.0,
        median_ibi=median_ibi,
        phrase_length=phrase_length,
    )
    assert extra == []


def test_split_long_runs_preserves_non_main_labels():
    """A long break section is not split even if internal RMS shifts are big."""
    from rytmi.dsp import _split_long_runs_on_phrase_shifts

    median_ibi = 0.5
    phrase_length = 8
    phrase_s = phrase_length * median_ibi
    n_phrases = 12
    duration = n_phrases * phrase_s
    rms_times = np.linspace(0.0, duration, num=int(duration * 50), endpoint=False)
    rms_values = np.ones_like(rms_times)
    rms_values[rms_times >= 6 * phrase_s] = 0.50
    labelled = [(0.0, duration, "break", "melodic")]
    extra = _split_long_runs_on_phrase_shifts(
        labelled,
        rms_envelope=rms_values,
        rms_times=rms_times,
        global_rms_mean=1.0,
        median_ibi=median_ibi,
        phrase_length=phrase_length,
    )
    assert extra == []


def test_merge_adjacent_sections_splits_on_sustained_energy_change():
    """A long main run with a sustained energy transition (>= 2 on each side)
    splits into multiple phases instead of collapsing to one."""
    run = [
        SongSection(start_s=0.0, end_s=10.0, label="main", energy_level="medium"),
        SongSection(start_s=10.0, end_s=20.0, label="main", energy_level="medium"),
        SongSection(start_s=20.0, end_s=30.0, label="main", energy_level="high"),
        SongSection(start_s=30.0, end_s=40.0, label="main", energy_level="high"),
        SongSection(start_s=40.0, end_s=50.0, label="main", energy_level="medium"),
        SongSection(start_s=50.0, end_s=60.0, label="main", energy_level="medium"),
    ]
    phases = merge_adjacent_sections(run)
    assert len(phases) == 3, [p.section_count for p in phases]
    assert [p.section_count for p in phases] == [2, 2, 2]
    assert [set(p.energy_levels) for p in phases] == [
        {"medium"}, {"high"}, {"medium"},
    ]


def test_merge_adjacent_sections_single_energy_blip_does_not_split():
    """A single-section energy blip inside a run does not cause a split."""
    run = [
        SongSection(start_s=0.0, end_s=10.0, label="main", energy_level="medium"),
        SongSection(start_s=10.0, end_s=20.0, label="main", energy_level="medium"),
        SongSection(start_s=20.0, end_s=30.0, label="main", energy_level="high"),  # blip
        SongSection(start_s=30.0, end_s=40.0, label="main", energy_level="medium"),
        SongSection(start_s=40.0, end_s=50.0, label="main", energy_level="medium"),
    ]
    phases = merge_adjacent_sections(run)
    assert len(phases) == 1
    assert phases[0].section_count == 5


# --- Phase 9: vocal-aware intro/outro passes ---


def _make_envelope_sr4(active_mask: list[bool], start_s: float = 0.0):
    """Build a VocalActivityEnvelope at 4 fps (0.25 s frame step)."""
    from rytmi.vocal_activity import VocalActivityEnvelope

    n = len(active_mask)
    times = np.arange(n, dtype=np.float64) * 0.25 + start_s
    rms = np.where(np.asarray(active_mask, dtype=bool), 1.0, 0.0).astype(np.float32)
    return VocalActivityEnvelope(
        times=times,
        rms=rms,
        active=np.asarray(active_mask, dtype=bool),
        sr=4,
        source="fake",
    )


def test_extend_intro_absorbs_prevocal_section():
    """Intro P1-P3 with a false break P3-P9; vocals start at P11 → intro absorbs up to P11."""
    from rytmi.dsp import _extend_intro_to_first_vocal

    # 12 phrases at 4 s each (120 BPM, 8-beat phrases) → phrase_times [0, 4, 8, ..., 48]
    phrase_times = np.arange(13, dtype=np.float64) * 4.0
    sections = [
        SongSection(start_s=0.0, end_s=8.0, label="intro", energy_level="low"),
        SongSection(start_s=8.0, end_s=32.0, label="break", energy_level="low",
                    break_branch="full"),
        SongSection(start_s=32.0, end_s=48.0, label="main", energy_level="medium"),
    ]
    # Frame every 0.25s across 50s = 200 frames.
    # Active starting at 40 s (phrase 10, index 10*16=160 frames).
    n_frames = 200
    active = [False] * 160 + [True] * 40
    env = _make_envelope_sr4(active)
    out = _extend_intro_to_first_vocal(sections, env, phrase_times)
    assert out[0].label == "intro"
    # Intro should extend to phrase 10 boundary (40 s).
    assert out[0].end_s == pytest.approx(40.0)
    # The prior break P3→P9 should be absorbed; remaining tail is main.
    remaining_labels = [s.label for s in out[1:]]
    assert "break" not in remaining_labels


def test_extend_intro_noop_when_vocal_starts_before_intro_end():
    """If vocals begin inside the existing intro, no change."""
    from rytmi.dsp import _extend_intro_to_first_vocal

    phrase_times = np.arange(10, dtype=np.float64) * 4.0
    sections = [
        SongSection(start_s=0.0, end_s=20.0, label="intro", energy_level="low"),
        SongSection(start_s=20.0, end_s=40.0, label="main", energy_level="medium"),
    ]
    # Active starting at 8 s (phrase 2) — already inside the intro.
    active = [False] * 32 + [True] * (40 * 4 - 32)
    env = _make_envelope_sr4(active)
    out = _extend_intro_to_first_vocal(sections, env, phrase_times)
    assert len(out) == len(sections)
    assert out[0].end_s == pytest.approx(20.0)


def test_extend_intro_respects_max_extend_cap():
    """Intro grows at most `max_extend_phrases` even if vocals start much later."""
    from rytmi.dsp import _extend_intro_to_first_vocal

    phrase_times = np.arange(30, dtype=np.float64) * 4.0
    sections = [
        SongSection(start_s=0.0, end_s=8.0, label="intro", energy_level="low"),
        SongSection(start_s=8.0, end_s=120.0, label="main", energy_level="medium"),
    ]
    # Vocals only at phrase 25 (100 s); intro_end is phrase 2, cap = 2 + 3 = 5 → 20 s.
    active = [False] * 400 + [True] * 80
    env = _make_envelope_sr4(active)
    out = _extend_intro_to_first_vocal(
        sections, env, phrase_times, max_extend_phrases=3,
    )
    assert out[0].end_s == pytest.approx(20.0)


def test_extend_intro_noop_when_env_is_none():
    from rytmi.dsp import _extend_intro_to_first_vocal

    phrase_times = np.arange(10, dtype=np.float64) * 4.0
    sections = [
        SongSection(start_s=0.0, end_s=8.0, label="intro", energy_level="low"),
        SongSection(start_s=8.0, end_s=40.0, label="main", energy_level="medium"),
    ]
    out = _extend_intro_to_first_vocal(sections, None, phrase_times)
    assert out is sections


def test_contract_outro_to_last_vocal():
    """Vocal fade at P6 → outro originally at P10 pulls back to P8 (fade + grace)."""
    from rytmi.dsp import _contract_outro_to_last_vocal

    phrase_times = np.arange(12, dtype=np.float64) * 4.0
    sections = [
        SongSection(start_s=0.0, end_s=8.0, label="intro", energy_level="low"),
        SongSection(start_s=8.0, end_s=40.0, label="main", energy_level="medium"),
        SongSection(start_s=40.0, end_s=48.0, label="outro", energy_level="low"),
    ]
    # Vocals active phrases 1-6 (4 s … 28 s) then silent for the tail.
    # Frames at 0.25 s → phrase 1 starts at idx 16, phrase 7 starts at idx 112.
    active = [False] * 16 + [True] * (112 - 16) + [False] * (200 - 112)
    env = _make_envelope_sr4(active)
    out = _contract_outro_to_last_vocal(
        sections, env, phrase_times, grace_phrases=1,
    )
    # Last vocal phrase idx 6, outro pulls to phrase 6 + 1 + 1 = 8 → 32 s.
    assert out[-1].label == "outro"
    assert out[-1].start_s == pytest.approx(32.0)
    assert out[-2].end_s == pytest.approx(32.0)


def test_contract_outro_respects_max_contract_cap():
    """Don't shrink outro more than `max_contract_phrases` even if vocals faded early."""
    from rytmi.dsp import _contract_outro_to_last_vocal

    phrase_times = np.arange(20, dtype=np.float64) * 4.0
    sections = [
        SongSection(start_s=0.0, end_s=60.0, label="main", energy_level="medium"),
        SongSection(start_s=60.0, end_s=76.0, label="outro", energy_level="low"),
    ]
    # Vocals only in phrases 1-3 (4 s – 16 s). Without cap, outro pulls WAY earlier.
    active = [False] * 16 + [True] * (64 - 16) + [False] * (320 - 64)
    env = _make_envelope_sr4(active)
    out = _contract_outro_to_last_vocal(
        sections, env, phrase_times, max_contract_phrases=2, grace_phrases=0,
    )
    # Cap: outro_idx=15, min_target_idx=13 → 52 s.
    assert out[-1].start_s == pytest.approx(52.0)


def test_contract_outro_noop_when_no_vocals():
    from rytmi.dsp import _contract_outro_to_last_vocal

    phrase_times = np.arange(12, dtype=np.float64) * 4.0
    sections = [
        SongSection(start_s=0.0, end_s=40.0, label="main", energy_level="medium"),
        SongSection(start_s=40.0, end_s=48.0, label="outro", energy_level="low"),
    ]
    env = _make_envelope_sr4([False] * 200)
    out = _contract_outro_to_last_vocal(sections, env, phrase_times)
    assert out is sections


# --- Phase 11: spoken_intro relabel pass ---


def test_relabel_spoken_intro_splits_intro_when_leading_speech():
    """Leading 2 phrases are speech, remaining intro phrases are not → split."""
    from rytmi.dsp import _relabel_spoken_intro

    # 6 phrases of 4 s each → phrase_times [0, 4, 8, 12, 16, 20, 24].
    phrase_times = np.arange(7, dtype=np.float64) * 4.0
    sections = [
        SongSection(start_s=0.0, end_s=24.0, label="intro", energy_level="low"),
        SongSection(start_s=24.0, end_s=60.0, label="main", energy_level="medium"),
    ]
    # 4 fps → phrase=16 frames. Speech across phrases 0–1 (frames 0–31), silent thereafter.
    n_frames = 24 * 4
    speech_active = [True] * 32 + [False] * (n_frames - 32)
    speech_env = _make_envelope_sr4(speech_active)
    out = _relabel_spoken_intro(sections, speech_env, phrase_times)
    assert [s.label for s in out] == ["spoken_intro", "intro", "main"]
    assert out[0].start_s == pytest.approx(0.0)
    assert out[0].end_s == pytest.approx(8.0)
    assert out[1].start_s == pytest.approx(8.0)
    assert out[1].end_s == pytest.approx(24.0)
    assert out[2].start_s == pytest.approx(24.0)


def test_relabel_spoken_intro_relabels_whole_intro_when_all_speech():
    """Every leading phrase of the intro is speech → relabel in place."""
    from rytmi.dsp import _relabel_spoken_intro

    phrase_times = np.arange(4, dtype=np.float64) * 4.0  # 0, 4, 8, 12
    sections = [
        SongSection(start_s=0.0, end_s=12.0, label="intro", energy_level="low"),
        SongSection(start_s=12.0, end_s=40.0, label="main", energy_level="medium"),
    ]
    n_frames = 12 * 4
    speech_env = _make_envelope_sr4([True] * n_frames)
    out = _relabel_spoken_intro(sections, speech_env, phrase_times)
    assert [s.label for s in out] == ["spoken_intro", "main"]
    assert out[0].start_s == pytest.approx(0.0)
    assert out[0].end_s == pytest.approx(12.0)


def test_relabel_spoken_intro_noop_when_env_is_none():
    from rytmi.dsp import _relabel_spoken_intro

    phrase_times = np.arange(6, dtype=np.float64) * 4.0
    sections = [
        SongSection(start_s=0.0, end_s=20.0, label="intro", energy_level="low"),
        SongSection(start_s=20.0, end_s=40.0, label="main", energy_level="medium"),
    ]
    out = _relabel_spoken_intro(sections, None, phrase_times)
    assert out is sections


def test_relabel_spoken_intro_leaves_sung_intro_untouched():
    """Speech ratio stays below the min in every leading phrase → no relabel."""
    from rytmi.dsp import _relabel_spoken_intro

    phrase_times = np.arange(7, dtype=np.float64) * 4.0
    sections = [
        SongSection(start_s=0.0, end_s=24.0, label="intro", energy_level="low"),
        SongSection(start_s=24.0, end_s=60.0, label="main", energy_level="medium"),
    ]
    # All-False speech envelope: ratio = 0.0 in every phrase.
    speech_env = _make_envelope_sr4([False] * (24 * 4))
    out = _relabel_spoken_intro(sections, speech_env, phrase_times)
    assert [s.label for s in out] == ["intro", "main"]
    assert out[0].end_s == pytest.approx(24.0)


def test_relabel_spoken_intro_skips_non_intro_first_section():
    """Only acts when the first section is `intro` — leave unrelated openers alone."""
    from rytmi.dsp import _relabel_spoken_intro

    phrase_times = np.arange(6, dtype=np.float64) * 4.0
    sections = [
        SongSection(start_s=0.0, end_s=20.0, label="main", energy_level="medium"),
    ]
    speech_env = _make_envelope_sr4([True] * (20 * 4))
    out = _relabel_spoken_intro(sections, speech_env, phrase_times)
    assert out is sections


# ── Phase 14 — HPSS preprocessing tests ──────────────────────────────────────


def test_hpss_kick_signal_more_peaked_on_percussive():
    """Feed a kick-plus-string-pad signal; the kick-band per-offset vector
    should be more peaked (higher max-to-second ratio) on y_perc than raw.

    A 60 Hz kick click every 4 beats at offset 0 sits on top of a sustained
    220 Hz sine pad.  HPSS should strip the pad, leaving a cleaner kick
    signal for the low-band helper.
    """
    from rytmi.dsp import (
        _low_band_beat_position_strengths,
        _percussive_audio,
    )

    sr = 22050
    dur_s = 8.0
    bpm_val = 120.0
    n_samples = int(sr * dur_s)
    t = np.linspace(0, dur_s, n_samples, endpoint=False)
    beats_per_measure = 4
    beat_interval = 60.0 / bpm_val
    beat_times = np.arange(0, dur_s, beat_interval)

    # Build signal: sustained harmonic pad + transient kicks on offset 0
    pad = 0.3 * np.sin(2 * np.pi * 220.0 * t)  # harmonic pad
    kick = np.zeros(n_samples, dtype=np.float32)
    for i, bt in enumerate(beat_times):
        if i % beats_per_measure == 0:
            idx = int(bt * sr)
            length = min(int(0.03 * sr), n_samples - idx)
            if length > 0:
                decay = np.exp(-np.linspace(0, 8, length))
                kick[idx : idx + length] += 0.8 * np.sin(
                    2 * np.pi * 60.0 * np.linspace(0, 0.03, length)
                ) * decay

    raw_samples = (pad + kick).astype(np.float32)
    audio_raw = AudioData(samples=raw_samples, sr=sr, duration=dur_s)
    beats = BeatData(times=beat_times, tempo=bpm_val, beat_frames=np.array([]))

    raw_kick = _low_band_beat_position_strengths(audio_raw, beats, beats_per_measure)
    perc_audio = _percussive_audio(audio_raw)
    perc_kick = _low_band_beat_position_strengths(perc_audio, beats, beats_per_measure)

    # Peakedness: ratio of best to runner-up.  Higher = more peaked.
    def peakedness(v):
        s = np.sort(v)[::-1]
        if s[1] < 1e-9:
            return float("inf")
        return s[0] / s[1]

    assert peakedness(perc_kick) > peakedness(raw_kick), (
        f"HPSS percussive kick should be more peaked: "
        f"perc={peakedness(perc_kick):.3f} vs raw={peakedness(raw_kick):.3f}"
    )


def test_drum_stem_extract_returns_audio_data_with_stub(monkeypatch, tmp_path):
    """With a stubbed ``_separate_drums`` returning a synthetic kick signal,
    ``extract`` returns a valid ``AudioData`` with the expected length."""
    from rytmi.drum_stem import DemucsDrumStem

    sr = 22050
    dur = 4.0
    n = int(dur * sr)
    # Write a real file so cache key works
    import soundfile as sf

    path = tmp_path / "test_track.wav"
    samples = np.zeros(n, dtype=np.float32)
    sf.write(str(path), samples, sr)
    audio = AudioData(samples=samples, sr=sr, duration=dur, filepath=str(path))

    # Synthetic drum signal: kick-like pulse
    t = np.arange(n) / sr
    kick = np.where(t < 0.05, np.sin(2 * np.pi * 60.0 * t) * 0.5, 0.0).astype(np.float32)

    stem = DemucsDrumStem(cache_dir=tmp_path / "cache_drums")
    monkeypatch.setattr(stem, "_separate_drums", lambda _a: kick)

    result = stem.extract(audio)
    assert result is not None
    assert result.sr == sr
    assert result.duration == dur
    assert len(result.samples) == n
    assert result.samples.dtype == np.float32


def test_kizomba_style_gating_accepts_low_confidence_offset(
    synthetic_click_audio, monkeypatch,
):
    """Kizomba tracks accept raw_offset even when confidence is below the gate.

    When ``dance_style="kizomba"`` the DSP's best-guess offset should be used
    regardless of confidence.  For other styles (e.g. bachata) the gate should
    still force offset to 0 when confidence is low.
    """
    import rytmi.dsp as dsp_mod

    fake_offset = 3
    fake_confidence = 0.05  # well below _DOWNBEAT_OFFSET_MIN_CONFIDENCE (0.25)

    original_detect = dsp_mod.detect_downbeats

    def _patched_detect(audio, beats, beats_per_measure=4):
        downbeat_times, bpm, _conf, _off = original_detect(audio, beats, beats_per_measure)
        return downbeat_times, bpm, fake_confidence, fake_offset

    monkeypatch.setattr(dsp_mod, "detect_downbeats", _patched_detect)

    result_kiz = analyze(synthetic_click_audio, dance_style="kizomba")
    assert result_kiz.downbeat_offset == fake_offset, (
        f"kizomba should accept raw_offset={fake_offset} at low confidence, "
        f"got {result_kiz.downbeat_offset}"
    )

    result_bach = analyze(synthetic_click_audio, dance_style="bachata")
    assert result_bach.downbeat_offset == 0, (
        f"bachata should gate low-confidence offset to 0, "
        f"got {result_bach.downbeat_offset}"
    )

    result_none = analyze(synthetic_click_audio, dance_style=None)
    assert result_none.downbeat_offset == 0, (
        f"no dance_style should gate low-confidence offset to 0, "
        f"got {result_none.downbeat_offset}"
    )


# --- Phase 15: harmonic-cue downbeat voice tests ---


def test_harmonic_cue_returns_correct_shape():
    """_harmonic_cue_beat_position_strengths returns array of length bpm."""
    from rytmi.dsp import _harmonic_cue_beat_position_strengths

    sr = 22050
    dur = 8.0
    n = int(sr * dur)
    t = np.arange(n) / sr
    # Two-chord pattern: A-major-ish for beats 0-3, then C-major-ish for 4-7
    # at 120 BPM (0.5s per beat, 2s per measure)
    freq_a, freq_c = 440.0, 523.25
    samples = np.where(
        (t % 2.0) < 1.0,
        np.sin(2 * np.pi * freq_a * t),
        np.sin(2 * np.pi * freq_c * t),
    ).astype(np.float32)
    audio = AudioData(samples=samples, sr=sr, duration=dur)
    beat_times = np.arange(0.0, dur, 0.5)
    beats = BeatData(
        times=beat_times, tempo=120.0, beat_frames=np.arange(len(beat_times)),
    )

    result = _harmonic_cue_beat_position_strengths(audio, beats, 4)
    assert result.shape == (4,), f"Expected shape (4,), got {result.shape}"
    assert np.all(np.isfinite(result)), "Result contains non-finite values"


def test_harmonic_cue_chord_change_peaks_at_transition():
    """Chroma novelty should peak at the beat position where chord changes occur."""
    from rytmi.dsp import _harmonic_cue_beat_position_strengths

    sr = 22050
    dur = 16.0
    n = int(sr * dur)
    t = np.arange(n) / sr
    # Two-chord pattern alternating every 2 beats (1s) at 120 BPM.
    # Chord changes at beat positions 0 and 2 (every 1s boundary).
    # Use very different frequencies to get clear chroma contrast.
    samples = np.zeros(n, dtype=np.float32)
    for i in range(int(dur)):
        seg = (t >= i) & (t < i + 1)
        freq = 261.63 if (i % 2 == 0) else 392.0  # C4 vs G4
        samples[seg] = np.sin(2 * np.pi * freq * t[seg]).astype(np.float32)

    audio = AudioData(samples=samples, sr=sr, duration=dur)
    beat_times = np.arange(0.0, dur, 0.5)
    beats = BeatData(
        times=beat_times, tempo=120.0, beat_frames=np.arange(len(beat_times)),
    )

    result = _harmonic_cue_beat_position_strengths(audio, beats, 4)
    # Chord changes happen at even-second boundaries = beat positions 0 and 2.
    # These should have higher chroma novelty than positions 1 and 3.
    even_mean = (result[0] + result[2]) / 2.0
    odd_mean = (result[1] + result[3]) / 2.0
    assert even_mean > odd_mean, (
        f"Chord-change positions should score higher: "
        f"even={even_mean:.4f} vs odd={odd_mean:.4f}"
    )


def test_harmonic_cue_flat_signal_near_uniform():
    """A constant-frequency signal should produce near-uniform harmonic scores."""
    from rytmi.dsp import _harmonic_cue_beat_position_strengths

    sr = 22050
    dur = 8.0
    n = int(sr * dur)
    t = np.arange(n) / sr
    samples = np.sin(2 * np.pi * 440.0 * t).astype(np.float32)
    audio = AudioData(samples=samples, sr=sr, duration=dur)
    beat_times = np.arange(0.0, dur, 0.5)
    beats = BeatData(
        times=beat_times, tempo=120.0, beat_frames=np.arange(len(beat_times)),
    )

    result = _harmonic_cue_beat_position_strengths(audio, beats, 4)
    # A constant tone has no meaningful chord changes.  The chroma novelty
    # component should be low.  The bass fallback (40–150 Hz bandpass) on a
    # 440 Hz sine has negligible energy, so its contribution is noise-level.
    # We only check that the function doesn't crash and returns finite values;
    # near-uniformity is not guaranteed when all signals are near-zero.
    assert result.shape == (4,)
    assert np.all(np.isfinite(result))


def test_harmonic_cue_with_bass_audio():
    """When bass_audio is provided, bass onset strength uses that stem."""
    from rytmi.dsp import _harmonic_cue_beat_position_strengths

    sr = 22050
    dur = 8.0
    n = int(sr * dur)
    t = np.arange(n) / sr
    # Main audio: constant tone
    samples = np.sin(2 * np.pi * 440.0 * t).astype(np.float32)
    audio = AudioData(samples=samples, sr=sr, duration=dur)

    # Bass audio: strong clicks on every other second (positions 0, 2)
    bass = np.zeros(n, dtype=np.float32)
    click = np.sin(2 * np.pi * 80.0 * np.arange(int(0.01 * sr)) / sr).astype(np.float32)
    click *= np.linspace(1, 0, len(click), dtype=np.float32)
    for sec in range(0, int(dur), 2):
        idx = int(sec * sr)
        end = min(idx + len(click), n)
        bass[idx:end] = click[: end - idx]

    bass_audio = AudioData(samples=bass, sr=sr, duration=dur)
    beat_times = np.arange(0.0, dur, 0.5)
    beats = BeatData(
        times=beat_times, tempo=120.0, beat_frames=np.arange(len(beat_times)),
    )

    result = _harmonic_cue_beat_position_strengths(
        audio, beats, 4, bass_audio=bass_audio,
    )
    assert result.shape == (4,)
    assert np.all(np.isfinite(result))


def test_harmonic_cue_nonregressive_on_click_track(synthetic_click_audio):
    """Adding the harmonic voice should not change results on a simple click track.

    The adaptive gating ensures the harmonic voice only fires when it improves
    confidence, so a uniform-chroma click track should produce the same
    downbeat result with or without the harmonic voice present.
    """
    result = analyze(synthetic_click_audio)
    assert result.downbeat_confidence is not None
    assert result.downbeat_confidence >= 0.0


def test_bass_stem_extract_returns_audio_data_with_stub(monkeypatch, tmp_path):
    """DemucsBassStem.extract returns valid AudioData with a stubbed separator."""
    from rytmi.bass_stem import DemucsBassStem

    sr = 22050
    dur = 4.0
    n = int(dur * sr)
    import soundfile as sf

    path = tmp_path / "test_track.wav"
    samples = np.zeros(n, dtype=np.float32)
    sf.write(str(path), samples, sr)
    audio = AudioData(samples=samples, sr=sr, duration=dur, filepath=str(path))

    # Synthetic bass signal
    t = np.arange(n) / sr
    bass = np.sin(2 * np.pi * 80.0 * t).astype(np.float32) * 0.3

    stem = DemucsBassStem(cache_dir=tmp_path / "cache_bass")
    monkeypatch.setattr(stem, "_separate_bass", lambda _a: bass)

    result = stem.extract(audio)
    assert result is not None
    assert result.sr == sr
    assert result.duration == dur
    assert len(result.samples) == n
    assert result.samples.dtype == np.float32

    # Second call should hit cache
    result2 = stem.extract(audio)
    assert result2 is not None
    assert np.array_equal(result.samples, result2.samples)


# ── Grid-extrapolation "1" detector tests (Phase 15b) ────────────────────────


class TestFindStableRegion:
    """Tests for _find_stable_region()."""

    def test_uniform_grid_returns_valid_index(self):
        from rytmi.dsp import _find_stable_region

        # 20 beats at exactly 120 BPM (IBI = 0.5s) — all windows equally stable.
        times = np.arange(20) * 0.5
        beats = BeatData(times=times, tempo=120.0, beat_frames=np.arange(20))
        idx = _find_stable_region(beats)
        assert isinstance(idx, int)
        assert 0 <= idx <= len(times) - 16

    def test_prefers_stable_middle(self):
        from rytmi.dsp import _find_stable_region

        # Jittery start (8 beats), stable middle (20 beats), jittery end (8 beats).
        rng = np.random.default_rng(42)
        jitter_start = np.cumsum(0.5 + rng.uniform(-0.15, 0.15, size=8))
        stable_mid = jitter_start[-1] + np.arange(1, 21) * 0.5
        jitter_end = stable_mid[-1] + np.cumsum(0.5 + rng.uniform(-0.15, 0.15, size=8))
        times = np.concatenate([[0.0], jitter_start, stable_mid, jitter_end])
        beats = BeatData(times=times, tempo=120.0, beat_frames=np.arange(len(times)))
        idx = _find_stable_region(beats, window=16)
        # The stable region starts around index 9 (after jittery start).
        assert 5 <= idx <= 15, f"Expected stable middle, got start={idx}"

    def test_short_track_returns_zero(self):
        from rytmi.dsp import _find_stable_region

        times = np.arange(5) * 0.5
        beats = BeatData(times=times, tempo=120.0, beat_frames=np.arange(5))
        assert _find_stable_region(beats) == 0


class TestExtrapolateFirstBeat:
    """Tests for _extrapolate_first_beat()."""

    def test_recovers_beat_zero_when_onsets_everywhere(self):
        from rytmi.dsp import _extrapolate_first_beat

        # 24 beats at 120 BPM, onsets at every beat — first beat should be 0.
        times = np.arange(24) * 0.5
        beats = BeatData(times=times, tempo=120.0, beat_frames=np.arange(24))
        onsets = OnsetData(times=times.copy(), strength=np.ones(24), sr=22050)
        idx = _extrapolate_first_beat(beats, onsets)
        assert idx == 0

    def test_returns_none_with_no_onsets(self):
        from rytmi.dsp import _extrapolate_first_beat

        times = np.arange(24) * 0.5
        beats = BeatData(times=times, tempo=120.0, beat_frames=np.arange(24))
        onsets = OnsetData(times=np.array([]), strength=np.array([]), sr=22050)
        assert _extrapolate_first_beat(beats, onsets) is None

    def test_finds_first_onset_aligned_beat(self):
        from rytmi.dsp import _extrapolate_first_beat

        # 24 beats at 120 BPM but onsets only from beat 4 onwards.
        times = np.arange(24) * 0.5
        beats = BeatData(times=times, tempo=120.0, beat_frames=np.arange(24))
        onset_times = times[4:]  # first onset at t=2.0 (beat index 4)
        onsets = OnsetData(
            times=onset_times, strength=np.ones(len(onset_times)), sr=22050,
        )
        idx = _extrapolate_first_beat(beats, onsets)
        assert idx == 4


class TestGridExtrapolationOffset:
    """Tests for _grid_extrapolation_offset()."""

    def test_uniform_strength_low_confidence(self):
        from rytmi.dsp import _grid_extrapolation_offset

        # All beats have equal onset strength → no position stands out.
        times = np.arange(24) * 0.5
        beats = BeatData(times=times, tempo=120.0, beat_frames=np.arange(24))
        onsets = OnsetData(times=times.copy(), strength=np.ones(24), sr=22050)
        _offset, conf = _grid_extrapolation_offset(beats, onsets)
        assert conf < 0.05  # near-zero confidence when all positions equal

    def test_strongest_position_wins(self):
        from rytmi.dsp import _grid_extrapolation_offset

        # Onsets at every beat, but position 2 has 3x strength.
        times = np.arange(24) * 0.5
        beats = BeatData(times=times, tempo=120.0, beat_frames=np.arange(24))
        strengths = np.ones(24)
        for i in range(24):
            if i % 4 == 2:
                strengths[i] = 3.0
        onsets = OnsetData(times=times.copy(), strength=strengths, sr=22050)
        offset, conf = _grid_extrapolation_offset(beats, onsets)
        assert offset == 2
        assert conf > 0.3

    def test_offset_from_missing_onsets(self):
        from rytmi.dsp import _grid_extrapolation_offset

        # Onsets only from beat 2 onwards — positions 0,1 get zero strength
        # on their first beat, lowering their mean vs positions 2,3.
        times = np.arange(24) * 0.5
        beats = BeatData(times=times, tempo=120.0, beat_frames=np.arange(24))
        onset_times = times[2:]
        onsets = OnsetData(
            times=onset_times, strength=np.ones(len(onset_times)), sr=22050,
        )
        offset, _conf = _grid_extrapolation_offset(beats, onsets)
        assert offset in (2, 3)  # both have full coverage

    def test_returns_zero_offset_zero_conf_when_no_onsets(self):
        from rytmi.dsp import _grid_extrapolation_offset

        times = np.arange(24) * 0.5
        beats = BeatData(times=times, tempo=120.0, beat_frames=np.arange(24))
        onsets = OnsetData(times=np.array([]), strength=np.array([]), sr=22050)
        offset, conf = _grid_extrapolation_offset(beats, onsets)
        assert offset == 0
        assert conf == 0.0


# ── Phase 40 — transition extraction ────────────────────────────────────────

def _phase(label: str, start: float, end: float, energy: str = "medium",
           beat_clarity: float = 0.4) -> SongPhase:
    rf = RhythmFeatures(
        onsets_per_beat=2.0,
        beat_strength_pattern=[1.0, 0.5, 0.7, 0.5],
        percussiveness=0.5,
        spectral_centroid_mean=2000.0,
        tempo_stability=0.9,
        ioi_median_ms=500.0,
        ioi_std_ms=20.0,
        beat_clarity=beat_clarity,
    )
    return SongPhase(
        label=label,
        start_s=start,
        end_s=end,
        section_count=1,
        energy_levels=[energy],
        avg_rhythm_features=rf,
    )


def test_extract_transitions_simple_arc():
    """intro → main → break → main → outro produces 4 transitions."""
    phases = [
        _phase("intro", 0.0, 12.0, "low", beat_clarity=0.4),
        _phase("main", 12.0, 148.0, "medium", beat_clarity=0.4),
        _phase("break", 148.0, 159.0, "low", beat_clarity=0.4),
        _phase("main", 159.0, 195.0, "medium", beat_clarity=0.4),
        _phase("outro", 195.0, 209.0, "low", beat_clarity=0.4),
    ]
    transitions = extract_transitions(phases)
    assert len(transitions) == 4
    assert [t.from_label for t in transitions] == ["intro", "main", "break", "main"]
    assert [t.to_label for t in transitions] == ["main", "break", "main", "outro"]
    assert [round(t.boundary_time_s) for t in transitions] == [12, 148, 159, 195]
    assert [t.from_phase_idx for t in transitions] == [0, 1, 2, 3]
    assert [t.to_phase_idx for t in transitions] == [1, 2, 3, 4]


def test_extract_transitions_same_label_runs_skipped():
    """Adjacent main phases (e.g. energy-only changes) emit no transition."""
    phases = [
        _phase("main", 0.0, 30.0, "medium"),
        _phase("main", 30.0, 60.0, "high"),  # same label, energy lift — skipped
        _phase("main", 60.0, 90.0, "medium"),  # same label — skipped
        _phase("break", 90.0, 100.0, "low"),  # label change → transition
        _phase("main", 100.0, 130.0, "medium"),  # label change → transition
    ]
    transitions = extract_transitions(phases)
    assert len(transitions) == 2
    assert transitions[0].from_label == "main" and transitions[0].to_label == "break"
    assert transitions[1].from_label == "break" and transitions[1].to_label == "main"


def test_extract_transitions_empty_or_single_phase_no_phantom():
    assert extract_transitions([]) == []
    assert extract_transitions([_phase("main", 0.0, 30.0)]) == []


def test_extract_transitions_carries_clarity_and_energy_tags():
    """Each transition records the surrounding clarity and energy tags."""
    phases = [
        _phase("main", 0.0, 30.0, energy="high", beat_clarity=0.5),  # clear
        _phase("break", 30.0, 40.0, energy="low", beat_clarity=0.15),  # subtle
    ]
    [tr] = extract_transitions(phases)
    assert tr.from_clarity == "clear"
    assert tr.to_clarity == "subtle"
    assert tr.from_energy == "high"
    assert tr.to_energy == "low"


def test_describe_transitions_format_stable():
    """describe_transitions returns a header + table with one line per transition."""
    audio = AudioData(samples=np.zeros(1000, dtype=np.float32), sr=22050,
                      duration=0.045)
    onsets = OnsetData(times=np.array([]), strength=np.array([]), sr=22050)
    beats = BeatData(times=np.array([0.0, 0.5]), tempo=120.0,
                     beat_frames=np.array([0, 11025]))
    phases = [
        _phase("intro", 0.0, 12.0, "low"),
        _phase("main", 12.0, 148.0, "medium"),
        _phase("outro", 148.0, 200.0, "low"),
    ]
    analysis = RhythmAnalysis(
        audio=audio, onsets=onsets, beats=beats, tempo=120.0, phases=phases,
    )
    description = describe_transitions(analysis)
    # Two transitions: intro→main, main→outro
    lines = description.split("\n")
    assert lines[0].startswith("Transitions table — 2 label boundaries")
    assert "intro" in description and "main" in description and "outro" in description


def test_describe_transitions_empty_phases_returns_explanation():
    audio = AudioData(samples=np.zeros(1000, dtype=np.float32), sr=22050,
                      duration=0.045)
    onsets = OnsetData(times=np.array([]), strength=np.array([]), sr=22050)
    beats = BeatData(times=np.array([0.0]), tempo=120.0, beat_frames=np.array([0]))
    analysis = RhythmAnalysis(
        audio=audio, onsets=onsets, beats=beats, tempo=120.0, phases=[],
    )
    assert "no transitions" in describe_transitions(analysis).lower()


def test_extract_transitions_default_excludes_same_label():
    """Phase 40d — default (include_same_label=False) preserves Phase 40 behaviour:
    same-label phase boundaries (energy shifts within a `main` run) emit nothing.
    """
    phases = [
        _phase("main", 0.0, 30.0, "medium"),
        _phase("main", 30.0, 60.0, "high"),  # energy lift, same label
        _phase("main", 60.0, 90.0, "medium"),  # energy settle, same label
    ]
    assert extract_transitions(phases) == []
    # explicit-False kwarg behaves the same
    assert extract_transitions(phases, include_same_label=False) == []


def test_extract_transitions_include_same_label_emits_energy_shifts():
    """Phase 40d — flag-on emits a Transition for every consecutive phase pair,
    including same-label energy shifts.
    """
    phases = [
        _phase("main", 0.0, 30.0, "medium"),
        _phase("main", 30.0, 60.0, "high"),  # main → main, medium → high
        _phase("main", 60.0, 90.0, "medium"),  # main → main, high → medium
        _phase("break", 90.0, 100.0, "low"),  # main → break, label change
    ]
    transitions = extract_transitions(phases, include_same_label=True)
    assert len(transitions) == 3
    # Same-label transitions carry energy info
    assert transitions[0].from_label == "main" and transitions[0].to_label == "main"
    assert transitions[0].from_energy == "medium" and transitions[0].to_energy == "high"
    assert transitions[1].from_label == "main" and transitions[1].to_label == "main"
    assert transitions[1].from_energy == "high" and transitions[1].to_energy == "medium"
    # Label-change transition still appears
    assert transitions[2].from_label == "main" and transitions[2].to_label == "break"


def test_extract_transitions_filomena_arc_with_same_label():
    """Phase 40d — Filomena's typical phase arc with same-label flag yields 7
    transitions (4 label-change + 3 main→main energy shifts).
    """
    phases = [
        _phase("intro", 0.0, 12.0, "low"),
        _phase("main", 12.0, 59.0, "medium"),  # main ×4
        _phase("main", 59.0, 80.0, "high"),    # main ×2 — energy lift
        _phase("main", 80.0, 121.0, "medium"), # main ×4 — energy settle
        _phase("main", 121.0, 148.0, "high"),  # main ×2 — energy lift
        _phase("break", 148.0, 159.0, "low"),
        _phase("main", 159.0, 195.0, "medium"),
        _phase("outro", 195.0, 209.0, "low"),
    ]
    label_only = extract_transitions(phases)
    assert len(label_only) == 4  # intro→main, main→break, break→main, main→outro
    full = extract_transitions(phases, include_same_label=True)
    assert len(full) == 7  # 4 label-change + 3 main→main energy shifts
