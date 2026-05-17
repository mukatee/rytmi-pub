# 09_kizomba batch outputs - model=google/gemma-4-26b-a4b-it

sources: eval_set=11, extended_set=6

## kizomba - rhythm_anatomy (genre intro)

```
Kizomba typically operates within a tempo range of 85-110 BPM in a 4/4 time signature. Rather than a heavy percussive grid, the rhythmic pulse is often carried by the bass line, which provides the primary driver for movement. The rhythm is characterized by a smooth, flowing feel where the pulse is felt through the bass rather than through sharp drum hits. A standard track follows a structural arc consisting of an intro, main sections, builds, peaks, occasional breaks, and an outro.

You may encounter various sub-styles, such as the slower, more grounded feel of Angolan kizomba or the more polished, melodic textures of urbankiz. Tarraxinha offers a distinctively different rhythmic character, often focusing on a more concentrated, slower pulse. Semba provides a more energetic and traditional rhythmic foundation. Use these variations in tempo and texture as hints to help you place the rhythmic character of a track as you listen.
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
This 252.2-second track moves at a tempo of 83 BPM, which is slower than the typical kizomba range. The musical journey begins with a low-energy intro, transitions into several main sections, builds tension through a build phase into a high-energy peak, and eventually moves through a break and an outro. Because the percussiveness is unusually low, the rhythm is not driven by a heavy drum kit; instead, the melodic and harmonic content carries the pulse, making the rhythm feel drum-light and driven by the bass line.

The most challenging moment for maintaining the pulse occurs during the intro from 0s to 20s, where the beat is only moderate and the percussiveness is very low. You may find it difficult to anchor your sense of time here because the pulse is felt through the bass rather than being clearly defined by percussion. Another point of interest is the peak at 107s, where the rhythm becomes more complex. During these transitions, do not chase the busier rhythmic layers; instead, feel the underlying pulse.
```

### kizomba_tutor (one-pass)

```
P1: 0s-20s, intro [beat: moderate] — The pulse is felt rather than heard; stay compact and test the pulse with small weight shifts.
P2: 20s-90s, main ×6 [beat: clear] — Establishing the foundation; trust the steady pulse to walk the basic and settle into the rhythm.
P3: 90s-107s, build [beat: clear] — Building tension; gradually increase your step size and intention as the music pulls you forward.
P4: 107s-118s, peak [beat: clear] — The emotional high point; use the clear pulse to add more expression and variety to your movement.
P5: 118s-175s, main ×4 [beat: clear] — Returning to the flow; re-establish the basic walk and focus on smooth weight transfers.
P6: 175s-188s, break [beat: clear] — A moment to reset; reduce your travel and keep a small, steady pulse in the body.
P7: 188s-217s, main ×3 [beat: clear] — Reconnecting with the music; find the rhythm again and let the bass guide your steps.
P8: 217s-240s, main ×2 [beat: clear] — Closing the phrase; keep your movement controlled and contract as the song winds down.
P9: 240s-252s, outro [beat: clear] — Ending gently; return to minimal movement and let the dance fade out naturally.
```

### kizomba_drills (verified)

```
P1: intro (0s-20s, beat: moderate) — Drill: keep steps small and test the pulse through the bass. 20s.
P2: main (20s-90s, beat: clear) — Drill: practice a steady walk-step focusing on weight transfer. 30s loop, repeated through the main phases. 69.8s.
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
P1: intro (0s-20s, beat: moderate) — Drill: keep steps small and test the pulse through the bass. 20s.
P2-P7: main (20s-89.8s, beat: clear) — Drill: practice a steady walk-step focusing on weight transfer. 30s loop, repeated through the main phases. 69.8s.
P8: build (89.8s-106.9s, beat: clear) — Drill: gradually increase step size and expression. 17.1s.
P9: peak (106.9s-118.4s, beat: clear) — Drill: execute a three-step pattern with a light pause. 11.5s.
P10-P13: main (118.4s-175.1s, beat: clear) — Drill: same walk-step as P2-P7, focusing on hips. 30s loop, repeated through the main phases. 56.7s.
P14: break (175.1s-187.6s, beat: clear) — Drill: reduce travel and keep a small pulse in the body. 12.5s.
P15-P19: main (187.6s-239.8s, beat: clear) — Drill: same walk-step as P2-P7, but now add subtle hip styling once the basic feels automatic. 30s loop, repeated through the main phases. 52.2s.
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
T3: 107s [build → peak, beat: clear → clear] — as the energy rises, add intention and more expression to your movement.
T4: 118s [peak → main, beat: clear → clear] — settle back, breathe, and return to a steady basic.
T5: 175s [main → break, beat: clear → clear] — as the energy fades and the percussion thins, keep a small pulse in the body, listen, and reset.
T6: 188s [break → main, beat: clear → clear] — walk-step on the first clear bass hit; don't chase the loudest percussion.
T7: 217s [main → main, beat: clear → clear] — as the energy settles, keep the basic and hold a steady frame.
T8: 240s [main → outro, beat: clear → clear] — as the energy fades, contract your movement and slow the basic to prepare to close.
```

### kizomba_transitions verifier stats

```
parsed=8 boundaries_matched=8 boundaries_invented=0 boundaries_missing_filled=0 skipped_lines=0 output_lines=8
```

### kizomba_tutor (polished)

```
P1: 0s-20s, intro [beat: moderate] — The pulse is subtle; stay compact and use small weight shifts to find the rhythm.
P2: 20s-90s, main ×6 [beat: clear] — Establish your foundation; use the steady pulse to ground your walk and settle into the rhythm.
P3: 90s-107s, build [beat: clear] — Building tension; gradually increase your step size and intention as the music pulls you forward.
P4: 107s-118s, peak [beat: clear] — The emotional high point; use the clear pulse to add more expression and movement variety.
P5: 118s-175s, main ×4 [beat: clear] — Returning to the flow; re-establish your basic walk and focus on smooth weight transfers.
P6: 175s-188s, break [beat: clear] — A moment to reset; reduce your travel and keep a small, steady pulse in the body.
P7: 188s-217s, main ×3 [beat: clear] — Reconnecting with the music; find the rhythm again and let the bass guide your steps.
P8: 217s-240s, main ×2 [beat: clear] — Closing the phrase; keep your movement controlled and focus on grounded, intentional steps.
P9: 240s-252s, outro [beat: clear] — Ending gently; return to minimal movement and let the dance fade out naturally.
```

### unified timeline (phases + transitions)

```
P1: 0s-20s, intro [beat: moderate] — The pulse is subtle; stay compact and use small weight shifts to find the rhythm.
T1: 20s [intro → main, beat: moderate → clear] — when the bass kicks in, walk-step the basic on the first clear hit.
P2: 20s-90s, main ×6 [beat: clear] — Establish your foundation; use the steady pulse to ground your walk and settle into the rhythm.
T2: 90s [main → build, beat: clear → clear] — as the energy shifts, commit to the new energy and travel more.
P3: 90s-107s, build [beat: clear] — Building tension; gradually increase your step size and intention as the music pulls you forward.
T3: 107s [build → peak, beat: clear → clear] — as the energy rises, add intention and more expression to your movement.
P4: 107s-118s, peak [beat: clear] — The emotional high point; use the clear pulse to add more expression and movement variety.
T4: 118s [peak → main, beat: clear → clear] — settle back, breathe, and return to a steady basic.
P5: 118s-175s, main ×4 [beat: clear] — Returning to the flow; re-establish your basic walk and focus on smooth weight transfers.
T5: 175s [main → break, beat: clear → clear] — as the energy fades and the percussion thins, keep a small pulse in the body, listen, and reset.
P6: 175s-188s, break [beat: clear] — A moment to reset; reduce your travel and keep a small, steady pulse in the body.
T6: 188s [break → main, beat: clear → clear] — walk-step on the first clear bass hit; don't chase the loudest percussion.
P7: 188s-217s, main ×3 [beat: clear] — Reconnecting with the music; find the rhythm again and let the bass guide your steps.
T7: 217s [main → main, beat: clear → clear] — as the energy settles, keep the basic and hold a steady frame.
P8: 217s-240s, main ×2 [beat: clear] — Closing the phrase; keep your movement controlled and focus on grounded, intentional steps.
T8: 240s [main → outro, beat: clear → clear] — as the energy fades, contract your movement and slow the basic to prepare to close.
P9: 240s-252s, outro [beat: clear] — Ending gently; return to minimal movement and let the dance fade out naturally.
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
This 270.6-second track runs at a slower 81 BPM than typical kizomba. The musical journey begins with a low-energy intro, transitions into an extended main section, encounters a brief break, and eventually settles into a gentle outro. Because the percussiveness is unusually low, the rhythm is not driven by a heavy drum kit; instead, the pulse is carried primarily by the melodic and harmonic content, with the bass line providing the essential rhythmic foundation.

The most challenging moment occurs during the break from 193s to 205s, where the beat clarity becomes moderate and the percussion thins out significantly. You may also find the high-energy main sections difficult to track because the onset density is unusually high, creating tight syncopation and ornamentation that can feel cluttered. To navigate these shifts, especially during the break, do not chase the ornamentation; instead, trust the bass line to find the underlying pulse.
```

### kizomba_tutor (one-pass)

```
P1: 0s-15s, intro [beat: clear] — Find the connection with a slow, steady pulse; use small weight shifts to feel the bass together.
P2: 15s-138s, main ×10 [beat: clear] — Establishing the rhythm; it is safe to trust the steady pulse and walk the basic with more travel.
P3: 138s-193s, main ×4 [beat: moderate] — Sustaining the energy; stay compact and test the pulse with small steps to avoid chasing the ornamentation.
P4: 193s-205s, break [beat: moderate] — A moment to reset; reduce travel and keep a small pulse in the body to prepare for what's next.
P5: 205s-252s, main ×5 [beat: clear] — Returning to the flow; the pulse is clear again, so you can re-establish your walk-step and follow the bass.
P6: 252s-271s, outro [beat: moderate] — Closing the dance; stay compact and let the movement contract as the song winds down.
```

### kizomba_drills (verified)

```
P1: intro (0s-15s, beat: clear) — Drill: maintain a close embrace and focus on weight transfer. 15s.
P2: main (15s-138s, beat: clear) — Drill: practice a steady walk-step following the bass line. 30s loop, repeated through the ten main phases.
P3: main (138s-193s, beat: moderate) — Drill: stay compact and test the pulse with small steps. 55s.
P4: break (193s-205s, beat: moderate) — Drill: reduce travel and keep a small pulse in the body to reset. 11s.
P5: main (205s-252s, beat: clear) — Drill: practice steady weight transfers through this section. 47s.
P6: outro (252s-271s, beat: moderate) — Drill: reduce travel and let the movement wind down. 19s.
```

### kizomba_drills verifier stats

```
parsed=6 repaired_ranges=2 duplicate_phases=0 filled_missing=4 skipped_lines=4 output_lines=6
```

### kizomba_drills raw Gemma draft

```
P1: intro (0s-15s, beat: clear) — Drill: maintain a close embrace and focus on weight transfer. 15s.
P2-P11: main (15s-138s, beat: clear) — Drill: practice a steady walk-step following the bass line. 30s loop, repeated through the ten main phases.
P12-P15: main (138s-193s, beat: moderate) — Drill: keep steps small and stay compact to avoid chasing the ornamentation. 55s.
P16: break (193s-205s, beat: moderate) — Drill: reduce travel and keep a small pulse in the body. 12s.
P17-P21: main (205s-252s, beat: clear) — Drill: same walk-step as P2-P11, but add subtle hip styling once the basic feels automatic. 30s loop, repeated through the five main phases.
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
T1: 15s [intro → main, beat: clear → clear] — when the bass kicks in, walk-step the basic on the first clear hit.
T2: 138s [main → main, beat: clear → moderate] — as the energy lifts, travel a little more and add intention.
T3: 193s [main → break, beat: moderate → moderate] — as the energy fades and the percussion thins, keep a small pulse in the body, listen, and reset.
T4: 205s [break → main, beat: moderate → clear] — walk-step on the first clear bass hit; don't chase the percussion that comes back loudest.
T5: 252s [main → outro, beat: clear → moderate] — as the energy fades, contract your movement, slow the basic, and prepare to close.
```

### kizomba_transitions verifier stats

```
parsed=5 boundaries_matched=5 boundaries_invented=0 boundaries_missing_filled=0 skipped_lines=0 output_lines=5
```

### kizomba_tutor (polished)

```
P1: 0s-15s, intro [beat: clear] — Establish your connection with a slow, steady pulse; use small weight shifts to feel the bass together.
P2: 15s-138s, main ×10 [beat: clear] — Build your rhythm; trust the steady pulse and use the clarity to step through your walk with more travel.
P3: 138s-193s, main ×4 [beat: moderate] — Sustain your energy; stay compact and use small steps to stay grounded without chasing the extra ornamentation.
P4: 193s-205s, break [beat: moderate] — A moment to reset; reduce your travel and keep a small pulse in the body to prepare for the next phase.
P5: 205s-252s, main ×5 [beat: clear] — Return to the flow; use the clear pulse to re-establish your walk-step and follow the bass.
P6: 252s-271s, outro [beat: moderate] — Close the dance; stay compact and let your movements contract as the song winds down.
```

### unified timeline (phases + transitions)

```
P1: 0s-15s, intro [beat: clear] — Establish your connection with a slow, steady pulse; use small weight shifts to feel the bass together.
T1: 15s [intro → main, beat: clear → clear] — when the bass kicks in, walk-step the basic on the first clear hit.
P2: 15s-138s, main ×10 [beat: clear] — Build your rhythm; trust the steady pulse and use the clarity to step through your walk with more travel.
T2: 138s [main → main, beat: clear → moderate] — as the energy lifts, travel a little more and add intention.
P3: 138s-193s, main ×4 [beat: moderate] — Sustain your energy; stay compact and use small steps to stay grounded without chasing the extra ornamentation.
T3: 193s [main → break, beat: moderate → moderate] — as the energy fades and the percussion thins, keep a small pulse in the body, listen, and reset.
P4: 193s-205s, break [beat: moderate] — A moment to reset; reduce your travel and keep a small pulse in the body to prepare for the next phase.
T4: 205s [break → main, beat: moderate → clear] — walk-step on the first clear bass hit; don't chase the percussion that comes back loudest.
P5: 205s-252s, main ×5 [beat: clear] — Return to the flow; use the clear pulse to re-establish your walk-step and follow the bass.
T5: 252s [main → outro, beat: clear → moderate] — as the energy fades, contract your movement, slow the basic, and prepare to close.
P6: 252s-271s, outro [beat: moderate] — Close the dance; stay compact and let your movements contract as the song winds down.
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
This 314.1-second track moves at a steady 108 BPM. The musical journey begins with a low-energy intro, transitions into a long, evolving main section, and builds through instrumental passages toward a high-energy peak. From there, the energy settles back into a medium-intensity main section before concluding with a gentle outro. Throughout the track, the pulse is felt through the bass line rather than a heavy percussive grid, creating a smooth, flowing atmosphere.

The beat remains clear for the majority of the song, but the hardest moment occurs during the high-energy instrumental and peak phases between 212s and 233s. During this stretch, the density of musical onsets increases significantly, which can make the underlying pulse feel more complex to track. While the beat remains easy to follow, the sudden influx of rhythmic activity might tempt you to over-analyze the surface layers. During this peak, don't chase the louder percussion; instead, feel the underlying pulse.
```

