def check_data(layer, fields):
    for field in fields:
        print(f"looking at field: {field}")
        
        # Get a set of unique non-null values for the current field
        unique_values = set()
        with arcpy.da.SearchCursor(layer, field) as cursor:
            for row in cursor:
                if row[0] is not None:
                    unique_values.add(row[0])
        
        print(f"unique values: {unique_values}")

        if len(unique_values) > 1:
            print(field, f"more than one nonnull value {unique_values}")
        else:
            # Fill in values
            query = f"{field} IS NULL OR {field} = ''"
            with arcpy.da.UpdateCursor(layer, field, query) as update_cursor:
                for row in update_cursor:
                    row[0] = list(unique_values)[0]
                    update_cursor.updateRow(row)
    
    return True


    return True


layer = "Street Lights"
fields = ["SUB_FLOC", "SUB"]
check_data(layer, fields)