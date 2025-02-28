#from fastapi import FastAPI
from flask import Flask, request, jsonify
from services.STT import recognize_from_microphone
from services.meteo import get_weather
from services.geolocalisation import get_coordinates
from services.NLP import get_location_and_date
from dotenv import load_dotenv
import os
from datetime import datetime
import requests

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

    parsed_text = get_location_and_date(text)
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
            if weather.empty: # Vérification si le DataFrame est vide
                return jsonify({"error": f"Impossible de récupérer la météo pour {city} à la date {date}"}), 400
            print(f"Météo pour {city} le {date} : {weather}\n")

            # Ajout du résultat dans la liste
            weather_results.append({
                "ville": city,
                "latitude": coords["latitude"],
                "longitude": coords["longitude"],
                "date": date,
                "météo": weather.to_dict(orient='records') # Convertir le DataFrame en dictionnaire
            })

    # Retourner toutes les prévisions météo détectées
    return jsonify({"résultats": weather_results}), 200
 
if __name__ == "__main__": #Vérifie si le fichier est exécuté directement (et non importé dans un autre script)
   try:
    app.run(debug=True)  #if __name__ == "__main__" : Démarre le serveur Flask sur http://127.0.0.1:5000/.
                        #debug=True : Active le mode développeur (recharge automatique du serveur et affichage des erreurs détaillées).
   except KeyboardInterrupt:
        print("Serveur Flask interrompu par l'utilisateur.")