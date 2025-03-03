from datetime import datetime, timedelta
import openai # Assure-toi d'importer ton client OpenAI correctement
from datetime import datetime, timedelta
import re
from dotenv import load_dotenv
import os



# Charger les variables d'environnement
load_dotenv()

# Récupérer la clé API
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("Erreur: la clé API est absente du fichier .env")



# Créer un modèle OPENAI_API
model="gpt-4o-mini"
# Définition des dates nécessaires
today = datetime.today().strftime("%d/%m/%Y")
tomorrow = (datetime.today() + timedelta(days=1)).strftime("%d/%m/%Y")
in_two_weeks = (datetime.today() + timedelta(weeks=2)).strftime("%d/%m/%Y")

# Texte à analyser
text = "Quel temps fera-t-il à Lyon dans 10 jours ?"
client = OpenAI()
# Création de la requête
completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": f"""
    Tu es un assistant météo qui doit extraire **avec précision** :
    - Les noms de villes, pays ou lieux.
    - Les dates mentionnées et les convertir **exactement** au format JJ/MM/AAAA.

        **IMPORTANT : Ne fais aucune approximation, utilise des dates exactes.**  
        N'invente pas de dates.  
        Ne donne pas plusieurs jours si ce n'est pas demandé.  

        **Règles pour la conversion des dates :**
    - **"aujourd’hui" → {today}**
    - **"demain" → {tomorrow}**
    - **"dans deux semaines" → {in_two_weeks}**  
    - **"dans X jours" → Ajoute X jours à aujourd’hui et donne une date exacte.**  
    - **"dans X semaines" → Ajoute X * 7 jours à aujourd’hui et donne une date exacte.**  

        **Exemples corrects :**
    - **Texte :** "Quel temps fera-t-il à Paris aujourd’hui ?"  
      **Réponse attendue :**
      {{
        "localisations": ["Paris"],
        "dates": ["{today}"]
      }}
    - **Texte :** "Quel temps fera-t-il à Reims dans deux semaines ?"  
      **Réponse attendue :**
      {{
        "localisations": ["Reims"],
        "dates": ["{in_two_weeks}"]
      }}
    - **Texte :** "Quel temps fera-t-il à Lyon dans 10 jours ?"  
      **Réponse attendue :**
      {{
        "localisations": ["Lyon"],
        "dates": ["{(datetime.today() + timedelta(days=10)).strftime("%d/%m/%Y")}"]
      }}

      **Texte à analyser :**
    {text}

    **Réponds uniquement en JSON valide**, sans texte supplémentaire.
    """
        }
    ]
)

print(completion.choices[0].message)

"""
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
from datetime import datetime
import pytz  # Importation de pytz pour la gestion des fuseaux horaires

#  Mapping des codes météo Open-Meteo en descriptions lisibles
WEATHER_CODE_MAP = {
    0: "Ciel clair",
    1: "Peu nuageux",
    2: "Partiellement nuageux",
    3: "Nuageux",
    45: "Brouillard",
    51: "Pluie légère",
    53: "Pluie modérée",
    55: "Pluie forte",
    61: "Averses de pluie légère",
    63: "Averses de pluie modérée",
    65: "Averses de pluie forte",
    80: "Averses orageuses",
    95: "Orage",
}

