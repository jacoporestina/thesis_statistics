import pandas as pd
import re  
import os
import matplotlib.pyplot as plt
import numpy as np

'''PART 1: COMBINE OUTPUT SIMULATIONS IN A BIGGER DATASET FOR ANALYSIS.'''
# Path to the folder containing your files
folder_path = 'output_model/'

# List to store all file paths
file_paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.csv')]

# Initialize two lists to store dataframes by density
dfs_high = []
dfs_low = []

# Function to extract repetition, density, and architecture from the filename
def extract_simulation_info(file_path):
    match = re.search(r'repetition_(\d+)_(High|Low)_(architecture[A-D]|control)', file_path)
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
combined_high.to_csv('combined_files/combined_high_ranks.csv', index=False)
combined_low.to_csv('combined_files/combined_low_ranks.csv', index=False)

print("Data processing complete. Files saved as 'combined_high_density.csv' and 'combined_low_density.csv'.")


'''PART 2: CHECK AND ELIMINATE OUTLIERS, CREATE BOXPLOT OF DATA (ORIGINAL AND CLEANED).'''
# Function to process data, detect outliers, generate boxplots, and save results
def process_ranks_data(input_file, output_cleaned_file, output_outliers_file, output_boxplot_folder, density_label):
    # Create folder for boxplots if it doesn't exist
    if not os.path.exists(output_boxplot_folder):
        os.makedirs(output_boxplot_folder)

    # Load the dataset
    data = pd.read_csv(input_file)

    # Initialize empty DataFrames to store cleaned data and outliers
    cleaned_data = pd.DataFrame()
    outliers = pd.DataFrame()

    # Process data by rank
    for rank in data['rank'].unique():
        # Filter data for the current rank
        rank_data = data[data['rank'] == rank]
        
        # Detect and remove outliers for each architecture within this rank
        for architecture in rank_data['architecture'].unique():
            # Filter data for the current architecture within the current rank
            arch_data = rank_data[rank_data['architecture'] == architecture]

            # Calculate Q1, Q3, and IQR
            multiplier = 1.5
            Q1 = arch_data['absorbedPAR_umol_m2_s1'].quantile(0.25)
            Q3 = arch_data['absorbedPAR_umol_m2_s1'].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - multiplier * IQR
            upper_bound = Q3 + multiplier * IQR

            # Identify and remove outliers
            is_outlier = (arch_data['absorbedPAR_umol_m2_s1'] < lower_bound) | (arch_data['absorbedPAR_umol_m2_s1'] > upper_bound)
            arch_outliers = arch_data[is_outlier]
            arch_data_cleaned = arch_data[~is_outlier]

            # Append the cleaned data and outliers
            cleaned_data = pd.concat([cleaned_data, arch_data_cleaned], ignore_index=True)
            outliers = pd.concat([outliers, arch_outliers], ignore_index=True)

        # Generate and save boxplot with outliers for the current rank
        plt.figure(figsize=(10, 6))
        rank_data.boxplot(column='absorbedPAR_umol_m2_s1', by='architecture', grid=False)
        plt.title(f'Boxplot of Absorbed PAR by Architecture for Rank {rank} ({density_label})')
        plt.suptitle('')
        plt.xlabel('Architecture')
        plt.ylabel('Absorbed PAR (umol m-2 s-1)')
        plt.savefig(os.path.join(output_boxplot_folder, f'{density_label}_rank_{rank}_with_outliers.png'))
        plt.close()

    # Save the cleaned data and outliers to CSV files
    cleaned_data.to_csv(output_cleaned_file, index=False)
    outliers.to_csv(output_outliers_file, index=False)

    # Print summary
    print(f"Outliers removed and saved to '{output_outliers_file}'")
    print(f"Cleaned data saved to '{output_cleaned_file}'")
    print(f"Boxplots with outliers saved in '{output_boxplot_folder}'")

    # Generate and save boxplots for cleaned data
    for rank in cleaned_data['rank'].unique():
        rank_data_cleaned = cleaned_data[cleaned_data['rank'] == rank]
        plt.figure(figsize=(10, 6))
        rank_data_cleaned.boxplot(column='absorbedPAR_umol_m2_s1', by='architecture', grid=False)
        plt.title(f'Cleaned Boxplot of Absorbed PAR by Architecture for Rank {rank} ({density_label})')
        plt.suptitle('')
        plt.xlabel('Architecture')
        plt.ylabel('Absorbed PAR (umol m-2 s-1)')
        plt.savefig(os.path.join(output_boxplot_folder, f'{density_label}_rank_{rank}_cleaned.png'))
        plt.close()

    print(f"Cleaned boxplots saved in '{output_boxplot_folder}'")


