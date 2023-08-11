from arcgis.gis import GIS

# Authenticate with ArcGIS Online
gis = GIS("https://www.arcgis.com", "your_username", "your_password")

# Access the Feature Service
feature_service_url = "https://services.arcgis.com/your_feature_service_url"
feature_layer = gis.content.get(feature_service_url).layers[0]

# Retrieve Data
query = "1=1"  # Adjust the query to filter the data if needed
features = feature_layer.query(where=query).features

# Prepare Data for Shapefile
output_shapefile_path = r"C:\path\to\output\directory"
output_shapefile_name = "output_shapefile"

# Create a shapefile folder
output_shapefile_folder = output_shapefile_path + "\\" + output_shapefile_name
output_shapefile_folder_item = gis.content.create_folder(output_shapefile_name)

# Iterate through features and create shapefile items
for feature in features:
    feature_attributes = feature.attributes
    shapefile_item = output_shapefile_folder_item.content.create_folder(feature_attributes["OBJECTID"])
    shapefile_item.layers.create_from_features([feature])

# Print a success message
print("Shapefile creation completed.")

# Note: Make sure to replace placeholders (e.g., URLs, paths, fields) with actual values.
