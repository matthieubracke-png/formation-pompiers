"""Agent 2 — Rédacteur : légendes, hooks, scripts vidéo. Anti-hallucination intégrée."""
import re
from . import llm

HASHTAGS_BASE = {"instagram": 8, "facebook": 3, "linkedin": 4, "tiktok": 5, "youtube": 4}


def _num(s):
    return re.sub(r"[\s  .,]", "", s)


def allowed_numbers(facts):
    nums = set()

    def walk(v):
        if isinstance(v, dict):
            for x in v.values():
                walk(x)
        elif isinstance(v, (list, tuple)):
            for x in v:
                walk(x)
        else:
            nums.update(_num(m) for m in re.findall(r"\d[\d\s  .,]*\d|\d", str(v)))
    walk(facts)
    return nums


def guard(text, facts):
    """Refuse tout chiffre (prix, m², pièces...) absent de la fiche. Renvoie la liste des intrus."""
    ok = allowed_numbers(facts)
    bad = []
    for m in re.findall(r"\d[\d\s  .,]*\d|\d", text):
        n = _num(m)
        if n and n not in ok:
            bad.append(m.strip())
    return bad


def _hashtags(prop, platform, extra=()):
    base = ["immobilier", (prop.d.get("ville") or "").replace(" ", "").replace("-", "").lower(),
            "agentimmobilier", "bienimmobilier", (prop.d.get("type_bien") or "").lower(),
            "achatimmobilier" if prop.d.get("transaction") != "location" else "location", "visite"]
    tags = [t for t in list(extra) + base if t]
    return ["#" + t for t in dict.fromkeys(tags)][: HASHTAGS_BASE.get(platform, 4)]


def _fallback(prop, cfg):
    d = prop.d
    verb = "À louer" if d.get("transaction") == "location" else "À vendre"
    where = d.get("quartier") or d.get("ville")
    t = f"{verb} à {d.get('ville')}" + (f" ({d['quartier']})" if d.get("quartier") else "")
    specs = " · ".join(x for x in [
        f"{d['type_bien']}" if d.get("type_bien") else "",
        f"{d['surface']} m²" if d.get("surface") else "",
        f"{d['pieces']} pièces" if d.get("pieces") else "",
        f"{d['chambres']} chambres" if d.get("chambres") else ""] if x)
    atouts = d.get("atouts") or []
    hook = f"{t} 👀"
    body = [specs] + [f"✔ {a}" for a in atouts[:4]]
    if d.get("description"):
        body.append(d["description"].strip().split("\n")[0][:240])
    cta = (f"Envie de visiter ? Commente « INFO » ou écris-moi en message privé, "
           f"ou appelle le {cfg['agent']['telephone']}.")
    script = [t] + ([specs] if specs else []) + atouts[:3] + [prop.prix_txt(), "Contacte-moi pour visiter"]
    return {"hook": hook, "body": "\n".join(b for b in body if b), "cta": cta,
            "script": [s for s in script if s]}


def property_post(prop, platform, cfg):
    facts = prop.facts()
    data = None
    if llm.available():
        sys_ = ("Tu es le community manager d'un agent immobilier français. Écris en français, ton: "
                f"{cfg['agent']['ton']}. {'Vouvoiement.' if cfg['agent'].get('vouvoiement') else 'Tutoiement.'} "
                "RÈGLE ABSOLUE: n'utilise QUE les faits fournis. Aucun chiffre, adresse, équipement ou "
                "superlatif non présent dans les faits. Pas de promesse de rentabilité. Réponds en JSON.")
        usr = (f"Réseau: {platform}. Faits (JSON): {facts}\n"
               'Format: {"hook": "accroche courte avec emoji", "body": "corps de légende, retours ligne ok", '
               '"cta": "appel à l\'action", "script": ["5 à 7 lignes très courtes pour une vidéo verticale"]}'
               "\nNe mets PAS le prix/honoraires/DPE: ils sont ajoutés automatiquement.")
        data = llm.complete_json(sys_, usr, model=cfg["llm"]["model"])
        if data:
            blob = " ".join([data.get("hook", ""), data.get("body", ""), data.get("cta", "")]
                            + list(data.get("script", [])))
            if guard(blob + " " + cfg["agent"]["telephone"], {**facts, "tel": cfg["agent"]["telephone"]}):
                data = None  # chiffre inventé => on jette
    data = data or _fallback(prop, cfg)
    caption = "\n\n".join([data["hook"], data["body"], data["cta"], prop.mentions(),
                           " ".join(_hashtags(prop, platform))])
    return {"caption": caption, "script": data["script"], "hook": data["hook"]}


# --- Contenu de marque personnelle (pas de chiffres inventés : aucun chiffre dans les sujets) ---
TOPICS = [
    ("Pourquoi une estimation gratuite ne vaut pas toujours une vraie estimation",
     ["Le prix affiché n'est pas le prix de vente", "Un bon prix se justifie par des ventes comparables",
      "Un prix trop haut allonge les délais", "Demande une estimation argumentée"]),
    ("Les erreurs à éviter quand on met son bien en vente",
     ["Ne pas préparer les photos", "Surestimer son bien", "Négliger les diagnostics",
      "Se passer d'un accompagnement"]),
    ("Acheter : les questions à poser avant de visiter",
     ["Quel budget réel, frais compris ?", "Que dit le diagnostic énergétique ?",
      "Quelles charges de copropriété ?", "Quel quartier à long terme ?"]),
    ("Home staging : petits changements, grand effet",
     ["Désencombre", "Lumière naturelle", "Neutralise les couleurs", "Soigne l'entrée"]),
    ("Le DPE expliqué simplement",
     ["Il note la performance énergétique", "De A à G", "Il influence la valeur et la location",
      "Des travaux peuvent l'améliorer"]),
    ("Comment se déroule une vente avec un agent",
     ["Estimation", "Mise en valeur et diffusion", "Visites et offres", "Compromis puis acte"]),
]


def brand_post(topic_index, cfg):
    title, pts = TOPICS[topic_index % len(TOPICS)]
    a = cfg["agent"]
    data = None
    if llm.available():
        data = llm.complete_json(
            f"Tu écris pour {a['nom']}, agent immobilier à {a['ville']}, ton {a['ton']}. Français. "
            "Aucun chiffre ni statistique (tu ne peux pas les vérifier). Pas de promesse. JSON.",
            f"Sujet: {title}\nPoints de départ: {pts}\n"
            '{"hook":"...", "body":"légende 4-6 lignes", "cta":"...", "script":["6 lignes courtes pour une vidéo"]}',
            model=cfg["llm"]["model"])
        if data and guard(" ".join([data.get("hook", ""), data.get("body", ""), data.get("cta", "")]
                                   + list(data.get("script", []))), {}):
            data = None
    if not data:
        data = {"hook": f"{title} 🏡", "body": "\n".join(f"→ {p}" for p in pts),
                "cta": f"Une question ? Écris-moi, je réponds personnellement. {a['nom']}, {a['agence']} ({a['ville']}).",
                "script": [title] + pts + [f"{a['nom']} — {a['ville']}"]}
    tags = " ".join(["#immobilier", "#" + a["ville"].replace(" ", "").replace("-", "").lower(),
                     "#conseilimmo", "#agentimmobilier"])
    return {"title": title, "caption": "\n\n".join([data["hook"], data["body"], data["cta"], tags]),
            "script": data["script"], "hook": data["hook"]}
