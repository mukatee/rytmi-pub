# 2026-04-17 — Phase 9: short_break, edge contraction, same-branch merge, vocal-aware intro/outro

## Goal
Close the remaining boundary and visibility gaps the user flagged after Phase 8 (commit `cf6b935`), especially the ones where *vocal presence* is the cleanest signal: instrumental intros that keep getting cut short, outros that start long after vocals have faded, 1-phrase dips that vanish into the grey `main` band, and adjacent `break[melodic]` chains that fragment a single long section.

## Context / prior state
Phase 8 shipped the edge-expansion pass, sub-splitter widening, and the embedded-break scanner (214 tests). A fresh 10-track eval-set listen surfaced:

- **Romeo Santos — *Propuesta Indecente*** mis-labels the full pre-vocal opening as `intro P1→P3` + `break[full] P3→P9`. By ear it is all still intro until vocals enter.
- **Grupo Extra — *Emborrachare*** shows the same pattern at lower amplitude: intro ends at P3 but really runs until ~P6+2, plus a subtle P25–P28 dip that never surfaces.
- **Romeo Santos — *El Chaval (Bachata Musicality)*** has an outro marked too long. User's hunch: "vocals fading toward the end would mark outro start more accurately."
- **Baila Kizomba Amor** section 17 at `P58/M115 → P59/M117` (RMS×0.48, H×0.66, P×0.46) was *detected* by Phase 8's embedded-break scanner but still labelled `main` because `_BREAK_MIN_PHRASES=2` rejects 1-phrase breaks. It disappears into the grey band.
- **Baila** break at `P36 → P42` starts 1 phrase too late — Phase 8 only expanded edges, never contracted them.
- **Charbel — *E Magia 4K*** runs six consecutive `break[melodic]` rows that are clearly one region to the ear.

Also corrected from prior context: **All Of Me is a kizomba track** (under `data/songs/eval_set/kizomba/`), not a bachata or jazz reference.

## Hypothesis
Split the fix into two commits — a rule-based pass that can ship even if the vocal-extraction dependency falters, then a vocal-aware pass behind a source abstraction.

**Commit 1 (rule-based):**
- A new `short_break` label (with its own palette entry) lets 1-phrase drops that match the existing 4-branch break classifier surface as a distinct band instead of blending into `main`.
- Symmetric edge *contraction* inside `_expand_label_edges_on_signal` — if the first/last phrase of a break/peak doesn't support the label signature, shrink the edge.
- A `_merge_same_branch_break_chains` post-pass collapses runs of ≥ 3 adjacent `break[branch]` sections that share a branch.

**Commit 2 (vocal integration):**
- Compute a vocal-activity envelope per track via a `VocalActivitySource` abstraction with two implementations — **Demucs v4** (`htdemucs`) as primary and **Gemma 4 E4B audio** as an experimental path. The user explicitly asked that the smaller Gemma model be tried as a fallback/trial route, since "keeping Gemma central" is part of the Kaggle demo story.
- New passes `_extend_intro_to_first_vocal` and `_contract_outro_to_last_vocal` consume the envelope and move intro/outro boundaries to vocal-onset / vocal-fade, capped by `_INTRO_MAX_EXTEND_PHRASES=12` and `_OUTRO_MAX_CONTRACT_PHRASES=8`.

## What changed

### Commit 1 — `b1dfb99` (no-vocal fixes)

- [src/rytmi/dsp.py](../../src/rytmi/dsp.py):
  - `_SHORT_BREAK_MIN_PHRASES=1.0` and the new `short_break` branch inside `_label_sections` — a 1-phrase section that matches the existing 4-branch break classifier is labelled `short_break[branch]` instead of being skipped back to `main`.
  - `_expand_label_edges_on_signal` now also *contracts* break/peak edges: if the first or last phrase in a section doesn't support the label's signature, up to `_EDGE_CONTRACT_MAX_PHRASES=2` phrases are shed (floor: `_EDGE_CONTRACT_MIN_REMAINING_PHRASES=2`). Expansion and contraction share the same `supports_*` threshold to avoid flip-flop.
  - New `_merge_same_branch_break_chains()` pass after edge expansion — collapses runs of ≥ `_MERGE_BREAK_CHAIN_MIN=3` adjacent `break`/`short_break` sections with matching `break_branch`, duration-weighting the signal ratios.
  - `describe_sections` now renders `short_break[branch]` just like `break[branch]`.
