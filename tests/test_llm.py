"""Tests for llm.py and prompts.py — no GPU or model download required."""

import sys
import types

import pytest

from rytmi.prompts import (
    ALL_QUESTIONS,
    DEFAULT_SYSTEM_PROMPT,
    QUESTION_COUNTING,
    downbeat_confidence_label,
    format_analysis_prompt,
)


# ---------------------------------------------------------------------------
# prompts.py tests
# ---------------------------------------------------------------------------

def test_format_analysis_prompt_no_unfilled_placeholders():
    result = format_analysis_prompt(
        duration=10.0,
        tempo=120.0,
        n_beats=20,
        n_onsets=20,
        beat_times=[0.0, 0.5, 1.0, 1.5],
        ioi_ms=[500.0, 500.0, 500.0],
        question=QUESTION_COUNTING,
    )
    assert "{" not in result
    assert "}" not in result


def test_format_analysis_prompt_contains_data():
    result = format_analysis_prompt(
        duration=10.0,
        tempo=120.0,
        n_beats=20,
        n_onsets=20,
        beat_times=[0.0, 0.5],
        ioi_ms=[500.0],
        question="Test question?",
    )
    assert "120" in result
    assert "10.0" in result
    assert "20" in result
    assert "Test question?" in result


def test_format_analysis_prompt_truncates_long_lists():
    beat_times = [i * 0.5 for i in range(20)]
    ioi_ms = [500.0] * 20
    result = format_analysis_prompt(
        duration=10.0,
        tempo=120.0,
        n_beats=20,
        n_onsets=20,
        beat_times=beat_times,
        ioi_ms=ioi_ms,
        question="Q",
    )
    assert "(20 total)" in result
    assert "(20 intervals)" in result


def test_format_analysis_prompt_empty_ioi():
    result = format_analysis_prompt(
        duration=5.0,
        tempo=100.0,
        n_beats=5,
        n_onsets=1,
        beat_times=[0.0],
        ioi_ms=None,
        question="Q",
    )
    assert "N/A" in result


def test_all_questions_keys():
    expected = {
        "time_signature", "counting", "style_fit",
        "difficulty", "exercise", "dancer", "song_arc", "sections",
        "rhythm_anatomy", "listening_guide", "kizomba_tutor", "kizomba_drills",
        "kizomba_transitions",
        "bachata_tutor", "bachata_drills", "bachata_transitions",
    }
    assert set(ALL_QUESTIONS.keys()) == expected


def test_all_questions_are_non_empty_strings():
    for key, text in ALL_QUESTIONS.items():
        assert isinstance(text, str), f"{key} is not a string"
        assert len(text) > 20, f"{key} question seems too short"


def test_default_system_prompt_not_empty():
    assert len(DEFAULT_SYSTEM_PROMPT) > 50


# ---------------------------------------------------------------------------
# downbeat_confidence_label tests
# ---------------------------------------------------------------------------

def test_confidence_label_high():
    assert downbeat_confidence_label(0.50) == "high confidence"
    assert downbeat_confidence_label(0.35) == "high confidence"


def test_confidence_label_plausible():
    assert downbeat_confidence_label(0.20) == "plausible guess"
    assert downbeat_confidence_label(0.15) == "plausible guess"


def test_confidence_label_ambiguous():
    assert downbeat_confidence_label(0.00) == "ambiguous — treat as a weak guess"
    assert downbeat_confidence_label(0.10) == "ambiguous — treat as a weak guess"
    # boundary: just below the low threshold
    assert downbeat_confidence_label(0.149) == "ambiguous — treat as a weak guess"


def test_confidence_label_boundary_between_plausible_and_high():
    # 0.35 is exactly the high boundary
    assert downbeat_confidence_label(0.35) == "high confidence"
    assert downbeat_confidence_label(0.3499) == "plausible guess"


# ---------------------------------------------------------------------------
# format_analysis_prompt — downbeat section tests
# ---------------------------------------------------------------------------

def test_format_analysis_prompt_with_downbeat_data_no_placeholders():
    """Adding downbeat data should not leave any unfilled placeholders."""
    import numpy as np

    result = format_analysis_prompt(
        duration=10.0,
        tempo=120.0,
        n_beats=20,
        n_onsets=20,
        beat_times=[0.0, 0.5, 1.0, 1.5],
        ioi_ms=[500.0, 500.0, 500.0],
        question=QUESTION_COUNTING,
        downbeat_times=np.array([0.0, 2.0, 4.0, 6.0, 8.0]),
        downbeat_confidence=0.42,
    )
    assert "{" not in result
    assert "}" not in result


def test_format_analysis_prompt_includes_downbeat_times_and_label():
    """Prompt should contain the downbeat times and the confidence label."""
    import numpy as np

    result = format_analysis_prompt(
        duration=10.0,
        tempo=120.0,
        n_beats=20,
        n_onsets=20,
        beat_times=[0.0, 0.5],
        ioi_ms=[500.0],
        question="Q?",
        downbeat_times=np.array([0.0, 2.0, 4.0]),
        downbeat_confidence=0.42,
    )
    assert "0.00" in result          # first downbeat time
    assert "high confidence" in result
    assert "0.42" in result


def test_format_analysis_prompt_low_confidence_adds_uncertainty_note():
    """A confidence below the low threshold should add an explicit uncertainty note."""
    import numpy as np

    result = format_analysis_prompt(
        duration=10.0,
        tempo=120.0,
        n_beats=20,
        n_onsets=20,
        beat_times=[0.0, 0.5],
        ioi_ms=[500.0],
        question="Q?",
        downbeat_times=np.array([0.0, 2.0]),
        downbeat_confidence=0.03,
    )
    assert "uncertain" in result.lower()
    assert "ambiguous" in result


def test_format_analysis_prompt_high_confidence_no_uncertainty_note():
    """A confident estimate should not add the uncertainty note."""
    import numpy as np

    result = format_analysis_prompt(
        duration=10.0,
        tempo=120.0,
        n_beats=20,
        n_onsets=20,
        beat_times=[0.0, 0.5],
        ioi_ms=[500.0],
        question="Q?",
        downbeat_times=np.array([0.0, 2.0]),
        downbeat_confidence=0.45,
    )
    assert "uncertain" not in result.lower()


