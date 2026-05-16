# How Rytmi Works

## The core idea in one sentence

Librosa (a signal processing library) analyzes your audio and extracts numbers — tempo, beat positions, onset times. Those numbers get formatted into a text prompt and sent to Gemma, which reads them like a music teacher reading a student's analysis sheet and explains what it sees.

**Gemma never hears your audio.** It only reads a structured text summary of what the DSP found. Yes — it's literally just a bullet list of numbers turned into a string.

---

## The two layers

### Layer 1: DSP (notebooks 01–03)

This is classical signal processing. No AI, no neural networks — just math on the audio waveform.

```
audio file (wav/mp3)
    │
    ▼
librosa.load()          → raw samples (a numpy array of floats)
    │
    ├─ onset_detect()   → timestamps where sounds begin (e.g., each clap, each drum hit)
    ├─ beat_track()     → timestamps of regular beats + estimated BPM
    ├─ onset_strength() → a curve showing "how likely is there an onset here" over time
    │
    ▼
RhythmAnalysis          → a Python dataclass holding all of the above
```

For the synthetic 120 BPM click track, this produces something like:
- Tempo: 120.0 BPM
- 20 beats at times [0.0, 0.5, 1.0, 1.5, ...]
- 20 onsets at roughly the same positions
- Inter-onset intervals: [500ms, 500ms, 500ms, ...] (evenly spaced)

These are honest measurements from the audio signal. They can be wrong (especially on complex music), but they are grounded in actual audio data.

### Layer 2: LLM (notebook 04)

Gemma is a text model. It cannot process audio. So we bridge the gap by **converting the DSP numbers into a text prompt**.

Here is the literal prompt that `explain_rhythm()` sends to Gemma (from `prompts.py`):

```
System: You are a music teacher explaining rhythm concepts. Be concise
and practical. Use musical terminology when helpful. When discussing
rhythm patterns, describe how a musician would count them. Base your
answers only on the analysis data provided — do not invent details.

User: Here is the rhythmic analysis of an audio clip:

- Duration: 10.0 seconds
- Estimated tempo: 120 BPM
- Number of detected beats: 20
- Number of detected onsets: 20
- Beat times (first 8, seconds): 0.00, 0.50, 1.00, 1.50, 2.00, 2.50, 3.00, 3.50 ... (20 total)
- Inter-onset intervals (first 8, ms): 500, 500, 500, 500, 500, 500, 500, 500 ... (19 intervals)

How would a musician count along with this rhythm? Give the counting
pattern (e.g. '1 and 2 and 3 and 4').
```

That's it. Gemma receives this text — the same way you'd describe a rhythm on paper to a music teacher — and writes back its interpretation.

Gemma is good at this because:
- It knows music theory from its training data
- The prompt gives it concrete data (BPM, beat spacing, onset density)
- The system prompt tells it to act as a teacher and stick to the data

Gemma is NOT:
- Listening to audio
- Doing beat detection
- Measuring tempo
- Doing anything with signal processing

---

## How the notebooks relate to each other

### They do NOT pass data between them

This is important: **each notebook is a standalone process**. They do not share memory, objects, or variables. When you open notebook 04, it does not receive a `RhythmAnalysis` object from notebook 02. There is no inter-process communication.

Instead, each notebook that needs audio data **loads the same wav file from disk and re-runs the analysis from scratch**. Here is what literally happens when you run each notebook:

```
Notebook 01: Audio Loading
    Loads: data/samples/click_120bpm.wav (from disk)
    Does:  load_audio(), trim_silence(), normalize()
    Purpose: Verify that audio loading works, play the file back

Notebook 02: Onset & Beat Detection
    Loads: data/samples/click_120bpm.wav (from disk, again independently)
    Does:  load_audio() → detect_onsets() → track_beats() → analyze()
    Purpose: Verify that DSP analysis works, print the numbers

Notebook 03: Visualization
    Loads: data/samples/click_120bpm.wav (from disk, again independently)
    Does:  load_audio() → analyze() → plot_analysis()
    Purpose: See the beats and onsets visually on a waveform

Notebook 04: Gemma Basics
    Loads: data/samples/click_120bpm.wav (from disk, again independently)
    Does:  load_audio() → analyze() → explain_rhythm()
    Purpose: Get Gemma to explain the rhythm in natural language
```

Every notebook starts from the same wav file on disk. Every notebook calls `load_audio()` and `analyze()` on its own. The shared thing between them is the **code** (the `rytmi` package installed in your venv), not data in memory.

### The notebooks are pedagogical, not a pipeline

The numbering (01, 02, 03, 04) reflects a learning sequence — each one introduces a new concept:

1. "Can I load audio?" (audio I/O)
2. "Can I extract rhythm?" (DSP)
3. "Can I see it?" (visualization)
4. "Can I get a text explanation?" (LLM)

But they are not stages of a data pipeline. You can run notebook 04 without ever opening notebooks 01–03. It will load the audio, run the DSP, and call Gemma all by itself.

### The only shared state is the filesystem

- The wav file lives at `data/samples/click_120bpm.wav`
- The library code lives at `src/rytmi/`
- Both are on disk and accessible to any notebook, script, or test

If you wanted to analyze a different audio file, you'd change the file path in whichever notebook you're running. There's no central configuration that links them.

---

## The handoff from DSP to LLM, in detail

This is the exact data flow inside notebook 04 when you call `explain_rhythm(result)`:

