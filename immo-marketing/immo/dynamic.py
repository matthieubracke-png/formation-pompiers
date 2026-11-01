"""Moteur de reels dynamiques : coupes rapides, mouvements de caméra variés, sous-titres animés
mot par mot (style TikTok/Reels), barre de progression, voix/avatar + musique.
Rendu 100 % local avec ffmpeg (libass pour les sous-titres)."""
import json, re, shutil, subprocess, tempfile
from pathlib import Path
from PIL import Image
from .util import run, need_ffmpeg
from .visuals import hex_rgb

W, H, FPS = 1080, 1920, 25
MOTIONS = ["in", "left", "out", "right"]


def audio_duration(path):
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(path)])
    return float(json.loads(r.stdout)["format"]["duration"])


def plan_timing(lines, total=None):
    """Durée par ligne (proportionnelle au nombre de caractères) -> [(start, dur, [(word, t0, t1)])]."""
    lines = [l.strip() for l in lines if l.strip()]
    if total is None:
        total = sum(max(1.6, len(l.split()) * 0.42) for l in lines)
    weights = [max(8, len(l)) for l in lines]
    sc = total / sum(weights)
    out, t = [], 0.0
    for l, w in zip(lines, weights):
        d = max(1.2, w * sc) if total / len(lines) > 1.2 else w * sc
        words = l.split()
        cw = [max(2, len(x)) for x in words]
        k = d / sum(cw)
        ws, tt = [], t
        for x, c in zip(words, cw):
            ws.append((x, tt, tt + c * k))
            tt += c * k
        out.append((t, d, ws))
        t += d
    return out


def _ass_time(s):
    cs = int(round(s * 100))
    return f"{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}"


def _esc(w):
    return re.sub(r"[{}\\]", "", w)


def make_ass(timing, cfg, total, price=None, status=None):
    acc = hex_rgb(cfg["brand"]["couleur_accent"])
    prm = hex_rgb(cfg["brand"]["couleur_principale"])
    bgr = lambda c: f"&H00{c[2]:02X}{c[1]:02X}{c[0]:02X}&"
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Cap,DejaVu Sans,92,&H00FFFFFF&,&H00FFFFFF&,&H00000000&,&H80000000&,1,0,0,0,100,100,0,0,1,8,2,2,60,60,560,1
Style: Tag,DejaVu Sans,54,{bgr(prm)},{bgr(prm)},{bgr(acc)},{bgr(acc)},1,0,0,0,100,100,0,0,3,14,0,8,60,60,170,1
Style: Foot,DejaVu Sans,34,&H00FFFFFF&,&H00FFFFFF&,&H00000000&,&H00000000&,1,0,0,0,100,100,0,0,1,3,0,2,60,60,60,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""
    ev = []
    for (_, _, ws) in timing:
        # blocs de 3 mots max, mot actif en couleur d'accent + effet « pop »
        for b in range(0, len(ws), 3):
            chunk = ws[b:b + 3]
            for i, (w, t0, t1) in enumerate(chunk):
                parts = []
                for j, (x, _, _) in enumerate(chunk):
                    x = _esc(x).upper()
                    if j == i:
                        parts.append(r"{\c" + bgr(acc) + r"\fscx118\fscy118\t(0,110,\fscx100\fscy100)}" + x + r"{\c&H00FFFFFF&}")
                    else:
                        parts.append(x)
                end = chunk[i + 1][1] if i + 1 < len(chunk) else t1
                ev.append(f"Dialogue: 0,{_ass_time(t0)},{_ass_time(end)},Cap,,0,0,0,,{' '.join(parts)}")
    if status:
        ev.append(f"Dialogue: 1,{_ass_time(0)},{_ass_time(total)},Tag,,0,0,0,,{_esc(status)}")
    if price:
        ev.append(f"Dialogue: 1,{_ass_time(max(0, total - 2.6))},{_ass_time(total)},Tag,,0,0,0,,{_esc(price)}")
    a = cfg["agent"]
    ev.append(f"Dialogue: 1,{_ass_time(0)},{_ass_time(total)},Foot,,0,0,0,,{_esc(a['nom'])} · {_esc(a['telephone'])}")
    return head + "\n".join(ev) + "\n"


def _prep_image(src, dst, size=(1620, 2880)):
    from PIL import ImageOps
    ImageOps.fit(Image.open(src).convert("RGB"), size, Image.LANCZOS).save(dst, quality=92)


