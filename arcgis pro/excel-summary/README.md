
# Excel Summary Tool

## Overview
The Excel Summary Tool is a Python script designed to automate the process of generating a summary sheet in an Excel workbook. It calculates the count of non-null values, total rows, and percentages for specified columns in a given sheet.

## Requirements
- Python 3
- openpyxl (Python library)

## Installation
First, ensure that Python 3 is installed on your system. Then, install the `openpyxl` library using pip:

```bash
pip install openpyxl
```

## Usage
Run the script from the command line by passing the Excel file path, the sheet name (optional), and the columns to summarize. The columns can be identified by letter, number, or heading.

```bash
python summary_tool.py <file_path> <sheet_name> <column1> <column2> ...
```

Example:
```bash
python summary_tool.py myfile.xlsx Sheet1 E F G H
```

## How It Works
- The script reads the specified Excel workbook and sheet (or the first sheet if no sheet name is provided).
- It then identifies the columns to be summarized based on the provided arguments.
- A "Summary" sheet is created in the workbook with columns for "Column Heading", "Count", "Total", and "Percentage" for each important column.
- The script saves the updated workbook with the newly added summary sheet.

## Notes
- Ensure that the first row of each column in the Excel file contains the heading.
- The script modifies the Excel file directly; it's advisable to backup your files before running the script.
- The tool is intended for Excel files with a standard layout and may require adjustments for different data structures or formats.

## Author
- Created by Danny McVey
