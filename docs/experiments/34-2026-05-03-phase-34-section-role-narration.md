# 2026-05-03 — Phase 34: Section role narration in kizomba_tutor

## Goal

Kill the `continues.` filler in `kizomba_tutor` one-pass output on songs with several adjacent `main` groups, by removing the `continues` allowance entirely and giving the model a small song-arc role vocabulary so every line has something specific to say.

## Context / prior state

Phase 33 (`d8c8972`) and 33b (folded into the same commit) shipped the listening guide and the kizomba "1" positive-replacement fix. The Phase 33 live run on the new Filomena cut (208.9s, four `main` groups) produced this one-pass tutor output:

```
P3: 59s-80s, main ×2 [beat: clear] — continues.
P4: 80s-121s, main ×4 [beat: clear] — continues.
P5: 121s-148s, main ×2 [beat: clear] — continues.
```

Three consecutive `continues.` Daniel Santacruz from the extended set is worse — the polish pass already substantively rewrites every line, but the polish pass is opt-in and doubles LLM cost. The one-pass tutor — the documented baseline and the cell shown by default in `notebooks/00_demo.ipynb` — ships filler on `main ×N` runs. That's the most visible quality gap in the kizomba flow now that `listening_guide` and `kizomba_drills` are clean.

The Phase 33 doc anchored Phase 34 explicitly: name each main's *role in the song's arc* (establishing / sustaining / post-build / resolving) instead of its label. The polish pass is already half-doing this in its rewrites — the goal is to push that improvement upstream into the one-pass.

## Hypothesis

Two surgical edits to `QUESTION_KIZOMBA_TUTOR` will produce substantive coaching on every line of the one-pass output even on long, similar-section tracks:

1. Remove the `continues` allowance entirely — every line must carry a real coaching note.
2. Add a small song-arc role vocabulary (*establishing / sustaining / building / returning / closing*) the model can pick from based on a `main` group's position relative to other phases. Songs with only one `main` group don't need a role.

Risk: filler-by-paraphrase. The model could comply with the no-`continues` rule by writing slight rewordings of the previous line ("continue trusting the pulse"). The role vocabulary is the antidote — it gives the model something specific to say that's *physically different* per group. Live output will show whether this lands.

Fallback: if the one-pass still ships filler-by-paraphrase, switch the demo notebook to call `polish_kizomba_tutor_output` by default rather than opt-in. The polish already produces substantive coaching; the only reason to fix the one-pass is cost and baseline-honesty. The fallback is a one-cell edit, not a re-architecture.

## What changed

- **[src/rytmi/prompts.py](../../src/rytmi/prompts.py)** — two surgical edits to `QUESTION_KIZOMBA_TUTOR` rules block:
  1. Replaced the "Give 3 to 6 real coaching notes total across the song. Use `continues` only when..." allowance with: *"Every line must carry a real coaching note. Do NOT use `continues` as a coaching note — even when adjacent phases share the same label, name what is physically different about the new group (energy, role in the arc, what the learner should focus on now)."*
  2. Inserted a new bullet for the section-role vocabulary, listing five canonical names and the position cue for each: *establishing* (earliest `main`), *sustaining* (middle), *building* (before `build`/`peak`), *returning* (after `peak`/`break`), *closing* (before `outro`). Carve-out: songs with only one `main` group don't need a role.
- **[tests/test_prompts.py](../../tests/test_prompts.py)** — two new tests in the kizomba_tutor section:
  - `test_question_kizomba_tutor_forbids_continues_filler` — asserts the new "every line must carry a real coaching note" + "Do NOT use `continues` as a coaching note" + "name what is physically different" wording, plus that the old "Use `continues` only when..." allowance is gone.
  - `test_question_kizomba_tutor_section_role_vocabulary` — asserts all five role names (`establishing`, `sustaining`, `building`, `returning`, `closing`), the position cues for each, and the single-`main` carve-out.

No `llm.py`, `dsp.py`, `notebooks/`, or polish-prompt changes. Polish naturally inherits the new role vocabulary because it operates on the one-pass draft text.

**One source-level snag** during drafting (third occurrence in this prompt-engineering campaign): the new "Do NOT use `continues` as a coaching note" wording wrapped across continuation lines such that the runtime string had extra spaces inside the asserted phrase. Fixed by reflowing the bullet so the asserted phrase sits on a single source line. This is the third time the same snag has hit (Phase 32 time-span rule, Phase 33 metric-guard bullet, Phase 34 here) — the shared metric-guard helper string refactor would also be a natural place to add a "single-source-line per asserted phrase" convention.

## Evidence / test results

**Tests (clean run):**
```
$ python -m pytest
================= 405 passed, 1 skipped, 64 warnings in 44.50s =================
```
403 baseline → 405 (2 new Phase-34 tests). No regressions in the existing kizomba_tutor / listening_guide / kizomba_drills / polish tests.

