import os
import arcpy
import shutil
import pandas as pd
import datetime


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
    gdb_path = os.path.join(
        data_folder, os.path.splitext(os.path.basename(file_path))[0] + ".gdb"
    )
    arcpy.conversion.CADToGeodatabase(file_path, gdb_path)
    return gdb_path


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
            elif file_path.endswith((".shp", ".gdb")):
                print(f"Copying dataset: {file_path}")
                shutil.copytree(file_path, os.path.join(data_folder, os.path.basename(file_path)))
            else:
                print(f"Skipped unsupported file: {file_path}")

        # add the datasets to the map
        working_folder = os.path.join(project_folder, "Working")
        if selected_folder == "Data_Requests":
            working_folder = os.path.join(project_folder, "Data")
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
                    for fc in arcpy.ListFeatureClasses("*", "", dataset):
                        m.addDataFromPath(os.path.join(data_folder, dataset, fc))
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
