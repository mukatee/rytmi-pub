# 2026-05-09 — Phase 38: Vocal-activity envelope in demo notebooks 00 & 09

## Goal

Wire the Demucs-based vocal-activity source into `notebooks/00_demo.ipynb` and `notebooks/09_kizomba_extended.ipynb` so each track's `analyze(...)` call receives a `vocal_env` argument. This unlocks the `_relabel_vocal_drop_instrumentals` pass in `src/rytmi/dsp.py` for both notebooks, surfacing `instrumental` sub-sections that vocal-quiet, high-energy runs deserve. Notebook 05 has had this wiring since Phase 9; the demo notebooks were running unaware of vocals and collapsing those runs into plain `main`.

## Context / prior state

User caught the gap by visually comparing notebooks 05 and 09 on the same _Baila Kizomba Amor_ track from `data/songs/eval_set/kizomba/`:

- Notebook 05: section table flagged a clear `instrumental` run starting at P39.
- Notebook 09: same audio, no `instrumental` label — that run collapsed into `main`.

Code path tracing confirms this is a notebook-configuration gap rather than a DSP regression:

- `src/rytmi/dsp.py:3032-3128` — `analyze(audio, dance_style=..., vocal_env=None)` defaults `vocal_env` to None.
- `src/rytmi/dsp.py:3108-3128` — the vocal-aware passes (including `_relabel_vocal_drop_instrumentals`) gate on `(vocal_env is not None or speech_env is not None)`. Both None → block skipped.
- `src/rytmi/dsp.py:2639-2670` — `_relabel_vocal_drop_instrumentals` short-circuits and returns the input untouched when `vocal_env is None`.
- `notebooks/05_batch_analysis.ipynb` (config cell) — explicitly: `VOCAL_SOURCE = "demucs"`, then `vocal_source = default_vocal_activity_source(prefer=VOCAL_SOURCE)`, then per-track: `vocal_env = vocal_source.compute(audio); analyze(..., vocal_env=vocal_env)`.
- `notebooks/00_demo.ipynb` (pre-Phase-38) — `analyze(audio, dance_style="kizomba")`, no vocal envelope.
- `notebooks/09_kizomba_extended.ipynb` (pre-Phase-38) — same.

Both demo notebooks were missing one input the section labeler needs.

## Hypothesis

Mirroring notebook 05's plumbing in notebooks 00 and 09 will:

1. Surface `instrumental` sub-sections on tracks that have meaningful vocal-drop runs (Baila Kizomba Amor at P39 is the canonical case; other extended-set tracks may also light up).
2. Improve the per-track `listening_guide` and `kizomba_tutor` outputs because the section labels are richer — coaching that previously read "P5 main: keep walking" can now read "P5 instrumental: lean into the texture, sustain attention through the vocal drop".
3. Not regress any Phase 33 / 34 / 35 / 36 / 37a / 37c wins — none of those touched `analyze()`'s vocal handling, and the `vocal_env` argument is purely additive.
4. Be optional via a `RUN_VOCAL_ACTIVITY` toggle (defaults True) for users without Demucs / VRAM. Demucs is ~80 MB and runs in seconds on CPU; cached separations live under `cache/vocals/` (already gitignored).

## What changed

