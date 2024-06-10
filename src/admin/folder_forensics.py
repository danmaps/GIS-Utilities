import requests
from arcgis.gis import GIS
import xml.etree.ElementTree as ET
import pandas as pd
import os,shutil,arcpy
import subprocess

def download_item(gis_connection, item_id, filename):
    """
    Downloads an item from ArcGIS Online or Enterprise given an item ID and saves it to the specified filename.
    """
    # Obtain the token from arcpy.GetSigninToken function
    token = arcpy.GetSigninToken()['token']

    # Construct the item data URL
    item_data_url = f"{gis_connection._url}/sharing/rest/content/items/{item_id}/data?token={token}"

    # Trigger the download
    response = requests.get(item_data_url, allow_redirects=True, verify=False)
    
    if response.status_code == 200:
        # Save the content to a file
        with open(filename, 'wb') as file:
            file.write(response.content)
        print("File downloaded successfully.")
    else:
        print(f"Failed to download file: {response.status_code}, URL: {item_data_url}")

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
#         # Check if the folder title is "Red List"
#         if folder['title'] == "Red List":
        print(f"Processing folder: {folder['title']}")
        folder_items = user.items(folder=folder['id'])

        for item in folder_items:
            if item.type == "Service Definition":
                item = gis_connection.content.get(item.id)
                # Construct the filename with full path
                filename = f'{item.title}.sd'
                # Download the item
                download_item(gis_connection, item.id, filename)
                output_folder = r"extract2"

                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE  # This prevents the command window from being shown

                try:
                    subprocess.run([
                        r"C:\Program Files\7-Zip\7z.exe", 
                        'x', 
                        f'-o{output_folder}', 
                        '-aoa',  # Overwrite all existing files without prompt
                        filename
                    ], startupinfo=startupinfo, check=True)
                    print(f"Extraction successful: {filename}")
                except subprocess.CalledProcessError as e:
                    print(f"Error extracting {filename}: {e}")

                manifest_path = os.path.join(output_folder, 'manifest.xml')
                parsed_username = parse_manifest(manifest_path)
                if parsed_username is None:
                    print(f"Manifest file missing or unable to extract username for item: {item.title}")
                    continue

                # Convert the item's modified date from Unix time to a readable format
                date_created = datetime.datetime.fromtimestamp(item.created / 1000).strftime('%Y-%m-%d %H:%M:%S')

                folder_data.append({
                    'folder': folder['title'],
                    'item': item.title,
                    'parsed_username': parsed_username,
                    'date_created': date_created  # Add the modified date to the dictionary

                })
                # Cleanup downloaded and extracted files
                os.remove(filename)
                shutil.rmtree(output_folder)
                if os.path.exists(manifest_path):
                    os.remove(manifest_path)

    return folder_data

gis = GIS("home")
df = pd.DataFrame(get_folder_creators(gis, "SCE_RP_GIS"))
print(df.shape)
df.to_excel("SCE_RP_GIS_folder_summary.xlsx")
