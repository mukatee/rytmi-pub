"""Render the full set of timeline videos for the Rytmi demo.

For each entry in ``CLIPS`` below, calls
:func:`make_timeline_video.render_timeline_video` to produce one MP4 with a
moving playhead and synced audio. Output goes to
``demo_assets/output/timeline_*.mp4``.

Picks of clips are aligned with the Gemma audio probe (Phase 43) plus a
couple of pieces that show off section transitions and a clean break — so
the demo can compare the same musical material across:
  - DSP timeline (this script's videos)
  - Gemma textual analysis (overlay text in PowerPoint)
  - Gemma raw-audio attempt (Phase 43 negative result)

Skips any clip whose source file is missing instead of aborting — useful
when running on a machine that has only some of the eval set.

Usage from repo root:
    .venv/bin/python demo_assets/scripts/make_all_demo_videos.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "demo_assets" / "scripts"))

from make_timeline_video import (  # noqa: E402
    prepare_analysis,
    render_from_analysis,
)


# Each clip is rendered twice from the same analysis: an uncaptioned
# `timeline_<stem>.mp4` and a captioned sibling `timeline_<stem>_captioned.mp4`.
# Captions, where possible, are *verbatim Gemma output* from
# notebooks/09_kizomba_extended_outputs.post-40e.md (kizomba_transitions
# verified pass) so the audience hears Gemma's own coaching voice on screen.
# A few captions are hybrid where the notebook output is older than a recent
# DSP fix (e.g. Phase 42); those are flagged in inline comments.
#
# Title convention: "<artist> — *<song>* (<what's happening>)" — artist-first,
# no dancer-pair labels (those go in the writeup, not on screen).
CLIPS: list[dict] = [
    {
        # Window shifted from 32–42 s so it now contains T1 (intro→main at 12s)
        # and the first half of P2 (steady main). Caption is Gemma's verbatim
        # T1 transition cue from the kizomba_transitions verified pass.
        "src": "data/songs/eval_set/kizomba/Filomena_Maricoa_-_Teu_Toque_Official_Video [sKbWzD0mt6I].mp3",
        "stem": "filomena_intro_to_main",
        "title": "Filomena Maricoa — Teu Toque (intro → main)",
        "start": 8.0, "duration": 14.0, "style": "kizomba",
        "caption": (
            "T1: 12s  [intro → main, beat: clear → clear]\n"
            "— when the bass kicks in, walk-step the basic on the first clear bass hit."
        ),
    },
    {
        # Hybrid caption: the notebook's Gemma run is pre-Phase-42 and would
        # mislabel this as intro→break. The clip's whole point is to show the
        # post-Phase-42 'main' label landing on the singer's entry, so the
        # caption tells the DSP-fix story directly. (Re-running notebook 09
        # against current code would give a verbatim Gemma line; tracked.)
        "src": "data/songs/eval_set/kizomba/Charbel_-_E_Magia_Official_Video_4K [QkfyDj8aJRM].mp3",
        "stem": "e_magia_intro_to_main",
        "title": "Charbel — E Magia (intro → vocal entry)",
        "start": 30.0, "duration": 14.0, "style": "kizomba",
        "caption": (
            "Singer enters around ~36s — section is now labelled 'main', not 'break'.\n"
            "Phase 42 demoted vocal-active false breaks; the genuine break is later in the song."
        ),
    },
    {
        # Verbatim Gemma T5 transition from the verified pass. Window contains
        # the actual main→break boundary at 165s.
        "src": "data/songs/eval_set/kizomba/Charbel_-_E_Magia_Official_Video_4K [QkfyDj8aJRM].mp3",
        "stem": "e_magia_vocal_break",
        "title": "Charbel — E Magia (genuine vocal-led break)",
        "start": 159.0, "duration": 14.0, "style": "kizomba",
        "caption": (
            "T5: 165s  [main → break, beat: clear → moderate]\n"
            "— as the energy fades and the percussion thins, keep a small pulse in the body and listen."
        ),
    },
    {
        # Verbatim Gemma T8 transition from the verified pass. Window contains
        # the main→break at 141s.
        "src": "data/songs/eval_set/kizomba/Charbel_-_E_Magia_Ben_Ana [6McenE8gUqM].mp3",
        "stem": "e_magia_alt_break",
        "title": "Charbel — E Magia (alt edit, vocal-led break)",
        "start": 135.0, "duration": 14.0, "style": "kizomba",
        "caption": (
            "T8: 141s  [main → break, beat: clear → moderate]\n"
            "— as the energy fades and the percussion thins, keep a small pulse, listen, and reset."
        ),
    },
    {
        # Window shifted from 125–135 s to 130–142 s so the actual T5
        # main→break boundary at 138s sits inside the frame. Caption is the
        # verbatim Gemma T5 cue.
        "src": "data/songs/eval_set/kizomba/Tony_Pirata_Lydia_Laprade_Filomena_Maricoa_-_Teu_Toque [B0l0VHVSBTQ].mp3",
        "stem": "teu_toque_alt_pre_break",
        "title": "Filomena Maricoa — Teu Toque (alt edit, pre-break build)",
        "start": 130.0, "duration": 14.0, "style": "kizomba",
        "caption": (
            "T5: 138s  [main → break, beat: clear → clear]\n"
            "— keep a small pulse in the body and listen as the energy fades and the percussion thins."
        ),
    },
    # ── Phase 2: bachata + variety. Captions are verbatim Gemma output from
    # the bachata_transitions / kizomba_transitions verified pass run via
    # demo_assets/scripts/harvest_transitions.py (see tmp/phase2_transitions.md).
    {
        # T2 break→main at 38s. Romeo's iconic spoken-intro-to-bongo-entry
        # moment, and the demo's clearest "land the 1" payoff.
        "src": "data/songs/eval_set/bachata/Romeo_Santos_-_Propuesta_Indecente_Official_Video [QFs3PIZb3js].mp3",
        "stem": "romeo_propuesta_break_to_main",
        "title": "Romeo Santos — Propuesta Indecente (break → main, bongo entry)",
        "start": 31.0, "duration": 14.0, "style": "bachata",
        "caption": (
            "T2: 38s  [break → main, beat: moderate → moderate]\n"
            "— Restart your 1-2-3-tap on the next clear 1 when the bongo pattern kicks in."
        ),
    },
    {
        # T4 main→outro at 194s. Richest line in the harvest — names a
        # specific bachata audible cue (güira drop) plus the count anchor.
        "src": "data/songs/eval_set/bachata/Prince_Royce_-_Corazon_Sin_Cara_Official_Video [XNGWDH-6yv8].mp3",
        "stem": "royce_corazon_main_to_outro",
        "title": "Prince Royce — Corazón Sin Cara (main → outro, güira drops)",
        "start": 187.0, "duration": 14.0, "style": "bachata",
        "caption": (
            "T4: 194s  [main → outro, beat: moderate → clear]\n"
            "— Contract your movement and finish on a clean 8 as the percussion thins and the güira drops out."
        ),
    },
    {
        # T2 short_break→main at 34s. Mirrors the Filomena T1 "bass kicks
        # in" pattern across a different kizomba track for the
        # comparison-across-songs angle.
        "src": "data/songs/eval_set/kizomba/MIKA_MENDES_-_MAGICO_2011 [ZM1GnUImrPw].mp3",
        "stem": "mika_magico_break_to_main",
        "title": "Mika Mendes — Mágico (short break → main, bass entry)",
        "start": 27.0, "duration": 14.0, "style": "kizomba",
        "caption": (
            "T2: 34s  [short_break → main, beat: clear → clear]\n"
            "— when the bass kicks in, start your steady walk-step."
        ),
    },
]


def main() -> int:
    out_dir = ROOT / "demo_assets" / "output"
    out_dir.mkdir(parents=True, exist_ok=True)

    rendered: list[Path] = []
    skipped: list[str] = []

    # Group clips by source file so Demucs/analyze runs once per song.
    by_src: dict[str, list[dict]] = {}
    for clip in CLIPS:
        by_src.setdefault(clip["src"], []).append(clip)

    for rel_path, clips in by_src.items():
        candidates = sorted(ROOT.glob(rel_path)) or [ROOT / rel_path]
        song = next((p for p in candidates if p.exists()), None)
        if song is None:
            print(f"SKIP (not found): {rel_path}", file=sys.stderr)
            for clip in clips:
                skipped.append(clip["stem"])
            continue

        print(f"\n=== analyzing {song.name} (used by {len(clips)} clip(s)) ===")
        try:
            audio, analysis = prepare_analysis(
                song, dance_style=clips[0]["style"],
            )
        except Exception as exc:
            print(f"FAIL analyze {song.name}: {exc}", file=sys.stderr)
            for clip in clips:
                skipped.append(clip["stem"])
            continue

        for clip in clips:
            stem = clip["stem"]
            for variant, caption in (("plain", None), ("captioned", clip["caption"])):
                suffix = "" if variant == "plain" else "_captioned"
                out_path = out_dir / f"timeline_{stem}{suffix}.mp4"
                print(f"\n--- {stem} ({variant}) ---")
                try:
                    render_from_analysis(
                        song, audio, analysis,
                        clip["start"], clip["duration"], out_path,
                        title=clip["title"], fps=30, caption=caption,
                    )
                    rendered.append(out_path)
                except Exception as exc:
                    print(f"FAIL {stem} ({variant}): {exc}", file=sys.stderr)

    print("\n--- SUMMARY ---")
    for p in rendered:
        kb = p.stat().st_size / 1024
        print(f"  {p.relative_to(ROOT)}  ({kb:.0f} KB)")
    if skipped:
        print(f"  {len(skipped)} skipped (missing source files or analyze failure)")

    return 0 if rendered else 1


if __name__ == "__main__":
    raise SystemExit(main())
