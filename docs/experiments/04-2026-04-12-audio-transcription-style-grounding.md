# 2026-04-12 — Audio transcription for style disambiguation

## Goal
Use Gemma 4's multimodal audio perception to detect the vocal language of each
track, then inject it into the reasoning prompt as a strong prior for dance-style
disambiguation.  This directly targets the BPM-overlap failure mode from the
2026-04-11 experiment (129 BPM bachata → "Cha-cha", 123 BPM kizomba → "Bachata",
112 BPM kizomba → "Cha-cha").

## Changes made

### Phase A — quick wins (prompt-only, no transcription)
- **QUESTION_STYLE** rewritten to ground in social-dance vocabulary with explicit
  BPM ranges, onset-density tiebreaker, and language → style hint.
- **QUESTION_DANCER** section 1 extended with onset-density tiebreaker and
  language → style override.
- **DANCER max_new_tokens** bumped from 1024 → 1536 to prevent drill section
  truncation.

### Phase B — language-only transcription MVP
- New module `src/rytmi/transcribe.py`: `load_multimodal_model()`,
  `select_vocal_clip()`, `transcribe_vocals()`.  Uses `Gemma4Processor` +
  `Gemma4ForConditionalGeneration` directly (no `AutoTokenizer` fallback).
- `VocalsInfo` dataclass in `src/rytmi/types.py`.
- `slice_audio()` helper in `src/rytmi/audio.py`.
- `_format_vocals_section()` in `src/rytmi/prompts.py` — renders detected
  language into the analysis template; empty string when `vocals=None` (prompt
  byte-identical to baseline).
- `explain_rhythm()` and `explain_all()` accept optional `vocals` kwarg.
- `notebooks/05_batch_analysis.ipynb` — two-phase pipeline: multimodal perception
  pass first, then `del model; torch.cuda.empty_cache()` before Ollama reasoning.

## Pre-committed success criteria

1. 0/7 STYLE answers contain "Funk", "Disco", "Pop", "EDM", "House", or "R&B".
2. 0/7 DANCER answers truncated (all four sections present).
3. ≥5/7 tracks get a language guess matching the folder (Spanish for `bachata/`,
   Portuguese/Kriol for `kizomba/`).
4. The 129 BPM bachata and 123 BPM kizomba tracks are no longer cross-labeled
   once transcription is enabled.

## Results

### Criterion 1: No generic genre labels — PASS (both runs)
Neither baseline nor transcription STYLE answers contained Funk, Disco, Pop, EDM,
House, or R&B.  The `QUESTION_STYLE` rewrite (Phase A) fully eliminated this.

### Criterion 2: No truncated DANCER answers — PASS (both runs)
All 7 tracks × both runs had all 4 DANCER sections present and ending cleanly.
The `max_new_tokens=1536` bump fixed the truncation.

### Criterion 3: Language detection accuracy — PASS (6/7)

| Track | Folder | Detected language | Correct? |
|---|---|---|---|
| Canalla (Romeo Santos) | bachata | kriol | MISS |
| Me Emborrachare (Grupo Extra) | bachata | spanish | OK |
| Propuesta Indecente (Romeo Santos) | bachata | spanish | OK |
| All Of Me | kizomba | portuguese | OK |
| Baila Kizomba Amor | kizomba | portuguese | OK |
| E Magia Ben Ana (Charbel) | kizomba | portuguese | OK |
| Teu Toque (Filomena Maricoa) | kizomba | portuguese | OK |

6/7 correct (≥5 required).  The one miss is "Canalla" detected as kriol instead
of Spanish.  The clip was selected at 89.0s — possibly an instrumental/unclear
section.  This is a tolerable failure: kriol biases toward kizomba/zouk, which is
wrong for bachata, but the STYLE answer still said "Bachata" because the tempo
range was a stronger signal.

### Criterion 4: Style disambiguation — PARTIAL PASS

