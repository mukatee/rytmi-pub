# 09_kizomba batch outputs - model=google/gemma-4-26b-a4b-it

sources: eval_set=11, extended_set=6

## kizomba - rhythm_anatomy (genre intro)

```
Kizomba typically operates within a tempo range of 85–110 BPM in a 4/4 time signature. Rather than relying on a heavy percussive grid, the rhythm is often driven by the bass line, which carries the pulse through melodic or harmonic content. While the underlying pulse remains steady, you may encounter syncopation or emphasis on off-beat intervals. Structurally, a track generally follows a predictable arc, moving from an intro through several main sections, potentially building toward a peak, experiencing a break or moment of stillness, and finally transitioning into an outro.

When dancing, you may encounter various sub-styles. Tarraxinha often features a slower, more grounded pulse with a focus on heavy, rhythmic textures, while Urbankiz frequently introduces more modern, polished production with varied energy levels. Ghetto Zouk tends to emphasize a more melodic, flowing rhythmic character. Use these distinctions in tempo and texture as hints to help you place the specific character of a track as it unfolds.
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
This 252.2-second track runs at a tempo of 83 BPM, which is slower than the typical kizomba range. The musical journey begins with a low-energy intro, moves through several main sections, builds tension into a peak, experiences a sudden low-energy break, and eventually settles into an outro. Because the percussiveness is unusually low, you will find that the melodic and harmonic content carries the rhythm rather than a heavy drum kit.

The primary challenge will be maintaining your connection to the pulse during the intro (0s–20s), where the beat is only moderate and the percussiveness is very low. While the beat remains clear for most of the song, the low percussiveness means the rhythm is felt through the bass rather than heard through sharp percussion. The hardest moment occurs during the break (175s–188s); although the beat is clear, the sudden drop in energy requires intense focus to stay connected. During this transition, trust the bass line to maintain the pulse.
```

### kizomba_tutor (one-pass)

```
P1: 0s-20s, intro [beat: moderate] — The pulse is felt rather than heard; stay compact and test the pulse with small weight shifts.
P2: 20s-90s, main ×6 [beat: clear] — The pulse is easy to follow; settle in by walking the basic and matching the bass.
P3: 90s-107s, build [beat: clear] — The rhythm is steady; build tension by gradually increasing your step size.
P4: 107s-118s, peak [beat: clear] — The beat is very easy to hear; use this emotional high point to travel more and add expression.
P5: 118s-175s, main ×4 [beat: clear] — The pulse is reliable; focus on your frame while maintaining a steady walk-step.
P6: 175s-188s, break [beat: clear] — The beat remains easy to follow; reset your connection and keep a small pulse in the body.
P7: 188s-217s, main ×3 [beat: clear] — The pulse is steady; reconnect with your partner and focus on smooth weight transfers.
P8: 217s-240s, main ×2 [beat: clear] — The beat is clear; as the song winds down, contract your movement and reduce travel.
P9: 240s-252s, outro [beat: clear] — The pulse is easy to track; let the dance end gently with minimal movement.
```

### kizomba_drills (verified)

```
P1: intro (0s-20s, beat: moderate) — Drill: keep steps very small and test the pulse. 20s.
P2: main (20s-90s, beat: clear) — Drill: practice a steady walk-step focusing on weight transfer. 70s loop, repeated through the main phases.
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
P1: intro (0.0s–20.3s, beat: moderate) — Drill: keep steps very small and test the pulse. 20s.
P2-P7: main (20.3s–89.8s, beat: clear) — Drill: practice a steady walk-step focusing on weight transfer. 70s loop, repeated through the main phases.
P8: build (89.8s–106.9s, beat: clear) — Drill: increase step size to build tension. 17s.
P9: peak (106.9s–118.4s, beat: clear) — Drill: practice a three-step pattern with a light pause. 11s.
P10-P13: main (118.4s–175.1s, beat: clear) — Drill: maintain a steady walk-step, following the bass line. 57s loop, repeated through the main phases.
P14: break (175.1s–187.6s, beat: clear) — Drill: reduce travel and keep a small pulse in the body. 13s.
P15-P19: main (187.6s–239.8s, beat: clear) — Drill: same walk-step as P2-P7, but now add subtle hip styling once the basic feels automatic. 52s loop, repeated through the main phases.
P20: outro (239.8s–252.2s, beat: clear) — Drill: slow the pace and return to minimal movement. 12s.
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
T1: 20s [intro → main, beat: moderate → clear] — when the bass kicks in, walk-step the basic with a steady pulse.
T2: 90s [main → build, beat: clear → clear] — as the energy shifts, commit to the new energy and travel more.
T3: 107s [build → peak, beat: clear → clear] — add intention and more expression to your movement as the music reaches its height.
T4: 118s [peak → main, beat: clear → clear] — settle back and return to the basic as the energy levels out.
T5: 175s [main → break, beat: clear → clear] — as the energy fades and the percussion thins, keep a small pulse in the body, listen, and reset.
T6: 188s [break → main, beat: clear → clear] — walk-step on the first clear bass hit; don't chase the percussion that returns loudest.
T7: 217s [main → main, beat: clear → clear] — as the energy settles, keep the basic and hold a steady frame.
T8: 240s [main → outro, beat: clear → clear] — as the energy fades, contract your movement, slow the basic, and prepare to close.
```

### kizomba_transitions verifier stats

```
parsed=8 boundaries_matched=8 boundaries_invented=0 boundaries_missing_filled=0 skipped_lines=0 output_lines=8
```

### kizomba_tutor (polished)

```
P1: 0s-20s, intro [beat: moderate] — The pulse is subtle; stay compact and test the rhythm with small, grounded weight shifts.
P2: 20s-90s, main ×6 [beat: clear] — The pulse is steady; settle into the rhythm by walking the basic and matching the bass.
P3: 90s-107s, build [beat: clear] — The rhythm is driving; build energy by gradually increasing your step size and connection.
P4: 107s-118s, peak [beat: clear] — The beat is prominent; use this high point to travel more and express the emotion.
P5: 118s-175s, main ×4 [beat: clear] — The pulse is reliable; focus on a strong frame while maintaining a steady walk-step.
P6: 175s-188s, break [beat: clear] — The beat remains present; reduce your travel, reset your connection, and keep a small pulse in the body.
P7: 188s-217s, main ×3 [beat: clear] — The pulse is steady; reconnect with your partner and focus on smooth weight transfers.
P8: 217s-240s, main ×2 [beat: clear] — The beat is clear; as the song winds down, contract your movement and reduce travel.
P9: 240s-252s, outro [beat: clear] — The pulse is easy to track; let the dance end gently with minimal, controlled movement.
```

### unified timeline (phases + transitions)

```
P1: 0s-20s, intro [beat: moderate] — The pulse is subtle; stay compact and test the rhythm with small, grounded weight shifts.
T1: 20s [intro → main, beat: moderate → clear] — when the bass kicks in, walk-step the basic with a steady pulse.
P2: 20s-90s, main ×6 [beat: clear] — The pulse is steady; settle into the rhythm by walking the basic and matching the bass.
T2: 90s [main → build, beat: clear → clear] — as the energy shifts, commit to the new energy and travel more.
P3: 90s-107s, build [beat: clear] — The rhythm is driving; build energy by gradually increasing your step size and connection.
T3: 107s [build → peak, beat: clear → clear] — add intention and more expression to your movement as the music reaches its height.
P4: 107s-118s, peak [beat: clear] — The beat is prominent; use this high point to travel more and express the emotion.
T4: 118s [peak → main, beat: clear → clear] — settle back and return to the basic as the energy levels out.
P5: 118s-175s, main ×4 [beat: clear] — The pulse is reliable; focus on a strong frame while maintaining a steady walk-step.
T5: 175s [main → break, beat: clear → clear] — as the energy fades and the percussion thins, keep a small pulse in the body, listen, and reset.
P6: 175s-188s, break [beat: clear] — The beat remains present; reduce your travel, reset your connection, and keep a small pulse in the body.
T6: 188s [break → main, beat: clear → clear] — walk-step on the first clear bass hit; don't chase the percussion that returns loudest.
P7: 188s-217s, main ×3 [beat: clear] — The pulse is steady; reconnect with your partner and focus on smooth weight transfers.
T7: 217s [main → main, beat: clear → clear] — as the energy settles, keep the basic and hold a steady frame.
P8: 217s-240s, main ×2 [beat: clear] — The beat is clear; as the song winds down, contract your movement and reduce travel.
T8: 240s [main → outro, beat: clear → clear] — as the energy fades, contract your movement, slow the basic, and prepare to close.
P9: 240s-252s, outro [beat: clear] — The pulse is easy to track; let the dance end gently with minimal, controlled movement.
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
This 270.6-second track moves at a tempo of 81 BPM, which is slower than the typical range for this style. The musical journey begins with an intro, transitions into an extended main section, moves through a brief break, returns to the main theme, and finally settles into an outro. Because the percussiveness is unusually low, the rhythm is not driven by a heavy drum kit; instead, the pulse is felt through the melodic and harmonic content, with the bass line carrying the primary rhythmic weight.

The most challenging moment occurs during the break from 193s to 205s, where beat clarity becomes moderate and the rhythm shifts toward a half-time feel. You may also find the high-energy peak between 179.2s and 193.3s difficult to navigate, as the beat clarity dips and the percussion thins significantly. During these transitions, the pulse becomes subtle and harder to anchor. When the music thins out or the rhythm shifts, trust the bass line to guide your sense of timing.
```

### kizomba_tutor (one-pass)

```
P1: 0s-15s, intro [beat: clear] — The pulse is steady; focus on connection and matching the bass with minimal movement.
P2: 15s-138s, main ×10 [beat: clear] — Establishing the rhythm; it is safe to trust the pulse and begin a steady walk-step.
P3: 138s-193s, main ×4 [beat: moderate] — Sustaining the energy; stay compact and test the pulse with small steps to avoid chasing the syncopation.
P4: 193s-205s, break [beat: moderate] — A moment to reset; reduce travel and keep a small pulse in the body as the energy shifts.
P5: 205s-252s, main ×5 [beat: clear] — Returning to the flow; the beat is easy to find, so you can re-establish your walk and follow the bass.
P6: 252s-271s, outro [beat: moderate] — Closing the dance; avoid extra movement and keep your steps small as the song winds down.
```

### kizomba_drills (verified)

```
P1: intro (0s-15s, beat: clear) — Drill: match the bass line with a steady weight transfer. 15s.
P2: main (15s-138s, beat: clear) — Drill: practice a smooth walk-step focusing on hip movement. 30s loop, repeated through the ten main phases.
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
P1: intro (0s-15s, beat: clear) — Drill: match the bass line with a steady weight transfer. 15s.
P2-P11: main (15s-138s, beat: clear) — Drill: practice a smooth walk-step focusing on hip movement. 30s loop, repeated through the ten main phases.
P12-P15: main (138s-193s, beat: moderate) — Drill: keep steps small to stay compact with the pulse. 55s.
P16: break (193s-205s, beat: moderate) — Drill: reduce travel and keep a small pulse in the body. 12s.
P17: main (205s-210s, beat: clear) — Drill: same walk-step as P2-P11, but add subtle hip styling once the basic feels automatic. 5s.
P18-P21: main (210s-252s, beat: clear) — Drill: practice the basic walk-step focusing on frame stability. 42s.
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
T1: 15s [intro → main, beat: clear → clear] — when the bass kicks in, walk-step the basic on the first clear pulse.
T2: 138s [main → main, beat: clear → moderate] — as the energy lifts, travel a little more and add intention.
T3: 193s [main → break, beat: moderate → moderate] — as the energy fades and the percussion thins, keep a small pulse in the body, listen, and reset.
T4: 205s [break → main, beat: moderate → clear] — walk-step on the first clear bass hit; don't chase the louder percussion.
T5: 252s [main → outro, beat: clear → moderate] — as the energy fades, contract your movement and slow the basic to prepare to close.
```

### kizomba_transitions verifier stats

```
parsed=5 boundaries_matched=5 boundaries_invented=0 boundaries_missing_filled=0 skipped_lines=0 output_lines=5
```

### kizomba_tutor (polished)

```
P1: 0s-15s, intro [beat: clear] — Use this steady pulse to find your connection and match the bass with gentle, minimal movement.
P2: 15s-138s, main ×10 [beat: clear] — Establish your rhythm by trusting the pulse; a steady walk-step is a great way to ground your movement.
P3: 138s-193s, main ×4 [beat: moderate] — Maintain your energy by staying compact; use small steps to feel the pulse without chasing the syncopation.
P4: 193s-205s, break [beat: moderate] — Use this moment to reset; reduce your travel and keep a small, subtle pulse in your body.
P5: 205s-252s, main ×5 [beat: clear] — Re-enter the flow by re-establishing your walk and letting your steps follow the bass.
P6: 252s-271s, outro [beat: moderate] — Wind down the dance by keeping your steps small and avoiding any unnecessary extra movement.
```

### unified timeline (phases + transitions)

```
P1: 0s-15s, intro [beat: clear] — Use this steady pulse to find your connection and match the bass with gentle, minimal movement.
T1: 15s [intro → main, beat: clear → clear] — when the bass kicks in, walk-step the basic on the first clear pulse.
P2: 15s-138s, main ×10 [beat: clear] — Establish your rhythm by trusting the pulse; a steady walk-step is a great way to ground your movement.
T2: 138s [main → main, beat: clear → moderate] — as the energy lifts, travel a little more and add intention.
P3: 138s-193s, main ×4 [beat: moderate] — Maintain your energy by staying compact; use small steps to feel the pulse without chasing the syncopation.
T3: 193s [main → break, beat: moderate → moderate] — as the energy fades and the percussion thins, keep a small pulse in the body, listen, and reset.
P4: 193s-205s, break [beat: moderate] — Use this moment to reset; reduce your travel and keep a small, subtle pulse in your body.
T4: 205s [break → main, beat: moderate → clear] — walk-step on the first clear bass hit; don't chase the louder percussion.
P5: 205s-252s, main ×5 [beat: clear] — Re-enter the flow by re-establishing your walk and letting your steps follow the bass.
T5: 252s [main → outro, beat: clear → moderate] — as the energy fades, contract your movement and slow the basic to prepare to close.
P6: 252s-271s, outro [beat: moderate] — Wind down the dance by keeping your steps small and avoiding any unnecessary extra movement.
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
This track lasts 314.1 seconds with a tempo of 108 BPM. The musical journey begins with a low-energy intro, transitions into a long, steady main section, moves through instrumental breaks, and builds toward a high-energy peak before settling into a medium-energy outro. Throughout the arc, the pulse is carried primarily by the bass line, providing a clear beat that remains easy to follow.

The pulse remains clear throughout the song, so your main challenge will be sustaining focus through the long stretches of the main section. The most demanding moment occurs during the high-energy peak around 228s to 233s; while the beat remains clear, the rhythm becomes much denser, which can make the underlying pulse feel more complex. During this peak, don't chase the louder percussion; instead, feel the underlying pulse to stay connected to the music.
```

### kizomba_tutor (one-pass)

