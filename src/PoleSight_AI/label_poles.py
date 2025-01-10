import streamlit as st
import folium
from streamlit_folium import st_folium
import json
import uuid
from datetime import datetime
import os

# Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "labels" not in st.session_state:
    st.session_state.labels = []
if "last_clicked" not in st.session_state:
    st.session_state.last_clicked = None

# Page config
st.set_page_config(page_title="Pole Labeling Tool", layout="wide")

# Title and instructions
st.title("🎯 Pole Labeling Tool")
with st.expander("Instructions", expanded=True):
    st.markdown("""
    1. Pan and zoom to find utility poles in the satellite imagery
    2. Click directly on poles to add labels
    3. Use the confidence selector for each label
    4. Save your work when done
    
    **Keyboard Shortcuts:**
    - `Z`: Undo last label
    - `S`: Save current labels
    """)

# Main interface
col1, col2 = st.columns([7, 3])

with col1:
    # Initialize the map
    m = folium.Map(
        location=[34.4265, -117.428113],
        zoom_start=17,
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr='Esri'
    )

    # Add click event handling through Streamlit
    map_data = st_folium(
        m,
        width=None,
        height=600,
        returned_objects=["last_clicked"]
    )

    # Handle new clicks
    if (map_data 
        and "last_clicked" in map_data 
        and map_data["last_clicked"] 
        and map_data["last_clicked"] != st.session_state.last_clicked):
        
        new_label = {
            "id": len(st.session_state.labels) + 1,
            "lat": map_data["last_clicked"]["lat"],
            "lng": map_data["last_clicked"]["lng"],
            "confidence": "high",  # default value
            "timestamp": datetime.now().isoformat()
        }
        st.session_state.labels.append(new_label)
        st.session_state.last_clicked = map_data["last_clicked"]

with col2:
    # Labels panel
    st.subheader(f"Labels ({len(st.session_state.labels)})")
    
    # Display and edit labels
    for i, label in enumerate(st.session_state.labels):
        with st.container():
            st.markdown(f"**Pole #{label['id']}**")
            cols = st.columns([3, 1])
            with cols[0]:
                st.text(f"Lat: {label['lat']:.6f}")
                st.text(f"Lng: {label['lng']:.6f}")
            with cols[1]:
                confidence = st.selectbox(
                    "Confidence",
                    ["high", "medium", "low"],
                    index=["high", "medium", "low"].index(label["confidence"]),
                    key=f"conf_{i}"
                )
                label["confidence"] = confidence
            st.divider()

    # Action buttons
    if st.button("Undo Last Label", type="secondary") and st.session_state.labels:
        st.session_state.labels.pop()
        st.rerun()

    if st.button("Save Labels", type="primary"):
        # Prepare data for saving
        data = {
            "session_id": st.session_state.session_id,
            "date": datetime.now().isoformat(),
            "region": {
                "bounds": map_data.get("bounds", None),
                "zoom": map_data.get("zoom", None)
            },
            "labels": st.session_state.labels
        }
        
        # Create directory if it doesn't exist
        os.makedirs("labels", exist_ok=True)
        
        # Save to file
        filename = f"labels/session_{st.session_state.session_id}.json"
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        
        st.success(f"Labels saved to {filename}")

    if st.button("Clear All Labels", type="secondary"):
        st.session_state.labels = []
        st.rerun()

# Display statistics
st.sidebar.markdown("### Session Statistics")
st.sidebar.metric("Total Labels", len(st.session_state.labels))
if st.session_state.labels:
    st.sidebar.metric("Last Label Added", 
                     f"Pole #{st.session_state.labels[-1]['id']}") 