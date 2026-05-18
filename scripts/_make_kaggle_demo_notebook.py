"""One-shot generator for notebooks/kaggle_demo.ipynb.

Run once with the project venv:

    .venv/bin/python scripts/_make_kaggle_demo_notebook.py

This is the judge-facing notebook for the Kaggle Gemma 4 Good Hackathon
submission.  It is self-contained: clones the public rytmi-pub repo via
pip, downloads three CC0 kizomba tracks from the Internet Archive, and
shows the full DSP + Gemma pipeline with pre-cached outputs so the
judges see results without running anything.

Three modes:

- ``cached``  — read every Gemma output from notebooks/cache/cc0_*.
                Works offline, no API key, always renders.
- ``live``    — call Gemma fresh for every prompt.  Needs
                ``GEMMA_API_KEY`` (Kaggle Secret or env).
- BYO audio  — set ``AUDIO_PATH`` to a Kaggle Dataset MP3 and run the
                BYO cell.  Requires ``MODE = "live"``.

The interactive_timeline widget gets a tiny Kaggle compatibility patch
so the scrolling waveform + audio player work both locally
(``notebooks/`` → ``../data/_timeline_cache/``) and on Kaggle
(``/kaggle/working/`` → ``_timeline_cache/``).
"""

from __future__ import annotations

import nbformat as nbf
from pathlib import Path

NB_PATH = Path(__file__).resolve().parent.parent / "notebooks" / "kaggle_demo.ipynb"


def md(src: str):
    return nbf.v4.new_markdown_cell(src)


def code(src: str, hide_input: bool = True):
    # Default hide_input=True so the Kaggle viewer shows only the cell
    # output (the visuals + Gemma text) and tucks the boilerplate code
    # behind a 'Show input' toggle.  Pass hide_input=False for the few
    # cells where seeing the call site adds value (the per-track
    # `display_track(...)` line is the obvious one).
    cell = nbf.v4.new_code_cell(src)
    if hide_input:
        cell.metadata["_kg_hide-input"] = True
    return cell


CELLS = []

# ----------------------------------------------------------------------
# 1. Title
# ----------------------------------------------------------------------
CELLS.append(md("""\
# Rytmi — rhythm learning for dance and music with Gemma 4

A submission for the **Gemma 4 Good Hackathon** (*Future of Education* track).

Rytmi helps dancers and musicians **hear the beat, find the "1", and feel
phrase structure** in music — especially in styles like kizomba where the
pulse is subtle and easy to lose.  It pairs **librosa DSP** (beat tracking,
onset detection, section/phase segmentation) with **Gemma 4** (per-section
coaching, transitions, listening guides, drills).

| Link | |
|---|---|
| Code (public mirror) | https://github.com/mukatee/rytmi-pub |
| Kaggle Notebook      | https://www.kaggle.com/code/donkeys/gemma-dancing |
| Demo video           | https://youtu.be/S3yNA6M_CFs |
| Writeup              | see `docs/kaggle_writeup.md` in the repo |

**Audio licence:** the demo track used below is released under
[**CC0 1.0 Universal**](https://creativecommons.org/publicdomain/zero/1.0/)
(public domain) from the album *"Un Toque De To"* on the Internet
Archive.  See the attribution cell at the bottom for full credit.
"""))

# ----------------------------------------------------------------------
# 2. Reading guide
# ----------------------------------------------------------------------
CELLS.append(md("""\
## How to read this notebook

> **You don't need to run anything to evaluate.**  Cached Gemma outputs
> are displayed inline below every prompt.  Hit *Run All* only if you
> want to re-render the interactive timeline widgets (which need the
> audio file present) or generate fresh Gemma text in live mode.

**Architecture in one line:**

```
audio  ─►  librosa DSP  ─►  RhythmAnalysis  ─►  Gemma 4 prompt  ─►  coaching text
            (beats,         (tempo, beats,        (style-aware,
             onsets,         downbeats,            grounded in
             sections)       phases, clarity)      DSP features)
```

**Why this split:** DSP gives Gemma reliable, *measurable* rhythm
features.  Gemma turns those into language a learner can act on.
Verifiers check that Gemma's output covers the song without inventing
sections.  We deliberately do **not** ask Gemma to detect the beat from
raw audio — DSP is better at that.

**5-minute skim path:**
*cells 1 → 2 → 9 → first track section → summary*.

**Modes:** cached (default, no setup) · live (Gemma API key) · bring
your own audio.  See cell 7 for configuration.
"""))

