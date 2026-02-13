from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import search_by_location as sl
import get_best_plants as bp
import parse_viz as pv
import flatten_summary as fs
from create_pdf import generate_pdf_from_rows as g_pdf
import io
import csv
from fastapi.responses import StreamingResponse


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

@app.get("/api/best-plants-to-plant/")
def best_plants_root(lat: float, long: float): # is the root naming convention standard
    response_json = {
        "response": [],
        "error": False,
        "err_msg" : ""
    }
    # TODO: Finish implementing this
    bp.get_best_plants(response_json, lat, long)
    
    # #region agent log
    import json, os
    log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".cursor", "debug.log")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "a") as f:
        f.write(json.dumps({"id":"log_backend_response","timestamp":int(__import__("time").time()*1000),"location":"main.py:72","message":"Backend returning response_json","data":{"response":response_json.get("response"),"response_length":len(response_json.get("response",[])),"error":response_json.get("error"),"response_type":str(type(response_json.get("response")))},"runId":"run1","hypothesisId":"C"})+"\n")
    # #endregion
    
    return response_json

@app.post("/api/export-pdf/")
def export_pdf(payload: dict):
    selected = payload.get("selectedCoords")
    if not selected:
        raise HTTPException(status_code=400, detail="Missing selectedCoords in request.")

    lat = selected.get("lat")
    long = selected.get("lng")
    if lat is None or long is None:
        raise HTTPException(status_code=400, detail="Invalid coordinates provided.")

    response_json = {
        "response": [],
        "region_type": payload.get("region_type"),
        "lat": lat,
        "long": long,
        "error": False,
        "err_msg": ""
    }

    # Run your pipeline
    sl.set_region_name(response_json)
    if response_json["error"]:
        raise HTTPException(status_code=400, detail=response_json["err_msg"])

    sl.filter_df(response_json, full_df)
    sl.summary_stats(response_json, inat_key)

    summary_stats = response_json.get("response", [])
    rows = fs.flatten_summary(summary_stats)

    if not rows:
        raise HTTPException(status_code=404, detail="No data returned for selected location.")

    # Generate PDF
    pdf_buffer = g_pdf(rows, title="Bee Data Export")

    filename = "beedata_export.pdf"

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )
    
