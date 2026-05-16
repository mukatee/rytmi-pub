---
description: "Use when editing project docs, README-style descriptions, or competition-facing writeups. Keep the competition reference and project vision aligned and grounded."
applyTo: "docs/**/*.md"
---
# Documentation Guidance

Use these files as the source of truth:
- `docs/gemma-kaggle-compo.md` — mostly static competition reference
- `docs/project-vision.md` — living project brief and evolving roadmap
- `docs/how-it-works.md` — current architecture explanation
- `docs/experiments/` — dated notes capturing what changed, what worked, and what was learned from meaningful experiments

- Keep competition claims aligned with the official Kaggle and Gemma documentation.
- Keep product direction aligned with the repo’s core theme: **rhythm learning for dance/music with DSP + Gemma tutoring**.
- When discussing Gemma audio capabilities, clearly note that current official support is strongest for **speech-oriented** tasks on `E2B` / `E4B`.
- Prefer honest wording about uncertainty, limitations, and what is still experimental.
- For major experiments, preserve the historical learning in a dated file under `docs/experiments/` instead of only overwriting the latest notebook or summary.