def test_format_analysis_prompt_omits_downbeat_block_for_kizomba():
    """Kizomba prompts keep beat-position anchoring out of scope.

    Phase 37a-bis: a live Filomena listening_guide echoed the low-confidence
    downbeat uncertainty note despite the output guard. Suppressing the analysis
    block for kizomba removes the conflicting prompt context at the source.
    """
    import numpy as np

    result = format_analysis_prompt(
        duration=10.0,
        tempo=92.0,
        n_beats=20,
        n_onsets=20,
        beat_times=[0.0, 0.5],
        ioi_ms=[500.0],
        question="Q?",
        downbeat_times=np.array([0.0, 2.0]),
        downbeat_confidence=0.03,
        dance_style="kizomba",
    )
    text = result.lower()
    assert "dance style (user-specified): kizomba" in text
    assert "likely downbeat" not in text
    assert "downbeat estimate" not in text
    assert "downbeat position" not in text
    assert "\"1\"" not in result


# ---------------------------------------------------------------------------
# format_analysis_prompt — style-aware tests
# ---------------------------------------------------------------------------


def test_format_analysis_prompt_with_dance_style_fills_placeholder():
    """When dance_style is provided, {style} placeholders in the question are filled."""
    result = format_analysis_prompt(
        duration=10.0,
        tempo=125.0,
        n_beats=20,
        n_onsets=20,
        beat_times=[0.0, 0.5],
        ioi_ms=[500.0],
        question="How does this fit {style}?",
        dance_style="bachata",
    )
    assert "bachata" in result
    assert "{style}" not in result


def test_format_analysis_prompt_with_style_context():
    """Style context block should appear in the prompt."""
    result = format_analysis_prompt(
        duration=10.0,
        tempo=100.0,
        n_beats=20,
        n_onsets=20,
        beat_times=[0.0, 0.5],
        ioi_ms=[500.0],
        question="Q?",
        dance_style="kizomba",
        style_context="Kizomba is a close-embrace dance.",
    )
    assert "kizomba" in result.lower()
    assert "close-embrace" in result


def test_format_analysis_prompt_no_style_no_placeholders():
    """Without dance_style, the prompt should not contain unfilled {style} markers."""
    result = format_analysis_prompt(
        duration=10.0,
        tempo=120.0,
        n_beats=20,
        n_onsets=20,
        beat_times=[0.0, 0.5],
        ioi_ms=[500.0],
        question=QUESTION_COUNTING,
    )
    assert "{style}" not in result
    assert "{" not in result


def test_format_analysis_prompt_no_downbeat_args_still_clean():
    """Callers that omit downbeat args should get a clean prompt with no gaps."""
    result = format_analysis_prompt(
        duration=10.0,
        tempo=120.0,
        n_beats=20,
        n_onsets=20,
        beat_times=[0.0, 0.5],
        ioi_ms=[500.0],
        question="Q?",
    )
    assert "{" not in result
    assert "}" not in result
    # No downbeat lines should appear
    assert "downbeat" not in result.lower()


def test_format_analysis_prompt_with_vocals_contains_language():
    """Passing a VocalsInfo should inject the language into the prompt text."""
    from rytmi.types import VocalsInfo

    vocals = VocalsInfo(
        language="portuguese",
        lyric_snippet="teu toque me faz sonhar",
        clip_start_s=45.0,
        clip_duration_s=20.0,
        raw_response="Portuguese\nteu toque me faz sonhar",
    )
    result = format_analysis_prompt(
        duration=240.0,
        tempo=96.0,
        n_beats=384,
        n_onsets=700,
        beat_times=[0.0, 0.6, 1.2],
        ioi_ms=[600, 600],
        question="Q?",
        vocals=vocals,
    )
    assert "{" not in result
    assert "}" not in result
    assert "portuguese" in result.lower()
    assert "teu toque" in result.lower()


def test_format_analysis_prompt_no_vocals_byte_identical_to_baseline():
    """Regression guard: passing vocals=None must not change the cloud-path prompt.

    The whole point of the perception stage is to be additive — the existing
    Ollama reasoning calls (which never see audio) must produce byte-identical
    prompts to the pre-feature version when transcription is disabled.
    """
    kwargs = dict(
        duration=180.0,
        tempo=128.0,
        n_beats=384,
        n_onsets=600,
        beat_times=[0.0, 0.5, 1.0, 1.5],
        ioi_ms=[500, 500, 500],
        question="Q?",
        downbeat_times=[0.5, 2.5, 4.5],
        downbeat_confidence=0.42,
    )
    with_none = format_analysis_prompt(vocals=None, **kwargs)
    without = format_analysis_prompt(**kwargs)
    assert with_none == without


def test_explain_rhythm_forwards_vocals_to_prompt(monkeypatch, synthetic_click_audio):
    """explain_rhythm() should forward vocals → format_analysis_prompt → prompt text."""
    from rytmi.dsp import analyze
    from rytmi.llm import explain_rhythm
    from rytmi.types import VocalsInfo

    analysis = analyze(synthetic_click_audio)

    captured = {}

    def fake_generate(processor, model, prompt, **kwargs):
        captured["prompt"] = prompt
        return "mocked"

    monkeypatch.setattr("rytmi.llm.generate", fake_generate)

    vocals = VocalsInfo(language="spanish", lyric_snippet="")
    explain_rhythm(
        analysis,
        question="Q?",
        processor=object(),
        model=object(),
        vocals=vocals,
    )
    assert "spanish" in captured["prompt"].lower()


def test_explain_all_verifies_kizomba_drills(monkeypatch):
    """Phase 37c — explain_all should clean invalid kizomba drill ranges."""
    from rytmi.llm import explain_all
    from rytmi.prompts import ALL_QUESTIONS
    from rytmi.types import RhythmFeatures, SongPhase

    rhythm_features = RhythmFeatures(
        onsets_per_beat=2.0,
        beat_strength_pattern=[1.0, 0.5, 0.7, 0.3],
        percussiveness=0.45,
        spectral_centroid_mean=2000.0,
        tempo_stability=0.05,
        ioi_median_ms=250.0,
        ioi_std_ms=40.0,
        beat_clarity=0.45,
    )
    phases = [
        SongPhase("main", 159.0, 195.0, 1, ["medium"], rhythm_features),
        SongPhase("outro", 195.0, 209.0, 1, ["low"], rhythm_features),
    ]
    analysis = types.SimpleNamespace(sections=[], phases=phases, dance_style="kizomba")
    raw_drills = (
        "P1-P2: main (159s-195s, beat: clear) — "
        "Drill: add subtle styling. 36s.\n"
        "P2: outro (195s-209s, beat: clear) — Drill: slow the pace. 14s."
    )

    def fake_explain_rhythm(analysis_arg, question, **kwargs):
        if question == ALL_QUESTIONS["kizomba_drills"]:
            return raw_drills
        return "mocked"

    monkeypatch.setattr("rytmi.llm.explain_rhythm", fake_explain_rhythm)

    results = explain_all(analysis, processor=object(), model=object())

    assert results["kizomba_drills_raw"] == raw_drills
    assert "P1-P2: main" not in results["kizomba_drills"]
    assert "P1: main (159s-195s, beat: clear)" in results["kizomba_drills"]
    assert results["kizomba_drills"].count("P2:") == 1
    assert "repaired_ranges=1" in results["kizomba_drills_verified_stats"]


