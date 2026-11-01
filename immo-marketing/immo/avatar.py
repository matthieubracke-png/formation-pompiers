"""Présentateur qui parle (sans que tu te filmes).
Modes :
 - clip : tu fournis toi-même des vidéos de présentateur (générées par l'outil de ton choix) ; le programme les
          découpe/recadre/sous-titre. TESTÉ localement.
 - did  : génération via l'API D-ID à partir d'UNE photo de toi. Écrit d'après la doc publique de D-ID, testé
          UNIQUEMENT contre un faux serveur ; jamais contre le vrai service (pas de clé ici). Clé: DID_API_KEY."""
import os, time
from pathlib import Path
import requests


class AvatarError(RuntimeError):
    pass


def make(cfg, text, out, key):
    a = cfg.get("avatar") or {}
    prov = a.get("provider", "none")
    out = Path(out)
    if prov in (None, "none"):
        return None
    if prov == "clip":
        d = Path(cfg["_base"]) / a.get("dossier", "brand/avatar")
        clips = sorted(d.glob("*.mp4")) if d.is_dir() else []
        if not clips:
            raise AvatarError(f"aucune vidéo de présentateur dans {d}")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(clips[hash(key) % len(clips)].read_bytes())
        return str(out)
    if prov == "did":
        return _did(a, text, out)
    raise AvatarError(f"provider avatar inconnu: {prov}")


def _did(a, text, out, poll=3, tries=60):
    key = os.environ.get(a.get("cle_env", "DID_API_KEY"))
    if not key:
        raise AvatarError("variable DID_API_KEY absente")
    if not a.get("photo_url"):
        raise AvatarError("avatar.photo_url requis (URL publique d'une photo de face)")
    base = (a.get("api_base") or "https://api.d-id.com").rstrip("/")
    h = {"Authorization": f"Basic {key}", "Content-Type": "application/json"}
    body = {"source_url": a["photo_url"],
            "script": {"type": "text", "input": text,
                       "provider": {"type": "microsoft", "voice_id": a.get("voix", "fr-FR-DeniseNeural")}}}
    r = requests.post(f"{base}/talks", json=body, headers=h, timeout=60)
    r.raise_for_status()
    tid = r.json()["id"]
    for _ in range(tries):
        g = requests.get(f"{base}/talks/{tid}", headers=h, timeout=60)
        g.raise_for_status()
        j = g.json()
        if j.get("status") == "done":
            v = requests.get(j["result_url"], timeout=300)
            v.raise_for_status()
            Path(out).parent.mkdir(parents=True, exist_ok=True)
            Path(out).write_bytes(v.content)
            return str(out)
        if j.get("status") == "error":
            raise AvatarError(f"D-ID erreur: {str(j.get('error'))[:200]}")
        time.sleep(poll)
    raise AvatarError("D-ID trop long")
