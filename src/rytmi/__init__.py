"""Rytmi — rhythm learning prototype with DSP analysis and Gemma explanations."""

__version__ = "0.1.0"

from rytmi.audio import load_audio, normalize, trim_silence
from rytmi.dsp import analyze, detect_onsets, estimate_tempo, track_beats
from rytmi.viz import (
    interactive_timeline,
    plot_analysis,
    plot_beats,
    plot_onsets,
    plot_timeline,
    plot_waveform,
)

__all__ = [
    "load_audio",
    "trim_silence",
    "normalize",
    "analyze",
    "detect_onsets",
    "estimate_tempo",
    "track_beats",
    "interactive_timeline",
    "plot_analysis",
    "plot_beats",
    "plot_onsets",
    "plot_timeline",
    "plot_waveform",
    # llm — imported lazily in llm.py to avoid torch at import time
]
