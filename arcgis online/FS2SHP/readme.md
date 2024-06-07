
# Work Orders Shapefile Export and Split Tool

This tool is designed to export work orders from an ArcGIS Online feature service to a shapefile and then split that shapefile into separate shapefiles based on the 'WorkOrder' attribute. The output is organized into a specified folder structure and zipped for convenient storage and transfer.

## Folder Structure

The tool will create the following folder structure:

```
WestCovina_SLs
    WorkOrders_DateTime.zip
        WorkOrders_DateTime.zip
            WorkOrders_DateTime.shp
        separate
            WorkOrder1_DateTime.zip
                WorkOrder1_DateTime.shp
            WorkOrder2_DateTime.zip
                WorkOrder2_DateTime.shp
```

## Requirements

- ArcGIS Pro 3.x
    - `arcpy`
    - Python 3.x
    - The `arcgis` Python package
- An ArcGIS Online account with access to the feature service

## Setup

Update the following paths and parameters in the script as needed:
    - `service_item_id`: The ID of the feature service item in ArcGIS Online.
    - `onedrive_folder`: The local path where the exported shapefiles will be stored.

## Usage

1. Save the script to a Python file, e.g., `export_workorders.py`.
2. Run the script using ArcGIS Pro's Python environment or another suitable Python environment.

## Script Overview

### Authentication

The script authenticates with ArcGIS Online using the currently logged-in user's credentials.

```python
gis = GIS("pro")
```

### Export Service to Shapefile

The script checks for new features in the feature service based on the feature count. If new features are detected, it exports the service to a shapefile.

```python
today_date = datetime.datetime.now().strftime("%m%d%Y_%H%M%S")
out_name = "WorkOrders_" + today_date

if count > prev_count:
    arcpy.management.CopyFeatures(service_item.url + r"/0", os.path.join(onedrive_folder, out_name, out_name) + ".shp")
```

### Explode Shapefile

The `explode_shapefile` function splits the exported shapefile into separate shapefiles based on the 'WorkOrder' attribute.

```python
def explode_shapefile(input_shp, output_folder, today_date):
    # Implementation
```

### Zipping Files

The script zips the exported and split shapefiles for storage and transfer.

```python
shutil.make_archive(zip_name, 'zip', out_dir)
```

### Count Management

The script maintains a count of features to determine if there are new features to export.

```python
count_file = os.path.join(onedrive_folder + "_count", "count.txt")
```


For any issues or contributions, please reach out to Daniel McVey.