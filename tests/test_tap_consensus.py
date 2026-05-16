"""Tests for ``rytmi.eval.tap_consensus``."""

from __future__ import annotations

import pytest

from rytmi.eval.tap_capture import TapTake
from rytmi.eval.tap_consensus import (
    consensus,
    correct_tap_latency,
    estimate_user_latency,
)


def _take(times: list[float], label: str = "t") -> TapTake:
    return TapTake(audio_stem="x", take=label, started_at="2026-01-01T00:00:00+00:00",
                   tap_times_s=times)


def test_consensus_recovers_clean_grid_within_window() -> None:
    grid = [i * 0.6 for i in range(8)]
    take_a = [t + 0.020 for t in grid]
    take_b = [t - 0.015 for t in grid]
    take_c = [t + 0.005 for t in grid]
    out = consensus([_take(take_a), _take(take_b), _take(take_c)],
                    agree_window_ms=80, min_agree=2)
    assert len(out) == len(grid)
    for got, want in zip(out, grid, strict=True):
        assert abs(got - want) < 0.015  # within mean-of-three of the truth


def test_consensus_drops_isolated_outliers() -> None:
    grid = [0.0, 0.6, 1.2, 1.8]
    bad_extra = [0.0, 0.3, 0.6, 1.2, 1.8]  # phantom tap at 0.3 only in this take
    out = consensus([_take(grid), _take(bad_extra), _take(grid)],
                    agree_window_ms=60, min_agree=2)
    assert len(out) == 4
    assert all(abs(o - g) < 0.05 for o, g in zip(out, grid, strict=True))


def test_consensus_too_few_takes_returns_empty() -> None:
    assert consensus([_take([0.0, 0.5])], min_agree=2) == []


def test_consensus_accepts_plain_lists() -> None:
    grid = [0.0, 0.5, 1.0]
    out = consensus([grid, grid, grid], min_agree=2)
    assert out == grid


def test_correct_tap_latency_subtracts_shift() -> None:
    assert correct_tap_latency([1.0, 2.0], latency_ms=120) == pytest.approx([0.88, 1.88])


def test_estimate_user_latency_recovers_known_offset() -> None:
    grid = [i * 0.6 for i in range(20)]  # 100 BPM
    latency_ms = 75.0
    taps = [g + latency_ms / 1000.0 for g in grid]
    est = estimate_user_latency(taps, grid)
    assert abs(est - latency_ms) < 5.0


def test_estimate_user_latency_handles_empty() -> None:
    assert estimate_user_latency([], [0.0, 0.6]) == 0.0
    assert estimate_user_latency([0.0], []) == 0.0


def test_estimate_then_correct_round_trip() -> None:
    grid = [i * 0.5 for i in range(10)]
    latency_ms = 60.0
    taps = [g + latency_ms / 1000.0 + (0.005 if i % 2 else -0.005)
            for i, g in enumerate(grid)]
    est = estimate_user_latency(taps, grid)
    corrected = correct_tap_latency(taps, est)
    for c, g in zip(corrected, grid, strict=True):
        assert abs(c - g) < 0.010
