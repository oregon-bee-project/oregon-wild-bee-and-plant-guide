"""
File for loading data for the model.

Calls parse_viz.py to get a dataframe from the viz 
files. Then cleans the data into a modeling ready state.
"""

import sys
import os
import pandas as pd

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(parent_dir)

from parse_viz import parse_viz_to_dataframe

"""
Load the data into two dataframes and returns them.
"""
def load_data() -> pd.DataFrame:
    file_path_labels = "data/b-team/plant-pollinators-OBA-2025-assigned-subset-labels.viz"
    file_path_taxa = "data/b-team/plant-pollinators-OBA-2025-assigned-taxa.viz"
    dflabels = parse_viz_to_dataframe(file_path_labels)
    dftaxa = parse_viz_to_dataframe(file_path_taxa)
    print("\nLabels DataFrame:\n")
    print(dflabels.head())
    print("\nTaxa DataFrame:\n")
    print(dftaxa.head())
    return dflabels, dftaxa

def main() -> None:
    load_data()


if __name__ == "__main__":
    main()