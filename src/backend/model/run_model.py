"""
Run the trained model to 
answer the prompt: "Which plants
should I grow to support local bees
in my area"
"""

from load_data import get_clean_observation_dataframe
from xgboost import XGBRegressor
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pickle

def load_model() -> XGBRegressor:
    model_pkl_file = "./backend/model/bee_diversity_reggressor_model.pkl"  

    with open(model_pkl_file, 'rb') as file:  
        model = pickle.load(file)
    return model


def get_candidate_plants(df: pd.DataFrame, region: int) -> list[str]:
    """
    Given the cleaned data and a region from the user, 
    output a list of candidate plants to test our model 
    on to determine the best plant to maximize Bthe Bee-Shannon 
    diversity index

    Currently candidate plants are all possible plants. This
    will likely be tuned to include less plants in the future,
    depending on runtime requirements. 
    """
    all_observed_plants = [column for column in df.columns if column.split("_")[0] == "plant"]
    candidates = all_observed_plants
    return candidates


def get_region_from_user() -> int:
    """
    This will need to get the region
    the user selected the location as
    """

    return 1


def main() -> None:
    df = get_clean_observation_dataframe()
    model = load_model()
    region = get_region_from_user()
    candidate_plants = get_candidate_plants(df, region)
    # run model with adding each candidate plant to the current region plant vector
    # get plants that leads to top diversity score and return them. 


if __name__ == "__main__":
    main()