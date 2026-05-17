# 09_kizomba batch outputs - model=google/gemma-4-26b-a4b-it

sources: eval_set=11, extended_set=6

## kizomba - rhythm_anatomy (genre intro)

```
Kizomba typically resides in a comfortable tempo range of 85–110 BPM, usually set in a 4/4 time signature. Rather than a heavy percussive grid, the pulse is often carried by a prominent bass line that dictates the rhythmic flow. While the underlying pulse remains steady, you will often encounter syncopation or emphasis on off-beat elements that create a subtle, driving feel. A standard track follows a structural arc, moving through an intro and main sections, often building tension toward a peak, potentially featuring a break or pause, before resolving in an outro.

When on the dance floor, you may encounter various sub-styles. Angolan kizomba often features a more traditional, grounded pulse, whereas urbankiz tends toward a more polished, electronic texture with higher energy. Tarraxinha focuses on a much slower, more intimate tempo with a heavy emphasis on rhythmic body movements. Recognizing these differences in tempo and texture can help you mentally place a track as soon as the music begins.
```

## eval_set: All_Of_Me

```
source=eval_set | file=All_Of_Me [d1HdMmw74Dg].mp3
  tempo=83.4 BPM | beats=347 | sections=20 | vocal_env=yes
    intro       0.0s-  20.3s  beat_clarity=0.23
    main       20.3s-  31.9s  beat_clarity=0.49
    main       31.9s-  43.4s  beat_clarity=0.47
    main       43.4s-  54.8s  beat_clarity=0.33
    main       54.8s-  65.9s  beat_clarity=0.43
    main       65.9s-  71.9s  beat_clarity=0.38
    main       71.9s-  89.8s  beat_clarity=0.44
    build      89.8s- 106.9s  beat_clarity=0.40
    peak      106.9s- 118.4s  beat_clarity=0.36
    main      118.4s- 129.4s  beat_clarity=0.46
    main      129.4s- 141.2s  beat_clarity=0.46
    main      141.2s- 158.4s  beat_clarity=0.39
    main      158.4s- 175.1s  beat_clarity=0.40
    break     175.1s- 187.6s  beat_clarity=0.41
    main      187.6s- 199.8s  beat_clarity=0.43
    main      199.8s- 205.5s  beat_clarity=0.42
    main      205.5s- 216.9s  beat_clarity=0.39
    main      216.9s- 228.4s  beat_clarity=0.47
    main      228.4s- 239.8s  beat_clarity=0.49
    outro     239.8s- 252.2s  beat_clarity=0.44
```

### listening_guide

```
This 252.2-second track moves at a tempo of 83 BPM, which is slower than the typical kizomba range. The song follows a structural arc that begins with an intro, moves through several main sections, builds toward a peak, experiences a break, and eventually settles into an outro. Because the percussiveness is unusually low, the rhythm is not driven by a heavy drum kit; instead, the melodic and harmonic content carries the pulse, making the rhythm feel more felt than heard.

The most challenging moment occurs during the intro from 0s to 20s, where the beat is only moderate and the percussiveness is very low. Because the pulse is subtle here, you may find it difficult to anchor your timing compared to the clear beat found in the later main sections. Another point of interest is the peak at 107s, where the rhythm becomes quite dense. To navigate the song effectively, trust the bass line through the intro to find the underlying pulse.
```

### kizomba_tutor (one-pass)

```
P1: 0s-20s, intro [beat: moderate] — The pulse is felt rather than heard; stay compact and test the rhythm with small weight shifts.
P2: 20s-90s, main ×6 [beat: clear] — The pulse is easy to follow; settle in by walking the basic and letting the bass guide your steps.
P3: 90s-107s, build [beat: clear] — The pulse is steady; increase your travel and intention as the energy climbs.
P4: 107s-118s, peak [beat: clear] — The pulse is very easy to hear; use this high point to add more expression and variety to your movement.
P5: 118s-175s, main ×4 [beat: clear] — The pulse is reliable; return to the basic walk and focus on maintaining a steady frame.
P6: 175s-188s, break [beat: clear] — The beat is clear but the texture changes; reduce your travel and reset your connection.
P7: 188s-217s, main ×3 [beat: clear] — The pulse is easy to find; re-establish your connection and focus on smooth weight transfers.
P8: 217s-240s, main ×2 [beat: clear] — The pulse is steady; begin to contract your movement as the song winds down.
P9: 240s-252s, outro [beat: clear] — The pulse remains easy to follow; let the dance end gently with minimal movement.
```

### kizomba_drills (verified)

```
P1: intro (0s-20s, beat: moderate) — Drill: keep steps very small and test the pulse with your feet. 20.3s.
P2: main (20s-90s, beat: clear) — Drill: practice a steady walk-step focusing on weight transfer. 30s loop, repeated through the six main phases. 69.5s.
P3: build (90s-107s, beat: clear) — Drill: practice steady weight transfers through this section. 17s.
P4: peak (107s-118s, beat: clear) — Drill: practice steady weight transfers through this section. 11s.
P5: main (118s-175s, beat: clear) — Drill: practice steady weight transfers through this section. 57s.
P6: break (175s-188s, beat: clear) — Drill: reduce travel and keep a small pulse in the body to reset. 12s.
P7: main (188s-217s, beat: clear) — Drill: practice steady weight transfers through this section. 29s.
P8: main (217s-240s, beat: clear) — Drill: practice steady weight transfers through this section. 23s.
P9: outro (240s-252s, beat: clear) — Drill: reduce travel and let the movement wind down. 12s.
```

### kizomba_drills verifier stats

```
parsed=8 repaired_ranges=3 duplicate_phases=0 filled_missing=7 skipped_lines=6 output_lines=9
```

### kizomba_drills raw Gemma draft

```
P1: intro (0.0s-20.3s, beat: moderate) — Drill: keep steps very small and test the pulse with your feet. 20.3s.
P2-P7: main (20.3s-89.8s, beat: clear) — Drill: practice a steady walk-step focusing on weight transfer. 30s loop, repeated through the six main phases. 69.5s.
P8: build (89.8s-106.9s, beat: clear) — Drill: gradually increase your step size to build tension. 17.1s.
P9: peak (106.9s-118.4s, beat: clear) — Drill: execute a three-step pattern with a light pause. 11.5s.
P10-P13: main (118.4s-175.1s, beat: clear) — Drill: maintain a steady walk-step while following the bass line. 30s loop, repeated through the four main phases. 56.7s.
P14: break (175.1s-187.6s, beat: clear) — Drill: reduce your travel and keep a small pulse in your body. 12.5s.
P15-P19: main (187.6s-239.8s, beat: clear) — Drill: same walk-step as P2-P7, but now add subtle hip styling once the basic feels automatic. 30s loop, repeated through the five main phases. 52.2s.
P20: outro (239.8s-252.2s, beat: clear) — Drill: slow the pace and return to minimal movement. 12.4s.
```

### describe_transitions

```
Transitions table — 8 label boundaries
======================================
 #  time   from              →  to                from→to beat   from→to energy
----------------------------------------------------------------------------------------
 1    20.3s  intro             →  main              moderate → clear         low → high/medium
 2    89.8s  main              →  build                clear → clear      high/medium → medium
 3   106.9s  build             →  peak                 clear → clear      medium → high  
 4   118.4s  peak              →  main                 clear → clear        high → high/medium
 5   175.1s  main              →  break                clear → clear      high/medium → low   
 6   187.6s  break             →  main                 clear → clear         low → high/medium
 7   216.9s  main              →  main                 clear → clear      high/medium → medium
 8   239.8s  main              →  outro                clear → clear      medium → medium
```

### kizomba_transitions (verified)

```
T1: 20s [intro → main, beat: moderate → clear] — when the bass kicks in, walk-step the basic on the first clear hit.
T2: 90s [main → build, beat: clear → clear] — as the energy shifts, commit to the new energy and travel more.
T3: 107s [build → peak, beat: clear → clear] — as the energy lifts, increase your intention and travel more.
T4: 118s [peak → main, beat: clear → clear] — as the energy settles, breathe and return to a steady basic.
T5: 175s [main → break, beat: clear → clear] — as the energy fades and the percussion thins, keep a small pulse in the body, listen, and reset.
T6: 188s [break → main, beat: clear → clear] — when the bass returns, walk-step on the first clear hit.
T7: 217s [main → main, beat: clear → clear] — as the energy settles, keep the basic and hold a steady frame.
T8: 240s [main → outro, beat: clear → clear] — as the energy fades, contract your movement and slow the basic to prepare to close.
```

### kizomba_transitions verifier stats

```
parsed=8 boundaries_matched=8 boundaries_invented=0 boundaries_missing_filled=0 skipped_lines=0 output_lines=8 retried=0 retry_succeeded=0
```

### kizomba_tutor (polished)

```
P1: 0s-20s, intro [beat: moderate] — The rhythm is subtle; stay compact and use small weight shifts to find the pulse.
P2: 20s-90s, main ×6 [beat: clear] — The pulse is steady; settle into a walking basic and let the bass guide your steps.
P3: 90s-107s, build [beat: clear] — The pulse is driving; increase your travel and step intention as the energy climbs.
P4: 107s-118s, peak [beat: clear] — The rhythm is very prominent; use this high point to add more expression and movement variety.
P5: 118s-175s, main ×4 [beat: clear] — The pulse is reliable; return to a steady walking basic and focus on a strong, consistent frame.
P6: 175s-188s, break [beat: clear] — The texture shifts; reduce your travel and reset your connection to prepare for the next phase.
P7: 188s-217s, main ×3 [beat: clear] — The pulse is easy to find; re-establish your connection and focus on smooth weight transfers.
P8: 217s-240s, main ×2 [beat: clear] — The pulse is steady; begin to contract your movements as the song winds down.
P9: 240s-252s, outro [beat: clear] — The rhythm remains clear; let the dance end gently with minimal, controlled movement.
```

### unified timeline (phases + transitions)

```
P1: 0s-20s, intro [beat: moderate] — The rhythm is subtle; stay compact and use small weight shifts to find the pulse.
T1: 20s [intro → main, beat: moderate → clear] — when the bass kicks in, walk-step the basic on the first clear hit.
P2: 20s-90s, main ×6 [beat: clear] — The pulse is steady; settle into a walking basic and let the bass guide your steps.
T2: 90s [main → build, beat: clear → clear] — as the energy shifts, commit to the new energy and travel more.
P3: 90s-107s, build [beat: clear] — The pulse is driving; increase your travel and step intention as the energy climbs.
T3: 107s [build → peak, beat: clear → clear] — as the energy lifts, increase your intention and travel more.
P4: 107s-118s, peak [beat: clear] — The rhythm is very prominent; use this high point to add more expression and movement variety.
T4: 118s [peak → main, beat: clear → clear] — as the energy settles, breathe and return to a steady basic.
P5: 118s-175s, main ×4 [beat: clear] — The pulse is reliable; return to a steady walking basic and focus on a strong, consistent frame.
T5: 175s [main → break, beat: clear → clear] — as the energy fades and the percussion thins, keep a small pulse in the body, listen, and reset.
P6: 175s-188s, break [beat: clear] — The texture shifts; reduce your travel and reset your connection to prepare for the next phase.
T6: 188s [break → main, beat: clear → clear] — when the bass returns, walk-step on the first clear hit.
P7: 188s-217s, main ×3 [beat: clear] — The pulse is easy to find; re-establish your connection and focus on smooth weight transfers.
T7: 217s [main → main, beat: clear → clear] — as the energy settles, keep the basic and hold a steady frame.
P8: 217s-240s, main ×2 [beat: clear] — The pulse is steady; begin to contract your movements as the song winds down.
T8: 240s [main → outro, beat: clear → clear] — as the energy fades, contract your movement and slow the basic to prepare to close.
P9: 240s-252s, outro [beat: clear] — The rhythm remains clear; let the dance end gently with minimal, controlled movement.
```

## eval_set: Anselmo_Ralph_-_Curticao

```
source=eval_set | file=Anselmo_Ralph_-_Curticao [mVb1lYstEGk].mp3
  tempo=80.7 BPM | beats=357 | sections=22 | vocal_env=yes
    intro       0.0s-  15.0s  beat_clarity=0.40
    main       15.0s-  20.6s  beat_clarity=0.46
    main       20.6s-  32.6s  beat_clarity=0.46
    main       32.6s-  43.8s  beat_clarity=0.42
    main       43.8s-  61.1s  beat_clarity=0.36
    main       61.1s-  73.1s  beat_clarity=0.39
    main       73.1s-  90.6s  beat_clarity=0.34
    main       90.6s- 107.7s  beat_clarity=0.34
    main      107.7s- 119.8s  beat_clarity=0.44
    main      119.8s- 126.0s  beat_clarity=0.38
    main      126.0s- 138.0s  beat_clarity=0.45
    main      138.0s- 149.6s  beat_clarity=0.41
    main      149.6s- 168.0s  beat_clarity=0.26
    main      168.0s- 179.2s  beat_clarity=0.43
    main      179.2s- 193.3s  beat_clarity=0.23
    break     193.3s- 204.8s  beat_clarity=0.27
    main      204.8s- 210.6s  beat_clarity=0.41
    main      210.6s- 222.0s  beat_clarity=0.42
    main      222.0s- 227.9s  beat_clarity=0.38
    main      227.9s- 240.0s  beat_clarity=0.37
    main      240.0s- 251.6s  beat_clarity=0.36
    outro     251.6s- 270.6s  beat_clarity=0.28
```

### listening_guide

```
This 270.6-second track moves at a tempo of 81 BPM, which is slower than typical for this style. The musical journey begins with a low-energy intro, transitions into an extended main section with varying energy levels, moves through a brief break, and eventually settles into a low-energy outro. Throughout the track, the rhythm is drum-light; rather than a heavy percussive grid, the pulse is primarily carried by the melodic and harmonic content and the underlying bass line.

The most challenging moment occurs during the break starting at 193s, where the beat clarity becomes moderate and the percussiveness drops significantly. You may also find the high-energy sections between 138s and 193s difficult because the beat clarity is moderate and the rhythm becomes quite dense with ornamentation, making it easy to lose the steady pulse. When the percussion thins out or the rhythm becomes complex, do not chase the ornamentation; instead, trust the bass line to find your way back to the pulse.
```

### kizomba_tutor (one-pass)

```
P1: 0s-15s, intro [beat: clear] — The pulse is easy to find; stay close and focus on connection with tiny weight shifts.
P2: 15s-138s, main ×10 [beat: clear] — Establishing the groove; trust the steady pulse to guide a smooth, even walk.
P3: 138s-193s, main ×4 [beat: moderate] — Sustaining the energy; keep your steps compact and avoid chasing the busy ornamentation.
P4: 193s-205s, break [beat: moderate] — A shift in texture; reduce travel and use small steps to test the pulse.
P5: 205s-252s, main ×5 [beat: clear] — Returning to the flow; the pulse is clear again, so you can re-establish your walk.
P6: 252s-271s, outro [beat: moderate] — Closing the dance; stay grounded and avoid extra movement as the song winds down.
```

### kizomba_drills (verified)

```
P1: intro (0s-15s, beat: clear) — Drill: focus on weight transfer through a steady walk-step. 15s.
P2: main (15s-138s, beat: clear) — Drill: maintain a steady walk-step, following the bass line. 30s loop, repeated through the ten main phases.
P3: main (138s-193s, beat: moderate) — Drill: stay compact and test the pulse with small steps. 55s.
P4: break (193s-205s, beat: moderate) — Drill: reduce travel and keep a small pulse in the body to reset. 11s.
P5: main (205s-252s, beat: clear) — Drill: practice steady weight transfers through this section. 47s.
P6: outro (252s-271s, beat: moderate) — Drill: reduce travel and let the movement wind down. 19s.
```

### kizomba_drills verifier stats

```
parsed=7 repaired_ranges=2 duplicate_phases=0 filled_missing=4 skipped_lines=5 output_lines=6
```

### kizomba_drills raw Gemma draft

```
P1: intro (0s-15s, beat: clear) — Drill: focus on weight transfer through a steady walk-step. 15s.
P2-P11: main (15s-138s, beat: clear) — Drill: maintain a steady walk-step, following the bass line. 30s loop, repeated through the ten main phases.
P12-P15: main (138s-193s, beat: moderate) — Drill: keep steps small to stay compact while testing the pulse. 55s.
P16: break (193s-205s, beat: moderate) — Drill: reduce travel and keep a small pulse in the body. 12s.
P17: main (205s-210s, beat: clear) — Drill: same walk-step as P2-P11, but now add subtle hip styling once the basic feels automatic. 5s.
P18-P21: main (210s-252s, beat: moderate) — Drill: use small steps to avoid chasing the syncopation. 42s.
P22: outro (252s-271s, beat: moderate) — Drill: slow the pace and return to minimal movement. 19s.
```

### describe_transitions

```
Transitions table — 5 label boundaries
======================================
 #  time   from              →  to                from→to beat   from→to energy
----------------------------------------------------------------------------------------
 1    15.0s  intro             →  main                 clear → clear         low → high/medium
 2   138.0s  main              →  main                 clear → moderate   high/medium → high  
 3   193.3s  main              →  break             moderate → moderate     high → medium
 4   204.8s  break             →  main              moderate → clear      medium → medium
 5   251.6s  main              →  outro                clear → moderate   medium → low
```

### kizomba_transitions (verified)

```
T1: 15s [intro → main, beat: clear → clear] — Walk-step the basic on the first clear bass hit as the percussion returns.
T2: 138s [main → main, beat: clear → moderate] — Travel a little more and add intention as the energy lifts and the texture thickens.
T3: 193s [main → break, beat: moderate → moderate] — Keep a small pulse in the body and listen as the energy fades and the percussion thins.
T4: 205s [break → main, beat: moderate → clear] — Walk-step on the first clear bass hit once the pulse returns.
T5: 252s [main → outro, beat: clear → moderate] — Contract your movement and slow the basic as the energy fades and the percussion thins.
```

### kizomba_transitions verifier stats

```
parsed=5 boundaries_matched=5 boundaries_invented=0 boundaries_missing_filled=0 skipped_lines=0 output_lines=5 retried=0 retry_succeeded=0
```

### kizomba_tutor (polished)

```
P1: 0s-15s, intro [beat: clear] — Use this steady pulse to find your center; practice small, rhythmic weight shifts while maintaining a soft connection.
P2: 15s-138s, main ×10 [beat: clear] — Lean into the consistent groove; let the steady rhythm guide a smooth, balanced walk with even steps.
P3: 138s-193s, main ×4 [beat: moderate] — Maintain your energy; keep your movements compact to avoid overextending or chasing the busier percussion.
P4: 193s-205s, break [beat: moderate] — As the texture shifts, reduce your travel and use small, controlled steps to stay synced with the pulse.
P5: 205s-252s, main ×5 [beat: clear] — Reconnect with the flow; use the clear rhythm to re-establish a confident, grounded walking pattern.
P6: 252s-271s, outro [beat: moderate] — As the song winds down, stay grounded and keep your movements minimal to finish with composure.
```

### unified timeline (phases + transitions)

```
P1: 0s-15s, intro [beat: clear] — Use this steady pulse to find your center; practice small, rhythmic weight shifts while maintaining a soft connection.
T1: 15s [intro → main, beat: clear → clear] — Walk-step the basic on the first clear bass hit as the percussion returns.
P2: 15s-138s, main ×10 [beat: clear] — Lean into the consistent groove; let the steady rhythm guide a smooth, balanced walk with even steps.
T2: 138s [main → main, beat: clear → moderate] — Travel a little more and add intention as the energy lifts and the texture thickens.
P3: 138s-193s, main ×4 [beat: moderate] — Maintain your energy; keep your movements compact to avoid overextending or chasing the busier percussion.
T3: 193s [main → break, beat: moderate → moderate] — Keep a small pulse in the body and listen as the energy fades and the percussion thins.
P4: 193s-205s, break [beat: moderate] — As the texture shifts, reduce your travel and use small, controlled steps to stay synced with the pulse.
T4: 205s [break → main, beat: moderate → clear] — Walk-step on the first clear bass hit once the pulse returns.
P5: 205s-252s, main ×5 [beat: clear] — Reconnect with the flow; use the clear rhythm to re-establish a confident, grounded walking pattern.
T5: 252s [main → outro, beat: clear → moderate] — Contract your movement and slow the basic as the energy fades and the percussion thins.
P6: 252s-271s, outro [beat: moderate] — As the song winds down, stay grounded and keep your movements minimal to finish with composure.
```

## eval_set: Baila_Kizomba_Amor

