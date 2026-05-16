"""Disk cache for `(audio, analysis)` pairs from `prepare_analysis`.

Keyed on (absolute path, mtime, size, dance_style, cache version). The
expensive parts — Demucs vocal separation + the full `analyze()` pass
(HPSS, beats, sections, vocal demote, etc.) — get pickled to
``data/_analysis_cache/`` so reruns and tuning iterations skip the
~5–8 minute Demucs pass entirely.

Falls back gracefully if pickling fails (e.g. an analysis object grows
non-picklable internals later); the caller will simply recompute.
"""

from __future__ import annotations

import hashlib
import pickle
from pathlib import Path

# Bump if the analysis schema changes in a way that should invalidate
# all existing caches (new field on RhythmAnalysis, etc.).
CACHE_VERSION = "v1"

_ROOT = Path(__file__).resolve().parents[2]
CACHE_DIR = _ROOT / "data" / "_analysis_cache"


def _key(song_path: Path, dance_style: str | None) -> Path:
    st = song_path.stat()
    raw = (
        f"{song_path.resolve()}|{st.st_mtime_ns}|{st.st_size}|"
        f"{dance_style or '-'}|{CACHE_VERSION}"
    )
    h = hashlib.sha1(raw.encode()).hexdigest()[:16]
    safe_stem = "".join(c if c.isalnum() or c in "-_" else "_" for c in song_path.stem)[:40]
    return CACHE_DIR / f"{safe_stem}_{h}.pkl"


def load(song_path: Path, dance_style: str | None):
    """Return cached `(audio, analysis)` or None if missing/unreadable."""
    p = _key(song_path, dance_style)
    if not p.exists():
        return None
    try:
        with open(p, "rb") as f:
            return pickle.load(f)
    except Exception as exc:
        print(f"  (analysis cache load failed: {exc}; recomputing)")
        return None


def save(song_path: Path, dance_style: str | None, payload) -> None:
    """Pickle `(audio, analysis)` to the cache. Best-effort."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    p = _key(song_path, dance_style)
    try:
        with open(p, "wb") as f:
            pickle.dump(payload, f, protocol=pickle.HIGHEST_PROTOCOL)
    except Exception as exc:
        print(f"  (analysis cache save failed: {exc}; continuing)")
        try:
            p.unlink(missing_ok=True)
        except Exception:
            pass
