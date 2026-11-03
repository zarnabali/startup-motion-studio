"""Shrink a HyperFrames project's images before rendering (big PNG photos crash/slow the renderer).

    python tools/optimize_assets.py <project_dir> [--max 2160] [--quality 90]

- Opaque PNG/WebP photos  -> JPEG (same stem, .jpg), long edge <= --max, references rewritten in .html/.css/.js/.json.
- Images with real transparency stay PNG, downscaled to <= --max and optimized.
- Originals are kept in <project_dir>/.orig-assets/ (delete after a good render).
"""
import argparse
import re
import shutil
from pathlib import Path

from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument("project")
ap.add_argument("--max", type=int, default=2160)
ap.add_argument("--quality", type=int, default=90)
a = ap.parse_args()
root = Path(a.project)
backup = root / ".orig-assets"
renames: dict[str, str] = {}
before = after = 0

for p in sorted(root.rglob("*")):
    if p.suffix.lower() not in {".png", ".webp", ".jpg", ".jpeg"} or not p.is_file():
        continue
    if any(part in {".orig-assets", "node_modules", "renders", ".hf-tmp"} for part in p.parts):
        continue
    before += p.stat().st_size
    im = Image.open(p)
    im.load()
    has_alpha = im.mode in ("RGBA", "LA", "PA") and im.getchannel("A").getextrema()[0] < 250
    scale = a.max / max(im.size)
    if scale < 1:
        im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
    rel = p.relative_to(root)
    (backup / rel).parent.mkdir(parents=True, exist_ok=True)
    if not (backup / rel).exists():
        shutil.copy2(p, backup / rel)
    if has_alpha:
        im.save(p, optimize=True)
        after += p.stat().st_size
    else:
        out = p.with_suffix(".jpg")
        im.convert("RGB").save(out, "JPEG", quality=a.quality, optimize=True, progressive=True)
        after += out.stat().st_size
        if out != p:
            p.unlink()
            renames[p.name] = out.name

text_files = [f for f in root.rglob("*") if f.suffix.lower() in {".html", ".css", ".js", ".json", ".md"}
              and f.is_file() and not any(x in {".orig-assets", "node_modules", "renders"} for x in f.parts)]
changed = 0
if renames:
    pat = re.compile("|".join(re.escape(k) for k in sorted(renames, key=len, reverse=True)))
    for f in text_files:
        s = f.read_text(encoding="utf-8", errors="ignore")
        n = pat.sub(lambda m: renames[m.group(0)], s)
        if n != s:
            f.write_text(n, encoding="utf-8")
            changed += 1
print(f"images {before/1e6:.1f} MB -> {after/1e6:.1f} MB; {len(renames)} converted to JPEG; {changed} text files updated")
