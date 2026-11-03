---
name: social-content
description: >
  Marketing content for a startup's socials, made in the studio's style: a content plan and calendar, short motion
  reels (6–30 s) built with the same seek(t) film engine, carousels and static posts rendered from code, cut-downs of
  a finished film, and platform-native captions, hooks and hashtags (LinkedIn, Instagram, TikTok, X, YouTube Shorts).
  Use when the user asks for social posts, a content calendar, a reel, a carousel, captions, hashtags, "what should
  I post", cut-downs of a film, or invokes /social-content. Never publishes — the user posts.
---

# /social-content — plan → drafts → final, in the brand's voice

Load first: `brand/BRAND_BRAIN.md` (facts, voice, CTA), `brand/tokens.json`, `brand/LEARNINGS.md`,
`references/platforms.md`. If BRAND_BRAIN is still the template, run `studio-onboard` first.
Same non-negotiables as `motion-film`: real product only, every feature = input → AI magic → output, no invented
claims, photos must not look AI, banned motion defaults, never publish or log in to anyone's accounts.

## Gates
| # | Gate | Output | |
|---|---|---|---|
| 0 | `PY tools/new_job.py <slug> --kind social` | `projects/<job>/` | |
| 1 | **Brief**: goal (awareness / waitlist / downloads / hiring), channels, period, cadence the user can sustain, what's already made (films, screenshots) | `00-brief.md` | **[me]** |
| 2 | **Plan**: 3–5 content pillars, a calendar (date · channel · format · pillar · hook · CTA), reuse map (one film → many posts) | `02-plan/PLAN.md` | **[me]** |
| 3 | **Drafts**: per post: hook, visual (rendered), caption per channel, hashtags, alt text, posting note | `04-posts/<date>-<id>/` | **[me]** |
| 4 | **Final**: files at each platform's spec + `POST_COPY.md` per channel, checks passed | `07-deliver/` | **[me]** |

## Content pillars (pick 3–5 that fit BRAND_BRAIN)
Product in action (one feature, input → output, 6–15 s) · the problem (the annoying "before") · behind the build
(founder notes, decisions) · user stories (only real, permissioned) · tips the audience can use without the product ·
launches and milestones (sourced numbers only) · community / culture.

## Formats and how to make them
| Format | Spec | How |
|---|---|---|
| Motion reel | 9:16 1080×1920, 6–30 s, hook ≤ 1.5 s, captions burned in | A small film: `new_film.py projects/<job>/04-posts/<id>/film --seconds 15 --size 1080x1920 --groups 1`, then the motion-film method at medium effort (state list → stills → draft → full → check_film). Keep top ~250 px and bottom ~330 px free of text. |
| Cut-down of a film | 6 / 15 / 30 s per channel | Re-lay out shots from the master's timeline at the new size (copy the film folder, change w/h); never crop the 16:9 master. |
| Carousel | 4:5 1080×1350, 5–10 slides | A film whose shots are slides (1 frame each, or 1 s each): `new_film.py … --seconds 10 --fps 1 --size 1080x1350 --groups 1`, then `render.py stills out/slides 0 1 2 …`. Slide 1 = the hook; last = CTA. One idea per slide, ≤ 25 words. |
| Static post | 1:1 or 4:5 | One-frame film, `render.py stills`. Real UI or a real-looking photo + one line. |
| Text post (LinkedIn/X) | — | Hook line ≤ 12 words, short paragraphs, one CTA, 3–5 hashtags at the end. |

## Copy rules (`references/captions.md` has the patterns)
- The hook is the first line / first 1.5 s: a specific situation, a sharp question or a surprising result — never
  "Introducing…". Then value, then ONE CTA from BRAND_BRAIN §6.
- Platform-native: LinkedIn = plain, useful, first-person; Instagram/TikTok = casual, short lines, emojis sparingly
  if the brand voice allows; X = one punchy line. Match the brand's 3 voice words.
- Hashtags: 3–5 relevant (LinkedIn/X), 5–10 (Instagram), 3–5 + trending in-app (TikTok). Mix broad + niche + brand.
- Every claim is in BRAND_BRAIN §5 with a source. Demo data is labelled. Alt text on every image.
- Music for reels: licensed tracks in the file, or "add trending sound in-app" noted in POST_COPY.md.

## Checks before the final gate
For every reel / cut-down: `PY tools/check_film.py <mp4> --film <film dir>` (all pass; look at the phone sheet).
For every post: spelling-and-facts · safe areas per platform · text readable at phone size · contrast 4.5:1 · one CTA
· caption length within the platform limit · hashtags count · alt text present · nothing cropped by the platform's
grid preview (Instagram 3:4 centre). Owner notes follow the motion-film notes protocol (error vs taste → new checks).

## Deliver
`07-deliver/<channel>/` with files named `<date>_<channel>_<id>.<ext>` + `POST_COPY.md` (caption, hashtags, alt text,
best posting time from the plan, sound note). The user posts; offer a reminder list, never post for them.
