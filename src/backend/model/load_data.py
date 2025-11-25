"""
File for loading and preprocessing data for the model.

Calls parse_viz.py to get a dataframe from the viz 
files. Then cleans the data into a modeling ready state.
"""

import sys
import os
import pandas as pd
from typing import Tuple

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(parent_dir)

from parse_viz import parse_viz_to_dataframe


def load_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load data from viz files into dataframes and returns them.
    """
    file_path_labels = "data/b-team/plant-pollinators-OBA-2025-assigned-subset-labels.viz"
    file_path_taxa = "data/b-team/plant-pollinators-OBA-2025-assigned-taxa.viz"
    df_observations = parse_viz_to_dataframe(file_path_labels)
    df_iNat_lookup = parse_viz_to_dataframe(file_path_taxa)
    
    return df_observations, df_iNat_lookup


def preprocess_observations(df: pd.DataFrame) -> pd.DataFrame:
    """
    Take observation dataframe and return a new dataframe
    with observations grouped by region
    """
    columns_to_keep = ["decimalLatitude", "decimalLongitude", "plantINatId", "pollinatorINatId"]
    df = df[columns_to_keep].copy()
    # approximate degrees per meter at Oregon latitude
    meters_per_deg_lat = 111132  # nearly constant
    meters_per_deg_lon = 78000   # approx at ~44° north

    cell_meters = 6000 # same as mellitoflora webpage

    lat_cell_deg = cell_meters / meters_per_deg_lat   # ≈ 0.054°
    lon_cell_deg = cell_meters / meters_per_deg_lon   # ≈ 0.077°

    # get min lat/long to anchor the grid
    min_lat = df["decimalLatitude"].min()
    min_lon = df["decimalLongitude"].min()

    # compute grid cell indices
    df["grid_row"] = ((df["decimalLatitude"] - min_lat) / lat_cell_deg).astype(int)
    df["grid_col"] = ((df["decimalLongitude"] - min_lon) / lon_cell_deg).astype(int)

    num_cols = df["grid_col"].max() + 1
    df["grid_cell_flattened"] = df["grid_row"] * num_cols + df["grid_col"]

    # group plant and pollinator counts by region
    plant_counts = (
        df.groupby('grid_cell_flattened')['plantINatId']
        .value_counts()
        .unstack(fill_value=0)
        .add_prefix("plant_")
    )

    pollinator_counts = (
        df.groupby('grid_cell_flattened')['pollinatorINatId']
        .value_counts()
        .unstack(fill_value=0)
        .add_prefix("pollinator_")
    )

    region_summary = plant_counts.join(pollinator_counts, how='outer').fillna(0).astype(int)

    # get total plant and pollinator counts for each region
    
    
    return region_summary


def main() -> None:
    df_observations, df_iNat_lookup = load_data()
    df_cleaned_observations = preprocess_observations(df_observations)
    print(df_cleaned_observations.head())



if __name__ == "__main__":
    main()
