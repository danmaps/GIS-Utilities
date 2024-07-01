# todo:
#   record a compelling demo
#   handle too-large geojson output gracefully instead of a cryptic error message

# potential features:
#   conversation context (create a point, ok thanks, now buffer that)
#   
#   add context
#       layers from active map
#       properties like on/off, extent, geometry type, feature count, symbology, fields
#       map properties, like extent
#       current view as a png
#       
#   give the AI abilities
#       turn layers on/off
#       make selections
#       pan/zoom, zoom to layer, zoom to selection
#       use geoprocessing tools (with code interpreter?)
#
#   sounds like a mixture of assistants
#       so far i've just got a simple blind feature layer creator
#       if i give it vision and some friends to talk to it'll have a better time
#   
#   attaching data
#       instead of winging it, use authoritative references to existing geometry
#       need to clarify if we are talking about reproducing geometry or using it for inspiration
#
#   "watch" the user operate editing tools and then draw on the map in a similar way
#       continue drawing
#       like a copilot for editing GIS data
#       need something like github copilot tab complete, where the suggestions are shown to the user and approved/dismissed
#       record a macro, start drawing, the information about the drawing and how it related to existing geometry is saved
#       this information is used by the AI as a "style guide" for continued drawing, which it does
#

import requests
import time
import arcpy
import json
import os

def get_ai_response(api_key, messages):
    """
    Generates an AI response for a given set of messages using the chat completions endpoint.

    Parameters:
    api_key (str): API key for OpenAI.
    messages (list): List of message dictionaries for the AI chat.

    Returns:
    str: AI response.
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4o",
        "response_format": { "type": "json_object" }, # this is very important
        "messages": messages
    }

    for _ in range(3):
        try:
            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data, verify=False)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"].strip()
        except requests.exceptions.RequestException as e:
            arcpy.AddWarning(f"Retrying AI response generation due to: {e}")
            time.sleep(1)
    raise Exception("Failed to get AI response after retries")

def infer_geometry_type(geojson_data):
    """
    Infers the geometry type from GeoJSON data.

    Parameters:
    geojson_data (dict): GeoJSON data as a dictionary.

    Returns:
    str: Geometry type compatible with ArcGIS Pro.

    Raises:
    ValueError: If multiple geometry types are found in the GeoJSON data.
    """
    geometry_type_map = {
        "Point": "Point",
        "MultiPoint": "Multipoint",
        "LineString": "Polyline",
        "MultiLineString": "Polyline",
        "Polygon": "Polygon",
        "MultiPolygon": "Polygon"
    }

    geometry_types = set()
    for feature in geojson_data["features"]:
        geometry_type = feature["geometry"]["type"]
        arcpy.AddMessage(f"found {geometry_type}")
        geometry_types.add(geometry_type_map.get(geometry_type))

    if len(geometry_types) == 1:
        return geometry_types.pop()
    else:
        raise ValueError("Multiple geometry types found in GeoJSON")
    
def expand_extent(extent, factor=1.1):
    """
    Expands the given extent by the specified factor.

    Parameters:
    extent (arcpy.Extent): The extent to be expanded.
    factor (float): The factor by which to expand the extent.

    Returns:
    arcpy.Extent: The expanded extent.
    """
    width = extent.XMax - extent.XMin
    height = extent.YMax - extent.YMin
    expanded_extent = arcpy.Extent(
        extent.XMin - width * (factor - 1) / 2,
        extent.YMin - height * (factor - 1) / 2,
        extent.XMax + width * (factor - 1) / 2,
        extent.YMax + height * (factor - 1) / 2
    )
    return expanded_extent


def fetch_geojson(api_key, query, output_layer_name):
    """
    Fetches GeoJSON data using an AI response and creates a feature layer in ArcGIS Pro.

    Parameters:
    api_key (str): API key for OpenAI.
    query (str): User query for the AI to generate GeoJSON data.
    output_layer_name (str): Name of the output layer to be created in ArcGIS Pro.
    """
    messages = [
        {"role": "system", "content": "You are a helpful assistant that always only returns valid GeoJSON in response to user queries. Don't use too many vertices. Include somewhat detailed geometry and any attributes you think might be relevant. Include factual information. If you want to communicate text to the user, you may use a message property in the attributes of geometry objects. For compatibility with ArcGIS Pro, avoid multiple geometry types in the GeoJSON output. For example, don't mix points and polygons."},
        {"role": "user", "content": query}
    ]

    try:
        geojson_data = get_ai_response(api_key, messages)

        # Add debugging to inspect the raw GeoJSON response
        arcpy.AddMessage(f"Raw GeoJSON data: {geojson_data}")

        geojson_data = json.loads(geojson_data)  # Assuming single response for simplicity
        geometry_type = infer_geometry_type(geojson_data)
    except Exception as e:
        arcpy.AddError(str(e))
        return

    geojson_file = os.path.join("geojson_output", f"{output_layer_name}.geojson")
    with open(geojson_file, 'w') as f:
        json.dump(geojson_data, f)

    arcpy.conversion.JSONToFeatures(geojson_file, output_layer_name, geometry_type=geometry_type)
    
    aprx = arcpy.mp.ArcGISProject("CURRENT")
    if aprx.activeMap:
        active_map = aprx.activeMap
        output_layer_path = os.path.join(aprx.defaultGeodatabase, output_layer_name)
        arcpy.AddMessage(f"Adding layer from: {output_layer_path}")
        
        try:
            active_map.addDataFromPath(output_layer_path)
            layer = active_map.listLayers(output_layer_name)[0]

            # Get the data source and its extent
            desc = arcpy.Describe(layer.dataSource)
            extent = desc.extent

            if extent:
                expanded_extent = expand_extent(extent)
                active_view = aprx.activeView

                # Check if the active view is a map view
                if hasattr(active_view, 'camera'):
                    active_view.camera.setExtent(expanded_extent)
                    arcpy.AddMessage(f"Layer '{output_layer_name}' added and extent set successfully.")
                else:
                    arcpy.AddWarning("The active view is not a map view, unable to set the extent.")
            else:
                arcpy.AddWarning(f"Unable to get extent for layer '{output_layer_name}'.")

        except Exception as e:
            arcpy.AddError(f"Error processing layer: {str(e)}")
    else:
        arcpy.AddWarning("No active map found in the current project.")
        
if __name__ == "__main__":
    api_key = arcpy.GetParameterAsText(0)
    query = arcpy.GetParameterAsText(1)
    output_layer_name = arcpy.GetParameterAsText(2)

    fetch_geojson(api_key, query, output_layer_name)