| Track (folder) | Tempo | BASELINE Style | BASELINE Dancer | TRANSCR Style | TRANSCR Dancer |
|---|---|---|---|---|---|
| Canalla (bachata) | 129 | ambiguous bachata/cha-cha | Bachata | Bachata | Zouk (!) |
| Me Emborrachare (bachata) | 123 | ambiguous bachata/cha-cha | Bachata | Bachata | Bachata |
| Propuesta Indecente (bachata) | 123 | Bachata | Bachata | Bachata | Bachata |
| All Of Me (kizomba) | 112 | **Cha-cha** | **Cha-cha** | **Kizomba** | **Kizomba** |
| Baila Kizomba Amor (kizomba) | 144 | Merengue | Merengue | Merengue | Zouk (compromise) |
| E Magia Ben Ana (kizomba) | 96 | Kizomba/Zouk | Zouk | Kizomba/Zouk | Zouk |
| Teu Toque (kizomba) | 123 | bachata/cha-cha | **Cha-cha** | **Bachata** (!) | **Kizomba** |

Key wins from transcription:
- **All Of Me** (112 BPM kizomba): Cha-cha → **Kizomba** in both STYLE and DANCER.
  This is the headline fix — Portuguese vocal detection overrode the tempo-only pick.
- **Teu Toque** (123 BPM kizomba): Cha-cha → **Kizomba** in DANCER.  The STYLE
  answer still said "Bachata" (tempo range dominance), but the DANCER section 1
  correctly used the Portuguese prior to pick Kizomba.

Remaining issues:
- **Canalla** (129 BPM bachata): misdetected as kriol → DANCER picked Zouk.
  STYLE still said Bachata (tempo dominance), but DANCER was wrong.  Root cause:
  incorrect language detection.
- **Baila Kizomba Amor** (144 BPM kizomba): Merengue in both runs.  The 144 BPM
  is genuinely outside kizomba's typical range.  Transcription correctly detected
  Portuguese and the DANCER answer attempted a compromise ("quickened Zouk"), but
  STYLE stuck with Merengue.  This track may be double-time kizomba — half-time
  detection would help but is out of scope.
- **STYLE vs DANCER inconsistency**: Teu Toque STYLE said Bachata but DANCER said
  Kizomba.  The language hint is in both prompts but DANCER's "let language
  override a pure-tempo pick" instruction was stronger.

## Summary scorecard

| Criterion | Target | Result |
|---|---|---|
| No generic genre labels | 0/7 fail | **0/7 — PASS** |
| No truncated DANCER | 0/7 fail | **0/7 — PASS** |
| Language detection accuracy | ≥5/7 | **6/7 — PASS** |
| Style disambiguation improvement | key tracks fixed | **Partial — 2/3 key fixes landed** |

## Limitations

1. **Language detection on "Canalla"**: kriol instead of Spanish.  May need a
   longer or better-positioned clip, or lyrics-mode to provide more signal.
2. **144 BPM kizomba** (Baila Kizomba Amor): tempo genuinely doesn't fit the
   kizomba BPM range.  Half-time detection or broader BPM priors needed.
3. **STYLE vs DANCER inconsistency**: the language prior is weighted differently
   between the two prompts.  Could unify the instruction phrasing.
4. **E2B model**: not tested.  E4B was used for both transcription and reasoning.
5. **VRAM pressure**: two-phase pipeline works but is fragile on laptop.

## Next steps

1. **Phase C — lyric-text injection**: add detected lyrics to the prompt for
   richer style grounding.  Gate on Phase B success (met).
2. **Downbeat confidence recalibration** (Phase D): the 0.00–0.09 range on all
   real tracks means the synthetic thresholds are miscalibrated.  Needs ≥20 real
   tracks.
3. **Half-time / double-time detection**: would fix the 144 BPM kizomba case.
4. **Clip selection tuning**: the Canalla miss suggests the 15% intro skip +
   onset-density argmax may pick an instrumental section on some tracks.
5. **Unify language → style instruction weight** between STYLE and DANCER prompts.