```
P1: 0s-18s, intro [beat: clear] — Use this slow start to find the pulse; keep movement minimal and focus on connection.
P2: 18s-172s, main ×13 [beat: clear] — Establishing the groove; trust the steady pulse to guide a smooth, consistent walk.
P3: 172s-195s, instrumental ×2 [beat: clear] — Sustaining the energy; keep your weight transfers fluid as the music continues.
P4: 195s-212s, main [beat: clear] — Building momentum; you can begin to travel a little more with your steps.
P5: 212s-228s, instrumental [beat: clear] — High energy arrives; use the strong pulse to add more intention to your movement.
P6: 228s-233s, peak [beat: clear] — The emotional high point; express yourself more freely while staying anchored to the beat.
P7: 233s-265s, main ×3 [beat: clear] — Returning to the basics; re-establish your connection with a steady, grounded walk.
P8: 265s-302s, main ×3 [beat: clear] — Closing the dance; contract your movement and prepare to wind down.
P9: 302s-314s, outro [beat: clear] — Let the dance end gently by returning to small, minimal movements.
```

### kizomba_drills (verified)

```
P1: intro (0s-18s, beat: clear) — Drill: practice a close embrace with minimal movement, just feeling the pulse together. 18s.
P2: main (18s-172s, beat: clear) — Drill: steady walk-step, letting the bass guide your weight transfer. 87.9s loop, repeated through the three main phases.
P3: instrumental (172s-195s, beat: clear) — Drill: practice steady weight transfers through this section. 23s.
P4: main (195s-212s, beat: clear) — Drill: practice steady weight transfers through this section. 17s.
P5: instrumental (212s-228s, beat: clear) — Drill: practice steady weight transfers through this section. 17s.
P6: peak (228s-233s, beat: clear) — Drill: practice steady weight transfers through this section. 5s.
P7: main (233s-265s, beat: clear) — Drill: practice steady weight transfers through this section. 32s.
P8: main (265s-302s, beat: clear) — Drill: practice steady weight transfers through this section. 36s.
P9: outro (302s-314s, beat: clear) — Drill: reduce travel and let the movement wind down. 13s.
```

### kizomba_drills verifier stats

```
parsed=9 repaired_ranges=2 duplicate_phases=0 filled_missing=7 skipped_lines=7 output_lines=9
```

### kizomba_drills raw Gemma draft

```
P1: intro (0s-18s, beat: clear) — Drill: practice a close embrace with minimal movement, just feeling the pulse together. 18s.
P2-P10: main (18s-105.9s, beat: clear) — Drill: steady walk-step, letting the bass guide your weight transfer. 87.9s loop, repeated through the three main phases.
P11: main (105.9s-119.1s, beat: clear) — Drill: lean into the syncopated feel by transferring weight on the bass pull. 13.2s.
P12-P14: main (119.1s-172.5s, beat: clear) — Drill: same walk-step as P2-P10, but now focus on matching the bass line. 53.4s.
P15-P17: instrumental (172.5s-211.6s, beat: clear) — Drill: maintain a smooth pulse with steady walk-steps. 39.1s.
P18-P19: peak (211.6s-232.8s, beat: clear) — Drill: use stronger leading variety and more expression. 21.2s.
P20-P22: main (232.8s-265.2s, beat: clear) — Drill: same walk-step as P2-P10, but add subtle hip styling once the basic feels automatic. 32.4s.
P23-P25: main (265.2s-301.6s, beat: clear) — Drill: lead with a strong step and follow with light steps. 36.4s.
P26: outro (301.6s-314.1s, beat: clear) — Drill: slow the pace and return to minimal movement to close the dance. 12.5s.
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
T1: 18s [intro → main, beat: clear → clear] — when the bass kicks in, walk-step the basic on the first clear hit.
T2: 172s [main → instrumental, beat: clear → clear] — keep your basic going steadily through this medium-energy section.
T3: 195s [instrumental → main, beat: clear → clear] — keep your basic going steadily.
T4: 212s [main → instrumental, beat: clear → clear] — keep your basic going steadily as the energy lifts.
T5: 228s [instrumental → peak, beat: clear → clear] — commit to the new energy, travel more, and add intention.
T6: 233s [peak → main, beat: clear → clear] — as the energy settles, settle back, breathe, and return to the basic.
T7: 265s [main → main, beat: clear → clear] — as the energy settles, keep the basic and hold a steady frame.
T8: 302s [main → outro, beat: clear → clear] — as the energy fades and the percussion thins, contract your movement and slow the basic to prepare to close.
```

### kizomba_transitions verifier stats

```
parsed=8 boundaries_matched=8 boundaries_invented=0 boundaries_missing_filled=0 skipped_lines=0 output_lines=8
```

### kizomba_tutor (polished)

```
P1: 0s-18s, intro [beat: clear] — Find the pulse through small, rhythmic movements; focus on establishing a stable connection.
P2: 18s-172s, main ×13 [beat: clear] — Settle into the groove; use the steady pulse to guide a smooth, consistent walk.
P3: 172s-195s, instrumental ×2 [beat: clear] — Maintain your flow; keep weight transfers fluid and rhythmic.
P4: 195s-212s, main [beat: clear] — Build momentum; try increasing your travel distance with slightly larger steps.
P5: 212s-228s, instrumental [beat: clear] — Energy rises; use the strong pulse to add more intention to your steps.
P6: 228s-233s, peak [beat: clear] — Express yourself more freely while staying anchored to the beat.
P7: 233s-265s, main ×3 [beat: clear] — Re-center your focus; return to a grounded, steady walk.
P8: 265s-302s, main ×3 [beat: clear] — Wind down; contract your movement and reduce your travel.
P9: 302s-314s, outro [beat: clear] — End gently by returning to small, minimal movements.
```

### unified timeline (phases + transitions)

```
P1: 0s-18s, intro [beat: clear] — Find the pulse through small, rhythmic movements; focus on establishing a stable connection.
T1: 18s [intro → main, beat: clear → clear] — when the bass kicks in, walk-step the basic on the first clear hit.
P2: 18s-172s, main ×13 [beat: clear] — Settle into the groove; use the steady pulse to guide a smooth, consistent walk.
T2: 172s [main → instrumental, beat: clear → clear] — keep your basic going steadily through this medium-energy section.
P3: 172s-195s, instrumental ×2 [beat: clear] — Maintain your flow; keep weight transfers fluid and rhythmic.
T3: 195s [instrumental → main, beat: clear → clear] — keep your basic going steadily.
P4: 195s-212s, main [beat: clear] — Build momentum; try increasing your travel distance with slightly larger steps.
T4: 212s [main → instrumental, beat: clear → clear] — keep your basic going steadily as the energy lifts.
P5: 212s-228s, instrumental [beat: clear] — Energy rises; use the strong pulse to add more intention to your steps.
T5: 228s [instrumental → peak, beat: clear → clear] — commit to the new energy, travel more, and add intention.
P6: 228s-233s, peak [beat: clear] — Express yourself more freely while staying anchored to the beat.
T6: 233s [peak → main, beat: clear → clear] — as the energy settles, settle back, breathe, and return to the basic.
P7: 233s-265s, main ×3 [beat: clear] — Re-center your focus; return to a grounded, steady walk.
T7: 265s [main → main, beat: clear → clear] — as the energy settles, keep the basic and hold a steady frame.
P8: 265s-302s, main ×3 [beat: clear] — Wind down; contract your movement and reduce your travel.
T8: 302s [main → outro, beat: clear → clear] — as the energy fades and the percussion thins, contract your movement and slow the basic to prepare to close.
P9: 302s-314s, outro [beat: clear] — End gently by returning to small, minimal movements.
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
This 301.0-second track maintains a steady 92 BPM, moving through an intro, several main sections, a peak, and an outro. Rather than a heavy drum grid, the pulse is carried primarily by the melodic and harmonic content, giving the song an unusually drum-light feel. The journey begins with low energy, builds through various main phases, reaches a high-energy peak around 158s, and eventually settles into a gentle outro.

The greatest challenge lies in maintaining connection when the pulse becomes subtle. You may find it difficult to anchor your timing during the outro starting at 287s, as the beat clarity becomes quite low and the rhythmic density thins out significantly. Additionally, the middle sections present a high density of syncopated notes that can feel cluttered. Because the percussiveness is so low throughout, the pulse is often felt through the bass rather than heard through a sharp strike. During the most subtle moments, trust the bass line to guide your sense of time.
```

### kizomba_tutor (one-pass)

```
P1: 0s-29s, intro [beat: moderate] — Focus on connection and finding the pulse with tiny weight shifts.
P2: 29s-65s, main ×3 [beat: moderate] — This establishing phase is for settling in; test the pulse with small, steady steps.
P3: 65s-158s, main ×8 [beat: moderate] — Sustain the movement by following the bass line and keeping your frame steady.
P4: 158s-165s, peak [beat: moderate] — Use this high energy to add more expression and travel a little more.
P5: 165s-248s, main ×7 [beat: moderate] — Returning to the basic, reconnect with your partner and maintain a consistent walk.
P6: 248s-287s, main ×4 [beat: moderate] — As we approach the end, keep the movement compact and focus on smooth weight transfers.
P7: 287s-301s, outro [beat: subtle] — The pulse is hard to lock onto; make your movement very small and let the dance end gently.
```

### kizomba_drills (verified)

```
P1: intro (0s-29s, beat: moderate) — Drill: maintain a close embrace and feel the pulse together. 29s.
P2-P3: main (29s-158s, beat: moderate) — Drill: steady walk-step, following the bass line with small steps. 30s loop, repeated through the four main phases.
P4: peak (158s-165s, beat: moderate) — Drill: stay compact and test the pulse with small steps. 7s.
P5: main (165s-248s, beat: moderate) — Drill: stay compact and test the pulse with small steps. 83s.
P6: main (248s-287s, beat: moderate) — Drill: stay compact and test the pulse with small steps. 39s.
P7: outro (287s-301s, beat: subtle) — Drill: reduce travel and let the movement wind down. 14s.
```

### kizomba_drills verifier stats

```
parsed=9 repaired_ranges=2 duplicate_phases=0 filled_missing=4 skipped_lines=7 output_lines=6
```

### kizomba_drills raw Gemma draft

```
P1: intro (0s-29s, beat: moderate) — Drill: maintain a close embrace and feel the pulse together. 29s.
P2-P12: main (29s-158s, beat: moderate) — Drill: steady walk-step, following the bass line with small steps. 30s loop, repeated through the four main phases.
P13: peak (158s-165s, beat: moderate) — Drill: increase leading variety and expression. 7s.
P14-P15: main (165s-186s, beat: moderate) — Drill: same walk-step as P2-P12, but now add subtle hip styling once the basic feels automatic. 21s.
P16-P17: main (186s-209s, beat: moderate) — Drill: slow your walk to match the half-time feel. 23s.
P18-P22: main (209s-287s, beat: moderate) — Drill: same walk-step as P14-P15, but now add subtle hip styling once the basic feels automatic. 78s.
P23: main (264s-277s, beat: moderate) — Drill: practice a three-step pattern with a light pause. 13s.
P24: main (277s-287s, beat: moderate) — Drill: return to a steady walk-step. 10s.
P25: outro (287s-301s, beat: subtle) — Drill: stand still and mark the pulse with a tiny shoulder bounce. 14s.
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
T1: 29s [intro → main, beat: moderate → moderate] — when the bass kicks in, walk-step the basic on the first clear hit.
T2: 65s [main → main, beat: moderate → moderate] — as the energy lifts, travel a little more and add intention.
T3: 158s [main → peak, beat: moderate → moderate] — commit to the new energy and travel more.
T4: 165s [peak → main, beat: moderate → moderate] — settle back, breathe, and return to the basic.
T5: 248s [main → main, beat: moderate → moderate] — as the energy shifts, keep the basic and hold a steady frame.
T6: 287s [main → outro, beat: moderate → subtle] — as the energy fades and the percussion thins, contract your movement and shrink the basic to small weight shifts.
```

### kizomba_transitions verifier stats

```
parsed=6 boundaries_matched=6 boundaries_invented=0 boundaries_missing_filled=0 skipped_lines=0 output_lines=6
```

### kizomba_tutor (polished)

```
P1: 0s-29s, intro [beat: moderate] — Focus on establishing connection and finding the pulse through tiny, rhythmic weight shifts.
P2: 29s-65s, main ×3 [beat: moderate] — Use this phase to settle into the rhythm; test the pulse with small, steady steps to find your center.
P3: 65s-158s, main ×8 [beat: moderate] — Sustain your momentum by following the bass line and keeping your frame steady and responsive.
P4: 158s-165s, peak [beat: moderate] — Use this energy to increase your expression and allow for slightly more travel through the space.
P5: 165s-248s, main ×7 [beat: moderate] — Reconnect with your partner and return to a consistent, grounded walk.
P6: 248s-287s, main ×4 [beat: moderate] — Keep your movement compact and focus on smooth, controlled weight transfers.
P7: 287s-301s, outro [beat: subtle] — As the pulse softens, minimize your movement and let the dance fade out gently.
```

### unified timeline (phases + transitions)

```
P1: 0s-29s, intro [beat: moderate] — Focus on establishing connection and finding the pulse through tiny, rhythmic weight shifts.
T1: 29s [intro → main, beat: moderate → moderate] — when the bass kicks in, walk-step the basic on the first clear hit.
P2: 29s-65s, main ×3 [beat: moderate] — Use this phase to settle into the rhythm; test the pulse with small, steady steps to find your center.
T2: 65s [main → main, beat: moderate → moderate] — as the energy lifts, travel a little more and add intention.
P3: 65s-158s, main ×8 [beat: moderate] — Sustain your momentum by following the bass line and keeping your frame steady and responsive.
T3: 158s [main → peak, beat: moderate → moderate] — commit to the new energy and travel more.
P4: 158s-165s, peak [beat: moderate] — Use this energy to increase your expression and allow for slightly more travel through the space.
T4: 165s [peak → main, beat: moderate → moderate] — settle back, breathe, and return to the basic.
P5: 165s-248s, main ×7 [beat: moderate] — Reconnect with your partner and return to a consistent, grounded walk.
T5: 248s [main → main, beat: moderate → moderate] — as the energy shifts, keep the basic and hold a steady frame.
P6: 248s-287s, main ×4 [beat: moderate] — Keep your movement compact and focus on smooth, controlled weight transfers.
T6: 287s [main → outro, beat: moderate → subtle] — as the energy fades and the percussion thins, contract your movement and shrink the basic to small weight shifts.
P7: 287s-301s, outro [beat: subtle] — As the pulse softens, minimize your movement and let the dance fade out gently.
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
This track lasts 185.4 seconds with a steady tempo of 96 BPM. The musical journey begins with a quiet intro, moves into a long main section, and then builds tension through a build phase into a high-energy peak. Following this peak, the music drops into a quiet break before settling into an outro. Because the percussiveness is unusually low, you will find that the rhythm is drum-light; instead of a heavy percussive grid, the melodic and harmonic content carries the pulse.

The most challenging moment occurs during the break from 141s to 163s. During this stretch, the beat clarity becomes moderate and the percussion thins out significantly, making the pulse much harder to lock onto. You may also find the pulse subtle during the middle sections where the percussiveness dips, requiring you to listen more closely to the underlying textures. When you reach that quiet break, do not try to find a heavy beat; instead, trust the bass line to guide your sense of timing.
```

### kizomba_tutor (one-pass)

