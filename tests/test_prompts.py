"""Tests for prompt templates and formatting helpers (Phase 10c)."""

from rytmi.prompts import (
    ALL_QUESTIONS,
    KIZOMBA_TUTOR_POLISH_SYSTEM,
    QUESTION_BACHATA_DRILLS,
    QUESTION_BACHATA_TUTOR,
    QUESTION_DANCER,
    QUESTION_KIZOMBA_DRILLS,
    QUESTION_KIZOMBA_TRANSITIONS,
    QUESTION_KIZOMBA_TUTOR,
    QUESTION_LISTENING_GUIDE,
    QUESTION_RHYTHM_ANATOMY,
    QUESTION_SECTIONS,
    QUESTION_SONG_ARC,
    _KIZOMBA_DOWNBEAT_GUARD_RULE,
    _METRIC_GUARD_RULE,
    _format_distinct_features_section,
    _format_rhythm_features_section,
    _format_sections_block,
    _format_transitions_block,
    _has_numeric_anchor,
    build_kizomba_tutor_polish_prompt,
    format_unified_timeline,
    verify_kizomba_drills_output,
    verify_kizomba_transitions_output,
    verify_sections_output,
)
from rytmi.styles import BACHATA_PROFILE, KIZOMBA_PROFILE
from rytmi.types import RhythmFeatures, SongPhase, SongSection, Transition


def _mid_rf(**overrides) -> RhythmFeatures:
    """Mid-of-the-road rhythm features that trigger no outliers by default."""
    defaults = dict(
        onsets_per_beat=2.0,
        beat_strength_pattern=[1.0, 0.5, 0.7, 0.3],
        percussiveness=0.45,
        spectral_centroid_mean=2000.0,
        tempo_stability=0.05,
        ioi_median_ms=250.0,
        ioi_std_ms=40.0,
    )
    defaults.update(overrides)
    return RhythmFeatures(**defaults)


def _phase(label: str, start_s: float, end_s: float, beat_clarity: float = 0.45) -> SongPhase:
    return SongPhase(
        label=label,
        start_s=start_s,
        end_s=end_s,
        section_count=1,
        energy_levels=["medium"],
        avg_rhythm_features=_mid_rf(beat_clarity=beat_clarity),
    )


# ── _format_distinct_features_section ─────────────────────────────────────────


def test_distinct_features_block_highlights_percussiveness_outlier():
    rf = _mid_rf(percussiveness=0.72)
    out = _format_distinct_features_section(
        tempo=128.0, rhythm_features=rf, style_profile=BACHATA_PROFILE
    )
    assert "Percussiveness 0.72" in out
    assert "unusually high" in out
    assert out.startswith("Distinctive features")


def test_distinct_features_block_highlights_low_percussiveness():
    rf = _mid_rf(percussiveness=0.18)
    out = _format_distinct_features_section(
        tempo=100.0, rhythm_features=rf, style_profile=KIZOMBA_PROFILE
    )
    assert "Percussiveness 0.18" in out
    assert "unusually low" in out


def test_distinct_features_block_highlights_dense_onsets():
    rf = _mid_rf(onsets_per_beat=3.4)
    out = _format_distinct_features_section(
        tempo=128.0, rhythm_features=rf, style_profile=BACHATA_PROFILE
    )
    assert "Onset density 3.4" in out
    assert "unusually dense" in out


def test_distinct_features_block_highlights_tempo_above_range():
    rf = _mid_rf()
    out = _format_distinct_features_section(
        tempo=150.0, rhythm_features=rf, style_profile=BACHATA_PROFILE
    )
    assert "150 BPM" in out
    assert "above" in out
    assert "bachata" in out


def test_distinct_features_block_highlights_tempo_below_range():
    rf = _mid_rf()
    out = _format_distinct_features_section(
        tempo=70.0, rhythm_features=rf, style_profile=KIZOMBA_PROFILE
    )
    assert "70 BPM" in out
    assert "below" in out
    assert "kizomba" in out


def test_distinct_features_block_empty_when_no_outliers():
    rf = _mid_rf()
    out = _format_distinct_features_section(
        tempo=128.0, rhythm_features=rf, style_profile=BACHATA_PROFILE
    )
    assert out == ""


def test_distinct_features_block_empty_without_style_profile():
    """Tempo bullet needs the style profile's bpm_range — skip it gracefully."""
    rf = _mid_rf()
    out = _format_distinct_features_section(
        tempo=128.0, rhythm_features=rf, style_profile=None
    )
    # Mid-range features + no style profile → no bullets
    assert out == ""


def test_distinct_features_block_capped_at_three_bullets():
    """A track hitting every outlier should still emit at most 3 bullets."""
    rf = _mid_rf(percussiveness=0.72, onsets_per_beat=3.4)
    out = _format_distinct_features_section(
        tempo=150.0, rhythm_features=rf, style_profile=BACHATA_PROFILE
    )
    # Three bullet lines starting with "- "
    bullet_lines = [line for line in out.splitlines() if line.startswith("- ")]
    assert len(bullet_lines) <= 3
    assert len(bullet_lines) >= 1


# ── QUESTION_SECTIONS rewrite ─────────────────────────────────────────────────


def test_question_sections_rewrite_present():
    """Phase 10 introduces a strict P#: <start>s-<end>s, <label> — line format."""
    assert "P#:" in QUESTION_SECTIONS
    # "specific number" is the numeric-anchoring keyword that must be enforced
    assert "specific number" in QUESTION_SECTIONS.lower()
    # Generic platitudes should be explicitly forbidden
    assert "must be deleted" in QUESTION_SECTIONS


def test_question_dancer_requires_numeric_anchoring():
    """QUESTION_DANCER must carry the numeric-anchoring rule."""
    assert "specific number" in QUESTION_DANCER.lower()
    assert "delete" in QUESTION_DANCER.lower()


def test_question_dancer_hides_raw_decimals_from_final_answer():
    """Phase 31 — the dancer answer must use BPM and timestamps but never
    narrate raw analysis decimals (beat strengths, accent arrays, onset
    density floats, percussiveness/tempo-stability/RMS ratios). This is
    the same surgery Phase 29 applied to QUESTION_KIZOMBA_TUTOR; without
    it the bachata demo output reads like a metrics report.
    """
    text = QUESTION_DANCER.lower()
    assert "do not quote raw decimals" in text
    assert "beat-strength" in text or "mean strength" in text
    assert "accent-pattern" in text or "accent pattern" in text
    assert "onset-density" in text or "onsets/beat" in text
    assert "percussiveness" in text
    assert "tempo-stability" in text or "tempo stability" in text
    assert "rms" in text
    assert "qualitative" in text
    # BPM and timestamps stay allowed
    assert "bpm and timestamps may be quoted directly" in text


def test_question_dancer_drill_uses_section_anchor():
    """Phase 31 — the drill must reference a real section/timestamp from
    the analysis, not just 'this tempo'. Keeps the drill grounded in
    the actual song structure.
    """
    text = QUESTION_DANCER.lower()
    assert "section label" in text or "section starting" in text
    assert "timestamp" in text


# ── kizomba_tutor (Phase 26) ──────────────────────────────────────────────────


def test_question_kizomba_tutor_registered_and_grounded():
    """The kizomba tutor question must:
    * be exposed via ALL_QUESTIONS,
    * use phase beat-feel labels for grounding,
    * forbid downbeat / "1" claims (kizomba downbeat is out of scope),
    * translate metrics into learner-facing movement coaching.
    """
    assert ALL_QUESTIONS.get("kizomba_tutor") is QUESTION_KIZOMBA_TUTOR
    text = QUESTION_KIZOMBA_TUTOR.lower()
    assert "beat-clarity" in text
    assert "subtle" in text and "clear" in text
    # Downbeat / "1" must be explicitly out of scope
    assert "downbeat" in text or "do not name" in text
    assert "movement strategy" in text
    assert "small weight shifts" in text
    assert "count 4 or 8 beats internally" in text


def test_question_kizomba_tutor_hides_raw_metrics_from_final_answer():
    """The tutor should use analysis internally without narrating decimals.

    Phase 35: metric-guard wording lifted into shared _METRIC_GUARD_RULE
    helper. Test now asserts the new canonical phrasing while keeping the
    kizomba-specific tempo-grounding addendum.
    """
    text = QUESTION_KIZOMBA_TUTOR.lower()
    assert "do not quote raw decimals" in text
    assert "beat-clarity decimals" in text
    assert "onsets/beat" in text
    assert "percussiveness" in text
    assert "rms" in text
    assert "required phase time span is enough numeric grounding" in text


def test_question_kizomba_tutor_label_slot_excludes_energy():
    """The label slot must be the section name (intro/main/peak/break/...),
    not the energy descriptor. Phase 29b nb07 trial caught Gemma putting
    'low energy' in the slot for Baila when both fields share a line in
    the phase summary.
    """
    text = QUESTION_KIZOMBA_TUTOR
    # Format string uses <section> not <label>
    assert "<section>" in text
    # Canonical section names enumerated
    for name in ("intro", "main", "break", "build", "peak", "outro"):
        assert name in text
    # Energy descriptor explicitly forbidden in the slot
    assert "low energy" in text or "high energy" in text
    assert "energy is context" in text or "not the label" in text.lower()


def test_question_kizomba_tutor_break_handling_uses_recovery_vocabulary():
    """Phase 29b — clear/moderate-beat breaks must steer away from
    'pause and hold' toward concrete recovery vocabulary discovered by
    the self-critique trial on Filomena.
    """
    text = QUESTION_KIZOMBA_TUTOR.lower()
    assert "pause and hold" in text  # explicitly named as the failure mode
    assert "reduce travel" in text
    assert "small pulse" in text
    assert "reconnect" in text


def test_question_kizomba_tutor_forbids_continues_filler():
    """Phase 34 — kill the `continues.` filler that shipped on songs with
    several adjacent `main` groups (Filomena re-run, Daniel Santacruz from
    the extended set). Every line must carry a real coaching note; the
    old "Use `continues` only when..." allowance is gone.
    """
    text = QUESTION_KIZOMBA_TUTOR.lower()
    # New rule wording is present
    assert "every line must carry a real coaching note" in text
    assert "do not use `continues` as a coaching note" in text
    assert "name what is physically different" in text
    # Old allowance wording is gone
    assert "use `continues`\n  only when" not in text
    assert "use `continues` only when" not in text


