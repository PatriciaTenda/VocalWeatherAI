import requests


def get_coordinates(city):
    """
    Récupère les coordonnées GPS d'une ville en utilisant l'API adresse.data.gouv.fr.
    
    Args:
        city (str): Le nom de la ville.
    
    Returns:
        dict: Un dictionnaire contenant la latitude et la longitude, ou None en cas d'erreur.
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
"""
# Exemple d'utilisation
if __name__ == "__main__":
    city = "Orléans"
    result = get_coordinates(city)
    if result:
        print(f"Coordonnées de {city} : {result}")
    else:
        print(f"Impossible de trouver les coordonnées de {city}")

  """     
"""
if __name__ == "__main__": #Vérifie si le fichier est exécuté directement (et non importé dans un autre script)
   city ='blois'
   print(get_coordinates(city))

"""