# Rytmi Project Vision — Living Project Brief

> Purpose: this is the **project-specific, evolving description** for this repo. Unlike the competition reference, this file is meant to change over time as the idea, implementation, and lessons learned become clearer.

- **Project name (working):** `kaggle-gemma4-rytmi`
- **Primary theme:** rhythm learning for dance and music
- **Status:** early exploration / prototyping
- **Last updated:** 2026-04-20

---

## 1) Why this project exists

This project starts from a **personal learning problem**.

I like practicing dance in my free time, including styles such as:
- reggaeton
- commercial
- twerk
- bachata
- kizomba
- tango argentino
- beginner salsa

A recurring challenge has been **hearing and internalizing rhythm clearly enough to move with confidence**, especially in social-dance contexts.

A very concrete example is **bachata**:
- the music often follows an **8-count structure**,
- but it can still be hard to reliably identify the pulse,
- and especially to feel where the **“1”** is so movement stays synchronized with the phrase.

With **kizomba**, the challenge is fundamentally different:
- finding "the 1" matters much less — every beat can function as a starting point,
- instead, the important skill is **hearing and stepping into the beat itself**, especially in songs where the pulse is subtle or layered with subdivisions,
- the dancer has freedom of movement and interpretation on every beat,
- the challenge is more about **beat clarity** — distinguishing the main pulse from ornamentation — than about phrase alignment.

So the real motivation here is simple:

> **Can AI-assisted tools help a person learn to hear, see, and understand rhythm better across different songs and dance styles?**

---

## 2) Main project goal

The goal is to build something that helps a learner:
- detect or follow the beat in music,
- understand rhythmic structure in a human-friendly way,
- identify likely count patterns such as 4s and 8s,
- better recognize where a phrase may begin,
- and connect that understanding to actual dance practice.

This is not only about dance instruction. It could also help anyone trying to learn:
- timing,
- groove,
- phrase awareness,
- musicality,
- or basic rhythm confidence.

---

## 3) Broader motivation

This project has **two parallel purposes**:

### A. Build a useful rhythm-learning tool
The practical aim is to support people who struggle with feeling the beat or finding the count in real music.

### B. Learn how to build this well with AI tools
This repo is also a hands-on learning exercise in:
- using **AI coding assistants** effectively,
- understanding where **LLMs** are genuinely useful in an application,
- and testing how **Gemma 4** can contribute to real product features rather than being added superficially.

So success here is not only “the model works perfectly.” It is also:
- learning what workflows are effective,
- learning what should stay classical/DSP-based,
- and learning where LLM reasoning adds real value.

---

## 4) Intended user problem

Many learners can hear music in a general sense but still struggle with questions like:
- "Where is the beat?" (especially in kizomba where the pulse can be subtle)
- "Where is the 1?" (critical in bachata, less so in kizomba)
- "Why does this song feel harder to count than another one?"
- "Should I step on every beat here, or is there a pause/accent pattern?"
- "What makes bachata, kizomba, salsa, or other styles feel rhythmically different?"
- "Which parts of this song have a clear beat and which parts are trickier?"

The learning challenge is **style-dependent**:
- In **bachata**, getting the "1" right is critical — every mini-choreo runs in 4+4 counts and missing the phrase start breaks the pattern.
- In **kizomba**, the "1" is less important because the dancer has continuous freedom of movement. The harder challenge is **hearing the beat itself** clearly, especially in songs where the pulse is not explicitly strong.

This project aims to make those questions easier to explore through:
- visualizations,
- beat markers,
- segment-level explanations,
- style-aware rhythm descriptions,
- and interactive feedback.

---

## 5) Product idea in one sentence

> **A rhythm-learning assistant that combines audio beat analysis with Gemma 4-based explanation and tutoring to help people understand timing, count structure, and musical feel in dance music.**

---

## 6) Current product direction

The current concept is to combine **classical audio analysis** with **LLM-assisted interpretation**, with **style-aware priorities** that match what actually matters for each dance.

### Style-differentiated analysis approach

Different dance styles need fundamentally different analysis:

#### Bachata mode
- **Primary goal:** find the "1" (phrase start) — the mini-choreo runs in 4+4 and the dancer must hit the phrase reset.
- **Key features:** downbeat detection, phrase boundary markers, 8-count grouping visualization.
- **Status:** downbeat detection already works well (all bachata eval tracks consistently pick offset=0 across multiple signal variants).