# ----------------------------------------------------------------------
# 3. Pip install — runtime deps
# ----------------------------------------------------------------------
CELLS.append(code("""\
# Runtime dependencies.  Quiet mode keeps Kaggle output tidy.
# `standard-aifc` / `standard-sunau` are needed because `audioop` was
# removed in Python 3.13 and librosa still imports them indirectly.
!pip install -q \\
    "librosa>=0.11" "scipy>=1.14" "numpy>=2.0" \\
    "matplotlib>=3.8" "soundfile" "openai" \\
    "standard-aifc; python_version>='3.13'" \\
    "standard-sunau; python_version>='3.13'" \\
    requests"""))

# ----------------------------------------------------------------------
# 4. Pip install — rytmi from public github
# ----------------------------------------------------------------------
CELLS.append(code("""\
# Install Rytmi straight from the public GitHub mirror — no need to
# attach the repo as a Kaggle Dataset.
!pip install -q "git+https://github.com/mukatee/rytmi-pub.git" """))

# ----------------------------------------------------------------------
# 5. Download CC0 audio
# ----------------------------------------------------------------------
CELLS.append(code("""\
# Pull the demo CC0 1.0 Universal track from the Internet Archive.
# The album is fetched as a single zip (more reliable than per-file URLs).
# Skips the download if the target is already present.
import io, os, sys, zipfile
from pathlib import Path
import requests

# Kaggle drops user-writable space at /kaggle/working; locally we use
# the repo's data/samples/kizomba_cc dir if it exists.
IS_KAGGLE = Path("/kaggle/working").exists()
if IS_KAGGLE:
    AUDIO_DIR = Path("/kaggle/working/cc0_audio")
else:
    repo_audio = Path("data/samples/kizomba_cc").resolve()
    AUDIO_DIR = repo_audio if repo_audio.exists() else Path("cc0_audio").resolve()
AUDIO_DIR.mkdir(parents=True, exist_ok=True)
print(f"audio dir: {AUDIO_DIR}")

# Target filenames expected by the rest of the notebook, keyed by track-number prefix.
PREFIX_TO_TARGET = {
    "07": "07_besame_otra_vez.mp3",
}

targets = {t: AUDIO_DIR / t for t in PREFIX_TO_TARGET.values()}

# Check which files are already present.
missing_prefixes = [
    prefix for prefix, tname in PREFIX_TO_TARGET.items()
    if not (AUDIO_DIR / tname).exists() or (AUDIO_DIR / tname).stat().st_size < 100_000
]

for tname, dest in targets.items():
    if dest.exists() and dest.stat().st_size > 100_000:
        print(f"  ok  {tname}  ({dest.stat().st_size:,} bytes, already present)")

if missing_prefixes:
    ZIP_URL = (
        "https://archive.org/compress/UnToqueDTo"
        "/formats=VBR%20MP3&file=/UnToqueDTo.zip"
    )
    print(f"  downloading album zip from archive.org …", flush=True)
    with requests.get(ZIP_URL, stream=True, timeout=300) as r:
        r.raise_for_status()
        data = r.content
    print(f"  zip downloaded ({len(data):,} bytes), extracting …")

    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        mp3_members = [n for n in zf.namelist() if n.lower().endswith(".mp3")]
        for prefix in missing_prefixes:
            # Find the zip entry whose filename starts with the two-digit prefix.
            match = next(
                (n for n in mp3_members if Path(n).name.startswith(prefix)),
                None,
            )
            if match is None:
                print(f"  WARNING: no file with prefix {prefix!r} found in zip")
                continue
            dest = AUDIO_DIR / PREFIX_TO_TARGET[prefix]
            dest.write_bytes(zf.read(match))
            print(f"  wrote {dest.name}  ({dest.stat().st_size:,} bytes)  ← {Path(match).name}")

print("audio ready.")"""))

