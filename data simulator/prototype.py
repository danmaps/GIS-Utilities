import arcpy
import pandas as pd
import random
import string

def anonymize_gis_data(input_data, count, output_csv):
    try:
        # Get the number of rows in the input dataset
        num_rows = int(arcpy.GetCount_management(input_data).getOutput(0))
    except:
        arcpy.AddError("Invalid input dataset. Please provide a valid file geodatabase, feature service, or table.")
        return
    print(num_rows)

    # Read data into a pandas DataFrame
    fields = [f.name for f in arcpy.ListFields(input_data)]
    data = [row for row in arcpy.da.SearchCursor(input_data, fields)][:count]
    df = pd.DataFrame(data, columns=fields)

    # Iterate through each field and anonymize the data
    for field in df.columns:
        field_info = arcpy.ListFields(input_data, field)[0]

        # Handle lat/long fields
        if field_info.type == 'Double' and ('Latitude' in field.lower() or 'Longitude' in field.lower()):
            df[field] = df.apply(lambda x: x[field] + random.uniform(-0.1, 0.1) if pd.notnull(x[field]) else None, axis=1)

        # Handle string fields
        elif field_info.type == 'String':
            word_list = [''.join(random.choices(string.ascii_lowercase, k=random.randint(3, 10))) for _ in range(df.shape[0])]
            df[field] = word_list

        # Handle numeric fields
        elif field_info.type in ['Integer', 'Double', 'Float']:
            df[field] = df.apply(lambda x: x[field] + random.uniform(-1, 1) if pd.notnull(x[field]) else None, axis=1)

    # Export anonymized data to a CSV file
    df.to_csv(output_csv, index=False)

if __name__ == '__main__':
    # Get input and output datasets from script tool parameters
    input_dataset = arcpy.GetParameterAsText(0)
    count = arcpy.GetParameterAsText(1)
    output_csv = arcpy.GetParameterAsText(2)

    # Call the function to anonymize the GIS data
    anonymize_gis_data(input_dataset, count, output_csv)
