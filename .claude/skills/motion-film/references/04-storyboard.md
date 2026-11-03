# Script gate — the state list on the beat grid (nothing is coded before the owner says OK)

## 1. SPEC.md — the script as a state list (always)
One row per beat/shot: `id | f0 | f1 | group | what is on screen (exact words) | VO line | feature it proves
(input → AI → output) | components (ui.js) | assets | camera | carrier into the next shot | SFX cue`.
Frames come from `film/film.json`. A state list, not a vibe: every row says exactly what is visible at the start and
the end of the beat. Pattern that works for UI films: **one container never cuts** — one shape morphs from state to
state and a cursor drives each change.

## 2. FILM_MAP.md — remakes only: reference shot → our shot, same time ranges
Columns: t-range (from the reference's cut list) · ref technique ids · our shot (what is on screen, exact copy) ·
feature it proves · assets. Keep the reference's hook, drop, pacing (shot count ±10 %, durations ±10 %) and ending
structure. Swap content, never grammar. Swap rules: reference brand colours → our accent (`paletteFilter` can re-hue
leftovers), reference name → ours, people → objects/cards of the same size and motion, every number = example data.
SPEC boundaries are often ±4 frames off the reference — build agents verify against `ref/full`.

## 3. Beat map (inside SPEC.md)
From `beats.json`: BPM, beat length, bar boundaries, the drop frame. The drop lands on the key visual. Every scene
starts on a beat or a measured accent (± 0.15 s for reveals, ± 0.10 s for small entrances). Nothing still for > 1 s
except the key idea's one-beat hold and the end card.

## 4. Copy rules
Sentence case, ≤ 6 words per frame unless it's a streamed answer, ≤ 3 words/second, every line held long enough to
read twice. Brand words from BRAND_BRAIN §6. No prices, dates or metrics except sourced ones. VO only where it adds
meaning: text that says itself on screen gets no VO. VO lines are written into `vo.json` with their start times.

## 5. Present to the owner
SPEC (+ FILM_MAP) + the 3–5 decisions only they can make (closing line, music licence, formats, VO yes/no). Stop and
wait. After approval the script is frozen: used word for word.
