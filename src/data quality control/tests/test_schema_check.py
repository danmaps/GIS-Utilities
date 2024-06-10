import unittest
from unittest.mock import mock_open, patch
import sys
import os

# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now you can import your module
from comparegdbschema_utils import compare_csv

class TestCompareCSV(unittest.TestCase):

    @patch('builtins.open', new_callable=mock_open)
    def test_compare_csv(self, mock_file):
        # Prepare test data
        csv1_content = 'gdb,feature_class,feature_class_alias\nvalue1,XXXvalue2,value3\nvalue4,XXX_value5_QX,value6'
        csv2_content = 'gdb,feature_class,feature_class_alias\nvalue1,ABCvalue2,value3\nvalue7,SCE_value8_Q1,value9'
        mock_file.side_effect = [
            mock_open(read_data=csv1_content).return_value,
            mock_open(read_data=csv2_content).return_value
        ]

        csv1 = 'file1.csv'
        csv2 = 'file2.csv'

        # Expected differences
        expected_differences = [
            "Row unique to csv1: ['XXX_value5_QX']",
            "Row unique to csv2: ['SCE_value8_Q1']"
        ]

        # Call the function and get the result
        result = compare_csv("csv1", "csv2", csv1, csv2, False)

        # Check the result
        self.assertEqual(result, expected_differences)

    # test for case where both csv files are the same
    @patch('builtins.open', new_callable=mock_open)
    def test_compare_csv_same(self, mock_file):
        # Prepare test data
        csv1_content = 'gdb,feature_class,feature_class_alias\nvalue1,XXXvalue2,value3\nvalue4,XXX_value5_QX,value6'
        csv2_content = 'gdb,feature_class,feature_class_alias\nvalue1,XXXvalue2,value3\nvalue4,XXX_value5_QX,value6'
        mock_file.side_effect = [
            mock_open(read_data=csv1_content).return_value,
            mock_open(read_data=csv2_content).return_value
        ]

        csv1 = 'file1.csv'
        csv2 = 'file2.csv'

        # Expected differences
        expected_differences = []

        # Call the function and get the result
        result = compare_csv("csv1", "csv2", csv1, csv2, False)

        # Check the result
        self.assertEqual(result, expected_differences)

    # test for case with modified field alias
    @patch('builtins.open', new_callable=mock_open)
    def test_compare_csv_modified_field_alias(self, mock_file):
        # Prepare test data
        csv1_content = 'Geodatabase,Feature Class/Table Name,Alias,Projection Name,Field Name,Field Alias,Field Type,Field Length\n'
        csv1_content +='XXX_2024_QX_2024_05_08_08_29_18_128434,XXX_Camera_2024_QX,,WGS_1984_California_Teale_Albers_FtUS,OBJECTID,OBJECTID,OID,4\n'
        csv1_content +='XXX_2024_QX_2024_05_08_08_29_18_128434,XXX_Camera_2024_QX,,WGS_1984_California_Teale_Albers_FtUS,Shape,Shape,Geometry,0\n'
        csv1_content +='XXX_2024_QX_2024_05_08_08_29_18_128434,XXX_Camera_2024_QX,,WGS_1984_California_Teale_Albers_FtUS,AssetID,Asset ID,String,50\n'
        csv1_content +='XXX_2024_QX_2024_05_08_08_29_18_128434,XXX_Camera_2024_QX,,WGS_1984_California_Teale_Albers_FtUS,SupportStructureID,Support Structure ID,String,50\n'
        csv1_content +='XXX_2024_QX_2024_05_08_08_29_18_128434,XXX_Camera_2024_QX,,WGS_1984_California_Teale_Albers_FtUS,UtilityID,Utility ID,String,10\n'
        csv1_content +='XXX_2024_QX_2024_05_08_08_29_18_128434,XXX_Camera_2024_QX,,WGS_1984_California_Teale_Albers_FtUS,CameraLocationName,Camera Location Name,String,30\n'
        csv1_content +='XXX_2024_QX_2024_05_08_08_29_18_128434,XXX_Camera_2024_QX,,WGS_1984_California_Teale_Albers_FtUS,HFTDClass,HFTD Class,String,10\n'
        csv2_content = 'Geodatabase,Feature Class/Table Name,Alias,Projection Name,Field Name,Field Alias,Field Type,Field Length\n'
        csv2_content +='XXX_2024_QX_2024,XXX_Camera_2024_QX,ignored_fc_alias,WGS_1984_California_Teale_Albers_FtUS,OBJECTID,OBJECTID,OID,4\n'
        csv2_content +='XXX_2024_QX_2024,XXX_Camera_2024_QX,ignored_fc_alias,WGS_1984_California_Teale_Albers_FtUS,Shape,Shape,Geometry,0\n'
        csv2_content +='XXX_2024_QX_2024,XXX_Camera_2024_QX,ignored_fc_alias,WGS_1984_California_Teale_Albers_FtUS,AssetID,Asset ID,String,50\n'
        csv2_content +='XXX_2024_QX_2024,XXX_Camera_2024_QX,ignored_fc_alias,WGS_1984_California_Teale_Albers_FtUS,SupportStructureID,Support Structure ID,String,50\n'
        csv2_content +='XXX_2024_QX_2024,XXX_Camera_2024_QX,ignored_fc_alias,WGS_1984_California_Teale_Albers_FtUS,UtilityID,Utility ID,String,10\n'
        csv2_content +='XXX_2024_QX_2024,XXX_Camera_2024_QX,ignored_fc_alias,WGS_1984_California_Teale_Albers_FtUS,CameraLocationName,MODIFIED FOR TESTING,String,30\n'
        csv2_content +='XXX_2024_QX_2024,XXX_Camera_2024_QX,ignored_fc_alias,WGS_1984_California_Teale_Albers_FtUS,HFTDClass,HFTD Class,String,10\n'
        mock_file.side_effect = [
            mock_open(read_data=csv1_content).return_value,
            mock_open(read_data=csv2_content).return_value
        ]

        csv1 = 'file1.csv'
        csv2 = 'file2.csv'

        # Expected differences
        expected_differences = [r'''Row unique to csv1: ['XXX_Camera_2024_QX', 'WGS_1984_California_Teale_Albers_FtUS', 'CameraLocationName', 'Camera Location Name', 'String', '30']''',
                                r'''Row unique to csv2: ['XXX_Camera_2024_QX', 'WGS_1984_California_Teale_Albers_FtUS', 'CameraLocationName', 'MODIFIED FOR TESTING', 'String', '30']''']

        # Call the function and get the result
        result = compare_csv("csv1", "csv2", csv1, csv2, False)

        # Check the result
        self.assertEqual(result, expected_differences)

    # test with actual csv files
    def test_compare_csv_actual(self):
        # Prepare csv paths
        csv1 = os.path.join(os.path.dirname(__file__),  'gdb1.csv')
        csv2 = os.path.join(os.path.dirname(__file__),  'gdb2.csv')

        # Expected differences
        expected_differences = [
            "Row unique to csv1: ['XXX_Camera_2024_QX', 'WGS_1984_California_Teale_Albers_FtUS', 'CameraLocationName', 'Camera Location Name', 'String', '30']",
            "Row unique to csv2: ['XXX_Camera_2024_QX', 'WGS_1984_California_Teale_Albers_FtUS', 'CameraLocationName', 'MODIFIED FOR TESTING', 'String', '30']"
        ]

        # Call the function and get the result
        result = compare_csv("csv1", "csv2", csv1, csv2, False)

        # Check the result
        self.assertEqual(result, expected_differences)


# This allows the tests to be run when the file is executed directly
if __name__ == '__main__':
    unittest.main()