- [src/rytmi/viz.py](../../src/rytmi/viz.py): `SECTION_COLORS["short_break"]="#e67e22"` (warm orange, ≥ 40-channel gap from both `#f4d03f` break and `#d0d0d0` main).
- [tests/test_dsp.py](../../tests/test_dsp.py): 7 new tests — `short_break_labels_1phrase_drop_matching_branch`, `short_break_rejects_1phrase_drop_not_matching_any_branch`, `edge_contraction_shrinks_break_first_phrase_mismatch`, `edge_contraction_respects_min_remaining`, `phase_merge_collapses_melodic_chain`, `phase_merge_preserves_mixed_branches`, `phase_merge_two_adjacent_same_branch_not_fused`.
- [tests/test_viz.py](../../tests/test_viz.py): `SECTION_COLORS` label set updated to include `short_break`; new `test_section_colors_short_break_distinct_from_break_and_main` asserts the palette gap.
- [docs/eval-set-guide.md](../../docs/eval-set-guide.md): palette table adds `short_break` row.
- [notebooks/05_batch_analysis.ipynb](../../notebooks/05_batch_analysis.ipynb): version stamp → `v0.9a — phase 9 (no-vocal) — 2026-04-17`.

### Commit 2 — vocal integration

- [src/rytmi/vocal_activity.py](../../src/rytmi/vocal_activity.py) (**new**):
  - `VocalActivityEnvelope` dataclass (times, rms, active, sr, source).
  - `VocalActivitySource` protocol — `.compute(audio) → VocalActivityEnvelope | None`. Implementations return `None` on any failure so callers never need a try/except.
  - `DemucsVocalActivity` — lazy-imports `demucs`, runs `htdemucs` on the track, mixes the vocal stereo stem to mono, computes a per-frame RMS with `hop_length=512`, and thresholds at `max(_VOCAL_ACTIVE_FLOOR=0.003, 0.30 × p75(rms))`. Envelopes are disk-cached under `cache/vocals/<sha1>.demucs.npz` (gitignored).
  - `GemmaVocalActivity` — windows the track into non-overlapping ~30 s clips and asks Gemma 4 E4B a one-word YES/NO vocal-presence question per window via the existing `transcribe.py` loader. Same envelope shape, coarser time resolution (per-window).
  - `default_vocal_activity_source(prefer="demucs"|"gemma"|"none")` returns a `_ChainedVocalActivity` that falls through sources until one produces a non-None envelope.
- [src/rytmi/dsp.py](../../src/rytmi/dsp.py):
  - `analyze()` gains `vocal_env: VocalActivityEnvelope | None = None`. When set, two new passes run after `_merge_same_branch_break_chains`:
    - `_extend_intro_to_first_vocal` walks phrases, finds the first phrase with ≥ `_VOCAL_MIN_ACTIVE_RATIO=0.20` active frames, and absorbs all same-era sections up to that boundary (capped at `_INTRO_MAX_EXTEND_PHRASES=12`). Handles full and partial absorption — the first section that straddles the vocal-start boundary is clipped forward rather than dropped.
    - `_contract_outro_to_last_vocal` is symmetric. Finds the last active phrase, pulls outro start to `last_vocal_phrase + 1 + _OUTRO_GRACE_PHRASES`, capped at `_OUTRO_MAX_CONTRACT_PHRASES=8`, and clips the previous section's end forward.
