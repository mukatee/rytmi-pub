# Where to Get Audio Files

Rytmi analyzes whatever audio you can legally play. Two Creative Commons
sources are built in, plus you can always drop your own files.

## Option 1: Free Music Archive (FMA) — no signup

The default backend. Streams individual MP3s directly out of the remote
`fma_small.zip` archive via HTTP Range requests, so you only download the
tracks you actually need (typically a few megabytes each) instead of the
full 7 GB archive.

```bash
python scripts/download_samples.py                       # defaults
python scripts/download_samples.py --genres rock jazz --per-genre 5
python scripts/download_samples.py --list-genres
```

Caveat: FMA Small is a random curated subset. Track quality varies and the
Latin categories are thin. For Latin dance styles, use Jamendo instead.

## Option 2: Jamendo — better Latin dance catalog

Jamendo has a much larger catalog of rhythm-focused music and filters well
by tag (`bachata`, `kizomba`, `salsa`, `merengue`, ...). Only CC-BY tracks
are downloaded, which keeps the demo safe to publish.

### One-time setup

1. Go to <https://devportal.jamendo.com/> and sign up (free).
2. Create an application. Copy the `client_id`.
3. Add it to `.env` in the project root:
   ```
   JAMENDO_CLIENT_ID=your_id_here
   ```
   (`.env` is already gitignored.)

### Usage

```bash
# Latin dance preset: bachata, kizomba, salsa, merengue, cha-cha, latin
python scripts/download_samples.py --source jamendo --latin

# Specific tags
python scripts/download_samples.py --source jamendo --tags salsa bachata --per-tag 3

# Override client_id without touching .env
python scripts/download_samples.py --source jamendo --latin --client-id XXX
```

Files are saved to `data/songs/<tag>/<id>_<artist>_<title>.mp3` with the
artist and title baked into the filename so you always have attribution.

### License note

Only `http://creativecommons.org/licenses/by/*` tracks are downloaded. These
allow redistribution and demo publication as long as you credit the artist.
CC-BY-SA tracks are filtered out because of the share-alike requirement
(which would force the entire project to be SA-licensed).

## Option 3: Your own files

The pipeline reads any `.wav`, `.mp3`, `.flac`, `.ogg`, or `.m4a` file. Drop
them into any subdirectory under `data/songs/` (gitignored). The batch
notebook at [notebooks/05_batch_analysis.ipynb](../notebooks/05_batch_analysis.ipynb)
scans the whole tree.

```
data/songs/
├── my_playlist/
│   ├── track1.mp3
│   └── track2.mp3
└── studio_recordings/
    └── session1.wav
```

## What we do NOT provide

**No tooling to download copyrighted content from streaming services**
(YouTube, Spotify, Apple Music, etc.). Getting tracks from those services
without authorization violates their terms of service and copyright law.

If you want to test with specific copyrighted songs you already own, rip
your own CDs or convert your purchased files, and drop them into
`data/songs/` manually. That usage is on you — the tool doesn't care where
the audio comes from.

## Option 3: Internet Archive — CC0 1.0 for redistribution-safe demos

For the Kaggle submission notebook (`notebooks/kaggle_demo.ipynb`) we
needed audio that is *fully free to redistribute* so judges can run the
notebook without rights issues. After surveying FMA, Jamendo, ccMixter,
and SoundCloud's CC filter, none had genuine kizomba/zouk tracks under a
permissive enough licence. We settled on one track from the album
*"Un Toque De To"* on Internet Archive, released under
[**CC0 1.0 Universal**](https://creativecommons.org/publicdomain/zero/1.0/)
(public domain — no rights reserved).

| # | Title | Direct download |
|---|---|---|
| 07 | *Besame Otra Vez*   | https://archive.org/download/un-toque-de-to/07%20Besame%20Otra%20Vez.mp3 |

Album landing page: <https://archive.org/details/un-toque-de-to>.

Tempo runs around 100 BPM (within real kizomba's ~80–100 range) and the
Afro-Latin character exercises the kizomba-tuned DSP path meaningfully.
The Kaggle demo notebook downloads the track on first run; locally we
keep it under `data/samples/kizomba_cc/` (gitignored — re-download with
the URL above).
