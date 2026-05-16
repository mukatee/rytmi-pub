# Phase 40e — Gemma retry for missing transition lines

Date: 2026-05-11
Status: Implemented and run end-to-end on demo notebooks (00 + 09).

## Goal

Phase 40c rewrote the kizomba_transitions prompt around a re-entry-primary,
audible-cue rule and forbade count-based anticipation language ("8-count",
"in the last", "after N beats"). Phase 40d closed the unified-timeline work
and surfaced one honest limitation: when Gemma skips a boundary, the
verifier's deterministic `_fallback_transition_tail` substitutes a templated
line. Earlier in this run (commit 325ad50) the fallback wording itself was
rewritten to be re-entry-primary, but the deeper issue remains: a
deterministic substitution silently violates the project's signature pattern
("code identifies, Gemma writes, code verifies") for that slot — the user
sees a stylistically-consistent line they think Gemma wrote.

Goal of Phase 40e: give Gemma one explicit, fully-specified second chance to
write any missing T# line, and only fall back to the deterministic line if
that retry also fails. Keep the deterministic line as the last-line safety
net so the output still reads cleanly even if the LLM is unreliable.

## What changed

**`src/rytmi/prompts.py`**
- New `_KIZOMBA_TRANSITION_RETRY_PROMPT_TEMPLATE` and public
  `build_kizomba_transition_retry_prompt(transition, idx)` — names the
  exact boundary, restates the re-entry-primary rule, bans the same
  count-based phrasing the main prompt bans, requires one sentence ≤25
  words, forbids preamble.
- New `_try_retry_transition` — invokes the callback, parses the response
  with the same `_KIZOMBA_TRANSITION_LINE_RE` the main verifier uses, and
  rejects responses whose time doesn't match the requested boundary
  (within the same ±2.0s tolerance as the primary pass). Catches all
  exceptions so retry can never break the verifier.
- `verify_kizomba_transitions_output` gains an opt-in `retry_callback`
  keyword arg. When provided, every missing boundary is retried once
  before the deterministic fallback. Stats gain `retried` and
  `retry_succeeded` only when a callback is supplied. After follow-up:
  `boundaries_missing_filled` now counts only deterministic fallback
  fills — successful retries are Gemma's writing and don't count as
  fills, so the stats line honestly reads "Gemma wrote it".

**`src/rytmi/llm.py`**
- `explain_all` gains `transition_retry: bool = False`. When `True` and
  the kizomba_transitions branch is taken, it builds a closure around
  `generate(processor, model, prompt, max_new_tokens=128, ...)` and
  passes it as `retry_callback`. Stats string extends with
  `retried=N retry_succeeded=M` when present.

**Notebooks 00 and 09**
- New flag `RUN_TRANSITION_RETRY = True` near
  `INCLUDE_SAME_LABEL_TRANSITIONS`.
- `verify_kizomba_transitions_output(...)` now receives a `retry_callback`
  closure when the flag is True.
- The verifier-stats formatter includes `retried` and `retry_succeeded`
  when present so the printed `[verifier: ...]` line shows retry
  activity directly.

**Tests**
- Six new tests in `tests/test_prompts.py`: retry-success uses Gemma's
  text; garbage response falls back; exception falls back; callback not
  called when no missing; wrong boundary rejected; retry-prompt builder
  contains the rules.
- 465 passed, 1 skipped. Ruff clean on touched files.

## Evidence — first end-to-end run

Run: notebooks 00 (Filomena) and 09 (extended kizomba set, 17 tracks),
all using `gemma-4-26b-a4b-it` over the cloud OpenAI-compatible endpoint.

Across all 18 kizomba transition passes, **the Phase 40c prompt landed every
boundary on the first try in 17/18 tracks** (`boundaries_missing_filled=0`,
no retry needed). Retry only had to fire once: track
**Tony_Pirata / Lydia_Laprade / Filomena_Maricoa — Teu_Toque**, T9 at 222s
(`main → main`, the same kind of same-label boundary the previous pass had
flagged on a Daniel-Santacruz run).

Pre-40e (deterministic fallback, count-based language re-introduced):

> T9: 222s [main → main, beat: clear → clear] — In the last 8-count of the
> main, prepare for the shift; on entering the main, settle into the new feel.

Post-40e (Gemma retry succeeded):

> T9: 222s [main → main, beat: clear → clear] — step into your weight transfer
> as the percussiveness remains constant.

Re-entry-primary, no count-based anticipation, no naming "the 1", one short
sentence — exactly what the retry prompt asked for.

## What worked

- **Tail-case fix without regression elsewhere.** The retry only engages when
  Gemma genuinely skipped a boundary — 17/18 tracks were untouched. No
  rewrite-everything churn.
- **Honest signature pattern.** When Gemma writes the missing line, the
  output is Gemma's words, not a template substitution dressed up to match
  the prompt's wording. The stats accounting was tightened so this is
  visible: `boundaries_missing_filled` now counts only deterministic fills,
  and `retried=1 retry_succeeded=1` shows up directly in the verifier line.
- **Boundary mismatch protection.** The retry parser requires the response
  time to match the requested boundary within ±2.0s. A confident-but-wrong
  retry response is silently rejected and the deterministic fallback wins.
  Tested explicitly.
- **Best-effort, not blocking.** Exceptions in the retry callback are
  caught and treated as a failed retry — the deterministic fallback still
  fires. The retry path can never break the demo.

## What didn't work / open questions

- The retry adds one extra LLM call per missing boundary. At current rates
  (1 retry across 18 tracks) the cost is negligible, but tracks with very
  uncertain section structure could plausibly trigger several retries per
  pass. Worth watching as the eval set grows.
- The retry prompt is single-shot — it doesn't see prior T# lines for the
  same track, so it can't actively avoid wording overlap with adjacent
  transitions. The Tony_Pirata T9 result is good in isolation but a
  hypothetical multi-retry track could end up with two near-identical
  re-entry lines back to back. Not yet observed.

## Decisions

- Keep `RUN_TRANSITION_RETRY = True` as the default for both demo notebooks.
  The signature-pattern integrity gain is worth the rare extra Gemma call.
- Keep `boundaries_missing_filled` as the count of *deterministic* fills,
  with `retried` / `retry_succeeded` surfacing the retry path separately.
  This makes the demo evidence trail readable: a stats line of
  `boundaries_missing_filled=0 retried=1 retry_succeeded=1` says "the model
  was incomplete on the first pass, the retry recovered it, no template
  substitution was used."

## Next step

Phase 40e closes the immediate gap exposed by the Phase 40d run.
Reasonable next steps if time allows before the deadline:

1. Update the Kaggle writeup's "Honest limitations" subsection: the
   deterministic-fallback caveat now reads "deterministic safety net only;
   Gemma gets a per-boundary retry first, and the verifier exposes whether
   the line came from Gemma or the fallback."
2. If a future eval run produces a high-retry track, capture the per-T#
   wording variation as an open question for Phase 41 (e.g. multi-shot
   retry conditioning on adjacent T# lines).
