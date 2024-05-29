import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import logging
import tempfile
import os
from projCreator_utils import create_project  # Ensure this import statement is correct

# Set up logging
logging.basicConfig(filename='error_log.txt', level=logging.ERROR,
                    format='%(asctime)s:%(levelname)s:%(message)s')

def submit_form(event=None):
    excel_path = excel_path_entry.get()
    sheet_name = sheet_name_entry.get()
    project_name = project_name_entry.get()
    selected_folder = folder_var.get()

    try:
        # Define the base path based on the selected folder
        base_path = r"P:\PROJECTS"
        if selected_folder == "2024Proj":
            project_path = os.path.join(base_path, "2024Proj", "2024_" + project_name)
        else:
            project_path = os.path.join(base_path, selected_folder, project_name)
        
        # Create the project
        if excel_path:
            create_project(project_path, excel_path, sheet_name, project_name, progress, status_label, root)
        else:
            create_project(project_path, None, None, project_name, progress, status_label, root)
        
        messagebox.showinfo("Success", "Project created successfully.")
        root.destroy()
    except FileNotFoundError:
        error_message = "Excel spreadsheet not found. Please check the path and try again."
        logging.error(error_message)
        messagebox.showerror("Error", error_message)
    except Exception as e:
        error_message = f"An unexpected error occurred: {str(e)}"
        logging.error(error_message)
        messagebox.showerror("Error", error_message)

def toggle_excel_options():
    if excel_options_frame.winfo_viewable():
        excel_options_frame.pack_forget()
    else:
        excel_options_frame.pack(anchor='w', padx=20, pady=10)

# Main GUI setup
root = tk.Tk()
root.geometry('800x400')
root.configure(bg='black')

# Main Form Frame
form_frame = tk.Frame(root, bg='black')
form_frame.pack(side='left', anchor='n', padx=20, pady=10)

# Project Name Frame
project_name_frame = tk.Frame(form_frame, bg='black')
project_name_frame.pack(anchor='w', padx=20, pady=10)

tk.Label(project_name_frame, text="Project Name:", bg='black', fg='white').grid(row=0, column=0, sticky='w')
project_name_entry = tk.Entry(project_name_frame, bg='grey', fg='white')
project_name_entry.grid(row=0, column=1, sticky='w')

# Folder Selection Frame
folder_frame = tk.Frame(form_frame, bg='black')
folder_frame.pack(anchor='w', padx=20, pady=10)

folder_var = tk.StringVar(value="2024Proj")
folder_dropdown = ttk.Combobox(folder_frame, textvariable=folder_var, values=["2024Proj", "MPO_Projects", "Special_Projects"])
folder_dropdown.pack(side='left', padx=5)

tk.Label(folder_frame, text="P:\\PROJECTS\\", bg='black', fg='white').pack(side='left')

# Excel Options Button and Frame
excel_options_button = tk.Button(form_frame, text="Show/Hide Excel Options", command=toggle_excel_options, bg='grey', fg='white')
excel_options_button.pack(anchor='w', padx=20, pady=10)

excel_options_frame = tk.Frame(form_frame, bg='black')
excel_options_frame.pack(anchor='w', padx=20, pady=10)
excel_options_frame.pack_forget()

tk.Label(excel_options_frame, text="Excel Spreadsheet Path (optional):", bg='black', fg='white').grid(row=0, column=0, sticky='w')
excel_path_entry = tk.Entry(excel_options_frame, bg='grey', fg='white')
excel_path_entry.grid(row=0, column=1, sticky='w')

tk.Label(excel_options_frame, text="Sheet Name (optional):", bg='black', fg='white').grid(row=1, column=0, sticky='w')
sheet_name_entry = tk.Entry(excel_options_frame, bg='grey', fg='white')
sheet_name_entry.grid(row=1, column=1, sticky='w')

# Submit Button
submit_button = tk.Button(form_frame, text="Create Project", command=submit_form, bg='grey', fg='white')
submit_button.pack(anchor='w', padx=20, pady=10)

# Status Label
status_label = tk.Label(form_frame, text="", bg='black', fg='white')
status_label.pack(anchor='w', padx=20, pady=10)

# Progress Bar Style
style = ttk.Style()
style.configure("TProgressbar",
                troughcolor='black',
                background='grey',
                troughrelief='flat',
                bordercolor='black')

# Progress Bar
progress = ttk.Progressbar(form_frame, orient="horizontal", length=200, mode="determinate", style="TProgressbar")
progress.pack(anchor='w', padx=20, pady=10)

# Information Frame
info_frame = tk.Frame(root, bg='black')
info_frame.pack(side='right', anchor='n', padx=20, pady=10)

# Information Label
info_text = (
    "This tool is for creating new projects. "
    "If you have any questions or comments, please contact Daniel McVey."
)
info_label = tk.Label(info_frame, text=info_text, bg='black', fg='white', wraplength=200, justify='left')
info_label.pack(anchor='n', padx=20, pady=10)

# Bind 'Enter' key to submit_form function
root.bind('<Return>', submit_form)

root.mainloop()