```
P1: 0s-17s, intro [beat: clear] — Find the pulse together with minimal movement and a close embrace.
P2: 17s-23s, short_break [beat: clear] — Maintain the connection while the energy begins to lift slightly.
P3: 23s-85s, main ×6 [beat: clear] — Establishing the rhythm; use a steady walk-step and let the bass guide your movement.
P4: 85s-90s, short_break [beat: clear] — Reset your frame and prepare for the next energy shift.
P5: 90s-110s, main ×2 [beat: clear] — Sustaining the flow; focus on smooth weight transfers to keep the walk even.
P6: 110s-120s, build [beat: clear] — The music is pulling you forward; gradually increase your step size and expression.
P7: 120s-131s, peak [beat: clear] — This is the emotional high point; use more variety in your lead and stronger steps.
P8: 131s-141s, main [beat: clear] — Returning to the basics; re-establish a steady walk-step after the peak.
P9: 141s-163s, break [beat: moderate] — The pulse is less obvious; stay compact and test the rhythm with small, gentle steps.
P10: 163s-185s, outro [beat: clear] — Closing the dance; slow down your movement and return to a gentle, minimal connection.
```

### kizomba_drills (verified)

```
P1: intro (0s-17s, beat: clear) — Drill: focus on connection with minimal movement. 17s.
P2: short_break (17s-23s, beat: clear) — Drill: reduce travel and keep a small pulse in the body. 6s.
P3: main (23s-85s, beat: clear) — Drill: steady walk-step, following the bass line. 62s loop, repeated through the six main phases.
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
P1: intro (0s-17s, beat: clear) — Drill: focus on connection with minimal movement. 17s.
P2: short_break (17s-23s, beat: clear) — Drill: reduce travel and keep a small pulse in the body. 6s.
P3-P8: main (23s-85s, beat: clear) — Drill: steady walk-step, following the bass line. 62s loop, repeated through the six main phases.
P9: short_break (85s-90s, beat: clear) — Drill: reset your frame and reconnect. 5s.
P10-P12: main (90s-120s, beat: clear) — Drill: maintain a steady walk-step, matching the bass. 30s loop.
P13: build (110s-120s, beat: clear) — Drill: increase step size and expression to build tension. 10s.
P14: peak (120s-131s, beat: clear) — Drill: use stronger saídas and more leading variety. 11s.
P15-P16: main (131s-141s, beat: clear) — Drill: same walk-step as P3-P8, but add subtle hip styling once the basic feels automatic. 10s.
P17: break (141s-163s, beat: moderate) — Drill: stay compact with small steps and test the pulse. 22s.
P18: outro (163s-185s, beat: clear) — Drill: slow the pace and return to minimal movement. 22s.
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
T1: 17s [intro → short_break, beat: clear → clear] — transition to a steady walk, matching the bass.
T2: 23s [short_break → main, beat: clear → clear] — as the energy lifts, travel a little more with intention.
T3: 85s [main → short_break, beat: clear → clear] — as the energy settles, keep the basic and hold a steady frame.
T4: 90s [short_break → main, beat: clear → clear] — return to a steady walk-step, following the bass.
T5: 110s [main → build, beat: clear → clear] — as the energy increases, commit to the new energy and travel more.
T6: 120s [build → peak, beat: clear → clear] — embrace the emotional high point with more expression and larger steps.
T7: 131s [peak → main, beat: clear → clear] — settle back, breathe, and return to the basic.
T8: 141s [main → break, beat: clear → moderate] — as the energy fades and the percussion thins, keep a small pulse in the body, listen, and reset.
T9: 163s [break → outro, beat: moderate → clear] — walk-step on the first clear bass hit, then contract movement and slow the basic to close.
```

### kizomba_transitions verifier stats

```
parsed=9 boundaries_matched=9 boundaries_invented=0 boundaries_missing_filled=0 skipped_lines=0 output_lines=9
```

### kizomba_tutor (polished)

```
P1: 0s-17s, intro [beat: clear] — Find the pulse together with minimal movement and a close embrace.
P2: 17s-23s, short_break [beat: clear] — Keep a small pulse in the body and prepare to move with the rising energy.
P3: 23s-85s, main ×6 [beat: clear] — Establish the rhythm; use a steady walk-step and let the bass guide your weight transfers.
P4: 85s-90s, short_break [beat: clear] — Reduce travel and reset your frame to prepare for the next energy shift.
P5: 90s-110s, main ×2 [beat: clear] — Sustain the flow by focusing on smooth, even steps that follow the steady pulse.
P6: 110s-120s, build [beat: clear] — The music is pulling you forward; gradually increase your step size and movement expression.
P7: 120s-131s, peak [beat: clear] — Use more variety in your lead and more intentional, grounded steps.
P8: 131s-141s, main [beat: clear] — Re-establish a steady, controlled walk-step to ground the dance after the peak.
P9: 141s-163s, break [beat: moderate] — Stay compact and avoid chasing extra percussion; use small, gentle steps to find the rhythm.
P10: 163s-185s, outro [beat: clear] — Close the dance by slowing your movement and returning to a gentle, minimal connection.
```

### unified timeline (phases + transitions)

```
P1: 0s-17s, intro [beat: clear] — Find the pulse together with minimal movement and a close embrace.
T1: 17s [intro → short_break, beat: clear → clear] — transition to a steady walk, matching the bass.
P2: 17s-23s, short_break [beat: clear] — Keep a small pulse in the body and prepare to move with the rising energy.
T2: 23s [short_break → main, beat: clear → clear] — as the energy lifts, travel a little more with intention.
P3: 23s-85s, main ×6 [beat: clear] — Establish the rhythm; use a steady walk-step and let the bass guide your weight transfers.
T3: 85s [main → short_break, beat: clear → clear] — as the energy settles, keep the basic and hold a steady frame.
P4: 85s-90s, short_break [beat: clear] — Reduce travel and reset your frame to prepare for the next energy shift.
T4: 90s [short_break → main, beat: clear → clear] — return to a steady walk-step, following the bass.
P5: 90s-110s, main ×2 [beat: clear] — Sustain the flow by focusing on smooth, even steps that follow the steady pulse.
T5: 110s [main → build, beat: clear → clear] — as the energy increases, commit to the new energy and travel more.
P6: 110s-120s, build [beat: clear] — The music is pulling you forward; gradually increase your step size and movement expression.
T6: 120s [build → peak, beat: clear → clear] — embrace the emotional high point with more expression and larger steps.
P7: 120s-131s, peak [beat: clear] — Use more variety in your lead and more intentional, grounded steps.
T7: 131s [peak → main, beat: clear → clear] — settle back, breathe, and return to the basic.
P8: 131s-141s, main [beat: clear] — Re-establish a steady, controlled walk-step to ground the dance after the peak.
T8: 141s [main → break, beat: clear → moderate] — as the energy fades and the percussion thins, keep a small pulse in the body, listen, and reset.
P9: 141s-163s, break [beat: moderate] — Stay compact and avoid chasing extra percussion; use small, gentle steps to find the rhythm.
T9: 163s [break → outro, beat: moderate → clear] — walk-step on the first clear bass hit, then contract movement and slow the basic to close.
P10: 163s-185s, outro [beat: clear] — Close the dance by slowing your movement and returning to a gentle, minimal connection.
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
This track lasts 254.3 seconds with a tempo of 96 BPM. The musical journey begins with a subtle intro, transitions into a series of main sections with varying energy levels, and incorporates several breaks before settling into a gentle outro. Throughout the duration, the rhythm is drum-light; instead of a heavy percussive grid, the melodic and harmonic content carries the pulse, making the rhythm feel more felt than heard.

The most challenging moments occur during the intro (0s–36s) and the breaks (such as at 165s), where the beat is described as subtle or moderate. In these sections, the pulse is less obvious, and the low percussiveness makes it easy to lose your sense of timing. The hardest moment is the initial intro, where the beat is at its most subtle and the rhythm is least defined. During these dips in clarity, do not search for a sharp hit; instead, simply feel the underlying pulse.
```

### kizomba_tutor (one-pass)

```
P1: 0s-36s, intro [beat: subtle] — The pulse is felt rather than heard; keep movements tiny and just focus on a small weight shift to find the connection.
P2: 36s-51s, break [beat: clear] — The pulse is easier to lock onto now; use this moment to reset your frame and prepare for more movement.
P3: 51s-103s, main ×5 [beat: clear] — Establishing the rhythm; it is safe to trust the steady pulse and begin a smooth, even walk-step.
P4: 103s-113s, short_break [beat: clear] — The rhythm has a syncopated feel; lean into the bass and use a slight weight transfer to stay connected.
P5: 113s-165s, main ×5 [beat: clear] — Sustaining the flow; keep your walk steady and let the bass guide your steps as you travel.
P6: 165s-187s, break [beat: moderate] — The beat is less obvious; stay compact and test the pulse with small steps rather than traveling.
P7: 187s-227s, main ×4 [beat: moderate] — Returning to the groove; avoid chasing extra percussion and focus on reconnecting with your partner through the bass.
P8: 227s-254s, outro [beat: moderate] — Closing the dance; keep your movement minimal and let the energy wind down gently.
```

### kizomba_drills (verified)

```
P1: intro (0s-36s, beat: subtle) — Drill: mark the pulse with a tiny shoulder bounce to prepare for re-entry. 36s.
P2: break (36s-51s, beat: clear) — Drill: reduce travel and keep a small pulse in the body. 15s.
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
P1: intro (0s-36s, beat: subtle) — Drill: mark the pulse with a tiny shoulder bounce to prepare for re-entry. 36s.
P2: break (36s-51s, beat: clear) — Drill: reduce travel and keep a small pulse in the body. 15s.
P3-P7: main (51s-103s, beat: clear) — Drill: practice a steady walk-step focusing on weight transfer. 52s.
P8: short_break (103s-113s, beat: clear) — Drill: shrink the dance and maintain a small body pulse. 10s.
P9-P13: main (113s-165s, beat: clear) — Drill: same walk-step as P3-P7, but now add subtle hip styling once the basic feels automatic. 52s.
P14: break (165s-187s, beat: moderate) — Drill: keep steps small and test the pulse. 22s.
P15-P18: main (187s-227s, beat: moderate) — Drill: stay compact with small steps to avoid chasing extra percussion. 40s.
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
T1: 36s [intro → break, beat: subtle → clear] — as the beat becomes clear, keep a small pulse in the body, listen, and reset.
T2: 51s [break → main, beat: clear → clear] — walk-step on the first clear bass hit.
T3: 103s [main → short_break, beat: clear → clear] — as the energy shifts, lean into the syncopated feel with a weight transfer.
T4: 113s [short_break → main, beat: clear → clear] — walk-step on the first clear bass hit.
T5: 165s [main → break, beat: clear → moderate] — as the energy fades and the percussion thins, keep a small pulse in the body and listen.
T6: 187s [break → main, beat: moderate → moderate] — when the bass kicks in, walk-step on the first clear hit.
T7: 227s [main → outro, beat: moderate → moderate] — as the energy fades and the percussion thins, contract your movement and slow the basic to prepare to close.
```

### kizomba_transitions verifier stats

```
parsed=7 boundaries_matched=7 boundaries_invented=0 boundaries_missing_filled=0 skipped_lines=0 output_lines=7
```

### kizomba_tutor (polished)

```
P1: 0s-36s, intro [beat: subtle] — The pulse is felt rather than heard; keep your movements tiny and focus on small weight shifts to establish your connection.
P2: 36s-51s, break [beat: clear] — The pulse is now easier to lock onto; use this moment to reduce travel, reset your frame, and prepare to reconnect.
P3: 51s-103s, main ×5 [beat: clear] — Establishing the rhythm; trust the steady pulse and practice a smooth, even walk-step.
P4: 103s-113s, short_break [beat: clear] — The rhythm feels syncopated; lean into the bass and use slight weight transfers to maintain your connection.
P5: 113s-165s, main ×5 [beat: clear] — Sustaining the flow; keep your walk steady and let the bass guide your steps as you travel through the space.
P6: 165s-187s, break [beat: moderate] — The beat is less obvious; stay compact and use a small body pulse rather than traveling.
P7: 187s-227s, main ×4 [beat: moderate] — Returning to the groove; avoid chasing extra percussion and focus on reconnecting with your partner through the bass.
P8: 227s-254s, outro [beat: moderate] — Closing the dance; keep your movements minimal and let the energy wind down gently.
```

### unified timeline (phases + transitions)

```
P1: 0s-36s, intro [beat: subtle] — The pulse is felt rather than heard; keep your movements tiny and focus on small weight shifts to establish your connection.
T1: 36s [intro → break, beat: subtle → clear] — as the beat becomes clear, keep a small pulse in the body, listen, and reset.
P2: 36s-51s, break [beat: clear] — The pulse is now easier to lock onto; use this moment to reduce travel, reset your frame, and prepare to reconnect.
T2: 51s [break → main, beat: clear → clear] — walk-step on the first clear bass hit.
P3: 51s-103s, main ×5 [beat: clear] — Establishing the rhythm; trust the steady pulse and practice a smooth, even walk-step.
T3: 103s [main → short_break, beat: clear → clear] — as the energy shifts, lean into the syncopated feel with a weight transfer.
P4: 103s-113s, short_break [beat: clear] — The rhythm feels syncopated; lean into the bass and use slight weight transfers to maintain your connection.
T4: 113s [short_break → main, beat: clear → clear] — walk-step on the first clear bass hit.
P5: 113s-165s, main ×5 [beat: clear] — Sustaining the flow; keep your walk steady and let the bass guide your steps as you travel through the space.
T5: 165s [main → break, beat: clear → moderate] — as the energy fades and the percussion thins, keep a small pulse in the body and listen.
P6: 165s-187s, break [beat: moderate] — The beat is less obvious; stay compact and use a small body pulse rather than traveling.
T6: 187s [break → main, beat: moderate → moderate] — when the bass kicks in, walk-step on the first clear hit.
P7: 187s-227s, main ×4 [beat: moderate] — Returning to the groove; avoid chasing extra percussion and focus on reconnecting with your partner through the bass.
T7: 227s [main → outro, beat: moderate → moderate] — as the energy fades and the percussion thins, contract your movement and slow the basic to prepare to close.
P8: 227s-254s, outro [beat: moderate] — Closing the dance; keep your movements minimal and let the energy wind down gently.
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
This 284.0-second track runs at a slow 81 BPM, which is below the typical range for this style. The musical journey begins with a quiet intro, moves into several main sections, experiences a short break and an instrumental passage, reaches a high-energy peak, and eventually settles into a low-energy outro. Because the percussiveness is unusually low, the rhythm is not driven by a heavy drum kit; instead, the melodic and harmonic content carries the pulse, making the music feel quite drum-light.

The most challenging moments occur during the short break starting at 16.4s and the outro beginning at 265s, where the beat clarity becomes moderate rather than clear. You may also find the pulse harder to lock into during the final main section around 238.7s, as the rhythm becomes quite thin and the percussion drops away. During these transitions where the pulse is less obvious, do not try to find a sharp percussive hit; instead, trust the bass line to carry you through the change.
```

### kizomba_tutor (one-pass)