### kizomba_tutor (one-pass)

```
P1: 0s-18s, intro [beat: clear] — Focus on connection and minimal movement; just feel the steady pulse together.
P2: 18s-172s, main ×13 [beat: clear] — Establishing the foundation; use a steady walk-step and let the bass guide your movement.
P3: 172s-195s, instrumental ×2 [beat: clear] — Maintain your flow; keep the pulse steady as the music shifts.
P4: 195s-212s, main [beat: clear] — Sustaining the energy; focus on smooth weight transfers while following the bass.
P5: 212s-228s, instrumental [beat: clear] — Building intensity; you can travel more and add more intention to your steps.
P6: 228s-233s, peak [beat: clear] — The emotional high point; use more expression and variety in your leading.
P7: 233s-265s, main ×3 [beat: clear] — Returning to the basics; re-establish the walk-step and reconnect with your partner.
P8: 265s-302s, main ×3 [beat: clear] — Closing the song; contract your movement and wind down the energy.
P9: 302s-314s, outro [beat: clear] — Let the dance end gently by returning to minimal, quiet movement.
```

### kizomba_drills (verified)

```
P1: intro (0s-18s, beat: clear) — Drill: maintain a close embrace and feel the pulse through the bass. 18s.
P2: main (18s-172s, beat: clear) — Drill: practice a steady walk-step, matching your weight transfer to the bass line. 30s loop, repeated through the phase. 87.9s.
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
P1: intro (0s-18s, beat: clear) — Drill: maintain a close embrace and feel the pulse through the bass. 18s.
P2-P10: main (18s-105.9s, beat: clear) — Drill: practice a steady walk-step, matching your weight transfer to the bass line. 30s loop, repeated through the phase. 87.9s.
P11: main (105.9s-141.6s, beat: clear) — Drill: lean into the weight transfer as the bass pulls on the off-beat. 35.7s.
P12-P17: main (141.6s-211.6s, beat: clear) — Drill: same walk-step as P2-P10, but now add subtle hip styling once the basic feels automatic. 70s.
P18-P19: instrumental (211.6s-232.8s, beat: clear) — Drill: focus on a slow, controlled walk to match the half-time feel. 21.2s.
P20: peak (228.1s-232.8s, beat: clear) — Drill: increase expression through more varied leading. 4.7s.
P21-P22: main (232.8s-265.2s, beat: clear) — Drill: use strong weight transfers on the primary pulse followed by lighter steps. 32.4s.
P23-P25: main (265.2s-301.6s, beat: clear) — Drill: same walk-step as P2-P10, but keep the energy high from the previous peak. 36.4s.
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
T2: 172s [main → instrumental, beat: clear → clear] — keep your basic going steadily through this instrumental section.
T3: 195s [instrumental → main, beat: clear → clear] — keep your basic going steadily.
T4: 212s [main → instrumental, beat: clear → clear] — keep your basic going steadily as the energy lifts.
T5: 228s [instrumental → peak, beat: clear → clear] — commit to the new energy and travel more.
T6: 233s [peak → main, beat: clear → clear] — settle back, breathe, and return to the basic as the energy levels out.
T7: 265s [main → main, beat: clear → clear] — as the energy settles, keep the basic and hold a steady frame.
T8: 302s [main → outro, beat: clear → clear] — as the energy fades and the percussion thins, contract your movement and prepare to close.
```

### kizomba_transitions verifier stats

```
parsed=8 boundaries_matched=8 boundaries_invented=0 boundaries_missing_filled=0 skipped_lines=0 output_lines=8
```

### kizomba_tutor (polished)

```
P1: 0s-18s, intro [beat: clear] — Find your connection and use the steady pulse to ground your weight.
P2: 18s-172s, main ×13 [beat: clear] — Build your foundation with a steady walk-step, letting the bass drive your momentum.
P3: 172s-195s, instrumental ×2 [beat: clear] — Maintain your rhythmic flow; keep your steps consistent as the texture shifts.
P4: 195s-212s, main [beat: clear] — Sustain the energy through smooth, controlled weight transfers.
P5: 212s-228s, instrumental [beat: clear] — Increase your travel and add more intention to your direction.
P6: 228s-233s, peak [beat: clear] — Express the music's intensity through larger movements or more varied leading.
P7: 233s-265s, main ×3 [beat: clear] — Return to your core walk-step and re-center your connection.
P8: 265s-302s, main ×3 [beat: clear] — Wind down the energy by tightening your frame and reducing your travel.
P9: 302s-314s, outro [beat: clear] — End gently by returning to small, quiet movements.
```

### unified timeline (phases + transitions)

```
P1: 0s-18s, intro [beat: clear] — Find your connection and use the steady pulse to ground your weight.
T1: 18s [intro → main, beat: clear → clear] — when the bass kicks in, walk-step the basic on the first clear hit.
P2: 18s-172s, main ×13 [beat: clear] — Build your foundation with a steady walk-step, letting the bass drive your momentum.
T2: 172s [main → instrumental, beat: clear → clear] — keep your basic going steadily through this instrumental section.
P3: 172s-195s, instrumental ×2 [beat: clear] — Maintain your rhythmic flow; keep your steps consistent as the texture shifts.
T3: 195s [instrumental → main, beat: clear → clear] — keep your basic going steadily.
P4: 195s-212s, main [beat: clear] — Sustain the energy through smooth, controlled weight transfers.
T4: 212s [main → instrumental, beat: clear → clear] — keep your basic going steadily as the energy lifts.
P5: 212s-228s, instrumental [beat: clear] — Increase your travel and add more intention to your direction.
T5: 228s [instrumental → peak, beat: clear → clear] — commit to the new energy and travel more.
P6: 228s-233s, peak [beat: clear] — Express the music's intensity through larger movements or more varied leading.
T6: 233s [peak → main, beat: clear → clear] — settle back, breathe, and return to the basic as the energy levels out.
P7: 233s-265s, main ×3 [beat: clear] — Return to your core walk-step and re-center your connection.
T7: 265s [main → main, beat: clear → clear] — as the energy settles, keep the basic and hold a steady frame.
P8: 265s-302s, main ×3 [beat: clear] — Wind down the energy by tightening your frame and reducing your travel.
T8: 302s [main → outro, beat: clear → clear] — as the energy fades and the percussion thins, contract your movement and prepare to close.
P9: 302s-314s, outro [beat: clear] — End gently by returning to small, quiet movements.
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
This 301.0-second track moves at a steady 92 BPM, following an arc that begins with a low-energy intro, transitions into several main phases of varying energy, reaches a high-energy peak around 158s, and eventually settles into a low-energy outro. Because the percussiveness is unusually low, the rhythm is not driven by a heavy drum kit; instead, the melodic and harmonic content carries the pulse, making the music feel drum-light.

The primary challenge will be maintaining a connection to the pulse during sections where the beat is only moderate or subtle. The hardest moment occurs during the outro starting at 287s, where the beat becomes subtle and the rhythm thins out significantly. You may also find the pulse difficult to lock onto during the main sections where the rhythm feels syncopated or the beat clarity is moderate. Throughout the track, the pulse is often felt through the bass rather than heard through sharp percussion. When the rhythm thins out toward the end, trust the bass line to guide you.
```

### kizomba_tutor (one-pass)

```
P1: 0s-29s, intro [beat: moderate] — Find the connection in a close embrace and just feel the pulse together.
P2: 29s-65s, main ×3 [beat: moderate] — Establishing the groove; use small steps to test the pulse and follow the bass.
P3: 65s-158s, main ×8 [beat: moderate] — Sustaining the movement; keep a steady walk and let the bass guide your weight transfers.
P4: 158s-165s, peak [beat: moderate] — This is the emotional high point; add more expression and variety to your leading.
P5: 165s-248s, main ×7 [beat: moderate] — Returning to the basics; reconnect with your partner and maintain a steady, compact walk.
P6: 248s-287s, main ×4 [beat: moderate] — Closing the dance; contract your movement and prepare to wind down.
P7: 287s-301s, outro [beat: subtle] — The pulse is hard to lock onto; make your movements very small and let the dance end gently.
```

### kizomba_drills (verified)

```
P1: intro (0s-29s, beat: moderate) — Drill: maintain a close embrace and feel the pulse through the bass. 29s.
P2-P3: main (29s-158s, beat: moderate) — Drill: practice small walk-steps, following the bass line without chasing extra percussion. 35.5s.
P4: peak (158s-165s, beat: moderate) — Drill: stay compact and test the pulse with small steps. 7s.
P5-P6: main (165s-287s, beat: moderate) — Drill: execute a steady walk-step, letting the bass guide each step. 30s loop, repeated through the three main phases. 93.3s.
P7: outro (287s-301s, beat: subtle) — Drill: reduce travel and let the movement wind down. 14s.
```

### kizomba_drills verifier stats

```
parsed=10 repaired_ranges=3 duplicate_phases=0 filled_missing=2 skipped_lines=7 output_lines=5
```

### kizomba_drills raw Gemma draft

```
P1: intro (0s-29s, beat: moderate) — Drill: maintain a close embrace and feel the pulse through the bass. 29s.
P2-P4: main (29s-64.5s, beat: moderate) — Drill: practice small walk-steps, following the bass line without chasing extra percussion. 35.5s.
P5-P12: main (64.5s-157.8s, beat: moderate) — Drill: execute a steady walk-step, letting the bass guide each step. 30s loop, repeated through the three main phases. 93.3s.
P13: peak (157.8s-164.7s, beat: moderate) — Drill: increase leading variety and expression in your frame. 6.9s.
P14-P15: main (164.7s-186.4s, beat: moderate) — Drill: same walk-step as P5-P12, but add subtle hip styling once the basic feels automatic. 21.7s.
P16-P17: main (186.4s-208.7s, beat: moderate) — Drill: slow your walking pace to match the half-time feel. 22.3s.
P18-P22: main (208.7s-287.5s, beat: moderate) — Drill: keep the pulse in your body and focus on weight transfer during syncopated moments. 78.8s.
P23: main (264.1s-277.4s, beat: moderate) — Drill: practice a three-step pattern with a pause. 13.3s.
P24: main (277.4s-287.5s, beat: moderate) — Drill: return to a steady walk-step. 10.1s.
P25: outro (287.5s-301.0s, beat: subtle) — Drill: stand still and mark the pulse with a tiny shoulder bounce. 13.5s.
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
T1: 29s [intro → main, beat: moderate → moderate] — when the bass kicks in, walk-step the basic on the first clear bass hit.
T2: 65s [main → main, beat: moderate → moderate] — as the energy lifts, travel a little more and add intention to your movement.
T3: 158s [main → peak, beat: moderate → moderate] — commit to the new energy, travel more, and add intention.
T4: 165s [peak → main, beat: moderate → moderate] — settle back, breathe, and return to the basic.
T5: 248s [main → main, beat: moderate → moderate] — as the energy lifts, travel a little more and add intention.
T6: 287s [main → outro, beat: moderate → subtle] — as the energy fades and the percussion thins, contract your movement and slow the basic, marking the subtle pulse with tiny weight shifts.
```

### kizomba_transitions verifier stats

```
parsed=6 boundaries_matched=6 boundaries_invented=0 boundaries_missing_filled=0 skipped_lines=0 output_lines=6
```

### kizomba_tutor (polished)

```
P1: 0s-29s, intro [beat: moderate] — Focus on finding a soft connection in a close embrace and feeling the shared pulse.
P2: 29s-65s, main ×3 [beat: moderate] — Start establishing your groove; use small, controlled steps to test the rhythm and follow the bass.
P3: 65s-158s, main ×8 [beat: moderate] — Maintain your momentum; keep a steady walk and let the bass guide your weight transfers.
P4: 158s-165s, peak [beat: moderate] — Use this moment to add more expression; try subtle variations in your connection or frame.
P5: 165s-248s, main ×7 [beat: moderate] — Return to your foundation; reconnect with your partner and maintain a steady, compact walk.
P6: 248s-287s, main ×4 [beat: moderate] — Begin to wind down; reduce your travel and keep your movements contained.
P7: 287s-301s, outro [beat: subtle] — The pulse is much softer; keep your movements very small and let the dance end gently.
```

### unified timeline (phases + transitions)

```
P1: 0s-29s, intro [beat: moderate] — Focus on finding a soft connection in a close embrace and feeling the shared pulse.
T1: 29s [intro → main, beat: moderate → moderate] — when the bass kicks in, walk-step the basic on the first clear bass hit.
P2: 29s-65s, main ×3 [beat: moderate] — Start establishing your groove; use small, controlled steps to test the rhythm and follow the bass.
T2: 65s [main → main, beat: moderate → moderate] — as the energy lifts, travel a little more and add intention to your movement.
P3: 65s-158s, main ×8 [beat: moderate] — Maintain your momentum; keep a steady walk and let the bass guide your weight transfers.
T3: 158s [main → peak, beat: moderate → moderate] — commit to the new energy, travel more, and add intention.
P4: 158s-165s, peak [beat: moderate] — Use this moment to add more expression; try subtle variations in your connection or frame.
T4: 165s [peak → main, beat: moderate → moderate] — settle back, breathe, and return to the basic.
P5: 165s-248s, main ×7 [beat: moderate] — Return to your foundation; reconnect with your partner and maintain a steady, compact walk.
T5: 248s [main → main, beat: moderate → moderate] — as the energy lifts, travel a little more and add intention.
P6: 248s-287s, main ×4 [beat: moderate] — Begin to wind down; reduce your travel and keep your movements contained.
T6: 287s [main → outro, beat: moderate → subtle] — as the energy fades and the percussion thins, contract your movement and slow the basic, marking the subtle pulse with tiny weight shifts.
P7: 287s-301s, outro [beat: subtle] — The pulse is much softer; keep your movements very small and let the dance end gently.
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
This track lasts 185.4 seconds with a tempo of 96 BPM. The musical journey begins with an intro, moves through several main sections, and builds through a build phase toward a high-energy peak. After this intensity, the song enters a low-energy break before concluding with an outro. Because the percussiveness is unusually low, you will find that the rhythm is drum-light, with melodic and harmonic content carrying the pulse rather than a heavy percussive grid.

The most challenging moment occurs during the break from 141s to 163s. During this stretch, the beat clarity becomes moderate and the percussion thins out significantly, making the pulse much harder to lock onto. You may also find the rhythm slightly more difficult to track during the peak and certain main sections where the beat clarity is only moderate. When you reach that low-energy break, do not try to find a heavy drum hit; instead, trust the bass line to carry the pulse through the stillness.
```