def test_explain_all_verifies_bachata_drills(monkeypatch):
    """Phase 39 — explain_all should clean invalid bachata drill ranges
    via the same structural verifier used for kizomba.
    """
    from rytmi.llm import explain_all
    from rytmi.prompts import ALL_QUESTIONS
    from rytmi.types import RhythmFeatures, SongPhase

    rhythm_features = RhythmFeatures(
        onsets_per_beat=2.0,
        beat_strength_pattern=[1.0, 0.5, 0.7, 0.3],
        percussiveness=0.55,
        spectral_centroid_mean=2200.0,
        tempo_stability=0.05,
        ioi_median_ms=235.0,
        ioi_std_ms=35.0,
        beat_clarity=0.55,
    )
    phases = [
        SongPhase("main", 12.0, 80.0, 1, ["medium"], rhythm_features),
        SongPhase("main", 80.0, 148.0, 1, ["medium"], rhythm_features),
        SongPhase("outro", 148.0, 165.0, 1, ["low"], rhythm_features),
    ]
    analysis = types.SimpleNamespace(sections=[], phases=phases, dance_style="bachata")
    raw_drills = (
        "P1-P3: main (12s-148s, beat: clear) — "
        "Drill: loop the 1-2-3-tap, 5-6-7-tap basic. 30s loop.\n"
        "P3: outro (148s-165s, beat: clear) — "
        "Drill: slow the basic, finish on a clean 8. 17s."
    )

    def fake_explain_rhythm(analysis_arg, question, **kwargs):
        if question == ALL_QUESTIONS["bachata_drills"]:
            return raw_drills
        return "mocked"

    monkeypatch.setattr("rytmi.llm.explain_rhythm", fake_explain_rhythm)

    results = explain_all(analysis, processor=object(), model=object())

    assert results["bachata_drills_raw"] == raw_drills
    # crossed `P1-P3: main` shrinks to `P1-P2: main`; outro renumbers to P3
    assert "P1-P3: main" not in results["bachata_drills"]
    assert "P1-P2: main (12s-148s, beat: clear)" in results["bachata_drills"]
    assert "P3: outro (148s-165s, beat: clear)" in results["bachata_drills"]
    assert results["bachata_drills"].count("P3:") == 1
    assert "repaired_ranges=1" in results["bachata_drills_verified_stats"]
    # kizomba_drills should NOT be verified (no kizomba_drills_raw key)
    assert "kizomba_drills_raw" not in results


def test_explain_all_verifies_kizomba_transitions(monkeypatch):
    """Phase 40 — explain_all should clean invented kizomba transitions
    via verify_kizomba_transitions_output and fill missing ones.
    """
    from rytmi.llm import explain_all
    from rytmi.prompts import ALL_QUESTIONS
    from rytmi.types import RhythmFeatures, SongPhase

    rhythm_features = RhythmFeatures(
        onsets_per_beat=2.0,
        beat_strength_pattern=[1.0, 0.5, 0.7, 0.3],
        percussiveness=0.45,
        spectral_centroid_mean=2000.0,
        tempo_stability=0.05,
        ioi_median_ms=250.0,
        ioi_std_ms=40.0,
        beat_clarity=0.45,
    )
    # intro → main → break → main → outro arc, 4 real transitions
    phases = [
        SongPhase("intro", 0.0, 12.0, 1, ["low"], rhythm_features),
        SongPhase("main", 12.0, 148.0, 1, ["medium"], rhythm_features),
        SongPhase("break", 148.0, 159.0, 1, ["low"], rhythm_features),
        SongPhase("main", 159.0, 195.0, 1, ["medium"], rhythm_features),
        SongPhase("outro", 195.0, 209.0, 1, ["low"], rhythm_features),
    ]
    analysis = types.SimpleNamespace(sections=[], phases=phases, dance_style="kizomba")
    # Output has one invented transition (T2 at 90s) and skips the
    # break → main re-entry (159s) so the verifier needs to drop and fill.
    raw_transitions = (
        "T1: 12s [intro → main, beat: clear → clear] — "
        "Settle into the pulse and walk-step on the first clear bass hit.\n"
        "T2: 90s [main → main, beat: clear → clear] — "
        "Invented mid-main boundary that does not exist.\n"
        "T3: 148s [main → break, beat: clear → clear] — "
        "Soften the basic and reduce travel; keep a small pulse in the body.\n"
        "T4: 195s [main → outro, beat: clear → clear] — "
        "Energy is winding down; contract movement and slow the basic."
    )

    def fake_explain_rhythm(analysis_arg, question, **kwargs):
        if question == ALL_QUESTIONS["kizomba_transitions"]:
            return raw_transitions
        return "mocked"

    monkeypatch.setattr("rytmi.llm.explain_rhythm", fake_explain_rhythm)

    results = explain_all(analysis, processor=object(), model=object())

    assert results["kizomba_transitions_raw"] == raw_transitions
    # Invented mid-main boundary dropped
    assert "Invented mid-main boundary" not in results["kizomba_transitions"]
    # Missing break → main re-entry filled with template text
    assert "break → main" in results["kizomba_transitions"]
    assert "first clear bass hit" in results["kizomba_transitions"]
    # All 4 real transitions covered, renumbered T1..T4 chronologically
    cleaned_lines = results["kizomba_transitions"].splitlines()
    assert len(cleaned_lines) == 4
    assert cleaned_lines[0].startswith("T1: 12s")
    assert cleaned_lines[1].startswith("T2: 148s")
    assert cleaned_lines[2].startswith("T3: 159s")
    assert cleaned_lines[3].startswith("T4: 195s")
    # Verifier stats reflect the repair pattern
    stats = results["kizomba_transitions_verified_stats"]
    assert "boundaries_matched=3" in stats
    assert "boundaries_invented=1" in stats
    assert "boundaries_missing_filled=1" in stats
    assert "output_lines=4" in stats


def test_explain_rhythm_prompt_contains_downbeat_data(monkeypatch, synthetic_click_audio):
    """explain_rhythm() should include downbeat confidence in the prompt."""
    from rytmi.dsp import analyze
    from rytmi.llm import explain_rhythm

    analysis = analyze(synthetic_click_audio)
    captured = {}

    def fake_generate(processor, model, prompt, **kwargs):
        captured["prompt"] = prompt
        return "ok"

    monkeypatch.setattr("rytmi.llm.generate", fake_generate)
    explain_rhythm(analysis, question="Q?", processor=object(), model=object())

    prompt = captured["prompt"]
    # analyze() always sets downbeat_confidence now, so the section should appear
    assert "downbeat" in prompt.lower()
    assert "confidence" in prompt.lower()


