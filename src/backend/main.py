from fastapi import FastAPI
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


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/api/location-data/")
def location_root(lat: float, long: float):
    response_json = {
        "response": [],
        "county": "",
        "error": False,
        "err_msg" : ""
    }
    
    sl.set_county(response_json, lat, long)
    
    if response_json["error"]:
        return response_json

    sl.filter_df(response_json, full_df)
    
    sl.summary_stats(response_json, inat_key)
    
    return response_json