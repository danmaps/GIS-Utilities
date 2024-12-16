import streamlit as st
import folium
from streamlit_folium import st_folium

st.title("Pole Detection Tool")
st.write("Drag the map to specify the area of interest and click 'Run Detection'.")

map_center = [34.4265, -117.428113 ] # Example coordinates

# Create a map object with no initial tiles
m = folium.Map(location=map_center, zoom_start=19, tiles="")

# Add a tile layer for satellite imagery
tile_layer = folium.TileLayer(
    tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attr='Esri',
    name='Esri Satellite',
    overlay=False,
    control=True
).add_to(m)

# Streamlit Folium integration
st_data = st_folium(m, width=700, height=500)

# Retrieve map bounds for ROI
bounds = st_data['bounds'] if st_data else None
if st.button("Run Detection"):
    st.write("Running model...")
