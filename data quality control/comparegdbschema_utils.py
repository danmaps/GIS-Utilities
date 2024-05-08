import arcpy
import csv
import os


def read_csv(file_path):
    """
    Reads a CSV file and returns its contents as a list of rows, excluding the first and third columns.
    :param file_path: Path to the CSV file.
    :return: List of rows, with each row represented as a tuple, excluding the first and third columns.
    """
    with open(file_path, mode='r', newline='\n') as file:
        reader = csv.reader(file)
        header = next(reader)
        header = header[1:2] + header[3:]  # Skip the first and third column in the header
        return [tuple(row[1:2] + row[3:]) for row in reader], header
    



def compare_csv(gdb1_name, gdb2_name, file1_path, file2_path, detailed_report):

    """
    Compare the contents of two CSV files and find any differences in the schema.

    Args:
        gdb1_name (str): The name of the first geodatabase.
        gdb2_name (str): The name of the second geodatabase.
        file1_path (str): The file path to the first CSV file.
        file2_path (str): The file path to the second CSV file.
        detailed_report (bool): Flag indicating whether to generate a detailed report.

    Returns:
        Differences between the two CSV files in the schema.

    Raises:
        None
    """
    content1, header1 = read_csv(file1_path)
    content2, header2 = read_csv(file2_path)

    # Create schema_row instances for each row in the CSV content
    rows1 = [schema_row(row) for row in content1]
    rows2 = [schema_row(row) for row in content2]
    arcpy.AddMessage("len(rows1): " + str(len(rows1)))
    arcpy.AddMessage("len(rows2): " + str(len(rows2)))

    # Find differences by comparing rows directly O(n^2)
    # todo: improve this with set subtraction for O(n) performance
    differences = []
    for row1 in rows1:
        found_match = False
        for row2 in rows2:
            if row1 == row2:
                found_match = True
                break
        if not found_match:
            differences.append(f"Row unique to {gdb1_name}: {row1}")

    for row2 in rows2:
        found_match = False
        for row1 in rows1:
            if row2 == row1:
                found_match = True
                break
        if not found_match:
            differences.append(f"Row unique to {gdb2_name}: {row2}")

    return differences    


class schema_row(list):
    """
    Represents a row of schema data for comparison.

    This class extends the built-in list class to provide custom comparison
    functionality for schema rows. Each instance of `schema_row` represents
    a single row of schema data, typically extracted from a CSV file or database.

    The comparison between `schema_row` instances is performed element-wise,
    considering special conditions such as 'X' placeholders. Equality between
    two `schema_row` instances is determined by comparing corresponding elements
    of the rows, allowing flexibility in schema comparison operations.

    Attributes:
        Inherits all attributes from the built-in list class.

    Methods:
        compare_chars(item1, item2): Compares characters of two items, considering
            special conditions such as 'X' placeholders. Returns True if the characters
            match or are both 'X', otherwise returns False.

    Example usage:
        row1 = schema_row(['SCE_pts_2024_Q7', 'SCE_pts_2024_Q7', 'Unknown', 'OID', 'OID', 'OID', '4'])
        row2 = schema_row(['XXX_pts_2024_QX', 'XXX_pts_2024_QX', 'Unknown', 'OID', 'OID', 'OID', '4'])
        if row1 == row2:
            print("Rows are equal")
        else:
            print("Rows are not equal")
    """
    def __eq__(self, other):
        # Check if both lists have the same number of elements
        if len(self) != len(other):
            print("both lists should have the same number of elements")
            print(len(self),len(other))
            return False

        # Compare characters at each position in both lists
        for item1, item2 in zip(self, other):
            # print(f"comparing {item1} to {item2}")
            if not self.compare_chars(item1, item2):
                return False

        return True
    
    def __hash__(self):
        # Convert the list to a tuple for hashing
        return hash(tuple(self))

    def compare_chars(self, item1, item2):
        # Check if both strings have the same number of characters
        if len(item1) != len(item2):
            # Return False if lengths are different
            return False
            
        # Iterate through each character pair in the strings
        for c1, c2 in zip(item1, item2):
            # If either character is 'X', skip comparison
            if c1 == 'X' or c2 == 'X':
                continue
            # If characters are different, return False
            if c1 != c2:
                return False
        
        # If all characters are either 'X' or matching, return True
        return True



def generate_schema_report(gdb_path, output_csv, detailed_report):
    """Generates a simple schema report for the given geodatabase."""
    arcpy.env.workspace = gdb_path
    gdb_name = arcpy.Describe(gdb_path).baseName

    headers = ["Geodatabase", "Feature Class/Table Name", "Alias", "Projection Name", "Field Name", "Field Alias", "Field Type", "Field Length"]

    feature_count = 0
    field_count = 0

    with open(output_csv, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)

        for dirpath, dirnames, filenames in arcpy.da.Walk(gdb_path, datatype=["FeatureClass", "Table"]):
            for filename in filenames:
                feature_count += 1
                item_path = os.path.join(dirpath, filename)
                item_desc = arcpy.Describe(item_path)
                projection_name = item_desc.spatialReference.name if item_desc.dataType == 'FeatureClass' else 'N/A'

                for field in arcpy.ListFields(item_path):
                    field_count += 1
                    writer.writerow([gdb_name,
                                    item_desc.name,
                                    item_desc.aliasName,
                                    projection_name,
                                    field.name,
                                    field.aliasName,
                                    field.type,
                                    field.length])

        if detailed_report:
            arcpy.AddMessage(f"Geodatabase: {gdb_name}")
            arcpy.AddMessage(f"Number of Feature Classes/Tables: {feature_count}")
            arcpy.AddMessage(f"Number of Fields: {field_count}")