#### Kizomba mode
- **Primary goal:** surface the beat itself — help the dancer hear and step into the pulse, especially in songs where it is not explicitly strong.
- **Key features:** beat clarity per section, rhythmic texture/density, where the beat is easy vs. hard to hear, subdivision vs. main-pulse separation.
- **Status:** downbeat/"1" detection is not meaningful here (onset energy is flat across all 4 beat positions — a musical fact, not a detection failure). The new direction focuses on beat feel and clarity instead.

### Likely split of responsibilities
#### Classical / DSP side
Use signal-processing tools (for example `librosa` and related analysis) for things like:
- onset detection
- tempo estimation
- beat tracking
- segmentation
- visual rhythm timelines
- extracting structured beat/event patterns from audio

#### LLM / Gemma side
Use Gemma 4 for things like:
- explaining the rhythm in plain language
- turning beat/onset patterns into learner-friendly feedback
- comparing rhythmic feel across songs/styles
- helping describe where phrase starts may occur
- generating practice cues or step suggestions
- answering user questions about what they are hearing

### High-level idea
A good division of labor may be:
1. **audio tools detect candidate structure**, and then
2. **Gemma interprets that structure for a human learner**.

Example:
- `librosa` detects beat timings and pattern irregularities
- Gemma explains: “this section feels delayed / syncopated / hard to count because the accents pull away from the expected phrase entrance.”

---

## 7) Role of Gemma 4 in this project

Gemma 4 should be used where it adds **meaningful value**, not just for the sake of the competition.

### Initial preference
Start with **smaller Gemma 4 variants locally via Ollama** when possible, because that is:
- more practical,
- more affordable,
- more reproducible,
- and potentially a better fit for the Kaggle hackathon’s local-first spirit.

### Optional extension
Use a **larger Gemma 4 model** (for example via a cloud endpoint) only when there is a clear gain for:
- better explanations,
- multimodal reasoning,
- stronger summarization,
- or more capable agent-style behavior.

### Principle
> Prefer the **smallest model that delivers useful results**.

That keeps the project more realistic and better aligned with deployment viability.

---

## 7A) Gemma 4 capability reference for this repo

> Source note: based on the official `Gemma 4` model card from Google AI / Kaggle, checked on 2026-04-11.

| Model | Architecture / size | Context | Modalities | Best use in this repo |
|---|---|---:|---|---|
| `E2B` | small dense, on-device oriented | 128K | text, image, **audio** | lightweight local tutor, quick explanations, speech transcription, spoken counting |
| `E4B` | stronger small dense, on-device oriented | 128K | text, image, **audio** | best default local model for richer explanation, interactive coaching, and speech-aware features |
| `26B A4B` | MoE, ~4B active parameters | 256K | text, image | stronger long-context reasoning/coding via cloud or larger local hardware |
| `31B` | large dense | 256K | text, image | heavyweight option for richer analysis or polished writeup/demo generation |

### Important audio clarification
Officially, **audio input is supported only on `E2B` and `E4B`**. The documented native audio uses are mainly:
- **automatic speech recognition (ASR)**
- **speech-to-translated-text translation**
- short audio clips, with the docs noting **up to 30 seconds** of audio input

That is useful, but it should **not be misunderstood as a full music-analysis model**.

For this project, that means:
- **good fit:** spoken counting, voice UI, short vocal/transcription tasks, maybe lyric or verbal cue extraction
- **unclear / limited fit:** robust downbeat detection, full song-form analysis, percussion-aware groove tracking, dance-oriented rhythm parsing from raw music alone

### Note on vocals and song structure
It is reasonable to **experiment** with the small audio-capable Gemma models on short song excerpts that contain clear vocals, especially if the goal is to:
- transcribe sung/spoken words,
- detect whether a section is more speech-like or vocal-led,
- or extract verbal cues that may help explain what is happening musically.

But the current official capability description still points much more toward **speech understanding** than full **music-structure analysis**.
So vocals can be a useful *auxiliary signal*, but they should not be treated as the main rhythm-analysis engine.

> Practical rule: use `librosa`/DSP to detect beats and structure; use Gemma to **explain**, **label**, **coach**, and **interact** around those results.