# ---------------------------------------------------------------------------
# llm.py tests — mock the model to avoid GPU dependency
# ---------------------------------------------------------------------------

def test_generate_with_mock(monkeypatch, synthetic_click_audio):
    """generate() should return the decoded string from the model."""
    import rytmi.llm as llm_module

    class FakeProcessor:
        def apply_chat_template(self, *args, **kwargs):
            import torch
            return {"input_ids": torch.zeros((1, 10), dtype=torch.long)}

        def decode(self, tokens, skip_special_tokens=True):
            return "  This is 4/4 at 120 BPM.  "

    class FakeModel:
        device = "cpu"

        def generate(self, **kwargs):
            import torch
            return torch.zeros((1, 15), dtype=torch.long)

    result = llm_module.generate(FakeProcessor(), FakeModel(), "test prompt")
    assert result == "This is 4/4 at 120 BPM."


def test_explain_rhythm_with_mock(monkeypatch, synthetic_click_audio):
    """explain_rhythm() should format a prompt and return model output."""
    from rytmi.dsp import analyze
    from rytmi.llm import explain_rhythm

    analysis = analyze(synthetic_click_audio)

    def fake_generate(processor, model, prompt, **kwargs):
        assert "BPM" in prompt
        return "Mocked explanation."

    monkeypatch.setattr("rytmi.llm.generate", fake_generate)

    result = explain_rhythm(
        analysis,
        question="What time signature?",
        processor=object(),
        model=object(),
    )
    assert result == "Mocked explanation."


def test_explain_rhythm_prompt_contains_analysis_data(monkeypatch, synthetic_click_audio):
    """The prompt passed to generate() should embed the DSP analysis data."""
    from rytmi.dsp import analyze
    from rytmi.llm import explain_rhythm

    analysis = analyze(synthetic_click_audio)
    captured = {}

    def fake_generate(processor, model, prompt, **kwargs):
        captured["prompt"] = prompt
        return "ok"

    monkeypatch.setattr("rytmi.llm.generate", fake_generate)
    explain_rhythm(analysis, question="Q?", processor=object(), model=object())

    prompt = captured["prompt"]
    assert str(int(analysis.tempo)) in prompt or str(round(analysis.tempo)) in prompt
    assert str(len(analysis.beats.times)) in prompt
    assert "Q?" in prompt


def test_load_model_falls_back_to_tokenizer_on_torchvision_error(monkeypatch):
    """load_model() should use AutoTokenizer when AutoProcessor needs torchvision."""
    import rytmi.llm as llm_module

    class FakeAutoProcessor:
        @staticmethod
        def from_pretrained(_model_id):
            raise ImportError("Gemma4VideoProcessor requires the Torchvision library")

    class FakeAutoTokenizer:
        @staticmethod
        def from_pretrained(_model_id):
            return "fake-tokenizer"

    class FakeBitsAndBytesConfig:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    class FakeModel:
        eval_called = False

        def eval(self):
            self.eval_called = True

    class FakeAutoModelForCausalLM:
        @staticmethod
        def from_pretrained(_model_id, **_kwargs):
            return FakeModel()

    fake_transformers = types.ModuleType("transformers")
    fake_transformers.AutoProcessor = FakeAutoProcessor
    fake_transformers.AutoTokenizer = FakeAutoTokenizer
    fake_transformers.AutoModelForCausalLM = FakeAutoModelForCausalLM
    fake_transformers.BitsAndBytesConfig = FakeBitsAndBytesConfig

    monkeypatch.setitem(sys.modules, "transformers", fake_transformers)

    processor, model = llm_module.load_model(
        model_id="google/gemma-4-E2B-it",
        profile="laptop",
        quantize=False,
        device_map="cpu",
    )

    assert processor == "fake-tokenizer"
    assert model.eval_called is True


def test_load_model_reraises_non_torchvision_processor_error(monkeypatch):
    """load_model() should not hide unrelated AutoProcessor import failures."""
    import rytmi.llm as llm_module

    class FakeAutoProcessor:
        @staticmethod
        def from_pretrained(_model_id):
            raise ImportError("unexpected processor import issue")

    class FakeAutoTokenizer:
        @staticmethod
        def from_pretrained(_model_id):
            raise AssertionError("Tokenizer fallback should not run")

    class FakeBitsAndBytesConfig:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    class FakeAutoModelForCausalLM:
        @staticmethod
        def from_pretrained(_model_id, **_kwargs):
            class FakeModel:
                def eval(self):
                    return None

            return FakeModel()

    fake_transformers = types.ModuleType("transformers")
    fake_transformers.AutoProcessor = FakeAutoProcessor
    fake_transformers.AutoTokenizer = FakeAutoTokenizer
    fake_transformers.AutoModelForCausalLM = FakeAutoModelForCausalLM
    fake_transformers.BitsAndBytesConfig = FakeBitsAndBytesConfig

    monkeypatch.setitem(sys.modules, "transformers", fake_transformers)

    with pytest.raises(ImportError, match="unexpected processor import issue"):
        llm_module.load_model(
            model_id="google/gemma-4-E2B-it",
            profile="laptop",
            quantize=False,
            device_map="cpu",
        )


def _make_fake_transformers(processor_value="fake-processor", model_fail_until=0):
    """Build a fake transformers module for load_model tests.

    Args:
        processor_value: What AutoProcessor.from_pretrained returns.
        model_fail_until: How many from_pretrained calls should fail before succeeding.
            When > 0, the first ``model_fail_until`` calls raise ValueError with
            the VRAM dispatch message.
    """

    class FakeAutoProcessor:
        @staticmethod
        def from_pretrained(_model_id):
            return processor_value

    class FakeAutoTokenizer:
        @staticmethod
        def from_pretrained(_model_id):
            return "fake-tokenizer"

    class FakeBitsAndBytesConfig:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    class FakeModel:
        eval_called = False

        def eval(self):
            self.eval_called = True

    calls = []

    class FakeAutoModelForCausalLM:
        @staticmethod
        def from_pretrained(_model_id, **kwargs):
            calls.append(kwargs)
            if len(calls) <= model_fail_until:
                raise ValueError(
                    "Some modules are dispatched on the CPU or the disk. "
                    "Set llm_int8_enable_fp32_cpu_offload=True and pass a custom device_map."
                )
            return FakeModel()

    mod = types.ModuleType("transformers")
    mod.AutoProcessor = FakeAutoProcessor
    mod.AutoTokenizer = FakeAutoTokenizer
    mod.AutoModelForCausalLM = FakeAutoModelForCausalLM
    mod.BitsAndBytesConfig = FakeBitsAndBytesConfig
    return mod, calls, FakeModel


