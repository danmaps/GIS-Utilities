import pandas as pd
import arcpy

# Load Excel file
excel_file = r'incoming_data.xlsx'
df = pd.read_excel(excel_file)

# Save as CSV
csv_file = 'incoming_data.csv' 
df.to_csv(csv_file, index=False)

# Convert CSV to table in default ArcGIS Pro geodatabase
out_table = 'incoming_data'

out_gdb = arcpy.mp.ArcGISProject("CURRENT").defaultGeodatabase

arcpy.conversion.TableToTable(csv_file, out_gdb, out_table)

print('Excel file converted to table in default geodatabase')