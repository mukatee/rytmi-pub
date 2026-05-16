from pathlib import Path

import numpy as np

from rytmi.audio import load_audio, normalize, trim_silence
from rytmi.types import AudioData

SAMPLE_PATH = Path(__file__).parent.parent / "data" / "samples" / "click_120bpm.wav"


def test_load_audio_returns_audio_data():
    audio = load_audio(SAMPLE_PATH)
    assert isinstance(audio, AudioData)


def test_load_audio_correct_sr():
    audio = load_audio(SAMPLE_PATH, sr=22050)
    assert audio.sr == 22050


def test_load_audio_correct_duration():
    audio = load_audio(SAMPLE_PATH, sr=22050)
    assert abs(audio.duration - 10.0) < 0.1


def test_load_audio_shape():
    audio = load_audio(SAMPLE_PATH, sr=22050)
    assert audio.samples.ndim == 1
    assert len(audio.samples) == int(audio.sr * audio.duration)


def test_load_audio_filepath():
    audio = load_audio(SAMPLE_PATH)
    assert audio.filepath == str(SAMPLE_PATH)


def test_trim_silence():
    audio = load_audio(SAMPLE_PATH)
    trimmed = trim_silence(audio)
    assert isinstance(trimmed, AudioData)
    assert trimmed.duration <= audio.duration


def test_normalize():
    audio = load_audio(SAMPLE_PATH)
    normed = normalize(audio)
    assert isinstance(normed, AudioData)
    assert np.max(np.abs(normed.samples)) <= 1.0 + 1e-6


def test_normalize_silent():
    silent = AudioData(
        samples=np.zeros(1000, dtype=np.float32),
        sr=22050,
        duration=1000 / 22050,
    )
    normed = normalize(silent)
    assert np.all(normed.samples == 0)
