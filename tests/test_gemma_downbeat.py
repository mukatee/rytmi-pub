"""Tests for the Phase 13 Commit B2 Gemma downbeat tiebreaker."""

from __future__ import annotations

from types import SimpleNamespace

import numpy as np
import pytest

from rytmi import gemma_downbeat as gd
from rytmi.gemma_downbeat import (
    DownbeatTiebreakResult,
    _candidate_clip_window,
    refine_downbeats_via_gemma,
)
from rytmi.types import AudioData, BeatData


# ------------------------------ fixtures ------------------------------


def _make_audio(duration_s: float = 16.0, sr: int = 22050) -> AudioData:
    n = int(duration_s * sr)
    return AudioData(
        samples=np.zeros(n, dtype=np.float32),
        sr=sr,
        duration=duration_s,
        filepath="/tmp/fake.wav",
    )


def _make_beats(n_beats: int = 32, period_s: float = 0.5) -> BeatData:
    times = np.arange(n_beats, dtype=np.float64) * period_s
    return BeatData(
        times=times,
        tempo=60.0 / period_s,
        beat_frames=np.arange(n_beats, dtype=np.intp),
    )


def _scripted_query(per_offset_votes: dict[int, float | None], beats_per_measure: int = 4):
    """Build a fake `_query_gemma_downbeat` that returns the vote attached to whichever
    candidate offset's window currently fires (identified by start_s % measure_s)."""

    def _fake(audio, processor, model, start_s, dur_s):  # noqa: ARG001
        # `start_s` corresponds to `times[offset + k*bpm]` for the first eligible k;
        # with our 0.5 s beats and bpm=4 that's just `0.5 * offset` for offset 0..3.
        offset = int(round(start_s / 0.5)) % beats_per_measure
        return per_offset_votes.get(offset)

    return _fake


# ------------------------------ no-op guards ------------------------------


def test_no_op_when_processor_is_none():
    audio = _make_audio()
    beats = _make_beats()
    result = refine_downbeats_via_gemma(
        audio, beats, processor=None, model=SimpleNamespace(),
        dsp_offset=2, dsp_confidence=0.10,
    )
    assert isinstance(result, DownbeatTiebreakResult)
    assert result.fired is False
    assert result.best_offset == 2
    assert result.confidence == pytest.approx(0.10)
    assert np.isnan(result.gemma_votes).all()
    # downbeat_times follows the DSP offset stride.
    assert np.allclose(result.downbeat_times, beats.times[2::4])


def test_no_op_when_model_is_none():
    audio = _make_audio()
    beats = _make_beats()
    result = refine_downbeats_via_gemma(
        audio, beats, processor=SimpleNamespace(), model=None,
        dsp_offset=0, dsp_confidence=0.10,
    )
    assert result.fired is False


def test_no_op_when_confidence_above_band(monkeypatch):
    audio = _make_audio()
    beats = _make_beats()
    # Above max → must short-circuit before any Gemma query.
    monkeypatch.setattr(
        gd, "_query_gemma_downbeat",
        lambda *a, **k: pytest.fail("Gemma must not be queried when conf is above band"),
    )
    result = refine_downbeats_via_gemma(
        audio, beats, processor=SimpleNamespace(), model=SimpleNamespace(),
        dsp_offset=1, dsp_confidence=0.50,
    )
    assert result.fired is False
    assert result.best_offset == 1


def test_no_op_when_confidence_below_band(monkeypatch):
    audio = _make_audio()
    beats = _make_beats()
    monkeypatch.setattr(
        gd, "_query_gemma_downbeat",
        lambda *a, **k: pytest.fail("Gemma must not be queried when conf is below band"),
    )
    result = refine_downbeats_via_gemma(
        audio, beats, processor=SimpleNamespace(), model=SimpleNamespace(),
        dsp_offset=0, dsp_confidence=-0.01,
    )
    assert result.fired is False


def test_no_op_when_too_few_beats(monkeypatch):
    """beats_per_measure (4) + clip_beats (8) = 12 needed; supply only 8."""
    audio = _make_audio()
    beats = _make_beats(n_beats=8)
    monkeypatch.setattr(
        gd, "_query_gemma_downbeat",
        lambda *a, **k: pytest.fail("Gemma must not run with too few beats"),
    )
    result = refine_downbeats_via_gemma(
        audio, beats, processor=SimpleNamespace(), model=SimpleNamespace(),
        dsp_offset=0, dsp_confidence=0.10,
    )
    assert result.fired is False


# ------------------------------ combination logic ------------------------------


def test_agree_endorses_dsp_and_boosts_confidence(monkeypatch):
    """Gemma YES only on dsp_offset → endorse dsp, conf = max(0.30, dsp_conf)."""
    audio = _make_audio()
    beats = _make_beats()
    monkeypatch.setattr(
        gd, "_query_gemma_downbeat",
        _scripted_query({0: 0.0, 1: 0.0, 2: 1.0, 3: 0.0}),
    )
    result = refine_downbeats_via_gemma(
        audio, beats, processor=SimpleNamespace(), model=SimpleNamespace(),
        dsp_offset=2, dsp_confidence=0.10,
    )
    assert result.fired is True
    assert result.best_offset == 2
    assert result.confidence == pytest.approx(0.30)
    assert result.gemma_votes.tolist() == [0.0, 0.0, 1.0, 0.0]
    assert np.allclose(result.downbeat_times, beats.times[2::4])


