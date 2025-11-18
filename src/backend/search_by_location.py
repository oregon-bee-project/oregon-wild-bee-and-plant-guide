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
def set_county(response, coordinates):
    
    full_location = coordinates.replace(" ", "")
    
    try:
        lat, long = full_location.split(",")
    except:
        response["error"] = True
        response["err_msg"] = "Does not provide Latitude and Longitude"
        return
    
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
def create_df(response):
    
    try:
        full_df = pd.read_json(DATA_PATH)
    except:
        response["error"] = True
        response["err_msg"] = "read_json() did not open properly"
        return
    
    # filter out rows that do not contain the county name
    df_filtered = full_df[full_df['county'].str.contains(response["county"], case = False, na = False, regex = False)]
    df_filtered = df_filtered.replace({np.nan: None})
    
    response["response"] = df_filtered.to_dict(orient="records")
    
    return

def summary_stats(response):
    stats = {
        "numRows" : 0,
        "numUniqueBees" : 0,
        "numUniquePlants" : 0,
        "mostCommonBee" : {
            "phylum" : "",
            "class" : "",
            "order" : "",
            "family" : "",
            "genus" : "",
            "subgenus" : "",
            "specificEpithet" : "",
            "count" : 0
        },
        "mostCommonPlant": {
            "phylum" : "",
            "class" : "",
            "order" : "",
            "family" : "",
            "genus" : "",
            "species" : "",
            "count" : 0
        }
    }
    
    data = response["response"]

    rows = data if isinstance(data, list) else []
    stats["numRows"] = len(rows)
    if not rows:
        return stats

    bee_counts = Counter()
    plant_counts = Counter()
    most_bee_row = None
    most_plant_row = None

    for row in rows:
        plant_rank = row.get("taxonRankPlant")
        bee_value = row.get("specificEpithet")
        plant_value = row.get(f"{plant_rank}Plant") if plant_rank else None

        if bee_value is not None:
            bee_counts[bee_value] += 1
            if bee_counts[bee_value] > stats["mostCommonBee"]["count"]:
                stats["mostCommonBee"]["count"] = bee_counts[bee_value]
                most_bee_row = row

        if plant_value is not None:
            plant_counts[plant_value] += 1
            if plant_counts[plant_value] > stats["mostCommonPlant"]["count"]:
                stats["mostCommonPlant"]["count"] = plant_counts[plant_value]
                most_plant_row = row

    stats["numUniqueBees"] = len(bee_counts)
    stats["numUniquePlants"] = len(plant_counts)

    if most_bee_row:
        stats["mostCommonBee"].update({
            "phylum": most_bee_row.get("phylum", ""),
            "class": most_bee_row.get("class", ""),
            "order": most_bee_row.get("order", ""),
            "family": most_bee_row.get("family", ""),
            "genus": most_bee_row.get("genus", ""),
            "subgenus": most_bee_row.get("subgenus", ""),
            "specificEpithet": most_bee_row.get("specificEpithet", ""),
        })

    if most_plant_row:
        stats["mostCommonPlant"].update({
            "phylum": most_plant_row.get("phylumPlant", ""),
            "class": most_plant_row.get("classPlant", ""),
            "order": most_plant_row.get("orderPlant", ""),
            "family": most_plant_row.get("familyPlant", ""),
            "genus": most_plant_row.get("genusPlant", ""),
            "species": most_plant_row.get("speciesPlant", ""),
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
