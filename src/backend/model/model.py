from load_data import get_clean_observation_dataframe

"""
Models to try:

xgboost regression
plsr

metric: R^2 
Goal: R^2 > 0.85
"""

def main() -> None:
    df = get_clean_observation_dataframe()
    print(df.head())


if __name__ == "__main__":
    main()