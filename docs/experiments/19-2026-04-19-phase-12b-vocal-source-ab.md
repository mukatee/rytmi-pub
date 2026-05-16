# 2026-04-19 — Phase 12 (Commit B): demucs vs gemma vocal source A/B verdict

## Goal

Decide whether `VOCAL_SOURCE = "gemma"` — the Gemma 4 E4B per-window audio-classifier vocal-activity source — should (a) become the recommended default, (b) stay in-tree as opt-in experimental, or (c) be removed. Demucs has been the default since Phase 9; the gemma branch was kept alive through Phase 11 under the "Gemma central" Kaggle-demo framing, without a grounded listening comparison.

## Context / prior state

Phase 9 introduced the `VocalActivitySource` protocol with two concrete implementations in [src/rytmi/vocal_activity.py](../../src/rytmi/vocal_activity.py):

- `DemucsVocalActivity` — htdemucs stem extraction → per-frame RMS → `max(0.003, 0.30 × p75(rms))` threshold with 3 s smoothing (Phase 11 v2).
- `GemmaVocalActivity` — windowed ~30 s audio clips handed to Gemma 4 E4B multimodal with a one-word YES/NO vocal-presence prompt.

Both drive the same downstream vocal-aware passes (`_extend_intro_to_first_vocal`, `_contract_outro_to_last_vocal`) via `default_vocal_activity_source(prefer=...)`. Phase 11 re-ran the 10-track eval set in three configurations and archived the outputs to [tmp/](../../tmp/):

| Archive | Reasoning model | Vocal source |
|---|---|---|
| `05_batch_analysis.phase11-main.txt` | `gemma4:e4b` | `demucs` |
| `05_batch_analysis.phase11-gemma-vocal.txt` | `gemma4:e4b` | `gemma` |
| `05_batch_analysis-26B.phase11.txt` | `google/gemma-4-26b-a4b-it` | `demucs` |

Only the first two matter for the vocal-source decision. The 26B archive is reserved for a separate reasoning-model evaluation.

## Hypothesis

If gemma's per-window audio classifier catches vocal transitions that demucs's stem-RMS envelope smooths over, then gemma should produce a **more faithful** section set on the eval tracks — not merely a finer one. "More faithful" means: when gemma introduces extra section boundaries (versus demucs), those boundaries correspond to real audible vocal-presence changes.

## Method

### Scripted diff

Section-count per track, both variants:

| Track | demucs N | gemma N | Δ |
|---|---|---|---|
| Baila Kizomba Amor | 28 | 36 | +8 |
| Grupo Extra — Me Emborrachare | 18 | 25 | +7 |
| Charbel E Magia — Official 4K | 18 | 24 | +6 |
| All Of Me | 20 | 25 | +5 |
| Tony Pirata | 18 | 23 | +5 |
| Bachata Musicality 12 | 18 | 20 | +2 |
| Romeo Santos — Canalla | 20 | 22 | +2 |
| Charbel E Magia — Ben & Ana cut | 14 | 16 | +2 |
| Filomena — Teu Toque | 18 | 20 | +2 |
| Romeo Santos — Propuesta Indecente | 24 | 24 | 0 |

All ten deltas are ≥ 0 — gemma only ever adds sections, never removes them. This makes the question binary: the extras are either real audible events (→ promote gemma) or noise (→ keep demucs).

### Listening pass (top 3 hotspots by |Δ|)

Rather than re-listening to all 10 tracks, the decision was resolved on the three largest-delta tracks plus awareness of the mid-delta tracks as tiebreakers. All timestamps below are as the user heard them in the source audio.

## Evidence / test results

### Hotspot 1 — Baila Kizomba Amor, ~180–195 s

- **Demucs:** single `main` block spanning the region.
- **Gemma:** 5 micro-sections alternating `instrumental` / `main`.
- **User verdict:** neither variant is fully correct. The region is genuinely instrumental (no singing, no lyrics) until P68 — demucs is too permissive calling it `main`, but gemma's alternation is **off by ~8 counts** in several places:
  - S12 labelled `main` is actually instrumental.
  - S13 labelled `instrumental` contains only 8 beats of real main before reverting.
  - S16 labelled `instrumental` is still singing up to P63.
- Demucs additionally misses that P75 → P78+6 should stay instrumental (classifies it `main` while no singing is present).

### Hotspot 2 — Grupo Extra — Me Emborrachare, ~21–95 s

- **Demucs:** smooth `main` across the whole 75 s region.
- **Gemma:** 4 inserted `instrumental` blocks at 21–37 s, 45–60 s, 60–72 s, 80–95 s.
- **User verdict:** gemma's inserted instrumentals are **false positives** — singing is constant through most of the 21–95 s range. Around M48–M92 gemma appears to **flip main ↔ instrumental wholesale** (labels `instrumental` where singing is clearly present, `main` where the brief instrumental window M52+3 → M56 actually is). Demucs misses that M52+3 → M56 instrumental window, but its `main` labelling elsewhere is correct.

### Hotspot 3 — Charbel E Magia — **Official** (full song, not the Ben & Ana cut), ~47–60 s and ~131–152 s