# ----------------------------------------------------------------------
# 6. Audio swap-in instructions
# ----------------------------------------------------------------------
CELLS.append(md("""\
### Bring your own audio (optional)

To run the pipeline on your own track instead of (or in addition to)
the CC0 tracks above:

1. Right sidebar → **Add Input → Datasets** → attach an existing Kaggle
   dataset that contains an MP3 or WAV, or upload your own.
2. In **cell 7 (config)** set `AUDIO_PATH = "/kaggle/input/<dataset>/<file>.mp3"`.
3. Make sure `MODE = "live"` (needs a `GEMMA_API_KEY` Kaggle Secret).
4. Run cells 1–7, then jump to the *Bring your own audio* cell near
   the bottom.

Rytmi will analyze the new track and stream a full Gemma coaching pass
just like the cached tracks below.
"""))

# ----------------------------------------------------------------------
# 7. Config cell
# ----------------------------------------------------------------------
CELLS.append(code("""\
# === Configuration ============================================================
# Three modes:
#   "cached" → read every Gemma output from notebooks/cache/  (no API key)
#   "live"   → call Gemma fresh for every prompt              (needs API key)
#   "auto"   → live if a key is present, cached otherwise
MODE = "auto"

# Gemma 4 model.  Default is the public HuggingFace id for the E4B
# instruction-tuned checkpoint -- well known, easy to look up, and small
# enough to self-host on Kaggle's free T4.  Override with whatever slug
# your endpoint expects (e.g. Ollama: 'gemma4:e4b';  Google AI Studio:
# 'models/gemma-4-e4b-it';  larger HF checkpoints: 'google/gemma-4-26b-a4b-it').
GEMMA_MODEL    = "google/gemma-4-e4b-it"
GEMMA_API_BASE = "https://generativelanguage.googleapis.com/v1beta/openai/"

# Bring-your-own audio — set to /kaggle/input/<dataset>/<file>.mp3 to run
# the live pipeline on your own track at the bottom of the notebook.
AUDIO_PATH = None

# === API key resolution =======================================================
# Prefers Kaggle Secret → env var.  Never falls back to disk.
import os
GEMMA_API_KEY = None
try:
    from kaggle_secrets import UserSecretsClient
    GEMMA_API_KEY = UserSecretsClient().get_secret("GEMMA_API_KEY")
    print("found GEMMA_API_KEY via Kaggle Secret")
except Exception:
    GEMMA_API_KEY = os.environ.get("GEMMA_API_KEY")
    if GEMMA_API_KEY:
        print("found GEMMA_API_KEY via environment")

if MODE == "auto":
    MODE = "live" if GEMMA_API_KEY else "cached"

print(f"resolved MODE = {MODE!r}")
print(f"model        = {GEMMA_MODEL!r}")
print(f"endpoint     = {GEMMA_API_BASE!r}")

# A quick reminder for judges:
if MODE == "cached":
    print()
    print("Cached mode: all Gemma outputs below are pre-generated.")
    print("To run live, add a Kaggle Secret named GEMMA_API_KEY and re-run from here.")
    print("API key: https://aistudio.google.com/apikey")"""))

