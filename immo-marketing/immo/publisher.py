"""Agent 6 — Publicateur. Deux modes réellement implémentés et testés :
 - manual  : dossier prêt à poster (médias + légende) + TODAY.md
 - webhook : POST multipart vers Make / Zapier / n8n, qui relaie vers les réseaux
Aucun accès direct aux API des réseaux n'est codé ici (voir README)."""
import shutil
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import requests


def due(cfg, state, now=None):
    tz = ZoneInfo(cfg.get("timezone", "Europe/Paris"))
    now = now or datetime.now(tz)
    return [i for i in state.get("schedule", []) if i["status"] == "planned"
            and datetime.fromisoformat(i["when"]) <= now]


def publish(cfg, state, outroot, now=None):
    mode = cfg["publication"]["mode"]
    done = []
    ready_root = Path(outroot) / "ready"
    for it in due(cfg, state, now):
        try:
            if mode == "manual":
                d = ready_root / f"{it['when'][:10]}_{it['platform']}_{it['id']}"
                d.mkdir(parents=True, exist_ok=True)
                for m in it["media"]:
                    shutil.copy(m, d / Path(m).name)
                (d / "legende.txt").write_text(it["caption"], encoding="utf-8")
                it["status"] = "ready"
                it["ready_dir"] = str(d)
            elif mode == "webhook":
                url = cfg["publication"].get("webhook_url")
                if not url:
                    raise RuntimeError("publication.webhook_url manquant")
                files = [("media", (Path(m).name, open(m, "rb"))) for m in it["media"]]
                try:
                    r = requests.post(url, data={"platform": it["platform"], "format": it["format"],
                                                 "caption": it["caption"], "id": it["id"], "when": it["when"]},
                                      files=files, timeout=120)
                finally:
                    for _, (_, fh) in files:
                        fh.close()
                r.raise_for_status()
                it["status"] = "published"
            else:
                raise RuntimeError(f"mode inconnu: {mode}")
            done.append(it)
        except Exception as e:  # une erreur ne bloque pas les autres posts
            it["status"] = "error"
            it["error"] = str(e)[:300]
    if mode == "manual":
        write_today(state, ready_root)
    return done


def write_today(state, ready_root):
    ready_root = Path(ready_root)
    ready_root.mkdir(parents=True, exist_ok=True)
    rows = [i for i in state.get("schedule", []) if i["status"] == "ready"]
    lines = ["# À poster", ""]
    for i in rows:
        lines.append(f"- **{i['when'][:16].replace('T', ' ')}** · {i['platform']} · {i['format']} · `{i['ready_dir']}`")
    if not rows:
        lines.append("_Rien en attente._")
    (ready_root / "TODAY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
