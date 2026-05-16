---
description: "Use when editing beat tracking, downbeat detection, onset analysis, tempo estimation, or rhythm visualization in `src/rytmi/`. Keep outputs grounded in DSP and learner-friendly."
applyTo:
  - "src/rytmi/audio.py"
  - "src/rytmi/dsp.py"
  - "src/rytmi/types.py"
  - "src/rytmi/viz.py"
---
# Rhythm DSP Guidance

- Treat **DSP as the source of truth** for beat timing, tempo, onset structure, and likely downbeat candidates.
- Prefer **explainable heuristics** over opaque logic; optimize for learner value, not just technical cleverness.
- Improve outputs that help users answer: "Where is the beat?", "Where is the `1`?", and "How confident is this guess?"
- Surface uncertainty instead of pretending exact certainty on difficult songs.
- Validate on more than synthetic click tracks when possible; include bachata, kizomba, salsa, and other real music examples.
- If you add new analysis fields, keep `RhythmAnalysis`, visualizations, and tests in sync.
