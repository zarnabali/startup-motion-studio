"""Synthesized SFX + music mix, frame-exact, two-pass loudnorm to -14 LUFS (claude-motion-design audio approach).
  python sfx.py cues.json OUT.wav [--music track.mp3 --music-offset SECONDS --music-gain 0.8] [--temp-ref] [--lufs -14]
                 [--vo out/audio/vo_track.wav --vo-gain 1 --duck 0.55 --sfx-gain 0.65]   (voice-over from vo.py ducks the music)
cues.json: [{"f": 162, "type": "hit", "gain": 0.3}, {"f": 440, "type": "keys", "n": 42, "dur_f": 50}, ...]
types: tick (soft UI tick) · click (tap) · keys (typing burst: n keystrokes over dur_f frames, human cadence) · pop ·
       whoosh (whip, dur_f) · hit (low thump for drops/logo) · swell (rising pad, dur_f) · shimmer (airy sparkle, dur_f)
--temp-ref: use the reference soundtrack (ref/audio.wav) as the music bed — INTERNAL REVIEW ONLY, never deliver.
"""
import json, subprocess, sys
from pathlib import Path

import imageio_ffmpeg
import numpy as np

FF = imageio_ffmpeg.get_ffmpeg_exe()
H = Path.cwd()
CFG = json.loads((H / "film.json").read_text(encoding="utf-8-sig"))
FPS, N, SR = CFG["fps"], CFG["frames"], 48000
DUR = N / FPS
rng = np.random.default_rng(7)


def env(n, a=0.002, d=0.08):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / max(d, 1e-4))


def tone(f0, f1, dur, d, a=0.002):
    n = int(dur * SR); t = np.arange(n) / SR
    f = np.linspace(f0, f1, n); ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * env(n, a, d)


def noise(dur, lo, hi, d, a=0.004):
    n = int(dur * SR); x = rng.standard_normal(n)
    X = np.fft.rfft(x); fr = np.fft.rfftfreq(n, 1 / SR); X[(fr < lo) | (fr > hi)] = 0
    y = np.fft.irfft(X, n); y /= np.abs(y).max() + 1e-9
    return y * env(n, a, d)


def layer(*parts):   # sum layers of different lengths
    out = np.zeros(max(len(p) for p in parts))
    for p in parts:
        out[:len(p)] += p
    return out


def make(c):
    t = c["type"]
    if t == "tick": return layer(0.5 * tone(2400, 1800, 0.05, 0.012), 0.3 * noise(0.03, 3000, 9000, 0.006))
    if t == "click": return layer(0.6 * tone(1400, 900, 0.07, 0.02), 0.4 * noise(0.04, 1500, 6000, 0.01))
    if t == "pop": return tone(500, 1100, 0.12, 0.05)
    if t == "hit": return layer(0.9 * tone(110, 42, 0.9, 0.35, a=0.003), 0.25 * noise(0.5, 40, 400, 0.2))
    if t == "whoosh":
        d = c.get("dur_f", 10) / FPS; y = noise(d + 0.15, 300, 7000, d * 0.6, a=d * 0.5); return y
    if t == "swell":
        d = c.get("dur_f", 30) / FPS; n = int(d * SR); x = np.linspace(0, 1, n)
        return (np.sin(2 * np.pi * 220 * np.arange(n) / SR) * 0.4 + np.sin(2 * np.pi * 330 * np.arange(n) / SR) * 0.25) * x ** 2 * (1 - x ** 8)
    if t == "shimmer":
        d = c.get("dur_f", 20) / FPS; y = noise(d, 6000, 14000, d * 0.5, a=d * 0.3); return 0.6 * y
    if t == "keys":
        n, d = c.get("n", 20), c.get("dur_f", 40) / FPS
        out = np.zeros(int((d + 0.2) * SR)); times = np.sort(rng.uniform(0, d, n))
        for k in times:
            s = 0.5 * noise(0.03, 2000, 8000, 0.006) + 0.3 * tone(1800 + rng.uniform(-200, 200), 1200, 0.03, 0.008)
            i = int(k * SR); out[i:i + len(s)] += s[:len(out) - i] * rng.uniform(0.6, 1.0)
        return out
    raise ValueError(t)


def opt(name, default):
    return type(default)(sys.argv[sys.argv.index(name) + 1]) if name in sys.argv else default


