import arcpy
import os
import functools
import time
import tempfile

arcpy.env.overwriteOutput = True


def split_merge(num_splits, split_field="SplitID"):
    """
    Decorator that splits a dataset by a field, runs the decorated function on each split,
    and then merges the results back together. Also reports the time taken.

    :param num_splits: Number of splits for the dataset.
    :param split_field: The field name used to split the dataset.
    :return: Decorator function.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(input_fc, output_fc, *args, **kwargs):
            start_time = time.time()

            # create a temporary directory
            temp_dir = tempfile.mkdtemp()
            # create a new GDB in the temporary directory
            temp_gdb = os.path.join(temp_dir, "temp.gdb")
            # Create the temporary GDB
            arcpy.management.CreateFileGDB(temp_dir, "temp.gdb")

            # Add a split field if not already present
            records = add_split_field(input_fc, split_field, num_splits)

            # Split the dataset by the attribute values
            # split_tables = split_table_by_attribute(input_fc, temp_gdb, split_field)

            arcpy.analysis.SplitByAttributes(input_fc, temp_gdb, [split_field])
            print(f"There are {num_splits} chunks with ~{records} records each.")

            arcpy.env.workspace = temp_gdb
            split_tables = arcpy.ListFeatureClasses()
            # print(split_tables)

            # Run the wrapped function on each split table
            output_tables = []
            for split_fc in split_tables:
                split_output_fc = os.path.join(
                    temp_gdb, f"processed_{os.path.basename(split_fc)}"
                )
                func(split_fc, split_output_fc, *args, **kwargs)
                output_tables.append(split_output_fc)

            # Merge the processed split tables into a single output
            # print(output_tables)
            arcpy.management.Merge(output_tables, output_fc)

            end_time = time.time()
            elapsed_time = end_time - start_time

            print(f"Final output merged into {output_fc}")
            print(f"Total time taken: {elapsed_time:.2f} seconds")
            return output_fc

        return wrapper

    return decorator


def add_split_field(input_fc, field_name="SplitID", num_splits=2):
    """
    Adds a new field to the feature class and assigns values that can be used to split the dataset.

    :param input_fc: Path to the input feature class.
    :param field_name: Name of the field to add.
    :param num_splits: Number of splits.
    :return: None
    """
    if arcpy.ListFields(input_fc, field_name):
        arcpy.management.DeleteField(input_fc, field_name)

    arcpy.management.AddField(input_fc, field_name, "LONG")

    total_count = int(arcpy.management.GetCount(input_fc)[0])
    records_per_split = max(1, total_count // num_splits)

    with arcpy.da.UpdateCursor(input_fc, [field_name, "OID@"]) as cursor:
        count = 0
        for row in cursor:
            row[0] = (count // records_per_split) + 1
            cursor.updateRow(row)
            count += 1

    # print(f"Field {field_name} added to {input_fc}")
    return records_per_split


# Test class for the decorator

import unittest


class TestSplitMergeDecorator(unittest.TestCase):
    def setUp(self):
        # Set up test environment
        self.workspace = arcpy.env.scratchGDB
        arcpy.env.workspace = self.workspace
        arcpy.env.overwriteOutput = True

        # Create a small test feature class
        self.input_fc = os.path.join(self.workspace, "test_input_fc")
        arcpy.management.CreateFeatureclass(self.workspace, "test_input_fc", "POINT")
        arcpy.management.AddField(self.input_fc, "TestTField", "TEXT")
        arcpy.management.AddField(self.input_fc, "TestNField", "LONG")

        # Insert test data
        with arcpy.da.InsertCursor(
            self.input_fc, ["SHAPE@", "TestTField", "TestNField"]
        ) as cursor:
            for i in range(8):
                cursor.insertRow([arcpy.Point(i, i), "string_" + str(i), i])

        # Create a large test feature class
        self.large = os.path.join(self.workspace, "large")
        arcpy.management.CreateFeatureclass(self.workspace, "large", "POINT")
        arcpy.management.AddField(self.large, "TestTField", "TEXT")
        arcpy.management.AddField(self.large, "TestNField", "LONG")

        # Insert large test data
        with arcpy.da.InsertCursor(
            self.large, ["SHAPE@", "TestTField", "TestNField"]
        ) as cursor:
            for i in range(1000000):
                cursor.insertRow([arcpy.Point(i, i), "string_" + str(i), i])

        self.output_fc = os.path.join(self.workspace, "test_output_fc")
        self.large_output_fc = os.path.join(self.workspace, "large_output_fc")

    def test_process_feature_class(self):
        @split_merge(num_splits=4, split_field="SplitID")
        def process_feature_class(in_fc, out_fc):
            # Simple processing: just copy features
            arcpy.management.CopyFeatures(in_fc, out_fc)
            # print(arcpy.GetCount_management(in_fc)[0])
            # return out_fc

        # Run the processing function
        process_feature_class(self.input_fc, self.output_fc)

        # Verify that the output feature class exists
        self.assertTrue(arcpy.Exists(self.output_fc))

        # Verify that the output feature class has the correct number of records
        output_count = int(arcpy.management.GetCount(self.output_fc)[0])
        self.assertEqual(output_count, 8)

        # Verify that the integer values are as expected
        expected_values = [0, 1, 2, 3, 4, 5, 6, 7]
        actual_values = []
        with arcpy.da.SearchCursor(self.output_fc, ["TestNField"]) as cursor:
            for row in cursor:
                actual_values.append(row[0])

        # Verify that the string values are as expected
        expected_values = [
            "string_0",
            "string_1",
            "string_2",
            "string_3",
            "string_4",
            "string_5",
            "string_6",
            "string_7",
        ]
        actual_values = []
        with arcpy.da.SearchCursor(self.output_fc, ["TestTField"]) as cursor:
            for row in cursor:
                actual_values.append(row[0])

        self.assertListEqual(actual_values, expected_values)

    def test_calculate_fields(self):
        @split_merge(num_splits=4, split_field="SplitID")
        def calculate_fields(in_fc, out_fc):
            # Calculate fields
            arcpy.management.AddField(in_fc, "NewNField", "LONG")
            arcpy.management.CalculateField(
                in_fc, "NewNField", "!TestNField! + 1", "PYTHON3"
            )
            arcpy.CopyFeatures_management(in_fc, out_fc)

        # Run the processing function
        calculate_fields(self.input_fc, self.output_fc)

        # Verify that the integer values are as expected
        expected_values = [1, 2, 3, 4, 5, 6, 7, 8]
        actual_values = []
        with arcpy.da.SearchCursor(self.output_fc, ["NewNField"]) as cursor:
            for row in cursor:
                actual_values.append(row[0])

        self.assertListEqual(actual_values, expected_values)

    def test_large(self):
        @split_merge(num_splits=2, split_field="SplitID")
        def calculate_field(in_fc, out_fc):
            start_time = time.time()

            # Calculate fields
            arcpy.management.AddField(in_fc, "NewNField", "LONG")
            arcpy.management.CalculateField(
                in_fc, "NewNField", "!TestNField! + 1", "PYTHON3"
            )
            arcpy.CopyFeatures_management(in_fc, out_fc)

            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"Output {out_fc}")
            print(f"Time taken: {elapsed_time:.2f} seconds")

        # Run the processing function
        calculate_field(self.large, self.large_output_fc)

        # Verify that the integer values are as expected
        expected_values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        actual_values = []
        with arcpy.da.SearchCursor(
            self.large_output_fc, ["NewNField"], where_clause="NewNField <= 10"
        ) as cursor:
            for row in cursor:
                actual_values.append(row[0])

        self.assertListEqual(actual_values, expected_values)

    def tearDown(self):
        # Clean up test environment
        arcpy.management.Delete(self.input_fc)
        arcpy.management.Delete(self.output_fc)


if __name__ == "__main__":
    unittest.main()
