"""Agent 4 — Réalisateur : reels verticaux 1080x1920 (Ken Burns + sous-titres + voix off/musique).
Aucune apparition à l'écran requise : « vidéo sans visage »."""
import shlex, subprocess, tempfile
from pathlib import Path
from PIL import Image, ImageDraw
from .util import run, need_ffmpeg
import shutil
from .visuals import background, pill, hex_rgb, font, wrap, status_label

W, H = 1080, 1920
SCENE = 3.2


def _overlay(text, cfg, path, price=None, status=None):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    f = font(cfg, 74, True)
    lines = wrap(d, text, f, 920)
    boxh = len(lines) * 92 + 60
    y0 = 1180
    d.rounded_rectangle([50, y0, W - 50, y0 + boxh], 30, fill=(0, 0, 0, 150))
    y = y0 + 30
    for ln in lines:
        d.text((80, y), ln, font=f, fill=(255, 255, 255, 255))
        y += 92
    if status:
        pill(im, status, cfg, (60, 110), 46)
    if price:
        pill(im, price, cfg, (60, y0 + boxh + 30), 50)
    a = cfg["agent"]
    d.rectangle([0, H - 130, W, H], fill=hex_rgb(cfg["brand"]["couleur_principale"]) + (235,))
    d.text((50, H - 95), f"{a['nom']} · {a['telephone']}", font=font(cfg, 38), fill=(255, 255, 255, 255))
    im.save(path)


def _scene(img, overlay, out, dur):
    frames = int(dur * 25)
    vf = (f"[0:v]scale=2160:3840:force_original_aspect_ratio=increase,crop=2160:3840,"
          f"zoompan=z='min(zoom+0.0009,1.18)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={W}x{H}:fps=25[bg];"
          f"[bg][1:v]overlay=eof_action=repeat,format=yuv420p[v]")
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(img), "-i", str(overlay), "-filter_complex", vf,
         "-map", "[v]", "-t", str(dur), "-r", "25", "-c:v", "libx264", "-preset", "veryfast", str(out)])


def tts(lines, cfg, workdir):
    cmd = (cfg.get("voix") or {}).get("commande")
    if not cmd:
        return None
    txt = Path(workdir) / "voix.txt"
    out = Path(workdir) / "voix.wav"
    txt.write_text(". ".join(lines), encoding="utf-8")
    subprocess.run(shlex.split(cmd.format(text_file=str(txt), out=str(out))), check=True, capture_output=True)
    return out if out.exists() else None


def build_reel(lines, images, cfg, out, prop=None):
    """lines: un sous-titre par scène ; images: liste de photos (réutilisées en boucle)."""
    need_ffmpeg()
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        brand_dir = Path(cfg["_base"]) / cfg["brand"].get("photos_marque", "brand/")
        pics = list(images) or (sorted(p for p in brand_dir.glob("*")
                                       if p.suffix.lower() in {".jpg", ".jpeg", ".png"}) if brand_dir.is_dir() else [])
        clips = []
        for i, line in enumerate(lines):
            src = pics[i % len(pics)] if pics else None
            bg = tmp / f"bg{i}.jpg"
            background((W, H), src, cfg, darken=0.15 if src else 0).save(bg)
            ov = tmp / f"ov{i}.png"
            last = i == len(lines) - 1
            _overlay(line, cfg, ov, price=prop.prix_txt() if (prop and last) else None,
                     status=status_label(prop) if prop else None)
            clip = tmp / f"c{i}.mp4"
            _scene(bg, ov, clip, SCENE)
            clips.append(clip)
        lst = tmp / "list.txt"
        lst.write_text("".join(f"file '{c}'\n" for c in clips))
        silent = tmp / "silent.mp4"
        run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(silent)])
        audio = tts(lines, cfg, tmp) or ((cfg.get("voix") or {}).get("musique"))
        if audio and Path(audio).exists():
            run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(silent), "-i", str(audio), "-map", "0:v", "-map", "1:a",
                 "-c:v", "copy", "-c:a", "aac", "-shortest", str(out)])
        else:
            shutil.copyfile(silent, out)
    return str(out)


def reframe_video(src, cfg, out, headline="", prop=None):
    """Prend une vidéo fournie (16:9 ou autre) -> 9:16, 30 s max, bandeau d'infos."""
    need_ffmpeg()
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        ov = Path(tmp) / "ov.png"
        _overlay(headline or (prop.d.get("ville", "") if prop else ""), cfg, ov, price=prop.prix_txt() if prop else None)
        vf = (f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1[bg];"
              f"[bg][1:v]overlay=eof_action=repeat,format=yuv420p[v]")
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-i", str(ov), "-filter_complex", vf,
             "-map", "[v]", "-map", "0:a?", "-t", "30", "-r", "25", "-c:v", "libx264", "-preset", "veryfast",
             "-c:a", "aac", str(out)])
    return str(out)
