# 2026-05-03 — Phase 33: Listening guide (pre-listen orientation prompt)

## Goal

Add a Gemma mode that helps the learner *understand the music* before being asked to *move to it*. The current per-phase tutor and drills are movement-coaching prompts; songs with many similar sections (e.g. Daniel Santacruz `main ×16`) cause the tutor to fall back on "continues" because there's nothing new to say *physically* per phase. A listening-orientation pass — what to hear, where it gets hard — is a different mode of Gemma usage that produces density on long, similar-section tracks and reframes the demo's opening beat as music-explanation, not movement-instruction.

This is the recommendation from the 09-notebook brainstorm round: ship the *what to listen for* + *difficulty map* ideas as a single combined prompt.

## Context / prior state

Live runs of the polished kizomba tutor on the extended set (Calema/Calo/Daniel/Isabelle/Tu_Es_um_Erro/Normal — kizomba_extended in `notebooks/09_kizomba_extended.ipynb`) showed:

- The polish layer reliably eliminates raw-metric leaks and the "continues" filler the one-pass leaves behind. Coaching language is now consistent and dance-appropriate across the set.
- Vocabulary is repetitive across tracks: "steady pulse", "walk-step", "follow the bass line", "small pulse", "chase extra percussion." This is fine within a single demo but limits per-track *understanding*. The tutor's job is movement, not music-explanation, and it does that job well; the missing mode is the pre-listen orientation.
- The Daniel Santacruz output is the canonical case: 16 `main` sections and a complex multi-section structure where the per-phase movement coaching has nothing new to say after P5, but a listening guide *would* have plenty: the build-into-peak around 109s where clarity dips, the long resolution arc, the bass-as-pulse-carrier feel.

The kaggle writeup's second-pass revision (`cc40b00`) already reframed Gemma's role from "explain music to a dancer" to "help a dancer hear and connect with what the music is doing." Phase 33 is that reframe made concrete.

## Hypothesis

A standalone pre-listen prompt — two short prose paragraphs covering (1) orientation and (2) a difficulty map — will:

1. Add a useful new mode to the demo flow (DSP → **listening guide** → song arc → tutor → polish → drills) that directly serves "help the learner understand the music."
2. Produce dense, track-specific output even on long, similar-section tracks where the per-phase tutor stalls.
3. Stay grounded by leaning on the same metric-guard pattern as `song_arc` / `kizomba_tutor` / `kizomba_drills` — and by explicitly forbidding movement coaching (the differentiator from the tutor).

## What changed

- **New prompt** [src/rytmi/prompts.py](../../src/rytmi/prompts.py) `QUESTION_LISTENING_GUIDE` — generic (style-templated), prose two-paragraph format, registered in `ALL_QUESTIONS["listening_guide"]`.
  - **Format:** two paragraphs (orientation + difficulty map), under 200 words, no P# format, no headers/bullets in the output.
  - **Grounding:** uses per-phase beat-clarity labels and section labels (intro/main/break/short_break/build/peak/outro) from the analysis.
  - **Guards:** explicit "LISTENING preparation, NOT movement coaching" guard with named forbidden tokens (`walk-step`, `weight transfer`, `travel`, `styling`); same metric-guard pattern as Phase 29/31/32 (no raw decimals; BPM/timestamps OK); kizomba-specific downbeat guard ("for kizomba specifically, do NOT name a downbeat or '1'").