def test_load_model_falls_back_to_cpu_on_vram_dispatch_error(monkeypatch):
    """If quantized GPU load fails with dispatch error, fall back to CPU bf16."""
    import torch
    import rytmi.llm as llm_module

    fake_transformers, calls, FakeModel = _make_fake_transformers(model_fail_until=1)
    monkeypatch.setitem(sys.modules, "transformers", fake_transformers)

    processor, model = llm_module.load_model(
        model_id="google/gemma-4-E2B-it",
        profile="laptop",
        quantize=True,
        device_map="auto",
    )

    assert processor == "fake-processor"
    assert model.eval_called is True
    assert len(calls) == 2
    # First call: quantized GPU attempt
    assert calls[0]["device_map"] == "auto"
    assert "quantization_config" in calls[0]
    # Second call: CPU bf16 fallback
    assert calls[1]["device_map"] == "cpu"
    assert calls[1]["torch_dtype"] is torch.bfloat16


def test_load_model_falls_back_to_cpu_on_type_error(monkeypatch):
    """TypeError from accelerate/bnb compat issues should also trigger CPU fallback."""
    import torch
    import rytmi.llm as llm_module

    class FakeAutoProcessor:
        @staticmethod
        def from_pretrained(_model_id):
            return "fake-processor"

    class FakeAutoTokenizer:
        @staticmethod
        def from_pretrained(_model_id):
            return "fake-tokenizer"

    class FakeBitsAndBytesConfig:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    class FakeModel:
        eval_called = False

        def eval(self):
            self.eval_called = True

    calls = []

    class FakeAutoModelForCausalLM:
        @staticmethod
        def from_pretrained(_model_id, **kwargs):
            calls.append(kwargs)
            if len(calls) == 1:
                raise TypeError(
                    "Params4bit.__new__() got an unexpected keyword argument '_is_hf_initialized'"
                )
            return FakeModel()

    mod = types.ModuleType("transformers")
    mod.AutoProcessor = FakeAutoProcessor
    mod.AutoTokenizer = FakeAutoTokenizer
    mod.AutoModelForCausalLM = FakeAutoModelForCausalLM
    mod.BitsAndBytesConfig = FakeBitsAndBytesConfig
    monkeypatch.setitem(sys.modules, "transformers", mod)

    processor, model = llm_module.load_model(
        model_id="google/gemma-4-E2B-it",
        profile="laptop",
        quantize=True,
        device_map="auto",
    )

    assert processor == "fake-processor"
    assert model.eval_called is True
    assert len(calls) == 2
    assert calls[1]["device_map"] == "cpu"
    assert calls[1]["torch_dtype"] is torch.bfloat16


def test_generate_uses_hf_device_map_when_model_has_no_device_attr():
    """generate() should place tensors on a valid device from hf_device_map."""
    import rytmi.llm as llm_module

    class FakeProcessor:
        def apply_chat_template(self, *args, **kwargs):
            import torch

            return {"input_ids": torch.zeros((1, 4), dtype=torch.long)}

        def decode(self, tokens, skip_special_tokens=True):
            return "ok"

    class FakeModel:
        hf_device_map = {"": "cpu"}

        def generate(self, **kwargs):
            import torch

            return torch.zeros((1, 6), dtype=torch.long)

    result = llm_module.generate(FakeProcessor(), FakeModel(), "test prompt")
    assert result == "ok"


# ---------------------------------------------------------------------------
# Cloud backend tests
# ---------------------------------------------------------------------------

def test_load_cloud_model_returns_client_and_model_id():
    """load_cloud_model() should return (OpenAI client, model_id string)."""
    from unittest.mock import patch

    from rytmi.llm import load_cloud_model

    with patch("openai.OpenAI") as MockOpenAI:
        MockOpenAI.return_value = "fake-client"
        client, model_id = load_cloud_model(
            model_id="my-model",
            base_url="http://localhost:8000/v1",
            api_key="test-key",
        )

    assert client == "fake-client"
    assert model_id == "my-model"
    MockOpenAI.assert_called_once_with(base_url="http://localhost:8000/v1", api_key="test-key")


def test_load_cloud_model_reads_env_vars(monkeypatch):
    """load_cloud_model() should fall back to RYTMI_API_BASE_URL and RYTMI_API_KEY."""
    from unittest.mock import patch

    from rytmi.llm import load_cloud_model

    monkeypatch.setenv("RYTMI_API_BASE_URL", "http://env-server/v1")
    monkeypatch.setenv("RYTMI_API_KEY", "env-key")

    with patch("openai.OpenAI") as MockOpenAI:
        MockOpenAI.return_value = "fake-client"
        client, model_id = load_cloud_model()

    MockOpenAI.assert_called_once_with(base_url="http://env-server/v1", api_key="env-key")
    assert model_id == "google/gemma-4-E2B-it"  # default


def test_load_cloud_model_raises_without_base_url(monkeypatch):
    """load_cloud_model() should raise ValueError if no base_url is available."""
    from rytmi.llm import load_cloud_model

    monkeypatch.delenv("RYTMI_API_BASE_URL", raising=False)

    with pytest.raises(ValueError, match="RYTMI_API_BASE_URL"):
        load_cloud_model()


def test_generate_dispatches_to_cloud_for_string_model():
    """generate() should call _generate_cloud when model is a string."""
    from unittest.mock import MagicMock

    from rytmi.llm import generate

    fake_client = MagicMock()
    fake_response = MagicMock()
    fake_response.choices = [MagicMock()]
    fake_response.choices[0].message.content = "  Cloud says hello.  "
    fake_client.chat.completions.create.return_value = fake_response

    result = generate(fake_client, "my-model", "test prompt")

    assert result == "Cloud says hello."
    fake_client.chat.completions.create.assert_called_once()
    call_kwargs = fake_client.chat.completions.create.call_args[1]
    assert call_kwargs["model"] == "my-model"
    assert any(m["role"] == "user" and "test prompt" in m["content"]
               for m in call_kwargs["messages"])


def test_format_rhythm_features_section_none():
    """rhythm_features=None → empty string (backwards compatible)."""
    from rytmi.prompts import _format_rhythm_features_section

    assert _format_rhythm_features_section(None) == ""


