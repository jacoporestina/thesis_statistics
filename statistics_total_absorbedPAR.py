import pandas as pd
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import matplotlib.pyplot as plt
from scipy.stats import levene, shapiro


# Import file and read as pandas dataframe.
filename = "total_absorbedPAR.csv"
data = pd.read_csv(filename)
print(data)

# Create output.txt for anova results and assumptions.
anova_output = open('output_statistics/ANOVA_total_absorbedPAR.txt', 'w')
assumptions = open('output_statistics/assumptions_total_absorbedPAR.txt', 'w') 

# ANOVA 2-way.
model = ols('absorbedPAR_umol_m2_s1 ~ C(density) * C(canopy)', data=data).fit()
anova_results = sm.stats.anova_lm(model, typ=2)
print(anova_results)

# Get descriptive statistics.
descriptive_statistics = data.describe()
print(descriptive_statistics)

# Write ANOVA results, model summary and descriptive statistics in txt file.
anova_output.write(f"\nANOVA results for total absorbedPAR: \n {anova_results} \n")
anova_output.write("\nModel summary: \n")
anova_output.write(model.summary().as_text())
anova_output.write(f"\nDescriptive statistics: {descriptive_statistics} \n")

# Post-hoc test (TukeyHSD).
if model.f_pvalue < 0.05:  # Check if the overall model is significant.
    mc = pairwise_tukeyhsd(data['absorbedPAR_umol_m2_s1'], data['density'] + data['canopy'])
    anova_output.write(f'\nPost-hoc (Tukeyhsd) Results:\n{mc}\n')

# Assumption Checks: Levene's Test and Normality Test.
group_a = data[data['density'] == 'High']['absorbedPAR_umol_m2_s1']
group_b = data[data['density'] == 'Low']['absorbedPAR_umol_m2_s1']
levene_stat, levene_p = levene(group_a, group_b)
shapiro_stat, shapiro_p = shapiro(model.resid)
assumptions.write(f'\nLevene Test: Stat={levene_stat}, p={levene_p}\n')
assumptions.write(f'\nShapiro-Wilk Test: Stat={shapiro_stat}, p={shapiro_p}\n')

# Plotting residuals for assumption checks.
residuals = model.resid
plt.figure()
sm.qqplot(residuals, line='s')
plt.title(f'Q-Q plot for residuals')
plt.savefig(f'qq_plots/qqplot_total_absorbedPAR.png')

# Close output files.
anova_output.close()
assumptions.close()

# Make a visualization of results with a bar chart. 
# 1) Calculate mean and st dev of data within densities.
data_grouped = data.groupby(['density', 'canopy'])['absorbedPAR_umol_m2_s1']
mean_values = data_grouped.mean().reset_index(name='mean')
mean_values['sd_dev'] = data_grouped.std().reset_index(name='std_dev')['std_dev']
densities = mean_values['density'].unique()
print(mean_values)
print(densities)

# 2)Create the bar charts.
for density in densities:
    # Filter dataset for densities
    filtered_density_data = mean_values[mean_values['density'] == density]
    print(filtered_density_data['canopy'])
    print(filtered_density_data['mean'])
    
    # Make the bar chart.
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ['red', 'green', 'yellow']
    ax.bar(filtered_density_data['canopy'], filtered_density_data['mean'], yerr=filtered_density_data['sd_dev'], 
           width=0.5, edgecolor='black', linewidth=0.5, capsize=5, color=colors)
    
    # Set the title and labels
    ax.set_title(f'Total Absorbed PAR for {density} density')
    ax.set_xlabel('Canopy')
    ax.set_ylabel('Absorbed PAR (umol m-2 s-1)')

    #plt.legend(bars, filtered_density_data['canopy'], title='Canopy')
    plt.savefig(f'plots/total absorbedPAR {density}.png')
    plt.close(fig)

