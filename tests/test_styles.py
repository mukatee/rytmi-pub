"""Tests for rytmi.styles — style profiles, accent classification, accent descriptions."""

import pytest

from rytmi.styles import (
    BACHATA_PROFILE,
    KIZOMBA_PROFILE,
    SEMBA_PROFILE,
    _classify_accent_pattern,
    describe_beat_accent,
    get_style_profile,
    list_styles,
)


# ---------------------------------------------------------------------------
# get_style_profile
# ---------------------------------------------------------------------------


def test_get_style_profile_known():
    assert get_style_profile("bachata") is BACHATA_PROFILE
    assert get_style_profile("kizomba") is KIZOMBA_PROFILE
    assert get_style_profile("semba") is SEMBA_PROFILE


def test_get_style_profile_case_insensitive():
    assert get_style_profile("Bachata") is BACHATA_PROFILE
    assert get_style_profile("KIZOMBA") is KIZOMBA_PROFILE


def test_get_style_profile_strips_whitespace():
    assert get_style_profile("  bachata  ") is BACHATA_PROFILE


def test_get_style_profile_unknown_returns_none():
    assert get_style_profile("waltz") is None


def test_get_style_profile_none_returns_none():
    assert get_style_profile(None) is None


def test_get_style_profile_empty_returns_none():
    assert get_style_profile("") is None


# ---------------------------------------------------------------------------
# list_styles
# ---------------------------------------------------------------------------


def test_list_styles():
    styles = list_styles()
    assert "bachata" in styles
    assert "kizomba" in styles
    assert "semba" in styles
    assert styles == sorted(styles), "list_styles should return sorted names"


# ---------------------------------------------------------------------------
# _classify_accent_pattern
# ---------------------------------------------------------------------------


def test_classify_empty_pattern():
    assert _classify_accent_pattern([]) == "even"


def test_classify_single_beat():
    assert _classify_accent_pattern([1.0]) == "even"


def test_classify_even_pattern():
    assert _classify_accent_pattern([0.8, 0.7, 0.8, 0.7]) == "even"


def test_classify_strong_123_weak_4():
    assert _classify_accent_pattern([1.0, 0.8, 0.7, 0.2]) == "strong_123_weak_4"


def test_classify_strong_1_only():
    assert _classify_accent_pattern([1.0, 0.5, 0.5, 0.5]) == "strong_1_only"


def test_classify_strong_1_and_3():
    assert _classify_accent_pattern([1.0, 0.3, 0.9, 0.3]) == "strong_1_and_3"


# ---------------------------------------------------------------------------
# describe_beat_accent
# ---------------------------------------------------------------------------


def test_describe_beat_accent_no_data():
    assert describe_beat_accent([]) == "no accent data"


def test_describe_beat_accent_with_profile():
    desc = describe_beat_accent([1.0, 0.8, 0.7, 0.2], BACHATA_PROFILE)
    # Should use style-specific accent hint
    assert "bachata" in desc.lower()


def test_describe_beat_accent_generic_fallback():
    desc = describe_beat_accent([1.0, 0.8, 0.7, 0.2])
    # No profile → generic description, should mention strong beats
    assert "strong" in desc.lower()


def test_describe_beat_accent_even_pattern():
    desc = describe_beat_accent([0.7, 0.7, 0.7, 0.7])
    assert "even" in desc.lower() or "pulse" in desc.lower()


# ---------------------------------------------------------------------------
# StyleProfile structure sanity
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("profile", [BACHATA_PROFILE, KIZOMBA_PROFILE, SEMBA_PROFILE])
def test_profile_has_required_sections(profile):
    """Each profile should have coaching for at least intro, main, break."""
    for section in ("intro", "main", "break"):
        assert section in profile.section_coaching, (
            f"{profile.name} missing section_coaching[{section!r}]"
        )


@pytest.mark.parametrize("profile", [BACHATA_PROFILE, KIZOMBA_PROFILE, SEMBA_PROFILE])
def test_profile_has_bpm_range(profile):
    lo, hi = profile.bpm_range
    assert lo < hi
    assert lo > 0


@pytest.mark.parametrize("profile", [BACHATA_PROFILE, KIZOMBA_PROFILE, SEMBA_PROFILE])
def test_profile_has_general_context(profile):
    assert len(profile.general_context) > 30