### kizomba_tutor (one-pass)

```
P1: 0s-17s, intro [beat: clear] — Feel the connection through a close embrace and just mark the pulse together.
P2: 17s-23s, short_break [beat: clear] — Use this transition to find a steady walk-step as the energy lifts.
P3: 23s-85s, main ×6 [beat: clear] — This establishing phase is for settling in; follow the bass line for your walk-steps.
P4: 85s-90s, short_break [beat: clear] — Reset your frame and prepare for the next movement.
P5: 90s-110s, main ×2 [beat: clear] — This sustaining phase focuses on weight transfer as you maintain the steady pulse.
P6: 110s-120s, build [beat: clear] — The music is pulling you forward; gradually increase your step size and expression.
P7: 120s-131s, peak [beat: clear] — This is the emotional high point; use stronger leading variety and more intention.
P8: 131s-141s, main [beat: clear] — This returning phase re-establishes the basic; reconnect with a steady walk.
P9: 141s-163s, break [beat: moderate] — Stay compact and test the pulse with small steps to avoid chasing the rhythm.
P10: 163s-185s, outro [beat: clear] — Slow down and return to minimal movement to let the dance end gently.
```

### kizomba_drills (verified)

```
P1: intro (0s-17s, beat: clear) — Drill: maintain a close embrace and feel the pulse through the connection. 17s.
P2: short_break (17s-23s, beat: clear) — Drill: reduce travel and keep a small pulse in the body. 6s.
P3: main (23s-85s, beat: clear) — Drill: practice a steady walk-step focusing on weight transfer. 62s loop, repeated through the three main phases.
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
P1: intro (0s-17s, beat: clear) — Drill: maintain a close embrace and feel the pulse through the connection. 17s.
P2: short_break (17s-23s, beat: clear) — Drill: reduce travel and keep a small pulse in the body. 6s.
P3-P8: main (23s-85s, beat: clear) — Drill: practice a steady walk-step focusing on weight transfer. 62s loop, repeated through the three main phases.
P9: short_break (85s-90s, beat: clear) — Drill: reset the frame and keep a small pulse in the body. 5s.
P10-P12: main (90s-120s, beat: clear) — Drill: same walk-step as P3-P8, but focus on following the bass line. 30s loop, repeated through the two main phases.
P13: build (110s-120s, beat: clear) — Drill: increase step size to build tension. 10s.
P14: peak (120s-131s, beat: clear) — Drill: use more variety in your lead. 11s.
P15: main (131s-141s, beat: clear) — Drill: same walk-step as P3-P8, but now add subtle hip styling once the basic feels automatic. 10s.
P16: break (141s-163s, beat: moderate) — Drill: stay compact with small steps and test the pulse. 22s.
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
T1: 17s [intro → short_break, beat: clear → clear] — find a steady pulse and a smooth walk-step.
T2: 23s [short_break → main, beat: clear → clear] — as the energy lifts, travel a little more with your walk-step.
T3: 85s [main → short_break, beat: clear → clear] — as the energy settles, keep the basic and hold a steady frame.
T4: 90s [short_break → main, beat: clear → clear] — return to a steady walk-step.
T5: 110s [main → build, beat: clear → clear] — as the energy builds, commit to the new energy and travel more.
T6: 120s [build → peak, beat: clear → clear] — add intention and more expression to your movement.
T7: 131s [peak → main, beat: clear → clear] — settle back and return to the basic.
T8: 141s [main → break, beat: clear → moderate] — as the energy fades and the percussion thins, keep a small pulse in the body and listen.
T9: 163s [break → outro, beat: moderate → clear] — walk-step on the first clear bass hit, then contract your movement to prepare to close.
```

### kizomba_transitions verifier stats

```
parsed=9 boundaries_matched=9 boundaries_invented=0 boundaries_missing_filled=0 skipped_lines=0 output_lines=9
```

### kizomba_tutor (polished)

```
P1: 0s-17s, intro [beat: clear] — Establish a close connection and find the pulse together through small, shared movements.
P2: 17s-23s, short_break [beat: clear] — Reduce your travel and use this moment to reset your frame for the upcoming steps.
P3: 23s-85s, main ×6 [beat: clear] — Settle into the rhythm by using the steady bass to guide your walking steps.
P4: 85s-90s, short_break [beat: clear] — Re-center your weight and prepare for a new direction.
P5: 90s-110s, main ×2 [beat: clear] — Focus on smooth weight transfers while maintaining a consistent, grounded pulse.
P6: 110s-120s, build [beat: clear] — Use the rising energy to expand your step size and increase your movement's intention.
P7: 120s-131s, peak [beat: clear] — Lean into the musical peak with more expressive, purposeful leading and following.
P8: 131s-141s, main [beat: clear] — Return to a grounded foundation by reconnecting with a steady, rhythmic walk.
P9: 141s-163s, break [beat: moderate] — Keep your movements compact and stay close to your center to avoid chasing the subtle percussion.
P10: 163s-185s, outro [beat: clear] — Gradually minimize your steps, letting the dance fade out with gentle, small pulses.
```

### unified timeline (phases + transitions)

```
P1: 0s-17s, intro [beat: clear] — Establish a close connection and find the pulse together through small, shared movements.
T1: 17s [intro → short_break, beat: clear → clear] — find a steady pulse and a smooth walk-step.
P2: 17s-23s, short_break [beat: clear] — Reduce your travel and use this moment to reset your frame for the upcoming steps.
T2: 23s [short_break → main, beat: clear → clear] — as the energy lifts, travel a little more with your walk-step.
P3: 23s-85s, main ×6 [beat: clear] — Settle into the rhythm by using the steady bass to guide your walking steps.
T3: 85s [main → short_break, beat: clear → clear] — as the energy settles, keep the basic and hold a steady frame.
P4: 85s-90s, short_break [beat: clear] — Re-center your weight and prepare for a new direction.
T4: 90s [short_break → main, beat: clear → clear] — return to a steady walk-step.
P5: 90s-110s, main ×2 [beat: clear] — Focus on smooth weight transfers while maintaining a consistent, grounded pulse.
T5: 110s [main → build, beat: clear → clear] — as the energy builds, commit to the new energy and travel more.
P6: 110s-120s, build [beat: clear] — Use the rising energy to expand your step size and increase your movement's intention.
T6: 120s [build → peak, beat: clear → clear] — add intention and more expression to your movement.
P7: 120s-131s, peak [beat: clear] — Lean into the musical peak with more expressive, purposeful leading and following.
T7: 131s [peak → main, beat: clear → clear] — settle back and return to the basic.
P8: 131s-141s, main [beat: clear] — Return to a grounded foundation by reconnecting with a steady, rhythmic walk.
T8: 141s [main → break, beat: clear → moderate] — as the energy fades and the percussion thins, keep a small pulse in the body and listen.
P9: 141s-163s, break [beat: moderate] — Keep your movements compact and stay close to your center to avoid chasing the subtle percussion.
T9: 163s [break → outro, beat: moderate → clear] — walk-step on the first clear bass hit, then contract your movement to prepare to close.
P10: 163s-185s, outro [beat: clear] — Gradually minimize your steps, letting the dance fade out with gentle, small pulses.
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
This track lasts 254.3 seconds with a steady tempo of 96 BPM. The musical journey begins with a subtle, low-energy intro that transitions into several main sections characterized by high and medium energy. These main phases are periodically interrupted by breaks and a short break, eventually tapering off into a gentle outro. Because the percussiveness is unusually low, you will find that the rhythm is not driven by a heavy drum kit; instead, the melodic and harmonic content carries the pulse, with the bass line providing the primary rhythmic anchor throughout the arc.

The most challenging moments occur when the beat clarity shifts from clear to subtle or moderate. Specifically, the intro (0s–36s) and the breaks (such as at 165s and 227s) present a dip in clarity where the pulse is felt rather than heard. The hardest stretch is the initial intro, where the rhythm is most understated and the percussion is at its thinnest. During these transitions and low-energy segments, do not attempt to find a sharp percussive edge; instead, trust the bass line to guide your sense of the pulse.
```

### kizomba_tutor (one-pass)

```
P1: 0s-36s, intro [beat: subtle] — The pulse is hard to lock onto as it is felt rather than heard; keep movement minimal and use tiny weight shifts to find the connection.
P2: 36s-51s, break [beat: clear] — The beat is now easy to follow; use this moment to reset your frame and prepare for the movement ahead.
P3: 51s-103s, main ×5 [beat: clear] — This establishing phase is safe to trust the steady pulse; settle into a smooth walk-step and let the bass guide your travel.
P4: 103s-113s, short_break [beat: clear] — The beat remains reliable; stay compact and use a small pulse in the body to prepare for the next energy shift.
P5: 113s-165s, main ×5 [beat: clear] — As we are sustaining the energy, focus on consistent weight transfers while following the clear, steady pulse.
P6: 165s-187s, break [beat: moderate] — The pulse is less obvious here; stay close and avoid chasing extra percussion by keeping your steps small.
P7: 187s-227s, main ×4 [beat: moderate] — This is a returning phase; test the pulse with small steps and reconnect with your partner as the rhythm settles.
P8: 227s-254s, outro [beat: moderate] — The song is winding down; contract your movement and let the dance end gently with the fading pulse.
```

### kizomba_drills (verified)

```
P1: intro (0s-36s, beat: subtle) — Drill: mark the pulse with a tiny shoulder bounce to prepare for re-entry. 36s.
P2: break (36s-51s, beat: clear) — Drill: reduce travel and keep a small pulse in the body. 15s.
P3: main (51s-103s, beat: clear) — Drill: practice a steady walk-step focusing on weight transfer. 52s loop, repeated through the five main phases.
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
P3-P7: main (51s-103s, beat: clear) — Drill: practice a steady walk-step focusing on weight transfer. 52s loop, repeated through the five main phases.
P8: short_break (103s-113s, beat: clear) — Drill: shrink the dance and maintain a small pulse. 10s.
P9-P13: main (113s-165s, beat: clear) — Drill: same walk-step as P3-P7, but now add subtle hip styling once the basic feels automatic. 52s loop, repeated through the five main phases.
P14: break (165s-187s, beat: moderate) — Drill: stay compact with small steps and test the pulse. 22s.
P15-P18: main (187s-227s, beat: moderate) — Drill: keep steps small and avoid chasing extra percussion. 40s.
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
T1: 36s [intro → break, beat: subtle → clear] — when the beat becomes clear, keep a small pulse in the body, listen, and reset.
T2: 51s [break → main, beat: clear → clear] — walk-step on the first clear bass hit.
T3: 103s [main → short_break, beat: clear → clear] — as the energy shifts, lean into the weight transfer on the syncopated bass.
T4: 113s [short_break → main, beat: clear → clear] — walk-step on the first clear bass hit.
T5: 165s [main → break, beat: clear → moderate] — as the energy fades and the percussion thins, keep a small pulse in the body, listen, and reset.
T6: 187s [break → main, beat: moderate → moderate] — when the bass kicks in, walk-step on the first clear hit.
T7: 227s [main → outro, beat: moderate → moderate] — as the energy fades, contract your movement, slow the basic, and prepare to close.
```

### kizomba_transitions verifier stats

```
parsed=7 boundaries_matched=7 boundaries_invented=0 boundaries_missing_filled=0 skipped_lines=0 output_lines=7
```

### kizomba_tutor (polished)

```
P1: 0s-36s, intro [beat: subtle] — The pulse is felt rather than heard; keep movement minimal and use tiny weight shifts to find the connection.
P2: 36s-51s, break [beat: clear] — The beat is now easy to follow; reduce your travel and use this moment to reset your frame.
P3: 51s-103s, main ×5 [beat: clear] — Trust this steady pulse; settle into a smooth walk-step and let the bass guide your travel.
P4: 103s-113s, short_break [beat: clear] — The beat remains reliable; stay compact and keep a small pulse in the body to prepare for the next energy shift.
P5: 113s-165s, main ×5 [beat: clear] — Sustain the energy by focusing on consistent weight transfers while following the steady pulse.
P6: 165s-187s, break [beat: moderate] — The pulse is less obvious; stay close and avoid chasing extra percussion by keeping your steps small.
P7: 187s-227s, main ×4 [beat: moderate] — Test the pulse with small steps and reconnect with your partner as the rhythm settles.
P8: 227s-254s, outro [beat: moderate] — The song is winding down; contract your movement and let the dance end gently with the fading pulse.
```

### unified timeline (phases + transitions)

```
P1: 0s-36s, intro [beat: subtle] — The pulse is felt rather than heard; keep movement minimal and use tiny weight shifts to find the connection.
T1: 36s [intro → break, beat: subtle → clear] — when the beat becomes clear, keep a small pulse in the body, listen, and reset.
P2: 36s-51s, break [beat: clear] — The beat is now easy to follow; reduce your travel and use this moment to reset your frame.
T2: 51s [break → main, beat: clear → clear] — walk-step on the first clear bass hit.
P3: 51s-103s, main ×5 [beat: clear] — Trust this steady pulse; settle into a smooth walk-step and let the bass guide your travel.
T3: 103s [main → short_break, beat: clear → clear] — as the energy shifts, lean into the weight transfer on the syncopated bass.
P4: 103s-113s, short_break [beat: clear] — The beat remains reliable; stay compact and keep a small pulse in the body to prepare for the next energy shift.
T4: 113s [short_break → main, beat: clear → clear] — walk-step on the first clear bass hit.
P5: 113s-165s, main ×5 [beat: clear] — Sustain the energy by focusing on consistent weight transfers while following the steady pulse.
T5: 165s [main → break, beat: clear → moderate] — as the energy fades and the percussion thins, keep a small pulse in the body, listen, and reset.
P6: 165s-187s, break [beat: moderate] — The pulse is less obvious; stay close and avoid chasing extra percussion by keeping your steps small.
T6: 187s [break → main, beat: moderate → moderate] — when the bass kicks in, walk-step on the first clear hit.
P7: 187s-227s, main ×4 [beat: moderate] — Test the pulse with small steps and reconnect with your partner as the rhythm settles.
T7: 227s [main → outro, beat: moderate → moderate] — as the energy fades, contract your movement, slow the basic, and prepare to close.
P8: 227s-254s, outro [beat: moderate] — The song is winding down; contract your movement and let the dance end gently with the fading pulse.
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
This 284.0-second track moves at a slow 81 BPM, which is below the typical range for this style. The musical journey begins with a low-energy intro, transitions into several main sections of varying energy, moves through a short break and an instrumental phase, reaches an emotional peak, and finally settles into a low-energy outro. Because the percussiveness is unusually low, you will find the rhythm is carried more by melodic and harmonic content than by a heavy drum presence, creating a pulse that is felt through the bass rather than a sharp percussive grid.

The most challenging moments occur during the short break starting at 16s and the outro at 265s, where the beat clarity becomes moderate rather than clear. You may also find the rhythm difficult to track in the later main sections, such as at 220.8s, where the beat clarity dips significantly. The hardest stretch is the final section near the end of the track, as the pulse becomes much more subtle and the percussion thins out. During these transitions, trust the bass line to guide your sense of timing.
```

