"""Shared test fixtures."""

from pathlib import Path

import numpy as np
import pytest

from rytmi.types import AudioData

SAMPLES_DIR = Path(__file__).parent.parent / "data" / "samples"


@pytest.fixture
def synthetic_click_audio() -> AudioData:
    """Generate a synthetic 120 BPM click track, 10 seconds."""
    sr = 22050
    duration = 10.0
    bpm = 120
    beat_interval = 60.0 / bpm

    samples = np.zeros(int(sr * duration), dtype=np.float32)
    click = np.sin(2 * np.pi * 1000 * np.arange(int(0.01 * sr)) / sr).astype(np.float32)
    click *= np.linspace(1, 0, len(click), dtype=np.float32)

    for t in np.arange(0, duration, beat_interval):
        idx = int(t * sr)
        end = min(idx + len(click), len(samples))
        samples[idx:end] = click[: end - idx]

    return AudioData(samples=samples, sr=sr, duration=duration)


@pytest.fixture
def synthetic_accented_click_audio() -> AudioData:
    """120 BPM click track where every 4th beat (the downbeat) is 5× louder.

    Uses a low-frequency (80 Hz) click to simulate a bass/kick drum transient,
    which produces a broad-spectrum onset that the confidence metric can detect
    clearly.  This fixture should produce meaningfully higher confidence than the
    uniform 1 kHz click track.
    """
    sr = 22050
    duration = 10.0
    bpm = 120
    beat_interval = 60.0 / bpm
    beats_per_measure = 4

    # ~20 ms low-frequency click — closer to a bass drum transient than a
    # narrow 1 kHz sine, so onset strength scales better with amplitude.
    click = np.sin(2 * np.pi * 80 * np.arange(int(0.02 * sr)) / sr).astype(np.float32)
    click *= np.linspace(1, 0, len(click), dtype=np.float32)

    samples = np.zeros(int(sr * duration), dtype=np.float32)
    for i, t in enumerate(np.arange(0, duration, beat_interval)):
        idx = int(t * sr)
        end = min(idx + len(click), len(samples))
        amplitude = 5.0 if (i % beats_per_measure == 0) else 1.0
        samples[idx:end] = amplitude * click[: end - idx]

    return AudioData(samples=samples, sr=sr, duration=duration)


@pytest.fixture
def click_wav_path() -> Path:
    """Path to the committed 120 BPM click track wav."""
    return SAMPLES_DIR / "click_120bpm.wav"
