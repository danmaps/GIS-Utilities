import arcpy
import os
import functools
import time

def split_merge_decorator(num_splits):
    """
    Decorator that splits a dataset into smaller parts, runs the decorated function on each part,
    and then merges the results back together. Also reports the time taken.

    :param num_splits: Number of splits for the dataset.
    :return: Decorator function.
    """
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(input_fc, output_fc, *args, **kwargs):
            start_time = time.time()

            # Create an in-memory workspace for temporary files
            temp_gdb = arcpy.env.scratchGDB
            
            # Split the dataset
            split_tables = split_table(input_fc, temp_gdb, num_splits)
            
            # Run the wrapped function on each split table
            output_tables = []
            for i, split_fc in enumerate(split_tables):
                split_output_fc = os.path.join(temp_gdb, f"processed_split_{i+1}")
                func(split_fc, split_output_fc, *args, **kwargs)
                output_tables.append(split_output_fc)
            
            # Merge the processed split tables into a single output
            arcpy.management.Merge(output_tables, output_fc)
            
            end_time = time.time()
            elapsed_time = end_time - start_time

            print(f"Final output merged into {output_fc}")
            print(f"Total time taken: {elapsed_time:.2f} seconds")
            return output_fc
        
        return wrapper
    
    return decorator

def split_table(input_fc, output_gdb, num_splits):
    """
    Splits an input feature class or table into multiple smaller tables.

    :param input_fc: Path to the input feature class or table.
    :param output_gdb: Path to the output geodatabase where the split tables will be saved.
    :param num_splits: Number of splits (e.g., 10 for splitting into 10 tables).
    :return: List of paths to the split tables.
    """
    
    total_count = int(arcpy.management.GetCount(input_fc)[0])
    records_per_split = total_count // num_splits
    split_tables = []

    with arcpy.da.SearchCursor(input_fc, "*") as cursor:
        for i in range(num_splits):
            split_name = f"split_{i+1}"
            split_output = f"{output_gdb}\\{split_name}"
            arcpy.management.CreateTable(output_gdb, split_name, input_fc)
            
            with arcpy.da.InsertCursor(split_output, [f.name for f in arcpy.ListFields(input_fc) if f.type != 'OID']) as insert_cursor:
                for j, row in enumerate(cursor):
                    insert_cursor.insertRow(row)
                    if j + 1 >= records_per_split and i < num_splits - 1:
                        break
            
            split_tables.append(split_output)
            print(f"Created {split_output} with {j + 1} records.")
    
    return split_tables

# Example usage of the decorator

@split_merge_decorator(num_splits=10)
def process_feature_class(input_fc, output_fc):
    """
    Example function to process a feature class (e.g., applying a field calculation).

    :param input_fc: Path to the input feature class.
    :param output_fc: Path to the output feature class.
    """
    # Example processing - copying the feature class (replace with actual processing logic)
    arcpy.management.CopyFeatures(input_fc, output_fc)
    print(f"Processed {input_fc} and saved to {output_fc}")

# Applying the decorator
# input_fc = r"Path\To\Your\LargeFeatureClass"
# output_fc = r"Path\To\Your\OutputFeatureClass"
# process_feature_class(input_fc, output_fc)
