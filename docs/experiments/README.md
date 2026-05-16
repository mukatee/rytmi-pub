# Experiment Notes

> Purpose: keep a **dated, durable history of meaningful experiments** so the project can preserve what was tried, what changed, what worked, and what remained uncertain even as notebooks and code evolve.

## When to add a note
Create or update an entry here for **bigger experiments or milestones**, especially when you:
- change DSP heuristics or confidence logic,
- change Gemma prompts or model strategy,
- evaluate on a new curated song set,
- learn something important that should be reusable in the final Kaggle writeup,
- or complete a meaningful coding/research pass with Copilot or Claude.

## Naming convention
Use numbered, dated filenames such as:
- `01-2026-04-11-downbeat-confidence.md`
- `08-2026-04-13-phase-3-5-quality-improvements.md`

The leading number gives chronological experiment order within the project.

## Suggested structure
Each note should usually contain:
1. **Goal**
2. **Context / prior state**
3. **Hypothesis**
4. **What changed**
5. **Evidence / test results**
6. **What worked**
7. **What did not / limitations**
8. **Decision / takeaway**
9. **Next step**

## Related: research-driven iteration loop

Starting in Phase 11, larger heuristic changes are sourced from a deliberate **question → follow-up → recipe** loop rather than from listening-pass tuning alone. The methodology and per-Q mapping live in [`../research/README.md`](../research/README.md); the raw Perplexity threads live next to it under [`../research/`](../research/).

## Current index
- [`01-2026-04-11-downbeat-confidence.md`](./01-2026-04-11-downbeat-confidence.md) — second-pass review and improvement of the likely downbeat / `1` confidence heuristic
- [`02-2026-04-11-confidence-surfacing.md`](./02-2026-04-11-confidence-surfacing.md) — surfacing downbeat confidence in learner flow
- [`03-2026-04-11-eval-set-style-grounding.md`](./03-2026-04-11-eval-set-style-grounding.md) — real-song eval set: grounding the STYLE question in social dance
- [`04-2026-04-12-audio-transcription-style-grounding.md`](./04-2026-04-12-audio-transcription-style-grounding.md) — audio transcription for style disambiguation
- [`05-2026-04-12-rhythm-features.md`](./05-2026-04-12-rhythm-features.md) — DSP rhythm features for style disambiguation
- [`06-2026-04-12-style-dancer-chaining.md`](./06-2026-04-12-style-dancer-chaining.md) — STYLE→DANCER chaining, half-time signal, clip retry, empty response retry
- [`07-2026-04-12-phase-1-style-input-and-key-alignment.md`](./07-2026-04-12-phase-1-style-input-and-key-alignment.md) — Phase 1 & 2: style input pivot, segmentation DSP
- [`08-2026-04-13-phase-3-5-quality-improvements.md`](./08-2026-04-13-phase-3-5-quality-improvements.md) — Phase 3.5: merge phases, song arc, basic_step guardrails
- [`09-2026-04-13-phase-4-section-aware-visualization.md`](./09-2026-04-13-phase-4-section-aware-visualization.md) — Phase 4: colored section bands, S1/S2/S3 labels, time ranges, reset/seek controls
- [`10-2026-04-13-phase-4-5-section-quality.md`](./10-2026-04-13-phase-4-5-section-quality.md) — Phase 4.5: section diagnostic helper, phrase-grid snapping, energy encoding on timeline
- [`11-2026-04-14-percentile-section-labels.md`](./11-2026-04-14-percentile-section-labels.md) — Phase 5: percentile-based energy + signal-aware break/peak labels (track 6 missed break caught)
- [`12-2026-04-15-phase-6-hpss-and-sub-splitter.md`](./12-2026-04-15-phase-6-hpss-and-sub-splitter.md) — Phase 6: HPSS-derived four-branch break classifier (melodic/percussive/severe/full) + narrow-scope sub-phrase splitter
- [`13-2026-04-16-phase-7-downbeat-offset-eval-set.md`](./13-2026-04-16-phase-7-downbeat-offset-eval-set.md) — Phase 7: downbeat-anchored phrase grid, confidence gating, eval set metadata + runner
- [`14-2026-04-17-phase-8-boundaries-and-viz.md`](./14-2026-04-17-phase-8-boundaries-and-viz.md) — Phase 8: break/peak edge expansion, sub-splitter widening, embedded-break scanner, outro palette refresh, notebook version stamp
- [`15-2026-04-17-phase-9-vocal-aware-boundaries.md`](./15-2026-04-17-phase-9-vocal-aware-boundaries.md) — Phase 9: short_break label, edge contraction, same-branch break-chain merge, Demucs/Gemma vocal-activity envelope, vocal-aware intro extension + outro contraction
- [`16-2026-04-18-phase-10-downbeat-instrumental-prompts.md`](./16-2026-04-18-phase-10-downbeat-instrumental-prompts.md) — Phase 10: downbeat-confidence v2 (kick-band fusion), `instrumental` label for vocal-drop passages, prompt distinctiveness constraints (numeric anchoring + distinct-features block)
- [`17-2026-04-18-phase-11-validated-upgrades.md`](./17-2026-04-18-phase-11-validated-upgrades.md) — Phase 11: vocal-RMS v2 (mean − 18 dB + 3 s smoothing), BeatNet downbeat fusion (5 tracks above the 0.25 gate), `spoken_intro` label via Gemma E4B speech-vs-singing, regex grounding verifier on `QUESTION_SECTIONS` output
- [`18-2026-04-18-phase-12-short-break-tightening.md`](./18-2026-04-18-phase-12-short-break-tightening.md) — Phase 12 (Commit A): short_break HPSS-branch gate — `melodic` / `percussive` on 1-phrase sections now require a real RMS drop or severe HPSS collapse, retracting Charbel-Ana false positives without touching regular `break[*]`
- [`19-2026-04-19-phase-12b-vocal-source-ab.md`](./19-2026-04-19-phase-12b-vocal-source-ab.md) — Phase 12 (Commit B): demucs vs gemma vocal-source A/B on the 10-track eval set — gemma flips main ↔ instrumental and drifts ~8 counts; demucs stays default, gemma demoted to opt-in experimental
- [`20-2026-04-19-phase-13-accent-templates.md`](./20-2026-04-19-phase-13-accent-templates.md) — Phase 13 (Commit A + A2): kizomba / bachata accent-template voice + eval-set expansion to 15 tracks; Commit A regressed 4 confident tracks, Commit A2's adaptive max-confidence guard recovers Phase-11 baseline (5 of 10 above gate retained, +1 newly above gate); Baila / Teu Toque / All Of Me remain stuck → Commit B2 (Gemma tiebreaker)
- [`21-2026-04-19-phase-13b2-gemma-downbeat-tiebreak.md`](./21-2026-04-19-phase-13b2-gemma-downbeat-tiebreak.md) — Phase 13 (Commit B2): Gemma E4B per-offset downbeat tiebreaker module + 13 unit tests + 16-track eval. Negative result — Gemma voted NO on every candidate on every below-gate track (52/52), module no-ops cleanly; Phase-13 recovery path shifts to Phase 14 preprocessing (HPSS-percussive / Demucs drum-stem)
- [`22-2026-04-19-phase-14-preprocessing-evaluation.md`](./22-2026-04-19-phase-14-preprocessing-evaluation.md) — Phase 14: three-way preprocessing evaluation (HPSS-percussive / Demucs drum-stem / B2 permissive prompt retry). All three produce ≤ ±0.014 movement on the three stuck kizomba tracks; none crosses the 0.25 gate. B2 path closed permanently (v1 all-NO, v2 all-YES). Recommendation: shelve all three, reframe as style-gating or user-tap problem
- Phases 23–41 (2026-04-20 → 2026-05-11): see filenames in this directory; covers beat-clarity scoring, batida tracker, tap ground truth, demo polish, listening guide, section-role narration, rhythm anatomy, substyles, drill verifier, vocal-activity in demo notebooks, bachata coaching surface, kizomba transitions and the four 40-series rewrites, and the Phase 41-lite / 41-D per-phase feature-tag trial (reverted; tag saturated under Demucs).
- [`42-2026-05-12-vocal-active-break-demotion.md`](./42-2026-05-12-vocal-active-break-demotion.md) — Phase 42: symmetric counterpart of Phase 10 — `break`/`short_break` sections with `vocal_ratio ≥ 0.5` AND non-low energy get demoted to `main`; energy gate preserves genuine vocal-led kizomba breaks. Fixes Charbel "E Magia" intro-adjacent false-break (both versions). +6 unit tests.
- [`43-2026-05-12-gemma-audio-probe.md`](./43-2026-05-12-gemma-audio-probe.md) — Phase 43 (negative result): `E4B` audio prompted with kizomba-teacher framing on three 12 s excerpts produced interchangeable boilerplate, did not differentiate clips, and mislabelled the break as "smooth and inviting". DSP-as-grounding architecture confirmed; raw-audio music-content prompting shelved. Reproducible probe: `python demo_assets/scripts/probe_gemma_audio.py`.

