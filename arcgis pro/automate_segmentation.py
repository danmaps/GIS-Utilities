import arcpy
import re
from arcgis.gis import GIS
from arcgis.features import FeatureLayer

# Log into ArcGIS Online
gis = GIS("Pro")


def clip_intersect(lyr):
    arcpy.analysis.Clip(
        in_features=lyr,
        clip_features="sce_HighFireRiskArea",
        out_feature_class=f"{lyr}_Clip",
    )
    arcpy.analysis.Intersect(
        in_features=f"{lyr}_Clip #;Subtrans_Segments #",
        out_feature_class=rf"{lyr}_Intersect",
    )

def create_field_mappings(target, join, join_field, output_field_name=None, merge_rule=None, delimiter=', ', output_field_length=255):
    """
    Creates field mappings for spatial join, setting output field as text type and specified length.

    Parameters:
    target (str): The target feature class for the join.
    join (str): The join feature class.
    join_field (str): The field name in the join feature class to match properties.
    output_field_name (str, optional): The name for the output field. Default is the same as join_field.
    merge_rule (str, optional): The merge rule to apply ('Join', 'Sum', 'Mean', etc.). Default is None.
    delimiter (str, optional): The delimiter for 'Join' merge rule. Default is ', '.
    output_field_length (int, optional): The length for the output field. Default is 255.

    Returns:
    arcpy.FieldMappings: The field mappings for the spatial join.
    """
    # Create field mappings
    field_mappings = arcpy.FieldMappings()
    field_mappings.addTable(target)

    # Create and set up the field map
    field_map = arcpy.FieldMap()
    field_map.addInputField(join, join_field)

    # Set output field properties
    out_field = arcpy.Field()
    out_field.name = output_field_name if output_field_name else join_field
    out_field.aliasName = out_field.name
    if output_field_name == 'COUNTY':
        out_field.type = "String"  # Explicitly set as text type
        out_field.length = output_field_length  # Set length to 255

    if merge_rule:
        field_map.mergeRule = merge_rule
        if merge_rule.lower() == 'join':
            field_map.joinDelimiter = delimiter

    field_map.outputField = out_field

    # Add the field map to the field mappings
    field_mappings.addFieldMap(field_map)

    return field_mappings


def perform_spatial_join(target_fc, join_fc, out_fc, join_field, output_field_name, merge_rule=None):
    """
    Performs a spatial join with field mappings.

    Parameters:
    target_fc (str): The target feature class for the join.
    join_fc (str): The join feature class.
    out_fc (str): The output feature class.
    join_field (str): The field name in the join feature class to match properties.
    output_field_name (str): The name for the output field.
    merge_rule (str, optional): The merge rule to apply ('Join', 'Sum', 'Mean', etc.).
    """
    arcpy.analysis.SpatialJoin(
        target_features=target_fc,
        join_features=join_fc,
        out_feature_class=out_fc,
        join_operation="JOIN_ONE_TO_ONE",
        join_type="KEEP_ALL",
        match_option="INTERSECT",
        field_mapping=create_field_mappings(
            target=target_fc, 
            join=join_fc, 
            join_field=join_field,
            output_field_name=output_field_name,
            merge_rule=merge_rule
        )
    )
def validate_and_calculate_field(layer, field, expression):
    # Validate field exists
    fields = [f.name for f in arcpy.ListFields(layer)]
    if field not in fields:
        raise ValueError(f"Field {field} does not exist in layer")

    # Validate expression fields exist
    def get_fields_from_expression(expression):
        matches = re.findall(r"!\w+!", expression)
        return [m[1:-1] for m in matches]

    expr_fields = get_fields_from_expression(expression)
    missing_fields = set(expr_fields) - set(fields)
    if missing_fields:
        raise ValueError(f"Expression contains invalid fields: {missing_fields}")

    # Calculate field if valid
    arcpy.management.CalculateField(layer, field, expression, "PYTHON3")

def schema_conform(source_fc, reference_fc):
    """
    Adjusts the schema of the source feature class to match the reference feature class by removing extra fields,
    excluding system-managed fields. For shapefiles, field names are truncated to 10 characters.

    Parameters:
    source_fc (str): Path to the source feature class whose schema needs adjustment.
    reference_fc (str): Path to the reference feature class to match schema with.
    """
    # System-managed fields that should not be removed
    protected_fields = {'OBJECTID', 'Shape_Length', 'Shape_Area', 'FID', 'Shape'}

    # Check if reference_fc is a shapefile
    is_shapefile = reference_fc.lower().endswith('.shp')

    # Get field names for both feature classes
    source_fields = {f.name for f in arcpy.ListFields(source_fc) if f.name not in protected_fields}
    reference_fields = {f.name for f in arcpy.ListFields(reference_fc)}
    # arcpy.AddMessage(f"{source_fc}:{len(source_fields)} fields") # debug
    # arcpy.AddMessage(f"{os.path.basename(reference_fc)}:{len(reference_fields)} fields") # debug

    # If reference_fc is a shapefile, truncate source field names to first 10 characters
    if is_shapefile:
        source_fields = {f[:10] for f in source_fields}

    # Identify fields to remove (present in source but not in reference)
    fields_to_remove = source_fields - reference_fields

    # Remove extra fields from source feature class
    if fields_to_remove:
        # If it's a shapefile, we need to map back truncated field names to original field names
        if is_shapefile:
            original_fields_to_remove = [f for f in arcpy.ListFields(source_fc) if f.name[:10] in fields_to_remove]
            fields_to_remove = [f.name for f in original_fields_to_remove]

        arcpy.DeleteField_management(source_fc, fields_to_remove)
        # arcpy.AddMessage(f"Removed fields from {source_fc}: {fields_to_remove}") # debug
        # source_fields = {f.name for f in arcpy.ListFields(source_fc) if f.name not in protected_fields}
        # arcpy.AddMessage(f"{source_fc}:{len(source_fields)} fields") # debug
        # arcpy.AddMessage(f"{os.path.basename(reference_fc)}:{len(reference_fields)} fields") # debug
    else:
        arcpy.AddMessage(f"No fields to remove. {source_fc} schema already conforms to {reference_fc}.")