```
P1: 0s-10s, intro [beat: clear] — Find the steady pulse and use a close embrace to feel the connection.
P2: 10s-16s, main [beat: clear] — Establishing the rhythm; use a steady walk-step and let the bass guide your movement.
P3: 16s-29s, short_break [beat: moderate] — The pulse is a bit less obvious; stay compact and test the rhythm with small steps.
P4: 29s-83s, main ×5 [beat: clear] — Sustaining the flow; trust the steady pulse to travel a little more with your walk.
P5: 83s-95s, instrumental [beat: clear] — The beat remains steady; keep your movement smooth as the melody carries the rhythm.
P6: 95s-101s, peak [beat: clear] — This is the emotional high point; use the clear pulse to add more expression and intention.
P7: 101s-265s, main ×13 [beat: clear] — Returning to the basics after the peak; re-establish your connection with a steady walk.
P8: 265s-284s, outro [beat: moderate] — The rhythm is less defined; avoid chasing extra percussion and return to minimal movement.
```

### kizomba_drills (verified)

```
P1: intro (0s-10s, beat: clear) — Drill: maintain a close embrace and feel the pulse together. 10s.
P2: main (10s-16s, beat: clear) — Drill: practice a steady walk-step following the bass line. 6s.
P3: short_break (16s-29s, beat: moderate) — Drill: reduce travel and keep a small pulse in the body. 13s.
P4: main (29s-83s, beat: clear) — Drill: same walk-step as P2, but add subtle hip styling once the basic feels automatic. 54s loop, repeated through the four main phases.
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
P1: intro (0s-10s, beat: clear) — Drill: maintain a close embrace and feel the pulse together. 10s.
P2: main (10s-16s, beat: clear) — Drill: practice a steady walk-step following the bass line. 6s.
P3: short_break (16s-29s, beat: moderate) — Drill: reduce travel and keep a small pulse in the body. 13s.
P4-P7: main (29s-83s, beat: clear) — Drill: same walk-step as P2, but add subtle hip styling once the basic feels automatic. 54s loop, repeated through the four main phases.
P8: instrumental (83s-95s, beat: clear) — Drill: focus on weight transfer during the walk-step. 12s.
P9: peak (95s-101s, beat: clear) — Drill: use more expression and varied leading. 6s.
P10-P15: main (101s-167s, beat: clear) — Drill: keep the energy high with stronger saídas. 66s loop, repeated through the four main phases.
P16-P17: main (167s-190s, beat: clear) — Drill: lead with a strong step, followed by light steps. 23s.
P18: main (190s-196s, beat: moderate) — Drill: stay compact with small steps to test the pulse. 6s.
P19-P21: main (196s-238s, beat: clear) — Drill: return to the steady walk-step. 42s.
P22: main (238s-251s, beat: moderate) — Drill: avoid chasing extra percussion; keep the pulse small. 13s.
P23: main (251s-265s, beat: clear) — Drill: focus on matching the bass line with your feet. 14s.
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
T3: 29s [short_break → main, beat: moderate → clear] — walk-step on the first clear bass hit once the pulse stabilizes.
T4: 83s [main → instrumental, beat: clear → clear] — keep your basic going steadily; the instrumental is medium-energy.
T5: 95s [instrumental → peak, beat: clear → clear] — commit to the new energy, travel more, and add intention.
T6: 101s [peak → main, beat: clear → clear] — settle back, breathe, and return to the basic.
T7: 265s [main → outro, beat: clear → moderate] — as the energy fades and the percussion thins, contract movement, slow the basic, and prepare to close.
```

### kizomba_transitions verifier stats

```
parsed=7 boundaries_matched=7 boundaries_invented=0 boundaries_missing_filled=0 skipped_lines=0 output_lines=7
```

### kizomba_tutor (polished)

```
P1: 0s-10s, intro [beat: clear] — Find the steady pulse and use a close embrace to establish a grounded connection.
P2: 10s-16s, main [beat: clear] — Focus on a consistent rhythm; use a steady walk-step and let the bass guide your weight transfers.
P3: 16s-29s, short_break [beat: moderate] — The pulse is less obvious; stay compact and use small, controlled steps to find the rhythm.
P4: 29s-83s, main ×5 [beat: clear] — Sustain your flow; use the steady pulse to increase your travel through the space with your walk.
P5: 83s-95s, instrumental [beat: clear] — The beat remains steady; keep your movement fluid and smooth as the melody unfolds.
P6: 95s-101s, peak [beat: clear] — This is the emotional high point; use the clear pulse to add more intention and presence to your connection.
P7: 101s-265s, main ×13 [beat: clear] — Return to the basics; re-establish your connection with a steady, rhythmic walk.
P8: 265s-284s, outro [beat: moderate] — The rhythm is less defined; avoid chasing extra percussion and return to minimal, subtle movement.
```

### unified timeline (phases + transitions)

```
P1: 0s-10s, intro [beat: clear] — Find the steady pulse and use a close embrace to establish a grounded connection.
T1: 10s [intro → main, beat: clear → clear] — walk-step the basic on the first clear bass hit.
P2: 10s-16s, main [beat: clear] — Focus on a consistent rhythm; use a steady walk-step and let the bass guide your weight transfers.
T2: 16s [main → short_break, beat: clear → moderate] — keep a small pulse in the body, listen, and reset.
P3: 16s-29s, short_break [beat: moderate] — The pulse is less obvious; stay compact and use small, controlled steps to find the rhythm.
T3: 29s [short_break → main, beat: moderate → clear] — walk-step on the first clear bass hit once the pulse stabilizes.
P4: 29s-83s, main ×5 [beat: clear] — Sustain your flow; use the steady pulse to increase your travel through the space with your walk.
T4: 83s [main → instrumental, beat: clear → clear] — keep your basic going steadily; the instrumental is medium-energy.
P5: 83s-95s, instrumental [beat: clear] — The beat remains steady; keep your movement fluid and smooth as the melody unfolds.
T5: 95s [instrumental → peak, beat: clear → clear] — commit to the new energy, travel more, and add intention.
P6: 95s-101s, peak [beat: clear] — This is the emotional high point; use the clear pulse to add more intention and presence to your connection.
T6: 101s [peak → main, beat: clear → clear] — settle back, breathe, and return to the basic.
P7: 101s-265s, main ×13 [beat: clear] — Return to the basics; re-establish your connection with a steady, rhythmic walk.
T7: 265s [main → outro, beat: clear → moderate] — as the energy fades and the percussion thins, contract movement, slow the basic, and prepare to close.
P8: 265s-284s, outro [beat: moderate] — The rhythm is less defined; avoid chasing extra percussion and return to minimal, subtle movement.
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
This track lasts 372.5 seconds with a tempo of 89 BPM. The musical journey begins with a medium-energy intro that transitions into a long, evolving main section. This core section moves through various energy levels before reaching a brief peak, followed by an instrumental break and a final main section that leads into a low-energy outro. Throughout most of the track, the pulse is carried by a clear percussive grid, though the energy fluctuates significantly as the song progresses.

The primary challenge for maintaining the pulse occurs during the intro, from 0s to 23s, where the beat is only moderate and the percussiveness is quite low. You may also find the pulse becomes more subtle during the transition into the low-energy instrumental section at 248s. The hardest moment is the very beginning, as the rhythm is less defined and requires more active listening to lock in. During this intro, focus on the bass line to find the underlying pulse.
```

### kizomba_tutor (one-pass)

```
P1: 0s-23s, intro [beat: moderate] — Keep movement compact and test the pulse with small weight shifts to find the connection.
P2: 23s-112s, main ×9 [beat: clear] — The pulse is easy to follow; use this establishing phase to settle into a steady walk-step.
P3: 112s-117s, peak [beat: clear] — The beat is very easy to hear; increase your expression and add more variety to your leading.
P4: 117s-177s, main ×5 [beat: clear] — Returning to the basic, trust the steady pulse to guide your weight transfers.
P5: 177s-204s, main ×2 [beat: clear] — Maintain your frame and focus on a smooth, consistent walk through this sustaining phase.
P6: 204s-248s, main ×3 [beat: clear] — Continue your steady walk, using the clear pulse to keep your movement fluid.
P7: 248s-258s, instrumental [beat: clear] — Use this quieter moment to reset your connection while keeping a small pulse in the body.
P8: 258s-280s, main ×3 [beat: clear] — Re-establish the basic and focus on breathing through your steps as you reconnect.
P9: 280s-357s, main ×5 [beat: clear] — This is a sustaining phase; travel a little more and let the clear pulse drive your momentum.
P10: 357s-373s, outro [beat: clear] — As the song winds down, contract your movement and let the dance end gently.
```

### kizomba_drills (verified)

```
P1: intro (0s-23s, beat: moderate) — Drill: stay compact with small steps and test the pulse. 23s.
P2: main (23s-112s, beat: clear) — Drill: practice a steady walk-step focusing on weight transfer. 89s.
P3: peak (112s-117s, beat: clear) — Drill: increase leading variety through the frame. 5s.
P4-P6: main (117s-248s, beat: clear) — Drill: same walk-step as P2, but now add subtle hip styling once the basic feels automatic. 131s.
P7: instrumental (248s-258s, beat: clear) — Drill: reduce travel and keep a small pulse in the body. 10s.
P8-P9: main (258s-357s, beat: clear) — Drill: maintain the walk-step and follow the bass line. 99s.
P10: outro (357s-373s, beat: clear) — Drill: slow the pace and return to minimal movement. 16s.
```

### kizomba_drills verifier stats

```
parsed=7 repaired_ranges=0 duplicate_phases=0 filled_missing=0 skipped_lines=0 output_lines=7
```

### kizomba_drills raw Gemma draft

```
P1: intro (0s-23s, beat: moderate) — Drill: stay compact with small steps and test the pulse. 23s.
P2-P2: main (23s-112s, beat: clear) — Drill: practice a steady walk-step focusing on weight transfer. 89s.
P3: peak (112s-117s, beat: clear) — Drill: increase leading variety through the frame. 5s.
P4-P6: main (117s-248s, beat: clear) — Drill: same walk-step as P2, but now add subtle hip styling once the basic feels automatic. 131s.
P7: instrumental (248s-258s, beat: clear) — Drill: reduce travel and keep a small pulse in the body. 10s.
P8-P9: main (258s-357s, beat: clear) — Drill: maintain the walk-step and follow the bass line. 99s.
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
T1: 23s [intro → main, beat: moderate → clear] — when the bass kicks in, walk-step the basic on the first clear hit.
T2: 112s [main → peak, beat: clear → clear] — commit to the new energy, travel more, and add intention.
T3: 117s [peak → main, beat: clear → clear] — settle back, breathe, and return to the basic.
T4: 177s [main → main, beat: clear → clear] — as the percussion thickens, travel a little more and add intention.
T5: 204s [main → main, beat: clear → clear] — as the energy settles, keep the basic and hold a steady frame.
T6: 248s [main → instrumental, beat: clear → clear] — keep your basic going steadily through the instrumental.
T7: 258s [instrumental → main, beat: clear → clear] — keep your basic going steadily.
T8: 280s [main → main, beat: clear → clear] — as the energy lifts, travel a little more and add intention.
T9: 357s [main → outro, beat: clear → clear] — as the energy fades and the percussion thins, contract movement, slow the basic, and prepare to close.
```

### kizomba_transitions verifier stats

```
parsed=9 boundaries_matched=9 boundaries_invented=0 boundaries_missing_filled=0 skipped_lines=0 output_lines=9
```

### kizomba_tutor (polished)

```
P1: 0s-23s, intro [beat: moderate] — Keep your movements compact and use small weight shifts to find the pulse and establish your connection.
P2: 23s-112s, main ×9 [beat: clear] — Use this steady pulse to settle into a rhythmic, grounded walk-step.
P3: 112s-117s, peak [beat: clear] — The beat is very prominent; use this energy to expand your movement and add more intention to your lead.
P4: 117s-177s, main ×5 [beat: clear] — Return to your foundation, trusting the steady pulse to guide your weight transfers.
P5: 177s-204s, main ×2 [beat: clear] — Maintain a strong frame and focus on smooth, consistent steps through this phase.
P6: 204s-248s, main ×3 [beat: clear] — Maintain your rhythmic walking, using the clear pulse to keep your momentum fluid.
P7: 248s-258s, instrumental [beat: clear] — Reduce your travel and keep a small pulse in the body to reset before the next phase.
P8: 258s-280s, main ×3 [beat: clear] — Re-establish your basic steps and focus on breathing through your connection as you reconnect.
P9: 280s-357s, main ×5 [beat: clear] — Use this sustaining phase to increase your travel, letting the clear pulse drive your momentum.
P10: 357s-373s, outro [beat: clear] — As the song winds down, contract your movement and let the dance end with gentle, controlled steps.
```

### unified timeline (phases + transitions)

```
P1: 0s-23s, intro [beat: moderate] — Keep your movements compact and use small weight shifts to find the pulse and establish your connection.
T1: 23s [intro → main, beat: moderate → clear] — when the bass kicks in, walk-step the basic on the first clear hit.
P2: 23s-112s, main ×9 [beat: clear] — Use this steady pulse to settle into a rhythmic, grounded walk-step.
T2: 112s [main → peak, beat: clear → clear] — commit to the new energy, travel more, and add intention.
P3: 112s-117s, peak [beat: clear] — The beat is very prominent; use this energy to expand your movement and add more intention to your lead.
T3: 117s [peak → main, beat: clear → clear] — settle back, breathe, and return to the basic.
P4: 117s-177s, main ×5 [beat: clear] — Return to your foundation, trusting the steady pulse to guide your weight transfers.
T4: 177s [main → main, beat: clear → clear] — as the percussion thickens, travel a little more and add intention.
P5: 177s-204s, main ×2 [beat: clear] — Maintain a strong frame and focus on smooth, consistent steps through this phase.
T5: 204s [main → main, beat: clear → clear] — as the energy settles, keep the basic and hold a steady frame.
P6: 204s-248s, main ×3 [beat: clear] — Maintain your rhythmic walking, using the clear pulse to keep your momentum fluid.
T6: 248s [main → instrumental, beat: clear → clear] — keep your basic going steadily through the instrumental.
P7: 248s-258s, instrumental [beat: clear] — Reduce your travel and keep a small pulse in the body to reset before the next phase.
T7: 258s [instrumental → main, beat: clear → clear] — keep your basic going steadily.
P8: 258s-280s, main ×3 [beat: clear] — Re-establish your basic steps and focus on breathing through your connection as you reconnect.
T8: 280s [main → main, beat: clear → clear] — as the energy lifts, travel a little more and add intention.
P9: 280s-357s, main ×5 [beat: clear] — Use this sustaining phase to increase your travel, letting the clear pulse drive your momentum.
T9: 357s [main → outro, beat: clear → clear] — as the energy fades and the percussion thins, contract movement, slow the basic, and prepare to close.
P10: 357s-373s, outro [beat: clear] — As the song winds down, contract your movement and let the dance end with gentle, controlled steps.
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
This track spans 208.9 seconds at a tempo of 92 BPM. The musical journey begins with a quiet intro, transitions into several main sections that fluctuate between medium and high energy, encounters a low-energy break, and finally settles into an outro. Because the percussiveness is unusually low, the rhythm is not driven by a heavy drum kit; instead, the melodic and harmonic content carries the pulse, making the bass line the primary guide for the song's rhythmic structure.

The beat remains clear throughout most of the track, but you may find the pulse harder to lock onto during the intro (0.0s–11.7s) and certain main sections, such as between 32.3s and 48.5s, where the beat clarity becomes more moderate. The most challenging moment occurs during the transition into the break at 148s, where the energy drops and the rhythm shifts. During these quieter, less percussive moments, do not try to find a heavy beat; instead, feel the underlying pulse provided by the bass.
```

