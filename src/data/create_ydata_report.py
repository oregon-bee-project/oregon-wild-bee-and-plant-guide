import pandas as pd
from ydata_profiling import ProfileReport

df = pd.read_excel("plant_bee_data_10_23_25.xlsx")
profile = ProfileReport(df, title="Profiling Report")
profile.to_file("bee_data_report.html")


