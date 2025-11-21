"""
File for loading data for the model.

Calls parse_viz.py to get a dataframe from the viz 
files. Then cleans the data into a modeling ready state.
"""

import pandas as pd
from ..parse_viz import parse_viz_to_dataframe


def main() -> None:
    file_path = "../data/b-team/plant-pollinators-OBA-2025-assigned-subset-labels.viz"
    file_path = "../data/b-team/plant-pollinators-OBA-2025-assigned-taxa.viz"
    df = parse_viz_to_dataframe(file_path)
    print(df.head())


if __name__ == "__main__":
    main()