### kizomba_tutor (one-pass)

```
P1: 0s-12s, intro [beat: clear] — Focus on connection in a close embrace; just feel the pulse together without much movement.
P2: 12s-59s, main ×4 [beat: clear] — Establishing the rhythm; use a steady walk-step and let the bass guide your weight transfers.
P3: 59s-80s, main ×2 [beat: clear] — Sustaining the energy; keep your walk even and follow the bass line for more intentional steps.
P4: 80s-121s, main ×4 [beat: clear] — Sustaining the flow; maintain a steady frame and let the bass dictate your movement.
P5: 121s-148s, main ×2 [beat: clear] — Building momentum; you can travel a little more as the energy climbs.
P6: 148s-159s, break [beat: clear] — Reset your connection; reduce travel and use this quiet moment to breathe and listen.
P7: 159s-195s, main ×3 [beat: clear] — Returning to the pulse; re-establish the basic walk-step and reconnect with your partner.
P8: 195s-209s, outro [beat: clear] — Closing the dance; slow down your movement and return to a minimal, gentle feeling.
```

### kizomba_drills (verified)

```
P1: intro (0s-12s, beat: clear) — Drill: find the pulse through a tiny shoulder bounce to establish connection. 12s.
P2-P5: main (12s-148s, beat: clear) — Drill: practice a steady walk-step, letting the bass line guide your weight transfer. 30s loop, repeated through the four main phases.
P6: break (148s-159s, beat: clear) — Drill: reduce your travel and keep a small pulse in the body to prepare for the return. 11s during the break.
P7: main (159s-195s, beat: clear) — Drill: same walk-step as P2-P5, but now add subtle hip styling once the basic feels automatic. 36s.
P8: outro (195s-209s, beat: clear) — Drill: slow the pace and return to minimal movement to end the dance gently. 14s.
```

### kizomba_drills verifier stats

```
parsed=5 repaired_ranges=1 duplicate_phases=0 filled_missing=0 skipped_lines=0 output_lines=5
```

### kizomba_drills raw Gemma draft

```
P1: intro (0s-12s, beat: clear) — Drill: find the pulse through a tiny shoulder bounce to establish connection. 12s.
P2-P5: main (12s-121s, beat: clear) — Drill: practice a steady walk-step, letting the bass line guide your weight transfer. 30s loop, repeated through the four main phases.
P6: break (148s-159s, beat: clear) — Drill: reduce your travel and keep a small pulse in the body to prepare for the return. 11s during the break.
P7-P8: main (159s-195s, beat: clear) — Drill: same walk-step as P2-P5, but now add subtle hip styling once the basic feels automatic. 36s.
P8: outro (195s-209s, beat: clear) — Drill: slow the pace and return to minimal movement to end the dance gently. 14s.
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
T3: 80s [main → main, beat: clear → clear] — as the energy settles, keep the basic and hold a steady frame.
T4: 121s [main → main, beat: clear → clear] — as the energy lifts, travel a little more and add intention to your steps.
T5: 148s [main → break, beat: clear → clear] — as the energy fades and the percussion thins, keep a small pulse in the body, listen, and reset.
T6: 159s [break → main, beat: clear → clear] — when the bass kicks in, walk-step on the first clear bass hit.
T7: 195s [main → outro, beat: clear → clear] — as the energy fades and the percussion thins, contract your movement and slow the basic to prepare to close.
```

### kizomba_transitions verifier stats

```
parsed=7 boundaries_matched=7 boundaries_invented=0 boundaries_missing_filled=0 skipped_lines=0 output_lines=7
```

### kizomba_tutor (polished)

```
P1: 0s-12s, intro [beat: clear] — Focus on establishing a soft connection in a close embrace; use the steady pulse to find a shared rhythm through small body movements.
P2: 12s-59s, main ×4 [beat: clear] — Establish your foundation; use a rhythmic walk-step and let the bass guide your weight transfers.
P3: 59s-80s, main ×2 [beat: clear] — Maintain your momentum; keep your steps even and use the bass line to add intention to your direction.
P4: 80s-121s, main ×4 [beat: clear] — Sustain the flow; keep a stable frame and let the bass dictate the timing of your steps.
P5: 121s-148s, main ×2 [beat: clear] — Build energy; you can increase your travel or step size as the music climbs.
P6: 148s-159s, break [beat: clear] — Reset your position; reduce your travel and keep a small pulse in the body to prepare for the next phase.
P7: 159s-195s, main ×3 [beat: clear] — Reconnect with the pulse; re-establish your basic walk-step and find your partner's lead again.
P8: 195s-209s, outro [beat: clear] — Close the dance; gradually reduce your movement and return to a minimal, gentle connection.
```

### unified timeline (phases + transitions)

```
P1: 0s-12s, intro [beat: clear] — Focus on establishing a soft connection in a close embrace; use the steady pulse to find a shared rhythm through small body movements.
T1: 12s [intro → main, beat: clear → clear] — when the bass kicks in, walk-step the basic on the first clear bass hit.
P2: 12s-59s, main ×4 [beat: clear] — Establish your foundation; use a rhythmic walk-step and let the bass guide your weight transfers.
T2: 59s [main → main, beat: clear → clear] — as the energy lifts, travel a little more and add intention to your steps.
P3: 59s-80s, main ×2 [beat: clear] — Maintain your momentum; keep your steps even and use the bass line to add intention to your direction.
T3: 80s [main → main, beat: clear → clear] — as the energy settles, keep the basic and hold a steady frame.
P4: 80s-121s, main ×4 [beat: clear] — Sustain the flow; keep a stable frame and let the bass dictate the timing of your steps.
T4: 121s [main → main, beat: clear → clear] — as the energy lifts, travel a little more and add intention to your steps.
P5: 121s-148s, main ×2 [beat: clear] — Build energy; you can increase your travel or step size as the music climbs.
T5: 148s [main → break, beat: clear → clear] — as the energy fades and the percussion thins, keep a small pulse in the body, listen, and reset.
P6: 148s-159s, break [beat: clear] — Reset your position; reduce your travel and keep a small pulse in the body to prepare for the next phase.
T6: 159s [break → main, beat: clear → clear] — when the bass kicks in, walk-step on the first clear bass hit.
P7: 159s-195s, main ×3 [beat: clear] — Reconnect with the pulse; re-establish your basic walk-step and find your partner's lead again.
T7: 195s [main → outro, beat: clear → clear] — as the energy fades and the percussion thins, contract your movement and slow the basic to prepare to close.
P8: 195s-209s, outro [beat: clear] — Close the dance; gradually reduce your movement and return to a minimal, gentle connection.
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
This 237.7-second track moves at 92 BPM, following a journey that begins with a quiet intro, transitions through several main sections, and experiences a build toward an emotional peak before settling into an outro. Throughout the song, the rhythm is notably drum-light, with melodic and harmonic content carrying the pulse rather than a heavy percussive grid. You will experience various energy shifts, including intentional breaks where the music thins out, creating a sense of ebb and flow.

The most challenging moments occur during the breaks at 65s and 135s, where the beat clarity becomes moderate and the percussion thins significantly. During these stretches, the pulse is less obvious and harder to lock onto, making it easy to lose your connection to the rhythm. The hardest moment is likely the break starting at 135s, as the energy drops and the beat becomes more subtle. During these dips in clarity, do not search for a heavy drum; instead, trust the bass line to guide your sense of timing.
```

### kizomba_tutor (one-pass)

```
P1: 0s-13s, intro [beat: clear] — The pulse is felt through the bass; start with a close embrace and minimal movement to find the connection.
P2: 13s-34s, short_break [beat: clear] — The pulse remains steady; keep your walk-steps small and focus on matching the bass.
P3: 34s-65s, main ×3 [beat: clear] — Establishing the rhythm; it is safe to trust the steady pulse and begin a comfortable walk-step.
P4: 65s-76s, break [beat: moderate] — The beat is less obvious; stay compact and test the pulse with small weight shifts rather than chasing percussion.
P5: 76s-135s, main ×5 [beat: clear] — Sustaining the dance; use the clear pulse to guide your travel and keep your frame steady.
P6: 135s-146s, break [beat: moderate] — The beat is moderate; avoid extra movement and simply reset your connection.
P7: 146s-157s, main [beat: clear] — Returning to the rhythm; re-establish your basic walk-step as the pulse becomes clear again.
P8: 157s-168s, build [beat: clear] — Building tension; the music is pulling you forward, so gradually increase your step size.
P9: 168s-174s, peak [beat: clear] — The emotional high point; the pulse is very clear, allowing for more expression and variety in your lead.
P10: 174s-228s, main ×4 [beat: clear] — Closing the song; the pulse is reliable, but begin to contract your movement as the energy winds down.
P11: 228s-238s, outro [beat: clear] — The song ends gently; return to minimal movement and let the dance fade out.
```

### kizomba_drills (verified)

```
P1: intro (0s-13s, beat: clear) — Drill: maintain a close embrace and feel the pulse through the bass. 13s.
P2: short_break (13s-34s, beat: clear) — Drill: reduce travel and keep a small pulse in the body. 10.6s.
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
P1: intro (0s-13s, beat: clear) — Drill: maintain a close embrace and feel the pulse through the bass. 13s.
P2-P2: short_break (13s-23.6s, beat: clear) — Drill: reduce travel and keep a small pulse in the body. 10.6s.
P3-P3: short_break (23.6s-33.6s, beat: clear) — Drill: reset your connection and prepare for the main section. 10s.
P4-P6: main (33.6s-64.9s, beat: clear) — Drill: practice a steady walk-step focusing on weight transfer. 31.3s loop, repeated through the three main phases.
P7: break (64.9s-75.8s, beat: moderate) — Drill: stay compact with small steps and test the pulse. 10.9s.
P8-P12: main (75.8s-135.2s, beat: clear) — Drill: same walk-step as P4-P6, but now add subtle hip styling once the basic feels automatic. 59.4s loop, repeated through the five main phases.
P13: break (135.2s-146.4s, beat: moderate) — Drill: keep the pulse in the body and avoid chasing extra percussion. 11.2s.
P14: main (146.4s-156.8s, beat: clear) — Drill: focus on a steady walk-step guided by the bass line. 10.4s.
P15: build (157s-168.1s, beat: clear) — Drill: gradually increase step size to build tension. 11.1s.
P16: peak (168.1s-174.1s, beat: clear) — Drill: use more leading variety and stronger expression. 6s.
P17-P20: main (174.1s-228.1s, beat: clear) — Drill: maintain the walk-step, keeping the energy you built during the peak. 54s loop, repeated through the four main phases.
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
T1: 13s [intro → short_break, beat: clear → clear] — keep a small pulse in the body and stay connected.
T2: 34s [short_break → main, beat: clear → clear] — walk-step the basic on the first clear bass hit as the energy lifts.
T3: 65s [main → break, beat: clear → moderate] — as the energy fades, keep a small pulse in the body and listen.
T4: 76s [break → main, beat: moderate → clear] — walk-step on the first clear bass hit once the pulse returns.
T5: 135s [main → break, beat: clear → moderate] — as the energy fades, keep a small pulse in the body and listen.
T6: 146s [break → main, beat: moderate → clear] — walk-step on the first clear bass hit as the energy returns.
T7: 157s [main → build, beat: clear → clear] — commit to the new energy and travel a little more.
T8: 168s [build → peak, beat: clear → clear] — commit to the new energy and add more intention to your movement.
T9: 174s [peak → main, beat: clear → clear] — settle back, breathe, and return to the basic.
T10: 228s [main → outro, beat: clear → clear] — as the energy fades, contract your movement and prepare to close.
```

### kizomba_transitions verifier stats

```
parsed=10 boundaries_matched=10 boundaries_invented=0 boundaries_missing_filled=0 skipped_lines=0 output_lines=10
```

### kizomba_tutor (polished)

```
P1: 0s-13s, intro [beat: clear] — Feel the bass through your feet; start with a close embrace and small, grounded movements to establish your connection.
P2: 13s-34s, short_break [beat: clear] — The pulse is steady; keep your steps small and focus on matching your weight shifts to the bass.
P3: 34s-65s, main ×3 [beat: clear] — Use this steady rhythm to find your flow; a simple, comfortable walk-step is a great way to anchor your movement.
P4: 65s-76s, break [beat: moderate] — The beat is less obvious; stay compact and use subtle weight shifts rather than chasing the percussion.
P5: 76s-135s, main ×5 [beat: clear] — Use the clear pulse to guide your travel while keeping your frame steady and your connection firm.
P6: 135s-146s, break [beat: moderate] — The beat is moderate; reduce your travel and keep a small pulse in your body to reset for the next phase.
P7: 146s-157s, main [beat: clear] — Re-establish your basic walk-step as the rhythm becomes clear again.
P8: 157s-168s, build [beat: clear] — As the tension builds, gradually increase your step size to match the growing energy.
P9: 168s-174s, peak [beat: clear] — The pulse is very clear; use this stability to add more expression or variety to your lead.
P10: 174s-228s, main ×4 [beat: clear] — The pulse remains reliable, but begin to contract your movement as the energy winds down.
P11: 228s-238s, outro [beat: clear] — Return to minimal movement and let the dance fade out naturally.
```

### unified timeline (phases + transitions)

```
P1: 0s-13s, intro [beat: clear] — Feel the bass through your feet; start with a close embrace and small, grounded movements to establish your connection.
T1: 13s [intro → short_break, beat: clear → clear] — keep a small pulse in the body and stay connected.
P2: 13s-34s, short_break [beat: clear] — The pulse is steady; keep your steps small and focus on matching your weight shifts to the bass.
T2: 34s [short_break → main, beat: clear → clear] — walk-step the basic on the first clear bass hit as the energy lifts.
P3: 34s-65s, main ×3 [beat: clear] — Use this steady rhythm to find your flow; a simple, comfortable walk-step is a great way to anchor your movement.
T3: 65s [main → break, beat: clear → moderate] — as the energy fades, keep a small pulse in the body and listen.
P4: 65s-76s, break [beat: moderate] — The beat is less obvious; stay compact and use subtle weight shifts rather than chasing the percussion.
T4: 76s [break → main, beat: moderate → clear] — walk-step on the first clear bass hit once the pulse returns.
P5: 76s-135s, main ×5 [beat: clear] — Use the clear pulse to guide your travel while keeping your frame steady and your connection firm.
T5: 135s [main → break, beat: clear → moderate] — as the energy fades, keep a small pulse in the body and listen.
P6: 135s-146s, break [beat: moderate] — The beat is moderate; reduce your travel and keep a small pulse in your body to reset for the next phase.
T6: 146s [break → main, beat: moderate → clear] — walk-step on the first clear bass hit as the energy returns.
P7: 146s-157s, main [beat: clear] — Re-establish your basic walk-step as the rhythm becomes clear again.
T7: 157s [main → build, beat: clear → clear] — commit to the new energy and travel a little more.
P8: 157s-168s, build [beat: clear] — As the tension builds, gradually increase your step size to match the growing energy.
T8: 168s [build → peak, beat: clear → clear] — commit to the new energy and add more intention to your movement.
P9: 168s-174s, peak [beat: clear] — The pulse is very clear; use this stability to add more expression or variety to your lead.
T9: 174s [peak → main, beat: clear → clear] — settle back, breathe, and return to the basic.
P10: 174s-228s, main ×4 [beat: clear] — The pulse remains reliable, but begin to contract your movement as the energy winds down.
T10: 228s [main → outro, beat: clear → clear] — as the energy fades, contract your movement and prepare to close.
P11: 228s-238s, outro [beat: clear] — Return to minimal movement and let the dance fade out naturally.
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
This track lasts 213.8 seconds with a tempo of 92 BPM. The musical journey begins with an intro that transitions into several main sections of varying energy, eventually leading into a low-energy break before a final main phase and a gentle outro. Because the percussiveness is unusually low, the rhythm is not driven by a heavy drum kit; instead, the melodic and harmonic content carries the pulse, making the bass line your primary guide for the rhythm.

The most challenging moment occurs during the outro starting at 196.0 seconds, where the beat clarity shifts from clear to moderate. As the energy drops and the percussion thins out, the pulse becomes much harder to track. You may also find the break at 138 seconds difficult as the energy dips significantly, requiring a shift in how you perceive the rhythm. During these quieter, less defined moments, do not try to find a heavy beat; instead, trust the bass line to maintain your connection to the pulse.
```

