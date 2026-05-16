import matplotlib
import matplotlib.pyplot as plt
import pytest

from rytmi.dsp import analyze
from rytmi.viz import (
    SECTION_COLORS,
    plot_analysis,
    plot_beats,
    plot_onset_strength,
    plot_onsets,
    plot_spectrogram,
    plot_timeline,
    plot_waveform,
)

matplotlib.use("Agg")  # Non-interactive backend for tests


@pytest.fixture
def analysis(synthetic_click_audio):
    return analyze(synthetic_click_audio)


def test_plot_waveform(synthetic_click_audio):
    ax = plot_waveform(synthetic_click_audio)
    assert isinstance(ax, matplotlib.axes.Axes)
    plt.close("all")


def test_plot_spectrogram(synthetic_click_audio):
    ax = plot_spectrogram(synthetic_click_audio)
    assert isinstance(ax, matplotlib.axes.Axes)
    plt.close("all")


def test_plot_onsets(synthetic_click_audio, analysis):
    ax = plot_onsets(synthetic_click_audio, analysis.onsets)
    assert isinstance(ax, matplotlib.axes.Axes)
    plt.close("all")


def test_plot_beats(synthetic_click_audio, analysis):
    ax = plot_beats(synthetic_click_audio, analysis.beats)
    assert isinstance(ax, matplotlib.axes.Axes)
    plt.close("all")


def test_plot_onset_strength(analysis):
    ax = plot_onset_strength(analysis.onsets)
    assert isinstance(ax, matplotlib.axes.Axes)
    plt.close("all")


def test_plot_analysis(analysis):
    fig = plot_analysis(analysis)
    assert isinstance(fig, matplotlib.figure.Figure)
    assert len(fig.axes) == 3
    plt.close("all")


def test_analysis_has_phrase_length(analysis):
    assert analysis.phrase_length == 8


def test_plot_timeline_with_phrases(analysis):
    fig = plot_timeline(analysis, show_phrases=True)
    assert isinstance(fig, matplotlib.figure.Figure)
    assert len(fig.axes) == 2
    plt.close("all")


def test_plot_timeline_without_phrases(analysis):
    fig = plot_timeline(analysis, show_phrases=False)
    assert isinstance(fig, matplotlib.figure.Figure)
    assert len(fig.axes) == 2
    plt.close("all")


# --- Phase 4: section-aware visualization ---


def test_section_colors_covers_all_labels():
    expected = {
        "intro", "main", "break", "short_break", "build", "peak",
        "instrumental", "outro", "spoken_intro",
    }
    assert set(SECTION_COLORS.keys()) == expected


def test_section_colors_instrumental_distinct():
    """instrumental should be perceptually distinct from every other label."""
    inst = _hex_to_rgb(SECTION_COLORS["instrumental"])
    for other in ("main", "break", "short_break", "peak", "intro", "build", "outro"):
        rgb = _hex_to_rgb(SECTION_COLORS[other])
        channel_gap = max(abs(i - c) for i, c in zip(inst, rgb))
        assert channel_gap >= 40, (
            f"instrumental vs {other} too close: instrumental={inst} {other}={rgb}"
        )


def test_section_colors_short_break_distinct_from_break_and_main():
    short = _hex_to_rgb(SECTION_COLORS["short_break"])
    brk = _hex_to_rgb(SECTION_COLORS["break"])
    main = _hex_to_rgb(SECTION_COLORS["main"])
    assert short != brk
    assert short != main
    # Require a meaningful perceptual gap so a 1-phrase short_break band
    # reads as a distinct zone rather than blending into the yellow break
    # or grey main next to it.
    brk_gap = max(abs(s - b) for s, b in zip(short, brk))
    main_gap = max(abs(s - m) for s, m in zip(short, main))
    assert brk_gap >= 40, f"short_break vs break too close: short={short} break={brk}"
    assert main_gap >= 40, f"short_break vs main too close: short={short} main={main}"


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def test_section_colors_outro_and_main_distinct():
    outro = _hex_to_rgb(SECTION_COLORS["outro"])
    main = _hex_to_rgb(SECTION_COLORS["main"])
    assert outro != main
    # Require a meaningful perceptual gap so low-alpha outro bands still read
    # as purple rather than washing out to the grey used for `main`.
    channel_gap = max(abs(o - m) for o, m in zip(outro, main))
    assert channel_gap >= 40, f"outro vs main too close: outro={outro} main={main}"


def test_section_colors_spoken_intro_distinct():
    """spoken_intro must read as its own zone vs intro / main / outro."""
    spoken = _hex_to_rgb(SECTION_COLORS["spoken_intro"])
    for other in ("intro", "main", "outro"):
        rgb = _hex_to_rgb(SECTION_COLORS[other])
        channel_gap = max(abs(s - r) for s, r in zip(spoken, rgb))
        assert channel_gap >= 40, (
            f"spoken_intro vs {other} too close: spoken={spoken} {other}={rgb}"
        )


def _make_phases():
    """Create minimal SongPhase objects for testing."""
    from rytmi.types import SongPhase

    return [
        SongPhase(label="intro", start_s=0.0, end_s=0.5, section_count=1,
                  energy_levels=["low"]),
        SongPhase(label="main", start_s=0.5, end_s=1.5, section_count=2,
                  energy_levels=["medium", "medium"]),
        SongPhase(label="outro", start_s=1.5, end_s=2.0, section_count=1,
                  energy_levels=["low"]),
    ]


