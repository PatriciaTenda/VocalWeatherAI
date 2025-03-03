document.addEventListener('DOMContentLoaded', function() {
    // Sélection des éléments HTML
    const dateHeader = document.querySelector('.header time');
    const microButton = document.querySelector('.middle-section .micro-button');
    const cityElement = document.getElementById('city-name');
    const temperatureElement = document.getElementById('temperature');
    const descriptionElement = document.getElementById('description');
    const feltTemperatureElement = document.getElementById('felt-temperature');
    const forecastMessageElement = document.getElementById('forecast-message');
    const accueilLink = document.querySelector('.footer a[href="/"]');
    const meteoActuelleLink = document.querySelector('.footer a[href="#middle-section"]'); // Lien vers la section "Middle Section"
    const previsionsLink = document.querySelector('.footer a[href="/previsions"]');
    const contactLink = document.querySelector('.footer a[href="/contact"]');
    const parametresLink = document.querySelector('.footer a[href="/parametres"]');

    // Données météo (à remplacer par des données dynamiques)
    const weatherData = {
        city: 'Bayonne',
        temperature: 2,
        description: 'Globalement nuageux',
        feltTemperature: -7,
        forecastMessage: 'Le ciel sera partiellement nuageux. La température minimale sera de 0°.'
    };

    // Fonction pour mettre à jour l'affichage
    function updateDisplay(data) {
        cityElement.textContent = data.city;
        temperatureElement.textContent = `${data.temperature}°C`;
        descriptionElement.textContent = data.description;
        feltTemperatureElement.textContent = `Ressenti: ${data.feltTemperature}°C`;
        forecastMessageElement.textContent = data.forecastMessage;
    }

    // Affichage initial
    updateDisplay(weatherData);

    // Gestionnaire d'événement pour le micro
    microButton.addEventListener('click', function() {
        console.log('Micro activé');
        // Ajouter ici la logique pour la saisie vocale
        startSpeechRecognition();
        document.getElementById('micro-button').addEventListener('click', function() {
            fetch('/weather', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.résultats) {
                    // Afficher les résultats météo
                    afficherResultatsMeteo(data.résultats);
        
                    // Rediriger vers /previsions avec les données de prévisions
                    window.location.href = '/previsions?data=' + encodeURIComponent(JSON.stringify(data.previsions));
                } else if (data.error) {
                    alert(data.error);
                }
            });
        });
        
        function afficherResultatsMeteo(resultats) {
            // Supposons que nous avons un élément HTML avec l'ID 'weather-info' où vous voulez afficher les résultats
            const weatherInfoDiv = document.querySelector('.weather-info');
            weatherInfoDiv.innerHTML = ''; // Effacer le contenu précédent
        
            resultats.forEach(resultat => {
                const ville = resultat.ville;
                const latitude = resultat.latitude;
                const longitude = resultat.longitude;
                const date = resultat.date;
                const meteo = resultat.météo[0]; // Supposons que vous voulez afficher la première entrée météo
        
                const villeElement = document.createElement('h2');
                villeElement.textContent = ville;
        
                const temperatureElement = document.createElement('h4');
                temperatureElement.textContent = `Température: ${meteo.temperature_2m}°C`;
        
                const conditionsElement = document.createElement('h4');
                conditionsElement.textContent = `Conditions: ${meteo.weather_code}`;
        
                weatherInfoDiv.appendChild(villeElement);
                weatherInfoDiv.appendChild(temperatureElement);
                weatherInfoDiv.appendChild(conditionsElement);
            });
        }

    // Gestionnaires d'événements pour les liens du footer
    accueilLink.addEventListener('click', function(event) {
        event.preventDefault();
        console.log('Accueil cliqué');
        // Recharger la page d'accueil ou ne rien faire
        if (window.location.pathname !== '/') {
            window.location.href = '/';
        }
    });

    meteoActuelleLink.addEventListener('click', function(event) {
        event.preventDefault();
        console.log('Météo actuelle cliqué');
        // Faire défiler jusqu'à la section "Middle Section"
        const middleSection = document.querySelector('.middle-section');
        if (middleSection) {
            middleSection.scrollIntoView({ behavior: 'smooth' });
        }
    });

    previsionsLink.addEventListener('click', function(event) {
        event.preventDefault();
        console.log('Prévisions cliqué');
        // Rediriger vers la page de prévisions
        window.location.href = '/previsions';
    });

    contactLink.addEventListener('click', function(event) {
        event.preventDefault();
        console.log('Nous contacter cliqué');
        // Rediriger vers la page de contact
        window.location.href = '/contact';
    });

    parametresLink.addEventListener('click', function(event) {
        event.preventDefault();
        console.log('Paramètres cliqué');
        // Rediriger vers la page de paramètres
        window.location.href = '/parametres';
    });

    // Fonction pour mettre à jour la date dans le header
    function updateDateHeader() {
        const now = new Date();
        const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
        const formattedDate = now.toLocaleDateString('fr-FR', options);
        dateHeader.textContent = formattedDate;
    }

    // Mettre à jour la date au chargement de la page
    updateDateHeader();

    // Fonction pour démarrer la reconnaissance vocale (à implémenter)
    function startSpeechRecognition() {
        // Ajouter ici la logique pour la reconnaissance vocale
        if ('webkitSpeechRecognition' in window) {
            const recognition = new webkitSpeechRecognition();
            recognition.lang = 'fr-FR';
            recognition.onresult = function(event) {
                const transcript = event.results[0][0].transcript;
                console.log('Texte reconnu : ' + transcript);
                // Ajouter ici la logique pour traiter le texte reconnu
            };
            recognition.onerror = function(event) {
                console.error('Erreur de reconnaissance vocale : ', event.error);
            };
            recognition.start();
        } else {
            console.error('La reconnaissance vocale n\'est pas supportée par ce navigateur.');
        }
    }
});
})