### kizomba_tutor (one-pass)

```
P1: 0s-10s, intro [beat: clear] — The pulse is easy to find; keep movement minimal and focus on connection.
P2: 10s-16s, main [beat: clear] — Establishing the rhythm; use a steady walk-step and follow the bass line.
P3: 16s-29s, short_break [beat: moderate] — The pulse is a bit less obvious; stay compact and test the rhythm with small steps.
P4: 29s-83s, main ×5 [beat: clear] — Sustaining the flow; trust the steady pulse to guide your weight transfers.
P5: 83s-95s, instrumental [beat: clear] — A brief melodic shift; keep your walk steady and maintain your frame.
P6: 95s-101s, peak [beat: clear] — The emotional high point; you can travel more and add more expression to your lead.
P7: 101s-265s, main ×13 [beat: clear] — Returning to the basics after the peak; re-establish your connection and walk evenly.
P8: 265s-284s, outro [beat: moderate] — The song is winding down; avoid chasing extra percussion and let the dance end gently.
```

### kizomba_drills (verified)

```
P1: intro (0s-10s, beat: clear) — Drill: maintain a close embrace and feel the pulse through the bass. 10s.
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
parsed=12 repaired_ranges=2 duplicate_phases=0 filled_missing=4 skipped_lines=8 output_lines=8
```

### kizomba_drills raw Gemma draft

```
P1: intro (0s-10s, beat: clear) — Drill: maintain a close embrace and feel the pulse through the bass. 10s.
P2: main (10s-16s, beat: clear) — Drill: practice a steady walk-step following the bass line. 6s.
P3: short_break (16s-29s, beat: moderate) — Drill: reduce travel and keep a small pulse in the body. 13s.
P4-P7: main (29s-83s, beat: clear) — Drill: same walk-step as P2, but add subtle hip styling once the basic feels automatic. 54s loop, repeated through the four main phases.
P8: instrumental (83s-95s, beat: clear) — Drill: focus on smooth weight transfers. 12s.
P9: peak (95s-101s, beat: clear) — Drill: increase leading variety and expression. 6s.
P10-P14: main (101s-167s, beat: clear) — Drill: keep the energy built from the peak with steady walk-steps. 66s loop, repeated through the four main phases.
P15-P17: main (167s-190s, beat: clear) — Drill: focus on leading with a strong step and light follow-through. 23s.
P18: main (190s-196s, beat: moderate) — Drill: test the pulse with small steps to avoid chasing the syncopation. 6s.
P19-P21: main (196s-238s, beat: clear) — Drill: return to the steady walk-step. 42s loop, repeated through the four main phases.
P22: main (238s-265s, beat: clear) — Drill: maintain a small pulse in the body while following the bass. 27s.
P23: outro (265s-284s, beat: moderate) — Drill: slow the pace and return to minimal movement. 19s.
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
T4: 83s [main → instrumental, beat: clear → clear] — keep your basic going steadily.
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
P1: 0s-10s, intro [beat: clear] — Find the steady pulse and use it to ground your connection with small, controlled movements.
P2: 10s-16s, main [beat: clear] — Establish your rhythm by using a consistent walk-step that follows the bass line.
P3: 16s-29s, short_break [beat: moderate] — The rhythm softens; stay compact and use small steps to find your center before reconnecting.
P4: 29s-83s, main ×5 [beat: clear] — Maintain your flow by using the steady pulse to guide smooth, rhythmic weight transfers.
P5: 83s-95s, instrumental [beat: clear] — As the melody shifts, keep your walk steady and maintain a strong, stable frame.
P6: 95s-101s, peak [beat: clear] — Use this energy to increase your travel and add more expressive intention to your lead.
P7: 101s-265s, main ×13 [beat: clear] — Return to your foundation by re-establishing a close connection and walking with even steps.
P8: 265s-284s, outro [beat: moderate] — As the song winds down, avoid chasing extra percussion and let your movements settle gently.
```

### unified timeline (phases + transitions)

```
P1: 0s-10s, intro [beat: clear] — Find the steady pulse and use it to ground your connection with small, controlled movements.
T1: 10s [intro → main, beat: clear → clear] — walk-step the basic on the first clear bass hit.
P2: 10s-16s, main [beat: clear] — Establish your rhythm by using a consistent walk-step that follows the bass line.
T2: 16s [main → short_break, beat: clear → moderate] — keep a small pulse in the body, listen, and reset.
P3: 16s-29s, short_break [beat: moderate] — The rhythm softens; stay compact and use small steps to find your center before reconnecting.
T3: 29s [short_break → main, beat: moderate → clear] — walk-step on the first clear bass hit once the pulse stabilizes.
P4: 29s-83s, main ×5 [beat: clear] — Maintain your flow by using the steady pulse to guide smooth, rhythmic weight transfers.
T4: 83s [main → instrumental, beat: clear → clear] — keep your basic going steadily.
P5: 83s-95s, instrumental [beat: clear] — As the melody shifts, keep your walk steady and maintain a strong, stable frame.
T5: 95s [instrumental → peak, beat: clear → clear] — commit to the new energy, travel more, and add intention.
P6: 95s-101s, peak [beat: clear] — Use this energy to increase your travel and add more expressive intention to your lead.
T6: 101s [peak → main, beat: clear → clear] — settle back, breathe, and return to the basic.
P7: 101s-265s, main ×13 [beat: clear] — Return to your foundation by re-establishing a close connection and walking with even steps.
T7: 265s [main → outro, beat: clear → moderate] — as the energy fades and the percussion thins, contract movement, slow the basic, and prepare to close.
P8: 265s-284s, outro [beat: moderate] — As the song winds down, avoid chasing extra percussion and let your movements settle gently.
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
This 372.5-second track maintains a steady tempo of 89 BPM. The musical journey begins with a medium-energy intro that transitions into a long series of main sections, eventually building toward a brief peak before descending through an instrumental break and a final high-energy stretch that winds down into a low-energy outro. Throughout most of the song, the pulse is felt through the bass line rather than a heavy percussive grid, providing a smooth, continuous flow.

The primary challenge for listening is the very beginning, specifically during the intro from 0s to 23s, where the beat is only moderate and the pulse is quite subtle. Because the percussiveness is low here, the beat is less distinct than in the later, clearer sections. You may also find your attention drifting during the long, repetitive main phases. When the clarity dips at the start, do not try to find a heavy drum; instead, focus on the bass to find your connection.
```

### kizomba_tutor (one-pass)

```
P1: 0s-23s, intro [beat: moderate] — The pulse is felt rather than heard; stay compact and test the pulse with small weight shifts.
P2: 23s-112s, main ×9 [beat: clear] — Establishing the groove; trust the steady pulse to guide a smooth, steady walk.
P3: 112s-117s, peak [beat: clear] — The emotional high point; use the clear pulse to add more expression and variety to your leading.
P4: 117s-177s, main ×5 [beat: clear] — Returning to the basics; reconnect with your partner and focus on steady weight transfers.
P5: 177s-204s, main ×2 [beat: clear] — Sustaining the energy; keep your frame strong and follow the bass line as it guides your steps.
P6: 204s-248s, main ×3 [beat: clear] — Sustaining the flow; maintain a consistent breath and steady walking rhythm.
P7: 248s-258s, instrumental [beat: clear] — A quieter moment; reduce your travel and keep a small, steady pulse in the body.
P8: 258s-280s, main ×3 [beat: clear] — Returning to the movement; re-establish the basic walk-step and find your connection again.
P9: 280s-357s, main ×5 [beat: clear] — Closing the song; movement should contract as you prepare to wind down.
P10: 357s-373s, outro [beat: clear] — The dance ends gently; slow your movement and let the energy fade out naturally.
```

### kizomba_drills (verified)

```
P1: intro (0s-23s, beat: moderate) — Drill: mark the pulse with a tiny shoulder bounce to find the connection. 23s.
P2: main (23s-112s, beat: clear) — Drill: focus on weight transfer during the steady walk-step. 89s.
P3: peak (112s-117s, beat: clear) — Drill: increase leading variety through the frame. 5s.
P4-P6: main (117s-248s, beat: clear) — Drill: same walk-step as P2, but now add subtle hip styling once the basic feels automatic. 131s.
P7: instrumental (248s-258s, beat: clear) — Drill: reduce travel and keep a small pulse in the body. 10s.
P8-P9: main (258s-357s, beat: clear) — Drill: maintain the walk-step while following the bass line for guidance. 99s.
P10: outro (357s-373s, beat: clear) — Drill: slow the pace and return to minimal movement. 16s.
```

### kizomba_drills verifier stats

```
parsed=7 repaired_ranges=0 duplicate_phases=0 filled_missing=0 skipped_lines=0 output_lines=7
```

### kizomba_drills raw Gemma draft

```
P1: intro (0s-23s, beat: moderate) — Drill: mark the pulse with a tiny shoulder bounce to find the connection. 23s.
P2-P2: main (23s-112s, beat: clear) — Drill: focus on weight transfer during the steady walk-step. 89s.
P3: peak (112s-117s, beat: clear) — Drill: increase leading variety through the frame. 5s.
P4-P6: main (117s-248s, beat: clear) — Drill: same walk-step as P2, but now add subtle hip styling once the basic feels automatic. 131s.
P7: instrumental (248s-258s, beat: clear) — Drill: reduce travel and keep a small pulse in the body. 10s.
P8-P9: main (258s-357s, beat: clear) — Drill: maintain the walk-step while following the bass line for guidance. 99s.
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
P1: 0s-23s, intro [beat: moderate] — The pulse is subtle; stay compact and use small weight shifts to find the rhythm.
P2: 23s-112s, main ×9 [beat: clear] — Focus on the groove; use the steady pulse to guide a smooth, rhythmic walk.
P3: 112s-117s, peak [beat: clear] — An expressive moment; use the clear pulse to add more intention and variety to your connection.
P4: 117s-177s, main ×5 [beat: clear] — Return to fundamentals; reconnect with your partner and focus on consistent weight transfers.
P5: 177s-204s, main ×2 [beat: clear] — Sustain the energy; keep your frame stable and let the bass guide your stepping pattern.
P6: 204s-248s, main ×3 [beat: clear] — Maintain the flow; keep a steady breathing rhythm and a consistent walking pace.
P7: 248s-258s, instrumental [beat: clear] — A brief transition; reduce your travel and keep a small, steady pulse in the body.
P8: 258s-280s, main ×3 [beat: clear] — Re-establish movement; return to a basic walk-step and find your connection again.
P9: 280s-357s, main ×5 [beat: clear] — As the song progresses, keep your movements controlled and intentional.
P10: 357s-373s, outro [beat: clear] — The dance concludes; slow your steps and let the energy fade out naturally.
```

### unified timeline (phases + transitions)

```
P1: 0s-23s, intro [beat: moderate] — The pulse is subtle; stay compact and use small weight shifts to find the rhythm.
T1: 23s [intro → main, beat: moderate → clear] — when the bass kicks in, walk-step the basic on the first clear hit.
P2: 23s-112s, main ×9 [beat: clear] — Focus on the groove; use the steady pulse to guide a smooth, rhythmic walk.
T2: 112s [main → peak, beat: clear → clear] — commit to the new energy, travel more, and add intention.
P3: 112s-117s, peak [beat: clear] — An expressive moment; use the clear pulse to add more intention and variety to your connection.
T3: 117s [peak → main, beat: clear → clear] — settle back, breathe, and return to the basic.
P4: 117s-177s, main ×5 [beat: clear] — Return to fundamentals; reconnect with your partner and focus on consistent weight transfers.
T4: 177s [main → main, beat: clear → clear] — as the percussion thickens, travel a little more and add intention.
P5: 177s-204s, main ×2 [beat: clear] — Sustain the energy; keep your frame stable and let the bass guide your stepping pattern.
T5: 204s [main → main, beat: clear → clear] — as the energy settles, keep the basic and hold a steady frame.
P6: 204s-248s, main ×3 [beat: clear] — Maintain the flow; keep a steady breathing rhythm and a consistent walking pace.
T6: 248s [main → instrumental, beat: clear → clear] — keep your basic going steadily through the instrumental.
P7: 248s-258s, instrumental [beat: clear] — A brief transition; reduce your travel and keep a small, steady pulse in the body.
T7: 258s [instrumental → main, beat: clear → clear] — keep your basic going steadily.
P8: 258s-280s, main ×3 [beat: clear] — Re-establish movement; return to a basic walk-step and find your connection again.
T8: 280s [main → main, beat: clear → clear] — as the energy lifts, travel a little more and add intention.
P9: 280s-357s, main ×5 [beat: clear] — As the song progresses, keep your movements controlled and intentional.
T9: 357s [main → outro, beat: clear → clear] — as the energy fades and the percussion thins, contract movement, slow the basic, and prepare to close.
P10: 357s-373s, outro [beat: clear] — The dance concludes; slow your steps and let the energy fade out naturally.
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
This 208.9-second track maintains a steady 92 BPM, following a structural arc that moves from a quiet intro through several main sections of varying energy, hits a sudden break, and concludes with an outro. Rather than a heavy drum-driven grid, the rhythm is carried primarily by the melodic and harmonic content, creating an unusually low percussive feel where the bass line provides the essential pulse.

The most challenging moment occurs during the transition into the break at 148s. While the beat remains clear, the energy drops significantly, and the rhythm shifts toward a more syncopated feel in the preceding section. Because the percussion is so light throughout the track, you may find it difficult to anchor yourself when the energy dips. During the break and the subsequent transition, do not try to find a heavy beat; instead, trust the bass line to guide your sense of timing.
```

