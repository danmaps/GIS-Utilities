from arcgis.gis import GIS, Item
import zipfile
import xml.etree.ElementTree as ET
import pandas as pd
def parse_manifest(manifest_path):
    """
    Parses an ArcGIS Service Definition manifest.xml file to extract the Windows username.

    Args:
        manifest_path (str): Path to the manifest.xml file.

    Returns:
        str: The extracted Windows username, or None if not found.
    """

    tree = ET.parse(manifest_path)
    root = tree.getroot()
    for path_tag in root.iter('OnPremisePath'):
        user_path = path_tag.text
        if user_path.startswith('C:\\Users\\'):
            return user_path.split('\\')[2]  # Extract username
    return None  # Return None if username not found

'''
# Example usage for testing:
test_manifest_file = "path/to/your/test/manifest.xml"
username = parse_manifest(test_manifest_file)
if username:
    print(f"Found username: {username}")
else:
    print("Username not found in manifest.xml")
'''

def get_folder_creators(gis_connection, username):
    user = gis_connection.users.get(username)
    folders = user.folders

    folder_data = []  # Store folder information

    for folder in folders:
        print(f"Processing folder: {folder['title']}")
        items = folder.items('Service Definition')

        for item in items:
            data = item.get_data()
            filename = item.title + '.zip'  # Construct filename
            with open(filename, 'wb') as f:
                f.write(data)

            with zipfile.ZipFile(filename, 'r') as zip_ref:
                zip_ref.extractall()

            # Parse manifest.xml
            tree = ET.parse('manifest.xml')
            root = tree.getroot()
            for path_tag in root.iter('OnPremisePath'):
                user_path = path_tag.text
                if user_path.startswith('C:\\Users\\'):
                    username = user_path.split('\\')[2]
                    break

            folder_data.append({
                'folder': folder['title'],
                'item': item.title,
                'username': username
            })

    return folder_data

if __name__ == "__main__":
    gis = GIS("https://your-org.maps.arcgis.com/", "SCE_RP_GIS", "password")
    results = get_folder_creators(gis, "SCE_RP_GIS")

    df = pd.DataFrame(results) 
    df.to_excel("folder_summary.xlsx")