def test_question_kizomba_tutor_section_role_vocabulary():
    """Phase 34 — when there are multiple `main` groups, the prompt
    enumerates a small song-arc role vocabulary so each line gets
    substance even on long, similar-section tracks. The carve-out for
    single-`main` songs prevents over-application.
    """
    text = QUESTION_KIZOMBA_TUTOR.lower()
    # Vocabulary is enumerated
    assert "*establishing*" in text
    assert "*sustaining*" in text
    assert "*building*" in text
    assert "*returning*" in text
    assert "*closing*" in text
    # Role-position cues are present so the model can pick the right name
    assert "earliest `main` group" in text
    assert "before a `build` or `peak`" in text
    assert "after a `peak` or `break`" in text
    assert "before an `outro`" in text
    # Carve-out for songs with a single main group
    assert "songs with only one `main` group don't need a role" in text


# ── Phase 29b kizomba tutor polish (second-pass rewrite) ─────────────────────


def test_kizomba_tutor_polish_system_forbids_overreach():
    """The polish system prompt must guard against added musical facts,
    new instruments, or downbeat/'1' claims sneaking into the rewrite.
    """
    text = KIZOMBA_TUTOR_POLISH_SYSTEM.lower()
    assert "beginner" in text or "improver" in text
    assert "preserve" in text and "grounding" in text
    assert "do not add" in text
    assert "instrument" in text
    assert "downbeat" in text
    assert "'1'" in KIZOMBA_TUTOR_POLISH_SYSTEM


def test_kizomba_tutor_polish_prompt_includes_draft_and_track_name():
    """The builder must embed the supplied track name and pass the draft
    through verbatim so the rewrite has the actual content to revise.
    """
    draft = (
        "P1: 0s-13s, intro [beat: clear] — Feel the pulse together with "
        "minimal movement.\n"
        "P2: 13s-180s, main [beat: clear] — Walk the basic.\n"
    )
    out = build_kizomba_tutor_polish_prompt("Baila Kizomba Amor", draft)
    assert "Baila Kizomba Amor" in out
    # Draft body present (after .strip())
    assert "P1: 0s-13s, intro [beat: clear]" in out
    assert "P2: 13s-180s, main [beat: clear]" in out


def test_kizomba_tutor_polish_prompt_preserves_structure_rules():
    """Rubric must keep P# headers, time spans, beat tags untouched and
    forbid adding/removing sections during the rewrite.
    """
    out = build_kizomba_tutor_polish_prompt("track", "P1: 0s-1s, intro — x").lower()
    assert "p# lines" in out
    assert "time spans" in out
    assert "beat tags" in out
    assert "do not add sections" in out
    assert "do not remove sections" in out


def test_question_kizomba_drills_registered_and_grounded():
    """Phase 32 — drills prompt is registered, uses beat-clarity labels,
    and emits a P# format with a `Drill:` prefix.
    """
    assert ALL_QUESTIONS.get("kizomba_drills") is QUESTION_KIZOMBA_DRILLS
    text = QUESTION_KIZOMBA_DRILLS.lower()
    assert "subtle" in text and "moderate" in text and "clear" in text
    assert "drill:" in text
    # Phase 32b: format spec uses `P#[-#]:` to support both single and ranged groups
    assert "p#[-#]:" in text


def test_question_kizomba_drills_covers_whole_song():
    """Phase 32b — the practice plan must cover EVERY phase from the
    analysis. The first Phase 32 shape (3-5 drills) was confusing for
    a learner because gaps between drilled phases implied 'do nothing'
    during the unmentioned 90+ seconds. New rule: every phase maps to
    exactly one drill line.
    """
    text = QUESTION_KIZOMBA_DRILLS.lower()
    assert "cover the whole song" in text
    assert "every phase" in text and "exactly one drill line" in text


def test_question_kizomba_drills_groups_adjacent_same_label():
    """Phase 32b — adjacent same-label same-beat phases collapse into a
    single P#-range line (e.g. P2-P5 if four consecutive `main [beat:
    clear]` phases). A contrasting section (break/peak/build) ends the
    group so a recurring same-label sequence after the contrast becomes
    a NEW group. Different labels MUST stay in separate groups even when
    beat tag matches.

    The previous live run regressed twice: first by emitting `P7-P8: main`
    when P7 was `main` and P8 was `outro`; then again after the rule was
    added — likely because the prompt's literal counter-example string
    (`P7-P8: main`) anchored the model to re-emit those tokens. Phase 32b
    final iteration replaces the literal string with abstract `Pn-Pm`
    notation so the model can't pattern-match a forbidden literal.
    """
    text = QUESTION_KIZOMBA_DRILLS.lower()
    assert "p# range" in text or "p#[-#]" in QUESTION_KIZOMBA_DRILLS
    assert "p2-p5" in text  # the canonical positive example of a grouped range
    assert "contrasting section" in text or "contrast" in text
    assert "new group" in text
    # Different-label-different-group rule, abstractly framed (no
    # literal `P7-P8` string the model could re-emit)
    assert "different labels = different groups" in text
    assert "pn-pm" in text  # abstract range notation
    assert "same section label" in text
    # Self-check rule that asks the model to verify before emitting
    assert "self-check" in text
    # Concrete examples of label boundaries (without literal P# numbers
    # that could be re-emitted)
    assert "main` next to an `outro" in text or "main next to an outro" in text
    # Worked positive example to anchor the correct shape when a song
    # has a main group followed by an outro
    assert "worked positive example" in text
    assert "p_a: main" in text and "p_b: outro" in text
    # Canonical label set enumerated in the rule paragraph
    for name in ("intro", "main", "break", "short_break", "build", "peak", "outro"):
        assert name in text


def test_question_kizomba_drills_handles_recurring_groups():
    """Phase 32b — when the same section type recurs after a contrast
    (e.g. `main` before and after a `break`), the second occurrence
    should note a meaningful variation tied to the narrative shift.
    """
    text = QUESTION_KIZOMBA_DRILLS.lower()
    assert "variation" in text
    # Concrete examples that should appear in the rule wording
    assert "post-break" in text or "after a break" in text
    assert "subtle styling" in text or "add styling" in text


def test_question_kizomba_drills_time_span_rule():
    """Phase 32b live-run regression: model emitted `P2-P5: main
    (12s-121s, ...)` where 121s is the end of P4, not P5 (which ends at
    148s). The grouped time span must run from the start of the FIRST
    phase to the end of the LAST phase in the group, not the
    second-to-last.
    """
    text = QUESTION_KIZOMBA_DRILLS.lower()
    assert "time span rule" in text
    assert "start of the first phase" in text
    assert "end of the last phase" in text
    # Worked example: P2-P5 = 12s-148s, NOT 12s-121s
    assert "12s-148s" in text
    assert "12s-121s" in text  # the wrong-end counter-example
    assert "second-to-last" in text


def test_question_kizomba_drills_chronological_ordering():
    """Phase 32b — drill lines must be ordered chronologically so the
    learner can follow top-to-bottom against the song.
    """
    text = QUESTION_KIZOMBA_DRILLS.lower()
    assert "chronologic" in text  # 'chronologically' or 'chronological'
    assert "p1 first" in text or "top-to-bottom" in text


def test_question_kizomba_drills_section_slot_excludes_energy():
    """Phase 32 — same Phase-29b label-slot fix as kizomba_tutor: the
    section slot must enumerate canonical labels and explicitly forbid
    the energy descriptor.
    """
    text = QUESTION_KIZOMBA_DRILLS
    assert "<section>" in text
    for name in ("intro", "main", "break", "short_break", "build", "peak", "outro"):
        assert name in text
    assert "low energy" in text or "high energy" in text


def test_question_kizomba_drills_hides_raw_metrics():
    """Phase 32 — fourth application of the metric-guard pattern (after
    kizomba_tutor / dancer / song_arc). Drills must not narrate raw
    decimals at the learner.

    Phase 35: metric-guard wording lifted into shared _METRIC_GUARD_RULE
    helper. Test now asserts the new canonical phrasing.
    """
    text = QUESTION_KIZOMBA_DRILLS.lower()
    assert "do not quote raw decimals" in text
    assert "beat-clarity decimals" in text
    assert "onsets/beat" in text
    assert "percussiveness" in text
    assert "rms" in text
    assert "accent-pattern" in text or "accent pattern" in text


def test_question_kizomba_drills_break_handling_uses_recovery_vocabulary():
    """Phase 32 follow-up — same Phase 29b lesson as kizomba_tutor: explicitly
    name the failure phrases ('pause and hold', 'stop your steps', 'hold
    stillness') and require recovery vocabulary on `beat: clear` /
    `beat: moderate` breaks. Live run on Filomena's `break [beat: clear]`
    produced 'Stop your steps and hold stillness' — exactly the failure
    mode the soft rule didn't catch.
    """
    text = QUESTION_KIZOMBA_DRILLS.lower()
    # Failure phrases explicitly forbidden
    assert "pause and hold" in text
    assert "stop your steps" in text
    assert "hold stillness" in text
    # Recovery vocabulary required
    assert "reduce travel" in text
    assert "small pulse in the body" in text
    assert "reconnect on the next phase" in text


def test_question_kizomba_drills_forbids_downbeat_and_requires_duration():
    """Phase 32 — same downbeat guard as kizomba_tutor; drills must also
    state a concrete duration (not 'practise this section').

    Phase 35: downbeat guard lifted into shared _KIZOMBA_DOWNBEAT_GUARD_RULE
    helper with the Phase-33b positive-replacement wording. Test now asserts
    against the new shared form.
    """
    text = QUESTION_KIZOMBA_DRILLS.lower()
    assert "downbeat" in text
    assert "'the 1'" in QUESTION_KIZOMBA_DRILLS
    # Duration anchoring
    assert "always state a duration" in text
    assert "30s" in text


