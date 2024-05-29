import os
import arcpy
import shutil
import pandas as pd


def validate_project_name(project_name):
    if not project_name or project_name.strip() in ["", "_", "-"]:
        raise ValueError("Valid project name is required.")
    return project_name.replace(' ', '_')


def create_folder_structure(base_path, template_path, project_name):
    print(project_name)
    if base_path.endswith("2024Proj"):
        project_folder = os.path.join(base_path, f"2024_{project_name}")
    else:
        project_folder = os.path.join(base_path, project_name)
    shutil.copytree(template_path, project_folder, dirs_exist_ok=True)
    return project_folder


def copy_excel_to_data_folder(excel_path, project_folder):
    data_folder = os.path.join(project_folder, "data")
    os.makedirs(data_folder, exist_ok=True)
    csv_path = os.path.join(data_folder, os.path.basename(excel_path))
    shutil.copyfile(excel_path, csv_path)
    return csv_path


def convert_excel_to_csv(excel_path, sheet_name, data_folder):
    df = pd.read_excel(excel_path, sheet_name=sheet_name if sheet_name else 0)
    csv_name = f"{os.path.splitext(os.path.basename(excel_path))[0]}"
    if sheet_name:
        csv_name += f"_{sheet_name}"
    csv_name += ".csv"
    csv_output_path = os.path.join(data_folder, csv_name)
    df.to_csv(csv_output_path, index=False)
    return csv_output_path


def create_project_from_template(template_project_path, working_folder, project_name):
    new_project_path = os.path.join(working_folder, f"{project_name}.aprx")
    aprx = arcpy.mp.ArcGISProject(template_project_path)
    aprx.saveACopy(new_project_path)
    return new_project_path


def update_project(aprx, project_folder, csv_output_path):
    m = aprx.listMaps("Map")[0]
    m.addDataFromPath(csv_output_path)
    aprx.updateFolderConnections([{"connectionString": project_folder, "alias": "", "isHomeFolder": True}], validate=False)
    return aprx


def set_project_defaults(aprx, working_folder, project_name):
    arcpy.CreateFileGDB_management(working_folder, f"{project_name}.gdb")
    aprx.defaultGeodatabase = os.path.join(working_folder, f"{project_name}.gdb")
    shutil.copyfile(r"P:\Tools\TemplateProject\template.atbx", os.path.join(working_folder, f"{project_name}.atbx"))
    aprx.defaultToolbox = os.path.join(working_folder, f"{project_name}.atbx")
    aprx.save()


def update_status(status_label, progress, root, status_text, progress_value):
    status_label.config(text=status_text)
    progress['value'] = progress_value
    root.update_idletasks()


def create_project(base_project_path, excel_path, sheet_name, project_name, progress, status_label, root):
    try:
        project_name = validate_project_name(project_name)

        excel_path = excel_path.replace('"', '') if excel_path else excel_path

        template_path = r"P:\PROJECTS\PROJECT_FOLDER_STRUCTURE"

        project_folder = create_folder_structure(base_project_path, template_path, project_name)
        working_folder = os.path.join(project_folder, "working")

        update_status(status_label, progress, root, "Step 1: Create new project folder and copy structure...", 20)

        if excel_path:
            if not os.path.exists(excel_path):
                raise FileNotFoundError(f"Excel file not found at {excel_path}.")
            csv_path = copy_excel_to_data_folder(excel_path, project_folder)
            update_status(status_label, progress, root, "Step 2: Copy the Excel file to the data subfolder...", 40)

            csv_output_path = convert_excel_to_csv(excel_path, sheet_name, os.path.join(project_folder, "data"))

        template_project_path = r"P:\Tools\TemplateProject\template.aprx"
        new_project_path = create_project_from_template(template_project_path, working_folder, project_name)
        update_status(status_label, progress, root, "Step 3: Create a new project from the template...", 60)

        aprx = arcpy.mp.ArcGISProject(new_project_path)
        if excel_path:
            aprx = update_project(aprx, project_folder, csv_output_path)
            update_status(status_label, progress, root, "Step 4: Add the CSV to the existing map...", 80)

        set_project_defaults(aprx, working_folder, project_name)
        update_status(status_label, progress, root, "Step 5: Set project defaults, then save and open the project...", 100)

        os.startfile(new_project_path)
        print(f"Project '{project_name}' created successfully at {project_folder}.")

    except Exception as e:
        status_label.config(text=f"Error: {e}")
        progress['value'] = 0
        root.update_idletasks()
