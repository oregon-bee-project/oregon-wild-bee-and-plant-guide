import zmq
import pandas as pd
import pandas_zmq as pdzmq
from geopy.geocoders import Nominatim

PORT = 5556
EXCEL_PATH = "https://oregonstate.box.com/s/lkrgmxck2gunm1d0yrjz7e48gjstel8u"

def get_county_from_coordinates(latitude, longitude):
    geolocator = Nominatim(user_agent="bee-data") # Replace with your app name
    location = geolocator.reverse((latitude, longitude))

    if location and location.raw and 'address' in location.raw:
        address = location.raw['address']
        county = address.get('county') or address.get('state_district') or address.get('suburb')
        return county
    return None

def get_location(message):
    
    full_location = message[16:]
    
    # find out a way to parse out the county from the full location given
    county_name = get_county_from_coordinates(full_location)
    
    return county_name


def create_df(county):
    
    col_names = ["day", "month", "year", "country", "stateProvince", "county", "locality", "samplingProtocol", 
                 "phylumPlant", "orderPlant", "familyPlant", "genusPlant", "speciesPlant", "taxonRankPlant", 
                 "phylum", "class", "order", "family", "genus", "subgenus", "specificEpithet", "taxonomicNotes", "scientificName", "sex", "caste", "taxonRank"]
    
    full_df = pd.read_excel(EXCEL_PATH, skiprows=1, usecols=col_names, sheet_name = "OBA_2018-2024")
    
    df_filtered = full_df[full_df['county'] == county]
    
    return df_filtered

def main():
    # USE zmq to receive signal
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(f"tcp://*:{PORT}")
    
    while 1:
        message = socket.recv_string()
        print(f"Received request: {message}")
        
        if message.contains("search_location_"):
            
            # do something
            county_name = get_location(message)
            df = create_df(county_name)
            
            #return df
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