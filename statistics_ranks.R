# Load necessary libraries
library(car)         # For Levene's test
library(agricolae)   # For LSD test
library(ggplot2)     # For QQ plots

# Read the data
data <- read.csv("combined_files/combined_high_ranks_cleaned.csv")

# Get unique ranks
ranks <- unique(data$rank)

# Initialize a text file to save outputs
sink("output_statistics/anova_ranks_high.txt")

# Loop through each rank
for (rank in ranks) {
  # Filter data for the current rank
  subset_data <- data[data$rank == rank, ]
  
  # Convert architecture to factor explicitly
  subset_data$architecture <- as.factor(subset_data$architecture)
  
  # Perform one-way ANOVA
  anova_result <- aov(absorbedPAR_umol_m2_s1 ~ architecture, data = subset_data)
  cat("\nANOVA for Rank:", rank, "\n")
  print(summary(anova_result))

  # Post-hoc LSD test
  lsd_test <- LSD.test(anova_result, "architecture", console=FALSE)
  cat("\nLSD Test for Rank:", rank, "\n")
  print(lsd_test)
  
  # Normality test (Shapiro-Wilk test on residuals)
  residuals_data <- residuals(anova_result)
  shapiro_test <- shapiro.test(residuals_data)
  cat("\nShapiro-Wilk Normality Test for Rank:", rank, "\n")
  print(shapiro_test)
  
  # Homogeneity of variances (Levene's Test)
  levene_test <- leveneTest(absorbedPAR_umol_m2_s1 ~ architecture, data = subset_data)
  cat("\nLevene's Test for Homogeneity of Variances for Rank:", rank, "\n")
  print(levene_test)
  
  # Generate QQ plot for residuals and save as image
  qqplot_filename <- paste0("qq_plots/qqplot_rank_", rank, ".png")
  png(qqplot_filename)
  qqnorm(residuals_data)
  qqline(residuals_data)
  dev.off()
  
  cat("\n---------------------------------------------\n")
}

# Close the text file
sink()
