# todo:
#   add dynamic assistant creation step
#   record a compelling demo

# potential features:
#   conversation context (create a point, ok thanks, now buffer that)
#   
#   add context
#       layers from active map
#       properties like on/off, extent, geometry type, feature count, symbology, fields
#       map properties, like extent
#       current view as a png
#       
#   give the AI abilities
#       turn layers on/off
#       make selections
#       pan/zoom, zoom to layer, zoom to selection
#       use geoprocessing tools (with code interpreter?)
#
#   sounds like a mixture of assistants
#       so far i've just got a simple blind feature layer creator
#       if i give it vision and some friends to talk to it'll have a better time
#   
#   attaching data
#       instead of winging it, use authoritative references to existing geometry
#       need to clarify if we are talking about reproducing geometry or using it for inspiration
#
#   "watch" the user operate editing tools and then draw on the map in a similar way
#       continue drawing
#       like a copilot for editing GIS data
#       need something like github copilot tab complete, where the suggestions are shown to the user and approved/dismissed
#       record a macro, start drawing, the information about the drawing and how it related to existing geometry is saved
#       this information is used by the AI as a "style guide" for continued drawing, which it does
#
#   enrich existing data with ai
#       add a column to an existing table with the result of the ai prompt
#       like existing excel/google sheets plugins
#       must be able to refer to existing columns in the dataset by name
#       compelling demo idea: 1. all 50 us state capitals 2. a fun fact about this city

import requests
import time
import arcpy
import json
import os

def create_thread(api_key):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "OpenAI-Beta": "assistants=v2"
    }
    for _ in range(3):
        try:
            response = requests.post("https://api.openai.com/v1/threads", headers=headers, json={}, verify=False)
            response.raise_for_status()
            return response.json()["id"]
        except requests.exceptions.RequestException as e:
            arcpy.AddWarning(f"Retrying thread creation due to: {e}")
            time.sleep(1)
    raise Exception(f"Failed to create thread after retries")

def submit_message(api_key, thread_id, user_message):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "OpenAI-Beta": "assistants=v2"
    }

    message_payload = {
        "role": "user",
        "content": user_message
    }
    
    for _ in range(3):
        try:
            response = requests.post(f"https://api.openai.com/v1/threads/{thread_id}/messages", headers=headers, json=message_payload, verify=False)
            response.raise_for_status()
            run_payload = {"assistant_id": "asst_AEeH9H8dWTl1DGszMInYIhqu"}
            run_response = requests.post(f"https://api.openai.com/v1/threads/{thread_id}/runs", headers=headers, json=run_payload, verify=False)
            run_response.raise_for_status()
            return run_response.json()["id"]
        except requests.exceptions.RequestException as e:
            arcpy.AddWarning(f"Retrying message submission due to: {e}")
            time.sleep(1)
    raise Exception(f"Failed to send message and initiate run after retries")

def wait_on_run(api_key, thread_id, run_id):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "OpenAI-Beta": "assistants=v2"
    }
    
    run_status_url = f"https://api.openai.com/v1/threads/{thread_id}/runs/{run_id}"
    
    while True:
        try:
            response = requests.get(run_status_url, headers=headers, verify=False)
            response.raise_for_status()
            if not response.content:
                raise Exception("Empty response received while checking run status.")
            run_status = response.json()
            status = run_status.get("status")
            if status == "completed":
                return run_status
            elif status in ["queued", "in_progress"]:
                time.sleep(0.5)
            else:
                raise Exception(f"Run failed with status: {status}")
        except requests.exceptions.RequestException as e:
            arcpy.AddWarning(f"Retrying run status check due to: {e}")
            time.sleep(1)

def get_response(api_key, thread_id):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "OpenAI-Beta": "assistants=v2"
    }

    for _ in range(3):
        try:
            response = requests.get(f"https://api.openai.com/v1/threads/{thread_id}/messages", headers=headers, verify=False)
            response.raise_for_status()
            if not response.content:
                raise Exception("Empty response received while retrieving messages.")
            messages = response.json()
            content = [msg['content'][0]['text']['value'] for msg in messages.get('data', []) if msg['role'] == 'assistant']
            return content
        except requests.exceptions.RequestException as e:
            arcpy.AddWarning(f"Retrying message retrieval due to: {e}")
            time.sleep(1)
    raise Exception(f"Failed to get messages after retries")

def infer_geometry_type(geojson_data):
    geometry_type_map = {
        "Point": "Point",
        "MultiPoint": "Multipoint",
        "LineString": "Polyline",
        "MultiLineString": "Polyline",
        "Polygon": "Polygon",
        "MultiPolygon": "Polygon"
    }

    geometry_types = set()
    for feature in geojson_data["features"]:
        geometry_type = feature["geometry"]["type"]
        arcpy.AddMessage(f"found {geometry_type}")
        geometry_types.add(geometry_type_map.get(geometry_type))

    if len(geometry_types) == 1:
        return geometry_types.pop()
    else:
        raise ValueError("Multiple geometry types found in GeoJSON")

def fetch_geojson(api_key, query, output_layer_name):
    try:
        thread_id = create_thread(api_key)
        run_id = submit_message(api_key, thread_id, query)
        run_status = wait_on_run(api_key, thread_id, run_id)
        geojson_data = get_response(api_key, thread_id)

        # Add debugging to inspect the raw GeoJSON response
        arcpy.AddMessage(f"Raw GeoJSON data: {geojson_data[0]}")

        geojson_data = json.loads(geojson_data[0])  # Assuming single response for simplicity
        geometry_type = infer_geometry_type(geojson_data)
    except Exception as e:
        arcpy.AddError(str(e))
        return

    geojson_file = os.path.join("geojson_output",f"{output_layer_name}.geojson")
    with open(geojson_file, 'w') as f:
        json.dump(geojson_data, f)

    arcpy.conversion.JSONToFeatures(geojson_file, output_layer_name, geometry_type=geometry_type)

    aprx = arcpy.mp.ArcGISProject("CURRENT")
    if aprx.activeMap:
        active_map = aprx.activeMap
        output_layer_path = os.path.join(aprx.defaultGeodatabase, output_layer_name)
        arcpy.AddMessage(f"Adding layer from: {output_layer_path}")
        
        try:
            active_map.addDataFromPath(output_layer_path)
            layer = active_map.listLayers(output_layer_name)[0]
            
            # Get the active view
            active_view = aprx.activeView
            
            #if isinstance(active_view, arcpy.mp.MapView):
            # Get the extent using getLayerExtent
            extent = active_view.getLayerExtent(layer)
            if extent:
                active_view.camera.setExtent(extent)
                arcpy.AddMessage(f"Layer '{output_layer_name}' added and extent set successfully.")
            else:
                arcpy.AddWarning(f"Unable to get extent for layer '{output_layer_name}'.")

        except Exception as e:
            arcpy.AddError(f"Error processing layer: {str(e)}")
    else:
        arcpy.AddWarning("No active map found in the current project.")
        
if __name__ == "__main__":
    api_key = arcpy.GetParameterAsText(0)
    query = arcpy.GetParameterAsText(1)
    output_layer_name = arcpy.GetParameterAsText(2)

    if not query:
        query = "Major California Cities"
    if not output_layer_name:
        output_layer_name = "assistant_output"

    fetch_geojson(api_key, query, output_layer_name)
