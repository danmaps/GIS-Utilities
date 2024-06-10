import arcpy

def main():
    # Get the parameters from the geoprocessing tool
    lyr = arcpy.GetParameterAsText(0)  # Input Layer

    # run select by location with where clause inverted
    arcpy.management.SelectLayerByLocation(
        in_layer=lyr,
        overlap_type="INTERSECT",
        select_features=r"P:\PROJECTS\Special_Projects\WSD_GIS_Schema\Data_ReferenceLayers\MB_State_Buffer\MB_State_1Mile_Buffer.gdb\MB_State_1MileBuffer",
        invert_spatial_relationship="INVERT"
    )

    # Get the count of selected features
    count = int(arcpy.GetCount_management(f"{lyr}")[0])

    # Check if there are problematic situations, and indicate failure with AddError
    if count > 0:
        arcpy.AddError(f"Found {count} assets outside the CA boundary.")
    
        # Get a list of OBJECTIDs for selected features
        objectids = [row[0] for row in arcpy.da.SearchCursor(f"{lyr}", ['OBJECTID'])]
        
        arcpy.AddError(f"OIDs {', '.join(map(str,objectids))} outside of CA.\n")
        
        return
    arcpy.AddMessage("Pass!")

if __name__ == "__main__":
    main()