> **Reproducible evidence (Phase 43, 2026-05-12):** ran `E4B` on three
> short kizomba excerpts (steady main / break / pre-break build) with
> dancer-teacher prompts. Output was generic kizomba boilerplate that
> did not differentiate the clips and mislabelled the break. Full probe:
> [`experiments/43-2026-05-12-gemma-audio-probe.md`](experiments/43-2026-05-12-gemma-audio-probe.md);
> raw model output: [`../demo_assets/output/gemma_audio_probe.md`](../demo_assets/output/gemma_audio_probe.md);
> reproduce with `python demo_assets/scripts/probe_gemma_audio.py`.

### Practical model-choice guidance

| Task | Best starting choice |
|---|---|
| Beat detection, onset timing, tempo, likely `1` candidates | classical DSP / heuristics |
| Explain plots and beat patterns to a learner | `Gemma 4 E4B` |
| Spoken count or voice command transcription | `Gemma 4 E2B` or `E4B` |
| Long comparative writeups or heavier reasoning | `Gemma 4 26B A4B` or `31B` |
| Local-first competition demo | small Gemma model + DSP pipeline |

---

## 7B) Suggested MVP roadmap

### Phase 1 — Rhythm explorer
Build the smallest useful tool:
- load a song/sample
- show waveform + onset/beat markers
- show estimated tempo and count grid
- highlight likely strong beats and phrase starts (bachata) or beat clarity regions (kizomba)
- let the user compare easier vs. harder songs

### Phase 2 — Gemma tutor layer
Add a learner-friendly explanation layer:
- “where is the beat?” — especially for kizomba tracks with subtler pulse
- “where is the likely `1`?” — primarily for bachata
- “why is this section harder to hear the beat in?”
- “what should I step to here?”
- “is this more steady pulse or more syncopated?”

### Phase 3 — Style-aware coaching
Add dance-specific guidance:
- **bachata**: phrase structure, "1" markers, 4+4 mini-choreo alignment
- **kizomba**: beat clarity map, rhythmic texture, sections of different intensity, "easy to follow" vs "trickier" zones
- comparison across genres in `data/samples/` and `data/songs/`

### Phase 4 — Optional multimodal extensions
Only if genuinely useful:
- short spoken-audio interaction with `E2B` / `E4B`
- cloud-assisted deeper reasoning with `26B A4B`
- video/frame-based explanation later if dance video support becomes relevant

### Candidate MVP features
1. **Beat timeline view**
2. **Style-aware analysis** (downbeat/"1" for bachata, beat clarity for kizomba)
3. **Gemma explanation box**
4. **Style comparison mode**
5. **Practice cue generator**

---

## 8) What success would look like

A useful first version of the project should help a learner do at least some of the following:
- load a song or sample,
- see a beat timeline or pulse visualization,
- inspect likely strong beats and phrasing,
- get a readable explanation of what the rhythm is doing,
- compare songs from different styles,
- and leave with clearer practice guidance than they had before.

A strong version would additionally:
- adapt explanations to different dance styles,
- handle songs that are harder to count,
- explain uncertainty instead of pretending confidence,
- and run locally enough to feel practical.

---

## 8A) Current design assumptions

These assumptions are built into the current implementation. They are
deliberate scoping decisions, not bugs, but they constrain what the system
can handle and should be revisited as the project evolves.

1. **The learner knows their dance style.** The system accepts style as
   explicit user input (or infers it from the folder structure of the audio
   library). It does not auto-detect dance style from audio content.
   Style-aware coaching, guardrails, and prompts all depend on this input.

2. **8-count phrasing in 4/4 time.** All current style profiles assume
   4/4 time with 8-count dancer phrases (two measures per phrase). Styles
   in 3/4, 6/8, or other meters are not yet supported.

3. **DSP-first for rhythm structure.** Beat tracking, tempo estimation,
   onset detection, and section segmentation are handled by classical DSP
   (librosa). Gemma's role is explanation, coaching, and language — not
   primary beat detection.

4. **Section segmentation is energy-based.** Section labels (intro, main,
   break, build, peak, outro) are derived from spectral novelty curves and
   energy thresholds, not from music-theory structure like verse/chorus.
   This means most sections in steady-energy tracks are labeled "main".

