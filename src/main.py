from flask import Flask, request, jsonify, render_template, session
from services.STT import recognize_from_microphone
from services.meteo import get_weather
from services.geolocalisation import get_coordinates
#from services.NLP import get_location_and_date
from modules.dates import dates_and_time_recodnition
from modules.localisations import find_loc_in_text
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


@app.route('/', methods=['GET'])
def home():
    weather_results = session.get('weather_results')
    return render_template('home.html', nom_app="Vocal Weather", weather_results=weather_results)

@app.route('/weather', methods=['POST'])
def analyse_weather():
    """
    Route pour récupérer la commande vocale et obtenir la météo.
    """
    text = recognize_from_microphone()
    
    if not text:
        return jsonify({"error": "Impossible de reconnaître la voix"}), 400

    print(f"Texte reconnu : {text}")

    # Extraction du lieu et des dates
    date_ = dates_and_time_recodnition(text)
    localisation_ = find_loc_in_text(text)
    parsed_text = {"dates" : [date_], "localisations" : localisation_}
    
    #verification que parse_text 
    print(f"Parsed text: {parsed_text}")
    # Ajoutez ces nouvelles lignes ici
    if not isinstance(parsed_text, dict):
        return jsonify({"error": "Erreur lors de l'analyse du texte"}), 400

    if not parsed_text or "localisations" not in parsed_text:
        return jsonify({"error": "Aucune ville détectée"}), 400

    # Le reste de votre code reste inchangé
    if not parsed_text.get("dates"):
        return jsonify({"error": "Aucune date détectée"}), 400
    
    cities = parsed_text["localisations"]  # Liste des villes détectées
    dates = parsed_text["dates"]  # Liste des dates détectées
    
    print(f"Villes détectées : {cities}")
    print(f"Dates détectées : {dates}")
    
    weather_results = []  # Liste pour stocker les résultats météo
    
    for city in cities:
        # Récupération des coordonnées GPS
        coords = get_coordinates(city)
        if not coords:
            return jsonify({"error": f"Impossible de trouver les coordonnées de {city}"}), 400

        print(f"Coordonnées pour {city} : {coords}")

        for date in dates:
            # Vérification que la date est bien dans un format valide
            try:
                parsed_date = datetime.strptime(date, "%d/%m/%Y")
               
            except ValueError:
                return jsonify({"error": f"Format de date invalide pour {date}"}), 400
            
            try:
                weather = get_weather(coords["longitude"], coords["latitude"], date)
            except requests.exceptions.RequestException as e:
                return jsonify({"error": f"Erreur lors de la récupération des données météo: {e}"}), 500
            except Exception as e:
                return jsonify({"error": f"Une erreur inattendue s'est produite: {e}"}), 500

            # Récupération de la météo
            weather = get_weather(coords["latitude"], coords["longitude"], date)
            
            if isinstance(weather, dict) and "error" in weather: #gestion des erreurs
                return jsonify(weather), 400
            if weather.empty:  # Vérification si le DataFrame est vide
                previsions = [{"date": date, "disponible": False}]  # Indiquer que les données sont manquantes
            else:
                previsions = []
                for index, row in weather.iterrows():
                    # Conversion des valeurs float32 en float
                    temperature_max = float(row["temperature_2m_max"]) if isinstance(row["temperature_2m_max"], np.float32) else row["temperature_2m_max"]
                    temperature_min = float(row["temperature_2m_min"]) if isinstance(row["temperature_2m_min"], np.float32) else row["temperature_2m_min"]

                    prevision = {
                        "date": row["date"],
                        "weather_code": row["weather_code"],
                        "temperature_2m_max": temperature_max,
                        "temperature_2m_min": temperature_min,
                        "disponible": True  # Indiquer que les données sont disponibles
                    }
                    previsions.append(prevision)
                    
            weather_results.append({
                "ville": city,
                "latitude": coords["latitude"],
                "longitude": coords["longitude"],
                "date": date,
                "météo": previsions  # Stocker les prévisions sous forme de liste de dictionnaires
            })
            print(weather_results)
    if weather_results:
        sessionobj.object = weather_results  # Stocker les résultats dans la session
        return jsonify({"résultats": weather_results, "previsions": weather_results}), 200
    else:
        return jsonify({"error": "Aucune donnée météo disponible"}), 404

