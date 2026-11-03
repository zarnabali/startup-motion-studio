"""Create a film workspace from the engine template — from a brief, or from a reference video to remake.
  python tools/film-engine/new_film.py <film_dir> --seconds 30 [--fps 30] [--size 1920x1080] [--groups 4]
  python tools/film-engine/new_film.py <film_dir> --ref <reference.mp4> [--groups 4]
-> <film_dir>/ engine files, assets/fonts (from brand/fonts), film.json (fps, frames, size, groups, brand tokens + fonts),
   shots/G1..Gn.js placeholders (contiguous frame ranges, one agent per group).
   With --ref also: ref/reference.mp4, ref/full/fNNNN.jpg (every frame, 0-based), ref/audio.wav, film.json cuts + beats,
   ref/sheet/*.jpg (every 6th frame, CUT labels); groups split at hard cuts.
Sizes: 1920x1080 (16:9) · 1080x1920 (9:16) · 1080x1350 (4:5) · 1080x1080 (1:1).
"""
import json, re, shutil, subprocess, sys
from fractions import Fraction
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw

FF = imageio_ffmpeg.get_ffmpeg_exe()
ENGINE = Path(__file__).resolve().parent
ROOT = ENGINE.parent.parent  # the studio root (brand/, tools/, projects/)
FONT_EXT = {".woff2", ".woff", ".otf", ".ttf"}


