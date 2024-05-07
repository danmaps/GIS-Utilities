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


# This allows the tests to be run when the file is executed directly
if __name__ == '__main__':
    unittest.main()