# Load necessary libraries
library(dplyr)  # for data manipulation
library(sf)     # for spatial data handling, if needed
library(data.table)  # for fast data manipulation

# Load input data (assuming one is a CSV and another is a spatial feature class)
input_fc1 <- st_read("C:/data/DM_ALL_STRUCS.gdb/OH_DM_ALL_STRUCS_0805")  # Reading spatial data
input_fc2 <- fread("C:/Users/mcveydb/Projects/local_problem_statements/subset.csv")  # Reading CSV

# Perform the join
joined_data <- input_fc1 %>%
  left_join(input_fc2, by = c("SAP_FLOC_ID" = "Floc"))

# Calculate the percentage of matches
total_count <- nrow(input_fc1)
matched_count <- sum(!is.na(joined_data$Floc))
match_percentage <- (matched_count / total_count) * 100

# Identify unmatched features
unmatched_features <- joined_data %>% filter(is.na(Floc))

# Save the output
output_fc <- sprintf("C:/Users/mcveydb/Projects/local_problem_statements/subset.gdb/output_feature_class_%s.shp", format(Sys.time(), "%Y%m%d_%H%M%S"))
st_write(joined_data, output_fc)

unmatched_output <- sprintf("C:/Users/mcveydb/Projects/local_problem_statements/subset.gdb/unmatched_output_%s.csv", format(Sys.time(), "%Y%m%d_%H%M%S"))
fwrite(unmatched_features, unmatched_output)

# Print summary
cat("Total records:", total_count, "\n")
cat("Number of matched records:", matched_count, "\n")
cat("Match percentage:", match_percentage, "%\n")
cat("Unmatched features saved to:", unmatched_output, "\n")
