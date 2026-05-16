"""Vocal activity envelope extraction for boundary-aware section labeling.

The DSP section labeller is signal-blind to vocals specifically — a long
instrumental intro looks like a `main` section, and a low-energy pre-vocal
passage can be mislabelled as a `break`.  This module produces a per-frame
or per-window vocal activity envelope that downstream passes
(`_extend_intro_to_first_vocal`, `_contract_outro_to_last_vocal`) consume to
pull intro/outro edges to where vocals actually start/end.

Two sources are provided behind a common protocol:

- `DemucsVocalActivity` — primary, uses Demucs v4 (`htdemucs`) to isolate the
  vocal stem and reports per-frame RMS.  Highest resolution, best quality,
  but adds an ~80 MB model download.

- `GemmaVocalActivity` — experimental, reuses the Gemma 4 E4B multimodal
  pipeline already present in `transcribe.py`.  Asks Gemma a per-window
  vocal-presence question and builds a coarser window-level envelope.
  Part of the Kaggle demo's "Gemma central" goal.

Both return `None` on any failure (missing dependency, model load error,
runtime exception) so the pipeline degrades to the pre-vocal behaviour
rather than crashing.

Phase 12b (docs/experiments/19-...) listening pass on the 10-track eval
set: `GemmaVocalActivity` was found to routinely flip main ↔ instrumental
labels (Grupo Extra M48-M92) and to drift by ~8 counts on Baila.  Demucs
remains the recommended default; the gemma source stays in-tree as an
opt-in experiment, not for production use.
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import numpy as np
from numpy.typing import NDArray

from rytmi.types import AudioData

__all__ = [
    "VocalActivityEnvelope",
    "VocalActivitySource",
    "DemucsVocalActivity",
    "GemmaVocalActivity",
    "GemmaSpeechDetector",
    "default_vocal_activity_source",
]


@dataclass
class VocalActivityEnvelope:
    """Time-resolved vocal activity signal for a track.

    `times[i]` is the centre time (s) of frame/window `i`.  `rms[i]` is a
    non-negative vocal-energy or vocal-confidence score — its scale depends
    on the source (Demucs: vocal-stem RMS; Gemma: YES/NO confidence).
    `active[i]` is the per-frame thresholded decision.
    """

    times: NDArray[np.float64]
    rms: NDArray[np.float32]
    active: NDArray[np.bool_]
    sr: int  # effective frames/second of the times grid
    source: str  # "demucs" | "gemma" | "fake" (tests)


class VocalActivitySource(Protocol):
    """Produces a `VocalActivityEnvelope` from an `AudioData` track.

    Implementations must return `None` on failure instead of raising, so
    callers can no-op the vocal-aware passes without a try/except.
    """

    def compute(self, audio: AudioData) -> VocalActivityEnvelope | None: ...

    def release(self) -> None: ...


# --- caching ---

_DEFAULT_CACHE_DIR = Path("cache") / "vocals"


def _cache_key(audio: AudioData, tag: str) -> str | None:
    """sha1 of (filepath, mtime, tag).  None when audio has no filepath."""
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


def _load_cached(path: Path, source: str) -> VocalActivityEnvelope | None:
    try:
        data = np.load(path, allow_pickle=False)
    except (OSError, ValueError):
        return None
    try:
        return VocalActivityEnvelope(
            times=np.asarray(data["times"], dtype=np.float64),
            rms=np.asarray(data["rms"], dtype=np.float32),
            active=np.asarray(data["active"], dtype=bool),
            sr=int(data["sr"].item()),
            source=source,
        )
    except KeyError:
        return None


def _save_cached(path: Path, env: VocalActivityEnvelope) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(
        path,
        times=env.times,
        rms=env.rms,
        active=env.active,
        sr=np.int64(env.sr),
    )


# --- Demucs path ---


_DEMUCS_MODEL = "htdemucs"
_DEMUCS_HOP = 512  # hop length for the RMS envelope, at 22050 Hz → ~43 fps
# Per-track adaptive cutoff per Ricci et al. 2025 (arXiv 2506.15514): convert the
# Demucs vocal-stem RMS to dB, take the per-track mean, and treat anything within
# `_VOCAL_DB_BELOW_MEAN` of that mean as vocal-active.  An absolute dB floor stops
# near-silence tracks from triggering false positives, and a moving-average smooth
# on the binary signal closes one-frame gaps inside a sustained vocal phrase.
_VOCAL_DB_BELOW_MEAN = 18.0
_VOCAL_SMOOTH_WINDOW_S = 3.0
_VOCAL_ACTIVE_FLOOR_DB = -60.0
_VOCAL_DB_EPS = 1e-8


class DemucsVocalActivity:
    """Primary vocal activity source backed by Demucs v4 `htdemucs`."""

    def __init__(
        self,
        *,
        cache_dir: Path | None = None,
        model_name: str = _DEMUCS_MODEL,
        hop_length: int = _DEMUCS_HOP,
        db_below_mean: float = _VOCAL_DB_BELOW_MEAN,
        floor_db: float = _VOCAL_ACTIVE_FLOOR_DB,
        smooth_window_s: float = _VOCAL_SMOOTH_WINDOW_S,
        device: str | None = None,
    ) -> None:
        self.cache_dir = Path(cache_dir) if cache_dir is not None else _DEFAULT_CACHE_DIR
        self.model_name = model_name
        self.hop_length = hop_length
        self.db_below_mean = db_below_mean
        self.floor_db = floor_db
        self.smooth_window_s = smooth_window_s
        self.device = device

    def compute(self, audio: AudioData) -> VocalActivityEnvelope | None:
        key = _cache_key(audio, f"demucs:{self.model_name}")
        cache_path = self.cache_dir / f"{key}.demucs.npz" if key else None
        if cache_path is not None and cache_path.exists():
            cached = _load_cached(cache_path, "demucs")
            if cached is not None:
                # Re-derive `active` from the cached vocal-stem RMS so threshold
                # tweaks take effect without paying the Demucs separation cost.
                frames_per_sec = (
                    float(audio.sr) / float(self.hop_length)
                    if self.hop_length > 0
                    else float(audio.sr)
                )
                refreshed = self._threshold(cached.rms, frames_per_sec=frames_per_sec)
                return VocalActivityEnvelope(
                    times=cached.times,
                    rms=cached.rms,
                    active=refreshed,
                    sr=cached.sr,
                    source=cached.source,
                )

        vocal_mono = self._separate_vocals(audio)
        if vocal_mono is None:
            return None

        import librosa

        rms = librosa.feature.rms(
            y=vocal_mono.astype(np.float32), hop_length=self.hop_length,
        )[0].astype(np.float32)
        times = librosa.frames_to_time(
            np.arange(len(rms)), sr=audio.sr, hop_length=self.hop_length,
        )
        frames_per_sec = (
            float(audio.sr) / float(self.hop_length) if self.hop_length > 0 else float(audio.sr)
        )
        active = self._threshold(rms, frames_per_sec=frames_per_sec)
        env = VocalActivityEnvelope(
            times=times.astype(np.float64),
            rms=rms,
            active=active,
            sr=int(audio.sr // self.hop_length) if self.hop_length > 0 else int(audio.sr),
            source="demucs",
        )
        if cache_path is not None:
            try:
                _save_cached(cache_path, env)
            except OSError:
                pass  # cache is best-effort
        return env

    def _threshold(
        self,
        rms: NDArray[np.float32],
        *,
        frames_per_sec: float,
    ) -> NDArray[np.bool_]:
        if rms.size == 0:
            return np.zeros_like(rms, dtype=bool)
        rms_db = 20.0 * np.log10(np.asarray(rms, dtype=np.float64) + _VOCAL_DB_EPS)
        mean_db = float(np.mean(rms_db))
        cutoff_db = max(self.floor_db, mean_db - self.db_below_mean)
        binary = rms_db > cutoff_db

        if self.smooth_window_s > 0.0 and frames_per_sec > 0.0 and binary.size > 0:
            window = max(1, int(round(self.smooth_window_s * frames_per_sec)))
            window = min(window, binary.size)
            if window > 1:
                from scipy.ndimage import uniform_filter1d

                smoothed = uniform_filter1d(
                    binary.astype(np.float64), size=window, mode="nearest",
                )
                binary = smoothed >= 0.5

        return binary.astype(bool)

    def release(self) -> None:
        """No-op for interface parity with Gemma-backed sources."""
        return None

    def _separate_vocals(self, audio: AudioData) -> NDArray[np.float32] | None:
        """Run Demucs and return the vocal-stem mono samples at audio.sr.

        Returns None if Demucs is unavailable or fails at runtime.  Imports
        happen lazily here so that `import rytmi.vocal_activity` stays cheap.
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
            vocal_idx = model.sources.index("vocals")
            vocal_stereo = sources[vocal_idx].detach().cpu().numpy()
            vocal_mono = vocal_stereo.mean(axis=0).astype(np.float32)

            if target_sr != audio.sr:
                import librosa

                vocal_mono = librosa.resample(
                    vocal_mono, orig_sr=target_sr, target_sr=audio.sr,
                ).astype(np.float32)

            return vocal_mono
        except Exception:
            return None


