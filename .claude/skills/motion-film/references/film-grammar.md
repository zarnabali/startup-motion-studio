# Film grammar — Gemini-grade product-film techniques and how to build them in the engine

Source: frame-by-frame study of a Gemini-launch-style startup film + claude-motion-design rules (MIT).
All are pure functions of F (`CORE.*`, `UI.*`). The last column is an example; map each to YOUR product.

| Id | Technique | Build recipe (engine) | Example use |
|---|---|---|---|
| T1 | Wordmark split | wordmark as two vector halves; `spv(F,f0,0,gap,'heavy')` widens the gap; content row slides out of the gap | logo halves part and pour the feature chips |
| T2 | Chip stream | row of `UI.chip` with icons; x = constant velocity + spring settle per chip; slight scale stagger | a row of feature names streaming past |
| T3 | Drop-flash montage | 5–8 shots of 4–5 frames on the drop; alternate macro UI / texture / mark; hard cuts listed in `film.json.cuts` | chips over product textures / macro UI on the drop |
| T4 | Texture b-roll | Codex still, `camera()` slow push (log-zoom 1.00→1.06) + light sweep gradient + grain; 0.5–1.5 s | product or workplace stills (no people unless allowed) |
| T5 | Macro-UI tilt | UI at 2–4× scale, `camera({rx:8–18, ry:-10–10, persp:1800})`, edge blur via a second blurred copy masked by a gradient | the app UI with accent glows |
| T6 | Shimmer loader | mark spinner + "Reading …" + 2–4 skeleton bars with a moving gradient `background-position` driven by F | "Reading 69 files…" |
| T7 | Streaming answer | words appear in groups (`CORE.words`/`rise`), list items tick ✓ with `sp(...,'ui')`, numbers count | the AI's answer or plan |
| T8 | Logo glow | `mark()` large on black + 2 radial glows breathing (sin of F), slow rotation ≤ 6° | the brand mark |
| T9 | Z-space collage | 15–30 assets placed in 3D (translateZ), camera dolly; parallax by depth | product cut-outs, screenshots, cards |
| T10 | Toggle morph | segmented control thumb springs; background crossfades light↔dark under it | Before ⇄ After, Off ⇄ On |
| T11 | Gradient greeting | huge "Hi, I'm <product>," with `gtext()` moving gradient (background-position from F) | opener of the assistant beat |
| T12 | Text→device match cut | same string, same position, cut into a phone screen render; camera keeps velocity | greeting continues inside the phone |
| T13 | Type-on prompt + glow | `UI.promptBar`, `typed(s, n)` with human cadence table (fast words, pauses at spaces/punctuation), animated gradient border glow | a real user request typed into the product |
| T14 | Glass cards assemble | `UI.glass` cards fly in on `box` springs, overlap stack → grid | results cards |
| T15 | B-roll + AR tag | pill with leader line pinned to a point on a still; line draws (stroke-dashoffset from F); pin pulses | a label pinned on a real object |
| T16 | Annotate the artifact | SVG strokes drawn on a flat-lay (dash offset), callout bubble springs in | circle the change + callout |
| T17 | Chip → sheet | glowing chip pressed (cursor/press), bottom sheet springs up (`ui`), answer streams | "Find what's missing" |
| T18 | Whip | 8–12 frames: big directional translate + `fast` subframe blur in film.json; cut at peak velocity, direction matched | between sections |
| T19 | Chip select zoom | camera pushes into the chosen chip as it fills with the accent | the chosen option |
| T20 | Tile carousel | category tiles slide on black; active tile scales | the product's main sections |
| T21 | Icon macro | one UI icon at 6–10× scale; morph or gets the mark sparkle | the app icon |
| T22 | Before/after overlay | two-colour diff overlay sweeps across an artifact | before/after of the result |
| T23 | Device on surface | Generated plate of a phone lying on a surface (blank screen) + UI composited with CSS `matrix3d` corner-pin | phone on a desk with the live UI |
| T24 | Voice wave | dark screen; 3 layered accent radial gradients modulated by sin/noise of F | voice input |
| T25 | Drag-drop | cursor path (kf), file stack follows with lag spring, drops into chat | files dropped in → "23 items found" |
| T26 | Cursor hover tooltip | macOS cursor eases to icon; tooltip springs (ui) | "Ask <product>" |
| T27 | Era line | blur-in left→right per word + glow halo; brand word gradient | the closing line |
| T28 | Logo assembly | point of light → seeded particles (or fabric swatch pixels) converge on the mark's sampled points, `heavy` springs | pixels converge into the logo |

## Motion law (from claude-motion-design, apply everywhere)
- Camera: one transform per shot container; keys `[f, zoom, x, y]`, zoom interpolated in LOG space; never zoom
  in-then-out back-to-back. Beat punches +0.012 per beat, +0.03 per bar after the drop, exponential decay.
- Shared elements carry every handoff (the chip becomes the button, the bubble becomes the sheet).
- Exits are geometric ×1.5 faster than entries; the next shot enters already moving in the exit's direction.
- No frozen frame except the final hold — keep a micro-drift alive.
- Targeted blur only on 1–3 slam moves; never blur readable text; supersample static type if needed.
- Reveals may shift ≤ 0.15 s (small entrances ≤ 0.10 s) to land on a music cue.