- **[notebooks/00_demo.ipynb](../../notebooks/00_demo.ipynb)** — imports updated with `from rytmi.vocal_activity import default_vocal_activity_source`; new `RUN_VOCAL_ACTIVITY = True` toggle in the config cell; new markdown + code cell pair after the Cloud-config diagnostic, building `vocal_source` once via the chained Demucs source. The `demo-kizomba-analyze` cell now computes `kiz_vocal_env` and passes `vocal_env=kiz_vocal_env` to `analyze(...)`. Same shape for `demo-bachata-run` with `bach_vocal_env`. The header `display(Markdown(...))` lines now also surface a `vocal_env: yes/no` chip so a demo viewer can see at a glance whether the vocal pass ran. The closing dump cell appends `vocal_env=...` to both per-track headers in `00_demo_outputs.md`.
- **[notebooks/09_kizomba_extended.ipynb](../../notebooks/09_kizomba_extended.ipynb)** — same plumbing applied to the kizomba batch helper. Imports updated; new `RUN_VOCAL_ACTIVITY` toggle in the config cell; new markdown + code cell pair after the model-load cell, building `vocal_source` once. The genre-intro seed analyze call now uses the seed track's vocal envelope (so the genre intro itself is grounded the same way the per-track analyses are). The per-track `tutor(...)` helper computes `vocal_env` per track and passes it to `analyze(...)`. The per-track header includes a `vocal_env=yes/no` chip.
- **No `src/rytmi/`, `tests/`, or other code changes.** This is purely a notebook-configuration phase. The DSP and prompt code already knew how to use `vocal_env`; the demo notebooks just weren't supplying it.

## Evidence / test results

**Tests (clean run, unchanged from Phase 37c):**
```
$ python -m pytest
================= 424 passed, 1 skipped, 64 warnings in 46.28s =================
```
No new tests added (this is a notebook-only change). No regressions.

**Compile check (both notebooks):**
```
00_demo.ipynb: 0 syntax errors
09_kizomba_extended.ipynb: 0 syntax errors
```
All edited code cells parse via `ast.parse` (skipping `%matplotlib` magic).

**Live run on `gemma-4-26b-a4b-it`:** notebook 00 (Filomena + Propuesta Indecente) and notebook 09 (11 eval_set + 6 extended_set kizomba tracks) both ran end-to-end with vocal activity enabled. Outputs in `notebooks/00_demo_outputs.md` and `notebooks/09_kizomba_extended_outputs.md`.

**Every track ran with `vocal_env=yes`.** Demucs separation succeeded across all 19 calls (1 + 17 + 1 bachata) plus the genre-intro seed. No fallbacks, no errors.

**`instrumental` labels surfaced on multiple tracks:**

| Track | Source | Instrumental run(s) |
|---|---|---|
| **Baila_Kizomba_Amor** | eval_set | 172.5–181.3s, 181.3–195.1s, 211.6–228.1s |
| **Criola** | eval_set | 82.8–94.8s |
| **Don_Kikas_-_Angolanamente_Sensual** | eval_set | 247.5–258.3s |
| **Romeo Santos — Propuesta Indecente** | bachata, notebook 00 | 186.8–194.6s (sections 23 → 24) |

