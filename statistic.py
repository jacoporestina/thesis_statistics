import pandas as pd
import re  

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
    match = re.search(r'(\d{8})_(High|Low)_(experiment|canopyA|canopyB)_(\d+)', file_path) # For extracting parts of the filename
    if match:
        return match.group(2), match.group(3), match.group(4)
    else:
        return 'Unknown', 'Unknown', 'Unknown'

# Loop through each file
for file in file_paths:
    # Load the file
    df = pd.read_csv(file)
    
    # Remove rows where Organ_ID starts with "organs.Internode"
    df = df[~df['Organ_ID'].str.startswith('organs.Internode')]

    # Extract density, canopy, and simulation number from the filename
    density, canopy_type, sim_number = extract_simulation_info(file)
    
    # Add the extracted information as new columns
    df['density'] = density
    df['canopy'] = canopy_type
    df['simulation'] = f'Sim{sim_number}'

    # Drop unnecessary columns
    columns_to_drop = [
        'organ_type', 'age_in_degree_days_dd of plant', 'age_in_days_d of plant',
        'order', 'dry_biomass_mg[mg]', 'dry_biomass_growth_mg for dynamic', 'SLA'
    ]
    df.drop(columns=columns_to_drop, inplace=True)
    
    # Create new column for absorbedPAR [umol m^-2 s^-1]
    df['absorbedPAR [umol m^-2 s^-1]'] = df['absorbedPAR [umol s^-1]'] / df['area_m2[m^2]']

    # Handle rank 2 separately by first summing the values for two leaves and then averaging
    rank2_df = df[df['rank'] == 2]
    numeric_columns = ['absorbedPAR [umol m^-2 s^-1]', 'area_m2[m^2]', 'absorbedPAR [umol s^-1]']
    rank2_summed = rank2_df.groupby(['density', 'canopy', 'simulation', 'plantNb']).sum().reset_index()
    rank2_averaged = rank2_summed.groupby(['density', 'canopy', 'simulation'])[numeric_columns].mean().reset_index()
    rank2_averaged['rank'] = 2  # Assigning rank 2 for merged data
    
    # Handle other ranks normally
    other_ranks_df = df[df['rank'] != 2]
    other_ranks_mean = other_ranks_df.groupby(['density', 'canopy', 'simulation', 'rank'])[numeric_columns].mean().reset_index()

    # Combine rank 2 and other ranks
    combined_df = pd.concat([rank2_averaged, other_ranks_mean], ignore_index=True)
    
    # Append the processed DataFrame to the list
    dfs.append(combined_df)

# Concatenate all dataframes into one
combined_data = pd.concat(dfs, ignore_index=True)

# Assuming 'combined_data' is your final DataFrame
combined_data = combined_data[['density', 'canopy', 'simulation', 'rank',  'area_m2[m^2]', 'absorbedPAR [umol m^-2 s^-1]']]

# Save the combined data to a new CSV
combined_data.to_csv('combined_results_simulations.csv', index=False)

print("Data processing complete. File saved as 'combined_simulation_data_filtered.csv'.")
