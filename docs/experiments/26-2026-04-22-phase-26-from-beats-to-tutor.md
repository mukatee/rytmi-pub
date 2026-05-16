# 2026-04-22 — Phase 26: from kizomba beats to kizomba tutor

## Goal
Phase 25 + 25a delivered a kizomba-tuned beat tracker and a hand-marked
listening-note overlay in `notebooks/06_kizomba_batida_check.ipynb`. The
beats look "quite good" by ear. Phase 26 turns that informal verdict
into a **measurable regression baseline** and adds the **first
learner-facing Gemma surface** for kizomba.

## Context / prior state
- `track_beats(audio, dance_style="kizomba")` shipped in Phase 25 and is
  byte-identical to legacy on non-kizomba paths.
- `_OVERLAY_STEPS` in notebook 06 cell 4 demonstrated that a parser from
  human notation (`"M1+3"`, `"0+2"`) onto onset times worked for a
  living-document set of perceived steps.
- All ground-truth notes were trapped inside the notebook — not loadable
  from scripts, not testable, not a regression source.
- No Gemma surface yet uses the kizomba dance style.

## Hypothesis
1. Lifting listening notes into YAML and the parser into
   `rytmi.eval.listening_notes` makes them reusable from scripts and
   tests without changing the visual notebook output.
2. A windowed beat-vs-note metric (mean-abs-distance + miss/extra
   counts within tolerance, scoped to the time span the notes cover)
   gives a defensible regression baseline that improves with future
   tweaks.
3. A `kizomba_tutor` prompt grounded in **per-section beat clarity**
   produces honest learner notes — including warnings on phases where
   the pulse is genuinely subtle — without trying to name a `"1"`
   (kizomba downbeat is explicitly out of scope).

## What changed
- **B2** Created `data/eval/kizomba_listening_notes.yaml` from the
  notebook 06 dict. Notation documented inline in the YAML.
- **B2** Added `src/rytmi/eval/listening_notes.py` (`load_notes`,
  `notes_to_times`, `find_notes_for_path`, `TrackNotes`). Tests in
  `tests/test_listening_notes.py` (6 cases).
- **B2** Refactored `notebooks/06_kizomba_batida_check.ipynb` to load
  notes from YAML and import the parser. Visualization output is
  unchanged.
- **B4** Added `scripts/eval_kizomba_beats.py` — windowed metric
  (`mean_ms`, `misses`, `extras`) per track. Unit tests for the
  `_nearest_dist` helper in `tests/test_eval_kizomba_beats.py`.
- **A1** Added `tmp/run_phase26_kizomba_check.py` and captured baseline
  output to `tmp/05_kizomba_phase25_check.txt` (kizomba eval set,
  `dance_style=None` vs `dance_style="kizomba"` side-by-side).
- **C5** Added `QUESTION_KIZOMBA_TUTOR` and registered it in
  `ALL_QUESTIONS["kizomba_tutor"]` (`src/rytmi/prompts.py`). Test in
  `tests/test_prompts.py`; updated `tests/test_llm.py` allow-list.
- **C6** Added `notebooks/07_kizomba_tutor.ipynb`: load → analyze →
  per-section beat-clarity table → interactive timeline → Gemma E4B
  via Ollama running `kizomba_tutor` per track.

## Evidence / test results
Baseline metrics on eval tracks with hand-marked notes
(`scripts/eval_kizomba_beats.py`, output in
`tmp/phase26_eval_baseline.txt`):

```
track                                    notes  res beats  mean_ms  miss extra
Baila_Kizomba_Amor                          22   22    20    133.5    13    11
Filomena_Maricoa_-_Teu_Toque_Official_Vi    20   20    22    135.1     8    10
summary (tol=100 ms): mean_ms=134.3  misses=21  extras=21  n_tracks=2
```

`pytest -q`: 355 passed, 1 skipped (was 345 before B2; 9 new tests for
the listening-notes module + script + prompt).

A1 sanity dump: `tmp/05_kizomba_phase25_check.txt`. Section tables on
all 11 kizomba eval tracks compare `dance_style=None` and
`dance_style="kizomba"` side-by-side; no crashes, downstream features
(downbeat offset, sections, energy ratios, vocal-aware boundaries,
break classifier) still produce well-formed output under the new
branch.

## What worked
- Refactor to YAML kept the notebook visually byte-identical (parser
  produces the same purple ✕ marks), confirming the move was a
  pure split.
- Eval script's first run reveals the obvious truth: the listening notes
  are **denser than the tracker beats** (e.g. Baila has 22 notes in the
  window where the tracker reports 20 beats), so the current Phase 25
  tracker is already in roughly the right place but mismatches in *which
  events get a beat* — exactly the kind of diff the metric was supposed
  to surface.
- New `kizomba_tutor` prompt is grounded in `beat: subtle/moderate/clear`
  labels that already live in the analysis prompt block — no extra DSP
  was needed.

## What did not work / limitations
- `mean_ms ≈ 134 ms` is well above the `100 ms` tolerance — the
  eyeball verdict "beats are quite good" is generous. This is a
  baseline, not a result.
- Listening notes only cover the **first ~10 measures** of each track;
  the windowed metric can't say anything about beat quality in
  later sections. Not yet a problem for regression checks but limits
  generalization claims.
- `notebooks/07_kizomba_tutor.ipynb` is wired but **not yet run end to
  end against a live Ollama endpoint** in this session — execution is
  the user's first action.
- `kizomba_tutor` was tuned by reading the prompt; it has not been
  scored against held-out reference coaching text.

## Decision / takeaway
- The listening-notes file is **append-only** ground truth; do not
  retroactively rewrite old marks when later listening updates a feel.
- Treat `mean_ms`, `misses`, `extras` (windowed, tol=100 ms) as the
  Phase 26 baseline. Future tracker tweaks must not regress them on
  Baila + Teu Toque without a written reason.
- Kizomba downbeat / `"1"` detection stays out of scope; the tutor
  prompt forbids naming one.

## Next step
1. Add 1–2 more kizomba tracks to the YAML (especially Bonga, the hard
   one) and re-baseline the eval script.
2. Run notebook 07 against the local Ollama Gemma E4B on Baila + Teu
   Toque + Bonga and capture the responses — verify that `subtle`-tagged
   phases get explicit warnings in the output.
3. If the eval script shows a systematic offset (e.g. tracker beats sit
   consistently early or late), try shifting the kizomba branch's
   `onset_backtrack` cap and measure.