# ----------------------------------------------------------------------
# 8. Setup helpers — cache loader, Gemma client, Kaggle path patch
# ----------------------------------------------------------------------
CELLS.append(code("""\
# Setup: cache loader, optional Gemma client, Kaggle-aware viz patch.
import json
from pathlib import Path

from IPython.display import HTML, Markdown, display

from rytmi import analyze, load_audio
from rytmi import viz as rytmi_viz
from rytmi.dsp import describe_sections, describe_transitions
from rytmi.prompts import (
    QUESTION_KIZOMBA_DRILLS,
    QUESTION_KIZOMBA_TRANSITIONS,
    QUESTION_KIZOMBA_TUTOR,
    QUESTION_LISTENING_GUIDE,
    QUESTION_RHYTHM_ANATOMY,
    QUESTION_SONG_ARC,
    format_unified_timeline,
)

# ---------------------------------------------------------------------------
# Cache directory — committed under notebooks/cache/ in the public repo.
# Both Kaggle (after `pip install git+...`) and local checkouts need to
# find it.  On Kaggle we re-download via git into /kaggle/working/_cache
# only if the pip-installed wheel didn't ship it (the public mirror keeps
# the cache files in-tree).
# ---------------------------------------------------------------------------
def _find_cache_dir() -> Path:
    candidates = [
        Path.cwd() / "notebooks" / "cache",        # local: notebook at repo root
        Path.cwd().parent / "notebooks" / "cache", # local: notebook in notebooks/
        Path("/kaggle/working/cache"),
    ]
    for c in candidates:
        if (c / "cc0_09_te_quiero_amor_outputs.json").exists():
            return c
    # Fallback: clone the public repo into /kaggle/working/_rytmi_cache
    target = Path("/kaggle/working/_rytmi_cache") if IS_KAGGLE else Path.cwd() / "_rytmi_cache"
    if not (target / "notebooks" / "cache" / "cc0_09_te_quiero_amor_outputs.json").exists():
        print(f"  cache not found in repo, cloning rytmi-pub into {target} …")
        import subprocess
        subprocess.run(
            ["git", "clone", "--depth=1",
             "https://github.com/mukatee/rytmi-pub.git", str(target)],
            check=True,
        )
    return target / "notebooks" / "cache"

CACHE_DIR = _find_cache_dir()
print(f"cache dir: {CACHE_DIR}")

# ---------------------------------------------------------------------------
# Cache file IO
# ---------------------------------------------------------------------------
def load_cached_outputs(slug: str) -> dict:
    p = CACHE_DIR / f"cc0_{slug}_outputs.json"
    return json.loads(p.read_text())

# ---------------------------------------------------------------------------
# Optional live Gemma client.  Only constructed in live mode.
# ---------------------------------------------------------------------------
GEMMA_CLIENT = None
if MODE == "live":
    from rytmi.llm import load_cloud_model, explain_rhythm  # noqa: F401
    GEMMA_CLIENT, _ = load_cloud_model(
        model_id=GEMMA_MODEL,
        base_url=GEMMA_API_BASE,
        api_key=GEMMA_API_KEY,
        print_url=True,
    )
    print(f"Gemma client ready: {GEMMA_MODEL}")

# ---------------------------------------------------------------------------
# Prompt menu — name → (question, max_tokens).  Token budgets are
# generous because some Gemma 4 checkpoints reserve a chunk of the
# completion window for internal reasoning before producing visible
# text.  Smaller models ignore the unused headroom.
# ---------------------------------------------------------------------------
PROMPTS = [
    ("rhythm_anatomy",       QUESTION_RHYTHM_ANATOMY,       4096),
    ("listening_guide",      QUESTION_LISTENING_GUIDE,      4096),
    ("song_arc",             QUESTION_SONG_ARC,             4096),
    ("kizomba_tutor",        QUESTION_KIZOMBA_TUTOR,        6144),
    ("kizomba_drills",       QUESTION_KIZOMBA_DRILLS,       6144),
    ("kizomba_transitions",  QUESTION_KIZOMBA_TRANSITIONS,  6144),
]

def run_live_outputs(analysis) -> dict:
    \"\"\"Run every Gemma prompt fresh.  Used in live mode and for BYO audio.\"\"\"
    from rytmi.llm import explain_rhythm
    out = {
        "_meta": {
            "duration_s": float(analysis.audio.duration),
            "tempo": float(analysis.tempo),
            "n_beats": int(len(analysis.beats.times)),
            "downbeat_confidence": float(getattr(analysis, "downbeat_confidence", 0.0) or 0.0),
            "n_sections": int(len(getattr(analysis, "sections", []) or [])),
            "n_phases": int(len(getattr(analysis, "phases", []) or [])),
            "sections_describe": describe_sections(analysis),
        },
        "_transitions_describe": describe_transitions(analysis),
    }
    for name, question, max_tok in PROMPTS:
        print(f"  Gemma → {name} …", flush=True)
        text = ""
        for budget in (max_tok, max_tok * 2):
            text = explain_rhythm(
                analysis, question=question,
                processor=GEMMA_CLIENT, model=GEMMA_MODEL,
                max_new_tokens=budget, temperature=0.5,
            )
            if text.strip():
                break
        out[name] = text
    if out.get("kizomba_tutor") and out.get("kizomba_transitions"):
        out["unified_timeline"] = format_unified_timeline(
            out["kizomba_tutor"], out["kizomba_transitions"],
        )
    return out

def get_outputs(slug: str, analysis=None) -> dict:
    \"\"\"Cached-mode reader; in live mode, re-runs Gemma.\"\"\"
    if MODE == "cached":
        return load_cached_outputs(slug)
    if analysis is None:
        raise ValueError("live mode needs an analysis to call Gemma against")
    return run_live_outputs(analysis)

# ---------------------------------------------------------------------------
# interactive_timeline asset patch (always on).
#
# `interactive_timeline` writes a PNG + WAV next to the installed rytmi
# package (.../site-packages/rytmi/../../data/_timeline_cache/) and
# emits HTML that references them via the relative URL
# `../data/_timeline_cache/<file>`.  That URL is resolved by the
# browser against the notebook's location, NOT against the package's
# install path — so when rytmi is installed via `pip install git+...`
# (as it is here), the widget writes to one place and the browser
# fetches from another, leaving the image blank and the audio dead.
#
# Fix: always write the assets into `<notebook_cwd>/_timeline_cache/`
# and rewrite the URL prefix to `_timeline_cache/` so the browser
# fetches them from the same place.  Works identically on Kaggle
# (/kaggle/working) and locally (notebooks/).
# ---------------------------------------------------------------------------
_PATCHED_DIR = Path.cwd() / "_timeline_cache"
_PATCHED_DIR.mkdir(parents=True, exist_ok=True)
rytmi_viz._timeline_cache_dir = lambda: _PATCHED_DIR

def show_timeline(analysis, title: str) -> None:
    html = rytmi_viz.interactive_timeline(analysis, title=title, pixels_per_second=80)
    # Same rewrite locally and on Kaggle: the assets now live next to
    # the notebook, not under ../data/.
    html = html.replace("../data/_timeline_cache/", "_timeline_cache/")
    display(HTML(html))

# ---------------------------------------------------------------------------
# Text rendering helper.  Gemma outputs use single newlines between
# lines (each `P1:`, `P2:` ... on its own line).  Markdown collapses
# single newlines into spaces within a paragraph, which turns each
# prompt's output into one long unreadable line.  Convert single
# newlines to Markdown hard breaks (two trailing spaces + newline) so
# per-line structure is kept intact, while leaving blank-line
# paragraph breaks alone.
# ---------------------------------------------------------------------------
def as_markdown(text: str) -> str:
    lines = text.split("\\n")
    out = []
    for i, line in enumerate(lines):
        is_last = i == len(lines) - 1
        next_blank = (not is_last) and lines[i + 1].strip() == ""
        if line.strip() == "" or is_last or next_blank:
            out.append(line)
        else:
            out.append(line + "  ")  # trailing 2 spaces = hard break
    return "\\n".join(out)

print("setup done.")"""))

