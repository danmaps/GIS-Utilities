import arcpy
import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed
import arcpy
import os


def join_feature_classes(input_fc1, join_field_fc1, input_fc2, join_field_fc2, output_fc, unmatched_output=None):
    """
    Joins two feature classes or tables based on a common field and creates a new feature class with the result.
    Also generates a report of the percentage of matches and a list of join features that did not match.
    
    :param input_fc1: Path to the first input feature class or table (e.g., FGDB feature class, table, or CSV).
    :param join_field_fc1: The join field in the first input feature class or table.
    :param input_fc2: Path to the second input feature class or table (e.g., FGDB feature class, table, or CSV).
    :param join_field_fc2: The join field in the second input feature class or table.
    :param output_fc: Path to the output feature class that will be created.
    :param unmatched_output: Optional path to save the unmatched features in the same format as input_fc2.
    :return: None
    """
    
    # Ensure the environment is set to overwrite outputs
    arcpy.env.overwriteOutput = True

    # The qualifiedFieldNames environment is used by Copy Features when persisting the join field names.
    arcpy.env.qualifiedFieldNames = False

    arcpy.env.workspace = r"C:\Users\mcveydb\Projects\local_problem_statements\split.gdb"


    # Perform the join using the arcpy.management.AddJoin function
    joined = arcpy.management.AddJoin(input_fc1, join_field_fc1, input_fc2, join_field_fc2)

    # list fields in joined
    print([f.name for f in arcpy.ListFields(joined)])
    
    # Copy the joined result to a new feature class
    arcpy.management.CopyFeatures(joined, output_fc)
    
    # Count the total number of records in the input feature class
    total_count = int(arcpy.management.GetCount(input_fc1)[0])
    
    # Count the number of matched records (where the join field in input_fc2 is not null)
    matched_count = 0
    unmatched_features = []
    input_fc1_name = os.path.basename(input_fc1)
    input_fc2_name = os.path.basename(input_fc2)
    # list fields in output_fc
    print([f.name for f in arcpy.ListFields(output_fc)])
    
    # with arcpy.da.SearchCursor(joined, [f"{input_fc1_name}.{join_field_fc1}", f"{input_fc2_name}.{join_field_fc2}"]) as cursor:
    #     for row in cursor:
    #         if row[1] is not None:
    #             matched_count += 1
    #         else:
    #             unmatched_features.append(row[0])

    # # Calculate the percentage of matched records
    # match_percentage = (matched_count / total_count) * 100
    
    # Output the results
    print(f"Total records in {input_fc1}: {total_count}")
    print(f"Number of matched records: {matched_count}")
    # print(f"Match percentage: {match_percentage:.2f}%")
    
    # if unmatched_features:
    #     print("Unmatched features:")
    #     for feature in unmatched_features:
    #         print(feature)
    # else:
    #     print("All features matched.")
    
    # Optionally, write the unmatched features to a format matching input_fc2
    if unmatched_output:
        # Determine the format of input_fc2
        desc = arcpy.Describe(input_fc2)
        if desc.dataType in ["FeatureClass", "Table"]:
            # Create an empty feature class or table with the same schema as input_fc2
            arcpy.management.CreateTable(os.path.dirname(unmatched_output), os.path.basename(unmatched_output), input_fc2)
            # Insert the unmatched records into the new output
            with arcpy.da.InsertCursor(unmatched_output, [join_field_fc2]) as insert_cursor:
                for feature in unmatched_features:
                    insert_cursor.insertRow([feature])
            print(f"Unmatched features saved to {unmatched_output}")
        elif desc.dataType == "TextFile" or unmatched_output.endswith('.csv'):
            # Write unmatched features to a CSV file
            with open(unmatched_output, 'w') as file:
                file.write(f"{join_field_fc2}\n")
                for feature in unmatched_features:
                    file.write(f"{feature}\n")
            print(f"Unmatched features saved to {unmatched_output}")

    print("Function completed successfully.")


def parallel_join(table):
    print(f"Processing table: {table}")
    join_feature_classes(
        input_fc1=r"C:\Users\mcveydb\Projects\local_problem_statements\split.gdb\OH_DM_ALL_STRUCS_0805",
        join_field_fc1='SAP_FLOC_ID',
        input_fc2=table,
        join_field_fc2='Floc',
        output_fc=fr"C:\Users\mcveydb\Projects\local_problem_statements\split.gdb\output_feature_class_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
        unmatched_output=fr"C:\Users\mcveydb\Projects\local_problem_statements\split.gdb\unmatched_output_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
    )
    return f"Joined {table}"

def main():
    arcpy.env.workspace = r"C:\Users\mcveydb\Projects\local_problem_statements\split.gdb"
    
    # List feature classes in the FGDB
    tables = arcpy.ListTables()
    
    # Run the join function in parallel using ProcessPoolExecutor
    with ProcessPoolExecutor() as executor:
        # Submit tasks to the executor
        futures = {executor.submit(parallel_join, table): table for table in tables}
        
        # Process the results as they complete
        for future in as_completed(futures):
            table = futures[future]
            try:
                result = future.result()
                print(result)
            except Exception as exc:
                print(f"{table} generated an exception: {exc}")

if __name__ == "__main__":
    main()