def arg(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def analyse_ref(ref, dst):
    """Every frame + audio + hard cuts + beats + contact sheets of the reference."""
    (dst / "ref/full").mkdir(parents=True, exist_ok=True); (dst / "ref/sheet").mkdir(exist_ok=True)
    r = dst / "ref/reference.mp4"
    if not r.exists():
        shutil.copy(ref, r)
    probe = subprocess.run([FF, "-hide_banner", "-i", str(r)], capture_output=True, text=True).stderr
    m = re.search(r"(\d+(?:\.\d+)?) fps", probe); fps_s = m.group(1) if m else "30"
    rate = "30000/1001" if abs(float(fps_s) - 29.97) < 0.01 else ("24000/1001" if abs(float(fps_s) - 23.976) < 0.01 else fps_s)
    full = dst / "ref/full"
    if not any(full.iterdir()):
        subprocess.run([FF, "-v", "error", "-i", str(r), "-start_number", "0", "-q:v", "3", str(full / "f%04d.jpg")], check=True)
        subprocess.run([FF, "-v", "error", "-y", "-i", str(r), "-vn", "-ac", "2", "-ar", "48000", str(dst / "ref/audio.wav")], check=True)
    frames = sorted(full.glob("f*.jpg")); n = len(frames); fps = float(Fraction(rate))
    small = [np.asarray(Image.open(f).convert("L").resize((192, 108)), dtype=np.float32) for f in frames]
    d = np.array([0.0] + [np.abs(small[i] - small[i - 1]).mean() for i in range(1, n)])
    cuts = []
    for i in range(1, n):
        lo, hi = max(1, i - 6), min(n, i + 7)
        loc = np.median(np.concatenate([d[lo:i], d[i + 1:hi]])) if hi - lo > 1 else 0
        if d[i] > 6 and d[i] > 3.5 * (loc + 0.5):
            cuts.append(i)
    w, h = Image.open(frames[0]).size
    beats, bpm = [], None
    try:
        import librosa
        y, sr = librosa.load(str(dst / "ref/audio.wav"), sr=22050, mono=True)
        tempo, bt = librosa.beat.beat_track(y=y, sr=sr)
        bpm = round(float(np.atleast_1d(tempo)[0]), 2); beats = [round(float(x), 3) for x in librosa.frames_to_time(bt, sr=sr)]
    except Exception as e:
        print("beat analysis skipped:", e)
    thumbs = [(i, Image.open(frames[i]).resize((256, 144))) for i in range(0, n, 6)]
    cols = 10
    for page in range(0, len(thumbs), 80):
        chunk = thumbs[page:page + 80]; rows = (len(chunk) + cols - 1) // cols
        s = Image.new("RGB", (cols * 256, rows * 160), "white"); dr = ImageDraw.Draw(s)
        for k, (i, im) in enumerate(chunk):
            x, y0 = (k % cols) * 256, (k // cols) * 160
            s.paste(im, (x, y0)); near = any(abs(i - c) < 6 for c in cuts)
            dr.text((x + 4, y0 + 146), f"f{i} {i / fps:.2f}s" + (" CUT" if near else ""), fill="red")
        s.save(dst / f"ref/sheet/sheet_{page // 80}.jpg", quality=80)
    return dict(fps=fps, rate=rate, w=w, h=h, frames=n, cuts=cuts, bpm=bpm, beats=beats)


def main():
    if len(sys.argv) < 2 or sys.argv[1].startswith("--"):
        sys.exit(__doc__)
    dst = Path(sys.argv[1]).resolve(); ref = arg("--ref"); groups = int(arg("--groups", 4))
    dst.mkdir(parents=True, exist_ok=True)
    for f in ["core.js", "index.html", "render.py", "ui.js", "sfx.py", "vo.py"]:
        if not (dst / f).exists():
            shutil.copy(ENGINE / f, dst / f)
    for d in ["assets/fonts", "assets/brand", "assets/img", "shots", "out"]:
        (dst / d).mkdir(parents=True, exist_ok=True)

    # brand: tokens + fonts + logo files
    brand = ROOT / "brand"
    tok = json.loads((brand / "tokens.json").read_text(encoding="utf-8")) if (brand / "tokens.json").exists() else {}
    fonts = tok.pop("fonts", [])
    for f in (brand / "fonts").glob("*") if (brand / "fonts").exists() else []:
        if f.suffix.lower() in FONT_EXT:
            shutil.copy(f, dst / "assets/fonts" / f.name)
    for f in (brand / "logo").glob("*") if (brand / "logo").exists() else []:
        if f.suffix.lower() in {".svg", ".png"}:
            shutil.copy(f, dst / "assets/brand" / f.name)
    tok = {k: v for k, v in tok.items() if not k.startswith("_")}

    if ref:
        cfg = analyse_ref(Path(ref).resolve(), dst)
    else:
        fps_s = arg("--fps", "30"); rate = "30000/1001" if fps_s in ("29.97", "30000/1001") else fps_s
        fps = float(Fraction(rate)); w, h = map(int, arg("--size", "1920x1080").lower().split("x"))
        n = int(round(float(arg("--seconds", 30)) * fps))
        cfg = dict(fps=fps, rate=rate, w=w, h=h, frames=n, cuts=[], bpm=None, beats=[])
    n, cuts = cfg["frames"], cfg["cuts"]
    bounds = [0]
    for g in range(1, groups):
        target = n * g / groups
        bounds.append(min(cuts, key=lambda c: abs(c - target)) if cuts else int(target))
    bounds = sorted(set(bounds)) + [n]
    gmap = {f"G{i + 1}": [bounds[i], bounds[i + 1]] for i in range(len(bounds) - 1)}
    cfg.update(groups=gmap, fast=[], preload=[], scripts=[], tokens=tok, fonts=fonts, paletteFilter=False)
    if not (dst / "film.json").exists():
        (dst / "film.json").write_text(json.dumps(cfg, indent=1), encoding="utf-8")
    for g, (a, b) in gmap.items():
        p = dst / f"shots/{g}.js"
        if not p.exists():
            p.write_text(f"""(function () {{
  const C = CORE, T = C.T;
  // {g}: frames {a}-{b}. One SHOT per shot in SPEC.md. Pure function of F (no timers, no Math.random).
  SHOT({{ id: '{g}_placeholder', f0: {a}, f1: {b}, render: (lf, F) =>
    `<div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font:500 48px ${{T.font}};color:#bbb;background:#fafafa">{g} · F${{F}}</div>` }});
}})();
""", encoding="utf-8")
    print(json.dumps({"dir": str(dst), "frames": n, "fps": cfg["rate"], "size": [cfg["w"], cfg["h"]], "cuts": len(cuts),
                      "bpm": cfg["bpm"], "groups": gmap}))


if __name__ == "__main__":
    main()
