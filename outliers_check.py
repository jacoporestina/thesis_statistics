import pandas as pd
import matplotlib.pyplot as plt

# Load the dataset
data = pd.read_csv('combined_high_ranks.csv')

# Process data by rank.
for rank in data['rank'].unique():
    # Filter data for the current rank.
    rank_data = data[data['rank'] == rank]

# Quick look at data summary to understand ranges and distributions
print(rank_data)
print(rank_data.describe())
