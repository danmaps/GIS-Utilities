import pytest
import pandas as pd
from dataSim import anonymize_gis_data

# Test CSV files
TEST_CSV_1 = "test_data_1.csv"
TEST_CSV_2 = "test_data_2.csv"
TEST_CSV_3 = "test_data_3.csv"
TEST_CSV_NUMERIC = "test_data_numeric.csv"
TEST_CSV_LATLONG = "test_data_latlong.csv"

# Function to check characteristics of fields in DataFrames
def check_field_characteristics(df_original, df_anonymized):
    for field in df_original.columns:
        if field != 'OID':  # Exclude ID field
            assert df_original[field].nunique() == df_anonymized[field].nunique()
            assert not df_original[field].equals(df_anonymized[field])

            # Check if data type and number of digits are preserved for numeric fields
            if field == 'IntegerField':
                assert df_anonymized[field].dtype == 'int64'
            elif field == 'FloatField':
                assert df_anonymized[field].dtype == 'float64'
                assert df_original[field].apply(lambda x: len(str(x).split(".")[1]) if pd.notnull(x) else 0).equals(
                    df_anonymized[field].apply(lambda x: len(str(x).split(".")[1]) if pd.notnull(x) else 0))

def test_numeric_fields():
    # Generate anonymized CSV
    anonymize_gis_data(TEST_CSV_NUMERIC, 3, "anonymized_test_data_numeric.csv")

    # Read original and anonymized data
    df_original = pd.read_csv(TEST_CSV_NUMERIC)
    df_anonymized = pd.read_csv("anonymized_test_data_numeric.csv")

    # Check if anonymized DataFrame has the same number of columns as the original
    assert len(df_original.columns) == len(df_anonymized.columns)

    # Check characteristics of fields in the original and anonymized DataFrames
    check_field_characteristics(df_original, df_anonymized)

def test_string_fields():
    # Generate anonymized CSV
    anonymize_gis_data(TEST_CSV_2, 3, "anonymized_test_data_2.csv")

    # Read original and anonymized data
    df_original = pd.read_csv(TEST_CSV_2)
    df_anonymized = pd.read_csv("anonymized_test_data_2.csv")

    # Check if columns are preserved and values are anonymized
    assert set(df_original.columns) == set(df_anonymized.columns)
    check_field_characteristics(df_original, df_anonymized)

def test_date_fields():
    # Generate anonymized CSV
    anonymize_gis_data(TEST_CSV_3, 3, "anonymized_test_data_3.csv")

    # Read original and anonymized data
    df_original = pd.read_csv(TEST_CSV_3)
    df_anonymized = pd.read_csv("anonymized_test_data_3.csv")

    # Check if columns are preserved and values are anonymized
    assert set(df_original.columns) == set(df_anonymized.columns)
    check_field_characteristics(df_original, df_anonymized)

def test_latlong_fields():
    # Generate anonymized CSV
    anonymize_gis_data(TEST_CSV_LATLONG, 3, "anonymized_test_data_latlong.csv")

    # Read original and anonymized data
    df_original = pd.read_csv(TEST_CSV_LATLONG)
    df_anonymized = pd.read_csv("anonymized_test_data_latlong.csv")

    # Check if columns are preserved and values are anonymized
    assert set(df_original.columns) == set(df_anonymized.columns)
    check_field_characteristics(df_original, df_anonymized)

# Clean up after tests
def teardown_module():
    import os
    files = ["anonymized_test_data_1.csv", "anonymized_test_data_2.csv", "anonymized_test_data_3.csv",
             "anonymized_test_data_latlong.csv", "anonymized_test_data_numeric.csv"]
    for file in files:
        if os.path.exists(file):
            os.remove(file)

if __name__ == "__main__":
    pytest.main()
