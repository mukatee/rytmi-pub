# 21 — Phase 13 Commit B2: Gemma E4B downbeat tiebreaker

**Date:** 2026-04-19
**Scope:** New module `src/rytmi/gemma_downbeat.py` + 13 unit tests + eval-pass diagnostic on the 16-track eval set.
**Status:** **Negative result.** Gemma E4B voted NO on every candidate offset for every below-gate track (52/52). The tiebreaker consistently no-ops; no track flipped offset or gained confidence. Keep the module in place as a diagnostic / future prompt-iteration scaffold; shift the Phase-13 recovery path to Phase 14 preprocessing (HPSS-percussive / Demucs drum-stem signals).

## Goal

Lift the three kizomba tracks that Commit A2 left stuck at `≤ 0.04` downbeat
confidence (Baila, Filomena Teu Toque, All Of Me) above the `0.25` gate by
adding a small-model audio judgment from Gemma E4B, used strictly as a
tiebreaker on DSP estimates in the ambiguity band.

## Context / prior state

Commit A2 shipped the adaptive safe-vs-full template fusion and restored
the Phase-11 baseline on confident tracks (note 20). It could not move the
three target kizomba tracks — their kick-band signal itself doesn't
correlate with any of the templates, so no DSP-signal reweighting helps.
See note 20 § "Decision / takeaway" for why a new signal source — not a
different template — was the right response.

Phase 11's plan FU-1b already flagged a Gemma-as-tiebreaker path as the
alternate route; Commit B2 implements it.

## Hypothesis

Gemma E4B, even with its speech-oriented audio front-end, can do better
than chance at "does this clip *start* on a musical beat-1" for a
fixed-length clip. We don't need it to be strong on music; we need it to
contribute **one usable bit of information** on top of a DSP signal that
is already *in the ambiguity band*. If Gemma can cast a single YES on one
of four candidate offsets, that flips the grid away from `beat[0]`
default; if it votes YES on multiple offsets, DSP still decides.

## What changed

- New module [`src/rytmi/gemma_downbeat.py`](../../src/rytmi/gemma_downbeat.py):
  `refine_downbeats_via_gemma()` + `DownbeatTiebreakResult` dataclass +
  private `_candidate_clip_window()` / `_query_gemma_downbeat()`.
- **Per-offset prompt** (fixed, all-caps emphasis to bias YES/NO compliance):
  > Listen to this short music clip. Does this clip **START** on a strong
  > musical beat that sounds like the **BEGINNING** of a measure or musical
  > phrase (the "1" in "1-2-3-4")? Answer with one word: YES or NO.
- **Clip layout:** 8 beats starting at the first eligible beat with that
  offset (~2 measures at 120 BPM, comfortably inside Gemma's ~30-s audio
  window). All four candidate clips start in the same region of the song
  so their judgments stay comparable.
- **Combination logic** (interpretable rather than probabilistic):
  - 0 YES → leave DSP.
  - 1 YES matching DSP → endorse, confidence = `max(0.30, dsp_conf)`.
  - 1 YES at a *different* offset → switch to Gemma's pick at fixed `0.30`.
  - Multi-YES with DSP among them → endorse DSP.
  - Multi-YES without DSP → ambiguous → leave DSP.
  - Any per-offset query failure → bail out with `fired=False`; preserve
    the partial vote vector for diagnostics.
- **Fail-soft guards** (all are no-ops, `fired=False`): missing
  processor / model, DSP confidence outside `[0.0, 0.25)`, fewer than
  `beats_per_measure + clip_beats` total beats.
- **No public API change.** `detect_downbeats()` signature is unchanged;
  the tiebreaker is an opt-in call layered on top by the caller.
- **13 new unit tests** in [`tests/test_gemma_downbeat.py`](../../tests/test_gemma_downbeat.py)
  covering every branch. Full suite: **310 passed, 1 skipped.**

## Evidence — DSP vs Gemma-refined

_Captured via `python tmp/run_b2_eval.py --pause 20`, log at
`tmp/b2_eval.log`. Tracks at/above the `0.25` gate shown as `DSP only`
(Gemma skipped for cost); below-gate tracks get queried and show
`DSP→Gem` with per-offset votes._

| Track | DSP (off, conf) | Gemma votes (offsets 0, 1, 2, 3) | Refined (off, conf) | Moved above gate? |
|---|---|---|---|---|
| bachata / Romeo Santos — Propuesta | (2, 0.181) | `N, N, N, N` | (2, 0.181) | ❌ no change |
| bachata / Grupo Extra — Me Emborrachare | **above gate — DSP only** | — | (2, 0.281) | was ✅, stays ✅ |
| kizomba / **All Of Me** (target) | (3, 0.040) | `N, N, N, N` | (3, 0.040) | ❌ no change |
| kizomba / **Baila Kizomba Amor** (target) | (2, 0.017) | `N, N, N, N` | (2, 0.017) | ❌ no change |
| kizomba / **Filomena Teu Toque** (target) | (3, 0.027) | `N, N, N, N` | (3, 0.027) | ❌ no change |
| kizomba / Tony Pirata Teu Toque (cut) | (3, 0.004) | `N, N, N, N` | (3, 0.004) | ❌ no change |
| kizomba / Anselmo Ralph — Curticão | (2, 0.038) | `N, N, N, N` | (2, 0.038) | ❌ no change |
| kizomba / Bonga — Mona Ki Ngi Xica | (3, 0.184) | `N, N, N, N` | (3, 0.184) | ❌ no change |
| kizomba / Criola | (0, 0.008) | `N, N, N, N` | (0, 0.008) | ❌ no change |
| kizomba / Don Kikas | (3, 0.053) | `N, N, N, N` | (3, 0.053) | ❌ no change |
| kizomba / Mika Mendes (cabo) | (2, 0.045) | `N, N, N, N` | (2, 0.045) | ❌ no change |

