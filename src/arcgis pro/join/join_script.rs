use polars::prelude::*;
use polars::frame::DataFrame;
use std::error::Error;

fn main() -> Result<(), Box<dyn Error>> {
    // Load the first CSV file into a DataFrame
    let df1 = CsvReader::from_path("C:/data/DM_ALL_STRUCS.csv")?
        .infer_schema(None)
        .has_header(true)
        .finish()?;

    // Load the second CSV file into a DataFrame
    let df2 = CsvReader::from_path("C:/Users/mcveydb/Projects/local_problem_statements/subset.csv")?
        .infer_schema(None)
        .has_header(true)
        .finish()?;

    // Perform a left join on the specified columns
    let joined_df = df1.left_join(&df2, "SAP_FLOC_ID", "Floc")?;

    // Write the joined DataFrame to a new CSV file
    CsvWriter::new(std::fs::File::create("output_feature_class.csv")?)
        .has_header(true)
        .finish(&joined_df)?;

    // Identify unmatched rows
    let unmatched_df = joined_df.filter(&joined_df["Floc"].is_null())?;

    // Write the unmatched rows to a new CSV file
    CsvWriter::new(std::fs::File::create("unmatched_output.csv")?)
        .has_header(true)
        .finish(&unmatched_df)?;

    Ok(())
}