5. **Style-specific guardrails prevent hallucination.** Each `StyleProfile`
   carries a `basic_step` text that constrains how the LLM describes
   counting patterns. Without this, the model tends to hallucinate
   incorrect groupings (e.g. "3+3+2" for bachata).

6. **Downbeat detection is style-dependent.** The downbeat/"1" is
   acoustically clear and important in bachata (all eval tracks consistently
   resolve to offset=0). In kizomba, extensive testing across 7 signal
   variants shows onset energy is flat across all beat positions — the "1"
   is not acoustically emphasized, which matches the dance: kizomba gives
   the dancer freedom to interpret any beat as a starting point. The system
   should therefore prioritize beat clarity and rhythmic texture for kizomba
   rather than forcing a downbeat answer.

---

## 9) Non-goals / constraints

This project is **not** primarily trying to:
- replace a professional dance teacher,
- produce perfect music-theory truth for every song,
- solve all beat-tracking problems universally,
- or force every rhythmic question into a rigid 8-count explanation.

Important constraint:
- different dance styles and songs may organize rhythm differently,
- so the tool should stay **helpful and honest**, not overly dogmatic.

---

## 10) Why this can still fit the Kaggle competition

Even if the project is personally motivated, it still connects well to the competition themes:

- **Future of Education** — helps people learn rhythm and musicality more effectively
- **Digital Equity & Inclusivity** — can become a more accessible, local-first learning tool
- **Safety & Trust** — can explain *why* it gives a rhythm interpretation instead of acting like a black box
- **Ollama / local-first angle** — smaller Gemma 4 models can support a practical offline or near-local workflow

So the impact story does not need to be exaggerated. A credible framing is:

> helping people learn rhythm, counting, and musical confidence in a clearer and more accessible way.

## 10A) Likely Kaggle submission angle

**Working pitch:** `Rytmi — a local-first Gemma 4 rhythm coach for dance and music learners`

### Best-fit track
- **Primary:** Future of Education
- **Secondary:** Digital Equity & Inclusivity
- **Possible special technology angle:** Ollama / local-first deployment if the demo runs well on consumer hardware

### Why this pitch is credible
- it starts from a real user problem
- it gives a clear and demo-friendly before/after story
- Gemma 4 has a meaningful role instead of being artificially attached
- it can be built as a believable prototype rather than a vague concept video

### Demo story to aim for
1. Load a bachata or kizomba track
2. Show detected beats and likely phrasing visually
3. Ask Gemma to explain what makes the rhythm feel tricky
4. Show a short learner-friendly practice recommendation
5. Compare with a second song to show generalization

## 10B) Concrete implementation task list for this repo

This section translates the vision into a repo-aware build plan.

### Immediate build order

| Priority | Task | Main repo areas |
|---|---|---|
| `P0` | strengthen rhythm analysis baseline | `src/rytmi/dsp.py`, `tests/test_dsp.py`, `notebooks/02_onset_beat_detection.ipynb` |
| `P0` | improve visual explanations | `src/rytmi/viz.py`, `notebooks/03_visualization.ipynb` |
| `P0` | make Gemma explanations more learner-focused | `src/rytmi/prompts.py`, `src/rytmi/llm.py`, `tests/test_llm.py` |
| `P1` | run multi-song comparison and batch summaries | `notebooks/05_batch_analysis.ipynb`, `data/songs/` |
| `P1` | add a simple user-facing demo | `app/` or a small CLI/script entrypoint |
| `P2` | package the Kaggle story and demo assets | `README`/docs, video outline, writeup draft |

### Workstream 1 — DSP / rhythm foundation
Goal: make the non-LLM rhythm extraction as solid and explainable as possible, with style-appropriate priorities.

**Tasks**
- **bachata**: maintain and verify downbeat/"1" detection (already working well — all eval tracks resolve offset=0)
- **kizomba**: add beat clarity scoring — onset strength variance, on-beat vs off-beat energy ratio, per-section beat confidence
- improve `detect_downbeats()` in `src/rytmi/dsp.py` with style-aware behavior
- expose phrase-start candidates and section boundaries in `RhythmAnalysis`
- evaluate results on bachata, kizomba, and a few easier/harder comparison tracks

**Done when**
- bachata tracks show reliable downbeat markers and phrase grouping
- kizomba tracks show per-section beat clarity instead of forcing a downbeat answer
- uncertainty is surfaced instead of hidden