- **Tests** [tests/test_prompts.py](../../tests/test_prompts.py) — 5 new tests mirroring `kizomba_tutor` and `song_arc` patterns: registered + grounded, forbids movement coaching, forbids P# format, hides raw metrics, kizomba downbeat guard.
- **Tests** [tests/test_llm.py:80-87](../../tests/test_llm.py#L80-L87) — `test_all_questions_keys` updated to expect `listening_guide` in `ALL_QUESTIONS`.
- **Demo notebook** [notebooks/00_demo.ipynb](../../notebooks/00_demo.ipynb) — new markdown + code cell pair inserted between the DSP visualisation and the song-arc cell on the kizomba side; bachata side's combined Gemma cell now also runs the listening guide first. `demo-closing` got a "Listening before moving" bullet.

No `llm.py` changes — the existing `explain_rhythm()` handles any prompt registered in `ALL_QUESTIONS`. No `dsp.py` changes — the prompt consumes existing analysis fields.

## Evidence / test results

**Tests (clean run, after Phase-33b prompt fix):**
```
$ python -m pytest
================= 403 passed, 1 skipped, 64 warnings in 45.43s =================
```
398 baseline → 403 (5 new listening-guide tests). No regressions.

**Two source-level snags during drafting** (both the same pattern). When a Python string-literal continuation indents the next line for source-readability, the indent leaks into the runtime string as extra spaces — e.g. `"...no beat-clarity " "  decimals..."` concatenates as `"no beat-clarity   decimals"` and breaks substring asserts. Hit once on the metric-guard bullet (fixed by reflowing) and again on the Phase-33b "the pulse is felt rather than heard" positive-replacement insertion (fixed the same way). Same lesson as the kizomba_drills time-span rule from Phase 32: when an assertion involves a phrase that crosses a Python string-literal continuation, watch for double-spacing.

### Live run — Filomena (kizomba) on `gemma-4-26b-a4b-it`

```
This track spans 208.9 seconds with a tempo of 92 BPM. The musical journey
begins with a low-energy intro, moves through several main sections that
fluctuate between medium and high energy, encounters a quiet break, and
eventually settles into a gentle outro. Rather than a heavy drum kit, the
rhythm is carried by melodic and harmonic content, creating a pulse that
feels driven more by the bass line than by sharp percussion.

The most challenging moment occurs between 32.3s and 48.5s, where the beat
clarity becomes moderate and the rhythm feels less defined. You may also
find the section around 131.3s difficult as it shifts to a half-time feel,
which can disrupt your sense of the steady pulse. Because the downbeat is
not clearly defined, the 1 is likely around various points but you may
need to listen for the bass rather than relying on a strict count. During
these dips in clarity, trust the bass line to guide your internal timing.
```

**What landed.** Paragraph 1 opens with duration + tempo as required, names what carries the pulse in qualitative terms ("driven more by the bass line than by sharp percussion"), and frames the structural arc as one journey rather than a per-phase walkthrough. Paragraph 2 anchors on specific timestamps (32.3s–48.5s, 131.3s) with reasons. Listening advice at the end is concrete ("trust the bass line"). The output is qualitatively distinct from `song_arc` — song_arc tells the energy story; the listening guide explains the music's anatomy and where attention will drift. That was the design intent and on the 26B model it lands.

**What leaked.** _"Because the downbeat is not clearly defined, the 1 is likely around various points but you may need to listen for the bass rather than relying on a strict count."_ The model is *trying* to acknowledge the no-clear-downbeat reality (good instinct) but does so by naming "the 1" and "the downbeat" — both forbidden. The neighbouring `kizomba_tutor` and `kizomba_drills` outputs do not leak the "1" framing, which suggests the listening-guide framing — "where will the learner likely lose the **count**" — is what was inviting count/downbeat language.

### Live run — Propuesta Indecente (bachata) on `gemma-4-26b-a4b-it`

```
This 268.0-second track maintains a very steady tempo of 123 BPM. The
musical journey begins with an intro and a break, transitions into several
main sections, builds toward a peak, and finally winds down through an
outro. Rather than a heavy drum beat, the rhythm is carried primarily by
melodic and harmonic content, which provides a subtle, drum-light pulse
throughout the piece.

The most challenging moment for maintaining your count occurs during the
main sections between 170.9s and 253.6s, where beat clarity becomes quite
low. During this stretch, the pulse is moderate but less obvious, making
it easy to drift from the underlying rhythm. Because the percussiveness is
so low, you may find it difficult to pin down the exact moment of each
beat. During these sections, focus on counting internally to stay
synchronized with the steady melodic pulse.
```

**What landed.** Both paragraphs land cleanly for bachata. Tempo, structure, qualitative pulse description, anchored difficulty timestamps, listening advice. No leak — bachata has a real acoustic "1" and the prompt allows that, but in this run the model didn't need to lean on it because the difficulty was about clarity-drift, not downbeat ambiguity.

### Phase 33b — prompt fix applied after first live run

Two surgical edits to address the kizomba "1" leak, applying the Phase 32 lesson (positive replacement beats negative-only):

1. **Paragraph 2 framing:** "Where will the learner likely lose the **count**" → "Where will the learner likely lose the **pulse**". Removes the count-thinking bait. Listening-advice example "count internally" replaced with "feel the underlying pulse".
2. **Kizomba guard strengthened with positive replacement:**
   ```
   For kizomba specifically, do NOT name a downbeat, 'the 1', or any
   specific count position. ... If the music's lack of a clear downbeat
   needs acknowledging, frame it as 'the pulse is felt rather than heard'
   or 'the bass carries the pulse' — never as 'the 1' or 'the downbeat'.
   ```
   Test asserts the new positive-replacement wording is present so future regressions get caught at the prompt level.

This is the **sixth application of the metric-guard pattern across prompts and the second time a positive replacement was needed after a negative-only guard leaked** (kizomba_drills was the first, Phase 32). The shared-helper-string refactor flagged in Phase 31/32 is now overdue at the level of "we keep solving the same problem one prompt at a time" — explicit follow-up tracked under Next step.

### Model comparison — `gemma-4-26b-a4b-it` vs `gemma4:e4b`

The same notebook was run on both models. Outputs diverge sharply.

**26B (`gemma-4-26b-a4b-it`) — usable for the demo.** Listening guide, song arc, tutor, drills all produce well-formed output that respects the prompt's structural rules. The "1" leak in the kizomba listening guide is the only clear miss, addressed by the 33b fix above. Outputs across all four prompts (listening_guide, song_arc, kizomba_tutor, kizomba_drills) are mutually distinct in role: anatomy + difficulty / energy story / movement coaching / practice plan.

**E4B (`gemma4:e4b`) — not viable for the demo on these tracks.**
- Listening guide misses the "open with duration and tempo" rule on both kizomba and bachata. Output reads as generic music-talk rather than a track-specific orientation.
- Song arc cuts off mid-sentence (truncation; the model exhausts its budget without reaching a full close).
- The kizomba tutor collapses entirely after P12 on the longer Filomena track: emits `"P13: 131.3s-131.3s, main [Skipping due to structural ambiguity]"` and then a self-correction note rather than a clean continuation. The track has many phases and the model loses the format.
- Polish pass on kizomba returns an empty response on first try; the retry succeeds but again truncates mid-line at P12.
- Drills output drops the required `P#: <section> (<start>s-<end>s, beat: <tag>) — Drill: <action>. <duration>.` format entirely and emits markdown bullets with prose, ignoring the structural rule.

**Why E4B falls behind.** The E4B model is roughly 8x smaller than 26B in parameter count (4B vs 26B active parameters), and the listening-guide / tutor / drills prompts ask for structured output across a full song's worth of phases — not a single-paragraph Q&A. The structural rules (P# format, label-slot enumeration, two-paragraph layout) are followed by 26B but ignored or partially followed by E4B once the analysis input exceeds a certain size. On short tracks (Filomena's first run was 195s with fewer phases) E4B produced cleaner output; on Daniel Santacruz-class long tracks, the gap widens. This matches the broader pattern documented in the project's earlier model-selection notes (`docs/gemma-kaggle-compo.md`): start with smaller local models, escalate to 26B / 31B when reasoning quality matters. For this demo, the role split has shifted — E4B is no longer the documented baseline for the listening_guide / tutor / drills layer.