```
Step 1: You already have a RhythmAnalysis object (from calling analyze())
        It contains numbers: tempo=120.0, beats=[0.0, 0.5, 1.0, ...], etc.

Step 2: explain_rhythm() calls format_analysis_prompt()
        This function does nothing clever — it uses Python f-strings to
        insert the numbers into a text template:

        f"Estimated tempo: {tempo:.0f} BPM"   →   "Estimated tempo: 120 BPM"
        f"Number of detected beats: {n_beats}" →   "Number of detected beats: 20"

        The output is a plain string. You can see it yourself in notebook 04,
        section 6 ("Inspect the prompt").

Step 3: That string becomes the "user" message in a chat conversation.
        A "system" message is prepended: "You are a music teacher..."

Step 4: The chat messages are tokenized and fed to Gemma's generate() method.
        Gemma produces tokens one by one (this is the slow part on CPU).

Step 5: The output tokens are decoded back into a string and returned.
```

The bridge between DSP and LLM is literally `format_analysis_prompt()` — a function that turns numbers into a formatted string. There is no embedding, no feature extraction, no audio encoding. Just `f"{tempo:.0f} BPM"`.

---

## Two ways to run the LLM

### Option A: Local inference (default)

```python
from rytmi.llm import load_model, explain_rhythm

processor, model = load_model()  # downloads & loads Gemma locally
result = explain_rhythm(analysis, processor=processor, model=model)
```

Requires `pip install rytmi[llm]` (torch, transformers, accelerate, bitsandbytes).

The model (Gemma 4 E2B-it, 5.1 billion parameters) doesn't fit in your GPU's VRAM with 4-bit quantization due to a library compatibility issue between accelerate and bitsandbytes. So it falls back to running entirely on CPU in bfloat16 precision. CPU inference for a 5B parameter model is roughly 10–50x slower than GPU inference.

On Kaggle with a T4 GPU (16 GB VRAM), the larger E4B-it model runs on GPU and will be much faster.

### Option B: Cloud / API endpoint

```python
from rytmi.llm import load_cloud_model, explain_rhythm

client, model_id = load_cloud_model(
    model_id="google/gemma-4-E2B-it",
    base_url="http://localhost:8000/v1",  # vLLM, Ollama, or any OpenAI-compatible server
)
result = explain_rhythm(analysis, processor=client, model=model_id)
```

Requires `pip install rytmi[cloud]` (just the `openai` package).

This works with any server that exposes an OpenAI-compatible chat completions API — vLLM, Ollama, llama.cpp, or cloud providers. You can also set `RYTMI_API_BASE_URL` and `RYTMI_API_KEY` environment variables instead of passing them directly.

### Both options use the same downstream code

The key design choice: `load_model()` returns `(processor, model)` where model is a HuggingFace object, while `load_cloud_model()` returns `(client, model_id)` where model is a string. The `generate()` function checks `isinstance(model, str)` to decide which backend to use. Everything downstream — `explain_rhythm()`, `explain_all()` — works identically with either backend.

One API distinction matters for demo reliability: `explain_rhythm()` is the raw single-question helper. It formats one prompt, sends it to Gemma, and returns the model's draft unchanged, which is useful for inspection and limitation evidence. Higher-level learner-facing paths such as `explain_all()` and the demo notebooks apply deterministic verifiers where exact structure matters, including section lines and kizomba drill P# ranges.

---

## What Gemma is actually useful for here

Given that Gemma only sees numbers, its value is in **musical interpretation** — the same thing a teacher does when a student says "I measured 120 BPM with beats every 0.5 seconds":

- **Counting**: "You'd count this as 1-2-3-4" (mapping BPM + beat spacing to a counting pattern)
- **Time signature**: "This is likely 4/4" (inferring from beat groupings and onset density)
- **Style**: "At 120 BPM with even spacing, this resembles a march or basic pop beat"
- **Difficulty**: "This is a 1/5 — perfectly even beats are the simplest rhythm"
- **Exercises**: "Try clapping along while counting out loud"

The quality depends on how much useful data the DSP layer provides. A simple click track gives very little for Gemma to work with. Real music with varying onset density, syncopation, or tempo changes would give it more to interpret.

---

## Likely downbeat / "1" detection

Finding the "1" — the start of each measure — is a separate problem from finding the beats. Beat tracking gives you a regular pulse; downbeat detection has to decide *which* of the pulses to call "beat 1". The DSP layer in `detect_downbeats()` does this with an explainable heuristic and reports a confidence score so the learner can see when the guess is shaky.

### The heuristic in plain words

1. Sample the **onset strength envelope** at each detected beat. Beats that coincide with strong transients (e.g., a kick drum) get a high value.
2. For each candidate "1" position in a measure (offsets `0..beats_per_measure-1`), take the **mean** onset strength of the beats that would be downbeats under that grouping. There are 4 candidates in 4/4.
3. The offset with the highest mean wins. Its beat times become the reported downbeats.

Mean (not sum) matters: with e.g. 18 detected beats and a 4-beat measure, two of the four offsets will hold 5 beats and two will hold 4. Sum-based scoring would systematically favor the offsets that happened to capture the extra beat — pure offset-count bias, not signal. Mean removes that bias.

### The confidence score

A bare "winner offset" is not enough — on a featureless click track every offset scores nearly the same, and the winner is essentially a coin flip. The project values honest uncertainty, so `detect_downbeats()` also returns a confidence in `[0.0, 1.0]` built from **two complementary signals**:

- **margin** — `(best - runner_up) / best`. How clearly the winning offset beats the next-best one. Low when two offsets are tied (e.g., a 2/4 feel scored against a 4/4 measure: offsets 0 and 2 carry the strong beats equally, and the "1" is genuinely ambiguous).
- **dominance** — `(winner_ratio - 1/bpm) / (1 - 1/bpm)`. How far the winner's share of the total mean strength rises above a uniform-chance baseline. Low when the winner is only marginally above noise.

The two signals are combined as the **geometric mean** `sqrt(margin × dominance)`. Both must be present for high confidence: a confident "1" needs the winner to clearly outscore *both* the runner-up *and* the chance baseline. If either component is near zero, confidence collapses.

What the numbers mean in practice:

