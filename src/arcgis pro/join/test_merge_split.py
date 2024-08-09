import arcpy
import os
import unittest

from split_merge_dec import split_merge_decorator

class TestSplitMergeDecorator(unittest.TestCase):

    def setUp(self):
        # Set up test environment
        self.workspace = arcpy.env.scratchGDB
        arcpy.env.workspace = self.workspace
        
        # Create a small test feature class
        self.input_fc = os.path.join(self.workspace, "test_input_fc")
        arcpy.management.CreateFeatureclass(self.workspace, "test_input_fc", "POINT")
        arcpy.management.AddField(self.input_fc, "TestField", "LONG")
        
        # Insert test data
        with arcpy.da.InsertCursor(self.input_fc, ["SHAPE@", "TestField"]) as cursor:
            cursor.insertRow([arcpy.Point(1, 1), 1])
            cursor.insertRow([arcpy.Point(2, 2), 2])
            cursor.insertRow([arcpy.Point(3, 3), 3])
            cursor.insertRow([arcpy.Point(4, 4), 4])
            cursor.insertRow([arcpy.Point(5, 5), 5])

        self.output_fc = os.path.join(self.workspace, "test_output_fc")

    def test_process_feature_class(self):
        @split_merge_decorator(num_splits=2)
        def process_feature_class(input_fc, output_fc):
            # Simple processing: just copy features
            arcpy.management.CopyFeatures(input_fc, output_fc)
        
        # Run the processing function
        process_feature_class(self.input_fc, self.output_fc)

        # Verify that the output feature class exists
        self.assertTrue(arcpy.Exists(self.output_fc))

        # Verify that the output feature class has the correct number of records
        output_count = int(arcpy.management.GetCount(self.output_fc)[0])
        self.assertEqual(output_count, 5)

        # Verify that the field values are as expected
        expected_values = [1, 2, 3, 4, 5]
        actual_values = []
        with arcpy.da.SearchCursor(self.output_fc, ["TestField"]) as cursor:
            for row in cursor:
                actual_values.append(row[0])

        self.assertListEqual(actual_values, expected_values)

    def tearDown(self):
        # Clean up test environment
        arcpy.management.Delete(self.input_fc)
        arcpy.management.Delete(self.output_fc)

if __name__ == "__main__":
    unittest.main()
