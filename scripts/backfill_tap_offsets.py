#!/usr/bin/env python3
"""Backfill ``audio_offset_s`` for tap takes using listening notes.

Existing tap takes were recorded with the convention "start the player,
then tap from beat 1". Their ``tap_times_s`` always start at 0 — i.e.
they're relative to the first tap, not absolute song time. To compare
them against DSP beats we need to know how far into the song the first
tap actually fell.

For each take this script:

  1. Loads the take's listening notes (resolved to song-absolute times
     via ``analyze()``).
  2. Searches for the offset ``S`` that, when added to every tap,
     minimizes the median nearest-note distance for taps falling inside
     the listening-note window.
  3. Reports the chosen ``S``, the residual error, and (with
     ``--write``) updates the take's ``audio_offset_s`` field.

Default is dry-run; pass ``--write`` to actually update the JSON
sidecars. Skip individual tracks with ``--track STEM_SUBSTR`` (repeat).

Example:

    # See what would change for everything in data/eval/taps/
    python scripts/backfill_tap_offsets.py

    # Commit the offsets for one track
    python scripts/backfill_tap_offsets.py --track Criola --write

    # Commit everything once you're happy with the residuals
    python scripts/backfill_tap_offsets.py --write
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rytmi import analyze, load_audio  # noqa: E402
from rytmi.eval.listening_notes import (  # noqa: E402
    load_notes,
    notes_to_times,
)
from rytmi.eval.tap_capture import TapTake, load_takes  # noqa: E402

DEFAULT_NOTES = REPO_ROOT / "data" / "eval" / "kizomba_listening_notes.yaml"
DEFAULT_AUDIO_DIR = REPO_ROOT / "data" / "songs" / "eval_set" / "kizomba"
DEFAULT_TAPS_ROOT = REPO_ROOT / "data" / "eval" / "taps"


def _find_audio(stem: str, audio_dir: Path, taps_root: Path | None = None) -> Path | None:
    """Find an audio file whose stem contains ``stem``.

    When multiple files match (e.g. several remixes of the same song),
    prefer one that has tap takes recorded under ``taps_root`` so we
    don't silently pick a sibling track that has no data to backfill.
    """
    matches = [p for p in sorted(audio_dir.glob("*.mp3")) if stem in p.stem]
    if not matches:
        return None
    if taps_root is not None and len(matches) > 1:
        with_takes = [p for p in matches if (taps_root / p.stem).is_dir()]
        if with_takes:
            return with_takes[0]
    return matches[0]


def _nearest_dist(times: np.ndarray, refs: np.ndarray) -> np.ndarray:
    if times.size == 0 or refs.size == 0:
        return np.array([], dtype=np.float64)
    refs_sorted = np.sort(refs)
    idx = np.searchsorted(refs_sorted, times)
    idx = np.clip(idx, 1, refs_sorted.size - 1)
    left = refs_sorted[idx - 1]
    right = refs_sorted[idx]
    return np.minimum(np.abs(times - left), np.abs(times - right))


def fit_offset(
    taps: np.ndarray,
    notes: np.ndarray,
    search_radius_s: float = 0.4,
    step_s: float = 0.005,
    window_pad_s: float = 0.3,
) -> tuple[float, float, int]:
    """Find the offset that best aligns ``taps`` to ``notes``.

    Returns ``(offset_s, residual_median_ms, n_taps_in_window)``.

    The search is centered on ``S_init = notes[0] - taps[0]`` (the
    naive "first tap == first note" assumption) and scans
    ``[S_init - search_radius_s, S_init + search_radius_s]``. For each
    candidate offset, taps falling inside ``[notes_min - window_pad_s,
    notes_max + window_pad_s]`` are scored against the nearest note;
    the candidate minimizing the **median** nearest-note distance wins.
    Median (not mean) so a few extra/missed taps don't dominate.

    The default radius (0.4 s) is roughly half a kizomba beat at
    ~80 BPM, which keeps the fit from sliding to a neighboring beat
    of the (highly periodic) music. Widen it only if you know the
    user's first tap might be more than half a beat from their first
    listening note.
    """
    if taps.size == 0 or notes.size == 0:
        return 0.0, float("nan"), 0

    notes = np.sort(notes.astype(np.float64))
    taps = np.sort(taps.astype(np.float64))
    s_init = float(notes[0] - taps[0])
    n_steps = int(round(search_radius_s / step_s))
    candidates = s_init + np.arange(-n_steps, n_steps + 1) * step_s

    notes_lo = float(notes[0]) - window_pad_s
    notes_hi = float(notes[-1]) + window_pad_s

    best_s = s_init
    best_score = float("inf")
    best_n = 0
    for s in candidates:
        shifted = taps + s
        in_win = shifted[(shifted >= notes_lo) & (shifted <= notes_hi)]
        if in_win.size < 3:
            continue
        d = _nearest_dist(in_win, notes)
        score = float(np.median(d))
        if score < best_score:
            best_score = score
            best_s = float(s)
            best_n = int(in_win.size)

    return best_s, best_score * 1000.0, best_n


def backfill_take(
    take: TapTake,
    note_times: np.ndarray,
    take_path: Path,
    write: bool,
    search_radius_s: float = 0.4,
) -> dict:
    """Compute and (optionally) write the offset for one take.

    Returns a row dict for the report table.
    """
    taps = np.asarray(take.tap_times_s, dtype=np.float64)
    if taps.size == 0:
        return {
            "take": take.take,
            "n_taps": 0,
            "s_init_s": float("nan"),
            "best_s_s": float("nan"),
            "delta_ms": float("nan"),
            "residual_ms": float("nan"),
            "n_scored": 0,
            "current_offset_s": take.audio_offset_s,
            "status": "skip-empty",
        }

    s_init = float(note_times[0] - taps[0]) if note_times.size else 0.0
    best_s, residual_ms, n_scored = fit_offset(
        taps, note_times, search_radius_s=search_radius_s
    )

    status = "ok"
    if n_scored < 3:
        status = "too-few-taps-in-window"
    elif residual_ms > 80.0:
        status = f"high-residual({residual_ms:.0f}ms)"

    if write and status == "ok":
        take.audio_offset_s = best_s
        take_path.write_text(json.dumps(asdict(take), indent=2))

    return {
        "take": take.take,
        "n_taps": int(taps.size),
        "s_init_s": s_init,
        "best_s_s": best_s,
        "delta_ms": (best_s - s_init) * 1000.0,
        "residual_ms": residual_ms,
        "n_scored": n_scored,
        "current_offset_s": take.audio_offset_s,
        "status": status,
    }


def _print_table(track_label: str, rows: list[dict]) -> None:
    print(f"\n=== {track_label} ===")
    print(
        f"{'take':18s} {'n':>3s} {'init_s':>7s} {'best_s':>7s} "
        f"{'Δms':>7s} {'resid_ms':>8s} {'scored':>6s} {'cur_off':>7s} status"
    )
    print("-" * 80)
    for r in rows:
        print(
            f"{r['take']:18s} {r['n_taps']:3d} {r['s_init_s']:7.3f} "
            f"{r['best_s_s']:7.3f} {r['delta_ms']:+7.0f} "
            f"{r['residual_ms']:8.1f} {r['n_scored']:6d} "
            f"{r['current_offset_s']:7.3f} {r['status']}"
        )


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--notes", type=Path, default=DEFAULT_NOTES)
    p.add_argument("--audio-dir", type=Path, default=DEFAULT_AUDIO_DIR)
    p.add_argument("--taps-root", type=Path, default=DEFAULT_TAPS_ROOT)
    p.add_argument(
        "--track",
        action="append",
        default=None,
        help="Substring of track stem to include (repeatable). "
        "Default: all tracks with both notes and takes.",
    )
    p.add_argument(
        "--write",
        action="store_true",
        help="Write best offset to each take's JSON sidecar (only for "
        "rows with status=ok). Without this flag the script is dry-run.",
    )
    p.add_argument(
        "--max-offset-s",
        type=float,
        default=0.4,
        help="Half-width of the offset search window around s_init "
        "(default 0.4 s ~ half a kizomba beat). Increase only if the "
        "first tap might be more than half a beat from the first "
        "listening note.",
    )
    args = p.parse_args(argv)

    all_notes = load_notes(args.notes)
    if not all_notes:
        print(f"no tracks in {args.notes}", file=sys.stderr)
        return 1

    n_written = 0
    n_flagged = 0
    for tn in all_notes:
        if args.track and not any(t in tn.stem for t in args.track):
            continue
        audio_path = _find_audio(tn.stem, args.audio_dir, args.taps_root)
        if audio_path is None:
            print(f"\n=== {tn.stem} ===\n  <no audio under {args.audio_dir}>")
            continue
        takes = load_takes(audio_path.stem, args.taps_root)
        if not takes:
            continue
        # Resolve listening notes once per track via analyze().
        audio = load_audio(audio_path)
        analysis = analyze(audio, dance_style="kizomba")
        note_times = notes_to_times(list(tn.notes), analysis)
        if note_times.size == 0:
            print(f"\n=== {tn.stem} ===\n  <no listening notes resolved>")
            continue

        rows = []
        take_dir = args.taps_root / audio_path.stem
        for take in takes:
            take_path = take_dir / f"{take.take}.json"
            row = backfill_take(
                take,
                note_times,
                take_path,
                args.write,
                search_radius_s=args.max_offset_s,
            )
            rows.append(row)
            if args.write and row["status"] == "ok":
                n_written += 1
            if row["status"] != "ok":
                n_flagged += 1
        _print_table(audio_path.stem.split(" [")[0], rows)

    print(
        f"\nsummary: {n_written} take(s) written, "
        f"{n_flagged} flagged for review"
        + ("" if args.write else " (DRY RUN — pass --write to commit)")
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
