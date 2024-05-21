import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from projCreator_utils import create_project
import time

def submit_form(event=None):
    excel_path = excel_path_entry.get()
    sheet_name = sheet_name_entry.get()
    project_name = project_name_entry.get()

    try:
        create_project(excel_path, sheet_name, project_name, progress, status_label, root)
        # messagebox.showinfo("Success", f"Project '{project_name}' created successfully.")
        root.destroy()  # Close the application
    except Exception as e:
        messagebox.showerror("Error", str(e))

root = tk.Tk()
root.geometry('500x200')  # Set window size to 500x200 pixels

tk.Label(root, text="Excel Spreadsheet Path:").pack()
excel_path_entry = tk.Entry(root)
excel_path_entry.pack()

tk.Label(root, text="Sheet Name (optional):").pack()
sheet_name_entry = tk.Entry(root)
sheet_name_entry.pack()

tk.Label(root, text="Project Name:").pack()
project_name_entry = tk.Entry(root)
project_name_entry.pack()

submit_button = tk.Button(root, text="Create Project", command=submit_form)
submit_button.pack()

status_label = tk.Label(root, text="")
status_label.pack()

progress = ttk.Progressbar(root, orient="horizontal", length=200, mode="determinate")
progress.pack()

root.bind('<Return>', submit_form)  # Bind 'Enter' key to submit_form function

root.mainloop()