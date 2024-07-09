# show_me.py

# takes a natural language prompt, interprets it, and generates Python code to make a selection and change the map extent

'''
todo:
    - remove map selection parameter
    - generating code as part of validation?
    - show user the map_info context in the tool UI?
    - edit the code in the tool UI?
    - they can then choose to run it or save it as a new tool
    - consider making the output of the tool another tool with the AI code as the source code
        - no parameters (at first) for simplicity
        - allow the user to change the output format (notebook, python toolbox tool, python file)

    - consider some logic to allow the AI to decide if it did a good job or not
        - if the goal is to make a selection and move the map, see if the extent changed and number of selected features changed
        - if not, ask the user for more information, like string value formats
'''

import requests
import time
import arcpy
import json


python_PROMPT = '''
I have a map in ArcGIS Pro. I've gathered information about this map and will give it to you in JSON format containing information about the map, including the map name, title, description, spatial reference, layers, and properties.

Based on this information, Write Python code that performs the following tasks in ArcGIS Pro:

Selects features from a specified layer based on a given attribute query.
Zooms the map extent to the selected features.
Assume the following inputs:

- user prompt: "show me top 5 points by ID in MyLayer"

You will need to write a SQL query to select features based on an attribute. 

The code should:

- Use the arcpy module.
- Select the features using arcpy.SelectLayerByAttribute_management.
- Zoom the map to the selected features using the arcpy.mapping module.

If the user asks about features with in a distance of another, use arcpy.SelectLayerByLocation_management in addition to arcpy.SelectLayerByAttribute_management.

Please provide the only the complete Python code with these requirements. Do not include any other text or comments.
'''

example_PROMPT = '''
show me the largest polygon in states
'''

example_PYTHON = '''
import arcpy

# User prompt: "show me the largest polygon in states"

# Inputs
layer_name = "states"
attribute_query = "shape_area = (SELECT MAX(shape_area) FROM states)"

# Get the current project and the active view
aprx = arcpy.mp.ArcGISProject("CURRENT")
active_map = aprx.activeMap
active_view = aprx.activeView

# Get the layer
layer = active_map.listLayers(layer_name)[0]

# Select features based on the attribute query
arcpy.management.SelectLayerByAttribute(layer, "NEW_SELECTION", attribute_query)

# Zoom to the extent of the selected features
active_view.camera.setExtent(active_view.getLayerExtent(layer))
'''