**Demo recommendation:** record the demo video against `gemma-4-26b-a4b-it` (or whichever 26B-class endpoint is available), not E4B. E4B remains useful for fast iteration on prompt structure and for the `song_arc` / `time_signature` / `counting` lighter-weight prompts, but the four-prompt kizomba flow needs the larger model to land structurally.

## What worked

- **Distinct role from `song_arc`.** On 26B, the listening guide and song_arc add up to two genuinely different paragraphs of value: anatomy + difficulty vs energy journey. The original concern (redundancy) didn't materialise.
- **Difficulty map anchors well.** Both kizomba and bachata outputs cite specific timestamps with specific reasons (clarity dips, half-time shifts, percussion-thinning sections). Not generic.
- **Bachata path works without style-specific prompt.** The templated-by-`{style}` design carried bachata cleanly without a `QUESTION_BACHATA_LISTENING_GUIDE` variant. The architectural lesson from the writeup ("style-specific prompts only when there's an idiosyncrasy worth guarding against") held up: kizomba has the downbeat idiosyncrasy and gets a guard; bachata has none requiring care here.
- **Movement-coaching leakage didn't happen.** The "save those for the tutor" rule plus the explicit forbidden-token list (walk-step / weight-transfer / travel / styling) was enough — neither 26B run drifted into coaching language.

