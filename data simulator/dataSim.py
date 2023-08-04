import arcpy
import pandas as pd
import random
import string
from datetime import datetime, timedelta

def anonymize_gis_data(input_data, count, output_csv):
    try:
        # Get the number of rows in the input dataset
        num_rows = int(arcpy.GetCount_management(input_data).getOutput(0))
    except:
        arcpy.AddError("Invalid input dataset. Please provide a valid file geodatabase, feature service, or table.")
        return

    # Read data into a pandas DataFrame
    fields = [f.name for f in arcpy.ListFields(input_data)]
    data = [row for row in arcpy.da.SearchCursor(input_data, fields)][:count]
    df = pd.DataFrame(data, columns=fields)

    # Iterate through each field and anonymize the data
    for field in df.columns:
        if field.upper() == "SHAPE":
            continue  # Skip SHAPE fields

        field_info = arcpy.ListFields(input_data, field)[0]

        # Handle lat/long fields
        if field_info.type == 'Double' and ('Latitude' in field.lower() or 'Longitude' in field.lower()):
            df[field] = df.apply(lambda x: x[field] + random.uniform(-0.1, 0.1) if pd.notnull(x[field]) else None, axis=1)

        # Handle string fields
        elif field_info.type == 'String':
            unique_values = df[field].unique()
            word_list = [anonymize_string(val) if pd.notnull(val) else None for val in df[field]]
            df[field] = word_list

        # Handle numeric fields
        elif field_info.type in ['Integer', 'Double', 'Float']:
            min_val, max_val = df[field].min(), df[field].max()
            df[field] = [random.uniform(min_val, max_val) if pd.notnull(val) else None for val in df[field]]

        # Handle date fields
        elif field_info.type == 'Date':
            date_format = "%m/%d/%Y %I:%M:%S %p"
            df[field] = [anonymize_date(val, date_format) if pd.notnull(val) else None for val in df[field]]

    # Drop the "SHAPE" column from the DataFrame
    if "SHAPE" in df.columns:
        df.drop(columns=["SHAPE"], inplace=True)
    
    # Create a dictionary to map original field names to new field names
    field_mapping = {field: f"field{i}" for i, field in enumerate(df.columns, 1)}

    # Rename the columns of the DataFrame using the dictionary
    df.rename(columns=field_mapping, inplace=True)

    # Export anonymized data to a CSV file
    df.to_csv(output_csv, index=False)

def anonymize_string(s):
    # Anonymize string by preserving case, length, and uniqueness
    if pd.notnull(s):
        random.seed(hash(s))  # Ensure the same value gets the same random string
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=len(s)))
    return None

def anonymize_date(d, date_format):
    # Anonymize date by adding random time intervals within a year
    if pd.notnull(d):
        random.seed(hash(d))  # Ensure the same value gets the same random date
        d_str = d.strftime(date_format)  # Convert Timestamp object to a string
        date_obj = datetime.strptime(d_str, date_format)
        random_interval = timedelta(days=random.randint(0, 365), seconds=random.randint(0, 86400))  # 1 year maximum interval
        return (date_obj + random_interval).strftime(date_format)
    return None

if __name__ == '__main__':
    # Get input and output datasets from script tool parameters
    input_dataset = arcpy.GetParameterAsText(0)
    count = int(arcpy.GetParameterAsText(1))
    output_csv = arcpy.GetParameterAsText(2)

    # Call the function to anonymize the GIS data
    anonymize_gis_data(input_dataset, count, output_csv)