def get_weather(lat, lon, date):
    #  Configuration de l'API avec cache et retry
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    #  Requête pour récupérer les prévisions météo
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min"],
        "timezone": "auto",
        "forecast_days": 7  # Récupérer les prévisions sur 7 jours
    }

    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]

    # Ajout de logs pour afficher la réponse brute de l'API
    print("Réponse brute de l'API :", response)

    # Vérifier que l'API retourne bien des prévisions
    if not response.Daily():
        return {"error": "Aucune donnée météo disponible"}

    # Récupérer les prévisions journalières
    daily = response.Daily()
    daily_dates = pd.date_range(
        start=pd.to_datetime(daily.Time(), unit="s", utc=True),
        periods=len(daily.Variables(0).ValuesAsNumpy()),
        freq="D"
    ).strftime("%d/%m/%Y").tolist()

    daily_weather_code = daily.Variables(0).ValuesAsNumpy()
    daily_temperature_max = daily.Variables(1).ValuesAsNumpy()
    daily_temperature_min = daily.Variables(2).ValuesAsNumpy()

    # Ajout de logs pour afficher les données traitées
    print("Dates :", daily_dates)
    print("Codes météo :", daily_weather_code)
    print("Températures max :", daily_temperature_max)
    print("Températures min :", daily_temperature_min)

    # Création d'un dictionnaire avec les prévisions météo par date
    weather_data = {
        daily_dates[i]: {
            "température_max": round(float(daily_temperature_max[i]), 1) if not pd.isna(daily_temperature_max[i]) else None,
            "température_min": round(float(daily_temperature_min[i]), 1) if not pd.isna(daily_temperature_min[i]) else None,
            "condition": WEATHER_CODE_MAP.get(int(daily_weather_code[i]), "Inconnu") if not pd.isna(daily_weather_code[i]) else "Donnée manquante"
        }
        for i in range(len(daily_dates))
    }

    # Vérifier si la date demandée est disponible dans les prévisions
    if date in weather_data:
        return weather_data[date]
    else:
        return {"error": f"Aucune prévision disponible pour {date}"}

if __name__ == "__main__":
    lon = 1.911358
    lat = 47.873569
    date = datetime.now().strftime("%d/%m/%Y")
    print(get_weather(lat, lon, date))

"""

"""# # Import des librairies

import dateparser
from transformers import CamembertTokenizer, AutoModelForTokenClassification, pipeline



# Chargement du tokenizer et du modèle de hugging face
tokenizer = CamembertTokenizer.from_pretrained("Jean-Baptiste/camembert-ner-with-dates")
model = AutoModelForTokenClassification.from_pretrained("Jean-Baptiste/camembert-ner-with-dates")


# Création de la pipeline de ner pour le modèle
nlp = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple")
    
def get_localisation_and_date_from_text(text):#Charge le modèle ne français

    # Extraction des entités
    entities = nlp(text)
    
    # Récupération des dates et localisations dans les entités (et parsing des dates)
    dates = [] 
    localisations = []

    for entite in entities:
        if entite["entity_group"] == "DATE":
            date_obj = dateparser.parse(entite["word"], languages=["fr"])
            if date_obj:  # Vérification que la date est bien reconnue
                dates.append(date_obj.strftime("%d/%m/%Y"))  # Stocke toutes les dates
       
        elif entite["entity_group"] == "LOC":
            localisations.append(entite["word"])
  
   # Retourner un dictionnaire (ou un objet si besoin)
    return {"dates": dates, "localisations": localisations}
"""
"""
import requests
import json

def get_coordinates(city):
    """
"""
    Récupère les coordonnées GPS d'une ville en utilisant l'API adresse.data.gouv.fr.
    
    Args:
        city (str): Le nom de la ville.
    
    Returns:
        dict: Un dictionnaire contenant la latitude et la longitude, ou None en cas d'erreur.
    """
"""
    url = f"https://api-adresse.data.gouv.fr/search/?q={city}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Lève une exception pour les codes d'erreur HTTP
        
        data = response.json()
        if data["features"]:
            coordinates = data["features"][0]["geometry"]["coordinates"]
            return {"longitude": coordinates[0], "latitude": coordinates[1]}
        else:
            print(f"Aucun résultat trouvé pour {city}")
            return None
    except requests.RequestException as e:
        print(f"Erreur lors de la requête : {e}")
        return None
    except (KeyError, IndexError) as e:
        print(f"Erreur dans le traitement des données : {e}")
        return None

# Exemple d'utilisation
if __name__ == "__main__":
    city = "Orléans"
    result = get_coordinates(city)
    if result:
        print(f"Coordonnées de {city} : {result}")
    else:
        print(f"Impossible de trouver les coordonnées de {city}")
        
        
"""