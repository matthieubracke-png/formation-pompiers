# Reels dynamiques, présentateur qui parle, ce qui marche — synthèse honnête

Recherche faite le 2026-10-31 par recherche web. **Aucune de ces sources n'est une étude contrôlée** : ce sont des blogs
d'agents, des comparatifs d'outils (souvent écrits par des vendeurs). À prendre comme des pistes, pas comme des preuves.

## 1. Ce qui est le plus répété pour les reels immobiliers
- Accroche **dans les 1 à 3 premières secondes**, ciblée (ex. une question à un type d'acheteur). — nowbam.com, shhots.ai
- Clips **courts et centrés sur 2-3 atouts**, coupes rapides plutôt que visite complète. — nowbam.com
- Instagram dit lui-même que la **probabilité de regarder jusqu'au bout** est un signal clé → on optimise la durée de visionnage.
- Chiffres souvent cités (« 3,7 % d'engagement », « 2,7× plus que les carrousels ») : **sans source d'origine traçable, non fiables**.
- **Ce que le programme applique** : première phrase = accroche, coupes de 1,5-3 s, mouvements de caméra alternés, sous-titres mot par mot,
  barre de progression. Je n'ai **pas** de preuve que cela te fera gagner des vues : seul TON historique le dira (voir §4).

## 2. Présentateur qui parle sans te filmer (à vérifier sur les pages officielles avant d'acheter)
Sources divergentes sur les prix/API (veed.io, guptadeepak.com, dev.to, morphed.app, pikvue.com) :
| Outil | Ce que disent les sources | Intégré ? |
|---|---|---|
| D-ID | le moins cher pour démarrer, API à l'usage | oui, mode `did` (**jamais testé contre le vrai service**) |
| HeyGen | abordable ; accès API flou selon les sources | non (mode `clip` : tu génères la vidéo chez eux, le programme la monte) |
| Synthesia | API réservée aux contrats entreprise (selon une source) | non |
| Hedra | meilleure synchro labiale citée ; tarifs API non confirmés | non (mode `clip`) |
Mode `clip` (marche aujourd'hui, testé avec un faux présentateur) : tu mets des `.mp4` de présentateur dans `brand/avatar/`,
le programme les découpe, alterne présentateur / images du bien, ajoute sous-titres, barre de progression, musique.

## 3. Connecteurs trouvés dans le registre Claude (NON connectés à ton compte)
Je ne peux pas les connecter moi-même ; il faut les ajouter dans les réglages de connecteurs de claude.ai :
- **HyperFrames by HeyGen** (animations HTML → vidéo), **Orshot** (vidéos/images depuis modèles + publication sociale),
  **Metricool** (planification de posts + statistiques), **vidIQ** (tendances YouTube/Instagram/TikTok), **Cloudinary** (hébergement médias,
  utile pour Instagram qui exige des URL publiques). Je ne les ai pas essayés : leur qualité réelle est inconnue.
- **Canva** est déjà connecté chez toi, mais l'outil dont je dispose génère des visuels, pas des reels animés.

## 4. Savoir « par nous-mêmes » ce qui marche : la boucle d'apprentissage
Personne ne peut te dire à l'avance ce qui marche **pour toi, dans ta ville**. Le programme apprend de tes vraies stats :
exporte les chiffres de tes posts dans `out/metrics.csv` (id, vues, likes, commentaires, enregistrements, partages) puis `python -m immo learn`.
À partir de 3 posts par format et par réseau, le planning privilégie le format qui a le meilleur score (enregistrements/partages pèsent plus que les likes).
Testé avec des données fictives ; **jamais avec de vraies statistiques**.
