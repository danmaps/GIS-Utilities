from textual.app import App, ComposeResult
from textual.widgets import Button, Label, Input, Static
from textual.containers import Container, Vertical
from textual.events import ButtonPressed

class ProjectCreatorApp(App):
    CSS_PATH = "styles.css"  # Optional: path to your Textual CSS file
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.target_folders = [
            r"c:\temp", "2024Proj", "MPO_Projects", 
            "Special_Projects", "Data_Requests"
        ]
        self.current_target_folder = self.target_folders[0]
    
    def compose(self) -> ComposeResult:
        # Create layout and widgets
        with Vertical():
            yield Label("ArcGIS Pro Project Creator", id="header")
            yield Label("Project Name:")
            self.project_name_input = Input(placeholder="Enter project name", id="project_name")
            yield self.project_name_input
            
            yield Label("Target Folder:")
            self.target_folder_button = Button(self.current_target_folder, id="target_folder")
            yield self.target_folder_button
            
            self.target_folder_options = Vertical(id="target_folder_options")
            for folder in self.target_folders:
                yield Button(folder, id=folder)
            yield self.target_folder_options
            
            yield Button("Add Dataset", id="add_dataset")
            self.dataset_container = Static(id="datasets")
            yield self.dataset_container
            
            yield Button("Create Project", id="submit")
            self.status_label = Label("", id="status")
            yield self.status_label
            
        self.target_folder_options.visible = False  # Hide options by default

    def on_button_pressed(self, event: ButtonPressed) -> None:
        if event.button.id == "add_dataset":
            self.add_dataset_field()
        elif event.button.id == "submit":
            self.submit_form()
        elif event.button.id == "target_folder":
            # Toggle the visibility of the dropdown options
            self.target_folder_options.visible = not self.target_folder_options.visible
            self.refresh()
        elif event.button.id in self.target_folders:
            # Update the target folder selection
            self.current_target_folder = event.button.id
            self.target_folder_button.label = self.current_target_folder
            self.target_folder_options.visible = False  # Hide options after selection
            self.refresh()

    def add_dataset_field(self):
        # Add a new dataset input field
        new_dataset_input = Input(placeholder="Enter dataset path")
        self.dataset_container.mount(new_dataset_input)

    def submit_form(self):
        project_name = self.project_name_input.value
        selected_folder = self.current_target_folder
        datasets = [child.value for child in self.dataset_container.children if isinstance(child, Input) and child.value]

        if not project_name or not selected_folder:
            self.status_label.update("Project name and folder are required!")
            return

        try:
            # Implement your project creation logic here
            self.status_label.update(f"Project '{project_name}' created successfully in '{selected_folder}'!")
        except Exception as e:
            self.status_label.update(f"Error: {e}")

if __name__ == "__main__":
    ProjectCreatorApp().run()