> Important: the eval set contains two versions of this track — the Official full-song video and a Ben & Ana cut that starts mid-song. Timestamps in this hotspot are from the Official version only.

- **Demucs:** unjustified `break` label spanning M31 → M47 with steady singing + beat throughout, then `build` at M47 (singer picks up), then again unjustified `break` around ~131–152 s.
- **Gemma:** keeps the first region labelled `intro`, then fires `break[melodic]` at M35/P18 followed by a long `instrumental` stretch where singing is clearly continuing.
- **User verdict:** both variants are wrong, but in different ways. Crucially, the `break` false positives are **not a vocal-source issue** — both demucs and gemma fire them, so the cause is the novelty-based break detector over-segmenting on soft-melodic kizomba signal profiles with steady vocal and beat. This behaviour should be addressed in a separate Phase 13 pass on break-detection thresholds, not by changing the vocal-source default.

### Decision matrix

| Track (hotspot) | Demucs accuracy | Gemma accuracy | Which is better? |
|---|---|---|---|
| Baila 180–195 s | too permissive (labels instrumental as main) | off-phase by ~8 counts, labels flipped | roughly tied; both imperfect, but gemma's phase error is harder to trust |
| Grupo Extra 21–95 s | misses one real instrumental drop | main ↔ instrumental flipped across large region | **demucs** — being too smooth is less misleading than being actively wrong |
| Charbel Official 47–60 s + 131–152 s | unjustified breaks | same unjustified breaks + wrong instrumental labels | **demucs** on labels where they differ; break FPs are not vocal-source-caused |

## What worked

- The scripted section-count delta table gave a clean binary framing (gemma only ever adds) so the listening pass didn't need to cover all 10 tracks. Three hotspots settled it.
- Separating the **break-false-positive** finding on Charbel Official from the **vocal-source** finding cleanly — both variants fire those breaks, so that failure mode belongs in Phase 13 DSP work, not in this commit.

## What did not / limitations

- **Listening pass was three tracks deep, not ten.** The mid-delta tracks (All Of Me and Tony Pirata at +5, four tracks at +2) were not audited by ear. If a future listener finds gemma's extras are real on those tracks, the verdict could soften — but for that to overturn this decision, gemma would need to be *clearly* better on ≥ 6/10 tracks, and the top-3 listening already shows it's wrong in structurally similar ways on the hardest cases.
- **Gemma's failure mode looks fixable, not fundamental.** The off-by-8-counts phase shift on Baila and the main ↔ instrumental flip on Grupo Extra both smell like a windowing-offset or threshold-polarity bug in `GemmaVocalActivity`, not noise in the Gemma classifier itself. That fix is its own research pass — see Phase 13 seeds below.
- **Demucs is not perfect either.** User flagged at least two genuine instrumental drops demucs misses (Grupo Extra M52+3 → M56; Baila P75 → P78+6). The vocal-RMS threshold `max(0.003, 0.30 × p75(rms))` or the 3 s smoothing window may be too permissive for brief drops.
- **No synthetic-signal ground-truth evaluation.** We're calling the verdict by listening, not by a metric. A future validation on a synthetic track with known vocal/silence windows would quantify both sources' accuracy.

## Decision / takeaway

**Demote `GemmaVocalActivity` from "experimental fallback that keeps the story" to "opt-in experiment, not recommended for default."**

- `default_vocal_activity_source(prefer="demucs")` stays the default.
- Gemma stays in-tree — the code works and the Kaggle demo's "Gemma central" narrative benefits from having a Gemma-native vocal source available — but docs, docstrings and the notebook comment now explicitly flag that gemma is known to flip main ↔ instrumental and to drift by ~8 counts on some tracks, so users don't adopt it expecting an upgrade.
- No code behaviour change in this commit. No test changes.

## Next step — Phase 13 seeds (not acted on in Commit B)

Three distinct follow-ups surfaced by the listening pass. Each is its own phase/commit; none is in scope for Phase 12.

1. **Gemma classifier phase/polarity bug.** Investigate whether the off-by-~8-counts pattern on Baila and the main ↔ instrumental flip on Grupo Extra stem from a windowing offset or label-polarity issue in `GemmaVocalActivity`. Reproduce on a synthetic clip with known vocal/silence alternation, then patch. If fixed, re-run this A/B.
2. **Demucs under-detection of brief instrumental drops.** User flagged Grupo Extra M52+3 → M56 and Baila P75 → P78+6 as genuine no-singing windows demucs misses. Revisit the `max(0.003, 0.30 × p75(rms))` threshold and the 3 s smoothing window with a targeted synthetic-silence-injection test.
3. **Charbel E Magia Official novelty-based break false positives.** Unjustified `break` labels at M31 → M47 and ~131–152 s are **not vocal-source-caused** (both variants fire them). These timestamps are on the Official full-song track; the eval set also contains a `Charbel_E_Magia_Ben_Ana` cut with different timestamps — any investigation should reproduce on the Official track first. Possible fix: raise the break-fire threshold, or add a "break requires RMS/novelty drop AND vocal drop" conjunction to suppress breaks on soft-melodic kizomba with steady vocal + beat.