### kizomba_tutor (one-pass)

```
P1: 0s-12s, intro [beat: clear] — Use this time to settle into a close embrace and just feel the pulse together.
P2: 12s-59s, main ×4 [beat: clear] — As we establish the rhythm, try a steady walk-step and let the bass guide your movement.
P3: 59s-80s, main ×2 [beat: clear] — Energy is climbing, so you can travel a little more while staying connected to the bass.
P4: 80s-121s, main ×4 [beat: clear] — Sustain the momentum by focusing on smooth weight transfers through your walk.
P5: 121s-148s, main ×2 [beat: clear] — This high-energy peak is great for more intentional movement, but keep your steps grounded.
P6: 148s-159s, break [beat: clear] — The music pulls back, so reduce your travel and just keep a small pulse in your body.
P7: 159s-195s, main ×3 [beat: clear] — Returning to the flow, re-establish your basic walk and reconnect with your partner.
P8: 195s-209s, outro [beat: clear] — As the song winds down, contract your movement and let the dance end gently.
```

### kizomba_drills (verified)

```
P1: intro (0s-12s, beat: clear) — Drill: maintain a close embrace and feel the pulse through the bass. 12s.
P2-P5: main (12s-148s, beat: clear) — Drill: practice a steady walk-step, letting the bass guide your weight transfer. 30s loop, repeated through the four main phases.
P6: break (148s-159s, beat: clear) — Drill: reduce travel and keep a small pulse in your body. 11s during the break.
P7: main (159s-195s, beat: clear) — Drill: same walk-step as P2-P5, but now add subtle hip styling once the basic feels automatic. 36s.
P8: outro (195s-209s, beat: clear) — Drill: reduce travel and let the movement wind down. 13s.
```

### kizomba_drills verifier stats

```
parsed=5 repaired_ranges=1 duplicate_phases=0 filled_missing=1 skipped_lines=1 output_lines=5
```

### kizomba_drills raw Gemma draft

```
P1: intro (0s-12s, beat: clear) — Drill: maintain a close embrace and feel the pulse through the bass. 12s.
P2-P5: main (12s-148s, beat: clear) — Drill: practice a steady walk-step, letting the bass guide your weight transfer. 30s loop, repeated through the four main phases.
P6: break (148s-159s, beat: clear) — Drill: reduce travel and keep a small pulse in your body. 11s during the break.
P7-P8: main (159s-195s, beat: clear) — Drill: same walk-step as P2-P5, but now add subtle hip styling once the basic feels automatic. 36s.
P9: outro (195s-209s, beat: clear) — Drill: slow the pace and return to minimal movement. 14s.
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
T1: 12s [intro → main, beat: clear → clear] — When the bass kicks in, walk-step the basic on the first clear hit.
T2: 59s [main → main, beat: clear → clear] — As the percussion thickens, travel a little more and add intention to your steps.
T3: 80s [main → main, beat: clear → clear] — As the energy settles, keep the basic and hold a steady frame.
T4: 121s [main → main, beat: clear → clear] — As the energy lifts, travel more and add intention to your movement.
T5: 148s [main → break, beat: clear → clear] — As the energy fades and the percussion thins, keep a small pulse in the body, listen, and reset.
T6: 159s [break → main, beat: clear → clear] — Walk-step on the first clear bass hit; don't chase the louder percussion.
T7: 195s [main → outro, beat: clear → clear] — As the energy fades, contract your movement, slow the basic, and prepare to close.
```

### kizomba_transitions verifier stats

```
parsed=7 boundaries_matched=7 boundaries_invented=0 boundaries_missing_filled=0 skipped_lines=0 output_lines=7
```

### kizomba_tutor (polished)

```
P1: 0s-12s, intro [beat: clear] — Settle into a close embrace and find a shared pulse through your connection.
P2: 12s-59s, main ×4 [beat: clear] — Establish a steady walking rhythm, letting the bass guide your weight transfers.
P3: 59s-80s, main ×2 [beat: clear] — As the energy builds, try increasing your travel while staying anchored to the bass.
P4: 80s-121s, main ×4 [beat: clear] — Sustain your momentum by focusing on smooth, continuous steps through your walk.
P5: 121s-148s, main ×2 [beat: clear] — Use this peak for more intentional movement, but keep your steps grounded and controlled.
P6: 148s-159s, break [beat: clear] — The music pulls back; reduce your travel and maintain a small, subtle pulse in your body.
P7: 159s-195s, main ×3 [beat: clear] — Re-establish your basic walk and reconnect with your partner to find the flow again.
P8: 195s-209s, outro [beat: clear] — As the song winds down, contract your movement and let the dance end gently.
```

### unified timeline (phases + transitions)

```
P1: 0s-12s, intro [beat: clear] — Settle into a close embrace and find a shared pulse through your connection.
T1: 12s [intro → main, beat: clear → clear] — When the bass kicks in, walk-step the basic on the first clear hit.
P2: 12s-59s, main ×4 [beat: clear] — Establish a steady walking rhythm, letting the bass guide your weight transfers.
T2: 59s [main → main, beat: clear → clear] — As the percussion thickens, travel a little more and add intention to your steps.
P3: 59s-80s, main ×2 [beat: clear] — As the energy builds, try increasing your travel while staying anchored to the bass.
T3: 80s [main → main, beat: clear → clear] — As the energy settles, keep the basic and hold a steady frame.
P4: 80s-121s, main ×4 [beat: clear] — Sustain your momentum by focusing on smooth, continuous steps through your walk.
T4: 121s [main → main, beat: clear → clear] — As the energy lifts, travel more and add intention to your movement.
P5: 121s-148s, main ×2 [beat: clear] — Use this peak for more intentional movement, but keep your steps grounded and controlled.
T5: 148s [main → break, beat: clear → clear] — As the energy fades and the percussion thins, keep a small pulse in the body, listen, and reset.
P6: 148s-159s, break [beat: clear] — The music pulls back; reduce your travel and maintain a small, subtle pulse in your body.
T6: 159s [break → main, beat: clear → clear] — Walk-step on the first clear bass hit; don't chase the louder percussion.
P7: 159s-195s, main ×3 [beat: clear] — Re-establish your basic walk and reconnect with your partner to find the flow again.
T7: 195s [main → outro, beat: clear → clear] — As the energy fades, contract your movement, slow the basic, and prepare to close.
P8: 195s-209s, outro [beat: clear] — As the song winds down, contract your movement and let the dance end gently.
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
This track lasts 237.7 seconds with a tempo of 92 BPM. The musical journey begins with an intro, moving through several main sections interspersed with short breaks, before building toward a peak and eventually settling into an outro. Because the percussiveness is unusually low, the rhythm is not driven by a heavy drum kit; instead, the melodic and harmonic content carries the pulse, making the music feel drum-light.

The most challenging moments occur during the breaks at 65s and 135s, where the beat clarity becomes moderate rather than clear. During these transitions, the pulse becomes less obvious and the rhythmic grid thins out, which can make it difficult to maintain a sense of timing. You may also find the rhythm harder to anchor during the build starting at 157s as the energy shifts. To navigate these dips, trust the bass line through the break to keep your connection to the music.
```

### kizomba_tutor (one-pass)

```
P1: 0s-13s, intro [beat: clear] — Focus on connection and minimal movement; just feel the steady pulse together.
P2: 13s-34s, short_break [beat: clear] — Keep the pulse steady with small weight shifts as you settle in.
P3: 34s-65s, main ×3 [beat: clear] — Establishing the rhythm; use a steady walk-step and follow the bass line.
P4: 65s-76s, break [beat: moderate] — Stay compact and test the pulse with small steps; avoid chasing extra percussion.
P5: 76s-135s, main ×5 [beat: clear] — Sustaining the movement; keep your frame steady and let the bass guide your steps.
P6: 135s-146s, break [beat: moderate] — Reset your connection and keep a small pulse in the body.
P7: 146s-157s, main [beat: clear] — Returning to the basics; re-establish your walk-step as the beat becomes clear.
P8: 157s-168s, build [beat: clear] — Gradually increase your step size and intention as the music pulls you forward.
P9: 168s-174s, peak [beat: clear] — This is the emotional high point; use more expression and variety in your leading.
P10: 174s-228s, main ×4 [beat: clear] — Closing the dance; contract your movement and return to a steady, controlled walk.
P11: 228s-238s, outro [beat: clear] — Slow down and let the dance end gently with minimal movement.
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
P3-P3: short_break (23.6s-33.6s, beat: clear) — Drill: reset your frame and reconnect with your partner. 10s.
P4-P6: main (33.6s-64.9s, beat: clear) — Drill: execute a steady walk-step focusing on weight transfer. 31.3s loop, repeated through the three main phases.
P7: break (64.9s-75.8s, beat: moderate) — Drill: keep steps small and test the pulse to avoid chasing extra percussion. 10.9s.
P8-P12: main (75.8s-135.2s, beat: clear) — Drill: same walk-step as P4-P6, but add subtle hip styling once the basic feels automatic. 59.4s loop, repeated through the five main phases.
P13: break (135.2s-146.4s, beat: moderate) — Drill: stay compact with tiny steps while maintaining the pulse. 11.2s.
P14: main (146.4s-156.8s, beat: clear) — Drill: return to a steady walk-step and follow the bass line. 10.4s.
P15: build (157s-168.1s, beat: clear) — Drill: gradually increase step size to build tension. 11.1s.
P16: peak (168.1s-174.1s, beat: clear) — Drill: use more leading variety and expression. 6s.
P17-P20: main (174.1s-228.1s, beat: clear) — Drill: keep the energy you built with strong, expressive walk-steps. 54s loop, repeated through the four main phases.
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
T1: 13s [intro → short_break, beat: clear → clear] — keep a close embrace and focus on the connection.
T2: 34s [short_break → main, beat: clear → clear] — when the bass kicks in, walk-step the basic.
T3: 65s [main → break, beat: clear → moderate] — as the energy fades, keep a small pulse in your body and listen.
T4: 76s [break → main, beat: moderate → clear] — walk-step on the first clear bass hit.
T5: 135s [main → break, beat: clear → moderate] — as the energy fades, keep a small pulse in your body and listen.
T6: 146s [break → main, beat: moderate → clear] — walk-step on the first clear bass hit.
T7: 157s [main → build, beat: clear → clear] — as the music pulls you forward, commit to the new energy and travel more.
T8: 168s [build → peak, beat: clear → clear] — commit to the high energy with more intention and expression.
T9: 174s [peak → main, beat: clear → clear] — as the energy settles, breathe and return to a steady basic.
T10: 228s [main → outro, beat: clear → clear] — as the energy fades, contract your movement and prepare to close.
```

### kizomba_transitions verifier stats

```
parsed=10 boundaries_matched=10 boundaries_invented=0 boundaries_missing_filled=0 skipped_lines=0 output_lines=10
```

### kizomba_tutor (polished)

```
P1: 0s-13s, intro [beat: clear] — Find your connection and use the steady pulse to ground your weight.
P2: 13s-34s, short_break [beat: clear] — Use small, rhythmic weight shifts to stay connected while you settle in.
P3: 34s-65s, main ×3 [beat: clear] — Focus on a consistent walk-step that follows the deep bass line.
P4: 65s-76s, break [beat: moderate] — Stay compact and use small steps; avoid chasing the lighter percussion.
P5: 76s-135s, main ×5 [beat: clear] — Maintain a steady frame and let the bass guide your step timing.
P6: 135s-146s, break [beat: moderate] — Reset your position and keep a subtle pulse in your body.
P7: 146s-157s, main [beat: clear] — Re-establish your foundational walk-step as the rhythm stabilizes.
P8: 157s-168s, build [beat: clear] — Increase your step intention and travel slightly more as the energy grows.
P9: 168s-174s, peak [beat: clear] — Use more expressive movement and varied leading to match the intensity.
P10: 174s-228s, main ×4 [beat: clear] — Bring your movement back to a controlled, steady walk to close.
P11: 228s-238s, outro [beat: clear] — Soften your movements and let the dance fade out gently.
```

### unified timeline (phases + transitions)

```
P1: 0s-13s, intro [beat: clear] — Find your connection and use the steady pulse to ground your weight.
T1: 13s [intro → short_break, beat: clear → clear] — keep a close embrace and focus on the connection.
P2: 13s-34s, short_break [beat: clear] — Use small, rhythmic weight shifts to stay connected while you settle in.
T2: 34s [short_break → main, beat: clear → clear] — when the bass kicks in, walk-step the basic.
P3: 34s-65s, main ×3 [beat: clear] — Focus on a consistent walk-step that follows the deep bass line.
T3: 65s [main → break, beat: clear → moderate] — as the energy fades, keep a small pulse in your body and listen.
P4: 65s-76s, break [beat: moderate] — Stay compact and use small steps; avoid chasing the lighter percussion.
T4: 76s [break → main, beat: moderate → clear] — walk-step on the first clear bass hit.
P5: 76s-135s, main ×5 [beat: clear] — Maintain a steady frame and let the bass guide your step timing.
T5: 135s [main → break, beat: clear → moderate] — as the energy fades, keep a small pulse in your body and listen.
P6: 135s-146s, break [beat: moderate] — Reset your position and keep a subtle pulse in your body.
T6: 146s [break → main, beat: moderate → clear] — walk-step on the first clear bass hit.
P7: 146s-157s, main [beat: clear] — Re-establish your foundational walk-step as the rhythm stabilizes.
T7: 157s [main → build, beat: clear → clear] — as the music pulls you forward, commit to the new energy and travel more.
P8: 157s-168s, build [beat: clear] — Increase your step intention and travel slightly more as the energy grows.
T8: 168s [build → peak, beat: clear → clear] — commit to the high energy with more intention and expression.
P9: 168s-174s, peak [beat: clear] — Use more expressive movement and varied leading to match the intensity.
T9: 174s [peak → main, beat: clear → clear] — as the energy settles, breathe and return to a steady basic.
P10: 174s-228s, main ×4 [beat: clear] — Bring your movement back to a controlled, steady walk to close.
T10: 228s [main → outro, beat: clear → clear] — as the energy fades, contract your movement and prepare to close.
P11: 228s-238s, outro [beat: clear] — Soften your movements and let the dance fade out gently.
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
This 213.8-second track maintains a steady tempo of 92 BPM. The musical journey begins with an intro, transitions into several main sections of varying energy, moves into a quiet break, and concludes with an outro. Rather than a heavy drum-driven beat, the rhythm is drum-light, with the melodic and harmonic content carrying the pulse. This creates a smooth, flowing texture where the bass line serves as the primary guide for the rhythm.

The most challenging moment occurs during the outro starting at 196.0 seconds, where the beat clarity shifts from clear to moderate. As the energy drops and the rhythmic density thins out, the pulse becomes harder to lock onto compared to the steady main sections. You may find the rhythm feels more elusive here as the track winds down. During this final stretch, focus on feeling the underlying pulse to maintain your connection to the music.
```

