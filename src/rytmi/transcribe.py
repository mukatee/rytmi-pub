"""Gemma 4 audio perception pass for rhythm learning.

This module is the **perception stage** of the two-stage pipeline:

- Perception (this module): one local multimodal Gemma 4 call per track.
  Detects the vocal language (and optionally a short lyric snippet) on a
  heuristically-selected clip.  Output is a small ``VocalsInfo`` record.
- Reasoning (``rytmi.llm``): many text-only Ollama calls per track consuming
  the perception output as an optional ``{vocals_section}`` in the prompt.

The split exists because Ollama's OpenAI-compatible API does NOT support
audio input, so the audio path has to go through local Hugging Face loading
with ``Gemma4ForConditionalGeneration`` + ``Gemma4Processor``.  Running both
models on the same GPU at once is not viable on a laptop, so the notebook
calls ``transcribe_vocals()`` once per track in a dedicated pass, then frees
the multimodal model before switching to the Ollama reasoning stage.

Transformers is imported lazily inside the loader and transcribe functions
so that ``import rytmi.transcribe`` stays free for tests that mock the model.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

import numpy as np

from rytmi.audio import slice_audio
from rytmi.types import AudioData, RhythmAnalysis, VocalsInfo

__all__ = [
    "VocalsInfo",
    "load_multimodal_model",
    "select_vocal_clip",
    "transcribe_vocals",
]


# Target sample rate Gemma 4's audio front-end expects.
_AUDIO_SR = 16_000

_LANGUAGE_PROMPT = (
    "Listen to this audio clip. What language are the vocals sung in? "
    "Answer with one word: the language name in English "
    "(e.g. Spanish, Portuguese, French, English, Kriol). "
    "If there are no vocals, say 'instrumental'. If you are unsure, say 'unknown'."
)

_LYRICS_PROMPT = (
    "Listen to this audio clip. Output exactly two lines.\n"
    "Line 1: the language of the vocals in one word "
    "(English name, or 'instrumental', or 'unknown').\n"
    "Line 2: up to 12 words of lyrics you can clearly hear, "
    "or leave it blank if none."
)


def load_multimodal_model(
    model_id: str | None = None,
    device_map: str = "auto",
):
    """Load the Gemma 4 multimodal model + processor for audio input.

    Parallels ``rytmi.llm.load_model`` but imports the multimodal classes
    directly.  There is **no silent fallback** to ``AutoTokenizer`` — if the
    processor fails to load, that would silently disable audio and cause
    confusing "audio was ignored" bugs downstream, so we raise instead.

    Args:
        model_id: Explicit HF model ID.  Defaults to ``google/gemma-4-E4B-it``
            because E2B's audio stack is weaker.
        device_map: Passed through to ``from_pretrained``.

    Returns:
        ``(processor, model)`` tuple suitable for ``transcribe_vocals``.
    """
    try:
        from transformers import (
            Gemma4ForConditionalGeneration,
            Gemma4Processor,
        )
    except ImportError as exc:
        raise RuntimeError(
            "transformers does not expose Gemma4ForConditionalGeneration / "
            "Gemma4Processor. Install a transformers version with Gemma 4 "
            "multimodal support (pip install rytmi[llm] with a recent "
            "transformers)."
        ) from exc

    if model_id is None:
        model_id = "google/gemma-4-E4B-it"

    print(f"Loading multimodal {model_id}  (device_map={device_map})")

    processor = Gemma4Processor.from_pretrained(model_id)
    model = Gemma4ForConditionalGeneration.from_pretrained(
        model_id,
        device_map=device_map,
        torch_dtype="auto",
    )
    model.eval()
    return processor, model


def select_vocal_clip(
    analysis: RhythmAnalysis,
    target_duration_s: float = 20.0,
    skip_intro_frac: float = 0.15,
    max_duration_s: float = 28.0,
) -> tuple[float, float]:
    """Pick the ``(start_s, duration_s)`` window most likely to contain vocals.

    Heuristic: convolve the onset-strength envelope with a rectangular window
    of ``target_duration_s`` and pick the argmax starting after
    ``skip_intro_frac * total_duration``.  This biases toward the densest
    middle region of the track — usually a chorus — without needing vocal
    separation or song-structure detection.

    Deterministic, pure numpy.  Clamped to the track end and to
    ``max_duration_s`` (which must stay under Gemma's ~30 s audio window).
    """
    total_duration = float(analysis.audio.duration)
    duration = float(min(target_duration_s, max_duration_s, max(total_duration, 0.0)))

    if duration <= 0.0 or total_duration <= 0.0:
        return 0.0, 0.0

    if total_duration <= duration:
        return 0.0, total_duration

    onset_times = np.asarray(analysis.onsets.times, dtype=np.float64)
    onset_strength = np.asarray(analysis.onsets.strength, dtype=np.float64)

    # Resample onset strength onto a uniform 0.1 s grid so the window size is
    # measured in grid steps, not frames.  Falls back to the raw strength array
    # when the onsets record is missing/empty.
    step_s = 0.1
    n_steps = max(1, int(round(total_duration / step_s)))
    grid = np.linspace(0.0, total_duration, n_steps, endpoint=False)
    if onset_strength.size > 0 and onset_times.size == onset_strength.size:
        # strength stored per onset event — spread across the grid by nearest.
        strength_grid = np.zeros(n_steps, dtype=np.float64)
        idx = np.clip((onset_times / step_s).astype(int), 0, n_steps - 1)
        np.add.at(strength_grid, idx, onset_strength)
    elif onset_strength.size > 0:
        # strength stored as a per-frame envelope — resample onto our grid.
        src_grid = np.linspace(0.0, total_duration, onset_strength.size, endpoint=False)
        strength_grid = np.interp(grid, src_grid, onset_strength)
    else:
        strength_grid = np.ones(n_steps, dtype=np.float64)

    window_steps = max(1, int(round(duration / step_s)))
    cumsum = np.cumsum(np.concatenate(([0.0], strength_grid)))
    window_sum = cumsum[window_steps:] - cumsum[:-window_steps]

    skip_steps = int(round(skip_intro_frac * n_steps))
    # Latest valid start step so that start + window fits in the track.
    latest_start = len(window_sum) - 1
    if skip_steps >= len(window_sum):
        skip_steps = max(0, latest_start)

    best_rel = int(np.argmax(window_sum[skip_steps:]))
    best_step = skip_steps + best_rel
    start_s = float(best_step * step_s)
    if start_s + duration > total_duration:
        start_s = max(0.0, total_duration - duration)
    return start_s, duration


def transcribe_vocals(
    audio: AudioData,
    analysis: RhythmAnalysis,
    processor,
    model,
    *,
    mode: str = "language_only",
    max_new_tokens_language: int = 8,
    max_new_tokens_lyrics: int = 64,
    max_retries: int = 3,
) -> VocalsInfo:
    """Run Gemma 4 audio calls on clips chosen by ``select_vocal_clip``.

    If the first clip yields ``"instrumental"`` or ``"unknown"``, retries with
    clips from later in the track (40% and 60% into the track).  Returns the
    first result with a recognized language, or the last result if all retries
    fail.

    Args:
        audio: Full-track audio.  A ~20 s sub-clip is extracted for the call.
        analysis: DSP analysis for the same track — used to find the clip.
        processor: ``Gemma4Processor`` returned from ``load_multimodal_model``.
        model: ``Gemma4ForConditionalGeneration``.
        mode: ``"language_only"`` (default) or ``"lyrics"``.  Language-only is
            cheaper and less prone to hallucination on instrumental sections.
        max_retries: Maximum number of clip positions to try (default 3).

    Returns:
        ``VocalsInfo`` — never raises on a bad model response; parse failures
        come back as ``language="unknown"`` with the raw text preserved.
    """
    skip_fracs = [0.15, 0.40, 0.60]
    retries = min(max_retries, len(skip_fracs))

    result: VocalsInfo | None = None
    for attempt in range(retries):
        start_s, duration_s = select_vocal_clip(
            analysis, skip_intro_frac=skip_fracs[attempt],
        )
        result = _transcribe_clip(
            audio, start_s, duration_s, processor, model, mode,
            max_new_tokens_language, max_new_tokens_lyrics,
        )
        if result.language not in {"instrumental", "unknown"}:
            return result
        if attempt > 0:
            print(f"  retry {attempt}: {result.language} @ {start_s:.1f}s")

    # All retries exhausted — return the last result (status quo behavior).
    assert result is not None
    return result


def _transcribe_clip(
    audio: AudioData,
    start_s: float,
    duration_s: float,
    processor,
    model,
    mode: str,
    max_new_tokens_language: int,
    max_new_tokens_lyrics: int,
) -> VocalsInfo:
    """Run a single Gemma 4 audio call on the given clip window."""
    import torch  # lazy so tests that mock the model don't need torch

    from rytmi.llm import _select_input_device

    clip = slice_audio(audio, start_s, duration_s)
    clip_samples = _resample_to(clip.samples, clip.sr, _AUDIO_SR)

    if mode == "lyrics":
        prompt_text = _LYRICS_PROMPT
        max_new_tokens = max_new_tokens_lyrics
    else:
        prompt_text = _LANGUAGE_PROMPT
        max_new_tokens = max_new_tokens_language

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "audio", "audio": clip_samples},
                {"type": "text", "text": prompt_text},
            ],
        }
    ]

    inputs = processor.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_tensors="pt",
        return_dict=True,
    )
    input_device = _select_input_device(model, torch)
    inputs = {
        k: v.to(input_device) if hasattr(v, "to") else v
        for k, v in inputs.items()
    }
    input_len = inputs["input_ids"].shape[-1]

    with torch.inference_mode():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
        )

    new_tokens = output_ids[0][input_len:]
    raw_response = processor.decode(new_tokens, skip_special_tokens=True).strip()

    language, lyric_snippet = _parse_response(raw_response, mode)
    return VocalsInfo(
        language=language,
        lyric_snippet=lyric_snippet,
        clip_start_s=start_s,
        clip_duration_s=duration_s,
        raw_response=raw_response,
    )


def _resample_to(samples: np.ndarray, src_sr: int, target_sr: int) -> np.ndarray:
    """Resample to ``target_sr`` if needed.  Uses librosa if available."""
    if src_sr == target_sr:
        return np.asarray(samples, dtype=np.float32)
    import librosa

    resampled = librosa.resample(
        np.asarray(samples, dtype=np.float32),
        orig_sr=src_sr,
        target_sr=target_sr,
    )
    return resampled


_KNOWN_LANGUAGES = {
    "spanish",
    "portuguese",
    "english",
    "french",
    "italian",
    "german",
    "kriol",
    "creole",
    "cape verdean creole",
    "cape verdean",
    "catalan",
    "instrumental",
    "unknown",
}


def _parse_response(raw: str, mode: str) -> tuple[str, str]:
    """Extract a (language, lyric_snippet) pair from a raw Gemma response.

    Never raises.  Unknown or unparseable responses map to ``("unknown", "")``.
    """
    text = (raw or "").strip()
    if not text:
        return "unknown", ""

    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        return "unknown", ""

    first = lines[0]
    # Strip surrounding punctuation / formatting and pull out the first word.
    first_clean = re.sub(r"[^\w\s-]", "", first).strip().lower()
    if not first_clean:
        return "unknown", ""

    # Try a multi-word match first (e.g. "cape verdean creole"), then single word.
    language = "unknown"
    if first_clean in _KNOWN_LANGUAGES:
        language = first_clean
    else:
        for known in sorted(_KNOWN_LANGUAGES, key=len, reverse=True):
            if known in first_clean:
                language = known
                break
        else:
            first_word = first_clean.split()[0]
            if first_word in _KNOWN_LANGUAGES:
                language = first_word

    # Normalize aliases — kizomba-adjacent creoles collapse to "kriol" so the
    # prompt's language→style hint has a single vocabulary.
    if language in {"creole", "cape verdean", "cape verdean creole"}:
        language = "kriol"

    # Refuse hedge responses.
    if any(p in first.lower() for p in ("cannot", "can't", "no audio", "don't know")):
        return "unknown", ""

    lyric_snippet = ""
    if mode == "lyrics" and len(lines) >= 2:
        lyric_snippet = lines[1][:160]

    return language, lyric_snippet
