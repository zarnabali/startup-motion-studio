"""Measure a music track's beat grid -> beats.json (course step 09). The film reads it to place cuts and SFX.
  python tools/beats.py track.wav [out.json] [--fps 29.97]
beats.json: {bpm, beats[s], downbeats[s] (every 4th beat from the strongest bar phase), hits[s] (onset peaks),
             and the same three lists in frames (beats_f, downbeats_f, hits_f)}.
Rules: state changes / cuts on beats, big moments on downbeats, SFX on hits.
"""
import json, sys
from pathlib import Path

import librosa
import numpy as np


def main():
    src = sys.argv[1]
    out = Path(sys.argv[2]) if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else Path(src).with_name("beats.json")
    fps = float(sys.argv[sys.argv.index("--fps") + 1]) if "--fps" in sys.argv else 30000 / 1001
    y, sr = librosa.load(src, sr=22050, mono=True)
    tempo, bf = librosa.beat.beat_track(y=y, sr=sr, units="frames", tightness=200)
    beats = librosa.frames_to_time(bf, sr=sr)
    onset = librosa.onset.onset_strength(y=y, sr=sr)
    # downbeat phase = the beat offset (0-3) whose beats carry the most onset energy
    phase = int(np.argmax([onset[bf[p::4]].sum() if len(bf[p::4]) else 0 for p in range(4)]))
    downs = beats[phase::4]
    pk = librosa.util.peak_pick(onset, pre_max=3, post_max=3, pre_avg=3, post_avg=5, delta=0.5, wait=10)
    hits = librosa.frames_to_time(pk, sr=sr)
    r = lambda a: [round(float(x), 3) for x in a]
    f = lambda a: [int(round(float(x) * fps)) for x in a]
    data = {"bpm": round(float(np.atleast_1d(tempo)[0]), 2), "duration": round(len(y) / sr, 3), "fps": fps,
            "beats": r(beats), "downbeats": r(downs), "hits": r(hits),
            "beats_f": f(beats), "downbeats_f": f(downs), "hits_f": f(hits)}
    out.write_text(json.dumps(data, indent=1), encoding="utf-8")
    print(f"{data['bpm']} BPM, {len(beats)} beats, {len(downs)} downbeats, {len(hits)} hits -> {out}")


if __name__ == "__main__":
    main()
