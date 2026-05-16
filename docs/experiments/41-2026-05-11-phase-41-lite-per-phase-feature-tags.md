# Phase 41-lite — per-phase qualitative feature tags (tried, mixed, off by default)

Date: 2026-05-11
Status: Implemented behind an opt-in flag, A/B'd across all 17 demo tracks,
default flipped back to `False`. Code retained as a switch, not promoted.

## Goal

Post-Phase 40e the demo coaching reads stable but templated. The hypothesis
for Phase 41-lite was that injecting two compact qualitative tags per phase
into the analysis dump — one for **texture** (bass-driven / percussive /
balanced) derived from the average HPSS harm/perc ratios of constituent
sections, and one for **onset density** (sparse / steady / busy) derived
from `avg_rhythm_features.onsets_per_beat` — would give kizomba_tutor and
kizomba_transitions enough additional song-specific signal to break out of
templated phrasing, without changing the schema or running a new analysis
pass.

Read-only DSP, no new computation, behind a flag, no prompt-rule changes
(the existing `_METRIC_GUARD_RULE` already covers translating analysis
values into qualitative language).

## What changed

**`src/rytmi/prompts.py`**
- New `_phase_texture_tag(phase, sections)` — averages `harm_ratio`/
  `perc_ratio` of sections contained in the phase. Returns `"bass-driven"`
  when h/p ≥ 1.3, `"percussive"` when p/h ≥ 1.3, `"balanced"` otherwise.
  Returns `None` and is omitted entirely when no constituent section has
  both ratios populated.
- New `_phase_density_tag(phase)` — from `avg_rhythm_features.onsets_per_beat`:
  `<1.0 → "sparse"`, `<1.8 → "steady"`, else `"busy"`. None when the phase
  has no `avg_rhythm_features`.
- `_format_sections_block` and `format_analysis_prompt` gained an opt-in
  `include_phase_features=False` keyword. When `True`, each phase summary
  line gains `, texture: X, onsets: Y` after the existing `[energy: ...,
  beat: ...]` cluster (each tag omitted independently when the source
  data is missing).

**`src/rytmi/llm.py`**
- `explain_rhythm` and `explain_all` thread the same flag down to
  `format_analysis_prompt`.

**`tests/test_prompts.py`**
- Five new tests covering: off-by-default omits both tags; bass-driven +
  steady; percussive + busy; balanced + sparse; texture omitted gracefully
  when constituent sections lack HPSS ratios while density still appears.

**`notebooks/00_demo.ipynb`, `notebooks/09_kizomba_extended.ipynb`**
- New `INCLUDE_PHASE_FEATURES` flag near `RUN_TRANSITION_RETRY`. Both
  `kizomba_tutor` and `kizomba_transitions` calls thread it through.
  Default is `False`.

## Evidence — A/B across 17 tracks

Notebooks 00 (Filomena) + 09 (full eval + extended kizomba set) re-run
with the flag on, diffed against the post-40e baseline saved as
`*_outputs.post-40e.md`. Programmatic per-prompt summary:

| Prompt | identical | substantive (>5% length) | paraphrase only (≤5%) |
|---|---:|---:|---:|
| listening_guide | 0 | 10 | 7 |
| kizomba_tutor (one-pass) | 0 | 10 | 7 |
| kizomba_tutor (polished) | 0 | 11 | 6 |
| kizomba_drills (verified) | 0 | 5 | 12 |
| kizomba_drills raw Gemma draft | 0 | 10 | 7 |
| kizomba_transitions (verified) | 0 | 8 | 9 |

Verifier-stat movement (the only objective signal):

| Track | Block | Delta |
|---|---|---|
| Baila_Kizomba_Amor | drills | `skipped_lines 7→2`, `filled_missing 7→5` (improvement) |
| Bonga_Mona_Ki_Ngi_Xica | drills | `skipped_lines 7→5`, `filled_missing 4→2` (improvement) |
| Tony_Pirata | drills | `skipped_lines 1→3`, `parsed 5→7` (regression — flagship demo track) |
| Calema_Leva_Tudo | drills | `skipped_lines 2→3` (mild regression) |
| Daniel_Santacruz_Lento | drills | `skipped_lines 7→8` (mild regression) |

Net drills stats: 2 improved, 3 regressed. Transitions verifier stats had
no real movement once the post-40e baseline's missing
`retried` / `retry_succeeded` fields are accounted for.

Qualitative read across the 17 tracks: about 20% of changes feel mildly
positive (slightly more concrete bass references on Filomena / E_Magia),
70% are neutral paraphrase, 10% mild-negative (extra raw-draft lines on
Tony_Pirata, a duplicated duration tag on E_Magia drills).

## What worked

- Plumbing was clean and surgical — three layers (`_format_sections_block`,
  `format_analysis_prompt`, `explain_rhythm`/`explain_all`) plus a single
  boolean flag, no schema change, no new analysis pass.
- Helpers degrade gracefully when source data is missing — no exception
  paths, no fabricated tags. The five tests cover the matrix.
- The A/B was reproducible and quick to repeat: rename baselines to
  `*_outputs.post-40e.md`, flip the flag, re-run, diff.

## What didn't

