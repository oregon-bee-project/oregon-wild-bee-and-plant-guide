import zmq
import pandas as pd
import numpy as np
from collections import Counter

from geopy.geocoders import Nominatim
from geopy.exc import (
    GeocoderTimedOut,
    GeocoderServiceError,
    GeocoderUnavailable,
    GeocoderQueryError,
    GeocoderQuotaExceeded,
)

PORT = 5556
DATA_PATH = "../data/example_data.json" # change this for GitHub Pages

# Seraches internet to find matching County depending on Lat and Long
def get_county_from_coordinates(latitude, longitude):
    geolocator = Nominatim(user_agent="bee-data")

    try:
        location = geolocator.reverse((latitude, longitude), timeout=5)
    except (
        GeocoderTimedOut,
        GeocoderServiceError,
        GeocoderUnavailable,
        GeocoderQueryError,
        GeocoderQuotaExceeded):
        print("ERROR - geolocator.reverse()")
        return None
    except Exception:
        # Fallback for any unexpected geopy/network errors
        print("ERROR - geolocator.reverse()")
        return None
    
    if location and location.raw and 'address' in location.raw:
        address = location.raw['address']
        county = address.get('county') or address.get('state_district') or address.get('suburb')
        return county
    
    return None

# Updates the response_json with the correct county name
def set_county(response, lat, long):
    
    try:
        lat, long = float(lat), float(long)
    except:
        response["error"] = True
        response["err_msg"] = "Latitude and Longitude cannot be converted to float"
        return
    
    county_name = get_county_from_coordinates(lat, long)
    
    # Return if an error is given
    if county_name is None:
        response["error"] = True
        response["err_msg"] = "County not found using Geopy Nominatim"
        return
        
    county_name = county_name.replace(" County", "")
    print(f"county name: {county_name}")
    response["county"] = county_name
    
    return

# creates a dataframe using the county name and the excel sheet, then passes it into the response_json
def filter_df(response, df):
    
    # filter out rows that do not contain the county name
    df_filtered = df[df['county'].str.contains(response["county"], case = False, na = False, regex = False)]
    df_filtered = df_filtered.replace({np.nan: None})
    
    response["response"] = df_filtered.to_dict(orient="records")
    
    return

def summary_stats(response, inat_key):
    stats = {
        "numRows": 0,
        "numUniqueBees": 0,
        "numUniquePlants": 0,
        "mostCommonBee": {
            "phylum": "",
            "class": "",
            "order": "",
            "family": "",
            "genus": "",
            "subgenus": "",
            "specificEpithet": "",
            "count": 0,
            "scientificName": ""
        },
        "mostCommonPlant": {
            "phylum": "",
            "class": "",
            "order": "",
            "family": "",
            "genus": "",
            "species": "",
            "count": 0,
            "plantINatId": "",
            "iNatURL": ""
        }
    }

    rows = response.get("response") or []
    if not isinstance(rows, list):
        rows = []

    stats["numRows"] = len(rows)
    if not rows:
        response["response"] = stats
        return

    def normalize_string(value):
        if value is None:
            return None
        if isinstance(value, str):
            trimmed = value.strip()
            return trimmed or None
        return str(value)

    def split_scientific_name(name):
        if not name:
            return "", ""
        parts = name.split()
        if not parts:
            return "", ""
        genus = parts[0]
        species = " ".join(parts[1:]) if len(parts) > 1 else ""
        return genus, species

    bee_counts = Counter()
    plant_counts = Counter()
    most_common_bee_row = None
    most_common_bee_name = ""
    most_common_plant_row = None
    most_common_plant_value = None

    for row in rows:
        # Pollinator counts
        bee_name = normalize_string(row.get("scientificName")) or normalize_string(row.get("specificEpithetVolDet"))
        if bee_name:
            bee_counts[bee_name] += 1
            if bee_counts[bee_name] > stats["mostCommonBee"]["count"]:
                stats["mostCommonBee"]["count"] = bee_counts[bee_name]
                most_common_bee_row = row
                most_common_bee_name = bee_name

        # Plant counts - only plantINatId is available in the dataset
        plant_value = row.get("plantINatId")
        if plant_value is not None:
            plant_counts[plant_value] += 1
            if plant_counts[plant_value] > stats["mostCommonPlant"]["count"]:
                stats["mostCommonPlant"]["count"] = plant_counts[plant_value]
                most_common_plant_row = row
                most_common_plant_value = plant_value

    stats["numUniqueBees"] = len(bee_counts)
    stats["numUniquePlants"] = len(plant_counts)

    if most_common_bee_row:
        genus, species = split_scientific_name(most_common_bee_name)
        stats["mostCommonBee"].update({
            "family": normalize_string(most_common_bee_row.get("familyVolDet")) or "",
            "genus": normalize_string(most_common_bee_row.get("genusVolDet")) or genus,
            "subgenus": normalize_string(most_common_bee_row.get("subgenus")) or "",
            "specificEpithet": normalize_string(most_common_bee_row.get("specificEpithetVolDet")) or species,
            "scientificName": most_common_bee_name
        })

    if most_common_plant_row is not None:
        plant_identifier = normalize_string(most_common_plant_value)
        row_mask = inat_key["id"] == int(plant_identifier)
        species_common_name = inat_key.loc[row_mask, "commonName"].iloc[0] if row_mask.any() else ""
        plant_image_url = inat_key.loc[row_mask, "iNaturalistTaxonImage"].iloc[0] if row_mask.any() else ""
        stats["mostCommonPlant"].update({
            "species": species_common_name or "",
            "plantINatId": plant_identifier or "",
            "iNatURL": plant_image_url or ""
        })

    response["response"] = stats

    return

def main():
    # USE zmq to receive signal
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(f"tcp://*:{PORT}")
    
    while 1:
        request_json = socket.recv_json()
        print(f"Received request: {request_json}")
        
        request = request_json.get("request")
        coords = request_json.get("arg1")
        
        
        if request == "search_location":
            
            response_json = {
                "response": [],
                "county": "",
                "error": False,
                "err_msg" : ""
            }
            
            set_county(response_json, coords)
            
            if response_json["error"]:
                socket.send_json(response_json)
                continue
                
            create_df(response_json)
            
            socket.send_json(response_json)
            
            
        elif request_json["request"] == "end":
            socket.send_json({})
            break
        
        else:
            # unknown request
            socket.send_json({"error" : True, "err_msg" : "Unknown Request"})
    
    socket.close()
    context.term()
    print("Server Closed")


if __name__ == "__main__":
    main()