# ----------------------------------------------------------------------
# 9. CC0 audio choice note
# ----------------------------------------------------------------------
CELLS.append(md("""\
## Why this track?

The [demo video](https://youtu.be/S3yNA6M_CFs) uses copyrighted
kizomba/bachata for authenticity (Filomena Maricoa, Charbel).  For this
notebook we needed audio that is **fully free to redistribute** so
judges can rerun without rights issues.  After surveying:

- **Free Music Archive** — no kizomba/zouk in any CC tier
- **Jamendo, ccMixter, SoundCloud CC filter** — same story

We settled on *Besame Otra Vez* from the **CC0 1.0 Universal** album
[*"Un Toque De To"*](https://archive.org/details/un-toque-de-to) on
Internet Archive.  At 89 BPM with a clearly audible break and peak
section it sits inside real-kizomba tempo range and gives the
kizomba-tuned DSP path something genuine to chew on — and **the
pipeline works equally well on any audio you supply**.  See the
*Bring your own audio* cell near the bottom.

Production note: real-world Rytmi users would point this at their own
practice tracks.  The CC0 substitution is a redistribution-rights
accommodation for this submission, not a product limitation.
"""))

# ----------------------------------------------------------------------
# Per-track helper function (defined once, used 3 times)
# ----------------------------------------------------------------------
CELLS.append(code("""\
# Per-track display function.  Takes a slug + display title; loads
# audio, runs DSP (always live — fast), pulls Gemma outputs from the
# cache or runs live, then renders everything inline.
def display_track(slug: str, display_title: str) -> None:
    print(f"=== {slug} ({display_title}) ===")
    audio = load_audio(str(AUDIO_DIR / f"{slug}.mp3"))
    analysis = analyze(audio, dance_style="kizomba")
    outs = get_outputs(slug, analysis if MODE == "live" else None)

    # --- DSP summary -------------------------------------------------------
    meta = outs.get("_meta", {})
    display(Markdown(
        f"**DSP summary** — tempo {analysis.tempo:.1f} BPM · "
        f"{len(analysis.beats.times)} beats · "
        f"{len(getattr(analysis, 'sections', []) or [])} sections · "
        f"{len(getattr(analysis, 'phases', []) or [])} phases · "
        f"downbeat confidence {getattr(analysis, 'downbeat_confidence', 0.0):.2f}"
    ))

    # --- Interactive timeline + audio player ------------------------------
    display(Markdown("### DSP · Interactive timeline\\n_What the signal layer detected._ "
                     "Play, scrub, or click to seek. The red cursor tracks the audio."))
    show_timeline(analysis, title=display_title)

    # --- Per-section table -------------------------------------------------
    # Wrap the plain-text table in a horizontally-scrollable <pre> so the
    # Kaggle notebook viewer (narrow column) doesn't word-wrap it.
    display(Markdown("### DSP · Section table — the structured input Gemma 4 reads"))
    import html as _html
    display(HTML(
        "<pre style='overflow-x:auto; white-space:pre; font-size:0.9em; "
        "line-height:1.3'>" + _html.escape(describe_sections(analysis)) + "</pre>"
    ))

    # --- Gemma outputs -----------------------------------------------------
    display(Markdown(
        "> **Everything below is Gemma 4's output.** The model turns the "
        "DSP table above into language a dancer can use — grounded in "
        "those numbers, never hand-written or invented."
    ))
    headings = {
        "rhythm_anatomy":      "Gemma 4 · Rhythm anatomy — kizomba as a genre",
        "listening_guide":     "Gemma 4 · Listening guide — orient the ear",
        "song_arc":            "Gemma 4 · Song arc — the energy journey",
        "kizomba_tutor":       "Gemma 4 · Kizomba tutor — per-phase coaching",
        "kizomba_drills":      "Gemma 4 · Practice plan — drills tied to sections",
        "kizomba_transitions": "Gemma 4 · Transitions — what to do at boundaries",
    }
    for key, heading in headings.items():
        text = outs.get(key, "")
        display(Markdown(f"### {heading}"))
        if text and not text.startswith("[ERROR"):
            display(Markdown(as_markdown(text)))
        else:
            display(Markdown(f"_(no cached output for `{key}` — re-run cache build)_"))

    if "unified_timeline" in outs:
        display(Markdown("### Gemma 4 + verifier · Unified timeline — coaching, code-checked against DSP sections"))
        display(HTML(
            "<pre style='overflow-x:auto; white-space:pre; font-size:0.9em; "
            "line-height:1.3'>" + _html.escape(outs["unified_timeline"]) + "</pre>"
        ))

print("display_track() ready.")"""))

