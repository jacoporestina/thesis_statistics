import pandas as pd
import matplotlib.pyplot as plt

# Load the dataset
data = pd.read_csv('combined_files/combined_high_ranks.csv')

# Initialize an empty DataFrame to store cleaned data
cleaned_data = pd.DataFrame()
outliers = pd.DataFrame()

# Process data by rank to generate boxplots and remove outliers
for rank in data['rank'].unique():
    # Filter data for the current rank
    rank_data = data[data['rank'] == rank]
    
    # Detect and remove outliers for each architecture within this rank
    for architecture in rank_data['architecture'].unique():
        # Filter data for the current architecture within the current rank
        arch_data = rank_data[rank_data['architecture'] == architecture]
        
        # Calculate Q1, Q3, and IQR
        Q1 = arch_data['absorbedPAR_umol_m2_s1'].quantile(0.25)
        Q3 = arch_data['absorbedPAR_umol_m2_s1'].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        # Identify and remove outliers
        is_outlier = (arch_data['absorbedPAR_umol_m2_s1'] < lower_bound) | (arch_data['absorbedPAR_umol_m2_s1'] > upper_bound)
        arch_outliers = arch_data[is_outlier]
        arch_data_cleaned = arch_data[~is_outlier]
        
        # Append the cleaned data to the main cleaned_data DataFrame
        outliers = pd.concat([outliers, arch_outliers], ignore_index=True)
        cleaned_data = pd.concat([cleaned_data, arch_data_cleaned], ignore_index=True)
        
        # Plot boxplot for the current rank and architecture
        plt.figure(figsize=(10, 6))
        rank_data.boxplot(column='absorbedPAR_umol_m2_s1', by='architecture', grid=False)
        plt.title(f'Boxplot of Absorbed PAR by Architecture for Rank {rank}')
        plt.suptitle('')  # Remove the automatic title from .boxplot()
        plt.xlabel('Architecture')
        plt.ylabel('Absorbed PAR (umol m-2 s-1)')
        
        # Save the plot with outliers
        plt.savefig(f'boxplots/high_rank_{rank}.png')
        plt.close()
    
# Save the cleaned data to a new CSV file
cleaned_data.to_csv('combined_files/combined_high_ranks_cleaned.csv', index=False)
print("Outliers removed and cleaned data saved to 'combined_high_ranks_cleaned.csv'")
print("Boxplots for each rank with outliers saved to the 'boxplots' folder.")
outliers.to_csv('combined_files/combined_high_ranks_outliers.csv', index=False)

# Display cleaned boxplots
# Load the high density dataset
data = pd.read_csv('combined_files/combined_high_ranks_cleaned.csv')

# Process data by rank to generate outlier boxplots for each rank
for rank in data['rank'].unique():
    # Filter data for the current rank
    rank_data = data[data['rank'] == rank]
    
    # Generate boxplot for absorbedPAR by architecture type for the current rank
    plt.figure(figsize=(10, 6))
    rank_data.boxplot(column='absorbedPAR_umol_m2_s1', by='architecture', grid=False)
    plt.title(f'Boxplot of Absorbed PAR by Architecture for Rank {rank}')
    plt.suptitle('')  # Remove the automatic title from .boxplot()
    plt.xlabel('Architecture')
    plt.ylabel('Absorbed PAR (umol m-2 s-1)')
    
    # Save the plot
    plt.savefig(f'boxplots/high_rank_{rank}_cleaned.png')
    plt.close()

print("Boxplots for each rank saved to the 'boxplots' folder.")


# Load the dataset for low density
data = pd.read_csv('combined_files/combined_low_ranks.csv')

# Initialize an empty DataFrame to store cleaned data
cleaned_data = pd.DataFrame()
outliers = pd.DataFrame()

# Process data by rank to generate boxplots and remove outliers
for rank in data['rank'].unique():
    # Filter data for the current rank
    rank_data = data[data['rank'] == rank]
    
    # Detect and remove outliers for each architecture within this rank
    for architecture in rank_data['architecture'].unique():
        # Filter data for the current architecture within the current rank
        arch_data = rank_data[rank_data['architecture'] == architecture]
        
        # Calculate Q1, Q3, and IQR
        Q1 = arch_data['absorbedPAR_umol_m2_s1'].quantile(0.25)
        Q3 = arch_data['absorbedPAR_umol_m2_s1'].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        # Identify and remove outliers
        is_outlier = (arch_data['absorbedPAR_umol_m2_s1'] < lower_bound) | (arch_data['absorbedPAR_umol_m2_s1'] > upper_bound)
        arch_outliers = arch_data[is_outlier]
        arch_data_cleaned = arch_data[~is_outlier]
        
        # Append the cleaned data to the main cleaned_data DataFrame
        outliers = pd.concat([outliers, arch_outliers], ignore_index=True)
        cleaned_data = pd.concat([cleaned_data, arch_data_cleaned], ignore_index=True)
        
        # Plot boxplot for the current rank and architecture
        plt.figure(figsize=(10, 6))
        rank_data.boxplot(column='absorbedPAR_umol_m2_s1', by='architecture', grid=False)
        plt.title(f'Boxplot of Absorbed PAR by Architecture for Rank {rank}')
        plt.suptitle('')  # Remove the automatic title from .boxplot()
        plt.xlabel('Architecture')
        plt.ylabel('Absorbed PAR (umol m-2 s-1)')
        
        # Save the plot with outliers
        plt.savefig(f'boxplots/low_rank_{rank}.png')
        plt.close()
    
# Save the cleaned data to a new CSV file
cleaned_data.to_csv('combined_files/combined_low_ranks_cleaned.csv', index=False)
print("Outliers removed and cleaned data saved to 'combined_low_ranks_cleaned.csv'")
print("Boxplots for each rank with outliers saved to the 'boxplots' folder.")
outliers.to_csv('combined_files/combined_low_ranks_outliers.csv', index=False)

# Display cleaned boxplots
# Load the high density dataset
data = pd.read_csv('combined_files/combined_low_ranks_cleaned.csv')

# Process data by rank to generate outlier boxplots for each rank
for rank in data['rank'].unique():
    # Filter data for the current rank
    rank_data = data[data['rank'] == rank]
    
    # Generate boxplot for absorbedPAR by architecture type for the current rank
    plt.figure(figsize=(10, 6))
    rank_data.boxplot(column='absorbedPAR_umol_m2_s1', by='architecture', grid=False)
    plt.title(f'Boxplot of Absorbed PAR by Architecture for Rank {rank}')
    plt.suptitle('')  # Remove the automatic title from .boxplot()
    plt.xlabel('Architecture')
    plt.ylabel('Absorbed PAR (umol m-2 s-1)')
    
    # Save the plot
    plt.savefig(f'boxplots/low_rank_{rank}_cleaned.png')
    plt.close()

print("Boxplots for each rank saved to the 'boxplots' folder.")





