import pandas as pd
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import levene, shapiro
import numpy as np
from scipy.stats import sem, t
import scikit_posthocs as sp

# Load the data.
data = pd.read_csv('combined_results_simulations.csv')

# Opening output files for ANOVA results and assumption checks.
anova_output = open('output_statistics/ANOVA_results_ranks.txt', 'w')
assumptions_output = open('output_statistics/assumption_checks_ranks.txt', 'w')

# Process data by rank.
for rank in data['rank'].unique():
    # Filter data for the current rank.
    rank_data = data[data['rank'] == rank]

   # ANOVA model.
    model = ols('absorbedPAR_umol_m2_s1 ~ C(density) * C(architecture)', data=rank_data).fit()
    anova_results = sm.stats.anova_lm(model, typ=2)

    # Function to format p-values with a minimum display value of 0.001
    def format_p_value(p):
        if p < 0.001:
            return "<0.001"
        else:
            return round(p, 3)  # Round to 3 decimal places

    # Apply the function to the ANOVA results' p-values
    anova_results['PR(>F)'] = anova_results['PR(>F)'].apply(format_p_value)
    
    # Write ANOVA results and summary to file.txt
    anova_output.write(f'\nANOVA Results for Rank {rank}:\n{anova_results}\n')

    # Get and write confidence intervals for model parameters
    conf_intervals = model.conf_int()
    anova_output.write(f'\nConfidence Intervals for Model Parameters:\n{conf_intervals}\n')

    # Post-hoc test (TukeyHSD).
    if model.f_pvalue < 0.05:  # Check if the overall model is significant.
        mc = pairwise_tukeyhsd(rank_data['absorbedPAR_umol_m2_s1'], rank_data['density'] + rank_data['architecture'])
        anova_output.write(f'\nPost-hoc (Tukeyhsd) Results for Rank {rank}:\n{mc}\n')

    # Assumption Checks: Levene's Test and Normality Test.
    grouped_data = rank_data.groupby(['density', 'architecture'])
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

# Close output files
anova_output.close()
assumptions_output.close()

# Create visualization of the results.

# 1) Calculate mean, std dev, and count for each combination
grouped = data.groupby(['density', 'architecture', 'rank'])['absorbedPAR_umol_m2_s1']
mean_values = grouped.mean().reset_index(name='mean')
mean_values['std_dev'] = grouped.std().reset_index(name='std_dev')['std_dev']
mean_values['n'] = grouped.count().reset_index(name='count')['count']

# 2) Calculate the t-value for 95% confidence interval
confidence = 0.95
mean_values['t_value'] = mean_values['n'].apply(lambda x: t.ppf((1 + confidence) / 2., x - 1))

# 3) Calculate the margin of error
mean_values['margin_error'] = mean_values['t_value'] * (mean_values['std_dev'] / np.sqrt(mean_values['n']))

# 4) Calculate lower and upper confidence bounds
mean_values['ci_lower'] = mean_values['mean'] - mean_values['margin_error']
mean_values['ci_upper'] = mean_values['mean'] + mean_values['margin_error']

# 5) Unique densities and canopies.
densities = mean_values['density'].unique()

# 6) Plotting for each density.
for density in densities:
    plt.figure(figsize=(10, 6))
    # Filter data for current density
    filtered_data = mean_values[mean_values['density'] == density]
    
    # Plotting lineplot for each architecture type within the current density
    for architecture in filtered_data['architecture'].unique():
        architecture_data = filtered_data[filtered_data['architecture'] == architecture]
        sns.lineplot(x='rank', y='mean', data=architecture_data, label=architecture, marker='o')
        # Adding the confidence interval as a shaded area
        plt.fill_between(architecture_data['rank'], architecture_data['ci_lower'], architecture_data['ci_upper'], alpha=0.3)
    
    plt.title(f'Absorbed PAR over Leaf Ranks for Density: {density}')
    plt.xlabel('Rank')
    plt.ylabel('Absorbed PAR umol m-2 s-1')
    plt.legend(title='Architecture Type')
    plt.savefig(f'plots/mean_absorbedPAR_for_{density}_density.png')
    plt.close()
