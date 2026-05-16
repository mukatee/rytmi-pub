"""Audio I/O: loading, trimming, normalization."""

from pathlib import Path

import librosa
import numpy as np

from rytmi.types import AudioData


def load_audio(
    path: str | Path,
    sr: int = 22050,
    mono: bool = True,
) -> AudioData:
    """Load an audio file and return an AudioData object."""
    path = str(path)
    y, sr_actual = librosa.load(path, sr=sr, mono=mono)
    return AudioData(
        samples=y,
        sr=sr_actual,
        duration=len(y) / sr_actual,
        filepath=path,
    )


def trim_silence(audio: AudioData, top_db: float = 20.0) -> AudioData:
    """Trim leading and trailing silence."""
    trimmed, _ = librosa.effects.trim(audio.samples, top_db=top_db)
    return AudioData(
        samples=trimmed,
        sr=audio.sr,
        duration=len(trimmed) / audio.sr,
        filepath=audio.filepath,
    )


def normalize(audio: AudioData) -> AudioData:
    """Peak-normalize audio to [-1, 1]."""
    peak = np.max(np.abs(audio.samples))
    if peak > 0:
        normalized = audio.samples / peak
    else:
        normalized = audio.samples
    return AudioData(
        samples=normalized,
        sr=audio.sr,
        duration=audio.duration,
        filepath=audio.filepath,
    )


def slice_audio(
    audio: AudioData,
    start_s: float,
    duration_s: float,
) -> AudioData:
    """Return a clipped copy of ``audio`` covering ``[start_s, start_s+duration_s)``.

    The window is clamped to the track bounds.  Negative starts are treated as 0.
    """
    start_s = max(0.0, float(start_s))
    end_s = min(audio.duration, start_s + max(0.0, float(duration_s)))
    start_idx = int(round(start_s * audio.sr))
    end_idx = int(round(end_s * audio.sr))
    clip = audio.samples[start_idx:end_idx]
    return AudioData(
        samples=clip,
        sr=audio.sr,
        duration=len(clip) / audio.sr if audio.sr > 0 else 0.0,
        filepath=audio.filepath,
    )
