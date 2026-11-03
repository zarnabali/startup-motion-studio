"""Startup Motion Studio film renderer (adapted from claude-motion-design remake_render/render_template, MIT). Windows / macOS / Linux.
Run from a film folder (copy of tools/film-engine) with the project venv:
  python render.py stills  OUT F1 F2 ...        -> OUT/o_fNNNN.png
  python render.py compare OUT F1 F2 ...        -> ref | ours tiles + OUT/compare_sheet.jpg  (needs ref/full)
  python render.py beats   OUT                  -> one frame per beat (BEATS in film.json) + sheet
  python render.py draft   OUT [F0 F1]          -> 960x540 1 sample/frame -> OUT/draft.mp4 (judge rhythm)
  python render.py draft   OUT --jobs 2         -> same, split over 2 parallel Chromiums (~2x faster)
  python render.py full    OUT F0 F1 [--jobs N] [--pipe] -> 1920x1080 PNG frames (motion-blur subframes on film.json "fast"
                                                   ranges); --pipe encodes straight to OUT/seg_F0.mp4 (no PNGs, saves ~5 GB)
  python render.py concat  OUT [audio.wav]      -> joins the seg_*.mp4 -> OUT/film_silent.mp4 (+ OUT/film.mp4 with audio)
  python render.py encode  OUT [audio.wav]      -> OUT/film.mp4 (BT.709 TV range, crf 16, AAC 256k)
  python render.py split   OUT                  -> OUT/split_screen.mp4  "original | ours" (QA only)
  python render.py pops    VIDEO                -> frame-diff spikes > 3x neighbours
  python render.py qa      OUT [--from-draft]   -> ref|ours one frame per second sheets (--from-draft: reuse out/draft frames)
The page is served by a private local HTTP server started here (no manual server needed).
"""
import asyncio, functools, http.server, json, os, socketserver, subprocess, sys, threading, time
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from playwright.async_api import async_playwright

H = Path(__file__).resolve().parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
CFG = json.loads((H / "film.json").read_text(encoding="utf-8-sig"))
FPS = CFG["fps"]; W, HH = CFG["w"], CFG["h"]; N = CFG["frames"]
CUTS = set(CFG.get("cuts", []))          # never blur across these
FAST = CFG.get("fast", [])               # [[f0,f1,subframes], ...] slam moves that get motion blur
FONTFILE = next((p for p in ["C:/Windows/Fonts/arial.ttf", "/System/Library/Fonts/Supplemental/Arial.ttf",
                             "/Library/Fonts/Arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"] if Path(p).exists()), None)
try:
    FONT = ImageFont.truetype(FONTFILE, 30)
except Exception:
    FONT = ImageFont.load_default()
FF_FONT = (FONTFILE or "").replace(":", "\\:")   # ffmpeg drawtext path escaping
ENC = ["-vf", "scale=in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv420p", "-color_range", "tv",
       "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
       "-c:v", "libx264", "-crf", "16", "-preset", "slow", "-movflags", "+faststart"]
RATE = CFG.get("rate", "30000/1001")


class _Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a, **k):
        pass


class _Server(socketserver.ThreadingTCPServer):
    request_queue_size = 128   # Windows refuses connections when Chromium opens ~10 at once with the default 5
    daemon_threads = True
    allow_reuse_address = True


def serve():
    handler = functools.partial(_Quiet, directory=str(H))
    srv = _Server(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}/index.html"


def subcount(F):
    for a, b, n in FAST:
        if a <= F < b:
            return n
    return 1


