import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from projCreator_utils import create_project

def submit_form(event=None):
    excel_path = excel_path_entry.get()
    sheet_name = sheet_name_entry.get()
    project_name = project_name_entry.get()

    try:
        create_project(excel_path, sheet_name, project_name, progress, status_label, root)
        root.destroy()  # Close the application
    except Exception as e:
        messagebox.showerror("Error", str(e))

root = tk.Tk()
root.geometry('500x200')  # Set window size to 500x200 pixels
root.configure(bg='black')  # Set background color to black

tk.Label(root, text="Excel Spreadsheet Path:", bg='black', fg='white').pack()
excel_path_entry = tk.Entry(root, bg='grey', fg='white')
excel_path_entry.pack()

tk.Label(root, text="Sheet Name (optional):", bg='black', fg='white').pack()
sheet_name_entry = tk.Entry(root, bg='grey', fg='white')
sheet_name_entry.pack()

tk.Label(root, text="Project Name:", bg='black', fg='white').pack()
project_name_entry = tk.Entry(root, bg='grey', fg='white')
project_name_entry.pack()

submit_button = tk.Button(root, text="Create Project", command=submit_form, bg='grey', fg='white')
submit_button.pack()

status_label = tk.Label(root, text="", bg='black', fg='white')
status_label.pack()

progress = ttk.Progressbar(root, orient="horizontal", length=200, mode="determinate")
progress.pack()

root.bind('<Return>', submit_form)  # Bind 'Enter' key to submit_form function

root.mainloop()