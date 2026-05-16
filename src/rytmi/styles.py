"""Dance style profiles for style-aware rhythm coaching.

Each ``StyleProfile`` holds per-style interpretation knowledge in one place:
section coaching, beat-accent hints, and general context injected into prompts.
DSP segmentation is style-agnostic — only the interpretation layer uses these.
"""

from __future__ import annotations

from rytmi.types import StyleProfile

# ── Beat-accent pattern classification thresholds ─────────────────────────────
# A beat position is "strong" if its normalised strength >= this fraction of max.
_STRONG_THRESHOLD = 0.65
# A beat position is "weak" if its normalised strength <= this fraction of max.
_WEAK_THRESHOLD = 0.35


# ── Bachata ───────────────────────────────────────────────────────────────────

BACHATA_PROFILE = StyleProfile(
    name="bachata",
    bpm_range=(120, 135),
    section_coaching={
        "intro": (
            "Relaxed basic step, connect with your partner, "
            "feel the guitar rhythm before committing to big movement."
        ),
        "main": (
            "Full basic with body movement and hip action. "
            "Follow the bongo pattern — the percussion guides your timing."
        ),
        "break": (
            "Styling opportunity — mambo footwork, body isolations, arm work. "
            "The music opens up here, use the space."
        ),
        "build": (
            "Energy is rising — prepare for turns or bigger movement. "
            "Keep the basic tight but let your movement grow."
        ),
        "peak": (
            "Turns, dips, show-off combinations. "
            "This is the high-energy moment; commit fully to each move."
        ),
        "outro": (
            "Wind down, return to basic, close connection. "
            "Match the music's decreasing energy."
        ),
    },
    accent_hints={
        "strong_123_weak_4": (
            "Clear 1-2-3, tap on 4 — the signature bachata basic."
        ),
        "strong_1_and_4": (
            "Accent on 1 and 4 — syncopated feel, add hip emphasis on the accented beats."
        ),
        "strong_1_and_3": (
            "Accent on 1 and 3 — half-time feel, emphasize the landing on each pair."
        ),
        "even": (
            "Steady pulse — keep the basic consistent, add your own styling accents."
        ),
        "strong_1_only": (
            "Strong downbeat with lighter follow-through — anchor your step firmly on 1."
        ),
    },
    general_context=(
        "Bachata is a Latin partner dance in 4/4 time, typically at 120-135 BPM. "
        "The basic step is three side-steps and a tap on count 4 (1-2-3-tap, "
        "5-6-7-tap). The guitar and bongo percussion define the rhythmic feel. "
        "Dancers listen for the downbeat (1) to start phrases and use the tap on "
        "4 and 8 for hip accents or styling."
    ),
    basic_step=(
        "The bachata basic is ALWAYS step-step-step-tap repeated twice per 8-count: "
        "1-2-3-tap(4), 5-6-7-tap(8). The tap lands on counts 4 and 8 with a hip "
        "accent. NEVER describe it as 3+3+2, step-step-tap-step-step-tap, or any "
        "other grouping. Pauses or styling may span 4 or 8 counts but the basic "
        "pattern itself is always 3-steps-then-tap."
    ),
)

# ── Kizomba ───────────────────────────────────────────────────────────────────

KIZOMBA_PROFILE = StyleProfile(
    name="kizomba",
    bpm_range=(85, 110),
    section_coaching={
        "intro": (
            "Close embrace, minimal movement, just feel the pulse together. "
            "This is about connection, not steps."
        ),
        "main": (
            "Steady walk-step, saídas, follow the bass line. "
            "Let the bass guide when to step — less is more."
        ),
        "break": (
            "Pause and hold — stop stepping, breathe, listen to the silence. "
            "The break is part of the dance; stillness is intentional."
        ),
        "build": (
            "Gradually increase step size and expression, build tension. "
            "The music is pulling you forward — let it."
        ),
        "peak": (
            "Stronger saídas, more leading variety, more expression. "
            "This is the emotional high point of the song."
        ),
        "outro": (
            "Slow down, return to minimal movement, close the feeling of the intro. "
            "Let the dance end gently."
        ),
    },
    accent_hints={
        "strong_1_only": (
            "Lead with the downbeat — strong step on 1, light steps follow."
        ),
        "strong_1_and_3": (
            "Half-time feel — step only on 1 and 3, or slow your walk to match."
        ),
        "even": (
            "Smooth pulse — steady walk, match the bass."
        ),
        "strong_123_weak_4": (
            "Three-step pattern with a light 4 — step-step-step-pause, "
            "similar feel to a tarraxinha moment."
        ),
        "strong_1_and_4": (
            "Syncopated feel — the bass pulls on 4, lean into it with weight transfer."
        ),
    },
    general_context=(
        "Kizomba is a close-embrace partner dance from Angola, typically at "
        "85-110 BPM. The bass line drives the movement — dancers step into the "
        "beat rather than counting strict 8-counts. Smoothness and connection "
        "matter more than flashy steps. Breaks and pauses in the music are "
        "danced as stillness, not filled with movement."
    ),
    basic_step=(
        "Kizomba uses a smooth walk-step guided by the bass line. There is no "
        "rigid 8-count pattern — the dancer follows the pulse and the lead, "
        "stepping when the bass invites movement. Avoid describing it with "
        "strict counted patterns like bachata or salsa."
    ),
)

# ── Semba ─────────────────────────────────────────────────────────────────────

