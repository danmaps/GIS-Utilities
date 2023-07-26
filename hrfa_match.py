import arcpy

# Function to check if HFTDClass field exists in the input layer
def field_exists(layer, field_name):
    field_list = [field.name for field in arcpy.ListFields(layer)]
    return field_name in field_list

def main():
    # Get the parameters from the geoprocessing tool
    lyr = arcpy.GetParameterAsText(0)  # Input Layer

    # Check if the input layer has the required field 'HFTDClass'
    if not field_exists(lyr, "HFTDClass"):
        arcpy.AddError("The field 'HFTDClass' does not exist in the input layer.")
        return

    # Run Spatial Join Geoprocessing Tool
    arcpy.analysis.SpatialJoin(
        target_features=lyr,
        join_features=r"https://services5.arcgis.com/z6hI6KRjKHvhNO0r/arcgis/rest/services/SCE_HighFireRiskArea/FeatureServer\0",
        out_feature_class=f"{lyr}_SpatialJoin",
    )

    arcpy.AddMessage(f"Created {lyr}_SpatialJoin")

    arcpy.MakeFeatureLayer_management(f"{lyr}_SpatialJoin",f"{lyr}_SpatialJoinLayer")

    arcpy.AddMessage(f"Select By Attributes")
    arcpy.management.SelectLayerByAttribute(
        in_layer_or_view=f"{lyr}_SpatialJoinLayer",
        selection_type="NEW_SELECTION",
        where_clause="(HFTDClass <> LABEL And LABEL IS NOT NULL) OR (HFTDClass <> 'Non-HFTD' AND LABEL IS NULL)",
    )

    # Get the count of selected features
    count = int(arcpy.GetCount_management(f"{lyr}_SpatialJoinLayer")[0])

    # Check if there are problematic situations, and indicate failure with AddError
    if count > 0:
        arcpy.AddError(f"Found {count} assets outside the specified HFTD Boundary.")
    
        # Get a list of OBJECTIDs for selected features
        objectids = [row[0] for row in arcpy.da.SearchCursor(f"{lyr}_SpatialJoinLayer", ['OBJECTID'])]
        
        # Get lists of HFTDClass and LABEL values
        hftd_values = [row[0] for row in arcpy.da.SearchCursor(f"{lyr}_SpatialJoinLayer", ['HFTDClass'])]
        label_values = [row[0] for row in arcpy.da.SearchCursor(f"{lyr}_SpatialJoinLayer", ['LABEL'])]

        # Create HTML table string
        table = "<table>"
        table += "<tr><th>OBJECTID</th><th>HFTDClass</th><th>LABEL</th></tr>"
        for i in range(len(objectids)):
            table += f"<tr><td>{objectids[i]}</td><td>{hftd_values[i]}</td><td>{label_values[i]}</td></tr>"
        table += "</table>"
        
        arcpy.AddMessage(table)

        mismatch_oids = {}

        for i in range(len(objectids)):
            hftd = hftd_values[i]
            label = label_values[i]
            
            if hftd != label:
                key = (hftd, label)
                if key not in mismatch_oids:
                    mismatch_oids[key] = []
                mismatch_oids[key].append(objectids[i])

        summary = ""
        
        for key,oids in mismatch_oids.items():
            hftd, label = key
            summary += f"OIDs {', '.join(map(str,oids))} have HFTDClass of {hftd} but LABEL is {label}\n"
        
        arcpy.AddError(summary)
        return
    arcpy.AddMessage("Pass!")

if __name__ == "__main__":
    main()