# --- Gemma experimental path ---


_GEMMA_WINDOW_S = 30.0
_GEMMA_WINDOW_HOP_S = 30.0
_GEMMA_YES_PROMPT = (
    "Listen to this audio clip. Is there any human singing or vocals audible? "
    "Answer with exactly one word: YES or NO."
)


class GemmaVocalActivity:
    """Experimental vocal activity source backed by Gemma 4 E4B multimodal.

    Windows the track into ~30 s clips and asks Gemma a per-window YES/NO
    vocal-presence question.  Coarser than Demucs and slower, but keeps the
    Kaggle demo's "Gemma central" story intact and provides a fallback when
    Demucs is unavailable.

    Per the Phase 12b listening pass
    (``docs/experiments/19-2026-04-19-phase-12b-vocal-source-ab.md``),
    prefer :class:`DemucsVocalActivity` for production — this source flips
    main ↔ instrumental and drifts by ~8 counts on some eval tracks.
    Opt-in for experiments only.
    """

    def __init__(
        self,
        *,
        processor=None,
        model=None,
        cache_dir: Path | None = None,
        window_s: float = _GEMMA_WINDOW_S,
        hop_s: float = _GEMMA_WINDOW_HOP_S,
        prompt: str = _GEMMA_YES_PROMPT,
    ) -> None:
        self.processor = processor
        self.model = model
        self.cache_dir = Path(cache_dir) if cache_dir is not None else _DEFAULT_CACHE_DIR
        self.window_s = window_s
        self.hop_s = hop_s
        self.prompt = prompt

    def compute(self, audio: AudioData) -> VocalActivityEnvelope | None:
        key = _cache_key(audio, "gemma")
        cache_path = self.cache_dir / f"{key}.gemma.npz" if key else None
        if cache_path is not None and cache_path.exists():
            cached = _load_cached(cache_path, "gemma")
            if cached is not None:
                return cached

        # Track whether we load the model here so we can free it afterward.
        # Caller-injected models (e.g. test fixtures) are left resident.
        owned_model = self.processor is None
        processor, model = self._ensure_model()
        if processor is None or model is None:
            return None

        try:
            windows = self._windows(audio.duration)
            if not windows:
                return None
            confidences: list[float] = []
            activities: list[bool] = []
            for start_s, dur_s in windows:
                score = self._query_window(audio, processor, model, start_s, dur_s)
                if score is None:
                    return None
                confidences.append(float(score))
                activities.append(score >= 0.5)

            centres = np.asarray(
                [s + d * 0.5 for s, d in windows], dtype=np.float64,
            )
            env = VocalActivityEnvelope(
                times=centres,
                rms=np.asarray(confidences, dtype=np.float32),
                active=np.asarray(activities, dtype=bool),
                sr=max(1, int(round(1.0 / self.hop_s))) if self.hop_s > 0 else 1,
                source="gemma",
            )
            if cache_path is not None:
                try:
                    _save_cached(cache_path, env)
                except OSError:
                    pass
            return env
        except Exception:
            return None
        finally:
            if owned_model:
                self._free_model()

    def _free_model(self) -> None:
        """Release the Gemma model from memory.

        Called after each compute() when the model was loaded by this instance
        (not passed in by a caller).  Frees VRAM before the next notebook cell
        loads another Gemma instance (e.g. USE_TRANSCRIPTION=True).
        """
        self.processor = None
        self.model = None
        try:
            import gc

            import torch

            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except Exception:
            pass

    def release(self) -> None:
        """Public wrapper for explicit notebook-side cleanup."""
        self._free_model()

    def _ensure_model(self):
        if self.processor is not None and self.model is not None:
            return self.processor, self.model
        try:
            from rytmi.transcribe import load_multimodal_model

            proc, mdl = load_multimodal_model()
            self.processor = proc
            self.model = mdl
            return proc, mdl
        except Exception:
            return None, None

    def _windows(self, total_duration: float) -> list[tuple[float, float]]:
        if total_duration <= 0.0:
            return []
        starts: list[tuple[float, float]] = []
        t = 0.0
        while t < total_duration:
            dur = min(self.window_s, total_duration - t)
            if dur <= 0.0:
                break
            starts.append((t, dur))
            t += self.hop_s if self.hop_s > 0 else self.window_s
        return starts

    def _query_window(
        self,
        audio: AudioData,
        processor,
        model,
        start_s: float,
        dur_s: float,
    ) -> float | None:
        """Return 1.0 for YES, 0.0 for NO, None on failure."""
        try:
            import torch

            from rytmi.audio import slice_audio
            from rytmi.llm import _select_input_device
            from rytmi.transcribe import _resample_to

            clip = slice_audio(audio, start_s, dur_s)
            clip_samples = _resample_to(clip.samples, clip.sr, 16_000)

            messages = [{
                "role": "user",
                "content": [
                    {"type": "audio", "audio": clip_samples},
                    {"type": "text", "text": self.prompt},
                ],
            }]
            inputs = processor.apply_chat_template(
                messages,
                add_generation_prompt=True,
                tokenize=True,
                return_tensors="pt",
                return_dict=True,
            )
            device = _select_input_device(model, torch)
            inputs = {
                k: v.to(device) if hasattr(v, "to") else v for k, v in inputs.items()
            }
            input_len = inputs["input_ids"].shape[-1]
            with torch.inference_mode():
                output_ids = model.generate(
                    **inputs, max_new_tokens=4, do_sample=False,
                )
            new_tokens = output_ids[0][input_len:]
            raw = processor.decode(new_tokens, skip_special_tokens=True).strip().lower()
            if raw.startswith("yes"):
                return 1.0
            if raw.startswith("no"):
                return 0.0
            # Unparseable — treat as NO but keep the envelope well-formed.
            return 0.0
        except Exception:
            return None


