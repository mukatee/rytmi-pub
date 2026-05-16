"""Cut a clean audio excerpt with optional fades.

Used by the demo recording flow to slice 5–15 second clips out of full songs
without re-encoding artifacts. Output format follows the file extension
(``.wav`` recommended for editor friendliness).

Example:
    python demo_assets/scripts/cut_excerpt.py \\
        --input "data/songs/eval_set/kizomba/Filomena_Maricoa_-_Teu_Toque_Official_Video [sKbWzD0mt6I].mp3" \\
        --start 32 --duration 10 \\
        --output demo_assets/output/filomena_hook.wav \\
        --fade-in 0.05 --fade-out 0.4
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def cut(
    input_path: Path,
    start: float,
    duration: float,
    output: Path,
    fade_in: float = 0.0,
    fade_out: float = 0.0,
) -> None:
    if shutil.which("ffmpeg") is None:
        sys.exit("ffmpeg not found on PATH")
    output.parent.mkdir(parents=True, exist_ok=True)
    filters: list[str] = []
    if fade_in > 0:
        filters.append(f"afade=t=in:st=0:d={fade_in}")
    if fade_out > 0:
        fade_start = max(0.0, duration - fade_out)
        filters.append(f"afade=t=out:st={fade_start}:d={fade_out}")
    cmd = [
        "ffmpeg", "-y",
        "-ss", f"{start}",
        "-t", f"{duration}",
        "-i", str(input_path),
    ]
    if filters:
        cmd += ["-af", ",".join(filters)]
    cmd += [str(output)]
    subprocess.run(cmd, check=True, capture_output=True)
    print(f"wrote {output}  (start={start}s, duration={duration}s)")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else "")
    p.add_argument("--input", required=True, type=Path)
    p.add_argument("--start", required=True, type=float, help="seconds")
    p.add_argument("--duration", required=True, type=float, help="seconds")
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--fade-in", type=float, default=0.0, help="seconds")
    p.add_argument("--fade-out", type=float, default=0.0, help="seconds")
    args = p.parse_args()
    cut(args.input, args.start, args.duration, args.output, args.fade_in, args.fade_out)


if __name__ == "__main__":
    main()
