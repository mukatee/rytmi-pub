# 2026-05-06 — Phase 37c: Deterministic verifier for kizomba drill ranges

## Goal

Turn a live Gemma output limitation into an explicit architecture lesson: use Gemma 4 for learner-facing coaching language, but validate structured phase coverage deterministically before showing the result to the learner.

## Trigger

After Phase 37a-bis, the user reran `notebooks/00_demo.ipynb` and `notebooks/09_kizomba_extended.ipynb`. The downbeat / count-position guard fix held: the Filomena listening guide no longer used forbidden beat-position wording, and the extended kizomba outputs had no learner-facing downbeat/count-position leaks.

The same fresh `00_demo` run exposed a separate structured-output failure in `kizomba_drills`:

```text
P7-P8: main (159s-195s, beat: clear) — Drill: same walk-step as P2-P5, but add subtle hip styling once the basic feels automatic. 36s.
P8: outro (195s-209s, beat: clear) — Drill: slow the pace and return to minimal movement. 14s.
```

This duplicated phase P8 and crossed a `main` → `outro` boundary. The prompt already contained the correct rule, a self-check instruction, and a positive worked example. That makes the result a useful Gemma-in-action limitation rather than just a missing prompt sentence: the model can produce good coaching text while still failing a rigid structural invariant.

## What changed

- **`src/rytmi/prompts.py`** — added `verify_kizomba_drills_output(...)` and `VerifiedKizombaDrillsOutput`.
  - Parses `P#` / `P#-P#` drill lines.
  - Compares each emitted range against `analysis.phases`.
  - Shrinks a range at the first section-label or beat-tag boundary.
  - Skips duplicate phase coverage.
  - Fills missing phases with conservative deterministic fallback drills.
  - Preserves Gemma's drill text whenever the range is structurally valid.
- **`src/rytmi/prompts.py`** — factored phase beat-tag wording through a shared `_beat_clarity_tag(...)` helper so the prompt summary and verifier use the same `subtle` / `moderate` / `clear` thresholds.
- **`src/rytmi/llm.py`** — `explain_all(...)` now applies the drills verifier by default when `analysis.phases` exists.
  - Clean learner-facing output remains under `results["kizomba_drills"]`.
  - Raw model output is preserved under `results["kizomba_drills_raw"]`.
  - Verifier stats are exposed under `results["kizomba_drills_verified_stats"]`.
- **`notebooks/00_demo.ipynb`** — the demo now applies `verify_kizomba_drills_output(...)` explicitly around the direct `explain_rhythm(...)` call.
  - Learner-facing `kizomba_drills` shows the verified practice plan.
  - The raw Gemma draft and verifier stats are exported as labeled evidence sections.
- **`notebooks/09_kizomba_extended.ipynb`** — added an optional Phase 37c smoke pass (`RUN_KIZOMBA_DRILLS=True`) so the extended kizomba set can generate verified drills per track.
  - The notebook stores cleaned drills, raw drafts, and verifier stats in `PER_TRACK` for review.
- **`tests/test_prompts.py`** — added focused verifier tests for:
  - the live final `main` / `outro` boundary failure,
  - preserving valid same-label groups,
  - filling a missing boundary phase with a fallback drill.
- **`tests/test_llm.py`** — added an `explain_all(...)` integration test proving the verifier is applied and raw/stats fields are preserved.

## Evidence

Focused tests:

```text
$ python -m pytest tests/test_prompts.py::test_verify_kizomba_drills_repairs_crossed_outro_range tests/test_prompts.py::test_verify_kizomba_drills_preserves_valid_same_label_group tests/test_prompts.py::test_verify_kizomba_drills_fills_missing_boundary_phase tests/test_llm.py::test_explain_all_verifies_kizomba_drills -q
....                                                                     [100%]
4 passed in 0.25s
```

Full suite after the verifier landed:

```text
$ python -m pytest
================= 418 passed, 1 skipped, 64 warnings in 47.22s =================
```

Initial post-verifier live rerun exposed an integration gap rather than a verifier bug: `00_demo` still showed the invalid `P7-P8: main` / `P8: outro` output because that notebook called the low-level `explain_rhythm(...)` helper directly. The verifier was wired into `explain_all(...)`, but the demo presentation path bypassed it.