- Most changes were **paraphrase**, not new content. Gemma reworded
  existing lines using slightly different connectives ("as the
  percussion thickens" → "as the bass line gains density") but the level
  of song-specificity stayed constant.
- The `texture: bass-driven` tag was nearly constant across kizomba
  tracks (the genre is bass-driven and low-percussiveness almost by
  definition), so it added no inter-phase contrast within a song — just
  repeated the same word ~8 times per track. The `_format_distinct_features`
  section was already telling Gemma about low percussiveness at the
  song level, so the new tag was largely redundant.
- The Tony_Pirata drills regression matters more than the Baila/Bonga
  improvements because Tony_Pirata is a flagship demo track. The raw
  Gemma draft inflated from 9 lines to 13 (model split a single `main`
  block into multiple loop entries), forcing the verifier to skip more
  lines.
- Other root causes of templating that the trial did **not** address:
  the kizomba_tutor instruction template itself maps each label to a
  stock action verb (Find/Establish/Sustain/Build/Reset/Return/Close);
  Phase 40c's strict ban on count-based language compresses the
  phrasing space; most kizomba tracks really are musically similar
  (same tempo band, same arc).

## Limitations

- A/B was a hand read, not a metric — no rubric or scoring beyond the
  verifier-stats roll-up.
- Trial only added two tags. Other candidate signals — vocal-activity
  ratio per phase (already computed, not surfaced), per-phase tempo
  drift, per-phase IOI variability — were left for later passes.
- All 17 tracks were kizomba. The `texture: bass-driven` saturation
  problem is genre-specific; the tag may behave differently on bachata
  or salsa where percussion-driven sections are common.

## Decision

- Default flipped to `INCLUDE_PHASE_FEATURES = False` in both notebooks.
- Code retained as an opt-in switch; tests stay green; no rollback.
- The mixed result is captured here so future experiments can build on
  the audit + plumbing without re-deriving them.

## Next step

Try one or more of:

1. **Vocal-activity per phase** — surface `vocal: present | quiet | sparse`
   per phase using the Demucs envelope we already feed into `analyze(...)`.
   Vocals come and go more than HPSS does within a kizomba song, so this
   should produce real inter-phase contrast where the texture tag did not.
2. **Per-phase contrast tags** — emit a tag only when a phase deviates
   from the song-average, not as an absolute label. Guarantees
   inter-phase variation by construction.
3. **Transitions-only retry** — drop the flag from tutor (where templating
   dominates) and keep it only in transitions where each line is short
   enough that one extra adjective might land cleaner.

The Phase 41-lite plumbing makes any of these a small extension rather
than a from-scratch effort.

## Update — Phase 41-D (vocal-activity per phase) tried, same null result

Followed up option 1 above. Added `SongSection.vocal_ratio` populated by
`analyze()` from the existing Demucs envelope (commit `9d7df50`), surfaced
as `vocal: present | sparse | quiet` per phase via an opt-in
`include_phase_vocal=False` flag through `_format_sections_block` →
`format_analysis_prompt` → `explain_rhythm` → `explain_all`. Six new
tests; 476 pass.

A/B reading on the 17-track set gave the same shape as 41-lite: A and B
versions are paraphrases of each other, with no new vocal-aware language
in the kizomba_tutor / kizomba_drills / kizomba_transitions outputs.

Root cause is mechanical and visible in the actual prompt phase blocks:

- Demucs is high-recall. With thresholds 0.55 / 0.20 / <0.20, the tag
  saturates on `present` for almost every phase except `intro`, `outro`,
  and the `break`. Concrete distributions:
  - Filomena: sparse / present×6 / quiet / sparse
  - E_Magia Ben Ana: quiet / present×9 (tag is essentially constant)
  - Tony_Pirata: sparse / present×4 / quiet / sparse / present
  - Daniel Santacruz Lento: quiet / present×9 / sparse
- The tag therefore co-fires with the section label (`intro`/`break`/
  `outro` → low vocals; `main`/`build`/`peak` → present). Gemma already
  has the section label, so the tag adds essentially no new signal.
- Listener ground-truth disagrees with the tag where it matters most:
  on E_Magia Ben Ana §9 (the 141s–163s `break`), the envelope reports
  `vocal_ratio=0.78 → present` but the singer is actually intermittent
  there. This is the saturation bias of frame-level Demucs averaging
  inside a long phrase, not a thresholding fix.

**Same lesson as 41-lite, sharpened**: a per-phase scalar tag whose
values track section labels does not give Gemma something it can
ground new language in. Adding a third such tag to the prompt does
not help.

Default `INCLUDE_PHASE_VOCAL` flipped to `False` in both notebooks.
Code, tests, and `vocal_ratio` field retained — the field itself is a
useful primitive for future work that consumes vocal activity in less
saturated ways.

### What looks more promising next

- **Vocal-state transitions as the salient signal**, not a per-phase
  static tag — e.g. "vocals enter for the first time at T2", "vocals
  drop out for 8s during P5". Boundary events break the saturation
  problem because they cannot co-fire with section labels by
  construction.
- **Per-section lyric / language snippets** from the existing
  `transcribe_vocals` pipeline — actual song-specific words won't
  co-vary with section labels.
- **Vocal-onset-aware section boundaries** — listener feedback on
  Charbel official "E Magia" notes the `intro` label ends roughly a
  phrase earlier than where the vocals actually start, then is
  followed (oddly) by a `break` that is itself vocal-active. Using
  the vocal envelope as a boundary cue alongside energy might
  produce more musically intuitive section labels. This is a DSP
  improvement, not a prompt-tag improvement.
- **Gemma audio model on short excerpts** — biggest potential value
  and biggest engineering cost; speech-oriented support on `E2B`/
  `E4B` may or may not yield useful music-structure signal.

The deeper takeaway worth carrying forward: cheap per-phase scalar
tags shoot below the bar of what Gemma needs to write song-specific
language. The next swing should target signals that vary
*independently* of the section label — boundary events, lyric
content, or actual audio understanding.
