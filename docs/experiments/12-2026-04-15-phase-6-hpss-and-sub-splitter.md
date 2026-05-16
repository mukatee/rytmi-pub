# Phase 6 — HPSS break branches + sub-phrase splitter

**Date:** 2026-04-15

> **TL;DR for future readers:** Phase 6 had a lost first iteration (git reset). The committed Phase 6 code **re-derives all features of that iteration**; nothing described below is missing from the repo. See "Context / prior state" for the full story.

## Goal

Give `_label_sections()` a melodic-vs-percussion signal so it can distinguish a kizomba **melodic drop** (bass and melody collapse while tumba / congas keep playing) from a bachata **full drop** (everything thins out at once), and add a narrow-scope sub-phrase splitter that can insert extra phrase-aligned boundaries inside long individual `main` sections where per-phrase RMS shifts exceed a local threshold.

## Context / prior state

Phase 5 shipped a two-branch break rule in `_label_sections()`:

- **severe** — `rms_ratio < 0.60 × track_median_rms` alone
- **moderate** — `rms_ratio < 0.85 × track_median_rms` AND `opb < 0.70 × track_median_opb`

This worked on bachata where breaks are quieter *and* sparser, but missed several real kizomba cases because the severe branch only looked at the global RMS envelope. On *Filomena Maricoa Teu Toque* (official), sec 13 had `RMS×0.42, opb=2.6` — the thin mix was clearly a break by ear, but the remaining percussion hits were busy enough that `opb` stayed above the moderate-branch threshold; it only fell into the severe branch by coincidence because RMS was very low. And on tracks where the melody drops but the drum pattern is *louder than average*, neither branch fired at all.

A prior iteration of Phase 6 existed — HPSS features + four-branch classifier + a first cut of the sub-splitter — but a notebook glitch trashed the working tree and a `git reset --hard origin/master` wiped the uncommitted work. Phase 6 as shipped here re-derives the HPSS and break-classifier work, salvages the sub-splitter with a narrower scope baked in from the start to avoid the sliver regression the first iteration hit, and is committed + pushed at the end so it can't evaporate again.

## Hypothesis

1. Running `librosa.effects.hpss` once per track and computing per-section `harm_ratio` / `perc_ratio` (segment mean over track-global mean) gives a four-branch break classifier — `melodic`, `percussive`, `severe`, `full` — enough signal to separate melodic drops from full drops without losing any Phase 5 break coverage.
2. A per-phrase RMS-shift splitter that only operates on individual long `main` sections (never on multi-section same-label runs, and only on `main`) can catch sub-structure the global novelty curve's `0.4 × max` threshold misses, without reintroducing the slivers the first iteration produced.

## What changed

**[src/rytmi/dsp.py](../../src/rytmi/dsp.py)**

- New module constant `_HPSS_MARGIN = 1.0`.
- New break-classifier thresholds: `_BREAK_MELODIC_HARM_RATIO`, `_BREAK_MELODIC_PERC_FLOOR`, `_BREAK_PERCUSSIVE_PERC_RATIO`, `_BREAK_PERCUSSIVE_HARM_FLOOR`, `_BREAK_SEVERE_HARM_RATIO`, `_BREAK_SEVERE_PERC_RATIO`.
- Removed `_BREAK_RMS_SEVERE_DROP` — the severe path is now HPSS-gated instead of RMS-gated.
- `detect_sections()` runs `librosa.effects.hpss(audio.samples)` once before the per-segment feature loop, computes per-segment `harm_ratio` / `perc_ratio` alongside the existing `rms_ratio` / `opb`, and feeds them into a widened 7-tuple `labeller_input`.
- `_label_sections()` widened return shape from `(start, end, label)` to `(start, end, label, break_branch)`. Break detection replaced with four disjunctive branches — `melodic`, `percussive`, `severe`, `full` — in that order. When HPSS ratios are legacy (all zero, synthetic fixtures) only the `full` branch runs, preserving Phase 5 behaviour for existing tests.
- New helper `_split_long_runs_on_phrase_shifts()`: returns additional phrase-aligned boundaries to inject inside individual `main` sections that are ≥ 4 phrases / 24 s long, where a per-phrase RMS shift (normalised by the global mean) exceeds `max(0.18, 90th percentile within-section)`. Narrow scope by design: `splittable_labels=("main",)`, single-section only, never walks multi-section same-label runs.
- `detect_sections()` refactored into a `_label_for(bounds)` closure so the feature / energy / label pass can re-run cleanly on an expanded boundary list after the sub-splitter proposes extras.
- `_snap_boundaries_to_phrases()` now propagates `harm_ratio`, `perc_ratio`, and `break_branch` onto the rebuilt `SongSection` objects (earlier omission was caught during eval when the H×/P× columns disappeared after snapping).
- `describe_sections()` adds `H×` and `P×` columns to the signals string and renames break rows to `break[branch]` (e.g. `break[melodic]`, `break[severe]`).

