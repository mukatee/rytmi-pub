"""Spacebar / button-click tap capture for beat ground truth.

Records timestamps (relative to playback start) of every "tap" — either a
spacebar press while a focused button has keyboard focus, or a direct
click on the button — and saves the result as a JSON sidecar next to
the audio under ``data/eval/taps/<audio_stem>/<take>.json``.

The widget here is the only Jupyter-coupled bit; the I/O layer
(:func:`save_take`, :func:`load_take`, :func:`load_takes`) is plain
Python so it can be unit-tested without any frontend.
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path

__all__ = [
    "TapTake",
    "save_take",
    "load_take",
    "load_takes",
    "tap_recorder",
]


@dataclass
class TapTake:
    """One run of tapping along to one audio file.

    Attributes
    ----------
    audio_stem:
        ``Path(audio_path).stem``; used as the directory name under
        ``data/eval/taps/``. Same convention as
        :class:`~rytmi.eval.listening_notes.TrackNotes`.
    take:
        Free-form label, e.g. ``"take_1"`` or ``"calibration"``.
    started_at:
        ISO-8601 timestamp (UTC) of the **first tap** of this take, or
        ``None`` if no taps have been recorded yet. Older sidecars that
        used "recorder armed" semantics still load fine; for those the
        value is whatever was originally written.
    saved_at:
        ISO-8601 timestamp (UTC) of when ``save_take`` was last called
        for this take, or ``None`` for in-memory takes that have never
        been saved. The :func:`save_take` helper sets it automatically.
    tap_times_s:
        Tap times in seconds since the first tap (i.e. since playback
        start, assuming the user starts tapping with the music).
    audio_offset_s:
        Seconds the user nudged playback before tapping (default 0).
        Tap times are stored *relative to the user's first tap*, not to
        the audio file's t=0; ``audio_offset_s`` lets a future caller
        re-align if needed.
    """

    audio_stem: str
    take: str
    started_at: str | None = None
    saved_at: str | None = None
    tap_times_s: list[float] = field(default_factory=list)
    audio_offset_s: float = 0.0


def _take_dir(taps_root: Path, audio_stem: str) -> Path:
    return Path(taps_root) / audio_stem


def save_take(take: TapTake, taps_root: str | Path) -> Path:
    """Write ``take`` as JSON under ``taps_root / audio_stem / <take>.json``.

    Stamps ``saved_at`` to the current UTC time before writing. Returns
    the path written. Creates parent directories as needed.
    """
    take.saved_at = datetime.now(UTC).isoformat(timespec="seconds")
    out_dir = _take_dir(Path(taps_root), take.audio_stem)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{take.take}.json"
    out_path.write_text(json.dumps(asdict(take), indent=2))
    return out_path


def load_take(path: str | Path) -> TapTake:
    """Load one ``TapTake`` from a JSON sidecar."""
    raw = json.loads(Path(path).read_text())
    return TapTake(
        audio_stem=raw["audio_stem"],
        take=raw["take"],
        started_at=raw.get("started_at"),
        saved_at=raw.get("saved_at"),
        tap_times_s=[float(t) for t in raw.get("tap_times_s", [])],
        audio_offset_s=float(raw.get("audio_offset_s", 0.0)),
    )


def load_takes(audio_stem: str, taps_root: str | Path) -> list[TapTake]:
    """Load every take recorded for ``audio_stem``, sorted by filename."""
    out_dir = _take_dir(Path(taps_root), audio_stem)
    if not out_dir.exists():
        return []
    return [load_take(p) for p in sorted(out_dir.glob("*.json"))]


# --- Jupyter-coupled widget --------------------------------------------------


def _next_take_label(taps_root: Path, audio_stem: str, prefix: str = "take") -> str:
    """Return the next free ``<prefix>_N`` label not already on disk.

    Scans ``taps_root/audio_stem/`` for filenames matching ``<prefix>_*.json``
    and returns ``<prefix>_<max+1>`` (or ``<prefix>_1`` if none exist).
    Non-numeric suffixes are ignored.
    """
    out_dir = _take_dir(taps_root, audio_stem)
    if not out_dir.exists():
        return f"{prefix}_1"
    used: list[int] = []
    for p in out_dir.glob(f"{prefix}_*.json"):
        suffix = p.stem[len(prefix) + 1 :]
        try:
            used.append(int(suffix))
        except ValueError:
            continue
    return f"{prefix}_{(max(used) + 1) if used else 1}"


def tap_recorder(
    audio_path: str | Path,
    take: str | None = None,
    taps_root: str | Path = "data/eval/taps",
    autoplay: bool = False,
):
    """Render an audio player + a TAP button + a Save button in a notebook.

    Workflow:
      1. Press Play in the audio widget.
      2. Click the TAP button (or focus it with Tab and hit spacebar) on
         every perceived beat.
      3. Click **Save take** to write the take to JSON. Each save picks
         the next free slot (``take_1``, ``take_2``, …) so re-running
         the same cell — or tapping again after a Reset — never
         overwrites previous takes.
      4. Click **Reset** to clear the in-memory tap buffer and start a
         fresh take in the same cell.

    Pass ``take="my_label"`` to use a custom prefix; the ``_N`` suffix
    is still appended automatically. ``take=None`` (default) uses
    ``"take"``.

    Tap times are stored as seconds since the **first** tap, not since
    audio playback start, because the browser's ``<audio>`` widget
    does not expose its current time to the kernel.

    Returns the in-progress :class:`TapTake` so the cell can ``display``
    or inspect it; tap times are appended live as the user clicks.
    """
    # Imported lazily so the module is importable in headless tests.
    import ipywidgets as widgets
    from IPython.display import Audio, display

    audio_path = Path(audio_path)
    taps_root_path = Path(taps_root)
    prefix = take or "take"
    take_obj = TapTake(
        audio_stem=audio_path.stem,
        take=_next_take_label(taps_root_path, audio_path.stem, prefix),
    )
    state = {"start_perf": None}

    tap_btn = widgets.Button(
        description="TAP (or focus + Space)",
        button_style="primary",
        layout=widgets.Layout(width="220px", height="60px"),
    )
    save_btn = widgets.Button(description="Save take", button_style="success")
    reset_btn = widgets.Button(description="Reset", button_style="warning")
    offset_field = widgets.FloatText(
        value=0.0,
        description="audio_offset_s:",
        step=0.05,
        style={"description_width": "initial"},
        layout=widgets.Layout(width="220px"),
    )
    offset_help = widgets.HTML(
        value=(
            "<small><i>Song-time of your first tap (seconds). "
            "Leave at 0 if you tapped from the very start of the track. "
            "You can also fix this later via "
            "<code>scripts/backfill_tap_offsets.py</code>.</i></small>"
        )
    )
    status = widgets.HTML(
        value=f"<i>0 taps recorded. Next save: <code>{take_obj.take}.json</code>.</i>"
    )

    def _on_tap(_):
        now = time.perf_counter()
        if state["start_perf"] is None:
            state["start_perf"] = now
            take_obj.started_at = datetime.now(UTC).isoformat(timespec="seconds")
            take_obj.tap_times_s.append(0.0)
        else:
            take_obj.tap_times_s.append(now - state["start_perf"])
        n = len(take_obj.tap_times_s)
        last = take_obj.tap_times_s[-1]
        status.value = (
            f"<b>{n}</b> taps recorded. Last at <b>{last:.3f}s</b>. "
            f"Next save: <code>{take_obj.take}.json</code>."
        )

    def _on_save(_):
        if not take_obj.tap_times_s:
            status.value = "<b>Nothing to save</b> — no taps recorded yet."
            return
        # Snapshot the current value of the offset field into the take.
        take_obj.audio_offset_s = float(offset_field.value)
        out = save_take(take_obj, taps_root_path)
        saved_label = take_obj.take
        saved_offset = take_obj.audio_offset_s
        # Roll over to a fresh take so the next batch of taps lands in a
        # new file instead of overwriting the one we just wrote.
        take_obj.tap_times_s.clear()
        state["start_perf"] = None
        take_obj.take = _next_take_label(
            taps_root_path, audio_path.stem, prefix
        )
        take_obj.started_at = None
        take_obj.saved_at = None
        take_obj.audio_offset_s = 0.0
        offset_field.value = 0.0
        status.value = (
            f"Saved <b>{saved_label}</b> to <code>{out}</code> "
            f"(audio_offset_s={saved_offset:.3f}). "
            f"Buffer cleared. Next save: <code>{take_obj.take}.json</code>."
        )

    def _on_reset(_):
        take_obj.tap_times_s.clear()
        state["start_perf"] = None
        # Reset does NOT advance the take counter; the buffer is just
        # discarded and the same slot is still next on save. Drop the
        # started_at so it can't leak into a future take recorded later.
        take_obj.started_at = None
        status.value = (
            f"<i>Reset. 0 taps recorded. Next save: "
            f"<code>{take_obj.take}.json</code>.</i>"
        )

    tap_btn.on_click(_on_tap)
    save_btn.on_click(_on_save)
    reset_btn.on_click(_on_reset)

    display(Audio(filename=str(audio_path), autoplay=autoplay))
    display(widgets.HBox([tap_btn, save_btn, reset_btn]))
    display(widgets.HBox([offset_field, offset_help]))
    display(status)
    return take_obj
