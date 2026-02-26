import numpy as np
import pandas as pd
from math import sqrt
from sklearn.metrics import mean_squared_error, r2_score
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

def get_train_test_split(interaction_matrix, test_ratio=0.2):
    """
    Masks a portion of the known interactions to create a training set.
    """
    # Convert to numpy for easier indexing
    matrix_values = interaction_matrix.values
    
    # Find indices where interactions exist (non-zero)
    nonzero_indices = np.argwhere(matrix_values > 0)
    
    # Shuffle indices to select random test points
    np.random.seed(42)
    np.random.shuffle(nonzero_indices)
    
    # Split into Train and Test
    num_test = int(len(nonzero_indices) * test_ratio)
    test_indices = nonzero_indices[:num_test]
    train_indices = nonzero_indices[num_test:]
    
    # Create the Training Matrix (copy original and mask test values)
    train_matrix = matrix_values.copy()
    
    # "Hide" the test interactions by setting them to 0
    # The tuple(...) is necessary to use the list of indices for assignment
    rows, cols = zip(*test_indices)
    train_matrix[rows, cols] = 0
    
    # Convert back to DataFrame to stay compatible with your run_svd function
    train_df = pd.DataFrame(
        train_matrix, 
        index=interaction_matrix.index, 
        columns=interaction_matrix.columns
    )
    
    return train_df, test_indices

def evaluate_model(original_matrix, predicted_matrix, test_indices):
    """
    Calculates Root Mean Square Error (RMSE) on the hidden test values.
    """
    rows, cols = zip(*test_indices)
    
    # Get the actual true values we hid
    true_values = original_matrix.values[rows, cols]
    
    # Get the values the model predicted for those spots
    predicted_values = predicted_matrix.values[rows, cols]
    
    # Calculate RMSE
    rmse = sqrt(mean_squared_error(true_values, predicted_values))
    r2 = r2_score(true_values, predicted_values)

    return rmse, r2

def print_log(interaction_matrix, var_ratio, predicted_matrix):
  num_bees = interaction_matrix.shape[0]
  num_plants = interaction_matrix.shape[1]
  print(f'Number of bees in data: {num_bees}\nNumber of plants in data: {num_plants}\n-----------------')
  print(f'Variance Ratio: {np.sum(var_ratio)}\n-----------------')
  print(predicted_matrix)

def save_to_csv(predicted_matrix):
  pd.DataFrame(predicted_matrix).to_csv("./src/data/predicted_interactions.csv")
  print("Saved to './src/data/predicted_interactions.csv")


if __name__ == "__main__":
  interaction_matrix = gen_interaction()
  
  # number of features/niches (tested and this is the best option)
  k = 50
  var_ratio, predictions = run_svd(interaction_matrix, k)
  print_log(interaction_matrix, var_ratio, predictions)
  save_to_csv(predictions)

  # Evaluate model
  train_df, test_indices = get_train_test_split(interaction_matrix)
  print(f"Masked {len(test_indices)} interactions for testing.")

  rmse, r2 = evaluate_model(interaction_matrix, predictions, test_indices)
  print("------------------------------------------------")
  print(f"Validation Results (k={k}):")
  print(f"RMSE: {rmse:.4f}")
  print(f"r2_score: {r2:.4f}")

