import pandas as pd

files = ['data_A', 'data_B', 'data_C', 'data_D']
dataframes = [pd.read_csv(f"output_{file}.csv") for file in files]
combined_data = pd.concat(dataframes, ignore_index=True)
combined_data.to_csv("combined_results.csv")
print("Results combined into combined_results.csv")