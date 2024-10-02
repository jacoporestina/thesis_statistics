import pandas as pd
import re  
import os

# Path to the folder containing your files
folder_path = 'output_model/'

# List to store all file paths
file_paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.csv')]

# Initialize two lists to store dataframes by density
dfs_high = []
dfs_low = []

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
    
    # Append the processed DataFrame to the appropriate list based on density
    if density == 'High':
        dfs_high.append(combined_df)
    elif density == 'Low':
        dfs_low.append(combined_df)

# Concatenate all High density dataframes into one
combined_high = pd.concat(dfs_high, ignore_index=True)

# Concatenate all Low density dataframes into one
combined_low = pd.concat(dfs_low, ignore_index=True)

# Assuming 'combined_high' and 'combined_low' are your final DataFrames
combined_high = combined_high[['density', 'architecture', 'repetition', 'rank',  'area_m2[m^2]', 'absorbedPAR_umol_m2_s1']]
combined_low = combined_low[['density', 'architecture', 'repetition', 'rank',  'area_m2[m^2]', 'absorbedPAR_umol_m2_s1']]

# Save the combined data to two new CSV files
combined_high.to_csv('combined_high_ranks.csv', index=False)
combined_low.to_csv('combined_low_ranks.csv', index=False)

print("Data processing complete. Files saved as 'combined_high_density.csv' and 'combined_low_density.csv'.")

# Create total absorbedPAR files for both high and low density.
# Define a function to process and aggregate the data
def aggregate_absorbed_PAR(file_path, output_path):
    # Load the data
    data = pd.read_csv(file_path)
    
    # Group the data by 'density', 'architecture', 'repetition' and sum the specified columns
    grouped_data = data.groupby(['density', 'architecture', 'repetition']).agg({
        'absorbedPAR_umol_m2_s1': 'sum',
        'area_m2[m^2]': 'sum'
    }).reset_index()
    
    # Save the aggregated data to a new CSV file
    grouped_data.to_csv(output_path, index=False)
    print(f"Aggregation complete. Data saved to: {output_path}")

# File paths for high and low density data
file_paths = {
    'high': ('combined_high_ranks.csv', 'high_total_absorbedPAR.csv'),
    'low': ('combined_low_ranks.csv', 'low_total_absorbedPAR.csv')
}

# Loop through both high and low files and apply the aggregation
for density, (input_file, output_file) in file_paths.items():
    aggregate_absorbed_PAR(input_file, output_file)