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

    # TF: Raw counts with Rows = Bees, Cols = Plants
    interaction_matrix = pd.crosstab(df['pollinatorINatId'].astype(str), df['plantINatId'].astype(str))

    # SVD works better when data compressed to be realtively close
    matrix_log = pd.DataFrame(np.log1p(interaction_matrix))

    total_bees = interaction_matrix.shape[0]
    bees_per_plant = (interaction_matrix > 0).sum(axis=0)
    idf_weights = np.log10(total_bees / (bees_per_plant + 1))
    
    tfidf_matrix = matrix_log.multiply(idf_weights, axis=1)

    return tfidf_matrix


def main() -> None:
    df_observations, _ = load_data()
    interaction_matrix = create_interactions_matrix(df_observations)
    print(interaction_matrix)


if __name__ == "__main__":
    main()