def test_format_rhythm_features_section_renders():
    """Verify key labels appear in the rendered section."""
    from rytmi.prompts import _format_rhythm_features_section
    from rytmi.types import RhythmFeatures

    features = RhythmFeatures(
        onsets_per_beat=2.3,
        beat_strength_pattern=[1.0, 0.61, 0.72, 0.89],
        percussiveness=0.72,
        spectral_centroid_mean=2100.0,
        tempo_stability=0.04,
        ioi_median_ms=210.0,
        ioi_std_ms=85.0,
    )
    result = _format_rhythm_features_section(features)
    assert "2.3 onsets/beat" in result
    assert "moderate" in result
    assert "0.72" in result
    assert "high" in result
    assert "2100 Hz" in result
    assert "very steady" in result
    assert "median 210ms" in result


def test_format_rhythm_features_section_with_half_time():
    """Half-time note should appear when tempo_half is provided."""
    from rytmi.prompts import _format_rhythm_features_section
    from rytmi.types import RhythmFeatures

    features = RhythmFeatures(
        onsets_per_beat=1.0,
        beat_strength_pattern=[1.0, 0.5],
        percussiveness=0.3,
        spectral_centroid_mean=1500.0,
        tempo_stability=0.05,
        ioi_median_ms=400.0,
        ioi_std_ms=50.0,
    )
    result = _format_rhythm_features_section(features, tempo_half=72.0)
    assert "half-time tempo: 72 BPM" in result


def test_format_analysis_prompt_with_features():
    """Full prompt should include rhythm features section."""
    from rytmi.types import RhythmFeatures

    features = RhythmFeatures(
        onsets_per_beat=1.8,
        beat_strength_pattern=[1.0, 0.5, 0.7, 0.6],
        percussiveness=0.45,
        spectral_centroid_mean=1800.0,
        tempo_stability=0.03,
        ioi_median_ms=300.0,
        ioi_std_ms=60.0,
    )
    result = format_analysis_prompt(
        duration=60.0,
        tempo=125.0,
        n_beats=125,
        n_onsets=225,
        beat_times=[0.0, 0.5, 1.0],
        ioi_ms=[500, 500],
        question="Q?",
        rhythm_features=features,
    )
    assert "{" not in result
    assert "}" not in result
    assert "1.8 onsets/beat" in result
    assert "Percussiveness" in result


def test_format_analysis_prompt_no_features_backwards_compatible():
    """Omitting rhythm_features should not change the prompt vs explicit None."""
    kwargs = dict(
        duration=60.0,
        tempo=120.0,
        n_beats=120,
        n_onsets=200,
        beat_times=[0.0, 0.5],
        ioi_ms=[500],
        question="Q?",
    )
    without = format_analysis_prompt(**kwargs)
    with_none = format_analysis_prompt(rhythm_features=None, **kwargs)
    assert without == with_none


def test_explain_rhythm_forwards_rhythm_features(monkeypatch, synthetic_click_audio):
    """explain_rhythm() should include rhythm features from analysis in the prompt."""
    from rytmi.dsp import analyze
    from rytmi.llm import explain_rhythm

    analysis = analyze(synthetic_click_audio)
    captured = {}

    def fake_generate(processor, model, prompt, **kwargs):
        captured["prompt"] = prompt
        return "ok"

    monkeypatch.setattr("rytmi.llm.generate", fake_generate)
    explain_rhythm(analysis, question="Q?", processor=object(), model=object())

    prompt = captured["prompt"]
    assert "onsets/beat" in prompt
    assert "Percussiveness" in prompt


def test_explain_rhythm_works_with_cloud_backend(monkeypatch, synthetic_click_audio):
    """explain_rhythm() should work identically with cloud (processor, model) tuple."""
    from rytmi.dsp import analyze
    from rytmi.llm import explain_rhythm

    analysis = analyze(synthetic_click_audio)

    def fake_generate(processor, model, prompt, **kwargs):
        assert isinstance(model, str)
        assert "BPM" in prompt
        return "Cloud explanation."

    monkeypatch.setattr("rytmi.llm.generate", fake_generate)

    result = explain_rhythm(
        analysis,
        question="What time signature?",
        processor=object(),  # stands in for an OpenAI client
        model="my-model",    # string triggers cloud path
    )
    assert result == "Cloud explanation."


# ---------------------------------------------------------------------------
# STYLE→DANCER chaining tests
# ---------------------------------------------------------------------------

def test_explain_all_iterates_all_questions(monkeypatch, synthetic_click_audio):
    """explain_all() should call generate once per ALL_QUESTIONS entry."""
    from rytmi.dsp import analyze
    from rytmi.llm import explain_all

    analysis = analyze(synthetic_click_audio)
    call_count = [0]

    def fake_generate(processor, model, prompt, **kwargs):
        call_count[0] += 1
        return f"Answer {call_count[0]}."

    monkeypatch.setattr("rytmi.llm.generate", fake_generate)

    results = explain_all(
        analysis, processor=object(), model=object(), verify_sections=False,
    )

    assert len(results) == len(ALL_QUESTIONS)
    assert call_count[0] == len(ALL_QUESTIONS)


def test_explain_all_runs_sections_verifier_by_default(monkeypatch, synthetic_click_audio):
    """sections answer is post-processed; raw + stats are stashed alongside."""
    from rytmi.dsp import analyze
    from rytmi.llm import explain_all

    analysis = analyze(synthetic_click_audio)

    sections_raw = (
        "P1: 0s-10s, intro — feel the bachata\n"
        "P2: 10s-30s, main — drives at 129 BPM\n"
    )

    def fake_explain_rhythm(_analysis, *, question, **kwargs):
        if "P#" in question:
            return sections_raw
        return "Mocked answer."

    monkeypatch.setattr("rytmi.llm.explain_rhythm", fake_explain_rhythm)

    results = explain_all(analysis, processor=object(), model=object())

    assert "sections" in results
    assert "sections_raw" in results
    assert "sections_verified_stats" in results
    assert results["sections_raw"] == sections_raw
    # First line should have been replaced; second preserved.
    cleaned = results["sections"].splitlines()
    assert "feel the bachata" not in cleaned[0]
    assert "continues the" in cleaned[0]
    assert "129 BPM" in cleaned[1]
    assert "passed=1" in results["sections_verified_stats"]
    assert "failed=1" in results["sections_verified_stats"]


def test_explain_all_with_dance_style(monkeypatch, synthetic_click_audio):
    """explain_all() should pass dance_style through to prompts."""
    from rytmi.dsp import analyze
    from rytmi.llm import explain_all

    analysis = analyze(synthetic_click_audio, dance_style="bachata")
    captured_prompts = []

    def fake_generate(processor, model, prompt, **kwargs):
        captured_prompts.append(prompt)
        return "Mocked."

    monkeypatch.setattr("rytmi.llm.generate", fake_generate)

    explain_all(analysis, processor=object(), model=object())

    # At least one prompt should contain "bachata" (from {style} placeholder filling)
    assert any("bachata" in p.lower() for p in captured_prompts)