### kizomba_tutor (one-pass)

```
P1: 0s-18s, intro [beat: clear] — The pulse is easy to find; focus on a close embrace and just feel the connection.
P2: 18s-55s, main ×3 [beat: clear] — Establishing the rhythm; use a steady walk-step and let the bass guide your weight transfers.
P3: 55s-71s, main ×2 [beat: clear] — Sustaining the energy; keep your frame solid and follow the bass line as you travel.
P4: 71s-112s, main ×4 [beat: clear] — Sustaining the flow; maintain your steady walk and focus on smooth movement.
P5: 112s-138s, main ×2 [beat: clear] — Building the intensity; you can travel a little more as the energy rises.
P6: 138s-149s, break [beat: clear] — A moment to reset; reduce your travel and keep a small pulse in the body.
P7: 149s-196s, main ×4 [beat: clear] — Returning to the groove; re-establish the basic and reconnect with your partner.
P8: 196s-214s, outro [beat: moderate] — Closing the dance; stay compact and test the pulse with small, gentle weight shifts.
```

### kizomba_drills (verified)

```
P1: intro (0s-18s, beat: clear) — Drill: focus on a steady frame and connection. 18s.
P2-P5: main (18s-138s, beat: clear) — Drill: practice a smooth walk-step following the bass line. 53s loop, repeated through the four main phases.
P6: break (138s-149s, beat: clear) — Drill: reduce travel and keep a small pulse in the body. 41s.
P7: main (149s-196s, beat: clear) — Drill: same walk-step as P2-P5, but add subtle hip styling once the basic feels automatic. 26s.
P8: outro (196s-214s, beat: moderate) — Drill: reduce travel and let the movement wind down. 18s.
```

### kizomba_drills verifier stats

```
parsed=7 repaired_ranges=2 duplicate_phases=0 filled_missing=1 skipped_lines=3 output_lines=5
```

### kizomba_drills raw Gemma draft

```
P1: intro (0s-18s, beat: clear) — Drill: focus on a steady frame and connection. 18s.
P2-P5: main (18s-71s, beat: clear) — Drill: practice a smooth walk-step following the bass line. 53s loop, repeated through the four main phases.
P6: break (71s-112s, beat: clear) — Drill: reduce travel and keep a small pulse in the body. 41s.
P7-P12: main (112s-138s, beat: clear) — Drill: same walk-step as P2-P5, but add subtle hip styling once the basic feels automatic. 26s.
P13: break (138s-149s, beat: clear) — Drill: shrink the dance and maintain a small internal pulse. 11s.
P14-P17: main (149s-196s, beat: clear) — Drill: practice weight transfer with a half-time feel. 47s.
P18: outro (196s-214s, beat: moderate) — Drill: stay compact with small steps to test the pulse. 18s.
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
T1: 18s [intro → main, beat: clear → clear] — when the bass kicks in, walk-step the basic to the steady pulse.
T2: 55s [main → main, beat: clear → clear] — as the percussion thickens, travel a little more and add intention to your movement.
T3: 71s [main → main, beat: clear → clear] — as the energy settles, keep the basic and hold a steady frame.
T4: 112s [main → main, beat: clear → clear] — as the percussion returns, travel a little more and add intention.
T5: 138s [main → break, beat: clear → clear] — as the energy fades and the percussion thins, keep a small pulse in the body, listen, and reset.
T6: 149s [break → main, beat: clear → clear] — when the bass kicks in, walk-step on the first clear hit and find the steady pulse.
T7: 196s [main → outro, beat: clear → moderate] — as the energy fades, contract your movement, slow the basic, and prepare to close.
```

### kizomba_transitions verifier stats

```
parsed=7 boundaries_matched=7 boundaries_invented=0 boundaries_missing_filled=0 skipped_lines=0 output_lines=7
```

### kizomba_tutor (polished)

```
P1: 0s-18s, intro [beat: clear] — Find the steady pulse; focus on establishing a soft, close embrace and feeling the connection.
P2: 18s-55s, main ×3 [beat: clear] — Establish your rhythm; use a steady walk-step and let the bass guide your weight transfers.
P3: 55s-71s, main ×2 [beat: clear] — Sustain the energy; keep your frame solid and follow the bass line as you travel through the space.
P4: 71s-112s, main ×4 [beat: clear] — Maintain the flow; keep your walking steps consistent and focus on smooth, continuous movement.
P5: 112s-138s, main ×2 [beat: clear] — Build the intensity; you can increase your travel or step size as the energy rises.
P6: 138s-149s, break [beat: clear] — A moment to reset; reduce your travel and keep a small, rhythmic pulse in the body.
P7: 149s-196s, main ×4 [beat: clear] — Return to the groove; re-establish your basic step and reconnect deeply with your partner.
P8: 196s-214s, outro [beat: moderate] — Close the dance; stay compact and use small, gentle weight shifts to follow the pulse.
```

### unified timeline (phases + transitions)

```
P1: 0s-18s, intro [beat: clear] — Find the steady pulse; focus on establishing a soft, close embrace and feeling the connection.
T1: 18s [intro → main, beat: clear → clear] — when the bass kicks in, walk-step the basic to the steady pulse.
P2: 18s-55s, main ×3 [beat: clear] — Establish your rhythm; use a steady walk-step and let the bass guide your weight transfers.
T2: 55s [main → main, beat: clear → clear] — as the percussion thickens, travel a little more and add intention to your movement.
P3: 55s-71s, main ×2 [beat: clear] — Sustain the energy; keep your frame solid and follow the bass line as you travel through the space.
T3: 71s [main → main, beat: clear → clear] — as the energy settles, keep the basic and hold a steady frame.
P4: 71s-112s, main ×4 [beat: clear] — Maintain the flow; keep your walking steps consistent and focus on smooth, continuous movement.
T4: 112s [main → main, beat: clear → clear] — as the percussion returns, travel a little more and add intention.
P5: 112s-138s, main ×2 [beat: clear] — Build the intensity; you can increase your travel or step size as the energy rises.
T5: 138s [main → break, beat: clear → clear] — as the energy fades and the percussion thins, keep a small pulse in the body, listen, and reset.
P6: 138s-149s, break [beat: clear] — A moment to reset; reduce your travel and keep a small, rhythmic pulse in the body.
T6: 149s [break → main, beat: clear → clear] — when the bass kicks in, walk-step on the first clear hit and find the steady pulse.
P7: 149s-196s, main ×4 [beat: clear] — Return to the groove; re-establish your basic step and reconnect deeply with your partner.
T7: 196s [main → outro, beat: clear → moderate] — as the energy fades, contract your movement, slow the basic, and prepare to close.
P8: 196s-214s, outro [beat: moderate] — Close the dance; stay compact and use small, gentle weight shifts to follow the pulse.
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
This track lasts 199.7 seconds with an estimated tempo of 86 BPM. The musical journey begins with a low-energy intro, moves through a series of main sections and a build-up that leads into an emotional peak. Following this peak, the energy fluctuates through several more main phases before settling into a low-energy outro. Throughout most of the track, the pulse is carried by a clear percussive grid, though the intensity shifts significantly as the song progresses.

The most challenging period for maintaining the pulse occurs during the final main sections and the outro, specifically from 147.9 seconds through to the end of the track. During this stretch, the beat clarity becomes moderate and the percussiveness thins out, making the rhythm feel less defined than in the earlier, clearer sections. Because the rhythmic grid becomes less obvious, you may find it harder to anchor your sense of timing. During these later phases, trust the bass line to carry the pulse.
```

### kizomba_tutor (one-pass)

```
P1: 0s-12s, intro [beat: clear] — Focus on connection and minimal movement; just feel the steady pulse together.
P2: 12s-35s, main ×2 [beat: clear] — Establishing the rhythm; use a steady walk-step and let the bass guide your steps.
P3: 35s-45s, build [beat: clear] — The music is pulling you forward; gradually increase your step size and expression.
P4: 45s-62s, peak [beat: clear] — This is the emotional high point; use stronger leading variety and more expression.
P5: 62s-148s, main ×7 [beat: clear] — Sustaining the dance; keep a steady walk-step and follow the bass line with less is more.
P6: 148s-182s, main ×3 [beat: moderate] — Returning to the basics; stay compact and test the pulse with small steps.
P7: 182s-200s, outro [beat: moderate] — Closing the dance; slow down and return to minimal movement to end gently.
```

### kizomba_drills (verified)

```
P1: intro (0s-12s, beat: clear) — Drill: maintain a close embrace and feel the pulse together. 12s.
P2: main (12s-35s, beat: clear) — Drill: practice a steady walk-step following the bass line. 33s.
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
P1: intro (0s-12s, beat: clear) — Drill: maintain a close embrace and feel the pulse together. 12s.
P2-P4: main (12s-45s, beat: clear) — Drill: practice a steady walk-step following the bass line. 33s.
P5: peak (45s-62s, beat: clear) — Drill: increase leading variety and expression. 17s.
P6-P15: main (62s-182s, beat: clear/moderate) — Drill: same walk-step as P2-P4, but now add subtle hip styling once the basic feels automatic. 120s loop, repeated through the main phases.
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
T1: 12s [intro → main, beat: clear → clear] — walk-step the basic on the first clear bass hit as the percussion returns.
T2: 35s [main → build, beat: clear → clear] — commit to the new energy and travel more as the music begins to pull you forward.
T3: 45s [build → peak, beat: clear → clear] — add more intention and variety to your movement to meet the emotional high point.
T4: 62s [peak → main, beat: clear → clear] — settle back into the basic and return to a steady frame.
T5: 148s [main → main, beat: clear → moderate] — travel a little more and add intention as the energy lifts, but keep your steps small to recover as the beat becomes less obvious.
T6: 182s [main → outro, beat: moderate → moderate] — contract your movement and slow the basic as the energy fades and the percussion thins.
```

### kizomba_transitions verifier stats

```
parsed=6 boundaries_matched=6 boundaries_invented=0 boundaries_missing_filled=0 skipped_lines=0 output_lines=6
```

### kizomba_tutor (polished)

```
P1: 0s-12s, intro [beat: clear] — Establish your connection and find the steady pulse through small, grounded movements.
P2: 12s-35s, main ×2 [beat: clear] — Ground your weight into a rhythmic walk-step, letting the bass guide your momentum.
P3: 35s-45s, build [beat: clear] — Feel the increasing energy; gradually expand your step size and increase your movement range.
P4: 45s-62s, peak [beat: clear] — Embrace the emotional peak by using more intentional weight transfers and expressive leading.
P5: 62s-148s, main ×7 [beat: clear] — Maintain your flow with a consistent walk-step; focus on quality of connection rather than complexity.
P6: 148s-182s, main ×3 [beat: moderate] — Return to a more compact frame; use smaller steps to stay synchronized with the subtle pulse.
P7: 182s-200s, outro [beat: moderate] — Wind down the energy by reducing your travel and returning to minimal, gentle movements.
```

### unified timeline (phases + transitions)

```
P1: 0s-12s, intro [beat: clear] — Establish your connection and find the steady pulse through small, grounded movements.
T1: 12s [intro → main, beat: clear → clear] — walk-step the basic on the first clear bass hit as the percussion returns.
P2: 12s-35s, main ×2 [beat: clear] — Ground your weight into a rhythmic walk-step, letting the bass guide your momentum.
T2: 35s [main → build, beat: clear → clear] — commit to the new energy and travel more as the music begins to pull you forward.
P3: 35s-45s, build [beat: clear] — Feel the increasing energy; gradually expand your step size and increase your movement range.
T3: 45s [build → peak, beat: clear → clear] — add more intention and variety to your movement to meet the emotional high point.
P4: 45s-62s, peak [beat: clear] — Embrace the emotional peak by using more intentional weight transfers and expressive leading.
T4: 62s [peak → main, beat: clear → clear] — settle back into the basic and return to a steady frame.
P5: 62s-148s, main ×7 [beat: clear] — Maintain your flow with a consistent walk-step; focus on quality of connection rather than complexity.
T5: 148s [main → main, beat: clear → moderate] — travel a little more and add intention as the energy lifts, but keep your steps small to recover as the beat becomes less obvious.
P6: 148s-182s, main ×3 [beat: moderate] — Return to a more compact frame; use smaller steps to stay synchronized with the subtle pulse.
T6: 182s [main → outro, beat: moderate → moderate] — contract your movement and slow the basic as the energy fades and the percussion thins.
P7: 182s-200s, outro [beat: moderate] — Wind down the energy by reducing your travel and returning to minimal, gentle movements.
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
This 267.5-second track moves at 89 BPM, following a journey that begins with a low-energy intro before transitioning into an extended main section. The music eventually moves through a medium-energy break into a high-energy peak, before settling into a final main sequence and a gentle outro. Throughout most of the journey, the pulse is carried by a clear percussive grid and a steady bass line, providing a consistent foundation for the music's progression.

The most challenging moment occurs during the outro starting at 242s, where the beat clarity shifts from clear to moderate. During this final stretch, the percussion thins out significantly, making the pulse feel less defined and harder to lock into. You may also find the break at 164s requires extra focus, as the rhythmic texture changes and the bass pulls with a more syncopated feel. When the percussion fades toward the end, don't chase the melody; instead, feel the underlying pulse to maintain your connection to the music.
```

### kizomba_tutor (one-pass)

```
P1: 0s-33s, intro [beat: clear] — The pulse is easy to find; focus on a close embrace and just feel the connection without much travel.
P2: 33s-164s, main ×12 [beat: clear] — As we establish the rhythm, trust the steady pulse to guide your walk-steps and follow the bass.
P3: 164s-181s, break [beat: clear] — The beat remains easy to follow; use this moment to reset your connection and breathe before the energy rises.
P4: 181s-192s, peak [beat: clear] — The pulse is very reliable here; use this high point to add more intention and variety to your movement.
P5: 192s-242s, main ×5 [beat: clear] — As we return to the main rhythm, keep your walk-steps steady and let the bass guide your weight transfers.
P6: 242s-267s, outro [beat: moderate] — The pulse is a bit less defined; stay compact and test the rhythm with small, gentle steps as we wind down.
```

### kizomba_drills (verified)

