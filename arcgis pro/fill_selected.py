def check_data(layer, fields):
    # Iterate over the specified fields
    for field in fields:
        print(f"looking at field: {field}")
        # Count unique non-null values
        unique_values = {row[0] for row in cursor if row[0] is not None}
        print(f"unique values: {unique_values}")
        # Check if there is only one distinct non-null value
        if len(unique_values) > 1:
            print(field,f"more than one nonnull value {unique_values}")
            return # don't do the fill
        # Fill in values
        query = f"{field} IS NULL OR {field} = ''"
        with arcpy.da.UpdateCursor(layer, [field], query) as cursor:
            # Update null values with the non-null value in all null rows
            for row in cursor:
                row[0] = list(unique_values)[0]
                cursor.updateRow(row)
    return True

layer = "Street Lights"
fields = ["SUB_FLOC", "SUB"]
check_data(layer, fields)