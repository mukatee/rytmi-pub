"""One-shot generator for notebooks/_build_kaggle_cache.ipynb.

Run once with the project venv:

    .venv/bin/python scripts/_make_cache_notebook.py

The generated notebook is the runnable counterpart of
``scripts/build_kaggle_cache.py`` — same outputs, same prompt list,
same retry-on-empty behavior — but split into per-track cells so the
user can run it against a fast cloud Gemma endpoint and re-run
individual cells if any prompt comes back empty.

Cache files (overwritten in ``notebooks/cache/``):

- ``cc0_<slug>.pkl``           — pickled RhythmAnalysis
- ``cc0_<slug>_waveform.png``  — beats over waveform
- ``cc0_<slug>_timeline.png``  — phases + sections bar chart
- ``cc0_<slug>_outputs.json``  — dict of prompt_name → text + _meta
"""

from __future__ import annotations

import nbformat as nbf
from pathlib import Path

NB_PATH = Path(__file__).resolve().parent.parent / "notebooks" / "_build_kaggle_cache.ipynb"

TRACKS = [
    ("09_te_quiero_amor", "Te Quiero Amor"),
    ("07_besame_otra_vez", "Besame Otra Vez"),
    ("06_en_talla",        "En Talla"),
]


def md(src: str):
    return nbf.v4.new_markdown_cell(src)


def code(src: str):
    return nbf.v4.new_code_cell(src)


CELLS = []

CELLS.append(md("""\
# Build Kaggle demo cache

Runs DSP + Gemma over the three CC0 kizomba tracks staged in
`data/samples/kizomba_cc/` and writes the cache files consumed by
`notebooks/kaggle_demo.ipynb` (the judge-facing notebook).

This notebook is the runnable counterpart of
`scripts/build_kaggle_cache.py` — same prompts, same budgets, same
retry-on-empty behavior — split into per-track cells so you can re-run
just the prompts that came back empty.

**Config (env)** — set in the kernel before launching:

- `RYTMI_API_BASE_URL` — OpenAI-compatible endpoint (default
  `http://localhost:11434/v1`)
- `RYTMI_API_KEY` — API key (use `ollama` for local Ollama)
- `RYTMI_MODEL_ID` — model id (e.g. `gemma4:26b`)

Outputs land in `notebooks/cache/cc0_*` and are git-ignored by the
existing `notebooks/cache/` rule (the kaggle_demo notebook reads them
through helper functions, not as git artifacts).
"""))

CELLS.append(code("""\
# Imports + paths + config
from __future__ import annotations
import os, json, pickle, time
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt

from rytmi import analyze, load_audio
from rytmi.dsp import describe_sections, describe_transitions
from rytmi.llm import explain_rhythm, load_cloud_model
from rytmi.prompts import (
    QUESTION_KIZOMBA_DRILLS,
    QUESTION_KIZOMBA_TRANSITIONS,
    QUESTION_KIZOMBA_TUTOR,
    QUESTION_LISTENING_GUIDE,
    QUESTION_RHYTHM_ANATOMY,
    QUESTION_SONG_ARC,
    format_unified_timeline,
)

REPO = Path.cwd().resolve()
# When the notebook is opened from notebooks/ jump up one level.
if REPO.name == "notebooks":
    REPO = REPO.parent

AUDIO_DIR = REPO / "data" / "samples" / "kizomba_cc"
CACHE_DIR = REPO / "notebooks" / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

API_BASE = os.environ.get("RYTMI_API_BASE_URL", "http://localhost:11434/v1")
API_KEY  = os.environ.get("RYTMI_API_KEY", "ollama")
MODEL_ID = os.environ.get("RYTMI_MODEL_ID", "gemma4:26b")

print(f"repo       = {REPO}")
print(f"audio dir  = {AUDIO_DIR}  (exists={AUDIO_DIR.exists()})")
print(f"cache dir  = {CACHE_DIR}")
print(f"api base   = {API_BASE}")
print(f"model id   = {MODEL_ID}")
"""))

CELLS.append(code("""\
# Prompt menu — 6 outputs per track.
# Budget is generous because the 26B model reserves a large chunk of the
# token window for internal reasoning before producing visible content.
# Smaller models simply ignore the unused headroom.
PROMPTS = [
    ("rhythm_anatomy",      QUESTION_RHYTHM_ANATOMY,      8192),
    ("listening_guide",     QUESTION_LISTENING_GUIDE,     8192),
    ("song_arc",            QUESTION_SONG_ARC,            8192),
    ("kizomba_tutor",       QUESTION_KIZOMBA_TUTOR,       8192),
    ("kizomba_drills",      QUESTION_KIZOMBA_DRILLS,      8192),
    ("kizomba_transitions", QUESTION_KIZOMBA_TRANSITIONS, 8192),
]

TRACKS = [
    {"slug": "09_te_quiero_amor", "title": "Te Quiero Amor"},
    {"slug": "07_besame_otra_vez", "title": "Besame Otra Vez"},
    {"slug": "06_en_talla",        "title": "En Talla"},
]
"""))

