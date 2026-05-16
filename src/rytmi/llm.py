"""Gemma model loading, text generation, and rhythm explanation.

Supports two backends:
- **local**: Load a HuggingFace model with transformers (GPU or CPU).
  Use ``load_model()`` — requires ``pip install rytmi[llm]``.
- **cloud**: Call any OpenAI-compatible API endpoint.
  Use ``load_cloud_model()`` — requires ``pip install rytmi[cloud]``.

Both return a ``(processor, model)`` tuple that plugs into ``generate()``,
``explain_rhythm()``, and ``explain_all()`` without any other code changes.
"""

from __future__ import annotations

import os

from rytmi.dsp import extract_transitions
from rytmi.prompts import (
    ALL_QUESTIONS,
    DEFAULT_SYSTEM_PROMPT,
    KIZOMBA_TUTOR_POLISH_SYSTEM,
    QUESTION_COUNTING,
    build_kizomba_tutor_polish_prompt,
    format_analysis_prompt,
    verify_kizomba_drills_output,
    verify_kizomba_transitions_output,
    verify_sections_output,
)
from rytmi.styles import get_style_profile
from rytmi.types import RhythmAnalysis

# Set to True (or `import rytmi.llm as llm; llm.CLOUD_DEBUG = True`) to print
# every prompt and raw response sent to the cloud endpoint.  Useful for
# diagnosing empty-response issues without touching call sites.
CLOUD_DEBUG: bool = False

# Model IDs indexed by profile name (HuggingFace IDs for local loading)
MODEL_IDS = {
    "laptop": "google/gemma-4-E2B-it",   # 5.1B params; 4-bit ~2.5 GB VRAM
    "kaggle": "google/gemma-4-E4B-it",   # 8B params; bf16 ~16 GB VRAM
}

# Ollama model names for cloud/local API usage
OLLAMA_IDS = {
    "e2b": "gemma4:e2b",   # ~2.4 GB VRAM as Q4
    "e4b": "gemma4:e4b",   # ~5 GB VRAM as Q4
}


def _is_kaggle() -> bool:
    return os.path.exists("/kaggle") or os.environ.get("KAGGLE_KERNEL_RUN_TYPE") is not None


def _is_low_vram_dispatch_error(exc: Exception) -> bool:
    """Return True for known quantized load failures that suggest CPU/disk offload."""
    msg = str(exc).lower()
    return (
        "dispatched on the cpu or the disk" in msg
        and "llm_int8_enable_fp32_cpu_offload" in msg
    )


def _select_input_device(model, torch_module):
    """Pick a safe device for input tensors when using accelerate device maps."""
    device_map = getattr(model, "hf_device_map", None)
    if isinstance(device_map, dict):
        for dev in device_map.values():
            if dev in {"cpu", "disk"}:
                continue
            if isinstance(dev, int):
                return torch_module.device(f"cuda:{dev}")
            return torch_module.device(str(dev))
        return torch_module.device("cpu")

    model_device = getattr(model, "device", None)
    if model_device is not None:
        return torch_module.device(model_device)
    return torch_module.device("cpu")


def load_model(
    model_id: str | None = None,
    profile: str | None = None,
    quantize: bool | None = None,
    device_map: str = "auto",
) -> tuple:
    """Load Gemma processor/tokenizer and model.

    Args:
        model_id: Explicit HuggingFace model ID. Overrides ``profile``.
        profile: ``"laptop"`` or ``"kaggle"``. Auto-detected when None.
        quantize: Enable 4-bit NF4 quantization. Defaults to True on laptop,
                  False on Kaggle.
        device_map: Passed to ``from_pretrained``; ``"auto"`` works for single GPU.

    Returns:
        (processor_or_tokenizer, model) tuple ready for ``generate()``.
    """
    from transformers import AutoModelForCausalLM, AutoProcessor, AutoTokenizer, BitsAndBytesConfig

    if profile is None:
        profile = "kaggle" if _is_kaggle() else "laptop"

    if model_id is None:
        model_id = MODEL_IDS[profile]

    if quantize is None:
        quantize = profile == "laptop"

    print(f"Loading {model_id}  (profile={profile}, quantize={quantize})")

    try:
        processor = AutoProcessor.from_pretrained(model_id)
    except ImportError as exc:
        # Gemma 4 text generation works with tokenizer-only path when video deps are missing.
        msg = str(exc)
        if "torchvision" not in msg.lower() and "gemma4videoprocessor" not in msg.lower():
            raise
        print("AutoProcessor unavailable (torchvision missing); falling back to AutoTokenizer.")
        processor = AutoTokenizer.from_pretrained(model_id)

    load_kwargs: dict = {"device_map": device_map}
    if quantize:
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype="bfloat16",
            bnb_4bit_use_double_quant=True,
        )
        load_kwargs["quantization_config"] = bnb_config
    else:
        load_kwargs["torch_dtype"] = "auto"

    try:
        model = AutoModelForCausalLM.from_pretrained(model_id, **load_kwargs)
    except (ValueError, TypeError) as exc:
        if isinstance(exc, ValueError) and not quantize:
            raise
        if isinstance(exc, ValueError) and not _is_low_vram_dispatch_error(exc):
            raise

        # Quantized auto-placement failed (VRAM too small, or accelerate/bnb
        # compat issue). Fall back to unquantized bf16 on CPU.
        import torch

        print(f"Quantized GPU load failed ({type(exc).__name__}); falling back to CPU bf16.")
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            device_map="cpu",
            torch_dtype=torch.bfloat16,
        )

    model.eval()

    return processor, model


