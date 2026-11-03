# ui.js — your product's UI kit for films (rebuilt from real screenshots)

Why: launch films look premium because the interface is LIVE code at macro scale — text types, answers stream, chips
select, sheets spring. Screenshots pasted into phone frames can't do that.

## 1. Inputs
Ask the owner for real screenshots of every screen the film shows (phone: full-resolution PNG; web: 2× browser
captures). Save them in `projects/<job>/03-assets/app/`. Never invent a screen or feature the product doesn't have.

## 2. ui-tokens (do once, update when the product changes)
Scan each screenshot in zoomed tiles; sample exact pixels; write `film/ui-tokens.json`: canvas, card, border, radius,
glass/blur, chip and active states, the accent, type family + sizes + weights, secondary grey, status bar. Record the
scale: 1 app pt = N film px for each shot type. Brand-level colours go in `brand/tokens.json` too.

## 3. Starter components in ui.js (pure functions → HTML strings; sizes in px at 1920×1080)
| Component | Typical use | Animatable params |
|---|---|---|
| `promptBar({text, n, glow, placeholder})` | AI ask bar | typed chars n, glow 0..1, caret blink from F, send |
| `chip({icon, label, fill, press, active})`, `chipRow([...])` | filters, suggestions, features | fill, press, glow |
| `glass(inner, opts)` · `card(inner, opts)` · `bloom({...})` | surfaces, accent glows | phase |
| `segmented({labels, pos})` | Before/After, tabs | thumb position (spring / `indicator`) |
| `tabBar({active})` | app tab bar | active index, badge |
| `spinner(F)` · `shimmer({label, F})` | "AI is working" loaders | sweep phase |
| `stream(text, t)` · `checklist(items, t)` | AI answers | progress |
| `scoreRing({value, t})` | scores, progress | count-up |
| `feedPost({user, img, likes, likeT})` | social proof / community | like burst |
| `sheet(inner, {t})` · `tag({x, y, text, t})` | bottom sheets, AR labels | spring y, draw-on |
| `voiceWave({F})` | voice input | level |
| `phone(inner, {w, h})` · `cornerPin(inner, quad, w, h)` | device frame, device-on-surface | tilt, glare |
| `icon(name)` · `txt(s, opts)` · `caret(F)` · `abs(x,y,w,h)` | helpers | — |
Add product-specific components (e.g. `invoiceCard`, `mapPin`, `chatThread`) in the same style.

## 4. Fidelity check
For every component render a still beside its source screenshot (`render.py stills` + a PIL side-by-side) until it is
recognisable at first glance. Polish is allowed (alignment, nicer demo content); new design language is not. Content
= believable demo data — never real customers' data; avatars = initials.
