import arcpy
import json

def map_to_json(mapx_file_path, output_json_path):
    # Load the .mapx file
    aprx = arcpy.mp.ArcGISProject(mapx_file_path)
    mapx_info = {}

    # Iterate through all maps in the project
    for map in aprx.listMaps():
        map_info = {
            "map_name": map.name,
            "spatial_reference": map.spatialReference.name,
            "layers": []
        }
        
        for layer in map.listLayers():
            if layer.isFeatureLayer:
                layer_info = {
                    "name": layer.name,
                    "type": layer.type,
                    "visible": layer.visible,
                    "spatial_reference": layer.spatialReference.name if layer.spatialReference else "Unknown",
                    "extent": {
                        "xmin": layer.getExtent().XMin,
                        "ymin": layer.getExtent().YMin,
                        "xmax": layer.getExtent().XMax,
                        "ymax": layer.getExtent().YMax
                    } if layer.getExtent() else "Unknown",
                    "fields": [],
                    "record_count": 0
                }
                
                # Get fields information
                fields = arcpy.ListFields(layer.dataSource)
                for field in fields:
                    field_info = {
                        "name": field.name,
                        "type": field.type,
                        "length": field.length
                    }
                    layer_info["fields"].append(field_info)
                
                # Get record count
                layer_info["record_count"] = arcpy.management.GetCount(layer.dataSource)[0]
                
                map_info["layers"].append(layer_info)

        mapx_info[map.name] = map_info

    # Write the map information to a JSON file
    with open(output_json_path, 'w') as json_file:
        json.dump(mapx_info, json_file, indent=4)

    print(f"Map information has been written to {output_json_path}")

# Example usage
mapx_file_path = '/mnt/data/California Coastline.mapx'
output_json_path = 'map_info.json'
map_to_json(mapx_file_path, output_json_path)
