"""Agent 3 — Designer : carrousels (images) + utilitaires de rendu."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

DEJAVU = "/usr/share/fonts/truetype/dejavu/DejaVuSans{}.ttf"


def font(cfg, size, bold=False):
    p = cfg["brand"].get("police")
    for cand in ([p] if p else []) + [DEJAVU.format("-Bold" if bold else "")]:
        try:
            return ImageFont.truetype(cand, size)
        except Exception:
            continue
    return ImageFont.load_default()


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def background(size, photo, cfg, darken=0.45):
    w, h = size
    if photo:
        im = ImageOps.fit(Image.open(photo).convert("RGB"), size, Image.LANCZOS)
        shade = Image.new("RGB", size, (0, 0, 0))
        return Image.blend(im, shade, darken)
    base = hex_rgb(cfg["brand"]["couleur_principale"])
    im = Image.new("RGB", size, base)
    d = ImageDraw.Draw(im)
    for y in range(h):  # dégradé vertical
        k = y / h
        d.line([(0, y), (w, y)], fill=tuple(int(c * (1 - 0.5 * k)) for c in base))
    return im


def wrap(draw, text, fnt, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= maxw:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text_block(im, text, cfg, xy, size, maxw, color="white", bold=True, anchor_bottom=False, spacing=14):
    d = ImageDraw.Draw(im)
    f = font(cfg, size, bold)
    lines = wrap(d, text, f, maxw)
    lh = size + spacing
    x, y = xy
    if anchor_bottom:
        y -= lh * len(lines)
    for ln in lines:
        d.text((x, y), ln, font=f, fill=color)
        y += lh
    return y


def pill(im, text, cfg, xy, size=40):
    d = ImageDraw.Draw(im)
    f = font(cfg, size, True)
    w = int(d.textlength(text, font=f)) + 50
    x, y = xy
    d.rounded_rectangle([x, y, x + w, y + size + 34], 40, fill=hex_rgb(cfg["brand"]["couleur_accent"]))
    d.text((x + 25, y + 14), text, font=f, fill=hex_rgb(cfg["brand"]["couleur_principale"]))


def footer(im, cfg):
    a = cfg["agent"]
    w, h = im.size
    d = ImageDraw.Draw(im)
    d.rectangle([0, h - 110, w, h], fill=hex_rgb(cfg["brand"]["couleur_principale"]))
    d.text((50, h - 82), f"{a['nom']} · {a['agence']} · {a['telephone']}", font=font(cfg, 30), fill="white")


def status_label(prop):
    return {"sous_compromis": "SOUS COMPROMIS", "vendu": "VENDU", "loue": "LOUÉ"}.get(prop.d.get("statut"))


def property_carousel(prop, lines, cfg, outdir):
    """5 à 8 slides 1080x1350."""
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    S = (1080, 1350)
    d = prop.d
    photos = prop.photos
    slides = []

    def ph(i):
        return photos[i % len(photos)] if photos else None

    # 1 couverture
    im = background(S, ph(0), cfg)
    if status_label(prop):
        pill(im, status_label(prop), cfg, (60, 60))
    verb = "À LOUER" if d.get("transaction") == "location" else "À VENDRE"
    text_block(im, f"{verb} · {d.get('ville', '')}".upper(), cfg, (60, 760), 76, 960)
    if prop.prix_txt():
        pill(im, prop.prix_txt(), cfg, (60, 1010), 52)
    footer(im, cfg)
    slides.append(im)
    # 2 chiffres clés
    im = background(S, None, cfg)
    text_block(im, "L'essentiel", cfg, (70, 120), 80, 940)
    facts = [x for x in [
        d.get("type_bien") and str(d["type_bien"]).capitalize(),
        d.get("surface") and f"{d['surface']} m²",
        d.get("pieces") and f"{d['pieces']} pièces",
        d.get("chambres") and f"{d['chambres']} chambres",
        d.get("etage") and f"Étage : {d['etage']}",
        d.get("quartier") and f"Quartier : {d['quartier']}"] if x]
    y = 300
    for t in facts:
        y = text_block(im, "• " + t, cfg, (80, y), 54, 920, bold=False) + 24
    footer(im, cfg)
    slides.append(im)
    # 3.. un atout par photo
    for i, a in enumerate((d.get("atouts") or [])[:4]):
        im = background(S, ph(i + 1), cfg, darken=0.35)
        text_block(im, a, cfg, (60, 1180), 66, 960, anchor_bottom=True)
        footer(im, cfg)
        slides.append(im)
    # mentions légales + CTA
    im = background(S, None, cfg)
    text_block(im, "Envie de visiter ?", cfg, (70, 140), 80, 940)
    text_block(im, "Écris-moi en message privé ou appelle-moi.", cfg, (70, 380), 50, 940, bold=False)
    text_block(im, prop.mentions(), cfg, (70, 720), 34, 940, bold=False)
    footer(im, cfg)
    slides.append(im)
    paths = []
    for i, im in enumerate(slides, 1):
        p = outdir / f"slide_{i:02d}.jpg"
        im.save(p, quality=90)
        paths.append(str(p))
    return paths


def brand_carousel(title, points, cfg, outdir):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    S = (1080, 1350)
    brand_dir = Path(cfg["_base"]) / cfg["brand"].get("photos_marque", "brand/")
    pics = sorted(p for p in brand_dir.glob("*") if p.suffix.lower() in {".jpg", ".jpeg", ".png"}) if brand_dir.is_dir() else []
    ims = []
    im = background(S, pics[0] if pics else None, cfg)
    text_block(im, title, cfg, (70, 400), 78, 940)
    pill(im, f"{cfg['agent']['nom']}", cfg, (70, 1000), 44)
    footer(im, cfg)
    ims.append(im)
    for i, pt in enumerate(points, 1):
        im = background(S, None, cfg)
        text_block(im, str(i), cfg, (70, 120), 200, 940)
        text_block(im, pt, cfg, (70, 460), 66, 940)
        footer(im, cfg)
        ims.append(im)
    im = background(S, None, cfg)
    text_block(im, "Une question ? Écris-moi.", cfg, (70, 400), 74, 940)
    footer(im, cfg)
    ims.append(im)
    out = []
    for i, im in enumerate(ims, 1):
        p = outdir / f"slide_{i:02d}.jpg"
        im.save(p, quality=90)
        out.append(str(p))
    return out
