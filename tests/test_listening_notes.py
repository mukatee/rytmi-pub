"""Tests for `rytmi.eval.listening_notes`."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from rytmi.eval.listening_notes import (
    find_notes_for_path,
    load_notes,
    notes_to_times,
)
from rytmi.types import AudioData, BeatData, OnsetData, RhythmAnalysis


def _make_analysis(
    onset_times: list[float],
    *,
    downbeat_times: list[float] | None = None,
    beat_times: list[float] | None = None,
    bpm: int = 4,
    downbeat_offset: int | None = None,
) -> RhythmAnalysis:
    """Build a minimal `RhythmAnalysis` for parser tests.

    Only the fields the parser actually reads are populated; other fields
    keep their dataclass defaults.
    """
    onsets = OnsetData(
        times=np.asarray(onset_times, dtype=np.float64),
        strength=np.ones(len(onset_times), dtype=np.float64),
        sr=22050,
    )
    beats = BeatData(
        times=np.asarray(beat_times or [], dtype=np.float64),
        tempo=120.0,
        beat_frames=np.zeros(len(beat_times or []), dtype=np.intp),
    )
    audio = AudioData(samples=np.zeros(1, dtype=np.float32), sr=22050, duration=0.0)
    return RhythmAnalysis(
        audio=audio,
        onsets=onsets,
        beats=beats,
        tempo=120.0,
        downbeats=np.asarray(downbeat_times, dtype=np.float64)
        if downbeat_times is not None
        else None,
        beats_per_measure=bpm,
        downbeat_offset=downbeat_offset,
    )


def test_notes_to_times_resolves_basic_M_notation():
    # Two measures starting at 1.0 and 2.0; onsets every 0.25 s.
    onsets = [0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.25]
    a = _make_analysis(onsets, downbeat_times=[1.0, 2.0])
    # Bucket -1 (before M1): 0.5, 0.75 -> 0+1, 0+2
    # Bucket 0 (M1): 1.0, 1.25, 1.5, 1.75 -> M1+1..M1+4
    # Bucket 1 (M2): 2.0, 2.25 -> M2+1, M2+2
    times = notes_to_times(["0+1", "0+2", "M1", "M1+3", "M2+2"], a)
    np.testing.assert_allclose(times, [0.5, 0.75, 1.0, 1.5, 2.25])


def test_notes_to_times_uses_beat_grid_when_no_downbeats():
    # Beats at 0.25 spacing, downbeat_offset=0, bpm=4: measures at idx 0, 4, 8...
    beats = list(np.arange(0.0, 2.5, 0.25))  # 0.0, 0.25, ..., 2.25
    onsets = [1.05, 1.55, 2.05]  # one per "measure" boundary
    a = _make_analysis(
        onsets,
        downbeat_times=None,
        beat_times=beats,
        downbeat_offset=0,
        bpm=4,
    )
    # Boundaries from beats[0::4] = 0.0, 1.0, 2.0
    # 1.05 -> bucket 1 (M2+1), 1.55 -> bucket 1 (M2+2), 2.05 -> bucket 2 (M3+1)
    times = notes_to_times(["M2", "M2+2", "M3"], a)
    np.testing.assert_allclose(times, [1.05, 1.55, 2.05])


def test_notes_to_times_skips_unparseable_and_missing():
    a = _make_analysis([0.5, 1.1], downbeat_times=[1.0])
    # "junk" unparseable; "M9+9" out of range; "M1" valid -> 1.1
    times = notes_to_times(["junk", "M9+9", "M1"], a)
    np.testing.assert_allclose(times, [1.1])


def test_notes_to_times_empty_inputs_safe():
    a = _make_analysis([], downbeat_times=[1.0])
    assert notes_to_times(["M1"], a).size == 0
    a2 = _make_analysis([0.5], downbeat_times=[])
    # No boundaries at all -> empty result
    assert notes_to_times(["M1"], a2).size == 0


def test_load_notes_and_find_by_substring(tmp_path: Path):
    p = tmp_path / "notes.yaml"
    p.write_text(
        "tracks:\n"
        "  - stem: Baila_Kizomba\n"
        "    notes: ['M1', 'M1+2']\n"
        "  - stem: Teu_Toque\n"
        "    notes: ['M2']\n"
    )
    all_notes = load_notes(p)
    assert len(all_notes) == 2
    assert all_notes[0].stem == "Baila_Kizomba"
    assert all_notes[0].notes == ("M1", "M1+2")

    hit = find_notes_for_path(
        "/some/dir/Baila_Kizomba_Amor [XG11YxMWgaI].mp3", all_notes
    )
    assert hit is not None and hit.stem == "Baila_Kizomba"
    assert find_notes_for_path("nope.mp3", all_notes) is None


def test_repo_yaml_loads_and_has_known_tracks():
    """The committed YAML should keep loading and contain both eval tracks."""
    repo_root = Path(__file__).resolve().parents[1]
    yaml_path = repo_root / "data" / "eval" / "kizomba_listening_notes.yaml"
    if not yaml_path.exists():
        pytest.skip("kizomba listening-notes YAML not present")
    notes = load_notes(yaml_path)
    stems = {tn.stem for tn in notes}
    assert "Baila_Kizomba" in stems
    assert "Teu_Toque" in stems
