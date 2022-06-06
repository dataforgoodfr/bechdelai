#Readme pour l'audio
## Installation
* .env
  * créer un fichier ".env" en local pour y placer le chemin vers la vidéo, comme dans .env.example
* poetry update / poetry install
* poetry run python .\gender_identification.py
* ffmpeg codex (pour Windows, suivre les instructions [ici](https://www.geeksforgeeks.org/how-to-install-ffmpeg-on-windows/) -
pas besoin de mettre à la racine en admin et de redémarrer ;
pour ubuntu `$ sudo apt-get install ffmpeg`, voir la [doc du projet](https://github.com/ina-foss/inaSpeechSegmenter))