```
source=eval_set | file=Baila_Kizomba_Amor [XG11YxMWgaI].mp3
  tempo=107.7 BPM | beats=543 | sections=26 | vocal_env=yes
    intro       0.0s-  17.8s  beat_clarity=0.67
    main       17.8s-  26.6s  beat_clarity=0.57
    main       26.6s-  35.4s  beat_clarity=0.45
    main       35.4s-  44.2s  beat_clarity=0.48
    main       44.2s-  53.0s  beat_clarity=0.48
    main       53.0s-  70.6s  beat_clarity=0.47
    main       70.6s-  83.8s  beat_clarity=0.51
    main       83.8s-  97.1s  beat_clarity=0.54
    main       97.1s- 105.9s  beat_clarity=0.48
    main      105.9s- 119.1s  beat_clarity=0.49
    main      119.1s- 141.6s  beat_clarity=0.39
    main      141.6s- 154.9s  beat_clarity=0.43
    main      154.9s- 163.7s  beat_clarity=0.46
    main      163.7s- 172.5s  beat_clarity=0.39
    instrumental  172.5s- 181.3s  beat_clarity=0.48
    instrumental  181.3s- 195.1s  beat_clarity=0.50
    main      195.1s- 211.6s  beat_clarity=0.44
    instrumental  211.6s- 228.1s  beat_clarity=0.39
    peak      228.1s- 232.8s  beat_clarity=0.39
    main      232.8s- 241.6s  beat_clarity=0.43
    main      241.6s- 251.5s  beat_clarity=0.48
    main      251.5s- 265.2s  beat_clarity=0.37
    main      265.2s- 278.5s  beat_clarity=0.52
    main      278.5s- 292.2s  beat_clarity=0.50
    main      292.2s- 301.6s  beat_clarity=0.45
    outro     301.6s- 314.1s  beat_clarity=0.40
```

### listening_guide

```
This track lasts 314.1 seconds with a steady tempo of 108 BPM. It begins with a low-energy intro that transitions into a long, evolving main section. The journey builds through instrumental passages and reaches a high-energy peak before settling into a medium-energy outro. Throughout the arc, the pulse is primarily carried by the bass line rather than a heavy percussive grid, providing a clear but smooth foundation for the music.

The beat remains clear throughout the entire track, so your main challenge will be sustaining focus rather than recovering from a dip in clarity. The most demanding moment occurs during the high-energy peak around 228s to 233s. At this point, the onset density increases significantly, creating a much busier rhythmic texture that can feel overwhelming. During this peak, don't chase the louder percussion; instead, feel the underlying pulse to maintain your connection.
```

### kizomba_tutor (one-pass)

```
P1: 0s-18s, intro [beat: clear] — Feel the connection through a close embrace; just mark the pulse with minimal movement.
P2: 18s-172s, main ×13 [beat: clear] — Establishing the foundation; use a steady walk-step and let the bass guide your weight transfers.
P3: 172s-195s, instrumental ×2 [beat: clear] — Sustaining the flow; keep a smooth pulse and maintain your frame as the texture stays balanced.
P4: 195s-212s, main [beat: clear] — Sustaining the energy; continue the steady walk-step and focus on following the bass line.
P5: 212s-228s, instrumental [beat: clear] — Building intensity; you can begin to travel more and add more intention to your steps.
P6: 228s-233s, peak [beat: clear] — The emotional high point; use more expression and varied leading to match the high energy.
P7: 233s-265s, main ×3 [beat: clear] — Returning to the basics; re-establish the walk-step and find your connection again.
P8: 265s-302s, main ×3 [beat: clear] — Closing the song; movement should contract and become more controlled as the energy settles.
P9: 302s-314s, outro [beat: clear] — End gently; return to minimal movement and let the dance fade out softly.
```

### kizomba_drills (verified)

```
P1: intro (0s-18s, beat: clear) — Drill: focus on connection through a close embrace with minimal movement. 18s.
P2: main (18s-172s, beat: clear) — Drill: practice a steady walk-step, letting the bass guide your weight transfer. 154s loop, repeated through the main phases.
P3: instrumental (172s-195s, beat: clear) — Drill: maintain a steady pulse through the hips. 40s.
P4: main (195s-212s, beat: clear) — Drill: practice steady weight transfers through this section. 17s.
P5: instrumental (212s-228s, beat: clear) — Drill: practice steady weight transfers through this section. 17s.
P6: peak (228s-233s, beat: clear) — Drill: practice steady weight transfers through this section. 5s.
P7: main (233s-265s, beat: clear) — Drill: practice steady weight transfers through this section. 32s.
P8: main (265s-302s, beat: clear) — Drill: same walk-step as P2-P2, but now add subtle hip styling once the basic feels automatic. 69s loop, repeated through the main phases.
P9: outro (302s-314s, beat: clear) — Drill: reduce travel and let the movement wind down. 13s.
```

### kizomba_drills verifier stats

```
parsed=6 repaired_ranges=4 duplicate_phases=0 filled_missing=5 skipped_lines=2 output_lines=9
```

### kizomba_drills raw Gemma draft

```
P1: intro (0s–18s, beat: clear) — Drill: focus on connection through a close embrace with minimal movement. 18s.
P2-P2: main (18s–172s, beat: clear) — Drill: practice a steady walk-step, letting the bass guide your weight transfer. 154s loop, repeated through the main phases.
P3-P4: instrumental (172s–212s, beat: clear) — Drill: maintain a steady pulse through the hips. 40s.
P5-P7: peak (228s–233s, beat: clear) — Drill: increase expression with stronger leading variety. 5s.
P8-P10: main (233s–302s, beat: clear) — Drill: same walk-step as P2-P2, but now add subtle hip styling once the basic feels automatic. 69s loop, repeated through the main phases.
P11: outro (302s–314s, beat: clear) — Drill: slow the pace and return to minimal movement to end gently. 12s.
```

### describe_transitions

```
Transitions table — 8 label boundaries
======================================
 #  time   from              →  to                from→to beat   from→to energy
----------------------------------------------------------------------------------------
 1    17.8s  intro             →  main                 clear → clear         low → low/medium
 2   172.5s  main              →  instrumental         clear → clear      low/medium → medium
 3   195.1s  instrumental      →  main                 clear → clear      medium → medium
 4   211.6s  main              →  instrumental         clear → clear      medium → high  
 5   228.1s  instrumental      →  peak                 clear → clear        high → high  
 6   232.8s  peak              →  main                 clear → clear        high → high  
 7   265.2s  main              →  main                 clear → clear        high → medium
 8   301.6s  main              →  outro                clear → clear      medium → medium
```

### kizomba_transitions (verified)

```
T1: 18s [intro → main, beat: clear → clear] — when the bass kicks in, walk-step the basic on the first clear bass hit.
T2: 172s [main → instrumental, beat: clear → clear] — keep your basic going steadily.
T3: 195s [instrumental → main, beat: clear → clear] — keep your basic going steadily.
T4: 212s [main → instrumental, beat: clear → clear] — keep your basic going steadily.
T5: 228s [instrumental → peak, beat: clear → clear] — commit to the new energy, travel more, and add intention.
T6: 233s [peak → main, beat: clear → clear] — as the energy settles, settle back, breathe, and return to the basic.
T7: 265s [main → main, beat: clear → clear] — as the energy settles and the percussion thins, keep the basic and hold a steady frame.
T8: 302s [main → outro, beat: clear → clear] — as the energy fades, contract your movement, slow the basic, and prepare to close.
```

### kizomba_transitions verifier stats

```
parsed=8 boundaries_matched=8 boundaries_invented=0 boundaries_missing_filled=0 skipped_lines=0 output_lines=8 retried=0 retry_succeeded=0
```

### kizomba_tutor (polished)

```
P1: 0s-18s, intro [beat: clear] — Find your connection in a close embrace; use a soft, minimal pulse to ground yourself.
P2: 18s-172s, main ×13 [beat: clear] — Build your foundation; use steady walk-steps and let the bass guide your weight transfers.
P3: 172s-195s, instrumental ×2 [beat: clear] — Maintain your flow; keep a smooth pulse and a stable frame as the texture stays balanced.
P4: 195s-212s, main [beat: clear] — Sustain the momentum; continue your rhythmic walking and focus on following the bass line.
P5: 212s-228s, instrumental [beat: clear] — Increase your presence; try traveling through the space with more intentional steps.
P6: 228s-233s, peak [beat: clear] — Embrace the energy; use more expressive movement and varied leading to match the intensity.
P7: 233s-265s, main ×3 [beat: clear] — Return to the basics; re-establish your walk-step and reconnect with your partner.
P8: 265s-302s, main ×3 [beat: clear] — Close with control; contract your movements and keep your steps compact as the energy settles.
P9: 302s-314s, outro [beat: clear] — End gently; return to a minimal pulse and let the dance fade out softly.
```

### unified timeline (phases + transitions)

```
P1: 0s-18s, intro [beat: clear] — Find your connection in a close embrace; use a soft, minimal pulse to ground yourself.
T1: 18s [intro → main, beat: clear → clear] — when the bass kicks in, walk-step the basic on the first clear bass hit.
P2: 18s-172s, main ×13 [beat: clear] — Build your foundation; use steady walk-steps and let the bass guide your weight transfers.
T2: 172s [main → instrumental, beat: clear → clear] — keep your basic going steadily.
P3: 172s-195s, instrumental ×2 [beat: clear] — Maintain your flow; keep a smooth pulse and a stable frame as the texture stays balanced.
T3: 195s [instrumental → main, beat: clear → clear] — keep your basic going steadily.
P4: 195s-212s, main [beat: clear] — Sustain the momentum; continue your rhythmic walking and focus on following the bass line.
T4: 212s [main → instrumental, beat: clear → clear] — keep your basic going steadily.
P5: 212s-228s, instrumental [beat: clear] — Increase your presence; try traveling through the space with more intentional steps.
T5: 228s [instrumental → peak, beat: clear → clear] — commit to the new energy, travel more, and add intention.
P6: 228s-233s, peak [beat: clear] — Embrace the energy; use more expressive movement and varied leading to match the intensity.
T6: 233s [peak → main, beat: clear → clear] — as the energy settles, settle back, breathe, and return to the basic.
P7: 233s-265s, main ×3 [beat: clear] — Return to the basics; re-establish your walk-step and reconnect with your partner.
T7: 265s [main → main, beat: clear → clear] — as the energy settles and the percussion thins, keep the basic and hold a steady frame.
P8: 265s-302s, main ×3 [beat: clear] — Close with control; contract your movements and keep your steps compact as the energy settles.
T8: 302s [main → outro, beat: clear → clear] — as the energy fades, contract your movement, slow the basic, and prepare to close.
P9: 302s-314s, outro [beat: clear] — End gently; return to a minimal pulse and let the dance fade out softly.
```

## eval_set: Bonga_-_Mona_Ki_Ngi_Xica

```
source=eval_set | file=Bonga_-_Mona_Ki_Ngi_Xica [GjR7H-IytJQ].mp3
  tempo=92.3 BPM | beats=421 | sections=25 | vocal_env=yes
    intro       0.0s-  28.7s  beat_clarity=0.24
    main       28.7s-  47.7s  beat_clarity=0.27
    main       47.7s-  53.5s  beat_clarity=0.33
    main       53.5s-  64.5s  beat_clarity=0.25
    main       64.5s-  75.7s  beat_clarity=0.29
    main       75.7s-  87.0s  beat_clarity=0.31
    main       87.0s-  98.8s  beat_clarity=0.29
    main       98.8s- 110.3s  beat_clarity=0.19
    main      110.3s- 122.0s  beat_clarity=0.32
    main      122.0s- 134.7s  beat_clarity=0.31
    main      134.7s- 140.4s  beat_clarity=0.37
    main      140.4s- 157.8s  beat_clarity=0.24
    peak      157.8s- 164.7s  beat_clarity=0.31
    main      164.7s- 175.9s  beat_clarity=0.32
    main      175.9s- 186.4s  beat_clarity=0.24
    main      186.4s- 198.0s  beat_clarity=0.39
    main      198.0s- 208.7s  beat_clarity=0.32
    main      208.7s- 219.5s  beat_clarity=0.30
    main      219.5s- 231.3s  beat_clarity=0.26
    main      231.3s- 248.2s  beat_clarity=0.27
    main      248.2s- 258.4s  beat_clarity=0.37
    main      258.4s- 264.1s  beat_clarity=0.27
    main      264.1s- 277.4s  beat_clarity=0.21
    main      277.4s- 287.5s  beat_clarity=0.30
    outro     287.5s- 301.0s  beat_clarity=0.15
```

### listening_guide

```
This 301.0-second track moves at a tempo of 92 BPM, following a journey from a low-energy intro through several main phases, reaching a high-energy peak at 158s, before settling into a gentle outro. The rhythm is drum-light, with melodic and harmonic content carrying the pulse rather than a heavy percussive grid. You will notice an unusually dense amount of ornamentation and syncopation throughout the track, making the musical texture feel very tight and intricate.

The most challenging moment occurs during the outro starting at 287s, where the beat becomes subtle and the pulse thins out significantly. You may also find the rhythm difficult to lock into during certain main sections where the beat clarity is only moderate, as the pulse is felt through the bass rather than being clearly defined by percussion. Because the percussiveness is so low throughout, the rhythm can feel elusive. During the final transition, simply feel the underlying pulse.
```

### kizomba_tutor (one-pass)

```
P1: 0s-29s, intro [beat: moderate] — Find the pulse through the bass and stay compact with minimal movement.
P2: 29s-65s, main ×3 [beat: moderate] — Establishing the rhythm; test the pulse with small, steady walk-steps.
P3: 65s-158s, main ×8 [beat: moderate] — Sustaining the flow; focus on smooth weight transfers to match the bass.
P4: 158s-165s, peak [beat: moderate] — The emotional high point; you can travel more and add more expression.
P5: 165s-248s, main ×7 [beat: moderate] — Returning to the basic; reconnect with your partner and keep the walk steady.
P6: 248s-287s, main ×4 [beat: moderate] — Closing the song; contract your movement and prepare to wind down.
P7: 287s-301s, outro [beat: subtle] — The pulse is hard to lock onto; make your movements very small and let the dance end gently.
```

### kizomba_drills (verified)

```
P1: intro (0s-29s, beat: moderate) — Drill: maintain a close embrace and feel the pulse together. 29s.
P2-P3: main (29s-158s, beat: moderate) — Drill: execute a steady walk-step following the bass line. 35.5s.
P4: peak (158s-165s, beat: moderate) — Drill: stay compact and test the pulse with small steps. 7s.
P5-P6: main (165s-287s, beat: moderate) — Drill: keep steps small and compact to avoid chasing the ornamentation. 100.2s.
P7: outro (287s-301s, beat: subtle) — Drill: reduce travel and let the movement wind down. 14s.
```

### kizomba_drills verifier stats

```
parsed=8 repaired_ranges=3 duplicate_phases=0 filled_missing=2 skipped_lines=5 output_lines=5
```

### kizomba_drills raw Gemma draft

```
P1: intro (0s-29s, beat: moderate) — Drill: maintain a close embrace and feel the pulse together. 29s.
P2-P4: main (29s-64.5s, beat: moderate) — Drill: execute a steady walk-step following the bass line. 35.5s.
P5-P15: main (64.5s-164.7s, beat: moderate) — Drill: keep steps small and compact to avoid chasing the ornamentation. 100.2s.
P16: peak (158s-165s, beat: moderate) — Drill: increase leading variety and expression. 7s.
P17-P22: main (165s-287s, beat: moderate) — Drill: same walk-step as P5-P15, but add subtle hip styling once the basic feels automatic. 122s.
P23: main (264.1s-277.4s, beat: moderate) — Drill: practice a three-step pattern with a light pause. 13.3s.
P24: main (277.4s-287.5s, beat: moderate) — Drill: return to a steady walk-step. 10.1s.
P25: outro (287.5s-301s, beat: subtle) — Drill: slow the pace and return to minimal movement. 13.5s.
```

### describe_transitions

```
Transitions table — 6 label boundaries
======================================
 #  time   from              →  to                from→to beat   from→to energy
----------------------------------------------------------------------------------------
 1    28.7s  intro             →  main              moderate → moderate      low → low   
 2    64.5s  main              →  main              moderate → moderate      low → high/medium
 3   157.8s  main              →  peak              moderate → moderate   high/medium → high  
 4   164.7s  peak              →  main              moderate → moderate     high → high/medium
 5   248.2s  main              →  main              moderate → moderate   high/medium → high/medium
 6   287.5s  main              →  outro             moderate → subtle     high/medium → low
```

### kizomba_transitions (verified)

```
T1: 29s [intro → main, beat: moderate → moderate] — walk-step the basic on the first clear bass hit as the percussion returns.
T2: 65s [main → main, beat: moderate → moderate] — travel a little more and add intention as the energy lifts and the texture becomes busier.
T3: 158s [main → peak, beat: moderate → moderate] — commit to the new energy and travel more as the music reaches its emotional high point.
T4: 165s [peak → main, beat: moderate → moderate] — settle back, breathe, and return to the basic as the energy settles.
T5: 248s [main → main, beat: moderate → moderate] — keep the basic and hold a steady frame as the energy shifts.
T6: 287s [main → outro, beat: moderate → subtle] — contract your movement, slow the basic, and prepare to close as the energy fades and the percussion thins; if the pulse feels too subtle, shrink to small weight shifts.
```

### kizomba_transitions verifier stats

```
parsed=6 boundaries_matched=6 boundaries_invented=0 boundaries_missing_filled=0 skipped_lines=0 output_lines=6 retried=0 retry_succeeded=0
```

### kizomba_tutor (polished)

```
P1: 0s-29s, intro [beat: moderate] — Listen for the bass to find the rhythm; keep your movements small and your frame compact.
P2: 29s-65s, main ×3 [beat: moderate] — Start finding the groove; use small, steady steps to test your connection and timing.
P3: 65s-158s, main ×8 [beat: moderate] — Maintain your flow; focus on smooth weight transfers that follow the steady pulse.
P4: 158s-165s, peak [beat: moderate] — Use this energy to increase your travel or add more expressive movement.
P5: 165s-248s, main ×7 [beat: moderate] — Return to the core rhythm; reconnect with your partner and maintain a consistent walk.
P6: 248s-287s, main ×4 [beat: moderate] — Begin to wind down; reduce your travel and tighten your movements as the song nears its end.
P7: 287s-301s, outro [beat: subtle] — The pulse is soft; keep your movements very minimal and let the dance fade out gently.
```

### unified timeline (phases + transitions)

```
P1: 0s-29s, intro [beat: moderate] — Listen for the bass to find the rhythm; keep your movements small and your frame compact.
T1: 29s [intro → main, beat: moderate → moderate] — walk-step the basic on the first clear bass hit as the percussion returns.
P2: 29s-65s, main ×3 [beat: moderate] — Start finding the groove; use small, steady steps to test your connection and timing.
T2: 65s [main → main, beat: moderate → moderate] — travel a little more and add intention as the energy lifts and the texture becomes busier.
P3: 65s-158s, main ×8 [beat: moderate] — Maintain your flow; focus on smooth weight transfers that follow the steady pulse.
T3: 158s [main → peak, beat: moderate → moderate] — commit to the new energy and travel more as the music reaches its emotional high point.
P4: 158s-165s, peak [beat: moderate] — Use this energy to increase your travel or add more expressive movement.
T4: 165s [peak → main, beat: moderate → moderate] — settle back, breathe, and return to the basic as the energy settles.
P5: 165s-248s, main ×7 [beat: moderate] — Return to the core rhythm; reconnect with your partner and maintain a consistent walk.
T5: 248s [main → main, beat: moderate → moderate] — keep the basic and hold a steady frame as the energy shifts.
P6: 248s-287s, main ×4 [beat: moderate] — Begin to wind down; reduce your travel and tighten your movements as the song nears its end.
T6: 287s [main → outro, beat: moderate → subtle] — contract your movement, slow the basic, and prepare to close as the energy fades and the percussion thins; if the pulse feels too subtle, shrink to small weight shifts.
P7: 287s-301s, outro [beat: subtle] — The pulse is soft; keep your movements very minimal and let the dance fade out gently.
```

## eval_set: Charbel_-_E_Magia_Ben_Ana

```
source=eval_set | file=Charbel_-_E_Magia_Ben_Ana [6McenE8gUqM].mp3
  tempo=95.7 BPM | beats=284 | sections=16 | vocal_env=yes
    intro       0.0s-  17.3s  beat_clarity=0.51
    short_break   17.3s-  22.8s  beat_clarity=0.50
    main       22.8s-  33.0s  beat_clarity=0.59
    main       33.0s-  38.1s  beat_clarity=0.61
    main       38.1s-  48.0s  beat_clarity=0.38
    main       48.0s-  58.2s  beat_clarity=0.28
    main       58.2s-  68.8s  beat_clarity=0.42
    main       68.8s-  84.7s  beat_clarity=0.27
    short_break   84.7s-  89.8s  beat_clarity=0.47
    main       89.8s- 100.0s  beat_clarity=0.56
    main      100.0s- 110.3s  beat_clarity=0.34
    build     110.3s- 120.5s  beat_clarity=0.36
    peak      120.5s- 130.7s  beat_clarity=0.39
    main      130.7s- 140.9s  beat_clarity=0.40
    break     140.9s- 163.2s  beat_clarity=0.24
    outro     163.2s- 185.4s  beat_clarity=0.36
```

### listening_guide

```
This 185.4-second track moves at a tempo of 96 BPM, following a structural arc that begins with a low-energy intro, moves into a main section, builds toward a high-energy peak, and eventually transitions into a quiet break before an outro. The rhythm is characterized by unusually low percussiveness, meaning the pulse is carried more by melodic and harmonic content than by a heavy drum kit.

The most challenging moment occurs during the break from 141s to 163s, where the beat clarity becomes moderate and the pulse thins out significantly. You may find it difficult to anchor your timing here because the rhythmic density drops and the percussion becomes very minimal. Another area to watch is the build and peak around 110s to 131s; while the energy is high, the beat remains subtle rather than driving. During the quietest break, do not try to find a heavy beat; instead, trust the bass line to guide your sense of timing.
```

