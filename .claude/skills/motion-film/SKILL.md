---
name: motion-film
description: >
  A motion-design film studio for startups: launch films, feature films, product promos and social reels with
  Apple / Linear / Gemini-grade motion. Claude is director AND motion engineer: it rebuilds the product UI in code and
  animates everything with closed-form springs in a deterministic seek(t) HTML engine (tools/film-engine), with a
  local voice-over, synthesized sound design, automated checks and a critic loop. Works from a brief or by REMAKING a
  reference video's grammar frame-locked for your brand. Use whenever the user asks for a video, ad, reel, launch
  film, promo, explainer, "remake this video", shares a reference video, or invokes /motion-film.
---

# /motion-film — gates, contract, engine

**"The prompt is 10 %, the harness is 90 %."** The harness = the seek(t) engine + a reference + a measured beat grid
+ voice/sound + checks + a critique loop where Claude looks at its own frames.
Read before every film: `references/studio-prompt.md` (the contract) and `brand/LEARNINGS.md`. Once per user:
`references/course-notes.md` (the method in plain words).

**Before the first film:** `brand/BRAND_BRAIN.md` and `brand/tokens.json` must be filled. If they still hold the
template text, run the `studio-onboard` skill first.

## Roles & effort
- **Claude = the whole studio**: director, writer, designer, animator, sound and render engineer. Effort: max for a
  launch film, xhigh for a new feature film, medium for fixes and re-renders.
- **Critic agents** (separate, read-only, default reject). Claude never approves its own work.
- **Images**: `tools/make_image.py` (Codex CLI, OpenAI API or prompt-only) — image assets ONLY, never whole scenes.
- **Owner** (the user) approves every `[me]` gate. Never publish or post anything; the owner publishes.

## Non-negotiables
1. **Real product only.** Screens are rebuilt in code from the owner's real screenshots (`ui.js`), never pasted, never
   an invented feature. **Every feature = input → AI magic → output**, 2–5 s each, self-explanatory on screen.
2. **Photos must not look AI** (`make_image.py --real` for anything photographic). Inspect each image at 100 %. No
   scraped images (Pinterest, Google, competitors): generate originals or use licensed stock with a licence note.
3. **Frame-pure engine:** everything from F inside `seek(t)`; no CSS transitions, timers, Math.random, Date, network.
   Springs = Framer Motion physics in closed form (`CORE.sp`, multi-target `CORE.track`, `indicator`, `swapAlpha`).
4. **Motion law:**
   - **Banned defaults:** centred title on a gradient · everything fading in · corner labels / frame borders · glow on
     UI chrome · particle bursts · dips to black or white (the screen never goes blank) · cropped images in cards.
   - Hook in the first 2 s · something new every 2–4 s · the key idea sits still for a beat.
   - Nothing linear except machines · stagger 2–4 f · overlap · **every cut has a carrier**.
   - Headlines ≥ 5 % of frame height, readable at 360 px wide; title-safe 5 %, action-safe 3.5 %.
5. **Truth:** no invented metrics, prices, dates, customers or reviews; demo data is labelled. End on the CTA + URL
   from BRAND_BRAIN §6. Logo used as given.
6. **Sound:** brand VO (`vo.json` → `vo.py`, local Kokoro) on the beat grid; VO only where it adds meaning (text that
   says itself gets none). Music ducked ≥ 6 dB under the voice. SFX on ~1 action in 5. −14 LUFS, TP ≤ −1.
   Licensed music only in anything delivered. A reference's song may only sit under an `INTERNAL-REVIEW-ONLY` cut.
7. **Owner's standing notes** in BRAND_BRAIN §8 and LEARNINGS override defaults.

