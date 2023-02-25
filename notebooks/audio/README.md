#Readme pour l'audio
## Installation
* .env
  * créer un fichier ".env" en local pour y placer le chemin vers la vidéo, comme dans .env.example
* poetry update / poetry install
* poetry run python .\gender_identification.py
* ffmpeg codex (pour Windows, suivre les instructions [ici](https://www.geeksforgeeks.org/how-to-install-ffmpeg-on-windows/) -
pas besoin de mettre à la racine en admin et de redémarrer ;
pour ubuntu `$ sudo apt-get install ffmpeg`, voir la [doc du projet](https://github.com/ina-foss/inaSpeechSegmenter))

* Pour installer `spleeter` de Deezer, la version de NumPy doit être entre 1.16.0 et 1.19.5.
Ce qui implique de changer également la version de tensorflow. Pour éviter de faire imploser les dépendances, il faut créer un environnement virtuel.
  * Installez virtualenv par votre moyen préféré
  * Créez un environnement virtuel dans le dossier "audio" en lançant `virtualenv venv` (ici, il s'appelle venv)
  * Activez venv avec les commandes suivantes :
    * Linux : `source venv/bin/activate`
    * Windows : (`set-executionpolicy unrestricted` si besoin) `.\venv\Scripts\activate`
  * Installez les bilbiothèques indiquées dans le requirement.txt
  * Exécutez normalement le code python
  * Quittez venv avec `deactivate`