### Workstream 2 — Visualization and learner UX
Goal: make the rhythm readable even for a beginner, with style-appropriate emphasis.

**Tasks**
- extend `src/rytmi/viz.py` to show:
  - beats and onset markers
  - downbeat/"1" markers for bachata
  - beat clarity shading for kizomba (where is the beat easy vs. hard to hear)
  - phrase groupings
  - confidence shading or annotations
- update `notebooks/03_visualization.ipynb` to show side-by-side examples across styles
- highlight sections that are likely “easy to follow” vs “rhythmically tricky”

**Done when**
- a user can glance at the plot and understand where to try stepping
- the visuals support the LLM explanation instead of duplicating it vaguely

### Workstream 3 — Gemma tutor layer
Goal: turn raw DSP output into useful coaching.

**Tasks**
- expand prompts in `src/rytmi/prompts.py` for:
  - likely `1` explanation
  - how to count this section
  - beginner practice advice
  - style-specific explanation (bachata vs kizomba etc.)
  - uncertainty-aware wording
- add or refine helper functions in `src/rytmi/llm.py` for:
  - compare-two-songs analysis
  - practice drill generation
  - one-click explanation variants for notebooks/demo
- compare outputs from smaller local Gemma models first

**Done when**
- the model output sounds like a helpful rhythm coach
- explanations stay grounded in the DSP results
- the same prompt style works across several genres without obvious hallucination

### Workstream 4 — Evaluation set and regression checks
Goal: avoid “looks good on one song only” failure.

**Tasks**
- curate a small internal evaluation set from `data/songs/`
- annotate a few clips manually with rough labels such as:
  - easy/hard to count
  - likely `1`
  - stable pulse vs syncopated feel
- add tests where possible in `tests/test_dsp.py`, `tests/test_viz.py`, and `tests/test_llm.py`
- keep a notes table of where DSP or Gemma outputs feel wrong or misleading

**Done when**
- improvements can be checked across more than one example
- regressions are easier to spot when prompts or DSP logic change

### Workstream 5 — User-facing demo
Goal: create something that is actually demoable for Kaggle.

**Tasks**
- build a very small UI or script flow in `app/` that:
  1. loads a track,
  2. runs analysis,
  3. shows the visual timeline,
  4. displays Gemma’s explanation,
  5. suggests a practice cue
- keep the flow local-first when possible
- support at least one “compare two songs” interaction

**Done when**
- a 1–3 minute demo can show a complete end-to-end learner workflow

### Workstream 6 — Kaggle packaging
Goal: make the repo submission-ready, not just technically interesting.

**Tasks**
- prepare a short writeup outline aligned to the scoring rubric
- prepare a video storyboard with before/after learner value
- document where Gemma 4 is central and where DSP is central
- include honest limitations and future work

**Done when**
- the repo tells a coherent story even to someone seeing it for the first time

### Recommended next 5 implementation steps
1. Add beat clarity scoring for kizomba (onset strength variance, on-beat vs off-beat ratio per section)
2. Verify bachata downbeat detection works reliably on eval set (likely already done — bachata consistently picks offset=0)
3. Extend `src/rytmi/viz.py` with style-differentiated display: phrase markers for bachata, beat clarity shading for kizomba
4. Add a "why is this section harder to hear?" explanation mode in `src/rytmi/prompts.py`
5. Build a tiny end-to-end demo flow in `app/` showing different analysis for bachata vs kizomba

---

## 11) Practical implementation philosophy

When building features for this repo, prefer:
- simple features that are actually useful,
- explainable pipelines over magic behavior,
- local-first approaches where reasonable,
- measurable demos over vague claims,
- and honest evaluation of what works vs. what does not.

### Especially important
If a classical method already solves something well, keep using it.
The LLM should augment the system where language, explanation, tutoring, or reasoning are needed.

---

## 12) Guidance for future AI-assisted coding sessions

If an AI coding assistant reads this file, it should assume the project priorities are:

1. **Help users learn rhythm in a practical way**
2. **Keep Gemma 4 meaningfully involved, but not artificially forced**
3. **Use DSP/audio tooling where it is strongest**
4. **Use Gemma for explanation, tutoring, pattern interpretation, and interactive guidance**
5. **Prefer local/smaller models first**
6. **Document what worked, what failed, and why**

