import os
import arcpy
import shutil
import pandas as pd
import datetime
import re


def validate_project_name(project_name):
    if not project_name or project_name.strip() in ["", "_", "-"]:
        raise ValueError("Valid project name is required.")
    return project_name.replace(" ", "_")


def create_folder_structure(base_path, template_path, project_name):
    if base_path.endswith("2024Proj"):
        project_folder = os.path.join(base_path, f"{datetime.now().strftime('%Y')}_{project_name}")
    elif base_path.endswith("Data_Requests"):
        project_folder = os.path.join(base_path, f"{datetime.now().strftime('%Y%m%d')}_{project_name}")
    else:
        project_folder = os.path.join(base_path, project_name)

    shutil.copytree(template_path, project_folder, dirs_exist_ok=True)
    DataCleanUp_docfile = os.path.join(
        project_folder, "DataCleanUp_Ver1_20130411_JL.doc"
    )
    if os.path.exists(DataCleanUp_docfile):
        os.remove(DataCleanUp_docfile)
    return project_folder


def create_project_from_template(template_project_path, working_folder, project_name):
    new_project_path = os.path.join(working_folder, f"{project_name}.aprx")
    aprx = arcpy.mp.ArcGISProject(template_project_path)
    aprx.saveACopy(new_project_path)
    return new_project_path


def set_project_defaults(aprx, folderPath, projectName):
    arcpy.CreateFileGDB_management(folderPath, f"{projectName}.gdb")
    aprx.defaultGeodatabase = os.path.join(folderPath, f"{projectName}.gdb")
    shutil.copyfile(
        r"P:\Tools\TemplateProject\template.atbx",
        os.path.join(folderPath, f"{projectName}.atbx"),
    )
    aprx.defaultToolbox = os.path.join(folderPath, f"{projectName}.atbx")
    aprx.updateFolderConnections(
        [{"connectionString": os.path.dirname(folderPath), "alias": "", "isHomeFolder": True}],
        validate=False,
    )
    aprx.save()


def handle_excel_csv(file_path, data_folder):
    if file_path.endswith(".csv"):
        csv_output_path = os.path.join(data_folder, os.path.basename(file_path))
        shutil.copyfile(file_path, csv_output_path)
        return file_path
    else:  # Excel file
        data = pd.read_excel(file_path, sheet_name=None)
        for sheet_name, df in data.items():
            csv_output_path = os.path.join(
                data_folder,
                os.path.splitext(os.path.basename(file_path))[0]
                + "_"
                + sheet_name
                + ".csv",
            )
            df.to_csv(csv_output_path, index=False)
        return csv_output_path


def handle_kml_kmz(file_path, data_folder):
    layer_output_path = os.path.join(
        data_folder, os.path.splitext(os.path.basename(file_path))[0] + ".lyrx"
    )
    arcpy.conversion.KMLToLayer(file_path, data_folder)
    return layer_output_path


def handle_cad(file_path, data_folder):
    
    # Construct the path for the output geodatabase
    out_gdb_path = os.path.join(data_folder, "cad.gdb")
    
    # Create the geodatabase if it doesn't exist
    if not arcpy.Exists(out_gdb_path):
        arcpy.management.CreateFileGDB(data_folder, "cad.gdb")

    arcpy.conversion.CADToGeodatabase(
        input_cad_datasets=file_path,
        out_gdb_path=out_gdb_path,
        out_dataset_name=re.sub(r'[^a-zA-Z0-9_]', '_', os.path.splitext(os.path.basename(file_path))[0]),
        reference_scale=1000,
        spatial_reference=None
    )
    return out_gdb_path


def handle_gdb(file_path, data_folder):
    gdb_path = os.path.join(data_folder, os.path.splitext(os.path.basename(file_path))[0] + ".gdb")
    # shutil.copytree(file_path, gdb_path, dirs_exist_ok=True)
    print(f"Source path: {file_path}")
    print(f"Destination path: {gdb_path}")
    arcpy.Copy_management(file_path.replace('/', '\\'), gdb_path)
    return gdb_path

def handle_gdb(file_path, data_folder):
    try:
        # Ensure the target directory exists
        if not os.path.exists(data_folder):
            os.makedirs(data_folder)

        # Construct the destination path
        gdb_name = os.path.basename(file_path)
        gdb_path = os.path.join(data_folder, gdb_name)

        # Create the target geodatabase if it doesn't exist
        if not arcpy.Exists(gdb_path):
            arcpy.management.CreateFileGDB(data_folder, os.path.splitext(gdb_name)[0])
        
        arcpy.env.workspace = file_path
        
        # Copy feature classes
        feature_classes = arcpy.ListFeatureClasses()
        for fc in feature_classes:
            arcpy.FeatureClassToFeatureClass_conversion(fc, gdb_path, fc)
        
        # Copy tables
        tables = arcpy.ListTables()
        for table in tables:
            arcpy.TableToTable_conversion(table, gdb_path, table)
        
        print(f"Successfully copied geodatabase to {gdb_path}")
        return gdb_path

    except arcpy.ExecuteError:
        print(f"Error copying geodatabase: {arcpy.GetMessages(2)}")
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise

