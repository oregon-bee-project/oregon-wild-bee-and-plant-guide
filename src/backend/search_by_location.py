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

    obs_gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(
            pd.to_numeric(df["decimalLongitude"], errors="coerce"),
            pd.to_numeric(df["decimalLatitude"],  errors="coerce"),
        ),
        crs="EPSG:4326",
    )
    obs_gdf = obs_gdf.dropna(subset=["geometry"])
    filtered_df = gpd.sjoin(obs_gdf, region_geo[["geometry"]], how="inner", predicate="within")
    return pd.DataFrame(filtered_df.drop(columns=["geometry", "index_right"], errors="ignore"))


def get_plant_top_bees(obs_df, top_n=5):
    """
    From an observations DataFrame (with plantINatId and bee name columns),
    return a dict: plant_id (str) -> list of {scientificName, count} for the top_n bees by observed count.
    """
    if obs_df is None or obs_df.empty:
        return {}

    def _norm(v):
        if v is None:
            return None
        if isinstance(v, float) and pd.isna(v):
            return None
        if isinstance(v, str):
            t = v.strip()
            return t or None
        return str(v)

    plant_bee = {}
    for row in obs_df.to_dict(orient="records"):
        bee_name = _norm(row.get("scientificName")) or _norm(row.get("specificEpithetVolDet"))
        plant_value = _norm(row.get("plantINatId"))
        if plant_value and bee_name:
            if plant_value not in plant_bee:
                plant_bee[plant_value] = Counter()
            plant_bee[plant_value][bee_name] += 1

    return {
        str(pid): [{"scientificName": bee, "count": int(count)} for bee, count in counter.most_common(top_n)]
        for pid, counter in plant_bee.items()
    }


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