# Define file paths and labels for high and low density datasets
datasets = [
    {
        'input_file': 'combined_files/combined_high_ranks.csv',
        'output_cleaned_file': 'combined_files/combined_high_ranks_cleaned.csv',
        'output_outliers_file': 'combined_files/combined_high_ranks_outliers.csv',
        'output_boxplot_folder': 'boxplots/high_ranks',
        'label': 'High Density'
    },
    {
        'input_file': 'combined_files/combined_low_ranks.csv',
        'output_cleaned_file': 'combined_files/combined_low_ranks_cleaned.csv',
        'output_outliers_file': 'combined_files/combined_low_ranks_outliers.csv',
        'output_boxplot_folder': 'boxplots/low_ranks',
        'label': 'Low Density'
    }
]

# Process each dataset using the function
for dataset in datasets:
    process_ranks_data(
        dataset['input_file'],
        dataset['output_cleaned_file'],
        dataset['output_outliers_file'],
        dataset['output_boxplot_folder'],
        dataset['label']
    )

print("Processing complete for all datasets.")


'''PART 3: CREATE DATASET FOR TOTAL ABSORBED PAR FOR EACH PLANT IN HIGH AND LOW DENSITY.'''
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
    'high': ('combined_files/combined_high_ranks.csv', 'combined_files/combined_total_absorbedPAR_high.csv'),
    'low': ('combined_files/combined_low_ranks.csv', 'combined_files/combined_total_absorbedPAR_low.csv')
}

# Loop through both high and low files and apply the aggregation
for density, (input_file, output_file) in file_paths.items():
    aggregate_absorbed_PAR(input_file, output_file)


