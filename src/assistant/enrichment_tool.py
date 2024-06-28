
#   enrich existing data with ai
#       add a column to an existing table with the result of the ai prompt
#       like existing excel/google sheets plugins
#       must be able to refer to existing columns in the dataset by name
#       compelling demo idea:
#           1. use generate ai feature layer to create "all 50 us state capitals" point feature class
#           2. use this new tool "Generate AI Field" to add a new column with a fun fact about this city


'''
given an existing feature layer in arcgis pro, add a column that holds the response from an ai assistant

parameters:
    in layer
    out layer
    field name
    prompt (with ability to refer to existing fields)
    sql query (only operate on matching records)
    
steps:
    convert feature layer to dataframe
    add the new text field
    parse fields and look for them in the prompt
    filter the data based on the sql query (if supplied)
    hit the openai assistant api for each prompt
    store the result in the new field
    convert the dataframe back to a feature layer

usage:
    if the prompt contains no field information, the AI will attempt to infer what you mean based on the geometry information

examples:
    given a feature class containing a list of US state capital cities and a prompt "a fun fact about this city"
    the "capital" column is assumed to be the target, so the query that's submitted is "a fun fact about {capital}"
    does this logic take a separate assistant?
    a simpler but less robust method might be to cram the whole row into the message, like "6 california sacramento, a fun fact about this city"
    or even "here is the subject of my query below: "OID: 6 state: california capital: sacramento" \n here is my query: "a fun fact about this city"
    use system prompt like "Respond in one simple sentence without preamble or extra context."

'''

import arcpy
import requests
import time
import json

def add_ai_response_to_feature_layer(api_key, in_layer, out_layer, field_name, prompt, sql_query=None):
    
    arcpy.CopyFeatures_management(in_layer,out_layer)
    arcpy.AddMessage(out_layer)

    # Add new field for AI responses
    if field_name not in [f.name for f in arcpy.ListFields(out_layer)]:
        arcpy.management.AddField(out_layer, field_name, "TEXT")
    else:
        arcpy.management.AddField(out_layer, field_name+"_AI", "TEXT")


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
                run_payload = {"assistant_id": "asst_GhFr3IsC3swaSHhrR8plskkV"}
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
    
    def get_ai_response(api_key,prompt):
        try:
            thread_id = create_thread(api_key)
            run_id = submit_message(api_key, thread_id, prompt)
            run_status = wait_on_run(api_key, thread_id, run_id)
            response = get_response(api_key, thread_id)

            # Add debugging to inspect the raw response
            arcpy.AddMessage(f"response: {response}")
            
        except Exception as e:
            arcpy.AddError(str(e))
            return
        
        return response[0]

    def generate_ai_responses_for_feature_class(api_key, feature_class, field_name, prompt_template):
        # Get the OID field name
        desc = arcpy.Describe(feature_class)
        oid_field_name = desc.OIDFieldName

        # Define the fields to be included in the cursor
        fields = [field.name for field in arcpy.ListFields(feature_class)]
        
        # Ensure the new field exists
        if field_name not in fields:
            arcpy.AddField_management(feature_class, field_name, "TEXT")
        
        fields.append(field_name)  # Add the new field to the fields list

        # Store prompts and their corresponding OIDs in a dictionary
        prompts_dict = {}

        # Use a SearchCursor to iterate over the rows in the feature class and generate prompts
        with arcpy.da.SearchCursor(feature_class, fields[:-1],sql_query) as cursor:  # Exclude the new field
            for row in cursor:
                row_dict = {field: value for field, value in zip(fields[:-1], row)}
                formatted_prompt = prompt_template.format(**row_dict)
                oid = row_dict[oid_field_name]
                prompts_dict[oid] = formatted_prompt

        # Debug: Check a sample record from prompts_dict
        if prompts_dict:
            # Get the first key-value pair from the dictionary
            sample_oid, sample_prompt = next(iter(prompts_dict.items()))
            arcpy.AddMessage(f"{oid_field_name} {sample_oid}: {sample_prompt}")
        else:
            arcpy.AddMessage("prompts_dict is empty.")

        # Get AI responses for each prompt
        responses_dict = {oid: get_ai_response(api_key, prompt) for oid, prompt in prompts_dict.items()}

        # Use an UpdateCursor to write the AI responses back to the feature class
        with arcpy.da.UpdateCursor(feature_class, [oid_field_name, field_name]) as cursor:
            for row in cursor:
                oid = row[0]
                if oid in responses_dict:
                    row[1] = responses_dict[oid]
                    cursor.updateRow(row)
    
    generate_ai_responses_for_feature_class(api_key,out_layer,field_name,prompt)


if __name__ == "__main__":
    api_key = arcpy.GetParameterAsText(0)
    in_layer = arcpy.GetParameterAsText(1)
    out_layer = arcpy.GetParameterAsText(2)
    field_name = arcpy.GetParameterAsText(3)
    prompt = arcpy.GetParameterAsText(4)
    sql_query = arcpy.GetParameterAsText(5)

    add_ai_response_to_feature_layer(api_key, in_layer, out_layer, field_name, prompt, sql_query)