**[src/rytmi/types.py](../../src/rytmi/types.py)**

- `SongSection` gains `harm_ratio: float | None`, `perc_ratio: float | None`, `break_branch: str | None`, all nullable so synthetic fixtures keep working.

**[tests/test_dsp.py](../../tests/test_dsp.py)**

- 10 new tests: `test_detect_sections_populates_hpss_ratios`, `test_label_sections_{melodic,percussive,severe,full}_branch_fires`, `test_label_sections_no_false_break_on_quieter_groove`, `test_split_long_runs_{inserts_boundary,no_op_on_short_run,preserves_non_main_labels}`, `test_describe_sections_shows_hpss_and_branch`.
- 5 existing Phase 5 break/peak/build tests updated to pass 7-tuples (with neutral HPSS ratios `1.00 / 1.00`) and to unpack the widened 4-tuple return from `_label_sections`. The `break_on_low_rms_low_opb` test now also asserts `break_branch == "full"`.

**[docs/how-it-works.md](../how-it-works.md)** — new "HPSS-based break classification (Phase 6)" subsection describing the four branches, the sub-splitter scope, and the `describe_sections()` H×/P× / `break[branch]` surfacing.

## Evidence / test results

`pytest tests/test_dsp.py -q` → **69 passed** (Phase 5 count + 10 Phase 6 additions). Full suite `pytest -q` → **199 passed, 1 skipped**.

Eval on the 10-track set (`tmp/run_phase5_eval.py`) after the fix to propagate HPSS fields through snapping:

| track | break row | branch | signals |
|---|---|---|---|
| bachata/Propuesta_Indecente | sec 1 | `full` | RMS×0.55 opb=1.6 H×0.52 P×0.63 |
| kizomba/All_Of_Me | sec 13 | `melodic` | RMS×0.81 opb=2.1 **H×0.67 P×1.07** |
| kizomba/Baila_Kizomba_Amor | sec 10 | `full` | RMS×0.53 opb=0.9 H×0.60 P×0.56 |
| kizomba/Charbel_E_Magia_Ben_Ana | sec 14 | `full` | RMS×0.72 opb=1.1 H×0.83 P×0.42 |
| kizomba/Charbel_E_Magia_Official_4K | secs 1–4, 9–10 | `melodic` (×6) | H×0.69–0.83 **P×1.61–1.63** |
| kizomba/Charbel_E_Magia_Official_4K | sec 15 | `full` | RMS×0.77 opb=0.4 H×0.91 P×0.49 |
| kizomba/Teu_Toque_Official | sec 13 | **`severe`** | RMS×0.42 opb=2.6 **H×0.45 P×0.28** |
| kizomba/Tony_Pirata Teu_Toque | sec 12 | **`severe`** | RMS×0.46 opb=2.7 **H×0.43 P×0.27** |