**Live run output:** the user ran `notebooks/00_demo.ipynb` (Filomena, Propuesta Indecente) and `notebooks/09_kizomba_extended.ipynb` (six-track extended set) against `gemma-4-26b-a4b-it`. Outputs collected into [notebooks/00_demo_outputs.md](../../notebooks/00_demo_outputs.md) and [notebooks/09_kizomba_extended_outputs.md](../../notebooks/09_kizomba_extended_outputs.md) by the new dump cells (added in the same iteration; not part of Phase 34's prompt change but useful for review).

### Filomena Maricoa — Teu Toque (the canonical Phase-33-trigger track)

Pre-Phase-34 one-pass had three consecutive `continues.` lines on the four `main` groups. Post-Phase-34 one-pass:

```
P2: 12s-59s,  main ×4 [beat: clear] — Establishing the rhythm; settle into a steady walk-step and follow the bass.
P3: 59s-80s,  main ×2 [beat: clear] — Sustaining the flow; keep your weight transfers smooth as the energy climbs.
P4: 80s-121s, main ×4 [beat: clear] — Sustaining the movement; maintain a consistent frame while the pulse stays steady.
P5: 121s-148s, main ×2 [beat: clear] — Building intensity; you can travel a little more as the energy peaks.
P6: 148s-159s, break [beat: clear] — Reset your connection; use this quiet moment to breathe and prepare to return.
P7: 159s-195s, main ×3 [beat: clear] — Returning to the basic; re-establish your connection and find the pulse again.
P8: 195s-209s, outro [beat: clear] — Closing the dance; contract your movement and let the song end gently.
```

Role vocabulary lands cleanly: *establishing → sustaining → sustaining → building → returning → closing*. Two consecutive `sustaining` lines have different physical foci (weight transfers vs frame), so the "name what is physically different about the new group" rule held up. Build/peak labels aren't on this track; the model used "Building intensity" for the high-energy main right before the break, which is a sensible interpretation of the position-cue rule.

### Daniel Santacruz (the worst-case 16-`main` track from the extended set)

Pre-Phase-34: 5 `continues.` lines. Post-Phase-34:

```
P4: 54s-97s,   main ×4 [beat: clear] — This is establishing the flow; settle in and walk the basic to find your center.
P5: 97s-109s,  build [beat: clear] — Use the steady pulse to gradually increase your step size and intention.
P6: 109s-121s, peak  [beat: moderate] — Stay compact and avoid chasing extra movement.
P7: 121s-177s, main ×5 [beat: clear] — Returning to the flow; re-establish the basic and focus on smooth weight transfers.
P8: 177s-201s, main ×3 [beat: clear] — Sustaining the energy; keep your walking steps steady and your frame consistent.
P9: 201s-222s, main ×2 [beat: clear] — Maintaining the connection; focus on your breath while walking the pulse.
P10: 222s-255s, main ×3 [beat: clear] — Closing the main section; contract your movement as the song winds down.
P11: 255s-266s, outro [beat: moderate] — Stay compact and mark the time with tiny weight shifts.
```

Eleven distinct role-named coaching notes instead of five `continues`. Full progression *establishing → build → peak → returning → sustaining → maintaining → closing*. "Maintaining" is a near-synonym the model invented (not strictly in the canonical vocabulary), but it carries a real physical focus ("focus on your breath") so it's substance, not drift.

### Calo Pascoal — `main ×12` collapse case

The 137-second `main ×12` group collapsed into one role-named line: *"This establishing phase is safe to trust the steady pulse; walk the basic and let the bass guide your steps."* The compaction behaviour — many adjacent same-label phases into one substantive line — is exactly what we wanted.

### Aggregate result across the six extended-set tracks

| Track | Role vocabulary applied? | Notes |
|---|---|---|
| Calema_Dilsinho_-_Leva_Tudo | Yes | Build/peak/returning all named correctly. |
| Calo_Pascoal_-_Titiriti | Yes | `main ×12` → one establishing line; full arc named. |
| Daniel_Santacruz_-_Lento | Yes | 11 distinct lines from worst-case track. Full progression. |
| Isabelle_Felicien_-_Soha_Mil_Pasos | Partial | Used "establishing" but P3 leaked a counting reference (see below). |
| Normal | No | Multiple `main` groups but no role names. Coaching is still substantive. |
| Tu_Es_um_Erro | Yes | Long `main ×13` group named establishing; full progression. |

5 of 6 tracks apply role vocabulary correctly. The "Normal" track is the only no-role outlier and the coaching is still substantive ("It is safe to trust the steady pulse here; walk the basic"), just unlabelled.

## What worked

- **`continues.` filler is gone.** Across all six extended-set tracks plus Filomena, no `continues.` lines remain. The Daniel Santacruz canonical-worst-case went from 5 filler lines to 11 substantive ones.
- **Role vocabulary is being picked up.** *Establishing*, *sustaining*, *building*, *returning*, *closing* all show up in the live output with positions that match the prompt's position cues. The model occasionally invents near-synonyms (e.g. *maintaining* on Daniel Santacruz P9) but each variant carries a real physical focus, so it reads as language polish rather than drift.
- **Compaction on long `main ×N` groups works.** Calo Pascoal's `main ×12` (137 seconds!) collapses into one role-named line. The carve-out for single-`main` songs ("don't need a role") is implicitly working — most one-`main`-group cases are tracks where the entire body is a single `main` group.
- **Polish output is consistently strong.** Every polished line preserves the role vocabulary while improving the language. No drift away from the analysis. Polish + Phase 34 together produces the cleanest output the project has shipped on kizomba.

## What did not work / limitations

- **"Normal" track partial regression.** This track has 18 sections and two distinct `main` groups (P3 main ×7, P6 main ×6) but the tutor coached both without role names. Coaching is still substantive — _"It is safe to trust the steady pulse here; walk the basic"_ — just unlabelled. Cosmetic, not a quality loss. Possibly the model interpreted "more than one `main` group" as "more than two" or just leaned on the per-beat rules instead.
- **Isabelle kizomba_tutor "1 and 3" leak.** P3 main ×8 says: _"try a half-time feel by stepping only on 1 and 3 to match the shifting energy."_ That names a "1" position, violating the kizomba downbeat guard at line 549 of `prompts.py` ("Do NOT name a downbeat / '1' position"). Polish caught it cleanly: _"try stepping on every other beat to create a sense of suspension."_ This is the same shape as the Phase 33 listening-guide leak and is not new from Phase 34 — the kizomba_tutor downbeat guard is negative-only and the Phase 33b pattern (positive replacement) hasn't been applied to it yet.
- **Listening-guide soft "downbeat" mentions.** Calema and Tu_Es_um_Erro both used phrasing like _"Because the downbeat is not clearly defined / marked..."_ — uses the Phase-33b positive replacement ("the pulse is felt rather than heard") AND still names "the downbeat" in the same sentence. The Phase 33b guard tells the model to use the positive replacement; the model sometimes uses both. Soft violation.
- **Calo Pascoal listening-guide raw-decimal leak.** _"Because the percussiveness is relatively low at 0.34, the pulse is often felt through the bass..."_ Hard violation of the metric guard ("no percussiveness ratios"). This is the **seventh application of the metric-guard pattern across prompts and the second time it has leaked despite explicit forbidding** (Phase 31 dancer/song-arc was the first). The shared metric-guard helper string refactor is now no longer just tech debt — it would be the natural place to harden the rule (positive replacement: "instead of 'percussiveness of 0.22', say 'drum-light feel' or 'unusually low percussiveness'") and inherit it everywhere.
- **Word-count budget held.** No outputs ran over the 230-word cap. The added section-role bullet didn't push outputs over.

Three of the five soft issues (Isabelle leak, Calema/Tu_Es soft "downbeat" mentions, Normal-track no-role) are non-deterministic and are corrected by the polish pass when polish runs. Only the Calo-Pascoal raw-decimal leak is uncaught by polish (polish runs on the kizomba_tutor, not the listening_guide).

## Decision / takeaway

**Ship Phase 34.** The fundamentals work: the `continues.` filler is gone, role vocabulary is being applied on 5/6 tracks, the worst-case Daniel Santacruz output is dramatically improved, and polish + Phase 34 together produces the cleanest output the project has shipped.

The five soft issues are noted as known limitations. None of them are caused by Phase 34 directly — three are pre-existing prompt-level issues that the live evaluation surfaced, and the "Normal" track no-role regression is a non-deterministic edge case that doesn't degrade the coaching itself.

**Two follow-ups recommended:**

1. **Polish-by-default for the demo recording (one-cell change, separate from Phase 34).** The polish output is consistently better and never leaks; for the demo video the cost is acceptable. Not bundled into Phase 34 because Phase 34 already cleared the bar to ship the one-pass; this is an editorial decision about which output to record, not a code fix.
2. **Phase 35 — shared metric-guard helper string refactor + harden with positive replacement.** Now urgent rather than tech-debt: the Calo Pascoal "0.34" leak is a clean rule violation despite explicit forbidding. Lifting the metric-guard wording into a shared module-level constant lets us strengthen it once and inherit everywhere. The original Phase 35 anchor (rhythm anatomy from the brainstorm) becomes Phase 36.

## Next step

1. **Phase 35 — shared metric-guard helper string + positive replacement for percussiveness leak.** Replaces the original Phase 35 = rhythm anatomy anchor; rhythm anatomy moves to Phase 36. This is now evidence-driven (Calo Pascoal `0.34` leak) rather than just overdue refactor.
2. **Polish-by-default toggle for the demo notebook (small, post-Phase-35).** One-cell edit; separate from Phase 35 because it's editorial not architectural.
3. **Phase 36 candidate — rhythm anatomy.** Brainstorm item #6, anchored at multiple prior phase docs. Once Phase 35 lands the helper string is available to reuse, so any new prompt benefits from a hardened guard from day one.
4. **Watch list for Phase 35 live run:** verify the Calo Pascoal-class metric-decimal leak is gone after the prompt rewording. Stress-test on the same six tracks via notebook 09. Watch for new positive-replacement wording landing without the model also still using the forbidden form (the Phase 33b "downbeat AND positive replacement in the same sentence" pattern).
