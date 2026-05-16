"""Demucs drum-stem extraction for downbeat-confidence preprocessing.

Phase 14 Option 2 — mirrors `vocal_activity.DemucsVocalActivity` but keeps
the drums stem (Demucs source index 0, ``model.sources.index("drums")``)
instead of the vocals stem.

The drum-stem samples are cached as ``.demucs-drums.npz`` files in
``cache/drums/`` so separation cost (~30 s / track on GPU) is paid only once.

Gate: ``_USE_DRUM_STEM = False`` by default; opt in from notebooks or eval
scripts.  Not wired into ``analyze()`` or the notebook flow in this phase.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from rytmi.types import AudioData

__all__ = ["DemucsDrumStem", "extract_drum_stem"]

_DEMUCS_MODEL = "htdemucs"
_DEFAULT_CACHE_DIR = Path("cache") / "drums"

# Module-level gate — off by default so nothing ships until reviewed.
_USE_DRUM_STEM = False


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
    """Load cached drum-stem mono samples from an ``.npz`` file."""
    try:
        data = np.load(path, allow_pickle=False)
    except (OSError, ValueError):
        return None
    try:
        return np.asarray(data["drums_mono"], dtype=np.float32)
    except KeyError:
        return None


def _save_cached(path: Path, drums_mono: NDArray[np.float32]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(path, drums_mono=drums_mono)


class DemucsDrumStem:
    """Extract and cache the Demucs drums stem for an audio track."""

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
        """Return an ``AudioData`` whose samples are the drums-stem mono.

        Returns ``None`` if Demucs is unavailable or separation fails.
        Cached by ``(filepath, mtime, demucs-drums:<model>)`` so repeated
        calls are free.
        """
        key = _cache_key(audio, f"demucs-drums:{self.model_name}")
        cache_path = self.cache_dir / f"{key}.demucs-drums.npz" if key else None
        if cache_path is not None and cache_path.exists():
            cached = _load_cached(cache_path)
            if cached is not None:
                return AudioData(
                    samples=cached,
                    sr=audio.sr,
                    duration=audio.duration,
                    filepath=audio.filepath,
                )

        drums_mono = self._separate_drums(audio)
        if drums_mono is None:
            return None

        if cache_path is not None:
            try:
                _save_cached(cache_path, drums_mono)
            except OSError:
                pass  # cache is best-effort

        return AudioData(
            samples=drums_mono,
            sr=audio.sr,
            duration=audio.duration,
            filepath=audio.filepath,
        )

    def _separate_drums(self, audio: AudioData) -> NDArray[np.float32] | None:
        """Run Demucs and return the drums-stem mono samples at ``audio.sr``.

        Returns ``None`` if Demucs is unavailable or fails at runtime.
        Imports happen lazily so ``import rytmi.drum_stem`` stays cheap.
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
            drum_idx = model.sources.index("drums")
            drum_stereo = sources[drum_idx].detach().cpu().numpy()
            drum_mono = drum_stereo.mean(axis=0).astype(np.float32)

            if target_sr != audio.sr:
                import librosa

                drum_mono = librosa.resample(
                    drum_mono, orig_sr=target_sr, target_sr=audio.sr,
                ).astype(np.float32)

            return drum_mono
        except Exception:
            return None


def extract_drum_stem(
    audio: AudioData,
    *,
    cache_dir: Path | None = None,
    device: str | None = None,
) -> AudioData | None:
    """Convenience wrapper: extract drums stem as ``AudioData`` or ``None``."""
    return DemucsDrumStem(cache_dir=cache_dir, device=device).extract(audio)
