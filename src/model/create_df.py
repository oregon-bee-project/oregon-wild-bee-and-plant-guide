import zmq
import pandas as pd
import pandas_zmq as pdzmq
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
    
    print("ERROR - Unable to find location info")
    return None

def get_location(message):
    
    full_location = message[16:]
    
    full_location = full_location.replace(" ", "")
    
    try:
        lat, long = full_location.split(",")
    except:
        print("ERROR - Does not provide Latitude and Longitude")
        return None
    
    try:
        lat, long = float(lat), float(long)
    except:
        print("ERROR - Latitude and Longitude cannot be converted to float")
        return None
    
    # find out a way to parse out the county from the full location given
    county_name = get_county_from_coordinates(lat, long)
    
    if county_name is None:
        return None
        
    county_name = county_name.replace(" County", "")
    print(f"county name : {county_name}")
    return county_name


def create_df(county):
    
    col_names = ["day", "month", "year", "country", "stateProvince", "county", "locality", "samplingProtocol", 
                 "phylumPlant", "orderPlant", "familyPlant", "genusPlant", "speciesPlant", "taxonRankPlant", 
                 "phylum", "class", "order", "family", "genus", "subgenus", "specificEpithet", "taxonomicNotes",
                 "scientificName", "sex", "caste", "taxonRank"]
    
    try:
        full_df = pd.read_excel(EXCEL_PATH, usecols=col_names, sheet_name = "OBA_2018-2024")
    except:
        print("ERROR - Excel did not open")
        return None
    
    df_filtered = full_df[full_df['county'] == county]
    
    return df_filtered

def main():
    # USE zmq to receive signal
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(f"tcp://*:{PORT}")  # ADD ERROR HANDLING
    
    while 1:
        message = socket.recv_string()  # ADD ERROR HANDLING
        print(f"Received request: {message}")
        
        if "search_location_" == message[:16]:
            
            # do something
            county_name = get_location(message)
            
            if county_name is None:
                pdzmq.send_dataframe(socket, pd.DataFrame()) #return an empty dataframe
                continue
                
            df = create_df(county_name)
            
            if df is None:
                pdzmq.send_dataframe(socket, pd.DataFrame()) #return an empty dataframe
                continue
            
            pdzmq.send_dataframe(socket, df)
            
            
        elif message == "end":
            socket.send_string("Ending Server")
            break
        
        else:
            # unknown request
            socket.send_string("Unknown request")
    
    socket.close()
    context.term()
    print("Server Closed")


if __name__ == "__main__":
    main()