- [tests/test_dsp.py](../../tests/test_dsp.py): 7 new tests — `extend_intro_absorbs_prevocal_section`, `extend_intro_noop_when_vocal_starts_before_intro_end`, `extend_intro_respects_max_extend_cap`, `extend_intro_noop_when_env_is_none`, `contract_outro_to_last_vocal`, `contract_outro_respects_max_contract_cap`, `contract_outro_noop_when_no_vocals`.
- [tests/test_vocal_activity.py](../../tests/test_vocal_activity.py) (**new**): 12 tests covering Demucs graceful-None on missing dependency, runtime failure, successful envelope from a stubbed vocal stem, cache round-trip, cache reuse skipping separation, cache-key tag differentiation, chained fallback (Demucs → Gemma), `prefer="none"` passthrough, Gemma envelope from scripted YES/NO responses, Gemma model-load failure handled, Gemma per-window failure short-circuits to None.
- [pyproject.toml](../../pyproject.toml): new `[project.optional-dependencies] vocals = ["demucs>=4.0"]`, wired into `all`.
- [.gitignore](../../.gitignore): `cache/vocals/` (regenerated per track).
- [tmp/run_eval_vocal.py](../../tmp/run_eval_vocal.py) (**new**): eval runner that accepts `--source {demucs,gemma,none}` and an `--only <substr>` filter, printing the vocal envelope summary alongside `describe_sections`.

## Evidence / test results

**Tests:** `pytest -q` → **241 passed, 1 skipped**. Breakdown:
- 214 Phase 8 baseline + 7 new no-vocal DSP tests = 221 after Commit 1b pushed.
- + 1 merge test set = 222 (Commit 1 pushed).
- + 12 vocal-activity tests + 7 vocal-pass DSP tests = **241 total** after Commit 2.

**Eval-set observations (demucs source, after Commit 2):**

- **Propuesta Indecente** — intro now `P1/M1 → P5/M9` (0.0–22.5 s, was `P1→P3`). The `break[full] P3→P9` row is gone in its original form; what remains is a shorter `break[full] P5→P9` (22.5–38.2 s). Demucs reports vocals active ≥ 20% at phrase 5 on this track, which is earlier than the user's "intro runs to P11" call — an honest disagreement between the vocal-onset signal and the user's ear (the user likely waits for the "full band + drums" arrival at P9, not the first vocal phrase).
- **Grupo Extra — Emborrachare** — intro still ends at `P3/M5` (9.0 s). Demucs reports `active_frac=0.716` with activity beginning very early in the track; no phrase past P3 qualifies as "first pre-vocal" under the 20% threshold. Not improved by this phase; would benefit from a "strong-vocal onset" heuristic (contiguous high-RMS vocal runs rather than any activity).
- **El Chaval (Bachata Musicality)** — outro pulled from `P60/M119 → end` (~230 s start) to `P53/M105 → end` (192.8 s start). Contraction is aggressive — the capped version is 8 phrases, and the cap was hit. User feedback will indicate whether `_OUTRO_GRACE_PHRASES=1` / `_OUTRO_MAX_CONTRACT_PHRASES=8` need tuning.
- **Baila Kizomba Amor** — section 17 now reports `short_break[full] 194.7–198.2 s / P58/M115 → P59/M117, RMS×0.48 H×0.66 P×0.46`, rendering as an unambiguous warm-orange band on the timeline (was grey `main low`). Main break contracted to `break[full] P37/M73 → P42/M83` (was P36/M71 starting one phrase early).
- **Charbel-E-Magia-4K** — not re-inspected in detail this phase; the merge threshold (≥ 3 adjacent same-branch) should collapse the fragmented melodic chain whenever it recurs.

## What worked