Follow-up source changes wired the verifier into `00_demo` explicitly and broadened `notebooks/09_kizomba_extended.ipynb` to cover both the curated `eval_set/kizomba/` and the broader `extended_set/kizomba/` source roots in one run, with source-labeled headings.

### Live evidence across 17 kizomba tracks (2026-05-08)

Reran `notebooks/09_kizomba_extended.ipynb` against `eval_set=11, extended_set=6` with `RUN_KIZOMBA_DRILLS=True` and `RUN_POLISH=True`. Per-track verifier stats are dumped in `notebooks/09_kizomba_extended_outputs.md`. Aggregated:

- **17/17** tracks completed end to end.
- **0/17** tracks emitted duplicate phases (`duplicate_phases=0` everywhere). The original Filomena-style `P8 / P8` collision did not recur in any track.
- **3/17** tracks needed zero verifier action (`repaired_ranges=0`, `filled_missing=0`, `skipped_lines=0`): `Charbel_-_E_Magia_Ben_Ana`, `Don_Kikas_-_Angolanamente_Sensual`, `MIKA_MENDES_-_MAGICO_2011`.
- **14/17** tracks needed at least one structural repair, missing-phase fill, or duplicate-line skip. The dominant failure mode was Gemma under-covering many same-label `main` segments via long `P#-P#` ranges, which the verifier expanded into per-phase coverage.
- Heaviest case: `Daniel_Santacruz_-_Lento` with `parsed=8 repaired_ranges=6 filled_missing=9 skipped_lines=6 output_lines=11`. Raw Gemma collapsed phases `P5-P9`, `P11-P15`, and `P16-P23`, with the last two crossing `main` vs. structural boundaries; verifier turned that into 11 phase-correct lines covering every section.
- Polished `kizomba_tutor` consistently preserved the one-pass `P#` headers, time spans, beat tags, and ordering. Polish operated as language smoothing, not structural rewriting, and the kizomba downbeat guard held across all 17 tracks.

Known caveat: when the verifier injects fallback drill text for `filled_missing` lines, the prose is repetitive (e.g. several `Drill: practice steady weight transfers through this section.` lines on `All_Of_Me`). Structure is reliable; the deterministic fill text is not learner-grade coaching.

## What worked

- The verifier fixes the exact live failure deterministically: `P7-P8: main` becomes `P7: main`, while the explicit `P8: outro` line is preserved.
- Valid ranges still pass through unchanged, so Gemma keeps doing the high-value work: generating natural practice language.
- Raw output and stats are retained, which is useful for the demo and competition writeup. We can show both the model's useful draft and the guardrail that makes it reliable.
- Keeping `explain_rhythm(...)` raw remains useful for inspection and debugging. Learner-facing demo paths now apply the verifier explicitly before presenting exact practice plans.

## Limitation / lesson

This is a concrete limitation of using Gemma for rigid structured output. Prompting reduced failures, but did not eliminate them. The lesson is not that Gemma is unsuitable; it is that Gemma should be used where it is strongest — explanation, tutoring tone, and practice-language generation — while deterministic code enforces invariants like "every phase appears once" and "a range cannot cross a section-label boundary."

The follow-up integration gap adds a second lesson: guardrails only help the learner if they are wired into every presentation path. A verifier in `explain_all(...)` does not protect a notebook cell that calls the raw single-question helper and prints the result directly.

For the competition story, this is a strength if presented honestly: the project shows Gemma 4 in the core learning loop, and also shows the engineering needed to make LLM output trustworthy in a learner-facing tool.

## Next step

1. Improve the deterministic fill text for `filled_missing` drill lines so verifier-injected coaching prose is more section-aware (or use a focused secondary Gemma pass that only rewrites the inserted lines while preserving structure).
2. Add a tiny structural-stats summary cell to `notebooks/09_kizomba_extended.ipynb` (e.g. tracks with zero repairs, max repair count, distribution of `filled_missing`) so future reruns produce a one-line trend instead of requiring manual aggregation.