### kizomba_tutor (one-pass)

```
P1: 0s-17s, intro [beat: clear] — The pulse is felt through the bass; keep movement minimal and focus on connection.
P2: 17s-23s, short_break [beat: clear] — The pulse remains steady; maintain a small, controlled walk.
P3: 23s-85s, main ×6 [beat: clear] — Establishing the rhythm; settle into a steady walk-step and follow the bass line.
P4: 85s-90s, short_break [beat: clear] — The pulse is still easy to find; keep your weight transfers smooth.
P5: 90s-110s, main ×2 [beat: clear] — Sustaining the energy; focus on a consistent frame as you continue your walk.
P6: 110s-120s, build [beat: clear] — The music is pulling you forward; gradually increase your step size and expression.
P7: 120s-131s, peak [beat: clear] — This is the emotional high point; use more variety in your leading and stronger steps.
P8: 131s-141s, main [beat: clear] — Returning to the basics; re-establish your steady walk-step after the peak.
P9: 141s-163s, break [beat: moderate] — The pulse is a bit less obvious; stay compact and test the rhythm with small weight shifts.
P10: 163s-185s, outro [beat: clear] — Winding down; slow your movement and return to a gentle, minimal connection.
```

### kizomba_drills (verified)

```
P1: intro (0s-17s, beat: clear) — Drill: focus on connection through a minimal frame. 17s.
P2: short_break (17s-23s, beat: clear) — Drill: reset your posture and prepare for movement. 6s.
P3: main (23s-85s, beat: clear) — Drill: practice a steady walk-step following the bass line. 30s loop, repeated through the six main phases. 62s.
P4: short_break (85s-90s, beat: clear) — Drill: reduce travel and keep a small pulse in the body to reset. 5s.
P5: main (90s-110s, beat: clear) — Drill: practice steady weight transfers through this section. 20s.
P6: build (110s-120s, beat: clear) — Drill: practice steady weight transfers through this section. 10s.
P7: peak (120s-131s, beat: clear) — Drill: practice steady weight transfers through this section. 10s.
P8: main (131s-141s, beat: clear) — Drill: practice steady weight transfers through this section. 10s.
P9: break (141s-163s, beat: moderate) — Drill: reduce travel and keep a small pulse in the body to reset. 22s.
P10: outro (163s-185s, beat: clear) — Drill: reduce travel and let the movement wind down. 22s.
```

### kizomba_drills verifier stats

```
parsed=10 repaired_ranges=4 duplicate_phases=0 filled_missing=7 skipped_lines=7 output_lines=10
```

### kizomba_drills raw Gemma draft

```
P1: intro (0s-17s, beat: clear) — Drill: focus on connection through a minimal frame. 17s.
P2: short_break (17s-23s, beat: clear) — Drill: reset your posture and prepare for movement. 6s.
P3-P8: main (23s-85s, beat: clear) — Drill: practice a steady walk-step following the bass line. 30s loop, repeated through the six main phases. 62s.
P9: short_break (85s-90s, beat: clear) — Drill: reduce travel and maintain a small pulse in the body. 5s.
P10-P12: main (90s-120s, beat: clear) — Drill: maintain the same walk-step as P3-P8. 30s loop, repeated through the three main phases. 30s.
P13: build (110s-120s, beat: clear) — Drill: gradually increase step size to build tension. 10s.
P14: peak (120s-131s, beat: clear) — Drill: use more variety in your leading. 11s.
P15: main (131s-141s, beat: clear) — Drill: same walk-step as P3-P8, but now add subtle hip styling once the basic feels automatic. 10s.
P16: break (141s-163s, beat: moderate) — Drill: keep steps small and test the pulse. 22s.
P17: outro (163s-185s, beat: clear) — Drill: slow the pace and return to minimal movement. 22s.
```

### describe_transitions

```
Transitions table — 9 label boundaries
======================================
 #  time   from              →  to                from→to beat   from→to energy
----------------------------------------------------------------------------------------
 1    17.3s  intro             →  short_break          clear → clear         low → medium
 2    22.8s  short_break       →  main                 clear → clear      medium → high/medium
 3    84.7s  main              →  short_break          clear → clear      high/medium → medium
 4    89.8s  short_break       →  main                 clear → clear      medium → medium
 5   110.3s  main              →  build                clear → clear      medium → high  
 6   120.5s  build             →  peak                 clear → clear        high → high  
 7   130.7s  peak              →  main                 clear → clear        high → high  
 8   140.9s  main              →  break                clear → moderate     high → low   
 9   163.2s  break             →  outro             moderate → clear         low → medium
```

### kizomba_transitions (verified)

```
T1: 17s [intro → short_break, beat: clear → clear] — As the energy lifts, transition from minimal movement to a steady walk-step.
T2: 23s [short_break → main, beat: clear → clear] — As the energy increases, travel a little more and add intention to your steps.
T3: 85s [main → short_break, beat: clear → clear] — As the energy settles, keep the basic going and hold a steady frame.
T4: 90s [short_break → main, beat: clear → clear] — As the energy lifts, travel a little more and add intention.
T5: 110s [main → build, beat: clear → clear] — As the energy increases, commit to the new energy and travel more.
T6: 120s [build → peak, beat: clear → clear] — Commit to the new energy, travel more, and add more expression.
T7: 131s [peak → main, beat: clear → clear] — As the energy settles, settle back, breathe, and return to the basic.
T8: 141s [main → break, beat: clear → moderate] — As the energy fades and the percussion thins, keep a small pulse in the body, listen, and reset.
T9: 163s [break → outro, beat: moderate → clear] — Walk-step on the first clear bass hit, then contract your movement and slow the basic to prepare to close.
```

### kizomba_transitions verifier stats

```
parsed=9 boundaries_matched=9 boundaries_invented=0 boundaries_missing_filled=0 skipped_lines=0 output_lines=9 retried=0 retry_succeeded=0
```

### kizomba_tutor (polished)

```
P1: 0s-17s, intro [beat: clear] — Feel the bass through your feet; keep your movements small and focus on establishing a solid connection.
P2: 17s-23s, short_break [beat: clear] — The rhythm is steady; maintain a small, controlled pulse in your steps to stay ready.
P3: 23s-85s, main ×6 [beat: clear] — Find your groove; settle into a consistent walk-step that follows the bass line.
P4: 85s-90s, short_break [beat: clear] — The pulse is easy to find; keep your weight transfers smooth and avoid sudden shifts.
P5: 90s-110s, main ×2 [beat: clear] — Maintain your energy; focus on a steady frame while continuing your rhythmic walk.
P6: 110s-120s, build [beat: clear] — The music is gaining momentum; try increasing your step size or adding more intention to your movement.
P7: 120s-131s, peak [beat: clear] — This is the musical highlight; use more variety in your steps and express the energy through your frame.
P8: 131s-141s, main [beat: clear] — Return to the foundation; re-establish your steady, rhythmic walk-step.
P9: 141s-163s, break [beat: moderate] — The rhythm is more subtle; stay compact and use small weight shifts to avoid chasing extra percussion.
P10: 163s-185s, outro [beat: clear] — Winding down; slow your pace and return to a gentle, minimal connection.
```

### unified timeline (phases + transitions)

```
P1: 0s-17s, intro [beat: clear] — Feel the bass through your feet; keep your movements small and focus on establishing a solid connection.
T1: 17s [intro → short_break, beat: clear → clear] — As the energy lifts, transition from minimal movement to a steady walk-step.
P2: 17s-23s, short_break [beat: clear] — The rhythm is steady; maintain a small, controlled pulse in your steps to stay ready.
T2: 23s [short_break → main, beat: clear → clear] — As the energy increases, travel a little more and add intention to your steps.
P3: 23s-85s, main ×6 [beat: clear] — Find your groove; settle into a consistent walk-step that follows the bass line.
T3: 85s [main → short_break, beat: clear → clear] — As the energy settles, keep the basic going and hold a steady frame.
P4: 85s-90s, short_break [beat: clear] — The pulse is easy to find; keep your weight transfers smooth and avoid sudden shifts.
T4: 90s [short_break → main, beat: clear → clear] — As the energy lifts, travel a little more and add intention.
P5: 90s-110s, main ×2 [beat: clear] — Maintain your energy; focus on a steady frame while continuing your rhythmic walk.
T5: 110s [main → build, beat: clear → clear] — As the energy increases, commit to the new energy and travel more.
P6: 110s-120s, build [beat: clear] — The music is gaining momentum; try increasing your step size or adding more intention to your movement.
T6: 120s [build → peak, beat: clear → clear] — Commit to the new energy, travel more, and add more expression.
P7: 120s-131s, peak [beat: clear] — This is the musical highlight; use more variety in your steps and express the energy through your frame.
T7: 131s [peak → main, beat: clear → clear] — As the energy settles, settle back, breathe, and return to the basic.
P8: 131s-141s, main [beat: clear] — Return to the foundation; re-establish your steady, rhythmic walk-step.
T8: 141s [main → break, beat: clear → moderate] — As the energy fades and the percussion thins, keep a small pulse in the body, listen, and reset.
P9: 141s-163s, break [beat: moderate] — The rhythm is more subtle; stay compact and use small weight shifts to avoid chasing extra percussion.
T9: 163s [break → outro, beat: moderate → clear] — Walk-step on the first clear bass hit, then contract your movement and slow the basic to prepare to close.
P10: 163s-185s, outro [beat: clear] — Winding down; slow your pace and return to a gentle, minimal connection.
```

## eval_set: Charbel_-_E_Magia_Official_Video_4K

```
source=eval_set | file=Charbel_-_E_Magia_Official_Video_4K [QkfyDj8aJRM].mp3
  tempo=95.7 BPM | beats=382 | sections=19 | vocal_env=yes
    intro       0.0s-  35.9s  beat_clarity=0.15
    break      35.9s-  51.2s  beat_clarity=0.50
    main       51.2s-  61.4s  beat_clarity=0.56
    main       61.4s-  71.6s  beat_clarity=0.32
    main       71.6s-  81.8s  beat_clarity=0.38
    main       81.8s-  92.5s  beat_clarity=0.35
    main       92.5s- 102.9s  beat_clarity=0.31
    short_break  102.9s- 113.4s  beat_clarity=0.47
    main      113.4s- 123.9s  beat_clarity=0.58
    main      123.9s- 134.2s  beat_clarity=0.38
    main      134.2s- 138.9s  beat_clarity=0.38
    main      138.9s- 154.6s  beat_clarity=0.38
    main      154.6s- 164.7s  beat_clarity=0.41
    break     164.7s- 186.5s  beat_clarity=0.25
    main      186.5s- 196.7s  beat_clarity=0.35
    main      196.7s- 206.9s  beat_clarity=0.29
    main      206.9s- 216.8s  beat_clarity=0.38
    main      216.8s- 227.4s  beat_clarity=0.36
    outro     227.4s- 254.3s  beat_clarity=0.25
```

### listening_guide

```
This track lasts 254.3 seconds with a tempo of 96 BPM. The musical journey begins with a low-energy intro, moves through several main sections of varying energy, and includes distinct breaks before settling into a gentle outro. Because the percussiveness is unusually low, you will find the rhythm is drum-light; instead of a heavy percussive grid, the pulse is carried primarily by the melodic and harmonic content and the underlying bass line.

The most challenging moment occurs during the intro from 0s to 36s, where the beat is subtle and the pulse is felt rather than heard. You may also find the transition into the break at 165s difficult as the beat clarity shifts to moderate. The hardest stretch is the very beginning, as the lack of prominent percussion makes the pulse harder to lock onto. During these subtle moments, focus on feeling the underlying pulse through the bass line.
```

### kizomba_tutor (one-pass)

```
P1: 0s-36s, intro [beat: subtle] — The pulse is hard to lock onto as the bass carries the rhythm; keep movement minimal and just feel a tiny weight shift to stay connected.
P2: 36s-51s, break [beat: clear] — The rhythm becomes much more percussive here; use this clear pulse to reset your frame and prepare for more movement.
P3: 51s-103s, main ×5 [beat: clear] — This establishing phase has a steady pulse; it is safe to trust the rhythm and begin a smooth, steady walk-step.
P4: 103s-113s, short_break [beat: clear] — The beat remains clear but feels more syncopated; lean into the weight transfers to stay in time.
P5: 113s-165s, main ×5 [beat: clear] — As we move into this sustaining phase, focus on maintaining a consistent frame while the pulse remains easy to follow.
P6: 165s-187s, break [beat: moderate] — The beat is less obvious now; stay compact and test the pulse with small, controlled steps.
P7: 187s-227s, main ×4 [beat: moderate] — This closing phase is building toward the end; keep your steps small and avoid chasing extra percussion.
P8: 227s-254s, outro [beat: moderate] — As the song winds down, avoid chasing the rhythm and simply return to gentle, minimal movement.
```

### kizomba_drills (verified)

```
P1: intro (0s-36s, beat: subtle) — Drill: mark the pulse with a tiny shoulder bounce and count 8 internally to prepare for the entry. 36s.
P2: break (36s-51s, beat: clear) — Drill: reduce travel and keep a small pulse in the body to reset. 15s.
P3: main (51s-103s, beat: clear) — Drill: practice a steady walk-step focusing on weight transfer. 52s.
P4: short_break (103s-113s, beat: clear) — Drill: reduce travel and keep a small pulse in the body to reset. 10s.
P5: main (113s-165s, beat: clear) — Drill: practice steady weight transfers through this section. 51s.
P6: break (165s-187s, beat: moderate) — Drill: reduce travel and keep a small pulse in the body to reset. 22s.
P7: main (187s-227s, beat: moderate) — Drill: stay compact and test the pulse with small steps. 41s.
P8: outro (227s-254s, beat: moderate) — Drill: reduce travel and let the movement wind down. 27s.
```

### kizomba_drills verifier stats

```
parsed=8 repaired_ranges=2 duplicate_phases=0 filled_missing=5 skipped_lines=5 output_lines=8
```

### kizomba_drills raw Gemma draft

```
P1: intro (0s-36s, beat: subtle) — Drill: mark the pulse with a tiny shoulder bounce and count 8 internally to prepare for the entry. 36s.
P2: break (36s-51s, beat: clear) — Drill: reduce travel and keep a small pulse in the body to reset. 15s.
P3-P7: main (51s-103s, beat: clear) — Drill: practice a steady walk-step focusing on weight transfer. 52s.
P8: short_break (103s-113s, beat: clear) — Drill: shrink the dance and maintain a small body pulse during the syncopated feel. 10s.
P9-P13: main (113s-165s, beat: clear) — Drill: same walk-step as P3-P7, but now add subtle hip styling once the basic feels automatic. 52s.
P14: break (165s-187s, beat: moderate) — Drill: keep steps small and test the pulse to stay compact. 22s.
P15-P18: main (187s-227s, beat: moderate) — Drill: maintain small steps and avoid chasing extra percussion. 40s.
P19: outro (227s-254s, beat: moderate) — Drill: slow the pace and return to minimal movement. 27s.
```

### describe_transitions

```
Transitions table — 7 label boundaries
======================================
 #  time   from              →  to                from→to beat   from→to energy
----------------------------------------------------------------------------------------
 1    35.9s  intro             →  break               subtle → clear         low → medium
 2    51.2s  break             →  main                 clear → clear      medium → high/medium
 3   102.9s  main              →  short_break          clear → clear      high/medium → medium
 4   113.4s  short_break       →  main                 clear → clear      medium → high/medium
 5   164.7s  main              →  break                clear → moderate   high/medium → low   
 6   186.5s  break             →  main              moderate → moderate      low → high/medium
 7   227.4s  main              →  outro             moderate → moderate   high/medium → low
```

### kizomba_transitions (verified)

```
T1: 36s [intro → break, beat: subtle → clear] — as the percussion returns, keep a small pulse in the body and listen to the new rhythm.
T2: 51s [break → main, beat: clear → clear] — walk-step on the first clear bass hit.
T3: 103s [main → short_break, beat: clear → clear] — as the energy settles, lean into the syncopated feel by transferring weight when the bass pulls.
T4: 113s [short_break → main, beat: clear → clear] — walk-step on the first clear bass hit.
T5: 165s [main → break, beat: clear → moderate] — as the energy fades and the percussion thins, keep a small pulse in the body and reset.
T6: 187s [break → main, beat: moderate → moderate] — as the percussion returns, walk-step on the first clear bass hit.
T7: 227s [main → outro, beat: moderate → moderate] — as the energy fades and the percussion thins, contract your movement and slow the basic to prepare to close.
```

### kizomba_transitions verifier stats

```
parsed=7 boundaries_matched=7 boundaries_invented=0 boundaries_missing_filled=0 skipped_lines=0 output_lines=7 retried=0 retry_succeeded=0
```

### kizomba_tutor (polished)

```
P1: 0s-36s, intro [beat: subtle] — The rhythm is soft and layered; keep your movements minimal, using tiny weight shifts to stay connected to your partner.
P2: 36s-51s, break [beat: clear] — The percussion becomes more defined; use this pulse to reset your frame and prepare for more active movement.
P3: 51s-103s, main ×5 [beat: clear] — This phase offers a steady pulse; use this stability to practice a smooth, consistent walk-step.
P4: 103s-113s, short_break [beat: clear] — The rhythm feels more syncopated; focus on clean weight transfers to stay in time with the pulse.
P5: 113s-165s, main ×5 [beat: clear] — As the song sustains, focus on maintaining a steady frame while following the easy-to-track rhythm.
P6: 165s-187s, break [beat: moderate] — The beat is less obvious; stay compact and use small, controlled steps to test the pulse.
P7: 187s-227s, main ×4 [beat: moderate] — As the energy builds, keep your steps small and avoid chasing extra percussion.
P8: 227s-254s, outro [beat: moderate] — As the song winds down, avoid chasing the rhythm and return to gentle, minimal movement.
```

### unified timeline (phases + transitions)

```
P1: 0s-36s, intro [beat: subtle] — The rhythm is soft and layered; keep your movements minimal, using tiny weight shifts to stay connected to your partner.
T1: 36s [intro → break, beat: subtle → clear] — as the percussion returns, keep a small pulse in the body and listen to the new rhythm.
P2: 36s-51s, break [beat: clear] — The percussion becomes more defined; use this pulse to reset your frame and prepare for more active movement.
T2: 51s [break → main, beat: clear → clear] — walk-step on the first clear bass hit.
P3: 51s-103s, main ×5 [beat: clear] — This phase offers a steady pulse; use this stability to practice a smooth, consistent walk-step.
T3: 103s [main → short_break, beat: clear → clear] — as the energy settles, lean into the syncopated feel by transferring weight when the bass pulls.
P4: 103s-113s, short_break [beat: clear] — The rhythm feels more syncopated; focus on clean weight transfers to stay in time with the pulse.
T4: 113s [short_break → main, beat: clear → clear] — walk-step on the first clear bass hit.
P5: 113s-165s, main ×5 [beat: clear] — As the song sustains, focus on maintaining a steady frame while following the easy-to-track rhythm.
T5: 165s [main → break, beat: clear → moderate] — as the energy fades and the percussion thins, keep a small pulse in the body and reset.
P6: 165s-187s, break [beat: moderate] — The beat is less obvious; stay compact and use small, controlled steps to test the pulse.
T6: 187s [break → main, beat: moderate → moderate] — as the percussion returns, walk-step on the first clear bass hit.
P7: 187s-227s, main ×4 [beat: moderate] — As the energy builds, keep your steps small and avoid chasing extra percussion.
T7: 227s [main → outro, beat: moderate → moderate] — as the energy fades and the percussion thins, contract your movement and slow the basic to prepare to close.
P8: 227s-254s, outro [beat: moderate] — As the song winds down, avoid chasing the rhythm and return to gentle, minimal movement.
```

## eval_set: Criola

```
source=eval_set | file=Criola [kCOie6jQXag].mp3
  tempo=80.7 BPM | beats=371 | sections=24 | vocal_env=yes
    intro       0.0s-  10.2s  beat_clarity=0.37
    main       10.2s-  16.4s  beat_clarity=0.36
    short_break   16.4s-  28.8s  beat_clarity=0.32
    main       28.8s-  40.8s  beat_clarity=0.44
    main       40.8s-  46.8s  beat_clarity=0.48
    main       46.8s-  64.8s  beat_clarity=0.46
    main       64.8s-  76.8s  beat_clarity=0.33
    main       76.8s-  82.8s  beat_clarity=0.40
    instrumental   82.8s-  94.8s  beat_clarity=0.46
    peak       94.8s- 100.8s  beat_clarity=0.47
    main      100.8s- 118.8s  beat_clarity=0.43
    main      118.8s- 130.7s  beat_clarity=0.36
    main      130.7s- 136.7s  beat_clarity=0.41
    main      136.7s- 154.7s  beat_clarity=0.35
    main      154.7s- 167.4s  beat_clarity=0.34
    main      167.4s- 178.8s  beat_clarity=0.41
    main      178.8s- 190.7s  beat_clarity=0.43
    main      190.7s- 196.5s  beat_clarity=0.39
    main      196.5s- 208.8s  beat_clarity=0.40
    main      208.8s- 220.8s  beat_clarity=0.32
    main      220.8s- 238.7s  beat_clarity=0.27
    main      238.7s- 251.3s  beat_clarity=0.26
    main      251.3s- 264.6s  beat_clarity=0.25
    outro     264.6s- 284.0s  beat_clarity=0.28
```

