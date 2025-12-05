from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import search_by_location as sl
import parse_viz as pv

app = FastAPI()

# This is the list of "origins" (websites) that are allowed to make requests.
# Even if you aren't using it yet, it's good practice to have.
origins = [
    "https://kellen-sullivan.github.io", # Your GitHub Pages URL
    "http://localhost:5173",         # Your local dev environment (Vite default)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

full_df = pv.parse_viz_to_dataframe("../data/b-team/plant-pollinators-OBA-2025-assigned-subset-labels.viz")
inat_key = pv.parse_viz_to_dataframe("../data/b-team/plant-pollinators-OBA-2025-assigned-taxa.viz")
# WINTER IMPROVEMENTS: include a parsing function for each spatial boundary file used

# WINTER IMPROVEMENTS: include an array of previous filtered dataframes, so that user can print reports
# from history or other processes can resuse data quickly

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/api/location-data/")
def location_root(lat: float, long: float):
    # WINTER IMPROVEMENTS: eventually will add field (or make county generic with another field for type)
    # so that different boundary types are supported
    response_json = {
        "response": [],
        "county": "",
        "lat": lat,
        "long": long,
        "error": False,
        "err_msg" : ""
    }
    
    # WINTER IMPROVEMENTS: Pass in the county boundary df for the function to use properly (or totally remove function call)
    sl.set_county(response_json, lat, long)
    # WINTER IMPROVEMENTS: Include functions for each spacial boundary (that is selected)
    
    if response_json["error"]:
        raise HTTPException(status_code=400, detail=response_json["err_msg"])

    sl.filter_df(response_json, full_df)
    
    sl.summary_stats(response_json, inat_key)

    # WINTER IMPROVMENTS: store responses in an array before returning them
    return response_json