| Confidence | Interpretation |
|---|---|
| `~0.0` | No usable evidence — uniform or silent signal, or top two offsets are tied |
| `~0.1–0.2` | Weak hint, treat as a guess |
| `~0.3–0.5` | Plausible — one offset is clearly winning on synthetic bass-accented test signals |
| `~0.7+` | Strong dominance — would require both a clear winner and a decisive margin on real music |

These bands are calibrated against synthetic clicks; real-music calibration is future work.

### Why this design

The project specifically wants to **avoid presenting weak beat guesses as certain facts**. A single-signal confidence (e.g., dominance alone) is blind to the most diagnostic ambiguity case — tied tops — and would happily report moderate confidence on a 2/4 feel, telling the learner "the 1 is here" when it could equally be elsewhere. Combining margin and dominance via a geometric mean gives a metric that says "I don't know" in *both* failure modes (noise-like signal AND structured-but-ambiguous signal), which is what an honest tutor would do.

The heuristic stays entirely DSP-grounded — no Gemma involvement, no learned components — so it is reproducible, fast, and easy to explain to a learner who asks "why do you think the 1 is here?"

---

## Rhythm features for style disambiguation

The DSP layer computes a `RhythmFeatures` dataclass with concrete numerical signals that help Gemma tell apart styles with overlapping BPM ranges (e.g., bachata vs cha-cha at 120–130 BPM, kizomba vs zouk at 85–110 BPM).

### What gets computed

| Feature | What it measures | How it helps |
|---|---|---|
| `onsets_per_beat` | Onset count / beat count | Dense (>2.5) → bachata, salsa; sparse (<1.5) → kizomba, zouk |
| `beat_strength_pattern` | Mean onset strength at each beat position in a measure, normalized to [0,1] | Reveals accent patterns (e.g., strong 1 and 3 vs even) |
| `percussiveness` | Energy ratio: percussive component² / total signal² (via HPSS) | Percussive → bachata, salsa; smooth → kizomba, zouk |
| `spectral_centroid_mean` | Average spectral brightness in Hz | Bright → crisp percussion; dark → bass-heavy smooth styles |
| `tempo_stability` | Coefficient of variation of inter-beat intervals | Near 0 = metronomic; higher = rubato or live feel |
| `ioi_median_ms` / `ioi_std_ms` | Median and standard deviation of inter-onset intervals | Tight clustering → regular patterns; wide spread → syncopation |

### Half-time detection

When `tempo > 140 BPM`, the analysis also reports `tempo_half = tempo / 2`. This appears in the prompt as a note, allowing Gemma to consider that a 144 BPM track might actually be 72 BPM kizomba played double-time.

### How it reaches Gemma

`_format_rhythm_features_section()` in `prompts.py` renders the features as labeled bullet points with interpretive annotations (e.g., "sparse — typical of kizomba, zouk"). These appear in the prompt between the vocals section and the noise disclaimer. When `rhythm_features` is None (e.g., older callers), the section is empty and the prompt is unchanged.

### Known limitations

- **Tempo octave errors are not corrected.** If `librosa.beat.beat_track` locks onto half- or double-time, the whole `beats_per_measure` accounting shifts. The metric will look internally consistent but be musically wrong. Future work: a sanity check or alternative tempo hypotheses.
- **Only one `beats_per_measure` is tried at a time.** The function takes 4 by default and never compares 3/4 vs 4/4 vs 6/8. The heuristic itself is `bpm`-agnostic, so adding a "score 3 and 4 separately, pick the higher confidence" wrapper would be a clean future extension.
- **Synthetic-only validation so far.** All current tests use synthetic click tracks (uniform, bass-accented, 2/4-feel). Real bachata, kizomba, and salsa tracks have not been measured yet — that work belongs to the evaluation workstream.
- **No sub-frame timing correction.** Beat strengths are sampled by linear interpolation. A windowed max-pool around each beat could absorb small beat-tracker timing errors, but in synthetic testing it did not change results meaningfully and was left out.
- **The confidence score is not yet surfaced to the visualization or to Gemma prompts.** It lives on `RhythmAnalysis.downbeat_confidence` but is not shown to the learner yet. Wiring it through is the natural next step.

---

## STYLE→DANCER chaining

When `explain_all()` runs all question templates, it explicitly generates the **STYLE** answer first, then prepends it as context to the **DANCER** question:

```
Context: this track was identified as Bachata at 125 BPM with syncopated guitar.

You are a dance coach analyzing THIS specific track...
```

This reduces disagreements between the two answers. Previously, STYLE and DANCER were independent calls that could pick different styles from the same data (e.g., STYLE=Bachata but DANCER=Cha-cha). The chaining makes DANCER aware of what STYLE already concluded.

The single-question `explain_rhythm()` API is unchanged — chaining only applies to `explain_all()`.

---

## Vocal clip selection with retry

The transcription pass (`transcribe_vocals()`) selects a ~20-second audio clip for language detection. If the first clip returns "instrumental" or "unknown" (e.g., because it landed on an instrumental break), it retries with clips from later in the track:

1. **Attempt 1**: clip starting at 15% into the track (default onset-density argmax)
2. **Attempt 2**: clip starting at 40% into the track
3. **Attempt 3**: clip starting at 60% into the track

The first result with a recognized language is returned. If all attempts fail, the last result is returned (status quo behavior).

---

## Empty response retry

Both the cloud (`_generate_cloud()`) and local (`_generate_local()`) generation backends retry once with `temperature=0.5` if the initial response is empty or whitespace-only. This handles occasional blank outputs from the model without requiring manual intervention.

---

## Cloud endpoint compatibility — what you need to know

This section documents real issues encountered when calling Gemma 4 over OpenAI-compatible cloud endpoints, and what the code does to handle them.  If you are writing the Kaggle submission story, this belongs in the "challenges and technical choices" part of the writeup.

