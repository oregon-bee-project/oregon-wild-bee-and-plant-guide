import pandas as pd
import numpy as np
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import pandas as pd


def everySpeciesList (response, inat_key):
    # Stats key
    # numRows - All observations in filtered area
    # numUniqueBees - 
    # numUniquePlants - 
    # totalMales - 
    # totalFemales - 
    # beeList - List of every bee species, frequency, and top 5 interacting plants
    stats = {
        "numRows": 0,
        "numUniqueBees": 0,
        "numUniquePlants": 0,
        "totalMales": 0,
        "totalFemales": 0,
        "beeList": []
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

    bee_counts = Counter()
    plant_counts = Counter()
    bee_plant_interactions = {}
    
    male_count = 0
    female_count = 0

    for row in rows:
        # Pollinator counts
        bee_name = normalize_string(row.get("scientificName")) or normalize_string(row.get("specificEpithetVolDet"))
        
        # Sex counts
        sex = normalize_string(row.get("sex"))
        if sex:
            s_lower = sex.lower()
            if s_lower == "male":
                male_count += 1
            elif s_lower == "female":
                female_count += 1

        # Plant counts
        plant_value = normalize_string(row.get("plantINatId"))
        
        if bee_name:
            bee_counts[bee_name] += 1
            if plant_value:
                if bee_name not in bee_plant_interactions:
                    bee_plant_interactions[bee_name] = Counter()
                bee_plant_interactions[bee_name][plant_value] += 1

        if plant_value:
            plant_counts[plant_value] += 1

    stats["numUniqueBees"] = len(bee_counts)
    stats["numUniquePlants"] = len(plant_counts)
    stats["totalMales"] = male_count
    stats["totalFemales"] = female_count

    # Create lookup dictionary for plant taxonomy
    inat_dict = {}
    if not inat_key.empty:
        try:
            temp_df = inat_key.copy()
            temp_df['id'] = pd.to_numeric(temp_df['id'], errors='coerce')
            temp_df = temp_df.dropna(subset=['id'])
            temp_df['id'] = temp_df['id'].astype(int)
            temp_df = temp_df.drop_duplicates(subset=['id'])
            inat_dict = temp_df.set_index('id').to_dict(orient='index')
        except Exception:
            inat_dict = {}

    # Build beeList
    for bee, count in bee_counts.most_common():
        bee_obj = {
            "scientificName": bee,
            "count": count,
            "topPlants": []
        }
        
        if bee in bee_plant_interactions:
            for plant_id, p_count in bee_plant_interactions[bee].most_common(5):
                # Resolve plant info
                common_name = ""
                taxon_name = ""
                image_url = ""
                
                try:
                    p_id_int = int(float(plant_id))
                    if p_id_int in inat_dict:
                        info = inat_dict[p_id_int]
                        common_name = normalize_string(info.get("commonName")) or ""
                        taxon_name = normalize_string(info.get("scientificName")) or normalize_string(info.get("name")) or ""
                        image_url = normalize_string(info.get("iNaturalistTaxonImage")) or ""
                except (ValueError, TypeError):
                    pass
                
                bee_obj["topPlants"].append({
                    "plantINatId": plant_id,
                    "commonName": common_name,
                    "scientificName": taxon_name,
                    "count": p_count,
                    "image": image_url
                })
        
        stats["beeList"].append(bee_obj)

    response["response"] = stats

    return

def heatmap (df):

    lat_min, lat_max = df['decimalLatitude'].min(), df['decimalLatitude'].max()
    lon_min, lon_max = df['decimalLongitude'].min(), df['decimalLongitude'].max()
    
    center_lat = (lat_min + lat_max) / 2
    center_lon = (lon_min + lon_max) / 2

    max_spread = max(lat_max - lat_min, lon_max - lon_min) * 1.1

    zoom_level = (8 - np.log2(max_spread)) - 1.0
    zoom_level = max(0, min(zoom_level, 15))

    dynamic_radius = 150 / (zoom_level if zoom_level > 0 else 1)

    fig = px.density_mapbox(df, 
                            lat='decimalLatitude', 
                            lon='decimalLongitude', 
                            radius= dynamic_radius, 
                            range_color = [0, len(df) ** 0.5], 
                            center=dict(lat=center_lat, lon=center_lon), 
                            zoom = zoom_level, 
                            mapbox_style="open-street-map")
    
    fig.update_layout(
        mapbox=dict(
            bounds=dict(
                west=lon_min - 0.2,
                east=lon_max + 0.2,
                south=lat_min - 0.2,
                north=lat_max + 0.2
            )
        ),
        margin={"r":0,"t":0,"l":0,"b":0}
    )
    
    fig.show()

    return