### listening_guide

```
This 284.0-second track moves at a tempo of 81 BPM, which is slower than the typical kizomba range. The song follows a structural arc that begins with a low-energy intro, moves through several main sections and a short break, reaches a high-energy peak, and eventually winds down through an outro. Because the percussiveness is unusually low, the rhythm is not driven by a heavy drum kit; instead, the melodic and harmonic content carries the pulse, creating a drum-light feel where the bass line is the primary guide for the rhythm.

The most challenging moments occur when the beat clarity shifts from clear to moderate. You may find it difficult to anchor yourself during the short break starting at 16.4s and again during the outro beginning at 265s, as the pulse becomes less obvious. The hardest stretch is the very end of the song, where the rhythm thins out significantly and the beat becomes less defined. During these transitions, do not try to find a sharp percussive hit; instead, trust the bass line to carry the pulse through the break.
```

### kizomba_tutor (one-pass)

```
P1: 0s-10s, intro [beat: clear] — The pulse is felt through the bass; stay close and just feel the connection.
P2: 10s-16s, main [beat: clear] — Establishing the rhythm; use a steady walk-step and let the bass guide your feet.
P3: 16s-29s, short_break [beat: moderate] — The rhythm shifts; stay compact and test the pulse with small weight transfers.
P4: 29s-83s, main ×5 [beat: clear] — Sustaining the energy; travel a little more with a steady, balanced walk.
P5: 83s-95s, instrumental [beat: clear] — Keeping the flow; maintain your walk-step as the texture shifts.
P6: 95s-101s, peak [beat: clear] — The emotional high point; add more expression and intention to your movement.
P7: 101s-265s, main ×13 [beat: clear] — Returning to the groove; reconnect with the basic and focus on smooth weight transfers.
P8: 265s-284s, outro [beat: moderate] — Closing the dance; reduce travel and let the movement end gently.
```

### kizomba_drills (verified)

```
P1: intro (0s-10s, beat: clear) — Drill: focus on connection through a close embrace without stepping. 10s.
P2: main (10s-16s, beat: clear) — Drill: practice a steady walk-step following the bass line. 6s.
P3: short_break (16s-29s, beat: moderate) — Drill: reduce travel and keep a small pulse in the body. 13s.
P4: main (29s-83s, beat: clear) — Drill: same walk-step as P2, but add subtle hip styling once the basic feels automatic. 54s.
P5: instrumental (83s-95s, beat: clear) — Drill: practice steady weight transfers through this section. 12s.
P6: peak (95s-101s, beat: clear) — Drill: practice steady weight transfers through this section. 6s.
P7: main (101s-265s, beat: clear) — Drill: practice steady weight transfers through this section. 164s.
P8: outro (265s-284s, beat: moderate) — Drill: reduce travel and let the movement wind down. 19s.
```

### kizomba_drills verifier stats

```
parsed=13 repaired_ranges=2 duplicate_phases=0 filled_missing=4 skipped_lines=9 output_lines=8
```

### kizomba_drills raw Gemma draft

```
P1: intro (0s-10s, beat: clear) — Drill: focus on connection through a close embrace without stepping. 10s.
P2: main (10s-16s, beat: clear) — Drill: practice a steady walk-step following the bass line. 6s.
P3: short_break (16s-29s, beat: moderate) — Drill: reduce travel and keep a small pulse in the body. 13s.
P4-P7: main (29s-83s, beat: clear) — Drill: same walk-step as P2, but add subtle hip styling once the basic feels automatic. 54s.
P8: instrumental (83s-95s, beat: clear) — Drill: maintain a steady walk-step with a focus on frame stability. 12s.
P9: peak (95s-101s, beat: clear) — Drill: use stronger, more expressive leading variety. 6s.
P10-P15: main (101s-167s, beat: clear) — Drill: practice weight transfer with a focus on following the bass. 66s.
P16-P17: main (167s-190s, beat: clear) — Drill: lead with a strong step and let lighter steps follow. 23s.
P18: main (190s-196s, beat: moderate) — Drill: keep steps small and test the pulse. 6s.
P19-P21: main (196s-238s, beat: clear) — Drill: return to the steady walk-step. 42s.
P22: main (238s-251s, beat: clear) — Drill: practice weight transfer while navigating the syncopation. 13s.
P23: main (251s-265s, beat: clear) — Drill: maintain a steady walk-step, keeping the energy low. 14s.
P24: outro (265s-284s, beat: moderate) — Drill: slow the pace and return to minimal movement. 19s.
```

### describe_transitions

```
Transitions table — 7 label boundaries
======================================
 #  time   from              →  to                from→to beat   from→to energy
----------------------------------------------------------------------------------------
 1    10.2s  intro             →  main                 clear → clear         low → low   
 2    16.4s  main              →  short_break          clear → moderate      low → medium
 3    28.8s  short_break       →  main              moderate → clear      medium → high/medium
 4    82.8s  main              →  instrumental         clear → clear      high/medium → medium
 5    94.8s  instrumental      →  peak                 clear → clear      medium → high  
 6   100.8s  peak              →  main                 clear → clear        high → high/low/medium
 7   264.6s  main              →  outro                clear → moderate   high/low/medium → low
```

### kizomba_transitions (verified)

```
T1: 10s [intro → main, beat: clear → clear] — walk-step the basic on the first clear bass hit.
T2: 16s [main → short_break, beat: clear → moderate] — keep a small pulse in the body, listen, and reset.
T3: 29s [short_break → main, beat: moderate → clear] — walk-step on the first clear bass hit.
T4: 83s [main → instrumental, beat: clear → clear] — keep your basic going steadily.
T5: 95s [instrumental → peak, beat: clear → clear] — commit to the new energy and travel more.
T6: 101s [peak → main, beat: clear → clear] — settle back, breathe, and return to the basic.
T7: 265s [main → outro, beat: clear → moderate] — as the energy fades and the percussion thins, contract your movement and slow the basic to prepare to close.
```

### kizomba_transitions verifier stats

```
parsed=7 boundaries_matched=7 boundaries_invented=0 boundaries_missing_filled=0 skipped_lines=0 output_lines=7 retried=0 retry_succeeded=0
```

### kizomba_tutor (polished)

```
P1: 0s-10s, intro [beat: clear] — Feel the deep bass pulse; stay close to your partner and focus on establishing a shared connection.
P2: 10s-16s, main [beat: clear] — Use the steady rhythm to find your stride; try a grounded walk-step that follows the bass.
P3: 16s-29s, short_break [beat: moderate] — The rhythm shifts; stay compact and use small, subtle weight transfers to stay in sync.
P4: 29s-83s, main ×5 [beat: clear] — Sustain the energy by increasing your travel with a balanced, rhythmic walk.
P5: 83s-95s, instrumental [beat: clear] — Maintain your flow; keep your walk-step consistent even as the musical texture changes.
P6: 95s-101s, peak [beat: clear] — Lean into the intensity; add more intention and presence to your movements.
P7: 101s-265s, main ×13 [beat: clear] — Return to the groove; focus on smooth, continuous weight transfers to maintain the flow.
P8: 265s-284s, outro [beat: moderate] — Wind down the dance; reduce your travel and let the movement settle gently.
```

### unified timeline (phases + transitions)

```
P1: 0s-10s, intro [beat: clear] — Feel the deep bass pulse; stay close to your partner and focus on establishing a shared connection.
T1: 10s [intro → main, beat: clear → clear] — walk-step the basic on the first clear bass hit.
P2: 10s-16s, main [beat: clear] — Use the steady rhythm to find your stride; try a grounded walk-step that follows the bass.
T2: 16s [main → short_break, beat: clear → moderate] — keep a small pulse in the body, listen, and reset.
P3: 16s-29s, short_break [beat: moderate] — The rhythm shifts; stay compact and use small, subtle weight transfers to stay in sync.
T3: 29s [short_break → main, beat: moderate → clear] — walk-step on the first clear bass hit.
P4: 29s-83s, main ×5 [beat: clear] — Sustain the energy by increasing your travel with a balanced, rhythmic walk.
T4: 83s [main → instrumental, beat: clear → clear] — keep your basic going steadily.
P5: 83s-95s, instrumental [beat: clear] — Maintain your flow; keep your walk-step consistent even as the musical texture changes.
T5: 95s [instrumental → peak, beat: clear → clear] — commit to the new energy and travel more.
P6: 95s-101s, peak [beat: clear] — Lean into the intensity; add more intention and presence to your movements.
T6: 101s [peak → main, beat: clear → clear] — settle back, breathe, and return to the basic.
P7: 101s-265s, main ×13 [beat: clear] — Return to the groove; focus on smooth, continuous weight transfers to maintain the flow.
T7: 265s [main → outro, beat: clear → moderate] — as the energy fades and the percussion thins, contract your movement and slow the basic to prepare to close.
P8: 265s-284s, outro [beat: moderate] — Wind down the dance; reduce your travel and let the movement settle gently.
```

## eval_set: Don_Kikas_-_Angolanamente_Sensual_Official_Video

```
source=eval_set | file=Don_Kikas_-_Angolanamente_Sensual_Official_Video [_yFZueebjeQ].mp3
  tempo=89.1 BPM | beats=528 | sections=31 | vocal_env=yes
    intro       0.0s-  23.4s  beat_clarity=0.25
    main       23.4s-  30.3s  beat_clarity=0.63
    main       30.3s-  47.3s  beat_clarity=0.39
    main       47.3s-  52.7s  beat_clarity=0.51
    main       52.7s-  68.9s  beat_clarity=0.56
    main       68.9s-  79.7s  beat_clarity=0.38
    main       79.7s-  85.1s  beat_clarity=0.60
    main       85.1s-  95.9s  beat_clarity=0.63
    main       95.9s- 101.3s  beat_clarity=0.57
    main      101.3s- 112.0s  beat_clarity=0.46
    peak      112.0s- 117.4s  beat_clarity=0.56
    main      117.4s- 128.2s  beat_clarity=0.59
    main      128.2s- 144.4s  beat_clarity=0.54
    main      144.4s- 155.2s  beat_clarity=0.56
    main      155.2s- 166.0s  beat_clarity=0.54
    main      166.0s- 176.8s  beat_clarity=0.59
    main      176.8s- 187.6s  beat_clarity=0.46
    main      187.6s- 203.7s  beat_clarity=0.50
    main      203.7s- 215.2s  beat_clarity=0.52
    main      215.2s- 226.0s  beat_clarity=0.45
    main      226.0s- 247.5s  beat_clarity=0.40
    instrumental  247.5s- 258.3s  beat_clarity=0.65
    main      258.3s- 263.8s  beat_clarity=0.49
    main      263.8s- 274.5s  beat_clarity=0.60
    main      274.5s- 279.9s  beat_clarity=0.47
    main      279.9s- 297.5s  beat_clarity=0.38
    main      297.5s- 308.2s  beat_clarity=0.46
    main      308.2s- 313.7s  beat_clarity=0.51
    main      313.7s- 324.4s  beat_clarity=0.43
    main      324.4s- 356.8s  beat_clarity=0.37
    outro     356.8s- 372.5s  beat_clarity=0.46
```

### listening_guide

```
This track spans 372.5 seconds at a steady 89 BPM. The musical journey begins with a medium-energy intro that transitions into a long, evolving main section characterized by varying energy levels. You will experience a brief, expressive peak before the music settles into several more main phases, eventually moving through an instrumental break and a high-energy stretch before concluding with a low-energy outro. Throughout most of the track, the pulse is felt through a clear percussive grid and a steady bass line.

The most challenging moment occurs during the very beginning, from 0s to 23s, where the beat is only moderate and the percussiveness is quite low. Because the pulse is more subtle here than in the later, clearer sections, it may be difficult to lock into the rhythm immediately. You might also find the transition into the instrumental phase at 248s requires extra focus as the energy drops. During that initial intro, don't try to find a heavy drum hit; instead, feel the underlying pulse through the bass.
```

### kizomba_tutor (one-pass)

```
P1: 0s-23s, intro [beat: moderate] — the pulse is felt through the bass; stay compact and test the pulse with small weight shifts.
P2: 23s-112s, main ×9 [beat: clear] — establishing the foundation; it is safe to trust the steady pulse and walk the basic.
P3: 112s-117s, peak [beat: clear] — the emotional high point; use the clear pulse to add more expression and intention.
P4: 117s-177s, main ×5 [beat: clear] — returning to the groove; re-establish the basic and focus on a steady weight transfer.
P5: 177s-204s, main ×2 [beat: clear] — sustaining the energy; keep your frame strong while following the steady pulse.
P6: 204s-248s, main ×3 [beat: clear] — sustaining the flow; focus on your breath and let the pulse guide your movement.
P7: 248s-258s, instrumental [beat: clear] — a quieter moment; reduce travel and keep a small, steady pulse in the body.
P8: 258s-280s, main ×3 [beat: clear] — returning to the rhythm; reconnect with your partner and use the clear pulse to walk evenly.
P9: 280s-357s, main ×5 [beat: clear] — closing the main theme; movement should begin to contract as you prepare to wind down.
P10: 357s-373s, outro [beat: clear] — the song is ending; let the dance end gently with minimal, smooth movement.
```

### kizomba_drills (verified)

```
P1: intro (0s-23s, beat: moderate) — Drill: test the pulse with tiny shoulder bounces while staying compact. 23s.
P2: main (23s-112s, beat: clear) — Drill: focus on weight transfer during a steady walk-step. 89s.
P3: peak (112s-117s, beat: clear) — Drill: use more expressive leading variety. 5s.
P4-P6: main (117s-248s, beat: clear) — Drill: same walk-step as P2, but now add subtle hip styling once the basic feels automatic. 131s.
P7: instrumental (248s-258s, beat: clear) — Drill: reduce travel and keep a small pulse in the body. 10s.
P8-P9: main (258s-357s, beat: clear) — Drill: maintain a steady walk-step following the bass line. 99s.
P10: outro (357s-373s, beat: clear) — Drill: slow the pace and return to minimal movement. 16s.
```

### kizomba_drills verifier stats

```
parsed=7 repaired_ranges=0 duplicate_phases=0 filled_missing=0 skipped_lines=0 output_lines=7
```

### kizomba_drills raw Gemma draft

```
P1: intro (0s-23s, beat: moderate) — Drill: test the pulse with tiny shoulder bounces while staying compact. 23s.
P2-P2: main (23s-112s, beat: clear) — Drill: focus on weight transfer during a steady walk-step. 89s.
P3: peak (112s-117s, beat: clear) — Drill: use more expressive leading variety. 5s.
P4-P6: main (117s-248s, beat: clear) — Drill: same walk-step as P2, but now add subtle hip styling once the basic feels automatic. 131s.
P7: instrumental (248s-258s, beat: clear) — Drill: reduce travel and keep a small pulse in the body. 10s.
P8-P9: main (258s-357s, beat: clear) — Drill: maintain a steady walk-step following the bass line. 99s.
P10: outro (357s-373s, beat: clear) — Drill: slow the pace and return to minimal movement. 16s.
```

### describe_transitions

```
Transitions table — 9 label boundaries
======================================
 #  time   from              →  to                from→to beat   from→to energy
----------------------------------------------------------------------------------------
 1    23.4s  intro             →  main              moderate → clear      medium → low/medium
 2   112.0s  main              →  peak                 clear → clear      low/medium → medium
 3   117.4s  peak              →  main                 clear → clear      medium → high/medium
 4   176.8s  main              →  main                 clear → clear      high/medium → high  
 5   203.7s  main              →  main                 clear → clear        high → high/medium
 6   247.5s  main              →  instrumental         clear → clear      high/medium → low   
 7   258.3s  instrumental      →  main                 clear → clear         low → medium
 8   279.9s  main              →  main                 clear → clear      medium → high/medium
 9   356.8s  main              →  outro                clear → clear      high/medium → low
```

### kizomba_transitions (verified)

```
T1: 23s [intro → main, beat: moderate → clear] — when the bass kicks in, walk-step the basic on the first clear bass hit.
T2: 112s [main → peak, beat: clear → clear] — commit to the new energy, travel more, and add intention.
T3: 117s [peak → main, beat: clear → clear] — settle back, breathe, and return to the basic.
T4: 177s [main → main, beat: clear → clear] — as the energy lifts and the percussion thickens, travel a little more with more intention.
T5: 204s [main → main, beat: clear → clear] — as the energy settles and the texture thins, keep the basic and hold a steady frame.
T6: 248s [main → instrumental, beat: clear → clear] — keep your basic going steadily through this instrumental section.
T7: 258s [instrumental → main, beat: clear → clear] — keep your basic going steadily as the main section returns.
T8: 280s [main → main, beat: clear → clear] — as the energy lifts and the percussion thickens, travel a little more with more intention.
T9: 357s [main → outro, beat: clear → clear] — as the energy fades and the percussion thins, contract your movement, slow the basic, and prepare to close.
```

### kizomba_transitions verifier stats

```
parsed=9 boundaries_matched=9 boundaries_invented=0 boundaries_missing_filled=0 skipped_lines=0 output_lines=9 retried=0 retry_succeeded=0
```

### kizomba_tutor (polished)

```
P1: 0s-23s, intro [beat: moderate] — feel the bass through your feet; stay compact and test the rhythm with small, subtle weight shifts.
P2: 23s-112s, main ×9 [beat: clear] — establish your foundation; use the steady pulse to practice consistent, grounded walking steps.
P3: 112s-117s, peak [beat: clear] — an emotional high point; use the clear pulse to add more intention and presence to your connection.
P4: 117s-177s, main ×5 [beat: clear] — returning to the groove; re-establish your basic and focus on smooth, rhythmic weight transfers.
P5: 177s-204s, main ×2 [beat: clear] — sustaining the energy; keep your frame stable while following the steady pulse.
P6: 204s-248s, main ×3 [beat: clear] — sustaining the flow; use your breath to stay relaxed as the pulse guides your movement.
P7: 248s-258s, instrumental [beat: clear] — a moment to reset; reduce your travel and maintain a small, steady pulse in the body.
P8: 258s-280s, main ×3 [beat: clear] — returning to the rhythm; reconnect with your partner and use the clear pulse to walk evenly.
P9: 280s-357s, main ×5 [beat: clear] — closing the main theme; begin to contract your movements to prepare for the finish.
P10: 357s-373s, outro [beat: clear] — the song is ending; let the dance conclude gently with minimal, smooth movements.
```

### unified timeline (phases + transitions)

```
P1: 0s-23s, intro [beat: moderate] — feel the bass through your feet; stay compact and test the rhythm with small, subtle weight shifts.
T1: 23s [intro → main, beat: moderate → clear] — when the bass kicks in, walk-step the basic on the first clear bass hit.
P2: 23s-112s, main ×9 [beat: clear] — establish your foundation; use the steady pulse to practice consistent, grounded walking steps.
T2: 112s [main → peak, beat: clear → clear] — commit to the new energy, travel more, and add intention.
P3: 112s-117s, peak [beat: clear] — an emotional high point; use the clear pulse to add more intention and presence to your connection.
T3: 117s [peak → main, beat: clear → clear] — settle back, breathe, and return to the basic.
P4: 117s-177s, main ×5 [beat: clear] — returning to the groove; re-establish your basic and focus on smooth, rhythmic weight transfers.
T4: 177s [main → main, beat: clear → clear] — as the energy lifts and the percussion thickens, travel a little more with more intention.
P5: 177s-204s, main ×2 [beat: clear] — sustaining the energy; keep your frame stable while following the steady pulse.
T5: 204s [main → main, beat: clear → clear] — as the energy settles and the texture thins, keep the basic and hold a steady frame.
P6: 204s-248s, main ×3 [beat: clear] — sustaining the flow; use your breath to stay relaxed as the pulse guides your movement.
T6: 248s [main → instrumental, beat: clear → clear] — keep your basic going steadily through this instrumental section.
P7: 248s-258s, instrumental [beat: clear] — a moment to reset; reduce your travel and maintain a small, steady pulse in the body.
T7: 258s [instrumental → main, beat: clear → clear] — keep your basic going steadily as the main section returns.
P8: 258s-280s, main ×3 [beat: clear] — returning to the rhythm; reconnect with your partner and use the clear pulse to walk evenly.
T8: 280s [main → main, beat: clear → clear] — as the energy lifts and the percussion thickens, travel a little more with more intention.
P9: 280s-357s, main ×5 [beat: clear] — closing the main theme; begin to contract your movements to prepare for the finish.
T9: 357s [main → outro, beat: clear → clear] — as the energy fades and the percussion thins, contract your movement, slow the basic, and prepare to close.
P10: 357s-373s, outro [beat: clear] — the song is ending; let the dance conclude gently with minimal, smooth movements.
```

## eval_set: Filomena_Maricoa_-_Teu_Toque_Official_Video

