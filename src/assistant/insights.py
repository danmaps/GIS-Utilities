import requests
import time
import arcpy
import json

description_PROMPT = '''
I have a JSON containing detailed information about a map in ArcGIS Pro. The JSON includes the following details:

- **Map Information**:
  - Map Name
  - Title
  - Description
  - Spatial Reference
  - Properties (Rotation, Units, Time Enabled, Metadata)

- **Layer Information** (for feature layers):
  - Name
  - Data Type
  - Visibility
  - Spatial Reference
  - Extent (xmin, ymin, xmax, ymax)
  - Source Type
  - Geometry Type
  - Renderer
  - Labeling Status
  - Metadata (Title, Tags, Summary, Description, Credits, Access Constraints, Extent)

- **Field Information** (for each layer):
  - Field Name
  - Field Type
  - Field Length

- **Record Count** (for each layer)

Based on this information, please provide a comprehensive description of the map, including its purpose, the significance of its layers, and any notable features or insights. Also, suggest potential analyses or visualizations that could be performed using this map data.

Feel free to omit details if the information is missing from the JSON.
'''

question_PROMPT = '''
I have a JSON containing detailed information about a map in ArcGIS Pro. The JSON includes the following details:

- **Map Information**:
  - Map Name
  - Title
  - Description
  - Spatial Reference
  - Properties (Rotation, Units, Time Enabled, Metadata)

- **Layer Information** (for feature layers):
  - Name
  - Data Type
  - Visibility
  - Spatial Reference
  - Extent (xmin, ymin, xmax, ymax)
  - Source Type
  - Geometry Type
  - Renderer
  - Labeling Status
  - Metadata (Title, Tags, Summary, Description, Credits, Access Constraints, Extent)

- **Field Information** (for each layer):
  - Field Name
  - Field Type
  - Field Length

- **Record Count** (for each layer)

Based on this information, please answer the users's questions.
'''

def map_to_json(in_map=None, output_json_path=None):

    # Function to convert metadata to a dictionary
    def metadata_to_dict(metadata):
        if metadata is None:
            return "No metadata"
        
        extent_dict = {
            "xmax": metadata.XMax if hasattr(metadata, "XMax") else "No extent",
            "xmin": metadata.XMin if hasattr(metadata, "XMin") else "No extent",
            "ymax": metadata.YMax if hasattr(metadata, "YMax") else "No extent",
            "ymin": metadata.YMin if hasattr(metadata, "YMin") else "No extent"
        }
        
        meta_dict = {
            "title": metadata.title,
            "tags": metadata.tags,
            "summary": metadata.summary,
            "description": metadata.description,
            "credits": metadata.credits,
            "access_constraints": metadata.accessConstraints,
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

def generate_insights(api_key, json_data, question=None):
    if question:
        messages = [
            {"role": "system", "content": question_PROMPT},
            {"role": "system", "content": json.dumps(json_data, indent=4)},
            {"role": "user", "content": question}
        ]
    else:
        messages = [
            {"role": "system", "content": description_PROMPT},
            {"role": "user", "content": json.dumps(json_data, indent=4)}
        ]

    try:
        insights = get_ai_response(api_key, messages)
        arcpy.AddMessage(insights)
    except Exception as e:
        arcpy.AddError(str(e))
        return
    
    return insights
        
if __name__ == "__main__":
    api_key = arcpy.GetParameterAsText(0)
    selected_map = arcpy.GetParameterAsText(1)
    question = arcpy.GetParameterAsText(2)
    
    if selected_map:
        map_info = map_to_json(selected_map)
    else:
        map_info = map_to_json() # current active view
    
    # Generate insights based on the JSON data
    generate_insights(api_key, map_info, question)
