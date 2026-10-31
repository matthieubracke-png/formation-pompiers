"""Appel à l'API Claude (HTTP direct). Sans clé => renvoie None et les agents
basculent sur leurs modèles de texte fixes."""
import json, os, re
import requests

_backend = None  # injectable pour les tests


def set_backend(fn):
    global _backend
    _backend = fn


def available():
    return _backend is not None or bool(os.environ.get("ANTHROPIC_API_KEY"))


def complete(system, user, model="claude-sonnet-5-5", max_tokens=1800):
    if _backend:
        return _backend(system, user)
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return None
    r = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
        json={"model": model, "max_tokens": max_tokens, "system": system,
              "messages": [{"role": "user", "content": user}]},
        timeout=120,
    )
    r.raise_for_status()
    return "".join(b.get("text", "") for b in r.json()["content"])


def complete_json(system, user, **kw):
    txt = complete(system, user, **kw)
    if not txt:
        return None
    m = re.search(r"\{.*\}", txt, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None