```
source=eval_set | file=Filomena_Maricoa_-_Teu_Toque_Official_Video [sKbWzD0mt6I].mp3
  tempo=92.3 BPM | beats=316 | sections=18 | vocal_env=yes
    intro       0.0s-  11.7s  beat_clarity=0.37
    main       11.7s-  22.0s  beat_clarity=0.47
    main       22.0s-  32.3s  beat_clarity=0.47
    main       32.3s-  48.5s  beat_clarity=0.31
    main       48.5s-  59.4s  beat_clarity=0.41
    main       59.4s-  69.7s  beat_clarity=0.36
    main       69.7s-  79.7s  beat_clarity=0.40
    main       79.7s-  90.4s  beat_clarity=0.31
    main       90.4s- 100.7s  beat_clarity=0.52
    main      100.7s- 111.0s  beat_clarity=0.45
    main      111.0s- 121.3s  beat_clarity=0.49
    main      121.3s- 131.3s  beat_clarity=0.38
    main      131.3s- 147.7s  beat_clarity=0.42
    break     147.7s- 159.2s  beat_clarity=0.47
    main      159.2s- 174.9s  beat_clarity=0.46
    main      174.9s- 185.2s  beat_clarity=0.44
    main      185.2s- 195.4s  beat_clarity=0.42
    outro     195.4s- 208.9s  beat_clarity=0.42
```

### listening_guide

```
This track lasts 208.9 seconds with a steady tempo of 92 BPM. The musical journey begins with a quiet intro, moves through several main sections of varying energy, encounters a brief break, and eventually settles into an outro. Rather than a heavy drum kit, the rhythm is driven by melodic and harmonic content, with the bass line carrying the pulse through an unusually low level of percussiveness.

The pulse remains clear throughout most of the track, but the most challenging moment occurs between 148s and 159s during the break. Because the energy drops and the percussiveness is low, the rhythmic grid becomes less obvious, making it easy to lose the connection to the underlying timing. You may also find the syncopated feel in the intro at 0.0s tricky, as the bass pulls on the final beat of the measure. During the break, do not try to find a heavy beat; instead, trust the bass line to maintain the connection.
```

### kizomba_tutor (one-pass)

```
P1: 0s-12s, intro [beat: clear] — Focus on connection and minimal movement; just feel the pulse together.
P2: 12s-59s, main ×4 [beat: clear] — Establishing the foundation; use a steady walk-step and let the bass guide your steps.
P3: 59s-80s, main ×2 [beat: clear] — Sustaining the momentum; keep your weight transfer smooth as the energy climbs.
P4: 80s-121s, main ×4 [beat: clear] — Sustaining the flow; maintain a steady walk and stay connected to the bass.
P5: 121s-148s, main ×2 [beat: clear] — Building the intensity; you can travel a little more as the energy peaks.
P6: 148s-159s, break [beat: clear] — A moment to reset; reduce travel and simply breathe with the bass.
P7: 159s-195s, main ×3 [beat: clear] — Returning to the groove; re-establish the basic walk-step and reconnect with your partner.
P8: 195s-209s, outro [beat: clear] — Closing the dance; slow down and return to minimal movement for a gentle end.
```

### kizomba_drills (verified)

```
P1: intro (0s-12s, beat: clear) — Drill: focus on connection through a close embrace and minimal movement. 12s.
P2-P5: main (12s-148s, beat: clear) — Drill: practice a steady walk-step, letting the bass guide your weight transfer. 30s loop, repeated through the four main phases.
P6: break (148s-159s, beat: clear) — Drill: reduce travel and keep a small pulse in the body to reset. 11s during the break.
P7: main (159s-195s, beat: clear) — Drill: same walk-step as P2-P5, but now add subtle hip styling once the basic feels automatic. 36s.
P8: outro (195s-209s, beat: clear) — Drill: slow the pace and return to minimal movement to end gently. 14s.
```

### kizomba_drills verifier stats

```
parsed=5 repaired_ranges=1 duplicate_phases=0 filled_missing=0 skipped_lines=0 output_lines=5
```

### kizomba_drills raw Gemma draft

```
P1: intro (0s-12s, beat: clear) — Drill: focus on connection through a close embrace and minimal movement. 12s.
P2-P5: main (12s-121s, beat: clear) — Drill: practice a steady walk-step, letting the bass guide your weight transfer. 30s loop, repeated through the four main phases.
P6: break (148s-159s, beat: clear) — Drill: reduce travel and keep a small pulse in the body to reset. 11s during the break.
P7-P8: main (159s-195s, beat: clear) — Drill: same walk-step as P2-P5, but now add subtle hip styling once the basic feels automatic. 36s.
P8: outro (195s-209s, beat: clear) — Drill: slow the pace and return to minimal movement to end gently. 14s.
```

### describe_transitions

```
Transitions table — 7 label boundaries
======================================
 #  time   from              →  to                from→to beat   from→to energy
----------------------------------------------------------------------------------------
 1    11.7s  intro             →  main                 clear → clear         low → medium
 2    59.4s  main              →  main                 clear → clear      medium → high  
 3    79.7s  main              →  main                 clear → clear        high → medium
 4   121.3s  main              →  main                 clear → clear      medium → high  
 5   147.7s  main              →  break                clear → clear        high → low   
 6   159.2s  break             →  main                 clear → clear         low → high/medium
 7   195.4s  main              →  outro                clear → clear      high/medium → low
```

### kizomba_transitions (verified)

```
T1: 12s [intro → main, beat: clear → clear] — when the bass kicks in, walk-step the basic on the first clear bass hit.
T2: 59s [main → main, beat: clear → clear] — as the energy lifts, travel a little more and add intention to your steps.
T3: 80s [main → main, beat: clear → clear] — as the energy settles, keep the basic and hold a steady frame to reconnect.
T4: 121s [main → main, beat: clear → clear] — as the energy lifts, travel a little more and add intention.
T5: 148s [main → break, beat: clear → clear] — as the energy fades and the percussion thins, keep a small pulse in the body, listen, and reset.
T6: 159s [break → main, beat: clear → clear] — when the bass kicks in, walk-step on the first clear bass hit.
T7: 195s [main → outro, beat: clear → clear] — as the energy fades and the percussion thins, contract your movement and slow the basic to prepare to close.
```

### kizomba_transitions verifier stats

```
parsed=7 boundaries_matched=7 boundaries_invented=0 boundaries_missing_filled=0 skipped_lines=0 output_lines=7 retried=0 retry_succeeded=0
```

### kizomba_tutor (polished)

```
P1: 0s-12s, intro [beat: clear] — Find your connection and use the steady pulse to ground your frame.
P2: 12s-59s, main ×4 [beat: clear] — Establish your foundation with a rhythmic walk-step, letting the bass guide your weight transfer.
P3: 59s-80s, main ×2 [beat: clear] — Maintain your momentum by keeping your steps smooth and your connection consistent.
P4: 80s-121s, main ×4 [beat: clear] — Sustain the flow with a steady walk, staying synchronized with the bass.
P5: 121s-148s, main ×2 [beat: clear] — Lean into the energy by allowing for slightly larger steps or more travel.
P6: 148s-159s, break [beat: clear] — Reduce your travel and keep a small pulse in the body to reset before the next phrase.
P7: 159s-195s, main ×3 [beat: clear] — Re-establish your basic walk-step and reconnect deeply with your partner's movement.
P8: 195s-209s, outro [beat: clear] — Wind down the dance by returning to minimal movement and a gentle, shared pulse.
```

### unified timeline (phases + transitions)

```
P1: 0s-12s, intro [beat: clear] — Find your connection and use the steady pulse to ground your frame.
T1: 12s [intro → main, beat: clear → clear] — when the bass kicks in, walk-step the basic on the first clear bass hit.
P2: 12s-59s, main ×4 [beat: clear] — Establish your foundation with a rhythmic walk-step, letting the bass guide your weight transfer.
T2: 59s [main → main, beat: clear → clear] — as the energy lifts, travel a little more and add intention to your steps.
P3: 59s-80s, main ×2 [beat: clear] — Maintain your momentum by keeping your steps smooth and your connection consistent.
T3: 80s [main → main, beat: clear → clear] — as the energy settles, keep the basic and hold a steady frame to reconnect.
P4: 80s-121s, main ×4 [beat: clear] — Sustain the flow with a steady walk, staying synchronized with the bass.
T4: 121s [main → main, beat: clear → clear] — as the energy lifts, travel a little more and add intention.
P5: 121s-148s, main ×2 [beat: clear] — Lean into the energy by allowing for slightly larger steps or more travel.
T5: 148s [main → break, beat: clear → clear] — as the energy fades and the percussion thins, keep a small pulse in the body, listen, and reset.
P6: 148s-159s, break [beat: clear] — Reduce your travel and keep a small pulse in the body to reset before the next phrase.
T6: 159s [break → main, beat: clear → clear] — when the bass kicks in, walk-step on the first clear bass hit.
P7: 159s-195s, main ×3 [beat: clear] — Re-establish your basic walk-step and reconnect deeply with your partner's movement.
T7: 195s [main → outro, beat: clear → clear] — as the energy fades and the percussion thins, contract your movement and slow the basic to prepare to close.
P8: 195s-209s, outro [beat: clear] — Wind down the dance by returning to minimal movement and a gentle, shared pulse.
```

## eval_set: MIKA_MENDES_-_MAGICO_2011

```
source=eval_set | file=MIKA_MENDES_-_MAGICO_2011 [ZM1GnUImrPw].mp3
  tempo=92.3 BPM | beats=353 | sections=21 | vocal_env=yes
    intro       0.0s-  13.0s  beat_clarity=0.35
    short_break   13.0s-  23.6s  beat_clarity=0.47
    short_break   23.6s-  33.6s  beat_clarity=0.36
    main       33.6s-  44.2s  beat_clarity=0.47
    main       44.2s-  54.7s  beat_clarity=0.48
    main       54.7s-  64.9s  beat_clarity=0.49
    break      64.9s-  75.8s  beat_clarity=0.34
    main       75.8s-  92.3s  beat_clarity=0.43
    main       92.3s- 108.1s  beat_clarity=0.33
    main      108.1s- 113.4s  beat_clarity=0.46
    main      113.4s- 124.6s  beat_clarity=0.35
    main      124.6s- 135.2s  beat_clarity=0.44
    break     135.2s- 146.4s  beat_clarity=0.21
    main      146.4s- 156.8s  beat_clarity=0.41
    build     156.8s- 168.1s  beat_clarity=0.39
    peak      168.1s- 174.1s  beat_clarity=0.41
    main      174.1s- 185.3s  beat_clarity=0.41
    main      185.3s- 201.1s  beat_clarity=0.43
    main      201.1s- 212.2s  beat_clarity=0.47
    main      212.2s- 228.1s  beat_clarity=0.36
    outro     228.1s- 237.7s  beat_clarity=0.48
```

### listening_guide

```
This track lasts 237.7 seconds with a tempo of 92 BPM. The musical journey begins with a quiet intro, moves through several main sections and short breaks, builds tension through a developmental phase, reaches an emotional peak, and finally settles into an outro. Rather than a heavy drum presence, the rhythm is unusually light on percussion, meaning the melodic and harmonic content carries the pulse.

The most challenging moments occur during the breaks, specifically around 65s and 135s, where the beat clarity becomes moderate. During these stretches, the rhythmic grid thins out, making the pulse feel less obvious and harder to lock into. You may also find the pulse subtle during the initial intro. When you hit these breaks, do not search for a heavy drum beat; instead, trust the bass line to guide your sense of timing.
```

### kizomba_tutor (one-pass)

```
P1: 0s-13s, intro [beat: clear] — The pulse is easy to find; use this time to settle into a close embrace and feel the steady rhythm together.
P2: 13s-34s, short_break ×2 [beat: clear] — The pulse remains steady; maintain your connection and keep a gentle, consistent walk.
P3: 34s-65s, main ×3 [beat: clear] — This establishing phase is perfect for finding your footing; trust the steady pulse to guide your walk-steps.
P4: 65s-76s, break [beat: moderate] — The pulse is a bit less obvious; stay compact and test the rhythm with small, controlled steps.
P5: 76s-135s, main ×5 [beat: clear] — As you sustain the dance, focus on smooth weight transfers while following the clear bass line.
P6: 135s-146s, break [beat: moderate] — The beat is less prominent; avoid chasing extra percussion and keep your movement small and centered.
P7: 146s-157s, main [beat: clear] — Returning to a steady pulse, re-establish your basic walk and reconnect with your partner.
P8: 157s-168s, build [beat: clear] — The music is pulling you forward; gradually increase your step size and intention.
P9: 168s-174s, peak [beat: clear] — This is the emotional high point; use the clear pulse to add more variety to your movement.
P10: 174s-228s, main ×4 [beat: clear] — As the song winds down, contract your movement and focus on a steady, closing walk.
P11: 228s-238s, outro [beat: clear] — The rhythm is becoming more percussive; let the dance end gently with minimal movement.
```

### kizomba_drills (verified)

```
P1: intro (0s-13s, beat: clear) — Drill: practice a close embrace with minimal movement, focusing on connection. 13s.
P2: short_break (13s-34s, beat: clear) — Drill: maintain a small body pulse while reducing travel. 10.6s.
P3: main (34s-65s, beat: clear) — Drill: practice steady weight transfers through this section. 31s.
P4: break (65s-76s, beat: moderate) — Drill: reduce travel and keep a small pulse in the body to reset. 11s.
P5: main (76s-135s, beat: clear) — Drill: practice steady weight transfers through this section. 59s.
P6: break (135s-146s, beat: moderate) — Drill: reduce travel and keep a small pulse in the body to reset. 11s.
P7: main (146s-157s, beat: clear) — Drill: practice steady weight transfers through this section. 10s.
P8: build (157s-168s, beat: clear) — Drill: practice steady weight transfers through this section. 11s.
P9: peak (168s-174s, beat: clear) — Drill: practice steady weight transfers through this section. 6s.
P10: main (174s-228s, beat: clear) — Drill: practice steady weight transfers through this section. 54s.
P11: outro (228s-238s, beat: clear) — Drill: reduce travel and let the movement wind down. 10s.
```

### kizomba_drills verifier stats

```
parsed=12 repaired_ranges=5 duplicate_phases=0 filled_missing=9 skipped_lines=10 output_lines=11
```

### kizomba_drills raw Gemma draft

```
P1: intro (0s-13s, beat: clear) — Drill: practice a close embrace with minimal movement, focusing on connection. 13s.
P2-P2: short_break (13s-23.6s, beat: clear) — Drill: maintain a small body pulse while reducing travel. 10.6s.
P3-P3: short_break (23.6s-33.6s, beat: clear) — Drill: keep the pulse in your body and reset your frame. 10s.
P4-P6: main (33.6s-64.9s, beat: clear) — Drill: execute a steady walk-step, letting the bass guide your weight transfer. 31.3s loop, repeated through the three main phases.
P7: break (64.9s-75.8s, beat: moderate) — Drill: stay compact with small steps and test the pulse. 10.9s.
P8-P12: main (75.8s-135.2s, beat: clear) — Drill: same walk-step as P4-P6, but add subtle hip styling once the basic feels automatic. 59.4s loop, repeated through the five main phases.
P13: break (135.2s-146.4s, beat: moderate) — Drill: avoid chasing extra percussion by keeping steps small. 11.2s.
P14: main (146.4s-156.8s, beat: clear) — Drill: focus on smooth weight transfers guided by the bass. 10.4s.
P15: build (157s-168.1s, beat: clear) — Drill: gradually increase step size and expression to build tension. 11.1s.
P16: peak (168.1s-174.1s, beat: clear) — Drill: use stronger leading variety and more expression. 6s.
P17-P20: main (174.1s-228.1s, beat: clear) — Drill: keep the energy built during the peak while maintaining a steady walk-step. 54s loop, repeated through the four main phases.
P21: outro (228.1s-237.7s, beat: clear) — Drill: slow the pace and return to minimal movement. 9.6s.
```

### describe_transitions

```
Transitions table — 10 label boundaries
=======================================
 #  time   from              →  to                from→to beat   from→to energy
----------------------------------------------------------------------------------------
 1    13.0s  intro             →  short_break          clear → clear         low → low   
 2    33.6s  short_break       →  main                 clear → clear         low → high/medium
 3    64.9s  main              →  break                clear → moderate   high/medium → medium
 4    75.8s  break             →  main              moderate → clear      medium → high/medium
 5   135.2s  main              →  break                clear → moderate   high/medium → low   
 6   146.4s  break             →  main              moderate → clear         low → low   
 7   156.8s  main              →  build                clear → clear         low → medium
 8   168.1s  build             →  peak                 clear → clear      medium → high  
 9   174.1s  peak              →  main                 clear → clear        high → high/low/medium
10   228.1s  main              →  outro                clear → clear      high/low/medium → low
```

### kizomba_transitions (verified)

```
T1: 13s [intro → short_break, beat: clear → clear] — keep your movement minimal and focus on the connection.
T2: 34s [short_break → main, beat: clear → clear] — as the percussion returns, walk-step the basic on the first clear bass hit.
T3: 65s [main → break, beat: clear → moderate] — as the energy fades, keep a small pulse in the body, listen, and reset.
T4: 76s [break → main, beat: moderate → clear] — walk-step on the first clear bass hit; don't chase the snare, just trust the steady pulse.
T5: 135s [main → break, beat: clear → moderate] — as the energy fades, keep a small pulse in the body, listen, and reset.
T6: 146s [break → main, beat: moderate → clear] — walk-step on the first clear bass hit.
T7: 157s [main → build, beat: clear → clear] — as the music pulls you forward, commit to the new energy and travel more.
T8: 168s [build → peak, beat: clear → clear] — commit to the new energy with stronger expression and more leading variety.
T9: 174s [peak → main, beat: clear → clear] — as the energy settles, breathe and return to the basic.
T10: 228s [main → outro, beat: clear → clear] — as the energy fades, contract your movement and slow the basic to prepare to close.
```

### kizomba_transitions verifier stats

```
parsed=10 boundaries_matched=10 boundaries_invented=0 boundaries_missing_filled=0 skipped_lines=0 output_lines=10 retried=0 retry_succeeded=0
```

### kizomba_tutor (polished)

```
P1: 0s-13s, intro [beat: clear] — Use this steady rhythm to settle into a close embrace and find a shared sense of timing.
P2: 13s-34s, short_break ×2 [beat: clear] — Keep a gentle, consistent walk to maintain your connection through the steady pulse.
P3: 34s-65s, main ×3 [beat: clear] — Focus on finding your footing by using the clear pulse to guide your walking steps.
P4: 65s-76s, break [beat: moderate] — Stay compact and use small, controlled steps to navigate the less obvious rhythm.
P5: 76s-135s, main ×5 [beat: clear] — Focus on smooth weight transfers while following the steady bass line.
P6: 135s-146s, break [beat: moderate] — Avoid chasing extra percussion; keep your movement small, centered, and grounded.
P7: 146s-157s, main [beat: clear] — Re-establish your basic walk and reconnect with your partner as the pulse returns.
P8: 157s-168s, build [beat: clear] — The music is pulling you forward; gradually increase your step size and movement intention.
P9: 168s-174s, peak [beat: clear] — Use the clear pulse to add more variety and expression to your movement.
P10: 174s-228s, main ×4 [beat: clear] — As the song winds down, contract your movement and focus on a steady, grounded walk.
P11: 228s-238s, outro [beat: clear] — Let the dance end gently with minimal movement as the rhythm becomes more percussive.
```

### unified timeline (phases + transitions)

```
P1: 0s-13s, intro [beat: clear] — Use this steady rhythm to settle into a close embrace and find a shared sense of timing.
T1: 13s [intro → short_break, beat: clear → clear] — keep your movement minimal and focus on the connection.
P2: 13s-34s, short_break ×2 [beat: clear] — Keep a gentle, consistent walk to maintain your connection through the steady pulse.
T2: 34s [short_break → main, beat: clear → clear] — as the percussion returns, walk-step the basic on the first clear bass hit.
P3: 34s-65s, main ×3 [beat: clear] — Focus on finding your footing by using the clear pulse to guide your walking steps.
T3: 65s [main → break, beat: clear → moderate] — as the energy fades, keep a small pulse in the body, listen, and reset.
P4: 65s-76s, break [beat: moderate] — Stay compact and use small, controlled steps to navigate the less obvious rhythm.
T4: 76s [break → main, beat: moderate → clear] — walk-step on the first clear bass hit; don't chase the snare, just trust the steady pulse.
P5: 76s-135s, main ×5 [beat: clear] — Focus on smooth weight transfers while following the steady bass line.
T5: 135s [main → break, beat: clear → moderate] — as the energy fades, keep a small pulse in the body, listen, and reset.
P6: 135s-146s, break [beat: moderate] — Avoid chasing extra percussion; keep your movement small, centered, and grounded.
T6: 146s [break → main, beat: moderate → clear] — walk-step on the first clear bass hit.
P7: 146s-157s, main [beat: clear] — Re-establish your basic walk and reconnect with your partner as the pulse returns.
T7: 157s [main → build, beat: clear → clear] — as the music pulls you forward, commit to the new energy and travel more.
P8: 157s-168s, build [beat: clear] — The music is pulling you forward; gradually increase your step size and movement intention.
T8: 168s [build → peak, beat: clear → clear] — commit to the new energy with stronger expression and more leading variety.
P9: 168s-174s, peak [beat: clear] — Use the clear pulse to add more variety and expression to your movement.
T9: 174s [peak → main, beat: clear → clear] — as the energy settles, breathe and return to the basic.
P10: 174s-228s, main ×4 [beat: clear] — As the song winds down, contract your movement and focus on a steady, grounded walk.
T10: 228s [main → outro, beat: clear → clear] — as the energy fades, contract your movement and slow the basic to prepare to close.
P11: 228s-238s, outro [beat: clear] — Let the dance end gently with minimal movement as the rhythm becomes more percussive.
```

