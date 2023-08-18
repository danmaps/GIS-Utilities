import arcpy
from arcgis.gis import GIS
import datetime
import zipfile
import os
import shutil

def explode_shapefile(input_shp, output_folder):
    """Explodes a shapefile with polygons into separate shapefiles based on 'WorkOrder' attribute"""
    
    # Get the shapefile name without extension
    shp_name = os.path.splitext(os.path.basename(input_shp))[0]
    
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    # Loop through features
    with arcpy.da.SearchCursor(input_shp, ["WorkOrder","SHAPE@","FID"]) as cursor:
        for row in cursor:
            work_order = row[0]
            polygon = row[1]
            
            # Check if work order is populated
            if work_order:
                out_shp = os.path.join(output_folder, f"{shp_name}_{work_order}.shp")
                
                # Export single feature to new shapefile
                if not os.path.exists(out_shp):
                    arcpy.conversion.ExportFeatures(input_shp, out_shp, f'"FID" = {row[2]}')

    print("Done exploding shapefile")


# Authentication 
gis = GIS("pro")

# Get service item ID
service_item_id = "f82022eb36514eb2a605dd6ea569fdb7" 
service_item = gis.content.get(service_item_id)
feature_layer = service_item.layers[0]

# Query the service for feature count
features = feature_layer.query()
count = len(features)

onedrive_folder = r"C:\Users\mcveydb\OneDrive - Southern California Edison\Documents\WestCovina_SLs"

# Export service to shapefile
# today_date = datetime.datetime.now().strftime("%m%d%Y")
today_date = datetime.datetime.now().strftime("%m%d%Y_%H%M%S")
out_name = "WorkOrders_" + today_date

# Check count file
count_file = os.path.join(onedrive_folder, "count.txt")
if os.path.exists(count_file):
    with open(count_file) as f:
        prev_count = int(f.read())
        
    # Check if there has been activity in the service, based on feature count
    if count > prev_count:
        print("New features detected. Exporting...")
        if not os.path.exists(os.path.join(onedrive_folder,out_name)):
            os.mkdir(os.path.join(onedrive_folder,out_name))
            
        arcpy.management.CopyFeatures(service_item.url+r"/0", os.path.join(onedrive_folder,out_name,out_name) + ".shp")

        # Zip shapefile folder
        zip_name = os.path.join(onedrive_folder,f"WorkOrders_{today_date}.zip")
        all_files = [f for f in os.listdir(os.path.join(onedrive_folder,out_name)) if os.path.isfile(os.path.join(onedrive_folder,out_name, f))]
        zip_file = zipfile.ZipFile(zip_name, "w")
        for file in all_files:
            zip_file.write(os.path.join(onedrive_folder,out_name, file), arcname=file)
        zip_file.close()

        # Set folder name
        folder_name = "Shapefile exports"

        # Publish shapefile to folder
        new_item = gis.content.add({"type":"Shapefile","title": f"WorkOrders_{today_date}"}, 
                                   os.path.join(onedrive_folder,f"WorkOrders_{today_date}.zip"),folder = folder_name)

        # Set sharing level                         
        new_item.share(org=True)

        print(new_item.homepage)
        
        # Overwrite count file
        with open(os.path.join(onedrive_folder,"count.txt"),"w") as f:
            f.write(str(count))                   

        # Explode shapefile into separate work order shapefiles
        input_shp = os.path.join(onedrive_folder,out_name,out_name) + ".shp"
        explode_shapefile(input_shp,os.path.join(os.path.dirname(input_shp),"exploded"))

        # Zip the entire output directory
        zip_name = os.path.join(onedrive_folder, f"WorkOrders_{today_date}_separate.zip") 
        out_dir = os.path.join(onedrive_folder,out_name)
        shutil.make_archive(zip_name,'zip',out_dir)
        # print(out_dir)

        os.remove(out_dir)

    else:
        print("No new features. Skipping export.")
else:        
    # Write initial count
    with open(os.path.join(onedrive_folder,"count.txt"),"w") as f:
        f.write(str(count))

print("Done")