## What did not work / limitations

- **Negative-only kizomba guard wasn't enough.** The original "do NOT name a downbeat or '1'" was followed by `kizomba_tutor` and `kizomba_drills` but bypassed by `listening_guide` because the listening framing itself ("lose the count") invited count-thinking. Fixed in 33b with a positive replacement.
- **E4B is not the right model for this layer.** Documented above. The demo flow assumes a 26B-class endpoint.
- **Word count on 26B kizomba is just under cap.** Output was ~165 words for the kizomba run, ~155 for bachata. Comfortable, but the paragraph-1 "open with duration and tempo" rule plus the structural-arc requirement leaves little room for richer anatomy on tracks with many phases. Could tighten the cap to 180 words to force pithier output, but acceptable as-is.
- **The `kizomba_tutor` output on the new Filomena run shipped here is `main ×4`, `main ×2`, etc. with `continues` filler in P3-P5**, which is a separate problem from listening_guide and exactly the diagnosis the brainstorm flagged: per-phase movement coaching has nothing new to say across same-label runs. **Phase 34 (section role narration) is the planned response.**

## Decision / takeaway

**Ship Phase 33 with the 33b fix in place.** The listening guide is doing its job on the demo's reference model (26B): qualitatively distinct from song_arc, anchored on the analysis, no movement-coaching leakage, and the original "1" leak is addressed at the prompt level with a test that pins the positive-replacement wording.

The model-quality boundary observation is itself a valuable artefact for the project record: the four-prompt kizomba flow (listening_guide / kizomba_tutor / polish / kizomba_drills) needs a 26B-class endpoint to land structurally. Smaller-model fallbacks would need a separate, simpler prompt set rather than the same prompts run with degraded compliance.

## Next step

1. **Phase 34 — section role narration.** Diagnosis-driven follow-up: the `kizomba_tutor` "continues" filler on `main ×N` runs is the next obvious quality gap. Naming each main's *role in the song's arc* (establishing / sustaining / post-build / resolving) instead of its label gives the tutor something to say even on long, similar-section tracks. The polish pass already half-does this; making it explicit in the one-pass prompt would propagate the improvement upstream.
2. **Shared metric-guard helper string — now overdue.** Phase 33 is the sixth application of the same metric-guard pattern (`song_arc`, `dancer`, `kizomba_tutor`, `kizomba_drills`, polish, listening_guide), and the second positive-replacement guard added retroactively after a leak. Refactoring the wording into a module-level constant (or small builder function) would let future prompts inherit the latest version of the rule by reference. Keep small in scope.
3. **E4B fallback prompts (optional).** If the project ever wants to be truly local-first on commodity hardware, the four-prompt kizomba flow needs an alternate, simpler prompt set tuned for E4B-class models. Out of scope for the hackathon demo.
