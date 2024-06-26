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

    geojson_file = "output.geojson"
    with open(geojson_file, 'w') as f:
        json.dump(geojson_data, f)

    arcpy.conversion.JSONToFeatures(geojson_file, output_layer_name, geometry_type=geometry_type)

    aprx = arcpy.mp.ArcGISProject("CURRENT")
    if aprx.activeMap:
        active_map = aprx.activeMap
        arcpy.AddMessage(os.path.join(aprx.defaultGeodatabase, output_layer_name))
        active_map.addDataFromPath(os.path.join(aprx.defaultGeodatabase, output_layer_name))

if __name__ == "__main__":
    api_key = arcpy.GetParameterAsText(0)
    query = arcpy.GetParameterAsText(1)
    output_layer_name = arcpy.GetParameterAsText(2)

    if not query:
        query = "Major California Cities"
    if not output_layer_name:
        output_layer_name = "assistant_output"

    fetch_geojson(api_key, query, output_layer_name)