def add_feature_classes_to_map(data_folder, dataset, map_obj):
    # Set the workspace to the dataset
    arcpy.env.workspace = os.path.join(data_folder, dataset)
    
    # Add feature classes at the base level
    for fc in arcpy.ListFeatureClasses():
        desc = arcpy.Describe(fc)
        print(f"Adding {desc.name} to map")
        map_obj.addDataFromPath(desc.catalogPath)
    
    # List all feature datasets and add their feature classes
    for fds in arcpy.ListDatasets(feature_type='feature'):
        arcpy.env.workspace = os.path.join(data_folder, dataset, fds)
        for fc in arcpy.ListFeatureClasses():
            desc = arcpy.Describe(fc)
            print(f"Adding {desc.name} to map")
            map_obj.addDataFromPath(desc.catalogPath)
    
    # Reset the workspace
    arcpy.env.workspace = None


def create_project(base_path, datasets, project_name, selected_folder):
    try:
        project_name = validate_project_name(project_name)
        selected_folder_path = os.path.join(base_path, selected_folder)
        folder_structure = r"P:\PROJECTS\PROJECT_FOLDER_STRUCTURE"
        if selected_folder == "Data_Requests":
            folder_structure = r"P:\PROJECTS\Special_Projects\WSD_GIS_Schema\Data_Requests\X_DR_FOLDER_STRUCTURE"
        project_folder = create_folder_structure(
            selected_folder_path, folder_structure, project_name
        )
        
        print(f"Created {project_name} at {project_folder}")
        working_folder = os.path.join(project_folder, "Working")
        if selected_folder == "Data_Requests":
            working_folder = os.path.join(project_folder, "Data")
        
        data_folder = os.path.join(project_folder, "Data")
        
        for file_path in datasets:
            if file_path.endswith((".xlsx", ".xls", ".csv")):
                print(f"Processing Excel/CSV file: {file_path}")
                handle_excel_csv(file_path, data_folder)
            elif file_path.endswith((".kml", ".kmz")):
                print(f"Processing KML/KMZ file: {file_path}")
                handle_kml_kmz(file_path, data_folder)
            elif file_path.endswith((".dwg", ".dxf", ".dgn")):
                print(f"Processing CAD file: {file_path}")
                handle_cad(file_path, data_folder)
            elif file_path.endswith((".gdb")):
                print(f"Processing GDB: {file_path}")
                handle_gdb(file_path, data_folder)
            else:
                shapefile_extensions = {'.shp', '.shx', '.dbf', '.prj', '.sbn', '.sbx', '.cpg', '.xml'}
                # Get the file extension
                _, file_extension = os.path.splitext(file_path)

                # Check if the file is part of a shapefile and if it is the main .shp file
                if file_extension in shapefile_extensions:
                    if file_extension == '.shp':
                        print(f"Processing Excel/CSV file: {file_path}")
                        arcpy.Copy_management(file_path, os.path.join(data_folder, os.path.splitext(os.path.basename(file_path))[0] + ".shp"))
                    else:
                        # Ignore other files that are part of the shapefile
                        continue
                if file_extension != '.shp':
                    print(f"Skipped unsupported file: {file_path}")

        # add the datasets to the map

        template_project_path = r"P:\Tools\TemplateProject\template.aprx"
        new_project_path = create_project_from_template(
            template_project_path, working_folder, project_name
        )
        aprx = arcpy.mp.ArcGISProject(new_project_path)
        m = aprx.listMaps()[0]
        for dataset in os.listdir(data_folder):
            if dataset.endswith(".csv"):
                m.addDataFromPath(os.path.join(data_folder, dataset))
            elif dataset.endswith(".lyrx"):
                m.addDataFromPath(os.path.join(data_folder, dataset))
            elif dataset.endswith(".gdb"):
                # if the dataset that endswith lyrx is added to the map
                # ignore the corresponding gdb with the same name
                # because that means it is a converted KML/KMZ file and the lyrx is added directly
                if not os.path.exists(os.path.join(data_folder, os.path.splitext(dataset)[0] + ".lyrx")):
                    add_feature_classes_to_map(data_folder,dataset,m)
            elif dataset.endswith(".shp"):
                m.addDataFromPath(os.path.join(data_folder, dataset))
            elif os.path.splitext(dataset)[1].lower() in ['.shx', '.dbf', '.prj', '.sbn', '.sbx', '.cpg', '.xml']:
                pass
            else:
                print(f"Unsupported dataset type: {dataset}")

        set_project_defaults(aprx, working_folder, project_name)
        aprx.save()

        print(
            f"Project '{project_name}' created successfully at {project_folder}"
        )

        os.startfile(new_project_path)

    except Exception as e:
        print(f"Error: {e}")
        raise
