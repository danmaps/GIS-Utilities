Set the script tool parameters as follows:
- Parameter 1: Input Dataset (Data Type: Feature Layer, Direction: Input)
- Parameter 2: Count (Data Type: Long, Direction: Input)
- Parameter 3: Output CSV (Data Type: File, Direction: Output)

Now you have a script tool that can be used to anonymize GIS data and export the anonymized data to a CSV file

To speed up testing in ArcGIS Pro, i found this approach helpful:
```python
arcpy.ImportToolbox(r"dataSim.atbx")
arcpy.Defaultatbx.Script("some_layer",50,"test.csv")
arcpy.MakeTableView_management(r"test.csv","test")
```