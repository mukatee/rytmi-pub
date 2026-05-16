---
description: "Use when adding or modifying tests for DSP, LLM prompting, visualizations, or regression coverage in `tests/`. Focus on real behavior and stable, reproducible checks."
applyTo: "tests/**/*.py"
---
# Testing Guidance

- Test **real behavior**, not just mock behavior.
- Prefer deterministic checks using synthetic audio, fixed arrays, or stable fixtures.
- For DSP changes, add or update tests for tempo ranges, beat counts, likely downbeat behavior, and confidence/uncertainty where relevant.
- For LLM code, mock at the backend boundary when needed, but assert that prompts include the real analysis data and that outputs remain grounded.
- Avoid default tests that require downloading large models or needing a GPU unless explicitly marked.
- Keep regression tests small and targeted so future prompt or DSP changes are easier to evaluate.
