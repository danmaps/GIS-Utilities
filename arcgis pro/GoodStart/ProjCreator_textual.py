# ProjCreator
# https://chatgpt.com/c/1dea25e7-4052-428c-97ea-4ce851414e04

import os
import shutil
import pandas as pd
import arcpy
from textual.app import App
from textual.widgets import Header, Footer, Input, Button, Static, Placeholder
from textual.containers import Vertical

# Define your Textual App
class ProjCreator(App):

    def compose(self):
        # Define the UI components
        yield Header()
        yield Vertical(
            Static("Enter Excel Spreadsheet Path:"),
            Input(id="excel_path"),
            Static("Enter Sheet Name (optional):"),
            Input(id="sheet_name"),
            Static("Enter Project Name:"),
            Input(id="project_name"),
            Button("Create Project", id="create_button"),
            Placeholder(),
        )
        yield Footer()

    def on_mount(self):
        # Focus the first input field when the app is started
        self.query_one(Input).focus()

    async def on_button_pressed(self, message):
        # Triggered when the button is pressed
        if message.button.id == "create_button":
            excel_path = self.query_one(Input, id="excel_path").value
            sheet_name = self.query_one(Input, id="sheet_name").value
            project_name = self.query_one(Input, id="project_name").value
            self.create_project(excel_path, sheet_name, project_name)

    def create_project(self, excel_path, sheet_name, project_name):
        # Replace spaces with underscores in the project name
        project_name = project_name.replace(' ', '_')

        # Define paths
        base_project_path = r"P:\PROJECTS\2024Proj"
        template_path = r"P:\PROJECTS\PROJECT_FOLDER_STRUCTURE"
        project_folder = os.path.join(base_project_path, project_name)

        # Create new project folder and copy structure
        os.makedirs(project_folder, exist_ok=True)
        shutil.copytree(template_path, project_folder, dirs_exist_ok=True)

        # Copy the Excel file to the data subfolder
        data_folder = os.path.join(project_folder, "data")
        os.makedirs(data_folder, exist_ok=True)
        csv_path = os.path.join(data_folder, os.path.basename(excel_path))
        shutil.copyfile(excel_path, csv_path)

        # Load the Excel file into a DataFrame
        df = pd.read_excel(excel_path, sheet_name=sheet_name if sheet_name else 0)
        csv_output_path = os.path.join(data_folder, "data.csv")
        df.to_csv(csv_output_path, index=False)

        # Create a new project from the template
        template_project_path = "Template_File_Path.aprx"  # Update this path
        new_project_path = os.path.join(project_folder, f"{project_name}.aprx")
        aprx = arcpy.mp.ArcGISProject(template_project_path)
        aprx.saveACopy(new_project_path)
        
        # Add a new map to the project and add the CSV
        new_aprx = arcpy.mp.ArcGISProject(new_project_path)
        new_map = new_aprx.createMap(project_name)
        new_map.addDataFromPath(csv_output_path)
        new_aprx.save()
        
        # Open the new project
        os.startfile(new_project_path)
        
        # Notify user of success (this could be a UI update instead)
        print(f"Project '{project_name}' created successfully at {project_folder}.")

# Run the ProjCreator app
if __name__ == "__main__":
    ProjCreator.run()
