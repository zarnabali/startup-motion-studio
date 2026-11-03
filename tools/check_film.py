"""Automated pre-gate checks for a rendered film (studio prompt <checks> + course step 11).
  python tools/check_film.py FILM.mp4 [--film projects/<job>/film] [--out DIR] [--hold 2.0]
Writes DIR/CHECKS.md (pass / FAIL / manual per check) + the review sheets the critic and Claude must LOOK at:
  frame_sheet.jpg (1 fps), phone_sheet.jpg (360 px wide, 1 fps = how it reads on a phone), contact.jpg (2 fps).
Automated: format · duration · loudness/true peak · black frames · white flashes · frozen runs.
Manual (critic): spelling-and-facts · text-safe-area 5 % · no-collisions · text contrast 4.5:1 · VO/beat sync <= 2 f.
"""
import json, re, subprocess, sys
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from PIL import Image

FF = imageio_ffmpeg.get_ffmpeg_exe()


def opt(k, d=None):
    return sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d


def probe(path):
    err = subprocess.run([FF, "-hide_banner", "-i", str(path)], capture_output=True, text=True).stderr
    v = re.search(r"Video: (\w+).*?, (\d{3,5})x(\d{3,5}).*?, ([\d.]+) fps", err)
    a = re.search(r"Audio: (\w+)", err)
    d = re.search(r"Duration: (\d+):(\d+):([\d.]+)", err)
    dur = int(d[1]) * 3600 + int(d[2]) * 60 + float(d[3]) if d else 0
    return {"vcodec": v[1] if v else None, "w": int(v[2]) if v else 0, "h": int(v[3]) if v else 0,
            "fps": float(v[4]) if v else 0, "acodec": a[1] if a else None, "dur": dur}


def loudness(path):
    err = subprocess.run([FF, "-hide_banner", "-i", str(path), "-af", "loudnorm=print_format=json", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    js = json.loads(err[err.rfind("{"): err.rfind("}") + 1])
    return float(js["input_i"]), float(js["input_tp"])


def frames(path, w=192, h=108, fps=None):
    vf = (f"fps={fps}," if fps else "") + f"scale={w}:{h},format=rgb24"
    raw = subprocess.run([FF, "-v", "quiet", "-i", str(path), "-vf", vf, "-f", "rawvideo", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)


def sheet(path, out, fps, w, cols):
    h = int(round(w * 9 / 16 / 2) * 2)
    f = frames(path, w, h, fps)
    rows = -(-len(f) // cols); s = Image.new("RGB", (cols * w, rows * h), "white")
    for i, im in enumerate(f):
        s.paste(Image.fromarray(im), ((i % cols) * w, (i // cols) * h))
    s.save(out, quality=82)


def main():
    film = Path(sys.argv[1]); out = Path(opt("--out", film.parent / "checks")); out.mkdir(parents=True, exist_ok=True)
    cfg = {}
    if opt("--film"):
        cfg = json.loads((Path(opt("--film")) / "film.json").read_text(encoding="utf-8-sig"))
    hold = float(opt("--hold", 2.0))
    res = []
    p = probe(film)
    ok = p["h"] >= 1080 and p["vcodec"] == "h264" and p["acodec"] == "aac"
    res.append(("format", ok, f"{p['w']}x{p['h']} {p['vcodec']}+{p['acodec']} {p['fps']} fps"))
    if cfg:
        exp = cfg["frames"] / cfg["fps"]
        res.append(("duration", abs(p["dur"] - exp) <= .05 * exp, f"{p['dur']:.2f} s vs film.json {exp:.2f} s"))
    if p["acodec"]:
        i, tp = loudness(film)
        res.append(("loudness", abs(i + 14) <= 1 and tp <= -1, f"{i:.1f} LUFS (target -14 +-1), true peak {tp:.1f} dBTP (<= -1)"))
    f = frames(film).astype(np.float32); luma = f.mean(axis=(1, 2, 3)); fps = p["fps"] or 30
    cuts = set(cfg.get("cuts", []))
    std = f.std(axis=(1, 2, 3)); black = [i for i, (l, sd) in enumerate(zip(luma, std)) if l < 6 and sd < 2.5]   # blank, not dark design
    res.append(("no-black-frames", not black, f"{len(black)} near-black frames {black[:12]}"))
    flash = [i for i in range(1, len(luma) - 1) if luma[i] - max(luma[i - 1], luma[i + 1]) > 60]
    res.append(("no-white-flashes", not flash, f"one-frame brightness spikes at {flash[:12]}"))
    diff = np.abs(np.diff(f, axis=0)).mean(axis=(1, 2, 3)); runs, s0 = [], None
    for i, d in enumerate(np.append(diff, 99)):
        if d < .08 and s0 is None: s0 = i
        if d >= .08 and s0 is not None:
            if (i - s0) / fps > 1.0 and i < len(diff) - hold * fps: runs.append((s0, i))
            s0 = None
    res.append(("no-frozen-runs > 1 s", not runs, f"frozen frame ranges {runs[:8]}"))
    sheet(film, out / "frame_sheet.jpg", 1, 384, 6)
    sheet(film, out / "phone_sheet.jpg", 1, 360, 6)
    sheet(film, out / "contact.jpg", 2, 270, 8)
    lines = ["# CHECKS · " + film.name, "", "| check | result | detail |", "|---|---|---|"]
    lines += [f"| {n} | {'pass' if okk else 'FAIL'} | {d} |" for n, okk, d in res]
    lines += ["| spelling-and-facts | manual | every word, name and number matches the brief or a source |",
              "| text-safe-area | manual | every text box 5 % inside each edge (phone_sheet.jpg) |",
              "| no-collisions | manual | nothing overlaps or clips by accident |",
              "| text-contrast | manual | 4.5:1 at its worst frame |",
              "| sync | manual | each key VO word lands with its visual within 2 frames |",
              "", "Look at: frame_sheet.jpg · phone_sheet.jpg (360 px = phone) · contact.jpg"]
    (out / "CHECKS.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines[4:4 + len(res)])); print("->", out / "CHECKS.md")


if __name__ == "__main__":
    main()
