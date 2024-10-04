import pandas as pd
import re
import os

# Specify folder path and create a list of all csv files contained in the folder path.
folder_path = "output_sensors/"
file_paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.csv')]

# Initialize two lists to store dataframes by density
dfs_high = []
dfs_low = []

# Function to extract repetition, density, and architecture from the filename
def extract_simulation_info(file_path):
    match = re.search(r'sensors_export_below_canopy\.csv_repetition_(\d+)_(High|Low)_(architecture[A-D]|control)', file_path)
    if match:
        return match.group(1), match.group(2), match.group(3)  # repetition, density, architecture
    else:
        return 'Unknown', 'Unknown', 'Unknown'
    
# Loop through each file.
for file in file_paths:
    # Load the file into a pandas dataframe.
    df = pd.read_csv(file)
    
    # Calculate mean of all rows for the specified numeric columns
    numeric_columns = [' Tile z cohordinate [m]', 'absorbedPARTile [umol^s-1]']
    mean_values = df[numeric_columns].mean()  # Mean values for each numeric column
    
    # Convert mean_values to a DataFrame to keep a single row
    mean_df = pd.DataFrame([mean_values])

    # Extract repetition, density, and architecture from the filename
    repetition, density, architecture = extract_simulation_info(file)

    # Add the extracted information as new columns
    mean_df['density'] = density
    mean_df['architecture'] = architecture
    mean_df['repetition'] = repetition  
    
    # Calculate the new column for absorbedPAR micromols m-2 s-1 (using mean values)
    mean_df['absorbedPAR_umol_m2_s1'] = mean_df['absorbedPARTile [umol^s-1]'] / mean_df[' Tile z cohordinate [m]']
    
    # Drop unnecessary columns from the mean_df
    mean_df.drop(columns=[' Tile z cohordinate [m]', 'absorbedPARTile [umol^s-1]'], inplace=True)
    
    # Append the processed DataFrame to the appropriate list based on density
    if density == 'High':
        dfs_high.append(mean_df)
    elif density == 'Low':
        dfs_low.append(mean_df)

# Concatenate all high and low density dataframes.
combined_high = pd.concat(dfs_high, ignore_index=True)
combined_low = pd.concat(dfs_low, ignore_index=True)

# Assuming 'combined_data' is your final DataFrame
combined_high = combined_high[['density', 'architecture', 'repetition', 'absorbedPAR_umol_m2_s1']]
combined_low = combined_low[['density', 'architecture', 'repetition', 'absorbedPAR_umol_m2_s1']]

# Save the combined data to a new CSV
combined_high.to_csv('combined_high_sensors.csv', index=False)
combined_low.to_csv('combined_low_sensors.csv', index=False)

print("Data processing complete.")
