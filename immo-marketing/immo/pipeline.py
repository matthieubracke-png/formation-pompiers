"""Orchestrateur : un seul appel quotidien fait tout."""
from pathlib import Path
from . import property as prop_mod, planner, publisher
from .util import read_json, write_json


def run_daily(cfg, inbox, outroot, now=None, log=print):
    inbox, outroot = Path(inbox), Path(outroot)
    # 1. Intake (fiches PDF/texte -> bien.yaml à relire)
    for folder in sorted(p for p in inbox.iterdir() if p.is_dir()):
        msg = prop_mod.extract_from_fiche(folder, cfg["llm"]["model"])
        if msg:
            log(f"[intake] {folder.name}: {msg}")
    props = prop_mod.load_properties(inbox)
    blocked = {}
    for p in props:
        pb = prop_mod.problems(p)
        p.d["_ok"] = not pb
        if pb:
            blocked[p.key] = pb
            log(f"[intake] ⛔ {p.key} non publié : {', '.join(pb)}")
    # 2-4. Planification + création des visuels/vidéos/textes
    sp = outroot / "state.json"
    state = read_json(sp, {"schedule": []})
    created = planner.plan(cfg, props, state, outroot, now=now)
    log(f"[planning] {len(created)} nouveaux posts planifiés")
    # 5. Publication des posts arrivés à échéance
    done = publisher.publish(cfg, state, outroot, now=now)
    log(f"[publication] {len(done)} posts traités (mode {cfg['publication']['mode']})")
    write_json(sp, state)
    return {"created": created, "published": done, "blocked": blocked}
