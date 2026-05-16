"""Unit tests for the Gemma audio perception stage.

These tests never load a real multimodal model.  The ``transcribe_vocals``
tests mock ``processor``/``model`` to exercise only the clip-selection,
dispatch, and response-parsing paths.  A separate opt-in integration test
(gated on ``RYTMI_RUN_MULTIMODAL_TESTS``) lives at the bottom of this file.
"""

from __future__ import annotations

import os
from types import SimpleNamespace
from unittest.mock import MagicMock

import numpy as np
import pytest

from rytmi.audio import slice_audio
from rytmi.transcribe import (
    VocalsInfo,
    _parse_response,
    select_vocal_clip,
    transcribe_vocals,
)
from rytmi.types import AudioData, BeatData, OnsetData, RhythmAnalysis


def _make_analysis(
    duration: float,
    onset_strength: np.ndarray,
    sr: int = 22050,
) -> RhythmAnalysis:
    n_samples = int(duration * sr)
    audio = AudioData(
        samples=np.zeros(n_samples, dtype=np.float32),
        sr=sr,
        duration=duration,
    )
    onset_times = np.linspace(0.0, duration, onset_strength.size, endpoint=False)
    onsets = OnsetData(times=onset_times, strength=onset_strength, sr=sr)
    beats = BeatData(
        times=np.arange(0.0, duration, 0.5),
        tempo=120.0,
        beat_frames=np.arange(int(duration / 0.5), dtype=np.intp),
    )
    return RhythmAnalysis(audio=audio, onsets=onsets, beats=beats, tempo=120.0)


def test_select_vocal_clip_skips_intro():
    """Energy ramping up after 30% → clip start must be past the 15% skip."""
    n = 300
    strength = np.zeros(n)
    strength[int(0.35 * n) : int(0.75 * n)] = 10.0  # dense middle
    analysis = _make_analysis(duration=120.0, onset_strength=strength)

    start_s, dur_s = select_vocal_clip(analysis, target_duration_s=20.0)

    assert dur_s == pytest.approx(20.0, abs=0.2)
    assert start_s >= 0.15 * 120.0
    # The dense region starts at 42s; the 20s window should overlap it.
    assert start_s <= 0.75 * 120.0


def test_select_vocal_clip_clamps_to_track_end():
    """Short track → returned window fits inside the track."""
    analysis = _make_analysis(duration=10.0, onset_strength=np.ones(40))
    start_s, dur_s = select_vocal_clip(analysis, target_duration_s=20.0)
    assert start_s == pytest.approx(0.0)
    assert dur_s == pytest.approx(10.0)
    assert start_s + dur_s <= 10.0 + 1e-6


def test_select_vocal_clip_deterministic():
    """Same input → same output (no RNG, no sampling)."""
    strength = np.sin(np.linspace(0.0, 4.0, 500)) ** 2
    analysis = _make_analysis(duration=180.0, onset_strength=strength)
    a = select_vocal_clip(analysis)
    b = select_vocal_clip(analysis)
    assert a == b


def test_transcribe_vocals_parses_language_only_response():
    """Mock returning 'Spanish' → VocalsInfo.language == 'spanish'."""
    analysis = _make_analysis(duration=60.0, onset_strength=np.ones(240))
    audio = analysis.audio

    processor = MagicMock()
    processor.apply_chat_template.return_value = {
        "input_ids": _fake_tensor(np.array([[1, 2, 3]])),
    }
    processor.decode.return_value = "Spanish"

    model = _fake_model(output_ids=np.array([[1, 2, 3, 99]]))

    result = transcribe_vocals(audio, analysis, processor, model)

    assert isinstance(result, VocalsInfo)
    assert result.language == "spanish"
    assert result.lyric_snippet == ""
    assert result.raw_response == "Spanish"
    assert result.clip_duration_s > 0


def test_transcribe_vocals_parses_two_line_lyrics_response():
    """lyrics mode: two lines → language + snippet."""
    analysis = _make_analysis(duration=60.0, onset_strength=np.ones(240))
    audio = analysis.audio

    processor = MagicMock()
    processor.apply_chat_template.return_value = {
        "input_ids": _fake_tensor(np.array([[1, 2, 3]])),
    }
    processor.decode.return_value = "Portuguese\nTeu toque me faz sonhar"

    model = _fake_model(output_ids=np.array([[1, 2, 3, 99]]))

    result = transcribe_vocals(
        audio, analysis, processor, model, mode="lyrics"
    )

    assert result.language == "portuguese"
    assert "Teu toque" in result.lyric_snippet


def test_transcribe_vocals_graceful_on_garbage_response():
    """Garbage/refusal responses → language='unknown', no raise."""
    analysis = _make_analysis(duration=60.0, onset_strength=np.ones(240))
    audio = analysis.audio

    for raw in ["", "I cannot hear any audio", "¯\\_(ツ)_/¯"]:
        processor = MagicMock()
        processor.apply_chat_template.return_value = {
            "input_ids": _fake_tensor(np.array([[1, 2, 3]])),
        }
        processor.decode.return_value = raw
        model = _fake_model(output_ids=np.array([[1, 2, 3, 99]]))

        result = transcribe_vocals(audio, analysis, processor, model)
        assert result.language == "unknown", f"raw={raw!r}"
        assert result.raw_response == raw


