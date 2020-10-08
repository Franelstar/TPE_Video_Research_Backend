# TPE Video Research Backend
Serveur de recherche de vidéo par le contenu. Ce serveur permet:
- De diviser une vidéo en scènes
- Pour chaque scène d'identifier le type de scène (Bedroom, Living romm, ...)
- Pour chaque scène d'identifier les objets qui s'y trouvent
- Pour chaque scène de compter le nombre de personnes qui s'y trouve et de les sauvegarder

Le serveur permet également de faire la recherche à partir des informations précédemment citées. L'application de recherche cliente est disponible via le lien https://github.com/Franelstar/TPE_Video_Research_Frontend

# Langage
Python

# Dépendances
- Tensorflow 2.3
- Flask
- psycopg2
- datetime
- time
- moviepy
- OpenCV
- Numpy
- face_recognition_models
- dlib
- face_recognition
- PILLOW
- matplotlib
- random
- scenedetect

# Base de données
Postgresql (Fichier de création disponible dans le dossier Base de données)

# Modèles
Les models utilisés pour la détection des scènes dont disponibles dans le dossier instances/models.
Il est possible que ces modèles soient mis à jour. Dans ce cas, les nouvelles versions seront disponibles via le lien https://drive.google.com/drive/folders/1JQSSLUoyUwyPcCDXVCDRbnefzdzeC__a?usp=sharing
