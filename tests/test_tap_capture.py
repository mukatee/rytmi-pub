"""Tests for ``rytmi.eval.tap_capture`` I/O layer (no widget)."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from rytmi.eval.tap_capture import (
    TapTake,
    _next_take_label,
    load_take,
    load_takes,
    save_take,
)


def _take(stem: str = "song", label: str = "take_1") -> TapTake:
    return TapTake(
        audio_stem=stem,
        take=label,
        started_at=datetime.now(UTC).isoformat(timespec="seconds"),
        tap_times_s=[0.0, 0.62, 1.24, 1.85],
    )


def test_save_then_load_round_trip(tmp_path: Path) -> None:
    take = _take()
    out = save_take(take, tmp_path)
    assert out == tmp_path / "song" / "take_1.json"
    loaded = load_take(out)
    assert loaded.audio_stem == "song"
    assert loaded.take == "take_1"
    assert loaded.tap_times_s == [0.0, 0.62, 1.24, 1.85]
    assert loaded.audio_offset_s == 0.0
    assert loaded.started_at == take.started_at
    # save_take stamps saved_at to current UTC time.
    assert loaded.saved_at is not None
    assert loaded.saved_at == take.saved_at


def test_save_take_stamps_saved_at(tmp_path: Path) -> None:
    take = _take()
    assert take.saved_at is None
    save_take(take, tmp_path)
    assert take.saved_at is not None


def test_taptake_defaults_have_no_timestamps() -> None:
    take = TapTake(audio_stem="x", take="take_1")
    assert take.started_at is None
    assert take.saved_at is None
    assert take.tap_times_s == []


def test_load_take_back_compat_old_schema(tmp_path: Path) -> None:
    # Pre-Phase-28-bugfix sidecars wrote no saved_at and a required
    # started_at. They must still load.
    p = tmp_path / "old.json"
    p.write_text(
        '{"audio_stem": "song", "take": "take_1", '
        '"started_at": "2026-01-01T00:00:00+00:00", '
        '"tap_times_s": [0.0, 0.5]}'
    )
    loaded = load_take(p)
    assert loaded.started_at == "2026-01-01T00:00:00+00:00"
    assert loaded.saved_at is None
    assert loaded.tap_times_s == [0.0, 0.5]


def test_save_take_handles_empty_taps(tmp_path: Path) -> None:
    take = _take()
    take.tap_times_s = []
    out = save_take(take, tmp_path)
    loaded = load_take(out)
    assert loaded.tap_times_s == []


def test_load_takes_returns_sorted(tmp_path: Path) -> None:
    save_take(_take(label="take_2"), tmp_path)
    save_take(_take(label="take_1"), tmp_path)
    save_take(_take(label="take_3"), tmp_path)
    takes = load_takes("song", tmp_path)
    assert [t.take for t in takes] == ["take_1", "take_2", "take_3"]


def test_load_takes_missing_dir_returns_empty(tmp_path: Path) -> None:
    assert load_takes("nope", tmp_path) == []


def test_save_take_overwrites_same_label(tmp_path: Path) -> None:
    save_take(_take(), tmp_path)
    take2 = _take()
    take2.tap_times_s = [10.0]
    save_take(take2, tmp_path)
    takes = load_takes("song", tmp_path)
    assert len(takes) == 1
    assert takes[0].tap_times_s == [10.0]


def test_load_take_rejects_garbage(tmp_path: Path) -> None:
    bad = tmp_path / "x.json"
    bad.write_text("{}")
    with pytest.raises(KeyError):
        load_take(bad)  # missing required 'audio_stem' / 'take'


def test_next_take_label_starts_at_one(tmp_path: Path) -> None:
    assert _next_take_label(tmp_path, "song") == "take_1"


def test_next_take_label_increments_past_existing(tmp_path: Path) -> None:
    save_take(_take(label="take_1"), tmp_path)
    save_take(_take(label="take_2"), tmp_path)
    assert _next_take_label(tmp_path, "song") == "take_3"


def test_next_take_label_ignores_non_numeric_suffix(tmp_path: Path) -> None:
    save_take(_take(label="take_calibration"), tmp_path)
    save_take(_take(label="take_1"), tmp_path)
    assert _next_take_label(tmp_path, "song") == "take_2"


def test_next_take_label_respects_custom_prefix(tmp_path: Path) -> None:
    save_take(_take(label="calib_1"), tmp_path)
    assert _next_take_label(tmp_path, "song", prefix="calib") == "calib_2"
    assert _next_take_label(tmp_path, "song", prefix="take") == "take_1"
