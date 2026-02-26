import pandas as pd
import numpy as np
import json
from collections import Counter

import geopandas as gpd
from shapely.geometry import Point

shape_files = {"county": "../frontend/public/GeoJSON/county.json",
               "ecoregion": "../frontend/public/GeoJSON/ecoregion.json",
               "national-forest": "../frontend/public/GeoJSON/national-forest.json",}

sf_name = {"county": "NAME",
           "ecoregion": "US_L3NAME",
           "national-forest": "FORESTNAME"}

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
        return (containing_region[sf_name[region_type]].values[0], containing_region)
    else:
        return (None, None)

# creates a dataframe using the region key and the df, then passes it into the response_json
def filter_df(response, df):

    try:
        lat, long = float(response['lat']), float(response['long'])
    except:
        response["error"] = True
        response["err_msg"] = "Latitude and Longitude cannot be converted to float"
        return None

    region_name, region_geo = get_region_from_coordinates(lat, long, response['region_type'])

    if region_name is None:
        response["error"] = True
        response["err_msg"] = "Region not found using provided Shape Files"
        return None
    
    print(f"region name = {region_name}")

    response["region_name"] = region_name

    filtered_rows = []

    for index, row in df.iterrows():
        try:
            cLat, cLon = float(row["decimalLatitude"]), float(row["decimalLongitude"])
        except (ValueError, TypeError):
            continue

        point = Point(cLon, cLat)
        if region_geo.contains(point).any():
            filtered_rows.append(row)

    if filtered_rows:
        df_filtered = pd.DataFrame(filtered_rows)
    else:
        df_filtered = pd.DataFrame(columns=df.columns)
    
    return df_filtered


def summary_stats(response, inat_key, df):
    # Stats key
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

    rows = df.to_dict(orient="records") or []
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