def script_tool(param0, param1):

    # Dictionary with layer IDs and their respective indices
    layer_details = {
        "bulktrans": ("80c86dd5aa184264896437b0e1d8e54b", 0),
        "subtrans": ("b653952755af48fd85a31680e07a6641", 0),
        "sce_HighFireRiskArea": ("38a2e08043e04268a1a386e63c3c69bd", 0),
        "Subtrans_Segments": ("71e126217f44483091982e52804e4171", 1),
        "districts": ("4414e648847445ffa6019523850f8d7f", 0),
        "counties": ("9998b507eef44f9db5ff962268d08ab6", 0),
    }

    arcpy.AddMessage("MakeFeatureLayer...")
    # Create feature layers using the details from the dictionary
    for layer_name, (layer_id, index) in layer_details.items():
        layer_url = gis.content.get(layer_id).layers[index].url
        arcpy.MakeFeatureLayer_management(layer_url, layer_name)

    # clip to HFRA and intersect with Segments
    arcpy.AddMessage("Clip to HFRA and intersect with Segments...")
    clip_intersect("bulktrans")
    clip_intersect("subtrans")

    arcpy.AddMessage("SpatialJoin to counties and districts...")
    # arcpy.AddMessage([f.name for f in arcpy.ListFields("subtrans_Intersect")]) # debug
    perform_spatial_join("bulktrans_Intersect", "counties", "bulktrans_counties", "NAME", "COUNTY", "Join")
    perform_spatial_join("bulktrans_counties", "districts", "bulktrans_districts", "NUMBER_", "DISTRICT")
    arcpy.management.AlterField("subtrans_Intersect", "NAME", "CIRCUIT_NAME")
    perform_spatial_join("subtrans_Intersect", "counties", "subtrans_counties", "NAME", "COUNTY", "Join")
    perform_spatial_join("subtrans_counties", "districts", "subtrans_districts", "NUMBER_", "DISTRICT")

    # Add missing fields
    arcpy.AddMessage("Add fields...")

    for lyr in ["bulktrans_districts", "subtrans_districts"]:
        arcpy.management.AddFields(
            in_table=lyr,
            field_description="CIRCUIT_SE TEXT # 255 # #;WIRE_CLASS TEXT # 50 # #;SUBSTATION TEXT # 255 # #;GUST_THRES LONG # # # #;WIND_THRES LONG # # # #",
        )
        arcpy.AlterField_management(lyr, "KV", "VOLTAGE")
    
    arcpy.AddMessage("Calculate fields...")
    validate_and_calculate_field("bulktrans_districts", "CIRCUIT_SE", "!CIRCUIT_NAME!.upper()+'_'+!SEGMENTS!")
    validate_and_calculate_field("bulktrans_districts", "WIRE_CLASS", '"Transmission"')
    validate_and_calculate_field("bulktrans_districts", "SUBSTATION", "!CIRCUIT_NAME!.split('-')[0].upper()")
    arcpy.AddMessage([f.name for f in arcpy.ListFields("subtrans_districts")]) # debug
    validate_and_calculate_field("subtrans_districts", "CIRCUIT_ID", "'ET-'+!CIRCUIT_NO!.split('-')[0]")  # 00158-BT -> ET-00158
    validate_and_calculate_field("subtrans_districts", "CIRCUIT_SE", "!CIRCUIT_NAME!.upper()+'_'+!SEGMENTS!")
    validate_and_calculate_field("subtrans_districts", "WIRE_CLASS", '"Transmission"')
    validate_and_calculate_field("subtrans_districts", "SUBSTATION", "!CIRCUIT_NAME!.split('-')[0].upper()")

    arcpy.AddMessage("Remove extra fields...")
    schema_conform("bulktrans_districts", r"P:\PROJECTS\Special_Projects\Business_Resiliency_IMT\Data\ArcPRO_Project_ALL_Segmentation\Tools\BulkTrans_segments_HFA_EXAMPLE.shp")
    schema_conform("subtrans_districts", r"P:\PROJECTS\Special_Projects\Business_Resiliency_IMT\Data\ArcPRO_Project_ALL_Segmentation\Tools\SubTrans_segments_HFA_EXAMPLE.shp")

    arcpy.AddMessage("Export...")
    arcpy.conversion.ExportFeatures("bulktrans_districts", param0)
    arcpy.conversion.ExportFeatures("subtrans_districts", param1)
    
    validate_and_calculate_field(param1, "CIRCUIT_NO", "'ET-'+!CIRCUIT_NO!.split('-')[0]")  # 00158-BT -> ET-00158

    return

if __name__ == "__main__":
    param0 = arcpy.GetParameterAsText(0)
    param1 = arcpy.GetParameterAsText(1)

    script_tool(param0, param1)