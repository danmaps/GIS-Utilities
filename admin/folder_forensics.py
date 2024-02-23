from arcgis.gis import GIS
import zipfile
import xml.etree.ElementTree as ET
import pandas as pd
import getpass
import os

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
        print(f"Processing folder: {folder['title']}")
        items = user.items(folder=folder['title'], item_type='Service Definition')
        for item in items:
            try:
                data = item.get_data()
                filename = item.title + '.zip'  # Construct filename
                with open(filename, 'wb') as f:
                    f.write(data)
                with zipfile.ZipFile(filename, 'r') as zip_ref:
                    zip_ref.extractall()
            except Exception as e:
                print(f"Error processing item {item.title}: {e}")
                continue  # Skip to the next item

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

password = getpass.getpass("Enter your password: ")
gis = GIS("https://your-organization-url.arcgis.com/", "your_username", password)

df = pd.DataFrame(get_folder_creators(gis, "your_username"))
df.to_excel("folder_summary.xlsx")