## eval_set: Tony_Pirata_Lydia_Laprade_Filomena_Maricoa_-_Teu_Toque

```
source=eval_set | file=Tony_Pirata_Lydia_Laprade_Filomena_Maricoa_-_Teu_Toque [B0l0VHVSBTQ].mp3
  tempo=92.3 BPM | beats=325 | sections=18 | vocal_env=yes
    intro       0.0s-  17.9s  beat_clarity=0.50
    main       17.9s-  33.7s  beat_clarity=0.49
    main       33.7s-  44.4s  beat_clarity=0.46
    main       44.4s-  55.4s  beat_clarity=0.44
    main       55.4s-  65.7s  beat_clarity=0.35
    main       65.7s-  70.8s  beat_clarity=0.41
    main       70.8s-  81.2s  beat_clarity=0.31
    main       81.2s-  91.5s  beat_clarity=0.44
    main       91.5s- 107.0s  beat_clarity=0.43
    main      107.0s- 112.1s  beat_clarity=0.49
    main      112.1s- 127.3s  beat_clarity=0.42
    main      127.3s- 138.2s  beat_clarity=0.38
    break     138.2s- 149.0s  beat_clarity=0.41
    main      149.0s- 165.0s  beat_clarity=0.47
    main      165.0s- 180.5s  beat_clarity=0.38
    main      180.5s- 190.8s  beat_clarity=0.42
    main      190.8s- 196.0s  beat_clarity=0.49
    outro     196.0s- 213.8s  beat_clarity=0.25
```

### listening_guide

```
This track lasts 213.8 seconds with a tempo of 92 BPM. It follows a structural arc that begins with a medium-energy intro, moves through several main sections of varying energy, hits a low-energy break, and eventually settles into a low-energy outro. Rather than a heavy drum kit, the rhythm is drum-light, with the melodic and harmonic content carrying the pulse through a smooth, steady flow.

The hardest moment to maintain your connection to the rhythm will be during the outro starting at 196.0 seconds. While the beat remains clear for most of the song, the clarity becomes only moderate here, and the pulse thins out significantly as the energy drops. You may find it difficult to anchor your timing as the rhythmic density decreases toward the end. During this final stretch, focus on feeling the underlying pulse to stay connected to the music.
```

### kizomba_tutor (one-pass)

```
P1: 0s-18s, intro [beat: clear] — Find your connection in a close embrace and simply feel the steady pulse together.
P2: 18s-55s, main ×3 [beat: clear] — As we begin establishing the rhythm, use a steady walk-step and let the bass guide your movement.
P3: 55s-71s, main ×2 [beat: clear] — Energy is rising, so feel more intentional with your weight transfers while maintaining a smooth walk.
P4: 71s-112s, main ×4 [beat: clear] — Sustain the momentum by traveling a little more, trusting that clear, steady pulse.
P5: 112s-138s, main ×2 [beat: clear] — This high-energy peak is a great time to increase your movement intention as the pulse stays solid.
P6: 138s-149s, break [beat: clear] — The music shifts; reduce your travel and use this moment to reset and breathe.
P7: 149s-196s, main ×4 [beat: clear] — We are returning to the groove, so re-establish your basic walk and reconnect with your partner.
P8: 196s-214s, outro [beat: moderate] — As the song winds down, stay compact and test the pulse with small, gentle weight shifts.
```

### kizomba_drills (verified)

```
P1: intro (0s-18s, beat: clear) — Drill: maintain a close embrace and feel the pulse through the bass. 18s.
P2-P5: main (18s-138s, beat: clear) — Drill: practice a steady walk-step focusing on weight transfer. 53s loop, repeated through the main phases.
P6: break (138s-149s, beat: clear) — Drill: reduce travel and keep a small pulse in the body. 41s.
P7: main (149s-196s, beat: clear) — Drill: same walk-step as P2-P5, but now add subtle hip styling once the basic feels automatic. 26s.
P8: outro (196s-214s, beat: moderate) — Drill: reduce travel and let the movement wind down. 18s.
```

### kizomba_drills verifier stats

```
parsed=7 repaired_ranges=1 duplicate_phases=0 filled_missing=1 skipped_lines=3 output_lines=5
```

### kizomba_drills raw Gemma draft

```
P1: intro (0s-18s, beat: clear) — Drill: maintain a close embrace and feel the pulse through the bass. 18s.
P2-P5: main (18s-71s, beat: clear) — Drill: practice a steady walk-step focusing on weight transfer. 53s loop, repeated through the main phases.
P6: break (71s-112s, beat: clear) — Drill: reduce travel and keep a small pulse in the body. 41s.
P7-P8: main (112s-138s, beat: clear) — Drill: same walk-step as P2-P5, but now add subtle hip styling once the basic feels automatic. 26s.
P9: break (138s-149s, beat: clear) — Drill: shrink the dance and reset your connection. 11s.
P10-P12: main (149s-196s, beat: clear) — Drill: same walk-step as P2-P5, but now focus on a half-time feel by slowing your walk. 47s.
P13: outro (196s-214s, beat: moderate) — Drill: keep steps small and test the pulse to stay compact. 18s.
```

### describe_transitions

```
Transitions table — 7 label boundaries
======================================
 #  time   from              →  to                from→to beat   from→to energy
----------------------------------------------------------------------------------------
 1    17.9s  intro             →  main                 clear → clear      medium → medium
 2    55.4s  main              →  main                 clear → clear      medium → high  
 3    70.8s  main              →  main                 clear → clear        high → medium
 4   112.1s  main              →  main                 clear → clear      medium → high  
 5   138.2s  main              →  break                clear → clear        high → low   
 6   149.0s  break             →  main                 clear → clear         low → high/medium
 7   196.0s  main              →  outro                clear → moderate   high/medium → low
```

### kizomba_transitions (verified)

```
T1: 18s [intro → main, beat: clear → clear] — walk-step the basic on the first clear bass hit as the percussion returns.
T2: 55s [main → main, beat: clear → clear] — travel a little more and add intention as the bass line gains density.
T3: 71s [main → main, beat: clear → clear] — keep the basic and hold a steady frame as the energy settles.
T4: 112s [main → main, beat: clear → clear] — travel a little more and add intention as the energy lifts.
T5: 138s [main → break, beat: clear → clear] — keep a small pulse in the body, listen, and reset as the energy fades and the percussion thins.
T6: 149s [break → main, beat: clear → clear] — walk-step on the first clear bass hit as the percussion returns.
T7: 196s [main → outro, beat: clear → moderate] — contract movement, slow the basic, and prepare to close as the energy fades and the percussion thins.
```

### kizomba_transitions verifier stats

```
parsed=7 boundaries_matched=7 boundaries_invented=0 boundaries_missing_filled=0 skipped_lines=0 output_lines=7 retried=0 retry_succeeded=0
```

### kizomba_tutor (polished)

```
P1: 0s-18s, intro [beat: clear] — Establish your connection in a close embrace and find the steady pulse together.
P2: 18s-55s, main ×3 [beat: clear] — Use a steady walk-step to ground your movement, letting the bass guide your weight transfers.
P3: 55s-71s, main ×2 [beat: clear] — As the energy rises, make your steps more intentional while maintaining a smooth, flowing walk.
P4: 71s-112s, main ×4 [beat: clear] — Sustain your momentum by increasing your travel, trusting the clear and steady pulse.
P5: 112s-138s, main ×2 [beat: clear] — During this peak, increase your movement intention and keep your steps sharp and rhythmic.
P6: 138s-149s, break [beat: clear] — The music shifts; reduce your travel and keep a small pulse in the body to prepare for the return.
P7: 149s-196s, main ×4 [beat: clear] — Re-establish your basic walk and reconnect with your partner to rejoin the groove.
P8: 196s-214s, outro [beat: moderate] — As the song winds down, stay compact and use small, gentle weight shifts to follow the pulse.
```

### unified timeline (phases + transitions)

```
P1: 0s-18s, intro [beat: clear] — Establish your connection in a close embrace and find the steady pulse together.
T1: 18s [intro → main, beat: clear → clear] — walk-step the basic on the first clear bass hit as the percussion returns.
P2: 18s-55s, main ×3 [beat: clear] — Use a steady walk-step to ground your movement, letting the bass guide your weight transfers.
T2: 55s [main → main, beat: clear → clear] — travel a little more and add intention as the bass line gains density.
P3: 55s-71s, main ×2 [beat: clear] — As the energy rises, make your steps more intentional while maintaining a smooth, flowing walk.
T3: 71s [main → main, beat: clear → clear] — keep the basic and hold a steady frame as the energy settles.
P4: 71s-112s, main ×4 [beat: clear] — Sustain your momentum by increasing your travel, trusting the clear and steady pulse.
T4: 112s [main → main, beat: clear → clear] — travel a little more and add intention as the energy lifts.
P5: 112s-138s, main ×2 [beat: clear] — During this peak, increase your movement intention and keep your steps sharp and rhythmic.
T5: 138s [main → break, beat: clear → clear] — keep a small pulse in the body, listen, and reset as the energy fades and the percussion thins.
P6: 138s-149s, break [beat: clear] — The music shifts; reduce your travel and keep a small pulse in the body to prepare for the return.
T6: 149s [break → main, beat: clear → clear] — walk-step on the first clear bass hit as the percussion returns.
P7: 149s-196s, main ×4 [beat: clear] — Re-establish your basic walk and reconnect with your partner to rejoin the groove.
T7: 196s [main → outro, beat: clear → moderate] — contract movement, slow the basic, and prepare to close as the energy fades and the percussion thins.
P8: 196s-214s, outro [beat: moderate] — As the song winds down, stay compact and use small, gentle weight shifts to follow the pulse.
```

## extended_set: Calema_Dilsinho_-_Leva_Tudo

```
source=extended_set | file=Calema_Dilsinho_-_Leva_Tudo [AHplh9CpILE].mp3
  tempo=86.1 BPM | beats=279 | sections=16 | vocal_env=yes
    intro       0.0s-  12.0s  beat_clarity=0.45
    main       12.0s-  29.0s  beat_clarity=0.54
    main       29.0s-  34.6s  beat_clarity=0.53
    build      34.6s-  45.3s  beat_clarity=0.53
    peak       45.3s-  62.4s  beat_clarity=0.41
    main       62.4s-  73.2s  beat_clarity=0.41
    main       73.2s-  79.3s  beat_clarity=0.44
    main       79.3s-  96.6s  beat_clarity=0.41
    main       96.6s- 107.8s  beat_clarity=0.42
    main      107.8s- 125.2s  beat_clarity=0.31
    main      125.2s- 130.8s  beat_clarity=0.49
    main      130.8s- 147.9s  beat_clarity=0.26
    main      147.9s- 160.1s  beat_clarity=0.34
    main      160.1s- 171.3s  beat_clarity=0.29
    main      171.3s- 182.4s  beat_clarity=0.37
    outro     182.4s- 199.7s  beat_clarity=0.32
```

### listening_guide

```
This track lasts 199.7 seconds with a steady tempo of 86 BPM. The musical journey begins with a quiet intro, transitions into a main section, builds tension, and reaches a peak before moving through extended main sections toward a gentle outro. Throughout most of the song, the pulse is carried by a clear percussive grid, though the energy fluctuates significantly as the song progresses.

The most challenging period for maintaining the pulse occurs during the final stages of the track, specifically from 148s to 182s, where the beat clarity becomes moderate. During this high-energy stretch, the percussion thins out and the rhythmic definition becomes less obvious compared to the earlier, clearer sections. You may find the pulse becomes harder to lock onto as the clarity dips. When you reach this point, focus on the underlying pulse and trust the bass line to guide your sense of time.
```

### kizomba_tutor (one-pass)

```
P1: 0s-12s, intro [beat: clear] — The pulse is easy to find; stay close in an embrace and just feel the connection.
P2: 12s-35s, main ×2 [beat: clear] — This is establishing the groove; trust the steady pulse to guide your walk-steps.
P3: 35s-45s, build [beat: clear] — The music is pulling you forward; gradually increase your step size and expression.
P4: 45s-62s, peak [beat: clear] — This is the emotional high point; use the clear pulse to add more variety to your lead.
P5: 62s-148s, main ×7 [beat: clear] — This is sustaining the energy; keep a steady walk-step and let the bass guide your weight transfer.
P6: 148s-182s, main ×3 [beat: moderate] — As we approach the end, stay compact and test the pulse with small, controlled steps.
P7: 182s-200s, outro [beat: moderate] — The song is winding down; reduce your travel and let the dance end gently.
```

### kizomba_drills (verified)

```
P1: intro (0s-12s, beat: clear) — Drill: maintain a close embrace and find the pulse through the bass. 12s.
P2: main (12s-35s, beat: clear) — Drill: practice a steady walk-step focusing on weight transfer. 22.6s.
P3: build (35s-45s, beat: clear) — Drill: practice steady weight transfers through this section. 11s.
P4: peak (45s-62s, beat: clear) — Drill: practice steady weight transfers through this section. 17s.
P5: main (62s-148s, beat: clear) — Drill: practice steady weight transfers through this section. 85s.
P6: main (148s-182s, beat: moderate) — Drill: stay compact and test the pulse with small steps. 34s.
P7: outro (182s-200s, beat: moderate) — Drill: reduce travel and let the movement wind down. 17s.
```

### kizomba_drills verifier stats

```
parsed=5 repaired_ranges=3 duplicate_phases=0 filled_missing=5 skipped_lines=3 output_lines=7
```

### kizomba_drills raw Gemma draft

```
P1: intro (0s-12s, beat: clear) — Drill: maintain a close embrace and find the pulse through the bass. 12s.
P2-P3: main (12s-34.6s, beat: clear) — Drill: practice a steady walk-step focusing on weight transfer. 22.6s.
P4: build (34.6s-45.3s, beat: clear) — Drill: gradually increase step size to build tension. 10.7s.
P5: peak (45.3s-62.4s, beat: clear) — Drill: use more varied leading and expression in your frame. 17.1s.
P6-P15: main (62.4s-182.4s, beat: clear/moderate) — Drill: same walk-step as P2-P3, but now add subtle hip styling once the basic feels automatic. 120s.
P16: outro (182.4s-199.7s, beat: moderate) — Drill: slow the pace and return to minimal movement. 17.3s.
```

### describe_transitions

```
Transitions table — 6 label boundaries
======================================
 #  time   from              →  to                from→to beat   from→to energy
----------------------------------------------------------------------------------------
 1    12.0s  intro             →  main                 clear → clear         low → medium
 2    34.6s  main              →  build                clear → clear      medium → medium
 3    45.3s  build             →  peak                 clear → clear      medium → medium
 4    62.4s  peak              →  main                 clear → clear      medium → high/low/medium
 5   147.9s  main              →  main                 clear → moderate   high/low/medium → high  
 6   182.4s  main              →  outro             moderate → moderate     high → low
```

### kizomba_transitions (verified)

```
T1: 12s [intro → main, beat: clear → clear] — as the percussion returns, walk-step the basic on the first clear bass hit.
T2: 35s [main → build, beat: clear → clear] — commit to the new energy, travel more, and add intention.
T3: 45s [build → peak, beat: clear → clear] — commit to the new energy, travel more, and add intention.
T4: 62s [peak → main, beat: clear → clear] — settle back, breathe, and return to the basic.
T5: 148s [main → main, beat: clear → moderate] — as the energy shifts, travel a little more and add intention; since the beat becomes less obvious, shrink your basic to small weight shifts.
T6: 182s [main → outro, beat: moderate → moderate] — as the energy fades and the percussion thins, contract your movement, slow the basic, and prepare to close.
```

### kizomba_transitions verifier stats

```
parsed=6 boundaries_matched=6 boundaries_invented=0 boundaries_missing_filled=0 skipped_lines=0 output_lines=6 retried=0 retry_succeeded=0
```

### kizomba_tutor (polished)

```
P1: 0s-12s, intro [beat: clear] — Find the steady rhythm early; maintain a close embrace and focus on feeling the connection through your frame.
P2: 12s-35s, main ×2 [beat: clear] — Establish your groove here; use the consistent pulse to guide smooth, grounded walk-steps.
P3: 35s-45s, build [beat: clear] — The energy is rising; gradually increase your step length and allow your movement to become more expansive.
P4: 45s-62s, peak [beat: clear] — This is the emotional peak; use the strong pulse to introduce more rhythmic variety into your lead and follow.
P5: 62s-148s, main ×7 [beat: clear] — Sustain the energy by keeping a steady walking pattern, letting the bass drive your weight transfers.
P6: 148s-182s, main ×3 [beat: moderate] — As the texture shifts, stay compact and use small, controlled steps to stay synchronized with the pulse.
P7: 182s-200s, outro [beat: moderate] — The song is winding down; reduce your travel and let the movement settle into a gentle finish.
```

### unified timeline (phases + transitions)

```
P1: 0s-12s, intro [beat: clear] — Find the steady rhythm early; maintain a close embrace and focus on feeling the connection through your frame.
T1: 12s [intro → main, beat: clear → clear] — as the percussion returns, walk-step the basic on the first clear bass hit.
P2: 12s-35s, main ×2 [beat: clear] — Establish your groove here; use the consistent pulse to guide smooth, grounded walk-steps.
T2: 35s [main → build, beat: clear → clear] — commit to the new energy, travel more, and add intention.
P3: 35s-45s, build [beat: clear] — The energy is rising; gradually increase your step length and allow your movement to become more expansive.
T3: 45s [build → peak, beat: clear → clear] — commit to the new energy, travel more, and add intention.
P4: 45s-62s, peak [beat: clear] — This is the emotional peak; use the strong pulse to introduce more rhythmic variety into your lead and follow.
T4: 62s [peak → main, beat: clear → clear] — settle back, breathe, and return to the basic.
P5: 62s-148s, main ×7 [beat: clear] — Sustain the energy by keeping a steady walking pattern, letting the bass drive your weight transfers.
T5: 148s [main → main, beat: clear → moderate] — as the energy shifts, travel a little more and add intention; since the beat becomes less obvious, shrink your basic to small weight shifts.
P6: 148s-182s, main ×3 [beat: moderate] — As the texture shifts, stay compact and use small, controlled steps to stay synchronized with the pulse.
T6: 182s [main → outro, beat: moderate → moderate] — as the energy fades and the percussion thins, contract your movement, slow the basic, and prepare to close.
P7: 182s-200s, outro [beat: moderate] — The song is winding down; reduce your travel and let the movement settle into a gentle finish.
```

## extended_set: Calo_Pascoal_-_Titiriti.wmv

```
source=extended_set | file=Calo_Pascoal_-_Titiriti.wmv [r6nwALqxPko].mp3
  tempo=89.1 BPM | beats=381 | sections=21 | vocal_env=yes
    intro       0.0s-  32.9s  beat_clarity=0.44
    main       32.9s-  43.8s  beat_clarity=0.55
    main       43.8s-  54.8s  beat_clarity=0.58
    main       54.8s-  65.7s  beat_clarity=0.38
    main       65.7s-  81.9s  beat_clarity=0.53
    main       81.9s-  92.8s  beat_clarity=0.54
    main       92.8s-  98.4s  beat_clarity=0.59
    main       98.4s- 109.3s  beat_clarity=0.43
    main      109.3s- 119.9s  beat_clarity=0.55
    main      119.9s- 136.6s  beat_clarity=0.51
    main      136.6s- 142.0s  beat_clarity=0.59
    main      142.0s- 152.9s  beat_clarity=0.40
    main      152.9s- 163.7s  beat_clarity=0.54
    break     163.7s- 180.9s  beat_clarity=0.37
    peak      180.9s- 191.8s  beat_clarity=0.48
    main      191.8s- 202.7s  beat_clarity=0.39
    main      202.7s- 213.6s  beat_clarity=0.28
    main      213.6s- 219.8s  beat_clarity=0.49
    main      219.8s- 230.7s  beat_clarity=0.52
    main      230.7s- 241.6s  beat_clarity=0.50
    outro     241.6s- 267.5s  beat_clarity=0.28
```

### listening_guide

```
This track lasts 267.5 seconds with a tempo of 89 BPM. The musical journey begins with a low-energy intro, moves into an extended main section, transitions into a brief break, reaches an emotional peak, and eventually settles into a low-energy outro. Throughout most of the song, the pulse is clear and driven by the bass line, providing a steady foundation for the music's progression.

The most challenging moment occurs during the outro starting at 242 seconds, where the beat clarity shifts from clear to moderate. You may find it harder to lock into the pulse here as the percussiveness thins out significantly. Another moment to watch is the break at 164 seconds; while the beat remains clear, the energy drops, requiring more focused listening to maintain the connection. As you reach the end of the track, focus on the smooth pulse and let the bass guide your sense of timing.
```

### kizomba_tutor (one-pass)

