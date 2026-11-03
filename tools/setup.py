"""One-command setup (Windows / macOS / Linux). Everything stays inside this folder; nothing is installed system-wide.
  python tools/setup.py            core: .venv + Python packages + Playwright Chromium
  python tools/setup.py --voice    + Kokoro TTS model files (~340 MB) into tools/tts  (local voice-over)
  python tools/setup.py --stems    + Demucs (PyTorch, ~1 GB) for stem separation (optional)
Needs Python 3.10-3.13 on PATH. Uses `uv` when installed (faster), else venv + pip.
"""
import os, shutil, subprocess, sys, urllib.request
from pathlib import Path

T = Path(__file__).resolve().parent
VENV = T / ".venv"
PY = VENV / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
CORE = ["playwright", "imageio-ffmpeg", "numpy", "pillow", "librosa", "soundfile", "scipy", "opencv-python-headless",
        "scenedetect", "yt-dlp"]
VOICE = ["kokoro-onnx"]
STEMS = ["torch", "torchaudio", "demucs"]
KOKORO = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/"


def run(*cmd):
    print("+", " ".join(map(str, cmd))); subprocess.run(list(map(str, cmd)), check=True)


def pip(pkgs):
    if shutil.which("uv"):
        run("uv", "pip", "install", "--python", PY, *pkgs)
    else:
        run(PY, "-m", "pip", "install", "--upgrade", *pkgs)


def main():
    if not PY.exists():
        if shutil.which("uv"):
            run("uv", "venv", "--python", "3.12", VENV)
        else:
            run(sys.executable, "-m", "venv", VENV)
    pip(CORE)
    run(PY, "-m", "playwright", "install", "chromium")
    if "--voice" in sys.argv:
        pip(VOICE); (T / "tts").mkdir(exist_ok=True)
        for f in ["kokoro-v1.0.onnx", "voices-v1.0.bin"]:
            if not (T / "tts" / f).exists():
                print("downloading", f); urllib.request.urlretrieve(KOKORO + f, T / "tts" / f)
    if "--stems" in sys.argv:
        pip(STEMS)
    print(f"\nsetup done. Python for every tool: {PY}")


if __name__ == "__main__":
    main()
