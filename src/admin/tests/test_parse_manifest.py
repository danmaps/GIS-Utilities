import zipfile
import os
import xml.etree.ElementTree as ET


def extract_manifest(sd_file_path, extract_to_folder):
    """
    Extracts the manifest.xml file from an .sd file to a specified folder.
    
    Args:
        sd_file_path (str): Path to the .sd file.
        extract_to_folder (str): Folder where manifest.xml should be extracted.
        
    Returns:
        str: The path to the extracted manifest.xml file.
    """
    manifest_file = 'manifest.xml'  # Assuming the manifest file is always named like this
    try:
        with zipfile.ZipFile(sd_file_path, 'r') as zip_ref:
            zip_ref.extract(manifest_file, path=extract_to_folder)
    except:
        import subprocess
        subprocess.run(['7z', 'x', f'-o{extract_to_folder}', sd_file_path])
    return os.path.join(extract_to_folder, manifest_file)
    
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

def test_parse_manifest():
    """
    Test the parse_manifest function with a known .sd file.
    """
    sd_file_path = 'C:\\Users\\mcveydb\\dev\\GIS-Utilities\\admin\\tests\\test.sd'
    extract_to_folder = 'C:\\Users\\mcveydb\\dev\\GIS-Utilities\\admin\\tests\\extracted'
    manifest_path = extract_manifest(sd_file_path, extract_to_folder)
    
    # Assuming parse_manifest is defined elsewhere
    extracted_username = parse_manifest(manifest_path)
    
    # Print the result for manual verification, or use assert for automated testing
    print(f"Extracted Username: {extracted_username}")
    
    # Cleanup extracted file
    os.remove(manifest_path)

# Run the test
test_parse_manifest()