def map_to_json(in_map=None, output_json_path=None):
    """
    Generates a JSON object containing information about a map.

    Args:
        in_map (str, optional): The name of the map to get information from. If not provided, the active map in the current project will be used. Defaults to None.
        output_json_path (str, optional): The path to the JSON file where the map information will be saved. If not provided, the map information will not be saved. Defaults to None.

    Returns:
        dict: A dictionary containing information about the map, including the map name, title, description, spatial reference, layers, and properties.

    Raises:
        ValueError: If no active map is found in the current project.

    Notes:
        - The function uses the `arcpy` module to interact with the ArcGIS Pro application.
        - The function collects information about the active map, including the map name, title, description, spatial reference, and layers.
        - For each layer, the function collects information such as the layer name, feature layer status, raster layer status, web layer status, visibility, metadata, spatial reference, extent, fields, record count, source type, geometry type, renderer, and labeling.
        - If `output_json_path` is provided, the map information will be saved to a JSON file at the specified path.

    Example:
        >>> map_info = map_to_json()
        >>> print(map_info)
        {
            "map_name": "MyMap",
            "title": "My Map",
            "description": "This is my map.",
            "spatial_reference": "WGS84",
            "layers": [
                {
                    "name": "MyLayer",
                    "feature_layer": True,
                    "raster_layer": False,
                    "web_layer": False,
                    "visible": True,
                    "metadata": {
                        "title": "My Layer",
                        "tags": ["Tag1", "Tag2"],
                        "summary": "This is my layer.",
                        "description": "This is a description of my layer.",
                        "credits": "Credits for the layer.",
                        "access_constraints": "Access constraints for the layer.",
                        "extent": {
                            "xmin": -180,
                            "ymin": -90,
                            "xmax": 180,
                            "ymax": 90
                        }
                    },
                    "spatial_reference": "WGS84",
                    "extent": {
                        "xmin": -180,
                        "ymin": -90,
                        "xmax": 180,
                        "ymax": 90
                    },
                    "fields": [
                        {
                            "name": "ID",
                            "type": "Integer",
                            "length": 10
                        },
                        {
                            "name": "Name",
                            "type": "String",
                            "length": 50
                        }
                    ],
                    "record_count": 100,
                    "source_type": "FeatureClass",
                    "geometry_type": "Point",
                    "renderer": "SimpleRenderer",
                    "labeling": True
                }
            ],
            "properties": {
                "rotation": 0,
                "units": "DecimalDegrees",
                "time_enabled": False,
                "metadata": {
                    "title": "My Map",
                    "tags": ["Tag1", "Tag2"],
                    "summary": "This is my map.",
                    "description": "This is a description of my map.",
                    "credits": "Credits for the map.",
                    "access_constraints": "Access constraints for the map.",
                    "extent": {
                        "xmin": -180,
                        "ymin": -90,
                        "xmax": 180,
                        "ymax": 90
                    }
                }
            }
        }
    """
	
    # Function to convert metadata to a dictionary
    def metadata_to_dict(metadata):
        if metadata is None:
            return "No metadata"
        
        extent_dict = {}
        if hasattr(metadata, "XMax"):
            extent_dict["xmax"] = metadata.XMax
        if hasattr(metadata, "XMin"):
            extent_dict["xmin"] = metadata.XMin
        if hasattr(metadata, "YMax"):
            extent_dict["ymax"] = metadata.YMax
        if hasattr(metadata, "YMin"):
            extent_dict["ymin"] = metadata.YMin
        
        meta_dict = {
            "title": metadata.title if hasattr(metadata, "title") else "No title",
            "tags": metadata.tags if hasattr(metadata, "tags") else "No tags",
            "summary": metadata.summary if hasattr(metadata, "summary") else "No summary",
            "description": metadata.description if hasattr(metadata, "description") else "No description",
            "credits": metadata.credits if hasattr(metadata, "credits") else "No credits",
            "access_constraints": metadata.accessConstraints if hasattr(metadata, "accessConstraints") else "No access constraints",
            "extent": extent_dict
        }
        return meta_dict

    aprx = arcpy.mp.ArcGISProject("CURRENT")    
    if not in_map:
        active_map = aprx.activeMap
        if not active_map:
            raise ValueError("No active map found in the current project.")
    else:
        active_map = aprx.listMaps(in_map)[0]
        
    # Collect map information
    map_info = {
        "map_name": active_map.name,
        "title": active_map.title if hasattr(active_map, 'title') else "No title",
        "description": active_map.description if hasattr(active_map, 'description') else "No description",
        "spatial_reference": active_map.spatialReference.name,
        "layers": [],
        "properties": {
            "rotation": active_map.rotation if hasattr(active_map, 'rotation') else "No rotation",
            "units": active_map.units if hasattr(active_map, 'units') else "No units",
            "time_enabled": active_map.isTimeEnabled if hasattr(active_map, 'isTimeEnabled') else "No time enabled",
            "metadata": metadata_to_dict(active_map.metadata) if hasattr(active_map, 'metadata') else "No metadata",
        }
    }

    # Iterate through layers and collect information
    for layer in active_map.listLayers():
        layer_info = {
            "name": layer.name,
            "feature_layer": layer.isFeatureLayer,
            "raster_layer": layer.isRasterLayer,
            "web_layer": layer.isWebLayer,
            "visible": layer.visible,
            "metadata": metadata_to_dict(layer.metadata) if hasattr(layer, 'metadata') else "No metadata"
        }

        if layer.isFeatureLayer:
            dataset = arcpy.Describe(layer.dataSource)
            layer_info.update({
                "spatial_reference": dataset.spatialReference.name if hasattr(dataset, "spatialReference") else "Unknown",
                "extent": {
                    "xmin": dataset.extent.XMin,
                    "ymin": dataset.extent.YMin,
                    "xmax": dataset.extent.XMax,
                    "ymax": dataset.extent.YMax
                } if hasattr(dataset, "extent") else "Unknown",
                "fields": [],
                "record_count": 0,
                "source_type": dataset.dataType if hasattr(dataset, "dataType") else "Unknown",
                "geometry_type": dataset.shapeType if hasattr(dataset, "shapeType") else "Unknown",
                "renderer": layer.symbology.renderer.type if hasattr(layer, "symbology") and hasattr(layer.symbology, "renderer") else "Unknown",
                "labeling": layer.showLabels if hasattr(layer, "showLabels") else "Unknown",
            })
            
            # Get fields information
            if hasattr(dataset, "fields"):
                for field in dataset.fields:
                    field_info = {
                        "name": field.name,
                        "type": field.type,
                        "length": field.length
                    }
                    layer_info["fields"].append(field_info)
            
            # Get record count if the layer has records
            if dataset.dataType in ["FeatureClass", "Table"]:
                layer_info["record_count"] = int(arcpy.management.GetCount(layer.dataSource)[0])

        map_info["layers"].append(layer_info)

    if output_json_path:
        # Write the map information to a JSON file
        with open(output_json_path, 'w') as json_file:
            json.dump(map_info, json_file, indent=4)

        print(f"Map information has been written to {output_json_path}")    

    return map_info

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
        "messages": messages,
        "temperature": 0.5, # be more predictable, less creative
        "max_tokens": 500,
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