def test_verify_kizomba_drills_repairs_crossed_outro_range():
    """Phase 37c — live 00 rerun produced `P7-P8: main` plus `P8: outro`.

    Prompt prose already forbids that shape, so the learner-facing output now
    gets normalized against the actual phase labels after generation.
    """
    phases = [
        _phase("intro", 0.0, 12.0),
        _phase("main", 12.0, 59.0),
        _phase("main", 59.0, 80.0),
        _phase("main", 80.0, 121.0),
        _phase("main", 121.0, 148.0),
        _phase("break", 148.0, 159.0),
        _phase("main", 159.0, 195.0),
        _phase("outro", 195.0, 209.0),
    ]
    raw = "\n".join([
        "P1: intro (0s-12s, beat: clear) — Drill: feel the pulse together. 12s.",
        "P2-P5: main (12s-148s, beat: clear) — Drill: steady walk-step. 30s loop.",
        "P6: break (148s-159s, beat: clear) — Drill: reduce travel. 11s.",
        "P7-P8: main (159s-195s, beat: clear) — Drill: add subtle styling. 36s.",
        "P8: outro (195s-209s, beat: clear) — Drill: slow the pace. 14s.",
    ])

    verified = verify_kizomba_drills_output(raw, phases)

    assert "P7-P8: main" not in verified.cleaned
    assert "P7: main (159s-195s, beat: clear) — Drill: add subtle styling. 36s." in verified.cleaned
    assert "P8: outro (195s-209s, beat: clear) — Drill: slow the pace. 14s." in verified.cleaned
    assert verified.cleaned.count("P8:") == 1
    assert verified.stats["repaired_ranges"] == 1
    assert verified.stats["filled_missing"] == 0


def test_verify_kizomba_drills_preserves_valid_same_label_group():
    phases = [
        _phase("main", 12.0, 59.0),
        _phase("main", 59.0, 80.0),
        _phase("main", 80.0, 121.0),
    ]
    raw = (
        "P1-P3: main (12s-121s, beat: clear) — "
        "Drill: repeat the same walk-step. 30s loop."
    )

    verified = verify_kizomba_drills_output(raw, phases)

    assert verified.cleaned == raw
    assert verified.stats["repaired_ranges"] == 0
    assert verified.stats["filled_missing"] == 0


def test_verify_kizomba_drills_fills_missing_boundary_phase():
    phases = [
        _phase("main", 159.0, 195.0),
        _phase("outro", 195.0, 209.0),
    ]
    raw = (
        "P1-P2: main (159s-195s, beat: clear) — "
        "Drill: add subtle styling. 36s."
    )

    verified = verify_kizomba_drills_output(raw, phases)

    assert "P1: main (159s-195s, beat: clear) — Drill: add subtle styling. 36s." in verified.cleaned
    assert "P2: outro (195s-209s, beat: clear) — Drill: reduce travel" in verified.cleaned
    assert verified.stats["repaired_ranges"] == 1
    assert verified.stats["filled_missing"] == 1


def test_kizomba_tutor_polish_prompt_forbids_metrics_and_downbeat():
    """Rubric must mirror the one-pass guardrails: no raw metrics, no
    downbeat / '1' claim, and the same break-handling recovery vocabulary.
    """
    out = build_kizomba_tutor_polish_prompt("track", "draft").lower()
    assert "raw metrics" in out
    assert "beat-clarity" in out
    assert "downbeat" in out
    assert "'1'" in build_kizomba_tutor_polish_prompt("track", "draft")
    # break-handling recovery vocabulary mirrors the one-pass tweak
    assert "reduce travel" in out
    assert "small pulse" in out
    assert "reconnect" in out
    assert "pause-and-hold" in out


def test_question_song_arc_requires_distinctiveness():
    """QUESTION_SONG_ARC must require track-specific novelty anchoring."""
    text = QUESTION_SONG_ARC.lower()
    assert "distinguish" in text
    # Phase 31 rephrased "numeric anchor" but the anchoring rule survives
    # via timestamp/BPM/structural feature wording.
    assert "anchor it on a timestamp" in text
    assert "structural feature" in text


def test_question_song_arc_hides_raw_decimals_from_final_answer():
    """Phase 31 — the song-arc 'distinguishes this track' sentence used to
    invite raw decimal narration ('percussiveness of 0.22'). Same surgical
    move as Phase 29 (kizomba_tutor) and the dancer rewrite: forbid raw
    decimals, allow timestamps and BPM, require qualitative translation.
    """
    text = QUESTION_SONG_ARC.lower()
    assert "do not quote raw decimals" in text
    assert "percussiveness" in text
    assert "rms" in text
    assert "onset-density" in text or "onset density" in text
    assert "beat-clarity" in text
    assert "tempo-stability" in text or "tempo stability" in text
    assert "qualitative" in text
    # BPM and timestamps stay allowed
    assert "bpm and timestamps may be quoted directly" in text


# ── rhythm_anatomy (Phase 36) ────────────────────────────────────────────────


def test_question_rhythm_anatomy_registered_and_grounded():
    """Phase 36 — genre-level rhythmic anatomy intro. Phase 37a expanded
    this from a single paragraph to two paragraphs (anatomy + sub-style
    hints). Must be registered, use the {style} placeholder, and
    reference the canonical structural-arc vocabulary
    (intro/main/break/build/peak/outro) so the genre intro frames the
    same vocabulary the per-track listening_guide and tutor will use.
    """
    assert ALL_QUESTIONS.get("rhythm_anatomy") is QUESTION_RHYTHM_ANATOMY
    text = QUESTION_RHYTHM_ANATOMY.lower()
    # Style-templated (parallel to listening_guide / song_arc / dancer)
    assert "{style}" in QUESTION_RHYTHM_ANATOMY
    # Two-paragraph prose format (Phase 37a)
    assert "two-paragraph genre intro" in text
    assert "two prose paragraphs" in text
    # Anatomy framing: tempo / time signature / pulse-carrier / structural arc
    assert "tempo range" in text
    assert "time signature" in text
    assert "structural arc" in text
    # Canonical phase labels — same vocabulary as the per-track prompts
    for name in ("intro", "main", "break", "build", "peak", "outro"):
        assert name in text


def test_question_rhythm_anatomy_forbids_movement_coaching():
    """Same differentiator as listening_guide (Phase 33): rhythm anatomy
    is genre explanation, not movement coaching. The forbidden-token
    list is identical so coaching language doesn't drift in from the
    tutor / drills prompts.
    """
    text = QUESTION_RHYTHM_ANATOMY.lower()
    assert "genre explanation, not movement coaching" in text
    assert "walk-step" in text
    assert "weight transfer" in text
    assert "travel" in text
    assert "styling" in text
    assert "save those for the tutor" in text


def test_question_rhythm_anatomy_is_genre_not_track():
    """rhythm_anatomy must speak about the genre in general, NOT about
    a specific track. The prompt forbids inventing a hypothetical
    track or quoting timestamps — the per-track listening_guide owns
    that role.
    """
    text = QUESTION_RHYTHM_ANATOMY.lower()
    assert "not track-specific" in text
    assert "do not invent a hypothetical track" in text
    assert "do not quote specific timestamps" in text or "do not refer to 'this track'" in text
    # Speak about the genre, not the song
    assert "as a genre" in text or "about {style}".lower() in text


def test_question_rhythm_anatomy_uses_shared_helpers():
    """Phase 36 inherits the Phase 35 metric-guard and kizomba-downbeat-
    guard helpers from day one — so rhythm_anatomy can describe Zouk-
    inherited syncopation without naming the kizomba '1', and reference
    percussion qualitatively without quoting decimals. Verifies the
    f-string interpolation actually landed.
    """
    assert _METRIC_GUARD_RULE in QUESTION_RHYTHM_ANATOMY
    assert _KIZOMBA_DOWNBEAT_GUARD_RULE in QUESTION_RHYTHM_ANATOMY


def test_question_rhythm_anatomy_includes_substyle_hints():
    """Phase 37a — second paragraph of the genre intro names 2-4 major
    sub-styles per genre with rhythmic distinguishers. The user picks
    hints themselves from the intro to place a track they'll hear; the
    system never claims to identify a song's sub-style from the
    `RhythmAnalysis` alone (that would be hallucination from partial
    information).

    Sub-style examples for both genres are listed in the prompt so the
    model has a stable reference set; the sub-style identification
    no-claim rule is the architectural honesty bit.
    """
    text = QUESTION_RHYTHM_ANATOMY.lower()
    # New paragraph-2 framing
    assert "sub-style" in text
    assert "2 to 4 major sub-styles" in text
    # Major kizomba sub-styles enumerated in the prompt as a stable
    # reference set (model uses the relevant list per {style})
    for substyle in ("angolan kizomba", "urbankiz", "tarraxinha"):
        assert substyle in text
    # Major bachata sub-styles enumerated similarly
    for substyle in ("dominican", "sensual", "bachatango"):
        assert substyle in text
    # Architectural honesty: do not claim to identify the sub-style of
    # any specific track. Sub-style identification from a RhythmAnalysis
    # alone is unreliable — this is the project's honest-uncertainty
    # discipline applied to a new dimension.
    assert "do not claim that any specific track belongs to a specific" in text
    assert "sub-style identification" in text and "unreliable" in text


# ── listening_guide (Phase 33) ───────────────────────────────────────────────


def test_question_listening_guide_registered_and_grounded():
    """Phase 33 — pre-listening orientation prompt. Must be registered in
    ALL_QUESTIONS, named two-paragraph prose (not P# format), and ground the
    difficulty map on per-phase beat-clarity labels.
    """
    assert ALL_QUESTIONS.get("listening_guide") is QUESTION_LISTENING_GUIDE
    text = QUESTION_LISTENING_GUIDE.lower()
    # Style-templated like dancer / song_arc
    assert "{style}" in QUESTION_LISTENING_GUIDE
    # Two-paragraph structure
    assert "two short paragraphs" in text
    assert "orientation" in text
    assert "difficulty map" in text
    # Beat-clarity labels are the grounding signal
    assert "beat-clarity" in text
    assert "subtle" in text and "moderate" in text and "clear" in text
    # Section labels available to ground the arc paragraph
    for name in ("intro", "main", "break", "build", "peak", "outro"):
        assert name in text


def test_question_listening_guide_forbids_movement_coaching():
    """The whole point of the listening guide is to be NOT-coaching: no
    walk-step instructions, weight transfers, travel directives, or styling
    cues. Those belong to the tutor and drills prompts.
    """
    text = QUESTION_LISTENING_GUIDE.lower()
    assert "listening preparation, not movement coaching" in text
    assert "walk-step" in text
    assert "weight transfer" in text
    assert "travel" in text
    assert "styling" in text
    assert "save those for the tutor" in text


def test_question_listening_guide_forbids_pn_format():
    """Output is prose paragraphs, not the P# phase format used by
    sections / kizomba_tutor / kizomba_drills. The tutor already produces
    per-phase lines; this prompt's job is the prose orientation that
    frames them.
    """
    text = QUESTION_LISTENING_GUIDE.lower()
    assert "do not use the p# format" in text
    assert "prose paragraph" in text


