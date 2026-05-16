# Phase 42 — Vocal-Active Break Demotion

**Date:** 2026-05-12
**Status:** Shipped (default-on)
**Branch:** main

## Goal

Fix a recurring section-labelling bug surfaced by the user: tracks where the
section right after the intro (or one immediately following a peak) gets
labelled `break` / `short_break` even though the **vocalist is clearly
present**. Charbel "E Magia" was the canonical case — a `break 35.9–51.2 s`
with `vocal_ratio = 0.74` immediately after a clean instrumental intro.

A break with the singer present is, by Rytmi's own dancer-facing definition,
not a break. Surfacing it as one is musically misleading and contradicts the
prompt's own framing of breaks as "instrumental thinning / breakdown" cues.

## What changed

New post-pass `_demote_vocal_active_breaks(sections, vocal_env)` in
[src/rytmi/dsp.py](src/rytmi/dsp.py), wired into `analyze()` right after the
existing vocal-aware helpers (`_extend_intro_to_first_vocal`,
`_contract_outro_to_last_vocal`, `_relabel_vocal_drop_instrumentals`).

Rule:

- Section label is `break` or `short_break`.
- `vocal_ratio` over the section ≥ 0.50 (singer present at least half the
  time).
- `energy_level` is **not** `low` (real kizomba/bachata vocal-led breaks thin
  the band — the energy gate keeps those intact).

When all three hold, the section is relabeled `main` and `break_branch` is
cleared. Conservative: only fires when `vocal_env` is available.

This is the **symmetric counterpart** of Phase 10's
`_relabel_vocal_drop_instrumentals`, which carves vocal-quiet runs *out of*
`main`/`peak` blocks. Phase 42 catches the inverse failure mode.

## Evidence — before vs after

Audit on 4 kizomba eval tracks (Demucs vocal envelope, default config):

| Track                | Section            | Before               | After                |
| -------------------- | ------------------ | -------------------- | -------------------- |
| E_Magia OFFICIAL     | 35.9–51.2 s, v=0.74 | `break` (E=medium)   | **`main`** ✅         |
| E_Magia OFFICIAL     | 164.7–186.5 s, v=0.76 | `break` (E=low)      | `break` (preserved)  |
| E_Magia Ben_Ana      | 17.3–22.8 s, v=0.68 | `short_break` (E=medium) | **`main`** ✅     |
| E_Magia Ben_Ana      | 140.9–163.2 s, v=0.78 | `break` (E=low)      | `break` (preserved)  |
| Filomena             | 138.2–149.0 s, v=0.00 | `break` (E=low)      | `break` (preserved)  |
| Tony_Pirata (same)   | 138.2–149.0 s, v=0.00 | `break` (E=low)      | `break` (preserved)  |

The energy gate proved essential: both E_Magia tracks have **legitimate**
vocal-led breaks mid-song (band thins, singer continues over sparse
percussion). Demoting those would be the opposite mistake.

## What worked

- Reusing the existing `_phrase_active_ratio` primitive (no new envelope
  ops).
- Energy gate (`energy_level != "low"`) cleanly separates the two failure
  modes — pure DSP, no per-track tuning needed.
- All 476 prior tests still pass; +6 new unit tests for the helper (482
  total).

## Limitations

- Threshold `0.50` is a single hand-picked number; not stress-tested against
  all dance styles. Bachata/salsa eval recommended before declaring it
  universal.
- `energy_level == "low"` is a coarse 3-bucket signal; a future iteration
  could use a continuous RMS ratio for more nuance.
- Doesn't try to *create* missing breaks where the labeler missed them —
  only fixes false positives.

## Next step

If A/B on bachata/salsa shows the same shape of fix is correct there,
consider lowering the threshold to 0.40 (more aggressive) or wiring the
ratio into the prompt as evidence ("vocals present 78 % of section, label
adjusted from `break` to `main`").

## Files touched

- [src/rytmi/dsp.py](src/rytmi/dsp.py) — `_demote_vocal_active_breaks`,
  Phase 42 constants, `analyze()` wiring.
- [tests/test_dsp.py](tests/test_dsp.py) — 6 new unit tests covering the
  positive case, the energy-gate carve-out, the no-vocal case,
  `short_break`, the `vocal_env=None` no-op, and the non-break-label no-op.
