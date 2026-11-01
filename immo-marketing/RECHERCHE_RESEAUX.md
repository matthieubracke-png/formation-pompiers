# Ce qui marche en immobilier sur Instagram, LinkedIn, Facebook — synthèse honnête (recherche du 2026-11-01)

**Limite principale** : je n'ai trouvé AUCUNE étude indépendante et contrôlée, et très peu de données françaises récentes.
Les sources sont des blogs d'agences, d'outils et de formations (qui vendent souvent le format qu'ils recommandent).
Les chiffres sont **indicatifs, non vérifiés**. Une source elle-même dit que comparer son compte à une « moyenne du secteur » n'a presque
pas de sens et qu'il faut suivre ses propres chiffres. D'où la boucle `python -m immo learn`, qui est la seule vraie réponse « pour toi ».

## Instagram
- **Reels courts** (accroche 1-3 s, < 15 s pour du B-roll, coupes rapides) ; visites guidées, avant/après home staging, points marché éclair.
  Sources : [nowbam](https://nowbam.com/3-reels-that-are-working-for-real-estate-agents-right-now/), [coffeecontracts](https://coffeecontracts.com/blog/instagram-reels-real-estate-agents), [ruche-pollen](https://ruche-pollen.com/blog-social-media/reseaux-sociaux-et-immobilier-generer-des-mandats-via-instagram-et-linkedin).
- **Accroche à « trou de curiosité »** + appel à **commenter un mot** pour recevoir les infos (capte des contacts).
- **Carrousels** : un benchmark publicitaire Meta les donne meilleurs que les Reels (4,1 % d'engagement) — **contradiction** avec les sources ci-dessus
  (métriques et contextes différents, publicité vs organique). Conclusion : produire les deux et mesurer.
- Ratio souvent cité : ~70 % contenu utile / 30 % promotion de biens ; les comptes « annonces uniquement » lassent. (Ratio de blogs, pas une règle de l'algorithme.)
- **Sujets** cités : analyse de quartier, questions d'acheteur (financement, négociation), décryptage fiscal/juridique, témoignages clients, coulisses.

## LinkedIn
- **Carrousel PDF** cité comme meilleur format organique (Inman ; chiffres Buffer relayés par des blogs, non vérifiés) : [Inman](https://www.inman.com/2026/07/06/latest-data-reveals-social-media-engagement/).
- **Posts texte** (histoire à la première personne, accroche, leçon finale) cités comme très efficaces et rapides à produire.
- **Vidéo** : citée en dessous des carrousels sur LinkedIn ; plutôt pour la voix/la démonstration.
- **Sujets** : éducation ultra-locale (coût de vie d'un quartier, rythme du marché local), pas les annonces seules.
- **Ce que fait le programme** : LinkedIn = carrousels + posts texte (nouveau format `texte`), pas de reels.
  Note : LinkedIn préfère un PDF pour les carrousels ; le programme sort des images (à assembler en PDF au besoin — pas automatisé).

## Facebook
- **Peu de données solides spécifiques**. Pistes : Reels de visite rapide, avant/après, points marché ; **titres « avantages/inconvénients de vivre à [ville] »,
  « meilleurs quartiers pour les familles »** (requêtes locales) ; **Reels dans les Groupes locaux** ; **Événements** pour portes ouvertes. Sources : [luxurypresence](https://www.luxurypresence.com/blogs/where-when-and-how-to-use-video-in-your-real-estate-business-2), [bigvu](https://bigvu.tv/blog/creator-decoder-top-realtors-get-views-2026-analyzed-10-accounts/).
- Les albums photo sont cités comme meilleur format Facebook dans le benchmark Meta (2,9 %).

## Ce que j'ai appliqué dans le programme (et ce que je n'ai PAS pu prouver)
Appliqué : 1re phrase = accroche ; coupes courtes ; sous-titres animés ; CTA « Commente INFO » ; 65 % biens / 35 % conseils (tu peux monter la part conseils dans `mix_biens`) ;
LinkedIn en carrousels + texte ; Instagram/Facebook en reels + carrousels.
Non fait / non prouvé : analyses de quartier (elles exigent des faits locaux fiables que je ne peux pas inventer : à fournir par toi) ; groupes et événements Facebook (aucune automatisation) ;
aucune preuve que ces choix te donneront plus de vues.
