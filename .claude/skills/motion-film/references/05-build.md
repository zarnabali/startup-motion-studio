# Build — style frames, then the parallel shot build (tools/film-engine)

## Workspace
`projects/<job>/film/` (created by `new_film.py`): `index.html` (loads film.json, core.js, ui.js, shots/G*.js),
`core.js` (engine: springs, camera, words/rise, cursor, pixel assembly, palette filter), `ui.js` (your UI kit),
`render.py`, `sfx.py`, `vo.py`, `assets/` (fonts, brand, img), `ref/` (remakes: reference frames + audio), `out/`.
`film.json` holds fps, size, frames, cuts, beats, groups, `tokens` (brand colours → `CORE.T`), `fonts`, `preload`
(every asset path, so nothing renders half-loaded), `scripts` (extra JS files to load before the shots), `fast`.

## Engine contract
- `SHOT({id, f0, f1, render:(lf, F) => html})` — return a full-frame HTML string; pure function of F.
- Springs: `CORE.sp(F, f0, 'ui'|'box'|'heavy'|'soft')`, `CORE.spv(F, f0, a, b, preset)`; multi-target
  `CORE.track(F, [[f0,v0],[f1,v1],…])`; stretchy selection `CORE.indicator`; text swap in a morphing box
  `CORE.swapAlpha`; seamless loop `CORE.loopF`.
- Easings `CORE.E.*` (lin, inQ, inC, outQ, ioQ, outC, ioC, outQuart, ioQuart, outExpo, ioExpo, brand); keyframes
  `CORE.kf(F, [[f,v],…])`; measured motion `CORE.samples(F, f0, arr)`; camera `CORE.cam(F, [[f,zoom,x,y],…])` +
  `CORE.camera(html, {s,tx,ty,rx,ry})`; text `CORE.rise`, `CORE.words`, `CORE.typed`, `CORE.gtext`; logo
  `CORE.mark`, `CORE.wordmark`; images `CORE.img`; seeded `CORE.rand`; tokens `CORE.T` (`T.o` = accent).
- Slam moves: add `[f0, f1, subframes]` to `film.json.fast` (motion blur); list hard cuts in `film.json.cuts`
  (never blurred across; full renders split into segments there).
- Inserting a shot mid-film: wrap later shots' render functions with a time offset instead of rewriting their maths.

## Style frames gate (3–5 stills)
Before any group is built: Claude builds the `ui.js` core components + one hero shot per group (opener, an
AI-at-work beat, a b-roll + tag beat, the finale), renders `PY render.py stills out/stills <frames>` (remakes:
`compare out/stills <frames>` = ref | ours) and shows the owner. Fix until approved.

## Parallel build (one agent per group, contiguous frames)
Each agent gets `BRIEF_GROUP.md` (shot rows from SPEC, LOOK.md, swap rules, ui.js components, the engine contract
above, "write ONLY shots/Gx.js") — this file is the shared animation guide so groups match. Method per shot:
1. Read its SPEC rows (+ `ref/full` frames when remaking; MEASURE with numpy: ink bboxes, typing counts, cursor tips,
   camera scale/offset, fade timings → drive motion with `CORE.samples`).
2. Render 3 stills per beat (start, middle, settled) + 2 frames into every transition (≤ 15 per call); look at
   them; iterate. Never claim a match without viewing the frames.
3. Report table: shot | frames | MATCHES / CLOSE / ROUGH | residual issue | spec errors.
Agents run in parallel (background); the director integrates, then runs the draft.

## Rendering
- Draft (rhythm / animatic): `PY render.py draft out/draft --jobs 2` (half resolution, 1 sample/frame).
  Re-render only touched shots: `PY render.py draft out/draft F0 F1 --noenc`, then encode all `d_%04d.png` once.
- QA sheets from the draft (no new render): `PY render.py qa out/qa --from-draft`.
- Full: `PY render.py full out/full 0 <frames> --jobs 2 --pipe` (x264 segments, no PNGs on disk) →
  `PY render.py concat out/full out/audio/mix.wav`; remakes: `render.py split out/full` = original | ours QA video.
- Other shapes (9:16, 4:5, 1:1): copy the film folder, change `w`/`h` in film.json, re-lay out each shot with
  `CORE.W`/`CORE.H` (never crop the 16:9 master).
- After EVERY render grep the logs (`out/<dir>/_*.log`) for `PAGE ERRORS` — a shot that throws renders blank.
- Performance (software raster): no `backdrop-filter` in stacked/scaled layers, no giant box-shadows as masks, no
  drop-shadow on layers scaled > 2×. `RENDER_GPU=1` tries GPU raster (measure: it can be slower).

## Gotchas
Measure text with canvas `measureText` (not DOM rects under camera scale); visibility:inherit for children of hidden
parents; z-index on every layer; wait for fonts before measuring; exact 0/1 at easing ends; never `Math.random`;
images in cards: container aspect = image aspect (no cropping).