In short:

> Build something genuinely useful for rhythm learning, and use Gemma 4 where it clearly improves the experience.

---

## 13) Current working hypotheses

These are the assumptions currently worth testing:

- Beat and onset detection can provide enough structure for meaningful learner feedback.
- LLM explanations may help users understand rhythm better than raw plots alone.
- Different dance styles need fundamentally different analysis goals, not just different parameters.
- In bachata, downbeat/"1" detection is the key problem and appears largely solved.
- In kizomba, beat clarity and rhythmic texture are more useful than downbeat identification.
- A local small model may be sufficient for many explanation tasks.
- Some parts of the problem will likely work better with DSP and heuristics than with LLMs.

---

## 14) What should be tracked over time

This file should be refined as the project evolves.
Useful updates include:
- what has been implemented,
- intended purpose of each feature,
- what worked well,
- what did not work,
- where Gemma 4 helped,
- where non-LLM methods were better,
- and which model/setup offered the best tradeoff.

---

## 15) Suggested running log structure

Use this section as a living changelog for direction and lessons.

### 2026-04-11 — Initial project vision
- Project motivated by personal dance/rhythm learning difficulties, especially hearing beat structure and finding the “1”.
- Current idea: combine beat detection + visualization + Gemma-based explanation/tutoring.
- Local small Gemma variants are preferred first; larger cloud-hosted models remain optional.
- Key question: how much real learner value can LLM-based explanation add on top of standard audio analysis?

### 2026-04-11 — Added roadmap and Gemma capability notes
- Added a concrete MVP roadmap and a likely Kaggle submission framing.
- Noted that official audio support is on `E2B` and `E4B` only, and the documented native audio tasks are mainly speech-oriented.
- Current working assumption: music structure should still be extracted mainly with DSP, then interpreted by Gemma for the learner.

### 2026-04-11 — Added concrete repo implementation plan
- Added a repo-aware task list covering DSP, visualization, Gemma prompting, evaluation, demo flow, and Kaggle packaging.
- Identified the next five practical implementation steps to move from concept to MVP.
- Clarified that vocals can be an auxiliary experimental signal, but not the main structure-analysis method.

### 2026-04-11 — First-pass downbeat / "1" confidence in `detect_downbeats()`
- Added a confidence score to `detect_downbeats()` so the DSP layer reports how trustworthy its likely-"1" guess is, instead of returning a bare offset as if it were certain.
- First-pass formula: winner-share above a uniform-chance baseline of `1/beats_per_measure`. Calibrated so 0.0 = "no information" and 1.0 = "one offset dominates completely".
- Propagated the new value to `RhythmAnalysis.downbeat_confidence` for downstream use by viz and Gemma prompts.
- Added `synthetic_accented_click_audio` test fixture using a low-frequency (80 Hz, bass-drum-like) click so onset strength scales meaningfully with amplitude — a 1 kHz sine click does not, because librosa's log-mel onset strength compresses dynamic range.
- Lesson: synthetic test signals must resemble what they are meant to model. A 1 kHz sine "click" looks nothing like a kick drum to spectral-flux onset detection, so it was a poor proxy for testing dance-music downbeat detection.

### 2026-04-11 — Second-pass review of downbeat confidence
- Identified two real flaws in the first-pass heuristic and fixed both:
  1. **Sum-based scoring biased toward offsets that captured one extra beat at the audio boundary.** Empirical proof: a *uniform* 100 Hz click track (no accent at all) reported confidence ~0.062 — pure offset-count noise. Switched to **mean per offset**, which removed the bias (uniform now ~0.034).
  2. **Single-signal confidence was blind to tied-top ambiguity.** A 2/4-feel signal scored against a 4/4 measure (offsets 0 and 2 tied) previously reported ~0.17 confidence — moderately confident in a fundamentally ambiguous case. Added a **margin** signal `(best - runner_up) / best` and combined it with the existing dominance via the **geometric mean** `sqrt(margin × dominance)`. The same tied-tops case now correctly reports ~0.028.