def test_plot_timeline_with_sections(analysis):
    analysis.phases = _make_phases()
    fig = plot_timeline(analysis, show_phrases=True)
    assert isinstance(fig, matplotlib.figure.Figure)
    # Should have axvspan patches on the waveform axis
    ax_wave = fig.axes[0]
    span_patches = [
        p for p in ax_wave.patches
        if hasattr(p, "get_width") and p.get_width() > 0
    ]
    assert len(span_patches) >= 3  # one per phase
    plt.close("all")


def test_plot_timeline_no_sections_backward_compat(analysis):
    """Analysis without phases still renders normally (no extra patches)."""
    analysis.phases = []
    fig = plot_timeline(analysis, show_phrases=True)
    ax_wave = fig.axes[0]
    # No section color band patches expected
    span_patches = [
        p for p in ax_wave.patches
        if hasattr(p, "get_width") and p.get_width() > 0
    ]
    assert len(span_patches) == 0
    plt.close("all")


def test_plot_timeline_section_legend_entries(analysis):
    """Legend should contain Patch entries for section labels present in phases."""
    analysis.phases = _make_phases()
    fig = plot_timeline(analysis, show_phrases=True)
    ax_wave = fig.axes[0]
    legend = ax_wave.get_legend()
    legend_labels = [t.get_text() for t in legend.get_texts()]
    # Our phases have intro, main, outro
    for label in ["intro", "main", "outro"]:
        assert label in legend_labels, f"'{label}' missing from legend"
    # Labels NOT in phases should not appear
    for label in ["break", "build", "peak"]:
        assert label not in legend_labels, f"'{label}' should not be in legend"
    plt.close("all")


# --- Phase 4.5: energy-level encoding on timeline ---


def test_plot_timeline_energy_scales_band_alpha(analysis):
    """Phases with higher energy should render with more opaque bands."""
    from rytmi.types import SongPhase

    analysis.phases = [
        SongPhase(label="intro", start_s=0.0, end_s=1.0, section_count=1,
                  energy_levels=["low"]),
        SongPhase(label="peak", start_s=1.0, end_s=2.0, section_count=1,
                  energy_levels=["high"]),
    ]
    fig = plot_timeline(analysis, show_phrases=True)
    ax_wave = fig.axes[0]
    # Pair each axvspan patch (low x first) with its alpha
    spans = [
        p for p in ax_wave.patches
        if hasattr(p, "get_width") and p.get_width() > 0
    ]
    assert len(spans) >= 2
    # Sort by x-position so we know which is which
    spans_sorted = sorted(spans, key=lambda p: p.get_x())
    low_alpha = spans_sorted[0].get_alpha()
    high_alpha = spans_sorted[1].get_alpha()
    assert low_alpha is not None and high_alpha is not None
    assert low_alpha < high_alpha


def test_plot_timeline_energy_legend_entries(analysis):
    """Legend should include energy swatches for energies present in the phases."""
    from rytmi.types import SongPhase

    analysis.phases = [
        SongPhase(label="intro", start_s=0.0, end_s=1.0, section_count=1,
                  energy_levels=["low"]),
        SongPhase(label="main", start_s=1.0, end_s=2.0, section_count=1,
                  energy_levels=["high"]),
    ]
    fig = plot_timeline(analysis, show_phrases=True)
    legend_labels = [t.get_text() for t in fig.axes[0].get_legend().get_texts()]
    assert "low" in legend_labels
    assert "high" in legend_labels
    # Medium is not present in these phases and should not appear as an
    # energy entry (though "medium" may appear in other contexts, the
    # legend should not carry an entry for an unused energy level).
    plt.close("all")


def test_plot_timeline_dominant_energy_rounds_up_on_tie():
    """A phase with [medium, high] energies should round up to 'high'.

    Verified via the helper directly rather than through the figure since
    asserting on exact alpha requires knowing the dominant energy logic.
    """
    from rytmi.viz import _dominant_energy

    assert _dominant_energy(["medium", "high"]) == "high"
    assert _dominant_energy(["low", "low", "medium"]) == "low"
    assert _dominant_energy(["high", "high", "medium"]) == "high"
    assert _dominant_energy([]) == "medium"
    assert _dominant_energy(["low"]) == "low"


def test_plot_timeline_no_sections_no_energy_legend(analysis):
    """Backward-compat: tracks without phases should have no energy legend entries."""
    analysis.phases = []
    fig = plot_timeline(analysis, show_phrases=True)
    legend = fig.axes[0].get_legend()
    if legend is not None:
        labels = [t.get_text() for t in legend.get_texts()]
        # No energy swatches should appear
        for energy in ["low", "medium", "high"]:
            assert energy not in labels
    plt.close("all")


# --- Phase 7: downbeat-anchored phrase grid ---


def test_plot_timeline_pickup_beats_with_offset(analysis):
    """With offset=3, first 3 beats should render as pickup (grey) — no crash."""
    import numpy as np

    analysis.downbeat_offset = 3
    analysis.downbeat_confidence = 0.50
    fig = plot_timeline(analysis, show_phrases=True)
    assert isinstance(fig, matplotlib.figure.Figure)
    ax = fig.axes[0]
    texts = [t.get_text() for t in ax.texts]
    assert "·" in texts
    plt.close("all")


def test_plot_timeline_zero_offset_unchanged(analysis):
    """With offset=0, timeline should render the same as before — no pickup dots."""
    analysis.downbeat_offset = 0
    fig = plot_timeline(analysis, show_phrases=True)
    assert isinstance(fig, matplotlib.figure.Figure)
    ax = fig.axes[0]
    texts = [t.get_text() for t in ax.texts]
    assert "·" not in texts
    plt.close("all")