def load_cloud_model(
    model_id: str = "google/gemma-4-E2B-it",
    base_url: str | None = None,
    api_key: str | None = None,
    print_url: bool = False,
) -> tuple:
    """Connect to an OpenAI-compatible cloud endpoint.

    Args:
        model_id: Model name to pass in API requests. The exact value depends
                  on what your endpoint expects (e.g. ``"google/gemma-4-E2B-it"``
                  or whatever the provider lists).
        base_url: API base URL. Falls back to the ``RYTMI_API_BASE_URL`` env var.
        api_key: API key. Falls back to ``RYTMI_API_KEY``, then ``"not-needed"``
                 (some local servers like vLLM / Ollama don't require a key).

    Returns:
        (client, model_id) tuple — pass these as ``(processor, model)`` to
        ``generate()``, ``explain_rhythm()``, etc.

    Example::

        client, model_id = load_cloud_model(
            model_id="gemma-4-e2b-it",
            base_url="http://localhost:8000/v1",
        )
        print(generate(client, model_id, "What is 4/4 time?"))
    """
    from openai import OpenAI

    base_url = base_url or os.environ.get("RYTMI_API_BASE_URL")
    api_key = api_key or os.environ.get("RYTMI_API_KEY", "not-needed")

    if not base_url:
        raise ValueError(
            "No base_url provided and RYTMI_API_BASE_URL is not set. "
            "Pass base_url= or set the environment variable."
        )

    client = OpenAI(base_url=base_url, api_key=api_key)
    if print_url:
        print(f"Cloud endpoint: {base_url}  model={model_id}")
    return client, model_id


def generate(
    processor,
    model,
    prompt: str,
    system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    max_new_tokens: int = 1024,
    temperature: float = 0.7,
    do_sample: bool = True,
) -> str:
    """Generate text from a prompt.

    Works with both backends:
    - **local**: ``processor`` is a HF tokenizer/processor, ``model`` is a HF model.
    - **cloud**: ``processor`` is an ``openai.OpenAI`` client, ``model`` is a model ID string.

    The backend is detected automatically from the type of ``model``.
    """
    if isinstance(model, str):
        return _generate_cloud(processor, model, prompt, system_prompt,
                               max_new_tokens, temperature)
    return _generate_local(processor, model, prompt, system_prompt,
                           max_new_tokens, temperature, do_sample)


def _build_cloud_messages(model_id: str, system_prompt: str, prompt: str) -> list[dict]:
    """Build the messages list for a cloud API call.

    Gemma models use a chat template that has no native ``system`` role turn.
    Many cloud providers either reject a leading ``system`` message or silently
    return empty content when one is present.  For Gemma we fold the system
    instructions into the first user turn instead.
    """
    if "gemma" in model_id.lower():
        return [{"role": "user", "content": f"{system_prompt}\n\n{prompt}"}]
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt},
    ]


def _effective_max_tokens(model_id: str, requested: int) -> int:
    """Return a safe max_tokens value for the given model.

    Thinking models (`:thinking` suffix) consume a large portion of the token
    budget for their internal chain-of-thought trace before writing any answer.
    We apply a 4× multiplier with a floor of 8192 so the actual response is not
    cut off.  The provider cap is typically 32 768, so this is still safe.
    """
    if ":thinking" in model_id.lower():
        return max(requested * 4, 8192)
    return requested


