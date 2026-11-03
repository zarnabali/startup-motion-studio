# Assets — images are generated, everything else is built in code

## A. What the image tool makes (`tools/make_image.py`) — ONLY these
| Kind | Spec notes | Used by |
|---|---|---|
| B-roll stills | the product's world without people (desk, shop, kitchen, warehouse, street…); 16:9 1536×1024; leave clean areas for tags | T4, T15, T23 |
| Textures | macro surfaces of the category (paper, fabric, metal, screen glow); 1024×1024, edge-to-edge | T3 drop montage |
| Cut-outs | one object per image, transparent background, consistent soft studio light | cards, T9, T14, T16 |
| Device-on-surface plates | phone/laptop on a real surface, screen pure black and unobstructed, 3/4 top-down | T23 (UI composited in code) |

Rules: the style lock + avoid list from `brand/IMAGE_STYLE.md` are added to every prompt automatically; `--real` for
anything that must pass as a real photo. No people unless BRAND_BRAIN §7 allows them; no text or logos in images; one
approved hero per recurring object, passed as `--ref` for continuity. Inspect every image at full size; regenerate
artefacts (max 3 tries). Never scrape images from Pinterest, Google or competitors.
Command: `PY tools/make_image.py --spec projects/<job>/03-assets/specs/<id>.md --out projects/<job>/film/assets/img/<id>_v1.png [--ref <img>] [--real]`.
Spec file = what, where in the frame, aspect, what must stay empty, input images.

## B. What Claude builds in code (never generated)
All UI (the `ui.js` kit from the owner's real screenshots — `ui-kit.md`), all type, the logo (from `brand/logo`),
glows, gradients, cursors, tags, charts, counters.

## C. Logo (once per film workspace)
`new_film.py` copies `brand/logo/wordmark.svg` + `mark.svg` into `film/assets/brand/`. PNG only: trace to SVG with a
transparent background and check the edges at 400 % zoom. Need halves for T1? Split the SVG into two files.

## D. Stills → "clips" (no video model needed)
Log-zoom push 1.00 → 1.06 over the shot, slow 10–30 px drift, a light-sweep gradient (screen blend) passing once,
2–3 % grain, and for depth: split a cut-out foreground from the background and move them at different speeds.
Only if the owner supplies a key: image-to-video (Veo / Kling via fal.ai) for 2–4 s of real motion.

## E. Optional real stock (owner approval per clip)
Pexels / Pixabay / Mixkit free licences allow commercial use without attribution (check each clip's licence).
No identifiable people or third-party logos unless cleared. Keep `03-assets/LICENSES.md` (URL, licence, date).

## F. Ledger
`03-assets/ASSET_BOARD.md`: id · kind · file · source (prompt file / stock URL) · shots · licence. Contact sheet of all.
Run `PY tools/optimize_assets.py projects/<job>/film/assets` before renders (opaque PNG → JPEG ≤ 2160 px).