Baila Kizomba Amor (the canonical case from the user's report) gets the new label exactly where it was visible in notebook 05 — three discrete instrumental runs in the back half of the track. Criola and Don Kikas each gain one instrumental run too. Section count for Propuesta Indecente went from 23 to 24 — the new instrumental run was carved cleanly out of what previously collapsed into `main`. Other tracks (Filomena and the rest of the eval+extended set) didn't gain instrumental sub-sections — their vocal patterns don't have meaningful drop runs.

**Sample `instrumental`-aware Gemma output (Baila Kizomba Amor, kizomba_tutor):**
```
P3: 172s-195s, instrumental ×2 [beat: clear] — Use this steady pulse to
    practice smooth, continuous walking.
P5: 212s-228s, instrumental [beat: clear] — Energy is rising; increase
    your intention and movement depth.
```

The model treated `instrumental` as a natural sibling of `main / break / build / peak / outro` even though the prompts don't explicitly enumerate it. No allow-list extension needed for the kizomba_tutor / kizomba_drills / listening_guide prompts. The section-role vocabulary (Phase 34) layers on cleanly: P5 gets a "rising energy" framing because it's the second `instrumental` group after a peak, not because the prompt was changed.

**Sample `instrumental`-aware listening_guide (Baila Kizomba Amor):**
> _"...builds through an instrumental phase toward a high-energy peak..."_
> _"The most challenging moment occurs during the high-energy instrumental and peak phases between 212s and 233s."_

The genre intro and per-track listening guide both naturally weave `instrumental` into the structural-arc narrative. No awkward phrasing, no rejection.

## What worked

- **`instrumental` labels surface on all tracks where they should.** Baila Kizomba Amor matches notebook 05's analysis depth. Criola, Don Kikas, and Propuesta Indecente also gain instrumental sub-sections that previously collapsed into `main`.
- **Demucs separation succeeded on every track.** First-track cold-start downloaded the htdemucs model once; subsequent tracks hit the cache.
- **Zero prompt-side rejection of the `instrumental` label.** All four kizomba prompts (listening_guide, kizomba_tutor, kizomba_drills, polish) accept the new vocabulary gracefully. The pre-Phase-38 worry that prompts would need allow-list extension didn't materialise.
- **The Phase 34 section-role vocabulary layers on top cleanly.** The kizomba_tutor's *establishing / sustaining / building / returning / closing* framing applies to instrumental groups the same way it applies to main groups — _"P5 instrumental: energy is rising; increase your intention"_ reads as natural building-phase coaching.
- **No regressions in any earlier-phase win.** Searched for raw decimals: zero in Gemma prose (all `0.NN` matches are in DSP describe_sections tables). Searched for the kizomba `downbeat` word: zero leaks. The one `downbeat` mention in the entire dump is in the bachata `dancer` output ("prepare for the next downbeat") — bachata has a real acoustic "1" so this is allowed.
- **Header chip on each analyze() result confirms `vocal_env=yes`.** Visible in the demo header markdown plus every per-track header in the dump files.

## What did not work / limitations

- **No actionable issues from this live run.** The cold-start Demucs cost was the only friction (~10s on the first track) and it's a one-time download.
- **Filomena (notebook 00 kizomba) didn't gain instrumental sub-sections.** Section count stayed at 18. The track's vocal pattern doesn't have a clear vocal-drop run that satisfies the DSP heuristic — this is correct behaviour, not a regression. The demo's kizomba example (Filomena) stays structurally simple while the bachata example (Propuesta Indecente) now has an instrumental run, which is actually a nice contrast for the demo recording.
- **`instrumental` label not yet enumerated in the prompt section-name allow-lists.** The Gemma-26B model handled it gracefully without explicit enumeration, but a smaller model or a different model family might not. **Defer.** If a smaller model is ever tried for the demo, this is a known one-line tightening per prompt.

## Decision / takeaway

**Ship Phase 38.** All goals met:

1. The demo notebooks now match notebook 05's analysis depth — no longer running unaware of vocals.
2. The user's specific concern (Baila Kizomba Amor missing `instrumental`) is resolved — and three other tracks gained the same label too.
3. No prompt-side regressions or required follow-ups.
4. The vocal-aware section labelling makes the demo flow visibly richer: the timeline + section table now shows distinct vocal-instrumental contrasts, and the per-track Gemma outputs use that vocabulary naturally.

**Architectural lesson worth recording:** the section-name allow-list concern (would prompts reject `instrumental`?) was wrong. The 26B model is robust to new section-name vocabulary as long as the surrounding context (per-section beat-clarity tags, structural-arc framing) is consistent. The Phase 34 section-role vocabulary applies generically across labels. We worried about a problem that didn't exist.

## Next step

1. **Writeup editorial pass — promote the demo flow to the central frame.** Now that the demo notebooks have full analysis depth (vocal-aware section labelling, sub-style hints, polished tutor by default, verified drills), the writeup should describe the seven-mode flow plus the vocal-aware section labelling. ~30 minutes of editorial work in `docs/kaggle_writeup.md`.
2. **Demo recording prep.** With Phase 38 in place, the demo will visibly show `instrumental` labels in the timeline + section table — a concrete artefact of the DSP's care that ties to the project's "DSP earns its keep by being the part that listens" thesis.
3. **Possible Phase 39 candidate (deferred unless evidence demands it):** explicit `instrumental` enumeration in the prompt section-name allow-lists. Only worth doing if a smaller model is ever tried for the demo.