def test_question_listening_guide_hides_raw_metrics():
    """Same metric guard pattern as song_arc, kizomba_tutor, dancer,
    kizomba_drills (now sixth application — the shared-helper-string
    refactor is overdue). Forbid raw decimals, allow timestamps and BPM.
    """
    text = QUESTION_LISTENING_GUIDE.lower()
    assert "do not quote raw decimals" in text
    assert "beat-clarity decimals" in text
    assert "percussiveness" in text
    assert "rms" in text
    assert "onset-density" in text or "onset density" in text
    assert "accent-pattern arrays" in text
    assert "qualitative" in text
    assert "bpm and timestamps may be quoted directly" in text


def test_question_listening_guide_kizomba_downbeat_guard():
    """Same downbeat guard as kizomba_tutor / kizomba_drills, but
    conditional on style — a bachata listening guide is allowed (and
    expected) to reference the clear acoustic '1', while kizomba must
    not name a downbeat.

    Phase 33 live-run iteration: the 26B model leaked 'the 1 is likely
    around various points' on Filomena despite the original guard. The
    Phase 32 lesson (positive replacement beats negative-only) applied:
    the prompt now ALSO tells the model what to say instead of '1' /
    'downbeat' — frame it as 'the pulse is felt rather than heard' or
    'the bass carries the pulse'.
    """
    text = QUESTION_LISTENING_GUIDE.lower()
    assert "for kizomba specifically" in text
    assert "downbeat" in text
    assert "'the 1'" in QUESTION_LISTENING_GUIDE
    assert "syncopation" in text or "off-beat" in text
    # Positive replacement wording — the part that survived 32b:
    assert "the pulse is felt rather than heard" in text
    assert "the bass carries the pulse" in text
    # Phase 37a-bis: live Filomena listening_guide echoed the analysis
    # phrase "downbeat position is ambiguous". The prompt now gives the
    # model a replacement for uncertain beat-position anchoring, without
    # naming the forbidden field in learner-facing prose.
    assert "uncertain beat-position anchoring" in text
    assert "trust the bass line" in text
    assert "avoid relying on a specific count" in text


# ── Phase 35 — shared metric-guard / downbeat-guard helpers ──────────────────


def test_metric_guard_rule_canonical_wording():
    """Phase 35c — _METRIC_GUARD_RULE rewritten after the Phase 35 live run
    showed the bachata song_arc leaked 'percussiveness of 0.16'. Diagnosis:
    the helper's example list ('percussiveness of 0.22', '0.16
    percussiveness', etc.) was being lifted as values to quote — same
    failure mode as Phase 35b's 'downbeat' echo, but with specific decimal
    examples instead of forbidden words. Phase 35c removes all specific
    decimal examples from the helper, uses '<number>' as a generic
    placeholder, and adds a 'not in narration, not as a distinguishing
    feature' meta-instruction parallel to 35b's downbeat-guard fix.
    """
    text = _METRIC_GUARD_RULE.lower()
    # Forbidden vocabulary across the analysis metrics
    assert "do not quote raw decimals" in text
    assert "beat-clarity decimals" in text
    assert "percussiveness ratios" in text
    assert "rms ratios" in text
    assert "onset-density floats" in text
    assert "onsets/beat" in text
    assert "accent-pattern arrays" in text
    assert "tempo-stability decimals" in text
    assert "beat-strength values" in text
    # Phase 35c meta-instruction: forbid specific decimals in any form,
    # parallel to 35b's downbeat-guard "not in narration, not in negation"
    assert "do not use any specific decimal number" in text
    assert "not in narration" in text
    assert "not as a distinguishing feature" in text
    assert "<number>" in text  # generic placeholder, not a real value
    # Positive replacement (Phase 34 carried forward)
    assert "drum-light feel" in text
    assert "qualitative" in text
    # Explicit allowance
    assert "bpm and timestamps may be quoted directly" in text
    # Phase 35c regression check: the helper must NOT contain specific
    # decimal examples that the model could lift as values to quote.
    # The bachata song_arc `percussiveness of 0.16` leak motivated this.
    assert "0.22" not in _METRIC_GUARD_RULE
    assert "0.34" not in _METRIC_GUARD_RULE
    assert "0.16" not in _METRIC_GUARD_RULE


def test_kizomba_downbeat_guard_rule_canonical_wording():
    """Phase 35b — _KIZOMBA_DOWNBEAT_GUARD_RULE rewritten after the Phase 35
    live run showed 3-of-7 listening_guide outputs still leaked the word
    'downbeat'. Diagnosis: the helper's own rationale text used 'downbeat'
    three times and the model echoed it. Phase 35b removes 'downbeat' from
    the rationale (keeps it only in the forbidden-token list) and adds an
    explicit 'not in narration, not in negation' meta-instruction.
    """
    text = _KIZOMBA_DOWNBEAT_GUARD_RULE.lower()
    # Hard forbidden tokens — direct prohibition replaces the Phase 35
    # "Do NOT name a downbeat" wording with the more emphatic
    # "Do NOT use the word 'downbeat'" so the rule fires on echoed
    # narration, not just on declarative claims.
    assert "do not use the word 'downbeat'" in text
    assert "'the 1'" in _KIZOMBA_DOWNBEAT_GUARD_RULE
    # Phase 35b meta-instruction: the model was leaking "downbeat" in
    # negation ("the downbeat is not clearly defined"). The new wording
    # forbids that explicitly.
    assert "not in narration" in text
    assert "not in negation" in text
    # Phase 34 specific-position examples (motivated the original helper)
    assert "step on 1 and 3" in text  # Isabelle leak phrasing
    assert "land on count 4" in text
    # Positive replacement (Phase 33b carried forward)
    assert "the pulse is felt rather than heard" in text
    assert "the bass carries the pulse" in text
    # Phase 37a-bis replacement for low-confidence beat-position leaks.
    assert "uncertain beat-position anchoring" in text
    assert "do not name that field" in text
    assert "trust the bass line" in text
    assert "avoid relying on a specific count" in text
    # Frame-it / Talk-instead pivot language
    assert "syncopation" in text or "off-beat" in text
    # Phase 35b regression check: the helper's rationale must NOT
    # contain "downbeat" outside the forbidden-token enumeration. The
    # word can appear in 'do not use the word ' but not in declarative
    # statements like 'Kizomba's downbeat is acoustically subtle'.
    assert "downbeat is acoustically" not in text
    assert "downbeat is subtle" not in text
    assert "lack of a clear downbeat" not in text
    assert text.count("downbeat") == 1


def test_shared_guards_used_in_consuming_prompts():
    """Phase 35 — assert each consuming prompt actually contains the shared
    helper text. If a future refactor accidentally drops the helper from a
    prompt this test fires before live runs do.
    """
    for q, name in (
        (QUESTION_LISTENING_GUIDE, "listening_guide"),
        (QUESTION_KIZOMBA_TUTOR, "kizomba_tutor"),
        (QUESTION_KIZOMBA_DRILLS, "kizomba_drills"),
        (QUESTION_SONG_ARC, "song_arc"),
        (QUESTION_DANCER, "dancer"),
    ):
        assert _METRIC_GUARD_RULE in q, (
            f"{name} prompt is missing the shared _METRIC_GUARD_RULE text"
        )
    # Kizomba downbeat guard only applies to the three kizomba-aware prompts
    for q, name in (
        (QUESTION_LISTENING_GUIDE, "listening_guide"),
        (QUESTION_KIZOMBA_TUTOR, "kizomba_tutor"),
        (QUESTION_KIZOMBA_DRILLS, "kizomba_drills"),
    ):
        assert _KIZOMBA_DOWNBEAT_GUARD_RULE in q, (
            f"{name} prompt is missing the shared "
            "_KIZOMBA_DOWNBEAT_GUARD_RULE text"
        )


# ── Phase 11d: regex grounding verifier ──────────────────────────────────────


def test_has_numeric_anchor_accepts_bpm_timestamp_bars():
    """Recognise BPM, timestamp seconds, bar/phrase counts, M#/P#, percentages."""
    assert _has_numeric_anchor("steady at 128 BPM throughout")
    assert _has_numeric_anchor("the drop at 45s lifts the energy")
    assert _has_numeric_anchor("4 bars of build before the chorus")
    assert _has_numeric_anchor("expect a fill at M84")
    assert _has_numeric_anchor("hits at 02:50 again")
    assert _has_numeric_anchor("perc ratio 0.65 ratio is unusually high")
    assert _has_numeric_anchor("accent pattern [1.00, 0.98, 0.97, 0.79]")


def test_has_numeric_anchor_rejects_platitude():
    """Generic style-level claims have no anchor and must fail."""
    assert not _has_numeric_anchor("feel the bachata basic")
    assert not _has_numeric_anchor("maintain your 4/4 counting")  # "4/4" is not anchored
    assert not _has_numeric_anchor("keep your weight grounded")
    assert not _has_numeric_anchor("the music feels warm and energetic")


def test_verify_sections_replaces_failing_lines():
    """Lines without a numeric anchor get the Phase-10c fallback."""
    sections = [
        SongSection(start_s=0.0, end_s=10.0, label="intro", energy_level="low"),
        SongSection(start_s=10.0, end_s=60.0, label="main", energy_level="medium"),
        SongSection(start_s=60.0, end_s=80.0, label="outro", energy_level="low"),
    ]
    raw = (
        "P1: 0s-10s, intro — feel the bachata\n"
        "P2: 10s-60s, main — bongo drives the 129 BPM pulse, layer hip styling\n"
        "P3: 60s-80s, outro — wind down softly\n"
    )
    out = verify_sections_output(raw, sections)
    lines = out.cleaned.splitlines()
    assert lines[0] == "P1: 0s-10s, intro — continues the previous feel"
    assert lines[1] == (
        "P2: 10s-60s, main — bongo drives the 129 BPM pulse, layer hip styling"
    )
    assert lines[2] == "P3: 60s-80s, outro — continues the main feel"
    assert out.stats["total"] == 3
    assert out.stats["passed"] == 1
    assert out.stats["failed"] == 2


