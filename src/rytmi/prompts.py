"""Prompt templates for Gemma rhythm explanations."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rytmi.types import SongPhase, SongSection, StyleProfile, Transition

# ── Downbeat confidence thresholds ────────────────────────────────────────────
# These are calibrated against synthetic test signals (see docs/experiments/).
# Real-music calibration is pending; treat the bands as provisional.
_CONF_HIGH = 0.35   # >= this: "high confidence"
_CONF_LOW = 0.15    # <  this: "ambiguous — treat as a weak guess"
# Between _CONF_LOW and _CONF_HIGH: "plausible guess"


def downbeat_confidence_label(confidence: float) -> str:
    """Return a learner-friendly label for a downbeat confidence score.

    Bands (provisional — calibrated on synthetic signals only):
      >= 0.35  →  "high confidence"
      0.15–0.35 → "plausible guess"
      <  0.15  →  "ambiguous — treat as a weak guess"
    """
    if confidence >= _CONF_HIGH:
        return "high confidence"
    if confidence >= _CONF_LOW:
        return "plausible guess"
    return "ambiguous — treat as a weak guess"


def _format_downbeat_section(downbeat_times, downbeat_confidence: float | None) -> str:
    """Build the downbeat block that is inserted into RHYTHM_ANALYSIS_TEMPLATE.

    Returns an empty string when no downbeat data is available (so that callers
    that pre-date this feature continue to work without visible gaps in the
    prompt).  When confidence is below the low threshold, appends an explicit
    uncertainty note so Gemma uses hedged language about the likely "1".
    """
    if downbeat_times is None or len(downbeat_times) == 0:
        return ""

    times_str = ", ".join(
        f"{round(t / 0.05) * 0.05:.2f}" for t in downbeat_times[:4]
    )
    n_total = len(downbeat_times)
    if n_total > 4:
        times_str += f" ... ({n_total} total)"

    if downbeat_confidence is None:
        return f"- Likely downbeat / \"1\" times (first 4, seconds): {times_str}\n"

    label = downbeat_confidence_label(downbeat_confidence)
    lines = [
        f"- Likely downbeat / \"1\" times (first 4, seconds): {times_str}",
        f"- Downbeat estimate confidence: {label} ({downbeat_confidence:.2f})",
    ]

    if downbeat_confidence < _CONF_LOW:
        lines.append(
            "\nNote: the downbeat position is uncertain for this track. "
            "The analysis could not clearly identify which beat is the \"1\". "
            "When discussing where the phrase starts or where to step on \"1\", "
            "use hedged language (e.g. \"the 1 is likely around...\", "
            "\"you may need to listen for the downbeat rather than relying on "
            "this estimate\")."
        )

    return "\n".join(lines) + "\n"


def _format_vocals_section(vocals) -> str:
    """Build the vocals block inserted into ``RHYTHM_ANALYSIS_TEMPLATE``.

    Returns an empty string when ``vocals`` is None so callers that omit the
    perception pass produce a prompt byte-identical to the pre-feature version.
    ``vocals`` is typed loosely (``VocalsInfo | None``) to avoid a circular
    import from ``rytmi.types``.
    """
    if vocals is None:
        return ""

    language = (getattr(vocals, "language", "") or "unknown").strip() or "unknown"
    snippet = (getattr(vocals, "lyric_snippet", "") or "").strip()

    lines = [f"- Detected vocal language: {language}"]
    if snippet:
        lines.append(f'- Sample lyric (if audible): "{snippet}"')
    return "\n".join(lines) + "\n"


def _format_rhythm_features_section(rhythm_features, tempo_half: float | None = None) -> str:
    """Build the rhythm features block for the analysis template.

    Returns empty string when ``rhythm_features`` is None so callers that
    predate this feature produce an unchanged prompt.
    """
    if rhythm_features is None:
        return ""

    opb = rhythm_features.onsets_per_beat
    if opb < 1.5:
        density_label = "sparse — typical of kizomba, zouk"
    elif opb <= 2.5:
        density_label = "moderate"
    else:
        density_label = "dense — typical of bachata, salsa"

    perc = rhythm_features.percussiveness
    if perc < 0.3:
        perc_label = "low"
    elif perc <= 0.6:
        perc_label = "moderate"
    else:
        perc_label = "high"

    pattern_str = ", ".join(f"{v:.2f}" for v in rhythm_features.beat_strength_pattern)

    lines = []

    # Half-time as a primary bullet (most prominent position) when present.
    if tempo_half is not None:
        lines.append(
            f"- Estimated half-time tempo: {tempo_half:.0f} BPM"
            f" (the detected tempo may be double-time; some styles like kizomba/semba"
            f" play at ~70-80 BPM but are detected at ~140-160 BPM)"
        )

    bc = rhythm_features.beat_clarity
    if bc < 0.2:
        bc_label = "very subtle — the beat is hard to hear; a beginner may struggle to find it"
    elif bc < 0.35:
        bc_label = "moderate — the beat is present but not always obvious"
    else:
        bc_label = "clear — the beat is easy to hear and follow"

    lines.extend([
        f"- Onset density: {opb:.1f} onsets/beat ({density_label})",
        f"- Beat accent pattern (mean strength per beat position): [{pattern_str}]",
        f"- Percussiveness: {perc:.2f} ({perc_label})",
        f"- Beat clarity: {bc:.2f} ({bc_label})",
        f"- Spectral brightness: {rhythm_features.spectral_centroid_mean:.0f} Hz",
        f"- Tempo stability: {rhythm_features.tempo_stability:.2f}"
        f" ({'very steady' if rhythm_features.tempo_stability < 0.05 else 'moderate variation'})",
        f"- IOI summary: median {rhythm_features.ioi_median_ms:.0f}ms,"
        f" std {rhythm_features.ioi_std_ms:.0f}ms",
    ])

    return "\n".join(lines) + "\n"


# ── Phase 10: distinct-feature thresholds ─────────────────────────────────────
# Outliers that earn a bullet in _format_distinct_features_section.  These
# coach the LLM to reach for the specific number instead of falling back on
# style-level platitudes ("energetic bachata", "4/4 time signature").  Values
# calibrated against the 10-track Phase-9 eval set: mid-of-the-road tracks
# should trigger zero bullets; a track that a listener would describe as
# "particularly percussive" or "unusually dense" should trigger one.
_DISTINCT_PERCUSSIVENESS_HIGH = 0.65
_DISTINCT_PERCUSSIVENESS_LOW = 0.25
_DISTINCT_OPB_DENSE = 3.0
_DISTINCT_OPB_SPARSE = 1.0


def _format_distinct_features_section(
    tempo: float | None,
    rhythm_features,
    style_profile: StyleProfile | None = None,
) -> str:
    """Build the distinctive-features block inserted into the analysis template.

    Returns 1-3 bullets that call out numeric outliers for THIS track (tempo
    outside the style's typical range, unusually high/low percussiveness, or
    unusually dense/sparse onset density).  Returns an empty string when
    nothing stands out so middle-of-the-road tracks don't accrue a spurious
    "this track is typical" bullet.

    The block is a coaching signal for the LLM: when it fires, the answer
    should reach for the specific number rather than the generic style
    description.
    """
    bullets: list[str] = []

    if tempo and style_profile is not None:
        lo, hi = style_profile.bpm_range
        if tempo > hi:
            bullets.append(
                f"- Tempo {tempo:.0f} BPM is above the typical "
                f"{style_profile.name} range ({lo}-{hi} BPM) — the track runs "
                "fast for the style."
            )
        elif tempo < lo:
            bullets.append(
                f"- Tempo {tempo:.0f} BPM is below the typical "
                f"{style_profile.name} range ({lo}-{hi} BPM) — the track runs "
                "slow for the style."
            )

    if rhythm_features is not None:
        perc = rhythm_features.percussiveness
        if perc > _DISTINCT_PERCUSSIVENESS_HIGH:
            bullets.append(
                f"- Percussiveness {perc:.2f} is unusually high — drums and "
                "percussion dominate the texture."
            )
        elif perc < _DISTINCT_PERCUSSIVENESS_LOW:
            bullets.append(
                f"- Percussiveness {perc:.2f} is unusually low — melodic or "
                "harmonic content carries the rhythm more than drums."
            )

        opb = rhythm_features.onsets_per_beat
        if opb > _DISTINCT_OPB_DENSE:
            bullets.append(
                f"- Onset density {opb:.1f} per beat is unusually dense — "
                "expect tight syncopation and ornamentation."
            )
        elif opb < _DISTINCT_OPB_SPARSE:
            bullets.append(
                f"- Onset density {opb:.1f} per beat is unusually sparse — "
                "the rhythm sits between the beats more than on them."
            )

    if not bullets:
        return ""

    bullets = bullets[:3]
    header = "Distinctive features of this track (vs. typical):"
    return header + "\n" + "\n".join(bullets) + "\n"


def _beat_clarity_tag(beat_clarity: float) -> str:
    if beat_clarity < 0.2:
        return "subtle"
    if beat_clarity < 0.35:
        return "moderate"
    return "clear"


def _format_transitions_block(
    phases: "list[SongPhase] | None",
    *,
    include_same_label: bool = False,
) -> str:
    """Build the transitions block inserted into ``RHYTHM_ANALYSIS_TEMPLATE``.

    Phase 40 — names label-change boundaries in the song so
    ``QUESTION_KIZOMBA_TRANSITIONS`` can coach the moments *between*
    sections: anticipation cue, the boundary itself, re-entry cue.

    Phase 40d — when ``include_same_label=True``, also emits same-label
    energy-shift transitions (``main`` → ``main`` with an energy delta).
    Default ``False`` preserves Phase 40 behaviour: only label-change
    boundaries appear in the prompt's transitions block.

    Returns an empty string when the phase list yields no transitions so
    this block is harmless to prompts that don't reference transitions.
    """
    if not phases:
        return ""
    from rytmi.dsp import extract_transitions  # avoid top-level dsp.py import

    transitions = extract_transitions(phases, include_same_label=include_same_label)
    if not transitions:
        return ""

    lines: list[str] = [f"- Transitions ({len(transitions)} label boundaries):"]
    for i, tr in enumerate(transitions, 1):
        # Phase 40d: include energy info so the model can coach same-label
        # energy shifts (main→main with energy: medium → high) when the
        # caller has opted into include_same_label transitions.
        energy_str = (
            f", energy: {tr.from_energy or '-'} → {tr.to_energy or '-'}"
            if tr.from_energy or tr.to_energy
            else ""
        )
        lines.append(
            f"  T{i}: {tr.boundary_time_s:.0f}s, {tr.from_label} → {tr.to_label} "
            f"(beat: {tr.from_clarity} → {tr.to_clarity}{energy_str})"
        )
    return "\n".join(lines) + "\n"


def _phase_texture_tag(
    phase: SongPhase, sections: list[SongSection] | None
) -> str | None:
    """Return a qualitative texture tag for a phase, or None if data is missing.

    Phase 41-lite — derive a single-word texture tag from the average
    harmonic / percussive RMS ratios (``harm_ratio`` / ``perc_ratio``) of the
    sections that make up this phase. The H× / P× values are already computed
    in ``describe_sections``; this helper just aggregates them up to the phase
    level and translates them into a learner-readable word per the
    ``_METRIC_GUARD_RULE`` ("translate analysis values into qualitative
    language").

    Returns None when no constituent section has both ratios set.
    """
    if not sections:
        return None
    members = [
        s for s in sections
        if s.start_s >= phase.start_s
        and s.end_s <= phase.end_s + 1e-3
        and s.harm_ratio is not None
        and s.perc_ratio is not None
    ]
    if not members:
        return None
    h_avg = sum(s.harm_ratio for s in members) / len(members)
    p_avg = sum(s.perc_ratio for s in members) / len(members)
    if h_avg <= 0 and p_avg <= 0:
        return None
    if p_avg > 0 and h_avg / p_avg >= 1.3:
        return "bass-driven"
    if h_avg > 0 and p_avg / h_avg >= 1.3:
        return "percussive"
    return "balanced"


def _phase_density_tag(phase: SongPhase) -> str | None:
    """Return a qualitative onset-density tag for a phase, or None.

    Phase 41-lite — translates ``avg_rhythm_features.onsets_per_beat`` into
    one of ``sparse`` / ``steady`` / ``busy`` so kizomba_tutor and
    kizomba_transitions can reference per-phase rhythmic density without
    seeing raw decimals (forbidden by ``_METRIC_GUARD_RULE``).
    """
    rf = phase.avg_rhythm_features
    if rf is None:
        return None
    opb = rf.onsets_per_beat
    if opb < 1.0:
        return "sparse"
    if opb < 1.8:
        return "steady"
    return "busy"


def _phase_vocal_tag(
    phase: SongPhase, sections: list[SongSection] | None
) -> str | None:
    """Return a qualitative vocal-presence tag for a phase, or None.

    Phase 41-D — averages the per-section ``vocal_ratio`` (fraction of
    frames flagged vocal-active by the Demucs envelope; populated in
    ``analyze()`` when ``vocal_env`` is supplied) across the sections
    contained in this phase, then translates the average into one of
    ``present`` / ``sparse`` / ``quiet``. Vocals come and go more than
    HPSS texture does within a single kizomba song, so per-phase vocal
    presence is the candidate signal most likely to give Gemma genuine
    inter-phase contrast.

    Thresholds match the project's existing ``_VOCAL_MIN_ACTIVE_RATIO``
    of 0.20 for the "has vocals at all" boundary; the upper threshold
    of 0.55 separates a vocal-led section from one with frequent breaks.

    Returns None when no constituent section has ``vocal_ratio`` set
    (i.e. ``analyze()`` was called without a ``vocal_env``).
    """
    if not sections:
        return None
    members = [
        s for s in sections
        if s.start_s >= phase.start_s
        and s.end_s <= phase.end_s + 1e-3
        and s.vocal_ratio is not None
    ]
    if not members:
        return None
    v_avg = sum(s.vocal_ratio for s in members) / len(members)
    if v_avg >= 0.55:
        return "present"
    if v_avg >= 0.20:
        return "sparse"
    return "quiet"


def _format_sections_block(
    sections: list[SongSection] | None,
    style_profile: StyleProfile | None = None,
    phases: list[SongPhase] | None = None,
    *,
    include_phase_features: bool = False,
    include_phase_vocal: bool = False,
) -> str:
    """Build the song-sections block inserted into ``RHYTHM_ANALYSIS_TEMPLATE``.

    Returns an empty string when ``sections`` is empty/None so callers that
    predate section detection produce an unchanged prompt.

    When ``phases`` are provided (merged same-label runs), the block leads
    with a compact phase summary for the user/dancer, followed by detailed
    per-section rhythm data for Gemma to reason over.

    When a ``StyleProfile`` is provided, each phase gets a coaching hint
    from the profile's ``section_coaching`` dict.

    Phase 41-lite — when ``include_phase_features=True``, the per-phase
    summary line gains qualitative texture (bass-driven / percussive /
    balanced) and onset-density (sparse / steady / busy) tags derived from
    DSP signals already present in ``RhythmAnalysis``. The tags help
    kizomba_tutor and kizomba_transitions write phase-specific coaching
    rather than generic section-label boilerplate. Off by default to keep
    the prompt byte-identical for existing callers; opt in via the flag.
    """
    if not sections:
        return ""

    from rytmi.styles import describe_beat_accent

    lines: list[str] = []

    # ── Phase summary (compact, user-oriented) ────────────────────────
    if phases:
        lines.append(f"- Song structure ({len(phases)} phases):")
        for i, ph in enumerate(phases, 1):
            count_str = f" ×{ph.section_count}" if ph.section_count > 1 else ""
            header = (
                f"  Phase {i}: {ph.label}{count_str}"
                f" ({ph.start_s:.0f}s–{ph.end_s:.0f}s)"
            )
            # Summarise energy spread
            unique_energies = sorted(set(ph.energy_levels))
            if len(unique_energies) == 1:
                header += f" — {unique_energies[0]} energy"
            else:
                header += f" — energy: {', '.join(unique_energies)}"
            # Phase-level beat clarity summary
            if ph.avg_rhythm_features is not None:
                header += f", beat: {_beat_clarity_tag(ph.avg_rhythm_features.beat_clarity)}"
            # Phase 41-lite — qualitative per-phase feature tags
            if include_phase_features:
                texture = _phase_texture_tag(ph, sections)
                if texture is not None:
                    header += f", texture: {texture}"
                density = _phase_density_tag(ph)
                if density is not None:
                    header += f", onsets: {density}"
            # Phase 41-D — qualitative per-phase vocal presence
            if include_phase_vocal:
                vocal = _phase_vocal_tag(ph, sections)
                if vocal is not None:
                    header += f", vocal: {vocal}"
            lines.append(header)

            # Phase-level coaching hint
            if style_profile and ph.label in style_profile.section_coaching:
                lines.append(
                    f"     Coaching hint: {style_profile.section_coaching[ph.label]}"
                )

    # ── Detailed per-section rhythm data (for Gemma analysis) ─────────
    lines.append(f"- Section detail ({len(sections)} segments):")
    for i, sec in enumerate(sections, 1):
        header = (
            f"  {i}. {sec.label} ({sec.start_s:.1f}s–{sec.end_s:.1f}s)"
            f" — {sec.energy_level} energy"
        )
        lines.append(header)

        if sec.rhythm_features is not None:
            rf = sec.rhythm_features
            accent_desc = describe_beat_accent(
                rf.beat_strength_pattern, style_profile
            )
            lines.append(
                f"     Rhythm: {rf.onsets_per_beat:.1f} onsets/beat,"
                f" percussiveness {rf.percussiveness:.2f},"
                f" beat clarity {rf.beat_clarity:.2f},"
                f" accent: {accent_desc}"
            )

    return "\n".join(lines) + "\n"


DEFAULT_SYSTEM_PROMPT = (
    "You are a music teacher explaining rhythm concepts. "
    "Be concise and practical. Use musical terminology when helpful. "
    "When discussing rhythm patterns, describe how a musician would count them. "
    "Base your answers only on the analysis data provided — do not invent details. "
    "When the analysis highlights a specific number (tempo, energy ratio, onset "
    "density, timestamp, percussiveness), emphasize that specific number. Avoid "
    "generic style-level statements that don't reference the numbers above."
)

RHYTHM_ANALYSIS_TEMPLATE = """\
Here is the rhythmic analysis of an audio clip (times are approximate, \
measured with ~25 ms precision):

- Duration: {duration:.1f} seconds
- Estimated tempo: {tempo:.0f} BPM
- Time signature: {beats_per_measure}/4 (assumed)
- Dancer phrase length: {phrase_length} counts \
({measures_per_phrase} measures per 8-count phrase)
- Number of detected beats: {n_beats}
- Number of detected onsets: {n_onsets}
- Beat times (first 8, seconds): {beat_times}
- Inter-onset intervals (first 8, ms): {ioi_summary}
{downbeat_section}{vocals_section}{rhythm_features_section}{distinct_features_section}{sections_block}{transitions_section}{style_section}\
Small differences in timing (under ~25 ms) are measurement noise, not \
intentional rhythmic variation. Focus on the overall pattern.

{question}"""

# Phase 35 — shared rule fragments used across multiple prompts.
# Each fragment is interpolated into the consuming prompt at module-load time
# so the canonical wording lives in one place. When the model leaks a
# forbidden form (Phase 31 percussiveness narration, Phase 33b "the 1" leak,
# Phase 34 Calo-Pascoal "0.34" and Isabelle "step on 1 and 3"), fix it here
# and every consuming prompt inherits the fix.

_METRIC_GUARD_RULE = (
    "Do NOT quote raw decimals or analysis jargon: no beat-clarity decimals, "
    "no percussiveness ratios, no RMS ratios, no onset-density floats "
    "(no 'onsets/beat' values), no accent-pattern arrays, no tempo-stability "
    "decimals, no beat-strength values. Do NOT use any specific decimal "
    "number from the analysis as a quantity in your output — not in "
    "narration, not as a distinguishing feature, not when explaining why a "
    "section is hard. Constructions like 'percussiveness of <number>' or "
    "'beat clarity of <number>' are forbidden in any form. Instead, "
    "translate analysis values into qualitative language: 'drum-light feel', "
    "'unusually low percussiveness', 'a clear percussive grid', 'pulse felt "
    "through the bass', 'comfortable mid-range', 'very steady tempo'. BPM "
    "and timestamps may be quoted directly."
)

_KIZOMBA_DOWNBEAT_GUARD_RULE = (
    "Do NOT use the word 'downbeat' or the phrase 'the 1' anywhere in "
    "your output — not in narration, not in negation, not when explaining "
    "why kizomba is hard to count. Also forbid specific count positions: "
    "'step on 1 and 3', 'land on count 4', 'count 1, 2, 3, 4'. If you "
    "need to acknowledge that the pulse is subtle or hard to lock onto, "
    "frame it as 'the pulse is felt rather than heard' or 'the bass "
    "carries the pulse'. If the analysis suggests uncertain beat-position "
    "anchoring, do not name that field; say 'the pulse is subtle', "
    "'trust the bass line', or 'avoid relying on a specific count' instead. "
    "Talk about the steady pulse, syncopation, and off-beat emphasis instead."
)


# Ready-made question strings — pass as `question` to the template
QUESTION_TIME_SIGNATURE = (
    "Based on the beat pattern and onset grouping, what time signature does this rhythm "
    "most likely use? Explain your reasoning in 2-3 sentences."
)

QUESTION_COUNTING = (
    "How would a musician count along with this rhythm? "
    "Give the counting pattern (e.g. '1 and 2 and 3 and 4')."
)

QUESTION_STYLE_FIT = (
    "The dancer is practicing **{style}**. Based on the analysis data above, "
    "how well does this track's rhythm fit {style}? In 2-3 concise sentences, cover: "
    "(1) whether the tempo is in the typical range for {style}, "
    "(2) what rhythmic features are typical or unusual for {style} "
    "(e.g. beat accent pattern, onset density, percussiveness), and "
    "(3) any specific things the dancer should be aware of (e.g. sections that are "
    "harder to count, unusual accents, or tempo variations)."
)

QUESTION_DIFFICULTY = (
    "Rate the difficulty of this rhythm for a beginner on a scale of 1 to 5 "
    "and explain why in one sentence."
)

QUESTION_EXERCISE = (
    "Suggest one short practice exercise a beginner could use to learn this rhythm. "
    "Be specific and practical."
)

QUESTION_DANCER = (
    "You are a dance coach analyzing THIS specific track for a **{style}** dancer. "
    "Do NOT write generic music descriptions — every sentence must tie to the "
    "actual tempo, phrase length, section structure, or counts from the "
    "analysis above. Coach like a dance teacher, not like a metrics report.\n\n"
    "Answer in exactly four short sections. Keep the full answer under about 220 words total. "
    "Each section should be 1-3 sentences max.\n\n"
    "1) **Tempo & feel.** State the BPM and how it fits {style}. "
    "Is it on the slow, typical, or fast end for this style? "
    "What does that mean for the dancer's movement quality?\n\n"
    "2) **8-count map.** Briefly map one 8-count phrase of the {style} basic. "
    "Be concrete but compact: one short line for counts 1–4 and one short "
    "line for 5–8 is enough. Be specific to {style} (e.g. bachata basic, "
    "kizomba walk-step, etc.).\n\n"
    "3) **Phrase dynamics.** Does the second 4-count of each 8 feel like "
    "a repeat, a mirror, or a build? Should the dancer add styling (hip, "
    "arm, head movement) on counts 4 and 8, or stay grounded?\n\n"
    "4) **Drill.** One 30-second practice tied to a real moment in this "
    "track. Pick a section label and a timestamp from the analysis (e.g. "
    "'During the main section starting at 65s, loop counts 1-8 of the "
    "{style} basic and focus on [specific body part] landing on count "
    "[1/4/5/8]'). Name ONE specific thing to focus on.\n\n"
    "Do not say things like 'this feels energetic' or 'a dancer might "
    "bounce'. Reference the actual BPM, phrase length, and section "
    "timestamps from the analysis.\n\n"
    "Every claim you make must tie to a specific number from the analysis "
    "above (BPM, timestamp, count, or phrase length). If you cannot back "
    "a sentence with one of those, delete the sentence.\n\n"
    f"{_METRIC_GUARD_RULE}"
)

QUESTION_SECTIONS = (
    "The song is segmented into phases (listed in the analysis above). "
    "You are coaching a **{style}** dancer through THIS specific track.\n\n"
    "Write ONE line per phase in exactly this format:\n"
    "    P#: <start>s-<end>s, <label> — <coaching>\n\n"
    "Rules:\n"
    "- Group adjacent phases with the same label into a single line covering "
    "the full span (e.g. \"P3-5: 45s-110s, main — ...\").\n"
    "- The coaching MUST reference at least one specific number from the "
    "analysis above (a timestamp, BPM, onset density, percussiveness, energy "
    "ratio, accent pattern, or rms ratio). Sentences like \"feel the bachata "
    "basic\" or \"maintain your 4/4 counting\" without a specific number must "
    "be deleted.\n"
    "- If a phase has no distinctive feature vs. the surrounding phases, "
    "write exactly: `P#: <start>s-<end>s, <label> — continues the "
    "<prev_label> feel` (a 5-word fallback — do not pad it).\n"
    "- Total answer under 250 words. No intro sentence, no outro sentence, "
    "no closing summary — just the P# lines."
)

QUESTION_SONG_ARC = (
    "Describe the overall energy journey of this track for a **{style}** dancer "
    "in 3-4 sentences. Where does the energy start, how does it build, where "
    "is the peak, and how does it resolve? Reference the phase structure and "
    "timing from the analysis above. Do not list individual sections — tell "
    "the story of this song as a single flowing narrative.\n\n"
    "Then, in ONE additional sentence, identify 1-2 things that distinguish "
    "THIS track from other {style} tracks at a similar tempo — anchor it on "
    "a timestamp, BPM, or a structural feature (e.g. 'a long break from 15s "
    "to 38s', 'a single high-energy peak at 139s', 'a percussion-led intro'). "
    "Do not write sentences that would apply unchanged to a random {style} "
    "track at this BPM.\n\n"
    f"{_METRIC_GUARD_RULE}"
)

QUESTION_RHYTHM_ANATOMY = (
    "You are introducing a learner to **{style}** as a musical genre, "
    "BEFORE they hear any specific track. Write a TWO-paragraph genre "
    "intro the learner reads before any track-specific work.\n\n"
    "**Paragraph 1 — rhythmic anatomy** (~100 words). Explain the "
    "rhythmic anatomy of {style}: the typical tempo range, the time "
    "signature, what carries the pulse (bass / percussion / melody / "
    "harmony), where the heavy rhythmic emphasis usually lands relative "
    "to the underlying pulse, and the structural arc a typical {style} "
    "track follows (intro / main / break / build / peak / outro).\n\n"
    "**Paragraph 2 — sub-style hints** (~80 words, 2-4 sentences). Name "
    "2 to 4 major sub-styles or stylistic variants of {style} that a "
    "learner is likely to encounter on the dance floor, and briefly "
    "distinguish them rhythmically (tempo range, pulse character, "
    "texture, energy). For kizomba, common sub-styles include Angolan "
    "kizomba, kizomba fusion, urbankiz, tarraxinha, ghetto zouk, and "
    "semba; pick the ones a learner is most likely to encounter and "
    "say what makes each rhythmically distinct. For bachata, common "
    "sub-styles include traditional / Dominican bachata, modern / "
    "sensual bachata, urban bachata, and bachatango; same approach. "
    "End with one sentence framing this as a hint the learner can use "
    "to *place* a track when they hear it — without us claiming to "
    "identify the sub-style of any specific song from the analysis.\n\n"
    "This intro runs ONCE at the top of a learning session and frames "
    "what the learner will hear in tracks afterward. It is NOT "
    "track-specific — do not invent a hypothetical track, do not quote "
    "specific timestamps, and do not refer to 'this track' or 'this "
    "song'. Speak about {style} as a genre.\n\n"
    "Hard rules:\n"
    "- This is GENRE explanation, NOT movement coaching. Do NOT "
    "  prescribe steps, walk-step instructions, weight transfers, "
    "  travel directives, or styling cues. Save those for the tutor.\n"
    "- Do NOT use the P# format. Write two prose paragraphs, no "
    "  headers, no bullet lists.\n"
    "- Do NOT invent specific instruments or vocal cues; speak in "
    "  abstract pulse / percussion / bass / melodic-content language "
    "  that any well-known {style} track would share.\n"
    "- Do NOT claim that any specific track belongs to a specific "
    "  sub-style. Sub-style identification from a `RhythmAnalysis` "
    "  alone is unreliable; the sub-style hints are framing for the "
    "  learner, not a classification of any song they will hear.\n"
    f"- {_METRIC_GUARD_RULE}\n"
    f"- For kizomba specifically: {_KIZOMBA_DOWNBEAT_GUARD_RULE}\n"
    "- Total answer under 220 words across both paragraphs."
)

QUESTION_LISTENING_GUIDE = (
    "You are orienting a **{style}** dancer to THIS specific track BEFORE "
    "they try to move. The goal is musical understanding, not movement "
    "coaching: help the learner know what to listen for in this song and "
    "where the music will likely be hardest to follow.\n\n"
    "Write TWO short paragraphs:\n\n"
    "Paragraph 1 — **orientation**. Open with the duration and tempo. "
    "Describe the song's structural arc using the phase labels from the "
    "analysis above (intro / main / break / build / peak / outro) — the "
    "broad shape, not a per-phase walkthrough. Note what carries the "
    "pulse in qualitative terms ('drum-light, with the bass line "
    "carrying the pulse', 'a clear percussive grid', 'melodic content "
    "over a soft pulse'). Do NOT list every section — describe the arc "
    "as one journey.\n\n"
    "Paragraph 2 — **difficulty map**. Where will the learner likely "
    "lose the pulse, and why? Anchor on specific timestamps and the "
    "per-phase beat-clarity labels (subtle / moderate / clear). Name "
    "the hardest moment of the song and the reason it's hard (a clarity "
    "dip, a long stretch where attention drifts, a section where the "
    "percussion thins). End with one piece of LISTENING advice for the "
    "hardest moment ('trust the bass line through the break', 'feel "
    "the underlying pulse', 'don't chase the louder percussion at the "
    "peak'). If the track stays clear throughout, say so — the challenge "
    "becomes sustaining attention rather than recovering from a dip.\n\n"
    "Hard rules:\n"
    "- This is LISTENING preparation, NOT movement coaching. Do NOT "
    "  prescribe steps, walk-step instructions, weight transfers, "
    "  travel directives, or styling cues. Save those for the tutor.\n"
    "- Do NOT use the P# format. Write prose paragraphs, not phase "
    "  lines.\n"
    f"- {_METRIC_GUARD_RULE}\n"
    "- Do NOT invent specific instruments or vocal cues that are not "
    "  inferable from the analysis. Use abstract pulse / percussion / "
    "  bass / melodic-content language.\n"
    f"- For kizomba specifically: {_KIZOMBA_DOWNBEAT_GUARD_RULE}\n"
    "- Total answer under 200 words. No headers, no bullet lists in "
    "  the output — just the two paragraphs."
)

QUESTION_KIZOMBA_TUTOR = (
    "You are coaching a learner who is trying to *hear* the kizomba beat in "
    "THIS specific track. Kizomba has a slow, often subtle pulse — your job "
    "is to be honest about where the beat is easy or hard to feel and to "
    "translate that analysis into practical movement choices. Coach like a "
    "beginner/improver dance teacher, not like a metrics report.\n\n"
    "Use ONLY the per-phase 'beat: subtle/moderate/clear' labels and the "
    "section structure from the analysis above. You may use the numbers to "
    "decide how confident to be, but do not quote raw metrics back to the "
    "learner. Do not invent specific instruments or accents that aren't "
    "shown in the data.\n\n"
    "Write ONE line per phase in exactly this format:\n"
    "    P#: <start>s-<end>s, <section> [beat: <subtle|moderate|clear>] — <coaching>\n\n"
    "The `<section>` slot is the section name from the phase summary "
    "(`intro`, `main`, `break`, `short_break`, `build`, `peak`, `outro`), "
    "optionally with the count suffix shown there (e.g. `main ×4`). Do "
    "NOT put the energy descriptor (`low energy`, `high energy`, "
    "`energy: low, medium`) in the section slot — energy is context for "
    "your coaching tone, not the label.\n\n"
    "Rules for the coaching text:\n"
    "- Every line must carry a real coaching note. "
    "Do NOT use `continues` as a coaching note — "
    "even when adjacent phases share the same label, "
    "name what is physically different about the new group "
    "(energy, role in the arc, what the learner should focus on now).\n"
    "- Treat exact moves as examples, not commands. Prefer movement strategy "
    "  plus one safe option: small weight shifts, mark the pulse in place, "
    "  reduce travel, keep walking evenly, count 4 or 8 beats internally, "
    "  wait for the next stable pulse, or build gradually from the previous "
    "  section.\n"
    "- For phases tagged `beat: subtle`, say the pulse is hard to lock onto "
    "  and give a recovery action: make movement smaller, count internally, "
    "  keep a tiny weight shift, or re-enter at the next clearer phase.\n"
    "- For phases tagged `beat: moderate`, give options: stay compact, test "
    "  the pulse with small steps, and avoid chasing extra percussion.\n"
    "- For phases tagged `beat: clear`, say it is safe to trust the steady "
    "  pulse and suggest how to use it physically: walk the basic, travel a "
    "  little more, or add styling only after the pulse feels automatic.\n"
    "- When the song has more than one `main` group, name each group's "
    "  role in the song's arc rather than just its label. Use this small "
    "  vocabulary, picked from position relative to other phases:\n"
    "    * The earliest `main` group is *establishing*: the learner "
    "      settles in and finds the pulse.\n"
    "    * `main` groups in the middle are *sustaining*: the same "
    "      strategy carries forward, with one specific focus per group "
    "      (weight transfer, frame, or breath).\n"
    "    * A `main` group immediately before a `build` or `peak` is "
    "      *building*: energy is climbing; the learner can travel more "
    "      or add intention.\n"
    "    * A `main` group immediately after a `peak` or `break` is "
    "      *returning*: the basic re-establishes; the learner reconnects.\n"
    "    * The final `main` group before an `outro` is *closing*: the "
    "      song is winding down; movement contracts.\n"
    "  Songs with only one `main` group don't need a role — coach it on "
    "  its own merits.\n"
    "- If the label is `break`, do not default to 'pause and hold'. Treat "
    "  it as a quieter or changed section. When the break has `beat: clear` "
    "  or `beat: moderate`, prefer recovery language: reduce travel, keep "
    "  a small pulse in the body, reset, then reconnect on the next phase. "
    "  Only suggest stillness or marking time when the beat is genuinely "
    "  `subtle`.\n"
    f"- {_METRIC_GUARD_RULE} "
    "If tempo helps, mention it at most once in plain language such as "
    "'comfortable slow pulse'. The required phase time span is enough "
    "numeric grounding.\n"
    f"- {_KIZOMBA_DOWNBEAT_GUARD_RULE}\n"
    "- Total answer under 230 words. No intro, no outro."
)

# Phase 29b — optional second-pass polish for kizomba tutor output.
# `polish_kizomba_tutor_output` in rytmi.llm pairs the system prompt below
# with `build_kizomba_tutor_polish_prompt(...)` to rewrite a one-pass draft
# against a stricter coaching rubric without changing analysis facts.
KIZOMBA_TUTOR_POLISH_SYSTEM = (
    "You are a kizomba dance coach reviewing a short tutor answer for a "
    "beginner/improver learner. Preserve the analysis grounding, but improve "
    "the coaching language. Do not add musical facts, new instruments, or a "
    "downbeat / '1'."
)


def build_kizomba_tutor_polish_prompt(track_name: str, draft: str) -> str:
    """Build the user-turn rewrite prompt for the kizomba tutor polish pass.

    The rubric mirrors the rules in ``QUESTION_KIZOMBA_TUTOR`` but speaks in
    rewrite-instructions form so the model edits an existing draft rather
    than re-deriving one from analysis.
    """
    return (
        f"Rewrite this kizomba tutor draft for {track_name}.\n\n"
        "Keep the same P# lines, phase labels, time spans, and beat tags. "
        "Do not add sections. Do not remove sections. Return only the "
        "revised P# lines.\n\n"
        "Improve only the coaching text after the dash:\n"
        "- Make it more useful to a beginner/improver dancer.\n"
        "- Prefer movement strategy plus one safe option, not exact move "
        "prescriptions.\n"
        "- Replace vague `continues` lines with what should physically "
        "continue.\n"
        "- For clear-beat sections, suggest how to use the stable pulse.\n"
        "- For moderate/subtle sections, suggest how to stay compact, "
        "recover, or avoid chasing extra percussion.\n"
        "- For `break` labels, do NOT default to silence, stillness, or "
        "pause-and-hold unless the beat tag is `subtle`. When the break "
        "has `beat: clear` or `beat: moderate`, prefer: reduce travel, "
        "keep a small pulse in the body, reset, then reconnect on the "
        "next phase.\n"
        "- Avoid raw metrics, repeated BPM mentions, beat-clarity "
        "decimals, and analysis jargon.\n"
        "- Do not name a downbeat or '1'.\n"
        "- Keep the whole answer under 230 words.\n\n"
        f"Draft:\n{draft.strip()}"
    )


QUESTION_KIZOMBA_DRILLS = (
    "You are a kizomba dance coach designing a practice plan for a "
    "beginner/improver learner working with THIS specific track. The plan "
    "should cover the WHOLE song — every phase from the analysis maps to "
    "exactly one drill line — and read like a real lesson plan, not a "
    "metrics report.\n\n"
    "Use ONLY the per-phase 'beat: subtle/moderate/clear' labels and the "
    "section structure from the analysis above. Do not invent specific "
    "instruments or accents that aren't shown in the data.\n\n"
    "Group adjacent phases that share the SAME section label AND the "
    "SAME beat tag into ONE drill line, with a P# range and the "
    "combined time span. For example, `P2-P5` if P2 through P5 are all "
    "`main [beat: clear]`. A contrasting section (a `break`, `peak`, "
    "or `build`) ENDS the group — phases of the same label after the "
    "contrast become a NEW group. When the same section type recurs "
    "after a contrast (e.g. `main` before and after a `break`), the "
    "second occurrence should note a meaningful variation if one fits "
    "(post-break: add subtle styling once the basic feels automatic; "
    "after a peak: keep the energy you built).\n\n"
    "TIME SPAN RULE for grouped lines: the combined time span MUST run "
    "from the START of the FIRST phase in the group to the END of the "
    "LAST phase in the group. Do NOT use the end of the second-to-last "
    "phase. Example: if P2 starts at 12s and P5 ends at 148s, write "
    "`P2-P5: main (12s-148s, beat: clear)` — NOT `(12s-121s)` even if "
    "121s is where P4 ends. Read each phase row carefully and use the "
    "LAST phase's end timestamp.\n\n"
    "DIFFERENT LABELS = DIFFERENT GROUPS, even when the beat tag is "
    "the same. The valid section-label set is `intro`, `main`, "
    "`break`, `short_break`, `build`, `peak`, `outro` — every change "
    "between any of these starts a new group. A P# range (`Pn-Pm`) is "
    "ONLY valid when every phase from Pn through Pm shares the SAME "
    "section label. Whenever two consecutive phases have different "
    "labels (a `main` next to an `outro`, an `intro` next to a `main`, "
    "etc.), they appear on separate drill lines — never inside a "
    "shared range. Each label change is also a chance for a tailored "
    "drill: the outro deserves its own wind-down (slow the pace, "
    "return to minimal movement); merging it into a preceding `main` "
    "group loses the closing arc.\n\n"
    "SELF-CHECK before emitting each line: read out the labels of "
    "every phase in your range. If any two differ, split the line. "
    "Never write a range whose end-phase has a different label from "
    "its start-phase.\n\n"
    "WORKED POSITIVE EXAMPLE — when a song has a `main` group followed "
    "by an `outro` (a common ending pattern), write them as TWO "
    "separate lines, not as a range. Schematically:\n"
    "    P_a: main (s_1-s_2, beat: clear) — Drill: <main-phase drill>. <duration>.\n"
    "    P_b: outro (s_2-s_3, beat: clear) — Drill: slow the pace, return to minimal movement. <duration>.\n"
    "Two lines, two different labels, two distinct drills (the outro "
    "always gets its own wind-down). Apply this same shape whenever "
    "the LAST main phase is followed by an outro — do not reach for a "
    "range across the boundary.\n\n"
    "Order drill lines chronologically (P1 first, last phase last) so "
    "a learner can follow the plan top-to-bottom against the song.\n\n"
    "Write ONE line per phase group in exactly this format:\n"
    "    P#[-#]: <section> (<start>s-<end>s, beat: <subtle|moderate|clear>) — Drill: <action>. <duration>.\n\n"
    "The `<section>` slot is the section name from the phase summary "
    "(`intro`, `main`, `break`, `short_break`, `build`, `peak`, "
    "`outro`). Do NOT put the energy descriptor (`low energy`, "
    "`high energy`) in the section slot.\n\n"
    "Rules for the drill text:\n"
    "- Each drill is ONE concrete thing the learner can do. Name a "
    "  body part, a movement, a count, or a recovery action — not a "
    "  vague feeling.\n"
    "- Always state a duration. For groups longer than 30s, name a "
    "  practice loop ('30s loop, repeated through the four main "
    "  phases'). For shorter sections, scale to actual length ('11s "
    "  during the break').\n"
    "- For `beat: subtle` phases, drill recovery: stand still, count 8 "
    "  internally, mark the pulse with a tiny shoulder bounce, or "
    "  practise re-entering on the next clearer phase.\n"
    "- For `beat: moderate` phases, drill staying compact: small steps, "
    "  test the pulse, avoid chasing extra percussion.\n"
    "- For `beat: clear` phases, drill the basic walk-step or weight "
    "  transfer; pick ONE focus (hips, weight, frame, or count).\n"
    "- For `break` / `short_break`, do NOT default to 'pause and hold', "
    "  'stop your steps', or 'hold stillness'. Drill the recovery "
    "  pattern: reduce travel, keep a small pulse in the body, reset, "
    "  reconnect on the next phase. Only suggest stillness or stopping "
    "  movement when the beat tag is genuinely `subtle` — for `beat: "
    "  clear` or `beat: moderate` breaks, the learner should keep the "
    "  pulse in their body and shrink the dance, not freeze.\n"
    "- For recurring groups (e.g. `main` before and after a `break`), "
    "  give the second occurrence a variation that builds on the "
    "  first: 'same walk-step as P2-P5, but now add subtle hip styling "
    "  once the basic feels automatic'.\n"
    f"- {_METRIC_GUARD_RULE} The phase time span is enough numeric "
    "grounding.\n"
    f"- {_KIZOMBA_DOWNBEAT_GUARD_RULE}\n"
    "- Total answer under 250 words. No intro, no outro — just the "
    "  drill lines, one per group."
)

# ── Phase 40: kizomba transitions coaching ───────────────────────────────────
# Coaches the moments BETWEEN sections — the re-entry into the new section
# (what to do when the dancer notices the change has happened) and, where
# the analysis supports it, an audible cue to listen for as the boundary
# approaches. Where kizomba_tutor and kizomba_drills give per-phase
# steady-state coaching, transitions cover the gap a learner hits when a
# `break` arrives mid-song without rehearsal: festival/YouTube dancers can
# plan transitions because they know the song; this prompt gives a regular
# learner a way to handle them on first listen.
#
# Phase 40c rewrite: re-entry-primary, audible-cue-secondary. The first
# draft assumed the learner could count to 8 and use that to predict the
# boundary ("in the last 8-count of the main, soften the basic..."), which
# inverted the project's premise — the target user can't reliably count
# to 8 and ends up noticing transitions *after* they happen. This version
# leads with re-entry (after-the-fact), offers anticipation only when an
# audible cue (energy fade, percussion thinning, bass entering, vocals
# dropping) can be composed from the section properties, and explicitly
# forbids count-based anticipation framing.
#
# Algorithmic transition extraction (`extract_transitions` in dsp.py) feeds
# the prompt a deterministic list of label boundaries via the analysis
# dump's "Transitions" block. The prompt writes coaching per transition;
# the structural verifier (`verify_kizomba_transitions_output`) ensures
# every T# in the output corresponds to a real boundary.

QUESTION_KIZOMBA_TRANSITIONS = (
    "You are coaching a learner through the transitions in THIS specific "
    "kizomba track — the moments where one section ends and another "
    "begins. The kizomba tutor and drills cover steady-state movement "
    "during each section; this output covers the moments BETWEEN them. "
    "Coach like a beginner/improver dance teacher, not like a metrics "
    "report.\n\n"
    "Critical assumption: the learner CANNOT reliably count to 8 yet — "
    "that's why they need this tool. They will most often NOTICE that a "
    "transition has happened and need to react on the fly to the new "
    "section. So your coaching must lead with what to do AFTER they "
    "notice the change, and may add an anticipation cue ONLY when you can "
    "name a specific AUDIBLE signal (energy fading, percussion thinning, "
    "bass entering, vocals dropping). NEVER anchor anticipation on counting "
    "beats: do NOT use 'in the last 8-count of <from>', 'in the final "
    "8-count', 'after N beats', '8 counts before', or any other count-based "
    "prediction. The learner has no reliable internal clock yet.\n\n"
    "The analysis above lists the transitions explicitly under the "
    "'Transitions (N label boundaries)' section, plus per-section energy "
    "and beat-clarity in the section structure. Use ONLY those transitions; "
    "do NOT invent transitions that are not listed; do NOT skip transitions "
    "that ARE listed. Every T# must reference a transition from that list "
    "by its exact boundary time.\n\n"
    "Write ONE line per transition in exactly this format:\n"
    "    T#: <boundary_time>s [<from_label> → <to_label>, beat: <from_clarity> → <to_clarity>] — <coaching>\n\n"
    "The `<from_label>` / `<to_label>` slots are section names from the "
    "transitions list (`intro`, `main`, `break`, `short_break`, `build`, "
    "`peak`, `outro`, `instrumental`). Beat-clarity tags are "
    "`subtle` / `moderate` / `clear`. Quote the boundary time exactly as "
    "it appears in the transitions list.\n\n"
    "Coaching shape:\n"
    "- Lead with **re-entry** — what the learner does once they notice the "
    "  new section has arrived. This is the primary content; every T# "
    "  line must include a re-entry cue.\n"
    "- Add an **audible cue** for anticipation ONLY when the section "
    "  properties make one obvious. Examples by contrast direction:\n"
    "    * High-energy → low-energy (main → break, main → outro): "
    "      'as the energy fades and the percussion thins'.\n"
    "    * Low-energy → medium/high-energy (intro → main, break → main): "
    "      'when the bass kicks in', 'as the percussion returns'.\n"
    "    * Vocals → instrumental boundary: 'when the vocals drop out'.\n"
    "    * Instrumental → vocals: 'when the vocals come back in'.\n"
    "  When you cannot compose a specific audible cue from the section "
    "  properties, OMIT anticipation and lead with re-entry only — do "
    "  NOT invent generic anticipation language.\n"
    "- For `<from>` → `break` transitions: re-entry = keep a small pulse "
    "  in the body, listen, reset. Do NOT default to 'pause and hold' "
    "  or 'freeze' unless the break is `beat: subtle`.\n"
    "- For `break` → `<to>` transitions: re-entry = walk-step on the "
    "  first clear bass hit; don't chase the cymbal or snare that comes "
    "  back loudest. Wait for the steady pulse.\n"
    "- For `<from>` → `peak` or `<from>` → `build`: re-entry = commit to "
    "  the new energy, travel more, add intention.\n"
    "- For `peak` → `<to>`: re-entry = settle back, breath, return to "
    "  the basic.\n"
    "- For `intro` → `main`: re-entry = walk-step the basic on the first "
    "  clear bass hit.\n"
    "- For `<from>` → `outro`: re-entry = contract movement, slow the "
    "  basic, prepare to close.\n"
    "- For `<from>` → `instrumental` or `instrumental` → `<to>`: re-entry "
    "  = keep your basic going steadily; the instrumental is medium-energy, "
    "  not low.\n"
    "- For **same-label** transitions where `<from_label>` == `<to_label>` "
    "  (typically `main → main` with an energy shift, e.g. `energy: medium "
    "  → high`): coach the *role shift* using the section-role vocabulary "
    "  from the kizomba tutor. When energy lifts (medium → high), the new "
    "  phase is *building*: re-entry = travel a little more, add intention. "
    "  When energy settles (high → medium), the new phase is *sustaining* "
    "  or *returning*: re-entry = keep the basic, hold a steady frame, "
    "  reconnect. The audible cue for these shifts is subtler than "
    "  label-change boundaries — the bass line gaining or losing density, "
    "  the percussion thickening or thinning, the vocal taking more or "
    "  less space. Name a specific cue when the energy delta and beat "
    "  context support it; otherwise lead with re-entry only. Keep these "
    "  lines short — one sentence is usually enough.\n"
    "- For transitions where beat-clarity drops (e.g. `clear → subtle`): "
    "  add a recovery cue to the re-entry — shrink the basic to a small "
    "  weight shift, mark the pulse with a tiny shoulder bounce, or "
    "  wait for the next clearer phase.\n"
    "- Treat exact moves as examples, not commands. Prefer movement "
    "  strategy plus one safe option.\n"
    f"- {_METRIC_GUARD_RULE} The boundary time in the T# header is enough "
    "numeric grounding.\n"
    f"- {_KIZOMBA_DOWNBEAT_GUARD_RULE}\n"
    "- Total answer under 220 words. No intro, no outro — just the "
    "  T# lines, one per transition."
)

# ── Bachata coaching surface (Phase 39) ──────────────────────────────────────
# Bachata is the "easier case" counterpoint to kizomba: the acoustic "1" is
# usually present (güira pattern, bongo/tumba) and downbeat detection is
# meaningful, so the tutor is allowed to talk about the 1 — but only as
# honestly as `downbeat_confidence` supports. The verifier in
# `verify_kizomba_drills_output` is structural and reused for bachata drills.

QUESTION_BACHATA_TUTOR = (
    "You are coaching a learner who is trying to *hold the count* in THIS "
    "specific bachata track. The common bachata pain is not finding the "
    "pulse once — it is keeping the 8-count when attention drifts (a new "
    "technique focus, an unexpected break, a fast section, a tiring song). "
    "Your job is to translate the analysis into practical movement choices "
    "that protect the count. Coach like a beginner/improver dance teacher, "
    "not like a metrics report.\n\n"
    "Use ONLY the per-phase 'beat: subtle/moderate/clear' labels and the "
    "section structure from the analysis above. You may use the numbers to "
    "decide how confident to be, but do not quote raw metrics back to the "
    "learner. Do not invent specific instruments or accents that aren't "
    "shown in the data.\n\n"
    "Honest use of the 1: bachata usually carries an acoustic '1' through "
    "the güira pattern and the bongo / tumba, so the analysis above will "
    "often report a non-trivial downbeat confidence. When the downbeat "
    "confidence is reported as 'high confidence' or 'plausible guess', "
    "you may anchor the learner on the 1 — say where the 1 is reliable "
    "and what to do when they hear it (land the basic step, restart the "
    "8-count). When the downbeat confidence is 'ambiguous' or missing, "
    "do NOT name the 1; tell the learner to anchor on the steady pulse "
    "they can hear and to count internally to 8 instead.\n\n"
    "Write ONE line per phase in exactly this format:\n"
    "    P#: <start>s-<end>s, <section> [beat: <subtle|moderate|clear>] — <coaching>\n\n"
    "The `<section>` slot is the section name from the phase summary "
    "(`intro`, `main`, `break`, `short_break`, `build`, `peak`, `outro`), "
    "optionally with the count suffix shown there (e.g. `main ×4`). Do "
    "NOT put the energy descriptor (`low energy`, `high energy`) in the "
    "section slot — energy is context for your coaching tone, not the "
    "label.\n\n"
    "Rules for the coaching text:\n"
    "- Every line must carry a real coaching note. Do NOT use `continues` "
    "  as a coaching note — when adjacent phases share the same label, "
    "  name what is physically different about the new group (energy, "
    "  role in the arc, the count cue you should listen for now).\n"
    "- The bachata basic is steps on counts 1-2-3 with a tap on 4, then "
    "  5-6-7 with a tap on 8. Use that vocabulary when it helps the "
    "  learner anchor: 'land the basic on 1', 'tap on 4', 'restart the "
    "  8-count when you hear the next clear 1'. Do not over-prescribe — "
    "  movement strategy plus one safe option is enough per phase.\n"
    "- For phases tagged `beat: clear`, say the count is safe to trust. "
    "  Suggest sustaining the 8-count basic, adding small styling on 4 "
    "  and 8 only after the count feels automatic, or letting the partner "
    "  follow the steady phrasing.\n"
    "- For phases tagged `beat: moderate`, treat the count as workable "
    "  but more demanding. Suggest staying compact, counting internally "
    "  to 8, and avoiding chasing extra percussion or melodic accents.\n"
    "- For phases tagged `beat: subtle`, say the count is hard to lock "
    "  onto. Give a recovery action: shrink the basic, mark the pulse "
    "  with a small weight shift, count 8 internally and wait for the "
    "  next clearer phase to re-enter on a fresh 1.\n"
    "- When the song has more than one `main` group, name each group's "
    "  role in the song's arc rather than just its label. Use the same "
    "  vocabulary as for kizomba (establishing, sustaining, building, "
    "  returning, closing). Songs with only one `main` group don't need "
    "  a role — coach it on its own merits.\n"
    "- If the label is `break`, do not default to 'pause and hold'. Treat "
    "  it as a quieter or changed section. When the break has `beat: "
    "  clear` or `beat: moderate`, prefer recovery language: shrink the "
    "  basic, keep the 8-count alive in the body, then re-enter on a "
    "  fresh 1 in the next phase. Only suggest stillness or marking time "
    "  when the beat is genuinely `subtle`.\n"
    f"- {_METRIC_GUARD_RULE} If tempo helps, mention it at most once in "
    "plain language (e.g. 'a comfortable mid-tempo bachata'). The required "
    "phase time span is enough numeric grounding.\n"
    "- Total answer under 230 words. No intro, no outro."
)


QUESTION_BACHATA_DRILLS = (
    "You are a bachata dance coach designing a practice plan for a "
    "beginner/improver learner working with THIS specific track. The plan "
    "should cover the WHOLE song — every phase from the analysis maps to "
    "exactly one drill line — and read like a real lesson plan, not a "
    "metrics report.\n\n"
    "Use ONLY the per-phase 'beat: subtle/moderate/clear' labels and the "
    "section structure from the analysis above. Do not invent specific "
    "instruments or accents that aren't shown in the data.\n\n"
    "Group adjacent phases that share the SAME section label AND the "
    "SAME beat tag into ONE drill line, with a P# range and the combined "
    "time span. For example, `P2-P5` if P2 through P5 are all `main "
    "[beat: clear]`. A contrasting section (a `break`, `peak`, or "
    "`build`) ENDS the group — phases of the same label after the "
    "contrast become a NEW group. When the same section type recurs after "
    "a contrast (e.g. `main` before and after a `break`), the second "
    "occurrence should note a meaningful variation if one fits "
    "(post-break: re-enter on a fresh 1, then add subtle styling on 4 "
    "and 8 once the basic feels automatic).\n\n"
    "TIME SPAN RULE for grouped lines: the combined time span MUST run "
    "from the START of the FIRST phase in the group to the END of the "
    "LAST phase in the group. Do NOT use the end of the second-to-last "
    "phase. Read each phase row carefully and use the LAST phase's end "
    "timestamp.\n\n"
    "DIFFERENT LABELS = DIFFERENT GROUPS, even when the beat tag is the "
    "same. The valid section-label set is `intro`, `main`, `break`, "
    "`short_break`, `build`, `peak`, `outro` — every change between any "
    "of these starts a new group. A P# range (`Pn-Pm`) is ONLY valid "
    "when every phase from Pn through Pm shares the SAME section label. "
    "Whenever two consecutive phases have different labels (a `main` "
    "next to an `outro`, an `intro` next to a `main`, etc.), they appear "
    "on separate drill lines — never inside a shared range. Each label "
    "change is also a chance for a tailored drill: the outro deserves "
    "its own wind-down (slow the basic, finish on a clean 8, return to "
    "minimal movement).\n\n"
    "SELF-CHECK before emitting each line: read out the labels of every "
    "phase in your range. If any two differ, split the line. Never write "
    "a range whose end-phase has a different label from its start-phase.\n\n"
    "WORKED POSITIVE EXAMPLE — when a song has a `main` group followed "
    "by an `outro` (a common ending pattern), write them as TWO separate "
    "lines, not as a range. Schematically:\n"
    "    P_a: main (s_1-s_2, beat: clear) — Drill: <main-phase drill>. <duration>.\n"
    "    P_b: outro (s_2-s_3, beat: clear) — Drill: slow the basic, finish on a clean 8. <duration>.\n"
    "Two lines, two different labels, two distinct drills.\n\n"
    "Order drill lines chronologically (P1 first, last phase last) so a "
    "learner can follow the plan top-to-bottom against the song.\n\n"
    "Write ONE line per phase group in exactly this format:\n"
    "    P#[-#]: <section> (<start>s-<end>s, beat: <subtle|moderate|clear>) — Drill: <action>. <duration>.\n\n"
    "The `<section>` slot is the section name from the phase summary "
    "(`intro`, `main`, `break`, `short_break`, `build`, `peak`, "
    "`outro`). Do NOT put the energy descriptor (`low energy`, "
    "`high energy`) in the section slot.\n\n"
    "Rules for the drill text:\n"
    "- Each drill is ONE concrete thing the learner can do. Name a body "
    "  part, a count, or a recovery action — not a vague feeling. The "
    "  bachata basic is steps on 1-2-3 (tap 4), 5-6-7 (tap 8); use that "
    "  vocabulary when it sharpens the cue.\n"
    "- Always state a duration. For groups longer than 30s, name a "
    "  practice loop ('30s loop, repeated through the four main "
    "  phases'). For shorter sections, scale to actual length ('11s "
    "  during the break').\n"
    "- For `beat: clear` phases, drill the basic on the count: 'loop the "
    "  1-2-3-tap, 5-6-7-tap basic, landing the 1 on the steady pulse'. "
    "  Pick ONE focus per group (count anchoring, hip on 4 and 8, frame, "
    "  or partner phrasing).\n"
    "- For `beat: moderate` phases, drill staying anchored: count 8 "
    "  internally, keep the basic compact, do not chase extra percussion. "
    "  Useful as the 'protect the count under cognitive load' surface — "
    "  do not stack new styling here.\n"
    "- For `beat: subtle` phases, drill recovery: shrink the basic to a "
    "  side-to-side weight shift, count 8 internally, re-enter on the "
    "  next clearer phase on a fresh 1.\n"
    "- For `break` / `short_break`, do NOT default to 'pause and hold'. "
    "  Drill the recovery pattern: shrink the basic, keep the 8-count "
    "  alive in the body, re-enter on a fresh 1 on the next phase. Only "
    "  suggest stillness when the beat tag is genuinely `subtle`.\n"
    "- For recurring groups (e.g. `main` before and after a `break`), "
    "  give the second occurrence a variation that builds on the first: "
    "  'same 1-2-3-tap basic as P2-P5, but now add a small hip drop on 4 "
    "  and 8 once the count feels automatic'.\n"
    f"- {_METRIC_GUARD_RULE} The phase time span is enough numeric "
    "grounding.\n"
    "- Total answer under 250 words. No intro, no outro — just the drill "
    "  lines, one per group."
)


# ── Phase 44: bachata transitions coaching ───────────────────────────────────
# Mirror of QUESTION_KIZOMBA_TRANSITIONS for bachata. Same structural T#
# line format so `verify_kizomba_transitions_output` accepts both styles.
# Differences from kizomba: bachata has an acoustic "1" most of the time
# (güira, bongo/tumba) so re-entry can talk about landing the basic on
# the 1 when downbeat confidence supports it. The bachata basic is steps
# on counts 1-2-3 with a tap on 4, then 5-6-7 with a tap on 8.

QUESTION_BACHATA_TRANSITIONS = (
    "You are coaching a learner through the transitions in THIS specific "
    "bachata track — the moments where one section ends and another "
    "begins. The bachata tutor and drills cover steady-state movement "
    "during each section; this output covers the moments BETWEEN them. "
    "Coach like a beginner/improver dance teacher, not like a metrics "
    "report.\n\n"
    "Critical assumption: the learner is *trying to hold the 8-count* — "
    "the common bachata pain is not finding the pulse once but keeping "
    "the count through breaks, energy shifts, and busy sections. Your "
    "coaching must lead with what to do AFTER the learner notices the "
    "transition (re-entry into the new section), and may add an "
    "anticipation cue ONLY when you can name a specific AUDIBLE signal "
    "(energy fading, percussion thinning, bass entering, vocals dropping, "
    "güira pattern stopping or returning). Do NOT anchor anticipation "
    "on counting beats.\n\n"
    "The analysis above lists the transitions explicitly under the "
    "'Transitions (N label boundaries)' section, plus per-section energy "
    "and beat-clarity in the section structure. Use ONLY those transitions; "
    "do NOT invent transitions that are not listed; do NOT skip transitions "
    "that ARE listed. Every T# must reference a transition from that list "
    "by its exact boundary time.\n\n"
    "Honest use of the 1: bachata usually carries the 1 through the güira "
    "and bongo/tumba, so you may say 're-enter on a fresh 1' when the "
    "incoming section's beat-clarity is `clear` or `moderate`. When the "
    "incoming section is `beat: subtle`, do NOT name the 1; tell the "
    "learner to anchor on the steady pulse and re-enter when the next "
    "clearer phase arrives.\n\n"
    "Write ONE line per transition in exactly this format:\n"
    "    T#: <boundary_time>s [<from_label> → <to_label>, beat: <from_clarity> → <to_clarity>] — <coaching>\n\n"
    "The `<from_label>` / `<to_label>` slots are section names from the "
    "transitions list (`intro`, `main`, `break`, `short_break`, `build`, "
    "`peak`, `outro`, `instrumental`). Beat-clarity tags are "
    "`subtle` / `moderate` / `clear`. Quote the boundary time exactly as "
    "it appears in the transitions list.\n\n"
    "Coaching shape:\n"
    "- Lead with **re-entry** — what the learner does once they notice "
    "  the new section has arrived. Use the bachata basic vocabulary "
    "  (1-2-3-tap, 5-6-7-tap, hip on 4 and 8) when it sharpens the cue. "
    "  Every T# line must include a re-entry cue.\n"
    "- Add an **audible cue** for anticipation ONLY when the section "
    "  properties make one obvious. Examples by contrast direction:\n"
    "    * High-energy → low-energy (main → break, main → outro): "
    "      'as the percussion thins and the güira drops out'.\n"
    "    * Low-energy → medium/high-energy (intro → main, break → main): "
    "      'when the güira pattern returns', 'when the bongo kicks in'.\n"
    "    * Vocals → instrumental boundary: 'when the vocals drop out'.\n"
    "    * Instrumental → vocals: 'when the vocals come back in'.\n"
    "  When you cannot compose a specific audible cue from the section "
    "  properties, OMIT anticipation and lead with re-entry only — do "
    "  NOT invent generic anticipation language.\n"
    "- For `<from>` → `break` transitions: re-entry = shrink the basic "
    "  to a small weight shift, keep the 8-count alive in the body, "
    "  listen. Do NOT default to 'pause and hold' unless the break is "
    "  `beat: subtle`.\n"
    "- For `break` → `<to>` transitions: re-entry = restart the 8-count "
    "  on the next clear 1; land the basic on 1, tap on 4. Don't chase "
    "  the loudest re-entry hit — wait for the steady güira/bongo pulse.\n"
    "- For `<from>` → `peak` or `<from>` → `build`: re-entry = commit to "
    "  the new energy, travel more, add hip on 4 and 8 once the count "
    "  feels automatic.\n"
    "- For `peak` → `<to>`: re-entry = settle back to the basic, breath, "
    "  return to a clean 1-2-3-tap.\n"
    "- For `intro` → `main`: re-entry = land the basic on the next clear "
    "  1; the güira pattern usually anchors it.\n"
    "- For `<from>` → `outro`: re-entry = contract movement, finish on a "
    "  clean 8, prepare to close.\n"
    "- For `<from>` → `instrumental` or `instrumental` → `<to>`: re-entry "
    "  = keep the 1-2-3-tap basic going steadily; the instrumental is "
    "  medium-energy, not low.\n"
    "- For **same-label** transitions where `<from_label>` == `<to_label>` "
    "  (typically `main → main` with an energy shift): coach the *role "
    "  shift*. When energy lifts (medium → high), re-enter by traveling "
    "  more and adding hip on 4 and 8. When energy settles (high → "
    "  medium), re-enter by returning to a compact basic, hold a steady "
    "  frame, reconnect with the partner. Name a specific audible cue "
    "  (güira density, bongo entering, vocal taking more space) when the "
    "  energy delta supports it; otherwise lead with re-entry only. Keep "
    "  these lines short — one sentence is usually enough.\n"
    "- For transitions where beat-clarity drops (e.g. `clear → subtle`): "
    "  add a recovery cue — shrink the basic, count 8 internally, wait "
    "  for the next clearer phase to re-enter on a fresh 1.\n"
    "- Treat exact moves as examples, not commands. Prefer movement "
    "  strategy plus one safe option.\n"
    f"- {_METRIC_GUARD_RULE} The boundary time in the T# header is enough "
    "numeric grounding.\n"
    "- Total answer under 220 words. No intro, no outro — just the "
    "  T# lines, one per transition."
)


ALL_QUESTIONS = {
    "time_signature": QUESTION_TIME_SIGNATURE,
    "counting": QUESTION_COUNTING,
    "style_fit": QUESTION_STYLE_FIT,
    "difficulty": QUESTION_DIFFICULTY,
    "exercise": QUESTION_EXERCISE,
    "dancer": QUESTION_DANCER,
    "song_arc": QUESTION_SONG_ARC,
    "sections": QUESTION_SECTIONS,
    "rhythm_anatomy": QUESTION_RHYTHM_ANATOMY,
    "listening_guide": QUESTION_LISTENING_GUIDE,
    "kizomba_tutor": QUESTION_KIZOMBA_TUTOR,
    "kizomba_drills": QUESTION_KIZOMBA_DRILLS,
    "kizomba_transitions": QUESTION_KIZOMBA_TRANSITIONS,
    "bachata_tutor": QUESTION_BACHATA_TUTOR,
    "bachata_drills": QUESTION_BACHATA_DRILLS,
    "bachata_transitions": QUESTION_BACHATA_TRANSITIONS,
}

# Keep old name around for backwards compatibility in tests
QUESTION_STYLE = QUESTION_STYLE_FIT


def _format_style_section(
    dance_style: str | None,
    style_context: str | None,
    basic_step: str | None = None,
) -> str:
    """Build the dance style context block for the analysis template.

    Returns empty string when ``dance_style`` is None so callers without a
    style produce an unchanged prompt.
    """
    if not dance_style:
        return ""

    lines = [f"- Dance style (user-specified): {dance_style}"]
    if style_context:
        lines.append(f"- Style context: {style_context}")
    if basic_step:
        lines.append(f"- IMPORTANT basic step rule: {basic_step}")
    return "\n".join(lines) + "\n"


def format_analysis_prompt(
    duration: float,
    tempo: float,
    n_beats: int,
    n_onsets: int,
    beat_times,
    ioi_ms,
    question: str,
    beats_per_measure: int = 4,
    phrase_length: int = 8,
    downbeat_times=None,
    downbeat_confidence: float | None = None,
    vocals=None,
    rhythm_features=None,
    tempo_half: float | None = None,
    dance_style: str | None = None,
    style_context: str | None = None,
    sections: list[SongSection] | None = None,
    style_profile: StyleProfile | None = None,
    phases: list[SongPhase] | None = None,
    basic_step: str | None = None,
    include_same_label_transitions: bool = False,
    include_phase_features: bool = False,
    include_phase_vocal: bool = False,
) -> str:
    """Format a RhythmAnalysis into a text prompt for Gemma.

    Beat times are rounded to 0.05s and IOIs to 5ms to avoid false precision
    (librosa's hop-based resolution is ~23ms).

    ``downbeat_times`` and ``downbeat_confidence`` are optional.  When provided
    for non-kizomba styles, the prompt includes the likely "1" positions and a
    confidence label, and adds an explicit uncertainty note when confidence is
    below the low threshold.  For kizomba, this block is omitted because the
    prompts intentionally keep beat-position anchoring out of scope.

    ``vocals`` is an optional ``VocalsInfo`` from the Gemma audio perception
    pass (``rytmi.transcribe.transcribe_vocals``).  When provided, the prompt
    includes the detected vocal language (and optional lyric snippet) so the
    reasoning stage can use language as a prior for dance-style disambiguation.

    ``rhythm_features`` is an optional ``RhythmFeatures`` from the DSP pipeline.
    When provided, the prompt includes onset density, percussiveness, beat accent
    pattern, and other features for style disambiguation in BPM-overlap zones.

    ``dance_style`` is the user-specified dance style (e.g. "bachata", "kizomba").
    ``style_context`` is an optional style description injected into the prompt.
    When ``dance_style`` is provided, style-parameterized questions (``{style}``)
    are filled in automatically.

    ``sections`` is an optional list of ``SongSection`` from the DSP pipeline.
    ``style_profile`` is an optional ``StyleProfile`` used to add per-section
    coaching hints.

    Callers that omit these parameters get the original prompt unchanged —
    backwards-compatible by design.
    """
    beat_str = ", ".join(f"{round(t / 0.05) * 0.05:.2f}" for t in beat_times[:8])
    if n_beats > 8:
        beat_str += f" ... ({n_beats} total)"

    if ioi_ms is not None and len(ioi_ms) > 0:
        ioi_str = ", ".join(f"{round(v / 5) * 5:.0f}" for v in ioi_ms[:8])
        if len(ioi_ms) > 8:
            ioi_str += f" ... ({len(ioi_ms)} intervals)"
    else:
        ioi_str = "N/A"

    measures_per_phrase = (
        phrase_length // beats_per_measure if beats_per_measure > 0 else 0
    )

    style_name = (dance_style or "").lower().strip()
    downbeat_section = (
        ""
        if style_name == "kizomba"
        else _format_downbeat_section(downbeat_times, downbeat_confidence)
    )
    vocals_section = _format_vocals_section(vocals)
    rhythm_features_section = _format_rhythm_features_section(rhythm_features, tempo_half)
    distinct_features_section = _format_distinct_features_section(
        tempo, rhythm_features, style_profile
    )
    sections_block = _format_sections_block(
        sections, style_profile, phases,
        include_phase_features=include_phase_features,
        include_phase_vocal=include_phase_vocal,
    )
    transitions_section = _format_transitions_block(
        phases, include_same_label=include_same_label_transitions,
    )
    style_section = _format_style_section(dance_style, style_context, basic_step)

    # Fill in {style} placeholders in the question when a dance style is provided.
    if dance_style and "{style}" in question:
        question = question.replace("{style}", dance_style)

    return RHYTHM_ANALYSIS_TEMPLATE.format(
        duration=duration,
        tempo=tempo,
        n_beats=n_beats,
        n_onsets=n_onsets,
        beat_times=beat_str,
        ioi_summary=ioi_str,
        beats_per_measure=beats_per_measure,
        phrase_length=phrase_length,
        measures_per_phrase=measures_per_phrase,
        downbeat_section=downbeat_section,
        vocals_section=vocals_section,
        rhythm_features_section=rhythm_features_section,
        distinct_features_section=distinct_features_section,
        sections_block=sections_block,
        transitions_section=transitions_section,
        style_section=style_section,
        question=question,
    )


# ── Phase 11d: regex grounding verifier ───────────────────────────────────────
# Post-generation pass on the QUESTION_SECTIONS answer.  Each `P#:` line MUST
# include at least one numeric anchor in its coaching tail (the part after the
# em-dash); otherwise the line is a generic platitude and gets replaced with
# the Phase-10c fallback line so a downstream learner never sees the bare
# style-level claim.

_P_LINE_RE = re.compile(
    r"^\s*(?P<head>(?:[*-]\s*)?P\d+(?:[-–]\d+)?\s*:\s*.+?)"
    r"\s+(?:[—–]|-)\s+(?P<tail>.+)$"
)

_KIZOMBA_DRILL_LINE_RE = re.compile(
    r"^\s*(?:[*-]\s*)?P(?P<start>\d+)"
    r"(?:\s*[-–]\s*P?(?P<end>\d+))?\s*:\s*"
    r"(?P<section>[A-Za-z_]+)(?:\s*×\d+)?\s*"
    r"\(\s*\d+(?:\.\d+)?s\s*[-–]\s*\d+(?:\.\d+)?s\s*,\s*"
    r"beat:\s*(?P<beat>subtle|moderate|clear)\s*\)"
    r"\s+(?:[—–]|-)\s*(?P<tail>.+)$",
    re.IGNORECASE,
)

_NUMERIC_ANCHOR_RE = re.compile(
    r"(?:"
    r"\b\d+(?:\.\d+)?\s*(?:s|sec|secs|seconds|BPM|Hz|%)\b"      # "45s", "128 BPM", "0.8%"
    r"|\b[MPS]\d+\b"                                             # "M84", "P11", "S3"
    r"|\b\d{1,2}:\d{2}\b"                                        # "02:50"
    r"|\b\d+(?:\.\d+)?\s*(?:ratio|x)\b"                          # "1.4 ratio", "2.5x"
    r"|\b\d+\s*(?:bars?|phrases?|beats?|counts?|measures?)\b"    # "4 bars", "8 phrases"
    r"|\[[\d.,\s]+\]"                                            # "[1.00, 0.98, 0.97, 0.79]"
    r")",
    re.IGNORECASE,
)


@dataclass
class VerifiedSectionsOutput:
    """Result of the regex grounding pass over a SECTIONS answer.

    ``cleaned`` keeps every passing P# line as-is and replaces failing ones
    with the Phase-10c fallback (`P#: <s>s–<e>s, <label> — continues the
    <prev_label> feel`).  Non-P# lines (intro/outro sentences the prompt
    forbids but Gemma sometimes still emits) are dropped from ``cleaned``
    so the verifier output is the canonical learner-facing answer.

    ``stats`` is a small dict suitable for logging: ``passed`` /
    ``failed`` / ``replaced`` counts and ``pass_rate`` in [0, 1].
    """

    original: str
    cleaned: str
    stats: dict = field(default_factory=dict)


@dataclass
class VerifiedKizombaDrillsOutput:
    """Result of the structural pass over a KIZOMBA_DRILLS answer.

    ``cleaned`` preserves parsed drill text where it still matches the DSP
    phase structure, but normalizes P# ranges so they cannot cross section
    labels, cannot duplicate phases, and cover missing phases with a simple
    deterministic fallback line.
    """

    original: str
    cleaned: str
    stats: dict = field(default_factory=dict)


@dataclass
class VerifiedKizombaTransitionsOutput:
    """Result of the structural pass over a KIZOMBA_TRANSITIONS answer.

    Phase 40 — checks every T# entry against the algorithmically-extracted
    transition list (``extract_transitions(analysis.phases)``).  Drops T#
    entries whose boundary time matches no real transition (within ±2.0s
    tolerance for rounding).  Fills any extracted transition the model
    skipped with a deterministic template line so the output covers every
    label boundary in the song.

    ``stats`` keys: ``parsed``, ``boundaries_matched``,
    ``boundaries_invented``, ``boundaries_missing_filled``,
    ``skipped_lines``, ``output_lines``. When a ``retry_callback`` is
    supplied to ``verify_kizomba_transitions_output``, additional keys
    ``retried`` (boundaries that triggered a retry) and ``retry_succeeded``
    (retries that produced a valid line accepted in place of the
    deterministic fallback) are included.
    """

    original: str
    cleaned: str
    stats: dict = field(default_factory=dict)


def _has_numeric_anchor(text: str) -> bool:
    """True if ``text`` contains at least one numeric anchor we recognise."""
    return bool(_NUMERIC_ANCHOR_RE.search(text))


def _section_at(sections: "list[SongSection] | None", index: int) -> "SongSection | None":
    if not sections:
        return None
    if 0 <= index < len(sections):
        return sections[index]
    return None


def _phase_beat_tag(phase: "SongPhase") -> str:
    rhythm_features = getattr(phase, "avg_rhythm_features", None)
    if rhythm_features is None:
        return "clear"
    return _beat_clarity_tag(rhythm_features.beat_clarity)


def _normalize_section_label(label: str) -> str:
    return label.strip().lower().replace("-", "_")


def _format_phase_ref(start_idx: int, end_idx: int) -> str:
    start_ref = f"P{start_idx + 1}"
    if start_idx == end_idx:
        return start_ref
    return f"{start_ref}-P{end_idx + 1}"


def _format_phase_seconds(seconds: float) -> str:
    return f"{seconds:.0f}s"


def _format_kizomba_drill_line(
    phases: "list[SongPhase]",
    start_idx: int,
    end_idx: int,
    tail: str,
) -> str:
    start_phase = phases[start_idx]
    end_phase = phases[end_idx]
    section = _normalize_section_label(start_phase.label)
    beat_tag = _phase_beat_tag(start_phase)
    return (
        f"{_format_phase_ref(start_idx, end_idx)}: {section} "
        f"({_format_phase_seconds(start_phase.start_s)}-"
        f"{_format_phase_seconds(end_phase.end_s)}, beat: {beat_tag}) — "
        f"{tail.strip()}"
    )


def _fallback_kizomba_drill_tail(phase: "SongPhase") -> str:
    section = _normalize_section_label(phase.label)
    beat_tag = _phase_beat_tag(phase)
    duration_s = max(1, round(phase.end_s - phase.start_s))

    if section in {"break", "short_break"}:
        action = "reduce travel and keep a small pulse in the body to reset"
    elif section == "outro":
        action = "reduce travel and let the movement wind down"
    elif beat_tag == "subtle":
        action = "keep movement minimal and mark the pulse in place"
    elif beat_tag == "moderate":
        action = "stay compact and test the pulse with small steps"
    else:
        action = "practice steady weight transfers through this section"

    return f"Drill: {action}. {duration_s}s."


def _uncovered_phase_runs(
    start_idx: int,
    end_idx: int,
    covered_phases: set[int],
) -> list[tuple[int, int]]:
    runs: list[tuple[int, int]] = []
    run_start: int | None = None

    for phase_idx in range(start_idx, end_idx + 1):
        if phase_idx in covered_phases:
            if run_start is not None:
                runs.append((run_start, phase_idx - 1))
                run_start = None
            continue
        if run_start is None:
            run_start = phase_idx

    if run_start is not None:
        runs.append((run_start, end_idx))
    return runs


def _fallback_p_line(
    head: str,
    sections: "list[SongSection] | None",
    line_idx: int,
) -> str:
    """Build the Phase-10c fallback line for a failing P# entry.

    ``head`` is the verbatim P#-prefix-and-label part the model already
    emitted (e.g. ``"P3-5: 45s-110s, main"``); we keep it so the cleaned
    output preserves the model's grouping.  When ``sections`` are
    available we look up the previous section's label for the
    ``continues the <prev_label> feel`` tail; otherwise we fall back to
    ``"the previous"``.
    """
    prev = _section_at(sections, line_idx - 1)
    prev_label = prev.label if prev is not None else "previous"
    return f"{head.strip()} — continues the {prev_label} feel"


def verify_sections_output(
    raw_answer: str,
    sections: "list[SongSection] | None" = None,
) -> VerifiedSectionsOutput:
    """Check QUESTION_SECTIONS output for numeric anchors per `P#:` line.

    Walks the raw answer line by line.  Lines that match the
    ``P#: ... — coaching`` shape get their tail checked against
    ``_NUMERIC_ANCHOR_RE``; failing lines are replaced with the
    Phase-10c ``continues the <prev_label> feel`` fallback.  Lines that
    don't match the P# shape (the prompt forbids them, but Gemma
    occasionally emits an intro/outro sentence) are dropped from
    ``cleaned`` so the learner never sees them.
    """
    raw = raw_answer or ""
    passed = 0
    failed = 0
    replaced_lines: list[str] = []
    line_idx = 0

    for raw_line in raw.splitlines():
        line = raw_line.rstrip()
        if not line.strip():
            continue

        m = _P_LINE_RE.match(line)
        if not m:
            continue

        head = m.group("head")
        tail = m.group("tail")
        if _has_numeric_anchor(tail):
            replaced_lines.append(line.lstrip())
            passed += 1
        else:
            replaced_lines.append(_fallback_p_line(head, sections, line_idx))
            failed += 1
        line_idx += 1

    total = passed + failed
    pass_rate = (passed / total) if total else 0.0
    stats = {
        "total": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": pass_rate,
    }
    cleaned = "\n".join(replaced_lines)
    return VerifiedSectionsOutput(original=raw, cleaned=cleaned, stats=stats)


def verify_kizomba_drills_output(
    raw_answer: str,
    phases: "list[SongPhase] | None" = None,
) -> VerifiedKizombaDrillsOutput:
    """Normalize KIZOMBA_DRILLS output against the DSP phase structure.

    Gemma is useful for writing learner-facing drill text, but live runs showed
    it can still produce invalid structure such as `P7-P8: main` followed by
    `P8: outro`. This pass keeps the model's drill text when the range matches
    real same-label/same-beat phases, shrinks invalid ranges at the first label
    or beat-tag boundary, skips duplicate phase coverage, and fills missing
    phases with deterministic fallback drills.
    """
    raw = raw_answer or ""
    if not phases:
        return VerifiedKizombaDrillsOutput(original=raw, cleaned=raw.strip(), stats={})

    emitted_lines: list[tuple[int, int, str]] = []
    covered_phases: set[int] = set()
    parsed = 0
    repaired_ranges = 0
    duplicate_phases = 0
    skipped_lines = 0

    for raw_line in raw.splitlines():
        line = raw_line.rstrip()
        if not line.strip():
            continue

        match = _KIZOMBA_DRILL_LINE_RE.match(line)
        if not match:
            continue

        parsed += 1
        start_idx = int(match.group("start")) - 1
        end_ref = match.group("end") or match.group("start")
        end_idx = int(end_ref) - 1

        if start_idx < 0 or start_idx >= len(phases) or end_idx < start_idx:
            skipped_lines += 1
            continue
        if end_idx >= len(phases):
            end_idx = len(phases) - 1
            repaired_ranges += 1

        emitted_section = _normalize_section_label(match.group("section"))
        expected_section = _normalize_section_label(phases[start_idx].label)
        if emitted_section != expected_section:
            repaired_ranges += 1
            skipped_lines += 1
            continue

        expected_beat = _phase_beat_tag(phases[start_idx])
        emitted_beat = match.group("beat").lower()
        if emitted_beat != expected_beat:
            repaired_ranges += 1

        usable_end_idx = start_idx
        for phase_idx in range(start_idx + 1, end_idx + 1):
            same_section = _normalize_section_label(phases[phase_idx].label) == expected_section
            same_beat = _phase_beat_tag(phases[phase_idx]) == expected_beat
            if not (same_section and same_beat):
                break
            usable_end_idx = phase_idx

        if usable_end_idx != end_idx:
            repaired_ranges += 1

        duplicate_phases += sum(
            1 for phase_idx in range(start_idx, usable_end_idx + 1)
            if phase_idx in covered_phases
        )
        new_runs = _uncovered_phase_runs(start_idx, usable_end_idx, covered_phases)
        if not new_runs:
            skipped_lines += 1
            continue

        tail = match.group("tail").strip()
        for run_start_idx, run_end_idx in new_runs:
            emitted_lines.append((run_start_idx, run_end_idx, tail))
            covered_phases.update(range(run_start_idx, run_end_idx + 1))

    if parsed == 0:
        stats = {
            "parsed": 0,
            "repaired_ranges": 0,
            "duplicate_phases": 0,
            "filled_missing": 0,
            "skipped_lines": 0,
            "output_lines": 0,
        }
        return VerifiedKizombaDrillsOutput(original=raw, cleaned=raw.strip(), stats=stats)

    filled_missing = 0
    for phase_idx, phase in enumerate(phases):
        if phase_idx in covered_phases:
            continue
        emitted_lines.append((phase_idx, phase_idx, _fallback_kizomba_drill_tail(phase)))
        covered_phases.add(phase_idx)
        filled_missing += 1

    emitted_lines.sort(key=lambda item: (item[0], item[1]))
    cleaned = "\n".join(
        _format_kizomba_drill_line(phases, start_idx, end_idx, tail)
        for start_idx, end_idx, tail in emitted_lines
    )
    stats = {
        "parsed": parsed,
        "repaired_ranges": repaired_ranges,
        "duplicate_phases": duplicate_phases,
        "filled_missing": filled_missing,
        "skipped_lines": skipped_lines,
        "output_lines": len(emitted_lines),
    }
    return VerifiedKizombaDrillsOutput(original=raw, cleaned=cleaned, stats=stats)


# ── Phase 40: kizomba_transitions structural verifier ────────────────────────

_KIZOMBA_TRANSITION_LINE_RE = re.compile(
    r"^\s*(?:[*-]\s*)?T(?P<num>\d+)\s*:\s*"
    r"(?P<time>\d+(?:\.\d+)?)\s*s\s*"
    r"\[\s*(?P<from_label>[A-Za-z_]+)\s*"
    r"(?:→|->|—>|–>)\s*"
    r"(?P<to_label>[A-Za-z_]+)\s*,\s*"
    r"beat\s*:\s*(?P<from_beat>subtle|moderate|clear)\s*"
    r"(?:→|->|—>|–>)\s*"
    r"(?P<to_beat>subtle|moderate|clear)\s*\]"
    r"\s*(?:[—–]|-)\s*(?P<tail>.+)$",
    re.IGNORECASE,
)

# Phase 40d — P# line regex matching the kizomba_tutor output format.
# Format: `P#: <start>s-<end>s, <section>[ ×N] [beat: <clarity>] — <coaching>`
_KIZOMBA_TUTOR_P_LINE_RE = re.compile(
    r"^\s*(?:[*-]\s*)?P(?P<num>\d+)\s*:\s*"
    r"(?P<start>\d+(?:\.\d+)?)\s*s\s*[-–]\s*"
    r"(?P<end>\d+(?:\.\d+)?)\s*s\s*,\s*"
    r"(?P<section>[A-Za-z_]+)(?:\s*×\d+)?\s*"
    r"\[\s*beat\s*:\s*(?P<beat>subtle|moderate|clear)\s*\]"
    r"\s*(?:[—–]|-)\s*(?P<tail>.+)$",
    re.IGNORECASE,
)

_TRANSITION_BOUNDARY_TOLERANCE_S = 2.0


def _fallback_transition_tail(transition: "Transition") -> str:
    """Deterministic coaching text used when the model skips a transition.

    Phase 40c rule: re-entry-primary, audible-cue-secondary, never
    count-based. Mirrors the prompt's branch language so the fallback
    reads consistently with what Gemma produces. Gemma's coaching is
    preferred when present; this is the structural fallback only.
    """
    from_label = transition.from_label
    to_label = transition.to_label

    if to_label in ("break", "short_break"):
        return (
            "as the energy fades and the percussion thins, keep a small "
            "pulse in the body, listen, and reset."
        )
    if from_label in ("break", "short_break"):
        return (
            "walk-step on the first clear bass hit; don't chase the "
            "louder percussion."
        )
    if to_label in ("peak", "build"):
        return (
            "as the music pulls you forward, commit to the new energy, "
            "travel more, and add intention."
        )
    if from_label == "peak":
        return "settle back, breathe, and return to the basic."
    if to_label == "outro":
        return (
            "as the energy fades, contract your movement, slow the "
            "basic, and prepare to close."
        )
    if from_label == "intro":
        return "when the bass kicks in, walk-step the basic on the first clear bass hit."
    if to_label == "instrumental" or from_label == "instrumental":
        return "keep your basic going steadily through the instrumental."
    # Same-label or generic energy-shift fallback. Use the role-shift
    # vocabulary from the prompt's same-label branch — coach via re-entry
    # without naming an audible cue we cannot guarantee from labels alone.
    return "as the energy shifts, keep the basic and hold a steady frame."


def _format_transition_line(transition: "Transition", num: int, tail: str) -> str:
    return (
        f"T{num}: {transition.boundary_time_s:.0f}s "
        f"[{transition.from_label} → {transition.to_label}, "
        f"beat: {transition.from_clarity} → {transition.to_clarity}] — {tail}"
    )


# ── Phase 40e: Gemma-retry prompt for missing/malformed transitions ──────────
#
# Used when ``verify_kizomba_transitions_output`` ends up with a boundary that
# would otherwise be filled by ``_fallback_transition_tail``. The retry asks
# Gemma to write *just one* T# line for a single boundary, with the bracket
# pre-built and the re-entry-primary rule restated. The verifier accepts the
# retry only if it parses cleanly and matches the requested boundary — the
# deterministic fallback is the safety net.

_KIZOMBA_TRANSITION_RETRY_PROMPT_TEMPLATE = """\
You are coaching a kizomba dancer through one transition between two phases of
a song. Write exactly ONE coaching line in this format and nothing else:

