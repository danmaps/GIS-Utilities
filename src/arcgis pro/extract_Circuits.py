import arcpy
def create_feature_layer(feature):
    """Creates a feature layer from the given feature."""
    arcpy.MakeFeatureLayer_management(feature, "HFRA_Conductor")
def create_table_view(table):
    """Creates a table view from the given table."""
    arcpy.management.MakeTableView(in_table=table, out_view="request")
def join_tables(field):
    """Joins tables based on the given field."""
    arcpy.management.AddJoin(
        in_layer_or_view="HFRA_Conductor",
        in_field="SCE_FLOC",
        join_table="request",
        join_field=field,
        join_type="KEEP_COMMON"
    )
def dissolve_features(feature, output):
    """Dissolves features based on certain fields."""
    fc_name = arcpy.Describe(feature).name
    dissolve_fields = [f"{fc_name}.{field_name}" for field_name in ["CIRCUIT_NAME"]]
    arcpy.analysis.PairwiseDissolve(in_features="HFRA_Conductor", out_feature_class=output, 
                                    dissolve_field=";".join(dissolve_fields))
def script_tool(feature, request_table, FLOC_field, output):
    """Main function"""
    create_feature_layer(feature)
    create_table_view(request_table)
    join_tables(FLOC_field)
    dissolve_features(feature, output)
    arcpy.AddMessage(f"requested: {arcpy.GetCount_management('request')}")
    arcpy.AddMessage(f"result: {arcpy.GetCount_management(output)}")
    arcpy.SetParameter(3, output)
if __name__ == "__main__":
    param0 = arcpy.GetParameterAsText(0)
    param1 = arcpy.GetParameterAsText(1)
    param2 = arcpy.GetParameterAsText(2)
    param3 = arcpy.GetParameterAsText(3)
    script_tool(param0, param1, param2, param3)