Above-gate count, 16-track eval set:
- Before B2: **6 of 16** (Commit A2 baseline — Bachata Musicality 12,
  Canalla, Grupo Extra, Charbel Ben-Ana, Charbel Official, Prince Royce).
- After B2: **6 of 16** — identical.
- Offsets flipped: **0**.
- Total below-gate Gemma queries: 10 tracks × 4 offsets = **40 queries, all NO**.
  (Log also shows an extra 12 NOs on `Gemma-refined` rows that fire
  beyond the strict 10 — total Gemma audio calls this run ≈ 52.)

## What worked

- **The fail-soft design did its job.** Every combination-logic branch
  that matters for this negative result (all-NO → leave DSP alone) kept
  DSP's answer intact with no confidence distortion. If the prompt were
  over-confidently saying YES on every candidate the result could have
  been a regression; instead it's a clean null.
- **The module stays small and self-contained.** 262 lines of production
  code, no `dsp.py` surface-area change, no notebook surgery. Re-using it
  after a prompt rewrite costs nothing.

## What did not / limitations

- **Gemma E4B refused to say YES on any candidate offset for any
  below-gate track.** 52 consecutive `no`-parsed responses. The most
  likely explanations, in priority order:
  1. **Speech-oriented audio front-end** (called out in CLAUDE.md):
     Gemma 4 E4B's multimodal audio path was trained primarily on
     speech, not music. Asking "does this clip start on a measure-1" may
     simply be outside its competence — it defaults to NO as the safer
     answer under uncertainty.
  2. **Prompt over-constraint.** The all-caps `START` / `BEGINNING` with
     a specific numeric anchor (`"1"` in `"1-2-3-4"`) may push the model
     toward NO when it's not sure. A more permissive question ("does
     this clip's first moment feel like the start of a musical phrase,
     or does it feel mid-phrase?") might produce a richer distribution.
  3. **Clip choice.** `_candidate_clip_window()` picks the *first*
     eligible window, which on most eval tracks is inside the intro.
     Intros often lack the rhythmic density that would let any listener
     (human or model) pin down beat-1. A later clip from the main
     section might produce better judgments.
  4. **Fixed ~4 s clip length.** 8 beats at ~105 BPM ≈ 4.6 s; at
     slower kizomba tempos this can shrink below what Gemma's audio
     encoder finds informative.
- The tiebreaker only fires inside the `[0.0, 0.25)` ambiguity band — by
  design. It cannot rescue tracks where DSP is confidently wrong, nor
  does it move tracks already above the gate.
- Per-track cost: ~4 Gemma audio inferences plus one model load. Even
  when the signal is useless this is a real cost in a power-constrained
  environment, so we should not wire B2 into the main notebook flow as-is.

## Decision / takeaway

- **Do not wire B2 into `analyze()` / the notebook flow.** On this eval
  set it adds GPU cost for zero signal. The conservative combination
  logic made sure there's no regression risk, but there's no upside
  either.
- **Keep the module.** `src/rytmi/gemma_downbeat.py` plus its 13 unit
  tests stay in — the code is small, self-contained, covered, and easy
  to revive after any of the prompt / clip / model changes listed above.
- **Shift Phase-13 recovery to Phase 14 preprocessing** (the user's own
  suggestion, flagged in note 20). HPSS-percussive-only fusion or a
  Demucs drum-stem-fed kick/onset would give us a cleaner DSP signal on
  kizomba *without* relying on a small multimodal model's music
  judgment. Preprocessing is a one-time cost per track and doesn't
  change the user-facing audio.

## Next step

- **Phase 14 (next commit) — preprocessing-fed DSP.** Either:
  1. **HPSS-percussive pass:** run `librosa.effects.hpss(margin=...)`
     and compute kick-band + onset signals on `y_perc` instead of raw
     audio. Near-zero new dependency (HPSS is already used for section
     features). Cheap enough to always run.
  2. **Demucs drum stem:** richer signal than HPSS but adds ~30 s /
     track. Good to A/B against the HPSS variant on the same eval set.
- **Do not commit further prompt-tuning on B2 in this phase.** If Phase
  14 lifts the stuck tracks, we close the Phase-13 story. If it
  doesn't, we revisit B2 with one targeted prompt-variant comparison
  before discarding the Gemma-tiebreak angle entirely.
- **No notebook change needed for this commit.** The only artifacts are
  this note, the `gemma_downbeat.py` module + tests (already landed),
  `tmp/run_b2_eval.py` + `tmp/b2_eval.log` (diagnostic), and the README
  index line.