async def capture(frames, out: Path, scale=1.0, sub=True, prefix="o_f", sink=None):
    out.mkdir(parents=True, exist_ok=True)
    srv, url = serve()
    paths = []
    async with async_playwright() as p:
        gpu = os.environ.get("RENDER_GPU") == "1"   # full Chromium + ANGLE/D3D11 raster: heavy CSS (blur, 3D) renders far faster
        b = await p.chromium.launch(channel="chromium" if gpu else None,
                                    args=["--font-render-hinting=none", "--force-color-profile=srgb",
                                          "--disable-gpu-vsync", "--run-all-compositor-stages-before-draw",
                                          "--disable-threaded-animation", "--disable-checker-imaging"]
                                    + (["--use-angle=d3d11", "--enable-gpu", "--ignore-gpu-blocklist", "--enable-gpu-rasterization"] if gpu else []))
        pg = await b.new_page(viewport={"width": W, "height": HH}, device_scale_factor=scale)
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: errs.append("console: " + m.text) if m.type == "error" else None)
        await pg.goto(url, timeout=180000)   # 2 browsers loading ~80 assets on low RAM can exceed 30 s
        await pg.wait_for_function("window.ready === true", timeout=180000)
        el = await pg.query_selector("#stage")

        async def shot(t):
            await pg.evaluate(f"window.seek({t + 1e-6})")
            # wait until every <img> of this frame is decoded: on low RAM Chromium evicts decoded bitmaps and the first
            # frames of a photo shot came out blank (critic: f581-583, f662-664, f803)
            await pg.evaluate("Promise.all([...document.querySelectorAll('#stage img')].map(i => (i.complete && i.naturalWidth)"
                              " ? i.decode().catch(() => {}) : new Promise(r => { i.addEventListener('load', r, {once: true});"
                              " i.addEventListener('error', r, {once: true}); setTimeout(r, 8000); })))")
            await pg.evaluate("new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))")
            # clip screenshot of the stage area (no element-stability wait: big 3D shots made el.screenshot time out)
            buf = await pg.screenshot(type="png", clip={"x": 0, "y": 0, "width": W, "height": HH}, timeout=180000)
            return np.asarray(Image.open(__import__("io").BytesIO(buf)).convert("RGB"), dtype=np.float32)

        for F in frames:
            n = subcount(F) if sub else 1
            if n <= 1:
                acc = await shot(F / FPS)
            else:  # 180 deg shutter: spread n samples over half a frame, never across a cut
                acc = None
                for k in range(n):
                    dt = (k / n - 0.25) * 0.5 / FPS
                    if (F in CUTS and dt < 0) or ((F + 1) in CUTS and dt > 0):
                        dt = 0
                    img = await shot(F / FPS + dt)
                    acc = img if acc is None else acc + img
                acc /= n
            frame = np.clip(acc, 0, 255).astype(np.uint8)
            if sink is not None:     # straight into an encoder (no PNGs on disk)
                sink(F, frame)
            else:
                pth = out / f"{prefix}{F:04d}.png"
                Image.fromarray(frame).save(pth)
                paths.append(pth)
        await b.close()
    srv.shutdown()
    if errs:
        print("PAGE ERRORS:", errs[:10])
    return paths


class SegSink:
    """x264 segments split at every cut (OUT/seg_FFFF.mp4): after a fix, re-render only the cut-to-cut ranges it touches,
    then `concat`. Segment names = first frame, so a re-render overwrites exactly the stale segment."""
    def __init__(self, out, starts):
        self.out, self.starts, self.p = out, set(starts), None

    def __call__(self, F, frame):
        if self.p is None or F in self.starts:
            self.close()
            self.p = subprocess.Popen([FF, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{HH}",
                                       "-framerate", RATE, "-i", "-", *ENC, str(self.out / f"seg_{F:04d}.mp4")], stdin=subprocess.PIPE)
        self.p.stdin.write(frame.tobytes())

    def close(self):
        if self.p:
            self.p.stdin.close(); self.p.wait(); self.p = None


