"""Overlay metronome clicks on a song clip at librosa-detected beat times.

Used in Act 1 of the demo to show what an off-the-shelf beat tracker hears
on a kizomba track without any of Rytmi's added structure. The clicks are
mixed into the music at low volume so they read as a guide rather than
replacing the audio.

Pipeline:
    1. Load audio with librosa
    2. Run ``librosa.beat.beat_track`` (defaults — vanilla baseline)
    3. Synthesize a click track at those beat times
    4. Mix click track over the music at ``--click-volume`` (default 0.35)
    5. Write a single ``.wav`` ready to drop into the editor

Example:
    python demo_assets/scripts/make_click_overlay.py \\
        --input "data/songs/eval_set/kizomba/Filomena_Maricoa_-_Teu_Toque_Official_Video [sKbWzD0mt6I].mp3" \\
        --start 32 --duration 10 \\
        --output demo_assets/output/filomena_clicks.wav
"""

from __future__ import annotations

import argparse
import warnings
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf


def make_overlay(
    input_path: Path,
    output_path: Path,
    start: float = 0.0,
    duration: float | None = None,
    click_volume: float = 0.35,
    sample_rate: int = 22050,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        y, sr = librosa.load(
            str(input_path), sr=sample_rate, offset=start, duration=duration
        )
    tempo, beats_frames = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beats_frames, sr=sr)
    click = librosa.clicks(times=beat_times, sr=sr, length=len(y), click_freq=2000.0)
    # Normalize music to ~0.85 peak, then add scaled click.
    peak = float(np.max(np.abs(y))) or 1.0
    music = y * (0.85 / peak)
    mixed = music + click_volume * click
    # Soft-limit any final overshoot.
    final_peak = float(np.max(np.abs(mixed))) or 1.0
    if final_peak > 0.99:
        mixed = mixed * (0.99 / final_peak)
    sf.write(str(output_path), mixed, sr)
    tempo_val = float(tempo) if np.isscalar(tempo) else float(tempo.item())
    print(
        f"wrote {output_path}  (tempo={tempo_val:.1f} BPM, "
        f"{len(beat_times)} clicks over {len(y) / sr:.2f}s)"
    )


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else "")
    p.add_argument("--input", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--start", type=float, default=0.0, help="seconds (default 0)")
    p.add_argument("--duration", type=float, default=None, help="seconds (default: full)")
    p.add_argument("--click-volume", type=float, default=0.35, help="0..1 (default 0.35)")
    p.add_argument("--sample-rate", type=int, default=22050)
    args = p.parse_args()
    make_overlay(
        args.input, args.output,
        start=args.start, duration=args.duration,
        click_volume=args.click_volume, sample_rate=args.sample_rate,
    )


if __name__ == "__main__":
    main()
