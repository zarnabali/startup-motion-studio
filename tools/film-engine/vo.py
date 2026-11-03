"""Voice-over track from vo.json with Kokoro TTS (local, open weights, Apache-2.0). Run from the film folder:
  python vo.py [vo.json] [OUT.wav]          -> out/audio/vo_track.wav (48 kHz stereo) + a per-line timing report
vo.json: {"voice": "af_heart", "lang": "en-us", "speed": 1.0, "lines": [{"t": 0.9, "text": "..."}, ...]}
Each line starts at t (seconds). A line that would run into the next one is re-spoken faster (max 1.15x) and flagged.
Model files: tools/tts/kokoro-v1.0.onnx + voices-v1.0.bin (thewh1teagle/kokoro-onnx release model-files-v1.0).
Mix with: python sfx.py cues.json OUT.wav --vo out/audio/vo_track.wav [--music track.mp3 ...]
"""
import json, sys
from pathlib import Path

import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

H = Path.cwd()
CFG = json.loads((H / "film.json").read_text(encoding="utf-8-sig"))
DUR = CFG["frames"] / CFG["fps"]; SR = 48000


def models():
    for p in [Path(__file__).resolve().parent, *Path(__file__).resolve().parents]:
        for m in (p / "tts", p / "tools" / "tts"):
            if (m / "kokoro-v1.0.onnx").exists():
                return m
    raise SystemExit("Kokoro model files not found (expected tools/tts/kokoro-v1.0.onnx + voices-v1.0.bin)")


def speak(k, text, voice, speed, lang):
    y, sr = k.create(text, voice=voice, speed=speed, lang=lang)
    y = np.asarray(y, np.float32); a = np.abs(y) > 0.012
    if a.any():                                   # trim TTS leading/trailing silence so t is the real onset
        i0, i1 = np.argmax(a), len(y) - np.argmax(a[::-1])
        y = y[max(0, i0 - int(0.02 * sr)): min(len(y), i1 + int(0.08 * sr))]
    n = int(len(y) * SR / sr)                     # resample 24 kHz -> 48 kHz
    return np.interp(np.arange(n) * sr / SR, np.arange(len(y)), y).astype(np.float32)


def main():
    vj = json.loads(Path(sys.argv[1] if len(sys.argv) > 1 else H / "vo.json").read_text(encoding="utf-8-sig"))
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else H / "out" / "audio" / "vo_track.wav"
    m = models(); k = Kokoro(str(m / "kokoro-v1.0.onnx"), str(m / "voices-v1.0.bin"))
    voice, lang, base = vj.get("voice", "af_heart"), vj.get("lang", "en-us"), vj.get("speed", 1.0)
    lines = sorted(vj["lines"], key=lambda l: l["t"]); track = np.zeros(int((DUR + 1) * SR), np.float32)
    print(f"{'start':>6} {'end':>6} {'next':>6} speed  text")
    for i, ln in enumerate(lines):
        nxt = lines[i + 1]["t"] if i + 1 < len(lines) else DUR
        sp = ln.get("speed", base); y = speak(k, ln["text"], voice, sp, lang); room = nxt - ln["t"] - 0.12
        if len(y) / SR > room:
            sp = min(1.15, sp * (len(y) / SR) / room); y = speak(k, ln["text"], voice, sp, lang)
        i0 = int(ln["t"] * SR); j = min(len(track), i0 + len(y)); track[i0:j] += y[: j - i0]
        end = ln["t"] + len(y) / SR
        print(f"{ln['t']:6.2f} {end:6.2f} {nxt:6.2f} {sp:4.2f}{'  OVERLAP' if end > nxt else ''}  {ln['text']}")
    track = track[: int(DUR * SR)]; out.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(out), np.stack([track, track], 1), SR, subtype="FLOAT")
    print("vo ->", out, f"| peak {np.abs(track).max():.2f}")


if __name__ == "__main__":
    main()
