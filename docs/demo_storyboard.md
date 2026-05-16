# Rytmi demo video storyboard

> **Target:** 3-minute pitch for the Gemma 4 Good Hackathon submission.
> **Working format:** screen recording with **captions / on-screen text overlays — no voice-over**. Sound-off review is the full experience, not a degraded one; the artifacts being demonstrated (Gemma outputs, section tables, architecture diagram) are themselves text, so a voice track would compete with what the viewer needs to read. Pre-render notebook outputs; do not run notebooks live during recording (cold-start LLM calls + Demucs separation are too slow for tight pacing).
> **Audience:** Kaggle judges plus general competition viewers. Some will dance, most won't. Some are technical, some aren't. Default to clear language, lean on the architecture insight rather than dance jargon.

## Caption style

- **6–12 words per beat**, max two short lines on screen at once. Captions need to be read *while* the visual sells itself; don't write paragraphs.
- **Don't caption text that's already on screen.** When a Gemma output, section table, or the architecture diagram is up, the caption job is to thread the architectural insight between those visual beats, not duplicate them.
- **Hold captions long enough to read.** Roughly 1 second per 3 words as a floor; pad extra time when the visual itself is dense.
- **Use the project's vocabulary verbatim** for the technical terms (`describe_sections`, `kizomba_tutor`, `verify_kizomba_drills_output`) — the audience includes engineers who will recognise them, and dancers who'll skip them without harm.
- The "Captions / on-screen text" sections below are the *narrative spine* — written as prose for clarity, but each block should be **chunked into 2–4 short captions per scene** during editing. Don't try to fit a whole paragraph on screen at once.

## Demo clips library (Phase 44)

Eight pre-rendered captioned MP4s ship in `demo_assets/output/`. Each is a 14 s window centred on a real DSP-detected transition, with the verbatim Gemma transition line baked into a bottom strip and a pink playhead animating across the timeline at song rate. They are the demo's primary "Gemma transitions, in context" visual: the audience hears 14 s of the song, sees the playhead cross the boundary, and reads exactly what Gemma said about that boundary — all simultaneously, no voice-over needed.

Built by `demo_assets/scripts/make_all_demo_videos.py` from a disk-cached `analyze(...)` result; full re-render of all 8 clips is ~2.5 min thanks to the analysis cache and the ffmpeg-overlay playhead (vs ~7.5 h for the matplotlib FuncAnimation predecessor).

| Stem | Style | Window | Boundary | Caption (verbatim Gemma) |
|---|---|---|---|---|
| `filomena_intro_to_main` | kizomba | 8–22 s | T1 intro→main @ 12 s | _"when the bass kicks in, walk-step the basic on the first clear bass hit."_ |
| `e_magia_intro_to_main` | kizomba | 30–44 s | (Phase 42 boundary fix story) | DSP-storytelling caption — Phase 42 demoted vocal-active false breaks |
| `e_magia_vocal_break` | kizomba | 159–173 s | T5 main→break @ 165 s | _"as the energy fades and the percussion thins, keep a small pulse in the body and listen."_ |
| `e_magia_alt_break` | kizomba | 135–149 s | T8 main→break @ 141 s | _"as the energy fades and the percussion thins, keep a small pulse, listen, and reset."_ |
| `teu_toque_alt_pre_break` | kizomba | 130–144 s | T5 main→break @ 138 s | _"keep a small pulse in the body and listen as the energy fades and the percussion thins."_ |
| `romeo_propuesta_break_to_main` | bachata | 31–45 s | T2 break→main @ 38 s | _"Restart your 1-2-3-tap on the next clear 1 when the bongo pattern kicks in."_ |
| `royce_corazon_main_to_outro` | bachata | 187–201 s | T4 main→outro @ 194 s | _"Contract your movement and finish on a clean 8 as the percussion thins and the güira drops out."_ |
| `mika_magico_break_to_main` | kizomba | 27–41 s | T2 short_break→main @ 34 s | _"when the bass kicks in, start your steady walk-step."_ |

Each clip exists in two variants: `timeline_<stem>.mp4` (no caption) and `timeline_<stem>_captioned.mp4` (with the Gemma caption strip). The plain variants are useful when the storyboard wants the timeline visual without competing text — the caption can be swapped in at edit time as on-screen overlay if needed.

**How to slot clips into Act 3:** the captioned variants are drop-in replacements for the "interactive HTML timeline + audio" beats — they are pre-rendered, pixel-stable across takes, and self-contained (audio + visual + caption in one file). The Act 3a §1:25 timeline beat and the Act 3a §1:50 unified-timeline beat are both natural landing spots. The bachata clips (Romeo, Royce) and the cross-kizomba Mika clip enable an optional Act 3c (cross-style or cross-track contrast) — see "Open question" below.

## Story arc (3 acts in 3 minutes)

```
0:00 ─ 0:30  Act 1 — the hook (problem)
0:30 ─ 1:00  Act 2 — architecture insight (DSP + Gemma split)
1:00 ─ 2:20  Act 3a — deep dive on Filomena _Teu Toque_ (seven Gemma modes for kizomba)
2:20 ─ 2:40  Act 3b — same pipeline, different feel (Charbel _E Magia_ contrast highlight)
2:40 ─ 3:00  Close — limitations as honest future work + links
```

## Act 1 — The hook (0:00–0:30)

**Captions / on-screen text** (chunked, hold each long enough to read):
> 1. (0:00–0:08) **"I wanted to hear the beat. It kept slipping."**
> 2. (0:08–0:18) **"Kizomba's pulse is subtle — heavy percussion lands on syncopated off-beats."**
> 3. (0:18–0:25) **"Generic beat trackers latch onto whatever's loudest. They confidently mislead."**

**Visual:**
- (0:00–0:25) A kizomba track plays (~10s of audible audio under captions 1–3). After caption 1, a generic beat-tracker click overlay starts hitting wrong beats — the "loud syncopation mistaken for the 1" failure mode made *audible* and visible.
- (0:25–0:30) Project name slide: _"Rytmi — DSP + Gemma 4 rhythm-learning prototype"_, subtitle _"helping dancers hear what the music is doing"_.

**Beat:** Lead with the *learner pain* — first-person stakes, not a feature pitch. Bachata is invisible in this Act; the demo's story is the kizomba learner's story.

## Act 2 — Architecture insight (0:30–1:00)

**Captions / on-screen text** (3 captions over 30s):
> 1. (0:30–0:42) **"Rytmi splits the problem in two. DSP listens. Gemma talks."**
> 2. (0:42–0:50) **"librosa detects beats, sections, beat-clarity, downbeat confidence. Gemma turns that into language a learner can use."**
> 3. (0:50–1:00) **"Tried Gemma-as-listener first. It missed obvious percussion. DSP earns its keep."**