def read_audio(path, off=0.0):
    raw = subprocess.run([FF, "-v", "quiet", "-ss", str(max(0, off)), "-i", str(path), "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2)


def main():
    cues = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8-sig")); out = Path(sys.argv[2]); out.parent.mkdir(parents=True, exist_ok=True)
    mix = np.zeros((int((DUR + 1) * SR), 2), np.float32)
    sfx_g = opt("--sfx-gain", 1.0)                      # with a voice-over the SFX sit lower (0.6-0.7)
    for c in cues:
        y = make(c) * c.get("gain", 0.2) * sfx_g; i = int(round(c["f"] / FPS * SR))
        if i >= len(mix): continue
        j = min(len(mix), i + len(y)); pan = c.get("pan", 0.0)
        mix[i:j, 0] += y[: j - i] * (1 - max(0, pan)); mix[i:j, 1] += y[: j - i] * (1 + min(0, pan))
    music = None
    if "--temp-ref" in sys.argv:
        music, off, g = str(H / "ref/audio.wav"), 0.0, 1.0
    elif "--music" in sys.argv:
        music = sys.argv[sys.argv.index("--music") + 1]
        off = float(sys.argv[sys.argv.index("--music-offset") + 1]) if "--music-offset" in sys.argv else 0.0
        g = float(sys.argv[sys.argv.index("--music-gain") + 1]) if "--music-gain" in sys.argv else 0.8
    vo = None
    if "--vo" in sys.argv:                              # voice-over track (vo.py): unity gain, ducks the music
        v = read_audio(sys.argv[sys.argv.index("--vo") + 1]) * opt("--vo-gain", 1.0)
        vo = np.zeros_like(mix); vo[: min(len(v), len(vo))] = v[: len(vo)]
    if music:
        m = read_audio(music, off) * g
        mus = np.zeros_like(mix); start = int(max(0, -off) * SR); k = min(len(mix) - start, len(m)); mus[start:start + k] = m[:k]
        if vo is not None:                              # sidechain duck: -depth when the voice speaks (60 ms attack, 400 ms release)
            lvl = np.abs(vo).max(1); hop = SR // 100
            env = np.array([lvl[i:i + hop].max() for i in range(0, len(lvl), hop)]) > 0.02
            sm = np.zeros(len(env)); a_up, a_dn = 1 - np.exp(-1 / 6), 1 - np.exp(-1 / 40)
            for i in range(len(env)):
                prev = sm[i - 1] if i else 0.0; sm[i] = prev + (a_up if env[i] > prev else a_dn) * (env[i] - prev)
            duck = 1 - opt("--duck", 0.55) * np.repeat(sm, hop)[: len(mus)]
            mus *= duck[:, None]
        mix += mus
    if vo is not None:
        mix += vo
    mix = mix[: int(DUR * SR)]
    fade = int(1.2 * SR); mix[-fade:] *= np.linspace(1, 0, fade)[:, None]
    raw = out.with_suffix(".raw.wav")
    subprocess.run([FF, "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", str(raw)], input=mix.astype(np.float32).tobytes(), check=True)
    L = float(sys.argv[sys.argv.index("--lufs") + 1]) if "--lufs" in sys.argv else -14.0   # SFX-only stem: -20
    m = subprocess.run([FF, "-hide_banner", "-i", str(raw), "-af", f"loudnorm=I={L}:TP=-1.3:LRA=11:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
    js = json.loads(m[m.rfind("{"): m.rfind("}") + 1])
    af = (f"loudnorm=I={L}:TP=-1.3:LRA=11:measured_I={js['input_i']}:measured_TP={js['input_tp']}:measured_LRA={js['input_lra']}:"
          f"measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true")
    subprocess.run([FF, "-v", "error", "-y", "-i", str(raw), "-af", af, "-ar", str(SR), str(out)], check=True)
    # loudnorm falls back to dynamic mode on short / sparse mixes and can miss by 1-3 LU: measure and correct once
    m = subprocess.run([FF, "-hide_banner", "-i", str(out), "-af", f"loudnorm=I={L}:TP=-1.3:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
    got = float(json.loads(m[m.rfind("{"): m.rfind("}") + 1])["input_i"])
    if abs(got - L) > 0.5:
        tmp = out.with_suffix(".tmp.wav"); out.replace(tmp)
        subprocess.run([FF, "-v", "error", "-y", "-i", str(tmp), "-af", f"volume={L - got:.2f}dB,alimiter=limit={10 ** (-1.5 / 20):.4f}:level=false",
                        "-ar", str(SR), str(out)], check=True)
        tmp.unlink(missing_ok=True)
    raw.unlink(missing_ok=True)
    print("mix ->", out, "| measured input", js["input_i"], "LUFS")


if __name__ == "__main__":
    main()
