import pytest
import pandas as pd
from dataSim import anonymize_gis_data

# Test CSV files
TEST_CSV_1 = "test_data_1.csv"
TEST_CSV_2 = "test_data_2.csv"
TEST_CSV_3 = "test_data_3.csv"

def test_numeric_fields():
    # Generate anonymized CSV
    anonymize_gis_data(TEST_CSV_1, 3, "anonymized_test_data_1.csv")

    # Read original and anonymized data
    df_original = pd.read_csv(TEST_CSV_1)
    df_anonymized = pd.read_csv("anonymized_test_data_1.csv")

    # Check if columns are preserved and values are anonymized
    assert set(df_original.columns) == set(df_anonymized.columns)
    for field in df_original.columns:
        if field != 'OID':  # Exclude ID field
            assert df_original[field].nunique() == df_anonymized[field].nunique()
            assert not df_original[field].equals(df_anonymized[field])

def test_string_fields():
    # Generate anonymized CSV
    anonymize_gis_data(TEST_CSV_2, 3, "anonymized_test_data_2.csv")

    # Read original and anonymized data
    df_original = pd.read_csv(TEST_CSV_2)
    df_anonymized = pd.read_csv("anonymized_test_data_2.csv")

    # Check if columns are preserved and values are anonymized
    assert set(df_original.columns) == set(df_anonymized.columns)
    for field in df_original.columns:
        if field != 'OID':  # Exclude ID field
            assert df_original[field].nunique() == df_anonymized[field].nunique()
            assert not df_original[field].equals(df_anonymized[field])

def test_date_fields():
    # Generate anonymized CSV
    anonymize_gis_data(TEST_CSV_3, 3, "anonymized_test_data_3.csv")

    # Read original and anonymized data
    df_original = pd.read_csv(TEST_CSV_3)
    df_anonymized = pd.read_csv("anonymized_test_data_3.csv")

    # Check if columns are preserved and values are anonymized
    assert set(df_original.columns) == set(df_anonymized.columns)
    for field in df_original.columns:
        if field != 'OID':  # Exclude ID field
            assert df_original[field].nunique() == df_anonymized[field].nunique()
            assert not df_original[field].equals(df_anonymized[field])

# Clean up after tests
def teardown_module():
    import os
    files = ["anonymized_test_data_1.csv", "anonymized_test_data_2.csv", "anonymized_test_data_3.csv"]
    for file in files:
        if os.path.exists(file):
            os.remove(file)

if __name__ == "__main__":
    pytest.main()
