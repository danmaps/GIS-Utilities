import fill_selected
import arcpy
from IPython.display import display
import pandas as pd

arcpy.env.overwriteOutput = True

def feature_class_to_dataframe(fc, field):
    data = [row for row in arcpy.da.SearchCursor(fc, field)]
    return pd.DataFrame(data, columns=[field])

def test_squash_nulls():
    # Create a temporary feature class in the memory workspace
    temp_fc = r"memory\temp_fc" # try memory instead of legacy in_memory
    arcpy.management.CreateFeatureclass("memory", "temp_fc", "POINT")
    
    # Add a field to the feature class
    field_name = "TestField"
    arcpy.management.AddField(temp_fc, field_name, "TEXT")
    
    # Insert rows into the feature class
    with arcpy.da.InsertCursor(temp_fc, ["SHAPE@", field_name]) as cursor:
        cursor.insertRow([(0, 0), None])
        cursor.insertRow([(1, 1), "some data"])
        cursor.insertRow([(2, 2), None])
    
    df_before = feature_class_to_dataframe(temp_fc, field_name)
    
    # Call the function
    fill_selected.squash_nulls(temp_fc, field_name)
    
    df_after = feature_class_to_dataframe(temp_fc, field_name)
    
    # Check that the null values have been filled with "value"
    with arcpy.da.SearchCursor(temp_fc, [field_name]) as cursor:
        for row in cursor:
            assert row[0] == "some data"
    
    print("Pass")
    
    return df_before, df_after