def test_switch_when_gemma_picks_different_single_offset(monkeypatch):
    """Single YES on a different offset → switch to it at the modest fixed conf."""
    audio = _make_audio()
    beats = _make_beats()
    monkeypatch.setattr(
        gd, "_query_gemma_downbeat",
        _scripted_query({0: 0.0, 1: 1.0, 2: 0.0, 3: 0.0}),
    )
    result = refine_downbeats_via_gemma(
        audio, beats, processor=SimpleNamespace(), model=SimpleNamespace(),
        dsp_offset=0, dsp_confidence=0.05,
    )
    assert result.fired is True
    assert result.best_offset == 1
    assert result.confidence == pytest.approx(0.30)
    assert np.allclose(result.downbeat_times, beats.times[1::4])


def test_all_no_leaves_dsp_unchanged(monkeypatch):
    """Gemma sees no measure-start anywhere → DSP carries through unchanged but fired."""
    audio = _make_audio()
    beats = _make_beats()
    monkeypatch.setattr(
        gd, "_query_gemma_downbeat",
        _scripted_query({0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0}),
    )
    result = refine_downbeats_via_gemma(
        audio, beats, processor=SimpleNamespace(), model=SimpleNamespace(),
        dsp_offset=3, dsp_confidence=0.12,
    )
    assert result.fired is True
    assert result.best_offset == 3
    assert result.confidence == pytest.approx(0.12)
    assert result.gemma_votes.tolist() == [0.0, 0.0, 0.0, 0.0]


def test_multi_yes_with_dsp_endorses_dsp(monkeypatch):
    """Multiple YES votes including DSP's pick → endorse DSP, conf = max(0.30, dsp)."""
    audio = _make_audio()
    beats = _make_beats()
    monkeypatch.setattr(
        gd, "_query_gemma_downbeat",
        _scripted_query({0: 1.0, 1: 0.0, 2: 1.0, 3: 1.0}),
    )
    result = refine_downbeats_via_gemma(
        audio, beats, processor=SimpleNamespace(), model=SimpleNamespace(),
        dsp_offset=2, dsp_confidence=0.08,
    )
    assert result.fired is True
    assert result.best_offset == 2
    assert result.confidence == pytest.approx(0.30)


def test_multi_yes_without_dsp_leaves_dsp(monkeypatch):
    """Multiple YES votes none of which match DSP → ambiguous, leave DSP untouched."""
    audio = _make_audio()
    beats = _make_beats()
    monkeypatch.setattr(
        gd, "_query_gemma_downbeat",
        _scripted_query({0: 1.0, 1: 1.0, 2: 0.0, 3: 0.0}),
    )
    result = refine_downbeats_via_gemma(
        audio, beats, processor=SimpleNamespace(), model=SimpleNamespace(),
        dsp_offset=2, dsp_confidence=0.07,
    )
    assert result.fired is True
    assert result.best_offset == 2
    assert result.confidence == pytest.approx(0.07)


def test_partial_failure_does_not_synthesize_decision(monkeypatch):
    """If any per-offset query returns None, refine bails out (fired=False) but
    preserves the votes vector for diagnostics."""
    audio = _make_audio()
    beats = _make_beats()
    monkeypatch.setattr(
        gd, "_query_gemma_downbeat",
        _scripted_query({0: 1.0, 1: 0.0, 2: None, 3: 0.0}),
    )
    result = refine_downbeats_via_gemma(
        audio, beats, processor=SimpleNamespace(), model=SimpleNamespace(),
        dsp_offset=0, dsp_confidence=0.10,
    )
    assert result.fired is False
    # DSP-original answer preserved.
    assert result.best_offset == 0
    assert result.confidence == pytest.approx(0.10)
    # Votes vector retains the partial info (one nan slot).
    assert result.gemma_votes[0] == 1.0
    assert result.gemma_votes[1] == 0.0
    assert np.isnan(result.gemma_votes[2])
    assert result.gemma_votes[3] == 0.0


# ------------------------------ helper ------------------------------


def test_candidate_clip_window_returns_none_when_too_few_beats():
    beats = _make_beats(n_beats=8)
    assert _candidate_clip_window(beats, offset=0, clip_beats=8, beats_per_measure=4) is None


def test_candidate_clip_window_picks_first_eligible_window():
    beats = _make_beats(n_beats=32, period_s=0.5)
    # offset=2 → first window starts at beats.times[2] = 1.0, spans 8 beats = 4.0 s.
    win = _candidate_clip_window(beats, offset=2, clip_beats=8, beats_per_measure=4)
    assert win is not None
    start_s, dur_s = win
    assert start_s == pytest.approx(1.0)
    assert dur_s == pytest.approx(4.0)
