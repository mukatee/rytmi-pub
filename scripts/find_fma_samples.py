"""
Find CC-licensed tracks from FMA metadata that might work as kizomba/zouk placeholders.

Usage:
  python scripts/find_fma_samples.py                  # default search
  python scripts/find_fma_samples.py --genre International
  python scripts/find_fma_samples.py --tags "zouk,afro,kizomba,semba,latin"
  python scripts/find_fma_samples.py --license-allow-nd  # include NoDerivatives
  python scripts/find_fma_samples.py --top 30

Prints a ranked table and the FMA download URL for each candidate.
The FMA mp3 download URL pattern is:
  https://files.freemusicarchive.org/storage-freemusicarchive-org/music/<N//1000>/<track_id:06d>.mp3
but that requires knowing the path prefix.  The stable public URL is:
  https://freemusicarchive.org/track/<track_id>/

To actually download use e.g.:
  wget "$(python scripts/find_fma_samples.py --top 1 --url-only)"
"""

import argparse
import ast
import sys
from pathlib import Path

import pandas as pd

METADATA_DIR = Path(__file__).parent.parent / "data" / "fma_metadata"


# Licences that allow redistribution + derivatives (safe for demo notebook)
OPEN_LICENSES = {
    "attribution",
    "attribution-sharealike",
    "attribution-noncommercial",
    "attribution-noncommercial-sharealike",
    "attribution-noncommercial-share alike",
    "attribution noncommercial share alike",
}

# Licences that explicitly forbid derivatives — usable but borderline
ND_LICENSES_FRAGMENTS = ["noderivatives", "no derivative", "no-derivative", "music sharing"]

# Tags to score up (order matters: first match wins the boost)
RHYTHM_TAGS = [
    "kizomba",
    "zouk",
    "semba",
    "cabo verde",
    "cape verdean",
    "afro-latin",
    "coladeira",
    "morna",
    "afrobeat",
    "afro",
    "cumbia",
    "latin",
    "world",
    "dance",
    "angola",
]


def load_tracks() -> pd.DataFrame:
    path = METADATA_DIR / "tracks.csv"
    if not path.exists():
        sys.exit(f"tracks.csv not found at {path}")
    df = pd.read_csv(path, index_col=0, header=[0, 1])
    # Flatten to single-level for easier access
    t = df["track"].copy()
    t["artist_name"] = df["artist"]["name"]
    t.index.name = "track_id"
    return t


def is_open_license(lic: str, allow_nd: bool) -> bool:
    if not isinstance(lic, str):
        return False
    low = lic.lower()
    for frag in OPEN_LICENSES:
        if frag in low:
            return True
    if allow_nd:
        for frag in ND_LICENSES_FRAGMENTS:
            if frag in low:
                return True
    return False


def tag_score(tags_raw, genre_top) -> tuple[int, list[str]]:
    """Return (score, matched_tags)."""
    tags_str = ""
    if isinstance(tags_raw, str):
        try:
            tags_list = ast.literal_eval(tags_raw)
            tags_str = " ".join(tags_list).lower()
        except Exception:
            tags_str = tags_raw.lower()
    if isinstance(genre_top, str):
        tags_str += " " + genre_top.lower()

    score = 0
    matched = []
    for i, tag in enumerate(RHYTHM_TAGS):
        if tag in tags_str:
            # Higher-priority tags score more
            pts = len(RHYTHM_TAGS) - i
            score += pts
            matched.append(tag)
    return score, matched


def fma_page_url(track_id: int) -> str:
    return f"https://freemusicarchive.org/track/{track_id}/"


def main():
    ap = argparse.ArgumentParser(description="Find CC kizomba/zouk-ish FMA tracks")
    ap.add_argument("--genre", default=None, help="Filter to a genre_top value, e.g. International")
    ap.add_argument(
        "--tags",
        default="kizomba,zouk,semba,afro,latin,coladeira,morna,angola,cabo verde",
        help="Comma-separated tag keywords to search for (OR logic)",
    )
    ap.add_argument("--top", type=int, default=20, help="How many results to print")
    ap.add_argument(
        "--license-allow-nd",
        action="store_true",
        help="Also include NoDerivatives licences (stricter, but still CC)",
    )
    ap.add_argument("--min-listens", type=int, default=0, help="Minimum listen count filter")
    ap.add_argument("--url-only", action="store_true", help="Print only the top-1 page URL")
    args = ap.parse_args()

    t = load_tracks()

    # License filter
    mask_lic = t["license"].apply(lambda x: is_open_license(x, args.license_allow_nd))

    # Tag / genre keyword filter
    keywords = [k.strip().lower() for k in args.tags.split(",") if k.strip()]
    tag_mask = t["tags"].fillna("").str.lower()
    genre_mask = t["genre_top"].fillna("").str.lower()
    combined_text = tag_mask + " " + genre_mask
    kw_mask = combined_text.apply(lambda s: any(k in s for k in keywords))

    # Genre filter (optional strict)
    genre_filt = pd.Series(True, index=t.index)
    if args.genre:
        genre_filt = t["genre_top"].fillna("").str.lower() == args.genre.lower()

    # Listens filter
    listens = pd.to_numeric(t["listens"], errors="coerce").fillna(0)
    listens_mask = listens >= args.min_listens

    candidates = t[mask_lic & kw_mask & genre_filt & listens_mask].copy()

    if candidates.empty:
        print("No matches found. Try --license-allow-nd or broader --tags.")
        sys.exit(0)

    # Score
    scores = candidates.apply(
        lambda row: tag_score(row["tags"], row["genre_top"]), axis=1
    )
    candidates["_score"] = scores.apply(lambda x: x[0])
    candidates["_matched"] = scores.apply(lambda x: ", ".join(x[1]))
    candidates["_listens"] = pd.to_numeric(candidates["listens"], errors="coerce").fillna(0)
    candidates = candidates.sort_values(["_score", "_listens"], ascending=False)

    top = candidates.head(args.top)

    if args.url_only:
        print(fma_page_url(top.index[0]))
        return

    print(f"\nFound {len(candidates)} candidates, showing top {len(top)}:\n")
    print(f"{'ID':>7}  {'Score':>5}  {'Listens':>7}  {'Artist':<30}  {'Title':<40}  {'Matched tags':<30}  License")
    print("-" * 160)
    for tid, row in top.iterrows():
        artist = str(row.get("artist_name", ""))[:29]
        title = str(row.get("title", ""))[:39]
        lic = str(row.get("license", ""))[:50]
        matched = str(row["_matched"])[:29]
        listens_val = int(row["_listens"])
        score = int(row["_score"])
        print(f"{tid:>7}  {score:>5}  {listens_val:>7}  {artist:<30}  {title:<40}  {matched:<30}  {lic}")
        print(f"         {'':>5}  {'':>7}  → {fma_page_url(tid)}")
    print()


if __name__ == "__main__":
    main()
