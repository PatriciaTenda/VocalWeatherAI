#importer les librairies 
import azure.cognitiveservices.speech as speechsdk  # Importe le SDK Azure Speech qui permet de faire la reconnaissance vocale.
import os  # Importe le module os, qui permet d’accéder aux variables d’environnement du système.
from dotenv import load_dotenv  # Importe load_dotenv, qui sert à charger les variables d’environnement stockées dans un fichier .env


"""  
    tester la reconnaissance vocale 

"""
 # Charge les variables d'environnement du fichier .env
 
load_dotenv() 
 
# Déclarer les variables qui vont contrenir la clé API et le service relatif à la région où on est localisée
#Récupération des clés API

SPEECH_KEY=os.getenv('SPEECH_KEY')  #Récupère la clé API stockée dans le fichier .env
SPEECH_REGION=os.getenv('SPEECH_REGION') #Récupère la région où est hébergé le service Azure

#Définition de la fonction de reconnaissance vocale                          
def recognize_from_microphone():
    
# Configuration du service de reconnaissance vocale
    # This instructions requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
    speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
    speech_config.speech_recognition_language="fr-FR"

    #Configure l’audio pour utiliser le micro par défaut de l’ordinateur.
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    
    # Création du reconnaisseur vocal
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    #Configure l’audio pour utiliser le micro par défaut de l’ordinateur.
    # Dès que l’utilisateur fait une pause, il arrête l’écoute et renvoie le texte reconnu.
    print("Parlez maintenant dans votre micro....")
    speech_recognition_result = speech_recognizer.recognize_once_async().get()
    
    #Vérifier si la reconnaissance a réussi
    if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:  #Vérifie si la reconnaissance a bien fonctionné. Si oui, on retourne le texte reconnu.
        print("Reconnu: {}".format(speech_recognition_result.text))  
        return"{}".format(speech_recognition_result.text)
    elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:   #Vérifie si aucune parole n’a été reconnue
        print("Aucune parole n'a été reconnue: {}".format(speech_recognition_result.no_match_details))  
    
    #Gérer les erreurs (ex : clé API incorrecte)    
    elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled: # Vérifie si la reconnaissance a été annulée à cause d’un problème
        cancellation_details = speech_recognition_result.cancellation_details
        print("Reconnaissance vocale annulée: {}".format(cancellation_details.reason)) #Affiche la raison de l’annulation 
        
        if cancellation_details.reason == speechsdk.CancellationReason.Error:   # Vérifie si la reconnaissance a été annulée à cause d’une erreur
            print("Détails de l'erreur: {}".format(cancellation_details.error_details))  #Affiche la raison de l’annulation 
            raise Exception("Erreur lors de la reconnaissance vocale : {}".format(cancellation_details.error_details))
            
recognize_from_microphone()
