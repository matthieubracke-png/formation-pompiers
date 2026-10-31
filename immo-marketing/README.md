# Agents IA — marketing immobilier automatisé

Tu déposes un bien (photos, fiche, vidéos éventuelles). Les agents font le reste :
textes, carrousels, reels, contenu de marque personnelle, planning, mise à disposition/publication.

## Ce que ça fait (vérifié par les tests : `python -m unittest discover -s tests`)

| Agent | Rôle | Fichier |
|---|---|---|
| 1 Intake | lit `inbox/<bien>/` ; fiche PDF/texte → `bien.yaml` pré-rempli **à relire** ; bloque les biens incomplets | `immo/property.py` |
| 2 Rédacteur | légendes par réseau, scripts vidéo ; via Claude si `ANTHROPIC_API_KEY`, sinon modèles fixes ; **tout chiffre absent de la fiche est rejeté** ; prix/honoraires/DPE ajoutés par le code, jamais par l'IA | `immo/copy.py` |
| 3 Designer | carrousels 1080×1350 (couverture, chiffres clés, atouts, mentions, CTA) aux couleurs de ta marque | `immo/visuals.py` |
| 4 Réalisateur | reels 1080×1920 (zoom lent, sous-titres, prix, voix off optionnelle) ; **ta propre vidéo** est recadrée en 9:16 avec bandeau | `immo/video.py` |
| 5 Planificateur | calendrier glissant (14 j), cadence par réseau, mix 65 % biens / 35 % marque, relance des biens actifs, 1 seul post « vendu/sous compromis », zéro doublon | `immo/planner.py` |
| 6 Publicateur | `manual` : dossiers prêts + `TODAY.md` ; `webhook` : envoi vers Make/Zapier/n8n | `immo/publisher.py` |

Pas besoin de te filmer : les vidéos de marque (conseils vendeurs/acheteurs, DPE, déroulé d'une vente…) sont des
reels « sans visage » : photos, texte à l'écran, et voix off si tu branches un outil de synthèse vocale.

## Démarrage

```bash
pip install -r requirements.txt        # + ffmpeg installé sur la machine
export ANTHROPIC_API_KEY=...           # optionnel mais recommandé
# 1. édite config.yaml (ton nom, agence, couleurs, cadence)
python -m immo new rue-victor-hugo     # crée inbox/rue-victor-hugo/{photos,videos,bien.yaml}
# 2. dépose photos/vidéos, remplis bien.yaml, mets a_verifier: false
python -m immo run                     # intake → visuels → planning → publication des posts échus
python -m immo status                  # voir le planning
```
Chaque jour, relance `python -m immo run` (cron, tâche planifiée, ou le workflow GitHub fourni).

## Ce qui n'est PAS automatique — à lire

1. **Publication directe sur Instagram/Facebook/LinkedIn/TikTok/YouTube : non codée.** Chaque réseau exige
   un compte pro, une app et une validation/clé API que je ne peux ni créer ni tester d'ici. Deux voies, toutes deux
   fonctionnelles dans le code : (a) mode `manual` — tu postes en 30 s depuis `out/ready/` (tu as dit en être prêt) ;
   (b) mode `webhook` — tu crées un scénario Make/Zapier/n8n qui reçoit le POST (légende + médias) et publie.
   Je n'ai testé le webhook que contre un serveur local, pas contre Make/Zapier/n8n eux-mêmes ni les réseaux.
2. **Voix off / avatar** : le code appelle la commande locale que tu indiques dans `voix.commande`
   (testée avec une fausse commande). Je n'ai testé aucun moteur vocal réel. Pour un avatar parlant à ton image
   (type HeyGen, Synthesia, D-ID…), il faudrait un compte chez eux : **non intégré, non vérifié** (tarifs/API non contrôlés).
3. **Qualité des textes** : sans clé Anthropic, les textes sont des modèles fixes, corrects mais répétitifs.
   Avec clé, je n'ai testé que la logique (réponses simulées), pas de vrais appels API.
4. **Conformité** : le code bloque la publication s'il manque prix, surface, ville, classe DPE, ou mention des honoraires.
   Ce n'est **pas un avis juridique** : vérifie les mentions obligatoires de ton métier (carte T, etc.) avant d'automatiser.
5. **Photos réelles** : testé avec des images synthétiques ; vérifie le rendu avec tes vraies photos.
6. Le workflow `.github/workflows/immo-marketing-daily.yml` n'a **pas été exécuté**.
7. Vidéos de marque sans photos : fond uni. Dépose quelques photos de toi/ta ville dans `brand/` pour les enrichir.
