import spacy
from geopy.geocoders import Nominatim


def main():
    find_loc_in_text()
    geopy_lati_longi()

def find_loc_in_text(text):
    

    nlp = spacy.load("fr_core_news_lg")

    text_ = text

    doc = nlp(text_)
    localistions = []
    for ent in doc.ents:
        if ent.label_ == "LOC":
            print(f"{ent.text} -> {ent.label_}")
            localistions.append(ent.text)
    return localistions

def geopy_lati_longi(city):


    geolocator = Nominatim(user_agent="vocal_wheather")
    location = geolocator.geocode(city)
    print(location.address)
    print((location.latitude, location.longitude))
    print(location.raw)
    geo_latitude = location.latitude
    geo_longitude = location.longitude
    return [geo_latitude, geo_longitude]

if __name__ == "__main__":
    main()