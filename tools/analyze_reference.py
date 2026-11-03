"""Deconstruct a reference video into measurable, reviewable evidence.

Usage:
    python tools/analyze_reference.py <url-or-file> <out_dir> [--sample 0.5] [--threshold 27]

Produces in <out_dir>:
    source.mp4            the downloaded / copied video
    meta.json             title, uploader, url, duration, fps, resolution, aspect
    scenes.json           every shot: index, start, end, duration, keyframes, motion, palette
    frames/               3 keyframes per shot (in / mid / out) — read these frame by frame
    sheets/               timestamped contact sheets (uniform sampling) for pacing review
    audio.wav             mono 22.05 kHz track (if the video has audio)
    rhythm.json           bpm, beat times, cut-to-beat alignment, shot-length stats
    analysis.json         everything above merged — the input to 01-analysis.md
"""
from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path

import cv2
import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
VENV_BIN = Path(sys.executable).parent


def log(msg: str) -> None:
    print(f"[analyze] {msg}", flush=True)


def fetch(src: str, out: Path) -> dict:
    target = out / "source.mp4"
    if Path(src).exists():
        shutil.copy(src, target)
        return {"url": None, "title": Path(src).stem, "uploader": None}
    ytdlp = VENV_BIN / ("yt-dlp.exe" if sys.platform == "win32" else "yt-dlp")
    info_path = out / "ytdlp-info.json"
    cmd = [
        str(ytdlp), src,
        "-f", "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/bv*+ba/b",
        "--merge-output-format", "mp4",
        "--ffmpeg-location", FFMPEG,
        "-o", str(target), "--no-playlist", "--write-info-json",
        "--force-overwrites",
    ]
    log("downloading with yt-dlp …")
    subprocess.run(cmd, check=True)
    meta = {"url": src, "title": None, "uploader": None}
    for p in out.glob("*.info.json"):
        info = json.loads(p.read_text(encoding="utf-8"))
        meta.update(title=info.get("title"), uploader=info.get("uploader"),
                    description=(info.get("description") or "")[:2000],
                    platform=info.get("extractor_key"), upload_date=info.get("upload_date"),
                    view_count=info.get("view_count"), like_count=info.get("like_count"))
        p.rename(info_path)
    return meta


def probe(path: Path) -> dict:
    cap = cv2.VideoCapture(str(path))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    w, h = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    g = math.gcd(w, h) or 1
    return {"fps": round(fps, 3), "frames": n, "width": w, "height": h,
            "duration": round(n / fps, 3), "aspect": f"{w // g}:{h // g}"}


def detect_scenes(path: Path, threshold: float) -> list[tuple[float, float]]:
    from scenedetect import ContentDetector, AdaptiveDetector, SceneManager, open_video

    video = open_video(str(path))
    sm = SceneManager()
    sm.add_detector(ContentDetector(threshold=threshold, min_scene_len=6))
    sm.add_detector(AdaptiveDetector(min_scene_len=6))
    sm.detect_scenes(video, show_progress=False)
    secs = lambda tc: tc.seconds if isinstance(getattr(type(tc), "seconds", None), property) else tc.get_seconds()
    scenes = [(secs(s), secs(e)) for s, e in sm.get_scene_list()]
    if not scenes:
        scenes = [(0.0, video.duration.get_seconds())]
    return scenes


def grab(cap: cv2.VideoCapture, t: float, fps: float):
    cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, int(round(t * fps))))
    ok, frame = cap.read()
    return frame if ok else None


def palette(frame, k: int = 5) -> list[dict]:
    small = cv2.resize(frame, (96, 96), interpolation=cv2.INTER_AREA).reshape(-1, 3).astype(np.float32)
    crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
    _, labels, centers = cv2.kmeans(small, k, None, crit, 3, cv2.KMEANS_PP_CENTERS)
    counts = np.bincount(labels.flatten(), minlength=k)
    out = []
    for i in np.argsort(-counts):
        b, g, r = (int(x) for x in centers[i])
        out.append({"hex": f"#{r:02x}{g:02x}{b:02x}", "share": round(float(counts[i] / counts.sum()), 3)})
    return out


