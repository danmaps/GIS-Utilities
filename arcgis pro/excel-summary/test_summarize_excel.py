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
