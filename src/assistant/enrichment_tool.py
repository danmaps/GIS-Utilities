
'''
The "Generate AI Field" tool is designed to enrich existing GIS feature layers by adding a new field
containing AI-generated responses. This tool can be used to add informative or fun facts to GIS data,
such as adding fun facts about US state capitals. The tool leverages OpenAI's API to generate responses
based on user-defined prompts and can refer to existing columns in the dataset by name.

'''

import arcpy
import requests
import json
import time

def add_ai_response_to_feature_layer(api_key, in_layer, out_layer, field_name, prompt_template, sql_query=None):
    """
    Enriches an existing feature layer by adding a new field with AI-generated responses.

    Parameters:
    api_key (str): API key for OpenAI.
    in_layer (str): Path to the input feature layer.
    out_layer (str): Path to the output feature layer. If None, in_layer will be updated.
    field_name (str): Name of the field to add the AI responses.
    prompt_template (str): Template for the prompt to be used by AI.
    sql_query (str, optional): Optional SQL query to filter the features.
    """
    if out_layer:
        arcpy.CopyFeatures_management(in_layer, out_layer)
        layer_to_use = out_layer
    else:
        layer_to_use = in_layer

    arcpy.AddMessage(layer_to_use)

    # Add new field for AI responses
    if field_name not in [f.name for f in arcpy.ListFields(layer_to_use)]:
        arcpy.management.AddField(layer_to_use, field_name, "TEXT")
    else:
        arcpy.management.AddField(layer_to_use, field_name + "_AI", "TEXT")
        field_name += "_AI"

    def get_ai_response(api_key, messages):
        """
        Generates an AI response for a given set of messages using the chat completions endpoint.

        Parameters:
        api_key (str): API key for OpenAI.
        messages (list): List of message dictionaries for the AI chat.

        Returns:
        str: AI response.
        """
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "gpt-4o",
            "messages": messages
        }

        for _ in range(3):
            try:
                response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data, verify=False)
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"].strip()
            except requests.exceptions.RequestException as e:
                arcpy.AddWarning(f"Retrying AI response generation due to: {e}")
                time.sleep(1)
        raise Exception("Failed to get AI response after retries")

    def generate_ai_responses_for_feature_class(api_key, feature_class, field_name, prompt_template):
        """
        Generates AI responses for each feature in the feature class and updates the new field with these responses.

        Parameters:
        api_key (str): API key for OpenAI.
        feature_class (str): Path to the feature class.
        field_name (str): Name of the field to add the AI responses.
        prompt_template (str): Template for the prompt to be used by AI.
        """
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
        with arcpy.da.SearchCursor(feature_class, fields[:-1], sql_query) as cursor:  # Exclude the new field
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
        role = "You are a helpful assistant. Respond in one simple sentence without preamble or extra context."
        responses_dict = {
            oid: get_ai_response(api_key, [{"role": "system", "content": role}, {"role": "user", "content": prompt}])
            for oid, prompt in prompts_dict.items()
        }

        # Use an UpdateCursor to write the AI responses back to the feature class
        with arcpy.da.UpdateCursor(feature_class, [oid_field_name, field_name]) as cursor:
            for row in cursor:
                oid = row[0]
                if oid in responses_dict:
                    row[1] = responses_dict[oid]
                    cursor.updateRow(row)
    
    generate_ai_responses_for_feature_class(api_key, layer_to_use, field_name, prompt_template)


if __name__ == "__main__":
    api_key = arcpy.GetParameterAsText(0)
    in_layer = arcpy.GetParameterAsText(1)
    out_layer = arcpy.GetParameterAsText(2)
    field_name = arcpy.GetParameterAsText(3)
    prompt_template = arcpy.GetParameterAsText(4)
    sql_query = arcpy.GetParameterAsText(5)

    add_ai_response_to_feature_layer(api_key, in_layer, out_layer, field_name, prompt_template, sql_query)
