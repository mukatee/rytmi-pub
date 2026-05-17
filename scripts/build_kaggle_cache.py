"""Build cached DSP + Gemma outputs for the Kaggle demo notebook.

Reads CC0 audio from ``data/samples/kizomba_cc/`` and writes:

- ``notebooks/cache/cc0_<slug>.pkl``           — pickled RhythmAnalysis
- ``notebooks/cache/cc0_<slug>_outputs.json``  — dict of prompt_name → text
- ``notebooks/cache/cc0_<slug>_timeline.png``  — static timeline visualization
- ``notebooks/cache/cc0_<slug>_waveform.png``  — waveform + beats visualization

Usage:
    python scripts/build_kaggle_cache.py            # all tracks
    python scripts/build_kaggle_cache.py --only 09  # one track (slug prefix match)
    python scripts/build_kaggle_cache.py --skip-llm # DSP + viz only

Gemma endpoint is configured via ``RYTMI_API_BASE_URL`` and ``RYTMI_API_KEY``
(plus ``RYTMI_MODEL_ID``).  Defaults to Ollama gemma3:4b on localhost.
"""

from __future__ import annotations

import argparse
import json
import os
import pickle
from dataclasses import asdict, is_dataclass
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from rytmi import analyze, load_audio, plot_beats
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

REPO = Path(__file__).resolve().parent.parent
AUDIO_DIR = REPO / "data" / "samples" / "kizomba_cc"
CACHE_DIR = REPO / "notebooks" / "cache"

TRACKS = [
    {"slug": "09_te_quiero_amor", "title": "Te Quiero Amor",       "bpm_hint": 95.7},
    {"slug": "07_besame_otra_vez", "title": "Besame Otra Vez",     "bpm_hint": 117.5},
    {"slug": "06_en_talla",        "title": "En Talla",            "bpm_hint": 117.5},
]

# Budget includes the 26B model's internal reasoning (~2000-6000 tokens) plus
# the visible answer.  The amount of internal thinking varies per call, so we
# leave generous headroom and additionally retry with a doubled budget if the
# first attempt comes back empty (length-truncated mid-think).  Smaller models
# (e.g. gemma3:4b on Kaggle) ignore the unused headroom.
PROMPTS = [
    ("rhythm_anatomy",      QUESTION_RHYTHM_ANATOMY,      8192),
    ("listening_guide",     QUESTION_LISTENING_GUIDE,     8192),
    ("song_arc",            QUESTION_SONG_ARC,            8192),
    ("kizomba_tutor",       QUESTION_KIZOMBA_TUTOR,       8192),
    ("kizomba_drills",      QUESTION_KIZOMBA_DRILLS,      8192),
    ("kizomba_transitions", QUESTION_KIZOMBA_TRANSITIONS, 8192),
]


def _save_pickle(obj, path: Path) -> None:
    with open(path, "wb") as f:
        pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)


def _render_waveform_png(analysis, out_path: Path, title: str) -> None:
    fig, ax = plt.subplots(figsize=(12, 3))
    plot_beats(analysis.audio, analysis.beats, ax=ax)
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(out_path, dpi=110)
    plt.close(fig)


def _render_timeline_png(analysis, out_path: Path, title: str) -> None:
    """Static timeline showing phases as colored bars on the time axis."""
    phases = getattr(analysis, "phases", None) or []
    sections = getattr(analysis, "sections", None) or []

    fig, ax = plt.subplots(figsize=(12, 2.4))
    duration = analysis.audio.duration

    # Plot sections as bottom bar
    if sections:
        ax.broken_barh(
            [(s.start_s, s.end_s - s.start_s) for s in sections],
            (0.1, 0.35),
            facecolors=["#9ecae1" if i % 2 == 0 else "#c6dbef" for i in range(len(sections))],
            edgecolor="#2171b5",
        )
        for s in sections:
            ax.text(
                (s.start_s + s.end_s) / 2, 0.27, s.label,
                ha="center", va="center", fontsize=8,
            )
        ax.text(-0.5, 0.27, "sections", ha="right", va="center", fontsize=8)

    # Phases as upper bar
    if phases:
        ax.broken_barh(
            [(p.start_s, p.end_s - p.start_s) for p in phases],
            (0.6, 0.35),
            facecolors=["#fdae6b" if i % 2 == 0 else "#fdd0a2" for i in range(len(phases))],
            edgecolor="#e6550d",
        )
        for p in phases:
            label = getattr(p, "role", None) or getattr(p, "label", "phase")
            ax.text(
                (p.start_s + p.end_s) / 2, 0.77, str(label),
                ha="center", va="center", fontsize=8,
            )
        ax.text(-0.5, 0.77, "phases", ha="right", va="center", fontsize=8)

    ax.set_xlim(0, duration)
    ax.set_ylim(0, 1.1)
    ax.set_yticks([])
    ax.set_xlabel("Time (s)")
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(out_path, dpi=110)
    plt.close(fig)


