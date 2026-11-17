# Bibliothèque musicale Rawi (Pixabay Music)

31 morceaux téléchargés depuis Pixabay Music le 17 nov. 2026 (licence Pixabay Content License : usage commercial autorisé, sans crédit obligatoire, sur YouTube, Meta, TikTok).

- Ambiances : tension, enquete, epique, emotion, tech, espace, archive, mystere (4 morceaux chacune, sauf tech : 3).
- `index.json` : nom, auteur, durée, lien Pixabay (`href`) et **certificat de licence / Content ID** (`cert`, à préfixer par https://pixabay.com). Les morceaux Pixabay sont enregistrés dans le Content ID de YouTube : en cas de réclamation, la contester avec ce certificat.
- Utilisation : `python3 tools/mix.py VIDEO VOICE.wav OUT.mp4 --mood tension [--sfx sfx.wav] [--lead 0.6]` → tapis musical continu (boucle en fondu enchaîné), ducking sidechain sous la voix, fondus, −14 LUFS / −1 dBTP.