## Phases & gates (approved work is frozen)
| # | Phase | Output | Gate |
|---|---|---|---|
| 0 | Intake: `python tools/new_job.py <slug> [--ref <file/url>]`; fill `{{TOPIC, AUDIENCE, TAKEAWAY, SECONDS, SHAPE, NARRATION}}` | `00-brief.md` | |
| 1 | **Brief**: 3 lines (what, for whom, takeaway) + only questions that change the video, each with a default | `00-brief.md` | **[me]** |
| 2 | Research + reference: `references/02-research.md`; if remaking, deconstruct it (`references/01-reference-analysis.md`); `beats.py` on the music → beats.json | `01-reference/BREAKDOWN.md`, `02-research/RESEARCH.md` | |
| 3 | **Script**: one idea per beat, VO lines + on-screen words, as a **state list on the beat grid** | `04-storyboard/SPEC.md` (+ FILM_MAP.md when remaking) | **[me]** |
| 4 | **Look + style frames**: `film/design/LOOK.md` + 3–5 full-res stills with real words | `film/out/stills` | **[me]** |
| 5 | **Transitions**: one panel per cut naming its carrier | `04-storyboard/TRANSITIONS.md` | **[me]** |
| 6 | Assets: UI kit from screenshots (`references/ui-kit.md`), images, VO synth, music bed (`references/03-assets.md`, `music.md`) | `film/assets`, `out/audio` | |
| 7 | **Animatic**: every beat timed, simple motion, `render.py draft` + VO + temp music | `out/draft/draft.mp4` | **[me]** |
| 8 | Build: shot groups in parallel (one agent per `shots/Gx.js`, shared `BRIEF_GROUP.md`); 3 stills per beat (start, middle, settled) | `film/shots/*.js` | |
| 9 | Checks + critique loop (≥ 3 rounds, all shots ≥ 8) → full render `--pipe` → mixes → `check_film.py` | `06-qa/`, `out/full/checks/CHECKS.md` | |
| 10 | **Final**: MP4(s) per channel (re-laid out, never cropped) + frame sheet + `POST_COPY.md`; notes protocol | `07-deliver/` | **[me]** |

Hand off to the `social-content` skill for cut-downs, captions and a posting plan after the final gate.

## Tools (from the studio root; `PY` = `tools/.venv/Scripts/python.exe` on Windows, `tools/.venv/bin/python` elsewhere)
| Need | Command |
|---|---|
| Setup (once) | `python tools/setup.py [--voice] [--stems]` |
| New job | `PY tools/new_job.py <slug> [--ref <file/url>]` |
| Film workspace | `PY tools/film-engine/new_film.py projects/<job>/film --seconds 45 [--size 1080x1920]` · remake: `--ref ref.mp4` |
| Reference stats | `PY tools/analyze_reference.py <url/file> projects/<job>/01-reference/stats` |
| Beat grid | `PY tools/beats.py <track.wav> projects/<job>/film/beats.json` |
| Stills / draft / full / concat / qa / pops | `cd projects/<job>/film` then `PY render.py stills OUT F…` · `draft out/draft --jobs 2` · `full out/full 0 N --jobs 2 --pipe` · `concat out/full [mix.wav]` · `qa out/qa --from-draft` · `pops out/full/film_silent.mp4` |
| Voice-over | `PY vo.py vo.json out/audio/vo_track.wav` |
| SFX + music + VO mix | `PY sfx.py cues.json out/audio/mix.wav --vo out/audio/vo_track.wav --music track.mp3 --music-gain 0.5 --duck 0.55` |
| Stems (remove a reference's voice, internal only) | `PY tools/stems.py in.wav out/audio/stems` |
| Automated checks + review sheets | `PY tools/check_film.py out/full/film.mp4 --film projects/<job>/film` |
| Image asset | `PY tools/make_image.py --spec spec.md --out film/assets/img/X_v1.png [--ref img] [--real]` |
| Shrink images | `PY tools/optimize_assets.py projects/<job>/film/assets` |
| Preview | serve `film/` (`PY -m http.server` inside it) and open `index.html` (Space play, ←/→ frame, `?f=` deep link) |

Render rules (`brand/LEARNINGS.md`): no backdrop-filter in stacked/scaled layers, no giant shadows as masks, fade glows
on layers scaled > 2×, max 2 parallel jobs on 16 GB, grep logs for `PAGE ERRORS` after every render.
Engine API + build method: `references/05-build.md`. Technique catalogue: `references/film-grammar.md`.
