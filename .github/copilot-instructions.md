# Rytmi — Copilot Workspace Instructions

## Project context
This repo is a **Gemma 4 Good Hackathon** prototype focused on **rhythm learning for dance and music**.

Before making major product, architecture, or prompt decisions, use these files as the source of truth:
- `docs/gemma-kaggle-compo.md` — competition goals, scoring, and constraints
- `docs/project-vision.md` — evolving project direction, MVP roadmap, and Gemma usage guidance
- `docs/how-it-works.md` — current DSP → prompt → Gemma architecture

## Product priorities
- Optimize for **learner value**, **demoability**, and **clear Gemma 4 integration**.
- Help users understand the **beat**, the likely **downbeat / "1"**, phrasing, and rhythm differences across songs and styles.
- Keep the system honest about uncertainty; do not present weak beat guesses as certain facts.

## Technical approach
- Use **DSP / librosa** for beat tracking, onset detection, tempo, downbeat candidates, and structure extraction.
- Use **Gemma 4** for explanation, tutoring, comparison, practice guidance, and other language/reasoning tasks.
- Do **not** treat Gemma as the primary beat detector.
- Prefer **small local Gemma models first** (`E2B`, `E4B`, often via Ollama or local endpoints). Use larger cloud models only when there is a clear quality gain.

## Important Gemma note
Official Gemma 4 audio input support is on **`E2B` and `E4B`** and is mainly documented for **speech-oriented tasks** such as transcription/translation. Do not overstate that as full music-structure understanding.

For this repo, vocals may be used as an **auxiliary signal**, but rhythm structure should still be extracted primarily with DSP.

## Repo conventions
- Keep Python code modular under `src/rytmi/`.
- Prefer explainable pipelines over opaque heuristics.
- If changing prompts or model behavior, keep outputs grounded in real analysis data.
- If changing project direction or major features, update `docs/project-vision.md`.
- If changing competition-facing positioning, keep it aligned with `docs/gemma-kaggle-compo.md`.
- For meaningful experiments or milestone changes, add or update a dated note under `docs/experiments/` summarizing: goal, what changed, evidence/results, what worked, limitations, and next step.
- File-specific guidance lives under `.github/instructions/` for DSP, Gemma prompting, tests, and docs.

## Secrets and env
- Do **not** open, read, quote, or rely on `.env`, `.env.*`, or other secret-bearing files unless the user explicitly asks for that exact file.
- Treat secret values as out of scope even if such files exist in the workspace; prefer code, docs, variable names, and user-provided non-secret context.
- Do **not** assume Jupyter, VS Code tasks, terminals, or Python processes auto-load `.env`; environment-backed config only exists when the launching process exports it.
- For cloud text inference, assume `RYTMI_API_BASE_URL` and `RYTMI_API_KEY` come from the real process environment, not automatic `.env` loading.
- Do **not** assume notebook/script model IDs have an environment fallback unless the code clearly implements one.
- Prefer external env injection mechanisms (shell export, launcher script, `direnv`, or OS/user-level secret storage) over repo-local secret files.

## Build and test
- Python requirement: `>=3.13`
- Main test command: `pytest`
- Ruff target/line length: `py313`, line length `99`

## Good feature directions
Prefer work that improves one or more of these:
- better downbeat / `1` detection
- clearer rhythm visualizations
- more learner-friendly Gemma explanations
- comparison of songs/styles
- a small end-to-end demo flow for Kaggle