CELLS.append(code("""\
# Helpers — pickle, timeline png, meta, json IO
#
# We deliberately do NOT cache a static waveform PNG.  The demo notebook
# renders the scrolling+audio widget at display time via
# ``rytmi.viz.interactive_timeline(analysis)`` (same approach as
# notebooks/00_demo.ipynb and notebooks/09_kizomba_extended.ipynb).  The
# only cached image is the static phases/sections timeline used as a
# lightweight fallback.

def _save_pickle(obj, path):
    with open(path, "wb") as f:
        pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)


def _render_timeline_png(analysis, out_path, title):
    phases = getattr(analysis, "phases", None) or []
    sections = getattr(analysis, "sections", None) or []
    fig, ax = plt.subplots(figsize=(12, 2.4))
    duration = analysis.audio.duration
    if sections:
        ax.broken_barh(
            [(s.start_s, s.end_s - s.start_s) for s in sections],
            (0.1, 0.35),
            facecolors=["#9ecae1" if i % 2 == 0 else "#c6dbef"
                        for i in range(len(sections))],
            edgecolor="#2171b5",
        )
        for s in sections:
            ax.text((s.start_s + s.end_s) / 2, 0.27, s.label,
                    ha="center", va="center", fontsize=8)
    if phases:
        ax.broken_barh(
            [(p.start_s, p.end_s - p.start_s) for p in phases],
            (0.6, 0.35),
            facecolors=["#fdae6b" if i % 2 == 0 else "#fdd0a2"
                        for i in range(len(phases))],
            edgecolor="#e6550d",
        )
        for p in phases:
            label = getattr(p, "role", None) or getattr(p, "label", "phase")
            ax.text((p.start_s + p.end_s) / 2, 0.77, str(label),
                    ha="center", va="center", fontsize=8)
    ax.set_xlim(0, duration)
    ax.set_ylim(0, 1.1)
    ax.set_yticks([])
    ax.set_xlabel("Time (s)")
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(out_path, dpi=110)
    plt.close(fig)


def _analysis_meta(analysis):
    sections = getattr(analysis, "sections", None) or []
    phases = getattr(analysis, "phases", None) or []
    return {
        "duration_s": float(analysis.audio.duration),
        "tempo": float(analysis.tempo),
        "n_beats": int(len(analysis.beats.times)),
        "n_onsets": int(len(analysis.onsets.times)),
        "downbeat_confidence": float(getattr(analysis, "downbeat_confidence", 0.0) or 0.0),
        "beats_per_measure": int(getattr(analysis, "beats_per_measure", 4) or 4),
        "phrase_length": int(getattr(analysis, "phrase_length", 4) or 4),
        "n_sections": int(len(sections)),
        "n_phases": int(len(phases)),
        "sections_describe": describe_sections(analysis),
    }


def _outputs_path(slug):
    return CACHE_DIR / f"cc0_{slug}_outputs.json"


def _load_outputs(slug):
    p = _outputs_path(slug)
    if p.exists():
        return json.loads(p.read_text())
    return {}


def _save_outputs(slug, outputs):
    p = _outputs_path(slug)
    p.write_text(json.dumps(outputs, indent=2, default=str))
    return p
"""))

CELLS.append(code("""\
# Load the cloud client once and keep it around.
client, model_id = load_cloud_model(
    model_id=MODEL_ID,
    base_url=API_BASE,
    api_key=API_KEY,
    print_url=True,
)
print(f"model ready: {model_id}")
"""))

CELLS.append(md("""\
## 1) DSP pass — analyze all three tracks

Loads each MP3 with the kizomba style hint, writes the pickle and the
two PNGs.  Cheap (~10-30 seconds per track) and idempotent — safe to
re-run.
"""))