### The three deployment variants

At the time of writing, cloud providers typically expose Gemma 4 26B in one of two forms:

| Suffix | What it does | Typical model ID |
|---|---|---|
| `-it` | Instruction-tuned, direct answer | `google/gemma-4-26b-a4b-it` |
| `-it:thinking` | Same base, but performs internal chain-of-thought before answering | `google/gemma-4-26b-a4b-it:thinking` |

The `-it` variant is the standard choice for Rytmi's use case. The thinking variant can produce higher-quality reasoning on hard questions but comes with practical complications (see below).

### Problem 1: Gemma has no native `system` role

The OpenAI chat API supports a `system` message as a separate role, placed before the first `user` message.  Gemma's chat template was trained without a dedicated system turn.

Many cloud providers that serve Gemma silently return an **empty response** or low-quality output when a `system` role message is present.  This is not an API error — the request succeeds with HTTP 200 and `finish_reason: stop`, but `content` is an empty string.

**How the code handles it** (`_build_cloud_messages()` in `llm.py`):

```python
# For any model ID containing "gemma", fold the system prompt into the user turn:
messages = [{"role": "user", "content": f"{system_prompt}\n\n{prompt}"}]

# For everything else, use the standard two-turn format:
messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": prompt},
]
```

Gemma's chat template applies a `<start_of_turn>user` token to the entire merged message, which is exactly how Gemma was trained to receive instructions.  The model sees the system guidance without any role-formatting mismatch.

### Problem 2: Thinking models exhaust the token budget before writing an answer

The `:thinking` variant runs an internal reasoning trace **before** generating its answer.  Both the reasoning trace and the answer count against the `max_tokens` limit.  The trace scales with prompt complexity — a short test prompt ("what is 4/4?") may consume 200–400 reasoning tokens; the actual Rytmi analysis prompt (with beat arrays, section data, and style context) can push that into the thousands.

With a modest `max_tokens=1024`:
- Simple prompt → reasoning trace fits → answer is written → works
- Complex analysis prompt → reasoning trace fills the budget → `finish_reason: length` → `content` is empty

This looks identical to Problem 1 from the outside: a 200 OK response with an empty `content` field and no Python exception.

**How the code handles it** (`_effective_max_tokens()` in `llm.py`):

```python
if ":thinking" in model_id.lower():
    return max(requested * 4, 8192)  # floor of 8 192, 4× multiplier
```

The multiplier ensures the budget is large enough for both the trace and the answer.  The floor of 8 192 applies even for the smallest `max_new_tokens` values used in the notebook.

### How to diagnose empty responses

The `CLOUD_DEBUG` flag in `llm.py` prints the full request and response for every cloud call:

```python
import rytmi.llm as llm
llm.CLOUD_DEBUG = True   # set before running explain_rhythm()
```

When debugging, look at `finish_reason` in the response:

| `finish_reason` | Likely cause |
|---|---|
| `stop` + empty `content` | System role rejected (Problem 1) or response genuinely empty (rare) |
| `length` + empty `content` | Token budget exhausted by thinking trace (Problem 2) |
| `stop` + non-empty `content` | Working correctly |

The smoke-test cells at the bottom of each `05_batch_analysis` notebook send three variants of the same prompt (user-only, system+user, system-folded-into-user) and print `finish_reason` and `content` for each, making it straightforward to confirm which format your provider accepts.

### Practical recommendations

- **For the Kaggle demo / eval run**: use the `-it` variant.  It reliably produces good rhythm explanations without the reasoning-trace overhead.
- **For the thinking variant**: it is usable but only on providers that surface the reasoning trace (some return it in `message.reasoning` or `message.reasoning_content`).  The 4× token multiplier in the code makes it functional, but expect 3–10× higher token costs per call.
- **For Ollama / local vLLM**: the system role issue does not apply — local servers apply the Gemma chat template correctly and the system prompt works as written.  The `_build_cloud_messages()` folding still fires (because the model ID contains "gemma"), which is harmless — Ollama produces correct output either way.

---

## Section-aware timeline visualization

`plot_timeline()` and the interactive HTML player render each track as a waveform with colored bands for **phases** — runs of consecutive same-label `SongSection` entries merged into a single display unit (`intro ×1`, `main ×3`, `break ×1`, …). The six phase labels each have a fixed color: intro/outro in cool greys, main in neutral, break/build/peak in warm tones. Labels are placed above the waveform as `S1`, `S2`, `S3` with the phase name, count, and start/end in seconds.

### Energy encoding (Phase 4.5)

Each `SongPhase` carries the list of per-section energy levels (`low` / `medium` / `high`) computed from RMS ratios. The timeline renders each band with an alpha proportional to that phase's **dominant** energy — the mean of the section energy ranks, rounded half-up so a tie like `[medium, high]` is drawn as `high`:

| Energy | Alpha | Chip |
|---|---|---|
| low | 0.15 | `▁` |
| medium | 0.30 | `▄` |
| high | 0.50 | `█` |

The chip is appended to the `S#` label (`S2: main ×3 ▄`) and the legend adds one grey swatch per energy level actually present in the phases — so a track with only `low`/`medium` phases does not get a spurious `high` entry. Tracks without any `phases` field stay completely backward-compatible: no band patches, no energy entries in the legend.

### Phrase-grid snapping

