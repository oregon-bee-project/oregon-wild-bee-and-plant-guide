"""
File for loading and preprocessing data to create 
normalized plant/bee interaction matrix

Calls parse_viz.py to get a dataframe from the viz 
files. Then cleans the data into a modeling ready state.
"""

import sys
import os
import numpy as np
import pandas as pd
from typing import Tuple

# Allow imports from parent directory
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


def create_interactions_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Take observation dataframe and return a weighted
    interaction matrix for every plant and bee observation
    in the data

    Use log(total interactions/distinct plants visited) to normalize each
    entry
    """

    # Each unique bee is a row, and each unique plant is a column. 
    # Each entry is the number of observations between the plant and bee.
    interaction_matrix = pd.crosstab(df['pollinatorINatId'], df['plantINatId'])

    # Weight each entry by log_10(total interactions/distinct plants visited)
    total_interactions = interaction_matrix.sum(axis=1) 
    distinct_plants_visited = (interaction_matrix > 0).sum(axis=1)
    weights = np.log10(total_interactions / distinct_plants_visited)
    weighted_interaction_matrix = interaction_matrix.multiply(weights, axis=0)

    return weighted_interaction_matrix


def main() -> None:
    df_observations, _ = load_data()
    interaction_matrix = create_interactions_matrix(df_observations)
    print(interaction_matrix)


if __name__ == "__main__":
    main()
