import re
import dateparser
import datetime

def main():
    dates_and_time_recodnition()

def dates_and_time_recodnition(text):

    """
    Détecte et extrait une seule date pertinente :
    - Fusionne les dates et heures trouvées ensemble.
    - Sélectionne la date la plus ancienne.
    - Associe la plus vieille heure détectée à la date la plus vieille.
    - Si seule une heure est trouvée, elle est associée à aujourd'hui.
    """

    pattern = r"""
        \b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2})\b |  # Formats classiques : 10/02/2024, 2024-05-10
        \b(?:\d{1,2}\s?h\s?(?:\d{2})?)\b |  # Heures : 10h, 14:30, 18h00, 19 h
        \b(?:demain|après-demain|hier|aujourd'hui|minuit|midi)\b |  # Expressions directes
        \b(?:dans|il y a)\s\d+\s(?:jours?|semaines?|mois?|années?)\b |  # Relatif : dans 3 jours, il y a 2 semaines
        \b(?:lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche)\b |  # Jours de la semaine
        \b(?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\b  # Mois
    """

    # Extraction des expressions temporelles avec regex
    matches = re.findall(pattern, text, re.IGNORECASE | re.VERBOSE)

    # Nettoyage des résultats
    extracted_dates = [match.strip() for match in matches if match.strip()]

    if not extracted_dates:
        return None  # Aucune date trouvée

    # Normaliser les heures : "19 h" -> "19h00"
    def normalize_hour(hour_text):
        hour_text = hour_text.replace(" ", "")  # Supprimer les espaces
        if re.match(r"^\d{1,2}h$", hour_text):  # Ex: "18h" → "18h00"
            return hour_text + "00"
        elif re.match(r"^\d{1,2}$", hour_text):  # Ex: "18" → "18h00"
            return hour_text + "h00"
        return hour_text

    hours = [normalize_hour(d) for d in extracted_dates if re.match(r"\b\d{1,2}\s?h\s?(?:\d{2})?\b", d)]
    dates_only = [d for d in extracted_dates if d not in hours]

    # Convertir toutes les dates en objets datetime
    parsed_dates = [
        dateparser.parse(date, settings={'PREFER_DATES_FROM': 'past', 'PREFER_DAY_OF_MONTH': 'first'})
        for date in dates_only
    ]

    # Supprimer les valeurs None et garder la date la plus ancienne
    parsed_dates = [d for d in parsed_dates if d is not None]
    oldest_date = min(parsed_dates) if parsed_dates else None

    # Convertir les heures en objets datetime
    parsed_hours = [
        dateparser.parse(hour, settings={'PREFER_DATES_FROM': 'past'})
        for hour in hours
    ]

    # Supprimer les valeurs None et garder l’heure la plus ancienne
    parsed_hours = [h for h in parsed_hours if h is not None]
    oldest_hour = min(parsed_hours, key=lambda h: h.time()) if parsed_hours else None

    # Cas où seule une heure est détectée → On l'associe à aujourd'hui
    if oldest_date is None and oldest_hour is not None:
        today = datetime.datetime.today()
        return datetime.datetime.combine(today.date(), oldest_hour.time())

    # Fusionner la plus vieille date avec la plus vieille heure
    if oldest_date and oldest_hour:
        return datetime.datetime.combine(oldest_date.date(), oldest_hour.time())
    elif oldest_date:
        return oldest_date
    else:
        return None





if __name__=="__main__":
    main()