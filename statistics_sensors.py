import pandas as pd
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.multicomp import pairwise_tukeyhsd, MultiComparison
import matplotlib.pyplot as plt
from scipy.stats import levene, shapiro
import seaborn as sns


# Import file and read as pandas dataframe.
filename = "combined_sensors_data.csv"
data = pd.read_csv(filename)
print(data)

# Create output.txt for anova results and assumptions.
anova_output = open('output_statistics/ANOVA_sensors.txt', 'w')
assumptions = open('output_statistics/assumptions_sensors.txt', 'w') 

# ANOVA 2-way.
model = ols('absorbedPAR_umol_m2_s1 ~ C(density) * C(architecture)', data=data).fit()
anova_results = sm.stats.anova_lm(model, typ=2)

# Function to format p-values with a minimum display value of 0.001
def format_p_value(p):
    if p < 0.001:
        return "<0.001"
    else:
        return round(p, 3)  # Round to 3 decimal places

# Apply the function to the ANOVA results' p-values
anova_results['PR(>F)'] = anova_results['PR(>F)'].apply(format_p_value)

# Get descriptive statistics.
descriptive_statistics = data.describe()

# Write ANOVA results, model summary and descriptive statistics in txt file.
anova_output.write(f"\nANOVA results for total absorbedPAR: \n {anova_results} \n")

# Post-hoc test (TukeyHSD).
if model.f_pvalue < 0.05:  # Check if the overall model is significant.
    comparison = MultiComparison(data['absorbedPAR_umol_m2_s1'], data['density'] + data['architecture'])
    tukey_result = comparison.tukeyhsd()
    anova_output.write(f'\nPost-hoc (TukeyHSD) Results:\n{tukey_result.summary()}\n')

# Assumption Checks: Levene's Test and Normality Test.
group_a = data[data['density'] == 'High']['absorbedPAR_umol_m2_s1']
group_b = data[data['density'] == 'Low']['absorbedPAR_umol_m2_s1']
levene_stat, levene_p = levene(group_a, group_b)
shapiro_stat, shapiro_p = shapiro(model.resid)
assumptions.write(f'\nLevene Test: Stat={levene_stat}, p={levene_p}\n')
assumptions.write(f'Shapiro-Wilk Test: Stat={shapiro_stat}, p={shapiro_p}\n')

# Plotting residuals for assumption checks.
residuals = model.resid
plt.figure()
sm.qqplot(residuals, line='s')
plt.title(f'Q-Q plot for residuals')
plt.savefig(f'qq_plots/qqplot_sensors.png')

# Close output files.
anova_output.close()
assumptions.close()

# Make a visualization of results with a bar chart. 
# 1) Calculate mean and st dev of data within densities.
data_grouped = data.groupby(['density', 'architecture'])['absorbedPAR_umol_m2_s1']
mean_values = data_grouped.mean().reset_index(name='mean')
mean_values['sd_dev'] = data_grouped.std().reset_index(name='std_dev')['std_dev']
densities = mean_values['density'].unique()
print(mean_values)
print(densities)

# 2)Create the bar charts.
for density in densities:
    # Filter dataset for densities
    filtered_density_data = mean_values[mean_values['density'] == density]
    print(filtered_density_data['architecture'])
    print(filtered_density_data['mean'])
    
    # Make the bar chart.
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(filtered_density_data['architecture'], filtered_density_data['mean'], yerr=filtered_density_data['sd_dev'], 
           width=0.5, edgecolor='black', linewidth=0.5, capsize=5, color='green')
    
    # Set the title and labels
    ax.set_title(f' Absorbed PAR sensors for {density} density')
    ax.set_xlabel('Canopy')
    ax.set_ylabel('Absorbed PAR (umol m-2 s-1)')

    #plt.legend(bars, filtered_density_data['canopy'], title='Canopy')
    plt.savefig(f'plots/absorbedPAR sensors {density}.png')
    plt.close(fig)