def _debug_print_request(model_id: str, messages: list[dict], max_tokens: int, temperature: float) -> None:
    sep = "=" * 72
    print(f"\n{sep}")
    print(f"[cloud-debug] REQUEST  model={model_id}  max_tokens={max_tokens}  temp={temperature}")
    print(sep)
    for m in messages:
        role = m["role"].upper()
        content = m["content"]
        print(f"── {role} ({len(content)} chars) ──")
        print(content)
    print(sep)


def _debug_print_response(response) -> None:
    choice = response.choices[0]
    sep = "=" * 72
    print(f"[cloud-debug] RESPONSE  finish={choice.finish_reason}  usage={response.usage}")
    print(sep)
    print(repr(choice.message.content))
    print(sep + "\n")


def _generate_cloud(
    client,
    model_id: str,
    prompt: str,
    system_prompt: str,
    max_new_tokens: int,
    temperature: float,
) -> str:
    """Generate via an OpenAI-compatible API.

    Retries once with temperature=0.5 if the response is empty.
    Set ``rytmi.llm.CLOUD_DEBUG = True`` to print every request/response.
    """
    messages = _build_cloud_messages(model_id, system_prompt, prompt)
    max_new_tokens = _effective_max_tokens(model_id, max_new_tokens)

    if CLOUD_DEBUG:
        _debug_print_request(model_id, messages, max_new_tokens, temperature)

    response = client.chat.completions.create(
        model=model_id,
        messages=messages,
        max_tokens=max_new_tokens,
        temperature=temperature,
    )

    if CLOUD_DEBUG:
        _debug_print_response(response)

    result = (response.choices[0].message.content or "").strip()
    if result:
        return result

    print("  empty response, retrying with temperature=0.5")
    response = client.chat.completions.create(
        model=model_id,
        messages=messages,
        max_tokens=max_new_tokens,
        temperature=0.5,
    )

    if CLOUD_DEBUG:
        _debug_print_response(response)

    return (response.choices[0].message.content or "").strip()


def _generate_local(
    processor,
    model,
    prompt: str,
    system_prompt: str,
    max_new_tokens: int,
    temperature: float,
    do_sample: bool,
) -> str:
    """Generate with a local HuggingFace model.

    Retries once with temperature=0.5 if the response is empty.
    """
    import torch

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt},
    ]

    def _run(temp: float) -> str:
        inputs = processor.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_tensors="pt",
            return_dict=True,
        )
        input_device = _select_input_device(model, torch)
        inputs_on_device = {k: v.to(input_device) for k, v in inputs.items()}
        input_len = inputs_on_device["input_ids"].shape[-1]

        with torch.inference_mode():
            output_ids = model.generate(
                **inputs_on_device,
                max_new_tokens=max_new_tokens,
                temperature=temp,
                do_sample=do_sample,
            )

        new_tokens = output_ids[0][input_len:]
        return processor.decode(new_tokens, skip_special_tokens=True).strip()

    result = _run(temperature)
    if result:
        return result

    print("  empty response, retrying with temperature=0.5")
    return _run(0.5)


