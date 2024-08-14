from textual.app import App, ComposeResult
from textual.widgets import Button, Label, Input, Static
from textual.containers import Container
# from projCreator_utils import create_project
import os
import logging
import subprocess

# arcgis pro python path
arcgispro_py3 = r"C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe"

class ProjectCreatorApp(App):
    CSS_PATH = "styles.css"  # Optional: path to your Textual CSS file

    def compose(self) -> ComposeResult:
        # Create layout and widgets
        with Container():
            yield Label("ArcGIS Pro Project Creator", id="header")
            yield Label("Project Name:")
            self.project_name_input = Input(placeholder="Enter project name", id="project_name")
            yield self.project_name_input
            
            yield Label("Target Folder:")
            self.folder_input = Input(value=r"c:\temp", id="folder")
            yield self.folder_input
            
            yield Button("Add Dataset", id="add_dataset")
            self.dataset_container = Static(id="datasets")
            yield self.dataset_container
            
            yield Button("Create Project", id="submit")
            self.status_label = Label("", id="status")
            yield self.status_label

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "add_dataset":
            self.add_dataset_field()
        elif event.button.id == "submit":
            self.submit_form()

    def add_dataset_field(self):
        # Add a new dataset input field
        new_dataset_input = Input(placeholder="Enter dataset path")
        self.dataset_container.mount(new_dataset_input)

    def submit_form(self):
        project_name = self.project_name_input.value
        selected_folder = self.folder_input.value
        datasets = [child.value for child in self.dataset_container.children if isinstance(child, Input) and child.value]

        if not project_name or not selected_folder:
            self.status_label.update("Project name and folder are required!")
            return

        try:
            # use a subprocess to run create_project() in a separate thread with arcgispro_py3
            subprocess.run([arcgispro_py3, "-c", f"""
import sys
from projCreator_utils import create_project
create_project(r'P:\\\\PROJECTS', {datasets}, r'{project_name}', r'{selected_folder}')
"""], check=True)


            self.status_label.update(f"Project '{project_name}' created successfully!")
        except subprocess.CalledProcessError as e:
            self.status_label.update(f"Subprocess error: {e}")
        except Exception as e:
            self.status_label.update(f"Error: {e}")

if __name__ == "__main__":
    ProjectCreatorApp().run()
