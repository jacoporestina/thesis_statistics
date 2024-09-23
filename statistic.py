import pandas as pd
import re  # For extracting parts of the filename

# List of file paths for each simulation
file_paths = [
    'output_model/20231114_High_experiment_1.csv', 'output_model/20231114_High_canopyA_1.csv', 
    'output_model/20231114_High_canopyB_1.csv', 'output_model/20231114_Low_experiment_1.csv',
    'output_model/20231114_Low_canopyA_1.csv', 'output_model/20231114_Low_canopyB_1.csv',
    'output_model/20231114_High_experiment_2.csv', 'output_model/20231114_High_canopyA_2.csv', 
    'output_model/20231114_High_canopyB_2.csv', 'output_model/20231114_Low_experiment_2.csv',
    'output_model/20231114_Low_canopyA_2.csv', 'output_model/20231114_Low_canopyB_2.csv'
]

# Initialize an empty list to store dataframes
dfs = []

# Function to extract density, canopy, and simulation number from the filename
def extract_simulation_info(file_path):
    # Use regular expressions to capture relevant parts of the filename
    match = re.search(r'(\d{8})_(High|Low)_(experiment|canopyA|canopyB)_(\d+)', file_path)
    
    if match:
        # Extract density, canopy type, and simulation number
        density = match.group(2)
        canopy_type = match.group(3)
        sim_number = match.group(4)
        
        return density, canopy_type, sim_number
    else:
        return 'Unknown', 'Unknown', 'Unknown'

# Loop through each file
for file in file_paths:
    # Load the file
    df = pd.read_csv(file)
    
    # Extract density, canopy, and simulation number from the filename
    density, canopy_type, sim_number = extract_simulation_info(file)
    
    # Add the extracted information as new columns
    df['density'] = density
    df['canopy'] = canopy_type
    df['simulation'] = f'Sim{sim_number}'  # Adding 'Sim' as a prefix for the simulation number
    
    # Reorder columns to place density, canopy, and simulation in the desired order
    cols = df.columns.tolist()  # Get a list of all columns
    cols.insert(2, cols.pop(cols.index('density')))
    cols.insert(3, cols.pop(cols.index('canopy')))
    cols.insert(4, cols.pop(cols.index('simulation')))
    df = df[cols]  # Reorder the dataframe with the new column order
    
    # Remove rows where Organ_ID starts with "organs.Internode"
    df = df[~df['Organ_ID'].str.startswith('organs.Internode')]
    
    # Append the dataframe to the list
    dfs.append(df)

# Concatenate all dataframes into one
combined_data = pd.concat(dfs, ignore_index=True)

# Save the combined data to a new CSV if needed
combined_data.to_csv('combined_simulation_data_filtered.csv', index=False)

print("Data processing complete. File saved as 'combined_simulation_data_filtered.csv'.")
