import zmq
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.exc import (
    GeocoderTimedOut,
    GeocoderServiceError,
    GeocoderUnavailable,
    GeocoderQueryError,
    GeocoderQuotaExceeded,
)

PORT = 5556
EXCEL_PATH = "C:/Users/15038/Capstone/bee-plant-data-exploration/src/data/cleaned_OBA_2018-2024_V1_7_10-3-2025.xlsx"

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
    
    col_names = ["day", "month", "year", "country", "stateProvince", "county", "locality", "samplingProtocol", 
                 "phylumPlant", "orderPlant", "familyPlant", "genusPlant", "speciesPlant", "taxonRankPlant", 
                 "phylum", "class", "order", "family", "genus", "subgenus", "specificEpithet", "taxonomicNotes",
                 "scientificName", "sex", "caste", "taxonRank"]
    
    try:
        full_df = pd.read_excel(EXCEL_PATH, usecols=col_names, sheet_name = "OBA_2018-2024")
    except:
        response["error"] = True
        response["err_msg"] = "Excel did not open properly"
        return
    
    # filter out rows that do not contain the county name
    df_filtered = full_df[full_df['county'].str.contains(response["county"], case = False, na = False, regex = False)]
    
    response["response"] = df_filtered.to_dict(orient="records")
    
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
