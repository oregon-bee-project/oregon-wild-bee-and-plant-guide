import pandas as pd
import numpy as np
from collections import Counter


def everySpeciesList(response, inat_key, df, bee_list_offset=0, bee_list_limit=None):
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

    if df is None or df.empty:
        stats["beeListTotal"] = 0
        stats["beeListOffset"] = bee_list_offset if bee_list_limit is not None else 0
        stats["beeListLimit"] = bee_list_limit
        stats["beeListHasMore"] = False
        response["response"] = stats
        return

    stats["numRows"] = int(len(df.index))
    if stats["numRows"] == 0:
        stats["beeListTotal"] = 0
        stats["beeListOffset"] = bee_list_offset if bee_list_limit is not None else 0
        stats["beeListLimit"] = bee_list_limit
        stats["beeListHasMore"] = False
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

    plant_counts = Counter()
    species_stats = {}
    
    male_count = 0
    female_count = 0

    for row in df.itertuples(index=False):
        # Pollinator counts
        bee_name = normalize_string(getattr(row, "scientificName", None)) or normalize_string(getattr(row, "specificEpithetVolDet", None))
        
        # Sex counts
        sex = normalize_string(getattr(row, "sex", None))
        s_lower = None
        if sex:
            s_lower = sex.lower()
            if s_lower == "male" or s_lower == "m":
                male_count += 1
            elif s_lower == "female" or s_lower == "f":
                female_count += 1

        # Plant counts
        plant_value = normalize_string(getattr(row, "plantINatId", None))
        
        if plant_value:
            plant_counts[plant_value] += 1

        if bee_name:
            if bee_name not in species_stats:
                species_stats[bee_name] = {
                    "count": 0,
                    "maleCount": 0,
                    "femaleCount": 0,
                    "winterCount": 0,
                    "springCount": 0,
                    "summerCount": 0,
                    "fallCount": 0,
                    "plant_interactions": Counter()
                }
            entry = species_stats[bee_name]
            entry["count"] += 1

            if s_lower:
                if s_lower == "male" or s_lower == "m":
                    entry["maleCount"] += 1
                elif s_lower == "female" or s_lower == "f":
                    entry["femaleCount"] += 1

            if plant_value:
                entry["plant_interactions"][plant_value] += 1

            event_date = getattr(row, "eventDate", None)
            if event_date:
                try:
                    dt = pd.to_datetime(str(event_date), errors='coerce')
                    if not pd.isna(dt):
                        month = dt.month
                        if month in [12, 1, 2]:
                            entry["winterCount"] += 1
                        elif month in [3, 4, 5]:
                            entry["springCount"] += 1
                        elif month in [6, 7, 8]:
                            entry["summerCount"] += 1
                        elif month in [9, 10, 11]:
                            entry["fallCount"] += 1
                except (ValueError, TypeError):
                    pass

    stats["numUniqueBees"] = len(species_stats)
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

    # Build beeList (optionally a slice for API pagination)
    sorted_species = sorted(species_stats.items(), key=lambda item: item[1]["count"], reverse=True)
    total_bees = len(sorted_species)
    stats["beeListTotal"] = total_bees

    if bee_list_limit is None:
        slice_species = sorted_species
        stats["beeListOffset"] = 0
        stats["beeListLimit"] = None
        stats["beeListHasMore"] = False
    else:
        slice_species = sorted_species[bee_list_offset : bee_list_offset + bee_list_limit]
        stats["beeListOffset"] = bee_list_offset
        stats["beeListLimit"] = bee_list_limit
        stats["beeListHasMore"] = (bee_list_offset + len(slice_species)) < total_bees

    for bee, entry in slice_species:
        bee_obj = {
            "scientificName": bee,
            "count": entry["count"],
            "maleCount": entry["maleCount"],
            "femaleCount": entry["femaleCount"],
            "winterCount": entry["winterCount"],
            "springCount": entry["springCount"],
            "summerCount": entry["summerCount"],
            "fallCount": entry["fallCount"],
            "topPlants": []
        }
        
        for plant_id, p_count in entry["plant_interactions"].most_common(5):
            common_name = ""
            taxon_name = ""
            image_url = ""
            
            try:
                p_id_int = int(float(plant_id))
                if p_id_int in inat_dict:
                    info = inat_dict[p_id_int]
                    common_name = normalize_string(info.get("commonName")) or ""
                    taxon_name = (
                        normalize_string(info.get("scientificName"))
                        or normalize_string(info.get("name"))
                        or normalize_string(info.get("iNaturalistTaxonName"))
                        or ""
                    )
                    image_url = normalize_string(info.get("iNaturalistTaxonImage")) or ""
            except (ValueError, TypeError):
                pass

            display_name = common_name or taxon_name
            
            bee_obj["topPlants"].append({
                "plantINatId": plant_id,
                "commonName": display_name,
                "scientificName": taxon_name,
                "count": p_count,
                "image": image_url
            })
        
        stats["beeList"].append(bee_obj)

    response["response"] = stats

    return

def heatmap_as_image(df):
    """
    Renders the density heatmap as a PNG and returns the raw bytes.
    Returns None if plotly or kaleido are not installed.
    """
    try:
        import plotly.express as px
        fig = heatmap(df)
        # scale=2 was very memory-heavy for large exports; keep PDFs smaller for browser downloads.
        return fig.to_image(format="png", width=900, height=560, scale=1)
    except Exception:
        return None


def heatmap(df):
    """
    Generates a Plotly density heatmap from a filtered observations DataFrame.
    Returns the plotly Figure object so callers can decide how to render or export it.
    Dependencies (plotly) are imported lazily so the server starts without them installed.
    """
    import plotly.express as px

    plot_df = df.dropna(subset=["decimalLatitude", "decimalLongitude"])
    if plot_df.empty:
        plot_df = df
    max_points = 5000
    if len(plot_df.index) > max_points:
        plot_df = plot_df.sample(n=max_points, random_state=42)

    lat_min, lat_max = df["decimalLatitude"].min(), df["decimalLatitude"].max()
    lon_min, lon_max = df["decimalLongitude"].min(), df["decimalLongitude"].max()

    center_lat = (lat_min + lat_max) / 2
    center_lon = (lon_min + lon_max) / 2

    max_spread = max(lat_max - lat_min, lon_max - lon_min) * 1.1

    zoom_level = (8 - np.log2(max_spread)) - 1.0
    zoom_level = max(0, min(zoom_level, 15))

    dynamic_radius = 150 / (zoom_level if zoom_level > 0 else 1)

    fig = px.density_mapbox(
        plot_df,
        lat='decimalLatitude',
        lon='decimalLongitude',
        radius=dynamic_radius,
        range_color=[0, max(len(plot_df) ** 0.5, 1)],
        center=dict(lat=center_lat, lon=center_lon),
        zoom=zoom_level,
        mapbox_style="open-street-map"
    )

    fig.update_layout(
        mapbox=dict(
            bounds=dict(
                west=lon_min - 0.2,
                east=lon_max + 0.2,
                south=lat_min - 0.2,
                north=lat_max + 0.2
            )
        ),
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )

    return fig