No breaks on El_Chaval (cut or official) or Grupo_Extra — all three lacked Phase 5 breaks too, confirming no regression on stable tracks.

## What worked

- The **melodic** branch fires cleanly on *All_Of_Me* sec 13, a section whose `RMS×0.81` is too high for the Phase 5 severe path and whose `opb=2.1` is too high for the moderate path, but whose `H×0.67 / P×1.07` signature is unambiguous once HPSS separates the components.
- The **severe** branch catches both *Teu Toque* cases (`H×0.45 P×0.28` and `H×0.43 P×0.27`) where `opb` stayed high (2.6–2.7) so the old moderate branch would have rejected them — direct evidence that HPSS gives break classification signal that global RMS + onset density alone cannot recover.
- The **full** branch preserves all the classic bachata / kizomba "everything thins out" breaks as a direct rename of the old moderate rule, so there is no regression on *Propuesta_Indecente*, *Baila_Kizomba_Amor*, or *Charbel Ben_Ana*.
- The sub-splitter no-ops on every track in the current eval set — the global novelty curve is already catching the main-run sub-structure that matters on real music — which is exactly the "costs nothing when it no-ops" design target. Coverage comes from the synthetic test proving it fires on a 12-phrase single `main` with a mid-run 30% RMS dip.

## What did not / limitations

- *Charbel_E_Magia_Official_4K* produces **six back-to-back `break[melodic]` sections** across the first minute of the track (secs 1–4 and 9–10). The H×/P× values (H×0.69–0.83, P×1.61–1.63) are honest — the song really does have an extended percussion-led intro with low harmonic content — but the result reads as a long run of tiny breaks where a dancer would probably perceive one ambient-intro section. This isn't a regression from Phase 5 (the same track looked equally noisy in the prior two-branch eval), and it isn't wrong in signal terms, but the presentation over-fires on this specific song shape. Candidates for Phase 7+ to tune: merge adjacent same-branch breaks at the phase layer, or add a "consecutive melodic breaks collapse into an `intro_groove` zone" post-pass.
- The **percussive** branch is present for completeness but fires on zero tracks in the current eval set. Revisit after Phase 8 grows the eval set — if no real track ever triggers it, consider dropping the branch.
- HPSS adds ~1–3 s to `analyze()` per track on a 4-minute song. Acceptable for notebook interactivity on the 10-track set; revisit if batch eval grows to 50+ tracks.
- `_BREAK_MELODIC_HARM_RATIO = 0.70` and `_BREAK_MELODIC_PERC_FLOOR = 0.85` are first-guess thresholds calibrated against the prior iteration's observations. The Charbel over-firing suggests they may be too loose on harmonically-thin percussion-led material. Phase 8 with a larger annotated eval set can tighten these numerically.

## Decision / takeaway

Ship it. HPSS break classification is a clear net win: three new branches that catch real kizomba breaks (*All_Of_Me* melodic, both *Teu Toque* severe) that Phase 5 either missed or caught only by accident, with no regressions on the bachata tracks. The sub-splitter is scoped narrowly enough that it cannot regress anything — it no-ops on every real eval track — and the synthetic test proves it is wired up correctly for the rare cases where novelty misses sub-structure.

Commit AND push at end of phase is now a standing procedural guardrail — losing the first Phase 6 iteration to a git reset cost a whole session of rework. The plan file for Phase 7 bakes this in as an explicit final step and the user-facing memory note documents the rule so it survives compaction.

## Next step

Phase 7 (downbeat-anchored phrase grid + eval set metadata / runner / guide) is fully scoped in [`.claude/plans/validated-tumbling-toast.md`](~/.claude/plans/validated-tumbling-toast.md) under "Next phase (Phase 7) preview". It depends on Phase 6 being committed + pushed first because both phases touch `describe_sections()` and `detect_sections()`. Starting Phase 7 before Phase 6 is merged would create unmanageable conflicts.