'''PART 4: OUTLIERS CHECK AND BOXPLOT GENERATION FO ORIGINAL AND CLEANED DATA OF TOTAL ABSORBED PAR PER PLANT.'''
# Function to detect outliers, generate boxplots (original and cleaned data), and save results
def handle_outliers_and_boxplots(input_file, output_cleaned_file, output_outliers_file, output_boxplot_folder, dataset_label):
    # Create folder for boxplots if it doesn't exist
    if not os.path.exists(output_boxplot_folder):
        os.makedirs(output_boxplot_folder)

    # Load the dataset
    data = pd.read_csv(input_file)

    # Initialize empty DataFrames to store cleaned data and outliers
    cleaned_data = pd.DataFrame()
    outliers = pd.DataFrame()

    # Detect and remove outliers for each architecture
    for architecture in data['architecture'].unique():
        # Filter data for the current architecture
        arch_data = data[data['architecture'] == architecture]

        # Calculate Q1, Q3, and IQR
        multiplier = 1.5
        Q1 = arch_data['absorbedPAR_umol_m2_s1'].quantile(0.25)
        Q3 = arch_data['absorbedPAR_umol_m2_s1'].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - multiplier * IQR
        upper_bound = Q3 + multiplier * IQR

        # Identify outliers and filter them
        is_outlier = (arch_data['absorbedPAR_umol_m2_s1'] < lower_bound) | (arch_data['absorbedPAR_umol_m2_s1'] > upper_bound)
        arch_outliers = arch_data[is_outlier]
        arch_data_cleaned = arch_data[~is_outlier]

        # Append the cleaned data and outliers
        cleaned_data = pd.concat([cleaned_data, arch_data_cleaned], ignore_index=True)
        outliers = pd.concat([outliers, arch_outliers], ignore_index=True)

    # Generate and save original boxplot (before outlier removal)
    plt.figure(figsize=(10, 6))
    data.boxplot(column='absorbedPAR_umol_m2_s1', by='architecture', grid=False)
    plt.title(f'Original Boxplot of Absorbed PAR ({dataset_label})')
    plt.suptitle('')
    plt.xlabel('Architecture')
    plt.ylabel('Absorbed PAR (umol m-2 s-1)')
    plt.savefig(os.path.join(output_boxplot_folder, f'{dataset_label}_original.png'))
    plt.close()

    # Generate and save cleaned boxplot (after outlier removal)
    plt.figure(figsize=(10, 6))
    cleaned_data.boxplot(column='absorbedPAR_umol_m2_s1', by='architecture', grid=False)
    plt.title(f'Cleaned Boxplot of Absorbed PAR ({dataset_label})')
    plt.suptitle('')
    plt.xlabel('Architecture')
    plt.ylabel('Absorbed PAR (umol m-2 s-1)')
    plt.savefig(os.path.join(output_boxplot_folder, f'{dataset_label}_cleaned.png'))
    plt.close()

    # Save the cleaned data and outliers
    cleaned_data.to_csv(output_cleaned_file, index=False)
    outliers.to_csv(output_outliers_file, index=False)

    # Print summary
    print(f"Outliers detected and saved to '{output_outliers_file}'")
    print(f"Cleaned data saved to '{output_cleaned_file}'")
    print(f"Boxplots saved in '{output_boxplot_folder}'")


# Define file paths and labels for high and low density datasets
datasets = [
    {
        'input_file': 'combined_files/combined_total_absorbedPAR_high.csv',
        'output_cleaned_file': 'combined_files/combined_total_absorbedPAR_high_cleaned.csv',
        'output_outliers_file': 'combined_files/combined_total_absorbedPAR_high_outliers.csv',
        'output_boxplot_folder': 'boxplots/total_absorbedPAR_high',
        'label': 'High Density'
    },
    {
        'input_file': 'combined_files/combined_total_absorbedPAR_low.csv',
        'output_cleaned_file': 'combined_files/combined_total_absorbedPAR_low_cleaned.csv',
        'output_outliers_file': 'combined_files/combined_total_absorbedPAR_low_outliers.csv',
        'output_boxplot_folder': 'boxplots/total_absorbedPAR_low',
        'label': 'Low Density'
    }
]

# Process each dataset using the function
for dataset in datasets:
    handle_outliers_and_boxplots(
        dataset['input_file'],
        dataset['output_cleaned_file'],
        dataset['output_outliers_file'],
        dataset['output_boxplot_folder'],
        dataset['label']
    )

print("Processing complete for all datasets.")


'''PART 5: LOG TRANFORMATION OF DATA.'''

import os
import pandas as pd
import numpy as np

# Define the folder paths
input_folder = 'combined_files/'
output_folder = 'log_transformed/'

# Create output folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Loop through the files in the input folder
for file_name in os.listdir(input_folder):
    if file_name.endswith('.csv'):
        # Load the CSV file
        file_path = os.path.join(input_folder, file_name)
        data = pd.read_csv(file_path)

        # Log transformation (base 10) of the 'absorbedPAR_umol_m2_s1' column
        if 'absorbedPAR_umol_m2_s1' in data.columns:
            # Apply log transformation
            data['log_absorbedPAR_umol_m2_s1'] = np.log(data['absorbedPAR_umol_m2_s1'])

            # Save the transformed data to a new file in the output folder
            output_file_path = os.path.join(output_folder, file_name)
            data.to_csv(output_file_path, index=False)

            print(f"Log transformation applied and saved for {file_name}")

print("All files processed and saved in 'log_transformed' folder.")