## Negative-result lookups (so the lessons don't get lost)

These are the experiments where the headline finding is "**don't bother
with this approach**" — preserved so future iterations don't re-spend the
same effort.

- **Gemma audio for music understanding** — [Phase 43](./43-2026-05-12-gemma-audio-probe.md). `E4B` audio is speech-shaped, not music-shaped. Use DSP for music structure; reserve the audio modality for the speech-vs-singing yes/no (Phase 11). See also project-vision audio note and [`../kaggle_writeup.md`](../kaggle_writeup.md) §audio.
- **Gemma per-offset downbeat tiebreaker** — [Phase 13b2](./21-2026-04-19-phase-13b2-gemma-downbeat-tiebreak.md). Voted NO on 52/52 candidates; no-ops cleanly but adds nothing.
- **HPSS-percussive / Demucs-drum / permissive-prompt retry for stuck downbeats** — [Phase 14](./22-2026-04-19-phase-14-preprocessing-evaluation.md). All three move the metric ≤ ±0.014; none crosses the gate. Solve via style-gating or user tap instead.
- **Gemma vocal source as default** — [Phase 12b](./19-2026-04-19-phase-12b-vocal-source-ab.md). Drifted ~8 counts vs Demucs. Demucs is default; Gemma vocal source stays opt-in.
- **Phase 41-D per-phase feature tags** — see Phase 41 file. Demucs vocal coverage saturates as "present", so the tag co-fires with the section label and adds no signal. Reverted; `vocal_ratio` field kept as primitive and used for Phase 42's energy-gated demotion.
