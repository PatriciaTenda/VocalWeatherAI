document.addEventListener('DOMContentLoaded', function() {
    // Récupérer les données de prévisions à partir du tableau HTML
    const tableRows = document.querySelectorAll('.table tbody tr');
    const forecastData = [];

    tableRows.forEach(row => {
        const cells = row.querySelectorAll('td');
        forecastData.push({
            date: cells[0].textContent,
            weather_code: cells[1].textContent,
            image: row.querySelector('img').getAttribute('src'), // Récupérer le chemin de l'image
            temperature_2m_max: cells[3].textContent,
            temperature_2m_min: cells[4].textContent,
        });
    });

    // Maintenant, vous avez les données dans 'forecastData'
    console.log(forecastData); // Vous pouvez les utiliser pour d'autres traitements

    // Exemple : Ajouter une classe CSS aux lignes avec "Nuageux"
    forecastData.forEach((forecast, index) => {
        if (forecast.weather_code === 'Nuageux') {
            tableRows[index].classList.add('cloudy-row'); // Ajoute une classe CSS
        }
    });
});