def sheet(tiles, out_path, cols=2, tw=965, th=295):
    rows = -(-len(tiles) // cols)
    s = Image.new("RGB", (cols * tw, rows * th), "white")
    for i, t in enumerate(tiles):
        s.paste(t.resize((tw, th)), ((i % cols) * tw, (i // cols) * th))
    s.save(out_path, quality=82)


def compare(frames, out: Path):
    paths = asyncio.run(capture(frames, out, sub=False))
    tiles = []
    for F, p in zip(frames, paths):
        rp = H / f"ref/full/f{F:04d}.jpg"
        ref = Image.open(rp).convert("RGB").resize((960, 540)) if rp.exists() else Image.new("RGB", (960, 540), "#333")
        ours = Image.open(p).convert("RGB").resize((960, 540))
        c = Image.new("RGB", (1930, 590), "white"); c.paste(ref, (0, 50)); c.paste(ours, (970, 50))
        d = ImageDraw.Draw(c); d.text((10, 8), f"REF f{F}", fill="red", font=FONT); d.text((980, 8), f"OURS f{F}", fill="blue", font=FONT)
        c.save(out / f"c_f{F:04d}.jpg", quality=85); tiles.append(c)
    sheet(tiles, out / "compare_sheet.jpg")
    print("compare ->", out / "compare_sheet.jpg")


def encode_frames(folder: Path, pattern: str, dst: Path, extra=()):
    subprocess.run([FF, "-v", "error", "-y", "-framerate", RATE, "-start_number", str(CFG.get("start", 0)),
                    "-i", str(folder / pattern), *extra, *ENC, str(dst)], check=True)


def fanout(mode, out_arg, a, b, jobs, extra=()):
    """Split [a,b) over `jobs` parallel renderer processes (one Chromium each; mind RAM at full size)."""
    (H / out_arg).mkdir(parents=True, exist_ok=True)
    step = (b - a) / jobs; inner = sorted(c for c in CUTS if a < c < b)
    # chunk borders snap to the nearest cut, so piped segments always start on a cut
    cuts = sorted({a, b} | {min(inner, key=lambda c: abs(c - (a + k * step))) if inner else int(a + k * step) for k in range(1, jobs)})
    procs = []
    for s, e in zip(cuts, cuts[1:]):
        log = open(H / out_arg / f"_{mode}_{s:04d}.log", "w")
        procs.append(subprocess.Popen([sys.executable, str(H / "render.py"), mode, out_arg, str(s), str(e), "--noenc", *extra],
                                      stdout=log, stderr=subprocess.STDOUT, cwd=str(H)))
    bad = [p.args[4:6] for p in procs if p.wait()]
    if bad:
        raise SystemExit(f"{mode} chunks failed {bad} - see {out_arg}/_{mode}_*.log")


def main():
    mode = sys.argv[1]
    if mode == "pops":
        v = sys.argv[2]
        raw = subprocess.run([FF, "-v", "quiet", "-i", v, "-vf", "scale=192:108,format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout
        a = np.frombuffer(raw, np.uint8).reshape(-1, 108, 192).astype(np.float32)
        d = np.abs(np.diff(a, axis=0)).mean(axis=(1, 2))
        hits = [i + 1 for i in range(1, len(d) - 1) if d[i] > 3 * max(d[i - 1], d[i + 1], 0.5) and (i + 1) not in CUTS]
        print("pops (frame idx, not in CUTS):", hits[:60]); return
    out = H / sys.argv[2]
    flags = {sys.argv[i]: sys.argv[i + 1] for i in range(3, len(sys.argv) - 1) if sys.argv[i] in ("--jobs", "--sub")}
    nums = [int(x) for i, x in enumerate(sys.argv[3:], 3) if x.lstrip("-").isdigit() and not x.startswith("--") and sys.argv[i - 1] not in flags]
    jobs = int(flags.get("--jobs", 1))   # parallel chunks (draft/full); ~1.5 GB RAM per job at full size
    if mode == "stills":
        asyncio.run(capture(nums, out, sub=False)); print("stills ->", out)
    elif mode == "compare":
        compare(nums, out)
    elif mode == "beats":
        beats = [int(round(b * FPS)) for b in CFG.get("beats", [])][:60]
        paths = asyncio.run(capture(beats, out, sub=False))
        sheet([Image.open(p).convert("RGB") for p in paths], out / "beats_sheet.jpg", cols=6, tw=480, th=270)
        print("beats ->", out / "beats_sheet.jpg")
    elif mode == "draft":
        a, b = (nums + [0, N])[:2] if nums else (0, N)
        if jobs > 1:
            fanout(mode, sys.argv[2], a, b, jobs)
        else:
            asyncio.run(capture(list(range(a, b)), out, scale=0.5, sub=False, prefix="d_"))
        if "--noenc" not in sys.argv:
            subprocess.run([FF, "-v", "error", "-y", "-framerate", RATE, "-start_number", str(a), "-i", str(out / "d_%04d.png"),
                            "-c:v", "libx264", "-crf", "23", "-preset", "veryfast", "-pix_fmt", "yuv420p", str(out / "draft.mp4")], check=True)
            print("draft ->", out / "draft.mp4")
    elif mode == "full":   # --pipe: frames go straight into x264 segments OUT/seg_F0.mp4 (no PNGs); join them with `concat`
        a, b = (nums + [0, N])[:2] if nums else (0, N)
        if jobs > 1:
            fanout(mode, sys.argv[2], a, b, jobs, ["--pipe"] if "--pipe" in sys.argv else [])
        elif "--pipe" in sys.argv:   # F0/F1 must sit on cuts (or 0/N) so segments line up with earlier renders
            out.mkdir(parents=True, exist_ok=True)
            seg = SegSink(out, [a] + [c for c in CUTS if a < c < b])
            asyncio.run(capture(list(range(a, b)), out, sub=True, sink=seg))
            seg.close()
        else:
            asyncio.run(capture(list(range(a, b)), out, sub=True))
        print("full", a, b, "->", out)
    elif mode == "concat":  # seg_*.mp4 from `full --pipe` -> OUT/film_silent.mp4 [+ audio -> OUT/film.mp4]
        segs = sorted(out.glob("seg_*.mp4"))
        (out / "segs.txt").write_text("".join(f"file '{s.name}'\n" for s in segs))
        subprocess.run([FF, "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(out / "segs.txt"), "-c", "copy",
                        "-movflags", "+faststart", str(out / "film_silent.mp4")], check=True)
        audio = sys.argv[3] if len(sys.argv) > 3 else None
        if audio:
            subprocess.run([FF, "-v", "error", "-y", "-i", str(out / "film_silent.mp4"), "-i", audio, "-c:v", "copy", "-c:a", "aac", "-b:a", "256k",
                            "-shortest", "-movflags", "+faststart", str(out / "film.mp4")], check=True)
        print("concat", len(segs), "segments ->", out)
    elif mode == "encode":
        audio = sys.argv[3] if len(sys.argv) > 3 else None
        dst = out / "film_silent.mp4"; CFG["start"] = 0
        encode_frames(out, "o_f%04d.png", dst)
        if audio:
            subprocess.run([FF, "-v", "error", "-y", "-i", str(dst), "-i", audio, "-c:v", "copy", "-c:a", "aac", "-b:a", "256k",
                            "-movflags", "+faststart", str(out / "film.mp4")], check=True)
        print("encoded ->", out)
    elif mode == "split":
        ref = H / "ref/reference.mp4"; ours = out / ("film.mp4" if (out / "film.mp4").exists() else "film_silent.mp4")
        vf = (f"[0:v]scale=944:-2,pad=960:ih+60:8:52:white,drawtext=fontfile='{FF_FONT}':text='original':x=12:y=12:fontsize=30[a];"
              f"[1:v]scale=944:-2,pad=960:ih+60:8:52:white,drawtext=fontfile='{FF_FONT}':text='ours':x=12:y=12:fontsize=30[b];"
              "[a][b]hstack=inputs=2,setsar=1[v]")
        subprocess.run([FF, "-v", "error", "-y", "-i", str(ref), "-i", str(ours), "-filter_complex", vf, "-map", "[v]", "-map", "1:a?",
                        *ENC[4:], "-c:a", "aac", "-b:a", "192k", "-shortest", str(out / "split_screen.mp4")], check=True)
        print("split ->", out / "split_screen.mp4")
    elif mode == "qa":
        frames = list(range(0, N, max(1, int(round(FPS)))))
        if "--from-draft" in sys.argv:   # reuse the half-res draft frames in out/draft (no new render)
            out.mkdir(parents=True, exist_ok=True); paths = [H / "out" / "draft" / f"d_{F:04d}.png" for F in frames]
        else:
            paths = asyncio.run(capture(frames, out, sub=False))
        tiles = []
        for F, p in zip(frames, paths):
            rp = H / f"ref/full/f{F:04d}.jpg"
            ref = Image.open(rp).convert("RGB").resize((480, 270)) if rp.exists() else Image.new("RGB", (480, 270), "#333")
            c = Image.new("RGB", (970, 300), "white"); c.paste(ref, (0, 28)); c.paste(Image.open(p).convert("RGB").resize((480, 270)), (490, 28))
            ImageDraw.Draw(c).text((6, 4), f"{F / FPS:05.2f}s  REF | OURS", fill="black", font=FONT); tiles.append(c)
        for i in range(0, len(tiles), 12):
            sheet(tiles[i:i + 12], out / f"qa_{i // 12 + 1:02d}.jpg", cols=3, tw=970, th=300)
        print("qa sheets ->", out)


if __name__ == "__main__":
    main()

