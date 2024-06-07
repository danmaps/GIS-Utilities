import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import logging
from projCreator_utils import create_project
from textwrap import dedent


# Set up logging
logging.basicConfig(
    filename="error_log.txt",
    level=logging.ERROR,
    format="%(asctime)s:%(levelname)s:%(message)s",
)


class ProjectCreatorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ArcGIS Pro Project Creator")
        self.geometry("1040x400")
        self.configure(bg="black")
        self.iconbitmap("newproj.ico")
        self.dataset_count = 0  # Initialize dataset_count before calling create_widgets
        self.create_widgets()

    def create_widgets(self):
        form_frame = tk.Frame(self, bg="black")
        form_frame.pack(side="left", anchor="n", padx=20, pady=10)

        project_name_frame = tk.Frame(form_frame, bg="black")
        project_name_frame.pack(anchor="w", padx=20, pady=10)
        tk.Label(project_name_frame, text="Project Name:", bg="black", fg="white").grid(
            row=0, column=0, sticky="w"
        )
        self.project_name_entry = tk.Entry(project_name_frame, bg="grey", fg="white")
        self.project_name_entry.grid(row=0, column=1, sticky="w")

        folder_frame = tk.Frame(form_frame, bg="black")
        folder_frame.pack(anchor="w", padx=20, pady=10)
        tk.Label(folder_frame, text="Target Folder:", bg="black", fg="white").pack(
            side="left"
        )
        self.folder_var = tk.StringVar(value=r"c:\temp")
        folder_dropdown = ttk.Combobox(
            folder_frame,
            textvariable=self.folder_var,
            values=[r"c:\temp","2024Proj","MPO_Projects","Special_Projects","Data_Requests"],
        )
        folder_dropdown.pack(side="left", padx=5)

        datasets_frame = tk.Frame(form_frame, bg="black")
        datasets_frame.pack(anchor="w", padx=20, pady=10)
        tk.Label(
            datasets_frame, text="Datasets to include (optional):", bg="black", fg="white"
        ).grid(row=0, column=0, sticky="w")
        self.datasets_frame = tk.Frame(datasets_frame, bg="black")
        self.datasets_frame.grid(row=1, column=0, sticky="w")
        self.add_dataset_field()

        submit_button = tk.Button(
            form_frame,
            text="Create Project",
            command=self.submit_form,
            bg="grey",
            fg="white",
        )
        submit_button.pack(anchor="w", padx=20, pady=10)

        status_label = tk.Label(form_frame, text="", bg="black", fg="white")
        status_label.pack(anchor="w", padx=20, pady=10)
        self.status_label = status_label

        info_frame = tk.Frame(self, bg="black", bd=0)
        info_frame.pack(side="right", anchor="n", padx=20, pady=10)

        info_text = dedent(
            """\
            Welcome!

            Enter a project name, select a folder, and add datasets to include in the project.

            Excel/CSV fully supported. Other formats coming soon!
                           
            Shapefiles, FGDB feature classes, KMZ, CAD...

            If you have any questions or comments, please contact Daniel McVey.
        """
        )

        info_text_widget = tk.Text(
            info_frame,
            bg="black",
            fg="white",
            wrap="word",
            width=50,
            height=15,
            padx=10,
            pady=10,
            font=("Arial", 10),
            bd=0,
        )
        info_text_widget.insert(tk.END, info_text)
        info_text_widget.config(state=tk.DISABLED)  # Make the Text widget read-only
        info_text_widget.pack(anchor="n", padx=20, pady=10)

    def add_dataset_field(self):
        row = self.dataset_count
        entry = tk.Entry(self.datasets_frame, bg="grey", fg="white", width=100)
        entry.grid(row=row, column=0, padx=(0, 10), pady=5, sticky="w")
        browse_button = tk.Button(
            self.datasets_frame,
            text="Browse",
            command=lambda e=entry: self.browse_file(e),
            bg="grey",
            fg="white",
        )
        browse_button.grid(row=row, column=1, padx=5, pady=5, sticky="w")
        self.dataset_count += 1

    def browse_file(self, entry):
        file_path = filedialog.askopenfilename()
        if file_path:
            entry.delete(0, tk.END)
            entry.insert(0, file_path)
            self.add_dataset_field()

    def submit_form(self):
        project_name = self.project_name_entry.get()
        selected_folder = self.folder_var.get()
        if selected_folder == "Data_Requests":
            selected_folder = "Special_Projects\WSD_GIS_Schema\Data Requests"
        datasets = [
            entry.get()
            for entry in self.datasets_frame.winfo_children()
            if isinstance(entry, tk.Entry) and entry.get()
        ]

        try:
            # Create the project
            create_project(r"P:\PROJECTS", datasets, project_name, selected_folder)
            self.destroy()
        except FileNotFoundError as e:
            logging.error(e)
            messagebox.showerror("Error", str(e))
        except Exception as e:
            logging.error(e)
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    app = ProjectCreatorApp()
    app.mainloop()
