# VocalWeatherAI
Ce projet vise à mettre en place une fonctionnalité qui améliorera l'expérience utilisateur concernant le besoin d'obtenir les informations météorologiques vocalement, sans avoir besoin de saisir un texte ou de faire une recherche sur internet via une application météo.

# Pour créer l'environnement 
```bash
     python -m venv env


# Pour activer l'environnement

```bash
     .\env\Scripts\activate



# Installation des packages à utiliser

```bash

# Pour voir les packages installés dans notre environnement

```bash
     pip freeze


# Créer un fichier requirements.txt qui va lister tous les packages installés dans notre environnement

```bash
     pip freeze > requirements.txt    


# installation de la librairie python azure-cognitiveservices-speech

```bash
      pip install azure-cognitiveservices-speech


# Installer FastAPI et Uvicorn

```bash
     pip install fastapi unvicorn


# Pour utiliser la commande fastapi run il faut installer au préalable la commande 

```bash
     pip install "fastapi[standard]"


# Pour lancer le serveur 

```bash
      uvicorn app.backend.main:app --reload

# Installation d el a librairie spaCy  et le modèle français pour le traitement automatique du langage naturel(NLP) pour la recuperation de la localisation dans le service NLP

```bash
     pip install spacy
     python -m spacy download fr_core_news_sm
     python -m spacy download fr_core_news_md
     python -m spacy download fr_core_news_lg
     python -m spacy download xx_ent_wiki_sm


# librairie dateparser pour recuperer la date  dans le service NLP:

```bash 
    pip istall dateparser


# Hugging Face Transformers et le modèle nécessaire pour recuperer la date  dans le service NLP:

```bash
    pip install transformers
    pip install torch


# librairie necessaire pour l'utilisation de l'API open meteo pour configure le service meteo

```bash
     pip install openmeteo-requests
     pip install requests-cache retry-requests numpy pandas


# Installer le SDK Python Gemini pour le traitement du texte

```bash
    pip install -q -U google-generativeai


# Installer le SDK Python Open AI

```bash
     pip install openai

# Installer geopy pour recupérer la latitude et la longitude


```bash
    pip install geopy


# Commandes Git utiles

Voici comment fusionner une branche avec `main` :

```bash
git checkout main
git merge ma-branche
git push origin main