def test_verify_sections_preserves_passing_lines():
    """Every line has an anchor → cleaned output equals the parsed lines."""
    raw = (
        "P1: 0s-16s, intro — relaxed basic, settle into 129 BPM\n"
        "P2-3: 16s-89s, main — bongo at 1.9 ratio drives 4 bars per phrase\n"
    )
    out = verify_sections_output(raw, sections=None)
    assert out.stats["passed"] == 2
    assert out.stats["failed"] == 0
    assert out.cleaned == raw.strip()


def test_verify_sections_drops_non_p_lines():
    """Forbidden intro/outro sentences disappear from the cleaned output."""
    raw = (
        "Here is the breakdown for the dancer:\n"
        "P1: 0s-16s, intro — relaxed at 129 BPM\n"
        "Hope this helps!\n"
    )
    out = verify_sections_output(raw, sections=None)
    assert out.cleaned == "P1: 0s-16s, intro — relaxed at 129 BPM"
    assert out.stats["total"] == 1


def test_verify_sections_handles_empty_input():
    out = verify_sections_output("", sections=None)
    assert out.cleaned == ""
    assert out.stats["total"] == 0
    assert out.stats["pass_rate"] == 0.0


# ── beat clarity in prompts ───────────────────────────────────────────────────


def test_rhythm_features_section_includes_beat_clarity():
    rf = _mid_rf(beat_clarity=0.42)
    out = _format_rhythm_features_section(rf)
    assert "Beat clarity: 0.42" in out
    assert "clear" in out


def test_rhythm_features_section_labels_subtle_beat():
    rf = _mid_rf(beat_clarity=0.12)
    out = _format_rhythm_features_section(rf)
    assert "very subtle" in out


def test_rhythm_features_section_labels_moderate_beat():
    rf = _mid_rf(beat_clarity=0.28)
    out = _format_rhythm_features_section(rf)
    assert "moderate" in out


def test_phase_summary_includes_beat_clarity_label():
    rf = _mid_rf(beat_clarity=0.40)
    sec = SongSection(
        start_s=0.0, end_s=30.0, label="main", energy_level="medium",
        rhythm_features=rf,
    )
    phase = SongPhase(
        label="main", start_s=0.0, end_s=30.0, section_count=1,
        energy_levels=["medium"], avg_rhythm_features=rf,
    )
    out = _format_sections_block([sec], phases=[phase])
    assert "beat: clear" in out


def test_phase_summary_shows_subtle_for_low_bc():
    rf = _mid_rf(beat_clarity=0.15)
    sec = SongSection(
        start_s=0.0, end_s=30.0, label="main", energy_level="low",
        rhythm_features=rf,
    )
    phase = SongPhase(
        label="main", start_s=0.0, end_s=30.0, section_count=1,
        energy_levels=["low"], avg_rhythm_features=rf,
    )
    out = _format_sections_block([sec], phases=[phase])
    assert "beat: subtle" in out


# ── Phase 41-lite — per-phase texture/density tags (opt-in) ──────────────────


def test_phase_features_off_by_default_omits_tags():
    """Without the include_phase_features flag, the phase summary is byte-
    identical to before — no 'texture:' or 'onsets:' in the line."""
    rf = _mid_rf(onsets_per_beat=1.4, beat_clarity=0.45)
    sec = SongSection(
        start_s=0.0, end_s=30.0, label="main", energy_level="medium",
        rhythm_features=rf, harm_ratio=1.4, perc_ratio=0.6,
    )
    phase = SongPhase(
        label="main", start_s=0.0, end_s=30.0, section_count=1,
        energy_levels=["medium"], avg_rhythm_features=rf,
    )
    out = _format_sections_block([sec], phases=[phase])
    assert "texture:" not in out
    assert "onsets:" not in out


def test_phase_features_flag_adds_bass_driven_and_steady_tags():
    """Phase 41-lite — H× >> P× yields 'bass-driven'; opb in [1.0, 1.8) yields
    'steady'. Both surface as qualitative tags on the phase summary line."""
    rf = _mid_rf(onsets_per_beat=1.4, beat_clarity=0.45)
    sec = SongSection(
        start_s=0.0, end_s=30.0, label="main", energy_level="medium",
        rhythm_features=rf, harm_ratio=1.5, perc_ratio=0.5,
    )
    phase = SongPhase(
        label="main", start_s=0.0, end_s=30.0, section_count=1,
        energy_levels=["medium"], avg_rhythm_features=rf,
    )
    out = _format_sections_block(
        [sec], phases=[phase], include_phase_features=True,
    )
    # Both tags appear on the same Phase 1 line.
    phase_line = next(line for line in out.splitlines() if "Phase 1" in line)
    assert "texture: bass-driven" in phase_line
    assert "onsets: steady" in phase_line


def test_phase_features_percussive_and_busy_tags():
    """P× >> H× yields 'percussive'; opb >= 1.8 yields 'busy'."""
    rf = _mid_rf(onsets_per_beat=2.4, beat_clarity=0.45)
    sec = SongSection(
        start_s=0.0, end_s=30.0, label="peak", energy_level="high",
        rhythm_features=rf, harm_ratio=0.5, perc_ratio=1.6,
    )
    phase = SongPhase(
        label="peak", start_s=0.0, end_s=30.0, section_count=1,
        energy_levels=["high"], avg_rhythm_features=rf,
    )
    out = _format_sections_block(
        [sec], phases=[phase], include_phase_features=True,
    )
    phase_line = next(line for line in out.splitlines() if "Phase 1" in line)
    assert "texture: percussive" in phase_line
    assert "onsets: busy" in phase_line


def test_phase_features_balanced_and_sparse_tags():
    """Near-equal H×/P× yields 'balanced'; opb < 1.0 yields 'sparse'."""
    rf = _mid_rf(onsets_per_beat=0.6, beat_clarity=0.30)
    sec = SongSection(
        start_s=0.0, end_s=30.0, label="break", energy_level="low",
        rhythm_features=rf, harm_ratio=1.0, perc_ratio=1.0,
    )
    phase = SongPhase(
        label="break", start_s=0.0, end_s=30.0, section_count=1,
        energy_levels=["low"], avg_rhythm_features=rf,
    )
    out = _format_sections_block(
        [sec], phases=[phase], include_phase_features=True,
    )
    phase_line = next(line for line in out.splitlines() if "Phase 1" in line)
    assert "texture: balanced" in phase_line
    assert "onsets: sparse" in phase_line


def test_phase_features_skips_texture_when_hpss_unset():
    """When constituent sections lack harm_ratio/perc_ratio, the texture tag
    is omitted entirely (no fabricated value). Density still appears if
    avg_rhythm_features is present."""
    rf = _mid_rf(onsets_per_beat=1.4, beat_clarity=0.45)
    sec = SongSection(
        start_s=0.0, end_s=30.0, label="main", energy_level="medium",
        rhythm_features=rf,  # harm_ratio / perc_ratio left None
    )
    phase = SongPhase(
        label="main", start_s=0.0, end_s=30.0, section_count=1,
        energy_levels=["medium"], avg_rhythm_features=rf,
    )
    out = _format_sections_block(
        [sec], phases=[phase], include_phase_features=True,
    )
    phase_line = next(line for line in out.splitlines() if "Phase 1" in line)
    assert "texture:" not in phase_line
    assert "onsets: steady" in phase_line


# ── Phase 41-D — per-phase vocal-presence tag (opt-in) ───────────────────────


def test_phase_vocal_off_by_default_omits_tag():
    """Without include_phase_vocal, the phase summary stays free of vocal
    tags even when sections have populated vocal_ratio."""
    rf = _mid_rf(beat_clarity=0.45)
    sec = SongSection(
        start_s=0.0, end_s=30.0, label="main", energy_level="medium",
        rhythm_features=rf, vocal_ratio=0.8,
    )
    phase = SongPhase(
        label="main", start_s=0.0, end_s=30.0, section_count=1,
        energy_levels=["medium"], avg_rhythm_features=rf,
    )
    out = _format_sections_block([sec], phases=[phase])
    assert "vocal:" not in out


def test_phase_vocal_present_above_high_threshold():
    """vocal_ratio >= 0.55 → 'vocal: present'."""
    rf = _mid_rf(beat_clarity=0.45)
    sec = SongSection(
        start_s=0.0, end_s=30.0, label="main", energy_level="medium",
        rhythm_features=rf, vocal_ratio=0.85,
    )
    phase = SongPhase(
        label="main", start_s=0.0, end_s=30.0, section_count=1,
        energy_levels=["medium"], avg_rhythm_features=rf,
    )
    out = _format_sections_block(
        [sec], phases=[phase], include_phase_vocal=True,
    )
    phase_line = next(line for line in out.splitlines() if "Phase 1" in line)
    assert "vocal: present" in phase_line


def test_phase_vocal_sparse_in_middle_band():
    """0.20 <= vocal_ratio < 0.55 → 'vocal: sparse'."""
    rf = _mid_rf(beat_clarity=0.45)
    sec = SongSection(
        start_s=0.0, end_s=30.0, label="break", energy_level="low",
        rhythm_features=rf, vocal_ratio=0.30,
    )
    phase = SongPhase(
        label="break", start_s=0.0, end_s=30.0, section_count=1,
        energy_levels=["low"], avg_rhythm_features=rf,
    )
    out = _format_sections_block(
        [sec], phases=[phase], include_phase_vocal=True,
    )
    phase_line = next(line for line in out.splitlines() if "Phase 1" in line)
    assert "vocal: sparse" in phase_line


def test_phase_vocal_quiet_below_low_threshold():
    """vocal_ratio < 0.20 → 'vocal: quiet'."""
    rf = _mid_rf(beat_clarity=0.45)
    sec = SongSection(
        start_s=0.0, end_s=30.0, label="intro", energy_level="low",
        rhythm_features=rf, vocal_ratio=0.05,
    )
    phase = SongPhase(
        label="intro", start_s=0.0, end_s=30.0, section_count=1,
        energy_levels=["low"], avg_rhythm_features=rf,
    )
    out = _format_sections_block(
        [sec], phases=[phase], include_phase_vocal=True,
    )
    phase_line = next(line for line in out.splitlines() if "Phase 1" in line)
    assert "vocal: quiet" in phase_line


def test_phase_vocal_skipped_when_data_unset():
    """No section has vocal_ratio set (analyze ran without vocal_env) → tag
    omitted entirely even when the flag is on."""
    rf = _mid_rf(beat_clarity=0.45)
    sec = SongSection(
        start_s=0.0, end_s=30.0, label="main", energy_level="medium",
        rhythm_features=rf,  # vocal_ratio left None
    )
    phase = SongPhase(
        label="main", start_s=0.0, end_s=30.0, section_count=1,
        energy_levels=["medium"], avg_rhythm_features=rf,
    )
    out = _format_sections_block(
        [sec], phases=[phase], include_phase_vocal=True,
    )
    assert "vocal:" not in out


