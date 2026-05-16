"""Gemma 4 audio tiebreaker for ambiguous downbeat estimates.

Phase 13 Commit B2 — companion to the DSP fusion in `rytmi.dsp.detect_downbeats`.

When the DSP fusion is in the ambiguous band (default `[0.0, 0.25)`) the
phrase grid defaults to `beat[0]`, drifting P/M numbering across the
analysis.  This module asks Gemma 4 (E4B) a per-candidate-offset yes/no
question — "does this clip start on a measure-1?" — and combines its votes
with the original DSP estimate.

The function is a no-op (returns the input unchanged) when:
- the Gemma model is unavailable / fails,
- DSP confidence is outside the ambiguity band,
- there are not enough beats to form 4 distinct candidate clips.

Design notes
------------
- Gemma E4B's audio front-end is primarily speech-oriented (per CLAUDE.md);
  we ask in lay terms ("strong musical beat / start of a measure") and
  accept that some queries will misfire.  The tiebreaker is fail-soft.
- Per-candidate-offset clips share length but start at the first beat with
  that offset.  Default 8-beat (~2 measures at 120 BPM) clips give Gemma
  enough audio to hear the downbeat without exceeding its ~30 s window.
- Combination logic is interpretable rather than probabilistic: when Gemma
  agrees with DSP we endorse DSP and bump confidence; when Gemma points to
  a single different offset we switch and use a fixed modest confidence;
  when Gemma is ambiguous we leave DSP untouched.  Reduces over-confidence
  on a small-model audio judgment.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from rytmi.types import AudioData, BeatData

__all__ = [
    "DownbeatTiebreakResult",
    "refine_downbeats_via_gemma",
]


_AUDIO_SR = 16_000
_DOWNBEAT_PROMPT = (
    "Listen to this short music clip. "
    "Does this clip START on a strong musical beat that sounds like "
    "the BEGINNING of a measure or musical phrase "
    "(the \"1\" in \"1-2-3-4\")? "
    "Answer with one word: YES or NO."
)

# Phase 14 Option 3 — permissive prompt variant.  No all-caps anchoring,
# no numeric "1-2-3-4".  Designed to reduce NO-bias from the original
# over-constrained wording.
_PROMPT_VARIANT: str | None = None  # Set to "v2" to activate.
_PROMPT_V2 = (
    "Listen to this short music clip. Does it sound like it begins "
    "right at the start of a musical phrase? If yes, say yes. If it "
    "sounds like it starts in the middle of a phrase, say no."
)

# Phase 14 Option 3 — fractional clip start position.  0.0 = first eligible
# beat (default behaviour), 0.5 = start from ~50% into the track.
_CLIP_START_FRACTION: float = 0.0

# Confidence band where the tiebreaker is allowed to fire.  Above max we
# already trust DSP; below min the DSP signals are essentially noise and
# Gemma's vote alone shouldn't carry the decision.
_DEFAULT_MIN_CONF = 0.0
_DEFAULT_MAX_CONF = 0.25
_DEFAULT_CLIP_BEATS = 8

# Confidence bumps applied after a successful tiebreak.  Modest values
# because Gemma E4B is small and music-judgment is not its strength.
_CONFIDENCE_ON_AGREE = 0.30
_CONFIDENCE_ON_SWITCH = 0.30


@dataclass
class DownbeatTiebreakResult:
    """Refined downbeat decision plus the per-offset Gemma votes for diagnostics."""

    downbeat_times: np.ndarray
    beats_per_measure: int
    confidence: float
    best_offset: int
    gemma_votes: np.ndarray  # per-offset, 1.0 for YES / 0.0 for NO / nan on failure
    fired: bool  # True when refinement actually ran (vs. no-op)


def refine_downbeats_via_gemma(
    audio: AudioData,
    beats: BeatData,
    processor,
    model,
    *,
    dsp_offset: int,
    dsp_confidence: float,
    beats_per_measure: int = 4,
    clip_beats: int = _DEFAULT_CLIP_BEATS,
    min_dsp_conf: float = _DEFAULT_MIN_CONF,
    max_dsp_conf: float = _DEFAULT_MAX_CONF,
) -> DownbeatTiebreakResult:
    """Refine an ambiguous DSP downbeat estimate using a Gemma E4B yes/no vote.

    Args:
        audio: Full-track audio.
        beats: Beat grid from `track_beats(audio)`.
        processor / model: Gemma 4 multimodal pair from
            `rytmi.transcribe.load_multimodal_model`.  May be `None` —
            then the function no-ops and returns the input unchanged.
        dsp_offset / dsp_confidence: Result from `detect_downbeats()`.
        beats_per_measure: 4 for all current Latin styles.
        clip_beats: How many beats per candidate clip.  8 ≈ 2 measures at
            120 BPM, comfortably within Gemma's 30-s audio window.
        min_dsp_conf / max_dsp_conf: Ambiguity band.  Outside this band
            the function no-ops.

    Returns:
        A `DownbeatTiebreakResult` carrying refined `(times, bpm, confidence,
        offset)` plus per-offset Gemma votes for the experiment note.
    """
    no_op = DownbeatTiebreakResult(
        downbeat_times=beats.times[dsp_offset::beats_per_measure],
        beats_per_measure=beats_per_measure,
        confidence=dsp_confidence,
        best_offset=dsp_offset,
        gemma_votes=np.full(beats_per_measure, np.nan),
        fired=False,
    )

    if processor is None or model is None:
        return no_op
    if not (min_dsp_conf <= dsp_confidence < max_dsp_conf):
        return no_op
    if len(beats.times) < beats_per_measure + clip_beats:
        return no_op

    votes = np.zeros(beats_per_measure, dtype=np.float32)
    any_failure = False
    for offset in range(beats_per_measure):
        clip_window = _candidate_clip_window(
            beats, offset, clip_beats, beats_per_measure,
            start_fraction=_CLIP_START_FRACTION,
        )
        if clip_window is None:
            any_failure = True
            votes[offset] = np.nan
            continue
        start_s, dur_s = clip_window
        vote = _query_gemma_downbeat(audio, processor, model, start_s, dur_s)
        if vote is None:
            any_failure = True
            votes[offset] = np.nan
        else:
            votes[offset] = vote

    if any_failure:
        # If any clip query failed, don't synthesize a decision from a partial
        # vote vector — that would mix Gemma evidence with default-zeros for
        # the failed offsets and bias toward whichever offsets *did* run.
        return DownbeatTiebreakResult(
            downbeat_times=no_op.downbeat_times,
            beats_per_measure=no_op.beats_per_measure,
            confidence=no_op.confidence,
            best_offset=no_op.best_offset,
            gemma_votes=votes,
            fired=False,
        )

    yes_offsets = np.where(votes >= 0.5)[0]
    if len(yes_offsets) == 0:
        # All NO — Gemma sees no measure-start in any candidate.  No info.
        new_offset, new_conf = dsp_offset, dsp_confidence
    elif len(yes_offsets) == 1:
        winner = int(yes_offsets[0])
        if winner == dsp_offset:
            new_offset = dsp_offset
            new_conf = max(_CONFIDENCE_ON_AGREE, dsp_confidence)
        else:
            new_offset = winner
            new_conf = _CONFIDENCE_ON_SWITCH
    else:
        # Multiple YES — Gemma can't disambiguate.  If DSP's pick is among
        # them, endorse DSP; otherwise leave DSP untouched.
        if dsp_offset in yes_offsets.tolist():
            new_offset = dsp_offset
            new_conf = max(_CONFIDENCE_ON_AGREE, dsp_confidence)
        else:
            new_offset, new_conf = dsp_offset, dsp_confidence

    return DownbeatTiebreakResult(
        downbeat_times=beats.times[new_offset::beats_per_measure],
        beats_per_measure=beats_per_measure,
        confidence=float(new_conf),
        best_offset=int(new_offset),
        gemma_votes=votes,
        fired=True,
    )


def _candidate_clip_window(
    beats: BeatData,
    offset: int,
    clip_beats: int,
    beats_per_measure: int,
    *,
    start_fraction: float = 0.0,
) -> tuple[float, float] | None:
    """Find the first beat at *offset* such that *clip_beats* beats fit after it.

    Returns ``(start_s, duration_s)`` or ``None`` if there's no fit.  Picks
    the *first* eligible window so all four candidates start near the same
    region of the song — keeping Gemma's judgments comparable.

    When ``start_fraction > 0``, skip beats before that fractional position
    along the track (Phase 14 Option 3 — avoids intro regions that lack
    rhythmic density).
    """
    times = np.asarray(beats.times, dtype=np.float64)
    if len(times) < beats_per_measure + clip_beats:
        return None
    # Determine the earliest beat index to consider.
    min_idx = 0
    if start_fraction > 0.0:
        min_idx = int(len(times) * float(np.clip(start_fraction, 0.0, 0.9)))
    # Smallest index whose offset matches and where clip_beats more beats fit.
    for i in range(offset, len(times) - clip_beats, beats_per_measure):
        if i < min_idx:
            continue
        start_s = float(times[i])
        end_s = float(times[i + clip_beats])
        dur_s = end_s - start_s
        if dur_s > 0:
            return start_s, dur_s
    return None


def _query_gemma_downbeat(
    audio: AudioData,
    processor,
    model,
    start_s: float,
    dur_s: float,
    *,
    prompt: str | None = None,
) -> float | None:
    """Return 1.0 (YES) / 0.0 (NO) / None (failure) for one candidate clip."""
    if prompt is None:
        prompt = _PROMPT_V2 if _PROMPT_VARIANT == "v2" else _DOWNBEAT_PROMPT
    try:
        import torch

        from rytmi.audio import slice_audio
        from rytmi.llm import _select_input_device
        from rytmi.transcribe import _resample_to

        clip = slice_audio(audio, start_s, dur_s)
        clip_samples = _resample_to(clip.samples, clip.sr, _AUDIO_SR)

        messages = [{
            "role": "user",
            "content": [
                {"type": "audio", "audio": clip_samples},
                {"type": "text", "text": prompt},
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
        return None
    except Exception:
        return None
