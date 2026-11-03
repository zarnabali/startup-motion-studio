# The method in plain words — and where it lives in this studio

Based on the public course "How to build a motion design studio with Opus 5.5" (@0xMovez on X, 12 steps). Big idea:
**"the prompt is 10 % of the video, the harness is 90 %."** The harness = render engine + reference + beat grid +
sound + a loop where Claude looks at its own frames and fixes them.

| # | Step | In plain words | In this studio |
|---|---|---|---|
| 01 | Pixels | Claude can't output video. It writes a program with `seek(t)` that draws any moment; a headless browser screenshots every frame; ffmpeg glues them. Same input = same video. | `tools/film-engine` |
| 02 | Setup | Claude Code (it can render, listen, look at frames), a house-rules file, high effort: medium for fixes, xhigh for new films, max for launches. | `CLAUDE.md`, effort rule in the skill |
| 03 | One-liner | "Make a dynamic 15 s showreel… go all out" works because it names a genre — but every one-liner film looks the same. | Only to test the engine. Real films start from a brief. |
| 04 | Brand | Point it at the real product: real screenshots, logo, colours, music. | `brand/` + `studio-onboard` skill |
| 05 | Reference | Without a reference Claude falls back to "centred text on a gradient, everything fading in". Give a frame or a video; take the grammar, never the content. | Remake mode (`new_film.py --ref`), LOOK.md |
| 06 | Spec | A **state list**, not a vibe: beat-by-beat states, build rules, gotchas. "One container never cuts": one shape morphs, a cursor drives each change. | SPEC.md (04-storyboard.md) |
| 07 | Engine | The seek(t) page + a renderer that pipes frames to ffmpeg, subframes blended for motion blur. | `render.py` draft / full --pipe / concat |
| 08 | Springs | Expensive motion has mass: closed-form springs. A value with several targets = sum of one spring per change. | `CORE.sp / track / indicator / swapAlpha / loopF` |
| 09 | Sound | Measure the track → beats, downbeats, hits. State changes on beats, big moments on downbeats, SFX on hits. | `tools/beats.py`, `sfx.py`, `vo.py` |
| 10 | Overnight brief | Long jobs: a director's brief (film in one line, references, look, beat sheet, gates, deliverables) + one shared animation guide for parallel agents. | `studio-prompt.md` + `BRIEF_GROUP.md` |
| 11 | Critique | Claude must LOOK: contact sheet, strips around fast moves, **phone test at 360 px**, harsh 1-10 scores, fix the 3 worst, repeat until all ≥ 8. | `tools/check_film.py` + critic agents |
| 12 | Ship | Every format from one timeline (re-layout, not crop); package the pipeline as a skill. | This kit + `social-content` skill |

## Rules that came out of it
1. Banned defaults: centred title on a gradient, everything fading in, corner labels / frame borders, glow on UI
   chrome, generic particle bursts, dips to black/white.
2. Something new every 2-4 s; hook in the first 2 s; the key idea sits still for a beat.
3. Every cut has a carrier (a shape, line or camera move) — crossfade only as a last resort.
4. Stagger 2-4 frames, overlap motions, never move a whole layout as one block.
5. Gates: brief → script → style frames → transitions → animatic → build → final. Approved work is frozen.
6. Checks before every gate. 7. Notes protocol: every uncaught error becomes a permanent check.
