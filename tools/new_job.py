"""Scaffold a new job: projects/<date>-<slug>/ with every phase folder, the brief and the gate tracker.
  python tools/new_job.py <slug> [--kind film|social] [--ref <path-or-url>]
"""
import argparse, re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

FILM_DIRS = ["01-reference", "02-research/mood", "03-assets/app", "03-assets/specs", "03-assets/music", "04-storyboard",
             "06-qa", "07-deliver"]
SOCIAL_DIRS = ["01-research", "02-plan", "03-assets/specs", "04-posts", "07-deliver"]

BRIEF = """# Brief - {name}

Reference: {ref}
Owner's notes (feel, animation, what to copy / change - verbatim):
>

| Slot | Value | Source (stated / inferred / default) |
|---|---|---|
| TOPIC (what the film is about) | | |
| AUDIENCE | | |
| TAKEAWAY (the ONE idea the viewer keeps) | | |
| SECONDS (30-120 for films, 6-45 for social) | | |
| SHAPE (16:9 / 9:16 / 4:5 / 1:1) | | |
| NARRATION (voice-over / text and music only) | | |
| Features shown (each = input -> AI magic -> output) | | |
| Channels | | |
| Music (licensed source) | | |
| CTA + URL | | |
| Deadline | | |
"""

FILM_STATUS = """# Status - {name}

| # | Gate | Artefact | Approved |
|---|---|---|---|
| 1 | Brief | 00-brief.md | [ ] |
| 2 | Script (state list on the beat grid + VO words) | 04-storyboard/SPEC.md | [ ] |
| 3 | Look + style frames | film/design/LOOK.md + film/out/stills | [ ] |
| 4 | Transitions (one panel per cut, named carrier) | 04-storyboard/TRANSITIONS.md | [ ] |
| 5 | Animatic (timed draft + temp audio) | film/out/draft/draft.mp4 | [ ] |
| 6 | Build + checks + critique (internal) | 06-qa/ | - |
| 7 | Final (MP4s + frame sheet + post copy) | 07-deliver/ | [ ] |

Approved work is frozen.

## Notes log (every owner note: error or taste, exactly what changed)
"""

SOCIAL_STATUS = """# Status - {name}

| # | Gate | Artefact | Approved |
|---|---|---|---|
| 1 | Brief | 00-brief.md | [ ] |
| 2 | Plan (pillars, calendar, post list) | 02-plan/PLAN.md | [ ] |
| 3 | Drafts (copy + visuals per post) | 04-posts/ | [ ] |
| 4 | Final (files + POST_COPY.md per channel) | 07-deliver/ | [ ] |

## Notes log
"""


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("slug"); ap.add_argument("--kind", default="film", choices=["film", "social"])
    ap.add_argument("--ref", default="")
    a = ap.parse_args()
    name = f"{date.today():%Y-%m-%d}-{re.sub('[^a-z0-9-]', '-', a.slug.lower())}"
    job = ROOT / "projects" / name
    if job.exists():
        raise SystemExit(f"job already exists: {job}")
    for d in FILM_DIRS if a.kind == "film" else SOCIAL_DIRS:
        (job / d).mkdir(parents=True, exist_ok=True)
    (job / "00-brief.md").write_text(BRIEF.format(name=name, ref=a.ref or "(none - from brief)"), encoding="utf-8")
    (job / "STATUS.md").write_text((FILM_STATUS if a.kind == "film" else SOCIAL_STATUS).format(name=name), encoding="utf-8")
    print("created", job)


if __name__ == "__main__":
    main()