# --- Gemma speech-vs-singing detector (Phase 11) ---


_GEMMA_SPEECH_WINDOW_S = 5.0
_GEMMA_SPEECH_HOP_S = 5.0
_GEMMA_SPEECH_MAX_DURATION_S = 60.0
_GEMMA_SPEECH_VS_SINGING_PROMPT = (
    "Listen to this short audio clip. "
    "Is the voice in this audio primarily speaking or singing? "
    'Answer with only one word: "YES" if the voice is primarily speaking '
    "(like normal speech, dialog, or narration). "
    '"NO" if the voice is primarily singing (with a clear melody and pitch control). '
    "Do not explain. Answer:"
)


class GemmaSpeechDetector:
    """Window-level speech-vs-singing classifier over the leading seconds.

    Spoken-dialog intros (Propuesta P1–P8 etc.) read as low-energy `intro`
    bands today, which then lure the coaching prompt into describing them as
    a singable opening.  This detector reuses the Gemma 4 E4B multimodal
    pipeline already wired up for `GemmaVocalActivity` to ask a YES/NO
    speech question per 5 s window across the first 60 s of the track, so
    the downstream `_relabel_spoken_intro` pass can split the intro into
    `spoken_intro` + `intro` when the leading phrases are predominantly
    spoken.

    Returns `None` on any failure (model load, runtime, missing audio) so
    callers can no-op the spoken-intro pass without try/except.
    """

    def __init__(
        self,
        *,
        processor=None,
        model=None,
        cache_dir: Path | None = None,
        window_s: float = _GEMMA_SPEECH_WINDOW_S,
        hop_s: float = _GEMMA_SPEECH_HOP_S,
        max_duration_s: float = _GEMMA_SPEECH_MAX_DURATION_S,
        prompt: str = _GEMMA_SPEECH_VS_SINGING_PROMPT,
    ) -> None:
        self.processor = processor
        self.model = model
        self.cache_dir = (
            Path(cache_dir) if cache_dir is not None else _DEFAULT_CACHE_DIR
        )
        self.window_s = window_s
        self.hop_s = hop_s
        self.max_duration_s = max_duration_s
        self.prompt = prompt

    def compute(self, audio: AudioData) -> VocalActivityEnvelope | None:
        key = _cache_key(audio, "gemma-speech")
        cache_path = (
            self.cache_dir / f"{key}.gemma-speech.npz" if key else None
        )
        if cache_path is not None and cache_path.exists():
            cached = _load_cached(cache_path, "gemma-speech")
            if cached is not None:
                return cached

        owned_model = self.processor is None
        processor, model = self._ensure_model()
        if processor is None or model is None:
            return None

        try:
            windows = self._windows(audio.duration)
            if not windows:
                return None
            confidences: list[float] = []
            activities: list[bool] = []
            for start_s, dur_s in windows:
                score = self._query_window(audio, processor, model, start_s, dur_s)
                if score is None:
                    return None
                confidences.append(float(score))
                activities.append(score >= 0.5)

            centres = np.asarray(
                [s + d * 0.5 for s, d in windows], dtype=np.float64,
            )
            env = VocalActivityEnvelope(
                times=centres,
                rms=np.asarray(confidences, dtype=np.float32),
                active=np.asarray(activities, dtype=bool),
                sr=max(1, int(round(1.0 / self.hop_s))) if self.hop_s > 0 else 1,
                source="gemma-speech",
            )
            if cache_path is not None:
                try:
                    _save_cached(cache_path, env)
                except OSError:
                    pass
            return env
        except Exception:
            return None
        finally:
            if owned_model:
                self._free_model()

    def _windows(self, total_duration: float) -> list[tuple[float, float]]:
        """Generate (start, dur) pairs over the leading `max_duration_s`."""
        if total_duration <= 0.0:
            return []
        cap = min(total_duration, self.max_duration_s)
        starts: list[tuple[float, float]] = []
        t = 0.0
        while t < cap:
            dur = min(self.window_s, cap - t)
            if dur <= 0.0:
                break
            starts.append((t, dur))
            t += self.hop_s if self.hop_s > 0 else self.window_s
        return starts

    def _ensure_model(self):
        if self.processor is not None and self.model is not None:
            return self.processor, self.model
        try:
            from rytmi.transcribe import load_multimodal_model

            proc, mdl = load_multimodal_model()
            self.processor = proc
            self.model = mdl
            return proc, mdl
        except Exception:
            return None, None

    def _free_model(self) -> None:
        self.processor = None
        self.model = None
        try:
            import gc

            import torch

            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except Exception:
            pass

    def release(self) -> None:
        self._free_model()

    def _query_window(
        self,
        audio: AudioData,
        processor,
        model,
        start_s: float,
        dur_s: float,
    ) -> float | None:
        """Return 1.0 for YES (speech), 0.0 for NO (singing), None on failure."""
        try:
            import torch

            from rytmi.audio import slice_audio
            from rytmi.llm import _select_input_device
            from rytmi.transcribe import _resample_to

            clip = slice_audio(audio, start_s, dur_s)
            clip_samples = _resample_to(clip.samples, clip.sr, 16_000)

            messages = [{
                "role": "user",
                "content": [
                    {"type": "audio", "audio": clip_samples},
                    {"type": "text", "text": self.prompt},
                ],
            }]
            inputs = processor.apply_chat_template(
                messages,
                add_generation_prompt=True,
                tokenize=True,
                return_tensors="pt",
                return_dict=True,
            )
            device = _select_input_device(model, torch)
            inputs = {
                k: v.to(device) if hasattr(v, "to") else v for k, v in inputs.items()
            }
            input_len = inputs["input_ids"].shape[-1]
            with torch.inference_mode():
                output_ids = model.generate(
                    **inputs, max_new_tokens=4, do_sample=False,
                )
            new_tokens = output_ids[0][input_len:]
            raw = processor.decode(new_tokens, skip_special_tokens=True).strip().lower()
            if raw.startswith("yes"):
                return 1.0
            if raw.startswith("no"):
                return 0.0
            return 0.0
        except Exception:
            return None


