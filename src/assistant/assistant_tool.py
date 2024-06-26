import arcpy
import json
import requests

def fetch_geojson(api_key, assistant_id, query, output_layer_name):
    arcpy.AddMessage((assistant_id, query))
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "OpenAI-Beta": "assistants=v2"
    }

    # Create thread
    thread_payload = {
        "assistant_id": assistant_id
    }
    thread_response = requests.post("https://api.openai.com/v1/threads", headers=headers, json=thread_payload)
    if thread_response.status_code != 200:
        arcpy.AddError(f"Failed to create thread: {thread_response.text}")
        return
    
    thread_id = thread_response.json()["id"]

    # Send query
    message_payload = {
        "messages": [
            {
                "role": "user",
                "content": query
            }
        ]
    }
    message_response = requests.post(f"https://api.openai.com/v1/threads/{thread_id}/messages", headers=headers, json=message_payload, verify=False)
    if message_response.status_code != 200:
        arcpy.AddError(f"Failed to send message: {message_response.text}")
        return
    
    geojson_data = message_response.json()

    # Save GeoJSON to a file
    geojson_file = arcpy.env.scratchFolder + "/output.geojson"
    with open(geojson_file, 'w') as f:
        json.dump(geojson_data, f)

    # Convert GeoJSON to Feature Class
    arcpy.conversion.JSONToFeatures(geojson_file, output_layer_name)

if __name__ == "__main__":
    # Get parameters
    api_key = arcpy.GetParameterAsText(0)
    assistant_id = "asst_AEeH9H8dWTl1DGszMInYIhqu"
    query = arcpy.GetParameterAsText(1)
    output_layer_name = arcpy.GetParameterAsText(2)

    # Set default values if parameters are empty
    if not query:
        query = "Major California Cities"
    if not output_layer_name:
        output_layer_name = "assistant_output"

    # Run the function
    fetch_geojson(api_key, assistant_id, query, output_layer_name)