def test_phase_vocal_averages_across_member_sections():
    """Multi-section phase: tag is computed from the average of constituent
    sections' vocal_ratio, not the first one."""
    rf = _mid_rf(beat_clarity=0.45)
    # Two sections in the phase: one quiet, one present. Avg = 0.45 → sparse.
    s1 = SongSection(
        start_s=0.0, end_s=15.0, label="main", energy_level="medium",
        rhythm_features=rf, vocal_ratio=0.10,
    )
    s2 = SongSection(
        start_s=15.0, end_s=30.0, label="main", energy_level="medium",
        rhythm_features=rf, vocal_ratio=0.80,
    )
    phase = SongPhase(
        label="main", start_s=0.0, end_s=30.0, section_count=2,
        energy_levels=["medium"], avg_rhythm_features=rf,
    )
    out = _format_sections_block(
        [s1, s2], phases=[phase], include_phase_vocal=True,
    )
    phase_line = next(line for line in out.splitlines() if "Phase 1" in line)
    assert "vocal: sparse" in phase_line


# ---------------------------------------------------------------------------
# Bachata coaching surface (Phase 39) — tutor + drills + verifier reuse
# ---------------------------------------------------------------------------


def test_question_bachata_tutor_registered_and_grounded():
    """Phase 39 — bachata tutor is registered and grounded in beat tags."""
    assert ALL_QUESTIONS.get("bachata_tutor") is QUESTION_BACHATA_TUTOR
    text = QUESTION_BACHATA_TUTOR.lower()
    # references the per-phase beat-clarity tag set
    assert "beat: subtle/moderate/clear" in text or "subtle/moderate/clear" in text
    # honest-about-the-1 framing tied to downbeat confidence labels
    assert "downbeat confidence" in text
    assert "high confidence" in text
    assert "plausible guess" in text
    assert "ambiguous" in text
    # P# format
    assert "p#:" in text


def test_question_bachata_tutor_does_not_inherit_kizomba_downbeat_guard():
    """Phase 39 — bachata is the genre where naming the 1 is honest.

    The kizomba downbeat guard explicitly forbids naming the 1; we must NOT
    drop that guard verbatim into the bachata tutor or the model would refuse
    to anchor the learner on the count, which is the whole point.
    """
    assert _KIZOMBA_DOWNBEAT_GUARD_RULE not in QUESTION_BACHATA_TUTOR
    text = QUESTION_BACHATA_TUTOR.lower()
    # bachata vocabulary the user actually needs
    assert "8-count" in text
    # basic-step counts on 1-2-3 (tap 4) / 5-6-7 (tap 8)
    assert "1-2-3" in text
    assert "5-6-7" in text


def test_question_bachata_tutor_break_handling_uses_recovery_vocabulary():
    """Mirrors the kizomba tutor recovery rule: don't default to pause-and-hold."""
    text = QUESTION_BACHATA_TUTOR.lower()
    assert "pause and hold" in text
    assert "shrink the basic" in text or "shrink" in text
    assert "8-count alive" in text or "count internally" in text


def test_question_bachata_drills_registered_and_groupable():
    """Phase 39 — bachata drills are registered, share the verifier-ready format."""
    assert ALL_QUESTIONS.get("bachata_drills") is QUESTION_BACHATA_DRILLS
    text = QUESTION_BACHATA_DRILLS.lower()
    # same drill line shape the verifier parses
    assert "p#[-#]:" in text
    assert "drill:" in text
    # bachata-specific anchoring vocabulary
    assert "1-2-3" in text
    assert "5-6-7" in text
    # explicit honesty rule on duration anchoring
    assert "always state a duration" in text
    # do not inherit the kizomba downbeat guard
    assert _KIZOMBA_DOWNBEAT_GUARD_RULE not in QUESTION_BACHATA_DRILLS


def test_verify_kizomba_drills_reuses_for_bachata_shaped_input():
    """Phase 39 — the structural verifier is style-agnostic.

    A bachata-shaped raw draft that crosses a `main`/`outro` boundary should
    be repaired the same way as the kizomba case. This proves we can reuse
    `verify_kizomba_drills_output` for bachata without writing a parallel
    verifier.
    """
    phases = [
        _phase("main", 12.0, 80.0),
        _phase("main", 80.0, 148.0),
        _phase("outro", 148.0, 165.0),
    ]
    raw = "\n".join([
        "P1-P3: main (12s-148s, beat: clear) — "
        "Drill: loop the 1-2-3-tap, 5-6-7-tap basic on the steady pulse. 30s loop.",
        "P3: outro (148s-165s, beat: clear) — "
        "Drill: slow the basic, finish on a clean 8. 17s.",
    ])

    verified = verify_kizomba_drills_output(raw, phases)

    # The crossed `P1-P3: main` range should be shrunk to `P1-P2`
    assert "P1-P3: main" not in verified.cleaned
    assert "P1-P2: main (12s-148s, beat: clear)" in verified.cleaned
    # The outro line is preserved and renumbered to P3
    assert "P3: outro (148s-165s, beat: clear)" in verified.cleaned
    # No phase appears twice
    assert verified.cleaned.count("P3:") == 1
    assert verified.stats["repaired_ranges"] == 1
    assert verified.stats["filled_missing"] == 0


# ── Phase 40: kizomba transitions ───────────────────────────────────────────

def test_format_transitions_block_lists_label_boundaries():
    """Phase 40 — _format_transitions_block emits one T# line per label change."""
    phases = [
        _phase("intro", 0.0, 12.0),
        _phase("main", 12.0, 148.0),
        _phase("break", 148.0, 159.0),
        _phase("main", 159.0, 195.0),
        _phase("outro", 195.0, 209.0),
    ]
    block = _format_transitions_block(phases)
    assert "Transitions (4 label boundaries)" in block
    # T# numbering and boundary times
    assert "T1: 12s, intro → main" in block
    assert "T2: 148s, main → break" in block
    assert "T3: 159s, break → main" in block
    assert "T4: 195s, main → outro" in block
    # beat clarity tags appear in the (beat: from → to) suffix
    assert "(beat:" in block


def test_format_transitions_block_skips_same_label_runs():
    """Adjacent same-label phases (energy-only changes) emit no T# lines."""
    phases = [
        _phase("main", 0.0, 30.0),
        _phase("main", 30.0, 60.0),  # same label — skipped
        _phase("break", 60.0, 70.0),  # label change → T1
    ]
    block = _format_transitions_block(phases)
    assert "Transitions (1 label boundaries)" in block
    assert "T1: 60s, main → break" in block
    # No T2 — same-label boundary at 30s isn't a transition
    assert "T2:" not in block


def test_format_transitions_block_empty_for_single_label_song():
    """A single-label phase list returns empty (block is harmless to other prompts)."""
    assert _format_transitions_block([_phase("main", 0.0, 200.0)]) == ""
    assert _format_transitions_block([]) == ""
    assert _format_transitions_block(None) == ""


def test_format_transitions_block_includes_energy():
    """Phase 40d — energy fields appear in the per-transition lines so the
    model can reason about same-label energy shifts (main → main with
    energy: medium → high).
    """
    # _phase defaults to energy="medium"; build different-label phases
    # so the block is not empty regardless of include_same_label flag.
    phases = [
        _phase("intro", 0.0, 12.0),
        _phase("main", 12.0, 60.0),
    ]
    block = _format_transitions_block(phases)
    # energy field appears in the (beat: ..., energy: from → to) suffix
    assert "energy:" in block
    assert "medium" in block  # _phase default energy


def test_question_kizomba_transitions_registered_and_grounded():
    """Phase 40 — kizomba_transitions registered, T# format defined, references the analysis."""
    assert ALL_QUESTIONS.get("kizomba_transitions") is QUESTION_KIZOMBA_TRANSITIONS
    text = QUESTION_KIZOMBA_TRANSITIONS
    # T# format is named explicitly
    assert "T#:" in text
    assert "<boundary_time>s" in text
    assert "<from_label>" in text and "<to_label>" in text
    assert "beat: <from_clarity> → <to_clarity>" in text
    # references the transitions sub-section by name so the model knows the
    # input list is authoritative
    assert "Transitions" in text
    assert "label boundaries" in text


def test_question_kizomba_transitions_inherits_metric_guard():
    """Phase 40 — same metric guard helper as other coaching prompts."""
    assert _METRIC_GUARD_RULE in QUESTION_KIZOMBA_TRANSITIONS


def test_question_kizomba_transitions_inherits_downbeat_guard():
    """Phase 40 — kizomba downbeat guard inherited; no naming the '1'."""
    assert _KIZOMBA_DOWNBEAT_GUARD_RULE in QUESTION_KIZOMBA_TRANSITIONS


def test_question_kizomba_transitions_no_invent_no_skip_rule():
    """Phase 40 — explicit rule that T# entries match the input list exactly."""
    text = QUESTION_KIZOMBA_TRANSITIONS.lower()
    assert "do not invent transitions" in text
    assert "do not skip transitions" in text
    assert "boundary time" in text


def test_question_kizomba_transitions_break_vocabulary():
    """Phase 40 — break boundaries get re-entry vocabulary, not 'pause and hold' default."""
    text = QUESTION_KIZOMBA_TRANSITIONS.lower()
    # Phase 40c: re-entry-primary framing
    assert "re-entry" in text
    # Break re-entry uses the canonical "first clear bass hit" / "wait for the
    # steady pulse" vocabulary (not "chase the loudest percussion").
    assert "first clear bass hit" in text
    assert "keep a small pulse" in text
    # Explicit warning against the 'pause and hold' default (kizomba_tutor lineage,
    # preserved in transitions for break entries).
    assert "do not default to 'pause and hold'" in text or "pause and hold" in text


