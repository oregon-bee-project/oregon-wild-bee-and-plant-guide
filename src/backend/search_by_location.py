import pandas as pd
import numpy as np
from collections import Counter

import geopandas as gpd
from shapely.geometry import Point

shape_files = {"county": "../frontend/public/GeoJSON/county.json",
               "ecoregion": "../frontend/public/GeoJSON/ecoregion.json",
               "refuge": "../frontend/public/GeoJSON/refuges.json",
               "national-forest": "../frontend/public/GeoJSON/national-forest.json",
               "park": "../frontend/public/GeoJSON/parks.json"}

sf_key = {"county": "COUNTY_FIP",
          "ecoregion": "US_L3CODE",
          "refuge": "FWSREGION", # not correct, dummy value
          "national-forest": "FORESTNUMB", 
          "park": "OBJECTID"} #not correct, dummy value

sf_name = {"county": "NAME",
           "ecoregion": "US_L3NAME",
           "refuge": "ORGNAME",
           "national-forest": "FORESTNAME",
           "park": "FULL_NAME"}

df_columns = {"county": "USA Counties",
              "ecoregion": "US Ecoregions Level IV",
              "refuge": "National Wildlife Refuge Boundaries",
              "national-forest": "Forest Service National Forest Boundaries",
              "park": "Oregon State Parks"}

# Cache for loaded GeoDataFrames to prevent re-reading from disk/URL
region_cache = {}

# Searches shape file to find matching County depending on Lat and Long
def get_region_from_coordinates(latitude, longitude, region_type):
    if region_type not in region_cache:
        regions = gpd.read_file(shape_files[region_type])
        # Ensure the shapefile is in the correct CRS (Latitude/Longitude)
        if regions.crs is not None:
            regions = regions.to_crs(epsg=4326)
        region_cache[region_type] = regions
    
    regions = region_cache[region_type]

    target_point = Point(longitude, latitude)
    containing_region = regions[regions.contains(target_point)]

    if not containing_region.empty:
        return (containing_region[sf_name[region_type]].values[0], int(containing_region[sf_key[region_type]].values[0]))
    else:
        return None

# Updates the response_json with the correct region name and code (which corresponds to the df)
def set_region_name(response):
    try:
        lat, long = float(response['lat']), float(response['long'])
    except:
        response["error"] = True
        response["err_msg"] = "Latitude and Longitude cannot be converted to float"
        return
    
    region_tuple = get_region_from_coordinates(lat, long, response['region_type'])
    
    # Return if an error is given
    if region_tuple is None:
        response["error"] = True
        response["err_msg"] = "Region not found using provided Shape Files"
        return
        
    print(f"region name, region key: {region_tuple}")
    response["region_name"], response["region_key"] = region_tuple
    
    return

# creates a dataframe using the region key and the df, then passes it into the response_json
def filter_df(response, df):

    col_name = df_columns[response["region_type"]]

    # filter out rows that do not contain the county name
    df_filtered = df[df[col_name] == response["region_key"]]
    df_filtered = df_filtered.replace({np.nan: None})
    #print("Filtered rows column headers:", list(df_filtered.columns))


    if df_filtered.empty and response["region_type"] == "county":
        county_name = response["region_name"].replace("County", "").strip()

        df_filtered = df[df["county"].str.contains(county_name, case=False, regex=True, na=False)]
        df_filtered = df_filtered.replace({np.nan: None})
    
    response["response"] = df_filtered.to_dict(orient="records")
    
    return


def summary_stats(response, inat_key):
    # Stats key
    # numRows - All observations in filtered area
    # numUniqueBees - 
    stats = {
        "numRows": 0,
        "numUniqueBees": 0,
        "numUniquePlants": 0,
        "mostCommonBees": [],
        "mostCommonPlant": {
            "iNatId": "",
            "iNatTaxonName": "",
            "commonName": "",
            "iNatURL": "",
            "count": 0,
            "topBees": []
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
    # Keep a reference row for each plant id so we can pull taxonomic fields later
    plant_rows_map = {}
    plant_bee_interactions = {}

    for row in rows:
        # Pollinator counts
        bee_name = normalize_string(row.get("scientificName")) or normalize_string(row.get("specificEpithetVolDet"))
        if bee_name:
            bee_counts[bee_name] += 1

        # Plant counts - only plantINatId is available in the dataset
        plant_value = normalize_string(row.get("plantINatId"))
        if plant_value:
            plant_counts[plant_value] += 1
            if plant_value not in plant_rows_map:
                plant_rows_map[plant_value] = row

            if bee_name:
                if plant_value not in plant_bee_interactions:
                    plant_bee_interactions[plant_value] = Counter()
                plant_bee_interactions[plant_value][bee_name] += 1

    stats["numUniqueBees"] = len(bee_counts)
    stats["numUniquePlants"] = len(plant_counts)

    for bee, count in bee_counts.most_common(5):
        stats["mostCommonBees"].append({
            "scientificName": bee,
            "count": count
        })

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

            if plant_identifier in plant_bee_interactions:
                for bee, count in plant_bee_interactions[plant_identifier].most_common(5):
                    stats["mostCommonPlant"]["topBees"].append({
                        "scientificName": bee,
                        "count": count
                    })
            break

    response["response"] = stats

    return