from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import search_by_location as sl
import parse_viz as pv
import flatten_summary as fs
import io
import csv

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

# WINTER IMPROVEMENTS: include an array of previous filtered dataframes, so that user can print reports
# from history or other processes can resuse data quickly

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.api_route("/health", methods=["GET", "HEAD"])
def health():
    """
    Health check endpoint to ping service and prevent it
    from spinning down when there is low activity.

    Used by UptimeRobot (uses HEAD method to ping).
    """
    return {"status": "live"}

@app.get("/api/location-data/")
def location_root(lat: float, long: float, region_type: str):
    response_json = {
        "response": [],
        "region_type": region_type,
        "region_name": "",
        "region_key": "",
        "lat": lat,
        "long": long,
        "error": False,
        "err_msg" : ""
    }
    
    sl.set_region_name(response_json)
    
    if response_json["error"]:
        raise HTTPException(status_code=400, detail=response_json["err_msg"])

    sl.filter_df(response_json, full_df)
    
    sl.summary_stats(response_json, inat_key)

    return response_json

# Export CSV endpoint - works for Prompt 1 "Common Bees"
@app.post("/api/export-csv/")
def export_csv(payload: dict):
    # Export works based off locationData structure
    selected = payload.get("selectedCoords")
    if not selected:
        raise HTTPException(status_code=400, detail="Missing selectedCoords in request.")
    lat = selected.get("lat")
    long = selected.get("lng")
    if lat is None or long is None:
        raise HTTPException(status_code=400, detail="Invalid coordinates provided.")
    # Create structure your existing functions expect
    response_json = {
        "response": [],
        "county": "",
        "lat": lat,
        "long": long,
        "error": False,
        "err_msg": ""
    }
    # --- Run your full backend pipeline ---
    sl.set_county(response_json, lat, long)

    if response_json["error"]:
        raise HTTPException(status_code=400, detail=response_json["err_msg"])

    sl.filter_df(response_json, full_df)
    sl.summary_stats(response_json, inat_key)

    summary_stats = response_json.get("response", [])
    print("Summary Stats:", summary_stats)
    rows = fs.flatten_summary(summary_stats)

    if not rows:
        raise HTTPException(status_code=404, detail="No data returned for selected location.")
    
    output = io.StringIO()
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["Metric", "Value"])
    writer.writeheader()
    writer.writerows(rows)

    output.seek(0)
    filename = 'beedata_export.csv'
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )