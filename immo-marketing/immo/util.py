import json, re, subprocess, shutil
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent


def load_config(path=None):
    p = Path(path) if path else ROOT / "config.yaml"
    with open(p, encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    cfg["_base"] = str(p.parent)
    return cfg


def slug(s):
    s = re.sub(r"[^a-zA-Z0-9]+", "-", str(s)).strip("-").lower()
    return s or "x"


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        raise RuntimeError(f"Commande en échec: {' '.join(map(str, cmd))}\n{r.stderr[-1500:]}")
    return r


def need_ffmpeg():
    if not shutil.which("ffmpeg"):
        raise RuntimeError("ffmpeg est requis pour les vidéos (apt install ffmpeg).")


def read_json(p, default):
    p = Path(p)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default


def write_json(p, data):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def fmt_eur(n):
    return f"{int(round(float(n))):,}".replace(",", " ") + " €"