```
P1: 0s-33s, intro [beat: clear] — The pulse is easy to follow; focus on a close embrace and small weight shifts to feel the connection.
P2: 33s-164s, main ×12 [beat: clear] — Establishing the rhythm; trust the steady pulse to guide a smooth walk-step and let the bass drive your movement.
P3: 164s-181s, break [beat: clear] — The pulse remains easy to hear; use this time to reset your frame and breathe before the energy climbs.
P4: 181s-192s, peak [beat: clear] — The pulse is very clear; use this emotional high point to travel more and add more expression to your lead.
P5: 192s-242s, main ×5 [beat: clear] — Returning to the rhythm; re-establish your basic walk-step and find your steady connection again.
P6: 242s-267s, outro [beat: moderate] — The pulse is a bit less distinct; stay compact and reduce your travel to let the dance end gently.
```

### kizomba_drills (verified)

```
P1: intro (0s-33s, beat: clear) — Drill: practice a close embrace with minimal movement, just feeling the pulse together. 33s.
P2: main (33s-164s, beat: clear) — Drill: maintain a steady walk-step, letting the bass guide your weight transfer. 30s loop, repeated through the main phases.
P3: break (164s-181s, beat: clear) — Drill: reduce travel and keep a small pulse in the body to reset. 17s.
P4: peak (181s-192s, beat: clear) — Drill: practice steady weight transfers through this section. 11s.
P5: main (192s-242s, beat: clear) — Drill: practice steady weight transfers through this section. 50s.
P6: outro (242s-267s, beat: moderate) — Drill: reduce travel and let the movement wind down. 26s.
```

### kizomba_drills verifier stats

```
parsed=6 repaired_ranges=2 duplicate_phases=0 filled_missing=4 skipped_lines=4 output_lines=6
```

### kizomba_drills raw Gemma draft

```
P1: intro (0s–33s, beat: clear) — Drill: practice a close embrace with minimal movement, just feeling the pulse together. 33s.
P2-P13: main (33s–164s, beat: clear) — Drill: maintain a steady walk-step, letting the bass guide your weight transfer. 30s loop, repeated through the main phases.
P14: break (164s–181s, beat: clear) — Drill: reduce travel and keep a small pulse in the body while listening to the silence. 17s.
P15: peak (181s–192s, beat: clear) — Drill: use stronger saídas and more expression in your frame. 11s.
P16-P20: main (192s–242s, beat: clear) — Drill: same walk-step as P2-P13, but now add subtle hip styling once the basic feels automatic. 30s loop, repeated through the main phases.
P21: outro (242s–267s, beat: moderate) — Drill: keep steps small and stay compact to end the dance gently. 25s.
```

### describe_transitions

```
Transitions table — 5 label boundaries
======================================
 #  time   from              →  to                from→to beat   from→to energy
----------------------------------------------------------------------------------------
 1    32.9s  intro             →  main                 clear → clear         low → high/medium
 2   163.7s  main              →  break                clear → clear      high/medium → medium
 3   180.9s  break             →  peak                 clear → clear      medium → high  
 4   191.8s  peak              →  main                 clear → clear        high → high/medium
 5   241.6s  main              →  outro                clear → moderate   high/medium → low
```

### kizomba_transitions (verified)

```
T1: 33s [intro → main, beat: clear → clear] — when the bass kicks in, walk-step the basic and follow the steady pulse.
T2: 164s [main → break, beat: clear → clear] — as the energy fades, keep a small pulse in the body, listen, and reset.
T3: 181s [break → peak, beat: clear → clear] — walk-step on the first clear bass hit and commit to the new energy with more intention.
T4: 192s [peak → main, beat: clear → clear] — settle back, breathe, and return to a steady, sustaining walk-step.
T5: 242s [main → outro, beat: clear → moderate] — as the energy fades and the percussion thins, contract your movement and slow the basic to prepare to close.
```

### kizomba_transitions verifier stats

```
parsed=5 boundaries_matched=5 boundaries_invented=0 boundaries_missing_filled=0 skipped_lines=0 output_lines=5 retried=0 retry_succeeded=0
```

### kizomba_tutor (polished)

```
P1: 0s-33s, intro [beat: clear] — Use this steady pulse to find your connection; focus on a close embrace and small, rhythmic weight shifts.
P2: 33s-164s, main ×12 [beat: clear] — Use the consistent rhythm to guide a smooth walk-step, letting the bass drive your movement through the floor.
P3: 164s-181s, break [beat: clear] — Keep a small pulse in the body and reduce your travel to reset your frame before the energy climbs.
P4: 181s-192s, peak [beat: clear] — With the pulse so distinct, use this high point to increase your travel and add more expression to your lead.
P5: 192s-242s, main ×5 [beat: clear] — Re-establish your basic walk-step and find your steady connection to the rhythm once more.
P6: 242s-267s, outro [beat: moderate] — As the pulse softens, stay compact and avoid chasing extra percussion to let the dance end gently.
```

### unified timeline (phases + transitions)

```
P1: 0s-33s, intro [beat: clear] — Use this steady pulse to find your connection; focus on a close embrace and small, rhythmic weight shifts.
T1: 33s [intro → main, beat: clear → clear] — when the bass kicks in, walk-step the basic and follow the steady pulse.
P2: 33s-164s, main ×12 [beat: clear] — Use the consistent rhythm to guide a smooth walk-step, letting the bass drive your movement through the floor.
T2: 164s [main → break, beat: clear → clear] — as the energy fades, keep a small pulse in the body, listen, and reset.
P3: 164s-181s, break [beat: clear] — Keep a small pulse in the body and reduce your travel to reset your frame before the energy climbs.
T3: 181s [break → peak, beat: clear → clear] — walk-step on the first clear bass hit and commit to the new energy with more intention.
P4: 181s-192s, peak [beat: clear] — With the pulse so distinct, use this high point to increase your travel and add more expression to your lead.
T4: 192s [peak → main, beat: clear → clear] — settle back, breathe, and return to a steady, sustaining walk-step.
P5: 192s-242s, main ×5 [beat: clear] — Re-establish your basic walk-step and find your steady connection to the rhythm once more.
T5: 242s [main → outro, beat: clear → moderate] — as the energy fades and the percussion thins, contract your movement and slow the basic to prepare to close.
P6: 242s-267s, outro [beat: moderate] — As the pulse softens, stay compact and avoid chasing extra percussion to let the dance end gently.
```

## extended_set: Daniel_Santacruz_-_Lento_-_Kizomba_Official_Video_HD

```
source=extended_set | file=Daniel_Santacruz_-_Lento_-_Kizomba_Official_Video_HD [cpYPPXf63a4].mp3
  tempo=89.1 BPM | beats=366 | sections=24 | vocal_env=yes
    intro       0.0s-  12.8s  beat_clarity=0.32
    break      12.8s-  24.4s  beat_clarity=0.47
    break      24.4s-  42.8s  beat_clarity=0.33
    short_break   42.8s-  53.8s  beat_clarity=0.54
    main       53.8s-  59.2s  beat_clarity=0.52
    main       59.2s-  75.6s  beat_clarity=0.49
    main       75.6s-  86.5s  beat_clarity=0.46
    main       86.5s-  97.4s  beat_clarity=0.50
    build      97.4s- 108.9s  beat_clarity=0.45
    peak      108.9s- 120.6s  beat_clarity=0.35
    main      120.6s- 132.1s  beat_clarity=0.49
    main      132.1s- 143.1s  beat_clarity=0.43
    main      143.1s- 153.6s  beat_clarity=0.48
    main      153.6s- 166.3s  beat_clarity=0.44
    main      166.3s- 177.5s  beat_clarity=0.48
    main      177.5s- 183.3s  beat_clarity=0.41
    main      183.3s- 194.2s  beat_clarity=0.40
    main      194.2s- 200.8s  beat_clarity=0.37
    main      200.8s- 211.6s  beat_clarity=0.40
    main      211.6s- 222.5s  beat_clarity=0.47
    main      222.5s- 233.8s  beat_clarity=0.41
    main      233.8s- 243.9s  beat_clarity=0.37
    main      243.9s- 254.9s  beat_clarity=0.45
    outro     254.9s- 266.1s  beat_clarity=0.31
```

### listening_guide

```
This track lasts 266.1 seconds with a tempo of 89 BPM. The musical journey begins with an intro, moves through several breaks, and transitions into a main section that builds toward a high-energy peak before winding down through an outro. Rather than a heavy drum kit, the pulse is carried primarily by melodic and harmonic content, giving the track an unusually drum-light feel where the bass line provides the rhythmic foundation.

The most challenging moment occurs during the peak between 109s and 121s, where the beat becomes moderate in clarity. Because the percussiveness is so low during this high-energy phase, the pulse is felt more through the texture than through a sharp percussive grid, making it easy to lose the connection. You may also find the intro and outro sections tricky as the beat clarity is only moderate. During the peak, don't chase the louder melodic elements; instead, feel the underlying pulse.
```

### kizomba_tutor (one-pass)

```
P1: 0s-13s, intro [beat: moderate] — The pulse is felt rather than heard; stay compact and test the rhythm with tiny weight shifts.
P2: 13s-43s, break ×2 [beat: clear] — The pulse is steady; reset your frame and use the clear rhythm to find a smooth walking step.
P3: 43s-54s, short_break [beat: clear] — Use this brief moment to breathe and re-establish your connection before the energy shifts.
P4: 54s-97s, main ×4 [beat: clear] — Establishing the flow; trust the steady pulse to guide a consistent, easy walk.
P5: 97s-109s, build [beat: clear] — Energy is climbing; increase your intention and start to travel a little more.
P6: 109s-121s, peak [beat: moderate] — The pulse is subtle; avoid chasing extra percussion and keep your movements centered.
P7: 121s-177s, main ×5 [beat: clear] — Returning to the basics; re-establish your connection and focus on smooth weight transfers.
P8: 177s-201s, main ×3 [beat: clear] — Sustaining the movement; keep your walk steady and focus on maintaining a solid frame.
P9: 201s-222s, main ×2 [beat: clear] — Sustaining the energy; focus on your breath as you continue the steady walk.
P10: 222s-255s, main ×3 [beat: clear] — Closing the dance; movement should contract and become more intimate as we wind down.
P11: 255s-266s, outro [beat: moderate] — The pulse is moderate; stay compact and let the dance end gently.
```

### kizomba_drills (verified)

```
P1: intro (0s-13s, beat: moderate) — Drill: test the pulse with tiny shoulder bounces to find the bass. 13s.
P2: break (13s-43s, beat: clear) — Drill: reduce travel and keep a small pulse in the body. 30s.
P3: short_break (43s-54s, beat: clear) — Drill: reduce travel and keep a small pulse in the body to reset. 11s.
P4: main (54s-97s, beat: clear) — Drill: practice steady weight transfers through this section. 44s.
P5: build (97s-109s, beat: clear) — Drill: practice steady weight transfers through this section. 12s.
P6: peak (109s-121s, beat: moderate) — Drill: stay compact and test the pulse with small steps. 12s.
P7: main (121s-177s, beat: clear) — Drill: practice steady weight transfers through this section. 57s.
P8: main (177s-201s, beat: clear) — Drill: practice steady weight transfers through this section. 23s.
P9: main (201s-222s, beat: clear) — Drill: practice steady weight transfers through this section. 22s.
P10: main (222s-255s, beat: clear) — Drill: practice steady weight transfers through this section. 32s.
P11: outro (255s-266s, beat: moderate) — Drill: reduce travel and let the movement wind down. 11s.
```

### kizomba_drills verifier stats

```
parsed=10 repaired_ranges=7 duplicate_phases=0 filled_missing=9 skipped_lines=8 output_lines=11
```

### kizomba_drills raw Gemma draft

```
P1: intro (0s-13s, beat: moderate) — Drill: test the pulse with tiny shoulder bounces to find the bass. 13s.
P2-P3: break (13s-43s, beat: clear) — Drill: reduce travel and keep a small pulse in the body. 30s.
P4: short_break (43s-54s, beat: clear) — Drill: reset your frame and reconnect with your partner. 11s.
P5-P8: main (54s-201s, beat: clear) — Drill: focus on smooth weight transfers following the bass line. 147s loop, repeated through the four main phases.
P9: build (97s-109s, beat: clear) — Drill: gradually increase step size and expression. 12s.
P10: peak (109s-121s, beat: moderate) — Drill: stay compact with small steps to avoid chasing the extra percussion. 12s.
P11-P15: main (121s-177s, beat: clear) — Drill: same walk-step as P5-P8, but add subtle hip styling once the basic feels automatic. 56s.
P16: main (177s-201s, beat: clear) — Drill: focus on steady walk-steps. 24s.
P17-P23: main (201s-255s, beat: clear) — Drill: keep the energy you built from the peak and focus on the bass. 54s.
P24: outro (255s-266s, beat: moderate) — Drill: slow the pace and return to minimal movement. 11s.
```

### describe_transitions

```
Transitions table — 10 label boundaries
=======================================
 #  time   from              →  to                from→to beat   from→to energy
----------------------------------------------------------------------------------------
 1    12.8s  intro             →  break             moderate → clear         low → low   
 2    42.8s  break             →  short_break          clear → clear         low → low   
 3    53.8s  short_break       →  main                 clear → clear         low → medium
 4    97.4s  main              →  build                clear → clear      medium → medium
 5   108.9s  build             →  peak                 clear → moderate   medium → high  
 6   120.6s  peak              →  main              moderate → clear        high → medium
 7   177.5s  main              →  main                 clear → clear      medium → high  
 8   200.8s  main              →  main                 clear → clear        high → medium
 9   222.5s  main              →  main                 clear → clear      medium → high/medium
10   254.9s  main              →  outro                clear → moderate   high/medium → medium
```

### kizomba_transitions (verified)

```
T1: 13s [intro → break, beat: moderate → clear] — keep a small pulse in the body, listen, and reset.
T2: 43s [break → short_break, beat: clear → clear] — keep a small pulse in the body, listen, and reset.
T3: 54s [short_break → main, beat: clear → clear] — when the bass kicks in, walk-step the basic on the first clear hit.
T4: 97s [main → build, beat: clear → clear] — as the texture shifts, commit to the new energy and travel more.
T5: 109s [build → peak, beat: clear → moderate] — as the energy rises, commit to the new energy and travel more; since the pulse is less obvious, shrink your steps to a small weight shift.
T6: 121s [peak → main, beat: moderate → clear] — as the energy settles, settle back, breathe, and return to the basic.
T7: 177s [main → main, beat: clear → clear] — as the percussion thickens, travel a little more and add intention.
T8: 201s [main → main, beat: clear → clear] — as the energy lifts, travel a little more and add intention.
T9: 222s [main → main, beat: clear → clear] — as the energy shifts, travel a little more and add intention.
T10: 255s [main → outro, beat: clear → moderate] — as the energy fades and the percussion thins, contract your movement, slow the basic, and prepare to close.
```

### kizomba_transitions verifier stats

```
parsed=10 boundaries_matched=10 boundaries_invented=0 boundaries_missing_filled=0 skipped_lines=0 output_lines=10 retried=0 retry_succeeded=0
```

### kizomba_tutor (polished)

```
P1: 0s-13s, intro [beat: moderate] — The pulse is subtle; stay compact and test the rhythm with tiny weight shifts.
P2: 13s-43s, break ×2 [beat: clear] — Use this steady rhythm to reset your frame and find a smooth, grounded walking step.
P3: 43s-54s, short_break [beat: clear] — Reduce your travel and re-establish your connection before the energy shifts.
P4: 54s-97s, main ×4 [beat: clear] — Focus on flow; use the steady pulse to guide a consistent, easy walk.
P5: 97s-109s, build [beat: clear] — Energy is climbing; increase your intention and allow for slightly more travel.
P6: 109s-121s, peak [beat: moderate] — The pulse is subtle; avoid chasing extra percussion and keep your movements centered.
P7: 121s-177s, main ×5 [beat: clear] — Return to basics; re-establish your connection and focus on smooth weight transfers.
P8: 177s-201s, main ×3 [beat: clear] — Sustain the movement by keeping your walk steady and your frame solid.
P9: 201s-222s, main ×2 [beat: clear] — Maintain the energy by focusing on your breath and a steady walking rhythm.
P10: 222s-255s, main ×3 [beat: clear] — As the dance winds down, let your movements contract and become more intimate.
P11: 255s-266s, outro [beat: moderate] — The pulse is soft; stay compact and let the dance end gently.
```

### unified timeline (phases + transitions)

```
P1: 0s-13s, intro [beat: moderate] — The pulse is subtle; stay compact and test the rhythm with tiny weight shifts.
T1: 13s [intro → break, beat: moderate → clear] — keep a small pulse in the body, listen, and reset.
P2: 13s-43s, break ×2 [beat: clear] — Use this steady rhythm to reset your frame and find a smooth, grounded walking step.
T2: 43s [break → short_break, beat: clear → clear] — keep a small pulse in the body, listen, and reset.
P3: 43s-54s, short_break [beat: clear] — Reduce your travel and re-establish your connection before the energy shifts.
T3: 54s [short_break → main, beat: clear → clear] — when the bass kicks in, walk-step the basic on the first clear hit.
P4: 54s-97s, main ×4 [beat: clear] — Focus on flow; use the steady pulse to guide a consistent, easy walk.
T4: 97s [main → build, beat: clear → clear] — as the texture shifts, commit to the new energy and travel more.
P5: 97s-109s, build [beat: clear] — Energy is climbing; increase your intention and allow for slightly more travel.
T5: 109s [build → peak, beat: clear → moderate] — as the energy rises, commit to the new energy and travel more; since the pulse is less obvious, shrink your steps to a small weight shift.
P6: 109s-121s, peak [beat: moderate] — The pulse is subtle; avoid chasing extra percussion and keep your movements centered.
T6: 121s [peak → main, beat: moderate → clear] — as the energy settles, settle back, breathe, and return to the basic.
P7: 121s-177s, main ×5 [beat: clear] — Return to basics; re-establish your connection and focus on smooth weight transfers.
T7: 177s [main → main, beat: clear → clear] — as the percussion thickens, travel a little more and add intention.
P8: 177s-201s, main ×3 [beat: clear] — Sustain the movement by keeping your walk steady and your frame solid.
T8: 201s [main → main, beat: clear → clear] — as the energy lifts, travel a little more and add intention.
P9: 201s-222s, main ×2 [beat: clear] — Maintain the energy by focusing on your breath and a steady walking rhythm.
T9: 222s [main → main, beat: clear → clear] — as the energy shifts, travel a little more and add intention.
P10: 222s-255s, main ×3 [beat: clear] — As the dance winds down, let your movements contract and become more intimate.
T10: 255s [main → outro, beat: clear → moderate] — as the energy fades and the percussion thins, contract your movement, slow the basic, and prepare to close.
P11: 255s-266s, outro [beat: moderate] — The pulse is soft; stay compact and let the dance end gently.
```

## extended_set: Isabelle_Felicien_-_Soha_Mil_Pasos_Kizomba_remix

```
source=extended_set | file=Isabelle_Felicien_-_Soha_Mil_Pasos_Kizomba_remix [dm_TzKprOls].mp3
  tempo=89.1 BPM | beats=216 | sections=13 | vocal_env=yes
    intro       0.0s-  22.0s  beat_clarity=0.46
    main       22.0s-  32.9s  beat_clarity=0.48
    main       32.9s-  43.8s  beat_clarity=0.43
    main       43.8s-  49.2s  beat_clarity=0.43
    main       49.2s-  60.1s  beat_clarity=0.48
    main       60.1s-  71.1s  beat_clarity=0.44
    main       71.1s-  82.0s  beat_clarity=0.41
    main       82.0s-  87.4s  beat_clarity=0.45
    main       87.4s-  98.3s  beat_clarity=0.45
    main       98.3s- 109.2s  beat_clarity=0.43
    main      109.2s- 120.1s  beat_clarity=0.54
    main      120.1s- 131.1s  beat_clarity=0.42
    outro     131.1s- 146.9s  beat_clarity=0.49
```

### listening_guide

```
This track lasts 146.9 seconds with a tempo of 89 BPM. The musical journey begins with an intro, transitions into a main section that fluctuates in energy, and concludes with an outro. Throughout the entire duration, the pulse is carried by a clear, steady beat that remains easy to follow, providing a consistent foundation for the music's progression.

The beat remains clear throughout the track, so your primary challenge is sustaining attention through the varying energy levels rather than recovering from a loss of pulse. The most significant shift occurs between 120.1s and 131.1s, where the energy drops and the percussion thins out significantly. During this moment, the rhythm takes on a half-time feel, making the pulse feel more subtle. In this section, trust the bass line to guide your sense of timing.
```

### kizomba_tutor (one-pass)

```
P1: 0s-22s, intro [beat: clear] — The pulse is easy to follow; stay in a close embrace and just feel the steady rhythm together.
P2: 22s-49s, main ×3 [beat: clear] — Establishing the groove; trust the steady pulse to guide a smooth walk-step and follow the bass line.
P3: 49s-131s, main ×8 [beat: clear] — Sustaining the movement; keep your weight transfers steady and use the clear beat to travel a little more.
P4: 131s-147s, outro [beat: clear] — Closing the dance; return to minimal movement and let the feeling end gently as the song winds down.
```

