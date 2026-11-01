"""Moteur d'animations (motion design) : vidéos sans photo, rendues image par image dans Chromium."""
import json, shutil, subprocess, tempfile
from pathlib import Path
from ..util import run, need_ffmpeg
from ..visuals import hex_rgb

HERE = Path(__file__).parent


def _dark(h, k=0.45):
    r, g, b = hex_rgb(h)
    return "#%02x%02x%02x" % (int(r * k), int(g * k), int(b * k))


def script_lines(sb):
    """Texte à dire (voix off / avatar) pour un storyboard."""
    out = []
    for s in sb["scenes"]:
        if s["type"] == "hook":
            out.append(s["text"].replace("*", ""))
        elif s["type"] in ("list", "steps"):
            out.append(s["title"])
            out += s["items"]
        elif s["type"] == "myth":
            out += [f"Idée reçue : {s['myth']}.", f"En réalité : {s['fact']}."]
        elif s["type"] == "cta":
            out.append(s["text"])
    return out


def render(sb, cfg, out, voice=None, fps=None):
    from ..dynamic import audio_duration
    fps = fps or int((cfg.get("rendu") or {}).get("fps", 25))
    need_ffmpeg()
    if not shutil.which("node"):
        raise RuntimeError("Node.js + playwright requis pour les animations (voir README).")
    out = Path(out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    scenes = [dict(s) for s in sb["scenes"]]
    total = sum(s["dur"] for s in scenes)
    if voice:  # on cale le montage sur la durée de la voix
        va = audio_duration(voice) + 0.4
        if va > total:
            k = va / total
            for s in scenes:
                s["dur"] *= k
            total = va
    data = {"colors": {"main": cfg["brand"]["couleur_principale"], "accent": cfg["brand"]["couleur_accent"],
                       "dark": _dark(cfg["brand"]["couleur_principale"])},
            "agent": {"nom": cfg["agent"]["nom"], "agence": cfg["agent"].get("agence", ""),
                      "telephone": cfg["agent"]["telephone"]},
            "scenes": scenes}
    html = (HERE / "template.html").read_text(encoding="utf-8").replace("__DATA__", json.dumps(data, ensure_ascii=False))
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "page.html").write_text(html, encoding="utf-8")
        silent = tmp / "silent.mp4"
        run(["node", str(HERE / "render.js"), str(tmp / "page.html"), str(silent), str(fps), f"{total:.3f}"], timeout=900)
        music = (cfg.get("voix") or {}).get("musique")
        music = str(Path(music).resolve()) if music and Path(music).exists() else None
        if voice and music:
            run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(silent), "-i", str(voice), "-stream_loop", "-1", "-i", music,
                 "-filter_complex", "[1:a]volume=1[a1];[2:a]volume=0.12[a2];[a1][a2]amix=inputs=2:duration=first[a]",
                 "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-shortest", str(out)])
        elif voice:
            run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(silent), "-i", str(voice), "-map", "0:v", "-map", "1:a",
                 "-c:v", "copy", "-c:a", "aac", "-shortest", str(out)])
        elif music:
            run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(silent), "-stream_loop", "-1", "-i", music, "-map", "0:v",
                 "-map", "1:a", "-af", "volume=0.5", "-c:v", "copy", "-c:a", "aac", "-t", f"{total:.2f}", str(out)])
        else:
            shutil.copyfile(silent, out)
    return str(out)
