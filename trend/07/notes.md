## Ép. 7 — « الذهب والبيتكوين يسقطان معًا… » — programmé le 18 nov. 2026
- Sujet : l'or est au plus bas depuis oct. 2025 (~3 865 $, après plus de 5 600 $ en janv. 2026). Le Bitcoin est vers 64 000 $ (contre ~126 000 $ en oct. 2025). Les ETF ont perdu 2,1 Mds $ en novembre et l'indice Fear & Greed est à 10. Cause : tout à la fois un tableau d'inflation US, des paris sur une hausse des taux et un dollar fort, avec des taux à 10 ans proches de 5 %. Mention « explication, pas un conseil ». Nvidia est annoncé pour la vidéo suivante (ép. 8, après les résultats officiels du 17 nov. à 21:20).
- YouTube https://youtu.be/fsxYBLvo23E (2:04) programmé le **18 nov. à 10:00** (sous-titres AR publiés, label IA, playlist ترند) ; Short https://youtube.com/shorts/QXG6G8uIHjQ le **19 nov. à 10:00** ; reel Meta FB+IG le **18 nov. à 11:00**.
- **Premier épisode avec le nouveau module `tools/agfx.py`** (graphismes animés et bruitages) :
  - les cartes tombent ou glissent avec un rebond et une ombre, les compteurs de prix défilent, le calendrier apparaît ;
  - jauge Fear & Greed animée, chaîne cause → effet révélée étape par étape sur la voix, tampons ;
  - bruitages synthétisés en numpy (papier, page tournée, tampon, whoosh, tic) mixés sur une piste à part.
  - Scènes dans `trend/07/scenes.py` ; part des graphismes : 38 %.
- Leçons :
  - Un clip vidéo complet de plus de 300 Mo (Commons, original sans dérivée) ou un tar de plus de 400 Mo bloque le transfert → ne télécharger que les petites dérivées.
  - Dans `bt7.py`, le cache des plans réutilise l'ancien rendu des scènes `a` → toujours relancer avec `REDO=` sur les indices `a` après une modification de `scenes.py`.
  - Une scène graphique ne doit jamais être vide au début : afficher un titre dès 0,05 s.
  - YouTube : à la 1re importation des sous-titres pendant le traitement de la vidéo, l'éditeur affichait les sous-titres automatiques → réimporter, vérifier le texte (avec diacritiques) dans l'éditeur, puis cliquer « Publier ».

