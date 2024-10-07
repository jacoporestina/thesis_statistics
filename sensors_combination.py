import pandas as pd
import re
import os
import matplotlib.pyplot as plt

'''PART 1: COMBINE RESULTS SENSORS FROM OUTPUT SIMULATION IN A BIGGER DATASET.'''
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
combined_high.to_csv('combined_files/combined_high_sensors.csv', index=False)
combined_low.to_csv('combined_files/combined_low_sensors.csv', index=False)

print("Data processing complete.")


'''PART 2: OUTLIERS CHECK AND BOXPLOT GENERATION FO ORIGINAL AND CLEANED DATA.'''
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
        'input_file': 'combined_files/combined_high_sensors.csv',
        'output_cleaned_file': 'combined_files/combined_high_sensors_cleaned.csv',
        'output_outliers_file': 'combined_files/combined_high_sensors_outliers.csv',
        'output_boxplot_folder': 'boxplots/high_sensors',
        'label': 'High Density'
    },
    {
        'input_file': 'combined_files/combined_low_sensors.csv',
        'output_cleaned_file': 'combined_files/combined_low_sensors_cleaned.csv',
        'output_outliers_file': 'combined_files/combined_low_sensors_outliers.csv',
        'output_boxplot_folder': 'boxplots/low_sensors',
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
