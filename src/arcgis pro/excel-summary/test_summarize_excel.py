from summarize_excel import main

def test_summary_tool():
    file_path = r"C:\Users\mcveydb\dev\GIS-Utilities\arcgis pro\excel-summary\Excel_Test_File.xlsx"
    sheet_name = 'TestData'
    columns = ['A', 'B', 'C', 'D', 'E']  # Update as needed based on your test file's columns

    # Run the tool
    main(file_path, sheet_name, *columns)

    # After running, manually open the file and verify the Summary sheet
    print("Test completed. Please open the file and manually verify the Summary sheet.")

# Call the test function
test_summary_tool()

def test_no_columns():
    file_path = r"C:\Users\mcveydb\dev\GIS-Utilities\arcgis pro\excel-summary\Excel_Test_File.xlsx"
    sheet_name = 'TestData'
    columns = []  # No columns specified

    # Run the tool
    main(file_path, sheet_name, *columns)

    # After running, manually open the file and verify the Summary sheet
    print("Test completed. Please open the file and manually verify the Summary sheet.")

# Call the test function
test_no_columns()

def test_invalid_columns():
    file_path = r"C:\Users\mcveydb\dev\GIS-Utilities\arcgis pro\excel-summary\Excel_Test_File.xlsx"
    sheet_name = 'TestData'
    columns = ['A', 'B', 'C', 'D', 'E', 'F']  # Invalid columns

    # Run the tool
    main(file_path, sheet_name, *columns)

    # After running, manually open the file and verify the Summary sheet
    print("Test completed. Please open the file and manually verify the Summary sheet.")

# Call the test function
test_invalid_columns()

def test_invalid_sheet():
    file_path = r"C:\Users\mcveydb\dev\GIS-Utilities\arcgis pro\excel-summary\Excel_Test_File.xlsx"
    sheet_name = 'InvalidSheet'
    columns = ['A', 'B', 'C', 'D', 'E']  # Update as needed based on your test file's columns

    # Run the tool
    main(file_path, sheet_name, *columns)

    # After running, manually open the file and verify the Summary sheet
    print("Test completed. Please open the file and manually verify the Summary sheet.")

# Call the test function
test_invalid_sheet()

def test_invalid_file():
    file_path = r"C:\Users\mcveydb\dev\GIS-Utilities\arcgis pro\excel-summary\Invalid_File.xlsx"
    sheet_name = 'TestData'
    columns = ['A', 'B', 'C', 'D', 'E']  # Update as needed based on your test file's columns

    # Run the tool
    main(file_path, sheet_name, *columns)

    # After running, manually open the file and verify the Summary sheet
    print("Test completed. Please open the file and manually verify the Summary sheet.")

# Call the test function
test_invalid_file()

