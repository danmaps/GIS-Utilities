import os
import arcpy
import shutil
import pandas as pd


def validate_project_name(project_name):
    if not project_name or project_name.strip() in ["", "_", "-"]:
        raise ValueError("Valid project name is required.")
    return project_name.replace(" ", "_")


def create_folder_structure(base_path, template_path, project_name):
    if base_path.endswith("2024Proj"):
        project_folder = os.path.join(base_path, f"2024_{project_name}")
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


def set_project_defaults(aprx, project_folder, project_name):
    arcpy.CreateFileGDB_management(project_folder, f"{project_name}.gdb")
    aprx.defaultGeodatabase = os.path.join(project_folder, f"{project_name}.gdb")
    shutil.copyfile(
        r"P:\Tools\TemplateProject\template.atbx",
        os.path.join(project_folder, f"{project_name}.atbx"),
    )
    aprx.defaultToolbox = os.path.join(project_folder, f"{project_name}.atbx")
    aprx.updateFolderConnections(
        [{"connectionString": project_folder, "alias": "", "isHomeFolder": True}],
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
        data_folder, os.path.splitext(os.path.basename(file_path))[0] + ".lyr"
    )
    arcpy.conversion.KMLToLayer(file_path, data_folder)
    return layer_output_path


def handle_cad(file_path, data_folder):
    gdb_path = os.path.join(
        data_folder, os.path.splitext(os.path.basename(file_path))[0] + ".gdb"
    )
    arcpy.conversion.CADToGeodatabase(file_path, gdb_path)
    return gdb_path


def update_status(message):
    print(message)


def create_project(base_path, datasets, project_name, selected_folder):
    try:
        project_name = validate_project_name(project_name)
        selected_folder_path = os.path.join(base_path, selected_folder)
        project_folder = create_folder_structure(
            selected_folder_path, r"P:\PROJECTS\PROJECT_FOLDER_STRUCTURE", project_name
        )
        data_folder = os.path.join(project_folder, "data")

        for file_path in datasets:
            if file_path.endswith((".xlsx", ".xls", ".csv")):
                update_status(f"Processing Excel/CSV file: {file_path}")
                handle_excel_csv(file_path, data_folder)
            elif file_path.endswith((".kml", ".kmz")):
                update_status(f"Processing KML/KMZ file: {file_path}")
                handle_kml_kmz(file_path, data_folder)
            elif file_path.endswith((".dwg", ".dxf", ".dgn")):
                update_status(f"Processing CAD file: {file_path}")
                handle_cad(file_path, data_folder)
            else:
                raise ValueError(f"Unsupported file type: {file_path}")

        update_status(f"Creating project structure at {project_folder}")

        # add the datasets to the map
        working_folder = os.path.join(project_folder, "working")
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
                if not os.path.exists(os.path.join(data_folder, dataset + ".lyrx")):
                    for fc in arcpy.ListFeatureClasses("*", "", dataset):
                        m.addDataFromPath(os.path.join(data_folder, dataset, fc))

            else:
                raise ValueError(f"Unsupported dataset type: {dataset}")
        set_project_defaults(aprx, project_folder, project_name)
        aprx.save()

        update_status(
            f"Project '{project_name}' created successfully at {project_folder}"
        )

        os.startfile(new_project_path)

    except Exception as e:
        update_status(f"Error: {e}")
        raise
