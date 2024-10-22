# Load necessary libraries
library(car)         # For Levene's test
library(agricolae)   # For LSD test
library(ggplot2)     # For plotting
library(FSA)         # For Dunn's test
library(multcompView) # For generating significant letters
library(dplyr)       # For data manipulation

# Function to format the ANOVA output
format_anova_output <- function(anova_result, lsd_test, rank) {
  cat("\nANOVA for Rank:", rank, "\n")
  anova_table <- summary(anova_result)[[1]]
  colnames(anova_table) <- c("Df", "Sum Sq", "Mean Sq", "F value", "Pr(>F)")
  print(as.data.frame(anova_table))
  
  cat("\nPost-hoc LSD Test for Rank:", rank, "\n")
  cat("\nMeans for Each Group:\n")
  means_table <- lsd_test$means
  print(as.data.frame(means_table))
  
  cat("\nGroups (Significant Letters):\n")
  print(lsd_test$groups)
}

# Function to perform analysis
perform_analysis <- function(file_name, output_prefix) {
  
  # Read the data
  data <- read.csv(file_name)
  
  # Create output directories if they don't exist
  if (!dir.exists("output_statistics")) dir.create("output_statistics")
  if (!dir.exists("qq_plots")) dir.create("qq_plots")
  if (!dir.exists("distribution_plots")) dir.create("distribution_plots")
  if (!dir.exists("plots")) dir.create("plots")
  
  # Get unique ranks
  ranks <- unique(data$rank)
  
  # Initialize text files to save outputs
  sink(paste0("output_statistics/", output_prefix, "_anova_ranks.txt"))
  
  # Loop through each rank for parametric analysis
  for (rank in ranks) {
    # Filter data for the current rank
    subset_data <- data[data$rank == rank, ]
    
    # Convert architecture to factor explicitly
    subset_data$architecture <- as.factor(subset_data$architecture)
    
    # Perform one-way ANOVA
    anova_result <- aov(
      absorbedPAR_umol_m2_s1 ~ architecture, 
      data = subset_data
    )
    lsd_test <- LSD.test(anova_result, "architecture", console = FALSE)
    
    # Format and print the ANOVA output
    format_anova_output(anova_result, lsd_test, rank)
    
    # Normality test (Shapiro-Wilk test on residuals)
    residuals_data <- residuals(anova_result)
    shapiro_test <- shapiro.test(residuals_data)
    cat("\nShapiro-Wilk Normality Test for Rank:", rank, "\n")
    print(shapiro_test)
    
    # Homogeneity of variances (Levene's Test)
    levene_test <- leveneTest(
      absorbedPAR_umol_m2_s1 ~ architecture, 
      data = subset_data
    )
    cat("\nLevene's Test for Homogeneity of Variances for Rank:", rank, "\n")
    print(levene_test)
    
    # Generate QQ plot for residuals and save as image
    qqplot_filename <- paste0(
      "qq_plots/qqplot_", output_prefix, "_rank_", rank, ".png"
    )
    png(qqplot_filename)
    qqnorm(residuals_data)
    qqline(residuals_data)
    dev.off()
    
    # Create a histogram for absorbedPAR_umol_m2_s1
    p <- ggplot(subset_data, aes(x = absorbedPAR_umol_m2_s1)) +
      geom_histogram(
        binwidth = 10, fill = "blue", color = "black", alpha = 0.7
      ) +
      labs(
        title = paste(
          "Histogram of absorbedPAR_umol_m2_s1 for Rank", rank
        ),
        x = "absorbedPAR_umol_m2_s1",
        y = "Frequency"
      ) +
      theme_minimal()
    
    # Save the plot as a PNG file
    ggsave(
      filename = paste0(
        "distribution_plots/histogram_", output_prefix, "_rank_", rank, ".png"
      ), 
      plot = p
    )
    
    cat("\n---------------------------------------------\n")
  }
  
  # Close the text file for ANOVA
  sink()

  # Non-parametric analysis
  sink(paste0(
    "output_statistics_nonparametric/", output_prefix, 
    "_kruskal_wallis_ranks.txt"
  ))

  # Loop through each rank for non-parametric analysis
  for (rank in ranks) {
    # Filter data for the current rank
    subset_data <- data[data$rank == rank, ]
    
    # Convert architecture to factor explicitly
    subset_data$architecture <- as.factor(subset_data$architecture)
    
    # Perform Kruskal-Wallis test
    kruskal_result <- kruskal.test(
      absorbedPAR_umol_m2_s1 ~ architecture, 
      data = subset_data
    )
    cat("\nKruskal-Wallis Test for Rank:", rank, "\n")
    print(kruskal_result)
    
    # Perform Dunn's test using the FSA package
    dunn_result <- dunnTest(
      absorbedPAR_umol_m2_s1 ~ architecture, 
      data = subset_data, 
      method = "bonferroni"
    )
    cat("\nDunn's Test for Rank:", rank, "\n")
    print(dunn_result)
    
    # Extract the p-values and comparisons
    p_values <- dunn_result$res$P.adj
    comparisons <- dunn_result$res$Comparison
    
    # Generate a matrix of p-values for pairwise comparisons
    p_matrix <- matrix(
      1, 
      nrow = length(unique(subset_data$architecture)),
      ncol = length(unique(subset_data$architecture))
    )
    rownames(p_matrix) <- levels(subset_data$architecture)
    colnames(p_matrix) <- levels(subset_data$architecture)
    
    # Fill in the p-value matrix based on the pairwise comparisons, 
    # only if p_values is not empty
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
      cat("No significant comparisons found for Rank:", rank, "\n")
    }
    
    # Use multcompView to generate significant letters
    significant_letters <- multcompLetters(p_matrix, threshold = 0.05)
    cat("\nSignificant Letters for Rank:", rank, "\n")
    print(significant_letters$Letters)
    
    cat("\n---------------------------------------------\n")
  }
  
  # Close the text file for Kruskal-Wallis
  sink()
}

# Analyze both high and low density files
perform_analysis(
  "combined_files/combined_high_ranks_cleaned.csv", 
  "high_density"
)
perform_analysis(
  "combined_files/combined_low_ranks_cleaned.csv", 
  "low_density"
)