T{idx}: {time_s}s [{from_label} → {to_label}, beat: {from_clarity} → {to_clarity}] — <one-sentence coaching>

Rules for the coaching sentence:
- Be RE-ENTRY PRIMARY: describe what the dancer does ON entering the new \
phase, not what to anticipate before it.
- Anchor on a concrete audible cue when you can name one safely (e.g. \
"on the first clear bass hit", "as the percussion thins", "as the energy \
fades"). If no safe cue exists, coach the body action directly.
- NEVER use count-based anticipation language. Forbidden: "in the last \
8-count of …", "after N beats", "in the final …", "counts before …", \
"eight-count".
- NEVER name "the 1" or a downbeat — kizomba downbeat detection is unreliable.
- Keep it to ONE sentence, ≤ 25 words, lowercase after the em-dash.

Output ONLY the line above. No preamble, no explanation, no extra lines.
"""


def build_kizomba_transition_retry_prompt(
    transition: "Transition", idx: int
) -> str:
    """Build the per-boundary retry prompt for one kizomba transition.

    Phase 40e — used by ``verify_kizomba_transitions_output`` when a
    ``retry_callback`` is supplied and a boundary would otherwise be
    filled with the deterministic fallback. Honest with the model about
    the bracket it must produce so the parser accepts the retry.
    """
    return _KIZOMBA_TRANSITION_RETRY_PROMPT_TEMPLATE.format(
        idx=idx,
        time_s=f"{transition.boundary_time_s:.0f}",
        from_label=transition.from_label,
        to_label=transition.to_label,
        from_clarity=transition.from_clarity,
        to_clarity=transition.to_clarity,
    )


def _try_retry_transition(
    transition: "Transition",
    idx: int,
    retry_callback,
) -> str | None:
    """Attempt a one-shot Gemma retry for a single transition.

    Returns the parsed coaching tail on success, or ``None`` if the retry
    raised, returned empty, failed to parse, or matched the wrong
    boundary. Caller falls through to the deterministic fallback when
    this returns ``None``.
    """
    prompt = build_kizomba_transition_retry_prompt(transition, idx + 1)
    try:
        response = retry_callback(prompt) or ""
    except Exception:  # noqa: BLE001 — retry is best-effort; fail to fallback
        return None
    for raw_line in response.splitlines():
        match = _KIZOMBA_TRANSITION_LINE_RE.match(raw_line.rstrip())
        if not match:
            continue
        time_quoted = float(match.group("time"))
        if abs(transition.boundary_time_s - time_quoted) > _TRANSITION_BOUNDARY_TOLERANCE_S:
            continue
        tail = match.group("tail").strip()
        if tail:
            return tail
    return None


def verify_kizomba_transitions_output(
    raw_answer: str,
    transitions: "list[Transition] | None" = None,
    *,
    retry_callback=None,
) -> VerifiedKizombaTransitionsOutput:
    """Normalize KIZOMBA_TRANSITIONS output against the extracted transitions.

    Phase 40 — Gemma writes per-transition coaching anchored on each
    boundary time from the analysis dump's transitions block. This pass
    drops T# entries whose boundary time doesn't match any real transition
    (within ±2.0s tolerance for rounding) and fills missing transitions
    with deterministic template text.

    Phase 40e — when ``retry_callback`` is supplied (a callable taking a
    prompt string and returning Gemma's response), each missing boundary
    is given one chance to be filled by Gemma instead of the deterministic
    fallback. The retry uses ``build_kizomba_transition_retry_prompt`` and
    is accepted only if the response parses cleanly and matches the
    requested boundary. Stats include ``retried`` and ``retry_succeeded``
    when a callback is supplied. ``boundaries_missing_filled`` counts only
    deterministic fallback fills — successful retries are Gemma's writing
    and are not counted as fills.
    """
    raw = raw_answer or ""
    if not transitions:
        return VerifiedKizombaTransitionsOutput(
            original=raw, cleaned=raw.strip(), stats={}
        )

    parsed = 0
    boundaries_matched = 0
    boundaries_invented = 0
    skipped_lines = 0

    # transition_idx → (tail, original_T#) so we can preserve user-facing text
    # and re-number sequentially based on chronological transition order.
    matched_tails: dict[int, str] = {}

    for raw_line in raw.splitlines():
        line = raw_line.rstrip()
        if not line.strip():
            continue

        match = _KIZOMBA_TRANSITION_LINE_RE.match(line)
        if not match:
            # Lines that don't parse are not counted as parsed; only T# header
            # candidates that fail the regex are noted as skipped.
            if line.lstrip().lower().startswith("t") and ":" in line:
                skipped_lines += 1
            continue

        parsed += 1
        time_quoted = float(match.group("time"))

        # Find the closest extracted transition by boundary time.
        best_idx = -1
        best_delta = float("inf")
        for idx, tr in enumerate(transitions):
            delta = abs(tr.boundary_time_s - time_quoted)
            if delta < best_delta:
                best_delta = delta
                best_idx = idx

        if best_delta > _TRANSITION_BOUNDARY_TOLERANCE_S or best_idx < 0:
            boundaries_invented += 1
            continue

        tail = match.group("tail").strip()
        if best_idx in matched_tails:
            # Duplicate coverage — skip silently; first match wins.
            skipped_lines += 1
            continue
        matched_tails[best_idx] = tail
        boundaries_matched += 1

    boundaries_missing_filled = 0
    retried = 0
    retry_succeeded = 0
    for idx, tr in enumerate(transitions):
        if idx in matched_tails:
            continue
        retry_tail: str | None = None
        if retry_callback is not None:
            retried += 1
            retry_tail = _try_retry_transition(tr, idx, retry_callback)
            if retry_tail is not None:
                retry_succeeded += 1
        if retry_tail is not None:
            matched_tails[idx] = retry_tail
        else:
            matched_tails[idx] = _fallback_transition_tail(tr)
            boundaries_missing_filled += 1

    cleaned = "\n".join(
        _format_transition_line(transitions[idx], idx + 1, matched_tails[idx])
        for idx in range(len(transitions))
    )

    stats = {
        "parsed": parsed,
        "boundaries_matched": boundaries_matched,
        "boundaries_invented": boundaries_invented,
        "boundaries_missing_filled": boundaries_missing_filled,
        "skipped_lines": skipped_lines,
        "output_lines": len(transitions),
    }
    if retry_callback is not None:
        stats["retried"] = retried
        stats["retry_succeeded"] = retry_succeeded
    return VerifiedKizombaTransitionsOutput(
        original=raw, cleaned=cleaned, stats=stats
    )


# ── Phase 40d: unified timeline post-processor ───────────────────────────────

def format_unified_timeline(tutor_text: str, transitions_text: str) -> str:
    """Interleave kizomba_tutor's P# lines with kizomba_transitions' T# lines
    in chronological order.

    Pure post-processing; no LLM call.  Produces a single learner-facing
    narrative — P1 is followed by T1 (the bridge into P2), then P2, then
    T2 (the bridge into P3), and so on.  T# lines anchor at their boundary
    time; P# lines anchor at their start time.  At equal times, the T#
    line appears before the P# that starts at that boundary so the
    transition reads as the bridge into the next phase.

    Falls back to printing the two outputs separately under headers when
    the tutor text yields no parseable P# lines (preserves all content so
    the caller still sees coaching even on format drift).
    """
    tutor_text = tutor_text or ""
    transitions_text = transitions_text or ""

    p_entries: list[tuple[float, str]] = []
    for raw_line in tutor_text.splitlines():
        line = raw_line.rstrip()
        if not line.strip():
            continue
        match = _KIZOMBA_TUTOR_P_LINE_RE.match(line)
        if match is None:
            continue
        start_s = float(match.group("start"))
        p_entries.append((start_s, line.strip()))

    if not p_entries:
        # Format drift on tutor output — fall back to passthrough so the
        # caller still sees the coaching content.
        parts: list[str] = []
        if tutor_text.strip():
            parts.append("--- kizomba_tutor ---")
            parts.append(tutor_text.strip())
        if transitions_text.strip():
            parts.append("--- kizomba_transitions ---")
            parts.append(transitions_text.strip())
        return "\n".join(parts)

    t_entries: list[tuple[float, str]] = []
    for raw_line in transitions_text.splitlines():
        line = raw_line.rstrip()
        if not line.strip():
            continue
        match = _KIZOMBA_TRANSITION_LINE_RE.match(line)
        if match is None:
            continue
        boundary_s = float(match.group("time"))
        t_entries.append((boundary_s, line.strip()))

    # Sort by time; at equal times, T# (kind=0) precedes P# (kind=1) so
    # the transition reads as the bridge into the next phase.
    timeline: list[tuple[float, int, str]] = []
    timeline.extend((time_s, 1, line) for time_s, line in p_entries)
    timeline.extend((time_s, 0, line) for time_s, line in t_entries)
    timeline.sort(key=lambda item: (item[0], item[1]))

    return "\n".join(line for _t, _k, line in timeline)
