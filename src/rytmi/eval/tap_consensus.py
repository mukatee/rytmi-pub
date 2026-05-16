"""Aggregate multiple tap takes into a single consensus tap track.

Two operations live here:

* :func:`consensus` — fold N takes into one cleaned tap series. A tap is
  kept if at least ``min_agree`` of the takes contain a tap within
  ``agree_window_ms`` of it; the kept time is the mean across the
  agreeing takes. This drops one-off slips and per-take drift.
* :func:`correct_tap_latency` / :func:`estimate_user_latency` — small
  helpers to back out a personal tap latency from a metronome
  calibration take and apply that correction to a real take.

Inputs are plain ``list[float]`` (seconds, monotonically increasing) so
the module is easy to test in isolation from the recorder widget.
"""

from __future__ import annotations

from collections.abc import Sequence
from statistics import median

from rytmi.eval.tap_capture import TapTake

__all__ = [
    "consensus",
    "correct_tap_latency",
    "estimate_user_latency",
]


def _take_times(take: TapTake | Sequence[float]) -> list[float]:
    if isinstance(take, TapTake):
        return list(take.tap_times_s)
    return list(take)


def consensus(
    takes: Sequence[TapTake | Sequence[float]],
    agree_window_ms: float = 80.0,
    min_agree: int = 2,
) -> list[float]:
    """Return one consensus tap track from several takes.

    A reference tap from the longest take is "confirmed" when at least
    ``min_agree`` takes contain a tap within ``agree_window_ms`` of it
    (the reference take itself counts as one). The output time is the
    mean of all agreeing taps. Once a tap from a take is consumed it
    cannot match another reference tap, which keeps the matching
    one-to-one and stable.

    Returns an empty list when fewer than ``min_agree`` takes are
    provided. Output is sorted.
    """
    series = [_take_times(t) for t in takes if _take_times(t)]
    if len(series) < min_agree:
        return []

    window_s = agree_window_ms / 1000.0
    # Use the longest take as the spine; it has the most candidate taps.
    series.sort(key=len, reverse=True)
    reference, others = series[0], series[1:]
    cursors = [0] * len(others)

    out: list[float] = []
    for ref_t in reference:
        agreeing = [ref_t]
        for i, other in enumerate(others):
            j = cursors[i]
            # Advance past taps strictly before the window.
            while j < len(other) and other[j] < ref_t - window_s:
                j += 1
            if j < len(other) and abs(other[j] - ref_t) <= window_s:
                agreeing.append(other[j])
                j += 1  # consume so it cannot match another reference tap
            cursors[i] = j
        if len(agreeing) >= min_agree:
            out.append(sum(agreeing) / len(agreeing))
    return out


def correct_tap_latency(taps: Sequence[float], latency_ms: float) -> list[float]:
    """Subtract a per-user tap latency (ms) from a list of tap times (s)."""
    shift = latency_ms / 1000.0
    return [t - shift for t in taps]


def estimate_user_latency(
    metronome_taps: Sequence[float],
    metronome_grid_s: Sequence[float],
    agree_window_ms: float = 150.0,
) -> float:
    """Estimate the user's tap latency in milliseconds from a calibration take.

    Each tap is matched to its nearest metronome grid point within
    ``agree_window_ms``; the median ``tap - grid`` difference is the
    latency. Median (not mean) so a single missed/extra tap doesn't
    skew the estimate.

    Returns 0.0 if no taps fall within the window.
    """
    if not metronome_taps or not metronome_grid_s:
        return 0.0
    window_s = agree_window_ms / 1000.0
    grid = sorted(metronome_grid_s)
    diffs: list[float] = []
    j = 0
    for tap in sorted(metronome_taps):
        # Advance grid pointer to the nearest candidate.
        while j + 1 < len(grid) and abs(grid[j + 1] - tap) < abs(grid[j] - tap):
            j += 1
        if abs(grid[j] - tap) <= window_s:
            diffs.append(tap - grid[j])
    if not diffs:
        return 0.0
    return median(diffs) * 1000.0