def motion_score(cap, start: float, end: float, fps: float) -> dict:
    """Mean optical-flow magnitude + dominant direction → static / pan / zoom / handheld hint."""
    ts = np.linspace(start + 0.05, max(start + 0.1, end - 0.05), num=6)
    prev, mags, dxs, dys, divs = None, [], [], [], []
    for t in ts:
        f = grab(cap, float(t), fps)
        if f is None:
            continue
        g = cv2.cvtColor(cv2.resize(f, (320, int(320 * f.shape[0] / f.shape[1]))), cv2.COLOR_BGR2GRAY)
        if prev is not None:
            flow = cv2.calcOpticalFlowFarneback(prev, g, None, 0.5, 3, 15, 3, 5, 1.2, 0)
            mags.append(float(np.linalg.norm(flow, axis=2).mean()))
            dxs.append(float(flow[..., 0].mean()))
            dys.append(float(flow[..., 1].mean()))
            h, w = g.shape
            xs, ys = np.meshgrid(np.arange(w) - w / 2, np.arange(h) - h / 2)
            divs.append(float(((flow[..., 0] * xs + flow[..., 1] * ys) / (np.hypot(xs, ys) + 1e-6)).mean()))
        prev = g
    if not mags:
        return {"magnitude": 0.0, "hint": "unknown"}
    m, dx, dy, dv = np.mean(mags), np.mean(dxs), np.mean(dys), np.mean(divs)
    if m < 0.4:
        hint = "static / locked-off"
    elif abs(dv) > 0.6 * m:
        hint = "push-in / zoom" if dv > 0 else "pull-out"
    elif abs(dx) > 0.5 * m:
        hint = "horizontal pan / slide"
    elif abs(dy) > 0.5 * m:
        hint = "vertical scroll / tilt"
    else:
        hint = "handheld / subject motion"
    return {"magnitude": round(float(m), 2), "dx": round(float(dx), 2), "dy": round(float(dy), 2), "hint": hint}