- Strong-winner cases (clear bass-accented downbeats) are essentially unchanged at ~0.4, so the fix improves honesty without breaking the working case.
- Added regression tests for tied-tops ambiguity, the `beats_per_measure < 2` edge case, and a tighter (`< 0.15`) threshold for uniform input.
- Lesson: a confidence metric for learner-facing tools should be **conservative by construction** — it should say "I don't know" in *all* failure modes, not just the obvious ones (silence/noise). Combining two complementary signals via a geometric mean is a simple, explainable way to enforce that — either signal being weak collapses the result.
- Lesson: the temptation to add ML or neural downbeat models is real, but a well-designed classical heuristic with calibrated uncertainty is more aligned with the project's "explainable, DSP-grounded" principle and is fast enough to run locally.
- Limitations carried forward: tempo octave errors are not corrected; only one `beats_per_measure` value is tried at a time; all validation is on synthetic clicks (real bachata/kizomba/salsa evaluation is still pending); the confidence is not yet surfaced to viz or Gemma prompts.

### 2026-04-12 — Audio transcription for style disambiguation
- Built a two-stage pipeline: Gemma 4 multimodal **perception** pass (local HF, one audio call per track to detect vocal language) followed by the existing Ollama **reasoning** pass (text-only, now with a `{vocals_section}` in the prompt).
- Language detection accuracy: 6/7 on the eval set (4 kizomba all correctly detected as Portuguese; 2/3 bachata correctly detected as Spanish; 1 bachata misdetected as Kriol).
- Key win: **All Of Me** (112 BPM kizomba) went from "Cha-cha" → **Kizomba** in both STYLE and DANCER answers once Portuguese was detected. **Teu Toque** (123 BPM kizomba) went from "Cha-cha" → **Kizomba** in the DANCER answer.
- Phase A quick wins also landed: rewritten `QUESTION_STYLE` grounded in social-dance vocabulary (eliminated all Funk/Disco/Pop labels); DANCER `max_new_tokens` bumped to 1536 (zero truncations); onset-density tiebreaker added.
- Remaining issues: 144 BPM kizomba (Baila Kizomba Amor) still classified as Merengue — genuinely outside kizomba's BPM range, needs half-time detection. One bachata track's DANCER answer picked Zouk due to the kriol misdetection.
- Lesson: vocal language is a powerful disambiguation signal in the BPM-overlap zone (110–135 BPM), where tempo alone cannot distinguish bachata from cha-cha from kizomba. Even imperfect detection (6/7) meaningfully improves style picks.
- Lesson: the two-phase VRAM pipeline (load multimodal model → transcribe all tracks → free → load Ollama) is honest about laptop constraints but fragile under memory pressure. Works reliably when other applications are closed.
- See `docs/experiments/2026-04-12-audio-transcription-style-grounding.md` for full A/B comparison.

### 2026-04-20 — Style-differentiated analysis: bachata "1" vs kizomba beat clarity
- Extensive bottom-up exploration (Phase 15b) tested 7 onset-strength signal variants (full, percussive, harmonic, bass, kick, snare, RMS) across 16 eval tracks to find the kizomba downbeat.
- **Result:** best match rate was 50% (full/perc/snare tied). 3 of 6 annotated kizomba tracks have genuinely flat energy distributions across all 4 beat positions — no signal variant can separate the "1".
- **Bass/kick isolation performed worst** (17%) — opposite of the initial hypothesis. Kizomba bass patterns do not emphasize the downbeat.
- **Key insight:** this is not a detection failure but a **musical fact**. Kizomba does not acoustically emphasize one beat position over others. The dance reflects this: dancers have continuous freedom of interpretation.
- **Direction change:** the project now treats analysis goals as **style-dependent**:
  - **Bachata:** the "1" matters critically (4+4 mini-choreo structure). Downbeat detection already works well (all eval tracks consistently pick offset=0).
  - **Kizomba:** the beat *itself* matters more than the "1". New focus: beat clarity scoring, rhythmic texture, sections where the beat is easy vs. hard to hear.
- Updated roadmap, workstreams, MVP features, and design assumptions to reflect this shift.
- See `docs/experiments/23-2026-04-20-phase-15b-bottom-up-multiband.md` for detailed evidence.

### Next updates to add later
- implemented features
- test results on different music styles
- examples of good/bad model outputs
- changes in scope or product direction

---

## 16) Short version

> This project is a personal but broadly useful attempt to build a rhythm-learning assistant for dance/music practice, combining audio analysis with Gemma 4-based explanation so learners can better hear the beat, understand phrasing, and move with confidence.
