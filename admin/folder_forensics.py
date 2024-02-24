from arcgis.gis import GIS
gis = GIS("home")

import zipfile
import xml.etree.ElementTree as ET
import pandas as pd
import getpass
import os
import subprocess

def parse_manifest(manifest_path):
    """
    Parses an ArcGIS Service Definition manifest.xml file to extract the Windows username.
    """
    if not os.path.exists(manifest_path):
        return None  # File doesn't exist
    try:
        tree = ET.parse(manifest_path)
        root = tree.getroot()
        for path_tag in root.iter('OnPremisePath'):
            user_path = path_tag.text
            if user_path and user_path.startswith('C:\\Users\\'):
                return user_path.split('\\')[2]  # Extract username
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
    return None

def get_folder_creators(gis_connection, user_name):
    user = gis_connection.users.get(user_name)
    folders = user.folders
    folder_data = []  # Store folder information
    
    for folder in folders:
        # Check if the folder title is "Red List"
        if folder['title'] == "Red List":
            print(f"Processing folder: {folder['title']}")
            folder_items = user.items(folder=folder['id'])
            
            for item in folder_items:
                if item.type == "Service Definition":
                    # Use the download method to save the file
                    filename = item.download(save_path=r'C:\Users\mcveydb\AppData\Local\Temp\ArcGISProTemp3044\Untitled', file_name=item.title + '.sd')
                    output_folder = r"C:\Users\mcveydb\AppData\Local\Temp\ArcGISProTemp3044\Untitled\extract"
                    archive_path = filename
                    print(archive_path)
                    try:
                        subprocess.run([r"C:\Program Files\7-Zip\7z.exe", 'x', f'-o{output_folder}', archive_path], check=True)
                        print(f"Extraction successful: {archive_path}")
                    except subprocess.CalledProcessError as e:
                        print(f"Error extracting {archive_path}: {e}")

                    manifest_path = 'manifest.xml'
                    parsed_username = parse_manifest(manifest_path)
                    if parsed_username is None:
                        print(f"Manifest file missing or unable to extract username for item: {item.title}")
                        continue  # Skip to the next item

                    folder_data.append({
                        'folder': folder['title'],
                        'item': item.title,
                        'parsed_username': parsed_username
                    })
                    # Clean up downloaded and extracted files
                    os.remove(filename)
                    if os.path.exists(manifest_path):
                        os.remove(manifest_path)
    return folder_data


# password = getpass.getpass("Enter your password: ")
# gis = GIS("https://your-organization-url.arcgis.com/", "your_username", password)

df = pd.DataFrame(get_folder_creators(gis, "SCE_RP_GIS"))
print(df.shape)
df.to_excel("folder_summary.xlsx")
