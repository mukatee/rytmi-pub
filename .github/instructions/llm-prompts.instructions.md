---
description: "Use when editing Gemma prompts, LLM integration, model selection, Ollama usage, or explanation logic in `src/rytmi/prompts.py` and `src/rytmi/llm.py`."
applyTo:
  - "src/rytmi/prompts.py"
  - "src/rytmi/llm.py"
---
# Gemma Prompting and Model Guidance

Before making major prompt or model decisions, consult:
- `docs/project-vision.md`
- `docs/gemma-kaggle-compo.md`
- `docs/how-it-works.md`

- Keep **Gemma 4 central for explanation, tutoring, comparison, and practice guidance**.
- Do **not** treat Gemma as the primary beat detector; it should interpret DSP results, not replace them.
- Prefer **small local models first** (`E2B`, `E4B`, often via Ollama or a local endpoint).
- Use larger models (`26B A4B`, `31B`) only when there is a clear quality gain.
- Audio support on `E2B` and `E4B` is mainly documented for **speech-oriented tasks**; do not overstate it as robust full-song music-structure analysis.
- Prompts should stay grounded in provided analysis data and avoid inventing unsupported musical facts.
- Good outputs are practical and uncertainty-aware: likely count, likely `1`, why a section is hard to count, and what to practice next.
