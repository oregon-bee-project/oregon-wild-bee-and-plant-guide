import pandas as pd
import numpy as np
from collections import Counter

from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.exc import (
    GeocoderTimedOut,
    GeocoderServiceError,
    GeocoderUnavailable,
    GeocoderQueryError,
    GeocoderQuotaExceeded,
)

PORT = 5556
DATA_PATH = "../data/example_data.json" # change this for GitHub Pages

COUNTY_FALLBACK = {
    # 44.56, -123.26 is Corvallis/Benton County
    (44, -123): "Benton", 
    (45, -122): "Clackamas", 
    # Add other Oregon counties as needed
}
# Seraches internet to find matching County depending on Lat and Long
def get_county_from_coordinates(latitude, longitude):
    geolocator = Nominatim(user_agent="bee-data")
    rl_geolocator = RateLimiter(geolocator.reverse, min_delay_seconds=1.1)
    try:
        location = rl_geolocator.reverse((latitude, longitude), timeout=5)
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
    
    region_key = (round(lat), round(long))
    

    if region_key in COUNTY_FALLBACK:
        response["county"] = COUNTY_FALLBACK[region_key]
        return
    
    county_name = get_county_from_coordinates(lat, long)
    # Return if an error is given
    if county_name is None and county_name != "Benton":
        response["error"] = True
        response["err_msg"] = "Geocoding failed. Using safe default (Benton) for stability."
        response["county"] = "benton" 
        
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
            "scientificName": "",
            "count": 0
        },
        "mostCommonPlant": {
            "iNatId": "",
            "iNatTaxonName": "",
            "commonName": "",
            "iNatURL": "",
            "count": 0
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
        if isinstance(value, float) and pd.isna(value):  # <- add NaN guard
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
    most_common_bee_name = ""
    # Keep a reference row for each plant id so we can pull taxonomic fields later
    plant_rows_map = {}

    for row in rows:
        # Pollinator counts
        bee_name = normalize_string(row.get("scientificName")) or normalize_string(row.get("specificEpithetVolDet"))
        if bee_name:
            bee_counts[bee_name] += 1
            if bee_counts[bee_name] > stats["mostCommonBee"]["count"]:
                stats["mostCommonBee"]["count"] = bee_counts[bee_name]
                most_common_bee_name = bee_name

        # Plant counts - only plantINatId is available in the dataset
        plant_value = normalize_string(row.get("plantINatId"))
        if plant_value:
            plant_counts[plant_value] += 1
            if plant_value not in plant_rows_map:
                plant_rows_map[plant_value] = row

    stats["numUniqueBees"] = len(bee_counts)
    stats["numUniquePlants"] = len(plant_counts)

    if most_common_bee_name:
        stats["mostCommonBee"]["count"] = bee_counts[most_common_bee_name]
        stats["mostCommonBee"]["scientificName"] = most_common_bee_name

    if plant_counts:
        for plant_id, count in plant_counts.most_common():
            plant_identifier = normalize_string(plant_id)
            common_name = ""
            taxon_name = ""
            plant_image_url = ""

            row_mask = None
            if plant_identifier:
                try:
                    row_mask = inat_key["id"] == int(float(plant_identifier))
                except (ValueError, TypeError):
                    row_mask = None

            if row_mask is not None and row_mask.any():
                if "commonName" in inat_key.columns:
                    common_name = normalize_string(inat_key.loc[row_mask, "commonName"].iloc[0]) or ""
                if not taxon_name and "scientificName" in inat_key.columns:
                    taxon_name = normalize_string(inat_key.loc[row_mask, "scientificName"].iloc[0]) or ""
                if not taxon_name and "name" in inat_key.columns:
                    taxon_name = normalize_string(inat_key.loc[row_mask, "name"].iloc[0]) or ""
                if "iNaturalistTaxonImage" in inat_key.columns:
                    plant_image_url = normalize_string(inat_key.loc[row_mask, "iNaturalistTaxonImage"].iloc[0]) or ""

            if not common_name:
                continue  # skip plants without a name

            stats["mostCommonPlant"]["count"] = count
            stats["mostCommonPlant"]["commonName"] = common_name
            stats["mostCommonPlant"]["iNatTaxonName"] = taxon_name
            stats["mostCommonPlant"]["iNatId"] = plant_identifier or ""
            stats["mostCommonPlant"]["iNatURL"] = plant_image_url
            break

    response["response"] = stats

    return