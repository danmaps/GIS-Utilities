import streamlit as st
import folium
from streamlit_folium import st_folium
from PIL import Image
import torch
from torchvision.models.detection import fasterrcnn_resnet50_fpn, FasterRCNN_ResNet50_FPN_Weights
from torchvision.transforms import ToTensor
import cv2
import requests
from osgeo import gdal
import warnings
import os
from owslib.wms import WebMapService
import rasterio
from datetime import datetime

# Enable GDAL exceptions
gdal.UseExceptions()

# Suppress non-critical warnings (optional)
warnings.filterwarnings("ignore")

# Load the pretrained model
@st.cache_resource
def load_model():
    # Load the model with updated syntax
    weights = FasterRCNN_ResNet50_FPN_Weights.COCO_V1
    model = fasterrcnn_resnet50_fpn(weights=weights)
    model.eval()
    return model

model = load_model()

# Function to detect poles
def detect_poles(image_path, confidence_threshold=0.8):
    image = Image.open(image_path).convert("RGB")
    transform = ToTensor()
    img_tensor = transform(image).unsqueeze(0)

    with torch.no_grad():
        predictions = model(img_tensor)

    # Filter predictions by confidence
    high_conf_poles = [
        box.numpy() for box, score in zip(predictions[0]['boxes'], predictions[0]['scores'])
        if score > confidence_threshold
    ]
    return high_conf_poles

# Function to draw bounding boxes on an image
def draw_bounding_boxes(image_path, boxes):
    img = cv2.imread(image_path)
    for box in boxes:
        x1, y1, x2, y2 = map(int, box)
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
    return img

def download_geotiff(bounds, output_path="extent.tif"):
    # NASA Global Imagery Browse Services WMS
    wms_url = "https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi"

    # st.write(f"Downloading GeoTIFF for bounds: {bounds}")
    params = {
        "SERVICE": "WMS",
        "VERSION": "1.1.1",
        "REQUEST": "GetMap",
        "LAYERS": "NASA_GIBS_EPSG4326_best",
        "STYLES": "",
        "BBOX": f"{bounds['_southWest']['lat']},{bounds['_southWest']['lng']},{bounds['_northEast']['lat']},{bounds['_northEast']['lng']}",
        "SRS": "EPSG:4326",
        "WIDTH": "1024",
        "HEIGHT": "1024",
        "FORMAT": "image/tiff",
        "TIME": "2021-03-21" # Use a valid time within the layer's range
    }

    # Download image
    response = requests.get(wms_url, params=params, stream=True)
    st.write(f"response: {response.status_code}")
    if response.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(response.content)
        
        return output_path
    else:
        st.error(f"Failed to download GeoTIFF. Server response: {response.status_code}")
        return None
    
def download_geotiff_with_owslib(bounds, output_path="extent.tif", time="2021-03-21"):
    try:
        # Connect to NASA GIBS WMS
        wms = WebMapService('https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi?', version='1.3.0')

        # Request GeoTIFF
        img = wms.getmap(
            layers=['MODIS_Terra_SurfaceReflectance_Bands143'],
            srs='epsg:4326',
            bbox=(bounds['_southWest']['lng'], bounds['_southWest']['lat'],
                  bounds['_northEast']['lng'], bounds['_northEast']['lat']),
            size=(1024, 512),
            time=time,
            format='image/tiff',
            transparent=True
        )

        # Save the GeoTIFF
        with open(output_path, 'wb') as f:
            f.write(img.read())

        st.success("GeoTIFF successfully downloaded.")

        # Inspect the file
        with rasterio.open(output_path) as src:
            st.write(f"Width: {src.width}, Height: {src.height}")
            st.write(f"CRS: {src.crs}")
            st.write(f"Bands: {src.count}")
        return output_path

    except Exception as e:
        st.error(f"Error downloading GeoTIFF: {e}")
        return None

import requests

def download_esri_geotiff(bounds, size=(2048, 2048), output_path="high_res_extent.tif"):
    export_url = "https://server.arcgisonline.com/arcgis/rest/services/World_Imagery/MapServer/export"
    params = {
        "bbox": f"{bounds['_southWest']['lng']},{bounds['_southWest']['lat']},"
                f"{bounds['_northEast']['lng']},{bounds['_northEast']['lat']}",
        "bboxSR": "4326",       # Input coordinate system (WGS84 lat/lon)
        "imageSR": "3857",      # Output coordinate system (Web Mercator)
        "size": f"{size[0]},{size[1]}",
        "format": "tiff",       # GeoTIFF format
        "f": "image",
        "adjustAspectRatio": "true"  # Adjust the image to match the real-world extents
    }

    response = requests.get(export_url, params=params, stream=True)
    if response.status_code == 200:
        with open(output_path, "wb") as file:
            file.write(response.content)
        return output_path
    else:
        raise Exception(f"Failed to download GeoTIFF. Status: {response.status_code}")

# Trigger GeoTIFF download and display

st.title("Pole Detection")

map_center = [34.4265, -117.428113 ] # Example coordinates

# Create a map object with no initial tiles
m = folium.Map(location=map_center, zoom_start=17, tiles="")

# Add a tile layer for satellite imagery
tile_layer = folium.TileLayer(
    tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attr='Esri',
    name='Esri Satellite',
    overlay=False,
    control=True
).add_to(m)

# Retrieve map bounds for ROI
st_data = st_folium(m, width=700, height=500)

bounds = st_data['bounds'] if st_data else None

# Display Current Bounds Dynamically
if st_data and "bounds" in st_data:
    bounds = st_data["bounds"]
    st.write("### Current Map Bounds:")
    st.write(f"**Southwest:** ({bounds['_southWest']['lat']}, {bounds['_southWest']['lng']})")
    st.write(f"**Northeast:** ({bounds['_northEast']['lat']}, {bounds['_northEast']['lng']})")
else:
    st.write("Map bounds will appear here once the map is moved or zoomed.")

# Initialize session state for GeoTIFF path
if "geotiff_path" not in st.session_state:
    st.session_state.geotiff_path = None

# Step 1: Download GeoTIFF
if st.button("Download GeoTIFF"):
    if st_data and "bounds" in st_data:
        st.write("Downloading GeoTIFF for the current extent...")
        bounds = st_data["bounds"]
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        geotiff_path = download_esri_geotiff(bounds, output_path=f"high_res_extent_{timestamp}.tif")
        
        if geotiff_path:
            st.session_state.geotiff_path = geotiff_path  # Save path in session state
            st.success(f"GeoTIFF downloaded: {geotiff_path}")
            file_size = os.path.getsize(geotiff_path) / (1024 * 1024)
            st.write(f"GeoTIFF size: {file_size:.2f} MB")
        else:
            st.error("Failed to download GeoTIFF.")
    else:
        st.warning("Please drag the map to specify an area of interest.")

# Run Detection on Button Click
if st.button("Run Detection"):
    if st.session_state.geotiff_path:
        st.write("Running detection...")
        
        # Process the saved GeoTIFF path
        temp_image_path = st.session_state.geotiff_path
        
        # Run detection
        poles = detect_poles(temp_image_path)
        st.write(f"Detected {len(poles)} poles.")

        # Draw bounding boxes
        result_img = draw_bounding_boxes(temp_image_path, poles)
        st.image(result_img, caption="Detected Poles", use_container_width=True)
    else:
        st.warning("No GeoTIFF found. Please download it first.")