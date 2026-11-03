"""Generate ONE image asset from a spec file, with the brand's style lock added automatically.
  python tools/make_image.py --spec SPEC.md --out projects/<job>/film/assets/img/S03_v1.png [--ref IMG ...] [--real]
                             [--provider auto|codex|openai|prompt] [--size 1536x1024]
Style lock: brand/IMAGE_STYLE.md section "Style lock" + "Avoid" (or "Real-photo lock" + "Real-photo avoid" with --real).
Providers:
  codex   OpenAI Codex CLI signed in with ChatGPT (`codex login`), built-in image tool — no API key needed.
  openai  OPENAI_API_KEY in the environment; model from IMAGE_MODEL (default gpt-image-1).
  prompt  writes OUT.prompt.txt only: paste it into any image tool you like and save the result at OUT.
  auto    codex if installed, else openai if OPENAI_API_KEY is set, else prompt.
Writes OUT.json beside the image (prompt, provider, refs) as provenance. Never overwrites: bump _v2, _v3 ...
"""
import argparse, base64, json, os, re, shutil, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def block(md, title):
    m = re.search(r"#+\s*[\d.a-z]*\s*" + re.escape(title) + r"[\s\S]*?```[a-z]*\s*([\s\S]*?)```", md, re.I)
    return m.group(1).strip() if m else ""


def build_prompt(spec, real, refs):
    style = (ROOT / "brand/IMAGE_STYLE.md").read_text(encoding="utf-8") if (ROOT / "brand/IMAGE_STYLE.md").exists() else ""
    lock, avoid = (block(style, "Real-photo lock"), block(style, "Real-photo avoid")) if real else (block(style, "Style lock"), block(style, "Avoid"))
    ref_note = ("Attached input images (in order): " + ", ".join(Path(r).name for r in refs) +
                ". Use them exactly as the spec says.") if refs else "No input images."
    return f"{ref_note}\n\n=== STYLE LOCK ===\n{lock}\n\n=== SPEC ===\n{spec}\n\n=== AVOID ===\n{avoid}\n"


def via_codex(prompt, refs, out):
    last = out.with_suffix(out.suffix + ".codex.txt")
    full = ("Use the $imagegen skill in its DEFAULT built-in mode (the built-in image_gen tool). Do NOT write any script.\n"
            "Generate exactly ONE image from the spec below. Do NOT run shell commands and do NOT copy or move files.\n"
            'Reply with ONLY this JSON on one line: {"source": "<absolute path of the generated file>"}\n\n' + prompt)
    cmd = [shutil.which("codex"), "exec", "--skip-git-repo-check", "--ephemeral", "-C", str(ROOT), "-s", "read-only", "-o", str(last)]
    for r in refs:
        cmd += ["-i", str(Path(r).resolve())]
    started = time.time()
    subprocess.run(cmd + ["-"], input=full, text=True, encoding="utf-8", capture_output=True)
    src = None
    try:
        src = json.loads(last.read_text(encoding="utf-8").strip()).get("source")
    except Exception:
        pass
    if not src or not Path(src).exists():   # fallback: newest file Codex wrote during this run
        gen = Path.home() / ".codex" / "generated_images"
        new = [p for p in gen.rglob("*") if p.suffix.lower() in (".png", ".jpg", ".webp") and p.stat().st_mtime > started] if gen.exists() else []
        src = str(max(new, key=lambda p: p.stat().st_mtime)) if new else None
    last.unlink(missing_ok=True)
    if not src:
        sys.exit("codex produced no image (is `codex login` done?)")
    shutil.copy(src, out)


def via_openai(prompt, refs, out, size):
    import urllib.request
    key = os.environ["OPENAI_API_KEY"]; model = os.environ.get("IMAGE_MODEL", "gpt-image-1")
    if refs:   # edits endpoint takes input images (multipart)
        import uuid
        bnd = uuid.uuid4().hex; parts = []
        for k, v in {"model": model, "prompt": prompt, "size": size}.items():
            parts.append(f'--{bnd}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
        for r in refs:
            parts.append(f'--{bnd}\r\nContent-Disposition: form-data; name="image[]"; filename="{Path(r).name}"\r\n'
                         f'Content-Type: image/png\r\n\r\n'.encode() + Path(r).read_bytes() + b"\r\n")
        body = b"".join(parts) + f"--{bnd}--\r\n".encode()
        req = urllib.request.Request("https://api.openai.com/v1/images/edits", body,
                                     {"Authorization": f"Bearer {key}", "Content-Type": f"multipart/form-data; boundary={bnd}"})
    else:
        req = urllib.request.Request("https://api.openai.com/v1/images/generations",
                                     json.dumps({"model": model, "prompt": prompt, "size": size}).encode(),
                                     {"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        data = json.loads(r.read())["data"][0]
    out.write_bytes(base64.b64decode(data["b64_json"]))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--spec", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--ref", nargs="*", default=[]); ap.add_argument("--real", action="store_true")
    ap.add_argument("--provider", default="auto", choices=["auto", "codex", "openai", "prompt"])
    ap.add_argument("--size", default="1536x1024")
    a = ap.parse_args()
    out = Path(a.out).resolve()
    if out.exists():
        sys.exit(f"refusing to overwrite {out} - bump the version suffix (_v2, _v3 ...)")
    out.parent.mkdir(parents=True, exist_ok=True)
    prompt = build_prompt(Path(a.spec).read_text(encoding="utf-8"), a.real, a.ref)
    prov = a.provider
    if prov == "auto":
        prov = "codex" if shutil.which("codex") else ("openai" if os.environ.get("OPENAI_API_KEY") else "prompt")
    if prov == "prompt":
        p = out.with_suffix(out.suffix + ".prompt.txt"); p.write_text(prompt, encoding="utf-8")
        print(f"[make_image] no image provider - prompt written to {p}. Generate it anywhere and save the image as {out}")
        return
    print(f"[make_image] {prov} -> {out}")
    via_codex(prompt, a.ref, out) if prov == "codex" else via_openai(prompt, a.ref, out, a.size)
    meta = {"spec": a.spec, "out": str(out), "refs": a.ref, "real": a.real, "provider": prov,
            "created": datetime.now(timezone.utc).isoformat(), "prompt": prompt}
    out.with_suffix(out.suffix + ".json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    print("[make_image] OK", out)


if __name__ == "__main__":
    main()
