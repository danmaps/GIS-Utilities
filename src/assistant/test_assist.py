import unittest
from unittest.mock import patch

from assist import *

class MapToJsonTestCase(unittest.TestCase):
    @patch('arcpy.mp.ArcGISProject')
    def test_no_active_map(self, mock_ArcGISProject):
        mock_ArcGISProject.return_value.activeMap = None
        with self.assertRaises(ValueError):
            map_to_json()

    @patch('arcpy.mp.ArcGISProject')
    def test_active_map_with_no_title(self, mock_ArcGISProject):
        mock_ArcGISProject.return_value.activeMap = MockMap(title=None)
        map_info = map_to_json()
        self.assertEqual(map_info['title'], 'No title')

    @patch('arcpy.mp.ArcGISProject')
    def test_active_map_with_no_description(self, mock_ArcGISProject):
        mock_ArcGISProject.return_value.activeMap = MockMap(description=None)
        map_info = map_to_json()
        self.assertEqual(map_info['description'], 'No description')

    @patch('arcpy.mp.ArcGISProject')
    def test_active_map_with_no_spatial_reference(self, mock_ArcGISProject):
        mock_ArcGISProject.return_value.activeMap = MockMap(spatialReference=None)
        map_info = map_to_json()
        self.assertEqual(map_info['spatial_reference'], 'Unknown')

    @patch('arcpy.mp.ArcGISProject')
    def test_active_map_with_no_metadata(self, mock_ArcGISProject):
        mock_ArcGISProject.return_value.activeMap = MockMap(metadata=None)
        map_info = map_to_json()
        self.assertEqual(map_info['properties']['metadata'], 'No metadata')

    @patch('arcpy.mp.ArcGISProject')
    def test_active_map_with_no_rotation(self, mock_ArcGISProject):
        mock_ArcGISProject.return_value.activeMap = MockMap(rotation=None)
        map_info = map_to_json()
        self.assertEqual(map_info['properties']['rotation'], 'No rotation')

    @patch('arcpy.mp.ArcGISProject')
    def test_active_map_with_no_units(self, mock_ArcGISProject):
        mock_ArcGISProject.return_value.activeMap = MockMap(units=None)
        map_info = map_to_json()
        self.assertEqual(map_info['properties']['units'], 'No units')

    @patch('arcpy.mp.ArcGISProject')
    def test_active_map_with_no_time_enabled(self, mock_ArcGISProject):
        mock_ArcGISProject.return_value.activeMap = MockMap(isTimeEnabled=None)
        map_info = map_to_json()
        self.assertEqual(map_info['properties']['time_enabled'], 'No time enabled')

    @patch('arcpy.mp.ArcGISProject')
    def test_active_map_with_no_layers(self, mock_ArcGISProject):
        mock_ArcGISProject.return_value.activeMap = MockMap(layers=[])
        map_info = map_to_json()
        self.assertEqual(map_info['layers'], [])

    @patch('arcpy.mp.ArcGISProject')
    def test_active_map_with_layer_with_no_title(self, mock_ArcGISProject):
        mock_ArcGISProject.return_value.activeMap = MockMap(layers=[MockLayer(title=None)])
        map_info = map_to_json()
        self.assertEqual(map_info['layers'][0]['title'], 'No title')


class TestGetOpenAIResponse(unittest.TestCase):
    def test_get_openai_response(self):
        try:
            import requests
        except ModuleNotFoundError:
            return

        api_key = "NOT_A_REAL_API_KEY"
        messages = [{"role": "system", "content": "This is a test."}]

        response = get_openai_response(api_key, messages)
        self.assertEqual(response, "No output was generated.")

    def test_get_openai_response_with_api_key(self):
        try:
            import requests
        except ModuleNotFoundError:
            return

        api_key = "NOT_A_REAL_API_KEY"
        messages = [{"role": "system", "content": "This is a test."}]

        response = get_openai_response(api_key, messages)
        self.assertEqual(response, "No output was generated.")