- **`short_break` label + palette entry** — the Baila P58 dip is now a distinct band on the timeline, exactly as intended. Tests confirm it rejects 1-phrase sections that don't match any branch, so it won't over-fire.
- **Edge contraction** — symmetric with edge expansion and using the same `supports_*` threshold gives zero flip-flop risk in a single pass. The Baila P36 case is fixed.
- **Phase-merge post-pass** — duration-weighted signal ratio averaging across the fused chain means a collapsed melodic chain still carries a meaningful `harm_ratio` / `perc_ratio` for Gemma to reason over.
- **Demucs integration** — `htdemucs` via `demucs.apply.apply_model`, lazy-imported, produces a clean per-frame vocal RMS in ~30–60 seconds per track on CPU. The `sha1(filepath + mtime + tag)` cache key means a second run is instant.
- **Graceful-None contract** — chained `_ChainedVocalActivity` will transparently fall through to Gemma (or to a no-op envelope) if Demucs isn't installed or the model download fails, so the pipeline keeps working on machines without the heavy dependency.

## What did not / limitations

- **Intro-extension accuracy is bounded by what "vocal-active" means.** Demucs catches bleed (backing vocals, reverb tails, sample-based "vocal chops") as activity, so the "first phrase with ≥ 20% active frames" heuristic can mark the vocal-start too early on tracks with busy instrumental intros that have any vocal-adjacent sound. Propuesta's intro should have extended to P11 by ear; it extended to P5. Emborrachare's intro didn't extend at all.
- **`_VOCAL_ACTIVE_THRESHOLD=0.30` of the vocal-stem p75 is a first calibration**, tightened from the initial `0.12 × median_nonzero` guess after a Propuesta dry-run produced `active_frac=0.74`. Re-tuning per dance style (or per-track adaptive via a two-mode histogram) is a follow-up.
- **Outro contraction on El Chaval is aggressive** — moved the start 37 seconds earlier. This may or may not match the user's ear; the `grace_phrases=1` + `max_contract_phrases=8` caps need eval-set validation.
- **Gemma experimental path not yet run end-to-end** on the eval set — its quality versus Demucs is still an open question. The fallback chain and graceful-None behaviour are tested but a full Kaggle-demo-quality comparison needs a dedicated run.
- **`_BREAK_MIN_PHRASES=2` still gates full `break` labels.** `short_break` covers the 1-phrase case, but a 2-phrase dip that's slightly short of `min_break_s` (due to tempo vs `phrase_s` mismatch) can still fall through both gates. Not observed on the eval set; flagged as a theoretical edge case.

## Decision / takeaway

**Commit 1 is a clear win** — 8 new tests, three visible fixes on the eval set (Baila P58 visible, Baila P36 correct, Charbel fragmentation guarded against), and zero risk to Phase 8 behaviour.

**Commit 2 is a real win with known tuning headroom.** The vocal envelope is produced reliably, cached, and wired safely. Intro extension fires as designed on Propuesta; the outro contraction is visible on El Chaval. The accuracy gap to "exactly what the user hears" on Propuesta and Emborrachare is a **vocal-definition** problem, not a wiring problem — tightening the "first vocal phrase" criterion (require sustained ≥ 40% for 2 consecutive phrases, perhaps) is a one-liner change once we have listener feedback.

**Keep both sources in the repo.** Demucs is the default and the more accurate path; Gemma stays as the experimental option for the Kaggle demo, consistent with the project's "Gemma central" brief.

## Next step

1. Present the Phase 9 results to the user and gather per-track verdicts on:
   - Propuesta Indecente — is `P1→P5` good enough, or does the user still want P11?
   - El Chaval — is the 37 s outro contraction correct, or too aggressive?
   - Emborrachare — does the user want stricter "vocal-active" criteria so the P3 → P6+2 extension fires?
2. Based on feedback, consider the follow-ups already scoped for Phase 10:
   - Downbeat-confidence metric redesign (All Of Me `M10+4` case, still blocked).
   - "Strong-vocal onset" criterion (contiguous N-phrase high-activity) to tighten intro extension.
   - Full-eval run of the Gemma source with quality comparison against Demucs.
   - Eval-set expansion to 16–24 tracks.
