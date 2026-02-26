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
        "lat": lat,
        "long": long,
        "error": False,
        "err_msg" : ""
    }
    
    filtered_df = sl.filter_df(response_json, full_df)

    if response_json["error"]:
        raise HTTPException(status_code=400, detail=response_json["err_msg"])
    
    sl.summary_stats(response_json, inat_key, filtered_df)

    return response_json

@app.get("/api/best-plants-to-plant/")
def best_plants_root(lat: float, long: float, region_type: str = "county"):
    response_json = {
        "response": [],
        "error": False,
        "err_msg": "",
        "region_name": "",
        "region_key": "",
        "lat": lat,
        "long": long,
    }
    # Resolve region name for display (same as location-data); do not fail request if not found
    region_lookup = {"lat": lat, "long": long, "region_type": region_type, "error": False, "err_msg": ""}
    sl.set_region_name(region_lookup)
    if not region_lookup.get("error"):
        response_json["region_name"] = region_lookup.get("region_name", "")
        response_json["region_key"] = region_lookup.get("region_key", "")
    bp.get_best_plants(response_json, lat, long)
    # Enrich list of plant IDs with display names and images from taxa lookup
    ids = response_json.get("response") or []
    if isinstance(ids, list) and ids:
        enriched = []
        for rank, plant_id in enumerate(ids[:5], start=1):
            display = bp.lookup_plant_display(inat_key, plant_id)
            enriched.append({
                "rank": rank,
                "commonName": display["commonName"],
                "iNatTaxonName": display["iNatTaxonName"],
                "iNatURL": display["iNatURL"],
            })
        response_json["response"] = enriched
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
        "region_name": "",
        "lat": lat,
        "long": long,
        "error": False,
        "err_msg" : ""
    }

    # Run your pipeline
    

    filtered_df = sl.filter_df(response_json, full_df)

    if response_json["error"]:
        raise HTTPException(status_code=400, detail=response_json["err_msg"])
    
    sl.summary_stats(response_json, inat_key, filtered_df)

    summary_stats = response_json.get("response", [])
    rows = fs.flatten_summary(summary_stats)

    if not rows:
        raise HTTPException(status_code=404, detail="No data returned for selected location.")

    # Generate PDF
    title = "Common Bee and Plant Report"
    location = response_json["region_name"]
    pdf_buffer = g_pdf(rows, title=title, location=location)

    safe_location = location.replace(" ","_")
    filename = f"{safe_location}_Common_Bee_Plant_Report.pdf"

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )
    
