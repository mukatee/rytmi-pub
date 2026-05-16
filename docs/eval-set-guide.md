# Eval Set Guide

## Purpose

The eval set is a curated collection of real songs in `data/songs/eval_set/` used to validate DSP pipeline changes against known musical characteristics. Each track has metadata in `metadata.yaml` describing its style, source, pairing, and attributes.

## Directory structure

```
data/songs/eval_set/
  metadata.yaml
  bachata/
    <track>.mp3
  kizomba/
    <track>.mp3
```

## Attribute taxonomy

| Attribute | Meaning |
|---|---|
| `cut_intro` | Song ripped from a dance video that starts partway through (intro clipped) |
| `has_break` | Song contains at least one audible break (energy drop) |
| `has_peak` | Song contains at least one energy peak section |
| `uniform_energy` | Steady energy throughout, no obvious structural contrast |
| `tempo_ambiguous` | BPM is ambiguous (double-time vs half-time) |

## Per-track metadata fields

- **file**: relative path from `eval_set/`
- **style**: `bachata` or `kizomba`
- **source**: `official_video` or `youtube_dance_video`
- **paired_with**: relative path to the paired version (same song, different cut) or `null`
- **attributes**: list of attributes from the taxonomy above
- **notes**: free-text description

## Why paired tracks matter — the "find 1 from mid-song" problem

Dancers rarely start a song from its first second. They walk onto the floor, hear the music, and must find the "1" — the start of a musical phrase — from whatever beat happens to be playing.

Many of our eval tracks are ripped from YouTube dance videos, which are themselves clipped mid-intro. So the mp3 file starts on (say) beat 3 of measure 11, not beat 1. This is exactly the problem the DSP has to solve when a dancer joins a song at an arbitrary point.

Where possible we pair each dance-video cut with the full **official video** of the same song, so the pipeline can be validated on both the clean case (official: first beat of the mp3 is beat 1 of the song) and the hard case (cut: first beat is somewhere in the middle of a musical phrase).

### Current pairs

| Cut (dance video) | Official (full) |
|---|---|
| `bachata/Bachata_Musicality_12_...` | `bachata/Romeo_Santos_El_Chaval...Canalla_Official...` |
| `kizomba/Charbel_-_E_Magia_Ben_Ana` | `kizomba/Charbel_-_E_Magia_Official_Video_4K` |
| `kizomba/Tony_Pirata_..._Teu_Toque` | `kizomba/Filomena_Maricoa_-_Teu_Toque_Official...` |

Run `python tmp/run_eval.py --pair` to print both sides of each pair side-by-side.

## Section colors (timeline bands)

`plot_timeline()` shades each section with a label-specific color (alpha scaled by relative energy). Keeping the palette documented here makes it discoverable when reading notebook output.

| Label | Hex | Notes |
|---|---|---|
| `spoken_intro` | `#34495e` | dark blue-grey — spoken dialog/narration before the music starts (Phase 11) |
| `intro` | `#4fc3f7` | light blue |
| `main` | `#d0d0d0` | neutral grey |
| `break` | `#f4d03f` | warm yellow |
| `short_break` | `#e67e22` | warm orange — 1-phrase drops that match a break branch |
| `build` | `#f39c12` | saturated orange |
| `peak` | `#e74c3c` | deeper red |
| `instrumental` | `#16a085` | teal — mid-song vocal-drop, energy-high passage (Phase 10) |
| `outro` | `#7b5aa6` | saturated purple (distinct from `main` even at low alpha) |

## Running the eval

```bash
python tmp/run_eval.py              # all tracks
python tmp/run_eval.py --fast       # fast subset (4 tracks)
python tmp/run_eval.py --style kizomba
python tmp/run_eval.py --attribute has_break
python tmp/run_eval.py --pair       # side-by-side paired tracks
```

## Adding tracks

1. Place the `.mp3` in the appropriate style subdirectory.
2. Add a track entry to `metadata.yaml` with all fields.
3. Run `python tmp/run_eval.py` to verify it loads.
4. If it has a paired version, add `paired_with` on both entries.

## Goal state

16-24 tracks with balanced coverage across:
- Styles: bachata, kizomba (and eventually semba, zouk)
- Sources: official videos and dance-video cuts
- Attributes: at least 3 tracks per attribute