SEMBA_PROFILE = StyleProfile(
    name="semba",
    bpm_range=(130, 160),
    section_coaching={
        "intro": (
            "Find the connection, feel the faster pulse — semba is energetic "
            "from the start but still grounded."
        ),
        "main": (
            "Bouncy walk-step at speed, use the chest lead. "
            "Semba is kizomba's faster ancestor — same close embrace, more energy."
        ),
        "break": (
            "Brief pause or slow moment — catch your breath, "
            "reset the connection before the energy returns."
        ),
        "build": (
            "The tempo pulls you in — let the energy build through the embrace, "
            "prepare for bigger movement."
        ),
        "peak": (
            "Full energy — bigger steps, more playful leading, "
            "embody the joy of the music."
        ),
        "outro": (
            "Ease down, smaller steps, return to the core connection."
        ),
    },
    accent_hints={
        "strong_1_only": (
            "Strong bounce on 1 — anchor each measure, let the momentum carry through."
        ),
        "strong_1_and_3": (
            "Bounce on 1 and 3 — quick-quick pulse, stay light on your feet."
        ),
        "even": (
            "Driving pulse — keep your walk even and grounded, match the percussion."
        ),
        "strong_123_weak_4": (
            "Step-step-step-light — similar to a quick semba basic pattern."
        ),
        "strong_1_and_4": (
            "Syncopated groove — feel the push-pull between 1 and 4."
        ),
    },
    general_context=(
        "Semba is an Angolan partner dance and the ancestor of kizomba, "
        "typically at 130-160 BPM. It shares kizomba's close embrace but is "
        "much faster and more playful. The music is often in Portuguese or "
        "Kimbundu. Dancers use a bouncy walk-step driven by chest connection. "
        "If a track is detected at 140+ BPM with Portuguese vocals, consider "
        "whether it might be semba rather than double-time kizomba."
    ),
    basic_step=(
        "Semba uses a bouncy walk-step driven by chest connection, faster and "
        "more playful than kizomba. The lead comes from the chest/torso, not "
        "the arms. Movement is grounded but with a visible bounce on each step."
    ),
)

# ── Profile registry ──────────────────────────────────────────────────────────

_PROFILES: dict[str, StyleProfile] = {
    p.name: p for p in [BACHATA_PROFILE, KIZOMBA_PROFILE, SEMBA_PROFILE]
}


def get_style_profile(name: str) -> StyleProfile | None:
    """Look up a style profile by name (case-insensitive).

    Returns ``None`` for unknown styles so callers can fall back gracefully.
    """
    return _PROFILES.get(name.lower().strip()) if name else None


def list_styles() -> list[str]:
    """Return the names of all registered style profiles."""
    return sorted(_PROFILES.keys())


# ── Beat accent description ───────────────────────────────────────────────────

def _classify_accent_pattern(pattern: list[float]) -> str:
    """Classify a normalised beat-strength pattern into a named accent type.

    The pattern is expected to be normalised to [0, 1] with the strongest
    position at 1.0.  Returns a key that matches ``StyleProfile.accent_hints``.
    """
    if not pattern or len(pattern) < 2:
        return "even"

    strong = [i for i, v in enumerate(pattern) if v >= _STRONG_THRESHOLD]
    weak = [i for i, v in enumerate(pattern) if v <= _WEAK_THRESHOLD]
    n = len(pattern)

    # All roughly equal
    if len(strong) == n:
        return "even"
    # No strong beats at all — uniform mid-range
    if not strong and not weak:
        return "even"

    has_strong_1 = 0 in strong

    if n >= 4:
        # strong 1,2,3 weak 4 (classic bachata-like)
        if has_strong_1 and 1 in strong and 2 in strong and 3 in weak:
            return "strong_123_weak_4"
        # strong 1 and 4
        if has_strong_1 and 3 in strong and 1 not in strong and 2 not in strong:
            return "strong_1_and_4"
        if has_strong_1 and (n - 1) in strong and len(strong) == 2:
            return "strong_1_and_4"

    # strong 1 and 3 (half-time)
    if has_strong_1 and 2 in strong and len(strong) == 2 and n >= 4:
        return "strong_1_and_3"
    if has_strong_1 and len(strong) <= 2 and n >= 3:
        # Just beat 1 dominant
        if len(strong) == 1:
            return "strong_1_only"
        # 1 and middle beat
        mid = n // 2
        if mid in strong:
            return "strong_1_and_3"

    return "even"


def describe_beat_accent(
    pattern: list[float],
    profile: StyleProfile | None = None,
) -> str:
    """Return a human-readable description of a beat-accent pattern.

    When a ``StyleProfile`` is provided and contains a matching accent hint,
    the style-specific description is returned.  Otherwise a generic
    description is built from the pattern.

    >>> describe_beat_accent([1.0, 0.8, 0.7, 0.2], BACHATA_PROFILE)
    'Clear 1-2-3, tap on 4 — the signature bachata basic.'
    """
    if not pattern:
        return "no accent data"

    accent_type = _classify_accent_pattern(pattern)

    # Try style-specific hint first
    if profile and accent_type in profile.accent_hints:
        return profile.accent_hints[accent_type]

    # Generic fallback
    return _generic_accent_description(pattern, accent_type)


def _generic_accent_description(pattern: list[float], accent_type: str) -> str:
    """Build a generic accent description when no style profile is available."""
    n = len(pattern)
    strong_beats = [str(i + 1) for i, v in enumerate(pattern) if v >= _STRONG_THRESHOLD]
    weak_beats = [str(i + 1) for i, v in enumerate(pattern) if v <= _WEAK_THRESHOLD]

    if accent_type == "even":
        return f"Even pulse across all {n} beats."

    parts = []
    if strong_beats:
        parts.append(f"strong on beat{'s' if len(strong_beats) > 1 else ''} {', '.join(strong_beats)}")
    if weak_beats:
        parts.append(f"weak on beat{'s' if len(weak_beats) > 1 else ''} {', '.join(weak_beats)}")

    return "; ".join(parts).capitalize() + "." if parts else f"Mixed accents across {n} beats."
