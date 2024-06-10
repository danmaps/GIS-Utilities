import unittest
import arcpy
from automate_segmentation import schema_conform
from unittest.mock import patch, Mock

class MockField:
    def __init__(self, name):
        self.name = name

class TestSchemaConform(unittest.TestCase):
    mock_delete_field = Mock()
    arcpy.DeleteField_management = mock_delete_field
    @patch('arcpy.ListFields')
    @patch('arcpy.DeleteField_management')
    def test_non_shapefile_source_has_extra_fields(self, mock_delete_field, mock_list_fields):
        # Mock the ListFields function to return a list of custom MockField objects
        mock_list_fields.side_effect = [
            [MockField('OBJECTID'), MockField('Shape_Length'), MockField('Shape_Area'), MockField('FID'), MockField('Shape'), MockField('Field1'), MockField('Field2')],
            [MockField('OBJECTID'), MockField('Shape_Length'), MockField('Shape_Area'), MockField('FID'), MockField('Shape'), MockField('Field1')]
        ]

        # Call the function with mocked inputs
        schema_conform('source.gdb/fc', 'reference.gdb/fc')

        # Check that DeleteField_management was called with the correct arguments
        mock_delete_field.assert_called_with('source.gdb/fc', {'Field2'})

    @patch('arcpy.ListFields')
    @patch('arcpy.DeleteField_management')
    def test_shapefile_source_has_extra_fields(self, mock_delete_field, mock_list_fields):
        # Mock the ListFields function to return a list of custom MockField objects
        mock_list_fields.side_effect = [
            [MockField('OBJECTID'), MockField('Shape_Length'), MockField('Shape_Area'), MockField('FID'), MockField('Shape'), MockField('Field1Field2')],
            [MockField('OBJECTID'), MockField('Shape_Length'), MockField('Shape_Area'), MockField('FID'), MockField('Shape'), MockField('Field1')],
            [MockField('OBJECTID'), MockField('Shape_Length'), MockField('Shape_Area'), MockField('FID'), MockField('Shape'), MockField('Field1Field2')]
        ]

        # Call the function with mocked inputs
        schema_conform('source.shp', 'reference.shp')

        # Check that DeleteField_management was called with the correct arguments
        mock_delete_field.assert_called_with('source.shp', ['Field1Field2'])

    @patch('arcpy.ListFields')
    @patch('arcpy.DeleteField_management')
    def test_source_schema_already_conforms(self, mock_delete_field, mock_list_fields):
        # Mock the ListFields function to return a list of field objects
        mock_list_fields.side_effect = [
            [MockField(name='OBJECTID'), MockField(name='Shape_Length'), MockField(name='Shape_Area'), MockField(name='FID'), MockField(name='Shape'), MockField(name='Field1')],
            [MockField(name='OBJECTID'), MockField(name='Shape_Length'), MockField(name='Shape_Area'), MockField(name='FID'), MockField(name='Shape'), MockField(name='Field1')]
        ]

        # Call the function with mocked inputs
        schema_conform('source.gdb/fc', 'reference.gdb/fc')
        # Check that DeleteField_management was not called
        mock_delete_field.assert_not_called()

if __name__ == '__main__':
    unittest.main()