def _analysis_meta(analysis) -> dict:
    """Compact summary of a RhythmAnalysis (json-safe)."""
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


def process_track(track: dict, *, processor, model_id: str | None, skip_llm: bool) -> None:
    slug = track["slug"]
    title = track["title"]
    mp3 = AUDIO_DIR / f"{slug}.mp3"
    if not mp3.exists():
        print(f"  SKIP {slug}: {mp3} not found")
        return

    print(f"\n=== {slug} ({title}) ===")
    print(f"  loading {mp3.name} …")
    audio = load_audio(str(mp3))
    print(f"  analyzing (style=kizomba) …")
    analysis = analyze(audio, dance_style="kizomba")
    print(
        f"    tempo={analysis.tempo:.1f} BPM  "
        f"beats={len(analysis.beats.times)}  "
        f"sections={len(getattr(analysis, 'sections', []) or [])}  "
        f"phases={len(getattr(analysis, 'phases', []) or [])}  "
        f"downbeat_conf={getattr(analysis, 'downbeat_confidence', 0.0):.2f}"
    )

    pkl_path = CACHE_DIR / f"cc0_{slug}.pkl"
    _save_pickle(analysis, pkl_path)
    print(f"  wrote {pkl_path.relative_to(REPO)}")

    wf_path = CACHE_DIR / f"cc0_{slug}_waveform.png"
    _render_waveform_png(analysis, wf_path, f"{title} — waveform + beats")
    print(f"  wrote {wf_path.relative_to(REPO)}")

    tl_path = CACHE_DIR / f"cc0_{slug}_timeline.png"
    _render_timeline_png(analysis, tl_path, f"{title} — phases / sections")
    print(f"  wrote {tl_path.relative_to(REPO)}")

    outputs: dict[str, str] = {"_meta": _analysis_meta(analysis)}

    if not skip_llm and processor is not None and model_id is not None:
        for name, question, max_tok in PROMPTS:
            print(f"  Gemma → {name} (max_tokens={max_tok}) …")
            text = ""
            for attempt_tok in (max_tok, max_tok * 2):
                try:
                    text = explain_rhythm(
                        analysis,
                        question=question,
                        processor=processor,
                        model=model_id,
                        max_new_tokens=attempt_tok,
                        temperature=0.5,
                    )
                except Exception as e:  # noqa: BLE001
                    text = f"[ERROR generating {name}: {e}]"
                    print(f"    ERROR: {e}")
                    break
                if text.strip():
                    break
                print(f"    empty at {attempt_tok} tokens, retrying with {attempt_tok * 2} …")
            outputs[name] = text
            preview = text.replace("\n", " ")[:90]
            print(f"    got {len(text)} chars  | {preview}…")

        # Transitions table + unified timeline (tutor + transitions text)
        outputs["_transitions_describe"] = describe_transitions(analysis)
        if "kizomba_tutor" in outputs and "kizomba_transitions" in outputs:
            outputs["unified_timeline"] = format_unified_timeline(
                outputs["kizomba_tutor"], outputs["kizomba_transitions"]
            )

    json_path = CACHE_DIR / f"cc0_{slug}_outputs.json"
    with open(json_path, "w") as f:
        json.dump(outputs, f, indent=2, default=str)
    print(f"  wrote {json_path.relative_to(REPO)}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Build Kaggle demo cache")
    ap.add_argument("--only", default=None, help="Slug prefix to filter (e.g. 09)")
    ap.add_argument("--skip-llm", action="store_true", help="DSP + viz only, skip Gemma")
    args = ap.parse_args()

    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    processor = None
    model_id = None
    if not args.skip_llm:
        model_id = os.environ.get("RYTMI_MODEL_ID", "gemma3:4b")
        base_url = os.environ.get("RYTMI_API_BASE_URL", "http://localhost:11434/v1")
        print(f"Gemma endpoint: {base_url}  model={model_id}")
        processor, model_id = load_cloud_model(model_id=model_id, base_url=base_url)

    tracks = TRACKS
    if args.only:
        tracks = [t for t in TRACKS if t["slug"].startswith(args.only)]
        if not tracks:
            print(f"No tracks match --only {args.only}")
            return 1

    for t in tracks:
        process_track(t, processor=processor, model_id=model_id, skip_llm=args.skip_llm)

    print("\nDone.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
