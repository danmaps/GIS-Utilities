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
import numpy as np
import torch
import supervision as sv
from groundingdino.util.inference import Model

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling

from tms2geotiff import download_extent, save_image_auto
import tempfile

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

def tms_download(bounds, zoom=17, output_path="high_res_extent.tif"):
    """
    Wrapper around tms2geotiff.download_extent to fetch a georeferenced GeoTIFF.
    
    '''
    ### **Summary of Options**
    | Provider             | Tile URL Format                                                                                     | Notes                          |
    |-----------------------|----------------------------------------------------------------------------------------------------|--------------------------------|
    | **Esri World Imagery** | `https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}` | No API key required, public.   |
    | **Google Satellite**  | `https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}`                                               | Requires API compliance.       |
    | **Bing Maps**         | `http://ecn.t3.tiles.virtualearth.net/tiles/a{q}.jpeg?g=1&key=YOUR_BING_API_KEY`                   | Free API key required.         |
    | **Sentinel Hub**      | Requires configuration with their WMS server.                                                     | Medium-resolution imagery.     |
    | **Mapbox Satellite**  | `https://api.mapbox.com/v4/mapbox.satellite/{z}/{x}/{y}.jpg90?access_token=YOUR_MAPBOX_API_KEY`    | High-quality, free tier limit. |
    '''

    Args:
        bounds: A dictionary with '_southWest' and '_northEast' keys for lat/lon.
        zoom: Tile zoom level.
        output_path: Output GeoTIFF file path.

    Returns:
        Path to the generated GeoTIFF file.
    """
    # Extract bounds
    lat0 = bounds['_southWest']['lat']
    lon0 = bounds['_southWest']['lng']
    lat1 = bounds['_northEast']['lat']
    lon1 = bounds['_northEast']['lng']

    # Generate the GeoTIFF
    st.write("Generating GeoTIFF... This may take some time.")
    try:
        image, matrix = download_extent(
            source = "https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",

            lat0=lat0, lon0=lon0, lat1=lat1, lon1=lon1,
            zoom=zoom, save_image=True
        )

        # Save the GeoTIFF temporarily or to a user-specified path
        save_image_auto(image, output_path, matrix)
        render_geotiff_with_context(output_path)
        return output_path

    except Exception as e:
        st.error(f"Error generating GeoTIFF: {e}")
        return None




def render_geotiff_with_context(output_path):
    """
    Reads and plots a GeoTIFF with geographic bounds for context using Matplotlib.

    Args:
        output_path: Path to the GeoTIFF file.
    """
    try:
        # Step 1: Open the GeoTIFF and read metadata
        with rasterio.open(output_path) as src:
            img_data = src.read(1)  # Read first band
            bounds = src.bounds  # Get geographic bounds

            # Extract bounds for plotting context
            left, bottom, right, top = bounds

            # Step 2: Plot the GeoTIFF with Matplotlib
            fig, ax = plt.subplots(figsize=(8, 6))
            plt.imshow(img_data, cmap="gray", extent=[left, right, bottom, top])

            # Add geographic bounds as a rectangle
            rect = patches.Rectangle(
                (left, bottom), right - left, top - bottom,
                linewidth=2, edgecolor="red", facecolor="none", label="GeoTIFF Bounds"
            )
            ax.add_patch(rect)

            # Add context grid and labels
            ax.set_title("Rendered GeoTIFF with Geographic Bounds")
            ax.set_xlabel("Longitude")
            ax.set_ylabel("Latitude")
            plt.grid(visible=True)

            # Step 3: Render the plot in Streamlit
            st.pyplot(fig)

    except Exception as e:
        st.error(f"Error rendering GeoTIFF: {e}")

def reproject_and_render_geotiff(output_path, target_crs="EPSG:4326"):
    """
    Reproject a GeoTIFF to EPSG:4326 and render it with Matplotlib.

    Args:
        output_path: Path to the original GeoTIFF file.
        target_crs: Target CRS (default: EPSG:4326).
    """
    reprojected_path = output_path.replace(".tif", "_4326.tif")
    
    try:
        # Step 1: Reproject the GeoTIFF
        with rasterio.open(output_path) as src:
            transform, width, height = calculate_default_transform(
                src.crs, target_crs, src.width, src.height, *src.bounds
            )
            kwargs = src.meta.copy()
            kwargs.update({
                'crs': target_crs,
                'transform': transform,
                'width': width,
                'height': height
            })

            with rasterio.open(reprojected_path, 'w', **kwargs) as dst:
                for i in range(1, src.count + 1):
                    reproject(
                        source=rasterio.band(src, i),
                        destination=rasterio.band(dst, i),
                        src_transform=src.transform,
                        src_crs=src.crs,
                        dst_transform=transform,
                        dst_crs=target_crs,
                        resampling=Resampling.nearest
                    )
        
        # Step 2: Plot the reprojected GeoTIFF
        with rasterio.open(reprojected_path) as src:
            img_data = src.read(1)  # Read first band
            bounds = src.bounds  # Get geographic bounds

            # Plot the GeoTIFF
            fig, ax = plt.subplots(figsize=(8, 6))
            plt.imshow(img_data, cmap="gray", extent=[bounds.left, bounds.right, bounds.bottom, bounds.top])
            rect = patches.Rectangle(
                (bounds.left, bounds.bottom),
                bounds.right - bounds.left,
                bounds.top - bounds.bottom,
                linewidth=2, edgecolor="red", facecolor="none", label="Reprojected Bounds"
            )
            ax.add_patch(rect)

            # Add context
            ax.set_title("Reprojected GeoTIFF (EPSG:4326)")
            ax.set_xlabel("Longitude")
            ax.set_ylabel("Latitude")
            plt.grid(visible=True)

            # Render in Streamlit
            st.pyplot(fig)

    except Exception as e:
        st.error(f"Error reprojecting and rendering GeoTIFF: {e}")

