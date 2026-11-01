import argparse, sys
from pathlib import Path
from . import pipeline, property as prop_mod
from .util import load_config, read_json, ROOT


def main(argv=None):
    ap = argparse.ArgumentParser(prog="immo", description="Agents IA marketing immobilier")
    ap.add_argument("cmd", choices=["run", "status", "new", "learn"], help="run = tout faire ; status = voir le planning ; new = créer un dossier bien ; learn = analyser tes statistiques")
    ap.add_argument("name", nargs="?")
    ap.add_argument("--config")
    ap.add_argument("--inbox", default=str(ROOT / "inbox"))
    ap.add_argument("--out", default=str(ROOT / "out"))
    a = ap.parse_args(argv)
    cfg = load_config(a.config)
    if a.cmd == "new":
        d = Path(a.inbox) / (a.name or "nouveau-bien")
        (d / "photos").mkdir(parents=True, exist_ok=True)
        (d / "videos").mkdir(exist_ok=True)
        (d / "bien.yaml").write_text(prop_mod.TEMPLATE, encoding="utf-8")
        print(f"Dossier créé : {d}\nDépose-y photos/, videos/ (optionnel), et remplis bien.yaml")
    elif a.cmd == "learn":
        from . import learn
        r = learn.run_learning(a.out)
        print("Pas de out/metrics.csv" if r is None else "\n".join(f"{k:<22} score {v['score']:.3f} · {v['vues']} vues · {v['posts']} posts" for k, v in sorted(r.items(), key=lambda kv: -kv[1]['score'])))
    elif a.cmd == "run":
        pipeline.run_daily(cfg, a.inbox, a.out)
    else:
        st = read_json(Path(a.out) / "state.json", {"schedule": []})
        for i in st["schedule"]:
            print(f"{i['when'][:16]}  {i['platform']:<9} {i['format']:<8} {i['category']:<7} {i['ref']:<22} {i['status']}")
        print(f"{len(st['schedule'])} posts")


if __name__ == "__main__":
    sys.exit(main())
