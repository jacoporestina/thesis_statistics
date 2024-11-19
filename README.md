# Data Visualization and Statistical Analysis for Plant Science

## Repository Overview

This repository contains scripts and notebooks for data visualization, file processing, and statistical analysis in the context of plant science research. It includes both Python and R scripts tailored for specific tasks.

## Files

### 1. `plotting_part.ipynb`

A Jupyter Notebook dedicated to creating visual representations of processed plant data.

#### Key Functionalities:
- Generates linear plots to visualize trends across different plant metrics.
- Includes confidence intervals to highlight variability.
- Suitable for comparing light interception across leaf ranks or densities.

#### Outputs:
- High-quality visualizations in formats such as PNG or PDF.

---

### 2. `file_combination.ipynb`

This Jupyter Notebook consolidates data from multiple files for streamlined analysis.

#### Key Functionalities:
- Reads multiple data files and merges them into a single dataset.
- Ensures consistent formatting and handles missing values.
- Prepares combined data for downstream statistical analysis or visualization.

#### Outputs:
- A consolidated dataset saved in CSV format.

---

### 3. `statistics_sensors_plants.r`

An R script for statistical analysis of sensor data across different plant setups.

#### Key Functionalities:
- Performs non-parametric tests (e.g., Kruskal-Wallis) for datasets not meeting normality assumptions.
- Conducts post-hoc analysis with Dunn’s test, including significance groupings.
- Generates QQ plots to check normality of residuals.

#### Outputs:
- Statistical summaries saved in text files.
- QQ plots saved as image files.

---

### 4. `statistics_ranks.R`

This R script is focused on analyzing light interception data across leaf ranks.

#### Key Functionalities:
- Analyzes the effect of rank on light interception using ANOVA.
- Visualizes the results with linear charts and confidence intervals.
- Prepares datasets for reporting and thesis documentation.

#### Outputs:
- Statistical result files summarizing the impact of rank.
- Line charts showing trends in light interception.

---

## Usage

### Setup
1. Install the required dependencies for Python:
    ```bash
    pip install pandas numpy matplotlib
    ```
2. For R, ensure the following packages are installed:
    - `ggplot2`
    - `dplyr`
    - `FSA`
    - `DescTools`

### Execution
- **Jupyter Notebooks**: Open and run in any environment supporting `.ipynb` files, such as JupyterLab or VS Code.
- **R Scripts**: Run in RStudio or any compatible R environment.

### Customization
Adapt file paths and column names within the scripts to fit your specific dataset and analysis needs.

---

## Outputs

The scripts and notebooks generate various outputs:
- **Visualizations**: Charts and plots illustrating key trends and metrics.
- **Statistical Results**: Detailed summaries of statistical tests.
- **Combined Data Files**: Consolidated datasets ready for further analysis.

## License

This repository is distributed under the [MIT License](LICENSE).

## Author

[Jacopo Restina] - Contributions to data visualization and statistical analysis in plant science research.
