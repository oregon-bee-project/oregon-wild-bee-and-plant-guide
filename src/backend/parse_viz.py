import zlib
import pandas as pd
from io import StringIO
import fastapi

def inflate_viz_file(file_path):
    with open(file_path, "rb") as f:
        raw = f.read()

    # Correct for zlib-wrapped DEFLATE (0x78 0x9C header)
    return zlib.decompress(raw).decode("utf-8")


def parse_viz_to_dataframe(path):
    csv_text = inflate_viz_file(path)
    df = pd.read_csv(StringIO(csv_text))
    return df


if __name__ == "__main__":
    file_path = "../data/b-team/plant-pollinators-OBA-2025-assigned-subset-labels.viz"
    file_path = "../data/b-team/plant-pollinators-OBA-2025-assigned-taxa.viz"
    df = parse_viz_to_dataframe(file_path)

    print("Rows:", len(df))
    print(df.head())
    print(fastapi.__version__)
    
