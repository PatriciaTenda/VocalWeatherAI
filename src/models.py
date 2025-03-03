from flask import Flask, request, jsonify
from services.STT import recognize_from_microphone
from services.meteo import get_weather
from services.geolocalisation import get_coordinates
from services.NLP import get_localisation_and_date_from_text
from dotenv import load_dotenv
import os
from datetime import datetime

print("Vous êtes bien sur le main")

load_dotenv()

SPEECH_KEY = os.getenv('SPEECH_KEY')
SPEECH_REGION = os.getenv('SPEECH_REGION')

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Bienvenue sur l'API Vocal Weather!"}), 200

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
    parsed_text = get_localisation_and_date_from_text(text)

    if not parsed_text or not parsed_text.get("localisations"):
        return jsonify({"error": "Aucune ville détectée"}), 400

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
            
            # Récupération de la météo
            weather = get_weather(coords["latitude"], coords["longitude"])
            if not weather:
                return jsonify({"error": f"Impossible de récupérer la météo pour {city} à la date {date}"}), 400

            print(f"Météo pour {city} le {date} : {weather}")

            # Ajout du résultat dans la liste
            weather_results.append({
                "ville": city,
                "latitude": coords["latitude"],
                "longitude": coords["longitude"],
                "date": date,
                "météo": weather
            })

    # Retourner toutes les prévisions météo détectées
    return jsonify({"résultats": weather_results}), 200

if __name__ == "__main__":
    app.run(debug=True)
