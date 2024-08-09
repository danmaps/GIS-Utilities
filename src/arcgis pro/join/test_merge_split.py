import unittest
import os
import arcpy

from split_merge_dec import split_merge_decorator

class TestSplitMergeDecorator(unittest.TestCase):

    def setUp(self):
        # Set up test environment
        self.workspace = arcpy.env.scratchGDB
        arcpy.env.workspace = self.workspace
        arcpy.env.overwriteOutput = True
        
        # Create a small test feature class
        self.input_fc = os.path.join(self.workspace, "test_input_fc")
        arcpy.management.CreateFeatureclass(self.workspace, "test_input_fc", "POINT")
        arcpy.management.AddField(self.input_fc, "TestField", "LONG")
        
        # Insert test data
        with arcpy.da.InsertCursor(self.input_fc, ["SHAPE@", "TestField"]) as cursor:
            for i in range(1, 8):
                cursor.insertRow([arcpy.Point(i, i), i])

        self.output_fc = os.path.join(self.workspace, "test_output_fc")

    def test_process_feature_class(self):
        @split_merge_decorator(num_splits=2)
        def process_feature_class(in_fc, out_fc):
            # Simple processing: just copy features
            arcpy.management.CopyFeatures(in_fc, out_fc)
        
        # Run the processing function
        process_feature_class(self.input_fc, self.output_fc)

        # Verify that the output feature class exists
        self.assertTrue(arcpy.Exists(self.output_fc))

        # Verify that the output feature class has the correct number of records
        output_count = int(arcpy.management.GetCount(self.output_fc)[0])
        self.assertEqual(output_count, 7)

        # Verify that the field values are as expected
        expected_values = [1, 2, 3, 4, 5, 6, 7]
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