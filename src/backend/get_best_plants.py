import pandas as pd

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