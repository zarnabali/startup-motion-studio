# Learnings — append after every job (dated). Claude reads this before creative work.

Each owner note that a check should have caught becomes a line here AND a check in
`.claude/skills/motion-film/references/06-qa.md`.

## Starter lessons (from the film that this studio was built on)
- **Method beats tools.** A film assembled from screenshots + AI stills as title-card scenes was rejected ("no flow,
  assets glued together"). Rebuilding the UI in code and animating it with springs, frame-locked to a strong reference,
  was approved. Remake grammar, never content.
- **Photos must not look AI.** Glossy, colour-sorted, symmetrical "editorial" images were all rejected. Use `--real`.
- **No cropped images** in cards or tiles: the card's aspect = the image's aspect.
- **Voice-over only where it adds meaning.** Text that says itself on screen (questions, labels) gets no VO.
- **The screen never goes blank.** `check_film.py` caught 3 black frames at a shot boundary after the owner had
  already seen the cut — run it before every review.
- **Logo rules are absolute.** A small mark placed inside the wordmark was the first note on the first draft.

## Render performance (software Chromium, ~1-1.5 s per 1080p frame on a 2017 laptop)
- Pathological frames (50-90 s) came from `backdrop-filter` inside stacked/motion-blurred layers, a 5000 px
  `box-shadow` used as a mask, and `filter: drop-shadow` on layers scaled 3-14×. Use solid rgba tints, clip with
  `overflow:hidden`, fade glows out once a layer outgrows the frame.
- 16 GB RAM: max 2 parallel jobs (`--jobs 2`). Low disk: render finals with `full ... --pipe` then `concat`.
- An empty HUD box printed in every frame → `#hud:empty{display:none}` (already in index.html).
- Builders call easings core.js lacks → the shot errors and renders blank. Grep render logs for `PAGE ERRORS`.
- Big font files (2+ MB) crash renderers: subset them.

## Job log
