import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
from datetime import datetime
import pytz

# Mapping des codes météo Open-Meteo en descriptions lisibles
WEATHER_CODE_MAP = {
    0: "Ciel clair",
    1: "Peu nuageux",
    2: "Partiellement nuageux",
    3: "Nuageux",
    45: "Brouillard",
    51: "Pluie légère",
    53: "Pluie modérée",
    55: "Pluie forte",
    61: "Averses de pluie légère",
    63: "Averses de pluie modérée",
    65: "Averses de pluie forte",
    80: "Averses orageuses",
    95: "Orage",
}

def get_weather(lat, lon, date):
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": ["temperature_2m", "weather_code"],
        "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min"],
        "timezone": "Europe/Paris",
        "models": "meteofrance_seamless"
    }
    
    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
    print(f"Elevation {response.Elevation()} m asl")
    print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
    print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")


    # Current values. The order of variables needs to be the same as requested.
    current = response.Current()

    current_temperature_2m = current.Variables(0).Value()

    current_weather_code = current.Variables(1).Value()

    print(f"Current time {current.Time()}")

    print(f"Current temperature_2m {current_temperature_2m}")
    print(f"Current weather_code {current_weather_code}")
    current_dict = {"temperature" : current_temperature_2m, "weather_code" : current_weather_code}   

    # Process daily data. The order of variables needs to be the same as requested.
    daily = response.Daily()
    daily_weather_code = daily.Variables(0).ValuesAsNumpy()
    daily_temperature_2m_max = daily.Variables(1).ValuesAsNumpy()
    daily_temperature_2m_min = daily.Variables(2).ValuesAsNumpy()

    daily_data = {"date": pd.date_range(
        start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
        end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = daily.Interval()),
        inclusive = "left"
    )}
    
      # Convertir les dates en fuseau horaire local
    if isinstance(daily_data["date"], pd.DatetimeIndex): #Vérification du type
        local_timezone = pytz.timezone("Europe/Paris")
        daily_data["date"] = daily_data["date"].tz_convert(local_timezone)
        daily_data["date"] = daily_data["date"].strftime('%d/%m/%Y %H:%M')
    else:
        print("La colonne 'date' n'est pas un DatetimeIndex valide.") #Ajout d'un log
        daily_data["date"] = ["Données non disponibles" for _ in range(len(daily_data["date"]))] #Remplacement par des données non disponibles.

    daily_data["weather_code"] = [WEATHER_CODE_MAP.get(code, "Données non disponibles") if pd.notna(code) else "Données non disponibles" for code in daily_weather_code]
    daily_data["temperature_2m_max"] = [temp if pd.notna(temp) else "Données non disponibles" for temp in daily_temperature_2m_max]
    daily_data["temperature_2m_min"] = [temp if pd.notna(temp) else "Données non disponibles" for temp in daily_temperature_2m_min]


    daily_dataframe = pd.DataFrame(data = daily_data)
    
    return {
        "current_temperature": current_temperature_2m,
        "current_weather_code": WEATHER_CODE_MAP.get(current_weather_code, "Données non disponibles"),
        "daily_forecast": daily_dataframe
    }

"""
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry


# Mapping des codes météo Open-Meteo en descriptions lisibles
WEATHER_CODE_MAP = {
    0: "Ciel clair",
    1: "Peu nuageux",
    2: "Partiellement nuageux",
    3: "Nuageux",
    45: "Brouillard",
    51: "Pluie légère",
    53: "Pluie modérée",
    55: "Pluie forte",
    61: "Averses de pluie légère",
    63: "Averses de pluie modérée",
    65: "Averses de pluie forte",
    80: "Averses orageuses",
    95: "Orage",
}
def get_weather(lat, lon): 
    
    #  Configuration de l'API avec cache et retry
    
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    # Requête pour recuper la prévision
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min"],
        "timezone": "auto",
        "forecast_hours": 7,
        "models": "meteofrance_seamless"
    }
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]
    
    # Vérifier que l'API retourne bien des prévisions
    if not response.Daily():
        return {"error": "Aucune donnée météo disponible"}
    
    # Récupérer les prévisions journalières
    print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
    print(f"Elevation {response.Elevation()} m asl")
    print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
    print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")


    # Current values. The order of variables needs to be the same as requested.
    current = response.Current()

    current_temperature_2m = current.Variables(0).Value()

    current_relative_humidity_2m = current.Variables(1).Value()

    current_is_day = current.Variables(2).Value()

    current_precipitation = current.Variables(3).Value()

    current_rain = current.Variables(4).Value()

    current_weather_code = current.Variables(5).Value()

    current_wind_speed_10m = current.Variables(6).Value()

    print(f"Current time {current.Time()}")

    print(f"Current temperature_2m {current_temperature_2m}")
    print(f"Current relative_humidity_2m {current_relative_humidity_2m}")
    print(f"Current is_day {current_is_day}")
    print(f"Current precipitation {current_precipitation}")
    print(f"Current rain {current_rain}")
    print(f"Current weather_code {current_weather_code}")
    print(f"Current wind_speed_10m {current_wind_speed_10m}")
    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
    hourly_relative_humidity_2m = hourly.Variables(1).ValuesAsNumpy()
    hourly_weather_code = hourly.Variables(2).ValuesAsNumpy()
    hourly_is_day = hourly.Variables(3).ValuesAsNumpy()

    hourly_data = {"date": pd.date_range(
        start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
        end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = hourly.Interval()),
        inclusive = "left"
    )}

    hourly_data["temperature_2m"] = hourly_temperature_2m
    hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m
    hourly_data["weather_code"] = hourly_weather_code
    hourly_data["is_day"] = hourly_is_day

    hourly_dataframe = pd.DataFrame(data = hourly_data)
    print(hourly_dataframe)

    # Process daily data. The order of variables needs to be the same as requested.
    daily = response.Daily()
    daily_weather_code = daily.Variables(0).ValuesAsNumpy()
    daily_temperature_2m_max = daily.Variables(1).ValuesAsNumpy()
    daily_temperature_2m_min = daily.Variables(2).ValuesAsNumpy()

    daily_data = {"date": pd.date_range(
        start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
        end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = daily.Interval()),
        inclusive = "left"
    )}

    daily_data["weather_code"] = daily_weather_code
    daily_data["temperature_2m_max"] = daily_temperature_2m_max
    daily_data["temperature_2m_min"] = daily_temperature_2m_min

    daily_dataframe = pd.DataFrame(data = daily_data)
    print(daily_dataframe)
   """
"""
if __name__ == "__main__": #Vérifie si le fichier est exécuté directement (et non importé dans un autre script)

    lon =  1.433805
    lat = 43.604082
    date = datetime.now().strftime("%d/%m/%Y") # Obtenir la date du jour au format "JJ/MM/AAAA"
    print(date)
    #ou date = "27/02/2025"
    print(get_weather(lat, lon, date))

"""

