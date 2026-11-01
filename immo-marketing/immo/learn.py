"""Boucle d'apprentissage : lit TES vraies statistiques (out/metrics.csv) et ajuste le mix de formats.
Colonnes : id,vues,likes,commentaires,enregistrements,partages  (id = identifiant du post dans state.json).
Export possible depuis Instagram/TikTok/Metricool/vidIQ. Sans données, rien ne change."""
import csv
from collections import defaultdict
from pathlib import Path
from .util import read_json, write_json


def score(r):
    v = max(1.0, float(r.get("vues") or 0))
    # enregistrements et partages pèsent plus que les likes (signaux d'intérêt fort)
    return (float(r.get("likes") or 0) + 3 * float(r.get("enregistrements") or 0)
            + 4 * float(r.get("partages") or 0) + 2 * float(r.get("commentaires") or 0)) / v, v


def run_learning(outroot):
    outroot = Path(outroot)
    mp = outroot / "metrics.csv"
    if not mp.exists():
        return None
    posts = {i["id"]: i for i in read_json(outroot / "state.json", {"schedule": []})["schedule"]}
    agg = defaultdict(lambda: [0.0, 0.0, 0])
    for r in csv.DictReader(open(mp, encoding="utf-8")):
        p = posts.get(r["id"])
        if not p:
            continue
        s, v = score(r)
        for key in (f"{p['platform']}|{p['format']}", f"*|{p['format']}", f"*|{p['category']}"):
            a = agg[key]
            a[0] += s * v
            a[1] += v
            a[2] += 1
    res = {k: {"score": round(a[0] / a[1], 4), "vues": int(a[1]), "posts": a[2]} for k, a in agg.items() if a[1]}
    write_json(outroot / "learn.json", res)
    return res


def format_order(outroot, platform, formats, min_posts=3):
    """Formats classés du meilleur au moins bon ; ne s'active qu'avec assez de données (min_posts)."""
    res = read_json(Path(outroot) / "learn.json", {})
    sc = {f: res.get(f"{platform}|{f}") for f in formats}
    if any(v is None or v["posts"] < min_posts for v in sc.values()):
        return list(formats)
    ranked = sorted(formats, key=lambda f: -sc[f]["score"])
    return ranked + [ranked[0]]  # le meilleur format passe 2 fois sur (n+1)
