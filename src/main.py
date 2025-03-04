from flask import Flask, request, jsonify, render_template, session
from services.STT import recognize_from_microphone
from services.meteo import get_weather
from services.geolocalisation import get_coordinates
#from services.NLP import get_location_and_date
from modules.dates import dates_and_time_recodnition
from modules.localisations import find_loc_in_text, geopy_lati_longi
from dotenv import load_dotenv
import os
from datetime import datetime
import requests
import json
import secrets
import pandas as pd
import numpy as np


class Session :
    def __init__(self, objet = ""):
        self.object = object
    
sessionobj = Session()   

secret_key = secrets.token_hex(16)  # Génère une clé de 32 caractères hexadécimaux
print(secret_key)
print("Vous êtes bien sur le main")

#Charger les variables d'nevironnement
load_dotenv()

SPEECH_KEY = os.getenv('SPEECH_KEY')
SPEECH_REGION = os.getenv('SPEECH_REGION')

#créez une instance de Flask
app = Flask(__name__)

#Charger la variable d'nevironnement
app.secret_key = os.environ.get('FLASK_SECRET_KEY')


def get_weather_image(weather_code):
    if weather_code == 'Ciel clair':
        return 'sun.png'
    elif weather_code == 'Nuageux':
        return 'cloudy-icon.png'
    elif weather_code == 'Pluie légère':
        return 'rain.png'
    else:
        return 'default.png' # Image par défaut si le code n'est pas reconnu


# Fonction auxiliaire pour obtenir les coordonnées sous forme de dict
def get_coordinates(city):
    try:
        coords = geopy_lati_longi(city)
        if coords is None:
            print(f"[ERROR] geopy_lati_longi a renvoyé None pour la ville: {city}")
            return None
        print(f"[DEBUG] Coordonnées obtenues pour {city} : {coords}")
        return {"latitude": coords[0], "longitude": coords[1]}
    except Exception as e:
        print(f"[ERROR] Exception dans get_coordinates pour {city} : {e}")
        return None

# Route du home page
@app.route('/', methods=['GET'])
def home():
    weather_results = session.get('weather_results')
    return render_template('home.html', nom_app="Vocal Weather", weather_results=weather_results)

# Route Post pour les données meterologiques
@app.route('/weather', methods=['POST'])
def analyse_weather():
    """
    Route pour récupérer la commande vocale et obtenir la météo.
    """
    # 1. Reconnaissance vocale
    text = recognize_from_microphone()
    print(f"[DEBUG] Texte reconnu: {text}")
    if not text:
        return jsonify({"error": "Impossible de reconnaître la voix"}), 400

    # 2. Extraction de la date
    date_obj = dates_and_time_recodnition(text)
    print(f"[DEBUG] Date extraite: {date_obj}")
    if date_obj is None:
        return jsonify({"error": "Aucune date détectée"}), 400

    # 3. Extraction des localisations
    localisations = find_loc_in_text(text)
    print(f"[DEBUG] Localisations extraites: {localisations}")
    if not localisations:
        return jsonify({"error": "Aucune ville détectée"}), 400

    # Préparation du parsed_text pour le log (optionnel)
    parsed_text = {"dates": [date_obj], "localisations": localisations}
    print(f"[DEBUG] Parsed text: {parsed_text}")

    # 4. Conversion de la date en string (format dd/mm/yyyy)
    date_str = date_obj.strftime("%d/%m/%Y")
    print(f"[DEBUG] Date formatée: {date_str}")

    weather_results = []

    # 5. Pour chaque ville détectée, obtenir les coordonnées et la météo
    for city in localisations:
        coords = get_coordinates(city)
        if not coords:
            return jsonify({"error": f"Impossible de trouver les coordonnées de {city}"}), 400

        try:
            weather_data = get_weather(coords["latitude"], coords["longitude"], date_str)
            print(f"[DEBUG] Données météo pour {city} : {weather_data}")
        except requests.exceptions.RequestException as e:
            return jsonify({"error": f"Erreur lors de la récupération des données météo: {e}"}), 500
        except Exception as e:
            return jsonify({"error": f"Une erreur inattendue s'est produite: {e}"}), 500

        # Vérifier que weather_data contient bien "daily_forecast"
        if not isinstance(weather_data, dict) or "daily_forecast" not in weather_data:
            return jsonify({"error": "Structure de données météo invalide"}), 500

        # Extraction des prévisions depuis le DataFrame
        daily_df = weather_data["daily_forecast"]
        previsions_list = []

        if hasattr(daily_df, "iterrows"):
            if daily_df.empty:
                previsions_list.append({"date": date_str, "disponible": False})
            else:
                for _, row in daily_df.iterrows():
                    # Formatage de la date
                    if hasattr(row["date"], "strftime"):
                        date_str_row = row["date"].strftime("%d/%m/%Y %H:%M")
                    else:
                        date_str_row = str(row["date"])
                    
                    # Gestion des températures : conversion si nécessaire
                    temp_max = row["temperature_2m_max"]
                    temp_min = row["temperature_2m_min"]
                    if isinstance(temp_max, np.float32):
                        temp_max = float(temp_max)
                    if isinstance(temp_min, np.float32):
                        temp_min = float(temp_min)
                    
                    prevision = {
                        "date": date_str_row,
                        "weather_code": row["weather_code"],
                        "temperature_2m_max": temp_max if temp_max is not None else "Données non disponibles",
                        "temperature_2m_min": temp_min if temp_min is not None else "Données non disponibles",
                        "disponible": True
                    }
                    previsions_list.append(prevision)
        else:
            print(f"[ERROR] daily_forecast n'est pas un DataFrame pour {city}")
            previsions_list.append({"date": date_str, "disponible": False})

        weather_result = {
            "ville": city,
            "latitude": coords["latitude"],
            "longitude": coords["longitude"],
            "demande_date": date_str,
            "météo": previsions_list
        }
        weather_results.append(weather_result)
        print(f"[DEBUG] Résultat météo pour {city}: {weather_result}")

    # 6. Stocker les résultats dans la session pour réutilisation éventuelle
    session['weather_results'] = weather_results
    print(f"[DEBUG] Résultats météo globaux: {weather_results}")
    return jsonify({"résultats": weather_results}), 200

