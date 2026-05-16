"""Shared data types for the Rytmi pipeline."""

from dataclasses import dataclass, field

import numpy as np
from numpy.typing import NDArray


@dataclass
class AudioData:
    """Raw audio signal with metadata."""

    samples: NDArray[np.float32]
    sr: int
    duration: float
    filepath: str | None = None


@dataclass
class OnsetData:
    """Detected onset events."""

    times: NDArray[np.float64]
    strength: NDArray[np.float64]
    sr: int


@dataclass
class BeatData:
    """Tracked beats and tempo."""

    times: NDArray[np.float64]
    tempo: float
    beat_frames: NDArray[np.intp]


@dataclass
class VocalsInfo:
    """Result of the Gemma audio perception pass.

    Produced by ``rytmi.transcribe.transcribe_vocals``.  The reasoning stage
    consumes only ``language`` (and optionally ``lyric_snippet`` in lyrics
    mode); the other fields are kept for logging and experiment reproducibility.
    """

    language: str  # lowercase English name, "instrumental", or "unknown"
    lyric_snippet: str = ""
    clip_start_s: float = 0.0
    clip_duration_s: float = 0.0
    raw_response: str = ""


@dataclass
class RhythmFeatures:
    """Computed rhythm features for style disambiguation.

    These give Gemma concrete numbers instead of vague instructions
    like "use onset density as a tiebreaker".
    """

    onsets_per_beat: float
    beat_strength_pattern: list[float]
    percussiveness: float
    spectral_centroid_mean: float
    tempo_stability: float
    ioi_median_ms: float
    ioi_std_ms: float
    beat_clarity: float = 0.0  # 0.0 = hard to hear, 1.0 = very clear pulse


@dataclass
class StyleProfile:
    """Per-style interpretation knowledge for dance coaching.

    DSP segmentation is style-agnostic.  The style profile controls how
    detected sections and beat-accent patterns are *interpreted* for a
    specific dance style (e.g. a "break" means "mambo footwork" in bachata
    but "pause and hold" in kizomba).
    """

    name: str
    bpm_range: tuple[int, int]
    section_coaching: dict[str, str]
    accent_hints: dict[str, str]
    general_context: str
    basic_step: str = ""


@dataclass
class SongSection:
    """A rhythmically distinct segment of a song.

    Dancer-relevant zones (intro, main, break, build, peak, outro) rather than
    music-theory labels (verse, chorus, bridge).  Each section carries its own
    ``RhythmFeatures`` and a human-readable accent description.

    ``raw_start_s`` / ``raw_end_s`` preserve the pre-snap boundaries when
    phrase-grid snapping is enabled, so diagnostics can show the drift that
    was corrected.  They are None when snapping did not move the boundary.

    ``harm_ratio`` / ``perc_ratio`` are segment-RMS-over-global-mean for the
    harmonic / percussive components from ``librosa.effects.hpss``.  They feed
    the four-branch break classifier and are shown as ``H×`` / ``P×`` columns
    in ``describe_sections``.  ``break_branch`` names which branch fired on a
    break row (``"melodic"``, ``"percussive"``, ``"severe"``, ``"full"``) or
    stays ``None`` on non-break sections.
    """

    start_s: float
    end_s: float
    label: str  # intro, main, break, build, peak, outro
    energy_level: str  # low, medium, high
    rhythm_features: RhythmFeatures | None = None
    accent_description: str = ""
    raw_start_s: float | None = None
    raw_end_s: float | None = None
    harm_ratio: float | None = None
    perc_ratio: float | None = None
    break_branch: str | None = None
    vocal_ratio: float | None = None  # fraction of frames vocal-active in [start_s, end_s)


@dataclass
class SongPhase:
    """Merged consecutive same-label sections for display.

    Phases collapse runs of e.g. main, main, main into a single
    ``main ×3`` entry.  Raw ``SongSection`` detail stays on
    ``RhythmAnalysis.sections`` for Gemma to reason over.
    """

    label: str
    start_s: float
    end_s: float
    section_count: int
    energy_levels: list[str] = field(default_factory=list)
    avg_rhythm_features: RhythmFeatures | None = None


@dataclass
class Transition:
    """A label boundary between two consecutive phases.

    Phase 40 — coaching surface for the moments *between* sections.  Where
    ``kizomba_tutor`` and ``kizomba_drills`` give per-phase steady-state
    coaching, transitions cover the anticipation cue (last 8-count of the
    incoming section), the moment of the boundary itself, and the re-entry
    cue (first 8-count of the outgoing section).

    Built by ``rytmi.dsp.extract_transitions`` from a phase list — only
    label changes are emitted (intro→main, main→break, break→main,
    main→outro, etc.).  Same-label phase boundaries (energy-only changes
    within a `main` run) are skipped because the section-role vocabulary
    in ``kizomba_tutor`` already covers those.
    """

    boundary_time_s: float
    from_label: str
    to_label: str
    from_clarity: str  # "subtle" / "moderate" / "clear"
    to_clarity: str
    from_phase_idx: int
    to_phase_idx: int
    from_energy: str = ""
    to_energy: str = ""


@dataclass
class RhythmAnalysis:
    """Complete rhythm analysis result from the DSP pipeline."""

    audio: AudioData
    onsets: OnsetData
    beats: BeatData
    tempo: float
    inter_onset_intervals: NDArray[np.float64] | None = None
    downbeats: NDArray[np.float64] | None = None
    beats_per_measure: int = 4
    phrase_length: int = 8  # dancer 8-count = 2 measures of 4
    downbeat_confidence: float | None = None  # 0.0 = random guess, 1.0 = very confident
    downbeat_offset: int | None = None  # 0 = clean start, positive = N pickup beats
    vocals: VocalsInfo | None = None  # set by the transcription perception pass
    rhythm_features: RhythmFeatures | None = None
    tempo_half: float | None = None  # set when tempo > 140 (possible double-time)
    dance_style: str | None = None  # user-provided style (e.g. "bachata", "kizomba")
    sections: list[SongSection] = field(default_factory=list)
    phases: list[SongPhase] = field(default_factory=list)