def explain_rhythm(
    analysis: RhythmAnalysis,
    question: str = QUESTION_COUNTING,
    processor=None,
    model=None,
    max_new_tokens: int = 1024,
    temperature: float = 0.7,
    do_sample: bool = True,
    vocals=None,
    include_same_label_transitions: bool = False,
    include_phase_features: bool = False,
    include_phase_vocal: bool = False,
) -> str:
    """Explain a RhythmAnalysis result using Gemma.

    If processor/model are None, loads the default laptop profile automatically.
    Pass pre-loaded processor and model to avoid reloading between calls.

    Generation settings can be overridden per call so notebooks or apps can use
    shorter, more deterministic answers for some questions and longer outputs
    for richer coaching prompts.

    ``vocals`` is an optional ``VocalsInfo`` from the Gemma audio perception
    pass.  When omitted, falls back to ``analysis.vocals``; when that is also
    None the prompt is byte-identical to the pre-perception version.
    """
    if processor is None or model is None:
        processor, model = load_model()

    ioi = analysis.inter_onset_intervals
    if vocals is None:
        vocals = getattr(analysis, "vocals", None)

    rhythm_features = getattr(analysis, "rhythm_features", None)
    tempo_half = getattr(analysis, "tempo_half", None)

    dance_style = getattr(analysis, "dance_style", None)
    style_context = None
    profile = None
    basic_step = None
    if dance_style:
        profile = get_style_profile(dance_style)
        if profile:
            style_context = profile.general_context
            basic_step = profile.basic_step or None

    sections = getattr(analysis, "sections", None) or None
    phases = getattr(analysis, "phases", None) or None

    prompt = format_analysis_prompt(
        duration=analysis.audio.duration,
        tempo=analysis.tempo,
        n_beats=len(analysis.beats.times),
        n_onsets=len(analysis.onsets.times),
        beat_times=analysis.beats.times,
        ioi_ms=ioi,
        question=question,
        beats_per_measure=analysis.beats_per_measure,
        phrase_length=analysis.phrase_length,
        downbeat_times=analysis.downbeats,
        downbeat_confidence=analysis.downbeat_confidence,
        vocals=vocals,
        rhythm_features=rhythm_features,
        tempo_half=tempo_half,
        dance_style=dance_style,
        style_context=style_context,
        sections=sections,
        style_profile=profile,
        phases=phases,
        basic_step=basic_step,
        include_same_label_transitions=include_same_label_transitions,
        include_phase_features=include_phase_features,
        include_phase_vocal=include_phase_vocal,
    )
    return generate(
        processor,
        model,
        prompt,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        do_sample=do_sample,
    )


def polish_kizomba_tutor_output(
    draft: str,
    processor=None,
    model=None,
    track_name: str = "this track",
    max_new_tokens: int = 700,
    temperature: float = 0.4,
) -> str:
    """Run a second-pass polish over a one-pass kizomba tutor draft.

    Phase 29b — pairs ``KIZOMBA_TUTOR_POLISH_SYSTEM`` with
    ``build_kizomba_tutor_polish_prompt(track_name, draft)`` to rewrite the
    coaching text against a stricter rubric while preserving every P# header,
    time span, and beat tag from the draft.  Returns the polished string.

    The rewrite is opt-in.  One-pass output (``explain_rhythm`` with
    ``QUESTION_KIZOMBA_TUTOR``) remains the documented baseline; the polish
    pass costs an extra LLM call and can preserve or amplify ungrounded
    language already in the draft, so use only when the extra polish is
    worth the latency and risk.

    If processor/model are None, loads the default laptop profile (matches
    ``explain_rhythm``).
    """
    if processor is None or model is None:
        processor, model = load_model()

    return generate(
        processor,
        model,
        build_kizomba_tutor_polish_prompt(track_name, draft),
        system_prompt=KIZOMBA_TUTOR_POLISH_SYSTEM,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
    )


