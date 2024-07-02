'''
This script gathers detailed information about the active map in an ArcGIS Pro project and exports it to a JSON file. It collects:

- **Map Information**:
  - Name
  - Title
  - Description
  - Spatial Reference
  - Rotation
  - Units
  - Time-enabled Status
  - Metadata

- **Layer Information** (for each feature layer):
  - Name
  - Data Type
  - Visibility
  - Spatial Reference
  - Extent
  - Source Type
  - Geometry Type
  - Renderer
  - Labeling Status

- **Field Information** (for each layer):
  - Name
  - Type
  - Length

- **Record Count** (for each layer)

This comprehensive dataset provides an in-depth overview of the map's structure and contents, suitable for further analysis and integration with other systems.


'''

import arcpy
import json

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
        arcpy.AddMessage(in_map)
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
            if layer.isFeatureLayer:
                dataset = arcpy.Describe(layer.dataSource)
                
                layer_info = {
                    "name": layer.name,
                    "data_type": dataset.dataType,
                    "visible": layer.visible,
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
                    "metadata": metadata_to_dict(layer.metadata) if hasattr(layer, 'metadata') else "No metadata"
                }
                
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