# ----------------------------------------------------------------------
# Per-track cells
# ----------------------------------------------------------------------
TRACKS = [
    ("07_besame_otra_vez", "Besame Otra Vez"),
]

for slug, title in TRACKS:
    CELLS.append(md(f"## *{title}* — full pipeline"))
    # hide_input=False: the `display_track(slug, title)` one-liner is
    # the only user-facing code call worth showing in the Kaggle viewer.
    CELLS.append(code(f"display_track({slug!r}, {title!r})", hide_input=False))

# ----------------------------------------------------------------------
# BYO audio
# ----------------------------------------------------------------------
CELLS.append(md("""\
## Bring your own audio

If you set `AUDIO_PATH` in the config cell and you are in `live` mode,
the cell below runs the full pipeline on your file.  Otherwise it is a
no-op.
"""))

CELLS.append(code("""\
if AUDIO_PATH and Path(AUDIO_PATH).exists():
    if MODE != "live":
        print("AUDIO_PATH set but MODE is not 'live' — set GEMMA_API_KEY and re-run cell 7.")
    else:
        print(f"Analyzing {AUDIO_PATH} live …")
        byo_audio = load_audio(AUDIO_PATH)
        byo_analysis = analyze(byo_audio, dance_style="kizomba")
        byo_outs = run_live_outputs(byo_analysis)
        display(Markdown(
            f"**DSP summary** — tempo {byo_analysis.tempo:.1f} BPM · "
            f"{len(byo_analysis.beats.times)} beats · "
            f"{len(getattr(byo_analysis, 'sections', []) or [])} sections"
        ))
        show_timeline(byo_analysis, title=Path(AUDIO_PATH).stem)
        display(Markdown(
            "> **Everything below is Gemma 4's output**, grounded in the "
            "DSP analysis above."
        ))
        for key, heading in [
            ("rhythm_anatomy",      "Gemma 4 · Rhythm anatomy"),
            ("listening_guide",     "Gemma 4 · Listening guide"),
            ("song_arc",            "Gemma 4 · Song arc"),
            ("kizomba_tutor",       "Gemma 4 · Kizomba tutor"),
            ("kizomba_drills",      "Gemma 4 · Drills"),
            ("kizomba_transitions", "Gemma 4 · Transitions"),
        ]:
            text = byo_outs.get(key, "")
            if text and not text.startswith("[ERROR"):
                display(Markdown(f"### {heading}"))
                display(Markdown(as_markdown(text)))
        if "unified_timeline" in byo_outs:
            import html as _html
            display(Markdown("### Gemma 4 + verifier · Unified timeline"))
            display(HTML(
                "<pre style='overflow-x:auto; white-space:pre; font-size:0.9em; "
                "line-height:1.3'>" + _html.escape(byo_outs["unified_timeline"]) + "</pre>"
            ))
else:
    print("No AUDIO_PATH set — skipping BYO cell.")
    print("To use your own audio: see the swap-in cell above.")"""))

