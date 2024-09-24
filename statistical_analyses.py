import pandas as pd
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import levene, shapiro

# Load the data.
data = pd.read_csv('combined_results_simulations_fake.csv')

# Print basic infor about the dataframe.
print(data.info())
print("\nUnique values in 'density':", data['density'].unique())
print("Unique values in 'canopy':", data['canopy'].unique())
print("Unique values in 'rank':", data['rank'].unique())

# Check for any NaN values.
print("\nNaN counts in DataFrame:")
print(data.isna().sum())

# Summary statistics for numeric columns.
print("\nSummary statistics for numeric columns:")
print(data.describe())


# Opening output files for ANOVA results and assumption checks.
anova_output = open('anova_results.txt', 'w')
assumptions_output = open('assumption_checks.txt', 'w')

# Process data by rank.
for rank in data['rank'].unique():
    # Filter data for the current rank.
    rank_data = data[data['rank'] == rank]
    
    # ANOVA model.
    try:
        model = ols('absorbedPAR_umol_m2_s1 ~ C(density) * C(canopy)', data=rank_data).fit()
        anova_results = sm.stats.anova_lm(model, typ=2)
    except Exception as e:
        print("Error in running ANOVA:", e) 

    anova_output.write(f'ANOVA Results for Rank {rank}:\n{anova_results}\n') # Write result to file.
   
    # Post-hoc test (LSD).
    if model.f_pvalue < 0.05:  # Check if the overall model is significant.
        mc = pairwise_tukeyhsd(rank_data['absorbedPAR_umol_m2_s1'], rank_data['density'] + rank_data['canopy'])
        anova_output.write(f'\nPost-hoc (LSD) Results for Rank {rank}:\n{mc}\n')

    # Assumption Checks: Levene's Test and Normality Test.
    grouped_data = rank_data.groupby(['density', 'canopy'])
    groups = [group['absorbedPAR_umol_m2_s1'] for name, group in grouped_data]
    levene_stat, levene_p = levene(*groups)
    shapiro_stat, shapiro_p = shapiro(model.resid)
    assumptions_output.write(f'\nLevene Test for Rank {rank}: Stat={levene_stat}, p={levene_p}\n')
    assumptions_output.write(f'\nShapiro-Wilk Test for Rank {rank}: Stat={shapiro_stat}, p={shapiro_p}\n')

    # Plotting residuals for assumption checks.
    residuals = model.resid
    plt.figure()
    sm.qqplot(residuals, line='s')
    plt.title(f'Q-Q plot for residuals of rank {rank}')
    plt.savefig(f'qq_plots/qqplot_rank_{rank}.png')
    
    # Plotting results.
    plt.figure(figsize=(10, 6))
    sns.lineplot(x='rank', y='absorbedPAR_umol_m2_s1', hue='canopy', style='density', data=rank_data, markers=True, errorbar=('ci', 95), err_style="band")
    plt.title(f'Absorbed PAR over Leaf Ranks for Rank {rank}')
    plt.savefig(f'plots/absorbedPAR_rank_{rank}.png')
    plt.close()

# Close output files
anova_output.close()
assumptions_output.close()
