# Contributing to Startup Motion Studio

Thanks for helping. Founders use this studio to make launch films and social content with Claude Code. The best
contributions make the films better, the setup easier, or the rules sharper.

## Ways to help
| Kind | Examples | Where |
|---|---|---|
| 🐛 Bug report | a render crash, a check that's wrong, setup failing on your OS | Issue → "Bug report" |
| ✨ Engine feature | a new `CORE` helper, a new `ui.js` component, faster rendering | PR to `tools/film-engine/` |
| 🎬 Technique | a new motion technique (T29+) with a working build recipe | PR to `motion-film/references/film-grammar.md` + an example shot |
| 🧠 Skill improvement | a clearer gate, a better critic rubric, a new check born from a real mistake | PR to `.claude/skills/` |
| 📣 Social formats | platform spec updates, caption patterns, new post formats | PR to `social-content/references/` |
| 📚 Docs | setup on your OS, troubleshooting, translations | PR to `docs/` or `README.md` |
| 🎥 Showcase | a film you made with the studio (link + 1 frame + what you learned) | Issue → "Showcase" |

## Ground rules (these keep the studio trustworthy)
1. **Frame-pure engine.** Every frame is a pure function of the frame number: no timers, no `Math.random`, no `Date`,
   no network at render time, no CSS transitions. Use `CORE.rand(n, seed)` and springs.
2. **No brand data in the kit.** Example content uses neutral demo data. Never commit anyone's logo, screenshots, fonts
   or music without a licence that allows it.
3. **No copyrighted media.** No ripped songs, scraped images or downloaded footage, not even in examples.
4. **Truth rules stay.** Skills must never tell Claude to invent metrics, customers, prices or features.
5. **Never post or log in for the user.** Skills prepare files; humans publish.
6. **Cross-platform.** Python tools must work on Windows, macOS and Linux (use `pathlib`, no shell-specific syntax).
7. **Small and focused.** One change per PR. Match the surrounding style (short comments, compact code).

## Development setup
```bash
git clone https://github.com/zarnabali/startup-motion-studio.git
cd startup-motion-studio
python tools/setup.py
git checkout -b feat/<short-name>
```
Before opening a PR, run the smoke test (it must pass):
```bash
cd examples/hello-film
PY render.py full out/full 0 180 --pipe
PY sfx.py cues.json out/audio/mix.wav
PY render.py concat out/full out/audio/mix.wav
PY ../../tools/check_film.py out/full/film.mp4 --film . --hold 1.5     # all checks must say pass
```
If you changed `tools/film-engine/*`, copy the changed engine files into `examples/hello-film/` too (the example is a
film workspace, which holds its own copy of the engine).

## Pull request format
- **Title:** `type(scope): what changed`. Types: `feat`, `fix`, `docs`, `skill`, `perf`, `chore`.
  Example: `feat(engine): add CORE.morphPath for SVG shape morphs`.
- **Body:** fill in the PR template:
  - what and why;
  - how you tested it (OS + the smoke test);
  - before/after frames for visual changes (`render.py stills`).
- **Visual changes need proof.** Attach a still or a short GIF of the before and after.
- **Skill changes need a reason.** Name the real mistake or film that prompted it. Rules that come from real notes
  are the studio's strength.

## Writing a new technique (film-grammar.md)
Add a row: `| T29 | Name | build recipe using CORE/UI functions | example use |`, plus a minimal shot in a PR comment
or `examples/`, so reviewers can render it. Recipes must be pure functions of F.

## Writing a new check
Checks come from real failures. Add it to `motion-film/references/06-qa.md` under "Checks born from owner notes".
If it can be automated, add it to `tools/check_film.py` too, with a pass/FAIL line in `CHECKS.md`.

## Reporting security issues
Don't open a public issue. Use GitHub's "Report a vulnerability" (Security tab).

## Code of conduct
This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md). Be kind and specific, and assume good intent.