# ----------------------------------------------------------------------
# Summary
# ----------------------------------------------------------------------
CELLS.append(md("""\
## What this demonstrates

- **Style-aware DSP.**  `analyze(audio, dance_style="kizomba")` runs a
  beat tracker tuned for the kizomba batida (low-pass + low-band onset
  envelope) and reports per-section *beat clarity tags* (subtle /
  moderate / clear) plus *downbeat confidence* so Gemma can judge how
  certain to sound.
- **Gemma 4 as the language layer.**  Six prompts cover genre context,
  listening orientation, song-arc narration, per-phase coaching, drills,
  and boundary transitions.  Each prompt is grounded in DSP features and
  carries hard rules (e.g. *"don't say 'the 1'"* for kizomba) baked
  directly into the prompt text.
- **Verifiers as guardrails.**  The drills and transitions prompts run
  through Python verifiers that drop or rewrite any Gemma output that
  invents sections, drops the P# format, or otherwise hallucinates.
- **Honest about uncertainty.**  When `downbeat_confidence` is low, the
  prompts explicitly tell Gemma to coach in *"feel the bass"* terms
  instead of count-based language.
- **Practical local-first stack.**  Default local target is Gemma 4 E2B /
  E4B via Ollama — small enough for a laptop, accurate enough for
  coaching.  Larger checkpoints help for the most stylized outputs but
  are never required.

> **Design principle:** *DSP grounds, Gemma writes, code verifies.*
> No layer is asked to do what another layer does better.
"""))

