import arcpy
import os

def split_table(input_fc, output_gdb, num_splits):
    """
    Splits an input feature class or table into multiple smaller tables.

    :param input_fc: Path to the input feature class or table.
    :param output_gdb: Path to the output geodatabase where the split tables will be saved.
    :param num_splits: Number of splits (e.g., 10 for splitting into 10 tables).
    :return: List of paths to the split tables.
    """

    #overwrite outputs
    arcpy.env.overwriteOutput = True
    
    # Count total number of records
    total_count = int(arcpy.management.GetCount(input_fc)[0])
    records_per_split = total_count // num_splits
    split_tables = []

    # if output_gdb doesn't exist, create it
    if not arcpy.Exists(output_gdb):
        arcpy.management.CreateFileGDB(os.path.dirname(output_gdb), os.path.basename(output_gdb))

    # Use a SearchCursor to iterate over the records and divide them
    with arcpy.da.SearchCursor(input_fc, "*") as cursor:
        for i in range(num_splits):
            split_name = f"split_{i+1}"
            split_output = f"{output_gdb}\\{split_name}"
            arcpy.management.CreateTable(output_gdb, split_name, input_fc)
            
            with arcpy.da.InsertCursor(split_output, [f.name for f in arcpy.ListFields(input_fc)]) as insert_cursor:
                for j, row in enumerate(cursor):
                    insert_cursor.insertRow(row)
                    if j + 1 >= records_per_split and i < num_splits - 1:
                        break
            
            split_tables.append(split_output)
            print(f"Created {split_output} with {j + 1} records.")

    return split_tables

# Usage example
input_fc = r"C:\Users\mcveydb\Projects\local_problem_statements\Default.gdb\DR_IGPEP3Notifications"
output_gdb = fr"C:\Users\mcveydb\Projects\local_problem_statements\split.gdb"
num_splits = 10
split_tables = split_table(input_fc, output_gdb, num_splits)