# ---------------------------------------------------------------------------
# Empty response retry tests
# ---------------------------------------------------------------------------

def test_empty_response_retry_cloud():
    """Cloud backend should retry once with temperature=0.5 on empty response."""
    from unittest.mock import MagicMock

    from rytmi.llm import generate

    fake_client = MagicMock()
    call_count = [0]

    def create_completion(**kwargs):
        call_count[0] += 1
        resp = MagicMock()
        if call_count[0] == 1:
            resp.choices = [MagicMock()]
            resp.choices[0].message.content = ""
        else:
            resp.choices = [MagicMock()]
            resp.choices[0].message.content = "Retry succeeded."
        return resp

    fake_client.chat.completions.create.side_effect = create_completion

    result = generate(fake_client, "my-model", "test prompt")

    assert result == "Retry succeeded."
    assert call_count[0] == 2
    # Second call should use temperature=0.5
    second_call = fake_client.chat.completions.create.call_args_list[1]
    assert second_call[1]["temperature"] == 0.5


def test_no_retry_when_response_not_empty():
    """Cloud backend should NOT retry when response has content."""
    from unittest.mock import MagicMock

    from rytmi.llm import generate

    fake_client = MagicMock()
    resp = MagicMock()
    resp.choices = [MagicMock()]
    resp.choices[0].message.content = "Good answer."
    fake_client.chat.completions.create.return_value = resp

    result = generate(fake_client, "my-model", "test prompt")

    assert result == "Good answer."
    assert fake_client.chat.completions.create.call_count == 1


# ---------------------------------------------------------------------------
# Half-time prompt rendering tests
# ---------------------------------------------------------------------------

def test_format_rhythm_features_half_time_prominent():
    """Half-time should appear as the FIRST bullet in the features section."""
    from rytmi.prompts import _format_rhythm_features_section
    from rytmi.types import RhythmFeatures

    features = RhythmFeatures(
        onsets_per_beat=1.0,
        beat_strength_pattern=[1.0, 0.5],
        percussiveness=0.3,
        spectral_centroid_mean=1500.0,
        tempo_stability=0.05,
        ioi_median_ms=400.0,
        ioi_std_ms=50.0,
    )
    result = _format_rhythm_features_section(features, tempo_half=72.0)
    lines = [ln for ln in result.strip().split("\n") if ln.startswith("- ")]
    assert "half-time tempo: 72 bpm" in lines[0].lower()
    assert "kizomba/semba" in lines[0].lower()


def test_question_style_fit_has_style_placeholder():
    """QUESTION_STYLE_FIT should contain {style} placeholder for parameterization."""
    from rytmi.prompts import QUESTION_STYLE_FIT

    assert "{style}" in QUESTION_STYLE_FIT


def test_question_dancer_has_style_placeholder():
    """QUESTION_DANCER should contain {style} placeholder for parameterization."""
    from rytmi.prompts import QUESTION_DANCER

    assert "{style}" in QUESTION_DANCER


# ---------------------------------------------------------------------------
# format_analysis_prompt — sections tests
# ---------------------------------------------------------------------------


def test_format_sections_block_empty():
    """Empty or None sections produce an empty string."""
    from rytmi.prompts import _format_sections_block

    assert _format_sections_block(None) == ""
    assert _format_sections_block([]) == ""


def test_format_sections_block_basic():
    """Sections block should list each section with label, timing, and energy."""
    from rytmi.prompts import _format_sections_block
    from rytmi.types import SongSection

    sections = [
        SongSection(start_s=0.0, end_s=10.0, label="intro", energy_level="low"),
        SongSection(start_s=10.0, end_s=30.0, label="main", energy_level="high"),
    ]
    result = _format_sections_block(sections)
    assert "2 segments" in result
    assert "intro" in result
    assert "main" in result
    assert "0.0s" in result
    assert "low energy" in result
    assert "high energy" in result


def test_format_sections_block_with_rhythm_features():
    """Sections with rhythm_features should include onset density and accent info."""
    from rytmi.prompts import _format_sections_block
    from rytmi.types import RhythmFeatures, SongSection

    rf = RhythmFeatures(
        onsets_per_beat=2.5,
        beat_strength_pattern=[1.0, 0.6, 0.7, 0.2],
        percussiveness=0.45,
        spectral_centroid_mean=2000.0,
        tempo_stability=0.03,
        ioi_median_ms=500.0,
        ioi_std_ms=30.0,
    )
    sections = [
        SongSection(
            start_s=0.0, end_s=20.0, label="main",
            energy_level="medium", rhythm_features=rf,
        ),
    ]
    result = _format_sections_block(sections)
    assert "2.5 onsets/beat" in result
    assert "percussiveness" in result
    assert "accent:" in result.lower()


def test_format_sections_block_with_style_profile():
    """When a style profile is provided with phases, coaching hints should appear."""
    from rytmi.prompts import _format_sections_block
    from rytmi.styles import BACHATA_PROFILE
    from rytmi.types import SongPhase, SongSection

    sections = [
        SongSection(start_s=0.0, end_s=8.0, label="intro", energy_level="low"),
        SongSection(start_s=8.0, end_s=30.0, label="main", energy_level="high"),
    ]
    phases = [
        SongPhase(label="intro", start_s=0.0, end_s=8.0, section_count=1,
                  energy_levels=["low"]),
        SongPhase(label="main", start_s=8.0, end_s=30.0, section_count=1,
                  energy_levels=["high"]),
    ]
    result = _format_sections_block(sections, style_profile=BACHATA_PROFILE, phases=phases)
    assert "Coaching hint:" in result
    # Bachata intro coaching mentions "guitar rhythm"
    assert "guitar" in result.lower()


def test_format_analysis_prompt_with_sections():
    """Sections data should appear in the formatted prompt."""
    from rytmi.types import SongSection

    sections = [
        SongSection(start_s=0.0, end_s=5.0, label="intro", energy_level="low"),
        SongSection(start_s=5.0, end_s=10.0, label="main", energy_level="high"),
    ]
    result = format_analysis_prompt(
        duration=10.0,
        tempo=125.0,
        n_beats=20,
        n_onsets=25,
        beat_times=[0.0, 0.5],
        ioi_ms=[500.0],
        question="Q?",
        sections=sections,
    )
    assert "Section detail" in result
    assert "intro" in result
    assert "main" in result
    assert "{" not in result
    assert "}" not in result


