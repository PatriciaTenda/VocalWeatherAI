document.addEventListener('DOMContentLoaded', function() {
    const microphoneButton = document.getElementById('microphone-button');
    const recordingIndicator = document.getElementById('recording-indicator');
    const recognizedTextDiv = document.getElementById('recognized-text');
    const weatherInfoDiv = document.getElementById('weather-info');

    // J'utilise ici l'API SpeechRecognition du navigateur Chrome ou Safari pour faire une démo rapide
    // Dans votre application, vous devriez récupérer l'audio et utiliser un service d'IA de speech-to-text
    if ('webkitSpeechRecognition' in window) { // l'API SpeechRecognition est utilisée par les navigateurs basés sur WebKit comme Chrome et Safari
        const recognition = new webkitSpeechRecognition();
        recognition.lang = 'fr-FR'; // Définir la langue pour la reconnaissance vocale
        recognition.interimResults = false; // Ne pas afficher les résultats intermédiaires. Si 'interimResults' était 'true', l'API pourrait retourner des transcriptions partielles pendant que l'utilisateur parle encore

        microphoneButton.addEventListener('click', function() {
            recognition.start(); // Démarrer la reconnaissance vocale, le navigateur commence à écouter l'entrée audio du microphone
            recordingIndicator.style.display = 'block'; // Afficher l'indicateur d'enregistrement
            recognizedTextDiv.textContent = ''; // Effacer le texte transcrit précédemment
            weatherInfoDiv.style.display = 'none'; // Hide previous weather info when starting new request
        });

        recognition.onstart = function() { // L'événement 'onstart' est déclenché lorsque la reconnaissance vocale commence à écouter
            console.log("Reconnaissance vocale démarrée"); // Message de log dans la console du navigateur pour debug
        };

        recognition.onspeechstart = function() { // L'événement 'onspeechstart' est déclenché lorsque la parole est détectée
            console.log("Parole détectée");
        };

        recognition.onspeechend = function() { // L'événement 'onspeechend' est déclenché lorsque la parole cesse d'être détectée
            console.log("Fin de la parole détectée");
            recognition.stop(); // Arrêter la reconnaissance vocale après la fin de la parole
            recordingIndicator.style.display = 'none'; // Cacher l'indicateur d'enregistrement
        };

        recognition.onerror = function(event) { // L'événement 'onerror' est déclenché si une erreur se produit pendant le processus de reconnaissance vocale
            console.error("Erreur de reconnaissance vocale:", event.error);
            recordingIndicator.style.display = 'none';
            recognizedTextDiv.textContent = "Erreur de reconnaissance vocale. Veuillez réessayer."; // Afficher un message d'erreur dans l'élément 'recognizedTextDiv'
        };

        recognition.onresult = function(event) { // L'événement 'onresult' est déclenché lorsque le service de reconnaissance vocale retourne un résultat final (une transcription de la parole)
            const transcript = event.results[0][0].transcript; // Récupérer la transcription
            console.log("Texte reconnu:", transcript);
            recognizedTextDiv.textContent = "Texte reconnu: " + transcript; // Afficher le texte reconnu
            sendVoiceCommand(transcript); // Envoyer le texte reconnu
        };


    } else {
        alert("La reconnaissance vocale n'est pas prise en charge par votre navigateur. Veuillez utiliser Chrome ou Safari.");
        microphoneButton.disabled = true; // Désactiver le bouton si non supporté
    }

    function sendVoiceCommand(voiceCommand) {
        fetch('/weather', { // Envoyer une requête HTTP à l'endpoint '/weather'
            method: 'POST',
            headers: { // Les en-têtes de la requête HTTP
                'Content-Type': 'application/x-www-form-urlencoded', // Indique au serveur que le corps de la requête est formaté comme des données d'URL encodées (formulaire HTML standard)
            },
            body: 'voice_command=' + encodeURIComponent(voiceCommand) // Corps de la requête
            // 'encodeURIComponent(voiceCommand)' encode la 'voiceCommand' pour qu'elle puisse être correctement transmise dans une URL (gestion des caractères spéciaux, espaces, etc.).
        })
        .then(response => response.json()) // '.then()' est utilisé pour gérer la réponse du serveur une fois la requête réussie
        // 'response => response.json()' transforme le corps de la réponse HTTP (qui est initialement un flux de données) en un objet JSON
        .then(data => { // Ce deuxième '.then()' s'exécute une fois que la transformation en JSON (dans le '.then' précédent) est réussie, 'data' contient maintenant l'objet JSON
            console.log("Réponse reçue:", data);
            displayWeatherInfo(data);
        })
        .catch(error => { // Gérer les erreurs qui pourraient survenir pendant la requête 'fetch' (par exemple, erreur de réseau, serveur indisponible, etc.)
            console.error('Erreur lors de la requête:', error);
            alert('Erreur lors de la récupération des données météo.');
        });
    }

    function displayWeatherInfo(weatherData) { // Afficher les données météo reçues dans l'interface utilisateur
        document.getElementById('city-name').textContent = weatherData.city; // Modifier le contenu textuel de l'élément HTML ayant l'ID 'city-name'
        document.getElementById('condition').textContent = weatherData.condition;
        document.getElementById('temperature').textContent = weatherData.temperature;
        document.getElementById('forecast').textContent = weatherData.forecast;
        document.getElementById('weather-info').style.display = 'block'; // Afficher la section météo
        // Cela rend la section contenant les informations météo visible (elle est initialement cachée avec 'display: none;')
    }
});