def explain_all(
    analysis: RhythmAnalysis,
    processor=None,
    model=None,
    max_new_tokens: int = 1024,
    temperature: float = 0.7,
    do_sample: bool = True,
    vocals=None,
    verify_sections: bool = True,
    verify_kizomba_drills: bool = True,
    verify_kizomba_transitions: bool = True,
    transition_retry: bool = False,
    include_same_label_transitions: bool = False,
    include_phase_features: bool = False,
    include_phase_vocal: bool = False,
) -> dict[str, str]:
    """Run all question templates and return a dict of {question_key: response}.

    When ``analysis.dance_style`` is set, style-parameterized questions
    automatically receive the style name via ``{style}`` placeholder filling
    in ``format_analysis_prompt``.

    When ``verify_sections=True`` (default) the SECTIONS answer is run
    through the Phase-11d regex grounding verifier: failing P# lines get
    replaced with the Phase-10c fallback and the cleaned output is what
    the dict carries under ``"sections"``.  The original raw model
    output and pass-rate stats are stashed under ``"sections_raw"`` and
    ``"sections_verified_stats"`` so callers (notebook viz, experiment
    notes) can show both the before/after and the verifier metrics.

    When ``verify_kizomba_drills=True`` (default) and ``analysis.dance_style``
    is ``"kizomba"`` or ``"bachata"``, the matching DRILLS answer is normalized
    against ``analysis.phases`` so generated P# ranges cannot cross
    section-label boundaries or duplicate phase coverage. The verifier is
    structural; the same routine handles both styles.

    When ``verify_kizomba_transitions=True`` (default) and ``analysis.dance_style``
    is ``"kizomba"``, the TRANSITIONS answer is normalized against the
    algorithmic transition list (``extract_transitions(analysis.phases)``):
    invented T# entries are dropped, missing transitions are filled with
    template text. Phase 40b will mirror this for bachata.

    When ``transition_retry=True`` (Phase 40e, opt-in), each missing transition
    is given one chance to be filled by Gemma via a per-boundary retry prompt
    instead of the deterministic template. The retry uses the same model /
    processor; the deterministic fallback remains the safety net when the
    retry fails to parse or matches the wrong boundary. Off by default to keep
    ``explain_all`` predictable and to avoid the extra LLM call when callers
    don't want it.
    """
    if processor is None or model is None:
        processor, model = load_model()

    sections_data = getattr(analysis, "sections", None) or None
    phases_data = getattr(analysis, "phases", None) or None
    dance_style = (getattr(analysis, "dance_style", "") or "").lower().strip()

    drills_keys_for_style = {
        "kizomba": "kizomba_drills",
        "bachata": "bachata_drills",
    }
    active_drills_key = drills_keys_for_style.get(dance_style)
    transitions_keys_for_style = {
        "kizomba": "kizomba_transitions",
        "bachata": "bachata_transitions",
    }
    active_transitions_key = transitions_keys_for_style.get(dance_style)

    results: dict[str, str] = {}
    for key, question in ALL_QUESTIONS.items():
        # Same-label transitions only matter for the *_transitions
        # prompts — other prompts don't reference the transitions block.
        per_question_same_label = (
            include_same_label_transitions
            if key in ("kizomba_transitions", "bachata_transitions")
            else False
        )
        raw = explain_rhythm(
            analysis,
            question=question,
            processor=processor,
            model=model,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            do_sample=do_sample,
            vocals=vocals,
            include_same_label_transitions=per_question_same_label,
            include_phase_features=include_phase_features,
            include_phase_vocal=include_phase_vocal,
        )
        if key == "sections" and verify_sections:
            verified = verify_sections_output(raw, sections_data)
            results["sections"] = verified.cleaned or raw
            results["sections_raw"] = raw
            results["sections_verified_stats"] = (
                f"total={verified.stats['total']} "
                f"passed={verified.stats['passed']} "
                f"failed={verified.stats['failed']} "
                f"pass_rate={verified.stats['pass_rate']:.2f}"
            )
        elif (
            key == active_drills_key
            and verify_kizomba_drills
            and phases_data
        ):
            verified = verify_kizomba_drills_output(raw, phases_data)
            results[key] = verified.cleaned or raw
            results[f"{key}_raw"] = raw
            results[f"{key}_verified_stats"] = (
                f"parsed={verified.stats['parsed']} "
                f"repaired_ranges={verified.stats['repaired_ranges']} "
                f"duplicate_phases={verified.stats['duplicate_phases']} "
                f"filled_missing={verified.stats['filled_missing']} "
                f"skipped_lines={verified.stats['skipped_lines']} "
                f"output_lines={verified.stats['output_lines']}"
            )
        elif (
            key == active_transitions_key
            and verify_kizomba_transitions
            and phases_data
            and dance_style in ("kizomba", "bachata")
        ):
            transitions = extract_transitions(
                phases_data, include_same_label=include_same_label_transitions,
            )
            retry_callback = None
            if transition_retry:
                def retry_callback(prompt: str, _proc=processor, _mod=model) -> str:
                    return generate(
                        _proc,
                        _mod,
                        prompt,
                        max_new_tokens=128,
                        temperature=temperature,
                        do_sample=do_sample,
                    )
            verified = verify_kizomba_transitions_output(
                raw, transitions, retry_callback=retry_callback,
            )
            results[key] = verified.cleaned or raw
            results[f"{key}_raw"] = raw
            if verified.stats:
                stats_str = (
                    f"parsed={verified.stats['parsed']} "
                    f"boundaries_matched={verified.stats['boundaries_matched']} "
                    f"boundaries_invented={verified.stats['boundaries_invented']} "
                    f"boundaries_missing_filled={verified.stats['boundaries_missing_filled']} "
                    f"skipped_lines={verified.stats['skipped_lines']} "
                    f"output_lines={verified.stats['output_lines']}"
                )
                if "retried" in verified.stats:
                    stats_str += (
                        f" retried={verified.stats['retried']}"
                        f" retry_succeeded={verified.stats['retry_succeeded']}"
                    )
            else:
                # No transitions in the analysis — verifier short-circuited.
                stats_str = "no_transitions"
            results[f"{key}_verified_stats"] = stats_str
        else:
            results[key] = raw
    return results
