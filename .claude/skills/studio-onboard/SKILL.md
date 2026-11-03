---
name: studio-onboard
description: >
  First-run setup for the Startup Motion Studio: checks the toolchain, then interviews the user about their startup
  and fills the brand kit (brand/BRAND_BRAIN.md, tokens.json, fonts, logo, IMAGE_STYLE.md, COMPETITORS.md) from their
  answers, their website and their screenshots. Use when the user first opens the studio, says "set up my brand",
  "onboard", "start", invokes /studio-onboard, or when motion-film / social-content finds the brand kit still empty.
---

# /studio-onboard — from zero to a filled brand kit (≈ 15 minutes)

Goal: every later film and post is checked against true, specific brand facts. Never invent a fact: unknown = ask, or
leave it marked `TODO`.

## Step 1 — Toolchain check (fix before anything creative)
Run and report in one short table (ok / missing + the fix):
- `python --version` (3.10–3.13) · Node is NOT needed.
- `tools/.venv` exists → else run `python tools/setup.py` (add `--voice` for local voice-over).
- `PY -c "import playwright, imageio_ffmpeg, librosa"` · Kokoro files in `tools/tts/` (only if VO wanted).
- Image provider: `codex --version` (signed in) or `OPENAI_API_KEY` set — else images fall back to prompt files the
  user pastes into any image tool. Never ask for, read out or store API keys or passwords; the user sets them.
- Smoke test: `cd examples/hello-film && PY render.py stills out/smoke 0 60 120` → look at the three stills.

## Step 2 — Interview (one message, numbered, each with a default or "skip")
1. Product name + website URL + one line (what it is, for whom, the result).
2. Who exactly is the audience? What do they want, what annoys them today?
3. The 3–6 features that exist TODAY, each as input → what the product does → output.
4. Proof you may say out loud (users, ratings, press) — with sources. Nothing else will ever be claimed.
5. Voice: 3 words; words you use / never use; the CTA line + URL.
6. Visual: brand colours (hex if known), fonts, logo files; people in visuals yes/no; photo style editorial or real.
7. Competitors (3–5) and brands whose videos they love (links welcome).
8. Channels they post on, and how often they can realistically post.
9. Standing rules ("never show X", "always Y").

## Step 3 — Research what you can instead of asking
- Read their website (WebFetch) for copy, features, colours (CSS custom properties / computed styles), fonts and the
  logo URL. Quote it back; the user confirms. Download nothing without the user's OK.
- Ask for real product screenshots (phone PNGs / web 2× captures) → `projects/_brand/screens/` — the UI kit is
  rebuilt from these later.

## Step 4 — Fill the kit
- `brand/BRAND_BRAIN.md` — every section; sources next to claims; `TODO` where unknown.
- `brand/tokens.json` — background, ink, card, line, the ONE accent (o) with a darker (oDeep), lighter (oLight)
  and tint (oTint) step, font stack + `fonts` list. Check accent-on-background contrast ≥ 3:1 for large type and ink
  on background ≥ 4.5:1; propose a fix if it fails.
- `brand/fonts/` — licensed files only (free default Inter, SIL OFL). Subset anything > 500 KB.
- `brand/logo/wordmark.svg` + `mark.svg` — trace PNGs to SVG if needed; never redraw.
- `brand/IMAGE_STYLE.md` — adapt the Style lock to their category (keep the headings).
- `brand/COMPETITORS.md` — table rows from their answers + a quick look at each competitor's site/socials.

## Step 5 — Confirm
Show a one-screen summary: product line, audience, features (input → AI → output), voice, palette swatches (as hex),
fonts, channels. Ask for corrections. Then suggest the first job:
- "Launch film (45–60 s, 16:9 + 9:16)" → `motion-film`
- "30-day social plan + first week of posts" → `social-content`
