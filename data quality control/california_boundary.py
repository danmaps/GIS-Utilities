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
        desc = arcpy.Describe(lyr)
        oid_field = desc.OIDFieldName
        objectids = [row[0] for row in arcpy.da.SearchCursor(f"{lyr}", [f'{oid_field}'])]
        
        arcpy.AddError(f"OIDs {', '.join(map(str,objectids))} outside of CA.\n")
        
        # Access current project/map
        aprx = arcpy.mp.ArcGISProject("CURRENT")
        mv = aprx.activeView # mapview
        if type(mv) == "MapView":
            my_layer = mv.map.listLayers(f"{lyr}")[0]
        
            # Select by objectid, the problematic features in the input feature class
            for oid in objectids:
                arcpy.SelectLayerByAttribute_management(my_layer.name,
                                                    "ADD_TO_SELECTION", 
                                                    oid_field+"="+str(oid))

            # Zoom to selected problematic features
            mv.camera.setExtent(mv.getLayerExtent(my_layer))
        
        return
    # no problem features found
    arcpy.AddMessage(" This item has PASSED this QC check. Mark it as such and continue to the next step.")

if __name__ == "__main__":
    main()
