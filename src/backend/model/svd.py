import numpy as np
import pandas as pd
from sklearn.decomposition import TruncatedSVD
from load_data import main as gen_interaction

def run_svd(interaction_matrix, k):
  # truncated svd learns weights 
  model = TruncatedSVD(n_components=k, random_state=42)
  bee_embeddings = model.fit_transform(interaction_matrix)  # num_bees x k
  plant_embeddings = model.components_                      # k x num_plants

  # tells us if we've kept correct number of niches (>.80 is good)
  var_ratio = model.explained_variance_ratio_

  # dot the two embedded matrices together to fill predicted matrix
  predicted_matrix = np.dot(bee_embeddings, plant_embeddings)
  predicted_df = pd.DataFrame(
    predicted_matrix, 
    index=interaction_matrix.index, 
    columns=interaction_matrix.columns
    )
  cleaned_matrix = predicted_df.clip(lower=0.0)

  return var_ratio, cleaned_matrix

def print_log(interaction_matrix, var_ratio, predicted_matrix):
  num_bees = interaction_matrix.shape[0]
  num_plants = interaction_matrix.shape[1]
  print(f'Number of bees in data: {num_bees}\nNumber of plants in data: {num_plants}\n-----------------')
  print(f'Variance Ratio: {np.sum(var_ratio)}\n-----------------')
  print(predicted_matrix)

def save_to_csv(predicted_matrix):
  pd.DataFrame(predicted_matrix).to_csv("predicted_interactions.csv")
  print("Saved to 'predicted_interactions.csv in the root folder")

if __name__ == "__main__":
  interaction_matrix = gen_interaction()
  # number of features/niches (tested and this is the best option)
  k = 50
  var_ratio, predictions = run_svd(interaction_matrix, k)
  print_log(interaction_matrix, var_ratio, predictions)
  save_to_csv(predictions)