def contact_sheets(cap, duration: float, fps: float, step: float, out: Path) -> list[str]:
    cols, rows, tw = 4, 4, 360
    times = np.arange(0, duration, step)
    sheets = []
    try:
        font = ImageFont.truetype("arial.ttf", 22)
    except OSError:
        font = ImageFont.load_default()
    per = cols * rows
    for si in range(0, len(times), per):
        tiles = []
        for t in times[si:si + per]:
            f = grab(cap, float(t), fps)
            if f is None:
                continue
            im = Image.fromarray(cv2.cvtColor(f, cv2.COLOR_BGR2RGB))
            im = im.resize((tw, int(tw * im.height / im.width)))
            d = ImageDraw.Draw(im)
            d.rectangle([0, 0, 92, 30], fill=(0, 0, 0))
            d.text((6, 4), f"{t:05.2f}s", fill=(255, 255, 255), font=font)
            tiles.append(im)
        if not tiles:
            continue
        th = tiles[0].height
        sheet = Image.new("RGB", (cols * tw, rows * th), (20, 20, 20))
        for i, im in enumerate(tiles):
            sheet.paste(im, ((i % cols) * tw, (i // cols) * th))
        p = out / f"sheet_{si // per + 1:02d}.jpg"
        sheet.save(p, quality=85)
        sheets.append(str(p.name))
    return sheets


def rhythm(video: Path, out: Path, cuts: list[float]) -> dict:
    wav = out / "audio.wav"
    r = subprocess.run([FFMPEG, "-y", "-i", str(video), "-vn", "-ac", "1", "-ar", "22050", str(wav)],
                       capture_output=True)
    if r.returncode != 0 or not wav.exists() or wav.stat().st_size < 10_000:
        return {"has_audio": False}
    import librosa

    y, sr = librosa.load(str(wav), sr=22050)
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    beat_t = librosa.frames_to_time(beats, sr=sr).tolist()
    onsets = librosa.onset.onset_detect(y=y, sr=sr, units="time").tolist()
    rms = librosa.feature.rms(y=y)[0]
    loud_t = librosa.frames_to_time(np.argsort(-rms)[:5], sr=sr).tolist()

    def near(t, arr, tol=0.09):
        return any(abs(t - b) <= tol for b in arr)

    inner = [c for c in cuts if c > 0.05]
    on_beat = sum(near(c, beat_t) for c in inner)
    on_onset = sum(near(c, onsets) for c in inner)
    return {
        "has_audio": True,
        "bpm": round(float(np.atleast_1d(tempo)[0]), 1),
        "beat_times": [round(b, 3) for b in beat_t],
        "cuts_on_beat_pct": round(100 * on_beat / max(1, len(inner)), 1),
        "cuts_on_onset_pct": round(100 * on_onset / max(1, len(inner)), 1),
        "loudest_moments_s": sorted(round(t, 2) for t in loud_t),
        "note": "cuts_on_beat_pct > 60 means the edit is beat-synced; replicate that.",
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--sample", type=float, default=0.5, help="contact-sheet sampling step (s)")
    ap.add_argument("--threshold", type=float, default=27.0, help="ContentDetector threshold")
    a = ap.parse_args()

    out = Path(a.out)
    (out / "frames").mkdir(parents=True, exist_ok=True)
    (out / "sheets").mkdir(exist_ok=True)

    meta = fetch(a.src, out)
    video = out / "source.mp4"
    meta.update(probe(video))
    log(f"{meta['width']}x{meta['height']} @ {meta['fps']} fps, {meta['duration']} s ({meta['aspect']})")

    scenes = detect_scenes(video, a.threshold)
    log(f"{len(scenes)} shots detected")
    cap = cv2.VideoCapture(str(video))
    fps = meta["fps"]
    shots = []
    for i, (s, e) in enumerate(scenes, 1):
        frames = {}
        for tag, t in (("in", s + 0.04), ("mid", (s + e) / 2), ("out", max(s, e - 0.06))):
            f = grab(cap, t, fps)
            if f is None:
                continue
            p = out / "frames" / f"shot_{i:03d}_{tag}_{t:06.2f}s.jpg"
            cv2.imwrite(str(p), f, [cv2.IMWRITE_JPEG_QUALITY, 88])
            frames[tag] = p.name
            if tag == "mid":
                pal = palette(f)
        shots.append({"shot": i, "start": round(s, 3), "end": round(e, 3), "duration": round(e - s, 3),
                      "frames": frames, "palette": pal, "motion": motion_score(cap, s, e, fps)})
    sheets = contact_sheets(cap, meta["duration"], fps, a.sample, out / "sheets")
    cap.release()

    durs = [s["duration"] for s in shots]
    pacing = {"shots": len(shots), "avg_shot_s": round(float(np.mean(durs)), 2),
              "median_shot_s": round(float(np.median(durs)), 2), "shortest_s": round(min(durs), 2),
              "longest_s": round(max(durs), 2), "cuts_per_10s": round(10 * len(shots) / meta["duration"], 2),
              "first_cut_s": shots[1]["start"] if len(shots) > 1 else None}
    rh = rhythm(video, out, [s["start"] for s in shots])

    (out / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    (out / "scenes.json").write_text(json.dumps(shots, indent=2), encoding="utf-8")
    (out / "rhythm.json").write_text(json.dumps({**rh, "pacing": pacing}, indent=2), encoding="utf-8")
    (out / "analysis.json").write_text(json.dumps(
        {"meta": meta, "pacing": pacing, "rhythm": rh, "shots": shots, "sheets": sheets}, indent=2), encoding="utf-8")
    log(f"done → {out / 'analysis.json'}  ({len(sheets)} contact sheets, {len(shots) * 3} keyframes)")
    log("NEXT: read every sheet + every shot keyframe, then write 01-analysis.md")


if __name__ == "__main__":
    main()