def test_format_analysis_prompt_no_sections_unchanged():
    """Omitting sections should produce a prompt identical to the pre-feature version."""
    kwargs = dict(
        duration=10.0,
        tempo=120.0,
        n_beats=20,
        n_onsets=20,
        beat_times=[0.0, 0.5],
        ioi_ms=[500.0],
        question="Q?",
    )
    with_none = format_analysis_prompt(sections=None, **kwargs)
    without = format_analysis_prompt(**kwargs)
    assert with_none == without


def test_question_sections_has_style_placeholder():
    """QUESTION_SECTIONS should contain {style} placeholder."""
    from rytmi.prompts import QUESTION_SECTIONS

    assert "{style}" in QUESTION_SECTIONS


def test_explain_rhythm_forwards_sections_to_prompt(monkeypatch, synthetic_click_audio):
    """explain_rhythm() should include section data in the prompt when sections exist."""
    from rytmi.dsp import analyze
    from rytmi.llm import explain_rhythm

    analysis = analyze(synthetic_click_audio, dance_style="bachata")

    captured = {}

    def fake_generate(processor, model, prompt, **kwargs):
        captured["prompt"] = prompt
        return "mocked"

    monkeypatch.setattr("rytmi.llm.generate", fake_generate)

    explain_rhythm(
        analysis,
        question="Q?",
        processor=object(),
        model=object(),
    )
    prompt = captured["prompt"]
    # analyze() now produces sections, so they should appear in the prompt
    assert "Song sections" in prompt or "Song structure" in prompt or "Section detail" in prompt
    # With bachata style, coaching hints should be present
    assert "Coaching hint:" in prompt


# ---------------------------------------------------------------------------
# Phase display + song_arc + basic_step tests
# ---------------------------------------------------------------------------


def test_format_sections_block_with_phases():
    """When phases are provided, the block should include Phase summary."""
    from rytmi.prompts import _format_sections_block
    from rytmi.types import SongPhase, SongSection

    sections = [
        SongSection(start_s=0.0, end_s=10.0, label="main", energy_level="medium"),
        SongSection(start_s=10.0, end_s=20.0, label="main", energy_level="high"),
        SongSection(start_s=20.0, end_s=30.0, label="break", energy_level="low"),
    ]
    phases = [
        SongPhase(label="main", start_s=0.0, end_s=20.0, section_count=2,
                  energy_levels=["medium", "high"]),
        SongPhase(label="break", start_s=20.0, end_s=30.0, section_count=1,
                  energy_levels=["low"]),
    ]
    result = _format_sections_block(sections, phases=phases)
    assert "2 phases" in result
    assert "Phase 1:" in result
    assert "main ×2" in result
    assert "Phase 2:" in result
    assert "break" in result
    # Also has per-section detail
    assert "Section detail" in result or "3 segments" in result


def test_format_sections_block_phases_with_style():
    """Phase coaching hints should appear when a style profile is provided."""
    from rytmi.prompts import _format_sections_block
    from rytmi.styles import BACHATA_PROFILE
    from rytmi.types import SongPhase, SongSection

    sections = [
        SongSection(start_s=0.0, end_s=8.0, label="intro", energy_level="low"),
    ]
    phases = [
        SongPhase(label="intro", start_s=0.0, end_s=8.0, section_count=1,
                  energy_levels=["low"]),
    ]
    result = _format_sections_block(sections, style_profile=BACHATA_PROFILE, phases=phases)
    assert "Coaching hint:" in result
    assert "guitar" in result.lower()


def test_question_song_arc_has_style_placeholder():
    """QUESTION_SONG_ARC should contain {style} placeholder."""
    from rytmi.prompts import QUESTION_SONG_ARC

    assert "{style}" in QUESTION_SONG_ARC


def test_basic_step_in_style_section():
    """basic_step should appear as an IMPORTANT rule in the style section."""
    from rytmi.prompts import _format_style_section

    result = _format_style_section(
        dance_style="bachata",
        style_context="Some context",
        basic_step="The bachata basic is ALWAYS step-step-step-tap.",
    )
    assert "IMPORTANT basic step rule:" in result
    assert "step-step-step-tap" in result


def test_basic_step_omitted_when_none():
    """No IMPORTANT rule line when basic_step is None."""
    from rytmi.prompts import _format_style_section

    result = _format_style_section(
        dance_style="bachata",
        style_context="Some context",
        basic_step=None,
    )
    assert "IMPORTANT basic step rule" not in result


def test_format_analysis_prompt_no_phases_backward_compat():
    """Omitting phases should produce the same prompt as explicit None."""
    from rytmi.types import SongSection

    sections = [
        SongSection(start_s=0.0, end_s=10.0, label="main", energy_level="high"),
    ]
    kwargs = dict(
        duration=10.0,
        tempo=120.0,
        n_beats=20,
        n_onsets=20,
        beat_times=[0.0, 0.5],
        ioi_ms=[500.0],
        question="Q?",
        sections=sections,
    )
    without = format_analysis_prompt(**kwargs)
    with_none = format_analysis_prompt(phases=None, **kwargs)
    assert without == with_none


def test_explain_rhythm_forwards_phases_to_prompt(monkeypatch, synthetic_click_audio):
    """explain_rhythm() should include phase data in the prompt."""
    from rytmi.dsp import analyze
    from rytmi.llm import explain_rhythm

    analysis = analyze(synthetic_click_audio, dance_style="bachata")

    captured = {}

    def fake_generate(processor, model, prompt, **kwargs):
        captured["prompt"] = prompt
        return "mocked"

    monkeypatch.setattr("rytmi.llm.generate", fake_generate)

    explain_rhythm(analysis, question="Q?", processor=object(), model=object())
    prompt = captured["prompt"]
    # analyze() now produces phases, so phase structure should appear
    assert "Phase" in prompt or "phase" in prompt


def test_explain_rhythm_forwards_basic_step_to_prompt(monkeypatch, synthetic_click_audio):
    """explain_rhythm() should include IMPORTANT basic step rule for bachata."""
    from rytmi.dsp import analyze
    from rytmi.llm import explain_rhythm

    analysis = analyze(synthetic_click_audio, dance_style="bachata")

    captured = {}

    def fake_generate(processor, model, prompt, **kwargs):
        captured["prompt"] = prompt
        return "mocked"

    monkeypatch.setattr("rytmi.llm.generate", fake_generate)

    explain_rhythm(analysis, question="Q?", processor=object(), model=object())
    prompt = captured["prompt"]
    assert "IMPORTANT basic step rule:" in prompt
    assert "step-step-step-tap" in prompt