@app.route('/previsions', methods=['GET'])
def previsions():
    weather_results = session.get('weather_results')
    print("[DEBUG] Weather results in session:", weather_results)
    if weather_results:
        forecasts = prepare_forecasts(weather_results)
        return render_template('daily_previsions.html', forecasts=forecasts)
    else:
        return jsonify({"error": "Aucune prévision disponible"}), 404

def prepare_forecasts(weather_results):
    forecasts = []
    if isinstance(weather_results, dict):
        if 'météo' in weather_results:
            for prevision in weather_results['météo']:
                forecasts.append(prevision)
    elif isinstance(weather_results, list):
        for result in weather_results:
            if 'météo' in result:
                for prevision in result['météo']:
                    forecasts.append(prevision)
    print(f"[DEBUG] Prévisions préparées: {forecasts}")
    return forecasts

@app.route('/test', methods=['GET'])
def test():
    """
    Route alternative pour récupérer la commande vocale, analyser date/ville,
    puis obtenir la météo via Open-Meteo.
    """
    text = recognize_from_microphone()
    print(f"[DEBUG] Texte reconnu dans /test : {text}")
    if not text:
        return jsonify({"error": "Impossible de reconnaître la voix"}), 400

    date_obj = dates_and_time_recodnition(text)
    print(f"[DEBUG] Date extraite dans /test : {date_obj}")
    if date_obj is None:
        return jsonify({"error": "Aucune date détectée"}), 400

    localisations = find_loc_in_text(text)
    print(f"[DEBUG] Localisations extraites dans /test : {localisations}")
    if not localisations:
        return jsonify({"error": "Aucune ville détectée"}), 400

    weather_results = []

    for city in localisations:
        try:
            coords = geopy_lati_longi(city)
            if coords is None:
                return jsonify({"error": f"Impossible de trouver les coordonnées de '{city}'"}), 400
            latitude, longitude = coords[0], coords[1]
            print(f"[DEBUG] Coordonnées pour {city} : lat={latitude}, lon={longitude}")
        except Exception as e:
            return jsonify({"error": f"Erreur lors de la géolocalisation de {city}: {e}"}), 400

        date_str = date_obj.strftime("%d/%m/%Y")
        print(f"[DEBUG] Date formatée pour {city}: {date_str}")

        try:
            weather_data = get_weather(latitude, longitude, date_str)
            print(f"[DEBUG] Données météo pour {city} dans /test: {weather_data}")
        except Exception as e:
            return jsonify({"error": f"Erreur lors de la récupération des données météo: {e}"}), 500

        current_temp = weather_data.get("current_temperature")
        current_code = weather_data.get("current_weather_code")
        daily_df = weather_data.get("daily_forecast")

        previsions_list = []
        if hasattr(daily_df, "iterrows"):
            for _, row in daily_df.iterrows():
                if hasattr(row["date"], "strftime"):
                    date_str_row = row["date"].strftime("%d/%m/%Y %H:%M")
                else:
                    date_str_row = str(row["date"])
                temp_max = row["temperature_2m_max"]
                temp_min = row["temperature_2m_min"]
                if isinstance(temp_max, np.float32):
                    temp_max = float(temp_max)
                if isinstance(temp_min, np.float32):
                    temp_min = float(temp_min)
                previsions_list.append({
                    "date": date_str_row,
                    "weather_code": row["weather_code"],
                    "temperature_2m_max": temp_max if temp_max is not None else "Données non disponibles",
                    "temperature_2m_min": temp_min if temp_min is not None else "Données non disponibles",
                })
        else:
            previsions_list.append({"date": date_str, "disponible": False})

        result = {
            "ville": city,
            "latitude": latitude,
            "longitude": longitude,
            "demande_date": date_str,
            "current_temperature": current_temp,
            "current_weather_code": current_code,
            "previsions": previsions_list
        }
        weather_results.append(result)
        print(f"[DEBUG] Résultat pour {city} dans /test : {result}")

    return jsonify({"résultats": weather_results}), 200


 
if __name__ == "__main__": #Vérifie si le fichier est exécuté directement (et non importé dans un autre script)
   try:
    app.run(debug=True)  #if __name__ == "__main__" : Démarre le serveur Flask sur http://127.0.0.1:5000/.
                        #debug=True : Active le mode développeur (recharge automatique du serveur et affichage des erreurs détaillées).
   except KeyboardInterrupt:
        print("Serveur Flask interrompu par l'utilisateur.")