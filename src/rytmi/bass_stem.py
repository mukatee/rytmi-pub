"""Demucs bass-stem extraction for harmonic-cue downbeat scoring.

Mirrors ``drum_stem.DemucsDrumStem`` but keeps the bass stem
(Demucs source ``"bass"``) instead of drums.

The bass-stem samples are cached as ``.demucs-bass.npz`` files in
``cache/bass/`` so separation cost is paid only once per track.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from rytmi.types import AudioData

__all__ = ["DemucsBassStem", "extract_bass_stem"]

_DEMUCS_MODEL = "htdemucs"
_DEFAULT_CACHE_DIR = Path("cache") / "bass"


def _cache_key(audio: AudioData, tag: str) -> str | None:
    """SHA-1 of ``(filepath, mtime, tag)``.  ``None`` when audio has no filepath."""
    if not audio.filepath:
        return None
    try:
        mtime = os.path.getmtime(audio.filepath)
    except OSError:
        return None
    h = hashlib.sha1()
    h.update(str(audio.filepath).encode())
    h.update(f"|{mtime:.6f}|{tag}".encode())
    return h.hexdigest()


def _load_cached(path: Path) -> NDArray[np.float32] | None:
    """Load cached bass-stem mono samples from an ``.npz`` file."""
    try:
        data = np.load(path, allow_pickle=False)
    except (OSError, ValueError):
        return None
    try:
        return np.asarray(data["bass_mono"], dtype=np.float32)
    except KeyError:
        return None


def _save_cached(path: Path, bass_mono: NDArray[np.float32]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(path, bass_mono=bass_mono)


class DemucsBassStem:
    """Extract and cache the Demucs bass stem for an audio track."""

    def __init__(
        self,
        *,
        cache_dir: Path | None = None,
        model_name: str = _DEMUCS_MODEL,
        device: str | None = None,
    ) -> None:
        self.cache_dir = Path(cache_dir) if cache_dir is not None else _DEFAULT_CACHE_DIR
        self.model_name = model_name
        self.device = device

    def extract(self, audio: AudioData) -> AudioData | None:
        """Return an ``AudioData`` whose samples are the bass-stem mono.

        Returns ``None`` if Demucs is unavailable or separation fails.
        Cached by ``(filepath, mtime, demucs-bass:<model>)`` so repeated
        calls are free.
        """
        key = _cache_key(audio, f"demucs-bass:{self.model_name}")
        cache_path = self.cache_dir / f"{key}.demucs-bass.npz" if key else None
        if cache_path is not None and cache_path.exists():
            cached = _load_cached(cache_path)
            if cached is not None:
                return AudioData(
                    samples=cached,
                    sr=audio.sr,
                    duration=audio.duration,
                    filepath=audio.filepath,
                )

        bass_mono = self._separate_bass(audio)
        if bass_mono is None:
            return None

        if cache_path is not None:
            try:
                _save_cached(cache_path, bass_mono)
            except OSError:
                pass  # cache is best-effort

        return AudioData(
            samples=bass_mono,
            sr=audio.sr,
            duration=audio.duration,
            filepath=audio.filepath,
        )

    def _separate_bass(self, audio: AudioData) -> NDArray[np.float32] | None:
        """Run Demucs and return the bass-stem mono samples at ``audio.sr``.

        Returns ``None`` if Demucs is unavailable or fails at runtime.
        Imports happen lazily so ``import rytmi.bass_stem`` stays cheap.
        """
        try:
            import torch

            from demucs.apply import apply_model
            from demucs.pretrained import get_model
        except ImportError:
            return None

        try:
            model = get_model(self.model_name)
            model.eval()
            device = self.device or ("cuda" if torch.cuda.is_available() else "cpu")
            model.to(device)

            target_sr = int(model.samplerate)
            samples = np.asarray(audio.samples, dtype=np.float32)
            if samples.ndim == 1:
                stereo = np.stack([samples, samples], axis=0)
            else:
                stereo = samples

            if audio.sr != target_sr:
                import librosa

                resampled = np.stack([
                    librosa.resample(stereo[0], orig_sr=audio.sr, target_sr=target_sr),
                    librosa.resample(stereo[1], orig_sr=audio.sr, target_sr=target_sr),
                ], axis=0)
            else:
                resampled = stereo

            wav = torch.tensor(resampled, dtype=torch.float32).unsqueeze(0).to(device)
            with torch.inference_mode():
                sources = apply_model(model, wav, device=device, progress=False)[0]
            bass_idx = model.sources.index("bass")
            bass_stereo = sources[bass_idx].detach().cpu().numpy()
            bass_mono = bass_stereo.mean(axis=0).astype(np.float32)

            if target_sr != audio.sr:
                import librosa

                bass_mono = librosa.resample(
                    bass_mono, orig_sr=target_sr, target_sr=audio.sr,
                ).astype(np.float32)

            return bass_mono
        except Exception:
            return None


def extract_bass_stem(
    audio: AudioData,
    *,
    cache_dir: Path | None = None,
    device: str | None = None,
) -> AudioData | None:
    """Convenience wrapper: extract bass stem with default settings."""
    return DemucsBassStem(cache_dir=cache_dir, device=device).extract(audio)