def broll_clip(img, dur, motion, out):
    n = max(2, int(dur * FPS))
    z = {"in": f"'1+0.16*on/{n}'", "out": f"'1.16-0.16*on/{n}'", "left": "1.14", "right": "1.14"}[motion]
    x = {"left": f"'(iw-iw/zoom)*(1-on/{n})'", "right": f"'(iw-iw/zoom)*on/{n}'"}.get(motion, "'iw/2-(iw/zoom/2)'")
    vf = (f"zoompan=z={z}:x={x}:y='ih/2-(ih/zoom/2)':d={n}:s={W}x{H}:fps={FPS},"
          f"eq=contrast=1.08:saturation=1.15,format=yuv420p")
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(img), "-vf", vf, "-frames:v", str(n),
         "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", str(FPS), str(out)])


def avatar_segment(src, t0, dur, out):
    vf = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps={FPS},format=yuv420p"
    run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{t0:.3f}", "-t", f"{dur:.3f}", "-i", str(src), "-vf", vf,
         "-an", "-c:v", "libx264", "-preset", "veryfast", "-r", str(FPS), str(out)])


def build(lines, images, cfg, out, voice=None, avatar=None, prop=None, status=None):
    """lines: phrases du script. voice: audio de voix off. avatar: vidéo d'un présentateur (avec sa voix)."""
    need_ffmpeg()
    out = Path(out).resolve()  # ffmpeg tourne dans un dossier temporaire : tout en chemins absolus
    out.parent.mkdir(parents=True, exist_ok=True)
    images = [str(Path(i).resolve()) for i in images]
    avatar = str(Path(avatar).resolve()) if avatar else None
    voice = str(Path(voice).resolve()) if voice else None
    speech = avatar or voice
    total = (audio_duration(speech) + 0.3) if speech else None
    timing = plan_timing(lines, total)
    total = timing[-1][0] + timing[-1][1]
    music = (cfg.get("voix") or {}).get("musique")
    music = str(Path(music).resolve()) if music else None
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        pics = []
        for i, p in enumerate(images):
            d = tmp / f"img{i}.jpg"
            _prep_image(p, d)
            pics.append(d)
        if not pics:  # fond dégradé de marque
            from .visuals import background
            bg = background((1620, 2880), None, cfg)
            d = tmp / "img0.jpg"
            bg.save(d)
            pics = [d]
        clips = []
        for i, (t0, dur, _) in enumerate(timing):
            c = tmp / f"c{i}.mp4"
            use_avatar = avatar and (i == 0 or i == len(timing) - 1 or i % 3 == 0)
            if use_avatar:
                avatar_segment(avatar, t0, dur, c)
            else:
                broll_clip(pics[i % len(pics)], dur, MOTIONS[i % 4], c)
            clips.append(c)
        lst = tmp / "list.txt"
        lst.write_text("".join(f"file '{c}'\n" for c in clips))
        cat = tmp / "cat.mp4"
        run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(cat)])
        (tmp / "cap.ass").write_text(make_ass(timing, cfg, total, price=prop.prix_txt() if prop else None,
                                              status=status), encoding="utf-8")
        accent = cfg["brand"]["couleur_accent"].lstrip("#")
        inputs = ["-i", str(cat)]
        fc = (f"[0:v]subtitles=cap.ass:fontsdir=/usr/share/fonts/truetype/dejavu[s];"
              f"color=c=0x{accent}:s={W}x14:d={total:.2f}:r={FPS}[bar];"
              f"[s][bar]overlay=x='-w+W*t/{total:.3f}':y=H-14:eval=frame,format=yuv420p[v]")
        maps = ["-map", "[v]"]
        ai = 1
        if speech:
            inputs += ["-i", str(speech)]
        if music and Path(music).exists():
            inputs += ["-stream_loop", "-1", "-i", str(music)]
        if speech and music and Path(music).exists():
            fc += f";[1:a]volume=1.0[a1];[2:a]volume=0.12[a2];[a1][a2]amix=inputs=2:duration=first[a]"
            maps += ["-map", "[a]"]
        elif speech:
            maps += ["-map", "1:a"]
        elif music and Path(music).exists():
            fc += ";[1:a]volume=0.5[a]"
            maps += ["-map", "[a]"]
        run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", fc, *maps, "-t", f"{total:.2f}",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-c:a", "aac", "-b:a", "160k", str(out)], cwd=tmp)
    return str(out)
