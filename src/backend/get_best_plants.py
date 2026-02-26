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
    if "iNaturalistTaxonImage" in inat_key.columns:
        plant_image_url = _normalize_string(inat_key.loc[row_mask, "iNaturalistTaxonImage"].iloc[0]) or ""
    if not common_name:
        common_name = taxon_name or f"Plant #{plant_identifier}"
    return {
        "commonName": common_name,
        "iNatTaxonName": taxon_name,
        "iNatURL": plant_image_url,
    }


def get_best_plants(response: dict, lat: float, long: float) -> None:
    """
    Update the response JSON to include 5 best plants based on interaction sums.

    TODO: Add a filter to the plants based on the allowed plants in the dictionary 
    that is also based on the latitude and longitude of the user.
    """
    try:
        predicted_interactions = pd.read_csv("../data/predicted_interactions.csv", index_col=0)

        plant_scores = predicted_interactions.sum(axis=0)

        # TODO: filter allowed_plants with dictionary here:
        # plant_scores = plant_scores[plant_scores.index.isin(allowed_plants_keys)]

        top_5_plants = plant_scores.nlargest(5).index.tolist()

        response["response"] = top_5_plants
        response["error"] = False
        response["err_msg"] = ""

    except Exception as e:
        response["response"] = []
        response["error"] = True
        response["err_msg"] = f"Error processing plant data: {str(e)}"

    return