CELLS.append(code("""\
analyses = {}

for t in TRACKS:
    slug, title = t["slug"], t["title"]
    mp3 = AUDIO_DIR / f"{slug}.mp3"
    if not mp3.exists():
        print(f"  SKIP {slug}: {mp3} not found")
        continue
    print(f"=== {slug} ({title}) ===")
    audio = load_audio(str(mp3))
    analysis = analyze(audio, dance_style="kizomba")
    print(f"    tempo={analysis.tempo:.1f} BPM  "
          f"beats={len(analysis.beats.times)}  "
          f"sections={len(getattr(analysis, 'sections', []) or [])}  "
          f"phases={len(getattr(analysis, 'phases', []) or [])}  "
          f"downbeat_conf={getattr(analysis, 'downbeat_confidence', 0.0):.2f}")

    pkl = CACHE_DIR / f"cc0_{slug}.pkl"
    _save_pickle(analysis, pkl); print(f"    wrote {pkl.name}")

    tl = CACHE_DIR / f"cc0_{slug}_timeline.png"
    _render_timeline_png(analysis, tl, f"{title} — phases / sections")
    print(f"    wrote {tl.name}")

    # Seed the outputs json with the meta block (preserve any prompt
    # outputs already cached from a previous run).
    outputs = _load_outputs(slug)
    outputs["_meta"] = _analysis_meta(analysis)
    outputs["_transitions_describe"] = describe_transitions(analysis)
    _save_outputs(slug, outputs)

    analyses[slug] = analysis

print()
print("DSP done for:", list(analyses))
"""))

CELLS.append(md("""\
## 2) Gemma pass — per-track cells

Each cell loops over the 6 prompts and writes
`cc0_<slug>_outputs.json`.  On an empty response it retries once with
double the token budget (the 26B reasoning trace occasionally consumes
the whole window before producing visible content).  Re-running the
cell only re-asks prompts that are currently empty or missing, so
you can safely retry until everything is filled.
"""))


def _gemma_cell(slug: str, title: str) -> str:
    return f"""\
# {title} — Gemma prompts
slug = {slug!r}
title = {title!r}

analysis = analyses.get(slug)
if analysis is None:
    pkl = CACHE_DIR / f"cc0_{{slug}}.pkl"
    with open(pkl, "rb") as f:
        analysis = pickle.load(f)
    print(f"loaded analysis from {{pkl.name}}")

outputs = _load_outputs(slug)

for name, question, max_tok in PROMPTS:
    existing = outputs.get(name, "")
    if existing and existing.strip() and not existing.startswith("[ERROR"):
        print(f"  SKIP {{name}}: already cached ({{len(existing)}} chars)")
        continue
    print(f"  Gemma → {{name}} (max_tokens={{max_tok}}) …", flush=True)
    t0 = time.time()
    text = ""
    try:
        for attempt_tok in (max_tok, max_tok * 2):
            text = explain_rhythm(
                analysis,
                question=question,
                processor=client,
                model=model_id,
                max_new_tokens=attempt_tok,
                temperature=0.5,
            )
            if text.strip():
                break
            print(f"    empty at {{attempt_tok}} tokens, retrying with {{attempt_tok * 2}} …",
                  flush=True)
    except Exception as e:
        text = f"[ERROR generating {{name}}: {{e}}]"
        print(f"    ERROR: {{e}}")
    outputs[name] = text
    _save_outputs(slug, outputs)  # save after each prompt so partial work is preserved
    dt = time.time() - t0
    preview = text.replace("\\n", " ")[:90]
    print(f"    got {{len(text)}} chars in {{dt:.1f}}s  | {{preview}}…")

# Unified timeline (only if both inputs present)
if outputs.get("kizomba_tutor") and outputs.get("kizomba_transitions"):
    outputs["unified_timeline"] = format_unified_timeline(
        outputs["kizomba_tutor"], outputs["kizomba_transitions"],
    )
    _save_outputs(slug, outputs)
    print(f"  wrote unified_timeline ({{len(outputs['unified_timeline'])}} chars)")
"""


for slug, title in TRACKS:
    CELLS.append(md(f"### {title} (`{slug}`)"))
    CELLS.append(code(_gemma_cell(slug, title)))

CELLS.append(md("""\
## 3) Verify

Lists every cache file with size and prompt fill rate.
"""))

CELLS.append(code("""\
for t in TRACKS:
    slug = t["slug"]
    print(f"--- {slug} ---")
    for suffix in (".pkl", "_waveform.png", "_timeline.png", "_outputs.json"):
        p = CACHE_DIR / f"cc0_{slug}{suffix}"
        if p.exists():
            print(f"  {p.name}  ({p.stat().st_size:,} bytes)")
        else:
            print(f"  MISSING: {p.name}")
    outs = _load_outputs(slug)
    filled = [k for k, v in outs.items()
              if k not in {"_meta", "_transitions_describe"}
              and isinstance(v, str) and v.strip()
              and not v.startswith("[ERROR")]
    missing = [k for k, _q, _b in PROMPTS if k not in filled]
    print(f"  prompts filled : {len(filled)}/{len(PROMPTS)} {filled}")
    if missing:
        print(f"  STILL MISSING  : {missing}")
"""))


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