### kizomba_drills (verified)

```
P1: intro (0s-22s, beat: clear) — Drill: maintain a close embrace and feel the pulse through the bass. 22s.
P2-P3: main (22s-131s, beat: clear) — Drill: practice a steady walk-step, focusing on weight transfer. 27s.
P4: outro (131s-147s, beat: clear) — Drill: reduce travel and let the movement wind down. 16s.
```

### kizomba_drills verifier stats

```
parsed=8 repaired_ranges=1 duplicate_phases=0 filled_missing=1 skipped_lines=6 output_lines=3
```

### kizomba_drills raw Gemma draft

```
P1: intro (0s-22s, beat: clear) — Drill: maintain a close embrace and feel the pulse through the bass. 22s.

P2-P4: main (22s-49s, beat: clear) — Drill: practice a steady walk-step, focusing on weight transfer. 27s.

P5: main (49s-60s, beat: clear) — Drill: slow your walk to match the half-time feel. 11s.

P6-P8: main (60s-87s, beat: clear) — Drill: return to the steady walk-step, matching the bass. 27s.

P9: main (87s-98s, beat: clear) — Drill: practice a three-step pattern with a light pause. 11s.

P10-P11: main (98s-120s, beat: clear) — Drill: same walk-step as P2-P4, but now add subtle hip styling once the basic feels automatic. 22s.

P12: main (120s-131s, beat: clear) — Drill: practice a half-time feel by stepping only on the alternating pulses. 11s.

P13: outro (131s-147s, beat: clear) — Drill: slow the pace and return to minimal movement. 16s.
```

### describe_transitions

```
Transitions table — 3 label boundaries
======================================
 #  time   from              →  to                from→to beat   from→to energy
----------------------------------------------------------------------------------------
 1    22.0s  intro             →  main                 clear → clear      medium → high/medium
 2    49.2s  main              →  main                 clear → clear      high/medium → high/low/medium
 3   131.1s  main              →  outro                clear → clear      high/low/medium → medium
```

### kizomba_transitions (verified)

```
T1: 22s [intro → main, beat: clear → clear] — walk-step the basic on the first clear bass hit as the percussion returns.
T2: 49s [main → main, beat: clear → clear] — as the energy shifts, travel a little more and add intention to your movement.
T3: 131s [main → outro, beat: clear → clear] — as the energy fades and the percussion thins, contract your movement, slow the basic, and prepare to close.
```

### kizomba_transitions verifier stats

```
parsed=3 boundaries_matched=3 boundaries_invented=0 boundaries_missing_filled=0 skipped_lines=0 output_lines=3 retried=0 retry_succeeded=0
```

### kizomba_tutor (polished)

```
P1: 0s-22s, intro [beat: clear] — Use this steady rhythm to find your connection; maintain a soft, close embrace and settle into a shared pulse.
P2: 22s-49s, main ×3 [beat: clear] — Focus on the groove; use the consistent beat to guide smooth, grounded walk-steps that follow the bass.
P3: 49s-131s, main ×8 [beat: clear] — Maintain momentum; keep your weight transfers rhythmic and use the clear pulse to explore slightly larger steps or more intentional travel.
P4: 131s-147s, outro [beat: clear] — Wind down the energy; transition into smaller, more subtle movements and let the dance conclude with a gentle, shared connection.
```

### unified timeline (phases + transitions)

```
P1: 0s-22s, intro [beat: clear] — Use this steady rhythm to find your connection; maintain a soft, close embrace and settle into a shared pulse.
T1: 22s [intro → main, beat: clear → clear] — walk-step the basic on the first clear bass hit as the percussion returns.
P2: 22s-49s, main ×3 [beat: clear] — Focus on the groove; use the consistent beat to guide smooth, grounded walk-steps that follow the bass.
T2: 49s [main → main, beat: clear → clear] — as the energy shifts, travel a little more and add intention to your movement.
P3: 49s-131s, main ×8 [beat: clear] — Maintain momentum; keep your weight transfers rhythmic and use the clear pulse to explore slightly larger steps or more intentional travel.
T3: 131s [main → outro, beat: clear → clear] — as the energy fades and the percussion thins, contract your movement, slow the basic, and prepare to close.
P4: 131s-147s, outro [beat: clear] — Wind down the energy; transition into smaller, more subtle movements and let the dance conclude with a gentle, shared connection.
```

## extended_set: Normal

```
source=extended_set | file=Normal [SR3aKEKo4tY].mp3
  tempo=89.1 BPM | beats=295 | sections=18 | vocal_env=yes
    intro       0.0s-  10.9s  beat_clarity=0.32
    short_break   10.9s-  16.4s  beat_clarity=0.33
    main       16.4s-  32.2s  beat_clarity=0.37
    main       32.2s-  37.5s  beat_clarity=0.47
    main       37.5s-  48.2s  beat_clarity=0.43
    main       48.2s-  54.2s  beat_clarity=0.46
    main       54.2s-  70.0s  beat_clarity=0.45
    main       70.0s-  80.8s  beat_clarity=0.15
    main       80.8s-  96.9s  beat_clarity=0.36
    build      96.9s- 108.2s  beat_clarity=0.46
    peak      108.2s- 118.9s  beat_clarity=0.41
    main      118.9s- 130.2s  beat_clarity=0.24
    main      130.2s- 140.8s  beat_clarity=0.44
    main      140.8s- 162.8s  beat_clarity=0.25
    main      162.8s- 173.5s  beat_clarity=0.32
    main      173.5s- 184.2s  beat_clarity=0.39
    main      184.2s- 194.8s  beat_clarity=0.37
    outro     194.8s- 206.6s  beat_clarity=0.44
```

### listening_guide

```
This 206.6-second track moves at 89 BPM, following a journey from a quiet intro through a series of main sections, a short break, a build, and a high-energy peak before settling into an outro. The rhythm is drum-light, with melodic and harmonic content carrying the pulse rather than a heavy percussive grid. You will find the pulse is felt primarily through the bass line throughout the song's progression.

The most challenging moment occurs between 70.0s and 80.8s, where the beat becomes moderate and less obvious, making the pulse harder to lock onto. You may also find the transition at 11s difficult as the music shifts into a short break with a syncopated feel where the bass pulls on the final beat of the measure. To navigate these shifts, trust the bass line to guide you through the break.
```

### kizomba_tutor (one-pass)

```
P1: 0s-11s, intro [beat: moderate] — Stay compact and test the pulse with small weight shifts to find the connection.
P2: 11s-16s, short_break [beat: moderate] — The bass pulls on the final beat of the measure; lean into it with a weight transfer.
P3: 16s-97s, main ×7 [beat: clear] — The pulse is steady; establish your walk-step and let the bass guide your movement.
P4: 97s-108s, build [beat: clear] — The music is pulling you forward; gradually increase your step size and expression.
P5: 108s-119s, peak [beat: clear] — Trust the steady pulse to drive stronger leading variety and more emotion.
P6: 119s-195s, main ×6 [beat: moderate] — Returning to a calmer state; re-establish the basic and keep your steps even.
P7: 195s-207s, outro [beat: clear] — The pulse is easy to follow; slow down and let the dance end gently.
```

### kizomba_drills (verified)

```
P1: intro (0s-11s, beat: moderate) — Drill: keep movement minimal and test the pulse with small steps. 11s.
P2: short_break (11s-16s, beat: moderate) — Drill: reduce travel and keep a small pulse in the body. 5s.
P3: main (16s-97s, beat: clear) — Drill: practice a steady walk-step focusing on weight transfer. 81s loop, repeated through the four main phases.
P4: build (97s-108s, beat: clear) — Drill: practice steady weight transfers through this section. 11s.
P5: peak (108s-119s, beat: clear) — Drill: practice steady weight transfers through this section. 11s.
P6: main (119s-195s, beat: moderate) — Drill: stay compact and test the pulse with small steps. 76s.
P7: outro (195s-207s, beat: clear) — Drill: reduce travel and let the movement wind down. 12s.
```

### kizomba_drills verifier stats

```
parsed=7 repaired_ranges=2 duplicate_phases=0 filled_missing=4 skipped_lines=4 output_lines=7
```

### kizomba_drills raw Gemma draft

```
P1: intro (0s-11s, beat: moderate) — Drill: keep movement minimal and test the pulse with small steps. 11s.
P2: short_break (11s-16s, beat: moderate) — Drill: reduce travel and keep a small pulse in the body. 5s.
P3-P9: main (16s-97s, beat: clear) — Drill: practice a steady walk-step focusing on weight transfer. 81s loop, repeated through the four main phases.
P10: build (97s-108s, beat: clear) — Drill: gradually increase step size and expression. 11s.
P11: peak (108s-119s, beat: clear) — Drill: lead with stronger saídas and more variety. 11s.
P12-P17: main (119s-195s, beat: moderate) — Drill: same walk-step as P3-P9, but now add subtle hip styling once the basic feels automatic. 76s loop, repeated through the four main phases.
P18: outro (195s-207s, beat: clear) — Drill: slow the pace and return to minimal movement. 12s.
```

### describe_transitions

```
Transitions table — 6 label boundaries
======================================
 #  time   from              →  to                from→to beat   from→to energy
----------------------------------------------------------------------------------------
 1    10.9s  intro             →  short_break       moderate → moderate      low → low   
 2    16.4s  short_break       →  main              moderate → clear         low → high/medium
 3    96.9s  main              →  build                clear → clear      high/medium → high  
 4   108.2s  build             →  peak                 clear → clear        high → high  
 5   118.9s  peak              →  main                 clear → moderate     high → low/medium
 6   194.8s  main              →  outro             moderate → clear      low/medium → low
```

### kizomba_transitions (verified)

```
T1: 11s [intro → short_break, beat: moderate → moderate] — keep a small pulse in the body, listen, and reset.
T2: 16s [short_break → main, beat: moderate → clear] — walk-step on the first clear bass hit as the percussion returns.
T3: 97s [main → build, beat: clear → clear] — commit to the new energy and travel more as the music pulls you forward.
T4: 108s [build → peak, beat: clear → clear] — add more intention and variety to your leading as the energy reaches its highest point.
T5: 119s [peak → main, beat: clear → moderate] — settle back, breathe, and return to the basic as the energy fades.
T6: 195s [main → outro, beat: moderate → clear] — contract your movement and slow the basic to prepare to close as the energy fades.
```

### kizomba_transitions verifier stats

```
parsed=6 boundaries_matched=6 boundaries_invented=0 boundaries_missing_filled=0 skipped_lines=0 output_lines=6 retried=0 retry_succeeded=0
```

### kizomba_tutor (polished)

```
P1: 0s-11s, intro [beat: moderate] — Stay compact and use small weight shifts to find the rhythm and your partner's connection.
P2: 11s-16s, short_break [beat: moderate] — Use the final bass pull to complete a weight transfer, then reset your frame.
P3: 16s-97s, main ×7 [beat: clear] — Use this steady pulse to establish a consistent walk and let the bass guide your steps.
P4: 97s-108s, build [beat: clear] — The energy is rising; gradually increase your step size and movement expression.
P5: 108s-119s, peak [beat: clear] — Use the strong, steady pulse to drive more intentional movement and connection.
P6: 119s-195s, main ×6 [beat: moderate] — As the energy settles, return to a smaller step size and maintain a steady, even pace.
P7: 195s-207s, outro [beat: clear] — Follow the clear pulse to gradually slow your steps and let the dance conclude gently.
```

### unified timeline (phases + transitions)

```
P1: 0s-11s, intro [beat: moderate] — Stay compact and use small weight shifts to find the rhythm and your partner's connection.
T1: 11s [intro → short_break, beat: moderate → moderate] — keep a small pulse in the body, listen, and reset.
P2: 11s-16s, short_break [beat: moderate] — Use the final bass pull to complete a weight transfer, then reset your frame.
T2: 16s [short_break → main, beat: moderate → clear] — walk-step on the first clear bass hit as the percussion returns.
P3: 16s-97s, main ×7 [beat: clear] — Use this steady pulse to establish a consistent walk and let the bass guide your steps.
T3: 97s [main → build, beat: clear → clear] — commit to the new energy and travel more as the music pulls you forward.
P4: 97s-108s, build [beat: clear] — The energy is rising; gradually increase your step size and movement expression.
T4: 108s [build → peak, beat: clear → clear] — add more intention and variety to your leading as the energy reaches its highest point.
P5: 108s-119s, peak [beat: clear] — Use the strong, steady pulse to drive more intentional movement and connection.
T5: 119s [peak → main, beat: clear → moderate] — settle back, breathe, and return to the basic as the energy fades.
P6: 119s-195s, main ×6 [beat: moderate] — As the energy settles, return to a smaller step size and maintain a steady, even pace.
T6: 195s [main → outro, beat: moderate → clear] — contract your movement and slow the basic to prepare to close as the energy fades.
P7: 195s-207s, outro [beat: clear] — Follow the clear pulse to gradually slow your steps and let the dance conclude gently.
```

## extended_set: Tu_Es_um_Erro

```
source=extended_set | file=Tu_Es_um_Erro [5PI109-P-EA].mp3
  tempo=92.3 BPM | beats=374 | sections=21 | vocal_env=yes
    intro       0.0s-  24.6s  beat_clarity=0.17
    main       24.6s-  29.7s  beat_clarity=0.41
    main       29.7s-  40.0s  beat_clarity=0.39
    main       40.0s-  51.3s  beat_clarity=0.42
    main       51.3s-  61.9s  beat_clarity=0.48
    main       61.9s-  72.3s  beat_clarity=0.49
    main       72.3s-  82.6s  beat_clarity=0.49
    main       82.6s-  93.5s  beat_clarity=0.47
    main       93.5s- 103.9s  beat_clarity=0.42
    main      103.9s- 114.9s  beat_clarity=0.20
    main      114.9s- 125.2s  beat_clarity=0.35
    main      125.2s- 135.5s  beat_clarity=0.42
    main      135.5s- 151.0s  beat_clarity=0.45
    main      151.0s- 167.8s  beat_clarity=0.50
    break     167.8s- 183.6s  beat_clarity=0.31
    main      183.6s- 194.2s  beat_clarity=0.49
    main      194.2s- 210.3s  beat_clarity=0.46
    main      210.3s- 220.7s  beat_clarity=0.46
    main      220.7s- 225.9s  beat_clarity=0.48
    main      225.9s- 236.8s  beat_clarity=0.42
    outro     236.8s- 251.8s  beat_clarity=0.44
```

### listening_guide

```
This 251.8-second track moves at a tempo of 92 BPM, following a structural arc that begins with a subtle intro, transitions into an extended main section, moves through a low-energy break, and concludes with a final main phase and a gentle outro. Because the percussiveness is unusually low, you will find that the rhythm is not driven by a heavy drum kit, but rather by melodic and harmonic content carrying the pulse.

The most challenging moment occurs during the intro from 0s to 25s, where the beat is subtle and the pulse is felt rather than heard. You may also find the break between 168s and 184s difficult, as the beat clarity becomes only moderate and the energy drops significantly. During these transitions, the rhythm can feel less defined, making it easy to lose your connection to the underlying timing. When the music thins out or the percussion fades, trust the bass line to guide your sense of the pulse.
```

### kizomba_tutor (one-pass)

```
P1: 0s-25s, intro [beat: subtle] — The pulse is felt rather than heard; keep movement minimal and just find the connection.
P2: 25s-168s, main ×13 [beat: clear] — Establishing the groove; trust the steady pulse at 92 BPM and settle into a smooth walk-step.
P3: 168s-184s, break [beat: moderate] — The beat is moderate; stay compact and test the pulse with small weight shifts.
P4: 184s-210s, main ×2 [beat: clear] — Returning to the rhythm; re-establish your basic walk and reconnect with your partner.
P5: 210s-237s, main ×3 [beat: clear] — Closing the main section; movement should begin to contract as the song winds down.
P6: 237s-252s, outro [beat: clear] — The pulse is clear; let the dance end gently with steady, controlled steps.
```

### kizomba_drills (verified)

```
P1: intro (0s-25s, beat: subtle) — Drill: stand still and mark the pulse with a tiny shoulder bounce to prepare for re-entry. 25s.
P2: main (25s-168s, beat: clear) — Drill: practice a steady walk-step, focusing on smooth weight transfers. 30s loop, repeated through the main phases. 143s.
P3: break (168s-184s, beat: moderate) — Drill: reduce travel and keep a small pulse in the body to reset. 16s.
P4: main (184s-210s, beat: clear) — Drill: practice steady weight transfers through this section. 27s.
P5: main (210s-237s, beat: clear) — Drill: practice steady weight transfers through this section. 26s.
P6: outro (237s-252s, beat: clear) — Drill: reduce travel and let the movement wind down. 15s.
```

### kizomba_drills verifier stats

```
parsed=5 repaired_ranges=2 duplicate_phases=0 filled_missing=4 skipped_lines=3 output_lines=6
```

### kizomba_drills raw Gemma draft

```
P1: intro (0s-25s, beat: subtle) — Drill: stand still and mark the pulse with a tiny shoulder bounce to prepare for re-entry. 25s.
P2-P14: main (25s-168s, beat: clear) — Drill: practice a steady walk-step, focusing on smooth weight transfers. 30s loop, repeated through the main phases. 143s.
P15: break (168s-184s, beat: moderate) — Drill: reduce travel and keep a small pulse in the body to stay compact. 16s.
P16-P20: main (184s-237s, beat: clear) — Drill: same walk-step as P2-P14, but now add subtle hip styling once the basic feels automatic. 30s loop, repeated through the main phases. 53s.
P21: outro (237s-252s, beat: clear) — Drill: slow the pace and return to minimal movement to end gently. 15s.
```

### describe_transitions

```
Transitions table — 5 label boundaries
======================================
 #  time   from              →  to                from→to beat   from→to energy
----------------------------------------------------------------------------------------
 1    24.6s  intro             →  main                subtle → clear         low → high/medium
 2   167.8s  main              →  break                clear → moderate   high/medium → low   
 3   183.6s  break             →  main              moderate → clear         low → high  
 4   210.3s  main              →  main                 clear → clear        high → high/medium
 5   236.8s  main              →  outro                clear → clear      high/medium → medium
```

### kizomba_transitions (verified)

```
T1: 25s [intro → main, beat: subtle → clear] — when the bass kicks in, walk-step the basic on the first clear pulse.
T2: 168s [main → break, beat: clear → moderate] — as the energy fades and the percussion thins, keep a small pulse in the body, listen, and reset.
T3: 184s [break → main, beat: moderate → clear] — when the bass kicks in, walk-step on the first clear bass hit rather than chasing loud percussion.
T4: 210s [main → main, beat: clear → clear] — as the energy shifts, travel a little more and add intention to your movement.
T5: 237s [main → outro, beat: clear → clear] — as the energy fades, contract your movement, slow the basic, and prepare to close.
```

### kizomba_transitions verifier stats

```
parsed=5 boundaries_matched=5 boundaries_invented=0 boundaries_missing_filled=0 skipped_lines=0 output_lines=5 retried=0 retry_succeeded=0
```

### kizomba_tutor (polished)

```
P1: 0s-25s, intro [beat: subtle] — Focus on finding the connection; keep your movement minimal and wait for the rhythm to emerge.
P2: 25s-168s, main ×13 [beat: clear] — Settle into the groove by using the steady pulse to guide a smooth, grounded walk.
P3: 168s-184s, break [beat: moderate] — Avoid chasing extra percussion; stay compact and use small weight shifts to maintain the pulse.
P4: 184s-210s, main ×2 [beat: clear] — Reconnect with your partner and re-establish your basic walking rhythm.
P5: 210s-237s, main ×3 [beat: clear] — Maintain your flow, but begin to contract your movements as the energy winds down.
P6: 237s-252s, outro [beat: clear] — Use the clear pulse to finish with steady, controlled steps and a gentle close.
```

### unified timeline (phases + transitions)

```
P1: 0s-25s, intro [beat: subtle] — Focus on finding the connection; keep your movement minimal and wait for the rhythm to emerge.
T1: 25s [intro → main, beat: subtle → clear] — when the bass kicks in, walk-step the basic on the first clear pulse.
P2: 25s-168s, main ×13 [beat: clear] — Settle into the groove by using the steady pulse to guide a smooth, grounded walk.
T2: 168s [main → break, beat: clear → moderate] — as the energy fades and the percussion thins, keep a small pulse in the body, listen, and reset.
P3: 168s-184s, break [beat: moderate] — Avoid chasing extra percussion; stay compact and use small weight shifts to maintain the pulse.
T3: 184s [break → main, beat: moderate → clear] — when the bass kicks in, walk-step on the first clear bass hit rather than chasing loud percussion.
P4: 184s-210s, main ×2 [beat: clear] — Reconnect with your partner and re-establish your basic walking rhythm.
T4: 210s [main → main, beat: clear → clear] — as the energy shifts, travel a little more and add intention to your movement.
P5: 210s-237s, main ×3 [beat: clear] — Maintain your flow, but begin to contract your movements as the energy winds down.
T5: 237s [main → outro, beat: clear → clear] — as the energy fades, contract your movement, slow the basic, and prepare to close.
P6: 237s-252s, outro [beat: clear] — Use the clear pulse to finish with steady, controlled steps and a gentle close.
```
