# Claude Code Guidance for `kaggle-gemma4-rytmi`

Use these files as the project source of truth before major coding or planning work:
- `docs/gemma-kaggle-compo.md`
- `docs/project-vision.md`
- `docs/how-it-works.md`

## What this project is
A rhythm-learning assistant for dance/music practice, built for the **Gemma 4 Good Hackathon** and for personal learning value.

## Core intent
- Help users hear and understand the beat, the likely **`1`**, phrasing, and rhythm differences across songs.
- Keep the app **practical, local-first when possible, and useful for learners**.
- Make **Gemma 4 central in explanation/tutoring**, but do not force it into tasks better solved by DSP.

## Expected technical split
- **DSP / librosa**: onset detection, beat tracking, tempo, downbeat candidates, structure extraction
- **Gemma 4**: explanation, tutoring, comparison, practice cues, interactive rhythm guidance

## Gemma 4 model guidance
- Start with **smaller local models** first (`E2B`, `E4B`, often via Ollama/local endpoints).
- Use larger models such as `26B A4B` or `31B` only when their extra reasoning quality clearly matters.
- Audio support on `E2B` / `E4B` is mainly **speech-oriented**. Do not assume full music-analysis capability from raw song audio.

## Working style for this repo
- Favor explainable, grounded outputs.
- Surface uncertainty instead of pretending confidence.
- Align new features with the roadmap in `docs/project-vision.md`.
- Prefer changes that improve the eventual Kaggle demo story.
- For bigger experiments or meaningful milestone changes, write a dated note under `docs/experiments/` capturing the goal, changes, evidence, what worked, limitations, and recommended next step.
- Also consult file-specific guidance under `.github/instructions/` when working on DSP, prompts/LLM integration, tests, or docs.

## When editing code
- Keep modules under `src/rytmi/` focused and simple.
- Add or update tests in `tests/` when behavior changes.
- Keep docs in sync when the product direction changes.