### kizomba_tutor (one-pass)

```
P1: 0s-18s, intro [beat: clear] — Find the steady pulse and settle into a close embrace with minimal movement.
P2: 18s-55s, main ×3 [beat: clear] — Establishing the rhythm; trust the steady pulse and use a smooth walk-step.
P3: 55s-71s, main ×2 [beat: clear] — Sustaining the energy; focus on your frame and let the bass guide your steps.
P4: 71s-112s, main ×4 [beat: clear] — Building intensity; you can travel a little more as the energy climbs.
P5: 112s-138s, main ×2 [beat: clear] — Reaching a peak; maintain a strong connection while the energy stays high.
P6: 138s-149s, break [beat: clear] — Reset your movement; reduce travel and use this quiet moment to breathe.
P7: 149s-196s, main ×4 [beat: clear] — Returning to the flow; re-establish the basic walk-step as the pulse returns.
P8: 196s-214s, outro [beat: moderate] — Closing the dance; stay compact and test the pulse with small, gentle weight shifts.
```

### kizomba_drills (verified)

```
P1: intro (0s-18s, beat: clear) — Drill: maintain a close embrace and focus on weight transfer. 18s.
P2-P5: main (18s-138s, beat: clear) — Drill: practice a steady walk-step following the bass line. 53s loop, repeated through the four main phases.
P6: break (138s-149s, beat: clear) — Drill: reduce travel and keep a small pulse in the body. 11s during the break.
P7: main (149s-196s, beat: clear) — Drill: same walk-step as P2-P5, but now add subtle hip styling once the basic feels automatic. 47s.
P8: outro (196s-214s, beat: moderate) — Drill: reduce travel and let the movement wind down. 18s.
```

### kizomba_drills verifier stats

```
parsed=5 repaired_ranges=1 duplicate_phases=0 filled_missing=1 skipped_lines=1 output_lines=5
```

### kizomba_drills raw Gemma draft

```
P1: intro (0s-18s, beat: clear) — Drill: maintain a close embrace and focus on weight transfer. 18s.
P2-P5: main (18s-71s, beat: clear) — Drill: practice a steady walk-step following the bass line. 53s loop, repeated through the four main phases.
P6: break (138s-149s, beat: clear) — Drill: reduce travel and keep a small pulse in the body. 11s during the break.
P7-P8: main (149s-196s, beat: clear) — Drill: same walk-step as P2-P5, but now add subtle hip styling once the basic feels automatic. 47s.
P9: outro (196s-214s, beat: moderate) — Drill: stay compact with small steps to test the pulse. 18s.
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
T3: 71s [main → main, beat: clear → clear] — keep the basic and hold a steady frame as the percussion thins.
T4: 112s [main → main, beat: clear → clear] — travel a little more and add intention as the energy lifts.
T5: 138s [main → break, beat: clear → clear] — keep a small pulse in the body and listen as the energy fades and the percussion thins.
T6: 149s [break → main, beat: clear → clear] — walk-step on the first clear bass hit as the percussion returns.
T7: 196s [main → outro, beat: clear → moderate] — contract movement and slow the basic as the energy fades and the percussion thins.
```

### kizomba_transitions verifier stats

```
parsed=7 boundaries_matched=7 boundaries_invented=0 boundaries_missing_filled=0 skipped_lines=0 output_lines=7
```

### kizomba_tutor (polished)

```
P1: 0s-18s, intro [beat: clear] — Find the steady pulse and settle into a close embrace with a subtle rhythmic sway.
P2: 18s-55s, main ×3 [beat: clear] — Establish your rhythm; use the steady pulse to guide a smooth, grounded walk-step.
P3: 55s-71s, main ×2 [beat: clear] — Sustain the energy; keep your frame firm and let the bass drive your weight transfers.
P4: 71s-112s, main ×4 [beat: clear] — Build intensity; you can increase your travel through the space as the energy climbs.
P5: 112s-138s, main ×2 [beat: clear] — Reach the peak; maintain a strong connection while keeping your movements intentional and high-energy.
P6: 138s-149s, break [beat: clear] — Reset your movement; reduce your travel and use this moment to stabilize your connection.
P7: 149s-196s, main ×4 [beat: clear] — Return to the flow; re-establish your basic walk-step as the steady pulse returns.
P8: 196s-214s, outro [beat: moderate] — Close the dance; stay compact and use small, gentle weight shifts to follow the subtle pulse.
```

### unified timeline (phases + transitions)

```
P1: 0s-18s, intro [beat: clear] — Find the steady pulse and settle into a close embrace with a subtle rhythmic sway.
T1: 18s [intro → main, beat: clear → clear] — walk-step the basic on the first clear bass hit as the percussion returns.
P2: 18s-55s, main ×3 [beat: clear] — Establish your rhythm; use the steady pulse to guide a smooth, grounded walk-step.
T2: 55s [main → main, beat: clear → clear] — travel a little more and add intention as the bass line gains density.
P3: 55s-71s, main ×2 [beat: clear] — Sustain the energy; keep your frame firm and let the bass drive your weight transfers.
T3: 71s [main → main, beat: clear → clear] — keep the basic and hold a steady frame as the percussion thins.
P4: 71s-112s, main ×4 [beat: clear] — Build intensity; you can increase your travel through the space as the energy climbs.
T4: 112s [main → main, beat: clear → clear] — travel a little more and add intention as the energy lifts.
P5: 112s-138s, main ×2 [beat: clear] — Reach the peak; maintain a strong connection while keeping your movements intentional and high-energy.
T5: 138s [main → break, beat: clear → clear] — keep a small pulse in the body and listen as the energy fades and the percussion thins.
P6: 138s-149s, break [beat: clear] — Reset your movement; reduce your travel and use this moment to stabilize your connection.
T6: 149s [break → main, beat: clear → clear] — walk-step on the first clear bass hit as the percussion returns.
P7: 149s-196s, main ×4 [beat: clear] — Return to the flow; re-establish your basic walk-step as the steady pulse returns.
T7: 196s [main → outro, beat: clear → moderate] — contract movement and slow the basic as the energy fades and the percussion thins.
P8: 196s-214s, outro [beat: moderate] — Close the dance; stay compact and use small, gentle weight shifts to follow the subtle pulse.
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
This track lasts 199.7 seconds with a tempo of 86 BPM. The musical journey begins with a low-energy intro that transitions into a main section, followed by a build and a peak. After reaching this emotional high point, the song moves through extended main sections before settling into a low-energy outro. Throughout the arc, the pulse is primarily felt through the bass line rather than a heavy percussive grid, providing a smooth, melodic foundation for the track.

The most challenging moments occur during the final stages of the song, specifically from 148s to 182s and during the outro starting at 182s. In these sections, the beat clarity shifts from clear to moderate, meaning the pulse becomes less obvious and harder to lock onto. As the percussiveness thins and the energy levels drop, the rhythmic structure becomes more subtle, making it easy to lose your sense of timing. During these transitions, do not chase the lighter percussion; instead, feel the underlying pulse of the bass.
```

### kizomba_tutor (one-pass)

```
P1: 0s-12s, intro [beat: clear] — Start with a close embrace and minimal movement; just feel the pulse together to build connection.
P2: 12s-35s, main ×2 [beat: clear] — Establishing the rhythm; use a steady walk-step and let the bass guide your steps.
P3: 35s-45s, build [beat: clear] — The music is pulling you forward; gradually increase your step size and expression to build tension.
P4: 45s-62s, peak [beat: clear] — This is the emotional high point; use stronger saídas and more variety in your lead.
P5: 62s-148s, main ×7 [beat: clear] — Sustaining the energy; keep a steady walk-step and focus on following the bass line.
P6: 148s-182s, main ×3 [beat: moderate] — Returning to the basics; stay compact and test the pulse with small steps to avoid chasing extra percussion.
P7: 182s-200s, outro [beat: moderate] — Closing the dance; slow down and return to minimal movement to let the song end gently.
```

### kizomba_drills (verified)

```
P1: intro (0s-12s, beat: clear) — Drill: maintain a close embrace and feel the pulse through the bass. 12s.
P2: main (12s-35s, beat: clear) — Drill: practice a steady walk-step focusing on weight transfer. 33s.
P3: build (35s-45s, beat: clear) — Drill: practice steady weight transfers through this section. 11s.
P4: peak (45s-62s, beat: clear) — Drill: practice steady weight transfers through this section. 17s.
P5: main (62s-148s, beat: clear) — Drill: practice steady weight transfers through this section. 85s.
P6: main (148s-182s, beat: moderate) — Drill: stay compact and test the pulse with small steps. 34s.
P7: outro (182s-200s, beat: moderate) — Drill: reduce travel and let the movement wind down. 17s.
```

### kizomba_drills verifier stats

```
parsed=4 repaired_ranges=2 duplicate_phases=0 filled_missing=5 skipped_lines=2 output_lines=7
```

### kizomba_drills raw Gemma draft

```
P1: intro (0s-12s, beat: clear) — Drill: maintain a close embrace and feel the pulse through the bass. 12s.
P2-P4: main (12s-45s, beat: clear) — Drill: practice a steady walk-step focusing on weight transfer. 33s.
P5: peak (45s-62s, beat: clear) — Drill: increase step size and lead variety with more expression. 17s.
P6-P15: main (62s-182s, beat: clear/moderate) — Drill: same walk-step as P2-P4, but now add subtle hip styling once the basic feels automatic. 120s loop, repeated through the phases.
P16: outro (182s-200s, beat: moderate) — Drill: slow the pace and return to minimal movement. 18s.
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
T1: 12s [intro → main, beat: clear → clear] — when the bass kicks in, walk-step the basic on the first clear hit.
T2: 35s [main → build, beat: clear → clear] — commit to the new energy, travel more, and add intention.
T3: 45s [build → peak, beat: clear → clear] — commit to the new energy, travel more, and add intention.
T4: 62s [peak → main, beat: clear → clear] — settle back, breathe, and return to the basic.
T5: 148s [main → main, beat: clear → moderate] — as the energy shifts, travel a little more and add intention, but since the beat becomes less obvious, shrink your steps to small weight shifts.
T6: 182s [main → outro, beat: moderate → moderate] — as the energy fades and the percussion thins, contract your movement, slow the basic, and prepare to close.
```

### kizomba_transitions verifier stats

```
parsed=6 boundaries_matched=6 boundaries_invented=0 boundaries_missing_filled=0 skipped_lines=0 output_lines=6
```

### kizomba_tutor (polished)

```
P1: 0s-12s, intro [beat: clear] — Establish a close embrace and find a shared pulse to ground your connection.
P2: 12s-35s, main ×2 [beat: clear] — Find your rhythm using a steady walk-step, letting the bass guide your weight transfers.
P3: 35s-45s, build [beat: clear] — Feel the increasing energy; gradually expand your step size and movement range to build tension.
P4: 45s-62s, peak [beat: clear] — Embrace the emotional peak; use more expansive travel or varied directions to express the music.
P5: 62s-148s, main ×7 [beat: clear] — Maintain your momentum; keep a consistent walk-step and stay anchored to the bass line.
P6: 148s-182s, main ×3 [beat: moderate] — Focus on precision; stay compact with small steps to stay centered without chasing the subtle percussion.
P7: 182s-200s, outro [beat: moderate] — Wind down the dance; reduce your travel and return to minimal, gentle movements as the song fades.
```

### unified timeline (phases + transitions)

```
P1: 0s-12s, intro [beat: clear] — Establish a close embrace and find a shared pulse to ground your connection.
T1: 12s [intro → main, beat: clear → clear] — when the bass kicks in, walk-step the basic on the first clear hit.
P2: 12s-35s, main ×2 [beat: clear] — Find your rhythm using a steady walk-step, letting the bass guide your weight transfers.
T2: 35s [main → build, beat: clear → clear] — commit to the new energy, travel more, and add intention.
P3: 35s-45s, build [beat: clear] — Feel the increasing energy; gradually expand your step size and movement range to build tension.
T3: 45s [build → peak, beat: clear → clear] — commit to the new energy, travel more, and add intention.
P4: 45s-62s, peak [beat: clear] — Embrace the emotional peak; use more expansive travel or varied directions to express the music.
T4: 62s [peak → main, beat: clear → clear] — settle back, breathe, and return to the basic.
P5: 62s-148s, main ×7 [beat: clear] — Maintain your momentum; keep a consistent walk-step and stay anchored to the bass line.
T5: 148s [main → main, beat: clear → moderate] — as the energy shifts, travel a little more and add intention, but since the beat becomes less obvious, shrink your steps to small weight shifts.
P6: 148s-182s, main ×3 [beat: moderate] — Focus on precision; stay compact with small steps to stay centered without chasing the subtle percussion.
T6: 182s [main → outro, beat: moderate → moderate] — as the energy fades and the percussion thins, contract your movement, slow the basic, and prepare to close.
P7: 182s-200s, outro [beat: moderate] — Wind down the dance; reduce your travel and return to minimal, gentle movements as the song fades.
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
This track lasts 267.5 seconds with a steady tempo of 89 BPM. The musical journey begins with a low-energy intro, transitions into an extended main section, moves through a brief break, reaches an emotional peak, and finally settles into a quiet outro. Throughout most of the song, the pulse is carried primarily by the bass line, providing a clear rhythmic foundation for the listener.

The most challenging moment occurs during the outro starting at 242s, where the beat clarity shifts from clear to moderate. As the energy drops and the percussiveness thins, the pulse becomes more subtle and harder to lock onto compared to the driving main sections. You may find it difficult to maintain your connection to the rhythm as the track winds down. During this final stretch, focus on feeling the underlying pulse rather than searching for a heavy beat.
```

### kizomba_tutor (one-pass)