def generate_python(api_key, map_info, prompt, explain=False):
    """
    Generate python using AI response for a given API key, JSON data, and a question.

    Parameters:
    api_key (str): API key for OpenAI.
    json_data (dict): JSON data containing map information.
    prompt (str): A prompt for the AI referring to a certain selection in the map.

    Returns:
    str: AI-generated insights.
    """
    if prompt:
        messages = [
            {"role": "system", "content": python_PROMPT},
            {"role": "user", "content": f"{example_PROMPT}"},
            {"role": "assistant", "content": f"{example_PYTHON}"},
            {"role": "system", "content": json.dumps(map_info, indent=4)},
            {"role": "user", "content": f"{prompt}"}
        ]

    try:
        code_snippet = get_ai_response(api_key, messages)
        def trim_code_block(code_block):
            # Remove the ```python from the beginning and ``` from the end
            if code_block.startswith("```python"):
                code_block = code_block[len("```python"):].strip()
            if code_block.endswith("```"):
                code_block = code_block[:-len("```")].strip()
            return code_block
        
        # trim response and show to user through message
        code_snippet = trim_code_block(code_snippet)
        msg = "AI generated code:\n\n" + code_snippet
        arcpy.AddMessage(msg)

    except Exception as e:
        arcpy.AddError(str(e))
        return
    
    return code_snippet
        
if __name__ == "__main__":
    api_key = arcpy.GetParameterAsText(0) # string
    prompt = arcpy.GetParameterAsText(1) # string
    eval = arcpy.GetParameterAsText(2) # boolean

    code_snippet = generate_python(api_key, map_to_json(), prompt.strip())
    
    if eval:
        try:
            # execute the code
            exec(code_snippet)

        # catch AttributeError: 'NoneType' object has no attribute 'camera'
        except AttributeError as e:
            arcpy.AddError(f"{e}\n\nMake sure a map view is active.")
        except Exception as e:
            arcpy.AddError(f"{e}\n\nThe code may be invalid. Please check the code and try again.")