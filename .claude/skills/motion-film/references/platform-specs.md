# Platform specs (consensus 2026; refresh in Phase 2 if older than 3 months — last checked 2026-10-02)

| Channel | Aspect / px | Length sweet spot | Notes |
|---|---|---|---|
| Instagram Reels | 9:16 · 1080×1920 | 15–30 s (hook ≤ 1.5 s) | keep top ~250 px, bottom ~330 px, right ~120 px clear; grid preview crops to 3:4 centre |
| Instagram feed | 4:5 · 1080×1350 | 15–30 s | most screen real estate in feed |
| TikTok | 9:16 · 1080×1920 | 15–34 s | add trending sound in-app, not in the file |
| LinkedIn feed | 4:5 or 1:1 (16:9 OK) | 30–60 s | MP4, 30 fps, 75 KB–200 MB, 3 s–30 min; most viewers are sound-off → burned-in captions |
| LinkedIn vertical | 9:16 | 20–45 s | |
| X | 16:9 or 1:1 | 20–45 s | |
| YouTube Shorts | 9:16 | ≤ 60 s | |
| App Store preview | device resolution | 15–30 s | real UI only, no hands/devices, no prices; verify current Apple guidelines |

Encoding: H.264 High, yuv420p, 30 fps (match reference if 24/60), AAC 48 kHz 192 kbps, −14 LUFS integrated.

Durations by video type: teaser 6–10 s · feature launch 20–30 s · hero/launch film 45–90 s.
Text: ≤ 3 words/second on screen; captions ≤ 2 lines × 32 chars.