```
P1: 0s-33s, intro [beat: clear] — The pulse is easy to follow; stay close in an embrace and just feel the steady rhythm together.
P2: 33s-164s, main ×12 [beat: clear] — As we establish the groove, trust the steady pulse to guide your walk-steps and follow the bass.
P3: 164s-181s, break [beat: clear] — The beat remains easy to hear; use this moment to reset your connection and breathe without stopping movement.
P4: 181s-192s, peak [beat: clear] — The pulse is very clear; increase your expression and travel more as we reach the emotional high point.
P5: 192s-242s, main ×5 [beat: clear] — Returning to the main groove, re-establish your steady walk-steps and let the bass guide your weight transfers.
P6: 242s-267s, outro [beat: moderate] — The pulse is a bit less defined; stay compact and test the rhythm with small, gentle steps to close the dance.
```

### kizomba_drills (verified)

```
P1: intro (0s-33s, beat: clear) — Drill: maintain a close embrace and feel the pulse together. 33s.
P2: main (33s-164s, beat: clear) — Drill: practice a steady walk-step following the bass line. 30s loop, repeated through the twelve main phases.
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
P1: intro (0s-33s, beat: clear) — Drill: maintain a close embrace and feel the pulse together. 33s.
P2-P13: main (33s-164s, beat: clear) — Drill: practice a steady walk-step following the bass line. 30s loop, repeated through the twelve main phases.
P14: break (164s-181s, beat: clear) — Drill: reduce your travel and keep a small pulse in the body. 17s during the break.
P15: peak (181s-192s, beat: clear) — Drill: increase leading variety and expression. 11s during the peak.
P16-P20: main (192s-242s, beat: clear) — Drill: same walk-step as P2-P13, but add subtle hip styling once the basic feels automatic. 30s loop, repeated through the five main phases.
P21: outro (242s-267s, beat: moderate) — Drill: keep steps small and test the pulse. 25s.
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
T1: 33s [intro → main, beat: clear → clear] — as the bass kicks in, walk-step the basic on the first clear hit.
T2: 164s [main → break, beat: clear → clear] — as the energy fades and the percussion thins, keep a small pulse in the body, listen, and reset.
T3: 181s [break → peak, beat: clear → clear] — walk-step on the first clear bass hit and commit to the new energy with more intention and travel.
T4: 192s [peak → main, beat: clear → clear] — settle back, breathe, and return to the basic steady walk.
T5: 242s [main → outro, beat: clear → moderate] — as the energy fades, contract your movement and slow the basic to prepare to close.
```

### kizomba_transitions verifier stats

```
parsed=5 boundaries_matched=5 boundaries_invented=0 boundaries_missing_filled=0 skipped_lines=0 output_lines=5
```

### kizomba_tutor (polished)

```
P1: 0s-33s, intro [beat: clear] — Use this steady rhythm to find your partner's timing; maintain a soft embrace and practice stepping together to the pulse.
P2: 33s-164s, main ×12 [beat: clear] — Lean into the groove by letting the bass guide your weight transfers; use consistent, grounded walk-steps to maintain momentum.
P3: 164s-181s, break [beat: clear] — The rhythm is still present; reduce your travel and use this moment to reset your frame and reconnect before the next phrase.
P4: 181s-192s, peak [beat: clear] — With the pulse very prominent, allow for more expansive movement and larger steps to match the increased energy.
P5: 192s-242s, main ×5 [beat: clear] — Return to a steady walking pattern, focusing on smooth weight shifts that follow the underlying bassline.
P6: 242s-267s, outro [beat: moderate] — As the rhythm softens, stay compact and avoid chasing extra percussion; use small, gentle steps to wind down the dance.
```

### unified timeline (phases + transitions)

```
P1: 0s-33s, intro [beat: clear] — Use this steady rhythm to find your partner's timing; maintain a soft embrace and practice stepping together to the pulse.
T1: 33s [intro → main, beat: clear → clear] — as the bass kicks in, walk-step the basic on the first clear hit.
P2: 33s-164s, main ×12 [beat: clear] — Lean into the groove by letting the bass guide your weight transfers; use consistent, grounded walk-steps to maintain momentum.
T2: 164s [main → break, beat: clear → clear] — as the energy fades and the percussion thins, keep a small pulse in the body, listen, and reset.
P3: 164s-181s, break [beat: clear] — The rhythm is still present; reduce your travel and use this moment to reset your frame and reconnect before the next phrase.
T3: 181s [break → peak, beat: clear → clear] — walk-step on the first clear bass hit and commit to the new energy with more intention and travel.
P4: 181s-192s, peak [beat: clear] — With the pulse very prominent, allow for more expansive movement and larger steps to match the increased energy.
T4: 192s [peak → main, beat: clear → clear] — settle back, breathe, and return to the basic steady walk.
P5: 192s-242s, main ×5 [beat: clear] — Return to a steady walking pattern, focusing on smooth weight shifts that follow the underlying bassline.
T5: 242s [main → outro, beat: clear → moderate] — as the energy fades, contract your movement and slow the basic to prepare to close.
P6: 242s-267s, outro [beat: moderate] — As the rhythm softens, stay compact and avoid chasing extra percussion; use small, gentle steps to wind down the dance.
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
This track lasts 266.1 seconds with a tempo of 89 BPM. It follows a journey that begins with a quiet intro, moves through several breaks, and enters a main section that builds into a high-energy peak before winding down through a final main phase toward the outro. Rather than a heavy drum kit, the pulse is carried primarily by melodic and harmonic content, creating a drum-light feel where the bass line provides the rhythmic foundation.

The most challenging moment occurs during the peak between 109s and 121s, where the beat clarity becomes moderate. Because the percussiveness is unusually low throughout the track, the pulse can feel subtle and may drift during these higher-energy stretches. You might also find the transitions between the clear sections and the moderate sections difficult to anchor. During the peak, don't chase the louder melodic textures; instead, feel the underlying pulse.
```

### kizomba_tutor (one-pass)

```
P1: 0s-13s, intro [beat: moderate] — The pulse is felt rather than heard; stay compact and test the rhythm with small weight shifts.
P2: 13s-43s, break ×2 [beat: clear] — The pulse is easy to find; reset your connection and use the steady rhythm to walk the basic.
P3: 43s-54s, short_break [beat: clear] — Use this brief moment to find your center and re-establish a steady walk.
P4: 54s-97s, main ×4 [beat: clear] — Establishing the groove; trust the steady pulse and focus on a smooth, even walk.
P5: 97s-109s, build [beat: clear] — Energy is climbing; increase your intention and start to travel a little more.
P6: 109s-121s, peak [beat: moderate] — The pulse is a bit more elusive; avoid chasing extra percussion and keep your movements controlled.
P7: 121s-177s, main ×5 [beat: clear] — Returning to the foundation; re-establish the basic and focus on consistent weight transfers.
P8: 177s-201s, main ×3 [beat: clear] — Sustaining the flow; keep the walk steady and focus on maintaining a solid frame.
P9: 201s-222s, main ×2 [beat: clear] — Sustaining the energy; use the clear pulse to focus on your breath and connection.
P10: 222s-255s, main ×3 [beat: clear] — Closing the main sequence; movement should begin to contract as the song winds down.
P11: 255s-266s, outro [beat: moderate] — The pulse is less obvious; stay close and use small, gentle movements to end the dance.
```

### kizomba_drills (verified)

```
P1: intro (0s-13s, beat: moderate) — Drill: keep steps tiny and test the pulse. 13s.
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
parsed=9 repaired_ranges=6 duplicate_phases=0 filled_missing=9 skipped_lines=7 output_lines=11
```

### kizomba_drills raw Gemma draft

```
P1: intro (0s-13s, beat: moderate) — Drill: keep steps tiny and test the pulse. 13s.
P2-P3: break (13s-43s, beat: clear) — Drill: reduce travel and keep a small pulse in the body. 30s.
P4: short_break (43s-54s, beat: clear) — Drill: reset your frame and reconnect with your partner. 11s.
P5-P9: main (54s-222s, beat: clear) — Drill: focus on weight transfer through a steady walk-step. 168s loop, repeated through the five main phases.
P10: peak (109s-121s, beat: moderate) — Drill: stay compact with small steps to avoid chasing extra percussion. 12s.
P11-P15: main (121s-177s, beat: clear) — Drill: same walk-step as P5-P9, but add subtle hip styling once the basic feels automatic. 56s.
P16-P18: main (177s-201s, beat: clear) — Drill: maintain the steady walk-step while increasing expression. 24s.
P19-P23: main (201s-255s, beat: clear) — Drill: keep the energy high with strong weight transfers. 54s.
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
T1: 13s [intro → break, beat: moderate → clear] — keep a small pulse in your body, listen, and reset.
T2: 43s [break → short_break, beat: clear → clear] — keep a small pulse in your body and listen.
T3: 54s [short_break → main, beat: clear → clear] — as the percussion returns, walk-step the basic on the first clear bass hit.
T4: 97s [main → build, beat: clear → clear] — commit to the new energy, travel more, and add intention.
T5: 109s [build → peak, beat: clear → moderate] — commit to the new energy and travel more; since the beat is less obvious, trust the bass line.
T6: 121s [peak → main, beat: moderate → clear] — settle back, breathe, and return to the basic.
T7: 177s [main → main, beat: clear → clear] — as the energy lifts, travel a little more and add intention.
T8: 201s [main → main, beat: clear → clear] — as the energy settles, keep the basic and hold a steady frame.
T9: 222s [main → main, beat: clear → clear] — step into your weight transfer as the percussiveness remains constant.
T10: 255s [main → outro, beat: clear → moderate] — as the energy fades and the percussion thins, contract movement and slow the basic to prepare to close.
```

### kizomba_transitions verifier stats

```
parsed=9 boundaries_matched=9 boundaries_invented=0 boundaries_missing_filled=1 skipped_lines=1 output_lines=10
```

### kizomba_transitions raw Gemma draft

```
T1: 13s [intro → break, beat: moderate → clear] — keep a small pulse in your body, listen, and reset.
T2: 43s [break → short_break, beat: clear → clear] — keep a small pulse in your body and listen.
T3: 54s [short_break → main, beat: clear → clear] — as the percussion returns, walk-step the basic on the first clear bass hit.
T4: 97s [main → build, beat: clear → clear] — commit to the new energy, travel more, and add intention.
T5: 109s [build → peak, beat: clear → moderate] — commit to the new energy and travel more; since the beat is less obvious, trust the bass line.
T6: 121s [peak → main, beat: moderate → clear] — settle back, breathe, and return to the basic.
T7: 177s [main → main, beat: clear → clear] — as the energy lifts, travel a little more and add intention.
T8: 201s [main → main, beat: clear → clear] — as the energy settles, keep the basic and hold a steady frame.
T9: 222s [main → main, beat: clear → high/medium] — as the energy lifts, travel a little more and add intention.
T10: 255s [main → outro, beat: clear → moderate] — as the energy fades and the percussion thins, contract movement and slow the basic to prepare to close.
```

### kizomba_tutor (polished)

```
P1: 0s-13s, intro [beat: moderate] — The pulse is subtle; stay compact and test the rhythm with small weight shifts.
P2: 13s-43s, break ×2 [beat: clear] — Use the steady rhythm to reset your connection and step into a controlled walk.
P3: 43s-54s, short_break [beat: clear] — Use this moment to find your center and re-establish a steady walking pace.
P4: 54s-97s, main ×4 [beat: clear] — Focus on the groove; trust the steady pulse to guide a smooth, even walk.
P5: 97s-109s, build [beat: clear] — As energy climbs, increase your intention and allow for slightly more travel.
P6: 109s-121s, peak [beat: moderate] — The pulse is more elusive; avoid chasing extra percussion and keep your movements controlled.
P7: 121s-177s, main ×5 [beat: clear] — Return to the foundation; re-establish the basic with consistent weight transfers.
P8: 177s-201s, main ×3 [beat: clear] — Sustain the flow by keeping your walk steady and your frame solid.
P9: 201s-222s, main ×2 [beat: clear] — Use the clear pulse to focus on your breath and maintain your connection.
P10: 222s-255s, main ×3 [beat: clear] — As the sequence winds down, begin to contract your movements.
P11: 255s-266s, outro [beat: moderate] — The pulse is less obvious; stay close and use small, gentle movements to finish.
```

### unified timeline (phases + transitions)

```
P1: 0s-13s, intro [beat: moderate] — The pulse is subtle; stay compact and test the rhythm with small weight shifts.
T1: 13s [intro → break, beat: moderate → clear] — keep a small pulse in your body, listen, and reset.
P2: 13s-43s, break ×2 [beat: clear] — Use the steady rhythm to reset your connection and step into a controlled walk.
T2: 43s [break → short_break, beat: clear → clear] — keep a small pulse in your body and listen.
P3: 43s-54s, short_break [beat: clear] — Use this moment to find your center and re-establish a steady walking pace.
T3: 54s [short_break → main, beat: clear → clear] — as the percussion returns, walk-step the basic on the first clear bass hit.
P4: 54s-97s, main ×4 [beat: clear] — Focus on the groove; trust the steady pulse to guide a smooth, even walk.
T4: 97s [main → build, beat: clear → clear] — commit to the new energy, travel more, and add intention.
P5: 97s-109s, build [beat: clear] — As energy climbs, increase your intention and allow for slightly more travel.
T5: 109s [build → peak, beat: clear → moderate] — commit to the new energy and travel more; since the beat is less obvious, trust the bass line.
P6: 109s-121s, peak [beat: moderate] — The pulse is more elusive; avoid chasing extra percussion and keep your movements controlled.
T6: 121s [peak → main, beat: moderate → clear] — settle back, breathe, and return to the basic.
P7: 121s-177s, main ×5 [beat: clear] — Return to the foundation; re-establish the basic with consistent weight transfers.
T7: 177s [main → main, beat: clear → clear] — as the energy lifts, travel a little more and add intention.
P8: 177s-201s, main ×3 [beat: clear] — Sustain the flow by keeping your walk steady and your frame solid.
T8: 201s [main → main, beat: clear → clear] — as the energy settles, keep the basic and hold a steady frame.
P9: 201s-222s, main ×2 [beat: clear] — Use the clear pulse to focus on your breath and maintain your connection.
T9: 222s [main → main, beat: clear → clear] — step into your weight transfer as the percussiveness remains constant.
P10: 222s-255s, main ×3 [beat: clear] — As the sequence winds down, begin to contract your movements.
T10: 255s [main → outro, beat: clear → moderate] — as the energy fades and the percussion thins, contract movement and slow the basic to prepare to close.
P11: 255s-266s, outro [beat: moderate] — The pulse is less obvious; stay close and use small, gentle movements to finish.
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
This track lasts 146.9 seconds with a steady tempo of 89 BPM. The musical journey begins with a medium-energy intro, moves into a long, fluctuating main section characterized by varying energy levels, and eventually settles into a medium-energy outro. Throughout the entire duration, the pulse is carried by a clear, steady beat that remains easy to follow, providing a consistent rhythmic foundation for the song's arc.

The challenge in this track is not a loss of clarity, but rather managing shifts in energy and rhythmic density. While the beat remains clear throughout, you will notice the percussion thins out significantly during the low-energy segment starting at 120.1 seconds. During this period, the percussiveness drops, making the pulse feel much more subtle. When you reach this section, do not chase the lighter percussion; instead, trust the bass line to guide your sense of timing.
```

