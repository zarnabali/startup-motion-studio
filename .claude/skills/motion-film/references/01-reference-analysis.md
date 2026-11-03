# Deconstruct the reference (remakes only — no building yet)

Goal: know the reference so precisely that we can rebuild its grammar frame-locked with the brand's own content.
Only remake videos the owner has the right to use as a reference. Take the grammar (rhythm, layout, transitions,
camera), never the content, footage, logo or music.

## 1. Tools (run all three; `PY` = the studio venv python)
```bash
# a) film workspace: every frame (0-based jpg), audio, hard cuts, beat grid, 4 contiguous shot groups, 6-frame sheets
PY tools/film-engine/new_film.py projects/<job>/film --ref "<ref.mp4>" --groups 4
# b) shot stats: keyframes in/mid/out, palette, motion hints, pacing, cut-on-beat %  (also accepts a URL, via yt-dlp)
PY tools/analyze_reference.py "<ref.mp4>" projects/<job>/01-reference/stats --sample 0.25
# c) review sheets (1 fps frame sheet, 2 fps contact sheet, 360 px phone sheet) of the reference itself
PY tools/check_film.py "<ref.mp4>" --out projects/<job>/01-reference/sheets
```

## 2. Read every sheet (non-negotiable), then the 6-frame sheets around fast moves
Also extract the audio accent map (`tools/beats.py ref/audio.wav`) and energy per 5 s: the drop, the plateau, the outro.

## 3. Write `01-reference/BREAKDOWN.md`
- Header: duration, fps, shots, median shot, cuts/10 s, BPM, drop time, what the film is an homage to (name the style).
- **Timeline table**: t-range · what is on screen · technique ids (see `film-grammar.md`). Note continuous moves that
  are NOT cuts (most modern launch films have 10–20 hard cuts and many morphs).
- **Technique catalog**: every distinct technique, defined so it can be coded.
- **Why our last film lost** (if any): concrete deltas.
Standard to hit: every shot of the reference is in the table with a technique id; nothing is "etc.".
