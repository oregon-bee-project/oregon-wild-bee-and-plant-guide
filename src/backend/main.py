from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import search_by_location as sl
import get_best_plants as bp
import parse_viz as pv
import flatten_summary as fs
from create_pdf import generate_pdf_from_rows as g_pdf
from create_pdf import generate_detailed_pdf as g_detailed_pdf
import io
import csv
from fastapi.responses import StreamingResponse
import detailed_report as dr

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

@app.get("/api/detailed-report/")
def detailed_report_root(
    lat: float,
    long: float,
    region_type: str,
    species_offset: int = Query(default=0, ge=0),
    species_limit: int = Query(default=25, ge=1, le=100),
):
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

    dr.everySpeciesList(
        response_json,
        inat_key,
        filtered_df,
        bee_list_offset=species_offset,
        bee_list_limit=species_limit,
    )

    return response_json


@app.post("/api/export-detailed-pdf/")
def export_detailed_pdf(payload: dict):
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
        "err_msg": ""
    }

    filtered_df = sl.filter_df(response_json, full_df)

    if response_json["error"]:
        raise HTTPException(status_code=400, detail=response_json["err_msg"])

    dr.everySpeciesList(
        response_json,
        inat_key,
        filtered_df,
        bee_list_limit=None,
    )

    stats = response_json.get("response", {})

    if not stats:
        raise HTTPException(status_code=404, detail="No data returned for selected location.")

    title = "Detailed Bee and Plant Report"
    location = response_json["region_name"]
    pdf_buffer = g_detailed_pdf(stats, title=title, location=location, filtered_df=filtered_df)

    safe_location = location.replace(" ", "_")
    filename = f"{safe_location}_Detailed_Bee_Plant_Report.pdf"

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )

@app.get("/api/best-plants-to-plant/")
def best_plants_root(lat: float, long: float, region_type: str = "county"):
    response_json = {
        "response": [],
        "error": False,
        "err_msg": "",
        "region_type": region_type,
        "region_name": "",
        "region_key": "",
        "lat": lat,
        "long": long,
    }
    # Resolve region name for display (same as location-data); do not fail request if not found
    try:
        region_name, _ = sl.get_region_from_coordinates(lat, long, region_type)
        if region_name:
            response_json["region_name"] = region_name
    except Exception:
        pass

    # Only reccomend plants that are observed in the same ecoregion that the user selected at least once
    allowed_plants = None
    eco_filtered_df = None
    eco_response = None
    try:
        eco_response = {
            "response": [],
            "region_type": "ecoregion",
            "region_name": "",
            "lat": lat,
            "long": long,
            "error": False,
            "err_msg": "",
        }
        eco_filtered_df = sl.filter_df(eco_response, full_df)
        if (
            not eco_response.get("error")
            and eco_filtered_df is not None
            and not eco_filtered_df.empty
            and "plantINatId" in eco_filtered_df.columns
        ):
            allowed_plants = set(
                eco_filtered_df["plantINatId"]
                .dropna()
                .astype(str)
                .tolist()
            )
    except Exception:
        allowed_plants = None

    regional_bee_counts = sl.get_regional_bee_counts(eco_filtered_df) if eco_filtered_df is not None else {}
    bp.get_best_plants(response_json, lat, long, inat_key=inat_key, allowed_plant_ids=allowed_plants, regional_bee_counts=regional_bee_counts)
    # Top bees per plant from observed interactions in the same ecoregion
    plant_top_bees = sl.get_plant_top_bees(eco_filtered_df, top_n=5) if eco_filtered_df is not None else {}
    # Enrich list of plant IDs with display names, images, scores, and top bees
    raw_response = response_json.get("response") or []
    if isinstance(raw_response, list) and raw_response:
        enriched = []
        for rank, item in enumerate(raw_response[:5], start=1):
            plant_id = item.get("id", item) if isinstance(item, dict) else item
            score = item.get("score") if isinstance(item, dict) else None
            display = bp.lookup_plant_display(inat_key, plant_id)
            pid_str = str(plant_id)
            top_bees = plant_top_bees.get(pid_str, [])
            enriched.append({
                "rank": rank,
                "commonName": display["commonName"],
                "iNatTaxonName": display["iNatTaxonName"],
                "iNatURL": display["iNatURL"],
                "score": score,
                "topBees": top_bees,
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
    