```
P1: intro (0s-33s, beat: clear) — Drill: maintain a close embrace and feel the pulse through the bass. 33s.
P2: main (33s-164s, beat: clear) — Drill: practice a steady walk-step focusing on smooth weight transfers. 30s loop, repeated through the main phases.
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
P1: intro (0s–33s, beat: clear) — Drill: maintain a close embrace and feel the pulse through the bass. 33s.
P2-P13: main (33s–164s, beat: clear) — Drill: practice a steady walk-step focusing on smooth weight transfers. 30s loop, repeated through the main phases.
P14: break (164s–181s, beat: clear) — Drill: reduce travel and keep a small pulse in the body. 17s.
P15: peak (181s–192s, beat: clear) — Drill: increase leading variety and expression in your frame. 11s.
P16-P20: main (192s–242s, beat: clear) — Drill: same walk-step as P2-P13, but now add subtle hip styling once the basic feels automatic. 30s loop, repeated through the main phases.
P21: outro (242s–267s, beat: moderate) — Drill: keep steps small and test the pulse to stay compact. 25s.
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
T1: 33s [intro → main, beat: clear → clear] — Walk-step the basic on the first clear bass hit as the percussion returns.
T2: 164s [main → break, beat: clear → clear] — Keep a small pulse in the body, listen, and reset as the energy fades and the percussion thins.
T3: 181s [break → peak, beat: clear → clear] — Commit to the new energy and travel more, walking on the first clear bass hit.
T4: 192s [peak → main, beat: clear → clear] — Settle back, breathe, and return to the basic.
T5: 242s [main → outro, beat: clear → moderate] — Contract your movement and slow the basic to prepare to close as the energy fades and the percussion thins.
```

### kizomba_transitions verifier stats

```
parsed=5 boundaries_matched=5 boundaries_invented=0 boundaries_missing_filled=0 skipped_lines=0 output_lines=5
```

### kizomba_tutor (polished)

```
P1: 0s-33s, intro [beat: clear] — Use this steady pulse to find your center; focus on a close embrace and practice small, grounded steps.
P2: 33s-164s, main ×12 [beat: clear] — With the rhythm well-established, use the steady pulse to guide your walking steps and follow the bass.
P3: 164s-181s, break [beat: clear] — The beat is still present; reduce your travel and keep a small pulse in the body to reset before the next phase.
P4: 181s-192s, peak [beat: clear] — The pulse is very reliable here; use this energy to add more intention and variety to your movement.
P5: 192s-242s, main ×5 [beat: clear] — As the rhythm returns, keep your walking steps steady and let the bass guide your weight transfers.
P6: 242s-267s, outro [beat: moderate] — The pulse is less defined; stay compact and use small, gentle steps to avoid chasing the subtle percussion.
```

### unified timeline (phases + transitions)

```
P1: 0s-33s, intro [beat: clear] — Use this steady pulse to find your center; focus on a close embrace and practice small, grounded steps.
T1: 33s [intro → main, beat: clear → clear] — Walk-step the basic on the first clear bass hit as the percussion returns.
P2: 33s-164s, main ×12 [beat: clear] — With the rhythm well-established, use the steady pulse to guide your walking steps and follow the bass.
T2: 164s [main → break, beat: clear → clear] — Keep a small pulse in the body, listen, and reset as the energy fades and the percussion thins.
P3: 164s-181s, break [beat: clear] — The beat is still present; reduce your travel and keep a small pulse in the body to reset before the next phase.
T3: 181s [break → peak, beat: clear → clear] — Commit to the new energy and travel more, walking on the first clear bass hit.
P4: 181s-192s, peak [beat: clear] — The pulse is very reliable here; use this energy to add more intention and variety to your movement.
T4: 192s [peak → main, beat: clear → clear] — Settle back, breathe, and return to the basic.
P5: 192s-242s, main ×5 [beat: clear] — As the rhythm returns, keep your walking steps steady and let the bass guide your weight transfers.
T5: 242s [main → outro, beat: clear → moderate] — Contract your movement and slow the basic to prepare to close as the energy fades and the percussion thins.
P6: 242s-267s, outro [beat: moderate] — The pulse is less defined; stay compact and use small, gentle steps to avoid chasing the subtle percussion.
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
This 266.1-second track moves at a steady 89 BPM. The musical journey begins with a quiet intro, transitions into several breaks and a build, reaches a high-energy peak, and eventually settles into a medium-energy outro through various main sections. Rather than a heavy drum kit, the pulse is carried primarily by the melodic and harmonic content, creating an unusually drum-light feel where the bass line serves as the rhythmic anchor.

The most challenging moments occur when the beat clarity shifts from clear to moderate. Specifically, around the 109s mark during the peak, the pulse becomes more subtle and harder to pin down. You may also find the beat less obvious during the intro and the final outro. Because the percussion is so light, the hardest moments are when the rhythmic grid thins out, making the pulse feel more felt than heard. During these transitions and at the peak, don't chase the melodic layers; instead, trust the bass line to guide your sense of timing.
```

### kizomba_tutor (one-pass)

```
P1: 0s-13s, intro [beat: moderate] — The pulse is felt rather than heard; stay compact and test the pulse with small weight shifts.
P2: 13s-43s, break ×2 [beat: clear] — The pulse is easy to follow; reduce travel and reset your connection to the steady rhythm.
P3: 43s-54s, short_break [beat: clear] — Use this clear pulse to find your center and prepare for the upcoming movement.
P4: 54s-97s, main ×4 [beat: clear] — Establishing the rhythm; it is safe to trust the steady pulse and walk the basic.
P5: 97s-109s, build [beat: clear] — The pulse is clear; build tension by gradually increasing your step size and intention.
P6: 109s-121s, peak [beat: moderate] — The pulse is a bit more subtle; stay compact and avoid chasing extra percussion.
P7: 121s-177s, main ×5 [beat: clear] — Returning to the rhythm; re-establish the basic and focus on smooth weight transfers.
P8: 177s-201s, main ×3 [beat: clear] — Sustaining the energy; the pulse is steady, so you can travel a little more.
P9: 201s-222s, main ×2 [beat: clear] — Sustaining the flow; keep your frame steady as you follow the clear pulse.
P10: 222s-255s, main ×3 [beat: clear] — Closing the song; the pulse is clear, but begin to contract your movement.
P11: 255s-266s, outro [beat: moderate] — The pulse is a bit harder to lock onto; keep tiny weight shifts to end gently.
```

### kizomba_drills (verified)

```
P1: intro (0s-13s, beat: moderate) — Drill: keep steps very small and test the pulse. 13s.
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
parsed=6 repaired_ranges=4 duplicate_phases=0 filled_missing=9 skipped_lines=4 output_lines=11
```

### kizomba_drills raw Gemma draft

```
P1: intro (0s-13s, beat: moderate) — Drill: keep steps very small and test the pulse. 13s.
P2-P3: break (13s-43s, beat: clear) — Drill: reduce travel and keep a small pulse in the body. 30s.
P4: short_break (43s-54s, beat: clear) — Drill: reset your frame and reconnect with your partner. 11s.
P5-P10: main (54s-121s, beat: clear/moderate) — Drill: practice a steady walk-step focusing on weight transfer. 67s loop, repeated through the main phases.
P11-P15: main (121s-166s, beat: clear) — Drill: same walk-step as P5-P10, but now add subtle hip styling once the basic feels automatic. 45s loop.
P16: main (177s-201s, beat: clear) — Drill: practice larger saídas while following the bass line. 24s.
P17-P23: main (201s-255s, beat: clear/moderate) — Drill: maintain the walk-step but keep steps compact to avoid chasing extra percussion. 54s loop.
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
T3: 54s [short_break → main, beat: clear → clear] — as the percussion returns, walk-step on the first clear bass hit.
T4: 97s [main → build, beat: clear → clear] — as the music pulls you forward, commit to the new energy and travel more.
T5: 109s [build → peak, beat: clear → moderate] — commit to the new energy and add more expression; since the pulse is less obvious, trust the bass line.
T6: 121s [peak → main, beat: moderate → clear] — settle back, breathe, and return to the basic.
T7: 177s [main → main, beat: clear → clear] — as the percussion thickens, travel a little more and add intention.
T8: 201s [main → main, beat: clear → clear] — as the energy settles, keep the basic and hold a steady frame.
T9: 222s [main → main, beat: clear → clear] — In the last 8-count of the main, prepare for the shift; on entering the main, settle into the new feel.
T10: 255s [main → outro, beat: clear → moderate] — as the energy fades and the percussion thins, contract your movement and prepare to close.
```

### kizomba_transitions verifier stats

```
parsed=9 boundaries_matched=9 boundaries_invented=0 boundaries_missing_filled=1 skipped_lines=1 output_lines=10
```

### kizomba_transitions raw Gemma draft

```
T1: 13s [intro → break, beat: moderate → clear] — keep a small pulse in the body, listen, and reset.
T2: 43s [break → short_break, beat: clear → clear] — keep a small pulse in the body, listen, and reset.
T3: 54s [short_break → main, beat: clear → clear] — as the percussion returns, walk-step on the first clear bass hit.
T4: 97s [main → build, beat: clear → clear] — as the music pulls you forward, commit to the new energy and travel more.
T5: 109s [build → peak, beat: clear → moderate] — commit to the new energy and add more expression; since the pulse is less obvious, trust the bass line.
T6: 121s [peak → main, beat: moderate → clear] — settle back, breathe, and return to the basic.
T7: 177s [main → main, beat: clear → clear] — as the percussion thickens, travel a little more and add intention.
T8: 201s [main → main, beat: clear → clear] — as the energy settles, keep the basic and hold a steady frame.
T9: 222s [main → main, beat: clear → high/medium] — as the energy lifts, travel a little more and add intention.
T10: 255s [main → outro, beat: clear → moderate] — as the energy fades and the percussion thins, contract your movement and prepare to close.
```

### kizomba_tutor (polished)

```
P1: 0s-13s, intro [beat: moderate] — The pulse is subtle; stay compact and use small weight shifts to find the rhythm.
P2: 13s-43s, break ×2 [beat: clear] — The rhythm is steady; reduce your travel and reset your connection to prepare for the next phase.
P3: 43s-54s, short_break [beat: clear] — Use this clear pulse to find your center and stabilize your frame.
P4: 54s-97s, main ×4 [beat: clear] — The pulse is reliable; trust the steady rhythm and focus on walking your basic.
P5: 97s-109s, build [beat: clear] — The pulse is strong; increase your intention and gradually expand your step size.
P6: 109s-121s, peak [beat: moderate] — The rhythm is more nuanced; stay compact and avoid chasing extra percussion.
P7: 121s-177s, main ×5 [beat: clear] — Re-establish the basic and focus on smooth, controlled weight transfers.
P8: 177s-201s, main ×3 [beat: clear] — The pulse is steady; sustain the energy by allowing for slightly more travel.
P9: 201s-222s, main ×2 [beat: clear] — Maintain your flow by keeping a steady frame against the clear pulse.
P10: 222s-255s, main ×3 [beat: clear] — The pulse remains clear, but begin to contract your movements to wind down.
P11: 255s-266s, outro [beat: moderate] — The rhythm is soft; use tiny weight shifts to end the dance gently.
```

### unified timeline (phases + transitions)

```
P1: 0s-13s, intro [beat: moderate] — The pulse is subtle; stay compact and use small weight shifts to find the rhythm.
T1: 13s [intro → break, beat: moderate → clear] — keep a small pulse in the body, listen, and reset.
P2: 13s-43s, break ×2 [beat: clear] — The rhythm is steady; reduce your travel and reset your connection to prepare for the next phase.
T2: 43s [break → short_break, beat: clear → clear] — keep a small pulse in the body, listen, and reset.
P3: 43s-54s, short_break [beat: clear] — Use this clear pulse to find your center and stabilize your frame.
T3: 54s [short_break → main, beat: clear → clear] — as the percussion returns, walk-step on the first clear bass hit.
P4: 54s-97s, main ×4 [beat: clear] — The pulse is reliable; trust the steady rhythm and focus on walking your basic.
T4: 97s [main → build, beat: clear → clear] — as the music pulls you forward, commit to the new energy and travel more.
P5: 97s-109s, build [beat: clear] — The pulse is strong; increase your intention and gradually expand your step size.
T5: 109s [build → peak, beat: clear → moderate] — commit to the new energy and add more expression; since the pulse is less obvious, trust the bass line.
P6: 109s-121s, peak [beat: moderate] — The rhythm is more nuanced; stay compact and avoid chasing extra percussion.
T6: 121s [peak → main, beat: moderate → clear] — settle back, breathe, and return to the basic.
P7: 121s-177s, main ×5 [beat: clear] — Re-establish the basic and focus on smooth, controlled weight transfers.
T7: 177s [main → main, beat: clear → clear] — as the percussion thickens, travel a little more and add intention.
P8: 177s-201s, main ×3 [beat: clear] — The pulse is steady; sustain the energy by allowing for slightly more travel.
T8: 201s [main → main, beat: clear → clear] — as the energy settles, keep the basic and hold a steady frame.
P9: 201s-222s, main ×2 [beat: clear] — Maintain your flow by keeping a steady frame against the clear pulse.
T9: 222s [main → main, beat: clear → clear] — In the last 8-count of the main, prepare for the shift; on entering the main, settle into the new feel.
P10: 222s-255s, main ×3 [beat: clear] — The pulse remains clear, but begin to contract your movements to wind down.
T10: 255s [main → outro, beat: clear → moderate] — as the energy fades and the percussion thins, contract your movement and prepare to close.
P11: 255s-266s, outro [beat: moderate] — The rhythm is soft; use tiny weight shifts to end the dance gently.
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
This 146.9-second track maintains a steady tempo of 89 BPM. The musical journey begins with an intro that establishes a medium energy, transitions into a main section characterized by shifting energy levels, and eventually winds down through an outro. Throughout this arc, the pulse is carried by a clear, steady bass line that provides a reliable foundation for the music.

The beat remains clear throughout the entire duration, so your primary challenge will be sustaining your focus through the shifting energy levels rather than recovering from a loss of rhythm. The most difficult moment occurs between 120.1s and 131.1s, when the energy drops and the percussion thins significantly, creating a half-time feel. During this stretch, the pulse becomes much more subtle and less driven by percussion. When you reach this section, trust the bass line to guide you.
```

### kizomba_tutor (one-pass)