def test_question_kizomba_transitions_forbids_count_based_anticipation():
    """Phase 40c — the prompt MUST NOT lean on counting beats for anticipation.

    The project's premise is helping learners who can't reliably count to 8;
    using the count to predict transitions inverts that. Anticipation must be
    grounded on audible cues (energy fade, percussion thinning, bass entering)
    or omitted.
    """
    text = QUESTION_KIZOMBA_TRANSITIONS.lower()
    # Explicit forbidden-list of count-based anticipation phrasings
    assert "never anchor anticipation on counting beats" in text
    assert "in the last 8-count of <from>" in text
    assert "in the final 8-count" in text
    # Reasoning is named so future iterators understand WHY this rule exists
    assert "cannot reliably count" in text or "no reliable internal clock" in text


def test_question_kizomba_transitions_audible_cue_vocabulary():
    """Phase 40c — anticipation, when present, names a specific audible signal."""
    text = QUESTION_KIZOMBA_TRANSITIONS.lower()
    # Audible-cue framing examples appear in the prompt (Gemma composes from these)
    assert "energy fades" in text or "energy fading" in text
    assert "percussion thin" in text  # "thinning" or "thins"
    assert "bass kicks in" in text or "bass entering" in text or "percussion returns" in text
    assert "vocals drop" in text  # vocals dropping / dropping out
    # Instructional rule: omit anticipation when no specific cue can be composed
    assert "omit anticipation" in text


def test_question_kizomba_transitions_same_label_rule():
    """Phase 40d — when from_label == to_label (energy shifts within a `main`
    run), the prompt coaches the role shift using the section-role
    vocabulary from kizomba_tutor (sustaining / building / returning).
    """
    text = QUESTION_KIZOMBA_TRANSITIONS
    # Same-label rule branch is named explicitly
    assert "<from_label>` == `<to_label>" in text or "from_label` == `<to_label" in text or "same-label" in text.lower()
    # Role-shift vocabulary references the kizomba_tutor section roles
    lower = text.lower()
    assert "building" in lower
    assert "sustaining" in lower or "returning" in lower
    # Audible-cue anchor specific to subtle same-label shifts
    assert "bass line" in lower
    assert "subtler" in lower or "subtle" in lower


def test_question_kizomba_transitions_re_entry_primary_framing():
    """Phase 40c — re-entry is the primary content of every T# line."""
    # Normalise whitespace so soft-wrap continuations don't trip the assertion
    text = " ".join(QUESTION_KIZOMBA_TRANSITIONS.lower().split())
    # Direct rule: every line MUST include a re-entry cue
    assert "every t# line must include a re-entry cue" in text
    # Re-entry is described as the primary content
    assert "primary content" in text
    # Learner-as-after-the-fact-noticer is named so the model orients to it
    assert "after they notice" in text or "after the dancer notices" in text or "notice that a transition has happened" in text


# ── Phase 40: verify_kizomba_transitions_output ──────────────────────────────

def _transition(
    boundary: float, from_label: str, to_label: str,
    from_clarity: str = "clear", to_clarity: str = "clear",
    from_idx: int = 0, to_idx: int = 1,
) -> Transition:
    return Transition(
        boundary_time_s=boundary,
        from_label=from_label,
        to_label=to_label,
        from_clarity=from_clarity,
        to_clarity=to_clarity,
        from_phase_idx=from_idx,
        to_phase_idx=to_idx,
    )


def test_verify_transitions_passes_clean_output():
    """Well-formed T# lines pass through with all boundaries matched."""
    transitions = [
        _transition(12.0, "intro", "main", from_idx=0, to_idx=1),
        _transition(148.0, "main", "break", from_idx=1, to_idx=2),
        _transition(159.0, "break", "main", from_idx=2, to_idx=3),
        _transition(195.0, "main", "outro", from_idx=3, to_idx=4),
    ]
    raw = "\n".join([
        "T1: 12s [intro → main, beat: clear → clear] — Settle into the pulse during the intro; walk-step on the first clear bass hit of the main.",
        "T2: 148s [main → break, beat: clear → clear] — In the last 8-count of the main, soften the basic and reduce travel; on entering the break, keep a small pulse.",
        "T3: 159s [break → main, beat: clear → clear] — On re-entry, walk-step on the first clear bass hit; don't chase the loudest percussion.",
        "T4: 195s [main → outro, beat: clear → clear] — Energy is winding down; contract movement and slow the basic for the outro.",
    ])

    verified = verify_kizomba_transitions_output(raw, transitions)

    assert verified.stats["parsed"] == 4
    assert verified.stats["boundaries_matched"] == 4
    assert verified.stats["boundaries_invented"] == 0
    assert verified.stats["boundaries_missing_filled"] == 0
    assert verified.stats["skipped_lines"] == 0
    assert verified.stats["output_lines"] == 4
    # Original coaching text preserved for each transition
    assert "Settle into the pulse" in verified.cleaned
    assert "soften the basic" in verified.cleaned


def test_verify_transitions_drops_invented_boundary():
    """A T# line with a boundary time matching no real transition is dropped."""
    transitions = [
        _transition(12.0, "intro", "main"),
        _transition(195.0, "main", "outro", from_idx=1, to_idx=2),
    ]
    raw = "\n".join([
        "T1: 12s [intro → main, beat: clear → clear] — Real transition.",
        "T2: 90s [main → main, beat: clear → clear] — Invented mid-main boundary.",
        "T3: 195s [main → outro, beat: clear → clear] — Real outro transition.",
    ])

    verified = verify_kizomba_transitions_output(raw, transitions)

    # Two real transitions matched; the invented 90s boundary dropped
    assert verified.stats["boundaries_matched"] == 2
    assert verified.stats["boundaries_invented"] == 1
    assert verified.stats["output_lines"] == 2
    assert "Invented mid-main boundary" not in verified.cleaned


def test_verify_transitions_fills_missing_boundary_with_template():
    """Extraction has 4 transitions, output has 3 — verifier fills the 4th."""
    transitions = [
        _transition(12.0, "intro", "main"),
        _transition(148.0, "main", "break", from_idx=1, to_idx=2),
        _transition(159.0, "break", "main", from_idx=2, to_idx=3),
        _transition(195.0, "main", "outro", from_idx=3, to_idx=4),
    ]
    # Skip the break → main re-entry transition (159s)
    raw = "\n".join([
        "T1: 12s [intro → main, beat: clear → clear] — A.",
        "T2: 148s [main → break, beat: clear → clear] — B.",
        "T3: 195s [main → outro, beat: clear → clear] — C.",
    ])

    verified = verify_kizomba_transitions_output(raw, transitions)

    assert verified.stats["boundaries_matched"] == 3
    assert verified.stats["boundaries_missing_filled"] == 1
    assert verified.stats["output_lines"] == 4
    # Filled-in T3 references the break → main re-entry
    assert "break → main" in verified.cleaned
    # Template uses the canonical re-entry vocabulary
    assert "first clear bass hit" in verified.cleaned


def test_verify_transitions_tolerates_2s_rounding():
    """A boundary at 121.34s vs output at 121s is matched (within ±2s)."""
    transitions = [_transition(121.34, "main", "break")]
    raw = "T1: 121s [main → break, beat: clear → clear] — Rounded by 0.34s."

    verified = verify_kizomba_transitions_output(raw, transitions)

    assert verified.stats["boundaries_matched"] == 1
    assert verified.stats["boundaries_invented"] == 0
    assert "Rounded by 0.34s" in verified.cleaned


def test_verify_transitions_no_phases_returns_raw():
    """When transitions list is empty, the verifier returns raw output unchanged."""
    raw = "T1: 12s [intro → main, beat: clear → clear] — anything."
    verified = verify_kizomba_transitions_output(raw, [])
    assert verified.cleaned == raw.strip()
    assert verified.stats == {}


def test_verify_transitions_fallbacks_never_use_count_based_language():
    """Phase 40c rule extends to the structural fallback: when the model
    skips a transition, the deterministic fill must NOT re-introduce the
    count-based anticipation framing the prompt forbids. Covers every
    fallback branch (break, re-entry, peak/build, peak-out, outro, intro,
    instrumental, same-label).
    """
    # One transition per fallback branch in _fallback_transition_tail. All
    # raw outputs are empty, so every cleaned line comes from the fallback.
    transitions = [
        _transition(10.0, "main", "break", from_idx=0, to_idx=1),
        _transition(20.0, "break", "main", from_idx=1, to_idx=2),
        _transition(30.0, "main", "peak", from_idx=2, to_idx=3),
        _transition(40.0, "peak", "main", from_idx=3, to_idx=4),
        _transition(50.0, "main", "outro", from_idx=4, to_idx=5),
        _transition(60.0, "intro", "main", from_idx=5, to_idx=6),
        _transition(70.0, "main", "instrumental", from_idx=6, to_idx=7),
        _transition(80.0, "main", "main", from_idx=7, to_idx=8),
    ]
    verified = verify_kizomba_transitions_output("", transitions)

    # All filled by fallback — every line present.
    assert verified.stats["boundaries_missing_filled"] == len(transitions)
    assert verified.stats["output_lines"] == len(transitions)

    cleaned_lower = verified.cleaned.lower()
    # Forbidden count-based anticipation phrases (mirrors prompt rule).
    forbidden_substrings = [
        "8-count",
        "8 count",
        "eight-count",
        "after n beats",
        "counts before",
        "in the final",
        "in the last",
    ]
    for phrase in forbidden_substrings:
        assert phrase not in cleaned_lower, (
            f"Fallback re-introduced banned anticipation phrase {phrase!r}: "
            f"{verified.cleaned}"
        )


def test_verify_transitions_retry_callback_succeeds_uses_gemma_line():
    """Phase 40e: when retry_callback is supplied and Gemma returns a valid
    line for the missing boundary, the verifier uses Gemma's tail instead of
    the deterministic fallback. Stats include retried + retry_succeeded."""
    transitions = [
        _transition(12.0, "intro", "main", from_idx=0, to_idx=1),
        _transition(148.0, "main", "break", from_idx=1, to_idx=2),
    ]
    # Raw output covers only T1; T2 is missing and would normally be filled
    # by the deterministic break-fallback.
    raw = "T1: 12s [intro → main, beat: clear → clear] — Walk on the first clear bass hit."

    retry_calls: list[str] = []

    def retry_callback(prompt: str) -> str:
        retry_calls.append(prompt)
        return (
            "T2: 148s [main → break, beat: clear → clear] — "
            "as the percussion thins, soften the frame and let the basic breathe."
        )

    verified = verify_kizomba_transitions_output(
        raw, transitions, retry_callback=retry_callback,
    )

    # Retry was triggered for the one missing boundary.
    assert verified.stats["retried"] == 1
    assert verified.stats["retry_succeeded"] == 1
    # Phase 40e: a successful retry is NOT counted as a deterministic fill,
    # so boundaries_missing_filled stays at 0 — the slot was filled by Gemma.
    assert verified.stats["boundaries_missing_filled"] == 0
    # Gemma's retry text appears in cleaned output, deterministic fallback does not.
    assert "as the percussion thins, soften the frame" in verified.cleaned
    assert "keep a small pulse in the body" not in verified.cleaned
    # Retry prompt named the right boundary.
    assert len(retry_calls) == 1
    assert "148s" in retry_calls[0]
    assert "main → break" in retry_calls[0]