**Visual:**
- (0:30–0:50) Architecture diagram animated in: audio file → librosa DSP → RhythmAnalysis → Gemma 4 prompt → explanation + coaching. **Recording note:** prefer a clean Excalidraw / Mermaid render over the writeup's ASCII-art block — ASCII reads awkwardly on video.
- (0:50–1:00) Optional inset: `RhythmAnalysis` dataclass visualization (the section table from `describe_sections`) appearing under the diagram so the viewer sees "this is the structured input Gemma gets".

**Beat:** The DSP/Gemma split is the spine of the project. The "tried Gemma-as-listener, it failed" beat earns the architecture's credibility; tightened to a one-liner so it lands as caption text.

## Act 3a — Filomena _Teu Toque_, end-to-end (1:00–2:20)

**Track:** Filomena Maricoa — _Teu Toque_ (kizomba, 92 BPM, energetic forward beat, severe break around 148s). 80-second walkthrough — seven Gemma modes, in the order they run in `notebooks/00_demo.ipynb`. Each segment's caption describes what the tool showed *me about this song*; the visual carries the kizomba-specific output.

Filomena is the **dense / forward-beat** half of a contrast pair completed by Act 3b. Showing the same pipeline on E Magia after this generalises the demo without overclaiming.

### 1:00–1:10 · `rhythm_anatomy` — what kind of music is this?

**Captions / on-screen text:**
> 1. **"First: what kind of music is this?"**
> 2. **"Two paragraphs on the genre — tempo, time signature, what carries the pulse."**

**Visual:** Two-paragraph genre intro from `00_demo_outputs.md`. Highlight the sub-style names briefly (Angolan kizomba, urbankiz, tarraxinha).

### 1:10–1:25 · `describe_sections` + interactive timeline — what's in the track?

**Captions / on-screen text:**
> 1. **"DSP names every section: intro, main, break, build, peak, outro."**
> 2. **"Plus `instrumental` — carved out by a Demucs vocal-activity envelope."**

**Visual:** Section table. Then the interactive HTML timeline with the cursor moving across the track (5–10s of audible Filomena under this beat). Section bands light up as the cursor enters them. **Phase-44 swap-in candidate:** [`timeline_filomena_intro_to_main.mp4`](../demo_assets/output/timeline_filomena_intro_to_main.mp4) (no caption variant) is a drop-in 14 s clip with the same waveform + section-band visual already rendered — use it instead of an HTML widget if a stable, takable artifact matters more than the cursor's interactivity.

### 1:25–1:40 · `listening_guide` — where will the pulse be hardest to follow?

**Captions / on-screen text:**
> 1. **"Where will the pulse be hardest to follow?"**
> 2. **"Two paragraphs: orient the ear, name the hard moment."**

**Visual:** `listening_guide` output. Highlight the difficulty-map sentence (the one that names the hardest moment in this song).

### 1:40–1:50 · `song_arc` — what makes this song's energy journey distinct?

**Captions / on-screen text:**
> **"What makes this song distinct? One sentence at the end says it."**

**Visual:** `song_arc` paragraph; brief highlight on the closing distinctive-feature sentence.

### 1:50–2:10 · `kizomba_tutor` + `kizomba_transitions` as a unified timeline

**Captions / on-screen text:**
> 1. **"Phase-by-phase coaching, anchored on per-section beat-clarity."**
> 2. **"Each `main` group named for its role: establishing, sustaining, building, returning, closing."**
> 3. **"Between every phase: a transition line. Anchored on what the music actually does at the boundary."**
> 4. **"Code identifies the boundaries. Gemma writes the lines. Code verifies they cover the song."**