# --- default source ---


class _ChainedVocalActivity:
    """Tries a list of sources in order; returns the first non-None envelope."""

    def __init__(self, sources: list[VocalActivitySource]) -> None:
        self._sources = sources

    def compute(self, audio: AudioData) -> VocalActivityEnvelope | None:
        for src in self._sources:
            env = src.compute(audio)
            if env is not None:
                return env
        return None

    def release(self) -> None:
        for src in self._sources:
            release = getattr(src, "release", None)
            if callable(release):
                release()


def default_vocal_activity_source(
    prefer: str = "demucs",
    *,
    cache_dir: Path | None = None,
) -> VocalActivitySource:
    """Return a chained source honouring `prefer` with graceful fallback.

    `prefer="demucs"`: try Demucs first, then Gemma.
    `prefer="gemma"`:  try Gemma first, then Demucs.
    `prefer="none"`:   returns a source that always yields None (pipeline
                       runs with vocal-aware passes disabled).

    Default is ``"demucs"``.  Phase 12b A/B on the 10-track eval set
    (``docs/experiments/19-2026-04-19-phase-12b-vocal-source-ab.md``)
    showed the gemma-first chain regresses label accuracy — before
    flipping the default to ``"gemma"``, fix the windowing-offset /
    polarity bug behind the main ↔ instrumental flips first.
    """
    demucs = DemucsVocalActivity(cache_dir=cache_dir)
    gemma = GemmaVocalActivity(cache_dir=cache_dir)
    if prefer == "gemma":
        return _ChainedVocalActivity([gemma, demucs])
    if prefer == "none":
        return _ChainedVocalActivity([])
    return _ChainedVocalActivity([demucs, gemma])
