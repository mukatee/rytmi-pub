"""Hand-marked listening notes — perceived step positions for eval tracks.

This module is the single source of truth for converting human-readable
listening-note strings (e.g. ``"M1+3"``) into times on a specific
:class:`~rytmi.types.RhythmAnalysis`. The notation matches the M-labels
drawn above the wave in ``notebooks/06_kizomba_batida_check.ipynb`` and
is documented in :mod:`data/eval/kizomba_listening_notes.yaml`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import yaml
from numpy.typing import NDArray

from rytmi.types import RhythmAnalysis

__all__ = [
    "TrackNotes",
    "load_notes",
    "notes_to_times",
    "find_notes_for_path",
]

_STEP_RE = re.compile(r"^\s*M?(\d+)(?:\+(\d+))?\s*$")


@dataclass(frozen=True)
class TrackNotes:
    """One eval track's listening notes."""

    stem: str  # substring matched against `Path(audio).stem`
    notes: tuple[str, ...]


def load_notes(path: str | Path) -> list[TrackNotes]:
    """Load a YAML listening-notes file into a list of :class:`TrackNotes`."""
    raw = yaml.safe_load(Path(path).read_text())
    out: list[TrackNotes] = []
    for entry in raw.get("tracks", []):
        out.append(TrackNotes(stem=entry["stem"], notes=tuple(entry["notes"])))
    return out


def find_notes_for_path(
    audio_path: str | Path, all_notes: list[TrackNotes]
) -> TrackNotes | None:
    """Return the first :class:`TrackNotes` whose ``stem`` is a substring of
    ``Path(audio_path).stem``, or ``None`` if no match.
    """
    stem = Path(audio_path).stem
    for tn in all_notes:
        if tn.stem in stem:
            return tn
    return None


def notes_to_times(
    notes: list[str] | tuple[str, ...],
    analysis: RhythmAnalysis,
) -> NDArray[np.float64]:
    """Resolve listening-note strings to times on ``analysis``.

    Notation:
        ``"M{m}+{n}"`` — the n-th onset (1-indexed) within measure m
            (M1 == first measure after the first detected downbeat).
        ``"M{m}"``     — same as ``"M{m}+1"``.
        ``"0+{n}"``    — the n-th onset in the partial pre-M1 region.

    Notes that cannot be parsed or that point to missing onsets are
    silently skipped (a printed warning would couple this to the notebook
    UI). Callers that care about miss tracking should compare
    ``len(result)`` to ``len(notes)``.
    """
    onset_times = np.asarray(analysis.onsets.times)
    beat_times = np.asarray(analysis.beats.times)
    db = analysis.downbeats
    downbeat_times = np.asarray(db) if db is not None else np.array([])
    bpm = max(int(analysis.beats_per_measure or 4), 1)
    if downbeat_times.size > 0:
        boundaries = downbeat_times
    elif beat_times.size > 0:
        offset = analysis.downbeat_offset or 0
        boundaries = beat_times[offset::bpm]
    else:
        return np.array([], dtype=np.float64)
    if onset_times.size == 0:
        return np.array([], dtype=np.float64)

    m_idx = np.searchsorted(boundaries, onset_times, side="right") - 1
    lookup: dict[tuple[int, int], float] = {}
    counter: dict[int, int] = {}
    for t, m in zip(onset_times, m_idx, strict=False):
        m_int = int(m)
        counter[m_int] = counter.get(m_int, 0) + 1
        lookup[(m_int, counter[m_int])] = float(t)

    out: list[float] = []
    for note in notes:
        match = _STEP_RE.match(note)
        if not match:
            continue
        # User notation: "M1" = first measure after first downbeat = bucket 0;
        # "0" (no "M") = the partial measure before M1 = bucket -1.
        raw_measure = int(match.group(1))
        prefix_m = note.lstrip().startswith("M")
        bucket = raw_measure - 1 if prefix_m else -1
        n = int(match.group(2)) if match.group(2) else 1
        t = lookup.get((bucket, n))
        if t is not None:
            out.append(t)
    return np.array(out, dtype=np.float64)
