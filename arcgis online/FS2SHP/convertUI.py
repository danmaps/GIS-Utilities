import tkinter as tk
from arcgis.gis import GIS

def convert_feature_service():
    username = username_entry.get()
    password = password_entry.get()
    feature_service_url = feature_service_entry.get()
    output_directory = output_directory_entry.get()
    
    gis = GIS("https://www.arcgis.com", username, password)
    feature_layer = gis.content.get(feature_service_url).layers[0]
    
    query = "1=1"  # Adjust the query as needed
    features = feature_layer.query(where=query).features
    
    # Rest of the conversion process using ArcGIS Python API

# Tkinter UI
root = tk.Tk()
root.title("Feature Service to Shapefile Converter")

username_label = tk.Label(root, text="Username:")
username_label.pack()
username_entry = tk.Entry(root)
username_entry.pack()

password_label = tk.Label(root, text="Password:")
password_label.pack()
password_entry = tk.Entry(root, show="*")
password_entry.pack()

feature_service_label = tk.Label(root, text="Feature Service URL:")
feature_service_label.pack()
feature_service_entry = tk.Entry(root)
feature_service_entry.pack()

output_directory_label = tk.Label(root, text="Output Directory:")
output_directory_label.pack()
output_directory_entry = tk.Entry(root)
output_directory_entry.pack()

convert_button = tk.Button(root, text="Convert", command=convert_feature_service)
convert_button.pack()

root.mainloop()