def verify_geotiff(file_path):
    """Verify that a GeoTIFF file has proper georeferencing."""
    try:
        with rasterio.open(file_path) as src:
            if src.crs is None:
                return False, "No coordinate reference system found"
            if src.transform == rasterio.transform.IDENTITY:
                return False, "No geotransform found"
            return True, f"Valid GeoTIFF with CRS: {src.crs}, Transform: {src.transform}"
    except Exception as e:
        return False, f"Error reading GeoTIFF: {str(e)}"

# streamlit app ui

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

# Download GeoTIFF using tms2geotiff
if st.button("Download GeoTIFF"):
    if bounds:
        # Create a temporary file for the GeoTIFF
        with tempfile.NamedTemporaryFile(suffix=".tif", delete=False) as temp_file:
            output_path = temp_file.name
        
        # Call the wrapper function
        tms_geotiff_path = tms_download(bounds, zoom=17, output_path=output_path)
        
        # Update the Streamlit session state
        if tms_geotiff_path:
            st.session_state.geotiff_path = tms_geotiff_path
            # Verify georeferencing
            is_valid, message = verify_geotiff(tms_geotiff_path)
            if is_valid:
                st.success(f"GeoTIFF downloaded and properly georeferenced: {message}")
            else:
                st.warning(f"GeoTIFF downloaded but georeferencing issue detected: {message}")
            
            file_size = os.path.getsize(tms_geotiff_path) / (1024 * 1024)
            st.write(f"GeoTIFF size: {file_size:.2f} MB")
        else:
            st.error("Failed to download GeoTIFF.")
    else:
        st.warning("Please specify a valid map area of interest.")

if st.button("Reproject and Show GeoTIFF"):
    if bounds:
        output_path = "high_res_extent.tif"
        tms_geotiff_path = tms_download(bounds, zoom=17, output_path=output_path)

        if tms_geotiff_path:
            st.success("GeoTIFF downloaded successfully!")
            reproject_and_render_geotiff(tms_geotiff_path)
        else:
            st.error("Failed to download GeoTIFF.")
    else:
        st.warning("Please specify a valid map area of interest.")

        
# Run Detection on Button Click
if st.button("Run Detection"):
    if st.session_state.geotiff_path:
        st.write("Running detection...")
        
        # Add text prompt input
        text_prompt = st.text_input("Enter detection prompt:", 
                                  value="wooden utility pole or power pole or telephone pole",
                                  help="Describe what you want to detect")
        
        confidence_threshold = st.slider("Confidence Threshold", 
                                      min_value=0.0, 
                                      max_value=1.0, 
                                      value=0.35)
        
        # Process the saved GeoTIFF path
        temp_image_path = st.session_state.geotiff_path
        
        # Run detection with text prompt
        detections = detect_with_prompt(
            temp_image_path, 
            text_prompt=text_prompt,
            box_threshold=confidence_threshold
        )
        
        if len(detections) > 0:
            st.write(f"Detected {len(detections)} objects matching '{text_prompt}'")
            
            # Draw detections
            result_img = draw_detections(temp_image_path, detections)
            st.image(result_img, caption=f"Detected {text_prompt}", use_container_width=True)
        else:
            st.warning(f"No objects matching '{text_prompt}' were detected. Try adjusting the confidence threshold or modifying the prompt.")
    else:
        st.warning("No GeoTIFF found. Please download it first.")

@st.cache_resource
def load_grounding_dino():
    model = Model(model_config_path="GroundingDINO/groundingdino/config/GroundingDINO_SwinT_OGC.py",
                 model_checkpoint_path="groundingdino_swint_ogc.pth")
    return model

# Function to detect objects with text prompt
def detect_with_prompt(image_path, text_prompt="wooden utility pole", box_threshold=0.35, text_threshold=0.25):
    model = load_grounding_dino()
    
    # Read image
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Detect objects
    detections = model.predict_with_classes(
        image=image,
        classes=[text_prompt],
        box_threshold=box_threshold,
        text_threshold=text_threshold
    )
    
    return detections

def draw_detections(image_path, detections):
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Create annotator
    box_annotator = sv.BoxAnnotator()
    
    # Prepare labels
    labels = [f"{detection.class_id}: {detection.confidence:.2f}" 
              for detection in detections]
    
    # Draw boxes
    annotated_image = box_annotator.annotate(
        scene=image, 
        detections=detections,
        labels=labels
    )
    
    return annotated_image

