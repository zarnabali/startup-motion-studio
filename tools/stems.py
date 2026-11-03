"""Split a soundtrack into stems with Demucs htdemucs (Meta, MIT; runs locally on CPU).
  python tools/stems.py IN.wav OUTDIR
  -> OUTDIR/vocals.wav, drums.wav, bass.wav, other.wav, instrumental.wav (= everything but vocals), 44.1 kHz stereo
Use: take a reference film's music bed without its voice-over (internal temp tracks only - the music stays unlicensed).
Weights (~80 MB) download once to the torch hub cache on first run.
"""
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
import torch
from scipy.signal import resample_poly
from demucs.apply import apply_model
from demucs.pretrained import get_model


def main():
    src, out = Path(sys.argv[1]), Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
    model = get_model("htdemucs"); model.eval(); msr = model.samplerate
    wav, sr = sf.read(str(src), always_2d=True, dtype="float32")             # (n, ch)
    if wav.shape[1] == 1:
        wav = np.repeat(wav, 2, 1)
    if sr != msr:
        g = np.gcd(int(sr), int(msr)); wav = resample_poly(wav, msr // g, sr // g, axis=0).astype(np.float32)
    x = torch.from_numpy(wav[:, :2].T.copy())                               # (2, n)
    ref = x.mean(0); mu, sd = ref.mean(), ref.std()
    with torch.no_grad():
        stems = apply_model(model, ((x - mu) / sd)[None], shifts=1, split=True, overlap=0.25, progress=True)[0]
    stems = stems * sd + mu
    inst = torch.zeros_like(stems[0])
    for name, s in zip(model.sources, stems):
        sf.write(str(out / f"{name}.wav"), s.numpy().T, msr, subtype="FLOAT")
        if name != "vocals":
            inst += s
    sf.write(str(out / "instrumental.wav"), inst.numpy().T, msr, subtype="FLOAT")
    print("stems ->", out, model.sources, "+ instrumental")


if __name__ == "__main__":
    main()
