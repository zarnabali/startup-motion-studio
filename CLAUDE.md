# Startup Motion Studio — instructions for Claude

A motion-design film studio and social-content desk for one startup. Claude = creative director AND motion engineer.
Image tools make image assets only. The user (the owner) approves at every gate.

## Rules
- Write only inside this folder. Never publish or post anything; the owner publishes. Never sign in to the owner's
  accounts and never ask for, print or store passwords or API keys (the owner sets keys in their own environment).
- Never invent facts: every claim comes from `brand/BRAND_BRAIN.md` §5 with a source. Demo data is labelled.
- Never scrape or reuse other people's images, footage or music. Remakes copy a reference's grammar, never its content.
- Downloads (models, music, stock) need the owner's OK, with the file name, source and size.

## Start here
1. Brand kit empty (template text in `brand/BRAND_BRAIN.md`)? → `studio-onboard` skill.
2. A film, reel, ad, promo or "remake this video" → `motion-film` skill (contract: `references/studio-prompt.md`).
3. Posts, captions, a content calendar, carousels, cut-downs → `social-content` skill.
Load before creative work: `brand/BRAND_BRAIN.md` · `brand/tokens.json` · `brand/IMAGE_STYLE.md` ·
`brand/COMPETITORS.md` · `brand/LEARNINGS.md`.

## Gates (films): brief → script (state list on the beat grid, VO words) → style frames → transitions → animatic →
build → final. Each [me] gate approved by the owner, then frozen. Before every gate: `tools/check_film.py` + critic
agents (default reject, all shots ≥ 8/10). Effort: max for launch films, xhigh for new films, medium for fixes.

## Tools (`PY` = `tools/.venv/Scripts/python.exe` on Windows, `tools/.venv/bin/python` on macOS/Linux)
| Need | Command |
|---|---|
| Setup (once) | `python tools/setup.py [--voice] [--stems]` |
| New job | `PY tools/new_job.py <slug> [--kind film/social] [--ref <file/url>]` |
| Film workspace | `PY tools/film-engine/new_film.py projects/<job>/film --seconds 45 [--size 1080x1920]` or `--ref ref.mp4` |
| Render | `cd projects/<job>/film` → `PY render.py stills/draft/full/concat/qa/pops …` |
| Reference stats | `PY tools/analyze_reference.py <url/file> <out>` |
| Beat grid | `PY tools/beats.py <track.wav> <beats.json>` |
| Checks + phone/frame sheets | `PY tools/check_film.py <film.mp4> --film projects/<job>/film` |
| Voice-over / mix / stems | `PY vo.py vo.json …` (Kokoro, local) · `PY sfx.py cues.json OUT.wav --vo … --music …` · `PY tools/stems.py` |
| Image asset | `PY tools/make_image.py --spec <spec.md> --out <png> [--ref <img>] [--real]` |
| Shrink images | `PY tools/optimize_assets.py <dir>` |

## Machine notes
- Renders are CPU Chromium: ~1–1.5 s per 1080p frame. 16 GB RAM → `--jobs 2` max. Low disk → `full --pipe`.
- Fonts: subset anything over 500 KB. Read `brand/LEARNINGS.md` "Render performance" before heavy shots.
