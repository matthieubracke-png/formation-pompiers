"""Agent 1 — Intake : lit le dossier d'un bien déposé dans inbox/ et le valide."""
from pathlib import Path
import yaml
from . import llm
from .util import fmt_eur

IMG = {".jpg", ".jpeg", ".png", ".webp"}
VID = {".mp4", ".mov", ".m4v"}

TEMPLATE = """# Remplis ce qui est connu. Tout champ vide reste vide : rien n'est inventé.
a_verifier: false        # passe à false quand tu as relu (obligatoire pour publier)
ref: ""
transaction: vente       # vente | location
statut: disponible       # disponible | sous_compromis | vendu | loue
type_bien: appartement   # appartement | maison | terrain | local ...
titre: ""
ville: ""
quartier: ""
prix: null               # vente: prix FAI en € ; location: loyer mensuel CC
surface: null            # m² habitables
pieces: null
chambres: null
etage: ""
atouts: []               # ex: ["balcon plein sud", "parking", "proche tram"]
dpe: ""                  # classe énergie A-G (OBLIGATOIRE dans l'annonce)
ges: ""
honoraires: ""           # texte exact, ex: "Honoraires 4 % TTC à la charge de l'acquéreur" (OBLIGATOIRE)
description: ""
"""


class Property:
    def __init__(self, folder: Path, data: dict):
        self.folder = Path(folder)
        self.d = data
        self.photos = sorted(p for p in (self.folder / "photos").glob("*") if p.suffix.lower() in IMG) \
            if (self.folder / "photos").is_dir() else []
        self.videos = sorted(p for p in (self.folder / "videos").glob("*") if p.suffix.lower() in VID) \
            if (self.folder / "videos").is_dir() else []

    def __getattr__(self, k):
        try:
            return self.__dict__["d"].get(k)
        except KeyError:
            raise AttributeError(k)

    @property
    def key(self):
        return str(self.d.get("ref") or self.folder.name)

    @property
    def disponible(self):
        return (self.d.get("statut") or "disponible") == "disponible"

    def prix_txt(self):
        if self.d.get("prix") in (None, ""):
            return ""
        suffix = " /mois CC" if self.d.get("transaction") == "location" else " FAI"
        return fmt_eur(self.d["prix"]) + suffix

    def mentions(self):
        """Mentions obligatoires, toujours ajoutées en programmatique (jamais confiées au LLM)."""
        bits = []
        if self.prix_txt():
            bits.append(self.prix_txt())
        if self.d.get("honoraires"):
            bits.append(str(self.d["honoraires"]))
        if self.d.get("dpe"):
            bits.append(f"DPE : {self.d['dpe']}" + (f" / GES : {self.d['ges']}" if self.d.get("ges") else ""))
        bits.append(f"Réf. {self.key}")
        return " — ".join(bits)

    def facts(self):
        keep = ("ref", "transaction", "statut", "type_bien", "titre", "ville", "quartier", "prix",
                "surface", "pieces", "chambres", "etage", "atouts", "dpe", "description")
        return {k: self.d[k] for k in keep if self.d.get(k) not in (None, "", [])}


def problems(p: Property):
    """Contrôle avant publication. Je ne suis pas juriste : adapte à ta réglementation en vigueur."""
    out = []
    d = p.d
    if d.get("a_verifier", True):
        out.append("fiche non relue (a_verifier: true)")
    for k, label in (("ville", "ville"), ("prix", "prix"), ("surface", "surface"),
                     ("dpe", "classe DPE"), ("honoraires", "mention des honoraires")):
        if d.get(k) in (None, "", 0):
            out.append(f"{label} manquant(e)")
    if d.get("dpe") and str(d["dpe"]).upper() not in list("ABCDEFG"):
        out.append("classe DPE invalide (A-G)")
    return out


def load_properties(inbox: Path):
    props = []
    for folder in sorted(Path(inbox).iterdir()):
        f = folder / "bien.yaml"
        if folder.is_dir() and f.exists():
            data = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
            props.append(Property(folder, data))
    return props


def extract_from_fiche(folder: Path, model):
    """Si l'agent n'a déposé qu'une fiche PDF/texte : extraction auto -> bien.yaml À RELIRE."""
    target = folder / "bien.yaml"
    if target.exists():
        return None
    text = ""
    for pdf in folder.glob("*.pdf"):
        from pypdf import PdfReader
        text += "\n".join((pg.extract_text() or "") for pg in PdfReader(str(pdf)).pages)
    for t in folder.glob("*.txt"):
        text += "\n" + t.read_text(encoding="utf-8", errors="ignore")
    data = None
    if text.strip() and llm.available():
        data = llm.complete_json(
            "Tu extrais des données d'une fiche immobilière en JSON. N'invente RIEN : "
            "si une info n'est pas explicitement dans le texte, laisse null/''/[].",
            "Champs: ref, transaction(vente|location), type_bien, titre, ville, quartier, prix(nombre), "
            "surface(nombre), pieces, chambres, etage, atouts(liste), dpe, ges, honoraires(texte exact), "
            f"description.\n\nFICHE:\n{text[:12000]}", model=model)
    if data:
        data["a_verifier"] = True
        data.setdefault("statut", "disponible")
        target.write_text("# Extrait automatiquement — RELIS puis mets a_verifier: false\n"
                          + yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
        return "extrait de la fiche (à relire)"
    target.write_text(TEMPLATE, encoding="utf-8")
    return "gabarit créé (à remplir)"
