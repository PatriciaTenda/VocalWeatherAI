from datetime import datetime, timedelta
import re
from dotenv import load_dotenv
import os
import google.generativeai as genai
import json

# Charger les variables d'environnement
load_dotenv()

# Récupérer la clé API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("Erreur: la clé API est absente du fichier .env")

# Configurer Gemini avec la clé API
genai.configure(api_key=GEMINI_API_KEY) 

# Créer un modèle Gemini
model = genai.GenerativeModel("gemini-1.5-pro-latest")

def get_location_and_date(text):
    today = datetime.today().strftime("%d/%m/%Y")
    tomorrow = (datetime.today() + timedelta(days=1)).strftime("%d/%m/%Y")
    in_two_weeks = (datetime.today() + timedelta(weeks=2)).strftime("%d/%m/%Y")

    prompt = f"""
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

    response = model.generate_content(prompt)
    #print("Réponse brute de Gemini :", response.text)  # Debug

    try:
        # Supprimer les ```json et ``` avec regex
        cleaned_response = re.sub(r"```(?:json)?|```", "", response.text).strip()
        return json.loads(cleaned_response)  # Convertir en JSON valide
    except json.JSONDecodeError:
        return {"error": "Réponse JSON invalide de Gemini"}

"""
if __name__ == "__main__":
    print(get_location_and_date("Quel temps fera-t-il à Reims dans le mois prochain ?"))
"""