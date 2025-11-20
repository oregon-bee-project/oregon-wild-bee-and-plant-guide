import zlib
import pandas as pd
from io import StringIO

# Functions used to parse .viz files
# inflate_viz_file: Decompresses a .viz file using zlib DEFLATE
def inflate_viz_file(file_path):
    with open(file_path, "rb") as f:
        raw = f.read()

    # Correct for zlib-wrapped DEFLATE (0x78 0x9C header)
    return zlib.decompress(raw).decode("utf-8")
#parse_viz_to_dataframe: Parses the decompressed .viz content into a pandas DataFrame
def parse_viz_to_dataframe(path):
    csv_text = inflate_viz_file(path)
    df = pd.read_csv(StringIO(csv_text))
    return df

# Example usage
# df holds the dataframe of parsed file, program can be changed to return the dataframe or write it
if __name__ == "__main__":
    file_path = "../data/b-team/plant-pollinators-OBA-2025-assigned-subset-labels.viz"
    file_path = "../data/b-team/plant-pollinators-OBA-2025-assigned-taxa.viz"
    df = parse_viz_to_dataframe(file_path)

    print("Rows:", len(df))
    print(df.head())
    
