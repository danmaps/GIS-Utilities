from ipywidgets import Button, Dropdown, VBox, Textarea, Layout, Text
from arcgis.gis import GIS
from datetime import datetime
from IPython.display import display

# Connect to GIS
gis = GIS("home")

# Initialize widgets
search_input = Text(placeholder='Enter search string')
search_button = Button(description='Search Notebooks')
dropdown = Dropdown(options=[('Select a notebook', None)], value=None)
download_button = Button(description='Download Notebook')
message_textarea = Textarea(value='', disabled=True, layout=Layout(width='100%'))

# Function to clear and reset UI elements
def clear_ui():
    dropdown.options = [('Select a notebook', None)]
    dropdown.value = None
    message_textarea.value = ""

# Search function
def search_notebooks(b):
    clear_ui()  # Clear UI elements
    search_string = search_input.value.strip()
    if search_string:  # Proceed only if the search string is not empty
        query = f'type:"Notebook" AND title:{search_string}'
        notebooks = gis.content.search(query=query, item_type="Notebook")

        if notebooks:
            dropdown.options = [(notebook.title, notebook) for notebook in notebooks]
        else:
            message_textarea.value = "No notebooks found."
    else:
        message_textarea.value = "Please enter a search string."

# Download function
def download_notebook(b):
    selected_notebook = dropdown.value
    if selected_notebook:
        current_time = datetime.now().strftime('%Y%m%d%H%M%S')
        unique_filename = f"{selected_notebook.title}_{current_time}.ipynb"
        
        try:
            save_path = f"./{unique_filename}"
            selected_notebook.download(save_path=save_path)
            message_textarea.value = f"Successfully downloaded as '{unique_filename}'\n"
            clear_ui()  # Optionally clear UI elements after download
            search_input.value = ''  # Clear search input to ready for new search
        except Exception as e:
            message_textarea.value = f"Error downloading '{selected_notebook.title}': {str(e)}"

# Event handlers
search_button.on_click(search_notebooks)
download_button.on_click(download_notebook)

# Organize widgets in VBox
vbox = VBox([search_input, search_button, dropdown, download_button, message_textarea])

# Display the VBox
display(vbox)
