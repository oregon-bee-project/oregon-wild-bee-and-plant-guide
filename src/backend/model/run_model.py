"""
Run the trained model to 
answer the prompt: "Which plants
should I grow to support local bees
in my area"
"""

from load_data import get_clean_observation_dataframe
from xgboost import XGBRegressor
from sklearn.preprocessing import MinMaxScaler
from sklearn.pipeline import Pipeline
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pickle

def load_model() -> Pipeline:
    model_pkl_file = "./backend/model/bee_diversity_reggressor_model.pkl"  

    with open(model_pkl_file, 'rb') as file:  
        model = pickle.load(file)
    return model


def get_candidate_plants(df: pd.DataFrame, region: int) -> np.array:
    """
    Given the cleaned data and a region from the user, 
    output a list of candidate plants to test our model 
    on to determine the best plant to maximize the Bee-Shannon 
    diversity index

    Currently candidate plants are all possible plants. This
    will likely be tuned to include less plants in the future,
    depending on runtime requirements. 
    """
    all_observed_plants = [column for column in df.columns if column.split("_")[0] == "plant"]
    candidates = all_observed_plants

    # TEST
    candidates = np.array(["plant_47121", "plant_47130", "plant_47324"])
    return candidates


def get_region_from_coordinates(df: pd.DataFrame, lat: float, long: float) -> int:
    """
    This will need to get the region
    the user selected based on the lat
    and long and return it
    """
    # same constants used in load data
    meters_per_deg_lat = 111132 
    meters_per_deg_lon = 78000   
    cell_meters = 6000 

    lat_cell_deg = cell_meters / meters_per_deg_lat   # ≈ 0.054°
    lon_cell_deg = cell_meters / meters_per_deg_lon   # ≈ 0.077°

    # get grid anchors from observation dataframe
    min_lat = df["_min_lat"].iloc[0]
    min_lon = df["_min_lon"].iloc[0]

    grid_row = int((lat - min_lat) / lat_cell_deg)
    grid_col = int((long - min_lon) / lon_cell_deg)

    num_cols = df["_num_cols"].iloc[0]

    return grid_row * num_cols + grid_col


def get_best_plants(response: dict, lat: float, long: float):
    """
    Run the entire workflow to get the best plants
    and populates the response_json with the top plants
    """
    TOP_K = 2 # number of plants to return

    model = load_model()
    df = get_clean_observation_dataframe().reset_index()
    region = get_region_from_coordinates(df, lat, long)
    candidate_plants = get_candidate_plants(df, region)

    # create a feature dataframe, where each row is the region
    # with the candidate plant added (if the candidate already exists
    # nothing changes, since they are one-hot-encoded)
    df_no_meta_data = df.drop(columns=["_min_lat", "_min_lon", "_num_cols"])
    region_row = df_no_meta_data[df_no_meta_data["region"] == region].iloc[0]
    
    rows = []

    for plant in candidate_plants:
        new_row = region_row.copy()
        new_row[plant] = 1
        rows.append(new_row)

    region_with_candidate_plants_added = pd.DataFrame(rows)

    # make predictions on the feature dataframe
    predictions = model.predict(region_with_candidate_plants_added)
    
    # get the top k plants for the highest predicted diversity
    topk_idx = np.argsort(predictions)[-TOP_K:][::-1]
    best_plants = candidate_plants[topk_idx]

    # return the names of those plants
    print(best_plants)
    response["response"] = best_plants


def main() -> None:
    print("Display test for coordinates Lat: 44.56, Lon: -123.25")
    response_json = {
        "response": [],
        "error": False,
        "err_msg" : ""
    }
    get_best_plants(response_json, 44.56, -123.25)


if __name__ == "__main__":
    main()