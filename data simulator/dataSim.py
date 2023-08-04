import arcpy
import pandas as pd
import random
import string
import re
from datetime import datetime, timedelta

def anonymize_gis_data(input_data, count, output_csv):
    # try:
    #     # Get the number of rows in the input dataset
    #     num_rows = int(arcpy.GetCount_management(input_data).getOutput(0))
    # except:
    #     arcpy.AddError("Invalid input dataset. Please provide a valid file geodatabase, feature service, or table.")
    #     return

    # Read data into a pandas DataFrame
    fields = [f.name for f in arcpy.ListFields(input_data)]
    data = [row for row in arcpy.da.SearchCursor(input_data, fields)][:count]
    df = pd.DataFrame(data, columns=fields)

    # Extract maximum field lengths for text fields
    field_lengths = {field: field_info.length for field, field_info in zip(fields, arcpy.ListFields(input_data))}
    
    # Iterate through each field and anonymize the data
    for field in df.columns:

        field_info = arcpy.ListFields(input_data, field)[0]

        # Handle lat/long fields
        if field_info.type == 'Double' and ('Latitude' in field.lower() or 'Longitude' in field.lower()):
            df[field] = df.apply(lambda x: x[field] + random.uniform(-0.1, 0.1) if pd.notnull(x[field]) else None, axis=1)

        # Handle string fields
        elif field_info.type == 'String':
            unique_values = df[field].unique()
            max_length = field_lengths.get(field, 50)  # Default to a max length of 50 if not found

            # Check if the field matches the FLOC format (e.g., "OH-######E")
            if all(re.match(r'^[A-Z]{2}-\d+[A-Z]$', str(val)) for val in unique_values if pd.notnull(val)):
                df[field] = [anonymize_floc(val) for val in df[field]]
            else:
                word_list = [anonymize_string(val, max_length) if pd.notnull(val) else None for val in df[field]]
                df[field] = word_list

        # Handle numeric fields
        elif field_info.type in ['Integer', 'Double', 'Float']:
            df[field] = anonymize_numeric(df[field], field_info.type)

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

def anonymize_string(s, max_length):
    # Anonymize string by preserving case, length, and uniqueness
    if pd.notnull(s):
        random.seed(hash(s))  # Ensure the same value gets the same random string
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=min(len(s), max_length)))
    return None

def anonymize_floc(s):
    # Anonymize FLOC field while preserving characters before the dash and anonymizing the numeric part
    if pd.notnull(s):
        floc_prefix, floc_suffix = s.split('-')
        random.seed(hash(floc_suffix))  # Ensure the same value gets the same random string
        anonymized_suffix = ''.join(random.choices(string.digits, k=len(floc_suffix)))
        return f"{floc_prefix}-{anonymized_suffix}{floc_suffix[-1]}"  # Preserve the last character after the numeric part
    return None

def anonymize_numeric(values, field_type):
    # Anonymize numeric values while preserving data type and number of digits (for floats)
    if field_type in ['Double', 'Float']:
        # Find the maximum number of digits after the decimal point in the original field
        num_decimals = max(map(lambda x: len(str(x).split(".")[1]) if pd.notnull(x) else 0, values))
        # Round the values to the same number of decimals
        values = [round(val, num_decimals) if pd.notnull(val) else None for val in values]
    else:  # For Integer fields, round to the nearest integer
        values = [round(val) if pd.notnull(val) else None for val in values]
    return values

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