### kizomba_tutor (one-pass)

```
P1: 0s-22s, intro [beat: clear] — The pulse is easy to follow; focus on connection and small weight shifts in a close embrace.
P2: 22s-49s, main ×3 [beat: clear] — Establishing the rhythm; trust the steady pulse to guide a smooth, consistent walk-step.
P3: 49s-131s, main ×8 [beat: clear] — Sustaining the movement; use the clear beat to travel more or refine your frame as the energy shifts.
P4: 131s-147s, outro [beat: clear] — Closing the dance; return to minimal movement and let the feeling end gently.
```

### kizomba_drills (verified)

```
P1: intro (0s-22s, beat: clear) — Drill: maintain a close embrace and focus on weight transfer to match the bass. 22s.
P2-P3: main (22s-131s, beat: clear) — Drill: practice a steady walk-step, letting the bass guide your movement. 27s.
P4: outro (131s-147s, beat: clear) — Drill: reduce travel and let the movement wind down. 16s.
```

### kizomba_drills verifier stats

```
parsed=8 repaired_ranges=1 duplicate_phases=0 filled_missing=1 skipped_lines=6 output_lines=3
```

### kizomba_drills raw Gemma draft

```
P1: intro (0s-22s, beat: clear) — Drill: maintain a close embrace and focus on weight transfer to match the bass. 22s.
P2-P4: main (22s-49s, beat: clear) — Drill: practice a steady walk-step, letting the bass guide your movement. 27s.
P5: main (49s-60s, beat: clear) — Drill: slow your walk to match the half-time feel. 11s.
P6-P8: main (60s-87s, beat: clear) — Drill: return to the steady walk-step, following the bass line. 27s.
P9: main (87s-98s, beat: clear) — Drill: practice a three-step pattern with a light pause to match the rhythm. 11s.
P10-P11: main (98s-120s, beat: clear) — Drill: resume the steady walk-step. 22s.
P12: main (120s-131s, beat: clear) — Drill: use a half-time feel by stepping only on the alternating pulses. 11s.
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
T1: 22s [intro → main, beat: clear → clear] — when the bass kicks in, walk-step the basic on the first clear bass hit.
T2: 49s [main → main, beat: clear → clear] — as the energy shifts, travel a little more and add intention to your movement.
T3: 131s [main → outro, beat: clear → clear] — as the energy fades and the percussion thins, contract your movement, slow the basic, and prepare to close.
```

### kizomba_transitions verifier stats

```
parsed=3 boundaries_matched=3 boundaries_invented=0 boundaries_missing_filled=0 skipped_lines=0 output_lines=3
```

### kizomba_tutor (polished)

```
P1: 0s-22s, intro [beat: clear] — Use this steady pulse to find your connection and practice small, rhythmic weight shifts within a close embrace.
P2: 22s-49s, main ×3 [beat: clear] — Establish your rhythm by using the consistent pulse to guide a smooth, grounded walk-step.
P3: 49s-131s, main ×8 [beat: clear] — Maintain your momentum; use the clear beat to increase your travel or refine your frame as the energy builds.
P4: 131s-147s, outro [beat: clear] — Wind down the dance by returning to minimal movement and letting the connection fade gently.
```

### unified timeline (phases + transitions)

```
P1: 0s-22s, intro [beat: clear] — Use this steady pulse to find your connection and practice small, rhythmic weight shifts within a close embrace.
T1: 22s [intro → main, beat: clear → clear] — when the bass kicks in, walk-step the basic on the first clear bass hit.
P2: 22s-49s, main ×3 [beat: clear] — Establish your rhythm by using the consistent pulse to guide a smooth, grounded walk-step.
T2: 49s [main → main, beat: clear → clear] — as the energy shifts, travel a little more and add intention to your movement.
P3: 49s-131s, main ×8 [beat: clear] — Maintain your momentum; use the clear beat to increase your travel or refine your frame as the energy builds.
T3: 131s [main → outro, beat: clear → clear] — as the energy fades and the percussion thins, contract your movement, slow the basic, and prepare to close.
P4: 131s-147s, outro [beat: clear] — Wind down the dance by returning to minimal movement and letting the connection fade gently.
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
This 206.6-second track moves at a steady 89 BPM. The musical journey begins with a low-energy intro and a short break, transitioning into a long main section that builds toward a high-energy peak before descending into a final main phase and a gentle outro. Because the percussiveness is unusually low, the rhythm is not driven by a heavy drum kit; instead, the melodic and harmonic content carries the pulse, making the bass line your primary guide for the rhythm.

The most challenging moment occurs during the main section between 70.0s and 96.9s, where the beat clarity becomes moderate and the pulse feels less obvious. You may find it harder to lock into the rhythm here as the percussive elements thin out. To navigate this, do not try to find a sharp percussive hit; instead, focus on the underlying pulse and trust the bass line to guide your timing.
```

### kizomba_tutor (one-pass)

```
P1: 0s-11s, intro [beat: moderate] — stay compact and test the pulse with small weight shifts to find the connection.
P2: 11s-16s, short_break [beat: moderate] — the bass pulls on the final beat of the phrase; lean into it with a weight transfer.
P3: 16s-97s, main ×7 [beat: clear] — the pulse is easy to trust; settle into a steady walk-step and follow the bass line.
P4: 97s-108s, build [beat: clear] — the music is pulling you forward; gradually increase your step size and expression.
P5: 108s-119s, peak [beat: clear] — this is the emotional high point; use stronger saídas and more leading variety.
P6: 119s-195s, main ×6 [beat: moderate] — the pulse is felt rather than heard; return to a steady walk-step and avoid chasing extra percussion.
P7: 195s-207s, outro [beat: clear] — the pulse is steady again; slow down and let the dance end gently with minimal movement.
```

### kizomba_drills (verified)

```
P1: intro (0s-11s, beat: moderate) — Drill: keep steps small and test the pulse through the bass. 11s.
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
P1: intro (0s-11s, beat: moderate) — Drill: keep steps small and test the pulse through the bass. 11s.
P2: short_break (11s-16s, beat: moderate) — Drill: reduce travel and keep a small pulse in the body. 5s.
P3-P9: main (16s-97s, beat: clear) — Drill: practice a steady walk-step focusing on weight transfer. 81s loop, repeated through the four main phases.
P10: build (97s-108s, beat: clear) — Drill: increase step size and expression to build tension. 11s.
P11: peak (108s-119s, beat: clear) — Drill: use stronger saídas and more leading variety. 11s.
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
T2: 16s [short_break → main, beat: moderate → clear] — when the bass kicks in, walk-step the basic on the first clear hit.
T3: 97s [main → build, beat: clear → clear] — as the energy lifts, travel a little more and add intention.
T4: 108s [build → peak, beat: clear → clear] — commit to the new energy with stronger saídas and more expression.
T5: 119s [peak → main, beat: clear → moderate] — as the energy fades, settle back, breathe, and return to the basic.
T6: 195s [main → outro, beat: moderate → clear] — as the energy fades, contract your movement, slow the basic, and prepare to close.
```

### kizomba_transitions verifier stats

```
parsed=6 boundaries_matched=6 boundaries_invented=0 boundaries_missing_filled=0 skipped_lines=0 output_lines=6
```

### kizomba_tutor (polished)

```
P1: 0s-11s, intro [beat: moderate] — stay compact and use small weight shifts to find the connection.
P2: 11s-16s, short_break [beat: moderate] — use the final beat to complete a weight transfer and reset your frame.
P3: 16s-97s, main ×7 [beat: clear] — use this stable pulse to settle into a steady walk-step and follow the bass.
P4: 97s-108s, build [beat: clear] — use the momentum to gradually increase your step size and energy.
P5: 108s-119s, peak [beat: clear] — lean into the energy with larger travel or more varied leading.
P6: 119s-195s, main ×6 [beat: moderate] — return to a steady walk-step and keep your movements compact to avoid chasing extra percussion.
P7: 195s-207s, outro [beat: clear] — use the steady pulse to slow your steps and let the dance end gently.
```

### unified timeline (phases + transitions)

```
P1: 0s-11s, intro [beat: moderate] — stay compact and use small weight shifts to find the connection.
T1: 11s [intro → short_break, beat: moderate → moderate] — keep a small pulse in the body, listen, and reset.
P2: 11s-16s, short_break [beat: moderate] — use the final beat to complete a weight transfer and reset your frame.
T2: 16s [short_break → main, beat: moderate → clear] — when the bass kicks in, walk-step the basic on the first clear hit.
P3: 16s-97s, main ×7 [beat: clear] — use this stable pulse to settle into a steady walk-step and follow the bass.
T3: 97s [main → build, beat: clear → clear] — as the energy lifts, travel a little more and add intention.
P4: 97s-108s, build [beat: clear] — use the momentum to gradually increase your step size and energy.
T4: 108s [build → peak, beat: clear → clear] — commit to the new energy with stronger saídas and more expression.
P5: 108s-119s, peak [beat: clear] — lean into the energy with larger travel or more varied leading.
T5: 119s [peak → main, beat: clear → moderate] — as the energy fades, settle back, breathe, and return to the basic.
P6: 119s-195s, main ×6 [beat: moderate] — return to a steady walk-step and keep your movements compact to avoid chasing extra percussion.
T6: 195s [main → outro, beat: moderate → clear] — as the energy fades, contract your movement, slow the basic, and prepare to close.
P7: 195s-207s, outro [beat: clear] — use the steady pulse to slow your steps and let the dance end gently.
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
This track lasts 251.8 seconds with a tempo of 92 BPM. It follows a structural arc that begins with a subtle intro, moves into an extended main section, transitions into a low-energy break, returns to a high-energy main phase, and eventually settles into a medium-energy outro. Because the percussiveness is unusually low, the rhythm is drum-light; instead of a heavy percussive grid, the melodic and harmonic content carries the pulse, making the bass line your primary guide for the journey.

The most challenging moment occurs during the intro (0s–25s) and the break (168s–184s), where the beat is described as subtle or moderate rather than clear. During these windows, the pulse is felt rather than heard, and you may find it difficult to anchor your timing as the percussion thins out. The transition from the intro into the first main phase is particularly tricky because the beat clarity shifts from subtle to clear. To navigate these dips, trust the bass line through the break and focus on the underlying pulse.
```

### kizomba_tutor (one-pass)

```
P1: 0s-25s, intro [beat: subtle] — The pulse is felt rather than heard; keep movement very small and just find a tiny weight shift to stay connected.
P2: 25s-168s, main ×13 [beat: clear] — As we begin establishing the rhythm, trust the steady pulse and use a smooth walk-step to settle into the groove.
P3: 168s-184s, break [beat: moderate] — The beat is less obvious here; stay compact and test the pulse with small steps to avoid chasing the rhythm.
P4: 184s-210s, main ×2 [beat: clear] — Now returning to the music, re-establish your connection and use the clear pulse to guide your walk.
P5: 210s-237s, main ×3 [beat: clear] — While sustaining the energy, keep your frame steady and let the bass line drive your movement.
P6: 237s-252s, outro [beat: clear] — As the song winds down, contract your movement and let the dance end gently with the fading pulse.
```

### kizomba_drills (verified)

```
P1: intro (0s-25s, beat: subtle) — Drill: mark the pulse with a tiny shoulder bounce. 25s.
P2: main (25s-168s, beat: clear) — Drill: focus on weight transfer during a steady walk-step. 143s loop, repeated through the main phases.
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
P1: intro (0s-25s, beat: subtle) — Drill: mark the pulse with a tiny shoulder bounce. 25s.
P2-P14: main (25s-168s, beat: clear) — Drill: focus on weight transfer during a steady walk-step. 143s loop, repeated through the main phases.
P15: break (168s-184s, beat: moderate) — Drill: reduce travel and keep a small pulse in the body. 16s.
P16-P20: main (184s-237s, beat: clear) — Drill: same walk-step as P2-P14, but now add subtle hip styling once the basic feels automatic. 53s loop.
P21: outro (237s-252s, beat: clear) — Drill: slow the pace and return to minimal movement. 15s.
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
T1: 25s [intro → main, beat: subtle → clear] — when the bass kicks in, walk-step the basic on the first clear hit.
T2: 168s [main → break, beat: clear → moderate] — as the energy fades and the percussion thins, keep a small pulse in the body, listen, and reset.
T3: 184s [break → main, beat: moderate → clear] — when the bass kicks in, walk-step on the first clear hit rather than chasing the loudest percussion.
T4: 210s [main → main, beat: clear → clear] — as the energy shifts, travel a little more and add intention to your steps.
T5: 237s [main → outro, beat: clear → clear] — as the energy fades, contract your movement and slow the basic to prepare to close.
```

### kizomba_transitions verifier stats

```
parsed=5 boundaries_matched=5 boundaries_invented=0 boundaries_missing_filled=0 skipped_lines=0 output_lines=5
```

### kizomba_tutor (polished)

```
P1: 0s-25s, intro [beat: subtle] — The pulse is felt rather than heard; keep your movement minimal and use tiny weight shifts to stay connected.
P2: 25s-168s, main ×13 [beat: clear] — As the rhythm establishes, trust the steady pulse and use a smooth, grounded walk to settle into the groove.
P3: 168s-184s, break [beat: moderate] — The beat becomes less obvious; stay compact and use small steps to find the pulse without chasing extra percussion.
P4: 184s-210s, main ×2 [beat: clear] — Returning to the music, re-establish your connection and use the clear pulse to guide your walking steps.
P5: 210s-237s, main ×3 [beat: clear] — While sustaining the energy, keep your frame steady and let the bass line drive your weight transfers.
P6: 237s-252s, outro [beat: clear] — As the song winds down, reduce your travel and let the dance end gently with the fading pulse.
```

### unified timeline (phases + transitions)

```
P1: 0s-25s, intro [beat: subtle] — The pulse is felt rather than heard; keep your movement minimal and use tiny weight shifts to stay connected.
T1: 25s [intro → main, beat: subtle → clear] — when the bass kicks in, walk-step the basic on the first clear hit.
P2: 25s-168s, main ×13 [beat: clear] — As the rhythm establishes, trust the steady pulse and use a smooth, grounded walk to settle into the groove.
T2: 168s [main → break, beat: clear → moderate] — as the energy fades and the percussion thins, keep a small pulse in the body, listen, and reset.
P3: 168s-184s, break [beat: moderate] — The beat becomes less obvious; stay compact and use small steps to find the pulse without chasing extra percussion.
T3: 184s [break → main, beat: moderate → clear] — when the bass kicks in, walk-step on the first clear hit rather than chasing the loudest percussion.
P4: 184s-210s, main ×2 [beat: clear] — Returning to the music, re-establish your connection and use the clear pulse to guide your walking steps.
T4: 210s [main → main, beat: clear → clear] — as the energy shifts, travel a little more and add intention to your steps.
P5: 210s-237s, main ×3 [beat: clear] — While sustaining the energy, keep your frame steady and let the bass line drive your weight transfers.
T5: 237s [main → outro, beat: clear → clear] — as the energy fades, contract your movement and slow the basic to prepare to close.
P6: 237s-252s, outro [beat: clear] — As the song winds down, reduce your travel and let the dance end gently with the fading pulse.
```
