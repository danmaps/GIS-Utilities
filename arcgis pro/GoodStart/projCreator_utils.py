import os
import arcpy
import shutil
import pandas as pd


def create_project(excel_path, sheet_name, project_name, progress, status_label, root):
        # Replace spaces with underscores in the project name
        project_name = project_name.replace(' ', '_')

        # handle the case where the user provides a path with double quotes
        excel_path = excel_path.replace('"', '')

        # Define paths
        base_project_path = r"P:\PROJECTS\2024Proj"
        template_path = r"P:\PROJECTS\PROJECT_FOLDER_STRUCTURE"
        project_folder = os.path.join(base_project_path, "2024_"+project_name)
        working_folder = os.path.join(project_folder, "working")

        # Create new project folder and copy structure
        os.makedirs(project_folder, exist_ok=True)
        shutil.copytree(template_path, project_folder, dirs_exist_ok=True)
        status_label.config(text="Step 1: Create new project folder and copy structure...")
        progress['value'] = 20
        root.update_idletasks()

        # Copy the Excel file to the data subfolder
        data_folder = os.path.join(project_folder, "data")
        os.makedirs(data_folder, exist_ok=True)
        csv_path = os.path.join(data_folder, os.path.basename(excel_path))
        shutil.copyfile(excel_path, csv_path)
        status_label.config(text="Step 2: Copy the Excel file to the data subfolder...") 
        progress['value'] = 40
        root.update_idletasks()

        # Load the Excel file into a DataFrame
        df = pd.read_excel(excel_path, sheet_name=sheet_name if sheet_name else 0)
        if sheet_name:
            csv_name = f"{os.path.splitext(os.path.basename(excel_path))[0]}_{sheet_name}.csv"
        else:
            csv_name = f"{os.path.splitext(os.path.basename(excel_path))[0]}.csv"

        csv_output_path = os.path.join(data_folder, csv_name)
        df.to_csv(csv_output_path, index=False)

        # Create a new project from the template
        template_project_path = r"P:\Tools\TemplateProject\template.aprx"
        new_project_path = os.path.join(working_folder, f"{project_name}.aprx")
        aprx = arcpy.mp.ArcGISProject(template_project_path)
        aprx.saveACopy(new_project_path)
        status_label.config(text="Step 3: Create a new project from the template...")
        progress['value'] = 60
        root.update_idletasks()

        # add the CSV to the existing map called Map in the project
        new_aprx = arcpy.mp.ArcGISProject(new_project_path)
        m = new_aprx.listMaps("Map")[0]
        m.addDataFromPath(csv_output_path)
        status_label.config(text="Step 4: Add the CSV to the existing map...")
        progress['value'] = 80
        root.update_idletasks()
        
        # update the project home folder
        connections = [
            {"connectionString": project_folder, "alias": "", "isHomeFolder": True},
            ]
        new_aprx.updateFolderConnections(connections, validate=False)

        # update the default geodatabase
        arcpy.CreateFileGDB_management(working_folder, f"{project_name}.gdb")
        new_aprx.defaultGeodatabase = os.path.join(working_folder, f"{project_name}.gdb")
        
        # update the default toolbox
        shutil.copyfile(r"P:\Tools\TemplateProject\template.atbx", os.path.join(working_folder, f"{project_name}.atbx"))
        new_aprx.defaultToolbox = os.path.join(working_folder, f"{project_name}.atbx")

        # save the project
        new_aprx.save()
        status_label.config(text="Step 5: Set project defaults, then save and open the project...")
        progress['value'] = 100
        root.update_idletasks()
                
        # Open the new project
        os.startfile(new_project_path)
        
        # Notify user of success (this could be a UI update instead)
        print(f"Project '{project_name}' created successfully at {project_folder}.")