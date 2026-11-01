"""Banque de sujets « immobilier en général » (sans bien précis).
Règles : conseils généraux, AUCUN chiffre statistique, AUCUN montant, aucune règle légale chiffrée ou datée.
Tout est à relire par le professionnel avant publication."""


def _hook(h, kicker):
    return {"type": "hook", "text": h, "kicker": kicker, "dur": 2.6}


def _cta(text="Une question ? Écris-moi"):
    return {"type": "cta", "text": text, "dur": 3.0}


def liste(famille, titre, kicker, hook, items, checks=False):
    return {"famille": famille, "titre": titre, "points": items,
            "scenes": [_hook(hook, kicker),
                       {"type": "list", "title": titre, "items": items, "checks": checks, "kicker": kicker,
                        "step": 1.0, "dur": 1.0 + 1.05 * len(items) + 0.8}, _cta()]}


def etapes(famille, titre, kicker, hook, items):
    return {"famille": famille, "titre": titre, "points": items,
            "scenes": [_hook(hook, kicker),
                       {"type": "steps", "title": titre, "items": items, "kicker": kicker,
                        "step": 1.0, "dur": 1.0 + 1.0 * len(items) + 0.8}, _cta()]}


def idees(famille, titre, kicker, hook, paires):
    return {"famille": famille, "titre": titre,
            "points": [f"{m} → {f}" for m, f in paires],
            "scenes": [_hook(hook, kicker)] + [{"type": "myth", "myth": m, "fact": f, "dur": 4.6} for m, f in paires]
            + [_cta()]}


STORYBOARDS = [
    liste("vendeur", "Les erreurs à éviter quand on vend", "Vendeurs", "Vendre sans faire *ces erreurs*",
          ["Fixer un prix au feeling", "Négliger les photos", "Oublier les diagnostics obligatoires",
           "Se lancer sans accompagnement"]),
    idees("idees-recues", "Idées reçues sur la vente", "Idée reçue", "Tu crois *encore* ça ?",
          [("Un prix élevé laisse de la marge pour négocier",
            "Un prix trop haut éloigne les acheteurs et le bien reste en ligne"),
           ("Les diagnostics, on verra plus tard",
            "Certains diagnostics sont obligatoires dès la mise en vente")]),
    liste("acheteur", "Avant de visiter, vérifie", "Acheteurs", "Avant ta *première visite*",
          ["Ton budget réel, frais compris", "Le diagnostic énergétique", "Les charges de copropriété",
           "Le quartier à différents moments"], checks=True),
    etapes("process", "Une vente, étape par étape", "Process", "Vendre : comment ça se passe *vraiment*",
           ["Estimation du bien", "Mise en valeur et diffusion", "Visites et offres", "Compromis puis acte"]),
    liste("vendeur", "Home staging : les bons réflexes", "Home staging", "Vends *plus vite* sans travaux lourds",
          ["Désencombrer les pièces", "Laisser entrer la lumière", "Neutraliser les couleurs",
           "Réparer les petits défauts"], checks=True),
    liste("acheteur", "Acheter ou louer ? Pose-toi ces questions", "Projet", "Acheter ou *louer* ?",
          ["Combien de temps vais-je rester ?", "De quel apport je dispose ?", "Quelle stabilité professionnelle ?",
           "Quel budget mensuel total ?"]),
    liste("acheteur", "À la visite, regarde bien", "Visite", "Ne visite pas *les yeux fermés*",
          ["Humidité et fissures", "Orientation et lumière", "Bruit à différentes heures", "Rangements et volumes"],
          checks=True),
    etapes("acheteur", "Faire une offre intelligente", "Négociation", "Comment *négocier* sans froisser",
           ["Compare avec des biens similaires", "Repère les travaux à prévoir", "Fais une offre argumentée",
            "Reste clair et courtois"]),
    etapes("vendeur", "Comment on estime un bien", "Estimation", "Ton bien vaut *combien* ?",
           ["Analyse du quartier", "Comparaison avec des ventes récentes", "État et prestations",
            "Prix de mise en vente argumenté"]),
    liste("acheteur", "Premier achat : par où commencer ?", "Premier achat", "Premier achat ? *Commence ici*",
          ["Définir ton budget", "Rencontrer ta banque", "Lister tes critères", "Visiter sans te précipiter"]),
    liste("energie", "Le DPE expliqué simplement", "DPE", "Le DPE, *c'est quoi* ?",
          ["Il note l'énergie du logement", "Des classes de A à G", "Il compte pour la vente et la location",
           "Des travaux peuvent l'améliorer"]),
    idees("idees-recues", "Idées reçues sur l'achat", "Idée reçue", "Attention aux *fausses bonnes idées*",
          [("Je regarde seulement le prix au mètre carré",
            "L'état, l'étage, le quartier et les charges comptent aussi"),
           ("Je visite une seule fois et je décide",
            "Une seconde visite à un autre moment révèle beaucoup de choses")]),
]