**Visual:** The **unified timeline** — interleaved `P1, T1, P2, T2, … P8` block from `format_unified_timeline(...)`. This is the single most important visual in Act 3a; let it breathe.
- First, the polished `kizomba_tutor` lines fade in alone (P# only) for ~5s.
- Then the T# lines slot in between, animating in chronologically. Briefly highlight T5 (main→break) and T6 (break→main) — the high-stakes transitions in this song.
- Final caption while the full unified block is on screen: pin the "code identifies / Gemma writes / code verifies" line. This is the **architectural signature beat**, not just a feature beat.

**Phase-44 swap-in candidate** for the T# evidence: cut from the static unified block to [`timeline_filomena_intro_to_main_captioned.mp4`](../demo_assets/output/timeline_filomena_intro_to_main_captioned.mp4) and [`timeline_e_magia_vocal_break_captioned.mp4`](../demo_assets/output/timeline_e_magia_vocal_break_captioned.mp4) back-to-back (~6 s each, audio under) so the audience *hears* the bass kick in / the percussion thin while reading the verbatim Gemma line about that exact moment. The static block carries the architectural argument; the clips carry the proof.

### 2:10–2:20 · `kizomba_drills` — a practice plan, structurally verified

**Captions / on-screen text:**
> 1. **"A practice plan: every phase to one drill."**
> 2. **"Same pattern: structural invariants enforced in code, not prompt prose."**

**Visual:** Drills output. **Decision (commit to one):** either (a) 3–5s diff visual of the Daniel Santacruz before/after — Gemma's draft compressed 11 phases into 8 with two cross-boundary ranges; verifier expanded to 11 phase-correct lines — or (b) drop the anecdote entirely. With no voice-over, "narrate it briefly" isn't an option. Default to (b) if Act 3a is running tight.

## Act 3b — Same pipeline, different feel: Charbel _E Magia_ (2:20–2:40)

**Track:** Charbel — _E Magia_ (kizomba, slower, sensual, instrumental phases, breaks for breath). Used as a **contrast highlight reel**, not a full re-run. Two or three sections where the same pipeline surfaces what makes *this* track distinct from Filomena.

**Captions / on-screen text** (chunked across 20s):
> 1. (2:20–2:28) **"Different kizomba feel: slower, more sensual, instrumental phases."**
> 2. (2:28–2:36) **"Same DSP. Same Gemma prompts. Different coaching surfaces."**
> 3. (2:36–2:40) **"The pipeline adapts to what the song is — it doesn't impose what it expects."**

**Visual:** 2–3 short cuts from notebook 09's `E Magia` output, each held just long enough to read one or two lines:
1. An **instrumental phase** with the tutor coaching restraint (no vocals → space to breathe in the basic).
2. A **same-label `main → main` transition** where the role shift is about *softening / sensuality* rather than energy lift — the contrast with Filomena's energy-forward T2/T4 should be visible side-by-side if there's room for a quick split-screen.
3. (Optional, if time) A **break** line where the coaching is about breath / connection rather than recovery.

**Beat:** The story of Act 3b is *generalization without overclaiming*. Not "works on all music" — "adapts to two clearly different kizomba feels." Choose the cuts at recording time based on which contrasts are most legible on screen.

## Close (2:40–3:00)

**Captions / on-screen text** (chunked):
> 1. (2:40–2:50) **"What ships now: section labels, beat-clarity tags, phase coaching, transitions, drills — verified end-to-end."**
> 2. (2:50–2:57) **"What's next: making the coaching less templated — phases and transitions that reference each other, drills tied to what makes a section distinct."**
> 3. (2:57–3:00) **_"DSP earns its keep by being the part that listens. Gemma talks."_**

**Visual:**
- (2:40–2:57) Closing slide: architecture diagram (back from Act 2) plus three text lines:
  - _GitHub: <repo URL>_
  - _Demo notebook: notebooks/00_demo.ipynb_
  - _Phase notes: docs/experiments/_
- (2:57–3:00) End on the project name + the closing line.

**Beat:** Honest about what ships (the unified timeline now answers what 40c/40d set out to fix), honest about the cracks (the coaching still reads more templated than song-specific in places). Naming the limitation as *future work* is stronger than hiding it. The closing line is the spine of the whole demo.

## Production notes

**Pre-render** every notebook output before recording. Run `notebooks/00_demo.ipynb` end-to-end with the polish pass on, save the output cells, and screen-record from the rendered notebook. Live execution introduces latency that disrupts pacing — and the Demucs cold-start on the first track adds 10-30s that has no place in a 3-minute pitch.

**Use the Phase-44 captioned clips as drop-ins.** Where this storyboard says "interactive HTML timeline with the cursor moving" or "unified timeline with T# evidence", the eight `demo_assets/output/timeline_*_captioned.mp4` files are pixel-stable, audio-included, caption-baked replacements built by `demo_assets/scripts/make_all_demo_videos.py`. They eliminate the "record-the-screen-and-hope-the-cursor-was-smooth" failure mode for those beats. The plain (uncaptioned) variants are also rendered for cases where the storyboard wants the visual without the Gemma-line text, e.g. Act 1 / Act 2 b-roll over their own captions.

**Section-by-section recording is fine.** Record each act separately and stitch in post. Caption text and timing can be revised any time without re-shooting; only the screen-capture portions are time-locked to a take.

**Audio — keep song clips short.** With no voice-over, music can play unattenuated where it serves the demo, but **keep audible song use under ~10 seconds per clip** to stay safely inside transformative-use norms for an educational competition submission. Three main audible moments:
- **Act 1 hook (5–10s):** the kizomba opener with the generic-beat-tracker click overlay so the misfire is *audible*, not just visual.
- **Act 3a §2 (5–10s):** Filomena _Teu Toque_ as the timeline cursor moves — long enough to see the cursor cross a section boundary, no longer.
- **Act 3b (3–6s, optional):** a short E Magia clip under the contrast cuts so the *feel difference* lands sonically, not just visually. Drop if Act 3b runs tight; the visual contrast is the primary carrier.

Mute the track everywhere else and let captions + visuals carry the rest. Soft ambient pad or silence under caption-only beats is fine; do not loop the demo track under everything (it both competes with the captions and stretches the audible song use past what's defensible).

**Captions are the narrative.** With no voice-over, on-screen captions are how the story gets told — see the "Caption style" section above for chunking, length, and pacing rules. Bake them into the video file rather than relying on YouTube auto-captions; the technical vocabulary will trip an auto-captioner.

**What NOT to show.** The 17-track extended-set evidence (notebook 09) is great for the writeup but too dense for a 3-minute pitch. Stick to the Filomena (deep-dive) + E Magia (contrast highlight) pair. The Daniel Santacruz verifier-repair anecdote — see Act 3a drills section for the show-or-drop decision; with no voice-over, "narrate it briefly" isn't an option.

## Track choices

- **Act 3a deep-dive track (kizomba, dense / forward-beat):** Filomena Maricoa — _Teu Toque_. 92 BPM, severe break at 148s, has all six section labels in its arc, the prompts have been tuned against this track since Phase 28. Locked as primary based on output quality observed across Phase 40 work.
- **Act 3b contrast track (kizomba, slower / sensual):** Charbel — _E Magia_. Slower feel, instrumental phases, breaks function as breath rather than reset. Chosen because the same DSP + Gemma pipeline surfaces a recognisably different coaching voice — the generalization story without overclaiming. The Phase 40d notebook 09 run is the source for which sections to cut to.
- **Phase-44 cross-style + cross-track additions** (use depends on Act-3 shape — see Open question):
  - **Romeo Santos — _Propuesta Indecente_** (bachata, T2 break→main @ 38 s). Picked because the bongo entry is clean and the Gemma line uses the bachata-native `1-2-3-tap` vocabulary on a clear `1`.
  - **Prince Royce — _Corazón Sin Cara_** (bachata, T4 main→outro @ 194 s). Picked for the most idiomatic bachata-transitions caption in the harvest ("contract your movement and finish on a clean 8 as the percussion thins and the güira drops out") — the line *sounds* like a bachata teacher.
  - **Mika Mendes — _Mágico_** (kizomba, T2 short_break→main @ 34 s). Picked as a third kizomba feel (warmer/funkier than Filomena or E Magia) if a within-style breadth beat is wanted instead of the cross-style one.
- **Cuts available if Act 3a runs long:**
  - Drop the Daniel Santacruz drills-repair anecdote (favoured cut).
  - Compress `song_arc` from 10s to 6s (one caption, no extra highlight).
  - Compress the unified-timeline beat by skipping the "P# lines first, T# lines slot in" animation and showing the final block immediately (loses the architectural-signature beat — only cut as last resort).

## Open questions

### Polish-pass beat

The polish pass is the demo's recommended kizomba output (default in `notebooks/00_demo.ipynb`). The captions above describe the *polished* tutor as "the kizomba tutor". That's accurate for what ships in the demo but elides the one-pass / polish split. If you want to make the polish pass itself a beat in the video (a tight ~10s clip showing the same P# line in one-pass and polished form, demonstrating the second-call refinement), Act 3a needs to expand by 10s and the cuts list above shows where it would come from. **Default: do not show the polish pass as its own beat — the unified timeline beat is now carrying the architectural-signature load it would have carried.**

### Act 3 shape now that bachata + cross-kizomba clips ship

The current Act 3 is **3a Filomena deep dive (kizomba) + 3b E Magia contrast (kizomba)**. Phase 44 added two production-ready bachata clips (Romeo, Royce) and one extra kizomba clip (Mika Mendes) — the cross-style story ("two styles, same architecture, different coaching surfaces") is now available without recording any new artifact. Three options:

- **Default — keep the existing 3a/3b shape.** Use the captioned clips inside the existing scenes (Filomena clip in §1:25 timeline beat; Filomena + E Magia clips in §1:50 unified-timeline beat). The bachata + Mika clips become *honourable mentions in the writeup* but don't appear in the video. Keeps the kizomba-deep-dive narrative intact; spends none of the 3-minute budget on the cross-style story.
- **Option Y — restructure to 3a kizomba (Filomena) + 3b bachata (Romeo + Royce).** True cross-style proof. Trades the kizomba-vs-kizomba contrast (E Magia) for kizomba-vs-bachata. Better competition story for "the architecture works on more than one style"; weaker for "the same DSP picks up subtle within-style differences".
- **Option Z — tighten to 3a/3b/3c (Filomena / E Magia / one bachata clip).** Two beats inside kizomba (deep + contrast) plus one cross-style beat. Carries both stories; needs Act 3b and 3c to be ~15 s each; the bachata clip is a single-cut "look, the same coaching shape applies to a different style" moment using either Romeo (intro→main, "1-2-3-tap on the next clear 1") or Royce (main→outro, the richest line in the harvest).

**Decision blocked on:** is the cross-style proof worth the 15–20 s it would cost the within-style contrast beat? Default until decided is to keep the existing 3a/3b and use the new clips only inside it.

**Decision (2026-05-15):** Option **Z** locked in for the stitched final reel — `demo_assets/scripts/compose_final_video.py` produces a 41 s reel (Filomena → E Magia → Royce). The reel covers ~1:50 onward of the master cut. Reverting to Default or switching to Y is a one-list edit in the `CLIPS` constant of that script.

### Act 3a pre-roll render style (in-progress)

The 50 s of Act 3a pre-roll (1:00–1:50 — `rhythm_anatomy`, sections+timeline, `listening_guide`, `song_arc`, before the unified-timeline beat at 1:50) needs PNG/MP4 panels rendered from `notebooks/00_demo_outputs.md`. Two options for the panel style:

- **Option (a) — caption-style PNG panels.** Reuse `make_caption_slide.py`. Stylized excerpts of the Gemma output, easy to iterate on, but loses the "this is the actual notebook output" feel.
- **Option (b) — notebook-style panels** *(picked 2026-05-16)*. Render the Gemma output blocks in monospace on a card with a "from `notebooks/00_demo.ipynb`" footer. More authentic; makes the architectural argument ("look — this is *real* Gemma output verbatim, not paraphrased") much stronger.

**Decision (2026-05-16):** going with **(b)**. New helper `make_notebook_panel.py` mirrors the `make_caption_slide.py` shape so swapping panel style later is a script-level swap inside `make_act3a_preroll_video.py`, not a rewrite. Length budget: full **50 s** (matches storyboard allocation; favour breathing over compression). If the master reel runs over 3 minutes, the documented compression cuts in the "Cuts available if Act 3a runs long" list above are the first place to look.

**Built (2026-05-16):** `demo_assets/scripts/make_act3a_preroll_video.py` produces `act3a_preroll.mp4` (49.5 s, 1920×1080, silent aac). 4 panels — `rhythm_anatomy` (11 s) → `describe_sections` truncated to 7 rows + ellipsis (12 s) → `listening_guide` (13 s) → `song_arc` (12 s). Verbatim Gemma text lives in module-level constants at the top of the script — those are the swap points if we want to substitute another song or trim wording. Body text size per panel is also a constant (`body_pt=22` for the wide table, 28–30 for prose) — first knob to turn if any panel feels cramped or sparse on review. The panel renderer preserves verbatim spacing on lines that fit (so monospace tables keep column alignment) and only wraps overflowing lines.

### Unified-timeline beat (1:50–2:10) — built

**Built (2026-05-16):** `demo_assets/scripts/make_act3a_unified_timeline_video.py` produces `act3a_unified_timeline.mp4` (21.0 s, 1920×1080, silent aac). Three stages with 0.5 s xfades:

1. **Stage A** (5.0 s): P# lines only. T# rows reserve vertical space but are blank so the layout doesn't shift between stages.
2. **Stage B** (10.0 s): full unified block — T# lines slot in (violet) between P# lines (slate-50); the eye instantly separates the two scaffolds by color.
3. **Stage C** (5.0 s): same block + pinned violet banner *"Code identifies the boundaries. Gemma writes the lines. Code verifies they cover the song."* — the architectural-signature line, pinned while the full evidence is on screen.

Verbatim 15-line interleave lives in the `LINES` constant at the top of `make_act3a_unified_timeline_video.py`. Shared renderer is `make_unified_timeline_panel.py` with `hide_transitions` and `pinned_caption` knobs — re-stagable if a future review wants a different timing or a 4-stage version (e.g. highlight T5 and T6 as a separate stage).

Knobs to revisit on master-cut review:
- **Stage durations**: currently 5/10/5. If Stage B feels rushed for reading 15 lines, push to 6/12/5 (= 23 s) and trim 2 s from elsewhere in Act 3a.
- **T# highlight pass**: storyboard called for *"briefly highlight T5 (main→break) and T6 (break→main)"*. Not yet implemented — would need a 4th stage or a per-line emphasis pass in the renderer. Defer until the master cut review.
- **Body font size**: `body_pt=20` with `line_h × 1.42` — chosen so all 15 lines (with 2-line wraps on the longer T#) fit above the pinned banner with breathing room. If readability is tight on smaller screens, raise to 22 and tighten by trimming a less-essential T# line.

### Close (2:51–3:08 in master) — built

**Built (2026-05-16):** `demo_assets/scripts/make_close_video.py` produces `close.mp4` (17.0 s, 1920×1080, silent aac). 3 caption scenes with 0.5 s xfades:

1. **"What ships now"** + section-labels/beat-clarity/coaching/transitions/drills summary (5.5 s).
2. **"What's next"** + honest future-work line about less-templated coaching (5.5 s).
3. **"DSP listens. Gemma talks."** signature + `Rytmi · github.com — Gemma 4 Good Hackathon` footer (5.0 s).

The closing line is the spine the storyboard pinned the whole demo on. Caption text and per-scene durations are constants at the top of the script — first knob to turn if the close feels too long/short on master review.

### Master reel — built

**Built (2026-05-16):** `demo_assets/scripts/compose_master_reel.py` chains the 6 act MP4s with 0.5 s xfade (video) + acrossfade (audio) into `demo_assets/output/rytmi_demo_master.mp4` (185.77 s = 3:05.77, 10.3 MB, 1920×1080 / 30 fps / h264 + stereo aac).

Per-act timing within the master:

| Act | File | Duration | Lands at |
|---|---|---:|---|
| 1 Hook | `act1_hook.mp4` | 29.75 s | 0:00–0:29.75 |
| 2 Architecture | `act2_architecture.mp4` | 30.00 s | 0:29.25–0:59.25 |
| 3a Pre-roll | `act3a_preroll.mp4` | 49.50 s | 0:58.75–1:48.25 |
| 3a Unified timeline | `act3a_unified_timeline.mp4` | 21.00 s | 1:47.75–2:08.75 |
| 3 Audio reel | `rytmi_demo_reel.mp4` | 41.01 s | 2:08.25–2:49.26 |
| Close | `close.mp4` | 17.00 s | 2:48.76–3:05.77 |

(Each successive act's start is offset back by `xfade_s = 0.5` because of the crossfade overlap.)

Total is ~6 s over the 3:00 storyboard target. Three places to trim if a tighter cut is wanted (none done yet — defer until end-to-end review):

- **(γ) Act 3a pre-roll** — drop the `describe_sections` panel (12 s) since the unified timeline and audio reel both make the section structure concrete. Brings master to ~2:54.
- **(δ) Close stage 1+2** — collapse "what ships" and "what's next" into a single slide (saves ~5 s). Loses some of the honest-limitations framing.
- **(ε) Reduce xfades** — drop the act-boundary xfade from 0.5 s to 0.25 s (saves 1.25 s). Mostly invisible to the eye.

The `ACTS` list at the top of `compose_master_reel.py` is the swap point if a single act needs to be replaced with an alternate cut (e.g. a 6/12/5 unified-timeline rebuild, or a different audio-reel order).

### Act 1 / Act 2 caption length & font sizing (open)

Act 1 caption 3 (*"Generic beat trackers latch onto whatever's loudest. They confidently mislead."*) wraps to two lines because the primary line is long. Acceptable for now, but if the reading rhythm feels off after watching the master cut end-to-end, two cleanup options:

- **(α)** Split into two captions (slide → "Generic beat trackers latch onto whatever's loudest." → slide → "They confidently mislead.") and recalculate scene durations.
- **(β)** Drop the primary font size from 72pt to ~64pt so it fits one line. Loses some weight; preserves pacing.

Same kind of issue may surface on Act 2 caption 2. Defer until master cut is reviewed end-to-end. **Defaults until decided: keep current sizing.**

### Clarity pass (2026-05-17) — built

After watching the 3:05.77 master end-to-end the Gemma framing didn't read clearly enough for a judge dropping into any single second: the hook is personal ("I wanted to hear the beat"), the bachata clip cold-opens with no genre signal, and the captioned timeline clips don't attribute the coaching text to Gemma. Four small patches landed (no act re-render needed beyond the clip + reel + master re-stitch):

1. **(φ) `Gemma 4:` prefix on every timeline caption strip** — `_add_caption_strip` in `make_timeline_video.py` now takes a `speaker="Gemma 4"` kwarg and paints a bold violet-400 label in the top-left of the caption band. All 8 captioned clips were regenerated. *Knob:* pass `speaker=None` to suppress, or pass another string ("Tutor", "Rytmi") if attribution wording changes. The two-tone layout (violet label, white body) avoids matplotlib mixed-inline-color hacks.

2. **(χ) Top context banner on the audio-reel clips** — `Clip` in `compose_final_video.py` grew `style_label` and `point` fields; `_build_filter_graph` now paints a translucent slate-800 strip (height 56 px) across the top of each input video before the xfade chain, with the style **upper-cased** (`KIZOMBA`, `BACHATA`) so the cross-style switch on clip 3 reads as deliberate. Banners:
   - Filomena → `KIZOMBA · 92 BPM · intro → main transition`
   - E Magia  → `KIZOMBA · vocal break collapse`
   - Royce    → `BACHATA · 123 BPM · main → outro transition`
   *Knob:* set `style_label=""` and `point=""` on a Clip to suppress its banner. `BANNER_*` constants at the top of the script control sizing/color.

3. **(ψ) Hook title slide subtitle** — `make_all_demo_clips.py` now renders the title slide with subtitle *"Rhythm coaching for dancers, powered by Gemma 4"* (was "DSP + Gemma 4 for rhythm learning"). Same slot in the same render — no act timing change.

4. **(ω) Global watermark on the master** — `compose_master_reel.py` appends a final `drawtext` stage that overlays *"Rytmi  ·  Gemma 4 Hackathon"* in slate-400 at 60% opacity, bottom-right (28 px margin, 20 pt DejaVu Sans). Reads as Rytmi/Gemma chrome on every frame including title/close slides; never competes with act content. *Knob:* `WATERMARK_*` constants at the top of `compose_master_reel.py`.

Master output unchanged in length (still 185.77 s = 3:05.77) since none of the patches alter timing — only the per-frame chrome. Re-stitch path on any future clarity tweak: re-render the relevant clip → `compose_final_video.py` (if the reel changed) → `compose_master_reel.py`. The four patches are independent and can each be reverted in isolation if a future review wants to dial one back.

Deferred (still open if a later review wants to push further):

- **(ξ) Watermark exceptions for title/close slides.** The watermark currently paints over the title and close slides too. Considered acceptable (it's small, low-contrast, and reinforces the Rytmi/Gemma framing on the most-screenshotted frames) but could be suppressed with per-act filter branches if it ever feels redundant against the explicit "Rytmi" wordmark on those slides.
- **(ζ) Banner positioning options.** Top banner picked over bottom strip so it doesn't compete with the existing bottom caption strip (which already has the violet `Gemma 4:` prefix). If a future review wants both pieces of attribution on the same edge, the banner could move to just-above the caption strip instead.
- **(η) Speaker wording.** Picked `Gemma 4:` over `Gemma:` / `Tutor:` / `Rytmi:` so the model attribution is explicit (matters for a Kaggle judge sampling a single frame). One-string change in `_add_caption_strip`'s default kwarg if the wording is wrong later.

### Clarity pass #2 (2026-05-18) — built

After a second watch of the 3:05.77 master a deeper restructuring gap surfaced: the *narrative flow* was the issue, not just the per-frame chrome. Three problems:

1. Act 1 carried the audible-misfire beat (clicks WAV) before the architecture had been set up — viewers heard "wrong" clicks before knowing what *right* would look like.
2. The reel banners (clarity-pass-1 χ) labelled each clip with its genre/tempo but never said *what this clip shows vs the previous one*, so the cross-style comparison read as three isolated examples instead of one pattern repeated across songs/styles.
3. The Act 3a panel headings were paraphrased Gemma-style prose questions ("What kind of music is this?") that didn't disambiguate which panel was Gemma's verbatim prose vs the DSP table that *feeds* Gemma.

Six phases shipped (master now 3:09.5, +3.75 s vs pass-1):

- **(A) Act 1 reorder.** `make_act1_video.py` now renders 3 silent scenes — `hook → title → bridge` (was 4 scenes ending on the clicks-overlay misfire beat). Hook stays personal ("I wanted to dance to the music and hear the beat. It kept slipping."), title slide subtitle updated to *"Rhythm coaching for dancers — Gemma 4 explains the music, code finds the beat"*, bridge sells the dancer's need for phrasing/transitions and names Gemma 4 as the explanation engine. Audible misfire moved to Act 2.5. Total length 21.5 s (was 29.75 s). `make_slide.py`'s `render_slide` was patched with greedy word-wrap (80 % canvas width) so the longer subtitle wraps cleanly at 56 pt.

- **(B) New Act 2.5: kizomba example case.** `make_act2_5_video.py` — 12.5 s, 2 scenes. Scene 1 (silent, 5 s): *"Example case: kizomba."* + style gloss. Scene 2 (7 s) carries the clicks overlay (`act1_filomena_hook_clicks.wav` — filename kept for backward compat) with caption *"Generic beat trackers misfire here."* and a footer *"Filomena Maricoa — Teu Toque · clicks below show a generic tracker's wrong guesses · listen to the bassline for the real pulse"* — turns the failure into a *teaching* beat: viewer is told **what to listen for** while hearing the misfire. Audio plumbing mirrors old Act 1 (`adelay`+`apad`+`atrim`) so the clicks land when scene 2 is fully visible.

- **(C) Act 3a panel heading attribution.** `make_act3a_preroll_video.py` panel headings rewritten so each frame's heading says **whose output you're reading**: `"Gemma 4 explains the music style"`, `"Code finds the sections (input to Gemma)"`, `"Gemma 4 coaches: where to listen"`, `"Gemma 4 narrates the song's arc"`. The DSP `describe_sections` panel also gets a custom footer (*"verbatim Rytmi DSP output — fed to Gemma below"*) so the data-flow direction reads off any single frame. *Knob:* heading and footer kwargs to `render_notebook_panel` per panel — the strings are the only swap point.

- **(D1) Reel banner rewrite.** `compose_final_video.py` `Clip` dataclass replaced `style_label`+`point` (clarity-pass-1 χ) with a single `banner_text` field. The three banners now say what *this* clip is relative to the previous one:
  - Filomena → *"Example Gemma 4 coaching for an intro → main transition · kizomba"*
  - E Magia → *"Same kizomba style, softer song · coaching for the vocal break"*
  - Royce → *"Different style: bachata · same coaching pattern still works"*
  No upper-casing — prose reads naturally; emphasis comes from the slate-800 strip + DejaVu-Bold.

- **(D2) Inline `Gemma 4:` caption prefix.** `_add_caption_strip` in `make_timeline_video.py` now renders the speaker label *inline* with the caption body using matplotlib's `HPacker`/`VPacker` (was pinned top-left in pass-1 φ). Same baseline, violet-400 bold prefix flows naturally into the white body text — reads as one coaching line with a Gemma stem, no longer as unrelated chrome. All 8 captioned clips regenerated.

- **(F) Act 2.5 inserted into master.** `compose_master_reel.py` ACTS list grew one entry between `act2_architecture.mp4` and `act3a_preroll.mp4`. Master is now **189.5 s = 3:09.5** (was 3:05.77, net +3.75 s).

Deferred (still open if a later review wants to push further):

- **(E) Waveform under the unified-timeline panel.** Would visually tie the Act 3a unified timeline to the audio playing underneath it (matching the look the reel clips have). Not built — would need a stage-by-stage render in `make_unified_timeline_panel.py` and pushes Act 3a length up. Park until the 3:09.5 master gets reviewed.
- **Asset reuse note.** The clicks WAV is still called `act1_filomena_hook_clicks.wav` on disk even though the beat now lives in Act 2.5. No rename — `make_all_demo_clips.py` still produces it, `make_act2_5_video.py` references it under the old name. Cheap rename if a future pass wants the filenames to match the new act numbering.

### Clarity pass #3 (2026-05-18) — built

After a third watch a viewer flagged two honesty gaps the pass-2 chrome had not closed:

1. The **unified-timeline beat had no Gemma attribution on screen** even though every `P#` and `T#` line in the panel is verbatim Gemma prose. A judge sampling a single frame from the Act 3a stage A/B panels would see only the violet `T#`/`P#` colour coding (the architectural signature didn't pin until stage C).
2. The reel caption strip's single `Gemma 4:` prefix (pass-2 D2) **over-attributed to Gemma**: the structured `T1: 12s [intro → main, beat: clear → clear]` header on those captions is DSP-rendered by `_format_transition_line` ([src/rytmi/prompts.py:2104](src/rytmi/prompts.py#L2104)) — only the prose after the em-dash is Gemma. (Indexing, timestamp, section labels and beat clarity come from the DSP `Transition` object; Gemma sees the whole `RHYTHM_ANALYSIS_TEMPLATE` and writes the coaching tail.)

Two patches shipped (master length unchanged at **189.5 s = 3:09.5**):

- **(α) Per-stage attribution banners on the unified timeline.** `make_act3a_unified_timeline_video.py` now renders three pinned banners instead of leaving stages A/B unlabelled:
  - **Stage A** (P-only, 5 s) → *"Gemma 4 names each phase — what's happening, how to dance it"*
  - **Stage B** (P + T, 10 s) → *"Gemma 4 coaches the transitions between them"*
  - **Stage C** (signature, 5 s) → unchanged ("Code identifies the boundaries. Gemma writes the lines. Code verifies they cover the song.")

  Renderer side already supported `pinned_caption` from pass-1; this just wires it for all three stages. Stage durations unchanged.

- **(β) Two-row provenance split on reel captions.** `_add_caption_strip` in `make_timeline_video.py` now sniffs the verifier scaffold pattern (`^T\d+:\s.*\[.*\]$`) on the caption's first line. When matched:
  - **Row 1** — teal `#5eead4` bold `Rytmi DSP:` prefix + the structured header (verbatim from the DSP-rendered prefix the verifier passes to Gemma)
  - **Row 2** — violet `#a78bfa` bold `Gemma 4:` prefix + the coaching prose (leading `"— "` stripped, since the violet prefix now anchors the row)

  Captions that don't match the pattern (hybrid notebook quotes, paraphrased context lines like the E Magia `intro → main` caption) fall back to the previous single-prefix rendering. *Knobs:* the regex in `_add_caption_strip` is the detection point; `dsp_props` colour and prefix text are the rendering point.

  Reads on screen as one tutoring line authored by two collaborators on a shared baseline — matches the actual data flow without overclaiming either side.

Deferred (still open if a later review wants to push further):

- **(γ) Pre/transition/post phase highlighting on reel clips.** Considered but skipped. Would visually tie the reel coaching to the surrounding phase context (the one bit the captions still hand-wave), but the Act 3a unified-timeline panel already shows phases + transitions side by side three seconds earlier in the master, so the reel clips don't need to re-establish that context. Would also require real per-beat overlay animation work and would push Act 3 length. Park until a future review wants more visual reinforcement.

### Clarity pass #4 (2026-05-18) — built

Another watch surfaced two remaining gaps from pass-3:

1. The pass-3 violet pinned banners under the unified-timeline panels (stages A and B) sat *below* the table; viewer attention lands on the heading and table first and the bottom strip often went unread. The Gemma attribution belonged in the heading.
2. The Close slide's "What's next" beat carried a single generic sentence ("less templated coaching — phases and transitions that reference each other; drills tied to what makes a section distinct"). With Gemma named explicitly on nearly every other frame of the master, the future-work slide felt thin by comparison and didn't say *what would actually be worked on*.

Two patches shipped (master now **193.5 s = 3:13.5**, +4 s vs pass-3):

- **(δ) Heading-level Gemma attribution on the unified-timeline panels.** `make_act3a_unified_timeline_video.py` now passes a per-stage `heading=` to `render_unified_timeline_panel` (renderer already supported this kwarg; default was `"Unified timeline — phases + transitions"`):
  - **Stage A** (P-only, 5 s) → heading *"Gemma 4 names each phase"*, no pinned banner
  - **Stage B** (P + T, 10 s) → heading *"Gemma 4 coaches the transitions"*, no pinned banner
  - **Stage C** (signature, 5 s) → heading reverts to neutral *"Unified timeline — phases + transitions"*, architectural-signature banner unchanged

  The two pass-3 banners (`PINNED_CAPTION_A`/`B`) were retired — having the same Gemma attribution in both the heading and a violet bottom strip felt redundant and competed for the eye. Stage C is the only stage with a pinned bottom banner; that line ("Code identifies the boundaries. Gemma writes the lines. Code verifies they cover the song.") is a distinct closing thought, not a duplicate of the heading.

- **(ε) Four grounded future-work bullets on the Close.** `make_close_video.py` SLIDE_2 body rewritten and `make_caption_slide.py` extended with `secondary_align` (`"left"` for bullet lists, `"center"` default) plus newline-aware wrapping (`secondary.split("\n")` so each pre-split line wraps independently rather than `text.split()` collapsing the bullet structure). Bullets balanced 2 DSP-side + 2 Gemma-side so the slide reads as half input-quality / half tutor-personalisation:
  - *Sharper beat & downbeat grid — meter votes + surfaced confidence* (DSP; addresses the green-dashed-grid drift, [docs/how-it-works.md L281-287](how-it-works.md#L281-L287), [docs/project-vision.md L601](project-vision.md#L601))
  - *Real-music tap-based eval, replacing synthetic-click calibration* (DSP; [docs/how-it-works.md L248](how-it-works.md#L248), [docs/experiments/28-2026-04-23-phase-28-tap-ground-truth.md](experiments/28-2026-04-23-phase-28-tap-ground-truth.md))
  - *Per-boundary cues for Gemma 4 — less templated transition coaching* (Gemma; [docs/experiments/40c-2026-05-10-phase-40c-transitions-prompt-rewrite.md L80-85](experiments/40c-2026-05-10-phase-40c-transitions-prompt-rewrite.md#L80-L85), [docs/kaggle_writeup.md L159](kaggle_writeup.md#L159))
  - *Gemma 4 learner levels — beginner vs improver drills, local-first E4B* (Gemma; [docs/experiments/31-2026-04-28-phase-31-demo-polish.md L101](experiments/31-2026-04-28-phase-31-demo-polish.md#L101), [docs/experiments/33-2026-05-03-phase-33-listening-guide.md L151](experiments/33-2026-05-03-phase-33-listening-guide.md#L151))

  Each bullet fits one line at 36 pt with the slide content area centred as a block (longest bullet anchors the left edge). Slide-2 visible duration bumped 5.5 s → 9.5 s so a viewer has time to read all four. Primary-pt nudged 96 → 88 to keep the heading and bullets in visual balance.

Deferred (lower priority for the demo close itself):

- **(ζ) Per-bullet citations on slide 2.** Citation links live in the storyboard above; the slide itself stays clean. Could add tiny grey doc references under each bullet but would push slide reading time past 10 s.
- **(η) Animated bullet reveal.** Bullets all appear at once. A staggered fade could draw the eye through the list but would need a per-bullet PNG sequence and complicates the simple PNG→video pipeline used for the rest of the Close.

### Clarity pass #5 (2026-05-18) — built — under-3-min cut

Pre-submission gap analysis (against `docs/gemma-kaggle-compo.md` §4) surfaced one blocking issue and several important ones; this pass closes the biggest: **the video was 3:13.5 against a 3:00 hard cap**. Two viewer observations drove the cut shape rather than a uniform shave:

1. The kizomba-intro / audible-misfire beat (Act 2.5) needed kizomba ear-training to read, was DSP-side rather than Gemma-side, and pushed time-to-beef to ~62.5 s.
2. The opening title/caption slides held longer than the words on them needed, and the Act 2 caption naming *librosa* by name was technically wrong — the DSP lane in the architecture diagram contains librosa *and* Demucs (vocal stems), and section labelling consumes both.

Three changes shipped (master now **175.5 s = 2:55.5**, **−18.0 s** vs pass-4):

- **(θ) Act 2.5 retired entirely.** `compose_master_reel.py` ACTS list drops `act2_5_kizomba_intro.mp4`. Saves 13.0 s and removes the slowest narrative beat for a viewer who doesn't know kizomba. The kizomba framing now lands via Gemma's own *rhythm_anatomy* panel in Act 3a (better attribution: it's Gemma naming the style and its rhythmic anatomy, not a static caption telling the viewer). The clicks WAV (`act1_filomena_hook_clicks.wav`) is left in `make_all_demo_clips.py` as a no-cost orphan — cheap to revive if a future pass wants to use it elsewhere.

- **(ι) Opening tightened by 5.0 s across 4 slides.** No new content lost; the existing captions were over-held.
  - Act 1 caption1 (personal hook): 6.5 → 5.5 s (−1.0)
  - Act 1 title slide (Rytmi + Gemma 4): 5.0 → 4.0 s (−1.0)
  - Act 2 caption1 ("DSP listens. Gemma talks."): 7.0 → 5.5 s (−1.5)
  - Act 2 caption3 ("Tried Gemma-as-listener first…"): 5.5 → 4.5 s (−1.0)

- **(κ) Act 2 caption2: librosa → DSP rewrite + 1.5 s trim.** Old: *"librosa detects beats, sections, beat-clarity, downbeat confidence."* — technically wrong because section labelling uses Demucs vocal envelope too, and HPSS/Demucs aren't "detecting beats." New: ***"DSP finds beats, sections, beat-clarity, downbeat confidence." / "Gemma 4 turns that into language a learner can use."*** — generalises correctly to the whole cyan lane in the architecture diagram, names Gemma as "Gemma 4" consistently with the rest of the deck, and is shorter so 8.0 → 6.5 s reads naturally.

- **(λ) Architecture diagram lane labels (no time cost).** Added cyan bold **"DSP"** above the librosa/HPSS/Demucs lane and violet bold **"Gemma 4"** above the prompt/Gemma/verifier lane. The diagram now self-attributes the two halves even in a single-frame screenshot (so the cover image and any judge sampling one frame still gets the architecture story). Box labels left as-is (the "librosa DSP" inner box is still accurate; the lane label clarifies it's not the *whole* DSP lane).

**Architecture diagram visible time intentionally kept at 8.0 s** — viewer feedback explicitly called this out as needing scanning time and the most important single frame in the deck.

Time-to-beef went from 62.5 s (pass-4) to **42.5 s** — viewer hits the first Gemma panel ~20 s sooner. Final length 175.5 s leaves ~4.5 s of headroom under the 3:00 cap for any last-minute tweaks.

Deferred (pre-submission gaps still open after pass #5):

- **(μ) LICENSE file at repo root, cover image, Gemma 4 model-card links in writeup, declared submission track, writeup trim to ≤1500 words, requirements-demo.txt, Kaggle Notebook badge, CC-BY sample-pack for `00_demo.ipynb`** — see the pre-submission gap analysis. None of these affect the video itself; they're the next tier of submission packaging.
- **(ν) YouTube music licensing.** The reel uses commercial tracks (Filomena Maricoa, E Magia, Romeo Santos). Demo video may get ContentID-claimed on upload. Two options: re-cut the reel with CC-BY equivalents from Jamendo (safe, big time investment), or upload as-is with an educational-use disclaimer in the writeup (risky). Not addressed in pass #5.

### Pre-submission gap closure (2026-05-18) — built — non-video deliverables

Post-pass-#5 (video locked at 2:55.5) followup that closes (μ) and (ν) from pass #5's deferred list, without touching the video itself.

- **(μ.1) `LICENSE` at repo root** — MIT, with explicit note that music files under `data/songs/` and the video reel remain the property of their rights holders (educational use only).
- **(μ.2) `demo_assets/cover.png`** — copy of `demo_assets/output/architecture.png`. Single frame that self-attributes both halves (cyan DSP lane label + violet Gemma 4 lane label from pass #5 λ).
- **(μ.3) `requirements-demo.txt`** — minimum reviewer install: librosa, scipy, soundfile, matplotlib, numpy, openai, jupyter, ipywidgets. Excludes `[downbeat]` (madmom-from-git, BeatNet) and `[llm]` (torch+transformers); just enough for `00_demo.ipynb` against any OpenAI-compatible Gemma endpoint.
- **(μ.4) Writeup rewrite** — `docs/kaggle_writeup.md` reduced from ~4500 to ~1530 words. Declared track now at the top: *Future of Education* primary, *Ollama Special Technology* secondary. Stripped the `_Updates:_` change log. Added Gemma model-card links (ai.google.dev, Kaggle Models, Ollama tags). Compressed *How Gemma 4 is used* + *Lessons learned* without dropping any of the four signature insights (rationale-echo, negative-example backfire, new-vocab robustness, code-beats-prompt for structural invariants).
- **(μ.5) README update** — demo-video link placeholder and cover image at the top; quickstart now points reviewers at `requirements-demo.txt` first; License section points at the new `LICENSE`.
- **(μ.6) `docs/submission-checklist.md`** — internal pre-submit gate covering: writeup paste, cover image, GitHub URL fill-in, YouTube URL fill-in, music-attribution risk acknowledgement, reproducibility smoke test, and what's explicitly deferred.
- **(ν) YouTube music licensing** — chose disclaimer route over re-cut. New writeup section *"A note on the demo video's audio"* explicitly names every commercial excerpt and documents the educational-use basis, plus a CC-alternative exploration paragraph and a takedown commitment. Reel itself stays as-is; commercial tracks remain because (per viewer assessment) the CC catalogue did not contain comparable instances of the failure modes the demo illustrates.

**Still deferred (post-submission OK):** CC-BY sample pack so `00_demo.ipynb` doesn't depend on user-supplied audio; Kaggle Notebook upload + badge URL in README.

### Restore Act 2.5 framing slide (2026-05-17) — built — context-cliff fix

After uploading the pass-#5 master to YouTube, a viewer flagged that the master jumps straight from the architecture diagram into Gemma's `rhythm_anatomy` panel for an unnamed song. Kizomba arrives via Gemma narration but the *style* itself is never named to the viewer — context cliff. Pass #5 had retired the whole 12.5 s Act 2.5 to make the 3:00 cap; only the audible-misfire beat actually deserved to go.

- **(ξ) Act 2.5 restored as a single 5.0 s silent framing slide** — *"Example case: kizomba."* / *"An Afro-Latin partner-dance style where the pulse a dancer steps on hides behind a syncopated kick."* `make_act2_5_video.py` rewritten from the old two-scene + clicks-audio version into a single-scene silent slide that mirrors `make_act1_video.py`'s `anullsrc` pattern. The audible-misfire scene from the original Act 2.5 is *not* restored (it needed kizomba ear-training to read and didn't earn screen time).
- **(ο) Act 1 caption1 trimmed 5.5 → 4.5 s** — the personal-hook slide ("I wanted to dance to the music…") was over-held; 4.5 s reads naturally and clears 1 s of budget for the restored framing slide.
- **Net timing change**: +5.0 s (new Act 2.5) − 0.5 s (one new inter-act xfade) − 1.0 s (Act 1 caption1 trim) = **+3.5 s**. Master goes 175.5 → **179.0 s = 2:59.0**, 1.0 s headroom under the 3:00 cap.

Trade-off accepted: 1 s of headroom is tight but the framing slide is worth more than the headroom because it removes a viewer cold-start question right before the Filomena deep-dive begins.