# ----------------------------------------------------------------------
# Attribution
# ----------------------------------------------------------------------
CELLS.append(md("""\
## Attribution & licences

### Audio — CC0 1.0 Universal (public domain)

The demo track is from the album **"Un Toque De To"**, released into
the public domain under
[CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/).
The work has no rights reserved: you may copy, modify, distribute, and
perform it, even for commercial purposes, without asking permission.

| # | Title | Source |
|---|---|---|
| 07 | *Besame Otra Vez*   | https://archive.org/details/un-toque-de-to |

### Model — Gemma 4

This notebook uses [Gemma 4](https://ai.google.dev/gemma) via the
OpenAI-compatible endpoint at
`https://generativelanguage.googleapis.com/v1beta/openai/`.  The default
slug in the config cell is `google/gemma-4-e4b-it` — small enough to
host on Kaggle's free T4.

> **Note on the cached outputs shown above:** the pre-generated Gemma
> text bundled with this notebook was produced with the larger
> `gemma-4-26b-a4b-it` checkpoint, which gives noticeably richer
> coaching language than E4B.  Running the notebook in *live* mode with
> `google/gemma-4-e4b-it` (the default) will produce shorter, simpler
> outputs — still grounded by the same DSP analysis and verifiers.
> Set `GEMMA_MODEL = "google/gemma-4-26b-a4b-it"` in the config cell to
> reproduce the cached quality live.

See `docs/project-vision.md` in the repo for model-selection guidance.

### Code — Rytmi

Rytmi's source code (this notebook, prompts, DSP pipeline, verifiers)
is in the public repository
[**mukatee/rytmi-pub**](https://github.com/mukatee/rytmi-pub).  See
`LICENSE` there for terms.

### Demo video

End-to-end walkthrough on real-world (copyrighted) kizomba and bachata
tracks: <https://youtu.be/S3yNA6M_CFs>.  Educational use only; rights
remain with the original artists.

### Further reading

All links point to the public mirror at
[mukatee/rytmi-pub](https://github.com/mukatee/rytmi-pub).

- [`docs/kaggle_writeup.md`](https://github.com/mukatee/rytmi-pub/blob/master/docs/kaggle_writeup.md) —
  the Kaggle submission writeup, including the lessons-learned section
  on what worked and what didn't when prompting Gemma 4 for grounded
  music coaching (e.g. *"helper rationale text becomes echoed
  vocabulary"*, *"negative examples can backfire"*, *"code beats prompt
  prose for structural invariants"*).
- [`docs/how-it-works.md`](https://github.com/mukatee/rytmi-pub/blob/master/docs/how-it-works.md) —
  walkthrough of the DSP → prompt → Gemma architecture and the
  verifier layer.
- [`docs/project-vision.md`](https://github.com/mukatee/rytmi-pub/blob/master/docs/project-vision.md) —
  problem framing, model-selection guidance, and roadmap.
- [`docs/audio-sources.md`](https://github.com/mukatee/rytmi-pub/blob/master/docs/audio-sources.md) —
  how the CC0 demo track was chosen and licensing details for other
  audio paths.
- [`docs/experiments/`](https://github.com/mukatee/rytmi-pub/tree/master/docs/experiments) —
  dated phase notes capturing each iteration: prompt-tuning learnings,
  the kizomba batida tracker, the mel-filterbank gotcha, the drills
  verifier, the unified-timeline design, and the Gemma audio probe
  negative result.
"""))


# ----------------------------------------------------------------------
# Write notebook
# ----------------------------------------------------------------------
nb = nbf.v4.new_notebook()
nb.cells = CELLS
nb.metadata = {
    "kernelspec": {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    },
    "language_info": {
        "name": "python",
    },
}
nbf.write(nb, NB_PATH)
print(f"wrote {NB_PATH} ({len(CELLS)} cells)")
