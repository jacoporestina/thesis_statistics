import pandas as pd
import re  
import os

# Path to the folder containing your files
folder_path = 'output_model/'

# List to store all file paths
file_paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.csv')]

# Initialize an empty list to store dataframes
dfs = []

# Function to extract repetition, density, and architecture from the filename
def extract_simulation_info(file_path):
    match = re.search(r'repetition_(\d+)_(High|Low)_(architecture[A-E]|control)', file_path)
    if match:
        return match.group(1), match.group(2), match.group(3)  # repetition, density, architecture
    else:
        return 'Unknown', 'Unknown', 'Unknown'

# Loop through each file
for file in file_paths:
    # Load the file
    df = pd.read_csv(file)
    
    # Adjust the 'rank' column by subtracting 1 from each value to start ranks from 1
    df['rank'] = df['rank'] - 1

    # Remove rows where Organ_ID starts with "organs.Internode"
    df = df[~df['Organ_ID'].str.startswith('organs.Internode')]

    # Extract repetition, density, and architecture from the filename
    repetition, density, architecture = extract_simulation_info(file)

    # Add the extracted information as new columns
    df['density'] = density
    df['architecture'] = architecture
    df['repetition'] = repetition  

    # Drop unnecessary columns
    columns_to_drop = [
        'organ_type', 'age_in_degree_days_dd of plant', 'age_in_days_d of plant',
        'order', 'dry_biomass_mg[mg]', 'dry_biomass_growth_mg for dynamic', 'SLA'
    ]
    df.drop(columns=columns_to_drop, inplace=True)
    
    # Create new column for absorbedPAR [umol m^-2 s^-1]
    df['absorbedPAR_umol_m2_s1'] = df['absorbedPAR [umol s^-1]'] / df['area_m2[m^2]']

    # Handle rank 1 separately by first summing the values for two leaves and then averaging
    rank1_df = df[df['rank'] == 1]
    numeric_columns = ['absorbedPAR_umol_m2_s1', 'area_m2[m^2]', 'absorbedPAR [umol s^-1]']
    rank1_summed = rank1_df.groupby(['density', 'architecture', 'repetition', 'plantNb']).sum().reset_index()
    rank1_averaged = rank1_summed.groupby(['density', 'architecture', 'repetition'])[numeric_columns].mean().reset_index()
    rank1_averaged['rank'] = 1 
    
    # Handle other ranks normally
    other_ranks_df = df[df['rank'] != 1]
    other_ranks_mean = other_ranks_df.groupby(['density', 'architecture', 'repetition', 'rank'])[numeric_columns].mean().reset_index()

    # Combine rank 2 and other ranks
    combined_df = pd.concat([rank1_averaged, other_ranks_mean], ignore_index=True)
    
    # Append the processed DataFrame to the list
    dfs.append(combined_df)

# Concatenate all dataframes into one
combined_data = pd.concat(dfs, ignore_index=True)

# Assuming 'combined_data' is your final DataFrame
combined_data = combined_data[['density', 'architecture', 'repetition', 'rank',  'area_m2[m^2]', 'absorbedPAR_umol_m2_s1']]

# Save the combined data to a new CSV
combined_data.to_csv('combined_results_simulations.csv', index=False)

print("Data processing complete. File saved as 'combined_simulation_data_filtered.csv'.")


# Get total light absorbed.
file_path = 'combined_results_simulations.csv' 
data = pd.read_csv(file_path)

# Group the data by 'density', 'architecture', 'repetition' and sum the specified columns
grouped_data = data.groupby(['density', 'architecture', 'repetition']).agg({
    'absorbedPAR_umol_m2_s1': 'sum',
    'area_m2[m^2]': 'sum'
}).reset_index()

# Save the aggregated data to a new CSV file
output_path = 'total_absorbedPAR.csv' 
grouped_data.to_csv(output_path, index=False)

print("Aggregation complete. Data saved to:", output_path)
