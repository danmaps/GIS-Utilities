'''
desired folder structure:
WestCovina_SLs
    WorkOrders_DateTime.zip
        WorkOrders_DateTime.zip
            WorkOrders_DateTime.shp
        separate
            WorkOrder1_DateTime.zip
                WorkOrder1_DateTime.shp
            WorkOrder2_DateTime.zip
                WorkOrder2_DateTime.shp
                    
'''

import arcpy
from arcgis.gis import GIS
import datetime
import zipfile
import os
import shutil
import time

def explode_shapefile(input_shp, output_folder, today_date):
    """Explodes a shapefile with polygons into separate shapefiles based on 'WorkOrder' attribute"""

    # consider replacing some of the logic below with Split By Attributes (Analysis)
    # arcpy.analysis.SplitByAttributes(Input_Table, Target_Workspace, Split_Fields)
    # https://pro.arcgis.com/en/pro-app/latest/tool-reference/analysis/split-by-attributes.htm
    
    # Get the shapefile name without extension
    shp_name = os.path.splitext(os.path.basename(input_shp))[0]
    
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    # Loop through features
    with arcpy.da.SearchCursor(input_shp, ["WorkOrder","SHAPE@","FID"]) as cursor:
        for row in cursor:
            work_order = row[0]            
            out_name = f"{shp_name}_{work_order}"
            
            # Check if work order is populated
            if work_order:
                out_shp = os.path.join(output_folder, f"{out_name}.shp")
                
                # Export single feature to new shapefile
                # print(out_shp)
                if not os.path.exists(out_shp) and not out_shp.endswith(" .shp"):
                    # print(os.path.exists(output_folder))
                    arcpy.conversion.ExportFeatures(input_shp, out_shp, f'"FID" = {row[2]}')
                    
                    # Zip separate shapefile folder
                    zip_name = os.path.join(output_folder,f"{out_name}.zip")
                    all_files = []
                    for f in os.listdir(os.path.join(output_folder)):
                        # print(f,work_order)
                        if os.path.isfile(os.path.join(output_folder, f)) and work_order in f:
                            if not f.endswith(".sr.lock"): 
                                all_files.append(f)
                    # print(all_files)
                    zip_file = zipfile.ZipFile(zip_name, "w")
                    for file in all_files:
                        zip_file.write(os.path.join(output_folder, file), arcname=file)
                    zip_file.close()

                    # Delete shapefile and folder
                    arcpy.Delete_management(os.path.join(output_folder,out_shp))
                    arcpy.Delete_management(os.path.join(output_folder, f"{shp_name}_{work_order}"))

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
count_file = os.path.join(onedrive_folder+"_count", "count.txt")
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
        zip_name = os.path.join(onedrive_folder,out_name,f"WorkOrders_{today_date}.zip")
        all_files = [f for f in os.listdir(os.path.join(onedrive_folder,out_name))
                     if os.path.isfile(os.path.join(onedrive_folder,out_name, f))
                     and not f.endswith(".sr.lock")]
        zip_file = zipfile.ZipFile(zip_name, "w")
        for file in all_files:
            # print(file)
            
            zip_file.write(os.path.join(onedrive_folder,out_name, file), arcname=file)
        zip_file.close()

        # # Set ArcGIS online folder name
        # folder_name = "Shapefile exports"

        # # Publish shapefile item to folder
        # new_item = gis.content.add({"type":"Shapefile","title": f"WorkOrders_{today_date}"}, 
        #                            os.path.join(onedrive_folder,f"WorkOrders_{today_date}.zip"),folder = folder_name)

        # # Set sharing level                         
        # new_item.share(org=True)

        # print("published:",new_item.homepage)
        
        # Overwrite count file
        with open(count_file,"w") as f:
            f.write(str(count))                   

        # Explode shapefile into separate work order shapefiles
        input_shp = os.path.join(onedrive_folder,out_name,out_name) + ".shp"
        explode_shapefile(input_shp,os.path.join(os.path.dirname(input_shp),"separate"),today_date)

        arcpy.Delete_management(os.path.join(input_shp))

        # Zip the entire output directory
        zip_name = os.path.join(onedrive_folder, f"WorkOrders_{today_date}") 
        out_dir = os.path.join(onedrive_folder,out_name)
        shutil.make_archive(zip_name,'zip',out_dir)
        # print(out_dir)

        arcpy.Delete_management(os.path.join(out_dir))

    else:
        print("No new features. Skipping export.")
else:        
    # Write initial count
    with open(os.path.join(onedrive_folder+"_count","count.txt"),"w") as f:
        f.write(str(count))

print("Done")