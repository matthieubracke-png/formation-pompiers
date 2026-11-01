"""Agent 5 — Planificateur : calendrier glissant, mix biens/marque, anti-doublon, relances."""
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
from . import copy as copywriter, visuals, video, avatar as avatar_mod, learn, motion, topics


def spread(n):
    n = max(1, min(7, n))
    return sorted({round(i * 7 / n) % 7 for i in range(n)})


def _assets_property(prop, fmt, cfg, outroot, lines):
    if fmt == "texte":
        return []
    base = Path(outroot) / "assets" / prop.key
    if fmt in ("carousel", "photo"):
        d = base / "carousel"
        if not d.exists() or not any(d.iterdir()):
            visuals.property_carousel(prop, lines, cfg, d)
        files = sorted(str(p) for p in d.glob("slide_*.jpg"))
        return files[:1] if fmt == "photo" else files
    f = base / "reel.mp4"
    if not f.exists():
        if prop.videos:
            video.reframe_video(prop.videos[0], cfg, f, prop=prop)
        else:
            video.build_reel(lines, [str(p) for p in prop.photos], cfg, f, prop=prop)
    return [str(f)]


def _assets_brand(idx, fmt, post, cfg, outroot):
    if fmt == "texte":
        return []
    title, pts = copywriter.TOPICS[idx % len(copywriter.TOPICS)]
    base = Path(outroot) / "assets" / f"marque-{idx % len(copywriter.TOPICS)}"
    if fmt in ("carousel", "photo"):
        d = base / "carousel"
        if not d.exists() or not any(d.iterdir()):
            visuals.brand_carousel(title, pts, cfg, d)
        files = sorted(str(p) for p in d.glob("slide_*.jpg"))
        return files[:1] if fmt == "photo" else files
    f = base / "reel.mp4"
    if not f.exists():
        av = None
        try:
            av = avatar_mod.make(cfg, ". ".join(post["script"]), base / "avatar.mp4", f"marque-{idx}")
        except Exception as e:  # avatar indisponible => reel sans visage, on ne bloque pas
            print(f"[avatar] {e} -> reel sans visage")
        if av:
            video.build_reel(post["script"], [], cfg, f, avatar=av)
        else:
            sb = topics.STORYBOARDS[idx % len(topics.STORYBOARDS)]
            try:
                import tempfile
                with tempfile.TemporaryDirectory() as tmp:
                    voice = video.tts(motion.script_lines(sb), cfg, tmp)
                    motion.render(sb, cfg, f, voice=voice)
            except Exception as e:  # pas de Node/Chromium => ancien montage photos/texte
                print(f"[motion] {e} -> montage simple")
                video.build_reel(post["script"], [], cfg, f)
    return [str(f)]


def plan(cfg, props, state, outroot, now=None):
    tz = ZoneInfo(cfg.get("timezone", "Europe/Paris"))
    now = now or datetime.now(tz)
    sched = state.setdefault("schedule", [])
    slots = {(i["platform"], i["when"]) for i in sched}
    ok = [p for p in props if p.d.get("_ok")]
    created = []
    for off in range(int(cfg.get("horizon_jours", 14))):
        day = (now + timedelta(days=off)).date()
        for platform, pc in cfg["plateformes"].items():
            wds = spread(pc["par_semaine"])
            if day.weekday() not in wds:
                continue
            hh, mm = pc["heures"][wds.index(day.weekday()) % len(pc["heures"])].split(":")
            dt = datetime(day.year, day.month, day.day, int(hh), int(mm), tzinfo=tz)
            if dt <= now or (platform, dt.isoformat()) in slots:
                continue
            item = _choose(cfg, ok, sched, platform, pc, dt, outroot)
            item["when"] = dt.isoformat()
            item["platform"] = platform
            item["id"] = f"{dt:%Y%m%d-%H%M}-{platform}"
            item["status"] = "planned"
            sched.append(item)
            slots.add((platform, item["when"]))
            created.append(item)
    sched.sort(key=lambda i: i["when"])
    return created


def _choose(cfg, props, sched, platform, pc, dt, outroot):
    mine = [i for i in sched if i["status"] != "error"]
    n_b = sum(1 for i in mine if i["category"] == "biens")
    n_m = sum(1 for i in mine if i["category"] == "marque")
    target = float(cfg.get("mix_biens", 0.65))
    want_bien = (n_b <= (n_b + n_m) * target)
    relance = timedelta(days=int(cfg.get("relance_bien_jours", 10)))
    cand = None
    if want_bien and props:
        def last(p):
            ds = [datetime.fromisoformat(i["when"]) for i in mine if i["platform"] == platform and i.get("ref") == p.key]
            return max(ds) if ds else None
        pool = []
        for p in props:
            l = last(p)
            if l is None or (p.disponible and dt - l >= relance):
                pool.append((l is not None, l or datetime.min.replace(tzinfo=dt.tzinfo), p))
        if pool:
            pool.sort(key=lambda t: (t[0], t[1]))
            cand = pool[0][2]
    fmts = learn.format_order(outroot, platform, pc["formats"])
    if cand:
        k = sum(1 for i in mine if i["platform"] == platform and i["category"] == "biens")
        fmt = fmts[k % len(fmts)]
        post = copywriter.property_post(cand, platform, cfg)
        lines = post["script"]
        media = _assets_property(cand, fmt, cfg, outroot, lines)
        return {"category": "biens", "ref": cand.key, "format": fmt, "caption": post["caption"], "media": media}
    idx = n_m
    k = sum(1 for i in mine if i["platform"] == platform and i["category"] == "marque")
    fmt = fmts[k % len(fmts)]
    post = copywriter.brand_post(idx, cfg)
    media = _assets_brand(idx, fmt, post, cfg, outroot)
    return {"category": "marque", "ref": f"marque-{idx % len(copywriter.TOPICS)}", "format": fmt,
            "caption": post["caption"], "media": media}
