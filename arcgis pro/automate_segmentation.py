import arcpy
import re
from arcgis.gis import GIS
from arcgis.features import FeatureLayer

# Log into ArcGIS Online
gis = GIS("Pro")
def script_tool(param0, param1):
    arcpy.AddMessage("MakeFeatureLayer...")

    arcpy.MakeFeatureLayer_management(gis.content.get("80c86dd5aa184264896437b0e1d8e54b").layers[0].url, "bulktrans")
    arcpy.MakeFeatureLayer_management(gis.content.get("b653952755af48fd85a31680e07a6641").layers[0].url, "subtrans")

    arcpy.MakeFeatureLayer_management(gis.content.get("38a2e08043e04268a1a386e63c3c69bd").layers[0].url, "sce_HighFireRiskArea")
    arcpy.MakeFeatureLayer_management(gis.content.get("71e126217f44483091982e52804e4171").layers[1].url, "Subtrans_Segments")

    arcpy.MakeFeatureLayer_management(gis.content.get("4414e648847445ffa6019523850f8d7f").layers[0].url, "districts")
    arcpy.MakeFeatureLayer_management(gis.content.get("9998b507eef44f9db5ff962268d08ab6").layers[0].url, "counties")

    # clip to HFRA and intersect with Segments
    arcpy.AddMessage("clip to HFRA and intersect with Segments...")

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
    clip_intersect("bulktrans")
    clip_intersect("subtrans")

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

    arcpy.AddMessage("SpatialJoin to counties and districts...")

    arcpy.analysis.SpatialJoin(
        target_features="bulktrans_Intersect",
        join_features="counties",
        out_feature_class="bulktrans_counties",
        join_operation="JOIN_ONE_TO_ONE",
        join_type="KEEP_ALL",
        match_option="INTERSECT",
        field_mapping=create_field_mappings(
            target="bulktrans_Intersect", 
            join="counties", 
            join_field="NAME",
            output_field_name="COUNTY",
            merge_rule="Join"
        )
    )

    arcpy.analysis.SpatialJoin(
        target_features="bulktrans_counties",
        join_features="districts",
        out_feature_class="bulktrans_districts",
        join_operation="JOIN_ONE_TO_ONE",
        join_type="KEEP_ALL",
        match_option="INTERSECT",
        field_mapping=create_field_mappings(
            target="bulktrans_counties", 
            join="districts",
            join_field="NUMBER_",
            output_field_name='DISTRICT'
        )
    )

    arcpy.management.AlterField(
        in_table="subtrans_Intersect",
        field="NAME",
        new_field_name="CIRCUIT_NAME"
    )

    arcpy.analysis.SpatialJoin(
        target_features="subtrans_Intersect",
        join_features="counties",
        out_feature_class="subtrans_counties",
        join_operation="JOIN_ONE_TO_ONE",
        join_type="KEEP_ALL",
        match_option="INTERSECT",
        field_mapping=create_field_mappings(
            target="subtrans_Intersect", 
            join="counties", 
            join_field="NAME",
            output_field_name="COUNTY",
            merge_rule="Join"
        )
    )

    arcpy.analysis.SpatialJoin(
        target_features="subtrans_counties",
        join_features="districts",
        out_feature_class="subtrans_districts",
        join_operation="JOIN_ONE_TO_ONE",
        join_type="KEEP_ALL",
        match_option="INTERSECT",
        field_mapping=create_field_mappings(
            target="subtrans_counties", 
            join="districts",
            join_field="NUMBER_",
            output_field_name='DISTRICT'
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

    # Add missing fields
    arcpy.AddMessage("Add missing fields...")

    for lyr in ["bulktrans_districts", "subtrans_districts"]:
        arcpy.management.AddFields(
            in_table=lyr,
            field_description="CIRCUIT_SE TEXT # 255 # #;WIRE_CLASS TEXT # 50 # #;SUBSTATION TEXT # 255 # #;GUST_THRES LONG # # # #;WIND_THRES LONG # # # #",
        )
    arcpy.AddMessage("Calculate fields...")
    # Calculate BulkTrans fields
    validate_and_calculate_field("bulktrans_districts", "CIRCUIT_SE", "!CIRCUIT_NAME!.upper()+'_'+!SEGMENTS!")
    validate_and_calculate_field("bulktrans_districts", "WIRE_CLASS", '"Transmission"')
    validate_and_calculate_field("bulktrans_districts", "SUBSTATION", "!CIRCUIT_NAME!.split('-')[0].upper()")

    # Calculate SubTrans fields
    # validate_and_calculate_field("subtrans_districts", "CIRCUIT_NO", "'ET-'+!CIRCUIT_NO!.split('-')[0]")  # 00158-BT -> ET-00158
    validate_and_calculate_field("subtrans_districts", "CIRCUIT_SE", "!CIRCUIT_NAME!.upper()+'_'+!SEGMENTS!")
    validate_and_calculate_field("subtrans_districts", "WIRE_CLASS", '"Transmission"')
    validate_and_calculate_field("subtrans_districts", "SUBSTATION", "!CIRCUIT_NAME!.split('-')[0].upper()")

    def schema_conform(source_fc, reference_fc):
        """
        Adjusts the schema of the source feature class to match the reference feature class by removing extra fields,
        excluding system-managed fields.

        Parameters:
        source_fc (str): Path to the source feature class whose schema needs adjustment.
        reference_fc (str): Path to the reference feature class to match schema with.
        """
        # System-managed fields that should not be removed
        protected_fields = {'OBJECTID', 'Shape_Length', 'Shape_Area', 'FID', 'Shape'}

        # Get field names for both feature classes
        source_fields = {f.name for f in arcpy.ListFields(source_fc) if f.name not in protected_fields}
        reference_fields = {f.name for f in arcpy.ListFields(reference_fc)}

        # Identify fields to remove (present in source but not in reference)
        fields_to_remove = source_fields - reference_fields

        # Remove extra fields from source feature class
        if fields_to_remove:
            arcpy.DeleteField_management(source_fc, list(fields_to_remove))
            print(f"Removed fields from {source_fc}: {fields_to_remove}")
        else:
            print(f"No fields to remove. {source_fc} schema already conforms to {reference_fc}.")

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