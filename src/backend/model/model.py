"""
Implement XGBoost Regressor Model
with 5 fold cross validation

metric: R^2 
Goal: R^2 > 0.85
"""

from load_data import get_clean_observation_dataframe
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap

from sklearn.compose import ColumnTransformer
from sklearn.metrics import r2_score
from sklearn.model_selection import cross_val_score, KFold, train_test_split
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler
from sklearn.pipeline import Pipeline
from xgboost import XGBRegressor


def train_5fold_XGBoost(df: pd.DataFrame, parameters: dict = None):
    """
    Train xgboost regressor using 5 fold 
    cross validation
    """
    X = df.drop(labels="bee_shannon_diversity_index", axis="columns")
    y = df["bee_shannon_diversity_index"]

    # get numerical and categorical columns
    num_cols = X.select_dtypes(include=["float64"]).columns.tolist()
    cat_cols = X.select_dtypes(include=["int64"]).columns.tolist()

    # create preprocessors
    num_processor = MinMaxScaler((0,1))
    cat_processor = "passthrough" # columns already contain one-hot-encoded counts for each plant and pollinator

    # preprocess data
    preprocessor = ColumnTransformer([
        ('num', num_processor, num_cols),
        ('cat', cat_processor, cat_cols)
    ])

    # create xgb model
    if parameters:
        model = XGBRegressor(**parameters)
    else:
        model = XGBRegressor()

    # create data preprocessing and modeling
    pipeline = Pipeline(steps=[
        ("preprocess", preprocessor),
        ("xgb", model)
    ])

    # Perform 5-fold cross-validation
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    scores = cross_val_score(pipeline, X, y, cv=kf)
    print(f"Cross-validation R^2 scores {scores}")
    print(f"Average R^2 score {scores.mean()}")


def train_XGBoost(df: pd.DataFrame, parameters: dict = None, plot: bool = False) -> XGBRegressor:
    """
    Train xgboost regressor using 80-20 
    train test split
    """
    X = df.drop(labels="bee_shannon_diversity_index", axis="columns")
    y = df["bee_shannon_diversity_index"]

    # get numerical and categorical columns
    num_cols = X.select_dtypes(include=["float64"]).columns.tolist()
    cat_cols = X.select_dtypes(include=["int64"]).columns.tolist()

    # create preprocessors
    num_processor = MinMaxScaler((0,1))
    cat_processor = "passthrough" # columns already contain one-hot-encoded counts for each plant and pollinator 

    # preprocess data
    preprocessor = ColumnTransformer([
        ('num', num_processor, num_cols),
        ('cat', cat_processor, cat_cols)
    ])
    preprocessor.fit(X)
    preprocessed_X = preprocessor.transform(X)

    # 80/20 train-test split
    X_train, X_test, y_train, y_test = train_test_split(preprocessed_X, y, test_size=0.2, random_state=42)

    # create xgb model
    if parameters:
        model = XGBRegressor(**parameters)
    else:
        model = XGBRegressor()
    model.fit(X_train, y_train)

    # get model performance
    predictions = model.predict(X_test)
    score = r2_score(predictions, y_test)
    print(f"R^2 score {score}")

    # get new feature names for SHAP
    if plot:
        # num_feature_names = preprocessor.named_transformers_['num'].get_feature_names_out(num_cols)
        # cat_feature_names = preprocessor.named_transformers_['cat'].get_feature_names_out(cat_cols)

        # all_feature_names = np.concatenate([num_feature_names, cat_feature_names])

        # create SHAP bar plot with feature importances
        explainer = shap.Explainer(model, feature_names=X.columns)
        shap_values = explainer(X_test)

        plt.figure(figsize=(8, 6))
        shap.plots.bar(shap_values)
        plt.savefig("shap_xgboost.png", dpi=300, bbox_inches="tight")
        plt.close()

    return model


def get_parameters() -> dict:
    """
    return parameters for 
    xgboost regressor
    """
    default_parameters = {
        "objective":'reg:squarederror',
        "n_estimators":100,
        "learning_rate":0.1,
        "max_depth":3,
        "subsample":1,
        "colsample_bytree":1,
        "gamma":0,
        "min_child_weight":1,
        "reg_alpha":0,
        "reg_lambda":1,
        "random_state":0
    }
    
    return default_parameters


def main() -> None:
    df = get_clean_observation_dataframe()
    params = get_parameters()
    xgb = train_XGBoost(df, plot=True)
    # xgb = train_XGBoost(df, params, True)
    # train_5fold_XGBoost(df)
    # train_5fold_XGBoost(df, params)


if __name__ == "__main__":
    main()