Learners naturally think in 8-count phrases (two 4/4 measures), so section boundaries that land mid-phrase look and feel wrong even when the underlying novelty peak is real. `analyze()` now takes a `snap_to_phrase_grid: bool = True` flag. When enabled, `_snap_boundaries_to_phrases()` runs after `detect_sections()` and nudges each **interior** section boundary (not the track's first start or last end) to the nearest phrase boundary on the beat grid — `beats.times[::phrase_length]`. A safety threshold of 8 beats prevents boundaries from being moved further than one phrase, and the snap enforces monotonicity so neighboring sections never collapse into zero-length slivers.

Pre-snap boundaries are preserved on each `SongSection` as `raw_start_s` / `raw_end_s` whenever snapping actually moved them. These flow into the diagnostic helper so the before/after drift can be inspected.

### Section diagnostic helper

`describe_sections(analysis)` returns a formatted text table — one row per `SongSection` — with:

- section index, label, and energy level
- start/end in seconds **and** in the `P#` / `M#` coordinates the notebook timeline uses
- drift in beats from the nearest phrase boundary (marked with `*` when snapping moved the boundary)
- duration in seconds and phrases
- the source signals behind the boundary: RMS ratio vs global mean and onset density (onsets per beat) over the section

It is a pure output helper — no algorithm changes — and is intended to be called from notebooks (see `05_batch_analysis.ipynb`) so learners can answer "why is this section here?" by looking at the same signals the DSP used.

### Percentile-based energy classification (Phase 5)

Real dance music has a compressed dynamic range: the loudest and quietest sections of a bachata or kizomba track are rarely more than ±25% away from the global mean. The earlier fixed-ratio classifier (`< 0.6×` → low, `> 1.3×` → high) almost never fired on real tracks, so every section collapsed to `medium` and the label classifier lost most of its signal.

`_classify_section_energies()` replaces that with a **per-track percentile** classification. Given the list of per-section RMS ratios for a track, it puts sections below the 30th percentile into `low` and above the 75th percentile into `high`, with absolute guardrails so a flat track does not get a spurious low/high split just from percentile noise: a section must *also* sit below `0.85 × global` (for low) or above `1.10 × global` (for high). Tracks with fewer than 4 sections fall back to the legacy per-section fixed-ratio path so synthetic click-track fixtures stay stable.

### Signal-aware section labels (Phase 5)

With percentile energies in place, `_label_sections()` no longer decides break/peak/build from the collapsed 3-bucket category — it reads the raw per-section RMS ratio and onsets-per-beat directly, compared against the **track medians** so a kizomba break is still allowed to be quieter than a bachata main:

- **peak** — `rms_ratio > 1.05 × track_median_rms_ratio` AND `opb > 1.00 × track_median_opb` AND the highest-RMS section in the middle half of the track.
- **build** — a `main` section immediately before a `peak` with strictly rising RMS vs its predecessor.

`merge_adjacent_sections()` also now splits a run of same-label sections when the per-section energy category changes on both sides of the split by at least 2 sections, so a 14-section `main` run with a high-energy middle surfaces as three phases instead of one without inventing any new boundaries.

### HPSS-based break classification (Phase 6)

Global RMS alone can't distinguish a kizomba **melodic drop** (the bass and melody drop out but the tumba / congas keep playing so onset density stays high) from a bachata **full drop** (everything thins out at once). Phase 6 runs [`librosa.effects.hpss`](https://librosa.org/doc/main/generated/librosa.effects.hpss.html) once per track in `detect_sections()` to split the audio into harmonic and percussive components, then attaches each section's per-component mean RMS (over the track-global mean) as `harm_ratio` and `perc_ratio` on `SongSection`. The four-branch break classifier reads those ratios alongside the existing `rms_ratio` and `opb`, against the track medians, and surfaces which branch fired via the `break_branch` field:

- **melodic** — `harm < 0.70 × median_harm` AND `perc > 0.85 × median_perc`. Classic kizomba melodic drop; Phase 5 could only see it indirectly if RMS also dipped.
- **percussive** — `perc < 0.70 × median_perc` AND `harm > 0.85 × median_harm`. Rare inverse where percussion drops but the melody carries.
- **severe** — `harm < 0.50 × median_harm` AND `perc < 0.50 × median_perc`. Both components collapse regardless of `opb`, catching busy-but-thin drops (e.g. *Filomena Maricoa Teu Toque* sec 13) that the old moderate branch missed because `opb` stayed high.
- **full** — `rms_ratio < 0.85 × median_rms` AND `opb < 0.70 × median_opb`. Classic bachata "everything thins out", and the fallback for legacy synthetic fixtures with no HPSS signal.

`describe_sections()` shows `H×` and `P×` columns on every row and renames break rows to `break[branch]` (e.g. `break[melodic]`, `break[severe]`) so the learner can read *why* each break fired.

A second Phase 6 helper, `_split_long_runs_on_phrase_shifts()`, inserts phrase-aligned boundaries inside long individual `main` sections where per-phrase RMS shifts exceed a local threshold (`max(0.18, 90th percentile)` of the in-section per-phrase diffs). Narrow scope by design: only single `main` sections ≥ 4 phrases / 24 s are candidates, never multi-section same-label runs — walking multi-section runs in an earlier iteration created slivers near existing interior boundaries and destabilised the track-median, flipping stable `main` sections into false-positive `break[melodic]`. On the 10-track eval set it mostly no-ops, which is fine — it only fires when the global novelty curve misses sub-structure inside a long main run.

### Downbeat-anchored phrase grid (Phase 7)

Many dance-video tracks are ripped from YouTube and start partway through the song's intro, so the first beat in the mp3 is not beat "1" of the musical phrase. `detect_downbeats()` already computed `best_offset` (which beat index within a measure has the strongest rhythmic evidence for being the downbeat), but the value was discarded at the return site.

Phase 7 exposes `best_offset` as a fourth return element and confidence-gates it: when `downbeat_confidence >= 0.25`, the phrase grid anchors at `beats.times[offset::phrase_length]` instead of `beats.times[::phrase_length]`. All downstream consumers — `_snap_boundaries_to_phrases()`, `describe_sections()` (P/M numbering, drift calculation), and `plot_timeline()` (beat/measure/phrase labels) — use `rel = beat_idx - offset` arithmetic.

When `offset > 0`, beats before the first downbeat are rendered as **pickup beats** (grey, lighter alpha) in the timeline visualization, with a dotted purple marker half a beat before the first real downbeat. `describe_sections()` shows a header line with the offset value and confidence.

On the current 10-track eval set all tracks have downbeat confidence below 0.25, so the offset is gated to 0 and behavior is unchanged from Phase 6. The infrastructure is in place for when either the confidence metric improves or tracks with clearer downbeat evidence are added.

See [eval-set-guide.md — "Why paired tracks matter"](eval-set-guide.md#why-paired-tracks-matter--the-find-1-from-mid-song-problem) for the full dance-floor rationale behind cut/official pairings.

### Vocal activity envelope (Phase 9)

Some boundary errors are easiest to see through vocal presence rather than RMS or HPSS. Long instrumental intros get mislabelled as `main` / `break[full]` because their pre-vocal energy still "looks" like the rest of the track; outros that start after the last chorus are slow to surface because the instrumental backing hasn't dropped yet.

`rytmi.vocal_activity` produces a `VocalActivityEnvelope` (per-frame `rms` + `active` boolean) behind a `VocalActivitySource` protocol. Two implementations ship:

- **`DemucsVocalActivity`** (default) — runs Demucs v4 `htdemucs` (~80 MB model), keeps the vocals stem, computes a per-frame RMS with `hop_length=512`, and thresholds at `max(0.003, 0.30 × p75(rms))`. Disk-cached under `cache/vocals/<sha1>.demucs.npz` so re-analysis is instant.
- **`GemmaVocalActivity`** (experimental) — windows the track into ~30 s clips and asks Gemma 4 E4B audio a one-word YES/NO vocal-presence question per window via the same loader `transcribe.py` uses. Coarser time resolution (one value per window) but keeps the "Gemma central" Kaggle-demo posture and provides a fallback when Demucs isn't installed.

`default_vocal_activity_source(prefer="demucs"|"gemma"|"none")` returns a chained source that falls through until one produces a non-None envelope. Every implementation returns `None` on any failure (missing dependency, model load error, runtime exception), so the pipeline stays functional without vocal extraction — the downstream `_extend_intro_to_first_vocal` and `_contract_outro_to_last_vocal` passes simply no-op.

Phase 12b listening pass (see [`experiments/19-2026-04-19-phase-12b-vocal-source-ab.md`](experiments/19-2026-04-19-phase-12b-vocal-source-ab.md)) compared both variants across the 10-track eval set. `GemmaVocalActivity` produces more section boundaries on every track, but on audition those extras were routinely wrong: main ↔ instrumental flipped wholesale on Grupo Extra (M48–M92) and drifted by ~8 counts on Baila Kizomba Amor. Demucs stays the recommended default; gemma remains opt-in for experiments and for the "Gemma central" demo posture, not for production section labelling.

When an envelope is passed into `analyze(audio, vocal_env=env)`, two vocal-aware passes run after the Phase 8 signal-aware boundary adjustments:

- `_extend_intro_to_first_vocal` grows the intro forward to the last pre-vocal phrase (first phrase with ≥ 20% active frames). Capped at `_INTRO_MAX_EXTEND_PHRASES=12` to bound the blast radius. Absorbs any fully-contained subsequent sections; clips the first straddling section's start forward.
- `_contract_outro_to_last_vocal` is symmetric. Pulls the outro start back to `last_vocal_phrase + 1 + grace_phrases`, capped at `_OUTRO_MAX_CONTRACT_PHRASES=8`. Clips the previous section's end forward.

### Downbeat-confidence v2 (Phase 10)

Phase 7 computed `best_offset` from a single signal — the full-band `onset_strength` averaged per beat position. On tracks where a syncopated hit at the end of the previous bar looks onset-strong, the "real" downbeat loses by a small margin, so `best_offset` points the wrong way and confidence stays low.

Phase 10 adds a **kick-drum band vote**: `_low_band_beat_position_strengths()` 4th-order-bandpasses the audio to 40–150 Hz (scipy `butter` + `filtfilt`), runs `librosa.onset.onset_strength` on the filtered signal, and groups the result per beat position. The filtered signal is silent on pure-sine / non-percussive tracks, in which case this source contributes zeros and the fusion falls back to the Phase 7 behaviour.

> **Gotcha (fixed in Phase 28 P5d, 2026-04-26):** `librosa.onset.onset_strength` defaults to a mel spectrogram with `n_mels=128, fmin=0`, which puts the lowest mel filter centre at ~80 Hz. On a 40–150 Hz BPF input that means the envelope is silently all-zero (librosa emits an easy-to-miss 'Empty filters detected in mel frequency basis' warning). The kick-band call now passes `fmin=20.0, n_mels=8, fmax=hi*1.5` so the filterbank actually has bins in the kick range. Same fix applied to `_track_kizomba_batida`'s 150 Hz LPF and to the bass-stem evidence channel in `detect_downbeats`. See [experiments/28-2026-04-23-phase-28-tap-ground-truth.md](experiments/28-2026-04-23-phase-28-tap-ground-truth.md) for the full audit.

The two signals are combined by **scale-normalization** — divide each per-offset score array by its own max (flat inputs → zeros) and add. Rank-averaging would spread a flat signal across [0, 1] and produce false confidence on uniform-click tracks; scale-normalization preserves each signal's within-array decisiveness.

Confidence is still `sqrt(margin × dominance)` on the combined score, but now with a **disagreement penalty**: when kick and onset pick different offsets and kick has any signal at all, confidence is halved. Keeps the confidence gate honest when the two votes contradict each other — worst case, we keep the Phase 9 behaviour.

The `0.25` confidence gate is unchanged, and on the current 10-track eval set no track clears it even with the kick-band signal added. What changed is the **raw `best_offset`**: it's non-zero on 5 of 10 tracks where Phase 9 picked all zeros, so the signal is meaningfully more diagnostic. When the eval set expands to semba / zouk (strong kick-led downbeats), or if the gate is re-calibrated lower based on listening evidence, the re-anchoring should fire on more tracks.

### Instrumental passages (Phase 10)

Mid-song passages where **vocals drop but instruments continue at full strength** (the "instrumental bridge") were previously mis-labelled as `main` / `break[melodic]` — RMS stays high, so HPSS alone can't catch them. The Phase 9 vocal envelope already knows these passages are vocal-quiet.

`_relabel_vocal_drop_instrumentals()` walks phrase windows fully inside each non-intro/non-outro section and identifies contiguous runs of phrases where:

- `vocal_active_ratio < _INSTRUMENTAL_MAX_VOCAL_ACTIVE_RATIO=0.25` (vocals absent), AND
- `rms_ratio >= _INSTRUMENTAL_MIN_RMS_RATIO=0.75` (energy still present — not a break).

Runs of ≥ `_INSTRUMENTAL_MIN_PHRASES=2` become new `instrumental` sections; whole-section matches relabel in place to avoid sliver boundaries. The pass runs inside the `if vocal_env is not None` block, after `_contract_outro_to_last_vocal` and before `_merge_same_branch_break_chains`, so it only fires when the vocal signal is trustworthy.

A Phase 8 `peak` with vocals quiet but energy high gets **demoted** to `instrumental` — which is the correct outcome for tracks like *Baila Kizomba Amor* at ~194 s, where the user's listening pass identified the section as "instrumental bridge" rather than "peak". A peak with vocals present (`vocal_active_ratio ≥ 0.25`) stays untouched.

Palette: `SECTION_COLORS["instrumental"] = "#16a085"` (teal — ≥ 40-channel RGB gap from every other label, verified by `test_section_colors_instrumental_distinct`).

### Prompt distinctiveness constraints (Phase 10)

Larger LLMs (Gemma 26B MoE and up) tend to paraphrase the analysis data into style-level platitudes — "this is a typical 4/4 bachata", "maintain your counting on 1-2-3-tap" — even when the track has an obvious distinguishing feature visible in the numbers. Phase 10 adds three layers of friction:

1. **`_format_distinct_features_section()`** surfaces 1–3 bullets in the analysis block when a track is a numeric outlier: tempo above/below the style's `bpm_range`, percussiveness > 0.65 or < 0.25, onsets-per-beat > 3.0 or < 1.0. Returns empty for middle-of-the-road tracks so typical tracks aren't padded with a "this track is typical" non-statement. Lives between `{rhythm_features_section}` and `{sections_block}` in `RHYTHM_ANALYSIS_TEMPLATE`.
2. **`QUESTION_SECTIONS` rewritten** into a strict `P#: <start>s-<end>s, <label> — <coaching>` line format. The coaching text "MUST reference at least one specific number from the analysis above" (timestamp, BPM, onset density, percussiveness, energy ratio, accent pattern, rms ratio); generic coaching sentences without numbers "must be deleted". A phase with no distinctive feature gets a 5-word fallback `continues the <prev_label> feel` rather than padding.
3. **`QUESTION_DANCER` + `QUESTION_SONG_ARC` + `DEFAULT_SYSTEM_PROMPT`** carry a parallel numeric-anchoring rule. `QUESTION_SONG_ARC` additionally asks for 1–2 sentences of **novelty** — what distinguishes THIS track from other same-style same-tempo tracks.

These are upstream guardrails, not a hard filter — smaller models may still paraphrase. But on well-aligned models the format is sticky, and the side-by-side comparison vs. `tmp/05_batch_analysis-26B.phase9.txt` is how we'll measure whether the boring-output problem is actually better.

### Vocal-stem RMS v2 (Phase 11)

Phase 9 thresholded the Demucs vocal stem at an absolute `_VOCAL_ACTIVE_THRESHOLD = 0.30` × per-track 75th-percentile RMS, with a `0.003` absolute floor. The number was chosen by hand and didn't generalise: tracks with a quieter mix slipped under the threshold (Baila Kizomba Amor's ~194 s passage), and tracks with a wide dynamic range over-flagged near-silent breaks.

Phase 11 swaps in the Ricci et al. 2025 recipe (arXiv 2506.15514) for music vocal-activity detection:

1. Convert the per-frame Demucs vocal RMS to dB: `rms_db = 20 * log10(rms + ε)`.
2. Take the per-track mean dB level.
3. Binary threshold: `rms_db > mean_db − 18 dB` AND `rms_db > _VOCAL_ACTIVE_FLOOR_DB = -60 dB`.
4. Smooth the binary signal with a 3 s moving average (`scipy.ndimage.uniform_filter1d`, mode `nearest` so boundary frames don't fade).
5. Re-binarise at 0.5.

The 18 dB headroom above the per-track mean accommodates per-track loudness without manual tuning; the smoothing absorbs short dips inside vocal phrases and the absolute floor blocks near-silence false positives. The downstream `VocalActivityEnvelope` shape is unchanged, so all Phase-9 vocal-aware passes (intro extension, outro contraction, instrumental relabelling) plug in unchanged.

Cache compatibility: the on-disk `.npz` cache stores the raw Demucs RMS (the expensive part) plus the derived `active` mask. On load, we keep the cached `rms` but **re-derive `active`** through the new threshold, so older caches transparently pick up the new thresholding without re-running Demucs.

### Downbeat v3 (Phase 11) — BeatNet fusion

Phase 10's kick-band signal raised raw `best_offset` accuracy on the eval set but couldn't lift any track above the `0.25` confidence gate. Phase 11 adds **BeatNet** (Heydari et al., ISMIR 2021) — a CNN+DBN downbeat tracker shipped on PyPI — as a third fusion ingredient:

- `_beatnet_beat_position_strengths(audio, beats, bpm)` lazy-imports BeatNet, stubs `pyaudio` (only needed for live-mic mode, which we never call), runs the offline DBN, and converts each predicted `beat_in_bar == 1` into a histogram aligned to the librosa beat grid. Returns zeros on any failure (import error, no filepath, runtime exception) so the fusion gracefully falls back to the Phase-10 onset+kick combination.
- Fusion: `combined = 0.5 × rank(beatnet) + 0.3 × rank(kick) + 0.2 × rank(onset)`, where `rank()` is rank-normalised within the per-offset score array. BeatNet dominates because it's the only signal trained directly on this task; kick and onset retain a vote because BeatNet's DBN can mis-fire on Afro-Latin grooves with off-beat snares.
- Confidence keeps the `sqrt(margin × dominance)` shape with a milder `× 0.7` disagreement penalty when BeatNet is present (still `× 0.5` for the older kick-vs-onset case) — the assumption is that two of three signals agreeing is meaningful, even if one disagrees.

Eval-set lift on the 10-track set, Phase 10 → Phase 11: Bachata Musicality `0.10 → 0.33`, Charbel Ben Ana `0.19 → 0.34`, Charbel Official `0.04 → 0.35`, Romeo Santos El Chaval `0.04 → 0.33`. Four tracks now clear the `0.25` gate and the Phase-7 phrase-grid re-anchoring fires on them. Three kizomba tracks (All Of Me, Baila, Teu Toque) remain below — they're the targets for Phase 12.

`madmom` (BeatNet's DBN backend) must come from upstream Git on Python ≥ 3.10 because the PyPI 0.16.1 release uses the removed `collections.MutableSequence`. Pinned in the new `downbeat` optional-dependency group.

### Spoken-intro detection (Phase 11)

Tracks like *Propuesta Indecente* open with **spoken dialog** rather than singing. The Phase-9 vocal-activity detector flags those windows as "vocal-active" (it's a voice), so the intro looks like a normal sung opening and the `QUESTION_SECTIONS` prompt produces sing-along coaching that doesn't fit. We want a distinct label so the prompt knows to treat the prefix differently.

Phase 11 adds `GemmaSpeechDetector` — a parallel of `GemmaVocalActivity` that asks the Gemma 4 E4B multimodal model a YES/NO question per 5 s window across the leading 60 s of the track:

> *"Is the voice in this audio primarily speaking or singing? Answer with only one word: YES if speaking, NO if singing."*

Per-window scores (`1.0 = speech`, `0.0 = singing`) are wrapped in the same `VocalActivityEnvelope` shape as the vocal detector, with `source = "gemma-speech"` and the same on-disk cache layout (`cache/<sha>.gemma-speech.npz`).

The downstream pass `_relabel_spoken_intro(sections, speech_env, phrase_times)`:

1. Looks at the leading section only when its label is `intro`.
2. Walks forward through phrase windows, computing the per-phrase `speech_active_ratio` via the same `_phrase_active_ratio` helper used by the vocal passes.
3. Counts the longest contiguous prefix of phrases with `speech_ratio > _SPOKEN_INTRO_MIN_SPEECH_RATIO = 0.6`.
4. If that prefix ≥ `_SPOKEN_INTRO_MIN_PHRASES = 2`:
   - whole intro qualifies → relabel in place as `spoken_intro`;
   - otherwise → split the intro into a `spoken_intro` prefix + `intro` suffix on the phrase-grid boundary.

Pipeline placement: runs after `_extend_intro_to_first_vocal` (so the intro boundary is settled) but before the outro/instrumental passes. The new optional `speech_env` parameter on `analyze()` defaults to `None`, so callers without a speech detector get the pre-Phase-11 behaviour exactly.

Palette: `SECTION_COLORS["spoken_intro"] = "#34495e"` (dark blue-grey — ≥ 40-channel RGB gap from `intro` teal-blue, `main` grey, and `outro` purple, verified by `test_section_colors_spoken_intro_distinct`).

### Regex grounding verifier (Phase 11)

Phase 10c's prompt rule that "every `P#:` line must cite a number" is upstream guidance — the model can ignore it. Phase 11d adds a **post-generation verifier** so a learner never sees a P# line without a numeric anchor.

`verify_sections_output(raw_answer, sections)` in `rytmi.prompts`:

1. Splits the raw answer into lines.
2. Matches each line against `_P_LINE_RE` — `P#:` or `P#-#:` prefix, an em-dash (or hyphen) separator, and a coaching tail.
3. Tests the **tail** against `_NUMERIC_ANCHOR_RE`, which accepts: timestamp seconds (`45s`, `2.5 sec`), BPM/Hz/percent, `M#`/`P#`/`S#` markers, `mm:ss` timestamps, ratios (`1.4 ratio`, `2.5x`), counts (`4 bars`, `8 phrases`), and bracketed accent patterns (`[1.00, 0.98, 0.97, 0.79]`).
4. Lines that pass go through unchanged. Lines that fail are replaced with the Phase-10c fallback `P#: <s>s–<e>s, <label> — continues the <prev_label> feel`, looking up the previous section's label from the `sections` argument.
5. Lines that don't match the P# shape (intro/outro sentences the prompt forbids but Gemma sometimes emits) are dropped from the cleaned output.

Returns a `VerifiedSectionsOutput` with `original`, `cleaned`, and `stats` (`total`, `passed`, `failed`, `pass_rate`).

`explain_all(verify_sections=True)` (default) wires this into the analysis pipeline: the cleaned answer is what the dict carries under `"sections"`, the original raw model output is stashed under `"sections_raw"`, and a one-line stat summary lands under `"sections_verified_stats"` for the experiment notebook to log. Setting `verify_sections=False` restores the pre-Phase-11d behaviour for tests and side-by-side comparison runs.
