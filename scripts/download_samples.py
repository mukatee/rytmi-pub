#!/usr/bin/env python3
"""Download sample audio files for rhythm analysis.

Two CC-licensed sources are supported:

**FMA (Free Music Archive)** — default, no signup. Streams individual
MP3s out of the remote ``fma_small.zip`` via HTTP Range requests so
you don't need to download the full 7 GB archive.

**Jamendo** — richer Latin dance catalog (kizomba, bachata, salsa).
Requires a free ``client_id`` from https://devportal.jamendo.com/,
stored in the ``JAMENDO_CLIENT_ID`` env var or passed via --client-id.
Only CC-BY tracks are downloaded (safe for publishable demos).

Usage:
    # FMA (default)
    python scripts/download_samples.py                         # 3 per genre
    python scripts/download_samples.py --genres rock jazz --per-genre 5

    # Jamendo — Latin dance preset
    python scripts/download_samples.py --source jamendo --latin
    python scripts/download_samples.py --source jamendo \\
        --tags salsa bachata kizomba --per-tag 3

    # Info
    python scripts/download_samples.py --list-genres
    python scripts/download_samples.py --list-sources

Tracks are saved to  data/songs/<genre-or-tag>/<id>[_artist_title].mp3
The FMA metadata CSV is cached in  data/fma_metadata/tracks.csv
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import zipfile
from pathlib import Path

class HTTPRangeFile:
    """Seekable file-like object backed by HTTP Range requests with buffering.

    Lets zipfile.ZipFile read a remote zip without downloading it entirely.
    """

    BUFFER_SIZE = 256 * 1024  # read-ahead 256 KB per HTTP request

    def __init__(self, url: str):
        import urllib.request

        self.url = url
        req = urllib.request.Request(url, method="HEAD")
        resp = urllib.request.urlopen(req)
        self.size = int(resp.headers["Content-Length"])
        self._pos = 0
        self._buf = b""
        self._buf_start = 0

    def seekable(self) -> bool:
        return True

    def readable(self) -> bool:
        return True

    def tell(self) -> int:
        return self._pos

    def seek(self, offset: int, whence: int = 0) -> int:
        if whence == 0:
            self._pos = offset
        elif whence == 1:
            self._pos += offset
        elif whence == 2:
            self._pos = self.size + offset
        return self._pos

    def read(self, n: int = -1) -> bytes:
        import urllib.request

        if n == -1 or n is None:
            n = self.size - self._pos
        if n <= 0 or self._pos >= self.size:
            return b""

        # Serve from buffer if fully available
        buf_end = self._buf_start + len(self._buf)
        if self._buf_start <= self._pos and self._pos + n <= buf_end:
            off = self._pos - self._buf_start
            data = self._buf[off : off + n]
            self._pos += len(data)
            return data

        # Fetch with read-ahead
        fetch = max(n, self.BUFFER_SIZE)
        start = self._pos
        end = min(start + fetch, self.size)
        req = urllib.request.Request(self.url)
        req.add_header("Range", f"bytes={start}-{end - 1}")
        self._buf = urllib.request.urlopen(req).read()
        self._buf_start = start

        data = self._buf[:n]
        self._pos += len(data)
        return data


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
SONGS_DIR = DATA_DIR / "songs"
META_DIR = DATA_DIR / "fma_metadata"

# FMA small: 8000 tracks, 30s each, ~7.2 GB total.
# We only download the metadata + a subset of actual audio.
FMA_META_URL = "https://os.unil.cloud.switch.ch/fma/fma_metadata.zip"
FMA_SMALL_URL = "https://os.unil.cloud.switch.ch/fma/fma_small.zip"

# Genre IDs from FMA (top-level genres in fma_metadata/tracks.csv)
# We map readable names to FMA genre IDs.
GENRE_MAP = {
    "electronic": 15,
    "experimental": 38,
    "folk": 17,
    "hip-hop": 21,
    "instrumental": 1235,
    "international": 2,
    "pop": 10,
    "rock": 12,
    "classical": 5,
    "jazz": 4,
    "country": 6,
    "blues": 1,
    "soul-rnb": 3,
    "spoken": 20,
    "old-time": 18,
}

DEFAULT_GENRES = ["rock", "jazz", "classical", "electronic", "folk", "hip-hop"]

# ── Jamendo backend ──────────────────────────────────────────────────────
JAMENDO_API = "https://api.jamendo.com/v3.0/tracks/"
# Creative Commons license URL prefixes.  CC-BY is always allowed; CC-BY-SA
# is optional via --any-cc (still redistributable but adds share-alike).
JAMENDO_CC_BY_PREFIX = "http://creativecommons.org/licenses/by/"
JAMENDO_CC_PREFIX = "http://creativecommons.org/licenses/"  # all CC

# Preset tags for Latin social dance styles.  Each entry lists search terms
# to try in order.  Jamendo's tag vocabulary is sparse for niche styles so
# we fall back to free-text search across title, artist, album, description.
LATIN_PRESETS = {
    "bachata": ["bachata"],
    "kizomba": ["kizomba", "zouk"],          # kizomba is close to zouk
    "salsa":   ["salsa"],
    "merengue": ["merengue"],
    "cha-cha": ["cha cha", "chachacha", "cha-cha-cha"],
    "latin":   ["latin"],
}

DEFAULT_JAMENDO_TAGS = ["rock", "electronic", "pop", "jazz"]

# Jamendo boost options: popularity_total, popularity_month, popularity_week,
# releasedate_desc, downloads_total, listens_total, buzzrate
JAMENDO_BOOST_OPTIONS = [
    "popularity_total",
    "popularity_month",
    "popularity_week",
    "listens_total",
    "buzzrate",
]


def _sanitize_filename(s: str) -> str:
    """Strip/replace characters that cause filesystem issues."""
    s = re.sub(r"[^\w\s.-]", "", s, flags=re.UNICODE)
    s = re.sub(r"\s+", "_", s.strip())
    return s[:60]  # keep filenames short


def _license_ok(track: dict, cc_by_only: bool) -> bool:
    url = track.get("license_ccurl", "")
    if cc_by_only:
        return url.startswith(JAMENDO_CC_BY_PREFIX)
    return url.startswith(JAMENDO_CC_PREFIX)


def _jamendo_api_call(params: dict) -> list[dict]:
    """Raw Jamendo API call.  Returns results list or [] on error."""
    import urllib.parse
    import urllib.request

    url = JAMENDO_API + "?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            payload = json.loads(resp.read().decode())
    except Exception as e:
        print(f"  ERROR: Jamendo API request failed: {e}")
        return []

    if payload.get("headers", {}).get("status") != "success":
        msg = payload.get("headers", {}).get("error_message", "unknown")
        print(f"  ERROR: Jamendo API returned failure: {msg}")
        return []

    return payload.get("results", [])


def jamendo_search(
    query: str,
    client_id: str,
    limit: int = 20,
    cc_by_only: bool = True,
    boost: str = "popularity_total",
    vocalinstrumental: str | None = None,
) -> list[dict]:
    """Search Jamendo for tracks matching a query term, cascading strategies.

    Tries multiple search parameters in order (fuzzy tags → full-text search
    → name search) and merges unique results by track id.  This surfaces
    tracks even when the target style isn't formally tagged.
    """
    base = {
        "client_id": client_id,
        "format": "json",
        "limit": str(limit),
        "audioformat": "mp32",
        "boost": boost,
        "include": "musicinfo licenses",
    }
    if vocalinstrumental in ("vocal", "instrumental"):
        base["vocalinstrumental"] = vocalinstrumental

    # Strategy cascade: fuzzy tag, full-text, name search
    strategies = [
        {"fuzzytags": query},
        {"search": query},
        {"namesearch": query},
    ]

    seen_ids: set = set()
    merged: list[dict] = []
    for strat in strategies:
        params = {**base, **strat}
        results = _jamendo_api_call(params)
        for t in results:
            tid = t.get("id")
            if tid and tid not in seen_ids and _license_ok(t, cc_by_only):
                seen_ids.add(tid)
                merged.append(t)
        # Stop early if we have plenty
        if len(merged) >= limit:
            break

    return merged[:limit]


def download_jamendo(
    tags: list[str],
    per_tag: int,
    client_id: str,
    cc_by_only: bool = True,
    boost: str = "popularity_total",
    vocalinstrumental: str | None = None,
) -> list[Path]:
    """Search Jamendo for each tag/query and download the top results.

    For entries in ``tags`` that match a LATIN_PRESETS key, try all the
    synonym search terms and merge results (e.g. kizomba → kizomba + zouk).
    """
    import urllib.request

    downloaded: list[Path] = []
    SONGS_DIR.mkdir(parents=True, exist_ok=True)

    for tag in tags:
        print(f"\nTag: {tag}")
        queries = LATIN_PRESETS.get(tag, [tag])

        # Gather unique results across synonym queries
        all_results: list[dict] = []
        seen: set = set()
        for q in queries:
            if len(queries) > 1:
                print(f"  trying query '{q}'...")
            hits = jamendo_search(
                q, client_id,
                limit=per_tag * 4,
                cc_by_only=cc_by_only,
                boost=boost,
                vocalinstrumental=vocalinstrumental,
            )
            for t in hits:
                tid = t.get("id")
                if tid and tid not in seen:
                    seen.add(tid)
                    all_results.append(t)

        if not all_results:
            licensing = "CC-BY" if cc_by_only else "any CC"
            print(f"  No {licensing} tracks found for '{tag}'. Try:")
            print("    - --any-cc (relax to all CC licenses)")
            print("    - --order releasedate_desc or --order buzzrate")
            print("    - --tags with alternative search terms")
            continue

        tag_dir = SONGS_DIR / tag
        tag_dir.mkdir(parents=True, exist_ok=True)

        print(f"  {len(all_results)} candidates, keeping top {per_tag}")
        for track in all_results[:per_tag]:
            tid = track.get("id", "unknown")
            title = _sanitize_filename(track.get("name", ""))
            artist = _sanitize_filename(track.get("artist_name", ""))
            audio_url = track.get("audio")
            if not audio_url:
                continue

            dest = tag_dir / f"{tid}_{artist}_{title}.mp3"
            if dest.exists():
                print(f"  Already have {dest.name}")
                downloaded.append(dest)
                continue

            print(f"  Downloading {dest.name}...", end=" ")
            try:
                urllib.request.urlretrieve(audio_url, dest)
                print(f"OK ({dest.stat().st_size // 1024} KB)")
                downloaded.append(dest)
            except Exception as e:
                print(f"FAILED ({e})")

    return downloaded


def _load_jamendo_client_id(cli_value: str | None) -> str | None:
    """Resolve Jamendo client_id from CLI arg, env var, or .env file."""
    if cli_value:
        return cli_value
    env_val = os.environ.get("JAMENDO_CLIENT_ID")
    if env_val:
        return env_val
    # Try reading .env file at project root
    env_path = DATA_DIR.parent / ".env"
    if env_path.exists():
        try:
            for line in env_path.read_text().splitlines():
                line = line.strip()
                if line.startswith("JAMENDO_CLIENT_ID="):
                    value = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if value:
                        return value
        except Exception:
            pass
    return None


def download_metadata() -> Path:
    """Download and extract FMA metadata CSV if not cached."""
    import urllib.request

    tracks_csv = META_DIR / "tracks.csv"
    if tracks_csv.exists():
        print(f"Metadata already cached: {tracks_csv}")
        return tracks_csv

    META_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Downloading FMA metadata (~180 MB)...")
    data, _ = urllib.request.urlretrieve(FMA_META_URL)

    with zipfile.ZipFile(data) as zf:
        # Extract just tracks.csv and genres.csv
        for name in zf.namelist():
            basename = Path(name).name
            if basename in ("tracks.csv", "genres.csv"):
                target = META_DIR / basename
                target.write_bytes(zf.read(name))
                print(f"  Extracted {target}")

    return tracks_csv


def parse_tracks_csv(csv_path: Path) -> list[dict]:
    """Parse the FMA tracks.csv and return list of track dicts.

    The FMA tracks.csv has a multi-level header (first 2 rows).
    Row 0 = top-level group, Row 1 = column name within that group.
    We need: track_id, genre_top (top-level genre), title.
    """
    import csv

    rows = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header_0 = next(reader)  # top-level groups
        header_1 = next(reader)  # column names

        # Build column index: find columns by (group, name) pair
        col_idx = {}
        current_group = ""
        for i, (g, n) in enumerate(zip(header_0, header_1)):
            if g.strip():
                current_group = g.strip()
            col_idx[(current_group, n.strip())] = i

        id_col = 0  # first column is always track_id
        genre_col = col_idx.get(("track", "genre_top"))
        title_col = col_idx.get(("track", "title"))

        set_col = col_idx.get(("set", "subset"))

        if genre_col is None:
            # Fallback: search by name only
            for (g, n), idx in col_idx.items():
                if n == "genre_top":
                    genre_col = idx
                    break
        if set_col is None:
            for (g, n), idx in col_idx.items():
                if g == "set" and n == "subset":
                    set_col = idx
                    break

        for row in reader:
            if len(row) <= max(id_col, genre_col or 0):
                continue
            track_id = row[id_col].strip()
            if not track_id.isdigit():
                continue
            genre = row[genre_col].strip() if genre_col else ""
            title = row[title_col].strip() if title_col else ""
            subset = row[set_col].strip() if set_col else ""
            rows.append({
                "id": int(track_id),
                "genre": genre.lower().replace(" ", "-").replace("/", "-"),
                "title": title,
                "subset": subset,
            })

    return rows


def select_tracks(
    all_tracks: list[dict],
    genres: list[str],
    per_genre: int,
) -> list[dict]:
    """Select a balanced subset of tracks across requested genres."""
    # Normalize genre names
    genre_set = set()
    for g in genres:
        g_norm = g.lower().replace(" ", "-").replace("/", "-")
        genre_set.add(g_norm)

    selected = []
    by_genre: dict[str, list[dict]] = {}
    for t in all_tracks:
        if t["genre"] in genre_set and t.get("subset") == "small":
            by_genre.setdefault(t["genre"], []).append(t)

    for genre in sorted(genre_set):
        tracks = by_genre.get(genre, [])
        if not tracks:
            print(f"  Warning: no tracks found for genre '{genre}'")
            continue
        # Pick evenly spaced tracks (deterministic, not random)
        step = max(1, len(tracks) // per_genre)
        picked = tracks[::step][:per_genre]
        selected.extend(picked)
        print(f"  {genre}: {len(picked)} tracks")

    return selected


def download_tracks(tracks: list[dict]) -> list[Path]:
    """Extract individual tracks from the remote fma_small.zip via HTTP Range requests.

    This avoids downloading the full ~7 GB zip: only the zip index and the
    requested MP3 bytes are transferred.
    """
    print("  Opening remote zip index (no full download)...")
    try:
        remote = HTTPRangeFile(FMA_SMALL_URL)
        zf = zipfile.ZipFile(remote)
    except Exception as e:
        print(f"  ERROR: Could not open remote zip: {e}")
        return []

    downloaded = []
    SONGS_DIR.mkdir(parents=True, exist_ok=True)

    for i, track in enumerate(tracks, 1):
        tid = track["id"]
        genre = track["genre"]

        genre_dir = SONGS_DIR / genre
        genre_dir.mkdir(parents=True, exist_ok=True)
        dest = genre_dir / f"{tid:06d}.mp3"

        if dest.exists():
            print(f"  [{i}/{len(tracks)}] Already have {dest.name}")
            downloaded.append(dest)
            continue

        tid_str = f"{tid:06d}"
        subdir = tid_str[:3]
        zip_path = f"fma_small/{subdir}/{tid_str}.mp3"

        print(f"  [{i}/{len(tracks)}] Extracting {dest.name} ({genre}) [{zip_path}]...", end=" ")
        try:
            data = zf.read(zip_path)
            dest.write_bytes(data)
            print(f"OK ({len(data) // 1024} KB)")
            downloaded.append(dest)
        except KeyError:
            print("NOT FOUND in zip")
        except Exception as e:
            print(f"FAILED ({e})")

    zf.close()
    return downloaded


def list_genres():
    print("Available FMA genres:")
    for name in sorted(GENRE_MAP):
        print(f"  {name}")


def list_sources():
    print("Available sources:")
    print("  fma      — Free Music Archive (no signup, streams fma_small.zip)")
    print("  jamendo  — Jamendo API (CC-BY only, needs JAMENDO_CLIENT_ID)")
    print("\nJamendo Latin preset tags: " + ", ".join(LATIN_PRESETS.keys()))
    print("\nLatin preset search strategies (fallbacks in order):")
    for tag, queries in LATIN_PRESETS.items():
        print(f"  {tag}: {', '.join(queries)}")


def run_fma(args):
    """FMA backend entry point."""
    print(f"Target: {args.per_genre} tracks each from: {', '.join(args.genres)}")
    print()

    print("Step 1: Metadata")
    csv_path = download_metadata()
    all_tracks = parse_tracks_csv(csv_path)
    print(f"  Parsed {len(all_tracks)} tracks from metadata")
    print()

    print("Step 2: Selecting tracks")
    selected = select_tracks(all_tracks, args.genres, args.per_genre)
    if not selected:
        print("No tracks selected. Check genre names with --list-genres")
        sys.exit(1)
    print(f"  Total: {len(selected)} tracks")
    print()

    print("Step 3: Downloading audio")
    downloaded = download_tracks(selected)
    print()
    print(f"Done! {len(downloaded)} tracks saved to {SONGS_DIR}/")


def run_jamendo(args):
    """Jamendo backend entry point."""
    client_id = _load_jamendo_client_id(args.client_id)
    if not client_id:
        print("ERROR: No Jamendo client_id found.")
        print("  Get a free one at: https://devportal.jamendo.com/")
        print("  Then either:")
        print("    - pass it via --client-id XXX")
        print("    - export JAMENDO_CLIENT_ID=XXX")
        print("    - add JAMENDO_CLIENT_ID=XXX to .env")
        sys.exit(1)

    if args.latin:
        tags = list(LATIN_PRESETS.keys())
    elif args.tags:
        tags = args.tags
    else:
        tags = DEFAULT_JAMENDO_TAGS

    licensing = "CC-BY" if not args.any_cc else "any CC"
    vocal_note = f" ({args.vocal})" if args.vocal else ""
    print(f"Target: {args.per_tag} {licensing} tracks per tag{vocal_note}, "
          f"ordered by {args.order}")
    print(f"Tags: {', '.join(tags)}")

    downloaded = download_jamendo(
        tags=tags,
        per_tag=args.per_tag,
        client_id=client_id,
        cc_by_only=not args.any_cc,
        boost=args.order,
        vocalinstrumental=args.vocal,
    )
    print()
    print(f"Done! {len(downloaded)} tracks saved to {SONGS_DIR}/")


def main():
    parser = argparse.ArgumentParser(
        description="Download CC-licensed sample audio for rhythm analysis"
    )
    parser.add_argument(
        "--source", choices=["fma", "jamendo"], default="fma",
        help="Audio source backend (default: fma)",
    )
    parser.add_argument(
        "--list-sources", action="store_true",
        help="List available source backends and exit",
    )
    parser.add_argument(
        "--list-genres", action="store_true",
        help="List available FMA genre names and exit",
    )

    # FMA-specific args
    fma = parser.add_argument_group("fma options")
    fma.add_argument(
        "--per-genre", type=int, default=3,
        help="FMA: tracks per genre (default: 3)",
    )
    fma.add_argument(
        "--genres", nargs="+", default=DEFAULT_GENRES,
        help=f"FMA: genres to download (default: {' '.join(DEFAULT_GENRES)})",
    )

    # Jamendo-specific args
    jam = parser.add_argument_group("jamendo options")
    jam.add_argument(
        "--tags", nargs="+",
        help="Jamendo: tags to search for (e.g. salsa bachata)",
    )
    jam.add_argument(
        "--per-tag", type=int, default=3,
        help="Jamendo: tracks per tag (default: 3)",
    )
    jam.add_argument(
        "--latin", action="store_true",
        help="Jamendo: Latin dance preset (bachata, kizomba, salsa, ...)",
    )
    jam.add_argument(
        "--any-cc", action="store_true",
        help="Jamendo: allow any CC license (not just CC-BY). More tracks, "
             "but CC-BY-SA adds share-alike requirements.",
    )
    jam.add_argument(
        "--order", choices=JAMENDO_BOOST_OPTIONS, default="popularity_total",
        help="Jamendo: result ordering (default: popularity_total). Try "
             "popularity_month or buzzrate for fresher picks.",
    )
    jam.add_argument(
        "--vocal", choices=["vocal", "instrumental"],
        help="Jamendo: bias toward vocal or instrumental tracks",
    )
    jam.add_argument(
        "--client-id",
        help="Jamendo: API client_id (or set JAMENDO_CLIENT_ID env var)",
    )

    args = parser.parse_args()

    if args.list_sources:
        list_sources()
        return
    if args.list_genres:
        list_genres()
        return

    if args.source == "fma":
        run_fma(args)
    elif args.source == "jamendo":
        run_jamendo(args)

    print("Run notebook 05_batch_analysis.ipynb to analyze the downloads.")


if __name__ == "__main__":
    main()
