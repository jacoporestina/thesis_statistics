# Define the Kruskal-Wallis function
process_kruskal <- function(input_file, output_kruskal) {
  # Load the data
  data <- read_csv(input_file)
  
  # Ensure architecture is a factor
  data$architecture <- as.factor(data$architecture)
  
  # Create output file
  kruskal_output <- file(output_kruskal, open = "wt")
  
  # Process data by rank
  ranks <- unique(data$rank)
  for (rank in ranks) {
    # Filter data for the current rank
    rank_data <- filter(data, rank == rank)
    
    # Perform Kruskal-Wallis test
    kruskal_result <- kruskal.test(absorbedPAR_umol_m2_s1 ~ architecture, data = rank_data)
    
    # Write Kruskal-Wallis results for this rank to the file
    writeLines(sprintf("\nKruskal-Wallis test results for rank %d:\n", rank), kruskal_output)
    writeLines(sprintf("Statistic: %f, p-value: %f\n", kruskal_result$statistic, kruskal_result$p.value), kruskal_output)
    
    # Post-hoc test (Dunn's test) if significant
    if (kruskal_result$p.value < 0.05) {
      posthoc_results <- dunnTest(absorbedPAR_umol_m2_s1 ~ architecture, data = rank_data, method = "bonferroni")
      
      # Write post-hoc results
      writeLines("\nPost-hoc (Dunn) Results:\n", kruskal_output)
      writeLines(capture.output(posthoc_results), kruskal_output)
      
      # Extract adjusted p-values and calculate letter groupings
      comp_matrix <- posthoc_results$res
      p_values <- setNames(comp_matrix$P.adj, comp_matrix$Comparison)
      
      # Generate letter groupings based on significance
      group_letters <- multcompLetters(p_values)
      
      # Write letter groupings
      writeLines("\nSignificance Letters:\n", kruskal_output)
      writeLines(capture.output(group_letters$Letters), kruskal_output)
    }
  }
  
  # Close the output file
  close(kruskal_output)
}

# Define input files and corresponding output paths
files <- list(
  list(
    input = "combined_files/combined_high_ranks_cleaned.csv",
    output_kruskal = "output_statistics/Kruskal_high_ranks.txt"
  ),
  list(
    input = "combined_files/combined_low_ranks_cleaned.csv",
    output_kruskal = "output_statistics/Kruskal_low_ranks.txt"
  )
)

# Loop through each file and apply the Kruskal-Wallis function
for (file_info in files) {
  process_kruskal(file_info$input, file_info$output_kruskal)
}

print("Kruskal-Wallis processing complete for all files.")