def prepare_forecasts(weather_results):
    forecasts = []
    
    # Si c'est un dictionnaire unique
    if isinstance(weather_results, dict):
        if 'météo' in weather_results:
            for prevision in weather_results['météo']:
                forecasts.append(prevision)
    
    # Si c'est une liste de dictionnaires
    elif isinstance(weather_results, list):
        for result in weather_results:
            if 'météo' in result:
                for prevision in result['météo']:
                    forecasts.append(prevision)
    
    print(f"Voici forecasts: {forecasts}")
    return forecasts

@app.route('/previsions', methods=['GET'])
def previsions():
    weather_results = session.get('weather_results')
    print("#################")
    print(weather_results)
    if weather_results:
        forecasts = prepare_forecasts(weather_results)
        print(forecasts)
        return render_template('daily_previsions.html', forecasts=forecasts)
    else:
        return jsonify({"error": "Aucune prévision disponible"}), 404
    
    
@app.route('/test', methods=['GET'])
def test():
    """ 
    Route pour récupérer la commande vocale et obtenir la météo.
    """
    text = recognize_from_microphone()
    
    if not text:
        return jsonify({"error": "Impossible de reconnaître la voix"}), 400

    date_ = dates_and_time_recodnition(text)
    localisation_ = find_loc_in_text(text)
    parsed_text = {"dates" : [date_], "localisations" : localisation_}
    
    if not isinstance(parsed_text, dict):
        return jsonify({"error": "Erreur lors de l'analyse du texte"}), 400

    if "localisations" not in parsed_text or not parsed_text["localisations"]:
        return jsonify({"error": "Aucune ville détectée"}), 400

    if "dates" not in parsed_text or not parsed_text["dates"]:
        return jsonify({"error": "Aucune date détectée"}), 400

    cities = parsed_text["localisations"]
    dates = parsed_text["dates"]

    weather_results = []

    for city in cities:
        coords = get_coordinates(city)
        if not coords:
            return jsonify({"error": f"Impossible de trouver les coordonnées de {city}"}), 400

        for date in dates:
            if isinstance(date, datetime.datetime):  
                date = date.strftime("%d/%m/%Y")  # S'assurer que la date est bien une string
    
            try:
                parsed_date = datetime.strptime(date, "%d/%m/%Y")
            except ValueError:
                return jsonify({"error": f"Format de date invalide pour {date}"}), 400


            try:
                weather = get_weather(coords["latitude"], coords["longitude"], date)
            except requests.exceptions.RequestException as e:
                return jsonify({"error": f"Erreur lors de la récupération des données météo: {e}"}), 500
            except Exception as e:
                return jsonify({"error": f"Une erreur inattendue s'est produite: {e}"}), 500

            if "daily_forecast" not in weather or weather["daily_forecast"].empty:
                previsions = [{"date": date, "disponible": False}]
            else:
                previsions = []
                for _, row in weather["daily_forecast"].iterrows():
                    prevision = {
                        "date": row["date"].strftime('%d/%m/%Y'),
                        "weather_code": row["weather_code"],
                        "temperature_2m_max": float(row["temperature_2m_max"]),
                        "temperature_2m_min": float(row["temperature_2m_min"]),
                        "disponible": True
                    }
                    previsions.append(prevision)

            weather_results.append({
                "ville": city,
                "latitude": coords["latitude"],
                "longitude": coords["longitude"],
                "date": date,
                "current_temperature": weather["current_temperature"],
                "current_weather_code": weather["current_weather_code"],
                "previsions": previsions
            })

    if weather_results:
        return jsonify({"résultats": weather_results}), 200
    else:
        return jsonify({"error": "Aucune donnée météo disponible"}), 404
     
if __name__ == "__main__": #Vérifie si le fichier est exécuté directement (et non importé dans un autre script)
   try:
    app.run(debug=True)  #if __name__ == "__main__" : Démarre le serveur Flask sur http://127.0.0.1:5000/.
                        #debug=True : Active le mode développeur (recharge automatique du serveur et affichage des erreurs détaillées).
   except KeyboardInterrupt:
        print("Serveur Flask interrompu par l'utilisateur.")