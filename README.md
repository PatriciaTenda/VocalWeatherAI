# VocalWeatherAI
Ce projet vise à mettre en place une fonctionnalité qui améliorera l'expérience utilisateur concernant le besoin d'obtenir les informations météorologiques vocalement, sans avoir besoin de saisir un texte ou de faire une recherche sur internet via une application météo.

# Pour créer l'environnement 
    ==> python -m venv env

# Pour activer l'environnement
    ==>.\env\Scripts\activate


# Installation des packages à utiliser


# Pour voir les packages installés dans notre environnement
    ==>pip freeze

# Créer un fichier requirements.txt qui va lister tous les packages installés dans notre environnement
    ==>pip freeze > requirements.txt    

# installation de la librairie python azure-cognitiveservices-speech
    ==> pip install azure-cognitiveservices-speech

# Installer FastAPI et Uvicorn
    ==> pip install fastapi unvicorn

# Pour utiliser la commande fastapi run il faut installer au préalable la commande 
    ==> pip install "fastapi[standard]"

# Pour lancer le serveur 
    ==>  uvicorn app.backend.main:app --reload

# Installation d el a librairie spaCy  et le modèle français pour le traitement automatique du langage naturel(NLP) pour la recuperation de la localisation dans le service NLP:
    ==> pip install spacy
    ==> python -m spacy download fr_core_news_sm
    ==> python -m spacy download fr_core_news_md
    ==> python -m spacy download fr_core_news_lg
    ==> python -m spacy download xx_ent_wiki_sm


# librairie dateparser pour recuperer la date  dans le service NLP:
    ==> pip istall dateparser
# Hugging Face Transformers et le modèle nécessaire pour recuperer la date  dans le service NLP:
    ==> pip install transformers
    ==> pip install torch

# librairie necessaire pour l'utilisation de l'API open meteo pour configure le service meteo
    ==> pip install openmeteo-requests
    ==> pip install requests-cache retry-requests numpy pandas


# Installer le SDK Python
    ==> pip install -q -U google-generativeai