def test_parse_response_aliases_creole_to_kriol():
    lang, snippet = _parse_response("Cape Verdean Creole", mode="language_only")
    assert lang == "kriol"
    assert snippet == ""


def test_parse_response_handles_trailing_punctuation():
    lang, _ = _parse_response("Spanish.", mode="language_only")
    assert lang == "spanish"


def test_transcribe_retries_on_instrumental():
    """If first clip returns 'instrumental', retry with a later clip position."""
    analysis = _make_analysis(duration=120.0, onset_strength=np.ones(480))
    audio = analysis.audio

    call_count = [0]

    def mock_decode(tokens, skip_special_tokens=True):
        call_count[0] += 1
        if call_count[0] == 1:
            return "instrumental"
        return "Spanish"

    processor = MagicMock()
    processor.apply_chat_template.return_value = {
        "input_ids": _fake_tensor(np.array([[1, 2, 3]])),
    }
    processor.decode.side_effect = mock_decode

    model = _fake_model(output_ids=np.array([[1, 2, 3, 99]]))

    result = transcribe_vocals(audio, analysis, processor, model)

    assert result.language == "spanish"
    assert call_count[0] == 2


def test_transcribe_returns_last_result_when_all_retries_fail():
    """If all retries return 'unknown', return the last result."""
    analysis = _make_analysis(duration=120.0, onset_strength=np.ones(480))
    audio = analysis.audio

    processor = MagicMock()
    processor.apply_chat_template.return_value = {
        "input_ids": _fake_tensor(np.array([[1, 2, 3]])),
    }
    processor.decode.return_value = "unknown"

    model = _fake_model(output_ids=np.array([[1, 2, 3, 99]]))

    result = transcribe_vocals(audio, analysis, processor, model, max_retries=3)

    assert result.language == "unknown"
    # Should have been called 3 times (all retries exhausted).
    assert processor.decode.call_count == 3


def test_transcribe_no_retry_when_language_detected():
    """If first clip returns a real language, no retry should happen."""
    analysis = _make_analysis(duration=60.0, onset_strength=np.ones(240))
    audio = analysis.audio

    processor = MagicMock()
    processor.apply_chat_template.return_value = {
        "input_ids": _fake_tensor(np.array([[1, 2, 3]])),
    }
    processor.decode.return_value = "Portuguese"

    model = _fake_model(output_ids=np.array([[1, 2, 3, 99]]))

    result = transcribe_vocals(audio, analysis, processor, model)

    assert result.language == "portuguese"
    assert processor.decode.call_count == 1


def test_slice_audio_clamps_to_bounds():
    sr = 1000
    samples = np.arange(5000, dtype=np.float32)
    audio = AudioData(samples=samples, sr=sr, duration=5.0)

    clip = slice_audio(audio, start_s=-1.0, duration_s=10.0)
    assert clip.duration == pytest.approx(5.0)
    assert clip.samples.size == 5000


# ── Mocking helpers ──────────────────────────────────────────────────────────


class _FakeTensor:
    """Minimal torch-tensor stand-in so transcribe_vocals can call .to() and .shape."""

    def __init__(self, arr: np.ndarray):
        self._arr = np.asarray(arr)

    @property
    def shape(self):
        return self._arr.shape

    def to(self, _device):
        return self

    def __getitem__(self, idx):
        return _FakeTensor(self._arr[idx])


def _fake_tensor(arr: np.ndarray) -> _FakeTensor:
    return _FakeTensor(arr)


def _fake_model(output_ids: np.ndarray):
    """Build a mock Gemma model whose .generate returns output_ids."""
    mock = MagicMock()
    mock.hf_device_map = None
    mock.device = "cpu"
    mock.generate.return_value = _FakeTensor(output_ids)
    return mock


# ── Opt-in slow integration test ─────────────────────────────────────────────


@pytest.mark.skipif(
    not os.environ.get("RYTMI_RUN_MULTIMODAL_TESTS"),
    reason="set RYTMI_RUN_MULTIMODAL_TESTS=1 to load the real Gemma 4 multimodal model",
)
def test_transcribe_vocals_real_model_on_click_fixture(synthetic_click_audio):
    """End-to-end smoke test: load real Gemma 4, transcribe a click track.

    Skipped by default.  Uses the synthetic click fixture (not copyrighted
    eval-set audio) so the test is fully self-contained.  The click is
    instrumental, so we only assert that the call completes and returns a
    plausible language string; we accept 'instrumental' or 'unknown' as correct.
    """
    from rytmi.dsp import analyze
    from rytmi.transcribe import load_multimodal_model

    analysis = analyze(synthetic_click_audio)
    processor, model = load_multimodal_model()
    result = transcribe_vocals(synthetic_click_audio, analysis, processor, model)
    assert isinstance(result.language, str)
    assert len(result.language) > 0