```
P1: 0s-22s, intro [beat: clear] — Find the connection in a close embrace and just feel the pulse together.
P2: 22s-49s, main ×3 [beat: clear] — This is establishing the rhythm; trust the steady pulse to guide a smooth walk-step.
P3: 49s-131s, main ×8 [beat: clear] — As we are sustaining the energy, focus on your weight transfer and let the bass guide your travel.
P4: 131s-147s, outro [beat: clear] — The song is winding down; return to minimal movement and let the dance end gently.
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
P6-P8: main (60s-87s, beat: clear) — Drill: return to a steady walk-step, matching the bass line. 27s.
P9: main (87s-98s, beat: clear) — Drill: practice a three-step pattern with a light pause. 11s.
P10-P11: main (98s-120s, beat: clear) — Drill: same walk-step as P2-P4, but now add subtle hip styling once the basic feels automatic. 22s.
P12: main (120s-131s, beat: clear) — Drill: step only on the pulse to match the half-time feel. 11s.
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
P1: 0s-22s, intro [beat: clear] — Establish a soft connection in a close embrace and find the shared pulse together.
P2: 22s-49s, main ×3 [beat: clear] — Use this steady rhythm to ground your movement; try a simple, rhythmic walk-step.
P3: 49s-131s, main ×8 [beat: clear] — Maintain your momentum by focusing on smooth weight transfers, letting the bass drive your travel.
P4: 131s-147s, outro [beat: clear] — As the energy fades, reduce your travel and let the dance settle into a gentle finish.
```

### unified timeline (phases + transitions)

```
P1: 0s-22s, intro [beat: clear] — Establish a soft connection in a close embrace and find the shared pulse together.
T1: 22s [intro → main, beat: clear → clear] — when the bass kicks in, walk-step the basic on the first clear bass hit.
P2: 22s-49s, main ×3 [beat: clear] — Use this steady rhythm to ground your movement; try a simple, rhythmic walk-step.
T2: 49s [main → main, beat: clear → clear] — as the energy shifts, travel a little more and add intention to your movement.
P3: 49s-131s, main ×8 [beat: clear] — Maintain your momentum by focusing on smooth weight transfers, letting the bass drive your travel.
T3: 131s [main → outro, beat: clear → clear] — as the energy fades and the percussion thins, contract your movement, slow the basic, and prepare to close.
P4: 131s-147s, outro [beat: clear] — As the energy fades, reduce your travel and let the dance settle into a gentle finish.
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
This 206.6-second track moves at a steady 89 BPM, traveling through an arc that begins with a quiet intro, transitions into a main body, builds toward a high-energy peak, and eventually settles into an outro. Because the percussiveness is unusually low, the rhythm is not driven by a heavy drum kit; instead, the pulse is carried primarily by the melodic and harmonic content, with the bass line providing the essential rhythmic foundation.

The most challenging moment for maintaining the pulse occurs during the main section between 70.0s and 96.9s, where the beat clarity becomes moderate and the pulse is less obvious. You may also find the short break starting at 11s difficult to anchor, as it introduces a syncopated feel where the bass pulls on the final beat of the measure. Throughout these sections, the pulse is felt rather than heard through a sharp percussive grid. When the clarity dips, trust the bass line to guide your sense of timing.
```

### kizomba_tutor (one-pass)

```
P1: 0s-11s, intro [beat: moderate] — Stay compact and test the pulse with small weight shifts to find your connection.
P2: 11s-16s, short_break [beat: moderate] — Keep a small pulse in the body and avoid chasing extra percussion as the bass pulls on the end of the phrase.
P3: 16s-97s, main ×7 [beat: clear] — Establishing the rhythm is easy here; trust the steady pulse to guide your walk-step.
P4: 97s-108s, build [beat: clear] — The pulse is very reliable, so gradually increase your step size and intention.
P5: 108s-119s, peak [beat: clear] — Use this clear rhythm to add more variety to your leading and expression.
P6: 119s-195s, main ×6 [beat: moderate] — Returning to a simpler feel, stay grounded and use the bass to guide steady, even walking.
P7: 195s-207s, outro [beat: clear] — The pulse is easy to follow again; slow your movement and let the dance end gently.
```

### kizomba_drills (verified)

```
P1: intro (0s-11s, beat: moderate) — Drill: maintain a close embrace and test the pulse with minimal movement. 11s.
P2: short_break (11s-16s, beat: moderate) — Drill: reduce travel and keep a small pulse in the body to reset. 5s.
P3: main (16s-97s, beat: clear) — Drill: practice a steady walk-step following the bass line. 16s.
P4: build (97s-108s, beat: clear) — Drill: practice steady weight transfers through this section. 11s.
P5: peak (108s-119s, beat: clear) — Drill: practice steady weight transfers through this section. 11s.
P6: main (119s-195s, beat: moderate) — Drill: stay compact and test the pulse with small steps. 76s.
P7: outro (195s-207s, beat: clear) — Drill: reduce travel and let the movement wind down. 12s.
```

### kizomba_drills verifier stats

```
parsed=11 repaired_ranges=1 duplicate_phases=0 filled_missing=4 skipped_lines=8 output_lines=7
```

### kizomba_drills raw Gemma draft

```
P1: intro (0s-11s, beat: moderate) — Drill: maintain a close embrace and test the pulse with minimal movement. 11s.
P2: short_break (11s-16s, beat: moderate) — Drill: reduce travel and keep a small pulse in the body to reset. 5s.
P3-P3: main (16s-32s, beat: clear) — Drill: practice a steady walk-step following the bass line. 16s.
P4-P7: main (32s-81s, beat: clear) — Drill: focus on weight transfer during the walk-step. 49s.
P8-P9: main (81s-97s, beat: moderate) — Drill: keep steps small and avoid chasing extra percussion. 16s.
P10: build (97s-108s, beat: clear) — Drill: gradually increase step size to build tension. 11s.
P11: peak (108s-119s, beat: clear) — Drill: use more leading variety and expressive hip movement. 11s.
P12-P13: main (119s-141s, beat: moderate) — Drill: same walk-step as P3, but add subtle hip styling once the basic feels automatic. 22s.
P14: main (141s-163s, beat: moderate) — Drill: maintain compact steps to stay connected to the pulse. 22s.
P15-P17: main (163s-195s, beat: moderate) — Drill: continue the steady walk-step, focusing on a smooth frame. 32s.
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
T1: 11s [intro → short_break, beat: moderate → moderate] — Keep a small pulse in the body, listen, and reset.
T2: 16s [short_break → main, beat: moderate → clear] — When the bass kicks in, walk-step on the first clear hit.
T3: 97s [main → build, beat: clear → clear] — As the energy lifts, travel a little more and add intention.
T4: 108s [build → peak, beat: clear → clear] — Commit to the new energy, travel more, and add intention.
T5: 119s [peak → main, beat: clear → moderate] — As the energy fades and the percussion thins, settle back, breathe, and return to the basic.
T6: 195s [main → outro, beat: moderate → clear] — As the energy fades, contract your movement, slow the basic, and prepare to close.
```

### kizomba_transitions verifier stats

```
parsed=6 boundaries_matched=6 boundaries_invented=0 boundaries_missing_filled=0 skipped_lines=0 output_lines=6
```

### kizomba_tutor (polished)

```
P1: 0s-11s, intro [beat: moderate] — Stay compact and use small weight shifts to find the pulse and your connection.
P2: 11s-16s, short_break [beat: moderate] — Keep a small pulse in the body and avoid chasing extra percussion as the bass pulls on the phrase.
P3: 16s-97s, main ×7 [beat: clear] — Use this steady pulse to guide a consistent, rhythmic walk-step.
P4: 97s-108s, build [beat: clear] — The pulse is very reliable; gradually increase your step size and movement intention.
P5: 108s-119s, peak [beat: clear] — Use this clear rhythm to add more variety to your leading and expression.
P6: 119s-195s, main ×6 [beat: moderate] — Return to a grounded feel, using the bass to guide steady, even walking steps.
P7: 195s-207s, outro [beat: clear] — The pulse is easy to follow; slow your movement and let the dance end gently.
```

### unified timeline (phases + transitions)

```
P1: 0s-11s, intro [beat: moderate] — Stay compact and use small weight shifts to find the pulse and your connection.
T1: 11s [intro → short_break, beat: moderate → moderate] — Keep a small pulse in the body, listen, and reset.
P2: 11s-16s, short_break [beat: moderate] — Keep a small pulse in the body and avoid chasing extra percussion as the bass pulls on the phrase.
T2: 16s [short_break → main, beat: moderate → clear] — When the bass kicks in, walk-step on the first clear hit.
P3: 16s-97s, main ×7 [beat: clear] — Use this steady pulse to guide a consistent, rhythmic walk-step.
T3: 97s [main → build, beat: clear → clear] — As the energy lifts, travel a little more and add intention.
P4: 97s-108s, build [beat: clear] — The pulse is very reliable; gradually increase your step size and movement intention.
T4: 108s [build → peak, beat: clear → clear] — Commit to the new energy, travel more, and add intention.
P5: 108s-119s, peak [beat: clear] — Use this clear rhythm to add more variety to your leading and expression.
T5: 119s [peak → main, beat: clear → moderate] — As the energy fades and the percussion thins, settle back, breathe, and return to the basic.
P6: 119s-195s, main ×6 [beat: moderate] — Return to a grounded feel, using the bass to guide steady, even walking steps.
T6: 195s [main → outro, beat: moderate → clear] — As the energy fades, contract your movement, slow the basic, and prepare to close.
P7: 195s-207s, outro [beat: clear] — The pulse is easy to follow; slow your movement and let the dance end gently.
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
This track lasts 251.8 seconds with a tempo of 92 BPM. The musical journey begins with a subtle intro, moves into an extended main section, transitions into a quiet break, and then returns through high-energy main phases before settling into a medium-energy outro. Because the percussiveness is unusually low, the rhythm is not driven by a heavy drum kit; instead, the melodic and harmonic content carries the pulse, making the bass line your primary guide for the rhythm.

The most challenging moment occurs during the intro (0s–25s), where the beat is subtle and the pulse is felt rather than heard. You may also find the break (168s–184s) difficult as the beat becomes only moderate, requiring more active listening to maintain connection. Throughout the main sections, watch for syncopated feels where the bass pulls unexpectedly, which can disrupt a steady sense of timing. During the quietest moments, especially the break, trust the bass line to find your way back to the pulse.
```

### kizomba_tutor (one-pass)

```
P1: 0s-25s, intro [beat: subtle] — The pulse is hard to lock onto; keep movement minimal with tiny weight shifts to find the connection.
P2: 25s-168s, main ×13 [beat: clear] — This is establishing the rhythm; trust the steady pulse and use a smooth walk-step to settle in.
P3: 168s-184s, break [beat: moderate] — The beat is a bit softer here; stay compact and test the pulse with small steps to avoid chasing the rhythm.
P4: 184s-210s, main ×2 [beat: clear] — This is returning to the groove; re-establish the basic walk and reconnect with your partner.
P5: 210s-237s, main ×3 [beat: clear] — This is closing the main sequence; movement should contract as you prepare to wind down.
P6: 237s-252s, outro [beat: clear] — The pulse remains steady; slow your travel and let the dance end gently with minimal movement.
```

### kizomba_drills (verified)

```
P1: intro (0s-25s, beat: subtle) — Drill: mark the pulse with a tiny shoulder bounce and prepare to re-enter the dance. 25s.
P2: main (25s-168s, beat: clear) — Drill: practice a steady walk-step focusing on smooth weight transfers. 30s loop, repeated through the main phases. 143s.
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
P1: intro (0s-25s, beat: subtle) — Drill: mark the pulse with a tiny shoulder bounce and prepare to re-enter the dance. 25s.
P2-P14: main (25s-168s, beat: clear) — Drill: practice a steady walk-step focusing on smooth weight transfers. 30s loop, repeated through the main phases. 143s.
P15: break (168s-184s, beat: moderate) — Drill: reduce travel and keep a small, compact pulse in the body. 16s.
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
T1: 25s [intro → main, beat: subtle → clear] — as the bass kicks in, walk-step the basic on the first clear bass hit.
T2: 168s [main → break, beat: clear → moderate] — as the energy fades and the percussion thins, keep a small pulse in the body, listen, and reset.
T3: 184s [break → main, beat: moderate → clear] — when the bass kicks in, walk-step on the first clear bass hit rather than chasing the loudest percussion.
T4: 210s [main → main, beat: clear → clear] — as the energy shifts, keep the basic and hold a steady frame to reconnect.
T5: 237s [main → outro, beat: clear → clear] — as the energy fades, contract your movement, slow the basic, and prepare to close.
```

### kizomba_transitions verifier stats

```
parsed=5 boundaries_matched=5 boundaries_invented=0 boundaries_missing_filled=0 skipped_lines=0 output_lines=5
```

### kizomba_tutor (polished)

```
P1: 0s-25s, intro [beat: subtle] — Focus on finding the connection through tiny weight shifts rather than large steps.
P2: 25s-168s, main ×13 [beat: clear] — Use this steady pulse to ground your movement with a smooth, rhythmic walk.
P3: 168s-184s, break [beat: moderate] — Reduce your travel and maintain a small pulse in the body to reset before the next phase.
P4: 184s-210s, main ×2 [beat: clear] — Reconnect with your partner and use the clear rhythm to re-establish your walking flow.
P5: 210s-237s, main ×3 [beat: clear] — Keep your steps controlled and slightly more compact as you prepare to wind down.
P6: 237s-252s, outro [beat: clear] — Use the steady pulse to slow your travel and let the dance conclude with gentle, minimal movement.
```

### unified timeline (phases + transitions)

```
P1: 0s-25s, intro [beat: subtle] — Focus on finding the connection through tiny weight shifts rather than large steps.
T1: 25s [intro → main, beat: subtle → clear] — as the bass kicks in, walk-step the basic on the first clear bass hit.
P2: 25s-168s, main ×13 [beat: clear] — Use this steady pulse to ground your movement with a smooth, rhythmic walk.
T2: 168s [main → break, beat: clear → moderate] — as the energy fades and the percussion thins, keep a small pulse in the body, listen, and reset.
P3: 168s-184s, break [beat: moderate] — Reduce your travel and maintain a small pulse in the body to reset before the next phase.
T3: 184s [break → main, beat: moderate → clear] — when the bass kicks in, walk-step on the first clear bass hit rather than chasing the loudest percussion.
P4: 184s-210s, main ×2 [beat: clear] — Reconnect with your partner and use the clear rhythm to re-establish your walking flow.
T4: 210s [main → main, beat: clear → clear] — as the energy shifts, keep the basic and hold a steady frame to reconnect.
P5: 210s-237s, main ×3 [beat: clear] — Keep your steps controlled and slightly more compact as you prepare to wind down.
T5: 237s [main → outro, beat: clear → clear] — as the energy fades, contract your movement, slow the basic, and prepare to close.
P6: 237s-252s, outro [beat: clear] — Use the steady pulse to slow your travel and let the dance conclude with gentle, minimal movement.
```