def test_verify_transitions_retry_callback_garbage_falls_back_to_deterministic():
    """Phase 40e: when the retry response can't be parsed or matches the wrong
    boundary, the verifier silently falls through to the deterministic
    fallback. retry_succeeded stays at 0."""
    transitions = [
        _transition(148.0, "main", "break", from_idx=0, to_idx=1),
    ]

    def retry_callback(prompt: str) -> str:
        return "Sure! Here's a coaching line for you: focus on the rhythm."

    verified = verify_kizomba_transitions_output(
        "", transitions, retry_callback=retry_callback,
    )

    assert verified.stats["retried"] == 1
    assert verified.stats["retry_succeeded"] == 0
    assert verified.stats["boundaries_missing_filled"] == 1
    # Deterministic break-fallback used (re-entry-primary, audible-cue language).
    assert "as the energy fades and the percussion thins" in verified.cleaned


def test_verify_transitions_retry_callback_exception_falls_back_silently():
    """Retry is best-effort: a callback that raises must not break the
    verifier; the deterministic fallback fills the slot."""
    transitions = [
        _transition(148.0, "main", "break", from_idx=0, to_idx=1),
    ]

    def retry_callback(prompt: str) -> str:
        raise RuntimeError("LLM call failed")

    verified = verify_kizomba_transitions_output(
        "", transitions, retry_callback=retry_callback,
    )

    assert verified.stats["retried"] == 1
    assert verified.stats["retry_succeeded"] == 0
    assert "as the energy fades and the percussion thins" in verified.cleaned


def test_verify_transitions_retry_callback_not_called_when_no_missing():
    """When every boundary is matched by the model output, the retry
    callback is not called and retried/retry_succeeded are both 0."""
    transitions = [
        _transition(12.0, "intro", "main", from_idx=0, to_idx=1),
    ]
    raw = "T1: 12s [intro → main, beat: clear → clear] — Walk on the first clear bass hit."

    calls: list[str] = []

    def retry_callback(prompt: str) -> str:
        calls.append(prompt)
        return ""

    verified = verify_kizomba_transitions_output(
        raw, transitions, retry_callback=retry_callback,
    )

    assert calls == []
    assert verified.stats["retried"] == 0
    assert verified.stats["retry_succeeded"] == 0


def test_verify_transitions_retry_callback_rejects_wrong_boundary():
    """A retry response whose time matches a different boundary must be
    rejected; the deterministic fallback fills the slot. Protects against
    Gemma confidently filling the wrong T#."""
    transitions = [
        _transition(148.0, "main", "break", from_idx=0, to_idx=1),
    ]

    def retry_callback(prompt: str) -> str:
        # Well-formed line but wrong time — must be rejected.
        return (
            "T1: 12s [intro → main, beat: clear → clear] — "
            "walk-step on the first clear bass hit."
        )

    verified = verify_kizomba_transitions_output(
        "", transitions, retry_callback=retry_callback,
    )

    assert verified.stats["retried"] == 1
    assert verified.stats["retry_succeeded"] == 0
    # Deterministic break-fallback wins, not Gemma's intro→main line.
    assert "as the energy fades and the percussion thins" in verified.cleaned
    assert "walk-step on the first clear bass hit" not in verified.cleaned


def test_build_kizomba_transition_retry_prompt_includes_rules():
    """The retry prompt names the bracket explicitly, restates the
    re-entry-primary rule, and bans count-based language. Without these
    the retry has no chance of producing a re-entry-primary line."""
    from rytmi.prompts import build_kizomba_transition_retry_prompt

    tr = _transition(148.0, "main", "break", from_idx=0, to_idx=1)
    prompt = build_kizomba_transition_retry_prompt(tr, idx=2)

    # Bracket reconstructed from the boundary metadata
    assert "T2: 148s [main → break, beat: clear → clear]" in prompt
    # Re-entry-primary rule restated
    assert "re-entry primary" in prompt.lower()
    # Count-based anticipation explicitly forbidden
    assert "8-count" in prompt.lower() or "eight-count" in prompt.lower()
    # Output discipline (one line, no preamble)
    assert "one" in prompt.lower() and "line" in prompt.lower()


def test_verify_transitions_preserves_chronological_order():
    """Output is renumbered T1, T2, T3, ... in transition-index order, even if
    the model emits them out of order."""
    transitions = [
        _transition(12.0, "intro", "main"),
        _transition(148.0, "main", "break", from_idx=1, to_idx=2),
        _transition(195.0, "main", "outro", from_idx=2, to_idx=3),
    ]
    raw = "\n".join([
        "T1: 195s [main → outro, beat: clear → clear] — Last.",
        "T2: 12s [intro → main, beat: clear → clear] — First.",
        "T3: 148s [main → break, beat: clear → clear] — Middle.",
    ])

    verified = verify_kizomba_transitions_output(raw, transitions)
    lines = verified.cleaned.splitlines()
    # Renumbered in chronological order
    assert lines[0].startswith("T1: 12s")
    assert lines[1].startswith("T2: 148s")
    assert lines[2].startswith("T3: 195s")
    # Original coaching text preserved per matched boundary
    assert "First" in lines[0]
    assert "Middle" in lines[1]
    assert "Last" in lines[2]


# ── Phase 40d: format_unified_timeline ───────────────────────────────────────

_FILOMENA_TUTOR_SAMPLE = (
    "P1: 0s-12s, intro [beat: clear] — Find your connection and settle in.\n"
    "P2: 12s-59s, main ×4 [beat: clear] — Establish your rhythm with a steady walk-step.\n"
    "P3: 59s-80s, main ×2 [beat: clear] — Maintain energy by keeping a stable frame.\n"
    "P4: 80s-121s, main ×4 [beat: clear] — Sustain the flow with consistent walking.\n"
    "P5: 121s-148s, main ×2 [beat: clear] — Build momentum with slightly larger steps.\n"
    "P6: 148s-159s, break [beat: clear] — Reduce travel; keep a small pulse, reset.\n"
    "P7: 159s-195s, main ×3 [beat: clear] — Re-establish your basic walk-step.\n"
    "P8: 195s-209s, outro [beat: clear] — Close the dance with smaller movements."
)

_FILOMENA_TRANSITIONS_SAMPLE = (
    "T1: 12s [intro → main, beat: clear → clear] — when the bass kicks in, walk-step.\n"
    "T2: 148s [main → break, beat: clear → clear] — as the energy fades, keep a small pulse.\n"
    "T3: 159s [break → main, beat: clear → clear] — as the percussion returns, walk-step.\n"
    "T4: 195s [main → outro, beat: clear → clear] — as the energy fades, contract movement."
)


def test_format_unified_timeline_interleaves_p_and_t_lines():
    """Phase 40d — given Filomena's tutor + transitions, the unified timeline
    interleaves P# and T# in chronological order with T# bridging adjacent
    phases.
    """
    out = format_unified_timeline(_FILOMENA_TUTOR_SAMPLE, _FILOMENA_TRANSITIONS_SAMPLE)
    lines = out.splitlines()
    expected_starts = [
        "P1: 0s",          # 0s
        "T1: 12s",          # boundary at 12s (before P2)
        "P2: 12s",          # 12s
        "P3: 59s",
        "P4: 80s",
        "P5: 121s",
        "T2: 148s",         # boundary at 148s (before P6)
        "P6: 148s",
        "T3: 159s",         # boundary at 159s (before P7)
        "P7: 159s",
        "T4: 195s",         # boundary at 195s (before P8)
        "P8: 195s",
    ]
    assert len(lines) == len(expected_starts), f"unexpected line count: {lines}"
    for line, start in zip(lines, expected_starts):
        assert line.startswith(start), f"line {line!r} should start with {start!r}"


def test_format_unified_timeline_t_before_p_at_same_boundary():
    """At equal time, T# precedes P# so the transition reads as the bridge."""
    tutor = "P1: 12s-59s, main [beat: clear] — coach me.\n"
    transitions = "T1: 12s [intro → main, beat: clear → clear] — bridge.\n"
    out = format_unified_timeline(tutor, transitions)
    lines = out.splitlines()
    assert lines[0].startswith("T1: 12s")
    assert lines[1].startswith("P1: 12s")


def test_format_unified_timeline_handles_empty_transitions():
    """Empty transitions text yields tutor lines only."""
    out = format_unified_timeline(_FILOMENA_TUTOR_SAMPLE, "")
    lines = out.splitlines()
    assert len(lines) == 8  # 8 P# lines, no T#
    assert all(line.startswith("P") for line in lines)


def test_format_unified_timeline_falls_back_when_tutor_unparseable():
    """If tutor has no parseable P# lines, both outputs are concatenated under
    headers so no coaching content is lost.
    """
    out = format_unified_timeline(
        "Sorry, I can't help with that.",  # no P# lines
        _FILOMENA_TRANSITIONS_SAMPLE,
    )
    assert "--- kizomba_tutor ---" in out
    assert "--- kizomba_transitions ---" in out
    assert "Sorry, I can't help with that." in out
    assert "T1: 12s" in out


def test_format_unified_timeline_handles_same_label_transitions():
    """Phase 40d — when same-label transitions are emitted (main → main with
    energy shift), they interleave between same-label P# lines.
    """
    tutor = (
        "P2: 12s-59s, main ×4 [beat: clear] — Establish your rhythm.\n"
        "P3: 59s-80s, main ×2 [beat: clear] — Maintain your energy.\n"
    )
    transitions = (
        "T1: 59s [main → main, beat: clear → clear] — "
        "as the bass thickens, travel a little more.\n"
    )
    out = format_unified_timeline(tutor, transitions)
    lines = out.splitlines()
    assert lines[0].startswith("P2: 12s")
    assert lines[1].startswith("T1: 59s")  # bridges P2 and P3
    assert lines[2].startswith("P3: 59s")
