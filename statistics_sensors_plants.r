# Function to perform the analysis
perform_analysis_no_rank <- function(file_name, output_prefix) {
  
  # Read the data
  data <- read.csv(file_name)
  
  # Create output directories if they don't exist
  if (!dir.exists("output_statistics")) dir.create("output_statistics")
  if (!dir.exists("qq_plots")) dir.create("qq_plots")
  if (!dir.exists("distribution_plots")) dir.create("distribution_plots")
  if (!dir.exists("plots")) dir.create("plots")
  
  # Convert architecture to factor explicitly
  data$architecture <- as.factor(data$architecture)
  
  # Determine the variable to use for analysis
  if ("absorbedPAR_umol_m2_s1_crop" %in% colnames(data)) {
  analysis_var <- "absorbedPAR_umol_m2_s1_crop"
  } else {
  analysis_var <- "absorbedPAR_umol_m2_s1"
  }
  
  # Parametric analysis
  sink(paste0("output_statistics/", output_prefix, "_anova.txt"))
  
  # Perform one-way ANOVA
  anova_result <- aov(as.formula(paste(analysis_var, "~ architecture")), data = data)
  lsd_test <- LSD.test(anova_result, "architecture", console = FALSE)
  
  # Format and print the ANOVA output
  cat("\nANOVA Analysis:\n")
  format_anova_output(anova_result, lsd_test)
  
  # Normality test (Shapiro-Wilk test on residuals)
  residuals_data <- residuals(anova_result)
  shapiro_test <- shapiro.test(residuals_data)
  cat("\nShapiro-Wilk Normality Test:\n")
  print(shapiro_test)
  
  # Homogeneity of variances (Levene's Test)
  levene_test <- leveneTest(as.formula(paste(analysis_var, "~ architecture")), data = data)
  cat("\nLevene's Test for Homogeneity of Variances:\n")
  print(levene_test)
  
  # Generate QQ plot for residuals and save as image
  qqplot_filename <- paste0("qq_plots/qqplot_", output_prefix, ".png")
  png(qqplot_filename)
  qqnorm(residuals_data)
  qqline(residuals_data)
  dev.off()
  
  # Create a histogram for the analysis variable
  p <- ggplot(data, aes_string(x = analysis_var)) +
  geom_histogram(binwidth = 10, fill = "blue", color = "black", alpha = 0.7) +
  labs(title = paste("Histogram of", analysis_var, "for", output_prefix),
     x = analysis_var,
     y = "Frequency") +
  theme_minimal()
  
  # Save the plot as a PNG file
  ggsave(filename = paste0("distribution_plots/histogram_", output_prefix, ".png"), plot = p)
  
  cat("\n---------------------------------------------\n")
  
  # Close the text file for ANOVA
  sink()

  # Non-parametric analysis
  sink(paste0("output_statistics_nonparametric/", output_prefix, "_kruskal_wallis.txt"))

  # Perform Kruskal-Wallis test
  kruskal_result <- kruskal.test(as.formula(paste(analysis_var, "~ architecture")), data = data)
  cat("\nKruskal-Wallis Test:\n")
  print(kruskal_result)
  
  # Perform Dunn's test using the FSA package
  dunn_result <- dunnTest(as.formula(paste(analysis_var, "~ architecture")), data = data, method = "bonferroni")
  cat("\nDunn's Test:\n")
  print(dunn_result)
  
  # Extract the p-values and comparisons
  p_values <- dunn_result$res$P.adj
  comparisons <- dunn_result$res$Comparison
  
  # Generate a matrix of p-values for pairwise comparisons
  p_matrix <- matrix(1, nrow = length(unique(data$architecture)),
           ncol = length(unique(data$architecture)))
  rownames(p_matrix) <- levels(data$architecture)
  colnames(p_matrix) <- levels(data$architecture)
  
  # Fill in the p-value matrix based on the pairwise comparisons, only if p_values is not empty
  if (length(p_values) > 0) {
  for (i in seq_along(p_values)) {
    comparison <- unlist(strsplit(comparisons[i], " - "))
    group1 <- comparison[1]
    group2 <- comparison[2]
    
    # Fill in the p-value for both (group1, group2) and (group2, group1)
    p_matrix[group1, group2] <- p_values[i]
    p_matrix[group2, group1] <- p_values[i]
  }
  } else {
  cat("No significant comparisons found.\n")
  }
  
  # Use multcompView to generate significant letters
  significant_letters <- multcompLetters(p_matrix, threshold = 0.05)
  cat("\nSignificant Letters:\n")
  print(significant_letters$Letters)
  
  cat("\n---------------------------------------------\n")
  
  # Close the text file for Kruskal-Wallis
  sink()
}

# Analyze each file
perform_analysis_no_rank("combined_files/combined_high_sensors_cleaned.csv", "high_sensors")
perform_analysis_no_rank("combined_files/combined_low_sensors_cleaned.csv", "low_sensors")
perform_analysis_no_rank("combined_files/combined_total_absorbedPAR_high_cleaned.csv", "high_total_absorbedPAR")
perform_analysis_no_rank("combined_files/combined_total_absorbedPAR_low_cleaned.csv", "low_total_absorbedPAR")
