setwd("C:/Users/jacop/OneDrive/Desktop/Thesis/Data analysis/Statistics")
total_absorbedPAR <- read.csv("total_absorbedPAR.csv")
head(total_absorbedPAR)
library(stats)

# Fit the ANOVA model
anova_model <- aov(absorbedPAR_umol_m2_s1 ~ density * canopy, data = total_absorbedPAR)

# Display the summary of the ANOVA model
summary(anova_model)



# Assuming you've already loaded your data into a DataFrame called new_data
new_data <- read.csv("combined_results_simulations_fake.csv")

# Split the data by rank
data_by_rank <- split(new_data, new_data$rank)

# Initialize a list to store ANOVA results
anova_results <- list()

# Loop through each rank and perform ANOVA
for (rank in names(data_by_rank)) {
  model <- aov(absorbedPAR_umol_m2_s1 ~ density * canopy, data = data_by_rank[[rank]])
  anova_results[[rank]] <- summary(model)
}

# Print the results for each rank
anova_results
