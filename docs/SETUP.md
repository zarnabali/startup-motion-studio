# Setup guide

This takes about 10 minutes. You end with a working studio and a rendered test video.

## 1. Requirements
| Need | Why | Get it |
|---|---|---|
| **Claude Code** | the studio's "director" | https://claude.com/claude-code (CLI, desktop app or IDE extension) |
| **Python 3.10–3.13** | render engine, audio, checks | https://www.python.org/downloads/ (Windows: tick "Add python.exe to PATH") |
| **Git** | to download and update the studio | https://git-scm.com/downloads |
| ~3 GB free disk | Chromium, voice model, renders | |
| 8 GB RAM minimum, 16 GB recommended | parallel renders | |
| *(optional)* Codex CLI or an OpenAI API key | image generation | https://github.com/openai/codex · https://platform.openai.com |

You don't need Node.js, a GPU or any paid video AI.

## 2. Install
```bash
git clone https://github.com/zarnabali/startup-motion-studio.git
cd startup-motion-studio
python tools/setup.py --voice
```
`setup.py` creates `tools/.venv`, installs the Python packages and Playwright's Chromium, and with `--voice` downloads
the Kokoro voice model (~340 MB) into `tools/tts/`. Nothing is installed system-wide.
Use `python3` instead of `python` on macOS / Linux if needed. Add `--stems` only if you want to split music into stems
(PyTorch, ~1 GB).

Your studio Python from now on (called `PY` in all docs):
- Windows: `tools\.venv\Scripts\python.exe`
- macOS / Linux: `tools/.venv/bin/python`

## 3. Test it (2 minutes)
```bash
cd examples/hello-film
../../tools/.venv/bin/python render.py stills out/test 20 100 175       # Windows: ..\..\tools\.venv\Scripts\python.exe
```
Open `examples/hello-film/out/test/` — you should see three frames of the demo. To watch it live, serve the folder
(`PY -m http.server 8000` inside `examples/hello-film`) and open http://localhost:8000 (Space = play, ←/→ = frame).

## 4. Image generation (optional)
`tools/make_image.py` picks the first that works:
1. **Codex CLI** signed in with ChatGPT (`codex login`), no API key needed.
2. **OpenAI API**: set `OPENAI_API_KEY` in your own shell or a `.env` that you never commit. Optional `IMAGE_MODEL`.
3. **Prompt only**: writes `<image>.prompt.txt` with the full prompt and your brand's style lock. Paste it into any
   image tool and save the result under the same name.

## 5. Your brand
Open the folder in Claude Code and say **"set up my brand"**. The `studio-onboard` skill asks ~9 questions, reads your
website, and fills `brand/`. Put in:
- `brand/fonts/`: your font files (free default: [Inter](https://rsms.me/inter/), `Inter-Regular.woff2` + `Inter-Medium.woff2`)
- `brand/logo/`: `wordmark.svg` + `mark.svg`
- real screenshots of your product when Claude asks for them.

## 6. Make something
- "Make a 45-second launch film for our app": `motion-film`
- "Remake the rhythm of this video for our product" + attach the file: `motion-film` in remake mode
- "Plan a month of LinkedIn and Instagram posts and make the first week": `social-content`

Claude stops at every gate (brief, script, style frames, transitions, animatic, final) and waits for your OK.

## Troubleshooting
| Problem | Fix |
|---|---|
| `playwright` can't find a browser | `PY -m playwright install chromium` |
| A shot renders blank | grep the render log (`out/<dir>/_*.log`) for `PAGE ERRORS` |
| Renders are very slow | see `brand/LEARNINGS.md` → "Render performance" (no backdrop-filter in scaled layers, `--jobs 2` max on 16 GB) |
| Text in the wrong font | font file missing in `brand/fonts` or not listed in `brand/tokens.json` → `fonts`; re-run `new_film.py` |
| `vo.py`: model files not found | `python tools/setup.py --voice` |
| Loudness check fails | re-run `sfx.py` (it measures and corrects to −14 LUFS) |
