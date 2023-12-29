import arcpy
import re
from arcgis.gis import GIS
from arcgis.features import FeatureLayer

# Log into ArcGIS Online
gis = GIS("Pro")

def script_tool(param0, param1):

    def check_missing_fields(layer, field_mapping):
        """
        Checks for missing fields in the specified layer based on the provided field mapping.
        If missing fields are found, an ArcPy warning is displayed.

        Parameters:
        layer (str): The name or path of the layer to check.
        field_mapping (str): The field mapping string.

        Returns:
        None
        """
        # List all fields in the layer
        fields = [field.name for field in arcpy.ListFields(layer)]

        # Parse field mapping to get field names
        mapped_fields = [f.split(' ')[0] for f in field_mapping.split(';')]

        # Check if each field in the field mapping exists in the layer
        missing_fields = [f for f in mapped_fields if f not in fields]

        # Add warning if missing fields are found
        if missing_fields:
            warning_message = "Missing fields in the layer '{}': {}".format(layer, ', '.join(missing_fields))
            arcpy.AddWarning(warning_message)

    
    arcpy.AddMessage("MakeFeatureLayer...")
    arcpy.MakeFeatureLayer_management(gis.content.get("80c86dd5aa184264896437b0e1d8e54b").layers[0].url, "bulktrans")
    arcpy.MakeFeatureLayer_management(gis.content.get("b653952755af48fd85a31680e07a6641").layers[0].url, "subtrans")
    arcpy.MakeFeatureLayer_management(gis.content.get("38a2e08043e04268a1a386e63c3c69bd").layers[0].url, "sce_HighFireRiskArea")
    arcpy.MakeFeatureLayer_management(gis.content.get("71e126217f44483091982e52804e4171").layers[1].url, "Subtrans_Segments")

    arcpy.AddMessage("ExportFeatures...")
    bulktrans_field_mapping='CIRCUIT_ID "CIRCUIT_ID" true true false 50 Text 0 0,First,#,bulktrans,CIRCUIT_ID,0,50;CIRCUIT_NAME "CIRCUIT_NAME" true true false 150 Text 0 0,First,#,bulktrans,CIRCUIT_NAME,0,150;KV "KV" true true false 0 Double 0 0,First,#,bulktrans,KV,-1,-1'
    check_missing_fields("bulktrans",bulktrans_field_mapping)
    arcpy.conversion.ExportFeatures(
        in_features="bulktrans",
        out_features="bulktrans_ExportFeatures",
        where_clause="",
        use_field_alias_as_name="NOT_USE_ALIAS",
        field_mapping=bulktrans_field_mapping,
        sort_field=None,
    )

    subtrans_field_mapping = 'CIRCUIT_NO "CIRCUIT_NO" true true false 7 Text 0 0,First,#,subtrans,CIRCUIT_NO,0,7;NAME "NAME" true true false 70 Text 0 0,First,#,subtrans,NAME,0,70;KV "KV" true true false 0 Double 0 0,First,#,subtrans,KV,-1,-1'
    check_missing_fields("subtrans",subtrans_field_mapping)
    arcpy.conversion.ExportFeatures(
        in_features="subtrans",
        out_features="subtrans_ExportFeatures",
        where_clause="",
        use_field_alias_as_name="NOT_USE_ALIAS",
        field_mapping=subtrans_field_mapping,
        sort_field=None,
    )

    arcpy.AddMessage("Clip and intersect...")

    # clip to HFRA and intersect with Segments
    def clip_intersect(lyr):
        arcpy.analysis.Clip(
            in_features=lyr,
            clip_features="sce_HighFireRiskArea",
            out_feature_class=rf"{lyr}_Clip",
        )
        arcpy.analysis.Intersect(
            in_features=rf"{lyr}_Clip #;Subtrans_Segments #",
            out_feature_class=rf"{lyr}_Intersect",
        )

    clip_intersect("bulktrans_ExportFeatures")
    clip_intersect("subtrans_ExportFeatures")

    arcpy.AddMessage("Spatial Joins...")

    arcpy.MakeFeatureLayer_management(gis.content.get("4414e648847445ffa6019523850f8d7f").layers[0].url, "districts")
    arcpy.MakeFeatureLayer_management(gis.content.get("9998b507eef44f9db5ff962268d08ab6").layers[0].url, "counties")

    arcpy.analysis.SpatialJoin(
        target_features="bulktrans_ExportFeatures_Intersect",
        join_features="counties",
        out_feature_class="bulktrans_join1",
        join_operation="JOIN_ONE_TO_ONE",
        join_type="KEEP_ALL",
        field_mapping='CIRCUIT_NO "CIRCUIT_NO" true true false 50 Text 0 0,First,#,bulktrans_ExportFeatures_Intersect,CIRCUIT_NO,0,50;CIRCUIT_NA "CIRCUIT_NA" true true false 150 Text 0 0,First,#,bulktrans_ExportFeatures_Intersect,CIRCUIT_NA,0,150;VOLTAGE "VOLTAGE" true true false 8 Double 0 0,First,#,bulktrans_ExportFeatures_Intersect,VOLTAGE,-1,-1;SEGMENTS "SEGMENTS" true true false 5 Text 0 0,First,#,bulktrans_ExportFeatures_Intersect,SEGMENTS,0,5;COUNTY "COUNTY" true true false 150 Text 0 0,Join,", ",counties,NAME,0,150',
        match_option="INTERSECT",
        search_radius=None,
        distance_field_name="",
    )

    arcpy.analysis.SpatialJoin(
        target_features="bulktrans_join1",
        join_features="districts",
        out_feature_class="bulktrans_join2",
        join_operation="JOIN_ONE_TO_ONE",
        join_type="KEEP_ALL",
        field_mapping='CIRCUIT_NO "CIRCUIT_NO" true true false 50 Text 0 0,First,#,bulktrans_join1,CIRCUIT_NO,0,50;CIRCUIT_NAME "CIRCUIT_NAME" true true false 150 Text 0 0,First,#,bulktrans_join1,CIRCUIT_NAME,0,150;VOLTAGE "VOLTAGE" true true false 8 Double 0 0,First,#,bulktrans_join1,VOLTAGE,-1,-1;SEGMENTS "SEGMENTS" true true false 5 Text 0 0,First,#,bulktrans_join1,SEGMENTS,0,5;COUNTY "COUNTY" true true false 150 Text 0 0,First,#,bulktrans_join1,COUNTY,0,150;DISTRICT "DISTRICT" true true false 2 Text 0 0,First,#,districts,NUMBER_,0,2',
        match_option="INTERSECT",
        search_radius=None,
        distance_field_name="",
    )

    arcpy.analysis.SpatialJoin(
        target_features="subtrans_ExportFeatures_Intersect",
        join_features="counties",
        out_feature_class="subtrans_join1",
        join_operation="JOIN_ONE_TO_ONE",
        join_type="KEEP_ALL",
        field_mapping='CIRCUIT_NO "CIRCUIT_NO" true true false 50 Text 0 0,First,#,subtrans_ExportFeatures_Intersect,CIRCUIT_NO,0,50;CIRCUIT_NA "CIRCUIT_NA" true true false 150 Text 0 0,First,#,subtrans_ExportFeatures_Intersect,CIRCUIT_NA,0,150;VOLTAGE "VOLTAGE" true true false 8 Double 0 0,First,#,subtrans_ExportFeatures_Intersect,VOLTAGE,-1,-1;SEGMENTS "SEGMENTS" true true false 5 Text 0 0,First,#,subtrans_ExportFeatures_Intersect,SEGMENTS,0,5;COUNTY "COUNTY" true true false 150 Text 0 0,Join,", ",counties,NAME,0,150',
        match_option="INTERSECT",
        search_radius=None,
        distance_field_name="",
    )

    arcpy.analysis.SpatialJoin(
        target_features="subtrans_join1",
        join_features="districts",
        out_feature_class="subtrans_join2",
        join_operation="JOIN_ONE_TO_ONE",
        join_type="KEEP_ALL",
        field_mapping='CIRCUIT_NO "CIRCUIT_NO" true true false 50 Text 0 0,First,#,subtrans_join1,CIRCUIT_NO,0,50;CIRCUIT_NA "CIRCUIT_NA" true true false 150 Text 0 0,First,#,subtrans_join1,CIRCUIT_NA,0,150;VOLTAGE "VOLTAGE" true true false 8 Double 0 0,First,#,subtrans_join1,VOLTAGE,-1,-1;SEGMENTS "SEGMENTS" true true false 5 Text 0 0,First,#,subtrans_join1,SEGMENTS,0,5;COUNTY "COUNTY" true true false 150 Text 0 0,First,#,subtrans_join1,COUNTY,0,150;DISTRICT "DISTRICT" true true false 2 Text 0 0,First,#,districts,NUMBER_,0,2',
        match_option="INTERSECT",
        search_radius=None,
        distance_field_name="",
    )

    arcpy.AddMessage("Adding new fields...")

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
    for lyr in [bulk_layer, sub_layer]:
        arcpy.management.AddFields(
            in_table=lyr,
            field_description="CIRCUIT_SE TEXT # 255 # #;WIRE_CLASS TEXT # 50 # #;SUBSTATION TEXT # 255 # #;GUST_THRES LONG # # # #;WIND_THRES LONG # # # #",
        )
    # Calculate BulkTrans fields
    validate_and_calculate_field(bulk_layer, "CIRCUIT_SE", "!CIRCUIT_NA!.upper()+'_'+!SEGMENTS!")
    validate_and_calculate_field(bulk_layer, "WIRE_CLASS", '"Transmission"')
    validate_and_calculate_field(bulk_layer, "SUBSTATION", "!CIRCUIT_NA!.split('-')[0].upper()")

    # Calculate SubTrans fields
    validate_and_calculate_field(sub_layer, "CIRCUIT_NO", "'ET-'+!CIRCUIT_NO!.split('-')[0]")  # 00158-BT -> ET-00158
    validate_and_calculate_field(sub_layer, "CIRCUIT_SE", "!CIRCUIT_NA!.upper()+'_'+!SEGMENTS!")
    validate_and_calculate_field(sub_layer, "WIRE_CLASS", '"Transmission"')
    validate_and_calculate_field(sub_layer, "SUBSTATION", "!CIRCUIT_NA!.split('-')[0].upper()")

    # Remove extra fields
    for lyr in [bulk_layer, sub_layer]:
        arcpy.management.DeleteField(
            in_table=lyr, drop_field="Join_Count;TARGET_FID;", method="DELETE_FIELDS"
        )

    arcpy.AddMessage("Exporting...")

    arcpy.conversion.ExportFeatures(bulk_layer, param0)
    arcpy.conversion.ExportFeatures(sub_layer, param1)

    return


if __name__ == "__main__":
    param0 = arcpy.GetParameterAsText(0)
    param1 = arcpy.GetParameterAsText(1)

    script_tool(param0, param1)
