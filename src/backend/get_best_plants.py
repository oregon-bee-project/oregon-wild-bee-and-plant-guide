import json
import pandas as pd

def _normalize_string(value):
    if value is None:
        return None
    if isinstance(value, float) and pd.isna(value):
        return None
    if isinstance(value, str):
        trimmed = value.strip()
        return trimmed or None
    return str(value)


def lookup_plant_display(inat_key, plant_id):
    """
    Look up display fields for a plant by iNaturalist ID.
    Returns dict with commonName, iNatTaxonName, iNatURL (empty string if not found).
    """
    common_name = ""
    taxon_name = ""
    plant_image_url = ""
    plant_identifier = _normalize_string(plant_id)
    if not plant_identifier:
        return {"commonName": "", "iNatTaxonName": "", "iNatURL": ""}
    try:
        row_mask = inat_key["id"] == int(float(plant_identifier))
    except (ValueError, TypeError):
        return {"commonName": plant_identifier, "iNatTaxonName": "", "iNatURL": ""}
    if not row_mask.any():
        return {"commonName": f"Plant #{plant_identifier}", "iNatTaxonName": "", "iNatURL": ""}
    if "commonName" in inat_key.columns:
        common_name = _normalize_string(inat_key.loc[row_mask, "commonName"].iloc[0]) or ""
    if "scientificName" in inat_key.columns:
        taxon_name = _normalize_string(inat_key.loc[row_mask, "scientificName"].iloc[0]) or ""
    if not taxon_name and "name" in inat_key.columns:
        taxon_name = _normalize_string(inat_key.loc[row_mask, "name"].iloc[0]) or ""
    if not taxon_name and "iNaturalistTaxonName" in inat_key.columns:
        taxon_name = _normalize_string(inat_key.loc[row_mask, "iNaturalistTaxonName"].iloc[0]) or ""
    if "iNaturalistTaxonImage" in inat_key.columns:
        plant_image_url = _normalize_string(inat_key.loc[row_mask, "iNaturalistTaxonImage"].iloc[0]) or ""
    if not common_name:
        common_name = taxon_name or f"Plant #{plant_identifier}"
    return {
        "commonName": common_name,
        "iNatTaxonName": taxon_name,
        "iNatURL": plant_image_url,
    }


def _load_oregon_flora_names():
    """Load the set of scientific names from oregon_flora_plants.json."""
    with open("../data/oregon_flora_plants.json", encoding="utf-8") as f:
        plants = json.load(f)
    return {p["scientific_name"].strip().lower() for p in plants}


def get_best_plants(
    response: dict,
    lat: float,
    long: float,
    inat_key=None,
    allowed_plant_ids=None,
    regional_bee_counts=None,
) -> None:
    """
    Update the response JSON to include 5 best plants based on interaction sums,
    filtered to only plants found in the Oregon Flora garden list and,
    when provided, to plants observed at least once in the user's Level III
    ecoregion (allowed_plant_ids).
    """
    try:
        predicted_interactions = pd.read_csv("../data/predicted_interactions.csv", index_col=0)

        # Weight each bee row by how frequently it is observed in the region.
        # Bees not seen in the region get weight 0 and are excluded from scoring,
        # so plants that attract locally-present bees rank higher.
        if regional_bee_counts:
            bee_ids = predicted_interactions.index.astype(str)
            weights = pd.Series(
                [regional_bee_counts.get(b, 0) for b in bee_ids],
                index=predicted_interactions.index,
                dtype=float,
            )
            regional_mask = weights > 0
            if regional_mask.any():
                plant_scores = (
                    predicted_interactions[regional_mask]
                    .multiply(weights[regional_mask], axis=0)
                    .sum(axis=0)
                )
            else:
                plant_scores = predicted_interactions.sum(axis=0)
        else:
            plant_scores = predicted_interactions.sum(axis=0)

        # Filter to plants that appear in Oregon Flora
        if inat_key is not None:
            oregon_names = _load_oregon_flora_names()
            allowed_ids = []
            for pid in plant_scores.index:
                try:
                    row = inat_key[inat_key["id"] == int(float(pid))]
                    if not row.empty:
                        taxon = row["iNaturalistTaxonName"].iloc[0]
                        if isinstance(taxon, str) and taxon.strip().lower() in oregon_names:
                            allowed_ids.append(pid)
                except (ValueError, TypeError):
                    continue
            plant_scores = plant_scores[plant_scores.index.isin(allowed_ids)]

        # Further restrict to plants that appear at least once in the user's
        # Level III ecoregion, if an allowed set is provided.
        if allowed_plant_ids:
            allowed_set = {str(pid) for pid in allowed_plant_ids}
            plant_scores = plant_scores[plant_scores.index.astype(str).isin(allowed_set)]

        # If no plants remain after filtering, surface a clear error.
        if plant_scores.empty:
            response["response"] = []
            response["error"] = True
            # Only override err_msg if nothing more specific was set earlier.
            if not response.get("err_msg"):
                response["err_msg"] = "No plants found in the selected ecoregion"
            return

        top_5_plants = plant_scores.nlargest(5).index.tolist()
        response["response"] = [
            {"id": pid, "score": float(plant_scores[pid])}
            for pid in top_5_plants
        ]
        response["error"] = False
        response["err_msg"] = ""

    except Exception as e:
        response["response"] = []
        response["error"] = True
        response["err_msg"] = f"Error processing plant data: {str(e)}"

    return