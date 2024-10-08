# Load necessary libraries
library(readr)
library(dplyr)
library(ggplot2)
library(car)
library(FSA)  # For Dunn's test
library(ggpubr)  # For QQ plot
library(multcompView)  # For significance letters
library(tidyr)  # For pivot_wider()

# Define a function to process Kruskal-Wallis, assumptions, and plotting for each dataset
process_data <- function(input_file, output_kruskal, qqplot_path) {
  
  # Load the data
  data <- read_csv(input_file)
  
  # Ensure architecture is a factor
  data$architecture <- as.factor(data$architecture)
  
  # Create output file for Kruskal-Wallis results
  kruskal_output <- file(output_kruskal, open = "wt")
  
  # Descriptive statistics for each architecture group
  descriptive_stats <- data %>%
    group_by(architecture) %>%
    summarise(
      mean_absorbedPAR = mean(absorbedPAR_umol_m2_s1),
      median_absorbedPAR = median(absorbedPAR_umol_m2_s1),
      sd_absorbedPAR = sd(absorbedPAR_umol_m2_s1)
    )
  
  writeLines("Descriptive Statistics:\n", kruskal_output)
  writeLines(capture.output(descriptive_stats), kruskal_output)
  writeLines("\n", kruskal_output)
  
  # Kruskal-Wallis test
  kruskal_result <- kruskal.test(absorbedPAR_umol_m2_s1 ~ architecture, data = data)
  
  # Write Kruskal-Wallis results to the file
  writeLines(sprintf("Kruskal-Wallis test results for total absorbed PAR:\n"), kruskal_output)
  writeLines(sprintf('Statistic = %f, p-value = %f\n', kruskal_result$statistic, kruskal_result$p.value), kruskal_output)
  
  # Post-hoc Dunn's test if significant
  if (kruskal_result$p.value < 0.05) {
    posthoc_results <- dunnTest(absorbedPAR_umol_m2_s1 ~ architecture, data = data, method = "bonferroni")
    
    # Write post-hoc results
    writeLines("\nPost-hoc (Dunn) Results:\n", kruskal_output)
    writeLines(capture.output(posthoc_results$res), kruskal_output)
    
    # Prepare data for significance letters
    # Create named vector of p-values from post-hoc test
    pvals <- posthoc_results$res %>%
      select(Comparison, P.adj) %>%
      filter(!is.na(P.adj)) 
    
    # Convert comparisons into a named vector for multcompLetters
    pvals_named <- setNames(pvals$P.adj, pvals$Comparison)
    
    # Generate significance letters
    sig_letters <- multcompLetters(pvals_named)$Letters
    
    # Write significance letters to the file
    writeLines("\nSignificance Letters:\n", kruskal_output)
    writeLines(capture.output(sig_letters), kruskal_output)
  } else {
    writeLines("\nNo significant differences found, skipping post-hoc analysis.\n", kruskal_output)
  }
  
  # Generate QQ plot for normality check
  qqplot <- ggqqplot(data$absorbedPAR_umol_m2_s1, title = "QQ Plot for absorbedPAR_umol_m2_s1")
  ggsave(qqplot_path, plot = qqplot)
  
  # Close output file
  close(kruskal_output)
}

# Define input files and corresponding output paths for high and low densities
files <- list(
  list(
    input_file = "combined_files/combined_total_absorbedPAR_high_cleaned.csv",
    output_kruskal = "output_statistics/Kruskal_total_absorbedPAR_high.txt",
    qqplot_path = "qq_plots/total_absorbedPAR_high.png"
  ),
  list(
    input_file = "combined_files/combined_total_absorbedPAR_low_cleaned.csv",
    output_kruskal = "output_statistics/Kruskal_total_absorbedPAR_low.txt",
    qqplot_path = "qq_plots/total_absorbedPAR_low.png"
  ),
  list(
    input_file = "combined_files/combined_high_sensors_cleaned.csv",
    output_kruskal = "output_statistics/Kruskal_sensors_high.txt",
    qqplot_path = "qq_plots/sensors_high.png"
  ),
  list(
    input_file = "combined_files/combined_low_sensors_cleaned.csv",
    output_kruskal = "output_statistics/Kruskal_sensors_low.txt",
    qqplot_path = "qq_plots/sensors_low.png"
  )
)

# Loop through each file and apply the Kruskal-Wallis function
for (file_info in files) {
  process_data(
    input_file = file_info$input_file,
    output_kruskal = file_info$output_kruskal,
    qqplot_path = file_info$qqplot_path
  )
}

print("Kruskal-Wallis analysis completed for all datasets.")
